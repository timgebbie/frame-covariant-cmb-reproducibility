#!/usr/bin/env python3
r"""D35 --- which term in the $W$-bracket accumulates on Einstein--de Sitter?

**The blocking question made specific.** D34's split by-parts moves the
$\ell\simeq7$ bump down by 30--50$\times$ and the Planck peak by eighty
multipoles, and **fails the Einstein--de Sitter null control at $1.0000$**
where it must read exactly $0$. By the outcome fixed before that run, nothing
in it is evidence until the null is understood.

**T-143 named the suspect and did not convict it.** It measured that
$C_0=+\tfrac13kv$ grows by $\sqrt{1+z_\ast}=33$ while $W$ falls only to
$0.368$, and that the bracket at $\eta_0$ is $1.04$--$1.18$ times $C_0$ --- a
statement about the *bracket's ratio*, not about *what accumulates*. P1-T's
rank-0 answer then confirmed $C_0$ belongs at $W$ unchanged, so the suspect is
now in direct disagreement with a derivation and deserves a verdict rather
than a suspicion.

WHAT THIS DOES
--------------
The $W$-bracket under `split_by_parts` is

    C_0  -  C_1^grav'  +  C_2''  +  2 V C_2'  +  Vdot C_2 .

This runs Einstein--de~Sitter with **one term suppressed at a time** and
reports the late share each time. A term whose removal takes the late share
from $1.0000$ to $\simeq0$ is the one accumulating; a term whose removal
changes nothing is exonerated.

**Scored on the late share and not on the bracket's ratio** --- which is
**M15**, and is the lesson of T-147 and T-148: a cancellation scored on the
wrong object returns a true number about something else.

PRE-REGISTERED
--------------
    C_0 removed        late share -> ~0.  C_0 = +kv/3 is the only term in
                       the bracket that grows without bound on EdS, because
                       Phi is constant there and every other term is built
                       from a derivative of something static.
    C_2'' removed      no change. T-146 measured C_2'' = -Phi_A' == 0 on EdS
                       exactly, so it has nothing to contribute.
    C_1^grav' removed  no change on EdS. It carries (Phi_A' - Phi_H'), which
                       is identically zero where Phi is constant.
    partners removed   small. They moved the null from 1.0000 to 0.9995,
                       which is their size.

    If C_0's removal does NOT clear the null, the growing mode is not the
    mechanism and T-143's attribution is wrong as well as its scoring.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d35-which-term-accumulates"

from dataclasses import replace  # noqa: E402

from functions.background.flrw import CDM_MODEL, LCDM_MODEL, PLANCK_N_S  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, bulk_source_primitives, coefficient_sets)

from _resumable import Checkpoint  # noqa: E402

ELLS = np.array([2, 7, 30])
K_MAX = 160.0
N_SLICES = 12
LATE_FROM = 0.01

#: (label, what to zero). `None` is the untouched split by-parts.
TERMS = [
    ("split by-parts, untouched", None),
    ("C_0 suppressed", "c0"),
    ("C_2'' suppressed", "c2_second"),
    ("C_1^grav' suppressed", "c1_grav"),
    ("partners suppressed", "partners"),
    # **The metric's own null, added 2026-10-26 after the first four returned
    # 0.9988 / 0.8014 / 0.9988 / 0.9987 --- that is, after NO single term
    # accounted for the EdS residue.** If the bracket is emptied ENTIRELY and
    # the late share is still ~1, then this metric is not reading the bracket:
    # it is reading the ratio of a bulk that grows all the way to eta_0 under
    # $W$ against a boundary that is fixed at $\eta_\ast$, and prediction 4 of
    # D34 was never a test of the integrated Sachs--Wolfe effect.
    #
    # **This is the control the first version of D35 lacked**, and its absence
    # is M14: four difference-gates, all blind to a defect common to all four.
    ("bracket emptied entirely", "everything"),
    # And the complement, because "C_0 is 20%" and "C_0 plus the partners are
    # 20%" are different statements and the four rows above cannot separate
    # them.
    ("C_0 and partners suppressed", "c0_and_partners"),
]

BACKGROUNDS = [("EdS", CDM_MODEL, 0.0224, 0.5, 0.48),
               ("LCDM", LCDM_MODEL, 0.0224, 0.5, 0.48)]


def _late(bg, obh2, h, gamma, zero):
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

    acc = np.zeros((ELLS.size, sl.size))
    dk = k_com[1] - k_com[0]
    for j, k in enumerate(k_com):
        s = coefficient_sets(float(k), env)[1]          # CDM frame
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        extra = dict(split_by_parts=True,
                     by_parts_weight_terms=zero not in (
                         "partners", "everything", "c0_and_partners"))
        extra.update(bulk_source_primitives(float(k), env, s))
        coeffs = s.coefficients
        c2s = np.asarray(s.c2_second, dtype=float)
        # **Suppression is by zeroing the array the bracket reads**, never by
        # a second code path: the branch under test must be the released one
        # with one input blanked, or the comparison is between two programs.
        if zero in ("c0", "everything", "c0_and_partners"):
            coeffs = replace(coeffs, c0=np.zeros_like(np.asarray(coeffs.c0)))
        if zero in ("c2_second", "everything"):
            c2s = np.zeros_like(c2s)
        if zero == "everything":
            # `bracket_w = (C_0 - C_1' + C_2'' + partners) + C_1^thom'`. With
            # C_0 and C_2'' blanked above, the partners dropped by
            # `by_parts_weight_terms=False`, and the WHOLE of C_1' handed to
            # the Thomson slot, the two C_1' terms cancel and `bracket_w` is
            # **exactly zero**. The BOUNDARY is deliberately left untouched:
            # the question is what the late share reads when the thing it is
            # supposed to be measuring is not there at all.
            extra["c1_thomson_prime"] = np.asarray(s.c1_prime, dtype=float)
        elif zero == "c1_grav":
            # zero the gravitational half by handing the whole of C_1' to the
            # Thomson slot, which split_by_parts then leaves at K'.
            extra["c1_thomson_prime"] = np.asarray(s.c1_prime, dtype=float)
        res = integral_solution(
            ELLS, coefficients=coeffs, c1_prime=s.c1_prime, c2_second=c2s,
            c2_prime_star=s.c2_prime_star, c2_prime=s.c2_prime,
            eta_slices=sl, table=table, weight=env.weight,
            diffusion=diffusion, damping_total=diffusion, eta_star=eta_star,
            eta_floor=float(env.eta[0]), visibility=env.visibility,
            eta_0=eta_0, **extra)
        boundary = (res.boundary_scalar + res.boundary_shear)[:, None]
        acc += (k ** 2 * power[j]) * (res.partial_bulk + boundary) ** 2 * dk

    x = (sl - eta_star) / span
    out = {}
    for i, l in enumerate(ELLS):
        out[int(l)] = (1.0 - float(np.interp(LATE_FROM, x, acc[i] / acc[i, -1]))
                       if acc[i, -1] > 0 else float("nan"))
    return out


def main() -> int:
    print(__doc__)
    rows = Checkpoint(ROOT / "diagnostics" / f"{SLUG}.csv",
                      ("background", "ell", "late_share"))
    seen: dict = {}
    for label, zero in TERMS:
        for bl, bg, obh2, h, gamma in BACKGROUNDS:
            key = f"{label} || {bl}"
            if rows.has(key):
                for r in rows.all():
                    if r["configuration"] == key:
                        seen[(label, bl, int(r["ell"]))] = float(r["late_share"])
                print(f"  [resumed] {key}", flush=True)
                continue
            try:
                got = _late(bg, obh2, h, gamma, zero)
            except Exception as exc:                          # noqa: BLE001
                print(f"  {key}: RAISED {type(exc).__name__}: {exc}", flush=True)
                continue
            for l, v in got.items():
                rows.add(key, background=bl, ell=l, late_share=f"{v:.6f}")
                seen[(label, bl, l)] = v
            print(f"  {key:<42} " +
                  "  ".join(f"l={l}:{v:+.4f}" for l, v in sorted(got.items())),
                  flush=True)

    print(f"\n{'='*86}\n  LATE SHARE at ell=2, CDM frame. EdS MUST be 0.\n{'='*86}")
    print(f"  {'bracket term':<30} {'EdS':>12} {'LCDM':>12}")
    for label, _ in TERMS:
        print(f"  {label:<30} " + "".join(
            f"{seen.get((label, b[0], 2), float('nan')):12.4f}"
            for b in BACKGROUNDS))
    print("""
  A term whose removal takes EdS from 1.0000 to ~0 is the one accumulating.
  A term whose removal changes nothing is exonerated.
  If NOTHING clears it, the growing mode is not the mechanism and T-143's
  attribution is wrong as well as its scoring.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
