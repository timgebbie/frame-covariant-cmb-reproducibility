#!/usr/bin/env python3
r"""D25 --- where in $k$ does each low-$\ell$ $C_\ell$ actually come from?

**Coordination's \S7, 2026-10-22, and it closes a gap P1-T and I had both
written down as a caveat rather than measured.**

T-117 established that the transfer misses the Sachs--Wolfe limit by
$9.4\times10^3$ (Newtonian) and $-1.10$ (CDM) as $k\to0$. Both of us then
wrote, in almost the same words, *"each $\ell$ integrates a different $k$
range"* and left it there. That sentence is the whole obstacle between a
$k\to0$ result and a statement about the plateau, and **it is a measurement,
not a caveat.**

WHAT IS COMPUTED
----------------
`cl_covariant_route` integrates `k**2 * power * transfer**2` in `dk`, so

    dC_l/dln k  =  k * (k^2 P(k) |T_l(k)|^2)  =  k^3 P |T_l|^2

and it is formed **from the same array the released route integrates**, not
rebuilt from the formula, so there is one definition and it cannot drift.
Reported per $\ell$:

  * the **median** $k$ --- the $k$ below which half the power lies;
  * the share from $k\le0.1$, where T-117's limit is settled and flat;
  * the share from $k\ge2$, where T-117 says the departure from Sachs--Wolfe
    is legitimate and carries **no** verdict;
  * the $k$ at which $\mathrm dC_\ell/\mathrm d\ln k$ peaks.

THE READING, FIXED IN ADVANCE
-----------------------------
  most of D_2..D_10 from k <= 0.1    T-117's defect IS the plateau: the
                                     sign-flipped CDM boundary and the 9.4e3
                                     Newtonian bulk reach the observable, and
                                     the missing connection is made with a
                                     number.
  most from k >= 2                   T-117 CANNOT be the plateau. The plateau
                                     lives where the transfer legitimately
                                     departs, which moves the whole question
                                     and is worth knowing before any repair.
  spread across both                 the decomposition is itself the answer:
                                     a k -> 0 instrument can never settle an
                                     ell-space failure, and we stop expecting
                                     one to.

WHAT THIS DOES **NOT** DO
-------------------------
It decomposes **the bundle's own** $C_\ell$. It says where the bundle's power
comes from, not whether that is right. The comparison that would make it a
verdict is the same decomposition of the matched CAMB spectrum, and
`reference/` carries **only $C_\ell$** --- `camb-tt-v1.2.0.csv` and
`class-tt-v1.2.0.csv` are two columns, `ell` and `cl_tt_muK2`, with no per-$k$
transfer in either. That was Coordination's open question and this is the
answer: **the comparison cannot be made from what the bundle holds.** So D25
answers *can a $k\to0$ measurement reach the plateau* and does not answer *is
the plateau right*. **M16**, stated rather than discovered later.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d25-k-decomposition"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_H, PLANCK_MODEL, PLANCK_N_S, PLANCK_OMEGA_B_H2)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, coefficient_sets, transfer_by_rank)

#: The plateau's own multipoles. D25 is about the plateau; the acoustic band
#: is F9's and D24's and is not re-measured here.
#: **173 added 2026-10-23, on P1-T's §6.** The first four are the plateau. 173
#: is where the $\kappa''$-suppressed first peak sits ($\ell=172.75$, T-121),
#: and the question there is different: if the peak position is *entirely* the
#: displaced $k\to\ell$ map, the ratio at the peak must be $\simeq1/0.635=1.57$
#: — the bottom of the 1.5–4.2 range, because the peak sits where the
#: displacement is least. A ratio of 1 there instead says the projection is
#: **not** displaced at the peak and $0.635$ needs another cause.
ELLS = np.array([2, 5, 10, 30, 173])

#: 200 is well past $\ell=30$ ($\ell\simeq k r_\theta$ puts it near $k=10$) and
#: is **not** F9's 1500: nothing above the plateau is being asked about, and a
#: grid sized for the damping tail would spend its resolution there.
K_MAX = 700.0

#: The two windows T-117 defines. `K_LOW` is where its limit is settled and
#: flat; `K_HIGH` is where it explicitly carries no verdict.
K_LOW, K_HIGH = 0.1, 2.0

FRAMES = ("newtonian", "cdm")


def _decompose(label, bg, obh2, h, gamma) -> None:
    env = build_environment(
        K_MAX, omega_m=bg.omega_m, omega_lambda=bg.omega_lambda,
        omega_r=bg.omega_r, omega_b_h2=obh2, transfer_gamma=gamma,
        hubble_h=h, f_2=F2_DEFAULT, line_of_sight_weight="printed")
    r_theta = float(env.background.eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    transfer = {f: np.zeros((ELLS.size, k_com.size)) for f in FRAMES}
    for j, k in enumerate(k_com):
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        for f in FRAMES:
            transfer[f][:, j] = transfer_by_rank(ELLS, float(k), sets[f],
                                                 env, table)[-1]

    print(f"\n{'='*86}\n  {label}   r_theta = {r_theta:.4f}, "
          f"{k_com.size} modes to k = {K_MAX:.0f}\n{'='*86}")
    print(f"  {'frame':<10} {'l':>3} {'median k':>10} {'peak k':>9} "
          f"{'share k<=0.1':>13} {'share k>=2':>11} {'l ~ k r_theta':>14}")
    print("  " + "-" * 80)
    for f in FRAMES:
        for i, l in enumerate(ELLS):
            # **The released integrand**, exactly as `cl_covariant_route`
            # forms it. dC/dln k is that times k.
            integrand = k_com ** 2 * power * transfer[f][i] ** 2
            total = float(np.trapezoid(integrand, k_com))
            if total <= 0.0:
                print(f"  {f:<10} {int(l):3d}   (no power)")
                continue
            cum = np.concatenate([[0.0], np.cumsum(
                0.5 * (integrand[1:] + integrand[:-1]) * np.diff(k_com))])
            frac = cum / total
            median_k = float(np.interp(0.5, frac, k_com))
            low = float(np.interp(K_LOW, k_com, frac))
            high = 1.0 - float(np.interp(K_HIGH, k_com, frac))
            peak_k = float(k_com[int(np.argmax(integrand * k_com))])
            print(f"  {f:<10} {int(l):3d} {median_k:10.3f} {peak_k:9.3f} "
                  f"{low:13.4f} {high:11.4f} {float(l)/r_theta:14.3f}")


def main() -> int:
    print(__doc__)
    _decompose("EdS  (CDM_MODEL, Gamma=0.48, h=0.5)",
               CDM_MODEL, 0.0224, 0.5, 0.48)
    _decompose("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H,
               shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H))
    print(f"""
  READING THIS
  ------------
  `share k<=0.1` is the fraction of C_l drawn from the window where T-117's
  verdict holds. `share k>=2` is the fraction from the window where T-117
  explicitly carries NO verdict. The last column is the naive expectation
  l ~ k r_theta inverted -- if `median k` tracks it, the projection is doing
  what a projection does and nothing exotic is happening in between.

  A large `share k<=0.1` at l = 2..10 means T-117 reaches the plateau and the
  two findings are one. A small one means they are not, and the plateau must
  be chased where the power actually is.

  THE COMPARISON THAT WOULD MAKE THIS A VERDICT CANNOT BE MADE HERE:
  reference/ carries C_l only, for both CAMB and CLASS. See the header.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
