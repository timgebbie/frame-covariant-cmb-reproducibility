# Accepted decisions — v1.0.0

**What has been agreed, and is therefore not reopened without a new decision.**
Everything here was accepted by the PI. A later reading of a source may *sharpen*
one of these; it does not silently overturn one. If a source contradicts an entry,
the contradiction is recorded and raised, and the entry stands until changed here.

Open questions live in `OPEN-QUESTIONS-v1.0.0.md`; findings against the antecedent
live in `ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md`. This file is neither: it is
the record of what *we* decided.

Last amended 2026-10-05.

---

## S — Scope and staging

| | Decision |
|---|---|
| **S1** | **v1.0.0 covers everything in Annals I, Annals II and the supporting literature**, with errors, typos and physics corrected in light of what the preprint correction established. The deliverable is the **CDM and ΛCDM angular power spectra in the almost-Friedmann–Lemaître formulation**: Eq. (186) computed from Eq. (176), by the mode route and by the covariant route of Eqs. (187) and (188). |
| **S2** | **v1.5.0 is the high-$\ell$ $O(\varepsilon^2\ell)$ effects, and it carries BOTH nonlinear corrections** — the gravitational coupling to the kinematic quantities, $\delta\dot\tau_{NL}$, and the nonlinear Thomson scattering coupling to the baryon velocity, $\dot{\delta C}_{NL}$. Both are named in thesis Chapters 2 and 6; see the thesis-abstract entry below for the displayed forms. It is **gated on Paper 1**, which P1-T is writing. It also carries the $\pm(\ell+2)$ control, where that term exists, and the restricted case as a recovery and check of v1.0.0. *Accepted 2026-10-05.* |
| **S3** | **v2.0.0 is calibration and data science**, including Planck. *Calibration* means calibrating the solver against standard results, never calibrating the amplitude of an effect. |
| **S4** | **This is a Boltzmann code written from scratch.** The only external code it is checked against is **CMBFAST** — nothing else, deliberately, to avoid scope creep. |
| **S5** | This stream's remit is **v1.0.0 and v1.5.0**. |
| **S6** | The bundle is a **separate repository**, publishable and DOI-able from the start. Publisher PDFs are never carried into it. |
| **S7** | Both CDM and ΛCDM are wanted **in the almost-FLRW setting at v1.0.0**, so that the high-$\ell$ extension at v1.5.0 is a clean delta rather than a change of model. |

## A — Acceptance criteria

v1.0.0 is complete when all hold, and not before.

| | Criterion | Status |
|---|---|---|
| **1** | the free-streaming recursion reproduces (F.1)–(F.4), external matches checked numerically | **closed** |
| **2** | covariant → mode → covariant round trip returns the input to machine precision | open |
| **3** | both harmonic phase conventions run end to end; only one reproduces the real, opposite-sign form of the external hierarchies, and the bundle adopts and names that one | **closed** |
| **4** | a known-wrong control runs and fails in a known shape | **closed** |
| **5a** | the Sachs–Wolfe limit is recovered over $2\le\ell\le20$ to 5% | open; range derived |
| **5b** | the CDM and ΛCDM angular power spectra are recovered to a stated tolerance over a stated range, checked against **CMBFAST** | open; tolerance and range to be set |
| **6** | every number the paper prints is regenerated here, or marked not-machine-checkable with the reason | open; closes at manuscript freeze |

## L — Language and voice

| | Decision |
|---|---|
| **L1** | **Corrections are silent**, marked by **one succinct footnote**. The word is *misprint*, not *error*. The forensics stay in `provenance/`. |
| **L2** | A finding that would move a sign, an $\ell$-weight or an acceptance criterion is **raised**, not footnoted. |
| **L3** | Equation numbers are **published** numbers. Where an edition differs, the difference is recorded; where it does not, that is recorded too. |
| **L4** | **The bundle reproduces; it does not argue.** No claim appears here that is not in the paper. |
| **L5** | **Independent checks are counted by their sources, not by their arguments.** A coefficient transcribed through a secondary source is that secondary source. |
| **L6** | **Be faithful to the $1+3$ approach wherever possible.** Carry a generic $u^a$; specialise to an explicit frame at the end, never at the start. |
| **L7** | Criterion 3's agreed wording, verbatim: *"Both harmonic phase conventions run end to end; only one reproduces the real, opposite-sign form of the external hierarchies, and the bundle adopts and names that one. Separately, the covariant multipole is shown invariant under the choice, so the two statements are not conflated again."* |
| **L8** | A succinct **disclosure of AI assistance** is carried under *Verification status*; the provenance record carries the detail. |

