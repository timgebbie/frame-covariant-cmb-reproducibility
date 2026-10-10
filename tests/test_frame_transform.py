r"""The numerical change of threading: what it establishes, and what it exposed.

`functions.spectra.frame_transform` turns the frame label into a calculation.
These tests fix the parts that are **exact** — the energy-frame condition and
the Weyl invariant, both at machine precision — and then pin the negative
result the machinery was built to find, finding **T-14**: the assembled
transfer function is *not* invariant under transforming the inputs to
(177)-(179), because those equations are themselves Newtonian-threading
expressions. A test that asserts a known defect is how the defect stays known.
"""

from __future__ import annotations

import numpy as np
import pytest

from functions.background.flrw import CDM_MODEL
from functions.spectra.acoustic import solve_acoustic
from functions.spectra.bessel_table import BesselTable
from functions.spectra.decoupling import RecombinationHistory
from functions.spectra.frame_transform import energy_frame_shift, to_frame
from functions.spectra.potentials import potentials
from functions.spectra.sources import (
    PerturbationHistory,
    ScatteringHistory,
    source_doppler,
    source_integrated,
    source_primary,
)

K_TEST = 0.02


def _setup(k: float = K_TEST):
    bg = CDM_MODEL
    rec = RecombinationHistory.build(bg)
    eta = rec.eta
    phi_a, phi_h = potentials(bg, eta)
    ac = solve_acoustic(k, eta, background=bg, phi_a=phi_a, phi_h=phi_h,
                        omega_b_h2=0.0224, expansion_coupling=False)
    hist = PerturbationHistory(eta=eta, delta_T=ac.delta_T, phi_a=phi_a,
                               phi_h=phi_h, tau_1=ac.tau_1, v_b=ac.tau_1,
                               frame="newtonian")
    return bg, rec, eta, phi_a, hist


def test_the_energy_frame_kills_the_acceleration_to_machine_precision():
    r"""$\tilde\Phi_A=0$, which is the **definition** of the frame, not a result.

    Worth asserting anyway: it is zero by construction only if the quadrature,
    the integrating factor and the exact $v'$ all agree, and any slip in those
    shows up here before it shows up anywhere interesting.
    """
    bg, _, eta, phi_a, hist = _setup()
    shift = energy_frame_shift(eta, phi_a, K_TEST, background=bg)
    moved = to_frame(hist, shift)

    scale = float(np.max(np.abs(hist.phi_a)))
    assert float(np.max(np.abs(moved.phi_a))) / scale < 1e-14


def test_the_weyl_invariant_survives_the_numerical_transformation():
    r"""$\Phi_A-\Phi_H$ is unchanged — GDE99 Eq. (24) and Stewart-Walker, in floats.

    `functions.frames` proves this symbolically. This is the statement that the
    numerical implementation carries the same rule, which is a different claim:
    a correct identity can still be implemented with a sign error.
    """
    bg, _, eta, phi_a, hist = _setup()
    moved = to_frame(hist, energy_frame_shift(eta, phi_a, K_TEST, background=bg))

    before = np.asarray(hist.phi_a) - np.asarray(hist.phi_h)
    after = np.asarray(moved.phi_a) - np.asarray(moved.phi_h)
    assert float(np.max(np.abs(after - before)) / np.max(np.abs(before))) < 1e-14


