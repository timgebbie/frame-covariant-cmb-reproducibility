# Open specification questions — v1.0.0

Items where the stream brief and the sources do not yet agree, raised before code
was written rather than resolved in flight. **v1.0.0 does not close until each
is settled by the issuing stream.**

---

## Q1 — criterion 3's wording — **REOPENED 2026-10-06**

**Brief §3, criterion 3** asks that both harmonic phase conventions run and that
**only one** be self-consistent.

**This stream first reported that the criterion could not hold, and that was
wrong.** The error was to apply the cancellation argument of brief §4 — finding
**B-1** — to the mode coefficients. It is a statement about the covariant
multipole. Both statements are true, about different objects, and conflating
them is the likeliest reason the same question has returned three different
verdicts from three careful passes.

Under $Q_{A_\ell}\to\lambda^\ell Q_{A_\ell}$, $\tau_\ell\to\lambda^{-\ell}
\tau_\ell$:

- the **covariant** multipole $\tau_{A_\ell}=\sum_k\tau_\ell Q_{A_\ell}$ is
  **invariant** — the slip never produced a wrong result, which is B-1; but
- the **mode** bracket of (F.1) is **not**. Its raising and lowering terms
  acquire $\lambda^{-1}$ and $\lambda^{+1}$, so their relative coefficient
  carries $\lambda^{-2}$ and **the relative sign flips whenever
  $c^2=-1$**. The two candidate normalisations — $(-k)^{-\ell}
  \mathrm{D}_{\langle A_\ell\rangle}Q$ and $(+ik)^{-\ell}\mathrm{D}_{\langle
  A_\ell\rangle}Q$ — differ by exactly $\lambda=i$, so they fall on opposite
  sides of that flip. A real $\lambda$ keeps the printed opposite-sign bracket; an
  imaginary one gives a same-sign bracket with an overall factor $\mp i$.

**Consequence: the Appendix F chain is the discriminator the project has been
looking for.** Hu & Sugiyama, Wilson & Silk Eq. (7), Ma & Bertschinger
Eqs. (49)/(50) and Seljak & Zaldarriaga Eq. (3d) all print **real** coefficients
of **opposite** relative sign. Only $\lambda^2=+1$ reproduces that, and the match
imports no basis — it compares coefficient structure. Criterion 3 is therefore
achievable at v1.0.0, and it is achieved by the spine the brief already
specifies.

**Proposed restatement, wording only.** Replace *"only one is self-consistent"*
with *"only one reproduces the real, opposite-sign form of the four external
hierarchies"*. Both conventions are internally consistent; the discrimination
comes from outside, which is what makes it count under the rule that independent
checks are counted by their sources.

Both facts are asserted executably in `tests/test_appendix_f_chain.py`.

**Agreed wording, adopted.**

> Both harmonic phase conventions run end to end; only one reproduces the real,
> opposite-sign form of the external hierarchies, and the bundle adopts and names
> that one. Separately, the covariant multipole is shown invariant under the
> choice, so the two statements are not conflated again.

**Status: closed.**

---

## Q2 — the $\pm(\ell+2)$ control — **WITHDRAWN 2026-10-05**

**Decided with the PI: the control is withdrawn from v1.0.0 and replaced.**

The reason is the one the question raised: Annals II, Appendix E, p. 378 states
that $F_{A_\ell}$ and $\sigma_{ab}$ are each at most $O(\varepsilon)$, so the shear
coupling $\sigma^{bc}\tau_{bcA_\ell}$ is $O(\varepsilon^2)$ and is absent from the
almost-Friedmann–Lemaître hierarchy at general $\ell$ — which is why (F.1)
carries no shear term at all. A control built on it would exercise a term this
release does not contain, and settling anything at $\ell=2$ alone is the
specialisation the index-algebra rule forbids.

**Replacement: D1, a relative-sign control on the free-streaming bracket.** The
bracket is run with its relative sign flipped — the $c^2=-1$ case of Q1 —
which is in v1.0.0's physics and which exercises the convention question that is
actually live. It is a wiring check, so it lives in `diagnostics/` and is not a
released figure: a control is not evidence.

The $\pm(\ell+2)$ control moves to **v1.5.0**, where the term it exercises exists.

**Status: closed.**

---

## Q3 — figure F3's comparison target, and the tolerance's $\ell$ range — **CLOSED 2026-10-05**

**Brief §3, criterion 5** asks that the almost-Friedmann–Lemaître temperature
spectrum of Annals II be recovered to a stated tolerance.

**What the source contains.** Annals II has **no figures and no tables**: 74
pages, four embedded images, all page furniture or equation strips. Its §8
derives the angular power spectrum in **closed form** (around Eqs. (196) and
(201)), on large scales, with the transfer function set to unity in places. There
is no published curve to overlay.

**Consequence, now recorded in the README.** Evaluating Annals II's own formula
and comparing it to a reconstruction derived from Annals II's own hierarchy is a
self-consistency check. **The independence of this bundle lives in F1**, the
Appendix F match, not in F3.

**Reading taken, pending confirmation.** F3 carries two comparisons: the analytic
spherical-Bessel solution of the (F.1) recursion, which Appendix F names on
p. 380, as the machine-precision acceptance test; and §8's closed form as the
paper-facing comparison. The frame decision has since made the second cleaner
than it was when this question was written — §8 is a Newtonian-frame result, and
v1.0.0 now carries a generic $u^a$ and specialises explicitly, so the comparison
is against the paper's own specialisation rather than against an inherited frame
choice.

**The $\ell$ range, derived.** The PI authorised this stream to set it. §8's
comparison is Sachs–Wolfe only: (196) descends from (181), where the acoustic
modulation $\cos(k r_s)$ is dropped by taking $r_s^*\to0$, and §8.3.2 sets the
transfer function to unity. The accuracy is therefore bounded by the term that was
dropped, $1-\cos(k r_s)$ with $\ell\simeq k\thinspace \Delta\eta_*$. Using Annals II's own
§8.3.2 model the acoustic scale is $\ell_A\simeq203$, giving $\ell\le9$ at 1%,
$\le12$ at 2%, $\le20$ at 5% and $\le29$ at 10%.

**Adopted: $2\le\ell\le20$ at 5%.** The lower bound is the quadrupole — there is
no monopole in the CGI approach (p. 366), the dipole is frame-dependent, and the
late ISW vanishes in the flat matter-dominated model the comparison uses.

Regenerated by `scripts/derive_ell_range.py`; the number is computed, not
asserted. The same script exercises finding **B-3**, which was found in the course
of this derivation.

**Status: closed.**

---

## Q4 — Wilson & Silk — **CLOSED 2026-10-06**

Appendix F matches the recursion to four external treatments. Wilson & Silk
(1981) predates arXiv and has not been obtained.

**Handling, agreed.** F1 ships with **three panels** — Hu & Sugiyama, Ma &
Bertschinger Eqs. (49)/(50), Seljak & Zaldarriaga Eq. (3d) — and the release
states three external hierarchies, not four. Nothing blocks on it, and a copy
turning up later is purely additive: a fourth panel.

