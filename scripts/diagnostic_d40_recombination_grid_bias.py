#!/usr/bin/env python3
r"""D40 --- does the recombination grid carry the bias `c12` predicts?

**P1T->P1B 2026-10-29 #13.** `c12` derives, for a uniform grid accumulating
$\kappa$ from $\kappa'$ by trapezoid,

    d(Int V) / Int V  =  -(h kappa'(eta_*))^2 / 12 ,

negative, so **a coarse grid lowers the visibility**. The error is in the
*construction* of $\kappa$ and not in the sampling of $\mathcal V$: a uniform
grid integrating a smooth $\mathcal V$ that decays at both ends errs only by
aliasing, which the band-limit argument makes negligible.

`RecombinationHistory.build` takes `n_eta = 4000` over the whole span, which
the rule puts near 11 samples across the FWHM and an error near
$4\times10^{-3}$.

WHY THIS IS NOT ALREADY ANSWERED BY D39
---------------------------------------
**D39 refined the line-of-sight grid with this one held at 4000 throughout.**
So if the bias is there it sits in **every row of that sweep equally** ---
including the Richardson limit T-164's 0.95\% is measured against. *A
refinement cannot see an error frozen into a grid it does not refine*, and
quoting a convergence against a contaminated limit would be a true number
about the wrong object (**M15**).

So this refines the grid D39 held fixed, and asks the same three questions of
it: does the bias exist, does it follow the predicted law, and does the
spectrum inherit it.

PRE-REGISTERED
--------------
    law holds        Int V falls as 1/n^2 with the coefficient c12 derives,
                     sign negative. Then n_eta = 4000 carries a known bias,
                     T-164's limit inherits it, and both must be requoted
                     against a limit refined in BOTH grids.
    law holds, bias  the law is right and 4000 is already converged, because
    negligible       the FWHM is wider in units of h than the rule's worst
                     case. Then D39 stands as measured and #13 closes.
    law fails        the construction is not what c12 models -- the history
                     may not accumulate kappa by trapezoid on this grid at
                     all -- and the rule needs restating before it governs a
                     graded grid.

WHAT IS SCORED
--------------
`Int V d eta` and `max V`, which are what c12's derivation speaks about, and
then **the spectrum**, because a bias in the visibility that does not reach
$C_\ell$ is not a defect in the released numbers.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d40-recombination-grid-bias"

from functions.background.flrw import (  # noqa: E402
    PLANCK_H, PLANCK_MODEL, PLANCK_N_S, PLANCK_OMEGA_B_H2, Background)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import (  # noqa: E402
    F2_DEFAULT, RecombinationHistory)
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)
from functions.spectra.pipeline import (  # noqa: E402
    primordial_power, required_k_points)
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

#: The released count, and refinements of it. 4000 is `build`'s default and
#: is what every number in this bundle has been computed on.
RELEASED_N = 4000
FACTORS = (1, 2, 4, 8)

#: Spread across plateau, rise and first peak, as D39's is, so a displacement
#: that is a shape is distinguishable from one that is a normalisation.
ELLS = np.array([2, 30, 100, 200, 250])
K_MAX = 300.0

#: **`--high-ell`, the run T-172 calls for.** The released axis stops at
#: $\ell=250$ and the bias measured there is 0.82\% and still climbing. The
#: question that matters is whether it keeps climbing where the **secondaries**
#: are: from $\ell_A=272.18$ they fall near $\ell\simeq539$ and
#: $\ell\simeq811$, which $k_{\max}=300$ cannot carry at all.
#:
#: Two configurations rather than four --- the released grid and $\times4$ ---
#: because the law is already established at $k_{\max}=300$ and what is wanted
#: here is the $\ell$-dependence, not another convergence sequence.
#:
#: **What it will show, said before it runs.** If the bias is a genuine shape
#: it keeps growing past $\ell=250$; if it saturates near 1\%, it is a
#: slowly-varying envelope after all and cannot remove a feature either, and
#: the secondaries are left to the assembly. **Saturation is the outcome that
#: refutes the lead**, and it is the one being tested.
HIGH_ELL = "--high-ell" in sys.argv
if HIGH_ELL:
    ELLS = np.array([2, 30, 100, 200, 250, 300, 400, 500, 539, 600,
                     700, 811, 900])
    K_MAX = 1500.0
    SLUG = SLUG + "-high-ell"


def _history(n_eta: int) -> RecombinationHistory:
    return RecombinationHistory.build(
        Background(omega_m=PLANCK_MODEL.omega_m,
                   omega_lambda=PLANCK_MODEL.omega_lambda,
                   omega_r=PLANCK_MODEL.omega_r),
        omega_b_h2=PLANCK_OMEGA_B_H2, h=PLANCK_H, n_eta=n_eta)


def _visibility_moments(rec) -> tuple[float, float, float, float, float]:
    r"""$\int\mathcal V$, $\max\mathcal V$, $\eta_\ast$, FWHM, $\kappa'(\eta_\ast)$."""
    eta = np.asarray(rec.eta, dtype=float)
    vis = np.asarray(rec.visibility, dtype=float)
    kp = np.asarray(rec.kappa_prime, dtype=float)
    total = float(np.trapezoid(vis, eta))
    peak = float(vis.max())
    star = float(rec.eta_star)
    inside = eta[vis >= peak / 2.0]
    fwhm = float(inside.max() - inside.min()) if inside.size > 1 else float("nan")
    kp_star = float(np.interp(star, eta, kp))
    return total, peak, star, fwhm, kp_star


