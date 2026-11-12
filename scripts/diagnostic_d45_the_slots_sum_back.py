#!/usr/bin/env python3
r"""D45 --- the three slots summed back to the integral they rearrange.

QUESTION
    The three slots of eq:assembly-invariant rearrange
    $\int W\{C_0K+C_1K'+C_2K''\}$ exactly only if every slot weight is right,
    and no frame test can see a weight, because each slot is invariant on its
    own. Built from one set of coefficients, do the slots give back the direct
    integral, mode by mode? How far do the photon moments stored after last
    scattering move the direct integral, and how far the slots? And on
    PLANCK, where the series is lost, which pair of slots cancels, and at
    which multipoles?

WHAT IS MEASURED (Paper 1's signs)
    Per mode, max over l of |difference| / max over l of |three slots|, for
    l = 2..1200, reported as the largest value in each k band, on the
    released $\eta$ grid and on one with half its step: a quadrature residual
    falls by four.
    1. SUM-BACK, both frames. One set of arrays feeds both sides, and in it
       $C_1^{\rm grav}{}'$ is the $\eta$-derivative of the $C_1^{\rm grav}$ it
       is paired with: (i) $C_1^{\rm grav}$ integrated from its (106)
       derivative, from the grid's start; (ii) the stored $C_1^{\rm grav}$,
       differentiated on the grid. The end points $[W(GK+C_2K')]$ at the
       grid's start and at $\eta_0$ are evaluated, not assumed. The identity
       also needs $W'=\mathcal V$. Since T-191's repair both come from one
       $\kappa$ on the grid, so they differ by quadrature alone; each
       comparison is made with them as built and again with $\mathcal V$
       replaced by $W'$ taken on the grid. Beside
       them, the five slots against the three, which differ by
       $\int(WC_2'K)'$ alone, and which side of the identity moves when the
       step is halved.
    2. STORED MOMENTS, Newtonian frame. (106) integrated from **each mode's
       own start** (T-192), the stored moment before it, against the stored
       $C_1^{\rm grav}$: in the direct integral,
       $\int W(C_1^{\rm grav}-C_{1\,(106)}^{\rm grav})K'$, and in the three
       slots as F9 builds them (the stored $C_1^{\rm grav}$ under
       $\mathcal V$, (106) under $W$),
       $-\int\mathcal V(C_1^{\rm grav}-C_{1\,(106)}^{\rm grav})K$. Anchored at
       the grid's start instead, the comparison measured the start rule and
       not (106) (T-192). And the three slots with $\mathcal V$ against the
       three slots with $W'$.
    3. CROSS-SPECTRA of the slots, Newtonian frame (each slot is invariant),
       on F9's k grid with F9's diffusion factor: the total $C_\ell$ as three
       auto-terms and three cross-terms, each a fraction of it, on D44's
       multipoles l = 2-1200, LCDM and PLANCK; and the maxima of $D_\ell$ by
       the shared prominence rule with every slot, without the integrated
       slot, and from the Sachs--Wolfe slot alone.

Each background checkpoints outside the tree (`D45_CACHE`, or the system
temporary directory), keyed on the sources and the configuration. `--report`
writes every number the report prints to two CSVs stamped with the sources, and
`--replot` rewrites the report and the figure from them alone, refusing a stamp
this tree did not compute (T-54): that is the release route's call.

USAGE
    python scripts/diagnostic_d45_the_slots_sum_back.py --background LCDM
    python scripts/diagnostic_d45_the_slots_sum_back.py --background PLANCK
    python scripts/diagnostic_d45_the_slots_sum_back.py --report
    python scripts/diagnostic_d45_the_slots_sum_back.py --replot
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
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
from _peak import acoustic_maxima  # noqa: E402
from functions.background.flrw import PLANCK_N_S  # noqa: E402
from functions.spectra.acoustic import acoustic_start_eta  # noqa: E402
from functions.spectra.angular import cl_covariant_route, d_ell  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.line_of_sight import (  # noqa: E402
    Kernels, Sources, kernel_set, slots, three_slots)
from functions.spectra.pipeline import (  # noqa: E402
    primordial_power, required_k_points)
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, cl_cross, covariant_coefficient_sets,
    line_of_sight_inputs)
from make_model_table import MODELS  # noqa: E402

VERSION = "v1.4.0"
TXT_REL = ("diagnostics", f"d45-the-slots-sum-back-{VERSION}.txt")
CSV_REL = ("diagnostics", "d45-the-slots-sum-back.csv")
MODES_REL = ("diagnostics", "d45-the-slots-sum-back-per-mode.csv")
PNG_REL = ("diagnostics", f"d45-the-slots-sum-back-{VERSION}.png")
BACKGROUNDS = {"LCDM": 1, "PLANCK": 2}
K_MAX = 1500.0
#: The identity is pointwise in k, so a sample is enough: forty modes in each
#: band, the bands being where the step $k\,\Delta\eta$ changes regime.
K_BANDS = ((2.0, 100.0), (100.0, 400.0), (400.0, K_MAX))
SUM_BACK_K = np.unique(np.concatenate(
    [np.linspace(lo, hi, 40) for lo, hi in K_BANDS]))
SUM_BACK_ELLS = np.array([2, 3, 10, 30, 100, 200, 300, 500, 800, 1200])
#: The second grid has half the first's $\eta$ step.
REFINE = 2
#: D44's multipoles, so that the two instruments read the same series.
CROSS_ELLS = np.unique(np.concatenate([[2, 3, 4, 5, 7, 10, 14, 20, 25],
                                       np.arange(30, 1201, 15)]))
CHECKPOINT_EVERY = 250
SLOTS = ("sw", "dop", "isw")
#: The total $C_\ell$, term by term: three auto-spectra, three cross-spectra.
TERMS = (("SW", "sw", "sw"), ("Dop", "dop", "dop"), ("ISW", "isw", "isw"),
         ("2SWxISW", "sw", "isw"), ("2DopxISW", "dop", "isw"),
         ("2SWxDop", "sw", "dop"))


def _env(index: int, n_eta: int | None = None):
    """F9's environment for `MODELS[index]`; `n_eta` only to refine it."""
    _label, bg, omega_b_h2, h, _n_s = MODELS[index]
    return build_environment(
        K_MAX, omega_m=bg.omega_m, omega_lambda=bg.omega_lambda,
        omega_r=bg.omega_r, omega_b_h2=omega_b_h2,
        transfer_gamma=shape_parameter(bg.omega_m, h), hubble_h=h,
        f_2=F2_DEFAULT, line_of_sight_weight="printed", n_eta=n_eta)


