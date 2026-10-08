# source/

Frozen reference material, following the house layout.

| | Holds | Status |
|---|---|---|
| `source-v1/` | the frozen target-paper source — Paper 1, at manuscript freeze | **pending**: Paper 1 is not yet frozen. It arrives with acceptance criterion 6 |

**What arrives here at freeze**, as of 2026-10-08:
`paper/TG-FrameCovariantCMBR-v1.0.0.{tex,bib}` from the project repository —
the `.pdf` is a build product and does not enter this tree. The earlier name
`nonlinear-shear-calibration.*` is retired; nothing in this bundle referenced
it, and nothing should, because **the filename carries a version and therefore
moves at every bump**. Record the path at the moment of freeze rather than
wiring it into a script: the freeze happens once per release, and a hardcoded
`v1.0.0` in a tool would be silently wrong at v1.1.0.

| `source-v2/` | computational conformity and clarification inserts — the statements this bundle makes about the target paper that are not in the paper itself | **pending** |

**Publisher PDFs never enter this repository.** The Annals papers this bundle
reconstructs are cited, never carried: the bundle must be publishable and
DOI-able from the start. Equation numbers are resolved from the published PDFs
held outside this tree, and `provenance/` records which edition each number came
from.

Everything under `source/` is listed in `IMMUTABLE-MANIFEST-SHA256.txt`: once
recorded, a change here is a release-blocking event.
