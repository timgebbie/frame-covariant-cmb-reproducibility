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
from functions.spectra.pipeline import (  # noqa: E402
    primordial_power,
    required_k_points,
)
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

#: Linear to 1500. Linear is the rule, not a preference: a logarithmic $k$ grid
#: aliases the integrand at high $k$ however many points it has. 1500 runs past
#: the damping scale, which **T-32** requires.
#:
#: **The spacing is now derived --- finding T-56.** This line read
#: ``np.arange(0.05, 1500.0, np.pi / 3.0)`` until 2026-10-17: the comment above
#: argued correctly against a logarithmic grid and then chose the linear step by
#: hand. $C_\ell$ carries $j_\ell(k\Delta\eta)$ **squared**, whose period in $k$
#: is $\pi/\Delta\eta$, so $dk=\pi/3$ gave **0.96 samples per oscillation** on
#: `PLANCK_MODEL` and 0.94 on $\Lambda$CDM --- below one --- for a measured
#: quadrature error of up to 22.5%, non-monotonic in $\ell$.
#:
#: `required_k_points` is called **per background**, because $\Delta\eta$ is:
#: Einstein--de Sitter's line of sight is 40% shorter and needs proportionally
#: fewer modes. `K_MAX` is shared; the grid is not.
K_MAX = 1500.0

#: Where this run writes. **A diagnostic run must not overwrite the release
#: artefacts** --- decision **V14**, *a control is not evidence; controls live
#: in `diagnostics/`, never `figures/`*. `--b-slot-repair` rebinds both of
#: these in `main()`, so the released figure, its CSV and their manifest
#: hashes are untouched by a T-88 run.
STEM = "f9-acoustic-spectrum"
CSV_PATH_REL = ("outputs", "f9-acoustic-spectrum.csv")

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
        K_MAX, omega_m=background.omega_m,
        omega_lambda=background.omega_lambda, omega_r=background.omega_r,
        omega_b_h2=omega_b_h2, transfer_gamma=gamma, hubble_h=hubble_h,
        f_2=F2_DEFAULT, line_of_sight_weight="printed")
    r_theta = float(env.background.eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    print(f"      r_theta = {r_theta:.4f}, k to {K_MAX:.0f} in {k_com.size} modes "
          f"({(np.pi / r_theta) / (k_com[1] - k_com[0]):.2f} samples per "
          f"j_l^2 oscillation; T-56)")
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)
    transfer = {"newtonian": np.zeros((ELLS.size, k_com.size)),
                "cdm": np.zeros((ELLS.size, k_com.size))}
    for j, k in enumerate(k_com):
        sets = dict(zip(("newtonian", "cdm"), coefficient_sets(float(k), env)))
        for name, coefficients in sets.items():
            transfer[name][:, j] = transfer_by_rank(
                ELLS, float(k), coefficients, env, table)[-1]
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)
    return {name: np.array([cl_covariant_route(int(l), k_com, block[i], power)
                            for i, l in enumerate(ELLS)])
            for name, block in transfer.items()}


def shape(ell: np.ndarray, cl: np.ndarray) -> np.ndarray:
    r"""$D_\ell/D_{30}$ --- **the plotted quantity. Reverted 2026-10-19.**

    This was briefly $C_\ell/C_{30}$ on log--log. The PI's call, having seen
    both: **linear--log works better and is more recognisable**, and that is
    the right criterion for a figure whose job is to be read. $D_\ell$ on a
    linear axis against $\log\ell$ is what a CMB spectrum is plotted in, the
    acoustic peaks are what the eye should find first, and a reader should not
    have to re-learn the axes to see them.

    The log--log experiment is not wasted: it is what made the *absence* of
    structure legible while the spectrum had none, and it is how the damping
    tail was read. Now that there is structure, the standard axes win.

    **$D_{30}$ is exact, not interpolated.** `ELLS` contains 30 explicitly
    (`np.arange(30, 1001, 30)` starts there), so `np.interp(30.0, ell, d)`
    returns the grid value. `d_ell` is $\ell(\ell+1)C_\ell/2\pi$ --- checked.
    """
    d = d_ell(ell, cl)
    return d / np.interp(30.0, ell, d)