def _grid(env) -> np.ndarray:
    """F9's k grid: spaced from the period of j_l^2 on this background."""
    r_theta = float(env.background.eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    return k_com


def _rebuilt(s: Sources) -> Sources:
    r"""(i): $C_1^{\rm grav}$ integrated from its (106) derivative, from the
    grid's start, so that it and the derivative the slots use are one object."""
    steps = 0.5 * (s.c1_grav_prime[1:] + s.c1_grav_prime[:-1]) * np.diff(s.eta)
    return dataclasses.replace(
        s, c1_grav=s.c1_grav[0] + np.concatenate([[0.0], np.cumsum(steps)]))


def _anchored(s: Sources, start: float) -> Sources:
    r"""(106) integrated from the mode's own start, and the stored moment
    before it: the solver holds the acoustic pair there, so before the start
    there is no (106) evolution to compare with (T-192)."""
    i0 = int(np.searchsorted(s.eta, start))
    if i0 == 0:
        return _rebuilt(s)
    steps = 0.5 * (s.c1_grav_prime[i0 + 1:] + s.c1_grav_prime[i0:-1]) \
        * np.diff(s.eta[i0:])
    c1 = np.array(s.c1_grav, dtype=float)
    c1[i0:] = c1[i0] + np.concatenate([[0.0], np.cumsum(steps)])
    return dataclasses.replace(s, c1_grav=c1)


def _differentiated(s: Sources) -> Sources:
    r"""(ii): the stored $C_1^{\rm grav}$ with its derivative taken on the grid."""
    return dataclasses.replace(
        s, c1_grav_prime=np.gradient(s.c1_grav, s.eta, edge_order=2))


def _ends(kern: Kernels, s: Sources) -> np.ndarray:
    r"""$[W(GK+C_2K')]$ from the grid's start to $\eta_0$, one per multipole."""
    g = s.c1_grav - s.c2_prime
    term = s.opacity * (g * kern.j + s.c2 * (-kern.k_com) * kern.jd)
    return term[:, -1] - term[:, 0]


def _consistent_weights(s: Sources) -> Sources:
    r"""$\mathcal V$ replaced by $W'$ taken on the grid, so the identity's
    $W'=\mathcal V$ holds there and not only in the recombination module."""
    return dataclasses.replace(
        s, visibility=np.gradient(s.opacity, s.eta, edge_order=2))


def _relative(a: np.ndarray, b: np.ndarray, scale: float) -> float:
    return float(np.max(np.abs(a - b))) / scale


def sum_back_mode(k: float, env) -> tuple[dict[str, float], dict]:
    """Measurements 1 and 2 at one mode on `env`'s grid, and the two transfers
    whose movement with the step says which side carries the quadrature."""
    kern = kernel_set(SUM_BACK_ELLS, k, eta=env.eta,
                      eta_0=float(env.background.eta_0))
    out: dict[str, float] = {}
    kept: dict = {}
    start = acoustic_start_eta(float(k), env.eta_rs, env.r_s_table)
    for frame, cs in zip("NC", covariant_coefficient_sets(k, env)):
        s, _ = line_of_sight_inputs(k, cs, env)
        built = three_slots(kern, s).transfer()      # as F9 builds it
        scale = max(float(np.max(np.abs(built))), 1e-300)
        rebuilt = _rebuilt(s)
        anchored = _anchored(s, start)
        for weights, base in (("", s), (", V=W'", _consistent_weights(s))):
            for tag, src in (("(i)", _rebuilt(base)),
                             ("(ii)", _differentiated(base))):
                out[f"sum-back {tag} {frame}{weights}"] = _relative(
                    three_slots(kern, src).transfer() + _ends(kern, src),
                    slots(kern, src).direct, scale)
            out[f"five vs three {frame}{weights}"] = _relative(
                slots(kern, base).total, three_slots(kern, base).transfer(),
                scale)
        if frame == "N":
            out["stored moments, direct N"] = _relative(
                slots(kern, s).direct, slots(kern, anchored).direct, scale)
            out["stored moments, three N"] = _relative(
                built, three_slots(kern, anchored).transfer(), scale)
            out["weights, three N"] = _relative(
                built, three_slots(kern, _consistent_weights(s)).transfer(),
                scale)
        kept[f"three {frame}"] = built
        kept[f"direct (i) {frame}"] = slots(kern, rebuilt).direct
        kept[f"scale {frame}"] = scale
    return out, kept


def _weights(env) -> dict[str, float]:
    r"""How far the grid's $\mathcal V$ is from its $W'$."""
    eta, w, v = (np.asarray(env.eta), np.asarray(env.opacity),
                 np.asarray(env.visibility))
    return {"V integral": float(np.trapezoid(v, eta)),
            "W rise": float(w[-1] - w[0]),
            "gap": float(
                np.max(np.abs(np.gradient(w, eta, edge_order=2) - v))
                / np.max(v))}


def _cache_path(index: int, k_com: np.ndarray) -> Path:
    config = repr((index, float(K_MAX), int(k_com.size), REFINE,
                   SUM_BACK_K.tolist(), SUM_BACK_ELLS.tolist(),
                   CROSS_ELLS.tolist()))
    key = hashlib.sha256((_digest(__file__) + config).encode()).hexdigest()[:16]
    base = Path(os.environ.get("D45_CACHE", tempfile.gettempdir()))
    return base / f"d45-{index}-{key}.npz"


def run_background(index: int) -> Path:
    """Every measurement on one background, checkpointed."""
    env = _env(index)
    k_com = _grid(env)
    cache = _cache_path(index, k_com)
    held = dict(np.load(cache)) if cache.exists() else {}

    def save() -> None:
        part = cache.with_suffix(".part.npz")
        np.savez(part, **held)
        os.replace(part, cache)

    def record(key: str, i: int, value: float) -> None:
        held.setdefault(key, np.zeros(SUM_BACK_K.size))[i] = value

    t0 = time.time()
    if "sum-back done" not in held:
        fine = _env(index, n_eta=REFINE * (env.eta.size - 1) + 1)
        for grid, suffix in ((env, ""), (fine, " fine")):
            for key, value in _weights(grid).items():
                held[f"weights {key}{suffix}"] = np.array(value)
        for i, k in enumerate(SUM_BACK_K):
            released, released_t = sum_back_mode(float(k), env)
            halved, halved_t = sum_back_mode(float(k), fine)
            for key, value in released.items():
                record(key, i, value)
            for key, value in halved.items():
                record(key + " fine", i, value)
            for frame in "NC":
                for name in ("three", "direct (i)"):
                    record(f"{name}, step halved {frame}", i, _relative(
                        halved_t[f"{name} {frame}"],
                        released_t[f"{name} {frame}"],
                        released_t[f"scale {frame}"]))
        held["sum-back done"] = np.array(1)
        save()
        print(f"   sum-back on {env.eta.size} and {fine.eta.size} points "
              f"({time.time() - t0:.0f}s)", flush=True)

    eta_0 = float(env.background.eta_0)
    shape = (CROSS_ELLS.size, k_com.size)
    for name in SLOTS:
        held.setdefault(name, np.zeros(shape))
    start = int(held.get("modes", 0))
    if start < k_com.size:
        needed = required_multipoles(CROSS_ELLS)
        table = BesselTable.build(
            ell_max=int(needed.max()), ells=needed,
            x_max=float(k_com.max() * (eta_0 - env.eta[0])) + 20.0)
        for j in range(start, k_com.size):
            k = float(k_com[j])
            kern = kernel_set(CROSS_ELLS, k, eta=env.eta, eta_0=eta_0,
                              table=table)
            s, damping = line_of_sight_inputs(
                k, covariant_coefficient_sets(k, env)[0], env)
            three = three_slots(kern, s)
            held["sw"][:, j] = damping * three.sachs_wolfe
            held["dop"][:, j] = damping * three.doppler
            held["isw"][:, j] = three.integrated
            if (j + 1) % CHECKPOINT_EVERY == 0 or j + 1 == k_com.size:
                held["modes"] = np.array(j + 1)
                save()
                print(f"   mode {j + 1} of {k_com.size} "
                      f"({time.time() - t0:.0f}s)", flush=True)
    held["k_com"] = k_com
    save()
    return cache


def cross_spectra(held: dict) -> dict[str, np.ndarray]:
    """The total C_l and its six terms as fractions of it, over CROSS_ELLS."""
    k_com = held["k_com"]
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)
    t = {n: held[n] for n in SLOTS}
    total = np.array([cl_covariant_route(int(l), k_com,
                                         t["sw"][i] + t["dop"][i] + t["isw"][i],
                                         power)
                      for i, l in enumerate(CROSS_ELLS)])
    out = {"total": total}
    for label, a, b in TERMS:
        if a == b:
            c = [cl_covariant_route(int(l), k_com, t[a][i], power)
                 for i, l in enumerate(CROSS_ELLS)]
        else:
            c = [2.0 * cl_cross(int(l), k_com, t[a][i], t[b][i], power)
                 for i, l in enumerate(CROSS_ELLS)]
        out[label] = np.array(c) / total
    return out


