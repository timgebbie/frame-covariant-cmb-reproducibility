"""The acoustic oscillation and its solution at last scattering, Annals II §7.1.

Published equation numbers, resolved against the accepted manuscript.

    (152)  tau_1^dot  ~= -(R^dot/(1+R)) tau_1 - (1/(1+R))(k/a) dT - (k/a) Phi_A
    (153)  dT^dot     ~= -H Phi_A - Phi_H^dot + (k/a)(1/3) tau_1
    (154)  dT'' + (R'/(1+R)) dT' + k^2 c_s^2 dT
                       ~= -Phi_H'' - (R'/(1+R)) Phi_H' - (k^2/3) Phi_A
    (180)  dT(eta,k) + Phi_A(eta_*,k)
                       ~= [dT(0,k) + (1+R) Phi_A(0,k)] cos(k r_s) - R Phi_A(eta_*,k)
    (181)  [dT + Phi_A](eta_*,k) ~= (1/3) Phi_A(0,k)(1+3R_*) cos(k r_s^*) -+ R_* Phi_A(0,k)

    sound speed, §6:   c_s^2 = 1/(3(1+R)),  R = 3 rho_M / 4 rho_R

**The pair is implemented, not the oscillator.** (154) is derived from (152) and
(153) by "ignoring the expansion coupled term (i.e the small scale
approximation)", which is the paper's own description. Dropping a term is a
specialisation, so the general object is the pair and (154) is a *consequence* of
it. Implementing the pair and recovering (154) makes what was dropped measurable:
`expansion_coupling=False` reproduces (154) exactly, and the difference between
the two integrations is the size of the approximation at any $k$ and $\\eta$.

That ordering matters more than it looks. Implementing (154) directly would make
the small-scale approximation invisible --- it would be baked into the only
object that exists, and no figure could ever show its cost.

**Finding B-8.** (181) prints $+R_*\\Phi_A$ where (180) gives $-R_*\\Phi_A$. The
oscillating parts of the two agree exactly, so (181) is (180) with one sign
flipped, and (181)'s own stated limit $r_s^*\\to0$ settles which is right: with
the minus the result is exactly $\\tfrac13\\Phi_A$ as the text asserts, while with
the plus it is $\\tfrac13\\Phi_A(1+6R_*)$ and the assertion needs $R_*\\to0$, which
is not stated and not true at last scattering. Corrected here; the printed form
is kept as `sachs_wolfe_at_last_scattering_printed` so the difference is
demonstrable rather than asserted.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import cumulative_trapezoid, solve_ivp
from scipy.interpolate import CubicSpline

from functions.background.flrw import Background

__all__ = [
    "ACOUSTIC_START_EPSILON",
    "RS_SAMPLES",
    "baryon_photon_ratio",
    "sound_speed_squared",
    "sound_horizon",
    "sound_horizon_from_zero",
    "acoustic_start_eta",
    "required_acoustic_points",
    "ACOUSTIC_POINTS_PER_PERIOD",
    "AcousticSolution",
    "solve_acoustic",
    "sachs_wolfe_at_last_scattering",
    "sachs_wolfe_at_last_scattering_printed",
    "ADIABATIC_MONOPOLE",
    "TIGHT_COUPLING_FACTOR",
]

#: Where the tight-coupling oscillator stops and its last value is held: the
#: integration runs to $\min(\eta_0,\;\texttt{TIGHT\_COUPLING\_FACTOR}\,\eta_*)$.
#:
#: **Finding T-58, and it lives here because it was living in three places.**
#: `pipeline.run` took it as a parameter defaulting to 6.0, `two_frame` kept a
#: module constant commented *"as `pipeline.run` sets it"*, and
#: `two_route.two_route_transfer` integrated the oscillator all the way to
#: $\eta_0$ --- so **the route criterion 5b gates was the one that did not
#: have the window at all**, and kept the photon--baryon fluid ringing for
#: seven times the span over which it is a fluid.
#:
#: 5b could not see it: both its columns are built from one acoustic solve, so
#: they share the window whatever it is. **T-3's rule, on a third quantity.**
#: Measured on `PLANCK_MODEL`, `two_frame` against `two_route`'s (177)--(179)
#: column, normalised by the row's own scale as `TwoRoute.relative` is: the
#: mismatched window alone costs $1.5\times10^{-1}$ at $k=3$ and
#: $1.6\times10^{0}$ at $k=10$, against 5b's own $5\times10^{-8}$.
#:
#: Six is not derived and is not claimed to be. It is the one number here that
#: is a modelling choice --- where tight coupling ends --- and it is now a
#: single modelling choice rather than three.
TIGHT_COUPLING_FACTOR = 6.0

#: Samples used to accumulate $r_s$ from the big bang. **Logarithmic, and that
#: is not a style choice**: $c_s\to1/\sqrt3$ as $\eta\to0$ while the span to
#: $\eta_*$ covers five decades, so a uniform grid spends every sample where
#: the integrand is flat and none where it turns over. Registered `measured`
#: with its convergence in `config/grid-register.toml`.
RS_SAMPLES = 400_000

#: The $\varepsilon$ in $k\,r_s(\eta_{\rm start})\le\varepsilon$.
#:
#: **Not a tolerance on an answer --- a statement of when an initial condition
#: is the right one.** (180) sets $\delta T(0,k)\simeq-\tfrac23\Phi_A(0,k)$ with
#: $\tau_1=0$ *at the big bang*, and that is the adiabatic growing mode only
#: while the mode is outside the sound horizon. Starting at finite $k\,r_s$
#: imposes a phase instead of inheriting one. 0.1 radians is one part in sixty
#: of a full oscillation; finding **T-51** measures what the bundle did
#: instead, which reached **10.7** at $k=600$.
ACOUSTIC_START_EPSILON = 0.1

#: The adiabatic initial condition §7.1.2 uses:
#: dT(0,k) ~ (1/3) Delta(0,k) ~ -(2/3) Phi_A(0,k), flat adiabatic CDM.
ADIABATIC_MONOPOLE = -2.0 / 3.0


def baryon_photon_ratio(
    a: np.ndarray | float, *, omega_b_h2: float = 0.0224, omega_gamma_h2: float = 2.47e-5
) -> np.ndarray:
    """R = 3 rho_B / 4 rho_gamma, which scales as a.

    `omega_gamma_h2` is a **standard** value and not one the antecedent supplies;
    it is recorded as such in the parameter table, because it enters only here
    and through the sound speed.
    """
    return (3.0 * omega_b_h2 / (4.0 * omega_gamma_h2)) * np.asarray(a, dtype=float)


def sound_speed_squared(r: np.ndarray | float) -> np.ndarray:
    """c_s^2 = 1/(3(1+R)), §6. Reduces to 1/3 for R -> 0 and to 0 in matter domination."""
    return 1.0 / (3.0 * (1.0 + np.asarray(r, dtype=float)))


def sound_horizon(eta: np.ndarray, r: np.ndarray) -> np.ndarray:
    r"""$\int_{\eta_0}^{\eta}c_s\,d\eta'$ **on the grid it is handed**.

    **The docstring used to say $\int_0^\eta$ and that was a lie whenever
    `eta[0] > 0`** --- which, in `pipeline.run`, it always was: the grid began
    at `RecombinationHistory.build`'s `z_max = 3000.0`, so this returned
    between 36% and 49% of the sound horizon and (180)'s $\cos(k r_s)$ carried
    a halved phase. That is finding **T-51**, and *this function was its twin*:
    the closed-form route inherited the same truncation independently of the
    ODE route, so the two agreed and criterion 5b saw nothing. **T-3**'s lesson
    --- two agreeing routes agree about what they share.

    Use `sound_horizon_from_zero` when the quantity wanted is $r_s$ proper.
    This one remains for accumulating over a given interval, which is a real
    and different question, and now says so.
    """
    c_s = np.sqrt(sound_speed_squared(r))
    return np.concatenate(([0.0], cumulative_trapezoid(c_s, np.asarray(eta, dtype=float))))


def sound_horizon_from_zero(
    background: Background, eta_max: float, *, omega_b_h2: float = 0.0224,
    samples: int = RS_SAMPLES,
) -> tuple[np.ndarray, np.ndarray]:
    r"""$(\eta, r_s(\eta))$ accumulated **from the big bang**, to `eta_max`.

    $r_s(\eta)=\int_0^\eta c_s\,d\eta'$ --- the quantity (180) means by
    $\cos(k r_s)$ and the one *Annals II* means by *"the sound-horizon near
    decoupling"* in its own acoustic-peak formula $\ell_j\simeq|r_\theta/r_s|j\pi$.

    Logarithmic in $\eta$: see `RS_SAMPLES`. The lower limit $10^{-9}$ is not a
    cutoff anyone has to converge --- $c_s\le1/\sqrt3$ bounds what lies below it
    at under $6\times10^{-10}$ against $r_s\simeq0.036$ --- and it is measured
    rather than argued in the grid register.
    """
    eta = np.logspace(-9.0, np.log10(float(eta_max)), int(samples))
    c_s = np.sqrt(sound_speed_squared(
        baryon_photon_ratio(background.a_of_eta(eta), omega_b_h2=omega_b_h2)))
    accumulated = np.concatenate(
        ([0.0], np.cumsum(0.5 * (c_s[1:] + c_s[:-1]) * np.diff(eta))))
    return eta, accumulated


def acoustic_start_eta(
    k_com: float, eta: np.ndarray, r_s: np.ndarray, *,
    epsilon: float = ACOUSTIC_START_EPSILON,
) -> float:
    r"""The $\eta$ at which mode `k_com` may be started: $k\,r_s(\eta)\le\varepsilon$.

    **Derived from $k$, the way `required_n_eta` is derived from $k_{\max}$**,
    and for the same reason: a single global start cannot serve a band spanning
    a factor of two thousand in $k$. At $k=600$ the condition wants
    $\eta\simeq0.015\,\eta_{\rm eq}$, and at $k=10$ it is satisfied almost
    anywhere --- one number cannot be right for both, so no number is chosen.

    Raises rather than clamping. A start the tabulated $r_s$ cannot reach is a
    mode this background cannot legitimately carry, and silently beginning it
    late is precisely finding **T-51**.
    """
    if k_com <= 0.0:
        raise ValueError("k_com must be positive")
    target = epsilon / float(k_com)
    r_s = np.asarray(r_s, dtype=float)
    if target <= r_s[0]:
        raise ValueError(
            f"k={k_com:g} needs r_s(eta_start) <= {target:.3e}, below the first "
            f"tabulated value {r_s[0]:.3e}. Extend the r_s table downward; do "
            "not start the mode late --- that is finding T-51.")
    if target > r_s[-1]:
        # **The mode never enters the sound horizon**: k r_s <= epsilon all the
        # way to eta_max, so it is frozen at its adiabatic initial condition
        # throughout and any early start is the right one. Returning the first
        # tabulated eta is not a clamp standing in for a failure --- it is the
        # answer. The large-angle modes that dominate the Sachs--Wolfe plateau
        # are exactly these, and raising here would refuse the easiest half of
        # the band for being easy.
        return float(np.asarray(eta, dtype=float)[0])
    return float(np.interp(target, r_s, np.asarray(eta, dtype=float)))


#: Samples per acoustic oscillation on a mode's own integration grid. The ODE
#: is stepped adaptively by DOP853; this sets the **output** grid, which is
#: then interpolated onto the common line-of-sight grid, so it is a
#: reconstruction rate rather than an accuracy knob. Twice the line-of-sight
#: rate, because this grid is resampled once more before it is used.
ACOUSTIC_POINTS_PER_PERIOD = 24

#: Floor on a mode's grid, for the super-horizon modes whose period is longer
#: than the integration itself and whose point count would otherwise round to
#: nothing. `solve_acoustic` separately refuses a window under 50 points.
ACOUSTIC_POINTS_FLOOR = 512


def required_acoustic_points(
    k_com: float, eta_span: float, *,
    points_per_period: int = ACOUSTIC_POINTS_PER_PERIOD,
) -> int:
    r"""How many output samples a mode's acoustic grid needs, **derived from $k$**.

    $\delta T$ oscillates as $\cos(k r_s)$, with period $2\pi/(k c_s)$ in
    $\eta$. That period is shortest where $c_s$ is largest, and
    $c_s^2=1/(3(1+R))\le1/3$, so the period is **at least**
    $2\pi\sqrt3/k$ --- a bound rather than an estimate, which is what lets this
    be arithmetic instead of a tuning knob. Same construction as
    `required_n_eta`, same reason: once the start is derived per mode
    (**T-51**), the span is per mode too, and one fixed point count cannot
    serve a band spanning a factor of two thousand in $k$.
    """
    if k_com <= 0.0 or eta_span <= 0.0:
        raise ValueError("k_com and eta_span must be positive")
    shortest_period = 2.0 * np.pi * np.sqrt(3.0) / float(k_com)
    return max(int(np.ceil(points_per_period * float(eta_span) / shortest_period)),
               ACOUSTIC_POINTS_FLOOR)


@dataclass(frozen=True)
class AcousticSolution:
    """delta T and tau_1 through decoupling, at one comoving wavenumber."""

    eta: np.ndarray
    delta_T: np.ndarray
    tau_1: np.ndarray
    k_com: float
    expansion_coupling: bool

    def at(self, eta_star: float) -> tuple[float, float]:
        """(delta T, tau_1) at last scattering --- what (176)'s sources need."""
        return (
            float(CubicSpline(self.eta, self.delta_T)(eta_star)),
            float(CubicSpline(self.eta, self.tau_1)(eta_star)),
        )


