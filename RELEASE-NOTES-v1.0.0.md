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
| 1 | the free-streaming recursion reproduces (F.1)–(F.4), with the external matches of (F.3) and (F.4) checked numerically rather than asserted | **open** — chain verified symbolically; external comparison not yet built |
| 2 | a covariant → mode → covariant round trip returns the input to machine precision | **open** |
| 3 | both harmonic phase conventions run, and only one reproduces the real, opposite-sign form of the external hierarchies | **open** — wording change requested, see `provenance/OPEN-QUESTIONS-v1.0.0.md` Q1 |
| 4 | both sign choices of $\pm(\ell+2)$ run, the wrong one growing $\propto\ell$ | **open** — scope question, see Q2 |
| 5 | the almost-Friedmann–Lemaître temperature spectrum is recovered to a stated tolerance | **open** — comparison target unresolved, see Q3 |
| 6 | every number the paper prints is regenerated here, or marked not-machine-checkable with the reason | **open** — depends on manuscript freeze, see Q5 |

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
  the generated conventions copy.

## Findings recorded so far

Two, both in `provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md`.

- **G1** — Annals I prints $(-1)^\ell$ where its own definition gives $i^\ell$.
  Typographical and inconsequential for the covariant multipole; the entry records
  both the slip and why it never produced a wrong result, and distinguishes it
  from the mode-coefficient statement it is easily confused with.
- **G2** — Annals II (F.4) is algebraically correct but is not in the Ma &
  Bertschinger form the following sentence identifies it with; the division the
  prose specifies was not applied to the display. Inconsequential for the physics,
  material for any test harness that compares the two directly.

## Known not to be in v1.0.0

- the high-$\ell$ $O(\varepsilon^2\ell)$ couplings — **v1.5.0**;
- Planck data, likelihoods, any calibration — **v2.0.0**;
- any claim the paper makes. The bundle reproduces; it does not argue.
