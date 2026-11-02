r"""The one-writer rule is a gate, not a habit. **Findings T-168 and T-188.**

On 2026-10-28 P1-B edited `handoff/P1T-to-P1B.md` --- P1-T's queue, one
writer by the channel's own rule --- and disclosed it in a commit message
rather than in the channel P1-T reads. Nothing caught it, because nothing was
watching. `scripts/check_stream_pathspec.py` now watches.

**T-188: it watches by READING `docs/CUSTODY.md`'s custody block, not by
restating it.** The restated table drifted in the four days between P1-B
asking Coordination whether to keep it and the block being published. These
tests therefore assert against the block itself wherever they can, so that a
custody change is a change in one place and the tests follow it.

WHAT IS ASSERTED
----------------
1. the block gives each handoff file to its own stream and only to it;
2. every owner the block names has a "raise it here instead" message;
3. a clean set passes, and the crossing that actually happened fails;
4. the most specific pattern wins, so `tests/frame/**` carves out of
   `tests/**` whatever order the block lists them in;
5. an unassigned path WARNS and is not refused --- the block's own rule;
6. `--allow` narrows and does not disable, and there is no `--force`;
7. the gate refuses when it cannot read its input OR its authority --- **T-44**:
   a gate that cannot see is not a gate that saw nothing;
8. and no second copy of the table survives in the gate.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_stream_pathspec import (  # noqa: E402
    RAISE_IN, STREAMS, classify, custody_rules, owner_of, touched)

GATE = ROOT / "scripts" / "check_stream_pathspec.py"
RULES = custody_rules()


def _refused(paths, stream, allow=()):
    return classify(paths, stream, list(allow), RULES)[0]


def test_each_handoff_file_belongs_to_its_own_stream_and_only_to_it():
    """The block itself, before anything that reads it.

    If the block gave both streams both files, or neither, every assertion
    below would still pass and the gate would enforce nothing. This is the one
    check that looks at the rule rather than at its enforcement.
    """
    assert owner_of("handoff/P1T-to-P1B.md", RULES)[0] == "P1-T"
    assert owner_of("handoff/P1B-to-P1T.md", RULES)[0] == "P1-B"
    assert owner_of("handoff/P1B-to-coordination.md", RULES)[0] == "P1-B"
    assert owner_of("docs/CUSTODY.md", RULES)[0] == "COORD"


def test_every_owner_the_block_names_says_where_to_raise_it():
    """A refusal that does not say what to do instead gets worked around."""
    owners = {o for o, _ in RULES}
    missing = sorted(owners - set(RAISE_IN))
    assert not missing, (
        f"the custody block names owners with no message: {missing}. A "
        "refusal would say the file cannot be written and not where to go.")


def test_a_clean_set_passes():
    assert _refused(
        ["scripts/figure_f10_formation_surface.py",
         "provenance/append-guard.txt", "handoff/P1B-to-P1T.md",
         "config/grid-register.toml"], "P1B") == []


def test_the_crossing_that_actually_happened_fails():
    """**The gate.** This exact set was committed on 2026-10-28 as `6e51a45`.

    It scores as TWO crossings now and was one then, because `README.md`
    moved to P1-T later that day. A pathspec gate scores against *current*
    custody, so it can refuse a commit being made and never judge one already
    made. The historical set is kept as the fixture anyway, because it is the
    only set anyone has confirmed was a real crossing.
    """
    bad = _refused(
        ["README.md", "handoff/P1B-to-P1T.md", "handoff/P1T-to-P1B.md",
         "provenance/BUNDLE-DEFECTS-v1.md"], "P1B")
    assert sorted(p for p, _ in bad) == ["README.md", "handoff/P1T-to-P1B.md"]
    assert all("handoff/P1B-to-P1T.md" in msg for _, msg in bad), (
        "a P1-T refusal must tell P1-B to raise it in its own queue")


@pytest.mark.parametrize("stream,path", [
    ("P1B", "tests/frame/gen_theory_audit.py"),
    # Deliberately NOT the live edition's filename: the hygiene gate refused
    # the first draft for spelling it, because six copies of that name is
    # how the v1.2.0 archive shipped two stale ones (T-50). This tests the
    # pattern `supplementary-materials/**`, which needs a path, not an edition.
    ("P1B", "supplementary-materials/any-build-output.pdf"),
    ("P1B", "source/anything.tex"),
    ("P1B", "docs/CUSTODY.md"),
    ("P1B", "correction/anything.md"),
    ("P1T", "handoff/P1B-to-P1T.md"),
    ("P1T", "scripts/figure_f9_acoustic_spectrum.py"),
    ("P1T", "functions/spectra/two_frame.py"),
])
def test_each_other_owners_path_is_refused(stream, path):
    assert _refused([path], stream) != []


def test_the_carve_out_wins_whatever_order_the_block_lists_it_in():
    """`tests/frame/**` is P1-T's inside P1-B's `tests/**`.

    **Most specific wins**, computed from the patterns rather than from their
    position, so reordering the block cannot silently hand P1-T's frame
    instruments to P1-B. Checked against both orders explicitly.
    """
    forward = [("P1-T", "tests/frame/**"), ("P1-B", "tests/**")]
    backward = list(reversed(forward))
    for rules in (forward, backward):
        assert owner_of("tests/frame/c11_kernel_partner.py", rules)[0] == "P1-T"
        assert owner_of("tests/test_two_route.py", rules)[0] == "P1-B"


def test_an_unassigned_path_warns_and_is_not_refused():
    """The block's own rule: *"An unlisted path is UNASSIGNED: warn, do not
    refuse."* The gate must not re-hardcode a refusal for a gap in the block
    --- that would be the second copy T-188 removed --- so a gap is reported
    and left for Coordination to close."""
    refused, unassigned = classify(
        ["a/path/the/block/never/mentions.txt"], "P1B", [], RULES)
    assert refused == []
    assert unassigned == ["a/path/the/block/never/mentions.txt"]


def test_allow_narrows_and_does_not_disable():
    """Naming one crossing must not excuse the next.

    The failure mode a `--force` flag has is that it is passed once for a good
    reason and then stays in the command. `--allow` takes a path, so the
    second crossing is a second argument and a second decision.
    """
    both = ["handoff/P1T-to-P1B.md", "docs/CUSTODY.md"]
    left = _refused(both, "P1B", ["handoff/P1T-to-P1B.md"])
    assert [p for p, _ in left] == ["docs/CUSTODY.md"]
    assert _refused(both, "P1B", both) == []


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

    **The first version of this test was itself blind**: it ran the script
    with `cwd=tmp_path`, but the script reads `git -C ROOT`, so it passed on
    the bundle's own clean tree. The function is called directly, against a
    directory that really is not a repository.
    """
    (tmp_path / "not-a-repo").mkdir()
    with pytest.raises(SystemExit) as caught:
        touched(tmp_path / "not-a-repo")
    assert "cannot see what changed" in str(caught.value)


