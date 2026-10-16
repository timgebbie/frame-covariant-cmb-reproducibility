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
    Artefact("the covariant coefficients C_0, C_1, C_2 from (89)", "S", "v1.2.0",
             module="functions.spectra.coefficients",
             objects=("match_coefficients", "newtonian_coefficients", "newtonian_set"),
             tests=("test_all_three_of_90_are_reproduced_by_the_match",
                    "test_b11_is_a_sign_in_89_not_in_90",
                    "test_the_newtonian_specialisation_is_equation_109"),
             note="(89) is implemented as the definition so (90) is a check; "
                  "B-11's delta_l0 sign resolved"),
    Artefact("the integral solution (102), carried with a generic u^a", "S", "v1.2.0",
             module="functions.spectra.integral_solution",
             objects=("integral_solution", "required_multipoles"),
             tests=("test_the_shear_boundary_term_is_empty_in_the_newtonian_frame",
                    "test_the_shear_boundary_term_is_not_empty_once_b2_is",
                    "test_the_specialisation_recovers_what_the_pipeline_computes")),
    Artefact("the generic source derivatives Annals II never wrote", "S", "v1.2.0",
             module="functions.spectra.coefficients",
             objects=("generic_shear_derivatives", "c2_derivatives"),
             tests=("test_the_rank_two_control_passes_symbolically",
                    "test_no_numerical_derivative_survives_in_the_c2_chain"),
             note="rank 2 closed from Appendix G with a control; rank 1 assembled "
                  "from printed equations and still carrying (*)"),
    Artefact("the CDM frame as a second frame", "S", "v1.2.0",
             module="functions.spectra.coefficients",
             objects=("cdm_frame_shear", "cdm_set", "background_fluid"),
             tests=("test_the_frame_shift_of_every_coefficient_is_the_closed_form_one",
                    "test_B13_the_printed_n_t1_does_not_close_and_the_general_rule_does",
                    "test_T24_the_closure_is_an_identity_in_both_conventions")),
    Artefact("the frame-invariance measurement, F5's question", "S", "v1.2.0",
             module="functions.spectra.coefficients",
             script="scripts/measure_frame_invariance.py",
             note="generated record; its prose is computed from its own table"),
    Artefact("the ell ceiling removed, 507 -> 2000", "S", "v1.2.0",
             module="functions.spectra.bessel_table",
             objects=("BesselTable",),
             tests=("test_unavailable_ell_is_refused",
                    "test_the_coefficients_are_exact_rationals_not_floats"),
             note="findings T-17 and T-18"),
    Artefact("D9 - the acoustic scale against the antecedent's own formula",
             "R", "v1.3.0",
             module="functions.spectra.acoustic",
             objects=("sound_speed_squared", "sound_horizon"),
             script="scripts/diagnostic_d9_acoustic_scale.py",
             tests=("test_the_peak_spacing_disagrees_with_the_antecedents_own_formula",
                    "test_the_initial_condition_is_imposed_rather_than_adiabatic"),
             note="**Annals II prints this check and the bundle never ran it**: "
                  "l_j = |r_theta/r_s| j pi, with both sides computable here "
                  "and no external code needed. It disagrees by a factor of "
                  "2.0-2.8 --- finding T-51, which is Q8's answer. R rather "
                  "than S because the number it reports is a DEFECT: the "
                  "instrument is sound and what it measures is not yet fixed. "
                  "Its tests assert the broken value and are written to FAIL "
                  "when T-51 is repaired, so the record cannot go out of date "
                  "quietly --- S33 clause (d) applied to a second finding"),
    Artefact("the stamped Planck 2018 set, wired as PLANCK_MODEL", "S", "v1.2.0",
             module="functions.background.flrw",
             objects=("PLANCK_MODEL", "OMEGA_GAMMA_H2"),
             script="scripts/diagnostic_d8_criterion_5b_gate.py",
             tests=("test_the_damping_uses_dif_damp_correct_and_f2_reaches_all_three_coefficients",
                    "test_the_two_routes_agree_on_every_background_the_bundle_ships"),
             note="provenance/COSMOLOGICAL-PARAMETERS-v1.md; the paper's own "
                  "stated baseline column, not one chosen here. A model "
                  "constant with a photon-only radiation era, Omega_gamma h^2 "
                  "DERIVED from T_CMB and the physical constants rather than "
                  "quoted: it reaches z_eq = 5756.0 against CAMB's 5756.0 and "
                  "CLASS's 5756.0 by an independent route. CDM_MODEL and "
                  "LCDM_MODEL untouched --- finding T-37. PROMOTED C -> R "
                  "2026-10-15: its blocker was that nothing of this bundle's "
                  "own exercised it, and D8 now does, on every harness run, as "
                  "one of the three backgrounds criterion 5b's gate sweeps"),
    Artefact("F5 - the source decomposition in two frames, by rank", "S", "v1.2.0",
             module="functions.spectra.two_frame",
             objects=("build_environment", "coefficient_sets", "transfer_by_rank",
                      "cl_cross"),
             tests=("test_the_ranks_add_to_the_total_in_the_transfer_but_not_in_cl",),
             script="scripts/figure_f5_sources.py",
             note="drawn in ranks, which (89) produces and which is defined in "
                  "every frame, rather than the Newtonian three-way split of "
                  "7.1.1 --- the PI's call 2026-10-14. The frame disagreement is "
                  "its own panel: 47% at l=2, 7% at l=102, 13% at l=405, median 15% "
                  "over 2 <= l <= 400 --- the post-T-37 numbers, moved from "
                  "42 / 7 / 11 by wiring the transfer function"),
    Artefact("F2 - truncation convergence, both frames", "S", "v1.2.0",
             module="functions.spectra.two_frame",
             objects=("build_environment", "coefficient_sets", "transfer_by_rank"),
             tests=("test_the_newtonian_frame_leaves_the_shear_sectors_empty_"
                    "and_the_cdm_frame_does_not",),
             script="scripts/figure_f2_truncation.py",
             note="Appendix E made quantitative in both frames. What a "
                  "truncation discards falls off a per-k cliff at l ~ k dEta; "
                  "what it destroys has no l_max in it at all, is flat at "
                  "0.54-0.68% to l~20 and rises to 32% by l=600 (0.8-0.9% and 29% "
                  "before T-37 wired the transfer function). Footnote 29 "
                  "p.365 checked and upheld: identically zero in the Newtonian "
                  "frame, which has no shear to lose. Its k grid runs to 1900 "
                  "rather than 420 --- finding T-32"),
    Artefact("F7 - frame specialisation", "S", "v1.2.0",
             module="functions.spectra.two_frame",
             objects=("build_environment", "coefficient_sets"),
             tests=("test_102_cannot_make_its_frame_response_depend_on_the_multipole",),
             script="scripts/figure_f7_frames.py",
             note="reports that its own planned claim is false: the dipole was "
                  "to stand an order of magnitude apart and lands on each curve "
                  "instead, worst ratio 1.25x, because (102) builds every l from "
                  "the same three C_A --- finding T-31. Its environment is built "
                  "for the k grid rather than the probe modes --- finding T-34"),
    Artefact("F9 - the angular spectrum with the acoustic peaks, both frames",
             "S", "v1.2.0",
             module="functions.spectra.two_frame",
             objects=("build_environment", "coefficient_sets", "transfer_by_rank"),
             script="scripts/figure_f9_acoustic_spectrum.py",
             tests=("test_the_two_routes_agree_on_every_background_the_bundle_ships",),
             note="**the release's deliverable** (S1): D_l renormalised at "
                  "l=30 for CDM, LCDM and PLANCK_MODEL, with the peaks and the "
                  "damping tail, and the same spectra in BOTH frames from one "
                  "solve. First peak l~162 by parabolic interpolation against "
                  "CAMB's 206 -- interpolated because the ell grid steps by 30 "
                  "and reading the peak off it would assert a precision the "
                  "sampling does not have. CAMB and CLASS drawn as context, "
                  "never as a target (S4c). The computation is 45 minutes and "
                  "its output CSV is committed; run_all redraws from that CSV "
                  "in seconds, which is the architecture the PI set for the "
                  "external comparison applied to a figure"),
    Artefact("criterion 5b's gate: (102) against (177)-(179)", "S", "v1.2.0",
             module="functions.spectra.two_route",
             objects=("TwoRoute", "two_route_transfer"),
             script="scripts/diagnostic_d8_criterion_5b_gate.py",
             tests=("test_the_specialisation_recovers_the_pipeline_at_every_k_not_only_at_sixty",
                    "test_the_two_routes_agree_on_every_background_the_bundle_ships",
                    "test_a_gate_that_cannot_fail_is_not_a_gate"),
             note="decision S4c, the PI's ruling 2026-10-15. Annals II writes "
                  "its integral solution twice and recovers the second from the "
                  "first symbolically; nothing evaluates both and compares "
                  "them. This does, over CDM, LCDM and PLANCK_MODEL, nine "
                  "modes 0.3 <= k <= 600 and 2 <= l <= 600. Worst 9.5e-06, "
                  "median 2.7e-08, gate 1e-03 --- a hundredfold margin, sized "
                  "to catch an algebra defect (T-41's plateau was a factor of "
                  "eighty) rather than to certify the number it returns. "
                  "Stated at the transfer level at fixed k with the same "
                  "weight on both sides, because at C_l the branches differ by "
                  "A-1 and A-2 legitimately. Findings T-44, T-45 and T-46 are "
                  "what it cost to make the measurement real",
             blocks=()),
    Artefact("criterion 5b's context: this bundle against CAMB and CLASS",
             "C", "v1.2.0",
             script="scripts/make_reference_spectra.py",
             tests=("test_camb_and_class_agree_with_each_other_and_that_sets_the_floor",
                    "test_criterion_5b_is_not_quietly_skipped"),
             note="CAMB 2.0.5 and CLASS v3.4.1 specialised to N_eff=0, no "
                  "reionisation, no lensing, helium explicit; both report "
                  "z_eq=5756.0 and a first peak at l=206, which PLANCK_MODEL "
                  "reaches independently by deriving Omega_gamma h^2 from "
                  "T_CMB. Mutual difference measured per band -- 0.125% / "
                  "0.370% / 0.223%. Stamped in "
                  "reference/REFERENCE-STAMP-v1.2.0.md. Measured against this "
                  "bundle: 97.8% in the plateau, 137% across the peaks, "
                  "itemised by approximation in provenance/CRITERION-5B-v1.md",
             blocks=("stays at C and that is the right rung, not an unfinished "
                     "one. Under S4c this is CONTEXT and not an acceptance "
                     "gate: the gate is the artefact above. R means run_all "
                     "runs it, and scripts/compare_criterion_5b.py takes ~15 "
                     "minutes and needs camb and classy installed, so it is "
                     "deliberately out of the harness and runs on demand "
                     "against the stamped reference/ CSVs",)),


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
    "v1.2.0": ("none. Criterion 5b closed 2026-10-15 under decision S4c: "
               "gated on (102) against (177)-(179) at 9.5e-06 against 1e-03, "
               "with CAMB and CLASS reported alongside as context",),
    "v1.5.0": ("Paper 1 (S2)", "v1.2.0, because a correction can only be read "
               "where the thing it corrects is already right"),
}

