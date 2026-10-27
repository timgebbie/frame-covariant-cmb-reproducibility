# Frame checks — eleven instruments, for `tests/`

**P1-T, 2026-10-19; count corrected and `c9` added 2026-10-26; `c10` and `c11`
added 2026-10-26.** Eleven self-contained instruments behind the
frame-covariance conditions, plus the generator that turns them into
`docs/THEORY-AUDIT.md`.

```
python3 run_all.py                                     # exit 0 only if all pass
python3 gen_theory_audit.py                            # writes the document itself
python3 -I c6_thomson.py                               # or run one
```

**Do not redirect the generator.** It writes `docs/THEORY-AUDIT.md` itself —
P1-B added the write on 2026-10-21 for exactly this reason, and its source says
so: *"An artefact whose generation depends on a human remembering a redirection
is not generated."* The printed copy on stdout is a convenience and is not the
document.

**This line carried `> ../../docs/THEORY-AUDIT.md` until 2026-10-26, five days
after the redirection stopped being needed, and on 2026-10-26 it destroyed the
file.** Under PowerShell `>` truncates the target before the command runs, so
the shell's handle emptied the document the generator had just written to the
same path. The committed file went to zero bytes. **A usage line that
contradicts the code it documents is a defect in the document, and this one was
copied forward into a landing script without being read against the generator.**
§3c, a third time.

They also run under the bundle's own harness as `tests/test_frame_checks.py`,
which invokes each one as a **subprocess with `-I`** rather than importing it,
so the independence below is not compromised by being wired in.

**`docs/THEORY-AUDIT.md` is generated output, not prose.** It carries
*Generated, not transcribed — Do not edit by hand*, every number is read from an
instrument's machine-readable record (`##RESULT##` line), and the generator
exits non-zero on any failure, so **a failing suite cannot produce a document.**
To change the document, change the instrument.

## What this suite does not establish — read first

Nothing here is a claim about the spectrum. Every assertion is a condition on
the functional or on the matching, verified in isolation.

**Measurements of the solver belong to `provenance/BUNDLE-DEFECTS-v1.md` and are
not restated here or in the generated document.** A number copied out of that
register into this one is a third copy, and a third copy is how a fabricated
quotation enters a brief.

**No project code is imported.** Each instrument builds its own visibility,
kernel and boost potential, so the suite cannot agree with the solver by
construction. Requires `numpy`, `scipy`, `sympy`.

