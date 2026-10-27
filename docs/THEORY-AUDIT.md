# Theory audit — frame covariance of the source assembly

> **Generated, not transcribed. Do not edit by hand.**
>
> Produced by `tests/frame/gen_theory_audit.py` at 2026-10-27 06:44 UTC. Every number below is read from the machine-readable record of the instrument named beside it. To change this document, change the instrument.

**Status: ALL CHECKS PASS** — 42 assertions across 11 instruments.

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

The exact bulk source is $W(C_0-C_1'+C_2'')-\mathcal{V}C_1+2\mathcal{V}C_2'+\dot{\mathcal{V}}C_2$. Annals II's printed `int_soln_damping` does not reproduce its own integral: $+2\mathcal{V}C_2'$ is printed as $-2\mathcal{V}C_2$, the sign on $\mathcal{V}C_1$ is reversed, and a lower-limit boundary $\mathcal{V}(\eta_\ast)C_2(\eta_\ast)$ is absent.

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

$a\Delta\mathcal{B}_0=\tfrac13kv=\tfrac13k^2\Delta C_2$ exactly, and $\gamma$ -- which pairs $\Delta C_0$ against $k^2\Delta C_2$ -- vanishes only with $\mathcal{B}_0$ restored. **Both measurements stand and the conclusion drawn from them was wrong.** Finding **T-107**: the partner of $\Delta C_0$ is not in $C_2$ but in $-C_1$′, so $\gamma$ asks the wrong pairing, and the restoration that makes it vanish counts the monopole source twice -- criterion 5b doubles at $98.5$%. See **C8**, which scores the whole rank-0 content of the bracket instead of one coefficient against another. **M15: a gate built from one coefficient cannot see a cancellation distributed across the bracket.**

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

*Instrument: `tests/frame/c5_monopole.py`, sha256 `8ea8d6c44ba8…`*

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

Multiplying the transport equation by $W=e^{-\kappa}$ sends the gravitational source to $W$ and the in-scattered Thomson source to $\mathcal V=W\kappa'$, its $\kappa'$ consumed by the integrating factor. **$\kappa'$ may live in $W$, in $\mathcal V$, or in a derivative of either --- never in a coefficient.** A coefficient carrying a bare $\kappa'$ manufactures $\kappa'^2$ the moment it is differentiated, which is what (102) does and what T-88 did. This separates the *legitimate* $\kappa'^2$ inside $\dot{\mathcal V}=(\kappa''+\kappa'^2)W$, from differentiating the **weight**, from the illegitimate one, from differentiating a **coefficient** --- both look identical in the output.

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

*Instrument: `tests/frame/c7_kappa_ledger.py`, sha256 `86711e106e83…`*

### The rank-0 partner, and where the monopole source enters

(107) already carries the monopole source: $-C_1'=(\kappa'\hat v_B)'+(a\mathcal{B}_1)'/k$ and $(a\mathcal{B}_1)'/k=(\Phi_A'-\Phi_H')+\tfrac k3\tau_1$, with $\tfrac k3\tau_1=-a\mathcal{B}_0$. So (89)'s $\delta_{\ell0}$ row is **correctly empty** of $\mathcal{B}_0$ and only its normalisation is wrong. With $\alpha_0$ in place of $\alpha_2$, $C_0=-\tfrac13a\mathcal{B}_2$ and its frame shift $+\tfrac13kv$ is cancelled **inside the bracket**, by $\Delta[\tfrac k3\tau_1]$ in $-C_1'$. Restoring $a\mathcal{B}_0$ counts the source twice and leaves the same residual with the opposite sign -- finding T-107, which criterion 5b caught at $98.5$% and no frame instrument could. **Addendum 2026-10-26.** Finding T-148 scored $C_0$ against $\tfrac k3\tau_1$ and found they do not cancel; both halves of that measurement are right and the pairing is not this one. What cancels is $\Delta C_0+\Delta[\tfrac k3\tau_1]$, two **shifts**, exactly and for any $\tau_1$ whatever, because only the boost law $\Delta\tau_1=-v$ enters. $C_0$ is the rank-2 source leaking into $\ell=0$ through $j_0''(0)=-\tfrac13$; $\tfrac k3\tau_1$ is the rank-0 source itself. A leakage term and a source term have no reason to cancel in value, and $\tau_1\to+0.18v$ at superhorizon scales is a fact about the dipole, not a failure of this cancellation.

| assertion | verdict |
|---|---|
| C8a  the printed row leaves a rank-0 shift | **PASS** |
| C8b  alpha_0 with NO B_0 cancels against (k/3)tau_1 in -C_1' | **PASS** |
| C8c  restoring B_0 counts the source twice | **PASS** — residual -1/3 k v, equal and opposite to B's partner |
| C8d  and what it leaves is exactly one more copy of the partner | **PASS** — the restoration adds a source the bracket already held |
| C8e  numerically, only B is at the floor | **PASS** — 0.0e+00 vs 3.3e-01 |
| C8f  the shift cancellation is independent of the values | **PASS** — holds for any a.B_2 and any tau_1: only the boost law enters |
| C8g  the VALUE pairing does not vanish, and is not required to | **PASS** — C_0 is the rank-2 leakage at ell=0, (k/3)tau_1 is the rank-0 source; T-148 scored a shift against a value |

| measured | value |
|---|---|
| `shift_printed` | 13/6 |
| `shift_alpha0_no_B0` | 0 |
| `shift_alpha0_with_B0` | -1/3 |
| `r_printed` | 2.16667 |
| `r_alpha0_no_B0` | 0 |
| `r_alpha0_with_B0` | 0.333333 |
| `shift_pairing_free_of_values` | 0 |
| `value_pairing` | -aB2_value/3 + k*tau1_value/3 |
| `t148_tau1_over_v` | 0.176076 |

*Instrument: `tests/frame/c8_rank0_partner.py`, sha256 `86d21d691502…`*

### The admissibility of the by-parts, and what (102) replaces it with

Equation~(90) bundles the Thomson rate into $C_1$. The bundling is itself a defect --- **C6** measures the frame obstruction it creates --- and this check measures the second consequence, which is what happens when the bundled coefficient is then differentiated. The exact rank-one bulk $-(WC_1)'$ splits into $W'C_1\sim\kappa'^2$ and $WC_1'\sim\kappa''$, whose sum is the total derivative $\mathrm{d}(\mathcal{V}\hat v_B)/\mathrm{d}\eta$ and is therefore bounded --- not because the two cancel pointwise, which they do not. (102) carries $\mathcal{V}C_1'$ in place of $WC_1'$ --- larger by exactly $\kappa'$ --- and drops $W'C_1$ altogether, destroying the cancellation from both sides in one operation; the same operation empties the $j_\ell'$ slot and carries $\kappa'\hat v_B$ into the boundary. The admissibility condition is that a coefficient holding a rate may not be carried through an integration by parts. It may hold one --- **C7**, T-113, S48 --- but it may not be differentiated while it does.

| assertion | verdict |
|---|---|
| C9a  W'C1s and W C1s' sum to the total derivative d(V.vhat_B)/d-eta | **PASS** — worst residual 1.6e-16; largest piece/sum ratio 8.0e+00 -- they do not cancel pointwise |
| C9b  (102) carries V.C1' where the exact form carries W.C1'; the ratio is exactly the scattering rate | **PASS** — worst deviation from r 0.0e+00; peak r 138.5 |
| C9c  (102)'s rank-1 scattering bulk exceeds the exact one by the scattering rate | **DEFECT PRESENT** — worst factor 320.6x |
| C9d  the split by-parts -- gravitational half by-parted, scattering half left at K' -- reproduces the ancestor | **PASS** — worst 1.2e-13 |
| C9e  the split assembly contains no kappa'' term; (102)'s does | **PASS** — split 0.0e+00 vs printed 5.5e-01 |

| measured | value |
|---|---|
| `worst_cancellation_residual` | 1.63e-16 |
| `largest_cancellation_factor` | 8.00046 |
| `worst_rate_ratio_deviation` | 0 |
| `peak_scattering_rate` | 138.462 |
| `worst_bulk_inflation` | 320.592 |
| `worst_split_residual` | 1.22e-13 |
| `split_sensitivity_to_kappa2` | 0 |
| `printed_sensitivity_to_kappa2` | 0.553822 |

*Instrument: `tests/frame/c9_byparts_admissibility.py`, sha256 `91ee416803fe…`*

### The oscillator phase, and the criterion that cannot see it

Eliminating $\tilde\tau_1$ between \emph{Annals~II} (152) and (153) returns $\delta\tilde T''+\frac{R'}{1+R}\delta\tilde T'+k^2c_s^2\delta\tilde T=-\frac{k^2}{3}\Phi_A-\mathcal F$ with $c_s^2=1/[3(1+R)]$ exactly. With $\Phi$ constant the boundary value $(\delta\tilde T+\Phi_A)(\eta_\ast)$ is a pure cosine of amplitude $\Phi/3$ and its phase is zero; with $\Phi$ time-dependent the phase is non-zero. The released acceptance criterion asks that the oscillator track $\cos(kr_s)$ in exact phase, so it accepts the undriven solution and rejects the driven one: the step that should have caught approximation **A-3** certifies its absence. On Einstein--de~Sitter $\Omega_r=0$ and the phase must be exactly zero, which is the control that separates a driving mechanism from a fit.

| assertion | verdict |
|---|---|
| C10a  (152)+(153) give the oscillator with c_s^2 = 1/(3(1+R)) | **PASS** — c_s^2 = 1/(3*(R(eta) + 1)), drag = Derivative(R(eta), eta)/(R(eta) + 1) |
| C10b  constant Phi: the boundary phase is zero at every k | **PASS** — worst |phi| = 4.6e-07 rad |
| C10c  time-dependent Phi: the boundary phase is non-zero at every k | **PASS** — smallest |phi| = 0.0012 pi |
| C10e  control: the undriven amplitude is the analytic Phi/3 | **PASS** — worst deviation 5.4e-11; driven/undriven amplitude -> 2.5000 |
| C10d  a "tracks cos(k r_s) in exact phase" criterion accepts the UNDRIVEN solution and rejects the DRIVEN one | **PASS** — at tolerance 0.001 rad: undriven accepted True, driven rejected True -- so the criterion certifies the absence of driving rather than the presence of the physics |

| measured | value |
|---|---|
| `c_s_squared` | 1/(3*(R(eta) + 1)) |
| `worst_undriven_phase_rad` | 4.62e-07 |
| `worst_undriven_amplitude_error` | 5.39e-11 |
| `smallest_driven_phase_over_pi` | 0.00124023 |
| `driven_over_undriven_amplitude` | 2.49998 |
| `criterion_tolerance_rad` | 0.001 |
| `criterion_accepts_undriven` | True |
| `criterion_rejects_driven` | True |

*Instrument: `tests/frame/c10_oscillator_phase.py`, sha256 `9311ccf27015…`*

### The third term, and the slot that keeps the source out of today

A by-parts taken against the kernel has three terms, not two: $\mathrm d(WCK)/\mathrm d\eta=\mathcal VCK+WC'K+WCK'$, whose integral is a pure boundary term, and both boundaries vanish for $\ell\ge1$ --- at $\eta_0$ because $j_\ell(0)=0$, at $\eta_i$ because $e^{-\kappa}\to0$. So $\int WC'K=-\int\mathcal VCK-\int WCK'$ exactly. The right-hand Sachs--Wolfe term sits at visibility weight and is confined to recombination; the left-hand term is the same coefficient differentiated at weight $e^{-\kappa}\simeq1$ and is supported almost entirely after it. An assembly that keeps $WC'K$ without its $WCK'$ partner therefore replaces a recombination-confined source with one that accumulates to today and carries the Sachs--Wolfe term in with the wrong sign. With $\Phi$ constant this does not go away, because $C_1^{\rm grav}$ still carries the free streaming of $\delta\tilde T$, which is why the Einstein--de~Sitter null is the control that sees it. **C9**'s two-term condition is the special case in which the kernel is held fixed.

| assertion | verdict |
|---|---|
| C11a  the three-term identity closes against its own boundary | **PASS** — worst relative residual 5.4e-08 over 8 rows |
| C11b  the boundary at eta_0 is exactly zero for l >= 1, because j_l(0) = 0 | **PASS** — worst |W C K|(eta_0) = 0.0e+00 |
| C11c  the boundary at eta_i is bounded by the optical depth there and vanishes with it | **PASS** — |W C K|(eta_i) / [e^-kappa(eta_i) max|C K|] = 0.446; e^-kappa(eta_i) = 1.8e-03 on this fixture and far smaller in the bundle |
| C11d  the Sachs-Wolfe term lives inside the visibility | **PASS** — worst late fraction of |V C K| is 5.5e-07 |
| C11e  the differentiated term at weight W lives outside the visibility, and the two terms have disjoint support | **PASS** — late fraction of |W C' K| is 0.750 to 0.987 against 5.5e-07 for |V C K| -- a separation of 1.4e+06 |
| C11f  dropping the K' partner is not a perturbation of the Sachs-Wolfe term it leaves behind | **PASS** — |W C K'| / |V C K| = 2.7 to 1896.4 |
| C11g  with Phi constant the late accumulation is unchanged, so the Einstein-de Sitter null does not exempt it | **PASS** — worst fractional change under Phi -> 7.5 Phi is 1.3e-13 |

| measured | value |
|---|---|
| `eta_star` | 0.035 |
| `late_begins_at_eta` | 0.095 |
| `worst_relative_residual` | 5.36e-08 |
| `worst_upper_boundary` | 0 |
| `worst_lower_boundary_over_bound` | 0.445888 |
| `worst_sachs_wolfe_late_fraction` | 5.49e-07 |
| `min_derivative_late_fraction` | 0.749971 |
| `max_derivative_late_fraction` | 0.987462 |
| `min_dropped_Kprime_over_sachs_wolfe` | 2.74826 |
| `worst_phi_independence` | 1.28e-13 |

*Instrument: `tests/frame/c11_kernel_partner.py`, sha256 `7fc61636bab8…`*

## Provenance

| | |
|---|---|
| generated | 2026-10-27 06:44 UTC |
| python | 3.13.16 |
| numpy | 2.5.3 |
| scipy | 1.18.1 |
| sympy | 1.14.0 |
| generator | `tests/frame/gen_theory_audit.py`, sha256 `e4514b1cb291…` |

Annals II is read from `sources/annals/cbrII.tex` and referred to by label — `IBE-source`, `modeibe`, `source-calB`, `find_coef`, `C-B-coef`, `int_soln_damping`, `slowdecoupling`, `slowdecoupling-ng-0`. Paper 1 is referred to by label (`eq:B`, `eq:frame-transf`, `eq:raise`), never by printed number: those differ between the two lines.

