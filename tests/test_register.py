"""The implementation register must describe the code that actually exists.

`config/implementation-register.toml` links every published equation to the
module and object implementing it and to the test checking it. The supplement's
audit tables are generated from it. That is only worth anything if the register
cannot drift, so this file resolves every reference in it.

A rename therefore breaks the build rather than quietly falsifying a table in a
published supplement.
"""

from __future__ import annotations

import importlib
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

with (ROOT / "config" / "implementation-register.toml").open("rb") as _fh:
    REGISTER = tomllib.load(_fh)

IMPLEMENTED = [e for e in REGISTER["equations"] if e.get("module")]
PENDING = [e for e in REGISTER["equations"] if not e.get("module")]


@pytest.mark.parametrize("entry", IMPLEMENTED, ids=lambda e: e["key"])
def test_registered_code_resolves(entry):
    """Every module and object named in the register exists."""
    module = importlib.import_module(entry["module"])
    if entry.get("object"):
        assert hasattr(module, entry["object"]), f"{entry['module']}.{entry['object']}"


@pytest.mark.parametrize("entry", IMPLEMENTED, ids=lambda e: e["key"])
def test_registered_test_exists(entry):
    """Every named test exists in the suite."""
    name = entry.get("test")
    if not name:
        pytest.skip("no test registered for this entry")
    found = any(
        name in path.read_text(encoding="utf-8")
        for path in (ROOT / "tests").glob("test_*.py")
    )
    assert found, f"registered test not found in the suite: {name}"


def test_every_source_key_is_defined():
    keys = set(REGISTER["sources"])
    for entry in REGISTER["equations"]:
        assert entry["source"] in keys, entry["key"]


def test_pending_entries_are_declared_pending():
    """An entry with no code must say so in its note, so the table reads honestly."""
    for entry in PENDING:
        assert "PENDING" in entry.get("note", ""), entry["key"]


def test_parameter_provenance_is_one_of_the_allowed_kinds():
    """Every number is attributed, and 'standard' is distinguished from sourced.

    A value that is standard in the field but not in the source paper must not be
    presented as if the paper supplied it.
    """
    allowed = {"stipulated", "standard", "derived"}
    for p in REGISTER["parameters"]:
        kind = p["source"]
        assert kind in allowed or kind.startswith("AnnalsII"), (p["symbol"], kind)
