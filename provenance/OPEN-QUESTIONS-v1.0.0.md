# Open specification questions — v1.0.0

Items where the stream brief and the sources do not yet agree, raised before code
was written rather than resolved in flight. **v1.0.0 does not close until each
is settled by the issuing stream.**

---

## Q1 — criterion 3 is meetable; only the word *self-consistent* needs changing

**Brief §3, criterion 3** asks that both harmonic phase conventions run and that
**only one** be self-consistent.

**This stream first reported that the criterion could not hold, and that was
wrong.** The error was to apply the cancellation argument of brief §4 — finding
**G1** — to the mode coefficients. It is a statement about the covariant
multipole. Both statements are true, about different objects, and conflating
them is the likeliest reason the same question has returned three different
verdicts from three careful passes.

Under $Q_{A_\ell}\to\lambda^\ell Q_{A_\ell}$, $\tau_\ell\to\lambda^{-\ell}
\tau_\ell$:

- the **covariant** multipole $\tau_{A_\ell}=\sum_k\tau_\ell Q_{A_\ell}$ is
  **invariant** — the slip never produced a wrong result, which is G1; but
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

**Status: open — wording change requested, no scope change.**

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

## Q3 — figure F3's comparison target, and the tolerance's $\ell$ range

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

**Still required: the $\ell$ range.** §8 is a large-scale result with the transfer
function set to unity in places, so criterion 5's tolerance is meaningless
without a stated range. Either state it, or authorise this stream to set it from
where the §8 approximations hold and record the derivation in `provenance/`.

**Status: open — one line needed.**

---

## Q4 — Wilson & Silk — **ON HOLD 2026-10-05, at the PI's direction**

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

**Status: on hold. Not blocking.**

---

## Q5 — acceptance criterion 6 depends on another stream

**Brief §3, criterion 6** requires every number the paper prints to be
regenerated here, or marked not-machine-checkable with a reason. That cannot
close until the paper's manuscript is frozen.

**Handling:** stage the release — criteria 1–5 first, criterion 6 on manuscript
freeze. Noted so that v1.0.0 is not reported complete while 6 is outstanding.

**Status: open, sequencing only.**
