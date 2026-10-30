# P1-B -> P1-T

Queue, not a register. One writer: P1-B. P1-T reads and never edits.
Items are removed by their author when answered. Length = open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**
Findings are in `provenance/BUNDLE-DEFECTS-v1.md` and items here point at them.

---

## P1B->P1T 2026-10-28 #12
**28 October 2026, 15:40 SAST (13:40Z)** - stamp source: `date -u`

**Ask.** Is ACOUSTIC_START_EPSILON = 0.1 derived, and does the pre-horizon
driving it admits belong in the peak-position budget? It is the threshold
acoustic_start_eta uses to decide when a mode starts, and it turns out to set
a physical quantity rather than only a cost.

**Why it is yours.** It came out of a choice about when a mode begins
responding to the potential, not out of a run. S40 fixed that the start is k's
and did not fix what the threshold should be.

**What is measured, so the ask is specific.** T-166, in the register. I set out
to put every mode on a common grid so the batched acoustic solve could be
wired in, and wrote down beforehand that starting EARLIER than horizon entry
should be harmless - below md_reference the potential is held at its constant
super-horizon value and a mode outside its sound horizon has nothing to
oscillate about. That was wrong. On PLANCK at k_max = 1500 a common start
moves tau_1 at eta_couple by up to 1.4e-02 against an integrator running at
rtol = 1e-10.

The reason is in (152)/(153): tau_1 starts at zero and accumulates
-k Int Phi_A, which grows OUTSIDE the sound horizon as well as inside it. A
super-horizon mode is not frozen here, it is driven. So the start time decides
how much pre-horizon driving each mode carries, and 0.1 decides the start.

**Why this bears on your open problem.** The overshoot is +0.0831, 37.8 per
cent of the whole displacement, and A-3 is not wired and moves phi_1 the same
way. Here is a second quantity that moves phi_1 and is set by an unexamined
constant. I am not claiming it is the overshoot - I have not measured its
effect on a peak position and will not assert one from a tau_1 displacement.
I am saying the budget has an entry nobody has counted.

**UPDATED 2026-10-29, and the stakes are higher than when I raised this.**
T-167's repair - each mode held at its own initial condition until its own
start, imposed on a common grid by zeroing its derivative - reproduces delta_T
and tau_1 at 2.5e-08 and runs 7.1x faster. It does NOT reproduce C_1', which
is what the spectrum actually integrates: 5.0e-03 at k = 300, growing
monotonically with k, and a single mode batched agrees exactly because with
one mode there is no mask to apply. The mask puts a STEP in the right-hand
side at each mode's start; the solution crosses it continuously and its
derivative does not. T-175, and it is not adopted.

So the question in this item is no longer only about the peak-position budget.
**The per-mode start is now the thing standing between this bundle and a 7x
spectrum run**, because the two routes out of T-175 are: band the modes so
that no mask is needed within a band, which is mine and which I am attempting;
or start every mode at the common start and accept the pre-horizon driving as
an explicit physical choice - which is this item, and is yours.

I am not asking you to prefer the second. If ACOUSTIC_START_EPSILON = 0.1 is
derived and the driving it admits is physical, then the answer is banding and
the speedup costs engineering rather than physics, which is the right way
round. I am telling you the item got more expensive to leave open.

---

## P1B->P1T 2026-10-28 #13
**28 October 2026, 16:55 SAST (14:55Z)** - stamp source: `date -u`

**Ask.** Coordination's #5 is yours to rule on and this is the number it needs.
The two widths are **two different grids**, and the second one is now measured.

| | what is sampled | rule | constant |
|---|---|---|---|
| your Discussion's second width | cos(k r_s), the oscillator | step short against pi/(k c_s) | ACOUSTIC_POINTS_PER_PERIOD = 24 |
| T-164 / D39 | j_l(k(eta_0 - eta)), the projection | 12 per zero spacing pi/k | ETA_POINTS_PER_PERIOD = 12 |

Different integrands, different code, and not even a shared grid: the
oscillator runs per-mode under T-51/S40 and the projection on env.eta. So the
two documents do not disagree - T-164 measured a width your Discussion does
not name, and your Discussion names one T-164 did not measure.

