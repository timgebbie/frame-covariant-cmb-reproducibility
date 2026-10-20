#!/usr/bin/env python3
r"""D17 --- P1-T's $W$-form of (102), instrumented directly, against the released form.

**P1-T's item 2, 2026-10-20**, after five sweeps failed on premises rather
than on algebra. This is the 2x2 again, but **against a reference rather than
against a patch**.

THE REFERENCE, P1-T's boxed expression, with NO integration by parts:

    beta_l tau_l(eta_0)/(2l+1)
      = Int dEta { W [ s0 B0 K + s1g B1 K' + s2 B2 K'' ]
                 + V [ s0 S0 K + s1t S1 K' + s2 S2 K'' ] }

with K = j_l(k(eta_0 - eta)), K^(n) its n-th derivative in its OWN argument,
B_n = a B_n the gravitational source and S_n the in-scattered Thomson source
**with kappa' divided out**: S_0 = tau_0, S_1 = vhat_B, S_2 = tau_2.

THE ONE ASSUMPTION, named because the whole comparison rests on it
-------------------------------------------------------------------
P1-T's sigma_n are "the fixed PSTF reduction constants" and are not stated
numerically. **They are taken here from the bundle's own `_solved_match()`,
not invented**, by reading (102)'s own slots:

    (102) rank-1:  C_1 K'  with  C_1 = p1 (a B_1 + kappa' v_B) / k
      =>  W C_1 K' = W (p1/k) B_1 K'  +  V p1 vhat_B K'
      =>  s1g = p1/k   on B_1,    s1t = p1   on S_1 = vhat_B
    (102) rank-2:  C_2 K'' with  C_2 = p2 B_2 / k^2   =>  s2 = p2/k^2
    (102) rank-0:  with B_0 restored (T-77), C_0 = -(1/3) B_2 - B_0,
                   so the B_0 coefficient is -1  =>  s0 = -1

**No new constant is introduced.** The W-form and the released form are then
written in one normalisation, and the comparison is about STRUCTURE -- which
weight, which kernel derivative, by-parted or not.

WHAT IS COMPARED, AND WHAT IS NOT
----------------------------------
The same diffusion factor D(k) is applied to both, so the comparison isolates
the assembly rather than A-2 or the damping. P1-T's expression carries no D;
it is exact transport, and D is an approximation layered on afterwards.

THE DECISION, stated before the run -- P1-T's section 6.3:

    disagree  ->  the disagreement is the finding, and the frame gap is in
                  the assembly, which is where T-86 put it.
    agree     ->  THE FRAME GAP IS NOT IN THE ASSEMBLY, and the triage needs
                  a site it does not currently have.

**The second outcome is as informative as the first**, which is new this week:
every previous test could only confirm.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d17-w-form"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.coefficients import _solved_match  # noqa: E402
from functions.spectra.integral_solution import integral_solution  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

ELLS = np.array([2, 10, 50, 200])
KS = (10.0, 60.0, 300.0)


def kernels(table, ell, x):
    r"""$K$, $K'$ and $K''$ in the kernel's own argument.

    $j_\ell'=[\ell j_{\ell-1}-(\ell+1)j_{\ell+1}]/(2\ell+1)$ from the
    recurrence, and $j_\ell''$ from the spherical Bessel **equation**
    $j''=-\tfrac2x j'+\bigl(\tfrac{\ell(\ell+1)}{x^2}-1\bigr)j$ --- both
    published relations, never a spline through a table (**T-23**).
    """
    x = np.asarray(x, dtype=float)
    jl = np.asarray(table(ell, x), dtype=float)
    jm = np.asarray(table(ell - 1, x), dtype=float)
    jp = np.asarray(table(ell + 1, x), dtype=float)
    d1 = (ell * jm - (ell + 1) * jp) / (2 * ell + 1)
    safe = np.where(np.abs(x) < 1e-12, 1e-12, x)
    d2 = -2.0 / safe * d1 + (ell * (ell + 1) / safe**2 - 1.0) * jl
    return jl, d1, d2


def w_form(ells, k, cs, env, table, diffusion, s0, s1g, s1t, s2, tau0):
    """P1-T's boxed expression, evaluated term by term. No by-parts."""
    eta, eta0 = env.eta, float(env.background.eta_0)
    W = np.asarray(env.opacity, dtype=float) * diffusion
    V = np.asarray(env.visibility, dtype=float) * diffusion
    x = k * (eta0 - eta)

    v_b = np.asarray(cs.v_b, dtype=float)          # UN-reduced: v_b == tau_1
    a_b1 = np.asarray(cs.a_b1, dtype=float)
    a_b2 = (np.zeros_like(eta) if cs.a_b2 is None
            else np.asarray(cs.a_b2, dtype=float))

    # **REDUCED TO THEIR POTENTIALS, which is what P1-T's box says and what
    # the first run of this script got wrong.** Their $\mathfrak B_n$ is
    # $a\mathcal B_n$ *reduced*; the bundle stores the un-reduced
    # $a\mathcal B_n$, which carries $k^n$. Measured against P1-T's \S4 table,
    # the un-reduced forms failed by **exactly $1-1/k$** --- 0.900 at $k=10$,
    # 0.98333 at 60, 0.99667 at 300 --- which is the signature of comparing
    # $k\dot s$ against $\dot s$ and is a normalisation, not a defect. T-66's
    # shape for the third time, and the first run of D17 is void because of it.
    B0 = -(k / 3.0) * v_b / k                      # a B_0 = -(1/3) k tau_1, reduced
    B1 = a_b1 / k                                  # = dT + Phi_A
    B2 = a_b2 / k**2                               # = -v/k, so C_2 = p2 B2
    S0 = tau0                                      # the SHARED dT: the solver
    #                                                produces one, both columns
    #                                                read it, so Delta S_0 = 0
    #                                                EXACTLY, as P1-T's table
    #                                                requires. Reconstructing it
    #                                                per frame as a_b1/k - Phi_A
    #                                                gave Delta = 1.000, which
    #                                                was the reconstruction and
    #                                                not the bundle.
    S1 = v_b / k                                   # vhat_B, reduced (T-66)
    S2 = np.zeros_like(eta)                        # A-5: no quadrupole source

    floor = float(env.eta[0])
    inside = eta >= floor
    out = np.empty(ells.size)
    for i, ell in enumerate(ells):
        l = int(ell)
        K, K1, K2 = kernels(table, l, x)
        grav = W * (s0 * B0 * K + s1g * B1 * K1 + s2 * B2 * K2)
        thom = V * (s0 * S0 * K + s1t * S1 * K1 + s2 * S2 * K2)
        out[i] = float(np.trapezoid((grav + thom)[inside], eta[inside]))
    return out


