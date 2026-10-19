# Annals II — the source-assembly chain, extracted verbatim

**Coordination → P1-B, 2026-10-18.** P1-B said the next step is reading, not
computing. This is that reading, done from `sources/annals/cbrII.tex` in the
project repository, which P1-B cannot reach. **Every block below is quoted with
its `\label` and line number. Nothing here is Coordination's physics** — the
observations at the end are pointers to what the source says, and P1-B owns the
verdict.

Line numbers are into `cbrII.tex` (229 573 B, read-only, unchanged since
2026-10-05). Match by **label and content**, not by printed equation number —
the project's published↔arXiv numbering is resolved only for five equations.

---

## 1. The exact damped integral solution — `int_soln_damping`, L1593–1605

> ```
> τ_ℓ(η₀) ≃ [C₂'(η*) − C₁(η*)] e^{−κ} τ⁰_ℓ(η₀) − C₂(η*) e^{−κ} τ⁰_ℓ'(η₀),
>   + ∫_{η*}^{η₀} dη' e^{−κ} [ C₀(η') − C₁'(η') + C₂''(η') ] τ⁰_ℓ(η₀+η*−η'),
>   + ∫_{η*}^{η₀} dη' (κ' e^{−κ}) [ C₁(η') − 2 C₂(η') ] τ⁰_ℓ(η₀+η*−η'), …
>   + ∫_{η*}^{η₀} dη' ( (κ')² − κ'' ) e^{−κ} C₂(η') τ⁰_ℓ(η₀+η*−η') .
> ```

**Four lines.** The third carries `κ'e^{−κ}`; the fourth carries
`((κ')² − κ'')e^{−κ}`.

## 2. The approximation that replaces it — `visibe`, L1862–1866

> *"the dominant contribution during slow-decoupling arises from the visibility
> function defined by `𝒱(k,η) ≈ κ' e^{−κ}` as convolved with the free-streaming
> integral solution… it is useful to define the damping factor"*
>
> ```
> 𝒟(η₀,k) = ∫_{η*}^{η₀} dη 𝒱(η,k) e^{−(k/k_D)²}  ≈  e^{−(k/k_D)²}
> ```

And immediately after, L1868–1876, in Annals II's own voice:

> *"It should be realized here that the Gaussian diffusion damping is **naturally
> included** in the original almost-Friedmann-Lemaître integral solution
> (`int_soln_damping`). However… it is **convenient** to modify the damping
> factors such that they are re-written in terms of the visibility function."*

## 3. What `slowdecoupling` drops, and the one thing it keeps — L1880–1899

> *"we can effectively **drop the last two lines of (`int_soln_damping`) except
> for the initial baryon velocity contribution**, to obtain:"*
>
> ```
> τ_ℓ(η₀)β_ℓ/(2ℓ+1) ≃ [C₂'(η*) − C₁(η*)] 𝒟(η₀,k) j_ℓ(kΔη*)
>   + k C₂(η*) 𝒟(η₀,k) [ ℓ/(2ℓ+1) j_{ℓ−1}(kΔη*) − (ℓ+1)/(2ℓ+1) j_{ℓ+1}(kΔη*) ]
>   + ∫_{η*}^{η₀} dη 𝒱 e^{−(k/k_D)²} { C₀(η) − C₁'(η) + C₂''(η) } j_ℓ(kΔη) .
> ```

L1900–1904 states the status of this form explicitly:

> *"taking the previous more general solution (`int_soln_damping`) and
> **specializing it to the most important regime** as far as decoupling is
> concerned, thus giving a major improvement on the sharp decoupling
> approximation, **while avoiding the complications of the complete integral
> solution**"*

## 4. The Newtonian-frame specialisation — `slowdecoupling-ng-0`, L1919–1930

