#!/usr/bin/env python3
r"""D8 --- criterion 5b's gate: (102) against (177)--(179), mode by mode.

    python scripts/diagnostic_d8_criterion_5b_gate.py

**What the gate is, and why it is this one.** Decision **S4c** sets criterion
5b's tolerance against *this bundle's own pipeline* rather than against CAMB and
CLASS. The two external codes are still run, still stamped, and still reported
--- by `scripts/compare_criterion_5b.py`, as context --- but they are not the
threshold. The reason is stated plainly in `provenance/CRITERION-5B-v1.md` and
is not a convenience: (102) is a slow-decoupling solution with no polarisation
hierarchy, no neutrino anisotropic stress and a visibility-weighted line of
sight, and a criterion it can only fail is not a criterion.

What *is* gateable, and is the thing v1.2.0's audit half (**S26**) exists to
establish, is that *Annals II*'s two writings of its own integral solution agree:
(102) carried with a generic $u^a$ and specialised afterwards, against the source
assembly (177)--(179) written in the Newtonian frame from the start. The paper
states the relation and carries the recovery out symbolically, which is the
right way to do it; nothing evaluates both forms and compares them. That is done
here.

**Stated at the transfer level at fixed $k$, with the same weight on both
sides.** Not at $C_\ell$, where the two branches legitimately differ by a factor
of eighty in the plateau --- that difference is approximations **A-1** and
**A-2**, the weight the line-of-sight integral carries, and it is a property of
what (102) prints rather than a disagreement to be gated away. The weighting is
measured separately by F6 and recorded as an approximation, not as a defect.

**What this gate does not establish.** Both routes are handed the same
background, the same recombination history, the same acoustic solution, the same
potentials, the same Bessel table and the same damping. A comparison that holds
an input fixed cannot check that input --- finding **T-3**, which is in this
bundle's record precisely because a coarsened grid once returned a smooth,
plausible spectrum 575% wrong while two routes agreed to $10^{-16}$. The shared
inputs are enumerated in `functions/spectra/two_route.py` and each is checked
elsewhere against something it did not come from. This gate establishes the
assembly algebra and says so.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL,
    LCDM_MODEL,
    PLANCK_MODEL,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.two_route import two_route_transfer  # noqa: E402

#: Criterion 5b names **the CDM and ΛCDM spectra**, and the external context is
#: run on `PLANCK_MODEL`. All three are gated, so the criterion's stated scope
#: and the comparison's actual cosmology are both covered rather than one
#: standing in for the other.
BACKGROUNDS = (
    ("CDM (Einstein-de Sitter)", CDM_MODEL, 0.0224),
    ("LCDM", LCDM_MODEL, 0.0224),
    ("PLANCK_MODEL", PLANCK_MODEL, PLANCK_OMEGA_B_H2),
)

#: **Logarithmic on purpose, and this is not T-32's mistake repeated.** That
#: finding --- and S24's correction to itself --- is about the $k$ grid a
#: *quadrature* runs on: a logarithmic grid aliases the integrand at high $k$
#: however many points it has, so $C_\ell$'s grid is linear at $dk=\pi/6$. Here
#: nothing is integrated over $k$. Each mode is an independent evaluation of the
#: same algebra, so the sampling law is free and the useful one spans decades.
K_SWEEP = np.array([0.3, 1.0, 3.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0])

#: Both bands the criterion states: the plateau ($2\le\ell<30$) and the acoustic
#: range ($30\le\ell<1000$).
ELLS = np.array([2, 5, 10, 50, 200, 600])

#: The gate. Measured worst is $9.5\times10^{-6}$, so the gate stands a hundred
#: times above it: it is a gate against a *regression* in the assembly algebra,
#: not a tolerance tuned to the number it already returns. A tolerance set at
#: the measured value is one that fails on the next platform --- finding
#: **T-15**, residual artefacts agreeing across machines to under one
#: significant figure. What it is sized to catch is an algebra defect, and those
#: are not marginal: a wrong sign, a dropped term or a mis-specialised
#: coefficient moves this by $10^{-1}$ or more. T-41's plateau was a factor of
#: eighty.
GATE = 1.0e-3


def main() -> int:
    print("D8  criterion 5b's gate: (102) against (177)-(179), mode by mode")
    print(f"    {K_SWEEP.size} modes k={K_SWEEP.min()}..{K_SWEEP.max()}, "
          f"ells {list(ELLS)}, {len(BACKGROUNDS)} backgrounds, gate {GATE:.0e}")

    rows: list[tuple[str, float, int, np.ndarray]] = []
    shipped: list[tuple[str, float, np.ndarray]] = []
    for name, background, omega_b_h2 in BACKGROUNDS:
        print(f"\n  {name}")
        print("      k    n_eta " + "".join(f"  l={l:<4d}" for l in ELLS)
              + "     worst  as-shipped")
        for k in K_SWEEP:
            gated = two_route_transfer(float(k), ELLS, background=background,
                                       omega_b_h2=omega_b_h2)
            as_is = two_route_transfer(float(k), ELLS, background=background,
                                       omega_b_h2=omega_b_h2,
                                       match_interpolation=False)
            rows.append((name, float(k), gated.n_eta, gated.relative))
            shipped.append((name, float(k), as_is.relative))
            print(f"    {k:7.1f} {gated.n_eta:6d} "
                  + "".join(f" {r:8.1e}" for r in gated.relative)
                  + f"  {gated.worst:8.2e}  {as_is.worst:8.2e}")

    every = np.array([r for _, _, _, r in rows])
    as_shipped = np.array([r for _, _, r in shipped])
    # `nan >= gate` is `False`, so a reduction that admitted one would hand this
    # script a PASS it never measured. Finding **T-44**; the finiteness
    # assertion below is the belt to this brace.
    worst = float(np.nanmax(every))
    flat = int(np.nanargmax(every))
    at_name, at_k, _, _ = rows[flat // every.shape[1]]
    at_ell = int(ELLS[flat % every.shape[1]])

    print(f"\n  worst over all (background, k, l):  {worst:.3e}"
          f"   [{at_name}, k={at_k:g}, l={at_ell}]")
    print(f"  median:                             {float(np.nanmedian(every)):.3e}")
    print("  per band:  "
          f"plateau 2<=l<30 {float(np.nanmax(every[:, ELLS < 30])):.3e}   "
          f"acoustic 30<=l<1000 {float(np.nanmax(every[:, ELLS >= 30])):.3e}")
    print("\n  the same comparison with the interpolants NOT matched --- "
          "(102) cubic at eta_*, pipeline.run linear, finding T-46:")
    print(f"    worst {float(np.nanmax(as_shipped)):.3e}, median "
          f"{float(np.nanmedian(as_shipped)):.3e}. This is the shipped "
          "pipeline's own boundary read, not an algebra difference, and it is "
          "reported here rather than left to be discovered.")

    out = ROOT / "outputs" / "criterion-5b-gate.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# criterion 5b's gate, decision S4c: |(102) - (177)-(179)| / |(177)-(179)|\n")
        fh.write("# transfer at fixed k, same e^{-kappa} weight on both sides\n")
        fh.write(f"# gate {GATE:.1e}; worst measured {worst:.6e}\n")
        fh.write("# normalised by max_l |Delta_l(k)|, not pointwise: see "
                 "functions/spectra/two_route.py\n")
        fh.write("background,k,n_eta," + ",".join(f"ell_{l}" for l in ELLS)
                 + "," + ",".join(f"as_shipped_ell_{l}" for l in ELLS) + "\n")
        for (name, k, n_eta, rel), (_, _, ship) in zip(rows, shipped):
            fh.write(f"{name},{k:.6g},{n_eta}," 
                     + ",".join(f"{r:.6e}" for r in rel) + ","
                     + ",".join(f"{r:.6e}" for r in ship) + "\n")
    print(f"\nwrote {out.relative_to(ROOT)}")

    # **A gate that cannot fail is not a gate.** The first version of this
    # script reduced with `max` over an array containing `nan`, got `nan`, and
    # printed PASS --- because `nan >= GATE` is `False`. Finding **T-44**. The
    # comparison below is written so that anything other than a measured number
    # under the gate is a failure.
    if not np.isfinite(worst) or every.size == 0:
        print(f"\nFAIL  the worst difference is {worst!r} over {every.size} "
              "pairs. An undefined or empty comparison is a failure, never a "
              "pass")
        return 1
    if worst >= GATE:
        print(f"\nFAIL  the two routes differ by {worst:.3e}, at or above the "
              f"gate {GATE:.1e}. They are the same calculation written in two "
              "orders and must not differ: this is an assembly defect, not a "
              "tolerance to widen.")
        return 1
    print(f"PASS  criterion 5b's gate: {worst:.3e} < {GATE:.1e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
