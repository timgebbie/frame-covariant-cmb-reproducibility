r"""(186), (187) and (188): the angular power spectrum by two routes.

The first test is the one that matters. The harmonic normalisation cancels out
of the observable exactly, and asserting that in **exact rationals** means a
$\beta_\ell$ or $\alpha_\ell$ slip cannot hide inside the spectrum.
"""

from __future__ import annotations

from fractions import Fraction
from math import pi

import numpy as np
import pytest

from functions.harmonics.weights import alpha, beta, delta_over_four_pi
from functions.spectra.angular import (
    angular_spectrum,
    cl_covariant_route,
    cl_mode_route,
    d_ell,
    multipole_mean_square,
)


def test_the_harmonic_normalisation_cancels_out_of_186_exactly():
    """$\\beta_\\ell^2\\alpha_\\ell^2/(2\\ell+1)^2 = 1$, as rationals, for every $\\ell$.

    (176) returns $\\alpha_\\ell^{-1}\\tau_\\ell$, so (186)'s prefactor multiplied by
    $\\alpha_\\ell^2$ must be unity. In exact arithmetic, because the point is that
    it is an identity and not a numerical near-miss.
    """
    for ell in (0, 1, 2, 3, 7, 20, 100, 1000):
        assert beta(ell) ** 2 * alpha(ell) ** 2 / Fraction(2 * ell + 1) ** 2 == 1


def test_the_two_routes_agree_to_machine_precision_on_real_input():
    """(186) and (187)+(188) are identical analytically; check the arithmetic.

    Proven exactly elsewhere; this runs both over a non-trivial transfer so the
    assertion covers the code that actually executes, not only the algebra.
    """
    k = np.logspace(-3, 0, 400)
    power = k ** (-3.0)
    for ell in (2, 10, 50, 200):
        transfer = np.sin(k * 100.0) / (1.0 + (k * 50.0) ** 2)
        mode = cl_mode_route(ell, k, transfer, power)
        cov = cl_covariant_route(ell, k, transfer, power)
        assert mode == pytest.approx(cov, rel=1e-12)


def test_188_is_delta_over_2l_plus_1_times_187():
    k = np.logspace(-3, 0, 200)
    power, transfer = k ** (-3.0), np.exp(-((k * 30.0) ** 2))
    for ell in (2, 9, 40):
        ms = multipole_mean_square(ell, k, transfer, power)
        expected = 4.0 * pi * float(delta_over_four_pi(ell)) / (2 * ell + 1) * ms
        assert cl_covariant_route(ell, k, transfer, power) == pytest.approx(expected, rel=1e-12)


def test_cl_is_quadratic_in_the_transfer_and_linear_in_the_power():
    k = np.logspace(-3, 0, 200)
    power, transfer = k ** (-3.0), np.exp(-((k * 30.0) ** 2))
    base = cl_mode_route(10, k, transfer, power)
    assert cl_mode_route(10, k, 2.0 * transfer, power) == pytest.approx(4.0 * base, rel=1e-12)
    assert cl_mode_route(10, k, transfer, 3.0 * power) == pytest.approx(3.0 * base, rel=1e-12)


def test_d_ell_is_the_plotted_combination():
    ell = np.array([2, 10, 100])
    cl = np.array([1.0, 0.5, 0.25])
    assert np.allclose(d_ell(ell, cl), ell * (ell + 1) * cl / (2 * pi))


def test_angular_spectrum_rejects_a_mis_shaped_transfer():
    k = np.logspace(-3, 0, 50)
    with pytest.raises(ValueError):
        angular_spectrum(np.array([2, 3]), k, np.zeros((3, k.size)), k ** (-3.0))


def test_angular_spectrum_reports_both_routes_and_their_gap():
    k = np.logspace(-3, 0, 300)
    power = k ** (-3.0)
    ells = np.array([2, 5, 10])
    transfer = np.vstack([np.exp(-((k * 20.0) ** 2)) * (1.0 + 0.1 * l) for l in ells])
    spectrum = angular_spectrum(ells, k, transfer, power)
    assert spectrum.max_route_difference < 1e-12
    assert np.all(spectrum.cl_mode > 0.0)
    assert np.allclose(spectrum.d_ell(), d_ell(ells, spectrum.cl_mode))


def test_the_route_comparison_states_what_the_two_routes_do_not_share():
    """Coordination's point, 2026-10-09, made executable.

    Agreement between two routes is evidence only about what differs between
    them. These two share the transfer function, both grids, the sources and
    the background; they differ in the harmonic weights alone. The docstring
    must keep saying so, because the figure's caption is written from it and a
    reader who takes $10^{-16}$ as evidence about the physics has been misled
    by us rather than by the number.

    T-3 is the case in point: the routes agreed throughout while the spectrum
    was wrong by 575%.
    """
    from functions.spectra.angular import AngularSpectrum

    doc = AngularSpectrum.max_route_difference.__doc__ or ""
    assert "do not share" in doc, "the property no longer says what is being compared"
    assert "harmonic weight" in doc, "the property no longer names the only difference"
    assert "T-3" in doc, "the property no longer carries the case that proves the point"