def _spectrum(n_eta: int) -> np.ndarray:
    r"""$C_\ell$ at $\eta_0$, CDM frame, with the history built at `n_eta`.

    The line-of-sight grid is left at its released size throughout --- the
    whole point is to move the grid D39 held fixed and nothing else.
    """
    env = build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2,
        transfer_gamma=shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H),
        hubble_h=PLANCK_H, f_2=F2_DEFAULT, line_of_sight_weight="printed",
        recombination_n_eta=n_eta)
    eta_star, eta_0 = float(env.eta_star), float(env.background.eta_0)
    floor = float(env.eta[0])
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, eta_0 - eta_star))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (eta_0 - floor)) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    acc, dk = np.zeros(ELLS.size), k_com[1] - k_com[0]
    for j, k in enumerate(k_com):
        s = coefficient_sets(float(k), env)[1]
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        res = integral_solution(
            ELLS, coefficients=s.coefficients, c1_prime=s.c1_prime,
            c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
            c2_prime=s.c2_prime, eta_slices=np.array([eta_0]), table=table,
            weight=env.weight, diffusion=diffusion, damping_total=diffusion,
            eta_star=eta_star, eta_floor=floor, visibility=env.visibility,
            eta_0=eta_0)
        total = res.integrated + res.boundary_scalar + res.boundary_shear
        acc += (k ** 2 * power[j]) * total ** 2 * dk
    return acc


def main() -> int:
    print(__doc__.split("PRE-REGISTERED")[0])

    rows = []
    for f in FACTORS:
        n = RELEASED_N * f
        rec = _history(n)
        total, peak, star, fwhm, kp_star = _visibility_moments(rec)
        span = float(rec.eta[-1] - rec.eta[0])
        h = span / (n - 1)
        rows.append((n, h, total, peak, star, fwhm, kp_star))

    n0, h0, t0, p0, s0, w0, kp0 = rows[0]
    print(f"    span {float(h0*(n0-1)):.6f}   eta_* {s0:.6f}   "
          f"kappa'(eta_*) {kp0:.2f}   FWHM {w0:.6e}")
    print(f"    released n_eta {n0}: {w0/h0:.1f} samples across the FWHM\n")

    print(f"    {'n_eta':>7} {'h kappa_*':>11} {'Int V':>14} {'max V':>14} "
          f"{'predicted dI/I':>16} {'observed':>13}")
    finest = rows[-1][2]
    for n, h, total, peak, star, fwhm, kp_star in rows:
        predicted = -((h * kp_star) ** 2) / 12.0
        observed = (total - finest) / finest
        print(f"    {n:7d} {h*kp_star:11.4f} {total:14.9f} {peak:14.4f} "
              f"{predicted:16.3e} {observed:13.3e}")

    print(f"""
    `predicted` is c12's -(h kappa'(eta_*))^2 / 12 for that grid.
    `observed` is Int V against the finest grid computed, so the finest row
    reads zero by construction and the comparison is of the OTHERS to it.
    The law holds if the two columns track, and the sign must be NEGATIVE:
    a coarse grid lowers the visibility.
""")

    print(f"{'='*78}\n  DOES THE SPECTRUM INHERIT IT?\n{'='*78}")
    spec = {}
    for f in ((1, 4) if HIGH_ELL else FACTORS[:3]):
        n = RELEASED_N * f
        spec[n] = _spectrum(n)
        print(f"    recombination n_eta = {n:6d}  done", flush=True)

    base = spec[RELEASED_N]
    fine = spec[RELEASED_N * 4]
    print(f"\n    {'ell':>5} {'released':>16} {'refined x4':>16} {'rel':>12}")
    worst = 0.0
    for i, l in enumerate(ELLS):
        rel = abs(base[i] - fine[i]) / max(abs(fine[i]), 1e-300)
        worst = max(worst, rel)
        print(f"    {int(l):>5} {base[i]:16.9e} {fine[i]:16.9e} {rel:12.3e}")
    print(f"""
    WORST {worst:.3e}

    T-164 measures 0.95 per cent on the line-of-sight grid against a limit
    extrapolated with THIS grid held at {RELEASED_N}. If the number above is
    comparable, that limit is contaminated and T-164's figure is the sum of
    two errors rather than one. If it is far smaller, D39 stands as measured.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
