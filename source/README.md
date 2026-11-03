# source/

Frozen reference material, one directory for each frozen edition of the
target paper.

| | Holds | Frozen |
|---|---|---|
| `source-v1.1.6/` | Paper 1 at its arXiv freeze, `v1.1.6-arxiv`: the source bundle `TG-FrameCovariantCMBR-v1.1.6-arxiv.zip` — the `.tex`, `.bib`, `.bbl` and the three figure sources it builds from — and `independent_checks_v1.1.6.py`, the algebra check written against that edition | 2026-11-02 |

**A directory is named for the edition it freezes, and a check sits beside
the source it checks.** A later edition arrives as a directory of its own and
never alters this one: the accepted manuscript, with acceptance criterion 6,
or a second paper. The version in each name is what makes an immutable prefix
safe, since nothing here has to change when the paper moves on. The two files
sat in separate directories, `source-v1/` and `source-v2/`, from 2 to
3 November 2026, and were moved together on 3 November.

**The algebra check runs from a clone of this repository alone.** It imports
the standard library, `numpy` and `sympy`, reads nothing, and writes its
verdicts beside itself. The manuscript's structure check is not carried: it
gates a build this repository does not hold, so here it could only fail.

**Record a path at the moment of freeze rather than wiring it into a
script.** A filename that carries a version moves at every bump, and a
hardcoded version in a tool is silently wrong at the next one.

**The `.pdf` of a paper is a build product and does not enter this tree**;
the three PDFs inside the archive are figure sources, inputs to the build.
**Publisher PDFs never enter this repository.** The Annals papers this bundle
reconstructs are cited, never carried: the bundle must be publishable and
DOI-able from the start. Equation numbers are resolved from the published
PDFs held outside this tree, and `provenance/` records which edition each
number came from.

Everything under `source/` is listed in `IMMUTABLE-MANIFEST-SHA256.txt`: once
recorded, a change here is a release-blocking event. The move of 3 November
is the one such change, made with the manifest in the same commit.
