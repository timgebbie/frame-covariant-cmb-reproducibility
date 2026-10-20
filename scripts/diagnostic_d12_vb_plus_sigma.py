#!/usr/bin/env python3
r"""D12 --- $v_B+\sigma$ differenced between the two columns, before projection.

**P1-T, 2026-10-19, converting CAMB's source into this bundle's slots.** CAMB
carries the rank-1 scattering source as $g\,(v_b+\sigma)$ --- *one object*.
Under a boost $v_b\to v_b-v$ while $\sigma$ shifts oppositely, so the sum is
invariant and **CAMB has no frame gap because it never separates them.** This
bundle does separate them, so the two columns must each produce the same sum.

**Why this is strictly stronger than the frame gap on $\tau_\ell$.** It is a
statement about the *source*, evaluated before any line-of-sight integral:

    no transfer function, no j_l, no weight, no damping, no validity gate

A failure here is upstream of everything (102) does, which is where the gap has
already been localised (T-77, T-79). A pass here puts the defect downstream, in
the slots and weights --- P1-T's items 2 and 3.

**Nothing about the sign is assumed.** The boost sends $\Delta C_2=+v/k$ and
$\Delta\hat v_B=+v/k$ going Newtonian to CDM, so *a priori* the invariant is the
difference; both combinations are printed and the measurement says which, rather
than this docstring. That is **M5a**, which is the clause this register landed
one finding earlier.

Shapes, so the slots are unambiguous:

    v_b  = reduce_dipole(tau_1, k) = tau_1 / k          the REDUCED dipole (T-66)
    C_2  = v / k         and        a B_2 = a sigma = -k v        so C_2 = -a B_2 / k^2
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra.two_frame import build_environment, coefficient_sets  # noqa: E402

SLUG = "d12-vb-plus-sigma"
VERSION = "v1.3.0"

KS = (1.0, 10.0, 60.0, 300.0)


def rel(a, b):
    """Max |a-b| over the grid, against the larger column's own scale."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    scale = max(np.max(np.abs(a)), np.max(np.abs(b)))
    return float(np.max(np.abs(a - b)) / (scale if scale > 0 else 1.0))


def _report() -> None:
    print(__doc__.split("Shapes")[0])
    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        # `line_of_sight_weight` is named because the release gate requires it
        # (A-1, enforced after T-57). D12 never reaches the line-of-sight
        # integral, so it cannot depend on the choice; 'printed' is the T-69
        # default, which keeps this environment identical to the one every other
        # number in the register was measured in.
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        print(f"\n=== {label} ===   does v_B + sigma agree between the columns?")
        print(f"  {'k':>5s} {'|d(v_b)|':>12s} {'|d(C_2)|':>12s}"
              f" {'|d(v_b - C_2)|':>16s} {'|d(v_b + C_2)|':>16s}")
        print("  " + "-" * 66)
        for k in KS:
            n_, c_ = coefficient_sets(float(k), env)
            # **CoefficientSet.v_b is the UN-REDUCED dipole** --- both sets
            # store `v_b = k * vb_t` (coefficients.py:677, 983), while C_2 is
            # v/k. Differencing them as stored is M4, and the first run of
            # this script did exactly that: every residual came out at
            # (k-1) x the boost, which is the signature of a normalisation
            # and not of a dynamics. Reduce first.
            nv, cv = n_.v_b / float(k), c_.v_b / float(k)
            n2, c2 = n_.coefficients.c2, c_.coefficients.c2
            print(f"  {k:5.0f} {rel(nv, cv):12.3e} {rel(n2, c2):12.3e}"
                  f" {rel(nv - n2, cv - c2):16.3e} {rel(nv + n2, cv + c2):16.3e}")
    print("\n  Columns 1 and 2 are the two halves apart; one of columns 3 and 4")
    print("  is the CAMB combination. Machine zero there puts the defect")
    print("  DOWNSTREAM of the source, in the slots and weights. Anything else")
    print("  puts it upstream of (102) entirely.")

    # ---- M11b: the validity condition, stated before the number is read -----
    #
    # `rel` divides by max|.| over the WHOLE grid. v_B oscillates, and faster
    # with k, so two integrations that are a boost apart but a fraction of a
    # period out of PHASE would also score O(1) here -- large, finite, and
    # meaning something other than "the boost fails". k=1 does not oscillate at
    # all, which is exactly the cell that passes, so the alternative explanation
    # fits every row. It has to be excluded before the table above is read.
    #
    # The discriminator: a boost failure leaves a residual with the SHAPE of
    # the boost; a phase error leaves one with the shape of the DERIVATIVE.
    print("\n  === is it the boost, or is it phase? (M11b) ===")
    print("  Newtonian v_b minus CDM v_b, against the boost v/k it should be.")
    print(f"  {'bg':<7} {'k':>5s} {'|res|/|v/k|':>13s} {'corr(res, v/k)':>16s}"
          f" {'corr(res, d/d.eta)':>20s}")
    print("  " + "-" * 66)
    for label, bg, obh2, h in (("EdS", CDM_MODEL, 0.0224, 0.5),
                               ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H)):
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
        for k in KS:
            n_, c_ = coefficient_sets(float(k), env)
            diff = (np.asarray(n_.v_b, float) - np.asarray(c_.v_b, float)) / float(k)
            boost = np.asarray(c_.coefficients.c2, float)      # = v/k
            res = diff - boost
            dvb = np.gradient(np.asarray(c_.v_b, float) / float(k), env.eta,
                              edge_order=2)

            def corr(x, y):
                x, y = x - x.mean(), y - y.mean()
                d = np.sqrt((x * x).sum() * (y * y).sum())
                return float((x * y).sum() / d) if d > 0 else 0.0

            sc = np.max(np.abs(boost))
            print(f"  {label:<7} {k:5.0f} {np.max(np.abs(res)) / sc:13.3e}"
                  f" {corr(res, boost):16.3f} {corr(res, dvb):20.3f}")
    print("\n  A residual aligned with v/k is a BOOST failure. One aligned with")
    print("  d(v_b)/d(eta) is a PHASE error between two integrations, and is a")
    print("  grid finding, not a frame finding.\n")


def main() -> int:
    """Print the report **and write it**, so `diagnostics/` is regenerated
    rather than hand-captured from a console redirect --- finding **T-87**."""
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _report()
    text = buf.getvalue()
    print(text, end="")
    out = ROOT / "diagnostics" / f"{SLUG}-{VERSION}.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
