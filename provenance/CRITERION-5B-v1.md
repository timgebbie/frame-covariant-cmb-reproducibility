# Criterion 5b — this bundle against CAMB and CLASS

**Generated context for `scripts/compare_criterion_5b.py`, run 2026-10-15.**
Every number below is measured; none is typed from memory.

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

## What this means for the criterion as worded

**S4b set the tolerance as the two codes' mutual difference. This bundle will
not meet 0.370% in the acoustic band and was never going to.** (102) is a
slow-decoupling solution with no polarisation hierarchy, no neutrino
anisotropic stress and a visibility-weighted line of sight; CAMB and CLASS are
full Boltzmann codes. A criterion that can only be failed is not a criterion.

**Two honest readings, and the choice is the PI's:**

- **5b becomes a measurement, not a gate.** It reports the three band
  differences and the itemisation above, and the release states them. That is
  what the comparison is actually good for: it says *how far* the 1+3
  slow-decoupling solution is from a Boltzmann code, in bands, with the
  dominant term named.
- **5b keeps a tolerance, set against something it can meet.** The natural
  candidate is **the bundle's own pipeline** rather than the external codes ---
  (102) against (177)--(179), which agree to $10^{-5}$ mode by mode --- with
  CAMB and CLASS reported alongside as context rather than as the gate.

**Nothing is decided here.** The measurement exists, is reproducible, and is
stamped; the criterion's wording is a release decision.
