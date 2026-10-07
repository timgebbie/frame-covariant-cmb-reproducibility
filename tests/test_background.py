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


# ---------------------------------------------------------------------------
# The Gauss constraint and Annals II (G.3)
# ---------------------------------------------------------------------------


def test_the_gauss_constraint_sign_is_the_corrected_one_and_the_printed_one_has_no_solution():
    """**Finding B-7.** Annals II (G.3) prints $+\\tfrac23\\Theta^2$; the thesis and
    Cargese (55) print $-\\tfrac23\\Theta^2$. The FLRW limit decides it.

    The $1+3$ Gauss constraint, with shear and vorticity switched off,

        R3 = 2 mu + 2 Lambda - (2/3) Theta^2,

    reduces at ``R3 = 6K/a^2``, ``Theta = 3H`` to ``H^2 = (mu+Lambda)/3 - K/a^2``,
    the Friedmann equation. The printed sign gives ``H^2 = K/a^2 - (mu+Lambda)/3``,
    which in the **flat** case is ``-(mu+Lambda)/3``: negative for any positive
    energy density, so there is no solution. (Coordination's independent check
    reached the same verdict; its intermediate form carried ``-K/a^2`` where this
    convention, ``R3 = +6K/a^2`` for a closed section, gives ``+K/a^2``. The
    conclusion is unaffected --- the flat case settles it without reference to
    ``K`` at all.)

    The point of this test is not that the misprint exists --- that belongs in the
    findings record --- but that **this bundle cannot inherit it**. The background
    is derived from the constraint rather than transcribed from (G.3), and this
    test pins the derived form against the implementation, so a later "correction"
    of the code towards the printed equation fails here.
    """
    import sympy as sp

    H, mu, Lam, K, a, Theta, R3 = sp.symbols("H mu Lambda K a Theta R3", positive=True)

    def friedmann(sign: int):
        constraint = sp.Eq(R3, 2 * mu + 2 * Lam + sign * sp.Rational(2, 3) * Theta**2)
        reduced = constraint.subs({R3: 6 * K / a**2, Theta: 3 * H})
        return sp.solve(reduced, H**2)[0]

    corrected, printed = friedmann(-1), friedmann(+1)
    assert sp.simplify(corrected - ((mu + Lam) / 3 - K / a**2)) == 0
    assert sp.simplify(printed - (K / a**2 - (mu + Lam) / 3)) == 0

    # flat case: the printed sign admits no solution with positive energy density
    assert printed.subs({K: 0}) == sp.simplify(-(mu + Lam) / 3)
    assert printed.subs({mu: 1, Lam: 0, K: 0, a: 1}) < 0

    # and the implementation carries the corrected form, identically in a
    h0, om_r, om_m, om_l = sp.symbols("H0 Omega_r Omega_m Omega_Lambda", positive=True)
    om_k = 1 - om_r - om_m - om_l
    mu_of_a = 3 * h0**2 * (om_r / a**4 + om_m / a**3)
    implemented = h0**2 * (om_r / a**4 + om_m / a**3 + om_k / a**2 + om_l)
    assert sp.simplify(
        implemented - corrected.subs({mu: mu_of_a, Lam: 3 * h0**2 * om_l, K: -(h0**2) * om_k})
    ) == 0


def test_the_implementation_agrees_numerically_with_the_friedmann_reduction():
    """The symbolic identity above, evaluated through the code that actually runs."""
    model = Background(omega_m=0.3, omega_lambda=0.7, omega_r=8.5e-5)
    a = np.array([1e-3, 1e-2, 0.1, 0.5, 1.0])
    mu = 3.0 * (model.omega_r / a**4 + model.omega_m / a**3)
    lam = 3.0 * model.omega_lambda
    curvature = -model.omega_k / a**2
    assert np.allclose((model.conformal_hubble(a) / a) ** 2, (mu + lam) / 3.0 - curvature)
