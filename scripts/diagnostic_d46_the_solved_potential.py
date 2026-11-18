#!/usr/bin/env python3
r"""D46 --- the solved potential, step 2 of sec:a3-construction, scored as registered.

QUESTION
    With the potential integrated from one start deep in the radiation era
    (`functions.spectra.radiation_era`), baryons as pressureless matter in the
    constraint, does the solve reproduce the registered numbers, do its own
    checks hold, and does the spectrum depend on the start?

WHAT IS MEASURED, on PLANCK_MODEL unless named
    1. THE START (T-194). $\Phi_A(\eta_*)/\Phi_i$ at $k=10^{-3}$ from the
       leading-order eq:radiation-ic and from the start on both constraints,
       at $\eta_i$, $\eta_i/2$ and $\eta_i/4$, against Kodama and Sasaki.
    2. THE REGISTERED NUMBERS, $k\to0$ ($k=10^{-3}$). The Sachs--Wolfe
       source $(\delta T+\Phi_A)(\eta_*)/\Phi_A(\eta_*)$ against
       $2-\tfrac32\Phi_i/\Phi_A(\eta_*)=0.379$. The radiation era's integrated
       term $[\Phi_A-\Phi_H]_{\eta_*}^{\eta_0}/\Phi_A(\eta_*)$ on PLANCK's
       $\Lambda$-free twin (same $a_{\rm eq}$, flat, last scattering at
       PLANCK's $a_*/a_{\rm eq}$), against $2[\tfrac9{10}\Phi_i-\Phi_A(\eta_*)]
       /\Phi_A(\eta_*)=-0.055$; and on PLANCK itself, where $\Lambda$'s late
       term stands beside it.
    3. THE CHECKS, per mode on a logarithmic $k$ grid: where the photons
       leave the constraint; the energy constraint over the sum of its terms'
       magnitudes at $\eta_*$ and at the exit, and the same with the baryon
       loading removed from (152), which is the control that says what the
       residual is; the photons' stress $(\Phi_A+\Phi_H)/\Phi_A$; and the
       hierarchy closed at twice `STEP_TWO_ELL_MAX`.
    4. THE TRANSFER (ruling 1, recorded, not gated): $\Phi_A(\eta_0,k)/
       \Phi_A(\eta_0,k\to0)$ against (J.5) at the shape parameter F9 uses.
    5. THE SPECTRUM, on F9's $\ell$ and $k$ grids with F9's damping and three
       slots: the largest $|\Delta D_\ell|$ over the largest $D_\ell$ when
       $\eta_i$ halves, against $10^{-4}$; the frame gap (e); and what the
       photons' anisotropic stress does to $D_\ell$, by the control
       $\Phi_A=-\Phi_H$ after $\eta_*$ (ruling 2: named and measured).

Part 5 checkpoints per mode outside the tree (`D46_CACHE`, or the system
temporary directory), keyed on the sources. `--report` writes every number the
report prints to a CSV stamped with the sources; `--replot` rewrites the report
from it alone, refusing a stamp this tree did not compute (T-54).

USAGE
    python scripts/diagnostic_d46_the_solved_potential.py            # compute, then report
    python scripts/diagnostic_d46_the_solved_potential.py --replot
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

from functions.background.flrw import (  # noqa: E402
    Background,
    PLANCK_H,
    PLANCK_MODEL,
    PLANCK_N_S,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.acoustic import common_start_eta  # noqa: E402
from functions.spectra.angular import cl_covariant_route, d_ell  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT, RecombinationHistory  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.line_of_sight import kernel_set, three_slots  # noqa: E402
from functions.spectra.pipeline import primordial_power, required_k_points  # noqa: E402
from functions.spectra.radiation_era import (  # noqa: E402
    STEP_TWO_ELL_MAX,
    kodama_sasaki,
    solve_mode,
)
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    SOLVED_PHI_I,
    TIGHT_COUPLING_FACTOR,
    build_environment,
    coefficient_sets,
    line_of_sight_inputs,
    mode_history,
)

CSV_REL = ("diagnostics", "d46-the-solved-potential.csv")

#: F9's grids, so part 5 measures the spectrum F9 draws.
ELLS = np.unique(np.concatenate([
    np.array([2, 4, 7, 11, 16, 22]),
    np.arange(30, 1001, 30),
]))
K_MAX = 1500.0

#: Part 3's modes: logarithmic, because the checks change character with
#: $k\eta_*$ and not with $k$; these are not a quadrature.
CHECK_K = np.geomspace(1e-3, K_MAX, 25)

#: Part 4's modes, in the bundle's units.
TRANSFER_K = np.geomspace(0.1, K_MAX, 13)

#: $k\to0$ for the registered numbers: $k\eta_0=3\times10^{-3}$ on PLANCK.
K_SUPERHORIZON = 1e-3

KEY_SW = "Sachs-Wolfe source over Phi_A(eta_*)"
KEY_SW_REG = "registered: 2 - (3/2) Phi_i/Phi_A(eta_*)"
KEY_RAD = "radiation-era integrated term, Lambda-free twin"
KEY_RAD_REG = "registered: 2[(9/10) Phi_i - Phi_A(eta_*)]/Phi_A(eta_*)"
KEY_TWIN = "twin Phi_A(eta_0)/Phi_i"
KEY_PLANCK_ISW = "PLANCK integrated term, radiation era and Lambda"
KEY_PLANCK_END = "PLANCK Phi_A(eta_0)/Phi_i"


def planck_environment(**kw):
    return build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m, omega_lambda=PLANCK_MODEL.omega_lambda,
        omega_r=PLANCK_MODEL.omega_r, omega_b_h2=PLANCK_OMEGA_B_H2,
        transfer_gamma=shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H),
        hubble_h=PLANCK_H, f_2=F2_DEFAULT, line_of_sight_weight="printed",
        acoustic_start="radiation era", potential="solved", **kw)


def solve(env, k, **kw):
    """One step-2 mode on `env`'s grid, as `mode_history` solves it."""
    bg = env.background
    args = dict(eta_i=env.eta_i, eta_star=env.eta_star,
                eta_couple=min(float(bg.eta_0), TIGHT_COUPLING_FACTOR * env.eta_star),
                phi_i=SOLVED_PHI_I, omega_b_h2=env.omega_b_h2)
    args.update(kw)
    return solve_mode(float(k), bg, env.eta, **args)


