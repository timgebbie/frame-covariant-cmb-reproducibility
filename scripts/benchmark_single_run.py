#!/usr/bin/env python3
r"""What one spectrum costs, stage by stage, and where the time actually goes.

    python scripts/benchmark_single_run.py

**Why this exists.** Decision **S24** froze a *factorised* interface for
v1.5.0 on a cost argument --- one forward evaluation at 23.1 s makes $10^5$
samples 27 days of serial wall clock, while the primordial step alone costs
0.64 ms --- and decision **S30** deferred run-time optimisation to a dedicated
assessment for v2.0.0. Both of those are decisions about cost, and until now the
cost was quoted from one measurement of the whole rather than broken down.

This breaks it down. **One run, one parameter set, no tests**: the physics a
reader would pay for to get an angular correlation function out of the bundle,
timed stage by stage. It is the benchmark the v2.0.0 handover is measured
against and the number v1.5.0's scope decisions should be taken on.

**A benchmark is a property of a machine, not of a repository.** The output
records the interpreter, the platform and the date beside every timing, and the
README carries the snapshot labelled as such. Nothing here is a gate, nothing
fails on a slow machine, and no release depends on a number in this file.

**Excluded, deliberately:** the regression suite, the figure scripts, the
manifests and every diagnostic. Those are what it costs to *check* the bundle,
which is a different question from what it costs to *run* it.
"""

from __future__ import annotations

import platform
import sys
import time
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    PLANCK_H,
    PLANCK_MODEL,
    PLANCK_N_S,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.angular import cl_covariant_route  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT, RecombinationHistory  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment,
    coefficient_sets,
    transfer_by_rank,
)

#: The release configuration, not a reduced one. A benchmark run on a grid
#: nobody ships measures a calculation nobody performs.
ELLS = np.unique(np.concatenate([np.array([2, 4, 7, 11, 16, 22]),
                                 np.arange(30, 1001, 30)]))
K_COM = np.arange(0.05, 1500.0, np.pi / 3.0)
THETA_DEG = np.linspace(0.0, 180.0, 721)

STAGES: list[tuple[str, float, str]] = []


@contextmanager
def stage(name: str, why: str):
    start = time.perf_counter()
    yield
    STAGES.append((name, time.perf_counter() - start, why))


def main() -> int:
    print("benchmark: one angular correlation function, all the physics")
    print(f"  {len(ELLS)} multipoles to {ELLS.max()}, {K_COM.size} modes to "
          f"{K_COM.max():.0f}, PLANCK_MODEL, f_2 = {F2_DEFAULT}")
    print(f"  {platform.python_implementation()} {platform.python_version()} on "
          f"{platform.system()} {platform.machine()}, numpy {np.__version__}")

    total_start = time.perf_counter()

    with stage("background", "one adaptive quadrature per panel; independent of k and l"):
        background = PLANCK_MODEL
        _ = background.eta_0

    with stage("recombination history",
               "a stiff Radau solve for Peebles, then the visibility and opacity"):
        recombination = RecombinationHistory.build(
            background, omega_b_h2=PLANCK_OMEGA_B_H2)

    with stage("environment and transfer function",
               "the eta grid, the potentials and the Bond-Efstathiou shape"):
        gamma = shape_parameter(background.omega_m, PLANCK_H)
        env = build_environment(
            float(K_COM.max()), omega_m=background.omega_m,
            omega_lambda=background.omega_lambda, omega_r=background.omega_r,
            omega_b_h2=PLANCK_OMEGA_B_H2, transfer_gamma=gamma,
            hubble_h=PLANCK_H, f_2=F2_DEFAULT, line_of_sight_weight="printed")

    with stage("Bessel table",
               "j_l(x) tabulated once, 12 samples per oscillation, reused by every mode"):
        needed = required_multipoles(ELLS)
        table = BesselTable.build(
            ell_max=int(needed.max()), ells=needed,
            x_max=float(K_COM.max() * (env.background.eta_0 - env.eta[0])) + 20.0)

    coefficient_time = 0.0
    projection_time = 0.0
    transfer = np.zeros((ELLS.size, K_COM.size))
    with stage("per-mode loop (total)",
               "the acoustic solve and the line-of-sight projection, once per k"):
        for j, k in enumerate(K_COM):
            t0 = time.perf_counter()
            _, cdm = coefficient_sets(float(k), env)
            t1 = time.perf_counter()
            transfer[:, j] = transfer_by_rank(ELLS, float(k), cdm, env, table)[-1]
            t2 = time.perf_counter()
            coefficient_time += t1 - t0
            projection_time += t2 - t1

    with stage("primordial power", "P(k) ~ k^{n_s-4}, one array"):
        power = primordial_power(K_COM, n_s=PLANCK_N_S, amplitude=1.0)

    with stage("k quadrature to C_l",
               "one integral over k per multipole against the stored transfer"):
        cl = np.array([cl_covariant_route(int(l), K_COM, transfer[i], power)
                       for i, l in enumerate(ELLS)])

    with stage("C_l -> C(theta)",
               "Legendre sum at 721 angles; the deliverable the reader asked for"):
        x = np.cos(np.deg2rad(THETA_DEG))
        legendre = np.polynomial.legendre.legvander(x, int(ELLS.max()))
        weights = (2 * ELLS + 1) / (4.0 * np.pi)
        _ = legendre[:, ELLS] @ (weights * cl)

    total = time.perf_counter() - total_start

    rows = [(name, seconds, 100.0 * seconds / total, why) for name, seconds, why in STAGES]
    print(f"\n  {'stage':34s} {'seconds':>9s} {'share':>7s}")
    for name, seconds, share, _ in rows:
        print(f"  {name:34s} {seconds:9.2f} {share:6.1f}%")
    print(f"  {'':34s} {'-' * 9} {'-' * 7}")
    print(f"  {'TOTAL':34s} {total:9.2f} {100.0:6.1f}%")
    print(f"\n  inside the per-mode loop: coefficients {coefficient_time:.2f} s, "
          f"projection {projection_time:.2f} s")
    print(f"  per mode: {1000 * (coefficient_time + projection_time) / K_COM.size:.1f} ms "
          f"over {K_COM.size} modes")

    out = ROOT / "outputs" / "benchmark-single-run.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# one angular correlation function, all the physics, no tests\n")
        fh.write(f"# {platform.python_implementation()} {platform.python_version()} "
                 f"on {platform.system()} {platform.machine()}, "
                 f"numpy {np.__version__}, {date.today().isoformat()}\n")
        fh.write(f"# {len(ELLS)} multipoles to {ELLS.max()}, {K_COM.size} modes "
                 f"to {K_COM.max():.0f}\n")
        fh.write("stage,seconds,share_percent,why\n")
        for name, seconds, share, why in rows:
            fh.write(f'"{name}",{seconds:.4f},{share:.2f},"{why}"\n')
        fh.write(f'"TOTAL",{total:.4f},100.00,""\n')
        fh.write(f'"  of which: coefficients",{coefficient_time:.4f},'
                 f'{100 * coefficient_time / total:.2f},"inside the per-mode loop"\n')
        fh.write(f'"  of which: projection",{projection_time:.4f},'
                 f'{100 * projection_time / total:.2f},"inside the per-mode loop"\n')
    print(f"\nwrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
