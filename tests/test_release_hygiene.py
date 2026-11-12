r"""The release-hygiene gate must be able to fail, and must fail on T-50's tree.

**A gate that cannot fail is not a gate** --- finding **T-24**, and the reason
every gate added since carries its own negative control. This one needs the
control more than most, because it was written *after* the defect it refuses
and against a tree that was already clean: a check written to pass on the tree
in front of it is a check written to pass.

So each test below builds the exact file that shipped in the v1.2.0 archive and
asserts the gate refuses it.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_release_hygiene.py"

sys.path.insert(0, str(ROOT / "scripts"))

from _versions import (  # noqa: E402
    released_version,
    supplement_figures,
    supplement_pdf,
    supplement_source,
    supplement_version,
    tree_version,
)


def run_gate() -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(GATE)], capture_output=True,
                          text=True, cwd=ROOT, timeout=300)


def test_the_gate_passes_on_this_tree():
    """The baseline. Everything below is *relative to this*."""
    result = run_gate()
    assert result.returncode == 0, result.stdout + result.stderr


# ---------------------------------------------------------------------------
# The three files that shipped. Each is rebuilt and the gate must refuse it.
# ---------------------------------------------------------------------------


def test_a_utf16_source_is_refused():
    r"""**The file that got through, and the reason it got through.**

    `SUPPLEMENTARY-MATERIAL-v1.0.0.tex` was restored by a PowerShell
    redirection, which writes UTF-16LE with a BOM. `check_portability.py`
    counts ``b"\r\n"`` against ``b"\n"`` to find mixed line endings, and in
    UTF-16LE a CRLF is ``0D 00 0A 00`` --- the two bytes are never adjacent, so
    the CRLF count is zero and the file reads as uniformly LF. **A byte-level
    gate that assumes one byte per character cannot see a wide encoding.**
    """
    # `.encode("utf-16")` prepends the BOM, which is what PowerShell's `>` and
    # `Out-File` actually write and what the shipped file carried.
    intruder = ROOT / "functions" / "_t50_control.py"
    intruder.write_bytes("# a restored file\r\nx = 1\r\n".encode("utf-16"))
    try:
        result = run_gate()
        assert result.returncode == 1, (
            "a UTF-16 source entered the bundle and the gate passed. That is "
            "exactly T-50, and the whole reason this file exists.\n" + result.stdout)
        assert "NUL bytes" in result.stdout and "UTF-16" in result.stdout
    finally:
        intruder.unlink()


def test_a_stale_build_output_is_refused():
    """`supplement-v1.0.0.pdf`: a rendering left behind when the build moved on."""
    stale = supplement_pdf(ROOT).with_name("supplement" + "-v0.9.0.pdf")
    stale.write_bytes(b"%PDF-1.4\n")
    try:
        result = run_gate()
        assert result.returncode == 1, (
            "a supplement rendering named for a version the build is not "
            "pointed at passed the gate.\n" + result.stdout)
        assert "left behind" in result.stdout
    finally:
        stale.unlink()


def test_a_stale_generated_include_is_refused():
    """`figures-v1.0.0.tex`: byte-identical to its successor, under a dead name."""
    live = supplement_figures(ROOT)
    stale = live.with_name("figures" + "-v0.9.0.tex")
    if not live.exists():                                   # pragma: no cover
        pytest.skip("the figure include has not been generated in this tree yet")
    shutil.copyfile(live, stale)
    try:
        result = run_gate()
        assert result.returncode == 1, (
            "a generated include under a stale version label passed the gate, "
            "byte-identical to the live one.\n" + result.stdout)
    finally:
        stale.unlink()


def test_a_hardcoded_supplement_name_is_refused():
    """The root cause: the name was a literal in nine places, so repointing missed two."""
    # **Assembled rather than written out**, so that *this* file contains no
    # literal the gate would refuse. The alternative is to exempt this path in
    # the gate, and a gate with an exemption for the file that tests it is a
    # gate with an exemption.
    source, pdf = "SUPPLEMENTARY-MATERIAL-v", "supplement-v"
    intruder = ROOT / "scripts" / "_t50_control.py"
    intruder.write_text(
        f'"""A docstring may name {source}1.2.0.tex: that is prose."""\n'
        f'PATH = "supplementary-materials/{pdf}1.2.0.pdf"\n',
        encoding="utf-8", newline="\n")
    try:
        result = run_gate()
        assert result.returncode == 1, (
            "a script spelled a supplement filename as a string literal and the "
            "gate passed.\n" + result.stdout)
        assert "string literal" in result.stdout
        assert result.stdout.count("_t50_control.py") == 1, (
            "the docstring mention was counted as a violation. Prose that names "
            "a file is documentation; only a literal the code acts on is the "
            "defect, and the gate walks the AST to tell them apart.")
    finally:
        intruder.unlink()


# ---------------------------------------------------------------------------
# The version source itself.
# ---------------------------------------------------------------------------


def test_the_two_version_statements_are_distinct_and_both_readable():
    """`CITATION.cff` states the release; the README header states the tree.

    They are *different facts* and the bundle has conflated them before: the
    archive generator defaulted to a version frozen into its own source
    (**T-49**), and the README header and its verification section disagreed
    for two days (**T-16**).
    """
    assert released_version(ROOT), "CITATION.cff states no released version"
    assert tree_version(ROOT), "the README header states no tree version"
    # **Three facts, and the third is NOT derived from the second.** This line
    # used to read `supplement_version == tree_version minus -dev`, which was
    # not a check: it restated how `supplement_version` was computed, so it
    # could only ever pass. It passed every day until 2026-10-26, when the
    # computational line stood at v1.3.0-dev and the supplement had reached
    # its seventeenth edition, and eight tests failed on a filename nothing
    # had written. A tautology is the one assertion that cannot warn you.
    assert supplement_version(ROOT), "the README declares no supplement edition"
    assert supplement_source(ROOT).exists(), (
        f"the README declares supplement edition v{supplement_version(ROOT)} "
        f"and {supplement_source(ROOT).name} is not in the tree")


def test_the_live_supplement_exists_and_the_frozen_ones_are_kept():
    """**S36**: one source per release, previous ones kept, one rendering only."""
    assert supplement_source(ROOT).exists(), (
        f"{supplement_source(ROOT).name} does not exist, and the README header "
        "says this tree is it")

    sources = sorted(p.name for p in ROOT.glob("SUPPLEMENTARY-MATERIAL-v*.tex"))
    assert len(sources) >= 1, "no supplement source at all"

    renderings = sorted(
        p.name for p in (ROOT / "supplementary-materials").glob("supplement-v*.pdf"))
    assert len(renderings) <= 1, (
        f"{len(renderings)} supplement renderings in the tree: {renderings}. "
        "S36 keeps the frozen `.tex`, not the build outputs --- the rendering "
        "of record for an earlier release is its release asset and its "
        "archived DOI.")


def _history(repo: Path):
    """A git runner for a throwaway history with stated commit times."""
    import os

    def git(*args: str, date: str | None = None) -> None:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.org",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.org")
        if date:
            env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        subprocess.run(["git", "-C", str(repo), *args], check=True,
                       capture_output=True, env=env)
    return git


def test_a_merged_input_older_than_the_pdf_is_caught(tmp_path):
    r"""**The control the review of 3 November asked for.** A branch changes an `\input`
    before the PDF is rebuilt on `main`, and is merged after. Its commit is
    older than the PDF's, so the commit clock called the PDF current; the PDF
    was not built from the input `main` now holds. The verdict compares the
    input's contents at the PDF's commit with its contents now, and no time
    enters it. A byte-identical restore of the input is current again (T-183's
    case, with no special branch).
    """
    from check_release_hygiene import stale_inputs

    repo = tmp_path / "history"
    repo.mkdir()
    git = _history(repo)
    git("init", "-q", "-b", "main")
    (repo / "master.tex").write_text("\\input{table.tex}\n", encoding="utf-8")
    (repo / "table.tex").write_text("one\n", encoding="utf-8")
    (repo / "doc.pdf").write_bytes(b"%PDF built from one")
    git("add", ".")
    git("commit", "-q", "-m", "A", date="2026-01-01T00:00:00+00:00")
    git("checkout", "-q", "-b", "side")
    (repo / "table.tex").write_text("two\n", encoding="utf-8")
    git("commit", "-q", "-am", "B: the input moves, early", date="2026-01-02T00:00:00+00:00")
    git("checkout", "-q", "main")
    (repo / "doc.pdf").write_bytes(b"%PDF rebuilt from one")
    git("commit", "-q", "-am", "C: the PDF is rebuilt, later", date="2026-01-03T00:00:00+00:00")
    git("merge", "-q", "--no-edit", "side", date="2026-01-04T00:00:00+00:00")

    sources = [repo / "master.tex", repo / "table.tex"]
    stale, by_git, by_clock = stale_inputs(repo, repo / "doc.pdf", sources)
    assert [s.name for s in stale] == ["table.tex"], (
        "a merged input that predates the PDF's rebuild passed the gate: the "
        "verdict is reading a clock, not the contents (review of 3 November)")
    assert (by_git, by_clock) == (2, 0)

    (repo / "table.tex").write_text("one\n", encoding="utf-8")
    git("commit", "-q", "-am", "D: a byte-identical restore", date="2026-01-05T00:00:00+00:00")
    stale, _, _ = stale_inputs(repo, repo / "doc.pdf", sources)
    assert stale == [], "a byte-identical restore was called stale (T-183)"

    (repo / "table.tex").write_text("three, not yet committed\n", encoding="utf-8")
    stale, by_git, by_clock = stale_inputs(repo, repo / "doc.pdf", sources)
    assert [s.name for s in stale] == ["table.tex"] and by_clock == 1, (
        "an uncommitted edit must be judged by its own clock, and it is newer")
