# Accepted decisions — v1.0.0

**What has been agreed, and is therefore not reopened without a new decision.**
Everything here was accepted by the PI. A later reading of a source may *sharpen*
one of these; it does not silently overturn one. If a source contradicts an entry,
the contradiction is recorded and raised, and the entry stands until changed here.

Open questions live in `OPEN-QUESTIONS-v1.0.0.md`; findings against the antecedent
live in `ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md`. This file is neither: it is
the record of what *we* decided.

Last amended 2026-10-08.

---

## S — Scope and staging

| | Decision |
|---|---|
| **S1** | **v1.0.0 covers everything in Annals I, Annals II and the supporting literature**, with errors, typos and physics corrected in light of what the preprint correction established. The deliverable is the **CDM and ΛCDM angular power spectra in the almost-Friedmann–Lemaître formulation**: Eq. (186) computed from Eq. (176), by the mode route and by the covariant route of Eqs. (187) and (188). |
| **S2** | **v1.5.0 is the high-$\ell$ $O(\varepsilon^2\ell)$ effects, and it carries BOTH nonlinear corrections** — the gravitational coupling to the kinematic quantities, $\delta\dot\tau_{NL}$, and the nonlinear Thomson scattering coupling to the baryon velocity, $\dot{\delta C}_{NL}$. Both are named in thesis Chapters 2 and 6; see the thesis-abstract entry below for the displayed forms. It is **gated on Paper 1**, which P1-T is writing. It also carries the $\pm(\ell+2)$ control, where that term exists, and the restricted case as a recovery and check of v1.0.0. *Accepted 2026-10-05.* |
| **S3** | **v2.0.0 is calibration and data science**, including Planck. *Calibration* means calibrating the solver against standard results, never calibrating the amplitude of an effect. |
| **S4** | **This is a Boltzmann code written from scratch.** The only external code it is checked against is **CMBFAST** — nothing else, deliberately, to avoid scope creep. |
| **S4a** | **Refinement of S4, accepted 2026-10-06.** CMBFAST is the *method* — line-of-sight integration, Seljak & Zaldarriaga, already in Annals II's bibliography — not a runnable code: Fortran 77, unmaintained since the early 2000s. The bundle therefore **cites Seljak & Zaldarriaga for the method and compares against CAMB and CLASS**, saying so explicitly. That is more honest than claiming a comparison against a code nobody can run. CAMB is also the natural choice because Challinor is already mapped in the conventions sheet as `[CL]`. This is not scope creep: it is the same single comparison S4 allowed, pointed at code that exists. |
| **S4b** | **The 5b tolerance is measured, not chosen.** Run CAMB and CLASS and take their mutual difference as the floor: no agreement can be claimed tighter than two trusted independent codes agree with each other. This converts “pick a tolerance” from a judgement into a measurement, which is the form this project keeps finding it wants. Reported in three $\ell$ bands, actual numbers, never the word *agrees*. *Accepted 2026-10-06.* |
| **S16** | **The repository is `frame-covariant-cmb-reproducibility`**, matching the house exemplar's all-lowercase form. The local working directory name is deliberately *not* encoded anywhere in the tree — `scripts/check_portability.py` enforces that — so the directory may be renamed independently and at any time. *Accepted 2026-10-07.* |
| **S19** | **The release sequence is fixed: retag v1.0.0 → submit Paper 1 → go public → then v1.1.0, v1.2.0 and v1.5.0 each public as it lands.** Public-releasing at v1.5.0 instead was considered and rejected, because it is strictly *slower*, not faster: v1.5.0 is gated on Paper 1 (S2) and going public is already gated on Paper 1's submission, so releasing at v1.5.0 only adds v1.1.0 and v1.2.0 to the critical path. It would also put the first public artefact's nonlinear correction on top of a linear spectrum never checked against CAMB or CLASS, which is exactly what S18 exists to prevent. **v1.0.0 is the reproducibility bundle for Paper 1**, and its strongest evidence — F1's five external hierarchies, four independent checks, two normalisations and two phase conventions — is a better first public impression than an extension whose baseline is unvalidated. The concept DOI resolving to latest also assumes a v1.0.0 base. **Not public before Paper 1 is submitted**: `provenance/` would otherwise announce ten corrections to a published paper ahead of the paper that makes them quietly, inverting decision L4's voice rule. *Proposed by P1-B, accepted by the PI 2026-10-09.* |
| **S22** | **Peebles is the default recombination from v1.1.0.** *Accepted by the PI 2026-10-10.* It was deliberately **not** the default on the day the module landed: the roadmap requires it to be "checkable on its own against the standard ionisation history before anything is built on it", so it shipped behind the `Recombination` enum, was checked standalone, and was promoted afterwards with the before-and-after in view. Measured through the visibility on the three backgrounds this bundle uses — CDM (Einstein–de Sitter), ΛCDM, and a realistic $\Omega_r\neq0$ comparison — the peak moves from $z\simeq1300$–$1320$ to $z\simeq1107$–$1131$ against a standard 1080–1100, and the FWHM widens from $\simeq116$–$122$ to $\simeq167$–$199$ against a standard 190–200. **Criterion 5a is unaffected**: D5 reports 0.26% where it reported 0.27%, which is what a shape-normalised large-scale comparison should do. `SAHA` is **kept rather than deleted** — it is the v1.0.0 result, so it is what makes the change measurable instead of merely asserted, and a known-worse alternative that must change the answer is evidence of the kind this project keeps (S12). |
| **S23** | **The generic-$u^a$ hierarchy moves into v1.2.0.** *Proposed by P1-B, accepted by the PI 2026-10-10.* Finding **T-14** established that the source equations (177)–(179) are Newtonian-threading expressions, and the consequence is larger than one figure: **F2, F5 and F7 all wait on the shear-carrying hierarchy**, and so does every $O(\varepsilon^2\ell)$ correction at v1.5.0. Leaving it inside v1.5.0 would have put four artefacts and a release behind an item the roadmap treated as part of something else. Folding it into v1.2.0 is the natural placement rather than merely the earliest: v1.2.0 already has to assemble the full linear source for the acoustic peaks (S18), and assembling it *generically* is the same work done once instead of twice. v1.5.0 then builds its nonlinear corrections on a generic base that already exists, which is also what makes the $\pm(\ell+2)$ control of S2 meaningful. |
| **S21** | **F5 and F7 move again, from v1.1.0 to v1.5.0 (and thence to v1.2.0 by S23), and this time for the real reason — finding T-14.** Building the frame transformation found that **(177)–(179) are Newtonian-threading expressions**, descending from (106), which the corrections record flags in exactly those words. Paper 1 Secs. VI B and VI C give the consequence: the Newtonian threading carries its whole $O(\ell)$ source in the **acceleration pair**, the CDM threading carries its whole source in the **shear pair**, and they are two reductions of one operator differing in which kinematic quantity supplies $K^a$. Setting $\tilde\Phi_A=0$ therefore deletes the coupling that was carrying the source without supplying the one that replaces it — measured, the assembled transfer function moves by a factor of **five** under the visibility weighting and **collapses to two parts in a thousand** under the opacity. **The transformation itself is not in question**: $\tilde\Phi_A=0$ and the Weyl invariant $\Phi_A-\Phi_H$ both hold to $1.1\times10^{-16}$, and `functions/frames.py` proves the rules symbolically with a negative control. What is missing is the **generic-$u^a$ source**, which is v1.5.0's subject by decision **S2** and is not a figure's worth of work. **So S20 deferred the right artefacts for the wrong reason, and this stream has now been wrong about F5 twice in opposite directions** — first that $\Phi_H$'s rule was missing when Paper 1 Sec. VI A supplies it, then that the remaining work was a figure when it is a hierarchy. Both are corrected in the record rather than tidied away, because a bundle that hides its own wrong turns is not reproducible in the way that matters. **What v1.1.0 keeps**: the frame machinery itself, exact and tested, and the measurement that found this. *Taken by P1-B 2026-10-09.* |
| **S20** | **F5 — the source decomposition drawn in two frames — moves to v1.1.0, beside F7.** F5 and F7 are one piece of machinery: both need the frame specialisation made *numerical*, and `"newtonian"` and `"energy"` are today labels on `PerturbationHistory` that nothing reads. Splitting them across releases was always artificial. Three reasons this is the right side of the line and not merely the convenient one. **(i)** What F5 would show numerically, **criterion 2 already establishes symbolically and exactly**: `functions/frames.py::roundtrip_residual()` returns the zero vector as an *identity in $\varepsilon$*, not to a tolerance — $\tilde{\mathcal B}_1=\mathcal B_1+\dot v_a$, no shear and no $Hv$. A plot of a small residual is weaker evidence than a proof that the residual is zero, so deferring F5 removes a picture of the claim, not the claim. **(ii)** The rule F5 needs is the transformation of $\Phi_H$ under a change of threading, which lives in exactly the sector where Paper 1 ships its two declared open items — **O1**'s asserted $(n+1)/(2n+3)$ prefactor and **O2**'s unshown absorption of $v_\perp\!\cdot\!\nabla_\perp\tau$ in Sec. VI D. Numerics resting on an analytic step the paper itself marks as not-shown produce a residual nobody can read: a disagreement could be a code defect, a convention slip, or O2 biting, and the figure cannot tell them apart. Building that three days before a submission is how a bundle acquires a wrong number it then has to defend. **(iii)** Paper 1 does not point at F5 — it points at the conventions sheet, the symbolic checks, the figure scripts, the supplement and the AI-provenance record, and all five are present. `supplementary-materials/figures-v1.0.0.tex` **already** lists F5 among those outstanding at this release candidate, so the shipped supplement was more honest than `scripts/run_all.py`, which still treated F5 as blocking; this decision makes the harness agree with the document it ships beside. **What v1.0.0 must then say plainly, and now does:** the frame-covariance claim is established *symbolically*, and the numerical two-frame decomposition lands at v1.1.0. *Taken by P1-B 2026-10-09, on the PI's delegation of the release call; reversible in one line if the PI would rather F5 were built before release.* <br><br> **CORRECTION, 2026-10-09, opening v1.1.0. Reason (ii) above is wrong, and is kept with this note rather than quietly rewritten.** It claimed the rule F5 needs — $\Phi_H$'s transformation under a change of threading — "lives in exactly the sector where Paper 1 ships its two declared open items". It does not. **Paper 1 Sec. VI A supplies it directly, with a source.** The deflection depends only on $\Phi_A-\Phi_H$, whose trace-free screen-projected Hessian is the electric Weyl tensor, $E_{ab}\approx\frac12\mathrm D_{\langle a}\mathrm D_{b\rangle}(\Phi_A-\Phi_H)$ (GDE99 Eq. (24)); $E_{ab}$ vanishes in the background, so by **Stewart–Walker** it is frame-invariant at first order, and therefore so is $\Phi_A-\Phi_H$. The same passage records GDE99's stronger statement from below its Eq. (35): $\rho$, $p$, $\pi_{ab}$, $E_{ab}$, $H_{ab}$ and every $\tau_{A_\ell}$ with $\ell>1$ are unchanged under $\tilde u_a\simeq u_a+v_a$, **only the dipole moving**, $\tilde\tau_a\approx\tau_a-v_a$ (its Eq. (37)). **O1 and O2 are second-order**, concerning the endpoint argument of Sec. VI D, and have no bearing on this first-order rule. **The decision was right; the reason was not.** F5 was correctly deferred on *timing* — the machinery did not exist and the tree was minutes from being tagged and deposited — but it was deferred behind a scientific justification that overstated the difficulty, because this stream had not read Sec. VI A before writing it. Deferring for a good reason and stating a bad one is still a defect in the record. The rule is now implemented and checked: `functions/frames.py::weyl_invariance_residual` is identically zero, **with a negative control showing it fails for any other rule**, and the dipole and $\ell\ge2$ statements are executable in `boosted_dipole` and `boosted_multipole`. |
| **S18** | **The full linear $C_\ell$ — acoustic peaks, Silk damping and the complete source assembly — lands at v1.2.0, *before* v1.5.0, with Peebles recombination at v1.1.0 ahead of it.** The ordering is forced, not preferred. v1.5.0 is an $O(\varepsilon^2\ell)$ **correction** to the high-$\ell$ spectrum, and a correction is only legible where the thing it corrects is already validated: added to a linear spectrum whose own high-$\ell$ behaviour has never been checked, the correction and the error are the same size and cannot be distinguished. Criterion 5b is what establishes "already validated", and 5b is blocked on recombination — equilibrium Saha places last scattering but decouples too sharply, setting the wrong visibility width, and the visibility width fixes the damping envelope. Hence v1.1.0 (Peebles) → v1.2.0 (peaks, 5b closed against CAMB and CLASS, acoustic sector against Hu \& Sugiyama) → v1.5.0 (nonlinear high-$\ell$) → v2.0.0. **This also protects S3**: v2.0.0 stays calibration and data science with no new physics in it, which it could not be if the peaks were still outstanding. **At v1.2.0 the README's key figure becomes the normalised spectrum with its peaks for CDM and ΛCDM**, and the present F3 moves to second place beside the acoustic-mode figures and their Hu \& Sugiyama checks. *Accepted 2026-10-08, on the PI's question of where the peaks land.* |
| **S17** | **Paper 1's title is fixed: _Frame covariance of CMB lensing in the exact $1+3$ covariant radiation hierarchy_.** The arXiv identifier is assigned on submission and is filled at manuscript freeze with acceptance criterion 6; it is not an outstanding request. *Accepted 2026-10-07.* |
| **S13** | **Findings carry a `B-` prefix, never `G`.** Annals II's Appendix~G equations are (G.1), (G.2), (G.3); findings numbered G1–G7 collided with them in the same sentence. Renumbered **B-1**–**B-7**. Raised by Coordination, 2026-10-06, after this project had already lost time to a `λ` collision. |
| **S14** | **Criterion 2's round trip has a stated target, supplied by Coordination 2026-10-06.** Annals II's source decomposes by rank: $\mathcal B_0=-\tfrac13 D^a\tau_a$, $\mathcal B_1 = D_a\ln T + A_a$, $\mathcal B_2=\sigma_{ab}$. The shear is **rank 2** and feeds $\mathcal B_2$, so $C_0$ and $C_2$ are built from it and $C_1$ is not — which is why $\tilde\sigma_{ab}\approx0$ kills $\tilde C_0$ and $\tilde C_2$ and says nothing about $\tilde C_1$. **$C_1$ does not change form off the Newtonian frame**, so criterion 2 is a *check*, not a rederivation. With $\tilde D_a\ln T\approx D_a\ln T - Hv_a$ and $\tilde A_a\approx A_a+\dot v_a+Hv_a$ the $Hv$ cancels, leaving **$\tilde{\mathcal B}_1=\mathcal B_1+\dot v_a$** — no shear, no $Hv$. Any other result from the generic-$u^a$ construction is a bug in this bundle. |
| **S15** | **An approximation of the source is not a finding against it.** `provenance/SOURCE-APPROXIMATIONS-v1.md` records deliberate narrow choices of the antecedent; `ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` records defects. A finding is corrected; an approximation is **reproduced faithfully when reproducing the source** and departed from only where the source is not the target, with the departure named at the call site and in the caption. *Accepted 2026-10-06, after Coordination corrected this stream on A-1.* |
| **S12** | **A settled finding's switch is kept as a control, not deleted.** B-6's `isw_sign` and the relative-sign control of D1 are known-wrong alternatives that must change the answer; that is evidence of the kind `diagnostics/` exists for, and is cheaper to keep than to rebuild. A control is still not evidence for the result (V-rule), and lives in `diagnostics/`. *Accepted 2026-10-06.* |
| **S11** | **Equation numbers are resolved against the accepted manuscript source, not assumed.** `provenance/EQUATION-NUMBERS-ANNALS-II-v1.md` carries the generated label→number map. An acceptance test anchored to the wrong numbering fails in a way that looks like a physics error; one mis-citation was found and fixed this way. *Accepted 2026-10-06.* |
| **S5** | This stream's remit is **v1.0.0 and v1.5.0**. |
| **S6** | The bundle is a **separate repository**, publishable and DOI-able from the start. Publisher PDFs are never carried into it. |
| **S7** | Both CDM and ΛCDM are wanted **in the almost-FLRW setting at v1.0.0**, so that the high-$\ell$ extension at v1.5.0 is a clean delta rather than a change of model. |
| **S8** | **“CDM” names a model, not a frame, and the two are kept lexically apart.** The CDM *model* is a cosmology; the CDM *frame* is the **total-energy frame** $q_a=0$, the threading in which the cold dark matter is at rest, because CDM is pressureless and geodesic and carries no energy flux of its own. They are independent: the ΛCDM model is computed in the same frame as the CDM model. In code the models are `CDM_MODEL` and `LCDM_MODEL` and the frames are `"energy"` and `"newtonian"`. *Accepted 2026-10-06.* |
| **S9** | **v1.0.0 carries no $O(\ell)$ coupling, and this is asserted rather than promised.** Every coupling in (F.1)–(F.4) and in the external hierarchies is a ratio of linear polynomials and tends to a constant; a v1.5.0 coupling wired in early would acquire a factor of $\ell$ and fail `tests/test_appendix_f_chain.py::test_no_coupling_in_the_v1_hierarchy_grows_with_ell` at large $\ell$. Raised by Coordination, 2026-10-06. |
| **S10** | **v1.0.0 is committed and pushed before v1.5.0 begins**, not held open against it. v1.5.0 is gated on Paper 1; v1.0.0 is not, and the two must not be allowed to block each other. *Accepted 2026-10-06.* |

