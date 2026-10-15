r"""(102) carried generically, and finding **T-23**.

The acceptance condition for a covariant assembly is not that it is prettier
than the specialised one --- it is that **specialising it returns the
specialised one**. Decision S2's *restricted case which must recover v1.0.0's
numbers*, applied to the integral solution rather than to a release.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.interpolate import CubicSpline

from functions.background.flrw import LCDM_MODEL
from functions.spectra.acoustic import solve_acoustic
from functions.spectra.bessel_table import BesselTable
from functions.spectra.coefficients import (
    match_coefficients,
    newtonian_c1_prime,
    newtonian_coefficients,
)
from functions.spectra.decoupling import RecombinationHistory, diffusion_scale
from functions.spectra.integral_solution import (
    integral_solution,
    required_multipoles,
)
from functions.spectra.potentials import potentials
from functions.spectra.two_route import two_route_transfer
from functions.spectra.sources import (
    PUBLISHED_ISW_SIGN,
    PerturbationHistory,
    ScatteringHistory,
    source_doppler,
    source_integrated,
    source_primary,
)

K = 60.0
ELLS = np.array([2, 5, 10, 50, 200])


@pytest.fixture(scope="module")
def setup():
    bg = LCDM_MODEL
    rec = RecombinationHistory.build(bg, omega_b_h2=0.0224)
    eta = np.linspace(rec.eta[0], bg.eta_0, 4000)
    phi_a, phi_h = potentials(bg, eta)
    aH = bg.conformal_hubble(bg.a_of_eta(eta))
    kp = np.interp(eta, rec.eta, rec.kappa_prime)
    vis = np.interp(eta, rec.eta, rec.visibility)
    opa = np.interp(eta, rec.eta, rec.opacity)
    k_d = float(diffusion_scale(rec, r_of_eta=rec.kappa_prime * 0.0)(rec.eta_star))
    inside = eta <= 6.0 * rec.eta_star
    ac = solve_acoustic(K, eta[inside], background=bg, phi_a=phi_a[inside],
                        phi_h=phi_h[inside], omega_b_h2=0.0224,
                        expansion_coupling=False)

    def freeze(v):
        out = np.empty_like(eta)
        out[inside], out[~inside] = v, v[-1]
        return out

    d = dict(bg=bg, rec=rec, eta=eta, phi_a=phi_a, phi_h=phi_h, aH=aH,
             kp=kp, vis=vis, opa=opa, k_d=k_d,
             dT=freeze(ac.delta_T), t1=freeze(ac.tau_1))
    need = required_multipoles(ELLS)
    d["table"] = BesselTable.build(
        ell_max=int(need.max()), ells=need,
        x_max=K * (bg.eta_0 - eta[0]) + 20.0)
    return d


def _pipeline_transfer(s) -> np.ndarray:
    """What `pipeline.run` assembles, from (177)-(179)."""
    h = PerturbationHistory(eta=s["eta"], delta_T=s["dT"], phi_a=s["phi_a"],
                            phi_h=s["phi_h"], tau_1=s["t1"], v_b=s["t1"],
                            frame="newtonian")
    sc = ScatteringHistory(eta=s["eta"], kappa_prime=s["kp"],
                           visibility=s["vis"], damping_k=s["k_d"])
    damping = sc.diffusion(K)
    star = float(np.interp(s["rec"].eta_star, s["eta"],
                           source_primary(h, sc, damping_total=damping)))
    integrated = (source_doppler(h, sc, K, weight=s["opa"])
                  + source_integrated(h, sc, K, aH=s["aH"],
                                      isw_sign=PUBLISHED_ISW_SIGN,
                                      weight=s["opa"]))
    x = K * (s["bg"].eta_0 - s["eta"])
    x_star = K * (s["bg"].eta_0 - s["rec"].eta_star)
    return np.array([
        star * float(s["table"](int(l), np.array([x_star]))[0])
        + float(np.trapezoid(integrated * s["table"](int(l), x), s["eta"]))
        for l in ELLS])


def _generic_transfer(s, *, spline_the_amplitude: bool):
    eta, bg = s["eta"], s["bg"]
    c = newtonian_coefficients(eta, K, delta_t=s["dT"], phi_a=s["phi_a"],
                               kappa_prime=s["kp"], v_b=s["t1"])
    if spline_the_amplitude:
        c1p = CubicSpline(eta, c.c1).derivative(1)(eta)          # T-23's trap
    else:
        c1p = newtonian_c1_prime(
            eta, K, delta_t=s["dT"], phi_a=s["phi_a"],
            phi_a_prime=CubicSpline(eta, s["phi_a"]).derivative(1)(eta),
            phi_h_prime=CubicSpline(eta, s["phi_h"]).derivative(1)(eta),
            tau_1=s["t1"], conformal_hubble=s["aH"],
            kappa_prime_v_b_prime=CubicSpline(
                eta, s["kp"] * s["t1"]).derivative(1)(eta))
    sc = ScatteringHistory(eta=eta, kappa_prime=s["kp"], visibility=s["vis"],
                           damping_k=s["k_d"])
    damping = sc.diffusion(K)
    return integral_solution(
        ELLS, coefficients=c, table=s["table"], weight=s["opa"],
        diffusion=damping, damping_total=damping,
        eta_star=s["rec"].eta_star, eta_0=bg.eta_0,
        c1_prime=c1p, eta_floor=float(eta[0]))


def test_the_specialisation_recovers_what_the_pipeline_computes(setup):
    r"""**The acceptance condition.** $\tilde\sigma_{ab}=0$ collapses (102) to
    (110), and the transfer must be the one (177)--(179) give. The integrands
    are analytically identical; the residual is T-19's cancellation amplifying
    a $10^{-3}$ difference in the boundary value at $\eta_*$."""
    worst = np.max(np.abs(
        _generic_transfer(setup, spline_the_amplitude=False).total
        - _pipeline_transfer(setup)) / np.abs(_pipeline_transfer(setup)))
    assert worst < 5e-2, f"the generic form does not recover the pipeline: {worst:.2e}"


def test_t23_splining_the_amplitude_is_wrong_and_the_test_can_tell(setup):
    r"""**The negative control for T-23.** Without it, the test above is
    indistinguishable from the derivative not mattering. A spline through the
    stored amplitude misses the $2H\mathcal B_1$ the mode expansion carries,
    and the recovery fails by two orders of magnitude more."""
    ref = _pipeline_transfer(setup)
    bad = np.max(np.abs(_generic_transfer(setup, spline_the_amplitude=True).total
                        - ref) / np.abs(ref))
    good = np.max(np.abs(_generic_transfer(setup, spline_the_amplitude=False).total
                         - ref) / np.abs(ref))
    # Stated as a ratio, not a threshold: an absolute cut would be calibrated to
    # one eta grid and would drift with it, which is the failure T-16 names.
    assert bad > 10.0 * good, (
        f"splining the amplitude should wreck the recovery; it gave {bad:.2e} "
        f"against {good:.2e} for the published relation, so either T-23 is "
        f"wrong or this test is not exercising it")


def test_the_shear_boundary_term_is_empty_in_the_newtonian_frame(setup):
    """(102)'s second line multiplies C_2, which the Newtonian frame zeroes.
    No released figure has ever evaluated it."""
    assert _generic_transfer(setup, spline_the_amplitude=False).shear_boundary_is_empty


def test_the_shear_boundary_term_is_not_empty_once_b2_is(setup):
    """The control: it must switch on the moment the shear sector is occupied."""
    eta = setup["eta"]
    sigma = 0.02 * np.exp(-((eta - setup["rec"].eta_star) / 0.4) ** 2)
    c = match_coefficients(eta, K, a_b1=K * (setup["dT"] + setup["phi_a"]),
                           a_b2=sigma,
                           kappa_prime_v_b=K * setup["kp"] * setup["t1"],
                           frame="cdm")
    sc = ScatteringHistory(eta=eta, kappa_prime=setup["kp"],
                           visibility=setup["vis"], damping_k=setup["k_d"])
    sol = integral_solution(
        ELLS, coefficients=c, table=setup["table"], weight=setup["opa"],
        diffusion=sc.diffusion(K), damping_total=sc.diffusion(K),
        eta_star=setup["rec"].eta_star, eta_0=setup["bg"].eta_0,
        c1_prime=np.zeros_like(eta), c2_prime_star=1e-3,
        eta_floor=float(eta[0]))
    assert not sol.shear_boundary_is_empty
    assert np.any(sol.boundary_shear != 0.0)


def test_the_table_must_carry_the_neighbours(setup):
    r"""(102)'s rank-two term needs $j_{\ell\pm1}$. Since T-18 the table raises
    on a multipole it does not carry rather than returning a different one, so
    this is caught rather than silently wrong."""
    assert required_multipoles(np.array([10])).tolist() == [9, 10, 11]
    assert required_multipoles(np.array([2, 3])).tolist() == [1, 2, 3, 4]


def test_the_three_terms_are_kept_apart(setup):
    """C_l is quadratic in the source, so the pieces do not add. A solution
    object that only ever shows the sum cannot display T-19's cancellation."""
    sol = _generic_transfer(setup, spline_the_amplitude=False)
    assert np.allclose(sol.total,
                       sol.boundary_scalar + sol.boundary_shear + sol.integrated)
    assert not np.allclose(sol.boundary_scalar, sol.total)


