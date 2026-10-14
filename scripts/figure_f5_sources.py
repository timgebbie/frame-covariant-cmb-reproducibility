#!/usr/bin/env python3
r"""F5 — the source decomposition in two frames, split by **rank**.

    python scripts/figure_f5_sources.py

The claim F5 exists to make: **the total is common to both frames and the
decomposition is not.** $\tau_{A_\ell}$ for $\ell\ge2$ is frame-invariant at
first order --- *Annals II* says so in the sentence below (37), and
`frames.py::boosted_multipole` is that sentence made callable --- so (102)
carried covariantly must return the same spectrum in the Newtonian and energy
frames while splitting it quite differently.

**Why rank and not primary/Doppler/integrated.** The three-way split of \S7.1.1
is a *Newtonian-frame* construction: it descends from (110) and (111), which
exist only after $\tilde\sigma_{ab}\approx0$ has emptied the shear sector.
Drawing the CDM frame that way would report a Newtonian-frame answer about a
frame that is not Newtonian. The rank split $C_0,C_1,C_2$ is what the
rank-by-rank match (89) actually produces, and it is defined in every frame.
*The PI's call, 2026-10-14.*

**Three panels, and the middle one is the figure.**

* **(a)** the two totals. They lie on top of each other --- to the residual
  measured in `provenance/FRAME-INVARIANCE-MEASUREMENT-v1.md` and printed in the
  panel, not to zero, and the difference between those two statements is the
  honest part of this figure.
* **(b)** the decomposition. In the Newtonian frame **one rank carries
  everything**; in the CDM frame **all three are occupied**. Same total,
  different parts: that is the whole claim, and it is one panel.
* **(c)** why the parts do not add. $C_\ell$ is **quadratic** in the source, so
  the three rank contributions to it do not sum to the total --- the three
  cross-spectra are the difference, and two of them are negative.

**This figure was deferred three times, twice for reasons that were wrong**
(S20's $\Phi_H$ claim, S21's hierarchy claim, S23's premise, which was
falsified). It is drawn now because the rank-two sign it rests on was settled
--- **B-13** --- and not because the deferral ran out.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from functions.plotting.style import (  # noqa: E402
    INK,
    SERIES,
    SERIES_DASH,
    save_figure,
    use_house_style,
)
from functions.spectra.angular import cl_covariant_route, d_ell  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment,
    cl_cross,
    coefficient_sets,
    transfer_by_rank,
)

ELLS = np.unique(np.round(np.logspace(np.log10(2.0), np.log10(400.0), 16)).astype(int))

#: **Linear at $dk=\pi/6$, as F3 uses.** A logarithmic grid aliases the
#: line-of-sight integrand at high $k$ however many points it has, and this
#: project has made that mistake once already (the S24 sweep).
#: **Runs to 1900, not 420 --- finding T-32.** The diffusion scale is
#: $k_D=871.4$, so a grid stopping at 420 stops where $e^{-(k/k_D)^2}=0.79$,
#: and the shear sector's $k$-integrand, carrying an extra factor of $k$, peaks
#: at $k_D/2\simeq436$ --- outside it. Rank 1 does not need that tail and ranks
#: 0 and 2 do. $e^{-(k_{\max}/k_D)^2}=8.6\times10^{-3}$ here, which is the gate
#: **T-16** wrote down during v1.0.0 and dated to v1.2.0.
K_COM = np.arange(0.05, 1900.0, np.pi / 3.0)

RANK_LABEL = {0: r"rank 0   $C_0$", 1: r"rank 1   $C_1$", 2: r"rank 2   $C_2$"}
RANK_SLOT = {0: 3, 1: 1, 2: 2}


def compute() -> dict:
    env = build_environment(float(K_COM.max()))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(K_COM.max() * (env.background.eta_0 - env.eta[0])) + 20.0,
    )

    shape = (ELLS.size, K_COM.size)
    transfer = {frame: {r: np.zeros(shape) for r in (-1, 0, 1, 2)}
                for frame in ("newtonian", "cdm")}

    for j, k in enumerate(K_COM):
        sets = dict(zip(("newtonian", "cdm"), coefficient_sets(float(k), env)))
        for frame, coefficients in sets.items():
            parts = transfer_by_rank(ELLS, float(k), coefficients, env, table)
            for r, values in parts.items():
                transfer[frame][r][:, j] = values

    # **The ranks add in the transfer and this is asserted, not assumed.**
    for frame in transfer:
        summed = sum(transfer[frame][r] for r in (0, 1, 2))
        worst = np.max(np.abs(summed - transfer[frame][-1])) / np.max(
            np.abs(transfer[frame][-1]))
        if worst > 1e-12:
            raise ValueError(f"{frame}: the ranks do not sum to the total ({worst:.2e})")
        print(f"  {frame:10s} ranks sum to the total to {worst:.2e}")

    power = primordial_power(K_COM, n_s=1.0, amplitude=1.0)
    cl = {frame: {r: np.array([cl_covariant_route(int(l), K_COM, transfer[frame][r][i],
                                                  power)
                               for i, l in enumerate(ELLS)])
                  for r in (-1, 0, 1, 2)}
          for frame in transfer}

    cross = {(a, b): np.array([cl_cross(int(l), K_COM, transfer["cdm"][a][i],
                                        transfer["cdm"][b][i], power)
                               for i, l in enumerate(ELLS)])
             for a, b in ((0, 1), (0, 2), (1, 2))}

    # **The parts plus the cross terms must be the whole**, and C_l is quadratic
    # so the parts alone are not. Both halves of that are checked here.
    autos = sum(cl["cdm"][r] for r in (0, 1, 2))
    reconstructed = autos + 2.0 * sum(cross.values())
    worst = np.max(np.abs(reconstructed - cl["cdm"][-1]) / np.abs(cl["cdm"][-1]))
    if worst > 1e-10:
        raise ValueError(f"autos + 2*crosses != total ({worst:.2e})")
    gap = np.max(np.abs(autos - cl["cdm"][-1]) / np.abs(cl["cdm"][-1]))
    print(f"  autos + 2x crosses reproduce C_l to {worst:.2e}; "
          f"autos alone are off by {gap:.2f} --- C_l is quadratic")

    residual = np.abs(cl["newtonian"][-1] - cl["cdm"][-1]) / np.maximum(
        np.abs(cl["newtonian"][-1]), np.abs(cl["cdm"][-1]))
    print(f"  the two frames' C_l agree to a median of {np.median(residual):.2e} "
          f"(worst {np.max(residual):.2e}) over {ELLS.min()} <= l <= {ELLS.max()}")

    return {"cl": cl, "cross": cross, "residual": residual,
            "autos_gap": float(gap), "power": power}


def draw(data: dict) -> plt.Figure:
    use_house_style()
    fig, axes = plt.subplots(
        4, 1, figsize=(6.6, 9.4), sharex=True,
        gridspec_kw={"height_ratios": [2.0, 1.0, 2.0, 1.5]})
    fig.subplots_adjust(top=0.875, bottom=0.065, left=0.145, right=0.955, hspace=0.16)
    cl, cross, residual = data["cl"], data["cross"], data["residual"]
    ax_a, ax_r, ax_b, ax_c = axes

    # ---- (a) the two totals -------------------------------------------
    for frame, slot, label in (("newtonian", 1, "Newtonian frame"),
                               ("cdm", 2, "CDM frame")):
        ax_a.loglog(ELLS, np.abs(d_ell(ELLS, cl[frame][-1])), color=SERIES[slot],
                    ls=SERIES_DASH[slot], lw=1.9, solid_capstyle="round", zorder=3)
        # Labelled where the two curves are **furthest apart**, not at the end,
        # where they converge and the text lands on the line.
        j = int(np.argmax(np.abs(residual)))
        ax_a.annotate(label, xy=(ELLS[j], abs(d_ell(ELLS, cl[frame][-1])[j])),
                      xytext=(12, 15 if slot == 1 else -17),
                      textcoords="offset points", fontsize=7.0,
                      color=INK["secondary"], ha="left")
    ax_a.set_ylabel(r"$\ell(\ell+1)C_\ell/2\pi$" + "\n(total)")

    # ---- (a') the residual, drawn rather than asserted ------------------
    best = int(ELLS[int(np.argmin(residual))])
    ax_r.semilogx(ELLS, 100.0 * residual, color=INK["primary"], lw=1.7,
                  solid_capstyle="round", zorder=3)
    ax_r.set_yscale("log")
    ax_r.set_ylabel("frame\ndisagreement  [%]")
    ax_r.annotate(
        f"{100 * residual[0]:.0f}% at $\\ell={int(ELLS[0])}$, "
        f"{100 * residual.min():.0f}% at $\\ell={best}$, "
        f"{100 * residual[-1]:.0f}% at $\\ell={int(ELLS[-1])}$",
        xy=(0.035, 0.12), xycoords="axes fraction", fontsize=7.0,
        color=INK["secondary"], va="bottom", ha="left")

    # ---- (b) the decomposition ----------------------------------------
    for rank in (1, 0, 2):
        slot = RANK_SLOT[rank]
        energy = np.abs(d_ell(ELLS, cl["cdm"][rank]))
        ax_b.loglog(ELLS, np.maximum(energy, 1e-12), color=SERIES[slot],
                    ls=SERIES_DASH[slot], lw=1.9, solid_capstyle="round", zorder=3)
        ax_b.annotate(RANK_LABEL[rank], xy=(ELLS[-1], max(energy[-1], 1e-12)),
                      xytext=(-4, 8), textcoords="offset points", fontsize=7.0,
                      color=INK["secondary"], ha="right")
    ax_b.loglog(ELLS, np.abs(d_ell(ELLS, cl["newtonian"][1])), color=INK["muted"],
                ls=(0, (1.0, 1.8)), lw=1.4, zorder=2)
    ax_b.annotate(
        "dotted: the Newtonian frame, where rank 1 carries\n"
        r"everything and $C_0\equiv C_2\equiv0$ — that is (110)",
        xy=(0.035, 0.10), xycoords="axes fraction", fontsize=7.0,
        color=INK["secondary"], va="bottom", ha="left")
    ax_b.set_ylabel(r"$\ell(\ell+1)C_\ell/2\pi$" + "\n(CDM frame, by rank)")

    # ---- (c) the cross terms ------------------------------------------
    scale = np.abs(d_ell(ELLS, cl["cdm"][-1]))
    # Vertical nudges: C^12 and C^02 both sit within a decade of zero on a
    # symlog axis, so their labels land on one another unless staggered.
    nudge = {(0, 1): -15.0, (1, 2): -15.0, (0, 2): 10.0}
    for (a, b), slot in zip(((0, 1), (1, 2), (0, 2)), (1, 2, 3)):
        share = 2.0 * d_ell(ELLS, cross[(a, b)]) / scale
        ax_c.plot(ELLS, share, color=SERIES[slot], ls=SERIES_DASH[slot], lw=1.9,
                  solid_capstyle="round", zorder=3)
        j = max(len(ELLS) - 5, 0)
        ax_c.annotate(rf"$2\,C_\ell^{{{a}{b}}}$", xy=(ELLS[j], share[j]),
                      xytext=(0, nudge[(a, b)]),
                      textcoords="offset points", fontsize=7.0,
                      color=INK["secondary"], ha="center")
    ax_c.axhline(0.0, color=INK["muted"], lw=0.9, ls=(0, (2, 2)), zorder=2)
    ax_c.set_xscale("log")
    ax_c.set_yscale("symlog", linthresh=1e-3)
    ax_c.set_ylabel("cross terms, as a\nshare of the total")
    ax_c.set_xlabel(r"multipole  $\ell$")
    ax_c.annotate(
        f"the three auto-spectra alone miss the total by {data['autos_gap']:.0%}:\n"
        r"$C_\ell$ is quadratic in the source, so the ranks do not add",
        xy=(0.035, 0.94), xycoords="axes fraction", fontsize=7.0,
        color=INK["secondary"], va="top", ha="left")

    for ax in axes:
        ax.set_xlim(float(ELLS.min()), float(ELLS.max()))

    fig.suptitle("F5   The source decomposition in two frames, by rank",
                 x=0.012, y=0.980, ha="left", fontsize=10, color=INK["primary"])
    fig.text(
        0.012, 0.945,
        "The total is common to both frames and the decomposition is not. Split "
        "by rank, which is what the match (89) produces\nand is defined in every "
        "frame — not by the primary/Doppler/integrated split of §7.1.1, which "
        "exists only after the\nNewtonian choice has emptied the shear sector. "
        "**The agreement is measured and it is not exact**: the second panel is "
        "the\ngap, and it is drawn rather than described.".replace("**", ""),
        ha="left", va="top", fontsize=7.4, color=INK["secondary"],
    )
    return fig


def main() -> int:
    data = compute()

    out = ROOT / "outputs" / "f5-sources.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# C_l by rank in two frames, covariant route, standard CDM\n")
        fh.write("frame,rank,ell,cl\n")
        for frame in ("newtonian", "cdm"):
            for rank in (-1, 0, 1, 2):
                tag = "total" if rank == -1 else str(rank)
                for l, c in zip(ELLS, data["cl"][frame][rank]):
                    fh.write(f"{frame},{tag},{int(l)},{c:.12e}\n")
        for (a, b), values in data["cross"].items():
            for l, c in zip(ELLS, values):
                fh.write(f"energy,cross{a}{b},{int(l)},{c:.12e}\n")
    print(f"wrote {out.relative_to(ROOT)}")

    for p in save_figure(draw(data), "f5-sources", "v1.2.0"):
        print(f"wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
