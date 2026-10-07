<!-- GENERATED FILE — DO NOT EDIT BY HAND.

Regenerate with:  python scripts/sync_conventions.py --source <path>

Source      : C:\Users\01404122\Documents\Claude\NonlinearShear\docs\conventions.md
SHA-256     : 064a3b659cd95502d2cbd94b9c123c7312178c6143cb6f764b964b5deed7d68e
Generated   : 2026-10-06

The normative sheet lives in the project repository and is owned by the
conventions gate. This bundle carries a generated copy so that the code and the
conventions it was written against ship together. If `--check` fails, the source
has moved: regenerate, re-read the diff, and record anything that changes a
weight or a sign in ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md.

Equation numbers in the source sheet are arXiv numbers. This bundle cites
PUBLISHED numbers. The re-pointing map is tracked separately; do not assume a
constant offset.
-->

# Conventions — the normative sheet

**Gate C1/C2 · built 2026-10-03 · stream 9 (conventions gate).**
Brief: `docs/streams/stream-conventions-gate.md`. Findings and the disagreement
list: `docs/streams/stream-conventions-results.md`. General-ℓ arithmetic behind
the rows marked ✓sym: `docs/streams/stream-conventions-check.py` (all pass).

## How to read this sheet

**Definitions are stipulations; results are checkable.** A row marked **DEF**
is adopted from the source named, with its equation number, and is not
"verified". It cannot be wrong, only inconsistently applied. A row marked
**RES** was derived *from* the definitions, and is audited here under them.

**Every line names a primary source.** Nothing here is taken from `CLAUDE.md`,
from either manuscript, or from the gate brief. Where a line is this project's
own choice, because no source fixes it, it says **STIPULATED HERE** and gives
the reason.

**§3b status of each audit:**
**IA** means settled in index algebra (recursion, contraction identities,
trace removal, or calculus on the printed equation, with no representation).
**CONF** means confirmatory only. It introduced a representation, and the row
names the convention it imported.

### Sources and how they are numbered

> ## The numbers below are arXiv numbers, and the published papers differ
>
> **Added by P1-T, 2026-10-05.** Annals I and II are now in the repository as
> published — `sources/pdf/annalsI-GE2000.pdf`, `annalsII-GDE2000.pdf` — and as
> LaTeX source in `sources/annals/`. **The published equation numbering differs
> from the arXiv numbering used throughout this sheet, and not by a constant
> offset.** In Annals I the Helmholtz equation is **(47)** in print against (48)
> on arXiv; the harmonic normalisation
> `Q_{A_ℓ} = (−k_phys)^{−ℓ} D_⟨A_ℓ⟩ Q` is **(48)** in print against (49) on
> arXiv; `G_ℓ[Q] = O^{A_ℓ}Q_{A_ℓ}` is **(49)** against (50); the mode expansion
> of `τ_{A_ℓ}` is **(53)** against (54) — while `O^{A_ℓ} = e^⟨A_ℓ⟩` is **(15) in
> both**. So a blanket offset is wrong and each number must be resolved
> individually from the PDFs.
>
> **The sheet's content is unaffected; only its citations are.** Nothing is
> withdrawn here. But anything citing this sheet into print must carry the
> printed number, because Paper 1 cites the published Annals papers. Re-pointing
> the rows is Coordination's, and P1-T is building the map as it writes the
> paper's conventions section.
>
> Two rows gain a source. **C1.1, the signature**, is sourced to MGE99 and the
> thesis and could not be sourced to GE98 because GE98 never states one — but it
> is fixed by GE98's own algebra: the paper writes `e^a e_a = 1, e^a u_a = 0`
> (twice) and defines `p_ab = h_ab − e_a e_b` with `p_a{}^a = 2`, a trace that
> holds only for `e^a e_a = +1`. **Annals I is (−,+,+,+)**, by index algebra on
> its own printed equations. The splice of GE98 harmonics onto MGE99 signature is
> therefore safe, and is now checked rather than assumed.
>
> **C3a is superseded in its consequence.** The `(−1)^c` contraction-count rule
> of C3a.5 is correct arithmetic about the plane-wave *basis tensor* and has no
> effect on any coupling: `τ_ℓ` is defined as the coefficient of `Q_{A_ℓ}`, so
> every bracket is a relation among the `τ_ℓ` and is invariant under
> `Q_{A_ℓ} → λ^ℓ Q_{A_ℓ}`, `τ_ℓ → λ^{−ℓ} τ_ℓ`. The phase cancels. **P-3 is
> settled: both brackets keep their printed relative signs and both pairs cancel
> at leading order.** The representation-free route is Annals II **Appendix F,
> pp. 379–380, Eqs. (F.1)–(F.4)**, which matches the covariant mode recursion to
> Hu & Sugiyama, Wilson & Silk Eq. (7), Ma & Bertschinger (49)/(50) and Seljak &
> Zaldarriaga Eq. (3d) — four external hierarchies in real coefficients. A basis
> phase leaking into the couplings would break all four matches.
>
> **G1 stands as a finding and should be re-filed as inconsequential**, with the
> reason above: that is the useful form, because it explains why the slip never
> produced a wrong result in twenty-five years.

