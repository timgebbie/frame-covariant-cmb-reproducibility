#!/usr/bin/env python3
r"""F7 — frame specialisation, and what (102) can and cannot say about it.

    python scripts/figure_f7_frames.py

The solution is carried with a **generic** $u^a$, with $\sigma_{ab}$ present,
and the explicit frames appear as choices made at the end:

* the **Newtonian frame**, $\tilde\sigma_{ab}=0$ --- the specialisation
  *Annals II* itself makes at p. 365, and so a reproduction;
* the **CDM frame**, $A_a=0$ --- the extension, and the frame the observer is
  actually in (decisions **S8a**, **S29**).

**A gauge-fixed treatment cannot draw this figure**, which is the reason it is
in the set: fixing the gauge before solving the hierarchy fixes the frame with
it, and there is then nothing left to vary.

**The lower panel does not show what this figure was planned to show, and that
is finding T-31.** The plan (`captions/FIGURE-PLAN-v1.0.0.md`) asked for the
difference "with the **dipole shown separately**, because the dipole is where
the frame lives and $\ell\ge2$ is where it does not" --- GDE99 Eq. (37),
$\tilde\tau_a=\tau_a-v_a$, with $\tau_{A_\ell}$ unchanged for $\ell\ge2$.

Measured, **the dipole sits on the same curve as every other multipole**:
9.91% at $k=20$ against a median of 9.92% over $\ell=2$--$400$; 3.92% against
3.88% at $k=60$; 4.29% against 3.44% at $k=140$. **Worst ratio 1.25x**, where
the plan expected an order of magnitude.

Those figures moved in the third decimal when T-32 and T-34 were fixed --- the
$\eta$ grid is now sized for $k=1900$ rather than for $k=140$, so the
line-of-sight integral at the probe modes has 81 samples per $j_\ell$
oscillation where it had 6. **The finding did not move**, which is the point: it
is structural, and a better-resolved quadrature of the same structure returns
the same answer.

The reason is structural rather than numerical. (102) builds **every** multipole
from the same three $\ell$-independent coefficients $C_0,C_1,C_2$, projected
with $j_\ell$. A change of frame moves the $C_A$ and nothing else, so the frame
response it can produce is $\ell$-independent up to the differing $j_\ell$
weights of its three lines --- which is precisely the *flat in $\ell$* signature
`provenance/FRAME-INVARIANCE-MEASUREMENT-v1.md` reports and attributes to "a
residual living in the $C_A$". This figure is that observation followed to its
conclusion: **(102) cannot distinguish "invariant at $\ell\ge2$" from "invariant
nowhere", because it has no mechanism for answering differently at different
$\ell$.**

The dipole's special status is real and is not in this equation. (98)'s
construction sets $\tau_\ell(\eta_*)=0$ and $\tau_0=0$ and solves for the
*generated* anisotropy; the observer's own dipole is not generated along the
line of sight, so nothing in (102) carries it. Showing it needs the multipole
equations, not their integral solution.

**So the figure reports the flat response and says what that costs**, rather
than drawing a separation that is not there. That is the more useful figure, and
it is the one the measurement supports.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from functions.plotting.style import (  # noqa: E402
    INK,
    SERIES,
    SERIES_DASH,
    save_figure,
    use_house_style,
)
from functions.spectra.angular import cl_covariant_route, d_ell  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution,
    required_multipoles,
)
from functions.spectra.pipeline import primordial_power  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment,
    coefficient_sets,
)

#: **The dipole is included deliberately.** Every other figure in this bundle
#: starts at $\ell=2$, because the dipole is frame-dependent and so is not an
#: observable. That is exactly why it is here: this figure is about the frame.
ELLS = np.unique(np.concatenate([
    [1], np.round(np.logspace(np.log10(2.0), np.log10(400.0), 15)).astype(int)]))

#: Linear at $dk=\pi/3$, as F5 uses. A logarithmic grid aliases the
#: line-of-sight integrand at high $k$ however many points it has.
#: **Runs to 1900, not 420 --- finding T-32.** The diffusion scale is
#: $k_D=871.4$, so a grid stopping at 420 stops where $e^{-(k/k_D)^2}=0.79$,
#: and the shear sector's $k$-integrand, carrying an extra factor of $k$, peaks
#: at $k_D/2\simeq436$ --- outside it. Rank 1 does not need that tail and ranks
#: 0 and 2 do. $e^{-(k_{\max}/k_D)^2}=8.6\times10^{-3}$ here, which is the gate
#: **T-16** wrote down during v1.0.0 and dated to v1.2.0.
K_COM = np.arange(0.05, 1900.0, np.pi / 3.0)

#: The modes the lower panel probes. Chosen across the range rather than at
#: the best one: a claim shown at its most favourable k is a claim about that k.
K_PROBE = (20.0, 60.0, 140.0)


def compute() -> dict:
    # **`K_COM.max()`, not `K_PROBE[-1]` --- finding T-34.** `build_environment`
    # sizes the eta grid from the k it is given (`required_n_eta`), because
    # $j_\ell(k(\eta_0-\eta))$ oscillates with period $\pi/k$ in $\eta$ and the
    # line-of-sight integral has to resolve it. This was built for $k=140$ and
    # then integrated over a grid running to 420: **two samples per oscillation
    # at the band edge, below Nyquist**, which is T-3's failure exactly --- an
    # aliased integrand returning a smooth, plausible spectrum of the wrong
    # shape. The lower panel, which is what T-31 is about, is evaluated only at
    # `K_PROBE` and was never affected; the upper panel was.
    env = build_environment(float(K_COM.max()), line_of_sight_weight="printed")
    needed = required_multipoles(ELLS)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(K_COM.max() * (env.background.eta_0 - env.eta[0])) + 20.0,
    )

    # --- the observable, over the full k grid -------------------------
    transfer = {f: np.zeros((ELLS.size, K_COM.size)) for f in ("newtonian", "cdm")}
    for j, k in enumerate(K_COM):
        sets = dict(zip(("newtonian", "cdm"), coefficient_sets(float(k), env)))
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        for name, cs in sets.items():
            transfer[name][:, j] = integral_solution(
                ELLS, coefficients=cs.coefficients, c1_prime=cs.c1_prime,
                c2_second=cs.c2_second, c2_prime_star=cs.c2_prime_star,
                table=table, weight=env.weight, diffusion=diffusion,
                damping_total=diffusion, eta_star=env.eta_star,
                eta_0=float(env.background.eta_0)).total

    power = primordial_power(K_COM, n_s=1.0, amplitude=1.0)
    cl = {f: np.array([cl_covariant_route(int(l), K_COM, transfer[f][i], power)
                       for i, l in enumerate(ELLS)]) for f in transfer}

    # --- the frame response at fixed k, which is where the dipole claim
    #     lives: C_l integrates over k and cannot show an l dependence that
    #     the per-mode answer does not have.
    per_k = {}
    for k in K_PROBE:
        sets = dict(zip(("newtonian", "cdm"), coefficient_sets(float(k), env)))
        diffusion = float(np.exp(-((float(k) / env.damping_k) ** 2)))
        t = {name: integral_solution(
                ELLS, coefficients=cs.coefficients, c1_prime=cs.c1_prime,
                c2_second=cs.c2_second, c2_prime_star=cs.c2_prime_star,
                table=table, weight=env.weight, diffusion=diffusion,
                damping_total=diffusion, eta_star=env.eta_star,
                eta_0=float(env.background.eta_0)).total
             for name, cs in sets.items()}
        scale = np.maximum(np.abs(t["newtonian"]), np.abs(t["cdm"]))
        rel = np.where(scale > 0.0, np.abs(t["cdm"] - t["newtonian"]) / np.where(
            scale > 0.0, scale, 1.0), np.nan)
        per_k[float(k)] = rel
        finite = rel[np.isfinite(rel)]
        above = rel[1:][np.isfinite(rel[1:])]
        print(f"  k={k:6.1f}  dipole {rel[0]:.4f}   l>=2 median "
              f"{np.median(above):.4f}   ratio {rel[0] / np.median(above):.2f}x"
              f"   spread over l {finite.max() / finite.min():.2f}")

    ratios = [per_k[k][0] / np.median(per_k[k][1:][np.isfinite(per_k[k][1:])])
              for k in K_PROBE]
    print(f"  worst dipole/median ratio over the probe set: {max(ratios):.2f}x "
          "-- the plan expected an order of magnitude")
    return {"cl": cl, "per_k": per_k, "ratios": ratios}


def draw(data: dict) -> plt.Figure:
    use_house_style()
    fig, (ax_a, ax_b) = plt.subplots(
        2, 1, figsize=(6.6, 5.9), sharex=True,
        gridspec_kw={"height_ratios": [2.0, 1.5]})
    fig.subplots_adjust(top=0.825, bottom=0.105, left=0.145, right=0.925,
                        hspace=0.14)
    cl, per_k = data["cl"], data["per_k"]

    # ---- (a) the observable in both specialisations --------------------
    # **The two curves nearly overlie**, so labelling them on the line puts the
    # text on the other one. Direct-labelled in the corner instead, each with a
    # short rule in its own colour and dash so the eye matches by both channels.
    for frame, slot, label, y in (
            ("newtonian", 1, r"Newtonian frame, $\tilde\sigma_{ab}=0$", 0.93),
            ("cdm", 2, r"CDM frame, $A_a=0$", 0.855)):
        ax_a.loglog(ELLS, np.abs(d_ell(ELLS, cl[frame])), color=SERIES[slot],
                    ls=SERIES_DASH[slot], lw=1.9, solid_capstyle="round", zorder=3)
        ax_a.plot([0.055, 0.115], [y, y], transform=ax_a.transAxes,
                  color=SERIES[slot], ls=SERIES_DASH[slot], lw=1.9,
                  solid_capstyle="round", clip_on=False, zorder=5)
        ax_a.annotate(label, xy=(0.132, y), xycoords="axes fraction",
                      fontsize=7.4, color=INK["secondary"], va="center", ha="left")
    ax_a.set_ylabel(r"$\ell(\ell+1)C_\ell/2\pi$")
    ax_a.annotate("the specialisation is made at the end, not at the start —\n"
                  "a gauge-fixed treatment has nothing left to vary here",
                  xy=(0.965, 0.07), xycoords="axes fraction", fontsize=7.0,
                  color=INK["secondary"], va="bottom", ha="right")

    # ---- (b) the frame response at fixed k, dipole marked --------------
    for (k, rel), slot in zip(sorted(per_k.items()), (1, 2, 3)):
        above = np.isfinite(rel) & (ELLS >= 2)
        ax_b.loglog(ELLS[above], 100.0 * rel[above], color=SERIES[slot],
                    ls=SERIES_DASH[slot], lw=1.8, solid_capstyle="round", zorder=3)
        if np.isfinite(rel[0]):
            ax_b.plot([1], [100.0 * rel[0]], marker="o", ms=6.5, color=SERIES[slot],
                      mfc=INK["surface"], mew=1.8, zorder=4)
        # k = 60 and k = 140 end within a few percent of one another; nudged
        # apart rather than moved into a key, for the contrast reason above.
        ax_b.annotate(rf"$k={k:.0f}$", xy=(ELLS[above][-1], 100.0 * rel[above][-1]),
                      xytext=(6, {20.0: 0.0, 60.0: -7.0, 140.0: 7.0}[k]),
                      textcoords="offset points", fontsize=7.0,
                      color=INK["secondary"], va="center", ha="left")
    ax_b.set_ylabel("frame difference in\nthe transfer  [%]")
    ax_b.set_xlabel(r"multipole  $\ell$   (open circles: the dipole)")
    ax_b.annotate(
        "the dipole lands **on** each curve, not above it: worst ratio "
        f"{max(data['ratios']):.1f}×.\n"
        "(102) builds every $\\ell$ from the same three $C_A$, so its\n"
        "frame response cannot depend on $\\ell$ — T-31".replace("**", ""),
        xy=(0.035, 0.07), xycoords="axes fraction", fontsize=7.0,
        color=INK["secondary"], va="bottom", ha="left")

    for ax in (ax_a, ax_b):
        ax.set_xlim(0.9, float(ELLS.max()))

    fig.suptitle("F7   Frame specialisation, and what (102) can say about it",
                 x=0.012, y=0.972, ha="left", fontsize=10, color=INK["primary"])
    fig.text(
        0.012, 0.928,
        "The generic $u^a$ is carried through and the frame chosen at the end: "
        "the Newtonian frame reproduces §7.1.1, the CDM frame\nextends it. The "
        "lower panel was planned to show the dipole standing apart — "
        "$\\tilde\\tau_a=\\tau_a-v_a$ moves it and leaves\n$\\ell \\geq 2$ "
        "invariant. It does not, and the reason is structural, not numerical: "
        "finding T-31. A figure that reports this is\nmore use than one that "
        "illustrates what was assumed.",
        ha="left", va="top", fontsize=7.4, color=INK["secondary"],
    )
    return fig


def main() -> int:
    data = compute()

    out = ROOT / "outputs" / "f7-frames.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# C_l in two frames, and the per-mode frame response\n")
        fh.write("quantity,k_com,ell,value\n")
        for frame in ("newtonian", "cdm"):
            for l, c in zip(ELLS, data["cl"][frame]):
                fh.write(f"cl_{frame},,{int(l)},{c:.12e}\n")
        for k, rel in sorted(data["per_k"].items()):
            for l, r in zip(ELLS, rel):
                fh.write(f"frame_difference,{k:.4f},{int(l)},{r:.12e}\n")
    print(f"wrote {out.relative_to(ROOT)}")

    for p in save_figure(draw(data), "f7-frames", "v1.2.0"):
        print(f"wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
