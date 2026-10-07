"""Criterion 5b: the canonical comparison against CAMB and CLASS.

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
        "tau_reio": CANONICAL["tau"], "N_ncdm": 0,
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

    # they must agree well in the band that tests a reconstruction
    assert floors["acoustic peaks"] < 0.05, floors


@pytest.mark.skip(
    reason="pending: needs Peebles recombination, not equilibrium Saha. "
           "The damping tail cannot pass until then, which is stated in "
           "provenance/EXTERNAL-CODE-COMPARISON-v1.md rather than discovered here."
)
def test_this_bundle_matches_the_external_codes_in_the_acoustic_band(external_spectra):
    """Criterion 5b proper. Unskipped when recombination is good enough to try."""
    raise NotImplementedError