| Key | Source | Numbering used |
|---|---|---|
| **GE98** | Gebbie & Ellis, *Covariant CMB anisotropies I*, arXiv:astro-ph/9804316 | arXiv PDF, `sources/pdf/GebbieEllis1998-covariant-cmb-I.pdf` |
| **MGE99** | Maartens, Gebbie & Ellis, PRD **59**, 083506, arXiv:astro-ph/9808163 | arXiv PDF, `sources/pdf/MaartensGebbieEllis1999-nonlinear-dynamics.pdf`. Agrees with the numbers `provenance.md` uses, e.g. (89) photon quadrupole |
| **Th** | Gebbie, PhD thesis, UCT 1999, `sources/TGEBBIE-PHD-001.zip` | Compiled 2026-10-03 (`pdflatex PHD-MAIN.TEX` ×2, 208 pp.). **Every number was resolved from the `.aux` files**, none counted by hand. Chapter 1 is GE98 and Chapter 2 is MGE99 §§II–V. **They are the same sources and count once** (§3a) |
| **CL** | Challinor, CQG **17**, 871 (2000), arXiv:astro-ph/9906474 | arXiv PDF, fetched to the session scratchpad, not to `sources/` |
| **BF** | Beneke & Fidler, PRD **82**, 063509 (2010), arXiv:1003.1834 | arXiv PDF, as above |
| **P09** | Pitrou, CQG **26**, 065006 (2009), arXiv:0809.3036 | arXiv PDF, as above |

---

## C1 — Signature and projector

| | Statement | Source | Kind |
|---|---|---|---|
| C1.1 | Signature **(−,+,+,+)**; `u^a u_a = −1` | MGE99 p.3 (*"the signature is (− + ++)"*), p.4 text; Th front matter, *Notation and Conventions* | DEF |
| C1.2 | `h_ab = g_ab + u_a u_b` projects into the rest space of `u^a` | MGE99 p.4 (a) | DEF |
| C1.3 | `ε_abc = η_abcd u^d`; `η_abcd = −√|g| δ^0_[a δ^1_b δ^2_c δ^3_d]` | MGE99 p.4 | DEF |
| C1.4 | `R^a_bcd = −∂_d Γ^a_bc + …`, `R_ab = R^c_acb`, `∇_[a∇_b]u_c = ½R_abcd u^d` | MGE99 p.3; Th front matter | DEF |
| C1.5 | Photon direction: `p^a = E(u^a + e^a)`, `e^a e_a = +1`, `e^a u_a = 0`, `E = −u_a p^a` | MGE99 (45); GE98 §2 | DEF |
| C1.6 | **A sign is acquired once per contracted index on a change of signature**, so rank-raising and rank-lowering couplings translate differently | CL p.2, *"Raising or lowering an index incurs a sign change when transforming between signatures"*. Exhibited in row T-CL below | RES, IA ✓sym |

## C2 — Spatial derivative and kinematics

