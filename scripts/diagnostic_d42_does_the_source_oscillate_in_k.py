#!/usr/bin/env python3
r"""D42 --- does the released source oscillate in $k$ at the visibility peak?

QUESTION
--------
The released spectrum (F9) is built from three slots, each invariant under a
change of frame --- the supplement's eq:assembly-invariant, coded as
`line_of_sight.three_slots`. At the visibility peak $\eta_\ast$, does each
slot's source oscillate in $k$ as $A\cos(kr_s-\theta)$ on a smooth pedestal,
coherently out to $k=600$, with the sound horizon $r_s$ of the model table?
And with what amplitude against its pedestal, and in what phase?

WHY IN $k$
----------
$C_\ell=\int dk\,k^2\mathcal P(k)\,|\Delta_\ell(k)|^2$ and $j_\ell(k\Delta\eta)$
maps $k\to\ell\simeq k\,r_\theta$. One slot whose source is $P+A\cos(kr_s-\theta)$
puts $2PA\cos(kr_s-\theta)$ into $|\Delta_\ell|^2$, period $2\pi/r_s$, and
$\tfrac12A^2\cos(2kr_s-2\theta)$, period $\pi/r_s$, which projects to one
maximum every $\ell_A=\pi r_\theta/r_s$. So $A/|P|$ is the number that decides
which of the two a slot contributes: a source that oscillates through zero
($A>|P|$) carries the series at $\ell_A$ on its own. The slots then add with
different kernels ($j_\ell$ against $j_\ell'$), so a Doppler source in
quadrature with the Sachs--Wolfe source fills the troughs the latter leaves.
This file measures the sources; D44 measures what the projection makes of
them.

THE OBJECTS
-----------
From `three_slots`'s integrands, read at $\eta_\ast$ (the visibility maximum),
on PLANCK, in the environment F9 builds (`acoustic_start="radiation era"`,
`potential="solved"`, the printed weight) and with Paper 1's source signs
(`covariant_coefficient_sets`):

    sachs_wolfe   -(C_1^grav - C_2')            multiplies  V j_l
    doppler       k (vhat_B + C_2)              multiplies  V j_l'
    integrated    C_0 - (C_1^grav' - C_2'')     multiplies  W j_l
    c0            C_0                           (in the integrated slot)

In the Newtonian frame $C_2\equiv0$, so the first two are $-(\delta T+\Phi_A)$
and $v_B$: the Sachs--Wolfe temperature and the baryon velocity. The Doppler
source carries the slot's own factor $k$, so that each object is the
coefficient of its kernel. $C_0$ under Paper 1's source carries
$a\mathcal B_0=-\tfrac k3\tau_1$ and is the antecedent's bracket
$C_0+\tfrac k3\tau_1$ identically.

The coefficients carry no diffusion: Silk damping enters the line of sight as
$e^{-(k/k_D)^2}$ (`line_of_sight_inputs`), so an amplitude that does not fall
with $k$ here is the construction, not a finding.

THE INSTRUMENT
--------------
In windows one acoustic period ($2\pi/r_s$) wide, centred at $k=100,\dots,500$,
a linear least-squares fit

    y = p_0 + p_1 x + p_2 x^2 + p_3 x^3
        + (a + a_1 x) cos(k r_s) + (b + b_1 x) sin(k r_s),
    x = (k - c) / (2 pi / r_s)

gives at the window's centre the pedestal $P=p_0$, the amplitude
$A=\sqrt{a^2+b^2}$ and the phase $\theta=\operatorname{atan2}(b,a)$, the wave
being $A\cos(kr_s-\theta)$; $a_1,b_1$ carry the amplitude's own slope across
the window, which every object here has. A phase constant from window to
window is an oscillation at the table's sound horizon. A source whose own
sound horizon is $r_s+\delta$ has $\theta$ falling as $-\delta c$; iterating
$r\to r-d\theta/dc$ to its fixed point returns it. The window at $k=100$ spans
$k\approx15$--$185$, where the pedestal turns over on the scale of the window:
it is reported and not scored, and the sound horizon is fitted on the four
windows above it.

CONTROLS, run before any series is read
---------------------------------------
    instrument   On the same grid and windows: three smooth pedestals with no
                 wave (a logarithm, a power law turning over at low k, a
                 slow tanh-and-sine) leak an amplitude that sets each window's
                 floor, which enters the outcome below as a threshold. Each
                 series is then calibrated on known waves with its own
                 amplitude envelope and its own A/|P| on those three
                 pedestals, sound horizon detuned by -5%, 0, +2% and +8%: the
                 worst error in the returned sound horizon is that series'
                 bias, printed beside it, and a bias above 1% leaves its
                 sound-horizon leg unscored.
    frame        Each series agrees between the Newtonian and CDM frames over
                 the visibility window to 1e-8 relative: the objects are
                 physical, and a modulation read off one frame is read off
                 both.
    identity     C_0 under Paper 1's source equals C_0 - a B_0 under the
                 antecedent's, over the visibility window, to 1e-10 relative,
                 on every tenth mode.

OUTCOMES, fixed before this version first ran
---------------------------------------------
    COHERENT    in every scored window A > 10 max(rms residual, floor |P|),
                and the source's sound horizon within 2% of the table's.
    DECOHERES   windows pass at low k and fail above some k_c; k_c is then
                the number.
    FLAT        no scored window passes.

Expected from the tight-coupling solution: COHERENT in all three slots, and
the Doppler source in quadrature with the Sachs--Wolfe source, their phases
differing by pi/2. The phase difference is reported and not scored.

The first run fitted a constant amplitude in each window and read the Doppler
source as $\hat v_B+C_2$. A known wave with an amplitude falling as $1/k$,
which $\hat v_B$ carries, came back with its sound horizon 3% short --- the
size of what that run returned for the Doppler slot, 0.964 --- and with the
quadrature drifting from 0.39 to 0.88 of pi/2 across the windows. The
instrument is repaired as written above (the envelope terms, the slot's own
coefficient, the per-series calibration); the outcomes are not changed. The
first run also held the floor to 2e-3 of the pedestal as a pass-or-fail of
its own; with the envelope terms the floor at k~200 is 2.5e-3, and since the
floor already sets the threshold inside COHERENT, it is that and nothing more.

READ ON v1.4.0 (the report beside the CSV carries every number)
---------------------------------------------------------------
All four sources oscillate coherently to k = 585, and the frames agree to
2.5e-13. The Sachs--Wolfe and Doppler sources oscillate through zero
(A/|P| from 4 to 340) at the table's sound horizon (0.992 and 0.991, the
instrument's bias on their shapes 0.3%), and the Doppler source is in
quadrature with the Sachs--Wolfe source to 1.3% of pi/2 in every scored
window: it fills the troughs the Sachs--Wolfe slot leaves. Against the
environment of 3 November (`--antecedent`), the radiation era multiplies the
Sachs--Wolfe wave at eta_* by 8 at k~200 and 44 at k~500, lifts it off its
pedestal (A/|P| 0.5--0.8 there), and turns an amplitude falling with k into
one rising towards saturation: the driving of modes that enter the horizon
in the radiation era, which the matter-era start could not see. The integrated
slot, smooth there, now carries a wave of the potential's own, A/|P| about 1,
whose phase moves by 0.5 rad between k~200 and 500; its sound-horizon leg is
unscored, the instrument's bias on that shape being 2.3%.

USAGE
-----
    python scripts/diagnostic_d42_does_the_source_oscillate_in_k.py
    python scripts/diagnostic_d42_does_the_source_oscillate_in_k.py --antecedent

The first writes the series to `diagnostics/d42-does-the-source-oscillate-in-k.csv`
(stamped with the sources) and the report beside it. `--antecedent` builds the
environment of 3 November instead (start "derived", the released potential)
and prints the same report without writing: on it `c0` is the bracket column
that run recorded, to the last digit.

HISTORY
-------
Built on 1 November to ask where the peak series was lost, when the released
spectrum had a first maximum at $\ell=210$ and no trough after it. Its first
draft counted zero crossings of the raw source and read FLAT; the second
counted crossings after a running mean one period wide, and on 3 November read
the antecedent's bracket as oscillating through zero, amplitude 6.5--6.8 at
$k\sim100$--$300$, while $C_0$ alone in the CDM frame was two smooth pedestals
cancelling. Restated on 19 November: it measured a matching, start and
potential the release no longer uses; its `minus_c1` column was $C_1$'s
Thomson half $-\kappa'v_B/k$, which at fixed $\eta_\ast$ is $v_B/k$ rescaled;
a crossing count cannot see phase, so "correctly phased" had not been
measured; and the running mean's width was a number of samples, equal to the
period only because the grid steps by one. The question it was built for is
answered by F9 and D44, whose spectra carry maxima at 210, 480 and 720 and a
minimum at 360.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _fingerprint import source_fingerprint as _digest  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra.transfer import shape_parameter  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, coefficient_sets, covariant_coefficient_sets,
    line_of_sight_inputs)
from make_model_table import MODELS, row  # noqa: E402

SLUG = "d42-does-the-source-oscillate-in-k"
VERSION = "v1.4.0"
CSV_REL = ("diagnostics", f"{SLUG}.csv")
TXT_REL = ("diagnostics", f"{SLUG}-{VERSION}.txt")

#: Step one to 600: about 171 samples per acoustic period, so each window
#: holds that many points against the fit's six parameters.
K_GRID = np.arange(2.0, 601.0, 1.0)
K_MAX = float(K_GRID[-1])
#: Window centres. The first is reported and not scored (see THE INSTRUMENT).
CENTRES = (100.0, 200.0, 300.0, 400.0, 500.0)
SCORED = CENTRES[1:]
PEDESTAL_DEGREE = 3
IDENTITY_EVERY = 10

FRAME_BAR = 1e-8
IDENTITY_BAR = 1e-10
CALIBRATION_BAR = 1e-2
#: A window holds at least this many samples per fitted parameter, or the fit
#: raises: the guard on `K_GRID` (config/grid-register.toml).
SAMPLES_PER_PARAMETER = 4
DETUNINGS = (0.95, 1.0, 1.02, 1.08)
COHERENT_SNR = 10.0
SOUND_HORIZON_BAR = 0.02

SERIES = ("sachs_wolfe", "doppler", "integrated", "c0")

#: PLANCK's environment as F9 builds it, and as D42 built it on 3 November.
CONFIGURATIONS = {
    "released": dict(acoustic_start="radiation era", potential="solved"),
    "antecedent": dict(acoustic_start="derived", potential="released"),
}


@dataclass(frozen=True)
class Window:
    centre: float
    pedestal: float
    amplitude: float
    phase: float
    residual: float


def fit_window(k: np.ndarray, y: np.ndarray, centre: float,
               r: float) -> Window:
    r"""Pedestal (cubic) plus a wave at $r$ whose amplitude has a slope, one
    period wide; the amplitude and phase are the wave's at the centre."""
    period = 2.0 * np.pi / r
    w = (k >= centre - period / 2) & (k <= centre + period / 2)
    x = (k[w] - centre) / period
    cos, sin = np.cos(k[w] * r), np.sin(k[w] * r)
    basis = np.column_stack([x ** n for n in range(PEDESTAL_DEGREE + 1)]
                            + [cos, sin, x * cos, x * sin])
    if basis.shape[0] < SAMPLES_PER_PARAMETER * basis.shape[1]:
        raise ValueError(
            f"the window at k={centre:g} holds {basis.shape[0]} samples for "
            f"{basis.shape[1]} parameters; the k grid is too coarse for the "
            "fit (config/grid-register.toml, K_GRID)")
    coef, *_ = np.linalg.lstsq(basis, y[w], rcond=None)
    resid = y[w] - basis @ coef
    a, b = float(coef[PEDESTAL_DEGREE + 1]), float(coef[PEDESTAL_DEGREE + 2])
    return Window(centre, float(coef[0]), float(np.hypot(a, b)),
                  float(np.arctan2(b, a)), float(np.sqrt(np.mean(resid ** 2))))


