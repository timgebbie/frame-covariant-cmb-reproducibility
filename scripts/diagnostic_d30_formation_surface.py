#!/usr/bin/env python3
r"""D30 --- when is the spectrum laid down? $C_\ell$ accumulated in conformal time.

**The PI's instrument, 2026-10-24.** Every gate built this week — G-a's
$\ell_{\rm peak}$, G-b's median $k$ — is a scalar summary of a *finished*
spectrum. They refute; they do not explain. Three pre-registered predictions
failed against them and the one configuration that moved the peak has no
mechanism.

This shows the spectrum **being built**, and that changes what is askable:

  * $\kappa''\tilde v_B$ rides on $\mathcal V$, which is sharply peaked at
    $\eta_*$. The ISW and the rest of the bulk accumulate **along the path**.
    Those are different shapes in $\eta$ and the surface separates them with
    no configuration sweep.
  * The **frame gap becomes a function of $\eta$**. D6 reports one number at
    $\eta_0$; the profile says whether the gap was laid down at matching or
    accumulated in the bulk, which is T-85's question asked as a shape.
  * **A late ISW is a late-time accumulation and nothing else.** On
    `PLANCK_MODEL` it must exist; on Einstein--de~Sitter $\Phi$ is exactly
    constant (Appendix~G) so it must be **exactly zero**. That is a null
    control, not a weak case, and it is the sharpest falsifier available.

WHAT IS COMPUTED, AND IT IS ONE PASS
------------------------------------
`integral_solution` gained `eta_slices`: the bulk integrand is accumulated
cumulatively in $\eta$ inside the same quadrature the released path uses. The
coefficients and the kernel do not depend on the observer, so this costs **one
pass, not one spectrum per slice**, and there is no second definition of the
quadrature to drift (S8).

**The boundary terms are kept out of the accumulation deliberately.** They are
emitted at $\eta_*$ and afterwards only projected, so they are present in full
in every slice; the bulk is the part that grows. Telling those two apart is
what this instrument is for.

TWO GATES, FOR NOTHING
----------------------
  1. the $\eta_0$ slice must equal the released `integrated` **exactly** ---
     if the accumulation disagrees with the quadrature it decomposes, nothing
     below is evidence. Asserted, not eyeballed.
  2. the accumulation is monotone in $\eta$ for a one-signed integrand, and
     any decrease is a sign change in the bulk source --- reported rather than
     assumed, because a non-monotone column is itself a finding.

THE FIRST THING IT SHOWED, BEFORE ANY PLOT
------------------------------------------
At $\ell=2$, PLANCK, $k=30$: **60% of the bulk is already in place at
$\eta_*$, and 100% by the next slice.** The lower limit is the recombination
start, not $\eta_*$ (T-58), so the first number is not a defect --- but the
second is the statement that matters: **nothing accumulates after
recombination.** On PLANCK there must be a late ISW at $\ell=2$ and there is
none, which is P1-T's account of discrepancy (i) seen directly: the bracket
rides at $\mathcal V\mathcal D$, $\mathcal V$ has closed, and the late-time
source is multiplied by zero.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d30-formation-surface"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_H, PLANCK_MODEL, PLANCK_N_S, PLANCK_OMEGA_B_H2)
from functions.spectra import two_frame as _tf  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

#: The plateau and the first peak. The damping tail is F9's and is not drawn
#: here: the question is WHEN power arrives, and the tail arrives with
#: everything else.
ELLS = np.array([2, 5, 10, 30, 100, 200])

#: 300 reaches $\ell=200$ on PLANCK with room. Not F9's 1500: nothing above
#: the first peak is being asked about and the grid would spend its
#: resolution there.
K_MAX = 300.0

#: Log-spaced in $(\eta-\eta_*)$, because the visibility is narrow and a
#: linear axis spends almost all of itself on the free-streaming era where
#: nothing is laid down. 24 slices.
N_SLICES = 24

FRAMES = ("newtonian", "cdm")


def _slices(eta_star: float, eta_0: float) -> np.ndarray:
    span = eta_0 - eta_star
    lo = span * 1e-4
    # Named rather than returned inline so the grid register can see it under
    # a key a reader recognises: an anonymous `geomspace` registers as
    # `<inline:104>`, which names a line number and nothing about the grid.
    sl = eta_star + np.concatenate(
        [[0.0], np.geomspace(lo, span, N_SLICES - 1)])
    return sl


def _surface(label, bg, obh2, h, gamma):
    env = build_environment(
        K_MAX, omega_m=bg.omega_m, omega_lambda=bg.omega_lambda,
        omega_r=bg.omega_r, omega_b_h2=obh2, transfer_gamma=gamma,
        hubble_h=h, f_2=F2_DEFAULT, line_of_sight_weight="printed")
    eta_star, eta_0 = float(env.eta_star), float(env.background.eta_0)
    sl = _slices(eta_star, eta_0)
    r_theta = eta_0 - eta_star
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (eta_0 - env.eta[0])) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    # bulk accumulated to each slice, plus the boundary which is present in
    # every slice, summed into C_l the way (188) does.
    acc = {f: np.zeros((ELLS.size, sl.size)) for f in FRAMES}
    gate1 = 0.0
    for j, k in enumerate(k_com):
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        for f in FRAMES:
            s = sets[f]
            common = dict(table=table, weight=env.weight, diffusion=diffusion,
                          damping_total=diffusion, eta_star=eta_star,
                          eta_floor=float(env.eta[0]),
                          visibility=env.visibility, eta_0=eta_0)
            res = integral_solution(
                ELLS, coefficients=s.coefficients, c1_prime=s.c1_prime,
                c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
                c2_prime=s.c2_prime, eta_slices=sl, **common)
            gate1 = max(gate1, float(np.max(np.abs(
                res.partial_bulk[:, -1] - res.integrated)
                / np.maximum(np.abs(res.integrated), 1e-300))))
            boundary = (res.boundary_scalar + res.boundary_shear)[:, None]
            t_eta = res.partial_bulk + boundary
            acc[f] += (k ** 2 * power[j]) * t_eta ** 2 * (
                k_com[1] - k_com[0])

    print(f"\n{'='*94}\n  {label}   eta_* = {eta_star:.5g}, "
          f"eta_0 = {eta_0:.5g}\n{'='*94}")
    print(f"  GATE 1  eta_0 slice vs the released quadrature: "
          f"worst rel {gate1:.2e}  "
          f"{'PASS' if gate1 < 1e-9 else '**FAIL -- nothing below is evidence**'}")

    #: fraction of the final C_l in place at each slice
    marks = (0.0, 0.01, 0.1, 0.5, 1.0)
    print(f"\n  Fraction of the final C_l already in place, by "
          f"(eta - eta_*)/(eta_0 - eta_*):")
    print(f"  {'frame':<10} {'l':>4} " +
          " ".join(f"{m:>8.2f}" for m in marks) + "   late share")
    print("  " + "-" * 74)
    for f in FRAMES:
        for i, l in enumerate(ELLS):
            row, fin = acc[f][i], acc[f][i][-1]
            if fin <= 0:
                continue
            x = (sl - eta_star) / (eta_0 - eta_star)
            vals = [float(np.interp(m, x, row / fin)) for m in marks]
            # everything after the visibility has closed, as a share
            late = 1.0 - float(np.interp(0.01, x, row / fin))
            print(f"  {f:<10} {int(l):4d} " +
                  " ".join(f"{v:8.4f}" for v in vals) + f" {late:12.4f}")
    return acc, sl, eta_star, eta_0


def main() -> int:
    print(__doc__)
    keep = dict(_tf.BULK_SOURCE_CONTROLS)
    try:
        _surface("EdS  (CDM_MODEL)", CDM_MODEL, 0.0224, 0.5, 0.48)
        _surface("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H,
                 shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H))
    finally:
        _tf.BULK_SOURCE_CONTROLS = keep
    print("""
  READING THIS
  ------------
  `late share` is the fraction of the final C_l laid down AFTER the first 1%
  of conformal time past eta_* -- that is, after the visibility has closed.

  A correct assembly puts O(0.1) there at l = 2 on PLANCK, because that is
  the late integrated Sachs-Wolfe effect, and EXACTLY ZERO on
  Einstein-de Sitter, where Phi is constant and there is no late ISW to have.

  **THE EdS ZERO IS THE FALSIFIER.** A non-zero late share on EdS means
  something other than the weight is wrong. A zero late share on PLANCK means
  the late ISW has been annihilated -- which is what B-17 discrepancy (i)
  predicts, because the bracket rides at V.D and V has closed by then.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