def test_tau1_prime_from_152_agrees_with_differentiating_the_solution(setup):
    r"""**The control on the (152) route**, and a lesson about where to measure.

    $\tilde\tau_1'$ is taken from the printed mode-dipole equation rather than
    by differentiating the integrated $\tilde\tau_1$ --- T-23's discipline
    applied a second time. Measured where (152) is the equation being
    integrated and away from both ends of that interval, the two agree to
    $5\times10^{-9}$ worst and $2\times10^{-10}$ median. **That is the
    transcription checked to nine significant figures.**

    Both ends have to be excluded and both reasons are instructive.

    - **The right end.** `pipeline.run` *freezes* $\tau_1$ at $6\eta_*$, so at
      that one grid point the spline sees a slope discontinuity and returns the
      average of the real slope and zero --- exactly half. Measured across the
      whole window the worst disagreement is **11%**, at one point out of 730.
    - **The left end.** The recombination grid begins at $0.91\eta_*$, so the
      window opens on the acoustic solver's own starting boundary, where the
      spline has a startup transient of $2\times10^{-6}$ that has decayed by
      $\eta_*$.

    **A maximum taken over an interval containing a known discontinuity is a
    statement about the discontinuity.** It is the same error as a ratio taken
    at a zero crossing, and this test is written to not make it.
    """
    from scipy.interpolate import CubicSpline

    from functions.spectra.acoustic import baryon_photon_ratio
    from functions.spectra.coefficients import tau_1_prime

    s = setup
    eta, bg = s["eta"], s["bg"]
    eta_star = s["rec"].eta_star
    R = baryon_photon_ratio(bg.a_of_eta(eta), omega_b_h2=0.0224)
    printed = tau_1_prime(K, tau_1=s["t1"], delta_t=s["dT"], phi_a=s["phi_a"],
                          r_baryon=R,
                          r_baryon_prime=CubicSpline(eta, R).derivative(1)(eta))
    splined = CubicSpline(eta, s["t1"]).derivative(1)(eta)

    window = eta <= 6.0 * eta_star
    scale = np.max(np.abs(splined[window]))
    deviation = np.abs(printed - splined) / scale

    interior = window & (eta > eta_star) & (eta < 5.0 * eta_star)
    assert np.max(deviation[interior]) < 1e-7, (
        f"(152) disagrees with the integrated solution in the interior: "
        f"{np.max(deviation[interior]):.2e}")
    assert np.median(deviation[interior]) < 1e-8

    # The control on the exclusion: the freezing edge must dominate. Without
    # this, excluding it would be indistinguishable from excluding whatever
    # happened to fail.
    edge = window & (eta > 5.9 * eta_star)
    assert np.max(deviation[edge]) > 1e4 * np.max(deviation[interior]), (
        "the freezing discontinuity should dominate at the window edge; if it "
        "does not, this test is excluding the wrong region")