def test_the_initial_condition_is_forgotten_rather_than_propagated():
    r"""The homogeneous mode is $v\propto1/a$, so a wrong start decays.

    `energy_frame_shift` begins on the matter-domination attractor
    $v=-k\Phi_A\eta/3$. If that choice were load-bearing the figure would depend
    on it, so this starts from **zero** instead and requires the two to converge
    by late times. It is the same discipline as deriving a grid instead of
    choosing one (T-3).
    """
    bg, _, eta, phi_a, _ = _setup()
    a = np.asarray(bg.a_of_eta(eta), dtype=float)

    attractor = energy_frame_shift(eta, phi_a, K_TEST, background=bg).v

    integrand = a * phi_a
    cumulative = np.concatenate(
        ([0.0], np.cumsum(0.5 * (integrand[1:] + integrand[:-1]) * np.diff(eta)))
    )
    from_zero = (a[0] * 0.0 - K_TEST * cumulative) / a

    late = slice(len(eta) // 2, None)
    drift = np.max(np.abs(attractor[late] - from_zero[late]))
    assert drift / np.max(np.abs(attractor[late])) < 1e-3


def test_applying_a_shift_twice_is_refused():
    """A history already in the target frame cannot be shifted into it again.

    The label used to be decoration, so nothing stopped a caller transforming
    an energy-frame history into the energy frame and double-counting $v$. It
    does now.
    """
    bg, _, eta, phi_a, hist = _setup()
    shift = energy_frame_shift(eta, phi_a, K_TEST, background=bg)
    moved = to_frame(hist, shift)

    with pytest.raises(ValueError, match="already in"):
        to_frame(moved, shift)


def test_T14_the_transfer_function_is_NOT_frame_invariant_under_177_to_179():
    r"""**Finding T-14, pinned.** The sum is an observable; this calculation is not it.

    `sources.py` claimed that because $\delta T$, $\Phi_A$, $v_B$ and $\tau_1$
    all shift under a change of threading, "only the total is an observable" —
    which is true physics, and was being read operationally as *transform the
    four inputs and the total is preserved*. It is not preserved. It moves by a
    factor of order **five**.

    The reason is that (177)-(179) are **Newtonian-threading expressions**, not
    generic-$u^a$ ones: they descend from (106), which the corrections record
    flags in those words, through (107), (110) and (111). The Newtonian
    threading carries its $O(\ell)$ source in the **acceleration** pair; the CDM
    threading carries it in the **shear** pair (Paper 1 Secs. VI B and VI C,
    Eqs. (newt-pair) and (cdm-triple)). Setting $\tilde\Phi_A=0$ therefore
    deletes the coupling that carried the source without supplying the one that
    replaces it — and the measured collapse to a fraction of a percent under the
    opacity weighting is exactly that signature.

    This test asserts the **defect**, so that the day the generic-$u^a$ source
    lands it fails loudly and is rewritten into the invariance it should then
    assert. See decision S21.
    """
    bg, rec, eta, phi_a, hist = _setup()
    eta_star = float(eta[int(np.argmax(rec.visibility))])
    aH = bg.aH_of_eta(eta)
    moved = to_frame(hist, energy_frame_shift(eta, phi_a, K_TEST, background=bg))

    sc = ScatteringHistory(eta=eta, kappa_prime=rec.kappa_prime,
                           visibility=rec.visibility, damping_k=np.inf)
    table = BesselTable.build(ell_max=12,
                              x_max=float(K_TEST * (bg.eta_0 - eta[0])) + 20.0)

    def transfer(h, ell):
        primary = float(np.interp(eta_star, eta,
                                  source_primary(h, sc, damping_total=1.0)))
        integrated = (source_doppler(h, sc, K_TEST, weight=rec.opacity)
                      + source_integrated(h, sc, K_TEST, aH=aH,
                                          weight=rec.opacity))
        j = table(ell, K_TEST * (bg.eta_0 - eta))
        return (primary * float(table(ell, K_TEST * (bg.eta_0 - eta_star)))
                + float(np.trapezoid(integrated * j, eta)))

    for ell in (2, 5, 10):
        newtonian, energy = transfer(hist, ell), transfer(moved, ell)
        relative = abs(energy - newtonian) / abs(newtonian)
        # Not invariance: near-total collapse of the source. Pinned as a range
        # so that either a fix or a regression changes the result.
        assert 0.9 < relative < 1.0, (
            f"l={ell}: expected the known T-14 collapse, got {relative:.3e}. "
            "If the generic-u^a source has landed, this test is now wrong and "
            "should assert invariance instead."
        )
