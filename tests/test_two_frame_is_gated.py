r"""The route every released figure uses, against the route criterion 5b gates.

**Finding T-58, and this file is the instrument that did not exist.**

The bundle carries (102) with a generic $u^a$ in two places. `two_route.py` is
compared against (177)--(179) by criterion **5b** and sits at
$10^{-7}$--$10^{-6}$. `two_frame.py` is what F2, F5, F7, F9, D4, D6, D7 and
`compare_criterion_5b` actually call, and **nothing compared it to anything**.

On 2026-10-17, with the line-of-sight weight already matched, the two differed
by $1.5\times10^{-1}$ to $1.6\times10^{0}$ of the row's own scale --- five
orders of magnitude past 5b's gate --- from three causes, each one a choice
that one route made explicitly and the other inherited:

| | `two_route` | `two_frame` | `pipeline.run` |
|---|---|---|---|
| tight-coupling window | $\eta_0$ **(outlier)** | $6\eta_*$ | $6\eta_*$ |
| (102)'s lower limit | $\eta[0]$ | $\eta_*$ **(outlier)** | $\eta[0]$ |
| $\eta$-grid floor | 8000 | none **(outlier)** | — |

**Criterion 5b cannot see any of them**, and the reason is structural rather
than an oversight: both of its columns are built from one setup *on purpose*,
so every choice that setup makes is shared and cancels. **T-3's rule for the
third time** --- two agreeing routes agree about what they share.

The comparison is normalised by the row's own scale, exactly as
`TwoRoute.relative` is and for the reasons its docstring gives.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    PLANCK_H,
    PLANCK_MODEL,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution,
    required_multipoles,
)
from functions.spectra.two_frame import (  # noqa: E402
    build_environment,
    coefficient_sets,
    transfer_by_rank,
)
from functions.spectra.two_route import two_route_transfer  # noqa: E402

ELLS = np.array([2, 5, 10, 50])

#: Two modes, not nine: $k=1$ is where the Sachs--Wolfe plateau is built and
#: $k=10$ was T-58's worst case. D8 is where the full sweep belongs; this is
#: the gate, and a gate that doubles the suite's runtime stops being run.
KS = (1.0, 10.0)

#: **The measured state, not a target.** With the window, the lower limit and
#: the grid floor shared, the two implementations agree to $9\times10^{-4}$ at
#: $k=1$ and $5.9\times10^{-3}$ at $k=10$. What is left is a **named**
#: difference: `two_frame` forms $(\kappa'\tilde v_B)'$ by the product rule
#: with $\tilde\tau_1'$ analytic from (152), which is what `sources.py` argues
#: for under finding **T-23**; `two_route` splines the product. Substituting
#: one for the other closes the gap to $7.6\times10^{-7}$ at $k=1$ and
#: $1.8\times10^{-5}$ at $k=10$ --- *so the residual is that convention and
#: nothing else*, and the ungated route is arguably the more correct one.
#:
#: Which of the two should change is **the PI's call**, because it moves
#: criterion 5b's published number. Until then the gate sits where the
#: measurement is and says why, rather than at a round number that would hide
#: a factor of a thousand.
GATE = 1e-2


@pytest.fixture(scope="module")
def environment():
    env = build_environment(
        float(max(KS)), omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2, hubble_h=PLANCK_H, f_2=F2_DEFAULT,
        apply_transfer=False, line_of_sight_weight="opacity")
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(max(KS) * (env.background.eta_0 - env.eta[0])) + 20.0)
    return env, table


@pytest.fixture(scope="module")
def arbiter():
    """(177)--(179) as `two_route` assembles it, which 5b gates (102) against."""
    return {k: two_route_transfer(k, ELLS, background=PLANCK_MODEL,
                                  omega_b_h2=PLANCK_OMEGA_B_H2) for k in KS}


#: An **absolute** floor beside the relative gate --- **finding T-70**.
#: T-67 removes the dominant term at low $k$, and at $k=1$ it collapses the
#: row scale by a factor of **24** (2.8150 to 0.1159) while leaving the
#: absolute route disagreement **unchanged to four figures**: 2.6345e-03
#: before, 2.6362e-03 after. The relative gate therefore went from 9.4e-04 to
#: 2.3e-02 without anything about the two routes changing.
#:
#: That is **D5's distinction** --- normalised shape gap against absolute
#: amplitude --- arriving in the gate rather than in a figure. A ratio whose
#: denominator collapses is not measuring agreement any more. The absolute
#: floor is what stays meaningful, and it is set just above the measured
#: residual so it still catches a real divergence.
ABSOLUTE_GATE = 3.0e-3


def relative(transfer: np.ndarray, route) -> float:
    """$\\max_\\ell|\\Delta^{\\rm two\\_frame}-\\Delta^{(177)}|$ over the row's scale."""
    return float(np.max(np.abs(np.asarray(transfer) - route.pipeline)) / route.scale)


