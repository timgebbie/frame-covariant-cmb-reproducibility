r"""The radiation era's construction, step 2: the potential solved, not supplied.

The supplement's `sec:a3-construction`. Every mode starts at one $\eta_i$ deep in
the radiation era and outside every horizon (`acoustic.common_start_eta`), on
the adiabatic growing mode, and the potential is **integrated with the matter
and the photons** rather than supplied to the oscillator:

    Phi_H' = H Phi_A + (3 H^2 / 2k) sum_i Omega_i(a) (1 + w_i) v_i     (momentum: the source)
    k^2 Phi_H = (3/2) H^2 sum_i Omega_i(a) Delta_i,
        Delta_i = delta_i - 3 H (1 + w_i) v_i / k                       (energy: the check)
    k^2 (Phi_A + Phi_H) = -(8/5) H^2 Omega_gamma(a) tau_2               (the photons' stress)

with $H$ the conformal Hubble rate and $\Omega_i(a)$ each species' share of the
critical density at $a$. The bundle's radiation is photons alone
($N_{\rm eff}=0$), so the stress constraint has one term.

**The species, in this bundle's Newtonian-frame variables.** They follow from Ma
& Bertschinger's conformal Newtonian gauge by $\psi=\Phi_A$, $\phi=-\Phi_H$ and
$\theta_i=-kv_i$, the map under which the three constraints above are theirs
term by term:

    matter:   delta_m' = k v_m - 3 Phi_H',   v_m' = -H v_m - k Phi_A
    photons:  dT' = -Phi_H' + (k/3) tau_1                                (153), expansion coupling dropped
              tau_1' = -(R'/(1+R)) tau_1 - (k/(1+R)) dT - k Phi_A        (152)

Step 2 takes the baryons as pressureless matter in the constraint: they move
with the CDM there, and the photons keep their baryon loading $R$ in (152).
The baryons' own term in the constraint is step 3. **The step-2 system is
therefore not closed at order $R$**: the momentum the photons give the baryons
through $R$ is not in the constraint, where the baryons move with the CDM, so
the energy constraint fails inside the horizon --- by up to 3% of its terms at
$\eta_*$ on `PLANCK_MODEL` --- and holds to $10^{-10}$ with $R\to0$ (D46). That
residual is the baryons' own term, measured before it is added.

**After $\eta_*$ the photons are a hierarchy with gravitational sources.** In
the velocity normalisation of (152)--(153), $\sigma_\ell=(-1)^\ell\tau_\ell$ with
$\tau_\ell$ the covariant multipoles of (F.1), so $\sigma_0=\delta T$ and
$\sigma_1=\tau_1$ hand over without a rescale, and

    sigma_l' = k [ w_l sigma_{l+1} - sigma_{l-1} ] - delta_{l0} Phi_H' - delta_{l1} k Phi_A,
    w_l = (l+1)^2 / [(2l+3)(2l+1)],

which is (F.1) continued to $\ell=0,1$ with eq:transport-exact's rank-0 and
rank-1 sources, closed at `ell_max` by Ma & Bertschinger's free-streaming
truncation. With $\sigma_2=\tfrac{15}2\Theta_2$ in their Legendre
normalisation, their $k^2(\phi-\psi)=12\pi Ga^2(\bar\rho+\bar P)\sigma$ is the
stress constraint above, coefficient and sign. **$\Phi_A$ is taken from it**,
so its residual vanishes by construction and the energy constraint is the
check on the whole solve. The photons are carried until their term in the
momentum constraint falls below `PHOTON_EXIT_FRACTION` of the sum, measured on
the envelope $\sqrt{\sigma_1^2+3\sigma_0^2}$ so that a node of the dipole cannot
end them early; the matter is carried to $\eta_0$.

**The line of sight keeps the released photon pair.** The pair (152)--(153)
continues past $\eta_*$ to `eta_couple` ($6\eta_*$) and is then held, as at step
1, driven by the solved potential; it is what the Sachs--Wolfe and Doppler
slots read where $\mathcal V\neq0$. The hierarchy is the photons as a source of
gravity. Before $\eta_*$ the two are one state. Changing what the slots read in
the visibility's tail is approximation A-5, and not this step.

**The start lies on both constraints (finding T-194).** eq:radiation-ic is
the growing mode at leading order in $(k\eta_i)^2$ and $a_i/a_{\rm eq}$. It
satisfies the momentum constraint, which the solve integrates, but not the
energy constraint beyond that order, and the momentum-constraint system has a
fifth solution the physical system does not: in the radiation era, outside the
horizon, $\Phi\propto\delta T\propto\eta$, with the energy constraint violated
in proportion. A start that leaves an $O(a_i/a_{\rm eq})$ violation therefore
grows by $a_{\rm eq}/a_i$ before equality, an error of order one that **does not
converge as $\eta_i$ falls**. Measured on `PLANCK_MODEL` at $k=10^{-3}$: the
leading-order start gives $\Phi(\eta_*)=0.98531\,\Phi_i$ at $\eta_i$, $\eta_i/2$
and $\eta_i/4$ alike, against Kodama and Sasaki's $0.92539$. `growing_mode`
places the start on both constraints, with $\Phi_A(\eta_i)$ and $\Phi_A'(\eta_i)$
from the two-fluid solution: the same mode, the leading-order expressions its
limit.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import binom

from functions.background.flrw import Background
from functions.spectra.acoustic import baryon_photon_ratio

__all__ = [
    "PHOTON_EXIT_FRACTION",
    "STEP_TWO_ELL_MAX",
    "SolvedMode",
    "growing_mode",
    "kodama_sasaki",
    "matter_weight",
    "photon_weight",
    "solve_mode",
]

#: Ruling 2's stated fraction: the photons leave the constraint once their term
#: in the momentum constraint is below this share of the sum.
PHOTON_EXIT_FRACTION = 1e-4

#: Where the photon hierarchy is closed after $\eta_*$. Measured on
#: `PLANCK_MODEL`: closed at 128 instead, the three-slot transfer moves by at
#: most $6\times10^{-5}$ of the mode's own maximum, at $k\ge500$ where the
#: damping factor is below 0.45; by $9\times10^{-6}$ at $k=200$ and
#: $5\times10^{-14}$ at $k=30$. D46 repeats the potential-level comparison.
STEP_TWO_ELL_MAX = 32

#: `kodama_sasaki` uses its series below this $y$ and its closed form above,
#: where the closed form's cancellation costs under $2\times10^{-13}$.
_KS_SERIES_BELOW = 0.1
_KS_N = np.arange(4, 20)
_KS_C = binom(0.5, _KS_N)


def matter_weight(background: Background, a: np.ndarray | float) -> np.ndarray:
    r"""$\tfrac32\mathcal H^2\Omega_m(a)=\tfrac32H_0^2\Omega_{m0}/a$."""
    return 1.5 * background.h0**2 * background.omega_m / np.asarray(a, dtype=float)


def photon_weight(background: Background, a: np.ndarray | float) -> np.ndarray:
    r"""$\tfrac32\mathcal H^2\Omega_\gamma(a)=\tfrac32H_0^2\Omega_{r0}/a^2$."""
    return 1.5 * background.h0**2 * background.omega_r / np.asarray(a, dtype=float) ** 2


def kodama_sasaki(y: np.ndarray | float) -> tuple[np.ndarray, np.ndarray]:
    r"""$\Phi/\Phi_i$ outside the horizon through equality, and its $y$-derivative.

    Kodama and Sasaki's two-fluid solution, $y=a/a_{\rm eq}$:

    $$\frac{\Phi}{\Phi_i}=\frac{16\sqrt{1+y}+9y^3+2y^2-8y-16}{10y^3}
      =1-\frac{y}{16}+\frac{7y^2}{160}-\dots ,$$

    $\to\tfrac9{10}$ as $y\to\infty$. The numerator cancels to $10y^3$ out of
    terms of order 16, so below `_KS_SERIES_BELOW` the series
    $1+\tfrac85\sum_{n\ge4}\binom{1/2}{n}y^{n-3}$ is used.
    """
    y = np.atleast_1d(np.asarray(y, dtype=float))
    if np.any(y < 0.0):
        raise ValueError("y = a/a_eq must be non-negative")
    f, fp = np.empty_like(y), np.empty_like(y)
    small = y < _KS_SERIES_BELOW
    ys = y[small][:, None]
    f[small] = 1.0 + 1.6 * np.sum(_KS_C * ys ** (_KS_N - 3), axis=1)
    fp[small] = 1.6 * np.sum(_KS_C * (_KS_N - 3) * ys ** (_KS_N - 4), axis=1)
    yl = y[~small]
    s = np.sqrt(1.0 + yl)
    num = 16.0 * s + 9.0 * yl**3 + 2.0 * yl**2 - 8.0 * yl - 16.0
    num_p = 8.0 / s + 27.0 * yl**2 + 4.0 * yl - 8.0
    f[~small] = num / (10.0 * yl**3)
    fp[~small] = (num_p * yl - 3.0 * num) / (10.0 * yl**4)
    return f, fp


def growing_mode(k_com: float, background: Background, eta_i: float,
                 phi_i: float) -> np.ndarray:
    r"""The state $(\Phi_H,\delta_m,v_m,\delta T,\tau_1)$ at $\eta_i$, on both constraints.

    $\Phi_A$ and $\Phi_A'$ are the two-fluid solution's (`kodama_sasaki`), or
    $\Phi_i$ and 0 where $\Omega_r=0$. The common velocity
    $v_m=\tau_1$ then follows from the momentum constraint, and with the
    adiabatic $\delta_m=3\delta T$ the energy constraint gives

    $$\delta T=\frac{\mathcal Hv}{k}+\frac{k^2\Phi_H}{3W_m+4W_\gamma},$$

    $W_i=\tfrac32\mathcal H^2\Omega_i(a)$. In the radiation era this is
    eq:radiation-ic, $\delta T=-\tfrac12\Phi_i$ and $\tau_1=-\tfrac12k\eta_i\Phi_i$,
    corrected at order $a_i/a_{\rm eq}$ and $(k\eta_i)^2$; on an $\Omega_r=0$
    background it is the matter-era mode, $\delta_m=-2\Phi_i-\tfrac16(k\eta_i)^2\Phi_i$
    exactly. Why the corrections are not optional is finding T-194, in the
    module docstring.
    """
    k, eta_i, phi_i = float(k_com), float(eta_i), float(phi_i)
    a = float(background.a_of_eta(eta_i))
    h = float(background.conformal_hubble(a))
    w_m = float(matter_weight(background, a))
    w_g = float(photon_weight(background, a))
    if float(background.omega_r) > 0.0:
        y = a * float(background.omega_m) / float(background.omega_r)
        f, fp = kodama_sasaki(y)
        phi_a, phi_h_prime = phi_i * float(f[0]), -h * y * phi_i * float(fp[0])
    else:
        phi_a, phi_h_prime = phi_i, 0.0
    phi_h = -phi_a
    v = k * (phi_h_prime - h * phi_a) / (w_m + 4.0 / 3.0 * w_g)
    d_t = h * v / k + k**2 * phi_h / (3.0 * w_m + 4.0 * w_g)
    return np.array([phi_h, 3.0 * d_t, v, d_t, v])


@dataclass(frozen=True)
class SolvedMode:
    r"""One mode of step 2 on the requested grid, with its checks.

    `delta_t` and `tau_1` are the photon pair the line of sight reads (held
    after `eta_couple`); `phi_a_prime` and `phi_h_prime` are evaluated from
    the equations at each point, never differentiated from a stored array
    (finding T-23).
    """

    k_com: float
    eta: np.ndarray
    phi_a: np.ndarray
    phi_h: np.ndarray
    phi_a_prime: np.ndarray
    phi_h_prime: np.ndarray
    delta_m: np.ndarray
    v_m: np.ndarray
    delta_t: np.ndarray
    tau_1: np.ndarray
    #: $\Phi_A$ at $\eta_*$ and the photon pair's $\delta T$ there.
    phi_a_star: float
    delta_t_star: float
    #: Where the photons left the constraint: $\eta_0$ if they never did, and
    #: $\eta_*$ where $\Omega_r=0$ gives them no weight in it.
    eta_exit: float
    #: The energy constraint, $E=k^2\Phi_H-\sum W_i\Delta_i$, over the sum of
    #: its terms' magnitudes, at $\eta_*$ and where the photons leave.
    energy_residual_star: float
    energy_residual_exit: float
    #: $(\Phi_A+\Phi_H)/\Phi_A$, the photons' anisotropic stress, at the exit
    #: and its largest magnitude after $\eta_*$ on the requested grid.
    stress_exit: float
    stress_max: float


def _free_streaming_weights(ell_max: int) -> np.ndarray:
    ell = np.arange(ell_max + 1, dtype=float)
    return (ell + 1.0) ** 2 / ((2.0 * ell + 3.0) * (2.0 * ell + 1.0))


class _LogASolution:
    r"""A `solve_ivp` result in $x=\ln a$, read back at the scale factors asked for."""

    def __init__(self, sol):
        self._sol = sol
        self.x, self.y, self.status = sol.t, sol.y, sol.status

    def sol(self, a):
        return self._sol.sol(np.log(a))


def _integrate_in_log_a(rhs, a0, a1, y0, *, events, rtol, atol, k):
    r"""Integrate $\mathrm dy/\mathrm d\ln a$ = `rhs` from $a_0$ to $a_1$.

    **The variable is not a convenience.** Outside the horizon the solution is
    a sum of powers of $\eta$, and in $\eta$ the step grows with $\eta$: on
    Einstein--de~Sitter DOP853 took one step from $6.7\times10^{-6}$ to
    $8\times10^{-4}$, its end values right to $6\times10^{-12}$ and its dense
    output, which the line-of-sight grid is read from, $8\times10^{-9}$ off
    inside it. In $\ln a$ powers are exponentials, a step spans a fixed ratio,
    and $\mathcal H(a)$ is the background's closed form, so no spline of $a(\eta)$
    enters the dynamics; it enters only where the result is read on an $\eta$
    grid.
    """
    sol = solve_ivp(rhs, (math.log(a0), math.log(a1)), y0, method="DOP853",
                    rtol=rtol, atol=atol, dense_output=True, events=events)
    if not sol.success:
        raise RuntimeError(f"step-2 integration failed at k={k}: {sol.message}")
    return _LogASolution(sol)


def solve_mode(
    k_com: float,
    background: Background,
    eta: np.ndarray,
    *,
    eta_i: float,
    eta_star: float,
    eta_couple: float,
    phi_i: float = 1.0,
    omega_b_h2: float = 0.0224,
    ell_max: int = STEP_TWO_ELL_MAX,
    exit_fraction: float = PHOTON_EXIT_FRACTION,
    anisotropic_stress: bool = True,
    rtol: float = 1e-11,
    atol: float = 1e-15,
) -> SolvedMode:
    r"""Integrate one mode from $\eta_i$ to $\eta_0$ and return it on `eta`.

    Three phases, joined where the physics changes: the photon--baryon pair in
    the constraint to $\eta_*$; the hierarchy from $\eta_*$, handed
    $(\delta T,\tau_1,0,\dots)$, until the photons leave the constraint; the
    matter alone after. The line of sight's pair runs beside them to
    `eta_couple` and is held there. `anisotropic_stress=False` sets
    $\Phi_A=-\Phi_H$ after $\eta_*$, the approximation ruling 2 asks to be named
    and measured; it is a control, not a physics switch.
    """
    k = float(k_com)
    eta = np.asarray(eta, dtype=float)
    eta_0 = float(background.eta_0)
    if not 0.0 < eta_i < eta_star < eta_0:
        raise ValueError("need 0 < eta_i < eta_star < eta_0")
    if eta.size and (eta[0] < eta_i * (1 - 1e-12) or eta[-1] > eta_0 * (1 + 1e-12)):
        raise ValueError("the output grid must lie in [eta_i, eta_0]")
    if ell_max < 3:
        raise ValueError("ell_max must be at least 3")
    eta_couple = min(float(eta_couple), eta_0)

    eta_of_a = background.eta_of_a
    h0, o_r, o_m = float(background.h0), float(background.omega_r), float(background.omega_m)
    o_k, o_l = float(background.omega_k), float(background.omega_lambda)
    c_m = 1.5 * h0**2 * o_m
    c_g = 1.5 * h0**2 * o_r
    r_per_a = float(baryon_photon_ratio(1.0, omega_b_h2=omega_b_h2))
    # (8/5) H^2 Omega_gamma / k^2 = (16/15) W_gamma / k^2, times a^2.
    stress_per_a2 = (16.0 / 15.0) * c_g / k**2 if anisotropic_stress else 0.0
    w_l = _free_streaming_weights(ell_max)
    lm = ell_max

    def background_at(x):
        """a, H, W_m, W_gamma, R at x = ln a: the background's closed forms."""
        a = math.exp(x)
        h = h0 * math.sqrt(o_r / (a * a) + o_m / a + o_k + o_l * a * a)
        return a, h, c_m / a, c_g / (a * a), r_per_a * a

    def pair(h, r, d_t, tau, d_phi_h, phi_a, active):
        if not active:
            return 0.0, 0.0
        return (-d_phi_h + k / 3.0 * tau,
                -(h * r / (1.0 + r)) * tau - k / (1.0 + r) * d_t - k * phi_a)

    # Each right-hand side is d/d(eta), divided by H to make it d/d(ln a).
    def tight(x, y):
        phi_h, d_m, v_m, d_t, tau = y
        a, h, w_m, w_g, r = background_at(x)
        phi_a = -phi_h
        d_phi_h = h * phi_a + (w_m * v_m + 4.0 / 3.0 * w_g * tau) / k
        d_pair = pair(h, r, d_t, tau, d_phi_h, phi_a, True)
        return np.array([d_phi_h, k * v_m - 3.0 * d_phi_h, -h * v_m - k * phi_a,
                         d_pair[0], d_pair[1]]) / h

    def free(active):
        def rhs(x, y):
            phi_h, d_m, v_m, d_t, tau = y[:5]
            s = y[5:]
            a, h, w_m, w_g, r = background_at(x)
            phi_a = -phi_h - stress_per_a2 / (a * a) * s[2]
            d_phi_h = h * phi_a + (w_m * v_m + 4.0 / 3.0 * w_g * s[1]) / k
            ds = np.empty_like(s)
            ds[:-1] = k * w_l[:-1] * s[1:]
            ds[0] -= d_phi_h
            ds[1:-1] -= k * s[:-2]
            ds[1] -= k * phi_a
            ds[-1] = (-k * (2.0 * lm + 1.0) / lm * s[-2]
                      - (lm + 1.0) / float(eta_of_a(a)) * s[-1])
            d_pair = pair(h, r, d_t, tau, d_phi_h, phi_a, active)
            out = np.empty_like(y)
            out[:5] = (d_phi_h, k * v_m - 3.0 * d_phi_h, -h * v_m - k * phi_a,
                       d_pair[0], d_pair[1])
            out[5:] = ds
            return out / h
        return rhs

    def matter(active):
        def rhs(x, y):
            phi_h, d_m, v_m, d_t, tau = y
            a, h, w_m, w_g, r = background_at(x)
            phi_a = -phi_h
            d_phi_h = h * phi_a + w_m * v_m / k
            d_pair = pair(h, r, d_t, tau, d_phi_h, phi_a, active)
            return np.array([d_phi_h, k * v_m - 3.0 * d_phi_h, -h * v_m - k * phi_a,
                             d_pair[0], d_pair[1]]) / h
        return rhs

    def exit_event(x, y):
        phi_h, d_m, v_m = y[0], y[1], y[2]
        s0, s1, s2 = y[5], y[6], y[7]
        a, h, w_m, w_g, r = background_at(x)
        phi_a = -phi_h - stress_per_a2 / (a * a) * s2
        photons = 4.0 / 3.0 * w_g * math.sqrt(s1 * s1 + 3.0 * s0 * s0) / k
        total = abs(h * phi_a) + abs(w_m * v_m / k) + 4.0 / 3.0 * w_g * abs(s1) / k
        return photons - exit_fraction * total
    exit_event.terminal = True
    exit_event.direction = -1

    scale = abs(float(phi_i))

    def integrate(rhs, a0, a1, y0, events=None):
        return _integrate_in_log_a(rhs, a0, a1, y0, events=events, rtol=rtol,
                                   atol=atol * scale, k=k)

    a_of = background.a_of_eta
    a_i, a_star = float(a_of(eta_i)), float(a_of(eta_star))
    a_couple, a_end = float(a_of(eta_couple)), 1.0
    if eta_couple >= eta_0:
        a_couple = a_end
    pieces = []      # (phase, pair active, a0, a1, solution)
    sol = integrate(tight, a_i, a_star, growing_mode(k, background, eta_i, phi_i))
    pieces.append(("tight", True, a_i, a_star, sol))
    # Where Omega_r = 0 the photons carry no weight in the constraint, so they
    # have none to leave it with: the matter goes on alone from eta_*.
    photons = c_g > 0.0
    y = (np.concatenate((sol.y[:, -1], sol.y[3:5, -1], np.zeros(ell_max - 1)))
         if photons else sol.y[:, -1])
    a, a_exit = a_star, (a_end if photons else a_star)
    for a_stop, active in ((a_couple, True), (a_end, False)):
        if a >= a_stop:
            continue
        if photons:
            sol = integrate(free(active), a, a_stop, y, events=exit_event)
            a_reached = math.exp(float(sol.x[-1]))
            pieces.append(("free", active, a, a_reached, sol))
            y, a = sol.y[:, -1], a_reached
            if sol.status == 1:
                photons, a_exit, y = False, a, y[:5]
        if not photons and a < a_stop:
            sol = integrate(matter(active), a, a_stop, y)
            pieces.append(("matter", active, a, a_stop, sol))
            y, a = sol.y[:, -1], a_stop

    return _assemble(k, background, eta, pieces, a_star=a_star, a_exit=a_exit,
                     stress_per_a2=stress_per_a2, w_l=w_l, c_m=c_m, c_g=c_g)


