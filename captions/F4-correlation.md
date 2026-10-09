+++
id = "F4"
order = 4
title = "The angular correlation function, and the transform that makes it"
script = "scripts/figure_f4_correlation.py"
artefact = "figures/f4-correlation-v1.0.0.pdf"
category = "acceptance"
caption = """
$C(\\theta)=\\sum_\\ell\\frac{2\\ell+1}{4\\pi}C_\\ell P_\\ell(\\cos\\theta)$, the
real-space view of Figure~3: the same content read as a correlation between two
directions separated by $\\theta$ rather than as power at a multipole.
\\textbf{Upper panel:} $C(\\theta)/C(0)$ for standard CDM and $\\Lambda$CDM,
summed over $2\\le\\ell\\le20$ --- the range Figure~3 claims, bounded by (186)
dropping the acoustic modulation. Summing further would draw multipoles this
release does not stand behind, and a real-space curve hides which $\\ell$
contributed, so the restriction is made in the transform rather than in this
caption. \\textbf{Lower panel:} the Legendre round trip
$C_\\ell\\to C(\\theta)\\to C_\\ell$, at $4\\times10^{-14}$ and
$7\\times10^{-14}$ against an acceptance of $10^{-13}$. It tests the transform
and \\emph{not} the spectrum --- the two share their $C_\\ell$ --- which is the
same caution Figure~3's residual panel carries and for the same reason.
"""
+++

# F4 — The angular correlation function

**The quadrature node count is derived, not chosen, and the first version of
this figure got it wrong in the unobvious direction.** The integrand is
$P_\ell P_{\ell'}$ of degree at most $2\ell_{\max}$, and $n$ Gauss--Legendre
nodes integrate degree $2n-1$ exactly, so $n=\ell_{\max}+1$ is the smallest
exact choice. It was first written with $n=128$, picked for comfort, and the
round-trip residual came out thirteen times worse: measured across node counts
the residual *grows*, 1.8e-14 at $n=21$ against 1.6e-12 at $n=512$. The
quadrature is already exact; every node past the requirement buys nothing and
costs summation error.

That is finding **T-3** seen from the other side. There a grid was too coarse
and aliased the integrand; here one was too fine and accumulated roundoff. Both
came of choosing a grid instead of deriving it from what the integrand needs.

**The acceptance is measured rather than chosen** for the same reason. The
first version carried $10^{-12}$ because it is a round number, and it failed —
which is the right outcome for a tolerance nobody measured.
