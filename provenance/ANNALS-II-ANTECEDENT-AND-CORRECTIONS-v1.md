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

## B-1 — Annals I prints $(-1)^\ell$ where its own definition gives $i^\ell$

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

## B-2 — Annals II (F.4) is not in the form it is immediately identified with

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
| (F.3) → (F.4), substitution of $\beta_\ell=\alpha_\ell^{-1}(2\ell+1)$ | — | exact; see B-2 for the form question |
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

## B-3 — Annals II (199) is correct only at even $m$; (204) and (205) inherit a 12.8% error

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
footnote and this record are the mechanism. **B-3 is therefore corrected silently
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
| †1 | **B-2** — (F.4) requires the $(2\ell+1)^{-1}$ division its prose specifies before it is in the Ma & Bertschinger form | F1 caption; supplement §Acceptance spine |
| †2 | **B-3** — (199) requires $[(m/2)!]^2$; (201) is unaffected, (204) and (205) are not | supplement §Comparison; `diagnostics/ell-range-v1.0.0.txt` |
| †3 | **B-1** — the $(-1)^\ell$ / $i^\ell$ slip in Annals I, inconsequential for the covariant multipole | supplement §Conventions |

---

## B-4 — Appendix F's Wilson citation names one paper and keys another

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
class as **B-2**: harmless to the physics, costly to anyone verifying.

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
| **[81]/[82]** | Wilson (1983) / Wilson & Silk (1981) | pre-arXiv; and see **B-4** — which one is cited is itself unresolved |

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
  (1995), 489, which works from the integral solution. Same class as **B-4**: a
  reader following [39] alone does not find it.
- **MB's arXiv copy numbers its hierarchy (49) and (50)** — the same numbers
  Annals II cites from the published paper. No offset here, unlike the Annals I
  and II case. Recorded because the absence of an offset is as worth knowing as
  its presence.

**Scattering terms dropped.** HS's $-\dot\tau\Theta_\ell$ and SZ's
$-\dot\kappa\Delta_{T\ell}$ are Thomson scattering, not free streaming.

**Wilson remains unread** — pre-arXiv, and **B-4** leaves it ambiguous which paper
is meant. The release states **three** external hierarchies, not four.

---

## B-4 — supporting evidence, 2026-10-05. Still open

The thesis chapter whose published form is *Annals I* opens by stating that the
angular correlation functions are obtained *"following the Wilson-Silk approach
for the mode representation, but derived and dealt with in $1+3$ covariant and
gauge invariant (CGI) form."*

That the mode-representation antecedent is **Wilson \& Silk** supports reading
Appendix F's `[81]` as a typo for `[82]`, which is Wilson \& Silk (1981), rather
than as a naming slip for `[81]`, Wilson (1983).

**This is supporting evidence, not a verification.** Resolving the citation still
requires Eq. (7) of the paper itself, and this bundle does not settle a citation
by inference. **B-4 remains open**, and the release continues to state three
external hierarchies rather than four.

---

## B-5 — Annals II (201) omits the comoving distance from the reduction

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
because $\Gamma(2)=1$ — that is finding **B-3**. B-5 is independent of B-3: a factor
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

## B-5 — confirmed independently, 2026-10-05

The obvious objection to B-5 is that $\chi$ might be absorbed into the
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

**B-5 therefore stands.** The printed (201) omits one factor of the comoving
distance.

---

## B-6 — the thesis abstract and Annals II disagree on a sign in the ISW source (179)

**Status: open. Implemented with the published sign and a switch. Not blocking.**

§7.1.1, p. 366. The integrated source of the temperature anisotropy is printed as

$$S_{\rm ISW}(\eta,k)=V e^{-(k/k_D)^2}\Big[\big[\Phi_A'-\Phi_H'\big](k,\eta)
-aH\big[\tilde\delta_T+3\Phi_A\big](k,\eta)\Big]\tag{179}$$

The thesis abstract carries the same expression with $+aH[\tilde\delta_T+3\Phi_A]$.

**This is not a transcription slip in one of the two.** The published *Annals of
Physics* text and the arXiv preprint `astro-ph/9904408` agree with each other on
the minus sign; the thesis abstract is the outlier, and it is internally
consistent in its own typesetting. Both readings are legible, so the
disagreement cannot be resolved by reading more carefully — only by derivation.