#: The rows of measurements 1-2, in the order the report prints them.
TWO_GRID = [f"sum-back {t} {f}{w}" for w in ("", ", V=W'")
            for t in ("(i)", "(ii)") for f in "NC"] + [
    f"five vs three {f}{w}" for w in ("", ", V=W'") for f in "NC"]
ONE_GRID = [f"{n}, step halved {f}" for n in ("three", "direct (i)")
            for f in "NC"] + [
    "stored moments, direct N", "stored moments, three N", "weights, three N"]
WEIGHT_KEYS = ("V integral", "W rise", "gap")


def _measured(held: dict) -> dict:
    """What the report reads from one background's cache, and nothing else."""
    fractions = cross_spectra(held)
    d = d_ell(CROSS_ELLS, fractions["total"])
    return {
        "modes": {**{row: held[row] for row in TWO_GRID},
                  **{row + " fine": held[row + " fine"] for row in TWO_GRID},
                  **{row: held[row] for row in ONE_GRID}},
        "weights": {f"{key}{suffix}": float(held[f"weights {key}{suffix}"])
                    for key in WEIGHT_KEYS for suffix in ("", " fine")},
        "fractions": {label: fractions[label] for label, _, _ in TERMS},
        "shape": d / np.max(d),
    }


def _from_caches() -> dict | None:
    found = {}
    for name, index in BACKGROUNDS.items():
        env = _env(index)
        path = _cache_path(index, _grid(env))
        if not path.exists():
            print(f"no cache for {name}: run --background {name} first")
            return None
        held = dict(np.load(path))
        if "k_com" not in held:
            print(f"{name} is incomplete: run --background {name} again")
            return None
        found[name] = _measured(held)
    return found


