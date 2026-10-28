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
def _rendered_markdown() -> list[str]:
    r"""Every ``.md`` in the tree that github.com will render.

    **Widened 2026-10-24, finding F4/T-123.** This was ``["README.md"]`` while
    the comment above it already said *"and anything else markdown-rendered"*,
    and the gap between the two is where a stray ``$$`` lived for a day — in
    `BUNDLE-DEFECTS-v1.md`, inverting 112 lines that the README points a reader
    at from four places. A list that names one file is not a policy; this
    discovers them, so a new document is covered the day it lands.

    `.tex` is excluded on purpose and not by omission: LaTeX has no emphasis
    parser, ``\eta_*`` is correct there, and enforcing these rules on the
    supplement would be the mirror-image mistake.
    """
    skip = {".git", "__pycache__", "node_modules", "sources", "correction"}
    out = []
    for p_ in sorted(ROOT.rglob("*.md")):
        if skip & set(p_.parts):
            continue
        out.append(p_.relative_to(ROOT).as_posix())
    return out


MARKDOWN = _rendered_markdown()

#: **The two severities, and why they are not enforced the same way.**
#:
#: Widening the file set on 2026-10-24 produced **48 failures across 41 files**,
#: which the audit predicted and called the point of running it. Fixing all of
#: them before any of the guard lands would mean the guard does not land today,
#: and the defect it exists to stop is a *daily* one. So the rules are split by
#: what they cost a reader:
#:
#:   **FATAL** --- the page breaks. An odd ``$$`` count inverts every display
#:   and every paragraph after it (T-120b, T-123); ``\tag{`` stacks an equation
#:   atom by atom (T-120c); ``\big``/``\Big`` throw a red error box; a newline
#:   inside a display becomes a layout break (T-120d); a bare ``*`` in a display
#:   eats the subscripts (T-120). Each destroys content a reader cannot
#:   reconstruct. **Zero tolerance, every file, no allowance.**
#:
#:   **COSMETIC** --- one expression renders as its own source. ``high-$\ell$``
#:   shows as ``high-$\ell$``; a bare ``*`` inline loses a subscript. The reader
#:   sees something ugly and still correct, and can read past it.
#:
#: Cosmetic rules are enforced as a **ratchet**: today's count is frozen below
#: and may only fall. A new document cannot add one, the backlog cannot grow,
#: and the number in this file is the work remaining. **A ratchet is a worse
#: gate than zero and a far better one than an unenforced comment**, which is
#: what this file had until today.
#:
#: Lower these as files are cleaned. Raising one requires saying why in the
#: commit, which is the whole mechanism.
COSMETIC_BASELINE = {
    "test_no_bare_asterisk_in_inline_maths": 18,
    "test_no_inline_maths_immediately_after_a_hyphen": 12,
    #: **P1-T's #9, 2026-10-27.** Frozen at 11 files rather than enforced at
    #: zero, and the reason is not timidity: **163 of the 218 instances are in
    #: `provenance/BUNDLE-DEFECTS-v1.md`, which is append-only and cannot be
    #: rewritten.** The guard that makes the register trustworthy is the same
    #: guard that makes this class permanent in it. The root `README.md` and
    #: `handoff/P1B-to-P1T.md` were cleared in the landing that added this, so
    #: the public face carries none.
    "test_no_maths_span_butted_against_a_word_or_dash": 11,
#: **Both lowered by one on 2026-10-25**, and not by a cleanup: `_prose`
#: stopped judging `captions/*.md` front matter --- which is LaTeX stored
#: for the build and was never going to render as prose --- by markdown
#: rules. The ratchet caught the fall itself and refused to pass until the
#: gain was recorded, which is the behaviour it exists for.
}


def _count_failures(rule) -> tuple[int, list[str]]:
    """How many files break `rule`, and which — for the ratchet."""
    bad = []
    for name in MARKDOWN:
        try:
            rule(name)
        except AssertionError:
            bad.append(name)
    return len(bad), bad


def _without_code(text: str) -> str:
    r"""Fenced blocks and inline code blanked, with the line numbering kept.

    A code span renders **literally**. Whatever delimiters it contains are not
    delimiters, so no rendering hazard in this file applies inside one, and a
    gate that reads code spans cannot be documented in the repository it
    guards --- **T-165**. Each run is replaced by spaces rather than removed
    so the line numbers in a failure message still point at the file.
    """
    def blank(match: re.Match) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = re.sub(r"```.*?```", blank, text, flags=re.S)
    return re.sub(r"(`+)[^\n]*?\1", blank, text)


