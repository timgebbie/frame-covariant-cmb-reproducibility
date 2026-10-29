# Custody and routes

**Maintained by Coordination. A map, not a record.** Who owns which path, and
how a change reaches `main`. Where the work stands is in each stream's standing
page; what has closed is in the project log. If this file ever starts carrying
findings it has become a third copy of something and should be cut back.

> **Renamed from `docs/STREAMS.md` on 2026-10-29, and the reason is a
> correction.** `docs/STREAMS.md` already exists — it is the project log in
> `timgebbie/NonlinearShear`, append-only, Coordination-only, and quite a
> different document. This file was created under that name on 2026-10-28 with
> a commit message asserting the name had never been used, which was reached by
> checking one repository out of two. One name for two documents is rule 1,
> introduced by the stream that enforces it; the log keeps the name.

---

## The two repositories

| local folder | GitHub | visibility | holds |
|---|---|---|---|
| `NonlinearShear-bundle` | `frame-covariant-cmb-reproducibility` | **public** | the reproducibility bundle — what a referee opens |
| `NonlinearShear` | `NonlinearShear` | **private**, branch `master` | the manuscript, submission artefacts, sources, the project log |

**The bundle must not be renamed to match.** Its URL is in arXiv v4's Comments
field beside the revision note, and it is the citation trail behind the Zenodo
DOI. arXiv versions are permanent, so the asymmetric naming is a constraint
rather than an oversight.

The private repository uses `master`; the bundle uses `main`. A connector write
that assumes `main` there will target a branch that does not exist.

## Streams

| stream | adjudicates | writes, in the bundle |
|---|---|---|
| **P1-T** | the theory | `supplementary-materials/`, `tests/frame/`, `handoff/P1T-to-P1B.md`, and the root `README.md` |
| **P1-B** | the implementation; **custodian of the bundle** | everything else, plus `handoff/P1B-to-P1T.md` |
| **Coordination** | consistency, never correctness; **custodian of the private repository** | `docs/CUSTODY.md` here, `docs/STREAMS.md` and `docs/RESUME.md` there |
| **PI** | everything irreversible | tags, releases, arXiv, the journal |

**The dividing line, testable per item: a number is P1-B's if it came out of a
run, and P1-T's if it came out of a derivation.**

**Custodian of a repository is not custodian of its contents.** Coordination
owns whether the private repository exists, what its remote is, what is tracked,
and whether the disk and the history agree. `paper/` inside it remains P1-T's.
The same separation holds for P1-B and the bundle.

**The root `README.md` is P1-T's by the PI's grant of 2026-10-28.** It had been
P1-B's, while the line in it declaring the live supplement edition can only be
invalidated by a P1-T action — the dependency and the custody ran in opposite
directions and the download link died twice in one morning. The grant makes
them coincide.

Anyone may prod any stream; the stream that owns the question rules on it.
Coordination names collisions and never allocates.

**Frozen, and no stream writes them.** `correction/` is closed — *public* there
means already published on arXiv, which is why it is frozen, and it is
unaffected by living in a private repository. `sources/` is read-only. Paper 1
is frozen at both submission lines.

## The handoff

| file | writer | reader |
|---|---|---|
| `handoff/P1T-to-P1B.md` | P1-T | P1-B |
| `handoff/P1B-to-P1T.md` | P1-B | P1-T |

One writer per file; neither stream edits the other's. **A queue, not a
register:** an item carries an identifier, a clock-sourced stamp, one line of
what is asked and one line of what it unblocks, and **its author removes it
once it is answered**, so each file's length is the number of open asks. An
answer is an append to one's own file citing the other's identifier.

The handoff carries **the ask, never the finding**. Findings live in
`provenance/BUNDLE-DEFECTS-v1.md` and in the standing pages.

**It is not synchronous, and it is not one-way either.** An item is ordinarily
read when the other stream next runs. For an item its writer has marked
**blocking**, that stream may **wake** the other — firing its working run with
the identifier named — once per item, and a woken session does not fire back in
the same run. Waking spends the other stream's budget, which is why the
governor is narrow.