def _stamp_of(path: Path) -> str:
    with path.open(encoding="utf-8") as fh:
        first = fh.readline().strip()
    return first.removeprefix("# sources: ") if first.startswith("# sources: ") else ""


def _write_csvs(found: dict, stamp: str) -> None:
    """Every number the report prints, at full precision, under one stamp."""
    with ROOT.joinpath(*CSV_REL).open("w", encoding="utf-8", newline="") as fh:
        fh.write(f"# sources: {stamp}\n")
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["background", "ell", "d_ell_over_max"]
                   + [label for label, _, _ in TERMS])
        for name, m in found.items():
            for i, l in enumerate(CROSS_ELLS):
                w.writerow([name, int(l), repr(float(m["shape"][i]))]
                           + [repr(float(m["fractions"][label][i]))
                              for label, _, _ in TERMS])
    with ROOT.joinpath(*MODES_REL).open("w", encoding="utf-8", newline="") as fh:
        fh.write(f"# sources: {stamp}\n")
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["background", "quantity"] + [repr(float(k)) for k in SUM_BACK_K])
        for name, m in found.items():
            for key, values in m["modes"].items():
                w.writerow([name, key] + [repr(float(v)) for v in values])
            for key, value in m["weights"].items():
                w.writerow([name, f"weights {key}", repr(value)])


