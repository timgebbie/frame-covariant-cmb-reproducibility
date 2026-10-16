#!/usr/bin/env python3
r"""Every discretisation in the bundle, found in the code and checked against the register.

    python scripts/make_grid_register.py

**What this closes.** Three findings in eight days were one failure, not three:
`n_eta` fixed rather than derived (**T-3**), the $k$ grid guarded by a comment
rather than by code (**S24**'s correction to itself), and the recombination grid
setting the primary source with nothing guarding it (**T-46**, question
**Q7**). Each was fixed where it was found. Fixing a third instance does not
stop a fourth.

So this does not fix an instance. It **walks the AST** of `functions/` and
`scripts/` for every `linspace`, `arange`, `logspace` and `geomspace`, joins the
sites against `config/grid-register.toml`, and **fails** when the code holds a
grid the register does not name or the register names one the code no longer
has. Adding a grid without saying what is known about it stops being possible.

That is the same argument `scripts/_bundle_files.py` makes about the file set and
`scripts/make_release_status.py` makes about the maturity ladder: **one
definition, enforced, rather than two descriptions that drift.**

The register is not a claim that every grid is fine. One row is `open`, says so,
and carries the measurement and the decision that owns it.
"""

from __future__ import annotations

import ast
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: The constructors that make a grid. `zeros`/`empty` are not here: they make an
#: array, not a discretisation of something continuous.
CONSTRUCTORS = frozenset({"linspace", "arange", "logspace", "geomspace"})

SEARCH = ("functions", "scripts")

STATUS_ORDER = ["open", "derived", "measured", "described", "index"]

STATUS_BLURB = {
    "open": ("**open**", "a chosen literal whose convergence is **not** "
             "established. This status is the point of the register."),
    "derived": ("**derived**", "computed from a physical scale by code that "
                "**raises** if the scale cannot be met. The only status that "
                "cannot silently degrade."),
    "measured": ("**measured**", "a chosen literal whose convergence has been "
                 "measured, with the number stated."),
    "described": ("**described**", "a chosen literal governed by a stated "
                  "rule, with a guard elsewhere that can fail."),
    "index": ("**index**", "an exact integer or index array — not a "
              "discretisation. Listed so the exclusion is on the record "
              "rather than by nobody looking."),
}


def _sites() -> dict[str, tuple[str, int, str]]:
    """Every grid-constructing call in the tree, keyed `path::name`.

    Keyed by the **assignment target**, not the line number: line numbers move,
    and a register that drifts against the code is worse than no register.
    """
    found: dict[str, tuple[str, int, str]] = {}
    for folder in SEARCH:
        for path in sorted((ROOT / folder).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            parent: dict[ast.AST, ast.AST] = {}
            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    parent[child] = node
            rel = path.relative_to(ROOT).as_posix()
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr in CONSTRUCTORS):
                    continue
                name, walk = None, node
                while walk in parent:
                    walk = parent[walk]
                    if isinstance(walk, ast.Assign):
                        target = walk.targets[0]
                        name = getattr(target, "id", None) or getattr(target, "attr", None)
                        break
                    if isinstance(walk, ast.AnnAssign):
                        name = getattr(walk.target, "id", None)
                        break
                    if isinstance(walk, (ast.FunctionDef, ast.AsyncFunctionDef,
                                         ast.Module)):
                        break
                if name is None:
                    # An unassigned grid is an inline expression. It is still a
                    # discretisation and still has to be registered, so it is
                    # keyed by its line and will read oddly in the register
                    # until someone names it --- which is the nudge intended.
                    name = f"<inline:{node.lineno}>"
                found[f"{rel}::{name}"] = (rel, node.lineno, node.func.attr)
    return found


def main() -> int:
    register = tomllib.loads(
        (ROOT / "config" / "grid-register.toml").read_text(encoding="utf-8"))
    rows = {entry["key"]: entry for entry in register["grid"]}
    sites = _sites()

    unregistered = sorted(set(sites) - set(rows))
    orphaned = sorted(set(rows) - set(sites))
    bad_status = sorted(k for k, r in rows.items()
                        if r["status"] not in STATUS_BLURB)

    print(f"grid register: {len(sites)} discretisations in "
          f"{len(SEARCH)} trees, {len(rows)} registered")

    if unregistered or orphaned or bad_status:
        for key in unregistered:
            rel, line, kind = sites[key]
            print(f"  UNREGISTERED  {key}  ({kind}, {rel}:{line})")
        for key in orphaned:
            print(f"  ORPHANED      {key} is registered and no longer exists")
        for key in bad_status:
            print(f"  BAD STATUS    {key}: {rows[key]['status']!r}")
        print("\nFAIL  A grid the register does not name is the fourth instance "
              "of T-3 waiting to happen. Register it with what is known about "
              "it --- `open` is a permitted and sometimes the honest answer.")
        return 1

    counts = {s: sum(1 for r in rows.values() if r["status"] == s)
              for s in STATUS_ORDER}
    lines = [
        "# Grid register — every discretisation, and what is known about it",
        "",
        "**Generated by `scripts/make_grid_register.py` from "
        "`config/grid-register.toml`. Do not edit by hand.**",
        "",
        "Three findings in eight days were one failure, not three: `n_eta` "
        "fixed rather than",
        "derived (**T-3**), the $k$ grid guarded by a comment rather than by "
        "code (**S24**'s",
        "correction to itself), and the recombination grid setting the primary "
        "source with",
        "nothing guarding it (**T-46**, **Q7**). Each was fixed where it was "
        "found, and fixing",
        "a third instance does not stop a fourth.",
        "",
        "So the generator walks the AST for every `linspace`, `arange`, "
        "`logspace` and",
        "`geomspace` in `functions/` and `scripts/`, and **fails** when the "
        "code holds a grid",
        "this register does not name. Adding one without saying what is known "
        "about it stops",
        "being possible.",
        "",
        "**This is not a claim that every grid is fine.** One row is `open` and "
        "says so.",
        "",
        "| status | count | means |",
        "|---|---|---|",
    ]
    for status in STATUS_ORDER:
        label, blurb = STATUS_BLURB[status]
        lines.append(f"| {label} | {counts[status]} | {blurb} |")
    lines.append("")

    for status in STATUS_ORDER:
        here = [r for r in register["grid"] if r["status"] == status]
        if not here:
            continue
        label, _ = STATUS_BLURB[status]
        lines += [f"## {label.strip('*')} — {len(here)}", ""]
        for entry in sorted(here, key=lambda r: r["key"]):
            rel, line, kind = sites[entry["key"]]
            name = entry["key"].split("::", 1)[1]
            lines += [
                f"### `{name}` — {entry['what']}",
                "",
                f"`{rel}:{line}`, `np.{kind}`",
                "",
                entry["note"].strip(),
                "",
            ]

    out = ROOT / "provenance" / "GRID-REGISTER-v1.md"
    # `newline="\n"` is not optional and not cosmetic. Without it Python's text
    # mode writes CRLF on Windows, so the same checkout generates a different
    # file on the PI's machine than on this one --- which is exactly the
    # cross-platform property `PORTABLE-MANIFEST` exists to guarantee, and
    # exactly what finding **T-15** is about. Every other generator in this
    # bundle passes it. This one did not, and finding **T-48** is the result:
    # the script written to close a defect class shipped an instance of
    # another one.
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"  " + ", ".join(f"{counts[s]}x{s}" for s in STATUS_ORDER if counts[s]))
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
