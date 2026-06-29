"""
Standalone reproduction for SSTR-019 — Weather Radar resource usage inaccuracy.

WHY THIS SCRIPT EXISTS
----------------------
The bug lives in weather_radar._update_resource_usage:

    self._resource_usage['cpu_usage'] = 30      # always 30
    self._resource_usage['memory_usage'] = 40   # always 40
    self._resource_usage['disk_usage'] = 20     # always 20

The requirement (WR[12]..WR[12.4]) is to report CPU/memory/disk usage that
reflects actual system load and updates dynamically. The method instead writes
the same three constants every call, regardless of mode or real load, so
resource monitoring is meaningless.

HOW THIS SCRIPT WORKS
---------------------
_update_resource_usage has no mode gate and no external dependencies, so this
script builds a real weather_radar and calls the REAL method directly. No
product behavior is changed — the script only invokes and observes.

THOROUGHNESS
------------
Three checks, with a combined verdict that flips to NO BUG once the values
become load-dependent:

  1. Repeat-call invariance: call _update_resource_usage many times and show
     the reported values never change.
  2. Mode invariance: call it in several different radar modes (STANDBY vs
     active) and show the values are identical across modes — they do not
     respond to operational state.
  3. Overwrite-with-constants: perturb _resource_usage to clearly different
     numbers, call the method once, and show it overwrites them back to the
     same hardcoded 30/40/20 — proving the values are fixed, not measured.

USAGE
-----
    cd B20SS
    python -m FMOFP.repro_sstr019
"""

import os
import sys

# The codebase mixes "FMOFP."-prefixed and bare imports, so both B20SS/ and
# B20SS/FMOFP/ must be importable. Mirror the app's path setup.
_FMOFP_DIR = os.path.dirname(os.path.abspath(__file__))   # .../B20SS/FMOFP
_PROJECT_ROOT = os.path.dirname(_FMOFP_DIR)               # .../B20SS
for _p in (_PROJECT_ROOT, _FMOFP_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from FMOFP.Systems.radarManagement.weather.weather_radar import (
    weather_radar, weather_radarMode,
)


def new_radar():
    # radar_control / radar_messenger are unused by _update_resource_usage.
    return weather_radar(name="weather_radar",
                         radar_control=None, radar_messenger=None)


def snapshot(radar):
    u = radar._resource_usage
    return (u['cpu_usage'], u['memory_usage'], u['disk_usage'])


def check_repeat_invariance(n=10):
    """Check 1: repeated calls never change the reported values."""
    radar = new_radar()
    seen = set()
    rows = []
    for i in range(n):
        radar._update_resource_usage()      # REAL method
        snap = snapshot(radar)
        seen.add(snap)
        if i < 3 or i == n - 1:
            rows.append((i + 1, snap))
    bug = len(seen) == 1                     # only ever one distinct value => static
    return {"rows": rows, "distinct": len(seen), "bug": bug}


def check_mode_invariance():
    """Check 2: values are identical across operational modes."""
    radar = new_radar()
    results = []
    # Try a representative spread of modes that exist in the enum.
    candidate_modes = ["STANDBY", "SURVEILLANCE", "MAPPING"]
    for name in candidate_modes:
        mode = getattr(weather_radarMode, name, None)
        if mode is None:
            continue
        radar.mode = mode                    # attribute set; no mode-change machinery
        radar._update_resource_usage()       # REAL method
        results.append((name, snapshot(radar)))
    distinct = len(set(snap for _, snap in results))
    bug = distinct == 1                       # same across all modes => ignores state
    return {"results": results, "distinct": distinct, "bug": bug}


def check_overwrite_with_constants():
    """Check 3: method overwrites perturbed values back to the hardcoded set."""
    radar = new_radar()
    # Set clearly different, plausible "measured" values.
    radar._resource_usage['cpu_usage'] = 77
    radar._resource_usage['memory_usage'] = 12
    radar._resource_usage['disk_usage'] = 55
    before = snapshot(radar)
    radar._update_resource_usage()           # REAL method
    after = snapshot(radar)
    # Bug: the perturbation is discarded and replaced by fixed constants.
    bug = after == (30, 40, 20) and before != after
    return {"before": before, "after": after, "bug": bug}


def main():
    print("=" * 72)
    print("SSTR-019 reproduction — Weather Radar resource usage inaccuracy")
    print("=" * 72)
    print("Requirement (WR[12]..WR[12.4]): report CPU/memory/disk that reflect")
    print("actual system load and update dynamically.")
    print("-" * 72)

    # ---- Check 1 ----
    c1 = check_repeat_invariance()
    print("CHECK 1 — repeated calls (cpu, mem, disk):")
    for i, snap in c1["rows"]:
        print(f"  call {i:>3}: {snap}")
    print(f"  distinct values observed across all calls: {c1['distinct']}")
    print(f"  -> {'STATIC (never changes)' if c1['bug'] else 'varies'}")
    print("-" * 72)

    # ---- Check 2 ----
    c2 = check_mode_invariance()
    print("CHECK 2 — values per mode (cpu, mem, disk):")
    for name, snap in c2["results"]:
        print(f"  {name:<13}: {snap}")
    print(f"  distinct values across modes: {c2['distinct']}")
    print(f"  -> {'STATIC (ignores mode/load)' if c2['bug'] else 'mode-dependent'}")
    print("-" * 72)

    # ---- Check 3 ----
    c3 = check_overwrite_with_constants()
    print("CHECK 3 — overwrite check:")
    print(f"  before call (perturbed): {c3['before']}")
    print(f"  after  call (live)     : {c3['after']}")
    print(f"  -> {'OVERWRITES to fixed 30/40/20' if c3['bug'] else 'preserves/updates measured values'}")
    print("-" * 72)

    failures = sum(1 for c in (c1, c2, c3) if c["bug"])
    if failures:
        print(f"RESULT: BUG CONFIRMED. {failures} of 3 checks show resource usage is")
        print("        reported as fixed constants (cpu=30, mem=40, disk=20) that never")
        print("        change with calls, mode, or actual load — violating WR[12]..[12.4].")
    else:
        print("RESULT: NO BUG. Resource usage values vary and respond to conditions,")
        print("        rather than being hardcoded constants.")
    print("=" * 72)


if __name__ == "__main__":
    main()
