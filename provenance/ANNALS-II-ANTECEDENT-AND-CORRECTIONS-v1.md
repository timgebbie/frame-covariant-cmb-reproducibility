# Annals II — antecedent and corrections, v1

**Theory-to-code traceability for the defects this reconstruction finds in its
antecedent.** The bundle reproduces Annals II from first principles; it is built
to find that paper's remaining errors, not to agree with it. This file is where
those findings are recorded.

> T. Gebbie, P. K. S. Dunsby and G. F. R. Ellis, *$1+3$ covariant cosmic
> microwave background anisotropies II: the almost-Friedmann–Lemaître model*,
> **Annals of Physics 282, 321–394 (2000)**, `doi:10.1006/aphy.2000.6034`.
>
> T. Gebbie and G. F. R. Ellis, *$1+3$ covariant cosmic microwave background
> anisotropies I: algebraic relations for mode and multipole expansions*,
> **Annals of Physics 282, 285–320 (2000)**.

## How a finding is classified

| Class | Handling |
|---|---|
| **Typographical and inconsequential** | corrected silently in the reconstruction; recorded here only where the slip can mislead a reader or a test harness |
| **Material** | corrected, and logged here with the printed equation number, what it should read, and whether anything downstream moves |
| **Load-bearing** | corrected, logged, and raised to the paper stream and the PI before anything is built on it |

**Equation numbers in this file are the published numbers.** The published and
arXiv numberings differ, and not by a constant offset — in Annals I the Helmholtz
equation is (47) in print and (48) on arXiv, the harmonic normalisation
$Q_{A_\ell}=(-k_{\rm phys})^{-\ell}\mathrm{D}_{\langle A_\ell\rangle}Q$ is (48) in
print and (49) on arXiv, while $O^{A_\ell}$ is (15) in both. Every number here is
resolved from the published PDF.

---

## G1 — Annals I prints $(-1)^\ell$ where its own definition gives $i^\ell$

**Class: typographical, inconsequential.** Carried forward from the conventions
gate as the model entry.

Annals I prints

$$(Q|_{\rm flat})_{\langle A_\ell\rangle} = (-1)^\ell\,O^{(k)}_{A_\ell}\,Q|_{\rm flat}$$

where its own definition and its own preceding line give $i^\ell$. It is a real
slip: it is the phase of the definition $Q_{A_\ell} = (+ik)^{-\ell}
\mathrm{D}_{\langle A_\ell\rangle}Q$, not of the normalisation the paper actually
adopts.

**Why it never produced a wrong result in twenty-five years.** $\tau_\ell$ is
defined as the coefficient of $Q_{A_\ell}$, so every bracket in the hierarchy is
a relation among the $\tau_\ell$, and every such relation is invariant under

$$Q_{A_\ell}\to\lambda^\ell Q_{A_\ell},\qquad \tau_\ell\to\lambda^{-\ell}\tau_\ell .$$

The phase sits on the basis tensor and cancels out of every coupling. The slip is
therefore inconsequential for the hierarchy, and the reconstruction corrects it
silently.

**Consequence for this bundle — and the distinction that must not be lost.** The
invariance above is a statement about the **covariant** multipole
$\tau_{A_\ell}$. It is *not* a statement about the mode coefficients: in the mode
bracket of (F.1) the raising and lowering terms acquire $\lambda^{-1}$ and
$\lambda^{+1}$, so their relative coefficient carries $\lambda^{-2}$ and the
relative sign flips whenever $\lambda^2=-1$ — which is exactly the difference
between the two candidate normalisations. Both facts are true, about different
objects, and conflating them is the likeliest source of the contradictory
verdicts this question has attracted.

The practical consequence is favourable: because the four external hierarchies of
Appendix F are all written with **real** coefficients of **opposite** relative
sign, the Appendix F match discriminates the normalisation without importing a
basis. Both statements are asserted executably in
`tests/test_appendix_f_chain.py`.

---

