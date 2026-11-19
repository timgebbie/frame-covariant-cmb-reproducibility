#!/usr/bin/env python3
r"""D19 --- the $\ell=0$ row correction, measured on the LIVE coefficients.

**The acceptance measurement for findings T-104 and T-105, taken before the
default moves and not after.** Five repairs have been attempted and withdrawn
(T-88--T-93); the one that looked best was a spurious $\times\kappa'$ of
320--682 scored on a lattice nobody had checked. This one is measured first.

WHAT IS BEING CHANGED
---------------------
`coefficients.MONOPOLE_ROW` switches (89)'s $\ell=0$ row, and
`coefficients.RANK_ONE_SOURCE` the rank-one source the coefficients are built
with. **Read with the table of 3 November** (`coefficients.MONOPOLE_ROW`'s
table), four configurations, each with the frame shift of $C_0$ it must give:

    row           source     C_0                          gamma
    printed       as built   -(5/2) a B_2                  5/2   alpha_2 on a monopole row
    corrected     as built   -(1/3) a B_2                  1/3   T-104: alpha_0
    corrected+b0  as built   -(1/3) a B_2 - a B_0           0    T-104 + T-105, refuted by T-107
    corrected     paper 1    -(1/3) a B_2 - a B_0           0    the released row since v1.4.0

`c5_monopole.py` gives the same three values symbolically: $5/2$ as printed,
$1/3$ with $\alpha_0$ only, and $0$ only with both. **$\gamma=0$ is the first
frame condition** of $W\{C_0K+C_1K'+C_2K''\}$. Under the antecedent's
matching it needs the $a\mathcal B_0$ that T-107 refutes restoring alone;
under Paper 1's source it comes with the rank-one sign, and that is the row
the frame-invariant line of sight is built from.

**Rewritten 2026-11-19.** This file was written on 21 October, when
`"corrected"` meant both corrections, and it asserted $\gamma=0$ for it.
Since 3 November `"corrected"` is $\alpha_0$ alone and both are
`"corrected+b0"`, so the old assertion failed on a live value of exactly
$1/3$, which is the table's. The instrument now measures the table.

THE FOUR THINGS MEASURED
------------------------
1. **gamma on the live coefficients**, each row against its value above.
   With $\Delta(a\mathcal B_2)=a\mathcal B_2$ in the CDM column and
   $a\mathcal B_2=-kv$,

       gamma_live  =  max |Delta C_0| / max |a_B2(CDM)|

2. **The size of the Newtonian rank-0 source.** $a\mathcal B_2\equiv0$ in
   that column, so $C_0$ there is $-a\mathcal B_0=\tfrac13k\tau_1$ where the
   row carries $a\mathcal B_0$ and zero where it does not. Reported against
   $C_1$.
3. **The rows that must not move.** At fixed source the row switch reaches
   $C_0$ alone: $C_1$ and $C_2$ must not move.
4. **$\kappa'$ in the row.** $a\mathcal B_0=-\tfrac13k\tau_1$ carries no
   scattering rate, so every corrected $C_0$ must grade clean under **S48**'s
   ledger.

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
VERSION = "v1.4.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra import coefficients as C  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

KS = (10.0, 60.0, 300.0)

#: gamma is a pure rational in exact arithmetic; on floating arrays the bar is
#: quadrature, not machine epsilon, because a B_2 and a B_0 are built by
#: different routes. T-85's floor is the precedent.
GAMMA_BAR = 1e-10


#: (row, rank-one source, gamma the 3 November table gives, label).
CONFIGURATIONS = (
    ("printed", "as built", 2.5, "printed, as built"),
    ("corrected", "as built", 1.0 / 3.0, "corrected, as built"),
    ("corrected+b0", "as built", 0.0, "corrected+b0, as built"),
    ("corrected", "paper 1", 0.0, "corrected, paper 1 (released)"),
)


def _sets(env, k: float, row: str, source: str = "as built"):
    was, C.MONOPOLE_ROW = C.MONOPOLE_ROW, row
    try:
        return coefficient_sets(float(k), env, source=source)
    finally:
        C.MONOPOLE_ROW = was


def _sup(a) -> float:
    return float(np.max(np.abs(np.asarray(a, dtype=float))))


def _gamma(n, c, den: float) -> float:
    d = (np.asarray(c.coefficients.c0, dtype=float)
         - np.asarray(n.coefficients.c0, dtype=float))
    return _sup(d) / den if den else float("nan")


def _report() -> None:
    print(__doc__.split("WHAT IS NOT MEASURED")[0])
    gammas = {cfg[3]: [] for cfg in CONFIGURATIONS}
    newtonian = {cfg[3]: [] for cfg in CONFIGURATIONS}
    moved = {"c1": [], "c2": []}
    ledger = []

    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        print(f"\n{'='*78}\n  {label}: gamma, and |C_0^N|/|C_1^N| beside it\n{'='*78}")
        heads = ("printed/built", "corrected/built", "+b0/built", "corrected/paper1")
        print(f"  {'k':>5}" + "".join(f" {h:>17}" for h in heads))
        print("  " + "-" * 76)
        for k in KS:
            sets = {cfg[3]: _sets(env, k, cfg[0], cfg[1]) for cfg in CONFIGURATIONS}
            _, c_p = sets["printed, as built"]
            den = _sup(c_p.a_b2 if hasattr(c_p, "a_b2") else c_p.coefficients.a_b2)
            row_g, row_n = [], []
            for cfg in CONFIGURATIONS:
                n, c = sets[cfg[3]]
                g = _gamma(n, c, den)
                c1n = _sup(n.coefficients.c1)
                ratio = _sup(n.coefficients.c0) / c1n if c1n else float("nan")
                gammas[cfg[3]].append(g)
                newtonian[cfg[3]].append(ratio)
                row_g.append(g)
                row_n.append(ratio)
            print(f"  {k:5.0f}" + "".join(f" {g:17.3e}" for g in row_g))
            print(f"  {'':5}" + "".join(f" {r:17.4f}" for r in row_n))
            # At fixed source the row reaches C_0 alone.
            n_p, c_p = sets["printed, as built"]
            for name in ("corrected, as built", "corrected+b0, as built"):
                n_x, c_x = sets[name]
                moved["c1"].append(max(
                    _sup(np.asarray(n_x.coefficients.c1) - np.asarray(n_p.coefficients.c1)),
                    _sup(np.asarray(c_x.coefficients.c1) - np.asarray(c_p.coefficients.c1))))
                moved["c2"].append(max(
                    _sup(np.asarray(n_x.coefficients.c2) - np.asarray(n_p.coefficients.c2)),
                    _sup(np.asarray(c_x.coefficients.c2) - np.asarray(c_p.coefficients.c2))))

        # S48's ledger on every corrected row: the C_0 built with kappa' zeroed.
        kp = np.asarray(env.kappa_prime, dtype=float)
        env0 = replace(env, kappa_prime=0.0 * kp,
                       kappa_second=0.0 * np.asarray(env.kappa_second, dtype=float))
        for row, source, _, name in CONFIGURATIONS[1:]:
            n_k, _ = _sets(env, KS[0], row, source)
            n_0, _ = _sets(env0, KS[0], row, source)
            kpart = _sup(np.asarray(n_k.coefficients.c0, dtype=float)
                         - np.asarray(n_0.coefficients.c0, dtype=float))
            ledger.append(kpart)
            print(f"  S48 ledger, {name}: kappa'-carrying part of C_0 = {kpart:.3e}"
                  f"  ({'CLEAN' if kpart == 0.0 else 'CARRIES kappa'})")

    print(f"\n{'='*78}\n  ACCEPTANCE\n{'='*78}")
    rows = []
    for row, source, want, name in CONFIGURATIONS:
        worst = max(abs(g - want) for g in gammas[name])
        rows.append((f"gamma = {want:.6g} for {name}", worst <= GAMMA_BAR, worst))
    rows.append(("C_1 does not move with the row", max(moved["c1"]) == 0.0,
                 max(moved["c1"])))
    rows.append(("C_2 does not move with the row", max(moved["c2"]) == 0.0,
                 max(moved["c2"])))
    rows.append(("every corrected C_0 is clean under S48", max(ledger) == 0.0,
                 max(ledger)))
    for i, (name, ok, worst) in enumerate(rows, 1):
        print(f"  {'PASS' if ok else 'FAIL':<6} A{i}  {name:46s} worst {worst:.1e}")
    for row, source, want, name in CONFIGURATIONS:
        lo, hi = min(newtonian[name]), max(newtonian[name])
        print(f"  Newtonian rank-0 source, {name:30s} |C_0|/|C_1| {lo:.4f} to {hi:.4f}")
    print("""
  READING THIS
  ------------
  A4 is the released row: Paper 1's source carries a B_0 in C_0 with the
  rank-one sign, and the first frame condition holds on the live arrays. A3 is
  the same zero reached under the antecedent's matching by restoring a B_0,
  which T-107 refutes on criterion 5b; it is kept so that the refuted variant
  stays regenerable. A2 is T-104's normalisation alone, and its 1/3 is the
  frame shift that a B_0 cancels. A1 is the control: alpha_2 on a monopole
  row, which an instrument that could not see would not see repaired either.

  The |C_0|/|C_1| lines are not acceptance conditions. They are the size of
  the Newtonian rank-0 source each row carries, zero where a B_0 is absent.
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
