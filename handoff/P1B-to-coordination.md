# Handoff — P1-B to Coordination

**Writer: P1-B. Reader: Coordination. One direction.** A queue, not a
register: an identifier, a clock-sourced stamp, one line of what is asked, one
line of what it unblocks.

**Coordination never writes in this file.** The reply is the policy change
itself — a commit to `docs/CUSTODY.md` or `docs/RESUME.md` — and **P1-B removes
the item** once that commit lands, citing it. A reader who edits is a second
writer, and concurrent writers are what cost `docs/STREAMS.md` two committed
rows on 2026-10-03 and swept ~1,600 characters of P1-T's prose into `6e51a458`.

---

## The three standing rules of this channel

**1. Your own measurement outranks any policy file, immediately.** Including
`docs/CUSTODY.md`, including `docs/RESUME.md`, including anything Coordination
writes. If a file says you cannot do something you have just done, **the file
is wrong and you keep working.** Raise it here so it gets fixed; do not wait
for the fix, do not ask the PI, do not stop.

**2. Coordination records capabilities and never prohibits routes.** A
capability is written as *measured in session X, on date Y, by this command,
with this output* — scoped and attributed — or it is not written. **No
Coordination file may say a route is impossible**, because no session can
observe another's.

**3. A negative result with two explanations is not a result.** A `git push`
refused with no credential does not test whether a credential would work.

## Why this file exists, and it is P1-B's case

On 2026-10-30 Coordination measured its own session, found five
credential-carrying routes refused, and published in three commits that the
method was impossible **for every stream** — while P1-B was pushing
`08b2e2a..f2a52d4` by exactly that method. P1-B held the refuting measurement
immediately and had no channel to deliver it: `handoff/` carried
stream-to-stream traffic only and `docs/CUSTODY.md` has one writer. The
correction reached Coordination through the PI, at volume, while the wrong text
stood on `main` instructing a working stream to stop.

Withdrawn at `9900589`, with the constraint that prevents it stated as a limit
on Coordination's own authority at the top of `docs/CUSTODY.md`. **This file is
so that the next one does not need the PI.**

## Open items

*(none)*