def shape_d(ell: np.ndarray, cl: np.ndarray) -> np.ndarray:
    r"""$D_\ell/D_{30}$ --- retained for **peak finding only**, not for the axes."""
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


def source_fingerprint() -> str:
    r"""A digest of **the code that produced the numbers**, for the CSV header.

    **Finding T-54.** F9 is wired into `run_all.py` as ``--replot``, because a
    full recompute is 1433 modes across three backgrounds and two frames and
    cannot run on every harness pass. That cache is sound and the staleness it
    allows was **invisible to every gate in the bundle**: `--replot` does not
    rewrite the CSV, so the CSV still matches its manifest hash, so
    `make_manifests.py --check` passes, so `run_all --rerun` prints **CLEAN**
    --- over a spectrum computed two days and three findings earlier. On
    2026-10-17 it printed CLEAN over an F9 carrying the pre-**T-51** acoustic
    scale, peak spacing 589.7 against the corrected 284.

    **A content hash cannot detect a file that was never regenerated.** It
    answers *"is this file what it was?"*, and the question here is *"was this
    file made by this code?"* --- so the code's identity goes into the file.

    The digest covers every `functions.*` module actually imported, resolved
    from `sys.modules` rather than listed, plus this script. **Deliberately
    conservative**: a docstring change invalidates the cache, because bytes
    cannot say whether a change was semantic. The cost of a false invalidation
    is one rerun; the cost of a false validation is shipping a stale spectrum
    under a CLEAN banner, which is what happened.
    """
    import hashlib

    digest = hashlib.sha256()
    loaded = sorted(
        (name, Path(module.__file__))
        for name, module in sys.modules.items()
        if name.startswith("functions.") and getattr(module, "__file__", None))
    for name, path in loaded:
        digest.update(name.encode("utf-8"))
        digest.update(path.read_bytes())
    digest.update(Path(__file__).read_bytes())
    return digest.hexdigest()[:16]