> **Do not quote Wilson & Silk Eq. (7) from Annals II Appendix F and count it as
> a fourth source.** Independent checks are counted by their sources, not by
> their arguments; a coefficient transcribed through Annals II is the same source
> as Annals II. This is recorded here precisely because it is the mistake a later
> session would make in good faith.

**Status: CLOSED 2026-10-06.** The PI supplied the scanned paper, and both
halves resolved from primary sources. Appendix F's prose names "Wilson & Silk"
while its key is **Wilson alone** (*Ap. J.* **273**, 2 (1983)); and it cites
Wilson's Eq. (7), which is the quadrupole equation, where the $\ell>2$ hierarchy
is his **Eq. (8)** — findings B-4 and B-9.

Wilson is now the **fourth** external hierarchy and the strongest of the four. His
weights are Hu & Sugiyama's, but he writes the recursion in the *imaginary*
convention, with both bracket terms positive under an overall $-ikT$; only
$\Theta_\ell=i^\ell\delta_\ell$ recovers the real, opposite-sign form. His panel
therefore tests the **phase convention** — the subject of B-1 and criterion 3 —
from a source published before any of the others. Residual $3.1\times10^{-14}$;
F1 now carries four panels.

---

## Q5 — release staging — **CLOSED 2026-10-05**

**Brief §3, criterion 6** requires every number the paper prints to be
regenerated here, or marked not-machine-checkable with a reason. That cannot
close until the paper's manuscript is frozen.

**Decided: option 5a, release candidate then release.** `v1.0.0-rc` is tagged
when criteria 1–5 close; `v1.0.0` is the release at manuscript freeze, with all
six closed. One DOI, reserved early so the paper has something to cite and minted
on publication of v1.0.0. No release ever claims a done-condition it has not met.

**Status: closed.**

---

## Q6 — the v1.0.0 target restated, and what it does to criterion 5

**Raised by the PI, 2026-10-05.** The staging was under-specified and this stream
had it partly wrong.

**The target of v1.0.0 is the CDM angular power spectrum: Eq. (186) computed from
Eq. (176)**, with (187) and (188) as the covariant route to the same number.
Equation numbers are identical in the published and arXiv editions here.

$$C_\ell=\frac{2}{\pi}\frac{\beta_\ell^2}{(2\ell+1)^2}\int_0^\infty\frac{dk}{k}\thinspace  k^3|\tau_\ell(k,\eta_0)|^2\quad(186)$$

$$\langle\tau_{A_\ell}\tau^{A_\ell}\rangle\simeq\frac{\beta_\ell}{2\pi^2} \int k^2dk\thinspace |\tau_\ell(k,\eta_0)|^2,\qquad C_\ell=\Delta_\ell(2\ell+1)^{-1}\langle\tau_{A_\ell}\tau^{A_\ell}\rangle \quad(187, 188)$$

**The two routes are identical**, exactly, given $\Delta_\ell=4\pi\beta_\ell/
(2\ell+1)$ — proven in `tests/`. That identity is the paper's own point stated as
a test: §7.1.4 says that at linear order the solutions do not differ importantly
from the canonical treatment, and that what the covariant formulation buys is the
route through the multipole mean-squares, *"not attainable in the canonical
treatment."* **The route is the result.**

### What this stream had wrong

**$\Lambda$CDM was placed at v2.0.0 on a bad argument.** This stream said it
needed a recombination history, tight coupling and diffusion damping. All three
are required by v1.0.0's own target, because (176) carries the acoustic and
Doppler sources and §8 carries the damping. The marginal cost of $\Lambda$CDM
over CDM is the expansion law (185) and the late-ISW term already present in
$S_{\rm ISW}$ (179). **$\Lambda$CDM belongs at v1.5.0**, as the PI proposed.

### Consequence: criterion 5 is now wrong as written

Criterion 5 reads *"the almost-Friedmann–Lemaître temperature spectrum is
recovered over $2\le\ell\le20$ to 5%"*. That range was derived in **Q3** for the
§8.3.1 **Sachs–Wolfe-only closed form**, where $\cos(kr_s)$ is dropped by taking
$r_s^*\to0$. With the target restated to (186) from (176) — which retains the
acoustic and Doppler sources — that restriction does not apply, and the
acceptance range should extend through the acoustic peaks and into the damping
tail.

**Q3's derivation is not withdrawn.** It remains correct and useful as a check on
the **Sachs–Wolfe limit**, and is worth keeping as a separate sub-criterion
because it is a closed-form target with no free parameters.

**Decision required.** Criterion 5 becomes two:

| | Statement | Target |
|---|---|---|
| **5a** | the Sachs–Wolfe limit is recovered over $2\le\ell\le20$ to 5% | §8.3.1 closed form; already derived, Q3 |
| **5b** | the CDM angular power spectrum is recovered to a stated tolerance over a stated range | (186) from (176) — **range and tolerance to be set** |

5b's range and tolerance cannot be derived the way 5a's was, because there is no
closed form to bound the error against. The honest options are an external
Boltzmann code at the level of the observable, or the canonical analytic
treatment of Hu & Sugiyama. **This reopens Q3's option 3b**, which was set aside
when the target was thought to be the §8 closed form alone.

**External target settled, 2026-10-05: CMBFAST, and nothing else.** The bundle is
a Boltzmann code written from scratch; it is checked against CMBFAST at best, and
no other code, deliberately, to avoid scope creep.

**ΛCDM moves into v1.0.0.** Both the CDM and the ΛCDM angular power spectra are
wanted in the almost-Friedmann–Lemaître setting at v1.0.0, so that the high-$\ell$
extension at v1.5.0 is a clean delta rather than a change of model. v1.5.0 is the
high-$\ell$ effects and is gated on Paper 1.

**Still open:** 5b's tolerance and $\ell$ range against CMBFAST.

**Status: the external target and the tolerance method are now settled
(2026-10-06); only the measured numbers remain.** Comparison is against **CAMB
and CLASS**, with CMBFAST cited for the *method* — line-of-sight integration,
Seljak & Zaldarriaga, already in Annals II's own bibliography — because the
Fortran 77 original is unmaintained and effectively unrunnable. The tolerance is
**measured, not chosen** — and under **S4c**, 2026-10-15, measured against the
bundle's own pipeline rather than against the external codes, which are reported
alongside as context. The paragraph below records the rule as it stood: the
CAMB–CLASS mutual difference was the floor, since no
agreement can be claimed tighter than two trusted independent codes agree with
each other. Reported in three $\ell$ bands whose failure modes differ: $2\le\ell<30$,
$30\le\ell<1000$, $1000\le\ell\le2000$. Decisions S4a and S4b.


---

## Q1, reopened 2026-10-06 — **CLOSED 2026-10-07 on C3.2**

**Raised by Coordination. Substantially correct, and this stream was wrong to
close criterion 3 on the external match.**

**The error.** Criterion 3 read: *"both harmonic phase conventions run end to
end; only one reproduces the real, opposite-sign form of the external
hierarchies."* As a basis for the convention that is **circular**. Rephasing both
sides of the comparison by $i^\ell$ is a change of variable and cannot fail:

