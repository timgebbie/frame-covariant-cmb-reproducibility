r"""(102) evaluated in two frames, and decomposed by **rank**.

This module exists because two consumers need the same thing --- the F5 figure
and the frame-invariance measurement --- and the second had it as a private
function in a script. A proof-of-concept used by two release-candidate artefacts
is a module with tests, not a helper someone imports across `scripts/`.

**The decomposition is by rank, not by the three-way split of \S7.1.1.** That
split --- primary, Doppler, integrated --- is a *Newtonian-frame* construction:
it descends from (110) and (111), which exist only after $\tilde\sigma_{ab}=0$
has removed the shear sector. Decomposing the CDM frame that way would be
reporting a Newtonian-frame answer about a frame that is not Newtonian. The rank
split $C_0,C_1,C_2$ is what (89) actually produces and is defined in any frame,
which is what makes it the covariant statement --- the PI's call, 2026-10-14.

What the two frames carry:

| | Newtonian | CDM |
|---|---|---|
| rank 0, $C_0$ | $0$ | $-\tfrac52a\mathcal B_2$ |
| rank 1, $C_1$ | the whole source | shifted by $-(v'-\kappa'v)/k$ |
| rank 2, $C_2$ | $0$ | $v/k$ |

**The transfer function is linear in the $C_A$ and $C_\ell$ is not.** That is
why `transfer_by_rank` returns three arrays that add, and why
`cl_cross` exists at all: the rank contributions to $C_\ell$ do **not** add, and
the cross terms are the difference. A figure that showed only the three
auto-spectra would be a figure whose parts do not sum to the whole it is drawn
beside.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from functions.background.flrw import Background
from functions.spectra.acoustic import baryon_photon_ratio, solve_acoustic
from functions.spectra.angular import cl_covariant_route
from functions.spectra.bessel_table import BesselTable
from functions.spectra.coefficients import (
    CoefficientSet,
    background_fluid,
    cdm_set,
    newtonian_set,
)
from functions.spectra.decoupling import RecombinationHistory, diffusion_scale
from functions.spectra.frame_transform import cdm_frame_shift
from functions.spectra.integral_solution import integral_solution
from functions.spectra.pipeline import required_n_eta
from functions.spectra.potentials import potential_derivative, potentials
from functions.spectra.transfer import (
    ANNALS_II_GAMMA,
    transfer_function,
)

__all__ = [
    "TwoFrameEnvironment",
    "build_environment",
    "cl_cross",
    "coefficient_sets",
    "transfer_by_rank",
]

#: The tight-coupling window, as `pipeline.run` sets it.
TIGHT_COUPLING_FACTOR = 6.0


#: $c/H_0$ in Mpc for $h=1$. The bundle works in units of $c/H_0$, the fit of
#: (J.5) works in Mpc$^{-1}$, and this is the only place the two meet.
HUBBLE_RADIUS_MPC = 2997.92458

@dataclass(frozen=True)
class TwoFrameEnvironment:
    r"""Everything both frames share, built once for a whole $k$ grid."""

    background: Background
    recombination: RecombinationHistory
    eta: np.ndarray
    eta_star: float
    a: np.ndarray
    conformal_hubble: np.ndarray
    conformal_hubble_prime: np.ndarray
    rho: np.ndarray
    pressure: np.ndarray
    phi_a: np.ndarray
    phi_h: np.ndarray
    phi_a_prime: np.ndarray
    phi_h_prime: np.ndarray
    r_baryon: np.ndarray
    r_baryon_prime: np.ndarray
    kappa_prime: np.ndarray
    kappa_second: np.ndarray
    visibility: np.ndarray
    damping_k: float
    omega_b_h2: float
    #: The $k$ this environment's $\eta$ grid was sized for. **Finding T-34.**
    #: `required_n_eta` gives six samples per $j_\ell$ oscillation at this $k$
    #: and no more, so asking for a larger one aliases the line-of-sight
    #: integral --- which is T-3, and it returns a smooth, plausible, wrong
    #: answer rather than an error. `check_k` is what makes it an error.
    k_max: float = float("inf")
    #: Appendix J's shape parameter and the dimensionless $h$, carried so the
    #: transfer function can be evaluated per mode. Defaults are *Annals II*
    #: \S8.3.2's standard-CDM model, $\Gamma=0.48$ and $h=0.5$, because that is
    #: the model `CDM_MODEL` reconstructs. **Finding T-37.**
    transfer_gamma: float = ANNALS_II_GAMMA
    hubble_h: float = 0.5
    #: `False` restores the pre-T-37 behaviour --- $\Phi$ handed to every mode
    #: with no $k$ in it --- so the change is a measurement rather than a claim.
    #: It is not a physics switch to leave lying about: it exists to regenerate
    #: the v1.2.0-dev figures both ways and comes out once the PI has chosen.
    apply_transfer: bool = True

    def transfer_at(self, k_com: float) -> float:
        r"""$T(k)$ of (J.5), corrected (**B-10**), at one comoving mode.

        **The unit conversion is the whole of this method and it is where a
        factor would hide.** `k_com` is in the bundle's units, where $h_0=1$ and
        lengths are in $c/H_0 = 2997.9/h$ Mpc, while (J.5)'s fit wants
        Mpc$^{-1}$:

        $$k[\mathrm{Mpc}^{-1}] = k_{com}\,h/2997.9 .$$

        At the top of the $k$ grid, $k_{com}=1900$ with $h=0.5$, that is
        $0.317\,\mathrm{Mpc}^{-1}$ and $T=0.045$ --- a factor of twenty-two in
        the potential and five hundred in power. Which is the point: without it
        every mode is driven by the same $\Phi$ and the acoustic peak *heights*
        carry no radiation-era suppression at all.
        """
        if not self.apply_transfer:
            return 1.0
        k_mpc = float(k_com) * self.hubble_h / HUBBLE_RADIUS_MPC
        return float(transfer_function(
            np.array([k_mpc]), gamma=self.transfer_gamma, h=self.hubble_h)[0])

    def check_k(self, k: float) -> None:
        r"""Raise if `k` is past what this environment's eta grid can resolve.

        `pipeline.run` has carried this guard since T-3. `build_environment` is
        a second entry point to the same physics and had none: it trusted its
        caller to pass the right $k_{\max}$, and in `figure_f7_frames.py` the
        caller passed the probe modes instead of the grid. The check belongs
        where both callers pass through, which is here.
        """
        if float(k) > self.k_max * (1.0 + 1e-9):
            samples = 6.0 * self.k_max / float(k)
            raise ValueError(
                f"this environment's eta grid was built for k_max={self.k_max:.1f} "
                f"and was asked for k={float(k):.1f}: {samples:.1f} samples per "
                f"j_l oscillation at that k, against the 6 required_n_eta "
                f"guarantees. Below 2 it is aliased and the spectrum comes back "
                f"smooth, plausible and wrong -- findings T-3 and T-34. Build the "
                f"environment with the k grid's maximum."
            )


def build_environment(
    k_max: float,
    *,
    omega_m: float = 1.0,
    omega_b_h2: float = 0.0224,
    n_eta: int | None = None,
    omega_lambda: float = 0.0,
    omega_r: float = 0.0,
    transfer_gamma: float = ANNALS_II_GAMMA,
    hubble_h: float = 0.5,
    apply_transfer: bool = True,
) -> TwoFrameEnvironment:
    r"""The $k$-independent half: background, recombination, potentials.

    $\mathcal H'$, $\rho$ and $p$ come from `background_fluid`, which derives all
    three from one expression so Appendix G cannot disagree with the
    $\Omega$'s. $R'=\mathcal HR$ is exact because $R\propto a$, so nothing here
    is splined except the potentials, whose derivative (179) needs anyway.
    """
    background = Background(omega_m=omega_m, omega_lambda=omega_lambda,
                            omega_r=omega_r)
    recombination = RecombinationHistory.build(background, omega_b_h2=omega_b_h2)
    eta_star = recombination.eta_star
    span = float(background.eta_0 - recombination.eta[0])
    n = required_n_eta(k_max, span) if n_eta is None else n_eta
    eta = np.linspace(recombination.eta[0], background.eta_0, n)

    phi_a, phi_h = potentials(background, eta)
    a = background.a_of_eta(eta)
    cH = background.conformal_hubble(a)
    rho, pressure, cH_prime = background_fluid(
        a, omega_m=omega_m, omega_lambda=omega_lambda, omega_r=omega_r)
    r = baryon_photon_ratio(a, omega_b_h2=omega_b_h2)

    kappa_prime = np.interp(eta, recombination.eta, recombination.kappa_prime)
    k_d = diffusion_scale(recombination, r_of_eta=np.zeros_like(recombination.eta))

    return TwoFrameEnvironment(
        background=background, recombination=recombination, eta=eta,
        eta_star=eta_star, a=a, conformal_hubble=cH,
        conformal_hubble_prime=cH_prime, rho=rho, pressure=pressure,
        phi_a=phi_a, phi_h=phi_h,
        phi_a_prime=potential_derivative(eta, phi_a),
        phi_h_prime=potential_derivative(eta, phi_h),
        r_baryon=r, r_baryon_prime=cH * r,
        kappa_prime=kappa_prime,
        kappa_second=np.gradient(kappa_prime, eta, edge_order=2),
        visibility=np.interp(eta, recombination.eta, recombination.visibility),
        k_max=float(k_max), transfer_gamma=float(transfer_gamma),
        hubble_h=float(hubble_h), apply_transfer=bool(apply_transfer),
        damping_k=float(k_d(eta_star)), omega_b_h2=omega_b_h2,
    )


def coefficient_sets(
    k_com: float, env: TwoFrameEnvironment
) -> tuple[CoefficientSet, CoefficientSet]:
    r"""`(newtonian, cdm)` at one $k$, from the same acoustic solution.

    **Both frames are built from one integration of the acoustic pair**, which
    is the point: the frames differ by the frame, not by the dynamics, so a
    difference between them that came from two separate integrations would be a
    difference between two integrations.

    Every caller reaches the $\eta$ grid through here, so this is where the grid
    is checked against the $k$ it is being used at --- finding **T-34**.
    """
    env.check_k(k_com)
    eta, eta_star, bg = env.eta, env.eta_star, env.background

    # **T(k) enters here, before the acoustic integration --- finding T-37.**
    # Not afterwards, and not folded into the primordial power: Phi *drives* the
    # oscillation, so a suppression applied to the output would damp the
    # amplitude while leaving the driving un-suppressed. T is independent of
    # eta, so scaling Phi and Phi' by the same number is exact rather than an
    # approximation to a time-dependent transfer.
    t_k = env.transfer_at(k_com)
    phi_a, phi_h = env.phi_a * t_k, env.phi_h * t_k
    phi_a_prime, phi_h_prime = env.phi_a_prime * t_k, env.phi_h_prime * t_k

    inside = eta <= min(float(bg.eta_0), TIGHT_COUPLING_FACTOR * eta_star)
    acoustic = solve_acoustic(
        float(k_com), eta[inside], background=bg,
        phi_a=phi_a[inside], phi_h=phi_h[inside],
        omega_b_h2=env.omega_b_h2, expansion_coupling=False)

    def freeze(values: np.ndarray) -> np.ndarray:
        out = np.empty_like(eta)
        out[inside], out[~inside] = values, values[-1]
        return out

    delta_t, tau_1 = freeze(acoustic.delta_T), freeze(acoustic.tau_1)
    shared = dict(
        delta_t=delta_t, phi_a=phi_a, phi_a_prime=phi_a_prime,
        phi_h_prime=phi_h_prime, tau_1=tau_1, kappa_prime=env.kappa_prime,
        kappa_double_prime=env.kappa_second, conformal_hubble=env.conformal_hubble,
        r_baryon=env.r_baryon, r_baryon_prime=env.r_baryon_prime)

    newtonian = newtonian_set(eta, float(k_com), **shared)
    shift = cdm_frame_shift(eta, phi_a, float(k_com), background=bg)
    cdm = cdm_set(
        eta, float(k_com), phi_h=phi_h,
        conformal_hubble_prime=env.conformal_hubble_prime, scale_factor=env.a,
        rho=env.rho, pressure=env.pressure, v=shift.v, v_prime=shift.v_prime,
        eta_star=eta_star, **shared)
    return newtonian, cdm


#: Which coefficients each rank keeps. Everything else is zeroed, so the three
#: evaluations are the *same* call to (102) with a mask, not three formulas.
_RANK_KEEPS = {0: ("c0",), 1: ("c1",), 2: ("c2",)}


def transfer_by_rank(
    ells: np.ndarray,
    k_com: float,
    coefficients: CoefficientSet,
    env: TwoFrameEnvironment,
    table: BesselTable,
) -> dict[int, np.ndarray]:
    r"""(102)'s transfer split into its rank-0, rank-1 and rank-2 parts.

    The three **add to the total exactly**, because (102) is linear in the
    $C_A$: the boundary scalar carries $C_2'(\eta_*)-C_1(\eta_*)$, the boundary
    shear carries $C_2(\eta_*)$ and the integrand carries $C_0-C_1'+C_2''$, and
    every one of those is a sum of terms each belonging to one rank. `tests/`
    asserts the sum rather than trusting the reading.

    Returned under keys `0`, `1`, `2` and `-1` for the total.
    """
    diffusion = float(np.exp(-((float(k_com) / env.damping_k) ** 2)))
    common = dict(table=table, weight=env.visibility, diffusion=diffusion,
                  damping_total=diffusion, eta_star=env.eta_star,
                  eta_0=float(env.background.eta_0))
    zero = np.zeros_like(env.eta)

    out: dict[int, np.ndarray] = {}
    for rank, keeps in _RANK_KEEPS.items():
        masked = replace(
            coefficients.coefficients,
            **{name: (getattr(coefficients.coefficients, name) if name in keeps
                      else zero) for name in ("c0", "c1", "c2")})
        out[rank] = integral_solution(
            ells, coefficients=masked,
            c1_prime=coefficients.c1_prime if rank == 1 else zero,
            c2_second=coefficients.c2_second if rank == 2 else zero,
            c2_prime_star=coefficients.c2_prime_star if rank == 2 else 0.0,
            **common).total
    out[-1] = integral_solution(
        ells, coefficients=coefficients.coefficients,
        c1_prime=coefficients.c1_prime, c2_second=coefficients.c2_second,
        c2_prime_star=coefficients.c2_prime_star, **common).total
    return out


def cl_cross(
    ell: int, k_com: np.ndarray, transfer_a: np.ndarray, transfer_b: np.ndarray,
    power: np.ndarray,
) -> float:
    r"""$C_\ell^{AB}$, the cross-spectrum of two transfer functions.

    Formed by polarisation --- $\tfrac12[C_\ell(A+B)-C_\ell(A)-C_\ell(B)]$ ---
    so that it uses `cl_covariant_route` and nothing else. Writing the bilinear
    form out again here would be a second place for (188)'s $\Delta_\ell/(4\pi)$
    to be misread, and it has been misread once already.
    """
    a, b = np.asarray(transfer_a, dtype=float), np.asarray(transfer_b, dtype=float)
    return 0.5 * (cl_covariant_route(int(ell), k_com, a + b, power)
                  - cl_covariant_route(int(ell), k_com, a, power)
                  - cl_covariant_route(int(ell), k_com, b, power))
