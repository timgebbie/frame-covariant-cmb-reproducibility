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
        ells: np.ndarray | None = None,
        points_per_period: int = 12,
    ) -> "BesselTable":
        r"""Tabulate $j_\ell(x)$ on $[0,x_{\max}]$, for `ells` or for
        $[\ell_{\min},\ell_{\max}]$.

        **`ells` tabulates only the multipoles asked for** --- finding **T-18**.
        The contiguous form builds every $\ell$ up to $\ell_{\max}$ whether or
        not the caller wants it, which is free at $\ell_{\max}=400$ and is not
        free at 2000: the spectrum is computed on a *logarithmic* $\ell$ grid of
        about thirty points, so the contiguous build is ~60x the splines, and at
        the $x_{\max}$ a high-$\ell$ run needs it comes to some 1.5 GB of cubic
        coefficients, nearly all of them for multipoles nothing will ever ask
        for. The sparse form is the same table with the unasked rows left out.

        The contiguous path is kept and is unchanged, because the diagnostics
        and the low-$\ell$ release figures use it and there is no reason to
        move them.
        """
        if x_max <= 0:
            raise ValueError("x_max must be positive")
        n = max(int(points_per_period * x_max / pi), 64)
        x = np.linspace(0.0, x_max, n)
        if ells is None:
            ell = np.arange(ell_min, ell_max + 1)
        else:
            ell = np.unique(np.asarray(ells, dtype=int))
            if ell.size == 0:
                raise ValueError("ells is empty")
            if ell[0] < 0:
                raise ValueError("ells must be non-negative")
        values = np.empty((ell.size, x.size))
        for i, l in enumerate(ell):
            values[i] = spherical_jn(int(l), x)
        splines = tuple(CubicSpline(x, values[i], extrapolate=False) for i in range(ell.size))
        return cls(ell=ell, x=x, values=values, _splines=splines)

    def __call__(self, ell: int, x: np.ndarray | float) -> np.ndarray:
        """j_l at arbitrary x, by interpolation. Zero outside the tabulated range.

        **Looked up, not subtracted.** The index used to be
        `ell - self.ell[0]`, which is correct only while the tabulated set is
        contiguous; a sparse table built from `ells` would have silently
        returned a *different* multipole's Bessel function rather than raising.
        """
        idx = int(np.searchsorted(self.ell, int(ell)))
        if idx >= self.ell.size or int(self.ell[idx]) != int(ell):
            raise ValueError(
                f"ell={ell} is not tabulated; this table carries "
                f"{self.ell.size} multipole(s) from {self.ell[0]} to {self.ell[-1]}"
            )
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