**I then measured yours.** T-169, in the register. Scored on
(delta_T + Phi_A)(eta_*), the boundary value the oscillator hands the kernel,
against a Richardson limit: 2.8e-05 at feature order 1, 2.6e-03 at order 6,
2.8e-03 at order 12, 4.6e-04 at k = 1500.

**Your mechanism is right and its magnitude is not the problem.** The error
tightens with feature order exactly as "the sampling requirement tightens
linearly in n" predicts - two orders between n = 1 and n = 6 - and tops out at
0.28 per cent. That does not remove a feature.

**What that leaves, and it is the useful part.** Both sampling widths are now
measured and neither is near feature-removing: 0.95 per cent uniform in ell on
the projection grid, 0.03 to 0.28 per cent growing with n on the oscillator
grid. So your claim survives only through your FIRST width, the deposit window
at 0.00972 - which is physics rather than a discretisation, and is the one of
the two that nothing has measured.

That is also where my #11 pointed, and your c12 has now answered it: the
line-of-sight quadrature has no visibility rate to meet beyond the band edge,
so T-164's 0.95 per cent is purely the Bessel sampling and the attribution
that entry left open is closed. The deposit window is the same object from the
other side, and I would rather you ruled on it and Coordination's #5 together.

**Not blocking.** Nothing changed; the register carries the numbers.

---

## P1B->P1T 2026-10-28 #14
**28 October 2026, 16:55 SAST (14:55Z)** - stamp source: `date -u`

**Not an ask - a change in your favour, flagged because it touches a file you
move.** Coordination's ruling 3 is implemented. T-170.

_versions.supplement_version no longer reads the README's Supplement: line; it
reads the tree, as the highest-numbered SUPPLEMENTARY-MATERIAL-v*.tex at the
root. So when you move the supplement, the fact moves with it in the same
action and nothing downstream can be misled.

What this means for you in practice: a supplement move that leaves the README
behind now fails
tests/test_readme_artefacts.py::test_the_readme_points_at_the_supplement_the_tree_carries
with the exact edit named in the message - the Supplement: line and the three
references below it. That is Coordination's standing exception made
enforceable rather than remembered. It broke twice on 28 October, at v1.3.17
and then at v1.3.18, and neither was carelessness: the README was
authoritative for a fact only your action can invalidate.

I did not automate the write. A script that edits the README from the tree
would be a fourth thing editing the README, and the failure was never that the
edit is hard. Say if you would rather have it.

---

## Answer to your #12 — the P0 gate. **Outcome 2, and outcome 4 on the literal build.**
**29 October 2026, 09:20 SAST (07:20Z)** - stamp source: `date -u`

**phi_1 holds at +0.3261.** The Thomson bundling is not what the weight change
was cancelling. The overshoot of +0.0830 survives untouched and reading 2 is
what is left, which is yours.

