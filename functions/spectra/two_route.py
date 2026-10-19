r"""One mode, computed twice: (102) generically, and (177)--(179) assembled.

**What this module is for.** Decision **S26** put an *audit* half in v1.2.0
beside the reproduction half, and this is the audit's executable form. *Annals
II* writes its integral solution twice --- once as (102), carried with a generic
$u^a$ and specialised afterwards, and once as the source assembly (177)--(179),
already in the Newtonian frame. They are the same calculation written in two
orders, and **the paper says so**: *"Later we will explicitly recover these
equations in the Newtonian frame of section (newtg)"*, and, at the end of that
recovery, *"This completes the recovery of the standard integral solution
results using the 1+3 CGI approach at linear order"*.

That recovery is carried out **symbolically**, on the page, as it should be.
What has never been done is to *evaluate* both forms and compare them, and a
symbolic recovery is an argument whose arithmetic nobody has run --- which is
what this bundle exists to supply.

Here it is checked, mode by mode, and the check is what criterion **5b** is
gated on (decision **S4c**).

**What is held fixed, stated rather than left to be noticed.** Both routes are
given, identically:

* the same background and the same $\eta$ grid;
* the same recombination history, so the same $\kappa'$, visibility and $\eta_*$;
* the same acoustic solution --- one call to `solve_acoustic`, whose $\delta T$
  and $\tau_1$ both routes read;
* the same potentials and the same Bessel table;
* the same diffusion damping;
* **the same line-of-sight weight, $e^{-\kappa}$, on both sides.**

That last one is deliberate and is the reason this comparison is stated at the
transfer level at fixed $k$ rather than at $C_\ell$. (102) *prints*
$\mathcal V=\kappa'e^{-\kappa}$ and (98) prints $e^{-\kappa}$; approximations
**A-1** and **A-2** record the difference, and it is large --- at $C_\ell$ the
two branches differ by a factor of eighty in the Sachs--Wolfe plateau for that
reason alone. Weighting both sides the same way removes the one thing this
comparison is *not* about, so that what is left is the assembly algebra.

**What a shared input cannot establish --- finding T-3.** A comparison that
holds an input fixed cannot check that input. This module therefore establishes
that the generic assembly and the Newtonian assembly agree; it establishes
nothing about the background, the recombination history, the acoustic solution,
the weighting choice, or whether any of them matches nature. Those are checked
elsewhere, each against something it did not come from, and the list above is
written out so that the boundary is readable rather than inferred.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import CubicSpline

from functions.background.flrw import LCDM_MODEL, Background
from functions.spectra.acoustic import (
    TIGHT_COUPLING_FACTOR,
    acoustic_start_eta,
    required_acoustic_points,
    solve_acoustic,
    sound_horizon_from_zero,
)
from functions.spectra.bessel_table import BesselTable
from functions.spectra.coefficients import (
    newtonian_c1_prime, newtonian_coefficients, reduce_dipole)
from functions.spectra.decoupling import RecombinationHistory, diffusion_scale
from functions.spectra.integral_solution import integral_solution, required_multipoles
from functions.spectra.pipeline import (
    N_ETA_FLOOR as PIPELINE_N_ETA_FLOOR,
    required_n_eta,
)
from functions.spectra.potentials import matter_domination_eta, potentials
from functions.spectra.sources import (
    PUBLISHED_ISW_SIGN,
    PerturbationHistory,
    ScatteringHistory,
    source_doppler,
    source_integrated,
    source_primary,
)

__all__ = ["TwoRoute", "two_route_transfer"]

#: Floor on the $\eta$ grid. **Re-exported, not defined here** --- finding
#: **T-58**: `two_frame` never had this floor and that was most of what was
#: left of **Q12**. `functions.spectra.pipeline` now owns it, beside the
#: `required_n_eta` whose rate it floors, and carries T-45's measurement.
N_ETA_FLOOR = PIPELINE_N_ETA_FLOOR

#: Samples per oscillation, and **four times what the $C_\ell$ route uses**.
#:
#: `ETA_POINTS_PER_PERIOD` is 12, set so that the line-of-sight quadrature
#: converges. That is the right number for a spectrum and the wrong one here,
#: for a reason worth stating: this comparison does not measure either route's
#: quadrature error, it measures **the difference between them**. The two routes
#: group the same integrand differently --- (102) carries $C_A$ with the
#: boundary terms $c_1'$ and $c_2''$, (177)--(179) carries a primary term plus
#: one line-of-sight integral --- so their trapezoid errors are different
#: functions of the grid and do not cancel when subtracted. At twelve samples
#: the difference at $k=600$ is $2\times10^{-2}$ and falls like $1/n$ thereafter:
#: a *quadrature* residual, which is exactly what it should be once the algebra
#: is right, and which must be pushed down rather than gated around.
POINTS_PER_PERIOD = 48

#: **The acoustic solution runs the whole span; it is not frozen after
#: decoupling.** Freezing it at $6\eta_*$ and holding the last value is the
#: cheaper thing and was done first. It introduces a step whose height is
#: whatever the oscillator happened to be doing at the last grid point inside
#: the window, so it *moves with the grid* --- and the two routes carry the
#: frozen tail through different groupings, so the step does not cancel between
#: them. It cost a factor of three in the measured difference at $k=60$ and
#: made the comparison non-monotone in the grid. Running the oscillator on costs
#: about 0.4 s per mode and removes a harness artefact from a gate, which is a
#: good trade at any price.


@dataclass(frozen=True)
class TwoRoute:
    """Both routes at one $k$, and the difference between them."""

    k: float
    ells: np.ndarray
    pipeline: np.ndarray
    generic: np.ndarray
    #: The $\eta$ grid this mode was actually given, derived from $k$. Reported
    #: rather than assumed, which is S24's accuracy-certificate argument applied
    #: to the one comparison that gates a criterion.
    n_eta: int = 0

    @property
    def scale(self) -> float:
        r"""The largest $|\Delta_\ell(k)|$ this mode produces, over $\ell$."""
        return float(np.max(np.abs(self.pipeline)))

    @property
    def relative(self) -> np.ndarray:
        r"""$|\Delta^{(102)}_\ell-\Delta^{(177)}_\ell|$ over the row's own scale.

        **Normalised by the largest transfer the mode produces, not pointwise.**
        That choice is the difference between a measurement and an artefact, and
        it has two independent reasons.

        *Zero crossings.* $\Delta_\ell(k)$ oscillates in $\ell$ and passes
        through zero. On `PLANCK_MODEL` at $k=120$ the two routes differ by
        $8\times10^{-5}$ in absolute value at **every** $\ell$ --- uniformly ---
        but $\Delta_{50}=-0.0075$ sits forty times below $\Delta_2$, so a
        pointwise ratio reports 1.1% there and $3\times10^{-5}$ beside it. The
        1.1% is the distance to a zero, not an error. Normalising by the row's
        scale returns $2.9\times10^{-4}$ at every $\ell$, which is what is
        actually true of the comparison.

        *The exponential tail.* Below the Bessel turning point $x\simeq\ell$ the
        transfer is numerically zero --- $5\times10^{-61}$ at $\ell=50,k=0.3$,
        and exactly $0$ at $\ell=600$ --- so a pointwise ratio there divides
        noise by noise or zero by zero and returns `nan`. Those modes
        contribute nothing to $C_\ell=\int\Delta_\ell^2P\,dk$, and against the
        row's scale they contribute nothing here either, which is the same
        statement arrived at honestly.

        The scale is the right denominator on its own terms and not only as a
        repair: $C_\ell$ is built from $\Delta_\ell^2$ integrated over $k$, so
        an error measured against the largest transfer a mode produces is the
        error that reaches the spectrum.
        """
        scale = self.scale
        # A row whose transfer is identically zero at every multipole has an
        # empty domain. It must raise rather than return `nan`, because
        # `nan >= gate` is `False` and a gate fed one takes the passing branch
        # --- finding **T-44**.
        if scale <= 0.0:
            raise ValueError(
                f"at k={self.k:g} the transfer is zero at every multipole, so "
                "there is nothing to compare. A comparison with an empty "
                "domain is not a passing comparison")
        return np.abs(self.generic - self.pipeline) / scale

    @property
    def worst(self) -> float:
        return float(np.max(self.relative))


def two_route_transfer(
    k: float,
    ells: np.ndarray,
    *,
    background: Background = LCDM_MODEL,
    omega_b_h2: float = 0.0224,
    points_per_period: int = POINTS_PER_PERIOD,
    match_interpolation: bool = True,
) -> TwoRoute:
    r"""$\Delta_\ell(k)$ by (102) generically and by (177)--(179) assembled.

    One setup, read by both. Every shared input is built once here so that the
    sharing is a property of the code rather than a thing the caller has to get
    right twice --- two setups with one rule cannot drift, which is `_bundle_files`'
    argument applied to a measurement.
    """
    ells = np.asarray(ells)
    bg = background
    rec = RecombinationHistory.build(bg, omega_b_h2=omega_b_h2)
    n_eta = max(N_ETA_FLOOR,
                required_n_eta(float(k), float(bg.eta_0 - rec.eta[0]),
                               points_per_period=points_per_period))
    eta = np.linspace(rec.eta[0], bg.eta_0, n_eta)
    # **T-51/S40, the third instance.** This gate's two routes share one
    # acoustic solution by construction --- that is what makes it a test of the
    # *assembly algebra* --- so a start at `rec.eta[0]` moved both together and
    # cancelled exactly. Criterion 5b sat at 9.5e-06 while half the sound
    # horizon was missing from both sides of it. **S4c says a self-comparison
    # cannot see a shared antecedent; this is the sharpest instance of it the
    # bundle has.** The start is derived here too, so the gate measures the
    # algebra on the physics the bundle actually computes.
    eta_rs, r_s_table = sound_horizon_from_zero(
        bg, float(rec.eta_star), omega_b_h2=omega_b_h2)
    md_reference = float(rec.eta[0])
    phi_a, phi_h = potentials(bg, eta, constant_below=md_reference)
    aH = bg.conformal_hubble(bg.a_of_eta(eta))
    kp = np.interp(eta, rec.eta, rec.kappa_prime)
    vis = np.interp(eta, rec.eta, rec.visibility)
    opa = np.interp(eta, rec.eta, rec.opacity)
    k_d = float(diffusion_scale(rec, r_of_eta=rec.kappa_prime * 0.0)(rec.eta_star))

    # **T-58.** This read `float(eta[-1])` --- $\eta_0$ --- until 2026-10-17,
    # so the gate's acoustic solve kept the photon-baryon fluid oscillating for
    # 7.6x the span over which it is a fluid, while `pipeline.run` and
    # `two_frame` both stopped at `TIGHT_COUPLING_FACTOR * eta_star` and held
    # the last value. **The route that gates criterion 5b was the one route
    # without a tight-coupling window.** 5b could not see it because both its
    # columns are built from this one solve and shared it; measured against
    # `two_frame`, the mismatch alone cost 1.5e-01 at k=3 and 1.6e+00 at k=10,
    # against 5b's own 5e-08.
    eta_couple = min(float(bg.eta_0), TIGHT_COUPLING_FACTOR * float(rec.eta_star))
    start = acoustic_start_eta(float(k), eta_rs, r_s_table)
    mode_eta = np.linspace(
        start, eta_couple, max(int(n_eta), required_acoustic_points(float(k), eta_couple - start)))
    mode_a, mode_h = potentials(bg, mode_eta, constant_below=md_reference)
    ac = solve_acoustic(k, mode_eta, background=bg, phi_a=mode_a, phi_h=mode_h,
                        omega_b_h2=omega_b_h2, expansion_coupling=False)
    delta_t = np.interp(eta, mode_eta, ac.delta_T)
    tau_1 = np.interp(eta, mode_eta, ac.tau_1)

    needed = required_multipoles(ells)
    table = BesselTable.build(ell_max=int(needed.max()), ells=needed,
                              x_max=k * (bg.eta_0 - eta[0]) + 20.0)
    scattering = ScatteringHistory(eta=eta, kappa_prime=kp, visibility=vis,
                                   damping_k=k_d)
    damping = scattering.diffusion(k)

    # ---- route one: (177)-(179), assembled in the Newtonian frame ---------
    # **T-66**: v_b is the reduced v~_B = v_B/k that (177)/(178) want; tau_1
    # stays velocity-normalised, which is what (178)'s (1/3) k tau~_1 wants.
    history = PerturbationHistory(eta=eta, delta_T=delta_t, phi_a=phi_a,
                                  phi_h=phi_h, tau_1=tau_1,
                                  v_b=reduce_dipole(tau_1, k),
                                  frame="newtonian")
    primary = source_primary(history, scattering, damping_total=damping)
    # **The one place the two routes are not reading the same way.** (102)'s
    # boundary term is `CubicSpline(eta, c_1)(eta_star)` inside
    # `integral_solution`; `pipeline.run` reads its primary term with
    # `np.interp` --- linear --- at the same point. On the same grid the two
    # arrays are pointwise identical, so with the same interpolant the boundary
    # terms agree to machine precision and what is left is the algebra. With
    # different interpolants they differ by $1.1\times10^{-4}$ of the source,
    # and that difference, not the algebra, is then most of what the comparison
    # reports. It is **not** the eta grid's doing: refining eta sixteen-fold
    # barely moves it, while refining the *recombination* grid fourfold removes
    # it --- finding **T-46**, which is the larger thing this comparison found.
    #
    # `match_interpolation=True` is the gate: it compares the assemblies. The
    # `False` branch is kept because the as-shipped difference is a real number
    # about this bundle and is reported beside the gate rather than hidden by it.
    star = (float(CubicSpline(eta, primary)(rec.eta_star)) if match_interpolation
            else float(np.interp(rec.eta_star, eta, primary)))
    integrated = (source_doppler(history, scattering, k, weight=opa)
                  + source_integrated(history, scattering, k, aH=aH,
                                      isw_sign=PUBLISHED_ISW_SIGN, weight=opa))
    x, x_star = k * (bg.eta_0 - eta), k * (bg.eta_0 - rec.eta_star)
    pipeline = np.array([
        star * float(table(int(l), np.array([x_star]))[0])
        + float(np.trapezoid(integrated * table(int(l), x), eta)) for l in ells])

    # ---- route two: (102), carried generically, specialised at the end ----
    # **T-66**, route two: the same reduction route one now makes. Both routes
    # reached the dipole through their own line, which is why no comparison
    # between them could see this -- T-3's lesson, in duplicate again.
    vb_t = reduce_dipole(tau_1, k)
    coefficients = newtonian_coefficients(eta, k, delta_t=delta_t, phi_a=phi_a,
                                          kappa_prime=kp, v_b=vb_t)
    c1_prime = newtonian_c1_prime(
        eta, k, delta_t=delta_t, phi_a=phi_a,
        phi_a_prime=CubicSpline(eta, phi_a).derivative(1)(eta),
        phi_h_prime=CubicSpline(eta, phi_h).derivative(1)(eta),
        tau_1=tau_1, conformal_hubble=aH,
        kappa_prime_v_b_prime=CubicSpline(eta, kp * vb_t).derivative(1)(eta))
    generic = integral_solution(
        ells, coefficients=coefficients, table=table, weight=opa,
        diffusion=damping, damping_total=damping, eta_star=rec.eta_star,
        eta_0=bg.eta_0, c1_prime=c1_prime, eta_floor=float(eta[0])).total

    return TwoRoute(k=float(k), ells=ells, pipeline=pipeline, generic=generic,
                    n_eta=int(n_eta))
