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

## Q2 — the $\pm(\ell+2)$ control is second order at general $\ell$

**Brief §3, criterion 4** asks that both sign choices of $\pm(\ell+2)$ run, the
wrong one growing $\propto\ell$.

**Why it cannot hold as written.** Annals II, Appendix E, p. 378 states that
$F_{A_\ell}$ and $\sigma_{ab}$ are each at most $O(\varepsilon)$. The shear
coupling $\sigma^{bc}\tau_{bcA_\ell}$ is therefore $O(\varepsilon^2)$ and is
absent from the almost-Friedmann–Lemaître hierarchy at general $\ell$ — which is
why (F.1) carries no shear term at all. It survives only at $\ell=2$, where
$\tau_{\ell-2}$ is the zeroth-order monopole; there $(\ell+2)$ is the number 4 and
there is no $\ell$-growth to exhibit. Settling a sign at $\ell=2$ is in any case
the specialisation the project's index-algebra rule forbids.

**Proposed restatement.** The coefficient is carried in the recursion as a
**switchable wiring control** for figure C3, labelled as a control and explicitly
not an almost-Friedmann–Lemaître result; the physics claim moves to v1.5.0.

**Status: open.**

---

## Q3 — figure C1 has no published curve to overlay

**Brief §3, criterion 5** asks that the almost-Friedmann–Lemaître temperature
spectrum of Annals II be recovered to a stated tolerance, and **brief §6** makes
C1 — recovered spectrum against the published one — the key figure.

**What the source contains.** Annals II has **no figures and no tables**: 74
pages, four embedded images, all page furniture or equation strips. Its §8
derives the angular power spectrum in **closed form** (around Eqs. (196) and
(201)), on large scales, with the transfer function set to unity in places. There
is no published curve.

**Consequence.** Evaluating Annals II's own formula and comparing it to a
reconstruction derived from Annals II's own hierarchy is a self-consistency
check, not the independent cross-check the brief's rationale rests on. The
independence of this bundle lives in Appendix F — that is, in figure **C2**, not
in C1.

**Options for C1's second series:**

1. the analytic spherical-Bessel solution of the (F.1) recursion, which Appendix F
   itself names on p. 380 — representation-free, machine-precision tolerance;
2. an external Boltzmann code, compared at the level of the observable $C_\ell$;
3. Annals II §8's closed-form $C_\ell$, with the $\ell$ range stated explicitly.

**Recommendation:** (1) as the acceptance test and (3) as the paper-facing
figure, with the independence claim relocated to C2.

**Status: open.**

---

## Q4 — one of the four external hierarchies may not be independently obtainable

Appendix F matches the recursion to four external treatments. Wilson & Silk
(1981) predates arXiv. If its Eq. (7) is transcribed from Appendix F rather than
read from the paper, it is **not an independent source** — the project's own rule
is that independent checks are counted by their sources, not by their arguments.

**Handling:** unless a copy of Wilson & Silk is supplied, the spine is **three**
external hierarchies and the release says so.

**Status: open.**

---

## Q5 — acceptance criterion 6 depends on another stream

**Brief §3, criterion 6** requires every number the paper prints to be
regenerated here, or marked not-machine-checkable with a reason. That cannot
close until the paper's manuscript is frozen.

**Handling:** stage the release — criteria 1–5 first, criterion 6 on manuscript
freeze. Noted so that v1.0.0 is not reported complete while 6 is outstanding.

**Status: open, sequencing only.**
