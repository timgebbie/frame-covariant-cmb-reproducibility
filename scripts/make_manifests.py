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

**Which files count is not decided here.** It comes from
`scripts/_bundle_files.py`, shared with the portability gate, and it honours
`.gitignore`. Before finding T-1 it did not, and a local `pdflatex` run's
`.aux`/`.log`/`.out` could enter the release fingerprint — making the
fingerprint a property of somebody's folder rather than of the repository.
"""

from __future__ import annotations

import argparse
import re
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _bundle_files import bundle_files  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

FILE_MANIFEST = ROOT / "FILE-MANIFEST-SHA256.txt"
IMMUTABLE_MANIFEST = ROOT / "IMMUTABLE-MANIFEST-SHA256.txt"
PORTABLE_MANIFEST = ROOT / "PORTABLE-MANIFEST-SHA256.txt"

#: Significant figures kept when canonicalising a generated numeric artefact.
#:
#: **Finding T-15.** `--strict` regenerates every artefact and then hashes it, so
#: it could only ever pass on the machine that produced the bytes. Three CSVs
#: differed between a Linux container and the PI's Windows machine --- not the
#: renderings, the *numbers*, in their last digits, because BLAS and libm differ.
#: Byte-identity is the wrong criterion for a generated numeric artefact.
#:
#: Cross-platform float noise is last-digit, around $10^{-15}$ relative, and a
#: solver amplifies it by a few orders at most. Nine significant figures is far
#: above that and far below any change worth calling a change. **This is the
#: first value tried, and the PI's machine is the measurement**: if a run there
#: fails at nine, the failure reports the real magnitude and this comes down.
SIGNIFICANT_FIGURES = 9

#: Generated artefacts whose bytes are a *rendering* --- fonts, freetype,
#: TeX Live version. A mismatch here is drift, reported and not release-blocking,
#: because a PNG that differs in hinting carries no scientific difference.
RENDERED_PREFIXES = ("figures/", "supplementary-materials/")
RENDERED_SUFFIXES = (".png", ".pdf")

#: Generated artefacts that are text but carry computed numbers.
NUMERIC_PREFIXES = ("outputs/", "tables/", "diagnostics/")
NUMERIC_SUFFIXES = (".csv", ".txt")

_FLOAT = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")

# The manifests cannot hash themselves. **Three of them now** --- the portable
# one added by T-15 is a tracked file like the others, and leaving it out of
# this set made it appear in its own listing on the first run.
EXCLUDE_FILES = {FILE_MANIFEST.name, IMMUTABLE_MANIFEST.name, PORTABLE_MANIFEST.name}

#: Paths frozen once recorded, relative to the repository root. Frozen reference
#: material only: anything here changing at all is a release-blocking event.
IMMUTABLE_PREFIXES = ("source/",)

#: Paths that may only GROW. The corrections record has to take new findings, so
#: freezing its hash would raise a release-blocking alarm every time the bundle
#: did its job — and an alarm that cries wolf is worse than no alarm. Instead the
#: guard stores the length and hash of what has been written so far and verifies
#: that those bytes are unchanged: appending is fine, rewriting history is not.
#: This is the project's append-only discipline, enforced rather than trusted.
APPEND_ONLY = (
    "provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md",
    "provenance/BUNDLE-DEFECTS-v1.md",
)

APPEND_GUARD = "provenance/append-guard.txt"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tracked_files() -> list[Path]:
    """Every file in the bundle except the two manifests, which cannot hash themselves."""
    return [p for p in bundle_files(ROOT) if p.name not in EXCLUDE_FILES]


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


def artefact_class(rel: str) -> str:
    """`rendered`, `numeric` or `exact`, **derived from the path, never listed**.

    A hand-maintained list of which files are which is one more thing to forget
    when a file is added --- the mistake T-1 and T-16 are both about. The rule
    is the location and the extension, so a new output lands in the right class
    by being put in the right directory.
    """
    if rel.endswith(RENDERED_SUFFIXES) and rel.startswith(RENDERED_PREFIXES):
        return "rendered"
    if rel.startswith("diagnostics/") and rel.endswith(".png"):
        return "rendered"
    if rel.endswith(NUMERIC_SUFFIXES) and rel.startswith(NUMERIC_PREFIXES):
        return "numeric"
    return "exact"


def _canonicalise(text: str) -> str:
    """Re-emit every float at `SIGNIFICANT_FIGURES`, leaving everything else alone.

    This is what makes a numeric artefact comparable across machines: the digits
    that differ between one BLAS and another are below the cut, and anything a
    reader would call a change survives it.
    """
    def round_one(m: re.Match) -> str:
        token = m.group(0)
        try:
            value = float(token)
        except ValueError:                     # pragma: no cover - regex is tight
            return token
        if token.lstrip("+-").isdigit():       # a plain integer is not a measurement
            return token
        return f"{value:.{SIGNIFICANT_FIGURES - 1}e}"

    return _FLOAT.sub(round_one, text)


def portable_digest(path: Path, rel: str) -> str:
    """The hash `--strict` binds on: canonicalised for numeric artefacts."""
    if artefact_class(rel) != "numeric":
        return sha256(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    return hashlib.sha256(_canonicalise(text).encode("utf-8")).hexdigest()


def render_portable(paths: list[Path]) -> str:
    """Everything but the renderings, numeric artefacts canonicalised."""
    lines = []
    for p in paths:
        rel = p.relative_to(ROOT).as_posix()
        if artefact_class(rel) == "rendered":
            continue
        lines.append(f"{portable_digest(p, rel)}  {rel}")
    return "\n".join(lines) + "\n"


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

    if not args.check:
        write_append_guard()
        # the guard is itself a tracked file, so recompute after writing it
        files = tracked_files()
        full = render(files)
        frozen = render([p for p in files if is_immutable(p.relative_to(ROOT).as_posix())])
        portable = render_portable(files)
        FILE_MANIFEST.write_text(full, encoding="utf-8", newline="\n")
        IMMUTABLE_MANIFEST.write_text(frozen, encoding="utf-8", newline="\n")
        PORTABLE_MANIFEST.write_text(portable, encoding="utf-8", newline="\n")
        print(f"wrote {APPEND_GUARD}      {len(APPEND_ONLY)} append-only files")
        print(f"wrote {FILE_MANIFEST.name}      {len(files)} files")
        print(f"wrote {IMMUTABLE_MANIFEST.name} {len(frozen.splitlines())} files")
        print(f"wrote {PORTABLE_MANIFEST.name}  "
              f"{len(portable.splitlines())} files, numeric canonicalised to "
              f"{SIGNIFICANT_FIGURES} s.f.")
        return 0

    full = render(files)
    frozen = render([p for p in files if is_immutable(p.relative_to(ROOT).as_posix())])
    portable = render_portable(files)

    failed = not check_append_guard()

    # **The portable manifest is what binds --- finding T-15.** It excludes the
    # renderings and canonicalises the numbers, so a machine that did not
    # generate the artefacts can still satisfy it. The byte manifest below is
    # then a *within-machine* drift check: it is reported, by class, and only
    # an `exact` mismatch there is release-blocking, which the portable check
    # has already caught.
    if not PORTABLE_MANIFEST.exists():
        print(f"FAIL  {PORTABLE_MANIFEST.name} is missing — run without --check to seed it")
        failed = True
    elif PORTABLE_MANIFEST.read_text(encoding="utf-8") != portable:
        print(f"FAIL  {PORTABLE_MANIFEST.name} does not match the tree")
        have = dict(reversed(ln.split("  ", 1))
                    for ln in PORTABLE_MANIFEST.read_text(encoding="utf-8").splitlines() if ln)
        want = dict(reversed(ln.split("  ", 1)) for ln in portable.splitlines() if ln)
        for name in sorted(set(have) | set(want)):
            if have.get(name) != want.get(name):
                state = ("added" if name not in have
                         else "removed" if name not in want else "changed")
                print(f"        {state:8s} {name}   [{artefact_class(name)}]")
        print("        ^ RELEASE-BLOCKING: this is content, not rendering")
        failed = True
    else:
        print(f"PASS  {PORTABLE_MANIFEST.name}  (binds; "
              f"numeric to {SIGNIFICANT_FIGURES} s.f., renderings excluded)")

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
            have = dict(reversed(ln.split("  ", 1)) for ln in actual.splitlines() if ln)
            want = dict(reversed(ln.split("  ", 1)) for ln in expected.splitlines() if ln)
            moved = [n for n in sorted(set(have) | set(want)) if have.get(n) != want.get(n)]
            by_class: dict[str, list[str]] = {}
            for name in moved:
                by_class.setdefault(artefact_class(name), []).append(name)

            blocking = label == "immutable" or "exact" in by_class
            print(f"{'FAIL' if blocking else 'DRIFT'}  {manifest.name} "
                  f"does not match the tree")
            for klass in ("exact", "numeric", "rendered"):
                for name in by_class.get(klass, []):
                    state = ("added" if name not in have
                             else "removed" if name not in want else "changed")
                    print(f"        {state:8s} {name}   [{klass}]")
            if label == "immutable":
                print("        ^ RELEASE-BLOCKING: a frozen record moved")
            elif not blocking:
                print("        ^ not release-blocking: renderings depend on the")
                print("          matplotlib and TeX Live that drew them, and numbers")
                print("          on the BLAS that computed them. The portable")
                print("          manifest above is what this release stands on.")
            failed = failed or blocking
        else:
            print(f"PASS  {manifest.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
