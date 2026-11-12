#!/usr/bin/env python3
r"""D44 --- the line of sight with Paper 1's source signs, scored as registered.

QUESTION
    Paper 1's linear redshift source carries the rank-one gravitational term
    with the sign opposite to the Thomson term, and carries the rank-zero term
    $a\mathcal B_0=-\tfrac k3\tau_1$. Built that way, do the coefficients meet
    the three frame conditions of $\int W\{C_0K+C_1K'+C_2K''\}$; does the
    assembly that keeps $\kappa'$ out of every derivative and $\hat v_B$ with
    $C_2$ give one $C_\ell$ in both frames; and does that $C_\ell$ carry an
    acoustic series?

REGISTERED BEFORE IT WAS BUILT (supplement v1.3.23)
    (a) the three conditions hold to the integrator's tolerance at every mode;
    (b) in the Newtonian frame the W-carried gravitational content is
        -(Phi_A' - Phi_H') and (k/3) tau_1 cancels;
    (c) the exact identity, the bracket at W with its visibility terms,
        returns C_l at l >= 2 identical in the two frames, and on
        Einstein-de Sitter no late power;
    (d) the assembly that keeps kappa' out of every derivative and vhat_B with
        C_2 carries a peak series in both frames, identical at l >= 2. If (d)
        fails while (a)-(c) hold, the loss of the series is not a frame defect.
    With it, from the transfer side: the full C_l agrees between the frames
    below 1e-12, and a residual above 1e-6 that does not track the quadrature
    refutes it.

WHAT IS MEASURED
    1. Coefficients, k = 2..400, all three backgrounds, as built and with
       Paper 1's signs: each condition as the largest relative frame shift
       over W > 1e-10; and (b), the Newtonian integrated source against
       -(Phi_A' - Phi_H').
    2. Per mode on F9's k grid to k = 1500, Paper 1's signs: the three slots
       of the supplement's eq:assembly-invariant (line_of_sight.three_slots)
       in both frames; the five slots and the
       direct integral in both frames. Five against three is the quadrature
       of the W C_2' K' term; direct against five is the stored photon
       moments against their own evolution after last scattering.
    3. (c) on every 75th mode: (102)'s bracket at W with its visibility terms,
       through transfer_by_rank, in both frames.
    4. C_l: the three slots in both frames --- the frame residual, the maxima
       and troughs of D_l by the shared prominence rule, the first maximum in
       units of l_A --- and the same slots with the Doppler slot's sign
       reversed, the relative sign no frame test can see; Einstein-de Sitter's
       integrated-slot share.

    CAMB and CLASS enter only after all of the above is scored, as context.

USAGE
    python scripts/diagnostic_d44_the_line_of_sight_in_invariant_slots.py --background PLANCK
    python scripts/diagnostic_d44_the_line_of_sight_in_invariant_slots.py --report

Each background checkpoints every 50 modes outside the tree (`D44_CACHE`, or
the system temporary directory), keyed by the source fingerprint and the
configuration, so a run resumes where it stopped and never from other code.
`--report` writes every number the report prints to two CSVs stamped with the
sources, and `--replot` rewrites the report and the figure from them alone,
refusing a stamp this tree did not compute (T-54): that is the release route's
call.

    python scripts/diagnostic_d44_the_line_of_sight_in_invariant_slots.py --replot
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _fingerprint import source_fingerprint as _digest  # noqa: E402
from _peak import (  # noqa: E402
    acoustic_maxima, acoustic_minima, first_acoustic_peak)
import functions.spectra.coefficients as coefficients  # noqa: E402
import functions.spectra.two_frame as two_frame  # noqa: E402
from functions.background.flrw import PLANCK_N_S  # noqa: E402
from functions.spectra.angular import cl_covariant_route, d_ell  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.coefficients import gravitational_rank_one  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.line_of_sight import (  # noqa: E402
    kernel_set, slots, three_slots)
from functions.spectra.pipeline import (  # noqa: E402
    primordial_power, required_k_points)
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, coefficient_sets, line_of_sight_inputs,
    transfer_by_rank)
from make_model_table import MODELS, row  # noqa: E402

VERSION = "v1.4.0"
K_MAX = 1500.0
SOURCE = "paper 1"
ELLS = np.unique(np.concatenate([[2, 3, 4, 5, 7, 10, 14, 20, 25],
                                 np.arange(30, 1201, 15)]))
BACKGROUNDS = {"EdS": 0, "LCDM": 1, "PLANCK": 2}
#: Where the coefficient-level conditions are checked: each k is an
#: independent pointwise identity, not a quadrature node.
CONDITION_K = np.arange(2.0, 401.0, 2.0)
IDENTITY_EVERY = 75
CSV_REL = ("diagnostics", "d44-line-of-sight-invariant-slots.csv")
TXT_REL = ("diagnostics", f"d44-line-of-sight-invariant-slots-{VERSION}.txt")
PNG_REL = ("diagnostics", f"d44-line-of-sight-invariant-slots-{VERSION}.png")
SUMMARY_REL = ("diagnostics", "d44-line-of-sight-invariant-slots-summary.csv")

SLOTS = ("sw", "dop", "isw")
TRANSFERS = tuple(f"{s}_{f}" for f in "NC" for s in SLOTS) + (
    "five_N", "five_C", "direct_N", "direct_C")


def _env(index: int, k_max: float = K_MAX):
    label, bg, omega_b_h2, h, _n_s = MODELS[index]
    return label, build_environment(
        k_max, omega_m=bg.omega_m, omega_lambda=bg.omega_lambda,
        omega_r=bg.omega_r, omega_b_h2=omega_b_h2,
        transfer_gamma=shape_parameter(bg.omega_m, h), hubble_h=h,
        f_2=F2_DEFAULT, line_of_sight_weight="printed")


def _rel(a, b, mask=slice(None)) -> float:
    a, b = np.asarray(a)[mask], np.asarray(b)[mask]
    scale = float(max(np.max(np.abs(a)), np.max(np.abs(b))))
    return float(np.max(np.abs(a - b)) / scale) if scale > 0 else 0.0


def conditions(index: int, choice: str) -> dict[str, float]:
    """Measurement 1: the three frame conditions, and (b)."""
    _label, env = _env(index, 410.0)
    on = np.asarray(env.opacity) > 1e-10
    out = dict.fromkeys(("rank zero", "scattering", "gravitational",
                         "integrated source vs ISW"), 0.0)
    with coefficients.rank_one_source(choice):
        for k in CONDITION_K:
            n, c = coefficient_sets(float(k), env, source=choice)
            gn, _ = gravitational_rank_one(n)
            gc, _ = gravitational_rank_one(c)
            c2p_n = np.zeros_like(env.eta) if n.c2_prime is None else n.c2_prime
            out["rank zero"] = max(out["rank zero"], _rel(
                n.coefficients.c0, c.coefficients.c0, on))
            out["scattering"] = max(out["scattering"], _rel(
                n.v_b / k + n.coefficients.c2, c.v_b / k + c.coefficients.c2,
                on))
            out["gravitational"] = max(out["gravitational"], _rel(
                gn - c2p_n, gc - c.c2_prime, on))
            s, _ = line_of_sight_inputs(float(k), n, env)
            isw = -env.transfer_at(float(k)) * (
                np.asarray(env.phi_a_prime) - np.asarray(env.phi_h_prime))
            src = s.c0 - s.c1_grav_prime + s.c2_second
            out["integrated source vs ISW"] = max(
                out["integrated source vs ISW"],
                float(np.max(np.abs((src - isw)[on]))
                      / np.max(np.abs(s.c0[on]) + np.abs(isw[on]))))
    return out


def _cache_path(index: int, k_com: np.ndarray) -> Path:
    config = repr((index, SOURCE, float(K_MAX), int(k_com.size),
                   IDENTITY_EVERY, ELLS.tolist()))
    key = hashlib.sha256((_digest(__file__) + config).encode()).hexdigest()[:16]
    base = Path(os.environ.get("D44_CACHE", tempfile.gettempdir()))
    return base / f"d44-{list(BACKGROUNDS)[index]}-{key}.npz"


def _grid(env) -> np.ndarray:
    """F9's k grid: spaced from the period of j_l^2 on this background."""
    r_theta = float(env.background.eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    return k_com


def run_background(index: int) -> Path:
    """Measurements 2 and 3: every transfer at every mode, checkpointed."""
    label, env = _env(index)
    k_com = _grid(env)
    cache = _cache_path(index, k_com)
    shape = (ELLS.size, k_com.size)
    data = {n: np.zeros(shape) for n in TRANSFERS}
    data["damping"] = np.zeros(k_com.size)
    data["identity_frame"] = np.full(k_com.size, np.nan)
    start = 0
    if cache.exists():
        held = np.load(cache)
        if held["sw_N"].shape == shape:
            data = {n: held[n].copy() for n in data}
            start = int(held["done"])
    print(f"    {label}: {k_com.size} modes to k = {K_MAX:.0f}, {ELLS.size} "
          f"multipoles, source {SOURCE!r}; from mode {start} ({cache.name})",
          flush=True)
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)
    eta0 = float(env.background.eta_0)
    t0 = time.time()
    for j in range(start, k_com.size):
        k = float(k_com[j])
        kern = kernel_set(ELLS, k, eta=env.eta, eta_0=eta0, table=table)
        sets = coefficient_sets(k, env, source=SOURCE)
        for frame, cs in zip("NC", sets):
            s, damping = line_of_sight_inputs(k, cs, env)
            three, five = three_slots(kern, s), slots(kern, s)
            data[f"sw_{frame}"][:, j] = three.sachs_wolfe
            data[f"dop_{frame}"][:, j] = three.doppler
            data[f"isw_{frame}"][:, j] = three.integrated
            data[f"five_{frame}"][:, j] = five.total
            data[f"direct_{frame}"][:, j] = five.direct
        data["damping"][j] = damping
        if j % IDENTITY_EVERY == 0:
            # (c): (102)'s bracket at W with its visibility terms
            held_controls = dict(two_frame.BULK_SOURCE_CONTROLS)
            try:
                two_frame.BULK_SOURCE_CONTROLS = dict(
                    bracket_all_at_w=True, by_parts_weight_terms=True)
                tn, tc = (transfer_by_rank(ELLS, k, cs, env, table)[-1]
                          for cs in sets)
            finally:
                two_frame.BULK_SOURCE_CONTROLS = held_controls
            data["identity_frame"][j] = _rel(tn, tc)
        if (j + 1) % 50 == 0 or j + 1 == k_com.size:
            tmp = cache.with_suffix(".tmp.npz")
            np.savez(tmp, done=j + 1, k_com=k_com, **data)
            os.replace(tmp, cache)
            if (j + 1) % 500 == 0 or j + 1 == k_com.size:
                print(f"      mode {j + 1:5d} of {k_com.size}  "
                      f"({time.time() - t0:.0f}s)", flush=True)
    return cache


