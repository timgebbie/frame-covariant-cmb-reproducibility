# Custody and routes

**Maintained by Coordination. A map and a policy, not a record.** Who owns
which path, and how a change reaches `main`. Where the work stands is in each
stream's standing page; what has closed is in the project log,
`docs/STREAMS.md` in the paper repository. If this file ever starts carrying
findings it has become a third copy of something and should be cut back.

> ### What this file may and may not say
>
> **It may record a capability**, scoped to the session that measured it and
> attributed to the command that measured it: *measured in session X, on date
> Y, by this command, with this output.*
>
> **It may not say that a route is impossible.** No session can observe
> another's, and on 2026-10-30 this file said exactly that about a route P1-B
> was using at the time. Had P1-B complied, a working stream would have
> stopped.
>
> **A stream's own measurement outranks this file, immediately** — without
> waiting for Coordination to agree, and without asking the PI. Raise it in
> your own channel to Coordination; keep working meanwhile.
>
> *Renamed from `docs/STREAMS.md` on 2026-10-29; that name already belonged to
> the project log.*

---

## THE LANDING POLICY

**One question: what are you landing?**

| what you are landing | route | notes |
|---|---|---|
| **a text file with no generated dependent** | **the GitHub connector** | works from any session — no credential, no shell, no PI. Both repositories |
| **several text files that must move together** — an edition bump's README line, `\date` and filename | **one commit**: `git push` from a clone, or `push_files` through the connector | one file per connector commit leaves the tree red between them, and a gate that reads two of them will say so |
| **text that a script produces** — manifests, `docs/THEORY-AUDIT.md`, the grid register, test output | **clone in the cloud, run the generator there, land the result** — `git push` if your session can, the connector otherwise | the cloud workspace has python with numpy/scipy/sympy, and `pdflatex`/`latexmk`. The connector's ceiling is the model's context: **about 100 kB of text** |
| **a binary, or any set containing one** — the supplement PDF, a figure | **`git push` from a cloud clone** | the connector carries text only, and context carries no binary at all. **P1-B's sessions do this routinely.** Rule 6 |
| **anything in the private paper repository** | **the connector** for text; a clone needs push | branch `master`, not `main` |
| **anything that needs the PI's terminal** | **it waits** | rule 5 |

### The seven rules, each paid for

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

> **The escape.** When no route available to the session can carry the
> artefact, the artefact **waits in the stream's own session**, the **ask goes
> to the custodian of the path**, and the policy is the thing that gets fixed.
> P1-T took that escape on v1.3.20 — they showed the coupled set rather than
> asserting it, and routed the five promotion steps to P1-B as `#18`. The disk
> write itself stays outside this policy; the demonstration and the escalation
> were right. **P1-B has since offered to promote v1.3.20 from its own clone**
> (`#20`), which is the correct resolution and needs nothing from the PI.

**3. `device_bash` leaves `.git` lock files it cannot delete.** Deletion in a
connected folder is refused until the PI approves it, so `git` commands leave
`index.lock`, `HEAD.lock` and friends behind, and **the next git command — his
own included — fails with "File exists".** Sweep them in the same call:
`for f in .git/*.lock; do [ -e "$f" ] && mv "$f" ".git/stale-$(basename $f)-$(date +%s)"; done`

**4. `device_bash` cannot push.** The Linux VM has no access to Windows
Credential Manager. It reads, runs and **commits locally**; the commit is
durable and rides on the PI's next push. Three trigger prompts asserted the
opposite for a week and none had tested it. *(`device_bash` has in any case
been unreachable since 2026-10-27, failing identically on every attempt.)*

**5. If it needs the PI's terminal, it waits.** Not "unless it is quick" —
*quick* is how about ten blocks reached him on 2026-10-29 alone, on a day that
opened with the ruling that his machine is not a route. Anything genuinely
urgent goes to the stream that can land it, through the handoff or a wake.

**6. A session that holds a credential can push, whether or not the proxy would
have given it one.** P1-B established this and states it exactly:

