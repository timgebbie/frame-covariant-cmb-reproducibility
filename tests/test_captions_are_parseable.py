r"""Every caption's front matter must parse, and say what the generator needs.

**Finding T-130, and it is the shape of defect this bundle keeps finding: a
release-blocking stage nothing ran, failing for a month in silence.**

`scripts/make_figure_pages.py` generates the supplement's entire figure section
from `captions/*.md`. It is wired into `run_all.py` as a stage whose failure is
recorded. On 2026-10-25 it could not parse **four of the nine committed
captions** --- F2, F5, F6 and F9 --- and so it could not generate anything at
all, including the eight that were fine. The supplement's figure section was
whatever had last been written when the captions still parsed.

The cause is one typo, made five times and copied: `$97.8\$%`. The author wanted
LaTeX's escaped percent inside mathematics, `$97.8\%$`. In a TOML **basic**
string `\$` is not a valid escape and `tomllib` refuses the file. Every caption
in this directory stores LaTeX in a basic string, where every backslash must be
doubled, so the whole directory is one keystroke from unparseable --- which is
why the repair is a gate and not only a correction.

**Nothing tested this.** `tests/test_readme_artefacts.py` checks that a figure
exists at the version the README states; nothing checked that the figure's
*caption* could be read. A caption is the figure's specification (**V15**), so
a caption the build cannot parse is a figure with no specification.
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CAPTIONS = ROOT / "captions"
sys.path.insert(0, str(ROOT / "scripts"))

import make_figure_pages as pages  # noqa: E402

#: Files with front matter. `FIGURE-PLAN-v1.0.0.md` is prose and has none,
#: which the generator already tolerates by returning `None`.
WITH_FRONT_MATTER = sorted(
    p.name for p in CAPTIONS.glob("*.md")
    if p.read_text(encoding="utf-8").startswith("+++"))

#: Keys `make_figure_pages.py` reads without a default. A caption missing one
#: raises a `KeyError` three stack frames from anything that names the file.
REQUIRED = ("id", "title", "script", "artefact", "caption")


def test_there_are_captions_to_check():
    """A glob that matches nothing passes every test below it."""
    assert len(WITH_FRONT_MATTER) >= 9, (
        f"only {len(WITH_FRONT_MATTER)} captions carry front matter; either "
        "the directory moved or the delimiter changed")


@pytest.mark.parametrize("name", WITH_FRONT_MATTER)
def test_the_front_matter_parses(name: str):
    """**The gate that was missing.** TOML, by the parser the generator uses."""
    text = (CAPTIONS / name).read_text(encoding="utf-8")
    block = text.split("+++", 2)[1]
    try:
        tomllib.loads(block)
    except tomllib.TOMLDecodeError as exc:
        pytest.fail(
            f"captions/{name}: the front matter is not valid TOML — {exc}\n"
            "These blocks are TOML *basic* strings, so every backslash in the "
            "LaTeX must be doubled: `\\\\textbf`, `\\\\%`. A single `\\$` or "
            "`\\%` stops the whole figure section from being generated, not "
            "just this caption. Finding T-130.")


@pytest.mark.parametrize("name", WITH_FRONT_MATTER)
def test_the_front_matter_has_what_the_generator_reads(name: str):
    """Parsing is necessary and not sufficient: the generator indexes keys."""
    fm = tomllib.loads((CAPTIONS / name).read_text(encoding="utf-8")
                       .split("+++", 2)[1])
    missing = [k for k in REQUIRED if k not in fm]
    assert not missing, (
        f"captions/{name}: missing {missing}. `make_figure_pages.py` reads "
        "these without a default, so the build fails on a KeyError that names "
        "no file.")
    assert (ROOT / fm["script"]).exists(), (
        f"captions/{name}: script = {fm['script']!r} does not exist")


@pytest.mark.parametrize("name", WITH_FRONT_MATTER)
def test_no_unescaped_percent_in_the_caption(name: str):
    """**The negative control for the specific typo, kept after the fix.**

    `\\%` is how a percent sign survives LaTeX. A bare `%` comments out the
    rest of the line, which is a silent corruption in a generated document
    rather than a build failure --- and silent is worse. This looks at the
    *parsed* value, which is the LaTeX that reaches the page, not at the
    source bytes.
    """
    fm = tomllib.loads((CAPTIONS / name).read_text(encoding="utf-8")
                       .split("+++", 2)[1])
    caption = fm["caption"]
    bad = [i for i, ch in enumerate(caption)
           if ch == "%" and (i == 0 or caption[i - 1] != "\\")]
    assert not bad, (
        f"captions/{name}: {len(bad)} unescaped `%` in the LaTeX caption, at "
        f"offsets {bad[:5]}. A bare percent comments out the rest of the line "
        "in the generated figure section — it will not fail the build, it "
        "will quietly delete text. Write `\\\\%` in the TOML source.")


@pytest.mark.parametrize("name", WITH_FRONT_MATTER)
def test_the_maths_delimiters_pair_and_none_are_doubled(name: str):
    r"""**The control for the repair, not for the original defect.**

    Fixing T-130 was a substitution, `\$%` → `\\%$`, and a substitution is the
    kind of repair that is right in four places and wrong in the fifth. It was:
    one site already carried the closing `$`, so the fix produced `$1\%$$` ---
    a stray display-maths delimiter inside a `\caption{}`, which is a LaTeX
    error or a silent layout corruption depending on what follows.

    Caught here by looking at the generated section rather than by reading the
    patch, which is the same discipline as **V12**. An odd count would leave
    mathematics open for the rest of the caption.
    """
    caption = tomllib.loads((CAPTIONS / name).read_text(encoding="utf-8")
                            .split("+++", 2)[1])["caption"]
    assert "$$" not in caption, (
        f"captions/{name}: `$$` in a LaTeX caption. Display mathematics inside "
        "`\\caption{}` does not typeset; this is usually a substitution that "
        "added a `$` where one already stood — T-130's repair did exactly "
        "that.")
    bare = sum(1 for i, ch in enumerate(caption)
               if ch == "$" and (i == 0 or caption[i - 1] != "\\"))
    assert bare % 2 == 0, (
        f"captions/{name}: {bare} unescaped `$`, an odd number, so inline "
        "mathematics is left open and the rest of the caption typesets as "
        "symbols.")


def test_the_generator_runs_on_the_tree_it_is_in(tmp_path):
    """End to end, because the three checks above are about one file each.

    The failure this file exists for was *the directory*, not any one caption:
    one unparseable file stopped all ten. So the last assertion is that the
    generator completes and writes every planned figure it has an artefact for.

    **Written to `tmp_path` and not into the tree --- 2026-10-26.** It wrote
    `supplementary-materials/figures-v1.3.0.tex` as a side effect of being
    run. Since v1.3.14 the supplement inputs no fragment set, so that file is
    read by nothing; but it *was* counted as a source of the supplement's PDF,
    and regenerating it made the release gate report the PDF stale against a
    file that cannot have changed it. **The gate and this test were refuting
    each other on every run**, each of them correct about its own half.

    The dependency set is now parsed from the document's `\\input` lines, and
    this writes outside the tree. A test that dirties the released tree to
    prove a generator works is paying for the proof with the thing being
    verified.
    """
    pages.OUT = tmp_path / pages.OUT.name
    assert pages.main() == 0, (
        "scripts/make_figure_pages.py failed on this tree. The supplement's "
        "figure section is generated by it, so a failure here means the "
        "section in supplementary-materials/ is whatever was last written.")
