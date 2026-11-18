+++
id = "F3"
order = 3
title = "The angular power spectrum from Annals II (186), by two routes"
script = "scripts/figure_f3_angular_spectrum.py"
artefact = "figures/f3-angular-spectrum-v1.0.0.pdf"
category = "recovery"
caption = """
Eq.~(186) computed from Eq.~(176), for the standard-CDM model of \\S8.3.2 and for
$\\Lambda$CDM, which \\emph{Annals~II} does not treat. The upper panel shows
$D_\\ell=\\ell(\\ell+1)C_\\ell/2\\pi$, each normalised to its own $\\ell=2$ value, so
that the comparison is of \\emph{shape} and not of an amplitude neither model
fixes here. (176) is integrated as printed, with (178) and (179) at the
visibility (A-1, A-2), and under that weight the Doppler source of (178)
carries the spectrum: $D_\\ell/D_2$ falls to $0.25$ for standard CDM and $0.34$
for $\\Lambda$CDM at $\\ell=6$, returns to $0.72$ and $0.74$ at $\\ell=20$, and
falls to $1.7$ and $1.3\\times10^{-3}$ at $\\ell=252$. There is no Sachs--Wolfe plateau
(A-2, T-69); the released spectrum is the frame-invariant assembly of Figure~9.
The lower panel shows the fractional difference between the mode route of (186)
and the covariant route of (187) with (188). Those two are identical
analytically, so the panel is a check on the arithmetic and not on the physics.
That check caught a factor of four in this bundle's own harmonic weights before
any figure was drawn. Since T-17 both routes combine their weights as exact
rationals, and they agree to the last bit.
"""
+++

# F3 — The angular power spectrum from Annals II (186), by two routes

**This is the v1.0.0 deliverable.** Everything upstream of it exists to make this
one number per multipole trustworthy: the background from the $1+3$ constraint,
recombination and the visibility, the acoustic pair (152)/(153), the three
sources (177)--(179), and the line-of-sight integral (176).

## What the figure shows

**Regenerated on 18 November 2026 (T-197).** Until then the committed figure
was the spectrum under the opacity weight $e^{-\kappa}$ of (98), drawn in
mid-October; the script had computed (176) at the printed visibility since the
default flipped on 19 October (A-2), and nothing re-ran it.

**The shape.** Under the visibility the Doppler source of (178) carries the
spectrum, which is the object A-2 names: $\mathcal V\kappa'\sim\kappa'^2e^{-\kappa}$.
$D_\ell/D_2$ falls to $0.25$ (standard CDM) and $0.34$ ($\Lambda$CDM) at
$\ell=6$, returns to $0.72$ and $0.74$ by $\ell=20$, reaches $0.76$ near
$\ell=30$, and falls to $1.7$ and $1.3\times10^{-3}$ at $\ell=252$. There is no
Sachs--Wolfe plateau. A-2's post-T-66 table (T-69) measured the same shape on
all three backgrounds, and the opacity weight's plateau without acoustic
structure beside it.

**That the two routes agree.** To the last bit on both models: since T-17 the
combined coefficients of (186) and of (187) with (188) are formed in exact
rationals, so the two routes are one arithmetic, and the lower panel's line is
drawn at its floor.

## What the figure does not claim

1. **That this is the spectrum.** The released spectrum is the frame-invariant
   assembly of F9 (v1.3.0), which replaced (176)'s line of sight. F3 is the
   antecedent's formalism integrated as printed, and the route check.
2. **Anything beyond $\ell=20$.** (186) drops the acoustic modulation, which
   costs 4.75% at $\ell=20$ and grows (`scripts/derive_ell_range.py`).
3. **A converged tail.** The $k$ grid stops at $k_{\max}=420$, where
   $e^{-(k/k_D)^2}$ is $0.77$ for standard CDM and $0.50$ for $\Lambda$CDM.
   Dropping its top 10% moves $D_\ell$ by $2\times10^{-8}$ over the claimed range
   and by $1.9\times10^{-3}$ and $7\times10^{-5}$ out to $\ell=400$; the
   script prints both on every run.

An earlier version of this caption read the $\Lambda$CDM ratio as $36$ against
CDM's $5.8$ and called the first of those wrong. **Both numbers were artefacts**
of an aliased line-of-sight integrand, finding **T-3**; the one that looked
right was as wrong as the one that looked wrong.

## The weighting used

(178) and (179) at the visibility $\mathcal V$, as printed, since 19 October.
Before then the integrated sources carried the opacity $e^{-\kappa}$ of (98),
on a measurement taken before T-66 corrected $\kappa'\tilde v_B$ by a factor of
$k$; T-69 found that basis void, and `provenance/SOURCE-APPROXIMATIONS-v1.md`
records both weights' spectra under **A-2**.

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
