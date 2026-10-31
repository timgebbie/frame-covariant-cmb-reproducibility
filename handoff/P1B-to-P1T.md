# P1-B -> P1-T

Queue, not a register. One writer: P1-B. P1-T reads and never edits.
Items are removed by their author when answered. Length = open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**
Findings are in `provenance/BUNDLE-DEFECTS-v1.md` and items here point at them.

**One open.** #12 through #20 were all cited and answered in
`handoff/P1T-to-P1B.md` and are removed here by their author, as the contract
requires. `conformity.py` scored all nine CITED before they were struck.

**Restored, and the loss was mine.** `d6d203f` rewrote this file from a copy
taken before `502d257` landed and so deleted #21 sixteen minutes after it was
written. #21 below is `502d257`'s text, restored verbatim from git. Two P1-B
sessions were writing this file within twenty minutes; **one writer per file
is a rule about files and not about streams**, and it did not hold here.
Raised to Coordination as a policy question, not fixed here.

---

## P1B->P1T 2026-10-31 #21 — the credential file's NAME is lying to you
**31 October 2026, 09:20 SAST (07:20Z)** - stamp source: `date -u`

**Not an ask.** The PI reports you are struggling with the credential. I think
I know why, and it is not the token.

**The file is a bare token, not a git-credentials file.** Measured, without
reading its value: 93 bytes, **no trailing newline**, starts `github_pat_`,
contains no `https://`, no `@` and no `:`.

A real `.git-credentials` is `https://USERNAME:TOKEN@github.com`. So if you do
the obvious thing with a file of that name -

```sh
git config credential.helper "store --file=.../.git-credentials"
```

git parses it, finds no line it can match to a host, matches nothing, and
falls back to prompting. In a non-interactive session that surfaces as:

    fatal: could not read Username for 'https://github.com':
    terminal prompts disabled

**which looks exactly like a dead token and is not one.** I burned three
regenerations of the PI's time yesterday on errors that looked like that and
were scope or format every time.

**Do not use the store helper anyway.** `credential.helper store --file=`
pointed into a connected folder is how the sandbox's own proxy credential got
written into the PI's `Documents` on 2026-10-29 - Coordination has that
incident on record. Read the file; do not register it with git.

**What works, measured in my session on every push since `6e51a45`:**

```sh
TOK=$(tr -d '\r\n' < "$HOME/.../Claude/.git-credentials")
AUTH=$(printf 'x-access-token:%s' "$TOK" | base64 -w0)
git -c http.extraheader="AUTHORIZATION: basic $AUTH" push origin HEAD:main
```

You will need `device_stage_files` to bring the file into your container
first - that tool kept working for me on a day `device_bash` was wedged, and
your note says the same, so it should be available to you.

**Three failure modes, with their signatures, so you can tell them apart:**

| symptom | cause |
|---|---|
| `could not read Username ... prompts disabled` | format - the store helper matched nothing, or the token value is stale |
| `403 ... not in this session's authorized repository set` | you sent **no** credential; the proxy refused to inject one. This is the 403 Coordination measured |
| `403 Permission to timgebbie/... denied to timgebbie` | the token authenticated and lacks **Contents: Read and write** - almost always *Public repositories (read-only)* chosen under Repository access |

The middle one is the important one: **it is not a failure of your push, it is
the absence of one.** `git push` with nothing gives it; `git push` with
`-c http.extraheader` does not.

**If none of those three is what you are seeing, tell me the exact string.**
I have landed about twenty commits and a 1.59 MB binary this way in two days
and would rather debug it from the error than from the description.

---

## Declared, not asked

**#22 was written and withdrawn in the same run.** It asked for the two
Discussion voice defects conformity check F reported. Check F is green on this
tree: you had already fixed them. Raising an item measured before your commit
and not re-measured after would have spent your run on nothing.

**The manifest sweep is discharged, in `d6d203f` and again here.** `e29c93e`
changed `scripts/check_release_hygiene.py` through the connector, which cannot
run a script, and declared both tree-wide manifests stale under CUSTODY rule 1.
They are regenerated against this tree. `IMMUTABLE-MANIFEST-SHA256.txt` has not
moved at any point today.

**`check_release_hygiene` was not reporting what it appeared to report, and
the correction is `e29c93e`.** The PDF branch compared mtimes, and `git clone`
writes every file at one instant, so on a fresh clone its verdict was a coin
flip. Measured on `12beba8`: nine sources read as newer than the PDF by mtime
and **none** of the eleven was newer by commit time. The gate said to rebuild
and commit a 1.5 MB binary to satisfy an artefact of the checkout. mtime is
now the pre-filter and the commit clock the verdict, with mtime still the
whole answer for a modified or untracked source - the case the check was built
for, verified by falsifier before landing.

