"""Annals II (176)-(179): the sources and the integral solution.

The test that earns its place here is the last one. (176)'s left-hand side is
$\\beta_\\ell\\tau_\\ell/(2\\ell+1)=\\alpha_\\ell^{-1}\\tau_\\ell$, which is exactly the
normalisation in which Appendix F's free-streaming solution is the bare spherical
Bessel function. So the integral solution and the hierarchy are two routes to one
object, and they are made to check each other across the two halves of the code.
"""

from __future__ import annotations

from fractions import Fraction

import numpy as np
import pytest
from scipy.interpolate import CubicSpline

from functions.background.flrw import CDM_MODEL
from functions.harmonics.free_streaming import analytic_projection
from functions.harmonics.weights import alpha, beta
from functions.spectra.sources import (
    PUBLISHED_ISW_SIGN,
    THESIS_ISW_SIGN,
    PerturbationHistory,
    ScatteringHistory,
    mode_multipole,
    source_doppler,
    source_integrated,
    temperature_transfer,
)


# ---------------------------------------------------------------------------
# fixtures: smooth, analytic histories. Nothing physical is claimed of them;
# they exist so the algebra of (177)-(179) can be checked without a
# recombination solve standing in the way.
# ---------------------------------------------------------------------------


def _history(eta: np.ndarray, *, constant_potentials: bool = False) -> PerturbationHistory:
    if constant_potentials:
        phi_a = np.full_like(eta, 0.3)
        phi_h = np.full_like(eta, -0.3)
    else:
        phi_a = 0.3 * np.exp(-eta / 1.7)
        phi_h = -0.3 * np.exp(-eta / 2.3)
    return PerturbationHistory(
        eta=eta,
        delta_T=0.11 * np.cos(0.7 * eta),
        phi_a=phi_a,
        phi_h=phi_h,
        tau_1=0.05 * np.sin(1.3 * eta),
        v_b=0.02 * np.sin(0.9 * eta) + 0.01,
        frame="newtonian",
    )


def _scattering(eta: np.ndarray, *, eta_star: float = 0.6, width: float = 0.05):
    kappa_prime = 1.0 / (0.2 + eta)
    visibility = np.exp(-0.5 * ((eta - eta_star) / width) ** 2) / (width * np.sqrt(2 * np.pi))
    return ScatteringHistory(
        eta=eta, kappa_prime=kappa_prime, visibility=visibility, damping_k=800.0
    )


# ---------------------------------------------------------------------------
# (177)-(179)
# ---------------------------------------------------------------------------


def test_history_rejects_a_ragged_grid():
    with pytest.raises(ValueError):
        PerturbationHistory(
            eta=np.linspace(0, 1, 10),
            delta_T=np.zeros(9),
            phi_a=np.zeros(10),
            phi_h=np.zeros(10),
            tau_1=np.zeros(10),
            v_b=np.zeros(10),
        )


def test_the_printed_doppler_bracket_equals_the_contracted_form():
    """(178) prints kappa' v_B' + kappa'' v_B. That is (kappa' v_B)'.

    The printed form is what the code carries, so this test is the guard that the
    transcription is the product rule and not something else that merely looks
    like it.
    """
    eta = np.linspace(0.05, 2.0, 2000)
    history = _history(eta)
    scattering = _scattering(eta)

    printed = scattering.kappa_prime * history.derivative("v_b") + (
        scattering.kappa_double_prime() * history.v_b
    )
    contracted = CubicSpline(eta, scattering.kappa_prime * history.v_b).derivative()(eta)

    interior = slice(5, -5)
    assert np.allclose(printed[interior], contracted[interior], rtol=1e-6, atol=1e-9)


def test_the_dipole_enters_the_doppler_source_linearly_in_k():
    """(1/3) k tau_1 is the only k-dependence of (178) apart from the damping."""
    eta = np.linspace(0.05, 2.0, 800)
    history = PerturbationHistory(
        eta=eta,
        delta_T=np.zeros_like(eta),
        phi_a=np.zeros_like(eta),
        phi_h=np.zeros_like(eta),
        tau_1=np.full_like(eta, 0.4),
        v_b=np.zeros_like(eta),
    )
    scattering = ScatteringHistory(
        eta=eta, kappa_prime=np.zeros_like(eta), visibility=np.ones_like(eta)
    )
    one = source_doppler(history, scattering, k_com=1.0)
    ten = source_doppler(history, scattering, k_com=10.0)
    assert np.allclose(ten, 10.0 * one)
    assert np.allclose(one, (1.0 / 3.0) * 0.4)


