r"""The $k$ grid, against a closed form. Finding **T-56**.

**This file contains no physics.** For a pure Sachs--Wolfe transfer
$T_\ell(k)=j_\ell(k\,\Delta\eta)$ with $\mathcal P\propto k^{n_s-4}$ at
$n_s=1$, the spectrum integral collapses to

    Int_0^inf dk j_l(k dEta)^2 / k  =  1 / [2 l (l+1)],

independent of $\Delta\eta$ --- so the quadrature error of a $k$ grid can be
read off against an exact number at every multipole, with nothing in the
comparison that could be mistaken for a model. That is the whole instrument.

**Why it had to be built.** `required_n_eta` derives the $\eta$ grid from the
oscillation it has to resolve. Nothing derived the $k$ grid. F9 shipped
``np.arange(0.05, 1500.0, np.pi/3)`` under a comment that correctly rejects a
logarithmic grid and then never asks what the linear spacing must resolve. The
control below measures what that costs: **22.5%** at $\ell=2$ on
$\Lambda$CDM, non-monotonic in $\ell$.

`scipy.special.spherical_jn` is used deliberately in place of the bundle's own
`BesselTable`. T-3's lesson is that two agreeing routes agree about what they
share; an arbiter built from the kernel under test shares the kernel. The last
test ties the two together so the independence is stated rather than assumed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.special import spherical_jn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.pipeline import (  # noqa: E402
    K_POINTS_PER_PERIOD,
    required_k_points,
    required_n_eta,
)

#: The three released lines of sight, $\Delta\eta=\eta_0-\eta_*$ in $1/H_0$,
#: as `diagnostic_d9_acoustic_scale.py` reports them.
R_THETA = {"CDM (Einstein-de Sitter)": 1.940448,
           "LCDM": 3.195556,
           "PLANCK_MODEL": 3.128924}

ELLS = (2, 5, 10, 30, 100, 200, 400)

#: F9's shipped grid, verbatim from `scripts/figure_f9_acoustic_spectrum.py`.
F9_DK, F9_K_MAX = np.pi / 3.0, 1500.0


def quadrature(k: np.ndarray, r_theta: float, ell: int) -> float:
    """The released quadrature rule --- `np.trapezoid` --- on the SW integrand."""
    return float(np.trapezoid(spherical_jn(ell, k * r_theta) ** 2 / k, k))


def exact(ell: int) -> float:
    r"""$\int_0^\infty dk\,j_\ell^2(k\Delta\eta)/k=1/[2\ell(\ell+1)]$."""
    return 1.0 / (2.0 * ell * (ell + 1.0))


def grid(k_max: float, r_theta: float, *, points_per_period: int) -> np.ndarray:
    n = required_k_points(k_max, r_theta, points_per_period=points_per_period)
    return np.linspace(0.05, k_max, n)


@pytest.mark.parametrize("name,r_theta", sorted(R_THETA.items()))
def test_the_derived_grid_reproduces_the_closed_form(name, r_theta):
    r"""`required_k_points` returns a grid good to 1% over the acoustic band.

    One percent is not a tuning target: the measured worst case is 0.4% and the
    assertion is loose enough that a change which *improves* the grid does not
    have to edit a test, which is what makes a tolerance a gate rather than a
    transcript.
    """
    k = grid(F9_K_MAX, r_theta, points_per_period=K_POINTS_PER_PERIOD)
    worst = max(abs(quadrature(k, r_theta, l) / exact(l) - 1.0) for l in ELLS)
    assert worst < 0.01, (
        f"{name}: the derived k grid ({k.size} points, "
        f"{(np.pi / r_theta) / (k[1] - k[0]):.2f} samples per j_l^2 oscillation) "
        f"misses the closed form by {worst:.1%}")


@pytest.mark.parametrize("name,r_theta", sorted(R_THETA.items()))
def test_f9s_shipped_grid_does_not(name, r_theta):
    r"""**The control, and the finding.** A gate that passes on the defect it
    was written for is not a gate.

    F9's $dk=\pi/3$ gives fewer than one sample per $j_\ell^2$ oscillation on
    both $\Lambda$CDM-like backgrounds. On Einstein--de Sitter, whose
    $\Delta\eta$ is 40% shorter, it gives 1.55 and the error stays near a
    percent --- which is precisely why the defect survived: **the figure that
    was eyeballed most often was the one background where the grid nearly
    worked.**
    """
    k = np.arange(0.05, F9_K_MAX, F9_DK)
    per_period = (np.pi / r_theta) / F9_DK
    worst = max(abs(quadrature(k, r_theta, l) / exact(l) - 1.0) for l in ELLS)
    if name.startswith("CDM"):
        assert per_period > 1.0 and worst < 0.02
        return
    assert per_period < 1.0, (
        f"{name}: dk=pi/3 should sample below one point per oscillation here")
    assert worst > 0.05, (
        f"{name}: the shipped grid was expected to miss the closed form by "
        f"more than 5% and missed it by {worst:.1%} --- if this now passes, "
        "the control has stopped controlling and T-56 needs re-measuring")


def test_the_error_is_non_monotonic_in_ell_which_is_why_it_moves_peaks():
    r"""Aliasing is not a bias, and that is the damaging part.

    A grid that were uniformly 20% low would cancel out of a spectrum
    normalised at $\ell=30$. This one is high at $\ell=2$, low at $\ell=30$ and
    high again at $\ell=100$ --- a ripple of a few percent whose sign turns
    over on a scale of tens in $\ell$. **That moves a peak**, and because each
    route's $T_\ell(k)$ aliases against the grid differently, it moves it by a
    different amount in each route, which is what made the two routes disagree
    about where the first peak was.
    """
    k = np.arange(0.05, F9_K_MAX, F9_DK)
    ratios = np.array([quadrature(k, R_THETA["PLANCK_MODEL"], l) / exact(l)
                       for l in ELLS])
    turns = int(np.sum(np.diff(np.sign(np.diff(ratios))) != 0))
    assert turns >= 2, (
        f"expected the error to turn over at least twice across l={ELLS}; "
        f"got ratios {np.round(ratios, 3)}")


def test_the_two_grid_rules_are_one_formula_read_along_two_axes():
    r"""`required_k_points` **is** `required_n_eta` with the span swapped.

    Both resolve $j_\ell(k\Delta\eta)$: one across $\eta$ at fixed $k$, one
    across $k$ at fixed $\Delta\eta$. If the two ever stop agreeing as
    arithmetic, one of them has acquired a fudge factor.
    """
    for k_max, span, ppp in ((1500.0, 3.128924, 3), (420.0, 1.940448, 12),
                             (60.0, 2.5, 7)):
        assert (required_k_points(k_max, span, points_per_period=ppp)
                == required_n_eta(k_max, span, points_per_period=ppp))


def test_degenerate_spans_raise_rather_than_returning_a_grid():
    for bad in ((0.0, 3.0), (1500.0, 0.0), (-1.0, 3.0), (1500.0, -3.0)):
        with pytest.raises(ValueError):
            required_k_points(*bad)


def test_the_independent_arbiter_and_the_shipped_kernel_are_the_same_function():
    r"""Ties `scipy.special.spherical_jn` to `BesselTable`.

    The arbiter above is independent *so that* it can judge the grid without
    sharing the kernel. Independence is only worth having if the two
    implementations are then shown to compute the same object; otherwise the
    closed form is testing scipy and nothing else.

    **They agree to the table's interpolation error and not beyond, and the
    difference matters.** `BesselTable` is a cubic spline through $j_\ell$
    sampled at twelve points per oscillation, so it is not the kernel but a
    stated approximation to it. Measured here, against its own peak amplitude:

        l             2        5       10       30      100      200
        |table-scipy| / max|j_l|
                  4.2e-6   3.6e-6   3.1e-6   2.5e-6   2.1e-6   1.8e-6

    Flat in $\ell$, which is what a fixed points-per-period spline gives and
    what a kernel disagreement would not. The first draft of this test asserted
    `atol=5e-9` and failed --- it was measuring the spline, not the identity,
    and the fix was to say so rather than to loosen the number until it passed.
    """
    ells = np.array(ELLS)
    x = np.linspace(0.5, 400.0, 2000)
    table = BesselTable.build(ell_max=int(ells.max()), ells=ells,
                              x_max=float(x.max()) + 20.0)
    for l in ELLS:
        exact_j = spherical_jn(int(l), x)
        scale = float(np.abs(exact_j).max())
        worst = float(np.abs(table(int(l), x) - exact_j).max()) / scale
        assert worst < 1e-5, (
            f"BesselTable and scipy differ by {worst:.2e} of the kernel's own "
            f"scale at l={l}. At twelve samples per period the spline is good "
            "to about 4e-6; an order of magnitude worse than that is a kernel "
            "disagreement, not an interpolation error.")
