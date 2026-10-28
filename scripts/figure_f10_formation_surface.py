#!/usr/bin/env python3
r"""F10 --- the angular autocorrelation as it forms: $C_\ell(\eta)$, a surface.

**The PI's figure, respecified 2026-10-25.** The first version of this file
drew six multipoles' accumulation against $\eta$ and called itself a surface.
**It was not one.** It sampled the surface along six lines of constant $\ell$
and threw the $\ell$ axis away, which is the axis the plateau and the acoustic
peaks live on. The question asked was *how the spectrum evolves through
conformal time*, and the answer to that is a spectrum at a sequence of times.

WHAT IT DRAWS
-------------
**(a) The autocorrelation at a sequence of conformal times.** $D_\ell$ against
$\ell$, one curve per epoch, from before decoupling through $\eta_\ast$ to
today. This is the picture the PI asked for in three parts --- *just before
decoupling, at decoupling, after decoupling* --- with the intermediate epochs
drawn so the three are read as a progression rather than as three facts.

**(b) The surface itself.** $C_\ell(\eta)/C_\ell(\eta_0)$ over the full
$(\ell,\eta)$ plane. Where panel (a) is read along $\ell$, this is read along
$\eta$: a correct assembly has structure in the upper band, where the late
integrated Sachs--Wolfe effect deposits power at low $\ell$ long after the
visibility has closed.

WHY A SPECTRUM AT EACH TIME AND NOT A FRACTION
----------------------------------------------
A normalised fraction answers *"how much of this multipole is in place?"* and
cannot answer *"what shape is the spectrum right now?"*. The plateau is a
statement about $\ell$-dependence at fixed $\eta$, so it is invisible to any
per-$\ell$ normalisation --- which is what the first version of this figure
did, and why it could show the defect only as a flat line rather than as the
missing shape.

THE LOWER LIMIT IS NOT $\eta_\ast$
----------------------------------
(102)'s bulk runs from the **recombination start** (T-58), not from
$\eta_\ast$, so *before decoupling* is a real epoch here with real
accumulation in it rather than an empty panel. The first slice is the grid's
own floor and the curve there is what the integral has built by then.

GATE
----
The $\eta_0$ column must reproduce the released quadrature --- it is the same
integral, decomposed. Asserted at $10^{-9}$.

``--replot``
------------
The accumulation lands in `outputs/f10-formation-surface.csv`, stamped with a
digest of the code that produced it, and ``--replot`` refuses to redraw
numbers this tree did not compute (**T-54**, **T-129**).
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
    PLANCK_H, PLANCK_MODEL, PLANCK_N_S, PLANCK_OMEGA_B_H2)
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
CSV = ROOT / "outputs" / "f10-formation-surface.csv"
# placeholder; --high-res retargets both below once ELLS is settled

#: The $\ell$ axis, and it must carry the plateau AND the first peak or the
#: figure cannot show the thing it is about. Dense below 30 where the plateau
#: is a shape, then stepping to past the first acoustic peak.
ELLS = np.unique(np.concatenate([
    np.array([2, 3, 4, 5, 7, 9, 12, 16, 20, 25, 30]),
    np.arange(40, 301, 20)]))

#: 400 reaches $\ell=300$ on PLANCK with room. Not F9's 1500: the damping
#: tail is F9's subject and it arrives with everything else.
K_MAX = 400.0

#: **`--high-res`, 2026-10-26, at the PI's request.** The released axis stops
#: at $\ell=300$, and on `PLANCK_MODEL` the released first peak is at
#: $\ell=266.6$ --- so the primary is the *last point on the axis* and the
#: secondaries are not on the picture at all. From $\ell_A=272.18$ they fall
#: at $\ell\simeq539$ and $\ell\simeq811$.
#:
#: This extends the axis past both and raises $k_{\max}$ to F9's 1500 so the
#: modes that build them are present. It is **not** the released F10: the
#: released grid stays exactly as it is, so the committed artefact and its
#: gate are untouched, and this writes to its own stem.
#:
#: **What it will show, said before it runs.** A peak series at the
#: *displaced* spacing, not CAMB's --- the released primary sits at
#: $0.980\,\ell_A$ against CAMB's $0.757$, because the radiation driving
#: (**A-3**) is not wired. Three maxima at the wrong spacing is the first
#: acoustic series this bundle has drawn and is **not** agreement.
if "--high-res" in sys.argv:
    ELLS = np.unique(np.concatenate([
        np.array([2, 3, 4, 5, 7, 9, 12, 16, 20, 25, 30]),
        np.arange(40, 301, 10),
        np.arange(310, 921, 15)]))
    K_MAX = 1500.0
    STEM = STEM + "-high-res"
    CSV = ROOT / "outputs" / "f10-formation-surface-high-res.csv"

#: **Low granulation in time, as the PI specified.** Fourteen epochs is
#: enough to read a progression and few enough that each curve is
#: distinguishable in panel (a).
N_SLICES = 14

#: The filled levels and the subset that carries a labelled line.
#: **Twenty-one filled levels and five labelled**, chosen so the eye reads
#: *when each fifth of the power arrives* rather than estimating a grey ramp
#: against a colourbar. 0.99 is included deliberately: the whole question the
#: panel answers is whether anything arrives after the visibility closes, and
#: the difference between 0.99 and 1.00 is the entire late integrated
#: Sachs--Wolfe budget.
LEVELS = np.linspace(0.0, 1.0, 21)
LABELLED = (0.25, 0.50, 0.75, 0.90, 0.99)

FRAME = "cdm"
FRAMES = ("newtonian", "cdm")

#: The three the PI named, located once the grid exists and annotated by
#: name rather than by number, because *"at decoupling"* is the physical
#: statement and $\eta_\ast=0.0606$ is not.
NAMED = ("just before decoupling", "at decoupling", "after decoupling")


def _accumulate():
    r"""$C_\ell$ at every slice, for both frames. One pass in $k$."""
    env = build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2,
        transfer_gamma=shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H),
        hubble_h=PLANCK_H, f_2=F2_DEFAULT, line_of_sight_weight="printed")
    eta_star, eta_0 = float(env.eta_star), float(env.background.eta_0)
    floor = float(env.eta[0])

    # From the recombination START (T-58), through eta_*, to today. Linear
    # across recombination so the three named epochs are resolved, then
    # geometric so the free-streaming era is sampled at all.
    pre = np.linspace(floor, eta_star, 4)
    post = eta_star + np.geomspace(
        (eta_0 - eta_star) * 1e-4, eta_0 - eta_star, N_SLICES - 4)
    sl = np.concatenate([pre, post])

    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, eta_0 - eta_star))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (eta_0 - floor)) + 20.0)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)

    acc = {f: np.zeros((ELLS.size, sl.size)) for f in FRAMES}
    gate, dk = 0.0, k_com[1] - k_com[0]
    for j, k in enumerate(k_com):
        sets = dict(zip(FRAMES, coefficient_sets(float(k), env)))
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        common = dict(table=table, weight=env.weight, diffusion=diffusion,
                      damping_total=diffusion, eta_star=eta_star,
                      eta_floor=floor, visibility=env.visibility, eta_0=eta_0)
        for f in FRAMES:
            s = sets[f]
            res = integral_solution(
                ELLS, coefficients=s.coefficients, c1_prime=s.c1_prime,
                c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
                c2_prime=s.c2_prime, eta_slices=sl, **common)
            # **Normalised by the largest transfer at this $k$, not pointwise
            # --- finding T-158, 2026-10-26.**
            #
            # This read `|difference| / |integrated|` element by element, and
            # at $K_{\max}=400$ with $\ell\le300$ it returned $4.6\times
            # 10^{-13}$ and looked exact. The first high-resolution run failed
            # it at $1.75\times10^{-8}$ --- and the decomposition had not
            # degraded at all. **The transfer has zeros**, and above
            # $\ell\simeq300$ at high $k$ they are deep: the worst case found
            # is $\ell=40$, $k=1176$, where the absolute difference is
            # $1.4\times10^{-20}$ against an $|{\rm integrated}|$ of
            # $6.1\times10^{-10}$. Machine precision divided by a number
            # passing through zero.
            #
            # Raising the slice count changes nothing --- 14, 24, 40 and 64
            # all return the same $10^{-13}$ --- which is what rules out a
            # resolution limit and leaves the metric.
            #
            # Measured against the largest transfer at the same $k$, that same
            # worst case is $3.5\times10^{-13}$: **the gate's own number at
            # $K_{\max}=400$, unchanged.** So this is not a loosened threshold,
            # it is a denominator that cannot vanish. The threshold is
            # untouched.
            scale = max(float(np.max(np.abs(res.integrated))), 1e-300)
            gate = max(gate, float(np.max(
                np.abs(res.partial_bulk[:, -1] - res.integrated))) / scale)
            boundary = (res.boundary_scalar + res.boundary_shear)[:, None]
            acc[f] += (k ** 2 * power[j]) * (res.partial_bulk + boundary) ** 2 * dk
        if j % 200 == 0:
            print(f"      k {k:7.1f} of {K_MAX:.0f}", flush=True)
    return acc, sl, eta_star, eta_0, floor, gate


def _write_csv(acc, sl, eta_star, eta_0, floor):
    import csv as _csv

    with CSV.open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"# sources: {_digest(__file__)}\n")
        fh.write(f"# eta_star {eta_star:.9e}  eta_0 {eta_0:.9e}  "
                 f"floor {floor:.9e}\n")
        w = _csv.writer(fh)
        w.writerow(["frame", "ell", "eta", "c_ell"])
        for f in FRAMES:
            for i, l in enumerate(ELLS):
                for j, e in enumerate(sl):
                    w.writerow([f, int(l), f"{e:.9e}", f"{acc[f][i, j]:.9e}"])


def _read_csv():
    import csv as _csv

    with CSV.open(newline="", encoding="utf-8") as fh:
        stamped = fh.readline()
        meta = fh.readline().split()
        rows = list(_csv.DictReader(fh))
    stamped = (stamped.split(":", 1)[1].strip()
               if stamped.startswith("# sources:") else "")
    if stamped != _digest(__file__):
        raise SystemExit(
            f"    FAIL  the cached CSV was produced by different code "
            f"(stamped {stamped or 'nothing'}, this tree {_digest(__file__)}).\n"
            "          --replot cannot redraw numbers it did not compute.\n"
            "          Rerun with no arguments. Finding T-54.")
    eta_star, eta_0, floor = float(meta[2]), float(meta[4]), float(meta[6])
    sl = np.array(sorted({float(r["eta"]) for r in rows}))
    acc = {f: np.zeros((ELLS.size, sl.size)) for f in FRAMES}
    idx = {float(e): j for j, e in enumerate(sl)}
    ell_idx = {int(l): i for i, l in enumerate(ELLS)}
    for r in rows:
        acc[r["frame"]][ell_idx[int(r["ell"])], idx[float(r["eta"])]] = \
            float(r["c_ell"])
    return acc, sl, eta_star, eta_0, floor


def _d_ell(c):
    return ELLS * (ELLS + 1.0) * c / (2.0 * np.pi)


def _draw(acc, sl, eta_star, eta_0, floor):
    use_house_style()
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6))

    # --- (a) the autocorrelation at a sequence of epochs -------------------
    ax = axes[0]
    a = acc[FRAME]
    final = _d_ell(a[:, -1])
    norm = np.max(final) if np.max(final) > 0 else 1.0
    # The three the PI named, plus the rest as context.
    i_before, i_at = 1, 3
    for j, e in enumerate(sl):
        d = _d_ell(a[:, j]) / norm
        if not np.any(d > 0):
            continue
        if j == i_before:
            kw = dict(color=SERIES[1], linestyle=SERIES_DASH[2], lw=1.7,
                      label="just before decoupling", zorder=5)
        elif j == i_at:
            kw = dict(color=SERIES[1], linestyle=SERIES_DASH[1], lw=2.0,
                      label=r"at decoupling, $\eta_\ast$", zorder=6)
        elif j == sl.size - 1:
            kw = dict(color=SERIES[1], linestyle=SERIES_DASH[3], lw=2.0,
                      label=r"today, $\eta_0$", zorder=6)
        else:
            kw = dict(color=SERIES[4], lw=0.8, alpha=0.9, zorder=2)
        ax.plot(ELLS, d, **kw)
    ax.set_xscale("log")
    ax.set_xlabel(r"$\ell$", fontsize=9)
    ax.set_ylabel(r"$D_\ell$, normalised to its maximum today", fontsize=8.5)
    ax.set_title("(a)  the autocorrelation, epoch by epoch", fontsize=9)
    ax.legend(fontsize=7, frameon=False, loc="upper left")

    # --- (b) the surface ---------------------------------------------------
    ax = axes[1]
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = a / np.where(a[:, -1:] > 0, a[:, -1:], np.nan)
    x = (sl - eta_star) / (eta_0 - eta_star)
    # A symlog abscissa: recombination is a sliver of the span and a linear
    # axis would spend the panel on free streaming, where nothing is added.
    #
    # **Filled contours, not `pcolormesh` --- the PI's respecification,
    # 2026-10-27.** The top-down mesh spent most of its area rendering a
    # plateau at $1.0$, with every gradient the figure is about crammed into
    # one narrow band beside $\eta_\ast$. A grey ramp also makes *when* each
    # fraction arrives something the reader has to estimate against a
    # colourbar.
    #
    # Contours put ink where the gradient is and nowhere else, and the
    # labelled lines let the panel **state** its fractions instead of
    # requiring them to be read off a scale. A 3-D surface was considered and
    # rejected for the same reason the mesh failed: a flat tabletop with a
    # cliff at one edge spends the plot on the region where nothing happens,
    # and any viewing angle that shows the cliff hides part of it.
    field = np.clip(frac, 0.0, 1.0)
    mesh = ax.contourf(x, ELLS, field, levels=LEVELS,
                       cmap="Greys", vmin=0.0, vmax=1.0, extend="neither")
    lines = ax.contour(x, ELLS, field, levels=LABELLED,
                       colors=INK["primary"], linewidths=0.7)
    ax.clabel(lines, fmt=lambda v: f"{v:.2f}", fontsize=6.5, inline=True)
    ax.set_xscale("symlog", linthresh=1e-4)
    ax.set_yscale("log")
    ax.axvline(0.0, color=INK["grid"], lw=0.8)
    ax.set_xlabel(r"$(\eta-\eta_\ast)/(\eta_0-\eta_\ast)$", fontsize=9)
    ax.set_ylabel(r"$\ell$", fontsize=9)
    ax.set_title(r"(b)  $C_\ell(\eta)/C_\ell(\eta_0)$, the surface",
                 fontsize=9)
    cb = fig.colorbar(mesh, ax=ax, pad=0.02)
    cb.set_label("fraction of today's value", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)

    fig.suptitle("F10  the angular autocorrelation as it forms — Planck 2018, "
                 "CDM frame", fontsize=10)
    fig.text(0.5, 0.015,
             # **The colour word was inverted --- finding T-161.** `cmap` is
             # `Greys` with `vmin=0, vmax=1`, so the fraction of today's value
             # reads **1.0 as BLACK**. The band to the right of recombination
             # is therefore black, meaning every multipole is already at its
             # final value; the caption said *white*, which on this colourbar
             # means the opposite — nothing accumulated at all. The physical
             # claim after the colon was correct throughout, which is why it
             # survived every reading: a reader who trusted the sentence got
             # the right physics and a reader who trusted the picture got the
             # right physics, and only someone checking one against the other
             # would see them disagree.
             "Panel (b) is uniformly black to the right of recombination on "
             "every row — every multipole already at today's value — so "
             "nothing is deposited after the visibility closes, where the "
             "late ISW must deposit ~10% of $C_2$.",
             ha="center", fontsize=7.5, color=INK["muted"])
    fig.tight_layout(rect=(0, 0.055, 1, 0.94))
    return fig


def main() -> int:
    print(__doc__.split("WHAT IT DRAWS")[0])
    if "--replot" in sys.argv:
        print(f"    replotting from {CSV.relative_to(ROOT)}")
        for p in save_figure(_draw(*_read_csv()), STEM, VERSION):
            print(f"    wrote {p.relative_to(ROOT)}")
        return 0

    acc, sl, eta_star, eta_0, floor, gate = _accumulate()
    print(f"\n    GATE  eta_0 column vs the released quadrature: "
          f"worst rel {gate:.2e}  {'PASS' if gate < 1e-9 else '**FAIL**'}")
    if gate >= 1e-9:
        print("    The accumulation does not decompose the released integral; "
              "nothing is written.")
        return 1

    # The reading, printed so it is in the log as well as in the picture.
    a = acc[FRAME]
    x = (sl - eta_star) / (eta_0 - eta_star)
    late = [1.0 - float(np.interp(0.01, x, a[i] / a[i, -1]))
            for i in range(ELLS.size) if a[i, -1] > 0]
    print(f"    late share, worst over {ELLS.size} multipoles: "
          f"{max(np.abs(late)):.4f}  (the late ISW needs ~0.1 at ell=2)")

    _write_csv(acc, sl, eta_star, eta_0, floor)
    print(f"    wrote {CSV.relative_to(ROOT)}")
    for p in save_figure(_draw(acc, sl, eta_star, eta_0, floor), STEM, VERSION):
        print(f"    wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