| comparison | residual |
|---|---|
| as the bundle does it, no phase | $6.2\times10^{-15}$ |
| both sides rephased by $i^\ell$ | $6.2\times10^{-15}$ |

Pinned at `tests/test_appendix_f_chain.py::test_the_external_match_is_invariant_under_a_common_rephasing`.
For Hu & Sugiyama, Ma & Bertschinger and Seljak & Zaldarriaga this bundle applies
**no** phase, which is a choice, not a derivation. Had the covariant recursion
been implemented in the other convention, the same three could have been matched
by applying $i^\ell$ to them, and nothing in the chain would have objected.

**The algebra, stated once.** Changing the harmonic normalisation
$Q_{A_\ell}=\mu^{-\ell}\mathrm D_{\langle A_\ell\rangle}Q$ rescales
$\tau_\ell\to c^\ell\tau_\ell$ with $c=\mu'/\mu$. A recursion
$\tau_\ell'=k[A_\ell\tau_{\ell-1}+B_\ell\tau_{\ell+1}]$ becomes
$(A_\ell/c,\thickspace B_\ell c)$, so **$B/A\to c^2B/A$**. At $c=i$ an opposite-sign real
bracket becomes a same-sign bracket under an overall $i$. The two conventions in
the literature are the two values of $c^2=\pm1$ and nothing else.

**Where Coordination overshoots.** The claim that "all four print the same real
opposite-sign bracket" is not what the sources say. **Wilson Eq. (8), read from
the scanned page, prints both bracket terms positive under an overall $-ikT$** —
the same-sign imaginary form. The four are *not* in one convention; three are at
one value of $c^2$ and Wilson is at the other.

**And that is what rescues a piece of it.** Annals II states, in the line
following its flat-case mode functions, that the covariant form

> "differs by a factor of $i^{-\ell}$ from Wilson [W83] since we are using plain
> mode functions instead of plane waves"

That phase is **specified by the antecedent**, not chosen by this stream. So the
Wilson comparison is the one place where the applied phase is externally fixed,
and the bundle matching it after exactly $i^\ell$ — with the transformed solution
*real* to $10^{-10}$, asserted separately — carries information the other three
do not.

**What the chain therefore establishes:**

| | status |
|---|---|
| the $\ell$-weights $\ell/(2\ell\mp1)$, $(\ell+1)/(2\ell+3)$ | **established**, four independent sources, convention-independent |
| that the bundle sits at the same $c^2$ as HS, MB and SZ | **established** |
| that Wilson sits at the *other* $c^2$, at $i^{-\ell}$ | **established**, and it is the antecedent's own statement |
| that $Q_{A_\ell}=(-k_{\rm phys})^{-\ell}\mathrm D_{\langle A_\ell\rangle}Q$ is the right reading of Annals I's definition | **NOT established by this chain.** It needs the definition, not the match |

**What criterion 3 must become.** It cannot claim the external match selects the
convention. It can claim what is true: that both conventions are run end to end,
that they are related by $c^2=-1$ and nothing else, that the bundle's choice is
the one at $i^{-\ell}$ from Wilson as the antecedent states, and that the
covariant $\tau_{A_\ell}$ is invariant under the choice while the mode
coefficients are not.

**Status: open.** Criterion 3 is **reopened** and the release notes carry the
restricted claim until it is settled from Annals I's definition of
$Q_{A_\ell}$ rather than from the match. Not blocking: nothing computed depends
on it, because every released figure plots the invariant multipole quantity.

**One discrepancy to settle with Coordination.** Their Q4 closure cites **Wilson
& Silk 1981, *Ap. J.* 243, 14, Eq. (7)**, read by P1-T. Annals II's key `W83`,
its bibliography entry, and the $i^{-\ell}$ statement all name **Wilson 1983,
*Ap. J.* 273, 2** — whose $\ell>2$ hierarchy is Eq. **(8)**, his (7) being the
quadrupole (finding B-9). Both papers are real sources, but they are different
papers, and the $i^{-\ell}$ statement is about the 1983 one. F1's fourth panel is
built on Wilson 1983 Eq. (8), read here from the scan the PI supplied.


---

## Q1 — CLOSED 2026-10-07. The definition settles it; the match confirms it

**Coordination pointed at `conventions.md` C3.2, which is what this stream said
was needed and had not looked for.** Q1's reopening was right and its resolution
was already in the project.

**C3.2**, marked **DEF** and *"Seed verified against the PDF, 2026-10-03"*:

> $Q_{A_\ell} = (-k_{\rm phys})^{-\ell}\mathrm D_{\langle A_\ell\rangle}Q$. The
> stripped factor is $(-k_{\rm phys})^{\ell}$: **real, no $i$**. For a real
> eigenfunction $Q$, every $Q_{A_\ell}$ is real.
> — GE98 (49); Th (1.48); restated GE98 p. 23 below (134), and Th App. D
> footnote to (D.44).

A real stripped factor means the two candidate normalisations differ by a
**real** ratio, so $c^2=+1$ and the relative sign inside the bracket cannot flip.
Only an imaginary ratio flips it. **That fixes the convention from the
definition, which is exactly what the match could not do.**

**And the two independent derivations of the phase agree.**

| | statement | source |
|---|---|---|
| **C3a.3** | $Q_{A_\ell}=(-k)^{-\ell}(-ik)^{\ell}O^{(k)}_{A_\ell}Q = i^{\ell}O^{(k)}_{A_\ell}Q$ | arithmetic on GE98 (49) and (147) |
| *Annals II*, after (modeff) | the covariant form "differs by a factor of $i^{-\ell}$ from Wilson since we are using plain mode functions instead of plane waves" | the antecedent itself |

Wilson uses plane waves. The two say the same thing by different routes, and the
measurement — Wilson Eq. (8) integrated complex and as printed, matching after
exactly $i^\ell$ at $3\times10^{-14}$, with the transformed solution real to
$10^{-10}$ asserted separately — is then a confirmation rather than a selection.

**The chain is no longer circular**: the definition selects, the derivations
agree, the measurement confirms. Criterion 3 closes.
`tests/test_appendix_f_chain.py::test_c32_fixes_the_convention_and_the_match_then_confirms_it`.

**Finding B-1 is corroborated by the same sheet.** C3a.4 records that GE98
(60)=(148), Th (1.59) and Th (A.50) print $Q_{A_\ell}=(-1)^{\ell}O^{(k)}_{A_\ell}Q$
and marks it *"error under C3.2"* — the phase of $Q_{A_\ell}=(+ik)^{-\ell}
\mathrm D_{\langle A_\ell\rangle}Q$, not of GE98 (49). That is B-1, reached
independently by Coordination from the definition where this stream reached it
by reimplementation.

**One distinction worth keeping.** C3.2 is **DEF**, externally verified, and is
what closes criterion 3. C3.5 — the sign $\lambda=-1$ of a *scalar's* mode
coefficient — is **STIPULATED** and is a different quantity. Criterion 3 rests on
the verified one.

---

## A note on symbols, 2026-10-07

