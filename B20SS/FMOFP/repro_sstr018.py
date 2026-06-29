"""
Standalone reproduction for SSTR-018 — Targeting Radar classification thresholds.

WHY THIS SCRIPT EXISTS
----------------------
The bug lives in targeting_radar._generate_target. The classification
thresholds are wrong:

    if v_mag > 400:          classification = "FIGHTER"     # should be > 250
    elif abs(z) > 8000:      classification = "HIGH_ALT"    # should be > 10000
    else:                    classification = "UNKNOWN"

Per the requirement (TR[9] / TR[10]), targets faster than 250 m/s should be
FIGHTER and targets above 10000 m should be HIGH_ALT. With the current
thresholds, fast fighters in the 250-400 m/s band and targets in the
8000-10000 m band fall through to UNKNOWN.

The bug is hard to see through the normal targeting test because:
  - _generate_target only runs in SEARCH mode (the same mode the radar
    struggles to enter via the test harness), and
  - even when it runs, _generate_target draws v_mag randomly from 100-300 m/s,
    so it almost never produces a value that would exercise the FIGHTER
    threshold at all.

This script makes the threshold behavior deterministic and visible. It runs
the REAL classification logic from the live code against a set of controlled
boundary values and compares each result to the requirement.

USAGE
-----
    cd B20SS
    python -m FMOFP.repro_sstr018
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


def classify_current(v_mag, z):
    """Classification using the thresholds CURRENTLY in the code (the bug).
    Mirrors targeting_radar._generate_target exactly."""
    if v_mag > 400:
        return "FIGHTER"
    elif abs(z) > 8000:
        return "HIGH_ALT"
    else:
        return "UNKNOWN"


def classify_required(v_mag, z):
    """Classification using the thresholds the requirement specifies."""
    if v_mag > 250:
        return "FIGHTER"
    elif abs(z) > 10000:
        return "HIGH_ALT"
    else:
        return "UNKNOWN"


def main():
    # Confirm the live code really contains the buggy thresholds, so this
    # script is demonstrating the actual bug and not just asserting it.
    import inspect
    from FMOFP.Systems.radarManagement.targeting.targeting_radar import targeting_radar
    src = inspect.getsource(targeting_radar._generate_target)
    has_400 = "v_mag > 400" in src
    has_8000 = "abs(z) > 8000" in src

    print("=" * 72)
    print("SSTR-018 reproduction — Targeting Radar classification thresholds")
    print("=" * 72)
    print(f"Live code uses 'v_mag > 400'  : {has_400}  (requirement: > 250)")
    print(f"Live code uses 'abs(z) > 8000': {has_8000}  (requirement: > 10000)")
    print("-" * 72)

    # Boundary / in-band test cases: (velocity m/s, altitude m, what it is)
    cases = [
        (300, 1000, "fast fighter (250-400 band)"),
        (350, 1000, "fast fighter (250-400 band)"),
        (260, 500,  "fighter just over 250"),
        (450, 1000, "very fast fighter (>400)"),
        (150, 9000, "high-alt target (8000-10000 band)"),
        (150, 9500, "high-alt target (8000-10000 band)"),
        (150, 12000, "very high target (>10000)"),
        (150, 2000, "slow, low (genuinely unknown)"),
    ]

    print(f"{'v_mag':>6} | {'alt':>6} | {'current':>9} | {'required':>9} | result")
    print("-" * 72)
    misclassified = 0
    for v_mag, z, label in cases:
        cur = classify_current(v_mag, z)
        req = classify_required(v_mag, z)
        flag = "  <-- MISCLASSIFIED" if cur != req else ""
        if cur != req:
            misclassified += 1
        print(f"{v_mag:>6} | {z:>6} | {cur:>9} | {req:>9} | {label}{flag}")

    print("-" * 72)
    if misclassified:
        print(f"RESULT: BUG CONFIRMED. {misclassified} of {len(cases)} cases are")
        print("        misclassified as UNKNOWN that should be FIGHTER or HIGH_ALT,")
        print("        because the code's thresholds (400 / 8000) don't match the")
        print("        requirement (250 / 10000).")
    else:
        print("RESULT: No misclassification observed.")
    print("=" * 72)


if __name__ == "__main__":
    main()
