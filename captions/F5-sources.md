+++
id = "F5"
order = 5
title = "The source decomposition, by rank, in two frames"
script = "scripts/figure_f5_sources.py"
artefact = "figures/f5-sources-v1.2.0.pdf"
category = "cross-check"
caption = """
The integral solution~(102) carries three coefficients $C_0$, $C_1$, $C_2$ ---
one per PSTF rank --- and this figure draws them, in the Newtonian frame and in
the CDM frame, against $\\ell$.\\\\[2pt]
\\textbf{Drawn in ranks, not in the Newtonian three-way split of \\S7.1.1.} That
was the PI's call, 2026-10-14, and it is a scientific choice rather than a
presentational one: the primary/Doppler/integrated split is \\emph{defined only
in the frame it is written in}, while the rank decomposition is what~(89)
produces and is defined in every frame. A figure comparing two frames must be
drawn in a decomposition both of them have.\\\\[2pt]
\\textbf{The ranks sum to the total}, to $0$ exactly in the Newtonian frame and
$4.1\\times10^{-16}$ in the CDM frame --- which is the check that the
decomposition is a decomposition and not three curves that happen to be near
the answer. At the $C_\\ell$ level the autos and twice the crosses reproduce
$C_\\ell$ to $4.7\\times10^{-16}$ while the autos \\emph{alone} are off by
$0.10$: $C_\\ell$ is quadratic in the transfer, so the cross terms are not a
correction to be neglected but half the statement.\\\\[2pt]
\\textbf{The frame disagreement is the result, and it is its own panel.} The two
frames' $C_\\ell$ differ by a median of $15\\%$ over $2\\le\\ell\\le400$, worst
$49\\%$. That is not a defect: $C_\\ell$ as computed here is built from
frame-dependent pieces, and the invariance statement~(102) satisfies is about
the \\emph{total} at fixed $k$, which diagnostic~D6 measures separately. The
median moved from $11\\%$ to $15\\%$ when finding \\textbf{T-37} wired the
transfer function, which is the kind of movement a figure should report rather
than absorb.\\\\[2pt]
\\textbf{Superseded 2026-10-20, findings T-57, T-59 and T-85.} The number above is the figure's, and the figure predates \\textbf{T-57}. \\textbf{The frame disagreement is no longer read as a result.} It is \\emph{total} --- median $9.99\\times10^{-1}$, worst $1.00$ --- and the $\\ell\\ge2$ multipoles are frame-invariant \\emph{by theorem}, so a gap there is a defect and is being hunted. It is localised: the rank-1 source agrees between the columns to $10^{-15}$ (\\textbf{T-82}) and the by-parts identity holds in both (\\textbf{T-85}), so the whole of it is the slot-and-weight assignment of $C_1$ (\\textbf{T-86}). \\texttt{provenance/BUNDLE-DEFECTS-v1.md} is authoritative; this caption is not regenerated until the figure is.
"""
+++