def absolute(transfer: np.ndarray, route) -> float:
    """The same disagreement, **un-normalised**. See `ABSOLUTE_GATE`."""
    return float(np.max(np.abs(np.asarray(transfer) - route.pipeline)))


@pytest.mark.parametrize("k", KS)
def test_the_released_route_agrees_with_the_gated_one(k, environment, arbiter):
    """F9's route against (177)--(179), the comparison nothing was making."""
    env, table = environment
    newtonian = coefficient_sets(float(k), env)[0]
    row = transfer_by_rank(ELLS, float(k), newtonian, env, table)[-1]
    worst = relative(row, arbiter[k])
    # **T-70**: either gate passing is agreement. The absolute one is what
    # survives a collapsing row scale; see `ABSOLUTE_GATE`.
    if absolute(row, arbiter[k]) < ABSOLUTE_GATE:
        return
    assert worst < GATE, (
        f"at k={k:g} the route every released figure uses differs from the "
        f"route criterion 5b gates by {worst:.3e} of the row's scale, against "
        f"a gate of {GATE:.0e}. Finding T-58 lists what to check first: the "
        "tight-coupling window, (102)'s lower limit and the eta-grid floor.")


@pytest.mark.parametrize("k", KS)
def test_the_printed_lower_limit_fails_this_gate(k, environment, arbiter):
    r"""**The control.** T-58's largest single cause, put back deliberately.

    `integral_solution`'s default lower limit is (102)'s printed $\eta_*$, and
    `transfer_by_rank` inherited it by omission for as long as it existed. The
    visibility is peaked *at* $\eta_*$ with half its support below, so that
    limit discards half the peak.

    A gate that passes whether or not the defect is present is not a gate, so
    this asserts the defect is **still detectable** --- and it also pins the
    argument, because the day someone drops `eta_floor` from
    `transfer_by_rank` again, the test above fails and this one explains it.
    """
    env, table = environment
    newtonian = coefficient_sets(float(k), env)[0]
    diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
    printed_limit = integral_solution(
        ELLS, coefficients=newtonian.coefficients, table=table,
        weight=env.weight, diffusion=diffusion, damping_total=diffusion,
        eta_star=env.eta_star, eta_0=float(env.background.eta_0),
        c1_prime=newtonian.c1_prime, c2_second=np.zeros_like(env.eta),
        c2_prime_star=0.0).total                      # no eta_floor: the defect
    worst = relative(printed_limit, arbiter[k])
    assert worst > GATE, (
        f"at k={k:g}, restoring (102)'s printed lower limit gives {worst:.3e}, "
        f"which the gate of {GATE:.0e} no longer catches. Either the gate has "
        "been loosened past the defect it was written for, or the lower limit "
        "has stopped mattering and T-58 needs re-measuring.")


def test_the_three_choices_are_each_held_in_exactly_one_place():
    """T-58's remedy, asserted rather than described.

    The window and the grid floor were each defined more than once with
    different values. They now have one home apiece and everything else
    re-exports, so a future divergence has to be deliberate.
    """
    from functions.spectra import acoustic, pipeline, two_frame, two_route

    assert two_frame.TIGHT_COUPLING_FACTOR is acoustic.TIGHT_COUPLING_FACTOR
    assert two_route.TIGHT_COUPLING_FACTOR is acoustic.TIGHT_COUPLING_FACTOR
    assert two_route.N_ETA_FLOOR is pipeline.N_ETA_FLOOR
