#!/usr/bin/env python3
"""Generate provenance/conventions.md from the project's normative sheet.

    python scripts/sync_conventions.py --source <path-to-docs/conventions.md>
    python scripts/sync_conventions.py --check

**The conventions sheet is never hand-copied into this bundle.** A hand copy is
how a project ends up with duplicates that contradict the record and then surface
in search as if authoritative; this project has already deleted nine of them. The
copy carried here is generated, and it records the source path, the source
SHA-256 and the date, so drift is detectable rather than silent.

`--check` recomputes the source hash and fails if the recorded copy is stale. It
is part of the strict release route.

The sheet is **read-only input**. This script never writes to the source
repository.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "provenance" / "conventions.md"
STAMP = ROOT / "provenance" / "conventions-source.txt"

HEADER = """<!-- GENERATED FILE — DO NOT EDIT BY HAND.

Regenerate with:  python scripts/sync_conventions.py --source <path>

Source      : {source}
SHA-256     : {digest}
Generated   : {when}

The normative sheet lives in the project repository and is owned by the
conventions gate. This bundle carries a generated copy so that the code and the
conventions it was written against ship together. If `--check` fails, the source
has moved: regenerate, re-read the diff, and record anything that changes a
weight or a sign in ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md.

Equation numbers in the source sheet are arXiv numbers. This bundle cites
PUBLISHED numbers. The re-pointing map is tracked separately; do not assume a
constant offset.
-->

"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recorded() -> dict[str, str]:
    if not STAMP.exists():
        return {}
    out = {}
    for line in STAMP.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, help="path to the project's docs/conventions.md")
    ap.add_argument(
        "--record-as",
        type=str,
        default=None,
        help=(
            "path to record as the source, when generation and checking happen on "
            "different machines. The bytes hashed are still --source's."
        ),
    )
    ap.add_argument("--check", action="store_true", help="verify the copy is current")
    args = ap.parse_args()

    if args.check:
        info = recorded()
        if not info or not TARGET.exists():
            print("FAIL  provenance/conventions.md has not been generated yet")
            return 1
        src = Path(info.get("source", ""))
        if not src.exists():
            print(f"SKIP  source not reachable from here: {src}")
            print("      (expected when the project repository is not mounted)")
            return 0
        if sha256(src) != info.get("sha256"):
            print("FAIL  the normative sheet has changed since this copy was generated")
            print(f"      source   {src}")
            print(f"      recorded {info.get('sha256')}")
            print(f"      actual   {sha256(src)}")
            return 1
        print("PASS  provenance/conventions.md is current")
        return 0

    if not args.source:
        ap.error("--source is required unless --check is given")
    src = args.source.expanduser().resolve()
    if not src.is_file():
        ap.error(f"source not found: {src}")

    digest = sha256(src)
    when = dt.date.today().isoformat()
    recorded_path = args.record_as or str(src)
    TARGET.write_text(
        HEADER.format(source=recorded_path, digest=digest, when=when)
        + src.read_text(encoding="utf-8"),
        encoding="utf-8",
        newline="\n",
    )
    STAMP.write_text(
        f"source: {recorded_path}\nsha256: {digest}\ngenerated: {when}\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {TARGET.relative_to(ROOT)}  from {src}")
    if args.record_as:
        print(f"      recorded source as {recorded_path}")
    print(f"      sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
