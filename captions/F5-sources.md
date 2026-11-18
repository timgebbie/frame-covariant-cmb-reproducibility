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
The figure is drawn in ranks, not in the Newtonian three-way split of
\\S7.1.1. That was the PI's call, 2026-10-14, and it is a scientific choice rather than a
presentational one: the primary/Doppler/integrated split is \\emph{defined only
in the frame it is written in}, while the rank decomposition is what~(89)
produces and is defined in every frame. A figure comparing two frames must be
drawn in a decomposition both of them have.\\\\[2pt]
The ranks sum to the total, to $0$ exactly in the Newtonian frame and
$1.8\\times10^{-16}$ in the CDM frame --- which is the check that the
decomposition is a decomposition and not three curves that happen to be near
the answer. At the $C_\\ell$ level the autos and twice the crosses reproduce
$C_\\ell$ to $7.2\\times10^{-16}$ while the autos \\emph{alone} are off by
$0.19$: $C_\\ell$ is quadratic in the transfer, so the cross terms are not a
correction to be neglected but half the statement.\\\\[2pt]
The frame disagreement is the result, and it has its own panel. The two
frames' $C_\\ell$ differ by a median of $89\\%$ over $2\\le\\ell\\le400$, worst
$99.9\\%$: the total~(102) builds is not frame-invariant (\\textbf{T-59}), which
is why v1.3.0 replaced it with the assembly diagnostic~D44 measures. Until this
figure was regenerated on 18 November 2026 (\\textbf{T-197}) this paragraph
read a median of $15\\%$ and called the difference the decomposition's, from a
figure drawn before the line-of-sight weight and the dipole's normalisation
were settled.\\\\[2pt]$^{\\dagger}$\\,\\emph{Superseded by findings} \\textbf{T-57}\\emph{,} \\textbf{T-59}\\emph{; see} \\texttt{provenance/BUNDLE-DEFECTS-v1.md}.
"""
+++
