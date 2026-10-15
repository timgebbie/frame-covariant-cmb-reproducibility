# Criterion 5b — the gate, and the external context

**Generated context for `scripts/compare_criterion_5b.py` and
`scripts/diagnostic_d8_criterion_5b_gate.py`, run 2026-10-15.**
Every number below is measured; none is typed from memory.

**Read the last section first if you are looking for the criterion.** Under
decision **S4c** the tolerance is set against this bundle's own pipeline and the
comparison with CAMB and CLASS, which is most of this document, is context.

---

## The comparison is like for like, and that took work

| | |
|---|---|
| cosmology | `PLANCK_MODEL` — the stamped Planck 2018 VI column with a photon-only radiation era, $\Omega_\gamma h^2$ **derived** from $T_{CMB}$, reaching $z_{eq}=5756.0$ against CAMB's and CLASS's 5756.0 by an independent route |
| external codes | CAMB 2.0.5, CLASS v3.4.1, specialised **down** to what this bundle contains: $N_{eff}=0$, no reionisation, no lensing, no tensors, helium explicit at $Y_{He}=0.245$ |
| frame | the **CDM frame** both sides — CLASS's synchronous gauge verified from `perturbations.c` to be realised by the CDM congruence, CAMB corroborated from its interface |
| damping | $f_2=3/4$, (dif-damp-correct) — ***Annals II*'s own corrected equation**, not a departure from it (T-43) |
| quantity | shape, $D_\ell$ renormalised at $\ell=30$. Neither side fixes $A_s$ the same way |

## What it measures

| band | $\ell$ | vs CAMB | vs CLASS | code–code floor |
|---|---|---|---|---|
| plateau and late ISW | $2\le\ell<30$ | **97.8%** | **97.8%** | 0.125% |
| acoustic peaks | $30\le\ell<1000$ | **137.0%** | **137.3%** | **0.370%** |

**First acoustic peak: this bundle at $\ell\simeq170$, CAMB and CLASS at
$\ell\simeq198$** on the comparison grid — about 15% low.

## The itemisation, which is the point

**A single number would say only *it differs*.** What is useful is which
approximation each part belongs to.

1. **The Sachs--Wolfe plateau, and it dominates.** (102) carries $\mathcal V$ by
   derivation --- the visibility substitution *enters* at (102) as a
   slow-decoupling correction --- and approximations **A-1** and **A-2** record
   that this cannot carry a late integrated Sachs--Wolfe term and gives
   $D_\ell\propto\ell^2$ in standard CDM. Measured: the rise from $\ell=2$ to 30
   is **80.5×** on (102)'s branch against the pipeline's 1.70× and CAMB's 1.14×.
   **This is a property of the antecedent's equation, not a defect of this
   reconstruction** --- findings T-41 and T-42.
2. **The damping coefficient, measured and attributable: 17.2%** in the acoustic
   band between $f_2=3/4$ and $f_2=1$. Both are *Annals II*'s.
3. **The acoustic scale**, $\ell_{\rm peak}$ 170 against 198, consistent with
   $z_*=1114.5$ here against CAMB's 1088.5 --- Peebles against HyRec --- and the
   sound-horizon treatment.
4. **The slow-decoupling order**, which F6 measures separately and which is the
   largest single approximation in the chain.

## The gate, which is the criterion — decision S4c

*Annals II* writes its integral solution **twice**: (102), carried with a
generic $u^a$ and specialised afterwards, and the source assembly (177)--(179),
written in the Newtonian frame from the start. The paper states the relation
between them and carries it out --- *"Later we will explicitly recover these
equations in the Newtonian frame"*, and afterwards *"This completes the recovery
of the standard integral solution results using the 1+3 CGI approach at linear
order"*. **The recovery is symbolic, and symbolic is the right way to do it.**

What has never been done is to evaluate both forms and compare them. That is
what this gates on: not whether the antecedent's argument is sound, but whether
this reconstruction's two implementations of it agree when run --- which is
v1.2.0's audit half (**S26**), and the only part of the claim that arithmetic
can settle.

`scripts/diagnostic_d8_criterion_5b_gate.py`, in `run_all.py`:

| | |
|---|---|
| backgrounds | CDM (Einstein--de Sitter), $\Lambda$CDM, `PLANCK_MODEL` |
| modes | nine, $0.3\le k\le600$, each on an $\eta$ grid **derived from $k$** at 48 samples per oscillation |
| multipoles | $\ell=2,5,10,50,200,600$ --- both bands the criterion states |
| measure | $\lvert\Delta^{(102)}_\ell-\Delta^{(177)}_\ell\rvert$ over $\max_\ell\lvert\Delta_\ell(k)\rvert$ |
| **worst** | $\mathbf{9.5\times10^{-6}}$, at Einstein--de Sitter, $k=30$, $\ell=2$ |
| **median** | $2.7\times10^{-8}$ |
| **gate** | $10^{-3}$ --- a hundredfold margin |

**At the transfer level at fixed $k$, with the same weight on both sides.** Not
at $C_\ell$: there the two branches differ by a factor of eighty in the plateau,
and that difference is approximations **A-1** and **A-2**, the weight the
line-of-sight integral carries. It is a property of what (102) prints, measured
separately by F6, and gating it away would be gating away the antecedent's own
equation.

**The gate can fail.** `test_a_gate_that_cannot_fail_is_not_a_gate` feeds it a
route wrong by 1% and requires it to say 1%, and feeds it an empty comparison
and requires it to raise. An algebra defect --- a wrong sign, a dropped term, a
mis-specialised coefficient --- moves this by $10^{-1}$ or more; T-41's plateau
was a factor of eighty. The gate catches a regression rather than certifying the
number it returns, which is **T-15**'s rule.

### What the gate does not establish, stated rather than left to be noticed

Both routes are handed the same background, the same recombination history, the
same acoustic solution, the same potentials, the same Bessel table and the same
damping. **A comparison that holds an input fixed cannot check that input** ---
finding **T-3**, where a coarsened grid returned a plausible spectrum 575% wrong
while two routes agreed to $10^{-16}$.

This is not a formality here. Setting this gate turned up **T-46**: the
recombination grid, which both routes share, moves the primary source at
$\eta_*$ by **1.2%** between `n_eta` 4 000 and 64 000, and the gate would read
$9.5\times10^{-6}$ throughout. It is raised as **Q7** for the PI. The shared
inputs are enumerated in `functions/spectra/two_route.py`, and each is checked
elsewhere against something it did not come from.

### What it cost to make the measurement real

The claim that the two routes *"agree to $10^{-5}$ mode by mode"* had stood in a
test docstring since T-41 and was about to be written into a release criterion.
Three findings stood between it and a measurement: **T-44**, a gate that printed
PASS on a `nan`; **T-45**, a fixed 4 000-point grid and a frozen acoustic tail,
on which both routes were un-converged *in the same direction* and so agreed two
hundred times better than they do; and **T-46**, the interpolant at $\eta_*$.
**The remembered figure turned out to be right.** It was also quoted four times
before anyone measured it, and that is the part worth keeping.

## Why the external codes are context and not the threshold

**S4b set the tolerance as the two codes' mutual difference. This bundle will
not meet 0.370% in the acoustic band and was never going to.** (102) is a
slow-decoupling solution with no polarisation hierarchy, no neutrino
anisotropic stress and a visibility-weighted line of sight; CAMB and CLASS are
full Boltzmann codes. **A criterion that can only be failed is not a
criterion** --- and S4b's merit, that a tolerance should be *measured* rather
than chosen, survives intact in S4c, which measures a different and meetable
thing.

The PI's ruling, 2026-10-15: *"5b keeps a tolerance set against the bundle's
own pipeline --- (102) against (177)--(179) --- with CAMB and CLASS reported
alongside as context, because this is self contained and retains the spirit of
the entire build."*

**Nothing above is withdrawn.** The two codes are still run, still stamped,
still specialised down to what this bundle contains, and their mutual difference
is still measured per band --- it remains the scale against which the
differences in this document should be read, since no agreement with either code
could be claimed tighter than they agree with each other. What changed is that
it is no longer the threshold.

**One consequence worth naming.** `scripts/compare_criterion_5b.py` takes about
fifteen minutes and needs `camb` and `classy` installed, so it cannot be in
`run_all.py` --- which means criterion 5b's artefact could never have reached
rung **R** under **S27**'s own definition. The gate runs in half a minute on
code this bundle owns, and is in the harness.
