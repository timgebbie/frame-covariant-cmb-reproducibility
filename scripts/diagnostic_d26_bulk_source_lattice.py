#!/usr/bin/env python3
r"""D26 --- W1. The bulk-source lattice, scored on the SPECTRUM for the first time.

**Why this instrument and not another repair.** `integral_solution`'s seven
controls have been walked before --- on fixtures (D14), on coefficients
(c3, c4), and once on the frame gap. The frame gap is **M14**-blind: an
acceptance condition built from the difference of two frames cannot see a
defect they share, and five repairs were withdrawn after being scored against
it. **Every point of this lattice except one was also unreachable from
`transfer_by_rank`**, so none of them had ever been scored on $C_\ell$ at all.

THE TWO GATES, AND BOTH ARE NEW
-------------------------------
  **G-a, from D24 (T-121):** $\ell_{\rm peak}/\ell_A$, expected $0.757$
  (matched CAMB, $206/272.177$). The released path gives $0.030$ --- a spurious
  maximum at $\ell=8$ --- and suppressing $\kappa''\tilde v_B$ alone gives
  $0.635$.

  **G-b, from D25 (T-122):** $\langle k\rangle_\ell\big/(\ell/r_\theta)$,
  expected $\simeq1$. The released path gives **1.5--4.2**: low-$\ell$ power
  drawn from small scales, which is what a *smooth* source at 99.8% of $C_1'$
  does, having no $j_\ell$ localisation.

**A repair must move BOTH, together.** One without the other is not the
repair: G-a alone can be reached by moving power in $\ell$ without fixing
where in $k$ it comes from, and G-b alone by flattening the source without
putting the acoustic structure back. That pairing is the whole design, and it
is why this file scores two numbers rather than one.

G-b IS THE SCREEN, G-a IS THE CONFIRMATION
------------------------------------------
G-b costs four multipoles on a $k$ grid sized for $\ell\le30$; G-a costs
ninety multipoles on a grid sized for $\ell\le420$, which is about twenty
times as much. So the lattice is screened on G-b and only the configurations
that move it are put to G-a. **This is stated because it is a compromise**:
**M11a** says two defects that fix it only together score as two failures one
at a time, and a screen tests one axis at a time. The named combinations below
are therefore chosen from the derivations rather than enumerated --- 128
spectra is not available --- and **a configuration absent from this table has
not been refuted, only not run**.

WHAT c3 SAYS THE CORRECT SOURCE IS
----------------------------------
`tests/frame/c3_byparts.py`, reproducing the integral to $<10^{-8}$:

    W C_0 - (W C_1)' + (W C_2)''
      = W(C_0 - C_1' + C_2'')  -  V C_1  +  2 V C_2'  +  Vdot C_2

(102) carries **only the first group**. Of the other three, $-\mathcal VC_1$
collapses to the primary under $\int\mathcal V=1$ and this bundle already
carries it as the boundary term; $+2\mathcal VC_2'$ and $\dot{\mathcal V}C_2$
are **rank two**, identically zero in the Newtonian frame, and are what
`by_parts_weight_terms` restores. Finding **B-17**, and P1-T's §7 note is the
reason it is in this table: discrepancy (i) is a $C_2'$-for-$C_2$ substitution
with a sign, and **a $\lambda$ on $\Phi'$ cannot see it** --- D24 is blind to
exactly this, so D26 must not be.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d26-bulk-source-lattice"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    PLANCK_H, PLANCK_MODEL, PLANCK_N_S, PLANCK_OMEGA_B_H2)
from functions.spectra import two_frame as _tf  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, coefficient_sets, transfer_by_rank)

ELLS = np.array([2, 5, 10, 30])
K_MAX = 200.0
FRAMES = ("newtonian", "cdm")

#: The named configurations, each from a derivation rather than from
#: enumeration. `None` marks the released path.
CONFIGS: list[tuple[str, dict]] = [
    ("released (102) as printed", {}),
    # c3's terms 3 and 4 -- the rank-two by-parts slot. Zero in the Newtonian
    # frame by construction, so any movement there would be a bug in the hook
    # and the Newtonian column is this row's own control.
    ("+ by_parts_weight_terms  (c3 terms 3,4)",
     dict(by_parts_weight_terms=True)),
    # T-90's derivation pair, which must be tested together: moving the
    # Thomson half to V without its -Int Vdot C_1 bulk term double-counts the
    # boundary. M11a, and the reason these two are never separated.
    ("+ slot_weight_split + thomson_boundary_and_vdot",
     dict(slot_weight_split=True, thomson_boundary_and_vdot=True)),
    # T-89: only the ISW belongs under W; (k/3)tau_1 oscillates and must not.
    ("+ ... + w_half_is_isw_only  (T-89)",
     dict(slot_weight_split=True, thomson_boundary_and_vdot=True,
          w_half_is_isw_only=True)),
    # The combination B_SLOT_REPAIR names, reachable here for comparison.
    ("B_SLOT_REPAIR's combination",
     dict(slot_weight_split=True, jprime_bulk_slot=True,
          thomson_carries_shear=True, boundary_weight_w=False)),
    # c3's rank-two terms ON TOP of the weight split -- the configuration
    # P1-T's section 7 says D24 is structurally blind to.
    ("+ by_parts + slot_weight_split + vdot",
     dict(by_parts_weight_terms=True, slot_weight_split=True,
          thomson_boundary_and_vdot=True)),
]


def _env():
    gamma = shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H)
    return build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2, transfer_gamma=gamma, hubble_h=PLANCK_H,
        f_2=F2_DEFAULT, line_of_sight_weight="printed")


def _median_ratios(env, table, k_com, power) -> dict[str, list[float]]:
    r"""$\langle k\rangle_\ell/(\ell/r_\theta)$ for each frame --- gate G-b."""
    r_theta = float(env.background.eta_0 - env.eta_star)
    transfer = {f: np.zeros((ELLS.size, k_com.size)) for f in FRAMES}
    for j, k in enumerate(k_com):
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        for f in FRAMES:
            transfer[f][:, j] = transfer_by_rank(ELLS, float(k), sets[f],
                                                 env, table)[-1]
    out = {}
    for f in FRAMES:
        row = []
        for i, l in enumerate(ELLS):
            integrand = k_com ** 2 * power * transfer[f][i] ** 2
            total = float(np.trapezoid(integrand, k_com))
            if not np.isfinite(total) or total <= 0.0:
                row.append(float("nan")); continue
            cum = np.concatenate([[0.0], np.cumsum(
                0.5 * (integrand[1:] + integrand[:-1]) * np.diff(k_com))])
            median_k = float(np.interp(0.5, cum / total, k_com))
            row.append(median_k / (float(l) / r_theta))
        out[f] = row
    return out


def main() -> int:
    print(__doc__)
    env = _env()
    r_theta = float(env.background.eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    print(f"\n{'='*92}\n  GATE G-b --- median k over (l / r_theta).  "
          f"EXPECTED 1.0 EVERYWHERE.\n"
          f"  PLANCK, r_theta = {r_theta:.4f}, {k_com.size} modes to "
          f"k = {K_MAX:.0f}\n{'='*92}")
    head = " ".join(f"{'l='+str(int(l)):>8}" for l in ELLS)
    print(f"  {'configuration':<42} {'frame':<10} {head}")
    print("  " + "-" * 88)

    keep = dict(_tf.BULK_SOURCE_CONTROLS)
    try:
        for label, cfg in CONFIGS:
            _tf.BULK_SOURCE_CONTROLS = dict(cfg)
            try:
                ratios = _median_ratios(env, table, k_com, power)
            except Exception as exc:                      # noqa: BLE001
                print(f"  {label:<42} {'--':<10} RAISED: "
                      f"{type(exc).__name__}: {exc}", flush=True)
                continue
            for f in FRAMES:
                print(f"  {label if f == FRAMES[0] else '':<42} {f:<10} " +
                      " ".join(f"{v:8.3f}" for v in ratios[f]), flush=True)
            print("  " + "-" * 88, flush=True)
    finally:
        _tf.BULK_SOURCE_CONTROLS = keep

    print("""
  READING THIS
  ------------
  1.0 is the answer. It says the power at multipole l comes from the k the
  projection puts there, which is what j_l(k r_theta) does when the source it
  weights is not smooth enough to swamp it. The released row reads 1.5-4.2.

  A configuration that moves a column TOWARDS 1 is a candidate and goes to
  D24 for gate G-a; a configuration that does not is refuted ON THIS GATE and
  on no other -- it may still be right about something this does not measure.

  THE NEWTONIAN COLUMN IS THE CONTROL for the rank-two rows. C_2 == 0 there,
  so `by_parts_weight_terms` CANNOT move it. If it does, the hook is wrong and
  nothing in this table is evidence.

  THIS IS A SCREEN, NOT THE LATTICE. Six named configurations out of 128,
  chosen from the derivations. M11a's warning stands: two defects that fix it
  only together score as two failures one at a time, so a row that does not
  move here is not thereby refuted in combination with another.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
