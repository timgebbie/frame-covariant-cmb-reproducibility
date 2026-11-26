"""**T-207.** A copy of the bundle inside the working tree is not the bundle.

A clean-checkout clone made from inside the tree sat in it whole, and `pytest`
from the root stopped on two `tests.conftest` modules, while the gates and the
archive would have walked a second bundle as this one's files.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _bundle_files import bundle_files, ignored_but_present, nested_trees  # noqa: E402


def test_a_clone_or_an_extracted_archive_inside_the_tree_is_left_out(tmp_path):
    (tmp_path / "FILE-MANIFEST-SHA256.txt").write_text("x\n", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a\n", encoding="utf-8")
    clone = tmp_path / "frame-covariant-cmb-reproducibility"
    (clone / ".git").mkdir(parents=True)
    (clone / "tests").mkdir()
    (clone / "tests" / "conftest.py").write_text("\n", encoding="utf-8")
    archive = tmp_path / "frame-covariant-cmb-reproducibility-1.4.0"
    archive.mkdir()
    (archive / "FILE-MANIFEST-SHA256.txt").write_text("y\n", encoding="utf-8")
    (archive / "c.txt").write_text("c\n", encoding="utf-8")

    assert [str(t) for t in nested_trees(tmp_path)] == [
        "frame-covariant-cmb-reproducibility",
        "frame-covariant-cmb-reproducibility-1.4.0"]
    names = [p.relative_to(tmp_path).as_posix() for p in bundle_files(tmp_path)]
    assert names == ["FILE-MANIFEST-SHA256.txt", "a.txt"], names
    stray = {str(r) for r in ignored_but_present(tmp_path)}
    assert {"frame-covariant-cmb-reproducibility/tests/conftest.py",
            "frame-covariant-cmb-reproducibility-1.4.0/c.txt"} <= stray, stray


def test_the_bundle_records_no_copy_of_itself():
    """No file the manifest lists marks a directory below the root as a tree.

    A working tree may hold a copy, which is left out; what the bundle records
    must not, or part of the bundle would be left out of its own file list.
    """
    from _bundle_files import TREE_MARKERS
    listed = [line.split(None, 1)[1].strip() for line in
              (ROOT / "FILE-MANIFEST-SHA256.txt").read_text(encoding="utf-8").splitlines()
              if line.strip() and not line.startswith("#") and len(line.split(None, 1)) == 2]
    assert listed, "the manifest parsed to nothing"
    marked = [p for p in listed if "/" in p and p.rsplit("/", 1)[1] in TREE_MARKERS]
    assert marked == [], marked


def test_pytest_collects_the_bundle_suite_alone():
    ini = (ROOT / "pytest.ini").read_text(encoding="utf-8")
    assert re.search(r"^testpaths\s*=\s*tests\s*$", ini, re.M), ini
