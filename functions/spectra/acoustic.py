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
    "baryon_photon_ratio",
    "sound_speed_squared",
    "sound_horizon",
    "AcousticSolution",
    "solve_acoustic",
    "sachs_wolfe_at_last_scattering",
    "sachs_wolfe_at_last_scattering_printed",
    "ADIABATIC_MONOPOLE",
]

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
    """r_s(eta) = Int_0^eta c_s d(eta'), the argument of cos(k r_s) in (180)."""
    c_s = np.sqrt(sound_speed_squared(r))
    return np.concatenate(([0.0], cumulative_trapezoid(c_s, np.asarray(eta, dtype=float))))


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
