"""The external free-streaming hierarchies, implemented exactly as printed.

Each function below is transcribed from the source paper itself, not through
Annals II Appendix F. That distinction is the point: a coefficient read through
Appendix F would be the same source as Appendix F, and this bundle counts
independent checks by their sources rather than by their arguments.

Read from source, 2026-10-05:

  **HS** Hu & Sugiyama, *Phys. Rev. D* **51** (1995), 2599, **Eq. (6)**, p. 2601
         (Annals II reference [40]):

             Theta_l^dot = k [ l/(2l-1) Theta_{l-1}
                               - (l+1)/(2l+3) (1 - l(l+2) K/k^2) Theta_{l+1} ]
                           - tau^dot Theta_l,   l > 2.

         Weights l/(2l-1) and (l+1)/(2l+3): this is the BETA normalisation, and
         therefore Annals II (F.3).

  **MB** Ma & Bertschinger, *Astrophys. J.* **455** (1995), 7, **Eqs. (49)** and
         **(50)**, synchronous and conformal Newtonian gauge respectively
         (Annals II reference [56]):

             F_{nu l}^dot = k/(2l+1) [ l F_{nu (l-1)} - (l+1) F_{nu (l+1)} ].

  **WI** M. L. Wilson, *Astrophys. J.* **273**, 2 (1983), **Eq. (8)**, p. 4
         (Annals II reference [W83]), read from the scanned paper:

             l > 2,  delta_l^dot = -n_e sigma_T delta_l
                       - i k T { l/(2l-1) delta_{l-1}
                                 + (l+1)/(2l+3) [1 - l(l+2) K/k^2] delta_{l+1} }.

         Weights l/(2l-1) and (l+1)/(2l+3): the BETA normalisation, as in HS.
         **But the two bracket terms carry the SAME sign, under an overall -i.**
         Wilson's delta_l differs from a real-coefficient Theta_l by a phase:
         Theta_l = i^l delta_l turns the same-sign imaginary form into the
         opposite-sign real form of Hu & Sugiyama, exactly. That makes Wilson a
         check on the phase convention and not only on the l-weights, which is
         what finding B-1 and acceptance criterion 3 are about.

         **Annals II cites "eqn 7" for this.** Wilson's (7) is the l = 2
         equation, which carries 9/10 n_e sigma_T, -4/3 Hdot and the factors
         2/5 and 3/7 (1 - 8K/k^2); the l > 2 hierarchy is his **(8)**. Finding
         B-9.

  **SZ** Seljak & Zaldarriaga, *Astrophys. J.* **469** (1996), 437, **Eq. (3d)**
         (Annals II reference [69]):

             Delta_{Tl}^dot = k/(2l+1) [ l Delta_{T(l-1)} - (l+1) Delta_{T(l+1)} ]
                              - kappa^dot Delta_{Tl},   l > 2.

         MB and SZ carry weights l/(2l+1) and (l+1)/(2l+1): the ALPHA
         normalisation, and therefore Annals II (F.4).

**Scattering terms are dropped.** `-tau^dot Theta_l` and `-kappa^dot Delta_{Tl}`
are Thomson scattering, not free streaming; v1.0.0 compares the free-streaming
recursion only.

**Editions.** MB's arXiv copy numbers its hierarchy (49) and (50), which are the
same numbers Annals II cites from the published paper; no offset here. HS's
equation number (6) is from the published Physical Review D article. Both are
recorded because this project has been bitten by assuming editions agree.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
from scipy.integrate import solve_ivp

__all__ = ["Form", "WEIGHTS", "integrate_external"]

Form = Literal["HS", "MB", "SZ"]

#: (lower weight, upper weight) as printed, as functions of l. K = 0 throughout.
WEIGHTS = {
    "HS": (lambda l: l / (2 * l - 1), lambda l: (l + 1) / (2 * l + 3)),
    "MB": (lambda l: l / (2 * l + 1), lambda l: (l + 1) / (2 * l + 1)),
    "SZ": (lambda l: l / (2 * l + 1), lambda l: (l + 1) / (2 * l + 1)),
}

#: Wilson's weights are HS's, but his equation is written in the imaginary
#: convention with both bracket terms positive under an overall -i.
WILSON_WEIGHTS = (lambda l: l / (2 * l - 1), lambda l: (l + 1) / (2 * l + 3))

CITATION = {
    "HS": "Hu & Sugiyama, Phys. Rev. D 51 (1995), 2599, Eq. (6)",
    "MB": "Ma & Bertschinger, Astrophys. J. 455 (1995), 7, Eqs. (49), (50)",
    "SZ": "Seljak & Zaldarriaga, Astrophys. J. 469 (1996), 437, Eq. (3d)",
    "WI": "M. L. Wilson, Astrophys. J. 273 (1983), 2, Eq. (8)",
}

#: Which Annals II Appendix F equation each external form corresponds to.
APPENDIX_F = {"HS": "(F.3)", "MB": "(F.4)", "SZ": "(F.4)", "WI": "(F.3)"}


def integrate_external(
    form: Form,
    k_com: float,
    eta: np.ndarray,
    *,
    ell_max: int = 60,
    initial: np.ndarray | None = None,
) -> np.ndarray:
    """Integrate the external hierarchy `form` as printed, from a unit monopole.

    Returns an array of shape (len(eta), ell_max + 1).

    The l = 0 and l = 1 equations of each source carry metric and fluid source
    terms that are not free streaming. For a pure free-streaming comparison the
    same recursion is continued down to l = 0, which is what every one of these
    hierarchies reduces to when its sources are switched off.
    """
    lower, upper = WEIGHTS[form]
    if initial is None:
        initial = np.zeros(ell_max + 1)
        initial[0] = 1.0

    def rhs(_eta: float, y: np.ndarray) -> np.ndarray:
        padded = np.concatenate([y, [0.0]])
        d = np.empty(ell_max + 1)
        d[0] = -k_com * upper(0) * padded[1]
        for ell in range(1, ell_max + 1):
            d[ell] = k_com * (lower(ell) * padded[ell - 1] - upper(ell) * padded[ell + 1])
        return d

    sol = solve_ivp(
        rhs,
        (float(eta[0]), float(eta[-1])),
        np.asarray(initial, dtype=float),
        t_eval=np.asarray(eta, dtype=float),
        rtol=1e-10,
        atol=1e-12,
        method="DOP853",
    )
    if not sol.success:
        raise RuntimeError(f"{form} did not integrate: {sol.message}")
    return sol.y.T


def integrate_wilson(
    k_com: float,
    eta: np.ndarray,
    *,
    ell_max: int = 60,
    initial: np.ndarray | None = None,
) -> np.ndarray:
    """Wilson Eq. (8) in his own imaginary convention, returned as Theta_l = i^l delta_l.

    Integrated as printed --- complex, with both bracket terms positive under an
    overall $-ik$ --- and only then transformed. Transforming the *equation*
    first and integrating the real form would be assuming the identity this is
    meant to test.

    At $K=0$ the curvature factor $[1-\\ell(\\ell+2)K/k^2]$ is unity, which is the
    case this bundle compares in.
    """
    lower, upper = WILSON_WEIGHTS
    if initial is None:
        initial = np.zeros(ell_max + 1, dtype=complex)
        initial[0] = 1.0

    def rhs(_eta: float, y: np.ndarray) -> np.ndarray:
        padded = np.concatenate([y, [0.0 + 0.0j]])
        d = np.empty(ell_max + 1, dtype=complex)
        # l = 0 continues the same recursion downwards, as for the other sources
        d[0] = -1j * k_com * (upper(0) * padded[1])
        for ell in range(1, ell_max + 1):
            d[ell] = -1j * k_com * (
                lower(ell) * padded[ell - 1] + upper(ell) * padded[ell + 1]
            )
        return d

    sol = solve_ivp(
        rhs,
        (float(eta[0]), float(eta[-1])),
        np.asarray(initial, dtype=complex),
        t_eval=np.asarray(eta, dtype=float),
        rtol=1e-10,
        atol=1e-12,
        method="DOP853",
    )
    if not sol.success:
        raise RuntimeError(f"Wilson did not integrate: {sol.message}")

    # Theta_l = i^l delta_l turns the same-sign imaginary form into the
    # opposite-sign real form. The result must be real to machine precision;
    # that it is, is the content of the check.
    phase = 1j ** np.arange(ell_max + 1)
    return (sol.y.T * phase).real


__all__ = __all__ + ["integrate_wilson", "WILSON_WEIGHTS"]
