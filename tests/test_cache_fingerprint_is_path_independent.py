r"""The cached-figure guard must digest the tree, not the run. **T-129.**

**Why this file exists.** `--replot` on F9 and F10 redraws a committed CSV
instead of recomputing it, and **T-54** closed the staleness that invites: the
CSV carries a digest of the code that made it, and a replot refuses to redraw
numbers this tree did not compute.

That guard had a hole for eight days. It hashed *every ``functions.*`` module
present in `sys.modules`* --- resolved from the live process rather than from a
list --- so the digest depended on **which branch the process had taken**:

  * `functions.spectra.peebles` is imported lazily, inside `build_environment`;
  * the **compute** branch calls that function and hashes peebles;
  * the **replot** branch never calls it, and **did not hash peebles at all**.

Both halves of that are defects and the second is the serious one. A changed
recombination history is exactly what must invalidate a cached spectrum, and on
the branch that *reads* the cache it was outside the digest. The guard against
false validation had a false-validation hole in it.

**A negative control, as finding T-44 requires.** T-44 is a gate that printed
PASS on a `nan`, and the lesson recorded there is that a gate is not tested by
the run that passes it. So this file does not merely check that two digests
agree today; it **reproduces the original defect** on a synthetic tree and
shows that the old rule would have missed what the new one catches.
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _fingerprint import source_fingerprint  # noqa: E402

#: The scripts that stamp a cached CSV and refuse to redraw a foreign one.
CACHED = [
    "scripts/figure_f9_acoustic_spectrum.py",
    "scripts/figure_f10_formation_surface.py",
]

#: Imported lazily inside `build_environment`, which is what exposed T-129.
#: Named rather than discovered, so that moving the import to the top of its
#: module makes this fixture wrong loudly instead of making the test vacuous.
LAZY = "functions.spectra.peebles"


def test_the_lazy_import_is_still_lazy():
    """The fixture, and it fails loudly rather than going quiet.

    If `peebles` became an eager import the two branches would agree for the
    wrong reason and every assertion below would pass while measuring nothing.
    That is the shape of the hazard this file is about, so it is checked.

    **The check is on the replot branch's behaviour, not on any one file's
    text.** An earlier version of this fixture grepped `two_frame.py` for the
    word and failed: the lazy import is further down, and which module holds
    it is not the point. What matters is the property the digest depended on
    --- that importing the figure script does *not* pull the module in.
    """
    # **Snapshot and restore, and that is not boilerplate.** The first
    # version of this test popped every `functions.*` module and did not put
    # them back, so the rest of the suite ran against FRESH module objects
    # while the test files already imported held references to the old ones.
    # A module-level control set on one copy was invisible on the other, and
    # `test_the_newtonian_frame_empties_the_shear_sector` failed in the full
    # run while passing alone. **A test that pollutes `sys.modules` is a test
    # that makes every later failure unattributable**, which is worse than
    # the hazard this file was written to catch.
    saved = {n: m for n, m in sys.modules.items()
             if n.startswith("functions.") or n.startswith("figure_f")}
    try:
        for name in saved:
            sys.modules.pop(name, None)
        importlib.import_module("figure_f10_formation_surface")
        leaked = LAZY in sys.modules
    finally:
        for name in list(sys.modules):
            if name.startswith("functions.") or name.startswith("figure_f"):
                sys.modules.pop(name, None)
        sys.modules.update(saved)
    assert not leaked, (
        f"{LAZY} is now imported by merely importing the figure script, so "
        "the compute and replot branches see the same module set and T-129 "
        "cannot be demonstrated here. Point LAZY at a module that is still "
        "imported lazily — do not delete the test: the hazard is lazy "
        "imports in general, and this one is only the instance that found it.")
    assert importlib.util.find_spec(LAZY) is not None, (
        f"{LAZY} does not exist in the tree at all; the fixture is stale")


@pytest.mark.parametrize("script", CACHED)
def test_the_digest_does_not_depend_on_what_has_been_imported(script: str):
    """The repair: same tree, different `sys.modules`, same digest."""
    before = source_fingerprint(ROOT / script)
    importlib.import_module(LAZY)
    assert LAZY in sys.modules, "fixture: the lazy module did not import"
    after = source_fingerprint(ROOT / script)
    assert before == after, (
        f"{script}: the cache digest changed from {before} to {after} because "
        f"a module was imported, with no file on disk altered. The digest is "
        "measuring the code path rather than the code — T-129. It must be "
        "computed from a declared set walked from disk.")


@pytest.mark.parametrize("script", CACHED)
def test_each_script_has_its_own_identity(script: str):
    """A shared helper must not collapse every cache onto one digest.

    `_fingerprint` hashes the **caller's** file, passed in. A version that
    hashed its own `__file__` would stamp F9's CSV and F10's with the same
    code identity, and either figure could then redraw the other's cache
    without complaint.
    """
    others = [s for s in CACHED if s != script]
    mine = source_fingerprint(ROOT / script)
    for other in others:
        assert mine != source_fingerprint(ROOT / other), (
            f"{script} and {other} digest identically. The helper is not "
            "including the calling script, so the guard cannot tell one "
            "cached artefact from another.")


def test_the_digest_moves_when_a_function_changes(tmp_path):
    """**The negative control.** A gate that only ever passes is not a gate."""
    target = ROOT / "functions" / "spectra" / "integral_solution.py"
    original = target.read_bytes()
    before = source_fingerprint(ROOT / CACHED[0])
    try:
        target.write_bytes(original + b"\n# T-129 control, removed below\n")
        after = source_fingerprint(ROOT / CACHED[0])
    finally:
        target.write_bytes(original)
    assert before != after, (
        "the digest did not move when functions/spectra/integral_solution.py "
        "changed. The declared set is not covering functions/, and a stale "
        "figure would redraw under a CLEAN banner — finding T-54, which is "
        "the failure this whole mechanism exists to prevent.")
    assert source_fingerprint(ROOT / CACHED[0]) == before, (
        "the control did not restore the tree; functions/ is now modified")


@pytest.mark.parametrize("script", CACHED)
def test_the_old_rule_would_have_missed_the_lazy_module(script: str):
    """**What the defect actually was**, reproduced rather than described.

    The superseded implementation is written out here in four lines and run
    against the live process on the *replot* branch's module set. It must come
    out blind to the lazy module — which is the statement that the guard had a
    hole, held as executable evidence rather than as a paragraph in a
    provenance file.
    """
    sys.modules.pop(LAZY, None)
    replot_view = {n for n in sys.modules if n.startswith("functions.")}
    assert LAZY not in replot_view, "fixture: the lazy module is still loaded"

    def superseded(view: set[str]) -> str:
        d = hashlib.sha256()
        for name in sorted(view):
            mod = sys.modules[name]
            if getattr(mod, "__file__", None):
                d.update(name.encode("utf-8"))
                d.update(Path(mod.__file__).read_bytes())
        d.update((ROOT / script).read_bytes())
        return d.hexdigest()[:16]

    stale = superseded(replot_view)
    importlib.import_module(LAZY)
    compute_view = replot_view | {LAZY}
    assert superseded(compute_view) != stale, (
        "the superseded rule gave the same digest with and without the lazy "
        "module, so T-129 cannot be demonstrated and this test is measuring "
        "nothing. Check that LAZY names a module that is actually hashed.")
    assert source_fingerprint(ROOT / script) == source_fingerprint(ROOT / script)
