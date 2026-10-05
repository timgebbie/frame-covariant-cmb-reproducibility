# $1+3$ covariant CMB anisotropies — analytical reproducibility bundle

**Release v1.0.0 — in preparation.** This tree is the pre-release skeleton: the
layout, licences, provenance discipline and test harness are in place; the
reconstruction itself is being built. Sections marked *specification* describe
what an artefact will contain, not what it currently contains.

- **Associated paper:** Paper 1 (preprint identifier to be assigned)
- **Supplementary materials:** `SUPPLEMENTARY-MATERIAL-v1.0.0.tex`
- **Code licence:** MIT · **Content licence:** CC BY 4.0 (see `CONTENT-LICENSE.md`)

---

## Key figure: angular autocorrelation and residual

*Specification.* Figure **F3** — the recovered almost-Friedmann–Lemaître angular
autocorrelation plotted against its comparison target, with a residual panel
beneath sharing the x-axis. The residual panel is the claim; the overlay is
context. Agreement is stated as a number.

---

## Current situation: v1.0.0

v1.0.0 is an **independent Python reconstruction, from first $1+3$ covariant
principles, of the almost-Friedmann–Lemaître results of**

> T. Gebbie, P. K. S. Dunsby and G. F. R. Ellis, *$1+3$ covariant cosmic
> microwave background anisotropies II: the almost-Friedmann–Lemaître model*,
> **Annals of Physics 282, 321–394 (2000)**, `doi:10.1006/aphy.2000.6034`.

It is written bottom-up. It is not a port of, or a wrapper on, an existing
Boltzmann code, and it inherits no other code's conventions.

**The acceptance spine is Annals II Appendix F, pp. 379–380, Eqs. (F.1)–(F.4)**,
where the covariant mode recursion is matched to external treatments written in
real coefficients. Reproducing that chain is a representation-free test of the
harmonic normalisation, because a basis phase leaking into the coupling
coefficients would break every one of the matches. **That match, figure F1, is
where this bundle's independence lives** — not the spectrum comparison, whose
target descends from the same antecedent.

**The solution is carried with a generic $u^a$.** The explicit frames — the
Newtonian frame $\tilde\sigma_{ab}=0$, in which Annals II itself solves (p. 365),
and the energy frame $q_a=0$ — appear as choices made at the end rather than
assumed at the start. That is the difference the $1+3$ covariant approach buys,
and no gauge-fixed treatment can exhibit it.

Nomenclature is kept strictly separate throughout, following Appendix F:
$\tau_\ell$ are **mode** coefficients, $\tau_{A_\ell}$ are **multipole**
coefficients. The distinction is not made in Bardeen-variable treatments.
Conflating them in code is how a sign is lost. Every released figure plots a
**multipole** mean-square: Annals II p. 366 notes that these hold for general
geometries while the mode mean-squares hold only for almost-Robertson–Walker
ones.

Equation numbers in this bundle are **published** numbers. The published and
arXiv numberings of the Annals papers differ, and not by a constant offset.

## Figure F1 — the Appendix F match

The free-streaming recursion against each external treatment of (F.1)–(F.4), one
panel per treatment. Four comparisons are four panels, not four colours on one
axis. This figure carries the independence of the bundle's cross-check.

## Figure F2 — truncation convergence

One series per $\ell_{\max}$, log y. Annals II Appendix E, pp. 378–379, warns that
truncation in the multipole hierarchy is dangerous even in the
almost-Friedmann–Lemaître case: if any four consecutive harmonics vanish, the
shear must vanish exactly. Run in both frames, because footnote 29 on p. 365
asserts that the Newtonian choice removes the truncation problem — a checkable
claim.

## Figure F3 — angular autocorrelation

Recovered $C_\ell$ against its target, residual panel beneath. The key figure.

## Figure F4 — real-space angular correlation

$C(\theta)$, the basis-free companion to F3.

## Figure F5 — source decomposition, in two frames

The split of §7.1.1, pp. 365–366: the integral solution (176) projects three
sources through $j_\ell$ — the primary Sachs–Wolfe and acoustic term (177),
secondary Doppler during slow decoupling (178), and the integrated, late- and
early-ISW terms (179).

$C_\ell$ is quadratic in the source, so the three pieces **do not add**: the upper
panel carries the three auto-spectra and the total, the lower panel the three
signed cross-spectra. Drawn in two frames, because the split is frame-dependent
while the total is not — which is the covariance argument made quantitative.

## Figure F6 — impact of the approximations

Ratios to the full result: the slow-decoupling order, the diffusion damping
$e^{-(k/k_D)^2}$, and the small-scale cancellation of §7.1.3.

## Figure F7 — frame specialisation

The generic-$u^a$ solution specialised to the Newtonian and energy frames, with
their difference beneath and the dipole shown separately — the dipole is where
the frame lives, and $\ell\ge2$ is where it does not.

## Figure F8 — coupling schematic

Where each coupling sits in the hierarchy. No data; generated by a script like
every other figure.

## Figure sequence

| Figure | Artefact | Evidence category |
|---|---|---|
| **F1** | Appendix F match, small multiples | cross-check |
| **F2** | truncation convergence against $\ell_{\max}$ | diagnostic |
| **F3** | angular autocorrelation with residual panel | acceptance |
| **F4** | real-space angular correlation $C(\theta)$ | acceptance |
| **F5** | source decomposition with cross terms, two frames | acceptance |
| **F6** | impact of the approximations | diagnostic |
| **F7** | frame specialisation | cross-check |
| **F8** | coupling schematic | schematic |

