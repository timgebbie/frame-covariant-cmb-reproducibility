#!/usr/bin/env python3
r"""Build the release archive, and verify it by extracting it — finding T-13.

    python scripts/make_release_archive.py
    python scripts/make_release_archive.py --version 1.1.0

**The zip attached to the v1.0.0 GitHub release and deposited to ZivaHub was
assembled by an ad-hoc script written in a chat session.** It was verified by
hand — extracted, with the portability and manifest gates run inside it — so the
artefact was sound. The *process* was the finding, and it is T-7's lesson
exactly: the supplement was built, moved and renamed by hand until R3 put it
under the harness, and in the meantime it shipped with 55mm of text past the
margin. The archive is the file a reader downloads. It belongs under the
harness.

Three properties, each of which was a separate lesson somewhere else:

1. **The file set is the shared selector**, `scripts/_bundle_files.py` — the
   same one the portability gate and the manifests use. Finding **T-1** was a
   fingerprint that disagreed with the bundle because it had its own idea of
   which files counted; there is one idea, and this is it.
2. **The timestamps are fixed**, so the archive is byte-reproducible from the
   same tree. Finding **T-11** is that `pdflatex` stamped a clock into the
   supplement and `--strict` could never pass; a zip stamps the wall clock into
   every member. Same defect, different generator, and the rule stated at the
   end of T-11 was that *any* artefact the harness generates must be
   byte-reproducible from the same inputs.
3. **It extracts what it built and runs the gates inside it**, rather than
   trusting that a zip of the right files is a working bundle. That is
   **R2**'s discipline — the acceptance runs on the released tree, not on the
   working folder — applied one level further out, to the file that leaves.

Skips nothing and fails loudly. A release archive that cannot be verified is
not a release archive.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _bundle_files import bundle_files  # noqa: E402

REPOSITORY = "frame-covariant-cmb-reproducibility"

#: Fixed member timestamp, so the same tree always produces the same bytes.
#: 2026-10-09T00:00:00Z, the same instant `scripts/build_supplement.py` pins
#: `SOURCE_DATE_EPOCH` to, so the two generators cannot disagree about when
#: "now" is. **A build clock that moves is the entire problem** (T-11).
FIXED_TIMESTAMP = (2026, 10, 9, 0, 0, 0)

#: The gates that must pass *inside* the extracted archive. Not a subset
#: chosen for speed: these are the two that answer "is this a working bundle",
#: and both run without a toolchain or a network.
GATES = (
    ("portability", ["scripts/check_portability.py"]),
    ("manifests", ["scripts/make_manifests.py", "--check"]),
)


def build(version: str, destination: Path) -> tuple[Path, int]:
    """Write the archive and return its path and file count."""
    prefix = f"{REPOSITORY}-{version}"
    files = sorted(
        bundle_files(ROOT),
        key=lambda p: str(p.relative_to(ROOT)).replace("\\", "/"),
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = str(path.relative_to(ROOT)).replace("\\", "/")
            info = zipfile.ZipInfo(f"{prefix}/{relative}", date_time=FIXED_TIMESTAMP)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())

    return destination, len(files)


def verify(archive: Path, version: str) -> bool:
    """Extract the archive and run the gates inside it. **This is the acceptance.**"""
    prefix = f"{REPOSITORY}-{version}"
    with tempfile.TemporaryDirectory(prefix="release-archive-") as tmp:
        with zipfile.ZipFile(archive) as handle:
            handle.extractall(tmp)
        tree = Path(tmp) / prefix
        if not tree.is_dir():
            print(f"FAIL  the archive does not contain {prefix}/")
            return False

        ok = True
        for label, command in GATES:
            print(f"\n--- {label} (inside the archive) " + "-" * max(0, 28 - len(label)))
            result = subprocess.run(
                [sys.executable, *command], cwd=tree,
                capture_output=True, text=True, timeout=600,
            )
            sys.stdout.write(result.stdout)
            if result.returncode != 0:
                sys.stdout.write(result.stderr)
                ok = False
        return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="1.0.0",
                        help="version string for the archive name and prefix")
    parser.add_argument("--out", default=None, help="output path for the zip")
    args = parser.parse_args()

    destination = Path(args.out) if args.out else (
        ROOT / "dist" / f"{REPOSITORY}-v{args.version}.zip"
    )

    archive, count = build(args.version, destination)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()

    print(f"built {archive.name}  —  {count} files, {archive.stat().st_size:,} bytes")
    print(f"  sha256 {digest}")

    if not verify(archive, args.version):
        print("\n" + "=" * 60)
        print("NOT RELEASABLE  --  the archive does not pass its own gates")
        return 1

    print("\n" + "=" * 60)
    print(f"the archive passes every gate it was given: {count} files.")
    print("That is the number a reader gets, verified by extracting it rather")
    print("than by trusting the file list that produced it.")
    print(f"\n  sha256  {digest}")
    print("  Publish this digest with the release; it is what attests the")
    print("  deposited copy is the same object.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