def the_start(env) -> dict:
    """Part 1: the leading-order start against the start on both constraints."""
    from scipy.integrate import solve_ivp
    from functions.spectra.acoustic import baryon_photon_ratio
    bg, k = env.background, K_SUPERHORIZON
    a_eq = bg.omega_r / bg.omega_m
    y_star = float(bg.a_of_eta(env.eta_star)) / a_eq
    c_m, c_g = 1.5 * bg.h0**2 * bg.omega_m, 1.5 * bg.h0**2 * bg.omega_r
    r_per_a = float(baryon_photon_ratio(1.0, omega_b_h2=env.omega_b_h2))

    def rhs(t, y):
        phi_h, d_m, v_m, d_t, tau = y
        a = float(bg.a_of_eta(t))
        h, r = float(bg.conformal_hubble(a)), r_per_a * a
        phi_a = -phi_h
        d = h * phi_a + (c_m / a * v_m + 4.0 / 3.0 * c_g / a**2 * tau) / k
        return [d, k * v_m - 3 * d, -h * v_m - k * phi_a, -d + k / 3 * tau,
                -(h * r / (1 + r)) * tau - k / (1 + r) * d_t - k * phi_a]

    out = {"kodama_sasaki": float(kodama_sasaki(y_star)[0][0]), "y_star": y_star}
    for divisor in (1, 2, 4):
        eta_i = env.eta_i / divisor
        v = -0.5 * k * eta_i
        lead = solve_ivp(lambda x, y: np.exp(x) * np.asarray(rhs(np.exp(x), y)),
                         (np.log(eta_i), np.log(env.eta_star)),
                         [-1.0, -1.5, v, -0.5, v], method="DOP853",
                         rtol=1e-11, atol=1e-16)
        both = solve_mode(k, bg, np.array([eta_i, env.eta_star]), eta_i=eta_i,
                          eta_star=env.eta_star, eta_couple=6 * env.eta_star,
                          omega_b_h2=env.omega_b_h2)
        out[f"leading-order start, eta_i/{divisor}"] = float(-lead.y[0, -1])
        out[f"start on both constraints, eta_i/{divisor}"] = float(both.phi_a_star)
    return out


