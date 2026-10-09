#!/usr/bin/env python3
r"""Build the computational supplement, and gate it — R3.

    python scripts/build_supplement.py

**The supplement was the one released artefact `run_all.py` did not generate.**
It was built by hand, moved by hand, and renamed by hand on the way, which is
how finding **T-7** reached print: 155.9pt and 81.4pt of text running past the
right margin of a document that ships. Every manual step in this project has
eventually drifted, and this one drifted into a PDF.

Three things, in order:

1. **Compile twice**, because `longtable` and `\ref` need the second pass to
   settle. A single pass leaves `??` in cross-references and the wrong column
   widths, and both look like content rather than like a build problem.
2. **Fail on any LaTeX error.** Not a warning, an error: `pdflatex` exits
   zero in `nonstopmode` whatever happens, so the log is read rather than the
   return code.
3. **Report every overfull box and fail above the threshold.** T-7's 55mm of
   overhang was invisible to every gate the bundle had, because none of them
   compiled anything.

**Why the source sits at the repository root while the output does not.** The
supplement `\input`s `tables/…` and `\includegraphics`es `figures/…`, both
relative to the build directory, so it must compile from the root. The released
PDF belongs beside the other supplementary material. The asymmetry of names is
therefore deliberate and is handled **here**, once, instead of in a `Move-Item`
retyped into every commit sequence.

Skips with exit 0 and a stated reason where `pdflatex` is absent. A gate that
fails on a missing toolchain repeats finding T-4.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "SUPPLEMENTARY-MATERIAL-v1.0.0.tex"
TARGET = ROOT / "supplementary-materials" / "supplement-v1.0.0.pdf"

#: Worst overfull box tolerated, in points. Proposed by P1-B and accepted by
#: the PI on 2026-10-09. Not a standard: a threshold nobody chose is a
#: threshold nobody owns. 35pt is about 12mm, which is visible but inside the
#: margin on this geometry.
MAX_OVERFULL_PT = 35.0

#: Worst overfull **vbox** tolerated, in points: none. Content running past the
#: bottom margin is not the same defect as content running into a generous side
#: margin --- it collides with the footer or leaves the page --- and the
#: supplement measures **zero** of them across 20 pages, so this is a statement
#: that the document has none rather than a judgement about how much would be
#: acceptable. The first one is a regression and should stop the build.
MAX_VBOX_OVERFULL_PT = 0.0

PASSES = 2

#: Fixed build clock, so the PDF is byte-reproducible --- finding **T-11**.
#: `pdflatex` stamps `/CreationDate`, `/ModDate` and a random `/ID` into every
#: file it writes, so each rebuild produced different bytes and `--strict`
#: could never pass once the harness started building this. That is **T-2 in a
#: new generator**: matplotlib was fixed and the lesson was not generalised, so
#: adding a generator reintroduced the defect.
#:
#: `SOURCE_DATE_EPOCH` is the reproducible-builds convention and TeX Live
#: honours it for all three fields; `FORCE_SOURCE_DATE` makes `\today`
#: deterministic too. The value is a constant rather than the wall clock,
#: because a build clock that moves is the whole problem.
SOURCE_DATE_EPOCH = "1791504000"  # 2026-10-09T00:00:00Z


def _overfulls(log: str) -> list[float]:
    """Overfull `\\hbox` — content past the **right** margin, in points."""
    return [float(x) for x in re.findall(r"Overfull \\hbox \(([0-9.]+)pt too wide", log)]


def _vbox_overfulls(log: str) -> list[float]:
    r"""Overfull `\vbox` — content past the **bottom** margin, in points.

    **Finding T-12, raised by Coordination 2026-10-09.** This function did not
    exist, and `_overfulls` matched `\hbox` only. The gate was therefore blind
    to vertical overflow for its whole life: a table or figure running off the
    bottom of a page would have produced a clean build and a released PDF, which
    is precisely what happened in the *paper's* gate, where Eq. (30) printed off
    the bottom of page 7 through every passing build until the PI saw it by eye.

    It is **T-3 and T-6's shape a third time** — a check that passes because it
    is looking at the wrong object. T-3's grid measured the wrong thing, T-6's
    comparison counted instead of comparing, and this one measured one of the
    two directions a box can overflow. The pattern is worth naming: each was a
    gate that reported PASS while the defect it existed to catch sat in front
    of it.

    Measured over the 20-page supplement at the time of the fix: **none.** The
    threshold below is therefore not a tolerance anybody guessed at --- the
    document has zero, so any occurrence is a regression and fails.
    """
    return [float(x) for x in re.findall(r"Overfull \\vbox \(([0-9.]+)pt too high", log)]


def _errors(log: str) -> list[str]:
    return [l for l in log.splitlines() if l.startswith("!")]


def main() -> int:
    if shutil.which("pdflatex") is None:
        print("SKIP  supplement build: pdflatex is not on PATH")
        print("      Not a failure. The supplement is built where LaTeX is,")
        print("      and the release gate is run there.")
        return 0
    if not SOURCE.exists():
        print(f"FAIL  {SOURCE.name} is missing")
        return 1

    # Build in a scratch directory so that .aux/.log/.out never land beside the
    # source. They are gitignored, but finding T-1 is that the fingerprint
    # should not depend on what a build happened to leave behind.
    with tempfile.TemporaryDirectory(prefix="supplement-") as tmp:
        build = Path(tmp)
        shutil.copy2(SOURCE, build / SOURCE.name)
        for d in ("tables", "figures", "supplementary-materials"):
            if (ROOT / d).is_dir():
                shutil.copytree(ROOT / d, build / d, dirs_exist_ok=True)

        log = ""
        for i in range(PASSES):
            import os

            env = dict(os.environ,
                       SOURCE_DATE_EPOCH=SOURCE_DATE_EPOCH,
                       FORCE_SOURCE_DATE="1")
            proc = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", SOURCE.name],
                cwd=build, capture_output=True, timeout=600, env=env,
            )
            log = (build / f"{SOURCE.stem}.log").read_text(
                encoding="utf-8", errors="replace"
            ) if (build / f"{SOURCE.stem}.log").exists() else proc.stdout.decode(
                "utf-8", "replace"
            )
            errs = _errors(log)
            if errs:
                print(f"FAIL  LaTeX reported {len(errs)} error(s) on pass {i + 1}:")
                for e in errs[:10]:
                    print("      " + e)
                return 1

        produced = build / f"{SOURCE.stem}.pdf"
        if not produced.exists():
            print("FAIL  pdflatex reported no errors but produced no PDF")
            return 1

        pages = re.search(r"Output written on .*?\((\d+) pages", log)
        over = sorted(_overfulls(log), reverse=True)
        worst = over[0] if over else 0.0
        vover = sorted(_vbox_overfulls(log), reverse=True)
        vworst = vover[0] if vover else 0.0

        TARGET.parent.mkdir(exist_ok=True)
        shutil.copy2(produced, TARGET)

        print(f"built {TARGET.relative_to(ROOT)}"
              f"  —  {pages.group(1) if pages else '?'} pages, 0 errors")
        print(f"  overfull hbox (right margin): {len(over)}, worst {worst:.1f}pt "
              f"(threshold {MAX_OVERFULL_PT:.0f}pt)")
        if over[:3]:
            print("  worst three: " + ", ".join(f"{x:.1f}pt" for x in over[:3]))
        print(f"  overfull vbox (bottom margin): {len(vover)}, worst {vworst:.1f}pt "
              f"(threshold {MAX_VBOX_OVERFULL_PT:.0f}pt — T-12)")

        failed = False
        if worst > MAX_OVERFULL_PT:
            print()
            print(f"FAIL  {worst:.1f}pt of content runs past the RIGHT margin.")
            print("      An `l` column cannot wrap, so one long cell sets the width")
            print("      of a whole table however narrow the others are — that was")
            print("      T-7. Bound the column, or make the content breakable.")
            failed = True
        if vworst > MAX_VBOX_OVERFULL_PT:
            print()
            print(f"FAIL  {vworst:.1f}pt of content runs past the BOTTOM margin,")
            print(f"      on {len(vover)} page(s). This is finding T-12: the gate")
            print("      used to match `\\hbox` only and could not see this at all.")
            print("      A float or table is too tall for the text block — give it")
            print("      its own page, shorten it, or let it break across pages.")
            failed = True
        return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
