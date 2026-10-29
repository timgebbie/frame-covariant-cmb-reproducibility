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

**Not blocking you.** The released path is untouched. T-167 is the repair that
lets the batch reproduce it exactly - each mode held at its own initial
condition until its own start, imposed on a common grid by zeroing its
derivative. Measured at 2.5e-08 against the released solve at identical times,
with a 7.1x speedup flat from 64 to 256 modes. It changes no number; it makes
the per-mode start explicit rather than implicit in a grid.

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

    AUTH=$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)
    git -c http.extraheader="AUTHORIZATION: basic $AUTH" push origin HEAD:main

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