def sound_horizon(k: np.ndarray, y: np.ndarray, r_s: float) -> float:
    r"""The fixed point of $r\to r-d\theta/dc$ over the scored windows."""
    r = r_s
    for _ in range(50):
        theta = np.unwrap([fit_window(k, y, c, r).phase for c in SCORED])
        step = float(np.polyfit(SCORED, theta, 1)[0])
        r -= step
        if abs(step) < 1e-12 * r_s:
            break
    return r


def _pedestals(k: np.ndarray) -> dict[str, np.ndarray]:
    """Smooth shapes with no wave, for the instrument's floor."""
    return {"logarithm": 30.0 + 0.2 * k + 2e-4 * k ** 2 + 5.0 * np.log(k),
            "power law": 40.0 * (k / 100) ** 0.9 - 15.0 * (k / 100) ** -0.4,
            "tanh+sine": 150.0 * np.tanh(k / 250) + 20.0 * np.sin(np.pi * k / 1200)}


def instrument_floor(k: np.ndarray, r_s: float) -> dict[float, float]:
    """Each window's A/|P| on the smooth pedestals, which carry no wave."""
    floor = {c: 0.0 for c in CENTRES}
    for ped in _pedestals(k).values():
        for c in CENTRES:
            f = fit_window(k, ped, c, r_s)
            floor[c] = max(floor[c], f.amplitude / abs(f.pedestal))
    return floor