# --------------------------------------------------------------------------
# Finding T-17: the bundle's ell ceiling was 507, set by a quantity equal to 1.
# --------------------------------------------------------------------------


def test_the_two_routes_agree_as_exact_rationals():
    r"""**The two-route statement, moved into $\mathbb Q$ where it survives.**

    `max_route_difference` compared the routes in doubles, and so could only
    make the comparison where $\beta_\ell$ and $\alpha_\ell$ were *separately*
    representable --- $\ell\le507$. Above that the comparison did not fail, it
    ceased to exist. Here the two rational coefficients are compared directly,
    over the whole range v1.2.0's peaks and v1.5.0's $O(\epsilon^2\ell)$ term
    live in.
    """
    from functions.spectra.angular import _covariant_coefficient, _mode_coefficient

    for ell in (2, 3, 20, 220, 507, 508, 900, 1500, 2000):
        assert _mode_coefficient(ell) == 1, f"(186)'s prefactor is not 1 at ell={ell}"
        assert _covariant_coefficient(ell) == 1, f"(188)'s is not 1 at ell={ell}"
        assert _mode_coefficient(ell) == _covariant_coefficient(ell)


def test_cl_is_computable_above_the_old_ell_ceiling():
    r"""**The regression test for T-17.**

    `float(beta(ell))**2 * float(alpha(ell))**2` raised `OverflowError` for every
    $\ell\ge508$: $\beta_\ell^2$ underflowed to zero, $\alpha_\ell^2$ overflowed,
    and their exact ratio of one was unreachable through them. The first acoustic
    peak is at $\ell\simeq220$ and the damping tail runs to $\ell\simeq2000$, so
    the ceiling sat between the second peak and everything v1.5.0 exists to add,
    with no diagnostic.
    """
    k = np.logspace(-2, 2, 400)
    power, transfer = k ** (-3.0), np.exp(-k / 50.0) / (1.0 + k**2)
    for ell in (508, 900, 1500, 2000):
        mode = cl_mode_route(ell, k, transfer, power)
        cov = cl_covariant_route(ell, k, transfer, power)
        assert np.isfinite(mode) and mode > 0.0, f"mode route failed at ell={ell}"
        assert np.isfinite(cov) and cov > 0.0, f"covariant route failed at ell={ell}"
        # The weights are combined exactly and the quadrature is shared, so
        # these are now the same double and not merely close.
        assert mode == cov, f"the routes differ in the last bit at ell={ell}"


def test_multipole_mean_square_names_its_own_ceiling():
    r"""The one quantity that genuinely overflows must say which it is.

    $\langle\tau_{A_\ell}\tau^{A_\ell}\rangle$ carries
    $\beta_\ell\alpha_\ell^2=(2\ell+1)^2/\beta_\ell$, which is past the double
    range by $\ell\simeq1500$. That is the number, not a defect --- so it raises
    with the reason and points at the route that stays finite, rather than
    returning `inf` into a spectrum. An `OverflowError` with no message is how
    T-17 hid.
    """
    k = np.logspace(-2, 0, 50)
    power, transfer = k ** (-3.0), np.exp(-((k * 30.0) ** 2))
    with pytest.raises(OverflowError, match="T-17"):
        multipole_mean_square(2000, k, transfer, power)
    # and it is still the published route wherever it is representable
    assert np.isfinite(multipole_mean_square(200, k, transfer, power))


def test_a_sparse_bessel_table_cannot_return_the_wrong_multipole():
    r"""Finding **T-18**'s negative control.

    `BesselTable.__call__` indexed by `ell - self.ell[0]`, which is correct only
    while the table is contiguous. Against a sparse table that arithmetic lands
    on a valid index of a **different** multipole and returns it silently. The
    lookup must raise instead.
    """
    from functions.spectra.bessel_table import BesselTable

    sparse = BesselTable.build(ell_max=400, ells=np.array([2, 37, 400]), x_max=50.0)
    assert sparse.ell.tolist() == [2, 37, 400]
    # the old arithmetic would have mapped ell=3 to index 1, i.e. j_37
    with pytest.raises(ValueError, match="not tabulated"):
        sparse(3, np.linspace(0.0, 10.0, 5))
    # and the tabulated ones are the ones asked for
    contiguous = BesselTable.build(ell_max=400, x_max=50.0)
    x = np.linspace(0.0, 40.0, 97)
    for ell in (2, 37, 400):
        assert np.allclose(sparse(ell, x), contiguous(ell, x), rtol=0, atol=0)
    assert sparse.values.shape[0] == 3 and contiguous.values.shape[0] == 401
