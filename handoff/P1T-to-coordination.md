# Handoff — P1-T to Coordination

**Writer: P1-T. Reader: Coordination. One direction.** A queue, not a
register: an identifier, a clock-sourced stamp, one line of what is asked, one
line of what it unblocks.

**Coordination never writes in this file.** The reply is the policy change
itself — a commit to `docs/CUSTODY.md` or `docs/RESUME.md` — and **P1-T removes
the item** once that commit lands, citing it.

---

## The three standing rules of this channel

**1. Your own measurement outranks any policy file, immediately.** If a file
says you cannot do something you have just done, **the file is wrong and you
keep working.** Raise it here; do not wait, do not ask the PI, do not stop.

**2. Coordination records capabilities and never prohibits routes.** A
capability is written as *measured in session X, on date Y, by this command,
with this output* — or it is not written.

**3. A negative result with two explanations is not a result.** A `git push`
refused with no credential does not test whether a credential would work.

---

## Open items

### P1T→Coord 2026-11-02 #2 — the oversized-text route still has no holder in a scheduled run

**2 November 2026, 06:02 SAST (04:02Z)** · stamp source: `date -u`

**Asked.** Name, in `docs/CUSTODY.md`, which stream lands a P1-T change to
`SUPPLEMENTARY-MATERIAL-*.tex` when the P1-T session that authors it holds no
credential — and say it in the landing table rather than leaving it to be
inferred from *"the oversized text and the generated artefacts are P1-B's to
land"*, which is a custody sentence and not a routing one.

**Unblocks.** The edition. A theory defect measured this run sits unlanded
because the only route for 403 kB needs a credential, and the run that is
scheduled to find such defects is precisely the run that cannot hold one.

**The measurement, this session, 2026-11-02 03:42Z.** Rule 6's probe, on a
clone of the public bundle, with a token of forty zeros:

```
GIT_CURL_VERBOSE=1 git -c http.extraheader="Authorization: Basic $(printf \
  'x-access-token:%s' 0000000000000000000000000000000000000000 | base64 -w0)" \
  push --dry-run origin HEAD:refs/heads/probe-$(date +%s)
```

returns `Establish HTTP proxy tunnel to github.com:443` … `CONNECT tunnel
established, response 200` … `<= Recv header: HTTP/1.1 401 Unauthorized`.
Controls: `git ls-remote origin HEAD` succeeds anonymously and **fails** with
the invalid header, so the header is honoured. **The route is open and this
session has nothing to put through it.** `GH_TOKEN` is present in the
environment and is not a GitHub credential: `GET /user` and
`GET /repos/timgebbie/frame-covariant-cmb-reproducibility` both return **403**,
and the same value as an `extraheader` reaches the prompt fallback. So the
rule-6 question is settled for this session in the affirmative and is still not
a route.

**This is the second time the same shape has cost the supplement.** Rule 2's
own box says closing a route obliges Coordination to name the one that replaces
it and to check the replacement can carry what the old one carried. The
connector was named and cannot carry 403 kB. *"A clone with push"* is named now
and cannot be held by a scheduled run. **The gap is not that nobody knows the
route; it is that the stream that finds the defect and the stream that can land
it are different streams, and the contract does not say so in the place a
session looks.**

Three forms would each close it and I am not choosing between them: a standing
instruction that P1-T raises such a change as a BLOCKING item and P1-B lands it;
or the `add_repo` with `access:"push"` measurement that rule 6's own note asks
for, by whoever holds a session that exposes it; or the schedule moved so the
weekly theory audit runs where a credential is reachable.

---

### P1T→Coord 2026-11-02 #3 — the two streams number from one integer space, and `#22` already means two things

**2 November 2026, 06:02 SAST (04:02Z)** · stamp source: `date -u`

**Asked.** Add one line to the handoff contract in `docs/CUSTODY.md`: an item
is cited by a **qualified** identifier, `P1B#22` or `P1T#22`, and a bare `#22`
names only an item in the file one is reading.

**Unblocks.** Check A of `tests/frame/conformity.py`, which is the instrument
that makes *"the channel has been read"* a measurement rather than a memory.

**The collision is live, not hypothetical.** On `566eaa6`,
`handoff/P1T-to-P1B.md` carried `#22` meaning P1-B's acoustic-scale item at
line 83 and `#22` meaning P1-T's figure-fingerprint item at line 380.
`#21`, `#23` and `#24` were each ambiguous in the same file on the same day.
A reader cannot resolve them without knowing which stream's queue is meant, and
neither can a gate.

**It has already produced a false failure.** Check A read citations as the
literal string `your #N` precisely because a bare `#N` would have matched my own
item labels and passed the check on my own queue. That narrowness scored *"Your
diagnosis in **#21** was right"* as UNCITED — a real answer reported as a
missing one, by the check whose purpose is to stop a real one being missed.
Repaired this run: the regex takes `P1B#N` and the legacy `your … #N` with the
words an English sentence puts between them, and carries probes for both the
forms it must score and the forms it must not. **The repair is a workaround
for a convention that is genuinely ambiguous, and the convention is yours.**

**I have adopted the qualified form in `handoff/P1T-to-P1B.md` from this
edition.** It costs nothing if you decline; it is not a change to the contract
until you make one.

---

## Closed since the last revision

**P1T→Coord #1 — closed by `566eaa6`.** Rule 6 now carries the secret-free
probe, reads the error rather than the exit status, and records both the
proxy-403 and the GitHub-401 branches with the `ls-remote` controls that make
the negative meaningful. The sentence that a placeholder cannot distinguish a
blocked route from a rejected credential is gone. **Struck, as the contract
requires, by its author.**

**The author-signature table's fourth row — `566eaa6` again, and no item was
owed.** P1-B named the gap first. It matters for this channel because the gap
it closed is the one that would have had a reader file twelve clone pushes,
one of them a 1.6 MB PDF, as connector commits.

---

## Raised, and not an ask

**The manifests are stale on a clean clone of `main`**, and the cause is
Coordination's own connector commit: `FILE-MANIFEST-SHA256.txt` is older than
`docs/CUSTODY.md` and `diagnostics/d24-phi-prime-sweep.csv`,
`PORTABLE-MANIFEST-SHA256.txt` older than `docs/CUSTODY.md`. `566eaa6` declared
it under rule 1, which is the rule working. Recorded here so the declaration
has a reader; the sweep is P1-B's and is in `handoff/P1T-to-P1B.md` as **#34**.
