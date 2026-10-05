# Release notes — v1.0.0

**Status: in preparation. Not released.**

v1.0.0 is the first public analytical reproducibility release: an independent
Python reconstruction, from first $1+3$ covariant principles, of the
almost-Friedmann–Lemaître results of Gebbie, Dunsby & Ellis, *Annals of Physics*
**282**, 321–394 (2000), `doi:10.1006/aphy.2000.6034`.

It is written bottom-up — not a port, not a wrapper — and it is built to find
that paper's remaining errors rather than to agree with it.

## Acceptance criteria

v1.0.0 is complete when all six hold, and not before.

| | Criterion | Status |
|---|---|---|
| 1 | the free-streaming recursion reproduces (F.1)–(F.4), with the external matches of (F.3) and (F.4) checked numerically rather than asserted | **closed** — HS Eq. (6), MB Eqs. (49)/(50) and SZ Eq. (3d) read from their own papers and integrated as printed; they match the bundle to $10^{-13}$–$10^{-14}$ at scale exactly 1. Two distinct normalisations, both matched |
| 2 | a covariant → mode → covariant round trip returns the input to machine precision | **open** |
| 3 | both harmonic phase conventions run end to end; only one reproduces the real, opposite-sign form of the external hierarchies, and the bundle adopts and names that one | **closed** — D1 runs both; the adopted normalisation sits on $j_\ell$ to $10^{-10}$ while the other diverges by $5\times10^{6}$ at $\ell=2$. The adopted convention is named in the supplement, \S2 |
| 4 | a known-wrong control runs and fails in a known shape | **closed** — D1 runs and diverges rather than projecting; the correct recursion matches $j_\ell$ to $10^{-10}$ beside it. Restated: The $\pm(\ell+2)$ control is **withdrawn** to v1.5.0, where that term exists, and replaced by a relative-sign control on the free-streaming bracket (D1). See Q2, closed |
| 5a | the Sachs–Wolfe limit is recovered over $2\le\ell\le20$ to 5%, against the **corrected** closed form of (201) | **open** — target settled; the printed (201) omits one factor of the comoving distance, finding **G5** |
| 5b | the **CDM and ΛCDM** angular power spectra are recovered to a stated tolerance over a stated range, checked against **CMBFAST** | **open** — external target settled; tolerance and range to be set, Q6 |
| 6 | every number the paper prints is regenerated here, or marked not-machine-checkable with the reason | **open** — closes at manuscript freeze. `v1.0.0-rc` is tagged on criteria 1–5; `v1.0.0` requires all six, Q5 closed |

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

- **G1** — Annals I prints $(-1)^\ell$ where its own definition gives $i^\ell$.
  Inconsequential for the covariant multipole, which is invariant under the
  choice; the mode coefficients are not, and the two statements are distinct.
- **G2** — (F.4) is algebraically correct but is not in the Ma & Bertschinger form
  the following sentence identifies it with: the $(2\ell+1)^{-1}$ division its
  text specifies was not applied to the display.
- **G3** — the Bessel identity (199) needs $[(m/2)!]^2$ in its denominator. It is
  exact where $\Gamma(m/2+1)=1$, so (201) is unaffected; (204) is low by 11.4% and
  the $D_\ell$ of (205) correspondingly high by 12.8%.
- **G4** — Appendix F names Wilson & Silk and keys Wilson. Different papers. Open.
- **G5** — (201) omits one factor of the comoving distance $\chi$ from the
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
