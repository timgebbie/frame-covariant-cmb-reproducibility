#!/usr/bin/env python3
r"""Flip every version label at once, from one source of truth.

    python scripts/bump_release.py --to 1.2.0 --dry-run     # close a release
    python scripts/bump_release.py --to 1.2.0
    python scripts/bump_release.py --open 1.3.0 --dry-run   # open the next one
    python scripts/bump_release.py --open 1.3.0

**Why this exists.** `tests/test_readme_artefacts.py` already checks that the
version labels agree, and its docstring records why: *"a label flipped by hand
is a label that drifts"*, after the README header read `v1.1.0` while its own
verification section read `v1.2.0-dev` and the supplement's `\date` still read
`v1.0.0` two releases later. The test catches the drift. It does not prevent it,
because the flip was still six hand edits in four files.

This is the flip, done once, from one argument. The test then checks the result
rather than catching a mistake nobody had a tool to avoid.

**What `--to` touches, and nothing else.** The README's label sites (the
header, the verification section, the three tag-check commands and the
release-sequence table's status cell), the supplement's computational label,
`CITATION.cff` and the changelog heading. It does **not** create the next
release's supplement: under decision **S36** each release freezes its own
`SUPPLEMENTARY-MATERIAL-vX.tex` and the previous ones are kept, so starting the
next one is a deliberate act at the start of a release rather than a side
effect of ending this one.

**`--open` is that deliberate act, and it exists because doing it by hand cost
a released archive.** Closing a release had a tool; opening the next one did
not, so it was five hand edits across five files --- three README labels, a
changelog heading, a copied supplement, and the build repointed at it. On
2026-10-16 two of the five were missed and
`supplementary-materials/figures-v1.0.0.tex` and `supplement-v1.0.0.pdf`
survived into the v1.2.0 release archive, one of them byte-identical to its
v1.2.0 successor. **That is finding T-50, and it is this script's own defect
class arriving from the end it did not cover.** `--open`:

* flips the three README labels to `vX.Y.Z-dev`, leaving `**Last release:**`
  and `CITATION.cff` alone --- those track the release and must not move ---
  and makes the new line's release-sequence row the one marked current;
* opens a `## [Unreleased] — vX.Y.Z in preparation` section in the changelog;
* **leaves the supplement alone.** Since 2026-10-26 the supplement numbers
  its own editions, declared on the README's `Supplement:` line, which
  `scripts/_versions.py` reads; an edition is not a release and a release does
  not create one. So opening a line copies, renames and deletes nothing: the
  supplement's `\date` keeps naming the computational release it documents
  until its next edition says otherwise. The copy-forward this script used to
  make belonged to the one-supplement-per-release scheme of S36, and under the
  edition scheme it would have duplicated the live document.

It does not need to repoint the build: `scripts/_versions.py` derives all three
supplement filenames from the README header, so the three scripts and two tests
that used to spell them follow automatically. `scripts/check_release_hygiene.py`
is the gate that refuses a tree where they do not.

**What it does not own: the prose beside a label.** It flips the version
*token* at each site, not the sentence next to it. On the v1.2.0 bump the
header duly read `Last release: **v1.2.0**` followed by *"Peebles
recombination and the frame specialisation made numerical"* --- v1.1.0's
descriptor under v1.2.0's number, which is the **T-16** class in the first
two lines a reader sees. The script cannot write that sentence; the release
checklist must. Read the header after bumping.

**Run it on a clean tree, immediately before tagging.** Everything it writes is
a claim that the release exists; `CITATION.cff` in particular is read by GitHub
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

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _versions import (  # noqa: E402
    supplement_source,
    tree_version,
)


def _edits(target: str, previous: str, today: str,
           supplement: str) -> list[tuple[str, str, str]]:
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
        # The README carries the check rather than the answer (T-30): three
        # commands that name the last release, and they move with it.
        ("README.md", rf"git tag --list v{re.escape(previous)} ",
         f"git tag --list v{target} "),
        ("README.md", rf"git log --oneline -1 v{re.escape(previous)} ",
         f"git log --oneline -1 v{target} "),
        ("README.md", rf"git merge-base --is-ancestor v{re.escape(previous)} HEAD",
         f"git merge-base --is-ancestor v{target} HEAD"),
        # The release-sequence table's status cell. It was not a site until
        # v1.3.0 had been published for six days with its row still reading
        # *current*: a label this script did not know about is a label that
        # drifts, which is the whole argument above.
        ("README.md", rf"^(\| \*\*v{re.escape(target)}\*\* \|.*)· \*\*current\*\* \|$",
         r"\1· released |"),
        # The supplement's \date carries its own edition and, since the
        # editions started moving faster than the code, the computational
        # label after it: "Supplement v1.3.31 --- <date> ... computational
        # v1.3.0-dev}". Only the computational label is the release's to flip.
        (supplement, rf"computational {re.escape(dev)}\}}", f"computational v{target}}}"),
        ("CITATION.cff", rf'^version: "{re.escape(previous)}"', f'version: "{target}"'),
        ("CITATION.cff", r"^date-released: .*$", f"date-released: {today}"),
        ("CHANGELOG.md", rf"^## \[Unreleased\] — v{re.escape(target)} in preparation$",
         f"## [{target}] — {today}"),
    ]


def _open_edits(target: str, current: str) -> list[tuple[str, str, str]]:
    """`--open`'s label sites: the tree's three, and nowhere the release lives.

    `**Last release:**` and `CITATION.cff` are deliberately absent. They state
    what has been tagged, which opening a development line does not change, and
    a `CITATION.cff` naming an untagged version asserts a release nobody can
    fetch. The supplement's file names are absent too: under the edition scheme
    they follow the README's `Supplement:` line, not the computational one.
    """
    dev, old = f"v{target}-dev", re.escape(current)
    return [
        ("README.md", rf"^Version: \*\*v{old}\*\*", f"Version: **{dev}**"),
        ("README.md", rf"^## Current situation: v{old}$", f"## Current situation: {dev}"),
        ("README.md", rf"this tree is v{old}\.", f"this tree is {dev}."),
        # The line being opened becomes the release-sequence table's one
        # current row; `--to` turns it to *released* when it ships.
        ("README.md", rf"^(\| \*\*v{re.escape(target)}\*\* \|.*)· planned \|$",
         r"\1· **current** |"),
    ]


def open_release(target: str, dry_run: bool) -> int:
    """Open the next development line. The inverse of `--to`, and its equal."""
    current = tree_version(ROOT)
    if current.endswith("-dev"):
        print(f"FAIL  this tree is already v{current}; a development line is open.")
        return 1
    if target == current:
        print(f"FAIL  --open {target} is the version this tree already is.")
        return 1

    print(f"open v{current} -> v{target}-dev" + ("  (dry run)" if dry_run else ""))

    bodies: dict[str, str] = {}
    failures: list[str] = []
    for edit in _open_edits(target, current):
        name, pattern, replacement = edit[0], edit[1], edit[2]
        expected = edit[3] if len(edit) > 3 else 1
        text = bodies.get(name) or (ROOT / name).read_text(encoding="utf-8")
        hits = len(re.findall(pattern, text, re.MULTILINE))
        if hits != expected:
            failures.append(
                f"{name}: {pattern!r} matched {hits} times, expected {expected}")
            continue
        found = re.search(pattern, text, re.MULTILINE)
        bodies[name] = re.sub(pattern, replacement, text, flags=re.MULTILINE)
        print(f"  {name}\n      - {found.group(0)}" + (f"  (x{hits})" if hits > 1 else "")
              + f"\n      + {found.expand(replacement)}")

    # The changelog's open section, inserted above the most recent dated one.
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    heading = f"## [Unreleased] — v{target} in preparation"
    if heading in changelog:
        failures.append(f"CHANGELOG.md: already carries {heading!r}")
    else:
        first = re.search(r"^## \[", changelog, re.MULTILINE)
        if not first:
            failures.append("CHANGELOG.md: no `## [` section to insert above")
        else:
            at = first.start()
            bodies["CHANGELOG.md"] = (
                changelog[:at] + heading + "\n\n" + changelog[at:])
            print(f"  CHANGELOG.md\n      + {heading}")

    if failures:
        for line in failures:
            print(f"  FAIL  {line}")
        print("\nNothing written. **A half-opened release line is the state this "
              "exists to prevent** --- it is where the v1.2.0 archive's two "
              "stale build outputs came from (T-50).")
        return 1

    if dry_run:
        print("\ndry run: nothing written")
        return 0

    for name, text in bodies.items():
        (ROOT / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"\nwrote {len(bodies)} files.")
    print("  NEXT: the README header's *descriptor* is still the previous\n"
          "        release's sentence. This script flips the version token, not\n"
          "        the prose beside it --- read the header.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--to", help="the version being released, e.g. 1.2.0")
    mode.add_argument("--open", dest="opening",
                      help="the next version to start work on, e.g. 1.3.0")
    ap.add_argument("--from", dest="previous", default=None,
                    help="the previous release; read from CITATION.cff if omitted")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change and write nothing")
    args = ap.parse_args()

    for flag, value in (("--to", args.to), ("--open", args.opening)):
        if value is not None and not re.fullmatch(r"\d+\.\d+\.\d+", value):
            ap.error(f"{flag} must be a bare semantic version, not {value!r}")

    if args.opening:
        return open_release(args.opening, args.dry_run)

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
    supplement = supplement_source(ROOT).name
    for name, pattern, replacement in _edits(args.to, previous, today, supplement):
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
    print(f"\nwrote {len(bodies)} files.")
    print("  NEXT, and it is part of the same release act: promote this\n        release's artefacts R -> S in scripts/make_release_status.py.\n        S27 defines S as 'in a tagged release', so the release commit\n        declares it and the tag points at that commit.")
    print("  THEN: run_all.py --strict, commit, tag.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
