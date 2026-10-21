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
from functions.spectra.acoustic import (
    TIGHT_COUPLING_FACTOR as ACOUSTIC_TIGHT_COUPLING_FACTOR,
    acoustic_start_eta,
    required_acoustic_points,
    sound_horizon_from_zero,
    baryon_photon_ratio, solve_acoustic,
)
from functions.spectra.angular import cl_covariant_route
from functions.spectra.bessel_table import BesselTable
from functions.spectra.coefficients import (
    CoefficientSet,
    background_fluid,
    cdm_set,
    newtonian_set,
)
from functions.spectra.decoupling import (
    F2_DEFAULT,
    RecombinationHistory,
    diffusion_scale,
)
from functions.spectra.frame_transform import cdm_frame_shift
from functions.spectra.integral_solution import integral_solution
from functions.spectra.pipeline import N_ETA_FLOOR, required_n_eta
from functions.spectra.potentials import (
    matter_domination_eta,
    potential_derivative,
    potentials,
)
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

#: The tight-coupling window. **Re-exported, not defined here** --- finding
#: **T-58**: it was defined in three places with three values, and
#: `functions.spectra.acoustic` is now the one that has it.
TIGHT_COUPLING_FACTOR = ACOUSTIC_TIGHT_COUPLING_FACTOR


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
    #: $e^{-\kappa}$ on the same grid. Carried so that **A-2** is a choice a
    #: caller can make and measure rather than one baked in --- finding T-41.
    opacity: np.ndarray
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
    #: **Approximation A-2, and the default is the one this project already
    #: chose on 2026-10-06 --- findings T-41 and T-42.**
    #:
    #: `provenance/SOURCE-APPROXIMATIONS-v1.md` records A-2 in full: weighting
    #: the integrated sources with $\mathcal V=\kappa'e^{-\kappa}$, as (178)
    #: prints it, gives $D_\ell\propto\ell^2$ --- *"there is no Sachs--Wolfe
    #: plateau at all"* --- while $e^{-\kappa}$, **as (98) prints it**, is flat
    #: to 30% over $2\le\ell\le20$. Both forms are the antecedent's, (98) is the
    #: earlier and less approximated, and **the bundle took (98)**.
    #:
    #: `pipeline` has carried that since the day it was found. **This path was
    #: written afterwards and passed $\mathcal V$**, reintroducing the defect by
    #: default --- finding **T-42**. Re-measured here: the rise from $\ell=2$ to
    #: 30 is **80.5x** with $\mathcal V$ and **8.17x** with $e^{-\kappa}$.
    #:
    #: `"opacity"` is therefore the default. `"printed"` reproduces (178)
    #: exactly and exists so the departure stays visible and measurable, which
    #: is what `source_doppler` and `source_integrated` already do.
    #:
    #: **Finding T-57, 2026-10-17. The paragraph above was written and the
    #: default below was not changed.** For eleven days this field read
    #: `"printed"` while its own documentation said `"opacity"` --- so every
    #: caller that did not name the weight took $\mathcal V$, and none of the
    #: eight named it. F2, F5, F7, F9, D6, D7, `compare_criterion_5b` and the
    #: benchmark all ran under the weighting A-2 says the bundle departs from.
    #: Measured on `PLANCK_MODEL` before the change: the rank-one (Doppler)
    #: sector is **100.5% of the transfer at every $2\le\ell\le100$**, against
    #: **0.1%** under $e^{-\kappa}$, and $D_2/D_{30}$ moves from 0.0082 to
    #: 0.0895 on the switch alone.
    #:
    #: **A docstring is not an executable decision.** T-41/T-42 were recorded,
    #: the reasoning was written out in full, and the one-line change was
    #: missed; nothing in the bundle could see the gap because no gate compared
    #: a default against the prose above it. `check_release_hygiene.py` now
    #: requires every released caller to name this argument, which is the
    #: enforcement A-1 asked for in words --- *"the caller states which"* ---
    #: and never had.
    #: **Finding T-69, 2026-10-19 --- flipped back to the antecedent.**
    #: A-2's basis is void. The measurement that justified departing from
    #: (102)'s printed $\mathcal V$ was taken **before T-66**, when
    #: $\kappa'\tilde v_B$ was too large by $k_{\rm com}$ --- and the object
    #: that destroyed the plateau is exactly
    #: $\mathcal V\kappa'\sim\kappa'^2e^{-\kappa}$, which T-66 divided by $k$.
    #: Re-measured on all three backgrounds, the $\mathcal V$ row no longer
    #: rises ($4.29\to1212$ became $0.371\to0.008$: the trend **reversed**),
    #: and on the one criterion that separates the two weights --- **does the
    #: spectrum have acoustic structure** --- $\mathcal V$ has interior maxima
    #: on **3 of 3** backgrounds and $e^{-\kappa}$ on **0 of 3**.
    #:
    #: This bundle's rule is reproduce the antecedent unless there is a
    #: measured reason to depart. The measured reason has evaporated, so the
    #: default returns to what (102) prints. **`"opacity"` is retained as the
    #: named control**, exactly as it was the default before.
    line_of_sight_weight: str = "printed"
    #: **Finding T-51, decision S40.** `"derived"` starts each mode where
    #: $k\,r_s(\eta)\le\varepsilon$; `"z_max"` starts every mode at the first
    #: point of the recombination grid, which is what this route did until
    #: 2026-10-16 and what discarded 51--64% of the sound horizon. **The defect
    #: had one instance per route** --- here, in `pipeline.run` and in
    #: `two_route` --- and all three began in the same place, which is why no
    #: comparison among them could see it. T-3's lesson, in triplicate.
    acoustic_start: str = "derived"
    #: The tabulated $r_s(\eta)$ from the big bang, and the single reference
    #: $\Phi_A$ is normalised at. `None` only on an environment built before
    #: these existed, which nothing now does.
    eta_rs: np.ndarray | None = None
    r_s_table: np.ndarray | None = None
    md_reference: float = 0.0

    @property
    def weight(self) -> np.ndarray:
        """The line-of-sight weight this environment was built to carry."""
        if self.line_of_sight_weight == "opacity":
            return self.opacity
        if self.line_of_sight_weight == "printed":
            return self.visibility
        raise ValueError(
            f"line_of_sight_weight must be 'opacity' (e^-kappa, as (98) "
            f"prints it, and this project's choice since 2026-10-06) or "
            f"'printed' (V, as (178) prints it, which has no Sachs-Wolfe "
            f"plateau); got {self.line_of_sight_weight!r}. See approximation "
            f"A-2 and findings T-41 and T-42.")

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
    f_2: float = F2_DEFAULT,
    line_of_sight_weight: str = "printed",
    acoustic_start: str = "derived",
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
    # **The floor is applied here too --- finding T-58.** `required_n_eta` is
    # the rate the $j_\ell$ oscillation demands at $k_{\max}$; `N_ETA_FLOOR` is
    # what the *recombination* structure demands near $\eta_*$, which no
    # function in this bundle yet derives (S33). `two_route` has carried the
    # floor since T-45 and this path did not, so an environment built at a
    # modest $k_{\max}$ was under-resolved where the visibility lives rather
    # than where the Bessel function oscillates. Measured against `two_route`'s
    # (177)--(179) column at $k=10$: **2.4e-01 without the floor, 5.9e-03 with
    # it** --- a factor of forty, from a grid that looked derived.
    n = max(N_ETA_FLOOR, required_n_eta(k_max, span)) if n_eta is None else n_eta
    eta = np.linspace(recombination.eta[0], background.eta_0, n)

    # **T-51/S40.** r_s from the big bang, and the one reference Phi_A is
    # normalised at, so that every mode shares a Phi_A(0,k) however early it
    # starts. Equality for a background with radiation; for Omega_r = 0 there
    # is no equality and the r_s table's own floor serves.
    eta_rs, r_s_table = sound_horizon_from_zero(
        background, float(eta_star), omega_b_h2=omega_b_h2)
    md_reference = float(recombination.eta[0])
    derived = str(acoustic_start) == "derived"
    if str(acoustic_start) not in ("derived", "z_max"):
        raise ValueError("acoustic_start is 'derived' (S40) or 'z_max' (the control)")

    phi_a, phi_h = (potentials(background, eta, constant_below=md_reference)
                    if derived else potentials(background, eta))
    a = background.a_of_eta(eta)
    cH = background.conformal_hubble(a)
    rho, pressure, cH_prime = background_fluid(
        a, omega_m=omega_m, omega_lambda=omega_lambda, omega_r=omega_r)
    r = baryon_photon_ratio(a, omega_b_h2=omega_b_h2)

    kappa_prime = np.interp(eta, recombination.eta, recombination.kappa_prime)
    k_d = diffusion_scale(recombination, r_of_eta=np.zeros_like(recombination.eta),
                          f_2=f_2)

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
        opacity=np.interp(eta, recombination.eta, recombination.opacity),
        line_of_sight_weight=str(line_of_sight_weight),
        acoustic_start=str(acoustic_start), eta_rs=eta_rs,
        r_s_table=r_s_table, md_reference=float(md_reference),
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

    eta_couple = min(float(bg.eta_0), TIGHT_COUPLING_FACTOR * eta_star)
    inside = eta <= eta_couple

    if env.acoustic_start == "derived":
        # **T-51/S40: the start is k's, not z_max's, and so is the grid.**
        # T(k) still multiplies Phi *before* the integration (finding T-37) ---
        # it is independent of eta, so scaling the mode's own potentials by the
        # same number is exact.
        start = acoustic_start_eta(float(k_com), env.eta_rs, env.r_s_table)
        mode_eta = np.linspace(
            start, eta_couple, required_acoustic_points(float(k_com), eta_couple - start))
        mode_a, mode_h = potentials(bg, mode_eta, constant_below=env.md_reference)
        acoustic = solve_acoustic(
            float(k_com), mode_eta, background=bg,
            phi_a=mode_a * t_k, phi_h=mode_h * t_k,
            omega_b_h2=env.omega_b_h2, expansion_coupling=False)
        # `np.interp` holds the end value past `eta_couple`, which **is** the
        # freeze the tight-coupling window calls for.
        delta_t = np.interp(eta, mode_eta, acoustic.delta_T)
        tau_1 = np.interp(eta, mode_eta, acoustic.tau_1)
    else:
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