**Why it is not cosmetic.** The second term is not an ordinary
integrated-Sachs–Wolfe contribution. The ISW proper, $\Phi_A'-\Phi_H'$,
*vanishes identically* in a flat matter-dominated background, where the
potentials are constant. The $aH[\tilde\delta_T+3\Phi_A]$ term does not: with
$aH=2/\eta$ in Einstein–de Sitter it survives everywhere the visibility is
non-zero. So the disputed sign governs a term that is the *entire* integrated
contribution in exactly the regime v1.0.0 delivers — standard CDM. It is
asserted as a test that the two readings differ by more than 10% of the source,
so the finding is not moot:
`tests/test_sources.py::test_g6_is_not_a_no_op`.

**How it is carried.** `functions.spectra.sources.source_integrated` takes
`isw_sign`, defaulting to `PUBLISHED_ISW_SIGN = -1.0`. The alternative is
`THESIS_ISW_SIGN = +1.0`. It is not a free parameter: any other value raises.
Published equation numbers and the published reading are the default throughout
this bundle, and a finding does not change that until it is settled.

**What will settle it, and it is not an argument.** Two discriminators, both
available once the $k$-integral of (176) runs end to end:

1. **The large-scale plateau.** On scales well outside the horizon at last
   scattering the CDM spectrum must reduce to the ordinary Sachs–Wolfe result,
   which is (198) and which this bundle already computes independently. Only one
   sign can leave the plateau intact; the other adds a term of the same order
   with a definite sign and tilts it.
2. **The frame statement.** $\tilde\delta_T+3\Phi_A$ is a threading-dependent
   combination, and the total of (176) is not. Recomputing (176) in the Newtonian
   and energy frames and demanding that the *sum* of the three sources be
   invariant is a check the individual terms cannot pass and the total must. Only
   one sign can survive it.

Discriminator 1 is cheap and comes with the v1.0.0 deliverable. Discriminator 2
arrives with the generic-$u^a$ machinery already scheduled for figures F5 and
F7. **B-6 is therefore scheduled to close inside v1.0.0, not deferred past it**,
and it is recorded here now so that the default is on the record before the
number it affects is published.

**No correction is made yet.** Correcting silently requires knowing which way;
here the bundle does not yet, and says so.

---

## B-7 — Annals II (G.3) prints $+\tfrac23\Theta^2$ in the Gauss constraint

**Status: confirmed misprint. The bundle does not inherit it, by construction.**

Appendix G. The $1+3$ Gauss constraint is printed with $+\tfrac23\Theta^2$ where
thesis Ch. 2 and the Cargèse lectures Eq. (55) both carry $-\tfrac23\Theta^2$.

**Raised by Coordination via P1-T, 2026-10-06, with an independent FLRW-limit
derivation. Confirmed here symbolically.** With shear and vorticity switched off,

$${}^3R = 2\mu + 2\Lambda - \tfrac23\Theta^2,$$

and substituting ${}^3R=6K/a^2$, $\Theta=3H$ gives

$$H^2=\frac{\mu+\Lambda}{3}-\frac{K}{a^2},$$

the Friedmann equation. The printed sign gives instead

$$H^2=\frac{K}{a^2}-\frac{\mu+\Lambda}{3},$$

which in the **flat** case is $-(\mu+\Lambda)/3$ — negative for any positive
energy density, so there is no solution. The flat case settles it on its own,
without reference to $K$.

*One note on the algebra, for the record rather than as a correction of
substance.* Coordination's intermediate form was $H^2=-(\mu+\Lambda)/3-K/a^2$;
in the convention used here, ${}^3R=+6K/a^2$ for a closed spatial section, the
curvature term comes out $+K/a^2$. The verdict is identical and does not depend
on it.

**Why the bundle is not exposed.** `functions/background/flrw.py` derives the
expansion law from the covariant energy constraint rather than transcribing
(G.3), which was a decision taken for independence and not in anticipation of
this finding. The corrected sign is therefore what the code already carries. It
is now **pinned**, so that a later well-meaning edit towards the printed equation
fails a test rather than quietly changing the background:
`tests/test_background.py::test_the_gauss_constraint_sign_is_the_corrected_one_and_the_printed_one_has_no_solution`,
with a numerical companion that evaluates the same identity through the code that
actually runs.

**This is the general case, not a lucky one.** B-7 is the third finding (with B-1
and B-6) in which an independently derived quantity disagrees with a printed one.
Deriving rather than transcribing is what makes the reconstruction an audit; a
port would have inherited every one of them silently.

