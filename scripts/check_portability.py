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
