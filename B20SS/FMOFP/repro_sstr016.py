"""
Standalone reproduction for SSTR-016 — AEWC Radar stealth-target memory leak.

WHY THIS SCRIPT EXISTS
----------------------
The leak lives in AEWCRadar._remove_target: track history is deleted for
regular targets but NOT for stealth targets, so the track_histories dict
keeps one entry per stealth track forever.

The leak cannot be observed through the normal AEWC test, because:
  - target generation only happens in SEARCH mode, and
  - the only call to _remove_target requires a target to drift past
    max_range (400 km), and
  - in practice the AEWC mode-change tests fail, so the radar never even
    enters SEARCH and no targets are ever created.

This script bypasses all of that. It builds a real AEWCRadar object and
drives _remove_target directly on a controlled set of regular and stealth
targets, then prints the track_histories count after each removal. It does
NOT change any product behavior — it only exercises and observes the real
method on the real class.

USAGE
-----
    cd B20SS
    python -m FMOFP.repro_sstr016
"""

import os
import sys
import time

# The codebase mixes "FMOFP."-prefixed and bare ("Systems.") imports, so both
# B20SS/ and B20SS/FMOFP/ must be importable. Mirror the app's path setup.
_FMOFP_DIR = os.path.dirname(os.path.abspath(__file__))          # .../B20SS/FMOFP
_PROJECT_ROOT = os.path.dirname(_FMOFP_DIR)                       # .../B20SS
for _p in (_PROJECT_ROOT, _FMOFP_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from FMOFP.Systems.radarManagement.aewc.aewc_radar import aewc_radar


def make_target(is_stealth):
    """Build a minimal target dict with the only field _remove_target reads."""
    return {
        "position": (0.0, 0.0, 0.0),
        "is_stealth": is_stealth,
        "last_update": time.time(),
    }


def seed_track(radar, track_id, is_stealth):
    """Register a target and a matching track-history entry, as the real
    update loop would."""
    radar.current_targets[track_id] = make_target(is_stealth)
    radar.track_histories[track_id] = ["history-sample"]  # stand-in for position history


def main():
    # radar_control and radar_messenger are unused by _remove_target, so None is fine.
    radar = aewc_radar(name="aewc_radar", radar_control=None, radar_messenger=None)

    # Seed an alternating mix of regular and stealth targets.
    plan = [
        (1, False),
        (2, True),
        (3, False),
        (4, True),
        (5, True),
        (6, False),
    ]
    for track_id, is_stealth in plan:
        seed_track(radar, track_id, is_stealth)

    print("=" * 64)
    print("SSTR-016 reproduction — AEWC stealth-target track_histories leak")
    print("=" * 64)
    print(f"Seeded {len(plan)} targets "
          f"({sum(1 for _, s in plan if s)} stealth, "
          f"{sum(1 for _, s in plan if not s)} regular).")
    print(f"Initial track_histories entries: {len(radar.track_histories)}")
    print("-" * 64)
    print(f"{'remove track':>12} | {'stealth':>7} | {'track_histories left':>20}")
    print("-" * 64)

    for track_id, is_stealth in plan:
        radar._remove_target(track_id)
        leftover = len(radar.track_histories)
        print(f"{track_id:>12} | {str(is_stealth):>7} | {leftover:>20}")

    print("-" * 64)
    remaining = sorted(radar.track_histories.keys())
    print(f"current_targets remaining: {len(radar.current_targets)} "
          "(expected 0 — all were removed)")
    print(f"track_histories remaining: {len(radar.track_histories)} "
          "(expected 0 if cleanup were correct)")
    print(f"leaked track_history ids:  {remaining}")
    print("-" * 64)

    leaked_stealth = [tid for tid, s in plan if s and tid in radar.track_histories]
    if remaining:
        print("RESULT: LEAK CONFIRMED. The leftover track_histories entries are")
        print(f"        exactly the stealth tracks {leaked_stealth} — their history")
        print("        was never deleted by _remove_target.")
    else:
        print("RESULT: No leak observed (track_histories fully cleaned).")
    print("=" * 64)


if __name__ == "__main__":
    main()
