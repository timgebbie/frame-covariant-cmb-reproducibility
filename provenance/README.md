# provenance/

Theory-to-code traceability for this bundle.

## The records

| File | What it carries |
|---|---|
| `ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` | the corrections record: every defect this reconstruction finds in its antecedent, classified and logged with published equation numbers |
| `SOURCE-APPROXIMATIONS-v1.md` | deliberate approximations in the antecedent — choices, **not** defects, and kept apart so the corrections record is not padded with things that were never wrong |
| `BUNDLE-DEFECTS-v1.md` | defects in **this bundle's own** machinery, kept apart for the same reason in the other direction |
| `EQUATION-NUMBERS-ANNALS-II-v1.md` | the published equation numbers, resolved from the accepted manuscript rather than from memory or from arXiv |
| `DECISIONS-v1.0.0.md` | the numbered decisions `S-n`, each with what was decided, when, and why the alternative was rejected |
| `OPEN-QUESTIONS-v1.0.0.md` | specification questions raised before code was written, each with a proposed resolution and a status |
| `EXTERNAL-CODE-COMPARISON-v1.md` | the canonical CAMB/CLASS comparison: parameter set, bands, and what their mutual difference does and does not license |
| `ALMOST-EGS-BOUNDS-v1.md` | forward-looking scope note for v2.0.0; a table skeleton with no derived bound in it |
| `AI-PROVENANCE-v1.md` | the account of AI assistance that Paper 1's disclosure points at: what the model did by section, the six audit findings fixed on 2026-10-09, **two items left open on the PI's recorded decision**, and what the passes did not reach. Received from P1-T |
| `conventions.md` | **generated** copy of the project's normative conventions sheet — never hand-edited; see `scripts/sync_conventions.py` |
| `conventions-source.txt` | the source path, SHA-256 and date of that copy, so drift is detectable |
| `append-guard.txt` | **generated** length-and-hash record of the append-only files; see below |

## How findings are numbered

A prefix says what a finding is *against*, so that the audit of the antecedent
stays readable as an audit of the antecedent.

| Prefix | Against | Lives in |
|---|---|---|
| `B-n` | *Annals II* — a defect in the antecedent | `ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` |
| `A-n` | nothing — a deliberate approximation, recorded so it is not later mistaken for one | `SOURCE-APPROXIMATIONS-v1.md` |
| `L-n` | the lineage — a correction made downstream of the antecedent, by someone else, that this bundle must meet | `ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` |
| `S-n` | nothing — a decision taken by this project | `DECISIONS-v1.0.0.md` |
| `T-n` | this bundle's own tooling | `BUNDLE-DEFECTS-v1.md` |

The distinction between `B-n` and `A-n` is the one that was got wrong once and
is worth stating: an approximation the antecedent *declares* is not a defect,
and filing it as one would misrepresent the paper (decision S15).

## The record is append-mostly

A finding is not deleted when it is resolved; its status changes.

Two files are **append-only**, enforced rather than trusted:
`ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` and `BUNDLE-DEFECTS-v1.md`.
`append-guard.txt` stores the length and SHA-256 of what has been written so
far, and `python scripts/make_manifests.py --check` verifies that **those bytes
are unchanged**. Appending is fine; rewriting history is release-blocking.

They are guarded this way rather than frozen into
`IMMUTABLE-MANIFEST-SHA256.txt` deliberately. A corrections record has to be
able to take new findings — that is its job — so freezing its hash would raise
a release-blocking alarm every time the bundle worked correctly, and an alarm
that cries wolf is worse than no alarm.

`IMMUTABLE-MANIFEST-SHA256.txt` covers `source/` only: frozen reference
material, where any change at all is release-blocking because it means a source
moved under a citation.