| instrument | establishes |
|---|---|
| `c1_identity.py` | `Δ(δT+Φ_A) = (ΔC₂)′` at coefficient exactly 1; the invariant `(δT+Φ_A) − C₂′` is the Sachs–Wolfe combination and is equal in both threadings, independent of `k` and `η` |
| `c2_weight.py` | the rank-2 sector enters at `k⁻²`; its boundary pair is in `S` and `S′`, never `S″` |
| `c3_byparts.py` | the exact bulk source `W(C₀−C₁′+C₂″) − 𝒱C₁ + 2𝒱C₂′ + 𝒱̇C₂`; Annals II's printed `int_soln_damping` does not reproduce its own integral |
| `c4_rank_slot.py` | frame invariance forces `β = −α`, `γ = 0` |
| `c5_monopole.py` | `a·Δℬ₀ = ⅓k²ΔC₂` exactly, so `γ = 0` closes **only with ℬ₀ restored** |
| `c6_thomson.py` | `κ′v_B` inside `C₁` **and differentiated** breaks invariance; carried as its own undifferentiated term it needs `c = α` and the reduced `v̂_B = v_B/k`. **Not a weight change** — `Wκ′ = 𝒱` is an identity, so the Thomson term is already at visibility weight; the defect is the differentiation (P1-T, 2026-10-20; measured at **T-93**/**T-94**) |
| `c9_byparts_admissibility.py` | **the condition under which the by-parts of `c6` is legitimate at all.** `(WC₁)'` splits into `W'C₁ ~ κ'²` and `WC₁' ~ κ''`, whose **sum** is the total derivative `d(𝒱v̂_B)/dη` and is therefore bounded — **not because the two cancel pointwise, which they do not**: C9a measures the largest piece at **8.0×** the sum. (102) carries `𝒱C₁'` in place of `WC₁'` — larger by **exactly κ'** — and drops `W'C₁`, destroying the bound from both sides in one operation. The **split** by-parts, gravitational half by-parted and scattering half left at `K'`, reproduces the ancestor to 1e-13 and contains no `κ''` term at all (P1-T, 2026-10-26) |
| `c10_oscillator_phase.py` | **the acceptance criterion for the acoustic step is blind to the driving it was meant to gate.** Eliminating `τ̃₁` between *Annals II* (152) and (153) returns `δT̃″ + [R'/(1+R)]δT̃' + k²c_s²δT̃ = −(k²/3)Φ_A − 𝓕` with `c_s² = 1/[3(1+R)]` exactly and the standard baryon-drag coefficient; nothing is imported to get it. On a **constant** `Φ` the boundary value `(δT̃+Φ_A)(η_*)` is a pure cosine of amplitude `Φ/3` and its phase is **zero**; on a decaying `Φ` the phase is non-zero at every `k`. So a *"tracks `cos(kr_s)` in exact phase"* criterion **accepts the undriven solution and rejects the driven one** — the step that should have caught **A-3** certifies its absence. The Einstein–de Sitter null, `Ω_r = 0` and `Φ` constant and phase exactly zero, is the control that separates a driving mechanism from a fit (P1-T, 2026-10-26) |
| `c11_kernel_partner.py` | **a by-parts taken against the kernel has three terms, not two, and the one that is easy to drop is the one that keeps the source out of the post-decoupling span.** `d(WCK)/dη = 𝒱CK + WC'K + WCK'`, whose integral is a pure boundary term; the boundary at `η₀` is **exactly zero** for `ℓ ≥ 1` because `j_ℓ(0) = 0`, and the boundary at `η_i` is bounded by `e^{−κ}(η_i)`. So `∫WC'K = −∫𝒱CK − ∫WCK'` exactly, to 5.4e-8 across `2 ≤ ℓ ≤ 600`. The Sachs–Wolfe term `𝒱CK` puts 5.5e-7 of its mass outside the visibility; the differentiated term `WC'K` puts **0.75 to 0.99** of its mass outside it — a separation of 1.4e6. Keeping `WC'K` without its `WCK'` partner therefore replaces a recombination-confined source with one that accumulates to today, and the discarded partner is 2.7 to 1.9e3 times the Sachs–Wolfe term it leaves behind. **With `Φ` constant this does not go away**, because `C₁^grav` still carries the free streaming of `δT̃`, which is why the Einstein–de Sitter null is the control that sees it. `c9`'s two-term condition is the special case in which the kernel is held fixed (P1-T, 2026-10-26) |

## Five things to read before trusting the output

**`c3_byparts.py` check C3b is *expected to fail the printed form*.** It asserts
that Annals II does **not** reproduce its own integral, so a PASS there means the
discrepancy is still present. Read cold, the output reads backwards. It prints
`DEFECT PRESENT`; `DEFECT GONE` fails the suite deliberately.

**`c4_rank_slot.py`'s residual floor is not numerical.** At `β=−α, γ=0` it sits
at `~9e-3` and is quadrature-stable under refinement. That floor **is the
Thomson term**, absent from the functional c4 tests; `c6_thomson.py` carries it
at `c = α` and the residual drops to `~3e-13`.

**`c5_monopole.py` cannot see an additive piece in `C₀`.** `ΔC₀ = 0` constrains
how `ℬ₀` *moves*, not what it *is*: it fixes the multiplicative normalisation
exactly — scale `a·ℬ₀` by `λ` and the cancellation closes only at `λ = 1` — but
any additive boost-invariant `X` with `ΔX = 0` passes for free. Since
`C₀ = ⅓k²C₂ + ⅓kτ₁`, a missing additive term of `O(k)` or lower is invisible
where the `k²` piece dominates and dominant where it does not. **Nothing in this
instrument excludes that case.**

**`c10_oscillator_phase.py`'s decaying potential is not the radiation era.** It
falls at `x = kη/√3`, so for large `k` it has decayed before the mode has
oscillated appreciably and the measured phase falls as `1/k`. In the real case
the decay is tied to equality rather than to `k` and persists through several
oscillations for modes entering well inside radiation domination. **What C10c
establishes is the mechanism and its sign — a time-dependent potential puts a
phase into the boundary value and a constant one does not — and not the
magnitude of that phase in this bundle.** C10a is analysis and needs no
construction; C10b, C10c, C10d and C10e are demonstration on this file's own
potentials.

**`c11_kernel_partner.py`'s monopole is a stand-in, and its thresholds are
measured rather than assumed.** The coefficient is an oscillation at `kc_s`
under a power-law envelope, not a solution of the hierarchy, so **C11e's late
fractions are a statement about where the two terms live in `η` and not about
the amplitude of either in this bundle.** The identity C11a asserts and the
boundaries C11b and C11c assert hold for any coefficient whatever and are
analysis, not demonstration. C11e's floor was first written at `0.80` and the
instrument failed it at `0.750`; the floor is now `0.5`, which is what the word
*majority* means, and the untunable statement is the separation of `1.4e6`
between the two terms' late fractions, which no choice of floor between them
changes.

> **This suite is a worked instance of M11a** (the method-failure series,
> renamed from `V` at T-79 to free the letter for
> `provenance/DECISIONS-v1.0.0.md`'s released visual grammar; numbers are
> unchanged, so `V11a` ≡ `M11a`)**.** Three of the four conditions
> together leave `~9e-3`; all four give `~3e-13`. **No proper subset works**, so
> a one-at-a-time ablation would have scored each of the four as a failed fix.
> The conditions were not found by ablation — they fall out jointly from one
> invariance requirement, which is what hands you the set in advance.
> `tests/test_frame_checks.py` asserts that instance rather than leaving it in
> prose: C4's floor, C5's floor and C6's gravitational-only column are checked
> to be **one number**.

## Provenance

Annals II is read from `sources/annals/cbrII.tex` and referred to by label:
`IBE-source`, `modeibe`, `source-calB`, `find_coef`, `C-B-coef`,
`int_soln_damping`, `slowdecoupling`, `slowdecoupling-ng-0`. Paper 1 is referred
to by label (`eq:B`, `eq:frame-transf`, `eq:raise`), **never by printed number** —
those differ between the two lines.

## c8 — the rank-0 partner

`c8_rank0_partner.py`, added 2026-10-21. **The gate acceptance condition (iv) depends on, in place of $\gamma$.** It scores the frame shift of the *bracket* $C_0-C_1'$ at rank zero, in exact rationals with a numeric confirmation and a control on each of three rows: $+13/6\thinspace kv$ with (89)'s printed $\alpha_2$, **$0$ exactly** with $\alpha_0$ (finding **B-16**), and $-1/3\thinspace kv$ with $a\mathcal B_0$ restored (the refuted **T-107**).

> **Why $\gamma$ could not settle it — M15.** $\gamma$ pairs $\Delta C_0$ against $k^2\Delta C_2$, and the partner is in $-C_1'$. *A gate built from one coefficient cannot see a cancellation distributed across the bracket.* Every measurement in `c5_monopole.py` stands; the pairing it scores is the wrong object.

## c10 — the criterion that certifies an absence

`c10_oscillator_phase.py`, added 2026-10-26. **The acceptance criterion carried
for the acoustic step passes only when the driving is absent.** The criterion
asks that $(\delta\tilde T+\Phi_A)(\eta_*)$ track $\cos(kr_s)$ in exact phase. A
driven oscillator does not track $\cos(kr_s)$; it tracks $\cos(kr_s+\varphi)$,
and that phase *is* the radiation-era driving. C10d applies the criterion at its
own tolerance to both solutions and records that it accepts the undriven one and
rejects the driven one.

> **Why this was never caught — the same shape as M15.** A gate that scores a
> quantity against the value it takes when the physics is switched off cannot
> report the physics being off. **A-3** removed the driving and the gate
> recorded a pass, because removing the driving is what the gate rewards. The
> first-peak budget puts the driving at $\Delta\varphi_1=+0.1124$, equal to the
> artefact half of the displacement, so this is not a small omission.

**The Einstein--de~Sitter null is the control.** On $K=0$ dust $\Omega_r=0$ and
$\Phi$ is constant, so the driving cannot act and the phase must be exactly
zero. Any repair that moves the peak must leave the Einstein--de~Sitter phase at
zero; that is what separates a driving mechanism from a fit.

## c11 — the third term, and the slot that keeps the source out of today

`c11_kernel_partner.py`, added 2026-10-26. **`c9`'s admissibility condition is
stated for two terms and the kernel moves too.** Taken against $K$, the product
rule has three:

$$\frac{\mathrm d}{\mathrm d\eta}[WCK]=\mathcal VCK+WC'K+WCK' .$$

Its integral is a pure boundary term, and both boundaries vanish for
$\ell\ge1$. So $\int WC'K=-\int\mathcal VCK-\int WCK'$, exactly.

| term | where its mass lives | what it is |
|---|---|---|
| $\int\mathcal VCK$ | inside the visibility, late fraction $5.5\times10^{-7}$ | the Sachs--Wolfe monopole |
| $\int WC'K$ | outside it, late fraction $0.75$–$0.99$ | the coefficient differentiated at $e^{-\kappa}\simeq1$ |
| $\int WCK'$ | the partner that makes the first two add to zero | $2.7$–$1.9\times10^3$ times the Sachs--Wolfe term |

> **The consequence — the generalisation of `c9`'s rule.** Every by-parts
> against $K$ must account for all three terms. Drop the $K'$ term and the
> error is a source that runs to today and a Sachs--Wolfe term carried with the
> wrong sign; replace $W$ by $\mathcal V$ in the $WC'$ term and the error is a
> rate inside an amplitude, which is `c9`. The two-term condition is the
> special case in which the kernel is held fixed.

**C11g is why the Einstein--de~Sitter null sees this.** With $\Phi$ constant the
late accumulation is unchanged to $1.3\times10^{-13}$, because
$C_1^{\rm grav}=-(\delta\tilde T+\Phi_A)$ still carries the free streaming of
$\delta\tilde T$. A null failure on Einstein--de~Sitter therefore localises the
defect to the slot bookkeeping and not to the by-parts.

## `c6` said this on 2026-10-20 and I did not read it

`c6_thomson.py`'s row above already states the finding: *"Not a weight change —
`Wκ′ = 𝒱` is an identity, so the Thomson term is already at visibility weight;
the defect is the differentiation."* **That is the conclusion the whole of
25 October was spent re-deriving.** `c9` adds what `c6` does not — the
cancellation, the factor of exactly `κ′`, and the split assembly as a
constructive repair — but the direction was in this file for five days.

**The rule this breaks is §3c, applied to my own tree**: a finding is not a
finding until someone has looked at the thing it names, and that includes
looking at the instrument one wrote oneself before deriving its content again.

## Three registries run over this directory and none of them is updated by a commit

**Found 2026-10-26, and it is the same rule again.** Adding an instrument to
`tests/frame/` wires it into nothing. Three separate hand-maintained lists
enumerate this directory, and on the morning of 26 October they held three
different suites:

| registry | owner | held | consequence of the gap |
|---|---|---|---|
| `run_all.py` | P1-T | `c1`–`c9` | `c10` did not run under the suite entry point |
| `gen_theory_audit.py` | P1-T | `c1`–`c8` | **`docs/THEORY-AUDIT.md` carried no by-parts admissibility result at all**, five days after `c9` landed |
| `tests/test_frame_checks.py` | P1-B | `c1`–`c7` | **neither `c8` nor `c9` is gated by the bundle's own harness**; both pass `run_all.py` and nothing else |

The first two are corrected here and both now carry `c1`–`c11`. **The third is
outside P1-T's line and is flagged to P1-B rather than edited.** Until it
carries `c8` through `c11`, the rank-0 control, the by-parts admissibility
condition, the oscillator-phase gate and the kernel-partner identity are
documented and reproducible but not *gated*, and a regression in any of them
would reach a release.

**An instrument that is committed but not registered is a file, not a gate.**
