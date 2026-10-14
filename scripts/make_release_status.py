r"""Where every artefact sits on decision S27's maturity ladder, and what that
means for v1.1.0, v1.2.0 and v1.5.0.

**The rungs are declared here and the evidence is verified here.** A status
document that is typed is a status document that drifts: this one names, for
each artefact, the module it lives in, the test that checks it and whether it is
wired into `run_all.py`, and then **checks that each of those exists**. A claim
whose evidence is missing fails the script rather than appearing in the output.

    (P) prototype          it runs and produces a number; no claim attaches
    (C) proof of concept   checked against something it did not come from,
                           with a negative control, in tests/
    (R) release candidate  in run_all.py, portable, manifested, its claims
                           generated from the data they describe
    (S) shipped            in a tagged release, hashed, cited

Promotion is a measurement, not a judgement, and **demotion is normal**: finding
T-24 demoted the CDM-frame closure from C to P and it re-entered at C with a
different test. That is the ladder working.

Run:  python scripts/make_release_status.py
"""

from __future__ import annotations

import importlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@dataclass(frozen=True)
class Artefact:
    """One thing that can be at a rung, with the evidence for the rung it claims."""

    name: str
    rung: str                      # P, C, R or S
    release: str                   # the release it belongs to
    module: str = ""               # dotted module path, verified to import
    objects: tuple[str, ...] = ()  # attributes of that module, verified present
    tests: tuple[str, ...] = ()    # test function names, verified to exist
    script: str = ""               # path under scripts/, verified in run_all.py for R
    note: str = ""
    blocks: tuple[str, ...] = field(default_factory=tuple)


