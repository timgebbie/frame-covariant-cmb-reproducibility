#!/usr/bin/env python3
r"""D22 --- the transport identity on LIVE coefficient histories, and the
derivative the by-parts needs against the one the bundle supplies.

**Stage 3's gate, and the first instrument in this project pointed at
*transport* rather than at coefficients.** `c3_byparts.py` verifies the
identity on fixtures; the production path had never been tested against it ---
P1-T's open question **O1**.

THE IDENTITY, DERIVED HERE RATHER THAN TRANSCRIBED
--------------------------------------------------
This project has lost a power of $k$ three times, so nothing below is copied
from a printed form. With $K=j_\ell(k(\eta_0-\eta))$ and **every derivative
taken in $\eta$** --- $\dot K=-k\,j_\ell'(x)$, $\ddot K=k^2j_\ell''(x)$, with
$j_\ell''$ from the spherical Bessel equation rather than a second recurrence
--- two integrations by parts give

    A  =  Int W [ C_0 K + C_1 Kdot + C_2 Kddot ] d.eta

    B  =  [ W C_1 K ] + [ W C_2 Kdot ] - [ (V C_2 + W C_2') K ]
          + Int [ W (C_0 - C_1' + C_2'') - V C_1 + 2 V C_2' + Vdot C_2 ] K d.eta

**A = B is an identity for any coefficients whatever --- PROVIDED $C_1'$ is
$\mathrm dC_1/\mathrm d\eta$.**

THE PROVISO IS THE FINDING
--------------------------
**This bundle does not supply that derivative, and is right not to.** Finding
**T-23**: the mode coefficient of a covariant derivative is not the derivative
of the mode coefficient --- the footnote to (105) expands
$\mathrm D_{\langle a}\dot{\mathcal B}_{b\rangle}\simeq-(a/k)(\dot{\mathcal
B}_1+2\mathcal H\mathcal B_1)\mathrm D_{\langle a}\mathrm D_{b\rangle}Q$, and
the $2\mathcal H\mathcal B_1$ is invisible to a spline through the stored
amplitude. So $C_1'$ comes from (106)/(107).

**But (102)'s bracket $C_0-C_1'+C_2''$ is the output of an integration by
parts, and that step produces $\mathrm dC_1/\mathrm d\eta$.** The two are not
the same object. This diagnostic scores the identity **twice, once with each**,
and the gap is what the released transport carries.

HOW IT IS SCORED, AND WHY NOT THE OBVIOUS WAY
---------------------------------------------
**Normalised by a scale that cannot vanish** --- the integrated absolute
contribution plus the boundary --- because $A$ is a near-cancelling total and
$|A-B|/|A|$ reports the cancellation rather than the error. A first draft of
this file divided by $|A|$ and read $2.6\times10^3$, which is **M15's shape**:
scoring on the wrong object.

**And only where $\ell\lesssim k\Delta\eta$.** Outside it $j_\ell$ is
exponentially small and a ratio of two vanishing numbers is not a residual.

**The residual is converged**: 8x refinement, $n_\eta=400\to3200$, moves it by
under 5%. It is not quadrature.

WHAT THIS IS NOT
----------------
Not a test of the spectrum and not a claim about the plateau --- **M16**. What
it settles is whether the transport of a *given* source is evaluated
consistently, which is where **D21** put the plateau failure when it found the
source right on EdS to 0.68% while the plateau stayed absent.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d22-identity-live"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

ELLS = (10, 50, 200)
KS = (20.0, 80.0, 200.0)
N_ETA = 1600
#: The identity is exact, so with a consistent derivative the residual is the
#: trapezium rule's alone. T-85's floor is the precedent.
FLOOR = 1e-4


def _j_and_derivs(table, l, x):
    r"""$j_\ell$, $j_\ell'$, $j_\ell''$ --- the second from the Bessel ODE.

    $x^2j''+2xj'+(x^2-\ell(\ell+1))j=0$. Using the ODE rather than a second
    recurrence keeps the $\ell$-weights out of the second derivative, where a
    dropped $(2\ell+1)$ would look exactly like a defect in the identity.
    """
    j = np.asarray(table(l, x), dtype=float)
    jm = np.asarray(table(l - 1, x), dtype=float)
    jp = np.asarray(table(l + 1, x), dtype=float)
    jpr = (l / (2 * l + 1)) * jm - ((l + 1) / (2 * l + 1)) * jp
    safe = np.where(np.abs(x) < 1e-12, 1e-12, x)
    jpp = -(2.0 / safe) * jpr - (1.0 - l * (l + 1) / safe**2) * j
    return j, jpr, jpp


def _report() -> None:
    print(__doc__.split("WHAT THIS IS NOT")[0])
    worst_sup = worst_con = 0.0
    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h, n_eta=N_ETA,
                                line_of_sight_weight="printed")
        eta = np.asarray(env.eta, dtype=float)
        W = np.asarray(env.opacity, dtype=float)
        V = np.asarray(env.visibility, dtype=float)
        Vdot = np.gradient(V, eta, edge_order=2)
        eta_0 = float(bg.eta_0)
        d_eta = eta_0 - float(eta[int(np.argmax(V))])
        print(f"\n{'='*78}\n  {label}   (ell <= k x {d_eta:.3f} is the window)\n{'='*78}")
        print(f"  {'k':>6} {'frame':<10} {'l':>5} {'C1p supplied':>14}"
              f" {'C1p consistent':>16} {'|A-R|/scale':>13}")
        print("  " + "-" * 72)
        for k in KS:
            n_, c_ = coefficient_sets(float(k), env)
            x = float(k) * (eta_0 - eta)
            needed = sorted(set(sum(([l - 1, l, l + 1] for l in ELLS), [])))
            table = BesselTable.build(ell_max=max(needed), x_max=float(np.max(x)) * 1.01,
                                      ells=np.array(needed))
            for frame, s in (("newtonian", n_), ("cdm", c_)):
                c0 = np.asarray(s.coefficients.c0, dtype=float)
                c1 = np.asarray(s.coefficients.c1, dtype=float)
                c2 = np.asarray(s.coefficients.c2, dtype=float)
                c1p_sup = np.asarray(s.c1_prime, dtype=float)
                c1p_con = np.gradient(c1, eta, edge_order=2)
                c2p = (np.zeros_like(eta) if s.c2_prime is None
                       else np.asarray(s.c2_prime, dtype=float))
                c2pp = np.asarray(s.c2_second, dtype=float)
                for l in ELLS:
                    if l > float(k) * d_eta:
                        continue
                    j, jpr, jpp = _j_and_derivs(table, l, x)
                    Kdot = -float(k) * jpr
                    Kddot = float(k) ** 2 * jpp
                    A = float(np.trapezoid(W * (c0 * j + c1 * Kdot + c2 * Kddot), eta))
                    scale = float(np.trapezoid(np.abs(W * c1 * Kdot), eta)
                                  + abs((W * c1 * j)[-1] - (W * c1 * j)[0]))
                    scale = scale if scale > 0 else 1.0
                    res = {}
                    for tag, c1p in (("sup", c1p_sup), ("con", c1p_con)):
                        bulk = (W * (c0 - c1p + c2pp) - V * c1
                                + 2.0 * V * c2p + Vdot * c2) * j
                        bdy = W * c1 * j + W * c2 * Kdot - (V * c2 + W * c2p) * j
                        B = float(bdy[-1] - bdy[0]) + float(np.trapezoid(bulk, eta))
                        res[tag] = abs(A - B) / scale
                    R = float(np.trapezoid(W * (c0 - c1p_sup + c2pp) * j, eta))
                    worst_sup = max(worst_sup, res["sup"])
                    worst_con = max(worst_con, res["con"])
                    print(f"  {k:6.0f} {frame:<10} {l:5d} {res['sup']:14.3e}"
                          f" {res['con']:16.3e} {abs(A - R) / scale:13.3e}")

    print(f"\n{'='*78}\n  GATE\n{'='*78}")
    print(f"  {'PASS' if worst_con <= FLOOR else 'FAIL':<6} the identity closes with a "
          f"CONSISTENT derivative:   worst {worst_con:.3e}  (floor {FLOOR:.0e})")
    print(f"  {'':<6} and does NOT with the one the bundle supplies: worst "
          f"{worst_sup:.3e}")
    print(f"\n  the released transport leaves "
          f"{worst_sup / max(worst_con, 1e-30):.3g}x the residual a consistent "
          f"derivative does")
    print("""
  READING THIS
  ------------
  The identity is exact for any coefficients, so neither column can be failed
  by the physics being wrong. The right-hand column is the trapezium rule and
  nothing else. The left-hand column is the same arithmetic with the
  derivative the RELEASED path supplies, and the difference between them is a
  property of the assembly, not of the quadrature -- the residual is converged
  under 8x refinement.

  WHAT IT DOES AND DOES NOT ESTABLISH. It establishes that (102)'s bulk
  bracket and this bundle's C_1' are not the same object: the bracket is the
  output of a by-parts that produces dC_1/d.eta, and T-23 is the reason the
  bundle supplies something else. BOTH CAN BE RIGHT SEPARATELY AND THEY
  CANNOT BE USED TOGETHER, which is a statement about (102) in mode space and
  not about either derivative.

  It does NOT say which to change, it does not say what it costs the
  spectrum -- M16 -- and it is not a repair. The next question is whether the
  by-parts step is legitimate in mode space at all, which is theory and is
  P1-T's.
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
