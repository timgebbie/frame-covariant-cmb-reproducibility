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

## 5. The external review of 2026-10-10, and what it says about §2

**Merged from P1-T, 2026-10-12, before the archived DOI goes live.** A
first-principles review of the submitted v1.0.0, written **without access to
this project's working notes**, was supplied by the PI. It is the strongest
check the manuscript has had, because it is the first one that did not share the
manuscript's own assumptions.

### What it confirmed independently

Reported first, because the confirmations constrain what the objections can
mean. Working from the text alone it reproduced the Liouville/PSTF construction;
the $+(\ell+2)$ sign of the $\ell-2$ shear coupling, against the legacy
misprint; the five acceleration and shear coefficient sums **in exact rational
arithmetic for $\ell=4,\dots,300$**; the scalar connection calculation; the
Gauss embedding relation; and App. C's three coefficients
$\tfrac3{16},\tfrac{17}{16},1$, evaluated independently. Those are the
load-bearing pieces, and they held.

### Ten corrections, and seven of them were this project's own

Each was re-derived or machine-checked by P1-T before being applied; none was
taken on the review's word. Items 1 and 2 were **carried from the legacy**
papers. Items 3–10 were **introduced in this project's own sessions** — among
them a drift from conventions row **C3.1** on whether $k$ is physical (item 3),
a harmonic-reduction error where contraction weights were read as holding on the
harmonics (item 4, the most consequential, disproved by a symbolic
counterexample at $Q=\cos kz$), and an App. E equation written the previous day
about an object the tensor sector does not admit (item 5).

**That ratio is the finding, and it is a finding about §2 of this record.** The
audits described above were run by agents reading the same manuscript under the
same conventions, and **they found none of items 3–10**. A reviewer who did not
share the frame found seven in a day.

> **An audit that imports the manuscript's own conventions cannot test those
> conventions.** It can still find real errors inside them — A1 was a genuine
> sign-and-$\ell$-weight error that nothing else caught — but its silence is not
> evidence.

Three further clarifications were **declined rather than missed**, all
statements of scope: the ray-orientation sentence in Sec. V B, the framing of
the stencil comparison in Sec. VI F, and naming the three senses of invariance
used in Sec. VI A. **O1 and O2 of §3 are untouched by the review** and ship
unchanged.

### What this bundle does about item 3, stated because it is not a boast

Item 3 is the $k$-is-physical drift from C3.1, and it is the one correction that
names a convention this bundle also depends on: C3.1 declares the sheet's $k$
physical with $k_{\rm phys}=k/a$, while *Annals II* Appendix F's $k$ is comoving.
The bundle guards it by **naming** — `k_com` and `k_phys` as distinct symbols and
never a bare `k`, recorded in the corrections record and enforced by reading
rather than by a gate.

**It was broken here too.** `functions/frames.py`, written 2026-10-09 for the
frame transformation, took a bare `k` in three signatures; it was found on
2026-10-12 while merging this section and corrected the same day. The guard
worked only because someone went looking, which is the same lesson as the
paragraph above: the discipline that catches a convention drift is a reader who
does not already know the convention.
