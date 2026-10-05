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

---

## G4 — Appendix F's Wilson citation names one paper and keys another

**Class: typographical, but consequential for verification.**
**Found 2026-10-05, while assembling the external sources for figure F1.**

Appendix F, p. 380, writes:

> "This can be immediately seen to be the same mode equation for $\ell>2$ as in Hu
> and Sugiyama [39] and Wilson and Silk [81, Eq. (7)])."

In Annals II's own reference list, p. 392:

| key | reference |
|---|---|
| **[81]** | M. L. Wilson, *Astrophys. J.* **273** (1983), 2 — **Wilson alone** |
| **[82]** | M. L. Wilson and J. Silk, *Astrophys. J.* **243** (1981), 14 — Wilson **and Silk** |

So the name says Wilson & Silk (1981) and the key points to Wilson (1983). One of
the two is wrong, and they are different papers: [82] is the flat-case
Boltzmann-hierarchy paper, [81] its negative-curvature sequel.

**Not resolved here.** Resolving it means reading Eq. (7) of each and seeing which
is the mode equation in question; both are pre-arXiv. The likely reading is that
the key is a typo for [82], since Appendix F is explicitly the flat $K=0$ case,
but *likely* is not a verification and this bundle does not guess a citation.

**Why it is logged rather than silently fixed.** A reader checking the acceptance
spine against the named source would open the wrong paper and find no Eq. (7)
matching — and would reasonably conclude the reconstruction was wrong. The same
class as **G2**: harmless to the physics, costly to anyone verifying.

**Consequence for F1.** Already recorded under Q4: the figure ships with the three
hierarchies that can be sourced independently, and the Wilson panel waits on a
library copy. Quoting Eq. (7) through Appendix F would make it the same source as
Appendix F, not a fourth.

**Status:** open, non-blocking. Needs one library visit, not a decision.

---

## External sources for the F1 panels — what has been read, and from where

Recorded so that no later session counts a coefficient twice (§3a).

| Annals II key | Paper | Status |
|---|---|---|
| **[69]** | Seljak & Zaldarriaga, *ApJ* **469** (1996), 437 | **read, verbatim**, from the arXiv HTML of astro-ph/9603033. Eq. (3d): $\dot\Delta^{(S)}_{T\ell}=\frac{k}{2\ell+1}[\ell\Delta^{(S)}_{T(\ell-1)}-(\ell+1)\Delta^{(S)}_{T(\ell+1)}]-\dot\kappa\Delta^{(S)}_{T\ell}$, $\ell>2$. Free-streaming part matches this bundle exactly |
| **[56]** | Ma & Bertschinger, *ApJ* **455** (1995), 7 | **not yet read from source.** An HTML render returned a paraphrase, not the displayed equation. A paraphrase is not a reading |
| **[39]** | Hu & Sugiyama, *ApJ* **444** (1995), 489 | not yet read |
| **[40]** | Hu & Sugiyama, *Phys. Rev. D* **51** (1995), 2599 | not yet read |
| **[81]/[82]** | Wilson (1983) / Wilson & Silk (1981) | pre-arXiv; and see **G4** — which one is cited is itself unresolved |

**Equation numbers must be recorded with their edition.** Annals II cites Ma &
Bertschinger's *published* (49)/(50). An arXiv copy may number differently, and
this project has already been bitten by assuming a constant offset between
editions.

---

## Criterion 1 — closed 2026-10-05. The external hierarchies, read from source

The three obtainable external treatments were transcribed from their own papers,
not through Appendix F, and integrated as printed.

