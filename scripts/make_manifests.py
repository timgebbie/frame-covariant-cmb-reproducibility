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

#: Paths frozen once recorded, relative to the repository root. Frozen reference
#: material only: anything here changing at all is a release-blocking event.
IMMUTABLE_PREFIXES = ("source/",)

#: Paths that may only GROW. The corrections record has to take new findings, so
#: freezing its hash would raise a release-blocking alarm every time the bundle
#: did its job — and an alarm that cries wolf is worse than no alarm. Instead the
#: guard stores the length and hash of what has been written so far and verifies
#: that those bytes are unchanged: appending is fine, rewriting history is not.
#: This is the project's append-only discipline, enforced rather than trusted.
APPEND_ONLY = ("provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md",)

APPEND_GUARD = "provenance/append-guard.txt"


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


def write_append_guard() -> None:
    lines = []
    for rel in APPEND_ONLY:
        data = (ROOT / rel).read_bytes()
        lines.append(f"{len(data)} {hashlib.sha256(data).hexdigest()}  {rel}")
    (ROOT / APPEND_GUARD).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def check_append_guard() -> bool:
    """True if every append-only file still begins with exactly what was recorded."""
    guard = ROOT / APPEND_GUARD
    if not guard.exists():
        print(f"FAIL  {APPEND_GUARD} is missing — run without --check to seed it")
        return False
    ok = True
    for line in guard.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        head, rel = line.rsplit("  ", 1)
        length, digest = head.split()
        data = (ROOT / rel).read_bytes()
        prefix = data[: int(length)]
        if len(prefix) < int(length) or hashlib.sha256(prefix).hexdigest() != digest:
            print(f"FAIL  {rel} was rewritten, not appended to")
            print("        ^ RELEASE-BLOCKING: a recorded finding moved")
            ok = False
        elif len(data) > int(length):
            print(f"PASS  {rel} grew by {len(data) - int(length)} bytes (append)")
        else:
            print(f"PASS  {rel} unchanged")
    return ok


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
        write_append_guard()
        # the guard is itself a tracked file, so recompute after writing it
        files = tracked_files()
        full = render(files)
        frozen = render([p for p in files if is_immutable(p.relative_to(ROOT).as_posix())])
        FILE_MANIFEST.write_text(full, encoding="utf-8", newline="\n")
        IMMUTABLE_MANIFEST.write_text(frozen, encoding="utf-8", newline="\n")
        print(f"wrote {APPEND_GUARD}      {len(APPEND_ONLY)} append-only files")
        print(f"wrote {FILE_MANIFEST.name}      {len(files)} files")
        print(f"wrote {IMMUTABLE_MANIFEST.name} {len(frozen.splitlines())} files")
        return 0

    failed = not check_append_guard()
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