def the_registered_numbers(env) -> dict:
    """Part 2: the k -> 0 Sachs-Wolfe source and integrated term."""
    bg = env.background
    m = solve(env, K_SUPERHORIZON)
    a_eq = bg.omega_r / bg.omega_m
    twin = Background(omega_m=1.0 / (1.0 + a_eq), omega_lambda=0.0,
                      omega_r=a_eq / (1.0 + a_eq))
    y_star = float(bg.a_of_eta(env.eta_star)) / a_eq
    twin_star = float(twin.eta_of_a(y_star * twin.omega_r / twin.omega_m))
    twin_i = common_start_eta(twin, K_MAX)
    t = solve_mode(K_SUPERHORIZON, twin, np.array([twin_star, float(twin.eta_0)]),
                   eta_i=twin_i, eta_star=twin_star, eta_couple=6 * twin_star,
                   phi_i=SOLVED_PHI_I, omega_b_h2=env.omega_b_h2)
    phi_i = SOLVED_PHI_I
    star = m.phi_a_star
    weyl = m.phi_a - m.phi_h
    twin_weyl = t.phi_a - t.phi_h
    return {
        "Phi_A(eta_*)/Phi_i": star / phi_i,
        KEY_SW: (m.delta_t_star + m.phi_a_star) / star,
        KEY_SW_REG: 2.0 - 1.5 * phi_i / star,
        KEY_RAD: float((twin_weyl[-1] - twin_weyl[0]) / t.phi_a[0]),
        KEY_RAD_REG: float(2.0 * (0.9 * phi_i - star) / star),
        KEY_TWIN: float(t.phi_a[-1] / phi_i),
        KEY_PLANCK_ISW: float(
            (weyl[-1] - np.interp(env.eta_star, m.eta, weyl)) / star),
        KEY_PLANCK_END: float(m.phi_a[-1] / phi_i),
    }


def the_checks(env) -> dict[str, np.ndarray]:
    """Part 3, per mode on CHECK_K."""
    rows = {key: [] for key in (
        "eta_exit", "energy residual at eta_*", "energy residual at exit",
        "energy residual at eta_*, R -> 0", "stress max after eta_*",
        "stress at exit", "hierarchy at 2 ell_max, max |dPhi_A|/max |Phi_A|",
        "energy residual at exit, R -> 0",
        "energy residual at exit, R -> 0 and Phi_A = -Phi_H")}
    for k in CHECK_K:
        m = solve(env, k)
        bare = solve(env, k, omega_b_h2=1e-12)
        flat = solve(env, k, omega_b_h2=1e-12, anisotropic_stress=False)
        wide = solve(env, k, ell_max=2 * STEP_TWO_ELL_MAX)
        rows["energy residual at exit, R -> 0"].append(bare.energy_residual_exit)
        rows["energy residual at exit, R -> 0 and Phi_A = -Phi_H"].append(
            flat.energy_residual_exit)
        rows["eta_exit"].append(m.eta_exit)
        rows["energy residual at eta_*"].append(m.energy_residual_star)
        rows["energy residual at exit"].append(m.energy_residual_exit)
        rows["energy residual at eta_*, R -> 0"].append(bare.energy_residual_star)
        rows["stress max after eta_*"].append(m.stress_max)
        rows["stress at exit"].append(m.stress_exit)
        rows["hierarchy at 2 ell_max, max |dPhi_A|/max |Phi_A|"].append(
            float(np.max(np.abs(wide.phi_a - m.phi_a)) / np.max(np.abs(m.phi_a))))
    return {key: np.array(v, dtype=float) for key, v in rows.items()}