def test_diffusion_damping_is_shared_by_the_two_integrated_sources():
    eta = np.linspace(0.05, 2.0, 400)
    history, scattering = _history(eta), _scattering(eta)
    aH = CDM_MODEL.aH_of_eta(np.clip(eta, 1e-6, CDM_MODEL.eta_0))

    undamped = ScatteringHistory(
        eta=eta, kappa_prime=scattering.kappa_prime, visibility=scattering.visibility
    )
    factor = scattering.diffusion(400.0)
    assert factor == pytest.approx(np.exp(-((400.0 / 800.0) ** 2)))
    assert np.allclose(
        source_doppler(history, scattering, 400.0),
        factor * source_doppler(history, undamped, 400.0),
    )
    assert np.allclose(
        source_integrated(history, scattering, 400.0, aH=aH),
        factor * source_integrated(history, undamped, 400.0, aH=aH),
    )


def test_isw_sign_is_a_finding_not_a_free_parameter():
    eta = np.linspace(0.05, 2.0, 100)
    history, scattering = _history(eta), _scattering(eta)
    aH = CDM_MODEL.aH_of_eta(np.clip(eta, 1e-6, CDM_MODEL.eta_0))
    with pytest.raises(ValueError):
        source_integrated(history, scattering, 100.0, aH=aH, isw_sign=0.0)


def test_b6_sign_alternative_is_not_a_no_op():
    """The two readings of (179) give different sources. B-6 has consequences.

    Worth asserting explicitly: if the threading term happened to be negligible
    the finding would be moot, and the record should not claim otherwise.
    """
    eta = np.linspace(0.05, 2.0, 600)
    history, scattering = _history(eta), _scattering(eta)
    aH = CDM_MODEL.aH_of_eta(np.clip(eta, 1e-6, CDM_MODEL.eta_0))

    published = source_integrated(history, scattering, 100.0, aH=aH, isw_sign=PUBLISHED_ISW_SIGN)
    thesis = source_integrated(history, scattering, 100.0, aH=aH, isw_sign=THESIS_ISW_SIGN)
    separation = np.max(np.abs(published - thesis)) / np.max(np.abs(published))
    assert separation > 0.1


def test_in_eds_with_constant_potentials_only_the_threading_term_survives():
    """The discriminator for B-6, stated as a test while the finding is open.

    Einstein-de Sitter has Phi' = 0, so (179)'s integrated-Sachs-Wolfe proper
    vanishes identically and whatever remains is the disputed term alone. That it
    does *not* vanish is the reason the sign matters: it is a term that survives
    where the standard ISW does not.
    """
    eta = np.linspace(0.05, 2.0, 600)
    history = _history(eta, constant_potentials=True)
    scattering = _scattering(eta)
    aH = CDM_MODEL.aH_of_eta(np.clip(eta, 1e-6, CDM_MODEL.eta_0))

    interior = slice(5, -5)
    isw_proper = (history.derivative("phi_a") - history.derivative("phi_h"))[interior]
    assert np.allclose(isw_proper, 0.0, atol=1e-10)

    remaining = source_integrated(history, scattering, 1.0, aH=aH)[interior]
    assert np.max(np.abs(remaining)) > 1e-3


# ---------------------------------------------------------------------------
# (176)
# ---------------------------------------------------------------------------


def test_the_left_hand_side_of_176_is_the_alpha_normalisation():
    """beta_l / (2l+1) == 1 / alpha_l, exactly, as rationals."""
    for ell in (0, 1, 2, 5, 17, 60):
        assert beta(ell) / Fraction(2 * ell + 1) == 1 / alpha(ell)