def test_102_runs_end_to_end_with_no_derivative_passed_in_by_hand(setup):
    r"""**(102) assembled entirely from published relations.**

    `newtonian_set` builds every input: $\tilde C_1$ from the (89) match,
    $\tilde C_1'$ from (106), $\tilde\tau_1'$ from (152), and
    $C_2=C_2'=C_2''=0$ identically because $\tilde\sigma_{ab}=0$. Nothing in the
    chain is splined except the background potentials, and the result must still
    be the transfer `pipeline.run` computes.

    This is the first time (102) runs with nothing taken on trust.
    """
    from scipy.interpolate import CubicSpline

    from functions.spectra.acoustic import baryon_photon_ratio
    from functions.spectra.coefficients import newtonian_set

    s = setup
    eta, bg = s["eta"], s["bg"]
    a = bg.a_of_eta(eta)
    R = baryon_photon_ratio(a, omega_b_h2=0.0224)
    sc = ScatteringHistory(eta=eta, kappa_prime=s["kp"], visibility=s["vis"],
                           damping_k=s["k_d"])
    cs = newtonian_set(
        eta, K, delta_t=s["dT"], phi_a=s["phi_a"],
        phi_a_prime=CubicSpline(eta, s["phi_a"]).derivative(1)(eta),
        phi_h_prime=CubicSpline(eta, s["phi_h"]).derivative(1)(eta),
        tau_1=s["t1"], kappa_prime=s["kp"],
        kappa_double_prime=sc.kappa_double_prime(),
        conformal_hubble=s["aH"], r_baryon=R,
        r_baryon_prime=CubicSpline(eta, R).derivative(1)(eta))

    assert np.all(cs.c2_second == 0.0), "the shear sector must be identically empty"

    damping = sc.diffusion(K)
    sol = integral_solution(
        ELLS, coefficients=cs.coefficients, table=s["table"], weight=s["opa"],
        diffusion=damping, damping_total=damping,
        eta_star=s["rec"].eta_star, eta_0=bg.eta_0,
        c1_prime=cs.c1_prime, c2_second=cs.c2_second,
        c2_prime_star=cs.c2_prime_star, eta_floor=float(eta[0]))

    ref = _pipeline_transfer(s)
    worst = np.max(np.abs(sol.total - ref) / np.abs(ref))
    assert worst < 5e-2, f"end-to-end (102) does not recover the pipeline: {worst:.2e}"
    assert sol.shear_boundary_is_empty


