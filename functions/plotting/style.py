"""House visual style for the bundle's figures.

Print artefacts: matplotlib to versioned PDF/PNG pairs. The web interaction layer
of the house data-visualisation standard is dropped; everything else applies.

The palette was re-validated against the house surfaces on 2026-10-05 rather than
inherited: worst adjacent CVD dE 9.1 light and 8.4 dark, worst adjacent
normal-vision dE 22.9 and 19.8, all above their gates.

**Slots 3 and 4 fall below 3:1 contrast on the light surface** (2.74 and 2.11).
The relief rule binds: they carry visible direct labels, never colour alone.

**Never more than three hues where all pairs must separate at once.** Yellow
against orange fails the all-pairs floors (normal-vision 13.7 light, CVD 4.8
dark). Slot 4 is the control slot and lives in diagnostics.

**A total is not a peer of its components**: parts take slots 1-3, the sum is
drawn in primary ink and heavier.

See captions/FIGURE-PLAN-v1.0.0.md for the binding rules.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

__all__ = ["SERIES", "INK", "use_house_style", "save_figure"]

ROOT = Path(__file__).resolve().parents[2]

#: Categorical slots, light surface. Assigned in fixed order, never cycled.
SERIES = {
    1: "#2a78d6",  # this reconstruction
    2: "#eb6834",  # the published or external result being matched
    3: "#1baf7a",  # a third series where one is needed
    4: "#eda100",  # the deliberately-wrong control — diagnostics only
}

SERIES_DARK = {1: "#3987e5", 2: "#d95926", 3: "#199e70", 4: "#c98500"}

INK = {
    "surface": "#fcfcfb",
    "primary": "#0b0b0b",
    "secondary": "#52514e",
    "muted": "#8a8880",
    "grid": "#e6e5e1",
}

#: Diverging pair, for a single signed series about zero.
DIVERGING = {"low": "#2a78d6", "high": "#e34948", "zero": "#f0efec"}


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
