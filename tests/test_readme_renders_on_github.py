"""The README's mathematics must render **on GitHub**, not merely be valid LaTeX.

**Finding T-120, and it is M13 again: a public artefact is written for the
reader it has.** The reader the README has is GitHub's markdown renderer, which
runs markdown's emphasis parser *before* the maths one. Two patterns that are
perfectly good LaTeX are destroyed by that order, and both were shipped:

1.  **A bare ``*`` inside a ``$$`` block.** ``\\eta_*`` is the standard spelling
    of conformal time at last scattering and the supplement uses it throughout,
    correctly --- LaTeX has no emphasis parser. In a GitHub ``$$`` block the
    asterisks **pair up as emphasis** and are consumed, so five ``\\eta_*`` in
    one display became ``\\eta__`` and the block rendered as the words
    *"Missing open brace for subscript"* above a wall of raw source. The (102)
    display, which is the centre of the physics chain, was unreadable on the
    repository front page. ``\\ast`` is the fix and is what this file enforces.

2.  **Inline ``$...$`` immediately after a hyphen** --- ``high-$\\ell$``,
    ``post-$\\beta$``, ``per-$k$``. These render as literal source.

Neither is caught by anything else: the markdown is well-formed, the LaTeX is
well-formed, every link resolves, and the file passes every other test in this
directory. It is only wrong *where it is read*, which is the one place no test
was looking. Found by the PI, from the rendered page, 2026-10-22 --- which is
how all three previous instances of this class were found, and the reason this
file exists rather than a fourth.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

#: Only the README and anything else markdown-rendered. **Not** the supplement:
#: `.tex` goes to LaTeX, which has no emphasis parser, and `\eta_*` is right
#: there. Enforcing this on the supplement would be the mirror-image mistake.
MARKDOWN = ["README.md"]


def _display_blocks(text: str) -> list[tuple[int, str]]:
    """Every ``$$…$$`` block, with the 1-based line it starts on."""
    out = []
    for m in re.finditer(r"\$\$(.*?)\$\$", text, re.S):
        out.append((text[: m.start()].count("\n") + 1, m.group(1)))
    return out


@pytest.mark.parametrize("name", MARKDOWN)
def test_the_display_delimiters_pair(name: str) -> None:
    r"""An odd number of ``$$`` inverts prose and mathematics for the rest of the page.

    **Finding T-120b, 2026-10-23, and it is the worse half of T-120.** A
    rendering note was added to stop the next hand undoing the asterisk fix.
    It said *"inside ``$$`` blocks this file writes ..."* — and that backticked
    ``$$`` is a 23rd delimiter. **GitHub's maths renderer counts it**; backticks
    do not hide it. It paired with the next block's opener, so the note and the
    prose after it rendered as mathematics, every real display rendered as
    prose, and the page was unreadable from that line to the end.

    The note warning about rendering is what broke the rendering, which is the
    sharpest possible argument for this test: **the author of a rendering rule
    is not thereby able to see a rendering failure.** Only counting can.

    This runs before the content checks below because a file that fails it has
    no well-defined display blocks at all, so every other result in this module
    would be measured against the wrong spans.
    """
    text = (ROOT / name).read_text(encoding="utf-8")
    n = text.count("$$")
    assert n % 2 == 0, (
        f"{name}: {n} occurrences of '$$' — an odd count. One of them is "
        f"stray, and from it onwards GitHub renders prose as mathematics and "
        f"mathematics as prose. Backticks do NOT exempt it; write 'display "
        f"block' in words instead.")


@pytest.mark.parametrize("name", MARKDOWN)
def test_display_blocks_are_one_source_line(name: str) -> None:
    r"""A newline inside ``$$…$$`` becomes a layout break on GitHub.

    **Finding T-120d.** LaTeX treats a source newline as a space, so a
    multi-line display is identical mathematics — and GitHub's preprocessor
    does not: the published page rendered (68), (71) and (GDE99 37) as
    vertical stacks of fragments. **The ``\tag{}`` → ``\quad()`` pass of the
    same morning did not touch line structure and so did not fix it**, which
    is how this was separated from T-120c rather than confused with it.

    Joining on whitespace cannot change what an expression means, so this is
    the one rule in this file with no cost attached to obeying it.

    **This test is also the answer to a question Coordination asked:** can the
    suite see a layout break at all? It can see *this* one, because line count
    is a property of the source. It cannot see width — display 8 is 347
    characters and whether that wraps in a 562 px column is a fact about the
    rendered page, not about the file. **So the manual look stays a named
    release step and is not an accident**; this test narrows what the look has
    to catch, it does not replace it.
    """
    text = (ROOT / name).read_text(encoding="utf-8")
    bad = [(text[: m.start()].count("\n") + 1, m.group(1).count("\n"))
           for m in re.finditer(r"\$\$(.*?)\$\$", text, re.S)
           if "\n" in m.group(1)]
    assert not bad, (
        f"{name}: display blocks with internal newlines at (line, breaks) "
        f"{bad}. GitHub renders each as a layout break and the equation "
        f"comes out as a vertical stack of fragments. Join the block onto "
        f"one source line — LaTeX reads a newline as a space, so the "
        f"mathematics is untouched.")


#: Commands that GitHub's maths pipeline cannot render, with the mechanism.
#: Each was read off the LIVE page's DOM, not inferred from documentation.
BANNED = {
    r"\tag{": (
        "emits <mlabeledtr>, which MathML Core -- what Chrome, Safari and "
        "Firefox actually implement -- does not support. The browser cannot "
        "lay out the row, falls back to rendering each child as its own "
        "block, and EVERY ATOM OF THE EQUATION STACKS VERTICALLY. Carry the "
        "number as \\quad(68) instead: that is an mtext in an mrow and "
        "touches no table construct."),
    r"\big": (
        "GitHub's MathJax configuration rejects it -- the live page carried "
        "'Missing or unrecognized delimiter for \\big' as a red error box. "
        "Use the plain delimiter."),
    r"\Big": (
        "same as \\big: 'Missing or unrecognized delimiter'. Use the plain "
        "delimiter."),
}


@pytest.mark.parametrize("name", MARKDOWN)
def test_no_command_github_cannot_render(name: str) -> None:
    r"""**Finding T-120c, 2026-10-23, and it is the third of three in two days.**

    T-120 was ``\eta_*`` eaten by the emphasis parser. T-120b was a stray
    backticked ``$$`` — *introduced by the note written to prevent T-120*.
    T-120c is ``\tag{}``, added the same day to carry the published equation
    numbers the PI asked for, which stacked all eleven displays atom by atom.

    **Each failure was introduced by the fix to the previous one, and all
    three passed every test in this repository.** The tests above check source
    patterns already known; by construction they cannot catch the next unknown
    one. This list can only ever be a record of what has already gone wrong.

    **So the test that matters is not in this file.** It is the release rule:
    *no change to README.md is complete until the rendered GitHub page has
    been loaded and its DOM read.* V12 — every figure rendered and looked at —
    already says this about figures; prose is what a colleague reads first and
    it was never covered.
    """
    text = (ROOT / name).read_text(encoding="utf-8")
    found = {cmd: text.count(cmd) for cmd in BANNED if cmd in text}
    assert not found, "\n".join(
        f"{name}: {n}x '{cmd}' — {BANNED[cmd]}" for cmd, n in found.items())


@pytest.mark.parametrize("name", MARKDOWN)
def test_no_bare_asterisk_in_a_display_block(name: str) -> None:
    """``\\eta_*`` in a ``$$`` block is eaten by markdown. Use ``\\eta_\\ast``."""
    text = (ROOT / name).read_text(encoding="utf-8")
    offenders = [(line, block.strip()[:70])
                 for line, block in _display_blocks(text) if "*" in block]
    assert not offenders, (
        f"{name}: a bare '*' inside $$…$$ is parsed as markdown emphasis "
        f"before the maths renderer sees it, and the subscript is destroyed. "
        f"Write \\ast. Offending blocks: {offenders}")


@pytest.mark.parametrize("name", MARKDOWN)
def test_no_bare_asterisk_in_inline_maths(name: str) -> None:
    r"""``$z_*=1114.5$`` is the same defect one dollar sign smaller.

    CommonMark's asymmetry is the whole of it: ``*`` opens emphasis
    **intraword** and ``_`` does not, so ``a_b_c`` is safe and ``a*b*c`` is
    not. That is why ``\tau_{A_\ell}`` has always rendered and ``\eta_*``
    never did. One bare ``*`` is enough, because the ``**bold**`` markers
    elsewhere in the same paragraph supply its partner.
    """
    text = (ROOT / name).read_text(encoding="utf-8")
    body = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)   # displays covered above
    hits = [(body[: m.start()].count("\n") + 1, m.group(0))
            for m in re.finditer(r"(?<!\$)\$(?!\s)([^$\n]{1,80}?)(?<!\s)\$(?!\$)",
                                 body)
            if "*" in m.group(1)]
    assert not hits, (
        f"{name}: a bare '*' inside inline $…$ pairs with the paragraph's "
        f"emphasis markers. Write \\ast. Found: {hits}")


@pytest.mark.parametrize("name", MARKDOWN)
def test_no_inline_maths_immediately_after_a_hyphen(name: str) -> None:
    """``high-$\\ell$`` renders as literal source. Reword it."""
    text = (ROOT / name).read_text(encoding="utf-8")
    bad = []
    for m in re.finditer(r"[A-Za-z0-9]-(\$[^$\n]{1,60}\$)", text):
        bad.append((text[: m.start()].count("\n") + 1, m.group(0)))
    assert not bad, (
        f"{name}: inline $…$ directly after a hyphen does not render on "
        f"GitHub. Reword so the maths is not hyphen-adjacent. Found: {bad}")


@pytest.mark.parametrize("name", MARKDOWN)
def test_every_display_block_has_balanced_braces(name: str) -> None:
    """A brace that markdown ate is a block that renders as an error message."""
    text = (ROOT / name).read_text(encoding="utf-8")
    bad = []
    for line, block in _display_blocks(text):
        depth = 0
        for i, ch in enumerate(block):
            escaped = i > 0 and block[i - 1] == "\\"
            if ch == "{" and not escaped:
                depth += 1
            elif ch == "}" and not escaped:
                depth -= 1
                if depth < 0:
                    break
        if depth != 0:
            bad.append((line, depth, block.strip()[:70]))
    assert not bad, f"{name}: unbalanced braces in a display block: {bad}"


@pytest.mark.parametrize("name", MARKDOWN)
def test_display_blocks_are_delimited_on_their_own_lines(name: str) -> None:
    r"""GitHub needs ``$$`` to open and close a block cleanly.

    A ``$$`` that opens mid-sentence, or a block whose closing ``$$`` is
    followed by text on the same line, renders inconsistently between the
    repository page and the mobile view. The README's own grammar already puts
    displays on their own lines; this keeps it that way.
    """
    text = (ROOT / name).read_text(encoding="utf-8")
    bad = [i + 1 for i, ln in enumerate(text.splitlines())
           if ln.count("$$") == 1 and ln.strip() not in ("$$",)
           and not (ln.strip().startswith("$$") or ln.strip().endswith("$$"))]
    assert not bad, f"{name}: a $$ delimiter is buried mid-line at {bad}"
