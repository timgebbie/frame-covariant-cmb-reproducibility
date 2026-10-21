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

**What `--to` touches, and nothing else.** The six label sites, plus
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
  and `CITATION.cff` alone --- those track the release and must not move;
* opens a `## [Unreleased] — vX.Y.Z in preparation` section in the changelog;
* copies the current supplement forward to `SUPPLEMENTARY-MATERIAL-vX.Y.Z.tex`
  and sets its `\date` to the new `-dev` label, **leaving the previous one
  frozen in place** as S36 requires;
* **removes the previous release's build outputs**, which S36 does not keep ---
  the rendering of record for an earlier release is its release asset and its
  archived DOI, not a stale file in this tree.

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
    supplement_figures,
    supplement_pdf,
    supplement_source,
    supplement_version,
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
        (supplement,
         rf"\\date\{{\\textbf\{{{re.escape(dev)}\}}", rf"\\date{{\\textbf{{v{target}}}"),
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
    fetch.
    """
    dev, old = f"v{target}-dev", re.escape(current)
    return [
        ("README.md", rf"^Version: \*\*v{old}\*\*", f"Version: **{dev}**"),
        ("README.md", rf"^## Current situation: v{old}$", f"## Current situation: {dev}"),
        ("README.md", rf"this tree is v{old}\.", f"this tree is {dev}."),
        # The preamble link and the artefact table both point at the rendering
        # that exists in this tree, and under S36 that is the live one. They
        # are two sites naming the same file, so the count below is 2 and not
        # 1 --- `_apply` takes the expected number rather than assuming one.
        ("README.md", rf"\(supplementary-materials/supplement-v{old}\.pdf\)",
         f"(supplementary-materials/supplement-v{target}.pdf)", 2),
        ("README.md", rf"\[supplement-v{old}\.pdf\]", f"[supplement-v{target}.pdf]", 2),
        ("README.md", rf"`SUPPLEMENTARY-MATERIAL-v{old}\.tex`",
         f"`SUPPLEMENTARY-MATERIAL-v{target}.tex`"),
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
        before = re.search(pattern, text, re.MULTILINE).group(0)
        bodies[name] = re.sub(pattern, replacement, text, flags=re.MULTILINE)
        print(f"  {name}\n      - {before}" + (f"  (x{hits})" if hits > 1 else "")
              + f"\n      + {replacement}")

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

    # The supplement is copied forward; the previous one stays frozen (S36).
    source = supplement_source(ROOT)
    destination = ROOT / f"SUPPLEMENTARY-MATERIAL-v{target}.tex"
    if not source.exists():
        failures.append(f"{source.name}: the current supplement does not exist")
    elif destination.exists():
        failures.append(f"{destination.name}: already exists; refusing to overwrite it")
    else:
        tex = source.read_text(encoding="utf-8")
        dated, n = re.subn(r"\\date\{\\textbf\{v[\d.]+(?:-dev)?\}",
                           rf"\\date{{\\textbf{{v{target}-dev}}", tex, count=1)
        if n != 1:
            failures.append(f"{source.name}: no `\\date{{\\textbf{{vX}}` line to re-label")
        # **The copy's own `\input` must follow it, and *only* that one.** The
        # supplement includes `supplementary-materials/figures-vX.tex`, which
        # this script is about to delete; a forward copy still inputting the
        # old name builds the previous release's figure section. Its build
        # banner names the source too, and a banner telling a reader to compile
        # a file that no longer exists is T-16 in the document's first line.
        #
        # **Both patterns are anchored to a full filename.** A blanket
        # `-vX.Y.Z.tex` -> `-vX.Y.Z+1.tex` rewrite is the obvious shortcut and
        # it is wrong: the supplement also inputs `tables/criterion-5b-v1.2.0.tex`,
        # a *table*, which keeps its introduced-in suffix through every release.
        # The `--dry-run` on the v1.3.0 open reported five includes repointed
        # where three were meant, and the two extra sit inside an
        # `\IfFileExists{...}{}{}` that would have dropped the criterion-5b
        # table out of the supplement **without an error**. Caught by looking
        # at the dry run, which is the only reason it has one.
        figures = re.escape(supplement_figures(ROOT).relative_to(ROOT).as_posix())
        repointed, m = re.subn(
            figures,
            supplement_figures(ROOT).parent.name + f"/figures-v{target}.tex", dated)
        banner, b = re.subn(rf"SUPPLEMENTARY-MATERIAL-v{re.escape(current)}\.tex",
                            f"SUPPLEMENTARY-MATERIAL-v{target}.tex", repointed)
        if n == 1:
            bodies[destination.name] = banner
            print(f"  {destination.name}\n      + copied from {source.name}; "
                  f"\\date v{target}-dev, {m} include(s) and {b} build "
                  "banner(s) repointed")

    stale = [p for p in (supplement_pdf(ROOT), supplement_figures(ROOT)) if p.exists()]

    if failures:
        for line in failures:
            print(f"  FAIL  {line}")
        print("\nNothing written. **A half-opened release line is the state this "
              "exists to prevent** --- it is where the v1.2.0 archive's two "
              "stale build outputs came from (T-50).")
        return 1

    for path in stale:
        print(f"  {path.relative_to(ROOT).as_posix()}\n      - removed: a build "
              f"output of v{supplement_version(ROOT)}, which S36 does not keep")

    if dry_run:
        print("\ndry run: nothing written")
        return 0

    for name, text in bodies.items():
        (ROOT / name).write_text(text, encoding="utf-8", newline="\n")
    for path in stale:
        path.unlink()
    print(f"\nwrote {len(bodies)} files, removed {len(stale)}.")
    print("  NEXT: the README header's *descriptor* is still the previous\n"
          "        release's sentence. This script flips the version token, not\n"
          "        the prose beside it --- read the header.")
    print("  THEN: run_all.py --rerun, which regenerates the supplement and its\n"
          "        figure pages under the new name.")
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
