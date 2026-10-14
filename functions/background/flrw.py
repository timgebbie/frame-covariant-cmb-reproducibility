"""The background expansion, from the 1+3 covariant constraint.

**Derived here, not transcribed.** The brief is a reconstruction from first $1+3$
principles, so the background is obtained from the covariant energy constraint
rather than copied from a printed expansion law. Annals II's own expansion law,
Eq. (185), is then a *check* on this module and not its source --- which is the
right order for an independent reconstruction, and the only order in which the
printed law can be audited at all.

**The constraint.** For an irrotational, shear-free congruence $u^a$ with
expansion $\\Theta = 3H$, the $1+3$ energy constraint (the Friedmann equation in
covariant form) is

    (1/3) Theta^2 = mu + Lambda - (1/2) R3,

with $\\mu$ the total energy density and ${}^3R$ the spatial curvature scalar.
Writing $\\Theta = 3\\dot a/a$ in proper time, splitting $\\mu$ into radiation,
matter and curvature contributions scaling as $a^{-4}$, $a^{-3}$ and $a^{-2}$,
and normalising at $a_0 = 1$,

    (a'/a)^2 = H0^2 [ Om_r a^-2 + Om_m a^-1 + Om_k + Om_L a^2 ],        (aH)

where a prime is $d/d\\eta$ and $\\eta$ is conformal time. The quantity on the
left is $aH$, which is exactly the combination Annals II (179) carries.

**Integration.** $\\eta(a)=\\int_0^a da'/(a'^2 H)$ has an integrable singularity
at the origin when $\\Omega_r = 0$. The substitution $a = u^2$ removes it:

    d(eta)/du = 2u / ( H0 sqrt( Om_r + Om_m u^2 + Om_k u^4 + Om_L u^8 ) ),

which is regular at $u=0$ for both a radiation-led and a matter-led start. One
substitution therefore serves CDM and $\\Lambda$CDM alike, which matters because
v1.0.0 must deliver both.

Units: $H_0 = 1$ by default, so conformal times and distances are in $1/H_0$ and
the EdS value $\\eta_0 = 2$ is immediate.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import math

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import CubicSpline

__all__ = ["Background", "eds_scale_factor"]


def eds_scale_factor(eta: np.ndarray | float, *, h0: float = 1.0) -> np.ndarray:
    """The closed-form Einstein-de Sitter solution, a = (H0 eta / 2)^2.

    Kept as an independent arbiter for the integrated background: the numerical
    route must reproduce it when Om_m = 1, and the test says so.
    """
    return (h0 * np.asarray(eta, dtype=float) / 2.0) ** 2


@dataclass(frozen=True)
class Background:
    """A spatially flat or curved FLRW background in conformal time.

    Parameters are density parameters today. `omega_k` is derived, never supplied,
    so a closed model cannot be built by accident.
    """

    omega_m: float = 1.0
    omega_lambda: float = 0.0
    omega_r: float = 0.0
    h0: float = 1.0
    n_panels: int = 400

    # ---- the constraint itself -------------------------------------------

    @property
    def omega_k(self) -> float:
        """Curvature, derived from the constraint. Zero for a flat model."""
        return 1.0 - self.omega_m - self.omega_lambda - self.omega_r

    def conformal_hubble(self, a: np.ndarray | float) -> np.ndarray:
        """aH = a'/a, the combination (179) carries. Equation (aH) above."""
        a = np.asarray(a, dtype=float)
        return self.h0 * np.sqrt(
            self.omega_r / a**2
            + self.omega_m / a
            + self.omega_k
            + self.omega_lambda * a**2
        )

    # ---- eta(a) and its inverse ------------------------------------------

    def _integrand(self, u: np.ndarray | float) -> np.ndarray:
        """d(eta)/du, written so that it is manifestly regular at u = 0.

        Two branches, because the cancellation that makes the origin regular is
        different in each and writing one expression for both leaves a 0/0 there:

        * $\\Omega_r>0$: the numerator vanishes and the denominator does not, so
          the integrand tends to zero.
        * $\\Omega_r=0$: one factor of $u$ cancels between numerator and
          denominator, leaving $2/(H_0\\sqrt{\\Omega_m+\\dots})$, a non-zero
          constant. Masking the origin instead of cancelling it loses exactly one
          grid interval of area --- small, systematic, and wrong.
        """
        u = np.asarray(u, dtype=float)
        if self.omega_r > 0.0:
            return 2.0 * u / (
                self.h0
                * np.sqrt(
                    self.omega_r
                    + self.omega_m * u**2
                    + self.omega_k * u**4
                    + self.omega_lambda * u**8
                )
            )
        return 2.0 / (
            self.h0
            * np.sqrt(self.omega_m + self.omega_k * u**2 + self.omega_lambda * u**6)
        )

    @cached_property
    def _eta_of_u(self) -> tuple[np.ndarray, np.ndarray]:
        """Conformal time on a grid in u = sqrt(a), integrated from u = 0.

        Integrated panel by panel with adaptive quadrature rather than by a
        trapezoid sweep. A radiation-led start puts a transition at
        $u\\simeq\\sqrt{\\Omega_r/\\Omega_m}$ that a uniform trapezoid grid resolves
        only by accident; adaptive panels resolve it by construction.
        """
        if self.omega_r <= 0.0 and self.omega_m <= 0.0:
            raise ValueError(
                "a background with neither radiation nor matter has no "
                "Friedmann-Lemaitre origin to integrate from"
            )
        u = np.linspace(0.0, 1.0, self.n_panels + 1)
        panels = np.array(
            [quad(self._integrand, u[i], u[i + 1], limit=100)[0] for i in range(self.n_panels)]
        )
        eta = np.concatenate(([0.0], np.cumsum(panels)))
        return u, eta

    @cached_property
    def eta_of_a(self) -> CubicSpline:
        u, eta = self._eta_of_u
        return CubicSpline(u**2, eta, extrapolate=True)

    @cached_property
    def a_of_eta(self) -> CubicSpline:
        u, eta = self._eta_of_u
        return CubicSpline(eta, u**2, extrapolate=True)

    @property
    def eta_0(self) -> float:
        """Conformal time today, a = 1."""
        return float(self._eta_of_u[1][-1])

    def eta_at_redshift(self, z: float) -> float:
        return float(self.eta_of_a(1.0 / (1.0 + z)))

    def conformal_distance(self, z: float) -> float:
        """Delta(eta) = eta_0 - eta(z), the argument of j_l in (176)."""
        return self.eta_0 - self.eta_at_redshift(z)

    def aH_of_eta(self, eta: np.ndarray | float) -> np.ndarray:
        """aH sampled on a conformal-time grid, as (179) needs it."""
        return self.conformal_hubble(self.a_of_eta(np.asarray(eta, dtype=float)))


