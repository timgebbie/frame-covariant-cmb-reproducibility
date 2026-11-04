# v1.3.0 — the frame-invariant line of sight

This release replaces the line of sight. We assemble
$\int W\lbrace C_0K+C_1K'+C_2K''\rbrace$ from Paper 1's linear redshift source
as three slots: Sachs–Wolfe, Doppler and integrated. Each slot is invariant
under a change of frame at every conformal time. The spectrum, F9, and its
formation in time, F10, are drawn from these slots, and the two frames give
one $C_\ell$ to $4\times10^{-14}$. The acoustic oscillator is still undriven:
the even peaks and the peak heights wait for the radiation era (approximation
**A-3**), which is v1.4.0's.

## The line of sight

With $G=C_1^{\rm grav}-C_2'$ the integrand rearranges exactly into

- a Sachs–Wolfe slot, $-\int\mathcal V\thinspace GK$;
- a Doppler slot, $-\int\mathcal V(\hat v_B+C_2)K'$;
- an integrated slot, $\int W(C_0-G')K$;
- an end-point term that reaches only $\ell\le1$.

This is the supplement's `eq:assembly-invariant`, implemented in
`functions/spectra/line_of_sight.py`. No coefficient that carries $\kappa'$ is
differentiated. The photon moments are read only where photons scatter, and in
the Newtonian frame the integrated slot's source is $-(\Phi_A'-\Phi_H')$, the
integrated Sachs–Wolfe term.

The source carries **Paper 1's signs** (eq:B). The rank-one gravitational term
enters with the sign opposite to the Thomson term, and $C_0$ carries
$a\mathcal B_0=-\tfrac k3\tau_1$. The two corrections are one switch,
`coefficients.RANK_ONE_SOURCE = "paper 1"`, because either alone breaks a frame
condition. `two_frame.covariant_coefficient_sets` builds the release's figures
under it. The module default remains `"as built"`, the antecedent (102) path
whose own measurements the supplement still reports.

## Measurements

| claim | instrument | result |
|---|---|---|
| the three frame conditions hold with Paper 1's signs | **D44** | $\le3.3\times10^{-13}$ on Einstein–de Sitter, ΛCDM and Planck; as built, two of the three fail at order one |
| one $C_\ell$ in both frames | **D44**, **F9** | $4.2\times10^{-14}$; $3.5\times10^{-14}$ |
| the slots sum back to the integral they rearrange | **D45** | the difference falls by 4.00 when the $\eta$ step halves, in every band to $k=1500$, both frames: quadrature in the direct integral, while the slots move by at most $6\times10^{-5}$ |
| the late integrated Sachs–Wolfe term | **F10** | on Planck it deposits 22–54% of today's $C_\ell$ at $\ell$ from 2 to 4 after the visibility has closed; every earlier F10, drawn from (102), showed none |

## The spectrum

F9 puts the first maxima at 165.4 (Einstein–de Sitter), 143.8 (ΛCDM) and
188.5 (Planck, $0.71\thinspace\ell_A$), against 206.1 for CAMB and 206.2 for CLASS. The
odd acoustic series is present on Einstein–de Sitter (165, 495) and ΛCDM (150,
450). The even peaks are absent on every background, which is the signature of
an undriven, baryon-loaded oscillator: an even peak stands at about
$(1+6R)^{-2}$ of its odd neighbours. On Planck the third maximum, near
$\ell\simeq700$, is too shallow for the shared prominence rule.

D45 splits the spectrum by slot. Across $\ell$ from 100 to 400 no pair of slots
cancels. On Planck the integrated slot is 1–5% of $C_\ell$ there, and its cross
term with the Sachs–Wolfe slot adds 11–16% in phase, as the early integrated
Sachs–Wolfe effect should. The Doppler and integrated slots move Planck's first
maximum *down*: from 225 (Sachs–Wolfe slot alone) to 210 (with the Doppler
slot) to 195 (with the integrated slot).

## Stated limits

- **No radiation-era potential (A-3).** $\Phi\propto D/a$ is the antecedent's
  matter-era potential, and the monopole starts at the matter-era $-\tfrac23\Phi$.
  This explains more than the missing even peaks. On Planck, at $k\to0$, the
  Sachs–Wolfe source at last scattering is 0.187 against $\Phi/3=0.310$ and the
  integrated slot carries 0.535. The two cancel at $\ell\lesssim30$, where
  $2\thinspace{\rm SW}\times{\rm ISW}$ reaches $-3.1$ of the total, so F9's Planck
  curve dips near $\ell=5$ where a plateau belongs. ΛCDM, without radiation,
  gives $\Phi/3$ to three figures. The supplement registers the v1.4.0 test of
  the wired radiation era before the work begins.
- **The visibility is not the grid derivative of the opacity (T-191).** They
  are interpolated separately onto the line-of-sight grid: $\int\mathcal V\thinspace{\rm
  d}\eta=0.99914$ on Planck against $W(\eta_0)-W(\eta_{\rm start})=1$. The slots
  move by at most $8\times10^{-4}$ when $\mathcal V$ is replaced by $W'$, and no
  frame result moves. The repair, one $\kappa$ on the line-of-sight grid, comes
  with the next regeneration.
- **The integrated slot takes (106), the small-scale form of the derivative.**
  The Sachs–Wolfe slot carries the oscillator's stored solution under
  $\mathcal V$, and its exact derivative is (152)–(153). The integrated slot
  uses (106) under $W$, which departs from the exact derivative by up to
  $1.3\times10^{-2}$ of the transfer on Planck at $k\le100$, and by
  $4\times10^{-4}$ on ΛCDM.
- **No claim to match CAMB or CLASS.** They are drawn as context, and the
  distance is measured, not minimised.

## Also in this release

- **D44**, the assembly scored against its registrations, and **D45**, the
  sum-back, the stored moments and the slots' cross-spectra.
- **F9's legend** sits in the north-east, in one column, above every curve.
  F9 and F10 now draw from the CSV they write, so the release route's replot
  reproduces each figure exactly. Before this, F9's replot weighted the $D_\ell$
  shape twice and read a frame gap of $3.5\times10^{-14}$ as zero.
- `tab:status` reads the first peak as F9 now draws it, and carries a row for
  the assembly.
- The rendered-markdown test skips `.pytest_cache`, so a second run of the
  suite tests the same files as the first.
- The supplement is edition v1.3.33, the edition for this release, and
  carries its own revision history.

## Reproducing

```bash
python scripts/run_all.py --strict     # regenerate, fail on any drift
pytest -q
```

F9 and F10 redraw from their committed CSVs in seconds. Recomputing them is
`python scripts/figure_f9_acoustic_spectrum.py` (about an hour on two cores)
and `python scripts/figure_f10_formation_surface.py` (minutes). D44 and D45
checkpoint per background and print their own instructions.

## The archive

`frame-covariant-cmb-reproducibility-v1.3.0.zip`, built by
`scripts/make_release_archive.py`, which extracts it and runs the portability
and manifest gates inside it. Its SHA-256 is published with the GitHub release.
