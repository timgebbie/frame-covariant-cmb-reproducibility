"""Criterion 5b's external context: the comparison against CAMB and CLASS.

**Not the gate, and not bundled testing.** Decision **S4c** gates criterion 5b
on the bundle's own pipeline; `scripts/diagnostic_d8_criterion_5b_gate.py` does
that, in `run_all.py`. The architecture for this half is the PI's, 2026-10-15:
the comparison is *recorded as part of the bundle, with enough to independently
run, but not run by default*, and *the result is stored in the supplementary
materials and is recoverable and reproducible but not part of the bundled
testing*. So `reference/` carries the stamped spectra,
`scripts/make_reference_spectra.py` regenerates them from the codes,
`scripts/compare_criterion_5b.py` reproduces the measurement from the stamps
without either code installed, neither script is in the harness, and
`tables/criterion-5b-v1.2.0.tex` is the recorded result the supplement carries.

**These tests skip when the codes are not installed, and that is deliberate.**
CAMB and CLASS are installed at the comparison stage, not carried as
dependencies of the whole bundle --- a reader reproducing F1 should not need a
Fortran toolchain. `pip install camb classy` turns this file on.

What is *not* deliberate, and would be a defect, is a skip that passes silently
in the release. `test_criterion_5b_is_not_quietly_skipped` fails whenever the
codes are absent **and** the release notes claim 5b is met, so the two cannot
drift apart.

The canonical parameter set, the three $\\ell$ bands, and the reasons
reionisation, lensing and massive neutrinos are switched off are in
`provenance/EXTERNAL-CODE-COMPARISON-v1.md`. They are duplicated here as code so
that the comparison is reproducible from the test alone.
"""

from __future__ import annotations

import numpy as np
import pytest

#: The canonical set. Fixed so a later disagreement cannot be explained away by
#: a settings change. See provenance/EXTERNAL-CODE-COMPARISON-v1.md.
CANONICAL = {
    "ombh2": 0.02237,
    "omch2": 0.1200,
    "H0": 67.36,
    "ns": 0.9649,
    "tau": 0.0,      # no reionisation: this bundle does not model it
    "As": 2.1e-9,
    # Helium ON and explicit. Finding T-37: CLASS cannot infer it from BBN at
    # N_eff = 0, and leaving the two codes to disagree about helium would put a
    # recombination difference into a number meant to measure a reconstruction.
    "YHe": 0.245,
}

#: (name, lo, hi_exclusive, is_a_gate)
BANDS = [
    ("plateau and late ISW", 2, 30, False),
    ("acoustic peaks", 30, 1000, True),
    ("damping tail", 1000, 2001, False),
]



def _try_import(name: str):
    try:
        return __import__(name)
    except Exception:  # noqa: BLE001 - any import failure means "not available"
        return None


def _band_difference(ell: np.ndarray, a: np.ndarray, b: np.ndarray, lo: int, hi: int) -> float:
    """Max fractional difference over a band, each spectrum normalised at l = 30.

    Shape, not amplitude: neither this bundle nor the comparison fixes $A_s$ the
    same way, and comparing amplitudes would measure the normalisation rather
    than the physics.
    """
    inside = (ell >= lo) & (ell < hi)
    if inside.sum() == 0:
        return float("nan")
    ref = np.interp(30.0, ell, a), np.interp(30.0, ell, b)
    return float(np.max(np.abs(a[inside] / ref[0] - b[inside] / ref[1]) / (a[inside] / ref[0])))


# ---------------------------------------------------------------------------
# the gate that cannot be skipped
# ---------------------------------------------------------------------------


def test_criterion_5b_is_not_quietly_skipped():
    """The release notes and the installed codes must agree about 5b's status.

    Everything else in this file skips when CAMB and CLASS are absent. This does
    not. If the release notes ever say 5b is **closed** while the codes are not
    installed, the claim has no evidence behind it and this fails.
    """
    from pathlib import Path

    notes = (Path(__file__).resolve().parents[1] / "RELEASE-NOTES-v1.0.0.md").read_text(
        encoding="utf-8"
    )
    row = next((l for l in notes.splitlines() if l.strip().startswith("| 5b |")), "")
    assert row, "criterion 5b has no row in the release notes"

    claims_closed = "**closed**" in row
    have_codes = _try_import("camb") is not None and _try_import("classy") is not None
    assert not (claims_closed and not have_codes), (
        "RELEASE-NOTES claims criterion 5b is closed, but CAMB and CLASS are not "
        "installed in this environment, so nothing has been compared against them."
    )


