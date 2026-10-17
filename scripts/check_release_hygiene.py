#!/usr/bin/env python3
r"""Refuse to ship a file nothing in this bundle can read or regenerate.

    python scripts/check_release_hygiene.py

**Finding T-50.** The v1.2.0 release archive shipped 198 files. The tree it was
cut from should have held 195. The three extra files were:

* `SUPPLEMENTARY-MATERIAL-v1.0.0.tex`, restored to satisfy **S36** by a
  PowerShell redirection, which writes **UTF-16LE with a BOM**. 51,622 bytes
  for ~25.8 kB of text. No LaTeX in the bundle can compile it and no `grep` in
  the bundle can read it.
* `supplementary-materials/figures-v1.0.0.tex`, **byte-identical** to
  `figures-v1.2.0.tex` --- v1.2.0 content under a v1.0.0 name, which is the
  **T-16** class in a generated artefact.
* `supplementary-materials/supplement-v1.0.0.pdf`, a rendering left behind when
  the build was repointed at the v1.2.0 source.

**Every gate passed over all three**, and the reason the first one got through
is worth stating because it is a defect in a gate rather than in a file.
`check_portability.py` tests for mixed line endings by counting ``b"\r\n"``
against ``b"\n"``. In UTF-16LE a CRLF is ``0D 00 0A 00``: the two bytes are
never adjacent, so the CRLF count is **zero** and the file presents as
uniformly LF. *A byte-level gate that assumes one byte per character cannot see
a wide encoding at all.* The rest of that script's checks are `.py`-only, so
nothing else looked.

Four checks here, and the first of them closes that hole:

1. **Every text file decodes as UTF-8 and contains no NUL byte.** This catches
   UTF-16 and UTF-32 with or without a BOM, and any binary that arrives under a
   text suffix. It is the encoding a reader on another machine will assume.
2. **The supplement's generated artefacts name the source the build is pointed
   at, and no other version.** Under **S36** the frozen artefact is the `.tex`
   and previous ones are kept; the *build outputs* are not, because the PDF of
   record for an earlier release is its release asset and archived DOI. So
   there is exactly one live rendering and one live figure-page include, and
   `scripts/_versions.py` says which.
3. **No consumer hardcodes a supplement filename.** The three artefacts' names
   were written literally into five files, which is why repointing the build
   left two of them behind. `scripts/_versions.py` derives all three from the
   README header; this refuses a string literal that goes around it.
4. **Every released caller of `build_environment` names its line-of-sight
   weight.** Added for **T-57**, where a field's documentation said one default
   and the code said the other, and eight figures and diagnostics ran for
   eleven days under the weighting approximation **A-2** says this bundle
   departs from. *The other three checks compare a file to a rule; this one
   compares a decision to its implementation*, which is the class of defect
   that had no instrument at all.

**What this deliberately does not check, and why.** An earlier draft also
refused any two bundle files that are byte-identical under different version
labels. It would have caught `figures-v1.0.0.tex` --- but check 2 already does,
exactly, and the duplicate rule needs three exemptions to be true: a supplement
source copied forward to open a release line is identical to its predecessor
until the work diverges, and a figure whose data did not move across a release
is legitimately redrawn to the same bytes. **A rule that needs carve-outs to be
true is a rule nobody will trust the next time it fires.** Two exact checks are
worth more than three approximate ones.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _bundle_files import BINARY_SUFFIXES, bundle_files  # noqa: E402
from _versions import (  # noqa: E402
    supplement_figures,
    supplement_pdf,
    supplement_source,
    supplement_version,
)

ROOT = Path(__file__).resolve().parents[1]

#: String literals that go around `_versions.py`. Scoped to exactly the three
#: supplement artefacts: `tables/equations-v1.0.0.tex` and its siblings keep
#: their suffixes under S36's *introduced-in* rule and are not this gate's
#: business.
HARDCODED = re.compile(
    r"(?:SUPPLEMENTARY-MATERIAL|supplement|figures)-v\d+\.\d+\.\d+")

#: The one module allowed to spell a supplement filename, plus this gate.
NAMING_AUTHORITY = frozenset({"scripts/_versions.py", "scripts/check_release_hygiene.py"})


def check_encoding(failures: list[str]) -> int:
    """Every text file decodes as UTF-8, and no text file contains a NUL."""
    checked = 0
    for path in bundle_files(ROOT):
        if path.suffix in BINARY_SUFFIXES:
            continue
        checked += 1
        raw = path.read_bytes()
        rel = path.relative_to(ROOT).as_posix()
        if b"\x00" in raw:
            if raw[:4] in (b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff"):
                width = "UTF-32"
            elif raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
                width = "UTF-16"
            elif raw[1::2].count(0) * 2 >= len(raw) - 1 or raw[::2].count(0) * 2 >= len(raw) - 1:
                width = "UTF-16, no BOM"
            else:
                width = "unknown encoding"
            failures.append(
                f"{rel}: contains NUL bytes ({width} encoded, {len(raw)} bytes). "
                "Nothing in this bundle reads it, and the mixed-line-ending "
                "check cannot see it --- T-50. Re-save as UTF-8: on Windows "
                "PowerShell, `Out-File -Encoding utf8` or `git show` piped "
                "through `Set-Content -Encoding utf8`, never a bare `>`.")
            continue
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"{rel}: not valid UTF-8 at byte {exc.start} ({exc.reason})")
    return checked


def check_supplement_set(failures: list[str]) -> str:
    """Exactly one live rendering and one live figure include, named for the source."""
    live = supplement_version(ROOT)
    source = supplement_source(ROOT)

    if not source.exists():
        failures.append(
            f"{source.relative_to(ROOT).as_posix()}: the README header says this "
            f"tree is v{live} and the supplement it names does not exist. Open "
            "the release line with `bump_release.py --open`, which copies the "
            "previous one forward rather than leaving the build pointed at a "
            "frozen document.")

    directory = ROOT / "supplementary-materials"
    for pattern, expected in ((f"supplement-v*.pdf", supplement_pdf(ROOT)),
                              (f"figures-v*.tex", supplement_figures(ROOT))):
        for found in sorted(directory.glob(pattern)):
            if found != expected:
                failures.append(
                    f"{found.relative_to(ROOT).as_posix()}: a build output left "
                    f"behind when the build was repointed at v{live}. Under S36 "
                    "the frozen artefact is the `.tex`; the rendering of record "
                    "for an earlier release is its release asset and archived "
                    "DOI, not a stale file in this tree. Remove it.")
    return f"      supplement set is v{live}, and only v{live}."


def check_no_hardcoded_names(failures: list[str]) -> int:
    """No `.py` file but `_versions.py` may spell a supplement artefact's name.

    A docstring that *mentions* a filename is prose and is fine --- this walks
    the AST and looks only at string literals that are not the docstring of a
    module, class or function, which is the same instrument
    `scripts/make_grid_register.py` uses to find discretisations.
    """
    scanned = 0
    for path in sorted(bundle_files(ROOT)):
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix != ".py" or rel in NAMING_AUTHORITY:
            continue
        scanned += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except (UnicodeDecodeError, SyntaxError, ValueError):
            # `check_encoding` has already reported this file, and a gate that
            # dies on the defect it is meant to name reports nothing at all.
            # **A gate must survive its own subject matter** --- the UTF-16
            # file of T-50 raised `SyntaxError: source code string cannot
            # contain null bytes` out of `ast.parse` and took the whole run's
            # output with it.
            continue
        docstrings = {
            id(node.body[0].value)
            for node in ast.walk(tree)
            if isinstance(node, (ast.Module, ast.ClassDef,
                                 ast.FunctionDef, ast.AsyncFunctionDef))
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        }
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and id(node) not in docstrings
                    and HARDCODED.search(node.value)):
                failures.append(
                    f"{rel}:{node.lineno}: spells a supplement filename as a "
                    "string literal. Import it from `scripts/_versions.py` "
                    "instead --- six copies of this name is why the v1.2.0 "
                    "archive carried two stale ones (T-50).")
    return scanned


def check_weight_is_stated(failures: list[str]) -> int:
    r"""Every released caller of `build_environment` names its line-of-sight weight.

    **Finding T-57.** Approximation **A-1** records the governance rule in
    words --- *"Both weightings implemented; the caller states which"* --- and
    for eleven days no caller stated it. `TwoFrameEnvironment`'s own field
    documentation said *"`"opacity"` is therefore the default"* while the line
    under it read ``= "printed"``, so all eight released callers silently took
    $\mathcal V=\kappa'e^{-\kappa}$: the weighting **A-2** says this bundle
    departs from, and under which the rank-one Doppler sector is 100.5% of the
    transfer at every $2\le\ell\le100$ and there is no Sachs--Wolfe plateau.

    **The gap was between prose and a default, so no gate could see it.** The
    manifests hash content, `check_portability` reads bytes, the regression
    suite compares a route against itself, and criterion 5b holds the weight
    *fixed on both sides* and therefore cannot see which one it fixed. Nothing
    in the bundle compared a decision to its implementation, because a decision
    recorded only in English is not comparable to anything.

    This is the smallest instrument that would have caught it: make the
    argument appear at the call site, where a reader of F9 can see which
    approximation F9 ran under without opening `two_frame.py`. It is the same
    move as `Weighting` having no default in `pipeline.run` and `weight` having
    none in `integral_solution`, applied to the one entry point that was
    written after those and did not inherit the habit.
    """
    stated = 0
    for path in sorted(bundle_files(ROOT)):
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix != ".py" or not rel.startswith("scripts/"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except (UnicodeDecodeError, SyntaxError, ValueError):
            continue        # already reported by `check_encoding`
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = (func.id if isinstance(func, ast.Name)
                    else func.attr if isinstance(func, ast.Attribute) else None)
            if name != "build_environment":
                continue
            if any(kw.arg == "line_of_sight_weight" for kw in node.keywords):
                stated += 1
                continue
            failures.append(
                f"{rel}:{node.lineno}: calls build_environment without naming "
                "line_of_sight_weight, so it takes the default and the figure "
                "does not say which approximation it ran under. A-1 requires "
                "the caller to state it; T-57 is what happened when nothing "
                "enforced that. Pass line_of_sight_weight='opacity' (e^-kappa, "
                "as (98) prints it and A-2 adopts) or ='printed' (V, as (178) "
                "prints it) deliberately.")
    return stated


def main() -> int:
    failures: list[str] = []
    checked = check_encoding(failures)
    note = check_supplement_set(failures)
    scanned = check_no_hardcoded_names(failures)
    stated = check_weight_is_stated(failures)

    if failures:
        print(f"FAIL  {len(failures)} release-hygiene problem(s):")
        for line in failures:
            print(f"      {line}")
        print()
        print("      A file the bundle cannot read is not evidence, and a build")
        print("      output whose source has moved is a label that no longer")
        print("      names what it points at. Neither may enter an archive.")
        return 1

    print(f"PASS  {checked} text files are UTF-8 with no NUL bytes; "
          f"{scanned} scripts name no supplement directly")
    print(note)
    print(f"      {stated} released callers of build_environment name their "
          f"line-of-sight weight (A-1, T-57).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