---

## B-4 — closed, 2026-10-06. A mis-named citation, not an ambiguous one

**Status: closed. Misprint in the prose; the key is correct.**

Appendix F, after (F.3), reads:

> "This can be immediately seen to be the same mode equation for $\ell>2$ as in
> Hu & Sugiyama [HS95a] and **Wilson & Silk** [W83] (eqn 7)."

Resolved against the accepted manuscript source. **Both papers are in Annals II's
own bibliography, under different keys**:

| key | entry |
|---|---|
| `W83` | M. L. Wilson, *Ap. J.* **273**, 2 (1983) — **one author** |
| `WS` | M. L. Wilson and J. Silk, *Ap. J.* **243**, 14 (1981) — two authors |

So the text names the 1981 two-author paper while the key points at the 1983
single-author one. **The key is right and the prose is wrong**, on the evidence
of usage: `W83` is cited at eleven places throughout the paper, including every
other reference to this hierarchy, while `WS` is cited exactly once, in the
introduction. Coordination reached the same conclusion independently and adds
that the 1983 paper is paper II, treating negative spatial curvature, and is the
one whose Eq. (7) carries the $\ell>2$ free-streaming mode equation.

**What this changes.** Nothing in the code: the release states three external
hierarchies and reproduces three. What it removes is the *reason* B-4 was open —
there is no longer a question of which paper is meant, and **no library copy is
needed**. ApJ of that vintage is openly readable through NASA ADS, bibcode
`1983ApJ...273....2W`.

**One item does not close with it.** The paper's *title* is not recorded here.
Volume, page and year are confirmed from Annals II's own bibliography; the title
is not, and web access is not available from this environment, so it is left to
be supplied from the ADS record rather than written from memory. It is needed
only if Wilson is ever added as a fourth external check.

---

## B-7 — confirmed verbatim against the accepted manuscript, 2026-10-06

B-7 was recorded on Coordination's report plus a symbolic derivation. It is now
confirmed against the source itself. Appendix G reads:

```latex
The almost-Friedmann-Lema\^{\i}tre Gauss-Codacci relation (Hamiltonian
constraint) is
\begin{equation}
^3 R \simeq 2 \rho + \frac23 \Theta^2\;.
\label{h-constraint}
\end{equation}
```

The label `h-constraint` generates **(G.3)**. The sign is `+\frac23 \Theta^2` as
reported. Note also that no $\Lambda$ appears in the printed constraint, so the
corrected form in the paper's own notation is ${}^3R \simeq 2\rho -
\tfrac23\Theta^2$, reducing to $H^2=\rho/3-K/a^2$. **B-7 stands, now on primary
evidence rather than on report.**

---

## B-2 and B-3 — confirmed verbatim against the accepted manuscript, 2026-10-06

**B-2.** Appendix F, immediately before (F.4), reads "(on first multiplying
through by $(2\ell+1)^{-1}$)", and the display that follows carries
$-(2\ell+1)(\alpha_\ell^{-1}\tau_\ell)'$ on the left — the division is stated in
the prose and absent from the display. Exactly as recorded.

**B-3.** (199) is printed as

```latex
\int_0^{\infty} {dz \over z^m} j_{\ell}^2 (z) = {\pi \over 2^{m+2}}
{m! \over (m/2)!}{ (\ell - \frac{m}{2} - \frac{1}{2} )! \over
(\ell + \frac{m}{2} + \frac{1}{2})!}
```

— a **single** $(m/2)!$ in the denominator where the identity requires
$[(m/2)!]^2$. Exactly as recorded.

Both findings were derived by reimplementation before the source was available.
That they survive contact with it is the point of the method.

---

## B-6 — CLOSED, 2026-10-06. The published sign is derived and correct

**Status: closed. The thesis abstract carries the misprint, not Annals II.**

B-6 was recorded as unresolvable by reading, needing a derivation. It needed no
external derivation: **Annals II derives it itself**, in §5, and the chain
survives checking. Resolved against the accepted manuscript.

**The chain, with the paper's own equation numbers.**

(106) defines the mode coefficient in the Newtonian frame:

$$\tilde{\mathcal B}_1 \approx \frac{k}{a}\big(\delta\tilde T + \Phi_A\big)
\qquad\Longrightarrow\qquad \frac{a\tilde{\mathcal B}_1}{k}=\delta\tilde T+\Phi_A$$

