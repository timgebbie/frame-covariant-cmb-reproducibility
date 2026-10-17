#!/usr/bin/env python3
r"""D4 --- the monopole claim, and which rank actually carries the spectrum.

    python scripts/diagnostic_d4_monopole.py

**Two questions, and the second is why this diagnostic exists at last.**

*Annals II* p. 366 states flatly that *"there is no monopole temperature
anisotropy in the CGI approach while there is one in the canonical
treatment"*. D4 was registered against that sentence in v1.0.0 and deferred
three times, because a claim the paper makes in one line looked like a claim
nothing could go wrong in. **It was deferred to v1.5.0 and is pulled forward to
v1.3.0 by finding T-57**, which is what happens when nobody measures which rank
is carrying the answer.

The covariant hierarchy carries $\tau^{A_\ell}$ for $\ell\ge1$: there is no
$\tau$ at $\ell=0$ to carry a monopole, and `integral_solution` refuses
$\ell<1$ for the independent reason that (102)'s rank-two term needs
$j_{\ell-1}$. So "the monopole sector" of this bundle means **rank 0 of
(102)** --- the $C_0$ coefficient and the scalar boundary term --- and the
Sachs--Wolfe plateau is its to carry. The dipole sector, rank 1, is the
Doppler term; it is $90^\circ$ out of phase with rank 0 and it carries one more
power of $k$.

**That phase relation is the whole diagnostic.** The monopole goes as
$\cos(k r_s)$ and sources $C_\ell$ peaks at $n\,\ell_A$; the dipole goes as
$\sin(k r_s)$ and sources them at $(n+\tfrac12)\,\ell_A$. So *where the peaks
sit says which rank is carrying the spectrum*, and it says it without
reference to any external code. On 2026-10-17 F9's peaks sat at
$(n+\tfrac12)\,\ell_A$ and the reason was T-57: every released caller of
`build_environment` took the default line-of-sight weight, which was
$\mathcal V=\kappa'e^{-\kappa}$ rather than the $e^{-\kappa}$ of approximation
**A-2**, and $\mathcal V$ multiplies (178)'s already-present $\kappa'$ a second
time.

**Both weights are run here, every time.** The departure A-2 records is only
*measurable* if the thing departed from is still executable --- the same reason
`expansion_coupling=False` keeps (154) and `acoustic_start='z_max'` keeps the
pre-T-51 grid. A diagnostic that ran only the choice the bundle made would
report that the bundle agrees with itself.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    PLANCK_H,
    PLANCK_MODEL,
    PLANCK_N_S,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.acoustic import sound_horizon_from_zero  # noqa: E402
from functions.spectra.angular import cl_covariant_route, d_ell  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment,
    coefficient_sets,
    transfer_by_rank,
)

VERSION = "v1.3.0"

#: Through the plateau and into the rise. The question here is the SHAPE at low
#: $\ell$, which is where the two weights differ by two orders of magnitude;
#: the acoustic band is F9's business and is not re-measured on this grid.
ELLS = np.array([2, 4, 7, 11, 16, 22, 30, 45, 60, 80, 100])

#: $k_{\max}=120$ covers $\ell\le100$ with room ($\ell\simeq k\,r_\theta$ puts
#: $\ell=100$ at $k\simeq32$), and the spacing is **derived** --- finding
#: **T-56**, the defect this diagnostic would otherwise have inherited.
K_MAX = 120.0

#: The two frames, and **both are run** --- finding **T-59**. (110) puts the
#: Newtonian frame's whole source in rank one and the CDM frame's in the shear
#: pair, so "which rank carries $C_\\ell$" has two answers and reporting one of
#: them is reporting half the question. It is also how T-59 was found: under
#: the corrected weight the Newtonian frame has a Sachs--Wolfe plateau and the
#: CDM frame does not, and F9 draws the CDM frame.
FRAMES = ("newtonian", "cdm")


def spectra(weight: str, frame: str) -> tuple[dict[int, np.ndarray], float, int]:
    """$C_\\ell$ by rank, at one line-of-sight weight and one frame."""
    gamma = shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H)
    env = build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2, transfer_gamma=gamma, hubble_h=PLANCK_H,
        f_2=F2_DEFAULT, line_of_sight_weight=weight)
    r_theta = float(env.background.eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)

    blocks = {r: np.zeros((ELLS.size, k_com.size)) for r in (-1, 0, 1, 2)}
    for j, k in enumerate(k_com):
        sets = dict(zip(("newtonian", "cdm"), coefficient_sets(float(k), env)))
        by_rank = transfer_by_rank(ELLS, float(k), sets[frame], env, table)
        for r in blocks:
            blocks[r][:, j] = by_rank[r]
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)
    out = {r: np.array([cl_covariant_route(int(l), k_com, block[i], power)
                        for i, l in enumerate(ELLS)])
           for r, block in blocks.items()}
    return out, r_theta, k_com.size


def acoustic_scale() -> tuple[float, float]:
    r"""$\ell_A=\pi r_\theta/r_s$, and $r_\theta$, from the bundle's own tables."""
    gamma = shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H)
    env = build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2, transfer_gamma=gamma, hubble_h=PLANCK_H,
        f_2=F2_DEFAULT, line_of_sight_weight="opacity")
    r_theta = float(env.background.eta_0 - env.eta_star)
    eta_rs, r_s_table = sound_horizon_from_zero(
        env.background, float(env.eta_star), omega_b_h2=PLANCK_OMEGA_B_H2)
    return float(np.pi * r_theta / float(r_s_table[-1])), r_theta


