"""The background is derived from the 1+3 constraint; these tests are its arbiters.

The Einstein-de Sitter closed form is the one case where the answer is known
exactly, so it is the check that matters: a quadrature or substitution error
shows up there before it reaches the sources.
"""

from __future__ import annotations

import numpy as np
import pytest

from functions.background.flrw import CDM_MODEL, LCDM_MODEL, Background, eds_scale_factor
from functions.spectra.sachs_wolfe import eds_conformal_distance


def test_curvature_is_derived_not_supplied():
    assert Background(omega_m=0.3, omega_lambda=0.7).omega_k == pytest.approx(0.0, abs=1e-15)
    assert Background(omega_m=0.3, omega_lambda=0.0).omega_k == pytest.approx(0.7)


def test_eds_conformal_time_today_is_two_over_h0():
    assert CDM_MODEL.eta_0 == pytest.approx(2.0, rel=1e-9)


def test_eds_scale_factor_matches_the_closed_form():
    eta = np.linspace(0.02, 2.0, 400)
    assert np.allclose(CDM_MODEL.a_of_eta(eta), eds_scale_factor(eta), rtol=1e-8, atol=1e-10)


def test_eds_conformal_distance_matches_the_sachs_wolfe_module():
    """The two routes to dEta_* must not disagree; (198) uses one and (176) the other."""
    assert CDM_MODEL.conformal_distance(1100.0) == pytest.approx(
        eds_conformal_distance(1100.0), rel=1e-7
    )


@pytest.mark.parametrize("model", [CDM_MODEL, LCDM_MODEL, Background(omega_m=0.3, omega_lambda=0.0)])
def test_the_constraint_holds_along_the_solution(model):
    """a'/a from the integrated solution reproduces aH from the constraint itself.

    This is the statement that the background actually solves the equation it was
    derived from, rather than merely being a smooth interpolation.
    """
    eta = np.linspace(0.15 * model.eta_0, 0.98 * model.eta_0, 300)
    a = model.a_of_eta(eta)
    a_prime = model.a_of_eta.derivative()(eta)
    assert np.allclose(a_prime / a, model.conformal_hubble(a), rtol=2e-6)


def test_lambda_extends_conformal_time_beyond_the_eds_value():
    """Not a precision test --- a sanity direction. Lambda buys conformal time."""
    assert LCDM_MODEL.eta_0 > CDM_MODEL.eta_0
    assert 3.0 < LCDM_MODEL.eta_0 < 3.5


def test_radiation_start_is_regular():
    """With Om_r > 0 the u = sqrt(a) substitution must still start at eta = 0."""
    model = Background(omega_m=0.3, omega_lambda=0.7, omega_r=8.5e-5)
    assert model.eta_of_a(0.0) == pytest.approx(0.0, abs=1e-12)
    assert np.all(np.diff(model.eta_of_a(np.linspace(0.0, 1.0, 50))) > 0.0)
