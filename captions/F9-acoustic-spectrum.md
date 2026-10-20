+++
id = "F9"
order = 9
title = "The angular spectrum with the acoustic peaks, in both frames"
script = "scripts/figure_f9_acoustic_spectrum.py"
artefact = "figures/f9-acoustic-spectrum-v1.2.0.pdf"
category = "acceptance"
caption = """
\\textbf{The release's deliverable} (decision~S1): the angular power spectrum
for the three backgrounds this bundle ships --- CDM (Einstein--de Sitter),
$\\Lambda$CDM, and the stamped Planck~2018 set with a photon-only radiation era
whose $\\Omega_\\gamma h^2$ is \\emph{derived} from $T_{\\rm CMB}$. Shape,
$D_\\ell$ renormalised at $\\ell=30$, because neither this bundle nor the
external codes fixes $A_s$ the same way and an amplitude comparison would
measure a normalisation.\\\\[2pt]
\\textbf{Panel (a) --- the spectrum.} The peaks and the damping tail come from
\\emph{Annals~II}'s own equations: the integral solution~(102) with the
Bond--Efstathiou transfer function driving the oscillation per mode, and the
diffusion scale from \\textbf{(dif-damp-correct)} at $f_2=3/4$, which is the
antecedent's own corrected coefficient rather than a departure from it
(\\textbf{T-43}). \\textbf{This shows that} the almost-Friedmann--Lemaitre
formulation, carried to the damping scale, produces acoustic structure without
anything being imported from a Boltzmann code.\\\\[2pt]
\\textbf{CAMB and CLASS are drawn as context and are not a target} ---
decision~\\textbf{S4c}. Criterion~5b is gated on this bundle's own pipeline,
(102) against (177)--(179), at $9.5\\times10^{-6}$ against $10^{-3}$. The
distance to the external codes is large, expected, and \\emph{itemised rather
than totalled} in \\texttt{provenance/CRITERION-5B-v1.md}: $97.8\\%$ across the
plateau, $137\\%$ across the peaks, of which the damping coefficient alone is
$17.2\\%$. The first peak is quoted from a \\emph{parabolic interpolation}
through the grid maximum and its neighbours, because the $\\ell$ grid steps by
30 across the acoustic band and reading the peak off it directly would assert a
precision the sampling does not have.\\\\[2pt]
\\textbf{Panel (b) --- the panel a gauge-fixed treatment cannot draw.} The same
spectra in \\emph{both} frames, from \\emph{one} solve: \\texttt{coefficient\\_sets}
returns the Newtonian and CDM triples together, because~(102) is carried with a
generic $u^a$ and the frame is chosen at the end. \\textbf{This shows that} the
frame is a choice made after the derivation rather than an assumption built
into its start --- the claim the $1+3$ covariant approach exists to make, drawn
here rather than asserted. The median frame gap reaches $40\\%$, which is a
\\emph{result} and not a defect: $C_\\ell$ is quadratic in frame-dependent
pieces, while the invariance~(102) satisfies is a statement about the total at
fixed $k$, measured separately by~D6.\\\\[2pt]
\\textbf{Superseded 2026-10-20, findings T-57, T-59 and T-85.} The number above is the figure's, and the figure predates \\textbf{T-57}. \\textbf{The frame disagreement is no longer read as a result.} It is \\emph{total} --- median $9.99\\times10^{-1}$, worst $1.00$ --- and the $\\ell\\ge2$ multipoles are frame-invariant \\emph{by theorem}, so a gap there is a defect and is being hunted. It is localised: the rank-1 source agrees between the columns to $10^{-15}$ (\\textbf{T-82}) and the by-parts identity holds in both (\\textbf{T-85}), so the whole of it is the slot-and-weight assignment of $C_1$ (\\textbf{T-86}). \\texttt{provenance/BUNDLE-DEFECTS-v1.md} is authoritative; this caption is not regenerated until the figure is.
"""
+++
