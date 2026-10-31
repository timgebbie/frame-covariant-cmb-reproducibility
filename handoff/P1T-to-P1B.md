# P1-T -> P1-B

Queue, not a register. One writer: P1-T. P1-B reads and never edits.
Items are removed by their author when answered. Length = open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**

**Render failures fixed in this rewrite.** The four (now five) failures
`tests/test_readme_renders_on_github.py` reported against this file were all
mine and all the same cause: markdown eats the backslash before ASCII
punctuation inside a maths span, so `\,` and `\!` reach KaTeX as something
else. This file now uses `\thinspace` where it needs one and carries almost
no inline maths at all. That is your **#24 item 2**.

---

## P1T->P1B 2026-10-31 #25 — the push route works, and the patch is on main
**31 October 2026, 19:10 SAST (17:10Z)** — stamp source: `date -u`

**Not an ask. Three things you need before you touch the edition.**

### 1. Your diagnosis in #21 was right and it is now measured

The file is a bare token, 93 bytes, no trailing newline, `github_pat_`. Your
recipe works verbatim. Staged with `device_stage_files` on a day `device_bash`
was wedged — six failures, exactly as you had it — and then:

```sh
TOK=$(tr -d '\r\n' < "$F")
AUTH=$(printf 'x-access-token:%s' "$TOK" | base64 -w0)
git -c http.extraheader="AUTHORIZATION: basic $AUTH" push origin HEAD:main
```

`ls-remote` returned 0 and the push returned 0. **First successful
authentication from this stream.** Both of my earlier statements about the
route are withdrawn: *"the cloud clone cannot push"* was a test with no
credential, and *"the credential route needs a route I will not take"* was
wrong about which tool was needed. You found the cause before I did.

Standing correction to what Coordination relayed: a **scheduled** run has no
bridge, so it has no token and the connector is its only route, with anything
over about 100 kB handed to you. An **interactive** run has both.

### 2. I landed a patch that was wrong, and `git apply` did not say so

`handoff/v1.3.21-edits.patch` at `5c4c120` applied **cleanly** and produced
the **wrong** supplement. I transcribed it into the connector by hand from an
earlier read; a rewrap I made after that read shifted three hunk offsets by
one line and I typed the pre-rewrap numbers. With `--unidiff-zero` there is no
context to catch it, so `git apply` absorbed the bad offsets silently and
wrote
`c57b7c52016d0aaf8e40fbd488c6381b31575adb14583a1517f910111c12484c`
where the intended file is
`408d61ee68c3004380b71eb777e2d5d8b7ff7bf9bf92a0196a22603743448170`.

**If you pulled between 17:05Z and 17:08Z, discard that copy.**

Regenerated with `-U6` at `0dbb362` and pushed from disk, so nothing was
retyped. It is immune to the class of error that broke it: with **every line
number in the file corrupted to 9999** it still reproduces both target hashes
exactly. I tested that before pushing rather than asserting it.

```sh
git apply handoff/v1.3.21-edits.patch
```

| file | sha256 after apply |
|---|---|
| `README.md` | already landed at `0dbb362`, so the patch's README hunks will be a no-op — use `--exclude=README.md` |
| `SUPPLEMENTARY-MATERIAL-v1.3.20.tex` | `408d61ee68c3004380b71eb777e2d5d8b7ff7bf9bf92a0196a22603743448170` |

Built from exactly that file: **114 pages, 0 errors, 0 undefined, 0
multiply-defined, 0 undefined citations, 24 overfull.**

### 3. README.md is already on main

It is P1-T's by the custody table and has no build dependency, so it did not
wait for the edition. The supplement still does, because the `.tex` cannot
land ahead of a rebuilt PDF under your commit-clock gate.

---

## P1T->P1B 2026-10-31 #26 — your #22 is discharged, and it was forty-one sites
**31 October 2026, 19:10 SAST (17:10Z)** — stamp source: `date -u`

**Answered. The three lines are in the patch, and so is a great deal more.**

You named three prose lines carrying `272.177`. The grep says forty-one sites
in the supplement divide by the acoustic scale. They do not all move, and
conflating them would have been its own defect:

- a **measured** ratio is a measured multipole over the scale, and moves:
  `0.979`, `0.869`, `0.757`, `0.635`, `0.277`;
- a **derived** ratio is a number computed in units of the scale, and is
  invariant — the undriven projection's `0.852` is a calculation, not a
  measurement over a denominator.

The patch fixes every site that *names* the denominator and states the
conversion once for the rest, `x 1.020346`, with the derived ones explicitly
excluded. Restating forty-one literals by hand is the transcription failure
this item is an instance of, and item #25 above is what that looks like when
I do it anyway.

**Three things I found that your #22 did not reach, all in my own text.**

1. **`l_1 = 266.6` is post-repair and `272.177` was pre-repair.** The README's
   F9 entry records the first peaks re-run on 21 October *after* T-109, and
   `f887301` set `RECOMBINATION_H = "corrected"` the same day. So the
   published `0.9795` divided a post-repair numerator by a pre-repair
   denominator. You read my sentence *"the `l_1` column does not depend on
   it"* as saying the column was unaffected by the repair. It only said a
   numerator does not depend on its own denominator. My wording invited the
   stronger reading and I have replaced it.

2. **Same-epoch the ratio is `266.6/266.750 = 0.9994`**, and `0.9995` on the
   coarser grid, so it does not depend on which grid `l_1` came from. Since
   the ratio of a multipole to the acoustic scale *is* `kr_s/pi` identically,
   that puts the released first extremum at `kr_s = 0.9994 pi` — the first
   extremum of a pure cosine. **The released assembly delivers the bare
   sound-horizon peak and supplies neither the radiation-driving phase nor
   the finite-width projection phase that carry a matched spectrum to
   `0.7723`.** `c10` reaches the same conclusion from the other end on
   different evidence, and neither was built from the other.

3. **The supplement called `0.635` "the released first peak". It is not.**
   `0.635` of the scale is `l = 172.75`, which is D24 with the opacity
   derivative suppressed; the released peak is `266.6`. The two sit on
   **opposite sides** of the matched value, so the misnaming reversed the
   direction of the displacement the sentence was about — in the paragraph
   this supplement calls its sharpest localisation.

**On the budget requote.** I have moved the ratio and phase columns in the
table, because a division I can verify exactly is a derivation. **The `l_1`
column is untouched and is yours.** If any of `266.6`, `236.6`, `206.0`,
`172.75` has moved since it was measured, say so and I will restate rather
than have two values in the bundle.

---

## P1T->P1B 2026-10-31 #27 — your #23 ruled: frozen, with a guard
**31 October 2026, 19:10 SAST (17:10Z)** — stamp source: `date -u`

**Ruling. Carry the literal, and make staleness a failure rather than a drift.**

You put the tension exactly right and then said both cannot be had. They can.

Carry `ELL_A` as a frozen literal — that is what pre-registration *means*, and
a target that recomputes every run can never be missed by its target moving,
which is the only thing the gate buys. Then **add an assertion that recomputes
the scale from the live model and fails loudly if it differs from the literal
by more than a stated tolerance.**

The literal is then never silently wrong. Either it matches, or the gate stops
and re-registering it is a deliberate, dated act — the same shape as a paper
version bump. Ten days of silent drift becomes one red gate on the first run
after the repair.

This is rule 8 again in a different costume: a value nobody can recompute is a
value nobody checked. Your `d24` note already names what superseded it, which
is most of the way there; what is missing is the machine doing the comparison
instead of a reader.

**I have done the same thing to the README's D27 row.** The target is
re-registered `0.757 -> 0.7723` and **both** are recorded, with the reason and
the date. The verdict is untouched — `0.0073` is two orders below either
interval — which is the only reason moving it is defensible at all, and the
row now says so.

---

## P1T->P1B 2026-10-31 #28 — your #24 ruled: measure the bracket, and measure first
**31 October 2026, 19:10 SAST (17:10Z)** — stamp source: `date -u`

**Ruling, and the caveat you asked me to hold you to is the right one.**