(107) gives its conformal-time derivative:

$$(a\tilde{\mathcal B}_1)' \approx -a^2H\tilde{\mathcal B}_1
+ k(\Phi_A'-\Phi_H') - 2Hak\Phi_A + \tfrac13k^2\tilde\tau_1$$

(108) and (109) connect it to the integral-solution coefficient:

$$-\tilde C_1' - (\kappa'\tilde v_B)' \approx +\tfrac1k(a\tilde{\mathcal B}_1)',
\qquad
-\tilde C_1 \approx \kappa'\tilde v_B + (\delta\tilde T+\Phi_A)$$

Dividing (107) by $k$ and substituting (106) into its **first** term,

$$-\frac{a^2H\tilde{\mathcal B}_1}{k}
= -aH\left(\frac{a\tilde{\mathcal B}_1}{k}\right)
= -aH\big(\delta\tilde T+\Phi_A\big),$$

so (110) reads

$$-\tilde C_1' \approx (\kappa'\tilde v_B)' + \tfrac13k\tilde\tau_1
+ (\Phi_A'-\Phi_H') \underbrace{- aH(\delta\tilde T+\Phi_A) - 2aH\Phi_A}
_{=\;-aH(\delta\tilde T+3\Phi_A)}$$

and the factor of 3 is $1+2$, exactly as (111) and hence (179) print it.

**Why the sign cannot be a misprint in Annals II.** It is *doubly sourced*. The
$-aH(\delta\tilde T+\Phi_A)$ comes from the $-a^2H\tilde{\mathcal B}_1$ term that
the conversion to conformal time produces; the $-2aH\Phi_A$ comes from a separate,
explicitly printed term in (107). A plus sign in (179) would require both to flip
independently, which no single typesetting slip does — and it would also break the
$1+2=3$ that makes (111)'s coefficient come out right. **The published minus is
correct; the thesis abstract is the misprint.**

**One claim of this record's own is corrected.** B-6's first entry said the
disputed term is "the entire integrated contribution" in a matter-dominated
background. Arithmetically that holds — $\Phi'=0$ there, so the ISW proper
vanishes — but it overstated the term's standing. Annals II's **(112)** drops it
explicitly, along with the Doppler and baryon terms, as second order "both in
terms of the scattering time and in the almost-Friedmann–Lemaître sense", in
order to recover the canonical integral solution. So it is the entire *retained*
integrated contribution at the order (176) keeps, and a term the antecedent
itself discards one equation later. Both statements are true and only the pair is
honest. Corrected here rather than quietly amended above.

**What this changes in the code.** Nothing computes differently: the default was
already `PUBLISHED_ISW_SIGN = -1.0`. The switch is **kept**, but it is now a
control rather than an open question — a known-wrong alternative that must change
the answer, which is the kind of thing `diagnostics/` exists for. Its test is
retained and renamed in intent: it demonstrates that the settled sign matters,
rather than that an unsettled one might.

**With this, B-1–B-7 are all closed.**

---

## B-8 — Annals II (181) carries $+R_*\Phi_A$ where (180) gives $-R_*\Phi_A$

**Status: confirmed misprint, corrected silently. Found 2026-10-06 by
reimplementation, confirmed symbolically.**

§7.1.2. (180) gives the acoustic solution at last scattering,

$$\delta\tilde T(\eta,k)+\Phi_A(\eta_*,k)\approx\big[\delta\tilde T(0,k)+(1+R)
\Phi_A(0,k)\big]\cos(kr_s)\;\mathbf{-}\;R\,\Phi_A(\eta_*,k)$$

and (181), the same quantity after the adiabatic substitution
$\delta\tilde T(0,k)\sim\tfrac13\Delta(0,k)\sim-\tfrac23\Phi_A(0,k)$ and
$\Phi_A(\eta_*)\approx\Phi_A(0)$, prints

$$[\delta\tilde T+\Phi_A](\eta_*,k)\approx+\tfrac13\Phi_A(0,k)(1+3R_*)
\cos(kr^*_s)\;\mathbf{+}\;R_*\Phi_A(0,k)\;\sim\;\tfrac13\Phi_A(0,k).$$

