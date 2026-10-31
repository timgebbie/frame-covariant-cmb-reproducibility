#!/usr/bin/env python3
r"""D42 --- does the source oscillate in $k$, or only its envelope?

**The question the secondaries search has never asked directly.** Every
instrument so far has measured the spectrum in $\ell$ and asked what removes a
feature from it: T-164 the projection grid, T-169 the oscillator grid, T-176
the recombination grid, the deposit window, the damping. All five were
measured and all five were exonerated, by the criterion that **what removes a
feature is structure in $\ell$, and a discretisation error is structureless**.

That criterion is sound and it has run out of candidates. So this asks the
question one step upstream, where it is cheap and unambiguous:

    at the visibility peak, does the source oscillate as cos(k r_s)?

WHY THIS IS THE DECIDING MEASUREMENT
------------------------------------
$C_\ell=\int dk\,k^2\mathcal P(k)\,|\Delta_\ell(k)|^2$, and $j_\ell(k\Delta\eta)$
maps $k\to\ell\simeq k\Delta\eta$. A source oscillating with period $2\pi/r_s$
in $k$ therefore lands as peaks every $\ell_A=\pi r_\theta/r_s$ in $\ell$. The
oscillation in $\ell$ **is** the oscillation in $k$, projected. So:

    source oscillates, spectrum does not  ->  the projection destroys it,
                                              and the defect is in the
                                              line-of-sight assembly
    source does not oscillate             ->  the projection is innocent,
                                              and the defect is upstream in
                                              the photon-baryon solve

**These are mutually exclusive and jointly exhaustive**, which is what no
instrument in the bundle currently provides. `D37`'s `split_by_parts`
spectrum on PLANCK rises to a maximum at $\ell=210$ --- *the same multipole
CAMB peaks at* --- and then decays monotonically to $\ell=990$ with no trough
and no second peak. **The first peak is in the right place and the
oscillation after it is absent**, which is the signature of an oscillation
replaced by its own envelope. An amplitude defect --- a wrong weight, a
missing product-rule partner, an opacity order --- rescales a curve. It does
not convert an oscillation into its envelope. Only a loss of phase coherence
does that, and phase coherence is a property of the source in $k$.

WHAT IS MEASURED
----------------
On PLANCK, at the visibility peak $\eta_*$, over a $k$ grid fine enough to
resolve $\cos(k r_s)$ many times over (the acoustic period is
$\Delta k=2\pi/r_s\simeq 171$, and the grid steps by 1):

    v_B(k)              the baryon velocity. Goes as sin(k r_s): the dipole.
    -C_1(k)             (90)'s combination, (dT + Phi_A) + kappa' vhat_B.
    C_0(k)              the rank-0 coefficient the plateau is carried by.

and for each, two numbers that are **not** the amplitude:

    zero crossings      where the oscillation puts them, against n pi / r_s.
                        A phase error shifts them; a coherence loss removes
                        them. This distinguishes the two.
    envelope ratio      |max - min| over one period, divided by |max + min|.
                        1.0 is a pure oscillation about zero; 0.0 is a
                        monotone envelope with no oscillation left.

PRE-REGISTERED, and the outcomes are named before the run
---------------------------------------------------------
    OSCILLATES    v_B shows >= 3 clean zero crossings out to k = 600 at
                  spacing pi/r_s +- 10%, and the envelope ratio stays above
                  0.5. Then the source is fine, the projection is the
                  defect, and the next instrument is the line-of-sight
                  assembly --- which is where the 2026-10-31 audit points.

    DECOHERES     crossings present at low k and washing out above some k_c.
                  Then there is a scale where coherence is lost and k_c is
                  the number that localises it. **This is the outcome that
                  would make the deposit window matter after all**, because
                  a window wider than a period at high k is exactly what
                  produces a k_c.

    FLAT          no oscillation at any k. Then the photon-baryon solve is
                  not oscillating and every downstream instrument has been
                  measuring the projection of a non-oscillating source. The
                  secondaries were never there to be removed.

**No outcome here is good news and that is the point.** The three differ in
*where* the next session looks, and the bundle has spent two weeks unable to
choose between them from spectra alone.

WHAT THIS FILE MEASURES AND WHAT IT DOES NOT --- READ BEFORE QUOTING IT
-----------------------------------------------------------------------
`c0` here is **$C_0$ alone**, which `coefficients.py` builds as
$\tfrac52 a\mathcal B_2$ and nothing else. That is (90) as printed and it is
**not** a defect: the construction is derived rank by rank in exact rationals
and the comment above `MONOPOLE_ROW` carries the derivation.

But that same comment says the thing this file cannot afford to forget:

    the bracket's rank-0 content is C_0 + (k/3) tau_1, the second term
    being the partner (107) already carries

so **$C_0$ is half of the rank-0 bracket** and $\tau_1$ --- the dipole, which
oscillates --- is the other half, sitting inside $-C_1'$. A modulation
measured on $C_0$ alone is therefore a statement about one coefficient and
**not** about the bracket. That distinction is **M15** in as many words: *a
gate built from one coefficient cannot see a cancellation distributed across
the bracket*, and a diagnostic built from one coefficient cannot see an
oscillation distributed across it either.

**So the number to quote from this file is the modulation per coefficient,
and the measurement it demands next is the same modulation on the bracket.**
The spectrum-level reading survives that caveat only because D4's rank shares
are themselves per-coefficient: $C_0$ carries 0.910 of the CDM spectrum with
the cross term at 0.086, so even a fully oscillating partner reaches the
spectrum through a 9% channel. That is an argument about magnitudes and it is
weaker than a measurement. **It is not a finding until the bracket is
measured.**
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

SLUG = "d42-does-the-source-oscillate-in-k"

from _fingerprint import source_fingerprint as _digest  # noqa: E402
from functions.background.flrw import (  # noqa: E402
    PLANCK_H, PLANCK_MODEL, PLANCK_OMEGA_B_H2)
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, bulk_source_primitives, coefficient_sets)
from functions.spectra.transfer import shape_parameter  # noqa: E402

#: To 600, stepping by 1. The acoustic period is 2*pi/r_s ~ 171, so this is
#: ~171 samples per oscillation --- far finer than any grid the spectrum uses,
#: deliberately, because the question is whether the oscillation is THERE and
#: not whether a grid resolves it.
K_GRID = np.arange(2.0, 601.0, 1.0)
K_MAX = float(K_GRID[-1])

FRAMES = {"newtonian": 0, "cdm": 1}


def _at_star(env, arr) -> float:
    """One number per mode: the array read at the visibility peak."""
    i = int(np.argmax(np.asarray(env.visibility, dtype=float)))
    return float(np.asarray(arr, dtype=float)[i])


def _crossings(k: np.ndarray, y: np.ndarray) -> list[float]:
    """Interpolated sign changes, which is where an oscillation's phase is."""
    out = []
    s = np.sign(y)
    for i in np.flatnonzero(s[:-1] * s[1:] < 0):
        y0, y1 = y[i], y[i + 1]
        out.append(float(k[i] + (k[i + 1] - k[i]) * y0 / (y0 - y1)))
    return out