def _derived(k, background, phase, a, state, stress_per_a2, w_l, c_m, c_g):
    """Phi_A, Phi_H', Phi_A' and the energy residual from a state, vectorised in a."""
    a = np.asarray(a, dtype=float)
    h = np.asarray(background.conformal_hubble(a), dtype=float)
    w_m, w_g = c_m / a, c_g / a**2
    phi_h, d_m, v_m, d_t, tau = state[:5]
    if phase == "free":
        s0, s1, s2, s3 = state[5], state[6], state[7], state[8]
        phi_a = -phi_h - stress_per_a2 / a**2 * s2
        d_phi_h = h * phi_a + (w_m * v_m + 4.0 / 3.0 * w_g * s1) / k
        d_s2 = k * (w_l[2] * s3 - s1)
        phi_a_prime = -d_phi_h - stress_per_a2 / a**2 * (d_s2 - 2.0 * h * s2)
        photon_d, photon_v = s0, s1
    else:
        phi_a = -phi_h
        photon_v = tau if phase == "tight" else 0.0 * tau
        photon_d = d_t if phase == "tight" else 0.0 * d_t
        d_phi_h = h * phi_a + (w_m * v_m + 4.0 / 3.0 * w_g * photon_v) / k
        phi_a_prime = -d_phi_h
    terms = (k**2 * phi_h, w_m * d_m, 3.0 * w_m * h * v_m / k,
             4.0 * w_g * photon_d, 4.0 * w_g * h * photon_v / k)
    energy = terms[0] - (terms[1] - terms[2] + terms[3] - terms[4])
    size = sum(np.abs(x) for x in terms)
    return phi_a, d_phi_h, phi_a_prime, energy / np.maximum(size, 1e-300)


