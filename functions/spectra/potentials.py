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

__all__ = [
    "growth_factor",
    "potentials",
    "potential_derivative",
    "radiation_era_potential",
]


def radiation_era_potential(
    k_com: float, eta: np.ndarray, *, amplitude: float = 1.0
) -> np.ndarray:
    r"""$\Phi$ through radiation domination, in closed form. **Approximation A-3.**

    **Derived, not transcribed.** In a flat radiation-dominated era the
    potential obeys the standard evolution equation with $c_s^2=\tfrac13$,

    $$\Phi''+3\mathcal H(1+c_s^2)\Phi'+c_s^2k^2\Phi=0 ,$$

    and $a\propto\eta$ there makes $\mathcal H=1/\eta$, so

    $$\Phi''+\frac4\eta\Phi'+\frac{k^2}{3}\Phi=0 .$$

    With $x\equiv k\eta/\sqrt3$ this is the $\ell=1$ spherical Bessel equation
    in disguise, and the solution regular at the origin is

    $$\Phi(\eta)=3\,\Phi_i\,\frac{\sin x-x\cos x}{x^3}
                =3\,\Phi_i\,\frac{j_1(x)}{x}.$$

    Two limits fix it and both are asserted in `tests/test_radiation_potential.py`:
    $\Phi\to\Phi_i$ as $x\to0$, because $\sin x-x\cos x\to x^3/3$; and
    $\Phi\simeq-3\Phi_i\cos x/x^2$ for $x\gg1$, **decaying as $x^{-2}$ while
    oscillating**.

    **That decay is the whole of A-3.** `potentials` returns the
    matter-dominated $\Phi\propto D/a$, which is *constant* in Einstein--de
    Sitter and has no radiation era in it at all, so a mode that enters the
    horizon before equality is driven here by a potential that does not decay.
    In the real universe it does, and because it decays on the same timescale
    the mode oscillates, it drives the oscillator **resonantly** --- which is
    the amplification Hu \& Sugiyama compute analytically and which is missing
    from every peak height this bundle produces.

    **This function is diagnostic, not yet wired into the released pipeline.**
    It is what `scripts/diagnostic_d10_radiation_driving.py` measures the gap
    with. Changing what drives `solve_acoustic` is the fix, and under this
    bundle's standing rule the measurement comes first and the matter-only
    branch is kept as a control afterwards.

    `amplitude` is $\Phi_i$, the super-horizon value; the released
    normalisation convention (``Phi = 1`` deep in matter domination) does
    **not** apply here, because the whole point is the ratio between the two
    eras.
    """
    k = float(k_com)
    if k <= 0.0:
        raise ValueError("k_com must be positive")
    eta = np.asarray(eta, dtype=float)
    if np.any(eta < 0.0):
        raise ValueError("eta must be non-negative")
    x = k * eta / np.sqrt(3.0)
    out = np.empty_like(x)
    # **The crossover is derived, not picked.** $\sin x-x\cos x$ is a
    # cancelling difference of two $O(x)$ terms whose value is $x^3/3$, so its
    # relative error is $\sim3\varepsilon/x^2$: at $x=10^{-3}$ the closed form
    # has already lost nine digits ($3\times10^{-10}$), and the first draft of
    # this function crossed over there and left a seam of $2\times10^{-9}$.
    # At $x=0.1$ the closed form is good to $3\times10^{-14}$ and the series
    # carried to $x^6$ has a first omitted term of $x^8/1330560$, so the two
    # branches meet at $1.8\times10^{-14}$ --- measured.
    # The two branches then meet where **both** are well conditioned, which is
    # the only place a crossover may be put.
    small = x < 0.1
    xs2 = x[small] ** 2
    out[small] = amplitude * (1.0 - xs2 / 10.0 + xs2**2 / 280.0
                              - xs2**3 / 15120.0)
    xs = x[~small]
    out[~small] = 3.0 * amplitude * (np.sin(xs) - xs * np.cos(xs)) / xs**3
    return out


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

    reference = float(constant_below)
    if not reference > 0.0:
        raise ValueError("constant_below must be positive; the growth factor "
                         "divides by a(eta) and a(0) = 0")

    # **Solved on the requested points themselves, anchored at the reference.**
    # No spline, and that is not a style preference. An earlier version
    # integrated the growth factor on its own logarithmic grid and splined the
    # result onto `eta`; the answer agreed to twelve figures and the
    # *derivative* did not, and `coefficients.cdm_set` holds Appendix G's
    # $\dot\sigma$ against the Euler equation at `rtol=1e-9`:
    #
    #     (a sigma)' = a' sigma + a^2 sigma-dot  ==  -k v'
    #
    # That is an **identity given the field equations**, so it holds for the
    # true $\Phi_A$ and not for a spline of it --- the two sides pick up
    # different interpolation errors and the frame stops closing. The guard
    # refused the regeneration, which is exactly what a guard is for, and
    # loosening it to accommodate a spline would have traded a check for a
    # convenience.
    #
    # Prepending the reference costs one extra point and makes the result
    # **grid-independent**: every caller anchors at the same eta, so a mode
    # starting at 1e-4 and the common grid starting at 0.036 carry one
    # Phi_A(0,k) between them --- which is what finding T-51's fix needs.
    above = eta >= reference
    if not above.any():
        phi_a = np.full_like(eta, amplitude)
        return phi_a, -phi_a

    requested = eta[above]
    prepend = float(requested[0]) > reference
    grid = np.concatenate(([reference], requested)) if prepend else requested
    if grid.size < 2:
        grid = np.array([reference, float(background.eta_0)])
        prepend = True

    ratio = growth_factor(background, grid) / background.a_of_eta(grid)
    shape = ratio / float(ratio[0])

    phi_a = np.empty_like(eta)
    phi_a[~above] = amplitude
    phi_a[above] = amplitude * (shape[1:1 + requested.size] if prepend
                                else shape[:requested.size])
    return phi_a, -phi_a


def potential_derivative(eta: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """d(Phi)/d(eta) by spline --- the quantity (179)'s ISW proper is built from."""
    return CubicSpline(np.asarray(eta, dtype=float),
                       np.asarray(phi, dtype=float)).derivative()(eta)