def _transfers(held) -> dict[str, np.ndarray]:
    d = held["damping"][None, :]
    out = {}
    for f in "NC":
        sw, dop, isw = (held[f"{s}_{f}"] for s in SLOTS)
        out[f"three_{f}"] = d * (sw + dop) + isw
        out[f"reversed_{f}"] = d * (sw - dop) + isw
        out[f"five_{f}"] = d * held[f"five_{f}"]
        out[f"direct_{f}"] = d * held[f"direct_{f}"]
    for s in SLOTS:
        out[f"slot_{s}"] = (held[f"{s}_N"] * (d if s != "isw" else 1.0))
    return out


def _series(cl: np.ndarray) -> dict:
    d = d_ell(ELLS, cl)
    return dict(maxima=acoustic_maxima(ELLS, d),
                troughs=acoustic_minima(ELLS, d),
                first=first_acoustic_peak(ELLS, d)[0])


CHOICES = ("as built", "paper 1")
CONDITION_KEYS = ("rank zero", "scattering", "gravitational",
                  "integrated source vs ISW")
CL_TAGS = tuple(f"{tag}_{f}" for tag in ("three", "reversed", "five", "direct")
                for f in "NC") + tuple(f"slot_{s}" for s in SLOTS)


def _measured() -> dict | None:
    """Everything the report prints, from the caches and the coefficients."""
    found = {}
    for name, index in BACKGROUNDS.items():
        _label, env = _env(index)
        k_com = _grid(env)
        cache = _cache_path(index, k_com)
        if not cache.exists() or int(np.load(cache)["done"]) != k_com.size:
            print(f"   {name}: no completed run; run --background {name}")
            return None
        held = np.load(cache)
        tr = _transfers(held)
        power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)
        cl = {n: np.array([cl_covariant_route(int(l), k_com, t[i], power)
                           for i, l in enumerate(ELLS)])
              for n, t in tr.items()}
        scale = [max(np.max(np.abs(tr["three_N"][:, j])),
                     np.max(np.abs(tr["three_C"][:, j])))
                 for j in range(k_com.size)]
        per_mode = {
            "three": max(_rel(tr["three_N"][:, j], tr["three_C"][:, j])
                         for j in range(k_com.size)),
            **{f"slot {s}": max(
                float(np.max(np.abs(held[f"{s}_N"][:, j]
                                    - held[f"{s}_C"][:, j]))) / scale[j]
                for j in range(k_com.size) if scale[j] > 0)
               for s in SLOTS},
            "five": max(_rel(tr["five_N"][:, j], tr["five_C"][:, j])
                        for j in range(k_com.size)),
            "direct": max(_rel(tr["direct_N"][:, j], tr["direct_C"][:, j])
                          for j in range(k_com.size)),
            "five vs three (CDM)": max(
                _rel(tr["five_C"][:, j], tr["three_C"][:, j])
                for j in range(k_com.size)),
            "identity (c)": float(np.nanmax(held["identity_frame"])),
        }
        found[name] = {
            "conditions": {choice: conditions(index, choice) for choice in CHOICES},
            "per_mode": per_mode,
            "cl": {tag: cl[tag] for tag in CL_TAGS},
            "l_A": float(row(*MODELS[index])["l_A"]),
        }
    return found