def the_transfer(env) -> dict[str, np.ndarray]:
    """Part 4: the solved late-time transfer against (J.5)."""
    zero = solve(env, K_SUPERHORIZON).phi_a[-1]
    solved = np.array([solve(env, k).phi_a[-1] / zero for k in TRANSFER_K])
    fitted = np.array([env.transfer_at(float(k)) for k in TRANSFER_K])
    return {"solved Phi(k)/Phi(k->0) at eta_0": solved, "(J.5)": fitted}


def the_start_halved(env) -> dict:
    """Part 5: F9's spectrum at eta_i and eta_i/2, both frames, checkpointed."""
    halved = dataclasses.replace(env, eta_i=env.eta_i / 2.0)
    eta_0 = float(env.background.eta_0)
    r_theta = float(eta_0 - env.eta_star)
    k_com = np.linspace(0.05, K_MAX, required_k_points(K_MAX, r_theta))
    needed = required_multipoles(ELLS)
    table = BesselTable.build(ell_max=int(needed.max()), ells=needed,
                              x_max=float(k_com.max() * (eta_0 - env.eta[0])) + 20.0)
    key = hashlib.sha256((_digest(__file__) + repr((k_com.size, K_MAX))).encode()).hexdigest()[:16]
    cache = Path(os.environ.get("D46_CACHE", tempfile.gettempdir())) / f"d46-modes-{key}.npz"
    names = ("newtonian", "cdm", "cdm, eta_i/2", "cdm, Phi_A = -Phi_H")
    transfer = {n: np.zeros((ELLS.size, k_com.size)) for n in names}
    start = 0
    if cache.exists():
        held = np.load(cache)
        if held[names[0]].shape == transfer[names[0]].shape:
            transfer = {n: held[n].copy() for n in names}
            start = int(held["done"])
            print(f"      resuming at mode {start} of {k_com.size}", flush=True)
    t0 = time.time()
    for j, k in enumerate(k_com):
        if j < start:
            continue
        kern = kernel_set(ELLS, float(k), eta=env.eta, eta_0=eta_0, table=table)
        runs = ((env, mode_history(float(k), env), ("newtonian", "cdm")),
                (halved, mode_history(float(k), halved), (None, "cdm, eta_i/2")),
                (env, mode_history(float(k), env, anisotropic_stress=False),
                 (None, "cdm, Phi_A = -Phi_H")))
        for e, history, wanted in runs:
            sets = coefficient_sets(float(k), e, source="paper 1", history=history)
            for name, cs in zip(wanted, sets):
                if name is None:
                    continue
                sources, damping = line_of_sight_inputs(float(k), cs, e)
                transfer[name][:, j] = three_slots(kern, sources).transfer(damping)
        if (j + 1) % 50 == 0 or j + 1 == k_com.size:
            tmp = cache.with_suffix(".tmp.npz")
            np.savez(tmp, done=j + 1, **transfer)
            os.replace(tmp, cache)
            if (j + 1) % 250 == 0:
                print(f"      mode {j + 1:5d} of {k_com.size} "
                      f"({time.time() - t0:.0f} s)", flush=True)
    power = primordial_power(k_com, n_s=PLANCK_N_S, amplitude=1.0)
    d = {n: d_ell(ELLS, np.array([cl_covariant_route(int(l), k_com, block[i], power)
                                   for i, l in enumerate(ELLS)]))
         for n, block in transfer.items()}
    top = float(np.max(np.abs(d["cdm"])))
    return {
        "modes": float(k_com.size),
        "max |D_l(eta_i/2) - D_l(eta_i)| / max D_l": float(
            np.max(np.abs(d["cdm, eta_i/2"] - d["cdm"])) / top),
        "frame gap (e), max |D_l^N - D_l^CDM| / max D_l": float(
            np.max(np.abs(d["newtonian"] - d["cdm"])) / top),
        "the stress: max |D_l(Phi_A = -Phi_H) - D_l| / max D_l": float(
            np.max(np.abs(d["cdm, Phi_A = -Phi_H"] - d["cdm"])) / top),
        "the stress at l = 2: D_2(Phi_A = -Phi_H) / D_2 - 1": float(
            d["cdm, Phi_A = -Phi_H"][0] / d["cdm"][0] - 1.0),
        "D_l": d["cdm"],
        "D_l, Phi_A = -Phi_H": d["cdm, Phi_A = -Phi_H"],
    }


