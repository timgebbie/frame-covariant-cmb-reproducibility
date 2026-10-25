#!/usr/bin/env python3
r"""D32 --- P1-T's one-run discriminator for B-17 (i). Does the late ISW come back?

**Specified by P1-T 2026-10-25T05:48Z, pre-registered here before it runs.**

T-128 measured that the late share is `0.0000` on all three backgrounds, where
$\Lambda$CDM and `PLANCK_MODEL` require $\mathcal O(0.1)$ and Einstein--de
Sitter requires exactly zero. That is *consistent with* discrepancy (i) --- the
bulk bracket riding at $\mathcal V\mathcal D$ where the exact by-parts wants
$W$ --- and consistent with is not established.

**This is the discriminator, and it is cheap because the instrument exists.**
The identity puts the bracket at $W$ and the partner terms
$-\mathcal VC_1+2\mathcal VC_2'+\dot{\mathcal V}C_2$ at $\mathcal V$ and
$\dot{\mathcal V}$. $W\to1$ late; the partners close at $\eta_*$. **So the
identity predicts the late ISW rides entirely on the $W$-weighted bracket.**
Move the gravitational content of $C_1'$ to $W$ and it must come back.

PRE-REGISTERED, before this runs
--------------------------------
    Column A, `slot_weight_split` alone --- P1-T's specification. The
    gravitational half of $C_1'$, which carries $(\Phi_A'-\Phi_H')$, moves to
    $W$; the Thomson half stays at $\mathcal V$.

      LambdaCDM and PLANCK, late share at ell = 2   NON-ZERO, order 0.1
      Einstein-de Sitter                            still EXACTLY 0.0000

    Column B, `bracket_all_at_w` --- discrepancy (i) at full strength, the
    whole bracket at W. **Added by P1-B and not in P1-T's specification.**
    Reason: A is the minimal intervention and B is the claim. If A returns the
    ISW and B does not, the attribution is to the split rather than to (i),
    and one column cannot tell those apart. Same prediction, larger.

    Column C, the identity --- the bracket at W WITH the partner terms at
    V and Vdot. **Added after A and B failed the EdS null control**, and
    pre-registered here before it runs. P1-T's T-133 specifies it: neither
    "all W" nor "all V" is the by-parts identity, so a column carrying only
    half of it is not a test of (i). A and B are now read as evidence that
    the partners are load-bearing, which is what T-133 said.

      Einstein-de Sitter, late share at ell = 2     EXACTLY 0.0000 again
      LambdaCDM and PLANCK                          NON-ZERO, order 0.1
      ell = 10 lifted LESS than ell = 2             on the Lambda backgrounds

    If EdS is non-zero here too, the partners are not what A and B were
    missing and the whole family is measuring something other than (i).

    OUTCOMES, fixed now:
      Lambda non-zero, EdS zero        (i) IS the mechanism. T-128 promoted
                                       from consistent-with to established.
      all three stay zero              (i) is NOT the mechanism. P1-T is
                                       wrong and the annihilation is
                                       something the weight does not reach.
      EdS goes non-zero                the control has failed and NEITHER
                                       column is evidence --- EdS has no late
                                       ISW to recover, so a non-zero there is
                                       the instrument, not the physics.
      Lambda non-zero but << 0.1       (i) is A mechanism and not the whole
                                       of it; a second term is also being
                                       annihilated.

**What it cannot establish, stated before the numbers exist.** That the
restored share is the *correct* late ISW. `reference/` carries $C_\ell$ only,
so there is no external late-ISW amplitude to score against; the test is
presence against exact zero, with EdS as the null. A column that returns
$\mathcal O(0.1)$ has shown the term is no longer annihilated and has not
shown it is right.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d32-isw-discriminator"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, LCDM_MODEL, PLANCK_H, PLANCK_MODEL, PLANCK_N_S,
    PLANCK_OMEGA_B_H2)
from functions.spectra import coefficients as _co  # noqa: E402
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

#: The quadrupole is where the late ISW lives and ell=10 is the control that
#: it does NOT live there. Two multipoles, because this is a discriminator and
#: not a survey, and every extra one is a full quadrature.
ELLS = np.array([2, 10])

#: 120 reaches ell=10 on every background with room. The late ISW is a
#: superhorizon-scale effect and nothing above the first acoustic peak is
#: being asked about.
K_MAX = 120.0

#: The slice grid only has to resolve "after the visibility has closed", so
#: twelve is enough; D30 runs 24 and F10 16, and all three agree that the
#: curves are a step followed by a flat.
N_SLICES = 12

FRAMES = ("newtonian", "cdm")

BACKGROUNDS = [
    ("EdS   (CDM_MODEL)", CDM_MODEL, 0.0224, 0.5, 0.48),
    ("LCDM", LCDM_MODEL, 0.0224, 0.5, 0.48),
    ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H, None),
]

#: The control lattice. The released row is run every time and is NOT a
#: formality: it is what says the instrument reproduces T-128 before any
#: column is read as moving away from it.
CONFIGS: list[tuple[str, dict]] = [
    ("released  (the T-128 baseline)", {}),
    ("A  slot_weight_split  --- P1-T's specification",
     dict(slot_weight_split=True)),
    ("B  bracket_all_at_w  --- (i) at full strength",
     dict(bracket_all_at_w=True)),
    # **Column C, added 2026-10-25 after A and B both failed the EdS null.**
    # P1-T's T-133 said this before either was run: the exact by-parts puts
    # the bracket at W AND the partner terms
    # -V C_1 + 2V C_2' + Vdot C_2 at V, so "all W" is not the identity any
    # more than "all V" is, and a B-slot column needs both in the same run.
    # A and B each move the bracket and leave the partners out, which is why
    # both put late power on a background that has no late ISW to have: with
    # the partners absent there is nothing left carrying the visibility.
    # This is D29's pre-registered first configuration, scored here on the
    # late share instead of on the peak.
    ("C  the identity --- bracket at W WITH its partners",
     dict(bracket_all_at_w=True, by_parts_weight_terms=True,
          boundary_weight_w=True)),
    # **Column D, added after C failed the EdS null at 0.9978.** C is the
    # identity and it is drowned: C_0 and C_2 grow by 33x to the present on
    # EdS (T-143) and W falls only to 0.368, so the late share measures the
    # growing mode and not the ISW. D is C with the driving switched OFF.
    # `PHI_PRIME_DRIVING_LAMBDA` scales (Phi_A' - Phi_H') and NOTHING else,
    # so D - C is the ISW channel with the growing-mode contamination
    # subtracted -- it is common to both and cancels.
    #
    # **And on EdS that difference is zero BY CONSTRUCTION**, because the knob
    # multiplies a term identically zero where Phi is constant. The null
    # control stops being a numerical coincidence and becomes structural,
    # which is what it should have been from the start.
    ("D  the identity with the driving OFF  (lambda = 0)",
     dict(bracket_all_at_w=True, by_parts_weight_terms=True,
          boundary_weight_w=True), 0.0),
    # **Column E, the hypothesis T-144 ends on.** C_0 and C_2 grow 33x to the
    # present and W falls only to 0.368, so the whole bracket at W is drowned
    # (T-143); the (Phi_A' - Phi_H') content of the SAME bracket behaves
    # correctly at W (T-144). So: **only the driving travels at W**, and
    # C_0, C_2'' and the rest of C_1' stay at V where the visibility holds
    # them at recombination. That is the standard line-of-sight integrand's
    # own shape, and this asks whether the by-parts identity agrees.
    #
    #   PRE-REGISTERED, before it runs:
    #     EdS, late share at l=2     EXACTLY 0 -- no driving to carry
    #     LambdaCDM and PLANCK       NON-ZERO, and LARGER than T-144's 1-2e-02
    #     l=2 lifted MORE than l=10  the late ISW is superhorizon
    #     the EARLY share            unchanged from released: the spectrum
    #                                must still be laid down at recombination,
    #                                which is what columns B and C destroyed
    #
    #   If the late share arrives but the spectrum stops being localised, the
    #   split is not along the driving either, and the growing mode belongs
    #   at W for a reason this project does not yet have.
    ("E  ONLY the driving at W, the rest at V",
     dict(isw_only_at_w=True), 1.0),
]

#: "After the visibility has closed" --- the first 1% of conformal time past
#: eta_*, matching D30 exactly so the numbers are comparable line by line.
LATE_FROM = 0.01


def _late_share(label, bg, obh2, h, gamma) -> tuple[dict, float]:
    """Fraction of the final C_ell deposited after LATE_FROM, per frame."""
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
        if _tf.BULK_SOURCE_CONTROLS.get("isw_only_at_w"):
            _co.PHI_PRIME_DRIVING_LAMBDA = 0.0
            off = dict(zip(FRAMES, coefficient_sets(float(k), env)))
            _co.PHI_PRIME_DRIVING_LAMBDA = 1.0
        else:
            off = {}
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        common = dict(table=table, weight=env.weight, diffusion=diffusion,
                      damping_total=diffusion, eta_star=eta_star,
                      eta_floor=float(env.eta[0]), visibility=env.visibility,
                      eta_0=eta_0)
        for f in FRAMES:
            s = sets[f]
            # **T-131.** The controls raise without these four arrays, and
            # `BULK_SOURCE_CONTROLS` alone reaches `integral_solution` only
            # through `transfer_by_rank`, which this instrument does not use.
            # Passing the dict without the primitives is how the first run of
            # this file measured the released configuration three times.
            extra = dict(_tf.BULK_SOURCE_CONTROLS)
            if extra:
                extra.update(bulk_source_primitives(float(k), env, s))
            if extra.get("isw_only_at_w"):
                # (Phi_A' - Phi_H') = [ (aB_1)'(lambda=1) - (aB_1)'(0) ] / k,
                # exactly, because the knob multiplies that term and nothing
                # else. Taken by differencing the live builder rather than
                # re-derived here: a second derivation in a diagnostic is the
                # drift S8 forbids, and `c1_prime_isw` has never had a
                # supplier, so `w_half_is_isw_only` has been moving zero.
                extra["c1_prime_isw"] = (
                    np.asarray(s.a_b1_prime, dtype=float)
                    - np.asarray(off[f].a_b1_prime, dtype=float)) / float(k)
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
        for i, l in enumerate(ELLS):
            row, fin = acc[f][i], acc[f][i][-1]
            out[(f, int(l))] = (
                float("nan") if fin <= 0
                else 1.0 - float(np.interp(LATE_FROM, x, row / fin)))
    return out, gate


def main() -> int:
    print(__doc__)
    rows = Checkpoint(ROOT / "diagnostics" / f"{SLUG}.csv",
                      ("background", "frame", "ell", "late_share", "gate"))
    keep = dict(_tf.BULK_SOURCE_CONTROLS)
    seen: dict[str, dict] = {}
    try:
        for row in CONFIGS:
            label, cfg = row[0], row[1]
            lam = row[2] if len(row) > 2 else 1.0
            for bl, bg, obh2, h, gamma in BACKGROUNDS:
                key = f"{label} || {bl}"
                if rows.has(key):
                    print(f"  [resumed] {key}", flush=True)
                    for r in rows.all():
                        if r["configuration"] == key:
                            seen.setdefault(label, {})[
                                (r["background"], r["frame"], int(r["ell"]))
                            ] = float(r["late_share"])
                    continue
                _tf.BULK_SOURCE_CONTROLS = dict(cfg)
                _co.PHI_PRIME_DRIVING_LAMBDA = float(lam)
                try:
                    got, gate = _late_share(bl, bg, obh2, h, gamma)
                except Exception as exc:                       # noqa: BLE001
                    print(f"  {key}: RAISED {type(exc).__name__}: {exc}",
                          flush=True)
                    continue
                for (f, l), share in got.items():
                    rows.add(key, background=bl, frame=f, ell=l,
                             late_share=f"{share:.6f}", gate=f"{gate:.3e}")
                    seen.setdefault(label, {})[(bl, f, l)] = share
                print(f"  {key}:  gate {gate:.2e}  " + "  ".join(
                    f"{f}/l={l} {s:+.4f}" for (f, l), s in sorted(got.items())),
                    flush=True)
    finally:
        _tf.BULK_SOURCE_CONTROLS = keep
        _co.PHI_PRIME_DRIVING_LAMBDA = 1.0

    print(f"\n{'='*94}\n  LATE SHARE at ell=2 --- the fraction of C_2 deposited "
          f"AFTER the first {LATE_FROM:.0%} of\n  conformal time past eta_*, "
          f"which is after the visibility has closed.\n{'='*94}")
    print(f"  {'configuration':<44} {'background':<20} "
          f"{'newtonian':>11} {'cdm':>11}")
    print("  " + "-" * 90)
    for label, *_ in CONFIGS:
        got = seen.get(label, {})
        for bl, *_ in BACKGROUNDS:
            n = got.get((bl, "newtonian", 2), float("nan"))
            c = got.get((bl, "cdm", 2), float("nan"))
            print(f"  {label if bl == BACKGROUNDS[0][0] else '':<44} "
                  f"{bl:<20} {n:11.4f} {c:11.4f}")
        print("  " + "-" * 90)

    print("""
  READING THIS AGAINST THE PRE-REGISTRATION AS WRITTEN
  ----------------------------------------------------
  Lambda non-zero, EdS zero     (i) IS the mechanism; T-128 is established.
  all three stay zero           (i) is NOT the mechanism.
  EdS goes non-zero             the control has failed; NEITHER column is
                                evidence, because EdS has no late ISW to
                                recover and a non-zero there is the
                                instrument rather than the physics.
  Lambda non-zero but << 0.1    (i) is A mechanism and not the whole of it.

  The ell=10 rows are the second control: the late ISW is a superhorizon
  effect, so a column that lifts ell=10 as much as ell=2 has not restored the
  late ISW, it has changed the normalisation.