The conventions sheet renamed `λ` to `s_Q` on 2026-10-06 because `λ` meant three
unrelated things two rows apart — in *Annals I/II* it is $k_{\rm phys}$, in C3.5
it was a scalar's sign, and in the P-3 row it is a basis rescaling.

**This bundle used it for a fourth thing**: "the $\lambda^2=-1$ normalisation".
That is now written **$c^2=-1$**, matching the symbol this bundle's own algebra
already used in `functions/spectra/angular.py` and the Appendix F tests.

Entries written before that date are **left as they were**. The findings record
is append-only and rewriting a historical entry to use a later symbol would be
exactly the kind of silent edit the guard exists to prevent. Where an older entry
says $\lambda^2=-1$, read $c^2=-1$.

---

## Q4 — SETTLED 2026-10-07, and the answer is five sources

**Coordination withdrew its reading and adopted this stream's; log rows v1.10.44
and v1.10.46.** The record:

*Annals II* means **M. L. Wilson 1983, *Ap. J.* 273, 2**, and its $\ell>2$
hierarchy is **Eq. (8)**. The key `W83` is consistent across every citation in
`cbrII.tex`; `\cite{WS}` appears exactly once, at l.215; and the load-bearing
$i^{-\ell}$ sentence at l.1364 names "Wilson" alone over `W83`. Only two prose
instances, l.500 and l.4037, write "\& Silk". **The key is right in every case
and the prose is the slip in two** — finding B-4, now corroborated by a full
citation sweep rather than by the bibliography alone.

**F1's fourth panel on Wilson 1983 Eq. (8) stands, and nothing in the bundle
changes.**

### The fifth source is real, and its phase is unknown

P1-T read **Wilson & Silk 1981, *Ap. J.* 243, 14, Eq. (7)** from a PI-supplied
scan: $\ell>2$, coefficients $\ell/(2\ell-1)$ and $(\ell+1)/(2\ell+3)$. That pin
does not pass through *Annals II*. It is a different paper, independently
verified, and the **earliest of the set**.

**What it gives:** a fifth independent source for the $\ell$-weights. The release
may state five external hierarchies, and F1 may take a fifth panel.

**What it does not give:** its phase convention. P1-T reported the weights, not
the relative sign, nor whether the coefficients are real. **This bundle will not
state which $c^2$ it sits at until someone has read the page.**

### The hypothesis worth testing — Coordination's, and it is a good one

Wilson 1983 Eq. (8) prints the **imaginary, same-sign** form. If Wilson & Silk
1981 Eq. (7) prints the **real, opposite-sign** form, then *the same first author
published in both conventions two years apart*.

That would be direct evidence, from a single author, that the phase is a
**convention and not a fact** — which is the content of the criterion 3 question,
arriving from outside this project entirely.

**It is a hypothesis, not a claim.** The scan settles it, and nothing may be
written either way until it is read. **Status: awaiting the W&S 1981 scan from
the PI.** Additive; blocks nothing.

### Attribution rule, adopted

*Annals II*'s Appendix F match and its $i^{-\ell}$ statement are about the **1983**
paper. **Wilson & Silk 1981 may be cited for the weights, never for *Annals II*'s
comparison.** *Annals II*'s own name/key mismatch is a defect in *Annals II* and
is recorded here as B-4; Coordination carries the corresponding documentation
row in `provenance.md`.

---

## Q5 — does the full $1+3$ treatment predict excess power at low $\ell$?

**Asked by the PI, 2026-10-14**, while reading criterion 5b's first run:
*"getting excess power at low-$\ell$ would be great if it was from the full
$1+3$ treatment and frame."* **Parked by the PI the same day**, with the
measurements below recorded so that it is parked rather than forgotten.

### Three measurements that already bear on it

**1. The sign is wrong for the hypothesis.** The bundle does not show excess
power at low $\ell$; it shows a **deficit**. $D_\ell$ at $\ell=2$ sits below the
plateau relative to $\ell=30$ by a factor of 80 on the $\mathcal V$ branch and 8
on the $e^{-\kappa}$ branch, against CAMB's 1.14. Finding **T-41** attributes a
factor of ten of that to approximation **A-2** and leaves 4.8 open. Nothing can
be concluded about a covariant excess while an approximation worth an order of
magnitude sits on top of the same multipoles.

**2. The frame cannot supply one at this order, and that is measured.**
Finding **T-31**: (102) builds every multipole from the same three
$\ell$-independent coefficients $C_0,C_1,C_2$, so a change of frame moves the
$C_A$ and nothing else and its response is $\ell$-independent up to three
$j_\ell$ weights. Measured dipole/median ratio **1.00–1.25x**, flat from
$\ell=1$ to 400. **A frame moves all $\ell$ together; it has no mechanism for a
low-$\ell$-specific excess.** F7 was built expecting the opposite and reported
this instead.

**3. The covariant sectors are a small-scale effect, not a large-scale one.**
The rank-0 and rank-2 sectors are what a gauge-fixed treatment cannot have,
because $\sigma_{ab}=0$ empties them --- (110). Their share of $C_\ell$ in the
CDM frame, measured, is **0.54% at $\ell=2$** and **32% at $\ell=600$**: least
at the quadrupole, growing with $\ell$. **F2's third panel is this**, drawn so
the negative result is a figure rather than a remark.

### Where an excess could still come from

* **$O(\epsilon^2\ell)$, which is v1.5.0.** The couplings v1.5.0 adds are
  products of two first-order quantities, and a product of two frame-dependent
  quantities is not frame-invariant merely because each factor's leading
  frame-dependence cancels. That is the one place in this programme where the
  frame stops being a device and becomes a prediction. The supplement already
  says so; nothing here changes it.
* **The almost-EGS direction, v2.0.0.** $\sigma_{ab}$, $\omega_{ab}$ and the
  Weyl quantities bounded *by* the low multipoles, in the covariant variables
  this bundle computes. That is a bound running from the data to the geometry,
  not a source of power running the other way, and it should not be confused
  with one.

### What would have to be true, and the control it needs

A covariant low-$\ell$ excess requires the rank-0/2 share to **rise** toward the
quadrupole, or a frame response that **depends on $\ell$**. Both are measured
and both go the other way at this order. If either is revisited, the search
needs a control that can fail before any number is quoted: **wanting the answer
is exactly the condition under which T-24 happened**, where a closure that could
not fail was cited as though it could. A negative result here is publishable and
should be set up as such.

**Status: parked by the PI. Blocks nothing. Revisit at v1.5.0**, where the
mechanism that could produce one first exists.

---

## Q7 — the recombination grid sets the primary source, and nothing guards it — **ANSWERED 2026-10-15, decision S33**

**Raised by P1-B 2026-10-15, out of finding T-46. The PI's call. Blocks
nothing at v1.2.0; it should be answered before v1.5.0 builds on this base.**

### The measurement

The primary term — the one that carries the Sachs–Wolfe plateau and the
acoustic amplitude — is read at a single point, $\eta_*$, off a source that is
built from $\kappa'$, the visibility and the opacity. Those three are
interpolated onto the line-of-sight grid from `RecombinationHistory`'s own,
which defaults to `n_eta=4000` — spacing $4.9\times10^{-4}$, **coarser than the
grid it is interpolated onto**. Refining it moves the answer:

