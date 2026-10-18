#!/usr/bin/env python3
r"""D10 --- what approximation A-3 costs: the potential that does not decay.

    python scripts/diagnostic_d10_radiation_driving.py

**A-3 in one sentence.** `potentials` holds $\Phi$ **constant** below its
matter-domination reference, which is the first point of the recombination
grid ($z_{\max}=3000$). Since **T-51** every mode's acoustic integration starts
far earlier than that --- where $k\,r_s(\eta)\le0.1$, which for $k=300$ on
`PLANCK_MODEL` is deep in radiation domination --- so the oscillator is driven
across the whole radiation era by a potential frozen at its super-horizon
value. In the real universe it decays, and because it decays while the mode is
oscillating it drives the oscillator **resonantly**. That amplification is the
one Hu \& Sugiyama compute analytically and it is absent from every peak height
this bundle produces.

**The control is the point of this diagnostic, not an afterthought.**
`CDM_MODEL` and `LCDM_MODEL` carry $\Omega_r=0$: they have **no radiation era
at all**, so A-3 is identically zero on them and the Sachs--Wolfe limit must
come out at exactly $\tfrac13\Phi_A(0,k)$. Finding **T-62** measured that it
does --- $1.0000$ on Einstein--de Sitter against $0.5996$ on `PLANCK_MODEL` ---
and that is what makes this measurable against a *known answer* rather than
against a tolerance. A diagnostic whose control has no right answer is a
diagnostic that cannot be wrong.

**This reports; it does not fail, and it changes nothing.** `potentials` is
untouched. Under this bundle's standing rule the measurement comes first and
the matter-only branch is kept as a control afterwards, the way
`acoustic_start='z_max'` keeps the pre-T-51 grid.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL,
    PLANCK_H,
    PLANCK_MODEL,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.acoustic import (  # noqa: E402
    TIGHT_COUPLING_FACTOR,
    acoustic_start_eta,
    required_acoustic_points,
    sachs_wolfe_at_last_scattering,
    solve_acoustic,
    sound_horizon_from_zero,
)
from functions.spectra.decoupling import RecombinationHistory  # noqa: E402
from functions.spectra.potentials import (  # noqa: E402
    matter_domination_eta,
    potentials,
    radiation_era_potential,
)

VERSION = "v1.3.0"

#: Spanning the band: $k=10$ enters after equality on `PLANCK_MODEL` and
#: $k=600$ long before, so the columns below should separate.
KS = (10.0, 30.0, 100.0, 300.0, 600.0)

BACKGROUNDS = [
    ("CDM (Einstein-de Sitter)", CDM_MODEL, 0.0224, 0.5),
    ("PLANCK_MODEL", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H),
]


def scope(background, omega_b_h2, k):
    r"""Where this mode sits relative to equality, and what the frozen
    potential omits. **Nothing is spliced.**

    The first draft of this diagnostic drove the oscillator twice --- once with
    the released frozen $\Phi$ and once with the radiation solution spliced in
    below equality --- and reported the ratio. **It does not work on this
    grid**, and the failure is worth recording because it is the same class as
    four others found this week.

    On `PLANCK_MODEL` at $k=10$ the splice changes $\Phi$ by at most
    $1.3\times10^{-3}$ and changes $\delta T(\eta_*)$ from $-0.751$ to
    $+1.190$ --- a sign flip on a $0.13\%$ input. The oscillator is driven by
    $\Phi$ **and its derivative**, the acoustic grid puts only **three points**
    below $\eta_{\rm eq}$, and a splice on three points is a step in
    $\Phi'$. *The response is to the kink, not to the physics.*

    So this reports the scoping --- which modes have a radiation era to see,
    how much of their span is in it, how far $\Phi$ has fallen by equality, and
    whether the grid could resolve it --- and stops there. **Driving the
    oscillator through a resolved radiation era is A-3's fix, not its
    measurement**, and it needs a grid derived for that era rather than for the
    acoustic one.
    """
    rec = RecombinationHistory.build(background, omega_b_h2=omega_b_h2)
    eta_rs, r_s = sound_horizon_from_zero(
        background, float(rec.eta_star), omega_b_h2=omega_b_h2)
    start = acoustic_start_eta(float(k), eta_rs, r_s)
    couple = min(float(background.eta_0), TIGHT_COUPLING_FACTOR * float(rec.eta_star))
    grid = np.linspace(start, couple, required_acoustic_points(float(k), couple - start))
    eta_eq = matter_domination_eta(background)
    below = int(np.sum(grid < eta_eq)) if eta_eq > 0.0 else 0
    decay = (float(radiation_era_potential(float(k), np.array([eta_eq]))[0])
             if eta_eq > 0.0 else 1.0)
    span = float(rec.eta_star) - start
    return {
        "start": start, "eta_eq": eta_eq, "eta_star": float(rec.eta_star),
        "x_eq": float(k) * eta_eq / np.sqrt(3.0),
        "decay": decay, "points_below": below, "n_grid": int(grid.size),
        # Zero where there is no radiation era, rather than negative:
        # eta_eq = 0 would otherwise make this (0 - start)/span.
        "fraction": (max(0.0, min(eta_eq, float(rec.eta_star)) - start) / span
                     if span > 0 else 0.0),
    }


def report() -> list[str]:
    say: list[str] = []
    a = say.append
    a("D10 - what approximation A-3 costs: the potential that does not decay")
    a("Generated by scripts/diagnostic_d10_radiation_driving.py. Do not edit by hand.")
    a("")
    a("  `potentials` holds Phi CONSTANT below its matter-domination reference,")
    a("  which is the recombination grid's first point (z_max = 3000). Since")
    a("  T-51 every mode starts far earlier than that. So the oscillator is")
    a("  driven across the radiation era by a frozen potential, where the truth")
    a("  is the closed form Phi = 3 Phi_i j_1(x)/x, x = k eta / sqrt(3), which")
    a("  decays as x^-2 while the mode oscillates. That resonance is the Hu &")
    a("  Sugiyama amplification and it is what A-3 discards.")
    a("")

    for label, background, omega_b_h2, hubble_h in BACKGROUNDS:
        rec = RecombinationHistory.build(background, omega_b_h2=omega_b_h2)
        eta_eq = matter_domination_eta(background)
        has_radiation = background.omega_r > 0.0
        a(f"  --- {label} " + "-" * max(0, 52 - len(label)))
        a(f"      Omega_r = {background.omega_r:.6g}"
          + ("" if has_radiation else "   <- NO RADIATION ERA: A-3 is identically zero here"))
        a(f"      eta_eq = {eta_eq:.6g}   grid reference eta[0] = {rec.eta[0]:.6f}"
          f"   eta_* = {rec.eta_star:.6f}")
        if not has_radiation:
            a("")
            a("      THE CONTROL. Appendix G is exactly right on this background,")
            a("      Phi is constant, and T-62 measures the Sachs-Wolfe limit at")
            a("      1.0000 against Phi_A(0)/3. Any departure below is the")
            a("      diagnostic's own error, not A-3.")
        a("")
        a(f"      {'k':>7s} {'eta_start':>11s} {'x at eta_eq':>12s} "
          f"{'Phi_rad(eta_eq)':>16s} {'A-3 omits':>11s} {'span in rad era':>16s} "
          f"{'grid pts below':>15s}")
        for k in KS:
            r = scope(background, omega_b_h2, k)
            a(f"      {k:7.0f} {r['start']:11.3e} {r['x_eq']:12.3f} "
              f"{r['decay']:16.4f} {1.0 - r['decay']:11.2%} "
              f"{r['fraction']:16.2%} {r['points_below']:7d} / {r['n_grid']:<5d}")
        a("")

    a("  --- how to read the columns ------------------------------------")
    a("      x at eta_eq      k eta_eq / sqrt(3): how far inside the sound")
    a("                       horizon the mode already is at equality. Above")
    a("                       ~1 the mode oscillated while Phi was decaying,")
    a("                       which is where the resonant driving lives.")
    a("      Phi_rad(eta_eq)  what the closed form says Phi has fallen to by")
    a("                       equality. The released driving uses 1.0000.")
    a("      A-3 omits        1 - that: the decay the frozen potential misses.")
    a("                       It is a LOWER bound on what A-3 is worth, because")
    a("                       a net factor is not the resonance -- the driving")
    a("                       is Phi CHANGING while the mode rings, and a")
    a("                       constant rescale of Phi rescales delta_T exactly")
    a("                       and teaches nothing.")
    a("      grid pts below   how many of the mode's acoustic grid points lie")
    a("                       below equality. THIS IS WHY THE OSCILLATOR")
    a("                       COMPARISON IS NOT HERE.")
    a("")
    a("  --- what this diagnostic deliberately does not do ----------------")
    a("      It does not drive the oscillator twice and report a ratio. That")
    a("      was the first draft and it failed: on PLANCK_MODEL at k = 10 a")
    a("      spliced Phi differing by 1.3e-03 moved delta_T(eta_*) from -0.751")
    a("      to +1.190, a sign flip on a 0.13% input, because the acoustic grid")
    a("      carries three points below equality and a splice on three points")
    a("      is a step in Phi-prime. The oscillator responds to the kink.")
    a("")
    a("      Driving through a resolved radiation era is A-3's FIX and needs a")
    a("      grid derived for that era, not for the acoustic one. The columns")
    a("      above say which modes need it and how badly, which is what a")
    a("      scoping diagnostic is for.")
    a("")
    a("      The Einstein-de Sitter block is the control and it is a no-op by")
    a("      construction: Omega_r = 0 makes matter_domination_eta return 0,")
    a("      nothing lies below the splice, and the decay factor is")
    a("      Phi_rad(0) = 1. An earlier draft spliced at the grid reference")
    a("      instead of equality and moved that control by factors of 7 to 10,")
    a("      on a background with no radiation era at all. The control caught")
    a("      it on the first run, which is the whole reason it is here.")
    return say


def main() -> int:
    lines = report()
    print("\n".join(lines))
    out = ROOT / "diagnostics" / f"d10-radiation-driving-{VERSION}.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"\nwrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
