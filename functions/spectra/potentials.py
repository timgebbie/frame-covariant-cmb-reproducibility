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


#: Samples on `potentials`' internal growth grid. Logarithmic, because it spans
#: from the acoustic start to today --- up to nine decades. `index` in the grid
#: register: it carries no physical scale of its own, it resamples a quantity
#: whose scale is set elsewhere, and the convergence stated there is that
#: $\Phi_A(\eta_*)$ agrees to nine figures between 4096 and 16384.
GROWTH_SAMPLES = 8192


def matter_domination_eta(background: Background, *, ratio: float = 1.0) -> float:
    r"""The $\eta$ at which $\rho_M/\rho_R=$ `ratio`, or 0 when there is no radiation.

    **Derived, with the ratio stated.** `CDM_MODEL` and `LCDM_MODEL` carry
    $\Omega_r=0$, so they are matter-dominated at every $\eta$ and this returns
    0: *Annals II*'s Appendix G is **exactly** right for them, and the acoustic
    start below is then no approximation at all.

    **The default is equality itself, and that is forced rather than chosen.**
    `PLANCK_MODEL` has $a_{\rm eq}=\Omega_r/\Omega_m=1.737\times10^{-4}$
    ($z_{\rm eq}=5756$) against $a_*=8.963\times10^{-4}$ ($z_*=1115$), so

        rho_M / rho_R at last scattering = a_* / a_eq = 5.16

    The real universe is **only marginally matter-dominated where the acoustic
    physics happens**. A reference at $\rho_M/\rho_R=9$ lands at
    $\eta=1.46\,\eta_*$ --- *after* last scattering, so there is no $\eta$
    before recombination at which matter domination holds in that strong a
    sense. The honest boundary is equality, and the residual marginality is
    approximation **A-3**, stated rather than hidden in a factor.
    """
    omega_r = float(background.omega_r)
    if omega_r <= 0.0:
        return 0.0
    a_target = ratio * omega_r / float(background.omega_m)
    lo, hi = 1e-12, float(background.eta_0)
    for _ in range(200):                      # bisection: a(eta) is monotone
        mid = 0.5 * (lo + hi)
        if float(background.a_of_eta(mid)) < a_target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def potentials(
    background: Background, eta: np.ndarray, *, amplitude: float = 1.0,
    constant_below: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    r"""$(\Phi_A,\Phi_H)$ on the conformal-time grid, normalised to `amplitude` early.

    $\Phi\propto D/a$ --- *Annals II* Appendix G, which derives it **for matter
    domination** and closes with *"a $\Phi_A(k,0) = (D/a)\,\Phi_A(k,t)$ where
    $D$ is the linear growth factor. The flat dust case is recovered using
    $D=a$."* $\Phi_H=-\Phi_A$ in the absence of anisotropic stress, which is
    the case at the order v1.0.0 works to; the two are returned separately
    regardless, because (179) carries $\Phi_A'-\Phi_H'$ and collapsing them
    here would hide a sign.

    **`constant_below` is what lets a mode be started at the big bang.**
    Without it this normalises at `eta[0]` *"which is taken to be deep in
    matter domination"* --- an assumption about the caller's grid, baked into a
    library, and one that silently fails the moment the grid is extended
    backwards, which is what finding **T-51**'s fix requires. Below it,
    $\Phi_A$ is held at `amplitude`: that is **the antecedent's own result**,
    $\Phi_E$ time-independent for $K=0$ dust, and it is exactly what (180)
    means by $\Phi_A(0,k)$.

    For $\Omega_r=0$ this is no approximation at all --- there is no radiation
    era to be wrong about. For a background with radiation it **is** one,
    recorded as approximation **A-3**: *Annals II* supplies no radiation-era
    potential, so a mode entering the sound horizon before equality carries no
    radiation driving. The acoustic *phase* is set by $r_s$ and survives this;
    the peak *heights* do not, and that is what Hu \& Sugiyama's analytic
    treatment supplies and what **S35a**'s comparison is for.
    """
    eta = np.asarray(eta, dtype=float)
    if constant_below is None:
        d = growth_factor(background, eta)
        a = background.a_of_eta(eta)
        phi = d / a
        phi_a = amplitude * phi / phi[0]
        return phi_a, -phi_a

    # **Computed on its own grid, so the answer does not depend on the caller's.**
    # The legacy branch above normalises at `eta[0]`, which means two callers
    # asking for the same $\Phi_A(\eta)$ on two different grids get two
    # different answers --- harmless while every grid began at the same place
    # and fatal the moment the acoustic start became per-mode. Below,
    # `constant_below` is the only thing that sets the normalisation, so every
    # mode in a run shares one $\Phi_A(0,k)$ however early it starts.
    reference = float(constant_below)
    if not reference > 0.0:
        raise ValueError("constant_below must be positive; the growth factor "
                         "divides by a(eta) and a(0) = 0")
    top = float(max(eta.max(), reference * (1.0 + 1e-9)))
    internal = np.logspace(np.log10(reference), np.log10(top), GROWTH_SAMPLES)
    ratio = growth_factor(background, internal) / background.a_of_eta(internal)
    shape = CubicSpline(internal, ratio / float(ratio[0]))

    phi_a = amplitude * np.where(eta < reference, 1.0,
                                 shape(np.clip(eta, reference, top)))
    return phi_a, -phi_a


def potential_derivative(eta: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """d(Phi)/d(eta) by spline --- the quantity (179)'s ISW proper is built from."""
    return CubicSpline(np.asarray(eta, dtype=float), np.asarray(phi, dtype=float)).derivative()(eta)
