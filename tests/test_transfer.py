"""Appendix J: the power spectrum normalisations and the transfer function.

Finding B-10 is the point of this file. The printed (J.5) and the corrected one
agree in the large-scale limit, so only the small-scale limit can tell them
apart — and only one of them has the limit a transfer function must have.
"""

from __future__ import annotations

import numpy as np
import pytest

from functions.spectra.transfer import (
    ANNALS_II_GAMMA,
    power_spectrum_j1,
    power_spectrum_j3,
    shape_parameter,
    transfer_function,
    transfer_function_printed,
)


# ---------------------------------------------------------------------------
# finding B-10
# ---------------------------------------------------------------------------


def test_both_forms_agree_on_large_scales_which_is_why_the_text_does_not_catch_it():
    """The bracket tends to 1 and $1^{\\pm1/\\nu}=1$, so $T\\to1$ either way.

    Annals II's own statement --- "the transfer function $T(k)\\sim+1$ on large
    scales" --- is therefore true of the printed form as well, and cannot detect
    the sign. Asserting that explicitly is what makes the *next* test the
    decisive one rather than merely a second opinion.
    """
    k = np.array([1e-5, 1e-4, 1e-3])
    assert np.allclose(transfer_function(k), 1.0, atol=2e-2)
    assert np.allclose(transfer_function_printed(k), 1.0, atol=2e-2)


def test_b10_the_printed_transfer_function_diverges_where_it_must_vanish():
    """**Finding B-10.** A transfer function suppresses small scales.

    Modes entering the horizon in radiation domination stagnate, so $T\\to0$ as
    $k\\to\\infty$. As printed it instead *grows without bound*. One sign is the
    physics and the other is its inverse; this is not a matter of convention.
    """
    k = np.array([0.1, 1.0, 10.0])
    corrected, printed = transfer_function(k), transfer_function_printed(k)

    assert np.all(np.diff(corrected) < 0.0)   # falls
    assert np.all(np.diff(printed) > 0.0)     # rises
    assert corrected[-1] < 1e-3
    assert printed[-1] > 1e3
    assert np.allclose(corrected * printed, 1.0)  # they are reciprocals


def test_the_corrected_transfer_function_has_the_cdm_asymptote():
    """$T\\propto k^{-2}$ at large $k$ --- what the Bond & Efstathiou fit fits.

    Checked as a slope in logarithmic variables over a decade where the $(ck)^2$
    term dominates, rather than at a point, so it is the asymptote and not a
    coincidence of one value.
    """
    k = np.logspace(1.5, 2.5, 40)
    slope = np.polyfit(np.log(k), np.log(transfer_function(k)), 1)[0]
    assert slope == pytest.approx(-2.0, abs=0.05)


# ---------------------------------------------------------------------------
# the two normalisations, and their relation to finding B-5
# ---------------------------------------------------------------------------


def test_j1_and_j3_differ_by_one_power_of_k():
    """The fact that settled B-5: (201) descends from (J.1), (204) from (J.3)."""
    k = np.logspace(-3, 0, 50)
    ratio = power_spectrum_j3(k, n=1.0) / power_spectrum_j1(k, n=1.0)
    assert np.allclose(ratio / k, ratio[0] / k[0])


def test_j1_is_constant_at_n_equals_one_and_eta0_drops_out():
    """At $n=1$, $(k\\eta_0)^{n-1}=1$, so B-5's analysis is unaffected by it."""
    k = np.logspace(-3, 0, 20)
    assert np.allclose(power_spectrum_j1(k, amplitude=3.0, n=1.0, eta_0=2.0), 3.0)
    assert np.allclose(
        power_spectrum_j1(k, amplitude=3.0, n=1.0, eta_0=7.0),
        power_spectrum_j1(k, amplitude=3.0, n=1.0, eta_0=2.0),
    )


def test_j3_reduces_to_the_sachs_wolfe_case_when_the_transfer_function_is_unity():
    """§8.3.2 sets $T=1$; (204) is that case."""
    k = np.logspace(-3, 0, 20)
    assert np.allclose(power_spectrum_j3(k, n=1.0), k)


# ---------------------------------------------------------------------------
# the shape parameter
# ---------------------------------------------------------------------------


def test_the_stated_gamma_is_not_omega0_h_and_the_gap_is_recorded():
    """Annals II says $\\Gamma\\simeq\\Omega_0h$ and then states $\\Gamma=0.48$.

    For its own model ($\\Omega_0=1$, $h=0.5$) $\\Omega_0h=0.50$. The stated value
    therefore carries an unnamed baryon correction of about 4%. The paper's own
    number is what the code uses; this test pins the gap so that nobody later
    "fixes" `ANNALS_II_GAMMA` to 0.5 on the grounds that the text says
    $\\Omega_0 h$.
    """
    assert shape_parameter(1.0, 0.5) == pytest.approx(0.50)
    assert ANNALS_II_GAMMA == pytest.approx(0.48)
    assert ANNALS_II_GAMMA / shape_parameter(1.0, 0.5) == pytest.approx(0.96)


def test_a_smaller_shape_parameter_moves_the_bend_to_larger_scales():
    """Gamma sets where the turnover is; the direction is a physics check."""
    k = np.array([0.05])
    assert transfer_function(k, gamma=0.3)[0] < transfer_function(k, gamma=0.6)[0]
