"""Tabulated spherical Bessel functions for the line-of-sight integrals.

**The tabulated half of route 3.** The integrated sources of Annals II (176) are
evaluated along the line of sight, so their k-integral carries
$j_\\ell(k\\Delta\\eta)j_\\ell(k\\Delta\\eta')$ with **two different arguments**. The
closed form of `kernels.py` applies only where the arguments coincide, which is
the primary term. Here the integral is done numerically, and the saving is that
$j_\\ell$ depends only on the product $k\\Delta\\eta$: one table in $x=k\\Delta\\eta$
serves every $(k,\\eta)$ pair.

That is the standard construction and it is what CMBFAST does; it is chosen here
because it is the dull, certain option where the elegant one does not apply.

**Grid.** $j_\\ell(x)$ oscillates with period $\\simeq\\pi$ once $x$ exceeds $\\ell$,
and is exponentially small below. The table therefore starts a little below
$\\ell$ and is sampled at a fixed number of points per period; `points_per_period`
is the single accuracy knob and its effect is measured in the tests rather than
assumed.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.special import spherical_jn

__all__ = ["BesselTable"]


@dataclass(frozen=True)
class BesselTable:
    """j_l(x) for a range of l, tabulated in x and interpolated by cubic spline."""

    ell: np.ndarray
    x: np.ndarray
    values: np.ndarray  # (n_ell, n_x)
    _splines: tuple

    @classmethod
    def build(
        cls,
        ell_max: int,
        x_max: float,
        *,
        ell_min: int = 0,
        points_per_period: int = 12,
    ) -> "BesselTable":
        """Tabulate j_l(x) for l in [ell_min, ell_max] on [0, x_max]."""
        if x_max <= 0:
            raise ValueError("x_max must be positive")
        n = max(int(points_per_period * x_max / pi), 64)
        x = np.linspace(0.0, x_max, n)
        ell = np.arange(ell_min, ell_max + 1)
        values = np.empty((ell.size, x.size))
        for i, l in enumerate(ell):
            values[i] = spherical_jn(int(l), x)
        splines = tuple(CubicSpline(x, values[i], extrapolate=False) for i in range(ell.size))
        return cls(ell=ell, x=x, values=values, _splines=splines)

    def __call__(self, ell: int, x: np.ndarray | float) -> np.ndarray:
        """j_l at arbitrary x, by interpolation. Zero outside the tabulated range."""
        idx = int(ell) - int(self.ell[0])
        if not 0 <= idx < self.ell.size:
            raise ValueError(f"ell={ell} outside the tabulated range {self.ell[0]}..{self.ell[-1]}")
        out = self._splines[idx](np.asarray(x, dtype=float))
        return np.nan_to_num(out, nan=0.0)

    @property
    def nbytes(self) -> int:
        return int(self.values.nbytes)


def line_of_sight(
    ell: int,
    k: float,
    eta: np.ndarray,
    source: np.ndarray,
    eta_0: float,
    table: BesselTable,
) -> float:
    """Int d(eta) S(k, eta) j_l(k (eta_0 - eta)), by trapezoid against the table.

    This is the integrated part of Annals II (176). The source is supplied already
    sampled on `eta`; nothing about the source is assumed here, which is what lets
    the same routine carry the Doppler and the integrated Sachs-Wolfe terms.
    """
    x = k * (eta_0 - np.asarray(eta, dtype=float))
    return float(np.trapezoid(np.asarray(source, dtype=float) * table(ell, x), eta))