#: **The R -> S promotion is part of the release act, not a follow-up.**
#: S27 defines S as "in a tagged release, hashed, cited", so the release
#: commit declares it and the tag points at that commit. Leaving it until
#: after the tag puts the tagged tree one rung below the release it is.
#: `tests/test_readme_artefacts.py` catches the gap: a README saying
#: "Released as vX" while the status still reads R fails, which is how
#: this step was found missing from the v1.2.0 sequence.
RUNG_NAMES = {"P": "prototype", "C": "proof of concept",
              "R": "release candidate", "S": "shipped"}


def _run_all_scripts() -> set[str]:
    """The scripts `run_all.py` actually runs, read out of it rather than assumed."""
    text = (ROOT / "scripts" / "run_all.py").read_text(encoding="utf-8")
    # `[^"]*` because a stage may carry arguments --- F9 is wired as
    # `... --replot`, its expensive half deliberately outside the harness. The
    # pattern used to require the closing quote immediately after `.py`, which
    # silently reported a wired script as unwired and so **failed a rung for a
    # punctuation reason**. A gate that fails on syntax rather than substance
    # teaches people to dismiss it.
    return set(re.findall(r'"(scripts/[A-Za-z0-9_]+\.py)[^"]*"', text))


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
        "**Nothing sits at R with an unresolved convention beneath it.** The rule",
        "was broken for a day and the tree said so: F2, F5 and F7 reached R while",
        "C3.5 still read *stipulated*, and `RELEASE-STATUS` declared both at once",
        "--- finding **T-40**. It is closed now, and closed in two halves because",
        "C3.5 had been two questions under one name. **\\lambda**, the",
        "rank-dependent rescaling, is fixed by physics: cold dark matter falls",
        "into a potential well, so gravity does positive work on it, and that",
        "relative sign between a rank-0 potential and a rank-1 velocity cannot",
        "cancel. **s_Q**, the sign of a scalar's own mode coefficient, is fixed",
        "by nothing --- it carries one factor in the scalar, its gradient and its",
        "second gradient alike, so it cancels from every ratio. Stipulating it is",
        "correct and the sheet's *not fixed by any source* was right all along.",
        "Both halves are asserted in `tests/test_frames.py`, the first with a",
        "control that climbs out of the well.",
        "",
        "**The normative sheet still says *stipulated*, and this bundle cannot",
        "change it.** `provenance/conventions.md` is generated by",
        "`scripts/sync_conventions.py` from the project's sheet, which lives",
        "outside this repository; hand-editing the copy is the drift that script",
        "exists to prevent. The replacement wording is the PI's to apply at the",
        "source, and until it is, the copy here will keep reading *stipulated*",
        "while the tests say otherwise. That gap is visible rather than silent,",
        "which is the most this bundle can do about a file it does not own.",
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