def _prose(name: str) -> str:
    r"""The part of a ``.md`` file that is **prose**, with TOML front matter cut.

    **Scoped 2026-10-25, with T-130.** `captions/*.md` open with a ``+++``
    block that is not markdown: it is the LaTeX caption, stored for
    `scripts/make_figure_pages.py`, where ``\%`` is *required* and every
    backslash is doubled for TOML. Judging that block by GitHub's markdown
    rules asks two incompatible things of the same bytes — valid LaTeX needs
    ``$97.8\%$``, and GitHub's parser eats ``\%`` inside ``$…$`` before
    KaTeX sees it.

    The resolution is **scope, not exemption**. The rules below are about what
    a reader sees as prose; the front matter has never rendered as prose
    (``\\textbf{…}`` throughout) and no rule here could make it. The markdown
    body underneath — the standalone long-form caption, which *is* read on
    github.com — is checked in full, as is every other file, because nothing
    else in the tree carries front matter.

    The delimiter must be a ``+++`` line of its own at the very start, so a
    ``+++`` appearing mid-document cuts nothing.
    """
    text = (ROOT / name).read_text(encoding="utf-8")
    if not text.startswith("+++"):
        return text
    end = text.find("\n+++", 3)
    if end < 0:
        return text
    # Blank the block rather than deleting it, so every line number this file
    # reports still matches the file on disk. A rule that points at line 32 of
    # a file whose line 32 is elsewhere is worse than no rule.
    head = text[: end + 5]
    return "\n" * head.count("\n") + text[end + 5:]


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
    text = _prose(name)
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
    text = _prose(name)
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
    text = _prose(name)
    # **Scoped to maths, 2026-10-24.** These three are hazards only where the
    # maths renderer sees them; in prose, ``\tag`` and ``\big`` are just words,
    # and a register that records a banned command has to be able to name it.
    # **``$$`` parity is deliberately NOT scoped this way** — T-120b and T-123
    # are both a backticked ``$$`` in prose, because the renderer counts
    # delimiters before anything else and backticks do not hide them. The two
    # rules differ because the failures differ, and that asymmetry is the
    # finding rather than an inconsistency.
    maths = "".join(m.group(0) for m in re.finditer(r"\$\$.*?\$\$", text, re.S))
    body = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
    maths += "".join(m.group(0) for m in re.finditer(
        r"(?<!\$)\$(?!\s)[^$\n]{1,200}?(?<!\s)\$(?!\$)", body))
    found = {cmd: maths.count(cmd) for cmd in BANNED if cmd in maths}
    assert not found, "\n".join(
        f"{name}: {n}x '{cmd}' inside maths — {BANNED[cmd]}"
        for cmd, n in found.items())


@pytest.mark.parametrize("name", MARKDOWN)
def test_no_bare_asterisk_in_a_display_block(name: str) -> None:
    """``\\eta_*`` in a ``$$`` block is eaten by markdown. Use ``\\eta_\\ast``."""
    text = _prose(name)
    offenders = [(line, block.strip()[:70])
                 for line, block in _display_blocks(text) if "*" in block]
    assert not offenders, (
        f"{name}: a bare '*' inside $$…$$ is parsed as markdown emphasis "
        f"before the maths renderer sees it, and the subscript is destroyed. "
        f"Write \\ast. Offending blocks: {offenders}")


def _bare_asterisk_in_inline_maths(name: str) -> None:
    r"""``$z_*=1114.5$`` is the same defect one dollar sign smaller.

    CommonMark's asymmetry is the whole of it: ``*`` opens emphasis
    **intraword** and ``_`` does not, so ``a_b_c`` is safe and ``a*b*c`` is
    not. That is why ``\tau_{A_\ell}`` has always rendered and ``\eta_*``
    never did. One bare ``*`` is enough, because the ``**bold**`` markers
    elsewhere in the same paragraph supply its partner.
    """
    text = _prose(name)
    body = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)   # displays covered above
    hits = [(body[: m.start()].count("\n") + 1, m.group(0))
            for m in re.finditer(r"(?<!\$)\$(?!\s)([^$\n]{1,80}?)(?<!\s)\$(?!\$)",
                                 body)
            if "*" in m.group(1)]
    assert not hits, (
        f"{name}: a bare '*' inside inline $…$ pairs with the paragraph's "
        f"emphasis markers. Write \\ast. Found: {hits}")


