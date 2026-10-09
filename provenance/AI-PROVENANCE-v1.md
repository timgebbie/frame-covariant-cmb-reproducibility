<!--
GENERATED HANDOVER. Source: docs/streams/stream-P1T-ai-provenance.md in the
project repository, received from P1-T 2026-10-09 and placed here unaltered
below this header.

**This file is what Paper 1's Disclosure of AI assistance points at.** The
disclosure is four sentences and says the detail is recorded here; if this file
is absent the disclosure cites a record that does not exist, which is worse
than a long disclosure.

It is listed in `provenance/README.md` under the T/B/A/L/S prefix scheme as a
record of its own kind: it is not a finding against the antecedent, not a
defect in this bundle, and not a decision. It is an account of how the paper
was made and what was checked about it.

Two things in it are worth a reader's attention before the table of findings.
Section 3 carries **two items left open on the PI's recorded decision**, and
says in terms that neither is a known error. Section 4 states what the audit
passes did **not** reach. A provenance record that lists only successes is not
one, and this one does not.
-->

# P1-T → bundle `provenance/` — the AI-assistance record, in full

**P1-T, 2026-10-09. PI-directed.** Paper 1's *Disclosure of AI assistance* is
thinned to four sentences and now points here. **This file is the thing it points
at.** It must be in the bundle before the preprint is posted, or the disclosure
cites a record that does not exist.

The preprint now reads, in full:

> A large language model (Claude, Anthropic) was used in preparing this work ---
> in the derivations, in the symbolic checking and in the drafting. What it did,
> and where, is recorded section by section in the reproducibility bundle,
> together with the audits run against it.
>
> All physical arguments, derivations and conclusions have been checked by the
> author, who takes full responsibility for them. The model is not an author and
> does not satisfy authorship criteria. No text was published without author
> review.

Nothing was removed from the claim. The section-by-section detail moved here.

---

## 1. What the model did, by section

This is the list that stood in the preprint until 2026-10-09, kept verbatim in
substance and expanded where the one-line form was compressed.

| Section | Contribution |
|---|---|
| Refs. [Gebbie2000], [GebbieThesis1999], [MaartensGebbieEllis1999] | auditing their algebra against the exact hierarchy |
| **Sec. III F** (`sec:shearsign`) | establishing the sign of the source by transposition; locating the sign misprint in the $\ell-2$ shear coupling and checking it against an independent reduction of the Liouville equation |
| **Sec. III C** (`sec:liouville`) | deriving the redshift--aberration split of Table I and the PSTF reductions behind it |
| **Sec. II F** (`sec:weyl`) | drafting |
| **Secs. II E, VI A** (`sec:threading`, `sec:framegen`) | constructing the frame-covariance argument |
| **Sec. VI D** (`sec:relabel`) | the multipole relabelling that closes it |
| **Sec. IV C** (`sec:pstfreduction`) | deriving the scale-factor weight; re-deriving the coefficient compositions and the $\beta_\ell$ cancellation |
| **Sec. V** (`sec:content`) | the line-of-sight identification of the invariant content with lensing, and the location of its two halves |
| **Sec. V D** (`sec:curvhalf`) | the conformal reduction of the free-streaming term |
| **Tables II and III** | the enumeration behind both |
| **Sec. VII** (`sec:quartic`) | checking symbolically the fourth-order expansion and the remainder |
| **the manuscript** | drafting and structuring, including Sec. VIII, the abstract and the title |

## 2. The audits run against it, and what they found

A derivation produced this way is checked, not trusted. Three audit passes were
run over the manuscript in session, by agents given the file and
`CLAUDE.md` §3b and told to report only defects they could state in index
algebra. **Six findings were confirmed and fixed on 2026-10-09**; they are
recorded because a provenance record that lists only successes is not one.

| | Where | What was wrong | Status |
|---|---|---|---|
| A1 | Sec. VI D, *Why not the chain rule* | The gloss said the missing $Hv^a_\perp$ was supplied by the screen projectors on the $\ell$ multipole indices, each contributing $-\frac13\Theta$. That is $-\ell Hv^a_\perp$: **wrong in sign and carrying a spurious factor of $\ell$**, and it contradicted App. D, which derives the term from the projector difference on the photon's single direction index with coefficient the background redshift rate. App. D was right; the gloss was rewritten to match it | fixed |
| A2 | App. E | The list of statements that hold only in the scalar sector **omitted Sec. V D**, which is the one place the vanishing shear does more than simplify: Eq. (gauss-tf) is exact only in a shear-free threading, and that is what gives $\Phi_C=\Phi_H$. With a tensor shear the same equation carries $-\frac13\Theta\sigma_{ab}$, so $\D_{\la a}\D_{b\ra}(\Phi_C-\Phi_H)=\frac13\Theta\sigma_{ab}$ and the two potentials part at first order. App. E now says so, and says what survives (the operator) and what does not (the identification of the potential, and the equality of the two halves for a point mass) | fixed |
| A3 | Sec. V D, after Eq. (PhiCPhiH) | GDE99 Eq. (49) and EvE98 Eq. (31) were attributed to **C2.5** (Eqs. potentials, a *definition* sourced to GDE99 Eq. 26). They are **C2.6**'s sources, and the same page derives Eq. (49) *from* the first of Eqs. (potentials), so the attribution also reversed the derivation. By App. A's own rule the table is right and the body was the mistake | fixed |
| A4 | `checks/gauss_probe.py` header | Asserted that C2.7 is marked **imported** in the paper. Table IV's caption defines *imported* and then says **no line is of that kind**; C2.7 is a *result*. The only artefact probing C2.7 claimed a provenance class the paper says is empty, for the line $\Phi_C=\Phi_H$ rests on | fixed |
| A5 | Sec. VI F, after Eq. (alignC) | "their high-$\ell$ limits are the $\frac14$ and $\frac1{16}$ of Eq. (legendre)" --- Eq. (legendre) carries $\ell/2$ and $\ell/4$. The $\frac14$ and $\frac1{16}$ are Eq. (modeform)'s, and the $\beta_\ell$ conversion between them is the step the paper is elsewhere at pains to separate | fixed |
| A6 | Sec. VI F, after Eq. (rankpres) | "by two routes that share no input" --- but Eqs. (alignN), (alignC) and (rankpres) all come from the same bracket, by applying Eq. (lamrec) twice. They are **two coefficients of one reduction**, which is what the text now says | fixed |

