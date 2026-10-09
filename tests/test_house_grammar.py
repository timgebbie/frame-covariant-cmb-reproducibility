"""R5 — the README follows the house layout, and its links resolve.

The repository form follows `github.com/timgebbie/correlation-emergence-reproducibility`:
different physics, same structure. That is a standing instruction from the PI,
and structure drifts silently — two pieces of it had already been lost here
before anyone looked, which is why this is a test rather than a convention.

**What was lost, and is now held:**

* the **reference to the computational supplement immediately below the
  title**, before the first section. A reader arriving at a reproducibility
  bundle should be told where the document explaining it is before they are
  shown a figure;
* the **table** in *DOI, citation and license*. The exemplar carries `Item` /
  `Value` rows for the paper, the supplement, the repository, the DOI and the
  two licences. Prose paragraphs carry the same facts and are harder to scan,
  and a reader checking a licence is scanning.

The link check is not house grammar but belongs with it: a public README whose
relative links do not resolve is the first thing a visitor finds and the last
thing anyone re-reads.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


@pytest.fixture(scope="module")
def text() -> str:
    return README.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def preamble(text: str) -> str:
    """Everything above the first section heading."""
    return text.split("\n## ", 1)[0]


# ---------------------------------------------------------------------------
# the two pieces that were lost
# ---------------------------------------------------------------------------


def test_the_supplement_is_referenced_before_the_first_section(preamble: str):
    """Below the title, not buried under *DOI, citation and license*."""
    assert "supplementary-materials/supplement-v1.0.0.pdf" in preamble, (
        "the computational supplement is not referenced above the first section"
    )


def test_the_preamble_says_what_the_supplement_is_for(preamble: str):
    """A bare link is a worse signpost than a sentence.

    The exemplar's reader is told what the document contains; a link alone
    makes them open it to find out whether they needed to.
    """
    assert re.search(r"supplement|supplementary", preamble, re.I)
    assert len(preamble.split()) > 60, "the preamble has been reduced to a stub"


def test_the_licence_section_is_a_table(text: str):
    """`Item` / `Value`, as the exemplar has it."""
    section = text.split("## DOI, citation and license", 1)[1]
    assert "| Item | Value |" in section, "the licence section is no longer a table"
    for row in ("Associated paper", "Supplementary PDF", "GitHub repository",
                "ZivaHub/Figshare DOI", "Code license"):
        assert row in section, f"the licence table has lost its {row!r} row"


def test_both_licences_are_named_in_the_table(text: str):
    """MIT for code, CC BY 4.0 for the supplement, text, figures and tables."""
    section = text.split("## DOI, citation and license", 1)[1]
    assert "MIT" in section and "CC BY 4.0" in section


# ---------------------------------------------------------------------------
# the house section order
# ---------------------------------------------------------------------------

#: The exemplar's order. Extra sections between these are allowed --- this
#: bundle carries a second key figure the exemplar has no counterpart for ---
#: but the spine must not be reordered or dropped.
HOUSE_ORDER = [
    "Current situation",
    "Future situation",
    "Scientific boundary",
    "Repository structure",
    "Installation",
    "Reproducing the active outputs",
    "Verification status",
    "Version-control policy",
    "DOI, citation and license",
]


def test_the_house_sections_appear_in_order(text: str):
    headings = re.findall(r"^## (.+)$", text, re.M)
    positions = []
    for want in HOUSE_ORDER:
        found = [i for i, h in enumerate(headings) if h.startswith(want)]
        assert found, f"the house section {want!r} is missing"
        positions.append(found[0])
    assert positions == sorted(positions), (
        f"house sections are out of order: {list(zip(HOUSE_ORDER, positions))}"
    )


def test_the_key_figure_leads(text: str):
    """The exemplar opens on a figure, and so does this.

    Which figure is a separate decision --- it is F3, the recovery --- but that
    the README opens on one is the house form.
    """
    headings = re.findall(r"^## (.+)$", text, re.M)
    assert headings, "the README has no sections"
    assert headings[0].startswith("Key figure"), headings[0]


# ---------------------------------------------------------------------------
# the links
# ---------------------------------------------------------------------------


def test_every_relative_link_resolves(text: str):
    """Not house grammar, but it belongs here.

    A public README whose links 404 is the first thing a visitor finds. External
    links are not checked --- this suite does not reach the network --- but
    everything pointing inside the repository must exist.
    """
    targets = re.findall(r"\]\(([^)]+)\)", text)
    missing = []
    for t in targets:
        if t.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if not (ROOT / t.split("#", 1)[0]).exists():
            missing.append(t)
    assert not missing, f"README links that do not resolve: {missing}"


def test_no_inline_image_points_at_a_missing_figure(text: str):
    missing = [t for t in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
               if not t.startswith("http") and not (ROOT / t).exists()]
    assert not missing, f"README images that do not resolve: {missing}"
