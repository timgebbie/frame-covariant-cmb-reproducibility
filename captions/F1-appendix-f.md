+++
id = "F1"
order = 1
title = "The covariant free-streaming recursion against four external hierarchies"
script = "scripts/figure_f1_appendix_f.py"
artefact = "figures/f1-appendix-f-v1.0.0.pdf"
category = "cross-check"
caption = """
The covariant free-streaming recursion of \\emph{Annals~II} Appendix~F, integrated
from a unit monopole, against four external treatments of the same hierarchy.
Each is transcribed from its own paper, never through Appendix~F.
\\textbf{Upper panels, context:} the reconstruction and the external form at
$\\ell=5$; they coincide. The panels do \\emph{not} share a vertical scale, because
two normalisations are on display. \\textbf{Lower panels, the claim:}
$\\max_\\eta|\\mathrm{external}-\\mathrm{reconstruction}|$ against $\\ell$, with the
acceptance threshold marked. Hu \\& Sugiyama write the recursion in the $\\beta$
normalisation and Ma \\& Bertschinger and Seljak \\& Zaldarriaga in the $\\alpha$
normalisation, which is why Appendix~F prints both (F.3) and (F.4); a basis phase
leaking into the couplings would break at least one match. Overall scale is
exactly $1.000000000$ --- nothing is fitted. Three panels, not four: Wilson is
pre-arXiv and the citation is ambiguous.
"""
+++

# F1 — The covariant free-streaming recursion against four external hierarchies

**Script:** `scripts/figure_f1_appendix_f.py`
**Artefacts:** `figures/f1-appendix-f-v1.0.0.pdf`, `figures/f1-appendix-f-v1.0.0.png`
**Data:** `outputs/f1-appendix-f-residuals.csv`
**Evidence category:** cross-check. **This is where the bundle's independence lives.**

---

The covariant free-streaming recursion of Annals II Appendix F, pp. 379–380,
integrated from a unit monopole and compared with four external treatments of
the same hierarchy. Each external hierarchy is transcribed in
`functions/harmonics/external.py` from its own paper, never through Appendix F: a
coefficient read through Appendix F would be the same source as Appendix F, and
independent checks are counted by their sources rather than by their arguments.

**Upper panels, context.** The reconstruction and the external form at multipole
$\ell=5$. They coincide. The three panels do **not** share a vertical scale,
because two different normalisations are on display and sharing the axis would
flatten two of them to make a point the figure is not making.

**Lower panels, the claim.** The residual across the hierarchy,
$\max_\eta|{\rm external}-{\rm reconstruction}|$ against $\ell$, log scale, with
the acceptance threshold marked.

| Source, as printed | Weights | Appendix F form | max residual, $\ell\le25$ |
|---|---|---|---|
| Hu & Sugiyama, *Phys. Rev. D* **51** (1995), 2599, Eq. (6) | $\ell/(2\ell-1)$, $(\ell+1)/(2\ell+3)$ | (F.3), $\beta$ | $1.2\times10^{-13}$ |
| Wilson, *Astrophys. J.* **273** (1983), 2, Eq. (8) | $\ell/(2\ell-1)$, $(\ell+1)/(2\ell+3)$ | (F.3), $\beta$ | $3.1\times10^{-14}$ |
| Ma & Bertschinger, *Astrophys. J.* **455** (1995), 7, Eqs. (49), (50) | $\ell/(2\ell+1)$, $(\ell+1)/(2\ell+1)$ | (F.4), $\alpha$ | $1.3\times10^{-14}$ |
| Seljak & Zaldarriaga, *Astrophys. J.* **469** (1996), 437, Eq. (3d) | $\ell/(2\ell+1)$, $(\ell+1)/(2\ell+1)$ | (F.4), $\alpha$ | $1.3\times10^{-14}$ |

**Two distinct normalisations and two distinct phase conventions.** Hu &
Sugiyama and Wilson write the recursion in the $\beta$ variable; Ma &
Bertschinger and Seljak & Zaldarriaga write it in the $\alpha$ variable.

Wilson is the strongest panel, and not because of his weights, which are Hu &
Sugiyama's. He writes the recursion in the **imaginary** convention — both
bracket terms positive under an overall $-ikT$ — where the others carry opposite
signs under a real $k$. The two are related by $\Theta_\ell=i^\ell\delta_\ell$,
exactly. He is integrated complex and as printed, and the phase removed only
afterwards; transforming the equation first would assume the identity under test.
That the transformed solution is *real* to $10^{-10}$ is asserted separately from
that it agrees. His panel therefore tests the phase convention — the subject of
finding B-1 and acceptance criterion 3 — from a source published before any of
the others. Appendix F prints both (F.3) and (F.4) for exactly that
reason. A basis phase leaking into the coupling coefficients would break at least
one of the two matches, which is what makes this a representation-free test of
the harmonic normalisation.

**Overall scale is exactly 1.000000000.** The monopole normalisation is common to
all four and nothing is fitted.

**Three panels, not four.** Wilson is not reproduced: the paper is pre-arXiv, and
Appendix F's citation names Wilson & Silk while its key points to Wilson —
see `provenance/`, finding **B-4**. Quoting Eq. (7) through Appendix F would make
it the same source as Appendix F rather than an independent fourth.

Thomson scattering terms, $-\dot\tau\Theta_\ell$ in Hu & Sugiyama and
$-\dot\kappa\Delta_{T\ell}$ in Seljak & Zaldarriaga, are dropped: they are not
free streaming.

†1 The comparison with (F.4) applies the $(2\ell+1)^{-1}$ division that the text
preceding it specifies and its display omits. A misprint; see `provenance/`,
finding **B-2**.