def solve_acoustic(
    k_com: float,
    eta: np.ndarray,
    *,
    background: Background,
    phi_a: np.ndarray,
    phi_h: np.ndarray,
    omega_b_h2: float = 0.0224,
    omega_gamma_h2: float = 2.47e-5,
    expansion_coupling: bool = True,
    initial: tuple[float, float] | None = None,
) -> AcousticSolution:
    """Integrate (152) and (153) in conformal time.

    In conformal time, multiplying each by $a$:

        tau_1' = -(R'/(1+R)) tau_1 - (k/(1+R)) dT - k Phi_A
        dT'    = -aH Phi_A - Phi_H' + (k/3) tau_1

    `expansion_coupling=False` drops the $-aH\\Phi_A$ term, which is the paper's
    "small scale approximation" and is exactly what turns the pair into (154).

    Potentials are **supplied**, not solved for, on the same grid as `eta`. This
    module integrates the radiation; what drives it is someone else's problem,
    which is what lets the same routine serve CDM and $\\Lambda$CDM.
    """
    eta = np.asarray(eta, dtype=float)
    a = background.a_of_eta(eta)
    r = baryon_photon_ratio(a, omega_b_h2=omega_b_h2, omega_gamma_h2=omega_gamma_h2)

    r_spline = CubicSpline(eta, r)
    r_prime = r_spline.derivative()
    aH = CubicSpline(eta, background.conformal_hubble(a))
    phi_a_spline = CubicSpline(eta, np.asarray(phi_a, dtype=float))
    phi_h_prime = CubicSpline(eta, np.asarray(phi_h, dtype=float)).derivative()

    def rhs(t: float, y: np.ndarray) -> list[float]:
        delta_t, tau_1 = y
        r_t = float(r_spline(t))
        d_tau = (
            -float(r_prime(t)) / (1.0 + r_t) * tau_1
            - k_com / (1.0 + r_t) * delta_t
            - k_com * float(phi_a_spline(t))
        )
        d_delta = -float(phi_h_prime(t)) + k_com / 3.0 * tau_1
        if expansion_coupling:
            d_delta -= float(aH(t)) * float(phi_a_spline(t))
        return [d_delta, d_tau]

    start = initial if initial is not None else (ADIABATIC_MONOPOLE * float(phi_a[0]), 0.0)
    solution = solve_ivp(
        rhs, (eta[0], eta[-1]), list(start), t_eval=eta,
        method="DOP853", rtol=1e-10, atol=1e-12,
    )
    if not solution.success:
        raise RuntimeError(f"acoustic integration failed: {solution.message}")

    return AcousticSolution(
        eta=eta,
        delta_T=solution.y[0],
        tau_1=solution.y[1],
        k_com=k_com,
        expansion_coupling=expansion_coupling,
    )


# ----------------------------------------------------------------------------
# the closed form at last scattering
# ----------------------------------------------------------------------------


def sachs_wolfe_at_last_scattering(
    phi_a0: float, r_star: float, k_rs_star: float
) -> float:
    """(181), **corrected**: the constant term carries $-R_*$. Finding B-8.

    At $r_s^*\\to0$ this is exactly $\\tfrac13\\Phi_A(0,k)$, which is what the text
    asserts and what (196) descends from.
    """
    return (
        (1.0 / 3.0) * phi_a0 * (1.0 + 3.0 * r_star) * np.cos(k_rs_star)
        - r_star * phi_a0
    )


def sachs_wolfe_at_last_scattering_printed(
    phi_a0: float, r_star: float, k_rs_star: float
) -> float:
    """(181) exactly as printed, with $+R_*$. Kept so B-8 is demonstrable."""
    return (
        (1.0 / 3.0) * phi_a0 * (1.0 + 3.0 * r_star) * np.cos(k_rs_star)
        + r_star * phi_a0
    )
