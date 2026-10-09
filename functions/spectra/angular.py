"""The angular power spectrum, Annals II §7.2 — the v1.0.0 deliverable.

    (186)  C_l = (2/pi) beta_l^2/(2l+1)^2 Int (dk/k) k^3 |tau_l(k,eta_0)|^2
    (187)  <tau_Al tau^Al> = beta_l/(2 pi^2) Int k^2 dk |tau_l|^2
    (188)  C_l = Delta_l (2l+1)^{-1} <tau_Al tau^Al>,   Delta_l = 4 pi beta_l/(2l+1)

**The prefactors cancel, exactly.** (176) returns
$T_\\ell(k)\\equiv\\beta_\\ell\\tau_\\ell(\\eta_0)/(2\\ell+1)=\\alpha_\\ell^{-1}\\tau_\\ell$,
so $\\tau_\\ell=\\alpha_\\ell T_\\ell$ and (186) becomes

    C_l = (2/pi) [beta_l^2/(2l+1)^2] alpha_l^2 Int dk k^2 |T_l|^2
        = (2/pi) Int dk k^2 |T_l(k)|^2,

because $\\alpha_\\ell=(2\\ell+1)/\\beta_\\ell$ makes the bracket exactly one. The
$\\ell$-dependent normalisation of the harmonic expansion vanishes from the
observable, which is what it should do, and the variable in which it vanishes is
precisely the one Appendix~F's free-streaming solution is bare in. Asserted as
exact rationals in `tests/test_angular.py`, not as floating point.

That is worth more than tidiness. It means a $\\beta_\\ell$ or $\\alpha_\\ell$ slip
cannot hide in the spectrum: it would have to survive a cancellation that is an
identity.

**Two routes, one answer.** (186) is the mode route and (187)+(188) the covariant
route; they were proven identical before either was implemented, and both are
computed here so the release reports a number from each rather than a claim that
they agree.

**The covariant route is the one that generalises.** (186) is a statement about
mode coefficients and holds only for almost-Robertson--Walker geometries; (187)
is a multipole mean-square and holds generally. Every released figure plots the
multipole quantity for that reason.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np

from functions.harmonics.weights import alpha, beta, delta_over_four_pi

__all__ = [
    "angular_spectrum",
    "AngularSpectrum",
    "cl_mode_route",
    "cl_covariant_route",
    "multipole_mean_square",
    "d_ell",
]


@dataclass(frozen=True)
class AngularSpectrum:
    """C_l by both routes, with the k-grid and transfers that produced it."""

    ell: np.ndarray
    cl_mode: np.ndarray
    cl_covariant: np.ndarray
    k_com: np.ndarray

    @property
    def max_route_difference(self) -> float:
        """The numerical gap between two analytically identical routes.

        **What the two routes do not share is the only thing this measures.**
        They share the transfer function, the $k$ grid, the $\eta$ grid, the
        sources and the background; agreement carries no information whatever
        about any of those. What differs between them is the **harmonic weight
        algebra alone** --- (186) carries $\beta_\ell^2\alpha_\ell^2/(2\ell+1)^2$
        while (187) with (188) carries $\beta_\ell$ and
        $\Delta_\ell(2\ell+1)^{-1}$ --- so this number tests that those weights
        cancel as the exact rationals say they do, and nothing else.

        Finding **T-3** is the proof that the distinction is not pedantic: the
        routes agreed to $10^{-16}$ throughout, on an aliased integrand, while
        the spectrum was wrong by up to 575%. A shared input cannot be checked
        by a comparison that holds it fixed.
        """
        scale = np.max(np.abs(self.cl_mode))
        if scale == 0.0:
            return 0.0
        return float(np.max(np.abs(self.cl_mode - self.cl_covariant)) / scale)

    def d_ell(self) -> np.ndarray:
        return d_ell(self.ell, self.cl_mode)


def d_ell(ell: np.ndarray, cl: np.ndarray) -> np.ndarray:
    """D_l = l(l+1) C_l / 2pi, the quantity CMB spectra are plotted in."""
    ell = np.asarray(ell, dtype=float)
    return ell * (ell + 1.0) * np.asarray(cl, dtype=float) / (2.0 * pi)


def cl_mode_route(
    ell: int, k_com: np.ndarray, transfer: np.ndarray, power: np.ndarray
) -> float:
    """(186), with `transfer` = what (176) returns, i.e. alpha_l^{-1} tau_l.

    The prefactor $\\beta_\\ell^2\\alpha_\\ell^2/(2\\ell+1)^2$ is **1** identically,
    so it is written out rather than silently dropped: the identity is the point,
    and a reader checking this against the printed (186) must be able to see
    where it went.
    """
    k = np.asarray(k_com, dtype=float)
    prefactor = float(beta(ell)) ** 2 * float(alpha(ell)) ** 2 / (2 * ell + 1) ** 2
    integrand = k**2 * np.asarray(power, dtype=float) * np.asarray(transfer, dtype=float) ** 2
    return float(2.0 / pi * prefactor * np.trapezoid(integrand, k))


def multipole_mean_square(
    ell: int, k_com: np.ndarray, transfer: np.ndarray, power: np.ndarray
) -> float:
    """(187): <tau_Al tau^Al> = beta_l/(2 pi^2) Int k^2 dk |tau_l|^2.

    Written in terms of $\\tau_\\ell=\\alpha_\\ell T_\\ell$, so the $\\alpha_\\ell^2$
    is explicit. This is the **covariant** quantity, which holds for general
    geometries where the mode mean-square does not.
    """
    k = np.asarray(k_com, dtype=float)
    integrand = (
        k**2
        * np.asarray(power, dtype=float)
        * (float(alpha(ell)) * np.asarray(transfer, dtype=float)) ** 2
    )
    return float(float(beta(ell)) / (2.0 * pi**2) * np.trapezoid(integrand, k))


def cl_covariant_route(
    ell: int, k_com: np.ndarray, transfer: np.ndarray, power: np.ndarray
) -> float:
    """(188): C_l = Delta_l (2l+1)^{-1} <tau_Al tau^Al>, Delta_l = 4 pi beta_l/(2l+1).

    `delta_over_four_pi` carries $\\Delta_\\ell/(4\\pi)$ as an exact rational --- it
    is **not** $\\Delta_\\ell/\\pi$, and reading the name as though it were is a
    factor of four straight into the released spectrum. The $4\\pi$ is restored
    here and nowhere else.

    That misreading happened. The function was originally named `delta_over_pi`
    while its body and docstring both said $\\Delta_\\ell/(4\\pi)$, and this
    module read the name rather than the docstring. **The two-route comparison
    caught it** --- the mode route was four times the covariant one --- which is
    the whole reason both routes are computed rather than one.
    """
    mean_square = multipole_mean_square(ell, k_com, transfer, power)
    delta_l = 4.0 * pi * float(delta_over_four_pi(ell))
    return float(delta_l / (2 * ell + 1) * mean_square)


def angular_spectrum(
    ells: np.ndarray,
    k_com: np.ndarray,
    transfer: np.ndarray,
    power: np.ndarray,
) -> AngularSpectrum:
    """Both routes over a range of l. `transfer` has shape (len(ells), len(k_com))."""
    ells = np.asarray(ells, dtype=int)
    transfer = np.asarray(transfer, dtype=float)
    if transfer.shape != (ells.size, np.asarray(k_com).size):
        raise ValueError(
            f"transfer must be (len(ells), len(k_com)) = "
            f"{(ells.size, np.asarray(k_com).size)}, got {transfer.shape}"
        )
    mode = np.array([cl_mode_route(int(l), k_com, transfer[i], power)
                     for i, l in enumerate(ells)])
    cov = np.array([cl_covariant_route(int(l), k_com, transfer[i], power)
                    for i, l in enumerate(ells)])
    return AngularSpectrum(
        ell=ells, cl_mode=mode, cl_covariant=cov, k_com=np.asarray(k_com, dtype=float)
    )
