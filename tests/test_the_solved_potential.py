r"""Step 2 of sec:a3-construction: the potential solved with the matter and the photons.

Every number asserted here is a statement about physics the solve must
reproduce, measured against something the solve does not use: Kodama and
Sasaki's two-fluid solution, $D/a$ from Heath's integral at the exact $a(\eta)$,
the energy constraint the solve never integrates, and the released path, which
an $\Omega_r=0$ background must keep bit for bit.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp

from functions.background.flrw import CDM_MODEL, LCDM_MODEL, PLANCK_MODEL
from functions.spectra.acoustic import baryon_photon_ratio, common_start_eta
from functions.spectra.decoupling import RecombinationHistory
from functions.spectra.radiation_era import (
    growing_mode,
    kodama_sasaki,
    matter_weight,
    photon_weight,
    solve_mode,
)
from functions.spectra.two_frame import (
    SOLVED_PHI_I,
    build_environment,
    coefficient_sets,
    line_of_sight_inputs,
    mode_history,
)
from functions.spectra.line_of_sight import kernel_set, three_slots

K_MAX = 1500.0


@pytest.fixture(scope="module")
def planck():
    rec = RecombinationHistory.build(PLANCK_MODEL, omega_b_h2=0.0224, h=0.674)
    eta_i = common_start_eta(PLANCK_MODEL, K_MAX)
    return PLANCK_MODEL, eta_i, float(rec.eta_star)


def _solve(background, eta_i, eta_star, k, eta=None, **kw):
    grid = (np.array([eta_i, eta_star, background.eta_0]) if eta is None else eta)
    return solve_mode(k, background, grid, eta_i=eta_i, eta_star=eta_star,
                      eta_couple=6.0 * eta_star, **kw)


def test_kodama_sasaki_series_meets_its_closed_form():
    """The two branches agree where they meet, and the limits are 1 and 9/10."""
    y = np.array([0.1 * (1 - 1e-12), 0.1])
    f, fp = kodama_sasaki(y)
    assert abs(f[0] - f[1]) < 1e-12 and abs(fp[0] - fp[1]) < 1e-11
    assert kodama_sasaki(0.0)[0][0] == 1.0
    assert kodama_sasaki(0.0)[1][0] == pytest.approx(-1.0 / 16.0, abs=1e-15)
    assert kodama_sasaki(1e8)[0][0] == pytest.approx(0.9, abs=1e-8)


def test_the_start_lies_on_both_constraints(planck):
    """T-194: the start is the growing mode on the momentum AND the energy constraint."""
    bg, eta_i, _ = planck
    for k in (1e-3, 15.0, K_MAX):
        phi_h, d_m, v, d_t, tau = growing_mode(k, bg, eta_i, 1.0)
        a = float(bg.a_of_eta(eta_i))
        h = float(bg.conformal_hubble(a))
        w_m, w_g = float(matter_weight(bg, a)), float(photon_weight(bg, a))
        terms = (k**2 * phi_h, w_m * d_m, 3 * w_m * h * v / k, 4 * w_g * d_t,
                 4 * w_g * h * tau / k)
        energy = terms[0] - (terms[1] - terms[2] + terms[3] - terms[4])
        assert abs(energy) / sum(abs(t) for t in terms) < 1e-13
        # and it is eq:radiation-ic at leading order
        assert d_t == pytest.approx(-0.5, rel=1e-3)
        assert v == pytest.approx(-0.5 * k * eta_i, rel=1e-3)


def test_t194_the_leading_order_start_does_not_converge(planck):
    """The leading-order start leaves Phi(eta_*) 6% high, at eta_i and eta_i/2 alike."""
    bg, eta_i, eta_star = planck
    k = 1e-3
    c_m, c_g = 1.5 * bg.omega_m, 1.5 * bg.omega_r
    r_per_a = float(baryon_photon_ratio(1.0, omega_b_h2=0.0224))

    def rhs(x, y):
        eta = np.exp(x)
        phi_h, d_m, v_m, d_t, tau = y
        a = float(bg.a_of_eta(eta))
        h, r = float(bg.conformal_hubble(a)), r_per_a * a
        d = -h * phi_h + (c_m / a * v_m + 4 / 3 * c_g / a**2 * tau) / k
        return eta * np.array([d, k * v_m - 3 * d, -h * v_m + k * phi_h,
                               -d + k / 3 * tau,
                               -(h * r / (1 + r)) * tau - k / (1 + r) * d_t + k * phi_h])

    ks = float(kodama_sasaki(float(bg.a_of_eta(eta_star)) * bg.omega_m / bg.omega_r)[0][0])
    lead = []
    for e in (eta_i, eta_i / 2):
        v = -0.5 * k * e
        sol = solve_ivp(rhs, (np.log(e), np.log(eta_star)), [-1, -1.5, v, -0.5, v],
                        method="DOP853", rtol=1e-11, atol=1e-16)
        lead.append(-sol.y[0, -1])
        assert _solve(bg, e, eta_star, k).phi_a_star == pytest.approx(ks, abs=1e-8)
    assert lead[0] - ks > 0.05 and abs(lead[0] - lead[1]) < 1e-5


def test_kodama_sasaki_outside_the_horizon(planck):
    """Phi(eta_*) = 0.92539 Phi_i at k -> 0, the registered super-horizon fall."""
    bg, eta_i, eta_star = planck
    y_star = float(bg.a_of_eta(eta_star)) * bg.omega_m / bg.omega_r
    m = _solve(bg, eta_i, eta_star, 1e-3)
    assert m.phi_a_star == pytest.approx(float(kodama_sasaki(y_star)[0][0]), abs=1e-8)
    assert m.phi_a_star == pytest.approx(0.92539, abs=5e-6)


def test_the_sachs_wolfe_source_at_k_to_zero_is_the_registered_number(planck):
    """(dT + Phi_A)(eta_*) = 2 Phi_A(eta_*) - (3/2) Phi_i = 0.379 Phi_A(eta_*)."""
    bg, eta_i, eta_star = planck
    m = _solve(bg, eta_i, eta_star, 1e-3, phi_i=SOLVED_PHI_I)
    source = (m.delta_t_star + m.phi_a_star) / m.phi_a_star
    assert source == pytest.approx(2.0 - 1.5 * SOLVED_PHI_I / m.phi_a_star, abs=1e-8)
    assert source == pytest.approx(0.37906, abs=2e-5)


def _heath_d_over_a(background, eta):
    """D/a in closed form at the exact a(eta), independent of the solve and of the spline."""
    def hubble(x):
        return np.sqrt(background.omega_m / x**3 + background.omega_lambda
                       + background.omega_k / x**2)
    a = np.asarray(background.a_of_eta(eta), dtype=float).copy()
    for _ in range(3):      # Newton on eta(a) = Int da / (a^2 H)
        eta_a = np.array([quad(lambda x: 1 / (x * x * hubble(x)), 0, ai,
                               epsabs=0, epsrel=2e-14, limit=200)[0] for ai in a])
        a -= (eta_a - eta) * a**2 * hubble(a)
    d = np.array([hubble(ai) * quad(lambda x: 1 / (x * hubble(x)) ** 3, 0, ai,
                                    epsabs=0, epsrel=2e-14, limit=200)[0] / ai
                  for ai in a])
    return d / d[0]


@pytest.mark.parametrize("background", [CDM_MODEL, LCDM_MODEL], ids=["EdS", "LCDM"])
def test_g1_the_solve_is_d_over_a_where_omega_r_vanishes(background):
    """(g1): baryons as dust, no radiation, the solve equals D/a to 1e-10."""
    rec = RecombinationHistory.build(background, omega_b_h2=0.0224, h=0.674)
    eta_i = common_start_eta(background, K_MAX)
    eta = np.linspace(eta_i, background.eta_0, 41)
    reference = _heath_d_over_a(background, eta)
    for k in (0.05, 300.0):
        m = _solve(background, eta_i, float(rec.eta_star), k, eta=eta)
        assert np.max(np.abs(m.phi_a - reference)) < 1e-10


@pytest.mark.parametrize("background", [CDM_MODEL, LCDM_MODEL], ids=["EdS", "LCDM"])
def test_g2_the_wiring_cannot_move_a_background_without_radiation(background):
    """(g2): where Omega_r = 0 the solved environment keeps the released potential."""
    kw = dict(omega_m=background.omega_m, omega_lambda=background.omega_lambda,
              omega_r=0.0, acoustic_start="radiation era", line_of_sight_weight="printed")
    released = build_environment(60.0, **kw)
    solved = build_environment(60.0, potential="solved", **kw)
    for k in (0.5, 40.0):
        a, b = mode_history(k, released), mode_history(k, solved)
        assert b.solved is None
        for name in ("phi_a", "phi_h", "phi_a_prime", "phi_h_prime", "delta_t", "tau_1"):
            assert np.array_equal(getattr(a, name), getattr(b, name))
        assert np.array_equal(a.shift.v, b.shift.v)


def test_the_energy_constraint_closes_without_the_baryon_loading(planck):
    """The solve is consistent: with R -> 0 the energy constraint holds to 1e-9.

    With R the step-2 system is not closed --- the photons' momentum given to
    the baryons is not in the constraint, where they move with the CDM --- and
    the residual is the baryons' own term, which step 3 adds. Asserted, so the
    step that removes it has to say so.
    """
    bg, eta_i, eta_star = planck
    for k in (1.0, 30.0, 300.0):
        bare = _solve(bg, eta_i, eta_star, k, omega_b_h2=1e-12)
        assert abs(bare.energy_residual_star) < 1e-9
        assert abs(bare.energy_residual_exit) < 1e-9
    loaded = _solve(bg, eta_i, eta_star, 30.0)
    assert abs(loaded.energy_residual_star) > 1e-3


def test_the_energy_constraint_sees_the_photons_stress(planck):
    """Phi_A from the stress constraint closes the energy constraint; Phi_A = -Phi_H does not."""
    bg, eta_i, eta_star = planck
    eta = np.linspace(eta_i, bg.eta_0, 801)   # stress_max is read on the grid
    for k in (1.0, 10.0):
        with_stress = _solve(bg, eta_i, eta_star, k, eta=eta, omega_b_h2=1e-12)
        without = _solve(bg, eta_i, eta_star, k, eta=eta, omega_b_h2=1e-12,
                         anisotropic_stress=False)
        assert abs(with_stress.energy_residual_exit) < 1e-9
        assert abs(without.energy_residual_exit) > 1e-5
        assert 0.03 < with_stress.stress_max < 0.05


def test_the_photons_leave_the_constraint_only_where_they_may(planck):
    """Super-horizon modes carry their photons to eta_0; sub-horizon ones leave."""
    bg, eta_i, eta_star = planck
    assert _solve(bg, eta_i, eta_star, 1e-3).eta_exit == pytest.approx(bg.eta_0)
    m = _solve(bg, eta_i, eta_star, 300.0)
    assert eta_star < m.eta_exit < bg.eta_0
    rec = RecombinationHistory.build(CDM_MODEL, omega_b_h2=0.0224, h=0.674)
    eds = _solve(CDM_MODEL, common_start_eta(CDM_MODEL, K_MAX), float(rec.eta_star), 30.0)
    assert eds.eta_exit == pytest.approx(float(rec.eta_star))


def test_the_hierarchy_is_closed_far_enough(planck):
    """Closing the photon hierarchy at twice ell_max moves the potential by < 1e-9 at k = 30."""
    bg, eta_i, eta_star = planck
    eta = np.linspace(eta_i, bg.eta_0, 401)
    a = _solve(bg, eta_i, eta_star, 30.0, eta=eta)
    b = _solve(bg, eta_i, eta_star, 30.0, eta=eta, ell_max=64)
    assert np.max(np.abs(a.phi_a - b.phi_a)) < 1e-9


@pytest.fixture(scope="module")
def solved_planck():
    return build_environment(
        60.0, omega_m=PLANCK_MODEL.omega_m, omega_lambda=PLANCK_MODEL.omega_lambda,
        omega_r=PLANCK_MODEL.omega_r, omega_b_h2=0.02237, hubble_h=0.6736,
        line_of_sight_weight="printed", acoustic_start="radiation era",
        potential="solved")


def test_e_the_two_frames_agree_under_the_solved_potential(solved_planck):
    """(e) at the mode: the CDM frame closes with the photons' stress in it."""
    env = solved_planck
    ells = np.array([2, 30, 200])
    for k in (3.0, 40.0):
        history = mode_history(k, env)
        assert history.solved is not None
        kern = kernel_set(ells, k, eta=env.eta, eta_0=float(env.background.eta_0))
        out = []
        for cs in coefficient_sets(k, env, source="paper 1", history=history):
            sources, damping = line_of_sight_inputs(k, cs, env)
            out.append(three_slots(kern, sources).transfer(damping))
        assert np.max(np.abs(out[0] - out[1])) / np.max(np.abs(out[1])) < 1e-11


def test_the_solved_potential_carries_no_j5_and_one_amplitude(solved_planck):
    """No (J.5) on the solve; Phi_i = 10/9, so the matter-era k -> 0 value is 1."""
    env = solved_planck
    h = mode_history(0.05, env)
    assert h.solved.phi_a_star == pytest.approx(SOLVED_PHI_I * 0.92539, rel=1e-4)
    halved = dataclasses.replace(env, eta_i=env.eta_i / 2)
    assert np.max(np.abs(mode_history(0.05, halved).phi_a - h.phi_a)) < 1e-8


def test_the_options_are_refused_where_nothing_is_solved():
    env = build_environment(30.0, acoustic_start="radiation era",
                            line_of_sight_weight="printed")
    with pytest.raises(ValueError):
        mode_history(1.0, env, anisotropic_stress=False)
    with pytest.raises(ValueError):
        build_environment(30.0, potential="solved", line_of_sight_weight="printed")
