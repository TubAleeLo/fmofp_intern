"""
Standalone reproduction for SSTR-016 — AEWC Radar stealth-target memory leak.

WHY THIS SCRIPT EXISTS
----------------------
The leak lives in aewc_radar._remove_target: track history is deleted for
regular targets but NOT for stealth targets, so the track_histories dict
keeps one entry per stealth track forever.

It cannot be observed through the normal AEWC test, because:
  - target generation only happens in SEARCH mode,
  - the only call to _remove_target requires a target to drift past
    max_range (400 km), and
  - the AEWC mode-change tests fail, so the radar never even enters SEARCH
    and no targets are ever created.

This script bypasses all of that. It builds a real aewc_radar object and
drives the REAL _remove_target on controlled targets. No product behavior is
changed — the script only exercises and observes the real method.

THOROUGHNESS
------------
Three checks, with a combined verdict that reports LEAK CONFIRMED if ANY
check fails and NO LEAK only if ALL pass (so it correctly flips to NO LEAK
once stealth cleanup is added to _remove_target):

  1. Per-removal check: remove a mix of regular and stealth targets and
     confirm regular histories are freed while stealth histories are not.
  2. Multi-point history check: give a stealth target several history points
     (a realistic deque, not an empty placeholder) and confirm the whole
     entry is orphaned on removal.
  3. Growth-over-time check: repeatedly add and remove stealth targets and
     show track_histories grows without bound — the actual "memory leak"
     framing — while current_targets stays at zero.

USAGE
-----
    cd B20SS
    python -m FMOFP.repro_sstr016
"""

import os
import sys
import time
from collections import deque

# The codebase mixes "FMOFP."-prefixed and bare imports, so both B20SS/ and
# B20SS/FMOFP/ must be importable. Mirror the app's path setup.
_FMOFP_DIR = os.path.dirname(os.path.abspath(__file__))   # .../B20SS/FMOFP
_PROJECT_ROOT = os.path.dirname(_FMOFP_DIR)               # .../B20SS
for _p in (_PROJECT_ROOT, _FMOFP_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from FMOFP.Systems.radarManagement.aewc.aewc_radar import aewc_radar


def make_target(is_stealth):
    """Minimal target dict with the only field _remove_target reads."""
    return {
        "position": (0.0, 0.0, 0.0),
        "is_stealth": is_stealth,
        "last_update": time.time(),
    }


def new_radar():
    # radar_control / radar_messenger are unused by _remove_target, so None is fine.
    return aewc_radar(name="aewc_radar", radar_control=None, radar_messenger=None)


def seed(radar, track_id, is_stealth, history_points=1):
    """Register a target plus a track-history deque, like the real update loop."""
    radar.current_targets[track_id] = make_target(is_stealth)
    hist = deque(maxlen=10)
    for i in range(history_points):
        hist.append({"position": (float(i), 0.0, 0.0), "timestamp": time.time()})
    radar.track_histories[track_id] = hist


def check_per_removal():
    """Check 1: regular histories freed, stealth histories orphaned."""
    radar = new_radar()
    plan = [(1, False), (2, True), (3, False), (4, True), (5, True), (6, False)]
    for tid, stealth in plan:
        seed(radar, tid, stealth)

    rows = []
    for tid, stealth in plan:
        radar._remove_target(tid)
        rows.append((tid, stealth, len(radar.track_histories)))

    leaked = sorted(radar.track_histories.keys())
    expected_leak = sorted(tid for tid, s in plan if s)  # stealth ids, if buggy
    # PASS (no bug) means nothing leaked. FAIL (bug) means stealth ids remain.
    bug = len(leaked) > 0
    return {
        "rows": rows,
        "leaked": leaked,
        "expected_leak_if_buggy": expected_leak,
        "bug": bug,
    }


def check_multi_point_history():
    """Check 2: a stealth target with several history points is fully orphaned."""
    radar = new_radar()
    seed(radar, 1, is_stealth=False, history_points=7)
    seed(radar, 2, is_stealth=True, history_points=7)

    before_pts_stealth = len(radar.track_histories[2])
    radar._remove_target(1)   # regular
    radar._remove_target(2)   # stealth
    stealth_still_present = 2 in radar.track_histories
    leaked_points = len(radar.track_histories[2]) if stealth_still_present else 0
    bug = stealth_still_present
    return {
        "before_pts_stealth": before_pts_stealth,
        "stealth_still_present": stealth_still_present,
        "leaked_points": leaked_points,
        "bug": bug,
    }


def check_growth_over_time(cycles=500):
    """Check 3: repeatedly add+remove a stealth target; track_histories grows."""
    radar = new_radar()
    samples = []
    for i in range(1, cycles + 1):
        seed(radar, i, is_stealth=True, history_points=3)
        radar._remove_target(i)
        if i in (1, cycles // 4, cycles // 2, cycles):
            samples.append((i, len(radar.current_targets), len(radar.track_histories)))
    final_hist = len(radar.track_histories)
    final_targets = len(radar.current_targets)
    # No bug: histories should return to 0 each cycle. Bug: grows ~1 per cycle.
    bug = final_hist > 0
    return {
        "cycles": cycles,
        "samples": samples,
        "final_targets": final_targets,
        "final_hist": final_hist,
        "bug": bug,
    }


def main():
    print("=" * 72)
    print("SSTR-016 reproduction — AEWC stealth-target track_histories leak")
    print("=" * 72)

    # ---- Check 1 ----
    c1 = check_per_removal()
    print("CHECK 1 — per-removal cleanup:")
    print(f"  {'remove track':>12} | {'stealth':>7} | {'track_histories left':>20}")
    for tid, stealth, left in c1["rows"]:
        print(f"  {tid:>12} | {str(stealth):>7} | {left:>20}")
    print(f"  leaked after removing all: {c1['leaked']} "
          f"(stealth ids = {c1['expected_leak_if_buggy']})")
    print(f"  -> {'LEAK' if c1['bug'] else 'clean'}")
    print("-" * 72)

    # ---- Check 2 ----
    c2 = check_multi_point_history()
    print("CHECK 2 — multi-point stealth history:")
    print(f"  stealth target had {c2['before_pts_stealth']} history points before removal")
    print(f"  stealth entry still present after removal: {c2['stealth_still_present']}")
    print(f"  orphaned history points: {c2['leaked_points']}")
    print(f"  -> {'LEAK' if c2['bug'] else 'clean'}")
    print("-" * 72)

    # ---- Check 3 ----
    c3 = check_growth_over_time()
    print(f"CHECK 3 — growth over {c3['cycles']} add/remove cycles (all stealth):")
    print(f"  {'after cycle':>12} | {'current_targets':>15} | {'track_histories':>15}")
    for i, ct, th in c3["samples"]:
        print(f"  {i:>12} | {ct:>15} | {th:>15}")
    print(f"  final: current_targets={c3['final_targets']}, "
          f"track_histories={c3['final_hist']}")
    print(f"  -> {'LEAK (grows unbounded)' if c3['bug'] else 'clean (returns to 0)'}")
    print("-" * 72)

    failures = sum(1 for c in (c1, c2, c3) if c["bug"])
    if failures:
        print(f"RESULT: LEAK CONFIRMED. {failures} of 3 checks show stealth track")
        print("        histories are never freed by _remove_target. Over many")
        print("        add/remove cycles, track_histories grows without bound while")
        print("        current_targets stays at 0 — a classic memory leak.")
    else:
        print("RESULT: NO LEAK. All 3 checks show track_histories is fully cleaned")
        print("        for both regular and stealth targets.")
    print("=" * 72)


if __name__ == "__main__":
    main()
