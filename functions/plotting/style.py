"""House visual style for the bundle's figures.

Print artefacts: matplotlib to versioned PDF/PNG pairs. The web interaction layer
of the house data-visualisation standard is dropped; everything else applies.

**The series are achromatic**, accepted by the PI on 2026-10-08. Hue is gone, so
it can no longer carry meaning, and that forces the rule the coloured palette
only applied to its weak slots: **every series carries a direct label or a
distinct dash, never its grey alone.** Removing hue costs one channel and buys
three things --- the figures survive greyscale printing unchanged, colour-vision
deficiency stops being a separate validation, and a reader cannot be led by a
colour that was chosen rather than measured.

Separation is by **lightness and dash together**, and both are needed: lightness
alone fails on a bad printer or a projector, dash alone fails where lines are
short or steep. Measured, not asserted --- against the light surface the slots
sit at 18.3, 8.0, 3.9 and 2.3, and **slot against adjacent slot** at 2.29, 2.07
and 1.66. Those second numbers are the honest measure of separability and they
are low: 1.66 between the third and fourth slots is not a difference a reader
should be asked to resolve. That is why `SERIES_DASH` is mandatory rather than
decorative.

**Slot 4 is the deliberately-wrong control and is the faintest on purpose.** It
lives in `diagnostics/` and must never read as a peer of the result it is
contradicting. Its 2.3:1 is below the 3:1 floor, which is why the direct-label
rule is absolute rather than advisory.

**A total is not a peer of its components**: parts take slots 1-3, the sum is
drawn in primary ink and heavier.

The coloured palette is kept below as `SERIES_CHROMATIC`, unused, so that the
change is a visible decision in the source rather than a deletion.

See captions/FIGURE-PLAN-v1.0.0.md for the binding rules.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

__all__ = ["SERIES", "SERIES_DASH", "SERIES_DARK", "INK", "use_house_style", "save_figure"]

ROOT = Path(__file__).resolve().parents[2]

#: Categorical slots, light surface. Assigned in fixed order, never cycled.
#: Achromatic: separation is by lightness, paired with SERIES_DASH.
SERIES = {
    1: "#121212",  # this reconstruction          18.4:1
    2: "#4f4f4f",  # the external result matched    8.3:1
    3: "#808080",  # a third series where needed    3.9:1
    4: "#a8a8a8",  # the deliberately-wrong control 2.5:1 — diagnostics only
}

#: Dark surface: the ramp inverts, it does not merely lighten.
SERIES_DARK = {1: "#f2f2f2", 2: "#bdbdbd", 3: "#8f8f8f", 4: "#6e6e6e"}

#: The second channel, and it is not optional. A grey ramp alone collapses on a
#: bad printer; these keep the slots apart when the lightness does not.
SERIES_DASH = {
    1: (0, ()),                 # solid: the reconstruction, always
    2: (0, (2.4, 2.4)),         # dashed: the external result
    3: (0, (5.5, 2.0)),         # long dash
    4: (0, (1.0, 1.8)),         # dotted: the control, visually subordinate
}

#: The palette this replaced, kept so the change is legible in the source.
#: **Unused.** Do not reintroduce it one call site at a time.
SERIES_CHROMATIC = {1: "#2a78d6", 2: "#eb6834", 3: "#1baf7a", 4: "#eda100"}

INK = {
    "surface": "#fcfcfb",
    "primary": "#0b0b0b",
    "secondary": "#52514e",
    "muted": "#8a8880",
    "grid": "#e6e5e1",
}

#: Diverging pair, for a single signed series about zero.
#:
#: **Achromatic diverging is genuinely weaker than chromatic, and this says so
#: rather than pretending otherwise.** Lightness is one-dimensional, so a reader
#: cannot tell "far below zero" from "far above" by value alone --- both ends
#: are simply dark. Where sign must be read off the mark itself, encode it with
#: hatching or an explicit sign annotation, not with this scale. Used for
#: magnitude about a known-signed baseline, nothing more.
DIVERGING = {"low": "#2b2b2b", "high": "#9a9a9a", "zero": "#efeeeb"}


def use_house_style() -> None:
    """Apply the house rcParams. Idempotent."""
    mpl.rcParams.update(
        {
            "figure.facecolor": INK["surface"],
            "axes.facecolor": INK["surface"],
            "savefig.facecolor": INK["surface"],
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "axes.titlesize": 9.0,
            "axes.titleweight": "regular",
            "axes.titlelocation": "left",
            "axes.labelcolor": INK["secondary"],
            "axes.edgecolor": INK["grid"],
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": INK["grid"],
            "grid.linewidth": 0.6,
            "grid.alpha": 1.0,
            "xtick.color": INK["secondary"],
            "ytick.color": INK["secondary"],
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "lines.linewidth": 1.6,
            "lines.markersize": 3.2,
            "legend.frameon": False,
            "legend.fontsize": 7.5,
            "text.color": INK["primary"],
            "figure.dpi": 150,
            "savefig.dpi": 300,
            
            "pdf.fonttype": 42,
        }
    )


#: Metadata written into every released figure, per format.
#:
#: **`CreationDate: None` is the whole point** (finding T-2). Matplotlib stamps
#: the wall clock into every PDF it writes, so two runs of the same script on
#: the same machine produced different bytes, every PDF hash moved on every run,
#: and `make_manifests.py --check` could never pass after a re-run --- which is
#: exactly what a reader re-running the pipeline wants it for. A fingerprint
#: that cannot survive regenerating what it fingerprints is not a fingerprint.
#:
#: `Creator` is pinned for the same reason, one variable fewer. What is **not**
#: claimed is byte-identity across matplotlib versions: a different renderer
#: genuinely lays the page out differently, and pretending otherwise by
#: stripping the version would hide a real difference instead of removing a
#: spurious one.
DETERMINISTIC_METADATA = {
    "pdf": {"CreationDate": None, "Creator": "frame-covariant-cmb-reproducibility"},
    "png": {"Software": "frame-covariant-cmb-reproducibility"},
}


def save_figure(fig, stem: str, version: str = "v1.0.0") -> list[Path]:
    """Write the versioned PDF/PNG pair into figures/ and return the paths.

    Figures are versioned in the filename, per the house layout, and written
    with deterministic metadata so that regenerating a figure that has not
    changed leaves its hash alone. See `DETERMINISTIC_METADATA`.
    """
    out = ROOT / "figures"
    out.mkdir(exist_ok=True)
    paths = []
    for ext in ("pdf", "png"):
        p = out / f"{stem}-{version}.{ext}"
        fig.savefig(p, metadata=DETERMINISTIC_METADATA[ext])
        paths.append(p)
    plt.close(fig)
    return paths
