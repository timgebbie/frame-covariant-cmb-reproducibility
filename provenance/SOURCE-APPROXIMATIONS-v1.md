# Approximations of the source — deliberate choices, not defects

This file is **not** the findings record. Findings `B-1`–`B-7` in
`ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` are places where *Annals II* says
something that is wrong. This file is for places where it says something that is
*right but narrow*: a deliberate approximation whose range is smaller than the
range this bundle has to cover.

The distinction is load-bearing. A finding gets corrected. An approximation gets
**reproduced faithfully when reproducing the source**, and departed from only
where the source is not the target — with the departure named at the call site
and in the caption.

The record exists because the failure mode is the same in both cases and the
remedy is opposite. Mistaking a narrow choice for an error produces a "correction"
that stops reproducing the paper. That nearly happened here: see A-1.

---

## A-1 — the visibility weighting on the integrated sources, (178) and (179)

**Status: faithful to the source. Both weightings implemented; the caller states
which.** Raised by Coordination, 2026-10-06, correcting this stream.

Equations (178) and (179) weight the integrated sources with the visibility
function $\mathcal V=\kappa'e^{-\kappa}$ (§5.2) rather than with the opacity
$e^{-\kappa}$.

**This is deliberate and the paper says so.** §5 states, of the step from (98) to
(102): *"A similar correction is made using the visibility function in the
integrated part of the solution, in order to best deal with a changing ionization
fraction."* §5.2 is the slow-decoupling solution, a specialisation built to model
a finite, changing ionisation fraction, and the visibility is the appropriate
weight for that question.

**One equation earlier the paper uses both weights and distinguishes them.** (98),
the slow-decoupling solution before the visibility approximation, carries
$e^{-\kappa}$ on the gravitational sources and $\kappa'e^{-\kappa}$ on the
scattering sources, and its own text immediately after reads: *"We see that
damping effects are controlled by $e^{-\kappa}$ and $\kappa'e^{-\kappa}$."* So
both weightings are the antecedent's; neither is imported.

**What it costs, and where.** (179) weighted by $\mathcal V$ is **not** the
standard integrated Sachs–Wolfe term. The standard ISW carries $e^{-\kappa}$ and
accumulates along the whole line of sight; this carries the visibility and
concentrates at last scattering. $\mathcal V$ is a sharp spike there and is zero
to many decimal places by $z\lesssim1$, which is exactly where a late-ISW from
$\Lambda$ accumulates. **So Annals II's expression cannot carry a late-ISW.**

In *Annals II* that costs nothing: §8.3.2's model is standard CDM, flat and
matter dominated, with no $\Lambda$ and therefore no late-ISW to lose. It costs
something **here**, because v1.0.0 must also deliver $\Lambda$CDM, which
*Annals II* does not treat.

**How the bundle handles it.** `functions/spectra/decoupling.py` implements both
as `Weighting.ANNALS_II` ($\mathcal V$) and `Weighting.STANDARD_ISW`
($e^{-\kappa}$), with **no default**. The caller states which question it is
asking:

| computing | weighting | why |
|---|---|---|
| the *Annals II* comparison | `ANNALS_II` | substituting $e^{-\kappa}$ would reproduce something the paper did not write |
| the $\Lambda$CDM spectrum | `STANDARD_ISW` | outside *Annals II*'s scope; needs a late-ISW the visibility cannot carry |

**Consequence for the figures.** If F4 is tested against a standard ISW it will
mismatch, **and that is not a defect in this code** — it is this approximation,
visible. Every figure touching the integrated sources must name its weighting in
the caption. A figure that does not say which it used is not evidence.

**How this nearly went wrong.** This stream first recorded the above as a finding
against the paper — "an approximation applied past its range, with a prose claim
that outruns it" — on the strength of §7.1.1's description of the last term as
modelling "the integrated Sachs–Wolfe (ISW), the late-ISW and early-ISW effects".
That reading skipped the sentence in §5 which states the choice explicitly.
Coordination caught it. Had it stood, the bundle would have silently stopped
reproducing *Annals II* while claiming to, which is worse than the thing it was
trying to fix — and it is the exact inverse of the error the findings record is
designed to catch.

---

## A-2 — the visibility weighting on the **Doppler** source destroys the Sachs–Wolfe plateau

**Status: this bundle uses (98)'s weighting for the integrated terms. Found
2026-10-06 by computing the spectrum; it is not visible in the equations.**

A-1 records that *Annals II* weights the integrated sources with the visibility
$\mathcal V=\kappa'e^{-\kappa}$ by deliberate choice, and that this cannot carry
a late integrated Sachs–Wolfe term. A-2 is the sharper consequence, on the
**Doppler** term of (178) rather than the gravitational term of (179), and it
bites in the standard-CDM case where A-1 costs nothing.

**The arithmetic.** (178) weights $(\kappa'\tilde v_B'+\kappa''\tilde v_B)$ by
$\mathcal V$, giving $\mathcal V\kappa'\sim\kappa'^2e^{-\kappa}$. With
$\kappa'\simeq1.4\times10^4$ at last scattering in these units, the Doppler source
reaches $\sim10^6$ against a primary source of order unity. It swamps everything.

**The consequence, measured.** Computing $C_\ell$ both ways over
$2\le\ell\le200$, standard CDM, normalised to $\ell=2$:

| weighting on the integrated terms | $D_5$ | $D_{10}$ | $D_{20}$ | $D_{50}$ | $D_{100}$ | $D_{200}$ |
|---|---|---|---|---|---|---|
| $\mathcal V$, as (178) prints it | 4.29 | 13.6 | 43.2 | 191 | 537 | 1212 |
| $e^{-\kappa}$, as (98) prints it | 0.80 | 0.74 | 0.87 | 1.60 | 3.28 | 6.93 |

The first is $D_\ell\propto\ell^2$, which is $C_\ell\simeq$ constant — **there is
no Sachs–Wolfe plateau at all**. The second is flat to within 30% over
$2\le\ell\le20$ and then rises into the acoustic region, which is the shape a CMB
spectrum has.

**(98) is the antecedent's own pre-approximation form**, and it prints the two
weights separately and distinguishes them in its own text: the gravitational and
Doppler sources carry $e^{-\kappa}$, and $\kappa'e^{-\kappa}$ appears only on a
third, separate bracket. The visibility substitution enters at (102), described
as a slow-decoupling correction. **So this bundle departs from (178) in favour
of (98), and both are the antecedent's.**

**What is not claimed.** This is *not* recorded as a finding against (178). The
tilde variables of §5 carry factors of $k$ relative to the untilded ones of (98),
and this stream has not derived that mapping in full; it is possible that (178)
is consistent under a reading of $\tilde v_B$ that differs from the
$\tilde v_B=\tilde\tau_1$ used here. What *is* established is narrower and
sufficient: **under this bundle's reading, (178)'s weighting produces no
Sachs–Wolfe plateau and (98)'s does**, and (98) is the earlier and less
approximated of the two. The departure is recorded rather than silent, and the
reading of $\tilde v_B$ is the thing to check if this is ever revisited.

**How it is carried.** `source_doppler` and `source_integrated` both take an
explicit `weight`, defaulting to the visibility so that (178) and (179) can still
be reproduced exactly as printed. `functions.spectra.pipeline` passes the
weighting the caller selected, for both.