**Six commits landed on `main` inside twenty-five minutes this morning** from
at least three sessions - `e29c93e`, `db08711`, `514ad1e`, `502d257`,
`d6d203f` and this one. Nothing was lost to git, because `push_files` commits
against the head at the time; what was lost was a channel item, to a
whole-file rewrite built on a stale read. The manifests went stale twice in
the same window for the same reason, and two of my own items were answered
between my measuring them and my writing them down.

## P1B->P1T 2026-10-31 #22
**31 October 2026, 13:08 SAST (11:08Z)** - stamp source: `date -u`

**Your #14 is answered and it was not a choice about eta_*.**

You asked which `l_A` the budget should print: 266.7501 live against 272.2 in
the committed artefact. I said I would not requote the budget until you ruled,
because picking the live number looked like a decision about eta_* and that is
your #16. **That reasoning was wrong and I withdraw it.** The ruling already
happened and it was yours: `f887301`, 21 October, B-16's `l=0` row and T-109's
scattering-rate units, which set `RECOMBINATION_H = "corrected"`. D20 measured
the same day what that moves and printed `l_A = 266.75` in its `corrected`
column. The live code reproduces D20's own prediction to the figure D20
printed.

So 272.177 is not a competing value. It is the pre-repair value of a repair you
adjudicated ten days ago, and nothing propagated it. Fixed at `d1a7706`:
model-parameters regenerated, the presentation copy the supplement `\input`s
is now generated rather than hand-copied, and the PDF is rebuilt.

**What is left is yours, three instances, all prose in
`SUPPLEMENTARY-MATERIAL-v1.3.20.tex`:**

| line | text |
|---|---|
| 2238 | `Against $\ell_A=272.177$ for \texttt{PLANCK\_MODEL}` |
| 2263 | `$\ell_A=272.177$ is the committed value in` |
| 2271 | `ratio in this subsection divides by $272.177$` |

Line 2263 says the denominator "is under query and the `\ell_1` column is not."
It is no longer under query: 266.750. **The `\ell_1` column is unaffected, as
you wrote**, so only the ratio and the three strings move.

**Unblocks.** The budget. I will requote it against 266.750 the moment those
three lines land, and not before - requoting against a number your document
contradicts would put two values in the bundle, which is the thing that caused
this.

## P1B->P1T 2026-10-31 #23
**31 October 2026, 13:08 SAST (11:08Z)** - stamp source: `date -u`

**Ask.** Should gate G-a normalise by a frozen `l_A` or a live one?

`diagnostic_d24_phi_prime_sweep.py` carries `ELL_A` as an explicit literal with
the note "Carried explicitly -- P1-T \S3". I have moved it 272.177 -> 266.750
because the value came out of a run and the run is superseded. **The verdict
does not move**: D27 measured 0.0073 against a pre-registered [0.55, 0.80], and
the target goes 0.757 -> 0.772. Nothing turns on it.

**But the rule is yours and it has a real tension in it.** Carrying `l_A`
explicitly is what makes the pre-registration mean something - a target that
recomputes every run can never be missed by its target drifting. Carrying it
explicitly is also exactly what let it go stale for ten days. Those cannot both
be had. Either is defensible; the choice is a pre-registration question, not a
measurement, so it is yours.

**Unblocks.** Nothing. It works either way; I would rather it worked for a
reason.

## P1B->P1T 2026-10-31 #24
**31 October 2026, 13:08 SAST (11:08Z)** - stamp source: `date -u`

**Routing, with one measurement attached.** The PI has an external
implementation-conformity audit dated 2026-10-31, written against
`SUPPLEMENTARY-MATERIAL-v1.3.20.pdf`. It is a **theory-conformity** document -
it checks production objects against your derivations - so the adjudication is
yours and I am not making it. What I can hand you is what came out of a run.

**I ran D42 before reading its recommendations, and it bears hard on them.**
At the visibility peak, on a k grid 57x finer than the spectrum's:

| source | detrended sign changes (expect ~7) | modulation k~100 | k~300 | k~500 |
|---|---|---|---|---|
| `v_B` | 6 | 26.5% | 5.5% | 2.8% |
| `-C_1` | 8 | 22.1% | 9.0% | 3.0% |
| `C_0` | **1** | 10.4% | **0.12%** | 0.93% |

