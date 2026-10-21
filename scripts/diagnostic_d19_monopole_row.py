#!/usr/bin/env python3
r"""D19 --- the $\ell=0$ row correction, measured on the LIVE coefficients.

**The acceptance measurement for findings T-104 and T-105, taken before the
default moves and not after.** Five repairs have been attempted and withdrawn
(T-88--T-93); the one that looked best was a spurious $\times\kappa'$ of
320--682 scored on a lattice nobody had checked. This one is measured first.

WHAT IS BEING CHANGED
---------------------
`coefficients.MONOPOLE_ROW` switches (89)'s $\ell=0$ row between:

    "printed"     C_0 = -(5/2) a B_2                   <- released
    "corrected"   C_0 = -(1/3) a B_2 - a B_0           <- T-104 + T-105

Two corrections, **one control**, because neither alone is a correction:
`c5_monopole.py` gives $\gamma=-5/2$ as printed, $+1/3$ with $\alpha_0$ only,
and $0$ only with both. Splitting them would score a still-wrong repair as an
improvement. **M11a.**

THE FOUR THINGS MEASURED
------------------------
1. **gamma on the live coefficients.** `c5_monopole.py` establishes
   $\gamma=0$ symbolically on its own fixtures; P1-T's acceptance condition is
   that the live arrays agree. With $\Delta(a\mathcal B_2)=a\mathcal B_2$ in
   the CDM column and $a\mathcal B_2=-kv$,

       gamma_live  =  Delta C_0 / a_B2(CDM)

   which is $p_0=-5/2$ exactly when the row is printed, and must be $0$ when
   it is corrected. **This is the condition that can fail early and cheaply.**
2. **The size of the new Newtonian rank-0 source.** $C_0\equiv0$ in that
   column today, because $a\mathcal B_2\equiv0$ there. $a\mathcal B_0=
   -\tfrac13k\tau_1$ is **not** zero there, so the correction gives the
   Newtonian column a monopole source it has never carried --- and the
   monopole is the Sachs--Wolfe plateau. Reported against $C_1$, the
   coefficient that currently dominates.
3. **The two rows that must not move.** $C_1$ and $C_2$ are untouched by this
   control. If either moves, the change has reached further than its
   derivation and the result is void.
4. **$\kappa'$ in the new row.** $a\mathcal B_0$ is $-\tfrac13k\tau_1$ and
   carries no scattering rate, so the corrected $C_0$ must still grade clean
   under **S48**'s ledger. Checked with D18's affine split rather than
   asserted.

WHAT IS NOT MEASURED HERE
-------------------------
The spectrum. A correct $C_0$ is a precondition for asking what the spectrum
does, not an answer about it --- **M11** --- and the full $C_\ell$ is a
45-minute run that belongs after this passes, not beside it.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d19-monopole-row"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra import coefficients as C  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

KS = (10.0, 60.0, 300.0)

#: gamma is a pure rational in exact arithmetic; on floating arrays the bar is
#: quadrature, not machine epsilon, because a B_2 and a B_0 are built by
#: different routes. T-85's floor is the precedent.
GAMMA_BAR = 1e-10


def _sets(env, k: float, row: str):
    was, C.MONOPOLE_ROW = C.MONOPOLE_ROW, row
    try:
        return coefficient_sets(float(k), env)
    finally:
        C.MONOPOLE_ROW = was


def _sup(a) -> float:
    return float(np.max(np.abs(np.asarray(a, dtype=float))))


def _report() -> None:
    print(__doc__.split("WHAT IS NOT MEASURED")[0])
    verdict = {"gamma_printed": [], "gamma_corrected": [],
               "c1_moved": [], "c2_moved": [], "c0_vs_c1": []}

    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        print(f"\n{'='*78}\n  {label}\n{'='*78}")
        print(f"  {'k':>5} {'gamma printed':>14} {'gamma corrected':>16}"
              f" {'|C_0^N|/|C_1^N|':>16} {'C_1 moved':>10} {'C_2 moved':>10}")
        print("  " + "-" * 76)
        for k in KS:
            n_p, c_p = _sets(env, k, "printed")
            n_c, c_c = _sets(env, k, "corrected")

            ab2 = np.asarray(c_p.coefficients.a_b2 if hasattr(c_p.coefficients, "a_b2")
                             else c_p.a_b2, dtype=float)
            den = _sup(ab2)

            def gamma(nn, cc) -> float:
                d = (np.asarray(cc.coefficients.c0, dtype=float)
                     - np.asarray(nn.coefficients.c0, dtype=float))
                return _sup(d) / den if den else float("nan")

            g_p = gamma(n_p, c_p)      # magnitude; sign is p_0's and is -5/2
            g_c = gamma(n_c, c_c)

            c0n = _sup(n_c.coefficients.c0)
            c1n = _sup(n_c.coefficients.c1)
            ratio = c0n / c1n if c1n else float("nan")

            c1_mv = _sup(np.asarray(n_c.coefficients.c1, dtype=float)
                         - np.asarray(n_p.coefficients.c1, dtype=float))
            c2_mv = _sup(np.asarray(c_c.coefficients.c2, dtype=float)
                         - np.asarray(c_p.coefficients.c2, dtype=float))

            print(f"  {k:5.0f} {g_p:14.6f} {g_c:16.3e} {ratio:16.4f}"
                  f" {c1_mv:10.1e} {c2_mv:10.1e}")
            verdict["gamma_printed"].append(g_p)
            verdict["gamma_corrected"].append(g_c)
            verdict["c1_moved"].append(c1_mv)
            verdict["c2_moved"].append(c2_mv)
            verdict["c0_vs_c1"].append(ratio)

        # the ledger, on the new row
        n_c, _ = _sets(env, KS[0], "corrected")
        kp = np.asarray(env.kappa_prime, dtype=float)
        env0 = replace(env, kappa_prime=0.0 * kp,
                       kappa_second=0.0 * np.asarray(env.kappa_second, dtype=float))
        was, C.MONOPOLE_ROW = C.MONOPOLE_ROW, "corrected"
        try:
            n_0, _ = coefficient_sets(float(KS[0]), env0)
        finally:
            C.MONOPOLE_ROW = was
        kpart = _sup(np.asarray(n_c.coefficients.c0, dtype=float)
                     - np.asarray(n_0.coefficients.c0, dtype=float))
        print(f"\n  S48 ledger on the corrected C_0: kappa'-carrying part = "
              f"{kpart:.3e}  ({'CLEAN' if kpart == 0.0 else 'CARRIES kappa'})")

    print(f"\n{'='*78}\n  ACCEPTANCE\n{'='*78}")
    gp = max(verdict["gamma_printed"]); gc = max(verdict["gamma_corrected"])
    c1 = max(verdict["c1_moved"]); c2 = max(verdict["c2_moved"])
    rows = [
        ("A1  gamma is 5/2 with the row as printed", abs(gp - 2.5) < 1e-9),
        ("A2  gamma is ZERO with the row corrected", gc <= GAMMA_BAR),
        ("A3  C_1 does not move", c1 == 0.0),
        ("A4  C_2 does not move", c2 == 0.0),
    ]
    for name, ok in rows:
        print(f"  {'PASS' if ok else 'FAIL':<6} {name}")
    print(f"\n  worst gamma printed   {gp:.6f}   (exactly 5/2 = 2.5)")
    print(f"  worst gamma corrected {gc:.3e}   (bar {GAMMA_BAR:.0e})")
    print(f"  new Newtonian rank-0 source, |C_0|/|C_1|: "
          f"{min(verdict['c0_vs_c1']):.4f} to {max(verdict['c0_vs_c1']):.4f}")
    print("""
  READING THIS
  ------------
  A2 is the condition P1-T stated in advance and it is the one that can fail
  early and cheaply: gamma = 0 on the LIVE coefficients, not only on
  c5_monopole's own fixtures. A1 is the control --- it says the instrument is
  pointed at the right quantity, because a measurement that could not see the
  defect could not see the repair either.

  The |C_0|/|C_1| column is NOT an acceptance condition. It is the size of a
  source the Newtonian column has never carried, reported so that whatever the
  spectrum does next is read against a number fixed beforehand. The monopole
  is the Sachs-Wolfe plateau, and the plateau is what F9 gets wrong at low
  ell -- but a source being the right size is not the same as the spectrum
  being right, which is M11 and is why the spectrum run comes after this.
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
