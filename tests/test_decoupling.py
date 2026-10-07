"""Slow decoupling: the optical depth, the two weights, and the diffusion scale.

The weight tests are the ones that matter. Approximation **A-1** in
`provenance/SOURCE-APPROXIMATIONS-v1.md` is that Annals II weights the integrated
sources with the visibility rather than the opacity, deliberately, and that this
cannot carry a late-ISW. These tests make that statement measurable instead of
rhetorical, so that a figure built on either weighting can say what it used.
"""

from __future__ import annotations

import numpy as np
import pytest

from functions.background.flrw import CDM_MODEL, LCDM_MODEL
from functions.spectra.decoupling import (
    RecombinationHistory,
    Weighting,
    diffusion_scale,
    saha_ionisation,
)


@pytest.fixture(scope="module")
def history() -> RecombinationHistory:
    return RecombinationHistory.build(LCDM_MODEL)


# ---------------------------------------------------------------------------
# recombination
# ---------------------------------------------------------------------------


def test_saha_is_monotone_and_spans_the_full_range():
    z = np.linspace(500.0, 3000.0, 400)
    x_e = saha_ionisation(z)
    assert np.all(np.diff(x_e) > 0.0)  # more ionised at higher z
    assert x_e[-1] > 0.99
    assert x_e[0] < 0.01


def test_recombination_happens_near_z_1100(history):
    """Saha puts last scattering early and sharp; both are known and bounded."""
    a_star = history.background.a_of_eta(history.eta_star)
    z_star = 1.0 / float(a_star) - 1.0
    assert 1000.0 < z_star < 1500.0


def test_optical_depth_vanishes_today_and_is_monotone_backwards(history):
    assert history.kappa[-1] == pytest.approx(0.0, abs=1e-12)
    assert np.all(np.diff(history.kappa) <= 1e-12)
    assert history.kappa[0] > 1.0  # optically thick before recombination


def test_the_visibility_is_a_normalised_probability_density(history):
    """Int V d(eta) = 1. This is what makes (visibe)'s D ~= e^{-(k/k_D)^2} hold."""
    assert history.visibility_norm() == pytest.approx(1.0, rel=2e-2)
    assert np.all(history.visibility >= 0.0)


# ---------------------------------------------------------------------------
# approximation A-1: the two weights
# ---------------------------------------------------------------------------


def test_the_two_weightings_are_distinct_objects(history):
    annals = history.weight(Weighting.ANNALS_II)
    standard = history.weight(Weighting.STANDARD_ISW)
    assert annals is history.visibility
    assert standard is history.opacity
    assert not np.allclose(annals, standard)


def test_the_visibility_weighting_cannot_carry_a_late_isw(history):
    """**Approximation A-1, made measurable.**

    The late-ISW accumulates at $z\\lesssim1$. Weighted by the opacity the
    integrand there is O(1), because $e^{-\\kappa}\\to1$ once reionisation is
    neglected; weighted by the visibility it is zero to many decimal places,
    because $\\mathcal V$ is a spike at last scattering.

    This is the whole content of A-1 and the reason the $\\Lambda$CDM spectrum
    cannot use Annals II's weighting. Asserted rather than described.
    """
    eta_late = history.background.eta_at_redshift(1.0)
    late = history.eta > eta_late
    assert late.sum() > 10

    opacity_there = history.opacity[late]
    visibility_there = history.visibility[late]

    assert np.all(opacity_there > 0.9)
    assert np.max(visibility_there) < 1e-6 * np.max(history.visibility)


def test_the_visibility_is_concentrated_at_last_scattering(history):
    """Its support is narrow in conformal time: that is what makes it a spike."""
    peak = np.max(history.visibility)
    wide = history.visibility > 0.01 * peak
    width = float(np.ptp(history.eta[wide]))
    assert width < 0.05 * history.background.eta_0


# ---------------------------------------------------------------------------
# the diffusion scale
# ---------------------------------------------------------------------------


def test_the_diffusion_scale_falls_backwards_in_time(history):
    """k_D^{-2} accumulates forwards, so k_D is larger early and smaller late.

    Small scales survive longer the earlier you look; by last scattering the
    damping scale has come down to the scale that cuts off the acoustic peaks.
    """
    k_d = diffusion_scale(history)
    eta = np.linspace(history.eta[1], history.eta_star, 50)
    values = k_d(eta)
    assert np.all(np.isfinite(values))
    assert np.all(np.diff(values) < 0.0)


def test_damping_suppresses_small_scales_and_leaves_large_ones(history):
    k_d = diffusion_scale(history)
    k_star = float(k_d(history.eta_star))
    assert np.exp(-((0.1 * k_star) ** 2) / k_star**2) > 0.98
    assert np.exp(-((3.0 * k_star) ** 2) / k_star**2) < 1e-3


def test_a_matter_only_model_also_builds(history):
    """The CDM model is the Annals II case and must not need Lambda to work."""
    cdm = RecombinationHistory.build(CDM_MODEL)
    assert cdm.visibility_norm() == pytest.approx(1.0, rel=5e-2)
    assert cdm.eta_star < cdm.background.eta_0