**The oscillating parts agree exactly; the constant terms differ by
$2R_*\Phi_A$.** Substituting the adiabatic value into (180) gives
$(\tfrac13+R_*)\Phi_A\cos(kr_s^*)-R_*\Phi_A$, whose oscillating coefficient is
$\tfrac13(1+3R_*)\Phi_A$ — exactly (181)'s. So (181) is (180) with one sign
flipped.

**(181)'s own stated limit settles which is right.** The text takes
$r_s^*\to0$, so $\cos\to1$:

| | value at $\cos(kr_s^*)=1$ |
|---|---|
| as printed, $+R_*$ | $\tfrac13\Phi_A(1+6R_*)$ |
| with $-R_*$ | $\tfrac13\Phi_A$ — **exactly** |

The text asserts the result "$\sim\tfrac13\Phi_A(0,k)$". With the minus sign that
is an identity requiring nothing further. With the plus it holds only if
$R_*\to0$ as well, which is neither stated nor true at last scattering
($R_*\sim0.6$ for the §8.3.2 parameters). **The minus is correct**, and it is
also the form Hu & Sugiyama print.

**Size.** Taken literally the printed (181) overstates the amplitude by
$1+6R_*\approx4.6$, hence $C_\ell$ by a factor of order twenty. It did not
propagate: the text's own next step uses $\tfrac13\Phi_A$, which is the corrected
value, and (196) descends from that. So the printed chain is self-correcting
downstream and **no published number moves**.

**Why it is recorded anyway.** Anyone reimplementing (181) as printed — which is
what this bundle set out to do — gets a normalisation wrong by a factor of
twenty with no indication that anything is amiss, because the result is smooth
and plausible. That is precisely the failure mode this reconstruction exists to
expose. Corrected silently, marked by one footnote, with the forensics here.

Asserted symbolically rather than numerically, so it cannot drift:
`tests/test_acoustic.py::test_b8_equation_181_sign_is_fixed_by_its_own_limit`.

---

## B-4 — the Wilson reference, resolved further, 2026-10-06

Coordination supplied the ADS bibcode and noted that reading Wilson's Eq. (7)
*directly* would make it a genuine fourth source, where quoting it through
Appendix F would not — which is this bundle's own rule applied correctly.

**The scanned paper is reachable.** `articles.adsabs.harvard.edu/pdf/
1983ApJ...273....2W` serves it, where the `ui.adsabs.harvard.edu` record does
not. The **title is confirmed** and can go into the `.bib`:

> M. L. Wilson, *"On the Anisotropy of the Cosmological Background Matter and
> Radiation Distribution. II. The Radiation Anisotropy in Models with Negative
> Spatial Curvature,"* **Ap. J. 273**, 2 (1983).

Coordination's description — paper II, negative spatial curvature — is confirmed
by the title itself.

**Equation (7) is not transcribable from here.** It is on p. 3, and the OCR of
the 1983 scan returns it as

```
Ó₂ = -Töneσ_T Ó₂ - íH - ikT[δ₀ + 1(1 - 3K/k²)δ₃]
```

with the following line, the $\ell>2$ case, as

```
I > 2, ôt= — neffTá, — ikT I ¿I-! + /+ 1 (2/- 1 '',_1' 2/ + 3
```

That second line *appears* to be $\dot\delta_\ell = -n_e\sigma_T\delta_\ell -
ikT[\frac{\ell}{2\ell-1}\delta_{\ell-1} + \frac{\ell+1}{2\ell+3}\delta_{\ell+1}]$
— the $\beta$ normalisation, which is what Annals II claims and what Hu &
Sugiyama Eq. (6) carries.

**It is not added as a fourth source on that basis, and the reason is the
project's own rule.** Reading $(2\ell-1)$ and $(2\ell+3)$ out of `(2/- 1` and
`2/ + 3` is not transcription; it is pattern-matching the garbled text against
the hierarchy this bundle already has, which is reading the expected answer back
out of noise. A fourth check obtained that way would be a *worse* failure than
quoting through Appendix F, because it would look independent and not be.

**What is needed:** a human-legible read of p. 3, Eq. (7). The PDF is openly
available at the URL above; one person looking at it settles it in a minute.
Until then the release continues to state **three** external hierarchies, which
is accurate and blocks nothing. F1's fourth panel waits on that read.

---

## B-4 — CLOSED, 2026-10-06. Wilson read directly; F1 has its fourth panel

The PI supplied the scanned paper. Both halves of B-4 are now settled from
primary sources.

