# Custody and routes

**Maintained by Coordination. A map and a policy, not a record.** Who owns
which path, and how a change reaches `main`. Where the work stands is in each
stream's standing page; what has closed is in the project log,
`docs/STREAMS.md` in the paper repository. If this file ever starts carrying
findings it has become a third copy of something and should be cut back.

> **Renamed from `docs/STREAMS.md` on 2026-10-29, and the reason is a
> correction.** That name already belonged to the project log. This file was
> created under it on 2026-10-28 with a commit message asserting the name had
> never been used, which was reached by checking one repository out of two.

---

## THE LANDING POLICY

**One question: what are you landing?**

| what you are landing | route | notes |
|---|---|---|
| **a text file with no generated dependent** | **the GitHub connector** | works from any session — no credential, no shell, no PI. Both repositories |
| **several text files that must move together** — an edition bump's README line, `\date` and filename | **`push_files` through the connector: many paths, one commit** | one file per commit leaves the tree red between them, and a gate that reads two of them will say so |
| **text that a script produces** — manifests, `docs/THEORY-AUDIT.md`, the grid register, test output | **clone the public bundle in the cloud, run the generator there, land the result** — `git push` if this session is authorized, the connector otherwise | the cloud workspace has python with numpy/scipy/sympy, and `pdflatex`/`latexmk`. The connector's ceiling is the model's context: **about 100 kB of text** |
| **a binary, or any set containing one** — the supplement PDF, a figure | **a cloud clone in a session the PI has authorized for push** | the connector carries text only, and context carries no binary at all. **Not a stream's property — a session's.** Rule 6 |
| **anything in the private paper repository** | **the connector** for text; a clone needs the same authorization | branch `master`, not `main` |
| **anything that needs the PI's terminal** | **it waits** | rule 5 |

### The six rules, each paid for

**1. A connector commit cannot run a script.** If it leaves a manifest or a
generated document stale, **say so in the commit message** and raise it in the
handoff. The sweep is the first item of the next run that takes a clone, and
**it must be zero at a tag.** Deferred to "the next run" it reached 64 files on
`FILE-MANIFEST` and 40 on `PORTABLE-MANIFEST` inside one day, with three gates
red on `main`.

**2. Never write a loose file into the PI's working tree.** It stranded
`tests/frame/conformity.py` there for 17.8 hours — invisible to every session,
including the scheduled run whose own standing page instructs it to execute
that file first — and it swept ~1,600 characters of P1-T prose into P1-B's
`6e51a458` when the two operated on that tree at once. **A file on the PI's
disk is not in the repository, and what is not in the repository cannot be
read by the next session.** Committing there is different and is allowed; a
commit is in git.

> **The escape, and it is new on 2026-10-30.** When no route available to the
> session can carry the artefact, the artefact **waits in the stream's own
> session**, the **ask goes to the custodian of the path**, and the policy is
> the thing that gets fixed. P1-T took that escape on v1.3.20 — they showed the
> coupled set rather than asserting it, and routed the five promotion steps to
> P1-B as `#18`. The disk write itself is still outside this policy and should
> not recur; the demonstration and the escalation were correct, and the gap
> they walked into was rule 6's, below.

**3. `device_bash` leaves `.git` lock files it cannot delete.** Deletion in a
connected folder is refused until the PI approves it, so `git` commands leave
`index.lock`, `HEAD.lock` and friends behind, and **the next git command — his
own included — fails with "File exists".** Sweep them in the same call:
`for f in .git/*.lock; do [ -e "$f" ] && mv "$f" ".git/stale-$(basename $f)-$(date +%s)"; done`

**4. `device_bash` cannot push.** The Linux VM has no access to Windows
Credential Manager. It reads, runs and **commits locally**; the commit is
durable and rides on the PI's next push. Three trigger prompts asserted the
opposite for a week and none had tested it.

**5. If it needs the PI's terminal, it waits.** Not "unless it is quick" —
*quick* is how about ten blocks reached him on 2026-10-29 alone, on a day that
opened with the ruling that his machine is not a route. Anything genuinely
urgent goes to the stream that can land it, through the handoff or a wake.

**6. `git push` authorization is per session, and only the PI can grant it.**
A cloud clone reads any public repository anonymously and writes to none. The
git proxy injects a credential only for repositories in **that session's**
authorized set; `gh api` is refused on the same ground, with the same message.
**The set does not carry from one session to the next**, so a stream that
pushed yesterday cannot push today unless it was granted again. Measured in
Coordination's session, 2026-10-30: both repositories 403 on shell `git push`
and on `gh api`, anonymous clone of the public bundle fine, connector reading
and writing both. This had been recorded below as a capability of P1-B for two
days without ever being run — rule 4's failure, repeated.

> **If a run needs `git push`, ask at the top of the run, in these words:**
> *Add `timgebbie/frame-covariant-cmb-reproducibility` and
> `timgebbie/NonlinearShear` to this session's sources with push access.*
>
> One ask, at the start, replaces every later block. It is the only thing in
> this policy that the PI must do, and rule 5 does not apply to it.

