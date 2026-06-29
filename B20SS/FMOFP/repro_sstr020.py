"""
Standalone reproduction for SSTR-020 — Weather Radar VIL precision loss.

WHY THIS SCRIPT EXISTS
----------------------
The bug lives in weather_radar._calculate_vil:

    if hasattr(ref, 'astype'):
        ref = ref.astype(np.float32)     # downcasts double -> single
    return self.vil_data_generator.calculate_vil(ref, elevation_angles)

The requirement (WR[17], WR[17.1], WR[17.3]) is to maintain IEEE-754 double
precision (64-bit, >= 15 significant digits) through the VIL calculation. The
astype(np.float32) cast throws away precision before the calculation runs.

It cannot be observed reliably through the normal weather test, because
_calculate_vil is only reached from the product-generation paths (scan() /
update_simulated()), which require a non-STANDBY mode. In practice the weather
mode-change tests fail, so the radar stays in STANDBY and those paths never
run. (Note: the passing 'request_vil_data' test does NOT exercise this method
— it is served by _handle_vil_data_sync, which calls the VIL generator
directly and never touches _calculate_vil.)

HOW THIS SCRIPT WORKS
---------------------
It builds a real weather_radar, sets a valid mode so the config lookup
succeeds, and calls the REAL _calculate_vil with a known float64 reflectivity
array. To observe what dtype the live method actually forwards into the VIL
calculation (without modifying product code), it temporarily wraps the
radar's vil_data_generator.calculate_vil to record the dtype it receives,
then restores it. The product method itself is unmodified and is what runs.

THOROUGHNESS
------------
Three checks, with a combined verdict that flips to NO BUG once the cast is
changed to np.float64:

  1. Live-dtype check: call the real _calculate_vil with a float64 array and
     record the dtype that actually reaches the VIL calculation. Bug => the
     method forwards float32; correct => it stays float64.
  2. Precision-loss check: take a float64 reflectivity value carrying >7
     significant digits, apply the SAME cast the live method uses (captured
     from check 1), and quantify how much precision is lost.
  3. Precision-at-boundary check: measure how many significant digits
     survive in the data that actually enters the VIL calculation under the
     live cast (float32 ~7 digits vs the >=15 the requirement needs). The
     final VIL output is NOT used as the signal, because the generator rounds
     to significant figures internally and masks the difference downstream.

USAGE
-----
    cd B20SS
    python -m FMOFP.repro_sstr020
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

import numpy as np

from FMOFP.Systems.radarManagement.weather.weather_radar import (
    weather_radar, weather_radarMode,
)


def make_radar():
    radar = weather_radar(name="weather_radar",
                          radar_control=None, radar_messenger=None)
    # _calculate_vil looks up config['vcp'][mode.name.lower()]; SURVEILLANCE
    # exists in the default config. Setting the attribute does not invoke the
    # (broken) mode-change machinery — it just satisfies the config lookup.
    radar.mode = weather_radarMode.SURVEILLANCE
    return radar


def make_reflectivity():
    """A 3D reflectivity volume (azimuth, elevation, range) of float64 values
    carrying more significant digits than float32 can represent."""
    # 4 elevations to match the 'surveillance' VCP.
    base = np.linspace(10.0, 60.0, 8 * 4 * 16, dtype=np.float64)
    ref = base.reshape(8, 4, 16)
    # Stamp in a value with ~15 significant digits at a known location.
    ref[0, 0, 0] = 12.3456789012345
    return ref


def capture_live_dtype(radar, ref):
    """Call the REAL _calculate_vil and record the dtype that actually reaches
    the VIL calculation, by temporarily wrapping the generator's method."""
    captured = {}
    gen = radar.vil_data_generator
    original = gen.calculate_vil

    def spy(reflectivity, elevation_angles):
        captured["dtype"] = getattr(reflectivity, "dtype", None)
        return original(reflectivity, elevation_angles)

    gen.calculate_vil = spy
    try:
        radar._calculate_vil(ref)            # REAL product method
    finally:
        gen.calculate_vil = original         # restore — no lasting change
    return captured.get("dtype")