@pytest.mark.parametrize("content", [
    None,                                         # the file does not exist
    "# CUSTODY\n\nno block here at all\n",        # the block is missing
    "```custody\n# only a comment\n```\n",       # the block is empty
])
def test_the_gate_refuses_when_its_authority_is_unreadable(tmp_path, content):
    """**T-44 for the authority, which T-188 introduced.**

    Reading the table instead of restating it opens a new way to pass without
    looking: if the block cannot be found, every path is unassigned and the
    gate would print warnings and PASS. So an unreadable, missing or empty
    block is a refusal, not an empty rulebook.
    """
    doc = tmp_path / "CUSTODY.md"
    if content is not None:
        doc.write_text(content, encoding="utf-8")
    with pytest.raises(SystemExit) as caught:
        custody_rules(doc)
    assert "FAIL" in str(caught.value)


def test_no_second_copy_of_the_table_survives_in_the_gate():
    """**T-188's structural guard.** The gate may not carry an owner table.

    The old gate's `FORBIDDEN` dict was the second copy; it drifted. This
    asserts no module-level dict or tuple in the gate maps a path PATTERN to
    anything --- `STREAMS` maps CLI names and `RAISE_IN` maps owners to
    messages, and neither contains a path pattern as a key.
    """
    tree = ast.parse(GATE.read_text(encoding="utf-8"))
    offenders = []
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue
        name = getattr(targets[0], "id", "")
        if name == "FORBIDDEN":
            offenders.append(name)
        if isinstance(value, ast.Dict):
            for k in value.keys:
                if (isinstance(k, ast.Constant) and isinstance(k.value, str)
                        and ("/" in k.value or "*" in k.value
                             or k.value.endswith(".md"))):
                    offenders.append(f"{name}[{k.value!r}]")
    assert not offenders, (
        f"the gate restates custody again: {offenders}. Read docs/CUSTODY.md's "
        "custody block instead; a map kept in two places is kept in neither.")
    assert set(STREAMS.values()) <= {o for o, _ in RULES}, (
        "a CLI stream names an owner the custody block does not know")


def test_the_gate_runs_on_this_tree():
    """And it must pass here, or this commit is itself a crossing."""
    out = subprocess.run(
        [sys.executable, "-I", str(GATE), "--stream", "P1B"],
        capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stdout + out.stderr
