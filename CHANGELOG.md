# Changelog

All notable changes to this bundle are recorded here. The version policy is in
`README.md` under *Version-control policy*.

## [Unreleased] — v1.0.0 in preparation

### Added

- House layout, root files and licences: MIT for code, CC BY 4.0 for the
  supplement, text, captions, generated figures and generated tables.
- `provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` — the corrections
  record, with findings G1 and G2.
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

### Notes

- Equation numbers in this bundle are **published** numbers, resolved from the
  published PDFs. The published and arXiv numberings differ, and not by a
  constant offset.
