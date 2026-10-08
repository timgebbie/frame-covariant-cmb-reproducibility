"""Finding T-3: the line-of-sight $\\eta$ grid must resolve $j_\\ell$'s oscillation.

$j_\\ell(k(\\eta_0-\\eta))$ oscillates with period $\\pi/k$ in $\\eta$. The grid was
fixed at `n_eta=1000` while that period shrinks as $1/k$, so above some $k$ the
integrand was **aliased** --- and an aliased integrand does not announce itself.
It returns a smooth, plausible spectrum of entirely the wrong shape, which is
why this survived into a tagged release candidate as the key figure.

Measured at the shipped grid, $k_{\\max}=420$, against `n_eta=8000`:

| $\\ell$ | CDM error | $\\Lambda$CDM error |
|---|---|---|
| 2 | 19% | 18% |
| 20 | 35% | 186% |
| 100 | 80% | 525% |
| 200 | 85% | **575%** |
| 400 | 94% | 334% |

and the $\\Lambda$CDM peak-to-plateau ratio read **37** where it converges to
**7.0**. The PI flagged that 37 as implausible; it was, and so was CDM's 5.8,
which looked right and was equally aliased.

The same argument was already written down in this bundle --- F3's own k-grid
comment says *a logarithmic grid aliases the integrand at high k however many
points it has*. It had simply never been applied to the other axis.
"""

from __future__ import annotations

import numpy as np
import pytest

from functions.background.flrw import CDM_MODEL, LCDM_MODEL
from functions.spectra.decoupling import Weighting
from functions.spectra.pipeline import (
    ETA_POINTS_PER_PERIOD,
    required_n_eta,
    run,
)

#: What F3 ships with.
K_MAX = 420.0


def test_the_requirement_is_arithmetic_not_a_knob():
    """n_eta scales linearly in k_max and in the span, and inversely in nothing else."""
    assert required_n_eta(100.0, 2.0) == pytest.approx(
        np.ceil(ETA_POINTS_PER_PERIOD * 100.0 * 2.0 / np.pi), abs=1
    )
    assert required_n_eta(200.0, 2.0) >= 2 * required_n_eta(100.0, 2.0) - 1
    assert required_n_eta(100.0, 4.0) >= 2 * required_n_eta(100.0, 2.0) - 1


@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_a_degenerate_grid_is_refused(bad):
    with pytest.raises(ValueError):
        required_n_eta(bad, 2.0)
    with pytest.raises(ValueError):
        required_n_eta(100.0, bad)


@pytest.mark.parametrize("model,name", [(CDM_MODEL, "CDM"), (LCDM_MODEL, "LCDM")])
def test_the_shipped_grid_is_below_nyquist_or_close_to_it(model, name):
    """The historical record, asserted so the scale of T-3 cannot be forgotten.

    Nyquist is 2 samples per period. ΛCDM's shipped grid gave 2.3 at the band
    edge: the integral was not merely coarse, it was at the sampling limit.
    """
    shipped = 1000
    span = float(model.eta_0)
    per_period = np.pi / K_MAX / (span / shipped)
    assert per_period < 4.0, (name, per_period)
    assert required_n_eta(K_MAX, span) > 3000


@pytest.mark.parametrize("model", [CDM_MODEL, LCDM_MODEL])
def test_an_undersampled_grid_raises_instead_of_aliasing(model):
    """The whole point. Silence was the defect, not coarseness."""
    k = np.arange(0.05, K_MAX, np.pi / 6.0)
    with pytest.raises(ValueError, match="aliases the line-of-sight integrand"):
        run(model, ells=np.array([2, 10]), k_com=k,
            weighting=Weighting.STANDARD_ISW, n_eta=1000)


def test_the_error_names_the_number_that_would_work():
    """An error that does not say what to do instead gets worked around."""
    k = np.arange(0.05, K_MAX, np.pi / 6.0)
    with pytest.raises(ValueError) as excinfo:
        run(CDM_MODEL, ells=np.array([2]), k_com=k,
            weighting=Weighting.STANDARD_ISW, n_eta=1000)
    message = str(excinfo.value)
    assert "n_eta >=" in message and "T-3" in message
    assert "samples per oscillation" in message


def test_a_derived_grid_runs_and_reports_both_diagnostics():
    """`n_eta=None` must work, and the run must say what it left out.

    `damping_at_k_max` is the weight still on the integrand where the k grid
    stops. At F3's k_max it is nowhere near zero, which is the *second* half of
    T-3 and is reported rather than silently accepted.
    """
    k = np.arange(0.05, 60.0, np.pi / 6.0)   # small, so the test is quick
    out = run(CDM_MODEL, ells=np.array([2, 10]), k_com=k,
              weighting=Weighting.STANDARD_ISW, n_eta=None)
    assert out.n_eta == required_n_eta(float(k.max()), float(CDM_MODEL.eta_0 - out.recombination.eta[0]))
    assert out.eta_points_per_period >= ETA_POINTS_PER_PERIOD - 0.5
    assert 0.0 <= out.damping_at_k_max <= 1.0


def test_f3_no_longer_hand_sets_the_grid():
    """The script that caused T-3 must not be able to cause it again."""
    from pathlib import Path

    import re

    src = (Path(__file__).resolve().parents[1]
           / "scripts" / "figure_f3_angular_spectrum.py").read_text(encoding="utf-8")
    assert "n_eta=None" in src

    # Code only. The comment above the call *quotes* the old value on purpose,
    # so a plain substring search would match the explanation of the fix.
    code = [l for l in src.splitlines() if not l.lstrip().startswith("#")]
    hardcoded = [l.strip() for l in code if re.search(r"n_eta\s*=\s*\d", l)]
    assert not hardcoded, hardcoded