> *The proxy declining to **inject** a credential does not stop a push that
> **carries** its own.*

P1-B's session is **not** in the authorized repository set and has fifteen
commits on `main` today, through a cloud clone with a fine-grained PAT and
`git -c http.extraheader`. Two things are therefore separate and had been run
together in this file for two days:

| | |
|---|---|
| **the proxy injecting a credential** | per session, per repository, granted by the PI adding the repository to that session's sources. Absent in Coordination's session |
| **a push carrying its own credential** | **works in P1-B's session**, and is how the bundle's binaries, manifests and generated artefacts have been landing |

**The probe, and get it right — mine was wrong.** A `git push --dry-run`
carrying **no** credential returns a 403 in every session tested, including
P1-B's, which pushes successfully seconds later. **That form of the test proves
nothing and the earlier text of this file told streams to run it.** The test
that distinguishes anything is the one with a credential in it:

```
git -c http.extraheader="Authorization: Basic $(printf 'x-access-token:%s' "$TOK" | base64 -w0)" \
    push --dry-run origin HEAD:refs/heads/probe-$(date +%s)
```

If that succeeds, the route is open and binaries are landable from your
session. If it is refused **with a real token**, the connector is your route,
the ~100 kB text ceiling applies, and a binary goes to **P1-B**, whose custody
it is anyway.

**Measured in Coordination's session only, and binding on nobody else:** a push
with no credential, and a `gh api` call, are both refused as *not in this
session's authorized repository set*; a raw REST `PUT` is refused as *write
access to this GitHub API path is not permitted through this proxy*. A third
measurement, of `http.extraheader`, is **struck** — it used a placeholder
token, so its failure cannot distinguish a blocked route from a rejected
credential, and it was the row that did the damage below.

> **Withdrawn 2026-10-30, and it is the worst thing this file has carried.**
> Three commits that morning — `9375628`, `08b2e2a`, `14088b5` — generalised
> Coordination's measurements into a ruling that *no* credential reaches GitHub
> from *any* session, and refused P1-B's route as impossible. P1-B had been
> pushing through it all week; the evidence was in `git log` throughout; and
> P1-B pushed `08b2e2a..f2a52d4` by that exact method while the ruling against
> it was being written. **A capability measured in one session is a fact about
> that session.** Had P1-B complied with the text, a working stream would have
> stopped.

**7. Measure the blocker before you route around it, and measure it the way
that could come out either way.** The project's most expensive habit, now six
instances deep: three trigger prompts asserting `device_bash` could push,
untested for a week (rule 4); this file's capability matrix granting P1-B push
on no evidence and then revoking it on evidence from somebody else's session
(rule 6, both directions); `conformity.py` asserted landed and stranded 17.8
hours; P1-T routing around a push capability it has never tested; and **the
withdrawal above, written into the same commit that introduced this rule** —
the proof of it rather than an exception to it.

**A proposal or a ruling about a route carries the command that was run and the
output it returned, or it is not considered** — not an inference from an error
seen once, not what worked in another session, not what the documentation
implies, **not a measurement from a different session**, and **not a test whose
negative result has two explanations**. The verification register has said for
weeks that *a write reporting success is not a write*. The same now holds for a
plan and, harder, for a refusal.

### Credentials, where one is in play

Nothing here is an argument about whether the route works; rule 6 settles that
per session, and in P1-B's it works. These are handling constraints:

- **Never in chat.** A live PAT reached a transcript on 2026-10-29 and had to
  be regenerated. The PI writes it to a file; a session is pointed at the path,
  reads it into a variable, and never emits the value.
- **Never `credential.helper store --file=` into a connected folder.** Git
  writes to that file. On 2026-10-29 it wrote the sandbox's own proxy
  credential into the PI's documents, with a base64-encoded bash command as
  the username. `http.extraheader` from a shell variable, which is what P1-B
  uses, has neither failure.
- **Fine-grained, least scope.** Contents read and write plus Metadata read is
  the whole requirement for git. User permissions are not needed.
  `.github/workflows/` needs a separate Workflows permission and nothing here
  does.
