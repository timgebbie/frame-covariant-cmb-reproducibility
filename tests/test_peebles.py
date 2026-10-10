r"""Peebles recombination, checked on its own before anything is built on it.

That phrase is the README's, and it is the acceptance for v1.1.0: the three-level
atom has to be right against the **standard ionisation history** as a standalone
object, because every later claim — the damping envelope, criterion 5b, the
acoustic peaks — inherits whatever it gets wrong.

So these tests check the physics, not the plumbing:

* the **freeze-out plateau**, which is the whole reason Saha is not enough;
* the **equilibrium limit**, where Peebles must agree with Saha or the initial
  condition is wrong;
* **initial-condition independence**, so the start redshift is not load-bearing;
* the **fudge factor's** size, measured rather than trusted;
* and the **visibility width**, the quantity S18 says fixes the Silk damping.
"""

from __future__ import annotations

import numpy as np
import pytest

from functions.background.flrw import Background
from functions.spectra.decoupling import (
    Recombination,
    RecombinationHistory,
    saha_ionisation,
)
from functions.spectra.peebles import RECFAST_FUDGE, peebles_ionisation


def _background() -> Background:
    """A realistic background. Recombination is atomic physics in a real universe.

    `CDM_MODEL` is Einstein-de Sitter, which is the right background for
    reproducing *Annals II* and the wrong one for asking where last scattering
    is: it has no radiation, so $H(z)$ at $z\\sim1100$ is not the physical one.
    """
    return Background(omega_m=0.315, omega_lambda=0.685, omega_r=9.2e-5, h0=1.0)


def test_the_residual_ionisation_freezes_out_near_two_parts_in_ten_thousand():
    r"""$x_e\to\sim2\times10^{-4}$ — the standard freeze-out, and Saha's blind spot.

    Recombination does not go to completion: the rate falls below the expansion
    rate and the remaining free electrons simply never find a proton. The
    residual is the single most quoted number in recombination and is the
    cleanest possible check that the three-level atom is wired correctly.
    """
    solution = peebles_ionisation(_background(), z_start=1800.0, z_end=100.0)
    assert 1.0e-4 < solution.freeze_out < 4.0e-4


def test_it_agrees_with_saha_while_equilibrium_still_holds():
    r"""At $z\gtrsim1600$ the gas **is** in equilibrium, so Peebles must be Saha.

    This is what makes the Saha initial condition legitimate rather than
    circular: the two agree in the regime where equilibrium is the physics, and
    separate exactly where it stops being.
    """
    solution = peebles_ionisation(_background(), z_start=1800.0, z_end=100.0)
    z = np.array([1700.0, 1650.0, 1600.0])
    peebles = solution.at(z)
    saha = saha_ionisation(z)
    assert np.all(np.abs(peebles - saha) / saha < 0.05)


def test_recombination_is_delayed_and_the_gap_grows():
    r"""Peebles recombines **later** than Saha, and the gap widens monotonically.

    Equilibrium overestimates how fast the universe recombines, because it
    ignores the Lyman-$\alpha$ bottleneck that $C_r$ encodes. By $z=800$ the two
    differ by orders of magnitude, and by $z=200$ Saha has reached $10^{-53}$ —
    a number with no physical content at all.
    """
    solution = peebles_ionisation(_background(), z_start=1800.0, z_end=100.0)
    z = np.array([1200.0, 1000.0, 800.0])
    ratio = solution.at(z) / saha_ionisation(z)

    assert np.all(ratio > 1.0), "equilibrium must recombine faster, not slower"
    assert ratio[0] < ratio[1] < ratio[2], "the gap must widen as freeze-out sets in"


def test_the_start_redshift_is_not_load_bearing():
    r"""Starting at $z=1800$ or $z=2200$ must give the same tail.

    If it did not, the answer would be a property of where the integration
    happened to begin. Same discipline as deriving a grid rather than choosing
    one — finding **T-3**.
    """
    low = peebles_ionisation(_background(), z_start=1800.0, z_end=100.0)
    high = peebles_ionisation(_background(), z_start=2200.0, z_end=100.0)

    z = np.array([900.0, 600.0, 300.0, 150.0])
    drift = np.abs(high.at(z) - low.at(z)) / low.at(z)
    assert np.all(drift < 2.0e-2), f"tail depends on the start redshift: {drift}"


