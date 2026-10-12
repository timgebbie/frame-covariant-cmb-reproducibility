# v1.1.0 — Peebles recombination, and the frame specialisation made numerical

A compatible scientific extension of v1.0.0. **It recovers nothing and breaks
nothing**: every v1.0.0 acceptance criterion still holds, and the one that could
have moved — 5a, the Sachs–Wolfe limit — is reported below.

`RELEASE-NOTES-v1.0.0.md` remains the record of what v1.0.0 established and is
not superseded by this file.

## What this release adds

**Peebles recombination, and it is now the default** (decision **S22**).
`functions/spectra/peebles.py` implements the effective three-level atom:
case-B recombination, photoionisation by detailed balance, the Peebles
suppression factor $C_r$ and the two-photon $2s\to1s$ channel. Equilibrium Saha
is kept rather than deleted, because it is the v1.0.0 result and so is what
makes the change **measurable** rather than merely asserted (decision S12).

| | freeze-out $x_e$ | visibility peak | FWHM in $z$ |
|---|---|---|---|
| Saha | → 0, unphysically | $z\simeq1300$ | $\simeq120$ |
| **Peebles** | $2.15\times10^{-4}$ | $z\simeq1107$ | $\simeq167$ |
| standard | $\sim2\times10^{-4}$ | 1080–1100 | 190–200 |

Saha placed last scattering roughly 200 too early in redshift and made the
visibility about 40% too narrow. **The visibility width is what fixes the Silk
damping envelope**, which is why acceptance criterion 5b was blocked on this
module and not on the spectrum code (S18).

What is **derived** and what is **imported** is tabulated in the module
docstring, because *derive, do not transcribe* has to stop somewhere and
recombination is where: the ODE structure and $\beta_B$ by detailed balance are
derived; $\alpha_B$'s Pequignot fit, the atomic constants and the RECFAST fudge
factor are imported with their sources. **The fudge is a named parameter**, not
a buried coefficient, and `tests/` measures what it is worth.

**The frame specialisation is a calculation, not a label.**
`functions/spectra/frame_transform.py` solves for the threading shift;
`"newtonian"` and `"energy"` used to be strings nothing read. The energy frame
is **derived** from $\tilde A_a=0$, which gives $v'+\mathcal Hv=-k_{\rm
com}\Phi_A$ — the Euler equation of a pressureless geodesic fluid, as it must
be — and the normalisation is corroborated independently by (152)'s
$R\to\infty$ limit. Numerically $\tilde\Phi_A=0$ and the Weyl invariant
$\Phi_A-\Phi_H$ both hold to $1.1\times10^{-16}$.

**Criterion 2's curvature half is closed, symbolically and with a negative
control.** `functions/frames.py::weyl_invariance_residual` is identically zero,
and a rule that leaves $\Phi_H$ fixed or flips its sign leaves a residual
proportional to $(v'+\mathcal Hv)$ — so the invariance is *forced* rather than
chosen to make a residual vanish. The dipole rule $\tilde\tau_a=\tau_a-v_a$ and
the $\ell\ge2$ invariance are executable rather than asserted.

**Two figures**: **F6**, what each approximation is worth, and **F8**, where each
coupling sits in the hierarchy.

**`scripts/make_release_archive.py`** — finding T-13 closed. It builds the
release asset from the shared file selector with pinned timestamps, then
**extracts it and runs the gates inside it**, so the published file is checked
as a bundle rather than trusted as a file list.

## Acceptance criteria

Unchanged from v1.0.0 — 1, 2, 3, 4, 5a and 6 closed, **5b at v1.2.0** (S18) —
with two strengthenings:

| | What moved |
|---|---|
| **2** | the curvature half now closed as well as the rank-one half, both symbolic, both with the mechanism asserted rather than only the result |
| **5a** | **re-measured under Peebles: 0.26%**, where it was 0.27% under Saha. A shape-normalised large-scale comparison should be insensitive to recombination detail, and it is — which is a small independent check that the default flip broke nothing structural |

## Findings recorded

**T-12** the supplement's margin gate watched only `\hbox`, so vertical overflow
was invisible — repaired before it bit, with the threshold measured at zero.
**T-13** the release archive was built by hand; **closed** by the script above,
which found `dist/` ungitignored on its first run, T-1 for the third time.
**T-14** `sources.py` asserted a frame invariance its equations cannot have:
(177)–(179) are Newtonian-threading expressions, so transforming the inputs and
re-evaluating them moves the total by a factor of five. **T-15** `--strict`
regenerates every artefact then hashes it, so the release route can only pass on
the machine that produced the bytes — three CSVs differ in their last digits
across platforms, not only the renderings. **T-16** F3's convergence alarm
reported a proxy without range or magnitude; the measured sensitivity over the
claimed range is $5.0\times10^{-3}$, and the 24% that the first corrected
measurement reported came from multipoles the figure tells readers not to trust.

**Decisions**: **S20** deferred F5 and F7 and gave a wrong reason for it;
**S21** corrected the reason to T-14; **S22** made Peebles the default;
**S23** moved the generic-$u^a$ hierarchy into v1.2.0, taking F2, F5 and F7
with it.

## What this release still does not do

No acoustic peaks, no Silk damping envelope, no comparison against CAMB or
CLASS. **F2, F5 and F7 wait on the generic-$u^a$ hierarchy**, not on figure work
(S23). `--strict` is not yet runnable on a second machine (T-15). All four land
at v1.2.0.
