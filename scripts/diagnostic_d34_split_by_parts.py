#!/usr/bin/env python3
r"""D34 --- P1-T's split by-parts, scored on their four predictions.

**Specified by P1-T 2026-10-25T17:25Z (v1.3.15), pre-registered here.**
**Supersedes the (98) branch of D33**, which P1-T withdrew in the same note:
the ISW arrives at $W$ as a by-product of the split rather than as a separate
change, and no $\kappa''$ is created to be suppressed afterwards.

THE OPERATION, AND IT IS ONE
----------------------------
(102) by-parts **all** of $C_1$. The gravitational half is a gradient and must
be; the scattering half was already in final form at $K'=-kj_\ell'$ and must
not be. **(90) is exonerated** --- $C_1$ carries $\kappa'v_B$ precisely so that
$WC_1^{\rm scatt}=-\mathcal V\hat v_B$ is the standard Doppler source.

Doing both at once produces three findings that are one:

  * $\kappa'\to\kappa''$ weighted by $\mathcal V$ instead of $W$ --- **T-94**,
    $1.8\times10^5$ times the Doppler source, and the ratio *is* $\kappa''$;
  * the Doppler term leaves the $j_\ell'$ slot --- **B-17 (iv)** is a term
    (102) *removed*, not one it lacks;
  * $\kappa'\hat v_B$ enters the boundary beside Sachs--Wolfe --- **T-101**,
    **T-121**, the $\kappa'$ share of $C_1(\eta_*)$ being 1.046--1.088 at
    $k=2$--$5$.

PRE-REGISTERED --- P1-T's four, fixed before this runs
-------------------------------------------------------
    1. the kappa'' term vanishes IDENTICALLY -- absent, not suppressed.
    2. the first peak moves 266.6 -> 236.6 +/- 5 on PLANCK_MODEL and STOPS
       there, because the radiation driving (A-3) is still absent.
    3. the ell ~ 7 plateau bump falls by the kappa' share, ~10^2.
    4. the late share rises from 1e-04 to O(0.1) on the Lambda backgrounds
       and stays EXACTLY 0 on Einstein-de Sitter. It did not reach O(0.1)
       under D33 because the denominator was still inflated by the artefact.

    OUTCOMES, fixed now:
      all four hold                  the assembly is repaired; what remains
                                     of the peak is A-3, an oscillator change
      peak moves past 236.6 toward   the split is doing A-3's work too, which
      206                            would mean the driving was not absent but
                                     drowned -- a different finding
      peak does not move             the kappa'' artefact is not what holds
                                     the peak at l_A, and P1-T's budget fails
      EdS late share non-zero        the null control fails and NOTHING here
                                     is evidence

WHAT IT CANNOT ESTABLISH
------------------------
That the spectrum is then right. A-3 is not wired, so by prediction 2 the peak
must stop 30 multipoles short of CAMB's 206 --- and **stopping short is the
success condition**, not a shortfall.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d34-split-by-parts"
VERSION = "v1.3.0"

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

#: Dense at the plateau so the ell ~ 7 bump is resolved, and stepping by 10
#: across the acoustic band so 236.6 +/- 5 is a statement the grid can carry.
ELLS = np.unique(np.concatenate([
    np.array([2, 3, 5, 7, 9, 12, 16, 20, 25, 30]),
    np.arange(40, 341, 10)]))

K_MAX = 460.0
N_SLICES = 12
FRAMES = ("newtonian", "cdm")
LATE_FROM = 0.01

BACKGROUNDS = [
    ("EdS", CDM_MODEL, 0.0224, 0.5, 0.48),
    ("LCDM", LCDM_MODEL, 0.0224, 0.5, 0.48),
    ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H, None),
]

CONFIGS = [
    ("released", {}),
    ("split by-parts", dict(split_by_parts=True)),
]


def _peak(ells, d, floor=30.0):
    """First interior maximum above `floor`, parabolically interpolated."""
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
    sl = eta_star + np.concatenate(
        [[0.0], np.geomspace(span * 1e-4, span, N_SLICES - 1)])
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, span))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (eta_0 - env.eta[0])) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    acc = {f: np.zeros((ELLS.size, sl.size)) for f in FRAMES}
    gate, dk = 0.0, k_com[1] - k_com[0]
    for j, k in enumerate(k_com):
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        common = dict(table=table, weight=env.weight, diffusion=diffusion,
                      damping_total=diffusion, eta_star=eta_star,
                      eta_floor=float(env.eta[0]), visibility=env.visibility,
                      eta_0=eta_0)
        for f in FRAMES:
            s = sets[f]
            extra = dict(controls)
            if extra:
                extra.update(bulk_source_primitives(float(k), env, s))
            res = integral_solution(
                ELLS, coefficients=s.coefficients, c1_prime=s.c1_prime,
                c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
                c2_prime=s.c2_prime, eta_slices=sl, **common, **extra)
            gate = max(gate, float(np.max(
                np.abs(res.partial_bulk[:, -1] - res.integrated)
                / np.maximum(np.abs(res.integrated), 1e-300))))
            boundary = (res.boundary_scalar + res.boundary_shear)[:, None]
            acc[f] += (k ** 2 * power[j]) * (res.partial_bulk + boundary) ** 2 * dk
        if j % 400 == 0:
            print(f"        k {k:7.1f}/{K_MAX:.0f}", flush=True)

    x = (sl - eta_star) / span
    out = {}
    for f in FRAMES:
        cl = acc[f][:, -1]
        d = ELLS * (ELLS + 1.0) * cl / (2.0 * np.pi)
        i30 = int(np.argmin(np.abs(ELLS - 30)))
        i7 = int(np.argmin(np.abs(ELLS - 7)))
        out[f"{f}/late2"] = (
            1.0 - float(np.interp(LATE_FROM, x, acc[f][0] / acc[f][0, -1]))
            if acc[f][0, -1] > 0 else float("nan"))
        # the bump: D_7 against D_30, which is what "a bump at ell ~ 7" means
        out[f"{f}/bump7"] = float(d[i7] / d[i30]) if d[i30] > 0 else float("nan")
        out[f"{f}/D2_D30"] = float(d[0] / d[i30]) if d[i30] > 0 else float("nan")
        out[f"{f}/peak"] = _peak(ELLS, d)
    return out, gate


def main() -> int:
    print(__doc__)
    rows = Checkpoint(ROOT / "diagnostics" / f"{SLUG}.csv",
                      ("background", "metric", "value", "gate"))
    seen: dict[str, dict] = {}
    for label, controls in CONFIGS:
        for bl, bg, obh2, h, gamma in BACKGROUNDS:
            key = f"{label} || {bl}"
            if rows.has(key):
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
            print(f"  {key}: gate {gate:.1e}  peak {got['cdm/peak']:7.2f}  "
                  f"bump7 {got['cdm/bump7']:8.3f}  "
                  f"late2 {got['cdm/late2']:+.4f}", flush=True)

    print(f"\n{'='*92}\n  AGAINST P1-T's FOUR, read as written\n{'='*92}")
    for m, name, pred in (
            ("peak", "first peak (CDM)", "2: 266.6 -> 236.6 +/- 5 on PLANCK, and STOPS"),
            ("bump7", "plateau bump D_7/D_30 (CDM)", "3: falls by the kappa' share, ~1e2"),
            ("late2", "late share at ell=2 (CDM)", "4: O(0.1) on Lambda, EXACTLY 0 on EdS")):
        print(f"\n  {name}\n    prediction {pred}")
        print(f"    {'configuration':<20} " +
              "".join(f"{b[0]:>13}" for b in BACKGROUNDS))
        for label, _ in CONFIGS:
            g = seen.get(label, {})
            print(f"    {label:<20} " + "".join(
                f"{g.get((b[0], f'cdm/{m}'), float('nan')):13.4f}"
                for b in BACKGROUNDS))
    print("""
  1 is STRUCTURAL and is asserted in the code rather than measured here: the
    split branch never forms C_1^scatt', so no kappa'' exists to suppress.
  And the success condition for 2 is STOPPING at 236.6, not reaching 206 --
    A-3 is not wired, so a peak that ran to 206 would mean the split is doing
    the driving's work and would be a DIFFERENT finding.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