def _stamp_of(path: Path) -> str:
    with path.open(encoding="utf-8") as fh:
        first = fh.readline().strip()
    return first.removeprefix("# sources: ") if first.startswith("# sources: ") else ""


def _write_csvs(found: dict, stamp: str) -> None:
    """Every number the report prints, at full precision, under one stamp."""
    with ROOT.joinpath(*CSV_REL).open("w", encoding="utf-8", newline="") as fh:
        fh.write(f"# sources: {stamp}\n")
        fh.write(f"# C_l, source {SOURCE!r}, primordial amplitude 1\n")
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["background", "ell", *CL_TAGS])
        for name, m in found.items():
            for i, l in enumerate(ELLS):
                w.writerow([name, int(l)]
                           + [repr(float(m["cl"][tag][i])) for tag in CL_TAGS])
    with ROOT.joinpath(*SUMMARY_REL).open("w", encoding="utf-8", newline="") as fh:
        fh.write(f"# sources: {stamp}\n")
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["background", "quantity", "value"])
        for name, m in found.items():
            for choice in CHOICES:
                for key in CONDITION_KEYS:
                    w.writerow([name, f"conditions, {choice}, {key}",
                                repr(float(m["conditions"][choice][key]))])
            for key, value in m["per_mode"].items():
                w.writerow([name, f"per mode, {key}", repr(float(value))])
            w.writerow([name, "l_A", repr(m["l_A"])])


