r"""The acoustic scale against *Annals II*'s own formula --- finding **T-51**.

**Written on 2026-10-16 to assert a defect, and rewritten the same day when
the defect was fixed** --- which is the discipline working, not a failure of
it. The original four tests pinned what the bundle then did; they survive below
as statements about **the `acoustic_start="z_max"` control**, because what they
measure is still true of it and is the cost the correction removes. What they
may no longer claim is that the bundle does it, and
`test_the_derived_start_reproduces_the_antecedents_peak_spacing` is the
positive assertion that replaces that claim.

**One of them did not fail when the defect was fixed, and that is worth
recording.** They measure the $r_s$ arithmetic --- what a start at $z=3000$
discards --- and that arithmetic is unchanged by a fix that alters where the
pipeline *begins integrating*. A test written to fail on repair must assert on
the repaired object, not on the quantity that motivated the repair.

The antecedent prints the check in \S*Some `Acoustic peak' Characteristics*:

    l_j ~= |r_theta / r_s| j pi,   k_{j+1} - k_j = k_A ~= pi / r_s

with $r_s$ *"the sound-horizon near decoupling"*, $\int_0^{\eta_*}c_s d\eta$.
Both sides are computable in this bundle without any external code, and nothing
compared them until 2026-10-16.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, LCDM_MODEL, PLANCK_MODEL, PLANCK_OMEGA_B_H2,
)
from functions.spectra.decoupling import RecombinationHistory  # noqa: E402

from functions.spectra.acoustic import (  # noqa: E402
    ACOUSTIC_START_EPSILON as START_EPSILON, sound_horizon_from_zero,
)
from diagnostic_d9_acoustic_scale import Z_MAX_AS_SHIPPED  # noqa: E402

#: The fraction of $r_s$ the shipped start **throws away**, per background,
#: measured 2026-10-16. Wider than the measurement because $\eta_*$ moves a
#: little with the recombination grid; narrow enough that halving the loss
#: fails here.
MISSING_AS_SHIPPED = {
    "CDM": (CDM_MODEL, 0.0224, 0.60, 0.69),
    "LCDM": (LCDM_MODEL, 0.0224, 0.60, 0.69),
    "PLANCK": (PLANCK_MODEL, PLANCK_OMEGA_B_H2, 0.46, 0.55),
}


def _scales(background, omega_b_h2):
    history = RecombinationHistory.build(
        background, omega_b_h2=omega_b_h2, n_eta=16_000)
    eta_star = float(history.eta[int(np.argmax(history.visibility))])
    eta, accumulated = sound_horizon_from_zero(
        background, eta_star, omega_b_h2=omega_b_h2)
    r_s_full = float(accumulated[-1])
    r_s_shipped = r_s_full - float(
        np.interp(float(history.eta[0]), eta, accumulated))
    return eta_star, r_s_full, r_s_shipped, float(background.eta_0) - eta_star


@pytest.mark.parametrize("name", sorted(MISSING_AS_SHIPPED))
def test_the_z_max_control_throws_away_what_T51_says_it_does(name):
    r"""What `acoustic_start="z_max"` costs, which is why it is only a control.

    This is the quantity finding **T-51** is about, and it is a property of the
    recombination grid's starting redshift rather than of the pipeline, so it
    is unchanged by the fix. It is kept because the control is kept: a branch
    nobody measures is a branch nobody can justify keeping.
    """
    background, omega_b_h2, lo, hi = MISSING_AS_SHIPPED[name]
    _, r_s_full, r_s_shipped, _ = _scales(background, omega_b_h2)
    missing = 1.0 - r_s_shipped / r_s_full
    assert lo <= missing <= hi, (
        f"{name}: the acoustic integration starts at z={Z_MAX_AS_SHIPPED:.0f} "
        f"and misses {missing:.3f} of the sound horizon, where T-51 records "
        f"{lo:.2f}-{hi:.2f}. If this is now SMALLER, the defect has been fixed "
        "and finding T-51, decision S37's record and this test must be "
        "rewritten together. If it is LARGER, something else has moved.")


@pytest.mark.parametrize("name", sorted(MISSING_AS_SHIPPED))
def test_the_peak_spacing_disagrees_with_the_antecedents_own_formula(name):
    r"""$\Delta\ell=\pi r_\theta/r_s$ is the paper's; ours is 2.0--2.8 times it."""
    background, omega_b_h2, *_ = MISSING_AS_SHIPPED[name]
    _, r_s_full, r_s_shipped, r_theta = _scales(background, omega_b_h2)
    paper = np.pi * r_theta / r_s_full
    ours = np.pi * r_theta / r_s_shipped
    assert 1.9 <= ours / paper <= 3.0, (
        f"{name}: the spacing this bundle integrates is {ours:.1f} against the "
        f"paper's {paper:.1f}, a ratio of {ours / paper:.2f}. T-51 records "
        "2.0-2.8. A ratio near 1 means the defect is fixed; update the record.")


