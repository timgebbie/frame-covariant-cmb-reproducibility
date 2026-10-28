#!/usr/bin/env python3
r"""D39 --- is the line-of-sight $\eta$ grid converged? **Finding T-164.**

**The PI's question, 2026-10-28:** is the time resolution adequate against the
characteristic physical scales? No gate in this bundle can answer it and no run
had ever asked.

WHY NO EXISTING GATE SEES THIS
------------------------------
F10 asserts that the sliced accumulation reproduces the released quadrature to
$10^{-9}$ --- **on the same grid**. It is an identity between two
decompositions of one sum, so an under-resolved grid passes it exactly. That is
**M14**: a difference-gate blind to a defect common to both sides.

WHAT IS BEING TESTED
--------------------
`required_n_eta` sizes the grid at `ETA_POINTS_PER_PERIOD = 12` samples per
$j_\ell$ zero spacing $\pi/k_{\max}$. The rule is arithmetic against the
physics; **the constant in it is not**. This refines $n_\eta$ at fixed
$k$-grid, fixed $k_{\max}$, fixed everything, and asks whether $C_\ell$ has
stopped moving.

`RecombinationHistory.build` carries its **own** grid, so $\eta_\ast$,
$\kappa'$ and $\mathcal V$ do not move with $n_\eta$. The attribution is to the
quadrature grid alone --- which matters, because scoring a resolution test on
an object that also moved is **M15**.

THE BAND-EDGE CONDITION, BOUGHT CHEAPLY
---------------------------------------
`N_ETA_FLOOR = 8000` lifts every modest-$k_{\max}$ run clear of the rule, so a
released run at $k_{\max}=300$ sits at **26.5** samples per zero and never
exercises the rule at all. The floor stops binding near $k_{\max}\simeq680$,
and F9 and F10 `--high-res` run at $k_{\max}=1500$ --- **12.0** samples per
zero, the rule's own condition.

Running the **derived** count at $k_{\max}=300$ reproduces 12-per-zero exactly.
So *"is 12 enough?"* is answered here for the price of a $k_{\max}=300$ pass
rather than a $k_{\max}=1500$ one.

PRE-REGISTERED
--------------
    converged          1x, 2x and 4x agree to <1e-3 and the derived count
                       agrees with them. The rule is sound and the floor is
                       belt-and-braces.
    floor-dependent    1x/2x/4x agree but the DERIVED count does not. Then
                       every run above k_max ~ 680 carries the gap, which is
                       F9 and F10 --high-res, and the constant is wrong.
    not converged      1x, 2x and 4x do not agree. Then no number in the
                       bundle is resolved and the grid is the first problem.

WHAT THIS CANNOT DECIDE
-----------------------
The grid is `np.linspace` --- **uniform** --- so one knob sets both the samples
per $j_\ell$ zero and the points across the visibility. They cannot be varied
independently, and a displacement found here cannot be attributed to either.
The visibility width is reported alongside for exactly that reason. **S33**
leaves the visibility's own rate underived and `N_ETA_FLOOR` is the patch over
it; T-58 measured $2.4\times10^{-1}$ without that patch against
$5.9\times10^{-3}$ with it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d39-eta-grid-convergence"

from functions.background.flrw import (  # noqa: E402
    PLANCK_H, PLANCK_MODEL, PLANCK_N_S, PLANCK_OMEGA_B_H2)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)
from functions.spectra.pipeline import (  # noqa: E402
    N_ETA_FLOOR, primordial_power, required_k_points, required_n_eta)
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

from _resumable import Checkpoint  # noqa: E402

#: $k_{\max}=300$ so the **derived** count reproduces the 12-per-zero condition
#: that $k_{\max}=1500$ runs at, without paying for $k_{\max}=1500$.
K_MAX = 300.0

#: Spread across the plateau, the rise and the first peak, so a displacement
#: that is a *shape* is distinguishable from one that is a *normalisation*.
#: That distinction is the whole reading: a uniform shift does not move a peak.
ELLS = np.array([2, 30, 100, 200, 250])

#: Refinements of the released grid, plus the derived count itself.
MULTIPLES = (1, 2, 4)

#: Rows per configuration: one $C_\ell$ per multipole. Passed to
#: `Checkpoint.has` so a run killed mid-write is recomputed rather than
#: resumed as complete --- **T-162**.
ROWS_PER_CONFIG = int(ELLS.size)


def _environment(n_eta: int | None):
    return build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2,
        transfer_gamma=shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H),
        hubble_h=PLANCK_H, f_2=F2_DEFAULT, line_of_sight_weight="printed",
        n_eta=n_eta)


def _spectrum(n_eta: int) -> np.ndarray:
    r"""$C_\ell$ at $\eta_0$, CDM frame, on a grid of exactly `n_eta` points."""
    env = _environment(n_eta)
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
        s = coefficient_sets(float(k), env)[1]          # CDM frame
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


def _richardson(values: list[float]) -> float:
    r"""Continuum limit from the last three refinements, at the measured order.

    Quoting a convergence against the finest grid *computed* understates the
    error by exactly the finest grid's own error, which is the quantity in
    question. The limit is extrapolated instead, at the order the sequence
    itself shows rather than at an assumed second order.
    """
    c, b, a = values[-1], values[-2], values[-3]
    d1, d2 = b - a, c - b
    if d2 == 0.0:
        return c
    ratio = d1 / d2
    return c + d2 / (ratio - 1.0) if ratio > 1.0 else c


def main() -> int:
    print(__doc__.split("PRE-REGISTERED")[0])

    probe = _environment(None)
    span = float(probe.background.eta_0) - float(probe.eta[0])
    derived = required_n_eta(K_MAX, span)
    released = max(N_ETA_FLOOR, derived)
    zero_spacing = np.pi / K_MAX

    v = np.asarray(probe.visibility, dtype=float)
    e = np.asarray(probe.eta, dtype=float)
    inside = e[v >= v.max() / 2.0]
    fwhm = float(inside.max() - inside.min())

    print(f"    span {span:.6f}   derived n_eta {derived}   "
          f"floor {N_ETA_FLOOR}   released {released}")
    print(f"    visibility FWHM {fwhm:.4e}\n")

    rows = Checkpoint(ROOT / "diagnostics" / f"{SLUG}.csv",
                      ("n_eta", "samples_per_zero", "visibility_points",
                       "ell", "c_ell"))
    grids = [("derived", derived)] + [(f"{m}x", released * m) for m in MULTIPLES]
    got: dict[str, np.ndarray] = {}

    for label, n in grids:
        key = f"{label} || n_eta={n}"
        if rows.has(key, expect=ROWS_PER_CONFIG):
            got[label] = np.array(
                [float(r["c_ell"]) for r in rows.all()
                 if r["configuration"] == key])
            print(f"    [resumed] {key}", flush=True)
            continue
        acc = _spectrum(n)
        got[label] = acc
        per = zero_spacing / (span / n)
        vis = int(round(fwhm / (span / n)))
        for i, l in enumerate(ELLS):
            rows.add(key, n_eta=n, samples_per_zero=f"{per:.2f}",
                     visibility_points=vis, ell=int(l), c_ell=f"{acc[i]:.9e}")
        print(f"    n_eta {n:7d}  ({label:>7})  {per:6.1f} samples per "
              f"j_l zero   {vis:4d} points across the visibility", flush=True)

    sequence = [got[f"{m}x"] for m in MULTIPLES]
    limit = np.array([_richardson([s[i] for s in sequence])
                      for i in range(ELLS.size)])

    print(f"\n{'='*78}\n  AGAINST THE EXTRAPOLATED CONTINUUM LIMIT\n{'='*78}")
    print(f"  {'ell':>5}" + "".join(f"{lab:>14}" for lab, _ in grids))
    for i, l in enumerate(ELLS):
        print(f"  {int(l):>5}" + "".join(
            f"{(got[lab][i]-limit[i])/limit[i]*100:>13.3f}%"
            for lab, _ in grids))

    worst_derived = max(abs(got["derived"][i] - limit[i]) / limit[i]
                        for i in range(ELLS.size))
    worst_released = max(abs(got["1x"][i] - limit[i]) / limit[i]
                         for i in range(ELLS.size))
    spread = (max((got["derived"][i] - limit[i]) / limit[i]
                  for i in range(ELLS.size))
              - min((got["derived"][i] - limit[i]) / limit[i]
                    for i in range(ELLS.size)))
    print(f"\n  derived count (12.0/zero, which F9 and F10 --high-res use): "
          f"{worst_derived*100:.3f}%")
    print(f"  released grid (floor-lifted):                               "
          f"{worst_released*100:.3f}%")
    print(f"  spread across ell at the derived count:                     "
          f"{spread*100:.3f}%")
    print("""
  A displacement that is UNIFORM in ell is a normalisation and does not move a
  peak. One that varies across ell is a shape, and does. The spread above is
  which of the two this is.

  The grid is uniform, so this cannot attribute a displacement to the Bessel
  sampling rather than to the visibility: one knob sets both. S33, open.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