def calibrate(k: np.ndarray, r_s: float, fits: list[Window]) -> float:
    r"""The worst sound-horizon error on known waves shaped like this series.

    The envelope is the power law through the scored windows' amplitudes and
    the wave's size is their median $A/|P|$, put on each smooth pedestal and
    detuned by `DETUNINGS`.
    """
    scored = [f for f in fits if f.centre in SCORED]
    power = float(np.polyfit(np.log([f.centre for f in scored]),
                             np.log([f.amplitude for f in scored]), 1)[0])
    ratio = float(np.median([f.amplitude / abs(f.pedestal) for f in scored]))
    worst = 0.0
    for ped in _pedestals(k).values():
        a0 = ratio * float(np.median(np.abs(ped)))
        for detune in DETUNINGS:
            y = ped + a0 * (k / 300.0) ** power * np.cos(detune * k * r_s - 1.0)
            worst = max(worst, abs(sound_horizon(k, y, r_s) / (detune * r_s) - 1.0))
    return worst


def _env(config: str):
    _label, bg, omega_b_h2, h, _n_s = MODELS[2]
    return build_environment(
        K_MAX, omega_m=bg.omega_m, omega_lambda=bg.omega_lambda,
        omega_r=bg.omega_r, omega_b_h2=omega_b_h2,
        transfer_gamma=shape_parameter(bg.omega_m, h), hubble_h=h,
        f_2=F2_DEFAULT, line_of_sight_weight="printed",
        **CONFIGURATIONS[config])