def test_the_canonical_set_switches_off_what_this_bundle_does_not_model():
    """Reionisation off, and the reason recorded rather than assumed.

    Leaving it on would compare a spectrum containing reionisation against one
    that does not, and then attribute the difference to the reconstruction.
    """
    assert CANONICAL["tau"] == 0.0


# ---------------------------------------------------------------------------
# the comparison itself
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def external_spectra():
    """TT spectra from CAMB and CLASS on a common l grid, lensing and nu_m off."""
    camb_mod, classy_mod = _try_import("camb"), _try_import("classy")
    if camb_mod is None or classy_mod is None:
        pytest.skip("CAMB and/or CLASS not installed; criterion 5b not runnable here")

    pars = camb_mod.CAMBparams()
    pars.set_cosmology(
        H0=CANONICAL["H0"], ombh2=CANONICAL["ombh2"], omch2=CANONICAL["omch2"],
        tau=CANONICAL["tau"], mnu=0.0, num_massive_neutrinos=0,
        # N_eff = 0. This hierarchy has ONE radiation species; three massless
        # neutrinos would change the expansion without adding anything to the
        # driving. Finding T-37, and scripts/make_reference_spectra.py.
        nnu=0.0, YHe=CANONICAL["YHe"],
    )
    pars.InitPower.set_params(As=CANONICAL["As"], ns=CANONICAL["ns"])
    pars.set_for_lmax(2500, lens_potential_accuracy=0)
    pars.WantTensors = False
    camb_cl = camb_mod.get_results(pars).get_cmb_power_spectra(
        pars, CMB_unit="muK", raw_cl=True
    )["unlensed_scalar"][:, 0]

    cosmo = classy_mod.Class()
    cosmo.set({
        "output": "tCl", "lensing": "no", "l_max_scalars": 2500,
        "omega_b": CANONICAL["ombh2"], "omega_cdm": CANONICAL["omch2"],
        "h": CANONICAL["H0"] / 100.0, "A_s": CANONICAL["As"], "n_s": CANONICAL["ns"],
        "N_ncdm": 0,
        # **Not `tau_reio: 0`.** CLASS fits z_reio to a target tau and cannot
        # reach zero: it fails inside thermodynamics_solve. reio_none is the
        # switch that actually turns reionisation off.
        "reio_parametrization": "reio_none",
        # N_ur = 0 to match CAMB's nnu = 0, and YHe explicit because CLASS's
        # BBN interpolation does not cover N_eff = 0 and fails in
        # thermodynamics_helium_from_bbn without it.
        "N_ur": 0.0, "YHe": CANONICAL["YHe"],
    })
    cosmo.compute()
    raw = cosmo.raw_cl(2500)
    class_cl = raw["tt"] * (cosmo.T_cmb() * 1e6) ** 2
    cosmo.struct_cleanup()

    ell = np.arange(2, 2001)
    return {
        "ell": ell,
        "camb": camb_cl[2:2001],
        "class": class_cl[2:2001],
        "versions": {
            "camb": getattr(camb_mod, "__version__", "unknown"),
            "classy": getattr(classy_mod, "__version__", "unknown"),
        },
    }