| | Statement | Source | Kind |
|---|---|---|---|
| C2.1 | `D_c J^{a…}{}_{…b} = h_c{}^d h^a{}_e ⋯ h_b{}^f ∇_d J^{e…}{}_{…f}`; overdot `J̇ = u^c∇_c J` | MGE99 p.4 | DEF |
| C2.2 | **`∇_b u_a = −A_a u_b + ⅓Θh_ab + ε_abc ω^c + σ_ab`**, where the acceleration term is **`−A_a u_b`** (contracting with `u^b` returns `+A_a`) | MGE99 p.4, display after (3), unnumbered; Th **(2.11)** | DEF |
| C2.3 | `Θ = D^a u_a`, `A_a = u̇_a = A_⟨a⟩`, `σ_ab = D_⟨a u_b⟩`, `ω_a = −½ curl u_a`, `curl V_a = ε_abc D^b V^c` | MGE99 p.4 | DEF |
| C2.4 | The vorticity sign differs from the Cargèse 1998 convention | Th front matter and footnote at (2.11) | DEF (warning) |
| C2.5 | Rank-2 and rank-3 PSTF distortions: `D_⟨a V_b⟩ = D_(a V_b) − ⅓(div V) h_ab`, `D_⟨a S_bc⟩ = D_(a S_bc) − ⅖ h_(ab (div S)_c)` | MGE99 p.4 | DEF |

## C3 — Harmonic normalisation

| | Statement | Source | Kind |
|---|---|---|---|
| C3.1 | Helmholtz: **`D^a D_a Q = −k_phys² Q`**, `k_phys = k/a`, `Q` time-independent | GE98 **(48)**; Th **(1.47)** | DEF |
| C3.2 | **`Q_{A_ℓ} = (−k_phys)^{−ℓ} D_⟨A_ℓ⟩ Q`**. The stripped factor is **`(−k_phys)^ℓ`: real, no `i`.** For a real eigenfunction `Q`, every `Q_{A_ℓ}` is real | GE98 **(49)**; Th **(1.48)**; restated in GE98 p.23 below (134), and in Th App. D footnote to **(D.44)** as `(−λ)^{−ℓ}D_⟨A_ℓ⟩Q = Q_{A_ℓ}` | DEF. **Seed verified against the PDF, 2026-10-03** |
| C3.3 | Mode function `G_ℓ[Q] = O^{A_ℓ}Q_{A_ℓ} = (−k_phys)^{−ℓ}O^{A_ℓ}D_⟨A_ℓ⟩Q` | GE98 (50), (51); Th (1.50) | DEF |
| C3.4 | Mode expansion `τ_{A_ℓ}(x) = Σ_k τ_ℓ(t,k)(−k_phys)^{−ℓ}D_⟨A_ℓ⟩Q = Σ_k τ_ℓ Q_{A_ℓ}` | GE98 (54); Th (1.48) ff. | DEF |
| C3.5 | **The sign of a scalar's mode coefficient, `X = λ Σ_k X(k) Q`, is not fixed by any source.** GE98 never expands a scalar field. The thesis and both manuscripts write gradients as `D_a X = +(k/a) X(k) Q_a`, which under C3.2 means **`λ = −1`**. **STIPULATED HERE: λ = −1**, because that is the existing usage, and it must be stated wherever a mode coefficient is | Th App. D **(D.44)**: `(D_a ln ρ_M)^k = +(k/a)Δ(k)Q_a`. Consequence under C3.2 by IA: `D_aX = −λ k X(k) Q_a`, `D_⟨aD_b⟩X = +λ k² X(k) Q_ab` | STIPULATED HERE |
| C3.6 | The radial eigenfunction has real stripped factor too: `O^{A_ℓ}_{(χ)}D_⟨A_ℓ⟩Q = (−k_phys)^ℓ O^{A_ℓ}_{(χ)}O^{(k)}_{A_ℓ}R_ℓ` | GE98 **(72)**, first relation | RES. The **second** relation of (72), `O^{A_ℓ}Q_{A_ℓ} = (−k_phys)^ℓ Q_ℓ`, has a factor `(−k)^ℓ` too many under C3.2 and (62), (67). Apparent misprint, low consequence (results note, G3) |

### C3a — Plane waves, and the phase they carry

