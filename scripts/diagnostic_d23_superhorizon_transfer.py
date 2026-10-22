#!/usr/bin/env python3
r"""D23 --- Stage 4(b): the COMPLETE transfer against the SACHS--WOLFE transfer as $k\to0$.

**P1-T's O2. Never run.** D21 settled the *source*: on EdS the scalar
$(\delta T+\Phi_A)-C_2'=\Phi_A/3$ holds to 0.68% at the visibility peak, so
the intrinsic temperature source reproduces the covariant large-scale result
and the plateau failure is **downstream**. Downstream is a large place. This
instrument is the next cut inside it.

THE STATEMENT UNDER TEST
------------------------
On super-horizon scales in matter domination the transfer function must
reduce to the Sachs--Wolfe transfer:

    T_l(k)  ->  (Phi_A(eta_*)/3) . D . j_l(k (eta_0 - eta_*))        as k -> 0

at fixed $\ell$. Both sides vanish like $(k\Delta\eta)^\ell$, so the **ratio**
is what is scored and the common projection factor cancels from it exactly.

WHY THE RATIO AND NOT THE DIFFERENCE
------------------------------------
Finding **M16**: a quantity measured on the coefficients does not become a
statement about the spectrum without the projection in between. D21 measured
coefficients. This measures the projected transfer --- the object (186)
squares --- so a verdict here *is* a statement about the plateau.

HOW THE REFERENCE IS BUILT, AND WHY IT CANNOT DISAGREE BY CONVENTION
--------------------------------------------------------------------
Two routes, and they are required to agree:

  (a) **through the bundle's own machinery.** `transfer_by_rank` is called a
      second time on a coefficient set in which everything is zeroed except
      $C_1=-\Phi_A/3$. `integral_solution` then returns
      `scalar = (C_2'(eta_*) - C_1(eta_*)) D j_l = (Phi_A(eta_*)/3) D j_l`,
      `shear = 0` (because $C_2=0$) and `integrated = 0` (because the bulk
      bracket $C_0-C_1'+C_2''$ is identically zero). Same Bessel table, same
      damping, same $\eta_*$, same (188) downstream. **Nothing about
      normalisation, $\alpha_\ell$ or the weight can enter the ratio.**

  (b) **written out.** $(\Phi_A(\eta_*)/3)\,\mathcal D\,j_\ell(x_*)$, two
      lines, from the same table.

They are printed side by side. If they disagree the reference is wrong and no
verdict below is worth reading --- which is the point of having two.

(a) is only clean while `B_SLOT_REPAIR` is `False`: with it on, `transfer_by_rank`
adds a $+k\int W(-C_1)j_\ell'$ bulk term that a reference carrying $C_1\ne0$
would pick up. The flag is asserted below rather than assumed.

THE COEFFICIENT-LEVEL DECOMPOSITION, DERIVED HERE
-------------------------------------------------
(102)'s rank-0/1 boundary is $[C_2'-C_1]_{\eta_*}$. By (109),

    -C_1 = (dT + Phi_A) + kappa' vhat_B ,          vhat_B = v_B / k

and by the Sachs--Wolfe scalar, $(\delta T+\Phi_A)=\Phi_A/3+C_2'$. Substituting,

    C_2' - C_1  =  Phi_A/3  +  2 C_2'  +  kappa' v_B / k .           (*)

In the Newtonian frame $C_2'\equiv0$ and (*) is $\Phi_A/3+\kappa'v_B/k$ exactly.
**So the Sachs--Wolfe limit is not a property of the source alone: it requires
the Doppler term $\kappa'v_B/k$ to die against $\Phi_A/3$ as $k\to0$.** That is
a statement about what the matching carries to the boundary, and it is
separately checkable. (*) is **verified numerically below**, not asserted:
the residual column is the test of this docstring.

Note what (*) does NOT say. It does not say $\kappa'v_B/k$ is spurious; (89)
puts it there and S48's ledger reviews it, it does not forbid it. It says the
super-horizon limit is where its size is decided, and that nothing in the
register has yet decided it.

WHAT A VERDICT MEANS
--------------------
  ratio -> 1      the transport is right in the limit the plateau lives in,
                  and the plateau defect is at finite k --- the acoustic
                  region bleeding down, not the large-scale limit failing.
  ratio -> const  a scale-independent miscalibration: the plateau has the
                  right SHAPE and the wrong HEIGHT. Then the morphology
                  question splits in two and only one half is open.
  ratio -> grows  the limit does not exist, and the plateau is not a plateau
                  for a reason that is visible at k -> 0 and cheap to chase.

**Which of the three it is was unknown when this file was written.** It is a
measurement and not an argument; nothing downstream of it was drafted first.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d23-superhorizon-transfer"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_H, PLANCK_MODEL, PLANCK_OMEGA_B_H2)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra import two_frame as _tf  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, coefficient_sets, transfer_by_rank)

#: Fixed multipoles, swept DOWN in k. The plateau is built at these.
ELLS = np.array([2, 4, 8, 20])

#: The sweep. `K_MAX` sizes the eta grid and the Bessel table once; every
#: smaller k is then resolved better than it needs to be, which is the safe
#: direction -- finding T-34 is the other one.
K_MAX = 40.0
#: Carried down to 0.025 because the first run settled the Newtonian column by
#: k=2 and left the CDM column still MOVING, toward a value near -1. Whether
#: it reaches -1 exactly is the difference between "the CDM frame has the
#: Sachs-Wolfe limit up to a sign" and "the CDM frame is also wrong, by less".
#: That is not a question to answer by extrapolating four points.
KS = (40.0, 20.0, 10.0, 5.0, 2.0, 1.0, 0.5, 0.25, 0.1, 0.05, 0.025)

FRAMES = ("newtonian", "cdm")


def _zeroed_sw_set(cset, phi_a_over_3: np.ndarray):
    r"""The same CoefficientSet with everything zeroed but $C_1=-\Phi_A/3$.

    Built with `dataclasses.replace` from the live object, so it inherits the
    live $\eta$ grid and $k$ and cannot drift from them. Every derivative is
    zeroed too: the bulk bracket is $C_0-C_1'+C_2''$ and the reference must
    carry **no bulk at all**.
    """
    z = np.zeros_like(phi_a_over_3)
    sc = replace(cset.coefficients, c0=z.copy(), c1=-phi_a_over_3, c2=z.copy())
    return replace(cset, coefficients=sc, c1_prime=z.copy(),
                   c2_second=z.copy(), c2_prime_star=0.0, c2_prime=z.copy(),
                   v_b=z.copy(), a_b1_prime=z.copy())


def _run(label, bg, obh2, h, gamma):
    env = build_environment(
        K_MAX, omega_m=bg.omega_m, omega_lambda=bg.omega_lambda,
        omega_r=bg.omega_r, omega_b_h2=obh2, transfer_gamma=gamma,
        hubble_h=h, line_of_sight_weight="printed")
    eta = np.asarray(env.eta, dtype=float)
    phi_a = np.asarray(env.phi_a, dtype=float)
    kp = np.asarray(env.kappa_prime, dtype=float)
    eta_star = float(env.eta_star)
    eta_0 = float(env.background.eta_0)
    d_eta = eta_0 - eta_star

    needed = required_multipoles(ELLS)
    table = BesselTable.build(ell_max=int(needed.max()), ells=needed,
                              x_max=float(K_MAX * (eta_0 - eta[0])) + 20.0)

    def at_star(arr):
        return float(np.interp(eta_star, eta, np.asarray(arr, dtype=float)))

    phi_star_3 = at_star(phi_a) / 3.0
    print(f"\n{'='*94}\n  {label}   "
          f"eta_* = {eta_star:.4g},  eta_0 = {eta_0:.4g},  "
          f"Phi_A(eta_*)/3 = {phi_star_3:.6e}\n{'='*94}")

    # --- (*) verified, not asserted -------------------------------------
    print("\n  (*)  C_2' - C_1  =  Phi_A/3 + 2 C_2' + kappa' v_B / k   "
          "-- the DERIVATION above, checked")
    print(f"  {'k':>6} {'frame':<10} {'C_2''-C_1':>14} {'Phi_A/3':>12} "
          f"{'2C_2''':>12} {'kappa''v_B/k':>14} {'rel resid':>11}")
    print("  " + "-" * 84)
    for k in KS:
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        for frame in FRAMES:
            s = sets[frame]
            c1s = at_star(s.coefficients.c1)
            c2ps = (0.0 if s.c2_prime is None else at_star(s.c2_prime))
            lhs = c2ps - c1s
            dop = at_star(kp * np.asarray(s.v_b, dtype=float)) / float(k)
            rhs = phi_star_3 + 2.0 * c2ps + dop
            rel = abs(lhs - rhs) / max(abs(lhs), abs(rhs), 1e-300)
            print(f"  {k:6.2f} {frame:<10} {lhs:14.5e} {phi_star_3:12.4e} "
                  f"{2*c2ps:12.4e} {dop:14.5e} {rel:11.2e}")

    # --- the transfer ratio ---------------------------------------------
    print("\n  T_l(k) / T_l^SW(k)   -- 1 if the transfer reduces to "
          "Sachs-Wolfe as k -> 0")
    print("  `bdy` and `bulk` are that ratio's two parts at l=2: the (102) "
          "boundary\n  [C_2'-C_1]D j_l over the same denominator, and the "
          "remainder, which is\n  (102)'s bulk integral. They add to the l=2 "
          "column by construction.")
    print(f"  {'k':>6} {'frame':<10} " +
          " ".join(f"{'l='+str(int(l)):>12}" for l in ELLS) +
          f" {'bdy(l=2)':>11} {'bulk(l=2)':>11} {'ref (a)/(b)':>12}")
    print("  " + "-" * (18 + 13 * ELLS.size + 38))
    out = {}
    for k in KS:
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        x_star = float(k) * d_eta
        damping = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        j_star = np.array([float(table(int(l), np.array([x_star]))[0])
                           for l in ELLS])
        sw_written = phi_star_3 * damping * j_star           # route (b)
        for frame in FRAMES:
            s = sets[frame]
            total = np.asarray(transfer_by_rank(ELLS, float(k), s, env,
                                                table)[-1], dtype=float)
            sw_machine = np.asarray(                          # route (a)
                transfer_by_rank(ELLS, float(k),
                                 _zeroed_sw_set(s, phi_a / 3.0),
                                 env, table)[-1], dtype=float)
            agree = float(np.max(np.abs(sw_machine - sw_written)
                                 / np.maximum(np.abs(sw_written), 1e-300)))
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio = np.where(np.abs(sw_machine) > 0,
                                 total / sw_machine, np.nan)
            out[(k, frame)] = ratio
            # (102)'s boundary at l=2, written out with the SAME table and
            # damping, over the SAME denominator. The remainder is the bulk
            # by subtraction, so the two cannot fail to add to the column.
            c1s = at_star(s.coefficients.c1)
            c2ps = (0.0 if s.c2_prime is None else at_star(s.c2_prime))
            den = sw_written[0]
            bdy = (c2ps - c1s) * damping * j_star[0] / den if den else np.nan
            print(f"  {k:6.3f} {frame:<10} " +
                  " ".join(f"{r:12.4e}" for r in ratio) +
                  f" {bdy:11.3e} {ratio[0]-bdy:11.3e} {agree:12.1e}")
    return out


def main() -> int:
    assert _tf.B_SLOT_REPAIR is False, (
        "route (a) is only a clean reference while B_SLOT_REPAIR is off: "
        "with it on, transfer_by_rank adds +k Int W(-C_1) j_l' and the "
        "reference carries C_1 != 0")
    print(__doc__)
    _run("EdS  (CDM_MODEL, Gamma=0.48, h=0.5)", CDM_MODEL, 0.0224, 0.5, 0.48)
    _run("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H,
         shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H))
    print("""
  READING THIS
  ------------
  The `ref (a)/(b)` column is the reference checking itself: the bundle's own
  machinery against the written-out expression. It must be at machine
  precision. If it is not, STOP -- every ratio beside it is meaningless.

  The ratio columns are the measurement. Read them DOWN, not across: the
  statement is about the k -> 0 LIMIT at fixed l, so what matters is whether
  each column settles, and to what.

  THE NEWTONIAN COLUMN IS THE CLEAN ONE. There C_2' = 0 identically, so (*)
  reads C_2' - C_1 = Phi_A/3 + kappa' v_B / k with nothing else in it, and the
  ratio is decided by one competition: the Doppler term against the
  Sachs-Wolfe one.

  THIS IS NOT A TEST OF C_l. It is a test of the transfer function at fixed l,
  which is the object (186) squares -- so unlike D21 a verdict here carries to
  the spectrum without a further step. That is the whole reason for running
  it after D21 rather than instead of it.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