def main():
    radar = make_radar()
    ref = make_reflectivity()
    probe_value = float(ref[0, 0, 0])

    print("=" * 72)
    print("SSTR-020 reproduction — Weather Radar VIL precision loss")
    print("=" * 72)
    print(f"Input reflectivity array dtype: {ref.dtype}")
    print(f"Probe value (15 sig figs):      {probe_value!r}")
    print("-" * 72)

    # ---- Check 1: live dtype forwarded into the VIL calculation ----
    live_dtype = capture_live_dtype(radar, ref)
    bug1 = (live_dtype == np.float32)
    print("CHECK 1 — dtype the live _calculate_vil forwards into the calculation:")
    print(f"  observed dtype: {live_dtype}  (required: float64)")
    print(f"  -> {'PRECISION LOST (float32)' if bug1 else 'ok (float64)'}")
    print("-" * 72)

    # ---- Check 2: quantify precision loss of that cast on the probe value ----
    # Apply the same cast the live method used (captured above) to one value.
    cast_value = np.array([probe_value], dtype=live_dtype)[0]
    abs_err = abs(float(cast_value) - probe_value)
    rel_err = abs_err / abs(probe_value) if probe_value else 0.0
    bug2 = live_dtype == np.float32 and abs_err > 0.0
    print("CHECK 2 — precision loss on a 15-significant-digit value:")
    print(f"  original (float64): {probe_value!r}")
    print(f"  after live cast   : {float(cast_value)!r}")
    print(f"  absolute error    : {abs_err:.3e}")
    print(f"  relative error    : {rel_err:.3e}")
    print(f"  -> {'PRECISION LOST' if bug2 else 'no loss'}")
    print("-" * 72)

    # ---- Check 3: precision available AT the calculation input ----
    # The requirement (WR[17.3]) governs the precision used FOR the
    # calculation. We show how many significant digits survive in the data
    # that actually enters calculate_vil under the live cast, versus float64.
    #
    # Note: comparing the final VIL *output* float32-vs-float64 is NOT a
    # reliable signal here, because VILDataGenerator.calculate_vil rounds to
    # significant figures at every step (round_to_sigfigs on z, on each
    # contribution, and on the final array). That rounding masks the
    # difference in the output even though the input precision was already
    # lost. So this check measures the precision at the calculation boundary,
    # which is what the requirement actually constrains.
    f64_val = np.array([probe_value], dtype=np.float64)[0]
    live_val = np.array([probe_value], dtype=live_dtype)[0]
    # Significant digits preserved (approx) = -log10(relative error).
    rel = abs(float(live_val) - probe_value) / abs(probe_value) if probe_value else 0.0
    import math
    sig_digits = (-math.log10(rel)) if rel > 0 else float("inf")
    bug3 = live_dtype == np.float32  # precision at the calc boundary is degraded
    print("CHECK 3 — precision at the calculation boundary (WR[17.3]):")
    print(f"  significant digits preserved entering the VIL calc: ~{sig_digits:.1f}")
    print(f"  requirement (WR[17.1]): >= 15 significant digits")
    print(f"  -> {'BELOW REQUIREMENT (float32 ~7 digits)' if bug3 else 'meets requirement (float64)'}")
    print("  note: the generator's internal sig-fig rounding masks this in the")
    print("        final VIL output, so the loss is only visible at the input.")
    print("-" * 72)

    failures = sum(1 for b in (bug1, bug2, bug3) if b)
    if failures:
        print(f"RESULT: BUG CONFIRMED. {failures} of 3 checks show the VIL calculation")
        print("        runs on float32-downcast data, violating the double-precision")
        print("        requirement (WR[17] / WR[17.1] / WR[17.3]). The astype(np.float32)")
        print("        cast in _calculate_vil discards precision before the calculation.")
    else:
        print("RESULT: NO BUG. The VIL calculation preserves float64 precision; the")
        print("        cast no longer downgrades the reflectivity data.")
    print("=" * 72)


if __name__ == "__main__":
    main()
