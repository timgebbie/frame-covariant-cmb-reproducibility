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


def _walk(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if set(rel.parts) & EXCLUDE_DIRS:
            continue
        yield p, PurePosixPath(rel.as_posix())


def bundle_files(root: Path) -> list[Path]:
    """Every file that *is* the bundle, in sorted order, on any machine.

    This is the one list. A file absent from it is absent from the fingerprint,
    absent from the portability gate, and absent from the released archive.
    """
    ign = GitIgnore.read(root)
    return [p for p, rel in _walk(root) if not ign.ignores(rel)]


def ignored_but_present(root: Path) -> list[PurePosixPath]:
    """Files sitting in the working tree that the bundle does not include.

    Reported by the gates rather than hidden, because the count difference
    between two machines is a question people will ask --- it was asked, and the
    answer took a round trip. It is a note, never a failure: a local build
    leaving `.aux` files behind is normal and must not block a release.
    """
    ign = GitIgnore.read(root)
    return [rel for _p, rel in _walk(root) if ign.ignores(rel)]