**The citation.** Appendix F's prose names "Wilson & Silk" and keys `W83`, which
the bibliography gives as **M. L. Wilson alone**, *Ap. J.* **273**, 2 (1983) —
title confirmed from the paper itself:

> *"On the Anisotropy of the Cosmological Background Matter and Radiation
> Distribution. II. The Radiation Anisotropy in Models with Negative Spatial
> Curvature."*

Wilson & Silk is the earlier *Ap. J.* **243**, 14 (1981), paper I. **The key is
right and the prose is wrong.**

**Wilson is now a genuine fourth external hierarchy**, read from his own paper
and not through Appendix F, and it is a *stronger* check than a fourth set of
weights would have been. See B-9 for the equation number, and the note below for
why the convention matters.

---

## B-9 — Annals II cites Wilson's Eq. (7); the $\ell>2$ hierarchy is his Eq. (8)

**Status: confirmed misprint. Not load-bearing; recorded for the citation.**

Appendix F: *"the same mode equation for $\ell>2$ as in Hu & Sugiyama [HS95a] and
Wilson & Silk [W83] **(eqn 7)**."* Wilson's numbered equations on pp. 3–4 are

| | |
|---|---|
| (5) | $\dot\delta_0 = -\tfrac13 ikT\delta_1 + \tfrac23\dot h$ |
| (6) | $\dot\delta_1 = -n_e\sigma_T(\delta_1-4v) - ikT[\delta_0 + \tfrac25(1-3K/k^2)\delta_2]$ |
| **(7)** | $\dot\delta_2 = -\tfrac9{10}n_e\sigma_T\delta_2 - \tfrac43\dot H - ikT[\tfrac25\delta_1 + \tfrac37(1-8K/k^2)\delta_3]$ |
| **(8)** | $\ell>2$: $\dot\delta_\ell = -n_e\sigma_T\delta_\ell - ikT\left\{\dfrac{\ell}{2\ell-1}\delta_{\ell-1} + \dfrac{\ell+1}{2\ell+3}\left[1-\dfrac{\ell(\ell+2)K}{k^2}\right]\delta_{\ell+1}\right\}$ |

(7) is the **quadrupole** equation, with its own $\tfrac9{10}n_e\sigma_T$,
$-\tfrac43\dot H$ and the coefficients $\tfrac25$, $\tfrac37$. The $\ell>2$
hierarchy Annals II describes is **(8)**. The citation points one equation early.

**Why it matters only for the citation.** The physics Annals II attributes is
genuinely in Wilson — it is simply at (8). Nothing downstream moves.

---

## Wilson as the fourth source — and why it is the strongest of the four

Wilson's weights are $\ell/(2\ell-1)$ and $(\ell+1)/(2\ell+3)$: the **$\beta$**
normalisation, the same as Hu & Sugiyama and therefore (F.3). The curvature
factor $[1-\ell(\ell+2)K/k^2]$ is also Hu & Sugiyama's, and is unity at $K=0$.

**But he writes it in a different convention**, and that is the interesting part.
Both of his bracket terms carry a **plus**, under an overall $-ikT$, where Hu &
Sugiyama carry opposite signs under a real $k$. The two are related by a phase:

$$\Theta_\ell = i^\ell\delta_\ell$$

turns the same-sign imaginary form into the opposite-sign real form, **exactly**.
Substituting $\delta_\ell=(-i)^\ell\Theta_\ell$ into (8) at $K=0$ gives
$\Theta_\ell' = k[\tfrac{\ell}{2\ell-1}\Theta_{\ell-1} -
\tfrac{\ell+1}{2\ell+3}\Theta_{\ell+1}]$, which is Hu & Sugiyama Eq. (6)
term for term.

So Wilson is not a fourth instance of the same test. **He tests the phase
convention** — the subject of finding B-1 and acceptance criterion 3 — from a
source written before any of the others, in the convention Annals I's own
definition implies. He is integrated **complex and as printed**, and the phase is
removed only afterwards; transforming the equation first would assume the
identity under test. That the result is real to $10^{-10}$ is a separate
assertion from that it agrees.

**Result: $3.1\times10^{-14}$** against a $10^{-11}$ threshold, overall scale
exactly 1. F1 now carries four panels.

Criterion 1 is restated: **four** external hierarchies, in two normalisations and
two phase conventions, each read from its own paper.

---

## B-10 — Annals II (J.5) prints the transfer function with $+1/\nu$

