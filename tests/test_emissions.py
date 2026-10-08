r"""The quantities emitted for Paper 1's floats.

The governing rule, from P1-T's work order: nothing here may recompute a
background. If a lensing kernel is built from a separately derived $\chi_*$ the
figure compares two cosmologies and the agreement means nothing. These tests
pin that.
"""

from __future__ import annotations

import numpy as np
import pytest

from functions.background.flrw import CDM_MODEL, LCDM_MODEL
from functions.spectra.decoupling import RecombinationHistory
from functions.spectra.emissions import (
    comoving_distance,
    lensing_efficiency,
    line_of_sight_field,
)


@pytest.fixture(scope="module")
def emission():
    rec = RecombinationHistory.build(LCDM_MODEL)
    return comoving_distance(LCDM_MODEL, rec), rec


def test_chi_comes_from_the_integrated_background_not_a_formula(emission):
    """chi(eta) = eta_0 - eta, with eta_0 the one the solver actually integrated."""
    em, _ = emission
    assert np.allclose(em.chi, LCDM_MODEL.eta_0 - em.eta)
    assert em.chi[-1] == pytest.approx(LCDM_MODEL.eta_0 - em.eta[-1])


def test_chi_star_is_the_visibility_peak_not_kappa_equals_one(emission):
    """The spectrum's primary term is evaluated at the visibility peak.

    A lensing kernel built on any other definition of last scattering is built
    on a different surface from the spectrum it is meant to accompany.
    """
    em, rec = emission
    assert em.eta_star == pytest.approx(rec.eta_star)
    assert em.chi_star == pytest.approx(LCDM_MODEL.eta_0 - rec.eta_star)


def test_the_lensing_kernel_is_exact_at_both_endpoints(emission):
    """P1-T's acceptance includes the endpoints, so rounding there is not allowed."""
    em, _ = emission
    kernel = lensing_efficiency(em)
    at_observer = kernel[np.argmin(np.abs(em.chi - 0.0))]
    assert kernel[np.argmin(np.abs(em.chi - em.chi_star))] == pytest.approx(0.0, abs=1e-6)
    assert at_observer == pytest.approx(1.0, abs=1e-6)
    assert np.all(kernel >= -1e-12)


def test_the_kernel_uses_the_emitted_chi_star(emission):
    """Changing chi_* must change the kernel --- it is not independently derived."""
    em, _ = emission
    import dataclasses

    shifted = dataclasses.replace(em, chi_star=em.chi_star * 0.9)
    assert not np.allclose(lensing_efficiency(em), lensing_efficiency(shifted))


def test_the_running_integral_returns_to_the_endpoint():
    """Fig. 3's acceptance, on a source this bundle can make without v1.5.0."""
    eta_0 = CDM_MODEL.eta_0
    eta = np.linspace(0.05, eta_0, 4000)
    source = np.exp(-0.5 * ((eta - 0.08) / 0.01) ** 2)
    ray = line_of_sight_field(10, 50.0, eta=eta, source=source, eta_0=eta_0)

    assert ray.running[0] == 0.0
    assert ray.running[-1] == pytest.approx(ray.endpoint)
    assert np.isfinite(ray.running_excursion)


def test_the_running_excursion_is_reported_and_not_silently_tolerated():
    """A running integral that wanders through the bulk must produce a large number.

    The point is that `running_excursion` reports rather than judges. It was
    called `bulk_fraction` until finding T-5, after a claim in Paper 1's caption
    that turned out to be inverted; the measurement was always this flatness
    statistic and is unchanged. Only the name, which had begun to carry an
    argument, is different.
    """
    eta_0 = CDM_MODEL.eta_0
    eta = np.linspace(0.05, eta_0, 2000)
    ray = line_of_sight_field(4, 3.0, eta=eta, source=np.ones_like(eta), eta_0=eta_0)
    assert ray.running_excursion > 0.1