def first_peak(ell: np.ndarray, s: np.ndarray, *, floor: float = 30.0) -> float:
    r"""The first **interior** maximum above `floor`, interpolated rather than
    read off the grid --- or `nan` when the curve has none.

    The $\ell$ grid steps by 30 across the acoustic band, so a grid maximum can
    only ever land on a multiple of 30 --- which would report the peak as 150 or
    180 and nothing between, an apparent precision the sampling does not have. A
    parabola through the maximum and its two neighbours gives the vertex to a
    fraction of a step, which is what the curve actually says.

    **This searched a fixed window, $80\le\ell\le400$, and returned the window's
    edge when the maximum sat on it.** On 2026-10-16, with the acoustic start
    corrected (**T-51**, **S40**), the Einstein--de Sitter curve stopped having an
    interior maximum there and this reported $\ell=90.0$ --- exactly the first
    grid point at or above 80, carrying no interpolation and no peak. It read as
    a measurement because it was a number.

    **A search window fitted to a result is a window that hides the result
    changing.** 80--400 was chosen when the peak sat near 170; the moment the
    physics moved, the window reported its own lower edge rather than the
    absence it had found. So there is no window now: this scans for the first
    *interior* local maximum above `floor` --- 30, the normalisation anchor,
    below which "first peak" means nothing --- and returns **`nan`** when the
    curve has none, which the caller must then say out loud.
    """
    x, y = np.asarray(ell, dtype=float), np.asarray(s, dtype=float)
    inside = np.nonzero(x >= float(floor))[0]
    for i in inside:
        if i == 0 or i == x.size - 1:
            continue
        if not (y[i] > y[i - 1] and y[i] > y[i + 1]):
            continue
        denom = y[i - 1] - 2.0 * y[i] + y[i + 1]
        if denom == 0.0:
            return float(x[i])
        return float(x[i] + 0.5 * (y[i - 1] - y[i + 1]) / denom * (x[i + 1] - x[i]))
    return float("nan")


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
    # **A curve with no interior maximum gets no peak line and says so.**
    # `first_peak` returns nan rather than a window edge (T-53), and a figure
    # that drew a line at nan would draw nothing at all while the caption went
    # on claiming a peak.
    ours = peaks["PLANCK_MODEL"]
    if np.isfinite(ours):
        ax.axvline(ours, color=INK["muted"], lw=0.8, ls=SERIES_DASH[4], zorder=1)
        said = f"first peak $\\ell\\simeq{ours:.0f}$"
    else:
        said = "no interior maximum above $\\ell=30$"
    ax.annotate(
        said + f"\nCAMB $\\ell\\simeq{peaks['CAMB']:.0f}$",
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

    # **Log-log, the PI's call, 2026-10-19.** A linear $D_\ell$ axis shows peak
    # *contrast* and hides everything below a few percent of $D_{30}$, which on
    # these curves is most of $\ell>400$. The damping tail is a power law times
    # a Gaussian and on log-log it is a straight line with a knee at $k_D$, so
    # the diffusion scale becomes something the eye can place rather than
    # something the caption has to assert. It also makes a curve that is
    # *monotonic* --- no acoustic structure at all --- immediately legible as
    # such, which a linear axis with one visible bump does not.
    #
    # `symlog` is deliberately **not** used: these are renormalised ratios that
    # stay positive, and a symlog threshold would be a free parameter sitting
    # under a figure whose whole claim is the shape.
    for ax in axes:
        ax.set_xscale("log")
        ax.set_xlabel(r"multipole $\ell$")
        # **Legend moved, PI 2026-10-19: it was covering the spectrum.**
        # Lower left is the empty corner once the acoustic peaks are
        # present -- the curve rises away from it -- and two columns keep
        # it short enough not to climb back into the first peak.
        ax.legend(fontsize=6.4, frameon=False, loc="lower left", ncol=2,
                  handlelength=2.2, borderaxespad=0.4, columnspacing=1.1)
    fig.tight_layout()
    written = save_figure(fig, STEM, VERSION)
    if STEM != "f9-acoustic-spectrum":
        # V14: a control does not enter figures/. The pair is moved rather
        # than save_figure being taught a second destination -- one writer,
        # one rule.
        moved = []
        for path in written:
            dest = ROOT / "diagnostics" / path.name
            dest.parent.mkdir(exist_ok=True)
            path.replace(dest)
            moved.append(dest)
        written = moved
    for path in written:
        print(f"wrote {path.relative_to(ROOT)}")

    return 0


def load_csv() -> tuple[np.ndarray, dict, dict]:
    """Re-read what the expensive half already produced.

    **The computation and the picture are separable and must stay that way.**
    Two plotting bugs --- a dash tuple and a palette key --- each surfaced after
    the last number had been produced, and the first of them threw the numbers
    away. `--replot` exists so the third one costs seconds.
    """
    path = ROOT.joinpath(*CSV_PATH_REL)
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
    global ELLS, STEM, CSV_PATH_REL
    print("F9  the normalised angular spectrum with the acoustic peaks")
    print(f"    ells {ELLS.min()}..{ELLS.max()} ({ELLS.size}), "
          f"k to {K_MAX:.0f}, f_2 = {F2_DEFAULT}; the k grid is derived per "
          f"background (T-56) and the")
    print("    line-of-sight weight is stated, not defaulted (T-57, A-1).")

    # **`--b-slot-repair` --- finding T-88, and it is a DIAGNOSTIC switch.**
    # With it on, C_1's gravitational half takes W = e^-kappa, its Thomson half
    # takes g = V carrying (vhat_B + C_2) TOGETHER (T-82's boost-invariant
    # pair), and the missing +k Int W M j_l' bulk slot is supplied.
    #
    # **What to expect, stated before the run so the output cannot be read
    # charitably.** D14 measures the repair closing the frame gap by up to four
    # orders at l >= 50 for k <~ 60, and doing NOTHING at k = 300, where it
    # rewrites the Newtonian column by 7x on PLANCK. F9 integrates to k = 1500.
    # **So the peaks should improve and the damping tail should be WRONG.** A
    # tail that comes out right falsifies T-88's account rather than confirming
    # it, and that is the point of saying so here rather than afterwards.
    #
    # The figure this produces is a control and does not enter `figures/` as a
    # release artefact --- decision **V14**, a control is not evidence.
    if "--b-slot-repair" in sys.argv:
        from functions.spectra import two_frame as _tf
        _tf.B_SLOT_REPAIR = True
        STEM = "d15-f9-b-slot-repair"
        CSV_PATH_REL = ("diagnostics", "d15-f9-b-slot-repair.csv")
        print("    **B-SLOT REPAIR ON (T-88)** --- diagnostic run. Expect the "
              "peaks to improve and the")
        print("    damping tail to be wrong above k ~ 100; see D14.")

    if "--replot" in sys.argv:
        cached = ROOT.joinpath(*CSV_PATH_REL)
        stamped = ""
        if cached.exists():
            for line in cached.read_text(encoding="utf-8").splitlines():
                if line.startswith("# sources:"):
                    stamped = line.split(":", 1)[1].strip()
                    break
        current = source_fingerprint()
        if stamped != current:
            print(f"    FAIL  the cached CSV was produced by different code "
                  f"(stamped {stamped or 'nothing'}, this tree {current}).")
            print("          --replot cannot redraw numbers it did not compute.")
            print("          Run `python scripts/figure_f9_acoustic_spectrum.py`")
            print("          with no arguments to recompute. Finding T-54.")
            return 1
        ELLS, curves, frames = load_csv()
        # The CSV now stores the C_l shape, so the D_l shape peaks are found
        # on are reconstructed rather than read: D_l/D_30 = [l(l+1)/(30*31)]
        # * (C_l/C_30), exactly. **Without this the replot branch would find
        # the first maximum of C_l and call it the acoustic peak**, which is a
        # different l -- the defect T-54 guards against in a different place.
        _w = (ELLS * (ELLS + 1.0)) / (30.0 * 31.0)
        peaks = {n: first_peak(ELLS, c * _w) for n, c in curves.items()}
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
        # **Peaks are found on D_l, drawn on C_l.** The acoustic peak
        # positions and l_A are D_l statements; the first maximum of C_l
        # is not the first acoustic peak. Mixing the two would move every
        # reported peak by order l_A/2.
        peaks[label] = first_peak(ELLS, shape_d(ELLS, both["cdm"]))
        gaps[label] = (np.abs(frames[label]["cdm"] - frames[label]["newtonian"])
                       / np.abs(frames[label]["cdm"]))
        where = (f"l={peaks[label]:.1f}" if np.isfinite(peaks[label])
                 else "NONE above l=30 -- the curve has no interior maximum")
        print(f"    {label:26s} first peak {where};  frame gap "
              f"median {np.median(gaps[label]):.1%} worst {gaps[label].max():.1%}")

    for name in ("camb", "class"):
        ell_ref, cl_ref = reference(name)
        s = np.interp(ELLS, ell_ref, shape(ell_ref, cl_ref))
        curves[name.upper()] = s
        peaks[name.upper()] = first_peak(
            ELLS, np.interp(ELLS, ell_ref, shape_d(ell_ref, cl_ref)))
        found = peaks[name.upper()]
        print(f"    {name.upper():26s} first peak at "
              + (f"l={found:.1f}" if np.isfinite(found) else "NONE above l=30"))

    # **The data lands before the picture does.** A dash-style type error
    # once threw away three backgrounds of computation at the plotting
    # call, forty-five minutes after the last number was produced. The
    # CSV is the expensive artefact; the figure is cheap and redrawable.
    out = ROOT.joinpath(*CSV_PATH_REL)
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# shape, D_l renormalised at l=30, both frames. "
                 "CAMB and CLASS are context (S4c).\n")
        # The code that made these numbers, so `--replot` cannot redraw a
        # spectrum some other version of this bundle computed --- T-54.
        fh.write(f"# sources: {source_fingerprint()}\n")
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
