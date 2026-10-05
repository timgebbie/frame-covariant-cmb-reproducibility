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

### Notes

- Equation numbers in this bundle are **published** numbers, resolved from the
  published PDFs. The published and arXiv numberings differ, and not by a
  constant offset.
