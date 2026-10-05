"""The Sachs-Wolfe angular power spectrum of Annals II §8.3.

Published equation numbers. Identical in the published and arXiv editions.

(198)   C^SW_l = (1/2pi) H0^4 Omega0^1.54 Int (dk/k^2) P(k) j_l^2(k dEta_*)

(199)   Int_0^inf (dz/z^m) j_l^2(z)
            = (pi/2^{m+2}) m! (l - m/2 - 1/2)! / [ (m/2)! (l + m/2 + 1/2)! ]

        **As printed, (199) is correct only where Gamma(m/2+1) = 1, that is at
        m = 0 and m = 2.** The denominator requires [(m/2)!]^2. Finding G3.

(200)   with P(k) = A k^{n-1} (J.1)

(201)   C_l = (A/2) H0^4 Omega0^1.54 / [(2l+3)(2l+1)(2l-1)]      for n = 1

(204)   C^(CDM)_l, the horizon-scale normalisation, using (199) at m = 1 ---
        the case where the printed identity is wrong.

**The analytic reduction.** Substituting z = k chi into (200),

    Int dk k^{n-3} j_l^2(k chi) = chi^{2-n} Int dz z^{n-3} j_l^2(z)
                                = chi^{2-n} I(m = 3-n),

so for n = 1 the reduction carries a factor chi = dEta_*, and

    C_l = (A/2) H0^4 Omega0^1.54 * chi / [(2l+3)(2l+1)(2l-1)].

The printed (201) does not carry that factor. Whether that is an omission or an
absorption into the normalisation of A is decided numerically, not asserted here:
`cl_large_scale_reduced` is the reduction and `cl_large_scale_printed` is (201)
as printed, and the test compares them.
"""

from __future__ import annotations

from math import pi

import numpy as np
from scipy.integrate import quad
from scipy.special import gamma, spherical_jn

__all__ = [
    "bessel_integral",
    "bessel_integral_printed",
    "bessel_integral_numeric",
    "cl_sachs_wolfe_quadrature",
    "cl_large_scale_reduced",
    "cl_large_scale_printed",
]


def bessel_integral(m: float, ell: float) -> float:
    """(199), corrected: the denominator carries [(m/2)!]^2. Finding G3."""
    return (
        (pi / 2 ** (m + 2))
        * gamma(m + 1)
        * gamma(ell - m / 2 + 0.5)
        / (gamma(m / 2 + 1) ** 2 * gamma(ell + m / 2 + 1.5))
    )


def bessel_integral_printed(m: float, ell: float) -> float:
    """(199) exactly as printed. Kept so the difference is demonstrable, not asserted."""
    return (
        (pi / 2 ** (m + 2))
        * gamma(m + 1)
        * gamma(ell - m / 2 + 0.5)
        / (gamma(m / 2 + 1) * gamma(ell + m / 2 + 1.5))
    )


def bessel_integral_numeric(m: float, ell: int, *, cycles: int = 500) -> float:
    """The same integral by quadrature, with an analytic tail. The arbiter.

    j_l^2 oscillates with period pi once z exceeds l, so the oscillatory region is
    integrated in windows aligned to that period rather than in a few wide panels.
    A single wide panel silently loses accuracy at large l, which is a property of
    the integrator and not of the identity being checked.
    """
    f = lambda z: spherical_jn(ell, z) ** 2 / z**m  # noqa: E731

    # the rise, where j_l is not yet oscillatory
    turn = max(2.0 * ell + 20.0, 40.0)
    total, _ = quad(f, 1e-12, turn, limit=800)

    # the oscillatory region, in windows of a few periods each
    width = 8.0 * pi
    a = turn
    for _ in range(cycles):
        b = a + width
        value, _ = quad(f, a, b, limit=80)
        total += value
        a = b

    return total + 1.0 / (2 * (1 + m) * a ** (1 + m))  # <sin^2> = 1/2


def cl_sachs_wolfe_quadrature(
    ell: int, *, d_eta: float, amplitude: float = 1.0, n: float = 1.0,
    h0: float = 1.0, omega0: float = 1.0,
) -> float:
    """(198) with P(k) = A k^{n-1}, integrated numerically in k.

    No analytic reduction is used, so this is independent of (199) and of the
    change of variable. It is the arbiter for (200) -> (201).
    """
    pref = h0**4 * omega0**1.54 / (2 * pi)
    f = lambda k: amplitude * k ** (n - 1) / k**2 * spherical_jn(ell, k * d_eta) ** 2  # noqa: E731
    total, a = 0.0, 1e-9 / d_eta
    for b in (1.0, 10.0, 50.0, 200.0, 1000.0, 5000.0, 20000.0):
        value, _ = quad(f, a, b / d_eta, limit=400)
        total += value
        a = b / d_eta
    m = 3 - n
    total += amplitude * d_eta ** (n - 2) / (2 * (1 + m) * (a * d_eta) ** (1 + m))
    return pref * total


def cl_large_scale_reduced(
    ell: int, *, d_eta: float, amplitude: float = 1.0, n: float = 1.0,
    h0: float = 1.0, omega0: float = 1.0,
) -> float:
    """(200) reduced with the corrected (199). Carries chi^{2-n}."""
    return (
        amplitude * h0**4 * omega0**1.54 / (2 * pi)
        * d_eta ** (2 - n)
        * bessel_integral(3 - n, ell)
    )


def cl_large_scale_printed(
    ell: int, *, amplitude: float = 1.0, h0: float = 1.0, omega0: float = 1.0
) -> float:
    """(201) exactly as printed, for n = 1. No chi."""
    return (
        amplitude / 2 * h0**4 * omega0**1.54
        / ((2 * ell + 3) * (2 * ell + 1) * (2 * ell - 1))
    )


def eds_conformal_distance(z_star: float = 1100.0) -> float:
    """dEta_* = eta_0 - eta_* in units of 1/H0, flat matter dominated, a_0 = 1."""
    return 2.0 * (1.0 - 1.0 / np.sqrt(1.0 + z_star))
