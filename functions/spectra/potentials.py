"""The gravitational potentials that drive the acoustic system.

`functions.spectra.acoustic` and `functions.spectra.sources` both take
$\\Phi_A$ and $\\Phi_H$ as *supplied* histories rather than solving for them.
This module supplies them, and it does so from the background --- derived, not
transcribed, for the same reason `functions.background` is.

**The growth equation.** For sub-horizon matter perturbations in conformal time,

    delta'' + aH delta' - (3/2) Om_m H0^2 delta / a = 0,

whose Einstein--de Sitter solutions are $\\delta\\propto\\eta^2\\propto a$ (growing)
and $\\eta^{-3}$ (decaying). The potential follows from the Poisson equation,
$k^2\\Phi\\propto\\delta/a$, so

    Phi(a)  proportional to  D(a)/a.

**Why this is the piece that makes $\\Lambda$CDM different.** In Einstein--de
Sitter $D\\propto a$ exactly, so $\\Phi$ is **constant** and
$\\Phi_A'-\\Phi_H'$ vanishes identically --- there is no integrated Sachs--Wolfe
term at all, which is why *Annals II*'s standard-CDM model never needed one.
Once $\\Lambda$ dominates, growth stalls while $a$ keeps increasing, $D/a$ falls,
and $\\Phi$ decays. That decay **is** the late integrated Sachs--Wolfe effect.

So the late ISW is not bolted on for $\\Lambda$CDM: it appears by itself, from
the same growth equation, the moment $\\Omega_\\Lambda\\neq0$. It is then carried
to the observer by the integrated source --- which must be weighted by the
opacity and not the visibility, or it is deleted again. See
`provenance/SOURCE-APPROXIMATIONS-v1.md`, approximation A-1.

**Normalisation.** $\\Phi$ is returned normalised to 1 deep in matter domination,
so the primordial amplitude lives in $P(k)$ and nowhere else. Two places setting
one amplitude is how a factor goes missing.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

from functions.background.flrw import Background

__all__ = ["growth_factor", "potentials", "potential_derivative"]


def growth_factor(background: Background, eta: np.ndarray) -> np.ndarray:
    """D(eta), the growing mode, normalised to D = a deep in matter domination.

    Integrated rather than taken from a fitting formula, so that the Einstein--de
    Sitter limit $D=a$ is a *result* and can be asserted as one.
    """
    eta = np.asarray(eta, dtype=float)
    a_of = background.a_of_eta
    aH_of = background.aH_of_eta
    three_halves_om = 1.5 * background.omega_m * background.h0**2

    def rhs(t: float, y: np.ndarray) -> list[float]:
        delta, delta_prime = y
        a = max(float(a_of(t)), 1e-12)
        return [delta_prime, -float(aH_of(t)) * delta_prime + three_halves_om * delta / a]

    # start deep in matter domination on the growing mode: D = a, D' = a'
    eta_i = eta[0]
    a_i = float(a_of(eta_i))
    a_prime_i = a_i * float(aH_of(eta_i))

    solution = solve_ivp(
        rhs, (eta_i, eta[-1]), [a_i, a_prime_i], t_eval=eta,
        method="DOP853", rtol=1e-10, atol=1e-14,
    )
    if not solution.success:
        raise RuntimeError(f"growth integration failed: {solution.message}")
    return solution.y[0]


def potentials(
    background: Background, eta: np.ndarray, *, amplitude: float = 1.0
) -> tuple[np.ndarray, np.ndarray]:
    """(Phi_A, Phi_H) on the conformal-time grid, normalised to `amplitude` early.

    $\\Phi\\propto D/a$, normalised to `amplitude` at the first grid point, which
    is taken to be deep in matter domination. $\\Phi_H=-\\Phi_A$ in the absence of
    anisotropic stress, which is the case at the order v1.0.0 works to; the two
    are returned separately regardless, because (179) carries
    $\\Phi_A'-\\Phi_H'$ and collapsing them here would hide a sign.
    """
    eta = np.asarray(eta, dtype=float)
    d = growth_factor(background, eta)
    a = background.a_of_eta(eta)
    phi = d / a
    phi_a = amplitude * phi / phi[0]
    return phi_a, -phi_a


def potential_derivative(eta: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """d(Phi)/d(eta) by spline --- the quantity (179)'s ISW proper is built from."""
    return CubicSpline(np.asarray(eta, dtype=float), np.asarray(phi, dtype=float)).derivative()(eta)
