# Theory audit — frame covariance of the source assembly

> **Generated, not transcribed. Do not edit by hand.**
>
> Produced by `tests/frame/gen_theory_audit.py` at 2026-10-22 16:39 UTC. Every number below is read from the machine-readable record of the instrument named beside it. To change this document, change the instrument.

**Status: ALL CHECKS PASS** — 23 assertions across 8 instruments.

## What this document does not establish — read first

Every assertion below is a condition on the functional or on the matching, verified in isolation against fixtures the instruments build themselves. **No project code is imported, so none of these can agree with the solver by construction — and none of them is a claim about the spectrum.** Attribution of a measured symptom to any of these conditions belongs to whoever can run the solver.

Measurements of the solver are recorded in `provenance/BUNDLE-DEFECTS-v1.md` and are **not** restated here. A number copied out of that register into this one is a third copy, and a third copy is how a fabricated quotation enters a brief.

**Polarity.** A row marked `DEFECT PRESENT` asserts that a defect in the antecedent is *still there*; it is not a failure of this suite. If such a row ever reads `DEFECT GONE` the suite fails deliberately, because this document would otherwise assert a defect that no longer exists.

## Results

### The frame identity and the Sachs--Wolfe invariant

Under $\tilde u_a=u_a+w_a$, $\Delta(\delta T+\Phi_A)=(\Delta C_2)'$ with coefficient exactly 1 — the $-Hw_a$ arising from the projector $\tilde h_{ab}=h_{ab}+2u_{(a}w_{b)}$, not from $T$. The boost-invariant combination $(\delta T+\Phi_A)-C_2'$ equals the same value in **both** threadings, independent of $k$ and $\eta$, and it is the Sachs--Wolfe combination.

| assertion | verdict |
|---|---|
| C1a  frame law predicts the measured bracket shift | **PASS** |
| C1b  invariant equal in both threadings | **PASS** |
| C1c  invariant equals the SW amplitude Phi/3 | **PASS** |
| C1d  invariant is k- and eta-independent | **PASS** |

| measured | value |
|---|---|
| `invariant` | Phi/3 |
| `predicted` | Phi/3 |
| `measured` | Phi/3 |

*Instrument: `tests/frame/c1_identity.py`, sha256 `8b505aea5e1b…`*

### The rank-2 weight

The rank-2 sector enters at $k^{-2}$, and the boundary pair left by two integrations by parts is in $S$ and $S'$ — **never** $S''$.

| assertion | verdict |
|---|---|
| C2   k^-2 weight, boundary pair in S and S' | **PASS** — worst 4.7e-08 |

| measured | value |
|---|---|
| `worst_rel` | 4.65e-08 |
| `n_pairs` | 40 |

*Instrument: `tests/frame/c2_weight.py`, sha256 `6e1145194dca…`*

### The bulk source, against the integral it comes from

