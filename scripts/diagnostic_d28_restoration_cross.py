#!/usr/bin/env python3
r"""D28 --- the two crosses nobody has run, and one of them is the PI's decisive test.

**Why this file exists.** G-a returned on 2026-10-23 and the pre-registered
prediction **failed**: `B_SLOT_REPAIR`'s combination, which won gate G-b
decisively (CDM median-$k$ 4.248 → 1.521), left $\ell_{\rm peak}/\ell_A$ at
**0.0073 in both frames** — the released value, and in the CDM frame it
*removed* the spurious $\ell=8$ maximum rather than moving it. **The two gates
disagree**, which is the third outcome the pre-registration fixed in advance
and is reported as a failure rather than as a narrower success.

So a configuration can fix *where in $k$ the power comes from* and do nothing
for *where in $\ell$ it lands*. That is worth more than a success would have
been: it says the two gates are not measuring one defect, and no single-gate
screen can be trusted again.

THE TWO CROSSES
---------------
**Cross A --- the PI's test.** *"The $+2\mathcal VC_2'$ restoration in the
$\kappa''$-suppressed CDM run is the decisive test and needs no repair to
run."* Correct, and it has never been run: D26 varies
`by_parts_weight_terms` at $\kappa''=1$, D24 varies $\kappa''$ with
`by_parts` off. **The cross of the two is empty.** It matters because
$+2\mathcal VC_2'$ is the only place the CDM column's Sachs--Wolfe
contribution can live (P1-T §9.2), and at $\kappa''=1$ that column is 99.8%
drowned — so restoring it there could not show.

**Cross B --- P1-T's \S3.** `thomson_boundary_and_vdot` sends CDM $\ell=2$ to
124 on G-b, and I used that to exclude it. P1-T's objection is my own M11a
turned on me: that control corrects what sits at the **boundary** and not the
**weight** on it, which is B-17's discrepancy (iii) and `boundary_weight_w`'s
job. Run without it, the identity's boundary content sits under the released
boundary's weight — two treatments, no reason the mixture behaves.

    P1-T's PREDICTION, stated before the run so it can fail visibly:
      if the 124 is the mixed-boundary artefact, adding `boundary_weight_w`
      REMOVES it -- not reduces it, removes it. If 124 survives, the Thomson
      correction is genuinely at fault and P1-T is wrong.

P1-T's §2 QUESTION, ANSWERED FROM THE IMPLEMENTATION
-----------------------------------------------------
They asked whether `slot_weight_split` moves the **whole** bracket to $W$ or
only $C_1$'s gravitational half, reading a docstring and saying so. From
`integral_solution.py` itself:

    bracket_w = coefficients.c0 - c1_grav_prime + c2_second
    bracket_v = -c1_thom_prime
    weight_w   = W_arr * diffusion
    weight_v   = visibility * diffusion

**$C_0$ and $C_2''$ go to $W$ with the gravitational half of $C_1'$; only the
Thomson half stays at $\mathcal V$.** So it does address discrepancy (i) for
all three bracket terms, the docstring's wording is narrower than the code,
and `by_parts + slot_weight_split` **is** the identity modulo (iii) and (iv).
The column is labelled correctly. **The docstring is what needs the repair**,
and that is P1-B's file.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d28-restoration-cross"
VERSION = "v1.3.0"

from functions.background.flrw import PLANCK_N_S  # noqa: E402
from functions.spectra import coefficients as _co  # noqa: E402
from functions.spectra import two_frame as _tf  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402

from diagnostic_d24_phi_prime_sweep import (  # noqa: E402
    ELL_A, ELLS, FRAMES, K_MAX, _env, peak_position, spectra_both_frames)

#: (label, BULK_SOURCE_CONTROLS, KAPPA_SECOND_LAMBDA)
CONFIGS: list[tuple[str, dict, float]] = [
    # the two reference points, re-measured here so the table is self-contained
    ("kappa''=0 only  (T-121, l=172.75)", {}, 0.0),
    # CROSS A -- the PI's decisive test
    ("kappa''=0  +  by_parts (+2 V C_2')",
     dict(by_parts_weight_terms=True), 0.0),
    # CROSS A, with the bracket also at W -- the full identity, undrowned
    ("kappa''=0  +  by_parts + slot_weight_split",
     dict(by_parts_weight_terms=True, slot_weight_split=True), 0.0),
    # CROSS B -- P1-T's section 3, at the released kappa''
    ("by_parts + slot + vdot + boundary_weight_w  (P1-T 3)",
     dict(by_parts_weight_terms=True, slot_weight_split=True,
          thomson_boundary_and_vdot=True, boundary_weight_w=True), 1.0),
]


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

    print(f"\n{'='*94}\n  ell_peak / ell_A.   target 0.757 (matched CAMB).  "
          f"released 0.0298 CDM.\n  PLANCK, r_theta = {r_theta:.4f}, "
          f"{k_com.size} modes to k = {K_MAX:.0f}\n{'='*94}")
    print(f"  {'configuration':<52} {'frame':<10} {'l_peak':>9} {'/ell_A':>8}")
    print("  " + "-" * 84)

    keep_b = dict(_tf.BULK_SOURCE_CONTROLS)
    keep_k = _co.KAPPA_SECOND_LAMBDA
    try:
        for label, cfg, k2 in CONFIGS:
            _tf.BULK_SOURCE_CONTROLS = dict(cfg)
            _co.KAPPA_SECOND_LAMBDA = float(k2)
            try:
                d = spectra_both_frames(env, table, k_com, power)
            except Exception as exc:                      # noqa: BLE001
                print(f"  {label:<52} {'--':<10} RAISED "
                      f"{type(exc).__name__}: {exc}", flush=True)
                continue
            for f in FRAMES:
                pos, _ = peak_position(ELLS, d[f])
                print(f"  {label if f == FRAMES[0] else '':<52} {f:<10} "
                      f"{pos:9.2f} {pos/ELL_A:8.4f}", flush=True)
            print("  " + "-" * 84, flush=True)
    finally:
        _tf.BULK_SOURCE_CONTROLS = keep_b
        _co.KAPPA_SECOND_LAMBDA = keep_k

    print("""
  READING THIS
  ------------
  CROSS A (rows 1-3). Row 1 is T-121's 0.635 re-measured. If restoring
  +2 V C_2' moves it TOWARD 0.757, the rank-two slot is carrying the CDM
  column's Sachs-Wolfe contribution as P1-T's 9.2 says it must, and the
  restoration is a repair rather than a knob. If it does not move, that
  argument is refuted at spectrum level and B-17's (ii) is not the peak.

  CROSS B (row 4). P1-T predicted the 124 at CDM l=2 is REMOVED, not reduced,
  by adding boundary_weight_w. This run reports l_peak rather than median k,
  so the companion G-b number is needed to score that prediction exactly;
  what this row settles is whether the full boundary treatment does anything
  for the peak, which no configuration so far has.

  AND THE STANDING CAVEAT, unchanged: PLANCK only, four configurations of 128,
  and neither gate says the plateau is RIGHT -- reference/ carries C_l only.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