#: **Declared, then verified.** Editing a rung here without the evidence to
#: match it makes the script fail, which is the only way a ladder stays honest.
ARTEFACTS: list[Artefact] = [
    # ---- v1.0.0, shipped -------------------------------------------------
    Artefact("the Appendix F chain against four external hierarchies", "S", "v1.0.0",
             module="functions.spectra.kernels",
             tests=("test_no_coupling_in_the_v1_hierarchy_grows_with_ell",),
             script="scripts/figure_f1_appendix_f.py"),
    Artefact("both routes to (186), agreeing exactly", "S", "v1.0.0",
             module="functions.spectra.angular",
             objects=("cl_mode_route", "cl_covariant_route", "AngularSpectrum"),
             script="scripts/figure_f3_angular_spectrum.py",
             note="exactly zero since T-17 put the combined coefficients in Q"),
    Artefact("the Sachs-Wolfe limit, criterion 5a", "S", "v1.0.0",
             module="functions.spectra.sachs_wolfe",
             script="scripts/diagnostic_d5_sachs_wolfe.py"),

    # ---- v1.1.0, release candidate --------------------------------------
    Artefact("Peebles recombination, default from this release (S22)", "S", "v1.1.0",
             module="functions.spectra.peebles",
             script="scripts/figure_f6_approximations.py",
             note="freeze-out 2.15e-4 against a standard ~2e-4; visibility peak "
                  "z~1107 against a standard 1080-1100"),
    Artefact("the frame change made numerical", "S", "v1.1.0",
             module="functions.spectra.frame_transform",
             objects=("FrameShift", "cdm_frame_shift", "to_frame"),
             tests=("test_T27_the_dipole_carries_the_same_inverse_k_as_the_monopole",)),
    Artefact("criterion 2's curvature half", "S", "v1.1.0",
             module="functions.frames",
             objects=("weyl_invariance_residual", "weyl_electric_amplitude"),
             script="scripts/diagnostic_d2_roundtrip.py"),

    # ---- v1.2.0, in progress --------------------------------------------
    Artefact("the covariant coefficients C_0, C_1, C_2 from (89)", "C", "v1.2.0",
             module="functions.spectra.coefficients",
             objects=("match_coefficients", "newtonian_coefficients", "newtonian_set"),
             tests=("test_all_three_of_90_are_reproduced_by_the_match",
                    "test_b11_is_a_sign_in_89_not_in_90",
                    "test_the_newtonian_specialisation_is_equation_109"),
             note="(89) is implemented as the definition so (90) is a check; "
                  "B-11's delta_l0 sign resolved"),
    Artefact("the integral solution (102), carried with a generic u^a", "C", "v1.2.0",
             module="functions.spectra.integral_solution",
             objects=("integral_solution", "required_multipoles"),
             tests=("test_the_shear_boundary_term_is_empty_in_the_newtonian_frame",
                    "test_the_shear_boundary_term_is_not_empty_once_b2_is",
                    "test_the_specialisation_recovers_what_the_pipeline_computes")),
    Artefact("the generic source derivatives Annals II never wrote", "C", "v1.2.0",
             module="functions.spectra.coefficients",
             objects=("generic_shear_derivatives", "c2_derivatives"),
             tests=("test_the_rank_two_control_passes_symbolically",
                    "test_no_numerical_derivative_survives_in_the_c2_chain"),
             note="rank 2 closed from Appendix G with a control; rank 1 assembled "
                  "from printed equations and still carrying (*)"),
    Artefact("the CDM frame as a second frame", "C", "v1.2.0",
             module="functions.spectra.coefficients",
             objects=("cdm_frame_shear", "cdm_set", "background_fluid"),
             tests=("test_the_frame_shift_of_every_coefficient_is_the_closed_form_one",
                    "test_B13_the_printed_n_t1_does_not_close_and_the_general_rule_does",
                    "test_T24_the_closure_is_an_identity_in_both_conventions")),
    Artefact("the frame-invariance measurement, F5's question", "R", "v1.2.0",
             module="functions.spectra.coefficients",
             script="scripts/measure_frame_invariance.py",
             note="generated record; its prose is computed from its own table"),
    Artefact("the ell ceiling removed, 507 -> 2000", "C", "v1.2.0",
             module="functions.spectra.bessel_table",
             objects=("BesselTable",),
             tests=("test_unavailable_ell_is_refused",
                    "test_the_coefficients_are_exact_rationals_not_floats"),
             note="findings T-17 and T-18"),
    Artefact("the stamped Planck 2018 parameter set", "P", "v1.2.0",
             module="functions.background.flrw",
             note="provenance/COSMOLOGICAL-PARAMETERS-v1.md; the paper's own "
                  "stated baseline column, not one chosen here",
             blocks=("recorded but not wired into a model constant, and nothing "
                     "checks the stamp against the release's round numbers --- "
                     "the ladder caught this one on its first run",)),
    Artefact("F5 - the source decomposition in two frames, by rank", "R", "v1.2.0",
             module="functions.spectra.two_frame",
             objects=("build_environment", "coefficient_sets", "transfer_by_rank",
                      "cl_cross"),
             tests=("test_the_ranks_add_to_the_total_in_the_transfer_but_not_in_cl",),
             script="scripts/figure_f5_sources.py",
             note="drawn in ranks, which (89) produces and which is defined in "
                  "every frame, rather than the Newtonian three-way split of "
                  "7.1.1 --- the PI's call 2026-10-14. The frame disagreement is "
                  "its own panel: 42% at l=2, 7% at l=139, 14% at l=400"),
    Artefact("F2 - truncation convergence, both frames", "P", "v1.2.0",
             blocks=("F5 has landed; these follow it and wait on nothing else",)),
    Artefact("F7 - frame specialisation", "P", "v1.2.0",
             blocks=("F5 has landed; these follow it and wait on nothing else",)),
    Artefact("criterion 5b against CAMB and CLASS", "P", "v1.2.0",
             blocks=("reference data must be stamped under reference/ and not vendored",
                     "the tolerance is the two codes' mutual difference (S4b), "
                     "which has not been measured",
                     "the frame each code evolves in must be VERIFIED against its "
                     "own documentation, not assumed: the supplement's table is "
                     "recorded as stated. A quantity compared across two frames "
                     "is not the same quantity")),

    # ---- v1.5.0, gated --------------------------------------------------
    Artefact("the quartic contribution and the nonlinear couplings", "P", "v1.5.0",
             blocks=("gated on Paper 1 (S2)",
                     "the interface spec S24 is accepted but not frozen (S25)")),
    Artefact("bundle1-v1.5.0's factorised interface", "P", "v1.5.0",
             blocks=("S24 accepted as option (a); the contract is not yet code",)),
]

#: What each release is waiting on, beyond its own artefacts.
GATES: dict[str, tuple[str, ...]] = {
    "v1.1.0": ("none. Tagged at the last commit whose content was "
               "v1.1.0 --- NOT at the tip, which has moved on to "
               "v1.2.0 and would mislabel the tree",),
    "v1.2.0": ("criterion 5b, which needs CAMB and CLASS reference data",
               "the conventions sheet's lambda (C3.5), which F5 stands on",
               "the supplement's derivation section, written from "
               "GENERIC-SOURCE-DERIVATIVES-v1.md (S26)"),
    "v1.5.0": ("Paper 1 (S2)", "v1.2.0, because a correction can only be read "
               "where the thing it corrects is already right"),
}

RUNG_NAMES = {"P": "prototype", "C": "proof of concept",
              "R": "release candidate", "S": "shipped"}


def _run_all_scripts() -> set[str]:
    """The scripts `run_all.py` actually runs, read out of it rather than assumed."""
    text = (ROOT / "scripts" / "run_all.py").read_text(encoding="utf-8")
    return set(re.findall(r'"(scripts/[A-Za-z0-9_]+\.py)"', text))


def _test_names() -> set[str]:
    names: set[str] = set()
    for path in (ROOT / "tests").glob("test_*.py"):
        names |= set(re.findall(r"^def (test_[A-Za-z0-9_]+)",
                                path.read_text(encoding="utf-8"), re.M))
    return names