| `RecombinationHistory` `n_eta` | 4 000 | 8 000 | 16 000 | 32 000 | 64 000 |
|---|---|---|---|---|---|
| primary source at $\eta_*$, EdS, $k=30$ | $-118.321$ | $-118.415$ | $-118.469$ | $-118.499$ | $-119.788$ |

That is **1.2%**, against criterion 5a's measured 0.26% and the same order as
the acoustic-band differences this bundle reports against CAMB and CLASS.
`required_n_eta` derives the line-of-sight grid from $k_{\max}$ and raises if it
is not met; **nothing derives or guards the recombination grid**, and it is the
one that sets the primary term.

### A second, smaller thing riding on the same mechanism

`pipeline.run` reads that source at $\eta_*$ with `np.interp` — linear — while
`integral_solution` reads the same quantity with a `CubicSpline`. The two
differ by $1.1\times10^{-4}$ of the source, and the difference does not fall
with the line-of-sight grid because it is set by the recombination grid's
piecewise-linear kinks.

### Why this is raised rather than fixed

Either change moves every generated figure, table and manifest in the release —
the interpolant at the $10^{-4}$ level, the grid at the $10^{-2}$ level. **Four
days before a freeze is not when one stream changes the amplitude of every
number in a bundle on its own authority.** Nothing currently *claimed* is
falsified by it: every stated tolerance is wider, and criterion 5b's gate is
unaffected because both routes share the history.

That last clause is also the uncomfortable one. **A comparison that holds an
input fixed cannot check that input** — finding T-3 — and this is the live
example: the two-route gate would report $9.5\times10^{-6}$ whatever the
recombination grid did.

### The three options, with what each costs

1. **Derive it, as `required_n_eta` derives the other one.** The honest fix and
   the project's own idiom: the resolution becomes arithmetic from the
   visibility's width rather than a default. Costs a regeneration of the whole
   tree and a re-measurement of 5a, F2, F5, F6, F7 and the 5b context.
2. **Raise the default and converge it once**, recording the converged values
   and the residual. Cheaper, and leaves the guard missing.
3. **Document and defer to v1.5.0.** Costs nothing now and means v1.5.0's
   nonlinear corrections are measured against a base with a known 1.2%
   amplitude uncertainty in its primary term, which is the wrong foundation for
   a correction whose whole claim is that it *matters*.

**P1-B's recommendation is (1), taken immediately after the v1.2.0 tag rather
than before it**, so the release that is nearly closed closes on measured
numbers and the change lands at the head of v1.5.0's work with a full
regeneration behind it. (3) is the one to avoid, for the reason given.

### Answered — the PI, 2026-10-15

*"I agree: my recommendation is to derive the grid, immediately after the
v1.2.0 tag, not before it. This makes sense and makes the staging worthwhile."*

**Option (1), staged after the tag. Recorded as decision S33**, which carries
the five acceptance conditions the work has to meet and the one instrument that
can check it — the CAMB/CLASS comparison, since 5b's gate shares the grid and
cannot. v1.2.0 ships this as a **stated limit** in the release notes and the
supplement, in the manner of O1 and O2.

**Status: closed as a question, open as scheduled work. Nothing in v1.2.0
changes for it.**

---

## Q8 — ANSWERED 2026-10-16. Finding T-51: the acoustic start, not the damping

**The question was answered the day after it was raised, by the PI asking the
opposite question.** *"Did the visibility function over damp away our acoustic
peaks?"* — no, and the visibility never touches them: (177) is a boundary term
at $\eta_*$, never integrated against $\mathcal V$, and $k_D$ carries Silk
diffusion alone. Chasing why not found the cause.

**The peaks are not missing. They are in the wrong place.** Our oscillation
period in $\ell$ is **589.7** against CAMB's **285.5**, and a damping envelope
multiplies — it cannot change a period. The acoustic ODE is handed a grid
starting at `RecombinationHistory.build`'s `z_max = 3000.0`, which discards
**50.8%** of the sound horizon $r_s(\eta_*)=\int_0^{\eta_*}c_s\thinspace d\eta$ and so
doubles the peak spacing. Starting at $z=2\times10^5$ reproduces CAMB's 285.5
to **1.6%**.

**The $0.14$ at $\ell=720$ below was our trough being compared with CAMB's
peak.** Regimes 2 and 3 of the three below are one defect, not two, and it is
not the one either of them names. Regime 1 is unaffected and stands.

**Criterion 5b could not see it**, because both of its routes take the same
`solve_acoustic` call on the same truncated grid — **S4c** exactly, and the
clearest demonstration yet that the external comparison earns its keep as
context. Finding **T-51**; the fix lands in v1.3.0 under **S37**.

*The original question is kept below in full, because a question answered by
being reframed is worth more intact than deleted.*

---

## Q8 (as raised) — the second and third acoustic peaks are missing, and one band number hides it

**Raised by P1-B 2026-10-15, on the PI's question "any thoughts on the
difference between ours and CAMB?". Measured from `outputs/f9-acoustic-spectrum.csv`,
which is committed. Nothing here blocks the v1.2.0 tag.**

### What the data says, in three regimes rather than one

Shape, $D_\ell$ renormalised at $\ell=30$, `PLANCK_MODEL` against CAMB:

| $\ell$ | 2 | 22 | 60 | 150 | 210 | 300 | 420 | 630 | 720 | 990 |
|---|---|---|---|---|---|---|---|---|---|---|
| ours / CAMB | **0.02** | 0.77 | **2.30** | 1.71 | 1.28 | 1.33 | **0.50** | 0.13 | **0.14** | 0.08 |

**Three regimes with three different signs, and they are not one defect.**

1. **$\ell<30$: we are a factor of fifty low.** This is understood and recorded:
   approximations **A-1** and **A-2**, the weight the line-of-sight integral
   carries. (102) prints $\mathcal V=\kappa'e^{-\kappa}$ and the plateau is what
   that costs — findings **T-41** and **T-42**, a factor of eighty measured
   there and $0.02$ here.
