#!/usr/bin/env python3
"""Land named files on ``main``, or refuse and say which check stopped it.

    python scripts/land.py -m "subject" -- README.md MANIFEST.txt
    python scripts/land.py -F message.txt -- path [path ...]
    python scripts/land.py --dry-run -m "..." -- path

**Why this exists, and it is a measured defect rather than a precaution.**
On 2026-10-31 a single session lost three commits to the same mechanism:

    git add -A -- README.md MANIFEST.txt OLD-NAME.tex

``git add`` with several pathspecs **aborts the entire call** when one path
does not match, and it does so while returning output that reads like
progress. The staged set was then whatever an earlier ``git mv`` had put
there, a guard that asked *was anything staged* passed on it, and the commit
went out carrying a rename with none of its content. Twice this left ``main``
internally inconsistent -- once with a document whose filename and title
block named different editions, once with a README pointing at a file that
had been renamed out from under it. A third time it deleted a handoff
artefact and landed nothing in its place.

The common shape is the one this bundle keeps finding elsewhere: **a check
that passes on the wrong thing is worse than no check**, because it spends
the attention that would have caught the error. ``was anything staged`` is
that check. ``is every file I named in the index`` is the one that works.

**So the contract here is: name every path, and the script proves each one
reached the commit.** It stages one path at a time so a failure names the
path that failed; it compares the index against the request as a set, so a
silent drop cannot survive; it runs the release gates before committing
rather than after; and it re-reads the pushed tree from the remote and
compares hashes, because every failure in that session was caught by the
hash check afterwards and none by the inspection before.

Exit status is 0 only when the named files are on ``origin/main`` with the
content they had on disk.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

GATES = [
    ("release hygiene", [sys.executable, "-I", "scripts/check_release_hygiene.py"]),
    ("README artefacts", [sys.executable, "-I", "-m", "pytest",
                          "tests/test_readme_artefacts.py", "-q"]),
]


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    kw.setdefault("text", True)
    return subprocess.run(cmd, capture_output=True, **kw)


def die(msg: str) -> None:
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-m", "--message", help="commit subject")
    ap.add_argument("-F", "--file", help="file holding the full commit message")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-missing", action="store_true",
                    help="permit a named path to be a deletion")
    ap.add_argument("paths", nargs="+")
    a = ap.parse_args()
    if not (a.message or a.file):
        die("no commit message: pass -m or -F")

    requested = [p.replace("\\", "/").rstrip("/") for p in a.paths]

    # 1. every named path must exist, unless it is explicitly a deletion.
    if not a.allow_missing:
        missing = [p for p in requested if not Path(p).exists()]
        if missing:
            die("named path(s) do not exist, which is how a renamed file "
                f"silently drops its content: {', '.join(missing)}")

    # 2. stage one at a time, so a failure names the path that failed.
    for p in requested:
        # -A so a named path that is a DELETION stages as one; a plain
        # `git add` fails on a path that no longer exists, which is the
        # abort this script exists to stop.
        r = run(["git", "add", "-A", "--", p])
        if r.returncode != 0:
            die(f"git add failed for {p}: {r.stderr.strip()}")

    # 3. the index must equal the request, as a set. This is the check that
    #    "was anything staged" is not.
    r = run(["git", "diff", "--cached", "--name-only"])
    if r.returncode != 0:
        die(f"cannot read the index: {r.stderr.strip()}")
    staged = {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}
    dropped = [p for p in requested if p not in staged]
    if dropped:
        die("named but NOT in the index after staging -- this is the defect "
            f"this script exists for: {', '.join(dropped)}")
    extra = sorted(staged - set(requested))
    if extra:
        die("in the index but NOT named; commit only what you named, so a "
            f"stray staged file cannot ride along: {', '.join(extra)}")
    if not staged:
        die("nothing staged")

    # 4. gates before the commit, not after.
    for name, cmd in GATES:
        if not Path(cmd[-1] if cmd[-1].endswith(".py") else cmd[-2]).exists():
            print(f"  skip  {name} (not in this tree)")
            continue
        g = run(cmd)
        if g.returncode != 0:
            tail = (g.stdout + g.stderr).strip().splitlines()[-12:]
            die(f"gate '{name}' is red:\n      " + "\n      ".join(tail))
        print(f"  pass  {name}")

    before = {p: sha256(Path(p)) for p in requested if Path(p).exists()}

    if a.dry_run:
        print("DRY RUN: index matches the request and the gates are green; "
              "nothing committed.")
        return 0

    msg = ["-F", a.file] if a.file else ["-m", a.message]
    c = run(["git", "commit", "-q", *msg])
    if c.returncode != 0:
        die(f"commit failed: {(c.stdout + c.stderr).strip()}")

    p = run(["git", "push", "origin", f"HEAD:{a.branch}"])
    if p.returncode != 0:
        die(f"push failed, commit is local only: {p.stderr.strip()}")

    # 5. re-read the pushed tree from the REMOTE and compare. Every failure
    #    in the session that motivated this script was caught here and none
    #    by the inspection beforehand.
    run(["git", "fetch", "--quiet", "origin"])
    bad = []
    for path, want in before.items():
        s = run(["git", "show", f"origin/{a.branch}:{path}"], text=False)
        if s.returncode != 0:
            bad.append(f"{path}: not on origin/{a.branch}")
            continue
        got = hashlib.sha256(s.stdout).hexdigest()
        if got != want:
            bad.append(f"{path}: remote {got[:16]} != local {want[:16]}")
    if bad:
        die("pushed, but the remote does not match what was on disk:\n      "
            + "\n      ".join(bad))

    print(f"LANDED on origin/{a.branch}, {len(before)} file(s), "
          "each verified by hash against the remote:")
    for path, want in sorted(before.items()):
        print(f"  {want[:16]}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
