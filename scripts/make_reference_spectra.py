#!/usr/bin/env python3
r"""Generate the stamped CAMB and CLASS reference spectra for criterion 5b.

    python scripts/make_reference_spectra.py

**Ring-fenced, and the fence is the point.** CAMB and CLASS are *not*
dependencies of this bundle and must never become them: a reader reproducing F1
should not need a Fortran toolchain, and a reconstruction that imports the codes
it is being checked against is not an independent reconstruction. So

* nothing under `functions/` imports `camb` or `classy`, and nothing ever may;
* this script is the only place either is called, it is not in `run_all.py`'s
  figure stages, and it exits cleanly with a message when they are absent;
* what enters the bundle is **data with a stamp**, under `reference/` --- the two
  spectra, the versions that produced them, the exact settings, and the derived
  parameters --- never vendored source;
* `tests/test_external_codes.py` reads the *installed codes* when they are
  present and this *stamped data* when they are not, so the comparison is
  reproducible either way and
  `test_criterion_5b_is_not_quietly_skipped` keeps the claim and the evidence
  from drifting apart.

**The specialisation, and why each piece of it.** Criterion 5b compares shapes,
so the two sides must be the same cosmology, not merely similar ones. The
external codes are therefore specialised *down* to what this bundle contains
rather than this bundle being flattered upward:

| switched off | why |
|---|---|
| massive neutrinos | not modelled here |
| **massless neutrinos**, $N_{eff}=0$ | this hierarchy has **one** radiation species. Three massless neutrinos would change the expansion without adding anything to the driving --- the same error as comparing a quantity across two frames |
| reionisation | not modelled here. CLASS cannot reach $\tau=0$ by fitting $z_{reio}$, so it takes `reio_parametrization = reio_none` rather than `tau_reio = 0` |
| lensing | not modelled here |
| tensors | not modelled here |

Helium is **on** at $Y_{He}=0.245$ in both, and given explicitly rather than left
to BBN: CLASS's BBN interpolation does not cover $N_{eff}=0$ and fails in
`thermodynamics_helium_from_bbn` without it.

Specialised this way both codes report $z_{eq}=5756.0$ --- which
`functions.background.flrw.PLANCK_MODEL` reaches independently, deriving
$\Omega_\gamma h^2$ from $T_{CMB}$ and the physical constants --- and a first
acoustic peak at $\ell=206$. **The acoustic peaks are there**, which is what
makes the band comparison meaningful at all.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    PLANCK_A_S,
    PLANCK_H,
    PLANCK_MODEL,
    PLANCK_N_S,
    PLANCK_OMEGA_B_H2,
    PLANCK_OMEGA_C_H2,
    PLANCK_Y_HE,
    OMEGA_GAMMA_H2,
)

VERSION = "v1.2.0"
L_MAX = 2500

#: The bands criterion 5b reports in, duplicated from `tests/test_external_codes`
#: so this script can be read alone. Only the acoustic band gates.
BANDS = [
    ("plateau and late ISW", 2, 30, False),
    ("acoustic peaks", 30, 1000, True),
    ("damping tail", 1000, 2001, False),
]


def band_difference(ell: np.ndarray, a: np.ndarray, b: np.ndarray,
                    lo: int, hi: int) -> float:
    """Worst fractional difference over a band, each spectrum renormalised at l=30.

    **Shape, not amplitude.** Neither this bundle nor the external codes fix
    $A_s$ the same way, so comparing amplitudes would measure a normalisation.
    """
    inside = (ell >= lo) & (ell < hi)
    ra, rb = np.interp(30.0, ell, a), np.interp(30.0, ell, b)
    return float(np.max(np.abs(a[inside] / ra - b[inside] / rb) / (a[inside] / ra)))


def camb_spectrum() -> tuple[np.ndarray, dict, str]:
    import camb

    pars = camb.CAMBparams()
    pars.set_cosmology(
        H0=100.0 * PLANCK_H, ombh2=PLANCK_OMEGA_B_H2, omch2=PLANCK_OMEGA_C_H2,
        tau=0.0, mnu=0.0, num_massive_neutrinos=0, nnu=0.0, YHe=PLANCK_Y_HE,
    )
    pars.InitPower.set_params(As=PLANCK_A_S, ns=PLANCK_N_S)
    pars.set_for_lmax(L_MAX, lens_potential_accuracy=0)
    pars.WantTensors = False
    results = camb.get_results(pars)
    cl = results.get_cmb_power_spectra(
        pars, CMB_unit="muK", raw_cl=True)["unlensed_scalar"][:, 0]
    d = results.get_derived_params()
    return cl, {k: float(d[k]) for k in ("zstar", "rstar", "thetastar", "zeq")
                if k in d}, camb.__version__


def class_spectrum() -> tuple[np.ndarray, dict, str]:
    import classy

    cosmo = classy.Class()
    cosmo.set({
        "output": "tCl", "lensing": "no", "l_max_scalars": L_MAX,
        "omega_b": PLANCK_OMEGA_B_H2, "omega_cdm": PLANCK_OMEGA_C_H2,
        "h": PLANCK_H, "A_s": PLANCK_A_S, "n_s": PLANCK_N_S,
        "N_ncdm": 0, "N_ur": 0.0, "YHe": PLANCK_Y_HE,
        # NOT tau_reio = 0: CLASS fits z_reio to a target tau and cannot reach
        # zero, failing inside thermodynamics_solve. reio_none is the switch.
        "reio_parametrization": "reio_none",
    })
    cosmo.compute()
    cl = cosmo.raw_cl(L_MAX)["tt"] * (cosmo.T_cmb() * 1e6) ** 2
    derived = cosmo.get_current_derived_parameters(["z_rec", "rs_rec", "100*theta_s"])
    derived["z_eq"] = float(cosmo.z_eq())
    version = classy.__version__
    cosmo.struct_cleanup()
    cosmo.empty()
    return cl, {k: float(v) for k, v in derived.items()}, version


def main() -> int:
    try:
        camb_cl, camb_derived, camb_version = camb_spectrum()
        class_cl, class_derived, class_version = class_spectrum()
    except ImportError as exc:
        print(f"CAMB and/or CLASS are not installed ({exc}).")
        print("They are deliberately not dependencies of this bundle; the stamped")
        print("spectra under reference/ are what the comparison uses without them.")
        print("  pip install camb classy")
        return 0

    ell = np.arange(2, 2001)
    camb_tt, class_tt = camb_cl[2:2001], class_cl[2:2001]

    out = ROOT / "reference"
    out.mkdir(exist_ok=True)
    for name, values in (("camb", camb_tt), ("class", class_tt)):
        path = out / f"{name}-tt-{VERSION}.csv"
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"# TT, unlensed scalar, muK^2, raw C_l. {name.upper()} "
                     f"specialised to N_eff=0, no reionisation, no lensing.\n")
            fh.write("ell,cl_tt_muK2\n")
            for l, v in zip(ell, values):
                fh.write(f"{int(l)},{v:.12e}\n")
        print(f"wrote {path.relative_to(ROOT)}")

    floors = {name: band_difference(ell, camb_tt, class_tt, lo, hi)
              for name, lo, hi, _ in BANDS}

    stamp = out / f"REFERENCE-STAMP-{VERSION}.md"
    lines = [
        f"# Reference spectra for criterion 5b — {VERSION}",
        "",
        f"Generated by `scripts/make_reference_spectra.py` on {date.today()}.",
        "**Data, stamped. Not vendored code** — neither CAMB nor CLASS is a",
        "dependency of this bundle and nothing under `functions/` imports either.",
        "",
        "## Versions",
        "",
        "| code | version |",
        "|---|---|",
        f"| CAMB | `{camb_version}` |",
        f"| CLASS (classy) | `{class_version}` |",
        "",
        "## The specialisation",
        "",
        "Both codes are specialised **down** to what this bundle contains, so the",
        "comparison is like for like. Massive neutrinos, massless neutrinos,",
        "reionisation, lensing and tensors are all off; helium is on at",
        f"`YHe = {PLANCK_Y_HE}`, given explicitly because CLASS's BBN interpolation",
        "does not cover $N_{eff}=0$.",
        "",
        "| parameter | value |",
        "|---|---|",
        f"| `ombh2` | {PLANCK_OMEGA_B_H2} |",
        f"| `omch2` | {PLANCK_OMEGA_C_H2} |",
        f"| `H0` | {100 * PLANCK_H} |",
        f"| `ns` | {PLANCK_N_S} |",
        f"| `As` | {PLANCK_A_S} |",
        f"| `YHe` | {PLANCK_Y_HE} |",
        "| `N_eff` | 0 — CAMB `nnu=0`, CLASS `N_ur=0` |",
        "| reionisation | CAMB `tau=0`; CLASS `reio_parametrization=reio_none` |",
        "",
        "## Derived parameters, and the independent check",
        "",
        "| quantity | CAMB | CLASS | this bundle |",
        "|---|---|---|---|",
        f"| $z_*$ | {camb_derived.get('zstar', float('nan')):.2f} | "
        f"{class_derived.get('z_rec', float('nan')):.2f} | — |",
        f"| $r_s(z_*)$ [Mpc] | {camb_derived.get('rstar', float('nan')):.3f} | "
        f"{class_derived.get('rs_rec', float('nan')):.3f} | — |",
        f"| $z_{{eq}}$ | {camb_derived.get('zeq', float('nan')):.1f} | "
        f"{class_derived.get('z_eq', float('nan')):.1f} | "
        f"**{PLANCK_MODEL.omega_m / PLANCK_MODEL.omega_r - 1:.1f}** |",
        "",
        f"`PLANCK_MODEL` reaches $z_{{eq}}$ independently: $\\Omega_\\gamma h^2 = "
        f"{OMEGA_GAMMA_H2:.6e}$ derived from $T_{{CMB}}=2.7255$ K and the physical",
        "constants, not quoted from either code. It lands on theirs.",
        "",
        "## The tolerance — a measurement, not a judgement (S4b)",
        "",
        "No agreement can be claimed tighter than two trusted independent codes",
        "agree with each other. Shape, each spectrum renormalised at $\\ell=30$:",
        "",
        "| band | $\\ell$ | CAMB vs CLASS | gate |",
        "|---|---|---|---|",
    ]
    for name, lo, hi, gate in BANDS:
        lines.append(f"| {name} | ${lo} \\le \\ell < {hi}$ | "
                     f"**{floors[name]:.3%}** | {'yes' if gate else 'no'} |")
    lines += [
        "",
        "The gated band's floor is the acceptance threshold for criterion 5b.",
        "It is written here because it was measured, not chosen.",
        "",
    ]
    stamp.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {stamp.relative_to(ROOT)}")
    for name, lo, hi, gate in BANDS:
        print(f"  {name:22s} {lo:5d} <= l < {hi:5d}   CAMB vs CLASS "
              f"{floors[name]:8.3%}{'   GATE' if gate else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
