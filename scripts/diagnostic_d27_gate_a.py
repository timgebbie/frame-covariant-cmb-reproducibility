#!/usr/bin/env python3
r"""D27 --- W1 gate G-a. The D26 candidate put to $\ell_{\rm peak}$.

**The prediction was written down before this ran** --- Coordination's
instruction, 2026-10-23: *"it be written down before W1 runs rather than read
off afterwards, with the tolerance stated, so the run can fail, which is the
property every repair this month has lacked."*

    PRE-REGISTERED, claude/stream-P1B-W1-preregistration-2026-10-23.md:

      B_SLOT_REPAIR's combination gives ell_peak / ell_A in [0.55, 0.80]
      in the CDM frame -- a first peak between l ~ 150 and l ~ 218 -- and
      the Newtonian frame lands within +-15% of it.

    REFERENCE POINTS, all already measured:
      released                 0.030   (spurious maximum at l = 8.10)
      kappa'' suppressed       0.635   (l = 172.75 +- 2.5)        T-121
      matched CAMB             0.772   (206 / 266.750)   T-181; was 0.757
                                       at the pre-repair l_A, and [0.55,
                                       0.80] contains both

    OUTCOMES, fixed in advance:
      in [0.55, 0.80] both frames   W1 succeeds on both gates
      moves but outside             partial; the l=2 row becomes the falsifier
      stays near 0.030              G-a and G-b disagree -- PREDICTION FAILS
      > 0.80 or l > 250             overshoot

**This file reproduces D24's machinery exactly** --- same `ELLS`, same
`K_MAX`, same derived $k$ grid, same parabolic peak finder --- by importing
them, so the number it reports is comparable to T-121's line by line and
cannot drift from it. The only difference is `BULK_SOURCE_CONTROLS`.

**Gate G-b is re-reported beside G-a for every configuration**, because the
pre-registration says both must move together and reporting one of them is
reporting half the question.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# D24 is imported below rather than copied, so this directory has to be
# importable however the script is invoked -- `python3 scripts/d27.py` from
# the root does not put `scripts/` on the path, only the invoking directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d27-gate-a"
VERSION = "v1.3.0"

from functions.background.flrw import PLANCK_N_S  # noqa: E402
from functions.spectra import two_frame as _tf  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402

# **Imported, not re-written.** D24 owns ELLS, K_MAX, ELL_A, the environment
# and the peak finder; a second copy here is a second place for them to drift,
# and T-121's numbers would stop being comparable the first time one moved.
from diagnostic_d24_phi_prime_sweep import (  # noqa: E402
    ELL_A, ELLS, FRAMES, K_MAX, _env, peak_position, spectra_both_frames)

LOW, HIGH = 0.55, 0.80          # the pre-registered interval
TARGET = 206.0 / ELL_A

#: The released path, and the candidate. Two rows, not six: G-b has already
#: refuted `slot_weight_split + thomson_boundary_and_vdot` (124.3) and shown
#: `by_parts_weight_terms` alone to be nearly inert (4.248 -> 3.907), and
#: G-a costs about twenty times G-b per row.
CONFIGS: list[tuple[str, dict]] = [
    ("released (102) as printed", {}),
    ("B_SLOT_REPAIR's combination",
     dict(slot_weight_split=True, jprime_bulk_slot=True,
          thomson_carries_shear=True, boundary_weight_w=False)),
]


def main() -> int:
    print(__doc__)
    env = _env()
    r_theta = float(env.background.eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    print(f"\n{'='*86}\n  GATE G-a --- ell_peak / ell_A.  PRE-REGISTERED "
          f"[{LOW}, {HIGH}].  target {TARGET:.3f}\n"
          f"  PLANCK, r_theta = {r_theta:.4f}, {k_com.size} modes to "
          f"k = {K_MAX:.0f}\n{'='*86}")
    print(f"  {'configuration':<32} {'frame':<10} {'ell_peak':>10} {'+-':>5} "
          f"{'/ell_A':>8}  verdict")
    print("  " + "-" * 82)

    keep = dict(_tf.BULK_SOURCE_CONTROLS)
    results: dict[tuple[str, str], float] = {}
    try:
        for label, cfg in CONFIGS:
            _tf.BULK_SOURCE_CONTROLS = dict(cfg)
            try:
                d_both = spectra_both_frames(env, table, k_com, power)
            except Exception as exc:                      # noqa: BLE001
                print(f"  {label:<32} {'--':<10} RAISED "
                      f"{type(exc).__name__}: {exc}", flush=True)
                continue
            for frame in FRAMES:
                pos, unc = peak_position(ELLS, d_both[frame])
                ratio = pos / ELL_A
                results[(label, frame)] = ratio
                if LOW <= ratio <= HIGH:
                    v = "IN the pre-registered interval"
                elif ratio > HIGH:
                    v = "ABOVE -- overshoot"
                elif ratio < 0.10:
                    v = "near released -- PREDICTION FAILS" if cfg else "(baseline)"
                else:
                    v = "moved, OUTSIDE -- partial"
                print(f"  {label if frame == FRAMES[0] else '':<32} "
                      f"{frame:<10} {pos:10.2f} {unc:5.1f} {ratio:8.4f}  {v}",
                      flush=True)
            print("  " + "-" * 82, flush=True)
    finally:
        _tf.BULK_SOURCE_CONTROLS = keep

    cand = [results.get(("B_SLOT_REPAIR's combination", f)) for f in FRAMES]
    print(f"""
  AGAINST THE PRE-REGISTRATION
  ----------------------------
  predicted: CDM in [{LOW}, {HIGH}], Newtonian within 15% of it.
  measured : CDM {cand[1]!r}, Newtonian {cand[0]!r}

  Read this against section 3 of the pre-registration AS WRITTEN. A result
  outside [{LOW}, {HIGH}] is a FAILED PREDICTION and is reported as one, not
  as a narrower success.

  WHAT THIS RUN CANNOT SETTLE, stated in advance and unchanged:
    - two configurations, not 128. M11a: a configuration absent here is not
      refuted, only not run.
    - PLANCK only. P7 wants both backgrounds; EdS follows if this holds, and
      a PLANCK-only success is not a result until it does.
    - neither gate says the plateau is RIGHT. reference/ carries C_l only
      (T-122), so the comparison against CAMB cannot be made from the bundle.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
