#!/usr/bin/env python3
r"""F10 --- when the spectrum is laid down. $C_\ell$ against conformal time.

**The PI's figure, 2026-10-24.** Every other instrument in this bundle
measures a *finished* spectrum. This one shows it being built, and it is the
only artefact here in which the plateau's defect is visible at all.

WHAT IT DRAWS
-------------
For each multipole, the fraction of today's $C_\ell$ already in place at
conformal time $\eta$ --- the bulk accumulated to $\eta$, plus the boundary
terms, which are emitted at $\eta_*$ and are present in every slice. Both
frames, three backgrounds, normalised per curve so the shape is the subject
rather than the growth.

The horizontal axis is $\log(\eta-\eta_*)$ because the visibility is narrow:
on a linear axis 99% of the panel is free streaming, where by construction
nothing is laid down.

WHAT IT SHOWS, AND IT IS THE RESULT RATHER THAN THE ILLUSTRATION
-----------------------------------------------------------------
**Every curve reaches 1 within 1% of the conformal span and is flat
afterwards.** The spectrum is finished at recombination.

That is a defect, and the figure is the only place it is visible:

  * On `PLANCK_MODEL` and $\Lambda$CDM the late integrated Sachs--Wolfe
    effect must deposit $O(0.1)$ of $C_2$ **after** the visibility closes.
    It deposits **zero**.
  * On Einstein--de~Sitter $\Phi$ is exactly constant (Appendix~G), so the
    late share must be **exactly** zero --- and it is. **That null control is
    what makes the PLANCK reading a defect rather than a numerical artefact**:
    if something other than the weight were wrong, EdS would not come out
    exactly zero.

The mechanism is B-17 discrepancy (i). (102) carries the bulk bracket at
$\mathcal V\mathcal D$ where the exact by-parts wants $W$; $\mathcal
V=W\kappa'$ is sharply peaked at $\eta_*$ and is zero afterwards, so every
late-time source is multiplied by zero. **The late ISW is not missing from
the formalism --- it is present at rank one and annihilated by the weight.**

WHY THIS AND NOT ANOTHER GATE
-----------------------------
$\ell_{\rm peak}$ and the median contributing $k$ are scalar summaries of the
endpoint. **The plateau's missing power is a defect in time**, so neither can
see it, and three pre-registered predictions were scored against them before
this was drawn. A figure is the right instrument when the defect is a shape.

**F9 is not superseded by this.** F9 shows *where* the power lands in $\ell$;
F10 shows *when* it was laid down. The peak position and the missing plateau
are different failures and each has its own figure.

GATE
----
The $\eta_0$ column must reproduce the released quadrature exactly --- it is
the same integral, decomposed. Asserted at $10^{-9}$, measured at $10^{-12}$.

``--replot``
------------
The computation is four minutes of quadrature and the harness runs on every
pass, so F10 follows F9's split: the accumulation lands in
`outputs/f10-formation-surface.csv`, which is committed, and ``--replot``
redraws the committed picture from it in a second. **The CSV carries a digest
of the code that produced it** and ``--replot`` refuses to redraw numbers this
tree did not compute --- finding **T-54**, where a cache that could not say
*who made this* printed CLEAN over a two-day-old spectrum.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, LCDM_MODEL, PLANCK_H, PLANCK_MODEL, PLANCK_N_S,
    PLANCK_OMEGA_B_H2)
from functions.plotting.style import (  # noqa: E402
    INK, SERIES, SERIES_DASH, save_figure, use_house_style)
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

from _fingerprint import source_fingerprint as _digest  # noqa: E402

VERSION = "v1.3.0"
STEM = "f10-formation-surface"

#: **Low granularity in time, as the PI asked.** Sixteen slices is enough to
#: show that every curve is a step at $\eta_*$ and flat afterwards, and the
#: cost is linear in neither --- the accumulation is one pass (D30) and the
#: slice count only sets how finely it is sampled.
N_SLICES = 16

#: The plateau, the first peak, and one point past it. The damping tail is
#: F9's: it arrives with everything else and adds nothing here.
ELLS = np.array([2, 5, 10, 30, 100, 200])

K_MAX = 300.0
FRAMES = ("newtonian", "cdm")

BACKGROUNDS = [
    ("CDM (Einstein–de Sitter)", CDM_MODEL, 0.0224, 0.5, 0.48),
    ("ΛCDM", LCDM_MODEL, 0.0224, 0.5, 0.48),
    ("Planck 2018", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H, None),
]


def _accumulate(bg, obh2, h, gamma):
    """Fraction of the final $C_\\ell$ in place at each slice, per frame."""
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
    worst = 0.0
    dk = k_com[1] - k_com[0]
    for j, k in enumerate(k_com):
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        common = dict(table=table, weight=env.weight, diffusion=diffusion,
                      damping_total=diffusion, eta_star=eta_star,
                      eta_floor=float(env.eta[0]), visibility=env.visibility,
                      eta_0=eta_0)
        for f in FRAMES:
            s = sets[f]
            res = integral_solution(
                ELLS, coefficients=s.coefficients, c1_prime=s.c1_prime,
                c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
                c2_prime=s.c2_prime, eta_slices=sl, **common)
            worst = max(worst, float(np.max(
                np.abs(res.partial_bulk[:, -1] - res.integrated)
                / np.maximum(np.abs(res.integrated), 1e-300))))
            boundary = (res.boundary_scalar + res.boundary_shear)[:, None]
            acc[f] += (k ** 2 * power[j]) * (res.partial_bulk + boundary) ** 2 * dk
    return acc, (sl - eta_star) / span, worst


CSV = ROOT / "outputs" / "f10-formation-surface.csv"


def source_fingerprint() -> str:
    """A digest of the code that produced the numbers, for the CSV header.

    **T-54's guard, over T-129's declared set.** The first version here copied
    F9's "every `functions.*` module in `sys.modules`" and that is a property
    of the code path: `peebles` is imported lazily inside `build_environment`,
    so the compute branch hashed it and the replot branch did not. `_fingerprint`
    walks `functions/` from disk instead, so the two branches agree and neither
    is blind to a lazily-imported module.
    """
    return _digest(__file__)


def _write_csv(emitted: list[tuple]) -> None:
    """The accumulation, written beside the figure.

    Re-rendering a layout fix should not recompute four minutes of quadrature
    (**T-127**), and the house pattern --- `outputs/f9-acoustic-spectrum.csv`
    --- already expects a figure to emit the data it drew.
    """
    import csv as _csv

    with CSV.open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"# sources: {source_fingerprint()}\n")
        w = _csv.writer(fh)
        w.writerow(["background", "frame", "ell", "eta_frac", "fraction"])
        for label, xs, accs in emitted:
            for f in FRAMES:
                for i, l in enumerate(ELLS):
                    fin = accs[f][i][-1]
                    if fin <= 0:
                        continue
                    for xv, yv in zip(xs, accs[f][i] / fin):
                        w.writerow([label, f, int(l), f"{xv:.6e}",
                                    f"{yv:.6f}"])


def _read_csv() -> list[tuple]:
    """The emitted accumulation, back in the shape `_draw` wants.

    Already-normalised fractions come back as the curves themselves, so
    `_draw`'s per-curve normalisation divides by a final value of 1 and is a
    no-op. The alternative --- a second normalisation convention on the replot
    path --- is exactly the drift S8 forbids.
    """
    import csv as _csv

    with CSV.open(newline="", encoding="utf-8") as fh:
        stamped = fh.readline()
        rows = list(_csv.DictReader(fh))
    stamped = (stamped.split(":", 1)[1].strip()
               if stamped.startswith("# sources:") else "")
    current = source_fingerprint()
    if stamped != current:
        raise SystemExit(
            f"    FAIL  the cached CSV was produced by different code "
            f"(stamped {stamped or 'nothing'}, this tree {current}).\n"
            f"          --replot cannot redraw numbers it did not compute.\n"
            f"          Run `python scripts/figure_f10_formation_surface.py`\n"
            f"          with no arguments to recompute. Finding T-54.")
    out = []
    for label, _, _, _, _ in BACKGROUNDS:
        sel = [r for r in rows if r["background"] == label]
        if not sel:
            raise SystemExit(f"    FAIL  {CSV.name} has no rows for {label}")
        xs = np.array(sorted({float(r["eta_frac"]) for r in sel}))
        acc = {f: np.zeros((ELLS.size, xs.size)) for f in FRAMES}
        for f in FRAMES:
            for i, l in enumerate(ELLS):
                pts = sorted(((float(r["eta_frac"]), float(r["fraction"]))
                              for r in sel
                              if r["frame"] == f and int(r["ell"]) == int(l)))
                if len(pts) != xs.size:
                    raise SystemExit(
                        f"    FAIL  {CSV.name}: {label}/{f}/l={int(l)} has "
                        f"{len(pts)} slices, the background has {xs.size}")
                acc[f][i] = np.array([p[1] for p in pts])
        out.append((label, xs, acc))
    return out


def _draw(emitted: list[tuple]) -> plt.Figure:
    """The picture, from accumulations that were computed or were read back."""
    use_house_style()
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.0), sharex=True,
                             sharey=True)
    for col, (label, x, acc) in enumerate(emitted):
        for row, frame in enumerate(FRAMES):
            ax = axes[row, col]
            for i, l in enumerate(ELLS):
                fin = acc[frame][i][-1]
                if fin <= 0:
                    continue
                ax.plot(np.maximum(x, 1e-5), acc[frame][i] / fin,
                        color=SERIES[1 + i % 4],
                        linestyle=SERIES_DASH[1 + i % 4],
                        linewidth=1.1, label=rf"$\ell={int(l)}$")
            ax.set_xscale("log")
            ax.axhline(1.0, color=INK["grid"], linewidth=0.6, zorder=0)
            if row == 0:
                ax.set_title(label, fontsize=9)
            if col == 0:
                ax.set_ylabel(f"{frame}\n" r"fraction of final $C_\ell$",
                              fontsize=8)
            if row == 1:
                ax.set_xlabel(r"$(\eta-\eta_*)/(\eta_0-\eta_*)$", fontsize=8)
    # Legend outside the data. It sat over the l=2 curve in the first
    # rendering, which V12 caught by looking rather than by any check.
    axes[0, 0].legend(fontsize=6, frameon=False, loc="upper left",
                      bbox_to_anchor=(0.0, -0.02), ncol=3,
                      handlelength=1.6, columnspacing=1.0)
    fig.suptitle("F10  when the spectrum is laid down — every curve is "
                 "complete at recombination", fontsize=10)
    # Two short lines, not one long one: the single line overran the figure
    # at both ends and was clipped.
    fig.text(0.5, 0.040,
             "A correct assembly deposits ~10% of $C_2$ after the visibility "
             "closes on ΛCDM and Planck — the late ISW —",
             ha="center", fontsize=7.5, color=INK["muted"])
    fig.text(0.5, 0.012,
             "and exactly none on Einstein–de Sitter, where $\\Phi$ is "
             "constant. All three read zero: B-17 (i), the bracket at "
             "$\\mathcal{V}$.",
             ha="center", fontsize=7.5, color=INK["muted"])
    fig.tight_layout(rect=(0, 0.075, 1, 0.965))
    return fig


def main() -> int:
    print(__doc__.split("WHAT IT DRAWS")[0])
    if "--replot" in sys.argv:
        print(f"    replotting from {CSV.relative_to(ROOT)}")
        for p in save_figure(_draw(_read_csv()), STEM, VERSION):
            print(f"    wrote {p.relative_to(ROOT)}")
        return 0

    gate = 0.0
    emitted: list[tuple] = []
    for label, bg, obh2, h, gamma in BACKGROUNDS:
        print(f"    {label} …", flush=True)
        acc, x, worst = _accumulate(bg, obh2, h, gamma)
        gate = max(gate, worst)
        emitted.append((label, x, acc))

    print(f"\n    GATE  eta_0 column vs the released quadrature: "
          f"worst rel {gate:.2e}  "
          f"{'PASS' if gate < 1e-9 else '**FAIL**'}")
    if gate >= 1e-9:
        print("    The accumulation does not decompose the released integral; "
              "neither the figure nor the CSV is written.")
        return 1

    _write_csv(emitted)
    print(f"    wrote {CSV.relative_to(ROOT)}")
    for p in save_figure(_draw(emitted), STEM, VERSION):
        print(f"    wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
