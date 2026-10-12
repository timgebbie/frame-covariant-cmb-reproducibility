#!/usr/bin/env python3
r"""F6 — what each approximation is worth, as a ratio to the fuller result.

    python scripts/figure_f6_approximations.py

*Annals II* makes three narrowing choices that this bundle reproduces rather
than corrects, because reproducing a paper means reproducing its approximations
(decision **S15**). They are recorded in
`provenance/SOURCE-APPROXIMATIONS-v1.md` as **A-n**, deliberately apart from the
defects recorded as **B-n**. This figure is the one place their *cost* is a
number instead of an adjective.

Each series is $C_\ell^{\text{approximate}}/C_\ell^{\text{fuller}}$ for standard
CDM, so the panel is scale-free and a flat line at 1 means the approximation is
free. **The three do not have comparable weights, and that is the result**, so
the axis is logarithmic over six decades rather than cropped to make them look
alike:

1. **The visibility weighting on the gravitational source** (A-1, and A-2's
   consequence). $\mathcal V$ in place of $e^{-\kappa}$ is not a small
   correction: $\mathcal V\kappa'\sim\kappa'^2e^{-\kappa}$ is enormous, and the
   Sachs–Wolfe plateau does not survive it. The ratio runs to $10^4$–$10^6$.
   It is a **different calculation**, not a perturbation of one, which is why
   `Weighting` has no default and makes every caller say which question it is
   asking.
2. **$k_D$ stipulated at last scattering**, rather than accumulated along the
   ray. Worth under $0.1\%$ across the claimed range and about $5\%$ by
   $\ell=400$. This one **vindicates the release**: the cheap choice costs
   nothing where the release makes claims.
3. **The small-scale approximation** — dropping $-aH\Phi_A$ from (153), which is
   exactly the step that turns the acoustic pair into the printed oscillator
   (154). Worst at *large* scales, which is what "small-scale approximation"
   predicts, and the curve says so by departing from 1 most at low $\ell$.

**A correction to the comparison itself, kept because it nearly became a
figure.** Series 2 was first computed with $k_D(\eta)$ evaluated along the whole
ray. After last scattering $\kappa'\to0$, so $1/\kappa'$ in (dif-damp) diverges
and $k_D$ collapses, damping every integrated source to nothing — a plasma
formula evaluated in a universe that no longer has a plasma. That version
reported the release's choice as costing a **factor of nine** at $\ell=2$. The
factor was the artefact. Clamped to $k_D(\min(\eta,\eta_*))$, the honest answer
is the one above, and the release's choice is cheap rather than expensive.
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

from functions.background.flrw import CDM_MODEL  # noqa: E402
from functions.plotting.style import (  # noqa: E402
    INK,
    SERIES,
    SERIES_DASH,
    save_figure,
    use_house_style,
)
from functions.spectra import pipeline  # noqa: E402
from functions.spectra.decoupling import Weighting  # noqa: E402

#: The range F3 claims. Beyond it the formalism fails, not the numerics, and the
#: panel shades it for the same reason F3 does.
CLAIMED_ELL_MAX = 20

#: Vertical nudge, in points, per series slot. See `draw`.
LABEL_OFFSET = {1: 0.0, 2: 9.0, 3: -16.0}

ELLS = np.unique(np.round(np.logspace(np.log10(2.0), np.log10(400.0), 18)).astype(int))
K_COM = np.arange(0.05, 420.0, np.pi / 6.0)

#: (label for the direct annotation, slot, kwargs that turn the approximation ON)
VARIANTS = [
    ("visibility weighting\non the gravitational source  (A-1)", 1,
     {"weighting": Weighting.ANNALS_II}),
    (r"$k_D$ stipulated at $\eta_*$", 2,
     {"weighting": Weighting.STANDARD_ISW, "damping_epoch": "star"}),
    ("small-scale approximation\n($-aH\\Phi_A$ dropped from (153))", 3,
     {"weighting": Weighting.STANDARD_ISW, "expansion_coupling": False}),
]

#: The fuller counterpart of each, in the same order.
FULLER = [
    {"weighting": Weighting.STANDARD_ISW},
    {"weighting": Weighting.STANDARD_ISW, "damping_epoch": "running"},
    {"weighting": Weighting.STANDARD_ISW, "expansion_coupling": True},
]


def compute() -> list[dict]:
    base = dict(ells=ELLS, k_com=K_COM, n_eta=None)
    rows = []
    for (label, slot, approx), fuller in zip(VARIANTS, FULLER):
        a = pipeline.run(CDM_MODEL, **base, **approx).spectrum.cl_mode
        f = pipeline.run(CDM_MODEL, **base, **fuller).spectrum.cl_mode
        ratio = np.abs(a) / np.maximum(np.abs(f), 1e-300)
        rows.append({"label": label, "slot": slot, "ratio": ratio})
        within = ELLS <= CLAIMED_ELL_MAX
        print(f"  slot {slot}: worst |1 - ratio| over l<={CLAIMED_ELL_MAX} "
              f"= {np.max(np.abs(ratio[within] - 1.0)):.3e}; "
              f"at l={int(ELLS.max())} ratio = {ratio[-1]:.4f}")
    return rows


def draw(rows: list[dict]) -> plt.Figure:
    use_house_style()
    fig, ax = plt.subplots(figsize=(6.6, 4.5))
    fig.subplots_adjust(top=0.78, bottom=0.16, left=0.13, right=0.70)

    ax.axvspan(CLAIMED_ELL_MAX, float(ELLS.max()), color=INK["grid"],
               alpha=0.30, lw=0, zorder=0)
    ax.axhline(1.0, color=INK["muted"], lw=0.9, ls=(0, (2, 2)), zorder=2)

    for row in rows:
        ax.loglog(ELLS, np.maximum(row["ratio"], 1e-3), color=SERIES[row["slot"]],
                  ls=SERIES_DASH[row["slot"]], lw=1.9, solid_capstyle="round",
                  zorder=3)
        # **Direct labels, not a legend.** Two of the four palette slots sit
        # below 3:1 contrast on a light surface, so the label has to be beside
        # the line rather than in a key the eye must match back by colour.
        # Per-slot vertical offsets: series 2 and 3 both end within a factor of
        # three of unity, so on a six-decade axis their labels land on top of
        # one another. Nudged apart rather than moved into a legend, because
        # two of the four slots are below 3:1 contrast and a key would make the
        # reader match them back by colour.
        ax.annotate(row["label"], xy=(ELLS[-1], max(row["ratio"][-1], 1e-3)),
                    xytext=(6, LABEL_OFFSET[row["slot"]]), textcoords="offset points",
                    fontsize=7.0, color=INK["secondary"], va="center", ha="left")

    ax.set_xlabel(r"multipole  $\ell$")
    ax.set_ylabel(r"$C_\ell^{\mathrm{approximate}}\,/\,C_\ell^{\mathrm{fuller}}$")
    ax.set_xlim(2, float(ELLS.max()))

    fig.suptitle("F6   What each approximation is worth", x=0.012, y=0.962,
                 ha="left", fontsize=10, color=INK["primary"])
    fig.text(
        0.012, 0.900,
        "A flat line at 1 is an approximation that costs nothing. **The three do "
        "not have comparable weights**, and the axis spans six\ndecades rather "
        "than cropping them to look alike: one is a different calculation, one is "
        "free where this release makes claims,\nand one is worst at large scales, "
        "exactly as its name predicts. Shaded: beyond $\\ell=20$, which this "
        "release does not claim.".replace("**", ""),
        ha="left", va="top", fontsize=7.4, color=INK["secondary"],
    )
    return fig


def main() -> int:
    rows = compute()

    out = ROOT / "outputs" / "f6-approximations.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# C_l(approximate)/C_l(fuller), standard CDM\n")
        fh.write("approximation,ell,ratio\n")
        for row in rows:
            tag = row["label"].split("\n")[0].strip()
            for l, r in zip(ELLS, row["ratio"]):
                fh.write(f"{tag},{int(l)},{r:.12e}\n")
    print(f"wrote {out.relative_to(ROOT)}")

    for p in save_figure(draw(rows), "f6-approximations"):
        print(f"wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
