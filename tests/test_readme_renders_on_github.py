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
