"""The Sachs-Wolfe spectrum of Annals II §8.3, and finding G5.

Convention imported: none. Arithmetic and quadrature on the printed equations.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.spectra.sachs_wolfe import (  # noqa: E402
    bessel_integral,
    bessel_integral_numeric,
    bessel_integral_printed,
    cl_large_scale_printed,
    cl_large_scale_reduced,
    cl_sachs_wolfe_quadrature,
    eds_conformal_distance,
)

ELLS = (2, 5, 10, 20, 30)


@pytest.mark.parametrize("ell", (2, 10, 30))
@pytest.mark.parametrize("m", (0, 1, 2, 3))
def test_corrected_bessel_identity_matches_quadrature(m, ell):
    """(199) with [(m/2)!]^2 reproduces the integral; as printed it does not."""
    from scipy.special import gamma

    numeric = bessel_integral_numeric(m, ell)
    assert abs(bessel_integral(m, ell) / numeric - 1) < 2e-5, (m, ell)
    # the printed form departs by exactly Gamma(m/2+1)
    assert abs(bessel_integral_printed(m, ell) / numeric - float(gamma(m / 2 + 1))) < 2e-5


def test_the_analytic_reduction_matches_the_quadrature():
    """(200) reduced through (199) equals (198) integrated directly in k."""
    chi = eds_conformal_distance()
    for ell in ELLS:
        q = cl_sachs_wolfe_quadrature(ell, d_eta=chi)
        r = cl_large_scale_reduced(ell, d_eta=chi)
        assert abs(r / q - 1) < 1e-5, ell


def test_g5_printed_201_is_short_by_the_comoving_distance():
    """Finding G5. (201) as printed omits the factor chi from the reduction.

    Substituting z = k chi into (200) gives Int dk k^{n-3} j_l^2(k chi)
    = chi^{2-n} Int dz z^{n-3} j_l^2(z), so n = 1 carries one factor of chi.
    The printed (201) does not.

    Pinned here so that a harness comparing a reconstruction against printed
    (201) does not read the resulting factor as an error of the reconstruction,
    and so that the amplitude is not normalised through the short form.
    """
    chi = eds_conformal_distance()
    for ell in ELLS:
        q = cl_sachs_wolfe_quadrature(ell, d_eta=chi)
        p = cl_large_scale_printed(ell)
        assert abs(q / p - chi) < 1e-4 * chi, ell