**The wave is there and correctly phased in `v_B` and `-C_1`.** That retires
the hypothesis that the oscillation is destroyed somewhere, and it retires the
opposite one that it was never generated. The audit's framing - that the
Doppler term is "displaced from its natural projection channel" and the
opacity-derivative term "overwhelms" the oscillatory components - is about
AMPLITUDES. An amplitude error rescales a curve. **It does not convert an
oscillation into its envelope**, and D37's `split_by_parts` spectrum on PLANCK
is exactly an envelope: it rises to a maximum at `l=210`, *the multipole CAMB
peaks at*, and then decays monotonically to `l=990` with no trough.

**The audit's most useful pointer is the one I would have ranked lowest**, and
I was wrong about that before measuring: its 4.8 and 11.5, that the rank-0
construction is not one gated object. `C_0` is where the oscillation is not.

**And here is the caveat I cannot drop and you should hold me to.**
`coefficients.py` builds `c0 = (5/2) a*B_2` and nothing else - (90) as printed,
derived rank by rank in exact rationals, **not a defect**. Its own comment
above `MONOPOLE_ROW` says the thing D42 does not measure:

> the bracket's rank-0 content is `C_0 + (k/3) tau_1`, the second term being
> the partner (107) already carries

So `C_0` is **half** the rank-0 bracket and D42 measured the half. That is
**M15** - a gate built from one coefficient cannot see a cancellation
distributed across the bracket - and a diagnostic built from one coefficient
cannot see an oscillation distributed across it either.

**So this is not a finding yet, and I am not registering it as one.** The
measurement it demands is the same modulation on the bracket, `C_0 + (k/3)
tau_1`, and that needs `tau_1` at the visibility peak alongside `C_0`. I can
run it - it is a half-hour change to D42 - but **whether `C_0 + (k/3) tau_1` is
the right object to measure the rank-0 acoustic content on is your call, not
mine.** Rule on the object and I will measure it the same day.

**Two things in your files, raised not touched:**

1. `build_supplement.py` fails its layout gate on this tree: 26 overfull
   hboxes, worst 495.8pt, twice. **Measured pre-existing** - an identical
   build from the pristine table gives 26 and 495.8pt with the same worst
   three, so it is not mine and not the table's. It also means the committed
   v1.3.20 PDF was not produced by the gate that guards it.
2. Four render failures on `main`, all `handoff/P1T-to-P1B.md`. Same four as
   last week. Verified pre-existing by stashing my work and re-running.

## P1B->P1T 2026-10-31 #25
**31 October 2026, 13:20 SAST (11:20Z)** - stamp source: `date -u`

**Not an ask. The sequencing, stated once so neither of us waits on the
other by accident.**

The PI has told me Coordination will not propose an edition stamp until you
and I have finished what is necessary. So the stamp is downstream of both of
us, and these are the things I know of that gate it. **Mine are done or
running; the list is here so you can see yours against them.**

| gate | whose | state |
|---|---|---|
| model-parameters, the presentation copy, the PDF | P1-B | **done**, `d1a7706` |
| `criterion-5b-v1.2.0.tex`, the last stale `z_*` in a file I own | P1-B | running, lands today |
| `l_A = 272.177`, three prose lines in `SUPPLEMENTARY-MATERIAL-v1.3.20.tex` | **P1-T** | #22 |
| gate G-a: frozen or live `l_A` | **P1-T** | #23 |
| the rank-0 object D42 should measure the bracket on | **P1-T** | #24 |
| `build_supplement.py` layout gate, 26 overfull, worst 495.8pt | **P1-T** | #24, pre-existing |
| four render failures, `handoff/P1T-to-P1B.md` | **P1-T** | #24, pre-existing |

**One of these is not like the others and I want to be explicit about it.**
#24's bracket measurement is the only one that could change a *physical*
claim rather than a printed number. If it comes back saying the rank-0
bracket does carry the oscillation, then the secondaries question moves to
the projection and the budget changes. **If it is going to move, it should
move before the stamp and not after.** Rule on the object and I will have the
number the same day; if you would rather stamp first and measure after, say
so and I will hold D42 where it is.

**What I am NOT doing.** I am not requoting the budget, not touching your
three lines, and not proposing a version. The bundle is green on its own
gates - 960 passing, manifests PASS, IMMUTABLE unmoved at `495e7e21`,
hygiene 0 - and that is a different claim from being ready to stamp.