def _from_csvs() -> tuple[dict, str] | None:
    """The report's numbers back from the two CSVs, if this tree wrote them."""
    paths = [ROOT.joinpath(*CSV_REL), ROOT.joinpath(*MODES_REL)]
    stamps = {_stamp_of(p) if p.exists() else "" for p in paths}
    here = _digest(__file__)
    if stamps != {here}:
        print(f"REFUSED: the CSVs carry {sorted(stamps)} and this tree's sources "
              f"are {here}. --replot draws only numbers this code computed "
              "(T-54); run --background for each, then --report.")
        return None
    found: dict = {name: {"modes": {}, "weights": {}, "fractions": {},
                          "shape": None} for name in BACKGROUNDS}
    with paths[0].open(encoding="utf-8") as fh:
        rows = [r for r in csv.reader(fh) if r and not r[0].startswith("#")]
    header, rows = rows[0], rows[1:]
    for name in BACKGROUNDS:
        mine = [r for r in rows if r[0] == name]
        found[name]["shape"] = np.array([float(r[2]) for r in mine])
        for j, label in enumerate(header[3:], start=3):
            found[name]["fractions"][label] = np.array([float(r[j]) for r in mine])
    with paths[1].open(encoding="utf-8") as fh:
        rows = [r for r in csv.reader(fh) if r and not r[0].startswith("#")]
    for r in rows[1:]:
        name, key = r[0], r[1]
        if key.startswith("weights "):
            found[name]["weights"][key.removeprefix("weights ")] = float(r[2])
        else:
            found[name]["modes"][key] = np.array([float(v) for v in r[2:]])
    return found, here


