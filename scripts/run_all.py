#!/usr/bin/env python3
"""Reproduce the active outputs of this bundle.

    python scripts/run_all.py --strict     # release route: fail on any drift
    python scripts/run_all.py --rerun      # development route: regenerate freely

`--strict` regenerates every output, figure and table, then verifies the SHA-256
manifests and the generated conventions copy, and fails if anything differs from
what was recorded. It is the route a release candidate must pass.

`--rerun` does the same work without the drift gate, and rewrites the manifests
afterwards.

**Pre-release.** The reconstruction stages are registered below and are reported
as pending until they exist. The harness is deliberately complete before the
physics, so that the first figure generated is already under manifest and already
has a caption that names its script.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Released figures, in build order: the recursion first, then convergence, then
#: everything that depends on a trusted solution. (label, path from the root).
#: Pending entries are reported, not skipped silently — a missing stage must be
#: visible. The specification for the set is captions/FIGURE-PLAN-v1.0.0.md.
STAGES: list[tuple[str, str]] = [
    ("F1  Appendix F match", "scripts/figure_f1_appendix_f.py"),
    ("F2  truncation convergence, both frames", "scripts/figure_f2_truncation.py"),
    ("F3  angular power spectrum, both routes", "scripts/figure_f3_angular_spectrum.py"),
    ("F4  real-space angular correlation", "scripts/figure_f4_correlation.py"),
    ("F5  source decomposition, two frames", "scripts/figure_f5_sources.py"),
    ("F6  impact of the approximations", "scripts/figure_f6_approximations.py"),
    ("F7  frame specialisation", "scripts/figure_f7_frames.py"),
    ("F8  coupling schematic", "scripts/figure_f8_schematic.py"),
    # **F9 is split, and the split is the point.** The computation is 45 minutes
    # --- 1433 modes in two frames --- and lands in outputs/f9-acoustic-spectrum.csv,
    # which is committed. The harness redraws the figure from that CSV in
    # seconds, so it verifies that the recorded data still produces the shipped
    # picture without re-deriving it. The same architecture the PI set for the
    # CAMB and CLASS comparison: recorded in the bundle, reproducible on
    # demand, not run by default.
    ("F9  angular spectrum with the acoustic peaks",
     "scripts/figure_f9_acoustic_spectrum.py --replot"),
]

#: Deferred to v1.1.0. A control is not evidence, so the diagnostics here are
#: not released figures; **scoped out of v1.0.0 by decision S45** (carried as `S-b` until T-87), accepted by
#: the PI 2026-10-09. A deferred artefact is still reported as pending, so it
#: cannot be forgotten; it just does not block the release it was deferred out
#: of.
#:
#: **F5 is the one entry here that S45 did not put here** — it is marked
#: *acceptance* in the figure plan, as F3 and F4 are, and acceptance figures
#: were what S45 kept. It moves by **decision S20**, and the reason is worth
#: carrying at the call site rather than only in the record: F5 and F7 are one
#: piece of machinery. Both need the frame specialisation made numerical, and
#: `"newtonian"` and `"cdm"` are today labels on `PerturbationHistory` that
#: nothing reads. What F5 would show numerically — that the decomposition is
#: frame-dependent while the total is not — **criterion 2 already establishes
#: symbolically**, as an exact identity in $\varepsilon$ rather than to a
#: tolerance: see `functions.frames.roundtrip_residual`. Deferring F5 therefore
#: removes a picture of the claim and not the claim, and `README.md` and the
#: release notes say so in those words.
#: Where each deferred artefact actually lands, and on whose decision. **A
#: single frozenset was wrong once S21 and S23 split the destinations**: the
#: harness went on printing "deferred to v1.1.0" for F2, F5 and F7 after they
#: had been moved to v1.2.0, which is the same class of staleness as a status
#: block nobody updates. The version is data now, so the message cannot drift
#: from the decision.
DEFERRED: dict[str, tuple[str, str]] = {
    # S45 (carried as `S-b` until T-87): diagnostic and cross-check
    # artefacts, not acceptance ones.
    # F6 and F8 were here and landed in v1.1.0; they are removed rather
    # than left with a stale version, which is T-16's lesson about labels.
    # **RETARGETED to v1.5.0, 2026-10-15 --- finding T-47.** Both were deferred
    # *to v1.1.0*, and v1.1.0 was tagged on 2026-10-12 without them, so for
    # three days the harness printed a deferral to a release that had already
    # happened. The dict below made the message *accurate*; nothing made it
    # *current*. `_released_versions` now closes that, which is the difference
    # between fixing an instance and closing a class.
    #
    # **D4 was here and is DISCHARGED**, written 2026-10-17. It had been
    # deferred three times --- to v1.1.0, then to v1.5.0 under T-47 --- on the
    # reasoning that the antecedent's "there is no monopole temperature
    # anisotropy in the CGI approach" is a one-line claim with little room for
    # error. **The deferral is what cost us eleven days.** D4 measures which
    # rank carries C_l, and under the weight every released caller was silently
    # taking, the rank-0 monopole sector was 0.002% of the spectrum and the
    # rank-1 dipole was 100.5% of it. Finding **T-57** is what D4 would have
    # reported the first time it ran.
    #
    # The lesson is not "defer less". It is that a diagnostic deferred because
    # its STATED question looks safe can be the only instrument pointed at a
    # different question entirely, and nothing in the deferral records what
    # else it would have measured.
    "D3  source terms against k": ("v1.5.0", "S45"),   # S-b, renumbered T-87/S45
    # **T-51 was here and is DISCHARGED**, fixed 2026-10-16 within hours
    # of being registered. It is removed rather than left with a stale
    # target --- which is the same rule F6 and F8 were removed under, and
    # the one T-47 exists to enforce. The mechanism worked: a defect
    # promised to a release was carried as data, and `check_deferrals`
    # would have refused v1.3.0 had it not been done.
    # S21 then S23 deferred F2, F5 and F7, twice for reasons that turned out
    # wrong. **All three landed 2026-10-14** and are removed rather than left
    # with a stale deferral, as F6 and F8 were. What actually blocked F5 was the
    # rank-two sign, settled as **B-13**, and the decomposition it is drawn in
    # --- ranks, not the Newtonian three-way split of 7.1.1 --- which was the
    # PI's call the same day. F2 and F7 followed it.
}

DEFERRED_TO_V1_1 = frozenset(DEFERRED)

DIAGNOSTICS: list[tuple[str, str]] = [
    ("D0  criterion 5 ell range, and B-3", "scripts/derive_ell_range.py"),
    ("D1  relative-sign control", "scripts/diagnostic_d1_sign_control.py"),
    ("D2  round-trip residual (a number)", "scripts/diagnostic_d2_roundtrip.py"),
    ("D3  source terms against k", "scripts/diagnostic_d3_sources.py"),
    ("D4  no monopole in the CGI approach", "scripts/diagnostic_d4_monopole.py"),
    ("D5  criterion 5a: the Sachs-Wolfe limit", "scripts/diagnostic_d5_sachs_wolfe.py"),
    # D6 writes provenance/FRAME-INVARIANCE-MEASUREMENT-v1.md, whose prose is
    # computed from its own table. It runs here so the record cannot fall out
    # of step with the code -- the same reason EMISSIONS exists.
    ("D6  (102) in two frames: the F5 measurement", "scripts/measure_frame_invariance.py"),
    # D7 measures how far the CDM frame is from the **total-energy** frame it
    # was identified with. Finding T-29; the amendment is S8a. Both halves of
    # this label said "CDM" until 2026-10-14 -- blanket-rename damage, the same
    # class as the one that inverted D7's own subject line. Finding T-33.
    ("D7  the CDM frame against the total-energy frame",
     "scripts/diagnostic_d7_frame_identification.py"),
    # D8 is **criterion 5b's gate**, decision S4c. It is in the harness and the
    # CAMB/CLASS comparison is not, and that is the whole point of moving the
    # tolerance onto the bundle's own pipeline: a gate that needs two external
    # codes and fifteen minutes cannot run on every release route, and one that
    # compares (102) with (177)-(179) over three backgrounds runs in half a
    # minute. scripts/compare_criterion_5b.py stays out, deliberately, and
    # reports the external context on demand.
    ("D8  criterion 5b's gate: (102) against (177)-(179)",
     "scripts/diagnostic_d8_criterion_5b_gate.py"),
    # D9 is the check **the antecedent prints and this bundle never ran**:
    # l_j = |r_theta/r_s| j pi, with both sides computable here and no external
    # code needed. It disagrees by a factor of 2.0--2.8 --- finding T-51 ---
    # and it reports rather than fails, because the fix is v1.3.0's and the
    # deferral above is what refuses to let it be forgotten. **A diagnostic
    # that fails every development run is a diagnostic people stop reading.**
    ("D9  the acoustic scale against the paper's own formula",
     "scripts/diagnostic_d9_acoustic_scale.py"),
    # **D10 scopes A-3 and deliberately does not measure it.** The released
    # driving freezes Phi below the recombination grid's first point, while
    # every mode has started far earlier since T-51, so the oscillator crosses
    # the radiation era on a potential that does not decay. D10 reports which
    # modes have a radiation era to see and how much Phi the frozen form omits
    # --- 0.13% at k=10 and 105% at k=600 on PLANCK_MODEL --- and stops there,
    # because the acoustic grid carries 3 to 26 points below equality and a
    # splice on three points is a step in Phi-prime, not physics. Finding T-64.
    ("D10 what A-3 costs: the potential that does not decay",
     "scripts/diagnostic_d10_radiation_driving.py"),
    # **D11, D12 and D13 are the frame-gap localisation**, and they were
    # outside the harness until **T-87** found that their `diagnostics/` files
    # had no generator -- they printed to stdout and the committed artefacts
    # were hand-captured console redirects, hashed into two manifests as if
    # they regenerated. Each now writes its own file and each runs here, which
    # is the only thing that makes a number in `BUNDLE-DEFECTS-v1.md` checkable
    # by re-running rather than by trusting a transcription. That is the whole
    # argument of **M5a**, applied to this bundle's own evidence.
    ("D11 the two driving terms of the l=0 equation",
     "scripts/diagnostic_d11_monopole_driving.py"),
    ("D12 v_B + sigma differenced between the frames, before projection",
     "scripts/diagnostic_d12_vb_plus_sigma.py"),
    ("D13 the by-parts identity, direct against by-parts, in both frames",
     "scripts/diagnostic_d13_byparts_2x2.py"),
    # D14 measures the B-slot repair over its full 2^4 control lattice, which
    # is M11a as a method rather than a maxim: T-77 is the instance where two
    # defects that fix the gap only together scored as two failed fixes one at
    # a time. Three of D14's four controls score as failures alone.
    ("D14 the B-slot repair, over the control lattice",
     "scripts/diagnostic_d14_slot_repair.py"),
    # **D16 is the column M11b demands, for the term that dominates (102).**
    # It measures and changes nothing: one term is 93-97% of the Newtonian
    # integrand and 1.8e5 times the physical Doppler source it stands for, and
    # the share is WEIGHT-INDEPENDENT, so A-2 cannot reach it. Finding T-94.
    # D15 is the diagnostic F9 under the withdrawn T-88 variant and is not a
    # harness entry: it is a 45-minute run and `figure_f9 --b-slot-repair`
    # produces it on demand.
    ("D16 the kappa-squared in (102)'s integrand",
     "scripts/diagnostic_d16_kappa_squared.py"),
    # D17 evaluates P1-T's boxed integrating-factor form of the line-of-sight
    # solution beside the released (102), in both frames. It is the discriminator
    # for where the frame gap enters: a W-form that is frame-invariant where
    # (102) is not puts the gap in the assembly, and a W-form that carries it too
    # says the assembly is not the site. It reads O(1) in both columns and is
    # held INCONCLUSIVE --- the rank-0 row needs sigma_0 and the CDM column needs
    # S_2, both referred to P1-T. It is registered so that an instrument in the
    # tree cannot drift away from the harness that is supposed to run it.
    ("D17 P1-T's W-form against the released (102)",
     "scripts/diagnostic_d17_w_form.py"),
    # D18 is P1-T's section 6 item 1: their kappa' ledger applied to the
    # arrays this bundle actually builds, rather than to c7's fixtures. The
    # split of each coefficient into its kappa'-free and kappa'-carrying parts
    # is EXACT -- every coefficient is affine in kappa' -- and the diagnostic
    # verifies that affineness at lambda=2 before reporting, so a construction
    # that stopped being affine would void the split rather than be reported
    # wrongly. Finding T-101.
    ("D18 the kappa' ledger against the released assembly",
     "scripts/diagnostic_d18_released_kappa_ledger.py"),
    # D19 is the acceptance measurement for the ell=0 row control. It is kept
    # after T-107 REFUTED the correction it measures, for D14's reason: a
    # withdrawn variant that cannot be regenerated cannot be checked. Its four
    # conditions all PASS and the repair is still wrong -- which is M14, and
    # the reason it is in the harness rather than in a notebook.
    ("D19 the ell=0 row control, measured on the live coefficients",
     "scripts/diagnostic_d19_monopole_row.py"),
]


#: Handover emissions. These are not figures and not diagnostics: they are
#: quantities another stream's floats need, which this bundle computes anyway
#: and would otherwise discard. They run with everything else so that the CSVs
#: in outputs/ cannot fall out of step with the code that made them --- the
#: emissions module existed for a day before this step did, and nothing was
#: produced in that time.
EMISSIONS: list[tuple[str, str]] = [
    ("handover fields: lensing kernel, line-of-sight ray", "scripts/emit_handover_fields.py"),
]


#: The gates. They run first and their failure is release-blocking: nothing
#: ships from this bundle that has only ever run where it was written, and
#: nothing ships that the bundle itself cannot read or regenerate. Portability
#: was adopted from Coordination's audit, 2026-10-06; release hygiene after
#: finding **T-50**, where three files the bundle could not read or rebuild
#: passed every gate in it and entered the released archive.
GATES = [
    ("portability", "scripts/check_portability.py"),
    ("release hygiene", "scripts/check_release_hygiene.py"),
]



def _released_versions() -> set[str]:
    """Versions with a dated `CHANGELOG.md` entry --- that is, already shipped.

    `## [1.1.0] - 2026-10-12` is released; `## [Unreleased] - v1.0.0 in
    preparation` is not.
    """
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    return {f"v{m}" for m in re.findall(r"^## \[(\d+\.\d+\.\d+)\] — \d", text, re.M)}


def check_deferrals() -> list[str]:
    """**A deferral to a release that has already happened is a stale label.**

    Finding **T-16** is stale labels; the `DEFERRED` dict above exists because
    of it, and stores the version as data so the message cannot contradict the
    decision. That made the message accurate and left it able to go out of
    date: D3 and D4 were deferred *to v1.1.0*, v1.1.0 shipped without them, and
    the harness went on announcing a deferral to a release in the past ---
    finding **T-47**, caught by Coordination rather than by a gate.

    This is the gate. It is cheap, it is arithmetic, and it is the difference
    between fixing the instance and closing the class.
    """
    released = _released_versions()
    return [f"{label!r} is deferred to {version}, which is already released. "
            "Retarget it or do it."
            for label, (version, _) in DEFERRED.items() if version in released]


def run(cmd: list[str], label: str) -> int:
    print(f"\n--- {label} " + "-" * max(0, 60 - len(label)))
    return subprocess.call(cmd, cwd=ROOT)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--strict", action="store_true", help="release route, fail on drift")
    mode.add_argument("--rerun", action="store_true", help="development route")
    args = ap.parse_args()

    failures: list[str] = []

    stale = check_deferrals()
    if stale:
        print("\n--- deferrals " + "-" * 47)
        for line in stale:
            print(f"    STALE  {line}")
        failures.append("stale deferrals")

    pending: dict[str, list[str]] = {"figures": [], "diagnostics": [], "emissions": []}
    # **The portability gate stops `--strict` and only reports in `--rerun`**
    # --- finding T-10. It used to abort both. `--rerun` is the route whose job
    # is to regenerate, so aborting it meant that any new, not-yet-committed
    # file blocked the very operation that would have brought the tree back
    # into agreement: regenerate to fix the manifests, but you cannot
    # regenerate until the manifests are fixed. That is T-4's mistake again in
    # a different place --- a gate ordered so that it blocks its own remedy.
    for label, script in GATES:
        if run([sys.executable, script], label) == 0:
            continue
        if args.strict:
            print("\n" + "=" * 60)
            print(f"NOT RELEASABLE  --  {label} gate failed")
            return 1
        failures.append(label)
        print("\n      --rerun CONTINUES past this. The gate is advisory on the")
        print("      development route and binding on the release route, because")
        print("      regenerating is how most of these get fixed.")

    for group, stages in (("figures", STAGES), ("diagnostics", DIAGNOSTICS),
                          ("emissions", EMISSIONS)):
        for label, script in stages:
            # `split()[0]`: a stage may carry arguments (F9 is wired as
            # `... --replot`), and the file that must exist is the script,
            # not the command line. Without this F9 reported PENDING while
            # sitting in the tree --- a gate lying in the safe direction.
            if not (ROOT / script.split()[0]).exists():
                pending[group].append(label)
                continue
            if run([sys.executable, *script.split()], label):
                failures.append(label)

    for group, stages in (("figures", STAGES), ("diagnostics", DIAGNOSTICS),
                          ("emissions", EMISSIONS)):
        print(f"\n--- {group} " + "-" * max(0, 56 - len(group)))
        blocking = [l for l in pending[group] if l not in DEFERRED_TO_V1_1]
        deferred = [l for l in pending[group] if l in DEFERRED_TO_V1_1]
        if blocking:
            print(f"{len(blocking)} of {len(stages)} pending for THIS release:")
            for label in blocking:
                print(f"    PENDING  {label}")
        else:
            print(f"all {group} this release needs are generated")
        for label in deferred:
            version, decision = DEFERRED[label]
            print(f"    deferred to {version} ({decision})  {label}")

    print("\n--- tables " + "-" * 50)
    if run([sys.executable, "scripts/make_tables.py"], "audit tables"):
        failures.append("tables")
    if run([sys.executable, "scripts/make_figure_pages.py"], "figure pages"):
        failures.append("figure pages")

    # R3. The supplement is the document this bundle is *for*, and it was the
    # one released artefact nothing here generated. Built and gated now, which
    # also retires the hand-typed rename on the way out. Skips cleanly without
    # a LaTeX toolchain.
    if run([sys.executable, "scripts/build_supplement.py"], "supplement"):
        failures.append("supplement")

    print("\n--- provenance " + "-" * 46)
    # The release status is **generated and verified**, not typed: every rung it
    # claims names a module, an object, a test or a harness entry, and the script
    # fails if one is missing. It caught five of its own claims on its first run.
    # Decision S27.
    if run([sys.executable, "scripts/make_release_status.py"], "release status"):
        failures.append("release status")
    # The grid register. It costs a tenth of a second and it is the gate that
    # closes T-3's class rather than its third instance --- see T-47's note
    # above on the difference, which this bundle has now paid for twice.
    if run([sys.executable, "scripts/make_grid_register.py"], "grid register"):
        failures.append("grid register")
    if run([sys.executable, "scripts/sync_conventions.py", "--check"], "conventions copy"):
        failures.append("conventions copy")

    print("\n--- manifests " + "-" * 47)
    if args.strict:
        if run([sys.executable, "scripts/make_manifests.py", "--check"], "manifest check"):
            failures.append("manifests")
    else:
        run([sys.executable, "scripts/make_manifests.py"], "manifest rewrite")

    # **The regression suite runs LAST, after everything it could be testing has
    # been regenerated** --- finding T-4. It used to run first, which meant that
    # on `--rerun` it tested the *previous* run's artefacts: after any change to
    # the file set it reported `NOT CLEAN -- tests` against a stale manifest that
    # the very same run then rewrote correctly. A gate that fails while the tree
    # is fine is worse than no gate, because the next failure gets dismissed too.
    if run([sys.executable, "-m", "pytest", "-q"], "regression suite"):
        failures.append("tests")

    print("\n" + "=" * 60)
    if failures:
        print("NOT CLEAN — " + ", ".join(failures))
        return 1
    outstanding = [l for l in pending["figures"] + pending["diagnostics"]
                   if l not in DEFERRED_TO_V1_1]
    if outstanding and args.strict:
        print(f"NOT RELEASABLE — {len(outstanding)} pending; see RELEASE-NOTES-v1.0.0.md")
        return 1
    print("CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