def _assemble(k, background, eta, pieces, *, a_star, a_exit, stress_per_a2,
              w_l, c_m, c_g) -> SolvedMode:
    n = eta.size
    out = {name: np.empty(n) for name in (
        "phi_a", "phi_h", "phi_a_prime", "phi_h_prime", "delta_m", "v_m",
        "delta_t", "tau_1", "stress")}
    # The grid is read in a through the background's own a(eta), at the end
    # points of each phase exactly, so a point on a boundary takes the later
    # phase and the last point the last.
    a_grid = np.minimum(np.asarray(background.a_of_eta(eta), dtype=float), 1.0)
    filled = np.zeros(n, dtype=bool)
    last = len(pieces) - 1
    for i, (phase, _active, a0, a1, sol) in enumerate(pieces):
        inside = ((a_grid >= a0 * (1 - 1e-14)) & ((a_grid < a1) | (i == last))
                  & ~filled)
        if not inside.any():
            continue
        a = np.clip(a_grid[inside], a0, a1)
        state = sol.sol(a)
        phi_a, d_phi_h, phi_a_prime, _ = _derived(
            k, background, phase, a, state, stress_per_a2, w_l, c_m, c_g)
        out["phi_a"][inside], out["phi_h"][inside] = phi_a, state[0]
        out["phi_a_prime"][inside], out["phi_h_prime"][inside] = phi_a_prime, d_phi_h
        out["delta_m"][inside], out["v_m"][inside] = state[1], state[2]
        out["delta_t"][inside], out["tau_1"][inside] = state[3], state[4]
        out["stress"][inside] = (phi_a + state[0]) / phi_a
        filled |= inside

    def at(phase_wanted, a_wanted):
        for phase, _active, a0, a1, sol in reversed(pieces):
            if phase == phase_wanted and a0 <= a_wanted <= a1 * (1 + 1e-14):
                state = sol.sol(min(a_wanted, a1))
                return state, _derived(k, background, phase, np.array([a_wanted]),
                                       state[:, None], stress_per_a2, w_l, c_m, c_g)
        return None, None

    state_star, derived_star = at("tight", a_star)
    state_exit, derived_exit = at("free", a_exit)
    after = a_grid > a_star
    return SolvedMode(
        k_com=k, eta=eta, **{key: value for key, value in out.items() if key != "stress"},
        phi_a_star=float(derived_star[0][0]), delta_t_star=float(state_star[3]),
        eta_exit=float(background.eta_of_a(a_exit)) if a_exit < 1.0 else float(background.eta_0),
        energy_residual_star=float(derived_star[3][0]),
        energy_residual_exit=(float(derived_exit[3][0]) if derived_exit else float("nan")),
        stress_exit=(float((derived_exit[0][0] + state_exit[0]) / derived_exit[0][0])
                     if derived_exit else 0.0),
        stress_max=float(np.max(np.abs(out["stress"][after]))) if after.any() else 0.0,
    )
