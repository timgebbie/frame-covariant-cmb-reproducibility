r"""The line of sight in two frames: one transfer, or a measured failure.

A first-order change of frame moves only the observer's dipole, so for
$\ell\ge2$ the Newtonian and CDM coefficient sets of one solve must give one
transfer. $W\{C_0K+C_1K'+C_2K''\}$ does that exactly when
$\Delta C_0=0$, $\Delta C_1^{\rm scatt}=\kappa'\Delta C_2$ and
$\Delta C_1^{\rm grav}=\Delta C_2'$. Paper 1's source equation meets all three;
the coefficients as built meet only the second. The as-built failures are held
as **strict expected failures**, so the suite goes red the day they change and
the marker has to be removed by hand.
"""
from __future__ import annotations

from contextlib import contextmanager

import numpy as np
import pytest
from scipy.special import spherical_jn

import functions.spectra.coefficients as coefficients
from functions.spectra.bessel_table import BesselTable
from functions.spectra.coefficients import gravitational_rank_one
from functions.spectra.integral_solution import required_multipoles
from functions.spectra.line_of_sight import kernel_set, three_slots
from functions.spectra.two_frame import (
    build_environment, coefficient_sets, line_of_sight_inputs,
    transfer_by_rank)

K_MAX = 60.0
MODES = (3.0, 20.0, 55.0)
ELLS = np.array([2, 3, 10, 30, 60])


@contextmanager
def source(choice: str):
    held = coefficients.RANK_ONE_SOURCE
    coefficients.RANK_ONE_SOURCE = choice
    try:
        yield
    finally:
        coefficients.RANK_ONE_SOURCE = held


@pytest.fixture(scope="module")
def env():
    return build_environment(K_MAX)


def _rel(a, b, mask=slice(None)):
    a, b = np.asarray(a)[mask], np.asarray(b)[mask]
    scale = max(np.max(np.abs(a)), np.max(np.abs(b)))
    return float(np.max(np.abs(a - b)) / scale) if scale else 0.0


def _conditions(env, k):
    """The three frame conditions, as the largest relative shift each leaves."""
    n, c = coefficient_sets(k, env)
    on = np.asarray(env.opacity) > 1e-10
    gn, gpn = gravitational_rank_one(n)
    gc, gpc = gravitational_rank_one(c)
    c2p_n = np.zeros_like(env.eta) if n.c2_prime is None else n.c2_prime
    return {
        "rank zero": _rel(n.coefficients.c0, c.coefficients.c0, on),
        "scattering": _rel(n.v_b / k + n.coefficients.c2,
                           c.v_b / k + c.coefficients.c2, on),
        "gravitational": _rel(gn - c2p_n, gc - c.c2_prime, on),
        "gravitational, derivative": _rel(gpn - n.c2_second,
                                          gpc - c.c2_second, on),
    }


def test_paper_1_source_meets_all_three_frame_conditions_at_every_eta(env):
    with source("paper 1"):
        for k in MODES:
            for name, shift in _conditions(env, k).items():
                assert shift < 1e-12, f"{name} at k={k}: {shift:.1e}"


def test_as_built_meets_only_the_scattering_condition(env):
    """The control: what the switch repairs is visible without it."""
    with source("as built"):
        for k in MODES:
            got = _conditions(env, k)
            assert got["scattering"] < 1e-12
            assert got["rank zero"] > 1e-2
            assert got["gravitational"] > 1e-2


def test_in_a_shear_free_frame_the_integrated_source_is_the_isw_alone(env):
    r"""$C_0-C_1^{\rm grav}{}'+C_2''=-(\Phi_A'-\Phi_H')$ in the Newtonian frame:
    the carried $a\mathcal B_0$ cancels the photon dipole in $-C_1'$, so
    nothing but the potentials accumulates along the path."""
    with source("paper 1"):
        for k in MODES:
            s, _ = line_of_sight_inputs(k, coefficient_sets(k, env)[0], env)
            isw = -env.transfer_at(k) * (np.asarray(env.phi_a_prime)
                                         - np.asarray(env.phi_h_prime))
            on = np.asarray(env.opacity) > 1e-10
            residual = (s.c0 - s.c1_grav_prime + s.c2_second - isw)[on]
            assert np.max(np.abs(residual)) < 1e-12 * np.max(np.abs(s.c0[on]))


