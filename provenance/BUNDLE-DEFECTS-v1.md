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