**Status: confirmed misprint, corrected silently. Load-bearing for the matter
power spectrum. Found 2026-10-06 by reimplementation.**

Appendix J. The Bond & Efstathiou parametrised transfer function is printed as

$$T(k)=\Big[1+\big(ak+(bk)^{3/2}+(ck)^2\big)^{\nu}\Big]^{\mathbf{+}1/\nu}$$

with $a=6.4\Gamma^{-1}$, $b=3.0\Gamma^{-1}$, $c=1.7\Gamma^{-1}$ (in $h^{-1}$ Mpc)
and $\nu=1.13$. **The exponent should be $-1/\nu$.**

**As printed it inverts the physics.** A transfer function *suppresses* small
scales: modes entering the horizon during radiation domination stagnate, so
$T\to0$ as $k\to\infty$. With $+1/\nu$ the bracket's $(ck)^{2\nu}$ term dominates
and $T\to(ck)^2$, growing without bound:

| $k$ [Mpc$^{-1}$] | 0.001 | 0.01 | 0.1 | 1 | 10 |
|---|---|---|---|---|---|
| as printed | 1.016 | 1.237 | 5.29 | $1.2\times10^{2}$ | $6.7\times10^{3}$ |
| corrected | 0.985 | 0.808 | 0.189 | $8.2\times10^{-3}$ | $1.5\times10^{-4}$ |

The two are exact reciprocals, which is the cleanest statement of the error.

**Why the text's own check does not catch it.** Appendix J says "the transfer
function $T(k)\sim+1$ on large scales", and that is true of *both* forms: as
$k\to0$ the bracket tends to 1 and $1^{\pm1/\nu}=1$. The large-scale limit cannot
distinguish them. Only the small-scale limit can, and only $-1/\nu$ gives the
$k^{-2}$ falloff that the Bond & Efstathiou form is a fit *to* — verified here as
a log-log slope of $-2.00\pm0.05$ over a decade where $(ck)^2$ dominates, rather
than at a point.

**Size.** Unbounded. There is no regime in which the printed form is usable for
the matter power spectrum; $P(k)\propto T^2$ would rise as $k^4$ at high $k$.

**Where it bites and where it does not.** §8.3.2's $C_\ell$ comparison sets
$T=1$, so the printed (201)/(204) are untouched and **no published number
moves**. It bites the moment the transfer function is actually used, which is
what v1.0.0 does.

Corrected silently; `transfer_function_printed` is kept so the difference is
demonstrable, and `tests/test_transfer.py` asserts both the divergence and the
reciprocal relation.

---

## A note on $\Gamma$, recorded as a parameter and not as a finding

Appendix J says $\Gamma\simeq\Omega_0h$ and then, for $h=0.5$ and
$\Omega_B=0.05$, states $\Gamma=0.48$. For that model $\Omega_0h=0.50$, so the
stated value carries an unnamed baryon correction of about 4%. The standard
corrections of that period, $\Gamma=\Omega_0h\exp[-\Omega_B(1+\sqrt{2h}/\Omega_0)]$,
give $0.452$ — not $0.48$ either.

**This is not recorded as a finding**, because the text says *approximately* and
the $\Gamma$ convention genuinely varied between authors at the time. The
bundle uses the paper's own $0.48$, and `ANNALS_II_GAMMA` carries the discrepancy
in a comment with a test pinning it, so that nobody later "fixes" it to $0.5$ on
the grounds that the text says $\Omega_0h$.


---

## Wilson & Silk 1981 — the fifth source, and a hypothesis falsified

**2026-10-07. Not a finding: a negative result, recorded because it is worth as
much as the positive one would have been.**

Coordination proposed a sharp test. Wilson 1983 Eq. (8) prints the **imaginary,
same-sign** form. If Wilson & Silk 1981 Eq. (7) printed the **real,
opposite-sign** form, then the same first author published in both conventions
two years apart — direct evidence, from one author, that the phase is a
convention and not a fact, arriving from outside this project.

**The scan refutes it.** W&S 1981 Eq. (7), p. 15, read from the PI-supplied scan:

$$\ell>2,\qquad \dot\delta_\ell = -n_e\sigma_T c\,\delta_\ell
- ikTc\left[\frac{\ell}{2\ell-1}\delta_{\ell-1}
+ \frac{\ell+1}{2\ell+3}\delta_{\ell+1}\right]$$

