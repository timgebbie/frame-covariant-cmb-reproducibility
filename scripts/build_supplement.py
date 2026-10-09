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

PASSES = 2


def _overfulls(log: str) -> list[float]:
    return [float(x) for x in re.findall(r"Overfull \\hbox \(([0-9.]+)pt", log)]


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
            proc = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", SOURCE.name],
                cwd=build, capture_output=True, timeout=600,
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

        TARGET.parent.mkdir(exist_ok=True)
        shutil.copy2(produced, TARGET)

        print(f"built {TARGET.relative_to(ROOT)}"
              f"  —  {pages.group(1) if pages else '?'} pages, 0 errors")
        print(f"  overfull boxes: {len(over)}, worst {worst:.1f}pt "
              f"(threshold {MAX_OVERFULL_PT:.0f}pt)")
        if over[:3]:
            print("  worst three: " + ", ".join(f"{x:.1f}pt" for x in over[:3]))

        if worst > MAX_OVERFULL_PT:
            print()
            print(f"FAIL  {worst:.1f}pt of content runs past the margin.")
            print("      An `l` column cannot wrap, so one long cell sets the width")
            print("      of a whole table however narrow the others are — that was")
            print("      T-7. Bound the column, or make the content breakable.")
            return 1
        return 0


if __name__ == "__main__":
    sys.exit(main())
