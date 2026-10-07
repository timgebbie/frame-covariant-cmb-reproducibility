# The external codes: what they model, what they do not, and what the comparison can prove

**Criterion 5b compares this bundle against CAMB and CLASS.** This file says what
that comparison establishes and — more importantly — what it structurally cannot.

Every claim in the capability table below is **to be verified against the
installed versions at 5b**, not taken from here. `tests/test_external_codes.py`
records the actual version strings and the actual settings used, so the released
numbers carry their own provenance. This file is the plan; the test is the
evidence.

---

## Why not CMBFAST, which is what *Annals II* would have been checked against

CMBFAST is Seljak & Zaldarriaga, *Ap. J.* **469**, 437 (1996) — already `[SeZalb]`
in *Annals II*'s own bibliography, and already the fourth of this bundle's
external hierarchies via Eq. (3d). It is Fortran 77, unmaintained since the early
2000s, and its distribution sites are gone.

**So CMBFAST is cited for the *method* — line-of-sight integration — and the
comparison is run against its maintained descendants.** Saying that is more
honest than claiming a comparison against a code nobody can run. Decision S4a.

---

## Capability table

| | **CAMB** | **CLASS** | **this bundle, v1.0.0** |
|---|---|---|---|
| Reference | Lewis, Challinor & Lasenby, *Ap. J.* **538**, 473 (2000) | Blas, Lesgourgues & Tram, *JCAP* **07**, 034 (2011) | Gebbie, Dunsby & Ellis, *Ann. Phys.* **282**, 321 (2000) |
| Lineage | descends from CMBFAST | independent reimplementation | independent, from $1+3$ principles |
| Install | `pip install camb` | `pip install classy` | this repository |
| Core language | Fortran 90 + Python | C + Python | Python |
| Method | line of sight | line of sight | line of sight |
| **Perturbation formalism** | **gauge-fixed** (synchronous / Newtonian) | **gauge-fixed** (synchronous / Newtonian) | **$1+3$ covariant and gauge-invariant** |
| Recombination | RECFAST, HyRec, CosmoRec | RECFAST, HyRec | **equilibrium Saha only** — the gap |
| Massive neutrinos | yes | yes | no |
| Spatial curvature | yes | yes | flat only (Appendix K is not implemented) |
| Dark energy beyond $\Lambda$ | $w_0w_a$, PPF | fluid, quintessence | $\Lambda$ only |
| Reionisation | yes | yes | no |
| Lensing of the CMB | yes, with HALOFIT | yes | no |
| Tensors, polarisation | yes | yes | **no** — scalar temperature only |
| $O(\varepsilon^2\ell)$ nonlinear couplings | **no** | **no** | **no at v1.0.0, by design; v1.5.0** |

---

## What the comparison establishes

**That the linear reconstruction is right.** Both codes solve the same linear
physics by the same method from independent implementations, and agree with each
other closely. If this bundle reproduces them over a stated range, the chain from
the $1+3$ hierarchy through (176) to (186) has been checked end to end against
work that does not share its conventions, its formalism, or its author.

That is worth having precisely because the four Appendix F hierarchies check only
the *free-streaming recursion*. Everything after it — recombination, the acoustic
system, the sources, the line-of-sight integral, the $k$-integral — has no
external check until 5b.

## What the comparison cannot establish

**1. It cannot validate v1.5.0.** Neither code carries the $O(\varepsilon^2\ell)$
couplings Paper 1 restores. The comparison is structurally a *linear* check, and
agreement at v1.0.0 says nothing about the nonlinear extension. This is the
reason the staging exists and the reason v1.0.0 must carry no $O(\ell)$ coupling
(decision S9): if one leaked in, v1.0.0 would disagree with CAMB and CLASS and
the disagreement would be indistinguishable from a bug.

**2. It cannot check the covariant content.** Both codes are gauge-fixed. Neither
distinguishes mode coefficients $\tau_\ell$ from multipole coefficients
$\tau_{A_\ell}$ — which is *Annals II*'s own observation, and the reason every
released figure here plots the multipole mean-square. The round trip of
criterion 2 and the frame-specialisation figures have no external analogue and
never will.

**3. It cannot set its own tolerance.** No agreement can be claimed tighter than
two trusted independent codes agree with each other, so **the CAMB–CLASS mutual
difference is the floor** and it is *measured*, not quoted from this file.
Decision S4b.

---

## The canonical comparison

One parameter set, fixed here so that the comparison is reproducible and so that
a later disagreement cannot be explained away by a settings change.

| | value |
|---|---|
| $\Omega_b h^2$ | 0.02237 |
| $\Omega_c h^2$ | 0.1200 |
| $h$ | 0.6736 |
| $n_s$ | 0.9649 |
| $\tau$ (reionisation) | **0** — this bundle has no reionisation; it must be switched off in both codes or the comparison is of different physics |
| $A_s$ | irrelevant: all three spectra are compared in shape, each normalised to its own value at $\ell=30$ |
| lensing | **off** in both codes |
| tensors | off |
| massive neutrinos | **off** in both codes |

Switching reionisation, lensing and massive neutrinos **off** is not a
convenience. Each is physics this bundle does not model, and leaving any of them
on would compare a spectrum that contains it against one that does not, then
attribute the difference to the reconstruction.

### The three bands

The failure modes differ, so one number across all $\ell$ would hide all three.

| band | what dominates | what a disagreement there means |
|---|---|---|
| $2\le\ell<30$ | cosmic variance; the Sachs–Wolfe plateau and the late ISW | the potentials, the growth factor, or the integrated-source weighting |
| $30\le\ell<1000$ | the acoustic peaks | **a hierarchy or recursion error** — this is the band that actually tests the reconstruction |
| $1000\le\ell\le2000$ | the damping tail | recombination and the diffusion scale; fractional differences blow up on a vanishing signal, so this band is reported but not used as a gate |

The middle band is the one that matters. The outer two are reported for
completeness and because a surprise in either is informative, but neither is
where a reconstruction error would first show.

### Expected to fail, today

The damping tail will not pass at present and the reason is known: recombination
is equilibrium Saha, which decouples too sharply and too early. Peebles'
effective three-level atom is required first. Stating that here means the failure
when it comes is a confirmation rather than a surprise.
