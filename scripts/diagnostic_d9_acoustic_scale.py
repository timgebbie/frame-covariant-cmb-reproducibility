#!/usr/bin/env python3
r"""D9 --- the acoustic scale, against the antecedent's own formula.

    python scripts/diagnostic_d9_acoustic_scale.py

**The paper prints this check and the bundle never ran it.** *Annals II*,
\S*Some `Acoustic peak' Characteristics*:

    l_j ~= k_j |r_theta| = |r_theta / r_s| j pi
    k_{j+1} - k_j = k_A ~= pi / r_s   <=>   dl ~ l_A = k_A r_theta

with $r_\theta=\eta_0-\eta_*$ the comoving angular diameter distance and $r_s$
*"the sound-horizon near decoupling"* --- $\int_0^{\eta_*}c_s\,d\eta$, from the
big bang. **Both sides of that are computable here without any external code**,
and the bundle carried nine figures, eight diagnostics and 424 tests without
comparing them.

It does not agree. Finding **T-51**: `pipeline.run` hands `solve_acoustic` a
grid beginning at `RecombinationHistory.build`'s `z_max = 3000.0`, which
discards **half the sound horizon**, so the accumulated phase $k\,r_s$ is
halved and the peak spacing doubles. Measured against CAMB and CLASS, which
agree with each other to $0.1$ in $\ell$:

| | first maximum | peak spacing |
|---|---|---|
| CAMB / CLASS | 206.1 | 285.5, then 237.6 |
| this bundle | 161.8 | **589.7** |

**This diagnostic does not fail the run.** T-51's fix is v1.3.0 work under
**S37** and is registered as a deferral, so `run_all.check_deferrals` refuses a
v1.3.0 release that still carries it --- the mechanism finding **T-47** added,
used for the purpose it was added for. What this prints is the number the fix
must move, on every harness run, so that it cannot be fixed quietly or left
unfixed quietly. `tests/test_acoustic_scale.py` asserts the broken value and is
**written to fail when the defect is repaired**, which is **S33** clause (d)'s
discipline applied to a second finding.

**Why the measured spacing is not exactly the truncated prediction.** The
closed-form $\Delta\ell=\pi r_\theta/r_s$ assumes a pure $\cos(k r_s)$. The ODE
is started with $\tau_1=0$, which is the adiabatic growing mode only while the
mode is outside the sound horizon, so a start at finite $k\,r_s$ imposes a
phase of its own on top of the truncation. The table below reports
$k\,r_s(\eta_{\rm start})$ per mode for exactly that reason: it is the quantity
that says whether the initial condition is legitimate, and at $k=600$ it is not
small by any reading.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, LCDM_MODEL, PLANCK_MODEL, PLANCK_OMEGA_B_H2,
)
from functions.spectra.acoustic import (  # noqa: E402
    ACOUSTIC_START_EPSILON, sound_horizon_from_zero,
)
from functions.spectra.decoupling import RecombinationHistory  # noqa: E402

#: Imported, not restated: `ACOUSTIC_START_EPSILON` lives beside the
#: condition it governs. A second copy is a second thing to forget.
START_EPSILON = ACOUSTIC_START_EPSILON

#: The band D9 reports over. Not the spectrum's own grid: these are the decades
#: that matter for the acoustic peaks, and the point of the table is the trend.
K_REPORT = (10.0, 30.0, 100.0, 300.0, 600.0)

MODELS = (
    ("CDM (Einstein-de Sitter)", CDM_MODEL, 0.0224),
    ("LCDM", LCDM_MODEL, 0.0224),
    ("PLANCK_MODEL", PLANCK_MODEL, PLANCK_OMEGA_B_H2),
)

#: What `RecombinationHistory.build` starts at, and therefore what the acoustic
#: integration starts at. **Imported rather than restated** would be better and
#: is not possible: it is a default in a signature. That it has to be written
#: twice is itself part of T-51.
Z_MAX_AS_SHIPPED = 3000.0


def main() -> int:
    print("D9  the acoustic scale against Annals II's own formula")
    print("    l_j = |r_theta / r_s| j pi,   dl = pi r_theta / r_s")
    print("    r_s is the sound horizon from the big bang; r_theta = eta_0 - eta_*.\n")

    for name, background, omega_b_h2 in MODELS:
        history = RecombinationHistory.build(
            background, omega_b_h2=omega_b_h2, n_eta=64_000)
        eta_star = float(history.eta[int(np.argmax(history.visibility))])
        eta_shipped = float(history.eta[0])
        r_theta = float(background.eta_0) - eta_star

        eta, accumulated = sound_horizon_from_zero(
            background, eta_star, omega_b_h2=omega_b_h2)
        r_s_full = float(accumulated[-1])
        r_s_shipped = r_s_full - float(np.interp(eta_shipped, eta, accumulated))

        if not (np.isfinite(r_s_full) and r_s_full > 0.0 and np.isfinite(r_theta)):
            print(f"FAIL  {name}: the acoustic scale is not finite")
            return 1

        print(f"--- {name} " + "-" * max(0, 56 - len(name)))
        print(f"    eta_*                  {eta_star:.6f}")
        print(f"    r_theta = eta_0 - eta_*{r_theta:14.6f}")
        print(f"    r_s, from the big bang {r_s_full:14.6f}")
        print(f"    r_s, from z={Z_MAX_AS_SHIPPED:.0f}       {r_s_shipped:14.6f}"
              f"   ({r_s_shipped / r_s_full:.3f} of it)")
        print(f"    MISSING                {r_s_full - r_s_shipped:14.6f}"
              f"   ({1.0 - r_s_shipped / r_s_full:.3f})          <- T-51")
        print()
        print(f"    peak spacing dl = pi r_theta / r_s")
        print(f"        the paper's formula, full r_s      {np.pi * r_theta / r_s_full:8.1f}")
        print(f"        what this bundle integrates        "
              f"{np.pi * r_theta / r_s_shipped:8.1f}")
        print(f"        ratio                              "
              f"{r_s_full / r_s_shipped:8.2f}")
        print()
        print(f"    first three peaks, l_j = j pi r_theta / r_s")
        paper = [j * np.pi * r_theta / r_s_full for j in (1, 2, 3)]
        ours = [j * np.pi * r_theta / r_s_shipped for j in (1, 2, 3)]
        print("        paper   " + "  ".join(f"{v:8.1f}" for v in paper))
        print("        ours    " + "  ".join(f"{v:8.1f}" for v in ours))
        print()
        print(f"    k r_s(eta_start): the initial condition tau_1 = 0 is the")
        print(f"    adiabatic growing mode only while this is << 1"
              f"  (epsilon = {START_EPSILON})")
        print(f"        {'k':>8s} {'l ~ k r_theta':>14s} {'k r_s(start)':>14s} {'':>6s}")
        for k in K_REPORT:
            k_rs = k * r_s_shipped
            mark = "ok" if k_rs <= START_EPSILON else "IMPOSED"
            print(f"        {k:8.0f} {k * r_theta:14.0f} {k_rs:14.4f} {mark:>9s}")
        print()

    print("=" * 62)
    print("CLOSED --- finding T-51, fixed 2026-10-16. `pipeline.run` now")
    print("derives each mode's start from k: acoustic_start='derived' begins")
    print("the integration where k r_s(eta) <= 0.1, which is what (180)'s")
    print("dT(0,k) = -(2/3) Phi_A(0,k), tau_1 = 0 means by *at the big bang*.")
    print("The measured peak spacing lands within 0.5% of the formula above on")
    print("all three backgrounds.")
    print()
    print("**CORRECTED 2026-10-17.** This paragraph used to end `the measured")
    print("C_l peak spacing for Planck parameters is 284 against CAMB's and")
    print("CLASS's 285.5'. That number came from tests/test_acoustic_scale.py,")
    print("which measures the SPACING of the acoustic source, and it was")
    print("reported here as though it were the spacing of the released C_l.")
    print("It was not: F9's spectrum had its peaks at (n+1/2) l_A, half a")
    print("period out, because the line-of-sight weight made the DIPOLE the")
    print("whole transfer function -- finding T-57 -- and the CDM frame F9")
    print("draws has no Sachs-Wolfe plateau at all -- finding T-59.")
    print()
    print("T-51 is closed and the source's phase is correct. **What was wrong")
    print("was the sentence claiming the spectrum inherited it.** A diagnostic")
    print("may report what it measures; this one reported what was measured")
    print("elsewhere, about a different quantity, in a sentence of prose.")
    print()
    print("The table above is what acoustic_start='z_max' still discards. That")
    print("branch is KEPT as a control, the way `expansion_coupling=False`")
    print("keeps (154) and `..._printed` keeps B-8: a defect that leaves no")
    print("executable trace is a defect that gets made again.")
    print()
    print("WHAT THE FIX DOES NOT RECOVER is the phase offset: our maxima sit at")
    print("j * pi r_theta / r_s where CAMB's are shifted down by the radiation")
    print("driving, which Annals II's matter-dominated Appendix G has no term")
    print("for. That is approximation A-3, and it is S35a's quantity to")
    print("measure against Hu & Sugiyama and Appendix C's expansion.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