def verify(artefacts: list[Artefact]) -> list[str]:
    """Every claim that can be checked, checked. Returns the failures."""
    failures: list[str] = []
    wired, tests = _run_all_scripts(), _test_names()

    for art in artefacts:
        if art.module:
            try:
                module = importlib.import_module(art.module)
            except Exception as exc:                      # noqa: BLE001
                failures.append(f"{art.name}: {art.module} does not import ({exc})")
                module = None
            if module is not None:
                for obj in art.objects:
                    if not hasattr(module, obj):
                        failures.append(f"{art.name}: {art.module} has no {obj!r}")
        for test in art.tests:
            if test not in tests:
                failures.append(f"{art.name}: no test named {test!r}")
        if art.script and not (ROOT / art.script).exists():
            failures.append(f"{art.name}: {art.script} does not exist")
        # The rung's own condition: R and S mean the harness runs it.
        if art.rung in ("R", "S") and art.script and art.script not in wired:
            failures.append(
                f"{art.name}: claims rung {art.rung} but {art.script} is not in "
                "run_all.py --- that is the rung's definition, not a formality")
        # C means there is a check in tests/ that is not the artefact itself.
        if art.rung == "C" and not art.tests:
            failures.append(
                f"{art.name}: claims rung C with no test named. A proof of "
                "concept is a number checked against something it did not come "
                "from; without that it is a prototype")
    return failures


def render(artefacts: list[Artefact]) -> str:
    lines = [
        "# Release status — where every artefact is on the ladder",
        "",
        "**Generated by `scripts/make_release_status.py`. Do not edit by hand.**",
        "",
        "Decision **S27**'s four rungs. The rung is declared in the script and the",
        "evidence for it is verified there: a claim whose module, object, test or",
        "harness entry is missing fails the script instead of appearing here.",
        "",
        "| rung | means |",
        "|---|---|",
        "| **P** | prototype — it runs and produces a number; no claim attaches |",
        "| **C** | proof of concept — checked against something it did not come from, with a negative control, in `tests/` |",
        "| **R** | release candidate — in `run_all.py`, portable, manifested, claims generated rather than typed |",
        "| **S** | shipped — in a tagged release, hashed, cited |",
        "",
    ]
    for release in ("v1.0.0", "v1.1.0", "v1.2.0", "v1.5.0"):
        here = [a for a in artefacts if a.release == release]
        if not here:
            continue
        counts = {r: sum(1 for a in here if a.rung == r) for r in "PCRS"}
        tally = ", ".join(f"{counts[r]}×{r}" for r in "SRCP" if counts[r])
        lines += [f"## {release} — {tally}", ""]
        for gate in GATES.get(release, ()):
            lines.append(f"- **Gate:** {gate}")
        if GATES.get(release):
            lines.append("")
        lines += ["| | artefact | evidence |", "|---|---|---|"]
        for art in sorted(here, key=lambda a: "SRCP".index(a.rung)):
            evidence = []
            if art.module:
                evidence.append(f"`{art.module}`")
            if art.script:
                evidence.append(f"`{art.script}`")
            for test in art.tests:
                evidence.append(f"`{test}`")
            if art.note:
                evidence.append(art.note)
            for block in art.blocks:
                evidence.append(f"**blocked:** {block}")
            lines.append(f"| **{art.rung}** | {art.name} | "
                         + "; ".join(evidence) + " |")
        lines.append("")

    lines += [
        "## How to read this",
        "",
        "A release is ready when every artefact in its scope is at **R** and its",
        "gates are clear. That is a question the tree can answer; *is it done* is",
        "not, which is why S27 exists.",
        "",
        "**Demotion is normal.** Finding **T-24** moved the CDM-frame closure",
        "from C back to P and it re-entered at C with a different test — one that",
        "asserts the closure holds for *every* convention, so it can never again",
        "be cited as evidence for one. A ladder with no demotions on it is a",
        "ladder nobody is using.",
        "",
        "**Nothing sits at R with an unresolved convention beneath it.** That is",
        "the single rule that keeps F5 at P: the question it answers is measured",
        "and recorded, and the figure would assert a decomposition whose rank-two",
        "sign rests on a row of the conventions sheet that is still stipulated.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    failures = verify(ARTEFACTS)
    if failures:
        print(f"FAIL  {len(failures)} unsupported rung claim(s):")
        for f in failures:
            print(f"      {f}")
        print()
        print("      A rung is a measurement. Fix the evidence or lower the rung.")
        return 1

    out = ROOT / "provenance" / "RELEASE-STATUS-v1.md"
    out.write_text(render(ARTEFACTS), encoding="utf-8", newline="\n")
    counts = {r: sum(1 for a in ARTEFACTS if a.rung == r) for r in "SRCP"}
    print(f"wrote {out.relative_to(ROOT)}      "
          + ", ".join(f"{counts[r]} at {r} ({RUNG_NAMES[r]})" for r in "SRCP"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