### What the same passes confirmed

Reported because a negative result from a check is a result. The closed
coefficient system was checked, not spot-checked: all six rows of Table I
reproduce the six coefficients of Eq. (hierarchy-exact); Eqs. (red-A), (red-s),
(red-sT), (red-w) follow from Eq. (eO), and red-w's missing rank-lowering term is
correctly absent; Eq. (abersplit) with $K\to A$ reproduces Eq. (newt-pair), and
Eq. (relabel) is that expression with $A\to v_C$ with the sign chain through
Eq. (slot) correct; Eq. (cdm-triple) is rows 3--5 transposed; Eq. (nl-source)'s
five coefficients are the correct transpositions. Every aligned-limit number
comes out in exact rationals, including the residual
$-1/2\ell^2$ and the opposite-sides approach that Fig. 4 draws. Also clean:
Eq. (curvop), Eq. (factorise), Eq. (gauss-tf), App. B's $3+2(m-2)=2m-1$ count,
App. C's kernel and all three coefficients $\frac3{16},\frac{17}{16},1$, the
$\int\dd^2\ell\,\Delta C_\ell=0$ identity, App. D end to end, and App. F's $d/2$.

## 3. Two items left open, and they are open on purpose

| | Where | What is missing |
|---|---|---|
| **O1** | Eq. (red-s), the rank-$n$ branch | The prefactor $(n+1)/(2n+3)$ is asserted. It matches neither C6.1 nor C6.2, and App. B produces the Eq. (detrace) counting but not this weight. **The answer is not in doubt** --- the Table I entry built on it closes the aligned-limit identity $\frac34+\frac14=1$ through Eq. (lamrec), which does not use Eq. (red-s), so there is an independent check on the result. What is missing is the intermediate step, and under §3b an audit agent's own re-derivation is not a substitute for one in the paper |
| **O2** | Sec. VI D, *The consequence* | "The difference of the two $O(\ep^2\ell)$ sources accordingly integrates along the ray to the difference of the relabellings at its two ends." Differentiating Eq. (relabel) along the ray gives two pieces: the source difference by Eq. (dK), and $v^a_\perp\,\dd(\partial\tau/\partial e^a)/\dd t$, which is $v_\perp\!\cdot\!\nabla_\perp\tau$ by Eq. (dtau) and is itself $O(\ep^2\ell)$. The second must be absorbed by the difference of the free-streaming operators in the two threadings. The step is not given, and the section's *Why not the chain rule* paragraph deliberately declines to supply it |

Neither was fixed, because fixing either means doing the algebra in the paper's
voice and that has not been done. **O2 is the more consequential**: it is a step
in the argument that the threading dependence is an endpoint term.

> **PI decision, 2026-10-09: both ship as stated limits, recorded here.** P1-T's
> recommendation had been to close O2 before submission. The PI's call is that it
> is acceptable open, provided it is in the provenance rather than only in a
> session transcript. It is, above. **Neither item is a known error**: O1's result
> is independently corroborated and only its intermediate step is missing, and O2
> is an unshown step, not a wrong one. A referee who works through Sec. VI D
> carefully may raise O2; the answer is that the second piece is absorbed by the
> difference of the free-streaming operators in the two threadings, and that the
> demonstration is not in this paper.

## 4. Coverage, stated honestly

The passes reached: the closed coefficient system; order bookkeeping; the
asserted-not-shown sweep; Apps. A--F; internal cross-references against
Table IV. They did **not** reach: Sec. I; Sec. II C and the C3/C4 harmonic block
(C3.5, C4.3, C4.4, C4.5 and the Eq. (lower) sign conventions); Sec. IV D's
scale-factor chain; the numerical claims in the figure captions (the $71\%$
within $|z|<b$, the efficiency ratio $2-\chi_s/\chi_*$ --- both of which are
recomputed and asserted by the figure scripts on every run, so they are covered
by a different artefact); Eq. (dCl) against Lewis & Challinor, which is external;
Sec. VIII; Table IV's C8 lines; and the bodies of the check scripts below their
headers.

**An earlier pass was lost twice to session limits.** This record covers the one
that completed.
