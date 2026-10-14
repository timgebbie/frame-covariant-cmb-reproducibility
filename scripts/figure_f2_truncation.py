#!/usr/bin/env python3
r"""F2 — truncation convergence: Appendix E made quantitative, in both frames.

    python scripts/figure_f2_truncation.py

*Annals II* Appendix E, from Ellis--Treciokas--Matravers:

> if **any** four consecutive harmonics vanish, say those with
> $\ell=L+1,\dots,L+4$, but those for $\ell=L$ are non-zero, then [...] **the
> shear must vanish exactly**, $\sigma_{ab}=0$.

and it anticipates the obvious objection and rejects it:

> A simplistic approach to linearisation will suggest that these relations [...]
> can be ignored in (linearised) almost-Friedmann--Lema\^itre universes, because
> the equations leading to these results are second-order relations and so can
> be dropped when linearising. **However that argument is not correct** [...]
> there are no zero or first order terms in the relevant equations [...] to
> explicitly linearise with respect to. [...] $O(\epsilon^2)\ll O(\epsilon)$
> [does not] mean that $O(\epsilon^2)=0$ on its own.

**That is the figure.** A truncation at $\ell_{\max}$ sets four consecutive
harmonics to zero and therefore kills the shear *exactly*, however small the
truncated multipoles are. So there are two quantities, and the whole point of
Appendix E is that they do not shrink together:

* **what the truncation discards numerically** --- the power above
  $\ell_{\max}$, which falls off a cliff once $\ell_{\max}$ passes $k\Delta\eta$
  and can be made as small as anyone likes;
* **what it destroys formally** --- the shear, and with it the rank-zero and
  rank-two sectors of (89). That cost **has no $\ell_{\max}$ in it at all**: it
  is a function of $\ell$, and measured here it *rises* with $\ell$, so it is
  largest exactly where a truncation would be placed.

The second point is the one worth stating carefully, because the obvious guess
is wrong. One expects a truncation to get cheaper as $\ell_{\max}$ is raised, and
numerically it does --- that is the upper panel. What the lower panel measures is
not a function of $\ell_{\max}$: it is the share of $C_\ell$ carried by the
sectors that $\sigma_{ab}=0$ empties, and raising the truncation does not return
any of it.

**Run in both frames, because footnote 29 on p. 365 makes a checkable claim**
--- that choosing the Newtonian frame "would also remove any problems we may
have with the introduction of high-$\ell$ truncation as discussed in Appendix
E". It is **true**, and the figure shows why it is less reassuring than it
sounds: the Newtonian frame removes the problem by having no shear to lose,
$\tilde\sigma_{ab}=0$ being its defining condition. The cost of a
shear-destroying truncation there is exactly zero because there is nothing in
the rank-zero and rank-two sectors to destroy --- (110). In the CDM frame, where
the observer actually is, it is not zero.
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
from functions.spectra.angular import cl_covariant_route  # noqa: E402
from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.integral_solution import required_multipoles  # noqa: E402
from functions.spectra.pipeline import primordial_power  # noqa: E402
from functions.spectra.two_frame import (  # noqa: E402
    build_environment,
    coefficient_sets,
    transfer_by_rank,
)

#: **Two $\ell$ grids, because the two panels cost different amounts.** The
#: upper panel is evaluated at three $k$ and is free, so it takes a dense grid
#: that resolves each cliff. The lower panel is evaluated at every $k$ in
#: `K_COM` --- which T-32 made 4.5x longer --- so it takes the coarsest grid that
#: resolves a smooth monotone curve. Splitting them is worth a factor of two in
#: the harness and costs nothing either panel needs.
ELLS = np.unique(np.round(np.logspace(np.log10(2.0), np.log10(600.0), 30)).astype(int))
ELLS_COST = np.unique(np.round(np.logspace(np.log10(2.0), np.log10(600.0), 16)).astype(int))

#: Linear at $dk=\pi/3$: $j_\ell(k\Delta\eta)$ oscillates with period
#: $\pi/\Delta\eta$ in $k$, so the grid must be linear and this is three samples
#: per oscillation. Refining it to $\pi/6$ moves the lower panel by 0.02%.
#:
#: **It runs to 1900, not to 420, and that is finding T-32.** The diffusion scale
#: is $k_D=871.4$, so a grid stopping at 420 stops where
#: $e^{-(k/k_D)^2}=0.79$ --- almost nothing has damped yet. The shear sector
#: carries an extra factor of $k$ in the transfer, so at $n_s=1$ its
#: $k$-integrand goes as $k\,e^{-2(k/k_D)^2}$ and **peaks at $k=k_D/2\simeq436$,
#: outside that grid**, while the scalar sector's has long since fallen: the
#: rank-0/2 sectors need a tail that rank 1 does not. On the 420 grid this
#: figure's $\ell=600$ number read 40.5%; it converges to 28.7%. 1900 is where
#: the bundle's own gate passes, $e^{-(k_{\max}/k_D)^2}<10^{-2}$ --- the
#: readiness test **T-16** wrote down during v1.0.0 and dated to v1.2.0.
#:
#: The sampling was tested first and came back clean. That is the trap: a
#: quadrature has two edges, and refining the one the integrand's mass is not at
#: cannot see the one it is.
K_COM = np.arange(0.05, 1900.0, np.pi / 3.0)

#: The gate `K_COM` is set by, restated here so the figure checks it rather than
#: inheriting it. `pipeline.SpectrumRun.k_grid_reaches_damping_scale` is the same
#: number for the released spectrum.
DAMPING_GATE = 1e-2

#: Drop the top 10% of the $k$ grid and recompute: if the answer does not move,
#: the integral has converged over the range plotted. F3's
#: `cl_truncation_sensitivity` is the same test on the released spectrum; this is
#: it applied to the **ratio** this figure draws, which is the quantity at risk.
CONVERGENCE_TOLERANCE = 1e-2

#: The truncations drawn in the upper panel.
ELL_MAX = (20, 40, 80, 160, 320)

#: The modes the tail is drawn for. $j_\ell(k\Delta\eta)$ turns over at
#: $\ell\simeq k\Delta\eta$, so each $k$ has its own cliff and that is the point.
#:
#: **The same three probe modes as F7**, deliberately: the two figures ask
#: different questions of the same modes, so a reader can carry a number from one
#: to the other. A fourth mode was drawn at first and dropped --- $k=300$ puts its
#: cliff at $k\Delta\eta\simeq580$, right at the edge of `ELLS`, so it was
#: resolved by two points and would have needed slot 4, which this bundle
#: reserves for the deliberately-wrong control.
K_TAIL = (20.0, 60.0, 140.0)


def compute() -> dict:
    env = build_environment(float(K_COM.max()))
    needed = required_multipoles(np.union1d(ELLS, ELLS_COST))
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(K_COM.max() * (env.background.eta_0 - env.eta[0])) + 20.0,
    )
    delta_eta = float(env.background.eta_0 - env.eta_star)

    # --- what the truncation discards numerically ------------------------
    # The free-streaming projection of a fixed source: the ell-dependence is
    # j_ell(k dEta), so the tail above ell_max is a property of the projection
    # and not of the source. Computed from the transfer itself rather than from
    # j_ell alone, so it is the quantity the spectrum is actually built from.
    tail = {}
    for k in K_TAIL:
        _, cdm = coefficient_sets(float(k), env)
        parts = transfer_by_rank(ELLS, float(k), cdm, env, table)
        weight = (2.0 * ELLS + 1.0) * parts[-1] ** 2
        total = float(np.trapezoid(weight, ELLS))
        above = np.array([
            float(np.trapezoid(weight[ELLS >= L], ELLS[ELLS >= L])) / total
            if (ELLS >= L).sum() > 1 else 0.0 for L in ELLS])
        tail[float(k)] = above
        crossing = float(k) * delta_eta
        print(f"  k={k:6.1f}  k dEta = {crossing:6.1f}   tail above "
              f"ell=2 {above[0]:.3f}, above ell={int(ELLS[-1])} "
              f"{above[-1]:.2e}")

    # --- what the truncation destroys formally ---------------------------
    # sigma = 0 empties ranks 0 and 2 of (89). What that costs is the share of
    # C_l they carry, auto terms and cross terms together, and it has no
    # ell_max in it -- which is the figure's point.
    shape = (ELLS_COST.size, K_COM.size)
    full = {f: np.zeros(shape) for f in ("newtonian", "cdm")}
    rank1 = {f: np.zeros(shape) for f in ("newtonian", "cdm")}
    for j, k in enumerate(K_COM):
        for name, cs in zip(("newtonian", "cdm"), coefficient_sets(float(k), env)):
            parts = transfer_by_rank(ELLS_COST, float(k), cs, env, table)
            full[name][:, j] = parts[-1]
            rank1[name][:, j] = parts[1]

    power = primordial_power(K_COM, n_s=1.0, amplitude=1.0)

    def cost_on(mask: np.ndarray) -> dict:
        """The cost of sigma -> 0, on whatever part of the k grid `mask` keeps."""
        k, p = K_COM[mask], power[mask]
        out = {}
        for name in full:
            whole = np.array([cl_covariant_route(int(l), k, full[name][i][mask], p)
                              for i, l in enumerate(ELLS_COST)])
            gone = np.array([cl_covariant_route(int(l), k, rank1[name][i][mask], p)
                             for i, l in enumerate(ELLS_COST)])
            out[name] = np.abs(whole - gone) / np.abs(whole)
        return out

    cost = cost_on(np.ones(K_COM.size, dtype=bool))
    for name in cost:
        print(f"  {name:10s} cost of sigma -> 0: median {np.median(cost[name]):.4f}, "
              f"max {cost[name].max():.4f}")

    if cost["newtonian"].max() > 1e-12:
        raise ValueError(
            "the Newtonian frame has something in its rank-0/2 sectors; "
            "(110) says it does not, and footnote 29's claim rests on it")

    # --- state the convergence rather than inheriting it -- T-32 -------------
    # Two edges, and the sampling is not the one that bit. `damping` is where the
    # grid stops relative to k_D; `sensitivity` is what the top 10% of it was
    # still contributing to the ratio drawn below.
    damping = float(np.exp(-((K_COM.max() / env.damping_k) ** 2)))
    short = cost_on(K_COM <= K_COM.max() * 0.9)
    sensitivity = np.abs(short["cdm"] - cost["cdm"]) / np.abs(cost["cdm"])
    print(f"  k grid: k_max={K_COM.max():.0f}, k_D={env.damping_k:.1f}, "
          f"exp[-(k_max/k_D)^2]={damping:.2e} "
          f"({'passes' if damping < DAMPING_GATE else 'FAILS'} the T-16 gate)")
    print(f"  dropping its top 10%: worst change in the cost {sensitivity.max():.2e} "
          f"at l={int(ELLS_COST[int(np.argmax(sensitivity))])}")
    if damping >= DAMPING_GATE:
        raise ValueError(
            f"k_max={K_COM.max():.0f} leaves exp[-(k_max/k_D)^2]={damping:.2e}; "
            f"the shear integrand peaks at k_D/2={env.damping_k / 2:.0f} and this "
            f"figure's lower panel is built from it. See finding T-32.")
    if sensitivity.max() >= CONVERGENCE_TOLERANCE:
        raise ValueError(
            f"the cost moves by {sensitivity.max():.2e} when the top 10% of the k "
            f"grid is dropped, above the {CONVERGENCE_TOLERANCE:.0e} this figure "
            f"claims. Raise k_max. See finding T-32.")

    # The shape of the CDM cost is the caption, so print it rather than
    # describing it. It is flat near 1% through the plateau and rises after.
    plateau = cost["cdm"][ELLS_COST <= 20]
    rising = bool(np.all(np.diff(cost["cdm"][ELLS_COST >= 20]) > -1e-12))
    print("  cdm cost by ell: " + "  ".join(
        f"l={int(l)} {100 * c:.2f}%" for l, c in zip(ELLS_COST, cost["cdm"])))
    print(f"  plateau l<=20: {100 * plateau.min():.2f}-{100 * plateau.max():.2f}%; "
          f"monotone above l=20: {rising}")
    return {"tail": tail, "cost": cost, "delta_eta": delta_eta,
            "damping": damping, "sensitivity": float(sensitivity.max()),
            "plateau": (float(plateau.min()), float(plateau.max())),
            "rising_above_20": rising}


def draw(data: dict) -> plt.Figure:
    use_house_style()
    fig, (ax_a, ax_b) = plt.subplots(
        2, 1, figsize=(6.6, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [1.65, 1.35]})
    fig.subplots_adjust(top=0.800, bottom=0.10, left=0.155, right=0.925, hspace=0.14)

    # ---- (a) what truncation discards: it falls off a cliff -------------
    # The three k are an ordered family, so they take the lightness ramp in
    # order. Slot 4 is not used: it is the deliberately-wrong control.
    for (k, above), slot in zip(sorted(data["tail"].items()), (1, 2, 3)):
        ax_a.loglog(ELLS, np.maximum(above, 1e-18), color=SERIES[slot],
                    ls=SERIES_DASH[slot], lw=1.8, solid_capstyle="round", zorder=3)
        # Label on the cliff, where the curve is steep and unambiguous, rather
        # than at k dEta, which for the largest k sits off the bottom of the axis.
        # Below and left of each cliff: the region under a curve's own plateau
        # is empty, where the region above it carries every other curve's.
        below = np.flatnonzero(above < 0.5)
        j = int(below[0]) if below.size else int(ELLS.size - 1)
        ax_a.annotate(rf"$k={k:.0f}$", xy=(ELLS[j], 3e-2),
                      xytext=(-5, 0), textcoords="offset points", fontsize=7.0,
                      color=INK["secondary"], ha="right", va="center", zorder=4)
    ax_a.set_ylim(1e-13, 4.0)
    ax_a.set_ylabel("power discarded above\n" r"$\ell_{\max}$,  as a fraction")
    ax_a.annotate("each $k$ has its own cliff\nat $\\ell\\simeq k\\Delta\\eta$: "
                  "numerically,\ntruncation can be made\nas cheap as you like",
                  xy=(0.035, 0.055), xycoords="axes fraction", fontsize=7.0,
                  color=INK["secondary"], va="bottom", ha="left")

    # ---- (b) what it destroys: frame-dependent, and rising ---------------
    floor = 3.0e-3
    ax_b.set_yscale("log")
    ax_b.set_ylim(2.4e-3, 90.0)
    for name, slot, label in (
            ("cdm", 1, "CDM frame — the shear is there to lose"),
            ("newtonian", 2, r"Newtonian frame — $\tilde\sigma_{ab}=0$: identically zero,"
                             "\ndrawn at the axis floor")):
        values = 100.0 * data["cost"][name]
        ax_b.semilogx(ELLS_COST, np.maximum(values, floor), color=SERIES[slot],
                      ls=SERIES_DASH[slot], lw=1.9, solid_capstyle="round", zorder=3)
        y = 0.95 if slot == 1 else 0.855
        ax_b.plot([0.055, 0.115], [y] * 2, transform=ax_b.transAxes,
                  color=SERIES[slot], ls=SERIES_DASH[slot], lw=1.9,
                  clip_on=False, zorder=5)
        ax_b.annotate(label, xy=(0.132, y), xycoords="axes fraction",
                      fontsize=7.4, color=INK["secondary"], va="center", ha="left")
    ax_b.set_ylabel("cost of a shear-destroying\n" r"truncation, in $C_\ell$  [%]")
    ax_b.set_xlabel(r"$\ell_{\max}$   (upper panel)   /   multipole $\ell$   (lower)")

    cdm = 100.0 * data["cost"]["cdm"]
    lo, hi = (100.0 * v for v in data["plateau"])
    ax_b.annotate(
        f"the cost has **no $\\ell_{{\\max}}$ in it**: a function of $\\ell$, not of the "
        f"truncation.\nFlat at {lo:.1f}–{hi:.1f}% while the monopole dominates, then "
        f"rising to **{cdm[-1]:.0f}%**\nby $\\ell={int(ELLS_COST[-1])}$ as the velocity term "
        "takes over — worst exactly where\na truncation is put, and raising "
        "$\\ell_{\\max}$ returns none of it.".replace("**", ""),
        xy=(0.035, 0.055), xycoords="axes fraction", fontsize=7.0,
        color=INK["secondary"], va="bottom", ha="left")
    # The figure's numerical standing, on the figure. T-32.
    ax_b.annotate(
        f"$k_{{\\max}}={K_COM.max():.0f}$: $e^{{-(k_{{\\max}}/k_D)^2}}="
        f"{data['damping']:.1e}$, and dropping the grid's top 10% moves this "
        f"panel by {data['sensitivity']:.0e}",
        xy=(1.0, -0.265), xycoords="axes fraction", fontsize=6.4,
        color=INK["muted"], va="top", ha="right")

    fig.suptitle("F2   Truncation: what it discards, and what it destroys",
                 x=0.012, y=0.968, ha="left", fontsize=10, color=INK["primary"])
    fig.text(
        0.012, 0.922,
        "Appendix E: four consecutive vanishing harmonics force "
        "$\\sigma_{ab}=0$ **exactly**, and the paper rejects the argument\nthat "
        "this is second order and so droppable — there are no first-order terms "
        "in that equation to drop it\nagainst. The two panels are the two "
        "quantities, and they do not shrink together: the upper falls off a\n"
        "cliff, the lower rises. Footnote 29 (p. 365) says the Newtonian frame "
        "removes the problem. It does, by\nhaving no shear to "
        "lose.".replace("**", ""),
        ha="left", va="top", fontsize=7.4, color=INK["secondary"],
    )
    return fig


def main() -> int:
    data = compute()

    out = ROOT / "outputs" / "f2-truncation.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# truncation: the discarded tail, and the cost of sigma -> 0\n")
        fh.write("quantity,k_com,ell,value\n")
        for k, above in sorted(data["tail"].items()):
            for l, a in zip(ELLS, above):
                fh.write(f"tail_above,{k:.4f},{int(l)},{a:.12e}\n")
        for name, values in data["cost"].items():
            for l, c in zip(ELLS_COST, values):
                fh.write(f"shear_cost_{name},,{int(l)},{c:.12e}\n")
    print(f"wrote {out.relative_to(ROOT)}")

    for p in save_figure(draw(data), "f2-truncation", "v1.2.0"):
        print(f"wrote {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
