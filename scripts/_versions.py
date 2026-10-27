#!/usr/bin/env python3
r"""One definition of *which version this tree is*, shared by every consumer.

**Why this module exists, and it is the same reason `_bundle_files.py` does.**
The name of the live supplement --- the one document this bundle is *for* ---
was written literally into six files: `scripts/build_supplement.py` (twice),
`scripts/make_figure_pages.py` (twice), `scripts/bump_release.py`,
`tests/test_translations.py` and `tests/test_readme_artefacts.py`. Opening a
release line therefore meant six hand edits in five files, which is precisely
the shape of defect `bump_release.py` was written to remove from the *other*
end of a release.

It cost exactly what that shape always costs. On 2026-10-16, between the
v1.2.0 tag and the tree being reopened, `supplementary-materials/` carried four
files where it should have carried two: `figures-v1.0.0.tex` byte-identical to
`figures-v1.2.0.tex`, and `supplement-v1.0.0.pdf` built from a source that had
since been renamed. Both were committed, both entered the released archive, and
**every gate in the bundle passed over them** --- see finding **T-50**.

So the version is read, once, from the two files that are allowed to state it:

* `CITATION.cff` carries the **released** version. It is the one version
  statement a machine acts on --- GitHub's *Cite this repository*
  both read it --- so a version there that is not tagged asserts a release
  nobody can fetch. See `bump_release.py`.
* `README.md`'s header carries the **tree** version, which during development
  is `vX.Y.Z-dev` and at a release is `vX.Y.Z`. Three statements in the README
  must agree about it and `tests/test_readme_artefacts.py` checks that they do.

Everything else is derived here. **No consumer may hardcode a version**, and
`scripts/check_release_hygiene.py` is the gate that refuses one.
"""

from __future__ import annotations

import re
from pathlib import Path

__all__ = [
    "release_line",
    "released_version",
    "supplement_figures",
    "supplement_pdf",
    "supplement_source",
    "supplement_version",
    "tree_version",
]


def released_version(root: Path) -> str:
    """The last released version, bare, e.g. ``"1.2.0"``.

    Read from `CITATION.cff`, which tracks the *released* version and never the
    tree's. Raises rather than guessing: a release archive named from a default
    frozen into the code is finding **T-49**.
    """
    text = (root / "CITATION.cff").read_text(encoding="utf-8")
    found = re.search(r'^version:\s*"([0-9]+\.[0-9]+\.[0-9]+)"', text, re.MULTILINE)
    if not found:
        raise RuntimeError(
            "CITATION.cff has no `version: \"X.Y.Z\"` field. It is the version "
            "statement GitHub reads; nothing here may substitute a "
            "default for it.")
    return found.group(1)


def tree_version(root: Path) -> str:
    """What this tree calls itself, e.g. ``"1.3.0-dev"`` or ``"1.2.0"``.

    Read from the README header. That header is one of three places the README
    states the tree version and `tests/test_readme_artefacts.py` requires all
    three to agree, so reading any one of them is reading all of them.
    """
    text = (root / "README.md").read_text(encoding="utf-8")
    found = re.search(r"^Version:\s+\*\*v([0-9]+\.[0-9]+\.[0-9]+(?:-dev)?)\*\*",
                      text, re.MULTILINE)
    if not found:
        raise RuntimeError(
            "README.md has no `Version: **vX.Y.Z**` header line. That line is "
            "where this tree says what it is.")
    return found.group(1)


def release_line(root: Path) -> str:
    """The **computational** release this tree is on, e.g. ``"1.3.0"``.

    The tree version with any ``-dev`` removed. It names the artefacts the
    *code* produces, and it is **not** the supplement's version --- see below.
    """
    return tree_version(root).removesuffix("-dev")


def supplement_version(root: Path) -> str:
    r"""The version the **live supplement** is named for, e.g. ``"1.3.17"``.

    **Read from the README's own `Supplement:` line, which is a second version
    statement and not a restatement of the first.**

    It used to be `tree_version()` with the ``-dev`` removed, on the reading
    that a supplement belongs to a release and therefore shares its number.
    That held while the two happened to agree and stopped holding the moment
    they did not: by 2026-10-26 the computational line was still ``v1.3.0-dev``
    --- the physics had not shipped --- while the supplement had been through
    **seventeen** editions, because a document under daily revision earns a
    number per revision and a release does not. The constructed name then
    pointed at `SUPPLEMENTARY-MATERIAL-v1.3.0.tex`, which had left the tree,
    and **eight tests failed on one cause**: six could not open the file, and
    the two that checked the README's link were comparing it against a name
    nothing had ever written.

    **Neither convention was wrong; coupling them was.** A supplement edition
    records a documentation gate and asserts nothing about whether the physics
    release has advanced, so the two lines are declared separately in the
    README and read separately here.

    This is the third repair of one shape in two days --- `tests/frame/` held a
    hand-written registry of instruments, `scripts/_fingerprint.py` digested
    the path rather than the code, and this constructed a filename it could
    have read. Each time the fix is the same: **take the fact from the one
    place entitled to state it, rather than deriving it from something that
    usually agrees.**
    """
    text = (root / "README.md").read_text(encoding="utf-8")
    found = re.search(r"^Supplement:\s+\*\*v([0-9]+\.[0-9]+\.[0-9]+)\*\*",
                      text, re.MULTILINE)
    if not found:
        raise RuntimeError(
            "README.md has no `Supplement: **vX.Y.Z**` line. That line is "
            "where the live supplement's edition is declared, and it is a "
            "separate statement from the `Version:` header: the computational "
            "release and the supplement edition advance independently and "
            "deriving one from the other is the defect this function was "
            "rewritten to remove.")
    return found.group(1)


def supplement_source(root: Path) -> Path:
    """The `.tex` the live edition is written in, named for that edition."""
    return root / f"SUPPLEMENTARY-MATERIAL-v{supplement_version(root)}.tex"


def supplement_pdf(root: Path) -> Path:
    """The rendering `scripts/build_supplement.py` writes. **Exactly one exists.**

    Under **S36** the frozen artefact is the `.tex`; the build outputs are not
    kept, because the PDF of record for a previous release is its release asset
    and its archived DOI rather than a stale file in the working tree. The name
    follows the source it was built from, which from v1.3.14 is the full
    `SUPPLEMENTARY-MATERIAL-` stem rather than the old `supplement-` one.
    """
    return (root / "supplementary-materials"
            / f"SUPPLEMENTARY-MATERIAL-v{supplement_version(root)}.pdf")


def supplement_figures(root: Path) -> Path:
    """The generated figure pages, named for the **computational** release.

    **Retired at v1.3.14 and kept as a path so the gate can refuse it.** The
    supplement became a single file carrying its figure pages inline, so
    nothing inputs this any more --- and `scripts/make_figure_pages.py` went on
    writing it, which is how `figures-v1.3.0.tex` entered the released archive
    on 2026-10-26 and then made the supplement's own PDF read as stale against
    a source it does not have. It is named from `release_line()` and not from
    the supplement edition because it was always an output of the *code*.
    """
    return root / "supplementary-materials" / f"figures-v{release_line(root)}.tex"
