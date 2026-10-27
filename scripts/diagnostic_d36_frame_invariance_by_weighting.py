#!/usr/bin/env python3
r"""D36 --- which weighting restores frame invariance, scored on both frames.

**The instrument T-157 asks for, and the reason it did not exist.** Every
diagnostic in this bundle since D24 has been scored on the CDM frame. D34
computed the Newtonian column too --- at no extra cost, since
`coefficient_sets` returns both --- stored it in its CSV, and nobody read it.
What it said, once read, is the strongest single result the repair has
produced:

  * **released, the Newtonian frame has no acoustic maximum at all.** The peak
    finder returns `nan` on all three backgrounds; the spectrum falls
    monotonically from the plateau and is five orders down at $\ell=900$.
  * **under the split by-parts it acquires one**, at $\ell\simeq60$--68.
  * and the plateau bump $D_7/D_{30}$, which the two frames disagreed about by
    a factor of **14--33**, comes into agreement at **4--16%**.

WHY THE NEWTONIAN FRAME IS THE INSTRUMENT AND NOT A SECOND OPINION
------------------------------------------------------------------
`newtonian_set` makes $\tilde{\mathcal B}_2=0$, which sets $C_0$, $C_2$,
$C_2'$ and $C_2''$ **identically zero** --- (102) collapses to (110). So
$C_1$ is the *only* live coefficient in that frame.

That is exactly what makes it sharp. **B-17 (iv)** and **T-94** are about
$C_1$'s scattering half being by-parted when it was already in final form at
$K'=-kj_\ell'$ --- which differentiates $\kappa'$ into $\kappa''$ and moves
the Doppler out of its slot. In the CDM frame that damage is **masked**,
because $C_0$ carries the oscillation whatever happens to $C_1$. In the
Newtonian frame there is nothing to mask it, so the damage is total and shows
up as a spectrum with no peaks in it.

**First-order covariance requires the two frames to agree for $\ell\ge2$.**
They do not, at order unity. So frame agreement is not a diagnostic of taste
between weightings --- it is a condition every admissible weighting must meet,
and it can therefore *refute*.

WHAT IS RUN
-----------
Each weighting, on each background, in **both** frames, and scored on three
things the released configuration already fails:

    frame gap       median and worst |D_cdm - D_newt| / max(|.|), over ell
    newtonian peak  the first interior maximum above ell = 30, or NONE
    bump agreement  (D_7/D_30)_newt  against  (D_7/D_30)_cdm

**Normalised at $\ell=30$ in each frame separately**, exactly as F9 does, so
the gap is a statement about *shape* and not about an overall amplitude the
frames are free to differ by.

PRE-REGISTERED, fixed before this runs
--------------------------------------
    1. released    frame gap -> ~100% median. This is F9's number and is the
                   control: if it does not reproduce, the harness is wrong
                   and nothing below is evidence.
    2. split       frame gap FALLS on all three backgrounds, and the
                   Newtonian peak EXISTS. Both are D34's stored columns and
                   must reproduce here on a different grid.
    3. bracket_at_w / slot_split / isw_at_w
                   UNKNOWN. These have never been scored on a frame, which is
                   the point of running them. A weighting that makes the gap
                   WORSE than released is refuted by first-order covariance
                   and can be struck.

    OUTCOMES, fixed now:
      exactly one weighting closes the gap    that one is the assembly, and
                                              the peak position becomes the
                                              remaining question
      several close it comparably             frame agreement does not
                                              discriminate among them and a
                                              different observable is needed
      none closes it, split included          the defect is NOT in the C_1
                                              weighting and T-157's mechanism
                                              is wrong

WHAT IT CANNOT ESTABLISH
------------------------
That the surviving weighting gives the right peak POSITION. A-3 is not wired,
so every configuration here is undriven and the peak sits near $\ell_A$ rather
than at CAMB's $0.757\,\ell_A$. **Frame agreement and peak position are
separate questions and this instrument answers only the first.**
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d36-frame-invariance-by-weighting"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, LCDM_MODEL, PLANCK_H, PLANCK_MODEL, PLANCK_N_S,
    PLANCK_OMEGA_B_H2)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, bulk_source_primitives, coefficient_sets)

from _resumable import Checkpoint  # noqa: E402

#: Dense through the plateau, stepping through the acoustic band to past the
#: first peak on every background (PLANCK's released peak is 266.6).
ELLS = np.unique(np.concatenate([
    np.array([2, 3, 5, 7, 10, 15, 20, 25, 30]),
    np.arange(40, 341, 15)]))

K_MAX = 460.0
FRAMES = ("newtonian", "cdm")

BACKGROUNDS = [
    ("EdS", CDM_MODEL, 0.0224, 0.5, 0.48),
    ("LCDM", LCDM_MODEL, 0.0224, 0.5, 0.48),
    ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H, None),
]

#: The five weightings `integral_solution` admits, as the register names them.
#: `released` is (102) exactly as printed and is the control.
CONFIGS = [
    ("released", {}),
    ("bracket_at_w", dict(bracket_all_at_w=True, by_parts_weight_terms=True)),
    ("slot_split", dict(slot_weight_split=True)),
    ("isw_at_w", dict(isw_only_at_w=True)),
    ("split_by_parts", dict(split_by_parts=True, by_parts_weight_terms=True)),
]


def _peak(ells, d, floor=30.0):
    """First interior maximum above `floor`, parabolically interpolated.

    Returns `nan` when there is none --- which is **not** a failure of the
    finder and is the released Newtonian frame's actual answer.
    """
    idx = np.nonzero(ells >= floor)[0]
    for i in idx[1:-1]:
        if d[i] > d[i - 1] and d[i] >= d[i + 1]:
            den = d[i - 1] - 2.0 * d[i] + d[i + 1]
            if den == 0.0:
                return float(ells[i])
            return float(ells[i] + 0.5 * (d[i - 1] - d[i + 1]) / den
                         * (ells[i + 1] - ells[i]))
    return float("nan")


def _measure(bg, obh2, h, gamma, controls):
    if gamma is None:
        gamma = shape_parameter(bg.omega_m, h)
    env = build_environment(
        K_MAX, omega_m=bg.omega_m, omega_lambda=bg.omega_lambda,
        omega_r=bg.omega_r, omega_b_h2=obh2, transfer_gamma=gamma,
        hubble_h=h, f_2=F2_DEFAULT, line_of_sight_weight="printed")
    eta_star, eta_0 = float(env.eta_star), float(env.background.eta_0)
    span = eta_0 - eta_star
    sl = np.array([eta_star, eta_0])
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, span))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (eta_0 - env.eta[0])) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    acc = {f: np.zeros(ELLS.size) for f in FRAMES}
    gate, dk = 0.0, k_com[1] - k_com[0]
    for j, k in enumerate(k_com):
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        common = dict(table=table, weight=env.weight, diffusion=diffusion,
                      damping_total=diffusion, eta_star=eta_star,
                      eta_floor=float(env.eta[0]), visibility=env.visibility,
                      eta_0=eta_0, eta_slices=sl)
        for f in FRAMES:
            s = sets[f]
            extra = dict(controls)
            if extra:
                extra.update(bulk_source_primitives(float(k), env, s))
            res = integral_solution(
                ELLS, coefficients=s.coefficients, c1_prime=s.c1_prime,
                c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
                c2_prime=s.c2_prime, **common, **extra)
            gate = max(gate, float(np.max(
                np.abs(res.partial_bulk[:, -1] - res.integrated)
                / np.maximum(np.abs(res.integrated), 1e-300))))
            t = res.integrated + res.boundary_scalar + res.boundary_shear
            acc[f] += (k ** 2 * power[j]) * t ** 2 * dk
        if j % 500 == 0:
            print(f"        k {k:7.1f}/{K_MAX:.0f}", flush=True)

    out = {}
    d = {}
    i30 = int(np.argmin(np.abs(ELLS - 30)))
    i7 = int(np.argmin(np.abs(ELLS - 7)))
    for f in FRAMES:
        dl = ELLS * (ELLS + 1.0) * acc[f] / (2.0 * np.pi)
        # **Normalised at ell = 30 in each frame separately, as F9 does.**
        # The frames are free to differ by an overall amplitude at this order;
        # what covariance fixes is the SHAPE, so the gap must be measured on a
        # quantity an amplitude cannot move.
        d[f] = dl / dl[i30] if dl[i30] > 0 else dl
        out[f"{f}/peak"] = _peak(ELLS, d[f])
        out[f"{f}/bump7"] = float(d[f][i7])
    den = np.maximum(np.abs(d["cdm"]), np.abs(d["newtonian"]))
    gapv = np.abs(d["cdm"] - d["newtonian"]) / np.where(den > 0, den, 1.0)
    out["gap/median"] = float(np.median(gapv))
    out["gap/worst"] = float(np.max(gapv))
    return out, gate


#: Rows this instrument writes per configuration: two frames x (peak, bump7) plus gap/median and gap/worst.
#: Passed to `Checkpoint.has` so a run killed mid-write is
#: **recomputed rather than resumed as complete** --- D36 lost
#: `bracket_at_w || PLANCK` to exactly that on 2026-10-27, and the
#: gap was found only by reading a `nan` out of the summary table.
ROWS_PER_CONFIG = 6


def main() -> int:
    print(__doc__)
    rows = Checkpoint(ROOT / "diagnostics" / f"{SLUG}.csv",
                      ("background", "metric", "value", "gate"))
    seen: dict[str, dict] = {}
    for label, controls in CONFIGS:
        for bl, bg, obh2, h, gamma in BACKGROUNDS:
            key = f"{label} || {bl}"
            if rows.has(key, expect=ROWS_PER_CONFIG):
                for r in rows.all():
                    if r["configuration"] == key:
                        seen.setdefault(label, {})[(bl, r["metric"])] = \
                            float(r["value"])
                print(f"  [resumed] {key}", flush=True)
                continue
            try:
                got, gate = _measure(bg, obh2, h, gamma, controls)
            except Exception as exc:                          # noqa: BLE001
                print(f"  {key}: RAISED {type(exc).__name__}: {exc}",
                      flush=True)
                continue
            for m, v in got.items():
                rows.add(key, background=bl, metric=m, value=f"{v:.6e}",
                         gate=f"{gate:.3e}")
                seen.setdefault(label, {})[(bl, m)] = v
            print(f"  {key}: gate {gate:.1e}  gap {got['gap/median']*100:6.2f}% "
                  f"median {got['gap/worst']*100:7.2f}% worst   "
                  f"newt peak {got['newtonian/peak']:7.2f}  "
                  f"cdm peak {got['cdm/peak']:7.2f}", flush=True)

    print(f"\n{'='*94}\n  FRAME GAP, median over ell. Covariance requires ~0 "
          f"for ell >= 2.\n{'='*94}")
    print(f"  {'weighting':<20} " + "".join(f"{b[0]:>14}" for b in BACKGROUNDS))
    for label, _ in CONFIGS:
        g = seen.get(label, {})
        print(f"  {label:<20} " + "".join(
            f"{g.get((b[0], 'gap/median'), float('nan'))*100:13.2f}%"
            for b in BACKGROUNDS))

    print(f"\n  NEWTONIAN first maximum above ell=30. `nan` = THERE IS NONE.")
    print(f"  {'weighting':<20} " + "".join(f"{b[0]:>14}" for b in BACKGROUNDS))
    for label, _ in CONFIGS:
        g = seen.get(label, {})
        print(f"  {label:<20} " + "".join(
            f"{g.get((b[0], 'newtonian/peak'), float('nan')):14.2f}"
            for b in BACKGROUNDS))

    print(f"\n  PLATEAU BUMP D_7/D_30, newtonian / cdm. Covariance requires 1.")
    print(f"  {'weighting':<20} " + "".join(f"{b[0]:>14}" for b in BACKGROUNDS))
    for label, _ in CONFIGS:
        g = seen.get(label, {})
        cells = []
        for b in BACKGROUNDS:
            n = g.get((b[0], "newtonian/bump7"), float("nan"))
            c = g.get((b[0], "cdm/bump7"), float("nan"))
            cells.append(f"{(n / c if c else float('nan')):14.3f}")
        print(f"  {label:<20} " + "".join(cells))

    print("""
  A weighting that makes the gap WORSE than released is refuted by
  first-order covariance and can be struck without further argument.
  A weighting that closes it is NOT thereby shown to give the right peak
  position: A-3 is not wired and every column here is undriven.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