def _from_csvs() -> tuple[dict, str] | None:
    """The report's numbers back from the two CSVs, if this tree wrote them."""
    paths = [ROOT.joinpath(*CSV_REL), ROOT.joinpath(*SUMMARY_REL)]
    stamps = {_stamp_of(p) if p.exists() else "" for p in paths}
    here = _digest(__file__)
    if stamps != {here}:
        print(f"REFUSED: the CSVs carry {sorted(stamps)} and this tree's sources "
              f"are {here}. --replot draws only numbers this code computed "
              "(T-54); run --background for each, then --report.")
        return None
    found = {name: {"conditions": {c: {} for c in CHOICES}, "per_mode": {},
                    "cl": {}, "l_A": None} for name in BACKGROUNDS}
    with paths[0].open(encoding="utf-8") as fh:
        rows = [r for r in csv.reader(fh) if r and not r[0].startswith("#")]
    header, rows = rows[0], rows[1:]
    for name in BACKGROUNDS:
        mine = [r for r in rows if r[0] == name]
        for j, tag in enumerate(header[2:], start=2):
            found[name]["cl"][tag] = np.array([float(r[j]) for r in mine])
    with paths[1].open(encoding="utf-8") as fh:
        rows = [r for r in csv.reader(fh) if r and not r[0].startswith("#")]
    for name, quantity, value in rows[1:]:
        if quantity.startswith("conditions, "):
            _, choice, key = quantity.split(", ", 2)
            found[name]["conditions"][choice][key] = float(value)
        elif quantity.startswith("per mode, "):
            found[name]["per_mode"][quantity.removeprefix("per mode, ")] = float(value)
        else:
            found[name]["l_A"] = float(value)
    return found, here