def test_the_derived_start_reproduces_the_antecedents_peak_spacing():
    r"""**The acceptance.** $\Delta\ell=\pi r_\theta/r_s$, the paper's own formula.

    Measured on the transfer function rather than on $C_\ell$, deliberately:
    $\delta T+\Phi_A$ at $\eta_*$ oscillates as $\cos(k r_s)$ with period
    $2\pi/r_s$ in $k$, and reading the period there needs sixty ODE solves
    instead of a full spectrum. Einstein--de Sitter, because $\Omega_r=0$ makes
    *Annals II*'s Appendix G **exact** for it --- there is no radiation era to
    approximate, so a disagreement here could only be ours.

    Measured 2026-10-16: 191.7 against the formula's 192.7, a ratio of 0.995.
    The ``z_max`` control gives 568.7, a ratio of 2.95.
    """
    from functions.spectra.acoustic import (
        acoustic_start_eta, required_acoustic_points, solve_acoustic,
    )
    from functions.spectra.potentials import matter_domination_eta, potentials

    background, omega_b_h2 = CDM_MODEL, 0.0224
    eta_star, r_s_full, _, r_theta = _scales(background, omega_b_h2)
    eta_tab, r_s_tab = sound_horizon_from_zero(
        background, eta_star, omega_b_h2=omega_b_h2)
    reference = matter_domination_eta(background) or float(eta_tab[0])

    ks = np.linspace(40.0, 900.0, 60)
    values = []
    for k in ks:
        start = acoustic_start_eta(float(k), eta_tab, r_s_tab)
        grid = np.linspace(start, eta_star,
                           required_acoustic_points(float(k), eta_star - start))
        phi_a, phi_h = potentials(background, grid, constant_below=reference)
        solution = solve_acoustic(float(k), grid, background=background,
                                  phi_a=phi_a, phi_h=phi_h, omega_b_h2=omega_b_h2)
        values.append(float(solution.delta_T[-1] + phi_a[-1]))

    y = np.asarray(values)
    slope = np.diff(y)
    turning = ks[1:-1][np.sign(slope[:-1]) != np.sign(slope[1:])]
    assert turning.size > 2, "no oscillation found in the transfer function"
    measured = 0.5 * (2.0 * float(np.mean(np.diff(turning)))) * r_theta
    paper = np.pi * r_theta / r_s_full
    assert abs(measured / paper - 1.0) < 0.05, (
        f"the derived start gives a peak spacing of {measured:.1f} against the "
        f"antecedent's own {paper:.1f} --- a ratio of {measured / paper:.3f}, "
        "outside 5%. On Einstein-de Sitter the paper's Appendix G is exact, so "
        "this disagreement would be ours.")


def test_the_initial_condition_is_imposed_rather_than_adiabatic():
    r"""$\tau_1=0$ is the growing mode only while $k\,r_s(\eta_{\rm start})\ll1$.

    **Every mode in the acoustic band violates this**, up to twelve radians at
    $k=600$ --- the mode has already completed two oscillations by the time the
    integration asserts it has not started. This is the half of T-51 that a
    lower ``z_max`` alone does not fix, and it is why the first maximum sits at
    $\ell=161.8$ rather than at the $\ell\simeq414$ a pure truncation gives.
    """
    _, _, r_s_shipped, _ = _scales(PLANCK_MODEL, PLANCK_OMEGA_B_H2)
    violated = [k for k in (10.0, 30.0, 100.0, 300.0, 600.0)
                if k * r_s_shipped > START_EPSILON]
    assert len(violated) == 5, (
        f"T-51 records every reported mode starting with an imposed phase; "
        f"{len(violated)} of 5 do. If fewer now violate it, the start has been "
        "moved and the finding must move with it.")
    assert 600.0 * r_s_shipped > 2.0 * np.pi, (
        "at k=600 the mode had completed more than a full oscillation before "
        "the integration begins; T-51 states that and this pins it")


def test_the_sound_horizon_helper_integrates_from_the_big_bang():
    """**The bug's twin, and the reason 5b could not see it.**

    `functions.spectra.acoustic.sound_horizon` returns the integral from
    ``eta[0]``, not from 0, so the closed-form route (180) inherits the same
    truncation whenever it is handed a grid that does not start at the big
    bang. Two implementations, one wrong assumption, nothing to disagree about
    --- which is **T-3**'s lesson and exactly what **S4c** says a
    self-comparison cannot see.
    """
    from functions.spectra.acoustic import sound_horizon, baryon_photon_ratio

    eta = np.linspace(0.02, 0.07, 2000)
    r = baryon_photon_ratio(PLANCK_MODEL.a_of_eta(eta),
                            omega_b_h2=PLANCK_OMEGA_B_H2)
    assert sound_horizon(eta, r)[0] == 0.0, (
        "sound_horizon no longer starts its accumulation at zero. If it now "
        "integrates from the big bang regardless of the grid it is handed, "
        "T-51's second half is fixed and this test must be rewritten.")
