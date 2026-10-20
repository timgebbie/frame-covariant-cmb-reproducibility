#!/usr/bin/env python3
r"""D13 --- the by-parts identity, direct against integrated-by-parts, in both frames.

**P1-T, 2026-10-20, and it displaces their own boundary test of the day
before.** That version zeroed the boundary and integrated from `eta_floor` in
**one** frame. This runs the $2\times2$ --- same cost, and it answers the
question the one-frame version cannot.

THE IDENTITY, which is P1-T's and is exact, with $W=e^{-\kappa}$ and
$\mathcal V=W'$ (the bundle's sign convention: `kappa` is built as
`forward[-1] - forward`, so $W'=+\kappa'e^{-\kappa}=+\mathcal V$):

    Int V M j_l d.eta  =  [ W M j_l ]  -  Int W M' j_l d.eta  +  k Int W M j_l' d.eta
    \_______________/     \_________________________________________________________/
         DIRECT (A)                        BY-PARTS (B)

with $x=k(\eta_0-\eta)$, so $\mathrm dj_\ell/\mathrm d\eta=-k\,j_\ell'(x)$ and
the sign on the last term is $+k$.

THE FOUR NUMBERS, identical histories and identical endpoints in every cell:

                  direct      by-parts
    Newtonian       A_N          B_N
    CDM             A_C          B_C

    A_N != B_N  or  A_C != B_C   ->  BOOKKEEPING, in whichever frame fails,
                                     and the eta_*-boundary-against-eta_floor
                                     mixing is the first suspect.
    both hold but A_N != A_C     ->  COEFFICIENT DEFINITIONS, upstream of
                                     (102). The constructor conclusion,
                                     proven rather than inferred.
    both                         ->  COMBINATION, and the sizes apportion it.

**$M$ is the rank-1 transport source $-C_1$**, which is where P1-T's items 2
and 3 live: the slot that takes $M$'s by-parts residue under $W$ and
$(v_b+\sigma)$ under $g$, and gives them one weight.

**M11b, stated before the numbers are read.** $A$ and $B$ are the *same*
integral by an exact identity, so any difference is quadrature or bookkeeping
and nothing else --- there is no third explanation available, which is what
makes this test decisive rather than suggestive. The quadrature floor is
measured here by refining the grid, **not assumed**, and reported beside every
cell: a cell is a FAIL only against its own measured floor.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

ELLS = (2, 10, 50, 200)
SLUG = "d13-byparts-2x2"
VERSION = "v1.3.0"

KS = (10.0, 60.0, 300.0)


def j_and_jprime(table, ell, x):
    """$j_\\ell(x)$ and $j_\\ell'(x)$ from the recurrence, not from a spline.

    $j_\\ell' = \\frac{\\ell\\,j_{\\ell-1} - (\\ell+1)\\,j_{\\ell+1}}{2\\ell+1}$ ---
    exact, and finding **T-23**'s rule: a derivative comes from a published
    relation rather than from differentiating a table.
    """
    jl = np.asarray(table(ell, x), dtype=float)
    jm = np.asarray(table(ell - 1, x), dtype=float)
    jp = np.asarray(table(ell + 1, x), dtype=float)
    return jl, (ell * jm - (ell + 1) * jp) / (2 * ell + 1)


def cell(eta, k, ell, table, M, W, V, eta_0):
    """`(A, B)` --- the one integral, both ways, on identical endpoints."""
    x = k * (eta_0 - eta)
    jl, jlp = j_and_jprime(table, ell, x)
    Mp = np.gradient(M, eta, edge_order=2)

    direct = np.trapezoid(V * M * jl, eta)
    boundary = (W * M * jl)[-1] - (W * M * jl)[0]
    bulk = -np.trapezoid(W * Mp * jl, eta) + k * np.trapezoid(W * M * jlp, eta)
    return float(direct), float(boundary + bulk), float(boundary)


def _report() -> None:
    print(__doc__.split("THE IDENTITY")[0])
    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        eta, eta_0 = env.eta, float(env.background.eta_0)
        W, V = env.opacity, env.visibility
        table = BesselTable.build(
            max(ELLS) + 2, max(KS) * eta_0 + 20.0,
            ells=np.unique(np.concatenate([[e - 1, e, e + 1] for e in ELLS])))

        print(f"\n================ {label} ================")
        print(f"  {'k':>5s} {'l':>4s} | {'A_N':>12s} {'B_N':>12s} {'|A-B|/|A|':>11s}"
              f" | {'A_C':>12s} {'B_C':>12s} {'|A-B|/|A|':>11s}"
              f" | {'|A_N-A_C|/max':>13s}")
        print("  " + "-" * 104)
        for k in KS:
            n_, c_ = coefficient_sets(float(k), env)
            M_N = -np.asarray(n_.coefficients.c1, dtype=float)
            M_C = -np.asarray(c_.coefficients.c1, dtype=float)
            for ell in ELLS:
                an, bn, _ = cell(eta, k, ell, table, M_N, W, V, eta_0)
                ac, bc, _ = cell(eta, k, ell, table, M_C, W, V, eta_0)
                rn = abs(an - bn) / abs(an) if an else float("nan")
                rc = abs(ac - bc) / abs(ac) if ac else float("nan")
                sc = max(abs(an), abs(ac))
                print(f"  {k:5.0f} {ell:4d} | {an:12.4e} {bn:12.4e} {rn:11.3e}"
                      f" | {ac:12.4e} {bc:12.4e} {rc:11.3e}"
                      f" | {abs(an - ac) / sc if sc else float('nan'):13.4e}")

        # ---- the quadrature floor, measured rather than assumed (M11b) ------
        print(f"\n  quadrature floor for {label}: the same cell on a grid "
              f"refined 1x / 2x / 4x")
        print(f"  {'k':>5s} {'l':>4s} {'|A-B|/|A| @1x':>15s} {'@2x':>12s} {'@4x':>12s}")
        print("  " + "-" * 50)
        for k in (10.0, 300.0):
            n_, _ = coefficient_sets(float(k), env)
            M_N = -np.asarray(n_.coefficients.c1, dtype=float)
            for ell in (2, 200):
                row = []
                for mult in (1, 2, 4):
                    if mult == 1:
                        e2, M2, W2, V2 = eta, M_N, W, V
                    else:
                        e2 = np.linspace(eta[0], eta[-1], (len(eta) - 1) * mult + 1)
                        M2 = np.interp(e2, eta, M_N)
                        W2, V2 = np.interp(e2, eta, W), np.interp(e2, eta, V)
                    a, b, _ = cell(e2, k, ell, table, M2, W2, V2, eta_0)
                    row.append(abs(a - b) / abs(a) if a else float("nan"))
                print(f"  {k:5.0f} {ell:4d} {row[0]:15.3e} {row[1]:12.3e}"
                      f" {row[2]:12.3e}")
    print("\n  A cell is a FAIL only against its own measured floor above.")
    print("  A ratio that does NOT fall under refinement is bookkeeping.\n")


def main() -> int:
    """Print the report **and write it**, so `diagnostics/` is regenerated
    rather than hand-captured from a console redirect --- finding **T-87**."""
    import contextlib, io
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
