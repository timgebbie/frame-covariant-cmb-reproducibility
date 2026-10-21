#!/usr/bin/env python3
r"""D20 --- what the two $h$ defects in the scattering rate are worth.

**Finding T-108, raised by the PI 2026-10-21.** `decoupling.RECOMBINATION_H`
switches between

    "released"    h = 0.674 in the Peebles ODE on every background, and
                  c/H_0 taken at h = 1 so the surviving 1/h is dropped
    "corrected"   the background's own h in both places

and this measures what moves. **Nothing is flipped by running it** --- T-107
is six hours old and is the register's standing reason: there, every stated
acceptance condition passed and criterion 5b still caught the repair at 98.5%.

WHY THE TWO LAND TOGETHER
-------------------------
The surviving $1/h$ cannot be applied without knowing $h$ per background, and
knowing $h$ per background *is* the second defect. **M11a is satisfied by the
arithmetic rather than by choice.**

WHAT IS MEASURED, AND AGAINST WHAT
----------------------------------
$\kappa'$ sets the visibility. Its peak fixes $z_*$ and therefore $r_s$; its
width fixes the Silk damping envelope. So the quantities are $z_*$, the
visibility peak and width, $r_s$, $r_\theta$ and $\ell_A=\pi r_\theta/r_s$.

**And there is an external known answer here, which is rare in this register.**
CAMB and CLASS, matched to this bundle's $N_{\rm eff}=0$, put $z_*=1088.5$ and
the first peak at $\ell\simeq206$. The released bundle has $z_*=1114.5$. Raising
$\kappa'$ makes recombination finish **later**, which lowers $z_*$ --- so the
correction's sign is known in advance and the question is only its size.

**That matters because of M14.** T-107's repair passed every condition built
from frame differences and was still wrong. $z_*$ against 1088.5 is not a
difference and not self-referential: it is the gate this correction has to
face.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLUG = "d20-recombination-h"
VERSION = "v1.3.0"

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL, LCDM_MODEL, PLANCK_MODEL, PLANCK_H, PLANCK_OMEGA_B_H2)
from functions.spectra import decoupling as D  # noqa: E402
from functions.spectra.two_frame import build_environment  # noqa: E402
from functions.spectra.acoustic import sound_horizon_from_zero  # noqa: E402

#: CAMB and CLASS, specialised to this bundle's N_eff = 0. flrw.py:233-240.
CAMB_Z_STAR = 1088.5
CAMB_FIRST_PEAK = 206.0

MODELS = (("EdS", CDM_MODEL, 0.0224, 0.5),
          ("LCDM", LCDM_MODEL, 0.0224, 0.7),
          ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H))


def _measure(bg, obh2, h, mode):
    was, D.RECOMBINATION_H = D.RECOMBINATION_H, mode
    try:
        env = build_environment(400.0, omega_m=bg.omega_m,
                                omega_lambda=bg.omega_lambda, omega_r=bg.omega_r,
                                omega_b_h2=obh2, hubble_h=h,
                                line_of_sight_weight="printed")
    finally:
        D.RECOMBINATION_H = was
    eta = np.asarray(env.eta, dtype=float)
    vis = np.asarray(env.visibility, dtype=float)
    kp = np.asarray(env.kappa_prime, dtype=float)
    i = int(np.argmax(vis))
    # FWHM of the visibility, in conformal time
    half = vis[i] / 2.0
    above = np.where(vis >= half)[0]
    width = float(eta[above[-1]] - above.size and eta[above[-1]] - eta[above[0]])
    a_star = float(bg.a_of_eta(np.array([eta[i]]))[0])
    z_star = 1.0 / a_star - 1.0
    # **r_s is accumulated FROM THE BIG BANG**, which is what (180)'s
    # cos(k r_s) means and what `make_model_table.py` uses. A first draft of
    # this file integrated from the recombination grid's own first point
    # instead, missing everything below z = 3000, and returned l_A = 553 on
    # PLANCK against the generated table's 272.177 --- a factor of 2.03 that
    # would have gone into the headline. Caught by reading the two against
    # each other, which is the only reason the table is generated.
    eta_rs, rs_tab = sound_horizon_from_zero(bg, float(eta[i]), omega_b_h2=obh2)
    rs = float(np.interp(float(eta[i]), eta_rs, rs_tab))
    r_theta = float(bg.eta_0 - eta[i])
    return {"z_star": z_star, "eta_star": float(eta[i]),
            "kp_star": float(kp[i]), "vis_peak": float(vis[i]),
            "width": width, "r_theta": r_theta, "r_s": rs,
            "l_A": float(np.pi * r_theta / rs) if rs else float("nan")}


def _report() -> None:
    print(__doc__.split("WHAT IS MEASURED")[0])
    for name, bg, obh2, h in MODELS:
        rel = _measure(bg, obh2, h, "released")
        cor = _measure(bg, obh2, h, "corrected")
        print(f"\n{'='*78}\n  {name}   h = {h}   (released runs it at 0.674)\n{'='*78}")
        print(f"  {'quantity':<22} {'released':>14} {'corrected':>14} {'ratio':>10}")
        print("  " + "-" * 64)
        for key, label in (("kp_star", "kappa'(eta_*)"),
                           ("z_star", "z_*"),
                           ("eta_star", "eta_*"),
                           ("r_theta", "r_theta"),
                           ("width", "visibility FWHM"),
                           ("vis_peak", "visibility peak"),
                           ("r_s", "r_s (sound horizon)"),
                           ("l_A", "l_A = pi r_theta / r_s")):
            a, b = rel[key], cor[key]
            r = b / a if a else float("nan")
            print(f"  {label:<22} {a:14.5g} {b:14.5g} {r:10.4f}")
        print(f"\n  z_* against CAMB/CLASS at N_eff = 0 ({CAMB_Z_STAR}):")
        print(f"      released  {rel['z_star']:8.2f}   "
              f"({rel['z_star'] - CAMB_Z_STAR:+.2f}, "
              f"{100*(rel['z_star']/CAMB_Z_STAR - 1):+.2f}%)")
        print(f"      corrected {cor['z_star']:8.2f}   "
              f"({cor['z_star'] - CAMB_Z_STAR:+.2f}, "
              f"{100*(cor['z_star']/CAMB_Z_STAR - 1):+.2f}%)")
        closer = abs(cor['z_star'] - CAMB_Z_STAR) < abs(rel['z_star'] - CAMB_Z_STAR)
        print(f"      -> the correction moves z_* "
              f"{'TOWARDS' if closer else 'AWAY FROM'} the external value")

    print("""
  READING THIS
  ------------
  kappa'(eta_*) does NOT rise by 1/h, and an earlier draft of this file said
  it must. That was wrong and is recorded as wrong: the SCALE rises by 1/h,
  but kappa' is then read at a peak that has MOVED, and a later peak sits at a
  lower electron density. On PLANCK the released h (0.674) and the true one
  (0.6736) are the same number to four figures, so defect (b) does nothing
  there and the 1.48 of defect (a) is the whole change in the scale -- and
  kappa'(eta_*) still comes out at 0.977, because eta_* moved by 2.3%. The row
  is reported because it is the input, not because its ratio is a check.

  z_* is the row that decides. It is an EXTERNAL known answer, specialised to
  this bundle's own N_eff = 0, and it is not a frame difference and not a
  self-comparison -- which is M14's requirement after T-107 passed four
  conditions and was still wrong.

  A correction that raises kappa' must LOWER z_*: more scattering means
  recombination finishes later. The sign is known in advance, so only the size
  is in question, and a correction that moved z_* the other way would be
  refuted on the spot.

  NOT MEASURED HERE: the spectrum. r_s and the damping scale follow from these
  quantities and the peaks follow from those, but C_l is a 45-minute run and
  it comes after this, not beside it. M11.
""")


def main() -> int:
    import contextlib
    import io
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
