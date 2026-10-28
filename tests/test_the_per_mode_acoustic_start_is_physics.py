r"""The per-mode acoustic start is **load-bearing physics**, not an optimisation.

**Findings T-166 and T-167.**

`coefficient_sets` gives every mode its own acoustic grid, running from
`acoustic_start_eta(k)` to `eta_couple` --- **T-51/S40**, *"the start is
$k$'s"*. `solve_ivp` integrates **one** $t$-span, so the measured 12--20x
batched solve cannot be wired into the released path without putting every
mode on a common grid, and a common grid moves each mode's initial condition
to a different time.

**That looked like plumbing and is not.** The expectation written down before
the measurement was that starting *earlier* than horizon entry is harmless:
below `md_reference` the potential is held at its constant super-horizon value
and a mode outside its sound horizon has nothing to oscillate about yet. **The
measurement refuted it** --- on `PLANCK_MODEL` at $k_{\max}=1500$, a common
start moves $\tau_1$ at $\eta_{\rm couple}$ by up to $1.4\times10^{-2}$
against an integrator running at `rtol=1e-10`.

The reason is in (152)/(153) themselves: $\tau_1$ starts at zero and
accumulates $-k\!\int\!\Phi_A$, which **grows outside the sound horizon as
well as inside it**. A super-horizon mode is not frozen here; it is driven. So
the start time decides how much pre-horizon driving each mode carries, and
moving it is a change to the spectrum.

WHAT IS ASSERTED
----------------
1. **the negative** --- a common start does *not* reproduce the released
   answer, by three or more orders of magnitude. If this ever stops failing,
   the premise of `start_eta` has gone and the mask is dead weight;
2. **the repair** --- the same per-mode start, imposed on a common grid by
   holding each mode at its initial condition until its own start, reproduces
   the released per-mode solve at the integrator's tolerance;
3. **compared at identical times**, with nothing interpolated. The first
   version of this measurement reported $6\times10^{-2}$ by interpolating the
   common-grid solution onto the per-mode grid --- at $k=1500$ that grid
   carries 24 points per sound period and linear interpolation of a sinusoid
   errs by $\sim\tfrac12(2\pi/24)^2=3.4\times10^{-2}$, which is the number it
   reported. **M15**: a true number about the instrument, not the solution;
4. and that `start_eta=None` is **exactly** the old behaviour, so the released
   path cannot move until something passes the array.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    PLANCK_H, PLANCK_MODEL, PLANCK_OMEGA_B_H2)
from functions.spectra.acoustic import (  # noqa: E402
    acoustic_start_eta, required_acoustic_points, solve_acoustic,
    solve_acoustic_batch)
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.potentials import potentials  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    TIGHT_COUPLING_FACTOR, build_environment)

#: The integrator runs at `rtol=1e-10`. Agreement is required at 1e-6, which
#: is four decades of slack and still four decades tighter than the
#: $1.4\times10^{-2}$ the common start costs.
TOLERANCE = 1e-6

#: What the common start costs, measured. The negative control asserts the
#: gap is at least a hundred times `TOLERANCE`, not merely nonzero: a
#: comparison that failed by $10^{-5}$ would be a tolerance quarrel rather
#: than the physical statement this file is making.
COMMON_START_FLOOR = 1e-4

#: $k=1500$ is F9's band edge and the shortest acoustic period in the bundle;
#: $k=10$ has the **latest** start and so the longest interval a common grid
#: would wrongly integrate. Both extremes, and three in between.
PROBE = np.array([1.0, 10.0, 60.0, 600.0, 1500.0])
K_MAX = 1500.0


@pytest.fixture(scope="module")
def setup():
    env = build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2,
        transfer_gamma=shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H),
        hubble_h=PLANCK_H, f_2=F2_DEFAULT, line_of_sight_weight="printed")
    bg = env.background
    couple = min(float(bg.eta_0), TIGHT_COUPLING_FACTOR * float(env.eta_star))
    starts = np.array([acoustic_start_eta(float(k), env.eta_rs, env.r_s_table)
                       for k in PROBE])
    grid = np.linspace(
        float(starts.min()), couple,
        required_acoustic_points(K_MAX, couple - float(starts.min())))
    phi = potentials(bg, grid, constant_below=env.md_reference)
    return env, bg, couple, starts, grid, phi


def _own(env, bg, couple, k, start, t_eval=None):
    """The released per-mode solve, optionally reported at given times."""
    eta = (np.linspace(start, couple,
                       required_acoustic_points(float(k), couple - start))
           if t_eval is None else t_eval)
    a, h = potentials(bg, eta, constant_below=env.md_reference)
    return solve_acoustic(float(k), eta, background=bg, phi_a=a, phi_h=h,
                          omega_b_h2=env.omega_b_h2, expansion_coupling=False)


def test_a_common_start_does_not_reproduce_the_released_answer(setup):
    """**The negative. T-166, and the reason `start_eta` exists at all.**"""
    env, bg, couple, starts, grid, (a_c, h_c) = setup
    worst = 0.0
    for k, start in zip(PROBE, starts):
        if start <= float(starts.min()):
            continue                      # its own start IS the common one
        own = _own(env, bg, couple, k, start)
        common = solve_acoustic(float(k), grid, background=bg, phi_a=a_c,
                                phi_h=h_c, omega_b_h2=env.omega_b_h2,
                                expansion_coupling=False)
        for f in ("delta_T", "tau_1"):
            x = np.asarray(getattr(own, f), float)
            y = np.asarray(getattr(common, f), float)
            scale = max(float(np.max(np.abs(x))), 1e-300)
            worst = max(worst, abs(float(y[-1]) - float(x[-1])) / scale)
    assert worst > COMMON_START_FLOOR, (
        f"a common acoustic start reproduced the released per-mode answer to "
        f"{worst:.3e}. If that is real then T-51/S40's per-mode start is an "
        "efficiency device after all, `start_eta` is dead weight, and the "
        "batch can be wired on a plain common grid — but it was measured at "
        "1.4e-02 on 2026-10-28 and something has changed."
    )


def test_the_masked_start_reproduces_the_released_solve(setup):
    """**The repair. T-167.** Same equation, same start, same answer."""
    env, bg, couple, starts, grid, (a_c, h_c) = setup
    batch = solve_acoustic_batch(
        PROBE, grid, background=bg, phi_a=a_c, phi_h=h_c,
        omega_b_h2=env.omega_b_h2, expansion_coupling=False,
        start_eta=starts)

    worst = 0.0
    for i, (k, start) in enumerate(zip(PROBE, starts)):
        # **Identical times, nothing interpolated** — the common grid's own
        # abscissae from this mode's start onward.
        live = grid >= start
        t_eval = grid[live]
        if float(t_eval[0]) > start:
            t_eval = np.concatenate([[start], t_eval])
        exact = _own(env, bg, couple, k, start, t_eval=t_eval)
        off = len(t_eval) - int(live.sum())
        for f in ("delta_T", "tau_1"):
            x = np.asarray(getattr(exact, f), float)[off:]
            y = np.asarray(getattr(batch[i], f), float)[live]
            scale = max(float(np.max(np.abs(x))), 1e-300)
            worst = max(worst, float(np.max(np.abs(y - x))) / scale)
    assert worst < TOLERANCE, (
        f"the masked batch and the released per-mode solve disagree by "
        f"{worst:.3e} at identical times, above the {TOLERANCE:.0e} this file "
        "allows. They are the same initial-value problem — same equation, "
        "same initial condition, applied at the same time — so a "
        "disagreement above tolerance means the mask is not imposing the "
        "start it claims to."
    )


def test_no_start_array_is_exactly_the_old_behaviour(setup):
    """`start_eta=None` must not move, or every number in the bundle does."""
    env, bg, couple, starts, grid, (a_c, h_c) = setup
    batch = solve_acoustic_batch(
        PROBE, grid, background=bg, phi_a=a_c, phi_h=h_c,
        omega_b_h2=env.omega_b_h2, expansion_coupling=False)
    for i, k in enumerate(PROBE):
        serial = solve_acoustic(float(k), grid, background=bg, phi_a=a_c,
                                phi_h=h_c, omega_b_h2=env.omega_b_h2,
                                expansion_coupling=False)
        for f in ("delta_T", "tau_1"):
            x = np.asarray(getattr(serial, f), float)
            y = np.asarray(getattr(batch[i], f), float)
            scale = max(float(np.max(np.abs(x))), 1e-300)
            assert float(np.max(np.abs(y - x))) / scale < TOLERANCE


def test_a_wrong_length_start_array_is_refused(setup):
    """A start per mode, or none. Silently broadcasting would be a defect.

    `np.where` would happily broadcast a length-1 array across every mode and
    give all of them the same start — which is the common start this file
    exists to refute, arriving through the repair for it.
    """
    env, bg, couple, starts, grid, (a_c, h_c) = setup
    with pytest.raises(ValueError, match="one start per mode"):
        solve_acoustic_batch(
            PROBE, grid, background=bg, phi_a=a_c, phi_h=h_c,
            omega_b_h2=env.omega_b_h2, expansion_coupling=False,
            start_eta=starts[:2])