The exact bulk source is $W(C_0-C_1'+C_2'')-\mathcal{V}C_1+2\mathcal{V}C_2'+\dot{\mathcal{V}}C_2$. Annals II's printed `int_soln_damping` does not reproduce its own integral: $+2\mathcal{V}C_2'$ is printed as $-2\mathcal{V}C_2$, the sign on $\mathcal{V}C_1$ is reversed, and a lower-limit boundary $\mathcal{V}(\eta_*)C_2(\eta_*)$ is absent.

| assertion | verdict |
|---|---|
| C3a  four-term bulk source reproduces the integral | **PASS** — worst 1.9e-11 |
| C3b  Annals II printed int_soln_damping does not reproduce its own integral | **DEFECT PRESENT** — worst relative error 2.6e+00 |

| measured | value |
|---|---|
| `worst_derived` | 1.87e-11 |
| `worst_printed` | 2.55227 |

*Instrument: `tests/frame/c3_byparts.py`, sha256 `2a0bb0f5b24d…`*

### The rank-2 slot forced by frame invariance

Requiring $\Delta\tau_\ell=0$ at $\ell\ge2$ for arbitrary boost potential gives $\beta=-\alpha$ and $\gamma=0$. **The residual floor here is not numerical** — it is the Thomson term, absent from this functional; see C6.

| assertion | verdict |
|---|---|
| C4a  symbolic condition is beta=-alpha, gamma=0 | **PASS** |
| C4b  that choice is >=10x better than either alternative | **PASS** — 8.9e-03 vs 3.2e-01 |

| measured | value |
|---|---|
| `r_beta_minus` | 0.00888329 |
| `r_beta_plus` | 1.01668 |
| `r_gamma_third` | 0.32445 |

*Instrument: `tests/frame/c4_rank_slot.py`, sha256 `6714794d409f…`*

### The monopole row and the dipole shift

$a\,\Delta\mathcal{B}_0=\tfrac13kv=\tfrac13k^2\Delta C_2$ exactly, and $\gamma$ -- which pairs $\Delta C_0$ against $k^2\Delta C_2$ -- vanishes only with $\mathcal{B}_0$ restored. **Both measurements stand and the conclusion drawn from them was wrong.** Finding **T-107**: the partner of $\Delta C_0$ is not in $C_2$ but in $-C_1$′, so $\gamma$ asks the wrong pairing, and the restoration that makes it vanish counts the monopole source twice -- criterion 5b doubles at $98.5\%$. See **C8**, which scores the whole rank-0 content of the bracket instead of one coefficient against another. **M15: a gate built from one coefficient cannot see a cancellation distributed across the bracket.**

| assertion | verdict |
|---|---|
| C5a  a.Delta B_0 cancels (1/3) k^2 Delta C_2 exactly | **PASS** |
| C5b  gamma reports zero for the row c8 REFUTES (M15) | **DEFECT PRESENT** — the pairing is wrong, not the arithmetic |
| C5c  and gamma scores it >=10x better than the correct row | **DEFECT PRESENT** — 8.9e-03 vs 3.2e-01 -- see c8, T-107 |

| measured | value |
|---|---|
| `gamma_printed` | -5/2 |
| `gamma_no_B0` | 1/3 |
| `gamma_restored` | 0 |
| `r_printed` | 2.50888 |
| `r_no_B0` | 0.32445 |
| `r_restored` | 0.00888329 |

*Instrument: `tests/frame/c5_monopole.py`, sha256 `bd1ff2707f09…`*

### The Thomson $v^B_a$ slot

$\kappa'v_B$ **cannot** sit inside $C_1$: the $K'$ coefficient becomes $2\alpha\mathcal{V}$ and no $(\alpha,\beta,\gamma)$ makes the bulk invariant. Carried as its own **undifferentiated** term, invariance requires $c=\alpha$ and the reduced $\hat v_B=v_B/k$; the un-reduced form needs $c=\alpha/k$, which is not a constant. **This is not a weight change**: $W\kappa'=\mathcal{V}$ is an identity, so the Thomson term is already at visibility weight in (102) as printed. What (102) does wrong is **differentiate** it --- $\mathrm d/\mathrm d\eta$ of a coefficient still carrying a bare $\kappa'$ is what manufactures $\kappa'^2$. The remedy is not to move it; it is not to differentiate it.

| assertion | verdict |
|---|---|
| C6a  symbolic: inside C_1 is unsatisfiable; outside needs c=alpha | **PASS** |
| C6b  c=alpha drives the residual to machine zero | **PASS** — 3.2e-13 |
| C6c  c=2alpha does not | **PASS** — 8.9e-03 |

| measured | value |
|---|---|
| `r_grav` | 0.00888329 |
| `r_inside` | 0.0177666 |
| `r_c_alpha` | 3.19e-13 |
| `r_c_2alpha` | 0.00888329 |

*Instrument: `tests/frame/c6_thomson.py`, sha256 `db4b1f479f98…`*

### The $\kappa'$ ledger

Multiplying the transport equation by $W=e^{-\kappa}$ sends the gravitational source to $W$ and the in-scattered Thomson source to $\mathcal V=W\kappa'$, its $\kappa'$ consumed by the integrating factor. **This is a REVIEW FLAG, not a prohibition --- revised 2026-10-21, finding T-113 and decision S48.** It read *``$\kappa'$ may live in $W$, in $\mathcal V$, or in a derivative of either --- never in a coefficient''* and was taken as normative. **It is not a theorem**: $W(\kappa'S)=\mathcal VS$ is exact, so a coefficient may hold $\kappa'$. The defect in (102) is wrong weights, signs, boundaries or missing partners --- which **C3b** measures at $2.6$ --- not the presence of $\kappa'$. The flag is kept because it is cheap and every assembly that failed this month trips it; what it may no longer do is settle a question on its own. Note also that $\kappa''=-\kappa'^2$ holds **at the visibility maximum**, where $\dot{\mathcal V}=0$, so *``three powers of $\kappa'$''* is a local statement and not a general one.

