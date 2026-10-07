# Figure plan — v1.0.0

**Agreed with the PI, 2026-10-05.** This file governs every figure in the
release: its form, its panels, its colour roles and the script that produces it.
A caption in this directory is the specification for its figure; this plan is the
specification for the set.

Figures are **print artefacts**: matplotlib → versioned PDF/PNG pairs. The web
interaction layer of the house data-visualisation standard is dropped. Everything
else — form chosen by the data's job, colour assigned by role, the validated
palette, thin marks, legend discipline, the accessibility pass — applies
unchanged.

---

## Binding rules

The house rules, plus those adopted in this release.

0. **Be faithful to the $1+3$ approach wherever possible.** Where a quantity can
   be written covariantly or in mode form, the covariant form is carried and
   reduced to modes only where a comparison requires it. Where a frame can be
   left generic, it is left generic and specialised explicitly at the end. This
   governs every choice below, and every choice not anticipated below.
1. **Plot multipole mean-squares, never mode mean-squares.** Annals II, p. 366:
   the multipole mean-squares $\langle\tau_{A_\ell}\tau^{A_\ell}\rangle$ "are
   given for general geometries, while the mode mean-squares are only for
   almost-Robertson–Walker geometries". The mode coefficients also carry the
   harmonic phase convention, so plotting $|\tau_\ell|^2$ would make a figure
   convention-dependent in exactly the way this bundle exists to avoid.
2. **Every figure names its frame.** v1.0.0 carries a generic $u^a$ and
   specialises late. Any quantity that is not invariant under a change of
   threading — the dipole, and the primary/Doppler/ISW split of §7.1.1 — is
   labelled with the frame it was computed in.
3. One axis. Never a dual y-axis. Two measures of different scale are two panels.
4. Legend present for $\ge 2$ series; $\le 4$ series are also direct-labelled, so
   identity is never carried by colour alone.
5. Text in ink, never in the series colour.
6. Grid and axes recessive; 2 px lines; markers $\ge 8$ px; a 2 px surface ring
   where marks overlap.
7. Dark mode is a selected variant from the same ramps, never an inverted light
   one.
8. Every figure is **rendered and looked at** before its caption is signed off.
   The validator checks colour, not layout.
9. **Corrections are silent, and marked by one footnote.** Where a figure depends
   on a corrected expression, its caption carries a single footnote naming the
   printed equation and pointing to
   `provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md`. The word is
   *misprint*, not *error*; the caption carries no narrative. The footnote
   register is at the foot of that file. F1's caption carries †1.

## Palette

Four categorical slots. **Re-validated 2026-10-05** against the house surfaces
rather than inherited: worst adjacent CVD $\Delta E$ **9.1** light / **8.4** dark,
worst adjacent normal-vision $\Delta E$ **22.9** light / **19.8** dark — all
above their gates in both modes.

| Slot | Light | Dark | Role in this bundle |
|---|---|---|---|
| 1 | `#2a78d6` blue | `#3987e5` | this reconstruction |
| 2 | `#eb6834` orange | `#d95926` | the published or external result being matched |
| 3 | `#1baf7a` aqua | `#199e70` | the third series where one is needed |
| 4 | `#eda100` yellow | `#c98500` | the deliberately-wrong control — **diagnostics only** |

**Slots 3 and 4 fall below 3:1 on the light surface** (2.74 and 2.11), confirmed
by the validator. The relief rule therefore binds: they carry visible direct
labels, never colour alone.

**Two constraints the slot table alone does not express.**

- **Never more than three hues where all pairs must be told apart at once** —
  scatter, small multiples read across panels, any figure where slot 4 would sit
  beside slot 2. Yellow against orange fails the all-pairs floors (normal-vision
  13.7 light, CVD 4.8 dark). The first three slots clear all-pairs in both modes.
- **A total is not a peer of its components.** Where a figure shows parts and
  their sum, the parts take slots 1–3 and the **sum is drawn in primary ink**,
  heavier. It is the reference, not another series.

