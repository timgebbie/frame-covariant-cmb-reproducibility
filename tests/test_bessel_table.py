"""The tabulated half of route 3: j_l tables and the line-of-sight projection."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.special import spherical_jn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.spectra.bessel_table import BesselTable, line_of_sight  # noqa: E402

X_MAX = 400.0


@pytest.fixture(scope="module")
def table():
    return BesselTable.build(60, X_MAX, points_per_period=12)


@pytest.mark.parametrize("ell", (2, 10, 40, 60))
def test_interpolation_reproduces_the_function(table, ell):
    """12 points per oscillation period holds the table to about 1e-6 absolute."""
    x = np.linspace(1.0, X_MAX - 5.0, 5000)
    assert np.max(np.abs(table(ell, x) - spherical_jn(ell, x))) < 5e-6


def test_accuracy_improves_with_sampling(table):
    """The accuracy knob does what it claims, so it can be tuned on evidence."""
    x = np.linspace(1.0, X_MAX - 5.0, 2000)
    errs = []
    for ppp in (6, 12, 20):
        t = BesselTable.build(20, X_MAX, points_per_period=ppp)
        errs.append(np.max(np.abs(t(10, x) - spherical_jn(10, x))))
    assert errs[0] > errs[1] > errs[2]


def test_outside_the_table_is_zero_not_garbage(table):
    """A query beyond x_max returns zero rather than an extrapolated artefact."""
    assert table(10, np.array([X_MAX * 2])) == 0.0


def test_unavailable_ell_is_refused(table):
    with pytest.raises(ValueError):
        table(10_000, 1.0)


@pytest.mark.parametrize("ell,k", ((2, 0.05), (10, 0.2), (40, 0.6)))
def test_line_of_sight_matches_direct_evaluation(table, ell, k):
    """The integrated term of (176), against the same integral evaluated directly."""
    eta = np.linspace(0.0, 190.0, 4001)
    eta_0 = 200.0
    source = np.exp(-(((eta - 150.0) / 12.0) ** 2))  # a visibility-like source
    got = line_of_sight(ell, k, eta, source, eta_0, table)
    ref = np.trapezoid(source * spherical_jn(ell, k * (eta_0 - eta)), eta)
    assert abs(got / ref - 1) < 1e-5
