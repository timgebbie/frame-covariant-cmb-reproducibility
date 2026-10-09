# Release notes — v1.0.0

**Status: in preparation. Not released.**

v1.0.0 is the first public analytical reproducibility release: an independent
Python reconstruction, from first $1+3$ covariant principles, of the
almost-Friedmann–Lemaître results of Gebbie, Dunsby & Ellis, *Annals of Physics*
**282**, 321–394 (2000), `doi:10.1006/aphy.2000.6034`.

It is written bottom-up — not a port, not a wrapper — and it is built to find
that paper's remaining errors rather than to agree with it.

## Acceptance criteria

v1.0.0 is complete when criteria **1, 2, 3, 4, 5a and 6** hold, and not before.

**Criterion 5b is v1.2.0**, by decision S18 and the PI's acceptance of
2026-10-09. It compares the spectra against CAMB and CLASS, which requires
Peebles recombination and the acoustic peaks — content an almost-Friedmann–
Lemaître release does not contain. Deferring it is a **scope decision taken in
advance, not a criterion waived at the end**, and the distinction is the whole
of the difference: `tests/test_external_codes.py` fails if these notes ever
claim 5b is closed while CAMB and CLASS are absent, so the deferral cannot
quietly become a pass.

The earlier wording — *"complete when all six hold"* — was left standing after
S18 moved 5b, which made v1.0.0 unclosable under its own acceptance. It was
blocked by arithmetic rather than by physics for two days.

| | Criterion | Status |
|---|---|---|
| 1 | the free-streaming recursion reproduces (F.1)–(F.4), with the external matches of (F.3) and (F.4) checked numerically rather than asserted | **closed** — HS Eq. (6), **Wilson Eq. (8)**, MB Eqs. (49)/(50) and SZ Eq. (3d), each read from its own paper and integrated as printed; all match the bundle to $10^{-13}$–$10^{-14}$ at scale exactly 1. **Five** sources — Wilson \& Silk 1981 Eq. (7) is the earliest, read from its own page, and at $K=0$ is Wilson 1983 Eq. (8) exactly, so it is credited and **not drawn**: four panels, four independent numerical checks. Two normalisations *and* two phase conventions — Wilson is written in the imaginary convention and tests the phase, not only the $\ell$-weights |
| 2 | a covariant → mode → covariant round trip returns the input to machine precision | **CLOSED 2026-10-09.** The residual is not small, it is **identically zero in exact symbolic arithmetic**: $\tilde{\mathcal B}_1-(\mathcal B_1+\dot v_a)=[0,0,0]$, S14's target met with no shear and no $Hv$. The cancellation is **exhibited rather than asserted** — the gradient half carries $-Hv_a$ through $v_a\dot{\overline{\ln T}}$ in the moving projector, the acceleration half $+Hv_a$ through $\tfrac13\Theta$ in $v^b\nabla_bu_a$, and it is the *same* $H$ twice. $\sigma_{ab}v^b$ and $\epsilon_{abc}v^b\omega^c$ are formed **in full** and leave at $O(\varepsilon^2)$ by series expansion rather than by hand, so "no shear" is a statement about order that sympy checks. `functions/frames.py`, `tests/test_frames.py`, D2 |
| 3 | both harmonic phase conventions run end to end; the convention is fixed by the **definition** of $Q_{A_\ell}$, and the external match then confirms it | **CLOSED 2026-10-07**, on `conventions.md` **C3.2** — marked DEF and seed-verified against the GE98 PDF: $Q_{A_\ell}=(-k_{\rm phys})^{-\ell}\mathrm D_{\langle A_\ell\rangle}Q$, the stripped factor **real, no $i$**. A real stripped factor forces $c^2=+1$ and the opposite-sign bracket. **C3a.3** then derives $Q_{A_\ell}=i^\ell O^{(k)}_{A_\ell}Q$, and *Annals II* independently states its form sits at $i^{-\ell}$ from Wilson's plane-wave basis — two derivations of the same phase, measured at $3.1\times10^{-14}$ with the transformed solution real to $10^{-10}$. The earlier wording was circular and was **reopened 2026-10-06** before this closed it; see Q1 |
| 4 | a known-wrong control runs and fails in a known shape | **closed** — D1 runs and diverges rather than projecting; the correct recursion matches $j_\ell$ to $10^{-10}$ beside it. Restated: The $\pm(\ell+2)$ control is **withdrawn** to v1.5.0, where that term exists, and replaced by a relative-sign control on the free-streaming bracket (D1). See Q2, closed |
| 5a | the Sachs–Wolfe limit is recovered over $2\le\ell\le20$ to 5%, against the **corrected** closed form of (201) | **CLOSED 2026-10-09** at **0.27%**, twenty times inside tolerance. D5 compares the **pipeline's own** $C_\ell$ — the same code that draws F3, with the Doppler and integrated terms switched off rather than reimplemented — against `cl_large_scale_reduced`. The comparison required translating one power of $k$ between *Annals II*'s primordial convention and this bundle's; untranslated it reports 835%, and the translation is recorded in `provenance/`. **D5 also states what it cannot do**: the corrected and printed forms differ by $\chi^{2-n}$, which is $\ell$-independent and cancels in the shape normalisation, so 5a is not evidence for B-5 — that rests on the absolute quadrature comparison |
| 5b | the **CDM and ΛCDM** angular power spectra recovered to a **measured** tolerance over three stated $\ell$ bands, checked against **CAMB and CLASS** | **MOVED to v1.2.0** — decision S18, accepted by the PI 2026-10-09. It needs Peebles recombination and the acoustic peaks, which this release does not contain; a criterion that cannot be met by the content of the release it gates is a scope error, not an open item. The tolerance remains **measured** — the CAMB–CLASS mutual difference is the floor — and `tests/test_external_codes.py` fails if these notes ever claim 5b closed while the codes are absent |
| 6 | every number the paper prints is regenerated here, or marked not-machine-checkable with the reason | **open** — closes at manuscript freeze. `v1.0.0-rc` is tagged on criteria 1–5; `v1.0.0` requires all six, Q5 closed |

