"""Table V, the translations: every cell sourced, none blank, the thesis twice.

The float specification states the acceptance, and one clause of it is the
reason the table exists:

> The thesis gets two columns and **they must differ** --- if they come out
> identical the two conventions have been conflated, which is the error the
> table exists to prevent.

**A test that simply asserted the two columns are unequal strings would pass on
a difference in wording.** That is the failure mode, not a guard against it: the
two thesis forms agree on most rows, and prose that varies where the physics
does not is exactly how a conflation hides. So the structure is asserted
instead --- the columns differ on the **kinematic** rows and nowhere else, and
the difference is a sign flip with a stated reason.

The other clauses: every cell derived from a line of the conventions sheet, no
cell blank, and where a treatment has no counterpart the cell says so.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "config" / "implementation-register.toml"
SHEET = ROOT / "provenance" / "conventions.md"

CONVENTION_COLUMNS = ("mge99", "cl", "th_k", "th_t", "bf", "p09")

#: What a cell says when the sheet establishes no counterpart. Spelled out so a
#: new way of saying it has to be added here deliberately rather than slipping
#: past as prose.
NO_COUNTERPART = ("not established", "no counterpart")

#: What the second thesis column says where the two forms agree.
SAME_AS_K = "as Th-K"


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    data = tomllib.loads(REGISTER.read_text(encoding="utf-8"))
    assert "translations" in data, "the register carries no translations section"
    return data["translations"]


@pytest.fixture(scope="module")
def sheet_lines() -> set[str]:
    """Every `Cn.m` label the conventions sheet actually defines."""
    text = SHEET.read_text(encoding="utf-8")
    return set(re.findall(r"\bC\d+[a-z]?\.\d+\b", text)) | set(
        re.findall(r"\bT-[A-Za-z-]+\b", text)
    )


# ---------------------------------------------------------------------------
# every cell derived from the sheet, and none blank
# ---------------------------------------------------------------------------


def test_no_cell_is_blank(rows):
    """'None blank' is literal. An empty cell is an unanswered question."""
    blank = [
        (r["key"], col)
        for r in rows
        for col in CONVENTION_COLUMNS
        if not str(r.get(col, "")).strip()
    ]
    assert not blank, f"blank translation cells: {blank}"


def test_every_row_names_a_sheet_line_that_exists(rows, sheet_lines):
    """A citation to a line the sheet does not define is worse than no citation.

    It reads as authority and resolves to nothing, which is the shape of every
    citation defect this project has recorded against its antecedent.
    """
    missing = []
    for r in rows:
        cited = set(re.findall(r"\bC\d+[a-z]?\.\d+\b|\bT-[A-Za-z-]+\b", r["sheet"]))
        assert cited, f"row {r['key']} cites no sheet line"
        missing += [(r["key"], c) for c in cited if c not in sheet_lines]
    assert not missing, f"sheet lines cited but not defined: {missing}"


def test_a_treatment_with_no_counterpart_says_so(rows):
    """The cell must state the absence, not imply it by vagueness."""
    for r in rows:
        for col in CONVENTION_COLUMNS:
            cell = r[col].lower()
            if "establish" in cell or "counterpart" in cell:
                assert any(p in cell for p in NO_COUNTERPART), (
                    f"{r['key']}/{col} gestures at absence without stating it: {r[col]!r}"
                )


# ---------------------------------------------------------------------------
# the clause the table exists for
# ---------------------------------------------------------------------------


def test_the_two_thesis_columns_are_not_globally_identical(rows):
    """The acceptance, at its weakest. Necessary, nowhere near sufficient."""
    assert any(r["th_t"] != r["th_k"] for r in rows), (
        "the thesis columns are identical throughout: the two conventions have "
        "been conflated, which is the error this table exists to prevent"
    )


def test_the_thesis_columns_differ_on_exactly_the_kinematic_rows(rows):
    """The acceptance, at its real strength.

    The $\\dot{\\mathcal T}$ form moves every kinematic term to the right-hand
    side, flipping its overall sign against the K/$\\Pi$ form. So the columns
    must differ on the kinematic rows and agree on the others. A row that
    differs without being kinematic is prose drift; a kinematic row that agrees
    is the conflation itself.
    """
    for r in rows:
        differs = r["th_t"] != SAME_AS_K
        assert differs == r["kinematic"], (
            f"row {r['key']}: kinematic={r['kinematic']} but the thesis columns "
            f"{'differ' if differs else 'agree'} --- "
            + (
                "a non-kinematic row must say 'as Th-K', not restate the cell in "
                "different words"
                if differs
                else "a kinematic row must carry the sign flip"
            )
        )


def test_the_kinematic_difference_is_a_sign_flip_with_a_reason(rows):
    """Not merely different text: the stated difference must be the sign.

    If the cell ever stops saying *why* the two differ, the table has lost the
    content that makes it worth printing.
    """
    kinematic = [r for r in rows if r["kinematic"]]
    assert kinematic, "no kinematic rows: the table cannot discharge its acceptance"
    for r in kinematic:
        cell = r["th_t"].lower()
        assert "sign" in cell or "flip" in cell or "rhs" in cell or "right-hand" in cell, (
            f"row {r['key']}: the thesis difference is asserted but not explained: {r['th_t']!r}"
        )


def test_at_least_one_row_carries_the_e9_correction(rows):
    """E9 is the defect the kinematic rows are about; it must be visible.

    MGE99 prints $-(\\ell+2)$ where $+(\\ell+2)$ is correct, and the table is the
    place a reader meets that without having to find the corrections record.
    """
    assert any("E9" in r["mge99"] for r in rows), "no row names the E9 defect"


# ---------------------------------------------------------------------------
# the generated artefacts
# ---------------------------------------------------------------------------


def test_the_generated_table_covers_every_row(rows):
    csv = (ROOT / "tables" / "translations-v1.0.0.csv").read_text(encoding="utf-8")
    for r in rows:
        assert r["key"] in csv, f"{r['key']} missing from the generated CSV"


def test_the_supplement_prints_the_table_rather_than_describing_it():
    """Once the table exists, the supplement must input it.

    It carried a paragraph explaining the table's absence. That paragraph was
    correct while the table did not exist and becomes a false statement the
    moment it does.
    """
    tex = (ROOT / "SUPPLEMENTARY-MATERIAL-v1.0.0.tex").read_text(encoding="utf-8")
    assert "tables/translations-v1.0.0.tex" in tex, (
        "the supplement does not input the translations table"
    )
    assert "does not yet exist" not in tex, (
        "the supplement still explains the absence of a table it now prints"
    )
