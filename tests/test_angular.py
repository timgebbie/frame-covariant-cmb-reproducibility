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
