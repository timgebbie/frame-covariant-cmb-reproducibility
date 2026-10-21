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


def supplement_version(root: Path) -> str:
    r"""The version the **live** supplement is named for, e.g. ``"1.3.0"``.

    The tree version with any ``-dev`` removed. A supplement in preparation for
    v1.3.0 is `SUPPLEMENTARY-MATERIAL-v1.3.0.tex` from the day the line opens:
    under decision **S36** each release freezes its own supplement, so the name
    is settled when the work starts and the `\date` line carries the ``-dev``
    until the release flips it.
    """
    return tree_version(root).removesuffix("-dev")


def supplement_source(root: Path) -> Path:
    """The `.tex` this release is written in. Previous ones are frozen beside it."""
    return root / f"SUPPLEMENTARY-MATERIAL-v{supplement_version(root)}.tex"


def supplement_pdf(root: Path) -> Path:
    """The rendering `scripts/build_supplement.py` writes. **Exactly one exists.**

    Under **S36** the frozen artefact is the `.tex`; the build outputs are not
    kept, because the PDF of record for a previous release is its release asset
    and its archived DOI rather than a stale file in the working tree.
    """
    return root / "supplementary-materials" / f"supplement-v{supplement_version(root)}.pdf"


def supplement_figures(root: Path) -> Path:
    """The generated figure pages `scripts/make_figure_pages.py` writes."""
    return root / "supplementary-materials" / f"figures-v{supplement_version(root)}.tex"
