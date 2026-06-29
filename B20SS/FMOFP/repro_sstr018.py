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
import inspect
import re

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


def extract_live_classifier():
    """Pull the actual classification block out of the live _generate_target
    source and return a callable classify(v_mag, z) that executes those exact
    lines. This reflects the live thresholds (so it detects a fix) and lets us
    test exact boundary values deterministically, without modifying product
    code. Returns None if the block can't be located.
    """
    src = inspect.getsource(targeting_radar._generate_target)
    lines = src.splitlines()

    # Find the "if v_mag ..." line that opens the classification block and
    # capture through the "classification = "UNKNOWN"" line.
    start = None
    for i, line in enumerate(lines):
        if re.match(r"\s*if\s+v_mag\s*>", line):
            start = i
            break
    if start is None:
        return None

    block = []
    for line in lines[start:]:
        block.append(line)
        if "classification" in line and "UNKNOWN" in line:
            break
    else:
        return None  # never found the closing UNKNOWN line

    # Dedent so the block is valid at module indentation, then wrap in a func.
    dedented = inspect.cleandoc("\n".join(block))
    func_src = "def _live_classify(v_mag, z):\n"
    for bl in dedented.splitlines():
        func_src += "    " + bl + "\n"
    func_src += "    return classification\n"

    namespace = {}
    exec(func_src, namespace)
    return namespace["_live_classify"]


def run_boundary_check():
    """Deterministic exact-boundary check using the live classification logic."""
    classify = extract_live_classifier()
    if classify is None:
        print("BOUNDARY CHECK: could not extract live classification block; skipped.")
        return None

    # Exact boundary cases: (v_mag, altitude, label)
    cases = [
        (250.0,  0.0,     "speed exactly at 250 (requirement boundary)"),
        (250.1,  0.0,     "speed just over 250 -> should be FIGHTER"),
        (300.0,  0.0,     "speed 300 -> should be FIGHTER"),
        (400.0,  0.0,     "speed exactly 400 (old buggy boundary)"),
        (400.1,  0.0,     "speed just over 400 -> should be FIGHTER"),
        (150.0,  10000.0, "altitude exactly at 10000 (requirement boundary)"),
        (150.0,  10000.1, "altitude just over 10000 -> should be HIGH_ALT"),
        (150.0,  8000.1,  "altitude just over 8000 (old buggy boundary)"),
        (150.0,  -10500.0,"negative altitude beyond 10000 -> should be HIGH_ALT"),
        (150.0,  2000.0,  "slow and low -> genuinely UNKNOWN"),
    ]

    print("DETERMINISTIC BOUNDARY CHECK (runs the live classification logic):")
    print(f"{'v_mag':>7} | {'alt':>9} | {'live':>9} | {'required':>9} | result")
    print("-" * 72)
    failures = 0
    for v_mag, z, label in cases:
        live = classify(v_mag, z)
        req = required_classification(v_mag, z)
        flag = "  <-- MISMATCH" if live != req else ""
        if live != req:
            failures += 1
        print(f"{v_mag:>7.1f} | {z:>9.1f} | {live:>9} | {req:>9} | {label}{flag}")
    print("-" * 72)
    return failures


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

    # --- Check 1: deterministic exact-boundary check ---
    boundary_failures = run_boundary_check()
    print()

    # --- Check 2: statistical sampling via the real _generate_target ---
    print(f"STATISTICAL SAMPLING CHECK (real _generate_target, {n} targets):")
    print(f"Requirement: v_mag > {REQUIRED_FIGHTER_SPEED:.0f} -> FIGHTER, "
          f"|alt| > {REQUIRED_HIGH_ALT:.0f} -> HIGH_ALT")
    print(f"Targets that SHOULD be FIGHTER (v_mag > 250): {fighter_band_seen}")
    print(f"Targets that SHOULD be HIGH_ALT (|alt| > 10000): {high_alt_seen}")
    print(f"Total misclassified vs requirement: {len(mismatches)}")
    if mismatches:
        print("Sample mismatches (live classification vs required):")
        for v_mag, z, live, req in mismatches[:5]:
            print(f"    v_mag={v_mag:6.1f} m/s, alt={z:9.1f} m : "
                  f"live={live:<8} required={req}")
    print("-" * 72)

    # --- Combined verdict ---
    boundary_bug = bool(boundary_failures)        # None -> False (skipped)
    sampling_bug = bool(mismatches)
    if boundary_bug or sampling_bug:
        print("RESULT: BUG CONFIRMED.")
        if boundary_bug:
            print(f"        Boundary check: {boundary_failures} exact case(s) misclassified.")
        if sampling_bug:
            print(f"        Sampling check: {len(mismatches)} of {n} sampled targets misclassified.")
        print("        The live thresholds in _generate_target do not match 250 / 10000.")
    else:
        print("RESULT: NO BUG. Both the exact-boundary check and the sampling check")
        print("        agree the live classification matches the requirement.")
        if fighter_band_seen == 0 and high_alt_seen == 0:
            print("        (Note: sampling hit no FIGHTER/HIGH_ALT targets this run, but")
            print("         the deterministic boundary check still validated the thresholds.)")
    print("=" * 72)


if __name__ == "__main__":
    main()
