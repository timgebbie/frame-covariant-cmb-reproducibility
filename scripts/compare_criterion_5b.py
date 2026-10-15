#!/usr/bin/env python3
r"""Criterion 5b's **context**: this bundle against the stamped CAMB and CLASS.

    python scripts/compare_criterion_5b.py

**This is not the gate.** Decision **S4c** sets criterion 5b's tolerance against
the bundle's own pipeline --- (102) against (177)--(179) --- and
`scripts/diagnostic_d8_criterion_5b_gate.py` measures it, in `run_all.py`, at
$9.5\times10^{-6}$ worst against a gate of $10^{-3}$. What this script produces
is the comparison with two full Boltzmann codes, reported alongside, which is a
different and still necessary thing: it says *how far* a $1+3$ slow-decoupling
solution stands from CAMB and CLASS, in bands, with the dominant term named.

**Why the external codes are context and not the threshold.** S4b set the
tolerance as the two codes' mutual difference, 0.370% in the acoustic band. This
bundle will not meet that and was never going to: (102) carries a slow-decoupling
expansion, no polarisation hierarchy, no neutrino anisotropic stress and a
visibility-weighted line of sight. **A criterion that can only be failed is not
a criterion**, and one met by construction is not one either --- what makes S4c
sound is that the self-comparison *can* fail, and states what it does not cover.

**Like for like, and that took work.** `PLANCK_MODEL` carries a photon-only
radiation era reaching $z_{eq}=5756.0$ by an independent route (**T-37**); the
transfer function drives the acoustic oscillation per mode (**T-37**); the
polarised quadrupole $16/15$ makes the damping like for like, for this
comparison alone (**S31**); CLASS's frame is verified from `perturbations.c` and
CAMB's corroborated; and the reference spectra are stamped under `reference/`
with the two codes' mutual difference measured per band.

**Shape, never amplitude.** Each spectrum is renormalised at $\ell=30$ before
anything is compared, because neither side fixes $A_s$ the same way and an
amplitude comparison would measure a normalisation.

**The answer is expected to be large, and the point is to itemise it rather
than total it.** A number alone would say only *it differs*; what is useful is
which approximation each part of the difference belongs to.
"""

from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    PLANCK_H,
    PLANCK_MODEL,
    PLANCK_N_S,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.angular import cl_covariant_route, d_ell  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import (  # noqa: E402
    F2_POLARISED,
    F2_TIGHT_COUPLING,
)
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment,
    coefficient_sets,
    transfer_by_rank,
)

VERSION = "v1.2.0"

#: Linear enough to resolve the peaks. They sit near 206, 410, 610 and 810 in
#: the external codes, so a *logarithmic* grid --- which every other figure here
#: uses --- would sample the first peak twenty times and the third twice. The
#: acoustic band is the claim, so the grid is linear across it.
ELLS = np.unique(np.concatenate([
    np.array([2, 4, 7, 11, 16, 22]),
    np.arange(30, 1001, 28),
]))

#: $k_D=536.9$ with the polarised coefficient, so $e^{-2(k/k_D)^2}$ at 1500 is
#: $2\times10^{-7}$: the grid runs past the damping scale, as **T-32** requires.
K_COM = np.arange(0.05, 1500.0, np.pi / 3.0)

BANDS = [
    ("plateau and late ISW", 2, 30, False),
    ("acoustic peaks", 30, 1000, True),
]

#: Measured in `reference/REFERENCE-STAMP-v1.2.0.md`: how closely the two
#: external codes agree **with each other**. It was criterion 5b's threshold
#: under S4b and is not one under S4c; it is printed because it is the scale
#: against which the differences below should be read, and because no agreement
#: with either code could be claimed tighter than this whatever the gate said.
FLOOR = {"plateau and late ISW": 0.00125, "acoustic peaks": 0.00370}


def bundle_spectrum(f_2: float) -> tuple[np.ndarray, dict]:
    """$C_\\ell$ in the **CDM frame** --- the frame the observer is in, and the
    one CLASS's synchronous gauge and CAMB both evolve in. Comparing across
    frames would not be comparing the same quantity."""
    gamma = shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H)
    env = build_environment(
        float(K_COM.max()), omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2, transfer_gamma=gamma, hubble_h=PLANCK_H,
        f_2=f_2)
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(K_COM.max() * (env.background.eta_0 - env.eta[0])) + 20.0)

    transfer = np.zeros((ELLS.size, K_COM.size))
    for j, k in enumerate(K_COM):
        _, cdm = coefficient_sets(float(k), env)
        transfer[:, j] = transfer_by_rank(ELLS, float(k), cdm, env, table)[-1]

    power = primordial_power(K_COM, n_s=PLANCK_N_S, amplitude=1.0)
    cl = np.array([cl_covariant_route(int(l), K_COM, transfer[i], power)
                   for i, l in enumerate(ELLS)])
    z_star = float(1.0 / env.background.a_of_eta(env.eta_star) - 1.0)
    return cl, {"z_star": z_star, "k_D": float(env.damping_k),
                "gamma": float(gamma), "n_eta": int(env.eta.size)}


