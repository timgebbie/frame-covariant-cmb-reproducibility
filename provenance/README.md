# provenance/

Theory-to-code traceability for this bundle.

| File | What it carries |
|---|---|
| `ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` | the corrections record: every defect this reconstruction finds in its antecedent, classified and logged with published equation numbers |
| `OPEN-QUESTIONS-v1.0.0.md` | specification questions raised before code was written, each with a proposed resolution and a status |
| `conventions.md` | **generated** copy of the project's normative conventions sheet — never hand-edited; see `scripts/sync_conventions.py` |
| `conventions-source.txt` | the source path, SHA-256 and date of that copy, so drift is detectable |

**The record is append-mostly.** A finding is not deleted when it is resolved; its
status changes. `ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` is listed in
`IMMUTABLE-MANIFEST-SHA256.txt`, so a change to it is release-blocking and has to
be acknowledged rather than absorbed.