# --------------------------------------------------------------------------
# The recovery, across k. Finding T-41.
# --------------------------------------------------------------------------

K_SWEEP = (0.3, 1.0, 3.0, 10.0, 30.0, 120.0, 300.0)


@pytest.mark.parametrize("k", K_SWEEP)
def test_the_specialisation_recovers_the_pipeline_at_every_k_not_only_at_sixty(k):
    r"""**Finding T-41, and the correction of its first diagnosis.**

    `test_the_specialisation_recovers_what_the_pipeline_computes` runs at one
    mode, `K = 60.0`. When the two-frame path turned out to miss the
    Sachs--Wolfe plateau by a factor of eighty, the obvious suspicion was that
    the single mode was hiding it --- $k=60$ is in the acoustic regime, the
    line-of-sight integrated sector has its weight at low $k$, and $\ell=2$ is
    built almost entirely from that sector.

    **The suspicion was wrong, and this test is what showed it.** Swept from
    $k=0.3$ to $k=300$, the two routes agree at every mode and every $\ell$
    down to 2. (102) and (177)--(179) are the same calculation, and the one-mode
    test was not concealing anything.

    **The figure this docstring used to carry --- "$10^{-5}$ or better" --- was
    not measured.** It was read off a sweep on a fixed 4000-point $\eta$ grid,
    where both routes are still converging and happen to be un-converged in the
    same direction. `scripts/diagnostic_d8_criterion_5b_gate.py` derives the
    grid from $k$ and sweeps three backgrounds to $k=600$: the agreement is
    $9.5\times10^{-6}$ worst and $2.7\times10^{-8}$ median, so the claim turns
    out to have been true --- but it is true for reasons findings **T-45** and
    **T-46** had to establish, and until they did it was a number repeated
    rather than a number taken.

    What the plateau discrepancy actually is, is **approximation A-2** --- the
    weight carried by the line-of-sight integral. Both routes here are given
    $e^{-\kappa}$. The two-frame path gives (102) the $\mathcal V$ that (102)
    prints, faithfully, and that choice is what costs the plateau.

    The test exists whichever way the answer had gone: an equivalence asserted
    at one point in a continuous parameter is not an equivalence.
    """
    result = two_route_transfer(k, ELLS)
    worst = result.worst
    assert worst < 1e-3, (
        f"at k={k} the two routes differ by {worst:.2e}; they are the same "
        f"calculation and must not")
