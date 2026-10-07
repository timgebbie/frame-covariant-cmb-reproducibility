"""The acoustic pair (152)/(153), its reduction to (154), and finding B-8.

Two of these are symbolic. A numerical agreement between a pair of ODEs and the
second-order equation derived from them can be made to look right by choosing a
tolerance; an algebraic identity cannot.
"""

from __future__ import annotations

import numpy as np
import pytest
import sympy as sp

from functions.background.flrw import CDM_MODEL
from functions.spectra.acoustic import (
    ADIABATIC_MONOPOLE,
    baryon_photon_ratio,
    sachs_wolfe_at_last_scattering,
    sachs_wolfe_at_last_scattering_printed,
    solve_acoustic,
    sound_horizon,
    sound_speed_squared,
)


# ---------------------------------------------------------------------------
# finding B-8
# ---------------------------------------------------------------------------


def test_b8_equation_181_sign_is_fixed_by_its_own_limit():
    """**Finding B-8**, as algebra.

    (181) is (180) after the adiabatic substitution. Their oscillating parts
    must agree --- they do, for either sign --- so the oscillating part cannot
    decide the constant term. (181)'s own stated limit can: the text takes
    $r_s^*\\to0$ and asserts the result is $\\tfrac13\\Phi_A$. Only one sign makes
    that an identity.
    """
    phi, r, cos_krs = sp.symbols("Phi_A R_star cos_krs", real=True)

    # (180) with dT(0) = -(2/3) Phi_A and Phi_A(eta_*) ~= Phi_A(0)
    printed_180 = (sp.Rational(-2, 3) * phi + (1 + r) * phi) * cos_krs - r * phi
    printed_181 = sp.Rational(1, 3) * phi * (1 + 3 * r) * cos_krs + r * phi
    corrected_181 = sp.Rational(1, 3) * phi * (1 + 3 * r) * cos_krs - r * phi

    # the oscillating parts agree either way: this is why the sign is not
    # detectable from the oscillation and the limit has to settle it
    assert sp.expand(printed_180 - printed_181).coeff(cos_krs) == 0
    assert sp.expand(printed_180 - corrected_181).coeff(cos_krs) == 0

    # and the corrected form IS (180), identically
    assert sp.simplify(printed_180 - corrected_181) == 0
    assert sp.simplify(printed_180 - printed_181) == sp.simplify(-2 * phi * r)

    # the stated limit r_s* -> 0
    assert sp.simplify(corrected_181.subs(cos_krs, 1) - phi / 3) == 0
    assert sp.simplify(printed_181.subs(cos_krs, 1) - phi / 3) != 0


def test_b8_costs_a_factor_of_twenty_in_cl_if_taken_literally():
    """The size of B-8, stated as a number rather than as 'large'."""
    phi_a0, r_star = 1.0, 0.6
    corrected = sachs_wolfe_at_last_scattering(phi_a0, r_star, 0.0)
    printed = sachs_wolfe_at_last_scattering_printed(phi_a0, r_star, 0.0)

    assert corrected == pytest.approx(phi_a0 / 3.0)
    assert printed == pytest.approx(phi_a0 / 3.0 * (1.0 + 6.0 * r_star))
    assert (printed / corrected) ** 2 == pytest.approx(21.2, rel=0.02)


# ---------------------------------------------------------------------------
# (152) + (153) -> (154)
# ---------------------------------------------------------------------------


