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


def test_the_readme_states_the_git_check_rather_than_its_answer():
    r"""**Finding T-30.** Nothing in this repository can see git, so nothing in
    it may assert git state.

    The README said *"the tag is placed at the last commit whose content was
    v1.1.0"*. That was a plan written as an observation, and it went into a
    released file. The container running these tests has no access to the
    repository the README describes, so no test here could have caught it ---
    which is the point: **a claim no check can reach should be replaced by the
    check**. The README now carries the three commands instead of the answer.
    """
    for command in ("git tag --list v1.1.0",
                    "git log --oneline -1 v1.1.0",
                    "git merge-base --is-ancestor v1.1.0 HEAD"):
        assert command in README, (
            f"the README no longer tells the reader to run `{command}`. If the "
            "tag discussion has moved, move the commands with it --- do not "
            "replace them with an assertion about where the tag is, which is "
            "exactly finding T-30.")

    forbidden = "The tag is placed at the last commit whose content was"
    assert forbidden not in README, (
        "the README is asserting a tag position again (T-30)")


def test_the_readme_does_not_claim_a_tag_that_does_not_exist():
    """**The rung is the claim, and it is the one the PI corrected.**

    A README saying *released as v1.1.0* while no `v1.1.0` tag exists reports
    the wrong rung, which is the thing decision **S27** is for. The tree says
    `v1.1.0-rc` until the tag lands; this asserts the two statements are not
    both present, so flipping one without the other fails.
    """
    states = [
        "**Released as v1.1.0; this tree is v1.2.0-dev.**" in README,
        "**This tree is v1.1.0-rc.**" in README,
        "**Released as v1.1.0.**" in README,
    ]
    assert sum(states) == 1, (
        "the README must make exactly one claim about where the tree sits "
        f"relative to v1.1.0; it makes {sum(states)}. Moving between them is "
        "this paragraph, the lineage table's last rows, and the v1.1.0 rungs in "
        "scripts/make_release_status.py --- three places, which is why this "
        "test exists.")

    # And the claim must match the rungs the status file carries.
    status = (ROOT / "provenance" / "RELEASE-STATUS-v1.md").read_text(encoding="utf-8")
    if states[0] or states[2]:
        assert "## v1.1.0 — 3×S" in status, (
            "the README says v1.1.0 is released and the generated status still "
            "has its artefacts at a lower rung")
    if states[1]:
        assert "## v1.1.0 — 3×R" in status, (
            "the README says v1.1.0-rc and the status has already shipped it")


# --------------------------------------------------------------------------
# Version labels, which have now gone stale twice.
# --------------------------------------------------------------------------


def _tree_version_from(text: str, pattern: str) -> str:
    import re

    m = re.search(pattern, text, re.MULTILINE)
    assert m, f"no version matched {pattern!r}"
    return m.group(1)


def test_the_readme_and_the_supplement_name_the_same_tree_version():
    r"""The supplement moves **once**, at v1.2.0, so its date line is the single
    place a version label has to be flipped at tag time --- and a label flipped
    by hand is a label that drifts.

    It drifted twice before this test existed. On 2026-10-14 the README header
    still read ``Version: v1.1.0`` while its own verification section said
    ``this tree is v1.2.0-dev``, and the supplement's ``\date`` still read
    ``v1.0.0 --- First public analytical reproducibility release, 5 October
    2026`` after two releases and a rewritten frames section. Both were caught
    by the PI reading them, which is finding **T-16**'s lesson arriving by the
    only route the bundle had left open.

    **The file names are deliberately not checked.** The house convention is
    that a version suffix marks the release an artefact was *introduced* in ---
    `config-v1.7.7.json` survives into a v2.2.0 release in the exemplar --- so
    `SUPPLEMENTARY-MATERIAL-v1.0.0.tex` keeps its name while its content moves.
    What must agree is what the documents *say*, which is content.
    """
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    supplement = (ROOT / "SUPPLEMENTARY-MATERIAL-v1.0.0.tex").read_text(encoding="utf-8")

    header = _tree_version_from(readme, r"^Version:\s+\*\*(v[0-9.]+(?:-dev)?)\*\*")
    status = _tree_version_from(readme, r"this tree is (v[0-9.]+(?:-dev)?)")
    dated = _tree_version_from(supplement, r"\\date\{\\textbf\{(v[0-9.]+(?:-dev)?)\}")

    assert header == status == dated, (
        f"version labels disagree: README header {header!r}, README verification "
        f"status {status!r}, supplement date line {dated!r}. The supplement moves "
        f"once, at the release, so all three flip together or none do."
    )


def test_the_released_version_is_named_consistently_too():
    """The last *released* version is one statement, and it is made twice."""
    import re

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    header = re.search(r"\*\*Last release: (v[0-9.]+)\*\*", readme)
    status = re.search(r"\*\*Released as (v[0-9.]+);", readme)
    assert header and status, "the README must name its last release in both places"
    assert header.group(1) == status.group(1), (
        f"README header says the last release is {header.group(1)}, its verification "
        f"section says {status.group(1)}")

    # CITATION.cff is the one version statement a machine acts on: GitHub's
    # "Cite this repository" and Zenodo both read it, so a version there that is
    # not tagged asserts a release nobody can fetch. It tracks the *released*
    # version, never the tree's.
    cff = re.search(r'^version:\s*"([0-9.]+)"',
                    (ROOT / "CITATION.cff").read_text(encoding="utf-8"), re.MULTILINE)
    assert cff, "CITATION.cff has no version field"
    assert f"v{cff.group(1)}" == header.group(1), (
        f"CITATION.cff says {cff.group(1)}, the README says the last release is "
        f"{header.group(1)}. Zenodo reads the first of those.")
