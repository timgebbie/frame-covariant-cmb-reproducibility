#!/usr/bin/env python3
r"""D21 --- the Sachs--Wolfe scalar, on the LIVE coefficients.

**P1-T's \S4.1, and it is the cheapest decisive instrument in the register.**
`c1_identity.py` verifies it against fixtures; **it has never been pointed at
the production path.**

THE THEOREM, AND ITS REGIME
---------------------------
In the **large-scale, adiabatic, matter-dominated** limit, in both threadings,

    (dT + Phi_A) - C_2'  =  + Phi / 3 .

$(\delta T+\Phi_A)$ is $a\mathcal B_1/k$. It is a statement about the
*coefficients*, upstream of every weight, every by-parts and every projection,
so it separates "the source assembly is wrong" from "the transport of a right
source is wrong" --- the division v1.3.0 turns on.

**What it does NOT contain, and an earlier draft of this file said it did.**
The expression holds $\delta T$, $\Phi_A$ and $C_2'$ and **nothing else**:
there is no $C_0$ in it, no $C_1'$, and no dipole. So it cannot be broken by a
wrong $C_0$, by a wrong $C_1'$, or by a dipole normalisation, and this
instrument must not be cited as covering any of them. It is a test of the
intrinsic temperature source against the potential, and that is all it is.

**Nor does it hold at arbitrary $k$ and $\eta$** --- the regime is stated
above, and the window below enforces it. Both corrections are P1-T's, against
their own earlier wording and against this file's first draft.

WHY IT IS WORTH RUNNING NOW
---------------------------
The plateau is built from multipoles whose source is $(\delta T+\Phi_A)$, and
P1-T measures that term at **0.15--3.9% of the coefficient it sits in** at
those multipoles, the other 96--99.8% being $\kappa'\hat v_B$. If the scalar
holds, the plateau's source is correct and the failure is entirely downstream;
if it fails, the plateau failure starts before any of that.

**Run in both frames and on both backgrounds, at several $k$ and over the
grid, because the theorem carries no $k$ and no $\eta$ --- so any dependence on
either is itself the finding.**
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d21-sachs-wolfe-scalar"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

KS = (2.0, 10.0, 60.0, 300.0)
#: Large scales: the theorem is a large-scale limit, so it is scored where the
#: mode is still outside the sound horizon. k r_s <= this.
SUPERHORIZON = 0.3


def _report() -> None:
    print(__doc__.split("WHY IT IS WORTH RUNNING")[0])
    print("""
  SCORED AS:   ratio = [ (dT + Phi_A) - C_2' ] / (Phi_A / 3)
  which the theorem puts at 1 everywhere. Reported at the visibility peak and
  as the worst over the super-horizon part of the grid.
""")
    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        eta = np.asarray(env.eta, dtype=float)
        phi_a = np.asarray(env.phi_a, dtype=float)
        i_star = int(np.argmax(np.asarray(env.visibility, dtype=float)))
        print(f"\n{'='*78}\n  {label}\n{'='*78}")
        print(f"  {'k':>5} {'frame':<10} {'ratio at eta_*':>16} {'worst, super-horizon':>22}")
        print("  " + "-" * 60)
        for k in KS:
            n_, c_ = coefficient_sets(float(k), env)
            for frame, s in (("newtonian", n_), ("cdm", c_)):
                a_b1 = np.asarray(s.a_b1, dtype=float)
                c2p = (np.zeros_like(eta) if s.c2_prime is None
                       else np.asarray(s.c2_prime, dtype=float))
                lhs = a_b1 / float(k) - c2p
                rhs = phi_a / 3.0
                with np.errstate(divide="ignore", invalid="ignore"):
                    ratio = np.where(np.abs(rhs) > 0, lhs / rhs, np.nan)
                # super-horizon window, from the acoustic sound horizon
                from functions.spectra.acoustic import sound_horizon_from_zero
                e_rs, rs = sound_horizon_from_zero(bg, float(eta[-1]),
                                                   omega_b_h2=obh2)
                rs_on_grid = np.interp(eta, e_rs, rs)
                win = (float(k) * rs_on_grid <= SUPERHORIZON) & np.isfinite(ratio)
                worst = (float(np.max(np.abs(ratio[win] - 1.0))) if win.sum()
                         else float("nan"))
                print(f"  {k:5.0f} {frame:<10} {ratio[i_star]:16.6f} {worst:22.3e}")
    print("""
  READING THIS
  ------------
  Inside its regime the ratio should be 1. A ratio that is 1 there says the
  intrinsic temperature source reproduces the covariant large-scale result, and
  the plateau failure is then entirely downstream -- in the weight, the
  by-parts or the projection. A ratio that is not 1, or that depends on k or
  eta, says the failure starts in the coefficients, before any of that.

  The Newtonian column has C_2' identically zero, so there the test is
  (dT + Phi_A) = Phi_A/3 alone and nothing can hide in the rank-two slot.

  THIS IS NOT A TEST OF THE SPECTRUM. It is the division between "wrong
  source" and "wrong transport of a right source", which is the question
  v1.3.0 exists to answer and the one five withdrawn repairs never posed.
""")


def main() -> int:
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _report()
    text = buf.getvalue()
    print(text, end="")
    out = ROOT / "diagnostics" / f"{SLUG}-{VERSION}.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
