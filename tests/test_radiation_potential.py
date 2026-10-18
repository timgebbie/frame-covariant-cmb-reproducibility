r"""The radiation-era potential, against its own limits and an ODE solver.

**Approximation A-3's missing piece, checked before it is used.**
`radiation_era_potential` is a closed form, so it is checkable three ways that
share nothing: the two analytic limits, the differential equation it claims to
solve, and `scipy`'s spherical Bessel function --- $\Phi=3\Phi_i j_1(x)/x$ is
the same statement as $3\Phi_i(\sin x-x\cos x)/x^3$ only if the identity
$j_1(x)=(\sin x-x\cos x)/x^2$ holds, and asserting it ties the derivation to a
library that did not come from it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.special import spherical_jn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.spectra.potentials import radiation_era_potential  # noqa: E402

KS = (1.0, 20.0, 300.0)


def test_the_superhorizon_limit_is_the_primordial_value():
    r"""$\Phi\to\Phi_i$ as $x\to0$, because $\sin x-x\cos x\to x^3/3$.

    This is what makes the normalisation mean anything: `amplitude` is the
    super-horizon potential, not a value at some arbitrary epoch.
    """
    for k in KS:
        eta = np.array([0.0, 1e-9, 1e-6]) / k
        phi = radiation_era_potential(k, eta, amplitude=0.7)
        assert np.allclose(phi, 0.7, rtol=1e-9), f"k={k}: {phi}"


@pytest.mark.parametrize("k", KS)
def test_the_subhorizon_envelope_decays_as_x_squared(k):
    r"""$\Phi\simeq-3\Phi_i\cos x/x^2$ for $x\gg1$. **This decay is A-3.**

    Asserted as a **fitted log-log slope** over a decade, not as a ratio of two
    windowed maxima. The first draft did the latter and read $92.6$ where
    $x^{-2}$ wants $100$ --- because a finite window does not always contain a
    point where $|\cos x|=1$, so its maximum undershoots the envelope by
    however far the nearest extremum happens to sit. *That is a sampling
    artefact being read as physics*, which is the error this bundle exists to
    avoid, so the slope is fitted instead.
    """
    x = np.linspace(20.0, 400.0, 200_000)
    phi = np.abs(radiation_era_potential(k, x * np.sqrt(3.0) / k))
    # Envelope: the maximum within each of 40 half-period bins, each of width
    # pi in x, so every bin contains an extremum by construction.
    edges = np.arange(20.0, 400.0, np.pi)
    centres, peaks = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (x >= lo) & (x < hi)
        centres.append(0.5 * (lo + hi))
        peaks.append(float(np.max(phi[m])))
    slope = np.polyfit(np.log(centres), np.log(peaks), 1)[0]
    assert slope == pytest.approx(-2.0, abs=0.02), (
        f"k={k}: the envelope falls as x^{slope:.3f}, not x^-2")


@pytest.mark.parametrize("k", KS)
def test_it_solves_the_equation_it_was_derived_from(k):
    r"""$\Phi''+\tfrac4\eta\Phi'+\tfrac{k^2}3\Phi=0$, integrated independently.

    **The derivation's only real check.** The two limits above are necessary
    and a wrong solution of the right equation can satisfy both; this
    integrates the equation with `solve_ivp` from the series initial condition
    and requires the closed form to land on it.
    """
    eta0, eta1 = 1e-4 / k, 40.0 / k

    def rhs(eta, y):
        return [y[1], -4.0 / eta * y[1] - k**2 / 3.0 * y[0]]

    x0 = k * eta0 / np.sqrt(3.0)
    y0 = [1.0 - x0**2 / 10.0, -(k / np.sqrt(3.0)) * x0 / 5.0]
    grid = np.linspace(eta0, eta1, 400)
    numeric = solve_ivp(rhs, (eta0, eta1), y0, t_eval=grid,
                        rtol=1e-11, atol=1e-14).y[0]
    closed = radiation_era_potential(k, grid)
    assert np.max(np.abs(numeric - closed)) < 2e-6, (
        f"k={k}: the closed form departs from its own ODE by "
        f"{np.max(np.abs(numeric - closed)):.2e}")


@pytest.mark.parametrize("k", KS)
def test_the_closed_form_is_three_j1_over_x(k):
    r"""$3\Phi_i j_1(x)/x$, against an implementation that is not this one."""
    eta = np.linspace(0.01, 40.0, 1000) / k
    x = k * eta / np.sqrt(3.0)
    assert np.allclose(radiation_era_potential(k, eta),
                       3.0 * spherical_jn(1, x) / x, rtol=1e-10)


def test_the_two_branches_agree_at_the_crossover(k=1.0):
    r"""The $x<0.1$ branch is a conditioning choice, not a different model.

    **Both branches evaluated at the same $x$**, which is the only way to see a
    seam. The first draft differenced $\Phi$ at *adjacent* $x$ across the
    crossover and read $2\times10^{-6}$ --- which is
    $|d\Phi/dx|\,\Delta x=0.02\times10^{-4}$, the function's own slope, and
    says nothing about either branch.

    $(\sin x-x\cos x)/x^3$ has relative error $\sim3\varepsilon/x^2$ and the
    series truncated at $x^4$ omits $x^6/15120$; at $x=0.1$ those are
    $3\times10^{-14}$ and $6.6\times10^{-11}$, so the two must agree to about
    $10^{-10}$.
    """
    x = 0.1
    closed = 3.0 * (np.sin(x) - x * np.cos(x)) / x**3
    series = 1.0 - x**2 / 10.0 + x**4 / 280.0 - x**6 / 15120.0
    assert abs(closed - series) < 1e-12, (
        f"the two branches differ by {closed-series:.2e} at the crossover")
    # Straddle it: 0.0999 takes the series branch, 0.1001 the closed one, and
    # both must land on the exact value.
    for probe in (0.0999, 0.1001):
        exact = 3.0 * (np.sin(probe) - probe * np.cos(probe)) / probe**3
        got = float(radiation_era_potential(k, np.array([probe * np.sqrt(3.0) / k]))[0])
        assert got == pytest.approx(exact, abs=1e-12), f"branch seam at x={probe}"


def test_degenerate_inputs_raise():
    with pytest.raises(ValueError):
        radiation_era_potential(0.0, np.array([1.0]))
    with pytest.raises(ValueError):
        radiation_era_potential(-1.0, np.array([1.0]))
    with pytest.raises(ValueError):
        radiation_era_potential(1.0, np.array([-1.0]))