| assertion | verdict |
|---|---|
| C7a  the W-form keeps every kappa-prime in the weight | **PASS** |
| C7b  (102) as printed carries kappa-prime in a coefficient | **DEFECT PRESENT** — differentiating it gives kappa-prime squared |
| C7c  T-88 carries kappa-prime in a coefficient | **DEFECT PRESENT** — measured 320-682x by P1-B |

| measured | value |
|---|---|
| `w_form_clean` | True |
| `printed_102_clean` | False |
| `t88_clean` | False |

*Instrument: `tests/frame/c7_kappa_ledger.py`, sha256 `0159b589ff6a…`*

### The rank-0 partner, and where the monopole source enters

(107) already carries the monopole source: $-C_1'=(\kappa'\hat v_B)'+(a\mathcal{B}_1)'/k$ and $(a\mathcal{B}_1)'/k=(\Phi_A'-\Phi_H')+\tfrac k3\tau_1$, with $\tfrac k3\tau_1=-a\mathcal{B}_0$. So (89)'s $\delta_{\ell0}$ row is **correctly empty** of $\mathcal{B}_0$ and only its normalisation is wrong. With $\alpha_0$ in place of $\alpha_2$, $C_0=-\tfrac13a\mathcal{B}_2$ and its frame shift $+\tfrac13kv$ is cancelled **inside the bracket**, by $\Delta[\tfrac k3\tau_1]$ in $-C_1'$. Restoring $a\mathcal{B}_0$ counts the source twice and leaves the same residual with the opposite sign -- finding T-107, which criterion 5b caught at $98.5\%$ and no frame instrument could.

| assertion | verdict |
|---|---|
| C8a  the printed row leaves a rank-0 shift | **PASS** |
| C8b  alpha_0 with NO B_0 cancels against (k/3)tau_1 in -C_1' | **PASS** |
| C8c  restoring B_0 counts the source twice | **PASS** — residual -1/3 k v, equal and opposite to B's partner |
| C8d  and what it leaves is exactly one more copy of the partner | **PASS** — the restoration adds a source the bracket already held |
| C8e  numerically, only B is at the floor | **PASS** — 0.0e+00 vs 3.3e-01 |

| measured | value |
|---|---|
| `shift_printed` | 13/6 |
| `shift_alpha0_no_B0` | 0 |
| `shift_alpha0_with_B0` | -1/3 |
| `r_printed` | 2.16667 |
| `r_alpha0_no_B0` | 0 |
| `r_alpha0_with_B0` | 0.333333 |

*Instrument: `tests/frame/c8_rank0_partner.py`, sha256 `aa5b11da2b5c…`*

## Provenance

| | |
|---|---|
| generated | 2026-10-22 16:39 UTC |
| python | 3.13.16 |
| numpy | 2.5.3 |
| scipy | 1.18.1 |
| sympy | 1.14.0 |
| generator | `tests/frame/gen_theory_audit.py`, sha256 `0a0dccfce65b…` |

Annals II is read from `sources/annals/cbrII.tex` and referred to by label — `IBE-source`, `modeibe`, `source-calB`, `find_coef`, `C-B-coef`, `int_soln_damping`, `slowdecoupling`, `slowdecoupling-ng-0`. Paper 1 is referred to by label (`eq:B`, `eq:frame-transf`, `eq:raise`), never by printed number: those differ between the two lines.

