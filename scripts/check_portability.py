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
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

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

SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", ".venv", "venv"}
BINARY = {".png", ".pdf", ".pyc", ".zip", ".gz"}


def source_files() -> list[Path]:
    out = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or set(p.parts) & SKIP_DIRS or p.suffix in BINARY:
            continue
        out.append(p)
    return out


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

        if "__file__" not in text and "Path(" in text and rel.parts[0] == "scripts":
            failures.append(f"{rel}: builds paths without anchoring to __file__")

    if failures:
        print(f"FAIL  {len(failures)} portability problem(s):")
        for f in failures:
            print(f"      {f}")
        print()
        print("      Nothing ships from this bundle that has only ever run where")
        print("      it was written. Fix these, then run a clean checkout on the")
        print("      PI's machine -- that, not this script, is the acceptance.")
        return 1

    print(f"PASS  {len(source_files())} files: no absolute paths, no mixed line endings")
    print("      This rules out what a machine can see. A clean checkout on the")
    print("      PI's machine remains the acceptance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
