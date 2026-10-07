+++
id = "F3"
order = 3
title = "The angular power spectrum from Annals II (186), by two routes"
script = "scripts/figure_f3_angular_spectrum.py"
artefact = "figures/f3-angular-spectrum-v1.0.0.pdf"
category = "recovery"
caption = """
Eq.~(186) computed from Eq.~(176), for the standard-CDM model of \\S8.3.2 and for
$\\Lambda$CDM, which \\emph{Annals~II} does not treat. \\textbf{Upper panel:}
$D_\\ell=\\ell(\\ell+1)C_\\ell/2\\pi$, each normalised to its own $\\ell=2$ value, so
that the comparison is of \\emph{shape} and not of an amplitude neither model
fixes here. \\textbf{Lower panel:} the fractional difference between the mode
route of (186) and the covariant route of (187) with (188). Those two are
identical analytically, so the panel is a check on the arithmetic and not on the
physics --- and it is worth having, because it caught a factor of four in this
bundle's own harmonic weights before any figure was drawn. It sits at
$10^{-16}$, five orders below the $10^{-11}$ acceptance threshold.
"""
+++

# F3 — The angular power spectrum from Annals II (186), by two routes

**This is the v1.0.0 deliverable.** Everything upstream of it exists to make this
one number per multipole trustworthy: the background from the $1+3$ constraint,
recombination and the visibility, the acoustic pair (152)/(153), the three
sources (177)--(179), and the line-of-sight integral (176).

## What the figure claims

**The shape.** A Sachs--Wolfe plateau at low $\ell$, an acoustic rise, a first
peak, and the beginning of damping. Standard CDM is flat to within 30% over
$2\le\ell\le20$ and peaks near $\ell\simeq200$ at $5.8$ times the plateau, which
is about right.

**That the two routes agree.** $3\times10^{-16}$ and $4\times10^{-16}$ for the two
models. The harmonic normalisation cancels out of (186) exactly once (176) is
written in $\alpha_\ell^{-1}\tau_\ell$, and that cancellation is asserted in exact
rationals rather than checked numerically.

## What the figure does not claim

**The peak position and amplitude are not yet trustworthy.** Three reasons, all
stated rather than discovered later:

1. **No external comparison has been run.** Criterion 5b compares against CAMB
   and CLASS with a tolerance measured as their mutual difference. Until that is
   done, nothing here has been checked against an independent code.
2. **Recombination is equilibrium Saha.** It places last scattering within a few
   percent in redshift and is enough to exercise every weight in the problem, but
   it decouples too sharply and too early. Peebles' effective three-level atom is
   required before 5b can be met.
3. **$\Lambda$CDM's peak-to-plateau ratio is about 36**, where it should be nearer
   six. Standard CDM's $5.8$ is about right, so whatever is wrong is specific to
   the $\Lambda$ case --- most likely in the late-time potential decay or in the
   normalisation of the integrated term that carries it. **This is the first
   thing to check at 5b**, and it is named here rather than left for a reader to
   notice.

## The weighting used, and why it is not (178)'s

The integrated sources are weighted by the opacity $e^{-\kappa}$ of (98), not by
the visibility $\mathcal V$ of (178). Both are the antecedent's own; (98) is the
earlier and less approximated. With $\mathcal V$ there is **no Sachs--Wolfe
plateau at all** --- $D_\ell\propto\ell^2$ across the whole range, because
$\mathcal V\kappa'\sim\kappa'^2e^{-\kappa}$ swamps the primary source by six
orders of magnitude. Recorded as approximation **A-2** in
`provenance/SOURCE-APPROXIMATIONS-v1.md`, with the measured comparison, and
explicitly **not** as a finding against (178): the mapping between the tilde
variables of §5 and the untilded ones of (98) has not been derived in full here,
and $\tilde v_B=\tilde\tau_1$ is the reading that would have to be revisited.

## Release status

**Release candidate.** This figure is the designated key figure for v1.0.0 and
replaces F1 in the README once criterion 5b is met. Until then F1 leads, because
F1 is the *independence* and F3 is the *recovery*, and a reader should not
mistake one for the other.
