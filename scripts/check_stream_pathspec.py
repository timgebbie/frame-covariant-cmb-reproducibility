#!/usr/bin/env python3
r"""Refuse a commit that writes another stream's file. **Finding T-168.**

**Why this exists, and it is not a policy document.** On 2026-10-28 P1-B
edited `handoff/P1T-to-P1B.md` --- P1-T's queue, one writer by the channel's
own rule --- to repair six rendering defects, and disclosed it in a commit
message rather than in the channel P1-T reads. The reasoning was that
rendering is P1-B's remit, which justifies the repair being P1-B's to make and
does **not** justify making it in someone else's file.

The same stream had, two days earlier, replaced a three-list registry in
`tests/frame/gen_theory_audit.py` with a glob, on the argument that *a rule
three lists be kept in step is kept only by someone remembering, and the note
was written because the remembering had already failed*. That argument is
correct and it applies here: **a one-writer rule enforced by discipline is
enforced until the first time it is inconvenient.**

So it is a gate. Run it before every commit.

USAGE
-----
    python scripts/check_stream_pathspec.py --stream P1B
    python scripts/check_stream_pathspec.py --stream P1B --allow handoff/P1T-to-P1B.md

`--allow` narrows rather than disables: a crossing has to be **named**, once,
on the command line, which makes it a deliberate act with a disclosure
attached rather than a flag that turns the gate off. There is no `--force`.
"""
from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: What each stream must **not** write. Patterns are `fnmatch` against paths
#: relative to the bundle root.
#:
#: The handoff pair is the channel's one-writer rule: each stream reads the
#: other's file and answers in its own, citing the identifier. `docs/STREAMS.md`
#: and `docs/RESUME.md` are Coordination's outright --- *"Do not write
#: `docs/STREAMS.md` or `docs/RESUME.md`"*, standing since the channel opened.
#: `tests/frame/` is P1-T's pathspec.
#: `README.md` moved to **P1-T** on 2026-10-28 by the PI's grant, recorded in
#: `docs/STREAMS.md` at `a0c8057`: the line declaring the live supplement
#: edition can be invalidated only by a P1-T action, so the dependency and the
#: custody ran in opposite directions and the download link died twice in one
#: morning. **This table was written the same day and already had it wrong** —
#: which is the gate's own lesson arriving immediately: a custody map kept in
#: two places is kept in neither, and the only reason it was caught is that
#: `a0c8057` landed on a fetch between a rebase and a push.
FORBIDDEN: dict[str, tuple[str, ...]] = {
    "P1B": ("handoff/P1T-to-P1B.md", "docs/STREAMS.md", "docs/RESUME.md",
            "tests/frame/*", "README.md", "supplementary-materials/*"),
    "P1T": ("handoff/P1B-to-P1T.md", "docs/STREAMS.md", "docs/RESUME.md"),
}

#: Why each one belongs to someone else, printed with the refusal so the
#: message says what to do instead rather than only what was refused.
WHOSE = {
    "handoff/P1T-to-P1B.md": "P1-T's queue. Raise it in handoff/P1B-to-P1T.md "
                             "as an item instead, citing the identifier.",
    "handoff/P1B-to-P1T.md": "P1-B's queue. Raise it in handoff/P1T-to-P1B.md "
                             "as an item instead, citing the identifier.",
    "docs/STREAMS.md": "Coordination's. Ask there; do not write it.",
    "docs/RESUME.md": "Coordination's. Ask there; do not write it.",
    "tests/frame/*": "P1-T's pathspec.",
    "supplementary-materials/*": "P1-T's, per docs/CUSTODY.md. The PDF is a "
                                 "build output P1-B produces, but the "
                                 "directory and its sources are P1-T's -- "
                                 "raise it in handoff/P1B-to-P1T.md.",
    "README.md": "P1-T's since 2026-10-28. Raise it in handoff/P1B-to-P1T.md; "
                 "the supplement line is the exception Coordination carved, "
                 "and it travels with the supplement move, not on its own.",
}


def touched(root: Path) -> list[str]:
    """Paths the working tree has modified, staged or not, plus untracked."""
    out = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain",
         "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if out.returncode != 0:
        raise SystemExit(
            "    FAIL  not a git repository, so the gate cannot see what "
            "changed.\n          A gate that cannot read its input must "
            "refuse rather than pass.")
    paths = []
    for line in out.stdout.splitlines():
        if not line.strip():
            continue
        rest = line[3:]
        # a rename prints 'old -> new'; the new path is the one written
        paths.append(rest.split(" -> ")[-1].strip().strip('"'))
    return paths


def offending(paths, stream: str, allow) -> list[tuple[str, str]]:
    allowed = set(allow or ())
    bad = []
    for p in paths:
        if p in allowed:
            continue
        for pattern in FORBIDDEN[stream]:
            if fnmatch.fnmatch(p, pattern):
                bad.append((p, WHOSE.get(pattern, "another stream's.")))
                break
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stream", required=True, choices=sorted(FORBIDDEN))
    ap.add_argument("--allow", action="append", default=[],
                    help="a path this commit crosses into deliberately; "
                         "name it here and disclose it in your handoff file")
    args = ap.parse_args()

    bad = offending(touched(ROOT), args.stream, args.allow)
    if not bad:
        print(f"    PASS  {args.stream} has written only its own files."
              + (f"  ({len(args.allow)} crossing(s) named)" if args.allow else ""))
        return 0

    print(f"    FAIL  {args.stream} has modified {len(bad)} file(s) it does "
          f"not own:\n")
    for path, whose in bad:
        print(f"          {path}\n              {whose}")
    print("""
          One writer per file. A repair that is yours to MAKE is not
          thereby yours to make IN SOMEONE ELSE'S FILE.

          If the crossing is deliberate, name it:
              --allow <path>
          and disclose it in your own handoff file, where the other stream
          reads --- not only in a commit message, where it does not.
""")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
