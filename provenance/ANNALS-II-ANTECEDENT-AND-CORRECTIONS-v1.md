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

---

## G3 — Annals II (199) is correct only at even $m$; (204) and (205) inherit a 12.8% error

**Class: material.** **Found 2026-10-05, before the solver was written, while
deriving the $\ell$ range for the release's tolerance.**

Appendix-free, §8.3, p. 372. Annals II prints the Bessel identity

$$\int_0^\infty \frac{dz}{z^{m}}\,j_\ell^2(z)=\frac{\pi}{2^{m+2}}\,
\frac{m!\,\left(\ell-\tfrac{m}{2}-\tfrac12\right)!}
{\left(\tfrac{m}{2}\right)!\,\left(\ell+\tfrac{m}{2}+\tfrac12\right)!}\tag{199}$$

and uses it twice: at $m=2$ for the large-scale result **(201)**, and at $m=1$ for
the CDM horizon-scale normalisation **(204)**.

**The denominator should carry $\left[\left(\tfrac{m}{2}\right)!\right]^2$, not
$\left(\tfrac{m}{2}\right)!$.** Numerical evaluation against the integral, at
$\ell=2,10,30$:

| $m$ | printed (199) | corrected | used by |
|---|---|---|---|
| 0 | exact | exact | — |
| 1 | **low by $\sqrt\pi/2 = 0.886227$** | exact | **(204)** |
| 2 | exact | exact | (201) |
| 3 | wrong by $\Gamma(5/2)=1.3293$ | exact | — |

The printed form happens to be right exactly where $\Gamma(\tfrac{m}{2}+1)=1$,
that is at $m=0$ and $m=2$ — which is why **(201) is correct as printed** and the
slip went unnoticed. The corrected identity reproduces all four columns to six
digits.

**What moves.** The printed (199) returns $\sqrt\pi/2=0.886227$ of the true
integral at $m=1$, so **(204) is low by 11.4%**; the corrected value is
$2/\sqrt\pi=1.128379$ times the printed one. $D_\ell$ in (205) carries
$C^{(CDM)}_\ell$ in the denominator, so $D_\ell$ is correspondingly **high by
12.8%**, and so is anything normalised through it. Nothing else moves: no sign
changes, no $\ell$-dependence changes — (199)'s $\ell$-structure is right at every
$m$, and the error is a pure constant.

**Raised to P1-T and the PI**, because Paper 1 citing any normalised amplitude
from §8.3.3 would inherit it. It is not load-bearing for this bundle's acceptance
spine, which uses neither (204) nor (205).

**Status:** corrected in the reconstruction; the corrected identity is asserted in
`tests/`, and the derivation is regenerated by
`scripts/derive_ell_range.py`.

---

## Criterion 5 — the $\ell$ range, derived

**Authorised by the PI, 2026-10-05**, as Q3's remaining line.

§8's comparison is a **Sachs–Wolfe-only** result: (196) descends from (181), where
the acoustic modulation $\cos(k r_s)$ is dropped by taking $r_s^*\to0$, and §8.3.2
sets the transfer function to unity. The tolerance is therefore bounded by the
acoustic term that was dropped, $1-\cos(k r_s)$, with $\ell \simeq k\,\Delta\eta_*$.

Using Annals II's own §8.3.2 model — $n=1$, $h=0.5$, $\Omega_B=0.05$, flat
matter-dominated, $a_0=1$, $z_*=1100$ — the acoustic scale is
$\ell_A=\pi\Delta\eta_*/r_s \simeq 203$, and

| tolerance | 1% | 2% | 5% | 10% |
|---|---|---|---|---|
| $\ell\le$ | 9 | 12 | 20 | 29 |

**Adopted: $2\le\ell\le20$, tolerance 5%.** The lower bound is the quadrupole;
there is no monopole in the CGI approach (p. 366), and the dipole is
frame-dependent. The late ISW vanishes in the flat matter-dominated model the
comparison uses, so the low-$\ell$ end is clean.

Regenerated by `scripts/derive_ell_range.py`; the number is computed, not
asserted.

---

## Amendment, 2026-10-05 — how corrections are surfaced

**PI direction.** The classification above stands, but the *handling* changes:

> **Correct silently in the reconstruction, and mark each correction with a
> succinct footnote.** The forensics stay here; the outputs carry a pointer, not
> a narrative.

So a correction is now surfaced in three places and no more:

| Where | What appears |
|---|---|
| the reconstruction | the corrected expression, no commentary in the code beyond the citation |
| the caption of any affected figure, and the supplement | **one footnote**, naming the printed equation and this record. The word is *misprint*, not *error* |
| this file | the full entry — what was printed, what it should read, what moves, and what does not |

This supersedes the earlier instruction that a **material** finding be raised to
the paper stream before anything is built on it. It is no longer a gate; the
footnote and this record are the mechanism. **G3 is therefore corrected silently
with a footnote**, not raised as a blocker. A finding that would change a sign, an
$\ell$-weight, or an acceptance criterion is still raised, because that changes
what the bundle is testing rather than what it prints.

**Standing instruction, recorded here because it governs every later choice:**
*be faithful to the $1+3$ approach wherever possible.* Where a quantity can be
written covariantly or in mode form, the reconstruction carries the covariant
form and reduces to modes only where a comparison requires it; where a frame can
be left generic, it is left generic and specialised explicitly at the end.

### Footnote register

Numbered footnotes used in the supplement and in captions, each resolving to an
entry above.

| Footnote | Resolves to | Appears in |
|---|---|---|
| †1 | **G2** — (F.4) requires the $(2\ell+1)^{-1}$ division its prose specifies before it is in the Ma & Bertschinger form | F1 caption; supplement §Acceptance spine |
| †2 | **G3** — (199) requires $[(m/2)!]^2$; (201) is unaffected, (204) and (205) are not | supplement §Comparison; `diagnostics/ell-range-v1.0.0.txt` |
| †3 | **G1** — the $(-1)^\ell$ / $i^\ell$ slip in Annals I, inconsequential for the covariant multipole | supplement §Conventions |