def _three_slot_transfers(env, k):
    kern = kernel_set(ELLS, k, eta=env.eta, eta_0=float(env.background.eta_0))
    return [three_slots(kern, line_of_sight_inputs(k, cs, env)[0])
            for cs in coefficient_sets(k, env)]


def test_the_three_slots_give_one_transfer_in_both_frames(env):
    r"""Slot by slot, each against the size of the whole transfer: on this
    Einstein--de~Sitter fixture the potentials are constant and the
    integrated slot is zero to rounding in both frames. The floor is rounding
    in that slot, where the carried photon dipole cancels against
    $C_1^{\rm grav}{}'$."""
    with source("paper 1"):
        for k in MODES:
            n, c = _three_slot_transfers(env, k)
            scale = np.max(np.abs(n.transfer()))
            for slot in ("sachs_wolfe", "doppler", "integrated"):
                gap = np.max(np.abs(getattr(n, slot) - getattr(c, slot)))
                assert gap < 1e-10 * scale, slot
            assert _rel(n.transfer(0.7), c.transfer(0.7)) < 1e-10


@pytest.mark.xfail(strict=True, reason="as built, rank zero and the "
                   "gravitational half shift between frames")
def test_as_built_the_three_slots_give_one_transfer_in_both_frames(env):
    with source("as built"):
        for k in MODES:
            n, c = _three_slot_transfers(env, k)
            assert _rel(n.transfer(), c.transfer()) < 1e-6


@pytest.mark.xfail(strict=True, reason="the released (102) assembly is "
                   "frame-dependent at order unity")
def test_the_released_assembly_gives_one_transfer_in_both_frames(env):
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=K_MAX * float(env.background.eta_0 - env.eta[0]) + 20.0)
    for k in MODES:
        n, c = coefficient_sets(k, env)
        assert _rel(transfer_by_rank(ELLS, k, n, env, table)[-1],
                    transfer_by_rank(ELLS, k, c, env, table)[-1]) < 1e-6


def test_the_switch_carries_both_corrections_or_neither(env):
    """Paper 1's sign without the rank-zero row would break a condition, so
    the switch refuses a monopole row that cannot carry the row."""
    held = coefficients.MONOPOLE_ROW
    try:
        coefficients.MONOPOLE_ROW = "printed"
        with source("paper 1"), pytest.raises(ValueError, match="B_0"):
            coefficient_sets(MODES[0], env)
    finally:
        coefficients.MONOPOLE_ROW = held


def test_the_kernels_come_from_relations_and_match_the_functions():
    r"""$j_\ell'$ by recurrence and $j_\ell''$ by Bessel's equation, with the
    $x\to0$ limits."""
    ells = np.array([2, 3, 7, 40])
    grid = np.linspace(0.0, 1.0, 4001)
    kern = kernel_set(ells, 120.0, eta=grid, eta_0=1.0)
    x = 120.0 * (1.0 - grid)
    inner = slice(2, -2)
    for i, l in enumerate(ells):
        assert np.max(np.abs(kern.j[i] - spherical_jn(l, x))) < 1e-14
        assert np.max(np.abs(kern.jd[i]
                             - spherical_jn(l, x, derivative=True))) < 1e-14
        numeric = np.gradient(spherical_jn(l, x, derivative=True), x)
        assert np.max(np.abs(kern.jdd[i][inner] - numeric[inner])) < 1e-4
    assert kern.jdd[0][-1] == pytest.approx(2.0 / 15.0)
    assert kern.jdd[1][-1] == 0.0