**Diverging is for a single signed series about zero** — the house blue↔red pair
with a neutral grey midpoint, used in F3's residual panel. **Three identified
signed series are categorical, not diverging**: F5's cross-term panel uses slots
1–3 with a zero rule in ink, because the hue there carries identity and the sign
is carried by position about zero.

**Ordered sets are sequential, not categorical.** F2's truncations are an ordered
family, so they take the house single-hue ramp light→dark with increasing
$\ell_{\max}$, validated for lightness monotonicity rather than as a categorical
set.

---

## The released figures

| | Figure | Form | Script | Category |
|---|---|---|---|---|
| **F1** | Appendix F match | small multiples | `scripts/figure_f1_appendix_f.py` | cross-check |
| **F2** | truncation convergence | lines, log y, sequential ramp | `scripts/figure_f2_truncation.py` | diagnostic |
| **F3** | angular autocorrelation | lines + residual panel | `scripts/figure_f3_spectrum.py` | acceptance |
| **F4** | real-space $C(\theta)$ | lines | `scripts/figure_f4_correlation.py` | acceptance |
| **F5** | source decomposition, two frames | two panels, two frames | `scripts/figure_f5_sources.py` | acceptance |
| **F6** | impact of the approximations | lines, ratios to full | `scripts/figure_f6_approximations.py` | diagnostic |
| **F7** | frame specialisation | lines + residual panel | `scripts/figure_f7_frames.py` | cross-check |
| **F8** | coupling schematic | diagram, no computation | `scripts/figure_f8_schematic.py` | schematic |

**The key figure is F3.** It is what a reader checks first and what the release is
for. **F1 is where the bundle's independence lives** — not F3, because F3's
comparison target is derived from the same antecedent.

### F1 — the Appendix F match

One panel per external treatment of Eqs. (F.1)–(F.4), pp. 379–380: Hu & Sugiyama,
Ma & Bertschinger Eqs. (49)/(50), Seljak & Zaldarriaga Eq. (3d), **Wilson Eq.
(8)**. **Four panels from five sources** — Wilson & Silk Eq. (7) (1981) was read
from its own page and is the earliest of the set, but at $K=0$ it is Wilson
(1983) Eq. (8) exactly, so it is credited rather than drawn: an identical curve
in a fifth box would present one check as two.

Each panel carries exactly two series: the reconstruction in slot 1, that
treatment in slot 2. Only two hues appear in the whole figure, which keeps it
clear of the all-pairs constraint; the panel title names the treatment. Four
comparisons are four panels, never four colours on one axis.

The comparison applies the $(2\ell+1)^{-1}$ division that (F.4)'s prose specifies
and its display omits — see `provenance/`, finding **B-2**. Without it the panel
reports a $(2\ell+1)$ mismatch that is not a defect of the reconstruction.

### F2 — truncation convergence

One series per $\ell_{\max}$, log y, house sequential ramp light→dark with
increasing $\ell_{\max}$. This is Appendix E, pp. 378–379, made quantitative:
if any four consecutive harmonics vanish the shear must vanish exactly, so
truncation is dangerous even in the almost-Friedmann–Lemaître case.

**Run in both frames.** Footnote 29 on p. 365 asserts that choosing the Newtonian
frame "would also remove any problems we may have with the introduction of high-$\ell$
truncation as discussed in Appendix E". That is a checkable claim and this figure
checks it.

### F3 — angular autocorrelation

The recovered $C_\ell$ against its comparison target, with a residual panel
beneath sharing the x-axis. The residual panel is the claim; the overlay is
context. Never a dual y-axis. Agreement is stated as a number; the word *agrees*
is not used.

Residual panel: a single signed series about zero, so the diverging pair with the
neutral grey midpoint.

> **One decision outstanding:** criterion 5's tolerance needs an $\ell$ range,
> because §8 is a large-scale result with the transfer function set to unity in
> places. See `provenance/OPEN-QUESTIONS-v1.0.0.md`, Q3.

### F4 — real-space angular correlation

$C(\theta)=\sum_\ell (2\ell+1)C_\ell P_\ell(\cos\theta)/4\pi$, the basis-free
companion to F3. Single series plus target; no legend box is needed for one
series, and the title names it.