## G2 — Annals II (F.4) is not in the form it is immediately identified with

**Class: typographical for the physics; material for the test harness.**
**Found 2026-10-05, before any code was written, by reading Appendix F against
the published PDF.**

Appendix F, p. 380, states that (F.3) can be rewritten *"(on first multiplying
through by $(2\ell+1)^{-1}$)"* as (F.4), and prints

$$-(2\ell+1)\big(\alpha_\ell^{-1}\tau_\ell\big)' \simeq k\big[(\ell+1)
\big(\alpha_{\ell+1}^{-1}\tau_{\ell+1}\big) - \ell\big(\alpha_{\ell-1}^{-1}
\tau_{\ell-1}\big)\big],$$

then identifies this as the form of the $\ell>2$ free-streaming integrated
Boltzmann equation of Ma & Bertschinger, Eqs. (49)/(50), and of Seljak &
Zaldarriaga, Eq. (3d).

**What is actually true.** The printed (F.4) is the *direct substitution* of
$\beta_\ell = \alpha_\ell^{-1}(2\ell+1)$ into (F.3), and is algebraically correct
as it stands — it follows from (F.3) exactly. The parenthetical instruction was
simply not applied to the display. The Ma & Bertschinger form, which carries
$k/(2\ell+1)$ on the right-hand side, is obtained only after the stated division:

$$-\big(\alpha_\ell^{-1}\tau_\ell\big)' \simeq \frac{k}{2\ell+1}\big[(\ell+1)
\big(\alpha_{\ell+1}^{-1}\tau_{\ell+1}\big) - \ell\big(\alpha_{\ell-1}^{-1}
\tau_{\ell-1}\big)\big].$$

**Nothing downstream moves.** No result in Annals II depends on the display
rather than on the identification, and the chain (F.1) → (F.2) → (F.3) → (F.4) is
internally consistent at every step.

**Why it is nevertheless logged.** A test harness that compares the printed (F.4)
directly against the printed Ma & Bertschinger recursion reports a $(2\ell+1)$
mismatch and reads as a failure of the reconstruction. The acceptance test must
apply the stated division before comparing. This is exactly the class of slip
that costs a day and looks like a physics error.

**Status:** corrected in the reconstruction; comparison in `tests/` performs the
division explicitly and names this entry.

---

## Verified consistent — no finding

Recorded so that later sessions do not re-derive them.

| Checked | Against | Result |
|---|---|---|
| (F.1) → (F.2), multiplication through by $\beta_\ell$ | $\beta_\ell = \ell/(2\ell-1)\,\beta_{\ell-1}$ and $\beta_{\ell+1} = (\ell+1)/(2\ell+1)\,\beta_\ell$ | exact, both terms |
| (F.2) → (F.3), proper to conformal time | $dt = a\,d\eta$ | exact |
| (F.3) → (F.4), substitution of $\beta_\ell=\alpha_\ell^{-1}(2\ell+1)$ | — | exact; see G2 for the form question |
| (F.1) weight $(\ell+1)^2/\big[(2\ell+3)(2\ell+1)\big]$ | the mode-recursion weight $\ell^2/\big[(2\ell+1)(2\ell-1)\big]$ at $\ell\to\ell+1$ | exact — the hierarchy is the adjoint of the mode recursion |

---

## Symbols that collide across the sources

**Not a defect in either source; a hazard in bridging them.**

`k` is used for the **comoving** wavenumber in Annals II Appendix F, which writes
the free-streaming coefficient as $k/a$ with a proper-time derivative. The
project's normative conventions sheet declares $k \equiv k_{\rm phys}$ in its
harmonic-recursion section, with $k_{\rm phys} = k/a$. The two differ by a factor
$a$, in precisely the equations this bundle bridges.

**Handling:** the code carries `k_com` and `k_phys` as distinct names and never a
bare `k`. This is the same discipline Appendix F itself asks for between
$\tau_\ell$ and $\tau_{A_\ell}$.