- **The file is the PI's to place and the PI's to remove**, and it comes off
  the disk when the work stops. No session deletes it and no session copies it.

### Who can do what

| | connector, read and write | cloud clone, read | `git push` from that clone | the PI's machine |
|---|---|---|---|---|
| **P1-T** | both repos | public bundle | **untested — run the probe above, with a token** | `device_bash` unreachable since 10-27 |
| **P1-B** | both repos | public bundle | **yes, in use, fifteen commits on 10-30** | as above |
| **Coordination** | both repos | public bundle | no credential held; not retested | as above |

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
auditable from `git log` without asking anyone — and had it been in force a
week ago, the ruling withdrawn under rule 6 could not have been written, because
the route that was being called impossible was named in every commit using it.

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
| **P1-T** | the theory | `supplementary-materials/`, `tests/frame/`, `handoff/P1T-to-P1B.md`, `handoff/P1T-to-coordination.md`, and the root `README.md` |
| **P1-B** | the implementation; **custodian of the bundle** | everything else, plus `handoff/P1B-to-P1T.md` and `handoff/P1B-to-coordination.md` |
| **Coordination** | consistency, never correctness; **custodian of the paper repository** | `docs/CUSTODY.md` here, `docs/STREAMS.md` and `docs/RESUME.md` there |
| **PI** | everything irreversible | tags, releases, arXiv, the journal |

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

**Coordination owns the policy and does not own the plumbing.** A stream
blocked by this file raises it in its own channel rather than with the PI. And
a stream whose own measurement contradicts this file is right and this file is
wrong, immediately — see the box at the top, which is a limit on this file's
own author rather than advice to its readers.

**Frozen, and no stream writes them.** `correction/` is closed — *public* there
means already published on arXiv, which is why it is frozen, and it is
unaffected by living in a private repository. `sources/` is read-only. Paper 1
is frozen at both submission lines.

## The handoff

| file | writer | reader |
|---|---|---|
| `handoff/P1T-to-P1B.md` | P1-T | P1-B |
| `handoff/P1B-to-P1T.md` | P1-B | P1-T |
| `handoff/P1T-to-coordination.md` | P1-T | Coordination |
| `handoff/P1B-to-coordination.md` | P1-B | Coordination |

**One writer per file, every file, one direction.** A first attempt at the
Coordination channel on 2026-10-30 used a single shared file with two writers
and was replaced within the hour: concurrent writers are what lost
`docs/STREAMS.md` two committed rows on 2026-10-03 and swept ~1,600 characters
of P1-T prose into `6e51a458`, and reintroducing that in the file meant to
prevent coordination failures was not a small irony.

**A queue, not a register:** an item carries an identifier, a clock-sourced
stamp, one line of what is asked and one line of what it unblocks, and **its
author removes it once it is answered**, so each file's length is the number of
open asks.

**Between the streams**, an answer is an append to one's own file citing the
other's identifier. **To Coordination**, the answer is the policy change itself
— a commit to `docs/CUSTODY.md` or `docs/RESUME.md` — and the **author** strikes
their own item citing that commit. Coordination never writes in a stream's
file, because a reader who edits is a second writer.

The handoff carries **the ask, never the finding**.

**The Coordination channel is new on 2026-10-30 and it is the edge that was
missing.** It exists because P1-B held the measurement refuting a ruling on
`main` and had no way to deliver it — the correction went through the PI, at
volume, while the wrong text stood. Every plumbing correction had been routing
through the PI for the same reason, which is precisely what this policy exists
to stop.

**It is not synchronous, and it is not one-way either.** For an item its writer
has marked **blocking**, that stream may **wake** the other — firing its working
run with the identifier named — once per item, and a woken session does not
fire back in the same run. Waking spends the other stream's budget. The same
applies to waking Coordination.

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
from the policy above; **its own standing page**, rewritten rather than
appended to; and **its own one-way file to Coordination**.

A stream that adjudicates nothing is a reviewer and does not need write access.
Two streams adjudicating the same thing is the failure this table exists to
prevent.