2. **$60\le\ell\le300$: we are up to $2.3\times$ high, with the first peak at
   $\ell\simeq162$ against $206$.** Part is the acoustic scale ($z_*=1114.5$
   here against CAMB's $1088.5$ — Peebles against HyRec). Part is an artefact
   of the comparison itself: see below.
3. **$\ell>390$: we collapse, and this one is not in the record.** CAMB's
   second and third peaks reach $1.78$ and $2.76$; ours reach $0.88$ and
   $0.40$. **We have essentially no second or third acoustic peak.**

### Two things this exposes about the comparison, not only about the physics

**The band average hides a sign change.** `compare_criterion_5b.py` reports the
acoustic band as a single worst-case $137$% over $30\le\ell<1000$. That band
contains a region where we are $130$% **high** and a region where we are
$90$% **low**, and a worst-case magnitude cannot distinguish them. *A single
number per band was the right first instrument and is now the wrong one.*
**Proposed:** split the acoustic band at the first peak, and report the signed
ratio's range rather than only $\max|{\rm diff}|$.

**The normalisation anchor sits on broken ground.** Everything is renormalised
at $\ell=30$ — but $\ell=30$ is on the steep rising part of *our* plateau, which
regime 1 says is wrong by a factor of fifty at $\ell=2$ and still $0.77$ at
$\ell=22$. **Anchoring a shape comparison at a point where one of the shapes is
known to be wrong propagates that error into every other band**, and some of
regime 2's excess is likely to be exactly that rather than physics. Renormalising
at the first peak instead would separate the two.

### What is NOT claimed here

**No mechanism is asserted for regime 3.** The obvious candidates — the
slow-decoupling order, which F6 already measures as the largest single
approximation in the chain; the visibility width; a loss of acoustic coherence
at high $k$ — are candidates and nothing more. **T-41's first diagnosis was
exactly this kind of reasoning and it was wrong**, and the lesson recorded there
is that the plausible cause and the actual cause were different. The damping
scale has been checked and is *not* sufficient on its own: at $\ell=720$,
$k\simeq225$ against $k_D=536.9$ gives an envelope of $0.70$, nowhere near the
factor of seven observed.

### Status

**Open. For v1.5.0**, where the acoustic sector is being touched anyway and
where **S35** already places the Hu \& Sugiyama analytic cross-check — which is
the instrument most likely to discriminate between these candidates, since it
is an *analytic* acoustic treatment whose approximations are individually
switchable. That is now a second, independent argument for S35's placement.

**What v1.2.0 claims is unaffected.** Criterion 5b is gated on the bundle's own
pipeline (**S4c**); the external comparison is context and is reported as a
measured distance, not as agreement. This question sharpens what that distance
is made of — which is the itemisation's stated purpose.

## Q9 — the register audits discretisations; nothing audits physical ranges

**Raised by P1-B 2026-10-16, on finding T-51.**

`config/grid-register.toml` names every `linspace`, `logspace`, `arange` and
`geomspace` in the bundle — 41 of 41 — and the generator fails on one it does
not know. **It would never have caught T-51.** `z_max = 3000.0` is not a
resolution: it is the *extent* of a physical range, and the grid it defines was
perfectly well resolved. A 2.0–3.0× error in the acoustic scale survived
thirty-seven registered grids because nothing in the bundle audits the question
*how far does this integration reach, and is that far enough*.

Other instances of the same shape, named now rather than found later:
`tight_coupling_factor = 6.0` (how far past $\eta_*$ the tight-coupling window
runs), `z_end` and `z_start` in `peebles_ionisation`, `x_max` in the Bessel
table, and the $\ell$ and $k$ band edges. Some are guarded; **none is
registered**, and the guards that exist were each written after a finding.

**What a range register would have to state** is different from a grid's:
not *samples per feature* but *what lies outside, and what it is worth*. For
`z_max` the answer was **half the sound horizon**.

**Not proposed as work for v1.3.0.** The grid register took a day and closed a
class that had already bitten three times; this one has bitten once, and the
instance is fixed. Raised so that the next range defect is found by looking
rather than by a comparison nobody expected to disagree.

## Q10 — does the second-order quadrupole ring for tensor modes?

**Raised by the PI 2026-10-17, on reading the re-derived Appendix C
expansion:** *"the hope is that additional anisotropic pressure or shear terms
might appear at higher order, that could be novel ... that there is additional
ringing for say tensor modes?"*

### The mechanism, which is real and derived

Appendix C's own solid-angle reduction puts the **shear** in $\mathcal B$'s
rank-two part,
$\int\mathrm d\Omega\thinspace O^{A_\ell}\mathcal B\simeq\dots+\delta^\ell_2[\tfrac{8\pi}{15}\sigma^{a_1a_2}]$.
At first order $-t_c\mathcal B$ therefore reproduces \S7.1's quadrupole
$\tau_{ab}\simeq-\dot\kappa^{-1}[\sigma_{ab}+\mathrm D_{\langle a}v^B_{b\rangle}]$,
as it must. At second order the closed form contributes
$+t_c^2\thinspace \mathcal D\mathcal B$, which is $\dot\sigma_{ab}$ at rank two and
$e^c\mathrm D_c\sigma_{ab}$ at rank three — and Appendix G's
$\dot\sigma_{ab}+2H\sigma_{ab}+E_{ab}\approx0$ turns the first of those into

    sigma-dot_ab = -2 H sigma_ab - E_ab,

so **the electric Weyl tensor enters the radiation quadrupole at second order
in the scattering time and does not at first.** That much is derivation, and it
is in the supplement's appendix.

**For a tensor mode both $\sigma^{(T)}_{ab}$ and $E^{(T)}_{ab}$ oscillate at
the gravitational-wave frequency**, so the second-order quadrupole acquires an
oscillatory driving on a scale set by the wave rather than by the sound
horizon. That is the mechanism the question asks about, and it is not the
acoustic one.

### Why the antecedent is the right place to have found it

*Annals~II* flags this regime itself, in a footnote to the very sentence about
removing the radiation quadrupole: *"If there are any anisotropic contributions
such as anisotropic scattering (in the matter frame) or **large shear (from
gravitational waves)** at that time this sort of approximation should be
considered with care --- such phenomena would break tight-coupling."* The
paper names gravitational-wave shear as what breaks the approximation and does
not pursue it. The expansion now exists at arbitrary order, so pursuing it is
arithmetic rather than a new formalism.

### What is **not** established, and the PI's framing needs one correction

The question proposes the new terms might be $\mathcal O(\varepsilon^2\ell)$
against $\mathcal O(t_c^2)$. **They are not, and cannot be.** The recursion is
**linear** in $V=v^ae_a$ and $\mathcal B$, so the closed form yields
$\mathcal O(t_c^m\epsilon)$ at every order and never $\epsilon^2$. Terms of
$\mathcal O(\varepsilon^2\ell)$ require the *quadratic* parts of the Boltzmann
equation, which \S5.5.1's almost-Friedmann--Lema\^{\i}tre linearisation
discards --- **S2**'s subject, not Appendix C's.

**The high-$\ell$ sensitivity the question is reaching for is real by a
different and cleaner route.** Each $e^a\mathrm D_a$ contributes one power of
$k$ and rank $r$ terms carry $k^{\thinspace r-1}$, so the expansion parameter is
$t_ck$ and not $t_c$. A cut in rank *is* a cut in $t_ck$, and the order at
which the expansion may be stopped **falls as $\ell$ rises**. That is a
statement about $t_ck$, carries no $\epsilon^2$, and is the one to take into
the high-$\ell$ work.

### What would settle it

Three steps, none of which needs new formalism.

1. **Reduce $\tau_{(2)}$'s six terms onto their multipoles** with Appendix C's
   own identities ($e^ae^b\mathrm D_av_b=O^{ab}\mathrm D_av_b+\tfrac13\mathrm
   D_av^a$ and its two siblings), so each term lands on a stated $\ell$.
2. **Separate the tensor sector.** $\sigma^{(T)}$ has no scalar potential
   behind it, so the driving is \eqref{eq:sigma-dot} alone and the comparison
   is clean.
3. **Project.** Ringing in the quadrupole is not ringing in $C_\ell$ until it
   survives the line-of-sight integral, and the visibility's finite width is
   the obvious thing that would erase it. **That is the step that decides the
   question**, and it is also the step at which a positive answer stops being
   a curiosity.

*Not scheduled.* Steps 1 and 2 sit naturally beside **S42**'s derivation in
v1.3.0; step 3 needs a tensor source the bundle does not have. Recorded so the
mechanism is written down while it is fresh, and so that a later claim about it
has to answer this entry rather than start clean.

## Q11 — the acoustic source has the right phase and the spectrum does not

**Ring-fenced 2026-10-17, after T-51's fix exposed it.** This is the live
blocker on v1.3.0's acoustic component and it is **localised**, which is why it
is worth a question of its own rather than more searching.

### The source is right

The monopole combination at last scattering, measured over 180 modes with the
derived acoustic start, in units of $k r_s/\pi$:

| extrema of $(\delta T+\Phi_A)(\eta_*)$ | 1.13, 2.09, 3.06, 4.07, 5.03, 6.05, 7.07, 8.03 |
|---|---|

**Integers.** So $(\delta T+\Phi_A)\propto\cos(k r_s)$, peaking at
$\ell=n\times272$ — which is (181) exactly, and which is where CAMB's peaks sit
(206, 492, 729, against $n\times272$ offset by the radiation driving, **A-3**).
The acoustic equation, its initial condition and its phase are **not** the
problem. **T-51** fixed what it was supposed to fix.

### The spectrum is not

F9's $C_\ell$ for `PLANCK_MODEL` has maxima at **408, 664, 925**, which are
$(n+\tfrac12)\times272$ — **half a period off**, the signature of $\sin(k r_s)$
rather than $\cos$. And the envelope collapses: normalised to its own maximum
above $\ell=60$, ours falls to **0.007 at $\ell=540$** where CAMB is at 0.438,
a factor of **60**.

So the defect sits **between the source and $C_\ell$** — in the coefficient
assembly, the rank decomposition or the projection — and not in the acoustic
sector that has had all the attention.

### The most likely place, and it is already written down

`newtonian_set`'s rank-zero coefficient is **identically zero**: measured
$c_0(\eta_*)=0$ at every $k$ from 40 to 1100. That is the antecedent's own
structure — (110) puts everything in the rank-one sector in the Newtonian
frame, and *Annals II* states flatly that *"there is no monopole temperature
anisotropy in the CGI approach while there is one in the canonical
treatment"*. If the $\cos$-bearing monopole never enters the projected
transfer, the spectrum inherits the rank-one dipole's $\sin$, and a half-period
offset is exactly what one would see.

**Whether that is correct physics or a missing integration by parts is the
question.** \S*Integration by Parts* exists in the paper precisely to move
contributions between ranks, and a monopole moved into the dipole by parts
carries its $\cos$ with it. **This bundle may be dropping a boundary term that
the antecedent's own manipulation requires.** That is a hypothesis with a named
mechanism, not a finding.

### Why nothing in the bundle caught it

Criterion **5b** compares (102) against (177)--(179) at $8.2\times10^{-6}$ ---
and **both routes share the coefficient assembly**. **T-3** again: two
agreeing routes agree about what they share. The instrument that would see this
is the **rank decomposition**, and the bundle has it: **F5** draws the source
by rank, and **D4** — *"no monopole in the CGI approach"* — is the diagnostic
written for this exact statement.

**D4 is deferred.** It was deferred to v1.1.0 under **S-b**, retargeted to
v1.5.0 under **T-47** when that deferral went stale, and has never run. *The
diagnostic that addresses the live blocker is the one that has been deferred
twice.* **Recommended: retarget D4 to v1.3.0 and run it**, which is the PI's
call and is raised rather than taken.

### What this means for the Hu \& Sugiyama comparison

**S35a/S42's comparison is aimed at the oscillator, and the oscillator is now
the one part shown to be right.** H\&S will not find Q11. The comparison
remains worth doing — A-4's cross terms and A-3's driving are real and it is
the instrument for both — but it is **not** the instrument for this, and
sequencing it first would spend the effort where the answer is already known.


---

### ANSWERED, 2026-10-17 — and the prediction above was right about the mechanism and wrong about the cause

The half-period offset **is** the rank-one dipole's $\sin(k r_s)$ showing
through, exactly as reasoned above. But the monopole was not missing by
construction. It was present and **outweighed a thousand to one** by a
line-of-sight weight no caller had named: finding **T-57**, where
`TwoFrameEnvironment.line_of_sight_weight` documented `"opacity"` as its
default and the code read `"printed"`.

**D4 — the diagnostic this entry recommended retargeting — is what measures
it**, and the PI approved that retargeting the same day. Written and run
2026-10-17; under $\mathcal V$ the rank-zero monopole sector is $2\times10^{-5}$
of $C_\ell$ and the rank-one dipole is $1.005$ of it, at every
$2\le\ell\le100$. Under $e^{-\kappa}$ it is $0.986$ monopole.

*The hypothesis in the section above — a boundary term dropped from an
integration by parts — is **not** what happened, and is withdrawn rather than
left standing as a live suspicion.* $c_0\equiv0$ in the Newtonian frame remains
true and remains the antecedent's own structure; it is simply not what was
suppressing the plateau, because the CDM frame carries a rank-zero sector and
showed the same defect.

**A second, independent defect was found in the same search and is recorded as
T-56**: F9's $k$ grid samples $j_\ell^2$ at 0.94–0.96 points per oscillation,
below Nyquist, giving a non-monotonic 5–22% quadrature error that moves peaks
differently in each route. It is **not** the plateau — refining $dk$ eightfold
leaves $D_2/D_{30}$ where it was — so the two are separate findings with
separate fixes.

**Q11 is downgraded from blocker to residual, not closed.** With the weight
corrected $D_2/D_{30}=0.0926$ against CAMB's 0.881: an order of magnitude
recovered, an order of magnitude outstanding, and the plateau still tilted
where `pipeline` reports it flat to 30%. The open part is now a **route**
question rather than a physics one — two implementations of (102) that agree
at $k=1$ and diverge above $k=3$ — and it is carried as **Q12**.


---

## Q12 — two implementations of (102) agree at $k=1$ and diverge above $k=3$

**Opened 2026-10-17**, as the residual of **Q11** after **T-57** and **T-56**
were fixed. This is the remaining order of magnitude in the Sachs--Wolfe
plateau, and it is a *route* question rather than a physics one.

The bundle computes (102) with a generic $u^a$ in **two places**:

* `functions/spectra/two_route.py`, which criterion **5b** gates against
  (177)--(179) at $8.240\times10^{-6}$;
* `functions/spectra/two_frame.py`, which F2, F5, F7, F9, D4, D6, D7 and
  `compare_criterion_5b` all use, and which **no criterion gates**.

With the line-of-sight weight matched to $e^{-\kappa}$ on both sides, the BBKS
transfer off on both, the same background, the same recombination history, the
same $R=0$ damping scale and `expansion_coupling=False` on both, on
`PLANCK_MODEL`, taking the ratio two_frame / two_route:

| $k$ | $\ell=2$ | $\ell=5$ | $\ell=10$ | $\ell=50$ |
|---|---|---|---|---|
| 1 (CDM frame) | 1.10 | 1.02 | 1.00 | 0.98 |
| 3 | 44.6 | 2.74 | 0.83 | 0.12 |
| 10 | $-22.0$ | $-28.4$ | $-45.1$ | 3.59 |
| 100 | $-101$ | $-111$ | $-121$ | $-341$ |

**They are the same object at $k=1$ and not at $k=3$.** Agreement to 1–2% in
the long-wavelength limit says the assembly algebra is broadly shared; a
divergence that grows with $k$ and flips sign says something scale-dependent
differs. Ruled out already: the weight (matched), the transfer function (off),
the oscillator option (`expansion_coupling=False` in both), the damping scale
(both use $R=0$ via `diffusion_scale(..., r_of_eta=0)`), and the acoustic start
(both derive it per mode since **T-51**).

Remaining candidates, in the order they are worth testing:

1. **The $\eta$ grid.** `two_route` derives `n_eta` per mode from $k$;
   `build_environment` builds **one** grid from `k_max` and every mode shares
   it. For $k\ll k_{\max}$ that grid is over-resolved, which should be
   harmless — so if this is the cause, the mechanism is not resolution.
2. **`damping_total` against `diffusion`.** `integral_solution`'s docstring
   says (102) *distinguishes* them — $e^{-(k/k_D)^2}$ on the integrand,
   $\mathcal D(\eta_0,k)$ on the two boundary terms. `transfer_by_rank` passes
   the **same scalar** to both.
3. **The coefficient construction itself**, which is the one thing the two do
   not share.

**Why this matters beyond the plateau.** A-2's own table, measured through
`pipeline`, reports $e^{-\kappa}$ as flat to 30% over $2\le\ell\le20$;
`two_frame` under the same weight gives a plateau that rises by $11\times$ from
$\ell=2$ to 30. Both cannot be right, and **the one that is ungated is the one
every released figure uses.**

**Criterion 5b cannot see this, by construction.** It compares two routes that
share a setup built once on purpose — *"two setups with one rule cannot
drift"* — and `two_frame` is a third setup that rule never reached. **S4c's
rule, reaching further than it was written for**: a self-comparison cannot see
a shared antecedent, and it cannot see a sibling it was never pointed at.


---

### ANSWERED, 2026-10-17 — finding T-58, three causes, all of them shared choices

Not the coefficient construction, which was the third candidate and is clean.
The causes were the **tight-coupling window** (`two_route` integrated to
$\eta_0$ where the other two stop at $6\eta_*$), **(102)'s lower limit**
(`two_frame` inherited the printed $\eta_*$ by omitting `eta_floor`, discarding
half the visibility peak), and the **$\eta$-grid floor** (`two_frame` never had
`N_ETA_FLOOR`, which `two_route` has carried since T-45).

Candidate 2 of the three listed above — `transfer_by_rank` passing one scalar
as both `diffusion` and `damping_total` — **was wrong**, and is withdrawn. The
two are equal by construction when `damping_epoch == "star"`, which is the
release's setting, so nothing was being conflated.

After the fix the two implementations agree to $3\times10^{-4}$–$6\times10^{-3}$
of the row's scale, from $1.5\times10^{-1}$–$1.6\times10^{0}$. **The remainder
is one named convention** — the analytic $\tilde\tau_1'$ of (152) against a
spline through $\kappa'\tilde v_B$ — and substituting it closes the gap to
$10^{-6}$. Which route should change is open, and is **Q13**, because it moves
criterion 5b's published number.

`tests/test_two_frame_is_gated.py` is the instrument this question asked for:
the released route now has a gate, with a control that restores the printed
lower limit and requires the gate to catch it.

---

## Q13 — which construction of $(\kappa'\tilde v_B)'$ is right?

**Opened 2026-10-17**, as the residual of **Q12**.

`two_frame` forms it by the product rule,
$\kappa'\tilde\tau_1'+\kappa''\tilde\tau_1$, with $\tilde\tau_1'$ **analytic
from (152)** and $\kappa''$ from `np.gradient`. `two_route` forms it as
`CubicSpline(eta, kappa_prime * tau_1).derivative(1)`.

`sources.py` argues for the first explicitly, under finding **T-23**:
*"mode-expanding a derivative is not differentiating a mode amplitude"*, and
*Annals II* derives (106) rather than differentiating (105) for the same
reason. On that argument **the ungated route is the more correct one.**

Against it: $\kappa''$ by `np.gradient` is second-order on a grid where
$\kappa'$ varies by orders of magnitude across recombination, so the product
rule trades a spline on a smooth product for a finite difference on a steep
factor. *Which error is larger has not been measured*, and that measurement —
both forms against a refined recombination grid, which is **S33**'s territory —
is what this question needs.

**It is worth 5b's published number**, so it is the PI's call: the two
constructions differ by $6\times10^{-3}$ of the row's scale, and criterion 5b
currently reports $8\times10^{-6}$ under one of them.


---

## Q14 — should $C_0$ enter the line-of-sight integrand at all?

**Opened 2026-10-17** by **T-60**, which measured that it is three to four
orders of magnitude of the CDM frame's spectrum and the whole of the frame gap.

$C_0$ is the coefficient of (89)'s $\delta_{\ell0}$ entry. The covariant
hierarchy has no $\ell=0$: *Annals II* p. 366 says so in one sentence, and
`integral_solution` refuses $\ell<1$ independently. `integral_solution`
nonetheless sums $C_0$ into the source bracket at every $\ell\ge2$, where
$C_0=p_0a\mathcal B_2$ against $C_2=p_2a\mathcal B_2/k^2$ makes it larger by
$2.5k^2$.

**Three readings, and this bundle has not established which is right.**

1. **$C_0$ belongs only at $\ell=0$ and contributes nothing.** Then the
   Newtonian frame is right by construction ($C_0\equiv0$ there) and the CDM
   frame is right once it is dropped — which is what the measurement shows, to
   1–15%. The attraction of this reading is that it needs no new physics and
   it is what the quoted sentence says.
2. **$C_0$ belongs in the integrand and (102) is transcribed correctly**, in
   which case the frames genuinely disagree by three orders of magnitude and
   the almost-EGS argument of Appendix E is in trouble, because a
   frame-dependent $C_\ell$ is not an observable.
3. **$C_0$ belongs but with (89)'s printed sign**, which is **B-11** — already
   recorded, already controlled by `use_printed_c0`, and **about the sign of
   this same coefficient**. B-11 questioned the sign and nobody questioned the
   placement.

**This is a question about the antecedent, not about the code**, and it needs
(89) and (90) read against each other on the page rather than another
measurement here. It is the first thing to settle in the frame sector and it
gates **S44** — which frame F9 draws is not answerable while one of them is
carrying a term that may not exist.
