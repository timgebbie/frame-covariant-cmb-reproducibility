#!/usr/bin/env python3
r"""D33 --- (98)'s $W$-weighted path integral, scored on P1-T's three predictions.

**Specified by P1-T 2026-10-25T16:55Z, pre-registered here before it runs.**

P1-T settled the question this instrument exists to act on. (102) as printed
has **no bulk term at $W$** --- every weight in it is $\mathcal V$ --- while
**(98), in the same section of the antecedent, carries $e^{-\kappa}$ on
gravitational sources and $\kappa'e^{-\kappa}$ on scattering sources**, and
the antecedent calls the two *the same solution*. That makes B-17 (i) a
**transcription defect between (98) and (102)**, not a regime, and the
acceptance criteria stand.

So this is not an exploratory control. It is (98) as the antecedent writes it.

WHAT IS RUN, AND WHY IT IS TWO CHANGES AND NOT ONE
--------------------------------------------------
`isw_only_at_w` puts the $(\Phi_A'-\Phi_H')$ content of the bracket at $W$
and leaves everything else at $\mathcal V$ --- which is (98)'s split for the
one term both streams agree about. $C_0$ and $C_2''$ stay at $\mathcal V$
pending P1-T's rank-0 answer, because T-143 measured that moving them to $W$
exposes a growing mode $33\times$ larger than the channel being looked for.

**And it is run with `TAU_CONTINUATION="free_stream"` as well**, because the
two defects are one mechanism. The hierarchy is frozen at
$\eta_{\rm couple}=6\eta_\ast$ --- 15.6% of the conformal span (**T-145**) ---
and under $\mathcal V$ that freeze multiplies by zero and is invisible. **The
moment the bulk rides at $W$ the integral runs to $\eta_0$ and the frozen
source becomes load-bearing immediately.** Scoring the weight change against a
frozen source would measure the freeze and call it the weight.

Both are therefore run, and separately, so the attribution is not a guess.

PRE-REGISTERED --- P1-T's predictions, fixed before this runs
-------------------------------------------------------------
    1. late share at ell = 2 becomes O(0.1) on LCDM and PLANCK,
       and stays EXACTLY 0 on Einstein-de Sitter.
    2. the low-ell plateau LIFTS on the Lambda backgrounds and NOT on EdS,
       because EdS has no late ISW to restore.
    3. the first peak DOES NOT MOVE -- it lives in the k-integral, which the
       weight does not enter except through the damping.

    **If (3) fails and the peak moves, that is a fourth finding and not a
    success**: it would mean the weight is entangled with the k-dependence.

    And P1-B's own, added because the ISW channel is small:
    4. the effect is bounded by what the channel carries. The ISW content of
       C_1' is 9.1e-05 of it (T-151), so a plateau lift of order unity would
       itself need explaining and would NOT be a clean confirmation.

WHAT IT CANNOT ESTABLISH
------------------------
That the restored plateau is the RIGHT height. `reference/` carries C_ell
only, and the comparison to CAMB and CLASS is context rather than a gate
(S4c). This measures presence, direction and background-dependence.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d33-w-path-integral"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, LCDM_MODEL, PLANCK_H, PLANCK_MODEL, PLANCK_N_S,
    PLANCK_OMEGA_B_H2)
from functions.spectra import pipeline as _pl  # noqa: E402
from functions.spectra import two_frame as _tf  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, bulk_source_primitives, coefficient_sets)

from _resumable import Checkpoint  # noqa: E402

#: The plateau needs low ell resolved and the peak needs ell ~ 200 present.
ELLS = np.unique(np.concatenate([
    np.array([2, 3, 5, 7, 10, 15, 20, 30]),
    np.arange(40, 321, 20)]))

K_MAX = 420.0
N_SLICES = 12
FRAMES = ("newtonian", "cdm")
LATE_FROM = 0.01

BACKGROUNDS = [
    ("EdS", CDM_MODEL, 0.0224, 0.5, 0.48),
    ("LCDM", LCDM_MODEL, 0.0224, 0.5, 0.48),
    ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H, None),
]

#: (label, bulk-source controls, TAU_CONTINUATION)
CONFIGS = [
    ("released", {}, "freeze"),
    ("(98) ISW at W", dict(isw_only_at_w=True), "freeze"),
    ("(98) ISW at W + free-streamed source",
     dict(isw_only_at_w=True), "free_stream"),
]


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

    x = (sl - eta_star) / span
    out = {}
    for f in FRAMES:
        cl = acc[f][:, -1]
        d = ELLS * (ELLS + 1.0) * cl / (2.0 * np.pi)
        i30 = int(np.argmin(np.abs(ELLS - 30)))
        # (1) late share at the quadrupole
        out[f"{f}/late2"] = (
            1.0 - float(np.interp(LATE_FROM, x, acc[f][0] / acc[f][0, -1]))
            if acc[f][0, -1] > 0 else float("nan"))
        # (2) the plateau, as the ratio the register already quotes
        out[f"{f}/D2_D30"] = float(d[0] / d[i30]) if d[i30] > 0 else float("nan")
        # (3) the first interior maximum above ell = 30
        pk = float("nan")
        for i in range(i30 + 1, ELLS.size - 1):
            if d[i] > d[i - 1] and d[i] >= d[i + 1]:
                pk = float(ELLS[i])
                break
        out[f"{f}/peak"] = pk
    return out, gate


#: Rows this instrument writes per configuration: two frames x (late2, D2_D30, peak).
#: Passed to `Checkpoint.has` so a run killed mid-write is
#: **recomputed rather than resumed as complete** --- D36 lost
#: `bracket_at_w || PLANCK` to exactly that on 2026-10-27, and the
#: gap was found only by reading a `nan` out of the summary table.
ROWS_PER_CONFIG = 6


def main() -> int:
    print(__doc__)
    rows = Checkpoint(ROOT / "diagnostics" / f"{SLUG}.csv",
                      ("background", "metric", "value", "gate"))
    keep_c, keep_t = dict(_tf.BULK_SOURCE_CONTROLS), _pl.TAU_CONTINUATION
    seen: dict[str, dict] = {}
    try:
        for label, controls, cont in CONFIGS:
            for bl, bg, obh2, h, gamma in BACKGROUNDS:
                key = f"{label} || {bl}"
                if rows.has(key, expect=ROWS_PER_CONFIG):
                    for r in rows.all():
                        if r["configuration"] == key:
                            seen.setdefault(label, {})[(bl, r["metric"])] = \
                                float(r["value"])
                    print(f"  [resumed] {key}", flush=True)
                    continue
                _pl.TAU_CONTINUATION = cont
                try:
                    got, gate = _measure(bg, obh2, h, gamma, controls)
                except Exception as exc:                      # noqa: BLE001
                    print(f"  {key}: RAISED {type(exc).__name__}: {exc}",
                          flush=True)
                    continue
                for m, v in got.items():
                    rows.add(key, background=bl, metric=m, value=f"{v:.6e}",
                             gate=f"{gate:.3e}")
                    seen.setdefault(label, {})[(bl, m)] = v
                print(f"  {key}: gate {gate:.1e}  "
                      f"late2(cdm) {got['cdm/late2']:+.4f}  "
                      f"D2/D30(cdm) {got['cdm/D2_D30']:.4f}  "
                      f"peak(cdm) {got['cdm/peak']:.0f}", flush=True)
    finally:
        _tf.BULK_SOURCE_CONTROLS = keep_c
        _pl.TAU_CONTINUATION = keep_t

    print(f"\n{'='*92}\n  AGAINST THE PRE-REGISTRATION, read as written\n{'='*92}")
    for m, name in (("late2", "late share at ell=2"),
                    ("D2_D30", "plateau  D_2/D_30"),
                    ("peak", "first peak above ell=30")):
        print(f"\n  {name}   (CDM frame)")
        print(f"    {'configuration':<40} " +
              "".join(f"{b[0]:>12}" for b in BACKGROUNDS))
        for label, _, _ in CONFIGS:
            g = seen.get(label, {})
            print(f"    {label:<40} " + "".join(
                f"{g.get((b[0], f'cdm/{m}'), float('nan')):12.4f}"
                for b in BACKGROUNDS))
    print("""
  1. late share O(0.1) on LCDM and PLANCK, EXACTLY 0 on EdS
  2. the plateau LIFTS on the Lambda backgrounds and NOT on EdS
  3. the first peak DOES NOT MOVE
     -> if it moves, that is a FOURTH FINDING and not a success.
  4. and the channel is 9.1e-05 of C_1' (T-151), so an order-unity lift
     would itself need explaining.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
