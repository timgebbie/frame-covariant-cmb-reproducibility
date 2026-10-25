#!/usr/bin/env python3
r"""D29 --- B-17's identity, run for the first time, at RELEASED $\kappa''$.

**Why this file exists: the identity had never been implemented.**

B-17 discrepancy (i) says the whole bracket $C_0-C_1'+C_2''$ belongs at $W$
and (102) carries it at $\mathcal V\mathcal D$. Both P1-T's §5 and my own D26
labelling took `slot_weight_split` to be the control for that. **It is not.**
It *splits* $C_1'$ — gravitational half to $W$, Thomson half left at
$\mathcal V$ — which is T-88's physics argument and a different claim, and it
leaves $\kappa''\tilde v_B$ (99.8% of $|C_1'|$, T-121) exactly where it was.

The exact by-parts is $-(WC_1)'=-W'C_1-WC_1'$: **the whole of $C_1'$ travels
at $W$**, and $-\mathcal VC_1$ is a separate term. So every configuration
labelled "the identity" so far was `slot_weight_split` plus partners.
`bracket_all_at_w` is the real one and was added today.

WHERE THIS STANDS, SO THE RUN CAN FAIL
--------------------------------------
    PLANCK, CDM, ell_peak / ell_A, target 0.757 (CAMB ell = 206)

      released                                            0.0298
      kappa''=0 only                               (knob) 0.6467
      kappa''=0 + by_parts alone                   (knob) 0.0294   destroys it
      kappa''=0 + by_parts + slot_weight_split     (knob) 0.7108
      by_parts + slot + vdot + boundary_weight_w  RELEASED 0.8691   overshoot
                                        Newtonian RELEASED 0.2770

The last row is the first peak this bundle has produced **without a knob**,
and it confirmed P1-T's §3 prediction: `thomson_boundary_and_vdot` was
refuted by its own company, and adding `boundary_weight_w` — the control for
discrepancy (iii) — transforms it.

**It also overshoots in CDM and undershoots in the Newtonian frame by a
factor of 3.1 between them.** A repair that lands the peak in one frame and
not the other is not the repair, because $\ell\ge2$ is frame-invariant at
first order.

PRE-REGISTERED, before this runs
--------------------------------
    The identity (bracket_all_at_w + by_parts + boundary_weight_w, at
    RELEASED kappa'') gives ell_peak / ell_A within [0.60, 0.90] in BOTH
    frames, and the two frames within 25% of each other.

    Reasoning, so it can be wrong for a stated reason: discrepancy (i) at
    full strength removes the surplus kappa' from kappa'' vhat_B as well as
    from C_0 and C_2'', which slot_weight_split does not. If the frame
    spread is the Thomson half sitting at the wrong weight, moving it closes
    the spread. If the spread survives, it is not the weight and the
    remaining asymmetry is rank two.

    OUTCOMES, fixed now:
      both in [0.60, 0.90], spread < 25%   the identity IS the repair; W2
      CDM lands, Newtonian does not        the weight is not the frame defect
      neither moves from released          (i) is not the peak at all
      worse than the cross-B row           the partners need (iii) and this
                                           configuration omits something
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d29-the-identity"
VERSION = "v1.3.0"

from functions.background.flrw import PLANCK_N_S  # noqa: E402
from functions.spectra import coefficients as _co  # noqa: E402
from functions.spectra import two_frame as _tf  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402

from _resumable import Checkpoint  # noqa: E402
from diagnostic_d24_phi_prime_sweep import (  # noqa: E402
    ELL_A, ELLS, FRAMES, K_MAX, _env, peak_position, spectra_both_frames)

LOW, HIGH, SPREAD = 0.60, 0.90, 0.25
TARGET = 206.0 / ELL_A

#: All at RELEASED kappa'' = 1. The knob is finished with; what is left is
#: whether the identity stands on its own.
CONFIGS: list[tuple[str, dict]] = [
    # **Trimmed 2026-10-24.** The comparison rows are dropped: cross B's
    # 0.8691/0.2770 is already measured in D28 and re-running it costs twenty
    # minutes to reproduce a number I have. What is NOT measured is the
    # identity, and three long runs have now been lost to container restarts
    # part-way. Two configurations is what completes.
    #
    # Cross B as labelled is also WRONG under T-125 -- `by_parts` was
    # discarded there -- so re-running it here would have reproduced
    # slot+vdot+boundary_weight_w under a name that no longer means that.
    ("THE IDENTITY  (i)+(ii)+(iii)",
     dict(bracket_all_at_w=True, by_parts_weight_terms=True,
          boundary_weight_w=True)),
    ("(i) alone  --- the bracket at W, nothing else",
     dict(bracket_all_at_w=True)),
]


def main() -> int:
    print(__doc__)
    assert _co.KAPPA_SECOND_LAMBDA == 1.0, (
        "this instrument is about the RELEASED kappa''; the knob must be 1.0")
    env = _env()
    r_theta = float(env.background.eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    print(f"\n{'='*92}\n  ell_peak / ell_A at RELEASED kappa''.  "
          f"PRE-REGISTERED [{LOW}, {HIGH}] BOTH frames, spread < {SPREAD:.0%}."
          f"\n  target {TARGET:.3f}.  PLANCK, {k_com.size} modes to "
          f"k = {K_MAX:.0f}\n{'='*92}")
    print(f"  {'configuration':<48} {'frame':<10} {'l_peak':>9} {'/ell_A':>8}")
    print("  " + "-" * 80)

    # **Checkpointed --- finding T-127.** Four long runs were lost part-way to
    # container restarts and relaunched from zero. A row is written and
    # fsync'd the moment it completes, and a rerun skips what is already
    # there, so the table completes whichever process computed which part.
    rows = Checkpoint(ROOT / "diagnostics" / "d29-the-identity.csv",
                      ("frame", "l_peak", "ratio"))
    keep = dict(_tf.BULK_SOURCE_CONTROLS)
    got: dict[str, dict[str, float]] = {}
    try:
        for label, cfg in CONFIGS:
            if rows.has(label):
                for r in rows.all():
                    if r["configuration"] == label:
                        got.setdefault(label, {})[r["frame"]] = float(r["ratio"])
                        print(f"  {label:<48} {r['frame']:<10} "
                              f"{float(r['l_peak']):9.2f} "
                              f"{float(r['ratio']):8.4f}   [resumed]",
                              flush=True)
                print("  " + "-" * 80, flush=True)
                continue
            _tf.BULK_SOURCE_CONTROLS = dict(cfg)
            try:
                d = spectra_both_frames(env, table, k_com, power)
            except Exception as exc:                      # noqa: BLE001
                print(f"  {label:<48} {'--':<10} RAISED "
                      f"{type(exc).__name__}: {exc}", flush=True)
                continue
            got[label] = {}
            for f in FRAMES:
                pos, _ = peak_position(ELLS, d[f])
                got[label][f] = pos / ELL_A
                rows.add(label, frame=f, l_peak=f"{pos:.4f}",
                         ratio=f"{pos / ELL_A:.6f}")
                print(f"  {label if f == FRAMES[0] else '':<48} {f:<10} "
                      f"{pos:9.2f} {pos/ELL_A:8.4f}", flush=True)
            print("  " + "-" * 80, flush=True)
    finally:
        _tf.BULK_SOURCE_CONTROLS = keep

    key = "THE IDENTITY  (i)+(ii)+(iii)"
    if key in got:
        n, c = got[key]["newtonian"], got[key]["cdm"]
        spread = abs(n - c) / max(abs(n), abs(c), 1e-300)
        inside = LOW <= n <= HIGH and LOW <= c <= HIGH
        print(f"""
  AGAINST THE PRE-REGISTRATION
  ----------------------------
    predicted  both in [{LOW}, {HIGH}], frames within {SPREAD:.0%}
    measured   Newtonian {n:.4f}, CDM {c:.4f}, spread {spread:.1%}
    verdict    {'BOTH INSIDE' if inside else 'OUTSIDE — PREDICTION FAILS'}, """
              f"""spread {'within' if spread < SPREAD else 'OVER'} tolerance

  Read against the outcomes fixed in the header AS WRITTEN. A frame spread
  over tolerance is a failure even if one frame lands on target, because
  ell >= 2 is frame-invariant at first order and a repair that is right in
  one threading is not right.
""")
    print("""  STANDING CAVEATS, unchanged: PLANCK only (P7 wants EdS too, and it is
  what withdrew the CDM boundary sign); four configurations of 128; and
  neither gate says the plateau is RIGHT -- reference/ carries C_l only.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
