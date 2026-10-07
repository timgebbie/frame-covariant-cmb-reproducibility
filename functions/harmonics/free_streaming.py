"""Free streaming of the covariant temperature hierarchy, in three normalisations.

Annals II, Appendix F, pp. 379-380, writes one recursion three ways. This module
integrates each as printed and lets them be compared without any of them being
privileged, which is the acceptance spine of v1.0.0.

Published equation numbers throughout.

(F.1), proper time, with the COMOVING wavenumber (the equation carries an
explicit 1/a against a proper-time derivative):

    -tau_l^dot  =  (k_com/a) [ w_l tau_{l+1} - tau_{l-1} ],
    w_l = (l+1)^2 / [(2l+3)(2l+1)],   l >= 2.

(F.3), the same in conformal time, after multiplying through by beta_l:

    -(beta_l tau_l)'  =  k_com [ (l+1)/(2l+3) (beta_{l+1} tau_{l+1})
                                 - l/(2l-1) (beta_{l-1} tau_{l-1}) ].

(F.4), with beta_l = alpha_l^{-1}(2l+1). The display as printed keeps (2l+1) on
the left; the text preceding it specifies a division by (2l+1) which was not
applied, and only after that division is it the Ma & Bertschinger form. We divide.
See provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md, finding B-2.

    -(alpha_l^{-1} tau_l)'  =  (k_com/(2l+1)) [ (l+1)(alpha_{l+1}^{-1} tau_{l+1})
                                                - l (alpha_{l-1}^{-1} tau_{l-1}) ].

**Never a bare `k`.** `k_com` is comoving; `k_phys = k_com / a`. The project's
conventions sheet declares `k == k_phys` in its harmonic-recursion section while
Appendix F's `k` is comoving, and the two differ by a factor `a` in precisely
these equations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import spherical_jn

from .weights import alpha, beta

__all__ = ["Normalisation", "rescale", "free_stream", "analytic_projection"]

Normalisation = Literal["covariant", "beta", "alpha"]

#: Which published equation each normalisation is written in.
EQUATION = {
    "covariant": "(F.1)",
    "beta": "(F.3)",
    "alpha": "(F.4), after the division its text specifies — finding B-2",
}


def _scale(norm: Normalisation, ell: int) -> float:
    """Factor multiplying tau_l in this normalisation."""
    if norm == "covariant":
        return 1.0
    if norm == "beta":
        return float(beta(ell))
    if norm == "alpha":
        return 1.0 / float(alpha(ell))
    raise ValueError(f"unknown normalisation {norm!r}")


def rescale(values: np.ndarray, frm: Normalisation, to: Normalisation) -> np.ndarray:
    """Map a hierarchy between normalisations, exactly."""
    out = np.array(values, dtype=float, copy=True)
    for ell in range(out.shape[-1]):
        out[..., ell] *= _scale(to, ell) / _scale(frm, ell)
    return out


@dataclass(frozen=True)
class Solution:
    normalisation: Normalisation
    equation: str
    eta: np.ndarray
    values: np.ndarray  # (len(eta), ell_max + 1), in `normalisation`
    ell_max: int
    k_com: float

    def covariant(self) -> np.ndarray:
        """The same solution expressed in tau_l, whatever it was integrated in."""
        return rescale(self.values, self.normalisation, "covariant")


def _rhs(norm: Normalisation, ell_max: int, k_com: float, sign_control: bool):
    """d/d(eta) of the hierarchy, in `norm`.

    `sign_control` flips the relative sign of the two couplings. That is the
    lambda^2 = -1 case of the harmonic phase question: it is not a different
    physical model, it is the same recursion written in the other candidate
    normalisation, and it must fail to reproduce the external form.
    """
    s = np.array([_scale(norm, ell) for ell in range(ell_max + 2)], dtype=float)
    rel = -1.0 if sign_control else 1.0

    def rhs(_eta: float, y: np.ndarray) -> np.ndarray:
        tau = np.zeros(ell_max + 2)
        tau[: ell_max + 1] = y / s[: ell_max + 1]  # back to covariant tau_l
        d = np.zeros(ell_max + 1)
        # l = 0: the monopole feeds the dipole only. From (F.1) continued to l = 0,
        # tau_0^dot = -(k/a) w_0 tau_1 with w_0 = 1/3.
        d[0] = -k_com * (1.0 / 3.0) * tau[1]
        for ell in range(1, ell_max + 1):
            w = (ell + 1) ** 2 / ((2 * ell + 3) * (2 * ell + 1))
            d[ell] = -k_com * (w * tau[ell + 1] + rel * (-1.0) * tau[ell - 1])
        return d * s[: ell_max + 1]

    return rhs


def free_stream(
    k_com: float,
    eta: np.ndarray,
    *,
    ell_max: int = 60,
    normalisation: Normalisation = "covariant",
    initial: np.ndarray | None = None,
    sign_control: bool = False,
) -> Solution:
    """Integrate free streaming from eta[0] to eta[-1].

    Default initial data is a pure monopole, tau_0 = 1, which is the clean case:
    its free-streaming projection is known analytically.
    """
    if initial is None:
        initial = np.zeros(ell_max + 1)
        initial[0] = 1.0
    y0 = rescale(np.asarray(initial, dtype=float), "covariant", normalisation)
    sol = solve_ivp(
        _rhs(normalisation, ell_max, k_com, sign_control),
        (float(eta[0]), float(eta[-1])),
        y0,
        t_eval=np.asarray(eta, dtype=float),
        rtol=1e-10,
        atol=1e-12,
        method="DOP853",
    )
    if not sol.success:
        raise RuntimeError(f"free streaming did not integrate: {sol.message}")
    return Solution(
        normalisation=normalisation,
        equation=EQUATION[normalisation],
        eta=np.asarray(eta, dtype=float),
        values=sol.y.T,
        ell_max=ell_max,
        k_com=k_com,
    )


def analytic_projection(k_com: float, eta: np.ndarray, eta_i: float, ell: int) -> np.ndarray:
    """The free-streaming projection of a unit monopole onto multipole `ell`.

    Appendix F, p. 380: "The solution to the mode coefficients with respect to the
    time-like integration in the flat (K=0) almost-Friedmann-Lemaitre case are
    spherical Bessel functions." A monopole at eta_i projects onto
    j_ell(k_com (eta - eta_i)); the normalisation per multipole is fixed by the
    recursion and is checked, not assumed, in tests.
    """
    return spherical_jn(ell, k_com * (np.asarray(eta, dtype=float) - eta_i))