def report(found: dict, stamp: str) -> int:
    lines: list[str] = []

    def say(text: str = "") -> None:
        print(text)
        lines.append(text)

    say(__doc__.split("USAGE")[0].rstrip())
    say()
    say(f"sources: {stamp}")
    say()
    say("1. COEFFICIENTS, k = 2..400: largest relative frame shift over "
        "W > 1e-10")
    say(f"   {'':8s} {'':9s} {'rank zero':>10s} {'scattering':>11s} "
        f"{'gravitational':>14s} {'(b) source-ISW':>15s}")
    for name in BACKGROUNDS:
        for choice in CHOICES:
            c = found[name]["conditions"][choice]
            say(f"   {name:8s} {choice:9s} {c['rank zero']:10.1e} "
                f"{c['scattering']:11.1e} {c['gravitational']:14.1e} "
                f"{c['integrated source vs ISW']:15.1e}")

    say()
    say("2-3. PER MODE, max over modes of max_l |T_N - T_C| / max_l |T|; "
        "each slot against the whole")
    say("     three-slot transfer, so a slot that is zero to rounding reads "
        "as rounding")
    for name in BACKGROUNDS:
        r = found[name]["per_mode"]
        say(f"   {name:8s} " + "  ".join(f"{k} {v:.1e}" for k, v in r.items()))

    say()
    say("4. C_l (Paper 1's signs). Frame residual max_l |C_N - C_C| / C_N; "
        "maxima and troughs of D_l;")
    say("   first maximum / l_A.")
    scores = {}
    for name in BACKGROUNDS:
        cl = found[name]["cl"]
        l_a = found[name]["l_A"]
        say(f"\n   {name}  (l_A = {l_a:.1f})")
        for tag in ("three", "reversed", "five", "direct"):
            frame = float(np.max(np.abs(cl[f"{tag}_N"] - cl[f"{tag}_C"])
                                 / np.abs(cl[f"{tag}_N"])))
            scores[(name, tag)] = frame
            say(f"     {tag:9s} frame residual {frame:.1e}")
            for fname in ("N", "C"):
                s = _series(cl[f"{tag}_{fname}"])
                first = (f"{s['first']:.0f} = {s['first'] / l_a:.2f} l_A"
                         if np.isfinite(s["first"]) else "none")
                say(f"       {'Newtonian' if fname == 'N' else 'CDM':9s} "
                    f"maxima {s['maxima']}  troughs {s['troughs']}  "
                    f"first {first}")
        share = float(np.max(cl["slot_isw"] / cl["three_N"]))
        say(f"     integrated-slot auto-spectrum / total, max over l: "
            f"{share:.1e}")

    say()
    say("SCORED")
    p5 = max(scores[(n, "three")] for n in BACKGROUNDS)
    say(f"   frame, three slots: worst C_l residual {p5:.1e} -> "
        + ("below 1e-12" if p5 < 1e-12 else "above 1e-6" if p5 > 1e-6
           else "between 1e-12 and 1e-6"))
    series = {n: _series(found[n]["cl"]["three_N"]) for n in BACKGROUNDS}
    say("   (d) series, three slots, Newtonian (troughs between maxima): "
        + ", ".join(f"{n} {len(s['maxima'])} maxima / {len(s['troughs'])} "
                    f"troughs" for n, s in series.items()))
    say("   (c) is section 2-3's 'identity (c)' column, transfer level.")

    say()
    say("CONTEXT, NOT TARGET: CAMB and CLASS maxima of D_l (same rule)")
    for ref in ("camb", "class"):
        ell, cl = [], []
        path = ROOT / "reference" / f"{ref}-tt-v1.2.0.csv"
        for r in csv.reader(path.open(encoding="utf-8")):
            if r and not r[0].startswith("#") and r[0] != "ell":
                ell.append(int(r[0]))
                cl.append(float(r[1]))
        ell, cl = np.array(ell), np.array(cl)
        say(f"   {ref:5s} maxima {acoustic_maxima(ell, d_ell(ell, cl))[:5]}")

    ROOT.joinpath(*TXT_REL).write_text("\n".join(lines) + "\n",
                                       encoding="utf-8")
    _draw({name: found[name]["cl"] for name in BACKGROUNDS})
    return 0


