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
  $\lambda^2=-1$**. The two candidate normalisations — $(-k)^{-\ell}
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
bracket is run with its relative sign flipped — the $\lambda^2=-1$ case of Q1 —
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
dropped, $1-\cos(k r_s)$ with $\ell\simeq k\,\Delta\eta_*$. Using Annals II's own
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

$$C_\ell=\frac{2}{\pi}\frac{\beta_\ell^2}{(2\ell+1)^2}\int_0^\infty\frac{dk}{k}\,
k^3|\tau_\ell(k,\eta_0)|^2\tag{186}$$

$$\langle\tau_{A_\ell}\tau^{A_\ell}\rangle\simeq\frac{\beta_\ell}{2\pi^2}
\int k^2dk\,|\tau_\ell(k,\eta_0)|^2,\qquad
C_\ell=\Delta_\ell(2\ell+1)^{-1}\langle\tau_{A_\ell}\tau^{A_\ell}\rangle
\tag{187, 188}$$

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
**measured, not chosen**: the CAMB–CLASS mutual difference is the floor, since no
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
$Q_{A_\ell}=\lambda^{-\ell}\mathrm D_{\langle A_\ell\rangle}Q$ rescales
$\tau_\ell\to c^\ell\tau_\ell$ with $c=\lambda'/\lambda$. A recursion
$\tau_\ell'=k[A_\ell\tau_{\ell-1}+B_\ell\tau_{\ell+1}]$ becomes
$(A_\ell/c,\;B_\ell c)$, so **$B/A\to c^2B/A$**. At $c=i$ an opposite-sign real
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
