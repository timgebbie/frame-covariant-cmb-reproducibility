+++
id = "F10"
order = 10
title = "When the spectrum is laid down: $C_\\ell$ accumulated in conformal time"
script = "scripts/figure_f10_formation_surface.py"
artefact = "figures/f10-formation-surface-v1.3.0.pdf"
category = "diagnostic"
caption = """
\\textbf{The fraction of today's $C_\\ell$ already in place at conformal time
$\\eta$}, for $\\ell=2,5,10,30,100,200$. Columns are the three backgrounds this
bundle ships --- CDM (Einstein--de~Sitter), $\\Lambda$CDM, and the stamped
Planck~2018 set; rows are the Newtonian and CDM frames, from \\emph{one} solve.
The abscissa is $(\\eta-\\eta_\\ast)/(\\eta_0-\\eta_\\ast)$ on a logarithm,
because the visibility is narrow and a linear axis spends almost all of itself
on the free-streaming era where by construction nothing is laid
down.\\\\[2pt]
\\textbf{What is accumulated, and it is one pass rather than one spectrum per
slice.} \\texttt{integral\\_solution} accumulates the bulk integrand
cumulatively in $\\eta$ \\emph{inside the quadrature the released path already
runs}, so there is no second definition of the integral to drift from the
first. The boundary terms are held out of the accumulation deliberately: they
are emitted at $\\eta_\\ast$ and afterwards only projected, so they are present
in full in every slice, and telling those two apart is what the instrument is
for.\\\\[2pt]
\\textbf{The gate, and it is what makes the rest of the figure evidence.} The
$\\eta_0$ column must reproduce the released spectrum exactly --- it is the
same integral, decomposed. Asserted at $10^{-9}$, measured at
$1.2\\times10^{-12}$. If the accumulation disagreed with the quadrature it
decomposes, nothing read off the panels would be about the
physics.\\\\[2pt]
\\textbf{What it shows, and it is the result rather than the illustration.}
Every curve reaches $1$ within $1\\%$ of the conformal span past
$\\eta_\\ast$ and is flat afterwards: \\emph{the spectrum is finished at
recombination}, on all three backgrounds and in both frames. The late share ---
everything deposited after the visibility has closed --- reads $0.0000$ in all
thirty-six curves. On $\\Lambda$CDM and the Planck set that is wrong by
construction, because the late integrated Sachs--Wolfe effect must deposit
$\\mathcal{O}(0.1)$ of $C_2$ there. On Einstein--de~Sitter it is right by
construction, because $\\Phi$ is exactly constant (Appendix~G) and there is no
late ISW to have. \\textbf{That null control is what makes the first two
readings a defect rather than a numerical artefact}: were something other than
the weight wrong, the EdS column would not come out exactly
zero.\\\\[2pt]
\\textbf{The mechanism, and it is B-17 discrepancy~(i).} (102) carries the bulk
bracket at $\\mathcal{V}\\mathcal{D}$ where the exact by-parts of its own
integral wants $W$; $\\mathcal{V}=W\\kappa'$ is sharply peaked at $\\eta_\\ast$
and is zero afterwards, so every late-time source is multiplied by zero.
\\textbf{The late ISW is not missing from the formalism --- it is present at
rank one and annihilated by the weight.} No repair has been adopted into the
released path, and \\texttt{provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md}
carries B-17 with all four of its discrepancies.\\\\[2pt]
\\textbf{Why a figure and not a gate.} $\\ell_{\\rm peak}$ (D27) and the median
contributing $k$ (D25) are scalar summaries of the \\emph{endpoint}, and three
pre-registered predictions were scored against them before this was drawn. The
missing plateau power is a defect \\emph{in time}, so no summary of the
endpoint can see it. \\textbf{F10 does not supersede F9}: F9 says \\emph{where}
the power lands in $\\ell$, F10 says \\emph{when} it was laid down, and those
are different failures with different causes.
"""
+++

