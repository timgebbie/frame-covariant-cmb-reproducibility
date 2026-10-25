"""A digest of the code that produced a cached result. One definition.

**Finding T-129, and it is a defect in the guard rather than in the physics.**

`figure_f9_acoustic_spectrum.py` has carried a `source_fingerprint` since
**T-54**: a cached CSV is stamped with a digest of the code that made it, and
``--replot`` refuses to redraw numbers this tree did not compute. The reasoning
is right and the implementation had a hole. It hashed

    every ``functions.*`` module **actually in `sys.modules`**

which is a property of *the path the process happened to take*, not of the
tree. `functions.spectra.peebles` is imported lazily inside
`build_environment`, so

  * the **compute** path hashes **20** modules, peebles among them;
  * the **replot** path never calls `build_environment`, hashes **19**, and
    **peebles is not in the digest at all**.

Two consequences, and the second is the serious one:

  1. *False invalidation.* The two digests can never agree, so a round trip
     compute-then-replot always fails the guard. F10 hit this the first time it
     was exercised, which is how this was found.
  2. **False validation.** On the reading path the digest is silently blind to
     every lazily-imported module. A change to the recombination history is
     exactly the kind of change that must invalidate a cached spectrum, and on
     the branch that *reads* the cache it was not being looked at. That is the
     hole T-54 exists to close, reopened inside T-54's own instrument.

The repair is not a longer module list. It is that **the digest must be a
property of the tree and not of the run**: a declared set, walked from disk,
identical whichever branch asks for it.

Deliberately conservative, as T-54's was: every `.py` under `functions/`, plus
the calling script. A docstring change invalidates the cache, because bytes
cannot say whether a change was semantic. The cost of a false invalidation is
one rerun; the cost of a false validation is shipping a stale figure under a
CLEAN banner, which is what happened on 2026-10-17.
"""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def source_fingerprint(script: pathlib.Path | str) -> str:
    """A 16-hex digest of `functions/` plus `script`, independent of the run.

    `script` is the caller's own file --- pass `__file__`. It is included
    because a figure's own assembly is part of what produced its numbers, and
    it must be the **caller's** path: a helper that hashed its own `__file__`
    would stamp every cache in the tree with the same script identity, which
    is the bug one layer down.
    """
    digest = hashlib.sha256()
    for path in sorted((ROOT / "functions").rglob("*.py")):
        digest.update(str(path.relative_to(ROOT).as_posix()).encode("utf-8"))
        digest.update(path.read_bytes())
    script = pathlib.Path(script).resolve()
    digest.update(script.name.encode("utf-8"))
    digest.update(script.read_bytes())
    return digest.hexdigest()[:16]