def report() -> list[str]:
    say: list[str] = []
    a = say.append
    a("D4 - the monopole claim, and which rank carries the spectrum")
    a("Generated by scripts/diagnostic_d4_monopole.py. Do not edit by hand.")
    a("")
    a("  Annals II p. 366: \"there is no monopole temperature anisotropy in")
    a("  the CGI approach while there is one in the canonical treatment\".")
    a("")
    a("  The covariant hierarchy carries tau^{A_l} for l >= 1, so there is no")
    a("  l = 0 object to carry a monopole and none is computed: integral_solution")
    a("  refuses ells below 1. What this bundle calls the monopole SECTOR is")
    a("  rank 0 of (102) - the C_0 coefficient and the scalar boundary term -")
    a("  and the Sachs-Wolfe plateau is its to carry.")
    a("")

    ell_a, r_theta = acoustic_scale()
    a(f"  PLANCK_MODEL   r_theta = {r_theta:.6f}   l_A = pi r_theta / r_s = {ell_a:.1f}")
    a("")
    a("  PHASE, and it is the whole diagnostic:")
    a(f"      rank 0, the monopole, goes as cos(k r_s)  ->  peaks at n l_A"
      f"        = {', '.join(f'{n*ell_a:.0f}' for n in (1, 2, 3))}")
    a(f"      rank 1, the dipole,   goes as sin(k r_s)  ->  peaks at (n+1/2) l_A"
      f"  = {', '.join(f'{(n+0.5)*ell_a:.0f}' for n in (0, 1, 2))}")
    a("      so WHERE the peaks sit says WHICH rank is carrying the spectrum,")
    a("      with no reference to any external code.")
    a("")

    results = {}
    for weight in ("opacity", "printed"):
        for frame in FRAMES:
            results[weight, frame] = spectra(weight, frame)

    _, _, n_k = results["opacity", "cdm"]
    a(f"  k grid derived from T-56: {n_k} points to k = {K_MAX:.0f}, "
      f"{(np.pi / r_theta) / (K_MAX - 0.05) * (n_k - 1):.2f} samples per")
    a("  j_l^2 oscillation. Everything but the weight and the frame is held fixed.")
    a("")
    a("  C_l by rank, as a fraction of the total. These are AUTO terms and")
    a("  C_l is quadratic, so they do not sum to 1 - the remainder is the")
    a("  cross terms, reported. F5 makes the same distinction for the same reason.")
    a("")

    for weight, title in (("opacity", "e^-kappa, as (98) prints it - A-2's choice, and this bundle's"),
                          ("printed", "V = kappa' e^-kappa, as (178) prints it - the control")):
      for frame in FRAMES:
        cl, _, _ = results[weight, frame]
        d = d_ell(ELLS, cl[-1])
        shape = d / np.interp(30.0, ELLS, d)
        a(f"  --- weight = {weight}, frame = {frame}:  {title}")
        a(f"      {'l':>5s} {'D_l/D_30':>10s} {'rank0 (mono)':>14s} "
          f"{'rank1 (dipole)':>16s} {'rank2 (shear)':>15s} {'cross':>9s}")
        for i, l in enumerate(ELLS):
            total = cl[-1][i]
            f0, f1, f2 = (cl[0][i] / total, cl[1][i] / total, cl[2][i] / total)
            a(f"      {l:5d} {shape[i]:10.4f} {f0:14.5f} {f1:16.5f} "
              f"{f2:15.3e} {1.0 - f0 - f1 - f2:9.4f}")
        a("")

    cl_o, cl_p = results["opacity", "cdm"][0], results["printed", "cdm"][0]
    do = d_ell(ELLS, cl_o[-1]); dp = d_ell(ELLS, cl_p[-1])
    so = do / np.interp(30.0, ELLS, do); sp = dp / np.interp(30.0, ELLS, dp)
    f1_o = float(np.median(cl_o[1] / cl_o[-1]))
    f1_p = float(np.median(cl_p[1] / cl_p[-1]))
    a("  --- what the control measures ----------------------------------")
    a(f"      median rank-1 share   e^-kappa {f1_o:9.5f}      V {f1_p:9.5f}")
    a(f"      D_2/D_30              e^-kappa {so[0]:9.4f}      V {sp[0]:9.4f}")
    a(f"      ratio of the two shapes at l=2:          {so[0] / sp[0]:9.2f}x")
    a("")
    a("      Under V the dipole IS the transfer function, at every multipole")
    a("      from 2 to 100, and the plateau is gone - D_l rises as l^2, which")
    a("      is C_l constant. That is approximation A-2 measured a second time,")
    a("      independently of the table in SOURCE-APPROXIMATIONS-v1.md and")
    a("      through a different route (two_frame rather than pipeline).")
    a("")
    cl_n = results["opacity", "newtonian"][0]
    dn = d_ell(ELLS, cl_n[-1]); sn = dn / np.interp(30.0, ELLS, dn)
    a("  --- finding T-59: the two frames do not agree, and only one has ---")
    a("      a Sachs-Wolfe plateau ------------------------------------------")
    a(f"      {'l':>5s} {'D_l/D_30 newtonian':>20s} {'D_l/D_30 cdm':>14s} "
      f"{'CAMB':>8s}")
    for i, l in enumerate(ELLS):
        camb = "0.881" if l == 2 else ("1.000" if l == 30 else "")
        a(f"      {l:5d} {sn[i]:20.4f} {so[i]:14.4f} {camb:>8s}")
    a("")
    a("      The Newtonian frame is FLAT to within 30% over 2 <= l <= 30, which")
    a("      is what SOURCE-APPROXIMATIONS-v1.md's A-2 table says e^-kappa gives")
    a("      and what a Sachs-Wolfe plateau is. The CDM frame rises by a factor")
    a(f"      of {1.0/so[0]:.0f} over the same range.")
    a("")
    a("      This is NOT the weight and it is NOT the grid: both columns above")
    a("      are one environment, one acoustic solution, one k grid, differing")
    a("      only in the frame (110) specialises to. In the Newtonian frame the")
    a("      rank-0 share is identically zero - (110) puts the whole source in")
    a("      rank one - and the plateau is there anyway, because the monopole")
    a("      combination (dT + Phi_A) sits INSIDE c_1 as a_b1 = k(dT + Phi_A).")
    a("      In the CDM frame rank 0 carries 99% and the plateau is not there.")
    a("")
    a("      **F9 draws the CDM frame.** So does the released spectrum.")
    a("")
    a("      Annals II's own statement, sources.py: the Newtonian frame carries")
    a("      its whole O(l) source in the ACCELERATION pair and the CDM frame")
    a("      in the SHEAR pair - two expressions for one operator - and the sum")
    a("      is an observable. These two are not the same observable. That is")
    a("      finding T-14 and decision S21, now measured without the weight")
    a("      masking it: F2 reports the cost of sigma -> 0 in the CDM frame as")
    a("      99.9% where it read 0.27% before T-57, and F5 reports the two")
    a("      frames' C_l agreeing to a median of 1.00e+00 - that is, not at all.")
    a("")
    a("      **Which frame F9 should draw is the PI\'s call**, because it is")
    a("      Paper 1\'s claim and not a numerical one. What is not a judgement")
    a("      call: the Newtonian frame is the one validated against an analytic")
    a("      arbiter - D5, 0.26% against the corrected (201) over 2 <= l <= 20,")
    a("      through pipeline.run, which is a Newtonian-frame assembly.")
    a("")
    a("  --- finding T-57 ------------------------------------------------")
    a("      TwoFrameEnvironment.line_of_sight_weight documented 'opacity' as")
    a("      its default and the code read 'printed'. None of the eight released")
    a("      callers named the argument, so F2, F5, F7, F9, D6, D7, the 5b")
    a("      comparison and the benchmark all ran under the control column above.")
    a("      Fixed 2026-10-17: the default now matches its own docstring, every")
    a("      caller states the weight, and check_release_hygiene.py refuses a")
    a("      release in which one does not. A-1 asked for exactly that in words")
    a("      - \"the caller states which\" - and nothing enforced it.")
    a("")
    a("      A docstring is not an executable decision. Every other gate in this")
    a("      bundle compares a file to a rule; this was a decision disagreeing")
    a("      with its own implementation, three lines apart, and no instrument")
    a("      in the bundle was pointed at that.")
    return say


def main() -> int:
    lines = report()
    print("\n".join(lines))
    out = ROOT / "diagnostics" / f"d4-monopole-{VERSION}.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"\nwrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