def _inline_maths_immediately_after_a_hyphen(name: str) -> None:
    """``high-$\\ell$`` renders as literal source. Reword it."""
    text = _prose(name)
    bad = []
    for m in re.finditer(r"[A-Za-z0-9]-(\$[^$\n]{1,60}\$)", text):
        bad.append((text[: m.start()].count("\n") + 1, m.group(0)))
    assert not bad, (
        f"{name}: inline $…$ directly after a hyphen does not render on "
        f"GitHub. Reword so the maths is not hyphen-adjacent. Found: {bad}")


def _maths_span_butted_against_a_word_or_dash(name: str) -> None:
    r"""``$\Lambda$CDM`` renders as literal source. **P1-T, 2026-10-27, #9.**

    **Code spans are blanked first --- finding T-165, 2026-10-28.** Without
    that, this gate fired twice on `handoff/P1T-to-P1B.md`: at the exact two
    places where P1-T *names the defect*, inside backticks, in the very item
    that asked for this rule. A code span renders literally by definition, so
    ``` `$\Lambda$CDM` ``` is not a maths span and cannot mis-render --- the
    hit was a false positive of the gate rather than a hazard in the file, and
    the only ways to satisfy it were to delete the documentation or to exempt
    the file. **A rule that cannot be written about is a rule nobody can
    document**, and this one was authored a day earlier by P1-B.

    GitHub's parser wants the delimiters free. A span immediately followed by
    a **letter or digit**, or touching an **en/em dash**, is not recognised as
    maths and prints as `$\Lambda$CDM`.

    **The rule is narrower than "any adjacency", deliberately.** P1-T named
    three sites: `$\Lambda$CDM`, an en-dash against `$10^{-14}$`, and `$1+3$`
    inside a quoted title. They did **not** name `$\ell$-dependent`, which
    this bundle's prose uses everywhere and which renders. Widening the rule to
    every adjacent character would have condemned 448 sites on the strength of
    evidence for 218, and most of the extra would have been a construction
    nobody has seen fail. That is the §3c failure in the direction nobody
    checks: generalising a confirmed observation past what was observed.

    **P1-B has not reproduced this.** `WebFetch` requires the URL in the
    conversation's provenance set and web search is disabled for the
    organisation, so the rendered page could not be loaded from here. The
    class is acted on because P1-T confirmed it on the page and because the
    repair is safe either way --- `$\Lambda\mathrm{CDM}$` renders correctly
    whether or not the original did.
    """
    text = re.sub(r"\$\$.*?\$\$", "", _without_code(_prose(name)), flags=re.S)
    bad = []
    for s in re.finditer(r"(?<!\$)\$(?!\s)[^$\n]{1,200}?(?<!\s)\$(?!\$)", text):
        before = text[s.start() - 1] if s.start() > 0 else "\n"
        after = text[s.end()] if s.end() < len(text) else "\n"
        if (re.match(r"[A-Za-z0-9]", after)
                or re.match(r"[\u2010-\u2015]", before)
                or re.match(r"[\u2010-\u2015]", after)):
            bad.append((text[: s.start()].count("\n") + 1,
                        f"{before}{s.group(0)}{after}"))
    assert not bad, (
        f"{name}: a maths span butted against a word character or an en-dash "
        f"does not render on GitHub. Put the whole token in one span "
        f"(`$\\Lambda\\mathrm{{CDM}}$`) or separate it with a word. "
        f"Found: {bad[:6]}")


@pytest.mark.parametrize("name", MARKDOWN)
def test_every_display_block_has_balanced_braces(name: str) -> None:
    """A brace that markdown ate is a block that renders as an error message."""
    text = _prose(name)
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
    text = _prose(name)
    bad = [i + 1 for i, ln in enumerate(text.splitlines())
           if ln.count("$$") == 1 and ln.strip() not in ("$$",)
           and not (ln.strip().startswith("$$") or ln.strip().endswith("$$"))]
    assert not bad, f"{name}: a $$ delimiter is buried mid-line at {bad}"