def test_camb_and_class_agree_with_each_other_and_that_sets_the_floor(external_spectra):
    """**The tolerance is a measurement, not a judgement.**

    No agreement can be claimed tighter than two trusted independent codes agree
    with each other. This records their mutual difference per band; the numbers
    it prints are the acceptance thresholds for this bundle, and they are written
    into the release notes rather than chosen.
    """
    s = external_spectra
    print(f"\n  versions: {s['versions']}")
    floors = {}
    for name, lo, hi, _gate in BANDS:
        floors[name] = _band_difference(s["ell"], s["camb"], s["class"], lo, hi)
        print(f"  {name:22s} {lo:5d} <= l < {hi:5d}   CAMB vs CLASS: {floors[name]:.3%}")

    # They must agree well in the band that tests a reconstruction. Measured
    # 2026-10-14 on CAMB 2.0.5 and CLASS v3.4.1, specialised as above:
    # 0.125% / 0.370% / 0.223%. The gated band's floor is criterion 5b's
    # acceptance threshold, and it is recorded in
    # reference/REFERENCE-STAMP-v1.2.0.md because it was measured, not chosen.
    assert floors["acoustic peaks"] < 0.05, floors
    assert floors["acoustic peaks"] > 0.0, (
        "a floor of exactly zero means the two codes were not independently "
        "computed; check that both actually ran")


# ---------------------------------------------------------------------------
# the recorded result: in the bundle, reproducible, out of the bundled testing
# ---------------------------------------------------------------------------
#
# `test_this_bundle_matches_the_external_codes_in_the_acoustic_band` stood here
# as a skipped `NotImplementedError` stub, reason *"pending: needs Peebles
# recombination, not equilibrium Saha"*. It is **WITHDRAWN 2026-10-15**, and the
# reason is worth keeping rather than deleting: it was stale twice over. Peebles
# became the default at **S22** on 2026-10-10, so the stated blocker had been
# gone for five days --- the T-16 and T-40 class, a marker asserting something
# the tree no longer believed. And its *premise* is withdrawn by **S4c**: this
# bundle is not required to match CAMB and CLASS, and a test named for a match
# it will never make is a gate that can only fail.
#
# What replaces it is what the PI specified, 2026-10-15: *"the CAMB and CLASS
# testing cannot be in the bundle but recorded as part of the bundle with enough
# to independently run but not run by default. The result is stored in the
# supplementary materials and is recoverable and reproducible but not part of
# the bundled testing."*


def test_the_external_comparison_is_recorded_and_reproducible_without_the_codes():
    r"""The architecture, asserted rather than described.

    Three things have to be true at once, and each would be easy to lose:

    **Recorded.** The measured result is a committed artefact the supplement
    carries, not a number in a chat log or a figure nobody can regenerate.

    **Reproducible without the codes.** `compare_criterion_5b.py` reads the
    stamped CSVs in `reference/`, so a reader reproduces the comparison with
    neither `camb` nor `classy` installed. Regenerating the *stamp* needs them,
    and `make_reference_spectra.py` is in the bundle for exactly that.

    **Out of the bundled testing.** Neither script is in `run_all.py`, and
    nothing in `tests/` runs either code. This test reads files; it does not
    import `camb`.
    """
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]

    for name in ("camb", "class"):
        stamp = root / "reference" / f"{name}-tt-v1.2.0.csv"
        assert stamp.exists(), f"the stamped {name.upper()} spectrum is missing"
        assert len(stamp.read_text(encoding="utf-8").splitlines()) > 1000, (
            f"the stamped {name.upper()} spectrum is too short to be a spectrum")

    for script in ("compare_criterion_5b.py", "make_reference_spectra.py"):
        assert (root / "scripts" / script).exists(), (
            f"{script} is how the comparison is reproduced; without it the "
            "recorded result is an assertion")

    recorded = root / "tables" / "criterion-5b-v1.2.0.tex"
    assert recorded.exists(), (
        "the measured comparison must be recorded in the bundle and carried in "
        "the supplement. Run `python scripts/compare_criterion_5b.py`")
    text = recorded.read_text(encoding="utf-8")
    assert "GENERATED by scripts/compare_criterion_5b.py" in text, (
        "the recorded result must be generated, never typed")
    assert r"\%" in text, "the recorded result carries no measured numbers"

    harness = (root / "scripts" / "run_all.py").read_text(encoding="utf-8")
    for script in ("compare_criterion_5b.py", "make_reference_spectra.py"):
        assert f'"scripts/{script}"' not in harness, (
            f"{script} must NOT be in run_all.py: the external comparison is "
            "recorded in the bundle and run on demand, not part of the bundled "
            "testing (the PI, 2026-10-15)")
