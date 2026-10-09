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

**The shape.** A Sachs--Wolfe plateau at low $\ell$ and a rise beyond it. Over
$2\le\ell\le20$ --- the range D0 independently adopts from the dropped acoustic
modulation --- standard CDM is flat to within 30%. $\Lambda$CDM's ratio of the
largest $D_\ell$ to $D_2$ is $7.15$ and standard CDM's is $60.9$, and the
difference between them is the $\chi_*$ lever arm: $\Lambda$CDM's larger
$\chi_*$ maps a given $\ell$ to a smaller $k$, so it climbs more slowly. This
formulation carries no matter transfer function and (178)'s Doppler term carries
an explicit factor of $k$, so power keeps rising until diffusion damping bites
--- which, on this $k$ grid, it never does.

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
3. **The $k$ grid is truncated, not converged.** It stops at $k_{\max}=420$
   where $\exp[-(k/k_D)^2]$ is still $0.89$ for CDM and $0.78$ for
   $\Lambda$CDM: the integral ends while the source is still contributing
   nearly its full weight. Measured against a grid four times longer, that
   costs $0.1\%$ at $\ell=2$, $5\%$ at $\ell=50$, $11\%$ at $\ell=200$ and
   $24\%$ at $\ell=400$. Reaching the cut-off needs $k_{\max}\gtrsim3100$ and
   a correspondingly finer $\eta$ grid, which this line-of-sight implementation
   cannot do in reasonable time --- an architecture problem, named in **T-3**
   and owned by v1.2.0, not a parameter to be nudged.

An earlier version of this caption read the $\Lambda$CDM ratio as $36$ against
CDM's $5.8$ and called the first of those wrong. **Both numbers were artefacts**
of an aliased line-of-sight integrand, finding **T-3**; the one that looked
right was as wrong as the one that looked wrong. The values above are measured
on the corrected grid.

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

**Released in v1.0.0, as the README's key figure.** F1 follows it rather than
leads it — but the distinction that ordering was protecting still holds and is
worth keeping in front of a reader: **F1 is the *independence* and F3 is the
*recovery***, and the two answer different questions. F3's comparison target is
derived from the same antecedent, so F3 cannot establish independence however
well it agrees; F1 can, because its four hierarchies were each read from their
own paper.

At **v1.2.0** the key figure becomes the normalised spectrum with its acoustic
peaks (decision S18), and F3 moves to second place beside the acoustic-mode
figures and their Hu &amp; Sugiyama checks.
