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
]

#: Diagnostics. A control is not evidence, so these are not released figures.
DIAGNOSTICS: list[tuple[str, str]] = [
    ("D0  criterion 5 ell range, and B-3", "scripts/derive_ell_range.py"),
    ("D1  relative-sign control", "scripts/diagnostic_d1_sign_control.py"),
    ("D2  round-trip residual (a number)", "scripts/diagnostic_d2_roundtrip.py"),
    ("D3  source terms against k", "scripts/diagnostic_d3_sources.py"),
    ("D4  no monopole in the CGI approach", "scripts/diagnostic_d4_monopole.py"),
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


#: The portability gate. It runs first and its failure is release-blocking:
#: nothing ships from this bundle that has only ever run where it was
#: written. Adopted from Coordination's audit, 2026-10-06.
GATE = ("portability", "scripts/check_portability.py")


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

    pending: dict[str, list[str]] = {"figures": [], "diagnostics": [], "emissions": []}
    label, script = GATE
    if run([sys.executable, script], label) != 0:
        print("\n" + "=" * 60)
        print("NOT RELEASABLE  --  portability gate failed")
        return 1

    for group, stages in (("figures", STAGES), ("diagnostics", DIAGNOSTICS),
                          ("emissions", EMISSIONS)):
        for label, script in stages:
            if not (ROOT / script).exists():
                pending[group].append(label)
                continue
            if run([sys.executable, script], label):
                failures.append(label)

    for group, stages in (("figures", STAGES), ("diagnostics", DIAGNOSTICS),
                          ("emissions", EMISSIONS)):
        print(f"\n--- {group} " + "-" * max(0, 56 - len(group)))
        if pending[group]:
            print(f"{len(pending[group])} of {len(stages)} pending:")
            for label in pending[group]:
                print(f"    PENDING  {label}")
        else:
            print(f"all {group} generated")

    print("\n--- tables " + "-" * 50)
    if run([sys.executable, "scripts/make_tables.py"], "audit tables"):
        failures.append("tables")
    if run([sys.executable, "scripts/make_figure_pages.py"], "figure pages"):
        failures.append("figure pages")

    print("\n--- provenance " + "-" * 46)
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
    outstanding = pending["figures"] + pending["diagnostics"]
    if outstanding and args.strict:
        print(f"NOT RELEASABLE — {len(outstanding)} pending; see RELEASE-NOTES-v1.0.0.md")
        return 1
    print("CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
