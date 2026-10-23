# Self-assessment criteria, and the assessment against them

**P1-B, 2026-10-22.** Criteria first, then the score. The criteria are written
so that **a failure against any one of them is a thing somebody can go and
look at**, not a judgement. Every one of them exists because the project
failed it at least once; the finding that produced it is named.

Reviewed weekly. The schedule and the checklist are at the end.

---

## Part 1 — Criteria for the physics

### P1. Every public claim is produced by a named instrument in the tree

Not "we checked"; a script, its output, and the output in the repository. The
generated `THEORY-AUDIT.md` exists because a hand-written one sat five days
and one instrument behind its own instruments, publishing a refuted conclusion
under a header reading *"Generated, not transcribed"* (**D6**).

### P2. Every instrument has a **known answer**

An instrument that measures a quantity without a value it is *required* to
return is a thermometer with no scale: it can report a number forever and
never fail. **T-117 is the standard to hold instruments to** — the transfer
over the Sachs–Wolfe transfer must be 1 as $k\to0$, and a reading of
$9.4\times10^3$ is therefore a verdict and not a datum.

The frame gap is the counter-example and the reason this criterion is here: it
has no known answer, so **M14** — an acceptance condition built only from
frame differences cannot see a defect common to both frames — and five repairs
were scored against it.

### P3. A defect is localised to source, transport or projection before any repair

Three places, three different repairs. **Five repairs were withdrawn** (T-88,
T-90, T-91, T-92, T-105) and every one of them was attempted before this
division had been made. It is now made by measurement: D21 clears the source
on EdS (0.68%); T-117's $\ell$-independence clears the projection; what is
left is the transport.

### P4. A derivation stated in a file prints its own residual

A docstring that asserts an identity and does not check it is a comment. D23
derives $C_2'-C_1=\Phi_A/3+2C_2'+\kappa'v_B/k$ and prints the residual beside
every row — which is how it was noticed that the identity closes to
$1.2\times10^{-6}$ on EdS and **plateaus at $2.3\times10^{-1}$ on PLANCK**.

### P5. A control is a named branch whose released default is bit-exact

