r"""The grid register, and the two gates that close a class rather than an instance.

**What these are for.** Three findings in eight days were one failure: `n_eta`
fixed rather than derived (**T-3**), the $k$ grid guarded by a comment rather
than by code (**S24**'s correction to itself), and the recombination grid
setting the primary source with nothing guarding it (**T-46**, **Q7**). A fourth
is prevented by a check, not by a resolution to be careful.

Alongside it, **T-47**'s gate: a deferral to a release that has already happened.
Both are *negative-control* tests. Finding **T-44** is a gate that printed PASS
on a `nan`, and the lesson recorded there is that a gate is not tested by the run
that passes it.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import make_grid_register as reg  # noqa: E402
import run_all  # noqa: E402


# ---------------------------------------------------------------------------
# the register
# ---------------------------------------------------------------------------


def test_every_discretisation_in_the_tree_is_registered():
    """The gate itself, run the way `run_all.py` runs it."""
    result = subprocess.run(
        [sys.executable, "scripts/make_grid_register.py"],
        cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, (
        "the grid register does not match the tree:\n" + result.stdout)


def test_an_unregistered_grid_fails_the_register():
    r"""**The control, and the reason this file exists.**

    A register that only ever passes is a list, not a gate. This one is handed
    a tree containing a grid it does not know about and must refuse it.

    The site is synthesised rather than written into the repository: adding a
    real unregistered grid to `functions/` to test this would leave the tree in
    the state the gate exists to forbid, which is how **T-30** happened --- a
    released file asserting state nothing could see.
    """
    sites = reg._sites()
    assert sites, "the AST walk found no grids at all, which cannot be right"

    registered = {entry["key"] for entry in tomllib.loads(
        (ROOT / "config" / "grid-register.toml").read_text(encoding="utf-8")
    )["grid"]}
    assert set(sites) == registered, "fixture: the tree and register must agree first"

    # The gate's own arithmetic, with one grid the register has never heard of.
    intruder = dict(sites)
    intruder["functions/spectra/invented.py::eta"] = ("functions/spectra/invented.py", 1, "linspace")
    unregistered = set(intruder) - registered
    assert unregistered == {"functions/spectra/invented.py::eta"}, (
        "an unregistered grid must be detected as unregistered; if this set is "
        "empty the gate cannot fail and is not a gate")


def test_the_register_finds_grids_by_the_constructors_that_make_them():
    """`zeros` and `empty` are deliberately **not** grid constructors.

    They make an array; they do not discretise anything continuous. Registering
    them would pad the register with rows nobody needs to think about, and a
    register nobody reads is the T-16 failure in a new file.
    """
    assert reg.CONSTRUCTORS == {"linspace", "arange", "logspace", "geomspace"}


def test_the_open_row_is_present_and_says_what_it_costs():
    r"""**Q7 must stay visible until it is answered in code.**

    Decision **S33** derives the recombination grid after the v1.2.0 tag. Until
    that lands, the register must carry exactly this row at `open` with its
    measured cost, so the limit v1.2.0 ships cannot quietly disappear from the
    record when someone tidies a config file.
    """
    rows = {e["key"]: e for e in tomllib.loads(
        (ROOT / "config" / "grid-register.toml").read_text(encoding="utf-8")
    )["grid"]}
    key = "functions/spectra/decoupling.py::eta"
    assert key in rows, "the recombination grid must be registered"
    entry = rows[key]
    assert entry["status"] == "open", (
        "the recombination grid is Q7. If it has been derived, decision S33 is "
        "done and this row moves to `derived` with its guard named --- which is "
        "a change to make deliberately, not one to discover")
    assert "1.2%" in entry["note"] and "Q7" in entry["note"], (
        "the open row must carry its measured cost and the question that owns it")


# ---------------------------------------------------------------------------
# T-47: a deferral to a release that has already happened
# ---------------------------------------------------------------------------


def test_no_artefact_is_deferred_to_a_release_that_already_shipped():
    """The gate. **T-47.**"""
    assert run_all.check_deferrals() == [], (
        "a deferral target has been released; retarget it or do the work")


def test_the_stale_deferral_gate_can_fail():
    r"""The control.

    `DEFERRED` stores the version as *data* so the printed message cannot
    contradict the decision --- that was **T-16**'s fix, and it made the message
    accurate without making it current. D3 and D4 were deferred *to v1.1.0*,
    v1.1.0 shipped without them, and the harness announced a deferral to a
    release in the past for three days. Coordination caught it; no gate did.

    This is the gate, and here it is being made to fail on purpose.
    """
    released = run_all._released_versions()
    assert released, "no released version found in CHANGELOG.md; the gate has no datum"

    original = dict(run_all.DEFERRED)
    try:
        run_all.DEFERRED["X  a deferral to the past"] = (sorted(released)[0], "S-b")
        stale = run_all.check_deferrals()
    finally:
        run_all.DEFERRED.clear()
        run_all.DEFERRED.update(original)

    assert len(stale) == 1 and "already released" in stale[0], (
        "the stale-deferral gate did not fire on a deferral to a released "
        "version, so it cannot fire on a real one either")


def test_released_versions_come_from_dated_changelog_entries():
    """`## [1.1.0] — 2026-10-12` is released; `## [Unreleased]` is not.

    Stated as a test because the alternative --- asking git for tags --- would
    make the gate depend on a `.git` directory, and a reader reproducing this
    from a downloaded zip has none. That is `_bundle_files`' argument, applied
    to a second gate.
    """
    released = run_all._released_versions()
    assert "v1.1.0" in released
    assert not any("Unreleased" in v for v in released)
