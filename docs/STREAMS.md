# Streams, custody and routes

**Maintained by Coordination. A map, not a record.** Where the work stands is
in each stream's standing page; this file says only who owns what, and how a
change reaches `main`. If it ever starts carrying findings, it has become a
third copy of something and should be cut back.

Written 2026-10-28, revised the same day. It had been reserved by standing
rule since 2026-10-22 and did not exist until then — which is the project's
own §3c, applied to a rule: *a finding is not a finding until someone has
looked at the thing it names.* Two of its own claims were wrong within hours
and are corrected below, which is the rule applied to this file in turn.

---

## Streams

| stream | adjudicates | writes, in this repository |
|---|---|---|
| **P1-T** | the theory | `supplementary-materials/`, `tests/frame/`, `handoff/P1T-to-P1B.md`, and the root `README.md` |
| **P1-B** | the implementation; **custodian of the bundle** | everything else, plus `handoff/P1B-to-P1T.md` |
| **Coordination** | consistency, never correctness | `docs/STREAMS.md` |
| **PI** | everything irreversible | tags, releases, arXiv, the journal |

**The dividing line, testable per item: a number is P1-B's if it came out of a
run, and P1-T's if it came out of a derivation.**

**The root `README.md` is P1-T's by the PI's grant of 2026-10-28**, and the
reason is worth keeping. It had been P1-B's, while the line in it that
declares the live supplement edition can be invalidated only by a P1-T action
— so the dependency and the custody ran in opposite directions, and the
download link died twice in one morning. The grant makes them coincide. It is
the one file where the stream that adjudicates the content also holds the
path, and it is that way because the alternative was measured and failed.

Anyone may prod any stream; the stream that owns the question rules on it.
Coordination names collisions and never allocates.

**Frozen, and no stream writes them.** `correction/` is public and closed;
`sources/` is read-only; Paper 1 is frozen at both submission lines, so
anything found in it is referee-response or proof-stage material, never an
edit. `paper/` lives in a separate repository that is not on GitHub.

## The handoff

| file | writer | reader |
|---|---|---|
| `handoff/P1T-to-P1B.md` | P1-T | P1-B |
| `handoff/P1B-to-P1T.md` | P1-B | P1-T |

One writer per file; neither stream edits the other's. **A queue, not a
register:** an item carries an identifier, a clock-sourced stamp, one line of
what is asked and one line of what it unblocks, and **its author removes it
once it is answered**, so the length of each file is the number of open asks.
An answer is an append to one's own file citing the other's identifier.

The handoff carries **the ask, never the finding**. Findings live in
`provenance/BUNDLE-DEFECTS-v1.md` and in the standing pages, and an item here
points at them.

**It is not synchronous, and it is not one-way either.** An item is ordinarily
read when the other stream next runs. For an item its writer has marked
**blocking**, that stream may **wake** the other — firing its working run with
the identifier named — once per item, and a woken session does not fire back
in the same run. Waking spends the other stream's budget, which is why the
governor is narrow.

> An earlier revision of this file ended this section *"anything genuinely
> urgent still goes to the PI, who alone can start a session."* That is false.
> Both streams carry the connector that starts a run and could have done so
> from the day the channel opened. Coordination wrote the sentence into two
> standing pages and three prompts without checking it, which is §3c applied
> to a rule rather than to a finding, and is the same error as reserving a
> file that did not exist.

## Routes to `main`

| route | carries | cannot |
|---|---|---|
| **GitHub MCP connector** | any text-only file, from any session | **run a script** |
| **shell on the PI's machine** | everything, with its generators in the same commit | — |
| **the PI's own hands** | the fallback | — |

**Try the connector first for text; anything with a generated dependent needs
a shell.** `FILE-MANIFEST-SHA256.txt` and `PORTABLE-MANIFEST` hash the whole
tree, `docs/THEORY-AUDIT.md` is generated from the instruments, and the
supplement needs a build. An API commit refreshes none of them, so one that
leaves an artefact stale **says so in its commit message**.

**That debt has a ceiling.** The sweep is the first item of the next
shell-capable run, not a background intention, and **it must be zero at a
tag.** It reached 64 files on `FILE-MANIFEST` and 40 on `PORTABLE-MANIFEST`
inside a single day, with three gates red on `main`, which is what deferring
it to "the next run" amounts to in practice.

Commits made through a shell name their files with a pathspec on the commit as
well as the add — never `git add -A`, because the PI's index often holds
another stream's staged work.

**No change to a rendered artefact is complete until the rendered artefact has
been loaded and read** — the built PDF for the supplement, the page and its DOM
for GitHub-rendered markdown, each against its own caption. A source-pattern
test catches the failures already known; the rendered page catches the next
one.

## Adding a stream

A new stream needs four things settled before it writes anything here, in this
order: **what it adjudicates**, stated so that a disputed item can be assigned
to exactly one stream; **which paths it writes**, disjoint from every existing
stream's; **which of the three routes it may use**; and **its own standing
page**, rewritten rather than appended to, which is the only document of that
stream anyone else is required to read.

A stream that adjudicates nothing is a reviewer and does not need write access.
Two streams that adjudicate the same thing is the failure this table exists to
prevent.