def test_the_pair_reduces_to_the_printed_oscillator_exactly():
    """(154) is (152) and (153) with the expansion-coupled terms dropped.

    Done symbolically, so it states *what* was dropped rather than that two
    numbers happened to be close: the residual is exactly
    $-(aH\\Phi_A)' - \\frac{R'}{1+R}aH\\Phi_A$, which is the paper's own "small
    scale approximation" and nothing else.
    """
    eta = sp.Symbol("eta", real=True)
    k = sp.Symbol("k", positive=True)
    R = sp.Function("R")(eta)
    dT = sp.Function("deltaT")(eta)
    tau1 = sp.Function("tau_1")(eta)
    PhiA = sp.Function("Phi_A")(eta)
    PhiH = sp.Function("Phi_H")(eta)
    aH = sp.Function("aH")(eta)

    # (152) and (153) in conformal time
    tau1_prime = -sp.diff(R, eta) / (1 + R) * tau1 - k / (1 + R) * dT - k * PhiA
    dT_prime = -aH * PhiA - sp.diff(PhiH, eta) + k / 3 * tau1

    # differentiate (153) and substitute (152), eliminating tau_1 via (153)
    dT_second = sp.diff(dT_prime, eta).subs(sp.Derivative(tau1, eta), tau1_prime)
    tau1_from_153 = sp.solve(sp.Eq(dT_prime, sp.Symbol("dTp")), tau1)[0]
    dT_second = dT_second.subs(tau1, tau1_from_153).subs(sp.Symbol("dTp"), sp.Derivative(dT, eta))

    c_s2 = 1 / (3 * (1 + R))
    lhs = dT_second + sp.diff(R, eta) / (1 + R) * sp.Derivative(dT, eta) + k**2 * c_s2 * dT
    printed_rhs = (
        -sp.diff(PhiH, eta, 2) - sp.diff(R, eta) / (1 + R) * sp.diff(PhiH, eta) - k**2 / 3 * PhiA
    )

    residual = sp.simplify(sp.expand(lhs - printed_rhs))
    expected_dropped = sp.simplify(
        -sp.diff(aH * PhiA, eta) - sp.diff(R, eta) / (1 + R) * aH * PhiA
    )
    assert sp.simplify(residual - expected_dropped) == 0


# ---------------------------------------------------------------------------
# the background pieces
# ---------------------------------------------------------------------------


def test_sound_speed_limits():
    assert sound_speed_squared(0.0) == pytest.approx(1.0 / 3.0)  # radiation
    assert sound_speed_squared(1e6) < 1e-6  # matter domination: c_s -> 0


def test_baryon_photon_ratio_scales_as_a():
    a = np.array([1e-4, 1e-3, 1e-2])
    r = baryon_photon_ratio(a)
    assert np.allclose(r / a, r[0] / a[0])
    assert 0.3 < baryon_photon_ratio(1.0 / 1101.0) < 1.0  # R_* is order a half


def test_the_sound_horizon_grows_and_is_bounded_by_the_light_horizon():
    eta = np.linspace(0.0, 0.1, 500)
    r = baryon_photon_ratio(CDM_MODEL.a_of_eta(eta))
    r_s = sound_horizon(eta, r)
    assert np.all(np.diff(r_s) > 0.0)
    assert np.all(r_s <= eta / np.sqrt(3.0) + 1e-12)  # c_s <= 1/sqrt(3)


# ---------------------------------------------------------------------------
# the integration
# ---------------------------------------------------------------------------


def _constant_potential_run(k_com: float, *, expansion_coupling: bool):
    eta = np.linspace(1e-4, 0.08, 4000)
    phi_a = np.full_like(eta, 0.1)
    phi_h = np.full_like(eta, -0.1)
    return eta, solve_acoustic(
        k_com, eta, background=CDM_MODEL, phi_a=phi_a, phi_h=phi_h,
        expansion_coupling=expansion_coupling,
    )


def test_the_oscillation_phase_is_the_sound_horizon():
    """Successive peaks are $2\\pi$ apart **in $k r_s$**, not in $\\eta$.

    That is the defining property of an acoustic oscillation and the reason
    $r_s^*$ sets the peak spacing in $\\ell$. Measured as peak spacing rather
    than as zero crossings, because the oscillation centre drifts with $R$
    through the window: from (180) it sits at $-(1+R)\\Phi_A$, and at these
    parameters the amplitude $(\\tfrac13+R)\\Phi_A$ is smaller than that offset,
    so the solution never crosses zero at all. A crossing test would have to
    assume the centre, which is assuming part of the answer.

    The residual few percent is the slow variation of $R$ across the window ---
    (180) is the constant-$R$ solution and $R$ roughly doubles here.
    """
    from scipy.signal import find_peaks

    k_com = 500.0
    eta, solution = _constant_potential_run(k_com, expansion_coupling=False)
    r = baryon_photon_ratio(CDM_MODEL.a_of_eta(eta))
    r_s = sound_horizon(eta, r)

    peaks, _ = find_peaks(solution.delta_T)
    assert peaks.size >= 3

    spacing = np.diff(k_com * r_s[peaks])
    assert np.allclose(spacing, 2.0 * np.pi, rtol=0.05)