Controls are not evidence and are not released as figures; they live in
`diagnostics/`, with the round-trip residual reported as a number rather than a
chart.

Every figure ships as a versioned PDF/PNG pair in `figures/`. Every caption is
standalone in `captions/` and names the script that produced the figure. The
caption is the specification, not a description; `captions/FIGURE-PLAN-v1.0.0.md`
is the specification for the set.

## Future situation: possible extensions

**These are possible extensions, not claims made by the current release.**

- **v1.5.0** — the high-$\ell$ $O(\varepsilon^2\ell)$ couplings of Paper 1, and
  the restricted case, which must recover v1.0.0's numbers. That makes v1.5.0 a
  recovery and a check rather than a new claim.
- **v2.0.0** — calibration and data-science release, including Planck data.
  *Calibration* there means calibrating the solver against standard results. It
  does **not** mean calibrating the amplitude of an effect.
- **A fractional-contribution form of F5**, each term drawn as its share of
  $C_\ell$ and summing to one by construction — scale-free, so the Sachs–Wolfe
  plateau and the damping tail read equally well.

## Scientific boundary

This is an analytical reproducibility bundle for the associated paper and its
supplement. It is not an empirical calibration, not a parameter-estimation
pipeline, and not a Boltzmann code for general use.

**No new effect is claimed here, and none is reported.** The exact $1+3$
covariant radiation multipole hierarchy contains couplings between the shear
$\sigma_{ab}$ and the temperature multipoles $\tau_{A_\ell}$ whose coefficient
grows linearly in $\ell$. Their $O(\varepsilon^2\ell)$ content is **gravitational
lensing together with observer aberration**, with no residue. Nothing in this
bundle is a detection claim.

Two statements must travel together, and neither stands alone:

- the nonlinear contribution $\delta\tau_{NL}$ **matters** — it is not negligible
  and it is not an artefact; and
- it **adds nothing** — it redistributes power rather than creating it, because
  $\delta\tau^{NL}\propto\Phi\Phi$ makes its contribution to $C_\ell$ quartic in
  $\Phi$ while the linear $C_\ell$ is quadratic.

The bundle reproduces; it does not argue. Any physics claim belongs to the paper,
and no claim appears here that is not in the paper.

## Repository structure

```text
config/                  Accepted scientific and release configurations
functions/               The reconstruction: harmonics, recursion, solution
scripts/                 Active reproduction and verification commands
tests/                   Compact claim-bearing regression suite
data/                    No empirical data are required at v1.0.0
outputs/                 Machine-readable curve and summary evidence
figures/                 Versioned PDF/PNG figure pairs
tables/                  Generated CSV/LaTeX publication tables
captions/                Standalone captions for the selected evidence
diagnostics/             Generated scientific acceptance checks
source/                  Frozen target-paper reference material
provenance/              Theory-to-code traceability and the corrections record
supplementary-materials/ Compiled computational supplement
```

## Installation

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Python 3.13 is the verified interpreter.

## Reproducing the active outputs

```bash
python scripts/run_all.py --strict     # regenerate everything, fail on any drift
python scripts/run_all.py --rerun      # regenerate without the drift gate
```

`--strict` is the release route: it regenerates every output, figure and table,
recomputes the manifests, and fails if any artefact differs from the recorded
hash. `--rerun` is the development route.

```bash
python scripts/make_manifests.py       # regenerate the two SHA256 manifests
python scripts/sync_conventions.py     # regenerate provenance/conventions.md
pytest -q                              # the claim-bearing regression suite
```

## Verification status

**Pre-release.** The acceptance criteria for v1.0.0 are recorded in
`RELEASE-NOTES-v1.0.0.md`; none is yet closed. The harness runs and the seeded
checks pass. Verification counts will be reported here at release.

## Version-control policy

The public version history follows semantic versioning:

```text
v1.0.0        first public analytical reproducibility release — Annals II recovered
v1.0.1        documentation or metadata updates without a scientific change
v1.5.0        compatible scientific extension — high-ell couplings, and the
              restricted case as a recovery and check of v1.0.0
v2.0.0        calibration and data-science release, including Planck data
v3.0.0        incompatible model, interface or scientific-scope change
```

**v1.5.0 must not change v1.0.0's recovered Annals II numbers.** If it does, it
is a breaking change and belongs at v2.0.0. That rule is itself the regression
test.

The development lineage:

| Stage | What it established | Bearing on this bundle |
|---|---|---|
| Correction to astro-ph/9912072 | withdrew the 1999 claim of a new effect | fixes the scientific boundary above |
| Conventions gate C1 | the normative sign and $\ell$-weight sheet | source of `provenance/conventions.md` |
| Paper 1 | the $1+3$ route to lensing from the exact hierarchy | the paper this bundle reproduces |
| v1.5.0, planned | the restricted case | a **recovery and check** of v1.0.0, not a new result |

## Disclosure of AI assistance

The code, tests and documentation in this bundle were written with AI assistance
(Claude, Anthropic). Derivations were checked against the published sources
rather than generated from them, and every finding carries its printed equation
number in `provenance/`. Responsibility for the content rests with the author.

## DOI, citation and license

**Associated paper:** identifier to be assigned.

**DOI:** to be minted on first public release.

**Code:** MIT License, see `LICENSE`.

**Supplementary materials, text, figures and tables:** CC BY 4.0, see
`CONTENT-LICENSE.md`.

Citation metadata is in `CITATION.cff`.
