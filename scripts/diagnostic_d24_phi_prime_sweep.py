#!/usr/bin/env python3
r"""D24 --- P1-T's $\Phi'$ sweep. Is the driving channel DEAD, DROWNED, or merely UNFED?

Three states need three different repairs and nothing in the register tells
them apart. Every coefficient-level measurement we hold --- c3's 10--250%,
T-101's share $\simeq1$, T-117's $9.4\times10^3$ --- is **silent about the
spectrum** until something like this runs. This reports $\ell_{\rm peak}$,
which is a spectrum-level quantity, so **M16** is satisfied by construction.

WHAT IS SCALED, AND WHAT MUST NOT BE
------------------------------------
    (a B_1)'/k  =  (Phi_A' - Phi_H')   +   (k/3) tau_1
                   \__ scale this __/       \_ NOT this _/

`PHI_PRIME_DRIVING_LAMBDA` multiplies the first term inside
`newtonian_a_b1_prime`, and therefore inside $C_1'$ in **both** frames.
Scaling $C_1'$ whole, or $a\mathcal B_1$ whole, would conflate driving with
Doppler and the sweep would then measure nothing in particular --- **M15**'s
class, with the structure inside the coefficient rather than across the
bracket. That is the one way this instrument can be built wrong and still run
green, which is why L1--L3 below are gates and not commentary.

`KAPPA_SECOND_LAMBDA` multiplies $\kappa''\tilde v_B$ inside
$(\kappa'\tilde v_B)'$, for P1-T's \S5 confound: a flat
$\ell_{\rm peak}(\lambda)$ means *dead channel* only if it is also flat with
the 93--97% $\kappa''$ term suppressed. Flat in one run and not the other is a
**drowned** channel, which is a different repair.

L1--L4 ARE THE GATE ON BELIEVING ANY SWEEP POINT
-------------------------------------------------
    L1  C_1'(lambda) = A + lambda B exactly, A and B independent of lambda
    L2  lambda = 1 is BIT-IDENTICAL to the unscaled expression
    L3  lambda reaches C_0, C_2, C_2'', C_1 and both boundary terms NOT AT ALL
    L4  the peak finder recovers a known maximum of a synthetic C_l to < 0.5

**If L1 or L2 fails this script prints no sweep result.** P1-T will not read
one that arrives without them and is right not to: if $\lambda=1$ is not
bit-identical, the sweep is measuring the split rather than the physics.

READING THE RESULT
------------------
Reported as $\ell_{\rm peak}(\lambda)/\ell_A$ so the numbers land beside
**1.00** (undriven) and **0.772** (matched CAMB, $206/266.750$). $\ell_A$ is
carried in the output so a later reader cannot mistake the background. **Was
$0.757$ at $\ell_A=272.177$ until T-181** --- the recombination repair of
2026-10-21 moved the bundle's acoustic scale and the target moved with it;
the verdict did not, and the constant carries the reasoning.

  flat in BOTH kappa'' runs      the channel is DEAD. The defect is upstream
                                 of Phi'; A-3 cannot fix it however well
                                 implemented. Repair C_1' first.
  flat only at kappa''=1         the channel is DROWNED. S48 / the W-form is
                                 the repair and A-3 is downstream of it.
  moves, reaches 0.757           the channel WORKS and the input is missing.
                                 A-3 proper; plateau and peak are two defects.
  moves, never reaches 0.757     the channel is MIS-WEIGHTED. c3's 10-250%
                                 now has a spectrum-level consequence.

All four are informative, which is the test of whether an instrument is worth
building.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d24-phi-prime-sweep"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    PLANCK_H, PLANCK_MODEL, PLANCK_N_S, PLANCK_OMEGA_B_H2)
from functions.spectra import coefficients as _co  # noqa: E402
from functions.spectra.angular import cl_covariant_route  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.coefficients import newtonian_a_b1_prime  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, coefficient_sets, transfer_by_rank)

from _resumable import Checkpoint  # noqa: E402

#: Rows this instrument writes per configuration: one per frame.
#: Passed to `Checkpoint.has` so a run killed mid-write is recomputed rather
#: than resumed as complete --- finding **T-162**.
ROWS_PER_CONFIG = 2

#: Dense through the first peak so the parabolic interpolation has three real
#: samples bracketing it, sparse elsewhere. **argmax on the released grid
#: jitters by more than the effect being looked for** -- P1-T \S3.
ELLS = np.unique(np.concatenate([
    np.array([2, 4, 7, 11, 16, 22, 30, 45, 60, 80]),
    np.arange(100, 421, 5)]))

#: 600, not F9's 1500: this sweep needs the FIRST peak located, not the
#: damping tail resolved, and ell <= 420 needs k <~ 420/r_theta. Stated so a
#: reader does not mistake it for F9's grid.
K_MAX = 600.0

#: Matched CAMB's own ratio, 206/266.750. Carried explicitly -- P1-T \S3.
#:
#: **T-181: this was 272.177 and the number it came from was superseded on
#: 2026-10-21.** `f887301` set `RECOMBINATION_H = "corrected"` and PLANCK's
#: $\ell_A$ moved to 266.750 (D20's own `corrected` column, to four figures).
#: The literal stayed. It is the bundle's $\ell_A$ that 206 is divided by ---
#: CAMB supplies the 206 and nothing else here --- so when the bundle's
#: acoustic scale moved, the target moved with it and the file did not.
#:
#: **The verdict does not move and saying so is the point.** D27 measured
#: 0.0073 against a pre-registered [0.55, 0.80]; the target goes 0.757 ->
#: 0.772 and the failure is a factor of ~100 either side of it. This is
#: corrected because a stale number is a stale number, not because anything
#: turns on it.
#:
#: **Raised to P1-T as `P1B->P1T #22`, and it is theirs:** carrying $\ell_A$
#: explicitly is what makes the pre-registration mean something, and carrying
#: it explicitly is also what let it go stale. Whether a gate normalises by a
#: frozen scale or a live one is a pre-registration question. The value is
#: P1-B's; the rule is not.
ELL_A = 266.750
TARGET = 206.0 / ELL_A

FRAMES = ("newtonian", "cdm")


def _env():
    gamma = shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H)
    return build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2, transfer_gamma=gamma, hubble_h=PLANCK_H,
        f_2=F2_DEFAULT, line_of_sight_weight="printed")


def peak_position(ell: np.ndarray, d_ell: np.ndarray) -> tuple[float, float]:
    r"""The maximum of $D_\ell$ by parabolic interpolation on three samples.

    Returns (position, spacing-limited uncertainty). **Not `argmax`**: on this
    grid argmax can only ever return a grid point, and the grid spacing near
    the peak is 5, which is larger than differences the sweep is looking for.
    The uncertainty returned is half that local spacing, which is the honest
    floor on a three-point interpolation.
    """
    ell = np.asarray(ell, dtype=float)
    d = np.asarray(d_ell, dtype=float)
    i = int(np.argmax(d))
    if i == 0 or i == d.size - 1:
        return float(ell[i]), float("nan")
    x0, x1, x2 = ell[i - 1], ell[i], ell[i + 1]
    y0, y1, y2 = d[i - 1], d[i], d[i + 1]
    # Lagrange vertex, valid for UNEQUAL spacing, which this grid has at the
    # join between its sparse and dense halves.
    den = (x0 - x1) * (x0 - x2) * (x1 - x2)
    if den == 0.0:
        return float(x1), float("nan")
    a = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
    b = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0) + x0 * x0 * (y1 - y2)) / den
    if a == 0.0:
        return float(x1), float("nan")
    return float(-b / (2.0 * a)), float(0.5 * min(x1 - x0, x2 - x1))


def spectra_both_frames(env, table, k_com, power):
    """$D_\\ell$ in **both** frames, on the released path, in one pass over $k$.

    One pass, not two. `coefficient_sets` returns both frames from a single
    acoustic solve, so looping per frame solves the oscillator twice for
    nothing --- and this sweep already pays for four $\\lambda$ settings.
    """
    transfer = {f: np.zeros((ELLS.size, k_com.size)) for f in FRAMES}
    for j, k in enumerate(k_com):
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        for f in FRAMES:
            transfer[f][:, j] = transfer_by_rank(ELLS, float(k), sets[f],
                                                 env, table)[-1]
    out = {}
    for f in FRAMES:
        cl = np.array([cl_covariant_route(int(l), k_com, transfer[f][i], power)
                       for i, l in enumerate(ELLS)])
        out[f] = ELLS * (ELLS + 1.0) * cl / (2.0 * np.pi)
    return out


def kappa_second_share(env, k: float, frame: str) -> float:
    r"""$\kappa''\tilde v_B$'s share of $|C_1'|$ at the visibility peak.

    The confound's size, reported beside every sweep point --- P1-T \S5. Taken
    as a share of the coefficient the sweep moves, by the affine split: run
    the live path, run it with `KAPPA_SECOND_LAMBDA = 0`, difference.
    """
    keep = _co.KAPPA_SECOND_LAMBDA
    i = int(np.argmax(np.asarray(env.visibility, dtype=float)))
    try:
        _co.KAPPA_SECOND_LAMBDA = keep
        live = dict(zip(FRAMES, coefficient_sets(float(k), env)))[frame]
        _co.KAPPA_SECOND_LAMBDA = 0.0
        off = dict(zip(FRAMES, coefficient_sets(float(k), env)))[frame]
    finally:
        _co.KAPPA_SECOND_LAMBDA = keep
    a = float(np.asarray(live.c1_prime, dtype=float)[i])
    b = float(np.asarray(off.c1_prime, dtype=float)[i])
    return abs(a - b) / max(abs(a), 1e-300)


# ----------------------------------------------------------------------------
# L1 - L4
# ----------------------------------------------------------------------------
def controls(env) -> bool:
    print(f"\n{'='*78}\n  L1-L4 --- the gate on believing any sweep point\n{'='*78}")
    ok = True
    k = 60.0
    eta = np.asarray(env.eta, dtype=float)

    def at(lam):
        keep = _co.PHI_PRIME_DRIVING_LAMBDA
        try:
            _co.PHI_PRIME_DRIVING_LAMBDA = float(lam)
            return dict(zip(FRAMES, coefficient_sets(k, env)))
        finally:
            _co.PHI_PRIME_DRIVING_LAMBDA = keep

    s0, s1, s2, sh = at(0.0), at(1.0), at(2.0), at(0.5)

    # --- L1 : exact affinity ------------------------------------------------
    print("\n  L1  C_1'(lambda) = A + lambda B exactly       gate 1e-14")
    for frame in FRAMES:
        A = np.asarray(s0[frame].c1_prime, dtype=float)
        B = np.asarray(s1[frame].c1_prime, dtype=float) - A
        scale = float(np.max(np.abs(np.asarray(s1[frame].c1_prime, dtype=float))))
        worst = 0.0
        for lam, s in ((0.0, s0), (0.5, sh), (1.0, s1), (2.0, s2)):
            got = np.asarray(s[frame].c1_prime, dtype=float)
            worst = max(worst, float(np.max(np.abs(got - (A + lam * B)))) / scale)
        good = worst <= 1e-14
        ok &= good
        print(f"      {frame:<10} worst {worst:.2e}   "
              f"{'PASS' if good else '**FAIL**'}")

    # --- L2 : bit-identity at lambda = 1 ------------------------------------
    print("\n  L2  lambda=1 is BIT-IDENTICAL to the unscaled expression")
    keep = _co.PHI_PRIME_DRIVING_LAMBDA
    try:
        _co.PHI_PRIME_DRIVING_LAMBDA = 1.0
        scaled = newtonian_a_b1_prime(
            k, delta_t=env.phi_a * 0.0 + 1.0, phi_a=env.phi_a,
            phi_a_prime=env.phi_a_prime, phi_h_prime=env.phi_h_prime,
            tau_1=np.ones_like(eta), conformal_hubble=env.conformal_hubble)
        _co.PHI_PRIME_DRIVING_LAMBDA = 2.0
        doubled = newtonian_a_b1_prime(
            k, delta_t=env.phi_a * 0.0 + 1.0, phi_a=env.phi_a,
            phi_a_prime=env.phi_a_prime, phi_h_prime=env.phi_h_prime,
            tau_1=np.ones_like(eta), conformal_hubble=env.conformal_hubble)
    finally:
        _co.PHI_PRIME_DRIVING_LAMBDA = keep
    unscaled = (k * (np.asarray(env.phi_a_prime, dtype=float)
                     - np.asarray(env.phi_h_prime, dtype=float))
                + (k ** 2 / 3.0) * np.ones_like(eta))
    bit = bool(np.array_equal(scaled, unscaled))
    moved = not bool(np.array_equal(scaled, doubled))
    ok &= bit and moved
    print(f"      array_equal(lambda=1, unscaled) = {bit}      "
          f"{'PASS' if bit else '**FAIL**'}")
    print(f"      lambda=2 differs from lambda=1  = {moved}      "
          f"{'PASS' if moved else '**FAIL** (the handle is not connected)'}")

    # --- L3 : lambda reaches nothing else -----------------------------------
    print("\n  L3  lambda reaches C_0, C_1, C_2, C_2'', C_2'(eta_*) NOT AT ALL")
    for frame in FRAMES:
        a, b = s0[frame], s2[frame]
        checks = {
            "C_0": (a.coefficients.c0, b.coefficients.c0),
            "C_1": (a.coefficients.c1, b.coefficients.c1),
            "C_2": (a.coefficients.c2, b.coefficients.c2),
            "C_2''": (a.c2_second, b.c2_second),
            "C_2'(eta_*)": (np.array([a.c2_prime_star]),
                            np.array([b.c2_prime_star])),
        }
        bad = [n for n, (x, y) in checks.items()
               if not np.array_equal(np.asarray(x, dtype=float),
                                     np.asarray(y, dtype=float))]
        ok &= not bad
        print(f"      {frame:<10} {'all identical  PASS' if not bad else '**FAIL** ' + ', '.join(bad)}")
    print("      (so lambda moves the BULK only: the boundary [C_2'-C_1] is "
          "lambda-free)")

    # --- L4 : the peak finder ------------------------------------------------
    print("\n  L4  the peak finder, on a synthetic maximum        gate 0.5 in ell")
    truth = 213.7
    synth = np.exp(-((ELLS - truth) / 60.0) ** 2)
    got, unc = peak_position(ELLS, synth)
    good = abs(got - truth) < 0.5
    ok &= good
    print(f"      truth {truth}, recovered {got:.3f} (+-{unc:.1f} grid)   "
          f"err {abs(got-truth):.3f}   {'PASS' if good else '**FAIL**'}")

    print(f"\n  {'ALL CONTROLS PASS' if ok else '*** CONTROLS FAILED ***'}")
    return ok


def main() -> int:
    print(__doc__)
    env = _env()
    if not controls(env):
        print("\n  NO SWEEP RESULT IS PRINTED. L1/L2 are the condition on the "
              "sweep being\n  evidence at all, and they did not hold.")
        return 1

    r_theta = float(env.background.eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    lams = [float(x) for x in sys.argv[1:]] or [0.0, 1.0]
    print(f"\n{'='*78}\n  THE SWEEP --- PLANCK, ell_A = {ELL_A}, target "
          f"{TARGET:.3f} (= 206/{ELL_A})\n"
          f"  k to {K_MAX:.0f} in {k_com.size} modes, r_theta = {r_theta:.4f}"
          f"\n{'='*78}")
    print(f"\n  {'kappa2':>7} {'lambda':>7} {'frame':<10} "
          f"{'ell_peak':>10} {'+-':>5} {'/ell_A':>8} {'k2 share':>10}")
    print("  " + "-" * 62)
    # **Checkpointed, 2026-10-27.** D24 was the one long diagnostic in the
    # bundle that was not. Its first run reached three of four blocks and was
    # then killed by its own timeout, losing all three -- including the
    # 172.75 row the supplement's budget cites. Every block here costs a full
    # spectrum in both frames, so recomputing one that already succeeded is
    # the most expensive kind of nothing.
    rows = Checkpoint(ROOT / "diagnostics" / f"{SLUG}.csv",
                      ("kappa2", "lam", "frame", "ell_peak", "unc", "ratio",
                       "k2_share"))
    for r in rows.all():
        print(f"  {float(r['kappa2']):7.1f} {float(r['lam']):7.2f} "
              f"{r['frame']:<10} {float(r['ell_peak']):10.2f} "
              f"{float(r['unc']):5.1f} {float(r['ratio']):8.4f} "
              f"{float(r['k2_share']):10.3f}   [resumed]", flush=True)

    keep_p, keep_k = _co.PHI_PRIME_DRIVING_LAMBDA, _co.KAPPA_SECOND_LAMBDA
    try:
        for k2 in (1.0, 0.0):
            _co.KAPPA_SECOND_LAMBDA = k2
            for lam in lams:
                key = f"kappa2={k2:g} lambda={lam:g}"
                if rows.has(key, expect=ROWS_PER_CONFIG):
                    continue
                _co.PHI_PRIME_DRIVING_LAMBDA = lam
                d_both = spectra_both_frames(env, table, k_com, power)
                for frame in FRAMES:
                    pos, unc = peak_position(ELLS, d_both[frame])
                    _co.KAPPA_SECOND_LAMBDA = 1.0
                    share = kappa_second_share(env, 60.0, frame)
                    _co.KAPPA_SECOND_LAMBDA = k2
                    rows.add(key, kappa2=f"{k2:g}", lam=f"{lam:g}",
                             frame=frame, ell_peak=f"{pos:.6f}",
                             unc=f"{unc:.6f}", ratio=f"{pos/ELL_A:.6f}",
                             k2_share=f"{share:.6f}")
                    print(f"  {k2:7.1f} {lam:7.2f} {frame:<10} "
                          f"{pos:10.2f} {unc:5.1f} {pos/ELL_A:8.4f} "
                          f"{share:10.3f}", flush=True)
    finally:
        _co.PHI_PRIME_DRIVING_LAMBDA, _co.KAPPA_SECOND_LAMBDA = keep_p, keep_k

    print("""
  The two-point test (P1-T \\S4): if ell_peak(0) == ell_peak(1) at kappa2=1,
  the driving contributes NOTHING at the released setting, and A-3 is
  irrelevant until C_1' is repaired -- the channel it would feed is not
  connected to the output. The kappa2=0 block is what distinguishes a DEAD
  channel from a DROWNED one, and only both blocks together license either
  word.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
