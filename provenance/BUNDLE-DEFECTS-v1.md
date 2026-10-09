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
