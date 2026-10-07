"""The temperature sources and the integral solution, Annals II §7.1.1.

**Published equation numbers, now confirmed rather than assumed.** The forms
below were checked character by character against the accepted Annals of Physics
manuscript source, whose labels `temp-anisotropy`, `primary`, `doppler` and
`secondary` generate exactly (176), (177), (178) and (179). See
`provenance/EQUATION-NUMBERS-ANNALS-II-v1.md`.

    (177)  S_P(eta,k)    = D(eta_0,k) [ (dT + Phi_A) + kappa' v_B ]

    (178)  S_DISW(eta,k) = V exp[-(k/k_D)^2] [ (1/3) k tau_1 + (kappa' v_B' + kappa'' v_B) ]

    (179)  S_ISW(eta,k)  = V exp[-(k/k_D)^2] [ (Phi_A' - Phi_H')(k,eta)
                                               - aH [ dT + 3 Phi_A ](k,eta) ]

    (176)  beta_l tau_l(eta_0) / (2l+1)
             ~= S_P(k,eta_*) j_l(k dEta_*)
                + Int_{eta_*}^{eta_0} d(eta) [ S_DISW + S_ISW ] j_l(k dEta)

**What (176) actually delivers.** Its left-hand side is
$\\beta_\\ell\\tau_\\ell/(2\\ell+1)$, and $\\alpha_\\ell = (2\\ell+1)/\\beta_\\ell$,
so (176) returns $\\alpha_\\ell^{-1}\\tau_\\ell$ --- precisely the normalisation in
which Appendix F's free-streaming solution is the *bare* spherical Bessel
function. That is not a coincidence and it is not decoration: it means the
integral solution and the hierarchy solved in `functions.harmonics` are
statements about the same object, and they can be made to check each other. An
impulsive source at $\\eta_*$ and no integrated terms must give exactly
$j_\\ell(k\\Delta\\eta_*)$, which is `free_stream`'s result in the $\\alpha$
normalisation. `tests/test_sources.py` asserts it. A normalisation slip anywhere
in either half breaks that identity, which is why it is worth having.

**The three terms are frame-dependent; their sum is not.** $\\delta T$, $\\Phi_A$,
$v_B$ and $\\tau_1$ all shift under a change of threading $u^a$, and the split of
(176) into primary, Doppler and integrated pieces shifts with them. Only the
total is an observable. The module therefore returns the three terms separately
*and* their combination, and never lets a caller plot one alone without saying
which frame it was computed in.

**Finding B-6, closed.** The thesis abstract carries the opposite sign on the
$aH[\\delta T+3\\Phi_A]$ term of (179). It is **settled in favour of the published
minus**, by the antecedent's own derivation at (106)--(111): $\\tilde{\\mathcal
B}_1=(k/a)(\\delta\\tilde T+\\Phi_A)$ at (106), so the $-a^2H\\tilde{\\mathcal B}_1$
term of (107) contributes $-aH(\\delta\\tilde T+\\Phi_A)$, and (107)'s separate
$-2Hak\\Phi_A$ supplies the rest: $1+2=3$. The sign is doubly sourced and cannot
flip by one slip. See the findings record.

`isw_sign` is **kept as a control, not as an open question** --- a known-wrong
alternative that must change the answer. That is a diagnostic, and it is why the
default is not simply hard-coded.

Nothing here manufactures a recombination history. $\\kappa'$, $\\kappa''$, the
visibility $V$ and the damping scale $k_D$ are supplied, because inventing them
inside the source terms would make the source terms untestable against an
analytic visibility. **Slow decoupling** --- (98), (102) and (111), with the
$C_0,C_1,C_2$ coefficients at (90) --- supplies them.

(Those numbers were previously cited in this bundle as "(180)-(182)", which is
wrong: (181) is the Sachs-Wolfe/acoustic result of \u00a77.1.2. Resolved against the
accepted manuscript; see `provenance/EQUATION-NUMBERS-ANNALS-II-v1.md`.)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.interpolate import CubicSpline

from functions.harmonics.weights import alpha
from functions.spectra.bessel_table import BesselTable

__all__ = [
    "PerturbationHistory",
    "ScatteringHistory",
    "source_primary",
    "source_doppler",
    "source_integrated",
    "temperature_transfer",
    "mode_multipole",
    "PUBLISHED_ISW_SIGN",
    "THESIS_ISW_SIGN",
]

# Finding B-6. The published paper and the arXiv preprint agree on -1; the thesis
# abstract reads +1. Carried, not resolved.
PUBLISHED_ISW_SIGN = -1.0
THESIS_ISW_SIGN = +1.0

#: A choice of threading $u^a$, made at the end and never at the start.
#:
#: * ``"generic"``  --- no specialisation. The default, and what the $1+3$
#:   approach buys over a gauge-fixed treatment.
#: * ``"newtonian"`` --- $\\tilde\\sigma_{ab}=0$, the specialisation Annals II
#:   itself makes at p. 365 to remove the shear terms.
#: * ``"energy"``    --- the **total-energy frame** $q_a=0$. This is the **CDM
#:   frame**: cold dark matter is pressureless and geodesic and carries no energy
#:   flux of its own, so the threading in which the CDM is at rest is the one in
#:   which the total energy flux vanishes.
#:
#: **"CDM" is not a frame name in this codebase**, because it is already a model
#: name --- `functions.background.CDM_MODEL`. Model and frame are independent:
#: the LCDM *model* is computed in the same *frame* as the CDM model, and
#: changing model is not changing frame. The two are kept lexically apart so a
#: call site cannot blur them.
Frame = Literal["generic", "newtonian", "energy"]


@dataclass(frozen=True)
class PerturbationHistory:
    """The perturbation variables of (177)-(179), sampled on a conformal-time grid.

    Every field is a function of conformal time at one comoving wavenumber. The
    frame is carried explicitly rather than assumed, because the split of (176)
    into three terms is frame-dependent even though the sum is not; a history
    that does not say which threading it was computed in cannot be plotted.
    """

    eta: np.ndarray
    delta_T: np.ndarray  # \tilde\delta_T, the covariant temperature perturbation
    phi_a: np.ndarray  # \Phi_A
    phi_h: np.ndarray  # \Phi_H
    tau_1: np.ndarray  # \tilde\tau_1, the dipole in the covariant normalisation
    v_b: np.ndarray  # \tilde v_B, the baryon velocity
    frame: Frame = "generic"

    def __post_init__(self) -> None:
        n = np.asarray(self.eta).size
        for name in ("delta_T", "phi_a", "phi_h", "tau_1", "v_b"):
            if np.asarray(getattr(self, name)).size != n:
                raise ValueError(f"{name} is not sampled on the same grid as eta")

    def derivative(self, name: str) -> np.ndarray:
        """d/d(eta) of a named field, by cubic spline. Primes in (178) and (179)."""
        values = np.asarray(getattr(self, name), dtype=float)
        return CubicSpline(np.asarray(self.eta, dtype=float), values).derivative()(self.eta)


@dataclass(frozen=True)
class ScatteringHistory:
    """Thomson scattering and diffusion, supplied rather than invented.

    `kappa_prime` is $\\kappa'=\\partial\\kappa/\\partial\\eta$, the differential
    optical depth; `visibility` is $V$; `damping_k` is the diffusion scale $k_D$;
    `damping_total` is $D(\\eta_0,k)$ of (177), as a callable in `k_com` so that an
    analytic test visibility can be supplied without a recombination solve.
    """

    eta: np.ndarray
    kappa_prime: np.ndarray
    visibility: np.ndarray
    damping_k: float = np.inf

    def kappa_double_prime(self) -> np.ndarray:
        return CubicSpline(
            np.asarray(self.eta, dtype=float),
            np.asarray(self.kappa_prime, dtype=float),
        ).derivative()(self.eta)

    def diffusion(self, k_com: float) -> float:
        """exp[-(k/k_D)^2], the factor (178) and (179) share."""
        if not np.isfinite(self.damping_k):
            return 1.0
        return float(np.exp(-((k_com / self.damping_k) ** 2)))


# ----------------------------------------------------------------------------
# The three sources
# ----------------------------------------------------------------------------


def source_primary(
    history: PerturbationHistory,
    scattering: ScatteringHistory,
    *,
    damping_total: float = 1.0,
) -> np.ndarray:
    """(177). D(eta_0,k) [ (dT + Phi_A) + kappa' v_B ].

    The ordinary Sachs-Wolfe combination $\\delta T+\\Phi_A$, plus the scattering
    term. `damping_total` is $D(\\eta_0,k)$, passed in because it is accumulated
    over the whole history and is not a property of the instant.
    """
    return damping_total * (
        (np.asarray(history.delta_T, dtype=float) + np.asarray(history.phi_a, dtype=float))
        + np.asarray(scattering.kappa_prime, dtype=float) * np.asarray(history.v_b, dtype=float)
    )


def source_doppler(
    history: PerturbationHistory,
    scattering: ScatteringHistory,
    k_com: float,
    *,
    weight: np.ndarray | None = None,
) -> np.ndarray:
    """(178). V exp[-(k/k_D)^2] [ (1/3) k tau_1 + (kappa' v_B)' ].

    The bracket's second pair is written as printed, $\\kappa'v_B'+\\kappa''v_B$,
    rather than contracted to $(\\kappa'v_B)'$: they are equal, and keeping the
    printed form means a transcription error shows up as a disagreement with the
    contracted form instead of hiding inside it. The test asserts the equality.

    `weight` is the weight the bracket carries, defaulting to the visibility
    $\\mathcal V$ as (178) prints it. Approximation **A-2** records why this
    bundle passes the opacity of (98) instead when computing a spectrum:
    $\\mathcal V\\kappa'\\sim\\kappa'^2e^{-\\kappa}$ is enormous, and with it the
    Sachs-Wolfe plateau does not exist.
    """
    v_b = np.asarray(history.v_b, dtype=float)
    kappa_prime = np.asarray(scattering.kappa_prime, dtype=float)
    bracket = (1.0 / 3.0) * k_com * np.asarray(history.tau_1, dtype=float) + (
        kappa_prime * history.derivative("v_b") + scattering.kappa_double_prime() * v_b
    )
    chosen = scattering.visibility if weight is None else np.asarray(weight, dtype=float)
    return np.asarray(chosen, dtype=float) * scattering.diffusion(k_com) * bracket


def source_integrated(
    history: PerturbationHistory,
    scattering: ScatteringHistory,
    k_com: float,
    *,
    aH: np.ndarray,
    isw_sign: float = PUBLISHED_ISW_SIGN,
    weight: np.ndarray | None = None,
) -> np.ndarray:
    """(179). W exp[-(k/k_D)^2] [ (Phi_A' - Phi_H') + s aH (dT + 3 Phi_A) ].

    `weight` is $W$: the weight the **gravitational** source carries. It
    defaults to the visibility $\\mathcal V$, which is what (179) prints, and
    `functions.spectra.decoupling.Weighting` supplies the opacity $e^{-\\kappa}$
    of (98) instead where a late integrated Sachs-Wolfe term is wanted. It is a
    parameter rather than something a caller divides back out afterwards, because
    a caller dividing by $\\mathcal V$ divides by zero wherever the visibility has
    fallen to nothing --- which is exactly the epoch the late ISW lives in.
    Approximation **A-1**.

    `isw_sign` is **finding B-6**: $s=-1$ is the published and arXiv reading,
    $s=+1$ the thesis abstract's. `aH` comes from `functions.background`, sampled
    on the same conformal-time grid, and is not recomputed here --- the background
    is one object with one definition, and (179) consumes it.
    """
    if isw_sign not in (PUBLISHED_ISW_SIGN, THESIS_ISW_SIGN):
        raise ValueError("isw_sign is a finding, not a free parameter: use -1.0 or +1.0")
    isw = history.derivative("phi_a") - history.derivative("phi_h")
    threading = np.asarray(aH, dtype=float) * (
        np.asarray(history.delta_T, dtype=float)
        + 3.0 * np.asarray(history.phi_a, dtype=float)
    )
    bracket = isw + isw_sign * threading
    chosen = scattering.visibility if weight is None else np.asarray(weight, dtype=float)
    return np.asarray(chosen, dtype=float) * scattering.diffusion(k_com) * bracket


# ----------------------------------------------------------------------------
# The integral solution
# ----------------------------------------------------------------------------


def temperature_transfer(
    ell: int,
    k_com: float,
    *,
    eta: np.ndarray,
    s_primary_at_star: float,
    s_integrated: np.ndarray,
    eta_0: float,
    eta_star: float,
    table: BesselTable | None = None,
) -> float:
    """(176), returning alpha_l^{-1} tau_l(eta_0) at one (l, k).

    The primary term is evaluated once, at $\\eta_*$; the integrated terms are
    carried along the line of sight. `table` is the tabulated $j_\\ell$ of route
    3 --- the hybrid --- and is built once per run rather than per mode.

    Returns $\\beta_\\ell\\tau_\\ell/(2\\ell+1)$, which is $\\tau_\\ell/\\alpha_\\ell$.
    `mode_multipole` converts to $\\tau_\\ell$ when that is what is wanted.
    """
    eta = np.asarray(eta, dtype=float)
    x = k_com * (eta_0 - eta)
    j = table(ell, x) if table is not None else _bessel(ell, x)

    primary = s_primary_at_star * (
        float(table(ell, k_com * (eta_0 - eta_star)))
        if table is not None
        else float(_bessel(ell, np.array([k_com * (eta_0 - eta_star)]))[0])
    )
    integrated = float(np.trapezoid(np.asarray(s_integrated, dtype=float) * j, eta))
    return primary + integrated


def mode_multipole(ell: int, transfer: float) -> float:
    """tau_l from (176)'s left-hand side: multiply by alpha_l."""
    return float(alpha(ell)) * transfer


def _bessel(ell: int, x: np.ndarray) -> np.ndarray:
    from scipy.special import spherical_jn

    return spherical_jn(int(ell), np.asarray(x, dtype=float))
