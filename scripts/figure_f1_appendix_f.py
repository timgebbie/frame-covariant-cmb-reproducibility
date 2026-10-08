#!/usr/bin/env python3
"""F1 — the Appendix F match. Small multiples, one panel per external treatment.

    python scripts/figure_f1_appendix_f.py

Writes figures/f1-appendix-f-v1.0.0.{pdf,png} and the machine-readable residuals
to outputs/f1-appendix-f-residuals.csv.

**This figure is where the bundle's independence lives.** Each external hierarchy
is transcribed in functions/harmonics/external.py from its own paper, never
through Annals II Appendix F; a coefficient read through Appendix F would be the
same source as Appendix F.

Two distinct normalisations are on display and both must match:

    Hu & Sugiyama Eq. (6)              l/(2l-1), (l+1)/(2l+3)   -> (F.3), beta
    Ma & Bertschinger Eqs. (49)/(50)   l/(2l+1), (l+1)/(2l+1)   -> (F.4), alpha
    Seljak & Zaldarriaga Eq. (3d)      l/(2l+1), (l+1)/(2l+1)   -> (F.4), alpha

Form: three columns, one per treatment. Row 1 is context — the two curves
overlaid at a representative multipole, which coincide. Row 2 is the claim — the
residual across the hierarchy, log y. Only two hues appear in the whole figure,
which keeps it clear of the all-pairs colour constraint; the column title names
the treatment. Never a dual y-axis.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.harmonics.external import (  # noqa: E402
    APPENDIX_F,
    CITATION,
    integrate_external,
    integrate_wilson,
)
from functions.harmonics.free_streaming import free_stream  # noqa: E402
from functions.plotting.style import (  # noqa: E402
    INK,
    SERIES,
    SERIES_DASH,
    save_figure,
    use_house_style,
)

K_COM = 1.0
ELL_MAX = 80
ELL_SHOWN = 5
ELL_COMPARED = 25
FORMS = ("HS", "WI", "MB", "SZ")
LABEL = {
    "HS": "Hu & Sugiyama",
    "WI": "Wilson",
    "MB": "Ma & Bertschinger",
    "SZ": "Seljak & Zaldarriaga",
}
EQUATION = {"HS": "Eq. (6)", "WI": "Eq. (8)", "MB": "Eqs. (49), (50)", "SZ": "Eq. (3d)"}


def compute():
    eta = np.linspace(0.0, 20.0, 1200)
    window = (eta > 2.0) & (eta < 18.0)
    mine = {
        "(F.3)": free_stream(K_COM, eta, ell_max=ELL_MAX, normalisation="beta").values,
        "(F.4)": free_stream(K_COM, eta, ell_max=ELL_MAX, normalisation="alpha").values,
    }
    rows = []
    for form in FORMS:
        ref = mine[APPENDIX_F[form]]
        ext = (
            integrate_wilson(K_COM, eta, ell_max=ELL_MAX)
            if form == "WI"
            else integrate_external(form, K_COM, eta, ell_max=ELL_MAX)
        )
        scale = ref[window, 0].mean() / ext[window, 0].mean()
        resid = np.max(np.abs(ext[window, : ELL_COMPARED + 1] * scale - ref[window, : ELL_COMPARED + 1]), axis=0)
        rows.append({"form": form, "eta": eta, "window": window, "ref": ref, "ext": ext * scale,
                     "scale": scale, "resid": resid})
    return rows


def draw(rows) -> plt.Figure:
    use_house_style()
    fig, axes = plt.subplots(
        2, 4, figsize=(9.8, 4.6), sharex="row",
        gridspec_kw={"height_ratios": [1.0, 0.85], "hspace": 0.62, "wspace": 0.30},
    )
    fig.subplots_adjust(top=0.735, bottom=0.255, left=0.068, right=0.988)
    # Row 1 must NOT share y: Hu & Sugiyama is in the beta normalisation and the
    # other two in alpha, so their amplitudes genuinely differ. Sharing the axis
    # would flatten two panels to make a point about normalisation that the
    # figure is not making. Row 2 shares y — residuals are in common units.
    for ax in axes[1, 1:]:
        ax.sharey(axes[1, 0])

    for col, row in enumerate(rows):
        form, eta, w = row["form"], row["eta"], row["window"]
        top, bot = axes[0, col], axes[1, col]

        # --- row 1: context. the two curves coincide, which is the result ----
        top.plot(eta[w], row["ref"][w, ELL_SHOWN], color=SERIES[1], lw=1.8,
                 ls=SERIES_DASH[1], solid_capstyle="round", zorder=3)
        top.plot(eta[w], row["ext"][w, ELL_SHOWN], color=SERIES[2], lw=1.8,
                 ls=SERIES_DASH[2], zorder=4)
        top.set_title(f"{LABEL[form]}\n{EQUATION[form]}  ·  {APPENDIX_F[form]}",
                      color=INK["primary"], pad=7)
        if col == 0:
            top.set_ylabel(rf"multipole $\ell={ELL_SHOWN}$")
        top.set_xlabel("")

        # --- row 2: the claim. residual across the hierarchy ----------------
        ell = np.arange(ELL_COMPARED + 1)
        bot.semilogy(ell, np.maximum(row["resid"], 1e-18), color=SERIES[2], lw=1.5, zorder=3)
        bot.axhline(1e-11, color=INK["muted"], lw=0.9, ls=(0, (1.6, 2.2)), zorder=2)
        if col == 0:
            bot.set_ylabel("residual")
            bot.text(0.04, 0.625, "acceptance threshold  $10^{-11}$",
                     transform=bot.transAxes, va="top", color=INK["muted"], fontsize=7.0)
        bot.set_xlabel("")
        bot.set_ylim(1e-17, 1e-8)
        worst = float(np.max(row["resid"]))
        bot.text(0.97, 0.07, f"max {worst:.1e}", transform=bot.transAxes,
                 ha="right", va="bottom", color=INK["primary"], fontsize=7.4)

    # one shared legend for the whole figure: the two curves coincide in every
    # panel, so repeating a legend three times would be noise
    handles = [
        Line2D([], [], color=SERIES[1], lw=1.8, ls=SERIES_DASH[1], label="this reconstruction"),
        Line2D([], [], color=SERIES[2], lw=1.8, ls=SERIES_DASH[2], label="external, as printed"),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.085, 0.905),
               ncol=2, columnspacing=1.6, handlelength=2.4)

    # With four columns the shared labels belong on the figure, centred, rather
    # than under one arbitrary panel.
    fig.text(0.528, 0.486, r"conformal time  $\eta$   [$1/k_{\rm com}$]",
             ha="center", va="top", fontsize="medium", color=INK["primary"])
    fig.text(0.528, 0.203, r"multipole  $\ell$",
             ha="center", va="top", fontsize="medium", color=INK["primary"])

    fig.suptitle(
        "F1   The covariant free-streaming recursion against four external hierarchies",
        x=0.012, y=0.975, ha="left", fontsize=10, color=INK["primary"],
    )
    fig.text(
        0.012, 0.105,
        "Each external hierarchy is transcribed from its own paper, not through Annals II Appendix F. Hu & "
        "Sugiyama and Wilson write the recursion in the\n$\\beta$ normalisation, Ma & Bertschinger and "
        "Seljak & Zaldarriaga in the $\\alpha$ normalisation — which is why the upper panels do not share a "
        "vertical scale. Wilson writes it in the\nimaginary convention, with both bracket terms positive "
        "under an overall $-i$; $\\Theta_\\ell = i^\\ell\\delta_\\ell$ recovers the real, opposite-sign "
        "form. That panel therefore\ntests the phase convention and not only the $\\ell$-weights. Overall "
        "scale is exactly 1; nothing is fitted.",
        ha="left", va="top", fontsize=7.2, color=INK["secondary"],
    )
    return fig


def main() -> int:
    rows = compute()
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    with (out / "f1-appendix-f-residuals.csv").open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("form,appendix_f_equation,source,scale,ell,residual\n")
        for row in rows:
            for ell, r in enumerate(row["resid"]):
                fh.write(f'{row["form"]},{APPENDIX_F[row["form"]]},"{CITATION[row["form"]]}",'
                         f'{row["scale"]:.12f},{ell},{r:.6e}\n')

    paths = save_figure(draw(rows), "f1-appendix-f")
    for p in paths:
        print(f"wrote {p.relative_to(ROOT)}")
    for row in rows:
        print(f"  {row['form']:3s} {APPENDIX_F[row['form']]}  scale {row['scale']:.9f}  "
              f"max residual {np.max(row['resid']):.3e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