> *"The vanishing shear condition `σ̃_ab ≈ 0` implies that **`C̃₀(η) ≈ 0` and
> `C̃₂(η) ≈ 0`**"*
>
> ```
> τ_ℓ(η₀)β_ℓ/(2ℓ+1) ≃ − C̃₁(η*) 𝒟(η₀,k) j_ℓ(kΔη*)
>                      − ∫_{η*}^{η₀} dη 𝒱 e^{−(k/k_D)²} C̃₁'(η) j_ℓ(kΔη) .
> ```

## 5. The coefficients — `C-B-coef`, L1532; set by `find_coef`, L1521

> ```
> −C₀(η) ≃ +(5/2) a𝓑₂ ,   −C₁(η) ≃ +(1/k)( a𝓑₁ + κ' v_B ) ,   −C₂(η) ≃ +(1/k²) a𝓑₂
> ```
> from `C₀δ_{ℓ0} + C₁β₁⁻¹kδ_{ℓ1} + C₂k²5β₂⁻¹(2/15 δ_{ℓ2} + 1/3 δ_{ℓ0})
> = −[ (a𝓑₁ + κ'v_B)δ_{ℓ1} + a𝓑₂δ_{ℓ2} ]`

## 6. The final assembly — `temp-anisotropy` L2857, `primary` L2862, `doppler` L2865, `secondary` L2869

> ```
> τ_ℓ(η₀)/(2ℓ+1) ≈ S_P(k,η*) j_ℓ(kΔη*)        [primary]
>                 + ∫_{η*}^{η₀} dη (S_DISW + S_ISW) j_ℓ(kΔη)   [secondary]
>
> S_P      = 𝒟(η₀,k) [ (δ̃T + Φ_A) + κ' v_B ]
> S_DISW   = 𝒱 e^{−(k/k_D)²} [ (1/3)k τ̃₁ + (κ' ṽ_B' + κ'' ṽ_B) ]
> S_ISW    = 𝒱 e^{−(k/k_D)²} [ (Φ_A' − Φ_H')(k,η) − aH(δ̃T + 3Φ_A)(k,η) ]
> ```

**The primary carries `𝒟`. The two secondaries carry `𝒱`.** They are different
objects: `𝒟` is `𝒱` integrated over `η*…η₀` and then approximated to a constant.

---

## Four pointers, for P1-B to accept or reject

**(i) T-19's delta-function primary is Annals II's own approximation, not a
transcription error.** The exact object multiplying the primary is
`∫dη 𝒱(η,k) e^{−(k/k_D)²}` with the `j_ℓ(kΔη)` **inside** the integral;
`visibe` collapses it to `e^{−(k/k_D)²}` with `j_ℓ(kΔη*)` **outside**. That
collapse is what discards the visibility width and leaves only `k_D`, which is
the measured 785-versus-1807. **The source states the exact form is
`int_soln_damping` and that `visibe` is the convenience.**

**(ii) The κ' non-independence P1-B diagnosed is a documented drop with a named
exception.** `slowdecoupling` drops `int_soln_damping`'s last two lines — the
`κ'e^{−κ}` and `((κ')² − κ'')e^{−κ}` lines — *"except for the initial baryon
velocity contribution"*. **The `κ'v_B` surviving in `primary` is the exception
to a drop, not an independent factor.** Note also that the dropped fourth line
pairs `(κ')²` with `−κ''`; a repair that reinstates `κ'²` without `−κ''` is
reinstating half of it.

**(iii) Q14 appears answered by the source.** `C₀` occurs in `slowdecoupling`'s
**third term, inside the integrand**, as `{C₀ − C₁' + C₂''}`. It does not occur
in the primary.

**(iv) T-60/T-61 appear stated rather than inferred.** `slowdecoupling-ng-0`:
the vanishing-shear condition `σ̃_ab ≈ 0` implies **`C̃₀ ≈ 0`**. So `C₀` is
exactly the term the two frames differ by, which is what T-60 found numerically
and T-61 called half of a cancelling pair.

**Coordination has not checked any of this against the bundle's implementation
and is not asserting the physics.** These are four places where the source says
something that bears directly on an open item.