## V — Visual grammar

| | Decision |
|---|---|
| **V1** | Figures are **print artefacts**: matplotlib to versioned PDF/PNG pairs. The web interaction layer of the house standard is dropped; everything else applies. |
| **V2** | **Plot multipole mean-squares, never mode mean-squares.** The former hold for general geometries (*Annals II* p. 366); the latter also carry the harmonic phase convention. |
| **V3** | **Every figure names its frame.** Any quantity not invariant under a change of threading is labelled with the frame it was computed in. |
| **V4** | **One axis. Never a dual y-axis.** Two measures of different scale are two panels. |
| **V5** | Legend present for $\ge2$ series; $\le4$ series are also direct-labelled, so identity is never colour alone. |
| **V6** | Text in ink, never in the series colour. |
| **V7** | Four categorical slots, **re-validated against the house surfaces** rather than inherited. Slots 3 and 4 fall below 3:1 on the light surface, so the direct-label relief rule binds. |
| **V8** | **Never more than three hues where all pairs must separate at once.** Yellow against orange fails the all-pairs floors. |
| **V9** | **A total is not a peer of its components**: parts take slots 1–3, the sum is primary ink and heavier. |
| **V10** | Diverging pair for a **single** signed series about zero; **categorical** slots with a zero rule for several *identified* signed series. |
| **V11** | **Ordered families are sequential**, not categorical — a single hue ramp, validated for lightness monotonicity. |
| **V12** | **Every figure is rendered and looked at** before its caption is signed off. The validator checks colour, not layout. |
| **V13** | Where a figure depends on a corrected expression, its caption carries **one** footnote naming the printed equation and pointing to `provenance/`. |
| **V14** | **A control is not evidence.** Controls live in `diagnostics/`, never in `figures/`, and do not enter the supplement. |
| **V15** | Each caption is **standalone** in `captions/` and names the script that produced the figure. The caption is the specification, not a description. |

## D — Documents and structure

| | Decision |
|---|---|
| **D1** | README and supplement **conform to the house exemplar's structure** — heading set, order and wording — with different physics in the same frame. |
| **D2** | The supplement is **authored by Tim Gebbie**, Department of Statistical Sciences, UCT. |
| **D3** | The **audit tables are generated** from `config/implementation-register.toml`; `tests/test_register.py` resolves every module, object and test named in them, so they cannot drift from the code. |
| **D4** | Figures enter the supplement **automatically once generated**, from the caption front matter; what is outstanding is stated rather than omitted. |
| **D5** | **The key figure for v1.0.0 is the recovered angular power spectrum with its residual panel** — the recovery of *Annals II*'s physics. F1 leads only until it exists. F1 carries the *independence*; the spectrum figure carries the *recovery*, and its target descends from the same antecedent. |

## R — Release and archive

| | Decision |
|---|---|
| **R1** | **Option 5a staging**: `v1.0.0-rc` is tagged when the criteria other than 6 close; `v1.0.0` is the release at manuscript freeze, with all of them. No release claims a done-condition it has not met. |
| **R2** | DOI **`10.25375/uct.34069509`**, reserved on ZivaHub against a private draft, licence **MIT**, item type Software. It is the **concept** DOI and is the one to cite. |
| **R3** | Code **MIT**; supplement, text, captions, figures and tables **CC BY 4.0**; the paper keeps its own terms. |
| **R4** | Two manifests guard the tree, and the corrections record is **append-guarded** rather than frozen: appending is permitted, rewriting recorded bytes is not. |
| **R5** | Development is in the cloud; the working tree is written to the PI's disk and **the PI owns git**. |

