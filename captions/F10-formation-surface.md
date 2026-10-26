+++
id = "F10"
order = 10
title = "The angular autocorrelation as it forms: $C_\\ell(\\eta)$"
script = "scripts/figure_f10_formation_surface.py"
artefact = "figures/f10-formation-surface-v1.3.0.pdf"
category = "diagnostic"
caption = """
\\textbf{The angular autocorrelation at a sequence of conformal times, and the
surface it sweeps.} Planck~2018, CDM frame, 25 multipoles from $\\ell=2$ to
$\\ell=300$, fourteen epochs from the start of recombination to
today.\\\\[2pt]
\\textbf{(a) The autocorrelation, epoch by epoch.} $D_\\ell$ against $\\ell$,
one curve per epoch, with the three the PI named drawn heavy --- just before
decoupling, at $\\eta_\\ast$, and today --- and the rest as context so the
three read as a progression. \\textbf{The lower limit is the recombination
start and not $\\eta_\\ast$} (T-58), so \\emph{before decoupling} is a real
epoch with accumulation in it.\\\\[2pt]
\\textbf{(b) The surface.} $C_\\ell(\\eta)/C_\\ell(\\eta_0)$ over the whole
$(\\ell,\\eta)$ plane. Panel~(a) is read along $\\ell$; this is read along
$\\eta$, and a correct assembly has structure in the band to the right of
recombination, where the late integrated Sachs--Wolfe effect deposits power at
low $\\ell$ long after the visibility has closed.\\\\[2pt]
\\textbf{What it shows, and it is a measurement rather than an illustration.}
Every row of panel~(b) changes colour at the same abscissa and is uniform to
the right of it. \\textbf{The spread across all 25 multipoles, at every epoch,
is at most $0.063$}: every multipole fills at the same rate, the shape in
$\\ell$ is laid down once at recombination, and \\emph{no power moves between
multipoles at any time}. Gated --- the $\\eta_0$ column reproduces the
released quadrature at $4.6\\times10^{-13}$, so the accumulation is that
integral decomposed and not a second definition of it.\\\\[2pt]
\\textbf{What that does and does not establish.} It is a \\emph{fourth}
independent measurement of the annihilation recorded as \\textbf{A-1} and
\\textbf{T-128}, and it adds one thing the other three could not: whatever
annihilates the late integrated Sachs--Wolfe effect does so \\textbf{with no
$\\ell$-dependence at all}, which excludes every candidate mechanism whose
strength varies with the multipole. \\textbf{It does not establish that the
collapse causes the missing plateau or the displaced peak.} Those have
separate causes already localised --- the bare $\\kappa'$ inside $C_1$
(\\textbf{T-101}, \\textbf{T-121}) and the by-parts taken onto the
coefficients (\\textbf{T-94}) --- and a collapsed (102) has been measured in
this bundle producing acoustic maxima and a surviving plateau, so the collapse
cannot be the cause of their absence.\\\\[2pt]
\\textbf{Why a spectrum at each time and not a fraction per multipole.} The
first version of this figure drew six multipoles' accumulation against $\\eta$
and normalised each one. A per $\\ell$ normalisation answers \\emph{how much
of this multipole is in place} and cannot answer \\emph{what shape is the
spectrum now} --- and the plateau is a statement about $\\ell$-dependence at
fixed $\\eta$. It was not a surface, and it could show the defect only as a
flat line rather than as the frozen shape.
"""
+++

# F10 — the angular autocorrelation as it forms

**The standalone caption.** Open this one to see *when* the spectrum is built,
and in particular to see that its shape in $\ell$ is settled at recombination
and never changes afterwards.

## The question it answers

Every other instrument in this bundle measures a *finished* spectrum. F9 draws
$C_\ell$ at $\eta_0$; D27 reduces that to a peak position; D25 reduces it to a
median contributing $k$. None of them can see a defect in *when* power is
deposited, because the endpoint is where the accumulation has already
finished.

So the instrument is the spectrum itself, at a sequence of times.

## How to read the two panels

**(a)** is the autocorrelation you would measure at each epoch, normalised
once — by the maximum of the final curve — so the panel shows growth and shape
together rather than six separately-scaled curves.

**(b)** is the same data as a surface: multipole up the side, conformal time
across, shade the fraction of today's value. A correct assembly is *not*
uniform here. The late ISW is a low $\ell$, late-time effect, so the bottom
rows should keep filling well to the right of recombination.

## What it reads

| | |
|---|---|
| spread across 25 multipoles, worst over all epochs | **0.063** |
| late share, worst multipole | **0.0007** |
| $\eta_0$ column against the released quadrature | $4.6\times10^{-13}$ |

**Every multipole fills at the same rate.** The shape is frozen at
recombination; only the amplitude moves.

## What it does not say

* **It does not say the collapse causes the missing plateau.** It does not. A
  collapsed (102) was measured in this bundle on 19 October producing three
  acoustic maxima and a surviving plateau, and the argument
  $j_\ell(k\Delta\eta_\ast)$ has $k$ integrated over it — which is where
  $\ell_A=\pi r_\theta/r_s$ comes from. The peak series survives a collapse in
  $\eta$; that is why instantaneous recombination is the textbook route to it.
* **It does not identify a mechanism**, only exclude a class: anything whose
  strength varies with $\ell$.
* **One background, one frame.** Planck, CDM. D30 carries three backgrounds
  and both frames on the same object and agrees.

## Provenance

Diagnostic **D30**; findings **T-128** (the annihilation) and the uniformity
recorded with it. Generated by `scripts/figure_f10_formation_surface.py`; the
accumulation is committed as `outputs/f10-formation-surface.csv`, stamped with
a digest of the code that produced it, and `--replot` refuses to redraw
numbers this tree did not compute (**T-54**, **T-129**).
