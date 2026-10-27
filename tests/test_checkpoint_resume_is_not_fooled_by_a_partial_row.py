r"""A configuration half-written must be recomputed, not resumed as complete.

**Finding T-162's repair, under test. The defect cost a measurement.**

`scripts/_resumable.Checkpoint` lets a long diagnostic survive a crash: each
completed row is flushed to disk as it is produced, and a resumed run skips
whatever is already there. The skip was decided by `any()` — *is there a row
under this configuration?* — and a caller writes **one row per metric**, so a
run killed between the first row and the last leaves a configuration that is
present but short.

`any()` then calls it done. The resume skips it. **The gap is permanent**,
because the instrument will never recompute what it believes it already has.

On 2026-10-27 D36 died on an `fsync` partway through
`bracket_at_w || PLANCK`, leaving three of its six metrics. The resumed run
skipped it and the summary table carried `nan` in one cell — on the one
background that matters most. It was caught by reading the table, which is the
weakest check in the bundle and not a gate at all.

WHAT IS ASSERTED
----------------
Three things, and the third is the one that matters:

1. a complete configuration resumes (the feature still works);
2. a **short** configuration does not (the repair);
3. a caller that passes no count keeps the old behaviour, so this cannot
   silently change an instrument that has not been taught its row count.

And a fourth, which is the negative control **T-44** requires: the test that
catches the short row must itself fail when handed a complete one, or it is
asserting nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _resumable import Checkpoint  # noqa: E402

FIELDS = ("background", "metric", "value")


def _cp(tmp_path: Path, name: str = "probe.csv") -> Checkpoint:
    return Checkpoint(tmp_path / name, FIELDS)


def test_a_complete_configuration_resumes(tmp_path):
    """The feature itself: three of three rows is done."""
    cp = _cp(tmp_path)
    for m in ("a", "b", "c"):
        cp.add("cfg || EdS", background="EdS", metric=m, value="1.0")

    fresh = _cp(tmp_path)
    assert fresh.has("cfg || EdS", expect=3)
    assert fresh.has("cfg || EdS")


def test_a_partial_configuration_is_recomputed(tmp_path):
    """**The repair.** Two of three rows is not done, and must say so."""
    cp = _cp(tmp_path)
    for m in ("a", "b"):
        cp.add("cfg || PLANCK", background="PLANCK", metric=m, value="1.0")

    fresh = _cp(tmp_path)
    assert not fresh.has("cfg || PLANCK", expect=3), (
        "a configuration with two of its three rows on disk reported as "
        "complete. That is the D36 defect: the resume skips it, the summary "
        "carries `nan`, and the instrument never recomputes it because it "
        "believes it already has."
    )


def test_an_untaught_caller_is_unchanged(tmp_path):
    """No `expect`, no change — the repair cannot break an instrument silently.

    Five diagnostics share this class. Changing the meaning of `has` for all
    of them at once, including the ones whose row count nobody has checked,
    would be a worse defect than the one being fixed.
    """
    cp = _cp(tmp_path)
    cp.add("cfg || LCDM", background="LCDM", metric="a", value="1.0")

    fresh = _cp(tmp_path)
    assert fresh.has("cfg || LCDM"), (
        "a caller that passes no count must get the old behaviour"
    )


def test_an_absent_configuration_is_absent(tmp_path):
    """Zero rows is not a partial row, and must not print a partial warning."""
    cp = _cp(tmp_path)
    cp.add("other", background="EdS", metric="a", value="1.0")

    fresh = _cp(tmp_path)
    assert not fresh.has("cfg || EdS", expect=3)
    assert not fresh.has("cfg || EdS")


def test_the_gate_fails_on_a_complete_row(tmp_path):
    """**The negative control, as T-44 requires.**

    T-44 is a gate that printed PASS on a `nan`, and its lesson is that a gate
    is not tested by the run that passes it. So the assertion in
    `test_a_partial_configuration_is_recomputed` is handed a *complete*
    configuration here and must stop firing — otherwise it would reject every
    resume, including the correct ones, and the class would be useless rather
    than wrong.
    """
    cp = _cp(tmp_path)
    for m in ("a", "b", "c"):
        cp.add("cfg || EdS", background="EdS", metric=m, value="1.0")

    fresh = _cp(tmp_path)
    with pytest.raises(AssertionError):
        assert not fresh.has("cfg || EdS", expect=3)


def test_every_checkpointed_diagnostic_declares_its_row_count():
    """A count nobody passes protects nothing.

    Discovered from the tree rather than listed, for the reason every other
    registry in this bundle is: a list of instruments drifts, and this one
    would drift the day a sixth diagnostic starts checkpointing.
    """
    import re

    offenders = []
    for path in sorted((ROOT / "scripts").glob("diagnostic_d*.py")):
        text = path.read_text(encoding="utf-8")
        if "Checkpoint(" not in text:
            continue
        if not re.search(r"\.has\([^)]*expect\s*=", text):
            offenders.append(path.name)

    # D29 and D32 predate the repair and are not rerun; they are named here
    # rather than silently excluded, so the exemption is visible and shrinks.
    known = {"diagnostic_d29_the_identity.py",
             "diagnostic_d32_isw_discriminator.py"}
    assert set(offenders) <= known, (
        f"checkpointed diagnostics that can resume a partial configuration: "
        f"{sorted(set(offenders) - known)}. Pass `expect=` the number of rows "
        "the instrument writes per configuration — see T-162."
    )
