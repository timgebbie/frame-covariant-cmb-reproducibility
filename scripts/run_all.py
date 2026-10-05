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

#: (label, module path relative to the repository root). Pending entries are
#: reported, not skipped silently — a missing stage must be visible.
STAGES: list[tuple[str, str]] = [
    ("C2  recursion against the external hierarchies", "scripts/figure_c2_recursion.py"),
    ("C3  known-wrong control", "scripts/figure_c3_control.py"),
    ("C4  convergence against ell_max", "scripts/figure_c4_convergence.py"),
    ("C5  round-trip residual", "scripts/figure_c5_roundtrip.py"),
    ("C6  coupling-structure schematic", "scripts/figure_c6_schematic.py"),
    ("C1  recovered spectrum with residual panel", "scripts/figure_c1_spectrum.py"),
]


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

    if run([sys.executable, "-m", "pytest", "-q"], "regression suite"):
        failures.append("tests")

    pending = []
    for label, script in STAGES:
        if not (ROOT / script).exists():
            pending.append(label)
            continue
        if run([sys.executable, script], label):
            failures.append(label)

    print("\n--- outputs " + "-" * 49)
    if pending:
        print(f"{len(pending)} of {len(STAGES)} stages pending:")
        for label in pending:
            print(f"    PENDING  {label}")
    else:
        print("all stages generated")

    print("\n--- provenance " + "-" * 46)
    if run([sys.executable, "scripts/sync_conventions.py", "--check"], "conventions copy"):
        failures.append("conventions copy")

    print("\n--- manifests " + "-" * 47)
    if args.strict:
        if run([sys.executable, "scripts/make_manifests.py", "--check"], "manifest check"):
            failures.append("manifests")
    else:
        run([sys.executable, "scripts/make_manifests.py"], "manifest rewrite")

    print("\n" + "=" * 60)
    if failures:
        print("NOT CLEAN — " + ", ".join(failures))
        return 1
    if pending and args.strict:
        print("NOT RELEASABLE — stages pending; see RELEASE-NOTES-v1.0.0.md")
        return 1
    print("CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
