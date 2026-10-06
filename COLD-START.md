# Cold start — pick this up after a break

**Last updated 2026-10-06.** Read this first, then `README.md`. If you are a new
session, read `provenance/DECISIONS-v1.0.0.md` before changing anything: it is
the record of what has been **accepted**, and it is not reopened without a new
decision.

---

## What this is, in one paragraph

An independent Python reconstruction, from first $1+3$ covariant principles, of
the almost-Friedmann–Lemaître results of **Annals II** — Gebbie, Dunsby & Ellis,
*Annals of Physics* **282**, 321–394 (2000). It is a Boltzmann code written from
scratch, deliberately: wrapping an existing one would import the harmonic
normalisation it is supposed to test. It reproduces; it does not argue.

**v1.0.0's deliverable** is the CDM and ΛCDM angular power spectra in the
almost-FLRW formulation: **Eq. (186) computed from Eq. (176)**, by the mode route
and by the covariant route of (187)+(188), which are proven identical.

## Where things stand

| | |
|---|---|
| Acceptance criteria | **1, 3, 4 closed**; 2, 5a, 5b, 6 open |
| Findings against the antecedent | **six**, G1–G6, in `provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md`. G4 and G6 open |
| Figures | 1 of 8 (**F1**, the Appendix F match) |
| Diagnostics | 1 of 4 (**D1**, the relative-sign control) |
| Tests | 131 passing, 2 skipped |
| Archive | DOI `10.25375/uct.34069509` reserved on ZivaHub, MIT, **private draft, not published** |

**What is already proven, and need not be redone.** The Appendix F chain closes
numerically against three external hierarchies read from their own papers, in two
distinct normalisations, at $10^{-13}$–$10^{-14}$. $\alpha_\ell^{-1}\tau_\ell =
j_\ell(k_{\rm com}\Delta\eta)$ to $10^{-10}$. The mode and covariant routes to
$C_\ell$ are identical exactly. The numerical strategy — route 3, the hybrid — is
built and cross-verified both ways.

## How to run it

```powershell
cd C:\Users\01404122\Documents\Claude\NonlinearShear-bundle
python -m venv .venv ; .venv\Scripts\Activate.ps1 ; pip install -r requirements.txt
python scripts\run_all.py --rerun     # expect CLEAN
pytest -q                             # expect 100 passed, 2 skipped
```

`--strict` is the release route and will report *NOT RELEASABLE* until the
pending figures and diagnostics exist. That is correct, not a fault.

**PowerShell 5.1 has no `&&`** — use `;`.

## The rules that actually bite

1. **Equation numbers are published numbers.** Editions differ, and not by a
   constant offset. Where an edition agrees, that is recorded too.
2. **Independent checks are counted by their sources, not their arguments.** A
   coefficient read through a secondary source *is* that secondary source.
3. **Corrections are silent, marked by one footnote**, the word *misprint* not
   *error*. Forensics stay in `provenance/`. Where a finding moves an acceptance
   criterion, adopt the corrected target and record why — do not block.
4. **Be faithful to the $1+3$ approach.** Carry a generic $u^a$; specialise to a
   frame at the end, never at the start.
5. **Plot multipole mean-squares, never mode mean-squares.**
6. **A control is not evidence** — controls live in `diagnostics/`.
7. **Never a bare `k`** in the code: `k_com` and `k_phys` differ by $a$, and
   Appendix F's `k` is comoving while the conventions sheet's is physical.
8. The PI owns git. Development happens in the cloud; the tree is written to disk
   and the PI commits named files, never `git add -A`.

## What to do next, in order

1. ~~The source terms (177)–(179) and the integral solution (176).~~ **Done** —
   `functions/spectra/sources.py`, with the background derived from the $1+3$
   constraint in `functions/background/flrw.py` rather than transcribed. (176)
   returns $\alpha_\ell^{-1}\tau_\ell$, and is checked against the free-streaming
   projection of `functions/harmonics/` — the two halves of the code now test
   each other. The ISW sign is **G6**, open, carried as a switch.
2. **Tight coupling** (180)–(182), which supplies $\delta T$ and $\tilde\tau_1$
   at last scattering — and the visibility $V$, $\kappa'$ and $k_D$ that
   `sources.py` deliberately does not manufacture for itself.
3. **The matter power spectrum and transfer function**, §8.1 and (J.1)/(J.3).
4. **The $k$-integral of (186)** and its covariant twin through (187)+(188).
   That is the deliverable, and figure **F3**, which becomes the key figure.
5. **ΛCDM**, via the expansion law (185) and the late-ISW term already in (179).
6. **F2** (truncation convergence in both frames), then the generic-$u^a$
   machinery, which unlocks **F5**, **F7** and criterion 2's round trip.

## Decisions still outstanding

| | |
|---|---|
| **G4** | Appendix F names Wilson & Silk and keys Wilson — different papers. Pre-arXiv; needs a library copy. Not blocking; the release states three external hierarchies, not four |
| **G6** | the thesis abstract and Annals II disagree on a sign in (179). Implemented with the published sign and a switch. **Scheduled to close inside v1.0.0**: the large-scale plateau discriminates it, and the two-frame invariance of (176) discriminates it again |
| **5b** | tolerance and $\ell$ range against CMBFAST. The external target is settled; the numbers are not |
| — | dark-mode figure variants: proposed as *only when a screen deliverable exists*. Unanswered |
| — | an `algorithm-layout-v1.0.0.tex` to match the exemplar's preamble exactly. Offered, unanswered |
| — | **Paper 1's title and arXiv identifier** — placeholders in `README.md` and `CITATION.cff` |

## Where everything is

```text
provenance/DECISIONS-v1.0.0.md      what has been ACCEPTED — read before changing anything
provenance/ANNALS-II-...-v1.md      the findings record, append-only
provenance/OPEN-QUESTIONS-v1.0.0.md the specification questions and their status
config/implementation-register.toml equation -> provenance -> .py file -> test
captions/FIGURE-PLAN-v1.0.0.md      the agreed figure set and the visual grammar
RELEASE-NOTES-v1.0.0.md             the acceptance criteria and their status
```

The register's `PENDING` rows are the work plan: they are exactly the equations
not yet implemented.

## Context that is not in the repository

v1.5.0 is the high-$\ell$ effects, carries **both** nonlinear corrections — the
gravitational $\delta\dot\tau_{NL}$ and the nonlinear-Thomson $\dot{\delta
C}_{NL}$ — and is **gated on Paper 1**, which the P1-T stream is writing.
v2.0.0 is calibration and data science.

This stream owns the bundle repository at v1.x and does not write to
`NonlinearShear` at all. `docs/STREAMS.md` and `docs/RESUME.md` there belong to
Coordination: send rows, never write them.