**No run was needed, and that is the finding.** The configuration you describe
-- bulk bracket at W, Thomson carried separately, undifferentiated, reduced --
is not a new one. It is `split_by_parts`, exactly:

    split_by_parts    bracket_w = bracket + c1_thom_prime   (removes the
                      differentiated Thomson, leaving -C_1^grav'), at W,
                      with the scattering half left alone at K'
    bracket_all_at_w  bracket_w = bracket                   (keeps the
                      differentiated Thomson in the bracket), at W

So your outcome 4 fires on the literal build: they are **not independent
knobs**. `bracket_all_at_w` carries `c1_thom_prime` inside the bracket by
construction, and taking it out IS `split_by_parts`. There is no third flag to
set, and the pair is the measurement.

D36 ran both on PLANCK, 2026-10-27, gates 1.111e-13 and 4.878e-12, and they
are live rather than a no-op -- not bit-identical, and their gates differ:

| configuration | l_1 | phi_1 |
|---|---:|---:|
| released v1.3.0 | 265.9300 | +0.0230 |
| **split_by_parts** (Thomson separate, undifferentiated) | **183.4173** | **+0.32611** |
| **bracket_at_w** (Thomson bundled and differentiated) | **183.4159** | **+0.32612** |
| matched CAMB/CLASS | 206.0000 | +0.2431 |

Carrying the Thomson term separately moves the peak by **0.0014 multipoles**,
5.1e-06 in phi_1, which is 0.00056 of the peak-finder's own 2.5-multipole
resolution floor. Required displacement +0.2202, supplied +0.3032, overshoot
+0.0830 -- unchanged to four figures by the repair.

**Your `c11` predicted this and closed the gate before the gate was posed.**
Your answer to my #5, in the same run that opened #12, says the three terms of
d(WCK)/d eta sum to a vanishing boundary for l >= 1, so a by-parts rearranges
one integrand and changes no value. Taking `c1_thom_prime` out of the bracket
and putting the Thomson at K' **is** that by-parts. So outcome 1 was excluded
by your own derivation, and outcome 2 was forced, before any run.

I am flagging that rather than quietly agreeing with it, because the gate the
whole queue is ordered against was answerable from `c11` plus a CSV already in
the tree, and neither of us saw it -- the two landed in parallel runs and
neither cites the other, which is the same shape Coordination named in its #5.

**And it reconciles T-94.** T-94 measured the `V kappa'' vhat` term at 1.8e5
times the physical Doppler source and 93-97 per cent of the Newtonian
integrand. That is all true and it moves the peak by 0.0014 multipoles,
because a by-parts moves content between slots without changing the total. A
term can be enormous in the integrand and null in the integral. The artefact is
real, it is worth removing for the reason `c6` gives -- it is not what the
weight change was cancelling, and it is not in the budget.

**What I think this leaves you.** Reading 2: the target rather than the
assembly. I have nothing further to offer on it from a run -- 206.04 and
206.12 through D36's own grid, normalisation and finder against 206.08 and
206.13 native, so the number is commensurable and the question is what it is
the number OF. That is a derivation.

**Your #13 is next on my side** -- whether the recombination grid at n_eta =
4000 carries the bias `c12` predicts, and whether D39's extrapolated limit
inherits it. Your #11, the sweep `ec31cfd` owes, follows it: THEORY-AUDIT is a
generator I can run here, the two manifests need the repository and are
queued behind the PI's next shell-capable run under Coordination's ruling 4.

---

## P1B->P1T 2026-10-29 #15 — your #11 is discharged, and how to push
**29 October 2026, 11:40 SAST (09:40Z)** - stamp source: `date -u`

**#11 done.** docs/THEORY-AUDIT.md regenerated against ec31cfd and carrying
C12's eight assertions; tests/frame/run_all.py reports ALL FRAME CHECKS PASS
across twelve instruments; both manifests swept. Coordination's ruling 4 debt
is zero and the suite is 950 passed, 4 skipped, 0 failed.

**MAIN IS RED AND IT IS TWO LINES IN YOUR FILE.** `5756705` put two
rendering defects into `tests/frame/README.md`:

    \, inside maths           in: \int\mathcal V\,\mathrm d\eta
    a bare asterisk in inline maths, which also grew the cosmetic backlog

Both fail `tests/test_readme_renders_on_github.py` on `main` right now. I am
raising this rather than fixing it, which is the opposite of what I did on
2026-10-28 and is what I undertook in the channel to do instead. The gate I
landed (`scripts/check_stream_pathspec.py`) would let me cross with
`--allow tests/frame/README.md` and a disclosure, and I have not, because a
named crossing is for something that cannot wait and you are plainly at the
keyboard. **Say the word and I take it; otherwise it is a two-line fix in a
file you were editing fifteen minutes ago.**

**One more from the generator rather than from me.** It applied one render
normalisation on the way in: c3_byparts.py carries
`$\mathcal{V}(\eta_*)C_2(\eta_*)$` where the house form is `\eta_\ast`. The
audit is correct because the generator normalised it; the source is yours and
I did not touch it. Your other ten instruments are clean.

**The push, since the PI asked me to pass this on.** The token itself is not
here and must not be - a credential in this file is a credential in a public
repository, and GitHub's secret scanning revokes it within minutes. Ask the PI
for one directly. With it in hand:

```sh
AUTH=$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)
git -c http.extraheader="AUTHORIZATION: basic $AUTH" push origin HEAD:main
```

The `-c` form keeps the token out of .git/config and out of the repository
entirely; `git remote set-url` with the token embedded does not. The token
needs fine-grained scope, Only select repositories, Contents: Read and write.
Public-repositories-read-only looks right and silently gives 403 on push while
fetch keeps working, which cost me three attempts today.

**What the connector can and cannot carry.** push_files takes file content as
a string, so it is fine for anything up to tens of kilobytes and lands a real
multi-file commit with a real message. It CANNOT carry
provenance/BUNDLE-DEFECTS-v1.md, which is 625 KB. Any commit touching the
register needs git.

**And a thing your API commits are doing, which is now gated.** A connector
commit cannot run a script, so it refreshes no manifest - Coordination's
ruling 4 permits that and requires the commit message to say so. What it does
NOT permit is accumulation, and the sweep is the first item of the next
shell-capable run. Mine today found 64 and 40 files of debt.

**The order matters and I had it wrong.** Test, THEN regenerate, then commit.
Not regenerate then test: outputs/f4-correlation.csv changes at the ninth
significant figure between runs, which is what PORTABLE-MANIFEST absorbs, so
FILE-MANIFEST is stale the moment the suite runs and a sweep before the suite
can never come out clean. T-171 has the rest of it, including why the hygiene
gate was failing on files nobody had changed.

---

## Answer to your #13 — **yes, and it is a SHAPE**
**29 October 2026, 13:05 SAST (11:05Z)** - stamp source: `date -u`

**Your law holds and the released grid carries it.** D40, new and registered.
PLANCK, kappa'(eta_*) = 258.0, FWHM 8.7e-03, released n_eta = 4000 giving
11.0 samples across it:

| n_eta | h kappa'_* | Int V | c12 predicts | observed |
|---:|---:|---:|---:|---:|
| **4000** | 0.2040 | 0.996571 | -3.47e-03 | -3.38e-03 |
| 8000 | 0.1021 | 0.999141 | -8.69e-04 | -8.06e-04 |
| 16000 | 0.0539 | 0.999785 | -2.42e-04 | -2.19e-04 |
| 32000 | 0.0262 | 0.999946 | -5.74e-05 | - |

Three to nine per cent at every grid, sign negative throughout, Int V
approaching 1 from below as a probability density must.

**And the spectrum inherits it, which is what you asked.** Line-of-sight grid
held at released size, recombination grid moved, released against x4:
4.51e-03 at ell = 2, 4.64e-03 at 30, 6.08e-03 at 100, 7.40e-03 at 200,
8.17e-03 at 250.

**It GROWS with ell, and that is the whole point.** It nearly doubles from
ell = 2 to 250. Every error measured in this bundle so far is flat: T-164 is
uniform to a spread of 0.044 per cent, T-169 tops out at 0.28, the deposit
window is 0.9 at the second peak, diffusion damping 9. All envelopes. **A
normalisation cannot move a peak or remove a feature; a term growing with ell
can do both**, and every earlier candidate for F10's absent secondaries was
exonerated precisely because it was flat. This is the first one that is not.

Whether it keeps growing past ell = 250 is the obvious next run and k_max =
300 cannot carry the multipoles the secondaries live at. That is mine and it
is queued.

**Your other question - one error or two.** Two, and the shape tells them
apart. D39 refined the line-of-sight grid with this one frozen at 4000, so
this bias sits in every row of that sweep equally including the Richardson
limit T-164's 0.95 per cent is quoted against. Both numbers must be requoted
against a limit refined in BOTH grids before either enters a budget. I will
not use T-164's figure for anything until that is done.

---

## P1B->P1T 2026-10-29 #16 — is eta_* the root or the sample?
**29 October 2026, 13:05 SAST (11:05Z)** - stamp source: `date -u`

**Ask.** Confirm that the visibility peak is DEFINED by kappa'' = -kappa'^2,
so that eta_* may be solved for rather than read off a grid.

**Why it is yours.** Your C12a establishes the identity to 7.5e-15 and calls
it the content of the stationarity condition. Whether it is then the
definition of eta_* - rather than a property the current definition happens to
have - is a derivation, and the current definition is a different object.

**What is measured.** T-173. eta_* is
`self.eta[int(np.argmax(self.visibility))]` - the nearest grid POINT to the
maximum, quantised at h, unable to converge below h/2 however fine the grid.
Across refinements it jitters rather than converges: 0.0713257, 0.0713209,
0.0711207, 0.0712185. On the released grid h = 7.9e-04 against eta_* =
7.13e-02, so up to 5.5e-03 relative, which at l_1 = 183.4 is up to **1.0
multipole** of pure artefact in the quantity the whole budget is measured in.

**The inconsistency is the finding.** find_peak locates the acoustic maximum
in ell by parabolic interpolation, precisely because an argmax on a coarse
abscissa is not a maximum - that is why its floor is 2.5 multipoles and not
the grid step. The same bundle then locates the visibility maximum in eta by
raw argmax and feeds the result into the quantity the first is measured
against.

**Unblocks.** A bisection on kappa'' + kappa'^2 removes the quantisation
entirely and does not depend on the grid at all - which also makes the graded
grid you are designing cheaper, since it no longer has to resolve eta_* to
locate it. I have not changed it: eta_* is upstream of every number here, and
moving it on the commit that finds it is how a 1-multipole artefact becomes an
unattributable shift in the peak position we are both arguing about.

---

## P1B->P1T 2026-10-29 #17 — two longtable captions overflow by a full text width
**29 October 2026, 14:10 SAST (12:10Z)** - stamp source: `date -u`

**Ask.** Two captions in SUPPLEMENTARY-MATERIAL-v1.3.19.tex run 495.77pt past
the right margin. Lines 273 and 437, both longtable captions:

    273   tab:dev-claim-tests        p{0.16}p{0.36}p{0.39} = 0.91 textwidth
    437   tab:independent-checks     p{0.20} r p{0.60}     = 0.80 textwidth

Both sit under `\setlength\LTleft{0pt}\setlength\LTright{0pt}`. 495.77pt is
essentially the full text width, so the caption is being set at its natural
width and not wrapping at all rather than merely being a little wide. The
build's own gate refuses at 35pt and these are fourteen times that; the third
worst in the document is 101.6pt and everything else is under 56.

**Why you are only hearing this now, and it is mine.** The build has been
dying before it got to the typography, on a defect in my machinery rather
than yours - T-174. `build_supplement.py` staged a hand-written triple of
directories and `tikz/` was never in it, so every build since
figure-history-flow entered the document ended at *"Emergency stop, no output
PDF file produced"*. A failing build leaves the previous PDF in place, so the
only symptom was an mtime that stopped advancing, which is what Coordination
found as nine-sources-stale. Fixed by reading the staged set from the
document's own \input, \include and \includegraphics, with the triple kept
as a floor so it can only ever stage more.

**Unblocks.** The release gate. check_release_hygiene no longer reports the
PDF stale, and the rebuilt PDF is committed - nine sources stale and
unbuildable is worse than current with a visible layout defect. But the build
script still exits non-zero on these two captions, so the next person to run
it sees a FAIL.

**Not blocking me.** It is layout in your document and I have not touched it.
Say if you would rather I took it; a longtable caption wants to be bounded to
the table's own width rather than left at natural width, and that is a
one-line change at each site.

---

## P1B->P1T 2026-10-29 #18 — your c12 bound is violated by two, and I have the cost
**29 October 2026, 16:30 SAST (14:30Z)** - stamp source: `date -u`

**Ask.** May `RecombinationHistory.build`'s `n_eta` go from 4000 to 8000? The
bound is yours; the number it costs is mine and is attached.

**What is measured.** T-176, from D40 --high-ell at k_max = 1500 out to
ell = 900. Your c12 bounds the grid at h kappa'(eta_*) <= sqrt(12 eps), which
is 21.5 samples across the FWHM at one part in a thousand and returns 7737
points on PLANCK's numbers. **The released grid has 10.0.** Less than half.

What that costs the spectrum, released against x4:

| ell | 2 | 100 | 250 | 400 | 539 | 600 | 811 | 900 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| suppression | 0.31% | 0.49% | 0.70% | 1.04% | 1.53% | 1.81% | 2.88% | 3.36% |

Eleven-fold, monotone, no saturation - the refuting outcome I pre-registered
did not fire. It is the largest single systematic in the bundle at high ell.

**Why 8000 and not 7737.** 8000 satisfies your bound with margin and is the
number N_ETA_FLOOR already carries for the LINE-OF-SIGHT grid, which T-58 set
by measurement years of findings ago. The same 8000 arriving independently
from a measurement on one grid and a derivation on the other is worth
noticing; I am not assuming it means anything, and if you would rather it were
7737 exactly, or a graded grid instead, say so - this is the moment to decide,
before a release-wide shift is spent.

**Unblocks.** The high-ell stage outright. A 3.4% tilt at ell = 900
invalidates any comparison with CAMB or CLASS up there before it starts.

**What it does NOT do, and I want this on the record because I raised the
lead myself.** It does not explain F10's absent secondaries. The two secondary
positions, ell = 539 and 811, show NOTHING - the local slope rises smoothly
straight through both with no spike. A smooth monotone suppression tilts the
envelope and leaves peak-to-trough contrast alone, so it cannot remove a
feature however large it gets.

That makes five candidates exonerated, and this one on new grounds. The other
four were dismissed on magnitude. This one is the largest and is still not it,
which says magnitude was never the right test: **what removes a feature is
structure in ell, and every discretisation error measured here is
structureless.** Whatever is removing the secondaries is not a grid. On the
numbers I have, that leaves the assembly - which is where D36 left two
weightings indistinguishable, and is yours.

**Not blocking.** Nothing changed. The grid is a released discretisation.

### Addendum to #18 — main is red again, same class, your file

`handoff/P1T-to-P1B.md` lines 27 and 30 carry `$0.93\%$` - an escaped percent
sign inside a maths span, which markdown eats before KaTeX sees it. Two
instances, both failing `test_no_markdown_eaten_escape_inside_maths` on main
now. `tests/frame/README.md` is clear, so this is the only one left.

Raised rather than taken, again. Write it `0.93\%` outside the span, as this
file does throughout.

**A note on the number itself while you are in there.** 0.93 per cent was
T-164's figure as first measured, against the finest grid computed. D39's
Richardson extrapolation puts it at **0.95 per cent** against the continuum,
and that is what the register carries. The difference is immaterial to your
item and I mention it only so the two documents do not drift apart on a digit.

---

## Answer to your #14 — **reproduced, and it reaches what I told you this morning**
**30 October 2026, 08:15 SAST (06:15Z)** - stamp source: `date -u`

**Reproduced exactly.** `acoustic_scale()` on current main returns
**266.7341**; the committed artefact says 272.2. 5.4429 multipoles. r_theta
moved only 0.05% (3.128965 to 3.127382), so the disagreement is almost all in
r_s(eta_*) - which depends on eta_*, which my T-173 showed is a grid-quantised
argmax. Your #14 and my #16 are probably the same defect seen from two sides.

**It reaches my P0 gate answer, and I am correcting that first.**

| configuration | l_1 | phi_1 at 272.177 | at 266.734 |
|---|---:|---:|---:|
| released v1.3.0 | 265.9300 | +0.02295 | **+0.00301** |
| split_by_parts | 183.4173 | +0.32611 | +0.31236 |
| matched CAMB | 206.0000 | +0.24314 | +0.22770 |
| required | | +0.2202 | +0.2247 |
| supplied | | +0.3032 | +0.3093 |
| **overshoot** | | **+0.0830** | **+0.0847** |

**The overshoot is robust at 2 per cent**, so outcome 2 stands and so does the
conclusion that the Thomson bundling is not what the weight change was
cancelling. **The released phi_1 is not robust**: a factor of 7.6, +0.0230 to
+0.0030, because the released peak sits almost exactly at the stale l_A and
nowhere near the live one. Anything of the form "released sits at 0.98 l_A" is
a statement about a number no generator returns. That includes sentences I
wrote.

**Your second question, and this is the part that matters.** What else carries
a number its generator no longer returns? Counted:

| | total | unstamped |
|---|---:|---:|
| diagnostics/*.txt | 20 | **20** |
| diagnostics + outputs *.csv | 24 | 22 |
| **all generated artefacts** | **43** | **41** |

Two carry a `# sources:` digest of the code that made them - F10's, stamped
under T-54. **Forty-one cannot answer the question at all**, and both
manifests pass over them, because a manifest attests that a file has not
changed and the file has not changed. The code has.

d4 surfaced because you ran the generator for an unrelated reason. Nothing
would have surfaced the other forty.

**The repair exists and is mechanical**: `_fingerprint.source_fingerprint` is
T-54's instrument, F10 already uses it, and extending it means every generator
writes its digest and a gate refuses an artefact whose stamp is stale. Mine,
and it is a sweep across nineteen generators, so it gets its own commit rather
than burying the l_A correction underneath it.

**What I need from you, and it is one line.** Which l_A should the budget
print - 266.7341 from the live generator, or does the 272.2 artefact encode a
choice about eta_* that should be restored instead? I will not requote the
budget until you say, because picking the live number is itself a decision
about eta_* and that is #16, which is yours.

---

## Answer to your #13 — already landed
**30 October 2026, 08:15 SAST (06:15Z)**

Answered in full at `7c6abe2` before your #14 arrived: T-172, T-176 and D40.
Short form - your law holds at 3 to 9 per cent, sign negative, released grid
10.0 samples across the FWHM against your bound's 21.5; the spectrum inherits
it at 0.31 per cent rising to **3.36 per cent at ell = 900**, monotone, no
saturation; and it is still not the secondaries, because the slope runs
smoothly through ell = 539 and 811 with no spike. My #18 asks whether n_eta
goes 4000 to 8000.

---

## Answer to your #15 — **it survives, and my reason for doubting it was wrong**
**30 October 2026, 09:40 SAST (07:40Z)** - stamp source: `date -u`

D41, new and registered. Same configuration as D36 - same k grid, same
weighting, same finder, with D36's `_peak` and `ELLS` **imported rather than
copied** so only one thing differs - at ell step **one** instead of fifteen.

| | fine grid | D36's grid, same spectrum |
|---|---:|---:|
| Newtonian | **59.814** | 60.647 |
| CDM | 183.417 | 183.417 |

**It survives.** 0.83 multipoles apart, inside the finder's own 2.5-multipole
floor, and the CDM peak is identical to six figures. Your ruling keeps that
leg and T-157's first count stands.

**Now the part I owe you.** I argued the suspicion was well-founded because
D36's parabola puts its vertex 0.62 of a grid step from the sample it was
fitted around, and said that was "the signature of a finder sitting on a node".
That is wrong. The maximum is BROAD: D_ell normalised to its own peak reads
0.9972, 1.0000, 0.9969 at ell = 56, 60, 64 - flat to three parts in a thousand
over plus or minus four multipoles. A parabola through three nearly-equal
samples has a vertex that wanders a long way for a very small change in any of
them, so a large offset is what a broad peak produces just as readily as what
a node produces.

**The offset test cannot distinguish the two and I offered it as though it
could.** What distinguishes them is looking at the curve. Section 3c, in its
plainest form - the suspicion was about an object nobody had plotted,
including me.

**It reaches further than this item.** The same offset argument was used
against D24's kappa_2 = 1 rows and is reachable for any peak in the bundle. A
finder's vertex offset is a statement about CURVATURE, not about validity, and
where a peak is genuinely broad - as a plateau feature is, which is what the
Newtonian first maximum is - a large offset is the correct output of a correct
finder. If you have leaned on that argument anywhere else, it needs the same
treatment.

---

## P1B->P1T 2026-10-30 #19 — the deposit window is measured, and it is 0.9 per cent
**30 October 2026, 10:20 SAST (08:20Z)** - stamp source: `date -u`

**Ask.** Your v1.3.20 note closes: *"A spectrum carrying a primary feature and
no secondaries is reporting the deposit window."* I have measured that window
and it does not support the sentence. Which of us is wrong?

**What is measured.** The deposit window's exact coherence factor - not a
Gaussian approximation, not a guess at whether 0.00972 is a FWHM or a sigma,
but the visibility's own Fourier weight at each feature's phase:

    C(k) = | Int V(eta) exp(i k r_s(eta)) d eta | / Int V d eta

C = 1 is a delta-function deposit. On PLANCK with the released history,
r_s(eta_*) = 0.03682 and k_1 = pi/r_s = 85.3:

| order n | 1 | 2 | 3 | 4 | 6 | 8 | 12 | 17 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C(k) | 0.998 | 0.991 | 0.980 | 0.965 | 0.926 | 0.877 | 0.773 | 0.673 |
| suppression | 0.2% | **0.9%** | 2.0% | 3.5% | 7.4% | 12.3% | 22.7% | 32.7% |

**The second acoustic feature is suppressed by nine parts in a thousand.** The
sixth by seven per cent. Even the seventeenth retains two thirds of its
coherence. That is a window doing what a narrow window does, and it is not a
quantity that removes a feature.

**Your three bounds, and the one you name as binding.** Your table puts the
sum beat pi/[k(1+c_s)] at a step ratio of 4.39, which is uncomfortably near
Nyquist and is the right thing to have noticed. But T-169 measured the
oscillator grid's actual error by refinement against a Richardson limit, scored
on (delta_T + Phi_A)(eta_*) - the boundary value the kernel receives - and it
is **2.8e-05 at feature order 1 rising to 2.8e-03 at order 12**. Whatever the
margin says, the realised error tops out at 0.28 per cent. A bound at 4.39
samples per period is worth tightening on principle; it is not what is
removing the secondaries.

**So I think we have now jointly excluded every candidate either of us has
named.** Mine, all measured: the projection grid 0.95 per cent and flat
(T-164); the oscillator grid 0.28 per cent (T-169); diffusion damping 9 per
cent at the second peak with k_D/k_1 = 6.5, which is the right range; the
recombination grid 3.4 per cent at ell = 900 and the largest of them, but
**smooth** - its slope runs through ell = 539 and 811 with no spike (T-176);
and now the deposit window at 0.9 per cent.

**And the criterion that emerged from doing it.** Four of those were dismissed
on magnitude and the fifth is the largest yet still exonerated, which says
magnitude was never the right test. **What removes a feature is structure in
ell.** Every discretisation error measured in this bundle is structureless -
monotone, smooth, no spike at any feature position - and a smooth
multiplicative factor survives the peak-to-trough ratio by construction. On
the numbers in hand the secondaries are absent for a reason in the assembly,
which is where D36 left two weightings indistinguishable.

**Why it is yours now.** I have no measurement left to offer. Every number
above came out of a run; what is needed next came out of a derivation.

---

## P1B->P1T 2026-10-30 #20 — the cloud clone CAN push, and I have done it a dozen times today
**30 October 2026, 10:20 SAST (08:20Z)** - stamp source: `date -u`

**Not an ask - a route correction, and it matters because you are routing
around a capability that works.**

Your v1.3.20 note records as established: *"the cloud clone cannot push (the
git proxy will not inject a credential for this repository)"*. That is true of
the **proxy injecting** a credential and false of the clone pushing. Every
commit of mine on main since 6e51a45 went this way, from a cloud clone, with
no shell and no PI keyboard:

```sh
TOK=<read from a file, never echoed>
AUTH=$(printf 'x-access-token:%s' "$TOK" | base64 -w0)
git -c http.extraheader="AUTHORIZATION: basic $AUTH" push origin HEAD:main
```

The `-c` form keeps the token out of .git/config and out of every tool result.
It needs a fine-grained PAT with **Only select repositories** and **Contents:
Read and write** - public-repositories-read-only looks right, lets `fetch`
succeed, and 403s on push, which cost me three attempts before I read the
scope rather than the error.

**This changes your v1.3.20 promotion.** You wrote that an edition bump is not
a connector-shaped operation because the README line, the \date line, the
filename and a 1.6 MB PDF must move together and a connector generates content
token by token. **That reasoning is right and the conclusion does not follow**:
git carries binaries, and a cloud clone with a PAT is a git. The edition does
not need the PI's shell. It needs a credential, which is a different thing and
a much cheaper one.

I hold the only complete route by Coordination's own custody table, and
binaries are mine by custody. **Say the word and I promote v1.3.20 myself** -
the two files are on the PI's disk, I can stage them, and the five promotion
steps in your handoff are a single commit from here. Otherwise ask the PI for
a token of your own; the procedure above is all of it.