#: **The B-slot repair --- finding T-88. `False` is the released behaviour.**
#:
#: With this on, `transfer_by_rank` gives $C_1$'s gravitational half the weight
#: $W=e^{-\kappa}$, gives its Thomson half $g=\mathcal V$ **carrying
#: $\hat v_B + C_2$ together** (T-82's boost-invariant pair, which the first
#: attempt separated and which is why that attempt failed), and supplies the
#: $+k\int W M j_\ell'$ bulk slot (102) has no counterpart for.
#:
#: **T-88 IS WITHDRAWN AND SO IS ITS RESULT.** This docstring read, until
#: 2026-10-21, that the flag *"closes the frame gap by up to four orders at
#: $\ell\ge50$ for $k\lesssim60$"*. **That number is void**: `slot_weight_split`
#: applied $\mathcal V\,C_1^{\rm thom}$ where (102) applies $W\,C_1^{\rm thom}$,
#: and since $W\kappa'=\mathcal V$ is an *identity* that is a spurious factor of
#: $\kappa'$, measured at **320--682** (**T-93**). The peak shift T-92 reported
#: with it went too. The withdrawal was recorded in the supplement within hours
#: and **not here**, so a reader of this module alone got the pre-withdrawal
#: reading for a day --- finding **T-103**'s class, and **S46**'s reason for
#: requiring that a withdrawal reach the public artefacts in the same commit.
#:
#: **It stays a control and not a default**, now for a structural reason rather
#: than a measured one: **T-101** shows every one of this file's controls
#: redistributes weights while leaving $\kappa'$ inside $C_1$ and leaving the
#: differentiation of $C_1$ in place, so none can be clean by `c7`'s grade.
#: The target assembly is the $W$-form --- decision **S48** --- which has no
#: coefficients to carry $\kappa'$ at all. Weight defaults still follow
#: **S43**: a default that encodes an approximation is named at every call site.
B_SLOT_REPAIR: bool = False


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
    # **`eta_floor` is stated here, not defaulted --- finding T-58.**
    # `integral_solution`'s default is (102)'s printed lower limit $\eta_*$,
    # and its docstring says the argument exists *"so the pipeline's
    # long-standing choice of integrating from the start of the recombination
    # history can be measured against the printed one rather than inherited"*.
    # `pipeline.run` and `two_route` both supply it; **this path did not, and
    # so inherited the printed limit by omission** --- T-57's class exactly, a
    # second instance, in the same file, found the same day.
    #
    # The recombination start is the physical limit: the visibility is peaked
    # *at* $\eta_*$ and half its support lies below, so a lower limit of
    # $\eta_*$ discards half the peak. Measured against `two_route`'s
    # (177)--(179) column with the window already matched, the omission alone
    # cost **2.2e-01 at k=1** --- the modes that build the Sachs-Wolfe
    # plateau --- and 8.1e-01 at k=10.
    # `visibility` is supplied beside `weight` because **T-72**'s rank-two
    # by-parts terms carry $\mathcal V$ regardless of which weight the caller
    # chose for the main bracket: they come from differentiating
    # $W=e^{-\kappa}$, not from A-2's choice.
    common = dict(table=table, weight=env.weight, diffusion=diffusion,
                  damping_total=diffusion, eta_star=env.eta_star,
                  eta_floor=float(env.eta[0]),
                  visibility=env.visibility,
                  eta_0=float(env.background.eta_0))
    if B_SLOT_REPAIR:
        # C_1's Thomson half and its derivative, from the stored primitives:
        # -C_1 = (dT + Phi_A) + kappa' vhat_B with vhat_B = v_B / k, and
        # `v_b` is the UN-reduced v_B (T-66). The derivative comes from (107),
        # -C_1' = (kappa' vhat_B)' + (a B_1)'/k, never from differentiating a
        # stored amplitude -- finding T-23.
        kp = np.asarray(env.kappa_prime, dtype=float)
        v_b = np.asarray(coefficients.v_b, dtype=float)
        a_b1_prime = np.asarray(coefficients.a_b1_prime, dtype=float)
        common.update(
            opacity=env.opacity,
            c1_thomson=-(kp * v_b / float(k_com)),
            c1_thomson_prime=np.asarray(coefficients.c1_prime, dtype=float)
            + a_b1_prime / float(k_com),
            c1_thomson_kappa=kp,
            slot_weight_split=True, jprime_bulk_slot=True,
            thomson_carries_shear=True, boundary_weight_w=False)
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
            c2_prime=coefficients.c2_prime if rank == 2 else None,
            **common).total
    out[-1] = integral_solution(
        ells, coefficients=coefficients.coefficients,
        c1_prime=coefficients.c1_prime, c2_second=coefficients.c2_second,
        c2_prime_star=coefficients.c2_prime_star,
        c2_prime=coefficients.c2_prime, **common).total
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
