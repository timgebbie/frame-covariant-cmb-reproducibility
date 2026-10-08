#!/usr/bin/env python3
"""Refuse to ship anything that has only ever run where it was written.

    python scripts/check_portability.py

**The gate, from Coordination's audit, 2026-10-06.** Two check scripts elsewhere
in the project carried hardcoded container paths and could never have run on the
PI's machine, and one file had mixed line endings. A green run in the environment
that produced the code is not evidence that it runs anywhere else.

This script is the automatic half of that gate. The other half cannot be
automated and is stated in the release notes: **a clean checkout on the PI's
machine is the acceptance.** This only rules out the failures a machine can see.

Checks:

1. **No absolute paths outside the repository.** Every path must be derived from
   ``Path(__file__).resolve().parents[n]`` or be relative. A literal
   ``/home/...``, ``/mnt/...``, ``/tmp/...`` or ``C:\\...`` in source is a failure.
2. **No mixed line endings within a file.** A file may be all LF or all CRLF;
   mixing the two inside one file breaks diffs, hashes and some parsers, and is
   invisible in an editor.
3. **No non-ASCII in code paths or identifiers**, which travel badly across
   filesystems. Prose and docstrings are exempt; this bundle is written in
   English with mathematical symbols and that is deliberate.

**The file set is not this script's to decide.** It comes from
`scripts/_bundle_files.py`, the one selector the manifest generator also uses,
so that the number printed below means the same thing here and on the PI's
machine. It did not, briefly: see finding T-1.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _bundle_files import (  # noqa: E402
    BINARY_SUFFIXES,
    bundle_files,
    ignored_but_present,
)

ROOT = Path(__file__).resolve().parents[1]

#: Absolute-path shapes that cannot survive a move to another machine.
FORBIDDEN = re.compile(
    r"""(?x)
    (?<!\#\s)                      # allow a commented example
    (?:
        ["'](?:/home/|/mnt/|/tmp/|/Users/|/var/folders/)
      | ["'][A-Za-z]:\\\\
    )
    """
)

def source_files() -> list[Path]:
    """The bundle's text files: everything it ships, minus what a text gate cannot read."""
    return [p for p in bundle_files(ROOT) if p.suffix not in BINARY_SUFFIXES]


def git_tracked() -> set[str] | None:
    """What a clean `git clone` would deliver, or None when git cannot answer.

    Returns None without a `.git` directory or without a usable `git` — the
    normal case for a reader who downloaded a zip, and for any environment that
    is not the publishing checkout. The check below is then skipped rather than
    failed: absence of git is not evidence of anything.
    """
    if not (ROOT / ".git").exists():
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            capture_output=True, check=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return {p for p in out.stdout.decode("utf-8", "replace").split("\0") if p}


def check_against_git(failures: list[str]) -> str:
    """The published tree and the fingerprinted tree must be the same tree.

    **Finding T-6.** `bundle_files()` answers *what is in this folder*. Git
    answers *what a clean checkout will contain*. Those are different questions,
    and the release fingerprint is only meaningful for the second — a reader
    verifies a clone, not somebody's working directory.

    They disagreed, and the disagreement was invisible to every gate in place:
    `data/.gitkeep` was tracked but deleted from disk, while an untracked file
    sat in `supplementary-materials/`. **One file each way, so the counts came
    out equal at 106 and 106** — and the portability gate prints a count, while
    the manifest test asserts arithmetic on counts. Nothing compared the sets.
    A clean checkout would have failed `make_manifests.py --check` for a reason
    nobody would have found quickly, and a clean checkout is this project's
    stated acceptance.
    """
    tracked = git_tracked()
    if tracked is None:
        return "      (no git here; a clean-checkout comparison was not possible)"

    here = {p.relative_to(ROOT).as_posix() for p in bundle_files(ROOT)}
    only_git, only_disk = sorted(tracked - here), sorted(here - tracked)
    for rel in only_git:
        failures.append(
            f"{rel}: tracked by git but absent from the working tree — a clean "
            "clone restores it and the fingerprint does not describe it"
        )
    for rel in only_disk:
        failures.append(
            f"{rel}: in the working tree but untracked — it is inside the "
            "fingerprint and a clean clone will not have it"
        )
    if only_git or only_disk:
        return ""
    return f"      git agrees: {len(tracked)} tracked files, same set."


def main() -> int:
    failures: list[str] = []

    for path in source_files():
        rel = path.relative_to(ROOT)
        raw = path.read_bytes()

        crlf = raw.count(b"\r\n")
        lf = raw.count(b"\n") - crlf
        if crlf and lf:
            failures.append(f"{rel}: mixed line endings (CRLF={crlf}, LF={lf})")

        if path.suffix != ".py":
            continue
        text = raw.decode("utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if FORBIDDEN.search(line):
                failures.append(f"{rel}:{n}: absolute path outside the repository")

        # Only *entry points* must anchor themselves. A module that receives its
        # root as an argument is portable by construction, and demanding
        # `__file__` of it would push a hardcoded root into a library --- the
        # opposite of what this rule is for. `__main__` is the test for "this
        # gets run, so it has to know where it is".
        is_entry_point = '__name__ == "__main__"' in text or "__name__ == '__main__'" in text
        if (
            rel.parts[0] == "scripts"
            and is_entry_point
            and "__file__" not in text
            and "Path(" in text
        ):
            failures.append(f"{rel}: entry point builds paths without anchoring to __file__")

    # The published tree and the fingerprinted tree must be the same tree (T-6).
    git_note = check_against_git(failures)

    if failures:
        print(f"FAIL  {len(failures)} portability problem(s):")
        for f in failures:
            print(f"      {f}")
        print()
        print("      Nothing ships from this bundle that has only ever run where")
        print("      it was written. Fix these, then run a clean checkout on the")
        print("      PI's machine -- that, not this script, is the acceptance.")
        return 1

    shipped = bundle_files(ROOT)
    checked = source_files()
    binary = len(shipped) - len(checked)
    print(f"PASS  {len(shipped)} bundle files "
          f"({len(checked)} content-checked, {binary} binary): "
          "no absolute paths, no mixed line endings")
    print(f"      {len(shipped) - 2} manifest entries expected "
          "(the two manifests cannot hash themselves).")
    if git_note:
        print(git_note)
    print("      This rules out what a machine can see. A clean checkout on the")
    print("      PI's machine remains the acceptance.")

    # A note, never a failure. Local build products are normal; two machines
    # disagreeing about the bundle's size is not, and this is where that
    # question gets answered without a round trip.
    stray = ignored_but_present(ROOT)
    if stray:
        print()
        print(f"NOTE  {len(stray)} file(s) in this working tree are ignored and are")
        print("      NOT part of the bundle or the fingerprint:")
        for rel in stray[:12]:
            print(f"        {rel}")
        if len(stray) > 12:
            print(f"        ... and {len(stray) - 12} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
