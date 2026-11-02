r"""Where the first acoustic peak is. **One definition, finding T-184.**

Three implementations of "the first acoustic peak" were live in this tree on
31 October 2026, with three different semantics, and the differences were not
documented anywhere because nobody had put them side by side:

===========================  =================  ==========================
instrument                   band               criterion
===========================  =================  ==========================
`d24.peak_position`          **none**, l >= 2   global `argmax` + parabola
`d36._peak`                  floor 30           **first interior maximum**
`compare_criterion_5b`       **[100, 320]**     `argmax`, no interpolation
===========================  =================  ==========================

**The one without a band is the one wired to a gate, and it is wrong.** The
released spectrum carries a spurious maximum at $\ell\simeq7$ at $9.6\times$
CAMB's plateau (T-181b). A global `argmax` over $\ell\ge2$ finds *that*, so
**D27's gate G-a has been reporting a plateau feature under the name of a
peak-position gate** --- its published $0.0073$ against a pre-registered
$[0.55,0.80]$ is the finder landing on $\ell=8.10$, which is what parabolic
interpolation gives around a maximum at the $\ell=7$ sample of D24's grid.

That number is in `README.md` as a scored and failed pre-registered
prediction. **It is an instrument artefact and the prediction was never
tested.**

WHY A FLOOR IS PHYSICS AND NOT TASTE
------------------------------------
$D_\ell$ below $\ell\sim30$ is the Sachs--Wolfe plateau, and the plateau is
**not acoustic**: it is the $\ell\to$ large-scale limit of the monopole and
potential, carrying no $\cos kr_s$ structure. An instrument asked for the
first *acoustic* extremum must therefore not be allowed to return one, and
the only thing separating the two is where you start looking. A finder with
no floor is not a more general finder --- **it is a finder that answers a
different question than the one its callers ask.**

The floor is a parameter because the right value depends on the background:
30 is where the plateau ends on PLANCK, and a model with a different
$\ell_A$ moves it. It is not a parameter so that callers can tune it until a
gate passes, and the default is stated rather than passed at every call site
so that a caller who has not thought about it gets the physics rather than
whatever they typed.

WHY ONE MODULE AND NOT A SHARED CONVENTION
------------------------------------------
This bundle has been bitten four times by the same shape --- a rule that two
or more copies be kept in step, kept only by someone remembering:
`gen_theory_audit.py`'s three registries, the two copies of the tight-coupling
continuation (**T-125**), `build_supplement.py`'s staged directory list
(**T-174**), and now this. Each time the author of the next change was not the
author of the list. **The repair is never a better note.**

D41 made this argument for itself in October and imported D36's finder rather
than copying it, which is why D41 and D36 cannot disagree. This file is that
argument applied to all of them.
"""
from __future__ import annotations

import numpy as np

#: Where the Sachs--Wolfe plateau ends on PLANCK, so the first *acoustic*
#: extremum is the first one above it. Stated once; see the module docstring
#: for why this is physics and why it is nonetheless a parameter.
PLATEAU_FLOOR = 30.0


def acoustic_maxima(
    ells, d_ell, *, floor: float = PLATEAU_FLOOR, prominence: float = 0.10,
) -> list[float]:
    r"""Every interior maximum above `floor` that stands `prominence` proud.

    **The threshold is the whole point and a count without one is noise.**
    On 2026-11-02 a bare count of local maxima reported the released
    Newtonian Einstein--de~Sitter spectrum as having *three* --- $\ell=450$,
    690 and 870 --- and that read as the acoustic peak series everyone has
    been looking for. It was not. The values are

        450  0.00152        690  0.00005        870  0.00004

    of $D_{30}$: the second and third are **3 per cent of the first**, in the
    fifth decimal of a renormalised quantity, a hundredfold down the damping
    tail. They are ripple on a floor, and a counter with no amplitude test
    cannot tell them from peaks.

    `prominence` is measured against the **running maximum so far**, not
    against the global one, because a genuine series falls steeply: the
    second acoustic peak of a real spectrum is a few tenths of the first, and
    a global threshold would discard it along with the noise. Ten per cent of
    the tallest peak seen up to that $\ell$ keeps a real series and rejects a
    tail ripple, and it is stated here rather than buried at a call site so
    that a count printed anywhere in this bundle means the same thing.
    """
    ells = np.asarray(ells, dtype=float)
    d = np.asarray(d_ell, dtype=float)
    out: list[float] = []
    tallest = 0.0
    # **The same candidate rule as `first_acoustic_peak`, exactly**: a
    # maximum's left neighbour must itself be at or above the floor. The first
    # draft let the floor point qualify, and on PLANCK's released Newtonian
    # frame that made l = 30 --- the renormalisation anchor, where D/D_30 is
    # 1 by construction --- a "maximum", which then seeded the prominence
    # test and rejected the real first peak at 415 as too small beside it.
    # The two functions in this module returned [30] and 415.4 for the same
    # curve: a second copy in miniature, inside the file that exists to
    # remove second copies.
    idx = np.nonzero(ells >= float(floor))[0]
    for i in idx[1:-1]:
        if not (d[i] > d[i - 1] and d[i] >= d[i + 1]):
            continue
        if tallest and d[i] < float(prominence) * tallest:
            continue
        tallest = max(tallest, float(d[i]))
        out.append(float(ells[i]))
    return out