""")

    c = seen.get("C  the identity --- bracket at W WITH its partners", {})
    d = seen.get("D  the identity with the driving OFF  (lambda = 0)", {})
    if c and d:
        print(f"\n{'='*94}\n  THE ISW CHANNEL ALONE:  (lambda=1) - (lambda=0), "
              f"with the growing mode subtracted.\n  EdS MUST be 0 by "
              f"construction -- the knob scales a term that is identically "
              f"zero there.\n{'='*94}")
        print(f"  {'background':<20} {'frame':<11} {'l=2':>12} {'l=10':>12}")
        print("  " + "-" * 60)
        eds = None
        for bl, *_ in BACKGROUNDS:
            for f in FRAMES:
                vals = [c.get((bl, f, l), float("nan"))
                        - d.get((bl, f, l), float("nan")) for l in (2, 10)]
                if bl.startswith("EdS") and f == "cdm":
                    eds = vals[0]
                print(f"  {bl:<20} {f:<11} {vals[0]:12.6f} {vals[1]:12.6f}")
        print("  " + "-" * 60)
        if eds is not None:
            ok = abs(eds) < 1e-6
            print(f"\n  STRUCTURAL NULL  EdS, CDM frame, l=2: {eds:+.3e}  "
                  f"{'PASS' if ok else '**FAIL**'}")
            if not ok:
                print("  The knob moved a background where the term it scales "
                      "is identically zero.\n  Nothing above is evidence: the "
                      "knob is not isolating what it claims to.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
