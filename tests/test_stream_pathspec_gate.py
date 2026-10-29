r"""The one-writer rule is a gate, not a habit. **Finding T-168.**

On 2026-10-28 P1-B edited `handoff/P1T-to-P1B.md` --- P1-T's queue, one
writer by the channel's own rule --- and disclosed it in a commit message
rather than in the channel P1-T reads. Nothing caught it, because nothing was
watching.

`scripts/check_stream_pathspec.py` now watches. This asserts it works, which
is a different question from whether it exists.

WHAT IS ASSERTED
----------------
1. the two streams' forbidden sets are **mutually exclusive and symmetric** on
   the handoff pair --- a table that let both streams write the same file
   would pass every test below while enforcing nothing;
2. a clean set passes;
3. a crossing **fails**, with the other stream named;
4. `--allow` narrows to the named path and **does not** excuse a second one,
   because a flag that excuses everything is a flag that turns the gate off;
5. and the gate refuses rather than passes when it cannot read its input ---
   **T-44**: a gate that cannot see is not a gate that saw nothing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_stream_pathspec import (  # noqa: E402
    FORBIDDEN, WHOSE, offending, touched)

GATE = ROOT / "scripts" / "check_stream_pathspec.py"


def test_the_two_streams_cannot_both_own_the_handoff_pair():
    """The table itself, before anything that reads it.

    If both streams were forbidden from neither file, or from both, every
    assertion below would still pass and the gate would enforce nothing. This
    is the one check that looks at the rule rather than at its enforcement.
    """
    assert "handoff/P1T-to-P1B.md" in FORBIDDEN["P1B"]
    assert "handoff/P1B-to-P1T.md" in FORBIDDEN["P1T"]
    assert "handoff/P1B-to-P1T.md" not in FORBIDDEN["P1B"], (
        "P1-B must be able to write its own queue")
    assert "handoff/P1T-to-P1B.md" not in FORBIDDEN["P1T"], (
        "P1-T must be able to write its own queue")
    for stream in FORBIDDEN:
        assert "docs/STREAMS.md" in FORBIDDEN[stream]
        assert "docs/RESUME.md" in FORBIDDEN[stream]


def test_every_forbidden_pattern_says_whose_it_is():
    """A refusal that does not say what to do instead gets worked around."""
    missing = sorted({p for s in FORBIDDEN.values() for p in s} - set(WHOSE))
    assert not missing, (
        f"forbidden patterns with no owner named: {missing}. The refusal "
        "message would tell the stream it cannot write the file and not "
        "where to raise it instead.")


def test_a_clean_set_passes():
    assert offending(
        ["scripts/figure_f10_formation_surface.py", "provenance/append-guard.txt",
         "handoff/P1B-to-P1T.md", "config/grid-register.toml"], "P1B", []) == []


def test_the_crossing_that_actually_happened_fails():
    """**The gate.** This exact set was committed on 2026-10-28 as `6e51a45`.

    **It scores as TWO crossings now and was one then**, because `README.md`
    moved to P1-T later the same day (`a0c8057`). That is not a flaw in the
    test, it is the one thing a pathspec gate cannot do: it scores against
    *current* custody, so it can refuse a commit being made and can never
    judge one already made. The historical set is kept as the fixture anyway,
    because it is the only set anyone has confirmed was a real crossing.
    """
    bad = offending(
        ["README.md", "handoff/P1B-to-P1T.md", "handoff/P1T-to-P1B.md",
         "provenance/BUNDLE-DEFECTS-v1.md"], "P1B", [])
    paths = [p for p, _ in bad]
    assert paths == ["README.md", "handoff/P1T-to-P1B.md"]
    assert "P1-T's queue" in dict(bad)["handoff/P1T-to-P1B.md"]
    assert "P1-T's since 2026-10-28" in dict(bad)["README.md"]


@pytest.mark.parametrize("stream,path", [
    ("P1B", "docs/STREAMS.md"),
    ("P1B", "docs/RESUME.md"),
    ("P1B", "tests/frame/gen_theory_audit.py"),
    ("P1T", "handoff/P1B-to-P1T.md"),
    ("P1T", "docs/STREAMS.md"),
])
def test_each_forbidden_path_is_refused(stream, path):
    assert offending([path], stream, []) != []


def test_allow_narrows_and_does_not_disable():
    """Naming one crossing must not excuse the next.

    The failure mode a `--force` flag has is that it is passed once for a good
    reason and then stays in the command. `--allow` takes a path, so the
    second crossing is a second argument and a second decision.
    """
    both = ["handoff/P1T-to-P1B.md", "docs/STREAMS.md"]
    assert offending(both, "P1B", ["handoff/P1T-to-P1B.md"]) == [
        ("docs/STREAMS.md", WHOSE["docs/STREAMS.md"])]
    assert offending(both, "P1B", both) == []


def test_there_is_no_force_flag():
    """A gate with an off switch is a gate nobody reads twice."""
    text = GATE.read_text(encoding="utf-8")
    for flag in ("--force", "--no-verify", "--skip"):
        assert f'"{flag}"' not in text, (
            f"{flag} would turn this gate off wholesale. A deliberate "
            "crossing names its path with --allow; there is nothing else to "
            "offer it.")


def test_the_gate_refuses_when_it_cannot_see(tmp_path):
    """**T-44.** Not a git tree, so it cannot know what changed: refuse.

    T-44 is a gate that printed PASS on a `nan`. The lesson is that the
    dangerous state is not *failing*, it is *passing without having looked* ---
    and a pathspec gate that cannot read a repository has looked at nothing.

    **The first version of this test was itself blind**, which is the control
    doing its job on the instrument rather than on the subject. It ran the
    script with `cwd=tmp_path` and expected a refusal; the script reads
    `git -C ROOT`, so `cwd` is irrelevant and it cheerfully passed on the
    bundle's own clean tree. A negative control that fails for the wrong
    reason is worth no more than one that does not fail at all --- so the
    function is called directly, against a directory that really is not a
    repository.
    """
    (tmp_path / "not-a-repo").mkdir()
    with pytest.raises(SystemExit) as caught:
        touched(tmp_path / "not-a-repo")
    assert "cannot see what changed" in str(caught.value)


def test_the_gate_runs_on_this_tree():
    """And it must pass here, or this commit is itself a crossing."""
    out = subprocess.run(
        [sys.executable, "-I", str(GATE), "--stream", "P1B"],
        capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stdout + out.stderr