def test_176_with_an_impulsive_source_is_the_free_streaming_projection():
    """The cross-check between the two halves of the code.

    With no integrated sources, (176) is S_P j_l(k dEta_*). Setting S_P = 1 must
    therefore return exactly the free-streaming projection of a unit monopole
    released at eta_*, which `functions.harmonics` already matches against three
    external hierarchies. A normalisation slip in either half breaks this.
    """
    eta_star, eta_0, k_com = 0.06, 2.0, 40.0
    eta = np.linspace(eta_star, eta_0, 4000)
    quiet = np.zeros_like(eta)

    for ell in (2, 5, 10, 25, 40):
        got = temperature_transfer(
            ell,
            k_com,
            eta=eta,
            s_primary_at_star=1.0,
            s_integrated=quiet,
            eta_0=eta_0,
            eta_star=eta_star,
        )
        expected = float(analytic_projection(k_com, np.array([eta_0]), eta_star, ell)[0])
        assert got == pytest.approx(expected, rel=1e-12, abs=1e-14)


def test_mode_multipole_undoes_the_alpha_normalisation():
    for ell in (2, 9, 30):
        assert mode_multipole(ell, 1.0) == pytest.approx(float(alpha(ell)))


def test_the_integrated_term_accumulates_along_the_line_of_sight():
    """A source that is non-zero only near eta_* must reproduce the primary term.

    This is the statement that the line-of-sight integral and the instantaneous
    evaluation are consistent: a narrow visibility is an impulse, and (176)'s two
    halves must agree in that limit.

    A narrow source of unit area is an impulse only to the extent that
    $j_\\ell$ is straight across it, so the residual is not zero and should not be
    asserted to be: it is the curvature of $j_\\ell$ over the width, of relative
    order $(k\\sigma)^2 j_\\ell''/j_\\ell$. The coefficient is not asserted, because
    it is a property of $j_\\ell$ at that argument and guessing it would be
    decoration; the *scaling* is asserted, because it is a property of the
    line-of-sight integral. Halve the width and the residual must fall by four.
    """
    eta_star, eta_0, k_com = 0.6, 2.0, 12.0
    eta = np.linspace(0.05, eta_0, 40001)

    def residual(width: float, ell: int) -> float:
        impulse = np.exp(-0.5 * ((eta - eta_star) / width) ** 2) / (width * np.sqrt(2 * np.pi))
        integrated = temperature_transfer(
            ell, k_com, eta=eta, s_primary_at_star=0.0,
            s_integrated=impulse, eta_0=eta_0, eta_star=eta_star,
        )
        instantaneous = temperature_transfer(
            ell, k_com, eta=eta, s_primary_at_star=1.0,
            s_integrated=np.zeros_like(eta), eta_0=eta_0, eta_star=eta_star,
        )
        return abs(integrated - instantaneous) / abs(instantaneous)

    for ell in (2, 8, 20):
        wide, narrow = residual(0.004, ell), residual(0.002, ell)
        assert wide < (k_com * 0.004) ** 2  # bounded by the curvature scale
        assert narrow / wide == pytest.approx(0.25, rel=0.1)


def test_the_tabulated_and_direct_bessel_routes_to_176_agree():
    """Route 3's tabulated half must not change the answer, only the cost."""
    from functions.spectra.bessel_table import BesselTable

    eta_star, eta_0, k_com = 0.06, 2.0, 30.0
    eta = np.linspace(eta_star, eta_0, 2000)
    history = _history(eta)
    scattering = _scattering(eta, eta_star=0.4, width=0.08)
    aH = CDM_MODEL.aH_of_eta(np.clip(eta, 1e-6, CDM_MODEL.eta_0))
    integrated = source_doppler(history, scattering, k_com) + source_integrated(
        history, scattering, k_com, aH=aH
    )

    table = BesselTable.build(ell_max=30, x_max=k_com * (eta_0 - eta_star) + 10.0)
    for ell in (2, 10, 30):
        kwargs = dict(
            eta=eta, s_primary_at_star=0.7, s_integrated=integrated,
            eta_0=eta_0, eta_star=eta_star,
        )
        direct = temperature_transfer(ell, k_com, **kwargs)
        tabulated = temperature_transfer(ell, k_com, table=table, **kwargs)
        assert tabulated == pytest.approx(direct, rel=1e-5, abs=1e-9)
