# Theory audit — frame covariance of the source assembly

> **Generated, not transcribed. Do not edit by hand.**
>
> Produced by `tests/frame/gen_theory_audit.py` at 2026-10-20 11:39 UTC. Every number below is read from the machine-readable record of the instrument named beside it. To change this document, change the instrument.

**Status: ALL CHECKS PASS** — 15 assertions across 6 instruments.

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

*Instrument: `tests/frame/c1_identity.py`, sha256 `f8479bace9bc…`*

### The rank-2 weight

The rank-2 sector enters at $k^{-2}$, and the boundary pair left by two integrations by parts is in $S$ and $S'$ — **never** $S''$.

| assertion | verdict |
|---|---|
| C2   k^-2 weight, boundary pair in S and S' | **PASS** — worst 4.7e-08 |

| measured | value |
|---|---|
| `worst_rel` | 4.65e-08 |
| `n_pairs` | 40 |

*Instrument: `tests/frame/c2_weight.py`, sha256 `d23ffb63e6eb…`*

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

*Instrument: `tests/frame/c3_byparts.py`, sha256 `32622838de38…`*

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

*Instrument: `tests/frame/c4_rank_slot.py`, sha256 `cb99cc6050d9…`*

### The monopole row and the dipole shift

$a\,\Delta\mathcal{B}_0=\tfrac13kv=\tfrac13k^2\Delta C_2$ exactly, so $\gamma=0$ closes **only with $\mathcal{B}_0$ restored** to the $\ell=0$ matching row. The monopole row is the only place GDE99 (37)'s dipole shift enters the integral solution. **This check cannot see an additive boost-invariant piece in $C_0$** — $\Delta C_0=0$ fixes normalisation, not content.

| assertion | verdict |
|---|---|
| C5a  a.Delta B_0 cancels (1/3) k^2 Delta C_2 exactly | **PASS** |
| C5b  only the restored row gives gamma = 0 | **PASS** |
| C5c  and it is >=10x better than either alternative | **PASS** — 8.9e-03 vs 3.2e-01 |

| measured | value |
|---|---|
| `gamma_printed` | -5/2 |
| `gamma_no_B0` | 1/3 |
| `gamma_restored` | 0 |
| `r_printed` | 2.50888 |
| `r_no_B0` | 0.32445 |
| `r_restored` | 0.00888329 |

*Instrument: `tests/frame/c5_monopole.py`, sha256 `61619282338d…`*

### The Thomson $v^B_a$ slot

$\kappa'v_B$ **cannot** sit inside $C_1$: the $K'$ coefficient becomes $2\alpha\mathcal{V}$ and no $(\alpha,\beta,\gamma)$ makes the bulk invariant. Carried separately under $\mathcal{V}$, invariance requires $c=\alpha$ and the reduced $\hat v_B=v_B/k$; the un-reduced form needs $c=\alpha/k$, which is not a constant.

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

*Instrument: `tests/frame/c6_thomson.py`, sha256 `4c5fcbe50c2c…`*

## Provenance

| | |
|---|---|
| generated | 2026-10-20 11:39 UTC |
| python | 3.13.16 |
| numpy | 2.5.3 |
| scipy | 1.18.1 |
| sympy | 1.14.0 |
| generator | `tests/frame/gen_theory_audit.py`, sha256 `167bf19347bf…` |

Annals II is read from `sources/annals/cbrII.tex` and referred to by label — `IBE-source`, `modeibe`, `source-calB`, `find_coef`, `C-B-coef`, `int_soln_damping`, `slowdecoupling`, `slowdecoupling-ng-0`. Paper 1 is referred to by label (`eq:B`, `eq:frame-transf`, `eq:raise`), never by printed number: those differ between the two lines.

