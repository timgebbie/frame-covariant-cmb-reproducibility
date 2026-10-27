#!/usr/bin/env python3
r"""D38 --- is the Einstein--de Sitter residue in $C_1$'s scattering half or its
gravitational half?

**P1-T's ask of 2026-10-27 13:26 SAST, `P1T->P1B #7`, pre-registered here
before it runs.**

THE HYPOTHESIS, AND IT IS THEIRS
--------------------------------
**T-155** measured two properties of the residue and could not explain either:

  * $\Delta S$ is **92.4% confined to the visibility** --- it lives where
    recombination is, not after it;
  * $\Lambda$CDM tracks Einstein--de~Sitter to $4\times10^{-4}$ in every row
    of D35 --- it is **background-independent**.

P1-T's reading is that both point at the **scattering** half rather than the
gravitational one, and the argument is one line: $\kappa'$ is set by
recombination and not by the background, so a defect carried in
$C_1^{\rm scatt}$ is background-independent *by construction* and lives
exactly where the visibility is. The gravitational half carries
$(\Phi_A'-\Phi_H')$, which is identically zero on Einstein--de~Sitter and
cannot be background-independent.

**That is a mechanism which predicts both measured properties in advance**,
which is more than anything P1-B has offered for them.

WHAT IS RUN
-----------
$\Delta S(\eta)=S_{\rm split}(\eta)-S_{\rm released}(\eta)$, on one
background, in three configurations:

    untouched          both halves of C_1 present
    C_1^scatt zeroed   the Thomson half blanked; C_1 is purely gravitational
    C_1^grav  zeroed   the whole of C_1' handed to the Thomson slot, so the
                       bracket's -C_1' + C_1^thom' cancels exactly

**Suppression is by blanking the array the bracket reads**, never by a second
code path --- D35's rule, and the reason its numbers are comparable with
these.

Scored on **two** quantities, because T-155's finding was that one of them
alone misleads:

    late share    1 - S(eta_* + 1% span)/S(eta_0).  A RATIO, and T-155
                  recorded that the repair collapses its denominator.
    |Delta S| inside the visibility, as a fraction of its total --- the
                  ABSOLUTE statement, and the one P1-T's #7 is about.

PRE-REGISTERED --- the outcomes, fixed now
------------------------------------------
    scattering half zeroed removes the residue
        The defect is the (90) bundling again. `c6` and `c9` already name the
        remedy and nothing new is needed from P1-B.

    gravitational half zeroed removes it
        P1-T's mechanism is wrong -- the gravitational half cannot be
        background-independent, since it vanishes identically on
        Einstein-de Sitter -- and the agreement across backgrounds would then
        need a separate explanation.

    NEITHER removes it
        Both halves are exonerated and the residue is in the kernel or the
        quadrature. That is a different search and P1-T says so.

    BOTH appear to remove it
        The measurement is not discriminating: zeroing either half leaves a
        bracket that is not the one under test. Read the absolute column, not
        the ratio.

WHAT IT CANNOT ESTABLISH
------------------------
That the split by-parts is right. Every configuration here is the split with
one input blanked; the comparison is between them and not against CAMB.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d38-which-half-carries-the-residue"

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
N_SLICES = 24
LATE_FROM = 0.01

#: (label, which half to blank)
HALVES = [
    ("untouched", None),
    ("C_1^scatt zeroed", "scatt"),
    ("C_1^grav zeroed", "grav"),
]

BACKGROUNDS = [("EdS", CDM_MODEL), ("LCDM", LCDM_MODEL)]


def _accumulate(bg, zero, split):
    env = build_environment(
        K_MAX, omega_m=bg.omega_m, omega_lambda=bg.omega_lambda,
        omega_r=bg.omega_r, omega_b_h2=0.0224, transfer_gamma=0.48,
        hubble_h=0.5, f_2=F2_DEFAULT, line_of_sight_weight="printed")
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
        s = coefficient_sets(float(k), env)[1]                 # CDM frame
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        # **The half is blanked in BOTH arms, not only the split one.**
        # $\Delta S=S_{\rm split}-S_{\rm released}$ is the object; a half
        # removed from the split arm alone would make $\Delta S$ a mixture of
        # *the half* and *the repair*, and the measurement could not say which
        # it had responded to. Removing it from both asks the question P1-T
        # asked: what is the split-against-released difference **in a world
        # where that half does not exist**.
        prim = bulk_source_primitives(float(k), env, s)
        thom_p = np.asarray(prim["c1_thomson_prime"], dtype=float)
        c1p = np.asarray(s.c1_prime, dtype=float)
        if zero == "scatt":
            c1p = c1p - thom_p
        elif zero == "grav":
            c1p = thom_p.copy()

        extra: dict = {}
        if split:
            extra = dict(split_by_parts=True, by_parts_weight_terms=True)
            extra.update(prim)
            if zero == "scatt":
                # **Removed, not relocated --- and the first version of this
                # branch relocated it.** It blanked `c1_thomson` and
                # `c1_thomson_prime` and left `c1_prime` whole. But
                # `bracket_w = (C_0 - C_1' + C_2'' + partners) + C_1^thom'`,
                # so zeroing `C_1^thom'` does not remove the scattering
                # content from the bracket --- it puts it BACK, as part of
                # the undifferentiated $-C_1'$, which is where (102) had it.
                # Together with the Doppler leaving $K'$, the two changes
                # very nearly cancelled: the transfer moved by $2.9\times
                # 10^{-4}$, against $1.3\times10^{-1}$ for the other half.
                #
                # That near-cancellation reads as *"the scattering half
                # carries nothing"* and would have refuted P1-T's #7 on an
                # artefact of the suppression. **M15**: a true number about
                # the wrong object. It was caught because two configurations
                # printed identical numbers to five significant figures,
                # which is the one signature a mis-specified control leaves.
                #
                # To remove the content, the scattering derivative must come
                # out of `c1_prime` as well, leaving the bracket carrying the
                # gravitational derivative alone and nothing at $K'$.
                extra["c1_thomson"] = np.zeros_like(
                    np.asarray(extra["c1_thomson"], dtype=float))
                extra["c1_thomson_prime"] = np.zeros_like(thom_p)
            elif zero == "grav":
                # `c1p` is already the Thomson derivative alone, so the
                # bracket's $-C_1' + C_1^{\rm thom}{}'$ cancels exactly: no
                # gravitational content remains and the scattering half still
                # rides undifferentiated at $K'$.
                extra["c1_thomson_prime"] = thom_p.copy()
        res = integral_solution(
            ELLS, coefficients=s.coefficients, c1_prime=c1p,
            c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
            c2_prime=s.c2_prime, eta_slices=sl, table=table,
            weight=env.weight, diffusion=diffusion, damping_total=diffusion,
            eta_star=eta_star, eta_floor=float(env.eta[0]),
            visibility=env.visibility, eta_0=eta_0, **extra)
        boundary = (res.boundary_scalar + res.boundary_shear)[:, None]
        acc += (k ** 2 * power[j]) * (res.partial_bulk + boundary) ** 2 * dk
    return acc, (sl - eta_star) / span, env, sl


def _score(bg, zero):
    """`late share` and the absolute support of Delta S inside the visibility."""
    a_split, x, env, sl = _accumulate(bg, zero, True)
    a_rel, _, _, _ = _accumulate(bg, zero, False)

    out = {}
    for i, l in enumerate(ELLS):
        tot = a_split[i, -1]
        out[f"late/{int(l)}"] = (
            1.0 - float(np.interp(LATE_FROM, x, a_split[i] / tot))
            if tot > 0 else float("nan"))

    # **The absolute statement, and it is the one #7 is about.** |Delta S|
    # accumulated inside the visibility against |Delta S| over the whole span.
    # A ratio whose denominator a repair can collapse is what made T-155's
    # first reading wrong; this denominator is the total movement itself.
    vis_end = float(np.interp(LATE_FROM, x, sl))
    inside = sl <= vis_end
    for i, l in enumerate(ELLS):
        d = np.abs(a_split[i] - a_rel[i])
        tot = float(d[-1])
        out[f"vis_share/{int(l)}"] = (
            float(np.max(d[inside])) / tot if tot > 0 else float("nan"))
        out[f"absdelta/{int(l)}"] = tot
    return out


def main() -> int:
    print(__doc__)
    rows = Checkpoint(ROOT / "diagnostics" / f"{SLUG}.csv",
                      ("background", "metric", "value"))
    seen: dict = {}
    for label, zero in HALVES:
        for bl, bg in BACKGROUNDS:
            key = f"{label} || {bl}"
            if rows.has(key):
                for r in rows.all():
                    if r["configuration"] == key:
                        seen[(label, bl, r["metric"])] = float(r["value"])
                print(f"  [resumed] {key}", flush=True)
                continue
            try:
                got = _score(bg, zero)
            except Exception as exc:                          # noqa: BLE001
                print(f"  {key}: RAISED {type(exc).__name__}: {exc}", flush=True)
                continue
            for m, v in got.items():
                rows.add(key, background=bl, metric=m, value=f"{v:.6e}")
                seen[(label, bl, m)] = v
            print(f"  {key:<30} late(l=2) {got['late/2']:+.4f}   "
                  f"|dS| inside visibility {got['vis_share/2']*100:6.2f}%   "
                  f"|dS| total {got['absdelta/2']:.4e}", flush=True)

    print(f"\n{'='*86}\n  AGAINST P1T->P1B #7, read as written\n{'='*86}")
    for m, name in (("vis_share/2", "|Delta S| inside the visibility, share"),
                    ("absdelta/2", "|Delta S| total, absolute"),
                    ("late/2", "late share (the RATIO -- T-155's trap)")):
        print(f"\n  {name}   (ell = 2, CDM frame)")
        print(f"    {'configuration':<22}" + "".join(f"{b[0]:>14}" for b in BACKGROUNDS))
        for label, _ in HALVES:
            print(f"    {label:<22}" + "".join(
                f"{seen.get((label, b[0], m), float('nan')):14.4f}"
                for b in BACKGROUNDS))
    print("""
  scattering half zeroed removes it  -> the (90) bundling; c6 and c9 name the
                                        remedy and nothing new is needed
  gravitational half zeroed removes it -> P1-T's mechanism is wrong; the
                                        gravitational half vanishes on EdS and
                                        cannot be background-independent
  neither removes it                 -> both exonerated; the residue is in the
                                        kernel or the quadrature
  both appear to                     -> not discriminating; read the absolute
                                        column and not the ratio
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