---

## Still awaiting a decision

| | Question |
|---|---|
| **Q4** | Wilson — pre-arXiv, and Appendix F names Wilson & Silk while keying Wilson. On hold; the release states three external hierarchies, not four. |
| **Q6** | Criterion 5b's tolerance and range. The external target is settled (**CMBFAST**); the numbers are not. |
| — | Dark-mode figure variants: proposed as *generated only when a screen deliverable exists*. Unanswered. |
| — | An `algorithm-layout-v1.0.0.tex` to match the exemplar's preamble line for line. Offered, unanswered. |
| — | Paper 1's **title** and **arXiv identifier**, placeholders in the README and `CITATION.cff`. |

---

## Evidence from the thesis chapter abstracts — proposed sharpening, 2026-10-05

**Not yet accepted. Recorded for the PI's confirmation.** The thesis opens each
chapter with an abstract-style block carrying that chapter's key equation. Read
from `sources/TGEBBIE-PHD-001.zip`. Nothing in S1–S7 is changed by this entry;
the proposal is to make them more precise.

Chapter files do not match chapter numbers; the include order is ONE, TWO, FIVE,
THREE, FOUR, SIX.

| Thesis chapter | File | Published as | Key equation in its abstract |
|---|---|---|---|
| 1 Algebraic relations | `CHAPTER-ONE` | **Annals I** | $C_\ell=\frac{2}{\pi}\frac{\beta_\ell^2}{(2\ell+1)^2}\int\frac{dk}{k}k^3|\tau_\ell|^2$ **and** $\langle\tau_{A_\ell}\tau^{A_\ell}\rangle=(2\ell+1)\Delta_\ell^{-1}C_\ell$ |
| 2 Temperature anisotropies | `CHAPTER-TWO` | **MGE99** | the exact IBE, $-[\dot\Pi+e^a\mathrm{D}_a\Pi]=4\mathcal{D}\Pi+K$ |
| 3 Sachs–Wolfe and kinetic theory | `CHAPTER-FIVE` | — | $T(x_0,e)=T(x_0)\exp[-\int\mathcal{D}E\,dv]$ — the nullcone/timelike link |
| 4 COBE–Copernican limits | `CHAPTER-THREE` | — | almost-EGS bounds. **Not this stream** — stream G, Paper 1b |
| 5 Scalar almost-FLRW | `CHAPTER-FOUR` | **Annals II** | $\tau_{A_\ell}(x_0)$ as the three-source projection — Eq. (176) in multipole form |
| 6 Scalar nonlinear corrections | `CHAPTER-SIX` | astro-ph/9912072 | $\delta\dot\tau_{NL}$ **and** $\dot{\delta C}_{NL}$ |

### What this fixes

**Chapter 1's abstract is exactly the v1.0.0 target.** It states (186) and the
inverse of (188) side by side as *the* result of the chapter — confirming that
the identity between the two routes, which this bundle now proves as a test, is
the chapter's own headline rather than an incidental relation.

**Chapter 5's abstract gives (176) in multipole form**, with the
$(2\ell+1)\beta_\ell^{-1}$ factor explicit, and ends by naming the chapter's
purpose: *"clarifying the connection between the more usual approaches (for
example that of Hu-Sugiyama) and the CGI treatment for scalar perturbations (for
example the alternative scalar covariant treatment of Challinor-Lasenby)."*
**Proposal, revised 2026-10-05 after the PI corrected it — see the note on
attribution below.** The supporting literature of S1 is **Hu & Sugiyama**, which
is the treatment the formulation was developed from and checked against.
**Challinor & Lasenby is contemporaneous and independent** and is used only for
convention translation, not as an antecedent. Wilson & Silk is the
mode-representation antecedent named by Chapter 1.

**Chapter 6 carries TWO nonlinear corrections, not one.** The gravitational
coupling to the kinematic quantities,

