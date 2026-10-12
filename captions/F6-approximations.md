+++
id = "F6"
order = 6
title = "What each approximation is worth"
script = "scripts/figure_f6_approximations.py"
artefact = "figures/f6-approximations-v1.1.0.pdf"
category = "diagnostic"
caption = """
Each series is
$C_\\ell^{\\mathrm{approximate}}/C_\\ell^{\\mathrm{fuller}}$ for standard CDM, so
the panel is scale-free and a flat line at unity is an approximation that costs
nothing. \\emph{Annals~II} makes three narrowing choices which this bundle
reproduces rather than corrects, because reproducing a paper means reproducing
its approximations (decision~S15); they are recorded as \\textbf{A-n} in
\\texttt{provenance/SOURCE-APPROXIMATIONS-v1.md}, deliberately apart from the
defects recorded as \\textbf{B-n}. This is the one place their cost is a number
rather than an adjective.\\\\[2pt]
\\textbf{The three do not have comparable weights, and that is the result}, so
the axis spans six decades rather than cropping them to look alike. The
visibility weighting on the gravitational source (A-1) runs to
$10^4$--$10^6$: it is a \\emph{different calculation}, not a perturbation of
one, which is why \\texttt{Weighting} has no default. Stipulating $k_D$ at
last scattering costs under $0.1\\%$ across the claimed range and about $5\\%$ by
$\\ell=400$ --- it \\textbf{vindicates the release}, which takes the cheap
choice where it makes claims. The small-scale approximation, dropping
$-aH\\Phi_A$ from~(153) and so producing the printed oscillator~(154), departs
from unity most at \\emph{large} scales, which is what its name predicts.
\\\\[2pt]
\\textbf{A correction kept because it nearly became this figure.} The $k_D$
series was first computed with $k_D(\\eta)$ along the whole ray. After last
scattering $\\kappa'\\to0$, so $1/\\kappa'$ in (dif-damp) diverges and $k_D$
collapses, damping every integrated source to nothing --- a plasma formula
evaluated in a universe that no longer has a plasma. That version reported the
release's choice as costing a factor of nine at $\\ell=2$; the factor was the
artefact. Clamped to $k_D(\\min(\\eta,\\eta_*))$ the comparison is a real one.
Shaded: beyond $\\ell=20$, which this release does not claim.
"""
+++
