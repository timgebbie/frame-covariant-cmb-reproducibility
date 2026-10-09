#!/usr/bin/env python3
"""Run the release gates against what a clean checkout actually contains.

    python scripts/check_clean_checkout.py

**This is the acceptance, generalised from one machine to one tree.** The
standing rule is that nothing ships from this bundle that has only ever run
where it was written, and `check_portability.py` is the automatic half of it.
But that script, and every other gate, runs against the **working folder** —
which is not what a reader receives. A reader receives the tracked tree at
`HEAD`: no untracked files, no files deleted locally but still tracked, no
build products.

Finding **T-6** is why this exists. Git and the working folder differed by one
file each way, so the counts matched at 106 and 106 and every gate passed, while
a clean clone would have failed `make_manifests.py --check`. Comparing the
**set** rather than its cardinality caught that, and `check_portability.py` now
does so whenever git is available. This script closes the remaining half: it
materialises the tree a reader would get and runs the gates inside it, so the
acceptance is performed rather than reasoned about.

`git archive HEAD` is used rather than `git clone`. It extracts exactly the
tracked tree with no `.git` directory, which is both faster and a better model
of a downloaded release — a reader unpacking a zip has no repository either, and
the gates must give them the same answer.

Exits non-zero if any gate fails inside the clean tree. Skips, with a stated
reason and exit 0, where git is unavailable: absence of git is not evidence of
anything, and a gate that fails on it would repeat finding T-4.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: The gates to run inside the clean tree, in order. Each is run as
#: `python <script>` from the extracted root, exactly as a reader would.
GATES = [
    ("portability", ["scripts/check_portability.py"]),
    ("manifests", ["scripts/make_manifests.py", "--check"]),
]


def unavailable() -> str | None:
    """Why this check cannot run here, or None if it can."""
    if not (ROOT / ".git").exists():
        return "no .git directory: this is not the publishing checkout"
    if shutil.which("git") is None:
        return "git is not on PATH"
    return None


def main() -> int:
    why = unavailable()
    if why is not None:
        print(f"SKIP  clean-checkout acceptance: {why}")
        print("      Not a failure. The acceptance is performed where the")
        print("      repository is, and reported there.")
        return 0

    with tempfile.TemporaryDirectory(prefix="clean-checkout-") as tmp:
        tree = Path(tmp) / "tree"
        tree.mkdir()
        archive = subprocess.run(
            ["git", "-C", str(ROOT), "archive", "HEAD"], capture_output=True
        )
        if archive.returncode != 0:
            print("FAIL  could not archive HEAD:")
            print("      " + archive.stderr.decode("utf-8", "replace").strip())
            return 1
        extract = subprocess.run(
            ["tar", "-x", "-C", str(tree)], input=archive.stdout, capture_output=True
        )
        if extract.returncode != 0:
            print("FAIL  could not extract the archived tree:")
            print("      " + extract.stderr.decode("utf-8", "replace").strip())
            return 1

        n = sum(1 for p in tree.rglob("*") if p.is_file())
        print(f"Clean checkout of HEAD extracted: {n} files, no .git, no untracked files.")
        print("This is what a reader receives. The gates below ran inside it.\n")

        failed = []
        for label, argv in GATES:
            print(f"--- {label} " + "-" * max(0, 58 - len(label)))
            if subprocess.call([sys.executable, *argv], cwd=tree) != 0:
                failed.append(label)

        print()
        if failed:
            print("FAIL  the clean checkout does not pass: " + ", ".join(failed))
            print()
            print("      The working folder may still pass, and that is the point:")
            print("      a gate that only ever sees the folder cannot see this.")
            return 1
        print("PASS  the clean checkout passes every gate it was given.")
        print(f"      {n} files, which is the number a reader gets.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