def _slot_sources(k: float, cs, env) -> dict[str, np.ndarray]:
    """The four objects over eta, from the set's own line-of-sight inputs."""
    s, _ = line_of_sight_inputs(k, cs, env)
    g = s.c1_grav - s.c2_prime
    g_prime = s.c1_grav_prime - s.c2_second
    return {"sachs_wolfe": -g, "doppler": float(k) * (s.v_hat_b + s.c2),
            "integrated": s.c0 - g_prime, "c0": s.c0}


def _rel(a, b) -> float:
    scale = float(max(np.max(np.abs(a)), np.max(np.abs(b))))
    return float(np.max(np.abs(a - b)) / scale) if scale > 0 else 0.0


def sweep(env) -> tuple[dict[str, np.ndarray], dict[str, float], float]:
    """The series at eta_*, the frame gap per series, the identity gap."""
    star = int(np.argmax(np.asarray(env.visibility, dtype=float)))
    window = np.asarray(env.visibility) > 0.01 * float(np.max(env.visibility))
    series = {n: np.zeros(K_GRID.size) for n in SERIES}
    frame = {n: 0.0 for n in SERIES}
    identity = 0.0
    for j, k in enumerate(K_GRID):
        newt, cdm = covariant_coefficient_sets(float(k), env)
        sn, sc = _slot_sources(float(k), newt, env), _slot_sources(float(k), cdm, env)
        for n in SERIES:
            series[n][j] = float(sc[n][star])
            frame[n] = max(frame[n], _rel(sn[n][window], sc[n][window]))
        if j % IDENTITY_EVERY == 0:
            _, built = coefficient_sets(float(k), env, source="as built")
            bracket = (np.asarray(built.coefficients.c0)
                       - np.asarray(built.a_b0))
            identity = max(identity, _rel(np.asarray(cdm.coefficients.c0)[window],
                                          bracket[window]))
    return series, frame, identity