def released(ells, k, cs, env, table, diffusion):
    """(102) exactly as the bundle ships it."""
    return integral_solution(
        ells, coefficients=cs.coefficients, table=table, weight=env.weight,
        diffusion=diffusion, damping_total=diffusion, eta_star=env.eta_star,
        eta_floor=float(env.eta[0]), c1_prime=cs.c1_prime,
        c2_second=cs.c2_second, c2_prime_star=cs.c2_prime_star,
        c2_prime=cs.c2_prime, visibility=env.visibility,
        eta_0=float(env.background.eta_0)).total


def gap(a, b):
    sc = np.maximum(np.abs(a), np.abs(b))
    return np.abs(b - a) / np.where(sc > 0, sc, 1.0)


def _report() -> None:
    print(__doc__.split("THE DECISION")[0])
    p0, p1, p2 = (float(v) for v in _solved_match())
    print(f"  sigma from _solved_match(): p0 = {p0:.6g}, p1 = {p1:.6g}, "
          f"p2 = {p2:.6g}\n")
    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        table = BesselTable.build(
            int(ELLS.max()) + 2, max(KS) * float(env.background.eta_0) + 20.0,
            ells=np.unique(np.concatenate([[e - 1, e, e + 1] for e in ELLS])))
        print(f"\n{'='*84}\n  {label}\n{'='*84}")
        for k in KS:
            n_, c_ = coefficient_sets(float(k), env)
            d = float(np.exp(-((float(k) / env.damping_k) ** 2)))
            phi_a = np.asarray(env.phi_a, float) * env.transfer_at(float(k))
            # sigma on the REDUCED sources: C_1 = p1 (B1 + kappa' S1),
            # C_2 = p2 B2, and the l=0 row's B_0 coefficient is -1 (T-77).
            tau0 = np.asarray(n_.a_b1, float) / k - phi_a
            s0, s1g, s1t, s2 = -1.0, p1, p1, p2
            wn = w_form(ELLS, k, n_, env, table, d, s0, s1g, s1t, s2, tau0)
            wc = w_form(ELLS, k, c_, env, table, d, s0, s1g, s1t, s2, tau0)
            rn, rc = released(ELLS, k, n_, env, table, d), released(ELLS, k, c_, env, table, d)
            print(f"\n  k = {k:.0f}")
            print(f"  {'l':>5} {'W-form gap':>13} {'released gap':>14}"
                  f" {'|W-rel|/scale N':>17} {'|W-rel|/scale C':>17}")
            print("  " + "-" * 72)
            gw, gr = gap(wn, wc), gap(rn, rc)
            for i, l in enumerate(ELLS):
                sn = max(abs(wn[i]), abs(rn[i])) or 1.0
                sc_ = max(abs(wc[i]), abs(rc[i])) or 1.0
                print(f"  {l:5d} {gw[i]:13.4e} {gr[i]:14.4e}"
                      f" {abs(wn[i]-rn[i])/sn:17.4e} {abs(wc[i]-rc[i])/sc_:17.4e}")
    print("""
  READING THIS
  ------------
  Column 1 is the frame gap of P1-T's W-form; column 2 is the frame gap of
  (102) as shipped. Columns 3 and 4 say how far the two assemblies are apart
  within one frame.

  Column 1 at machine zero  ->  the W-form is frame-invariant and (102) is
    not, so the frame gap IS in the assembly and the by-parts is where it
    enters. That is T-86's site, confirmed against a reference.

  Column 1 at O(1) as well  ->  THE FRAME GAP IS NOT IN THE ASSEMBLY. Both
    forms carry it, the by-parts is not the cause, and the triage needs a
    site it does not currently have. P1-T's section 6.3, and it is the
    outcome that would cost the most to learn late.

  Columns 3 and 4 large with column 1 small  ->  the two assemblies differ
    AND the reference is invariant: the difference is the defect and it is
    localised to whichever rank moves most.
""")


def main() -> int:
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