def test_the_fudge_factor_is_worth_a_measurable_amount():
    r"""`fudge=1.0` is the honest three-level atom; $F=1.14$ is the calibration.

    The factor exists because the three-level model is not the true multi-level
    atom. Carrying it as a named parameter means its size can be *measured*:
    removing it slows recombination and leaves a larger residual. A fudge whose
    effect nobody has looked at is a free parameter in disguise.
    """
    fudged = peebles_ionisation(_background(), z_start=1800.0, z_end=100.0)
    honest = peebles_ionisation(_background(), z_start=1800.0, z_end=100.0, fudge=1.0)

    assert honest.freeze_out > fudged.freeze_out
    ratio = honest.freeze_out / fudged.freeze_out
    assert 1.02 < ratio < 1.30, f"fudge worth {ratio:.3f}x, which is not the known size"
    assert fudged.fudge == RECFAST_FUDGE


def test_x_e_decreases_monotonically_forward_in_time():
    """Nothing re-ionises here, so x_e must fall as z falls. A sign check.

    Reionisation is a later, separate physical process and is not in this
    module; if x_e ever rose, it would be the integrator, not the universe.
    """
    solution = peebles_ionisation(_background(), z_start=1800.0, z_end=100.0)
    ordered = solution.x_e[np.argsort(solution.z)]  # ascending z
    assert np.all(np.diff(ordered) >= -1e-12)


def _visibility_shape(mode: Recombination) -> tuple[float, float, float]:
    """(z of the peak, FWHM in z, the normalisation integral)."""
    background = _background()
    history = RecombinationHistory.build(
        background, z_max=2400.0, n_eta=6000, recombination=mode
    )
    z = 1.0 / np.clip(background.a_of_eta(history.eta), 1e-12, None) - 1.0
    peak = int(np.argmax(history.visibility))
    above = np.where(history.visibility >= history.visibility[peak] / 2.0)[0]
    return (float(z[peak]), float(abs(z[above[0]] - z[above[-1]])),
            history.visibility_norm())


def test_peebles_moves_last_scattering_and_widens_the_visibility():
    r"""**The result v1.1.0 exists for**, and the reason 5b was blocked on it.

    Saha puts last scattering around $z\simeq1300$ with a visibility far too
    narrow. Peebles brings the peak down to $z\simeq1100$ — the standard value
    is 1080--1100 — and widens the function by roughly half. **The width is what
    fixes the Silk damping envelope** (decision S18), so a 45% error in it is
    not a detail.

    Bounds rather than point values: the FWHM depends on the $\eta$ grid, and a
    test that pinned a hand-typed number would go stale the first time the grid
    changed. That is the mistake the README's "230 tests pass" made.
    """
    saha_peak, saha_width, saha_norm = _visibility_shape(Recombination.SAHA)
    peebles_peak, peebles_width, peebles_norm = _visibility_shape(Recombination.PEEBLES)

    # the visibility is a probability density, either way
    assert 0.97 < saha_norm < 1.01
    assert 0.97 < peebles_norm < 1.01

    # the peak moves to the standard epoch
    assert 1050.0 < peebles_peak < 1150.0
    assert saha_peak > 1250.0, "Saha should put last scattering much too early"

    # and the function widens substantially
    assert peebles_width > 1.3 * saha_width


@pytest.mark.parametrize("mode", list(Recombination))
def test_both_histories_build_and_stay_physical(mode: Recombination):
    """Whichever history is chosen, x_e stays in [0, 1] and kappa decreases to zero."""
    history = RecombinationHistory.build(
        _background(), z_max=2400.0, n_eta=2000, recombination=mode
    )
    assert np.all(history.x_e >= 0.0) and np.all(history.x_e <= 1.0 + 1e-12)
    assert history.kappa[-1] == pytest.approx(0.0, abs=1e-12)
    assert np.all(np.diff(history.kappa) <= 1e-12), "kappa must fall forward in time"