def reference(name: str) -> tuple[np.ndarray, np.ndarray]:
    ell, cl = [], []
    with (ROOT / "reference" / f"{name}-tt-{VERSION}.csv").open(encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if not row or row[0].startswith("#") or row[0] == "ell":
                continue
            ell.append(int(row[0]))
            cl.append(float(row[1]))
    return np.array(ell), np.array(cl)


def shape(ell: np.ndarray, cl: np.ndarray) -> np.ndarray:
    """$D_\\ell$ renormalised at $\\ell=30$."""
    d = d_ell(ell, cl)
    return d / np.interp(30.0, ell, d)


def band_difference(ell: np.ndarray, a: np.ndarray, b: np.ndarray,
                    lo: int, hi: int) -> tuple[float, int]:
    """Worst fractional difference in a band, and the $\\ell$ it occurs at."""
    inside = (ell >= lo) & (ell < hi)
    diff = np.abs(a[inside] - b[inside]) / np.abs(b[inside])
    j = int(np.argmax(diff))
    return float(diff[j]), int(ell[inside][j])


def peak_position(ell: np.ndarray, s: np.ndarray) -> int:
    band = (ell >= 100) & (ell <= 320)
    return int(ell[band][int(np.argmax(s[band]))])


def main() -> int:
    print("criterion 5b: this bundle against the stamped CAMB and CLASS spectra")
    print(f"  ells {ELLS.min()}..{ELLS.max()} ({ELLS.size} points), "
          f"k to {K_COM.max():.0f} ({K_COM.size} modes)")

    cl_pol, meta = bundle_spectrum(F2_POLARISED)
    print(f"  PLANCK_MODEL: z_* = {meta['z_star']:.1f}, k_D = {meta['k_D']:.1f}, "
          f"Gamma = {meta['gamma']:.5f}, n_eta = {meta['n_eta']}")
    cl_printed, _ = bundle_spectrum(F2_TIGHT_COUPLING)

    ours = shape(ELLS, cl_pol)
    ours_printed = shape(ELLS, cl_printed)
    results, peaks = {}, {"this bundle": peak_position(ELLS, ours)}
    for name in ("camb", "class"):
        ell_ref, cl_ref = reference(name)
        ref = np.interp(ELLS, ell_ref, shape(ell_ref, cl_ref))
        peaks[name.upper()] = peak_position(ELLS, ref)
        results[name] = {b: band_difference(ELLS, ours, ref, lo, hi)
                         for b, lo, hi, _ in BANDS}

    print("\n  first acoustic peak: " + ", ".join(
        f"{k} at l={v}" for k, v in peaks.items()))
    print("\n  shape, renormalised at l=30:")
    for b, lo, hi, gate in BANDS:
        line = f"  {b:22s} {lo:5d} <= l < {hi:5d}  "
        for name in ("camb", "class"):
            d, at = results[name][b]
            line += f"  vs {name.upper()}: {d:7.1%} (worst at l={at})"
        print(line + (f"   code-code {FLOOR[b]:.3%}" if gate else ""))

    # The damping coefficient's own contribution, isolated: S31's 16/15 against
    # what Annals II prints, through the whole pipeline rather than in k_D alone.
    damping_item = {b: band_difference(ELLS, ours, ours_printed, lo, hi)[0]
                    for b, lo, hi, _ in BANDS}
    print("\n  itemised, the part this bundle can attribute:")
    for b, lo, hi, _ in BANDS:
        print(f"    (dif-damp-correct) f_2=3/4 against (dif-damp) f_2=1: "
              f"{damping_item[b]:7.1%}  [{b}]")

    out = ROOT / "outputs" / "criterion-5b.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# shape, D_l renormalised at l=30\n")
        fh.write("ell,bundle_polarised,bundle_printed,camb,class\n")
        ec, cc = reference("camb")
        ecl, ccl = reference("class")
        rc = np.interp(ELLS, ec, shape(ec, cc))
        rl = np.interp(ELLS, ecl, shape(ecl, ccl))
        for i, l in enumerate(ELLS):
            fh.write(f"{int(l)},{ours[i]:.9e},{ours_printed[i]:.9e},"
                     f"{rc[i]:.9e},{rl[i]:.9e}\n")
    print(f"\nwrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
