#!/usr/bin/env python3
"""One definition of *which files are the bundle*, shared by every gate.

**Why this module exists.** The release fingerprint is supposed to be a property
of the repository: the same checkout must produce the same
`FILE-MANIFEST-SHA256.txt` on every machine. It was not. `make_manifests.py` and
`check_portability.py` each walked the working directory with its own skip list
and neither honoured `.gitignore`, so **anything lying in the folder entered the
fingerprint** --- a `pdflatex` run's `.aux`/`.log`/`.out`, an editor swap file, a
Windows `Thumbs.db`. Two machines with identical commits then disagreed about
what the bundle is. That is finding **T-1**; see
`provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md`.

The fix is structural rather than another skip list: there is now exactly one
selector, here, and the gates import it. Two gates with two rules will drift;
two gates with one rule cannot.

**No dependency on git.** The matcher below reads `.gitignore` and applies it
directly. Shelling out to `git ls-files` would be simpler and is deliberately not
done: a reader reproducing F1 from a downloaded zip has no `.git` directory, and
the gates must give them the same answer as they give the repository.

The supported subset of `.gitignore` syntax is exactly what this bundle's own
ignore file uses --- basename globs, directory-only patterns, anchored patterns
containing a slash, and `!` negation, with later patterns winning. Anything
outside that subset raises rather than silently mismatching git.
"""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path, PurePosixPath

__all__ = [
    "BINARY_SUFFIXES",
    "EXCLUDE_DIRS",
    "GitIgnore",
    "bundle_files",
    "ignored_but_present",
]

#: Directories that are never part of the bundle on any machine, whether or not
#: `.gitignore` happens to mention them. Belt and braces: a missing or truncated
#: `.gitignore` must not be able to pull a virtualenv into the fingerprint.
EXCLUDE_DIRS = frozenset(
    {".git", "__pycache__", ".pytest_cache", ".ipynb_checkpoints", ".venv", "venv"}
)

#: Suffixes whose *contents* no text gate can meaningfully read. These files are
#: still part of the bundle and still hashed into the manifest --- the figures
#: are deliverables. They are only skipped by content checks.
BINARY_SUFFIXES = frozenset({".png", ".pdf", ".pyc", ".zip", ".gz", ".jpg", ".jpeg"})


class GitIgnore:
    """The subset of `.gitignore` this bundle uses, applied without git."""

    def __init__(self, patterns: list[str]) -> None:
        self.rules: list[tuple[str, bool, bool, bool]] = []
        for raw in patterns:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if "**" in line:
                raise ValueError(
                    f"{line!r}: '**' is outside the supported subset. Extend this "
                    "matcher deliberately rather than letting it disagree with git."
                )
            negated = line.startswith("!")
            if negated:
                line = line[1:]
            dir_only = line.endswith("/")
            pat = line.rstrip("/")
            anchored = pat.startswith("/") or "/" in pat
            self.rules.append((pat.lstrip("/"), negated, dir_only, anchored))

    @classmethod
    def read(cls, root: Path) -> "GitIgnore":
        path = root / ".gitignore"
        if not path.exists():
            return cls([])
        return cls(path.read_text(encoding="utf-8").splitlines())

    def ignores(self, rel: PurePosixPath) -> bool:
        """Whether `rel` (a file, relative to the root) is ignored.

        Later rules win, which is what makes `!figures/*.pdf` able to rescue the
        figure deliverables from the blanket `*.pdf` above it --- the rule that
        keeps publisher PDFs out of the repository.
        """
        parts = rel.parts
        decided = False
        for pat, negated, dir_only, anchored in self.rules:
            if anchored:
                if dir_only:
                    hit = any(
                        fnmatch(str(PurePosixPath(*parts[: i + 1])), pat)
                        for i in range(len(parts) - 1)
                    )
                else:
                    hit = fnmatch(str(rel), pat)
            else:
                # An unanchored pattern matches at any depth. When it matches a
                # directory component, everything beneath it is ignored.
                candidates = parts[:-1] if dir_only else parts
                hit = any(fnmatch(part, pat) for part in candidates)
            if hit:
                decided = not negated
        return decided


def order_key(rel: str) -> list[str]:
    r"""The one ordering of bundle paths: by POSIX parts, case-sensitive.

    **T-200.** `sorted()` on `Path` objects is not this on every machine: a
    `WindowsPath` compares case-insensitively, so `independent_checks_...py`
    sorted before `TG-...zip` on Windows and after it on Linux. Every
    manifest line agreed and the manifests did not, so the immutable gate
    failed on a clean Windows tree and named no file. This key is what a
    `PosixPath` sorts by on Linux, so the order the manifests were written in
    does not move.
    """
    return rel.split("/")


def _walk(root: Path):
    for p in sorted(root.rglob("*"),
                    key=lambda q: order_key(q.relative_to(root).as_posix())):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if set(rel.parts) & EXCLUDE_DIRS:
            continue
        yield p, PurePosixPath(rel.as_posix())


#: What marks a directory as a whole copy of a tree rather than a part of this
#: one: a clone carries its own `.git`, and an extracted release archive its own
#: manifest. No directory of the bundle itself carries either.
TREE_MARKERS = (".git", "FILE-MANIFEST-SHA256.txt")


def nested_trees(root: Path) -> list[PurePosixPath]:
    """The directories inside `root` that are another copy of a tree.

    **T-207.** A clean-checkout clone made from inside the working tree sat in
    it as `frame-covariant-cmb-reproducibility/`, and every file of it was
    walked as the bundle's: `pytest` stopped on two `tests.conftest` modules,
    and the manifests and the archive would have taken a second bundle in. A
    copy is recognised by its own marker and left out whole; the outermost
    copy is named, since a copy can hold a copy.
    """
    found: set[PurePosixPath] = set()
    for marker in TREE_MARKERS:
        for path in root.rglob(marker):
            rel = path.parent.relative_to(root)
            if rel.parts and not (set(rel.parts) & EXCLUDE_DIRS):
                found.add(PurePosixPath(rel.as_posix()))
    return sorted(
        (t for t in found
         if not any(o != t and t.parts[:len(o.parts)] == o.parts for o in found)),
        key=lambda t: order_key(t.as_posix()))


def inside(rel: PurePosixPath, trees: list[PurePosixPath]) -> bool:
    """Whether `rel` lies in one of `trees` (as `nested_trees` names them)."""
    return any(rel.parts[:len(t.parts)] == t.parts for t in trees)


def bundle_files(root: Path) -> list[Path]:
    """Every file that *is* the bundle, in sorted order, on any machine.

    This is the one list. A file absent from it is absent from the fingerprint,
    absent from the portability gate, and absent from the released archive.
    A copy of a tree sitting inside it is not part of it (T-207).
    """
    ign = GitIgnore.read(root)
    trees = nested_trees(root)
    return [p for p, rel in _walk(root)
            if not ign.ignores(rel) and not inside(rel, trees)]


def ignored_but_present(root: Path) -> list[PurePosixPath]:
    """Files sitting in the working tree that the bundle does not include.

    Reported by the gates rather than hidden, because the count difference
    between two machines is a question people will ask --- it was asked, and the
    answer took a round trip. It is a note, never a failure: a local build
    leaving `.aux` files behind is normal and must not block a release.
    """
    ign = GitIgnore.read(root)
    trees = nested_trees(root)
    return [rel for _p, rel in _walk(root)
            if ign.ignores(rel) or inside(rel, trees)]