# ---------------------------------------------------------------------------
# Named MODELS.
#
# **"CDM" names two different things and this codebase keeps them apart.**
# Here it is a *model*: a cosmology. The *CDM frame* is something else entirely
# --- a choice of frame u^a, namely A_a = 0, the frame in which the cold dark
# matter is at rest, because CDM is pressureless and collisionless and so moves
# on geodesics. That is exact in GR, not a limit. Frames live in
# `functions.spectra.sources.Frame`, not here, and the LCDM model is computed in
# the same frame as the CDM model. Changing model is not changing frame.
#
# The suffix is deliberate and is not to be dropped: a bare `CDM` at a call site
# cannot be read unambiguously, and this distinction has already had to be made
# once in conversation.
#
# Annals II section 8.3.2 is standard CDM: h = 0.5, Omega_B = 0.05, flat and
# matter dominated. LCDM is not treated in Annals II at all; it is delivered in
# v1.0.0 regardless, because the marginal cost over the CDM case is the expansion
# law and the late-time integrated term and nothing else.
CDM_MODEL = Background(omega_m=1.0, omega_lambda=0.0, omega_r=0.0, h0=1.0)
LCDM_MODEL = Background(omega_m=0.3, omega_lambda=0.7, omega_r=0.0, h0=1.0)


