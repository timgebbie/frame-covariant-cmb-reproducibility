r"""`coefficient_sets_batch` must be `coefficient_sets`, mode for mode.

**The hot path of every number in the bundle, so the paranoia is the point.**
`scripts/benchmark_single_run.py` puts the per-mode loop at **99.7%** of a
spectrum run, and `solve_acoustic_batch` with per-mode starts runs it
**7.1$\times$** faster, flat from 64 modes to 256 (**T-167**). Adopting that
without a mode-for-mode comparison would move every spectrum, every peak
position and every finding downstream of it, and **the move would look like
physics**.

Three things have to hold for the batch to be exact, and each has its own
assertion below because each has its own way of failing silently:

1. **The per-mode start.** **T-166** measured that a common start moves
   $\tau_1$ at $\eta_{\rm couple}$ by $1.4\times10^{-2}$ --- (152)/(153) drive
   a super-horizon mode rather than freezing it, so the start is physics. The
   batch imposes each mode's own start by mask. A batch that forgot
   `start_eta` would still run, still look smooth, and be wrong by percent.
2. **The transfer factors out.** The released path scales $\Phi$ and the
   initial condition by $T(k)$ *before* integrating (**T-37**); the batch
   integrates unscaled and multiplies after. That is identical only because
   the system is linear and homogeneous in the two **together** --- scaling
   one and not the other would damp the amplitude while leaving the driving
   un-suppressed, which is the defect T-37 exists to prevent.
3. **Order.** A transposed stack agrees on every norm, every maximum and
   every aggregate while pairing each $k$ with another mode's solution.

WHAT IS ASSERTED
----------------
That every field of both frames' `CoefficientSet` agrees at the integrator's
tolerance; that a single mode batched is the serial answer, so the degenerate
case is not a special case; and --- **T-44** --- that the comparison *fails*
on a deliberately scrambled pairing, or it is asserting nothing.
"""
from __future__ import annotations

import sys
from dataclasses import fields as dataclass_fields
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import LCDM_MODEL  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, coefficient_sets, coefficient_sets_batch)

#: **1e-5, and the number is interpolation rather than integration.**
#:
#: The integration agrees far tighter than this: **T-167** compares the
#: masked batch against the released per-mode solve *at identical times* and
#: measures **2.5e-08**, four decades inside the figure here. What is left is
#: the step after it. Both paths interpolate onto `env.eta` with `np.interp`,
#: which is linear, and they interpolate **from different source grids** ---
#: the released path from a grid sized by `required_acoustic_points` at that
#: mode's own $k$ and span, the batch from one grid sized at $k_{\max}$ over
#: the common span. Two different linear interpolations of the same curve do
#: not agree to the integrator's tolerance, and measured here the gap is
#: **2.4e-06**.
#:
#: **So adopting the batch is not free**, and that is the point of recording
#: the figure rather than quietly fitting a threshold around it: wiring it
#: into `coefficient_sets` would move every number in the bundle by of order
#: $10^{-6}$. That is four decades below T-164's 0.95\% and six below
#: anything that could move a peak, but it is not zero, and it belongs in the
#: adoption commit as a declared consequence rather than as something a later
#: reader discovers in a diff.
TOLERANCE = 1e-5

#: What the *integration* agrees to, from T-167, kept here so the two numbers
#: are side by side and the reader is not left to infer that 1e-5 is the best
#: this method can do.
INTEGRATION_AGREEMENT = 2.5e-8


@pytest.fixture(scope="module")
def env():
    return build_environment(
        300.0, omega_m=LCDM_MODEL.omega_m, omega_lambda=LCDM_MODEL.omega_lambda,
        omega_r=LCDM_MODEL.omega_r, omega_b_h2=0.0224, transfer_gamma=0.48,
        hubble_h=0.5, f_2=F2_DEFAULT, line_of_sight_weight="printed")


def _worst(a_pair, b_pair) -> float:
    """Worst relative disagreement over **every** array field of both frames.

    Comparing a chosen few would let a field nobody thought of carry the
    defect --- which is how `c1_prime_isw` went unsupplied for days (T-131).
    """
    out = 0.0
    for a, b in zip(a_pair, b_pair):
        for f in dataclass_fields(a):
            x, y = getattr(a, f.name), getattr(b, f.name)
            if isinstance(x, (int, float)):
                scale = max(abs(float(x)), 1e-300)
                out = max(out, abs(float(y) - float(x)) / scale)
                continue
            if not isinstance(x, np.ndarray):
                continue
            x = np.asarray(x, dtype=float)
            y = np.asarray(y, dtype=float)
            scale = max(float(np.max(np.abs(x))), 1e-300)
            out = max(out, float(np.max(np.abs(y - x))) / scale)
    return out