# ---------------------------------------------------------------------------
# the cosmetic ratchet
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("rule_name,rule", [
    ("test_no_bare_asterisk_in_inline_maths", _bare_asterisk_in_inline_maths),
    ("test_no_inline_maths_immediately_after_a_hyphen",
     _inline_maths_immediately_after_a_hyphen),
    ("test_no_maths_span_butted_against_a_word_or_dash",
     _maths_span_butted_against_a_word_or_dash),
])
def test_cosmetic_backlog_does_not_grow(rule_name, rule) -> None:
    """A cosmetic hazard may be removed from the tree and never added to it.

    These two do not break a page; they render one expression as its own
    source. Enforcing them at zero today would block the FATAL guards from
    landing, and the fatal class is the one that cost three days this week.
    So they are frozen at today's count and ratcheted down.

    **If this fails because the count ROSE**, a new document added a hazard and
    the fix is in that document. **If it fails because the count FELL**, lower
    `COSMETIC_BASELINE` in this file — that is a cleanup landing, and recording
    it is how the backlog stays visible instead of becoming permanent.
    """
    n, bad = _count_failures(rule)
    allowed = COSMETIC_BASELINE[rule_name]
    assert n <= allowed, (
        f"{rule_name}: {n} files now carry this hazard, baseline {allowed}. "
        f"New or worsened: {sorted(bad)}")
    assert n == allowed, (
        f"{rule_name}: down to {n} from a baseline of {allowed} — good. "
        f"Lower COSMETIC_BASELINE['{rule_name}'] to {n} so the ratchet holds "
        f"the gain. Remaining: {sorted(bad)}")


#: **Backslash + ASCII punctuation, finding T-126 / P1-T 2026-10-24.**
#: CommonMark treats a backslash before ASCII punctuation as an escape and
#: consumes it **before** the maths renderer runs. So `\,` reaches KaTeX as a
#: bare comma, `\{` as a grouping brace rather than a delimiter, and `\%` as
#: a **comment** — which discards the rest of that span. The README carried 26
#: of these across twelve lines and the PI saw the commas on the page.
#: Alphabetic control words survive, which is why the repairs are
#: `\thinspace`, `\negthinspace`, `\lbrace`/`\rbrace`, and for the percent
#: sign, moving it outside the maths entirely.
MARKDOWN_EATEN = {
    ",": r"\thinspace",
    "!": r"\negthinspace",
    "{": r"\lbrace",
    "}": r"\rbrace",
    "%": "move the percent sign OUTSIDE the maths span",
    "#": "avoid, or use \\mathrm",
    "&": "avoid in a GitHub maths span",
    "_": "only outside a subscript; a literal underscore needs \\textunderscore",
}


def _maths_spans(text: str) -> list[str]:
    out = [m.group(1) for m in re.finditer(r"\$\$(.*?)\$\$", text, re.S)]
    body = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
    out += [m.group(1) for m in re.finditer(
        r"(?<!\$)\$(?!\s)([^$\n]{1,300}?)(?<!\s)\$(?!\$)", body)]
    return out


@pytest.mark.parametrize("name", MARKDOWN)
def test_no_markdown_eaten_escape_inside_maths(name: str) -> None:
    r"""The general form of the comma defect, not the twenty-six instances.

    **This is the test the previous three render findings should have been.**
    T-120, T-120b, T-120c and T-120d each banned a specific token after it had
    already reached the published page. This one bans the *class*: any
    backslash followed by ASCII punctuation inside a maths span, because
    markdown will eat the backslash and leave the punctuation to mean
    something else to KaTeX.

    ``\%`` is the dangerous member and the reason the class matters more than
    the list: stripped to a bare ``%`` it is a **comment**, so everything after
    it in that span silently disappears. A reader sees a truncated equation
    with no error.
    """
    bad = []
    for span in _maths_spans(_prose(name)):
        for ch, fix in MARKDOWN_EATEN.items():
            tok = "\\" + ch
            if tok in span:
                bad.append((tok, fix, span.strip()[:60]))
    assert not bad, (
        f"{name}: markdown eats the backslash before ASCII punctuation inside "
        f"maths, leaving the character to mean something else to KaTeX. "
        + "; ".join(f"'{t}' -> {f}  in: {s}" for t, f, s in bad[:6]))
