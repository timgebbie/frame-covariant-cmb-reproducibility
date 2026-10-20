#!/usr/bin/env python3
r"""D16 --- the $\kappa'^2$ in (102)'s integrand, measured against its neighbours.

**Finding T-93's one surviving result, and it is in the RELEASED code.** This
is not a repair and it changes nothing: it is the column **M11b** demands --
each quantity's operational definition, its validity condition, and **its size
against its neighbours** -- supplied for the term P1-T named in their item-2
list and which T-93 located.

THE TERM
--------
(102) carries the whole bracket $\{C_0 - C_1' + C_2''\}$ under $\mathcal V$,
and from (107)

    -C_1' = (kappa' vhat_B)' + (a B_1)'/k
          = kappa'' vhat_B + kappa' vhat_B'  +  (Phi_A' - Phi_H') + (k/3) tau_1
            \__Thomson, two pieces_______/      \__ISW__________/   \__dT'___/

so the integrand carries

    V * kappa'  vhat_B'  =  W * kappa'^2    * vhat_B'
    V * kappa'' vhat_B   =  W * kappa' kappa'' * vhat_B

**Two powers of the scattering rate where the $W$-form carries one.** At
$\kappa'\simeq1.4\times10^4$ that is not a small distinction, and P1-T's
\S5.3 flags the same structure in $\dot{\mathcal V}=(\kappa''+\kappa'^2)e^{-\kappa}$
as a conditioning requirement: **form it from the weight's own derivative,
never assemble it from $\kappa'^2$ and $\kappa''$ separately.**

WHAT THIS MEASURES, AND WHAT IT DOES NOT
----------------------------------------
Measures: the six pieces of the released integrand at the visibility peak and
in integrated magnitude, each against the others.

Does **not** measure: whether the released spectrum is wrong because of it.
A term can be large and correct. **The size is the precondition for asking,
not the answer** --- which is the whole of M11, and T-93 is the entry that
records what happens when a 500x factor goes into a control unmeasured.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d16-kappa-squared"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

KS = (10.0, 60.0, 300.0)


def _report() -> None:
    print(__doc__.split("WHAT THIS MEASURES")[0])
    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        eta, V, W = env.eta, env.visibility, env.opacity
        kp = np.asarray(env.kappa_prime, dtype=float)
        kpp = np.asarray(env.kappa_second, dtype=float)
        i_star = int(np.argmax(V))
        print(f"\n{'='*78}\n  {label}   kappa'(eta_*) = {kp[i_star]:.4e},  "
              f"kappa''(eta_*) = {kpp[i_star]:.4e},  V(eta_*) = {V[i_star]:.4e}")
        print(f"  kappa'^2(eta_*) = {kp[i_star]**2:.4e}   "
              f"(kappa'^2 / |kappa''| = {kp[i_star]**2/abs(kpp[i_star]):.4g})")
        print(f"{'='*78}")

        for k in KS:
            n_, _ = coefficient_sets(float(k), env)
            tk = env.transfer_at(float(k))
            vhat = np.asarray(n_.v_b, dtype=float) / float(k)   # v_b is UN-reduced
            vhat_p = np.asarray(n_.v_b_prime, dtype=float) / float(k)
            tau1 = vhat * float(k)        # the velocity-normalised dipole
            isw = (env.phi_a_prime - env.phi_h_prime) * tk

            # the six pieces of the released integrand, all at V weight
            pieces = {
                "V C_0":                 V * np.asarray(n_.coefficients.c0, float),
                "V C_2''":               V * np.asarray(n_.c2_second, float),
                "V kappa'' vhat":        V * kpp * vhat,
                "V kappa' vhat'":        V * kp * vhat_p,
                "V (Phi_A'-Phi_H')":     V * isw,
                "V (k/3) tau_1":         V * (float(k) / 3.0) * tau1,
            }
            tot = sum(np.abs(p) for p in pieces.values())
            sc = float(np.max(tot))
            print(f"\n  k = {k:.0f}      {'at eta_*':>14} {'max over grid':>16}"
                  f" {'share of total':>16}")
            print("  " + "-" * 72)
            for name, arr in pieces.items():
                share = float(np.max(np.abs(arr))) / sc if sc else float("nan")
                print(f"  {name:<22} {arr[i_star]:14.4e} "
                      f"{float(np.max(np.abs(arr))):16.4e} {share:16.4f}")
            # the one the W-form would carry once instead of twice
            v_kp = float(np.max(np.abs(V * kp * vhat_p)))
            w_kp = float(np.max(np.abs(W * kp * vhat_p)))
            print(f"  {'':<22} {'':>14} {'V/W on that term:':>16} "
                  f"{v_kp / w_kp if w_kp else float('nan'):16.4e}")
    print("""
  READING THIS
  ------------
  `V kappa' vhat'` is W kappa'^2 vhat'. The last line of each block is the
  factor by which the PRINTED form exceeds the W-form on that one term, and it
  is kappa'(eta_*) by construction -- stated so the arithmetic is visible
  rather than asserted.

  A large share is NOT a defect on its own. (102) is the printed equation and
  this bundle reproduces it; A-2 records that the weight is a choice the
  caller states. What the column establishes is which terms a change of weight
  would move, BEFORE anyone changes one -- which is the column T-93 did not
  have when it mattered.
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