> An earlier revision ended this section *"anything genuinely urgent still goes
> to the PI, who alone can start a session."* False, and never checked. Both
> streams carry the connector that starts a run and could have done so from the
> day the channel opened.

## Routes to `main`

| route | carries | needs |
|---|---|---|
| **the GitHub connector** | any text file, from any session | nothing |
| **a cloud clone** | everything a script produces | `git clone --depth 1` of the public repository |
| ~~the PI's machine~~ | — | **not a route** |

**Measured 2026-10-29, because this table previously asserted a dependency
nobody had tested.** On a fresh shallow clone in the cloud workspace:
`pdflatex` and `latexmk` are present, so the supplement builds; numpy 2.4.4,
scipy 1.17.1 and sympy 1.14.0 are present, so the instruments run;
`tests/frame/run_all.py` reports ALL FRAME CHECKS PASS over twelve instruments,
independent and isolated; `make_manifests.py --check` passes all five
manifests; `check_portability.py` passes over 319 files with git agreeing on
the set.

**The pattern for anything with a generated dependent is: clone, run the
generator, push the generated files through the connector.** The bundle is
public, so the clone needs no credential and no session is privileged over any
other.

A connector commit cannot refresh a manifest in the same breath, so one that
leaves an artefact stale **says so in its commit message**. The sweep is the
first item of the next run that takes a clone, and **it must be zero at a tag.**

**Writing to the PI's working tree is withdrawn as a route.** It caused two
failures in two days: `tests/frame/conformity.py` was written there on
2026-10-28 and spent 17.8 hours invisible to every session, including the
scheduled run its own standing page instructs to execute it first; and about
1,600 characters of P1-T prose were swept into `6e51a458` when P1-B rebased
while that tree held a file P1-T had just written into it. **A file on the PI's
disk is not in the repository, and what is not in the repository cannot be read
by the next session.**

**No change to a rendered artefact is complete until the rendered artefact has
been loaded and read** — the built PDF for the supplement, the page and its DOM
for GitHub-rendered markdown, each against its own caption.

## Recovery

**The bundle.** This repository is its only complete copy and, as of
2026-10-29, a sufficient one: the measurements above are a recovery test rather
than a claim. A clone plus the cloud toolchain reconstitutes every generated
artefact.

**The paper.** Backed up for the first time on 2026-10-29. Until that morning
it existed on one disk, and its `origin` pointed at `github.com/timgebbie/
nonlinear-shear`, which does not exist — so every push since that remote was
set had failed into the same error and nobody owned the container closely
enough to notice. On taking custody Coordination found twenty-six files in
`paper/` outside the repository, including every manuscript revision after
v1.0.0 and `VERSIONS.md`, which is the record of what distinguishes them; three
entire directories (`arxiv/`, `grg/`, `overleaf/`, about 17 MB of as-submitted
archives); eight untracked `docs/streams/` files including the Paper 2 startup
briefs; and a staged reorganisation of `docs/` left in the index since 4
October. All of it is now committed and pushed.

**What custody of a container means, so this class cannot recur:** that the
disk and the repository agree. Coordination checks it by comparing directory
listings against the repository, which needs no shell and no cooperation from
either stream. A reconciliation that runs on its own is the answer to a dead
remote; a rule saying someone should look is not.

**Still uncovered.** The Claude project documents — both standing pages and
every stream note — are not in git. Their only copy outside Claude is a nightly
Google Drive backup, and that backup re-snapshots only the Coordination page by
name, so the two stream standing pages are held at their first captured version
and nothing since.

## Adding a stream

A new stream needs four things settled before it writes anything, in this
order: **what it adjudicates**, stated so a disputed item can be assigned to
exactly one stream; **which paths it writes**, disjoint from every existing
stream's; **which routes it may use**; and **its own standing page**, rewritten
rather than appended to, which is the only document of that stream anyone else
is required to read.

A stream that adjudicates nothing is a reviewer and does not need write access.
Two streams adjudicating the same thing is the failure this table exists to
prevent.
