r"""The README's artefact table must describe the tree it is in.

**This file exists because the README has drifted from the tree twice.** The
verification paragraph once claimed a test total that was 36 short and a
criteria tally that was half the truth, and finding **T-16** is about a label
that no longer named what it pointed at. A table of figures, evidence and
versions is exactly the shape of thing that goes stale quietly: nothing breaks,
it just stops being true.

So every row is checked against two sources that cannot both be edited by
accident --- `figures/` on disk and `scripts/run_all.py`'s own lists.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
RUN_ALL = (ROOT / "scripts" / "run_all.py").read_text(encoding="utf-8")

#: `| **F3** label | evidence | `v1.0.0` |` --- the drawn rows.
ROW = re.compile(
    r"^\|\s*\*\*(?P<tag>[FD]\d)\*\*[^|]*\|[^|]*\|\s*`(?P<version>v[\d.]+)`\s*\|$",
    re.M)

#: `| *F2* label | *not yet drawn* ... | — |` --- the undrawn ones.
DEFERRED_ROW = re.compile(r"^\|\s*\*(?P<tag>[FD]\d)\*[^|]*\|[^|]*\|\s*—\s*\|$", re.M)


def _rows() -> dict[str, str]:
    return {m.group("tag"): m.group("version") for m in ROW.finditer(README)}


def _deferred() -> set[str]:
    tags = set()
    for m in DEFERRED_ROW.finditer(README):
        tags.add(m.group("tag"))
    # the `*D3*, *D4*` row names two tags in one cell
    if re.search(r"^\|\s*\*D3\*,\s*\*D4\*", README, re.M):
        tags |= {"D3", "D4"}
    return tags


def test_the_table_is_not_empty():
    """A regex that matches nothing passes every test below it."""
    rows = _rows()
    assert len(rows) >= 10, (
        f"the README artefact table parsed to {len(rows)} rows. Either it has "
        "been removed or its formatting changed and this file's regex is now "
        "measuring nothing.")
    assert _deferred(), "no deferred rows parsed; the same hazard"


@pytest.mark.parametrize("tag,version", sorted(_rows().items()))
def test_every_drawn_artefact_exists_at_the_version_the_readme_states(tag, version):
    """A figure row must point at a file; a diagnostic row at its script."""
    if tag.startswith("F"):
        matches = list((ROOT / "figures").glob(f"{tag.lower()}-*-{version}.pdf"))
        assert matches, (
            f"README says {tag} is at {version}, and no "
            f"figures/{tag.lower()}-*-{version}.pdf exists. Either the figure "
            "was regenerated at a new version and the table was not updated, "
            "or the row names a figure that was never drawn.")
    else:
        assert re.search(rf'"{tag}\s', RUN_ALL), (
            f"README lists {tag} as a generated diagnostic, and run_all.py does "
            "not run it")


@pytest.mark.parametrize("tag", sorted(_deferred()))
def test_every_deferred_artefact_is_deferred_in_the_harness(tag):
    """The README may not call something deferred that the harness runs."""
    deferred_block = RUN_ALL[RUN_ALL.index("DEFERRED:"):RUN_ALL.index("DEFERRED_TO_V1_1")]
    assert re.search(rf'"{tag}\s', deferred_block), (
        f"README calls {tag} deferred and run_all.py's DEFERRED does not list "
        "it. If it has landed, the row moves into the drawn table with its "
        "version --- as F6 and F8 did, and as F5 did on 2026-10-14.")


def test_no_drawn_artefact_is_also_listed_as_deferred():
    """The two halves of the table must not disagree with each other."""
    overlap = set(_rows()) & _deferred()
    assert not overlap, f"listed as both drawn and deferred: {sorted(overlap)}"


def test_the_readme_does_not_claim_a_tag_that_does_not_exist():
    """**The rung is the claim, and it is the one the PI corrected.**

    A README saying *released as v1.1.0* while no `v1.1.0` tag exists reports
    the wrong rung, which is the thing decision **S27** is for. The tree says
    `v1.1.0-rc` until the tag lands; this asserts the two statements are not
    both present, so flipping one without the other fails.
    """
    claims_release = "**Released as v1.1.0.**" in README
    claims_rc = "**This tree is v1.1.0-rc.**" in README
    assert claims_release != claims_rc, (
        "the README must say exactly one of 'Released as v1.1.0' and 'This tree "
        "is v1.1.0-rc'. Promoting it is a two-line change --- this paragraph and "
        "the lineage table's last row --- plus the three v1.1.0 rungs in "
        "scripts/make_release_status.py.")
