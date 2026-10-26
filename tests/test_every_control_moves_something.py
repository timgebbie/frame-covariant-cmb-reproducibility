r"""Every control must change the answer, or raise. **Nothing may be silent.**

**This file closes the T-125 class, which happened three times in one day.**

A control is a named branch with the released default (decision **S43**), and
the point of one is that turning it on measures a different configuration.
Three times on 2026-10-25 a control did not:

* **T-125** — `by_parts_weight_terms` is *discarded* under `slot_weight_split`:
  the split branch rebuilds the bracket from the coefficients and never reads
  the partner terms. A finding was published attributing a result to the pair
  when only one of them was acting, and it had to be withdrawn within the hour.
* **the D32 no-op** — `BULK_SOURCE_CONTROLS` reaches `integral_solution` only
  through `transfer_by_rank`. A diagnostic that calls the integral directly
  set the dict, saw it ignored, and computed the released configuration three
  times under three different names. It was caught **only** because a
  quadrature gate came back bit-identical across configurations that should
  have moved it.
* **T-151** — `w_half_is_isw_only` had no supplier for `c1_prime_isw`
  anywhere in the tree, so it sent an array of zeros to $W$ and left the
  bracket alone. It had been in D26's lattice, labelled, for days.

**The common shape: a control that reads as live, raises nothing, and
measures the released configuration.** Every one was found by accident. This
file finds them on purpose.

THE RULE
--------
For each control, on one fixed fixture, exactly one of these must hold:

1. **it moves the answer** --- the transfer differs from the released default
   by more than quadrature noise; or
2. **it raises** --- because its required inputs are absent, which is the
   honest failure and is what `bracket_all_at_w` and `isw_only_at_w` do.

**Silently returning the released answer is the one outcome forbidden**, and
it is the outcome all three defects above produced.

WHAT THIS IS NOT
----------------
**It is not a physics test.** It asserts nothing about whether a control is
*right*, only that it is *connected*. A control that moves the answer in a
wrong direction passes here and fails elsewhere, which is the correct
division: this file is about wiring.
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, bulk_source_primitives, coefficient_sets)
from functions.spectra.bessel_table import BesselTable  # noqa: E402

#: Every boolean control on the integral, discovered from the signature
#: rather than listed. **A new control is covered the day it lands**, which
#: is the property a hand-maintained list does not have --- and a
#: hand-maintained list is how `w_half_is_isw_only` sat unexercised.
CONTROLS = sorted(
    name for name, p in inspect.signature(integral_solution).parameters.items()
    if p.default is False)

#: One mode, one background, a handful of multipoles. The fixture only has to
#: be sensitive, not physical: a control that cannot move *this* cannot move
#: a spectrum built from 1433 of them.
#:
#: **$\Lambda$CDM and NOT Einstein--de Sitter, and the reason is T-146.** On
#: EdS $\Phi$ is exactly constant, so $(\Phi_A'-\Phi_H')\equiv0$ and every
#: control that moves the ISW channel has *nothing to move*. The first
#: version of this fixture was EdS and this gate duly reported
#: `isw_only_at_w` and `w_half_is_isw_only` as dead — **the same
#: background-specific cancellation that produced four withdrawn readings on
#: 2026-10-25, reproduced inside the test written to stop that class.** A
#: fixture on a background where the quantity vanishes identically cannot
#: test anything that acts on it.
K = 30.0
ELLS = np.array([2, 10, 50, 200])


@pytest.fixture(scope="module")
def fixture():
    from functions.background.flrw import LCDM_MODEL
    env = build_environment(
        60.0, omega_m=LCDM_MODEL.omega_m, omega_lambda=LCDM_MODEL.omega_lambda,
        omega_r=LCDM_MODEL.omega_r, omega_b_h2=0.0224,
        transfer_gamma=0.48, hubble_h=0.5, f_2=F2_DEFAULT,
        line_of_sight_weight="printed")
    s = coefficient_sets(K, env)[1]
    needed = required_multipoles(ELLS)
    eta_0 = float(env.background.eta_0)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(K * (eta_0 - env.eta[0])) + 20.0)
    diffusion = float(np.exp(-((K / env.damping_k) ** 2)))
    common = dict(table=table, weight=env.weight, diffusion=diffusion,
                  damping_total=diffusion, eta_star=float(env.eta_star),
                  eta_floor=float(env.eta[0]), visibility=env.visibility,
                  eta_0=eta_0)
    common.update(bulk_source_primitives(K, env, s))
    coeffs = dict(coefficients=s.coefficients, c1_prime=s.c1_prime,
                  c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
                  c2_prime=s.c2_prime)
    return common, coeffs


def _transfer(common, coeffs, **flags) -> np.ndarray:
    res = integral_solution(ELLS, **coeffs, **common, **flags)
    return np.asarray(res.integrated, dtype=float) \
        + np.asarray(res.boundary_scalar, dtype=float) \
        + np.asarray(res.boundary_shear, dtype=float)


def test_there_are_controls_to_check():
    """A signature scan that finds nothing passes every test below it."""
    assert len(CONTROLS) >= 7, (
        f"only {len(CONTROLS)} boolean controls discovered on "
        "integral_solution; either they have been renamed or the signature "
        "scan is measuring nothing")


@pytest.mark.parametrize("control", CONTROLS)
def test_the_control_moves_the_answer_or_raises(control, fixture):
    """**The gate.** Connected, or honest about not being. Never silent."""
    common, coeffs = fixture
    released = _transfer(common, coeffs)
    try:
        got = _transfer(common, coeffs, **{control: True})
    except (ValueError, TypeError) as exc:
        # Raising is a pass: a control that cannot run without inputs it has
        # not been given must say so rather than quietly doing nothing.
        assert str(exc).strip(), f"{control} raised with an empty message"
        return

    scale = max(float(np.max(np.abs(released))), 1e-300)
    moved = float(np.max(np.abs(got - released))) / scale
    assert moved > 1e-10, (
        f"`{control}=True` returned the released answer to {moved:.2e} and "
        "raised nothing. That is the T-125 class: a control that reads as "
        "live, is accepted without complaint, and measures the released "
        "configuration under another name. Either wire it up, or make it "
        "raise when the inputs it needs are absent — do not let it pass "
        "silently. Every diagnostic that has ever set this flag has been "
        "measuring the default.")


def test_the_gate_catches_a_control_that_does_nothing(fixture):
    """**The negative control, as finding T-44 requires.**

    T-44 is a gate that printed PASS on a `nan`, and the lesson recorded there
    is that a gate is not tested by the run that passes it. So this one is
    handed a flag that provably changes nothing and must refuse it.

    `integral_solution` takes `**_ignored`? It does not --- so the synthetic
    no-op is built the other way, by asking for the released answer twice and
    checking the comparison itself fires. If this ever stops failing, the
    assertion above has stopped measuring anything.
    """
    common, coeffs = fixture
    a = _transfer(common, coeffs)
    b = _transfer(common, coeffs)
    scale = max(float(np.max(np.abs(a))), 1e-300)
    moved = float(np.max(np.abs(b - a))) / scale
    assert moved <= 1e-10, (
        "two identical calls differ, so the comparison in the test above "
        "cannot distinguish a live control from a dead one")