### Release mechanics

Not scientific claims. A release fails on any of them, and each is decidable
from a command rather than from a judgement.

| | Gate | The test that decides it | Status |
|---|---|---|---|
| **R1** | the harness is clean | `python scripts/run_all.py --strict` → `CLEAN` | **GO** |
| **R2** | the acceptance runs on the **released tree**, not a working folder | `python scripts/check_clean_checkout.py` → `PASS`. Extracts `git archive HEAD` and runs the gates inside it — no `.git`, no untracked files, no build products, which is what a reader receives | **GO** |
| **R3** | the supplement is built **by the harness** | `python scripts/build_supplement.py` → 0 LaTeX errors, worst overfull ≤ 35pt. It was the one released artefact nothing here generated, which is how **T-7** put 55mm of text past the margin of a shipped PDF | **GO** |
| **R4** | F3 claims only what it has | published over its measured range, caption naming the binding limit **and the tolerance** — at 5% the formalism binds, at 1% the numerics do | **GO** |
| **R5** | the README follows the house layout | `tests/test_house_grammar.py`. The form follows `correlation-emergence-reproducibility`: supplement referenced below the title, `Item`/`Value` licence table, house section order, and every relative link resolving | **GO** |

**R2 is the one that generalises the others.** T-1, T-6 and T-8 were each a
version of the same mistake — treating the working directory as the thing being
released — and each was invisible to a gate that measured something adjacent to
the question. R2 asks the question directly.

## What is in this tree now

- the house layout, root files and licences — MIT for code, CC BY 4.0 for
  supplement, text, figures and tables;
- `provenance/` with the corrections record and the open specification questions;
- `functions/harmonics/weights.py` — the PSTF weights $\beta_\ell$,
  $\alpha_\ell$, $\Delta_\ell$ and the (F.1) free-streaming weight, as **exact
  rationals**, each cited to a published equation number;
- `tests/test_appendix_f_chain.py` — eleven checks, all passing: the
  $\beta_\ell$ recurrences at general $\ell$, the (F.1) → (F.2) → (F.3) → (F.4)
  chain, the adjointness of the hierarchy and the mode recursion, and the two
  rephasing statements;
- `scripts/` — the strict and rerun routes, manifest generation and checking, and
  the generated conventions copy;
- `captions/FIGURE-PLAN-v1.0.0.md` — the agreed specification for the figure set.

## The figure set

Agreed with the PI on 2026-10-05 and specified in `captions/FIGURE-PLAN-v1.0.0.md`.
Eight released figures: **F1** the Appendix F match, which is where the bundle's
independence lives; **F2** truncation convergence, run in both frames because
Annals II footnote 29 on p. 365 makes a checkable claim about it; **F3** the
angular autocorrelation with a residual panel, the key figure; **F4** the
real-space $C(\theta)$; **F5** the source decomposition of §7.1.1 with its three
auto- and three cross-spectra, drawn in two frames because the split is
frame-dependent while the total is not; **F6** the impact of the approximations;
**F7** frame specialisation from a generic $u^a$; **F8** the coupling schematic.

Four diagnostics are **not** released as figures, because a control is not
evidence: the relative-sign control, the round-trip residual as a number, the
source terms plotted directly, and the no-monopole check.

The palette was **re-validated** against the house surfaces rather than inherited
— worst adjacent CVD $\Delta E$ 9.1 light and 8.4 dark, normal-vision 22.9 and
19.8 — and the two light-mode slots below 3:1 contrast are confirmed, so the
direct-label rule is load-bearing rather than decorative.

## Findings recorded so far

Five, all in `provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md`.

- **B-1** — Annals I prints $(-1)^\ell$ where its own definition gives $i^\ell$.
  Inconsequential for the covariant multipole, which is invariant under the
  choice; the mode coefficients are not, and the two statements are distinct.
- **B-2** — (F.4) is algebraically correct but is not in the Ma & Bertschinger form
  the following sentence identifies it with: the $(2\ell+1)^{-1}$ division its
  text specifies was not applied to the display.
- **B-3** — the Bessel identity (199) needs $[(m/2)!]^2$ in its denominator. It is
  exact where $\Gamma(m/2+1)=1$, so (201) is unaffected; (204) is low by 11.4% and
  the $D_\ell$ of (205) correspondingly high by 12.8%.
- **B-4** — Appendix F names Wilson & Silk and keys Wilson. Different papers. Open.
- **B-5** — (201) omits one factor of the comoving distance $\chi$ from the
  reduction of (200). Confirmed independently: (204) descends from a $P(k)$
  definition differing by one power of $k$ and is correctly $\chi$-free, so the
  asymmetry is not a units convention. Sets criterion 5a's target.

All are **corrected silently in the reconstruction and marked by a succinct
footnote** in the supplement and in any affected caption; the full forensics stay
in `provenance/`. Where a finding moves an acceptance criterion, the corrected
target is recorded and adopted rather than blocking the work.

## Known not to be in v1.0.0

- the high-$\ell$ $O(\varepsilon^2\ell)$ effects and **both** nonlinear
  corrections, gravitational and nonlinear-Thomson — **v1.5.0**, gated on Paper 1;
- Planck data, likelihoods, any calibration — **v2.0.0**;
- any external code check other than **CMBFAST**, deliberately, to avoid scope
  creep;
- any claim the paper makes. The bundle reproduces; it does not argue.
