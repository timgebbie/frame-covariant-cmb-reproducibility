#!/usr/bin/env python3
"""Emit the fields the solver computes and would otherwise discard.

    python scripts/emit_handover_fields.py

Writes, with the parameter set recorded in each file's header:

    outputs/lensing-kernel.csv   chi(eta), chi_*, and the inserted kernel
    outputs/line-of-sight-field.csv         the line-of-sight field and its running
                                        integral along one ray
    outputs/handover-params.txt the parameter set, once, in full

**STATUS: active. Convention imported: none.** Every quantity is read off the
objects this bundle integrates; nothing is recomputed from parameters.

**Floats are named by content, never by number.** P1-T's specification records
that the printed numbers moved under them --- `fig:efficiency` prints as Fig. 2
where the work order said Fig. 5 --- so a handover keyed to a number would reach
the wrong box.

`fig:efficiency` needs v1.0.0 and is complete here. `fig:bulk` needs v1.5.0 for
its $O(\\varepsilon^2\\ell)$ source; what v1.0.0 owes it is the **field** that
source is evaluated on, which is what the second file carries --- the integrand
of (176) at each $\\chi$ and its running integral, not just the endpoint $C_\\ell$
that (186) keeps.

**The governing rule**, from the work order: *if it is re-derived afterwards the
figure compares two different cosmologies and the agreement means nothing.* So
$\\chi_*$ here is the one the spectrum uses --- the **visibility peak** --- and the
inserted kernel is built from that same $\\chi_*$, not from a fresh one.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import LCDM_MODEL  # noqa: E402
from functions.spectra.acoustic import solve_acoustic  # noqa: E402
from functions.spectra.decoupling import RecombinationHistory, Weighting  # noqa: E402
from functions.spectra.emissions import (  # noqa: E402
    comoving_distance,
    lensing_efficiency,
    line_of_sight_field,
)
from functions.spectra.pipeline import (  # noqa: E402
    ETA_POINTS_PER_PERIOD,
    required_n_eta,
)
from functions.spectra.potentials import potentials  # noqa: E402
from functions.spectra.sources import (  # noqa: E402
    PerturbationHistory,
    ScatteringHistory,
    source_doppler,
    source_integrated,
)

#: The ray `fig:bulk` is drawn along. Stated here rather than chosen in the
#: figure, so the paper and the bundle cannot drift about which ray it is.
RAY_ELL = 20
RAY_K_COM = 60.0

#: Omega_b h^2, the one parameter the emissions need beyond the model itself.
OMEGA_B_H2 = 0.0224


def main() -> int:
    model = LCDM_MODEL
    recombination = RecombinationHistory.build(model, omega_b_h2=OMEGA_B_H2)

    # --- fig:efficiency --------------------------------------------------
    distance = comoving_distance(model, recombination)
    kernel = lensing_efficiency(distance)

    efficiency = ROOT / "outputs" / "lensing-kernel.csv"
    with efficiency.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# float=fig:efficiency  model={distance.model}\n")
        fh.write(f"# chi_star={distance.chi_star:.12e}  eta_star={distance.eta_star:.12e}\n")
        fh.write("# chi_star is the VISIBILITY PEAK, which is where (176)'s primary\n")
        fh.write("# term is evaluated. The inserted kernel below is built from this\n")
        fh.write("# same chi_star, never from a separately derived one.\n")
        fh.write("eta,chi,chi_over_chi_star,inserted_kernel\n")
        for e, c, k in zip(distance.eta, distance.chi, kernel):
            fh.write(f"{e:.12e},{c:.12e},{c / distance.chi_star:.12e},{k:.12e}\n")

    # --- fig:bulk --------------------------------------------------------
    # **T-3 guard.** The ray carries j_l(k_com (eta_0 - eta)), period pi/k in
    # eta. F3's spectrum was aliased because its grid was set against a band
    # edge of k=420; this ray sits at k=60, where the same 1500 points give
    # 24 samples per oscillation. That is comfortable -- but it was luck, not
    # design, so it is now checked here and recorded in the parameter file.
    n_eta = 1500
    span = float(model.eta_0 - recombination.eta[0])
    needed = required_n_eta(RAY_K_COM, span)
    per_period = np.pi / RAY_K_COM / (span / n_eta)
    if n_eta < needed:
        raise ValueError(
            f"the fig:bulk ray is aliased: {per_period:.1f} samples per j_l "
            f"oscillation at k={RAY_K_COM}, {ETA_POINTS_PER_PERIOD} required "
            f"(n_eta >= {needed}). See finding T-3."
        )
    eta = np.linspace(recombination.eta[0], model.eta_0, n_eta)
    phi_a, phi_h = potentials(model, eta)
    aH = model.conformal_hubble(model.a_of_eta(eta))
    opacity = np.interp(eta, recombination.eta, recombination.opacity)
    kappa_prime = np.interp(eta, recombination.eta, recombination.kappa_prime)
    visibility = np.interp(eta, recombination.eta, recombination.visibility)

    inside = eta <= 6.0 * recombination.eta_star
    acoustic = solve_acoustic(
        RAY_K_COM, eta[inside], background=model,
        phi_a=phi_a[inside], phi_h=phi_h[inside],
        omega_b_h2=OMEGA_B_H2, expansion_coupling=False,
    )
    pad = inside.size - inside.sum()
    delta_T = np.concatenate([acoustic.delta_T, np.full(pad, acoustic.delta_T[-1])])
    tau_1 = np.concatenate([acoustic.tau_1, np.full(pad, acoustic.tau_1[-1])])

    history = PerturbationHistory(
        eta=eta, delta_T=delta_T, phi_a=phi_a, phi_h=phi_h,
        tau_1=tau_1, v_b=tau_1, frame="newtonian",
    )
    scattering = ScatteringHistory(
        eta=eta, kappa_prime=kappa_prime, visibility=visibility,
        damping_k=float(np.inf),
    )
    source = source_doppler(
        history, scattering, RAY_K_COM, weight=opacity
    ) + source_integrated(
        history, scattering, RAY_K_COM, aH=aH, weight=opacity
    )

    ray = line_of_sight_field(
        RAY_ELL, RAY_K_COM, eta=eta, source=source, eta_0=model.eta_0
    )
    ray.to_csv(ROOT / "outputs" / "line-of-sight-field.csv")

    # --- the parameter set, once, in full --------------------------------
    params = ROOT / "outputs" / "handover-params.txt"
    with params.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("Parameter set for the handover fields\n")
        fh.write("Generated by scripts/emit_handover_fields.py. Do not edit by hand.\n\n")
        fh.write(f"  model              {distance.model}\n")
        fh.write(f"  Omega_b h^2        {OMEGA_B_H2}\n")
        fh.write(f"  eta_0              {model.eta_0:.12e}  [1/H0]\n")
        fh.write(f"  eta_*              {distance.eta_star:.12e}  (visibility peak)\n")
        fh.write(f"  chi_*              {distance.chi_star:.12e}\n")
        fh.write(f"  ray ell            {RAY_ELL}\n")
        fh.write(f"  ray k_com          {RAY_K_COM}\n")
        fh.write(f"  integrated weight  {Weighting.STANDARD_ISW.name}"
                 "  (opacity e^-kappa; see A-2)\n")
        fh.write(f"  recombination      equilibrium Saha\n")
        fh.write(f"  ray eta samples    {n_eta}  ({per_period:.1f} per j_l oscillation\n")
        fh.write(f"                     at k={RAY_K_COM}; {ETA_POINTS_PER_PERIOD} required, see T-3)\n\n")
        fh.write(f"  running excursion  {ray.running_excursion:.6e}\n")
        fh.write("    REPORTED, not tolerated.\n")
        fh.write("\n")
        fh.write("    READ THIS BEFORE USING THE NUMBER. It is NOT yet the quantity\n")
        fh.write("    the fig:bulk acceptance is written against, and the two must\n")
        fh.write("    not be conflated.\n")
        fh.write("\n")
        fh.write("      what this measures  the running line-of-sight integral of\n")
        fh.write("                          (176) departing from its endpoint value\n")
        fh.write("                          through the bulk of the ray\n")
        fh.write("      what the acceptance the running integral of the O(eps^2 l)\n")
        fh.write("      is about            ABERRATION operator K_perp . d(tau)/de\n")
        fh.write("                          returning to ITS endpoint -- Eq. (28),\n")
        fh.write("                          which is v1.5.0 and does not exist yet\n")
        fh.write("\n")
        fh.write("    v1.0.0 owes the FIELD that operator is evaluated on, which is\n")
        fh.write("    the tau_Al column. This fraction characterises that field; the\n")
        fh.write("    bulk-cancellation claim is tested at v1.5.0 on the operator.\n")
        fh.write("    A 12% figure here is therefore not a failed cancellation --\n")
        fh.write("    nothing has been asked to cancel yet.\n")

    for path in (efficiency, ROOT / "outputs" / "line-of-sight-field.csv", params):
        print(f"wrote {path.relative_to(ROOT)}")
    print(f"  chi_* = {distance.chi_star:.6f} [1/H0]   kernel endpoints "
          f"{kernel[np.argmin(np.abs(distance.chi))]:.6f} .. "
          f"{kernel[np.argmin(np.abs(distance.chi - distance.chi_star))]:.6f}")
    print(f"  ray l={RAY_ELL} k={RAY_K_COM}: endpoint {ray.endpoint:.6e}, "
          f"running excursion {ray.running_excursion:.4e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