## A — Acceptance criteria

v1.0.0 is complete when all hold, and not before.

| | Criterion | Status |
|---|---|---|
| **1** | the free-streaming recursion reproduces (F.1)–(F.4), external matches checked numerically | **closed** |
| **2** | covariant → mode → covariant round trip returns the input to machine precision | open |
| **3** | both harmonic phase conventions run end to end; only one reproduces the real, opposite-sign form of the external hierarchies, and the bundle adopts and names that one | **closed** |
| **4** | a known-wrong control runs and fails in a known shape | **closed** |
| **5a** | the Sachs–Wolfe limit is recovered over $2\le\ell\le20$ to 5%, against the **corrected** closed form of (201) — the printed form omits one factor of $\chi$, finding B-5 | open; target settled 2026-10-05 |
| **5b** | the CDM and ΛCDM angular power spectra are recovered to a **measured** tolerance over three stated $\ell$ bands, checked against **CAMB and CLASS** — superseding this row's original wording, per S4a and S4b | open; **closes at v1.2.0** (S18), where the peaks exist to compare and Peebles recombination is in place |
| **6** | every number the paper prints is regenerated here, or marked not-machine-checkable with the reason | open; closes at manuscript freeze |

## L — Language and voice

| | Decision |
|---|---|
| **L1** | **Corrections are silent**, marked by **one succinct footnote**. The word is *misprint*, not *error*. The forensics stay in `provenance/`. |
| **L2** | A finding that would move a sign, an $\ell$-weight or an acceptance criterion is **raised in the record**. **Amended 2026-10-05:** raising it does not block the work. The corrected target is adopted and the correction made silently, with the raise standing in `provenance/` as the account of why the target changed. B-5 is the first case and set the precedent. |
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
| ~~**Q4**~~ | **CLOSED 2026-10-07 at five sources.** Annals II means Wilson (1983) Eq. (8); the key is right and the prose slips in two places (B-4, B-9). Wilson & Silk (1981) Eq. (7) is a genuine fifth source, read from its own page, and at $K=0$ is the same equation — credited, not drawn. |
| ~~**Q6**~~ | **CLOSED 2026-10-09, and it had gone stale in a way worth recording.** The row read "the external target is settled (**CMBFAST**); the numbers are not" — but **S4a had already superseded CMBFAST** with CAMB and CLASS, so the open-questions table was still naming a target the decisions table had retired, and the two halves of this file disagreed. The method is settled by **S4b** (the tolerance is the measured CAMB–CLASS mutual difference, reported in three $\ell$ bands, never the word *agrees*) and the schedule by **S18** (5b closes at v1.2.0, where the peaks exist to compare against). Nothing is awaiting a decision; it is awaiting a release. |
| ~~—~~ | **CLOSED 2026-10-09.** Dark-mode figure variants: not needed at v1.0.0, which has no screen deliverable. The proposal stands for whenever one exists. |
| ~~—~~ | **CLOSED 2026-10-09.** An `algorithm-layout-v1.0.0.tex` matching the exemplar's preamble line for line: not taken up. The exemplar's *visual grammar* is conformed to directly — the lineage table's `Version` / `Established or changed` / `Status in v1.0.0` columns and the supplementary-material link form — which is what the conformity was for. |
| ~~—~~ | **CLOSED 2026-10-09 on the manuscript freeze.** Paper 1's **title** is settled — *Frame covariance of CMB lensing in the exact 1+3 covariant radiation hierarchy* — and is in `README.md` and `CITATION.cff`. The **arXiv identifier** is not a decision: it is assigned at submission, and both files say so in those words rather than carrying a placeholder that looks like an oversight. |

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

### Supporting evidence toward B-4, not a resolution

Chapter 1's abstract says the angular correlation functions are found *"following
the Wilson-Silk approach for the mode representation, but derived and dealt with
in 1+3 covariant and gauge invariant (CGI) form."* That the mode-representation
antecedent is **Wilson & Silk** supports reading Appendix F's `[81]` as a typo for
`[82]`. It is supporting evidence, not a verification: resolving B-4 still needs
Eq. (7) of the paper itself. **B-4 stays open.**

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
| **Wilson & Silk** | the **mode-representation antecedent**, named as such by thesis Chapter 1 | and the subject of finding **B-4** |
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