def test_the_integration_converges_to_the_closed_form_180_as_r_is_held_constant():
    """(180) is the **constant-$R$** solution, and this is the check that the
    integration reproduces it in the limit where it applies.

    Over a window where $R$ changes by a factor of $10^5$ the two disagree by
    38%, which is not a defect in either: (180) assumes a constant $R$ and $R$
    is not constant. Narrowing the window so that $R$ varies less must drive the
    disagreement down, and it does, monotonically. **That is the justification
    for integrating (152) and (153) rather than evaluating (180)** --- the closed
    form is used only at last scattering, where $R_*$ is a single number.

    A test that merely compared the two at one window would have had to pick a
    tolerance. This one checks a trend, which has no free parameter.
    """
    phi_a = 0.1

    def disagreement(lo: float, hi: float, k_com: float) -> tuple[float, float]:
        eta = np.linspace(lo, hi, 3000)
        r = baryon_photon_ratio(CDM_MODEL.a_of_eta(eta))
        r_s = sound_horizon(eta, r)
        start_value = (ADIABATIC_MONOPOLE + (1.0 + r[0])) * phi_a - r[0] * phi_a - phi_a
        solution = solve_acoustic(
            k_com, eta, background=CDM_MODEL,
            phi_a=np.full_like(eta, phi_a), phi_h=np.full_like(eta, -phi_a),
            expansion_coupling=False, initial=(start_value, 0.0),
        )
        closed = (
            (ADIABATIC_MONOPOLE + (1.0 + r)) * phi_a * np.cos(k_com * r_s)
            - r * phi_a - phi_a
        )
        spread = float(r[-1] / r[0])
        error = float(np.max(np.abs(solution.delta_T - closed)) / np.max(np.abs(closed)))
        return spread, error

    windows = [(0.040, 0.080, 1000.0), (0.060, 0.080, 2000.0), (0.070, 0.080, 4000.0)]
    results = [disagreement(*w) for w in windows]

    spreads = [s for s, _ in results]
    errors = [e for _, e in results]

    assert spreads == sorted(spreads, reverse=True)   # R varies less each time
    assert errors == sorted(errors, reverse=True)     # and the disagreement falls
    assert errors[-1] < 0.12                          # to the sub-WKB level


def test_dropping_the_expansion_coupling_is_a_small_scale_approximation():
    """It must matter less as k grows --- that is what makes it 'small scale'."""
    ratios = []
    for k_com in (40.0, 400.0):
        eta, full = _constant_potential_run(k_com, expansion_coupling=True)
        _, reduced = _constant_potential_run(k_com, expansion_coupling=False)
        scale = np.max(np.abs(full.delta_T))
        ratios.append(np.max(np.abs(full.delta_T - reduced.delta_T)) / scale)
    assert ratios[1] < ratios[0]


def test_the_adiabatic_initial_condition_is_the_one_the_text_uses():
    eta, solution = _constant_potential_run(200.0, expansion_coupling=False)
    assert solution.delta_T[0] == pytest.approx(ADIABATIC_MONOPOLE * 0.1, rel=1e-9)
    assert solution.tau_1[0] == pytest.approx(0.0, abs=1e-12)


def test_at_returns_both_sources_the_integral_solution_needs():
    eta, solution = _constant_potential_run(200.0, expansion_coupling=False)
    delta_t, tau_1 = solution.at(0.05)
    assert np.isfinite(delta_t) and np.isfinite(tau_1)
