# 1+3 covariant CMB anisotropies reproducibility bundle

Version: **v1.2.0-dev** — the full linear spectrum with the acoustic peaks and
the Silk damping tail (F9), in both frames; the integral solution (102) carried
with a generic 4-velocity and specialised back; acceptance criterion 5b closed.
**Last release: v1.1.0** — Peebles recombination and the frame specialisation
made numerical.

Supplementary code and materials for: Tim Gebbie, *"Frame covariance of CMB
lensing in the exact $1+3$ covariant radiation hierarchy,"* arXiv: identifier
assigned on submission.

The supplementary-materials document is included here:

> [supplement-v1.0.0.pdf](supplementary-materials/supplement-v1.0.0.pdf)

Built from `SUPPLEMENTARY-MATERIAL-v1.0.0.tex` by `scripts/build_supplement.py`.
It carries the scope, the theory-to-computation map, the acceptance spine, the
conventions and translations tables, and the interpretive limits — read it
before the code if you want to know what this release does and does not claim.

## Key figure: the angular spectrum with the acoustic peaks

![F9 — the normalised angular spectrum for CDM, ΛCDM and the Planck 2018 set, with the acoustic peaks, against CAMB and CLASS as context](figures/f9-acoustic-spectrum-v1.2.0.png)

**This is the release where the spectrum stops being the almost-Friedmann–
Lemaître analytic skeleton.** **Panel (a)** is the deliverable: shape, $D_\ell$
renormalised at $\ell=30$, for the three backgrounds this bundle ships — CDM (Einstein–de Sitter), ΛCDM, and the
stamped Planck 2018 set with a derived photon-only radiation era. The peaks and
the damping tail come from *Annals II*'s own equations: the integral
solution (102) with the Bond–Efstathiou transfer function driving the
oscillation per mode, and the diffusion scale from **(dif-damp-correct)** at
$f_2=3/4$ — the antecedent's own corrected coefficient, not a departure from it
(**T-43**).

**CAMB and CLASS are drawn dashed, and they are context rather than a target**
(**S4c**). Criterion 5b is gated on this bundle's own pipeline, (102) against
(177)–(179), which agree to $9.5\times10^{-6}$ against a gate of $10^{-3}$.
The distance to the external codes is large, expected, and **itemised rather
than totalled**: 97.8% across the plateau, 137% across the peaks, of which the
damping coefficient alone is 17.2%, the rest attributable to the
slow-decoupling order and the visibility weight (102) carries. The first peak
sits at $\ell\simeq170$ here against 198 in both codes, consistent with
$z_*=1114.5$ against 1088.5. The itemisation is in
`provenance/CRITERION-5B-v1.md`; the derivations are in the supplement.

**Panel (b) draws the same spectra in both frames, and it is the panel a
gauge-fixed treatment cannot produce.** Both come from *one* solve: (102) is
carried with a generic $u^a$ and the frame is chosen at the end, so the
Newtonian and CDM curves are two projections of the same coefficients rather
than two calculations. **This shows that** the frame is a choice made at the
end of the derivation and not an assumption built into its start — which is the
claim the $1+3$ covariant approach exists to make, drawn here rather than
asserted.

## Second figure: the angular power spectrum by two routes

![F3 — the angular power spectrum of Annals II (186), computed by the mode route and by the covariant route](figures/f3-angular-spectrum-v1.0.0.png)

Eq. (186) computed from Eq. (176) by the **mode route** and the **covariant
route**, agreeing exactly because they are one calculation written twice. This
is the almost-Friedmann–Lemaître skeleton: no transfer function, no acoustic
modulation, claimed only over $2\le\ell\le20$ — a range **derived** rather than
chosen (`scripts/derive_ell_range.py`). Read beside F9 it is the progression in
one glance.

## Third figure: the Appendix F match

![F1 — the covariant free-streaming recursion against four external hierarchies](figures/f1-appendix-f-v1.0.0.png)

The covariant free-streaming recursion of *Annals II* Appendix F against **Hu &
Sugiyama** Eq. (6), **Wilson** Eq. (8), **Ma & Bertschinger** Eqs. (49)/(50) and
**Seljak & Zaldarriaga** Eq. (3d), each read from its own paper and integrated
as printed. Residuals of $10^{-13}$–$10^{-14}$ against a $10^{-11}$
threshold, at overall scale exactly 1. Four independent checks in **two
normalisations and two phase conventions** — Wilson is written in the imaginary
convention and so tests the phase, not only the $\ell$-weights. This is the
bundle's strongest single piece of evidence and it has held unchanged across
all three releases.

## Current situation: v1.2.0-dev

