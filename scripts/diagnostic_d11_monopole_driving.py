#!/usr/bin/env python3
"""P1-T's addendum, settled by reading `d_delta` and then measuring it.

THE QUESTION P1-T LEFT TO THE CODE
----------------------------------
"If a B_0 is the streaming term rather than a source, then c5_monopole's
*restore B_0 to the l=0 matching row* restores the wrong object. ... That is
settled by reading `d_delta`."

WHAT `d_delta` IS, READ OFF acoustic.py AND THE PRODUCTION CALL
---------------------------------------------------------------
    d_delta = -phi_h_prime + k/3 * tau_1          [expansion_coupling=False,
                                                   which is production:
                                                   two_frame.py:384,393]
and  a B_0 = -(1/3) k tau_1   (B_0 = -(1/3) D^a tau_a, coefficients.py:20),
so   d_delta = -a B_0 - phi_h'.

So a B_0 sits on the RIGHT, ONCE, as a source. The printed l=0 form's LHS
(k/3) tau_1 is ABSENT. The solver resolves the double count by keeping the RHS
placement and dropping the LHS one.

THAT IS A READ, NOT A MEASUREMENT. The measurement below is the other half:
a B_0 is a source but NOT the only one -- phi_h' drives tau_0 too, and no
B carries it. So the l=0 matching RHS predicted by d_delta is

    -a B_0 - phi_h'      not      -a B_0

and the question is whether the missing piece matters. Sizes, max over the
eta grid, both frames' shared background quantities.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (                                   # noqa
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra.acoustic import (                                  # noqa
    acoustic_start_eta, required_acoustic_points, solve_acoustic)
from functions.spectra.potentials import potentials                       # noqa
from functions.spectra.two_frame import (                                 # noqa
    TIGHT_COUPLING_FACTOR, build_environment)
from scipy.interpolate import CubicSpline                                 # noqa

KS = (10.0, 60.0, 300.0)

print()
print("  d_delta = -phi_h' + (k/3) tau_1 ,  a B_0 = -(1/3) k tau_1")
print("  => d_delta = -a B_0 - phi_h'   -- a B_0 is a SOURCE, on the right, ONCE")
print()
print(f"  {'bg':<7} {'k':>5} {'max|-aB_0|':>12} {'max|-phi_h|':>12}"
      f" {'|phi_h|/|aB_0|':>15} {'max|d_delta|':>13}")
print("  " + "-" * 70)

for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                           ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
    # `line_of_sight_weight` is named because the release gate requires every
    # caller to name it (A-1, enforced after T-57), **not** because this
    # diagnostic depends on it: nothing below the environment build touches the
    # line-of-sight integral. 'printed' is the T-69 default, so the environment
    # here is the same one the register's other numbers were measured in.
    env = build_environment(400.0, omega_m=bg.omega_m, omega_lambda=bg.omega_lambda,
                            omega_r=bg.omega_r, omega_b_h2=obh2, hubble_h=h,
                            line_of_sight_weight="printed")
    for k in KS:
        t_k = env.transfer_at(k)
        couple = min(float(env.background.eta_0),
                     TIGHT_COUPLING_FACTOR * env.eta_star)
        start = acoustic_start_eta(float(k), env.eta_rs, env.r_s_table)
        me = np.linspace(start, couple,
                         required_acoustic_points(float(k), couple - start))
        ma, mh = potentials(env.background, me, constant_below=env.md_reference)
        ac = solve_acoustic(float(k), me, background=env.background,
                            phi_a=ma * t_k, phi_h=mh * t_k,
                            omega_b_h2=env.omega_b_h2, expansion_coupling=False)
        # exactly the two terms rhs() forms, on the solver's own grid
        php = CubicSpline(me, mh * t_k).derivative()(me)
        a_b0 = -(k / 3.0) * ac.tau_1          # a B_0
        src_b0 = -a_b0                        # the +(k/3) tau_1 term
        src_ph = -php                         # the -phi_h' term
        d_delta = src_b0 + src_ph
        mb, mp = np.max(np.abs(src_b0)), np.max(np.abs(src_ph))
        print(f"  {label:<7} {k:>5.0f} {mb:>12.4e} {mp:>12.4e}"
              f" {mp / mb:>15.4f} {np.max(np.abs(d_delta)):>13.4e}")
print()
print("  READ, not measured: a B_0 is on the right, once. c5_monopole restores")
print("  the right object. What it does NOT restore is -phi_h', which drives")
print("  tau_0 in d_delta and which no B carries.")
print()
