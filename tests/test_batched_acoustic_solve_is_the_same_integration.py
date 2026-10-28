r"""The batched acoustic solve must be the serial one, to the integrator's tolerance.

**What this guards, and why it is worth a file of its own.**

`scripts/benchmark_single_run.py` puts the per-mode loop at **99.7%** of a
spectrum run, and a `cProfile` of `coefficient_sets` puts ~84% of the
coefficients stage inside `acoustic.solve_acoustic`'s right-hand side — in
scalar `CubicSpline` evaluations of five quantities that **do not depend on
$k$** and are rebuilt for every one of 4480 modes.

`solve_acoustic_batch` integrates every mode in one `solve_ivp`, which is
legitimate because (152)/(153) are linear in $(\delta_T,\tau_1)$ with $k$ a
scalar multiplier: the splines are then evaluated once per step for all modes
instead of once per step per mode. Measured: **12x** across the whole $k$
range and **20x** in a narrow band.

**A 12x speedup on the hot path of every number in the bundle is exactly the
kind of change that is worth being paranoid about.** If the batched and serial
solutions differ by more than the integrator's own tolerance, then adopting it
would move every spectrum, every peak position and every finding downstream —
and the move would look like physics. So the assertion here is agreement at
`rtol`, not agreement to plotting accuracy.

WHAT IS ASSERTED
----------------
1. the two agree across the full $k$ range at the solver's tolerance;
2. they agree in a narrow band, where the step controller behaves differently;
3. the batch is **order-preserving** — mode $i$ out is mode $i$ in, which a
   transposed stack would silently violate while still agreeing on norms;
4. one mode batched is the serial answer, so the degenerate case is not a
   special case;
5. and the negative control **T-44** requires: the comparison must *fail* when
   handed a deliberately wrong pairing, or it is asserting nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import LCDM_MODEL  # noqa: E402
from functions.spectra.acoustic import (  # noqa: E402
    solve_acoustic, solve_acoustic_batch)
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.two_frame import build_environment  # noqa: E402

#: The integrator runs at `rtol=1e-10`. Agreement is required at 1e-7, which
#: is three decades of slack on the tolerance and still six decades tighter
#: than anything that could move a peak position.
TOLERANCE = 1e-7


@pytest.fixture(scope="module")
def env():
    return build_environment(
        300.0, omega_m=LCDM_MODEL.omega_m, omega_lambda=LCDM_MODEL.omega_lambda,
        omega_r=LCDM_MODEL.omega_r, omega_b_h2=0.0224, transfer_gamma=0.48,
        hubble_h=0.5, f_2=F2_DEFAULT, line_of_sight_weight="printed")


def _serial(env, ks):
    return [solve_acoustic(float(k), env.eta, background=env.background,
                           phi_a=np.asarray(env.phi_a, dtype=float),
                           phi_h=np.asarray(env.phi_h, dtype=float))
            for k in ks]


def _batched(env, ks):
    return solve_acoustic_batch(
        ks, env.eta, background=env.background,
        phi_a=np.asarray(env.phi_a, dtype=float),
        phi_h=np.asarray(env.phi_h, dtype=float))


def _worst(a, b):
    """Worst relative disagreement, normalised by the serial mode's own scale."""
    out = 0.0
    for s, t in zip(a, b):
        for field in ("delta_T", "tau_1"):
            x = np.asarray(getattr(s, field), dtype=float)
            y = np.asarray(getattr(t, field), dtype=float)
            scale = max(float(np.max(np.abs(x))), 1e-300)
            out = max(out, float(np.max(np.abs(y - x))) / scale)
    return out


@pytest.mark.parametrize("label,ks", [
    ("whole range", np.linspace(0.05, 300.0, 8)),
    ("narrow band", np.linspace(120.0, 150.0, 8)),
])
def test_the_batch_is_the_serial_integration(label, ks, env):
    """**The gate.** Same system, same tolerances, same answer."""
    worst = _worst(_serial(env, ks), _batched(env, ks))
    assert worst < TOLERANCE, (
        f"batched and serial acoustic solutions disagree by {worst:.3e} over "
        f"the {label} — above the {TOLERANCE:.0e} this file allows, which is "
        "already three decades of slack on the integrator's own rtol. "
        "Adopting the batch would move every spectrum in the bundle and the "
        "move would look like physics."
    )


def test_the_batch_preserves_mode_order(env):
    """Mode *i* out is mode *i* in.

    A transposed or reversed stack would still agree on every norm, every
    maximum and every aggregate — and would silently pair each $k$ with
    another mode's solution. Checking the returned `k_com` is not enough
    either, since that is copied from the input: this compares each batched
    mode against **its own** serial counterpart, which is the only comparison
    a transposition fails.
    """
    ks = np.array([5.0, 80.0, 200.0])
    for i, (s, t) in enumerate(zip(_serial(env, ks), _batched(env, ks))):
        assert t.k_com == pytest.approx(float(ks[i]))
        scale = max(float(np.max(np.abs(s.delta_T))), 1e-300)
        moved = float(np.max(np.abs(t.delta_T - s.delta_T))) / scale
        assert moved < TOLERANCE, f"mode {i} (k={ks[i]}) is not its own solution"


def test_one_mode_batched_is_the_serial_answer(env):
    """The degenerate case must not be a special case."""
    k = 60.0
    assert _worst(_serial(env, [k]), _batched(env, [k])) < TOLERANCE


def test_the_comparison_fails_on_a_wrong_pairing(env):
    """**The negative control, as T-44 requires.**

    T-44 is a gate that printed PASS on a `nan`; its lesson is that a gate is
    not tested by the run that passes it. Here the batched modes are paired
    with the *wrong* serial ones, and `_worst` must notice. If it does not,
    then the assertions above would pass on a transposed stack and this file
    would be decoration.
    """
    ks = np.array([5.0, 200.0])
    serial = _serial(env, ks)
    batched = _batched(env, ks)
    assert _worst(serial, list(reversed(batched))) > TOLERANCE, (
        "pairing each mode with another mode's solution went unnoticed, so "
        "the comparison cannot distinguish a correct batch from a scrambled "
        "one"
    )