# F10 — when the spectrum is laid down

**The standalone caption.** This is the figure a reader should open first if
they want to know what is wrong with this release's spectrum, because it is the
only artefact in the bundle in which the plateau's defect is visible at all.

## The question it answers

Every other instrument here measures a *finished* spectrum. F9 draws $C_\ell$
at $\eta_0$; D27 reduces that spectrum to a peak position; D25 reduces it to a
median contributing $k$. Those refute, and they refuted three pre-registered
predictions over the week before this was drawn — but **a defect in *when*
power is deposited has no signature in any summary of the endpoint**, because
the endpoint is the one place where the accumulation has already finished.

So the instrument is the accumulation itself: for each multipole, what fraction
of today's $C_\ell$ is already in place at conformal time $\eta$.

## How to read the panels

Each panel is one background and one frame. Each curve is one multipole,
normalised by its own final value, so the subject is the **shape in $\eta$**
rather than the growth. The abscissa is the fraction of the conformal span past
recombination, logarithmically, because the visibility is narrow: on a linear
axis, ninety-nine percent of the panel would be free streaming.

A correct assembly on $\Lambda$CDM or the Planck set shows two features: a step
at $\eta_\ast$ as the visibility deposits the acoustic and Doppler terms, and
then a **second rise at late times** at low $\ell$, as the decaying potential
deposits the late integrated Sachs–Wolfe contribution along the line of sight.
Einstein–de Sitter shows only the first, because $\Phi$ is constant there.

## What it reads

All six panels show the step and **none shows the second rise**. The late
share — the fraction deposited after the first one percent of conformal time
past $\eta_\ast$, which is after the visibility has closed — is `0.0000` in
every one of the thirty-six curves.

| background | required late share at $\ell=2$ | measured |
|---|---|---|
| Einstein–de Sitter | exactly 0 — $\Phi$ constant, Appendix G | 0.0000 |
| $\Lambda$CDM | $\mathcal O(0.1)$ — the late ISW | 0.0000 |
| Planck 2018 | $\mathcal O(0.1)$ — the late ISW | 0.0000 |

**The first row is the falsifier.** A numerical defect that annihilated late
accumulation would have to annihilate it on EdS too, and EdS is the one
background where zero is the right answer. A defect that produced spurious late
accumulation would show up there as a non-zero share. Zero on EdS and zero on
the Λ backgrounds together say: *the late-time source is being multiplied by
something that has already gone to zero*, and not that the integration is
wrong.

That something is $\mathcal V = W\kappa'$. B-17 discrepancy (i): (102) carries
the bulk bracket $C_0 - C_1' + C_2''$ at $\mathcal{V}\mathcal{D}$ where the
exact by-parts of its own integral wants $W$. $W=e^{-\kappa}$ survives to
$\eta_0$; $\mathcal V$ is the visibility and closes at recombination.

## What it does not say

* **It does not say the plateau is now right.** It says one named term is
  annihilated, and locates the annihilation. The plateau's level also depends
  on the ordinary Sachs–Wolfe term and on the frame gap, neither of which this
  figure measures.
* **It does not adopt a repair.** `bracket_all_at_w` is the control for
  discrepancy (i) and is reachable from the spectrum, but no configuration has
  been adopted into the released path: the one that lands the first peak in the
  CDM frame (D28) misses it by a factor of 3.1 in the Newtonian frame, and
  $\ell\ge2$ is frame-invariant at first order.
* **It is sixteen slices**, which is enough to establish that the curves are a
  step followed by a flat, and not enough to resolve the shape of the step
  itself. D30 runs twenty-four and reports the same thing.

## Provenance

Diagnostic **D30**, finding **T-128**. Generated by
`scripts/figure_f10_formation_surface.py`; the accumulation is committed as
`outputs/f10-formation-surface.csv`, stamped with a digest of the code that
produced it, and `--replot` refuses to redraw numbers this tree did not compute
(**T-54**).
