#!/usr/bin/env python3
r"""D41 --- does the Newtonian maximum survive a finer $\ell$ grid?

**`P1T→P1B 2026-10-29 #15`.** D36 reports a Newtonian first maximum at
$\ell=60.65$ on PLANCK under both surviving weightings. Its $\ell$ grid is
`arange(40, 341, 15)`, so the samples bracketing that value are 55, 70 and 85
— and the parabola's vertex lands **0.62 of a grid step** away from the
sampled maximum it was fitted around.

That is the signature of a finder sitting on a **node** rather than on a peak.
A well-resolved maximum puts its vertex well inside the central interval; a
vertex two thirds of the way to a neighbour means the three samples do not
bracket what the finder claims they bracket. **D24 had this shape** and the
number it produced was about a plateau bump rather than an acoustic peak.

WHAT THIS DOES
--------------
The same configuration — PLANCK, $k_{\max}=460$, `split_by_parts`, Newtonian
frame, the released finder with its floor at 30 — on an $\ell$ grid stepping
by **one** through the band where the claim lives, rather than by fifteen.
Nothing else moves: same $k$ grid, same weighting, same finder.

PRE-REGISTERED
--------------
    survives     a maximum exists on the fine grid within a few multipoles of
                 60.65. The coarse grid was adequate, T-157's first count
                 stands, and P1-T's ruling keeps that leg.
    vanishes     no interior maximum above the floor anywhere on the fine
                 grid. Then 60.65 is a finder artefact on a node, the
                 Newtonian frame has no acoustic maximum under this weighting
                 either, and T-157's count is the one that changes.
    moves        a maximum exists but somewhere else. Then the existence
                 claim survives and the VALUE does not, which is the outcome
                 that most needs saying out loud because D36's table prints
                 the value.

**The finder is not changed.** Re-running the released finder on a finer grid
asks whether the grid was adequate; replacing the finder would ask a different
question and would make the answer unattributable between the two.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d41-newtonian-maximum-fine-grid"

from functions.background.flrw import (  # noqa: E402
    PLANCK_H, PLANCK_MODEL, PLANCK_N_S, PLANCK_OMEGA_B_H2)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)
from functions.spectra.pipeline import (  # noqa: E402
    primordial_power, required_k_points)
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, bulk_source_primitives, coefficient_sets)

#: **Step one, not fifteen.** Through the band D36's claim lives in, plus the
#: plateau below the floor so the finder sees the same approach it saw before.
ELLS = np.unique(np.concatenate([
    np.array([2, 3, 5, 7, 10, 15, 20, 25]),
    np.arange(28, 141, 1),
    np.arange(145, 341, 15)]))

#: D36's exactly, so the two are comparable and a disagreement is the grid.
K_MAX = 460.0
FRAME_INDEX = {"newtonian": 0, "cdm": 1}

#: **D36's finder and D36's grid, IMPORTED rather than copied.** The first
#: draft reproduced both verbatim with a note promising they would be kept in
#: step. That promise is the thing this bundle has been bitten by three times
#: --- `gen_theory_audit.py`'s three registries, the two copies of the
#: tight-coupling continuation (**T-125**), and `build_supplement.py`'s staged
#: directory list (**T-174**) --- and the whole point of D41 is that *one*
#: thing differs from D36. A copied finder is a second thing that can differ,
#: silently, and it would make a disagreement unattributable between the grid
#: and the instrument.
from diagnostic_d36_frame_invariance_by_weighting import (  # noqa: E402
    ELLS as D36_ELLS, _peak)


def _spectrum():
    env = build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2,
        transfer_gamma=shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H),
        hubble_h=PLANCK_H, f_2=F2_DEFAULT, line_of_sight_weight="printed")
    eta_star, eta_0 = float(env.eta_star), float(env.background.eta_0)
    floor = float(env.eta[0])
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, eta_0 - eta_star))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (eta_0 - floor)) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    acc = {f: np.zeros(ELLS.size) for f in FRAME_INDEX}
    dk = k_com[1] - k_com[0]
    for j, k in enumerate(k_com):
        sets = coefficient_sets(float(k), env)
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        for f, which in FRAME_INDEX.items():
            s = sets[which]
            extra = dict(split_by_parts=True, by_parts_weight_terms=True)
            extra.update(bulk_source_primitives(float(k), env, s))
            res = integral_solution(
                ELLS, coefficients=s.coefficients, c1_prime=s.c1_prime,
                c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
                c2_prime=s.c2_prime, table=table, weight=env.weight,
                diffusion=diffusion, damping_total=diffusion,
                eta_star=eta_star, eta_floor=floor,
                visibility=env.visibility, eta_0=eta_0, **extra)
            total = res.integrated + res.boundary_scalar + res.boundary_shear
            acc[f] += (k ** 2 * power[j]) * total ** 2 * dk
        if j % 200 == 0:
            print(f"      k {k:7.1f} of {K_MAX:.0f}", flush=True)
    return ELLS, acc


def main() -> int:
    print(__doc__.split("PRE-REGISTERED")[0])
    ells, acc = _spectrum()

    out = ROOT / "diagnostics" / f"{SLUG}.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("frame,ell,d_ell\n")
        for f in FRAME_INDEX:
            d = ells * (ells + 1.0) * acc[f] / (2.0 * np.pi)
            for i, l in enumerate(ells):
                fh.write(f"{f},{int(l)},{d[i]:.9e}\n")
    print(f"\n    wrote {out.relative_to(ROOT)}")

    print(f"\n{'='*74}\n  THE NEWTONIAN MAXIMUM, STEP 1 AGAINST D36's STEP 15\n{'='*74}")
    for f in FRAME_INDEX:
        d = ells * (ells + 1.0) * acc[f] / (2.0 * np.pi)
        fine = _peak(ells, d)
        keep = np.isin(ells, D36_ELLS)
        coarse = _peak(ells[keep], d[keep])
        print(f"    {f:<10} fine grid {fine:9.3f}    D36's grid reproduced "
              f"{coarse:9.3f}")

    # What the finder actually sees near the claim, printed so the reading is
    # not taken on trust.
    d = ells * (ells + 1.0) * acc["newtonian"] / (2.0 * np.pi)
    band = (ells >= 40) & (ells <= 100)
    print(f"\n    D_ell, Newtonian, 40 to 100 (normalised to its max in band):")
    dm = float(np.max(d[band])) or 1.0
    for l, v in zip(ells[band], d[band]):
        if int(l) % 4 == 0:
            bar = "#" * int(round(40 * v / dm))
            print(f"      {int(l):4d} {v/dm:7.4f} {bar}")
    print("""
    A maximum that is real shows as a turn in this column. If the column is
    monotone, D36's 60.65 was the finder interpolating across a node and the
    Newtonian frame has no acoustic maximum under this weighting either.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