This bundle is an **independent Python reconstruction, from first 1+3 covariant
principles, of the almost-Friedmann–Lemaître results of** T. Gebbie,
P. K. S. Dunsby and G. F. R. Ellis, *1+3 covariant cosmic microwave background
anisotropies II: the almost-Friedmann–Lemaître model*, **Annals of Physics 282,
321–394 (2000)**, [doi:10.1006/aphy.2000.6034](https://doi.org/10.1006/aphy.2000.6034).

It is written bottom-up. It is not a port of, or a wrapper on, an existing
Boltzmann code, and it inherits no other code's conventions.

**Derived, not transcribed**, wherever the antecedent prints a result that can be
obtained instead. The FLRW background is integrated from the 1+3 energy
constraint, so Eqs. (185) and (G.3) are **checks on this bundle rather than
sources for it** — three of the fourteen recorded findings are disagreements between a
derived quantity and a printed one, and a port would have inherited all three
silently. The exceptions are stated where they occur: recombination rests on an
imported atomic-physics fit, and `functions/spectra/peebles.py` tabulates what is
derived there and what is not.

**Three releases, latest first**, each with the figure that carries it.

| | what it established | its figure |
|---|---|---|
| **v1.2.0** | the spectrum **with structure in it**: the full linear $C_\ell$ — acoustic peaks, Silk damping, the complete source assembly, and (102) carried with a generic $u^a$ and specialised back. Criterion 5b closes | **F9**, immediately below |
| **v1.1.0** | the recombination that **makes peaks possible**: Peebles' effective three-level atom replacing equilibrium Saha and made the default (**S22**). The visibility peak moves $z\simeq1300\to1107$ against a standard 1080–1100, and the function widens by about 40% — and the width is what sets the Silk damping envelope | **F6**, *what each approximation is worth* |
| **v1.0.0** | the reconstruction is **faithful**: the free-streaming chain of Appendix F reproduced against **four external hierarchies**, in four conventions and two normalisations, at $10^{-13}$–$10^{-14}$ — and the almost-Friedmann–Lemaître spectrum by two independent routes | **F1**, below |

### Release status: where v1.2.0 stands

**A milestone gate, so the state is stated rather than implied.** Every number
below is generated by the harness; this table says *where*, so that reading it
and reading the tree cannot disagree.

| | state | recorded in |
|---|---|---|
| acceptance criteria | **6 of 6 closed** — 5b gated by **S4c** on (102) against (177)–(179) | `RELEASE-NOTES-v1.2.0.md` |
| artefact maturity (**S27**) | shipped / release-candidate / proof-of-concept / prototype, each rung **verified rather than declared** | `provenance/RELEASE-STATUS-v1.md` |
| outstanding release gate | **none** | same |
| stated limit shipped with it | the recombination grid, **1.2%**, which 5b cannot bound | **Q7**, **S33** |
| discretisations | **all** registered; the generator fails on one it does not name | `provenance/GRID-REGISTER-v1.md` |
| external comparison | recorded, reproducible without CAMB or CLASS, **outside** the bundled testing | `tables/criterion-5b-v1.2.0.tex` |
| findings against the antecedent | **B-1 … B-14** | `provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` |
| findings against this bundle | **T-1 … T-48** | `provenance/BUNDLE-DEFECTS-v1.md` |
| decisions | **S1 … S35**, with the withdrawn ones struck rather than deleted | `provenance/DECISIONS-v1.0.0.md` |

**This shows that** the release closes on evidence that regenerates, not on a
claim typed once: the only way to change a number above is to change the code
that produces it and re-run the harness, which is the property the whole
`provenance/` tree exists to buy.

### Compute cost: what one spectrum takes

**Measured, not estimated** — `scripts/benchmark_single_run.py`, one angular
correlation function from all the physics at a fixed parameter set, excluding
the tests, the figures and the manifests. Those measure what it costs to
*check* the bundle, which is a different question from what it costs to *run*
it.

*Snapshot: CPython 3.13 on Linux x86_64, numpy 2.5, 2026-10-15; 39 multipoles
to $\ell=990$, 1433 modes to $k=1500$, `PLANCK_MODEL`. A benchmark is a
property of a machine, so this is dated and labelled rather than asserted;
re-run the script anywhere to replace it.*

| stage | seconds | share | why |
|---|---:|---:|---|
| background | 0.05 | 0.0% | adaptive quadrature per panel; independent of $k$ and $\ell$ |
| recombination history | 0.31 | 0.1% | one stiff Radau solve, then the visibility and opacity |
| environment and transfer function | 0.44 | 0.1% | the $\eta$ grid, the potentials, the Bond–Efstathiou shape |
| Bessel table | 6.85 | 1.5% | $j_\ell(x)$ tabulated **once** and reused by every mode |
| **per-mode loop** | **452.47** | **98.3%** | the acoustic solve and the line-of-sight projection, once per $k$ |
| &nbsp;&nbsp;*of which* coefficients | *239.22* | *52.0%* | solving (152)/(153) and assembling $C_0,C_1,C_2$ |
| &nbsp;&nbsp;*of which* projection | *213.24* | *46.3%* | $\int\mathrm d\eta$ against $j_\ell$ for every $\ell$ |
| primordial power | 0.00 | 0.0% | $P(k)\sim k^{n_s-4}$, one array |
| $k$ quadrature to $C_\ell$ | 0.01 | 0.0% | one integral per multipole against the stored transfer |
| $C_\ell\to C(\theta)$ | 0.01 | 0.0% | Legendre sum at 721 angles |
| **TOTAL** | **460.13** | **100%** | **316 ms per mode, over 1433 modes** |

**This shows that the cost is in one place, and that the place is not where a
reader would guess.** Recombination — the physics that took a release to get
right — is 0.1%. The deliverable the reader actually asked for, $C(\theta)$, is
0.01 seconds. **Everything is the per-mode loop**, split almost evenly between
solving the oscillator and projecting it along the line of sight, and it is
linear in the number of modes because each mode is independent.

**What it means for v1.5.0.** It is the measurement decision **S24** was argued
on, now broken down: $A_s$ and $n_s$ enter *only* the last two rows, which cost
$0.01$ s against the $452$ s above them. A sampler that re-runs the whole chain
per proposal pays four hundred times for something it could store — which is
why the v1.5.0 interface must expose $T_\ell(k)$ and its grid as a first-class
product rather than only $C_\ell(\theta)$. **This table is the argument, not an
illustration of it.**

**What it does not license.** Decision **S30** defers run-time optimisation to a
dedicated assessment for v2.0.0, and nothing here overrides that: the loop is
embarrassingly parallel and obviously so, and that is precisely why tuning it
now — before the handover this benchmark exists to measure against — would be
optimising ahead of the requirement.

### Governance: the contracts this release is bound by

**The README is a summary; `provenance/DECISIONS-v1.0.0.md` is the contract.**
Where the two differ, the record governs. These are the decisions that constrain
what may be built, released or claimed — not all thirty-five, but the ones a
reader must know to read the rest honestly.

| | the contract | why it binds |
|---|---|---|
| **S1** | the deliverable is **the CDM and ΛCDM angular power spectra** in the almost-Friedmann–Lemaître formulation — (186) from (176), by both routes | it is what "done" means; F9 is that deliverable |
| **S15** | **reproduce the antecedent's approximations rather than correct them** | reproducing a paper means reproducing its narrowing choices. They are recorded as **A-n**, kept apart from defects (**B-n**), and F6 is the one place their cost is a number rather than an adjective |
| **S19** | the release sequence is fixed, and **nothing goes public before Paper 1 is submitted** | otherwise `provenance/` announces fourteen corrections to a published paper *ahead of* the paper that makes them quietly. **Paper 1 is submitted and frozen**, so this gate is satisfied |
| **S26** | v1.2.0 is an extension **and an audit**, and the audit half is in scope | a bundle that only reproduces cannot say whether what it reproduces is right. It is why the generic $\dot{\mathcal B}_A$ relations and criterion 5b's gate exist at all |
| **S27** | every artefact carries a **maturity rung**, and the rung is **verified, not declared** | a claim whose module, object, test or harness entry is missing fails `scripts/make_release_status.py` instead of appearing in the record |
| **S30** | **run-time optimisation is deferred** to a dedicated assessment for v2.0.0 | the benchmark below measures the cost; it does not license tuning it now, and no decision in this release may be taken on speed |
| **S4c** | criterion 5b is gated on the bundle's **own pipeline**, with CAMB and CLASS as **context** | a criterion that can only be failed is not a criterion |
| **S33** | the recombination grid is derived **immediately after this tag**, not before | the release closes on the numbers it was measured with |

**This shows that** the governance is not advisory: six of the eight above are
enforced by something that fails — the harness, a test, or a generator — rather
than by a reader remembering them.

**What is still open, and none of it blocks the tag.** The recombination grid
(**Q7**/**S33**, derived immediately after this tag); the numeric manifest gate,
which canonicalises by rounding to a string and so cannot express a tolerance
(**T-38** part 1, three designs recorded, the PI's choice); the Hu & Sugiyama
acoustic cross-check, deferred with its reason to v1.5.0 (**S35**); and a
parked physics question about whether the full $1+3$ treatment predicts excess
power at low $\ell$ (**Q5**), which F2's third panel measures and which goes
the other way at this order.

**The acceptance spine is Appendix F, pp. 379–380, Eqs. (F.1)–(F.4)**, where the
covariant mode recursion is matched to external treatments written in real
coefficients. Reproducing that chain is a representation-free test of the
harmonic normalisation, because a basis phase leaking into the coupling
coefficients would break every one of the matches. That match is where this
bundle's independence lives — not the spectrum comparison, whose target descends
from the same antecedent.

**The solution is carried with a generic 4-velocity.** The explicit frames — the
Newtonian frame in which *Annals II* itself solves at p. 365, and the energy
frame — appear as choices made at the end rather than assumed at the start. That
is the difference the 1+3 covariant approach buys, and no gauge-fixed treatment
can exhibit it.

**At v1.2.0 that is established numerically as well as symbolically, and the
distinction is worth stating plainly because it was the honest caveat for two
releases.** `functions/frames.py` carries the first-order change of frame with
every term tagged by its order in ε, so that "second order" is a fact sympy
checks rather than a judgement; its `roundtrip_residual()` returns the zero
vector as an **identity**, not as a small number — 𝓑̃₁ = 𝓑₁ + v̇_a, no shear and
no Hv, which is acceptance criterion 2's stated target. What v1.0.0 could *not*
do was compute an assembled spectrum in two frames and draw the difference.
**It is drawn now**: F5 decomposes the source by rank in both frames, F7
specialises (102) at the end rather than the start, and D6 measures the residual
sector by sector. The two frames' $C_\ell$ differ by a median of 15% over
$2\le\ell\le400$ — which is a *result*, not a defect, because $C_\ell$ is
quadratic in frame-dependent pieces while the invariance (102) satisfies is
about the total at fixed $k$.

**The second frame is the CDM frame, and the label was wrong for a week.**
*Annals II* §4.1 lists **three** choices — the energy frame $\tilde q_a=0$, the
zero-acceleration or CDM frame $\tilde A_a=0$, and the Newtonian frame. This
bundle integrates $v'+\mathcal Hv=-k\Phi_A$, which is the geodesic condition,
so what it computes is the **CDM frame** throughout; it was labelled the energy
frame. No released number moved — finding **T-29**, amendment **S8a**, with D7
measuring the tilt between the two at up to 45% of the frame velocity, worst
exactly where the acoustic physics is.

**That scale is context and not the threshold** — decision **S4c**, 2026-10-15.
It was the threshold, and a slow-decoupling solution with no polarisation
hierarchy and no neutrino anisotropic stress cannot meet two full Boltzmann
codes' 0.370%, so the criterion could only be failed. Criterion 5b is gated
instead on the thing *Annals II* writes twice and recovers symbolically but
never evaluates: (102), carried with a generic $u^a$ and specialised afterwards,
against the source assembly (177)–(179) written in the Newtonian frame from the
start. They agree
to **9.5×10⁻⁶** worst against a gate of 10⁻³, over three backgrounds and
$0.3\le k\le600$. The external comparison is still run and still reported —
97.8% in the plateau, 137% across the peaks, itemised by approximation in
`provenance/CRITERION-5B-v1.md`.

**Hu & Sugiyama** is the treatment this formulation was developed from and
checked against, which is why the acceptance spine matches their Eq. (6)
directly. **Challinor & Lasenby** is a contemporaneous and independent covariant
treatment, used here only for convention translation, since it works in the
opposite signature.

Equation numbers throughout are **published** numbers. The published and arXiv
numberings of the Annals papers differ, and not by a constant offset.

### Figure 1: the Appendix F match

The free-streaming recursion against each external treatment of (F.1)–(F.4), one
panel per treatment; four comparisons are four panels, not four colours on one
axis. Hu & Sugiyama write the recursion in the β normalisation, Ma & Bertschinger
and Seljak & Zaldarriaga in the α normalisation, which is why Appendix F prints
both (F.3) and (F.4). **Four panels from five sources**: Wilson & Silk (1981) is
the earliest and was read from its own page, but at $K=0$ it is Wilson (1983)
Eq. (8) exactly, so it is credited and not drawn — *Annals II*
names Wilson & Silk while keying Wilson.

### Legacy treatment from [Annals of Physics 282, 321 (2000)](https://doi.org/10.1006/aphy.2000.6034)

This bundle reconstructs its antecedent rather than porting it, and is built to
find that paper's remaining errors rather than to agree with it. These are the
findings that **change what the code computes**:

- **B-1** — *Annals I* prints (−1)^ℓ where its own definition gives i^ℓ.
  Inconsequential for the covariant multipole, which is invariant under the
  choice; the mode coefficients are not, and the two statements are distinct.
- **B-2** — (F.4) is algebraically correct but is not in the Ma & Bertschinger
  form the following sentence identifies it with: the (2ℓ+1)⁻¹ division its text
  specifies was not applied to the display.
- **B-3** — the Bessel identity (199) needs [(m/2)!]² in its denominator. It is
  exact where Γ(m/2+1) = 1, so (201) is unaffected; (204) is low by 11.4% and the
  D_ℓ of (205) correspondingly high by 12.8%.
- **B-5** — (201) omits one factor of the comoving distance in the reduction.
  This is the target of acceptance criterion 5a, so the criterion is stated
  against the corrected closed form rather than the printed one.
- **B-8** — (181) carries +R_*Φ_A where (180) gives −R_*Φ_A. Both forms are
  implemented; the printed one is kept as a control.
- **B-10** — (J.5) prints the transfer function with +1/ν where the fit requires
  −1/ν. Both forms are implemented, for the same reason.

The complete record — fourteen findings, together with the antecedent's deliberate
approximations and the one lineage note — is in `provenance/`.

## Future situation: the route to the full spectrum

**These are planned releases, not claims made by the current one.**

- **v1.1.0 — Peebles recombination. Released.** The effective
  three-level atom replaces equilibrium Saha. Saha places last scattering
  correctly but decouples too sharply and too early, which sets the wrong
  visibility width — and the visibility width is what fixes the damping
  envelope. Self-contained, and checked on its own against the standard
  ionisation history before anything was built on it. It is the default from
  this release (decision **S22**), with Saha kept as the measurable alternative.
- **v1.2.0 — the full linear C_ℓ: acoustic peaks, Silk damping, and the
  complete source assembly. RELEASED.** The spectrum stops being the almost-FLRW
  analytic skeleton and becomes a spectrum with structure in it; **F9** is that
  figure and it now leads this README, with the former Figure 3 kept beside it
  as the before. Acceptance criterion **5b closed here** — and *what it is
  gated against changed*, which this bullet states rather than quietly drops.
  The plan was to gate on CAMB and CLASS on a reduced parameter set. Measured,
  that comparison is 137% across the peaks against a code–code floor of 0.370%:
  a slow-decoupling solution with no polarisation hierarchy and no neutrino
  anisotropic stress cannot meet two full Boltzmann codes, and **a criterion
  that can only be failed is not a criterion**. Decision **S4c** gates instead
  on this bundle's own pipeline, (102) against (177)–(179), at
  9.5×10⁻⁶ against 10⁻³, with CAMB and CLASS run on the reduced set exactly as
  planned, stamped, and **reported alongside as context**.
  **The acoustic sector is not checked against Hu & Sugiyama here, and that is
  deferred rather than done** — decision **S35**. The sector is already measured
  against two full Boltzmann codes; adding a third, *analytic* comparator with
  approximations of its own would not strengthen it, and inventing an external
  check under freeze pressure is how finding **T-24** happened. What *is*
  checked against Hu & Sugiyama is the free-streaming chain, their Eq. (6), in
  **F1** — which is the part of their treatment this formulation was developed
  from, and it holds at 10⁻¹³.
  One **stated limit** ships with the release: the recombination grid sets the
  primary source and nothing derives it, worth 1.2% — question **Q7**, taken as
  decision **S33**, derived immediately after the tag.
- **v1.5.0** — the high-ℓ O(ε²ℓ) effects, **gated on Paper 1**, carrying **both**
  nonlinear corrections: the gravitational coupling to the kinematic quantities,
  δτ̇_NL, and the nonlinear Thomson scattering coupling to the baryon velocity,
  δĊ_NL. Also the restricted case, which must recover v1.0.0's numbers, making
  that part a recovery and a check rather than a new claim. **It is where the
  shear, acceleration and vorticity couplings belong** — each is a product of
  two first-order quantities and is dropped at linear order, which is why
  decision **S23**, having moved them into v1.2.0, is recorded as falsified by
  its own premise.
  **Four things v1.2.0 hands it, in order.** (i) The recombination grid, derived
  rather than fixed — **S33**, the first work after this tag, because a
  nonlinear correction measured against a base with a 1.2% uncertainty in the
  term it modifies is measured against the wrong thing. (ii) The Hu & Sugiyama
  acoustic cross-check, deferred with its reason — **S35**. (iii) The numeric
  manifest gate, **T-38** part (1). (iv) The factorised interface of **S24**,
  accepted as option (a) and deliberately not frozen until the forward model's
  high-ℓ envelope was right (**S25**) — which it now is.
- **v2.0.0** — calibration and data-science release, including Planck data.
  *Calibration* there means calibrating the solver against standard results; it
  does **not** mean calibrating the amplitude of an effect. **No new physics
  enters at v2.0.0**: everything it calibrates is already in place by v1.5.0.
- **A fractional-contribution form of the source decomposition**, each term drawn
  as its share of C_ℓ and summing to one by construction.

**Why the peaks come before v1.5.0 and not after it.** v1.5.0 is an O(ε²ℓ)
*correction* to the high-ℓ spectrum. A correction can only be read where the
thing it corrects is already right: added to a linear spectrum whose own high-ℓ
behaviour has never been validated, the correction and the error are the same
size and cannot be told apart. Criterion 5b is what establishes "already right",
and it is blocked on recombination. So the order is forced — recombination,
then peaks, then the external comparison that closes 5b, and only then the
nonlinear high-ℓ term that v1.5.0 exists to add.

## Scientific boundary

This is an analytical reproducibility bundle for the associated paper and its
supplement. It is not an empirical calibration, not a parameter-estimation
pipeline, and not a Boltzmann code for general use.

**No new effect is claimed here, and none is reported.** The exact 1+3 covariant
radiation multipole hierarchy contains couplings between the shear and the
temperature multipoles whose coefficient grows linearly in ℓ. Their O(ε²ℓ)
content is **gravitational lensing together with observer aberration**, with no
residue. Nothing here is a detection claim.

Two statements must travel together, and neither stands alone: the nonlinear
contribution δτ_NL **matters** — it is not negligible and not an artefact — and
it **adds nothing**, redistributing power rather than creating it, because
δτ_NL ∝ ΦΦ makes its contribution to C_ℓ quartic in Φ while the linear C_ℓ is
quadratic.

The bundle reproduces; it does not argue. Any physics claim belongs to the paper,
and no claim appears here that is not in the paper.

## Repository structure

```text
config/                  Accepted scientific and release configurations
functions/background/    The FLRW background, integrated from the 1+3 constraint
functions/frames.py      The frame shift, symbolically, with orders tracked
functions/harmonics/     PSTF weights, the recursion, and the external hierarchies
functions/spectra/       Sources, recombination, the acoustic pair, the spectrum
functions/plotting/      House visual style, shared by every figure
scripts/                 Active reproduction and verification commands
tests/                   Compact claim-bearing regression suite
data/                    No empirical data are required at v1.0.0
outputs/                 Machine-readable curve and summary evidence
figures/                 Versioned PDF/PNG figure pairs
tables/                  Generated audit tables: equations, parameters, notation
captions/                Standalone captions, and the figure plan for the set
diagnostics/             Generated scientific acceptance checks
source/source-v1/        Frozen target-paper source
source/source-v2/        Computational conformity and clarification inserts
provenance/              Theory-to-code traceability and the corrections record
supplementary-materials/ Compiled computational supplement
```

Scientific object versions such as `supplement-v1.0.0.pdf` and output suffixes
such as `-v1.0.0.png` are retained where they identify a released object — the
suffix marks the release an artefact was **introduced** in, not the release
that last regenerated it, so F6 and F8 carry `-v1.1.0` while the figures
specified at v1.0.0 keep theirs. The current documentation uses v1.1.0, and the
public v1.0.0 tag and its release asset remain unchanged.

## Installation

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Python 3.13 is the verified interpreter. PowerShell 5.1 has no `&&`; use `;`.

## Reproducing the active outputs

```bash
python scripts/run_all.py --strict     # regenerate everything, fail on any drift
python scripts/run_all.py --rerun      # regenerate without the drift gate
```

`--strict` is the release route: it regenerates every output, figure and table,
recomputes the manifests, and fails if any artefact differs from the recorded
hash. `--rerun` is the development route.

```bash
python scripts/make_tables.py          # regenerate the audit tables
python scripts/make_figure_pages.py    # regenerate the supplement's figure section
python scripts/make_manifests.py       # regenerate the two SHA256 manifests
python scripts/sync_conventions.py     # regenerate provenance/conventions.md
pytest -q                              # the claim-bearing regression suite
```

## Verification status

**Released as v1.1.0; this tree is v1.2.0-dev.** Every artefact carries a
maturity rung — prototype, proof of concept, release candidate, shipped — and a
release gates on the rung rather than on an opinion that the work is done. That
is decision **S27**, and `provenance/RELEASE-STATUS-v1.md` carries the rung of
everything in the tree. It is **generated and verified**: each rung names the
module, object, test or harness entry that earns it, and a claim whose evidence
is missing fails the run rather than appearing in the file.

**The v1.1.0 tag does not sit at the tip**, and deliberately: v1.1.0 is Peebles
recombination and the numerical frame specialisation, while the work that landed
after it — the covariant coefficient assembly, the integral solution (102), F5,
two diagnostics and eight findings — is v1.2.0's, and labelling it v1.1.0 would
label a tree by a release it has moved past.

**This file does not assert where the tag is, and that is a correction.** It
previously did, on an assumption nobody had checked; the repository is the only
thing that knows, so the check is written here instead of the answer:

```
git tag --list v1.1.0                                  # does it exist
git log --oneline -1 v1.1.0                            # where does it point
git merge-base --is-ancestor v1.1.0 HEAD; echo $?      # 0 if it is behind the tip
```

Finding **T-30**.

**Nine PNGs will always report as drifted, and that is not a defect of this
bundle.** Every `.png` written to a working copy through the Claude desktop
bridge gains a 5 770-byte `caBX` provenance chunk, inserted after `IHDR` by the
application rather than by anything here; the pixels are bit-identical and the
`.pdf` of the same figure round-trips byte-exact. This is why the manifests are
split. **`PORTABLE-MANIFEST-SHA256.txt` is what binds** — it excludes the
renderings entirely and canonicalises numerics to nine significant figures, and
a mismatch there is release-blocking. `FILE-MANIFEST-SHA256.txt` is a
*within-machine* drift check reported by class, and these nine are class
`rendered`, which is reported and does not block. **The PDF is the authoritative
artefact of every figure**; the PNG is a convenience copy. Findings **T-15** and
**T-36**.

The regression suite passes and `python scripts/run_all.py --strict` reports
`CLEAN` — run `pytest -q` for the current counts rather than trusting a number
typed here, which is how the previous version of this paragraph came to claim a
test total that was 36 short and a criteria tally that was half the truth.

The acceptance criteria are recorded in `RELEASE-NOTES-v1.0.0.md` and this
release's in `RELEASE-NOTES-v1.2.0.md`; **all six are closed.** 1, 2, 3, 4, 5a
and 6 closed in v1.0.0's scope; **5b closed here**, moved to v1.2.0 by decision
**S18** and gated by decision **S4c** on this bundle's own pipeline — (102)
against (177)–(179) at $9.5\times10^{-6}$ against $10^{-3}$, measured by
`scripts/diagnostic_d8_criterion_5b_gate.py` on every harness run.

**The CAMB and CLASS comparison is recorded in the bundle and deliberately
outside the bundled testing**, which is why the suite still reports skips there:
`reference/` carries the stamped spectra, `scripts/make_reference_spectra.py`
regenerates them from the codes, `scripts/compare_criterion_5b.py` reproduces
the measurement from the stamps **with neither code installed**, and
`tables/criterion-5b-v1.2.0.tex` is the result the supplement carries. A skip
cannot pass silently: `tests/test_external_codes.py` fails if that recorded
result or the means to reproduce it ever goes missing, and fails if either
script is ever added to the harness.

`config/implementation-register.toml` links every published equation the numerics
implement to its provenance, to the `.py` file and object implementing it, and to
the test that checks it. `scripts/make_tables.py` generates the equations,
parameters and notation tables from it, and `tests/test_register.py` resolves
every module, object and test named in it — so a rename breaks the build rather
than quietly falsifying a table in a published supplement. The parameters table
distinguishes values taken from the source paper from standard values that are
not, from values derived here, and from values stipulated for this release.

Two manifests guard the tree. `FILE-MANIFEST-SHA256.txt` is the release
fingerprint; `IMMUTABLE-MANIFEST-SHA256.txt` covers frozen reference material,
where any change is release-blocking. The corrections record is append-guarded
rather than frozen, because it must take new findings: appending is allowed and
rewriting recorded bytes is not.

*Disclosure of AI assistance.* The code, tests and documentation in this bundle
were written with AI assistance (Claude, Anthropic). Derivations were checked
against the published sources rather than generated from them, and every finding
carries its printed equation number in `provenance/`. Responsibility for the
content rests with the author.

## Version-control policy

The public version history follows semantic versioning:

```text
v1.0.0        first public analytical reproducibility release — the CDM and
              LambdaCDM angular power spectra in the almost-FLRW formulation,
              Eq. (186) from Eq. (176), by both the mode route and the covariant
              route of Eqs. (187) and (188)
v1.0.1        documentation or metadata updates without a scientific change
v1.1.0        Peebles effective three-level atom replacing equilibrium Saha;
              no change to v1.0.0's almost-FLRW numbers outside the visibility
v1.2.0        the full linear C_ell — acoustic peaks, Silk damping and the
              complete source assembly for CDM and LambdaCDM; acceptance
              criterion 5b closes here against CAMB and CLASS, with the
              acoustic sector checked against Hu & Sugiyama. The README's key
              figure becomes the normalised spectrum with its peaks
v1.5.0        compatible scientific extension — the high-ell effects, carrying
              BOTH nonlinear corrections (the gravitational coupling to the
              kinematic quantities and the nonlinear Thomson coupling to the
              baryon velocity), gated on Paper 1, with the restricted case as a
              recovery and check of v1.0.0
v2.0.0        calibration and data-science release, including Planck data
v3.0.0        incompatible model, interface or scientific-scope change
```

**v1.5.0 must not change v1.0.0's recovered Annals II numbers.** If it does, it
is a breaking change and belongs at v2.0.0. That rule is itself the regression
test.

The artefacts, what each one is evidence for, and the version it was last
regenerated at. A figure's version is the release that last changed its content,
which is why F1, F3 and F4 still carry `v1.0.0` — **a figure regenerated with no
change of content does not get a new label**, which is finding T-16's lesson
about labels that drift from what they name. `tests/test_readme_artefacts.py`
checks every row against `figures/` and `scripts/run_all.py`, so this table
cannot go stale the way the verification paragraph above once did.

| Figure | Evidence for | Version |
|---|---|---|
| **F1** Appendix F match | criterion 1 — the free-streaming chain against **four external hierarchies** in four conventions, two normalisations and two phase conventions, residuals $\lesssim10^{-13}$ | `v1.0.0` |
| **F2** truncation convergence, both frames | **Appendix E made quantitative.** Two quantities that do not shrink together: what a truncation *discards* falls off a per-$k$ cliff at $\ell\simeq k\Delta\eta$; what it *destroys* — the shear, and with it ranks 0 and 2 — has **no $\ell_{\max}$ in it**, is flat at 0.54–0.68% to $\ell\simeq20$ and rises to 32% by $\ell=600$. Footnote 29 (p. 365) is checked and holds: the cost is **identically zero** in the Newtonian frame, which has no shear to lose. A third panel answers the question of whether the covariant sectors supply an **excess at low $\ell$**: they do not — their share is **0.54% at the quadrupole** and grows with $\ell$, and T-31 shows the frame cannot supply one either | `v1.2.0` |
| **F3** angular spectrum, both routes | criteria 3 and 4 — (186) by the mode route and the covariant route, agreeing **exactly** since T-17 put the combined coefficients in $\mathbb Q$ | `v1.0.0` |
| **F4** real-space correlation | the round trip $C_\ell\to C(\theta)\to C_\ell$, residual $<10^{-13}$ | `v1.0.0` |
| **F5** source decomposition, two frames | **the total is common to both frames and the decomposition is not**, split by rank (S28). The frame disagreement is its own panel: 42% at $\ell=2$, 7% near $\ell=139$, 11% at $\ell=400$ | `v1.2.0` |
| **F6** what each approximation is worth | A-1, A-2 and the small-scale approximation as **ratios**, over six decades — one is a different calculation, one is free where this release claims, one is worst at large scales | `v1.1.0` |
| **F7** frame specialisation | the generic $u^a$ carried through and the frame chosen at the end — a figure a gauge-fixed treatment cannot draw. **It reports that its own planned claim is false**: the dipole was expected to stand an order of magnitude apart and lands on each curve instead, worst ratio **1.25×**, because (102) builds every $\ell$ from the same three $C_A$ and has no mechanism for answering differently at different $\ell$ (T-31) | `v1.2.0` |
| **F8** coupling schematic | a structural statement, not a measurement: which couplings exist at which order | `v1.1.0` |
| **F9** angular spectrum with the acoustic peaks | **the release's deliverable** — $D_\ell$ for CDM, $\Lambda$CDM and the Planck set, shape-normalised at $\ell=30$, with the peaks and the damping tail, against CAMB and CLASS as context (S4c) | `v1.2.0` |

| Diagnostic | Evidence for | Version |
|---|---|---|
| **D0** $\ell$ range, and B-3 | criterion 5's claimed range, derived rather than chosen: $2\le\ell\le20$ at 5% | `v1.0.0` |
| **D1** relative-sign control | criterion 4, and criterion 3 in executable form — the $c^2=-1$ branch **diverges**, which is what makes the correct one evidence | `v1.0.0` |
| **D2** round-trip residual | criterion 2's kinematic half, identically zero in exact arithmetic | `v1.0.0` |
| **D5** Sachs–Wolfe limit | criterion 5a at 5%, **and the statement that it cannot discriminate B-5** — the two forms differ by a factor with no $\ell$ dependence | `v1.0.0` |
| **D6** (102) in two frames | the frame-invariance measurement F5 rests on, with the residual split by sector | `v1.2.0` |
| **D7** CDM frame vs energy frame | **T-29** — *Annals II* §4.1 lists them as two of three distinct choices and this bundle conflates them; the tilt is up to 45% of the frame velocity | `v1.2.0` |
| *D3*, *D4* | *deferred to v1.5.0 (S-b)* — cross-checks, not acceptance artefacts. **Retargeted 2026-10-15, finding T-47**: they were deferred *to v1.1.0*, which shipped without them, so the harness announced a deferral to a release in the past. `run_all.py` now fails on a deferral to an already-released version | — |

The development lineage:

| Version | Established or changed | Status in v1.2.0 |
|---|---|---|
| *Annals II* (2000) | the almost-Friedmann–Lemaître 1+3 covariant hierarchy, its integral solution (176) and the spectrum (186) | the antecedent this bundle reconstructs; **fourteen** findings recorded against it in `provenance/`, B-1 to B-14 |
| Correction to astro-ph/9912072 | withdrew the 1999 claim of a new effect | binding — it fixes the scientific boundary stated above, and no new effect is claimed here |
| Conventions gate C1 | the normative sign and ℓ-weight sheet | source of the generated `provenance/conventions.md`; drift detectable through `conventions-source.txt` |
| Paper 1 (2026) | the 1+3 route to CMB lensing from the exact hierarchy | the paper this bundle reproduces; frozen 2026-10-09 |
| v1.0.0 | the independent reconstruction: the Appendix F chain against four external hierarchies, both routes to (186), the Sachs–Wolfe limit, and frame covariance established **symbolically** | superseded by v1.1.0; its tag, release asset and archived DOI are unchanged |
| v1.1.0 | Peebles recombination replacing equilibrium Saha and made the default (S22); the frame specialisation made numerical, closing criterion 2's curvature half; figures F6 and F8 | **released**; superseded by v1.2.0. Its tag is behind the tip by design, and the commands above are how to confirm that rather than take this row's word for it |
| **v1.2.0** | the covariant coefficient assembly (89)/(90); the integral solution (102) carried with a generic $u^a$ and **specialised back**; the generic $\dot{\mathcal B}_A$ relations; the CDM frame as a second frame; the full linear $C_\ell$ with acoustic peaks and Silk damping; `PLANCK_MODEL` with a derived radiation era; figures F2, F5 and F7, diagnostics D6, D7 and **D8**; and findings T-17 to T-48, B-11 to B-14 | **this tree.** Criterion 5b is **closed** — gated on (102) against (177)–(179) at $9.5\times10^{-6}$ against $10^{-3}$ (decision **S4c**), with CAMB and CLASS recorded alongside as context. No outstanding gate. One **stated limit** ships with it: the recombination grid, **Q7**/**S33**, derived immediately after the tag |
| v1.5.0, planned | the high-ℓ O(ε²ℓ) effects, carrying both nonlinear corrections, gated on Paper 1 | planned; carries the restricted case as a recovery and check of v1.0.0, not a new result |
| v2.0.0, planned | calibration and data science, including Planck | planned; no new physics in it, which is what keeps v1.2.0 ahead of it |

The current release identifier and Git tag are `v1.1.0`. The corresponding
GitHub Release title is **v1.1.0 — Peebles recombination and the numerical
frame specialisation**, and the release asset is
`frame-covariant-cmb-reproducibility-v1.1.0.zip`, built and verified by
`scripts/make_release_archive.py` — which extracts the archive it has just
written and runs the portability and manifest gates inside it, so the published
file is checked as a bundle rather than trusted as a file list.

`CITATION.cff` identifies the software version as v1.1.0. This does not alter
the frozen public v1.0.0 tag, its release asset or its archived DOI; the
concept DOI resolves to the latest version, which is what makes it the one to
cite.

## DOI, citation and license

| Item | Value |
|---|---|
| **Associated paper** | Gebbie, Tim (2026). *Frame covariance of CMB lensing in the exact 1+3 covariant radiation hierarchy*. arXiv: identifier assigned on submission |
| **Supplementary PDF** | [supplement-v1.0.0.pdf](supplementary-materials/supplement-v1.0.0.pdf) |
| **GitHub repository** | [timgebbie/frame-covariant-cmb-reproducibility](https://github.com/timgebbie/frame-covariant-cmb-reproducibility) |
| **ZivaHub/Figshare DOI** | [10.25375/uct.34069509](https://doi.org/10.25375/uct.34069509) — **live**. The **concept** DOI: it always resolves to the latest version, so it is the one to cite |
| **Associated antecedent** | Gebbie, T.; Dunsby, P. K. S.; Ellis, G. F. R. (2000). *1+3 covariant cosmic microwave background anisotropies II: the almost-Friedmann–Lemaître model*. Annals of Physics **282**, 321–394. [doi:10.1006/aphy.2000.6034](https://doi.org/10.1006/aphy.2000.6034) |
| **Code license** | MIT, see [`LICENSE`](LICENSE) |
| **Supplement, text, figures and tables** | CC BY 4.0, see [`CONTENT-LICENSE.md`](CONTENT-LICENSE.md) |

Citation metadata is in [`CITATION.cff`](CITATION.cff). Its `version` field
tracks the tag that exists, not the one in preparation: GitHub's *Cite this
repository* and Zenodo both read it, and a version there that has not been
released asserts a release nobody can fetch.