| | Statement | Source | Kind |
|---|---|---|---|
| C3a.1 | GE98's flat plane wave is **`Q = exp(−i k_phys e^{(k)}_a x^a)`** | GE98 **(145)** | DEF |
| C3a.2 | `D_⟨A_ℓ⟩ Q = (−i k_phys)^ℓ O^{(k)}_{A_ℓ} Q` | GE98 **(147)** = (59); Th **(1.58)** | RES (calculus on C3a.1) |
| C3a.3 | **Hence, under C3.2, `Q_{A_ℓ} = (−k)^{−ℓ}(−ik)^ℓ O^{(k)}_{A_ℓ}Q = i^ℓ O^{(k)}_{A_ℓ} Q`.** | Arithmetic on GE98 (49) and (147) | RES, CONF: imports the plane wave of GE98 (145) |
| C3a.4 | **GE98 (60) = (148), Th (1.59) and Th (A.50) print `Q_{A_ℓ} = (−1)^ℓ O^{(k)}_{A_ℓ}Q`. That is inconsistent with C3.2 + C3a.2.** It is the phase of the definition `Q_{A_ℓ} = (+ik)^{−ℓ}D_⟨A_ℓ⟩Q`, not of GE98 (49) | GE98 (60), (148); Th (1.59), (A.50). **One source**: Th Ch. 1 and App. A reproduce GE98 | RES: **error under C3.2** |
| C3a.5 | **The contraction-count rule.** If a two-mode product `N_{A}(k′) M_{B}(k)` is projected onto `Q_{C}(k*)` with `c` index pairs contracted, the aligned mode-form coefficient carries **`(−1)^c` relative to the uncontracted coupling** under C3a.3, and **`+1`** under the printed C3a.4. Acceleration rank-lowering of τ (`A^bτ_{bA_ℓ}`, c = 1) flips. Shear (`σ^{bc}τ_{bcA_ℓ}`, c = 2) and both rank-raising couplings (c = 0) do not | Arithmetic: `i^{ℓ+m}/i^{ℓ+m−2c} = (−1)^c`, with Th (A.51) as the product rule | RES, CONF: imports GE98 (145) and Th (A.51). **Same argument as stream H, H-1 route 1, located at its source. Not an independent check** (§3a) |
| C3a.6 | The thesis Fourier kernel is `e^{+ik·x}` (Th (A.42)) while GE98's plane wave is `e^{−ik·x}` (GE98 (145)). A Fourier coefficient of the thesis multiplies `Q(−k)`, whose `Q_{A_ℓ}` phase is `(−i)^ℓ`. **Any calculation that mixes the two must say which is used** | Th (A.42); GE98 (145) | DEF clash, recorded |

## C4 — The harmonic recursion

All flat (`K = 0`) unless stated. `k ≡ k_phys`.

| | Statement | Source | Kind |
|---|---|---|---|
| C4.1 | **`D_a Q = −k Q_a`** | C3.2 at ℓ = 1 | RES, IA |
| C4.2 | **`D_⟨a Q_{A_ℓ⟩} = −k Q_{aA_ℓ}`** (rank-raising: one factor `−k`) | C3.2: `(−k)^{−ℓ}D_⟨aA_ℓ⟩Q = (−k)·(−k)^{−(ℓ+1)}D_⟨aA_ℓ⟩Q` | RES, IA |
| C4.3 | **PSTF divergence of a gradient:** `D^a D_⟨a Q_{A_ℓ⟩} = (ℓ+1)/(2ℓ+1) · (−k²)[1 − (K/k²)ℓ(ℓ+2)] Q_{A_ℓ}` | GE98 **(137)** | RES (sourced; ℓ = 0, 1 IA by hand) |
| C4.4 | **`D^a Q_{aA_ℓ} = +(ℓ+1)/(2ℓ+1) · k [1 − (K/k²)ℓ(ℓ+2)] Q_{A_ℓ}`** (rank-lowering: **`+k`**, against `−k` for raising) | C4.2 into C4.3. **Cross-check:** at ℓ = 1, Th App. D footnote to (D.44) prints `D^bQ_ab = −⅔(ak)^{−1}(−k²+3K)Q_a`, which is identical | RES, IA |
| C4.5 | **Mode recursion:** `e^aD_a G_ℓ[Q] = +k[ℓ²/((2ℓ+1)(2ℓ−1)) (1 − (K/k²)(ℓ²−1)) G_{ℓ−1} − G_{ℓ+1}]`. Free streaming in mode form couples `ℓ±1` with **opposite** real signs, although both covariant couplings are `+` | GE98 **(57)** = (138). At K = 0 it is re-derived here from C4.2, C4.3 and C6.4 | RES, IA |
| C4.6 | Curvature-modified Helmholtz: `D^aD_a Q_{A_ℓ} = −k̃_ℓ² Q_{A_ℓ}`, `−k̃_ℓ² = a^{−2}(Kℓ(ℓ+2) − k²)` | GE98 (56) = (135), (136) | RES (sourced) |

