+++
id = "F2"
order = 2
title = "What a truncation discards, and what it destroys"
script = "scripts/figure_f2_truncation.py"
artefact = "figures/f2-truncation-v1.2.0.pdf"
category = "cross-check"
caption = """
Appendix~E of \\emph{Annals~II} proves that four consecutive vanishing harmonics
force $\\sigma_{ab}=0$ exactly. This figure makes that quantitative in both
frames, and the two panels answer two different questions that a single
``truncation error'' would blur.\\\\[2pt]
What a truncation \\emph{discards} falls off a per-$k$ cliff at
$\\ell\\simeq k\\thinspace \\Delta\\eta$: above the cliff there is nothing left to keep, and
the tail above $\\ell=600$ is identically zero at every probe mode. What
it \\emph{destroys} has no $\\ell_{\\max}$ in it at all. Setting $\\sigma_{ab}\\to0$
costs $0.03$--$1.3\\%$ out to $\\ell=20$, rises monotonically above
$\\ell=20$, and reaches $33.8\\%$ by $\\ell=600$ --- a cost that grows with the
multipole rather than being bounded by it, which is why a truncation argument
cannot retire the shear.\\\\[2pt]
Footnote~29 (p.~365) is checked and holds: in the Newtonian frame the
cost is \\emph{identically zero}, median and maximum alike, because that frame
has no shear to lose --- which is the content of the footnote's claim that the
Newtonian specialisation removes the truncation problem. The script raises
rather than draws if the Newtonian rank-0/2 sectors are ever non-empty, so the
claim is a gate and not a caption.\\\\[2pt]
The third panel reports a negative result. The
rank-0/2 share is $0.06\\%$ at the quadrupole and $0.03\\%$ at $\\ell=4$, and
rises only with $\\ell$:
a $1+3$ excess at low $\\ell$ would appear here, and does not. That question is
parked as \\textbf{Q5}, and this panel is what parks it honestly.\\\\[2pt]$^{\\dagger}$\\,\\emph{Superseded by finding} \\textbf{T-57}\\emph{; see} \\texttt{provenance/BUNDLE-DEFECTS-v1.md}.
Its $k$ grid runs to 2000, not 420 --- finding \\textbf{T-32}, where
every v1.2.0 figure had been drawn on a grid stopping at the peak of the shear
integrand. At $k_{\\max}=2000$ against $k_D=890.3$ the damping envelope is
$6.5\\times10^{-3}$, and dropping the grid's top decile moves the cost by
$4\\times10^{-11}$. It ran to 1900 until the scattering-rate correction moved
$k_D$ past what 1900 holds, and from then until 18 November 2026 the generator
aborted on its own gate (\\textbf{T-196}). The lesson recorded there is the rule here: vary the limit
and the resolution separately, because one grid number conflates them.
"""
+++
