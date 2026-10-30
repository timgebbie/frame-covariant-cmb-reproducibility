# Handoff — streams to Coordination

**Writers: P1-T and P1-B. Reader: Coordination, which removes an item when it
is answered.** A queue, not a register. Same discipline as the other two
handoff files: an identifier, a clock-sourced stamp, one line of what is asked,
one line of what it unblocks.

**Why this file exists.** On 2026-10-30 Coordination published a ruling that a
route P1-B uses daily was impossible. P1-B had the refuting measurement
immediately and no way to deliver it: `handoff/` carried stream-to-stream
traffic only and `docs/CUSTODY.md` has one writer. The correction reached
Coordination through the PI, loudly, while the wrong text sat on `main`
instructing a working stream to stop. Every plumbing correction had been
routing through the PI for the same reason — which is the thing the landing
policy exists to prevent.

---

## The three standing rules of this channel

**1. Your own measurement outranks any policy file, immediately.** Including
`docs/CUSTODY.md`, including `docs/RESUME.md`, including anything Coordination
writes. If a file says you cannot do something you have just done, **the file
is wrong and you keep working.** Raise it here so it gets fixed; do not wait
for the fix, do not ask the PI, and do not stop.

**2. Coordination records capabilities, never prohibits routes.** A capability
is written here as *measured in session X on date Y, by this command, with this
output* — scoped and attributed — or it is not written. **No entry in any
Coordination file may say a route is impossible**, because no session can
observe another's, and the one time that was tried it nearly stopped a stream
mid-flight.

**3. A negative result with two explanations is not a result.** A `git push`
refused with no credential does not test whether a credential would work. A
probe that cannot come out the other way measures nothing. Coordination
published one of those too, and it would have told P1-T its working route was
dead.

## What belongs here

- **A policy file that is wrong**, with the measurement that shows it. Highest
  priority: these can stop a stream.
- **A route you need that the policy does not cover** — the case P1-T hit with
  v1.3.20, where four coupled files, one of them 1.6 MB of binary, had no
  described route and the ask went to the PI instead.
- **A collision**: two streams about to write the same path, or a custody
  question with no obvious owner.
- **A cold-start page that misled you.** `docs/RESUME.md` is read by every new
  session and has been wrong three times.

**Not** findings, not physics, not anything the other stream owns — those go to
the stream-to-stream files. This channel is about the plumbing and the map.

## Open items

*(none)*

---

> Coordination answers in `docs/CUSTODY.md` and removes the item here, citing
> the commit that carries the fix. If an item is marked **blocking**, the
> writing stream may wake Coordination's run with the identifier named, once
> per item — the same rule as the other two files.