def compute() -> dict:
    env = planck_environment()
    found = {}
    print("    1. the start", flush=True)
    found["start"] = the_start(env)
    print("    2. the registered numbers", flush=True)
    found["registered"] = the_registered_numbers(env)
    print("    3. the checks", flush=True)
    found["checks"] = the_checks(env)
    print("    4. the transfer", flush=True)
    found["transfer"] = the_transfer(env)
    print("    5. the start halved, on F9's grids", flush=True)
    found["halved"] = the_start_halved(env)
    return found


def _write_csv(found: dict, stamp: str) -> None:
    path = ROOT.joinpath(*CSV_REL)
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(f"# sources: {stamp}\n")
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["part", "quantity", "values"])
        for part in ("start", "registered"):
            for q, v in found[part].items():
                w.writerow([part, q, repr(float(v))])
        w.writerow(["checks", "k", *[repr(float(k)) for k in CHECK_K]])
        for q, v in found["checks"].items():
            w.writerow(["checks", q, *[repr(float(x)) for x in v]])
        w.writerow(["transfer", "k", *[repr(float(k)) for k in TRANSFER_K]])
        for q, v in found["transfer"].items():
            w.writerow(["transfer", q, *[repr(float(x)) for x in v]])
        w.writerow(["halved", "ell", *[str(int(l)) for l in ELLS]])
        for q, v in found["halved"].items():
            if q.startswith("D_l"):
                w.writerow(["halved", q, *[repr(float(x)) for x in v]])
            else:
                w.writerow(["halved", q, repr(float(v))])


def _from_csv() -> tuple[dict, str] | None:
    path = ROOT.joinpath(*CSV_REL)
    here = _digest(__file__)
    stamp = ""
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            first = fh.readline().strip()
        stamp = first.removeprefix("# sources: ")
    if stamp != here:
        print(f"REFUSED: the CSV carries {stamp or 'nothing'} and this tree's "
              f"sources are {here}. --replot draws only numbers this code "
              "computed (T-54); run without it first.")
        return None
    found: dict = {"start": {}, "registered": {}, "checks": {}, "transfer": {},
                   "halved": {}}
    with path.open(encoding="utf-8") as fh:
        rows = [r for r in csv.reader(fh) if r and not r[0].startswith("#")][1:]
    for part, q, *vals in rows:
        if part in ("start", "registered") or (
                part == "halved" and q != "ell" and not q.startswith("D_l")):
            found[part][q] = float(vals[0])
        elif q not in ("k", "ell"):
            found[part][q] = np.array([float(v) for v in vals])
    return found, here


