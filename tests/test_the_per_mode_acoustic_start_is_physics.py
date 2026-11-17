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
    acoustic_start_eta, required_acoustic_points, solve_acoustic)
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




def test_t192_the_start_rule_breaks_the_sachs_wolfe_source_on_planck(setup):
    r"""**T-192, and it stays pinned on the start that carries it.**

    A mode that reaches $k\,r_s=\varepsilon$ before $\eta_*$ starts there, on
    the matter-era condition $\delta T=-\tfrac23\Phi_A$. On `PLANCK_MODEL` the
    potential has already decayed by then (A-3), while a mode that never
    reaches it starts at the table's first point and carries the decay through
    continuity. The Sachs--Wolfe source at last scattering therefore jumps
    where the rule changes branch, near $k=2.75$.

    **Since step 1 of the radiation era the covariant figures do not use this
    start**: every mode starts at one $\eta_i$ deep in the radiation era, and
    `test_one_start_makes_the_sachs_wolfe_source_smooth_across_t192s_band`
    holds the repair. The derived start remains the antecedent's, and this test
    holds what it does.
    """
    from functions.spectra.two_frame import (
        covariant_coefficient_sets, line_of_sight_inputs)

    env = setup[0]
    eta, v = np.asarray(env.eta), np.asarray(env.visibility)

    def source(k: float) -> float:
        s, _ = line_of_sight_inputs(k, covariant_coefficient_sets(k, env)[0], env)
        return (float(np.trapezoid(v * s.c1_grav, eta) / np.trapezoid(v, eta))
                / env.transfer_at(k))

    smooth = abs(source(2.7) / source(2.6) - 1.0)
    jump = source(2.8) / source(2.7)
    assert smooth < 1e-2, f"the source is not smooth below the boundary: {smooth:.2e}"
    assert jump > 1.3, (
        f"T-192's jump has gone from the derived start ({jump:.3f}): the "
        "antecedent's start rule or its initial condition changed.")


# ---------------------------------------------------------------------------
# Step 1 of the radiation era: one start for every mode (sec:a3-construction)
# ---------------------------------------------------------------------------


def test_the_one_start_is_deep_in_the_radiation_era_and_outside_every_horizon():
    r"""$a_i\le10^{-3}a_{\rm eq}$ and $k_{\max}\eta_i\le10^{-2}$, read from the
    background's own $\eta(a)$; where $\Omega_r=0$ the horizon condition alone."""
    from functions.background.flrw import CDM_MODEL
    from functions.spectra.acoustic import (
        RADIATION_ERA_START_A_FRACTION, RADIATION_ERA_START_K_ETA, common_start_eta)

    eta_i = common_start_eta(PLANCK_MODEL, K_MAX)
    a_eq = PLANCK_MODEL.omega_r / PLANCK_MODEL.omega_m
    assert float(PLANCK_MODEL.a_of_eta(eta_i)) <= RADIATION_ERA_START_A_FRACTION * a_eq * (1 + 1e-6)
    assert K_MAX * eta_i <= RADIATION_ERA_START_K_ETA * (1 + 1e-12)
    assert common_start_eta(CDM_MODEL, K_MAX) == pytest.approx(RADIATION_ERA_START_K_ETA / K_MAX)


def test_the_growing_mode_starts_on_its_own_trajectory():
    r"""eq:radiation-ic. With $R\to0$, (152) gives $\tau_1'=-k(\delta T+\Phi_A)$,
    which is $-\tfrac12k\Phi$ in the radiation era and $-\tfrac13k\Phi$ in the
    matter era, so the initial $\tau_1$ is that line at $\eta_i$."""
    from functions.spectra.acoustic import adiabatic_growing_mode

    d_t, tau = adiabatic_growing_mode(3.0, 1e-5, 2.0, radiation_era=True)
    assert d_t == pytest.approx(-1.0) and tau == pytest.approx(-(3.0 * 1e-5 / 2.0) * 2.0)
    assert tau == pytest.approx(-3.0 * 1e-5 * (d_t + 2.0))
    d_t, tau = adiabatic_growing_mode(3.0, 1e-5, 2.0, radiation_era=False)
    assert d_t == pytest.approx(-4.0 / 3.0)
    assert tau == pytest.approx(-3.0 * 1e-5 * (d_t + 2.0))


def test_one_start_makes_the_sachs_wolfe_source_smooth_across_t192s_band():
    r"""**T-192, repaired by step 1 of the radiation era's construction.**

    Every mode starts at one $\eta_i$ deep in the radiation era on the
    adiabatic growing mode, so no mode starts after its potential has begun to
    decay. On the released potential the Sachs--Wolfe source at last
    scattering is then smooth across $2.7<k<5.4$, where the derived start
    jumps by 60\%, and as $k\to0$ it is $2\Phi_A-\tfrac32\Phi_A(\eta_i)$ read
    under the visibility: the start's $-\tfrac12\Phi$, with the potential's
    fall carried into $\delta T$ by continuity.
    """
    from functions.spectra.two_frame import (
        covariant_coefficient_sets, line_of_sight_inputs)

    env = build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2,
        transfer_gamma=shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H),
        hubble_h=PLANCK_H, f_2=F2_DEFAULT, line_of_sight_weight="printed",
        acoustic_start="radiation era")
    eta, v = np.asarray(env.eta), np.asarray(env.visibility)

    def source(k: float) -> float:
        s, _ = line_of_sight_inputs(k, covariant_coefficient_sets(k, env)[0], env)
        return (float(np.trapezoid(v * s.c1_grav, eta) / np.trapezoid(v, eta))
                / env.transfer_at(k))

    ks = [2.6, 2.7, 2.8, 3.5, 4.5, 5.5]
    values = np.array([source(k) for k in ks])
    steps = np.abs(values[1:] / values[:-1] - 1.0)
    assert np.all(np.diff(values) < 0.0), f"not monotone across the band: {values}"
    assert steps[:2].max() < 2e-3, f"a step at k = 2.6-2.8: {steps[:2]}"
    assert steps.max() < 2e-2, f"a step across the band: {steps}"

    # Outside the horizon, continuity carries the potential's fall into dT one
    # for one, so dT + Phi_A = 2 Phi_A - (3/2) Phi_A(eta_i), read under the
    # visibility as the source is.
    early = float(potentials(env.background, np.array([env.eta_i, env.eta_i * 2.0]),
                             constant_below=env.md_reference)[0][0])
    mean = float(np.trapezoid(v * np.asarray(env.phi_a), eta) / np.trapezoid(v, eta))
    assert source(0.05) == pytest.approx((2.0 * mean - 1.5 * early) / early, abs=2e-3)