## C5 — PSTF basis, β_ℓ, Δ_ℓ

| | Statement | Source | Kind |
|---|---|---|---|
| C5.1 | **`O^{A_ℓ} = e^⟨A_ℓ⟩`**, the PSTF part of `e^{a₁}⋯e^{a_ℓ}`; `τ(x,e) = Σ_ℓ τ_{A_ℓ}O^{A_ℓ}` | GE98 **(15)**, (16); Th **(1.15)** | DEF |
| C5.2 | **`β_ℓ = O^{A_ℓ}O_{A_ℓ} = (ℓ!)²2^ℓ/(2ℓ)! = ℓ!/(2ℓ−1)!!`** | GE98 **(24)**; Th **(1.23)** | DEF ✓sym |
| C5.3 | `β_ℓ = (2ℓ+1)/(ℓ+1) β_{ℓ+1}`, `β_ℓ = ℓ/(2ℓ−1) β_{ℓ−1}`, `β_{ℓ+1}/β_{ℓ−1} = ℓ(ℓ+1)/((2ℓ+1)(2ℓ−1))` | GE98 **(25)**; Th **(1.24)** | RES ✓sym |
| C5.4 | `O^{A_ℓ}O′_{A_ℓ} = β_ℓ P_ℓ(e·e′)` | GE98 (28), (140) | RES (sourced) |
| C5.5 | **`Δ_ℓ = 4π 2^ℓ(ℓ!)²/(2ℓ+1)! = 4πβ_ℓ/(2ℓ+1)`**; `∫dΩ O^{A_ℓ}O_{B_m} = δ_{ℓm} Δ_ℓ h^⟨A_ℓ⟩{}_⟨B_ℓ⟩` | GE98 **(119)**; MGE99 **(47)** (same value, written `4π(ℓ!)²2^ℓ/(2ℓ+1)!`) | DEF ✓sym |
| C5.6 | Inversion: `τ_{A_ℓ} = Δ_ℓ^{−1}∫dΩ O_{A_ℓ} τ(x,e)` | GE98 (23) = (122); MGE99 (47), (79); Th (2.42), (2.78) | RES |
| C5.7 | `h^⟨A_ℓ⟩{}_⟨A_ℓ⟩ = 2ℓ+1` | GE98 (121) | RES |
| C5.8 | `∫e^{A_ℓ}dΩ = 4π/(ℓ+1) h^{(a₁a₂}⋯h^{a_{ℓ−1}a_ℓ)}` for ℓ even, 0 for ℓ odd | MGE99 (48); GE98 (113) (same content at rank 2ℓ) | RES |

## C6 — PSTF contraction identities

| | Statement | Source | Kind |
|---|---|---|---|
| C6.1 | **`e_{a₁} O^{A_ℓ} = ℓ/(2ℓ−1) O^{A_{ℓ−1}}`**; equivalently **`e_a O^{aA_ℓ} = (ℓ+1)/(2ℓ+1) O^{A_ℓ}`** | GE98 **(21)**; Th **(1.20)** | RES (sourced; ℓ = 1, 2 by hand) |
| C6.2 | Iterated: `e_a e_b O^{abA_ℓ} = (ℓ+1)(ℓ+2)/((2ℓ+1)(2ℓ+3)) O^{A_ℓ}` | C6.1 applied twice | RES, IA |
| C6.3 | `O^{A_{ℓ+1}} = e^{(a_{ℓ+1}}O^{A_ℓ)} − ℓ²/((2ℓ+1)(2ℓ−1)) h^{(a_{ℓ+1}a_ℓ}O^{A_{ℓ−1})}` | GE98 **(22)**; Th **(1.21)** | RES (sourced) |
| C6.4 | **EMT Lemma 2:** `V_⟨b S_{A_ℓ}⟩ = V_(b S_{A_ℓ)} − ℓ/(2ℓ+1) V^c S_{c(A_{ℓ−1}}h_{a_ℓ b)}`; with `V = e`, `S = O`, this gives `e^bO^{A_ℓ} = O^{bA_ℓ} + ℓ/(2ℓ+1) h^{b⟨a_ℓ}O^{A_{ℓ−1}⟩}` | MGE99 **(62)**; Th **(2.62)**; GE98 **(20)**. All three cite Ellis, Matravers & Treciokas (1983) p. 470, so they are **one source** | RES (sourced) |
| C6.5 | **EMT Lemma 3** (rank-2 `W` with PSTF `S`): weights `1/(2ℓ+3)`, `2ℓ/(2ℓ+3)`, `ℓ(ℓ−1)/((2ℓ+1)(2ℓ+3))` | Th **(2.63)** | RES (sourced) |
| C6.6 | `v^a e_a f = Σ_ℓ [F_⟨A_{ℓ−1}v_{a_ℓ⟩} + (ℓ+1)/(2ℓ+3) F_{A_ℓa}v^a] e^⟨A_ℓ⟩` | MGE99 **(61)**; Th **(2.61)** | RES (sourced) |
| C6.7 | **The weight `(ℓ+1)/(2ℓ+1)` has two distinct origins, and they must not be confused.** On the *sphere* it is C6.1, a contraction of `e` with `O`. In *space* it is C4.3, a divergence of a gradient. Both are real and positive. Neither carries a phase. The phase enters only through C3a | — | note |

