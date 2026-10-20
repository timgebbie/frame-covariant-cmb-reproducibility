# Defects in this bundle's own machinery

**Append-only. Entries are numbered `T-n` and are never rewritten.**

This record is separate from
`ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` on purpose. That file is the
audit of *Annals II*; a reader checking whether the paper's (181) carries the
right sign should not have to wade through our own tooling bugs to find out.
Findings against the **antecedent** are `B-n`; deliberate **approximations** are
`A-n` in `SOURCE-APPROXIMATIONS-v1.md`; **lineage** notes are `L-n`; defects in
**this bundle's infrastructure** are `T-n`, here.

A defect is recorded here when it affects something a reader relies on — a
released artefact, a gate, a published number — even when no physics is wrong.
Tooling that quietly certifies the wrong thing is worth more scrutiny than
tooling that fails loudly, not less.

---

## T-1 — the release fingerprint was a property of the folder, not of the repository

**Raised 2026-10-07. Severity: material, and load-bearing for the release
mechanism.** Corrected the same day; this entry is the log, and the raise went
to the PI in the same message.

### How it surfaced

`v1.0.0-rc` was pushed and the PI ran the portability gate on their own machine
as the acceptance step. It printed **95 files**. The same gate in the
development container printed **93**, and `FILE-MANIFEST-SHA256.txt` carried
**97** entries. Three numbers, one commit.

The prediction in the hand-off had been 93, so the gap was two files and could
have been written off as a counting convention. It was not a counting
convention.

### The defect

`scripts/make_manifests.py` and `scripts/check_portability.py` each walked the
working directory with **its own** hard-coded skip list, and **neither honoured
`.gitignore`**. Anything lying in the directory was therefore part of the
bundle:

* a local `pdflatex` run leaves `SUPPLEMENTARY-MATERIAL-v1.0.0.aux`, `.log` and
  `.out` beside the source;
* Windows Explorer writes `Thumbs.db` into any folder of images — `figures/`
  qualifies — merely because someone *looked* at it;
* macOS Finder writes `.DS_Store` on the same terms.

`.gitignore` already named the LaTeX products, so git was right and the gates
were wrong. The OS metadata files were named nowhere, so both were wrong.

**Why this is load-bearing rather than cosmetic.**
`FILE-MANIFEST-SHA256.txt` is the release fingerprint: it is what a reader
checks a download against. A fingerprint that absorbs whatever is in the folder
fingerprints *a folder*, not *a release*. Two consequences, both bad:

1. `make_manifests.py --check` fails on a correct checkout, for reasons having
   nothing to do with the bundle — and a gate that cries wolf gets ignored,
   which is how a real drift gets through.
2. Worse in the other direction: regenerating the manifest on a machine with
   build products **writes those products into the fingerprint**, so the
   released fingerprint then names files that are not in the release and cannot
   be reproduced by anyone.

Neither had happened. The second was one `python scripts/make_manifests.py`
away on a machine that had run `pdflatex`, which is exactly the machine that
builds the supplement.

### The correction

**Structural, not another skip list.** Two gates with two rules drift; the fix
is that there is now one rule and both import it.

* **`scripts/_bundle_files.py`** (new) is the single selector. It honours
  `.gitignore` — including `!` negation, which is what keeps the blanket
  `*.pdf` rule (there to stop publisher PDFs entering the repository) from
  swallowing the three released PDFs rescued by `!figures/*.pdf` and
  `!supplementary-materials/*.pdf`.
* It does **not** shell out to `git ls-files`. A reader reproducing F1 from a
  downloaded zip has no `.git` directory, and the gates must give them the same
  answer they give the repository. The matcher implements the subset of
  `.gitignore` syntax this bundle uses and **raises** on anything outside it
  (`**`), rather than silently disagreeing with git.
* `.gitignore` gained the OS-metadata patterns it was missing, so git and the
  gates agree about `Thumbs.db` and `.DS_Store` too.
* `check_portability.py` now prints all three reconciling numbers — bundle
  files, content-checked, manifest entries expected — and **lists** any ignored
  files present in the working tree as a note. That note is never a failure:
  a local build leaving `.aux` files is normal. It is there so the next person
  who sees two machines disagree gets the answer on the spot instead of over a
  round trip, which is what this one cost.

One rule was also sharpened rather than suppressed. The gate required every
file under `scripts/` to anchor its paths to `__file__`; the new selector takes
its root as an argument, as a library should, and tripped it. Demanding
`__file__` of a library would push a hardcoded root *into* the shared code —
the opposite of the rule's purpose — so the rule now applies to **entry
points**, detected by the `__main__` guard. That is the real test for "this
gets run, so it has to know where it is."

### What holds it closed

`tests/test_bundle_file_selection.py`. It asserts that both gates select through
the *same function object* (checking that they merely agree today would pass
right up until someone edited one list); that planting `.aux`, `.log`, `.out`,
`Thumbs.db` and `.DS_Store` into a tree changes the selected set not at all;
that negation is order-sensitive the way git's is; and that the three released
PDFs are still in the fingerprint — a matcher that got negation backwards would
have dropped the v1.0.0 deliverable out of the manifest without a word.

### Status

**Closed.** The counts now reconcile on any machine: `bundle files = manifest
entries + 2`, the two being the manifests, which cannot contain their own
hashes. What the PI's machine was carrying is no longer diagnosed, because it
can no longer matter — but the note in the gate's output will name it.

### The general lesson, recorded because it will recur

The gates were written in the container that produced the code and were
therefore only ever run against a tree that container had made. That is
precisely the failure mode Coordination's standing gate of 2026-10-06 names:
*nothing ships from this bundle that has only ever run where it was written.*
The gate caught two scripts with hardcoded paths. It did not catch itself, and
the first run on another machine found it within a minute. **The acceptance
step worked.** The lesson is not to trust it less but to keep doing it first.

---

## T-2 — every released PDF carried a wall-clock stamp, so the fingerprint could never verify a re-run

**Raised 2026-10-07, in the first `run_all.py --strict` after T-1 was fixed.
Severity: material, and load-bearing for the same mechanism T-1 was.**
Corrected the same day.

### How it surfaced

With the file set finally stable, `--strict` still refused to pass:

```text
FAIL  FILE-MANIFEST-SHA256.txt does not match the tree
        changed  figures/f1-appendix-f-v1.0.0.pdf
        changed  figures/f3-angular-spectrum-v1.0.0.pdf
```

Nothing scientific had changed. The two PNGs, regenerated in the same run from
the same arrays, were byte-identical; only the PDFs moved.

### The defect

Matplotlib writes the wall clock into every PDF it produces:

```text
CreationDate = D:20261007144937+02'00'
```

So the PDF hash changed on **every** run, and `--strict` — the release route,
whose entire job is to regenerate everything and fail on drift — could never
pass on a machine that had regenerated the figures. Two bad outcomes, both
reachable:

1. The gate fails for a reason that has nothing to do with the bundle, every
   time. A gate that always fails gets routed around, and then a real drift
   goes through with it.
2. The reader this fingerprint exists for is someone who downloads the bundle,
   re-runs the pipeline and checks they got the same thing. For the figures,
   **they never could** — not because the figures differ, but because the clock
   does.

T-1 made the fingerprint independent of what was lying in the folder. T-2 is the
other half: making it independent of *when* it was computed.

### The correction

`functions/plotting/style.save_figure` now writes deterministic metadata —
`CreationDate: None`, and `Creator` pinned to the repository name — and
`scripts/diagnostic_d1_sign_control.py`, which writes its own PNG rather than
going through `save_figure`, does the same. Two runs seconds apart now produce
byte-identical files.

**What is deliberately not claimed** is byte-identity across matplotlib
versions. A different renderer genuinely lays the page out differently, and
stripping the version string would hide a real difference rather than remove a
spurious one. The timestamp is noise; the renderer version is information.

### Status

**Closed.** `python scripts/run_all.py --strict` reports `CLEAN`, and a repeated
run leaves every hash alone.

### Why both halves were found on the same day

T-1 surfaced because the release route was run on a second machine for the first
time. T-2 surfaced because, with T-1 fixed, `--strict` could get far enough to
reach the figures — it had been failing earlier, on the file set, and the figure
drift was hiding behind it. **One gate failing masks the next one.** That is
worth remembering the next time a gate is left amber: the cost is not the one
failure, it is everything downstream of it that nobody has seen fail yet.

---

## T-3 — the line-of-sight $\eta$ grid aliased $j_\ell$, and the key figure of `v1.0.0-rc` is wrong

**Raised 2026-10-08. Severity: load-bearing, and release-blocking for
`v1.0.0-rc`.** This one is not infrastructure. It is a numerical defect in the
physics pipeline, it changes every number in the released angular spectrum, and
the tag must be superseded rather than amended.

### How it surfaced

The PI asked why the $\Lambda$CDM peak-to-plateau ratio read $\sim36$ when it
should be nearer 6, noting that standard CDM's 5.8 looked about right.

**Both numbers were wrong.** The one that looked wrong was the one that found
the bug; the one that looked right was equally aliased and happened to land on a
plausible value. That is the part worth remembering: a number passing the
eyeball test is not evidence, and here the eyeball test actively protected the
defect in one model while exposing it in the other.

### The defect

The line-of-sight integral of (176) carries $j_\ell(k(\eta_0-\eta))$, which
oscillates with **period $\pi/k$ in $\eta$**. `scripts/figure_f3_angular_spectrum.py`
passed a fixed `n_eta=1000`. The period shrinks as $1/k$ while the grid does
not, so above some $k$ the integrand is **aliased**:

| model | $\eta$ span | samples per oscillation at $k_{\max}=420$ |
|---|---|---|
| standard CDM | 2.000 | 3.7 |
| $\Lambda$CDM | 3.305 | **2.3** |

Nyquist is 2. $\Lambda$CDM was being integrated at the sampling limit.

**An aliased integrand does not announce itself.** It does not oscillate, blow
up or return NaN. It returns a smooth, plausible, monotonic spectrum of entirely
the wrong shape — which is how this survived into a tagged release candidate as
the designated key figure.

Measured at $k_{\max}=420$ against `n_eta=8000`, $D_\ell$:

| $\ell$ | CDM, n=1000 | n=8000 | error | ΛCDM, n=1000 | n=8000 | error |
|---|---|---|---|---|---|---|
| 2 | 9.72 | 8.15 | 19% | 10.89 | 9.27 | 18% |
| 20 | 9.61 | 14.69 | 35% | 26.42 | 9.24 | 186% |
| 100 | 31.0 | 152.7 | 80% | 198.9 | 31.8 | 525% |
| 200 | 56.0 | 363 | 85% | 394.2 | 58.4 | **575%** |
| 400 | 32.5 | 533 | 94% | 281 | 64.8 | 334% |

and the ratio the PI queried:

| $D_\ell^{\max}/D_2$ | n=1000 | n=2000 | n=4000 | n=8000 |
|---|---|---|---|---|
| standard CDM | 5.76 | 59.8 | 59.9 | 65.4 |
| $\Lambda$CDM | **37.3** | 12.0 | 7.13 | **6.99** |

**The PI's reading was right to three significant figures.** $\Lambda$CDM
converges to 6.99, "nearer 6". CDM converges to $\sim60$, not 5.8 — its rise is
real, because this almost-FLRW formulation carries no matter transfer function
and the Doppler source of (178) carries an explicit factor of $k$, so power
keeps growing until Silk damping bites at $\ell\sim2400$. $\Lambda$CDM's
larger $\chi_*$ maps a given $\ell$ to a smaller $k$, which is exactly why its
ratio is the smaller of the two. The two converged numbers make physical sense;
the two shipped numbers did not, and one of them hid it.

### The argument was already written down in this bundle

F3's own k-grid comment reads:

> The k-grid is LINEAR with dk = pi/6 ... a logarithmic grid aliases the
> integrand at high k however many points it has.

The sampling argument was understood, stated, and applied to one axis of a
two-dimensional integral. **Nothing carried it to the other.** The fix is not
new physics or new insight; it is the application of a rule this project had
already written for itself.

### The correction

`n_eta` is now **derived**, not chosen. `functions/spectra/pipeline.required_n_eta`
returns $\lceil 12\,k_{\max}(\eta_0-\eta_{\min})/\pi\rceil$ — twelve samples per
oscillation at the band edge, matching `BesselTable`'s sampling of the same
oscillation in $x$, because two grids resolving one function have no business
disagreeing about how finely. `run(..., n_eta=None)` is the default and derives
it; an explicit value below the requirement **raises**, and the message names
the number that would work, because an error that does not say what to do
instead gets worked around.

For F3's grid that is `n_eta >= 3209` (CDM) and `>= 5302` (ΛCDM), against the
1000 that shipped.

### The second half, reported rather than fixed

The $k$ grid is **also** short, and this is now reported on every run as
`damping_at_k_max`. The diffusion cut-off sits at $k_D=1240$ (CDM) and $850$
(ΛCDM); the grid stops at $k_{\max}=420$, where $\exp[-(k/k_D)^2]$ is still
**0.89** and **0.78**. The integral is therefore truncated, not converged — the
grid ends while the source is still contributing nearly its full weight.
Measured at fixed `n_eta`, truncating at 420 rather than 1680 costs 0.1% at
$\ell=2$, 5% at $\ell=50$, 11% at $\ell=200$ and **24%** at $\ell=400$.

This is **not** patched, and the reason is honest: reaching the cut-off needs
$k_{\max}\gtrsim2.5k_D\approx3100$, and the derived $\eta$ grid then needs
$n_\eta\approx39{,}000$ — a $6000\times39{,}000$ evaluation this architecture
cannot do in reasonable time. That is an architecture problem, not a parameter
problem, and it is the real content of the v1.2.0 line-of-sight work: the
standard remedy, which CMBFAST uses, is a sparse $k$ grid with interpolation in
$\ell$ and the $j_\ell$ oscillation handled analytically rather than sampled.
Recorded here so v1.2.0 meets it as a known design requirement instead of
rediscovering it.

### Consequences for the release

1. **F3 as published in `v1.0.0-rc` is wrong and must be regenerated.** Every
   $D_\ell$ in `outputs/f3-angular-spectrum.csv` moves.
2. **The two-route agreement of $4\times10^{-16}$ is unaffected and remains
   valid.** Both routes integrated the same aliased integrand, so the lower
   panel measured what it claims to measure — the arithmetic of (186) against
   (187)+(188) — and measured it correctly. It could not have caught this, and
   the caption already says it checks the arithmetic and not the physics. That
   statement was right, and this is the case that proves why the distinction was
   worth making.
3. **Criterion 1 and Figure 1 are unaffected.** The Appendix F chain is a
   recursion check with no line-of-sight integral in it.
4. **Acceptance criterion 5a is unaffected in target but must be re-measured.**
5. **The Paper 1 emissions must be re-run.** `scripts/emit_paper1_floats.py`
   builds its ray on the same grid; `fig:bulk`'s field and its bulk fraction of
   0.1196 are computed from an aliased integrand and are not to be drawn from
   until re-run. `fig:efficiency` is unaffected — $\chi(\eta)$ and the kernel
   are background quantities with no line-of-sight integral.

### Status

**Correction landed; re-measurement outstanding.** The guard is in place and
`tests/test_line_of_sight_sampling.py` holds it. The regenerated spectrum, the
honest converged $\ell$ range, and the re-run emissions are the next work, and
`v1.0.0-rc` should be superseded rather than released.

### The general lesson

T-1 and T-2 were caught by running the release route on a second machine. T-3
was caught by **a physicist looking at a number and saying it was the wrong
size**. No gate in this bundle would have found it: every test passed, both
routes agreed to $10^{-16}$, the manifests were clean and the portability gate
was green. A convergence study is not a gate anyone had written, because
convergence had been treated as a property of the method rather than of the
grid. It is now a property of the grid, checked.

### T-3, update 2026-10-08: regenerated, and one of my own claims withdrawn

**F3 is regenerated on the derived grid** — `n_eta=3150` for CDM and `5196` for
ΛCDM, both at exactly 12.0 samples per oscillation at the band edge — and
`run_all.py --strict` now passes its manifest check, so the figures are
byte-reproducible at the corrected resolution.

| | shipped (`n_eta=1000`) | corrected | converged reference |
|---|---|---|---|
| CDM $D_\ell^{\max}/D_2$ | 5.76 | **60.9** | $\sim$60–65 |
| ΛCDM $D_\ell^{\max}/D_2$ | 37.3 | **7.15** | 6.99 |

The two-route agreement is unchanged in kind and in size: $6.21\times10^{-16}$
(CDM) and $5.46\times10^{-16}$ (ΛCDM).

**Withdrawn: consequence 5 above, that the Paper 1 emissions must be re-run.**
That was wrong and is corrected here rather than edited away. The `fig:bulk` ray
sits at $k=60$, not at the spectrum's band edge of $k=420$, and the same 1500
$\eta$ samples give it **24.3 per oscillation** against the 12 required. It was
never aliased. Re-running it reproduces every figure exactly — endpoint
$-1.950790$, bulk fraction $0.11964$, kernel endpoints $1.000000$ and
$0.000000$ — which is the check, not the assumption.

The emission was nonetheless *lucky* rather than *designed*: nothing had
verified its sampling. `scripts/emit_paper1_floats.py` now computes the
requirement, raises if the ray is under-sampled, and records the achieved
samples-per-oscillation in `outputs/paper1-emissions-params.txt`. An accident
that holds is still an accident until something checks it.

**The lesson on the withdrawal.** On finding T-3 I generalised from the
spectrum to everything built on an $\eta$ grid, and told the PI to stop P1-T
drawing `fig:bulk`. The aliasing criterion depends on $k$, and the ray's $k$ is
seven times smaller than the spectrum's band edge — which the criterion would
have said in one line had I applied it instead of extrapolating from it. A
correct rule, applied, beats the same rule used as an intuition.

---

### T-1, update 2026-10-08: which machine generates the fingerprint

T-1 made the fingerprint independent of what is lying in a folder. A second
question surfaced when the corrected tree was transferred to the PI's machine
and `make_manifests.py --check` was run there: **two working copies existed,
and they held different files.**

| file | development container | PI's machine |
|---|---|---|
| `tests/__init__.py` | absent | present, since the bundle began |
| `source/.gitkeep` | absent | present |
| `supplementary-materials/stream-P1T-to-supplement-2026-10-07.tex` | absent | present — P1-T's handover, added that morning |

None of this is drift in the T-1 sense; the gate was working exactly as built
and said so precisely, including the release-blocking flag on `source/`, which
is correct behaviour for a new file appearing under frozen material even when
the file is innocuous.

**The rule this settles: the manifest is generated on the machine that
publishes.** A fingerprint written in a working copy and carried to the
publishing tree describes the wrong tree, and whichever copy is behind wins by
accident. The publishing tree is authoritative for *which files exist*; a
working copy is authoritative only for *the content it changed*. So the
sequence after any transfer is: reconcile the file set, then regenerate the
manifests **there**, then commit.

**A transport limitation, recorded because it will recur.** The same transfer
moved 31 files. Every text file and both PDFs arrived byte-exact — the manifest
check named only three differences, all of them PNGs. The bridge re-encodes
PNG images. Nothing is wrong with the images, but their hashes move, so **PNG
figures cannot be shipped across it**: they are regenerated on the target
machine instead, which `run_all.py --rerun` does, and which is what the rule
above says to do anyway.

---

## T-4 — the release harness tested the previous run's artefacts

**Raised 2026-10-08, on the first `run_all.py --rerun` after the file set
changed. Severity: material. A false failure, not a missed one.** Corrected the
same day.

`run_all.py` ran the regression suite **first**, before regenerating figures,
tables, outputs and manifests. So on `--rerun` — the route whose whole purpose
is to rewrite those artefacts — the suite tested the artefacts from the
*previous* run.

It surfaced the moment it could do damage. With three files reconciled into the
tree, `--rerun` reported:

```text
FAILED tests/test_bundle_file_selection.py::test_the_manifest_covers_every_bundle_file_but_itself
  assert 106 == (101 + 2)
...
--- manifest rewrite ---
wrote FILE-MANIFEST-SHA256.txt      104 files
============================================================
NOT CLEAN — tests
```

**The run announced a failure and then, eleven lines later, fixed the thing it
had failed on.** The tree was correct when the run ended; the verdict said
otherwise. Nothing was wrong with the test — it asserts a real invariant, and
it was the test that caught the file-set divergence in the first place. What was
wrong was asking it a question before the answer had been written.

T-1's entry says it in as many words: *a gate that cries wolf gets ignored,
which is how a real drift gets through.* This is that failure mode arriving
from the other direction — not a gate that passes when it should fail, but one
that fails when it should pass, which erodes the same trust and does it faster,
because a false alarm is visible and a false pass is not.

### The correction

The suite now runs **last**, after every artefact it could be testing has been
regenerated, in both modes. The cost is losing fail-fast — a broken tree is
found after the figures are drawn rather than before — and that is the right
trade: a correct verdict late beats a wrong verdict early. `--strict` is
unaffected in substance, since nothing should change there anyway.

### Status

**Closed.** Ordering is a property of the harness, now stated in the code where
it is enforced rather than left to the order the steps happened to be written
in.

---

## T-5 — a quantity named for the conclusion it was expected to support

**Raised 2026-10-08 by the PI. Severity: material.** No number changed; the
name did, and the name was doing argumentative work.

### Origin, which is upstream of this bundle

Paper 1's caption for `fig:bulk` read:

> The bulk contribution cancels; what survives is the lever-arm endpoint, and
> that endpoint is the lensing.

**That is backwards**, and the PI established it from the section rather than
from the caption: $\Delta e_\perp(0)=0$ kills the *lower boundary* term, so what
survives is the **bulk integral**, which on exchanging the double integral is
$-\int(\chi_*-\chi)\nabla_\perp\Phi_A\,\dd\chi$ — the deflection with the
lensing efficiency inside it. The endpoint vanishes; the bulk is the signal.

P1-T's float specification of 2026-10-06 was written from that caption, so the
inverted statement reached this stream as a work order and had been live for two
days.

### What it did here

The emission dutifully produced a statistic whose **name** asserted the
inverted claim: `bulk_fraction`, read naturally as *the fraction of the signal
contributed by the bulk*, reported as `0.1196`. A reader comparing that against
"the bulk cancels" would conclude the cancellation was failing at the 12% level.

Both readings are wrong, and the code was never computing either:

```python
interior = slice(len(running) // 10, -len(running) // 10)
max(abs(running[interior] - endpoint)) / abs(endpoint)
```

That is the **largest excursion of the running line-of-sight integral away from
its final value, through the middle 80% of the ray, relative to that final
value**. A flatness measure. It cannot be a bulk-over-total ratio, because the
running integral *is* the total — such a ratio built from it is identically
zero, which is why the "~0.95 if something is off" the question anticipated was
never reachable.

**And 12% is a real, sensible number read correctly.** The ray's integral
arrives within 12% of its endpoint by $\chi=3.195$ — 1.3% of the way from last
scattering — then drifts within that band and settles to 5% only over the final
11% of the ray. That is the signature of a source dominated by the
last-scattering spike with a late integrated Sachs–Wolfe contribution spread
along the line of sight, at the ~12% level, for $\Lambda$CDM at $\ell=20$. It
is a property of (176)'s integrand and says nothing whatever about the
$O(\varepsilon^2\ell)$ aberration operator of Eq. (28), which does not exist
until v1.5.0 and is what the bulk-versus-endpoint question is actually about.

### The correction

`RayEmission.bulk_fraction` is now `RayEmission.running_excursion`, documented
by its formula. The computation is byte-identical; the CSV header and the
parameter file carry the new name and a statement of what it does and does not
speak to.

### The lesson, which is the reason this has an entry at all

**A number named after the conclusion it is expected to support will be read as
evidence for that conclusion, whatever it computes.** The inversion originated
in a caption, travelled through a specification into a property name, and from
there into a CSV header that P1-T would have plotted. Nothing checked it,
because every step was faithful to the step above it. The defence is the one
this project already applies to equation numbers: name the thing by what it
*is*, resolve claims against the derivation, and let the agreement be an
observation rather than a label.

**One consequence is worth more than the correction.** Under the corrected
statement, the surviving bulk term carries the factor $(\chi_*-\chi)$ — which
is exactly the lensing efficiency `fig:efficiency` already shows emerging from
the lever arm. The two figures stop being independent checks and become the two
halves of one argument, and the bundle already emits the kernel both need.

### Status

**Closed here; the caption and the specification are the PI's and P1-T's to
correct.** Recorded in this bundle because the inverted claim reached the code
and was shipped in an output header.

---

## T-6 — the fingerprinted tree and the published tree were not the same tree

**Raised 2026-10-08, from a `git ls-tree -r --name-only HEAD` listing the PI
pasted. Severity: release-blocking.** Corrected the same day.

### How it surfaced, and why nothing had caught it

The gates answer *what is in this folder*. Git answers *what a clean checkout
will contain*. **The release fingerprint is only meaningful for the second** — a
reader verifies a clone, not somebody's working directory — and the two had
drifted apart in both directions at once:

| | |
|---|---|
| `data/.gitkeep` | tracked by git, **deleted from the working tree** |
| `supplementary-materials/stream-P1T-to-supplement-2026-10-07.tex` | in the working tree, **untracked** |

**One file each way, so the counts came out equal: 106 against 106.** The
portability gate prints a count. `test_the_manifest_covers_every_bundle_file_but_itself`
asserts arithmetic on counts. Nothing compared the sets, so both passed on a
tree where a clean clone would have failed `make_manifests.py --check` — and *a
clean checkout is this project's stated acceptance*. The failure would have
appeared at the worst moment, on someone else's machine, with the fingerprint
apparently sound everywhere it had been checked.

This completes a family. **T-1** was the fingerprint absorbing junk that was in
the folder. **T-6** is the fingerprint missing files that were not. Both reduce
to the same mistake: treating the working directory as the thing being
released.

### The correction

`check_portability.check_against_git()` compares `git ls-files` against
`bundle_files()` and **fails on any difference in either direction**, naming the
file and saying which way it is wrong. It returns a note and no failure when
`.git` or `git` is unavailable, which is the normal case for a reader who
downloaded a zip and for any non-publishing environment: absence of git is not
evidence of anything, and a gate that fails on it would be the T-4 mistake
again.

The untracked case fails too, deliberately. A file inside the fingerprint that
a clone will not have is as wrong as the reverse, and failing forces the
question — *where does this file belong?* — instead of letting the mismatch sit.

### What the two files themselves need

`data/.gitkeep` is redundant beside `data/README.md`, exactly as `source/.gitkeep`
is redundant beside `source/README.md`; neither directory needs a keeper. It is
removed from tracking rather than restored to disk.

The P1-T handover is **input**, not a supplementary material, and ships looking
like part of the supplement where it sits. `source/source-v2/` is defined as
"computational conformity and clarification inserts", which is what it is.

### The general lesson

**Equal counts are not an equal set, and every gate here was counting.** The
cheapest check that would have caught this — comparing two sorted lists — was
not written because the quantity being watched had been chosen for how easy it
was to print. When a gate reports a number, ask what it would fail to notice.

### T-6, note 2026-10-08: the first live run, and a transport limitation

The git comparison fired correctly on its first real use and named five
untracked files. Four were not a defect in the tree but an artefact of how the
correction reached it: **the device bridge writes files and cannot delete
them.** A rename performed in the development container therefore arrives on
the publishing machine as an *addition*, leaving the old name in place, and
`git rm --cached` clears the index without touching the working tree. So
`outputs/paper1-fig-bulk.csv`, `outputs/paper1-fig-efficiency.csv`,
`outputs/paper1-emissions-params.txt` and `scripts/emit_paper1_floats.py`
survived their own rename.

This is the second transport limitation worth recording beside the PNG
re-encoding: **renames and deletions do not cross the bridge, only content
does.** Any rename is therefore two operations — write the new name across,
then delete the old name on the publishing machine — and the second one has to
be asked for explicitly. The gate catching it on the first run is the system
working; it would otherwise have shipped four duplicate files inside the
fingerprint.

The fifth file, P1-T's supplement handover, is a real open question and the
gate is right to keep failing on it. It is draft material *for* the supplement,
not a supplementary material and not frozen reference, so neither tracking it
where it sits nor freezing it under `source/` is correct. It is folded into
`SUPPLEMENTARY-MATERIAL-v1.0.0.tex` and removed; until then the tree is
honestly not releasable, which is what the red gate says.

### T-6, closed 2026-10-08: the handover is folded and the gate is clean

P1-T's handover is incorporated and the file removed. It was **not** pasted:
most of its App. C material was already in the supplement, so the fold is four
surgical edits plus one new paragraph, and it corrected the supplement where it
had fallen behind the resolved Wilson question.

| was | now |
|---|---|
| "Four external treatments are used" | **five read, four drawn** --- Wilson \& Silk (1981) Eq.~(7) credited, and not drawn because at $K=0$ it *is* Wilson (1983) Eq.~(8) |
| "Two misprints in one citation" | **one mismatched pairing.** Both papers are real and both numbers are right for the paper they belong to; *Annals II* pairs the 1981 name with the 1983 key and a number correct for 1981 |
| "the four-source match" | the five-source match, with the added finding that **both** Wilson papers are in the imaginary convention --- so no author published in both, and the hypothesis that one had is dead |
| (absent) | Hu \& Sugiyama Eq.~(2) cited as where the $\beta$ normalisation is fixed |

**The translations table was deliberately not pasted.** The handover carries it
as a `\PH{}` placeholder gated on the conventions gate, and an empty box in a
*released* supplement is worse than an acknowledged gap --- the paper's own rule
that a precise empty caption beats a plausible curve applies to a draft, not to
a document that ships. The supplement now names the table, says why it is
absent, and states its acceptance in advance, including the one that matters:
the thesis takes two columns and **they must differ**.

One citation is left as the bundle has it. The handover gives Ma \& Bertschinger
Eqs.~(63) and (64) where this bundle integrates and cites Eqs.~(49) and (50).
Ma \& Bertschinger print the hierarchy in two gauges, so both may be correct for
different displays — and under S11 that is resolved from the source, not agreed
between streams. **Open, and raised rather than silently reconciled.**

---

## T-7 — the released supplement had text running off the page, and nothing looked

**Raised 2026-10-09 while adding Table V. Severity: material, cosmetic in
effect.** Corrected the same day.

Compiling the supplement after adding the translations table showed overfull
boxes of **155.9pt and 81.4pt** — 55mm and 29mm of content past the right
margin of a document that ships. Both predate Table V; they were found only
because something new was compiled beside them and its own overrun had to be
measured.

### Cause, which was not the column widths

Three `longtable` specifications used bare `l` columns, and `l` **cannot wrap**.
One long cell therefore sets the width of the whole table however narrow the
other columns are. Narrowing the `p{}` columns by 30mm changed the overrun by
exactly nothing, which is what pointed at the real cause.

Underneath that, `tt()` made underscores breakable but left `/` and `::`
unbreakable, so a path like `tests/test\_appendix\_f\_chain.py::test\_...`
stayed a single rigid box that no column width could contain.

### The correction

Every `l` column in a generated table is now a bounded `p{}`; `tt()` inserts
`\allowbreak` after `/` and `::` as well as after `_`. Worst overrun falls from
155.9pt to 31.9pt, and the two large ones are gone.

### What this says about the gates

The bundle checks hashes, file sets, portability, convergence and the register.
**Nothing compiles the supplement**, so `supplementary-materials/supplement-v1.0.0.pdf`
is the one released artefact `run_all.py` does not generate — it is built by
hand and moved by hand under a different name. Every manual step in this project
has drifted eventually, and this one drifted into print.

Paper 1 has `checks/build_gate.py` for exactly this. The bundle's equivalent is
the obvious next guard: compile the supplement in `run_all.py`, fail on a LaTeX
error, report overfull boxes above a stated threshold, and skip cleanly where
`pdflatex` is absent — the same shape as the git comparison of T-6. **Named
here rather than built today**, so that it is a decision rather than something
rediscovered the next time a table is added.

---

## T-8 — the generated CSVs were CRLF, git stores LF, and the manifest hashed the wrong one

**Raised 2026-10-09 from a one-line git warning in the PI's terminal. Severity:
release-blocking.** Corrected the same day.

```text
warning: in the working copy of 'tables/translations-v1.0.0.csv',
         CRLF will be replaced by LF the next time Git touches it
```

### The defect

`csv.writer`'s **default line terminator is `\r\n` on every platform**, not just
on Windows. `write_csv` opened its file with `newline=""` — which is the correct
opener for the `csv` module, and is exactly why the default terminator then
applies unmodified. So all five generated CSVs were CRLF everywhere, including
in the Linux container.

`.gitattributes` says `* text=auto eol=lf`, so **git stores them as LF**. The
release fingerprint hashes the working tree. Therefore:

| | SHA-256, first 24 |
|---|---|
| working tree (CRLF) | `aab77f543111811778cacb0a` |
| what a clone receives (LF) | `e3ba5daf66feaf564ed64a58` |
| `FILE-MANIFEST-SHA256.txt` records | `aab77f543111811778cacb0a` |

**The manifest describes the folder, not the release.** `make_manifests.py
--check` would fail on a clean checkout, on five files, for a reason that looks
like corruption and is not.

### Why no gate saw it

`check_portability.py` rejects **mixed** line endings within a file. A file that
is uniformly CRLF passes, correctly — mixed endings are the defect it was
written for. Nothing compared the working tree's bytes against the tree git
would hand out.

This is the third member of a family and the pattern is now unmistakable. **T-1:**
the fingerprint absorbed files the folder had and the release did not. **T-6:**
it missed files the release had and the folder did not. **T-8:** it covers the
right files with the wrong bytes. Every one is the same mistake — treating the
working directory as the thing being released — and each was invisible to a gate
that measured something adjacent to the question.

### The correction

`csv.writer(fh, lineterminator="\n")`. All five CSVs are now LF, matching what
git stores and what a clone receives.

**And the gate that generalises all three is now written rather than described.**
`scripts/check_clean_checkout.py` extracts `git archive HEAD` into a temporary
directory — exactly the tracked tree, no `.git`, no untracked files, no build
products — and runs the portability and manifest gates **inside it**. That is
the acceptance performed rather than reasoned about, and it is the form
Coordination asked for: compare the tree, not the folder, and run the acceptance
from a clean checkout. `git archive` is used in preference to `git clone`
because a reader unpacking a zip has no repository either, and the gates must
give them the same answer.

### The lesson

**A warning is a finding.** This one was printed by git, in passing, in the
middle of a successful commit, and would have been read as noise by anyone not
already looking for this class of defect. Three of the eight findings in this
file were caught by someone noticing that a number or a message was the wrong
shape, and none by a gate that was watching for them.

---

## T-9 — two corrections to the same caption silently did nothing

**Raised 2026-10-09, by looking at the figure. Severity: material.** Corrected
the same day, and the method of correcting it is the entry.

F3's footer carried the pre-T-3 reading — *"ΛCDM's peak-to-plateau ratio near 36
is well above the six or so it should be, where standard CDM's 5.8 is about
right"* — printed under a plot showing 7.15 and 60.9. It was **corrected twice**
and survived both times.

### Why

Both corrections used `str.replace` with a pattern containing a right single
quote as the literal character `’`, while the source file carries it as the
escape `’`. No match, no replacement, **no error**. `str.replace` returns
the string unchanged and says nothing, and the surrounding script printed
`captions corrected` because it had reached its last line.

The figure was regenerated each time and looked plausible, because the plot was
right and only the footer was wrong — and a footer is the last thing anyone
re-reads.

### The correction, and the rule

The footer was replaced **by line number**, with the target lines asserted
before the edit and the stale text asserted absent after it:

```python
assert "RELEASE CANDIDATE" in lines[153]
assert "5.8 is about right" in lines[156]
lines[153:157] = new
...
assert "5.8 is about right" not in txt, "stale footer survived again"
```

**An edit that cannot fail cannot be trusted.** Every subsequent in-place edit
in this project asserts that it changed something, and where the old text must
not survive, asserts that too. This is the same discipline the bundle already
applies to its own outputs — measure, do not assume — turned on the act of
editing, which had been exempt.

### Why it belongs in this file

Three of the nine findings here were caught by a person noticing that a number
or a sentence was the wrong shape. This one was caught the same way, and the
thing noticing it was a rendered image: the plot and its caption disagreed, and
only one of them could be right. **Regenerating an artefact and then looking at
it is a test**, and it is the only one that would have caught this.

A related correction landed in the same pass and is recorded here rather than
separately. F3's footer, once it finally took, claimed the $k$-grid truncation
reaches 5% near $\ell\simeq100$. That was the **CDM-only** figure, written while
the ΛCDM arm of the convergence study was still running. Taking the worse of the
two models it is $\ell\simeq50$, and the footer now says so. A number quoted
from a partial run is a number quoted from the wrong population.

---

## T-10 — the portability gate blocked the operation that fixes it

**Raised 2026-10-09 from the PI's terminal, by the clean-checkout gate's first
two real runs. Severity: material.** Corrected the same day.

`run_all.py --rerun` aborted whenever the portability gate failed:

```text
--- portability ---
FAIL  2 portability problem(s):
      diagnostics/ell-convergence-v1.0.0.txt: in the working tree but untracked
      scripts/derive_ell_convergence.py: in the working tree but untracked
NOT RELEASABLE  --  portability gate failed
```

and returned **before regenerating anything**. `--rerun` is the development
route, documented as *"regenerate without the drift gate"*, and its job is to
rebuild figures, outputs, tables and manifests. So a newly written, not-yet-
committed file blocked the one operation that would bring the tree back into
agreement: **regenerate to fix the manifests, but you cannot regenerate until
the files are committed and the manifests fixed.**

Both of the PI's `--rerun` invocations that day hit this and silently
regenerated nothing, which is why the following `check_clean_checkout.py` then
reported seven stale artefacts — figures, outputs and the supplement PDF that
had never been rebuilt.

This is **T-4's mistake in a different place**: a gate ordered so that it
blocks its own remedy. There it was the suite testing the previous run's
artefacts; here it is a gate refusing the regeneration that would satisfy it.

### The correction

The portability gate is **binding on `--strict` and advisory on `--rerun`**. It
still runs, still prints, and still records a failure in the summary, so the
development route cannot report `CLEAN` while it fails — but it no longer
prevents the regeneration.

### The second half, and it is mine

The same clean-checkout run named seven artefacts the PI's tree had never
rebuilt. The cause was not only T-10: **I shipped `FILE-MANIFEST-SHA256.txt`
across the bridge**, describing my container's tree, while transferring only
some of the artefacts it describes.

That is precisely the rule recorded in this file under T-1 — *the manifest is
generated on the machine that publishes* — written by me, followed for two
transfers, and then dropped. **A rule in the record is not a rule in the
hands.** Manifests are no longer transferred at all; they are regenerated on
the publishing machine as the last step before commit, and the clean-checkout
gate is what proves it worked.

---

## T-11 — T-2 came back the moment a new generator was added

**Raised 2026-10-09, by `--strict` failing on manifests immediately after R3
landed. Severity: release-blocking.** Corrected the same hour.

`pdflatex` stamps `/CreationDate`, `/ModDate` and a random `/ID` into every PDF
it writes:

```text
CreationDate = D:20261009140726+02'00'
ID           = <FD20DE95268126836819A88126F80A31> ...
```

So two builds of an unchanged source produced different bytes, and the moment
`run_all.py` started building the supplement — R3, added that morning —
`--strict` could never pass again.

### This is not a new mistake

**It is T-2, in a different generator.** T-2 was matplotlib stamping the wall
clock into every released figure; it was found, fixed, and recorded. What was
*not* done was to state the rule the fix implied: **every generator this harness
owns must produce the same bytes from the same inputs.** Without that rule
written down as a rule, adding a generator reintroduced the defect, and the
entry for T-2 sat three screens above it in this same file.

A finding recorded is not a finding generalised. T-1 and T-6 were the same pair
twice over, and this is the third instance of the pattern: the specific fix
landed and the class did not.

### The correction

`SOURCE_DATE_EPOCH` fixed at a constant, with `FORCE_SOURCE_DATE=1` so `\today`
is deterministic as well. These are the reproducible-builds conventions and TeX
Live honours them for all three fields. Two builds two seconds apart now give
`f0a9b3b1dc13b9628d5eca2b` both times.

**The value is a constant, not the current time**, because a build clock that
moves is the entire problem. What is deliberately *not* claimed is byte-identity
across TeX Live versions: a different engine lays out the page differently, and
stripping the version would hide a real difference rather than remove a spurious
one — the same distinction T-2 drew for matplotlib.

### The rule, stated this time

**Any artefact `run_all.py` generates must be byte-reproducible from the same
inputs, and the check is to build it twice.** That is now a property worth
testing directly rather than discovering through a manifest failure, and it is
the obvious next guard: a generator added without it will reintroduce this a
fourth time.

---

## T-12 — the supplement's margin gate watched one of the two margins

**Raised by Coordination, 2026-10-09, from three defects P1-T found in the
paper's own `checks/build_gate.py`.** One of those three was an `Overfull
\hbox` check with nothing watching `\vbox`, and it is how Eq. (30) printed off
the bottom of page 7 of the manuscript through every clean build until the PI
saw it by eye. Coordination's question was whether
`scripts/build_supplement.py` had the same blind spot.

It did.

```python
def _overfulls(log: str) -> list[float]:
    return [float(x) for x in re.findall(r"Overfull \\hbox \(([0-9.]+)pt", log)]
```

`\hbox` only. A table or figure running past the **bottom** margin produced a
clean build, a PASS, and a released PDF. The gate that exists because T-7 put
55mm past the right margin could not see the other direction at all.

### What it was measured at

**Zero.** Across the 20-page supplement there are no overfull `\vbox`es and no
underfull ones either, so the defect never bit — this is a gate repaired before
it was needed rather than after. That also fixes the threshold without a
judgement: `MAX_VBOX_OVERFULL_PT = 0.0`, because the document has none and the
first one is a regression. Contrast `MAX_OVERFULL_PT = 35.0`, which *is* a
judgement about how far into a side margin is tolerable, and is owned as one.

### Why this one is worth a numbered finding although nothing was wrong

Because it is **the third instance of one pattern**, and the pattern is now
named. T-3's η grid measured the wrong thing. T-6 counted two sets and called
equal counts agreement instead of comparing them. T-12 measured one of the two
directions a box can overflow. In each case the gate reported PASS with the
defect it existed to catch standing in front of it, and in each case the gate
looked, to anyone reading it, like it was doing its job.

**The rule: a gate's blind spot is a defect even while the content is clean.**
It cannot be found by running the gate — a passing gate is exactly what it
produces — so it is found only by asking what the check does *not* match. That
question is cheap and this project has now paid for it three times.

The supplement grows at v1.1.0, when F2, F5, F6, F7 and F8 each add a figure
page. That is precisely when vertical overflow becomes likely, and the gate
would have been blind to it.

### Two of Coordination's three do not apply here

Stated so the absence is recorded rather than assumed. The **log encoding** is
already explicit — `read_text(encoding="utf-8", errors="replace")`, with the
`proc.stdout` fallback decoded the same way — so log length does not depend on
the platform's default codec. The **`.bib` versus `.bbl`** defect has no
analogue: this bundle compiles no bibliography.

---

## T-13 — the release archive was built by hand, on the way out

**Recorded 2026-10-09, immediately after v1.0.0 shipped, and deliberately not
fixed before the tag.** The zip attached to the GitHub release and deposited to
ZivaHub was assembled by an ad-hoc script written in the session, not by
anything in `scripts/`. It was verified — extracted, and `check_portability.py`
and `make_manifests.py --check` run inside it, giving 124 files and four PASSes
— so the artefact is sound. The *process* is the finding.

**Every manual step in this project has eventually drifted, and this is the
file a reader downloads.** That is T-7's lesson exactly: the supplement was
built, moved and renamed by hand until R3 put it under the harness, and in the
meantime it shipped with 55mm of text past the margin. The archive is now in
the same position the supplement was in before R3.

It becomes `scripts/make_release_archive.py` at v1.1.0, with the fixed
timestamp already used here (so the zip is byte-reproducible, the T-11 rule
applied to the archive), the prefix directory, and the extract-and-gate check
run automatically rather than by hand.

**Why not before the tag:** adding a script changes the file count, the
manifests and the clean-checkout number, in a tree that had just passed every
gate and was minutes from being tagged and deposited. Fixing process debt by
disturbing a verified release candidate is how a clean release becomes an
unclean one. The debt is cheaper carried for one version than paid at that
moment.

---

## T-14 — the sources module asserted a frame invariance its equations cannot have

**Found 2026-10-09, opening v1.1.0, by building the thing that would have used
it.** `functions/spectra/sources.py` carried this, from the first version of the
module:

> **The three terms are frame-dependent; their sum is not.** $\delta T$,
> $\Phi_A$, $v_B$ and $\tau_1$ all shift under a change of threading $u^a$, and
> the split of (176) into primary, Doppler and integrated pieces shifts with
> them. Only the total is an observable.

Every sentence of that is true as physics. As a statement about **this code** it
was read — by this stream, when it specified F5 — as licensing an operation it
does not license: transform those four fields into another threading,
re-evaluate (177)–(179), and recover the same total.

### What it does instead, measured

With the energy frame reached exactly — $\tilde\Phi_A=0$ and the Weyl invariant
$\Phi_A-\Phi_H$ both preserved to $1.1\times10^{-16}$, so the transformation
itself is not in question — the assembled transfer function at $k=0.02$:

| weighting | $\ell=2$ | $\ell=5$ | $\ell=10$ | $\ell=20$ |
|---|---|---|---|---|
| visibility | 4.43 | 4.41 | 4.41 | 4.42 |
| opacity | 0.998 | 0.998 | 0.998 | 0.998 |

as a relative difference. Under the visibility weighting the total moves by a
factor of **five**. Under the opacity weighting the energy-frame source very
nearly **vanishes** — it retains about two parts in a thousand.

### Why, and why the second row is the diagnosis rather than a second symptom

**(177)–(179) are Newtonian-threading expressions.** They descend from (106),
which this record already flags in exactly those words — *"(106) defines the
mode coefficient in the Newtonian frame"* — through (107), (110) and (111). The
specialisation is upstream of everything the module computes.

Paper 1 Secs. VI B and VI C say what the other threading looks like. In the
Newtonian threading $\tilde\sigma_{ab}=0$ and $\tilde A_a=\mathrm D_a\Phi_A$, so
the whole $O(\ell)$ source is the **acceleration pair**, Eq. (newt-pair). In the
CDM threading $\tilde A_a=0$ and $\sigma^C_{ab}=\mathrm D_{\langle a}v^C_{b\rangle}$,
so the whole of it is the **shear pair**, Eq. (cdm-triple). They are two
reductions of the one operator $K_\perp^a\partial/\partial e^a$, differing in
which kinematic quantity supplies $K^a$.

So moving to the energy frame sets to zero the coupling that was carrying the
source, while the coupling that should replace it is **not in these equations at
all**. The near-total collapse is that deletion. It is not a frame-dependence of
the sky, and reading it as one would be the serious error here.

### What this changes

**F5 and F7 cannot be drawn from this module, in any frame but one.** That is
decision **S21**, and it supersedes S20's placement of them at v1.1.0. The
figures need the generic-$u^a$ source, which is v1.5.0's subject (decision S2)
and not a figure's worth of work.

**S20's reason was wrong twice over, in opposite directions**, and both are now
corrected in the record. It said the blocker was $\Phi_H$'s transformation rule;
that rule was already in Paper 1 Sec. VI A with a source, and is now implemented
and checked. The actual blocker is one layer deeper and was not identified at
all: the source equations are themselves frame-specialised. **A deferral can be
right and still rest on a wrong reason, and this one did.**

### The pattern, again

T-3, T-6 and T-12 were each a check looking at the wrong object. T-14 is its
sibling: **a docstring asserting a property the code does not have**, which is
worse, because a comment is read as documentation rather than as a claim needing
evidence. It survived from the module's first version through a tagged release
because nothing exercised it — the only artefact that would have was F5, and F5
was deferred.

`tests/test_frame_transform.py::test_T14_the_transfer_function_is_NOT_frame_invariant_under_177_to_179`
pins the measured collapse as a range, so that a fix and a regression are
distinguishable and the day the generic-$u^a$ source lands the test fails and is
rewritten into the invariance it should then assert.

### T-13 — closed 2026-10-10

`scripts/make_release_archive.py`. The file set comes from the shared selector
(T-1), member timestamps are pinned to the same instant `build_supplement.py`
uses so the two generators cannot disagree about "now" (T-11), and the script
**extracts what it built and runs the portability and manifest gates inside it**
before reporting success — R2's discipline applied to the file that leaves.

**It found a defect on its first run, which is the argument for having written
it.** `dist/` was not in `.gitignore`, so the archive — a zip *of the bundle* —
landed inside the file set the fingerprint is taken over. Building a release
would have changed the manifest, which would have invalidated the archive that
had just been built. That is **T-1 for the third time**, and this time the gates
T-1 produced caught it before it reached anything. Fixed in `.gitignore`, with
the reason recorded there rather than as a bare line.

### T-14 — scope extended 2026-10-10: F2 is blocked by the same thing

Recorded here rather than as a new finding, because it is the same defect seen
from another figure. **F2 cannot be drawn as specified either.** Its
specification is *"run in both frames"*, checking Annals II footnote 29 on
p. 365 — that choosing the Newtonian frame "would also remove any problems we
may have with the introduction of high-$\ell$ truncation as discussed in
Appendix E". Checking that claim requires running the hierarchy in a threading
that **has** shear, and the bundle has only the shear-free one.

So **three of the five figures deferred to v1.1.0 — F2, F5 and F7 — wait on the
generic-$u^a$ hierarchy**, not on figure work. F6 and F8 do not: F6 is ratios of
approximations within one threading, and F8 is a schematic with no computation.
A single-frame F2 is buildable and would make Appendix E quantitative, but it
would not check footnote 29, which is the stated reason the figure exists —
so it is not built here, and the choice is the PI's rather than this stream's.

---

## T-15 — the release route cannot pass on a second machine

**Found 2026-10-10, by the PI running `run_all.py --strict` on Windows against
a manifest whose artefacts were generated in a Linux container.** It reported
`NOT CLEAN — manifests`. The mismatch:

```
changed  diagnostics/d1-sign-control-v1.0.0.png
changed  figures/f1-appendix-f-v1.0.0.pdf      changed  figures/f1-...png
changed  figures/f3-angular-spectrum-v1.0.0.pdf  changed  figures/f3-...png
changed  figures/f4-correlation-v1.0.0.pdf     changed  figures/f4-...png
changed  supplementary-materials/supplement-v1.0.0.pdf
changed  outputs/f1-appendix-f-residuals.csv
changed  outputs/f4-correlation.csv
changed  outputs/line-of-sight-field.csv
```

**`--strict` regenerates every artefact and then checks its hash.** So it can
only pass on the machine that produced the committed bytes. That is not a bug in
the gate; it is the gate asking a question nobody checked was answerable.

### The part that was predicted, and the part that was not

The seven renderings and the supplement were expected. `pdflatex` lays a page out
differently across TeX Live versions — **T-11's own docstring says so in those
words**, "what is deliberately *not* claimed is byte-identity across TeX Live
versions" — and matplotlib output depends equally on its version, on freetype and
on the installed fonts. A disclaimer written in one finding and a gate written in
another, neither aware of the other.

**The three CSVs were not predicted, and they are the more interesting half.**
They are plain text written with `%.12e`. Differing bytes mean the *numbers*
differ in their last digits between a Linux container and a Windows machine —
different BLAS, different libm, different scipy build. That is ordinary
floating-point reality, and it means the defect is not confined to renderings:
**byte-identity is the wrong criterion for any generated numerical artefact**,
not merely for pictures.

### What this does and does not threaten

It does **not** threaten any released result. `check_clean_checkout.py` does not
regenerate; it hashes what the tag contains, which is why v1.0.0 passed on the
PI's machine at 124 files and why the deposited archive verifies. The
reproducibility claim the bundle makes — *run this and you get these numbers* —
is intact at the precision that matters.

What it threatens is the **release route**: `--strict` is documented as the route
a release candidate must pass, and a second person cannot run it. A gate only one
machine can satisfy is a gate that will be routed around.

### The fix, and why it is not "loosen the tolerance"

The scientific content of a figure is the data behind it, not its pixels, and the
content of a CSV is its numbers, not their last bit. So:

* **text artefacts stay binding**, compared as *numbers within a tolerance*
  rather than as bytes where they are numeric;
* **renderings become a within-machine drift check** that reports rather than
  blocks, because a PNG that differs only in font hinting carries no scientific
  difference;
* and `--strict` must **say which kind of mismatch it found**, so a byte
  difference in a PNG is never again indistinguishable from a changed number.

Deferred to v1.2.0 with its own entry rather than patched now: it touches the
manifest format, the gate and the clean-checkout script together, and the PI's
tree is mid-release-cycle. **Until it lands, `--rerun` is the route to use on a
machine that did not generate the artefacts**, and the manifest should be
rewritten locally rather than shipped between machines.

---

## T-16 — a convergence alarm that reported a proxy instead of the quantity

**Found 2026-10-10 in the same run.** `figure_f3_angular_spectrum.py` printed,
beside the key figure of a released bundle, on **every** run:

```
damping still 0.892 at the k grid edge  <-- TRUNCATED, not converged
```

The predicate was `damping_at_k_max < 1e-2`: whether the $k$ grid runs past the
Silk damping cut-off. That is a real question with a real answer — the grid does
stop short — but it is **not the question the message answers**, and a reader
cannot tell from it whether the released spectrum is trustworthy.

### Two wrong readings, both recorded

**This stream's first diagnosis was wrong.** Reasoning that $j_\ell(k\Delta\eta)$
contributes near $k\simeq\ell/\Delta\eta$, so $\ell\le20$ lives near $k\simeq10$
on a grid running to 420, it concluded the alarm was crying wolf. Replacing the
flag with a direct test — recompute every $C_\ell$ with the top 10% of the grid
removed — returned **2.4e-1**, and the alarm was vindicated.

**That measurement was also wrong**, for the opposite reason: it maximised over
every $\ell$ computed, and F3 computes to $\ell=400$ while claiming only
$\ell\le20$ and **shading the rest of the panel**. The 24% came entirely from
multipoles the figure tells the reader not to trust.

Measured over the claimed range, dropping the top 10% of the grid:

| | $\ell\le20$ (claimed) | all computed, to $\ell=400$ |
|---|---|---|
| standard CDM | **5.0e-3** | 2.4e-1 |
| $\Lambda$CDM | **8.9e-4** | 4.6e-2 |

So the released spectrum is converged to half a percent over what it claims, and
badly unconverged where it says so itself.

### The defect, stated properly

Not that the alarm was false — it was true. **It reported a proxy for the
quantity of interest, without the range or the magnitude, so its severity could
not be judged.** Severity is the whole content of a convergence warning.

The gate now reports the measured sensitivity **over the claimed range**, the
same number over everything computed, and the Silk-scale statement separately and
labelled as what it is: a readiness condition for v1.2.0's acoustic peaks, which
this release does not need.

**Related to T-12 and T-14 but distinct from both.** T-12 was a check that looked
at the wrong object; T-14 a docstring asserting a property the code lacked; T-16
a check that looked at the *right* object and reported it in a form that could
not be acted on. All three pass or fail honestly and all three mislead.

### T-15 — closed 2026-10-12

`PORTABLE-MANIFEST-SHA256.txt`, and `--strict` now binds on it rather than on
byte-identity.

**The design, and why it is not "loosen the tolerance".** Three classes, derived
from the path and never from a hand-maintained list — the mistake T-1 and T-16
are both about:

| class | what it is | how it is compared |
|---|---|---|
| `exact` | source, documents, configuration | byte hash, **release-blocking** |
| `numeric` | generated text carrying computed numbers | every float re-emitted at **9 significant figures**, then hashed; **release-blocking** |
| `rendered` | PNG, PDF, the supplement | byte hash, **reported as drift, not blocking** |

`FILE-MANIFEST-SHA256.txt` is unchanged and still `sha256sum -c`-able; it has
become the *within-machine* drift report. The portable manifest is what the
release stands on, and it excludes the renderings because a PNG differing in
font hinting carries no scientific difference, while keeping every number that
does.

**Nine significant figures is a first value, not a measurement**, and that is
stated where it is defined. Cross-platform noise is last-digit, around
$10^{-15}$ relative, and a solver amplifies it by a few orders at most; nine is
far above that and far below any change worth the name. **The PI's machine is
the measurement**: a Windows run against this Linux-generated manifest either
passes, which is the evidence, or fails and reports the real magnitude.

**Tested with its control, which is the part that matters.** Perturbing every
float in `outputs/f4-correlation.csv` by $3\times10^{-16}$ — what another BLAS
does — leaves the binding gate **passing with exit 0**, the byte manifest
reporting `DRIFT`, and the release route runnable by a second person. A change
of $10^{-4}$ **fails with exit 1**. Without the second assertion the first is
indistinguishable from having switched the gate off, so both are in
`tests/test_portable_manifest.py`.

**What this does not change.** No released artefact moves, no number moves, and
`check_clean_checkout.py` inherits the improvement without modification. What
changes is that the route documented as the one a release candidate must pass
can now be run by somebody who did not render the figures.

### T-15 — reopened and closed properly, 2026-10-12

**The first close was premature, and the PI's machine said so.** Nine
significant figures was offered as a first value with the explicit note that
the PI's run was the measurement. The run came back: **fourteen of sixteen
sampled artefacts agreed** across Linux and Windows — and two did not. Both had
been in the original mismatch list, and they turned out to be *different
problems*, neither of which a single significance cut can fix.

#### `outputs/line-of-sight-field.csv` — signed zero

Every number in it agrees to about **twelve significant figures**, and the
headline values in its header — `endpoint`, `running_excursion` — are
character-for-character identical. Nine should have absorbed that and did not.
The cause is one row: `-0.000000000000e+00` on one machine, unsigned on the
other. `f"{-0.0:.8e}"` is `-0.00000000e+00`, so the canonicalisation preserved a
minus sign in front of zero and moved the hash of a file in which nothing had
changed. **The sign of zero is not a scientific statement** and is now
normalised away.

#### `outputs/f1-appendix-f-residuals.csv` — not a digit problem at all

Measured across all 104 rows, the worst relative difference is **62%**:
$2.2\times10^{-14}$ against $5.8\times10^{-14}$. They agree to **less than one
significant figure**.

That is not float noise and no cut can absorb it. A residual is a difference of
nearly equal quantities, so its own relative precision is set by the
cancellation and not by its inputs; both numbers are the same claim — *zero to
machine precision* — in two roundoff realisations. Lowering the cut far enough
to make this file pass would have weakened the gate for every other artefact to
accommodate one that can never pass it.

**So it leaves the binding manifest, and is checked by what the bundle actually
claims about it instead.** `artefact_class` gained a fourth value, `bounded`.

#### The gap that found, which is the more serious half

F1 is where this bundle's independence lives — four external hierarchies, each
read from its own paper. Its evidence is that CSV. **Nothing verified it.** The
script printed the residuals, the caption claimed $10^{-13}$–$10^{-14}$, the
manifest hashed the bytes, and no gate ever asked whether the numbers were
small. A hash is not a check on content; it only notices change.

`tests/test_appendix_f_chain.py` now asserts the ceiling: every residual below
$5\times10^{-13}$, four hierarchies present, and every `scale` exactly one —
because a match obtained by rescaling would not be a match. The ceiling is
measured: the largest observed is $9.5\times10^{-14}$, **independently on both
machines**, so five times that is a bound with room and still twelve orders
below the quantities being differenced.

**The pattern, for the fourth time.** T-3, T-6, T-12 and T-16 were each a check
looking at the wrong object. This is the same family seen from a new side: a
gate that hashes an artefact looks like it is checking the artefact, and is
checking only that it has not moved. Asking what a gate does *not* match
remains the cheapest question this project knows.

## T-17 — the bundle's $\ell$ ceiling was 507, set by a quantity equal to one

**Found 2026-10-12, while measuring the forward-evaluation cost for the
`bundle1-v1.5.0` interface question.** Timing `pipeline.run` over a doubled
$\ell$ grid raised, from the first line of (186)'s prefactor:

```
OverflowError: (34, 'Numerical result out of range')
  prefactor = float(beta(ell)) ** 2 * float(alpha(ell)) ** 2 / (2 * ell + 1) ** 2
```

That prefactor is $\beta_\ell^2\alpha_\ell^2/(2\ell+1)^2$, and it is **exactly
one for every $\ell$** — the module docstring says so, three times, and it is
the reason the bundle can claim that an $\alpha_\ell$ or $\beta_\ell$ slip
cannot hide in the spectrum. It was being evaluated by converting each factor
to a double and then dividing. $\beta_\ell=(\ell!)^22^\ell/(2\ell)!$ is
$6.3\times10^{-270}$ at $\ell=900$, so $\beta_\ell^2$ underflows to zero while
$\alpha_\ell^2=(2\ell+1)^2/\beta_\ell^2$ overflows, and their exact ratio of one
was unreachable through them.

Bisected, the largest $\ell$ at which the released code could return a $C_\ell$
was **507**. At $\ell=507$ the prefactor evaluated to `1.0000000000000004`; at
508 it raised. The covariant route inherited the same ceiling through
`multipole_mean_square`, whose own coefficient
$\beta_\ell\alpha_\ell^2=(2\ell+1)^2/\beta_\ell$ stops being a double near
$\ell\simeq1500$.

### Why 507 is the wrong number to have as a ceiling

The first acoustic peak is at $\ell\simeq220$ and the damping tail runs to
$\ell\simeq2000$. The ceiling therefore sat **between the second peak and the
third**, which is nowhere: too high for v1.0.0 to have noticed, since the
release claims $2\le\ell\le20$ and F3 computes to 400, and too low for anything
planned.

**v1.5.0 is an $O(\epsilon^2\ell)$ correction to the high-$\ell$ spectrum.
Its entire content lives above $\ell=507$.** The release that exists to add the
high-$\ell$ term could not compute the high-$\ell$ spectrum, and nothing said
so. v1.2.0's acoustic peaks would have met it first.

### The correction

The coefficients are combined in $\mathbb Q$ and converted once, which is what
`weights.py` already instructs — *multiply by `4 * math.pi` at the point of
numerical use, never before a comparison*. `_mode_coefficient` and
`_covariant_coefficient` return `Fraction`s; both are asserted equal to one over
$2\le\ell\le2000$. `cl_covariant_route` no longer routes through
`multipole_mean_square`: $\Delta_\ell$'s $\beta_\ell$ cancels the $1/\beta_\ell$
in the mean square, and cancelling it exactly costs nothing while forming both
halves in doubles costs the answer. The published route is unchanged — (187)
then (188), in that order — with the division done before the conversion rather
than after.

`multipole_mean_square` is the one quantity here that genuinely exceeds the
double range, and it keeps doing so: the multipole mean square really is that
large in a normalisation where $\beta_\ell$ is that small. It now raises with
the reason named and points at the route that stays finite, rather than
returning `inf` into a spectrum.

**No released number changes.** At $\ell\le507$ the old prefactor was one to
within a few ulp, so the correction moves released artefacts at the
$10^{-16}$ level and the portable manifest — which binds at nine significant
figures — is unmoved.

### The checking defect, which is the half worth keeping

`tests/test_angular.py` **already asserted this identity exactly**, as
`Fraction`s, at $\ell=1000$:

```python
assert beta(ell) ** 2 * alpha(ell) ** 2 / Fraction(2 * ell + 1) ** 2 == 1
```

It passed. It had always passed. It asserts the identity at an $\ell$ where the
code it is meant to be testing **raises**, because the test evaluates the
expression in exact arithmetic and the implementation evaluated it in doubles.
The test proved the mathematics and said nothing whatever about the code.

That is a new member of the family — T-3, T-6, T-12, T-15, T-16 were each a
check looking at the wrong object, and this one looks at the right object in the
wrong arithmetic. **An exact assertion about an expression is not a test of an
implementation that evaluates it differently**, and the gap is invisible exactly
where it matters, because exact arithmetic is precisely what does not overflow.
`test_cl_is_computable_above_the_old_ell_ceiling` now calls the functions.

### What it says about the interface freeze

Had `bundle1-v1.5.0` frozen its $\ell$ range before this was found, the frozen
number would have been an artefact of a double-precision intermediate in a
quantity equal to one, and P2-B would have inherited it as a physical limit.
The cheapest moment to find a boundary defect is before the boundary is
declared, which is the argument for declaring it now and the argument for
measuring rather than describing the code when answering what it can do.

## T-18 — the Bessel table built every multipole, asked for or not

**Found 2026-10-13, on the first run past T-17's ceiling.** `pipeline.run` built
its table as

```python
table = BesselTable.build(ell_max=int(ells.max()), x_max=...)
```

and `BesselTable.build` tabulates the **contiguous** range
$[\ell_{\min},\ell_{\max}]$. But `ells` is logarithmic and sparse — the release
grid is 24 points from 2 to 400, the high-$\ell$ grid 38 points from 2 to 2000 —
so the table carried about **fifty-three times** the multipoles anybody asked
for, each with its own cubic spline.

Measured at the $x_{\max}$ a high-$\ell$ run needs ($k_{\max}=1500$,
$x_{\max}=4878$, 18631 samples):

| | multipoles | values | splines | total |
|---|---|---|---|---|
| contiguous $0\ldots2000$ | 2001 | 284 MB | 1138 MB | **1.39 GB** |
| the 38 actually requested | 38 | 5.4 MB | 21.6 MB | **0.026 GB** |

At $\ell_{\max}=400$ this is 57 MB and nobody notices. **It becomes 1.4 GB at
exactly the $\ell_{\max}$ T-17 just made reachable**, which is the pattern worth
naming: removing one ceiling exposes the next, and the next one had never been
under load because the first one stopped everything short of it.

### The correction, and the bug it would have hidden

`build` takes an optional `ells`, and `pipeline.run` passes the grid it was
given. The contiguous path is unchanged and still used by the diagnostics and
the low-$\ell$ figures.

`__call__` had to change with it, and this is the part worth keeping. It read

```python
idx = int(ell) - int(self.ell[0])
```

which is correct **only** while the tabulated set is contiguous. Against a
sparse table that arithmetic lands on a valid index of the **wrong multipole** —
asking for $j_{400}$ and receiving $j_{37}$ — silently, with no error and a
plausible-looking spectrum out the far end. It is now a lookup that raises on a
multipole the table does not carry.

**The defect and its fix were one keystroke apart**, which is the whole argument
for making the index say what it means rather than exploiting a property of the
current caller. T-3, T-16 and this are the same shape: an expression that is
true of the inputs it happens to receive, and silent when it stops being.

## T-19 — there is no last-scattering-thickness damping, and the spectrum needs it first

**Found 2026-10-13, on the first spectrum computed past T-17's ceiling**, which is
the point: this defect lives entirely above $\ell\simeq700$ and the bundle could
not reach $\ell=508$.

### What the high-$\ell$ spectrum does

$\Lambda$CDM and standard CDM, $k_{\max}=1500$ (so the grid passes the Silk
cut-off, $\exp[-(k_{\max}/k_D)^2]=7.3\times10^{-4}$), $n_\eta$ derived at 18551,
twelve samples per oscillation, $n_s=0.96$, normalised to $\ell=2$:

| $\ell$ | 2 | 10 | 20 | 100 | **200** | 250 | 300 | 570 | **870** | 1300 | 2000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| $\Lambda$CDM | 1.00 | 0.76 | 0.87 | 2.3 | **3.17** | 3.09 | 3.04 | 7.4 | **11.5** | 5.7 | 2.31 |
| CDM | 1.00 | — | — | — | — | — | — | — | **25.8** | — | 2.86 |

**What is right.** The Sachs–Wolfe plateau is flat to within 30% over
$2\le\ell\le30$. The first acoustic peak is at $\ell\simeq200$ against a standard
220, and the first trough follows at $\ell\simeq250$–300. The peak *spacing* is
about right.

**What is wrong.** $D_\ell$ **grows** through the acoustic region instead of
falling: it reaches $11.5\times$ the $\ell=2$ value at $\ell\simeq870$ for
$\Lambda$CDM and $25.8\times$ for CDM. A real spectrum's peaks decline under the
damping envelope. **There is no damping tail here at all.**

### It is not numerics, and that is established rather than assumed

| | measured |
|---|---|
| $k$-grid truncation, top 10% dropped, $\ell\le20$ | $6.0\times10^{-10}$ |
| the same over every computed $\ell$ | $1.3\times10^{-6}$ |
| $\eta$ samples per $j_\ell$ oscillation at $k_{\max}$ | 12.0, derived (T-3) |
| two-route gap | exactly 0 (T-17) |
| `reaches_diffusion_scale` | **True** |

So T-3's and T-16's machinery earns its keep here: it says, before any argument
about the physics, that the quadrature is converged and the error is in the
**source assembly**.

### The cause

`pipeline.run` assembles the primary term as

```python
primary_at_star * j_l(k * (eta_0 - eta_star))
```

— the visibility replaced by a **delta function at $\eta_*$**. Last scattering is
instantaneous, so the $j_\ell$ oscillations are never averaged across the
surface's width and nothing suppresses high $\ell$ from that direction. The only
suppression left is Silk, $\exp[-(k/k_D)^2]$, and $k_D$ is stipulated at
$\eta_*$.

Measured, the two scales are not interchangeable:

| suppression | scale | $\ell=k\,\Delta\eta$ |
|---|---|---|
| Silk, $k_D(\eta_*)$ | 557.8 | **1807** |
| the visibility's own width, $1/\sigma_\eta$ (FWHM $0.00972$) | 242.3 | **785** |

**The spectrum departs at $\ell\simeq700$.** The thickness scale sits at 785 and
the Silk scale more than twice as far out, so the one the bundle implements
cannot do the job of the one it omits.

**And the width was measured at v1.1.0, by the release's own named deliverable.**
Peebles recombination moved the visibility's FWHM from $\Delta z\simeq120$ to
$\simeq167$, and `RELEASE-NOTES-v1.1.0.md` says in terms: *"The visibility width
is what fixes the Silk damping envelope, which is why acceptance criterion 5b was
blocked on this module."* The assembly then evaluates the primary source at a
single $\eta$ and throws that width away. **The release computed the right number
and did not use it.**

### Two repairs tried, both falsified, both the same way

Recorded because a wrong turn costs more when it is not written down.

**(i) Split (178)'s bracket.** A-2 moved the whole Doppler bracket to the
opacity; probing it showed 74–82% of its line-of-sight weight now sits at
$\eta>\eta_*$, against a $\tau_1$ frozen at the end of tight coupling. So:
$(1/3)k\tau_1$ on the visibility, $(\kappa'v_B)'$ on the opacity — following
A-2's own note that (98) *"prints the two weights separately"*. **Result: worse
at both ends.** The plateau dips to 0.48 at $\ell=16$ and the high-$\ell$ growth
reaches $23\times$.

**(ii) Integrate the primary against $\mathcal V$** rather than evaluating it at
$\eta_*$. **Result: no plateau at all** — $D_\ell$ reaches $273\times$ at
$\ell=200$, which is $C_\ell\simeq$ constant, A-2's pathology exactly.

Both failures have one shape: **moving a term onto the visibility makes
$\mathcal V\kappa'\sim\kappa'^2e^{-\kappa}$ dominate**, with
$\kappa'\simeq1.4\times10^4$ at last scattering. The $\kappa'$ in (177)'s
$\kappa'v_B$ and the $\kappa'$ inside $\mathcal V=\kappa'e^{-\kappa}$ are not
independent, and the assembly is double-counting or mis-assigning one of them.

### What is actually blocked, and it is not numerical

A-2 ends: *"The tilde variables of §5 carry factors of $k$ relative to the
untilded ones of (98), and this stream has not derived that mapping in full ...
**the reading of $\tilde v_B$ is the thing to check if this is ever
revisited**."*

It is now revisited, and that sentence has gone from a footnote to the blocker.
A-2 was established over $2\le\ell\le200$, where neither failure mode is visible;
T-17 then kept the bundle out of the range where they are. **Two defects hid each
other**, which is the fourth time in this record that a ceiling has concealed the
thing just past it.

**The next step is reading, not computing**: (98) and its three brackets, the
(102) visibility substitution, and the §5 tilde mapping, against (176)–(179).
Two numerical guesses have now been falsified in a row, which is the signal to
stop guessing. **v1.2.0's "full source assembly" is this, and it is a derivation
of a page or two rather than a code change.**

---

### CORRECTION, 2026-10-13, hours after the above. **The cause named above is
wrong, and it is kept with this note rather than rewritten.**

The section above attributes the missing envelope to the delta-function
treatment of last scattering. That is a real approximation and it is really
there — but it is **far too small to be the cause**, and this stream reported it
before measuring it at the level that decides.

Measured properly: what enters $C_\ell$ is
$\int dk\,k^2\mathcal P|T_\ell|^2$, so the quantity is the **phase-averaged
mean square** of the projection over $k$, not its value at any one $k$. Taking
a band of $k$ spanning several $j_\ell$ oscillations,

$$R(\ell)=\frac{\big\langle[\int\mathcal V j_\ell\,d\eta]^2\big\rangle_k}
{\big\langle j_\ell(k\Delta\eta_*)^2\big\rangle_k}$$

| $\ell$ | 10 | 100 | 200 | 400 | 700 | 1000 | 1500 | 2000 |
|---|---|---|---|---|---|---|---|---|
| $R(\ell)$ | 0.992 | 0.993 | 0.975 | 0.954 | 0.901 | **0.841** | 0.740 | **0.639** |

**16% at $\ell=1000$ and 36% at $\ell=2000$.** The spectrum is wrong there by a
factor of **eleven**. Tens of percent cannot produce that, so the delta surface
is a defect of the assembly but **not** the one this finding set out to name.

**Two estimates were wrong in the same direction, and both were mine.** The
Gaussian form $\exp[-(k\sigma)^2]$ predicts 0.19 at $\ell=1000$ where the truth
is 0.84, and the "fraction of a $j_\ell$ oscillation spanned",
$f=k\,\mathrm{FWHM}/\pi$, predicts failure from $f\simeq0.7$ onward. Both
over-estimate the smearing badly, for the same reason: near its turning point
$x\simeq\ell$, $j_\ell$ does **not** oscillate with period $\pi$ — it varies far
more slowly, so a surface that looks thick in units of the asymptotic period is
thin in units of the function's actual variation. **An asymptotic period used
outside the asymptotic regime is not a scale.**

**No threshold is therefore shipped on $f$.** A guard on a parameter that has
been shown not to govern the thing would be worse than no guard: it would carry
the authority of an enforced check and the content of a coincidence. The
governing quantity is $R(\ell)$, it is measurable directly, and nothing will be
enforced until what it has to be enforced against is known.

**What survives of the section above**, unchanged: the spectrum is right to
$\ell\simeq300$ and wrong above $\simeq700$; it is **not** numerics
($k$-truncation $6\times10^{-10}$ at $\ell\le20$, $n_\eta$ derived, two routes
exact); it is **not** the $k$ spacing (refining $dk$ from $\pi/6$ to $\pi/24$
moves $C_\ell$ by $1.7\times10^{-3}$ and then stops); and the two weighting
repairs are falsified. What is withdrawn is the claim that the thickness is the
cause. **The cause is being measured by decomposing (176) into its three terms
rather than inferred from a plausible mechanism** — which is what should have
happened before it was reported.

**The pattern, named because it has now cost three statements in two days.**
S21, S23 and this one were each a cause inferred from a description rather than
read out of a measurement or a source. Here the inference was worse than usual
because a *number* was attached to it — $\ell\simeq785$ — and a number reads as
a measurement whether or not anything measured it.

### The decomposition, which is a measurement and not an inference

(176)'s three terms, computed separately and then as transfers at
$k=\ell/\Delta\eta$ (the $k$ that dominates each $\ell$), $\Lambda$CDM:

| $\ell$ | $T^{\rm primary}$ | $T^{\rm Doppler}$ | $T^{\rm grav}$ | $T^{\rm total}$ | cancellation |
|---|---|---|---|---|---|
| 20 | $-1.078$ | $+1.022$ | $-1.9\times10^{-1}$ | $-0.246$ | 4.4× |
| 100 | $-1.450$ | $+1.356$ | $-1.9\times10^{-2}$ | $-0.113$ | 12.8× |
| **200** | $-1.356$ | $+1.277$ | $-4.6\times10^{-3}$ | $-0.0838$ | **16.2×** |
| 500 | $-0.138$ | $+0.202$ | $-1.4\times10^{-3}$ | $+0.0632$ | 3.2× |
| **1000** | $-0.0717$ | $-0.0070$ | $-4.8\times10^{-4}$ | $-0.0792$ | **0.9×** |
| 2000 | $-0.0257$ | $-0.0080$ | $-7.2\times10^{-5}$ | $-0.0337$ | 0.8× |

**The primary and Doppler transfers are opposite in sign and nearly equal at low
$\ell$**: the spectrum there is the residue of a cancellation that reaches **one
part in sixteen** at $\ell=200$. Above $\ell\simeq500$ the cancellation fails, the
two terms take the same sign, and the total becomes the primary term alone —
which carries no envelope. **The growth is not something added at high $\ell$; it
is something that stops being subtracted.**

The gravitational term is $10^{-2}$–$10^{-5}$ of either and is not involved.

**The hypothesis this points at, stated as a hypothesis.** (177) carries
$\kappa'v_B$ and (178) carries $(\kappa'v_B)'$ — the boundary term and the bulk
term of one integration by parts of a visibility-weighted Doppler source.
Carrying both would double-count, and a double-count that partially undoes
itself is exactly a near-cancellation that holds while the boundary term
dominates and breaks when it does not. **This stream has now been wrong about a
cause three times in two days and will not act on this one before reading (98),
(102) and the §5 tilde mapping against (176)–(179).** The table above is a
measurement; the sentence before it is not.

**Why it matters beyond correctness, and before v1.5.0.** A spectrum that is the
residue of a 16× cancellation is numerically fragile — it is where the $dk$
bias of $1.7\times10^{-3}$ and every other small error get amplified. v1.5.0's
$O(\varepsilon^2\ell)$ term would be added on top of that. If the assembly is
carrying a term twice, removing it does not merely fix the envelope: it removes
the cancellation, and the quartic then sits on something stable. **That is the
argument for fixing it before the interface freezes rather than after.**

### The reading, done 2026-10-13 against `sources/annals/cbrII.tex`

**A-2's flagged question is answered, and the answer clears the bundle.**

| read from | says |
|---|---|
| (90) `C-B-coef` | $-C_1(\eta)\simeq\frac1k(a\mathcal B_1+\kappa'v_B)$, and **"Note that these are CGI with respect to $u^a$"** |
| (109) `calc-ng` | $-\tilde C_1(\eta)\approx\kappa'\tilde v_B+(\delta\tilde T+\Phi_A)$ |
| (98) `slowdec_1` | carries an explicit $\frac1k$ on **both** baryon-velocity terms, weighted by $e^{-\kappa}$ |
| (111) `slowdecoupling-ng` | the same three brackets as (177)–(179), **with $\kappa'\tilde v_B$ tilded** |
| (156) `v-2nd` | $v_a^B\approx\tau_a-\frac R{\dot\kappa}[\dot v_a^B+Hv_a^B+A_a]+O(\dot\kappa^{-2})$ |
| footnote to (152) | $\tilde{\mathcal D}_a\ln T\approx\frac ka\delta\tilde TQ_a$ but $\tilde\tau_a\approx\tilde\tau_1Q_a$ |

**The $k$ factors are mode-decomposition, not notation.** $\mathcal B_1$ and
$\Phi_A$ are *gradients* and carry $k/a$; $\tau_a$ and $v^B_a$ are *vectors* and
do not. (90)'s $v_B$ sits beside $a\mathcal B_1$, so it is the gradient-level
coefficient, and the $\frac1k$ that converts it is the same $\frac1k$ that
converts $a\mathcal B_1$ into $(\delta\tilde T+\Phi_A)$. At vector level (156)
gives $v^B_a\approx\tau_a$ at zeroth order in the scattering time, with **no
$k$**. **So `v_b = tau_1` is correct and the bundle is faithful.**

Tested anyway, because the inference had been wrong three times: setting
`v_b = tau_1/k` **destroys the acoustic structure entirely** — $D_\ell$ becomes
monotonically decaying, peaking at $\ell=2$ and reaching $1.7\times10^{-3}$ by
$\ell=2000$. **Fourth falsified repair.**

**One finding against the paper.** (177) writes $\kappa'v_B$ **untilded** where
(111), the equation it is transcribed from, writes $\kappa'\tilde v_B$, and
where (109) and (178)–(179) all keep their tildes. A dropped tilde in (177).
It changes nothing here — the bundle implements (111)'s form — but it is a
defect in the printed equation and belongs in the corrections record as a
**B-finding**, not here.

### What the reading leaves standing, and it is not a code defect

Four repairs are now falsified and the assembly reads as faithful to (176)–(179)
and to (111). What has **never been tested** is the paper's own stated validity
condition for the solution being implemented. §5 introduces it as

$$\kappa''\ll1,\qquad(\kappa')^2\ll1$$

— the **slow-decoupling approximation** — and adds *"A further approximation
would be to take $e^{-\kappa}\gg\kappa'e^{-\kappa}$, so that we need only
consider the free-streaming like solutions."* Both are conditions on the
scattering rate against the mode frequency, so **both are $k$-dependent, and
nothing in this bundle measures where they hold.**

That is a *measurement*, not a mechanism, and it is the next one: **the bundle
may be reproducing Annals II correctly and reproducing it outside its stated
range.** T-16's lesson in a new place — the question is not only whether the
code matches the equation but whether the equation was claimed to apply here.

**Not asserted as the cause.** Three causes have been asserted and withdrawn in
two days. This one will be measured before it is named.

## T-20 — Annals II's two weightings are each right in one regime, and neither in both

**Found 2026-10-13, reading `int_soln_damping` and re-reading the variant runs.**
The reading first **cleared** the stated approximations:

- $(\kappa')^2\ll1$, $\kappa''\ll1$ multiply **$C_2$ alone** in the general damped
  solution's last line — and $\tilde C_2\approx0$ identically in the Newtonian
  frame, where $\tilde\sigma_{ab}\approx0$. **The approximation is exact here.**
- the $\int\kappa'e^{-\kappa}[C_1-2C_2]$ line that (102) drops is suppressed
  relative to the retained $\int e^{-\kappa}C_1'$ as $\kappa'/k$, since $C_1$
  varies on the mode timescale. **It gets better at high $k$, not worse.**

So neither stated approximation explains a high-$\ell$ failure. What does show
up is the weighting, and it shows up as a **crossover**:

| | $2\le\ell\le30$ | first peak | $\ell\simeq870$ | $\ell=2000$ |
|---|---|---|---|---|
| $\mathcal V$, as (178)–(179) print it | **no plateau**, $D_\ell\propto\ell^2$ | 772 at $\ell\simeq247$ | 121 | **11.1** |
| $e^{-\kappa}$, (98)'s weighting (A-2, the release) | plateau flat to 30% | 3.17 at $\ell\simeq200$ | **11.5** | 2.31 |

**The visibility weighting has the envelope and no plateau. The opacity
weighting has the plateau and no envelope.** The $\mathcal V$ variant falls by a
factor of **seventy** from its peak; the $e^{-\kappa}$ variant rises by a factor
of four past its own.

**This reframes A-2.** A-2 recorded the opacity substitution as a departure
chosen to recover the Sachs–Wolfe plateau, with the plateau measured over
$2\le\ell\le200$ — and it is right about that, as the table confirms. What it
could not see, and what the $\ell=507$ ceiling of **T-17** guaranteed nobody
would see, is that the same substitution removes the high-$\ell$ envelope.
**It is not a choice between a better and a worse weighting. It is a choice
that cannot be made globally**, and the bundle has been making it globally.

The mechanism is a smearing mismatch and is consistent with everything measured:
the primary term is a **delta at $\eta_*$** and is never smeared; its
cancellation partner, the Doppler term, is weighted by $e^{-\kappa}$ and so is
spread over the whole post-decoupling history. At low $k$ the $j_\ell$
oscillation is slow and both survive; at high $k$ the spread partner averages
towards zero while the delta does not, **so the 16:1 cancellation of T-19 stops
being a cancellation**. Under $\mathcal V$ both partners are narrow, which is
why that variant keeps its envelope.

**Still not asserted as the whole cause.** Three causes have been named and
withdrawn; this one is a measured crossover and a mechanism consistent with it,
and the repair is not obvious — the two assignments that the mechanism suggests
have both been tried and both fail (T-19's falsified repairs (i) and (ii)).
What is now established is narrower and firmer: **the weighting cannot be a
single global choice, and the release's choice is the one that fails at high
$\ell$.**

## T-21 — the pipeline computes R and then passes zeros to the damping scale

```python
k_d = diffusion_scale(recombination, r_of_eta=recombination.kappa_prime * 0.0)
```

`diffusion_scale`'s own docstring carries $R$ in the integrand,
$[R^2+\tfrac45(1+R)]/(1+R)^2$, and `run` computes
`r = baryon_photon_ratio(a, omega_b_h2=omega_b_h2)` **two lines earlier**. The
call site then constructs an array of zeros out of `kappa_prime` and passes
that, with no comment saying why.

Measured: $R(\eta_*)=0.6125$, and

| | $k_D(\eta_*)$ | $\ell_D=k_D\Delta\eta$ |
|---|---|---|
| $R=0$, as called | 557.8 | **1783** |
| $R$ as the bundle computes it | 621.2 | **1985** |

**11%, and in the wrong direction** — including $R$ makes the damping weaker
still, against a standard $\ell_D\simeq1300$–1500 that both already overshoot by
a third. So this is not T-19's cause and fixing it does not help the envelope.

### CORRECTION, 2026-10-13, on the PI supplying Planck 2018 VI

**The paragraph above is wrong about the direction, and the error is this
stream's.** It compared against "a standard $\ell_D\simeq1300$–1500", which was
recalled rather than sourced and which conflates the $\ell$ where the damping
envelope becomes *visible* with $k_D\chi_*$. Planck 2018 VI Table 2 tabulates
$k_D$ and $\theta_*$ directly, and they give

$$\chi_*=r_*/\theta_*=13873\ \text{Mpc},\qquad \ell_D=k_D\chi_*=\mathbf{1954}$$

Against that number:

| | $\ell_D$ | vs Planck |
|---|---|---|
| $R$ passed as zeros, **as the code calls it** | 1783 | $-8.8\%$ |
| $R$ as the bundle computes it, **the fix** | **1985** | **$+1.6\%$** |

**So the fix lands the number and the defect is the thing costing 9%.** T-21
goes from "a defect that does not help" to "a defect whose correction brings the
Silk scale to 1.6% of Planck's". The conformal geometry is corroborated at the
same time: $\Delta\eta_*=3.1955\,c/H_0$ against Planck's
$\chi_*=3.1171\,c/H_0$, **+2.5%** at round-number parameters, which is why the
$\ell=k\Delta\eta$ comparisons throughout this record are meaningful at all.

**The lesson is the one T-16 taught in a different place.** A remembered
constant is not a measurement, and it reads like one. The comparison that
mattered took one table and the PI had to supply it. See
`provenance/COSMOLOGICAL-PARAMETERS-v1.md`.

It is recorded anyway, and as a defect rather than an approximation, because
**a quantity the code computes and then discards at one call site is not a
choice — it is a choice nobody made.** A-1 and A-2 are approximations: named,
reasoned, measured. `kappa_prime * 0.0` is an idiom for "zeros" written in terms
of an unrelated array, which is what a placeholder looks like when it survives.
The separate question of why $\ell_D$ overshoots the standard value by a third
is **open and is not this**.

## T-22 — the bundle is already half-Planck, and nothing says so

**Found 2026-10-13, on the PI's suggestion that the baseline move to current
best-fit parameters.** The suggestion is right, and the state it lands on is
sharper than it looks.

```python
CDM_MODEL  = Background(omega_m=1.0, omega_lambda=0.0, omega_r=0.0, h0=1.0)
LCDM_MODEL = Background(omega_m=0.3, omega_lambda=0.7, omega_r=0.0, h0=1.0)
```

against `omega_b_h2: float = 0.0224` appearing as a **bare default in eight
places** — `acoustic.py` twice, `decoupling.py` twice, `peebles.py`,
`diagnostic_d5_sachs_wolfe.py`, `emit_handover_fields.py`,
`test_frame_transform.py` — and `omega_gamma_h2: float = 2.47e-5` beside it.
**Neither is cited anywhere.** $\Omega_bh^2=0.0224$ is Planck's; $0.3/0.7$ are
round numbers; $\Omega_r$ is exactly zero.

So the recombination history is computed at a Planck baryon density inside a
background that is not Planck's and carries no radiation, and **the bundle whose
discipline is that every weight is cited to a published equation number has two
uncited empirical constants in its hot path.**

### Three separate problems, and only one of them is the PI's suggestion

1. **Uncitedness**, which is a defect now and independent of any parameter
   change. A constant with no source cannot be audited, and `tables/parameters`
   exists precisely to carry this.
2. **Internal inconsistency.** $\Omega_bh^2$ is only meaningful with an $h$, and
   the models carry $h_0=1$. $\Omega_b h^2 = 0.0224$ beside $\Omega_m=0.3$ is
   not one cosmology.
3. **$\Omega_r=0$ exactly**, while $R=3\rho_M/4\rho_R$ is computed from a photon
   density that is not zero. Radiation is omitted from the background geometry
   and retained in the baryon-photon ratio.

### Why this is probably not cosmetic

Two open discrepancies in this record are geometry-sensitive and both point the
same way: the first acoustic peak comes out at $\ell\simeq200$ against a
standard 220, and $\ell_D\simeq1783$ against a standard 1300–1500. Every
$\ell=k\Delta\eta$ depends on the conformal geometry, and $\Omega_r=0$ gets the
early-time part of it wrong. **Some fraction of what T-19 and T-20 are chasing
may be the parameter point rather than the assembly**, and that has to be
separated before either is closed. It does not explain a factor of eleven; it
may well explain ten per cent of a peak position.

### What is proposed, for v1.2.0 and beside the 5b work

- A **named, stamped** $\Lambda$CDM parameter set, with the release, table and
  column recorded in `provenance/`, on the `conventions-source.txt` mechanism.
  *Which* best fit is a real choice — TT+lowE and TT,TE,EE+lowE+lensing differ —
  so it is named, not "Planck".
- **The round-number $\Lambda$CDM is kept beside it**, because every released
  v1.0.0 and v1.1.0 $\Lambda$CDM figure used it and deleting it makes them
  irreproducible. Decision **S12**'s rule, applied to a cosmology.
- **`CDM_MODEL` does not change.** It is *Annals II* §8.3.2's own model — flat,
  matter dominated — and changing it stops reproducing the paper. The faithful
  model and the realistic one are different objects and the bundle carries both,
  as it already carries both weightings and both recombinations.
- $\Omega_r\ne0$ for the stamped set, and the cited constants cited.

**"No empirical data are required" stays true and should be said rather than
assumed.** A parameter point is not data: nothing here is fitted, no likelihood
is evaluated, and `CITATION.cff`'s sentence survives. But a bundle that carries
Planck's $\Omega_bh^2$ silently is one wording away from being wrong about
itself, which is the kind of thing this record exists for.

**Not yet actioned.** The exact column must come from the paper; web search is
unavailable in this session, so the values are the PI's to confirm.

## T-23 — mode-expanding a derivative is not differentiating a mode amplitude

**Found 2026-10-13, wiring (102) into the integral solution**, on the first
attempt to carry $u^a$ generic. It is the failure mode conventions row
**C3.1a** was written to predict, met in a different place from the one it
names.

The obvious way to assemble (102) is to build $C_0,C_1,C_2$ on the $\eta$ grid
and spline them for $C_1'$ and $C_2''$. **That is wrong, and not slightly.**
*Annals II* mode-expands $\mathcal D_{\langle a}\dot{\mathcal B}_{b\rangle}$
with the footnote to (105):

$$\mathcal D_{\langle a}\dot{\mathcal B}_{b\rangle}\approx
-\frac ak\big(\dot{\mathcal B}_1+2H\mathcal B_1\big)
\mathcal D_{\langle a}\mathcal D_{b\rangle}Q$$

The $2H\mathcal B_1$ comes from the $1/a$ inside $\tilde{\mathcal B}_1\approx
\frac ka(\delta\tilde T+\Phi_A)$ and is **invisible to a spline through the
stored amplitude**. Measured against (106), a plain conformal derivative of
$a\tilde{\mathcal B}_1$ is wrong by a **median of 100%** over
$\eta_*<\eta<0.8\eta_0$, worst 7.2, with the missing term worth **60% of the
whole**. Near last scattering the ratio is 0.70.

**This is why *Annals II* derives (106) rather than differentiating (105)**, and
the reason was not obvious until the derivative was needed generically.

### Consequence for the architecture

`integral_solution` takes `c1_prime` and `c2_second` as **supplied inputs**. It
does not differentiate, and will not: each $\mathcal B_A$ owes its own
mode-expanded derivative relation, and that relation is frame-specific because
the kinematic quantities are. `coefficients.newtonian_c1_prime` implements
(106)+(107) for the Newtonian frame; **a generic frame owes the same derivation
for $\mathcal B_0$ and $\mathcal B_2$, and that is the substance of v1.2.0's
covariant extension** --- not the wiring, which took an afternoon, but the three
derivative relations, which did not exist.

### The recovery, measured

With $\tilde C_1'$ from (106), (102) specialised to $\tilde\sigma_{ab}=0$
reproduces what `pipeline.run` has always computed:

| | worst relative difference |
|---|---|
| $C_1'$ by spline through the amplitude | **4.7** |
| $C_1'$ from (106) | **3.0e-2** |

The integrands are **analytically identical** --- expanding
$-\tilde C_1'=(\kappa'\tilde v_B)'+\tfrac1k(a\tilde{\mathcal B}_1)'$ gives
$(\kappa'\tilde v_B)'+(\Phi_A'-\Phi_H')-aH(\delta\tilde T+3\Phi_A)+\tfrac13k
\tilde\tau_1$, which is (178)+(179) term for term, including where (179)'s
$3\Phi_A$ comes from --- and the boundary terms likewise. The residual 3% is
not structural: the two routes differ by $1.2\times10^{-3}$ in the boundary
value at $\eta_*$ (the pipeline interpolates $S_P$ linearly where this splines
it, across a grid cell over which $S_P$ moves 28%), and **T-19's cancellation
amplifies sub-0.2% differences in the pieces into 3% in their residue**. The
largest discrepancies sit at exactly the $\ell$ where the total is smallest.

That amplification is itself the finding restated: a spectrum assembled as a
small difference of large terms converts every small error into a large one,
and this is the second independent place it has shown up.

---

## T-24 — the energy frame closed three ways against the field equations, on the wrong branch

**Found 2026-10-13, building the energy-frame coefficient set for F5.** Nothing
released was touched: the rank-two sector has never been evaluated. But the
defect would have **inverted the answer to the question F5 exists to ask**, and
it survived a check written in the same sitting and described, correctly, as the
bundle's first comparison of the frame machinery against the Einstein equations.

`energy_frame_shear` took

$$\sigma=+k_{\rm phys}v,\qquad E=+k_{\rm phys}^2\Phi_A .$$

Both signs are wrong. With $v$ as `energy_frame_shift` returns it --- the
velocity of the energy frame relative to the Newtonian one, which is what
`ThreadingShift.temperature_shift` independently fixes --- **n-t1** with
conventions row **C4.2** gives $\sigma=-k_{\rm phys}v$, and **C3.5** ($s_Q=-1$)
gives $\mathcal D_{\langle a}\mathcal D_{b\rangle}X=-k_{\rm phys}^2X$, hence
$E=-k_{\rm phys}^2\Phi_A$. `frames.py::weyl_electric_amplitude`, written for
criterion 2 long before this module existed, returns
$-\tfrac12(k/a)^2(\Phi_A-\Phi_H)$ --- the same thing, from a third direction.

### Why the closure could not see it

Write $\sigma=c\,k_{\rm phys}v$ and $E=e\,k_{\rm phys}^2\Phi_A$. The residual of
the three statements

1. $\sigma_{ab}=\mathcal D_{\langle a}v_{b\rangle}$,
2. $\dot\sigma=-2H\sigma-E$ (Appendix G, $A_a=0$),
3. $v'+\mathcal Hv=-k\Phi_A$ (the energy-frame Euler equation),

is $k^2(e-c)\Phi_A/a^2$. **It vanishes for every $c=e$.** The closure fixes the
*product* of the two rank-raising signs and never either one, so $c=e=+1$ closed
to $10^{-16}$ while disagreeing with the conventions sheet, with `frames.py` and
with the labelling in `frame_transform.py`. The function's own docstring had said
the closure fixes $c^2$ and that "the rank-one match against (106) fixes $c$
itself" --- and then the rank-one match was never run for this branch.

### What it would have cost

The rank-two contribution would have pointed the wrong way against everything
rank-one. The frame-invariance measurement would have returned a different
number with the same plausibility, and the figure drawn from it would have been
an argument for a conclusion produced by a sign.

### The fix

Both signs taken from the sheet. `tests/` now pins them **absolutely** ---
against `frames.py::weyl_electric_amplitude` and against **n-t1** --- and a
second test asserts that the three-way closure passes on *both* branches, so
that the degeneracy is recorded as a property of the check rather than
rediscovered.

**The lesson is not about a sign.** A check that compares two things it derived
from the same convention is a consistency check, and this one was described as
stronger than it was. Closure against the field equations is still worth having;
it is not worth trusting alone.

---

## T-25 — two arguments whose names differ by `_prime` are not derivatives of each other

**Found 2026-10-13, by the control in
`tests/test_coefficients.py::test_the_frame_shift_of_every_coefficient_is_the_closed_form_one`.**
Mine, found before it left the container, and recorded because the trap is still
in the module and will catch the next person.

`match_coefficients` takes `kappa_prime_v_b`, which is $\kappa'v_B$ as **(89)
prints it**. `newtonian_c1_prime` takes `kappa_prime_v_b_prime`, which is
$(\kappa'\tilde v_B)'$ --- the derivative of the quantity **(109)** carries,
$\tilde v_B=v_B/k$. The two differ by $k_{\rm com}$, and the names say they
differ by a derivative. The first draft of `energy_set` built the second with
the $k$ of the first.

| | at $k=60$ |
|---|---|
| $\Delta C_1,\Delta C_0,\Delta C_2,\Delta C_2''$ against their closed forms | $<10^{-15}$ |
| $\Delta C_1'$ against its closed form | **86** |
| (102) total, Newtonian vs energy | $+14.6$ vs $-973$ |

**The failure was invisible in four of five coefficients and in both frames
separately.** It showed up only in the *difference* between frames, because that
is where $C_1'$ stops being large and starts being a small shift of a large
number. Nothing in the Newtonian frame could have found it.

### The fix, and the trap

The two are now named `kappa_prime_v_b_E` and
`kappa_prime_v_b_tilde_prime_E` at the call site, with the normalisation in a
comment. More usefully, `CoefficientSet` now **carries the primitives of (89)**
--- $a\mathcal B_1$, $a\mathcal B_2$, $v_B$ and their derivatives, in the
printed normalisation --- so that a caller who needs them, as any
implementation of (98) or (101) does, does not reconstruct them by
re-multiplying by $k$ in the right places.

---

## T-26 — an exact relation, evaluated in a variable that cancels

**Found 2026-10-13, by the same control.** T-23 established that a derivative
must come from a published relation rather than from a spline. T-26 is the other
edge of that knife: **the published relation must also be evaluated in a
variable that does not cancel.**

$C_2''$ has two routes. Through the threading velocity it is $v''/k$ --- three
closed-form terms, since $a\mathcal B_2=a\sigma=-k_{\rm com}v$ exactly. Through
Appendix G it is $-(a\sigma)''/k^2$ with
$(a\sigma)''=a''\sigma+2a'\sigma'+a\sigma''$ and $\ddot\sigma$ from the Bianchi
propagation equation. They are the same number, and only one of them can be
computed:

| | magnitude |
|---|---|
| $\ddot\sigma$ on the grid | $3.6\times10^{15}$ |
| $C_2''$, the result | $1.7\times10^{-3}$ |
| digits of cancellation | **about eighteen** |

so the Appendix G route returns noise --- and returned it **silently**, as a
number of the right order with none of the right digits, because the
cancellation is almost complete rather than catastrophic in the obvious way.

### What this does and does not say about Appendix G

It says nothing against the relation. $\dot\sigma$ and $\ddot\sigma$ agree with
the Euler route to $5\times10^{-16}$ and $1.7\times10^{-5}$ respectively, where
nothing cancels; the **first** derivative $(a\sigma)'=a'\sigma+a^2\dot\sigma$
agrees with $-k v'$ to machine precision and `energy_set` now **raises** if it
does not. Only the second derivative is unusable in that grouping.

`energy_set` evaluates $C_2,C_2',C_2''$ through $v$ and keeps Appendix G as the
check. `tests/` pins the conditioning failure itself, so that reinstating
`c2_derivatives` in that position fails rather than quietly returning noise.

**Open:** the general fix is to propagate the natural rank-two variable
$a^2\sigma$, which is what Appendix G's printed second-order relation is
actually a statement about --- the scale-factor rule of
`provenance/GENERIC-SOURCE-DERIVATIVES-v1.md`, applied to the *evaluation* and
not only to the derivation. Not done; not needed while the frame in hand has a
closed form.

---

## T-27 — the dipole's frame shift was too large by $k_{\rm com}$

**Found 2026-10-13, in a released module.** `frame_transform.to_frame` shifted
$\tilde\tau_1$ and $\tilde v_B$ by $-v$. It is $-v/k$.

`ThreadingShift` holds two rank-one shifts and **one of them already had it
right**. `temperature_shift` returns $-\mathcal Hv/k$: the monopole carries the
$1/k$ because a scalar amplitude is $1/k_{\rm phys}$ times its gradient's, so
$\mathcal D_a\ln T\to\mathcal D_a\ln T-Hv_a$ becomes $\delta T\to\delta
T-\mathcal Hv/k$. The dipole is carried in the same covariant normalisation ---
$\tilde\tau_1=\tilde v_B=v_B/k$, which is exactly what makes **(109)** read
$-\tilde C_1=(\delta\tilde T+\Phi_A)+\kappa'\tilde v_B$ against the $\kappa'v_B$
**(89)** prints --- so GDE99 Eq. (37) $\tilde\tau_a=\tau_a-v_a$ reads
$\tilde\tau_1\to\tilde\tau_1-v/k$ here. Two rank-one objects in one dataclass,
one divided by $k$ and one not.

### The symptom, which needs no conventions

| $k_{\rm com}$ | $\max|\tilde\tau_1|$ | old shift $\max|v|$ | corrected $\max|v/k|$ | old ratio |
|---|---|---|---|---|
| 5 | 0.59 | 3.3 | 0.67 | 5.7 |
| 20 | 2.12 | 13.3 | 0.67 | 6.3 |
| 60 | 3.22 | 40.0 | 0.67 | 12.4 |
| 140 | 2.16 | 93.3 | 0.67 | 43.2 |
| 300 | 1.08 | 200.0 | 0.67 | **186** |

**A first-order frame change was 186 times the quantity it corrects**, and grew
without bound with $k$. Corrected, $|v/k|/|\tilde\tau_1|$ stays between 0.2 and
1.1 across the whole grid. That test is in `tests/` and needs no conventions
sheet at all.

### What it changes, and what it does not

It changes the frame-invariance measurement by one to two orders of magnitude
(see `provenance/FRAME-INVARIANCE-MEASUREMENT-v1.md`).

**It does not change T-14.** T-14's numbers move from the pinned 0.9--1.0 band to
1.0138, 1.0099, 1.0099 --- a 6% shift from a factor of $k_{\rm com}=50$ in the
dipole shift --- and the collapse is untouched, because T-14 is the **absence of
the shear sector** from (177)--(179) and not the size of the dipole shift. The
band has been widened and the re-measurement recorded in the test. A defect whose
cause has been correctly named survives the correction of a different defect;
that is the test of the naming, and T-14 passes it.

---

## T-24 — CORRECTED THE SAME DAY. The entry above states the finding backwards.

**The record above is wrong and is kept.** It says `energy_frame_shear` had two
signs wrong and that the conventions sheet fixes them. The first half is half
right and the second half is wrong, and the sequence matters more than the
conclusion, so neither is being edited out.

### What actually happened

I read the frame transformation rule as $\tilde\sigma_{ab}=\sigma_{ab}
+\mathcal D_{\langle a}v_{b\rangle}$. *Annals II* prints it, in **n-t1**, as

$$0\approx\sigma_{ab}-\mathcal D_{\langle a}v^N_{b\rangle}$$

with $n_a=u_a+v^N_a$ and $n^a$ the shear-free threading --- a **minus**, and
with the tilde on the *Newtonian* frame, not the energy one. I flipped
$\sigma$'s sign on the strength of the wrong rule, and flipped $E$'s on the
strength of C3.5, and the two flips cancelled in the closure, which is exactly
the degeneracy the entry above correctly identifies. **The check I wrote to
catch a sign error could not catch the sign error I then made in it.**

$\sigma=+k_{\rm phys}v$ was right all along, and is the one part of this that
needs no convention at all: n-t1 uses the raising sign once and $v=-v^N$ uses it
again, so whatever C4.2 carries, the shear comes out $+k_{\rm phys}v$. It has
been reverted.

### What the finding actually is

Write $\mathcal D_aX=\lambda k_{\rm phys}XQ_a$ for a scalar and $\mathcal
D_{\langle a}Q_{b\rangle}=rk_{\rm phys}Q_{ab}$. Then **n-t2** gives both the
Euler equation $v'+\mathcal Hv=-\lambda k\Phi_A$ and, through *Annals II*'s own
definition $\mathcal D_{\langle a}\tilde A_{b\rangle}\approx E_{ab}
-\tfrac12\pi_{ab}\Rightarrow\tilde A_a\approx\mathcal D_a\Phi_A$, the amplitude
$E=\lambda rk_{\rm phys}^2\Phi_A$. Substituting both into Appendix G's
$\dot\sigma+2H\sigma+E\approx0$ leaves

$$\boxed{\;\frac{2\lambda r k^2\Phi_A}{a^2}\;}$$

**which is zero for neither branch.** Three published relations --- n-t1, n-t2
and the Appendix G shear propagation equation --- do not close under any single
convention. Verified symbolically.

The bundle's closure passes to $10^{-16}$ because it takes the Euler equation
from $\lambda=+1$ and $E$ from $\lambda=-1$:

| | $\lambda$ |
|---|---|
| Euler equation as `frames.py` derives it, $v'+\mathcal Hv=-k\Phi_A$ | $+1$ |
| conventions row **C3.5**, $s_Q=-1$, with C4.1 | $+1$ |
| `frames.py::weyl_electric_amplitude` | $+1$ |
| *Annals II*'s printed mode expansion, $\Phi_{A|\alpha}=-k\Phi_AY_\alpha$ | $-1$ |
| `coefficients.py::energy_frame_shear` | $-1$ |

### What has been done, and what has not

`energy_frame_shear` keeps $\lambda=-1$, because that is the branch that closes
with the Euler equation the bundle already integrates, and the choice is now
**named in one place** instead of being distributed across three modules. Two
tests replace the ones the wrong entry added: one asserts that the closure holds
for *neither* single $\lambda$, and one asserts that
`weyl_electric_amplitude` and `energy_frame_shear` are exact negatives of each
other --- pinning the contradiction rather than papering over it.

**Not resolved, and raised.** Which $\lambda$ is right is the conventions
sheet's to settle, and `provenance/conventions.md` is a generated copy. C3.5 is
a **stipulation** --- the sheet says in terms that the sign *"is not fixed by
any source"* --- and this is now the second result that bears on it, after the
rank-one match against (106). The note in
`GENERIC-SOURCE-DERIVATIVES-v1.md` saying the closure "corroborates the
magnitude" is **withdrawn**: it corroborates nothing until $\lambda$ is single
valued, because it was passing on a mixture.

### The part of the original entry that stands

The degeneracy. A closure of the form $\dot\sigma=-2H\sigma-E$ against a frame
transformation fixes the *product* of the two rank-raising signs and never
either one, so it cannot be cited for either. That was right when it was written
for the wrong reason, and it is what let the wrong fix through.

**And the method lesson, which is the expensive one.** The wrong version of this
entry was written with a symbolic check, two independent in-repository
corroborations and a measured consequence. All three were real; the premise ---
one transformation rule, read from a summary rather than from the printed
equation --- was not. **Every piece of evidence downstream of an unchecked
premise corroborates the premise.** The printed n-t1 was forty lines from
material already read twice in this session.

---

## T-24 — RESOLVED. The closure is an identity; the error was in the antecedent.

Two entries above state T-24, the second correcting the first. **Both are
superseded**, and both are kept, because the sequence is the finding.

### What it is

Annals II's **(31)**, the general frame transformation
$\tilde\sigma_{ab}\approx\sigma_{ab}+\mathcal D_{\langle a}v_{b\rangle}$,
contradicts its own specialisation **(40)**. (31) is right --- see **B-13** in
`ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` for the three reasons. With (31):

$$\sigma=-k_{\rm phys}v,\qquad E=-k_{\rm phys}^2\Phi_A,\qquad
v'+\mathcal Hv=-k\Phi_A$$

all consistent with conventions rows **C3.5** ($s_Q=-1$) and **C4.2**, and with
`frames.py::weyl_electric_amplitude`, which is Annals II **(24)** and was
written for criterion 2 before `coefficients.py` existed. **Nothing in the
bundle's conventions needed changing.**

### What T-24 is now a finding about

The three-way closure --- frame transformation, Appendix G, Euler equation ---
**holds identically in both convention signs** once (31) replaces (40). That is
what it should do: it is a statement about physical fields, so a basis cannot
enter it.

Therefore the closure is **evidence for no convention at all**. The claim in
`GENERIC-SOURCE-DERIVATIVES-v1.md` that it *"corroborates the magnitude"* of
C3.5 stays withdrawn, now for the right reason: not because it was passing on a
mixture, but because an identity corroborates nothing. The rank-one match
against (106) remains the only thing in this bundle that constrains that sign.

And it explains the whole episode. A check that cannot fail is a check that
cannot catch a sign error made inside it --- which is exactly what happened,
twice, in opposite directions, in one day.

### The sequence, which is the part worth keeping

| | what I did | what was wrong |
|---|---|---|
| 1 | flipped $\sigma$ and $E$ on the strength of a transformation rule remembered from a summary | nothing, as it turns out --- the right answer, for a reason I could not have defended |
| 2 | reverted both on the strength of the **printed (40)** | trusted a specialisation over the general rule two pages earlier, which the paper itself derives it from |
| 3 | read (31)--(37), and (33) against (40) | --- |

Step 2 was *more* careful than step 1 --- it went to the printed source, which
is the rule. It was still wrong, because it went to the nearest printed source
rather than the one carrying the citation. **"Check the source" is not a
procedure until it says which source**, and in a paper that derives a
specialisation from a general rule, the general rule is the source and the
specialisation is a derived result that can carry a slip.

The PI's instruction --- *"the physics rules; Annals II is a template not the
physics"* --- is what resolved it, and it resolved it without any literature
search: the physics was the field-equation closure, and the arbiter was two
pages earlier in the same file.

### Pinned

- `test_T24_the_closure_is_an_identity_in_both_conventions` --- the closure
  holds for all four $(\lambda,r)$ combinations, so it can never again be cited
  as evidence for one.
- `test_B13_the_printed_n_t1_does_not_close_and_the_general_rule_does` --- the
  (40) residual is exactly $2E_{ab}$.
- `test_the_two_modules_now_agree_on_E_and_on_sigma` --- the two $E_{ab}$ in the
  repository are now the same number, checked against each other.

---

## T-28 — a new entry point ran only where PYTHONPATH was already set

**Found 2026-10-13, by the PI's first run**, which is the acceptance this
bundle's portability gate exists to anticipate and did not.

`scripts/measure_frame_invariance.py` was added as **D6** and imports
`functions.*` with no `sys.path` bootstrap. `python scripts/x.py` puts
`scripts/` on `sys.path`, not the repository root, so it raises
`ModuleNotFoundError` on every machine where `PYTHONPATH` is not already set
--- which is every machine but the one that wrote it. Here it was run as
`PYTHONPATH=. python3 scripts/...` and passed; on the PI's machine D6 died and
the run came back `NOT CLEAN`.

This is **T-15 in a new place** --- "the release route cannot pass on a second
machine" --- and the gate that was built for T-15 watched the adjacent thing:
it checks that an entry point anchors its *output* paths to `__file__`, which
this script did, and not that it can *import* at all.

**Fixed, and the gate widened.** `check_portability.py` now fails any
`scripts/` entry point that contains `from functions.` without `sys.path`, with
the reason in the message. The guard was checked by removing the bootstrap and
confirming it fires. The script now runs from outside the repository with no
environment set, which is the only form of this test worth running.

**The general lesson, which has now cost twice.** A convenience used while
developing --- `PYTHONPATH=.` here, a mounted project repository for
`sync_conventions` before it --- silently supplies something the shipped
artefact must supply itself. The gate can only catch what it is told to look
for, so every time one of these escapes, the gate gets the new case rather than
the author getting a resolution.

---

## T-29 — the bundle's frame label contradicts the paper it reproduces

**Found 2026-10-14**, from the PI's question *"what is the difference between
the energy frame and the CDM frame, sometimes these are used interchangeably"*
--- a question, not a bug report, and the honest answer is that this bundle is
one of the places using them interchangeably.

Decision **S8** says:

> The CDM *frame* is the **total-energy frame** $q_a=0$, the threading in which
> the cold dark matter is at rest, because CDM is pressureless and geodesic and
> carries no energy flux of its own.

**Paper 1 v1.1.0 says the opposite**, in terms:

> The *energy frame* is the threading in which the total energy flux vanishes,
> $q_a=0$; it and the CDM threading [...] are **separate stipulations**, and
> they agree only to $\approx$ [...]. Setting $q_a=0$ in a mixture gives
> $\rho_{\!_C}v^a_{\!_C}+\tfrac43\rho_{\!_R}v^a_{\!_R}+\ldots=0$, so the energy
> frame **tilts away from the CDM one by $O(\rho_{\!_R}/\rho_{\!_C})$** and the
> two coincide in the limit of matter domination.

S8's reason is the giveaway. *"CDM carries no energy flux of its own"* is true
and is about **CDM alone**; the frame condition is about the **total**, and in
the CDM rest frame the total flux is not zero because the baryons and the
photons are moving. A justification narrower than the claim it supports is how
this one survived eight days.

### No released number moves, and that is worth being precise about

`energy_frame_shift` integrates $v'+\mathcal Hv=-k\Phi_A$, which descends from
$\tilde A_a=0$ --- the **geodesic** condition, and geodesic is exactly what
makes a congruence the CDM's. **The frame this bundle computes is the CDM
threading**, which is the one Paper 1 uses throughout. The arithmetic has been
right since the module landed. The label has not.

A label is not a small thing in this project: **S8 itself exists because "CDM"
named both a model and a frame**, and **S13** exists because `λ` named three
things two rows apart. This is the third.

### The size of it, measured --- D7

`scripts/diagnostic_d7_frame_identification.py`, run in the harness so the
numbers cannot go stale:

| at $\eta_*$ | this release (EdS, $h=0.5$) | Planck 2018 VI Table 2 |
|---|---|---|
| $\rho_b/\rho_C$ | 0.090 | 0.186 |
| $\rho_R/\rho_C$ | 0.113 | 0.225 |
| full tilt parameter $(\rho_b+\tfrac43\rho_R)/\rho_C$ | **0.240** | **0.486** |

and as a fraction of the Newtonian-to-CDM threading velocity the bundle
integrates, the tilt runs from 8% at $k=5$ to **45% at $k=60$** and back to 17%
at $k=300$.

**So "they coincide in the limit of matter domination" is a limit this
calculation is not in**, at the one epoch the calculation is about. It improves
afterwards on both counts --- $\rho_R/\rho_C$ falls, and after decoupling the
baryons stop moving with the photons and start moving with the CDM, which
removes their share entirely.

### A note for P1-T, not a correction

Paper 1 names the smallness parameter as $\rho_R/\rho_C$. With tight coupling
$v_B=v_\gamma$, the baryons tilt the frame too --- they are not CDM and they
move with the photons --- so the parameter is
$(\rho_b+\tfrac43\rho_R)/\rho_C$, and the baryon share of it is **37%** at
$\eta_*$ in this release's background and 38% in the stamped Planck column.
Paper 1's bound is the radiation half of the real one. Raised rather than
edited: Paper 1 is P1-T's.

### Proposed, not done

**S8a** amends S8 to match Paper 1 and renames the frame in code and prose from
*energy* to *CDM*. S8 is a decision, so the amendment is the PI's. Until it is
taken, `Frame = "energy"` stays as it is rather than being changed under a
decision that still says otherwise --- changing a label while the record
justifying it says the opposite is how a project ends up with two of them.

### T-29, strengthened the same day: *Annals II* enumerates them as distinct

The PI: *"this is also in the early parts of Annals II"*. It is, and it is
stronger than Paper 1's paragraph, because the antecedent does not merely
distinguish the two --- it **lists them as separate items**, in §4.1 *Frame
Transformations and Gauge Fixing*, immediately after the general
transformations (31)--(37):

> While various choices of $\tilde u^a$ are available in a multi-fluid
> description of the early universe, there are **three particularly useful
> choices**.
>
> 1. **The energy frame**: $\tilde q_a=0$ [...]
> 2. **The zero acceleration frame (or CDM frame)**: $\tilde u_a=u^C_a\approx
>    u_a+v^C_a$. From the CDM velocity equation and (32) we then find
>    $\dot v^C_a+Hv^C_a+A_a\approx0\Rightarrow\tilde A_a\approx0$. This choice
>    is particularly useful in multi-species situations, as **this frame will be
>    geodesic right through tight-coupling, slow decoupling and into the
>    free-streaming era**.
> 3. **The Newtonian frame**: $\tilde\sigma_{ab}\approx0$ [...]

**Item 2 is what this bundle computes**, line for line: `energy_frame_shift`
integrates $v'+\mathcal Hv=-k\Phi_A$, which is $\dot v^C_a+Hv^C_a+A_a\approx0$
in mode form. It is labelled item 1.

Three things follow.

**The name already exists and it is not "energy".** *Annals II* calls it the
**zero acceleration frame, or CDM frame**. S8a should use the antecedent's own
name rather than invent one.

**The bundle's choice is the right one and for the printed reason.** *"Geodesic
right through tight-coupling, slow decoupling and into the free-streaming
era"* is exactly the property this calculation needs, and it is a property of
item 2 and not of item 1. The energy frame is recommended there for *two
coupled species*; this is a three-species problem crossing decoupling. So the
code picked correctly and documented it incorrectly.

**S8 contradicts the antecedent as well as the paper.** Three sources now say
the same thing --- *Annals II* §4.1's list, Paper 1 v1.1.0's paragraph, and
D7's measurement --- and one decision record says otherwise. That is no longer
a question of interpretation.

**And the pattern is the one T-24 recorded.** S8 was written from a
specialisation --- §4.1.2's *The Energy Frame*, where scalar perturbations are
treated and the two are used together --- rather than from the enumeration two
pages earlier that keeps them apart. The same shape as reading (40) instead of
(31): the nearest printed passage, not the one that defines the terms.

---

## T-30 — a released file asserted git state that nothing in the repository can see

**Found 2026-10-14**, by the PI running `git tag --list v1.1.0` and getting
`v1.1.0` back.

Over three messages this stream asserted that the v1.1.0 tag did not exist, then
that it was not placed, then wrote into `README.md` that *"the tag is placed at
the last commit whose content was v1.1.0"* --- a **plan written as an
observation**, in a released file. On the strength of the first assertion the
README was changed from *Released as v1.1.0* to *v1.1.0-rc* and the three
v1.1.0 rungs were demoted from S to R, then changed back.

**The tag existed throughout.** It is `c7516b6`, *"v1.1.0: Peebles
recombination, numerical frame specialisation, F6 and F8"* --- a purpose-made
release commit, placed by the PI, and placed **better** than the plan would
have: the plan was "the commit before the next thing landed", which is a
position inferred from what came after rather than a commit made to be the
release. `git merge-base --is-ancestor` returns 0, and the release zip built
from the tag contains **143 files with none of the v1.2.0 work in it** --- no
`coefficients.py`, no `integral_solution.py`, no F5, no D6, no D7.

### Why no test caught it

**Because no test could.** The container these tests run in has no access to the
repository the README describes. `tests/test_readme_artefacts.py` was written
the same day to stop exactly this class of drift, and it checks the README
against `figures/` and `scripts/run_all.py` --- **the tree**. It has no way to
reach git, so every statement about tag state was unguarded, and the one
statement that was false was in that unguarded class.

The README's line 371 had said the tag existed. It was right. This stream read
it as stale.

### The fix, and it is not a better guess

The README now carries **the commands instead of the answer**:

```
git tag --list v1.1.0
git log --oneline -1 v1.1.0
git merge-base --is-ancestor v1.1.0 HEAD; echo $?
```

and `test_the_readme_states_the_git_check_rather_than_its_answer` fails if they
are removed or if the old assertion returns. **A claim no check can reach is
replaced by the check.** That is the general rule this finding is for, and it
applies past git: anything about the state of a system this bundle cannot
inspect --- the PI's machine, an external code's gauge convention, a journal's
equation numbering --- belongs in the tree as a procedure, not as an answer.

### The pattern, third instance in three days

| | asserted from | the primary source, which was available |
|---|---|---|
| **T-24** | a transformation rule remembered from a summary | *Annals II* (31), two pages from material already read twice |
| **T-29** | S8's reason, which was about CDM alone | *Annals II* \S4.1's enumeration and Paper 1's own paragraph |
| **T-30** | an inference about what a tag must be | `git tag --list`, one command, on the PI's screen |

T-24 and T-29 were caught by controls this bundle had built. **T-30 was not,
because the thing it asserted was outside everything the bundle can measure.**
That is the distinction worth keeping: the controls work, and they only work
where they can reach. The remedy is not more care --- it is noticing when a
claim has left the region the controls cover, and converting it to a procedure
before it is written down.

---

## T-31 — F7's planned claim was false, and the reason is structural

**Found** building F7 for v1.2.0, by measuring before writing the caption.
**Status:** figure rewritten around the measurement; no released number moves.

`captions/FIGURE-PLAN-v1.0.0.md` specifies F7's lower panel as the difference
between the two frames "with the **dipole shown separately**, because the dipole
is where the frame lives and $\ell\ge2$ is where it does not". That is Annals II
(37), $\tilde\tau_a=\tau_a-v_a$, with $\tau_{A_\ell}$ unchanged for $\ell\ge2$,
and it is correct about the transformation.

**It is not correct about this calculation.** Measured, the dipole sits on the
same curve as every other multipole: 9.91% at $k=20$ against a median of 9.92%
over $\ell=2$–$400$; 3.92% against 3.88% at $k=60$; 4.29% against 3.44% at
$k=140$. Worst dipole/median ratio **1.25×**, not an order of magnitude.

*(First measured as 1.19x on the grid T-32 and T-34 later corrected. The
third decimal moved; the finding did not.)*

The cause is in (102), not in the arithmetic. (102) builds **every** multipole
from the same three $\ell$-independent coefficients $C_0,C_1,C_2$ projected with
$j_\ell$. A change of frame moves the $C_A$ and nothing else, so the frame
response it can produce is $\ell$-independent up to the differing $j_\ell$
weights of three lines. **(102) cannot distinguish "invariant at $\ell\ge2$"
from "invariant nowhere", because it has no mechanism for answering differently
at different $\ell$.**

This is the same observation `provenance/FRAME-INVARIANCE-MEASUREMENT-v1.md`
reports as a residual "living in the $C_A$", followed to its conclusion. The
dipole's special status is real and is not in this equation: (98) sets
$\tau_\ell(\eta_*)=0$ and $\tau_0=0$ and solves for the *generated* anisotropy,
while the observer's own dipole is not generated along the line of sight.

**What was nearly published.** The caption had been drafted from the plan before
the measurement existed. The figure now reports what it measured, and says so.

---

## T-32 — every v1.2.0 figure was drawn on a k grid that stops at the peak of the shear integrand

**Found** building F2, by sweeping $k_{\max}$ instead of trusting the grid.
**Status:** corrected; no released artefact moves. **Raised with the PI.**

F2's lower panel was about to publish "40% of $C_\ell$ at $\ell=600$". Before
writing it, two convergence tests were run and they disagreed:

| test | change | effect on the $\ell=600$ number |
|---|---|---|
| **sampling**: $dk=\pi/3 \to \pi/6$ | twice as dense | **0.02%** — the grid is dense enough |
| **range**: $k_{\max}=420\to700$ | longer | **−9.5 percentage points** |

The range test is the one that mattered, and the reason is written in this
bundle already. The diffusion scale is $k_D=871.4$, so at the top of the grid
the damping factor is

$$\exp[-(420/871.4)^2] = \mathbf{0.79},$$

i.e. **the grid stops essentially at the peak of the shear integrand rather than
past it.** The shear sector carries an extra factor of $k$ in the transfer
(`shear[i] = k * c2_star * damping_total * combination`), so with $n_s=1$ its
$k$-integrand goes as $k\,e^{-2(k/k_D)^2}$ and peaks at $k=k_D/2\simeq436$ —
beyond the grid's edge — while the scalar sector's has long since fallen. **The
rank-0/2 sectors need a tail that rank 1 does not.**

### This was predicted, by this bundle, during v1.0.0

Finding **T-16** renamed `k_truncation_is_negligible` to
`k_grid_reaches_damping_scale` and recorded it as *"a readiness test for
**v1.2.0**, not a convergence test for this release — the acoustic peaks and
Silk damping of v1.2.0 **do** need the cut-off."* That is exactly what has
happened. The gate was correct, it was written down, and it bound on schedule.

### What moves and what does not

**Nothing released moves.** F3 sets `CLAIMED_ELL_MAX = 20`, shades every $\ell$
beyond it, and reports the drop-top-10% sensitivity over the claimed range. The
v1.0.0/v1.1.0 claim lives near $k\simeq10$ on a grid running to 420, with four
decades of margin.

**What moves is every v1.2.0 figure drawn so far** — F2, F5 and F7, all on
`np.arange(0.05, 420.0, ...)`, all plotted to $\ell=400$–600, i.e. twenty to
thirty times past the range this bundle has established.

### The correction

$k_{\max}$ raised to where the bundle's own gate passes:
$\exp[-(k/k_D)^2]<10^{-2}$ requires $k_{\max}\gtrsim1870$. Measured convergence
of the $\ell=600$ cost along the way — 40.5% (420), 31.0% (700), 30.3% (1000),
29.2% (1400) — with the drop-top-10% sensitivity falling from $6.3\times10^{-3}$
to $1.1\times10^{-4}$ between 1000 and 1400.

Each affected figure now also **states the $\ell$ range it claims and shades
beyond it**, the way F3 already does, rather than drawing a curve into a region
whose convergence nothing has measured.

### The convergence test this bundle already had could not have caught it

`cl_truncation_sensitivity` drops the top 10% of the $k$ grid and recomputes.
It is the right idea and it is the test T-16 recommended over the damping gate.
Run alongside the sweep above, it reported:

| $k_{\max}$ | drop-top-10% | the $\ell=600$ answer | still moving by |
|---|---|---|---|
| 1000 | $6.3\times10^{-3}$ | 30.34% | — |
| 1400 | $1.1\times10^{-4}$ | 29.17% | **1.17 pp** |
| 1900 | $1.1\times10^{-6}$ | 28.69% | **0.48 pp** |

At $k_{\max}=1400$ it read $10^{-4}$ — four orders inside any tolerance anyone
would set — while the answer was still a percent and a half from converged.

**The reason is that it is an interior test.** Dropping the top 10% of a grid
that stops too early asks what the grid's own edge contributes; it cannot ask
what lies beyond the edge, because nothing beyond the edge was ever computed. It
shares its blind spot exactly with refining $dk$: both vary something *inside*
the domain, and the mass this integrand hides is *outside* it.

So the damping gate is not a weaker proxy for the sensitivity test, as T-16's
phrasing implied — **it is the only one of the two that looks outside the
grid**, and it is a statement about the integrand made before any quadrature. It
has to be run *with* the sensitivity test, not replaced by it. Both now run in
`scripts/figure_f2_truncation.py`, and the figure carries both numbers.

### The lesson, and it is not "test convergence"

Convergence was tested. **The wrong parameter was varied.** Refining $dk$ is the
reflex, it is cheap, and here it returned a clean 0.02% that would have been
quoted as evidence. A quadrature has two edges and only one of them is the
spacing; the other is where it stops, and for an integrand whose peak lies
outside the grid no amount of refinement inside the grid can see it. The guard
against this is not more care — it is varying the *limit* and the *resolution*
separately, and knowing which one the physics puts the mass at.

---

## T-33 — "frame" names two different objects in this bundle, and the code uses it for both

**Found** 2026-10-14, from the PI's enumeration. **Status:** recorded; the
mapping is proposed object by object, **not** applied by substitution.

The PI's table separates what is specified at an event from what is specified
throughout a region:

| Object | What is specified | Where |
|---|---|---|
| Instantaneous observer rest frame | a unit timelike vector $u^a(p)$ | at an event |
| Local orthonormal frame | a tetrad $e_{\hat\alpha}{}^a(p)$, $e_{\hat0}{}^a=u^a$ | at an event |
| Observer worldline | a timelike curve with tangent $u^a$ | along one history |
| **Threading** | a smooth timelike congruence $u^a(x)$ | throughout a region |
| Adapted orthonormal frame field | a tetrad field following the congruence | throughout that region |

This bundle uses rows one and four and calls both of them "frame". They are not
the same object and the difference is load-bearing here:

* $\tilde\sigma_{ab}=0$ and $\tilde A_a=0$ are conditions on a **congruence
  throughout a region**. Neither can be imposed "at the observer", which is why
  the Newtonian one is admissible only in restricted cases.
* The **dipole** is a statement about $u^a$ **at reception**. F7's two panels are
  exactly this pair held apart, and T-31 is what happens when the equation
  carrying the propagation has no mechanism for telling them apart.

Nothing in this bundle is a tetrad: every quantity is PSTF, built from $u^a$ and
$h_{ab}$, so rows two and five are named only to be set aside.

**It is a defect of naming, not of calculation.** Every object computed is the
congruence quantity, correctly. The supplement now carries the table and the
distinction; the call-site mapping goes to the PI before any identifier moves.

**Why not `sed`.** A blanket rename earlier in this session inverted the meaning
of diagnostic D7, whose subject is *the CDM threading measured against the CDM
frame* — the one place in the bundle where both senses appear in a single
sentence, and therefore precisely the place a substitution cannot see. The rule
that follows: **a rename that a regular expression can perform is a rename whose
exceptions nothing will catch.**

---

## T-34 — F7 sized its $\eta$ grid for $k=140$ and then integrated to $k=420$

**Found** 2026-10-14, reading F7 while fixing T-32. **Status:** corrected.
Unreleased work only.

`scripts/figure_f7_frames.py` opened with

```python
env = build_environment(float(K_PROBE[-1]))     # 140
...
for j, k in enumerate(K_COM):                   # runs to 420
```

`build_environment` derives the $\eta$ grid from the $k$ it is handed —
`n = required_n_eta(k_max, span)`, six samples per $j_\ell$ oscillation at
$k_{\max}$ — because $j_\ell(k(\eta_0-\eta))$ has period $\pi/k$ in $\eta$ and
the line-of-sight integral has to resolve it. Sized for 140 and used to 420, the
grid gave **two samples per oscillation at the band edge, below Nyquist.**

That is **T-3** again, in a new script: *"passed n_eta=1000, which gave 2.3
samples per $j_\ell$ oscillation at the band edge — below Nyquist — and the
aliased integrand returned a smooth, plausible spectrum of the wrong shape."*
The same number, 2, in the same place, for the same reason.

**What it touches.** F7's **upper** panel, which integrates over `K_COM`. Not the
lower panel, and therefore **not finding T-31**: the per-mode frame response is
evaluated only at `K_PROBE`, i.e. at $k\le140$, which is exactly what the grid
was sized for. T-31's measurement — worst dipole/median ratio 1.19x — stands as
measured.

**Fixed** to `build_environment(float(K_COM.max()))`, which is what F2 and F5
already did. With T-32 raising `K_COM.max()` to 1900 the discrepancy would have
been 13.6x rather than 3x, so this would have gone from a wrong figure to an
obviously wrong one — which is luck, not a process.

**The pattern.** T-3 was recorded, understood and written into `pipeline.run`,
which raises if the $\eta$ grid is too coarse for its $k$ grid. `build_environment`
is a second entry point to the same physics, written later for the two-frame
work, and **it has no such guard** — it trusts its caller to pass the right
$k_{\max}$. A check that lives in one of two parallel entry points protects the
one it lives in. The guard belongs in `build_environment` as well, and that is
open.

---

## T-35 — the PI's working tree had drifted 42 files from the harness output

**Found** 2026-10-14, preparing the write list for this session's commit.
**Status:** corrected by writing every differing file; the procedure is changed.

Each commit batch in this project has been assembled **from what this stream
remembered changing**: the scripts edited, the records appended, the figures
whose content was known to move. Everything else the harness regenerates was
assumed to come back byte-identical and therefore not worth writing.

That assumption is sound — regeneration *is* byte-identical, re-tested here:
`figure_f1_appendix_f.py` run twice in the same container gives the same SHA-256
for its PNG and its CSV, which is what `DETERMINISTIC_METADATA` and finding T-2
are for. **The assumption was applied to the wrong question.** Deterministic
regeneration means a file that has not changed comes back identical; it says
nothing about a file that *has* changed and was simply left off the list.

Measured by staging the PI's own `FILE-MANIFEST-SHA256.txt` and diffing it
against this container's:

| | |
|---|---|
| files differing in content | **34** |
| files present here and absent there | **8** |
| stale files present there and absent here | **4** — `f6-approximations-v1.0.0.*` and `f8-schematic-v1.0.0.*`, the mislabelled pair that `save_figure`'s version argument fixed |

Among the 34 were `figures/f1-appendix-f-v1.0.0.*`, `f3`, `f4`, `f6` and `f8`,
and four CSVs in `outputs/` — artefacts this stream had no reason to think had
moved, and which had moved anyway through changes upstream of them.

### Why nothing caught it

The bundle's drift gate is `make_manifests.py --check`, and it is correct. It
runs **on whichever tree it is pointed at**: here, where the tree is consistent
by construction, it passes trivially. The tree that could have failed it is the
PI's, and nothing in this stream's procedure put the two manifests side by side.
The check existed, the data existed, and the comparison was never made.

### The procedure, changed

**The write list is now computed, not recalled.** Before any commit batch:
stage the PI's `FILE-MANIFEST-SHA256.txt`, diff it against this container's, and
write every entry that differs or is missing — plus the manifests themselves, so
the tree is self-consistent when it lands. Files present there and absent here
are reported for deletion rather than left to accumulate.

This is **T-30's rule applied to a second system**: *anything about the state of
a system this bundle cannot inspect belongs in the tree as a procedure, not as
an answer.* T-30 was about git on the PI's machine. This is about the PI's
filesystem, and the answer this time was not an assertion but an omission —
which is the harder form, because an omission leaves nothing to check.

---

## T-36 — every PNG gains 5 770 bytes on the way to the PI's disk, and the bundle already survives it

**Found** 2026-10-14, hash-verifying the files written for T-35.
**Status:** measured and explained. **Nothing is broken, and that is the
finding.** No change made; a documentation change is proposed.

Verifying the 45 files written to the PI's machine, three sampled PNGs failed
and every text file, CSV and PDF passed. The three failures had **the same
byte delta**, which is not what corruption looks like:

| file | container | on disk | delta |
|---|---|---|---|
| `figures/f2-truncation-v1.2.0.png` | 458 800 | 464 570 | **+5 770** |
| `figures/f5-sources-v1.2.0.png` | 466 516 | 472 286 | **+5 770** |
| `figures/f7-frames-v1.2.0.png` | 380 560 | 386 330 | **+5 770** |

All three diverge at byte 35 — immediately after `IHDR`. Walking the chunk
lists:

```
container: IHDR tEXt pHYs IDAT*7 IEND
on disk  : IHDR caBX tEXt pHYs IDAT*7 IEND
                ^^^^ 5 758 bytes, +12 of chunk framing = 5 770
```

**`caBX` is a private ancillary PNG chunk inserted by the desktop application
on the write path.** It is a provenance stamp. It is applied to **PNG only**:
`f1`, `f8` and `d1-sign-control` show the same +5 770, while every `.pdf`, every
`.csv` and every `.py` and `.md` round-trips byte-identical. The pixels are
untouched — `IHDR`, `pHYs` and all seven `IDAT` chunks match exactly.

So **the PNGs in the git repository can never equal what the harness produces**,
on the PI's machine or anyone's, and that was already true of every PNG this
project has ever committed. It also explains the five PNGs in `figures/` that
T-35's diff reported as "content differs" with no change upstream of them: they
were never stale, they were stamped.

### Why nothing is broken

Because **T-15 already answered this**, two releases ago, for a different reason.
`make_manifests.py` splits the claim in two:

* **`PORTABLE-MANIFEST-SHA256.txt` binds.** It *excludes the renderings*
  entirely — `RENDERED_PREFIXES = ("figures/", "supplementary-materials/")`,
  `RENDERED_SUFFIXES = (".png", ".pdf")` — and canonicalises numerics to nine
  significant figures. It contains **zero** PNG entries. A mismatch there is
  release-blocking. **It is untouched by this.**
* **`FILE-MANIFEST-SHA256.txt` is a within-machine drift check**, reported by
  class, and only an `exact`-class mismatch blocks a release.
  `artefact_class` returns **`rendered`** for every one of these files.

The reason T-15 gave was fonts, freetype and TeX Live versions — *"a PNG that
differs in hinting carries no scientific difference."* A provenance chunk added
by an application the bundle never heard of is a different cause with exactly
the same shape, and the rule written for the first case covers the second
without amendment. **A gate drawn around the right category survives causes
nobody anticipated.**

### What is actually wrong, and it is a sentence

The PI will see nine `rendered`-class drift lines on every `--check`, for ever,
with no explanation anywhere in the bundle. An alarm that fires on every correct
run is the thing T-4 and T-16 are both about, and this is a third instance
arriving by a route neither of them covered.

**Proposed**, for the PI: one paragraph in the README's verification section and
one in the supplement saying that `figures/*.png` carry a tool-added provenance
chunk, that the pixels are identical, that **the PDF is the authoritative
artefact** of every figure, and that the binding check excludes renderings for
exactly this reason. No code change. The alternative — canonicalising PNGs by
stripping ancillary chunks — would make the drift line disappear, and would also
make the byte manifest stop reporting a real class of change for the sake of
tidiness. The bundle's own preference, stated at T-16, is to explain an alarm
rather than silence it.

---

## T-37 — the potentials have no $k$ in them, and criterion 5b cannot close until they do

**Found** 2026-10-14, building the comparison cosmology for criterion 5b.
**Status:** the background half is fixed. The driving half is **open**, and
fixing it would move figures the PI has just accepted. **Raised, not taken.**

### What was fixed

`CDM_MODEL` and `LCDM_MODEL` both carry $\Omega_r = 0$. *Annals II*'s \S8.3.2
standard CDM is Einstein--de Sitter and this bundle's $\Lambda$CDM extension kept
the same matter-only background. **A matter-only background has no equality**,
so no $z_{eq}$, no sound horizon that any external code would recognise, and a
first acoustic peak in the wrong place for reasons that have nothing to do with
the reconstruction.

`PLANCK_MODEL` now carries the stamped Planck column with a photon-only
radiation era, $\Omega_\gamma h^2$ **derived** from $T_{CMB}=2.7255$ K and the
physical constants rather than quoted. It reaches

$$z_{eq} = \Omega_m/\Omega_r - 1 = \mathbf{5756.0}$$

against CAMB's 5756.0 and CLASS's 5756.0, by an independent route. The released
models are untouched and nothing outside the 5b path refers to the new one.

### What is not fixed, and it is larger

`functions.spectra.potentials.potentials` returns

$$\Phi_A(\eta) = D(\eta)/a(\eta),$$

normalised at the first grid point. **There is no $k$ in it.** Every mode is
handed the same potential history, which is correct only for modes that stay
super-horizon through the whole integration in pure matter domination.

The acoustic peaks are *driven* by the potential. Without its $k$ dependence —
the radiation-era suppression, Meszaros — the peak **positions** can be right
while the peak **heights** at high $k$ are wrong by a large factor. Criterion
5b's gated band is $30 \le \ell < 1000$, which is exactly the peaks.

`functions/spectra/transfer.py` **already contains** `transfer_function` and
`shape_parameter`, with tests covering the CDM asymptote, the bend, and B-10's
divergence. **Nothing in `pipeline.py`, `sources.py` or `two_frame.py` calls
it.** The piece exists and is not connected.

### How large, measured rather than asserted

The $\eta$ grid starts at $z = 3000$ and $z_{eq} = 5756$, so

| | $\rho_r/\rho_m$ |
|---|---|
| grid start, $z=3000$ | **0.52** |
| last scattering, $z_*\simeq1115$ | **0.19** |

Radiation is half of matter where the integration begins and a fifth of it at
last scattering. $\Phi \propto D/a$ is a matter-era solution being used across a
range that is not matter-dominated at the accuracy the acoustic band needs.

### Why this is raised rather than taken

Wiring $T(k)$ into the per-mode potentials changes **the driving term**, so
$C_0$, $C_1$ and $C_2$ change, so **F2, F5 and F7 all move** — three figures
accepted the same day. That is not a silent fix, and the bundle's own rule is
that a correction which moves accepted artefacts is the PI's to see first.

**Proposed:** wire `transfer_function` into `coefficient_sets` behind an explicit
flag, default off; regenerate F2, F5 and F7 both ways; bring both sets of numbers
and let the PI choose which is v1.2.0's. The flag is removed once chosen, because
a physics switch left in the tree is a second bundle nobody runs.

**What 5b stands on meanwhile.** The reference half is complete and stamped:
both codes specialised to $N_{eff}=0$, no reionisation, no lensing, helium
explicit, both reporting $z_{eq}=5756.0$ and a first peak at $\ell=206$, with
their mutual difference measured per band — **0.125%, 0.370%, 0.223%**, the
middle one being the gate. The tolerance is a measurement, as S4b requires. What
is missing is the bundle's side of the comparison, and this is what it is
missing.

---

## T-38 — the portable manifest canonicalises by rounding to a string, and that cannot express what it means

**Found** 2026-10-14, from the first cross-platform `--check` on the PI's
machine. **Status:** measured. **The fix changes a released gate, so it is
raised, not taken.**

`make_manifests.py --check` on the PI's Windows machine, against a tree
generated in a Linux container:

```
FAIL  PORTABLE-MANIFEST-SHA256.txt does not match the tree
        changed  outputs/line-of-sight-field.csv            [numeric]
        changed  provenance/FRAME-INVARIANCE-MEASUREMENT-v1.md  [exact]
        ^ RELEASE-BLOCKING
```

**This is the measurement `SIGNIFICANT_FIGURES = 9` was waiting for** — its own
comment says *"the first value tried, and the PI's machine is the measurement:
if a run there fails at nine, the failure reports the real magnitude and this
comes down."* The magnitude, measured by parsing both trees' numbers and taking
the worst agreement in each file:

| file | worst agreement | worst pair |
|---|---|---|
| `outputs/f2-truncation.csv` | **12.19 s.f.** | — |
| `outputs/f5-sources.csv` | **10.58 s.f.** | — |
| `outputs/line-of-sight-field.csv` | **9.69 s.f.** | `-3.586227044579e-03` vs `-3.586227043840e-03` |
| `provenance/FRAME-INVARIANCE-MEASUREMENT-v1.md` | **1.27 s.f.** | `-2.7373e-91` vs `-2.8941e-91` |

### The first failure is not what it looks like, and lowering the cut will not fix it

`line-of-sight-field.csv` agrees to **9.69** significant figures and the gate is
set at **9**. It should pass. It fails because the canonicaliser **rounds to a
9-significant-figure string and hashes that**, and two numbers agreeing to 9.69
s.f. can still fall either side of a rounding boundary. Round-to-$N$ has
boundaries everywhere; the probability a pair agreeing to $s$ figures straddles
one is about $10^{N-s}$, so at $N=9$, $s=9.69$ it is roughly **20% per number**,
and the file has thousands.

**Lowering $N$ makes it rarer, never absent.** At $N=7$ it is about 0.2% per
number, which over $10^4$ numbers is still some twenty expected straddles. The
defect is not the value of $N$; it is that **a hash of a rounded string cannot
express "agrees to $N$ significant figures"** — hashing is exact equality, and
the claim is a tolerance.

### The second failure is a bound being printed as a value

`FRAME-INVARIANCE-MEASUREMENT-v1.md` disagrees at **1.27 s.f.**, on numbers of
order $10^{-91}$. Nothing is wrong: $-2.7\times10^{-91}$ and
$-2.9\times10^{-91}$ are the same statement, *zero to machine precision*, and no
significant-figure rule will ever reconcile their digits. D6 prints a residual
that is a **bound** as though it were a **value**.

This is the case the bundle already wrote down for `*-residuals.csv`: *"their
digits are not reproducible on any machine and never were... they leave the
binding manifest and are checked by what the bundle actually claims about them
instead."* D6's generated record is the same object and was not given the same
treatment --- and it sits in the `exact` class, which is the strictest one,
because it is a `.md`. **A generated record of computed numbers is not exact
text.**

### Proposed, for the PI

1. **The numeric gate compares parsed values, not hashed strings.** Keep the
   portable manifest as a fingerprint, but make the release-blocking check for
   `numeric` files *"every value agrees to $N$ significant figures"*, computed by
   comparison. That is the claim; hashing a rounded string is an approximation to
   it that fails at the boundaries.
2. **D6 prints bounds as bounds.** A residual below, say, $10^{-30}$ prints as
   `< 1e-30` rather than to four digits, and the record moves to the `numeric`
   class with the other generated artefacts.
3. **Manifests are seeded where the tree lives.** Writing this container's
   manifests onto the PI's machine guaranteed a mismatch, because their harness
   regenerates the artefacts with their own libraries. After taking a batch the
   PI runs `make_manifests.py` without `--check` to reseed from their own tree,
   and `--check` thereafter means what it says.

Point 3 is procedure and takes effect immediately. Points 1 and 2 change a
released check and a released record, so they wait.

### Not a defect

Two files named `figures/f2-truncation-v1.2.0-1.png` and
`figures/f7-frames-v1.2.0-1.png` appeared in the tree and were committed. They
are filesystem duplicates --- the `-1` suffix a Windows or sync layer appends on
a write collision --- not artefacts of anything. They are removed.

### T-38, carried out: part (2) done, and one of its premises was wrong

**The PI's order was (2) then (1), 2026-10-14.** Part (2) --- D6 printing bounds
as bounds --- is done. `RESIDUAL_FLOOR = 1e-12`, taken relative to the largest
transfer at the same $k$: above $\ell\simeq k\Delta\eta$ the Bessel projection
dies, and **13 of the table's 42 entries** sit below it, at magnitudes down to
$10^{-211}$. They now read `below floor` instead of four digits of libm noise,
which is what put numbers into a committed record that no two machines will ever
agree on.

**The premise that part (2) would also fix the record's headline was wrong, and
checking it is the only reason that is known.** The reasoning had been: the ratio
of two sub-floor numbers is an $O(1)$ quantity that looks like a result, several
such rows reported `rel` near 1.85, and the record's *worst relative difference*
was 1.859 --- so the headline was presumably being set by rows where both frames
return zero. Excluding **all** of them moves it to **1.853**. It was not. There
are modes where the two frames' transfers genuinely differ by more than 100%,
and that number is a measurement. The floor buys reproducibility of the file and
nothing else, which is still worth having and is less than was claimed for it.

### Part (1): lowering the significant-figure cut cannot work, and here is why

The obvious reading of `SIGNIFICANT_FIGURES = 9`'s own comment --- *"if a run
there fails at nine, this comes down"* --- is that the cut is too tight. It is
not. `outputs/line-of-sight-field.csv` agrees to **9.69** significant figures
against a gate of **9** and fails anyway, because the canonicaliser **rounds to a
9-figure string and hashes it**. Rounding has boundaries everywhere, and a pair
agreeing to $s$ figures straddles an $N$-figure boundary with probability about
$10^{N-s}$:

| cut $N$ | straddle probability per number | expected straddles in that file (~8 800 numbers) |
|---|---|---|
| 9 | $2\times10^{-1}$ | ~1 800 |
| 7 | $2\times10^{-3}$ | ~18 |
| 6 | $2\times10^{-4}$ | ~2 |
| 5 | $2\times10^{-5}$ | ~0.2 |

Lowering the cut makes failure rarer, never impossible, and buys that rarity by
throwing away precision the comparison should be keeping. **No deterministic map
from the reals to strings can implement a tolerance**: hashing tests exact
equality of the image, and the claim being made is *agreement to within
something*.

So part (1) is not a parameter change. The gate has to hold **both** value sets
to compare them, and a hash holds neither. Three shapes it could take, for the
PI:

1. **The drift gate moves inside `run_all.py --strict`**, which is the one place
   that has both: the artefact already in the tree and the one it has just
   regenerated. It compares values with a stated tolerance before overwriting.
   The manifests stay as fingerprints and stop being the numeric gate.
2. **A separate comparison against the release archive**, which the bundle
   already builds: `check_numeric_agreement.py` takes two trees and reports the
   worst significant-figure agreement per file. That is the claim, stated
   directly, and it is what a third party would actually run.
3. **Keep hashing, report rather than block.** Cheapest, and it weakens the only
   gate the bundle calls binding. Recorded for completeness; not recommended.

(1) and (2) are the same measurement from two directions and could share one
implementation. **Nothing is changed until the PI picks**, because `--check`'s
verdict is a released claim about what this bundle guarantees.

---

## T-39 — the polarisation back-reaction cannot be switched off in CAMB or CLASS, and the like-for-like move is on this side

**Asked by the PI**, 2026-10-14: *"can we turn the back-reaction and missing
polarisation off in CAMB/CLASS? so it is more like for like?"* **Status:**
tested, measured, and a proposal.

### It cannot, and this was tested rather than assumed

| knob | result |
|---|---|
| CLASS `l_max_pol_g = 6` | runs; moves the acoustic band **0.006%** |
| CLASS `l_max_pol_g = 4` | runs; moves it **0.043%**, the tail 0.345% |
| CLASS `l_max_pol_g = 2`, `1`, `0` | **fails** in `perturbations_solve` |
| CAMB `DoLateRadTruncation = False` | runs; moves the band **0.007%** — a numerical knob, not physics |
| CAMB, a switch for the feedback itself | **there is none** |

The polarisation feedback is **structural in both codes**, not an output option:
the Thomson collision term carries $\Pi=\Theta_2+E_0+E_2$, so it needs the
polarisation hierarchy to at least $\ell=2$, and that is exactly where CLASS
stops being able to run. Truncating the hierarchy from 10 to 4 is not the same
experiment --- it bounds the *depth*, which is worth 0.04%, not the *feedback*.

### The like-for-like move is on this side, and it is one coefficient

The back-reaction enters this bundle at exactly one place: the coefficient of
the $(1+R)^{-1}$ term in the diffusion damping, `diffusion_scale`. Measured on
`PLANCK_MODEL`, with $R=0$ as the bundle's convention has it:

| coefficient | value | $k_D(\eta_*)$ | ratio |
|---|---|---|---|
| *Annals II* (dif-damp), as printed | 4/5 | **619.9** | 1.000 |
| Hu & Sugiyama, no polarisation | 8/9 | 588.1 | 0.949 |
| with polarisation | 16/15 | **536.9** | **0.866** |

and what that is worth in the damping factor the sources carry:

| $k$ | $e^{-(k/k_D)^2}$ at 4/5 | at 16/15 |
|---|---|---|
| 200 | 0.901 | 0.870 |
| 400 | 0.660 | 0.574 |
| 800 | 0.189 | 0.109 |

**13.4% in $k_D$**, and tens of percent in $C_\ell$ across the acoustic band and
the tail. This is one of the dominant terms in criterion 5b's residual, and it
is now a number rather than a guess.

### The tension, which is real and is the PI's to resolve

Carrying 16/15 would make the comparison like for like. It would also stop
reproducing what *Annals II* prints, and **this bundle reproduces**. The two
pull opposite ways and no single default satisfies both.

**Proposed:** 4/5 stays the default, because it is the printed equation; 16/15
becomes a named option used by criterion 5b and nothing else; and the gap above
is reported as an itemised residual rather than absorbed. That is the shape of
`transfer_function` against `transfer_function_printed` for **B-10** --- with
one difference worth stating plainly: B-10's printed form is *wrong*, and this
one is not. It is a different physical model, and the paper is entitled to it.

### A question, not a finding

4/5 matches **neither** standard coefficient: not 8/9 unpolarised, not 16/15
polarised. That may be a convention --- how $R$ and the factor of 6 are
distributed differs between treatments --- or it may be something to check
against the printed equation. It is recorded as a question because asserting
from a remembered form is the **T-24** failure, and the printed page settles it.

---

## T-40 — three artefacts sit at R on a convention the tree still calls stipulated

**Found** 2026-10-14, answering *"how far are we from v1.2.0?"* from the tree
rather than from memory. **Status:** raised. The fix is a test, and it is cheap.

`provenance/RELEASE-STATUS-v1.md` ends with the rule it is built on:

> **Nothing sits at R with an unresolved convention beneath it.** That is the
> single rule that keeps F5 at P.

**That sentence is now false of the tree it describes.** F5 is at R. So are F2
and F7, and all three stand on the same place: `provenance/conventions.md` row
**C3.5**, the sign of a scalar's mode coefficient, which still reads

> **STIPULATED HERE: `s_Q = −1`**, because that is the existing usage.

C3.5 is also still listed as a **gate on v1.2.0** in the same file. So the
release status simultaneously names the convention as open, declares the rule
that nothing may sit at R above it, and lists three artefacts at R above it.

### What is actually known, and what is not

**Known.** Finding **T-24** established that the three-way closure is an
identity in $\lambda$ and $r$ --- it holds for *every* convention --- so it was
never evidence for this one, and
`test_T24_the_closure_is_an_identity_in_both_conventions` now says so in a form
that can never be misread as support again. That was a real result and it
*removed* a false justification; it did not supply a true one.

**Not known, in the tree.** The PI proposed a route that settles the sign with
no mode convention at all: *"the physical sign of CDM falling into a well fixes
$\lambda$"*. It was discussed and accepted in conversation. **It was never
written down.** There is no test, no row in the conventions sheet marked
resolved, and no entry in `DECISIONS`. Searching for `s_Q` finds it in
`coefficients.py`, this file, `GENERIC-SOURCE-DERIVATIVES`, `OPEN-QUESTIONS` and
the conventions sheet --- stipulated in every one.

This is **T-30's pattern in a new place**: a claim settled in conversation and
never converted into something the tree can check. The difference is that T-30's
claim was about git and this one is about physics that the bundle *can* check.

### The fix, which is a test and a negative control

Cold dark matter falls **into** a potential well. That fixes the sign of the
CDM velocity relative to $\Phi$ with no reference to any harmonic convention,
which is the whole point of the PI's route. Concretely:
`cdm_frame_shift(...).v` against `phi_a` for an overdensity has one admissible
sign, and the opposite stipulation of $s_Q$ must make the CDM climb out of the
well. **The control is the half that matters** --- S27's C rung requires a check
that can fail, and T-24 is the finding that exists because a closure which
cannot fail was cited as though it could.

Until that test exists, the honest statements are: C3.5 is **stipulated**, three
R-rung artefacts depend on it, and v1.2.0 cannot close on a rule its own status
file declares and breaks.

### T-40, closed: C3.5 was two questions under one name

Written 2026-10-14, at the PI's instruction to do this before 5b.

**$\lambda$ is fixed by physics**, which is the PI's own route finally in the
tree. The CDM frame solves $v'+\mathcal Hv=-k\Phi_A$, so **gravity does
positive work on the matter in the growing mode**: $v\cdot(-k\Phi_A)>0$ at
every epoch, for every $k$, and for either sign of the potential's amplitude.
$\lambda$ is the *rank-dependent* rescaling $Q_{A_\ell}\to\lambda^\ell
Q_{A_\ell}$, so it cannot cancel between a rank-0 potential and a rank-1
velocity --- which is exactly why their relative sign fixes it, with no harmonic
convention anywhere in the argument.
`test_c35_gravity_does_positive_work_on_the_cdm_which_fixes_lambda`.

**The control climbs out of the well.** The same quadrature with the Euler
sign reversed gives negative work everywhere. Without it this would be a test of
the integrator; **T-24** is the finding that exists because a closure which could
not fail was cited as though it could.
`test_c35_the_control_climbs_out_of_the_well`.

**$s_Q$ is fixed by nothing, and that is a result.** The scalar, its gradient
and its second gradient each carry exactly one factor of $s_Q$ --- $X=s_Q\sum
X^{(k)}Q$, $\mathrm D_aX=-s_Qk X^{(k)}Q_a$, $\mathrm D_{\langle a}\mathrm
D_{b\rangle}X=+s_Qk^2X^{(k)}Q_{ab}$ --- so it cancels from every ratio of them.
No physical statement can depend on it and therefore none can fix it.
Stipulating it is the correct treatment, and the sheet's own *"not fixed by any
source"* was right. Asserted symbolically in
`test_c35_s_q_cancels_from_every_ratio_and_so_no_physics_can_fix_it`.

**What this bundle cannot do.** `provenance/conventions.md` is **generated** by
`scripts/sync_conventions.py` from the project's normative sheet, which lives
outside this repository. Hand-editing the copy is precisely the drift that
script exists to prevent --- nine duplicates have already been deleted over it
--- so the copy will keep reading *STIPULATED HERE* until the PI changes the
source. The replacement wording has been sent. **The gap is visible rather than
silent**, which is the most a bundle can do about a file it does not own.

---

## T-41 — the two-frame path does not reproduce the Sachs–Wolfe plateau, and a one-mode test could not see it

**Found** 2026-10-14, by the first run of criterion 5b. **Status:** measured and
localised. **Release-blocking for F2, F5 and F7's low-$\ell$ claims.**

Criterion 5b's first run put this bundle against the stamped spectra and the
acoustic band came back at **137%**. Chasing that found something larger and
closer to home.

### The measurement

$D_\ell$ renormalised at $\ell=30$, standard CDM, transfer function off,
$n_s=1$ --- so nothing recent is implicated:

| $\ell$ | two-frame, Newtonian | two-frame, CDM | pipeline (F3, released) | CAMB |
|---|---|---|---|---|
| 2 | **0.012** | **0.008** | ~0.59 | **0.881** |
| 30 | 1.000 | 1.000 | 1.000 | 1.000 |
| rise $\ell=2\to30$ | **×80** | **×124** | **×1.7** | **×1.14** |

A Sachs--Wolfe plateau is **flat in $D_\ell$**. The pipeline's (176)/(186) route
gives one --- F3's released numbers run 1.000, 0.883, 0.916, 1.207 at
$\ell=2,5,10,20$, flat to twenty per cent and matching CAMB. **The two-frame
(102) route rises by a factor of eighty.**

### What it is not

* **Not the transfer function.** The rise is identical with `apply_transfer`
  off; T-37 is not implicated.
* **Not $n_s$, not the radiation era, not `PLANCK_MODEL`.** Present at $n_s=1$
  on `CDM_MODEL`, which is the released configuration.
* **Not a frame effect.** Both frames show it, and they differ from each other
  by only the 47% F5 already reports. Whatever this is, it is upstream of the
  frame choice.
* **Not the rank-0/2 sectors.** In the Newtonian frame those are identically
  zero --- (110) --- and rank 1 alone carries the whole of the rise.

### Why nothing caught it

`test_the_specialisation_recovers_what_the_pipeline_computes` asserts exactly
this equivalence and **passes**, at 5%. It runs at

```python
K = 60.0
ELLS = np.array([2, 5, 10, 50, 200])
```

**one mode.** The two paths do agree at $k=60$, across every $\ell$ it checks.
They agree there because $k=60$ is in the acoustic regime, where the
line-of-sight integrated terms contribute almost nothing; the integrated
sector's weight is at **low** $k$, and $\ell=2$ is built almost entirely from
it. So the test is blind by construction to the one place the paths can differ,
and its ℓ list reaching down to 2 gives the *appearance* of low-$\ell$ coverage
that the single $k$ takes away again.

**This is T-32's lesson in a second form.** There it was a quadrature refined in
the parameter whose variation could not see the defect. Here it is an
equivalence checked at the one mode where the suspect term is negligible. In
both, the check varied the wrong axis and returned a clean number.

### What it blocks

F2, F5 and F7 are all built on the two-frame path and all three are at **R**.
Their high-$\ell$ content is not in question --- the acoustic sector is where
the two paths agree --- but every low-$\ell$ number they report is. **F5's
headline frame disagreement of 47% at $\ell=2$ is a difference between two
spectra that are both wrong there**, and should not be quoted until this is
resolved.

### Next

The suspect is the integrated sector: (102)'s line-of-sight term against the
pipeline's `Weighting.STANDARD_ISW`. The experiment is the recovery test run
**across $k$** rather than at one mode --- $k$ from below 1 to a few hundred,
comparing the two transfers mode by mode --- which localises the disagreement in
$k$ before anything is changed. That test should exist whatever the outcome,
because its absence is the finding.

### T-41, corrected: the routes agree exactly. It is approximation A-2.

**The first diagnosis above was wrong on both counts and the experiment it
proposed is what proved it.** T-41 said the two-frame path "does not reproduce"
the pipeline and that the one-mode recovery test was "blind by construction".
Swept across $k$, the two routes agree to **$10^{-5}$ or better at every mode
from 0.3 to 300 and every $\ell$ down to 2**:

| $k$ | $\ell=2$ | $\ell=5$ | $\ell=10$ | $\ell=50$ | $\ell=200$ |
|---|---|---|---|---|---|
| 0.3 | 2.7e-07 | 3.8e-07 | 5.5e-07 | 5.3e-07 | 5.3e-07 |
| 10 | 2.7e-06 | 5.7e-06 | 1.4e-05 | 1.5e-05 | 8.1e-06 |
| 300 | 8.5e-06 | 2.1e-06 | 1.2e-05 | 7.2e-06 | 4.6e-05 |

(102) and (177)--(179) are the same calculation. The one-mode test at $k=60$ was
concealing nothing, and the accusation that it was blind was made from the
*shape* of a previous finding --- T-32, where a check had indeed been varied
along the wrong axis --- rather than from a measurement. **That is pattern
matching standing in for evidence, which is the T-24 failure wearing a
methodological hat.** It is recorded rather than quietly replaced because the
wrong diagnosis was written into this file and pushed.

### What it actually is

**Approximation A-2: the weight carried by the line-of-sight integral.**
`integral_solution`'s docstring has said so all along --- *"`weight` is
$\mathcal V$ as (102) prints it, or $e^{-\kappa}$ where a caller departs from
it --- approximation A-2, and finding T-20"*. The pipeline passes
$e^{-\kappa}$. **The two-frame path passes $\mathcal V$, faithfully reproducing
what (102) prints.** Measured, standard CDM, $n_s=1$, transfer off, $D_\ell$
renormalised at $\ell=2$:

| | rise $\ell=2\to30$ |
|---|---|
| two-frame, `weight` $=\mathcal V$, as (102) prints | **80.5×** |
| two-frame, `weight` $=e^{-\kappa}$ | **8.17×** |
| pipeline, F3, released | **1.70×** |
| CAMB | **1.14×** |

So the printed $\mathcal V$ confines the integrated sector to the
last-scattering surface and removes the late ISW, which is most of $\ell=2$.
**It costs a factor of ten.** T-20 measured the two weights against each other
and concluded they are *"each right in one regime and neither in both"*; it did
not measure them here, at low $\ell$, where the difference is an order of
magnitude and the regime is exactly where $\mathcal V$ is wrong.

### What is still open, and it is a factor of 4.8

Two-frame with $e^{-\kappa}$ gives 8.17×; the pipeline gives 1.70×. The routes
agree to $10^{-5}$ mode by mode, so **this residual is not in the integral
solution** --- it is in what feeds it: the $\eta$ grid, the $k$ grid, $n_s$, or
`Weighting.STANDARD_ISW` doing something beyond passing $e^{-\kappa}$. **Named
as open rather than attributed**, because the last attribution in this entry was
made from a resemblance and was wrong.

### What it blocks, unchanged

F2, F5 and F7 take the $\mathcal V$ branch. Their acoustic content is sound; the
low-$\ell$ numbers carry a documented approximation worth a factor of ten there,
and **F5's 47% frame disagreement at $\ell=2$ is a difference between two
spectra that both take it**. Whether these figures should take the printed
$\mathcal V$ --- which is what the bundle reproduces --- or $e^{-\kappa}$ ---
which is what makes them comparable with anything else --- is **S31's question
in a second place**, and it is the PI's.

`test_the_specialisation_recovers_the_pipeline_at_every_k_not_only_at_sixty`
now exists for all seven modes. It was worth writing whichever way the answer
went: an equivalence asserted at one point in a continuous parameter is not an
equivalence.

---

## T-42 — approximation A-2 was found, measured, documented and fixed on 2026-10-06, and the two-frame path reintroduced it eight days later

**Found** 2026-10-14, while writing up T-41. **Status:** default corrected;
A-2's measurement is now a test. **A residual remains and is open.**

T-41 reported, as a discovery, that weighting (102)'s line-of-sight integral
with $\mathcal V$ costs the Sachs--Wolfe plateau. It is not a discovery.
`provenance/SOURCE-APPROXIMATIONS-v1.md` has said so since **2026-10-06**, under
the heading *"A-2 --- the visibility weighting on the **Doppler** source
destroys the Sachs--Wolfe plateau"*, with this table:

| weighting on the integrated terms | $D_5$ | $D_{10}$ | $D_{20}$ |
|---|---|---|---|
| $\mathcal V$, as (178) prints it | 4.29 | 13.6 | **43.2** |
| $e^{-\kappa}$, as (98) prints it | 0.80 | 0.74 | **0.87** |

and the conclusion *"the first is $D_\ell\propto\ell^2$, which is $C_\ell\simeq$
constant --- **there is no Sachs--Wolfe plateau at all**"*. The record also
settles which form the bundle takes, and why it is not a departure from the
antecedent: **(98) is the antecedent's own pre-approximation form**, it prints
the two weights separately, and the visibility substitution enters only at
(102), described there as a slow-decoupling correction. **The bundle took (98).
`pipeline` has carried it ever since.**

**The two-frame path was written afterwards and passed `env.visibility`.** It
reintroduced, by default, the exact defect that had been found by computing the
spectrum, measured into a table, written up with its reasoning, and fixed in the
other path.

### Why it came back

**A-2's measurement lived in prose.** It was a table in a provenance file, and
nothing executed it. `pipeline` was corrected and the correction stuck there
because that is where the author was looking; a second path, written later by
the same stream, had nothing to trip over. **A record only a reader can check
does not survive a second code path** --- and the reader, eight days later, was
this stream, which did not re-read it.

That is the third assertion-from-resemblance in one day. T-41's first diagnosis
blamed a one-mode test from the *shape* of T-32; S32 set the default to
$\mathcal V$ reasoning *"the bundle reproduces"* without reading the record that
says the antecedent prints **two** forms and the bundle chose the earlier one;
and T-41 itself presented A-2 as new. **In each case the record existed and was
not read.** T-24's rule was *go to the primary source*; this is its sibling: **go
to your own record before claiming something is new.**

### What is fixed

`line_of_sight_weight` now defaults to `"opacity"`, matching `pipeline` and
A-2's resolution; `"printed"` reproduces (178) exactly and keeps the departure
visible and measurable. **`test_a2_the_two_frame_path_keeps_the_sachs_wolfe_plateau`
runs A-2's measurement**, with the printed weighting as the control that must
fail. Decision **S32** is corrected: it was never an open choice.

### What is not fixed, and is open

With the weight corrected the two-frame path gives $D_\ell/D_2$ = 1.00, 1.36,
2.31, **5.01** at $\ell=2,5,10,20$, against the pipeline's 0.80, 0.74, **0.87**.
A **residual factor of about six** survives --- the same 4.8 T-41 named and did
not attribute. The two routes agree to $10^{-5}$ mode by mode, so it is in what
feeds them, not in the integral solution. The test asserts only that the default
is not $\ell^2$; **it does not assert a recovered plateau, because there is not
one**, and asserting flatness to make a test look better would be the failure
this entry is about.

### T-42, withdrawn and replaced: (102) must carry the visibility, and the inversion broke three figures

**Written 2026-10-14, unattended, within the hour of the entry above.**

**T-42 as written is wrong, and acting on it inverted the physics.** It read
A-2's heading --- *"the visibility weighting on the Doppler source destroys the
Sachs--Wolfe plateau"* --- and concluded that the two-frame path had
reintroduced a fixed defect by passing $\mathcal V$. It had not. A-2's own last
paragraph says where its argument stops:

> **(98) is the antecedent's own pre-approximation form**, and it prints the two
> weights separately [...] **The visibility substitution enters at (102),
> described as a slow-decoupling correction.**

So A-2 is about the pipeline's (177)--(179), where the weight is a free choice
and $e^{-\kappa}$ is the one this bundle takes. **(102) is the form in which the
$\mathcal V$ substitution has already been made.** Substituting $e^{-\kappa}$
into its bracket is not a weighting choice; it is using the wrong equation.

**Measured, immediately after making the change:**

| `line_of_sight_weight` | rank-0/2 share of $C_\ell$, $2\le\ell\le20$ |
|---|---|
| `"printed"` ($\mathcal V$, as (102) is derived with) | **0.47–0.62%** |
| `"opacity"` ($e^{-\kappa}$, substituted in) | **99.3–99.7%** |

The rank-1 sector --- the one (110) says carries **everything** in the Newtonian
frame --- carried nothing. F2 reported a truncation cost of 99.95%, F5 reported
the two frames agreeing to 0%, and F7's frame difference went to unity at every
$\ell$. **Three figures were regenerated wrong before the numbers were read.**

**Reverted.** `line_of_sight_weight` defaults to `"printed"` again, which is
what it was before this hour. Decision **S32a** is withdrawn; **S32 stands as
first written**. The test is inverted to guard the thing that actually breaks:
`test_102_must_carry_the_visibility_and_substituting_the_opacity_wrecks_it`,
with the 99.5% signature as its control.

### And T-41's framing is wrong too, for the same reason

T-41 presented the two-frame path's missing Sachs--Wolfe plateau as a defect
with an open residual. **It is not a defect.** (102) carries $\mathcal V$ by
derivation, A-1 and A-2 record that this *cannot* carry a late integrated
Sachs--Wolfe term and gives $D_\ell\propto\ell^2$ in standard CDM, and the
pipeline differs because (177)--(179) admit a weight that (102) has already
spent. **The two paths implement two different approximations of the same
physics, and the bundle documents both.** The "residual factor of 4.8" is not a
residual: it is the distance between two approximations, and the only thing
missing is that nobody had put a number on it at low $\ell$ before today.

### The pattern, fourth instance in one day, and this one did damage

T-41's first diagnosis blamed a one-mode test from the shape of T-32. S32 set a
default from *"the bundle reproduces"* without reading what the bundle had
decided. T-42 called A-2 a rediscovery, having read its heading and not its last
paragraph. **This one changed a default, regenerated three released-candidate
figures, and would have shipped them if the output had not been read.**

The common form is now unmistakable: **a conclusion reached from the shape of a
neighbouring result, written down with the confidence of a measurement.** T-24's
rule was *go to the primary source*. Its sibling, earned four times over today:
**read the record to its end, and when a change moves a default, look at what it
produced before believing it.** The figures were regenerated and *then* read,
which is the only reason this is a finding rather than a release.

---

## T-43 — 16/15 is not a departure from *Annals II*. It is *Annals II*'s own corrected equation.

**Found** 2026-10-15, during a workspace audit, by reading `cbrII.tex` --- which
had been sitting in this session's scratch directory since 2026-10-06.
**Status:** corrected. **Decision S31's central premise is withdrawn.**

T-39 recorded a question: *Annals II*'s (dif-damp) prints a quadrupole
coefficient of **4/5**, which matches neither Hu \& Sugiyama's unpolarised
**8/9** nor the polarised **16/15**, and the printed page would settle it.
S31 then adopted 16/15 for criterion 5b and framed it as a **tension**: *"it
would also stop reproducing what Annals II prints, and this bundle
reproduces."*

**There is no tension. The paper prints both.** `cbrII.tex` line 2624 gives
(dif-damp) as the tight-coupling result, and twenty lines later:

> This derivation can be easily corrected to include the effect of anisotropic
> scattering (which breaks the tight-coupling approximation) and polarization.
> [...] We follow the approach of Kaiser [...] and include the correction $f_2$
> to find the modified damping factor:
> $$\gamma^* \approx k^2\Big(\tfrac{\kappa'^{-1}}{6}\Big)
>   \Big[\tfrac{R^2+\tfrac45 f_2^{-1}(1+R)}{(1+R)^2}\Big]$$
> where, first, for the anisotropic effect, $f_2=\tfrac{9}{10}$, and second, to
> compensate for the polarization, $f_2=\tfrac34$.

So the coefficient is $\tfrac45 f_2^{-1}$ and **the paper supplies the values**:

| $f_2$ | $\tfrac45 f_2^{-1}$ | |
|---|---|---|
| 1 | **4/5** | (dif-damp), tight coupling |
| 9/10 | **8/9** | anisotropic scattering |
| 3/4 | **16/15** | polarisation |

**All three numbers measured in T-39 are *Annals II*'s**, reached through one
parameter the paper names. The bundle had implemented 4/5 as a bare constant and
so could not express the other two without appearing to leave the page.

### And the paper's own downstream use is the corrected one

\S*The Visibility Function* defines the damping envelope as *"now including
diffusion damping, which will be derived from the coupled baryon-photon
equations in (\ref{dif-damp-correct})"* --- the **corrected** equation, cited by
label. The form the paper carries forward is $\gamma^*$, not $\gamma$.

**Whether the two $f_2$ compose is not settled here.** *"first... and second..."*
can be read as two successive corrections, $f_2=\tfrac{9}{10}\cdot\tfrac34$, or
as two separate cases. The sentence does not disambiguate and **this entry does
not guess** --- which is the whole lesson of the four preceding days.
`F2_DEFAULT` is therefore left at tight coupling, so no released number moves,
and the choice is named in one place for the PI rather than buried in a call
site.

### What is carried now

`quadrupole_from_f2(f_2)` returns $\tfrac45 f_2^{-1}$, with
`F2_TIGHT_COUPLING`, `F2_ANISOTROPIC` and `F2_POLARISED` taking the paper's
values. `ANNALS_II_QUADRUPOLE` and `POLARISED_QUADRUPOLE` remain as the two
numbers already in use, now documented as $f_2=1$ and $f_2=3/4$ rather than as a
printed value and a departure from it.

### The lesson, and it is the fifth in five days

**The source was in this session's scratch directory the whole time.** T-39
wrote *"the printed page settles it, not a remembered form"* and then did not
open the page that was already on disk. The four errors before it were
assertions from resemblance; this one is the same failure in its laziest form
--- **a question recorded as open while its answer sat unread two directories
away.** `scratchpad/annals/cbrII.tex` is the antecedent's source. Open it.

---

## T-44 — the new gate printed PASS on a number it never measured

**Found 2026-10-15, by reading its own first output.** Criterion 5b's gate
(decision **S4c**) reduces a table of fractional differences and compares the
worst against a threshold. The first version did it with `np.max` over an array
containing `nan`, got `nan`, and printed:

```
PASS  criterion 5b's gate: nan < 1.0e-03
```

`nan >= GATE` is `False` in IEEE 754, so the failure branch was unreachable
whenever any entry was undefined. **The gate could not fail.** It had been
written minutes earlier, in a script whose docstring argues that a criterion
which can only be failed is not a criterion; this is the same sentence read from
the other end.

### Where the `nan` came from, which is the more useful half

Below its turning point $x\simeq\ell$ the spherical Bessel function is
exponentially suppressed, so $\Delta_\ell(k)$ at $k(\eta_0-\eta_*)\ll\ell$ is
numerically zero --- this bundle returns $5\times10^{-61}$ at $\ell=50,k=0.3$
and exactly $0$ at $\ell=600$. A *pointwise* fractional difference there divides
zero by zero. Fifty of 162 pairs in the first sweep were in that state.

### What is carried now, and it is not a `nan` filter

The metric is **normalised by the largest $|\Delta_\ell(k)|$ the mode produces**
rather than pointwise, which removes the undefined entries by making the
quantity the right one rather than by excluding the wrong ones --- see
`functions/spectra/two_route.py`. The second reason for that choice is in
**T-46**. The explicit `np.isfinite` refusal stays anyway: a reduction that can
return `nan` must not be the thing a release depends on, whether or not anything
currently feeds it one.

### The lesson

**A gate is not tested by the run that passes.** Three of this bundle's findings
are now gates that could not fail --- T-4 (ordered so it blocked its own
remedy), T-30 (asserted state nothing could see), and this one. The cheap
discipline is to make a gate fail on purpose once before trusting it, and the
cheaper one is to write the failure branch so that *anything other than a
measured number under the threshold* takes it.

---

## T-45 — the two-route agreement was measured on a grid that hid it

**Found 2026-10-15, while setting criterion 5b's tolerance.** The claim that
(102) and (177)--(179) *"agree to $10^{-5}$ mode by mode"* had been in a test
docstring since T-41 and was about to go into a release criterion. It was taken
from a comparison with two defects, both in the harness rather than in the
physics.

**First, a fixed $\eta$ grid.** `_both_routes` built `np.linspace(..., 4000)` at
every $k$. `required_n_eta` exists in this bundle precisely so that nothing does
that, and asks for 7 422 points at $k=600$. The consequence is not that the
answer was slightly coarse: at $k=60$ **both routes are still converging at 4000
points and are un-converged in the same direction**, so they agreed to
$1.1\times10^{-7}$ --- two hundred times better than the converged difference.
Refining to 8 000 made the reported agreement *worse*, and refining again made
it better: non-monotone, which is the signature of aliasing and not of
convergence. **The best number this comparison ever produced was its least
trustworthy.**

**Second, a frozen acoustic tail.** The oscillator was solved on
$\eta\le6\eta_*$ and held at its last value after. The height of that step is
whatever the oscillator was doing at the last grid point inside the window, so
it *moves with the grid*; and the two routes carry the frozen tail through
different groupings, so it does not cancel between them. It cost a factor of
three at $k=60$.

### What is carried now

`functions/spectra/two_route.py` derives $n_\eta$ from $k$ at **48 samples per
oscillation** --- four times the $C_\ell$ route's twelve, because this
comparison measures *the difference between two quadrature errors*, which does
not average the way either error alone does --- on a floor of 8 000, and solves
the acoustic equation over the whole span. One definition, used by both the test
and `scripts/diagnostic_d8_criterion_5b_gate.py`.

### The claim, now measured

$9.5\times10^{-6}$ worst and $2.7\times10^{-8}$ median, over three backgrounds,
nine modes from $k=0.3$ to 600 and six multipoles from 2 to 600. **The remembered
figure was right.** That is worth stating plainly and so is the rest of it: it
was right by luck, it was quoted four times before it was measured, and the
measurement needed T-46 as well.

---

## T-46 — the primary source at $\eta_*$ is read by linear interpolation, and the recombination grid is what limits it

**Found 2026-10-15, as the residue of T-45.** With the grid repaired, the two
routes still differed by $1\times10^{-4}$ to $3\times10^{-3}$, flat in the grid.
Decomposed by term, the line-of-sight integrals agreed to $10^{-7}$ and
**the entire difference sat in the one boundary term at $\eta_*$**.

`functions/spectra/pipeline.py` line 342 reads it as

```python
np.interp(eta_star, eta, source_primary(history, scattering, damping_total=damping))
```

and `integral_solution` reads the same quantity as `CubicSpline(eta, c_1)(eta_star)`.
On one grid the two arrays are pointwise identical --- checked:
$(-c_1^*)\cdot\mathcal D$ and the cubic evaluation of `source_primary` agree to
all printed digits --- so **the difference is the interpolant and nothing else**.
It is $1.3\times10^{-2}$ out of a source of 118, a relative
$1.1\times10^{-4}$.

**Refining $\eta$ sixteen-fold barely moved it** ($1.33\times10^{-2}\to
1.23\times10^{-2}$), which is what makes the second half of this entry the
important one.

### The binding grid is the recombination history's, and nothing guards it

$\kappa'$, the visibility and the opacity are `np.interp`-ed onto the
line-of-sight grid from `RecombinationHistory`'s own, which carries
`n_eta=4000` by default --- spacing $4.9\times10^{-4}$, **coarser than the
line-of-sight grid it is interpolated onto**. The result is piecewise-linear
with kinks at every recombination node, and a cubic spline through it does not
reproduce a cubic. Refining the *recombination* grid is what removes the
disagreement: the gap falls $1.33\times10^{-2}\to2.18\times10^{-3}\to0$ for
`n_eta` 4 000, 8 000, 16 000.

**And the value itself has not converged.** Measured on Einstein--de Sitter at
$k=30$, the primary source at $\eta_*$ runs

| `RecombinationHistory` `n_eta` | 4 000 | 8 000 | 16 000 | 32 000 | 64 000 |
|---|---|---|---|---|---|
| source at $\eta_*$ | $-118.321$ | $-118.415$ | $-118.469$ | $-118.499$ | $-119.788$ |

a **1.2% drift**, which is four times criterion 5a's measured 0.26% and the same
order as the acoustic-band differences the bundle reports against CAMB and
CLASS. `required_n_eta` derives the line-of-sight grid from $k_{\max}$ and
raises; **nothing derives or guards the recombination grid**, and it is the one
that sets the primary term.

### What this entry does and does not do

**It does not change a number.** The interpolant is left as it is and the
recombination default is left at 4 000, because moving either moves every
generated figure, table and manifest in the release, at the $10^{-4}$ level for
the first and the $10^{-2}$ level for the second. That is the PI's call and it
is raised as **Q7**, not taken here.

**It does change what criterion 5b's gate compares.** `two_route_transfer`
matches the interpolants, so the gate measures the assembly algebra --- which is
what it is for --- and reports the as-shipped difference beside it rather than
inside it. Both numbers are printed by D8 on every harness run.

### The lesson, and it is T-3's with the subject changed

**T-3 was a coarsened grid returning a smooth, plausible spectrum 575% wrong
while two routes agreed to $10^{-16}$.** The guard built in answer to it,
`required_n_eta`, watches the grid T-3 happened to be about. This finding is the
same failure one grid to the left: the two routes again agree, again share the
under-resolved input, and again cannot see it --- *a comparison that holds an
input fixed cannot check that input*. That sentence was written into
`functions/spectra/two_route.py` as a caution before this was found. It is now
an example.


---

## T-46 — ANSWERED the same day. Decision S33: derive the grid, after the tag.

The entry above closes with *"That is the PI's call and it is raised as **Q7**,
not taken here."* It was taken, 2026-10-15:

> *"I agree: my recommendation is to derive the grid, immediately after the
> v1.2.0 tag, not before it. This makes sense and makes the staging
> worthwhile."*

**Option (1) of the three costed in Q7**, staged after the tag. The reasoning
and the five acceptance conditions are **S33**; this entry records only what it
means for the finding.

**Nothing in v1.2.0 changes.** The interpolant stays linear in `pipeline.run`,
the recombination default stays at 4 000, every generated number stands, and
v1.2.0 ships the 1.2% as a **stated limit** in the release notes and the
supplement — the treatment **O1** and **O2** already have. A measured bound
declared in the release is a different object from one found in it afterwards,
and the distinction is the whole value of having measured it before the freeze
rather than after.

**What will check the fix, which is not what checks the bundle.** Criterion 5b's
gate reads $9.5\times10^{-6}$ before and after, because both routes share the
recombination history — the thing S4c says in advance that a self-comparison
cannot do. Internally the instrument is convergence under refinement.
Externally it is the **CAMB/CLASS comparison**, because a grid change moves
$z_*$, the visibility width, the damping scale and the peak positions, and
those survive the shape renormalisation at $\ell=30$ that a uniform amplitude
change would not. The comparison S4c demoted from gate to context is the only
thing in this bundle that can watch Q7's fix land, which is worth stating
plainly: **context is not decoration.**

`tests/test_two_route.py::test_the_interpolant_at_eta_star_is_what_T46_says_it_is`
is written to **fail** when the interpolant is matched. That is deliberate and
it is this entry's enforcement: the change cannot land quietly.

---

## T-47 — two deferrals outlived the release they were deferred to, and the fix for that had already been built

**Found by Coordination, 2026-10-15, reading the README.** `D3` and `D4` were
listed as *"deferred to v1.1.0 (S-b)"*. **v1.1.0 was tagged on 2026-10-12
without them.** For three days the harness, the README and the release record
all announced a deferral to a release that had already happened.

### Why this one stings

The `DEFERRED` dict in `scripts/run_all.py` exists **because of this class**.
Its own comment says so:

> *A single frozenset was wrong once S21 and S23 split the destinations: the
> harness went on printing "deferred to v1.1.0" for F2, F5 and F7 after they had
> been moved to v1.2.0 … The version is data now, so the message cannot drift
> from the decision.*

That fix was correct and it was not enough. Storing the version as data stops
the message from contradicting the **decision**; nothing stopped the decision
itself from going out of date. **An accurate label and a current label are
different properties, and T-16's fix only bought the first.**

### What is carried now

`check_deferrals()` reads the released versions out of `CHANGELOG.md` — a dated
`## [1.1.0] — 2026-10-12` is released, `## [Unreleased]` is not — and
**fails the harness** on any deferral whose target has shipped. It reads the
changelog rather than git tags deliberately: a reader reproducing this from a
downloaded zip has no `.git`, and a gate that answers differently for them is
not a gate. That is `_bundle_files`' argument applied again.

`tests/test_grid_register.py::test_the_stale_deferral_gate_can_fail` makes it
fail on purpose, because **T-44** is the finding that a gate is not tested by
the run that passes.

D3 and D4 are **retargeted to v1.5.0**, not dropped. D4 in particular is worth
keeping: the antecedent states flatly that *"there is no monopole temperature
anisotropy in the CGI approach while there is one in the canonical treatment"*,
and a claim the paper makes in one sentence is exactly what a reproduction
bundle should check.

### The lesson, and it is the same one three entries running

**Fixing the instance is not closing the class.** T-16 fixed a stale label and
left the mechanism that produces stale labels. T-3 fixed one unguarded grid and
left the rest unregistered, which is T-46 and Q7. Both classes are closed now,
each by a cheap check that can fail —
`check_deferrals()` and `scripts/make_grid_register.py` — and neither closure
cost more than the finding that prompted it. **The expensive thing was finding
the third instance, not writing the gate.**

---

## T-48 — the script written to close a defect class shipped an instance of another one

**Found on the PI's machine, 2026-10-15, by `git add`.** `scripts/`
`make_grid_register.py` wrote its output with `Path.write_text(...)` and no
`newline="\n"`. On Linux that is LF; on Windows, Python's text mode translates
to **CRLF**. The PI's run produced:

```
warning: in the working copy of 'provenance/GRID-REGISTER-v1.md',
         CRLF will be replaced by LF the next time Git touches it
```

**Every other generator in this bundle passes `newline="\n"`** ---
`make_manifests.py` on all three manifests and the append guard,
`make_release_status.py`, `sync_conventions.py`. This one did not, so the same
checkout generated a different file on the PI's machine than on the one that
wrote it.

### Why it matters beyond a git warning

`PORTABLE-MANIFEST-SHA256.txt` exists to assert that **the same checkout
produces the same fingerprint on every machine**. A generated file whose line
endings depend on the platform breaks that directly, and it would have been
found as a mysterious portable-manifest mismatch on a third machine rather than
as a one-line omission.

### The part worth keeping

`make_grid_register.py` was written **in this session, to close the class of
unguarded discretisations** after T-3, S24's correction to itself, and T-46.
It shipped carrying an instance of the platform-portability class that
**T-15** already exists for. Closing one class does not inoculate the code that
closes it, and new code is exactly where the house conventions are least likely
to be applied --- there is no old version of it to copy from.

**The check that would have caught it does not exist and is not built here.**
A grep for `write_text(` without `newline=` across `scripts/` would be two
lines, and it is noted as worth doing rather than done, because adding a third
gate in the same session that added two is how a harness becomes something
people stop reading. Recorded for v1.5.0.

---

## T-49 — the release archive was named from a version frozen into the code

**Found by the PI, 2026-10-16, looking in `dist/` for a file that was never
going to be there.** `scripts/make_release_archive.py` declared

```python
parser.add_argument("--version", default="1.0.0", ...)
```

so `python scripts/make_release_archive.py` with no argument built a
**v1.0.0-named archive out of a v1.2.0 tree**. The archive itself was sound ---
it passed every gate it was given, because those gates check the *contents*
against the manifests and the contents were correct. Only the **name** was a
release behind.

### Why it is worse than a wrong filename

The archive prints a sha256 and says *"publish this digest with the release; it
is what attests the deposited copy is the same object."* A file named
`-v1.0.0.zip` carrying v1.2.0 content, with a digest published beside it, is an
attestation pointing at the wrong release. Nothing in the gates could catch it:
every one of them verifies the content, and the content was right.

### The class, for the fourth time

**T-16** is stale labels. **T-47** was a deferral to a release that had already
happened. **T-48** was a generated file whose line endings depended on the
platform. This is a *version* frozen into code at the moment it was written,
going stale at the next release and failing **silently** --- the operator
simply does not find the file, and there is nothing to read that says why.

### What is carried now

The default is `None` and resolves from `CITATION.cff`, which
`scripts/bump_release.py` keeps current as part of the release act and which
`tests/test_readme_artefacts.py` already calls *the one version statement a
machine acts on*, since GitHub's "Cite this repository" and Zenodo both read
it. **An archive named from the same field the release is declared in cannot
disagree with the release it is an archive of.**

### The lesson, and it is a general one

**A hard-coded default is a label.** `n_eta=4000` was one (T-3, T-46),
`"v1.1.0"` in a deferral dict was one (T-47), and `"1.0.0"` here is one. Each
was correct on the day it was typed. The bundle now has three mechanisms that
derive rather than declare --- `required_n_eta`, `check_deferrals`,
`released_version` --- and the pattern is the same every time: **find the one
place the fact already lives, and read it.**

## T-50 — three files the bundle cannot read or rebuild passed every gate and shipped

**Found by P1-B, 2026-10-16, counting the released archive against the tree it
was cut from.** The PI's `scripts/make_release_archive.py --version 1.2.0` run
reported **198 files**, sha256
`71c204e61486e766486c7fe2c756ece5bf3787b3aa29041eb61ee5a89d9a8e14`, with
portability and all three manifests PASS *inside the extracted archive*. This
tree held **195**. The three extra files were:

| file | what it actually is |
|---|---|
| `SUPPLEMENTARY-MATERIAL-v1.0.0.tex` | **UTF-16LE with a BOM and CRLF**, 51,622 bytes for ~25.8 kB of text. No LaTeX in the bundle compiles it; no `grep` in the bundle reads it. |
| `supplementary-materials/figures-v1.0.0.tex` | **byte-identical** to `figures-v1.2.0.tex`, sha256 `4295dcb3…`. v1.2.0 content under a v1.0.0 name. |
| `supplementary-materials/supplement-v1.0.0.pdf` | 37 pages, built the same morning, left behind when the build was repointed at the v1.2.0 source. |

The first came from restoring the frozen v1.0.0 supplement to satisfy **S36**.
In Windows PowerShell 5.1 a bare `>` redirection and `Out-File` without
`-Encoding` both write **UTF-16LE**, so `git show v1.0.0:… > …` produces a file
twice the size and readable by nothing. The other two came from the opposite
end of the same operation: the build was repointed from
`SUPPLEMENTARY-MATERIAL-v1.0.0.tex` to `-v1.2.0.tex`, and the outputs it had
already written under the old name were never removed.

### Why every gate passed, and this is the part that is a defect in a gate

`scripts/check_portability.py` finds mixed line endings by counting `b"\r\n"`
against `b"\n"`. **In UTF-16LE a CRLF is `0D 00 0A 00`** --- the two bytes are
never adjacent, so the CRLF count is **zero** and the file presents as
uniformly LF. Its remaining checks are `.py`-only, so nothing else looked at a
`.tex` at all. *A byte-level gate that assumes one byte per character cannot
see a wide encoding.* The manifests hash bytes and so were content with
whatever the bytes were; `check_against_git` compared the tracked set to the
disk set and they agreed, because all three files were committed.

### What it did and did not cost

**The release reproduces.** `scripts/build_supplement.py` named its source as a
single pinned path, not a glob, so nothing in `run_all.py` ever opened the
UTF-16 file, and `figures-v1.0.0.tex` and `supplement-v1.0.0.pdf` are read by
nothing. The three files are inert. What shipped is a `supplement-v1.0.0.pdf`
that is **not** the v1.0.0 supplement and a `figures-v1.0.0.tex` that is
**not** v1.0.0's figure section --- the **T-16** class, in a frozen artefact,
under a name a reader comparing releases would trust.

**The tag is not moved and no patch release is cut.** Coordination's rule ---
*"do not retag anything already released; a moved tag is the git equivalent of
editing a frozen directory"* --- and the published digest both forbid the
first. The second would cost a full `--strict` run, a new archive and a new DOI
to remove three files nobody executes. Decision **S39** records the reasoning;
the v1.2.0 release notes carry the contents note; the files come out at v1.3.0.

### The root cause, which is neither encoding nor cleanup

**The live supplement's name was a string literal in nine files.**
`build_supplement.py` (twice), `make_figure_pages.py` (twice),
`bump_release.py`, `test_translations.py`, `test_readme_artefacts.py`,
`test_house_grammar.py`, `test_bundle_file_selection.py` and
`test_portable_manifest.py` (three times) --- and four more sites in
`README.md`. **Opening a release line was therefore a dozen hand edits**, which
is exactly the shape of defect `bump_release.py` was built to remove from the
*closing* end. It had no `--open`. The end with the tool did not drift; the end
without one did, on its first use.

Counting the hardcoded sites was not possible by eye: the gate written below
found **five that this analysis had missed**, in tests nobody had thought of as
naming the supplement.

### What is carried now

* **`scripts/_versions.py`** --- the one module that says what version this
  tree is. `CITATION.cff` states the *released* version, `README.md`'s header
  states the *tree* version, and all three supplement filenames are derived.
  Nine literals became zero.
* **`scripts/check_release_hygiene.py`**, a release-blocking gate beside
  portability in `run_all.py`: every text file decodes as **UTF-8 with no NUL
  byte**; the supplement's generated artefacts name **only** the source the
  build is pointed at; and no `.py` file but `_versions.py` spells a supplement
  filename as a string literal. It walks the AST, so a docstring that *mentions*
  a file is prose and a literal the code acts on is the defect.
* **`scripts/bump_release.py --open X.Y.Z`** --- the symmetric half. It flips
  the three tree labels and the README's two supplement links, opens the
  changelog section, copies the supplement forward with its `\date` and its own
  `\input` repointed, and **removes the previous release's build outputs**.
* **`tests/test_release_hygiene.py`** --- four negative controls that rebuild
  each shipped file and assert the gate refuses it. **T-24**'s discipline: a
  check written after the defect, against a tree already clean, is a check
  written to pass.

### Two lessons, and the second is the larger one

**A gate must survive its own subject matter.** The first draft of the new gate
`ast.parse`d every `.py` file, and on the UTF-16 control it died with
*`SyntaxError: source code string cannot contain null bytes`* and printed
**nothing at all** --- a gate that crashes on the defect it exists to name
reports less than no gate. It now continues past a file `check_encoding` has
already reported.

**A tool for one end of an operation is a hazard at the other.**
`bump_release.py` exists because *"a label flipped by hand is a label that
drifts"*. Having it for closing a release made closing reliable and left
opening one entirely manual --- and made it feel safe, because the version
labels were now somebody's job. The defect did not appear in spite of the tool;
it appeared **in the half the tool did not cover**. When a script is written
for a procedure, ask what the inverse procedure is and whether anyone owns it.

## T-51 — the acoustic oscillation starts at z = 3000, which discards half the sound horizon

**Found 2026-10-16, on the PI's question: "did the visibility function over damp
away our acoustic peaks?"** The answer is no --- the visibility never touches
them --- and chasing why not found the thing that does.

### The peaks are not damped. They are in the wrong place.

Extrema of $D_\ell$, parabolically interpolated off the released F9 grid:

| | first maximum | peak spacing |
|---|---|---|
| CAMB | $\ell=206.1$ | 285.5, then 237.6 |
| CLASS | $\ell=206.2$ | 285.5, then 237.6 |
| **this bundle** | $\ell=161.8$ | **589.7** |

**A damping envelope multiplies; it cannot change a period.** Ours is 2.1--2.5
times too long, so this was never an amplitude problem. **Q8** read
ours/CAMB $=0.14$ at $\ell=720$ as missing second and third peaks; what it was
measuring is our *trough* at $\ell=549$ sitting on CAMB's second *maximum* at
$\ell=492$. Two curves out of phase, compared bin by bin.

### Where the phase goes

$\ell_{\text{peak}}$ spacing is $\pi(\eta_0-\eta_*)/r_s(\eta_*)$, and
$r_s(\eta_*)=\int_0^{\eta_*}c_s\,d\eta$ runs from the big bang.
`functions.spectra.pipeline.run` hands `solve_acoustic` the grid
`eta[inside]`, which begins at `recombination.eta[0]` --- and that is
$\eta$ at `RecombinationHistory.build`'s **`z_max = 3000.0`**. For
`PLANCK_MODEL`:

| | $\eta_{\text{start}}$ | $r_s$ | fraction of the full horizon |
|---|---|---|---|
| $\int_0^{\eta_*}$ | 0 | 0.036135 | 1.000 |
| as shipped, from $z=3000$ | 0.033332 | 0.017789 | **0.492** |

**50.8% of the sound horizon is missing**, so the accumulated phase $k\,r_s$ is
halved and the peak spacing doubles. Predicted $\Delta\ell=552.6$ against the
measured 589.7; with the full horizon, 272.0 against CAMB's 285.5.

### Confirmed by construction, not by arithmetic alone

Starting the integration earlier and changing nothing else, the measured period
in $k$ tracks $2\pi/r_s(\eta_{\text{start}}\to\eta_*)$ at every start:

| `z_max` | $\eta_{\text{start}}$ | fraction | $\Delta\ell$ implied |
|---|---|---|---|
| 3 000 | 0.033332 | 0.492 | 571 |
| 20 000 | 0.006345 | 0.899 | 319 |
| 200 000 | 0.000672 | 0.989 | **281** |

**At $z_{\max}=2\times10^5$ the bundle reproduces CAMB's 285.5 to 1.6%.**

### Why nothing in the bundle could see it, and this is S4c vindicated

Criterion **5b** compares (102) against (177)--(179) at
$9.5\times10^{-6}$ --- and **both routes take their acoustic solution from the
same `solve_acoustic` call on the same truncated grid.** A self-comparison
cannot see a shared antecedent, which is exactly what **S4c** says and why it
demoted the external comparison from gate to context. *Context is not
decoration*: the CAMB/CLASS comparison is the only instrument in the bundle
that could detect a missing half of the sound horizon, and it is the one that
did. **T-3**'s lesson in its sharpest form yet --- two agreeing routes agree
about what they share.

`functions.spectra.acoustic.sound_horizon` carries the same truncation
independently: it returns `concatenate(([0.0], cumulative_trapezoid(c_s, eta)))`,
the integral from `eta[0]` rather than from 0, so the closed-form route (180)
inherits it whenever it is handed a grid that does not start at the big bang.
**Two implementations, one wrong assumption, no disagreement to notice.**

### The class, and it is the third instance

`z_max = 3000.0` is a **chosen literal standing where a derivation belongs** ---
**T-3**'s `n_eta=4000`, **T-46**'s recombination grid, and now the acoustic
start. The grid register classifies discretisations and would not have caught
this: $z_{\max}$ is not a *resolution*, it is a **physical range**, and nothing
in the bundle audits those. That is a gap in the register's own premise and is
raised as its own question rather than patched here.

### What the fix is, and why it is not simply a bigger number

Lowering $\eta_{\text{start}}$ alone is not enough. `solve_acoustic` starts from
`(ADIABATIC_MONOPOLE * phi_a[0], 0.0)` --- $\tau_1=0$, which is the adiabatic
growing mode only while the mode is **outside the sound horizon**. At
$z=2\times10^5$ and $k=900$, $k\eta_{\text{start}}=0.60$: not small, so that
start imposes a phase of its own, and it is why the first maximum sits at
$\ell=161.8$ rather than at the $\ell\simeq414$ a pure truncation would give.

**The start must be derived per mode from $k$**, as `required_n_eta` is derived
from $k_{\max}$: integrate each mode from the $\eta$ at which
$k\eta\le\varepsilon$ for a stated $\varepsilon$, and **raise** if the
background cannot reach it. A single global $z_{\max}$ cannot serve a band
spanning a factor of 2000 in $k$.

**No number is changed here.** This lands in v1.3.0 under **S37**'s second half,
with **S33**'s derived recombination grid beneath it, and the released v1.2.0
figures stand as measured --- **S39**: a release is corrected by a new release.


## T-51 — FIXED the same day. The acoustic start is derived per mode from $k$.

**Fixed 2026-10-16, hours after being recorded.** `pipeline.run` takes
`acoustic_start`, defaulting to **`"derived"`**: each mode is integrated from
the $\eta$ at which $k\,r_s(\eta)\le0.1$, which is what (180)'s
$\delta T(0,k)\simeq-\tfrac23\Phi_A(0,k)$, $\tau_1=0$ means by *at the big
bang*. `"z_max"` reproduces the old behaviour exactly and is **kept as a
control**, the way `expansion_coupling=False` keeps (154) and
`sachs_wolfe_at_last_scattering_printed` keeps B-8: a defect that leaves no
executable trace is a defect that gets made again.

### What it recovers

Peak spacing against the antecedent's own $\Delta\ell=\pi r_\theta/r_s$,
measured on the transfer function at $\eta_*$:

| | `z_max` | **derived** | the paper's formula |
|---|---|---|---|
| CDM (Einstein--de Sitter) | 568.7 (×2.95) | **191.7** (×0.995) | 192.7 |
| $\Lambda$CDM | 491.4 (×2.85) | **172.5** (×0.999) | 172.7 |
| `PLANCK_MODEL` | 574.0 (×2.11) | **271.7** (×0.998) | 272.2 |

**Einstein--de Sitter is the one that settles it.** $\Omega_r=0$ makes Appendix
G *exact* for it --- there is no radiation era to approximate --- so the 0.5%
there is the whole error, and it is ours no longer.

The $C_\ell$ peak spacing for Planck parameters comes out at **284** against
CAMB's and CLASS's **285.5**, from 589.7 before.

### Four things the fix needed that the diagnosis did not predict

1. **`potentials` normalised at `eta[0]`.** *"which is taken to be deep in
   matter domination"* --- an assumption about the caller's grid, baked into a
   library. Harmless while every grid began at the same place; **fatal** the
   moment the start became per mode, because every mode would have carried its
   own $\Phi_A(0,k)$. `constant_below` now sets the normalisation from one
   reference, computed on `potentials`' own internal grid, and the result is
   grid-independent to twelve figures. Tested.
2. **`matter_domination_eta` cannot use a comfortable margin.**
   $\rho_M/\rho_R=5.16$ at last scattering for Planck parameters, and a
   reference at 9 lands *after* recombination. The default is equality, and the
   marginality is approximation **A-3**.
3. **The per-mode grid needed deriving too.** `required_acoustic_points(k,
   span)` at 24 samples per oscillation, from the bound $c_s\le1/\sqrt3$. The
   start being per mode makes the *span* per mode; a fixed point count cannot
   serve a band spanning 2000× in $k$. Same construction as `required_n_eta`,
   same reason.
4. **`potentials` could not be called per mode.** It runs a growth integration
   on an 8192-point internal grid, and $\Phi$ does not depend on $k$ at all;
   1433 of them would have been the whole run. Splined once over the widest
   span any mode asks for.

### What it does not recover, and that is the interesting half

The *phase offset*. Our maxima sit at $j\,\ell_A$ with
$\ell_A=\pi r_\theta/r_s=272$ --- 272, 544, 816 against measured 552 and 836 ---
where CAMB's are at 206, 492, 729, shifted **down**. That shift is the
radiation driving, and *Annals II*'s matter-dominated Appendix G has no term
for it. Recorded as approximation **A-3** rather than chased: it is the
antecedent's scope, not a defect, and **S15** says reproduce.

**So the acoustic sector now splits cleanly into a scale and a driving**, and
only the second is open. That is a far better position for **S35a**'s Hu \&
Sugiyama comparison than Q8 was: it has a specific term to measure rather than
a spectrum-wide discrepancy to explain, and **Appendix C**'s scattering-strength
expansion is the frame-covariant object to set against it.

### The record's own lesson

`tests/test_acoustic_scale.py` was written *"to fail when the defect is
repaired"*, and **it did not fail**. It measures what a start at $z=3000$
discards, which is arithmetic about the recombination grid and is unchanged by
a fix to where the pipeline begins integrating. **A test written to fail on
repair must assert on the repaired object**, not on the quantity that motivated
the repair. It now carries
`test_the_derived_start_reproduces_the_antecedents_peak_spacing`, which does.

## T-52 — the correction for T-51 nearly rescaled every Einstein–de Sitter amplitude by $10^{-6}$

**Found 2026-10-16, within the hour, by a test whose job is to fail.**

Fixing **T-51** required `potentials` to normalise $\Phi_A$ at one reference
rather than at the caller's first grid point. For a background with radiation
that reference is matter–radiation equality. For $\Omega_r=0$ there is no
equality, and the first attempt used the $r_s$ table's own floor, $10^{-9}$ —
on the reasoning that it was *"a quantity the grid register already carries
rather than a new literal"*.

**It is a quantity that exists for a different purpose.** $10^{-9}$ is the
lower limit of an $r_s$ integral whose integrand is bounded by $1/\sqrt3$, so
nothing below it can matter. `growth_factor` started there integrates an
**explicit** ODE whose friction is $aH=2/\eta=2\times10^{9}$ and whose source
is $\propto1/a\sim10^{18}$:

| `constant_below` | $\Phi_A$ for Einstein–de Sitter |
|---|---|
| $10^{-9}$ | **1.58e-06** |
| $10^{-6}$ | 0.655 |
| $\eta(z=3000)$ | **1.000000000000000** |

$D=a$ exactly in Einstein–de Sitter, so $\Phi\propto D/a$ is **identically
one**. The first row is wrong by six orders of magnitude, and it is *smooth,
constant and plausible* — the same failure mode as **T-3**'s aliased grid,
which also returned a clean wrong answer rather than an error.

### What would have shipped, and what stopped it

Every Einstein–de Sitter amplitude would have been rescaled by $1.6\times
10^{-6}$. **Nothing in the physics suite would have seen it**: F9 renormalises
at $\ell=30$, criterion 5b compares two routes that would both have carried the
factor, the frame comparison is a ratio, and F2's truncation tails are
fractions. A uniform rescaling is invisible to every instrument built to be
insensitive to normalisation — which is most of them, deliberately.

What caught it was the **control half** of T-42's test,
`test_102_must_carry_the_visibility_and_substituting_the_opacity_wrecks_it`:
the assertion that substituting $e^{-\kappa}$ into (102) *must* wreck the rank
decomposition. It stopped wrecking it, at three of four multipoles. **A test
that only ever passes cannot report anything**; this one is half control by
construction, and the control is what fired. Finding **T-24** is where that
discipline came from, and this is the first time it has paid for itself on a
defect it was not written for.

### What is carried now

`tests/test_frames.py::test_phi_is_exactly_one_in_einstein_de_sitter_whatever_the_reference`
pins the identity directly, at three references, so the next reference that is
too early fails *there* rather than four tests away in a control nobody expects
to be load-bearing.

**The lesson is about reuse, not about ODEs.** The $10^{-9}$ was chosen
*because* it was already registered and justified — and it was justified **for
an integral with a bounded integrand**, not for an initial-value problem. A
constant imported from where it is safe into where it is not is still a
hard-coded literal; it has merely borrowed someone else's argument for being
one.

## T-53 — a search window fitted to a result reported its own edge as a measurement

**Found 2026-10-16, on the first regeneration after T-51's fix.** F9 printed

    CDM (Einstein-de Sitter)   first peak l=90.0

`90.0` is exactly the first $\ell$ on the grid at or above 80, carries no
interpolation, and is not a peak.

`first_peak(ell, s)` searched a fixed band, $80\le\ell\le400$, took `argmax`
within it, and guarded the parabolic interpolation with

```python
i = int(np.argmax(y))
if i == 0 or i == x.size - 1:
    return float(x[i])
```

That guard is correct as arithmetic — a parabola needs two neighbours — and
**wrong as a report**: an extremum at the edge of a search window is evidence
that the window is in the wrong place, and returning the edge converts that
evidence into a number. With the acoustic start corrected (**T-51**,
**S40**) the Einstein--de Sitter curve stopped having an interior maximum in
$80\le\ell\le400$ at all, and the absence was reported as a measurement.

### Why the window was there, and why that is the finding

**80--400 was chosen when the peak sat near 170.** It is not a physical band:
nothing says the first acoustic peak lies in it, and the moment the physics
moved the window became a filter on the answer rather than a search for it.

*A search window fitted to a result is a window that hides the result
changing.* It is the same shape as **T-3**'s `n_eta=4000` and **T-49**'s
`"1.0.0"` default — a literal that was right on the day it was typed — but it
fails in a worse direction than either, because it does not go silent. It
returns a plausible number of the right order, next to five other numbers that
are real.

### What is carried now

There is **no window**. `first_peak` scans for the first *interior* local
maximum above $\ell=30$ --- the normalisation anchor, below which "first peak"
has no meaning --- and returns **`nan`** when the curve has none. The caller
prints *"NONE above l=30 — the curve has no interior maximum"*, and `draw`
annotates the absence on the figure instead of ruling a line at `nan`, which
would have drawn nothing while the caption went on claiming a peak.

**`nan` is the right return and the earlier `float(x[i])` was not**, for the
reason finding **T-44** gives: that gate printed `PASS` on a `nan` because
`nan >= gate` is `False`. The lesson there was to refuse non-finite values
explicitly. The lesson here is its converse --- **when the honest answer is
"there isn't one", return something that cannot be mistaken for a measurement**,
and make every caller say so out loud.

## T-54 — the harness printed CLEAN over a two-day-old spectrum, and no gate could see it

**Found 2026-10-17, auditing the PI's regeneration.** `run_all.py --rerun`
finished with

```
wrote PORTABLE-MANIFEST-SHA256.txt  177 files, numeric canonicalised to 9 s.f.
441 passed, 3 skipped
============================================================
CLEAN
```

and `outputs/f9-acoustic-spectrum.csv` was stamped **2026-10-15 18:23**, two
days and three findings earlier. Its extrema still read `max@162, min@549,
max@752`, peak spacing **589.7** — the pre-**T-51** acoustic scale, against the
corrected 284. Every other artefact had regenerated correctly within a
twelve-minute window: F2, F3, D5, D6 and D8 all carry 2026-10-16 14:08–14:20.

### Why no gate caught it, and this is the part worth keeping

F9 is wired into `run_all` as `"scripts/figure_f9_acoustic_spectrum.py --replot"`,
and deliberately: a full recompute is 1433 modes × 3 backgrounds × 2 frames and
cannot run on every harness pass. **That cache is sound. What it allowed was
invisible.**

1. `--replot` reads the CSV and redraws. **It does not rewrite the CSV.**
2. So the CSV still matches its recorded hash.
3. So `make_manifests.py --check` passes.
4. So `run_all --rerun` prints **CLEAN**.

**A content hash cannot detect a file that was never regenerated.** It answers
*"is this file what it was?"* — and that is exactly the wrong question for a
cached artefact, where the right one is *"was this file made by this code?"*
The manifest machinery is not weak here; it is being asked something it does
not claim to answer. **T-1** built one selector so two gates could not disagree
about what the bundle is; this is the complementary gap — one artefact the
gates agree about and neither can date.

It is also the third time a *caching* convenience has cost a regeneration in
two days: the first F9 run of 2026-10-16 recomputed for 35 minutes and produced
byte-identical output because `two_frame` was unfixed (**T-51**), and the PI's
run here skipped the recompute entirely. Both cost about an hour. The cache is
still right; it simply had no way to say when it was wrong.

### What is carried now

The CSV carries a `# sources:` line — a sha256 over **every `functions.*`
module actually imported**, resolved from `sys.modules` rather than listed, plus
the script itself. `--replot` recomputes it and **refuses** on a mismatch:

```
FAIL  the cached CSV was produced by different code
      (stamped nothing, this tree a73e8d9dc8115b17).
      --replot cannot redraw numbers it did not compute.
```

**Deliberately conservative.** A docstring change invalidates the cache,
because bytes cannot say whether a change was semantic. The cost of a false
invalidation is one rerun; the cost of a false validation is shipping a stale
spectrum under a CLEAN banner, which is what happened.

### The class, and where else it lives

**Any artefact whose regeneration is cached is an artefact whose staleness a
content hash cannot see.** F9 is the only `--replot` stage today. The same
shape applies to anything the harness skips rather than recomputes — and
`scripts/compare_criterion_5b.py` is already outside the harness by **S4c**, so
`provenance/CRITERION-5B-v1.md` carries 2026-10-15 09:55 and
`outputs/criterion-5b.csv` 2026-10-14 18:36. **Those are stale by the same
mechanism and by deliberate design**, which makes the design's cost explicit
for the first time: the README quotes that file's 97.8% and 137% in three
places, and nothing in the bundle dates them. Raised as a question rather than
patched here, because S4c's reason for keeping the comparison out of the
harness has not changed.

## T-55 — the potential reference was put at equality, and the frame-closure guard failed on one platform

**Found 2026-10-17 on the PI's Windows machine**, during the F9 recompute that
**T-54** had just unblocked. CDM and $\Lambda$CDM completed; `PLANCK_MODEL`
stopped at

```
ValueError: Appendix G's sigma-dot and the Euler equation disagree on
(a sigma)'; the CDM frame no longer closes
```

**The source files were identical on both machines** — staged and diffed, byte
for byte — and the same configuration passed at every $k$ from 0.05 to 1499 in
this container. A physics guard that passes on Linux and fails on Windows is
reporting something about the calculation, not about the platform.

### What was wrong

**T-51**'s fix needed one $\Phi_A$ reference shared by every mode, so that a
mode starting at $\eta=10^{-4}$ and the common grid starting at $0.033$ carry
one $\Phi_A(0,k)$ between them. For a background with radiation I set that
reference to **matter–radiation equality**, reasoning that it was where the
antecedent's matter-dominated Appendix G becomes applicable.

For `PLANCK_MODEL` that is $\eta_{\rm eq}=1.949\times10^{-2}$, **below** the
recombination grid's first point at $0.0333$. So `growth_factor` began its
integration *at equality* — from $D=a$, $D'=a'$, which is the **matter**
growing mode, in a universe that is half radiation there. The integration opens
on a transient.

`coefficients.cdm_set` holds Appendix G against the Euler equation,

    (a sigma)' = a' sigma + a^2 sigma-dot  ==  -k v',

at `rtol=1e-9`, **over every $\eta$ including those first points** — and the
transient sits exactly there. The residual straddles $10^{-9}$, and DOP853
choosing different step sequences on two platforms decides which side.

### Why equality was unnecessary as well as wrong

`constant_below` has one job: fix the normalisation so it does not depend on
the caller's grid. **Any** fixed $\eta$ does that, and $\Phi_A$ is held
*constant* below it either way — which is not a modelling choice but the
antecedent's own result, $\Phi_E$ time-independent for $K=0$ dust. Equality
bought nothing and cost the integration its initial condition.

The reference is now **the recombination grid's first point, for every
background**. The common-grid potentials come out **bit-identical** to the
pre-T-51 ones — measured, `max|new/legacy - 1| = 0.000e+00` on CDM,
$\Lambda$CDM and `PLANCK_MODEL` — so **no released number moves for this
reason**, only for T-51's. The guard passes at $k=0.05$ through $1499$ on all
three.

`matter_domination_eta` stays, and is no longer an input to anything computed:
it is the diagnostic that measures **A-3**'s marginality, $\rho_M/\rho_R=5.16$
at last scattering.

### The lesson, which is about where a guard looks

This is the **third** time in two days that choosing a reference *earlier*
broke something: **T-52**, the $r_s$ table's $10^{-9}$ floor returning
$1.58\times10^{-6}$ for a quantity identically one; this, equality opening on a
transient; and in both cases the quantity itself looked fine while a derived
one did not. **An initial-value problem has a domain of validity and a grid
does not**, so a reference chosen for a grid's convenience will keep landing
outside it.

What caught it is worth naming too. The guard checks an **identity**, not a
tolerance — $(a\sigma)'=-kv'$ holds exactly given the field equations — and it
checks it *pointwise over the whole grid* rather than at the one $\eta$ the
answer is read at. A guard that had looked only at $\eta_*$ would have passed
on both platforms and shipped the transient. **Finding T-24's rule, inverted:
a check that can only fail where nobody reads the answer is the one worth
keeping.**


---

## T-56 — the $k$ grid was set by hand, and samples the projection kernel below Nyquist

**Found 2026-10-17**, while separating the quadrature from the physics in **Q11**.

`required_n_eta` derives the line-of-sight $\eta$ grid from the oscillation it
has to resolve: $j_\ell(k(\eta_0-\eta))$ has period $\pi/k$ in $\eta$, so the
grid carries twelve samples per period at $k_{\max}$. **Nothing derived the $k$
grid.** F9 ships

```python
K_COM = np.arange(0.05, 1500.0, np.pi / 3.0)
```

under a comment that correctly rejects a logarithmic grid — *"a logarithmic $k$
grid aliases the integrand at high $k$ however many points it has"* — and then
chooses the linear spacing without asking what it must resolve.

### The arithmetic it skipped

$C_\ell=\int dk\,k^2\mathcal P(k)|T_\ell(k)|^2$ carries $j_\ell(k\,\Delta\eta)$
**squared**, whose period in $k$ is $\pi/\Delta\eta$. So

$$dk\;\le\;\frac{\pi}{\texttt{points\_per\_period}\;\Delta\eta},$$

which is `required_n_eta`'s formula with $\Delta\eta$ in place of the $\eta$
span. **One kernel, two axes; the bundle derived one of them.**

| background | $\Delta\eta$ | $\pi/\Delta\eta$ | samples per period at $dk=\pi/3$ |
|---|---|---|---|
| CDM (Einstein–de Sitter) | 1.9404 | 1.619 | **1.55** |
| $\Lambda$CDM | 3.1956 | 0.983 | **0.94** |
| `PLANCK_MODEL` | 3.1289 | 1.004 | **0.96** |

Below one sample per oscillation on both $\Lambda$CDM-like backgrounds.

### Measured against a closed form, not a convergence study

For a pure Sachs–Wolfe transfer at $n_s=1$ the spectrum integral collapses to
an exact number at every multipole, independent of $\Delta\eta$:

$$\int_0^\infty\frac{dk}{k}\,j_\ell^2(k\,\Delta\eta)=\frac{1}{2\ell(\ell+1)}.$$

Computed / exact on `PLANCK_MODEL`:

| grid | $n_k$ | per period | $\ell=2$ | $\ell=30$ | $\ell=200$ | $\ell=400$ |
|---|---|---|---|---|---|---|
| F9, $dk=\pi/3$ | 1433 | 0.96 | **1.211** | **0.950** | 1.017 | 0.985 |
| $\Lambda$CDM, same grid | 1433 | 0.94 | **1.225** | 1.054 | 1.018 | 0.978 |
| derived, $dk=\pi/12$ | 5730 | 3.84 | 1.000 | 1.000 | 0.999 | 0.996 |

**The error is non-monotonic in $\ell$** — high at 2, low at 30, high again at
100 — so it does not cancel out of a spectrum normalised at $\ell=30$; it is a
few-percent ripple whose sign turns over on a scale of tens in $\ell$. *That
moves a peak*, and because each route's $T_\ell(k)$ aliases against the grid
differently, it moves it by a different amount in each route. The two routes
disagreeing about where the first peak sat — pipeline 119/365/573 against
two_frame 105/410/655 — is partly this.

### Why no gate saw it

**T-16** and **T-32** gate $k_{\max}$ against the Silk damping scale, and F2
reports $\exp[-(k_{\max}/k_D)^2]$ on every run. Both are about *where the grid
stops*. Nothing was about *how finely it steps*, because the quantity that sets
the step is $\Delta\eta$ — a property of the projection, not of the physics the
$k$ grid was being chosen for.

**Fixed**: `required_k_points` in `functions/spectra/pipeline.py`, beside
`required_n_eta` and sharing its arithmetic, with
`K_POINTS_PER_PERIOD = 3` derived from the table above rather than copied from
the $\eta$ grid's twelve — the two grids integrate the same kernel against
different companions, and the $k$ integral's sign-definite $j_\ell^2$ against a
smooth $k^2\mathcal P$ converges far faster. `tests/test_k_grid.py` asserts the
closed form and keeps F9's shipped grid as a **failing control**.

---

## T-57 — a field's documentation said one default and the code said the other, for eleven days

**Found 2026-10-17.** The dominant cause of **Q11**, and the most expensive
single line in the bundle so far.

`TwoFrameEnvironment.line_of_sight_weight` carried twenty lines of correct
reasoning, citing **A-2**, findings **T-41** and **T-42**, and re-measuring the
cost ($D_\ell$ rises $80.5\times$ from $\ell=2$ to 30 under $\mathcal V$ and
$8.17\times$ under $e^{-\kappa}$), and ending:

> `"opacity"` is therefore the default.

The line underneath it read:

```python
line_of_sight_weight: str = "printed"
```

### What that cost

**Approximation A-1** states the governance rule in words: *"Both weightings
implemented; **the caller states which**."* No caller did. All eight released
entry points took the default:

`figure_f2_truncation`, `figure_f5_sources`, `figure_f7_frames`,
`figure_f9_acoustic_spectrum`, `measure_frame_invariance` (D6),
`diagnostic_d7_frame_identification`, `compare_criterion_5b`,
`benchmark_single_run`.

So every one of them ran under $\mathcal V=\kappa'e^{-\kappa}$ — the weighting
**A-2** records that *"this bundle departs from"* — including the comparison
that produces `CRITERION-5B-v1.md`'s external-agreement numbers.

Measured on `PLANCK_MODEL`, CDM frame, one switch and nothing else (**D4**):

| | rank 0, monopole | rank 1, dipole | $D_2/D_{30}$ |
|---|---|---|---|
| $e^{-\kappa}$, A-2's choice | **0.986** | 0.0014 | 0.0926 |
| $\mathcal V$, as (178) prints it | **0.00002** | **1.0058** | 0.0083 |

**Under $\mathcal V$ the dipole is the entire transfer function at every
multipole from 2 to 100 and the monopole is two parts in a hundred thousand.**
(178) already carries $\kappa'\tilde v_B'+\kappa''\tilde v_B$; weighting it
again by $\mathcal V$ puts in a second factor of $\kappa'\simeq1.4\times10^4$.

### Why it produced exactly the symptoms Q11 recorded

Q11 predicted the mechanism and named the wrong cause. It reasoned: *"If the
$\cos$-bearing monopole never enters the projected transfer, the spectrum
inherits the rank-one dipole's $\sin$, and a half-period offset is exactly what
one would see"*, and attributed the missing monopole to (110)'s structure —
$c_0\equiv0$ in the Newtonian frame. **The prediction was right and the
attribution was wrong.** The monopole was not absent by construction; it was
present and outweighed a thousand to one. Hence, all at once:

* peaks at $(n+\tfrac12)\ell_A$ — the dipole's $\sin(k r_s)$ against the
  monopole's $\cos$;
* no Sachs–Wolfe plateau — $D_\ell\propto\ell^2$, which is $C_\ell$ constant;
* $C_2$ fed from $k\gg\ell/r_\theta$ — half of it from beyond $k=11$ where
  $\ell/r_\theta=0.64$ — because the Doppler term carries one more power of
  $k$ than the monopole.

### Why no gate saw it, and this is the part worth keeping

Criterion **5b** holds the weight **fixed on both sides** — `two_route`'s
docstring says so: *"the same line-of-sight weight, $e^{-\kappa}$, on both
sides"* — so it cannot see *which* weight it fixed. The manifests hash content.
`check_portability` reads bytes. The regression suite compares a route against
itself. **Every instrument in the bundle compares a file to a rule; this was a
decision disagreeing with its own implementation, three lines apart.**

**T-3's lesson in a new place**: two agreeing routes agree about what they
share, and here what they shared was a default argument neither named.

**Fixed 2026-10-17.** The default now matches its own docstring; all eight
callers state the weight explicitly; and `check_release_hygiene.py` gained a
fourth check that walks the AST of every released script and refuses a release
in which any caller of `build_environment` omits it. **D4**, deferred three
times, was written and now runs both weights every time — the departure A-2
records is only measurable while the thing departed from stays executable.

### What is not yet explained

Switching the weight moves $D_2/D_{30}$ from 0.0083 to 0.0926 against CAMB's
0.881. **An order of magnitude recovered and an order of magnitude still
missing**, and the plateau still rises rather than being flat. A-2's own table,
measured through `pipeline`, reports $e^{-\kappa}$ as *"flat to within 30% over
$2\le\ell\le20$"* — which `two_frame` does not reproduce. Two implementations
of (102), and with weights matched, BBKS off, identical backgrounds, identical
damping scale and `expansion_coupling=False` on both, they agree to 1–2% at
$k=1$ in the CDM frame and diverge by 20–800$\times$ with sign flips from
$k=3$ upward. That is the next thread and it is open.


### Postscript to T-56 — the register had it, and nothing escalated

`config/grid-register.toml` carried this grid all along, with its status given
honestly as **`described`**:

> `arange(0.05, 1500.0, pi/3)`, the same grid and the same rule as [...]

The register's own ladder distinguishes `derived` from `described`, and the
entry said plainly that this one was not derived. **What was missing was a rule
that a released deliverable's quadrature grid must be `derived`.** The
instrument existed, recorded the right thing, and had no consequence attached
to it — which is a different failure from not measuring, and a cheaper one to
fix. The entry is now `derived`; the register prints
`1xopen, 9xderived, 5xmeasured, 10xdescribed, 18xindex`, and the open question
of which of the remaining `described` grids feed a released number is worth one
pass before the tag.


---

## T-58 — three shared choices, three different values, and the gate could see none of them

**Found 2026-10-17**, closing **Q12**. The bundle carries (102) with a generic
$u^a$ in two implementations. Criterion **5b** gates one of them. **Every
released figure uses the other.**

With the line-of-sight weight already matched by **T-57**, the two differed by
$1.5\times10^{-1}$ to $1.6\times10^{0}$ of the row's own scale — five orders of
magnitude past 5b's $10^{-7}$–$10^{-6}$. Three causes, and each is the same
shape: *a choice one route made explicitly and the other inherited.*

| | `two_route` (gated) | `two_frame` (released) | `pipeline.run` |
|---|---|---|---|
| tight-coupling window | $\eta_0$ **← outlier** | $6\eta_*$ | $6\eta_*$ |
| (102)'s lower limit | $\eta[0]$ | $\eta_*$ **← outlier** | $\eta[0]$ |
| $\eta$-grid floor | 8000 | none **← outlier** | — |

### Each one, measured

**The window.** `two_route` integrated the acoustic oscillator to $\eta_0$,
keeping the photon–baryon fluid ringing for **7.6×** the span over which it is
a fluid, while the other two stopped at $6\eta_*$ and held the last value.
Cost at $k=3$: $1.5\times10^{-1}$. At $k=10$: $1.6\times10^{0}$.

**The lower limit.** `integral_solution`'s default is (102)'s printed $\eta_*$,
and its own docstring says `eta_floor` exists *"so the pipeline's long-standing
choice of integrating from the start of the recombination history can be
measured against the printed one rather than inherited."* `pipeline.run` and
`two_route` supply it; `transfer_by_rank` did not, **and so inherited the
printed limit by omission**. The visibility is peaked *at* $\eta_*$ with half
its support below, so that limit discards half the peak. Cost at $k=1$ — the
modes that build the Sachs–Wolfe plateau — $2.2\times10^{-1}$.

**The grid floor.** `N_ETA_FLOOR = 8000` existed in `two_route` because
**T-45** measured what going without it costs. `two_frame` sized its grid from
$k_{\max}$ alone, which resolves the $j_\ell$ oscillation and *not* the
recombination structure near $\eta_*$. Cost at $k=10$: $2.4\times10^{-1}$
without, $5.9\times10^{-3}$ with — **a factor of forty from a grid that looked
derived.**

### Fixed, and the remedy is structural

`TIGHT_COUPLING_FACTOR` and `N_ETA_FLOOR` now live in one module each
(`acoustic.py` and `pipeline.py`) and everything else re-exports;
`transfer_by_rank` states `eta_floor`; `build_environment` applies the floor.
`tests/test_two_frame_is_gated.py` compares the released route against the
gated one with a **control** that puts the printed lower limit back and
requires the gate to catch it, and asserts each of the three constants has
exactly one home.

Measured after, against (177)–(179), normalised by the row's scale:

| $k$ | 0.3 | 1 | 3 | 10 | 30 | 100 | 300 |
|---|---|---|---|---|---|---|---|
| before | — | 2.3e-01 | 1.5e-01 | 1.6e+00 | 1.2e+00 | 1.2e+00 | 1.2e+00 |
| after | 3.4e-04 | 9.4e-04 | 5.7e-04 | 5.9e-03 | 5.6e-03 | 3.5e-04 | 1.4e-03 |

**Two to three orders of magnitude**, and 5b's own number is unharmed: the
window change moves it within $10^{-7}$–$10^{-6}$, where it already was.

### What remains, and it is named

The residual is **one documented convention**. `two_frame` forms
$(\kappa'\tilde v_B)'$ by the product rule with $\tilde\tau_1'$ **analytic from
(152)**, which is exactly what `sources.py` argues for under finding **T-23**:
*"mode-expanding a derivative is not differentiating a mode amplitude"*.
`two_route` splines the product. Substituting one for the other closes the gap
to $7.6\times10^{-7}$ at $k=1$ and $1.8\times10^{-5}$ at $k=10$ — so the
residual is that convention and nothing else.

**The ungated route is arguably the more correct one**, and changing
`two_route` to match would move criterion 5b's published number. That is the
PI's call and is raised rather than taken.

### The lesson, which is the same one three times

T-3 says two agreeing routes agree about what they share. **5b's two columns
are built from one setup on purpose** — *"two setups with one rule cannot
drift"* — so every choice that setup makes is shared, cancels, and is invisible
to the comparison *by construction*. The instrument was sound and pointed at
the wrong pair.

Within one day the same shape appeared four times: the weight (**T-57**), the
window, the lower limit and the grid floor. In each, a parameter had a default
that encoded a choice, and a caller that never named it. **`check_release_hygiene.py`
now refuses an unstated weight; the other three are held by having one home
each.** The general rule — *a default that encodes an approximation must be
named at every call site* — is worth a decision of its own, and is proposed as
**S43** rather than asserted here.


---

## T-59 — the two frames disagree by 100%, and only one of them has a Sachs–Wolfe plateau

**Found 2026-10-17**, immediately after **T-57** removed the weight that was
masking it. This is the remaining order of magnitude in **Q11**, and it is not
a further defect in the quadrature or the assembly: *it is the frame.*

D4, one environment, one acoustic solution, one $k$ grid, differing **only** in
which frame (110) specialises to:

| $\ell$ | 2 | 4 | 7 | 11 | 16 | 22 | 30 | 45 | 60 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|
| $D_\ell/D_{30}$, Newtonian | **1.294** | 1.082 | 0.978 | 0.891 | 0.885 | 0.927 | 1.000 | 1.132 | 1.226 | 1.216 |
| $D_\ell/D_{30}$, CDM | **0.093** | 0.173 | 0.290 | 0.437 | 0.608 | 0.792 | 1.000 | 1.282 | 1.442 | 1.457 |
| CAMB | 0.881 | | | | | | 1.000 | | | |

**The Newtonian frame is flat to within 30% over $2\le\ell\le30$**, which is
exactly what `SOURCE-APPROXIMATIONS-v1.md`'s A-2 table says $e^{-\kappa}$
gives, and what a Sachs–Wolfe plateau *is*. The CDM frame rises by a factor of
eleven over the same range.

### The part that looked like a paradox and is not

In the Newtonian frame the **rank-zero share is identically zero** — (110) puts
the whole source in rank one — and *the plateau is there anyway*. Q11's
original write-up read $c_0\equiv0$ as "the $\cos$-bearing monopole never
enters the projected transfer" and inferred the half-period shift from it. The
inference was wrong: the monopole combination sits **inside $c_1$**, as
`newtonian_set`'s `a_b1 = k * (delta_t + phi_a)`. Rank one in the Newtonian
frame is not the Doppler sector; it is everything.

In the CDM frame rank zero carries 99% and the plateau is absent. Two
statements of one operator, and only one of them reproduces the limit.

### Corroborated twice over, by numbers that moved the same day

* **F2**: the cost of $\sigma\to0$ in the CDM frame is **99.93–100%**, where it
  read 0.27–26% before T-57. The CDM frame's source *is* the shear, as Paper 1
  §VI C says — and that only became visible once the dipole stopped carrying
  everything.
* **F5**: the two frames' $C_\ell$ now agree to a median of $9.99\times10^{-1}$
  — that is, not at all. It read $1.63\times10^{-1}$ before.
* **D6**: worst relative difference $1.316$, from $1.069$.

**This is finding T-14 and decision S21, measured.** `sources.py` already said
it in words: *"it does not [return the same total]: measured against the CDM
frame it moves by a factor of about five, **and under the opacity weighting the
source very nearly collapses altogether**."* The opacity weighting is now the
release's weighting, so the collapse is no longer hypothetical.

### What this means for the release, stated plainly

**F9 draws the CDM frame.** `curves[label] = frames[label]["cdm"]`. So the key
figure of a frame-covariance release is drawn in the frame that does not
reproduce the Sachs–Wolfe limit, and the frame that does is drawn beside it as
the comparison.

**Which frame F9 should draw is the PI's call**, because it is Paper 1's claim
and not a numerical one, and it is raised as **S44** rather than taken. What is
*not* a judgement call: the Newtonian frame is the one with an analytic
arbiter behind it — **D5**, 0.26% against the corrected (201) over
$2\le\ell\le20$, through `pipeline.run`, which is a Newtonian-frame assembly,
and `tests/test_sachs_wolfe.py`'s absolute comparison behind that.

### The sequence this closes

Q11 asked why the spectrum's peaks were in the wrong place when the source's
phase was right. Four findings answered it, and each was hidden by the one
before:

1. **T-57**, the weight — made the dipole 100.5% of the transfer, which put the
   peaks at $(n+\tfrac12)\ell_A$ and flattened $C_\ell$.
2. **T-56**, the $k$ grid — 0.96 samples per $j_\ell^2$ oscillation, a
   non-monotone 22% that moved peaks differently in each route.
3. **T-58**, three shared choices — window, lower limit, grid floor, which put
   the released route five orders of magnitude outside the gate it was never
   compared to.
4. **T-59**, the frame — the last order of magnitude, and the only one of the
   four that is a question about the physics rather than about a default.

**The first three were defaults nobody named. The fourth is Paper 1's subject.**
That is the right place for a reproduction bundle's investigation to end up.


---

## T-60 — the frame gap is $C_0$, the coefficient of a multipole that does not exist

**Found 2026-10-17**, resolving **T-59**. The PI asked whether the CDM-frame
result is "pure Doppler because of the frame". It is not Doppler, and it is not
a cancellation failure. It is **one coefficient, carrying two powers of $k$ it
should not have, projected onto every multipole.**

### The mechanism, in six lines of `match_coefficients`

```python
c0 = p0 * a_b2
c1 = p1 / k    * (a_b1 + kappa_prime_v_b)
c2 = p2 / k**2 * a_b2
```

$C_0$ and $C_2$ are **the same array**, $a\mathcal B_2$, divided by different
powers of $k$. In the CDM frame $a\mathcal B_2=a\sigma=-k v$ exactly (n-t1,
and the bundle asserts it), so

$$C_0=-p_0\,k\,v,\qquad C_2=-p_2\,\frac{v}{k},
\qquad \frac{C_0}{C_2}=\frac{p_0}{p_2}k^2 .$$

Measured, at $\eta_*$, on all three backgrounds and at every $k$ from 1 to 300:
$C_0/(k^2C_2)=\mathbf{2.5000}$ — a pure rational, exactly $p_0/p_2$ from (89),
because nothing else is in it. In the Newtonian frame $\mathcal B_2=0$, so
$C_0\equiv0$ and the term cannot appear at all.

`integral_solution` then adds $C_0$ to the bracket at **every** multipole:

```python
bracket = coefficients.c0 - c1_prime + c2_second
integrated[i] = trapezoid((weight * diffusion * bracket * j_l)[inside], ...)
```

### Measured: it is the entire gap

Dropping $C_0$ from the CDM frame and comparing with the **Newtonian total**,
relative to the Newtonian scale:

| background | $k$ | CDM total / N | CDM **minus $C_0$** vs N |
|---|---|---|---|
| CDM (Einstein–de Sitter) | 20 | 53.5 | **0.032** |
| | 300 | 1719 | **0.035** |
| $\Lambda$CDM | 20 | 62.8 | **0.105** |
| | 300 | 6868 | **0.154** |
| `PLANCK_MODEL` | 20 | 72.2 | **0.111** |
| | 300 | 3687 | **0.058** |

**Three to four orders of magnitude, to a residual of 1–15%**, which is the
honest size of the frame-covariance statement once the artefact is out of it.
D4 measured the same thing from the other side: rank zero is **98.6%** of
$C_\ell$ in the CDM frame and **identically zero** in the Newtonian one.

### Why this is a rank error and not an arithmetic one

$C_0$ is the coefficient of the $\delta_{\ell0}$ entry of (89). *Annals II*
p. 366 states flatly that **"there is no monopole temperature anisotropy in the
CGI approach while there is one in the canonical treatment"**, and
`integral_solution` refuses $\ell<1$ for the independent reason that (102)'s
rank-two term needs $j_{\ell-1}$. **There is no $\ell=0$ for $C_0$ to be the
coefficient of**, and it is nevertheless summed into the source at every
$\ell\ge2$, where its $k^2$ makes it dominant.

**Finding B-11 is already about this coefficient** — (89) prints the wrong sign
on its $\delta_{\ell0}$ entry, and `use_printed_c0` exists as the control. The
sign was questioned; the *placement* was not.

### D4 answers the question it was written for

D4 — *"no monopole in the CGI approach"* — was registered in v1.0.0 against
that one sentence, deferred to v1.1.0, retargeted to v1.5.0 under T-47, and
written on 2026-10-17 only because T-57 forced it. **It is the diagnostic for
exactly this**, and the sentence it was written to check is the sentence that
resolves the release's largest discrepancy. Three deferrals of the instrument
pointed at the answer.

### What this does NOT fix, and a correction to T-59

With $C_0$ removed both frames agree, and **both fall** through the acoustic
band — $D_\ell$ going $1.00$ at $\ell=30$ to $0.24$ at $\ell=270$ where CAMB
rises by about six.

**T-59's write-up inferred the opposite and was wrong.** It argued that because
one frame rose and the other fell through the same band on the same $T(k)$ and
the same acoustic solution, the missing acoustic amplitude "is T-59's, not
A-3's". The rise was $C_0$. With the artefact removed there is no rise in
either frame, so the inference is withdrawn: **the falling envelope is A-3**,
the absent radiation driving, and nothing in the frame sector will supply it.

That moves **Hu & Sugiyama from the end of the queue to the critical path**. It
was scheduled last on the grounds that it could not see T-56 through T-59.
It cannot — and T-56 through T-60 are now closed, which leaves the driving as
the only thing between this bundle and the peak heights.


---

## T-61 — $C_0$ is one half of a cancelling pair, and (102) carries only that half

**Found 2026-10-17**, answering **Q14** from the manuscript source rather than
from another measurement. **T-60** established that $C_0$ is the whole frame
gap; this says what $C_0$ *is*.

### (89), as the manuscript prints it

```
C_0 d_{l0} + C_1 b_1^-1 k d_{l1}
           + C_2 k^2 5 b_2^-1 ( (2/15) d_{l2} + (1/3) d_{l0} )
  = - [ (a B_1 + kappa' v_B) d_{l1} + a B_2 d_{l2} ]
```

**The right-hand side has no $\delta_{\ell0}$ entry.** The source is non-zero
at $\ell=1$ and $\ell=2$ only. So the $\ell=0$ component of (89) reads

$$C_0+\tfrac{5}{3\beta_2}k^2C_2=0,$$

and that is the *entire definition* of $C_0$: **it is the term that cancels
$C_2$'s own $\delta_{\ell0}$ leakage.** $C_2$'s coefficient multiplies both
$\delta_{\ell2}$ and $\delta_{\ell0}$; $C_0$ exists to make the $\ell=0$ line
come out to zero, which is what *"there is no monopole temperature anisotropy
in the CGI approach"* means **as an equation**.

$C_0$ and $C_2$ are therefore **one degree of freedom, not two**, and
$C_0=-\tfrac{5}{3\beta_2}k^2C_2$ is where T-60's measured
$C_0/(k^2C_2)=2.5000$ comes from — it is $5/(3\beta_2)$, a pure rational, and
nothing in the dynamics can change it.

### What (102) does with the pair

(102) --- the manuscript's `slowdecoupling` --- carries

$$\int d\eta\;\mathcal V\,e^{-(k/k_D)^2}\big\{C_0-C_1'+C_2''\big\}j_\ell .$$

**$C_0$ appears undifferentiated and $C_2$ appears as $C_2''$.** The
cancellation that *defines* $C_0$ is against $k^2C_2$, not against $C_2''$, so
the integrand takes one member of a cancelling pair and pairs it with the
second derivative of the other. For a slowly varying $C_2$, $C_2''\ll k^2C_2$,
so what is left is $C_0$ alone, larger than its intended partner by
$\sim(k/\partial_\eta)^2$.

**In the Newtonian frame the question cannot arise**, and the manuscript says
why in one sentence: *"the vanishing shear condition $\tilde\sigma_{ab}\approx0$
implies that $\tilde C_0(\eta)\approx0$ and $\tilde C_2(\eta)\approx0$"*. Both
halves vanish together. *Annals II* derives (102) for a general $u^a$ and then
**only ever evaluates it where both members of the pair are zero.**

### So the defect is not in the bundle and not in the paper

It is in the **extension**. Evaluating (102) in a frame with shear is new work
--- it is what Paper 1 is for --- and it has found the boundary of (102)'s
validity: *(102) is a specialisation whose dropped terms and whose
undifferentiated $C_0$ are both safe only where $C_0\approx C_2\approx0$.*

Measured: dropping $C_0$ from the CDM frame recovers the Newtonian answer to
**1–15%** from **53–6868×**, on all three backgrounds (T-60's table).

### A hypothesis tested and refuted, kept because it was tested

(102) is the manuscript's (93) with its last two lines dropped --- *"we can
effectively drop the last two lines of (93) except for the initial baryon
velocity contribution"*. Those lines are

$$\int(\kappa'e^{-\kappa})\big[C_1-2C_2\big]j_\ell
\quad\text{and}\quad
\int\big((\kappa')^2-\kappa''\big)e^{-\kappa}\,C_2\,j_\ell .$$

Both carry $C_1$ and $C_2$, so the obvious hypothesis was that **they are the
counterweight** and that restoring them would close the frame gap.
**They are not.** Restored, on `PLANCK_MODEL` against the Newtonian total:

| $k$ | (102) as shipped | + line 3 | + lines 3 and 4 |
|---|---|---|---|
| 1 | 0.128 | 0.196 | 1.725 |
| 20 | 72.17 | 71.49 | 71.61 |
| 140 | 1473.3 | 1474.5 | 1474.7 |
| 300 | 3686.9 | 3686.8 | 3686.8 |

Unmoved at every $k$ above 1, and *worse* at $k=1$. The frame gap is not the
dropped lines; it is the surviving $C_0$. **Recorded because a refuted
hypothesis that leaves no trace gets formed again** --- it is the same argument
`acoustic_start='z_max'` and `use_printed_c0` are kept under.

### What this does and does not license

It does **not** license deleting $C_0$ from `match_coefficients`: $C_0$ is
correct there, it is (89)'s own solution, and **B-11** is a live question about
its sign. What it licenses is a question about `integral_solution`'s
**integrand**, which is **Q14**, now answered in favour of reading (1) with a
mechanism rather than an assertion. The change belongs behind a named control,
the way every other departure in this bundle does.


---

## T-62 — the Sachs–Wolfe limit separates the frame defect from A-3, on one scalar

**Found 2026-10-18**, on a check proposed by the Paper 1 stream: on large
scales, adiabatic, matter-dominated, the covariant calculation must give
$\Delta T/T\to\tfrac13\Phi_A(0,k)$ in **either** threading. One scalar, one
limit, two backgrounds.

The quantity is $a\mathcal B_1/k$ at $\eta_*$: in the Newtonian frame that is
$(\delta\tilde T+\Phi_A)$, and in the CDM frame, where $A_a=0$, it is
$\delta T^{E}$ alone. The target is exact --- `sachs_wolfe_at_last_scattering`
reduces to $\tfrac13\Phi_A(0,k)$ at $kr_s\to0$ for any $R_*$, the $3R_*$ and
the $-R_*$ cancelling.

| background | $\Phi_A(\eta_*)/\Phi_A(0)$ | Newtonian | ratio | CDM $\delta T^E$ | ratio |
|---|---|---|---|---|---|
| CDM (Einstein–de Sitter) | $1.000000$ | $3.33331\times10^{-1}$ | $\mathbf{1.0000}$ | $2.18\times10^{-7}$ | $\mathbf{0.0000}$ |
| `PLANCK_MODEL` | $0.933264$ | $1.99860\times10^{-1}$ | $\mathbf{0.5996}$ | $-1.71542\times10^{-1}$ | $-0.5146$ |

**Two failures, and they had been reading as one.**

### The CDM threading's $\mathcal B_1$ is identically empty, and that is algebra

In Einstein–de Sitter $\mathcal H=2/\eta$ and $\Phi$ is exactly constant, so the
Euler equation $v'+\mathcal Hv=-k\Phi_A$ --- which **is** the frame condition
$\tilde A_a=0$ --- integrates by the factor $a\propto\eta^2$ to $v=-k\Phi\eta/3$,
hence $\mathcal Hv/k=-\tfrac23\Phi$. With (180)'s $\delta T=-\tfrac23\Phi_A$,

$$\delta T^{E}=\delta T-\frac{\mathcal Hv}{k}
=-\tfrac23\Phi+\tfrac23\Phi=0\qquad\textbf{identically.}$$

Measured $2.18\times10^{-7}$, which is the grid. **So in the CDM threading there
is no gravitational redshift left in $\mathcal B_1$ at all**: the whole of it
has moved into the shear sector, which is what Paper 1's Eq. (B) requires ---
$-\sigma_{ab}e^ae^b$ carries what $-A_ae^a$ carried --- and is why this frame
cannot be checked on $\mathcal B_1$ alone.

### And it re-enters at the wrong weight

Fitted $d\ln|C|/d\ln k$ at $\eta_*$ over $k=0.1\ldots30$, `PLANCK_MODEL`:

| | $C_1$ Newtonian | $C_0$ CDM | $C_2$ CDM |
|---|---|---|---|
| slope | $+0.97$ | $+2.00$ | $\mathbf{-0.00}$ |

$C_2=v/k$ is **exactly $k$-independent** --- the $k$ in $v$ cancels the $1/k$,
leaving $-\Phi\eta/3$ --- while the Newtonian $C_1$ goes as $k^{+1}$. The
gravitational content therefore sits at $k^0$ in one threading and $k^{+1}$ in
the other, so at small $k$ the CDM frame carries a finite $C_2$ where the
Newtonian $C_1$ vanishes. **Partial restoration at a different weight**, which
is a plateau deficit rather than a total loss, and which is what T-59 measured
from the far end.

### PLANCK's Newtonian $0.5996$ is **not** the frame. It is A-3.

$\Phi_A$ falls from $1.000000$ to $0.933264$ between $\eta[0]$ and $\eta_*$ ---
$6.7\%$. But $\delta T+\Phi_A$ is a **small residue of two numbers near $0.73$
and $0.93$**, so a $6.7\%$ drift in $\Phi$ becomes a $40\%$ deficit in the
Sachs–Wolfe amplitude. Einstein–de Sitter, where $\Phi$ is constant to sixteen
digits, returns $1.0000$ on the same code path.

**This is the separation the plateau question needed.** The frame question owns
the CDM column; **A-3 owns the difference between the two rows of the Newtonian
column**, and nothing in the frame sector will touch it. It also makes
Einstein–de Sitter the right background to measure A-3 on, because there the
Newtonian answer is known to be $1.0000$ and any departure is the driving
alone.

### Credit, and a note on how this was found

The check is the Paper 1 stream's, proposed in one sentence and needing no new
machinery. It is sharper than the $C_\ell$-level comparisons this bundle had
been running because it is a **single scalar at a known limit**, where those
are integrals over everything. *A quantity with one right answer beats a
tolerance on a quantity with none*, and three of the measurements this stream
made on 2026-10-17 would have been shortened by running this first.


---

## T-63 — the frame residual does not converge, so it is a defect and not a grid

**Measured 2026-10-18**, on a criterion the Paper 1 stream supplied: GDE99 (37)
makes $\tau_{A_\ell}$ **unchanged** under a first-order boost for every
$\ell>1$, so the two threadings must give *numerically identical* multipoles at
$\ell\ge2$ --- not agreement within a tolerance. **T-60**'s $1$--$15\%$
residual after $C_0$ is dropped therefore cannot be $O(\varepsilon^2)$: the
theorem is exact at the order this bundle solves.

Refining the $\eta$ grid fourfold, $C_0$ dropped, against the Newtonian scale:

| background | $n_\eta$ | $k$ | $|E_1{+}E_2-N|/|N|$ | rank-1 | rank-2 |
|---|---|---|---|---|---|
| CDM (EdS) | 8000 | 1 | $5.4870\times10^{-2}$ | $2.20\times10^{-2}$ | $3.29\times10^{-2}$ |
| | 32000 | 1 | $5.4708\times10^{-2}$ | $2.18\times10^{-2}$ | $3.29\times10^{-2}$ |
| | 8000 | 140 | $1.0631\times10^{-2}$ | | |
| | 32000 | 140 | $1.0655\times10^{-2}$ | | |
| `PLANCK_MODEL` | 8000 | 20 | $1.1059\times10^{-1}$ | $3.94\times10^{-2}$ | $7.12\times10^{-2}$ |
| | 32000 | 20 | $1.1056\times10^{-1}$ | $3.94\times10^{-2}$ | $7.11\times10^{-2}$ |

**Four times the resolution moves it by under $0.3\%$ of itself**, and at
$k=140$ it moves the wrong way. Not a grid artefact.

**And it localises to both ranks.** rank-1 and rank-2 carry the same order at
every $k$ on both backgrounds, which by the stream's own argument names
**both** $\mathcal B_1$ and $\mathcal B_2$ as entry points --- consistent with
a mis-assigned $\kappa'$, which sits in the Thomson term in $C_1$ while the
velocity it multiplies also drives the shear sector.

---

## T-64 — a diagnostic that splices two solutions measures its own kink

**Found 2026-10-18**, on the first run of **D10**, and recorded because it is
the **fifth** sampling artefact this week and the cheapest one to repeat.

D10 was to drive the oscillator twice --- once with the released frozen
$\Phi$, once with the closed-form radiation solution spliced in below equality
--- and report the ratio. On `PLANCK_MODEL` at $k=10$:

```
max |Phi_corrected / Phi_released - 1|  =  1.266e-03
delta_T(eta_*)   released  -7.505929e-01
                 corrected +1.189578e+00
```

**A sign flip on a $0.13\%$ input.** The oscillator is driven by $\Phi$ *and
its derivative*; the acoustic grid carries **three points** below
$\eta_{\rm eq}$ at that $k$; and a splice across three points is a step in
$\Phi'$. The response is to the kink.

**An earlier draft was worse and the control caught it in one run.** It spliced
at the grid reference rather than at equality --- which on `PLANCK_MODEL` is
*after* equality, $\eta[0]=0.0333$ against $\eta_{\rm eq}=0.0195$ --- and
applied the radiation solution on `CDM_MODEL`, which has $\Omega_r=0$ and no
radiation era at all. The control moved by factors of **7 to 10** where A-3 is
identically zero. It now reads $1.0000$ at every $k$, **by construction rather
than by a branch**: `matter_domination_eta` returns 0 at $\Omega_r=0$, so
nothing lies below the splice and the decay factor is $\Phi_{\rm rad}(0)=1$.

**What D10 does instead.** It reports the scoping and stops: which modes have a
radiation era to see, what fraction of their span lies in it, how far $\Phi$
has fallen by equality, and **how many grid points lie below it**. Driving
through a resolved radiation era is A-3's *fix*, needing a grid derived for
that era rather than for the acoustic one, and is not its measurement.

### The lesson, and it is the week's

Five artefacts in four days --- the $k$ grid below Nyquist (**T-56**), a
pointwise ratio reading distance-to-zero as error (**Q12**), an envelope read
off a window that contained no extremum, a seam read off a function's own
slope, and now a splice read as physics. Every one was a **measurement of the
sampling**, and every one looked like a result.

What separated them was not care. It was whether a *control with a known
answer* was in the same run. The two that were caught immediately --- the
$\Omega_r=0$ control here, and T-62's Einstein--de Sitter $1.0000$ --- had one.
The three that cost hours did not. **A tolerance on a quantity with no right
answer cannot fail usefully**, and that is now the standing argument for
building the control first.


---

## T-65 — `fig:bulk` is on the right side of T-57, and the control says what it would have cost

**Measured 2026-10-18**, closing a question Coordination raised about a paper
under review. `outputs/line-of-sight-field.csv` is what Paper 1's `fig:bulk` is
drawn from, and `scripts/emit_handover_fields.py` builds it as

```python
source = source_doppler(history, scattering, RAY_K_COM, weight=opacity) \
       + source_integrated(history, scattering, RAY_K_COM, aH=aH, weight=opacity)
```

with `source_primary` **never called** --- correctly, since the primary term is
a boundary term at $\eta_*$ and `fig:bulk` is a statement about the bulk.

### The control, run on the released script

Not on a rebuild. **The first attempt rebuilt the ray by hand and did not
reproduce the released file** --- the endpoint agreed to four digits and the
running excursion did not --- so none of its numbers were evidence and they
were discarded. This monkeypatches one thing per trial, calls
`emit_handover_fields.main()` itself, and diffs the CSV the script writes. The
released file is regenerated unpatched at the end and reproduces
`endpoint = -1.088150e+00`, `excursion = 2.2172e-01` exactly.

| perturbation | integrand, $|\Delta|/$scale | integrand **shape** | running **shape** | endpoint |
|---|---|---|---|---|
| $\kappa'\times1.01$ | $1.001\times10^{-2}$ | $2.91\times10^{-4}$ | $1.81\times10^{-3}$ | $\times1.008$ |
| weight $\to\mathcal V$ (**T-57**) | $3.009\times10^{2}$ | $0.491$ | $0.392$ | $\times197$ |

**The file is not unmoved, and the two rows say different things.**

A 1% change in $\kappa'$ moves the amplitude by 1.0% and the **shape by
0.03%** --- very nearly a pure rescale, so `fig:bulk`'s structural claim is
insensitive to a $\kappa'$ rescaling even though the field is linear in it.

The T-57 weight substitution moves the amplitude by **301$\times$**, the
endpoint by **197$\times$**, and the **shape by 49%**. That is not a rescale.
It would be a different figure.

### And it does not apply, because this caller named its weight

`emit_handover_fields.py` passes `weight=opacity` **explicitly**, on both
source terms. It is one of the callers that complied with approximation
**A-1**'s rule --- *"the caller states which"* --- all along, which is exactly
what the eight `two_frame` callers of T-57 did not do.

**So `fig:bulk` is on the correct weighting and the finding does not reach the
paper.** The control is worth keeping anyway: it prices what the defect would
have cost had this path defaulted like the others, and it is the difference
between asserting that and knowing it.

### A note on the instrument

The useful column is the **shape**, not the amplitude, and the first version of
this control reported only the amplitude. Under $\kappa'\times1.01$ that reads
"MOVES" and says nothing; the shape column separates *the figure's amplitude
moved* from *the figure's claim moved*, which for a paper under review is the
entire question. That is **D5's distinction** --- the normalised shape gap ---
applied to a different artefact.

---

## T-66 — the dipole conversion that was never written

**2026-10-18. Five instances, one defect, one per route. Landed.**

`solve_acoustic` returns the photon dipole in the **velocity** normalisation.
Three independent confirmations, all in the code rather than in the reading:
(152) is integrated with $k$ on *both* source terms,
$-k\delta T/(1+R)-k\Phi_A$; (153) carries $+(k/3)\tau_1$; and the
heavily-loaded limit $\tau_1'+\mathcal H\tau_1=-k\Phi_A$ is **identical** to
`cdm_frame_velocity_equation` for $v$. So $\tau_1=v_B$, un-reduced.

Everything from (89) down assumes the **reduced** dipole
$\tilde v_B=\tilde\tau_1=v_B/k$. `newtonian_coefficients` multiplies its `v_b`
by $k$ to rebuild (89)'s $\kappa'v_B$; (107) takes the derivative of the
*un*-multiplied one, which is **T-25**. **T-25 got the derivative right under
a convention the oscillator never honoured.** No conversion existed anywhere
between the two, and five call sites each wrote `v_b=tau_1` in their own line.

### The measurement

At $\eta_*$ on Einstein--de Sitter, where $\Omega_r=0$ and **A-3** is
identically zero, so nothing here is radiation driving. The Doppler piece of
the Newtonian primary against its temperature piece:

| $k$ | $(\delta T+\Phi_A)(\eta_*)$ | $\kappa'\tau_1$ as released | $\kappa'\tau_1/k$ per (90) | ratio |
|---:|---:|---:|---:|---:|
| 10 | $3.183\times10^{-1}$ | $-5.916\times10^{1}$ | $-5.916\times10^{0}$ | 10.0 |
| 50 | $-2.038\times10^{-2}$ | $-2.316\times10^{2}$ | $-4.632\times10^{0}$ | 50.0 |
| 200 | $-1.245\times10^{-1}$ | $-4.935\times10^{1}$ | $-2.468\times10^{-1}$ | 200.0 |
| 400 | $-8.277\times10^{-2}$ | $-1.595\times10^{1}$ | $-3.987\times10^{-2}$ | 400.0 |
| 600 | $-5.675\times10^{-2}$ | $-8.376\times10^{0}$ | $-1.396\times10^{-2}$ | 600.0 |

**The arbiter is the physics, not a tolerance.** Doppler and Sachs--Wolfe are
the same order at the acoustic scales or the oscillator is not an oscillator.
Released, the ratio is **397$\times$ at $k=200$** and **193$\times$ at
$k=400$**; under (90) it is **1.92** and **0.47**. A ratio that scales exactly
as $k$ is a power of $k$, not an error bar.

### What it does to the spectrum, and the negative result

EdS, Newtonian, $K_{\max}=900$, 1668 modes, $n_\eta=8000$, opacity weight.
$\ell_A=192.8$, so $\cos(kr_s)$ peaks at 193, 386, 578.

| $\ell$ | released | T-66 |
|---:|---:|---:|
| 2 | 1.3126 | 1.7135 |
| 100 | 1.0609 | 0.5278 |
| 200 | 0.6494 | 0.1637 |
| 300 | 1.0662 | 0.0617 |
| 400 | 1.0554 | 0.0257 |
| 600 | 0.5417 | 0.0056 |
| 800 | 0.4098 | 0.0016 |

```
  released   max over l>100 = 1.2398 at l = 360
  T-66       max over l>100 = 0.4107 at l = 120
```

**The released $\ell\approx360$ maximum was the $\kappa'\tau_1$ contamination,
not a weak acoustic peak.** The earlier framing --- *"peaks roughly 4$\times$
too weak"* --- was wrong in the way that matters: there were no peaks to be
weak. T-66 **removes a spurious signal; it does not supply a missing one**, and
it is correct independently of that, because it is settled by (90)'s own
dimensional content.

### The five instances

`newtonian_set`, `cdm_set`, `pipeline.run`, `two_route` (both halves) and
`emit_handover_fields`. Each reached the dipole through its own line, which is
**why no comparison among them could see it** --- T-3's lesson, now in
quintuplicate. `reduce_dipole` is the single conversion point, so the
convention is stated once rather than assumed six times.

`DIPOLE_NORMALISATION="reduced"` restores the released behaviour as a control,
the way `acoustic_start='z_max'` keeps the pre-T-51 grid.

### The frame change, and two readings that are both right

`FrameShift.dipole_shift` returns $-v/k$ and its reasoning is **correct**: a
*reduced* dipole shifts by $-v/k$. What was missing is that the object it was
applied to was not reduced. `velocity_shift` is the $-v$ an un-reduced dipole
takes, and `to_frame` now gives `tau_1` the first and `v_b` the second.

P1-T \S3.2 (*"the boost is $-v$"*) and the external review (*"$-v/k$ is the
correct boost for the reduced dipole"*) are **both right, about different
objects**. The released code applied the reduced boost to the un-reduced
quantity. This also withdraws P1-B's earlier "worry 2 is settled" measurement
(degradation 11$\times$/131$\times$/202$\times$): that compared `tau_1 - v/k`
against `tau_1 - v` in `FrameShift` and was aimed at the wrong object. It does
not bear on T-66.

### Attribution

Converged on independently by three streams: P1-B's measurement above; P1-T
\S3.3, withdrawing its own acceptance of T-27 (*"available in principle, not in
force"*); and the external review, narrowing to *"the assembly passes the
oscillator output directly into the reduced-dipole coefficient machinery; I did
not find a conversion between those equations."*

### Blast radius

307 physics tests pass. One moved and is recorded in place:
`test_102_must_carry_the_visibility_and_substituting_the_opacity_wrecks_it`'s
printed-weight rank share goes 0.47--0.62% to 0.22%, 0.11%, 0.71%, **5.19%**
over $\ell=2,5,10,20$. Rank 1 got smaller and nothing else changed, so the
rank-0/2 share rises; the threshold moves **with the measurement recorded**,
and the control half --- which must invert --- is untouched and still does.

---

## T-67 — (106)'s expansion terms double-count in comoving $k$. **OPEN**

**2026-10-18. Measured, implemented behind a switch, default unchanged.**

(106) carries $-a^2H\tilde{\mathcal B}_1-2Hak\Phi_A$. Those are the
product-rule terms for **physical** $k$ with a varying $a$. This bundle is
comoving-$k$ throughout and $a\tilde{\mathcal B}_1=k_{\rm com}(\delta\tilde
T+\Phi_A)$ carries no $a$ at all, so in a comoving-$k$ implementation they
double-count. That is **P1-T \S6.4's test**, and it returns a **C3.1
violation**:

| $k$ | med $\lvert$released$/dC_1\rvert$ | med $\lvert$comoving$/dC_1\rvert$ | max rel err |
|---:|---:|---:|---:|
| 20 | 5.2736 | **1.000004** | $8.5\times10^{-4}$ |
| 50 | 1.2270 | **0.999998** | $8.3\times10^{-4}$ |
| 150 | 0.5620 | **1.000001** | $3.4\times10^{-3}$ |
| 400 | 0.5310 | **1.000004** | $2.2\times10^{-2}$ |
| 600 | 0.4951 | **1.000172** | $3.6\times10^{-2}$ |

Scattering off throughout, so T-66's contamination cannot enter. The residual
at high $k$ is spline error on a fast oscillation and falls with $k$.

Dropping the pair makes the supplied $\tilde C_1'$ **exactly** the derivative
of the $\tilde C_1$ the code constructs; as released it is wrong by factors of
**2--5 across the whole band**. The structural argument needs no reading of the
source: (102)'s boundary carries $C_1(\eta_*)$ and its integrand carries
$C_1'$, so if those are not one object's value and derivative then (102) is not
a by-parts of anything.

**T-23's defence does not reach this and is hereby narrowed.** T-23 is about
mode-expanding $\mathcal D_{\langle a}\dot{\mathcal B}_{b\rangle}$, where a
tensor index is carried through a derivative. By the time (102) is evaluated,
$C_1$ is a **scalar** mode coefficient and there is no tensor left to commute.

**The default stays `A_B1_PRIME_EXPANSION_TERMS=True`, (106) as printed**, for
two reasons that are not timidity. P1-T owns the algebra and has been asked to
confirm against (105)/(106) in `cbrII.tex` that $a\tilde{\mathcal B}_1$
carrying a different $a$-dependence is excluded. And P1-T \S6.2 is right that a
by-parts identity cannot be *judged* until item (iii) is settled, so flipping
this on the spectrum would be the error T-3 warns about. **The switch exists so
that the decision costs one word when it is P1-B's to make.**

Measured with the switch flipped, on EdS: `max over l>100 = 1.0846 at l = 120`
and `D_2/D_30 = 0.0901`. The quadrupole collapse is **not** evidence against
T-67 for the reason above.

### The sign hazard, confirmed

`decoupling.py` builds `kappa = forward[-1] - forward`, so $\kappa(\eta_0)=0$
and $d\kappa/d\eta=-\,$`kappa_prime`. Therefore
$W'=\mathrm d(e^{-\kappa})/\mathrm d\eta=+\kappa'e^{-\kappa}=+\mathcal V$,
**positive**. The stored `kappa_prime` is the scattering **rate**, not the
derivative of the optical-depth array. Raised independently by P1-T \S5.4 and
by the external review's claim 4; both are right, and the by-parts expansion
$WC_0-(WC_1)'+(WC_2)''=W(C_0-C_1'+C_2'')-\mathcal VC_1+2\mathcal VC_2'
+\dot{\mathcal V}C_2$ carries that sign.

---

## T-68 — the bulk integral buries the peaks, and A-2 rests on a measurement T-66 invalidated

**2026-10-19. Measured on Einstein--de Sitter, post-T-66. The mechanism of the
acoustic peak deficit, found at last.**

### The oscillation exists at last scattering

$(\delta T+\Phi_A)(\eta_*)$ tracks $\cos(kr_s)$ in **exact phase and period**.

> **Corrected 2026-10-19, same day.** This paragraph first read *"amplitude
> $0.565$ on an offset of $-0.295$ --- a contrast better than the closed form
> (181)'s $0.935/{-0.605}$."* **Both numbers were wrong and the conclusion was
> backwards.** They were read by eye off a $\Delta k=20$ print-out rather than
> computed. Measured properly over $k=40\ldots410$ in steps of 10:
>
> | | amplitude | offset | $\lvert$amp/offset$\rvert$ |
> |---|---|---|---|
> | solved $(\delta T+\Phi_A)(\eta_*)$ | 0.4698 | $-0.3890$ | 1.208 |
> | closed form (181) | 0.9365 | $-0.6041$ | 1.550 |
>
> **The solved oscillation amplitude is 1.99$\times$ too small and its contrast
> is 22% worse, not better.** Neither $(1/3)(1+3R_*)=0.937$ nor the WKB
> $(1/3)(1+R_*)^{-1/4}=0.296$ reproduces $0.4698$, so the solver is not
> obviously either form and the disagreement is open --- **two routes in this
> bundle to the same quantity differ by a factor of two**, which is a T-3
> finding in its own right and is tracked as such.
>
> *Process note.* Two arithmetic slips in one day, both from reading a coarse
> table by eye instead of computing the summary statistic. That is **V4**'s
> neighbour: not comparing across stages, but comparing across *samplings*.
> Any amplitude/offset pair quoted in this bundle is now computed, never read. $r_s(\eta_*)=0.03164$,
$r_\theta=1.9404$, $\ell_A=\pi r_\theta/r_s=192.7$. **So the peaks are created
correctly and destroyed in projection.**

### Which half destroys them

(102) has two pieces in the Newtonian frame and `IntegralSolution` keeps them
apart, so one pass separates them. EdS, T-66 landed, T-67 default, $T(k)$ off:

| $\ell$ | boundary | bulk | total |
|---:|---:|---:|---:|
| 100 | 0.5175 | 0.9127 | 0.8474 |
| 200 | 0.0577 | 0.4726 | 0.4546 |
| 400 | 0.0216 | 0.1588 | 0.1558 |
| 580 | 0.0091 | 0.0653 | 0.0634 |

```
  boundary  interior maxima above l=100: [460]
  bulk      interior maxima above l=100: NONE
  total     interior maxima above l=100: NONE
```

**The boundary carries acoustic structure. The bulk has none at all, is
perfectly monotonic, and is 7--8$\times$ larger across the whole acoustic
band.** The peaks are not weak; they are buried.

**And on this background the bulk should be nearly empty.** EdS has
$\Omega_r=0$ and T-52 measures $\Phi_A=1.0$ to $10^{-13}$, so
$\Phi_A'=\Phi_H'=0$ and the true integrated Sachs--Wolfe effect is
**identically zero**. A term that should vanish is dominating. What fills it is
$W=e^{-\kappa}\to1$ running over the entire line of sight against a $\tau_1$
frozen past $6\eta_*$ --- that is **approximation A-2**, plus T-67's disputed
expansion terms, which on EdS *are* the rest of the integrand.

### The printed weight restores them

The same run with (102)'s printed $\mathcal V$ on the bulk:

| $\ell$ | boundary | bulk | total |
|---:|---:|---:|---:|
| 2 | 1.3952 | 1.4467 | 1.4469 |
| 200 | 0.0577 | 0.0262 | 0.0261 |
| 460 | --- | --- | *interior maximum* |

```
  total  D_2/D_30 = 1.4469   interior maxima above l=100: [320, 460, 700]
```

**Acoustic structure appears, and the Sachs--Wolfe plateau survives.**

### Why this reopens A-2

`SOURCE-APPROXIMATIONS-v1.md` records A-2's basis: weighting the integrated
sources with $\mathcal V$ *"gives $D_\ell\propto\ell^2$ --- there is no
Sachs--Wolfe plateau at all"*, measured as a rise from $\ell=2$ to 30 of
**80.5$\times$** against 8.17$\times$ for $e^{-\kappa}$. That measurement was
made **before T-66**, when $\kappa'\tilde v_B$ was too large by $k_{\rm com}$
--- and the object that destroyed the plateau is exactly
$\mathcal V\kappa'\sim\kappa'^2e^{-\kappa}$, which P1-T \S5.2 flags and which
**T-66 has now divided by $k$**.

Post-T-66 the printed weight gives $D_2/D_{30}=1.4469$: a **flat plateau**, not
$\ell^2$.

> **A-2 is a released departure from the antecedent resting on a measurement
> that T-66 invalidated.** It must be re-measured on all three backgrounds
> before any further conclusion is drawn from a spectrum. This is T-3's lesson
> arriving from a new direction: a *decision* taken from a measurement is only
> as good as the measurement, and nothing in the bundle re-checks a decision
> when its evidence moves.

### What is **not** claimed

The peak **positions** (320, 460, 700 against $\ell_A$, $2\ell_A$,
$3\ell_A=193$, 386, 578) and the high-$\ell$ **amplitude** (still orders below
CAMB) are **both still wrong**. T-68 identifies the mechanism that was hiding
the oscillation; it does not claim a correct spectrum. Those are the next
questions and they are separable now that there is structure to measure.

### Also retired here

$T(k)$ --- Appendix J, **T-37** --- is a *radiation-era* transfer function and
is applied on `CDM_MODEL`, which carries $\Omega_r=0$ and has no radiation era
at all. It suppresses $k=600$ to $0.273\times$ of $k=100$, a factor of 13 in
power at the third peak. It is A-3's mirror image: **A-3 omits radiation
driving, which would raise the peaks; $T(k)$ applies radiation suppression,
which lowers them.** On Einstein--de Sitter neither belongs, and the EdS
*control* has carried this contaminant throughout. Measured with it off, high
$\ell$ rises by 6--15$\times$. Raised independently in the external review.

---

## T-69 — A-2's basis is void, re-measured on all three backgrounds

**2026-10-19.** Full table and the amendment in place in
`SOURCE-APPROXIMATIONS-v1.md`. Summary: the $\mathcal V$ row that justified
departing from (178) went $4.29\to1212$ pre-T-66 and goes $0.371\to0.008$
post-T-66 --- the trend **reversed**, not merely shrank. $\mathcal V$ gives
acoustic interior maxima on **3 of 3** backgrounds; $e^{-\kappa}$ on **0 of 3**.

**The governance finding is the one that generalises.** A-2's own closing
paragraph named the defect that would invalidate it --- *"it is possible that
(178) is consistent under a reading of $\tilde v_B$ that differs from the
$\tilde v_B=\tilde\tau_1$ used here"* --- thirteen days before T-66 found
exactly that, and the decision stood on the measurement regardless.

> **Nothing in this bundle re-checks a decision when its evidence moves.**
> Every approximation in `SOURCE-APPROXIMATIONS-v1.md` is a decision taken
> from a measurement at a stated stage. A finding that changes that stage
> should re-open every decision that rests on it, and no mechanism does that.
> A-1, A-3 and A-4 have not been re-measured post-T-66 either.

Method note, against **V4**: both weights were computed from **one** acoustic
solve per $k$ --- the weight enters only at `integral_solution` --- so the two
rows differ by the weight and by nothing else. Running them separately would
have been two integrations of the same dynamics, which is the difference T-3
warns about.

---

## T-70 — a gate whose denominator collapsed

**2026-10-19.** `test_two_frame_is_gated` went red at $k=1$ after T-67, at
$2.27\times10^{-2}$ against a $10^{-2}$ gate. **It is not a new disagreement.**

| T-67 | absolute gap | row scale | relative |
|---|---|---|---|
| on (as printed) | $2.6345\times10^{-3}$ | 2.8150 | $9.36\times10^{-4}$ |
| off (comoving) | $2.6362\times10^{-3}$ | 0.1159 | $2.27\times10^{-2}$ |

**The absolute gap is unchanged to four figures.** T-67 removes the dominant
term at low $k$, collapsing the row scale by **24$\times$**, and the ratio grew
entirely through its denominator. That is **D5's distinction** --- normalised
shape gap against absolute amplitude --- arriving in a gate rather than in a
figure: *a ratio whose denominator collapses is not measuring agreement any
more.* `ABSOLUTE_GATE` is now checked beside the relative one.

---

## T-71 — T-67 flipped, and where the peaks actually are

**2026-10-19. P1-T supplied the confirmation T-67 was gated on.**
`cbrII.tex` lines 540--541, verbatim: *"corresponding to a wavenumber $k$. The
physical wavenumber is defined by $k_{phys}(t)=k/a(t)$."* **Annals II's $k$ is
comoving**, in its own text. Paper 1's **C3.1** declares $k$ *physical*,
$\dot k=-\mathcal Hk$. One symbol, opposite conventions, two documents, neither
saying so. So $a\tilde{\mathcal B}_1=k_{\rm com}(\delta\tilde T+\Phi_A)$ carries
no scale factor, $\dot k=0$, and (106)'s two terms cannot arise from either
product rule. **Default flipped; `True` retained as the control.**

**The same term appears in both routes under two printed forms** --- (106)'s
$-a^2H\tilde{\mathcal B}_1-2Hak\Phi_A$ is (179)'s $-aH(\delta\tilde T+3\Phi_A)$
times $-k$ --- so `source_integrated` gained `expansion_terms` and the gate
caught the mismatch within one test run. Two transcription tests now state
`expansion_terms=True` to pin (179) **as printed**; they are marked
`transcription` under Coordination's split and are correct to fail against the
released default.

### Peak positions, against a known-answer control

The projection machinery was cleared first: a synthetic $\cos(kr_s)$ fed
through the bundle's own kernel and `cl_covariant_route` gives maxima at
**172, 360, 552, 744** --- spacing $\simeq\ell_A$ --- and a $\sin(kr_s)$
control at **76, 264, 456, 648**, offset by $\ell_A/2$ exactly as it must be.
**The kernel is sound and uses comoving $k$ with conformal $\Delta\eta$**
(`integral_solution`: `x = k_com * (eta_0 - eta)`), which is what Annals II's
own convention requires --- so P1-T's proposed kernel-argument run is a no-op
here and the varying-$a$ mechanism is **excluded**.

Following P1-T: peaks located in the **oscillatory residual**, not the total
(degree-4 log-log fit divided out; a quartic over 2.5 decades cannot
manufacture three maxima). EdS, $\mathcal V$ weight, $T(k)$ off:

| | residual maxima |
|---|---|
| synthetic control, measured contrast | 196, 544 |
| boundary only | 164, 468 |
| total | 176, 476 |

**Boundary and total now agree** --- post-T-67 the bulk no longer drags the
located maxima, which was P1-T's concern and T-68's mechanism.

The residual maxima sit at $0.898$ and $0.875$ of the control's. **That
compression is roughly uniform**, and by P1-T's own discriminator a uniform
rescale is $r_s$ or a constant $r_\theta$ --- *not* the varying-$a$ kernel,
which is independently excluded above. **A $\simeq12\%$ constant in the sound
horizon or the angular-diameter distance is the next thing to measure.**

### Not claimed

Only two maxima resolve in the residual where three were sought; the degree-4
fit may be absorbing one. The synthetic control carries no damping and no
envelope, so the comparison is indicative rather than exact. And the solved
oscillation amplitude is still $1.99\times$ below the closed form (T-68, as
corrected), which is a separate open disagreement between two of this bundle's
own routes.

### Frame invariance moved

`test_T14_the_transfer_function_is_NOT_frame_invariant_under_177_to_179`
pinned *near-total collapse*, $0.9<r<1.05$. It now measures **0.604 at
$\ell=2$**. Both T-66 and T-67 sit in the rank-one source that gap is a gap in.
Re-pinned to what is measured, not to what is wanted: P1-T's acceptance
criterion is a theorem --- identical multipoles at every $\ell\ge2$ --- so the
target is **0**, and 0.604 is progress, not arrival.

### A locator rule, adopted

P1-T: cite Paper 1 by **label** (`eq:resN`, `eq:resC`), never by printed
number --- (83)/(84) today, different at v1.0.x, and the table reference
already differs between the GRG and arXiv lines. Adopted. This bundle's
Annals II numbers stay as they are, because they are **generated** from the
accepted source's own `.aux` rather than read off a PDF.

---

## T-72 — the rank-two by-parts slot, implemented and measured. **Not the carrier.**

**2026-10-19.** The exact bulk source of $\int W[C_0K+C_1K'+C_2K'']$ is
$W(C_0-C_1'+C_2'')-\mathcal VC_1+2\mathcal VC_2'+\dot{\mathcal V}C_2$ (P1-T
\S2.1, verified by direct quadrature to $10^{-11}$--$10^{-15}$). (102) carries
only the first group. $-\mathcal VC_1$ collapses to the primary under
$\int\mathcal V=1$ --- Annals II's own `visibe` step, already carried as the
boundary. The other two are **rank two**: identically zero in the Newtonian
frame, which is why Annals II never needed them, having specialised at \S7.1.1
*before* writing its sources.

Implemented behind `by_parts_weight_terms`, **default off**. Measured frame gap
on EdS: $1.2847\to1.3157$ at $k=10$, $1.5642\to1.7239$ at $k=60$ ---
**slightly worse, not better.** Default stays off until the pairing question
below is settled; adding exact terms to a wrong pairing is not obviously right.

---

## T-73 — the frame mismatch is real, and it is none of the things we suspected

**2026-10-19. The PI's hypothesis, tested.** *"We have the physics right before
decoupling but it is not correctly projected in free streaming... the problem
might be the frame mechanics, and that is not entirely in Annals II."*

### What it is not

| candidate | result |
|---|---|
| $C_0$'s monopole-row normalisation (P2-T \S4, ratio 7.5) | scaling $C_0$ by $2/15$ moves the gap $1.2847\to1.2825$ at $k=10$. **Not the carrier.** |
| the rank-two by-parts terms (T-72) | $1.2847\to1.3157$. **Not the carrier.** |
| the projection kernel | synthetic $\cos(kr_s)$ gives maxima at 172, 360, 552, 744, spacing $\simeq\ell_A$; $\sin$ control offset by $\ell_A/2$. **Sound**, and already comoving $k$ with conformal $\Delta\eta$. |
| anything acting per multipole | the gap is **$\ell$-independent**: 1.0003 at every $\ell$ for $k=1$; 1.2847 at every $\ell$ for $k=10$; $\simeq1.6$ for $k=60$. |

**Control throughout: the Newtonian column moves by exactly $0.000\times10^{0}$
under every $C_0$ rescaling**, as it must, $C_0$ being identically zero there.

### What is *correct*, measured

**P1-T's \S6.3 gate passes.** The invariant combination
$(\delta T+\Phi_A)-C_2'$ comes out **identical in the two threadings to every
printed digit**, at $k=1,10,60,300$ and at $\eta_*,2\eta_*,8\eta_*$ --- and
equals $\Phi/3=0.33333$ to $2\times10^{-4}$ exactly where it should, in the
super-horizon limit ($k=1$ at $\eta_*$). It departs from $\Phi/3$ once
$kr_s\gtrsim1$, which **is the acoustic oscillation, not a defect**.

> **So the frame transformation is right and the invariant is preserved.**

### Where that leaves it

The same physics sits in **$C_1$** in the Newtonian threading and in
**$C_2'$** in the CDM one --- $\Phi_A^E=0$ and $\delta T_E\equiv0$ by
construction and T-62, so the CDM column has no rank-one source at all and
everything must arrive through $C_2$. (102)'s bulk then takes $-C_1'$ against
$+C_2''$, and its boundary $-C_1(\eta_*)$ against $+C_2'(\eta_*)$.

**For the two frames to agree, that pairing must be exact, and P1-T \S1.3 says
it is not:** *"the weight is $k^{-2}$ on $\sigma_{ab}$, i.e. $k^0$ on $C_2$ ---
the same weight as the rank-1 potential. $C_2''$ is not the pairing; it is one
derivative too many, since nothing at rank 1 changes by $\ddot w/k$."*

**That is the open item**, and it is where the PI's instinct pointed: the
defect is in how (102) *consumes* the coefficients across ranks, not in the
frame transformation, not in the sources, and not in the projection.

### And it is new, which is why it was never found

Annals II specialises to the Newtonian frame at \S7.1.1 **before** it writes
its sources, so (110), (111) and (176)--(181) carry $\tilde C_1$ alone and the
rank-two slots of (102) are **never evaluated anywhere in the antecedent**.
This bundle carries a generic $u^a$ through (102) and specialises at the end.
*It is the first thing to evaluate those slots at all.* A defect in them could
not have been found by reproducing Annals II, only by departing from it in the
direction the bundle departed.

### The ISW question, answered

The PI asked where the ISW went. **A-1 answers it, and the T-69 flip made it
binding.** $\mathcal V=\kappa'e^{-\kappa}$ is a sharp spike at recombination
and is zero to many decimal places by $z\lesssim1$, which is exactly where a
late ISW from $\Lambda$ accumulates --- A-1's own words: ***"Annals II's
expression cannot carry a late-ISW."*** It cost Annals II nothing because
\S8.3.2's model is standard CDM with no $\Lambda$. Flipping A-2 back to the
printed weight restores the acoustic structure **and gives up the late ISW on
$\Lambda$CDM and PLANCK**. On Einstein--de Sitter there is none to lose.

### The plateau is **not** resolved

Normalised at $\ell=2$ on EdS with $\mathcal V$: $D_5/D_2=0.371$,
$D_{10}=0.405$, $D_{20}=0.604$. A Sachs--Wolfe plateau is flat in $D_\ell$;
this is a factor $2.7$ dip at $\ell=5$ recovering by $\ell=20$. Under
$e^{-\kappa}$: $0.779,0.654,0.601$ --- monotone, also not flat. **Both weights
put too much power at $\ell=2$ relative to $5\le\ell\le30$**, and that is a
separate open defect from the peaks.

---

## T-74 — the ISW is not what deletes the low-$\ell$ power, and the frame gap is immune to (102)

**2026-10-19. Two of P1-T's four ledger items refuted by their own controls.**

### Item 1: $\mathcal V$ does **not** delete an ISW

P1-T: *"$\mathcal V=0$ after recombination and $e^{-\kappa}=1$. Weighting the
integrated group with $\mathcal V$ deletes the integrated Sachs--Wolfe term
outright. That is the missing low-$\ell$ power... in EdS, $\Phi$ is constant,
so there is no late ISW to delete... Every frame and weight test run so far has
been blind to this row."*

**The test they asked for, with their own control.** $D_\ell/D_{30}$ ---
*not* normalised at $\ell=2$, because that hides the quantity under test:

| background | weight | $\ell=2$ | 3 | 5 | 10 | 30 | 100 |
|---|---|---|---|---|---|---|---|
| **EdS (control, $\Phi$ const)** | $\mathcal V$ | 1.437 | 1.342 | 0.526 | 0.626 | 1.000 | 0.471 |
| **EdS (control)** | $e^{-\kappa}$ | 0.086 | 0.124 | 0.197 | 0.376 | 1.000 | 1.646 |
| $\Lambda$CDM | $\mathcal V$ | 1.440 | 1.356 | 0.594 | 0.714 | 1.000 | 0.382 |
| $\Lambda$CDM | $e^{-\kappa}$ | 0.094 | 0.134 | 0.210 | 0.392 | 1.000 | 1.485 |
| PLANCK | $\mathcal V$ | 1.612 | 1.542 | 1.387 | 0.342 | 1.000 | 0.750 |
| PLANCK | $e^{-\kappa}$ | 0.096 | 0.135 | 0.210 | 0.388 | 1.000 | 1.588 |

**Ratio $e^{-\kappa}/\mathcal V$ at $\ell=2$: EdS 0.060, $\Lambda$CDM 0.065,
PLANCK 0.060.** The three agree to a few percent --- **including the control
with no ISW in it at all.**

> **If the difference were the ISW, EdS would show none.** It shows the same
> factor of sixteen as the two $\Lambda$ backgrounds. The weight difference at
> low $\ell$ is **not** the integrated Sachs--Wolfe term.

What $e^{-\kappa}$ actually produces on EdS is a monotone rise,
$0.086\to1.000\to1.646$, on a background where $\Phi_A'=\Phi_H'=0$ exactly, so
**there is no gravitational integrand at all**. It is the frozen $\tau_1$
Doppler term running the whole line of sight under $W\to1$ --- **T-68's
mechanism, confirmed on a new axis**, and it is what A-2 originally described
before T-66 reversed the trend.

**Also measured and separately deficient:** neither weight produces a
detectable late ISW. PLANCK's $\ell=2$ exceeds EdS's by 12% under $\mathcal V$;
$\Lambda$CDM's by 0.2%. **A real late ISW is a factor, not a few percent.** The
bundle does not carry one, and the reason is *not* the weight. That is a
separate open defect and it is now named.

**Consequence for the A-2 flip (T-69): it stands.** P1-T asked for the weight
to be changed inside item (iii) and for no switch. The premise does not
survive its own control, so the change is not made. The switch stays because
it is how this bundle measures, not a configuration option offered to a reader.

### Item 3: refuted on the number P1-T themselves named

*"Compute $r_s$ and $r_\theta$ from the background the code actually
integrates and compare $\ell_A$ to the control's."* Done. EdS:
$r_s=0.031641$, $r_\theta=1.9404$, $\ell_A=192.7$ --- **the same values the
synthetic control used**, so there is no discrepancy in the tabulated
quantities. And the *solver's* effective sound horizon, fitted from the
extrema of $(\delta T+\Phi_A)(\eta_*)$ over $k=20\ldots700$, is
$0.032289$ --- a ratio of **1.0205**, and the series $201,302,400,500,599$
matches $n\times99.3$ to $\simeq1\%$ once the spurious first extremum at
$k=117$ ($n\simeq1.18$, not 1) is dropped. **2%, not the 11% the
$\sqrt{(1+R)/(1+R/2)}$ mechanism requires.** The numerical coincidence
($1.1099$ against an apparent $1.1287$) is real and is not this.

### The frame gap is immune to every term in (102)

Eleven candidates, each measured, **each with the control that the Newtonian
column must not move** --- it never did, to $10^{-14}$:

| candidate | gap at $k=10$, EdS |
|---|---|
| released | 1.2847 |
| $C_0\times2/15$ (P2-T \S4) | 1.2825 |
| rank-2 by-parts terms (T-72) | 1.3157 |
| $\gamma=0$: drop $C_0$ from the bulk (P1-T) | 1.2824 |
| $\beta=-\alpha$: flip $C_2''$ (P1-T) | 1.2847 |
| both, P1-T's full prescription | 1.2824 |
| $-C_2'(\eta_*)$ at the boundary | 1.2846 |
| shear boundary zeroed | 1.2843 |
| Thomson term $\kappa'\tilde v_B$ zeroed | 1.2846 |
| $\mathcal V$ against $e^{-\kappa}$ on the bulk | unchanged in the gap |
| projection kernel | verified sound against a synthetic known answer |

**P1-T's rank-2 derivation does not close it**, and at $k=60$ their full
prescription is *worse*: $1.5642\to1.9112$. $\beta=-\alpha$ is numerically a
no-op on EdS, which says the $C_2''$ slot carries essentially nothing there.

### Where that leaves the frame question

P1-T's \S6.3 gate **passes exactly** --- the invariant
$(\delta T+\Phi_A)-C_2'$ is identical in both threadings to every printed
digit. The invariant is preserved and the transfer is not, and **no
rearrangement of (102) reconciles them.** The gap is $\ell$-independent, order
one, and immune to every slot, boundary and weight the equation has.

> **So the defect is upstream of (102), in how the CDM coefficient set is
> built --- not in how (102) consumes it.** That is where the next work goes,
> and it narrows the search from an equation to a constructor.

---

## T-75 — the Thomson term rides the by-parts it should never have entered

**2026-10-19. P2-T's D2, which P1-B wrongly discharged, is the dominant lever
on both open symptoms at once.**

### The decomposition that should have been run three rounds earlier

(102) term by term, EdS, $\ell=10$, $\mathcal V$ weight:

| $k$ | term | Newtonian | CDM | CDM/Newt |
|---:|---|---:|---:|---:|
| 10 | boundary scalar | $-1.009\times10^{-1}$ | $2.014\times10^{-2}$ | $-0.1995$ |
| 10 | boundary shear | $0$ | $-8.710\times10^{-3}$ | --- |
| 10 | **integrated** | $\mathbf{3.477\times10^{1}}$ | $-9.904\times10^{0}$ | $-0.2849$ |
| 10 | total | $3.467\times10^{1}$ | $-9.893\times10^{0}$ | $-0.2854$ |

**The bulk is 344$\times$ the boundary in the Newtonian frame**, and
CDM/Newtonian is $-0.2849$ for the bulk against $-0.2854$ for the total. The
bulk *is* the frame gap and it *is* what buries the peaks: **T-68 and T-73 are
one defect.**

### What makes it 344x

$\tilde C_1$ carries both halves, $-\tilde C_1=(\delta\tilde T+\Phi_A)
+\kappa'\tilde v_B$, and (102) by-parts **all** of it. Under $\mathcal V$ the
Thomson half contributes $\mathcal V\kappa''\tilde v_B\sim\kappa'\kappa''
e^{-\kappa}$. That is P1-T \S5.2's *"~$10^8$ and they nearly cancel"* and it is
**A-2's own arithmetic**: *"the Doppler source reaches $\sim10^6$ against a
primary source of order unity. It swamps everything."*

> **A-2 described this mechanism correctly in 2026-10-06 and attributed it to
> the weight.** It is not the weight. It is by-parting a term whose own
> $\kappa'$ already makes the visibility.

### P1-T \S5.3's split, measured

Bulk carries the **gravitational half only**, $-(a\tilde{\mathcal B}_1)'/k$:

| background | $k$ | frame gap, released | split | bulk/boundary, released | split |
|---|---:|---:|---:|---:|---:|
| EdS | 10 | 1.2847 | **0.2779** | 344.41 | **0.09** |
| EdS | 60 | 1.5642 | 0.8772 | 343.99 | 2.63 |
| EdS | 300 | 1.0362 | 0.9925 | 143.73 | 14.87 |
| PLANCK | 10 | 1.4159 | **0.5983** | 221.65 | **0.74** |
| PLANCK | 60 | 1.6705 | 0.9204 | 164.62 | 5.38 |
| PLANCK | 300 | 0.9961 | 1.0050 | 43.72 | 56.04 |

**The first change all day to move the frame gap by more than a percent**, and
it removes the bulk's absurd dominance at the same time --- one change, both
symptoms.

Leaving the Thomson half un-by-parted puts it on the **kernel derivative**,
$j_\ell'$, which is the standard Doppler projection and which this bundle has
never carried. Measured with both sign conventions (P1-T: Annals II has two,
differing by a sign per derivative): it moves the gap by a further few percent
at $k=10$ and is not the dominant piece. **The split is.**

### What is still open

$k=300$ is untouched ($1.0362\to0.9925$ on EdS, $0.9961\to1.0050$ on PLANCK),
and the gap is $0.28$--$0.92$ rather than zero. **This is a large improvement,
not a closure**, and the acceptance criterion is a theorem.

### P1-B's error, recorded

**I discharged D2 on 2026-10-19 on a measurement that did not test it.** The
"cancellation metric 1.00 at every $k$ and $\ell$" measured
*boundary-against-bulk* cancellation. **D2 is a *within-bulk* conditioning
defect** --- $\mathcal VC_1$ against $WC_1'$ --- and I never measured that, and
measured the wrong weight besides, pre-T-69. P2-T's D-table and P1-T \S5.2
were right and the discharge is withdrawn.

*This is the second time today that a conclusion came from a statistic that
did not address the claim* (the first being T-68's amplitude/offset, read off a
coarse table). The pattern is **answering an adjacent question and reporting it
as the question**, and it is worth its own guard beside V4.

### The restored monopole row --- P1-T's, confirmed and excluded

With $\mathcal B_0$ restored, $C_0=-\tfrac13a\mathcal B_2-a\mathcal B_0$ and
$a\mathcal B_0=-\tfrac13k\tau_1$ ($\tau_1$ velocity-normalised, T-66):

$$\Delta C_0=-\tfrac13a\Delta\mathcal B_2+\tfrac13k\Delta\tau_1
=+\tfrac13kv-\tfrac13kv=0 .$$

**Measured on the grid: $\Delta C_0=3.5\times10^{-15}$, $3.2\times10^{-14}$,
$3.4\times10^{-16}$, $1.9\times10^{-15}$, $6.5\times10^{-15}$,
$1.5\times10^{-13}$** --- machine zero at every $k$ on both backgrounds.
**$C_0$ is boost-invariant with $\mathcal B_0$ restored and is not without
it**, confirming P1-T's derivation independently.

It does **not** close the frame gap ($1.5642\to1.5203$ at $k=60$; *worse* at
$k=300$ on PLANCK). So $C_0$ is now **excluded by proof rather than by
ablation**, which is a stronger statement than the one T-74 could make.

**Note the contradiction this creates and do not assume it away.**
`slowdecoupling-ng-0` states that $\tilde\sigma_{ab}\approx0$ implies
$\tilde C_0\approx0$. That holds only if $C_0\propto\mathcal B_2$ alone. With
an $a\mathcal B_0$ term the Newtonian frame acquires a rank-0 source it has
never had, and (110) is wrong --- or the restoration is. **Unresolved.**

---

## T-76 — a correction to T-74's elimination table, and the guard it earns

**2026-10-19. P1-T caught this and it is P1-B's error.**

T-74 listed `beta = -alpha: flip C_2''` among eleven eliminated candidates,
on the measurement $1.2847\to1.2847$ at $k=10$ on EdS, and concluded *"which
says the $C_2''$ slot carries essentially nothing there."* **The conclusion
was drawn from a test that could not have come out any other way.**

$|C_2''|$ against the terms it sits beside in the same bracket, CDM frame:

| background | $k$ | $\lvert C_0\rvert$ | $\lvert C_1'\rvert$ | $\lvert C_2''\rvert$ | $C_2''/C_1'$ |
|---|---:|---:|---:|---:|---:|
| EdS | 10 | $1.667\times10^{2}$ | $8.072\times10^{3}$ | $1.306\times10^{-4}$ | $1.6\times10^{-8}$ |
| EdS | 60 | $6.000\times10^{3}$ | $2.428\times10^{3}$ | $1.306\times10^{-4}$ | $5.4\times10^{-8}$ |
| EdS | 300 | $1.500\times10^{5}$ | $1.699\times10^{4}$ | $1.306\times10^{-4}$ | $7.7\times10^{-9}$ |
| PLANCK | 10 | $1.856\times10^{2}$ | $2.699\times10^{3}$ | $1.125\times10^{1}$ | $4.2\times10^{-3}$ |
| PLANCK | 60 | $6.680\times10^{3}$ | $3.104\times10^{3}$ | $1.125\times10^{1}$ | $3.6\times10^{-3}$ |

**On EdS the slot is $10^{-8}$ of its neighbours.** Flipping its sign is a
no-op *by construction*, so the measurement was void. On PLANCK it is
$10^{-3}$: not void, but orders below the sensitivity the test needed.

> **`beta = -alpha` is UNTESTED, not eliminated.** T-74's table is corrected
> here. The derivation stands as exact algebra; nothing this bundle has run
> bears on it, and a background with $C_2''$ comparable to $C_1'$ is required
> before it can.

### The guard

P1-T's own diagnosis of six of its corrections --- *"a mechanism derived
correctly, then offered as a diagnosis without being run against the control
that would falsify it"* --- applies to P1-B in a second form, and today it
caught three:

| | what happened |
|---|---|
| T-68 | an amplitude/offset pair **read off a coarse table** instead of computed; the conclusion came out backwards |
| T-75 | D2 discharged on a **boundary-against-bulk** metric when D2 is a **within-bulk** claim |
| T-76 | a sign flipped on a term that is $10^{-8}$ of its neighbours, and the null **reported as information** |

All three are the same shape: **answering an adjacent question and reporting
it as the question.** V4 guards comparing across stages; this is comparing
across *questions*, and it needs its own line:

> **V11 --- before reporting that a change did not matter, show that it
> could have.** A null from a lever with no travel is not evidence. State
> the magnitude of the thing varied against the thing it sits beside, or
> the null says nothing.

This bundle's residual register (the Replacement's item 4) should carry that
column: not only each quantity's stage and normalisation, but **its size
against its neighbours**, so a void test is visible before it is run.

---

## T-77 — the two defects were masking each other

**2026-10-19, late. The strongest result of the day, and the reason thirteen
single-candidate ablations all came back null.**

### Are the two coefficient sets a boost apart?

Every test before this asked what (102) *does* with the two sets. None asked
whether the sets are related by the boost at all. Against the theory ---
$\Delta C_2=s=v/k$, $\Delta C_1=-\dot s+\kappa's$, $\Delta C_0=0$ --- measured
relative to each row's own scale:

| background | $k$ | $C_2$ | $C_1$ | $C_1$ without $\kappa's$ | $C_0$ |
|---|---:|---:|---:|---:|---:|
| EdS | 10 | $3.3\times10^{-16}$ | $6.1\times10^{-16}$ | $1.698$ | $\mathbf{1.000}$ |
| EdS | 300 | $3.3\times10^{-16}$ | $3.3\times10^{-16}$ | $0.999$ | $\mathbf{1.000}$ |
| PLANCK | 10 | $3.0\times10^{-16}$ | $5.3\times10^{-16}$ | $1.755$ | $\mathbf{1.000}$ |
| PLANCK | 300 | $3.0\times10^{-16}$ | $3.4\times10^{-16}$ | $0.915$ | $\mathbf{1.000}$ |

**$C_1$ and $C_2$ are exactly a boost apart.** P1-T's $+\kappa's$ term is
confirmed independently: without it the $C_1$ residual is $O(1)$, with it
machine zero. **$C_0$ is not a boost apart, by 100% of its own scale**, at
every $k$ on both backgrounds --- because the code's $C_0\propto a\mathcal B_2$
alone, which is zero in one frame and not the other.

### Neither fix alone; both together

| background | $k$ | released | split only | $\mathcal B_0$ only | **split + $\mathcal B_0$** |
|---|---:|---:|---:|---:|---:|
| EdS | 60 | 1.5642 | 0.8772 | 1.5203 | **0.0593** |
| EdS | 300 | 1.0362 | 0.9925 | 1.0672 | **0.0710** |
| PLANCK | 60 | 1.6705 | 0.9204 | 1.8779 | **0.2315--0.4008** |
| PLANCK | 300 | 0.9961 | 1.0050 | 1.0145 | **0.0606--0.3648** |

**A factor of 5 to 25 at $k\ge60$, and neither fix alone gets near it.**
$\mathcal B_0$ alone barely moves the gap; the split alone halves it. **They
mask each other**, which is exactly why thirteen single-candidate ablations ---
including both of these --- came back null, and why T-74's elimination table
was reasoning from a method that could not see a pair.

> **A one-at-a-time ablation cannot find two defects that compensate.** That
> is not a new failure mode in this project, it is **T-3's** --- *two agreeing
> routes agree about what they share* --- turned around: two *disagreeing*
> candidates can each look innocent alone. The elimination tables of T-73 and
> T-74 are sound as measurements and were over-read as exclusions.

### What is still open, stated plainly

$k=10$ goes the **wrong way**: EdS $0.278\to0.980$, PLANCK $0.598\to1.743$.
Unexplained. Those are modes near or outside the sound horizon at $\eta_*$,
where $a\mathcal B_0\propto k\tau_1$ is small, so either the $\mathcal B_0$
normalisation used here is wrong at low $k$ or a third term matters there.

And $0.06$--$0.40$ is **not** $0$. The acceptance criterion is a theorem ---
identical multipoles at every $\ell\ge2$ --- so this is a large improvement and
not an arrival.

### P1-T's item 4, answered

The post-split residual against $\ell$, EdS $k=60$: $0.877$, $0.895$, $0.883$,
$0.896$, $0.896$, $0.892$, $0.900$, $0.896$, $0.894$, $0.896$, $0.894$,
$0.896$, $0.894$ over $\ell=2\ldots200$. PLANCK $k=60$: $0.912$--$0.928$.
**Flat.** By P1-T's own criterion the residue is still the constructor, not the
rank-2 slot, and the rank-2 condition should stay untouched until a background
with $C_2''\not\ll C_1'$ exists.

### P1-T's control objection, accepted

*"The Newtonian column must not move" is correct for rearrangements of (102)
and wrong for anything touching $v^B_a$, because $\tilde v^B_a=v^B_a-v_a$.*
Accepted. T-74's *"Thomson term $\kappa'\tilde v_B$ zeroed"* row was judged
against a control that cannot respond to it, and is withdrawn from the
elimination list on that ground as well as T-77's.

---

## T-78 — the restored monopole source and (106)'s dipole term are the same object

**2026-10-19, late. A structural finding, and an explicit failure to explain
what it was sought for.**

With $\mathcal B_0$ restored (T-77), $C_0=-\tfrac13a\mathcal B_2-a\mathcal B_0$
and $a\mathcal B_0=-\tfrac13k\tau_1$. In the **Newtonian** frame
$a\mathcal B_2=0$, so $C_0^N=+\tfrac13k\tau_1$.

$-\tilde C_1'$ already contains $+\tfrac{k}{3}\tau_1$, from (106)'s
$\tfrac13k^2\tilde\tau_1$ divided by $k$. Measured, Newtonian frame, max over
the $\eta$ grid:

| background | $k$ | $C_0$ restored | $\tau_1$ piece of $-C_1'$ | **ratio** | rest of $-C_1'$ | $C_0$/rest |
|---|---:|---:|---:|---:|---:|---:|
| EdS | 10 | $3.8494\times10^{0}$ | $3.8494\times10^{0}$ | **1.0000** | $5.897\times10^{3}$ | 0.0007 |
| EdS | 60 | $6.5439\times10^{1}$ | $6.5439\times10^{1}$ | **1.0000** | $1.139\times10^{4}$ | 0.0057 |
| EdS | 300 | $1.1228\times10^{2}$ | $1.1228\times10^{2}$ | **1.0000** | $3.587\times10^{3}$ | 0.0313 |
| PLANCK | 10 | $3.7712\times10^{0}$ | $3.7712\times10^{0}$ | **1.0000** | $4.651\times10^{3}$ | 0.0008 |
| PLANCK | 300 | $4.8973\times10^{1}$ | $4.8973\times10^{1}$ | **1.0000** | $3.311\times10^{3}$ | 0.0148 |

**Identically equal, to every digit, at every $k$ on both backgrounds.**

So the bracket $\{C_0-C_1'+C_2''\}$ carries the dipole-divergence source
**twice** once $\mathcal B_0$ is restored. The two are different objects by
provenance --- $\mathcal B_0=-\tfrac13\mathcal D^a\tau_a$ is the $\ell=0$
*source* in the matching; (106)'s $\tilde\tau_1$ term is the *time evolution*
of the rank-1 coefficient, through $\delta T'=\tfrac k3\tau_1$ --- and
numerically they are one number. **One of the two slots is wrong and this does
not say which.** For P1-T.

### What this does **not** explain, stated because it is what it was sought for

It is **not** the $k=10$ reversal. The doubled term is **0.07%** of the rest
of $-C_1'$ at $k=10$ and 3% at $k=300$ --- orders too small to turn
$0.278\to0.980$. The $k=10$ reversal of T-77 remains **unexplained**.

*Recorded this way deliberately.* The measurement was run to explain $k=10$,
found something real, and does not explain $k=10$. Under **V11** the honest
report is both halves; reporting only the finding would be the same error in a
fifth costume --- answering an adjacent question and letting it stand for the
question asked.

### Why the $k=10$ reversal is larger than it looks

Restoring $\mathcal B_0$ **creates** a rank-0 source in the Newtonian frame
(where there was none) and **shrinks** the CDM one from $-\tfrac52a\mathcal B_2$
to $\tfrac13k\tau_1$. The Newtonian side moves by 0.07%; the CDM side moves by
a lot. So the frame gap moves mostly because the CDM column moved, and at
$k=10$ it moves the wrong way. That is a description of the arithmetic, **not
a diagnosis**, and it is the next thread.

---

## T-79 — the $\ell=0$ row: $\kappa'$ is absent from **both** sides, and *Annals II* prints two different $\ell=0$ equations

**2026-10-19, late. P1-T asked one binary question and it decides the branch.
This entry also withdraws a P1-B result from earlier the same day.**

### The question, and the answer read off the artefact

> *"Is $\kappa'$ absent from both sides of the $\ell=0$ equation, or only from
> the right?"*

**Both sides.** `grep kappa functions/spectra/acoustic.py` returns nothing and
exits 1: $\kappa'$ does not appear anywhere in the module that integrates the
acoustic pair, at either $\ell$.

```
d_tau   = -R'/(1+R) tau_1 - k/(1+R) delta_t - k phi_a
d_delta = -phi_h' + k/3 tau_1            [- aH phi_a, and
                                          expansion_coupling=False is
                                          production: two_frame.py:384,393]
```

### The asymmetry, which is the finding

The **matching** carries $\kappa'$ at $\ell=1$ and nothing at all at $\ell=0$.
From `_solved_match()`, verbatim:

```
# ell = 2:  C_2 k^2 * (5/b2) * j_2''(0) = -(a B_2)
# ell = 1:  C_1 * (1/b1) * k            = -(a B_1 + kappa' v_B)
# ell = 0:  C_0 + C_2 k^2 * (5/b2) * j_0''(0) = 0        <- RHS is zero
```

| | $\ell=0$ | $\ell=1$ |
|---|---|---|
| solver (`acoustic.py`) | no $\kappa'$ | no $\kappa'$ |
| matching (`coefficients.py`) | no $\kappa'$, **and no source of any kind** | $\kappa'v_B$ |

So the $\ell=1$ row is sourced and the $\ell=0$ row is not. **That is one
defect with a direction**, not a mismatch to be discovered: the dipole row was
brought to the solver's convention and the monopole row was left behind.

### P1-T's addendum, and what it corrects in this entry's first draft

P1-T reads `modeibe` at $\ell=0$, where the recursion coefficient is
$(\ell+1)^2/[(2\ell+1)(2\ell+3)]=\tfrac13$ and $\tau_{-1}=0$:

$$\tau_0'+\tfrac{k}{3}\tau_1+\kappa'\tau_0=-a\mathcal B_0,\qquad
a\mathcal B_0=-\tfrac13k\tau_1\ \Longrightarrow\ \tau_0'+\kappa'\tau_0=0$$

with the convention checked against `cbrII.tex` line 2563 rather than imported.
**The printed $\ell=0$ equation is self-cancelling**: the streaming term is on
the right as $-a\mathcal B_0$ *and* on the left as $+\tfrac k3\tau_1$, and they
cancel, leaving a monopole with no source that is then damped by a $\kappa'$
Thomson scattering does not supply.

**P1-B's first draft of this entry said the solver had silently corrected
*Annals II*. That is not what the code shows and it is withdrawn.**
`solve_acoustic` integrates **(152)/(153)** — `mode-dipole` and `mode-mono` —
not (70) `modeibe` at $\ell=0$. Those are two *printed* equations for the same
quantity and they are not the same equation:

| | $+\tfrac k3\tau_1$ | $\kappa'\tau_0$ | $\Phi_H'$ |
|---|---|---|---|
| (70) `modeibe` at $\ell=0$, as P1-T reads it | on the **left**, and again on the right as $-a\mathcal B_0$ | **present** | absent |
| (153) `mode-mono`, as the bundle integrates it | on the **right**, once | absent | **present** |

So the correction is *Annals II*'s own, made between its general-$\ell$
hierarchy and its specialised monopole equation, and the bundle follows the
second. The matching (89) `find_coef` descends from (71) `source-calB`, which
is (70)'s source — **so the matching inherits the first.** That is why the
monopole row was left behind, and it is a sharper statement than "the code
fixed the paper".

> **P1-B cannot read `sources/annals/cbrII.tex` from this workspace.** It is
> not in the repository and the cloud session has no copy. Everything above
> about what (70) and (153) *print* is P1-T's reading and the bundle's own
> transcriptions, and is marked as such. **For P1-T, who has the file:**
> confirm (153)'s printed form carries $+\tfrac k3\tau_1$ on the right and no
> $\kappa'$, which is the half of the table P1-B cannot check.

### What `d_delta` settles — P1-T's caution, answered

P1-T flagged that if $a\mathcal B_0$ is the streaming term rather than a
source, `c5_monopole.py` restores the wrong object while still returning
$\Delta C_0=0$, and left it to be settled by reading `d_delta`. Read:

$$\texttt{d\_delta}=-\Phi_H'+\tfrac k3\tau_1,\qquad
a\mathcal B_0=-\tfrac13k\tau_1\ \Longrightarrow\
\boxed{\texttt{d\_delta}=-a\mathcal B_0-\Phi_H'}$$

**$a\mathcal B_0$ is on the right, once, as a source.** `c5_monopole.py`
restores the right object, and the double count P1-T identifies in the printed
equation is not in the code. The V11a worry does not apply in that form.

### But there is a second driving term, and no $\mathcal B$ carries it

$\Phi_H'$ drives $\tau_0$ in `d_delta` and appears in no $\mathcal B$, so the
$\ell=0$ matching row cannot see it. Measured as `rhs()` forms the two terms,
max over the solver's own grid, production settings:

| background | $k$ | $\lvert-a\mathcal B_0\rvert$ | $\lvert-\Phi_H'\rvert$ | **ratio** |
|---|---:|---:|---:|---:|
| EdS | 10 | $3.7434\times10^{0}$ | $3.0159\times10^{-10}$ | **0.0000** |
| EdS | 60 | $5.2884\times10^{1}$ | $4.2171\times10^{-10}$ | **0.0000** |
| EdS | 300 | $4.0876\times10^{1}$ | $1.9084\times10^{-10}$ | **0.0000** |
| PLANCK | 10 | $3.6674\times10^{0}$ | $2.1647\times10^{0}$ | **0.5903** |
| PLANCK | 60 | $2.8214\times10^{1}$ | $1.7990\times10^{0}$ | **0.0638** |
| PLANCK | 300 | $2.2362\times10^{1}$ | $8.1059\times10^{-1}$ | **0.0362** |

**Machine zero on EdS at every $k$** — matter domination holds $\Phi_H$
constant — and **59% of the monopole source on PLANCK at $k=10$.**

This is the fourth time EdS has been the control that kills a candidate
(T-74 ISW, T-76 rank-2, T-77's $\beta=-\alpha$, now this): **$\Phi_H'$ cannot
be the EdS $k=10$ reversal, because on EdS it is not there.** Stated under
V11 before the interesting half.

The interesting half is that it is **background-dependent with exactly the
shape of the EdS/PLANCK asymmetry P1-T predicted no single constant could
reconcile** — zero on one background and 0.59 on the other, at the same $k$.
That is a lead, not a result.

**It is not landed and will not be until a double count is excluded.**
`sources.py:291` builds the integrated bracket as
$\texttt{isw}=\Phi_A'-\Phi_H'$, and the integral's lower limit is
`eta_floor = env.eta[0]`, **not** $\eta_*$ — so the integrated slot already
covers the range in which $\Phi_H'$ drives $\tau_0$. Whether adding $-\Phi_H'$
to the $\ell=0$ matching row restores a missing term or counts an existing one
twice is a question about two integration limits, it is a **read** rather than
a measurement, and it has not been done. **Nothing is added to $C_0$ until it
has.**

---

### Withdrawn: $\kappa'\tau_0$'s "gap collapse" is a metric artefact

P1-B reported earlier today that supplying $\kappa'\tau_0$ to the $\ell=0$ row
collapses the frame gap — EdS $k=10$ $0.98\to0.03$, and similarly at $k=60$
and $k=300$. **The gap is $\lvert C_{\rm CDM}-C_{\rm Newt}\rvert/\text{scale}$,
and only the denominator moved.** Measured at $\ell=10$:

| $k$ | variant | $\lvert c-n\rvert$ | scale | gap |
|---:|---|---:|---:|---:|
| 10 | $\mathcal B_0$ | $1.1237\times10^{-1}$ | $1.1896\times10^{-1}$ | 0.9446 |
| 10 | $\mathcal B_0-\kappa'\tau_0$ | $1.1237\times10^{-1}$ | $4.6771\times10^{0}$ | **0.0240** |
| 60 | $\mathcal B_0$ | $2.8191\times10^{-2}$ | $1.6397\times10^{-1}$ | 0.1719 |
| 60 | $\mathcal B_0-\kappa'\tau_0$ | $2.8191\times10^{-2}$ | $2.3860\times10^{0}$ | **0.0118** |
| 300 | $\mathcal B_0$ | $4.1191\times10^{-3}$ | $4.3145\times10^{-2}$ | 0.0955 |
| 300 | $\mathcal B_0-\kappa'\tau_0$ | $4.1191\times10^{-3}$ | $8.0172\times10^{-1}$ | **0.0051** |

**$\lvert c-n\rvert$ is identical to five figures in every pair.** The two
columns did not move together; the scale inflated by up to $39\times$ and
carried the ratio down with it. **The frames agree no better than before.**

This is **T-70 inverted** — there a denominator collapsed and manufactured a
large number; here one inflates and manufactures a small one. It is the same
defect and the register now has it in both polarities.

P1-B had already stated the risk one message earlier — *"a term $4\times10^3$
times its neighbour that makes two columns agree is as likely to have made two
**wrong** columns agree; frame agreement is necessary, not sufficient"* — and
the measurement shows it was the weaker failure still: not even frame
agreement. **The additive route via $\kappa'\tau_0$ is closed on this evidence**,
which is the branch P1-T's first fork predicts.

---

### The method clause, and a numbering decision

P1-T proposed, and it is landed in their wording:

> **A statement about what a quantity must be is not a statement about what
> the code has.** Size tells you what a term would *do* if absent, never
> whether it *is* absent. **Any claim about an artefact is read off the
> artefact or it is not made.**

**The attribution is split, and splitting it is the point.**

| | the error | mode |
|---|---|---|
| P1-T | withdrew $\kappa'\tau_0$ on *"if it were absent nothing would work at all — it is present"*: a statement about what must be, offered as a statement about what the code has | **the new clause** |
| P1-B | reported a gap collapse from a ratio whose **denominator** moved by $39\times$ while the numerator did not move at all | **V4** — comparing across normalisations — and **V11b**, whose definition column would have pinned the denominator before the number was recorded |

Putting both under the new clause would be the error the new clause names.
P1-B read the artefact; P1-B compared two numbers without holding their
normalisation fixed. Those are different failures and they need different
guards.

**The numbering, which P1-T left to P1-B.** There is a name collision and this
is the cheapest moment it will ever be fixed. `provenance/DECISIONS-v1.0.0.md`
carries a **V-series of its own** — V1–V15, the *visual grammar*, where V5 is
*"Legend present for $\ge2$ series"* — and it is released, hashed and cited by
figure captions, so it cannot move. The method series lives in project
documents and in two lines of this repository, so it moves for the cost of one
commit.

**Decision: the method-failure series is renamed `M`.** M1–M11b are V1–V11b
unchanged in content and in number, so every cross-reference written this week
resolves by substituting the letter. The new clause is **M5a**, placed under
M5 (*assessing a finding from a summary, not its own file* — guard: *open the
manuscript*), which it generalises from a manuscript to any artefact, code
included.

It is **not** M11c. M11's family is about *magnitude as a test of travel*;
this is about *reading as a substitute for inferring*, which is M5's. That
distinction is the same one the attribution table above makes, and collapsing
it would lose both.

*Executive decision, P1-B's lane, informing P1-T and Coordination rather than
asking. `tests/frame/README.md` and `tests/test_frame_checks.py` carry the two
repository references to `V11a`; they are updated in the same commit.*

---

## T-80 — an independent review's five concerns, mapped onto the register

**2026-10-19, late. Relayed by the PI.** A reader ranked five concerns from the
code snapshot. **Four of the five land on findings already open, and the
reader's first-ranked concern names the three suspects T-66, T-77 and T-79
name.** Recorded for the mapping, and because item 5 is new.

> **M2 — this is not counted as an independent check, and the first draft of
> this entry counted it as one.** P1-T's caution, accepted and applied here
> rather than noted: *"whether this is corroboration or restatement depends on
> whether the reviewer reached those suspects from the code or from a briefing
> that already carried them. Three arrivals through one briefing is one
> check."* **P1-B does not know which**, and wrote *"arrived at
> independently"* without establishing it — which is M2 exactly, in the entry
> that lands M5a. The claim is withdrawn and the mapping below stands on its
> own, because a map is useful whether or not it is a second witness.
>
> **The one question that settles it, for the PI:** was this reader given any
> of this project's material — the register, a stream document, a summary —
> before they read the code? A *yes* makes the first four items a restatement
> and leaves only item 5. A *no* makes them a second source and they are
> counted. **Until then they are counted as zero**, which is the conservative
> direction and costs nothing, since item 5 does not depend on it.

| rank | the concern, in the reader's framing | register |
|---|---|---|
| **1** | frame cancellation incomplete; monopole/shear normalisation, **omitted monopole source**, **Thomson velocity term** | **T-66** ($\kappa'v_B$'s spurious $\times k$), **T-77** ($C_0$ not a boost apart; split + $\mathcal B_0$), **T-79** (the $\ell=0$ row). *All three named suspects are open findings.* |
| **2** | scattering belongs under $g$, gravitational redshift under $e^{-\kappa}$; combining before differentiating adds rate factors, drops product-rule terms, double-counts boundaries | **A-2** (the weight choice, flipped by T-69), **T-72** (the rank-2 by-parts pair), **T-69** (A-2's basis void) |
| **3** | potentials prescribed from matter growth, not evolved with the photons; static $T(k)$ suppresses the initial amplitude and its forcing | **A-3** (matter-dominated driving), **T-67/T-71** (the comoving $k$ of the transfer) |
| **4** | tight coupling frozen at a fixed time; **photon quadrupole, polarization and baryon–photon slip** | **A-1** covers the freeze. **Polarization and slip are carried by neither A-1 nor any finding — new, and correctly raised.** |
| **5** | diffusion uses zero baryon loading against a baryon-loaded oscillator; one damping factor on sources with different histories; `LCDM_MODEL` omits $\Omega_r$; helium; $h$; the Thomson-rate conversion | **T-21** for the first, and **confirmed again below**. The rest is partly new. |

### What was checked on receipt, and what it says

**Zero baryon loading in the damping — confirmed, and it is T-21.**
`pipeline.py:437` passes `r_of_eta=recombination.kappa_prime * 0.0`, while the
oscillator runs at $R(\eta_*)=0.6038$ (EdS), $0.6125$ (LCDM), $0.6089$
(PLANCK) — read from `provenance/MODEL-PARAMETERS-v1.3.0.md`, which the code
generates. T-21 measured the cost: $\ell_D=1783$ as called against $1985$ with
the $R$ the bundle already has. `scripts/make_model_table.py:69` carries the
same `np.zeros_like` call, so the generated table's `k_D` row is the $R=0$
number and **is mislabelled**; the row is correct for what was asked of it and
wrong for what it is read as.

**`LCDM_MODEL` omits $\Omega_r$ — confirmed.** `Omega_r` is `0` for both CDM
and LCDM in the generated table. For EdS that is the **control** and is
deliberate, and the table says so. **For LCDM it is neither a control nor
stated**, and at $z_*\simeq1109$ the radiation the model omits is not
negligible. *New. Not previously registered.*

**Helium — confirmed absent.** `_thomson_scale` takes
$n_{b,0}=1.123\times10^{-5}\,\omega_bh^2\ \mathrm{cm^{-3}}$ and
`kappa_prime = thomson_scale * x_e * a**(-2)` uses it as the *electron*
density. With helium, $n_e=x_e(1-Y_p)n_b$, so a factor $(1-Y_p)\simeq0.76$ is
missing from $\kappa'$ uniformly. `grep` for helium in `decoupling.py` returns
nothing. *New. Not previously registered.* It is a uniform rescaling of
$\kappa'$ and therefore of the visibility's **width and height but not its
location**, which is why no test has seen it.

**$h$ propagation — not adjudicated.** `_thomson_scale`'s docstring gives an
explicit cancellation argument for the one surviving factor of $h$. It may be
right. It was not re-derived here and **nothing is claimed either way**, which
is M5a.

### What this review is, and what it is not

It is a ranking, not a measurement — the reader says so themselves: *"the
relative contribution of each problem still requires controlled numerical
isolation"* — and that isolation is exactly what T-77 showed one-at-a-time
ablation cannot do (**M11a**). Its evidential weight is suspended pending the
M2 question above.

**One clause of item 2 is already refuted and must not be acted on.**
*"Gravitational redshifts accumulated along the photon path belong under the
survival probability $e^{-\kappa}$"* is correct as algebra and **was refuted as
a prescription by this bundle's EdS control at T-74**: EdS contains no ISW, and
the three columns moved by 0.060/0.065/0.060 under it, so the weight is not
what is costing the plateau. P1-T raised the same clause as a mechanism on
2026-10-18 and withdrew it on that control. **Anyone acting on item 2's
$e^{-\kappa}$ clause as written repeats a refuted step**, and it is flagged
here because the review will be read by people who do not have T-74.

**P1-T's reading of items 3 and 4, recorded so the mapping is complete.**
Item 3 is not the peak explanation: the measured effective sound horizon shift
is **2%**, against the **11%** that mechanism requires. Item 4's closing
sentence — *"the Bessel projection itself is a legitimate free-streaming
method; the concern is the source history supplied to it"* — **is T-71**, and
is the bundle's own position.

**Their closing judgement is the bundle's own and worth recording in their
words:** these are *"problems in the implemented specialization and
approximations; they do not establish a failure of the underlying
frame-covariant formulation"*, and *"the acoustic oscillator is present"*.
That is the PI's standing position — *paper 1 is correct, the problem is
getting the acoustic peaks working* — reached from outside.

### Actions

1. **Polarization and baryon–photon slip** are added to A-1's scope in
   `provenance/SOURCE-APPROXIMATIONS-v1.md` as *stated, unimplemented, and not
   a control*. They are not candidates for the frame gap — neither is
   frame-dependent — so they are an **envelope** concern, which is where the
   reader placed them.
2. **Item 5 gets entries of its own at T-81**, on P1-T's suggestion and
   because it is the only item with no prior finding behind it.
   **`LCDM_MODEL`'s $\Omega_r=0$** and **the missing $(1-Y_p)$** are
   **not fixed in this commit.** Both change the envelope
   and neither changes the frame gap; fixing an envelope term while the frame
   gap is open would move the one number the week is measuring, for reasons
   unrelated to it. They are **v1.4.0 work**, after the gap closes.
3. **`make_model_table.py`'s `k_D` row** is relabelled in place to say it is
   the $R=0$ value and to name T-21. One line, and it stops the table being
   read as a parameter sheet it is not.

---

## T-81 — item 5: the damping and background inputs, opened as their own entries

**2026-10-19, late.** T-80's item 5 is the only one of the five with no prior
finding behind it, so it gets entries rather than a row in a mapping table.
**P1-T: *"None has been looked at."* Five have now been looked at; four are
confirmed, one is half-wrong and the correction matters more than the half
that stands.**

### T-81a — zero baryon loading in the diffusion scale. **Confirmed. It is T-21.**

`pipeline.py:437` and `scripts/make_model_table.py:69` both pass
`r_of_eta = zeros` while the oscillator beside them runs at
$R(\eta_*) = 0.6038$ (EdS), $0.6125$ (LCDM), $0.6089$ (PLANCK).
T-21 measured it: $\ell_D = 1783$ as called against $1985$ with the $R$ the
bundle already computes, **12% in the damping knee**. Open since T-21 and now
raised a second time from outside. The generated model table's `k_D` row is
relabelled in this commit to say which number it is.

### T-81b — *"one damping factor on sources with different histories."* **Half wrong, and the correction is the interesting half.**

**The half that is wrong.** The bundle already separates them.
`integral_solution.py:118` states it and lines 206 and 226/236 do it:

```
integrand_weight = weight * diffusion       # e^{-(k/k_D(eta))^2}, an ARRAY
scalar[i] = (c2_prime_star - c1_star) * damping_total * j_l_star   # a SCALAR
```

The boundary carries $\mathcal D(\eta_0,k)$ and the integrand carries the
pointwise $e^{-(k/k_D(\eta))^2}$. **It is not one factor and the review's
wording should not be transcribed as if it were.**

**The half that stands, and it is sharper than what was asked.** The integrand
carries a diffusion factor **at all**. Photon diffusion damps perturbations
that are *scattering*; gravitational redshift accumulated along the path after
decoupling is not damped by it. So
`integrand_weight = weight * diffusion` applies a scattering suppression to a
gravitational source for the whole line of sight.

**This sits directly beside the missing late ISW, and gives it a second
mechanism.** A-1 already says *Annals II*'s $\mathcal V$ weight cannot carry a
late ISW because $\mathcal V$ is zero by $z\lesssim1$. T-81b adds that even
under $e^{-\kappa}$ the integrand would still be multiplied by
$e^{-(k/k_D)^2}$. **Two independent suppressions of the same term**, and T-74's
EdS control cannot distinguish them — EdS has no ISW to suppress, so **it is
void against both** (**M11**, stated before the lead rather than after it).

**Not measured.** Whether removing the diffusion factor from the integrand
recovers a late ISW is one run and it has not been made. It is the first
candidate in the register with a *named mechanism* for the missing ISW rather
than a symptom, which is why it is written down tonight and not acted on
tonight.

### T-81c — `LCDM_MODEL` omits $\Omega_r$. **Confirmed.**

`Omega_r` is exactly `0` for `CDM_MODEL` and `LCDM_MODEL` in
`provenance/MODEL-PARAMETERS-v1.3.0.md`, which the code generates from the
`Background` objects it integrates. For EdS that is the **control** and is
stated. **For LCDM it is neither a control nor intended**, and at
$z_*\simeq1109$ the omitted radiation is not negligible. **Envelope, not frame.**

### T-81d — helium is absent from $\kappa'$. **Confirmed.**

`_thomson_scale` takes $n_{b,0}=1.123\times10^{-5}\,\omega_bh^2\
\mathrm{cm^{-3}}$ and `kappa_prime = thomson_scale * x_e * a**(-2)` uses it as
the **electron** density. With helium, $n_e = x_e(1-Y_p)n_b$, so a uniform
factor $(1-Y_p)\simeq0.76$ is missing. `grep` for helium in `decoupling.py`
returns nothing.

**Why no test has seen it.** It rescales $\kappa'$ uniformly, so it changes the
visibility's **width and height** and not its **location** — and $\eta_*$ is
defined here as the visibility *peak*. Every test that pins decoupling pins the
peak. **Envelope, not frame.**

### T-81e — $h$ propagation and the Thomson-rate conversion. **Not adjudicated.**

`_thomson_scale`'s docstring gives an explicit argument for the one surviving
factor of $h$: $n_{b,0}\propto\omega_bh^2$ against $c/H_0 = 9.2506\times
10^{27}/h$ cm leaves one $h$, *"which cancels against $c/H_0$ for the
combination that appears here."* **It was not re-derived.** Nothing is claimed
either way, which is **M5a** — the clause landed at T-79 one entry earlier, and
the first place it binds is P1-B's own entry.

### Triage, and why none of it is fixed tonight

| | changes the frame gap? | changes the envelope? | when |
|---|---|---|---|
| T-81a | no | **yes**, 12% in $\ell_D$ | v1.4.0 |
| T-81b | no | **yes**, and is a *named mechanism for the missing ISW* | **next measurement** |
| T-81c | no | **yes** | v1.4.0 |
| T-81d | no | **yes**, visibility width | v1.4.0 |
| T-81e | unknown | unknown | after it is read |

**Not one of these can open or close the frame gap** — none is
frame-dependent, so none redistributes between intrinsic temperature,
velocity, acceleration and shear. They move the envelope **under** the number
the week is measuring. Fixing an envelope term mid-measurement changes that
number for reasons unrelated to it, which is the M4 error with a schedule
attached. **T-81b is the exception and is promoted**, because the missing late
ISW is a separate open defect that has had no named cause since it was raised,
and it now has one.

---

## T-82 — $v_B+\sigma$ agrees between the columns to machine precision. **The source is not where the frame gap is.**

**2026-10-19, late. P1-T's conversion of CAMB's source into this bundle's
slots, run as the action item it was offered as.** CAMB carries the rank-1
scattering source as $g\,(v_b+\sigma)$ — **one object**. Under a boost
$v_b\to v_b-v$ while $\sigma$ shifts oppositely, so the sum is invariant and
*CAMB has no frame gap because it never separates them.* This bundle does
separate them, so the two columns must produce the same sum.

**Strictly stronger than the frame gap on $\tau_\ell$**: no transfer function,
no $j_\ell$, no weight, no damping, no validity gate. A failure is upstream of
everything (102) does. `scripts/diagnostic_d12_vb_plus_sigma.py`,
`diagnostics/d12-vb-plus-sigma-v1.3.0.txt`.

| background | $k$ | $\lvert\Delta(\hat v_B-C_2)\rvert$ | $\lvert\Delta(\hat v_B+C_2)\rvert$ |
|---|---:|---:|---:|
| EdS | 1 | 1.098 | $\mathbf{9.34\times10^{-16}}$ |
| EdS | 10 | 1.095 | $\mathbf{1.61\times10^{-15}}$ |
| EdS | 60 | 1.043 | $\mathbf{4.25\times10^{-15}}$ |
| EdS | 300 | 1.003 | $\mathbf{6.53\times10^{-14}}$ |
| PLANCK | 1 | 1.090 | $\mathbf{1.25\times10^{-15}}$ |
| PLANCK | 10 | 1.083 | $\mathbf{1.64\times10^{-15}}$ |
| PLANCK | 60 | 1.020 | $\mathbf{1.02\times10^{-14}}$ |
| PLANCK | 300 | 1.001 | $\mathbf{1.80\times10^{-13}}$ |

**$\hat v_B+C_2$ is the CAMB combination and it is invariant to machine
precision at every $k$ on both backgrounds.** The residual against the boost
$v/k$ runs $1.7$–$4.1\times10^{-16}$ throughout, and is aligned with neither
the boost nor $\mathrm d\hat v_B/\mathrm d\eta$.

### What this decides

**The rank-1 source is frame-consistent before projection.** The gap measured
at T-77 and T-79 is therefore **downstream** of the source — in the slot and
weight assignment, which is P1-T's items 2 and 3:

> **2.** The rank-1 slot takes two different things under two different
> weights. $M$'s by-parts residue enters under $W$; $(v_b+\sigma)$ enters
> under $g$. $C_1=-(\delta T+\Phi_A+qU/k)$ bundles both and gives them one
> weight. *That is §5.3's split with the weights now specified — which §5.3
> did not do, and which is why the split helped but did not close.*
>
> **3.** $M$ belongs in the $j_\ell$ slot, not $j_\ell'$. Converting it into
> the $j_\ell'$ slot generates a boundary carrying $W$ and a bulk
> $-\int WM'j_\ell$. **This bundle's boundary carries $\mathcal D(k)$ and no
> $W$; its bulk carries $+\int g\,(-C_1')j_\ell$. Weight and sign both differ
> from the identity.**

**This reorders the work**, and the reorder is the finding's practical content.
The PI's proposed order was *source construction → coupled gravitational
driving → decoupling and diffusion*. **The first item is discharged by this
measurement**: the source is already consistent, and T-77's split "helped but
did not close" for the reason item 2 names. The frame gap now has exactly one
place left to be, and it is item 3's slot-and-weight mismatch.

### P1-B ran this wrong first, and the guard written an hour earlier caught it

**`CoefficientSet.v_b` is the *un-reduced* dipole** — both sets store
`v_b = k * vb_t` (`coefficients.py:677` and `:983`) while $C_2=v/k$. The first
run of D12 differenced them **as stored**, mixing normalisations. That is
**M4**, and it is the **third M4 in one day** (T-79's $\kappa'\tau_0$ gap, and
T-68's amplitude pair before it).

It produced a table that read as a catastrophic frame failure — invariance at
$k=1$ and $O(1)$ violation at every other $k$ — and **it would have been
reported** but for the discriminator built into the script before it was run:

```
  bg       k   |res|/|v/k|
  EdS      1     1.669e-16
  EdS     10     9.000e+00
  EdS     60     5.900e+01
  EdS    300     2.990e+02
```

$9$, $59$, $299$ at $k=10,60,300$ is **exactly $k-1$**, and $\mathrm{corr}(\text{res},v/k)=1.000$.
**A residual that is an exact integer multiple of the thing it is compared
against is the signature of a normalisation, not of a dynamics** — and $k=1$
passing is not a physical scale, it is the one $k$ at which reduced and
un-reduced coincide.

**The guard was M11b's second clause**, written into the script as a validity
condition before the number was read, for a different purpose — to separate a
boost failure from a phase error between two integrations. It separated a
third thing instead. **Recorded because a guard that catches what it was not
written for is the only evidence that the guard is real**, and because this
register now carries the same mode three times in one day, which is the
argument for the column rather than for the maxim.

*The script is fixed to reduce before differencing and the comment at the
fix site says why. The uncorrected table is not in `diagnostics/`; it is
above, in full, because a withdrawn number that is not shown cannot be
checked.*

### The overnight F9, which arrived after this entry was written, and makes it sharper

The PI's overnight F9 run, 2026-10-19 16:49, local:

```
CDM (Einstein-de Sitter)   first peak l=280.4;  frame gap median 100.0% worst 100.0%
$\Lambda$CDM               first peak l=224.5;  frame gap median 100.0% worst 100.0%
PLANCK_MODEL               first peak l=341.7;  frame gap median 100.0% worst 340.8%
CAMB                       first peak at l=206.1
CLASS                      first peak at l=206.2
```

**The frame gap at the spectrum is 100%.** Set that beside this entry's
measurement — $\lvert\Delta(\hat v_B+C_2)\rvert$ between $9\times10^{-16}$ and
$2\times10^{-13}$ — and the two numbers together say something neither says
alone:

> **The source is frame-consistent to fourteen significant figures and the
> spectrum it produces is 100% apart.** Everything between the two is the
> projection: the slot assignment and the weights. There is no longer a
> *range* of places the frame gap can be; T-82 closes the upstream end and F9
> measures the downstream end at saturation.

That is P1-T's items 2 and 3 with nothing else left beside them, and it is the
first time this register can say so rather than rank it.

### The peaks, which are a second and separate finding

| | first peak | $\ell_A$ | ratio |
|---|---:|---:|---:|
| EdS | 280.4 | 192.663 | **1.455** |
| LCDM | 224.5 | 172.71 | **1.300** |
| PLANCK | 341.7 | 272.177 | **1.255** |
| CAMB | 206.1 | — | — |
| CLASS | 206.2 | — | — |

**CAMB and CLASS agree to 0.05%**, which is the external comparison working
and is worth stating before the discrepancy.

**The first peak should sit *below* $\ell_A$, near $0.7$–$0.8\,\ell_A$**, and
in all three backgrounds it sits **above** it. The ratio is not constant —
1.455, 1.300, 1.255 — so **it is not a single missing factor**, and
`provenance/MODEL-PARAMETERS-v1.3.0.md`'s test applies in the negative: three
models whose peaks do not track their own $\ell_A$ do **not** differ by a
parameter.

**This is not the frame gap and must not be folded into it.** $\ell_A$ is
computed from the background alone and is frame-independent; a peak in the
wrong place relative to its own $\ell_A$ is a statement about the projection's
$\ell$–$k$ correspondence, not about the two columns. It is recorded as its
own thread. **It is also the PI's standing objective** — *getting the acoustic
peaks working* — so it is first in the order, beside items 2 and 3, and the
two may well be one defect: a slot that enters under $j_\ell'$ instead of
$j_\ell$ shifts power in $\ell$, which is exactly item 3.

---

## T-83 — $\ell_A$ for all three backgrounds. **P1-T's 192.7 is EdS; PLANCK is 10% low, not 36%; LCDM is where the omitted radiation shows**

**2026-10-19, late. No run: the numbers are already generated**, in
`provenance/MODEL-PARAMETERS-v1.3.0.md`, which `scripts/make_model_table.py`
builds from the `Background` objects the code integrates. P1-T asked for one
number and the table has three.

| | $r_\theta$ | $r_s$ | $\ell_A=\pi r_\theta/r_s$ | against $\simeq302$ |
|---|---:|---:|---:|---:|
| **EdS** | 1.94041 | 0.0316406 | **192.663** | *not applicable* |
| **LCDM** | 3.1955 | 0.0581262 | **172.71** | $0.572\times$ |
| **PLANCK** | 3.12897 | 0.0361159 | **272.177** | $\mathbf{0.901\times}$ |

### The three answers

**1. P1-T's 192.7 is EdS**, from their own $r_\theta=1.9404$, $r_s=0.031641$ —
the EdS row to six figures. Their first branch applies: *"if it is EdS it is
expected and means nothing."* $\Omega_m=1$, $h=0.5$, no $\Lambda$: its $\ell_A$
is not supposed to be 302 and the comparison is void. **The $0.64\times$ does
not stand**, and the inference drawn from it does not either.

**2. PLANCK is $0.901\times$, not $0.64\times$.** A 10% deficit in the acoustic
scale. That is real and it is open — it is the **T-51/S40** sound-horizon
thread, where $r_s$ is integrated from the big bang — but it is a tenth of
what was inferred, and a 10% error cannot be what misplaces the peaks, because:

**The peaks are misplaced in the opposite direction.** The overnight F9 puts
PLANCK's first peak at $\ell=341.7$ against its own $\ell_A=272.177$, a ratio
of **1.255** where it should be $\simeq0.75$. An $\ell_A$ that is **too small**
moves peaks **down**. The measured peaks are **up**, by $1.67\times$. So the
$\ell_A$ deficit and the peak misplacement have **opposite signs** and the
second is not caused by the first. **The peak position is in the projection**,
which is what T-82 and P1-T's item 3 say.

**3. LCDM is where the omitted radiation shows, and the direction is P1-T's.**
LCDM and PLANCK differ in $\Omega_m$ by 0.3 against 0.3138 — four percent —
and in $\ell_A$ by **37%**. The mechanism is exactly the one P1-T names:

| | $\eta_*$ | $r_s$ |
|---|---:|---:|
| LCDM ($\Omega_r=0$) | 0.109581 | 0.0581262 |
| PLANCK ($\Omega_r=5.45\times10^{-5}$) | 0.0697426 | 0.0361159 |
| **ratio** | **1.571** | **1.610** |

*Matter domination earlier, larger $\eta_*$, larger $r_s$, smaller $\ell_A$* —
confirmed, at $1.6\times$ in both. **T-81c is therefore not only an envelope
concern**: on LCDM it is a peak-position error of 37%, independent of every
source question. The T-81 triage table's *"changes the frame gap? no"* stands;
its *"envelope"* column understates it for LCDM and is corrected here.

### The validity note P1-T asked for, beside the 2%

> **P1-B's effective-sound-horizon measurement — 2%, against the 11% the
> radiation-driving mechanism needs — compared the solver's effective $r_s$
> against the $r_s$ the code computes from the same background. Both are
> wrong together if the background is. An internal-consistency check is blind
> to a background error by construction.**

That is **M4**'s shape and it is recorded here rather than left in a message.
The 2% is not withdrawn — it is correct for what it measures, which is the
solver against its own background — but it **cannot** bound a background
error, and it was offered as if it could. The three-column table above is the
check that is not blind to it, and it exists because the PI asked for a model
table two days ago for exactly this reason.

---

## T-84 — the published preprint's title is `CMBR`; decision S17 fixed `CMB`. **Raised, not silently normalised**

**2026-10-20. The PI supplied the Paper 1 preprint reference and the record
does not say what the bundle says.**

| | string |
|---|---|
| Zenodo record 23475234, title as printed | *Frame covariance of **CMBR** lensing in the exact 1+3 covariant radiation hierarchy* |
| attached file | `TG-FrameCovariantCMBR-v1.1.6.pdf` |
| decision **S17**, accepted 2026-10-07, **closed 2026-10-09 on the manuscript freeze** | *Frame covariance of **CMB** lensing in the exact 1+3 covariant radiation hierarchy* |
| `README.md`, `CITATION.cff`, `SUPPLEMENTARY-MATERIAL-v1.3.0.tex` before today | `CMB` |
| the PI's own message supplying the reference, 2026-10-20 | `CMB` |

**Read twice off the record, the second time asking for a character-for-character
transcription with no normalisation**, because a summariser silently correcting
`CMBR` to `CMB` is exactly the failure this would look like. Both reads return
`CMBR`, and the filename carries it independently.

### What was changed, and why this way

**The citation slots now carry the record's string.** A citation reproduces the
title of the thing it points at or it does not resolve for a reader, and the
record is the artefact. The supplement's own title and its two prose references
to its companion were changed with them, because a supplement naming a
companion that does not exist under that name is the cohesion failure mode
this project already has on file — a correction landing where it was found and
not travelling to the places that restate it.

Changed: `README.md` (header, and the *Associated paper* row), `CITATION.cff`
(`preferred-citation`), `SUPPLEMENTARY-MATERIAL-v1.3.0.tex` (`\title`, the
abstract, §*Scientific scope*). **Not** changed: `SUPPLEMENTARY-MATERIAL-v1.2.0.tex`,
which is a frozen released artefact, and **S17 itself**, which is a PI decision.

### Why it is raised rather than corrected silently

The standing rule makes a typographical difference silent and a material one
correctable-with-a-log. **This is neither.** Two artefacts that are supposed to
name one paper name two, and *which string is canonical is not determinable
from either of them*:

- If **S17 is right**, the Zenodo record's title is wrong and fixing it means
  **uploading a new version**, which mints a new version DOI and makes the one
  now in `README.md` point at a superseded record.
- If **the record is right**, S17 was superseded on 19 October by an act that
  did not reach the decision register, and S17 should be amended to say so.

**Only the PI can say which**, and the cost is asymmetric enough that guessing
is not available: one branch changes a published DOI.

### The second thing the record does not have

**No concept DOI.** `10.5281/zenodo.23475234` is a **version** DOI: the record
exposes no *Cite all versions* entry and its Versions list is empty. This
bundle's own `README.md` already argues, for the ZivaHub DOI, that *the concept
DOI is the one to cite because it resolves to the latest version* — and the
Zenodo row cannot honour that yet. **Stated in the table rather than left for a
reader to discover**, and it interacts with the branch above: a v1.1.7 uploaded
to fix the title would strand the string now published in this README.

---

## T-85 — the $2\times2$. **Both identities hold; $A_N\neq A_C$. The constructor conclusion is proven, not inferred**

**2026-10-20. P1-T's decisive check, which displaced their own one-frame
boundary test of the day before.** The same transport source $M=-C_1$
evaluated directly and through its fully integrated-by-parts form, identical
histories and identical endpoints, in both frames.

$$\int \mathcal V M j_\ell\,\mathrm d\eta=\bigl[W M j_\ell\bigr]-\int W M' j_\ell\,\mathrm d\eta+k\int W M j_\ell'\,\mathrm d\eta$$

`scripts/diagnostic_d13_byparts_2x2.py`, `diagnostics/d13-byparts-2x2-v1.3.0.txt`.

### Result 1 — both identities hold. **It is not bookkeeping.**

$\lvert A-B\rvert/\lvert A\rvert$ sits at $10^{-3}$–$10^{-2}$ in every valid
cell **and falls under grid refinement**, which is the discriminator and was
measured rather than assumed:

| background | $k$ | $\ell$ | $1\times$ | $2\times$ | $4\times$ |
|---|---:|---:|---:|---:|---:|
| EdS | 10 | 2 | $2.83\times10^{-3}$ | $2.20\times10^{-3}$ | $2.04\times10^{-3}$ |
| EdS | 300 | 2 | $1.105$ | $0.279$ | $0.0727$ |
| PLANCK | 10 | 200 | $8.68\times10^{-4}$ | $2.35\times10^{-4}$ | $7.74\times10^{-5}$ |
| PLANCK | 300 | 2 | $9.230$ | $2.326$ | $0.598$ |

The $k=300$, $\ell=2$ cells start large and fall by $\simeq4\times$ per
doubling — second order, which is what `trapezoid` on an oscillatory integrand
gives. **Quadrature, not a defect.**

> **$A$ and $B$ are the same integral by an exact identity, so a difference
> has only two available explanations and one of them has now been measured
> away.** The $\eta_*$-boundary-against-`eta_floor` mixing P1-T named as the
> first suspect **is excluded.**

**One cell is void and is not read:** EdS $k=10$, $\ell=200$, where the ratio
is $2.646$ and does **not** fall under refinement — because $A=-3.9\times
10^{-176}$. That is $\ell\gg k\Delta\eta$ ($k\Delta\eta\simeq19.4$), the
validity condition already in P1-B's diagnostic register, and both numbers are
noise. **It is in the table rather than removed from it**, because a cell
dropped silently is a cell a reader cannot check.

### Result 2 — $A_N\neq A_C$ in every valid cell, by $1.00$ to $1.78$ of scale

| background | $k$ | $\ell$ | $A_N$ | $A_C$ | $\lvert A_N-A_C\rvert/\max$ |
|---|---:|---:|---:|---:|---:|
| EdS | 10 | 2 | $1.8666\times10^{-1}$ | $-5.0149\times10^{-2}$ | **1.269** |
| EdS | 60 | 2 | $-9.2737\times10^{-3}$ | $4.5815\times10^{-3}$ | **1.494** |
| EdS | 300 | 200 | $-5.2384\times10^{-4}$ | $3.4448\times10^{-3}$ | **1.152** |
| PLANCK | 10 | 10 | $1.4919\times10^{-1}$ | $-5.7453\times10^{-2}$ | **1.385** |
| PLANCK | 60 | 200 | $-5.7596\times10^{-4}$ | $4.4693\times10^{-4}$ | **1.776** |
| PLANCK | 300 | 50 | $-1.3534\times10^{-5}$ | $1.6379\times10^{-3}$ | **1.008** |

**This is P1-T's second branch, taken:** *"Both identities hold but
$A_N\neq A_C$ → coefficient definitions, upstream of (102). Your constructor
conclusion, proven rather than inferred."* The sign flips between columns in
every row, which is the whole of the frame gap and not a fraction of it.

### Result 3 — the $\ell$-independence is **the visibility, not the frames**, and is not reported as a finding

At $k=10$ the ratio $A_C/A_N$ is $\ell$-free to four figures
($-3.72208$, $-3.71998$, $-3.72062$ at $\ell=2,10,50$ on EdS), and P1-T's own
earlier criterion reads an $\ell$-independent residue as *still constructor*.
**It carries no information here, and the reason is mechanical:** $\mathcal V$
is a spike, so $\int\mathcal V f j_\ell\simeq f(\eta_*)j_\ell(x_*)\int\mathcal V$
for **any** $f$, and the ratio of two $\mathcal V$-weighted integrals is
$f_C(\eta_*)/f_N(\eta_*)$ — $\ell$-free by construction, whatever the frames do.

Measured against that prediction:

| background | $k$ | $A_C/A_N$ | $M_C/M_N$ at $\eta_*$ | agreement |
|---|---:|---:|---:|---:|
| EdS | 10 | $-0.2688$ | $-0.2574$ | **4.2%** |
| EdS | 60 | $-0.4508$ | $-0.4462$ | **1.0%** |
| PLANCK | 10 | $-0.3851$ | $-0.3818$ | **0.9%** |
| EdS | 300 | $-7.3793$ | $-5.4682$ | 25.9% |
| PLANCK | 300 | $-0.1934$ | $-18.2734$ | 9346% |

**Confirmed where the spike approximation holds and failing where it does
not** — at $k=300$ the mode oscillates inside the visibility width, and the
$2\times2$'s own $k=300$ rows are correspondingly **not** $\ell$-free
($A_C/A_N$ runs $-7.38$ at $\ell=10$ and $-0.152$ at $\ell=200$).

*Recorded under **M11** before the result it sits beside.* The
$\ell$-independence was about to be reported as corroboration and it is an
artefact of the weight. Stating it costs one run and removes a finding rather
than adding one.

### What the $2\times2$ and T-82 say **together**, which neither says alone

| | measured | verdict |
|---|---|---|
| the rank-1 **source**, $\hat v_B+C_2$ (T-82) | $9\times10^{-16}$ – $2\times10^{-13}$ | **frame-consistent** |
| the by-parts **identity**, $\lvert A-B\rvert/\lvert A\rvert$ (T-85) | quadrature, falls under refinement | **not bookkeeping** |
| the rank-1 **slot**, $A_N$ against $A_C$ (T-85) | $1.00$–$1.78$ of scale, sign flipped | **the whole gap** |

> **The object is right, the integral is right, and the split of the object
> across the slots is wrong.** That is P1-T's item 2 stated as a measurement
> rather than as a reading of CAMB: *the rank-1 slot takes two different
> things under two different weights — $M$'s by-parts residue under $W$ and
> $(v_b+\sigma)$ under $g$ — and $C_1$ bundles both and gives them one
> weight.* Both ends are now measured and nothing is left between them.

**This is why §5.3's split helped and did not close** (T-75, T-77): splitting
$C_1$ without also splitting its **weight** fixes half of a defect whose two
halves were never independent. That is **M11a** once more, and the third time
this register has recorded it.

### T-84 closed, 2026-10-20

The PI supplied the citation in the record's form —
*"Gebbie, T. (2026). Frame covariance of CMBR lensing in the exact 1+3
covariant radiation hierarchy (Version v1.1.6). Zenodo.
https://doi.org/10.5281/zenodo.23475234"* — so the branch is taken: **the
record is canonical and `CMBR` is the title.** Decision **S17** is amended in
place with that date and this finding's number, rather than the Zenodo record
being re-uploaded, which keeps the published DOI resolving to the version the
bundle now cites. The second half of T-84 stands open and is not closed by
this: **the Zenodo row carries a version DOI, not a concept DOI**, and the
README says so.

---

## T-86 — the B-slot read. **The identity's three terms all carry $W$; the bundle's two carry $\mathcal D$ and $\mathcal V\mathcal D$, and the third is absent**

**2026-10-20. P1-T's §8 item 1, and it is a read, not a run.** The shape they
predicted is the shape the code has. Under their §9 that keeps the frame gap's
named site; had it not matched, the gap would have returned to having none.

### The identity, and the bundle beside it

$$\int g M j_\ell=\underbrace{\bigl[W M j_\ell\bigr]}_{W}\;\underbrace{-\int W M' j_\ell}_{W,\ \text{minus}}\;\underbrace{+\,k\!\int W M j_\ell'}_{W,\ M\ \text{undifferentiated}}$$

| | the identity requires | `functions/spectra/integral_solution.py` has | line |
|---|---|---|---|
| **boundary** | $\bigl[W M j_\ell\bigr]$, weight $W=e^{-\kappa}$ | `(c2_prime_star - c1_star) * damping_total * j_l_star` — weight $\mathcal D(\eta_0,k)$, a **diffusion** factor, with no $W$ and no $\mathcal V$ in it | 226 |
| **$j_\ell$ bulk** | $-\int W M' j_\ell$, weight $W$, **minus** | `integrand_weight * bracket * j_l` with `integrand_weight = weight * diffusion` and `bracket = c0 - c1_prime + c2_second` — weight $\mathcal V\mathcal D$ under the T-69 default, **plus** | 206, 240 |
| **$j_\ell'$ bulk** | $+k\int W M j_\ell'$, $M$ **undifferentiated** | **nothing. The bulk has no $j_\ell'$ slot at all.** | — |

**All three of the identity's terms carry $W$. The bundle's two carry
$\mathcal D$ and $\mathcal V\mathcal D$. Not one of the three weights matches,
and the third term has no counterpart.**

### Why there is no $j_\ell'$ slot, which is the structural half

Everything was by-parted **onto the coefficients** — $\{C_0-C_1'+C_2''\}$ is
(102)'s printed bracket, and it is the $W$-weighted by-parts form of
$\int W[C_0K+C_1K'+C_2K'']$. **That decomposition is not available at $g$
weight**, and the bundle then evaluates it at $g$ weight. P1-T's sentence, and
the code says it in two lines.

The boundary is Annals II's own `visibe` collapse: under $\int\mathcal V=1$
the $-\mathcal V C_1$ term becomes $C_1(\eta_*)$, which is what line 226
evaluates. **So the bundle carries one term from each of two incompatible
decompositions** — (102)'s $W$-weighted bracket in the bulk and the
$\mathcal V$-collapsed primary at the boundary — and then applies a third
weight, $\mathcal D$, to the second and $\mathcal V\mathcal D$ to the first.

### The machinery for the missing slot already exists

$j_\ell'=\bigl[\ell j_{\ell-1}-(\ell+1)j_{\ell+1}\bigr]/(2\ell+1)$ is **already
built in this file**, at line 235, inside the rank-2 *boundary* term:

```python
combination = (l / (2 * l + 1)) * j_lm1 - ((l + 1) / (2 * l + 1)) * j_lp1
```

That is $j_\ell'(x_*)$ under another name. **The recurrence is present, in the
one slot that has never been evaluated** — it is guarded by `if c2_star == 0.0`
and $C_2$ is zero in every Newtonian run. So the missing bulk slot needs no new
numerics, only the term.

### What the fix is, stated so it can be refuted

**Not a split of the slot. A split, plus a weight change on each half, plus a
slot the bulk does not have.** In P1-T's words and now in the code's:

1. $C_1$'s two contents separate — $M$'s by-parts residue and $(v_b+\sigma)$.
2. They take **different weights**: $W$ for the gravitational half, $g$ for the
   scattering half. One weight for both is the defect T-85 measured.
3. The $W$-weighted half needs **both** bulk slots, $j_\ell$ **and**
   $j_\ell'$, because by-parting onto the coefficients is what removed the
   second and that step is only legal at $W$.

**And C6 is the same change seen again.** T-81b's *"the integrand carries a
diffusion factor at all"* is this table's second row: $\mathcal D$ multiplying
a gravitational source generated where no scattering occurs. **Scattering
damping belongs to the scattering half and not to the gravitational one**, so
the split that fixes the weights fixes the damping in the same stroke. One
change, three symptoms — the frame gap, the missing late ISW, and the
$\mathcal D$-on-the-boundary mismatch.

### Validity, stated before the next step

**This is a read.** It establishes what the code does, not that changing it
closes the gap. The test is already specified and is cheap: the split must
leave T-85's $A_N$ and $A_C$ **equal** and must not move the Newtonian column
by more than the quadrature floor T-85 measured. **Frame agreement alone will
not do** — two wrong columns can agree — so the spectrum adjudicates, and it
adjudicates last.

---

## T-87 — project audit: the record had drifted from the tree in fourteen places, and three of them were load-bearing

**2026-10-20, at the PI's direction.** A mechanical sweep for staleness,
dangling references, orphans, superseded claims and duplication. **It is an
audit of the record, not of the physics**, and it is recorded here because the
record is a deliverable of this bundle rather than packaging around one.

### The three that were load-bearing

**1. D11, D12 and D13 had no generator.** `diagnostics/d11-*.txt`,
`d12-*.txt` and `d13-*.txt` were **hand-captured console redirects** — the
three scripts printed to stdout and wrote nothing — and the files were hashed
into `FILE-MANIFEST-SHA256.txt` and `PORTABLE-MANIFEST-SHA256.txt` **as if
they regenerated**. `BUNDLE-DEFECTS-v1.md` cites d12's and d13's files as the
evidence for T-82 and T-85.

> **A number in this register whose artefact cannot be regenerated is a
> transcription, and this register's own clause M5a says a claim about an
> artefact is read off the artefact or it is not made.** The clause was landed
> at T-79 and the first thing it binds is the evidence for T-82 and T-85.

Fixed: each now writes its own file through a `_report()`/`main()` split, and
**all three are registered in `scripts/run_all.py`'s `DIAGNOSTICS`**, so they
run on a release route. Re-run after the change, all three exit 0 and
reproduce their committed tables.

**2. Decision **S17** closed twice, with two answers.** The row at
`DECISIONS-v1.0.0.md:153` still read *"CLOSED 2026-10-09 … the title is
settled — Frame covariance of **CMB** lensing"* while S17 itself, 116 lines
above in the same file, had been amended to **CMBR** on 2026-10-20 by T-84.
**One register, two canonical titles.** Corrected, with the history kept: the
2026-10-09 closure stood for eleven days against a record that reads `CMBR`.

**3. `captions/FIGURE-PLAN-v1.0.0.md` names `scripts/figure_f3_spectrum.py`,
which does not exist.** The script is `figure_f3_angular_spectrum.py`. Every
other row in that table resolves. Corrected.

### Superseded claims that were still standing

| where | the claim | superseded by |
|---|---|---|
| `README.md` ×2 | the Hu & Sugiyama cross-check is *"deferred to v1.5.0 (S35)"* | **S35a**, which promoted it to v1.3.0's method and which the same README cites twice elsewhere |
| `README.md` | *"The regression suite passes and `run_all.py --strict` reports `CLEAN`"* | **T-54** — the finding that `CLEAN` was printed over a two-day-old spectrum — and the same README's figure table, which records F9 as *unrun and failing its fingerprint correctly*, eighty lines later |
| `README.md` | T-84 presented as a live discrepancy | T-84's own closure, same day |
| `captions/F5-sources.md` | frame gap *"median 15%, worst 49% … not a defect"* | **T-57**, **T-59** — it is total, and $\ell\ge2$ is frame-invariant by theorem |
| `captions/F9-acoustic-spectrum.md` | frame gap *"median 40% … a result and not a defect"* | the same |
| `captions/F2-truncation.md` | truncation cost *"0.54–0.68% … 32.6%"* | **T-57** — $99.93\%$ and $100\%$ |

**The three captions are annotated, not overwritten.** Decision **V15** makes
a caption the figure's *specification*, and these figures predate T-57, so
replacing the numbers would describe a figure that does not exist. Each now
carries a dated *Superseded* block naming the finding and pointing at this
register, and says it is not regenerated until the figure is.

### Stale counts, corrected

`README.md` advertised the registers as **T-1…T-50** (now T-87), **S1…S39**
(now S42) and **B-1…B-14** (now B-15), and said *"fourteen findings"* against
the antecedent in three places and *"the 424 tests in this tree"* in one —
in a paragraph that elsewhere forbids typing a test count because *"the
previous version of this paragraph came to claim a test total that was 36
short."* **The paragraph had done it again.** The count is replaced by a
pointer to `pytest -q`. The dated decision prose in **S37** and **S38** keeps
its 2026-10-16 numbers: that is historical quotation and is correct.

### Raised, not fixed — these need the PI

**`RELEASE-NOTES-v1.0.0.md` says *"Status: in preparation. Not released."***
and `README.md` says v1.0.0 has a *"frozen public tag, release asset and
archived DOI"*, and `dist/` holds v1.1.0 and v1.2.0 and **no v1.0.0 archive**.
Three statements, at most two of which can be true. `CHANGELOG.md` carries two
`## [Unreleased]` headings for this reason, and `scripts/run_all.py:197`'s
released-version regex matches neither — so **v1.0.0 is invisible to the
harness's released-version check**, which is the mechanism T-47 added to refuse
a deferral to an already-released version. **Not guessed at**: whether v1.0.0
was tagged and whether the ZivaHub DOI covers it is the PI's to say, and the
fix differs by branch.

**Decisions `S43`, `S44` and `S-b` are referenced as live and are in no
register.** `S44` in `README.md`, `BUNDLE-DEFECTS-v1.md` and
`OPEN-QUESTIONS-v1.0.0.md`; `S43` in `BUNDLE-DEFECTS-v1.md`; **`S-b` in nine
places including `scripts/run_all.py` ×5**, where the harness prints it to an
operator as the authority for a deferral. The register runs S1…S42 and its
*Still awaiting a decision* table lists none of the three. **Either they are
decisions and belong in the register, or they are placeholders and must not be
printed as authorities.** Needs one line from the PI each; `S-b` additionally
needs a real identifier before the next release route runs.

**`captions/F7-frames.md` and `provenance/RELEASE-STATUS-v1.md` say the worst
frame ratio is $1.25\times$; `README.md:705` says $1.24\times$.** One is
wrong. **It could not be adjudicated from the artefact**: `outputs/f7-frames.csv`
carries `frame_difference` as a *fraction* (max $0.0999$), which is neither
number, so the ratio is computed somewhere the committed output does not hold.
**Stated as unadjudicated rather than resolved by picking one**, which is M5a.

**`provenance/RELEASE-STATUS-v1.md` has no v1.3.0 section at all**, because
`scripts/make_release_status.py:353` enumerates only `v1.0.0, v1.1.0, v1.2.0,
v1.5.0`. The tree is v1.3.0-dev with D9–D13, S40–S42 and T-51…T-87 landed and
**none of it has a rung on S27's maturity ladder.** The generator needs a
v1.3.0 row written for it; what belongs on that rung is a release decision.

### What this audit does not cover

**Nothing here touches the physics or the mathematics.** The frame-gap chain
T-82/T-85/T-86 is untouched by it, and no finding in this entry changes a
coefficient, a sign, an $\ell$-weight or a result. The one thing it changes
about the *evidence* is item 1 — that three diagnostics now regenerate — and
that strengthens the chain rather than altering it.

---

## T-88 — the repair. **$C_2$ must travel with $\hat v_B$ under $g$, and when it does the frame gap falls by four orders at $\ell\ge50$**

**2026-10-20. The B-slot repair of T-86, implemented as four controls and
measured over the lattice.** `scripts/diagnostic_d14_slot_repair.py`,
`diagnostics/d14-slot-repair-v1.3.0.txt`. Every control defaults `False`;
`tests/test_integral_solution.py` passes unchanged and the released row of
every table below shows `Newt moved = 0.000e+00`, so nothing shipped has moved.

### The first attempt failed, and the way it failed is the finding

T-86 specified: split $C_1$ into its gravitational and Thomson halves, give the
gravitational half $W$ and the Thomson half $g$, and supply the missing
$j_\ell'$ bulk slot. Implemented exactly, **it does not close the gap** — EdS
$k=10$ moves $1.2847\to1.1027$ at $\ell=2$ and *rises* $1.2854\to1.3750$ at
$\ell=10$ — and at $k=300$ it rewrites the Newtonian column by $111\%$.

**Why: it separated the one pair T-82 had just shown must stay together.**
P1-T's reading of CAMB is that the rank-1 scattering source is
$g\,(v_b+\sigma)$ — *one object* — and T-82 measured that in this bundle's
variables the boost-invariant combination is $\hat v_B + C_2$, to $10^{-15}$.
The split put $\hat v_B$ under $g$ and left $C_2$ in the rank-2 sector under a
different weight. **The CDM column is where $C_2\ne0$, which is exactly where
it broke.**

So the Thomson slot must carry $-\kappa'(\hat v_B + C_2)$, not
$-\kappa'\hat v_B$. **The added piece $-\kappa'C_2$ is a term this bundle has
nowhere at present.** That is control 4, `thomson_carries_shear`.

### With it, measured

Frame gap $\lvert c-n\rvert/\max$, all four controls on, against the released
row:

| background | $k$ | $\ell=2$ | $\ell=10$ | $\ell=50$ | $\ell=200$ |
|---|---:|---:|---:|---:|---:|
| EdS | 10 | $1.2847\to\mathbf{0.1454}$ | $1.2854\to\mathbf{0.0895}$ | $1.2854\to\mathbf{2.6\times10^{-3}}$ | $1.2921\to\mathbf{8.5\times10^{-5}}$ |
| EdS | 60 | $1.5642\to1.0376$ | $1.6169\to1.3283$ | $1.6490\to\mathbf{0.4220}$ | $1.6205\to\mathbf{3.8\times10^{-3}}$ |
| PLANCK | 10 | $1.4159\to1.0209$ | $1.4343\to\mathbf{0.1347}$ | $1.4349\to\mathbf{4.8\times10^{-3}}$ | $1.4372\to\mathbf{3.5\times10^{-3}}$ |
| PLANCK | 60 | $1.6705\to1.0239$ | $1.6187\to1.0309$ | $1.4619\to1.0251$ | $1.7426\to\mathbf{0.0221}$ |
| EdS | 300 | $1.0362\to0.9999$ | $1.0342\to0.9998$ | $0.8272\to0.9998$ | $1.0295\to1.0008$ |
| PLANCK | 300 | $0.9961\to0.9998$ | $0.9962\to0.9998$ | $0.9943\to0.9995$ | $0.9957\to1.0004$ |

**Four orders of magnitude at $\ell=200$, on both backgrounds, at $k=10$.** And
the cell that matters most for the acoustic peaks is PLANCK $k=60$,
$\ell=200$: with $r_\theta=3.129$, $\ell\simeq k r_\theta$ puts the first peak
region there, and it moves $1.7426\to0.0221$ — **a factor of 79**.

**`thomson_carries_shear` is the whole of it.** Every row with `split` and
without it stays at $O(1)$; every row with both collapses. `jprime_bulk_slot`
and `boundary_weight_w` move the third and fourth figure and nothing more.
**That is M11a again, and the fourth instance in this register**: three of the
four controls score as failures alone, and the set was not found by ablation
but by reading T-82 forwards.

### What does not work, stated with the result rather than after it

**$k=300$ is untouched** — every cell sits at $\sim1.0$ with the controls on,
and the split moves the Newtonian column by $1.1$ on EdS and $\mathbf{7.1}$ on
PLANCK. The gravitational half's weight is not right there. That is **A-2's
own statement** (**T-20**: *the two weightings are each right in one regime and
neither in both*), now visible as a $7\times$ rewrite rather than as a choice.

**$\ell=2$ does not close anywhere**, and $\ell=10$ closes on EdS $k=10$
($0.0895$) and PLANCK $k=10$ ($0.1347$) but not at $k=60$. The low-$\ell$,
low-$k$ corner is a separate residue.

### A correction to this entry's own acceptance condition

T-86 wrote two conditions: the gap must fall, **and** the Newtonian column must
not move by more than D13's quadrature floor, $2.2\times10^{-3}$. **The second
condition is not a clean test and it should not have been written that way.**
Moving the gravitational half from $\mathcal V$ to $W$ *is* **A-2**, whose
basis **T-69** recorded as void — so the Newtonian column is expected to move,
and a condition that forbids it presumes the column is right on a weight
choice this register already questions. **M4**: the condition compared two
numbers across a normalisation the change itself alters.

The condition is replaced by one that can be met: **the Newtonian column may
move by the amount A-2 accounts for, and no more**, which is measurable by
running the released code under `line_of_sight_weight="opacity"` and
differencing. That measurement has not been made and the claim above is
therefore bounded: *the gap falls*, and *whether the column that moved was
right* is open.

### Order from here

1. **Measure the A-2 bound** so condition 2 becomes decidable — one run of the
   released code under the other weight.
2. **The spectrum**, with `split + jprime + thomson_carries_shear` on, as a
   **diagnostic and not a release figure**. The peaks should improve and
   **the damping tail should be wrong**, because F9 integrates to $k=1500$ and
   the repair does nothing above $k\simeq100$. A tail that comes out right
   would falsify this entry's account rather than confirm it.
3. The low-$\ell$ residue, which is the last frame-sensitive thing standing.

---

## T-89 — the $7\times$ rewrite is $(k/3)\tau_1$ under the wrong weight, and **the same term closes the gap**. The two requirements pull it in opposite directions

**2026-10-20, while F9 runs.** T-88 left two things unexplained: the repair
does nothing at $k=300$, and the split rewrites the Newtonian column by
$1.1$ on EdS and $7.1$ on PLANCK. Both are one term, and identifying it
produces a contradiction rather than a fix.

### The diagnosis

T-88 moved the **whole** gravitational half of $C_1$ to $W$. The standard
line-of-sight decomposition says that is wrong: the Sachs--Wolfe combination
$(\delta T+\Phi_A)$ is evaluated **at last scattering** and belongs under $g$;
only the potential derivative accumulated **along the path** belongs under $W$.
From (107), with `newtonian_a_b1_prime`'s own expansion,

$$-C_1'=(\kappa'\hat v_B)'+\frac{(a\mathcal B_1)'}{k},\qquad
\frac{(a\mathcal B_1)'}{k}=\underbrace{(\Phi_A'-\Phi_H')}_{\text{ISW}\ \to\ W}
+\underbrace{\tfrac{k}{3}\tau_1}_{\delta T'\ \to\ g}$$

so the gravitational half is itself **two** things and only the first is a path
integral. Putting $\tfrac{k}{3}\tau_1$ under $W$ puts a rapidly oscillating
source under the wrong weight — and $\tau_1$ oscillates fastest exactly where
the repair fails.

### Measured, and the diagnosis is confirmed on one criterion and refuted on the other

`w_half_is_isw_only` restricts the $W$ half to $(\Phi_A'-\Phi_H')$ and leaves
$\tfrac k3\tau_1$ at $\mathcal V$, where (102) had it:

| background | $k$ | isw-only | gap $\ell=50$ | gap $\ell=200$ | **Newt moved** |
|---|---:|---|---:|---:|---:|
| EdS | 60 | F | $4.233\times10^{-1}$ | $\mathbf{1.475\times10^{-3}}$ | $6.19\times10^{-2}$ |
| EdS | 60 | **T** | $7.837\times10^{-1}$ | $1.527$ | $\mathbf{3.50\times10^{-4}}$ |
| EdS | 300 | F | $9.978\times10^{-1}$ | $1.008$ | $1.108$ |
| EdS | 300 | **T** | $9.987\times10^{-1}$ | $1.007$ | $\mathbf{7.74\times10^{-3}}$ |
| PLANCK | 60 | F | $1.025$ | $\mathbf{1.703\times10^{-2}}$ | $1.68\times10^{-1}$ |
| PLANCK | 60 | **T** | $1.028$ | $1.943$ | $\mathbf{2.91\times10^{-3}}$ |
| PLANCK | 300 | F | $9.995\times10^{-1}$ | $1.000$ | $\mathbf{7.088}$ |
| PLANCK | 300 | **T** | $9.999\times10^{-1}$ | $1.000$ | $\mathbf{1.26\times10^{-1}}$ |

**The diagnosis is right about the column.** The $7.088$ rewrite collapses to
$0.126$ and EdS's $1.108$ to $7.7\times10^{-3}$ — at or near D13's quadrature
floor. **$\tfrac k3\tau_1$ under $W$ *is* what rewrites the Newtonian column.**

**And it is wrong about the gap.** Every cell T-88 closed re-opens: EdS $k=60$,
$\ell=200$ goes $1.5\times10^{-3}\to1.527$; PLANCK's $1.7\times10^{-2}\to1.943$.

### The contradiction, stated rather than resolved

**The term that closes the frame gap and the term that preserves the Newtonian
column are the same term, and the two acceptance conditions pull it in
opposite directions.** $\tfrac k3\tau_1$ must be under $W$ for the gap to
close and under $\mathcal V$ for the column to stand.

**Neither weight is right, so the question is not which.** $\tau_1$ differs
between the columns — the CDM set carries $\tau_1-v$ — so
$\tfrac k3\tau_1$ is frame-dependent and cannot simply be reassigned: **it
carries part of the boost**, and whichever weight it takes, the boundary term
must move with it, because the boundary *is* the $\mathcal V$-collapse of
$-\mathcal VC_1$ and collapsing a term that is no longer at $\mathcal V$ weight
is not available.

**That is the next thing to derive, and it is a derivation and not a sweep.**
T-77 is the standing warning: a lattice walked over controls that are not
independent scores every cell as a partial failure, which is what the table
above is. **The four controls are not independent and this entry is the proof
of it** — M11a, fifth instance, and the first where the method's own
instrument says to stop sweeping.

### What is now established, and what is not

| | |
|---|---|
| the missing $-\kappa'C_2$ in the $g$ slot | **established**, T-88: four orders at $\ell\ge50$, $k\le60$ |
| $\tfrac k3\tau_1$ under $W$ rewrites the Newtonian column | **established**, this entry: $7.088\to0.126$ |
| which weight $\tfrac k3\tau_1$ takes | **open, and the two criteria disagree** |
| the boundary term under a reassigned $\tfrac k3\tau_1$ | **not derived.** Nothing here is valid until it is |
| $k=300$ | **untouched either way.** Not explained by this entry |

**No control is promoted to a default on this evidence**, and
`two_frame.B_SLOT_REPAIR` keeps T-88's combination for F9's diagnostic run
rather than adopting `w_half_is_isw_only`, because the run was launched under
it and changing the code under a running measurement is how a comparison
becomes void.

---

## T-90 — the boundary derivation, and its refutation. **A $\mathcal V$-carried term owes no $-\mathcal VC$; it does not follow that it owes no primary**

**2026-10-20.** T-89 left one thing to derive: what replaces the
$\mathcal V$-collapse when $\tfrac k3\tau_1$ leaves $\mathcal V$ weight. This
is that derivation, implemented and **refuted by measurement**, with the error
identified. Sent to P1-T for independent checking at
`claude/stream-P1B-to-P1T-boundary-derivation-2026-10-20.md`.

### The derivation

(102) descends from $\int W[C_0K+C_1K'+C_2K'']$ with $K=j_\ell(k(\eta_0-\eta))$.
For a term carried under $W$,

$$\int W C K'=\bigl[WCK\bigr]-\int \mathcal V C K-\int W C' K,$$

and $[WCK]$ vanishes at both ends — $W(\eta_0)=1$ with $j_\ell(0)=0$ for
$\ell\ge1$ at the top, $W\to0$ at the bottom. **So the whole boundary this
bundle draws is the collapse of $-\int\mathcal VCK$ under $\int\mathcal V=1$,
and it is forced by the product rule rather than chosen.** For a term carried
under $\mathcal V$ instead,

$$\int \mathcal V C K'=\bigl[\mathcal VCK\bigr]-\int \dot{\mathcal V} C K-\int \mathcal V C' K,\qquad \bigl[\mathcal VCK\bigr]=0$$

since $\mathcal V$ vanishes at both ends. **No $-\mathcal VC$ term, and a
$\dot{\mathcal V}C$ bulk term that (102) has nowhere.** T-88 moved the Thomson
half to $\mathcal V$ and left the boundary carrying $C_1(\eta_*)$ in full, so
on this reading it double-counts at the boundary and omits a bulk term.

### Measured, both corrections together, and it is worse

| background | $k$ | T-90 | $\ell=2$ | $\ell=10$ | $\ell=50$ | **Newt moved** |
|---|---:|---|---:|---:|---:|---:|
| EdS | 10 | off | $1.472\times10^{-1}$ | $8.754\times10^{-2}$ | $4.94\times10^{-4}$ | $5.58\times10^{-3}$ |
| EdS | 10 | **on** | $1.189$ | $5.300\times10^{-1}$ | $6.73\times10^{-3}$ | $\mathbf{1.028}$ |
| EdS | 60 | **on** | $9.598\times10^{-1}$ | $9.403\times10^{-1}$ | $9.033\times10^{-1}$ | $\mathbf{0.920}$ |
| PLANCK | 10 | **on** | $1.090$ | $9.397\times10^{-1}$ | $2.05\times10^{-2}$ | $\mathbf{0.990}$ |

**Every cell T-88 closed re-opens and the Newtonian column moves by order
one.** The two corrections were supplied together rather than apart, which is
**M11a** and is also what the derivation requires: it produces them together.

### The error, and it is specific

**The derivation treats the Thomson half as owing no primary at all. That does
not follow, and the standard solution says so.** The Doppler term is

$$\int g\,v_b\,j_\ell'\,\mathrm d\eta\;\simeq\;v_b(\eta_*)\,j_\ell'(x_*)\int g$$

— it **has** a primary, and the primary sits in the $j_\ell'$ slot rather than
the $j_\ell$ slot. The algebra above is about where the $-\mathcal VC$ term
goes; **it is not a statement that a $\mathcal V$-carried source has no
last-scattering contribution.** Doppler *is* a last-scattering effect, and
removing its primary removes the Doppler peak.

**So the implementation removed the Thomson primary instead of moving it.**
The correction the algebra licenses is that the Thomson primary leaves the
$j_\ell$ boundary and reappears at $j_\ell'(x_*)$, with the
$\dot{\mathcal V}$ bulk term beside it. **That has not been implemented or
measured**, and whether the $\dot{\mathcal V}$ term survives it is open.

### One premise P1-T is asked to check, because it may void the refutation

$[WCK]$ was taken to vanish at the lower limit because $W\to0$ there. **The
bundle integrates from `eta_floor = env.eta[0]`, not from $\eta_*$** — finding
T-58 — so the lower limit is the start of the recombination history, where
$\kappa$ is large but finite. If $W(\eta_{\rm floor})$ is not negligible
against the terms it sits beside, the derivation is incomplete and **T-90
refutes the wrong statement.** That is one print and it has not been made;
stated here rather than after.

### Standing

| | |
|---|---|
| $-\kappa'C_2$ missing from the $g$ slot | **established**, T-88 |
| $\tfrac k3\tau_1$ under $W$ rewrites the Newtonian column | **established**, T-89 |
| the product-rule derivation above | **unchecked by anyone but its author** |
| that derivation as implemented | **refuted**, this entry |
| the $j_\ell'(x_*)$ correction | **asserted, not instrumented** |
| $W(\eta_{\rm floor})$ negligible | **assumed, not measured** |
| $k=300$ | **untouched by any variant tried** |

**No control is a default.** `tests/test_integral_solution.py` passes
unchanged and D14's released row still shows `Newt moved = 0.000e+00`.

---

## T-91 — the premise is settled. $\kappa(\eta_{\rm floor})=123$ and $185.5$, against P1-T's threshold of $15$. **§2 stands and T-90's refutation is of §2 itself**

**2026-10-20. P1-T checked the derivation and supplied the criterion; P1-B had
already made the print.** The two arrived within minutes of each other and
agree, which is the first time this week two streams have converged on a
number without one having seen the other's.

### P1-T's criterion

$W(\eta_{\rm floor})=\int_{-\infty}^{\eta_{\rm floor}}\mathcal V\,\mathrm d\eta$
— the visibility mass below the floor — and the discarded
$\lvert[WCK]_{\rm floor}\rvert$ against the collapsed primary, with
$\sigma=\Delta\eta_{\rm vis}/2.355=0.00413$:

| floor | $W$ | $\kappa$ | $\ell{=}2,k{=}300$ |
|---|---:|---:|---:|
| $-1\sigma$ | $1.6\times10^{-1}$ | 1.8 | $\mathbf{1.4}$ |
| $-3\sigma$ | $1.4\times10^{-3}$ | 6.6 | $5.3\times10^{-3}$ |
| $-5\sigma$ | $2.9\times10^{-7}$ | 15.1 | $4.8\times10^{-7}$ |

*"$\kappa(\eta_{\rm floor})\gtrsim15$ and §2 stands; $\kappa\lesssim5$ and §2
is incomplete."*

### Measured

| background | $\kappa(\eta_{\rm floor})$ | $W(\eta_{\rm floor})$ | $W(\eta_*)$ |
|---|---:|---:|---:|
| EdS | $\mathbf{123}$ | $3.94\times10^{-54}$ | $0.3945$ |
| PLANCK | $\mathbf{185.5}$ | $2.75\times10^{-81}$ | $0.3692$ |

and $\lvert[WCK]_{\rm floor}\rvert$ against the collapsed primary runs
$10^{-52}$ to $10^{-55}$ on EdS and $10^{-79}$ to $10^{-81}$ on PLANCK, at
every $(k,\ell)$ tried.

**$123$ and $185.5$ against a threshold of $15$.** The floor is eight times
further out than §2 needs, and P1-T's $-1\sigma$ row — where the discarded
boundary is $1.4\times$ the primary — is nowhere near where this bundle
integrates from.

**So §2's premise holds, T-90 refutes §2 itself rather than §2-with-a-bad-premise,
and the error identified at T-90's §4 is the error.** P1-T's standing note is
discharged: §2 is now checked by someone other than its author, and the one
number it rested on is printed.

### P1-T's two further rulings, recorded because they close questions

**§4 is right, and CAMB confirms it independently.** CAMB's implemented source
carries $[g(v_b+\sigma)]'/k$, which against $j_\ell$ gives
$\int g(v_b+\sigma)j_\ell'\,\mathrm d\eta$ — boundary vanishing because $g$
does — and collapses to $(v_b+\sigma)(\eta_*)\,j_\ell'(x_*)$ in the sharp
limit. **The coefficient is $(v_b+\sigma)$, not $v_b$ alone**, which is T-82's
pair and T-88's four orders arriving from a third direction.

> **The primary §2 removed and the $j_\ell'$ slot T-86 found missing are the
> same slot**, needed for two independent reasons: the Doppler primary under
> $g$, and the gravitational $+k\int WMj_\ell'$ under $W$. A bulk with no
> $j_\ell'$ slot can hold neither.

**$\dot{\mathcal V}C$ survives §4 and is not optional.** It comes from
differentiating the weight, which §4 does not touch, and it is already in the
four-term identity as $\dot{\mathcal V}C_2$ — *the one piece of
`int_soln_damping` Annals II prints correctly*, which `c3_byparts.py`
confirms. **Implementation note from P1-T, and it is a conditioning
requirement rather than a preference:** $\dot{\mathcal V}=(\kappa''+\kappa'^2)e^{-\kappa}$,
so at $\kappa'\simeq1.4\times10^4$ it carries the $\kappa'^2$ problem and
**must be formed from the weight's own derivative, never assembled from
$\kappa'^2$ and $\kappa''$ separately.**

---

## T-92 — the spectrum under T-88. **The peaks crossed the target rather than reaching it, and the frame gap did not move. The prediction held**

**2026-10-20. The diagnostic F9 run, `--b-slot-repair`**, written to
`diagnostics/d15-f9-b-slot-repair.{csv,pdf,png}`; the released pair is
untouched and still carries 2026-10-19. The banner printed its expectation
before the numbers, which is what makes the result readable:

> *Expect the peaks to improve and the damping tail to be wrong above
> $k\simeq100$.*

### Measured

| | $\ell_A$ | released $\ell_1$ | ratio | **repaired $\ell_1$** | **ratio** |
|---|---:|---:|---:|---:|---:|
| EdS | 192.663 | 280.4 | 1.455 | $\mathbf{106.9}$ | $\mathbf{0.555}$ |
| LCDM | 172.710 | 224.5 | 1.300 | $\mathbf{168.5}$ | $\mathbf{0.976}$ |
| PLANCK | 272.177 | 341.7 | 1.255 | $\mathbf{154.0}$ | $\mathbf{0.566}$ |
| CAMB | — | — | — | 206.1 | — |
| CLASS | — | — | — | 206.2 | — |

An adiabatic first peak sits near $0.73$–$0.78\,\ell_A$. **The peaks moved
from all three too high to two of three too low: they crossed the target
rather than reaching it.** That is a large effect in the right direction and
it overshoots.

**EdS $0.555$ and PLANCK $0.566$ agree to 2%.** LCDM's $0.976$ is the outlier
and it is the model whose $\ell_A$ is **known wrong** — $\Omega_r=0$, a 37%
error, **T-81c** and **T-83**. Against a radiation-corrected $\ell_A$ near
PLANCK's, LCDM gives $0.619$. **So all three backgrounds return a peak ratio
of $0.56$–$0.62$ once a known background defect is accounted for** — flat
across three very different backgrounds, which makes it a property of the
**projection** and not of the parameters. It is low by a factor of $\simeq1.3$.

### The frame gap did not move, and that is the prediction holding

| | released | repaired |
|---|---|---|
| EdS | 100.0% / 100.0% | 99.9% / 100.0% |
| LCDM | 100.0% / 100.0% | 100.0% / 100.0% |
| PLANCK | 100.0% / **340.8%** | 99.9% / **105.7%** |

Against D14's per-mode gaps of $10^{-3}$–$10^{-4}$ at $\ell\ge50$ for
$k\le60$. **F9 integrates to $k=1500$ and the repair does nothing above
$k\simeq100$**, so the sum is dominated by modes it does not touch and the
spectrum-level gap stays at saturation. That is exactly what the banner said
would happen; **a gap that had closed here would have falsified T-88**, and
it did not.

PLANCK's *worst* cell improving $340.8\%\to105.7\%$ is the one place the
repair is visible in the spectrum, and it is the cell where $\ell\simeq k
r_\theta$ puts the first peak — the same cell D14 measured at $79\times$.

### What this does and does not license

**Does:** the repair has a large, consistent, background-independent effect on
peak position. It is not a parameter effect and it is not noise.

**Does not:** it is not an improvement in the spectrum. Two of three ratios
moved from 1.3–1.5 to 0.56, and *passing through* the right answer is not
reaching it. **CAMB and CLASS agree at $206.1$ and $206.2$** and neither
column is near them.

**And it is a control, not a figure.** `diagnostics/`, never `figures/` —
decision **V14**. The released F9 is unchanged.

---

## T-93 — **T-88 is withdrawn. The four orders came from a spurious $\times\kappa'$ of $320$–$680$, and T-92's peak shift with it**

**2026-10-20, within the hour. This is T-66's defect, one level up, and this
time it is in P1-B's repair rather than in the released code.**

### The identity that settles it

$C_1^{\rm thom}=-\kappa'\hat v_B$ and $W\kappa'=\mathcal V$ **by definition**,
so

$$W\,C_1^{\rm thom}\;=\;-W\kappa'\hat v_B\;=\;-\mathcal V\,\hat v_B$$

**identically.** The Thomson term is *already* at $g$ weight in (102) as
printed — the $\kappa'$ inside $C_1$ and the $W$ outside it combine into the
visibility with nothing left over. **There was never a weight to change.**

Measured, on the bundle's own grids:

| background | $\max\lvert W\kappa'-\mathcal V\rvert/\max\lvert\mathcal V\rvert$ | $\lvert WC_1^{\rm thom}-(-\mathcal V\hat v_B)\rvert/\text{scale}$ | $\lvert\mathcal V C_1^{\rm thom}\rvert/\lvert WC_1^{\rm thom}\rvert$ |
|---|---:|---:|---:|
| EdS, $k=10$ | $1.11\times10^{-2}$ | $1.07\times10^{-2}$ | $\mathbf{509}$ |
| EdS, $k=60$ | — | $1.10\times10^{-2}$ | $\mathbf{523}$ |
| EdS, $k=300$ | — | $1.36\times10^{-2}$ | $\mathbf{682}$ |
| PLANCK, $k=10$ | $1.40\times10^{-2}$ | $1.34\times10^{-2}$ | $\mathbf{350}$ |
| PLANCK, $k=300$ | — | $1.24\times10^{-2}$ | $\mathbf{321}$ |

The $1.1$–$1.4\%$ is the recombination grid's own residual — **T-46**, measured
at $1.2\%$ in the primary — not a discrepancy in the identity.

**T-88's `slot_weight_split` applies $\mathcal V\,C_1^{\rm thom}$ where (102)
applies $W\,C_1^{\rm thom}$. That is a spurious factor of $\kappa'$, measured
at $320$ to $682$.**

### What is withdrawn

**T-88's headline — *"four orders of magnitude at $\ell=200$"* — is withdrawn.**
It was produced by a $500\times$ error on one term, and a term inflated by
$500$ that makes two columns agree is the failure mode this register has now
recorded five times. **Frame agreement is necessary, not sufficient**, and
here it was not even that: it was agreement bought with a wrong number.

**T-92 goes with it.** The peak shift from $1.455\,\ell_A$ to $0.555\,\ell_A$,
and the $0.56$–$0.62$ ratio *"flat across three backgrounds, which makes it a
property of the projection"* — that was a sentence away from being reported
as a finding. **It is the signature of a $500\times$ error, not of the
projection.** The diagnostic F9 at `diagnostics/d15-f9-b-slot-repair.*` is
retained as the record of what the defective variant produces and is **not**
evidence about the physics.

**T-90's refutation is void in both directions.** It tested a boundary
correction on top of a $\kappa'$-inflated Thomson term, so neither its failure
nor §2's standing can be read from it. **T-91's conclusion that *"T-90 refutes
§2 itself"* is withdrawn**: §2's algebra is checked and its premise is
measured ($\kappa(\eta_{\rm floor})=123$ and $185.5$), and both of those
stand — but what T-90 refuted was an implementation with a $500\times$ error
in it, which is not §2.

### What survives, and it is not nothing

| | |
|---|---|
| **T-82** — $\hat v_B+C_2$ agrees between the columns to $10^{-15}$ | **stands.** Independent of all of this; no weight enters it |
| **T-85** — the by-parts identity holds in both frames; $A_N\neq A_C$ | **stands.** Measured on the released coefficients |
| **T-86** — the boundary carries $\mathcal D$, the bulk $\mathcal V\mathcal D$, and there is no $j_\ell'$ slot | **stands as a read.** It is what the file contains |
| **T-91 §2** — the product-rule algebra and $\kappa(\eta_{\rm floor})\simeq123$ | **stands.** Checked by P1-T, premise printed |
| **T-91 §5.2** — the Doppler primary belongs at $j_\ell'(x_*)$ with coefficient $(v_b+\sigma)$ | **stands.** P1-T's, from CAMB, independent of P1-B's code |
| T-88's fix | **withdrawn** |
| T-92's peak numbers as physics | **withdrawn** |
| T-90's refutation | **void** |

### And the released code's $\kappa'^2$, which this *does* locate

(102) carries the whole bracket $\{C_0-C_1'+C_2''\}$ under $\mathcal V$, and
$C_1'$ contains $(\kappa'\hat v_B)'=\kappa''\hat v_B+\kappa'\hat v_B'$. Under
$\mathcal V$ that is $\mathcal V\kappa''\hat v_B+\mathcal V\kappa'\hat v_B'$
— and $\mathcal V\kappa'=W\kappa'^2$. **So the released code already carries
$\kappa'^2$ where the $W$-form would carry $\kappa'$ once**, which is
precisely P1-T's *"extra scattering-rate factors"* and the $\kappa'^2$-against-$\kappa''$
mechanism from their item-2 list. **That is a real finding and it is the one
this correction leaves standing** — it is in the released code, not in the
repair, and it was reached by taking the repair apart.

### How it was caught, recorded because the route matters

**Not by a test.** P1-T's §5.2 said the Doppler coefficient is
$(v_b+\sigma)$ *"not $v_b$ alone"*, which sent P1-B back to the Thomson slot's
algebra to see where $\sigma$ would enter — and $W\kappa'=\mathcal V$ is the
first line you write. **One print, and it was available from the moment
`slot_weight_split` was written.**

Under **M11**: the magnitude of the thing varied against the thing it sits
beside was never stated for `slot_weight_split`. Had it been — $\mathcal V$
against $W$ is a factor of $\kappa'$, and $\kappa'\simeq1.4\times10^4$ at
decoupling — **the control would not have been written in that form.** The
column the register has been demanding since T-76 is the column that was
missing here, in P1-B's own work, four days after P1-B wrote the rule.

---

## T-94 — **the released Newtonian integrand is 93–97% one term, and that term is $1.8\times10^5$ times the physical Doppler source**

**2026-10-20. T-93's one surviving result, measured.**
`scripts/diagnostic_d16_kappa_squared.py`,
`diagnostics/d16-kappa-squared-v1.3.0.txt`. **P1-T derived the same statement
symbolically within the hour and from the other direction**; their derivation
and this measurement are recorded together below because neither was made with
sight of the other.

### The six pieces of (102)'s integrand, Newtonian frame

From (107), $-C_1'=\kappa''\hat v_B+\kappa'\hat v_B'+(\Phi_A'-\Phi_H')+\tfrac k3\tau_1$,
so the released bracket under $\mathcal V$ carries:

| term | EdS $k{=}10$ | EdS $k{=}60$ | EdS $k{=}300$ | PLANCK $k{=}10$ | PLANCK $k{=}60$ |
|---|---:|---:|---:|---:|---:|
| $\mathcal V\kappa''\hat v_B$ | $\mathbf{0.935}$ | $\mathbf{0.971}$ | $\mathbf{0.616}$ | $\mathbf{0.933}$ | $\mathbf{0.974}$ |
| $\mathcal V\kappa'\hat v_B'$ | 0.066 | 0.024 | 0.314 | 0.065 | 0.015 |
| $\mathcal V\tfrac k3\tau_1$ | 0.0002 | 0.0064 | 0.082 | 0.0004 | 0.013 |
| $\mathcal V(\Phi_A'-\Phi_H')$ | $0.0000$ | $0.0000$ | $0.0000$ | $\mathbf{0.0018}$ | $0.0028$ |
| $\mathcal VC_0$, $\mathcal VC_2''$ | 0 | 0 | 0 | 0 | 0 |

*(shares of the summed absolute integrand; rank 0 and 2 are identically zero
in the Newtonian frame, which is (110))*

**One term is 93–97% of the integrand at $k\le60$ on both backgrounds.** The
acoustic driving $\tfrac k3\tau_1$ is **0.02%**. The ISW on PLANCK — where
there is one — is **0.18%**.

### What that term is, against the source it is supposed to represent

The physical Doppler source is $g\,\hat v_B=W\kappa'\hat v_B$. The released
dominant term is $\mathcal V\kappa''\hat v_B=W\kappa'\kappa''\hat v_B$. Their
ratio is $\kappa''$, measured:

| | $\kappa''(\eta_*)$ | $\max\lvert\mathcal V\kappa''\hat v_B\rvert/\max\lvert\mathcal V\hat v_B\rvert$ | $\kappa'(\eta_*)^2$ |
|---|---:|---:|---:|
| EdS | $-1.474\times10^{5}$ | $\mathbf{1.811\times10^{5}}$ | $1.459\times10^{5}$ |
| PLANCK | $-6.885\times10^{4}$ | $\mathbf{8.988\times10^{4}}$ | $6.979\times10^{4}$ |

and $\kappa'^2/\lvert\kappa''\rvert=0.989$ (EdS), $1.014$ (PLANCK) — **$\kappa''\simeq-\kappa'^2$.**
So the dominant term carries **three powers of $\kappa'$** where the physical
source carries one.

### It is **not** A-2, and that is the point

Changing $\mathcal V\to W$ divides **every** term in the bracket by $\kappa'$
uniformly and **changes no ratio**. The shares above are weight-independent.
**A-2 cannot reach this**, and neither can any of the weight controls T-88
through T-90 tried.

**The $\kappa''$ term exists only because (102) differentiates $C_1$, which
contains $\kappa'$.** It is an artefact of by-parting **onto the coefficients**
— T-86's structural finding, now with a number on it.

### P1-T's derivation, arrived at independently and within the hour

Multiplying the transport equation by the integrating factor,

$$\tau_\ell'+(\text{streaming})+\kappa'\tau_\ell=a\mathcal B_\ell+\kappa'\mathcal S_\ell
\ \xrightarrow{\times W}\
\frac{\mathrm d}{\mathrm d\eta}\bigl[W\tau_\ell\bigr]+W(\text{streaming})
=W\,a\mathcal B_\ell+\underbrace{(W\kappa')}_{=\,\mathcal V}\mathcal S_\ell$$

> *"The gravitational source arrives under $W$. The in-scattered Thomson
> source arrives under $\mathcal V$, with its $\kappa'$ consumed by the
> integrating factor. **Nothing is left carrying a bare $\kappa'$.** So no
> by-parts can manufacture $\kappa'^2$ — unless it differentiates a
> coefficient that still has one in it, which is exactly what (102) does."*

Verified symbolically on their side: **(102)'s $-\mathcal VC_1'$ reaches
$\kappa'^2$; $\mathcal V\mathcal S_1$ reaches $\kappa'^1$.** And the rule with
its mechanism:

> **By-parts the product, never the coefficient.** CAMB by-parts too — on
> $g\cdot\text{source}$, which generates $\dot{\mathcal V}$ and can never
> generate $\kappa'^2$.

**Three independent routes now say one thing**: T-86's read of the file,
P1-T's integrating-factor derivation, and this magnitude column. None was made
with sight of the others.

### What this does not establish, stated before it is read as more

**A large term is not automatically wrong**, and (102) is the printed equation
this bundle reproduces. What is established is that **one term dominates the
released integrand by two orders over everything the physics is supposed to
produce**, that it carries two powers of $\kappa'$ more than the source it
represents, and that **no weight choice can move it.** Whether removing it
produces a correct spectrum is unmeasured and is not claimed.

**A caveat on $\kappa''$ itself.** `two_frame.py:331` builds it as
`np.gradient(kappa_prime, eta, edge_order=2)` — a spline through a steep
amplitude, which is the shape **T-23** warns against. The
$\kappa''\simeq-\kappa'^2$ agreement at $1\%$ is independent support that it
is near enough for a magnitude column, **and it is not good enough for a
coefficient.** If $\kappa''$ enters any landed expression it owes a published
relation first.

### And a correction P1-T supplies to their own instrument

`tests/frame/c6_thomson.py`'s docstring said $\kappa'v_B$ is *"carried
separately under $\mathcal V$"*, which reads as a weight change. P1-T's
2026-10-18 §5.3 said the right thing — *leave $C_1^{\rm Th}$ under
$e^{-\kappa}$ where its own $\kappa'$ makes $\mathcal V$ directly; by-parts
only $C_1^{\rm grav}$* — and the instrument restated it as a weight.
**T-88 implemented the phrasing, not the derivation.** What survives of c6 is
the obstruction: $\Delta C_1\supset\kappa's$ puts $\kappa'$ into the boost
response and no $(\alpha,\beta,\gamma)$ removes it. **The remedy is not to
move the term. It is not to differentiate it.**

---

## T-95 — **six commits carry subject lines that do not distinguish them, because P1-B reused one message file.** The content is intact; the history is not navigable

**2026-10-20. Raised by the PI on reading the pushed history.** Read off
`github.com/timgebbie/frame-covariant-cmb-reproducibility/commits/main`
through the browser, since the API is not reachable from this session.

### What is sound

**Every commit is real, distinct and pushed.** Fifteen distinct SHAs over
three days, `git status -sb` reports `## main...origin/main` with no `ahead`
or `behind`, and the only uncommitted change is one CHANGELOG correction.
`scripts/make_manifests.py --check` passes on the local tree, and the local
tree equals `HEAD`. **Nothing is missing and nothing is corrupted.**

### What is not

Six commits carry subjects that a reader cannot tell apart:

| SHA | subject | |
|---|---|---|
| `c0d1ff2` | T-94: one term is 93-97% of (102)'s integrand… | **duplicate subject** |
| `60faeae` | T-94: one term is 93-97% of (102)'s integrand… | **duplicate subject** |
| `6622abf` | T-91..T-93: the premise holds… | |
| `fc8d545` | T-90: the boundary derivation, and its refutation | |
| `9806a51` | T-89: the 7x rewrite is (k/3)tau_1… | |
| `3bb6cdb` | T-79..T-88: the repair — C_2 must travel with v_B under g | **duplicate subject** |
| `2b1306c` | T-79..T-88: the repair — C_2 must travel with v_B under g | **duplicate subject** |
| `ee5ebac` | T-79..T-87: the frame gap is the slot-and-weight split… | |
| `1d007e2` | T-79..T-85: the frame gap is in the split… | |
| `b0a4168` | T-79..T-83: the l=0 row, the external review… | |

**And `tests/frame/c7_kappa_ledger.py` appears under no commit of its own.**
It was handed over after the T-94 message file was written, so it is almost
certainly inside `c0d1ff2` — a commit whose subject says T-94 and whose
content includes P1-T's seventh instrument. *A commit that does not announce
what it carries.*

### The cause, which is P1-B's and is a process defect not a judgement one

**P1-B wrote every commit message to one path, `commit-msg-t79-t82.txt`, and
rewrote it in place as the work grew.** Each time the PI ran
`git commit -F`, the file had moved on. The `T-79..T-83 / T-79..T-85 /
T-79..T-87 / T-79..T-88` series is that file being extended four times, and
the two identical pairs are it being committed twice without changing.

**This matters here more than it would elsewhere.** This bundle's record *is*
its deliverable — `provenance/` is the product, and **L5** counts independent
checks by their sources. A history in which `git log --oneline` cannot say
which commit carries which finding is a record that has to be reconstructed
rather than read, and reconstruction is where **M5** says errors enter.

### What is not being done about it

**The history is not rewritten.** It is pushed, the PI owns git, and **S39**'s
principle — *a released tag is never moved* — applies with more force to
public history than to a tag. **Rewriting ten commits to tidy their subjects
would destroy the only authentic record of the order in which this week's
findings were made and withdrawn**, which is the thing the bundle exists to
carry. The defect is recorded; the history stands.

### The process fix, in force from now

**One commit message, one uniquely named file, never reused.**
`commit-msg-<finding>-<date>.txt`, written once, and a new path for every
commit even when the previous one was not used. P1-B does not rewrite a
message file that the PI may already have committed from.

### What the PI can verify in one command

```
git log --oneline --name-status -12
```

The mapping above is **reconstructed from this session's record of which
message file held what, not read off `git log`** — the browser shows subjects
and SHAs, not file lists. If `c0d1ff2` does not contain
`tests/frame/c7_kappa_ledger.py`, this entry is wrong about that one claim and
nothing else.

---

## T-96 — the $W$-form instrumented. **The first run was void on a normalisation; the second is not conclusive and is not reported as if it were**

**2026-10-20. P1-T's item 2**, `scripts/diagnostic_d17_w_form.py`,
`diagnostics/d17-w-form-v1.3.0.txt`.

### Run 1, void — and the signature proves it rather than argues it

P1-T's box carries $\mathfrak B_n=a\mathcal B_n$ **reduced to its potential**;
the bundle stores the *un*-reduced $a\mathcal B_n$, which carries $k^n$. The
first run used the stored form. Measured against P1-T's §4 frame table, the
residual on $\Delta\mathfrak B_1$ against $\dot s$ came out at

$$0.900\ (k{=}10),\qquad 0.98333\ (k{=}60),\qquad 0.99667\ (k{=}300)$$

which is **exactly $1-1/k$** — the signature of comparing $k\dot s$ against
$\dot s$. **A normalisation, not a defect**, and it is T-66's shape for the
third time in this register.

The same run read $\Delta\mathcal S_0=1.000$ against P1-T's required $0$.
**That was also the instrument.** $\mathcal S_0=\tau_0=\delta T$ and the
acoustic solver produces **one** $\delta T$ that both columns read, so
$\Delta\mathcal S_0=0$ *by construction*; reconstructing it per frame as
$a\mathcal B_1/k-\Phi_A$ is what moved it, because $a\mathcal B_1=k(\delta
T+\Phi_A)$ holds in the Newtonian specialisation and was applied to both.

**With normalisations matched, three of P1-T's four frame conditions are
satisfied by the bundle's own inputs**, and $\Delta\mathcal S_1=-s$ holds at
$1.7\times10^{-16}$.

### Run 2, corrected, and **not conclusive**

| background | $k$ | $\ell=2$ | $\ell=10$ | $\ell=50$ | $\ell=200$ |
|---|---:|---:|---:|---:|---:|
| EdS | 10 | 1.492 | 1.157 | $\mathbf{2.68\times10^{-2}}$ | 1.595 |
| EdS | 60 | 1.082 | 1.020 | 1.675 | $\mathbf{1.43\times10^{-2}}$ |
| EdS | 300 | 0.998 | 0.987 | 0.991 | 0.874 |

The $W$-form's frame gap is $O(1)$ at most cells and **two orders below that
at two of them**. It is not machine zero and it is not uniformly $O(1)$.

### Why this is **not** reported as P1-T's §6.3 second branch

The tempting reading is *"the reference is not invariant either, so the frame
gap is not in the assembly and the triage needs a new site."* **Two defects in
this instrument are unexcluded and either would produce exactly this.**

1. **$\sigma_0$ on the rank-0 row is taken as $-1$**, from T-77's restored
   $C_0=-\tfrac13\mathfrak B_2-\mathfrak B_0$. P1-T do not state $\sigma_0$
   numerically and `_solved_match()` gives $p_0=-2.5$ for a row that carries
   $\mathcal B_2$, not $\mathcal B_0$. **The rank-0 normalisation is a
   choice this instrument made and did not measure.**
2. **$\mathcal S_2=\tau_2$ is set to zero** because the bundle has no photon
   quadrupole source (**A-5**) — while $\mathfrak B_2\neq0$ in the CDM column.
   **T-72** records that $\delta T_E\equiv0$ there, so rank 1 vanishes
   identically and *everything the CDM column has arrives through rank 2*.
   **Zeroing one half of the rank-2 pair in the column that is entirely
   rank-2 is the leading candidate for this result**, and it is a property of
   the instrument, not of (102).

**So the second branch is not taken.** Claiming it would be the sixth premise
failure of the week, and the first five are in this register above.

### What run 2 does establish

**The two assemblies differ by $O(1)$ within a single frame** — columns 3 and
4 of the diagnostic run $0.99$–$1.08$ at nearly every cell. The $W$-form and
(102) are not small perturbations of one another, which is consistent with
T-94: the by-parts moves a term that is $93$–$97\%$ of the integrand.

### What is needed before the branch can be taken

| | |
|---|---|
| $\sigma_0$ for the rank-0 row | from P1-T, or derived; **not** chosen here |
| $\mathcal S_2$ in the CDM column | the bundle has none (A-5). Either P1-T's form needs it and the comparison is incomplete without it, or it is $O(t_c)$ and may be dropped — **and which is a derivation** |
| the $k=300$ column | unmoved by every variant, here as elsewhere |

---

## T-97 — the GitHub repository is the project's public face, and letting it lag is a failure mode. **M12, and decision S46**

**2026-10-20, the PI, after T-95.** Two instructions, taken as standing and
recorded here rather than remembered:

> *"Please in the future be aware of the GitHub repo state. This is important
> as this is the public face of the project and it needs to be the cleanest
> and most reliable representation."*
>
> *"Please consider it a failure mode when the GitHub repo deviates more than
> six hours away from the current state of play of the project."*
>
> *"Colleagues look at the README and supplementary materials in order to get
> an idea of the current state of play."*

### M12 — the public artefact is six hours behind, or it is a defect

> **M12 — a public artefact that lags the work is wrong, not merely old.**
> The GitHub repository, `README.md` and the supplement are read by people
> who are not in the session and who have no other source. **A reader who
> acts on a six-hour-old state of play is acting on a finding that may have
> been withdrawn since**, and five of this week's were.

**It joins the method series as a failure mode rather than a preference,
because it has the same shape as the rest of it:** M5a says a claim about an
artefact is read off the artefact; M12 says the artefact a *reader* has must
be the one the claim was read off. T-93 withdrew a four-order result within
six hours of recording it. **In that window the README said it was a
result.**

### S46 — what that requires operationally

**Taken, P1-B's call under the PI's delegation, 2026-10-20.**

1. **Every working session ends with a commit and a push**, not with files on
   disk waiting for one. A finding that is in `provenance/` locally and not on
   GitHub is a finding only this session can see.
2. **`README.md` carries the current state of play, not the last release's.**
   The register counts, the figure's status block and the open-defect summary
   are part of the deliverable and go stale faster than anything else in the
   tree. They were four findings and six diagnostics behind when T-87 found
   them, and two findings behind again six hours later.
3. **The supplement carries the live result**, not only the settled ones.
   §\emph{The frame discrepancy} now carries the five failed repairs and the
   $\kappa'^2$ measurement, because a reader who has only this document should
   be able to see what is open and what has been withdrawn.
4. **A withdrawal propagates to the public artefacts in the same commit as
   the withdrawal.** This is `failure-mode-cohesion-and-propagation`'s rule
   — *a correction lands where it was found and is never carried to the
   places that restate it* — applied to the one audience that cannot ask.

### The outstanding audit items from T-87, now closed

| | |
|---|---|
| v1.0.0's release state | **closed** — tagged and released; CHANGELOG heading qualified, T-95 |
| `S43`, `S44`, `S-b` dangling | **closed** — S43 taken, S44 deferred with a trigger, S-b renumbered S45 |
| `RELEASE-STATUS-v1.md` had no v1.3.0 section | **closed** — `make_release_status.py` enumerated four releases and not this one, so the generator *could not* emit it; v1.3.0 now has a rung |
| its pre-T-57 numbers presented as current | **closed** — corrected in the generator, with what they read now beside what they read then |
| `energy frame` alias after **S8a** retired it | **closed** — in the generated table's header, its local variable, and `provenance/README.md`. S8a says *"no aliases were kept"*; one was, for six days, in a generated file |
| `FIGURE-PLAN`'s *"the key figure is F3"* | **closed** — superseded block added; the plan is kept as a v1.0.0 artefact rather than rewritten to a release it did not plan |
| F7's $1.25\times$ against README's $1.24\times$ | **still open, and now labelled as open in both** — the authoritative value is `figure_f7_frames.py`'s own `.2f` print and neither copy was read off it |

---

## T-98 — P1-B broke **V13** while fixing T-87's captions, and the PI caught it. **The audit's own output needed auditing**

**2026-10-20, the PI:** *"Do not break or deviate from the agreed visual
grammar in terms of conformity — that was also a previous failure mode, as was
staleness in the project state files. That is the purpose of the audit."*

### The deviation

**V13:** *"Where a figure depends on a corrected expression, its caption
carries **one** footnote naming the printed equation and pointing to
`provenance/`."* And `captions/FIGURE-PLAN-v1.0.0.md` rule 9, which is V13's
own statement of itself: *"Corrections are silent, and marked by one
footnote… **the caption carries no narrative.**"*

**T-87 annotated three captions — F2, F5 and F9 — with four- to six-sentence
blocks.** Each named the superseding findings, restated the current numbers,
explained why the figure had not been regenerated and asserted which file was
authoritative. **That is narrative, and V13 forbids it in a caption.**

> **The fix for a staleness defect introduced a conformity defect.** T-87 was
> opened to close exactly these two classes, and its own output carried one of
> them for six hours. **M12** applies to the audit's product as much as to the
> work it audits.

### Corrected

Each of the three now carries the conforming one-line form and nothing more:

```
$^{\dagger}$ Superseded by findings T-57, T-59; see
             provenance/BUNDLE-DEFECTS-v1.md.
```

The narrative is where it belongs — in this register, which is the file V13
points the reader at. **V15 is also satisfied again**: *the caption is the
specification, not a description*, and a paragraph about which findings
superseded which numbers is a description.

### What this says about the audit, and it is the PI's point

**An audit that is not itself audited produces its own class of defect.**
T-87's sweep was mechanical and found real things; its *repairs* were written
by hand and were not checked against the decision register they were repairing
*to*. The repair is the part that needed a gate and did not have one.

**There is no automated check for V13 and this entry does not propose one** —
"carries no narrative" is not expressible as an assertion. What is available
is cheaper: **a repair that touches a caption, a figure or the supplement is
read against §V of `provenance/DECISIONS-v1.0.0.md` before it is committed.**
Fifteen rows, and the PI read them faster than any gate would have run.
