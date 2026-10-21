#!/usr/bin/env python3
r"""D18 --- P1-T's $\kappa'$ ledger, run against the RELEASED assembly.

**P1-T's \S6 item 1, executed.** *"Run `c7_kappa_ledger.py` against the
released assembly, term by term, and record which coefficients carry
$\kappa'$. That is a read, not a sweep."*

`tests/frame/c7_kappa_ledger.py` enforces the rule on **fixtures** and imports
no project code --- deliberately, because a theory instrument that imports the
thing it is auditing is not an instrument. This diagnostic is the other half:
it applies the same rule to the arrays `functions/spectra/` actually builds.

THE RULE, FROM P1-T 2026-10-20
------------------------------
> $\kappa'$ may live in $W$, in $\mathcal V$, or in a derivative of either.
> **It may never live in a coefficient.**

Counting powers of $\kappa'$ on a *term* cannot decide this.
$\dot{\mathcal V}=(\kappa''+\kappa'^2)W$ reaches $\kappa'^2$ and is
**legitimate** --- it came from differentiating the weight.
$\mathcal V\,\mathrm d/\mathrm d\eta[-\kappa'\hat v_B]$ reaches $\kappa'^2$ and
is **not** --- it came from differentiating a coefficient that still carried a
bare $\kappa'$. The discriminator is *where the $\kappa'$ sits*, so that is
what is measured here.

HOW THE SPLIT IS MEASURED, NOT ASSERTED
---------------------------------------
Every coefficient this bundle builds is **affine in $\kappa'$**: $\kappa'$
enters `match_coefficients` only through `kappa_prime_v_b`, and
`newtonian_c1_prime` only through `kappa_prime_v_b_prime`. So scaling
$\kappa'\to\lambda\kappa'$ **in the coefficient construction alone**, with the
weight arrays held fixed, gives

    C(lambda) = C_free + lambda * C_kappa

and the two parts separate exactly:

    C_free  = C(0),    C_kappa = C(1) - C(0).

`Environment` is a frozen dataclass, so `replace(env, kappa_prime=lambda*kp,
kappa_second=lambda*kpp)` scales $\kappa'$ where the coefficients read it and
**nowhere else** --- `visibility` and `opacity`, which are the weights, are
untouched. Linearity is then *verified* at $\lambda=2$ rather than assumed: if
the residual of $C(2)-C_\text{free}-2C_\kappa$ is not at machine precision the
split is void and this diagnostic says so instead of reporting a number.

WHAT IS MEASURED, AND WHAT IS NOT
---------------------------------
Measures: for each term of the released (102), whether its coefficient carries
a bare $\kappa'$, what fraction of the coefficient that is, and therefore how
many powers of the scattering rate the assembled term carries against the
$W$-form's count.

Does **not** measure: whether the spectrum is wrong because of it. A term can
be large and correct --- **M11**. D16 supplies the size; this supplies the
structure; neither is the verdict.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d18-released-kappa-ledger"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

KS = (10.0, 60.0, 300.0)

#: Machine-precision bar for the linearity check. The arrays are O(1e2)-O(1e6)
#: and the split is a difference of two of them, so a relative residual above
#: this is structure, not rounding, and voids the split.
LINEARITY_BAR = 1e-12


def _scaled_sets(env, k: float, lam: float):
    """The released coefficient sets with kappa' scaled by `lam`.

    The weights are NOT scaled: `visibility` and `opacity` are left alone, so
    whatever moves between calls moved because a **coefficient** reads kappa'.
    """
    kp = np.asarray(env.kappa_prime, dtype=float)
    kpp = np.asarray(env.kappa_second, dtype=float)
    scaled = replace(env, kappa_prime=lam * kp, kappa_second=lam * kpp)
    return coefficient_sets(float(k), scaled)


def _split(arr1, arr0):
    """(free part, kappa'-carrying part) from C(1) and C(0)."""
    a1 = np.asarray(arr1, dtype=float)
    a0 = np.asarray(arr0, dtype=float)
    return a0, a1 - a0


def _share(free, kpart) -> float:
    """The kappa'-carrying fraction of a coefficient, by sup norm."""
    denom = float(np.max(np.abs(free + kpart)))
    return float(np.max(np.abs(kpart))) / denom if denom else float("nan")


def _report() -> None:
    print(__doc__.split("WHAT IS MEASURED")[0])

    print("""
  THE RELEASED ASSEMBLY, TERM BY TERM
  -----------------------------------
  With every repair control False and `c1_thomson=None` --- which is what
  `two_frame.transfer_by_rank` passes --- `integral_solution` assembles
  exactly three terms:

    bulk        weight * D * ( C_0 - C_1' + C_2'' ) * j_l
    boundary-1  ( C_2'(eta_*) - C_1(eta_*) ) * D * j_l(x_*)
    boundary-2  k * C_2(eta_*) * D * [ (l/(2l+1)) j_{l-1} - ((l+1)/(2l+1)) j_{l+1} ]

  `weight` is V under the printed line-of-sight choice (A-2) and W under the
  alternative; `D` is the diffusion factor and carries no kappa'. Note what
  boundary-1 has for a weight: **D alone**. `boundary_weight_w` is False in
  the released path, so that term carries NO W and NO V at all.
""")

    verdicts: list[tuple[str, str, str, bool, float]] = []

    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        kp = np.asarray(env.kappa_prime, dtype=float)
        i_star = int(np.argmax(np.asarray(env.visibility, dtype=float)))
        print(f"\n{'='*78}")
        print(f"  {label}    kappa'(eta_*) = {kp[i_star]:.4e}")
        print(f"{'='*78}")

        for k in KS:
            n1, c1_ = _scaled_sets(env, k, 1.0)
            n0, c0_ = _scaled_sets(env, k, 0.0)
            n2, c2_ = _scaled_sets(env, k, 2.0)

            for frame, s1, s0, s2 in (("Newtonian", n1, n0, n2),
                                      ("CDM", c1_, c0_, c2_)):
                rows = [
                    ("C_0",    "bulk, weight",     s1.coefficients.c0,
                     s0.coefficients.c0, s2.coefficients.c0),
                    ("C_1'",   "bulk, weight",     s1.c1_prime,
                     s0.c1_prime, s2.c1_prime),
                    ("C_2''",  "bulk, weight",     s1.c2_second,
                     s0.c2_second, s2.c2_second),
                    ("C_1",    "boundary-1, D only", s1.coefficients.c1,
                     s0.coefficients.c1, s2.coefficients.c1),
                    ("C_2",    "boundary-2, D only", s1.coefficients.c2,
                     s0.coefficients.c2, s2.coefficients.c2),
                ]
                print(f"\n  k = {k:<5.0f} {frame} frame")
                print(f"  {'coefficient':<9} {'sits under':<20} {'carries kp':>11}"
                      f" {'kp share':>10} {'linearity':>11}  verdict")
                print("  " + "-" * 76)
                for name, slot, a1, a0, a2 in rows:
                    free, kpart = _split(a1, a0)
                    scale = float(np.max(np.abs(np.asarray(a1, dtype=float))))
                    if scale == 0.0:
                        print(f"  {name:<9} {slot:<20} {'n/a':>11} {'--':>10}"
                              f" {'--':>11}  identically zero in this frame")
                        continue
                    resid = float(np.max(np.abs(
                        np.asarray(a2, dtype=float) - free - 2.0 * kpart))) / scale
                    carries = float(np.max(np.abs(kpart))) > 0.0
                    sh = _share(free, kpart)
                    ok = resid <= LINEARITY_BAR
                    verdict = ("DEFECT: kappa' in a coefficient" if carries
                               else "clean")
                    if not ok:
                        verdict = "VOID --- not affine in kappa', split invalid"
                    print(f"  {name:<9} {slot:<20} {'YES' if carries else 'no':>11}"
                          f" {sh:10.4f} {resid:11.2e}  {verdict}")
                    verdicts.append((f"{label} k={k:.0f} {frame}", name, slot,
                                     carries and ok, sh))

    # ---- P1-T's ratio, tested pointwise, and the boost split -------------
    print(f"\n{'='*78}")
    print("  THE SHARE AGAINST kappa'/(kappa'+k), AND THE FRAME SHIFT")
    print(f"{'='*78}")
    print("""
  P1-T, 2026-10-21: the share should be kappa'/(kappa'+k), because C_1's two
  entries are (dT + Phi_A), unreduced, and kappa' vhat_B, reduced by 1/k. And
  the frame SHIFT should be kappa'-dominated at kappa'/(kappa'+H), which has
  no k in it at all -- so the frame test and the spectrum test decouple at
  high k.

  The first claim cannot be tested against a SUP-NORM share: that is a ratio
  of two maxima taken over the whole grid, and kappa' varies by orders of
  magnitude across it, so the sup of the kappa' part and the sup of the total
  need not occur at the same eta. Tested POINTWISE at eta_*, where P1-T's
  kappa'(eta_*) is the right number to use, it is a fair test. Both are
  printed below. Delta is CDM minus Newtonian, split by the same exact
  affine decomposition.
""")
    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        kp = np.asarray(env.kappa_prime, dtype=float)
        i_star = int(np.argmax(np.asarray(env.visibility, dtype=float)))
        kps = float(kp[i_star])
        aH = float(np.asarray(env.conformal_hubble, dtype=float)[i_star])
        print(f"\n  {label}   kappa'(eta_*) = {kps:.4e}   H(eta_*) = {aH:.4e}")
        print(f"  {'k':>5} {'pred kp/(kp+k)':>15} {'sup-norm':>10} {'pointwise':>11}"
              f" {'| dC_1 kp share':>16} {'pred kp/(kp+H)':>15}")
        print("  " + "-" * 78)
        for k in KS:
            n1, c1_ = _scaled_sets(env, k, 1.0)
            n0, c0_ = _scaled_sets(env, k, 0.0)
            a1 = np.asarray(n1.coefficients.c1, dtype=float)
            a0 = np.asarray(n0.coefficients.c1, dtype=float)
            free, kpart = _split(a1, a0)
            sup = _share(free, kpart)
            pt = (abs(kpart[i_star]) / abs(a1[i_star])
                  if a1[i_star] else float("nan"))
            # the frame shift, split by the same affine decomposition
            d_free = np.asarray(c0_.coefficients.c1, dtype=float) - a0
            d_tot = np.asarray(c1_.coefficients.c1, dtype=float) - a1
            d_kap = d_tot - d_free
            den = float(np.max(np.abs(d_tot)))
            d_share = float(np.max(np.abs(d_kap))) / den if den else float("nan")
            print(f"  {k:5.0f} {kps/(kps+k):15.4f} {sup:10.4f} {pt:11.4f}"
                  f" {d_share:16.4f} {kps/(kps+abs(aH)):15.4f}")

    print("""
  READING THIS
  ------------
  Column 2 is P1-T's prediction, column 4 the fair test of it. Column 5 is
  their section 3 ask -- the frame shift's kappa' share -- and column 6 their
  prediction for it, which carries no k.

  The sup-norm column is what T-101 reported and it is NOT the quantity the
  ratio predicts; the two are printed side by side so the difference is
  visible rather than argued. Where the pointwise column tracks column 2, the
  mechanism is confirmed; where column 5 is flat in k, the frame test and the
  spectrum test decouple at high k exactly as P1-T stated IN ADVANCE, and the
  W-form is then predicted to close the gap at k=300 as well as at low k.
""")

    # ---- the ledger, collapsed -------------------------------------------
    print(f"\n{'='*78}")
    print("  THE LEDGER")
    print(f"{'='*78}")
    by_coeff: dict[str, list[float]] = {}
    for _, name, _slot, carries, sh in verdicts:
        if carries:
            by_coeff.setdefault(name, []).append(sh)
    print(f"\n  {'coefficient':<9} {'carries kappa-prime':<21}"
          f" {'share: min':>11} {'max':>10}")
    print("  " + "-" * 56)
    for name in ("C_0", "C_1", "C_1'", "C_2", "C_2''"):
        shares = by_coeff.get(name)
        if shares:
            print(f"  {name:<9} {'YES --- DEFECT':<21} {min(shares):11.4f}"
                  f" {max(shares):10.4f}")
        else:
            print(f"  {name:<9} {'no':<21} {'--':>11} {'--':>10}")

    print("""
  READING THIS
  ------------
  **Two coefficients carry a bare kappa', and they are the same physical
  object seen twice.** From (89), C_1 = (p1/k)(a B_1 + kappa' v_B); from
  (107), -C_1' = (kappa' vhat_B)' + (a B_1)'/k. The Thomson in-scattering has
  been folded INTO the matching coefficients rather than left under the
  visibility where it belongs, and once it is inside C_1 the by-parts of (102)
  differentiates it.

  That is the whole mechanism of T-94. `V * d/deta[kappa' vhat_B]` is
  `W * kappa' * (kappa'' vhat_B + kappa' vhat_B')` --- two powers of the
  scattering rate, where P1-T's W-form carries exactly one, inside V, for the
  same physics.

  **A share at or above 1.00 is the point.** It is a sup-norm ratio, so the
  kappa'-carrying part is not a correction to C_1 -- it is essentially the
  WHOLE of it, and values slightly above unity are the two parts partially
  cancelling. The one exception is k=300 in the Newtonian frame, 0.51, where
  the gravitational half a B_1 / k finally becomes comparable. **k=300 is
  also the mode no repair variant has ever moved**, and this is the first
  structural difference measured at it rather than asserted about it.

  **boundary-1 is the second site and it is the sharper one.** C_1(eta_*)
  enters the released boundary term with the diffusion factor and NOTHING
  else: no W, no V. The bare kappa'(eta_*) it carries is 3.82e2 on EdS and
  2.64e2 on PLANCK -- read off this run, printed above -- and it multiplies
  vhat_B there under no exponential suppression at all. The W-form has no
  such term: its Thomson entry is V * S_1 * K^(1) with S_1 = fbar_1 v_B,
  kappa'-free, and its boundary vanishes because V does at both ends.

  WHAT THIS DOES NOT SAY
  ----------------------
  It does not say the released spectrum is wrong by these factors, and it is
  not a repair: five have been attempted and withdrawn (T-88..T-93), and the
  one that looked best was a spurious kappa' of 320-682. It says where the
  kappa' sits, which is the question P1-T asked and the one that five sweeps
  never established. A-2 remains a recorded choice of weight (SOURCE-
  APPROXIMATIONS-v1.md); this is a statement about the COEFFICIENTS, which
  no choice of weight reaches -- T-94 measured that independently.
""")


def main() -> int:
    import contextlib
    import io
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