def report(found: dict, stamp: str) -> int:
    lines: list[str] = []

    def say(text: str = "") -> None:
        print(text, flush=True)
        lines.append(text)

    say(__doc__.split("Each background")[0].rstrip())
    say()
    say(f"sources: {stamp}")
    say()
    bands = [f"{lo:.0f}-{hi:.0f}" for lo, hi in K_BANDS]
    say("1-2. PER MODE: max_l |difference| / max_l |three slots|, largest in "
        "each k band; l = " + ", ".join(str(l) for l in SUM_BACK_ELLS))
    say(f"   {'':38s}{'released eta step':>27s}{'half the step':>27s}")
    say(f"   {'k band':38s}" + "".join(f"{b:>9s}" for b in bands * 2))

    def band_max(values: np.ndarray) -> list[float]:
        return [float(np.max(values[(SUM_BACK_K >= lo) & (SUM_BACK_K <= hi)]))
                for lo, hi in K_BANDS]

    for name, m in found.items():
        modes = m["modes"]
        say(f"   {name}")
        for row in TWO_GRID:
            say(f"     {row:36s}" + "".join(
                f"{c:9.1e}" for c in band_max(modes[row])
                + band_max(modes[row + " fine"])))
        for row in ONE_GRID:
            say(f"     {row:36s}" + "".join(
                f"{c:9.1e}" for c in band_max(modes[row])))
        for suffix, grid in (("", "released step"), (" fine", "half step")):
            w = {key: m["weights"][f"{key}{suffix}"] for key in WEIGHT_KEYS}
            say(f"     weights, {grid}: Int V d(eta) = {w['V integral']:.6f}, "
                f"W(eta_0) - W(start) = {w['W rise']:.6f}, "
                f"max|W' - V| / max V = {w['gap']:.1e}")
    say()
    say("   SCORED: released step / half step, largest in each band; a "
        "quadrature residual falls by four")
    for name, m in found.items():
        for row in ("sum-back (i) N, V=W'", "sum-back (i) C, V=W'",
                    "sum-back (ii) N, V=W'", "sum-back (ii) C, V=W'",
                    "five vs three C, V=W'", "sum-back (i) N", "sum-back (i) C"):
            say(f"     {name:7s}{row:30s}" + "".join(
                f"{a / b:9.2f}" for a, b in zip(
                    band_max(m["modes"][row]), band_max(m["modes"][row + " fine"]))))
    say()
    say("3. CROSS-SPECTRA, Newtonian frame: each term of the total C_l as a "
        "fraction of it (the six add to 1); D/max is the total's D_l shape")
    for name, m in found.items():
        c, shape = m["fractions"], m["shape"]
        closure = np.max(np.abs(sum(c[label] for label, _, _ in TERMS) - 1.0))
        say(f"\n   {name}  (closure of the six: {closure:.1e})")
        say("      l  D/max" + "".join(f"{label:>10s}" for label, _, _ in TERMS))
        for i, l in enumerate(CROSS_ELLS):
            say(f"   {int(l):4d}  {shape[i]:5.3f}"
                + "".join(f"{c[label][i]:+10.3f}" for label, _, _ in TERMS))
        at = int(np.argmax(c["ISW"]))
        say(f"   ISW auto-spectrum / total, largest: {c['ISW'][at]:.2f} at "
            f"l = {int(CROSS_ELLS[at])}")
        # The same fractions recombined: without the integrated slot the total
        # is SW + Dop + 2SWxDop, and the Sachs-Wolfe slot alone is SW. A
        # maximum does not move under a positive scale, so the shape serves.
        for label, part in (
                ("every slot", 1.0),
                ("without the integrated slot",
                 c["SW"] + c["Dop"] + c["2SWxDop"]),
                ("the Sachs-Wolfe slot alone", c["SW"])):
            maxima = acoustic_maxima(CROSS_ELLS, shape * part)
            say(f"   maxima of D_l, {label}: "
                + (", ".join(f"{m_:.0f}" for m_ in maxima) or "none"))

    ROOT.joinpath(*TXT_REL).write_text("\n".join(lines) + "\n",
                                       encoding="utf-8")
    _draw(found)
    return 0


def _draw(found: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from functions.plotting.style import (
        DETERMINISTIC_METADATA, SERIES, SERIES_DASH, use_house_style)

    use_house_style()
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 5.6), sharex=True)
    for r, (name, held) in enumerate(found.items()):
        c = held["fractions"]
        for col, labels in enumerate((("SW", "Dop", "ISW"),
                                      ("2SWxISW", "2DopxISW", "2SWxDop"))):
            ax = axes[r, col]
            for n, label in enumerate(labels, start=1):
                ax.plot(CROSS_ELLS, c[label], color=SERIES[n],
                        ls=SERIES_DASH[n], lw=1.5, label=label)
            ax.plot(CROSS_ELLS, held["shape"], color=SERIES[4],
                    ls=SERIES_DASH[4], lw=1.0, label=r"$D_\ell/\max D_\ell$")
            ax.axhline(0.0, color=SERIES[4], lw=0.6)
            ax.set_xscale("log")
            ax.set_title(f"{name}: {'auto' if col == 0 else 'cross'}-spectra")
            if r == 1:
                ax.set_xlabel(r"$\ell$")
            if col == 0:
                ax.set_ylabel(r"fraction of $C_\ell$")
            if r == 0:
                ax.legend(frameon=False, fontsize=7)
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
        found = _from_caches()
        if found is None:
            return 1
        stamp = _digest(__file__)
        _write_csvs(found, stamp)
        loaded = _from_csvs()            # the report is drawn from what is kept
        return 1 if loaded is None else report(*loaded)
    if args.replot:
        loaded = _from_csvs()
        return 1 if loaded is None else report(*loaded)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