def report(found: dict, stamp: str) -> int:
    say = print
    say("D46 --- the solved potential, step 2, on PLANCK_MODEL")
    say(f"sources: {stamp}")
    s = found["start"]
    say("\n1. THE START (T-194): Phi_A(eta_*)/Phi_i at k = 1e-3")
    say(f"   Kodama-Sasaki at a_*/a_eq = {s['y_star']:.4f}: {s['kodama_sasaki']:.9f}")
    for d in (1, 2, 4):
        lead = s[f"leading-order start, eta_i/{d}"]
        both = s[f"start on both constraints, eta_i/{d}"]
        say(f"   eta_i/{d}: leading-order {lead:.7f} ({lead - s['kodama_sasaki']:+.2e});"
            f" on both constraints {both:.9f} ({both - s['kodama_sasaki']:+.1e})")
    r = found["registered"]
    say("\n2. THE REGISTERED NUMBERS, k -> 0")
    say(f"   Phi_A(eta_*) = {r['Phi_A(eta_*)/Phi_i']:.7f} Phi_i")
    say(f"   Sachs-Wolfe source {r[KEY_SW]:.5f} Phi_A(eta_*)   registered {r[KEY_SW_REG]:.5f}")
    say(f"   radiation era's integrated term (Lambda-free twin) {r[KEY_RAD]:+.5f} "
        f"Phi_A(eta_*)   registered {r[KEY_RAD_REG]:+.5f}")
    say(f"   the twin's Phi_A(eta_0) = {r[KEY_TWIN]:.6f} Phi_i")
    say(f"   PLANCK's integrated term, radiation era and Lambda: {r[KEY_PLANCK_ISW]:+.5f} "
        f"Phi_A(eta_*); Phi_A(eta_0) = {r[KEY_PLANCK_END]:.5f} Phi_i")
    c = found["checks"]
    say("\n3. THE CHECKS, per mode")
    say("   E is the energy constraint over the sum of its terms' magnitudes;"
        " R -> 0 removes the baryon loading from (152)")
    say("        k  eta_exit  E(eta_*)  E(exit)  | R->0: E(eta_*)  E(exit)  no stress"
        "  | stress max  at exit | 2 ell_max")
    for i, k in enumerate(CHECK_K):
        say(f"   {k:8.3g} {c['eta_exit'][i]:7.4f}  {c['energy residual at eta_*'][i]:+.1e}"
            f"  {c['energy residual at exit'][i]:+.1e}"
            f"  |  {c['energy residual at eta_*, R -> 0'][i]:+.1e}"
            f"  {c['energy residual at exit, R -> 0'][i]:+.1e}"
            f"  {c['energy residual at exit, R -> 0 and Phi_A = -Phi_H'][i]:+.1e}"
            f"  |  {c['stress max after eta_*'][i]:.2e}  {c['stress at exit'][i]:+.1e}"
            f" | {c['hierarchy at 2 ell_max, max |dPhi_A|/max |Phi_A|'][i]:.1e}")
    t = found["transfer"]
    say("\n4. THE TRANSFER at eta_0, solved against (J.5) (recorded, not gated)")
    for i, k in enumerate(TRANSFER_K):
        say(f"   k = {k:8.3g}   solved {t['solved Phi(k)/Phi(k->0) at eta_0'][i]:.4f}"
            f"   (J.5) {t['(J.5)'][i]:.4f}")
    h = found["halved"]
    say("\n5. THE SPECTRUM, F9's grids, three slots, CDM frame")
    say(f"   modes {int(h['modes'])}; max |D_l(eta_i/2) - D_l(eta_i)| / max D_l = "
        f"{h['max |D_l(eta_i/2) - D_l(eta_i)| / max D_l']:.2e}   (registered < 1e-4)")
    say(f"   (e) frame gap: {h['frame gap (e), max |D_l^N - D_l^CDM| / max D_l']:.2e}"
        "   (registered < 1e-12)")
    say(f"   the photons' stress, by the control Phi_A = -Phi_H after eta_*: max |dD_l| / max D_l "
        f"= {h['the stress: max |D_l(Phi_A = -Phi_H) - D_l| / max D_l']:.2e}, "
        f"D_2 moves by {h['the stress at l = 2: D_2(Phi_A = -Phi_H) / D_2 - 1']:+.2e}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--replot", action="store_true",
                    help="rewrite the report from the stamped CSV alone")
    args = ap.parse_args()
    if not args.replot:
        found = compute()
        _write_csv(found, _digest(__file__))
    loaded = _from_csv()
    if loaded is None:
        return 1
    return report(*loaded)


if __name__ == "__main__":
    raise SystemExit(main())