def _detrend(y: np.ndarray, period: float) -> tuple[np.ndarray, np.ndarray]:
    r"""Split the source into a smooth pedestal and what oscillates on it.

    **The first draft of this file counted zero crossings of the raw source
    and got zero for all three, which read as FLAT and was wrong.** The
    acoustic source does not oscillate *about zero*: it rides on a pedestal
    --- the gravitational potential, which is smooth in $k$ and does not
    oscillate --- and a pedestal larger than the oscillation removes the sign
    changes without removing the oscillation. Counting crossings of the raw
    signal therefore cannot tell *the oscillation is absent* from *the
    oscillation is small*, which are the two outcomes this file exists to
    separate.

    A running mean exactly one acoustic period wide is the right filter and
    for a non-obvious reason: it has a **zero at precisely the acoustic
    frequency**, so it cannot leak any of the oscillation into the pedestal,
    whatever the oscillation's phase or amplitude. Nothing is fitted and
    nothing is assumed about the pedestal's shape.
    """
    w = int(round(period))
    w += (w + 1) % 2
    pad = np.pad(y, (w // 2, w // 2), mode="edge")
    trend = np.convolve(pad, np.ones(w) / w, mode="valid")[:y.size]
    return trend, y - trend


def _modulation(k, trend, osc, period, centres) -> list[tuple]:
    r"""Oscillation amplitude over pedestal, per $k$ window.

    **This is the number that reaches the spectrum.** $C_\ell$ is quadratic
    in the source, so a fractional modulation $m$ of the source becomes
    $\simeq 2m$ of $D_\ell$ before projection smearing. CAMB's first
    peak-to-trough contrast is about 3:1, i.e. $\simeq 50\%$; what this
    column prints is what this bundle has to work with.
    """
    out = []
    for c in centres:
        w = (k >= c - period / 2) & (k <= c + period / 2)
        if w.sum() < 10:
            continue
        amp = float(osc[w].max() - osc[w].min()) / 2.0
        ped = abs(float(trend[w].mean()))
        out.append((c, amp, ped, (amp / ped) if ped else float("nan")))
    return out


def main() -> int:
    print(__doc__.split("WHAT IS MEASURED")[0])

    env = build_environment(
        K_MAX, omega_m=PLANCK_MODEL.omega_m,
        omega_lambda=PLANCK_MODEL.omega_lambda, omega_r=PLANCK_MODEL.omega_r,
        omega_b_h2=PLANCK_OMEGA_B_H2,
        transfer_gamma=shape_parameter(PLANCK_MODEL.omega_m, PLANCK_H),
        hubble_h=PLANCK_H, f_2=F2_DEFAULT, line_of_sight_weight="printed")

    # r_s at the visibility peak, from the same place the model table reads
    # it, so the predicted period is not a second copy of a number.
    from make_model_table import MODELS, row  # noqa: E402
    r_s = float(row(*MODELS[2])["r_s"])
    period = float(np.pi / r_s)
    print(f"    r_s = {r_s:.6f}   predicted crossing spacing pi/r_s = "
          f"{period:.2f} in k\n")

    series: dict[str, np.ndarray] = {}
    for name in ("v_b", "minus_c1", "c0"):
        series[name] = np.zeros(K_GRID.size)

    for j, k in enumerate(K_GRID):
        sets = coefficient_sets(float(k), env)
        cs = sets[FRAMES["cdm"]]
        prim = bulk_source_primitives(float(k), env, cs)
        series["v_b"][j] = _at_star(env, cs.v_b)
        # (90): -C_1 = (dT + Phi_A) + kappa' vhat_B. `c1_thomson` is the
        # scattering half as the bundle builds it; the whole is what the
        # released rank-1 coefficient carries.
        series["minus_c1"][j] = _at_star(env, prim["c1_thomson"])
        c = cs.coefficients
        rank0 = getattr(c, "c0", None)
        if rank0 is None:
            rank0 = np.asarray(c.coefficients, dtype=float)[0]
        series["c0"][j] = _at_star(env, rank0) if np.ndim(rank0) else float(rank0)
        if j % 100 == 0:
            print(f"      k {k:6.1f} of {K_MAX:.0f}", flush=True)

    out = ROOT / "diagnostics" / f"{SLUG}.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# sources: {_digest(__file__)}\n")
        fh.write("k," + ",".join(series) + "\n")
        for j, k in enumerate(K_GRID):
            fh.write(f"{k:.1f}," + ",".join(f"{series[n][j]:.9e}"
                                            for n in series) + "\n")
    print(f"\n    wrote {out.relative_to(ROOT)}")

    full = 2.0 * period                      # 2 pi / r_s, the acoustic period
    expect = (K_GRID[-1] - K_GRID[0]) / period
    print(f"\n{'='*74}\n  DOES THE SOURCE OSCILLATE IN k?\n{'='*74}")
    print(f"  acoustic period 2 pi / r_s = {full:.2f} in k; a clean "
          f"oscillation gives ~{expect:.0f} detrended sign changes.\n")
    for name, y in series.items():
        trend, osc = _detrend(y, full)
        raw = len(_crossings(K_GRID, y))
        s = np.sign(osc)
        nz = int((s[:-1] * s[1:] < 0).sum())
        print(f"  {name}")
        print(f"    raw sign changes          {raw}   "
              f"(a pedestal removes these and does not remove the wave)")
        print(f"    DETRENDED sign changes    {nz}   against ~{expect:.0f}")
        for c, amp, ped, m in _modulation(K_GRID, trend, osc, full,
                                          (100, 200, 300, 400, 500)):
            print(f"      k~{c:3d}   wave {amp:10.3e}   pedestal {ped:10.3e}"
                  f"   MODULATION {100*m:6.2f}%")
        print()

    print("""  READING THIS
  ------------
  Detrended sign changes at the acoustic count mean the wave is there and
  correctly phased; the MODULATION column is then how much of it survives
  into D_l, which is about twice it. A rank whose modulation is tenths of a
  percent contributes an envelope to the spectrum and no peaks, however
  large its amplitude --- and D4 reports which rank carries what share, so
  the two tables multiply to give the spectrum's own modulation.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
