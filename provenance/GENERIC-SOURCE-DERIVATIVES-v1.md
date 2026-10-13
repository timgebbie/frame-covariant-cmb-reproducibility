# The generic source derivatives — what (102) needs and *Annals II* never wrote

**Opened 2026-10-13**, on the PI's instruction. *Annals II* derives
$(a\tilde{\mathcal B}_1)'$ in the Newtonian frame at (106) and nothing else:
the generic relations were, in the PI's words, *"a template, it was missing."*
Finding **T-23** is why they cannot be substituted by differentiating the
coefficient arrays. This file is the derivation, built in the open, and it is
the source for the supplement section.

## What is needed and why

(102)'s integrand is $C_0-C_1'+C_2''$ and its boundary terms carry
$C_2'(\eta_*)$. With (90),

$$-C_0\simeq+\tfrac52a\mathcal B_2,\quad
-C_1\simeq\tfrac1k(a\mathcal B_1+\kappa'v_B),\quad
-C_2\simeq\tfrac1{k^2}a\mathcal B_2$$

so the derivatives the solution needs are $(a\mathcal B_1)'$,
$(a\mathcal B_2)'$ and $(a\mathcal B_2)''$, for **arbitrary $u^a$**.

## The sources, verbatim and generic

*Annals II* §4, in the integrated Boltzmann equation
$\dot\tau+e^a\mathcal D_a\tau+\mathcal B\simeq C[x,e]$:

$$\mathcal B=-\tfrac13\mathcal D^a\tau_a+(\mathcal D_a\ln T+A_a)e^a
+\sigma_{ab}e^ae^b$$

Read off by rank, with **no frame choice made**:

| | | vanishes in the background? |
|---|---|---|
| $\mathcal B_0$ | $-\tfrac13\mathcal D^a\tau_a$ | yes — $\tau_a$ does |
| $\mathcal B_1$ | $\mathcal D_a\ln T+A_a$ | yes — both terms do |
| $\mathcal B_2$ | $\sigma_{ab}$ | yes |

All three vanish in FLRW, so all three are gauge-invariant at first order by
**Stewart–Walker** — which is the paper's *"Note that these are CGI with
respect to $u^a$"*, and the PI's recorded reason for treating the $\ell=0$ row
as a constraint.

## Rank 2 — $\dot{\mathcal B}_2$, which *is* in the paper, generically

Appendix G's linearised propagation equations carry it, with no frame choice:

$$\dot\sigma_{\langle ab\rangle}+2H\sigma_{\langle ab\rangle}
-\mathcal D_{\langle a}A_{b\rangle}+E_{\langle ab\rangle}
\simeq\tfrac12\pi_{\langle ab\rangle}$$

$$\boxed{\;\dot{\mathcal B}_2=\dot\sigma_{\langle ab\rangle}
=-2H\sigma_{ab}+\mathcal D_{\langle a}A_{b\rangle}-E_{ab}
+\tfrac12\pi_{ab}\;}$$

**So the rank-two relation was never missing — it was in Appendix G, one
specialisation away from where it was needed.** It couples the shear to the
acceleration, the electric Weyl tensor and the anisotropic stress; the
Newtonian frame sets $\tilde\sigma_{ab}\approx0$ and the whole equation becomes
a constraint on $A_a$, $E_{ab}$ and $\pi_{ab}$ instead of an evolution.

For scalar perturbations in matter domination the paper also gives the
specialised pair

$$\dot\sigma_{ab}+2H\sigma_{ab}+E_{ab}\approx0
\iff(a^2\sigma_{ab})^{\textstyle\cdot}\approx-a^2E_{ab}$$

and **the right-hand form is the one to implement**, for the reason in the next
section.

## The scale-factor rule, which is what T-23 is about

A rank-$n$ PSTF source's natural variable carries $a^n$:

| rank | natural variable | where the paper writes it |
|---|---|---|
| 0 | $\mathcal B_0$ | — |
| 1 | $a\mathcal B_1$ | (106), $(a\tilde{\mathcal B}_1)'$ |
| 2 | $a^2\sigma_{ab}$ | Appendix G, $(a^2\sigma_{ab})^{\textstyle\cdot}$ |

That is why the footnote to (105) carries $\dot{\mathcal B}_1+2H\mathcal B_1$
rather than $\dot{\mathcal B}_1$: the combination is exactly

$$\dot{\mathcal B}_1+2H\mathcal B_1=\frac1{a^2}(a^2\mathcal B_1)^{\textstyle\cdot}$$

so the rank-two object built from a rank-one source, $\mathcal D_{\langle
a}\dot{\mathcal B}_{b\rangle}$, carries the rank-two power. **It is not a
commutator correction bolted on; it is the rank showing up in the measure**,
and it is conventions row **C3.1a** — *the $\ell$ factors of $\mathcal D$ each
carry $1/a$ while the $\ell$ factors of $k_{\rm phys}^{-1}$ each carry an $a$* —
read in the direction nobody had needed.

Under C3.1, C3.2 and C4.2 the mode functions themselves are time-independent at
every rank and $\mathcal D_{\langle a}Q_{b\rangle}=-k_{\rm phys}Q_{ab}$, so
**all** of the $H$'s in these relations come from the $a^n$ and none from the
$Q$'s. That is the statement to implement against, and it is checkable: it
predicts (106)'s $2H$ before (106) is consulted.

## Rank 1 — $\dot{\mathcal B}_1$, assembled from printed equations

The paper never states it, but every ingredient is printed, and two of them are
in a **footnote**.

The footnote to §6's gradient step gives the commutator for a scalar,
$(\mathcal D_af)^{\textstyle\cdot}\simeq\mathcal D_a\dot f-H\mathcal D_af+A_a\dot f$,
and specialises it: with $\dot{\overline{\ln T}}=-H$ in the background,
$A_a\dot{\overline{\ln T}}=-HA_a$ and the two correction terms combine into
$\mathcal B_a$ itself,

$$(\mathcal D_a\ln T)^{\textstyle\cdot}\simeq\mathcal D_a\dot{\ln T}
-H\underbrace{(\mathcal D_a\ln T+A_a)}_{\mathcal B_a}$$

(L009), the spatial gradient of the radiation energy-conservation equation, is
then generic — no frame has been chosen — and its left-hand side is
$\mathcal D_a\mathcal B_0$ by the definition of $\mathcal B_0$:

$$\mathcal D_a\mathcal B_0\simeq(\mathcal D_a\ln T)^{\textstyle\cdot}
+\tfrac13\mathcal D_a\Theta+H\mathcal B_a$$

With $\mathcal B_a=\mathcal D_a\ln T+A_a$, those two give

$$\boxed{\;\dot{\mathcal B}_a\simeq\mathcal D_a\mathcal B_0
-\tfrac13\mathcal D_a\Theta-H\mathcal B_a+\dot A_a\;}$$

**The rank-one source's evolution is sourced by the rank-zero one.** That is not
an accident of this assembly — it is the same coupling the footnote to (105)
shows from the other side, where $\mathcal D_{\langle a}\mathcal D_{b\rangle}
\mathcal B_0$ appears on the right of the Newtonian $\dot{\mathcal B}$ relation.

### The check against (106), and the one convention that decides it

Reduced with $A_a=\Phi_uQ_a$ (Appendix G, source terms) and
$(a\mathcal B_1)'=a^2(\dot{\mathcal B}_1+H\mathcal B_1)$:

$$(a\mathcal B_1)'=\tfrac13k^2\tau_1+\tfrac13ak\Theta+a^2\dot\Phi_u$$

and **the $H\mathcal B_1$ of (L009) cancels the $a'\mathcal B_1$ of the product
rule exactly** — the rank-one scale factor doing what the previous section
predicted it would.

| | $\tau_1$ coefficient |
|---|---|
| this derivation | $\tfrac13k_{\rm com}^2$ |
| **(106) as printed** | $\tfrac13k_{\rm com}^2$ |

**Exact.** And it is exact only because the raising and lowering signs are kept
apart:

| | |
|---|---|
| **C4.1** | $\mathcal D_aQ=-kQ_a$ — rank-**raising**, $-k$ |
| **C4.4** | $\mathcal D^aQ_{aA_\ell}=+\frac{\ell+1}{2\ell+1}k[\cdots]Q_{A_\ell}$ — rank-**lowering**, $+k$ |

$\mathcal D_a\mathcal B_0$ raises and $\mathcal B_0=-\tfrac13\mathcal D^c\tau_c$
lowers, so the chain carries $(-k)(+k)=-k^2$ against the $-\tfrac13$, giving
$+\tfrac13k^2$. **Using one sign for both gives $s^2$ and reconciles with (106)
only at $s=\pm i$** — which is what the first attempt returned, and is how the
error announced itself. The conventions sheet states the distinction in those
words, and this is the second time today it has predicted the answer before the
source was consulted.

### A cleaner route to the same relation, and the background cancellation

(L009) is the spatial gradient of (L001) with the commutator applied, so the
assembly can start one step earlier. **(L001)**, the radiation energy
conservation / $\ell=0$ multipole divergence equation, is

$$(\ln T)^{\textstyle\cdot}+\tfrac13\Theta\simeq-\tfrac13\mathcal D^a\tau_a
=\mathcal B_0$$

Split into background and perturbation — $\ln T=\ln\bar T(t)+\delta\tilde T$
with $(\ln\bar T)^{\textstyle\cdot}=-H$, and $\Theta=3H+\delta\Theta$ — the
background terms cancel identically and what is left is

$$\dot{\delta\tilde T}+\tfrac13\delta\Theta=\mathcal B_0$$

as it must. Taking $\mathcal D_a$ and applying the commutator returns
$\dot{\mathcal B}_a$ above, which is the same relation by a shorter path and
makes clear that **$\Theta$ enters only through its perturbation**.

### Two pieces of the check close exactly

PSTF-projecting the generic relation and specialising with
$\tilde A_a=\mathcal D_a\Phi_A$:

$$\mathcal D_{\langle a}\dot{\mathcal B}_{b\rangle}
=\mathcal D_{\langle a}\mathcal D_{b\rangle}\mathcal B_0
-\tfrac13\mathcal D_{\langle a}\mathcal D_{b\rangle}\delta\Theta
-H\mathcal D_{\langle a}\mathcal D_{b\rangle}\delta\tilde T
+\mathcal D_{\langle a}\mathcal D_{b\rangle}\dot\Phi_A
-2H\mathcal D_{\langle a}\mathcal D_{b\rangle}\Phi_A$$

against the paper's (105):

$$\mathcal D_{\langle a}\dot{\tilde{\mathcal B}}_{b\rangle}
\approx\mathcal D_{\langle a}\mathcal D_{b\rangle}(\dot\Phi_A-\dot\Phi_H)
-2H\mathcal D_{\langle a}\mathcal D_{b\rangle}\Phi_A
-\tfrac13\mathcal D_{\langle a}\mathcal D_{b\rangle}(\mathcal D^c\tilde\tau_c)$$

| | |
|---|---|
| $\mathcal B_0$ term | **exact** — $-\tfrac13\mathcal D^c\tau_c$ *is* $\mathcal B_0$, so the two are the same term written twice |
| $-2H\mathcal D_{\langle a}\mathcal D_{b\rangle}\Phi_A$ | **exact** — and it is assembled from **two** sources, one $H\Phi_A$ from the scalar commutator acting on $\mathcal D_a\Phi_A$ and one from $-H\mathcal B_a$. Neither alone gives it |
| $\dot\Phi_A$ | **exact** |
| $-\tfrac13\delta\Theta-H\delta\tilde T$ vs $-\dot\Phi_H$ | **open** |

So three of four terms close, and the $-2H\Phi_A$ one closes only because both
contributions are present — which is a real check, not a coincidence: a wrong
commutator or a dropped $-H\mathcal B_a$ would have given $-H$ or $-3H$.

### What is not yet checked

**CORRECTION, same session.** The previous revision of this file said the
expansion--potential relation was *"not yet located in the paper"*. **It is in
the paper**, in §`newtg`, which had not been read. Kept rather than rewritten,
because "I could not find it" and "it is not there" are different claims and
this file conflated them for an hour.

§`newtg` supplies three things, all of them generic until the last step:

$$\textbf{(ng-expansion)}\quad
\tfrac13\mathcal D_{\langle a}\tilde{\mathcal D}_{b\rangle}\tilde\Theta
\approx\mathcal D_{\langle a}\mathcal D_{b\rangle}\dot\Phi_H
-H\mathcal D_{\langle a}\mathcal D_{b\rangle}\Phi_A$$

$$\textbf{(tempc)}\quad(\tilde{\mathcal D}_a\ln T)^{\textstyle\cdot}
+H(\tilde{\mathcal D}_a\ln T+\tilde A_a)
\approx-\tfrac13\tilde{\mathcal D}_a\tilde\Theta
-\tfrac13\mathcal D_a(\mathcal D^c\tau_c)$$

and $\tilde A_a\approx\mathcal D_a\Phi_A$ from the shear evolution equation with
$\tilde\sigma_{ab}=0$.

**(tempc) is (L009) in the Newtonian frame and it confirms the assembly term for
term** --- note its $H(\tilde{\mathcal D}_a\ln T+\tilde A_a)$, which is
$H\tilde{\mathcal B}_a$ written out. The derivation above was right to carry it.

### Closing the check

Substituting (ng-expansion) into the generic relation, with
$\tilde A_b=\mathcal D_b\Phi_A$ and the scalar commutator on
$(\mathcal D_b\Phi_A)^{\textstyle\cdot}$:

$$\mathcal D_{\langle a}\dot{\tilde{\mathcal B}}_{b\rangle}
=\mathcal D_{\langle a}\mathcal D_{b\rangle}\mathcal B_0
+\mathcal D_{\langle a}\mathcal D_{b\rangle}(\dot\Phi_A-\dot\Phi_H)
-2H\mathcal D_{\langle a}\mathcal D_{b\rangle}\Phi_A
\;\underbrace{-\,H\mathcal D_{\langle a}\tilde{\mathcal D}_{b\rangle}\ln T}_{\textstyle(\star)}$$

against (105) as printed:

$$\mathcal D_{\langle a}\dot{\tilde{\mathcal B}}_{b\rangle}
\approx\mathcal D_{\langle a}\mathcal D_{b\rangle}(\dot\Phi_A-\dot\Phi_H)
-2H\mathcal D_{\langle a}\mathcal D_{b\rangle}\Phi_A
+\mathcal D_{\langle a}\mathcal D_{b\rangle}\mathcal B_0$$

**Every term matches, and the generic assembly carries one more: $(\star)$.**
Derived twice by two routes --- through (L009) and through §`newtg`'s own scalar
monopole equation --- with the same result.

### What $(\star)$ is, and the question it raises

$-H\mathcal D_{\langle a}\tilde{\mathcal D}_{b\rangle}\ln T$ is the
temperature-gradient half of $-H\tilde{\mathcal B}_a$; its acceleration half is
one of the two $H\Phi_A$'s that **do** survive into (105). So (105) keeps one
half of $H\tilde{\mathcal B}_a$ and drops the other.

Two readings, and this stream is not choosing between them here:

- **The small-scale approximation.** §6 states *"we drop all terms of
  $O(\epsilon\epsilon_H)$"* --- first order times $H$ --- and $(\star)$ is
  exactly that shape. But so is $-2H\mathcal D_{\langle a}\mathcal
  D_{b\rangle}\Phi_A$, which is kept, so the approximation does not by itself
  explain which survives.
- **An omission**, in which case (105), (106) and every equation descending from
  them are short a term of the same order as ones they keep.

**It is first order and it does not obviously vanish**, which is enough to say
the question is real. Settling it needs the $O(\epsilon\epsilon_H)$ bookkeeping
of §2.5 read against each term of (105) --- not a guess about which is
negligible, after this week. **Logged as an open item against B-class, not yet
filed as a finding.**

What is not in question: the generic relation stands, it reproduces every term
(105) prints, and the discrepancy is in the direction of the generic form
carrying *more*, which is what a specialisation-free assembly should do.

(106)'s $-a^2H\tilde{\mathcal B}_1$ is separately accounted: it is the
conversion between the footnote's $a^2(\dot{\mathcal B}_1+2H\mathcal B_1)$ and
$(a\mathcal B_1)'=a^2(\dot{\mathcal B}_1+H\mathcal B_1)$. Bookkeeping, not
physics, and the previous section predicts it.

## Rank 0 — **not needed by (102)**, and the plan was wrong to say otherwise

A correction to this file's own plan. (102) needs $C_0$, $C_1$, $C_1'$, $C_2$,
$C_2'$ and $C_2''$, and by (90)

$$C_0\propto a\mathcal B_2,\qquad C_1\propto\tfrac1k(a\mathcal B_1+\kappa'v_B),
\qquad C_2\propto a\mathcal B_2$$

**$C_0$ carries $\mathcal B_2$, not $\mathcal B_0$, and it enters the integrand
undifferentiated.** So $\dot{\mathcal B}_0$ is not required for the integral
solution at all. $\mathcal B_0$ enters only through the
$a\mathcal B_0\delta_{\ell0}$ term that §4 writes and (89) drops — the open
item above — and through $\mathcal D_a\mathcal B_0$ inside the rank-one
relation, where it appears as a value and not a derivative.

What (102) actually needs is **rank 2 to second order**, which the previous
plan did not say.

## Rank 2 to second order — closed, with a control that passes

Differentiating Appendix G's shear equation and substituting its $\dot E_{ab}$
equation, with $E_{ab}$ eliminated through the first:

$$\ddot\sigma=-5H\dot\sigma+\left[\tfrac12(\rho+p)-2\dot H-6H^2\right]\sigma
+3H\Lambda+\dot\Lambda+2H\pi+\dot\pi-\mathrm{curl}\,H
+\tfrac12\mathcal D_{\langle a}q_{b\rangle}$$

with $\Lambda\equiv\mathcal D_{\langle a}A_{b\rangle}$. **Generic — no frame,
no matter model, no scalar restriction.**

### The control, which this file previously said did not exist

The paper prints the scalar matter-dominated second derivative directly:

$$(a^2\sigma_{ab})^{\ddot{}}+H(a^2\sigma_{ab})^{\dot{}}
\approx+\tfrac12a^2\rho_{\!_M}\sigma_{ab}$$

Reducing the generic result with $A_a\approx0$, $\pi_{ab}=0$, $q_a=0$,
$\mathrm{curl}\,H=0$, $p=0$ and solving the printed equation for
$\ddot\sigma$, the two are **term for term identical and their difference is
identically zero** — before the Friedmann relation is even needed. Checked
symbolically.

**So rank 2 has a control and it passes.** An earlier revision of this file said
*"nothing checks rank 0 or rank 2"*; that was wrong, and is corrected here
rather than deleted. The rank-2 control is in fact the cleaner of the two — it
is an exact identity, where rank 1's leaves the open term $(\star)$.

### What the two controls now establish

| | control | result |
|---|---|---|
| rank 1, $(a\mathcal B_1)'$ | (105)/(106) | every printed term reproduced; generic form carries one extra, $(\star)$ |
| rank 2, $\ddot\sigma$ | the printed $(a^2\sigma)^{\ddot{}}$ pair | **exact, difference identically zero** |
| rank 0 | — | **not required by (102)** |

**The derivation is complete for everything (102) needs.**

$\dot{\mathcal B}_0$ needs $\dot\tau_a$, which comes from the hierarchy's own
$\ell=1$ row and so is **internal** — no new physics, but C4.4's rank-lowering
has to be carried correctly, which rank 1 has just shown is where this goes
wrong if it is not.

**Superseded:** this paragraph said the paper provides no control for rank 2.
It provides one — the printed $(a^2\sigma)^{\ddot{}}$ pair — and the generic
result passes it exactly. Kept because the order it argued for was still the
right one: rank 1 first, since its control is the one that turned out to have
something in it.

## A loose thread in (89), independent of B-11

*Annals II* writes its own source as

$$\mathcal S_B=-\left[a\mathcal B_0\delta_{\ell0}
+(a\mathcal B_1+\kappa'v_B)\delta_{\ell1}+a\mathcal B_2\delta_{\ell2}\right]$$

**with the $a\mathcal B_0\delta_{\ell0}$ term present**, and says beneath it that
$\tau_0=0$ is a solution *"consistent with the definitions we introduced above
($\mathcal B_0$ cancels the dipole term on the right in this case)"*. Two pages
later, (89) matches the coefficients against a right-hand side **with that term
dropped**. The thesis does the same thing in the same order.

That is checkable and it checks: at $\ell=0$ the free-streaming bracket leaves
$\tfrac13k\tau_1$, so $\tau_0\equiv0$ solves the row exactly when
$a\mathcal B_0=-\tfrac13k\tau_1$, which is $\mathcal B_0=-\tfrac13\mathcal
D^a\tau_a$ in mode form. **$\mathcal B_0$ is the no-monopole statement**, not an
independent source.

Whether dropping it from (89) is therefore correct — the row having already been
used — or whether (89) should carry it, is **open**, and is the same question as
the $\tau^{(0)}_\ell$ normalisation left open against B-11. It does not affect
B-11's resolution: the sign flip on $j_0''(0)$ reproduces all three of (90)
either way, because $\mathcal B_0$ enters $C_0$ additively and $\mathcal B_2$
multiplicatively.

## Status

Rank 2 **closed**, from Appendix G. The scale-factor rule **stated and
checkable**. Rank 1 **assembled, three of four terms verified against (105)/(106)** —
$\mathcal B_0$, $\dot\Phi_A$ and $-2H\Phi_A$ close exactly, the last of them
only because both of its contributions are present. The expansion--potential relation **is** in §`newtg`
(ng-expansion); substituting it reproduces every term (105) prints and leaves
the generic form carrying **one extra**, $-H\mathcal D_{\langle
a}\tilde{\mathcal D}_{b\rangle}\ln T$, whose status --- small-scale
approximation or omission --- is open. Rank 2 **closed to second
order, with an exact control**. Rank 0 **not required by (102)** — $C_0$ carries
$\mathcal B_2$. **The derivation is complete for what the integral solution
needs**; what remains open is $(\star)$ and the dropped
$a\mathcal B_0\delta_{\ell0}$, both of which are questions about the
antecedent rather than gaps in this assembly.
Nothing here is implemented yet; `functions/spectra/integral_solution.py` takes
the derivatives as inputs precisely so that this file can be finished before
anything depends on it.