## C7 — Trace removal

| | Statement | Source | Kind |
|---|---|---|---|
| C7.1 | STF part at general rank: `[F_{A_ℓ}]^{STF} = Σ_{n=0}^{[ℓ/2]} B_{ℓn} h_(a₁a₂⋯h_{a_{2n−1}a_{2n}} F_{a_{2n+1}…a_ℓ)}`, with `B_{ℓn} = (−1)^n ℓ!(2ℓ−2n−1)!!/((ℓ−2n)!(2ℓ−1)!!(2n)!!)` | GE98 **(17)** (Pirani); Th **(1.17)** | DEF |
| C7.2 | PSTF = project, then STF: `T_⟨ab⟩ = [[T_ab]^{STF}]^P` | GE98 (18) | DEF |
| C7.3 | Explicit rank 2: `S_⟨ab⟩ = {h_(a^c h_b)^d − ⅓h^{cd}h_ab}S_cd` | MGE99 p.3 | DEF |
| C7.4 | `O^{A_ℓ} = Σ_{k=0}^{[ℓ/2]} B_{ℓk} h^{(A_{2k}}e^{A_{ℓ−2k})}` | GE98 (19); Th (1.18) | RES (sourced) |

## C8 — Fourier measure

| | Statement | Source | Kind |
|---|---|---|---|
| C8.1 | `f(x) = (2π)^{−3}∫d³k e^{+ik·x} f(k)`, `f(k) = ∫d³x e^{−ik·x} f(x)`, `⟨Δ(k)Δ*(k′)⟩ = (2π)³δ(k−k′)P(k)` | Th **(A.42)**, (A.43), **(A.45)**; same kernel as BF **(41)** | DEF |
| C8.2 | `Σ_k → ∫d³k → ∫k²dk∫dΩ_k` used interchangeably; **the normalisation volume is not fixed by any source** | Th **(A.46)** (*"we will not be considering closed universes hence the loose nature of the notation"*) | DEF (gap) |
| C8.3 | Convolution `W = NM`: `W(k) = ½∫d³k′/(2π)³[N(k−k′)M(k′) + N(k′)M(k−k′)]`; aligned and isotropic: **`W(k) = 4π∫k′²dk′/(2π)³ N(k′)M(|k−k′|)`** | Th **(A.48)**, **(A.49)** | RES |
| C8.4 | Arithmetic: **`4π/(2π)³ = 1/(2π²) = 2/(2π)²`**. It is **not** `1/(2π)²`; see results note, G7 | — | IA ✓ |

## C9 — Translation table

Each row maps the external quantity **into this sheet**. Every map was checked
by reproducing at least one printed coefficient of the external source.

