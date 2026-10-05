"""The closed-form k-integral kernel, and the FFTLog built on it.

Convention imported: none. Arithmetic and quadrature on the printed identity.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import spherical_jn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.spectra.kernels import (  # noqa: E402
    bessel_square_kernel,
    convergence_window,
    fftlog_primary_integral,
)
from functions.spectra.sachs_wolfe import bessel_integral  # noqa: E402

CHI = 1.9397249997058175


def _cdm_like(k):
    q = k / 0.48
    t = (
        np.log(1 + 2.34 * q) / (2.34 * q)
        * (1 + 3.89 * q + (16.1 * q) ** 2 + (5.46 * q) ** 3 + (6.71 * q) ** 4) ** -0.25
    )
    return k * t**2 / k**2


def _quadrature(ell, chi=CHI):
    g = lambda k: _cdm_like(k) * spherical_jn(ell, k * chi) ** 2  # noqa: E731
    total, a = 0.0, 1e-7
    for b in np.concatenate([np.logspace(-6, 1, 60), np.arange(10.0, 600.0, 0.5)]):
        value, _ = quad(g, a, b, limit=60)
        total += value
        a = b
    return total


@pytest.mark.parametrize("m", (0.0, 1.0, 2.0, 2.6))
@pytest.mark.parametrize("ell", (2, 10, 30))
def test_complex_kernel_reduces_to_the_real_identity(m, ell):
    assert abs(complex(bessel_square_kernel(m, ell)).real / bessel_integral(m, ell) - 1) < 1e-12


def test_kernel_survives_large_ell():
    """loggamma keeps the kernel finite where gamma would overflow, above l ~ 170."""
    value = complex(bessel_square_kernel(2.0, 1000)).real
    assert np.isfinite(value) and value > 0


def test_convergence_window_is_reported():
    assert convergence_window(2) == (-1.0, 5.0)


@pytest.mark.parametrize("ell", (2, 10, 40, 100))
def test_fftlog_matches_quadrature_on_a_non_power_law_integrand(ell):
    """The whole point: no oscillatory quadrature, and it still agrees."""
    k = np.logspace(-5, 4, 8192)
    got = fftlog_primary_integral(k, _cdm_like(k), ell, CHI)
    assert abs(got / _quadrature(ell) - 1) < 1e-5, ell


def test_an_untilted_decomposition_fails_at_moderate_ell():
    """bias = 0 collapses to a numerical floor. Pinned so the default is not 'tidied'.

    The failure is cancellation, not a coding error: the terms are far larger than
    their sum. It is recorded as a test so that nobody later removes the tilt.
    """
    k = np.logspace(-5, 4, 8192)
    untilted = fftlog_primary_integral(k, _cdm_like(k), 100, CHI, bias=0.0)
    assert abs(untilted / _quadrature(100) - 1) > 1.0
