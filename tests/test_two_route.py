r"""Criterion 5b's gate, and the controls that make it one.

Decision **S4c**. *Annals II* writes its integral solution twice --- (102)
carried with a generic $u^a$ and specialised afterwards, and (177)--(179)
assembled in the Newtonian frame from the start --- and recovers the second from
the first symbolically, saying so on the page. Nothing evaluates the two and
compares them. These tests do, and then check that the check can fail.
"""

from __future__ import annotations

import numpy as np
import pytest

from functions.background.flrw import (
    CDM_MODEL,
    LCDM_MODEL,
    PLANCK_MODEL,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.two_route import TwoRoute, two_route_transfer

#: The gate `scripts/diagnostic_d8_criterion_5b_gate.py` applies. Named once,
#: here, so the test and the diagnostic cannot drift to two thresholds.
GATE = 1.0e-3

ELLS = np.array([2, 10, 50, 200])

BACKGROUNDS = [
    pytest.param(CDM_MODEL, 0.0224, id="CDM"),
    pytest.param(LCDM_MODEL, 0.0224, id="LCDM"),
    pytest.param(PLANCK_MODEL, PLANCK_OMEGA_B_H2, id="PLANCK"),
]


@pytest.mark.parametrize("background,omega_b_h2", BACKGROUNDS)
@pytest.mark.parametrize("k", [3.0, 60.0, 300.0])
def test_the_two_routes_agree_on_every_background_the_bundle_ships(
        background, omega_b_h2, k):
    r"""Criterion 5b's gate, at three modes on each of the three backgrounds.

    **All three, not one.** Criterion 5b names *the CDM and $\Lambda$CDM
    spectra*, and the external comparison is run on `PLANCK_MODEL`; a gate that
    swept only the middle one would leave the criterion's own stated scope and
    the comparison's actual cosmology both ungated. They are not
    interchangeable: Einstein--de Sitter is the hardest case here, because the
    primary and line-of-sight pieces largely cancel at low $\ell$ and the
    denominator of any fractional measure is correspondingly small.
    """
    result = two_route_transfer(k, ELLS, background=background,
                                omega_b_h2=omega_b_h2)
    assert result.worst < GATE, (
        f"at k={k} the two routes differ by {result.worst:.2e}; they are the "
        "same calculation written in two orders and must not")


def test_the_gate_is_not_merely_passed_but_passed_with_room():
    r"""The margin is part of the claim.

    A gate sitting just above the number it measures is a gate that fails on
    the next platform for reasons that are not scientific --- finding
    **T-15**, where residual artefacts agreed across machines to under one
    significant figure. This asserts the measured value is at least an order of
    magnitude inside, so that a future failure means something changed rather
    than something drifted.
    """
    result = two_route_transfer(60.0, ELLS)
    assert result.worst < GATE / 10.0, (
        f"the gate's margin has gone: {result.worst:.2e} against {GATE:.0e}. "
        "Find out what moved before widening anything")


def test_a_gate_that_cannot_fail_is_not_a_gate():
    r"""The negative control, and **finding T-44**'s standing reminder.

    Two ways this comparison can report a pass it never measured, both of which
    it did at least once:

    *A difference it should refuse.* A `TwoRoute` carrying a route that is
    wrong by 1% must report 1%, not something smaller --- the normalisation is
    by the row's own scale, so a defect at the largest multipole is reported at
    its own size.

    *An undefined comparison.* A mode whose transfer is zero at every $\ell$
    has an empty domain. `nan >= gate` is `False` in IEEE 754, so a comparison
    that returned `nan` there would take the passing branch. It must raise.
    """
    ells = np.array([2, 10, 50])
    good = np.array([1.0, 0.5, 0.25])

    broken = TwoRoute(k=60.0, ells=ells, pipeline=good,
                      generic=good + np.array([0.01, 0.0, 0.0]), n_eta=8000)
    assert broken.worst == pytest.approx(0.01, rel=1e-12)
    assert broken.worst > GATE, "a 1% defect must not pass a 0.1% gate"

    empty = TwoRoute(k=60.0, ells=ells, pipeline=np.zeros(3),
                     generic=np.zeros(3), n_eta=8000)
    with pytest.raises(ValueError, match="nothing to compare"):
        _ = empty.worst


def test_the_exponential_tail_cannot_manufacture_a_failure():
    r"""Below the Bessel turning point both routes return zero, and that is a
    pass, not a `nan` and not a divergence.

    At $k=0.3$ the transfer at $\ell=200$ is $4\times10^{-216}$ and at
    $\ell=600$ it is exactly zero. A pointwise fractional difference there
    divides noise by noise or zero by zero; against the row's own scale it is
    zero, which is both finite and true --- those modes contribute nothing to
    $C_\ell=\int\Delta_\ell^2P\,dk$ either.
    """
    result = two_route_transfer(0.3, np.array([2, 50, 200, 600]))
    assert np.all(np.isfinite(result.relative))
    assert result.relative[-1] == 0.0


def test_the_interpolant_at_eta_star_is_what_T46_says_it_is():
    r"""**Finding T-46**, pinned so it cannot be quietly fixed or quietly lost.

    `pipeline.run` reads its primary source at $\eta_*$ with `np.interp` ---
    linear --- while `integral_solution` reads the same quantity with a
    `CubicSpline`. On one grid the two arrays are pointwise identical, so with
    the interpolants matched the boundary terms agree and what is left is the
    algebra; with them unmatched the difference is one to three orders of
    magnitude larger and is **the shipped pipeline's boundary read**, not a
    disagreement between (102) and (177)--(179).

    The gate compares the algebra. This test holds the other number in view, so
    that the day the interpolant is changed --- which is open question **Q7**,
    the PI's call --- this test fails and says why rather than leaving a silent
    improvement in a figure nobody re-derived.
    """
    matched = two_route_transfer(30.0, ELLS, background=CDM_MODEL)
    as_shipped = two_route_transfer(30.0, ELLS, background=CDM_MODEL,
                                    match_interpolation=False)
    assert matched.worst < GATE / 10.0
    assert as_shipped.worst > 10.0 * matched.worst, (
        "T-46 says the unmatched comparison is dominated by the interpolant at "
        f"eta_*. It now reports {as_shipped.worst:.2e} against the matched "
        f"{matched.worst:.2e}. If that gap has closed, the interpolant changed "
        "and Q7 was answered without the record being updated")


def test_the_eta_grid_is_derived_from_k_and_not_fixed():
    r"""**Finding T-45.** The grid was `linspace(..., 4000)` at every $k$, and
    at $k=60$ that made the two routes agree two hundred times better than they
    do, because both were un-converged in the same direction.

    `required_n_eta` exists so that nothing in this bundle fixes a grid. This
    asserts the comparison obeys it: a mode an order of magnitude higher must
    be given a correspondingly finer grid, not the same one.
    """
    low = two_route_transfer(10.0, ELLS)
    high = two_route_transfer(600.0, ELLS)
    assert high.n_eta > 3 * low.n_eta, (
        f"k=600 was given {high.n_eta} points against k=10's {low.n_eta}. A "
        "grid that does not move with k is T-45 again")