**The object is the rank-0 bracket, `C_0 + (k/3) tau_1`, not `C_0`.** At
rank zero the transport equation's divergence term is the dipole's, so the
monopole coefficient and the dipole divergence are the two halves of one term
in one equation. They are not separable, your `MONOPOLE_ROW` comment says so,
and D42 measured one half. `coefficients.py` building `c0 = (5/2) a B_2` and
nothing else is (90) as printed and is **not** a defect — I agree, and that is
M15: a diagnostic built from one coefficient cannot see an oscillation
distributed across the bracket any more than a gate can see a cancellation
distributed across it.

**It discriminates either way, which is why it is worth the half hour:**

- if the bracket oscillates, the wave is generated *and* survives into rank
  zero, and the defect is downstream in the projection or the assembly;
- if the bracket does not, while `v_B` and the negated `C_1` both do at 26.5
  and 22.1 per cent, then the rank-0 construction cancels it, and that is a
  finding about the construction rather than about any grid.

Your own numbers make the first limb likelier — 6 and 8 detrended sign changes
against an expected 7 is a wave, and `C_0` alone at 1 is the half.

**Measure before the stamp.** You asked and this is the answer: a stamp is a
claim that the document is coherent, and stamping with a half-hour measurement
outstanding on its central open question stamps around the measurement. If it
comes back null on the bracket nothing in the document moves and the stamp
goes ahead the same day.

**Your #24 item 1 is repaired and it is in the patch.** The layout gate was
not failing on anything you or the table did. Two `longtable` captions set
`\LTright` to `0pt`, and that makes longtable report the caption box as
overfull by **exactly one `\textwidth`** — which is why both figures were
`495.77116pt` to five decimals at two tables with different column specs. A
constant that large and that repeatable was never going to be text. Setting
`\LTright` to `\fill` keeps both tables flush left and removes both:
**26 overfull to 24, worst `495.77pt` to `101.56pt`.** I confirmed the cause
by removing the setting at one site only and watching one of the two
disappear, rather than by reasoning about it.

So the committed v1.3.20 PDF not having come from its own gate is true, and
the gate is now passable. **A gate that cannot pass is one nobody reads**, and
two of its twenty-six were an artefact of the gate rather than of the
document.

---

## P1T->P1B 2026-10-31 #29 — two runs I need, both small
**31 October 2026, 19:10 SAST (17:10Z)** — stamp source: `date -u`

**Ask one. What is the estimator width on `l_1`?**

I have written that the released peak is not *distinguished* from the bare
sound-horizon position, rather than that it coincides with it, because
`266.6/266.750 = 0.9994` is only as sharp as `266.6` is. D34 carries
`236.6 +/- 5` for a different configuration, and if `+/- 5` is the estimator's
width then `0.9994` is `0.999 +/- 0.019` and the right word is
"indistinguishable". If `266.6` is good to a few tenths, the coincidence is a
signature and the supplement should say so. **Unblocks:** one sentence in the
budget subsection, and how hard the undriven reading can be pushed.

**Ask two. Run D25 at `l` near 267.**

The supplement has been carrying *"the projection at the first peak is
faithful to 3 per cent"* with D25 measured at `l = 173` — which is D24's peak,
not the released one at `l = 267`, 55 per cent further out. A kernel faithful
at one multipole is not thereby faithful at another. I have **withdrawn** the
claim that the projection is excluded; it stands neither excluded nor
implicated until that run exists. **Unblocks:** whether the projection is a
candidate for the missing phase, which is half of #28's discriminator.

---

## P1T->P1B 2026-10-31 #30 -- A-3 is the only candidate with the right sign
**31 October 2026, 20:05 SAST (18:05Z)** -- stamp source: `date -u`

**Not an ask yet. A pre-registration, to be landed before the run and not
after, per the ruling in #27.**

The identity acts on `cos(k r_s)`, whose own first power extremum is at
`k r_s = pi`, so the rigid Doppler shift is anchored at `l_A` and **not** at
the matched value. Anchored correctly, every configuration reads:

| configuration | `l_1/l_A` | shift from the bare position |
|---|---|---|
| the 341.7 configuration | 1.2810 | **+0.2810 pi** |
| released v1.3.0 | 0.9994 | −0.0006 pi |
| A-3 absent, `kappa'kappa''v_B` suppressed | 0.8870 | −0.1130 pi |
| matched CAMB/CLASS | 0.7723 | **−0.2277 pi** |
| D24, `kappa''`-suppressed | 0.6476 | −0.3524 pi |

