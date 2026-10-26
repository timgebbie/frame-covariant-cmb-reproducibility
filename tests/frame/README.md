# Frame checks — nine instruments, for `tests/`

**P1-T, 2026-10-19; count corrected and `c9` added 2026-10-26.** Nine self-contained instruments behind the frame-covariance
conditions, plus the generator that turns them into `docs/THEORY-AUDIT.md`.

```
python3 run_all.py                                     # exit 0 only if all pass
python3 gen_theory_audit.py > ../../docs/THEORY-AUDIT.md
python3 -I c6_thomson.py                               # or run one
```

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
| `c9_byparts_admissibility.py` | **the condition under which the by-parts of `c6` is legitimate at all.** `(WC₁)'` splits into `W'C₁ ~ κ'²` and `WC₁' ~ κ''`, which are the two halves of `d(𝒱v̂_B)/dη` and **cancel**; (102) carries `𝒱C₁'` in place of `WC₁'` — larger by **exactly κ'** — and drops `W'C₁`, destroying the cancellation from both sides in one operation. The **split** by-parts, gravitational half by-parted and scattering half left at `K'`, reproduces the ancestor to 1e-13 and contains no `κ''` term at all (P1-T, 2026-10-26) |

## Three things to read before trusting the output

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
