#!/usr/bin/env python3
"""F3 — the angular power spectrum, by both routes, for CDM and LambdaCDM.

    python scripts/figure_f3_angular_spectrum.py

Writes figures/f3-angular-spectrum-v1.0.0.{pdf,png} and the machine-readable
spectrum to outputs/f3-angular-spectrum.csv.

**This is the v1.0.0 deliverable**: Annals II (186) computed from (176), by the
mode route and by the covariant route of (187)+(188), for the standard-CDM model
of section 8.3.2 and for LambdaCDM, which Annals II does not treat.

Form. Row 1 is the spectrum itself, D_l = l(l+1)C_l/2pi, two models, log x. Row 2
is the verification that exists today: the fractional difference between the two
routes, which are identical analytically. Two hues, one per model; the route
difference is drawn in the ink colour because it belongs to neither.

**What this figure does not yet show.** There is no comparison against an
external code: criterion 5b compares against CAMB and CLASS with a measured
tolerance, and that is not run here. Recombination is equilibrium Saha, which
places last scattering but decouples too sharply. **The peak position and
amplitude are therefore not yet trustworthy; the shape is.** The caption says so,
and the figure is marked a release candidate until 5b is met.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import CDM_MODEL, LCDM_MODEL  # noqa: E402
from functions.plotting.style import (  # noqa: E402
    INK,
    SERIES,
    SERIES_DASH,
    save_figure,
    use_house_style,
)
from functions.spectra import pipeline  # noqa: E402
from functions.spectra.decoupling import Weighting  # noqa: E402

#: The l-grid. Logarithmic, because the plateau and the peak live decades apart.
ELLS = np.unique(np.round(np.logspace(np.log10(2.0), np.log10(400.0), 24)).astype(int))

#: The k-grid is LINEAR with dk = pi/6 in units of 1/eta_0. j_l(k dEta) oscillates
#: with period pi/dEta in k, so a logarithmic grid aliases the integrand at high
#: k however many points it has. Six samples per oscillation.
K_COM = np.arange(0.05, 420.0, np.pi / 6.0)

#: **The range this figure claims, and the limit that sets it.** Two limits
#: bound it and they are not the same. The *physics* limit is that (186) drops
#: the acoustic modulation $1-\cos(kr_s)$, which costs 4.75% at $\ell=20$ and
#: grows --- `scripts/derive_ell_range.py`. The *numerical* limit is the k-grid
#: truncation measured by `scripts/derive_ell_convergence.py`, which at 5%
#: reaches $\ell\simeq50$ taking the worse of the two models. **At 5% the physics binds**, so the claim stops at
#: the formalism rather than at the grid, which is the better of the two
#: sentences to publish and happens also to be the true one. At 1% they invert.
CLAIMED_ELL_MAX = 20

MODELS = (("standard CDM", CDM_MODEL, 1), (r"$\Lambda$CDM", LCDM_MODEL, 2))


def compute():
    rows = []
    for label, model, slot in MODELS:
        # n_eta is DERIVED from k_max, never set here. Finding T-3: this script
        # passed n_eta=1000, which gave 2.3 samples per j_l oscillation at the
        # band edge for LambdaCDM -- below Nyquist -- and the aliased integrand
        # returned a smooth, plausible spectrum of the wrong shape.
        run = pipeline.run(
            model, ells=ELLS, k_com=K_COM,
            weighting=Weighting.STANDARD_ISW, n_eta=None,
        )
        print(f"  {label}: n_eta={run.n_eta} "
              f"({run.eta_points_per_period:.1f} samples per oscillation at k_max); "
              f"damping still {run.damping_at_k_max:.3f} at the k grid edge"
              f"{'' if run.k_truncation_is_negligible else '  <-- TRUNCATED, not converged'}")
        rows.append({
            "label": label, "slot": slot, "run": run,
            "d_ell": run.spectrum.d_ell(),
            "gap": np.abs(run.spectrum.cl_mode - run.spectrum.cl_covariant)
                   / np.abs(run.spectrum.cl_mode),
        })
    return rows


def draw(rows) -> plt.Figure:
    use_house_style()
    fig, axes = plt.subplots(
        2, 1, figsize=(6.8, 6.0), sharex=True,
        gridspec_kw={"height_ratios": [1.0, 0.5], "hspace": 0.18},
    )
    fig.subplots_adjust(top=0.830, bottom=0.235, left=0.125, right=0.975)
    top, bot = axes

    for row in rows:
        top.loglog(ELLS, row["d_ell"] / row["d_ell"][0], color=SERIES[row["slot"]],
                   ls=SERIES_DASH[row["slot"]], lw=1.9, solid_capstyle="round",
                   label=row["label"], zorder=3)
        bot.semilogy(ELLS, np.maximum(row["gap"], 1e-18), color=SERIES[row["slot"]],
                     ls=SERIES_DASH[row["slot"]], lw=1.5, zorder=3)

    # Log y: the two models differ by a factor of seven at the peak while sharing
    # a plateau at unity, and on a linear axis the CDM curve is a flat line at the
    # bottom of the frame. Log shows plateau and peak at once, which is the shape
    # the figure is about.
    top.set_ylabel(r"$D_\ell\,/\,D_2$")
    top.set_ylim(0.4, 60.0)
    top.legend(frameon=False, loc="upper left", borderaxespad=0.0)
    top.axhline(1.0, color=INK["grid"], lw=0.8, zorder=1)

    # **The claimed range is marked, and the rest is still drawn.** Everything
    # past CLAIMED_ELL_MAX is a correct integration of (186); what fails there
    # is (186) itself, which drops the acoustic modulation. Hiding it would be
    # less informative than showing it and saying where the claim stops.
    for ax in (top, bot):
        ax.axvspan(CLAIMED_ELL_MAX, float(ELLS.max()), color=INK["grid"],
                   alpha=0.45, lw=0, zorder=0)
    top.axvline(CLAIMED_ELL_MAX, color=INK["muted"], lw=0.9,
                ls=(0, (1.5, 1.8)), zorder=2)
    top.text(CLAIMED_ELL_MAX * 1.15, 0.47,
             f"beyond $\\ell={CLAIMED_ELL_MAX}$ the formalism, not the\n"
             "integration, is out of range --- (186) drops\n"
             "the acoustic modulation",
             fontsize=6.8, color=INK["muted"], va="bottom", ha="left")

    bot.set_xscale("log")
    bot.set_xlabel(r"multipole  $\ell$")
    bot.set_ylabel("route\ndifference")
    bot.axhline(1e-11, color=INK["muted"], lw=0.9, ls=(0, (2, 2)), zorder=2)
    bot.text(2.3, 1.6e-11, r"acceptance threshold  $10^{-11}$",
             fontsize=7.4, color=INK["muted"], va="bottom")
    bot.set_ylim(1e-18, 1e-8)

    fig.suptitle(
        "F3   The angular power spectrum from Annals II (186), by two routes",
        x=0.012, y=0.962, ha="left", fontsize=10, color=INK["primary"],
    )
    fig.text(
        0.012, 0.905,
        "(186) computed from (176). The lower panel is the fractional difference between the mode route "
        "(186) and the\ncovariant route (187)+(188), which are identical analytically — it is a check on the "
        "arithmetic, not on the physics.",
        ha="left", va="top", fontsize=7.6, color=INK["secondary"],
    )
    fig.text(
        0.012, 0.098,
        "CLAIMED OVER $2\\leq\\ell\\leq20$ TO 5%, and shaded beyond. The binding limit is the formalism,\n"
        "not the integration: (186) drops the acoustic modulation, which costs 4.75% at $\\ell=20$ and grows.\n"
        "The $k$-grid truncation is looser at this tolerance, reaching 5% at $\\ell\\simeq50$; at 1% the two\n"
        "invert. Recombination is equilibrium Saha. Criterion 5b, against CAMB and CLASS, is v1.2.0.",
        ha="left", va="top", fontsize=7.2, color=INK["muted"],
    )
    return fig


def main() -> int:
    rows = compute()
    fig = draw(rows)
    save_figure(fig, "f3-angular-spectrum")

    out = ROOT / "outputs" / "f3-angular-spectrum.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("model,ell,C_ell_mode,C_ell_covariant,D_ell\n")
        for row in rows:
            s = row["run"].spectrum
            for i, l in enumerate(ELLS):
                fh.write(f"{row['label']},{l},{s.cl_mode[i]:.8e},"
                         f"{s.cl_covariant[i]:.8e},{row['d_ell'][i]:.8e}\n")
    print(f"wrote {out.relative_to(ROOT)}")
    for row in rows:
        print(f"  {row['label']:14s} max route difference {row['gap'].max():.2e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