### Who can do what

| | connector, read and write | cloud clone, read | `git push` from that clone | the PI's machine |
|---|---|---|---|---|
| **P1-T** | both repos | public bundle | **only if this session was authorized** | `device_bash`, local commits |
| **P1-B** | both repos | public bundle | **only if this session was authorized** | `device_bash`, local commits |
| **Coordination** | both repos | public bundle | **only if this session was authorized** | `device_bash`, local commits |

**There is no per-stream capability in this table, and the version it replaces
invented one.** Every session starts with the connector and nothing else.

What differs between streams is **custody, not capability**: the binaries and
the generated artefacts are **P1-B's to land**, because P1-B is the bundle's
custodian, and that stays true whichever session happens to hold a credential.
A stream that finds itself able to push something it does not own should hand
it to the owner, not land it.

### Branches, and they differ

| repository | GitHub | visibility | branch |
|---|---|---|---|
| the bundle | `frame-covariant-cmb-reproducibility` | public | **`main`** |
| the paper | `NonlinearShear` | **private** | **`master`** |

A connector write to the paper repository that assumes `main` targets nothing.
**The bundle must not be renamed** to match the local folder names: its URL is
in arXiv v4's Comments field beside the revision note, and it is the citation
trail behind the Zenodo DOI. arXiv versions are permanent.

### Always

**Name the route in the commit message.** One line, first line of the body:
`Route: connector` · `Route: push_files` · `Route: cloud clone, git push` ·
`Route: device_bash, local commit`. It costs a line and makes adherence
auditable from `git log` without asking anyone, which is the only kind of
adherence check this project can afford.

Commits made through a shell name their files with a pathspec on the commit as
well as the add — never `git add -A`. **But a pathspec on `git commit` commits
tracked files from the working tree and ignores staged additions**, so when the
point is to add *new* files, stage them and commit without one.

**No change to a rendered artefact is complete until the rendered artefact has
been loaded and read** — the built PDF for the supplement, the page and its DOM
for GitHub-rendered markdown, each against its own caption.

---

## Streams

| stream | adjudicates | writes, in the bundle |
|---|---|---|
| **P1-T** | the theory | `supplementary-materials/`, `tests/frame/`, `handoff/P1T-to-P1B.md`, and the root `README.md` |
| **P1-B** | the implementation; **custodian of the bundle** | everything else, plus `handoff/P1B-to-P1T.md` |
| **Coordination** | consistency, never correctness; **custodian of the paper repository** | `docs/CUSTODY.md` here, `docs/STREAMS.md` and `docs/RESUME.md` there |
| **PI** | everything irreversible | tags, releases, arXiv, the journal — and session authorization, rule 6 |

**The dividing line, testable per item: a number is P1-B's if it came out of a
run, and P1-T's if it came out of a derivation.**

**Custodian of a repository is not custodian of its contents.** Coordination
owns whether the paper repository exists, what its remote is, what is tracked,
and whether the disk and the history agree. `paper/` inside it remains P1-T's.
The same separation holds for P1-B and the bundle.

**The root `README.md` is P1-T's by the PI's grant of 2026-10-28.** It had been
P1-B's, while the line declaring the live supplement edition can only be
invalidated by a P1-T action — the dependency and the custody ran in opposite
directions and the download link died twice in one morning.

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

The handoff carries **the ask, never the finding**.

**It is not synchronous, and it is not one-way either.** For an item its writer
has marked **blocking**, that stream may **wake** the other — firing its working
run with the identifier named — once per item, and a woken session does not
fire back in the same run. Waking spends the other stream's budget.

> An earlier revision ended this section *"anything genuinely urgent still goes
> to the PI, who alone can start a session."* False, and never checked.

## Recovery

**The bundle.** This repository is its only complete copy and, as of
2026-10-29, a sufficient one: a clone plus the cloud toolchain reconstitutes
every generated artefact, which is a recovery test rather than a claim.

**The paper.** Backed up for the first time on 2026-10-29. Until that morning
its `origin` pointed at a repository that does not exist, so every push had
failed into the same error; twenty-six files in `paper/`, three whole
directories and a staged reorganisation were outside version control.

**Still uncovered.** The Claude project documents, including both standing
pages, are in no repository. Their only copy outside Claude is a nightly Google
Drive backup, which from 2026-10-29 snapshots all three standing pages dated
rather than only Coordination's.

**What custody of a container means, so the class cannot recur:** that the disk
and the repository agree. Coordination checks it by comparing directory
listings against the repository, which needs no shell and no cooperation from
either stream.

## Adding a stream

Four things settled before it writes anything: **what it adjudicates**, stated
so a disputed item can be assigned to exactly one stream; **which paths it
writes**, disjoint from every existing stream's; **which routes it may use**,
from the policy above; and **its own standing page**, rewritten rather than
appended to.

A stream that adjudicates nothing is a reviewer and does not need write access.
Two streams adjudicating the same thing is the failure this table exists to
prevent.
