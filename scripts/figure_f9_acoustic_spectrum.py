#!/usr/bin/env python3
r"""F9 --- the normalised angular spectrum with the acoustic peaks.

    python scripts/figure_f9_acoustic_spectrum.py

**The figure v1.2.0 was promised.** The README's roadmap has said since v1.0.0
that *"at v1.2.0 the key figure of this README becomes the normalised angular
spectrum for CDM and ΛCDM, with the peaks --- the present Figure 3 moves to
second place"*. F3 is the almost-Friedmann--Lemaitre skeleton, claimed only to
$\ell\le20$ and drawn on a $k$ grid that stops short of the Silk scale. This is
the spectrum once it has structure in it.

**Three backgrounds, because the deliverable names them.** Decision **S1** makes
v1.0.0's deliverable *the CDM and ΛCDM angular power spectra*, and the external
comparison runs on `PLANCK_MODEL`; drawing two of the three and calling it the
key figure would leave the third asserted rather than shown.

**Shape, never amplitude.** Each spectrum is renormalised at $\ell=30$, as the
5b comparison is, because neither this bundle nor the external codes fixes $A_s$
the same way and an amplitude comparison would measure a normalisation.

**CAMB and CLASS are drawn as context and labelled as such** --- decision
**S4c**. They are not the gate, they are not a target, and the distance to them
is itemised in `provenance/CRITERION-5B-v1.md` rather than left for a reader to
eyeball off a log axis.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL,
    LCDM_MODEL,
    PLANCK_H,
    PLANCK_MODEL,
    PLANCK_N_S,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.angular import cl_covariant_route, d_ell  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment,
    coefficient_sets,
    transfer_by_rank,
)
from functions.plotting.style import (  # noqa: E402
    INK,
    SERIES,
    SERIES_DASH,
    save_figure,
    use_house_style,
)

VERSION = "v1.2.0"

#: Linear across the acoustic band, as `compare_criterion_5b.py` is and for the
#: same reason: the peaks sit near 200, 410 and 610, and a logarithmic grid
#: samples the first peak many times and the third twice.
ELLS = np.unique(np.concatenate([
    np.array([2, 4, 7, 11, 16, 22]),
    np.arange(30, 1001, 30),
]))

#: Linear at $dk=\pi/3$ to 1500. Linear is the rule, not a preference: a
#: logarithmic $k$ grid aliases the integrand at high $k$ however many points it
#: has. 1500 runs past the damping scale, which **T-32** requires.
K_COM = np.arange(0.05, 1500.0, np.pi / 3.0)

BACKGROUNDS = [
    ("CDM (Einstein-de Sitter)", CDM_MODEL, 0.0224, 0.5),
    (r"$\Lambda$CDM", LCDM_MODEL, 0.0224, 0.7),
    ("PLANCK_MODEL", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H),
]


def spectrum(background, omega_b_h2: float,
             hubble_h: float) -> dict[str, np.ndarray]:
    r"""$C_\ell$ in **both frames**, with the transfer function and Silk damping.

    `coefficient_sets` returns the Newtonian and the CDM coefficient triples
    from one solve, so carrying both costs a second projection and no second
    solution. **That is the point of (102) being carried with a generic $u^a$
    and specialised at the end rather than at the start**, and a key figure for
    a frame-covariance release that drew only one frame would be showing the
    thing the release is not about.
    """
    gamma = shape_parameter(background.omega_m, hubble_h)
    env = build_environment(
        float(K_COM.max()), omega_m=background.omega_m,
        omega_lambda=background.omega_lambda, omega_r=background.omega_r,
        omega_b_h2=omega_b_h2, transfer_gamma=gamma, hubble_h=hubble_h,
        f_2=F2_DEFAULT)
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(K_COM.max() * (env.background.eta_0 - env.eta[0])) + 20.0)
    transfer = {"newtonian": np.zeros((ELLS.size, K_COM.size)),
                "cdm": np.zeros((ELLS.size, K_COM.size))}
    for j, k in enumerate(K_COM):
        sets = dict(zip(("newtonian", "cdm"), coefficient_sets(float(k), env)))
        for name, coefficients in sets.items():
            transfer[name][:, j] = transfer_by_rank(
                ELLS, float(k), coefficients, env, table)[-1]
    power = primordial_power(K_COM, n_s=PLANCK_N_S, amplitude=1.0)
    return {name: np.array([cl_covariant_route(int(l), K_COM, block[i], power)
                            for i, l in enumerate(ELLS)])
            for name, block in transfer.items()}


def shape(ell: np.ndarray, cl: np.ndarray) -> np.ndarray:
    d = d_ell(ell, cl)
    return d / np.interp(30.0, ell, d)


def reference(name: str) -> tuple[np.ndarray, np.ndarray]:
    ell, cl = [], []
    with (ROOT / "reference" / f"{name}-tt-{VERSION}.csv").open(encoding="utf-8") as fh:
        for row in csv.reader(fh):
            if not row or row[0].startswith("#") or row[0] == "ell":
                continue
            ell.append(int(row[0])); cl.append(float(row[1]))
    return np.array(ell), np.array(cl)


def first_peak(ell: np.ndarray, s: np.ndarray) -> float:
    r"""The first acoustic peak, **interpolated rather than read off the grid**.

    The $\ell$ grid steps by 30 across the acoustic band, so the grid maximum
    can only ever land on a multiple of 30 --- which would report the peak as
    150 or 180 and nothing between, an apparent precision the sampling does not
    have. A parabola through the maximum and its two neighbours gives the
    vertex to a fraction of a step, which is what the curve actually says.
    """
    band = (ell >= 80) & (ell <= 400)
    x, y = ell[band].astype(float), s[band]
    i = int(np.argmax(y))
    if i == 0 or i == x.size - 1:
        return float(x[i])
    denom = y[i - 1] - 2.0 * y[i] + y[i + 1]
    if denom == 0.0:
        return float(x[i])
    offset = 0.5 * (y[i - 1] - y[i + 1]) / denom
    return float(x[i] + offset * (x[i + 1] - x[i]))


def label_for(name: str, curves: dict) -> str:
    """Say in the legend that CLASS lies underneath CAMB, because it does.

    The two agree to 0.3% across the whole range --- which is the *point*, since
    that mutual difference is the scale any external comparison must be read
    against. Drawn, it makes CLASS invisible, and an invisible curve with a
    legend entry reads as a plotting failure rather than as a result. So the
    legend states the coincidence and the number.
    """
    if name != "CLASS":
        return f"{name} — context (S4c)"
    gap = float(np.max(np.abs(curves["CLASS"] - curves["CAMB"])
                       / np.abs(curves["CAMB"])))
    return f"CLASS — under CAMB, agreeing to {gap:.1%}"


def draw(curves, peaks, frames, gaps) -> int:
    use_house_style()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2), sharey=True)

    # (a) the deliverable: three backgrounds, CDM frame, external codes dashed.
    ax = axes[0]
    for i, (label, _, _, _) in enumerate(BACKGROUNDS, start=1):
        ax.plot(ELLS, curves[label], color=SERIES[i], lw=1.8, label=label)
    for j, name in enumerate(("CAMB", "CLASS"), start=3):
        ax.plot(ELLS, curves[name], color=INK["muted"], lw=1.2,
                ls=SERIES_DASH[j], label=label_for(name, curves))
    ax.axvline(peaks["PLANCK_MODEL"], color=INK["muted"], lw=0.8,
               ls=SERIES_DASH[4], zorder=1)
    ax.annotate(
        f"first peak $\\ell\\simeq{peaks['PLANCK_MODEL']:.0f}$\n"
        f"CAMB $\\ell\\simeq{peaks['CAMB']:.0f}$",
        xy=(0.985, 0.30), xycoords="axes fraction", ha="right", va="top",
        fontsize=7.2, color=INK["secondary"])
    ax.set_title("(a) the spectrum, CDM frame", fontsize=9, loc="left")
    ax.set_ylabel(r"$D_\ell/D_{30}$  (shape, renormalised at $\ell=30$)")

    # (b) the same spectra in BOTH frames. (102) is carried with a generic u^a
    # and specialised at the end, so both frames come from one solve --- the
    # thing a gauge-fixed treatment cannot exhibit, drawn rather than asserted.
    ax = axes[1]
    for i, (label, _, _, _) in enumerate(BACKGROUNDS, start=1):
        ax.plot(ELLS, frames[label]["cdm"], color=SERIES[i], lw=1.8,
                label=f"{label} — CDM frame")
        ax.plot(ELLS, frames[label]["newtonian"], color=SERIES[i], lw=1.1,
                ls=SERIES_DASH[2], alpha=0.85,
                label=f"{label} — Newtonian frame")
    worst = max(np.median(g) for g in gaps.values())
    ax.annotate(
        "one solve, frame chosen at the end\n"
        f"median frame gap up to {worst:.0%}",
        xy=(0.985, 0.30), xycoords="axes fraction", ha="right", va="top",
        fontsize=7.2, color=INK["secondary"])
    ax.set_title("(b) the same spectra, both frames", fontsize=9, loc="left")

    for ax in axes:
        ax.set_xscale("log")
        ax.set_xlabel(r"multipole $\ell$")
        ax.legend(fontsize=6.6, frameon=False, loc="upper left",
                  handlelength=2.6, borderaxespad=0.4)
    fig.tight_layout()
    for path in save_figure(fig, "f9-acoustic-spectrum", VERSION):
        print(f"wrote {path.relative_to(ROOT)}")

    return 0


def load_csv() -> tuple[np.ndarray, dict, dict]:
    """Re-read what the expensive half already produced.

    **The computation and the picture are separable and must stay that way.**
    Two plotting bugs --- a dash tuple and a palette key --- each surfaced after
    the last number had been produced, and the first of them threw the numbers
    away. `--replot` exists so the third one costs seconds.
    """
    path = ROOT / "outputs" / "f9-acoustic-spectrum.csv"
    rows = [r for r in csv.reader(path.open(encoding="utf-8"))
            if r and not r[0].startswith("#")]
    header, body = rows[0][1:], np.array([[float(v) for v in r] for r in rows[1:]])
    ells = body[:, 0].astype(int)
    columns = {name: body[:, i + 1] for i, name in enumerate(header)}
    frames = {label: {frame: columns[f"{label}|{frame}"]
                      for frame in ("cdm", "newtonian")}
              for label, _, _, _ in BACKGROUNDS}
    curves = {label: frames[label]["cdm"] for label, _, _, _ in BACKGROUNDS}
    curves.update({n: columns[n] for n in ("CAMB", "CLASS")})
    return ells, curves, frames


def main() -> int:
    global ELLS
    print("F9  the normalised angular spectrum with the acoustic peaks")
    print(f"    ells {ELLS.min()}..{ELLS.max()} ({ELLS.size}), "
          f"k to {K_COM.max():.0f} ({K_COM.size} modes), f_2 = {F2_DEFAULT}")

    if "--replot" in sys.argv:
        ELLS, curves, frames = load_csv()
        peaks = {n: first_peak(ELLS, c) for n, c in curves.items()}
        gaps = {label: np.abs(frames[label]["cdm"] - frames[label]["newtonian"])
                       / np.abs(frames[label]["cdm"])
                for label, _, _, _ in BACKGROUNDS}
        print("    replotting from outputs/f9-acoustic-spectrum.csv")
        return draw(curves, peaks, frames, gaps)

    curves, peaks, frames, gaps = {}, {}, {}, {}
    for label, background, omega_b_h2, hubble_h in BACKGROUNDS:
        both = spectrum(background, omega_b_h2, hubble_h)
        frames[label] = {n: shape(ELLS, cl) for n, cl in both.items()}
        curves[label] = frames[label]["cdm"]
        peaks[label] = first_peak(ELLS, curves[label])
        gaps[label] = (np.abs(frames[label]["cdm"] - frames[label]["newtonian"])
                       / np.abs(frames[label]["cdm"]))
        print(f"    {label:26s} first peak l={peaks[label]};  frame gap "
              f"median {np.median(gaps[label]):.1%} worst {gaps[label].max():.1%}")

    for name in ("camb", "class"):
        ell_ref, cl_ref = reference(name)
        s = np.interp(ELLS, ell_ref, shape(ell_ref, cl_ref))
        curves[name.upper()] = s
        peaks[name.upper()] = first_peak(ELLS, s)
        print(f"    {name.upper():26s} first peak at l={peaks[name.upper()]}")

    # **The data lands before the picture does.** A dash-style type error
    # once threw away three backgrounds of computation at the plotting
    # call, forty-five minutes after the last number was produced. The
    # CSV is the expensive artefact; the figure is cheap and redrawable.
    out = ROOT / "outputs" / "f9-acoustic-spectrum.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# shape, D_l renormalised at l=30, both frames. "
                 "CAMB and CLASS are context (S4c).\n")
        cols = [(f"{b[0]}|{frame}", frames[b[0]][frame])
                for b in BACKGROUNDS for frame in ("cdm", "newtonian")]
        cols += [(n, curves[n]) for n in ("CAMB", "CLASS")]
        fh.write("ell," + ",".join(c.replace(",", ";") for c, _ in cols) + "\n")
        for i, l in enumerate(ELLS):
            fh.write(f"{int(l)}," + ",".join(f"{v[i]:.9e}" for _, v in cols) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")

    return draw(curves, peaks, frames, gaps)


if __name__ == "__main__":
    sys.exit(main())
