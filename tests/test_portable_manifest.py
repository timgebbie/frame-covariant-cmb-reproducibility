r"""Finding T-15: the release route has to be runnable on a second machine.

`--strict` regenerates every artefact and then hashes it, so before this it
could only pass where the bytes were made. The PI's Windows run against a
Linux-generated manifest reported twelve mismatches: the seven renderings and
the supplement, which were expected, **and three CSVs**, which were not — plain
text at `%.12e`, differing in their last digits because BLAS and libm differ.

So byte-identity is the wrong criterion for any *generated* artefact, not only
for pictures. `PORTABLE-MANIFEST-SHA256.txt` is what `--strict` binds on: it
drops the renderings and canonicalises every number to
`SIGNIFICANT_FIGURES`. `FILE-MANIFEST-SHA256.txt` stays exactly as it was,
`sha256sum -c`-able, and becomes a within-machine drift report.

**These tests are the negative control for that design.** A gate that tolerates
platform noise is only worth having if it still fails on a real change, so both
halves are asserted here. Without the second one, the first would be
indistinguishable from switching the gate off.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from make_manifests import (  # noqa: E402
    SIGNIFICANT_FIGURES,
    _canonicalise,
    artefact_class,
)

PROBE = ROOT / "outputs" / "f4-correlation.csv"

_FLOAT = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _check() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/make_manifests.py", "--check"],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )


def _perturb(text: str, relative: float) -> str:
    """Move every float by `relative`, which is what another BLAS does."""
    def one(m: re.Match) -> str:
        token = m.group(0)
        if "e" not in token and "." not in token:
            return token
        try:
            value = float(token)
        except ValueError:                      # pragma: no cover
            return token
        return repr(value * (1.0 + relative)) if value else token

    return _FLOAT.sub(one, text)


@pytest.mark.parametrize("rel,expected", [
    ("figures/f3-angular-spectrum-v1.0.0.png", "rendered"),
    ("figures/f6-approximations-v1.1.0.pdf", "rendered"),
    ("supplementary-materials/supplement-v1.0.0.pdf", "rendered"),
    ("diagnostics/d1-sign-control-v1.0.0.png", "rendered"),
    ("outputs/f4-correlation.csv", "numeric"),
    ("diagnostics/d5-sachs-wolfe-v1.0.0.txt", "numeric"),
    ("tables/equations-v1.0.0.csv", "numeric"),
    ("functions/frames.py", "exact"),
    ("README.md", "exact"),
])
def test_artefact_class_is_derived_from_the_path(rel: str, expected: str):
    """**Derived, never listed.** A hand-maintained list is one more thing to
    forget when a file is added, which is what T-1 and T-16 are both about."""
    assert artefact_class(rel) == expected


def test_canonicalisation_keeps_integers_and_rounds_floats():
    """Integers are not measurements and must survive untouched."""
    out = _canonicalise("model,7,1.23456789012345e-13,2.0")
    assert ",7," in out, "a plain integer was rewritten as a float"
    assert "1.23456789e-13" in out
    assert f"{2.0:.{SIGNIFICANT_FIGURES - 1}e}" in out


def test_platform_float_noise_does_not_block_the_release(tmp_path):
    r"""The T-15 case: last-digit noise must leave the binding gate passing.

    Asserts the *exit code*, not the text, because the exit code is what
    `run_all.py --strict` acts on and therefore what decides whether a second
    person can run the release route at all.
    """
    backup = PROBE.read_bytes()
    try:
        PROBE.write_text(_perturb(PROBE.read_text(encoding="utf-8"), 3e-16),
                         encoding="utf-8")
        result = _check()
        assert result.returncode == 0, (
            "platform float noise blocked the release route:\n" + result.stdout)
        assert "PASS  PORTABLE-MANIFEST-SHA256.txt" in result.stdout
        assert "DRIFT" in result.stdout, "the byte difference should still be reported"
    finally:
        PROBE.write_bytes(backup)


def test_a_real_change_still_fails(tmp_path):
    """**The control.** Without this, the test above is 'the gate was disabled'.

    A change far above the canonicalisation cut must be release-blocking.
    """
    backup = PROBE.read_bytes()
    try:
        PROBE.write_text(_perturb(PROBE.read_text(encoding="utf-8"), 1e-4),
                         encoding="utf-8")
        result = _check()
        assert result.returncode == 1, (
            "a 1e-4 change passed the binding gate:\n" + result.stdout)
        assert "FAIL  PORTABLE-MANIFEST-SHA256.txt" in result.stdout
    finally:
        PROBE.write_bytes(backup)


def test_renderings_are_outside_the_binding_manifest():
    """A PNG differing in font hinting carries no scientific difference.

    It is still hashed in `FILE-MANIFEST-SHA256.txt`, so within-machine drift is
    visible; it is simply not what the release stands on.
    """
    portable = (ROOT / "PORTABLE-MANIFEST-SHA256.txt").read_text(encoding="utf-8")
    byte_manifest = (ROOT / "FILE-MANIFEST-SHA256.txt").read_text(encoding="utf-8")

    assert "f3-angular-spectrum-v1.0.0.png" in byte_manifest
    assert "f3-angular-spectrum-v1.0.0.png" not in portable
    assert "supplement-v1.0.0.pdf" in byte_manifest
    assert "supplement-v1.0.0.pdf" not in portable
    # and the content half is still there
    assert "functions/frames.py" in portable