# ---------------------------------------------------------------------------
# The comparison model --- criterion 5b only.
# ---------------------------------------------------------------------------

#: Photon energy density today, as $\Omega_\gamma h^2$, **derived from $T_{CMB}$
#: and the physical constants rather than quoted.**
#:
#: $\rho_\gamma = 4\sigma_{SB}T_0^4/c^3$ against
#: $\rho_{crit}h^{-2} = 3H_{100}^2/8\pi G$. Deriving it rather than pasting
#: $2.47\times10^{-5}$ is what makes the agreement with CAMB a *check*: an
#: independent route to $z_{eq}$ that either lands on theirs or does not.
#: It lands on 5756.0 against CAMB's 5756.0.
def _omega_gamma_h2(t_cmb_k: float = 2.7255) -> float:
    sigma_sb, c, g_newton = 5.670374419e-8, 2.99792458e8, 6.67430e-11
    mpc_m = 3.0856775814913673e22
    rho_gamma = 4.0 * sigma_sb * t_cmb_k**4 / c**3
    h100 = 100.0e3 / mpc_m
    return float(rho_gamma / (3.0 * h100**2 / (8.0 * math.pi * g_newton)))


OMEGA_GAMMA_H2 = _omega_gamma_h2()

#: **The stamped Planck 2018 VI column, with a radiation era, for criterion 5b
#: and nothing else.**
#:
#: `CDM_MODEL` and `LCDM_MODEL` both carry $\Omega_r=0$: *Annals II*'s \S8.3.2
#: standard CDM is Einstein--de Sitter, and this bundle's $\Lambda$CDM extension
#: kept the same matter-only background. A matter-only background **has no
#: equality**, so it has no $z_{eq}$, no radiation-driven decay of the potential
#: and a sound horizon belonging to a different cosmology from anything CAMB or
#: CLASS will produce. Comparing acoustic peak positions from such a background
#: against an external code measures the missing radiation era and reads as a
#: failure of the reconstruction. That is **finding T-37**.
#:
#: This third constant exists so that 5b has a like-for-like cosmology **without
#: moving a single released number**: `CDM_MODEL` and `LCDM_MODEL` are untouched,
#: and nothing outside the 5b path refers to this one.
#:
#: **Photons only, $N_{eff}=0$,** and that is a deliberate specialisation rather
#: than an omission. This bundle's hierarchy has one radiation species. Adding
#: three massless neutrinos to the background would change the expansion without
#: adding anything to the driving, which is the same error as comparing a
#: quantity across two frames. The external codes are specialised to match:
#: CAMB `nnu=0`, CLASS `N_ur=0` with `YHe` given explicitly, because its
#: BBN interpolation does not cover $N_{eff}=0$. Both then report
#: $z_{eq}=5756.0$ and a first acoustic peak at $\ell=206$.
PLANCK_OMEGA_B_H2 = 0.02237
PLANCK_OMEGA_C_H2 = 0.1200
PLANCK_H = 0.6736
PLANCK_N_S = 0.9649
PLANCK_A_S = 2.1e-9
PLANCK_Y_HE = 0.245

_PLANCK_OM = (PLANCK_OMEGA_B_H2 + PLANCK_OMEGA_C_H2) / PLANCK_H**2
_PLANCK_OR = OMEGA_GAMMA_H2 / PLANCK_H**2

PLANCK_MODEL = Background(
    omega_m=_PLANCK_OM,
    omega_lambda=1.0 - _PLANCK_OM - _PLANCK_OR,
    omega_r=_PLANCK_OR,
    h0=1.0,
)
