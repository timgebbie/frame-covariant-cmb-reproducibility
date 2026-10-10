# Changelog

All notable changes to this bundle are recorded here. The version policy is in
`README.md` under *Version-control policy*.

## [Unreleased] — v1.1.0 in preparation

### Added

- `functions/spectra/peebles.py` — **Peebles recombination**, the effective
  three-level atom, and v1.1.0's named deliverable. Freeze-out comes out at
  $2.15\times10^{-4}$ against the standard $\sim2\times10^{-4}$, and it moves the
  visibility peak from $z\simeq1300$ (Saha) to $z\simeq1107$, against a standard
  1080–1100, while **widening the function by about 40%**. The width is what
  fixes the Silk damping envelope, which is why criterion 5b was blocked on this
  (S18). What is *derived* and what is *imported* is tabulated in the module
  docstring: the ODE structure and $\beta_B$ by detailed balance are derived, and
  $\alpha_B$, the atomic constants and the RECFAST fudge factor are imported with
  their sources. **The fudge is a named parameter, not a buried coefficient**, and
  `tests/` measures what it is worth.
- `functions/spectra/decoupling.py` — a `Recombination` enum. **`SAHA` remains
  the default**: flipping it changes every number in every released figure, which
  is a decision to be taken once with the before-and-after in view, not a side
  effect of adding a module.
- `functions/spectra/frame_transform.py` — the threading change made numerical.
  $\tilde\Phi_A=0$ and the Weyl invariant $\Phi_A-\Phi_H$ both hold to
  $1.1\times10^{-16}$.
- `functions/frames.py` — the curvature half of criterion 2:
  `weyl_invariance_residual` is identically zero, **with a negative control**
  showing it fails for any other potential rule, plus the dipole and
  $\ell\ge2$ statements as callable functions.
- `scripts/make_release_archive.py` — finding **T-13** closed. It found a real
  defect on its first run: `dist/` was not gitignored, so a release archive
  would have entered the fingerprint it was an archive of.

### Fixed

- `functions/spectra/sources.py` — a docstring that asserted a frame invariance
  the equations cannot have. Finding **T-14**.

### Changed

- **S21**: F5 and F7 move from v1.1.0 to v1.5.0, and F2 joins them — all three
  wait on the generic-$u^a$ hierarchy, not on figure work.

## [Unreleased] — v1.0.0 in preparation

### Added

- `functions/background/flrw.py` — the expansion law **derived** from the $1+3$
  covariant energy constraint, so that (185) and (G.3) are checks on this bundle
  rather than sources for it. `CDM_MODEL` and `LCDM_MODEL` are *models*; the CDM
  *frame* is the total-energy frame and lives elsewhere (decision S8).
- `functions/spectra/sources.py` — the three temperature sources (177)–(179) and
  the integral solution (176), which returns $\alpha_\ell^{-1}\tau_\ell$ and is
  checked against the free-streaming projection of `functions/harmonics/`.
- `functions/spectra/decoupling.py` — optical depth, visibility (101), the
  diffusion scale (168), and **both** weightings of the integrated source.
- `functions/spectra/acoustic.py` — the acoustic pair (152)/(153), with the
  printed oscillator (154) recovered symbolically and the dropped term named.
- `functions/spectra/transfer.py` — (J.1), (J.3) and the transfer function (J.5).
- `functions/spectra/angular.py` — (186), (187) and (188): both routes to
  $C_\ell$, computed rather than asserted to agree.
- `functions/harmonics/external.py` — **Wilson Eq. (8)** as a fourth external
  hierarchy, integrated complex and as printed, in the imaginary convention.
- `provenance/EQUATION-NUMBERS-ANNALS-II-v1.md` — the generated label→number map
  from the accepted manuscript, which caught a tight-coupling mis-citation.
- `provenance/SOURCE-APPROXIMATIONS-v1.md` — **deliberate narrow choices of the
  source**, kept separate from defects (decision S15, approximation A-1).
