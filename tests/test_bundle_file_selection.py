"""Finding T-1: the release fingerprint must be a property of the repository.

The two gates --- `make_manifests.py` and `check_portability.py` --- each walked
the working directory with its own skip list, and neither honoured `.gitignore`.
So a `pdflatex` run's `.aux`/`.log`/`.out`, or a `Thumbs.db` that Windows
Explorer writes into `figures/` merely because someone looked at it, entered the
file set. Two machines at the same commit then disagreed about what the bundle
is: the PI's reported 95 files where this container reported 93.

That is not cosmetic. `FILE-MANIFEST-SHA256.txt` is the release fingerprint. If
it can absorb whatever is lying in the folder, it fingerprints a folder rather
than a release, and `--check` fails on a correct checkout for reasons that have
nothing to do with the bundle.

These tests hold the fix in place:

* there is **one** selector, and both gates use it (a second rule is how the
  first one drifts);
* planting ignored files changes **nothing** about what is selected;
* `!figures/*.pdf` still rescues the figure deliverables from the blanket
  `*.pdf` that keeps publisher PDFs out --- a matcher that got negation wrong
  would silently drop three released figures from the fingerprint;
* and the three numbers the gates print still reconcile against the real tree.
"""

from __future__ import annotations

import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _bundle_files import GitIgnore, bundle_files, ignored_but_present  # noqa: E402

import pytest  # noqa: E402


# ---------------------------------------------------------------------------
# one selector, not two
# ---------------------------------------------------------------------------


def test_both_gates_select_through_the_same_function():
    """Import identity, not equal behaviour.

    Checking that the two gates happen to agree today would pass right up until
    someone edited one skip list. The invariant worth holding is that there is
    only one list to edit.
    """
    import check_portability
    import make_manifests

    assert check_portability.bundle_files is bundle_files
    assert make_manifests.bundle_files is bundle_files


def test_neither_gate_kept_a_private_skip_list():
    """The old `SKIP_DIRS` / `EXCLUDE_DIRS` constants must be gone, not shadowed."""
    import check_portability
    import make_manifests

    assert not hasattr(check_portability, "SKIP_DIRS")
    assert not hasattr(make_manifests, "EXCLUDE_DIRS")


# ---------------------------------------------------------------------------
# the matcher, on a synthetic tree
# ---------------------------------------------------------------------------


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A miniature of this bundle's own ignore situation."""
    (tmp_path / ".gitignore").write_text(
        "__pycache__/\n"
        "*.aux\n"
        "*.log\n"
        "*.out\n"
        "*.pdf\n"
        "!figures/*.pdf\n"
        "Thumbs.db\n"
        ".DS_Store\n",
        encoding="utf-8",
    )
    for rel in (
        "paper.tex",
        "figures/f1.pdf",
        "figures/f1.png",
        "source/annals-ii.pdf",
        "functions/model.py",
        "functions/__pycache__/model.cpython-311.pyc",
    ):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
    return tmp_path


def _rels(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in bundle_files(root)}


def test_the_negation_rescues_the_released_figures(tree: Path):
    """`!figures/*.pdf` must beat `*.pdf`, which is above it.

    Getting this backwards drops `figures/f1-appendix-f-v1.0.0.pdf` and
    `figures/f3-angular-spectrum-v1.0.0.pdf` out of the fingerprint without a
    word --- and those are the v1.0.0 deliverable.
    """
    selected = _rels(tree)
    assert "figures/f1.pdf" in selected
    assert "source/annals-ii.pdf" not in selected, "the publisher PDF rule must still bite"


def test_a_pycache_is_excluded_by_directory(tree: Path):
    assert "functions/__pycache__/model.cpython-311.pyc" not in _rels(tree)


def test_planting_build_products_changes_nothing(tree: Path):
    """The whole point. Two machines, one of which has run pdflatex, must agree."""
    before = _rels(tree)
    for rel in (
        "paper.aux",
        "paper.log",
        "paper.out",
        "figures/Thumbs.db",
        "functions/.DS_Store",
    ):
        (tree / rel).write_text("x", encoding="utf-8")

    assert _rels(tree) == before
    assert {str(r) for r in ignored_but_present(tree)} >= {
        "paper.aux", "paper.log", "paper.out", "figures/Thumbs.db", "functions/.DS_Store"
    }


def test_an_unsupported_pattern_raises_rather_than_silently_disagreeing(tmp_path: Path):
    """`**` is outside the implemented subset.

    A matcher that quietly mis-handles a pattern git understands is worse than
    one that refuses: the fingerprint would differ between this bundle and
    anyone using git, with nothing to show for it.
    """
    with pytest.raises(ValueError, match=r"\*\*"):
        GitIgnore(["docs/**/draft.md"])


def test_negation_is_order_sensitive_the_way_git_is():
    """Later wins. Reversing these two lines must change the answer."""
    rescued = GitIgnore(["*.pdf", "!figures/*.pdf"])
    shadowed = GitIgnore(["!figures/*.pdf", "*.pdf"])
    rel = PurePosixPath("figures/f1.pdf")
    assert not rescued.ignores(rel)
    assert shadowed.ignores(rel)


# ---------------------------------------------------------------------------
# the real tree
# ---------------------------------------------------------------------------


def test_the_manifest_covers_every_bundle_file_but_itself():
    """The arithmetic the gates print, checked rather than trusted.

    `bundle files = manifest entries + 2`, the two being the manifests, which
    cannot contain their own hashes.
    """
    manifest = ROOT / "FILE-MANIFEST-SHA256.txt"
    entries = [ln for ln in manifest.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(bundle_files(ROOT)) == len(entries) + 2


def test_the_provenance_readme_lists_every_record():
    """A stale index is how a record becomes invisible.

    `provenance/README.md` had gone stale once already --- five records existed
    that it did not mention, and it described the append-only guard as though it
    were the immutable manifest. An index nobody checks is worse than none,
    because it is believed.
    """
    readme = (ROOT / "provenance" / "README.md").read_text(encoding="utf-8")
    missing = [
        p.name
        for p in sorted((ROOT / "provenance").iterdir())
        if p.is_file() and p.name != "README.md" and f"`{p.name}`" not in readme
    ]
    assert not missing, f"provenance/README.md does not list: {missing}"


def test_the_released_figures_are_in_the_bundle():
    """Guards the negation on the real `.gitignore`, not only the synthetic one."""
    selected = {p.relative_to(ROOT).as_posix() for p in bundle_files(ROOT)}
    for rel in (
        "figures/f1-appendix-f-v1.0.0.pdf",
        "figures/f3-angular-spectrum-v1.0.0.pdf",
        "supplementary-materials/supplement-v1.0.0.pdf",
    ):
        assert rel in selected, f"{rel} fell out of the fingerprint"