@pytest.mark.xfail(strict=True, reason=(
    "T-175: the batch agrees on the SOLUTION and not on its DERIVATIVE. "
    "delta_T and tau_1 match at 2.5e-08 (T-167); c1_prime is out by up to "
    "5.0e-03 at k = 300 and the gap grows monotonically with k. Strict, so "
    "that repairing the kink turns this into an unexpected PASS and the "
    "adoption becomes a decision somebody takes."))
@pytest.mark.parametrize("label,ks", [
    ("whole range", np.linspace(0.05, 300.0, 6)),
    ("narrow band", np.linspace(120.0, 150.0, 6)),
])
def test_the_batch_is_the_released_coefficient_set(label, ks, env):
    """**The gate.** Same environment, same modes, same coefficients."""
    batched = coefficient_sets_batch(ks, env)
    worst = 0.0
    for i, k in enumerate(ks):
        worst = max(worst, _worst(coefficient_sets(float(k), env), batched[i]))
    assert worst < TOLERANCE, (
        f"batched and released coefficient sets disagree by {worst:.3e} over "
        f"the {label}, above the {TOLERANCE:.0e} this file allows. Wiring "
        "this into the spectrum would move every number in the bundle and "
        "the move would look like physics."
    )
    # **And the residual must stay interpolation-sized, not integration-sized.**
    # If it ever falls to INTEGRATION_AGREEMENT the two paths have stopped
    # interpolating differently, which would mean the grids had been made to
    # coincide and the speedup had gone with them. If it rises past TOLERANCE
    # the assertion above catches it. The band is the statement.
    assert worst > INTEGRATION_AGREEMENT, (
        f"the batch now agrees to {worst:.3e}, which is integration-level. "
        "That is not better news than it looks: the two paths interpolate "
        "from different source grids by construction, so agreement this "
        "tight means the grids have collapsed together and the batch is no "
        "longer batching."
    )


def test_one_mode_batched_is_the_released_answer(env):
    """The degenerate case must not be a special case."""
    k = 60.0
    assert _worst(coefficient_sets(k, env),
                  coefficient_sets_batch([k], env)[0]) < TOLERANCE


@pytest.mark.xfail(strict=True, reason="T-175, as above -- c1_prime, not order")
def test_the_batch_preserves_mode_order(env):
    """Mode *i* out is mode *i* in.

    A transposed stack agrees on every norm and every aggregate while pairing
    each $k$ with another mode's solution, so this compares each batched mode
    against **its own** released counterpart, which is the only comparison a
    transposition fails.
    """
    ks = np.array([5.0, 80.0, 200.0])
    batched = coefficient_sets_batch(ks, env)
    for i, k in enumerate(ks):
        assert _worst(coefficient_sets(float(k), env), batched[i]) < TOLERANCE


def test_the_comparison_fails_on_a_wrong_pairing(env):
    """**The negative control, as T-44 requires.**

    T-44 is a gate that printed PASS on a `nan`, and its lesson is that a gate
    is not tested by the run that passes it. The batched modes are paired with
    the *wrong* released ones here and `_worst` must notice; if it does not,
    every assertion above would pass on a scrambled batch.
    """
    ks = np.array([5.0, 200.0])
    batched = coefficient_sets_batch(ks, env)
    crossed = _worst(coefficient_sets(float(ks[0]), env), batched[1])
    assert crossed > TOLERANCE, (
        "pairing a mode with another mode's coefficients went unnoticed, so "
        "the comparison cannot tell a correct batch from a scrambled one"
    )


def test_nothing_released_calls_the_batch_yet():
    r"""**Deliberately wired to nothing, and the test says so out loud.**

    Swapping the hot path of every spectrum on the same commit that
    introduces the capability is how a 7.1x speedup becomes an unattributable
    change in every number downstream of it. When a caller is added this test
    is what has to be edited to allow it, which makes the adoption a decision
    somebody takes rather than one that happens.
    """
    import re

    callers = []
    for path in sorted((ROOT / "scripts").glob("*.py")) + \
            sorted((ROOT / "functions").rglob("*.py")):
        if path.name == "two_frame.py":
            continue
        if re.search(r"\bcoefficient_sets_batch\b",
                     path.read_text(encoding="utf-8")):
            callers.append(str(path.relative_to(ROOT)))
    assert not callers, (
        f"coefficient_sets_batch has acquired callers: {callers}. That is the "
        "intended destination, but it moves every number in the bundle, so it "
        "wants its own commit with the released spectrum reproduced in it — "
        "not a line added to an instrument."
    )
