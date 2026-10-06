"""The Friedmann-Lemaitre background, derived rather than imported.

`CDM_MODEL` and `LCDM_MODEL` are *models*, not frames. The CDM **frame** is
the total-energy frame q_a = 0 and lives in `functions.spectra.sources.Frame`.
"""

from functions.background.flrw import (
    CDM_MODEL,
    LCDM_MODEL,
    Background,
    eds_scale_factor,
)

__all__ = ["Background", "eds_scale_factor", "CDM_MODEL", "LCDM_MODEL"]
