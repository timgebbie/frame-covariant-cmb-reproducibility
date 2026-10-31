#!/usr/bin/env python3
r"""The three backgrounds side by side, with every derived scale.

    python scripts/make_model_table.py            # print
    python scripts/make_model_table.py --write    # and write the provenance file

**The PI's request, 2026-10-19, and it is a diagnostic rather than a
convenience.** The three models were defined in three places and compared
nowhere, so a question like *"is the difference between panels a parameter
difference?"* had no cheap answer. It does now: everything a spectrum's shape
depends on is in one table, derived from the `Background` objects the code
actually integrates --- **not transcribed from the parameter sheet**.

`provenance/COSMOLOGICAL-PARAMETERS-v1.md` stays as it is: it is the
*citation* for the Planck column, which is a different job. This file is what
the code does with it.

The columns that set the acoustic scale are the last three. $\ell_A=\pi
r_\theta/r_s$ is what fixes where the peaks sit, and reading it beside
$\Omega_m$, $\Omega_\Lambda$ and $h$ is how a parameter difference is told
apart from a defect.

FINDING T-181 --- THE SUPPLEMENT CARRIED THIS TABLE FROM BEFORE A REPAIR
------------------------------------------------------------------------
On **2026-10-21**, `f887301` set `decoupling.RECOMBINATION_H = "corrected"`:
the $h$ in the Peebles ODE became the background's own, and the surviving
$1/h$ stopped being dropped. **D20 measured exactly what that would move** and
its `corrected` column is the live code's answer to four figures. Eight of the
fifteen rows below moved with it, and the committed table was generated the
day before:

    row                  committed      live        shift (PLANCK)
    z_*                   1114.54      1079.44      -3.1%
    eta_*                0.0697426    0.0713209     +2.3%
    r_s                  0.0361159    0.0368321     +2.0%
    l_A                   272.177      266.750      -2.0%
    k_D                   536.866      557.012      +3.8%   (+10.1% on EdS)

**The row that changes an argument rather than a number is $z_*$.**
`tables/criterion-5b-v1.2.0.tex` itemised the bundle's residual against
CAMB/CLASS with *"the acoustic scale, $z_*=1114.5$ here against CAMB's
1088.5"* --- a cost of $+2.40\%$. The live value is $1079.44$, which is
$-0.83\%$: **the repair moved the bundle to the other side of the external
value, and the published text still claimed the old side.** D20 said so in
terms at the time (*"the correction moves z_* TOWARDS the external value"*)
and nothing read it back into the table.

WHY IT SURVIVED A REGENERATION
------------------------------
`tables/model-parameters-layout-v1.3.5.tex` is what the supplement actually
`\input`s, and it was committed on **2026-10-25**, four days *after* the
repair, with a header reading *"CAPTION PRESENTATION COPY, all numeric cells
unchanged"*. It is the base table plus two lines: a header comment and one
`\captionsetup`. It is a **hand-made third rendering**, and its own caption
says the table is *"generated ... not transcribed"* --- a claim that was false
of the file carrying it.

Decision **D3** is written three functions below in as many words: *"a table
the document carries is generated from the code or it drifts. One generator,
two renderings."* The drift is what happens when someone adds the third by
hand. So `render_tex` now takes `layout=`, `--write` emits all three, and the
presentation copy is generated like the other two. **The filename stays at
`v1.3.5`** because it is a contract with the supplement's `\input` line, and
that line is P1-T's.

Each output carries a `source_fingerprint` of the tree that produced it
(**T-54**, repaired at **T-129**), so the next time this question is asked it
is answered by reading one line rather than by re-deriving the history of a
switch.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _fingerprint import source_fingerprint as _digest  # noqa: E402

from functions.background.flrw import (  # noqa: E402
    CDM_MODEL,
    LCDM_MODEL,
    PLANCK_H,
    PLANCK_MODEL,
    PLANCK_N_S,
    PLANCK_OMEGA_B_H2,
)
from functions.spectra.acoustic import (  # noqa: E402
    baryon_photon_ratio,
    sound_horizon_from_zero,
)
from functions.spectra.decoupling import RecombinationHistory, diffusion_scale  # noqa: E402

VERSION = "v1.3.0"

#: The presentation copy's filename, **pinned separately and deliberately**.
#: The supplement's `\input` line names it, that line is P1-T's, and a
#: generator must not rename a file out from under a document it does not own.
LAYOUT_VERSION = "v1.3.5"

#: `(label, Background, omega_b_h2, h, n_s)`. `h` and `n_s` are the values the
#: *figures* pass, which is the thing that matters for a shape comparison ---
#: `Background` itself carries `h0 = 1` for all three, the bundle working in
#: units of $c/H_0$.
MODELS = [
    ("CDM (Einstein-de Sitter)", CDM_MODEL, 0.0224, 0.5, 1.0),
    ("LCDM", LCDM_MODEL, 0.0224, 0.7, 1.0),
    ("PLANCK", PLANCK_MODEL, PLANCK_OMEGA_B_H2, PLANCK_H, PLANCK_N_S),
]


def row(label, bg, omega_b_h2, hubble_h, n_s):
    rec = RecombinationHistory.build(bg, omega_b_h2=omega_b_h2)
    eta_star = float(rec.eta_star)
    eta_rs, r_s_tab = sound_horizon_from_zero(bg, eta_star, omega_b_h2=omega_b_h2)
    r_s = float(np.interp(eta_star, eta_rs, r_s_tab))
    r_theta = float(bg.eta_0) - eta_star
    a_star = float(bg.a_of_eta(np.array([eta_star]))[0])
    k_d = diffusion_scale(rec, r_of_eta=np.zeros_like(rec.eta))
    return {
        "model": label,
        "Omega_m": bg.omega_m,
        "Omega_L": bg.omega_lambda,
        "Omega_r": bg.omega_r,
        "omega_b h^2": omega_b_h2,
        "h": hubble_h,
        "n_s": n_s,
        "eta_0": float(bg.eta_0),
        "eta_*": eta_star,
        "a_*": a_star,
        "z_*": 1.0 / a_star - 1.0,
        "R(eta_*)": float(baryon_photon_ratio(
            np.array([a_star]), omega_b_h2=omega_b_h2)[0]),
        "r_s": r_s,
        "r_theta": r_theta,
        "l_A": np.pi * r_theta / r_s,
        "k_D": float(k_d(eta_star)),
    }


KEYS = ["Omega_m", "Omega_L", "Omega_r", "omega_b h^2", "h", "n_s",
        "eta_0", "eta_*", "a_*", "z_*", "R(eta_*)",
        "r_s", "r_theta", "l_A", "k_D"]

NOTE = {
    "Omega_r": "zero on two of three -- **A-3 and T(k) are both identically "
               "inapplicable there**, which is what makes EdS the control. "
               "**For `LCDM` it is neither a control nor intended** and is "
               "recorded at **T-80**: at $z_*\\simeq1109$ the omitted "
               "radiation is not negligible",
    "eta_*": "conformal time at the visibility peak, not at kappa = 1",
    "R(eta_*)": "baryon loading; sets the acoustic amplitude (1+3R)/3 and the "
                "offset -R",
    "r_s": "sound horizon at eta_*, integrated from the big bang (T-51/S40)",
    "r_theta": "eta_0 - eta_*, the angular-diameter distance in these units",
    "l_A": "**pi r_theta / r_s -- where the acoustic peaks sit.** A difference "
           "between two models' spectra is a parameter difference only if it "
           "tracks this",
    "k_D": "diffusion scale at eta_*; the damping knee. **This row is the "
           "$R=0$ value** --- `diffusion_scale` is called with "
           "`r_of_eta = zeros`, which is finding **T-21**, while the "
           "oscillator beside it runs at the `R(eta_*)` three rows up. T-21 "
           "measured the cost: $\\ell_D = 1783$ as called against $1985$ with "
           "the $R$ the bundle already has. Read it as the damping the code "
           "applies, **not** as the damping the parameters imply",
}


def fmt(v):
    if isinstance(v, str):
        return v
    if v == 0:
        return "0"
    return f"{v:.6g}" if (1e-3 <= abs(v) < 1e5) else f"{v:.4e}"


def render(rows):
    out = [f"# The three backgrounds, side by side",
           "",
           f"**Generated by `scripts/make_model_table.py` on {date.today().isoformat()}. "
           "Do not edit by hand.**",
           "",
           "Derived from the `Background` objects the code integrates, **not "
           "transcribed** from the parameter sheet. "
           "`provenance/COSMOLOGICAL-PARAMETERS-v1.md` is the *citation* for "
           "the Planck column and stays as it is; this is what the code does "
           "with it.",
           "",
           "| | " + " | ".join(r["model"] for r in rows) + " |",
           "|---|" + "---|" * len(rows)]
    for k in KEYS:
        out.append(f"| `{k}` | " + " | ".join(fmt(r[k]) for r in rows) + " |")
    out += ["", "## How to read it", ""]
    for k, why in NOTE.items():
        out.append(f"- **`{k}`** --- {why}.")
    out += ["",
            "**The last three rows are the ones that answer a shape question.** "
            "Two models whose spectra differ *in the position of the peaks* "
            "differ in `l_A`. Two whose peaks sit at the same `l_A` and still "
            "look different do **not** differ by a parameter, and the "
            "difference is somewhere in "
            "`provenance/BUNDLE-DEFECTS-v1.md`.",
            ""]
    return "\n".join(out)


def _tex_num(v: str) -> str:
    """`1.23e-05` to `$1.23\\times10^{-5}$`, and a plain number to math mode.

    Written out rather than done with two `str.replace` calls, because the
    first draft of this function produced `5.4502\\times10^{-5` --- an
    unclosed brace in text mode --- which `pdflatex` would have rendered as
    garbage on a page nobody reads closely. A number in a generated table is
    exactly where that is not noticed.
    """
    m = re.fullmatch(r"(-?[\d.]+)e([+-])0*(\d+)", v)
    if m:
        mant, sign, exp = m.groups()
        return f"${mant}\\times10^{{{'-' if sign == '-' else ''}{exp}}}$"
    return f"${v}$"

def render_tex(rows, *, layout: bool = False):
    r"""The same table as LaTeX, for the supplement. **Same `rows`, one
    generator** --- the Markdown and the TeX cannot disagree because neither
    is transcribed from the other.

    `layout=True` emits the presentation copy the supplement `\input`s: the
    identical table plus one `\captionsetup`. **It is a rendering flag and not
    a second table** --- finding T-181, where the presentation copy was made
    by hand, survived the recombination repair by four days, and put eight
    stale rows into the published PDF under a caption claiming it was
    generated.
    """
    esc = {"Omega_m": r"$\Omega_m$", "Omega_L": r"$\Omega_\Lambda$",
           "Omega_r": r"$\Omega_r$", "omega_b h^2": r"$\omega_b h^2$",
           "h": r"$h$", "n_s": r"$n_s$", "eta_0": r"$\eta_0$",
           "eta_*": r"$\eta_*$", "a_*": r"$a_*$", "z_*": r"$z_*$",
           "R(eta_*)": r"$R(\eta_*)$", "r_s": r"$r_s$",
           "r_theta": r"$r_\theta$", "l_A": r"$\ell_A=\pi r_\theta/r_s$",
           "k_D": r"$k_D$ (at $R=0$, T-21)"}
    out = [r"\begin{table}[htbp]", r"\centering\small"]
    if layout:
        out.append(r"\captionsetup{width=0.76\linewidth,"
                   r"justification=raggedright,singlelinecheck=false}")
    out += [r"\caption{The three backgrounds side by side, with every derived "
           r"scale. \textbf{Generated by \texttt{scripts/make\_model\_table.py}} "
           r"from the \texttt{Background} objects the code integrates, not "
           r"transcribed. The last three rows are the ones that answer a shape "
           r"question: two models whose peaks differ in position differ in "
           r"$\ell_A$, and two whose peaks sit at the same $\ell_A$ and still "
           r"differ do not differ by a parameter. $\Omega_r=0$ is the control "
           r"on \textsc{cdm} and finding \textbf{T-81c} on \textsc{lcdm}; "
           r"$k_D$ is the $R=0$ value, finding \textbf{T-21}.}",
           r"\label{tab:model-parameters}",
           r"\begin{tabular}{l" + "r" * len(rows) + "}", r"\toprule",
           " & " + " & ".join(r["model"].replace("Einstein-de Sitter",
                                                 r"Einstein--de Sitter")
                              for r in rows) + r" \\", r"\midrule"]
    for k in KEYS:
        cells = " & ".join(_tex_num(fmt(r[k])) for r in rows)
        out.append(f"{esc.get(k, k)} & {cells} " + r"\\")
    out += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(out)

def main() -> int:
    rows = [row(*m) for m in MODELS]
    text = render(rows)
    print(text)
    if "--write" in sys.argv:
        stamp = _digest(__file__)
        out = ROOT / "provenance" / f"MODEL-PARAMETERS-{VERSION}.md"
        out.write_text(f"<!-- sources: {stamp} -->\n" + text + "\n",
                       encoding="utf-8", newline="\n")
        print(f"\nwrote {out.relative_to(ROOT)}")
        # **The supplement needs this table too and must not transcribe it.**
        # The PI asked where the model parameters are in the supplement, which
        # is the question decision D3 exists to make unaskable: a table the
        # document carries is generated from the code or it drifts. One
        # generator, two renderings -- **three since T-181**, because the
        # presentation copy the supplement actually reads was the one being
        # made by hand, and it is the one that drifted.
        tex = ROOT / "tables" / f"model-parameters-{VERSION}.tex"
        tex.parent.mkdir(exist_ok=True)
        tex.write_text(f"% sources: {stamp}\n" + render_tex(rows) + "\n",
                       encoding="utf-8", newline="\n")
        # **The filename stays `v1.3.5`.** It is a contract with
        # `\input{tables/model-parameters-layout-v1.3.5.tex}` in the
        # supplement, and the supplement is P1-T's. A version in a generated
        # filename tracks the table's SCHEMA -- which rows exist -- and the
        # rows did not change. Which code produced the numbers is what the
        # fingerprint on line one says, and saying it there is the repair.
        lay = ROOT / "tables" / f"model-parameters-layout-{LAYOUT_VERSION}.tex"
        lay.write_text(
            f"% {LAYOUT_VERSION} caption presentation copy. GENERATED -- "
            f"see T-181.\n% sources: {stamp}\n"
            + render_tex(rows, layout=True) + "\n",
            encoding="utf-8", newline="\n")
        print(f"wrote {lay.relative_to(ROOT)}")
        print(f"wrote {tex.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