### F5 — source decomposition, drawn in two frames

The split of §7.1.1, pp. 365–366: the integral solution (176) projects three
sources through $j_\ell$ —

- `S_P` (177), the primary Sachs–Wolfe and acoustic term;
- `S_DISW` (178), secondary Doppler during slow decoupling;
- `S_ISW` (179), the integrated, late- and early-ISW terms.

Both secondary terms carry the damping factor $e^{-(k/k_D)^2}$.

**$C_\ell$ is quadratic in the source, so the three pieces do not add.** With
$\Delta_\ell=\Delta^P_\ell+\Delta^D_\ell+\Delta^I_\ell$ there are three auto-spectra
and three signed cross-spectra, and the figure shows all six.

| Panel | Contents | Colour |
|---|---|---|
| top | the three auto-spectra, plus the total | slots 1–3 for the autos; **the total in primary ink**, heavier |
| bottom, shared x | the three cross-spectra, signed, about a zero rule | slots 1–3, zero rule in ink |

**Drawn in two frames.** The split is frame-dependent — $\tilde\tau_1$ and $v_B$
are frame objects, so what counts as Doppler and what counts as ISW redistributes
under a change of threading, while the total does not. Frames are distinguished
by **line style, solid and dashed, not by hue**, because hue already carries
source identity. That composite encoding also keeps the figure to three hues.

This is the figure that makes the covariance argument quantitative: the total is
common to both frames, the decomposition is not.

### F6 — impact of the approximations

Ratios to the full result, so the panel is scale-free: the slow-decoupling order,
the diffusion damping factor $e^{-(k/k_D)^2}$ with $\exp\tau$ against
$\exp\tau^*$, and the small-scale cancellation of §7.1.3, p. 367. One axis, one
panel, three series in slots 1–3 with direct labels.

### F7 — frame specialisation

The point of the $1+3$ route, drawn. The solution is carried with a **generic**
$u^a$, with $\sigma_{ab}$ present, and the explicit frames appear as choices made
at the end:

- the Newtonian frame, $\tilde\sigma_{ab}=0$ — the specialisation Annals II itself
  makes at p. 365, and so a reproduction;
- the energy frame, $q_a=0$ — the extension.

Upper panel: the observable in both specialisations. Lower panel, shared x: their
difference about zero, with the **dipole shown separately**, because the dipole is
where the frame lives and $\ell\ge2$ is where it does not.

A gauge-fixed treatment cannot draw this figure, which is the reason it is in the
set.

### F8 — coupling schematic

Where each coupling sits in the hierarchy. No data, so no palette rules beyond
ink and the four slots used as identity. **Generated by a script like every other
figure**, so that the manifest covers it and its caption can name a producing
script.

---

## Diagnostics — not released figures

A control is not evidence. These live in `diagnostics/`.

| | What | Why here |
|---|---|---|
| **D1** | relative-sign control: the free-streaming bracket run with its relative sign flipped, which is the $c^2=-1$ case | the cheapest wiring check in the bundle, and it exercises the convention question that is live at v1.0.0. **It replaces the $\pm(\ell+2)$ control**, which would have exercised a second-order term the release does not contain |
| **D2** | round-trip residual, covariant → mode → covariant | a number with its tolerance. If it is machine precision it is not a chart |
| **D3** | the source terms (177)–(179) plotted directly against $k$ | the direct picture of the three printed equations, strictly linear and free of the cross-term question. Nearly free once F5 exists |
| **D4** | no monopole in the CGI approach | Annals II p. 366 states it; a test, not a picture |

## Deferred

- **v1.5.0** — the $\pm(\ell+2)$ control, where the term it exercises actually
  exists; and the restricted case, which must recover v1.0.0's numbers. That
  recovery is the regression test.
- **Possible extensions, not claims of this release** — the fractional-contribution
  form of F5, each term as a share of $C_\ell$ summing to one by construction,
  which is scale-free and makes the plateau and the damping tail equally legible.
