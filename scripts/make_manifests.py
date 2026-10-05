#!/usr/bin/env python3
"""Regenerate FILE-MANIFEST-SHA256.txt and IMMUTABLE-MANIFEST-SHA256.txt.

    python scripts/make_manifests.py            # rewrite both manifests
    python scripts/make_manifests.py --check    # verify, exit 1 on any drift

`FILE-MANIFEST-SHA256.txt` covers every tracked file in the bundle. It is the
release fingerprint.

`IMMUTABLE-MANIFEST-SHA256.txt` covers only what must never change once
recorded — frozen reference material under `source/`, and the provenance records
of findings already raised. A change there is a release-blocking event, not a
routine update, because it means a recorded finding or a frozen source moved.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILE_MANIFEST = ROOT / "FILE-MANIFEST-SHA256.txt"
IMMUTABLE_MANIFEST = ROOT / "IMMUTABLE-MANIFEST-SHA256.txt"

EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", ".ipynb_checkpoints"}
EXCLUDE_FILES = {FILE_MANIFEST.name, IMMUTABLE_MANIFEST.name}

#: Paths whose contents are frozen once recorded, relative to the repository root.
IMMUTABLE_PREFIXES = (
    "source/",
    "provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tracked_files() -> list[Path]:
    out: list[Path] = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if set(rel.parts) & EXCLUDE_DIRS:
            continue
        if rel.name in EXCLUDE_FILES:
            continue
        out.append(p)
    return out


def is_immutable(rel: str) -> bool:
    return any(rel == pre or rel.startswith(pre) for pre in IMMUTABLE_PREFIXES)


def render(paths: list[Path]) -> str:
    lines = []
    for p in paths:
        rel = p.relative_to(ROOT).as_posix()
        lines.append(f"{sha256(p)}  {rel}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="verify without rewriting")
    args = ap.parse_args()

    files = tracked_files()
    full = render(files)
    frozen = render([p for p in files if is_immutable(p.relative_to(ROOT).as_posix())])

    if not args.check:
        FILE_MANIFEST.write_text(full, encoding="utf-8", newline="\n")
        IMMUTABLE_MANIFEST.write_text(frozen, encoding="utf-8", newline="\n")
        print(f"wrote {FILE_MANIFEST.name}      {len(files)} files")
        print(f"wrote {IMMUTABLE_MANIFEST.name} {len(frozen.splitlines())} files")
        return 0

    failed = False
    for manifest, expected, label in (
        (FILE_MANIFEST, full, "file"),
        (IMMUTABLE_MANIFEST, frozen, "immutable"),
    ):
        if not manifest.exists():
            print(f"FAIL  {manifest.name} is missing")
            failed = True
            continue
        actual = manifest.read_text(encoding="utf-8")
        if actual != expected:
            print(f"FAIL  {manifest.name} does not match the tree")
            have = dict(reversed(ln.split("  ", 1)) for ln in actual.splitlines() if ln)
            want = dict(reversed(ln.split("  ", 1)) for ln in expected.splitlines() if ln)
            for name in sorted(set(have) | set(want)):
                if have.get(name) != want.get(name):
                    state = (
                        "added" if name not in have else "removed" if name not in want else "changed"
                    )
                    print(f"        {state:8s} {name}")
                    if label == "immutable":
                        print("        ^ RELEASE-BLOCKING: a frozen record moved")
            failed = True
        else:
            print(f"PASS  {manifest.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
