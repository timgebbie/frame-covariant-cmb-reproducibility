#!/usr/bin/env python3
r"""F4 — the angular correlation function, and the transform that makes it.

    python scripts/figure_f4_correlation.py

$C(\theta)=\sum_\ell \frac{2\ell+1}{4\pi}C_\ell P_\ell(\cos\theta)$ is the
real-space view of F3: the same content, read as a correlation between two
directions separated by $\theta$ rather than as power at a multipole. It is the
form the PI has asked become the README's key figure at v1.2.0, once the
acoustic peaks exist to put a feature in it.

**Summed only over the range F3 claims.** $2\le\ell\le20$, the limit set by
(186) dropping the acoustic modulation — see `diagnostics/ell-range-v1.0.0.txt`
and `ell-convergence-v1.0.0.txt`. Summing further would draw a curve carrying
multipoles the release does not stand behind, and a real-space plot hides which
$\ell$ contributed, so the restriction has to be made here rather than left to
a caption.

**The lower panel is what makes this an acceptance figure rather than a
picture.** A Legendre sum is invertible:
$C_\ell = 2\pi\int_{-1}^{1}C(\theta)P_\ell(\cos\theta)\,\dd\cos\theta$. Going
out to $C(\theta)$ and back must return the input, and the residual is a
statement about the quadrature and the normalisation that no amount of looking
at the upper panel would give. It is the same discipline as F3's two routes,
and the same caution applies: **the round trip shares the $C_\ell$ with
itself**, so it tests the transform and says nothing about the spectrum.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import eval_legendre

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

#: The range F3 claims. Not a plotting choice; see the module docstring.
ELL_MIN, ELL_MAX = 2, 20

#: Gauss-Legendre nodes, **derived from the requirement rather than chosen
#: comfortably above it**. The integrand is $P_\ell P_{\ell'}$ of degree at most
#: $2\ell_{\max}$, and $n$ nodes integrate degree $2n-1$ exactly, so
#: $n=\ell_{\max}+1$ is the smallest exact choice and every node past it adds
#: **only roundoff**.
#:
#: That is not a micro-optimisation. This script was first written with
#: `QUAD_NODES = 128`, picked for comfort, and the round-trip residual came out
#: at $3\times10^{-12}$ — thirteen times worse than at the derived value.
#: Measured across node counts the residual *grows*: 1.8e-14 at n=21, 7.9e-14
#: at n=32, 1.1e-12 at n=128, 1.6e-12 at n=512. The quadrature is already exact;
#: more nodes buy nothing and cost summation error.
#:
#: It is finding **T-3** seen from the other side. There a grid was too coarse
#: and aliased; here one was too fine and accumulated. Both came of choosing a
#: grid instead of deriving it.
QUAD_NODES = ELL_MAX + 1

THETA_DEG = np.linspace(0.0, 180.0, 721)

#: **Measured, not chosen.** With the node count derived above, the residual is
#: limited by summation roundoff over the $\ell$ range and by the dynamic range
#: of $C_\ell$ across it. Measured at 1.8e-14 for a flat spectrum; 1e-13 leaves
#: room for the conditioning of a real one without leaving room for a defect.
#: The first version of this file carried 1e-12 because that is a round number,
#: and it failed — which is the correct outcome for a tolerance nobody measured.
ACCEPTANCE = 1e-13


def load_spectrum() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """F3's own C_l, read from its committed output rather than recomputed.

    Recomputing here would compare two runs of the same code and call the
    agreement a check. The figure reads what F3 wrote.
    """
    rows = list(csv.DictReader(
        (ROOT / "outputs" / "f3-angular-spectrum.csv").open(encoding="utf-8")
    ))
    out: dict[str, tuple[list[int], list[float]]] = {}
    for r in rows:
        ell = int(r["ell"])
        if not (ELL_MIN <= ell <= ELL_MAX):
            continue
        out.setdefault(r["model"], ([], []))
        out[r["model"]][0].append(ell)
        out[r["model"]][1].append(float(r["C_ell_mode"]))
    return {k: (np.array(a), np.array(b)) for k, (a, b) in out.items()}


def correlation(ell: np.ndarray, cl: np.ndarray, theta_deg: np.ndarray) -> np.ndarray:
    r"""$C(\theta)=\sum_\ell\frac{2\ell+1}{4\pi}C_\ell P_\ell(\cos\theta)$."""
    mu = np.cos(np.deg2rad(theta_deg))
    terms = [(2 * l + 1) / (4 * np.pi) * c * eval_legendre(int(l), mu)
             for l, c in zip(ell, cl)]
    return np.sum(terms, axis=0)


def inverse(ell: np.ndarray, c_theta_at: callable) -> np.ndarray:
    r"""$C_\ell = 2\pi\int_{-1}^{1}C(\theta)P_\ell(\mu)\,\dd\mu$, by Gauss-Legendre.

    The quadrature is exact for the polynomial degrees in play, so any residual
    is the transform's own arithmetic and not a discretisation error that could
    be tuned away with more nodes.
    """
    mu, w = leggauss(QUAD_NODES)
    values = c_theta_at(mu)
    return np.array([2 * np.pi * np.sum(w * values * eval_legendre(int(l), mu))
                     for l in ell])


def compute() -> list[dict]:
    rows = []
    for slot, (label, key) in enumerate(
        (("standard CDM", "standard CDM"), (r"$\Lambda$CDM", r"$\Lambda$CDM")), start=1
    ):
        spectra = load_spectrum()
        if key not in spectra:
            continue
        ell, cl = spectra[key]
        c_theta = correlation(ell, cl, THETA_DEG)

        def at_mu(mu, ell=ell, cl=cl):
            return np.sum([(2 * l + 1) / (4 * np.pi) * c * eval_legendre(int(l), mu)
                           for l, c in zip(ell, cl)], axis=0)

        recovered = inverse(ell, at_mu)
        residual = np.abs(recovered - cl) / np.abs(cl)
        rows.append({"label": label, "slot": slot, "ell": ell, "cl": cl,
                     "c_theta": c_theta, "residual": residual})
    return rows


def draw(rows: list[dict]) -> plt.Figure:
    use_house_style()
    fig, axes = plt.subplots(2, 1, figsize=(6.6, 5.4), height_ratios=(2.4, 1.0),
                             sharex=False)
    top, bot = axes
    fig.subplots_adjust(top=0.80, bottom=0.21, left=0.13, right=0.97, hspace=0.42)

    for row in rows:
        top.plot(THETA_DEG, row["c_theta"] / row["c_theta"][0],
                 color=SERIES[row["slot"]], ls=SERIES_DASH[row["slot"]], lw=1.9,
                 solid_capstyle="round", label=row["label"], zorder=3)
        bot.semilogy(row["ell"], np.maximum(row["residual"], 1e-18),
                     color=SERIES[row["slot"]], ls=SERIES_DASH[row["slot"]],
                     lw=1.5, zorder=3)

    top.axhline(0.0, color=INK["grid"], lw=0.8, zorder=1)
    top.set_xlabel(r"separation  $\theta$  [degrees]")
    top.set_ylabel(r"$C(\theta)\,/\,C(0)$")
    top.set_xlim(0.0, 180.0)
    top.legend(frameon=False, loc="upper right", borderaxespad=0.0)

    bot.axhline(ACCEPTANCE, color=INK["muted"], lw=0.9, ls=(0, (2, 2)), zorder=2)
    bot.text(ELL_MIN + 0.3, ACCEPTANCE * 2.2,
             rf"acceptance  ${ACCEPTANCE:.0e}$".replace("e-12", r"\times10^{-12}"),
             fontsize=7.4, color=INK["muted"], va="bottom")
    bot.set_xlabel(r"multipole  $\ell$")
    bot.set_ylabel("round-trip\nresidual")
    bot.set_xlim(ELL_MIN, ELL_MAX)
    bot.set_ylim(1e-18, 1e-8)

    fig.suptitle("F4   The angular correlation function, and the transform that makes it",
                 x=0.012, y=0.962, ha="left", fontsize=10, color=INK["primary"])
    fig.text(
        0.012, 0.905,
        r"$C(\theta)=\sum_\ell\frac{2\ell+1}{4\pi}C_\ell P_\ell(\cos\theta)$, summed over "
        rf"${ELL_MIN}\leq\ell\leq{ELL_MAX}$ — the range F3 claims. The lower panel is"
        "\nthe Legendre round trip, which tests the transform and not the spectrum: "
        "the two share their $C_\\ell$.",
        ha="left", va="top", fontsize=7.6, color=INK["secondary"],
    )
    fig.text(
        0.012, 0.085,
        "Normalised to $C(0)$, so the comparison is of shape. Summing past "
        rf"$\ell={ELL_MAX}$ would draw multipoles this release"
        "\ndoes not stand behind, and a real-space curve hides which $\\ell$ "
        "contributed — so the restriction is made here, not in a caption.",
        ha="left", va="top", fontsize=7.2, color=INK["muted"],
    )
    return fig


def main() -> int:
    rows = compute()
    if not rows:
        print("FAIL  no spectra found in outputs/f3-angular-spectrum.csv")
        return 1

    out = ROOT / "outputs" / "f4-correlation.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# C(theta) summed over {ELL_MIN} <= l <= {ELL_MAX}, "
                 f"the range F3 claims\n")
        fh.write("model,theta_deg,c_theta\n")
        for row in rows:
            for t, c in zip(THETA_DEG, row["c_theta"]):
                fh.write(f"{row['label']},{t:.6f},{c:.12e}\n")
    print(f"wrote {out.relative_to(ROOT)}")

    for p in save_figure(draw(rows), "f4-correlation"):
        print(f"wrote {p.relative_to(ROOT)}")

    worst = 0.0
    for row in rows:
        w = float(np.max(row["residual"]))
        worst = max(worst, w)
        print(f"  {row['label']:16s} round-trip residual  max {w:.3e}")
    print(f"  acceptance {ACCEPTANCE:.0e}: {'PASS' if worst <= ACCEPTANCE else 'FAIL'}")
    return 0 if worst <= ACCEPTANCE else 1


if __name__ == "__main__":
    sys.exit(main())