def first_acoustic_peak(
    ells, d_ell, *, floor: float = PLATEAU_FLOOR,
) -> tuple[float, float]:
    r"""First interior maximum of $D_\ell$ above `floor`, interpolated.

    Returns `(position, uncertainty)`, the uncertainty being **half the local
    grid spacing** --- the honest floor on a three-point interpolation, not an
    error estimate. Returns `(nan, nan)` when there is no interior maximum
    above `floor`, which is **a result and not a failure**: the released
    Newtonian frame genuinely has none under some weightings, and D36 reports
    exactly that.

    **Parabolic, not `argmax`.** On these grids `argmax` can only return a
    sample, and the spacing near the peak is larger than the differences the
    sweeps are looking for. The vertex of a parabola through three nearly
    equal samples wanders, so a vertex offset far from the central sample is a
    statement about **curvature** and not about validity --- D41 established
    that against a broad maximum and it is recorded here so the next reader
    does not re-derive it as a defect.
    """
    ells = np.asarray(ells, dtype=float)
    d = np.asarray(d_ell, dtype=float)
    if ells.shape != d.shape or ells.size < 3:
        raise ValueError("ells and d_ell must share a shape of at least 3")

    idx = np.nonzero(ells >= float(floor))[0]
    if idx.size < 3:
        return float("nan"), float("nan")

    for i in idx[1:-1]:
        if d[i] > d[i - 1] and d[i] >= d[i + 1]:
            den = d[i - 1] - 2.0 * d[i] + d[i + 1]
            half = 0.5 * float(min(ells[i] - ells[i - 1], ells[i + 1] - ells[i]))
            if den == 0.0:
                return float(ells[i]), half
            # **The Lagrange vertex, which is exact for UNEQUAL spacing.**
            # Taken from D24, whose interpolation was always the better of
            # the two: these grids change spacing at the join between their
            # sparse and dense halves, and D36's form assumes the three
            # samples are evenly spaced.
            #
            # **Measured before adopting, because a refactor that silently
            # moves a published number is the thing this file exists to
            # prevent.** On D41's committed spectra, both frames, on D36's
            # grid and on D41's fine grid: the two forms agree to **+0.000 in
            # all four**, D36's 60.65 reproducing as 60.647. They agree
            # because wherever a first interior maximum is actually found the
            # three bracketing samples turn out to be evenly spaced, so the
            # exact form and the even-spacing form coincide there. Nothing
            # published moves; the exactness is insurance for grids that have
            # not been built yet.
            x0, x1, x2 = ells[i - 1], ells[i], ells[i + 1]
            y0, y1, y2 = d[i - 1], d[i], d[i + 1]
            lag = (x0 - x1) * (x0 - x2) * (x1 - x2)
            if lag == 0.0:
                return float(x1), half
            a = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / lag
            b = (x2 * x2 * (y0 - y1) + x1 * x1 * (y2 - y0)
                 + x0 * x0 * (y1 - y2)) / lag
            if a == 0.0:
                return float(x1), half
            return float(-b / (2.0 * a)), half
    return float("nan"), float("nan")