def _draw(spectra: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from functions.plotting.style import (
        DETERMINISTIC_METADATA, SERIES, SERIES_DASH, use_house_style)

    use_house_style()
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.4))
    for ax, (name, cl) in zip(axes, spectra.items()):
        def shape(c):
            d = d_ell(ELLS, c)
            return d / np.interp(30.0, ELLS, d)
        ax.plot(ELLS, shape(cl["three_N"]), color=SERIES[1],
                ls=SERIES_DASH[1], lw=1.8, label="three slots, Newtonian")
        ax.plot(ELLS, shape(cl["three_C"]), color=SERIES[2],
                ls=SERIES_DASH[2], lw=1.2, label="three slots, CDM")
        ax.plot(ELLS, shape(cl["reversed_N"]), color=SERIES[4],
                ls=SERIES_DASH[4], lw=1.0, label="Doppler sign reversed")
        ax.set_xscale("log")
        ax.set_title(name)
        ax.set_xlabel(r"$\ell$")
    axes[0].set_ylabel(r"$D_\ell/D_{30}$")
    axes[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(ROOT.joinpath(*PNG_REL),
                metadata=DETERMINISTIC_METADATA["png"])
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--background", choices=list(BACKGROUNDS))
    ap.add_argument("--report", action="store_true",
                    help="read the caches, write the CSVs, the report and the figure")
    ap.add_argument("--replot", action="store_true",
                    help="rewrite the report and the figure from the CSVs alone")
    args = ap.parse_args()
    if args.background:
        run_background(BACKGROUNDS[args.background])
        return 0
    if args.report:
        found = _measured()
        if found is None:
            return 1
        _write_csvs(found, _digest(__file__))
        loaded = _from_csvs()            # the report is drawn from what is kept
        return 1 if loaded is None else report(*loaded)
    if args.replot:
        loaded = _from_csvs()
        return 1 if loaded is None else report(*loaded)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