| Annals II key | Source, as read | Weights as printed | Appendix F form |
|---|---|---|---|
| **[40]** | Hu & Sugiyama, *Phys. Rev. D* **51** (1995), 2599, **Eq. (6)**, p. 2601 | $\ell/(2\ell-1)$, $(\ell+1)/(2\ell+3)$ | **(F.3)**, the $\beta$ normalisation |
| **[56]** | Ma & Bertschinger, *Astrophys. J.* **455** (1995), 7, **Eqs. (49)**, **(50)** | $\ell/(2\ell+1)$, $(\ell+1)/(2\ell+1)$ | **(F.4)**, the $\alpha$ normalisation |
| **[69]** | Seljak & Zaldarriaga, *Astrophys. J.* **469** (1996), 437, **Eq. (3d)** | $\ell/(2\ell+1)$, $(\ell+1)/(2\ell+1)$ | **(F.4)** |

**Result.** Against the bundle's own integration, with the monopole normalisation
common and therefore an overall scale of exactly $1.000000$:

| | max abs difference over $\ell\le25$ | relative |
|---|---|---|
| HS vs (F.3) | $1.3\times10^{-13}$ | $5\times10^{-14}$ |
| MB vs (F.4) | $1.4\times10^{-14}$ | $3\times10^{-14}$ |
| SZ vs (F.4) | $1.4\times10^{-14}$ | $3\times10^{-14}$ |

**Two distinct normalisations, both matched.** That is the substance: Hu &
Sugiyama write the hierarchy in the $\beta$ variable and Ma & Bertschinger and
Seljak & Zaldarriaga in the $\alpha$ variable, and Appendix F prints (F.3) and
(F.4) for exactly that reason. A basis phase leaking into the couplings would
break at least one of the two.

**Two things the sources corrected in the asking.**

- The mode equation attributed to "Hu and Sugiyama [39, 40]" is in **[40]**, the
  *Physical Review D* paper. It was not located in **[39]**, *Astrophys. J.* **444**
  (1995), 489, which works from the integral solution. Same class as **G4**: a
  reader following [39] alone does not find it.
- **MB's arXiv copy numbers its hierarchy (49) and (50)** — the same numbers
  Annals II cites from the published paper. No offset here, unlike the Annals I
  and II case. Recorded because the absence of an offset is as worth knowing as
  its presence.

**Scattering terms dropped.** HS's $-\dot\tau\Theta_\ell$ and SZ's
$-\dot\kappa\Delta_{T\ell}$ are Thomson scattering, not free streaming.

**Wilson remains unread** — pre-arXiv, and **G4** leaves it ambiguous which paper
is meant. The release states **three** external hierarchies, not four.

---

## G4 — supporting evidence, 2026-10-05. Still open

The thesis chapter whose published form is *Annals I* opens by stating that the
angular correlation functions are obtained *"following the Wilson-Silk approach
for the mode representation, but derived and dealt with in $1+3$ covariant and
gauge invariant (CGI) form."*

That the mode-representation antecedent is **Wilson \& Silk** supports reading
Appendix F's `[81]` as a typo for `[82]`, which is Wilson \& Silk (1981), rather
than as a naming slip for `[81]`, Wilson (1983).

**This is supporting evidence, not a verification.** Resolving the citation still
requires Eq. (7) of the paper itself, and this bundle does not settle a citation
by inference. **G4 remains open**, and the release continues to state three
external hierarchies rather than four.

---

## G5 — Annals II (201) omits the comoving distance from the reduction

**Class: material, and it moves an acceptance criterion — therefore RAISED, not
footnoted.** Found 2026-10-05 while building the Sachs–Wolfe spectrum.

§8.3.1, p. 372. From (198) with $P(k)=Ak^{n-1}$, Annals II writes

$$C_\ell=\frac{1}{2\pi}AH_0^4\Omega_0^{1.54}\int\frac{dk}{k^2}\,k^{n-1}
j_\ell^2(k\chi)\tag{200}$$

and states that "using (199) for $m=2$ ($n=1$)" gives

$$C_\ell=\frac{A}{2}H_0^4\Omega_0^{1.54}\frac{1}{(2\ell+3)(2\ell+1)(2\ell-1)}.
\tag{201}$$