- `COLD-START.md` — the resume file. **Removed again before release**: it was
  working scaffolding, not a reader's artefact. It carried a session status
  block that went stale within days — at removal it reported the wrong
  acceptance-criteria set, contradicted itself on the findings count in a single
  cell, named one figure where three had been generated, and listed as "next"
  two stages that were done — and it opened by telling a reader to read it
  first. Its durable content was already elsewhere: the run instructions in
  `README.md`, the rules in `provenance/DECISIONS-v1.0.0.md`, the `k_com`/
  `k_phys` discipline in the corrections record. Nothing was lost.

### Changed

- Findings renumbered **G1–G10 → B-1–B-10**: Annals II's own appendix equations
  are (G.1)–(G.3) and the two collided (decision S13).
- `delta_over_pi` → `delta_over_four_pi`. It returned $\Delta_\ell/(4\pi)$ while
  its name said otherwise; the two-route $C_\ell$ comparison caught the resulting
  factor of four before it reached a figure.
- Criterion 1 restated for **four** external hierarchies in two normalisations
  *and* two phase conventions; F1 redrawn with four panels.
- Criterion 5b: compare against CAMB and CLASS with a **measured** tolerance
  (decisions S4a, S4b).
- $\Lambda$CDM corrected from v2.0.0 to **v1.0.0** in the supplement's
  interpretive limits, where stale text had survived the scope decision.

- House layout, root files and licences: MIT for code, CC BY 4.0 for the
  supplement, text, captions, generated figures and generated tables.
- `provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` — the corrections
  record, with findings B-1 and B-2.
- `provenance/OPEN-QUESTIONS-v1.0.0.md` — specification questions raised before
  code was written rather than resolved in flight.
- `functions/harmonics/weights.py` — PSTF weights as exact rationals, each cited
  to a published equation number.
- `tests/test_appendix_f_chain.py` — the Appendix F acceptance spine as
  arithmetic on the printed equations; no convention imported.
- `scripts/run_all.py`, `scripts/make_manifests.py`, `scripts/sync_conventions.py`.
- *Disclosure of AI assistance* in `README.md`.
- `captions/FIGURE-PLAN-v1.0.0.md` — the agreed specification for the figure set
  F1–F8 and the diagnostics, with colour roles and panel structure.

- `config/implementation-register.toml` and `scripts/make_tables.py` — the audit
  spine: published equation → provenance → `.py` file and object → test, generated
  into `tables/` and included by the supplement.
- `tests/test_register.py` — resolves every reference in the register, so the
  audit tables cannot drift from the code.
- `functions/harmonics/free_streaming.py`, `functions/harmonics/external.py` —
  the recursion in three normalisations, and the external hierarchies as
  printed in their own papers.
- `functions/plotting/style.py` and figure **F1**, the Appendix F match.

### Changed

- Figure set revised with the PI: the released set is now F1–F8, organised around
  the angular autocorrelation, the source decomposition of §7.1.1 drawn in two
  frames, and frame specialisation from a generic $u^a$.
- The $\pm(\ell+2)$ control is **withdrawn from v1.0.0** and replaced by a
  relative-sign control on the free-streaming bracket, in `diagnostics/`. The
  $\pm(\ell+2)$ term is second order and is not in this release's physics.
- v1.5.0 restated as a **recovery and check** of v1.0.0 rather than an extension
  of it, in the version-control policy and the supplement.
- Palette re-validated against the house surfaces rather than inherited.
- Criterion 5's range derived and closed: $2\le\ell\le20$ at 5%, generated by
  `scripts/derive_ell_range.py` rather than asserted.
- Finding **B-3** recorded: Annals II's Bessel identity (199) is correct only at
  even $m$; (204) and (205) inherit a constant error.
- `make_manifests.py` now distinguishes **append** from **rewrite** on the
  corrections record. Hash-freezing it raised a release-blocking alarm every time
  a finding was added — an alarm that fires on success trains people to ignore
  it. The guard now fails only if recorded bytes change.

### Notes

- Equation numbers in this bundle are **published** numbers, resolved from the
  published PDFs. The published and arXiv numberings differ, and not by a
  constant offset.
