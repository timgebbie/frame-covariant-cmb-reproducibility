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
#:
#: **`\d+`, not `\d`, and that was a real hole.** Until 2026-10-25 this read
#: `[FD]\d`, so `**D10**` matched `D1` and then failed on the `0` where `\*\*`
#: was required --- and the row was **silently skipped**. Every two-digit
#: artefact in the table, D10 through D18, was unchecked for a month while
#: `test_the_table_is_not_empty` went on passing on the fifteen single-digit
#: rows. That is the class of defect this file was written to catch, in this
#: file: a gate that cannot see most of what it claims to cover, and nothing
#: breaking to say so. The `>= 10` floor below is exactly why it stayed quiet.
#:
#: `CELL` is "anything up to an **unescaped** pipe", not `[^|]*`. D9's evidence
#: cell contains the antecedent's own `\|r_θ/r_s\| jπ`, and `[^|]*` stops dead
#: at the first `\|` --- so D9 was unchecked too, found the moment the parser
#: was made to compare itself against a looser reading of the same table.
CELL = r"(?:\\\||[^|])*"
ROW = re.compile(
    rf"^\|\s*\*\*(?P<tag>[FD]\d+)\*\*{CELL}\|{CELL}\|\s*`(?P<version>v[\d.]+)`\s*\|$",
    re.M)

#: `| *F2* label | *not yet drawn* ... | — |` --- the undrawn ones.
DEFERRED_ROW = re.compile(
    rf"^\|\s*\*(?P<tag>[FD]\d+)\*{CELL}\|{CELL}\|\s*—\s*\|$", re.M)


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


#: Any line that *starts a table row with a bold artefact tag*. Deliberately
#: looser than `ROW`: it does not care what follows, so it cannot be fooled by
#: a formatting change in the version cell.
ANY_TAGGED_ROW = re.compile(r"^\|\s*\*\*([FD]\d+)\*\*", re.M)


def test_the_parser_sees_every_row_the_table_has():
    """**The floor above cannot detect a parser that sees most of the table.**

    `>= 10` passed for a month over a regex that silently skipped every
    two-digit artefact, because fifteen single-digit rows cleared the floor on
    their own. A count threshold is the wrong instrument for *"is this reading
    all of it?"*; the right one is a second, looser reading of the same text,
    and the two must name the same set.

    This is the same argument as **M14**, applied to this file: a gate whose
    failure mode is invisible to itself needs an independent column.
    """
    strict, loose = set(_rows()), set(ANY_TAGGED_ROW.findall(README))
    assert strict == loose, (
        f"the artefact table has {len(loose)} rows with a bold tag and the "
        f"version-checking parser sees {len(strict)} of them. Missed: "
        f"{sorted(loose - strict)}. Either those rows' version cells are "
        "malformed, or `ROW` has stopped matching the table's shape — and "
        "either way the rows below are not being checked.")


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
    released = re.search(r"\*\*Last release: (v[\d.]+)\*\*", README)
    assert released, "the README header does not name a last release"
    tag = released.group(1)

    for command in (f"git tag --list {tag}",
                    f"git log --oneline -1 {tag}",
                    f"git merge-base --is-ancestor {tag} HEAD"):
        assert command in README, (
            f"the README no longer tells the reader to run `{command}`. If the "
            "tag discussion has moved, move the commands with it --- do not "
            "replace them with an assertion about where the tag is, which is "
            "exactly finding T-30. **The tag here is read from the header**, "
            "not carried as a literal: this assertion named v1.1.0 for two "
            "releases after v1.1.0 stopped being the one a reader should "
            "check, which is T-16 in the file written to catch T-16.")

    forbidden = "The tag is placed at the last commit whose content was"
    assert forbidden not in README, (
        "the README is asserting a tag position again (T-30)")


