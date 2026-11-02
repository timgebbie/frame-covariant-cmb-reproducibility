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
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: **The authority is the `custody` block in `docs/CUSTODY.md`, and this
#: file READS it rather than restating it. T-188.**
#:
#: Until 2026-11-02 this gate carried its own `FORBIDDEN` table, and its own
#: comment already recorded why that was wrong: *"a custody map kept in two
#: places is kept in neither."* P1-B raised exactly that to Coordination as
#: `P1B->COORD 2026-10-30 #2` --- should the gate encode the table, or read a
#: machine-readable form? --- naming three earlier instances of the same
#: failure: `gen_theory_audit.py`'s registries, T-125's two continuations, and
#: T-174's staged directory list. Coordination answered by publishing the
#: block, and by the time the answer landed the restated table had already
#: drifted: it lacked `source/`, `handoff/P1T-to-coordination.md` and
#: `docs/CUSTODY.md`. **The second copy failed in the four days it took to ask
#: whether to keep it.**
#:
#: Semantics are the block's own and are not reinterpreted here: one writer
#: per path; the most specific pattern wins, which is how `tests/frame/**`
#: carves out of `tests/**`; and **an unlisted path is UNASSIGNED --- warn, do
#: not refuse.** Where the block has a gap the gate reports it, and the repair
#: is to the block, which is Coordination's. Re-hardcoding a refusal here
#: would be the second copy again.
CUSTODY_DOC = ROOT / "docs" / "CUSTODY.md"

#: The block's owner names, against the CLI's stream names. The CLI keeps
#: `P1B` / `P1T` because P1-T's instructions already say `--stream P1T`.
STREAMS = {"P1B": "P1-B", "P1T": "P1-T"}

#: Where a crossing should be raised instead, by owner --- printed with each
#: refusal so the message says what to do rather than only what was refused.
RAISE_IN = {
    "P1-T": "P1-T's. Raise it in handoff/P1B-to-P1T.md as an item, citing "
            "the identifier.",
    "P1-B": "P1-B's. Raise it in handoff/P1T-to-P1B.md as an item, citing "
            "the identifier.",
    "COORD": "Coordination's. Raise it in your own handoff file to "
             "Coordination; the reply is the policy change itself.",
    "FROZEN": "Frozen. No stream writes it.",
}


def custody_rules(path: Path = CUSTODY_DOC) -> list[tuple[str, str]]:
    """`(owner, pattern)` pairs from the ```custody block, in file order.

    **Refuses rather than returning nothing when the block cannot be read.**
    A gate whose authority is unreadable would otherwise pass every path as
    unassigned and print a cheerful warning --- the same failure as a gate
    that cannot see `git status`, refused for the same reason.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"    FAIL  cannot read {path}: {exc}\n"
                         "          A gate that cannot read its authority "
                         "must refuse rather than pass.")
    m = re.search(r"^```custody\n(.*?)^```", text, re.S | re.M)
    if not m:
        raise SystemExit(f"    FAIL  no ```custody block in {path}.\n"
                         "          A gate that cannot read its authority "
                         "must refuse rather than pass.")
    rules = []
    for line in m.group(1).splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            owner, pattern = line.split(None, 1)
            rules.append((owner, pattern.strip()))
    if not rules:
        raise SystemExit("    FAIL  the custody block is empty.")
    return rules


def _specificity(pattern: str) -> tuple[int, int]:
    """Literal path segments before the first wildcard, then length.

    `tests/frame/**` scores 2 and `tests/**` scores 1, so the carve-out wins
    whichever order the block lists them in.
    """
    n = 0
    for seg in pattern.split("/"):
        if any(c in seg for c in "*?["):
            break
        n += 1
    return (n, len(pattern))


def owner_of(path: str, rules) -> tuple[str | None, str | None]:
    """`(owner, matching pattern)`, or `(None, None)` when unassigned."""
    hits = [(_specificity(p), o, p) for o, p in rules
            if fnmatch.fnmatch(path, p)]
    if not hits:
        return None, None
    _, owner, pattern = max(hits)
    return owner, pattern


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


def classify(paths, stream: str, allow, rules):
    """`(refused, unassigned)`: what the stream may not write, and what nobody
    owns. Refused entries carry the message saying where to raise it."""
    me = STREAMS[stream]
    allowed = set(allow or ())
    refused, unassigned = [], []
    for p in paths:
        if p in allowed:
            continue
        owner, _ = owner_of(p, rules)
        if owner is None:
            unassigned.append(p)
        elif owner != me:
            refused.append((p, RAISE_IN.get(owner, f"{owner}'s.")))
    return refused, unassigned


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stream", required=True, choices=sorted(STREAMS))
    ap.add_argument("--allow", action="append", default=[],
                    help="a path this commit crosses into deliberately; "
                         "name it here and disclose it in your handoff file")
    args = ap.parse_args()

    rules = custody_rules()
    refused, unassigned = classify(touched(ROOT), args.stream, args.allow,
                                   rules)
    for p in unassigned:
        print(f"    WARN  {p} is UNASSIGNED in docs/CUSTODY.md's custody "
              f"block. Not refused --- the block says warn --- but the gap "
              f"is Coordination's to close.")
    if not refused:
        print(f"    PASS  {args.stream} has written only its own files."
              + (f"  ({len(args.allow)} crossing(s) named)" if args.allow
                 else ""))
        return 0

    print(f"    FAIL  {args.stream} has modified {len(refused)} file(s) it "
          f"does not own:\n")
    for path, whose in refused:
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