**The reduction carries a factor $\chi$ that the display does not.** Substituting
$z=k\chi$ into (200),

$$\int dk\,k^{n-3}j_\ell^2(k\chi)=\chi^{2-n}\int dz\,z^{n-3}j_\ell^2(z)
=\chi^{2-n}\,I(m=3-n),$$

so $n=1$ carries one factor of $\chi$, and with $I(2)=\pi/[(2\ell+3)(2\ell+1)
(2\ell-1)]$ the result is $(A\chi/2)H_0^4\Omega_0^{1.54}/[(2\ell+3)(2\ell+1)
(2\ell-1)]$.

**Demonstrated numerically, not argued.** (198) integrated directly in $k$, with
no change of variable and no use of (199), agrees with the reduction to eight
digits and exceeds the printed (201) by exactly $\Delta\eta_*$ at every $\ell$
tested:

| $\ell$ | 2 | 5 | 10 | 20 | 30 |
|---|---|---|---|---|---|
| quadrature / printed (201) | 1.939725 | 1.939724 | 1.939722 | 1.939735 | 1.939740 |

against $\Delta\eta_*=1.939725/H_0$ for the flat matter-dominated background at
$z_*=1100$. The ratio is the distance, at every multipole, to six figures.

**Note that (199) is not at fault here.** At $m=2$ the printed identity is exact,
because $\Gamma(2)=1$ — that is finding **G3**. G5 is independent of G3: a factor
dropped between (200) and (201), not an error in the identity used to get there.

**What moves.** (201) sets the large-scale CDM normalisation. Normalising the
amplitude $A$ through the printed form makes it too large by $\Delta\eta_*\approx
1.94$ — not a small correction. Nothing involving a sign or an $\ell$-weight
moves; the $\ell$-dependence of (201) is correct.

**Why it is raised rather than footnoted.** It changes the target of acceptance
criterion **5a**, *"the Sachs–Wolfe limit is recovered over $2\le\ell\le20$ to
5%"*. Comparing a correct reconstruction against the printed (201) would show a
94% discrepancy and read as a failure of the reconstruction.

**Proposed resolution:** criterion 5a's target becomes **(198) itself** — equally
closed-form, and the quantity (201) is a reduction of — with (201) carried in
`provenance/` as a corrected expression. On that target 5a is already met at the
analytic level: the quadrature and the reduction agree to $10^{-5}$.

**Status: raised to P1-T and the PI. Criterion 5a's target awaits confirmation.**

---

## G5 — confirmed independently, 2026-10-05

The obvious objection to G5 is that $\chi$ might be absorbed into the
normalisation of $A$, in which case "correcting" (201) would introduce an error
rather than remove one. **It is not.** The companion equation settles it.

(201) and (204) are reduced the same way from (198), but from **different
definitions of $P(k)$**:

| | $P(k)$ | reduction | at $n=1$ |
|---|---|---|---|
| (201), via (J.1) | $Ak^{n-1}$ | $\int dk\,k^{n-3}j_\ell^2 \to \chi^{2-n}$ | $\chi^1$ — **one factor of $\chi$** |
| (204), via (J.3) | $BT^2(k)k^{n}$, $T=1$ | $\int dk\,k^{n-2}j_\ell^2 \to \chi^{1-n}$ | $\chi^0=1$ — **no $\chi$** |

So (204) is $\chi$-free *as printed and correctly so*, while (201) should carry
one factor. Verified by quadrature at $n=1$: the (J.3) route reproduces
$1/[2\ell(\ell+1)]$ with no distance factor to within $10^{-5}$ at $\ell=2,10,30$.

**The asymmetry is explained by the two appendix definitions of $P(k)$, which
differ by one power of $k$ — not by a units convention in which $\chi=1$.** If
$\chi$ were being set to unity it would have to be absent from both reductions,
and it is not.

**G5 therefore stands.** The printed (201) omits one factor of the comoving
distance.