$$\delta\dot\tau_{NL}\approx-\ell\,O_{A_\ell}\Big[\tfrac14\sigma_{bc}\tau^{bcA_\ell}
+\sigma^{\langle a_\ell a_{\ell-1}}\tau^{A_{\ell-2}\rangle}
-\big(A^{\langle a_\ell}\tau^{A_{\ell-1}\rangle}-\tfrac12 A_b\tau^{bA_\ell}\big)\Big],$$

**and a nonlinear Thomson scattering coupling to the baryon velocity,**

$$\dot{\delta C}_{NL}\approx+\sigma_T n_e O_{A_\ell}\Big[\tau^{\langle A_{\ell-1}}
v_B^{a_\ell\rangle}+\tfrac12\tau^{A_\ell a}v^B_a\Big].$$

Chapter 2's abstract names both: *"a coupling between the radiation multipole and
the baryonic velocity via nonlinear Thomson scattering and a gravitational
coupling between the radiation multipoles and the kinematic quantities."*
**ACCEPTED 2026-10-05: S2 names both.** This stream had been tracking only the
gravitational one.

**Chapter 6's cancellation claim is frame-dependent in the source itself**:
*"gravitational nonlinearity ... leads to cancellation on small-scales when
threading in the Newtonian frame. Generically this cancellation does not occur,
it is unique to the shear free threading."* That is the same frame-dependence the
two-frame figures are built to show, stated by the antecedent.

### Supporting evidence toward G4, not a resolution

Chapter 1's abstract says the angular correlation functions are found *"following
the Wilson-Silk approach for the mode representation, but derived and dealt with
in 1+3 covariant and gauge invariant (CGI) form."* That the mode-representation
antecedent is **Wilson & Silk** supports reading Appendix F's `[81]` as a typo for
`[82]`. It is supporting evidence, not a verification: resolving G4 still needs
Eq. (7) of the paper itself. **G4 stays open.**

---

## Attribution — how the related work is positioned, and what is not said

**Recorded 2026-10-05 on the PI's account.** This entry exists so that a later
session does not write something that misstates the lineage. It governs
*language*; it changes no physics and makes no claim in any released artefact.

### What the bundle says

| Work | How it is positioned | Why |
|---|---|---|
| **Hu & Sugiyama** | the treatment this formulation was **developed from and checked against** | the PI's own account, and demonstrable: the acceptance spine matches their Eq. (6) directly, in the $\beta$ normalisation |
| **Challinor & Lasenby** | a **contemporaneous and independent** covariant treatment | used in this project only for **convention translation** — it works in the opposite signature, and the conventions sheet carries a row mapping to it |
| **Wilson & Silk** | the **mode-representation antecedent**, named as such by thesis Chapter 1 | and the subject of finding **G4** |
| **Ellis, Treciokas & Matravers (1983)** | the PSTF lineage the covariant treatment rests on | GE98, MGE99 and the thesis all cite it for the same lemmas, so they are one source |

### What the bundle does not say

**No priority claim appears in any released artefact.** The bundle reproduces; it
does not argue (**L4**), and the project's voice rule is that the work corrects
quietly and does not dig up skeletons. A priority dispute is the clearest possible
case of something that belongs outside a reproducibility bundle: it cannot be
settled by running code, and asserting it would undercut the one thing the bundle
is for.

**Equally, the bundle must not imply the reverse.** The $1+3$ covariant line here
runs Ellis–Treciokas–Matravers $\to$ GE98 and MGE99 $\to$ Annals I and II. It does
**not** derive from Challinor & Lasenby, and no wording should suggest that it
responds to or follows from that treatment. *Annals II*'s own abstract speaks of
clarifying the connection to it; this bundle neither contradicts nor amplifies
that sentence.

The accurate and sufficient statement is that the two covariant treatments are
contemporaneous and independent. That is what is written, and nothing further.

### Polarisation

**Polarisation is out of scope for v1.0.0 and v1.5.0.** If it is ever taken up,
**Challinor & Lasenby is the prior work** and must be cited as such. Recorded here
so that the question is already answered before anyone reaches it.