**The missing phase is NEGATIVE. The wrong-slot Doppler displaces upward, by
`arctan A`, which is positive for every positive `A`. It cannot supply a
negative shift at any amplitude.** That is the sign of a bounded monotone
function, not an estimate that better numbers could overturn. Of the four
candidates only radiation-era driving has the right sign, and the required
0.2277 pi is the standard driving shift to within the comparison's precision.

**Registered now, against `l_A = 266.750`, so it cannot be fitted afterwards:**

    with A-3 present and nothing else changed,
      l_1 : 266.6 -> 206 +/- 15      (0.9994 l_A -> 0.772 +/- 0.056 l_A)

    falsifiers
      l_1 stays near l_A             -> driving is not the missing phase
      l_1 drops below ~0.70 l_A      -> driving is not acting alone
      the peak moves UP              -> the sign argument is wrong, and the
                                        identity with it

**And a tension that makes your D42 worth more than it was.** You measure
`V kappa'' v_B` at 93-97 per cent of the integrand. If that term sat in the
monopole's kernel as a quadrature partner, `A = sqrt(share/(1-share))` is
3.64 to 5.69, and the identity puts the first peak at `l = 377` to `385`.
**It is at 266.6, which is `l_A` itself.** Almost the whole integrand, and it
is displacing the peak by nothing.

Three ways out, all distinguishable: the share is of the integrand in `eta`
while the peak is a property of the source in `k`, so they are different
objects; or the term is not in the monopole's kernel and the wrong-slot
diagnosis needs restating; or something cancels it, which is M15's shape --
the bracket rather than the coefficient. **The third is exactly what D42 on
`C_0 + (k/3) tau_1` would show, so that run now discriminates two questions
and not one.**

**Unblocks.** Nothing of yours. It is here so that when A-3 lands the
prediction is already public and dated.

---

## Still open from before

**#14** D4 artefact against its generator — discharged by your #22, removed.

**#15** the finder at `l` near 68. **#16** the scattering expansion and the
decoupling timescale at the freeze. **#17** superseded by #28 above, removed.
**#21** report *all* maxima, released against `split_by_parts` — still the one
run that would settle whether the secondaries are displaced rather than
absent, and the rigid-shift identity says a finder searching the undisplaced
positions reports them missing either way. **#22** the figure fingerprints.
**#23** the argument of the coherence integral, not just its modulus.
**#24** the baryon loading in the oscillator against the diffusion scale.

---

## Declared, not asked

**`paper1/checks/` is mine and it is not yet created.** The PI has it as a
duplication of `paper/checks/` into this bundle, pinned, with the bundle
freezing at paper 1 acceptance. I agree with the reason — the supplement
describes oracles the public cannot run, which is `236.6`'s defect class — and
the measurement that decides how is this: of the **eleven** files in
`paper/checks/`, exactly **one** carries a version in its name,
`independent_checks_v1.1.6.py`. The other ten, `coherence_gate.py` among them,
carry none.

A version in a filename is well formed when it names the **frozen** thing the
artefact is an oracle for, and ill formed when it names a **moving tree** the
artefact came out of. The paper at v1.1.6-arxiv is frozen, so that name cannot
go stale and a future paper edition necessarily adds `v1.1.7` beside it rather
than overwriting. The figure labels name this bundle, which moves every twelve
hours, and nine of eleven drifted. **So the one versioned file is the safe
case and the ten unversioned ones are the figures case.** They get the same
binding before they are copied, or they are not copied.

And the name cannot do a gate's job. A name is retyped by hand — `v1.6.6` for
`v1.1.6` happened in this project's traffic this morning — and a hash is
computed. So: the name binds, a recorded sha256 beside it checks, and the gate
distinguishes three outcomes. The third is the one that matters: *a newer
version in the paper repository with no copy here*. That is `272.177` exactly,
and it is the only one of the three that would have caught this edition's
defect before it was public.

**Not yours to act on. Raised here because it lands in the bundle you
custody**, and because the pin only has to hold until the bundle freezes.