def test_the_readme_does_not_claim_a_tag_that_does_not_exist():
    r"""**The rung is the claim, and the claim must name a tag that exists.**

    A README saying *released as vX* while no `vX` tag exists reports the wrong
    rung, which is what decision **S27** is for.

    **This test was version-locked and went stale at the first release after it
    was written.** It matched three literal sentences about v1.1.0, so the
    v1.2.0 bump --- which correctly rewrote that sentence --- made it match
    *none* of them and the test failed for being out of date rather than for
    finding anything. That is the **T-16** class inside the very file that
    exists to catch T-16, and it cost a failed `--strict` on the release run.
    It is written version-agnostically now: it reads the versions out of the
    README and checks them against each other and against the generated status,
    so it has nothing left to go stale about.
    """
    import re

    claim = re.search(
        r"\*\*Released as (v[0-9.]+); this tree is (v[0-9.]+(?:-dev)?)\.\*\*", README)
    assert claim, (
        "the README must state, once, which version is released and where this "
        "tree sits relative to it, as '**Released as vX; this tree is vY.**'")
    released, tree = claim.group(1), claim.group(2)

    header = re.search(r"\*\*Last release: (v[0-9.]+)\*\*", README)
    assert header and header.group(1) == released, (
        f"the README header says the last release is "
        f"{header.group(1) if header else None!r} and its verification section "
        f"says {released!r}")

    # The generated status must have shipped what the README calls released.
    status = (ROOT / "provenance" / "RELEASE-STATUS-v1.md").read_text(encoding="utf-8")
    shipped = re.search(rf"^## {re.escape(released)} — .*?(\d+)×S", status, re.MULTILINE)
    assert shipped, (
        f"the README says {released} is released, and the generated status "
        f"carries no shipped artefacts for it. One of the two is wrong, and the "
        f"status is the generated one.")


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

    **The file names are deliberately not checked here, and the convention
    they follow changed at v1.2.0.** It used to be stated as *a version suffix
    marks the release an artefact was introduced in*, generalising from
    `config-v1.7.7.json`, which does survive into a v2.2.0 release in the
    exemplar. **That generalisation was wrong for supplements.** The exemplar
    carries `SUPPLEMENTARY-MATERIAL-v2.0.0.tex`, `-v2.1.0.tex` and `-v2.2.0.tex`
    side by side, one per release, exactly as it carries one release-notes file
    per release. Decision **S36** adopts that: each release freezes its own
    supplement and the previous ones are kept rather than rewritten. What must
    agree is what the *current* document says, which is content.
    """
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from _versions import supplement_source

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    supplement = supplement_source(ROOT).read_text(encoding="utf-8")

    header = _tree_version_from(
        readme, r"^Version:\s+\*\*(v\d+\.\d+\.\d+(?:-dev)?)\*\*")
    status = _tree_version_from(
        readme, r"this tree is (v\d+\.\d+\.\d+(?:-dev)?)")

    assert header == status, (
        f"the two statements of the COMPUTATIONAL version disagree: README "
        f"header {header!r}, README verification status {status!r}."
    )

    # **The supplement's date line is checked against the README's
    # `Supplement:` line and NOT against the header, since 2026-10-26.** This
    # assertion used to run `header == status == dated`, on the reading that a
    # supplement belongs to a release and carries its number. The two lines
    # came apart as soon as the document started moving faster than the
    # physics: seventeen supplement editions against one unreleased
    # computational line. Chaining them made a *document* revision look like a
    # false claim that the *code* had advanced, which is the opposite of what
    # this test is for.
    declared = _tree_version_from(readme, r"^Supplement:\s+\*\*v(\d+\.\d+\.\d+)\*\*")
    dated = _tree_version_from(supplement, r"\\date\{[^}]*?v(\d+\.\d+\.\d+)")

    assert declared == dated, (
        f"the supplement's own edition is stated twice and the two disagree: "
        f"the README's `Supplement:` line says v{declared}, the document's "
        f"\\date line says v{dated}. These are the supplement edition and are "
        f"a separate fact from the computational release ({header}), which is "
        "why they are compared here and not chained to it."
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
    # "Cite this repository" reads it, so a version there that is
    # not tagged asserts a release nobody can fetch. It tracks the *released*
    # version, never the tree's.
    cff = re.search(r'^version:\s*"([0-9.]+)"',
                    (ROOT / "CITATION.cff").read_text(encoding="utf-8"), re.MULTILINE)
    assert cff, "CITATION.cff has no version field"
    assert f"v{cff.group(1)}" == header.group(1), (
        f"CITATION.cff says {cff.group(1)}, the README says the last release is "
        f"{header.group(1)}. GitHub reads the first of those.")


#: The decisions a reader must know to read the README honestly. Adding one
#: here is the deliberate act; the test then refuses a README that drops it.
#: **Not all thirty-five** --- a README that recited the whole contract would be
#: the contract, and nobody would read either.
BINDING_DECISIONS = ("S1", "S4c", "S15", "S19", "S26", "S27", "S30", "S33")


def test_the_readme_summarises_every_binding_decision():
    r"""**The README is a gateway to the contracts, and a gateway that omits one
    is worse than no gateway** --- it reads as complete.

    The PI, 2026-10-15: *"The README should conform in summary to the key
    features and requirements of the more expansive and binding governance
    contracts within the project bundle itself ... We need to get this right
    before we engage in v1.5.0 because this is where mistakes will start to
    really cost us."*

    When this was first written, four of the eight were absent: **S15**
    (reproduce the approximations rather than correct them), **S19** (nothing
    public before Paper 1 is submitted), **S26** (the audit half is in scope)
    and **S30** (optimisation deferred). S19 is the one that mattered --- it
    governs whether the repository may be made public at all, and the README
    that a reader would check for exactly that said nothing about it.
    """
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    decisions = (ROOT / "provenance" / "DECISIONS-v1.0.0.md").read_text(encoding="utf-8")

    missing = [d for d in BINDING_DECISIONS if f"**{d}**" not in readme]
    assert not missing, (
        f"the README does not summarise {', '.join(missing)}. Each is a "
        "contract that constrains what may be built, released or claimed, and "
        "a reader who only has the README would not know it applies.")

    undefined = [d for d in BINDING_DECISIONS if f"| **{d}** |" not in decisions]
    assert not undefined, (
        f"{', '.join(undefined)} is named as binding here but has no row in "
        "DECISIONS. The summary must not outlive its contract.")


def test_the_readme_points_at_the_supplement_the_tree_carries():
    r"""**Coordination's ruling 3, 2026-10-28 --- finding T-170.**

    The README's `Supplement:` line is a string P1-B owns that **only a P1-T
    action can invalidate**: the dependency and the custody run in opposite
    directions. It broke twice on 28 October, once pointing at a deleted
    v1.3.17 and again at a deleted v1.3.18, both times leaving a dead link on
    the page colleagues open to find the state of play.

    `_versions.supplement_version` now reads the **tree** --- the
    highest-numbered `SUPPLEMENTARY-MATERIAL-v*.tex` present --- so nothing
    downstream can be misled by the README any more. This is what holds the
    README itself to it, and it is the gate behind Coordination's standing
    exception that whoever moves the supplement carries this line in the same
    commit: with it, "carries it in the same commit" is enforced rather than
    remembered.
    """
    from _versions import readme_supplement_version, supplement_version

    tree = supplement_version(ROOT)
    says = readme_supplement_version(ROOT)
    assert says == tree, (
        f"the README declares the live supplement is v{says} and the tree "
        f"carries v{tree}. Edit README.md's `Supplement: **v{says}**` line "
        f"and the three SUPPLEMENTARY-MATERIAL-v{says} references below it to "
        f"v{tree}. Whoever moved the supplement carries this line in the same "
        "commit — Coordination, 2026-10-28, ruling 3."
    )


def test_the_supplement_version_is_read_from_the_tree_and_not_the_readme():
    r"""**The negative control T-44 requires, for T-170's inversion.**

    The test above compares two values and passes when they agree --- which it
    would also do if both came from the README, since a string always agrees
    with itself. That is the whole defect being repaired, so the inversion has
    to be asserted directly: the value must come from a file that **exists**,
    independently of anything the README claims.
    """
    import re

    from _versions import supplement_version

    on_disk = sorted(
        tuple(int(p) for p in m.group(1).split("."))
        for path in ROOT.glob("SUPPLEMENTARY-MATERIAL-v*.tex")
        if (m := re.fullmatch(
            r"SUPPLEMENTARY-MATERIAL-v([0-9]+\.[0-9]+\.[0-9]+)\.tex",
            path.name)))
    assert on_disk, "no supplement source in the tree to read"
    highest = ".".join(str(p) for p in on_disk[-1])
    assert supplement_version(ROOT) == highest, (
        "supplement_version did not return the highest-numbered "
        "SUPPLEMENTARY-MATERIAL-*.tex in the tree, so it is still deriving "
        "the live edition from something other than the file that is there."
    )
    assert (ROOT / f"SUPPLEMENTARY-MATERIAL-v{highest}.tex").is_file()