| | Source | Signature | Multipole normalisation | Map into this sheet | Checked by |
|---|---|---|---|---|---|
| **T-MGE** | MGE99 | (−,+,+,+), same | `f = Σ F_{A_ℓ}e^{A_ℓ}` (46); `Π_{A_ℓ} = ∫E³F_{A_ℓ}dE` (50); `Π = ρ/4π`, `Π^a = 3q^a/4π`, `Π^{ab} = 15π^{ab}/8π`; `τ_{A_ℓ} ≈ (π/ρ)Π_{A_ℓ}` (80) | Identity. **Known defects:** E9 (`−(ℓ+2)` in (71), (88), (90), (99)), E12, E13, E14, E15. See `provenance.md` §A | (70)→(71) by `∫E³dE` reproduces 5 of 6 kinematic rows; the 6th gives `+(ℓ+2)` ✓sym. (89) at ℓ = 2 prints `+8/15 ρσ`, i.e. `+(ℓ+2)` |
| **T-Th-K** | Th (2.72)–(2.75), K/Π form | same | as MGE99 | Identity; carries E9 in (2.73) | (2.72)→(2.73) by the same `∫E³dE` reproduces every row except `σ, ℓ−2` |
| **T-Th-T** | Th (2.81)–(2.84), 𝒯̇ form | same | `𝒯^{A_ℓ} = (π/rT⁴)Π^{A_ℓ}` (unnumbered, before (2.81)) | **Every kinematic term flips overall sign** against (2.73), because it is moved to the RHS. Compare coefficients only after flipping. Carries E9 (as `+(ℓ+2)` on the RHS) and E15 | All six (2.73) kinematic rows map to (2.84) with exactly one flip |
| **T-CL** | CL | **(+,−,−,−)** (CL p.2) | `I(e) = Σ Δ^C_ℓ{}^{−1} I_{A_ℓ}e^{A_ℓ}` (2.22), **`Δ^C_ℓ = 4π(−2)^ℓ(ℓ!)²/(2ℓ+1)! = (−1)^ℓ Δ_ℓ`** (2.23); `ρ = I`, `q_a = I_a`, `π_ab = I_ab` (2.24) | **`I^{A_ℓ}_{CL} = Δ_ℓ Π^{A_ℓ}_{MGE}` with all indices up.** Under `g → −g` at fixed `u^a`: `σ_ab → −σ_ab`, `A_a → −A_a` (CL footnote to §2). `cosθ = −e^ae′_a` in CL (2.27) | CL (2.25) free streaming: `−ℓ/(2ℓ+1)D_⟨a_ℓ I_{A_{ℓ−1}⟩}` and `+D^bI_{bA_ℓ}` both reproduced from MGE99 (71) ✓sym. `−8/15 δ²_ℓ Iσ` gives `+(ℓ+2)` (`provenance.md` [CL]) |
| **T-P** | P09 | **(−,+,+,+)**, by IA: (1.5) `S_μν = g_μν + e^o_μe^o_ν − n_μn_ν` annihilates `e_o` only if `e_o·e_o = −1`; (1.4) `n·n = +1` | `I = Σ I_{A_ℓ}n^{A_ℓ}` (1.28), `Δ_ℓ = 4πℓ!/(2ℓ+1)!!` (1.29); normal modes `I^m_ℓ(k)` via `e^{−ik·x}` and `Y^m_{A_ℓ}` (7.5)–(7.10) | `I_{A_ℓ}` = this sheet's `F_{A_ℓ}`, identically (same expansion, same `Δ_ℓ` ✓sym). Normal-mode coefficients carry Pitrou's `Y^m_{A_ℓ}` normalisation (7.8), including `(−1)^m`; **not mapped here** | Δ_ℓ ✓sym. **Not checked** against a hierarchy coefficient; Pitrou works in Poisson gauge |
| **T-BF** | BF | **(+,−,−,−)** (BF p.2, notation paragraph) | `f = Σ_{ℓm}(−i)^ℓ √(4π/(2ℓ+1)) f_ℓm {}_sY_ℓm(n)` (43), inverse (44); Fourier as C8.1 (41); convolution (42) | **An explicit `(−i)^ℓ` per multipole.** For comparison with C3a: BF's `(−i)^ℓ` is the phase a mode coefficient carries under C3a.3 when the field is `e^{+ik·x}`. Observer at rest in BF | Signature and (41)–(44) read. **No coefficient reproduced**: BF's hierarchy is in `(ℓ,m)` and tetrad form. **OPEN** for C2 |

---

## What this sheet does not settle

1. **The mode-form coefficients of a two-mode product.** No source states a
   product rule consistent with C3.2. Th (A.51) states one together with the
   inconsistent phase of C3a.4. **H-1/H-2 is decidable under this sheet, but
   the sheet does not decide it.** That needs one normalisation, C3.2 with
   C3a.3 or an explicitly stipulated alternative, carried through both the
   contraction and the integral solution `τ_ℓ(k)`.
2. **The normalisation volume `V`** (C8.2).
3. **BF and Pitrou at the level of hierarchy coefficients** (T-BF, T-P).
