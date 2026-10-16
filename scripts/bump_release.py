#!/usr/bin/env python3
r"""Flip every version label at once, from one source of truth.

    python scripts/bump_release.py --to 1.2.0 --dry-run
    python scripts/bump_release.py --to 1.2.0

**Why this exists.** `tests/test_readme_artefacts.py` already checks that the
version labels agree, and its docstring records why: *"a label flipped by hand
is a label that drifts"*, after the README header read `v1.1.0` while its own
verification section read `v1.2.0-dev` and the supplement's `\date` still read
`v1.0.0` two releases later. The test catches the drift. It does not prevent it,
because the flip was still six hand edits in four files.

This is the flip, done once, from one argument. The test then checks the result
rather than catching a mistake nobody had a tool to avoid.

**What it touches, and nothing else.** The six label sites, plus `CITATION.cff`
and the changelog heading. It does **not** rename a file: the house convention
is that a version suffix marks the release an artefact was *introduced* in, so
`SUPPLEMENTARY-MATERIAL-v1.0.0.tex` keeps its name while its content moves ---
and `provenance/BUNDLE-DEFECTS-v1.md` is append-only and refers to that name, so
a rename would strand a reference in a file nothing may rewrite.

**Run it on a clean tree, immediately before tagging.** Everything it writes is
a claim that the release exists; `CITATION.cff` in particular is read by Zenodo
and GitHub, so a version there that is not tagged asserts a release nobody can
fetch.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _edits(target: str, previous: str, today: str) -> list[tuple[str, str, str]]:
    """`(path, pattern, replacement)`, each of which must match exactly once."""
    dev = f"v{target}-dev"
    return [
        ("README.md", rf"^Version: \*\*{re.escape(dev)}\*\*", f"Version: **v{target}**"),
        ("README.md", rf"^## Current situation: {re.escape(dev)}$",
         f"## Current situation: v{target}"),
        ("README.md", rf"this tree is {re.escape(dev)}", f"this tree is v{target}"),
        ("README.md", rf"\*\*Last release: v{re.escape(previous)}\*\*",
         f"**Last release: v{target}**"),
        ("README.md", rf"\*\*Released as v{re.escape(previous)};",
         f"**Released as v{target};"),
        ("SUPPLEMENTARY-MATERIAL-v1.0.0.tex",
         rf"\\date\{{\\textbf\{{{re.escape(dev)}\}}", rf"\\date{{\\textbf{{v{target}}}"),
        ("CITATION.cff", rf'^version: "{re.escape(previous)}"', f'version: "{target}"'),
        ("CITATION.cff", r"^date-released: .*$", f"date-released: {today}"),
        ("CHANGELOG.md", rf"^## \[Unreleased\] — v{re.escape(target)} in preparation$",
         f"## [{target}] — {today}"),
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--to", required=True, help="the version being released, e.g. 1.2.0")
    ap.add_argument("--from", dest="previous", default=None,
                    help="the previous release; read from CITATION.cff if omitted")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change and write nothing")
    args = ap.parse_args()

    if not re.fullmatch(r"\d+\.\d+\.\d+", args.to):
        ap.error(f"--to must be a bare semantic version, not {args.to!r}")

    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    found = re.search(r'^version: "([0-9.]+)"', cff, re.MULTILINE)
    if not found:
        print("FAIL  CITATION.cff has no version field")
        return 1
    previous = args.previous or found.group(1)
    today = dt.date.today().isoformat()

    print(f"bump v{previous} -> v{args.to}" + ("  (dry run)" if args.dry_run else ""))

    planned: list[tuple[Path, str]] = []
    failures: list[str] = []
    bodies: dict[str, str] = {}
    for name, pattern, replacement in _edits(args.to, previous, today):
        text = bodies.get(name) or (ROOT / name).read_text(encoding="utf-8")
        hits = len(re.findall(pattern, text, re.MULTILINE))
        if hits != 1:
            failures.append(
                f"{name}: {pattern!r} matched {hits} times, expected exactly 1")
            continue
        before = re.search(pattern, text, re.MULTILINE).group(0)
        bodies[name] = re.sub(pattern, replacement, text, count=1, flags=re.MULTILINE)
        print(f"  {name}\n      - {before}\n      + "
              f"{re.search(pattern, text, re.MULTILINE).expand(replacement)}")

    if failures:
        for line in failures:
            print(f"  FAIL  {line}")
        print("\nNothing written. **A partial bump is worse than none** --- it is "
              "exactly the split-label state this script exists to prevent, and "
              "the one the README was in for two days. Fix the mismatch and "
              "run again.")
        return 1

    if args.dry_run:
        print("\ndry run: nothing written")
        return 0

    for name, text in bodies.items():
        (ROOT / name).write_text(text, encoding="utf-8", newline="\n")
        planned.append((ROOT / name, text))
    print(f"\nwrote {len(bodies)} files. Now: run_all.py --strict, commit, tag.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
