#!/usr/bin/env python3
r"""D14 --- the B-slot repair, measured over the full control lattice.

**The repair T-86 specified, and the measurement that decides whether it is
one.** Three independent controls in `functions.spectra.integral_solution`,
all `False` by default:

    slot_weight_split   C_1's two contents separate; the gravitational half
                        moves to W = e^-kappa, the Thomson half keeps
                        g = V. Scattering damping belongs to the scattering
                        source -- this is C6 / T-81b in the same stroke.
    jprime_bulk_slot    supplies the missing +k Int W M j_l', the term the
                        identity has and (102) does not.
    boundary_weight_w   puts W(eta_*) on the boundary, where the released
                        code has the diffusion factor D(eta_0,k) alone.

**The lattice is walked in full, all eight cells, and that is M11a rather
than thoroughness for its own sake.** T-77 is the instance: two defects that
fix the gap only together score as two *failed* fixes one at a time. A single
column licenses nothing here.

THE TWO ACCEPTANCE CONDITIONS, stated before the run (T-86):

  1. the frame gap |c-n|/max must FALL,
  2. and the Newtonian column must NOT move by more than the quadrature floor
     D13 measured, ~2e-3 relative.

Condition 2 is the one that can fail quietly. A change that closes the gap by
moving the column that was already right has not repaired anything --- it has
made two wrong columns agree, which is the failure mode this register has
recorded four times.

**Frame agreement is necessary and not sufficient.** Nothing here is a claim
about the spectrum; `scripts/figure_f9_acoustic_spectrum.py` adjudicates that
and it adjudicates last.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d14-slot-repair"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.integral_solution import integral_solution  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

ELLS = np.array([2, 10, 50, 200])
KS = (10.0, 60.0, 300.0)
CONTROLS = ("slot_weight_split", "jprime_bulk_slot", "boundary_weight_w",
            "thomson_carries_shear")
#: D13's measured quadrature floor, relative. A Newtonian column that moves by
#: less than this has not moved.
FLOOR = 2.2e-3


def thomson_halves(cset, k, kappa_prime):
    r"""$C_1$'s Thomson half and its derivative, from the stored primitives.

    $-C_1 = (\delta T+\Phi_A) + \kappa'\hat v_B$ with $\hat v_B = v_B/k$, and
    `CoefficientSet.v_b` is the **un-reduced** $v_B$ (T-66, and the trap D12
    fell into on its first run). So

        C_1^{thomson}  = -kappa' v_B / k
        C_1^{thomson'} = c1_prime + a_b1_prime / k

    the second from (107), $-C_1' = (\kappa'\hat v_B)' + (a\mathcal B_1)'/k$.
    **Both are derived from published relations, never from differentiating a
    stored amplitude** --- finding T-23.
    """
    kp = np.asarray(kappa_prime, dtype=float)
    v_b = np.asarray(cset.v_b, dtype=float)
    a_b1_prime = np.asarray(cset.a_b1_prime, dtype=float)
    c1_thom = -(kp * v_b / float(k))
    c1_thom_prime = np.asarray(cset.c1_prime, dtype=float) + a_b1_prime / float(k)
    return c1_thom, c1_thom_prime


def _report() -> None:
    print(__doc__.split("THE TWO ACCEPTANCE")[0])
    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        table = BesselTable.build(
            int(ELLS.max()) + 2, max(KS) * float(env.background.eta_0) + 20.0,
            ells=np.unique(np.concatenate([[e - 1, e, e + 1] for e in ELLS])))
        print(f"\n{'='*86}\n  {label}\n{'='*86}")

        for k in KS:
            n_, c_ = coefficient_sets(float(k), env)
            diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
            common = dict(table=table, weight=env.weight, diffusion=diffusion,
                          damping_total=diffusion, eta_star=env.eta_star,
                          eta_floor=float(env.eta[0]), visibility=env.visibility,
                          eta_0=float(env.background.eta_0),
                          opacity=env.opacity)

            # the split, and the consistency check on it
            halves = {}
            for nm, cs in (("N", n_), ("C", c_)):
                ct, ctp = thomson_halves(cs, k, env.kappa_prime)
                halves[nm] = (cs, ct, ctp)
            # C_1^grav must equal -(a B_1)/k. This is a derivation, checked.
            cs, ct, _ = halves["N"]
            grav = np.asarray(cs.coefficients.c1, dtype=float) - ct
            want = -np.asarray(cs.a_b1, dtype=float) / float(k)
            sc = max(np.max(np.abs(grav)), np.max(np.abs(want)))
            resid = np.max(np.abs(grav - want)) / (sc if sc else 1.0)

            def run(cs, ct, ctp, **flags):
                return integral_solution(
                    ELLS, coefficients=cs.coefficients, c1_prime=cs.c1_prime,
                    c2_second=cs.c2_second, c2_prime_star=cs.c2_prime_star,
                    c2_prime=cs.c2_prime, c1_thomson=ct, c1_thomson_prime=ctp,
                    c1_thomson_kappa=env.kappa_prime,
                    **flags, **common).total

            base_n = run(*halves["N"])
            print(f"\n  k = {k:.0f}   (C_1 split check: |C_1^grav + aB_1/k| / scale "
                  f"= {resid:.2e})")
            print(f"  {'split':>5} {'jpri':>5} {'bndW':>5} {'+shr':>5} | "
                  + " ".join(f"{'gap l=' + str(e):>12}" for e in ELLS)
                  + f" | {'Newt moved':>11}")
            print("  " + "-" * 84)
            for combo in itertools.product((False, True), repeat=4):
                if combo[3] and not combo[0]:
                    continue   # the shear slot only exists once C_1 is split
                flags = dict(zip(CONTROLS, combo))
                a = run(*halves["N"], **flags)
                b = run(*halves["C"], **flags)
                sc_ = np.maximum(np.abs(a), np.abs(b))
                gap = np.abs(b - a) / np.where(sc_ > 0, sc_, 1.0)
                mv = np.max(np.abs(a - base_n)) / max(np.max(np.abs(base_n)), 1e-300)
                mark = "" if any(combo) else "  <- released"
                print(f"  {str(combo[0])[0]:>5} {str(combo[1])[0]:>5} "
                      f"{str(combo[2])[0]:>5} {str(combo[3])[0]:>5} | "
                      + " ".join(f"{g:12.4e}" for g in gap)
                      + f" | {mv:11.3e}{mark}")
    print(f"""
  READING THIS TABLE
  ------------------
  A cell passes only on BOTH conditions: the gap falls, AND 'Newt moved' is
  at or below the quadrature floor {FLOOR:.1e}. A cell that closes the gap
  while moving the Newtonian column has made two wrong columns agree.

  The 'released' row is all-False and reproduces the shipped code exactly.
  If any released number moved, that is a defect in this patch and not a
  result -- `tests/test_integral_solution.py` is the gate on it.
""")


def main() -> int:
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _report()
    text = buf.getvalue()
    print(text, end="")
    out = ROOT / "diagnostics" / f"{SLUG}-{VERSION}.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
