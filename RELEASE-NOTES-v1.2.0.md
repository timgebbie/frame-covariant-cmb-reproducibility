# v1.2.0 — the full linear spectrum, and the audit of the equations that produce it

The release where the spectrum stops being the almost-Friedmann–Lemaître
analytic skeleton and becomes a spectrum with structure in it: acoustic peaks,
a Silk damping tail, and the complete linear source assembled from *Annals II*'s
own equations.

It is also, by decision **S26**, an **audit** of that linear theory in covariant
$1+3$ — and the audit half is in scope rather than decorative. A reproduction
that only reproduces cannot say whether what it reproduces is right.

## What this release adds

- **F9 — the angular spectrum with the acoustic peaks.** The release's
  deliverable and now this README's lead figure: $D_\ell$ renormalised at
  $\ell=30$ for CDM, ΛCDM and the stamped Planck 2018 set, with CAMB and CLASS
  drawn as context. The former lead, F3, is kept beside it as the before.
- **The integral solution (102) carried with a generic $u^a$** and specialised
  back, with the covariant coefficient assembly (89)/(90) beneath it and the
  generic $\dot{\mathcal B}_A$ relations the antecedent never wrote.
- **The CDM frame as a second frame**, and with it F2, F5, F7 and D6 — the
  truncation cost, the source decomposition by rank, the frame specialisation,
  and the frame-invariance measurement.
- **`PLANCK_MODEL`**, a photon-only radiation era with $\Omega_\gamma h^2$
  **derived** from $T_{\rm CMB}$ rather than quoted, reaching $z_{eq}=5756.0$
  against CAMB's and CLASS's 5756.0 by an independent route.
- **The Bond–Efstathiou transfer function**, per mode, which is what puts the
  oscillation in the spectrum (**T-37**).
- **D8**, criterion 5b's gate, and **the grid register** — see below.

## Acceptance criteria

**All six hold.** Criterion **5b closed here**, and what it is gated against
changed on the way:

| | |
|---|---|
| planned | the CAMB–CLASS mutual difference as the floor — 0.370% across the peaks (**S4b**) |
| measured | this bundle stands at **137%** there, and was never going to meet it: (102) is a slow-decoupling solution with no polarisation hierarchy, no neutrino anisotropic stress and a visibility-weighted line of sight |
| **taken** | **S4c** — gate on the bundle's own pipeline, (102) against (177)–(179), at **$9.5\times10^{-6}$ against $10^{-3}$**, over three backgrounds, $0.3\le k\le600$, $2\le\ell\le600$. CAMB and CLASS run on the reduced set exactly as planned, stamped, and reported alongside as **context** |

**A criterion that can only be failed is not a criterion.** S4b's merit — that a
tolerance is *measured* rather than chosen — survives intact in S4c, which
measures a different and meetable thing: the agreement between *Annals II*'s two
writings of its own integral solution, which the paper recovers symbolically and
nobody had ever evaluated.

The external comparison is **recorded in the bundle, reproducible, and not part
of the bundled testing** (the PI, 2026-10-15): `reference/` carries the stamped
spectra, `scripts/make_reference_spectra.py` regenerates them from the codes,
`scripts/compare_criterion_5b.py` reproduces the measurement from the stamps
with neither code installed, neither script is in the harness, and
`tables/criterion-5b-v1.2.0.tex` is the result the supplement carries.

## What this release ships as a stated limit

**The recombination grid sets the primary source at $\eta_*$ and nothing derives
it** — refining it moves that source by **1.2%**. Finding **T-46**, question
**Q7**, decision **S33**: derived immediately *after* this tag, so the release
closes on the numbers it was measured with.

**Criterion 5b does not bound this and cannot.** Both of its routes are handed
the same recombination history, so a grid shift moves them together and cancels.
$9.5\times10^{-6}$ is the agreement between two assemblies of one source; it is
**not** the accuracy of the spectrum, and the 1.2% is twelve times 5b's gate and
about thirteen hundred times its worst residual. The release notes for v1.0.0
carry both numbers side by side for this reason.

## Two failure classes closed, rather than two more instances fixed

- **Grids.** `n_eta` fixed rather than derived (**T-3**), the $k$ grid guarded by
  a comment rather than by code, and now the recombination grid — three
  instances in eight days. `provenance/GRID-REGISTER-v1.md` lists **all 32**
  discretisations, generated from the AST, and `scripts/make_grid_register.py`
  **fails when the code holds a grid the register does not name**. One row is
  `open` and says so.
- **Stale deferrals.** D3 and D4 were deferred *to v1.1.0*, which shipped
  without them (**T-47**). `run_all.py` now fails on a deferral to an
  already-released version, and both are retargeted to v1.5.0.

## Findings recorded

**T-17 to T-48** and **B-11 to B-14**. The ones that changed a number or a
claim: **T-32** (every v1.2.0 figure drawn on a $k$ grid stopping at the peak of
the shear integrand), **T-37** (the potentials had no $k$ in them), **T-41** and
**T-42** (the Sachs–Wolfe plateau, misdiagnosed twice and settled as
approximation **A-2**), **T-43** (16/15 is *Annals II*'s own corrected
coefficient, not a departure from it), **T-44** (a gate that printed PASS on a
`nan`), **T-45** (the two-route agreement measured on a grid that hid it),
**T-46**, **T-47**, and **T-48** (the register generator shipped CRLF on
Windows — the script written to close one class carrying an instance of
another).

## What this release still does not do

- **No $O(\varepsilon^2\ell)$ couplings.** The shear, acceleration and vorticity
  couplings are products of two first-order quantities and are dropped at linear
  order; they are v1.5.0's subject, where decision **S2** always had them.
  Decision **S23**, which moved them here, is recorded as **falsified by its own
  premise**.
- **No Hu & Sugiyama acoustic cross-check** — deferred to v1.5.0 as **S35**,
  with the reason recorded. What *is* checked against them is the free-streaming
  chain, their Eq. (6), in F1 at $10^{-13}$.
- **No claim to match CAMB or CLASS.** The distance is measured and itemised,
  not minimised.
- **The numeric manifest gate still canonicalises by rounding to a string**,
  which cannot express a tolerance — **T-38** part (1), three designs recorded,
  the PI's choice outstanding.