Same weights, same same-sign bracket, same overall $-ikTc$. **Wilson published in
one convention, consistently, twice.** The 1983 paper is the negative-curvature
generalisation — it is the flat equation with $[1-\ell(\ell+2)K/k^2]$ on the
$\delta_{\ell+1}$ term — and the 1981 paper, being spatially flat throughout,
carries no such factor. Paper I flat, paper II curved, exactly as Coordination
described them.

**What it gives.** A **fifth independent source** for the $\ell$-weights, the
earliest of the set, read from its own page and not through Appendix F. And a
*second* source in the imaginary convention, which makes that convention
demonstrably a used one rather than an idiosyncrasy of a single paper.

**What it does not give, and F1 does not pretend otherwise.** At $K=0$ it is
Wilson 1983 Eq. (8) *exactly*. It is therefore **not a fifth numerical check**,
and **F1 keeps four panels**. Drawing an identical curve in a fifth box would
present one check as two, which is the kind of padding this bundle exists to
avoid. The source is credited in the conventions table and in F1's caption; it is
not given a panel it has not earned.

**The cleaner statement the negative result buys.** The convention splits by
**author lineage**, not by paper: Wilson's two papers in the imaginary
convention, Hu \& Sugiyama, Ma \& Bertschinger and Seljak \& Zaldarriaga in the
real one. That is a more useful thing to know than the hypothesis would have
been, and it is consistent with *Annals II* naming the $i^{-\ell}$ relation
against Wilson specifically.

---

## Lineage note L-1 — Pitrou's correction to MGE99 (60), and why it is not live at v1.0.0

**Not a B-finding.** There is no defect in *Annals II* here. This is a published
correction to a *different* paper in the lineage, recorded because v1.5.0 and
v2.0.0 go where it bites and v1.0.0 does not. Raised by Coordination from P1-T,
2026-10-07.

**The correction.** Pitrou, *Class. Quantum Grav.* **26**, 065006 (2009), §7.5,
p. 39, corrects Maartens, Gebbie & Ellis, *Phys. Rev. D* **59**, 083506 (1999),
Eq. (60): a missing factor 6. It carries the $-3$ before $\rho_R v_B^av_B^b$ in
(63) to $-7$, and the $I_\emptyset v^{a_1}v^{a_2}$ coefficient in the collision
multipoles from 3 to 7. It is a **second-order Thomson collision term**, arising
from the change to the baryon frame.

### Does *Annals II* reproduce MGE99 (60)? **No.**

Asked by Coordination, and answered from the source rather than assumed.
*Annals II* cites MGE99 at eight places — lines 165, 179, 183, 243, 247, 252,
262, 319 — for the **nonlinear framework**, never for the collision term. Its own
collision term is printed at (68):

```latex
C[x,e] \approx \dot{\kappa} (e^a v_a^B - \tau)
```

**That is linear in $v_B$.** There is no $v_B^av_B^b$ term anywhere in it, so
there is nothing for the factor 6 to be missing from. *Annals II* takes MGE99's
exact framework and then linearises the scattering, which is what its `$\approx$`
denotes — equality "to at least O[1] in the almost-Friedmann–Lemaître sense", by
its own convention statement.

### Consequence, stated rather than assumed

| release | reaches a second-order collision term? | exposed to L-1? |
|---|---|---|
| **v1.0.0** | **no** — (68) is linear in $v_B$ and the target is almost-FLRW | **no** |
| **v1.5.0** | **yes** — decision S2 carries the nonlinear-Thomson coupling $\dot{\delta C}_{NL}$, which is this territory | **yes** |
| **v2.0.0** | yes, inherited from v1.5.0 | **yes** |

**v1.0.0 is not exposed, and that is checked rather than believed.** The
implemented collision term is the one in `functions/spectra/sources.py`, whose
scattering enters only through $\kappa'v_B$ and $(\kappa'\tilde v_B)'$ — linear
in $v_B$ throughout, as (177) and (178) print it.

**v1.5.0 must adopt the corrected coefficients from the outset.** When
$\dot{\delta C}_{NL}$ is implemented it should be built on Pitrou's corrected
MGE99 (60), **not** on (60) as printed — and the first thing to check there is
whether the $-7$ and the coefficient 7 reproduce from the baryon-frame change
independently, since this bundle's standing method is to derive rather than
transcribe. Flagged here so that the v1.5.0 stream meets it before writing code
rather than after.
