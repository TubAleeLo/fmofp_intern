"""
Standalone reproduction for SSTR-018 — Targeting Radar classification thresholds.

WHY THIS SCRIPT EXISTS
----------------------
The bug lives in targeting_radar._generate_target. Per the requirement
(TR[9] / TR[10]): targets faster than 250 m/s should be FIGHTER, and targets
above 10000 m altitude should be HIGH_ALT. The buggy code uses 400 and 8000
instead, so it misclassifies targets relative to the requirement.

HOW THIS SCRIPT WORKS (important)
---------------------------------
This script calls the REAL targeting_radar._generate_target method and reads
the 'classification' field it returns. It then recomputes the target's speed
(v_mag) and altitude (z) from the returned vectors and checks whether the
live classification matches the requirement for those values.

Because it invokes the actual product method, this script reflects whatever
thresholds the live code currently uses: if the bug is present it reports
BUG CONFIRMED, and if you FIX the thresholds in _generate_target it will
report NO BUG. (An earlier version of this script hardcoded the thresholds
and could not detect a fix — this version does not.)

Note: _generate_target draws v_mag from 100-300 m/s, so the FIGHTER boundary
of interest is the 250-300 band. Altitude is derived from range/elevation and
can exceed 10000 m. The script samples many targets to populate these bands.

USAGE
-----
    cd B20SS
    python -m FMOFP.repro_sstr018
"""

import os
import sys
import math

# The codebase mixes "FMOFP."-prefixed and bare imports, so both B20SS/ and
# B20SS/FMOFP/ must be importable. Mirror the app's path setup.
_FMOFP_DIR = os.path.dirname(os.path.abspath(__file__))   # .../B20SS/FMOFP
_PROJECT_ROOT = os.path.dirname(_FMOFP_DIR)               # .../B20SS
for _p in (_PROJECT_ROOT, _FMOFP_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from FMOFP.Systems.radarManagement.targeting.targeting_radar import targeting_radar

# Requirement thresholds (TR[9] / TR[10]).
REQUIRED_FIGHTER_SPEED = 250.0   # m/s
REQUIRED_HIGH_ALT = 10000.0      # m


def required_classification(v_mag, z):
    """What the classification SHOULD be, per the requirement."""
    if v_mag > REQUIRED_FIGHTER_SPEED:
        return "FIGHTER"
    elif abs(z) > REQUIRED_HIGH_ALT:
        return "HIGH_ALT"
    else:
        return "UNKNOWN"


def main():
    radar = targeting_radar(name="targeting_radar",
                            radar_control=None, radar_messenger=None)

    n = 20000
    mismatches = []
    fighter_band_seen = 0   # targets with v_mag in (250, 300]
    high_alt_seen = 0       # targets with |z| > 10000

    for _ in range(n):
        target = radar._generate_target()        # REAL product method

        vx, vy, vz = target["velocity"]
        x, y, z = target["position"]
        v_mag = math.sqrt(vx * vx + vy * vy + vz * vz)

        live = target["classification"]
        req = required_classification(v_mag, z)

        if v_mag > REQUIRED_FIGHTER_SPEED:
            fighter_band_seen += 1
        if abs(z) > REQUIRED_HIGH_ALT:
            high_alt_seen += 1

        if live != req:
            mismatches.append((v_mag, z, live, req))

    print("=" * 72)
    print("SSTR-018 reproduction — Targeting Radar classification thresholds")
    print("=" * 72)
    print(f"Generated {n} targets via the REAL _generate_target method.")
    print(f"Requirement: v_mag > {REQUIRED_FIGHTER_SPEED:.0f} -> FIGHTER, "
          f"|alt| > {REQUIRED_HIGH_ALT:.0f} -> HIGH_ALT")
    print("-" * 72)
    print(f"Targets that SHOULD be FIGHTER (v_mag > 250): {fighter_band_seen}")
    print(f"Targets that SHOULD be HIGH_ALT (|alt| > 10000): {high_alt_seen}")
    print(f"Total misclassified vs requirement: {len(mismatches)}")
    print("-" * 72)

    if mismatches:
        print("Sample mismatches (live classification vs required):")
        for v_mag, z, live, req in mismatches[:8]:
            print(f"    v_mag={v_mag:6.1f} m/s, alt={z:9.1f} m : "
                  f"live={live:<8} required={req}")
        print("-" * 72)
        print("RESULT: BUG CONFIRMED. The live classification disagrees with the")
        print("        requirement for the cases above, because _generate_target's")
        print("        thresholds do not match 250 / 10000.")
    else:
        print("RESULT: NO BUG. The live classification matches the requirement")
        print("        for every sampled target. Thresholds appear correct.")
        if fighter_band_seen == 0 and high_alt_seen == 0:
            print("        (Caveat: no targets landed in the FIGHTER/HIGH_ALT bands")
            print("         this run, so the check was weak. Re-run to sample more.)")
    print("=" * 72)


if __name__ == "__main__":
    main()