def _report(config: str) -> dict[str, np.ndarray]:
    print(__doc__.split("USAGE")[0])
    r_s = float(row(*MODELS[2])["r_s"])
    period = 2.0 * np.pi / r_s
    env = _env(config)
    print(f"{'=' * 78}\n  PLANCK, {config}: start {env.acoustic_start!r}, "
          f"potential {env.potential!r}, Paper 1's source signs\n"
          f"  r_s = {r_s:.6f}, acoustic period 2 pi / r_s = {period:.2f} in k, "
          f"eta_* at the visibility maximum\n{'=' * 78}")

    floor = instrument_floor(K_GRID, r_s)
    print("\n  CONTROL instrument")
    print("    floor, smooth pedestal with no wave, A/|P| by window: "
          + "  ".join(f"k~{c:.0f} {floor[c]:.1e}" for c in CENTRES))
    print("    the floor is a threshold inside COHERENT; each series' sound "
          "horizon is calibrated below, on known waves with its own envelope "
          "and A/|P|")

    series, frame, identity = sweep(env)
    print("\n  CONTROL frame, worst relative Newtonian-vs-CDM gap over the "
          "visibility window")
    print("    " + "   ".join(f"{n} {frame[n]:.1e}" for n in SERIES))
    print(f"\n  CONTROL identity, C_0 (Paper 1) against C_0 - a B_0 (as built): "
          f"{identity:.1e}")
    frame_ok = max(frame.values()) < FRAME_BAR
    identity_ok = identity < IDENTITY_BAR

    print(f"\n{'=' * 78}\n  THE SOURCE AT eta_*, IN k\n{'=' * 78}")
    verdicts, phases = {}, {}
    for n in SERIES:
        y = series[n]
        fits = [fit_window(K_GRID, y, c, r_s) for c in CENTRES]
        phases[n] = [f.phase for f in fits]
        r_src = sound_horizon(K_GRID, y, r_s)
        bias = calibrate(K_GRID, r_s, fits)
        passed = [f.amplitude > COHERENT_SNR * max(f.residual, floor[f.centre]
                                                   * abs(f.pedestal))
                  for f in fits]
        scored = passed[1:]
        horizon = abs(r_src / r_s - 1.0)
        if bias > CALIBRATION_BAR:
            leg = "unscored: the instrument's bias on this shape exceeds 1%"
        else:
            leg = "within 2%" if horizon < SOUND_HORIZON_BAR else "outside 2%"
        if not any(scored):
            verdicts[n] = "FLAT"
        elif not all(scored):
            k_c = next(f.centre for f, p in zip(fits[1:], scored) if not p)
            verdicts[n] = f"DECOHERES (first failing window k~{k_c:.0f})"
        elif bias > CALIBRATION_BAR:
            verdicts[n] = "COHERENT in amplitude; sound horizon unscored"
        elif horizon < SOUND_HORIZON_BAR:
            verdicts[n] = "COHERENT"
        else:
            verdicts[n] = "NOT COHERENT: sound horizon outside 2%"
        print(f"\n  {n}:  sound horizon r_src / r_s = {r_src / r_s:.5f}, "
              f"instrument bias on this shape {bias:.1e} ({leg})")
        print(f"    {verdicts[n]}")
        print(f"    {'k':>5} {'pedestal P':>12} {'amplitude A':>12} "
              f"{'A/|P|':>8} {'phase':>7} {'residual':>10}  ")
        for f, ok in zip(fits, passed):
            tag = "  (reported)" if f.centre == CENTRES[0] else (
                "" if ok else "  below 10x floor")
            print(f"    {f.centre:5.0f} {f.pedestal:12.4e} {f.amplitude:12.4e} "
                  f"{f.amplitude / abs(f.pedestal):8.3f} {f.phase:7.3f} "
                  f"{f.residual:10.2e}{tag}")

    print("\n  QUADRATURE, Doppler phase minus Sachs-Wolfe phase at the table's "
          "r_s, in units of pi/2 (reported):")
    print("    " + "   ".join(
        f"k~{c:.0f} {((phases['doppler'][i] - phases['sachs_wolfe'][i] + np.pi) % (2 * np.pi) - np.pi) / (np.pi / 2):+.3f}"
        for i, c in enumerate(CENTRES)))

    print(f"\n{'=' * 78}\n  CONTROLS AND OUTCOMES\n{'=' * 78}")
    for name, ok in (("frame", frame_ok), ("identity", identity_ok)):
        print(f"  {'PASS' if ok else 'FAIL':<6} {name}")
    for n in SERIES:
        print(f"  {n:<12} {verdicts[n]}")
    if not (frame_ok and identity_ok):
        print("\n  A control failed, so no outcome above is evidence.")
    return series


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--antecedent", action="store_true",
                    help="the environment of 3 November; prints, writes nothing")
    args = ap.parse_args()
    config = "antecedent" if args.antecedent else "released"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        series = _report(config)
    text = buf.getvalue()
    print(text, end="")
    if args.antecedent:
        return 0
    csv_path = ROOT.joinpath(*CSV_REL)
    with csv_path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# sources: {_digest(__file__)}\n")
        fh.write("k," + ",".join(SERIES) + "\n")
        for j, k in enumerate(K_GRID):
            fh.write(f"{k:.1f}," + ",".join(f"{series[n][j]:.9e}"
                                            for n in SERIES) + "\n")
    txt_path = ROOT.joinpath(*TXT_REL)
    txt_path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {csv_path.relative_to(ROOT)} and {txt_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