**S43.** `PHI_PRIME_DRIVING_LAMBDA = 1.0` multiplies, and IEEE-754
multiplication by 1.0 is exact, so the released path is unchanged and
`array_equal` says so (D24's **L2**). A control that cannot be shown
bit-identical at its released value is measuring its own introduction.

### P6. An affine split is verified linear before it is split

**L1**, and T-101's method. Scale the input where the object under test reads
it and nowhere else; check $f(\lambda)=A+\lambda B$ to $10^{-14}$; then split.
Skipping the check is how a split that reaches a second term gets read as a
measurement of the first.

### P7. Both frames, both backgrounds, every time

**T-59.** One frame is half the question. And the backgrounds disagree
diagnostically: T-117's CDM boundary is $-0.9999$ on EdS and $+1.270$ on
PLANCK, and **reporting EdS alone would have produced a confident and wrong
sign hypothesis.** That nearly happened; see the assessment below.

### P8. A refuted claim is withdrawn in writing, with the measurement that refuted it

The register is append-guarded for this: appending is permitted, rewriting
recorded bytes is not. A withdrawal that edits the original leaves no trace
that the project believed something false, and the next stream repeats it.

### P9. The gate that can see the failure is built **before** the repair meant to fix it

Coordination §2.1, and it is the correction to a staged plan that had put the
only such gate last. D24 goes ahead of A-3 for this reason.

### P10. Every result states what it does **not** license

**M15** — a gate built from one coefficient cannot see a cancellation
distributed across the bracket. **M16** — a quantity measured on the
coefficients is not a statement about the spectrum without the projection in
between. Both are in every instrument's output, not in a style guide.

---

## Part 2 — Criteria for the bundle as it appears on GitHub

The bundle's reader is a colleague who opens the repository page, reads the
README and the supplement, and decides whether this is serious. Every
criterion below is about **that** reader.

### G1. It renders where it is read

Not "the LaTeX is valid" — valid LaTeX that GitHub's markdown parser destroys
is a broken page. **Found failing today (T-120):** five `\eta_*` in the (102)
display paired as markdown emphasis and the centre of the physics chain
rendered as the words *"Missing open brace for subscript"* above a wall of raw
source. CommonMark's asymmetry is the whole mechanism — `*` opens emphasis
intraword and `_` does not — and nothing in the suite was looking at the
rendered page. `tests/test_readme_renders_on_github.py` is now.

### G2. Freshness — the repository is never more than six hours behind the project

The PI's bound, and it is a correctness criterion rather than a tidiness one:
colleagues read the README and the supplement to learn the state of play, so a
stale repository is a false report.

### G3. One command reproduces everything

`scripts/run_all.py` — every figure, diagnostic, table, emission and generated
document, with the gates first.

### G4. Nothing in the tree the bundle cannot itself read or rebuild

**T-50**, where three such files passed every gate and entered the released
archive.

### G5. A generated artefact is generated, not remembered

An artefact whose production depends on a human recalling a shell redirection
is not generated. `gen_theory_audit.py` writes its own file because for five
days it did not, and a well-meant `>/dev/null` discarded the document.

### G6. Every discretisation is registered, with a status and a measurement

48 of 48. `open` is a permitted status and one row carries it, with the
decision that owns it.

### G7. Provenance is append-guarded by hash

Length and SHA-256 of what has been written so far. Appending permitted;
rewriting refused.

### G8. It runs where it was not written

`check_portability.py`, adopted from Coordination's audit.

### G9. The README is physics first

Governance belongs in the version-control tables, not on the front page —
**M13**, and the PI removed the bloat by hand once, which is once too often.

### G10. The visual grammar holds, V1–V15

**V12**, every figure rendered and *looked at*; **V15**, the caption is the
specification.

### G11. Citations are versioned and use published equation numbers

Never arXiv numbering for Annals II; `astro-ph/9912072` cited with its version
suffix, because the bare identifier has carried three distinct documents.

### G12. A test asserts the invariant, not the number

A test that pins $9.5\times10^{-6}$ is a test that gets updated when the
number moves. A test that pins *"both routes agree below $10^{-3}$"* is a
test.

---

## Part 3 — The assessment, 2026-10-22

| | criterion | verdict |
|---|---|---|
| P1 | claims have instruments | **holds** — 123 register entries, each with a script |
| P2 | instruments have known answers | **improving** — T-117 is the first spectrum-level gate with an exact expected value. The frame gap still has none |
| P3 | source / transport / projection | **holds, newly** — the division is now made by measurement rather than asserted |
| P4 | derivations print residuals | **holds** — and it earned its keep today |
| P5 | controls bit-exact at default | **holds** — L2 passes `array_equal` |
| P6 | affine splits verified linear | **holds** — L1 at $1.6\times10^{-16}$ |
| P7 | both frames, both backgrounds | **holds, and it saved a wrong conclusion today** |
| P8 | refutations written down | **holds** — 5 withdrawn repairs, each with its measurement |
| P9 | gate before repair | **holds, newly** — D24 precedes A-3 |
| P10 | states what it does not license | **holds** |
| G1 | renders where read | **FAILED today, now guarded** |
| G2 | six-hour freshness | **at risk** — this is the fourth consecutive day the bound was reached rather than held |
| G3 | one command | **holds** |
| G4 | readable and rebuildable | **holds** |
| G5 | generated is generated | **holds** |
| G6 | grids registered | **holds** — 48/48 |
| G7 | append-guarded | **holds** |
| G8 | portable | **holds** |
| G9 | physics-first README | **holds** since the restructure |
| G10 | visual grammar | **holds** |
| G11 | versioned citations | **holds** since T-116/T-119 |
| G12 | invariants not numbers | **partial** — see below |

### The five things that are actually wrong

**1. Control proliferation.** `integral_solution` carries **7 boolean controls
— 128 configurations** — and `coefficients.py`, `two_frame.py` and
`decoupling.py` carry 16 module-level constants between them. **M11a** says
not to test controls apart, and nobody can run 128 together. Each was right to
add; the set has no retirement policy. **A control whose question has been
answered must be removed or promoted to the default, and the answer recorded.**
Three are already answerable: `w_half_is_isw_only` (T-89), `thomson_carries_shear`
(T-88, withdrawn) and `by_parts_weight_terms` (T-72).

**2. The register has no index.** 9 481 lines, 483 kB, 123 entries, read
linearly. A finding that cannot be found is not a record. A generated index at
the head — number, one-line claim, status (standing / withdrawn / superseded)
— costs one script.

**3. README numbers are hand-copied from the register.** Every figure quoted on
the front page — $9.5\times10^{-6}$, $10^{-13}$, 0.68%, 29% — is transcribed
by hand with no gate. That is a drift surface on the public face, and it is the
same shape as the defect G5 exists to prevent. **This is the most likely source
of the next public error.**

**4. G12 is partial.** Several tests pin numbers rather than invariants. They
pass, and they will be edited the day the physics moves, which is exactly when
a test should instead fail and be *read*.

**5. Correspondence proliferation.** One file per stream per day was agreed and
is not enforced; the project now has 77 docs and five of today's are variations
on two subjects.

### The near miss worth recording

Working from the EdS block alone, the CDM boundary tends to $-0.9999$ — the
Sachs–Wolfe transfer with the sign reversed to one part in $10^4$ — and the
obvious reading is a sign defect, with **B-11** standing ready as the culprit.
**The PLANCK block says $+1.270$.** Right sign, 27% high. So it is not one
sign, and the EdS $-1$ is an EdS coincidence rather than a mechanism. I
recorded it as a hypothesis rather than a finding, which was right, but the
hypothesis is now **weaker than the entry states** and P7 is the only reason
the second number existed to check it against.

---

## Part 4 — Engineering principles, reassessed

These are the principles the bundle is actually built on. They are working;
the reassessment is where each one is thin.

**1. One definition, enforced — never two descriptions that drift.**
`_bundle_files.py` for the file set, `grid-register.toml` for discretisations,
`gen_theory_audit.py` for the audit. *Thin at:* the README's numbers, which are
a second description of the register with nothing enforcing agreement (item 3
above).

**2. A derivative comes from a published relation, never from differentiating a
stored amplitude.** T-23, and the measured cost of breaking it is a median of
100%. *Not thin.* It is the single most load-bearing rule in the bundle.

**3. A control is a named branch with the released default.** S43. *Thin at:*
no retirement policy (item 1 above).

**4. Append-only provenance, hash-guarded.** *Thin at:* no index (item 2).

**5. Measurement over argument.** The project's strongest habit, and the reason
five wrong repairs cost days instead of weeks. *Not thin.*

**6. State the limits of every result.** M15, M16. *Not thin,* and today it
kept a wrong sign hypothesis out of the record.

**7. The public artefact is written for the reader it has.** M13. *Was thin;*
G1's test is the repair.

### What I propose to change

- **A control budget.** `integral_solution` keeps at most four live controls.
  Each new one retires one, or states in its docstring why it cannot yet.
- **A generated register index**, written by the same script that checks the
  append guard.
- **A gate that reads the register's numbers into the README's**, so a figure
  on the front page cannot differ from the entry it came from.
- **Weekly self-audit**, below.

---

## Part 5 — The weekly audit

Saturdays. Checklist, in order, roughly one hour:

1. `python3 scripts/run_all.py` — gates, figures, diagnostics, emissions.
2. Every criterion G1–G12 scored in this file, with the date.
3. The repository's rendered README and the supplement PDF **looked at**, not
   diffed — V12 applied to the public face.
4. Controls: any whose question is answered, retired or promoted.
5. Register: regenerate the index; mark any entry the week refuted.
6. Correspondence: consolidate the week's stream files to one per subject.
7. The six-hour bound: was it held every day, and if not, when and why.

This document is the output. It is rewritten, not appended to, because it is an
assessment of a present state rather than a record of events — which is the
opposite of what `BUNDLE-DEFECTS-v1.md` is, and the distinction is deliberate.
