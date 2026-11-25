# Changelog

All notable changes to this bundle are recorded here. The version policy is in
`README.md` under *Version-control policy*.

## [Unreleased] — v1.5.0 in preparation

### Corrected in the v1.4.0 record

- **D42's summary** read the frames as agreeing to $2.5\times10^{-13}$, the
  value before the one photon density (T-201); its frame control on the
  release tree reads $3.3\times10^{-13}$, and the summary now quotes it. Every
  other number in the report reproduces bit for bit. The v1.4.0 entry below
  carries the earlier value.
- **D45's sum-back** falls by 4.00 in every band and both frames. The v1.4.0
  entry's "4.00 to 4.01" took its 4.01 from the five-against-three row, a
  different comparison.
- **The F5 record's readings are chosen by its table** (T-205).
  `provenance/FRAME-INVARIANCE-MEASUREMENT-v1.md` measures (102) in two frames
  with the coefficients as built, and its median disagreement is of order one
  at every $k$ (1.00 to 1.84). Its fixed sentences said the median fell
  "roughly like $1/k$", from 1.00e+00 at $k=1$ to 1.00e+00 at $k=1$, and
  printed an empty set of $k$ as a sentence. The record now says that (102) as
  built is not frame-invariant at any $k$ measured and points to D44's three
  conditions; `tests/test_frame_invariance_reading.py` holds a falling median,
  one of order one and the empty sets to their readings.

### Changed

- `make_release_archive.py` takes its members in the bundle's one file order,
  POSIX parts (T-200), as the manifests do. For v1.4.0's 342 files the two
  orders agree, so that archive is unchanged.

## [1.4.0] — 2026-11-25

Tag `v1.4.0` on `50c8e2c`. Archive `frame-covariant-cmb-reproducibility-v1.4.0.zip`, 342 files, SHA-256
`7d97dcb836f12db32339556e1775e7838f47f79d116e1cd332dc853ae5a8d8d1`.

### The release regeneration: the hand-over's sign, one photon density, and every artefact re-stamped

- **The hand-over carries (F.1) with its own sign** (T-195, repaired). The
  pair's multipoles are $(-1)^{\ell+1}$ times (F.1)'s, the overall sign fixed
  by *Annals I*'s harmonics (supplement, `sec:a3-construction`), so
  `_continue_by_free_streaming` turns the monopole in and out and passes the
  dipole as it stands. Ranks 0 and 1 come back bit for bit; a quadrupole read
  from the continuation now has (F.1)'s sign. `radiation_era.py` states
  $(-1)^{\ell+1}$ and names the 1+3 derivation of the species, Ma &
  Bertschinger the comparator.
- **One photon density** (T-201). The oscillator's loading $R$ read the rounded
  $\omega_\gamma=2.47\times10^{-5}$ while the background derives
  $2.47298\times10^{-5}$ from $T_0=2.7255$ K; it reads the background's now,
  and $R$ falls by 0.12%. On Planck the first maximum stays at 205.5 and the
  maxima and the first minimum at 210, 480, 720 and 360; the heights relative
  to CAMB move from $+6.42$, $-1.41$, $+4.48$% to $+6.37$, $-1.35$, $+4.50$%,
  the rms over $30\le\ell\le990$ from 6.18 to 6.19% and $\ell=840$ from
  $-14.94$ to $-14.97$%; below $\ell\simeq30$ the curve stays within 1.8%
  (1.76% at $\ell=2$). ΛCDM's first maximum moves from 139.9 to 139.8. F11's
  late shares are unchanged to four places at $\ell=2$ and 90 (0.2059,
  0.1883) and move from 0.0830 to 0.0829 at 210.
- **Every stamped artefact regenerated** on the release tree, F1 to F11 and
  D44 to D46, and every diagnostic `run_all.py` runs, D0 to D42; their
  verdicts are unchanged. D44: the three conditions hold to
  $2.8\times10^{-13}$, the frames to $3.5\times10^{-14}$ in $C_\ell$, and
  Planck's maxima stay at 210, 480, 705 and 990 with the trough at 375
  ($\ell_A=266.7$). D45: the sum-back residual falls by 4.00 to 4.01 with the
  step, and $\int\mathcal V=0.99983$. D46: halving $\eta_i$ moves $D_\ell$ by
  $1.31\times10^{-5}$ of its maximum, the frames agree to $2.1\times10^{-15}$,
  and the energy constraint closes to $3.5\times10^{-10}$. Criterion 5b's gate
  (D8) reads $5.1\times10^{-6}$ against $10^{-3}$. Captions F4, F5, F9, F10 and
  F11 carry the regenerated numbers.
- **The diagnostics' checkpoints are keyed on the code** (T-202): D32 to D35
  had resumed rows of 26 and 27 October into the rerun, because a checkpoint
  resumed any row whose configuration it recognised. A checkpoint now names the
  sources that wrote it and resumes only this tree's rows, with a test that
  another code's row is recomputed; D32 to D35 are recomputed from scratch.
- **The model table is in the harness** (T-204). `make_model_table.py` stood
  outside `run_all.py` from 31 October, so the supplement's table of the three
  backgrounds printed $R(\eta_\ast)$, $r_s$ and $\ell_A$ from older code:
  regenerated, Planck's $R(\eta_\ast)$ is 0.627922 (was 0.628678), $r_s$
  0.0368363 (0.0368321) and $\ell_A$ 266.72 (266.75). The hygiene gate now
  checks the stamps of the table's three renderings as it does the CSVs'.
- **A stale stamp fails the hygiene gate** (T-203). It was listed under the
  PASS banner with exit 0, so from 19 to 25 November a tree on which none of
  the fifteen stamped artefacts was its code's read as passing, to the suite
  and to a clean checkout. A change to `functions/` now lands with the
  regeneration that re-stamps it.
- **B-18 registered**: (153)'s $-H\Phi_A$ is not in the 1+3 equations, since
  (149) drops the lapse term of the expansion gradient; the text is the
  supplement's (v1.4.11), gated by `c15`. `expansion_coupling=False` is the
  1+3 equation, and no released number moves.
- **The release status emits v1.4.0**, which the generator's tuple had left
  out (T-87's class): the radiation era, F9 and F11 at R, and v1.5.0's
  prototypes carry A-5, T-21 and `LCDM_MODEL`'s $\Omega_r$.

### The supplement and the README at the tag (v1.4.8 to v1.4.14)

- **v1.4.8** (`979cdc3`): the radiation era's third step on the record in four
  places, with the registered test's (f) the first maximum and the interior
  minimum and the heights recorded and gated nowhere; the regenerated figures
  read (F5's frames differ by a median of 89%, F2's cost 0.06% and 0.03%); and
  (F.1)'s overall sign fixed by *Annals I*'s harmonics, on which *Annals II*
  puts the pair: its multipoles are $(-1)^{\ell+1}$ times (F.1)'s.
- **v1.4.9** (`4fbcc16`): both documents in release voice. v1.4.0 is the
  radiation era alone; A-5, $k_D$ at the baryon loading (T-21) and
  `LCDM_MODEL`'s $\Omega_r$ move to v1.5.0; the reference runs set
  $N_{\rm eff}=0$, as the bundle does; D42's earlier numbers are cited as at
  `3bb4490` beside the restated instrument; a v1.4.0 subsection joins the
  release history. `2b0963f` restored two attribution tags in the frame
  instruments and added the README's AI-use disclosure; `c83a503` restored the
  current-situation label `bump_release.py` flips.
- **v1.4.10** (`ef1149a`): the claims and evidence tables brought to v1.4.0,
  `tab:status` reading the solved potential with a row for the radiation era
  (D46, `c14`); the figure section re-spliced.
- **v1.4.11** (`ee5c2e2`): the $-H\Phi_A$ of *Annals II*'s (153) is not in the
  1+3 equations, since (149) drops the lapse term of the expansion gradient
  (B-18); `eq:expansion-gradient`, and the fifteenth frame instrument `c15`,
  with two negative controls. The released `expansion_coupling=False` is the
  1+3 equation.
- **v1.4.12** (`13de4f2`): the figure section re-spliced from the regenerated
  captions. **v1.4.13**: the model table it inputs regenerated (T-204).
- **v1.4.14** (`d93fe65`): the release edition. Every number quoted from an
  artefact the regeneration moved is re-read against it, among them the two
  frames on Planck to $8\times10^{-15}$, the $\eta_i$ halving
  $1.3\times10^{-5}$, D44's conditions to $2.8\times10^{-13}$ and criterion
  5b's $5.1\times10^{-6}$ on the release tree; D18's $\kappa'(\eta_\ast)$ and
  D45's halving paragraph are brought to the shipped reports; B-18 enters at
  its sites.

### The sources at the visibility peak, D19 restated, and the suite on Windows

- **D42 reads the released sources in $k$** (T-199): the three frame-invariant
  slots' sources and $C_0$ at $\eta_\ast$, in F9's environment and with Paper
  1's signs, by a fit in acoustic windows (pedestal, amplitude with its slope,
  phase), each series' sound horizon calibrated on known waves of its own
  shape. The Sachs–Wolfe and Doppler sources oscillate through zero at the
  table's sound horizon (0.992, 0.991) and in quadrature to 1.3% of $\pi/2$.
  Against the 3 November environment (`--antecedent`) the radiation era
  multiplies the Sachs–Wolfe wave at $\eta_\ast$ by 8 at $k\sim200$ and 44 at
  $k\sim500$ and lifts it off its pedestal. The frames agree to
  $2.5\times10^{-13}$, and $C_0$ under Paper 1's source is the antecedent's
  bracket $C_0-a\mathcal B_0$ exactly. It had read the antecedent's matching,
  start and potential, with a column that was $C_1$'s Thomson half and a sign
  count that could not see phase. D42 now runs in `run_all.py`.
- **D19 measures the 3 November table** on the live coefficients: $\gamma$ is
  5/2 as printed, 1/3 with $\alpha_0$ alone, and 0 with $a\mathcal B_0$ beside
  it, under the antecedent's matching and under Paper 1's source; $C_1$ and
  $C_2$ do not move with the row, and the ledger is clean. It had asserted 0
  for `"corrected"`, which meant both corrections on 21 October.
- **The suite passes on Windows** (T-198, T-200): the weighting freeze
  compares values at $10^{-7}$ rather than bytes, which the integrators'
  step control makes a fact about the platform; and the bundle's file order is
  POSIX parts on every machine, where `sorted()` on Windows paths had ignored
  case and failed the manifests while naming no file.
- **Corrected:** at step 3 halving $\eta_i$ moved $D_\ell$ by
  $1.5\times10^{-5}$ of its maximum (it is $1.3\times10^{-5}$ on the release
  tree, T-201), and below $\ell\simeq30$ the Planck curve lies within 1.8% of
  CAMB's shape (1.75% at $\ell=2$); these read $1.6\times10^{-5}$ and 1.7%.
- **T-195 amended:** the supplement fixes (F.1)'s overall sign by the
  harmonics, $\tau_0=-\delta T$ with the dipole shared. The control
  continuation hands over $\delta T$ and $-\tau_1$, every rank with the
  opposite sign; it returns only $\delta T$ and $\tau_1$, so nothing computed
  moves. The hand-over is repaired in the release's one change to
  `functions/` (`c8190a2`; see the release regeneration above).

### D44 and D45 on the solved potential, and what one spectrum costs now

- **D44 and D45 read the solved potential** (`potential="solved"`), and D44's
  check (b) compares the integrated source with each mode's own
  $-(\Phi_A'-\Phi_H')$ from `mode_history`, the one place a mode's dynamics
  are computed, where it read the released potential times $T(k)$.
- **D44:** the three conditions hold to $3.0\times10^{-13}$ and (b) to
  $4\times10^{-16}$ on all three backgrounds, and the slots give one $C_\ell$
  in both frames to $3.9\times10^{-14}$. **On Planck the assembly carries the
  series:** maxima of $D_\ell$ by the shared prominence rule at
  $\ell=210$, 480, 705 and 990 with the first trough at 375, the first maximum
  at $0.77\thinspace\ell_A$, where on the released potential it carried a single
  maximum at $0.71\thinspace\ell_A$ and no trough. The integrated slot's
  auto-spectrum is at most 0.38 of $C_\ell$, at the quadrupole.
- **D45:** the sum-back residual falls by 4.00 with the step on ΛCDM and Planck
  in both frames, so it is the direct integral's quadrature; $\int\mathcal V$
  on Planck is 0.99983 against 1 and also falls by four. At the first maximum
  twice the cross-spectrum of the Sachs–Wolfe and integrated slots adds 21% of
  $C_\ell$, in phase; from $\ell=2$ to 10 it is $-0.38$ to $-0.27$. The maxima
  are the same with and without the integrated slot.
- **Compute cost, re-measured on the released path** (README, *Compute cost*):
  `benchmark_single_run.py` times the radiation-era solve, the coefficients and
  the three slots per mode in the CDM frame, where it had timed (102)'s path.
  One spectrum, 4480 modes to $k=1500$ and 39 multipoles to 990, takes 2152 s
  on one core: 479 ms per mode, 77.5% of it the solve and 21.2% the
  projection.

### F11: the formation surface with the radiation era solved, v1.4.0's lead figure

- `scripts/figure_f10_formation_surface.py --radiation-era` draws F10's two
  panels with both slots on the potential solved through the radiation era,
  to $\ell=910$ and $k_{\max}=1500$, F9's. The accumulation checkpoints per
  mode outside the tree (`F10_MODE_CACHE`) and took 54 minutes on one core;
  the $\eta_0$ column is the full integral to $3.4\times10^{-14}$.
- The acoustic series is in place at decoupling, at an eighth of today's
  height. The late integrated Sachs–Wolfe term deposits a positive share at
  every multipole: 21% of $C_2$, 6% at $\ell=16$, 19% at $\ell=90$ where the
  potential is still decaying after decoupling, 8% at the first maximum, and
  under 2% from $\ell\simeq330$. On the released potential (F10) the same
  count is negative from $\ell=2$ to 25: that cancellation was the incomplete
  radiation era's.
- F11 moves from `DEFERRED` to `STAGES` in `run_all.py`, replotted from its
  stamped CSV, and is the README's key figure. `--high-res`, whose outputs
  left the tree with (102), is retired into it.
- `provenance/RELEASE-STATUS-v1.md` regenerates again. F9's status row named a
  test renamed at Stage A, so `make_release_status.py` had refused since then,
  and the notes of the previous change had not reached the generated file.

### The figures regenerated, and every generated CSV names the code that wrote it

- **F2 builds again (T-196).** Its $k$ grid stopped at 1900, and once the
  scattering-rate correction moved $k_D$ to 890.3 its own damping gate needed
  $k_{\max}\ge1910.4$: from before the v1.3.0 tag the generator computed for
  seven minutes and raised. The grid runs to 2000, where
  $e^{-(k_{\max}/k_D)^2}=6.5\times10^{-3}$. F5 and F7 sat on the same grid with
  no gate; they now check it against their environment's own $k_D$.
- **Every generated CSV carries `# sources:` (T-197)**, the digest of
  `functions/` and its generator: F1 to F7 beside F9, F10, D44, D45 and D46, and
  F4 also names the F3 it summed. `check_release_hygiene.py` fails on an
  unstamped generated CSV and lists every stamp the tree no longer computes,
  with a control in `tests/test_release_hygiene.py`.
- **F1 to F7 and F10 regenerated.** F3 to F7 had been drawn in mid-October,
  before the line-of-sight weight, the dipole's normalisation, the scattering
  rate and the source signs were settled, and under the opacity weight on
  (178) and (179); the printed weight has been the default since 19 October
  (A-2). Regenerated:
  - F3: the Doppler source of (178) carries the spectrum. $D_\ell/D_2$ falls to
    $0.25$ (standard CDM) and $0.34$ ($\Lambda$CDM) at $\ell=6$ and to $1.7$
    and $1.3\times10^{-3}$ at $\ell=252$, with no Sachs–Wolfe plateau (A-2,
    T-69). The two routes agree to the last bit;
  - F5: the two frames' totals differ by a median of 89%, worst 99.9% (T-59);
  - F2: $\sigma_{ab}\to0$ costs 0.06% at $\ell=2$ and 34% at $\ell=600$;
  - F6: the small-scale approximation leaves $10^{-9}$ to $10^{-7}$ of
    $C_\ell$ at $\ell\le7$;
  - F7: the dipole stands on each curve at $1.00\times$, and T-31 stands;
  - F10, on the one radiation-era start and the released potential: the late
    term deposits 1 to 15% above $\ell\simeq30$ and cancels 4 to 48% of
    today's $C_\ell$ from $\ell=2$ to 25, 32% at the quadrupole.

  Axes, floors and annotations that had been fixed for the old numbers are
  taken from the data, and the captions, the README and the release status say
  what the figures now show. D44 and D45 are listed stale until they are
  recomputed on the solved potential.

### The radiation era, step 3: the baryons' own term, and the registered test

Step 3 of `sec:a3-construction`, and the test registered on 4 November scored
after it, as registered.

- **The baryons carry their own term in both constraints**
  (`radiation_era.solve_mode`, `baryons="own"`, the default):
  - their weight is $W_b=\tfrac43RW_\gamma$, so (152)'s loading and the
    constraint are one momentum budget;
  - they move with the photon pair until $\eta_*$, $v_b=\tau_1$ and
    $\delta_b'=k\tau_1-3\Phi_H'$, and are released there as dust from the
    pair's velocity;
  - the CDM is carried separately, and the CDM frame is its velocity.

  Step 2's construction stays as `baryons="dust"`, the null control of (g1).
- **The energy constraint closes.** The solve never integrates it, and it now
  holds to $3.5\times10^{-10}$ of its terms at $\eta_*$ at every $k$ and to
  $5\times10^{-11}$ where the photons leave, where step 2 left it open by up
  to 3% (D46).
- **The registered test, scored on F9 and D46:**
  - (e): on Planck the two frames agree to $7\times10^{-15}$ at every
    multipole, and D46's spectrum to $1.5\times10^{-15}$ of its maximum;
  - (f): the first maximum of $D_\ell$ is at 205.5, against $206\pm6$. By the
    shared prominence rule the maxima stand at $\ell=210$, 480 and 720, with
    the first interior minimum at 360, between 300 and 900. CAMB's fall on the
    same multipoles;
  - (g1): unchanged, $2.6\times10^{-11}$; (g2): Einstein–de Sitter and ΛCDM
    are bit-identical to steps 1 and 2.
- **F9 at step 3, Planck:**
  - relative to $\ell=30$ the heights are within 6.4% of CAMB's at the three
    maxima, with an rms difference of 6.2% over $30\le\ell\le990$ and 15% at
    most, at $\ell=840$ in the damping tail;
  - below $\ell\simeq30$ the curve lies within 1.8% of CAMB's shape;
  - the baryons' own term raised the heights by up to 30% from step 2's.
- **Recorded beside the test (D46):**
  - halving $\eta_i$ moves $D_\ell$ by $1.5\times10^{-5}$ of its maximum,
    against the registered $10^{-4}$ ($1.3\times10^{-5}$ on the release tree,
    T-201);
  - the photons' anisotropic stress moves $D_\ell$ by 1.3% of its maximum;
  - $(\Phi_A+\Phi_H)/\Phi_A$ after $\eta_*$ outside the horizon has its
    extremum at $-0.0432$ at $1.63\eta_*$, against $-0.042$ near $1.6\eta_*$
    from the two-fluid potential with decoupling taken instantaneous;
  - the dipole in the constraint tends to the matter era's
    $-(k\eta/3)\Phi_A$, at 1.154, 1.057 and 1.024 times it at 3, 10 and 30
    $\eta_*$;
  - the solved late-time transfer stands within 12% of (J.5) from $k=0.1$ to
    1500, now that the baryons do not cluster before $\eta_*$.
- F9's note in panel (b) sits in the upper left, clear of the Planck curve's
  second and third peaks.

### The radiation era, step 2: the potential solved

Step 2 of `sec:a3-construction`: on a background with radiation, each mode's
potential is integrated with the matter and the photons from the one start,
with the baryons as pressureless matter in the constraint, and that one
$\Phi(k,\eta)$ drives the oscillator and fills the Sachs–Wolfe and integrated
slots. (J.5) is not applied to it.

- **The solve** (`functions/spectra/radiation_era.py`):
  - $\Phi_H$ from the momentum constraint, with the energy constraint as its
    check;
  - the CDM and baryons as dust, $\delta'=kv-3\Phi_H'$ and
    $v'=-\mathcal Hv-k\Phi_A$;
  - the photon pair (152)–(153) until $\eta_*$, then a hierarchy with the
    rank-0 and rank-1 gravitational sources, carried until the photons' term in
    the momentum constraint falls below $10^{-4}$ of the sum;
  - after $\eta_*$, $\Phi_A$ from the photons' anisotropic stress,
    $k^2(\Phi_A+\Phi_H)=-\tfrac85\mathcal H^2\Omega_\gamma\tau_2$.

  It is integrated in $\ln a$ with the background's closed-form
  $\mathcal H(a)$, and normalised so that the matter-era potential at $k\to0$
  is 1, as the released one is ($\Phi_i=\tfrac{10}9$).
- **Wiring.** `two_frame.mode_history` is the one place a mode's potentials,
  photon pair and CDM velocity are computed, and `coefficient_sets` builds both
  frames from it. Use `build_environment(potential="solved")`. The CDM frame
  is the solve's own CDM velocity. Where $\Omega_r=0$ the released potential is
  kept, so those backgrounds cannot move (the restated (g2)). The line of sight
  still reads the photon pair held from $6\eta_*$, as at step 1.
- **The CDM frame carries the photons' stress.** Appendix G's shear equation
  takes $\pi=k^2_{\rm phys}(\Phi_A+\Phi_H)$, which is zero wherever
  $\Phi_H=-\Phi_A$. The frame guard is read against the mode's own scale where
  $v'$ passes through zero.
- **T-194, found and repaired before the solve was released.** The
  leading-order start excites a solution that the momentum constraint carries
  and the energy constraint forbids. It grows as $a$ in the radiation era, and
  it left $\Phi(\eta_*)$ 6% high on Planck at every $\eta_i$. The start now lies
  on both constraints.
- **T-195, found and repaired.** The free-streaming continuation, a control,
  handed over the dipole with its sign reversed. No released figure used it.
- **Scored as registered** (D46, F9):
  - (e): the two frames give one $D_\ell$ to $3.2\times10^{-15}$ of its maximum (D46),
    and F9's worst multipole on Planck agrees to $1.1\times10^{-14}$;
  - (g1): the solve equals $D/a$ to $2.6\times10^{-11}$ on both $\Omega_r=0$
    backgrounds, against Heath's integral at the exact $a(\eta)$;
  - (g2): Einstein–de Sitter and ΛCDM are unchanged, bit for bit;
  - at $k\to0$ on Planck:
    - $\Phi(\eta_*)=0.9253872\thinspace\Phi_i$, Kodama and Sasaki's value to
      $3\times10^{-10}$;
    - the Sachs–Wolfe source is $0.37906\thinspace\Phi_A(\eta_*)$;
    - the radiation era's integrated term is
      $-0.05473\thinspace\Phi_A(\eta_*)$, against the registered $-0.05487$;
      the difference is the photons' free streaming, which the two-fluid
      value does not carry;
  - halving $\eta_i$ moves $D_\ell$ by $4.0\times10^{-7}$ of its maximum, against $10^{-4}$.
- **The energy constraint as step 2's measure of step 3.** With the baryon
  loading removed from (152) it closes to $10^{-10}$ at every $k$. With the
  loading it fails by up to 3% of its terms at $\eta_*$, because the momentum
  the photons give the baryons is not in the constraint, where the baryons move
  with the CDM. That residual is the baryons' own term.
- **The photons' stress.** After $\eta_*$, $(\Phi_A+\Phi_H)/\Phi_A$ reaches
  4.3% outside the horizon. Without it the energy constraint fails at
  $2\times10^{-4}$ to $4\times10^{-4}$; with it the constraint closes. On F9's
  spectrum the stress moves $D_\ell$ by 1.6%, and $D_2$ by $-9.8\times10^{-4}$ of its maximum.
- **F9 at step 2**, on Planck:
  - the first maximum is at 204.6 ($0.767\thinspace\ell_A$), from 188.1,
    against CAMB's 206.1 and CLASS's 206.2;
  - the even peaks appear, a shallow second maximum near 510 and a third near
    690;
  - below $\ell\simeq30$ the curve lies within 1.4% of CAMB's shape, where it
    lay at 0.54 to 0.62 against 0.78;
  - the heights are 15 to 25% below CAMB's between $\ell=60$ and 550.

  Einstein–de Sitter and ΛCDM are bit-identical to step 1. (f) is recorded
  here and scored after step 3, as registered.
- The solved late-time $\Phi(k)/\Phi(k\to0)$ is recorded against (J.5) at the
  shape parameter F9 uses, without a gate. It stands above (J.5): by 24% at
  $k=60$ and 40% at $k=136$. Two things contribute: equality here is at
  $z=5756$, because the radiation is photons alone, and at step 2 the baryons
  cluster with the CDM.

### The radiation era, step 1: one start

The construction is the supplement's `sec:a3-construction`, built in three
registered steps, each scored against the one before. Step 1 is the start
alone, on the released potential.

- **Every mode starts at one $\eta_i$**, deep in the radiation era and
  outside every horizon. On Planck $\eta_i=6.7\times10^{-6}$, where
  $k_{\max}\eta_i=10^{-2}$ binds before $a_i=10^{-3}a_{\rm eq}$ does.
- **The state there is the adiabatic growing mode:** $\delta T=-\tfrac12\Phi_A$
  and $\tau_1=-\tfrac12k\eta_i\Phi_A$, or the matter-era mode where
  $\Omega_r=0$. The code is `acoustic.common_start_eta`,
  `acoustic.adiabatic_growing_mode` and `acoustic_start="radiation era"`, set by
  F9, F10, D44 and D45. The instruments that measure (102) keep the derived
  start.
- **T-192 repaired.** Planck's Sachs–Wolfe source at last scattering, over
  $T(k)$, is smooth across $2.7<k<5.4$: 0.3513, 0.3510, 0.3508, 0.3488, 0.3453
  and 0.3408 at $k=2.6$, 2.7, 2.8, 3.5, 4.5 and 5.5. The derived start jumped
  from 0.185 to 0.296. As $k\to0$ the source is
  $2\Phi_A-\tfrac32\Phi_A(\eta_i)$ under the visibility.
- **T-193, found and repaired.** The derived start set $\tau_1=0$, which is not
  the growing mode. On Einstein–de Sitter it moved $(\delta T+\Phi_A)(\eta_*)$
  by up to 13% at $k=60$; given the growing mode's dipole, the derived start
  agrees with the one start to $1.5\times10^{-3}$.
- **F9 at step 1**, recorded on every background:
  - the first maxima are 159.6, 139.9 and 188.1 ($0.705\thinspace\ell_A$),
    from 165.4, 143.8 and 188.5;
  - the two frames agree to $3.3\times10^{-14}$;
  - on Planck $D_\ell/D_{30}$ for $\ell$ from 4 to 11 is 0.54 to 0.62, where
    it was 0.44 and CAMB holds 0.78.

  The Ω_r = 0 backgrounds move only by the start, as the restated (g2)
  requires; their move is T-193's. F10, D44 and D45 carry the step-1 start
  and are recomputed once, after step 3.
- F9's first-peak annotation sits in the empty upper left of panel (a), off
  CAMB's curve. The comment on `TAU_CONTINUATION` states T-147's measurement
  in place of the reading T-147 refuted.

### Changed

- `scripts/bump_release.py --open` follows the supplement's edition scheme: it
  flips the tree's three labels and opens this section, and no longer copies,
  renames or deletes the supplement, whose editions are declared on the
  README's `Supplement:` line.
- `scripts/bump_release.py` flips the README release-sequence table's status
  cell: `--to` turns the shipped line's row to *released*, and `--open` makes
  the new line's row the one *current* row. `tests/test_readme_artefacts.py`
  checks the cell against the header.
- **`RANK_ONE_SOURCE` defaults to Paper 1's signs.** The two-frame sets take
  no default: `two_frame.coefficient_sets` requires `source`, which is
  `"as built"` for (102) and every instrument that measures it, and
  `"paper 1"` for the frame-invariant line of sight
  (`covariant_coefficient_sets`). `two_route` builds (102) under
  `"as built"`, and `coefficients.rank_one_source` is the one way to choose
  for a block of code. Nothing (102) reports moves.
- **D44 and D45 enter `run_all.py`.** `--report` writes every number the
  report prints to CSVs stamped with the sources. `--replot` rewrites the
  report and the figure from them alone and refuses a stamp this tree did not
  compute (T-54), as F9 and F10 do.
- **D45's stored-moment rows start at each mode's own start** (T-192). Before
  the start the stored moment is held, so the comparison measures (106)
  against the stored moment and not the start rule.
- F9's first-peak marker stops just above the curves, below the legend.
- `make_manifests.py --check` lists a residual file's drift with the
  renderings'. F1's residuals regenerate different digits on every machine by
  design, which keeps them out of the binding manifest; the drift report left
  them out as well and so said they had not moved. That is what the v1.3.0
  release route saw as F1's drift: two renderings and a residual bound, none
  of them release-blocking.
- **The PDF gate reads contents, not clocks.** `check_release_hygiene.py`
  judges each input of the supplement by its git blob at the PDF's last commit
  against its blob now, wherever git can speak for both, and by mtime only for
  an uncommitted file. The commit clock it replaced called a PDF current
  against a branch made before the rebuild and merged after it; a test now
  builds that history and requires the gate to fail on it. The figures the
  supplement draws count among its inputs.
- **A skipped supplement build is counted.** Without `pdflatex`,
  `build_supplement.py` exits 3 instead of 0, and `run_all.py` reports the
  build and its overhang gate as not run: a failure of `--strict`, a reported
  line of `--rerun`.
- **F9 carries the v1.4.0 stamp**, the release that last changed what it
  shows; its files, caption, README links and the supplement's include follow.
  D44 and D45 write their v1.4.0 reports.
- The figure captions are restyled to the supplement's voice: claims are
  stated as the captions' own sentences rather than set in bold, and F6 is
  *The cost of each approximation*.

### Fixed

- **The README described v1.3.0 as unreleased after it shipped.** The
  release-sequence table still marked v1.3.0 current, and the F10 and F9
  sections, their artefact rows and *Where the implementation stands* still
  described the spectra (102) drew before the release. They now describe the
  released figures: one $C_\ell$ in both frames, the odd acoustic peaks
  present and the even ones absent, the late integrated Sachs–Wolfe term
  restored, and the low multipoles and peak heights that wait for the
  radiation era (A-3).
- **T-191: one $\kappa$ on every line-of-sight grid.**
  `RecombinationHistory.weights_on` interpolates $\kappa'$ onto a grid and
  integrates $\kappa$ there, so $W=e^{-\kappa}$ and $\mathcal V=\kappa'W$ are
  one function and its derivative on it. `two_frame`, `pipeline`,
  `two_route` and the handover emission all use it. On Planck the separate
  interpolation left $\int\mathcal V-[W]$ at $-8.6\times10^{-4}$ at every
  step. It now falls by four per halving: $-2.1\times10^{-4}$,
  $-5.4\times10^{-5}$ and $-1.3\times10^{-5}$ at 16 000, 32 000 and 64 000
  points. A grid of 8000 points, which serves every $k_{\max}$ up to about 670,
  is the recombination grid's own and does not move. So F9, D44 and D45 are
  recomputed at v1.4.0, and F10 is not.
- F9's per-background checkpoint kept ten digits, so a background resumed
  from it read the two frames' $10^{-14}$ gap as zero. It keeps every digit
  now. The released F9 was computed without resuming and is unaffected.

### Removed

- The high-resolution F10 of 26 October (two renderings and a CSV). It was
  drawn from (102), which the frame-invariant line of sight replaced, and
  nothing cited it. `--high-res` remains.

### Measured

- **T-192**, `tests/test_the_per_mode_acoustic_start_is_physics.py`. The start
  of each mode is derived from $kr_s$, and on Planck it puts the modes with
  $2.7<k<5.4$ on the matter-era initial condition after their potential has
  decayed: the Sachs–Wolfe source jumps from 0.185 to 0.296 between $k=2.7$
  and $2.8$. This is what (106)'s departure from the stored moment measured,
  not a grid. The test is written to fail when the radiation era repairs the
  start and the initial condition together.
- **D45 at v1.4.0, with one $\kappa$.** On Planck $\int\mathcal V\thinspace{\rm d}\eta$
  is 0.999833 at the released step and 0.999958 at half of it, where
  $W(\eta_0)-W(\eta_{\rm start})=1$: the floor is gone and what remains falls by
  four. Replacing $\mathcal V$ by $W'$ now moves the slots by at most
  $1.5\times10^{-4}$, from $8\times10^{-4}$. The stored $C_1^{\rm grav}$ under
  $\mathcal V$ against (106) integrated from each mode's own start differs by
  $6.7\times10^{-4}$ of the transfer on Planck at $k\le100$; integrated from the
  grid's start it was $1.3\times10^{-2}$, which was T-192.
- **F9 at v1.4.0.** One $\kappa$ moves the spectrum's shape by at most
  $1.2\times10^{-3}$ on Planck and $4\times10^{-4}$ on the other two
  backgrounds. The first maxima stay at 165.4, 143.8 and 188.5, and the two
  frames still agree to $1.3$, $3.5$ and $1.1\times10^{-14}$.

### Planned

- **A-5, the tight-coupling transition**, moves to v1.5.0 (PI, 19 November
  2026): the photon pair carried through the transition, with slip and a
  growing quadrupole, in place of the held moments. It is the precondition of
  second order in the shear, whose coupling enters the oscillator through the
  quadrupole tight coupling suppresses, and its registration comes first.
  With it go $k_D$ at the baryon loading the oscillator runs at (T-21) and
  $\Omega_r$ in `LCDM_MODEL`. v1.4.0 is the radiation era (A-3) alone.
- D3 stays deferred to v1.5.0 (S45). F11, deferred to v1.4.0, is drawn and its
  deferral discharged.

## [1.3.0] — 2026-11-04

Tag `v1.3.0` on `0fd58a9`. Archive `frame-covariant-cmb-reproducibility-v1.3.0.zip`, 331 files, SHA-256
`57b095c81a16c388d3cc4b722000216afa11fed61e02436b19a0e040e8f31db7`.

### Added

- `functions/spectra/line_of_sight.py` — **the line of sight in
  frame-invariant slots**, the supplement's eq:assembly-invariant. With
  $G=C_1^{\rm grav}-C_2'$, $\int W\lbrace C_0K+C_1K'+C_2K''\rbrace$ becomes a Sachs–Wolfe
  slot $-\int\mathcal V GK$, a Doppler slot $-\int\mathcal V(\hat v_B+C_2)K'$
  and an integrated slot $\int W(C_0-G')K$, plus an end-point term that
  touches only $\ell\le1$. Each slot is invariant under a change of frame at
  every $\eta$, no coefficient holding $\kappa'$ is differentiated, and the
  photon moments are read only where photons scatter: in the Newtonian frame
  the integrated slot's source is $-(\Phi_A'-\Phi_H')$. `three_slots` is the
  physics; `slots` keeps the five-term form and the direct integral beside it
  as checks.
- `coefficients.RANK_ONE_SOURCE` — Paper 1's eq:B carries the rank-one
  gravitational source with the sign opposite to the Thomson term, and
  carries $a\mathcal B_0=-\tfrac k3\tau_1$ in $C_0$. The two are one switch
  because either alone breaks a frame condition.
  `two_frame.covariant_coefficient_sets` and `line_of_sight_inputs` build the
  slots' inputs under it; the module default stays `"as built"`, which is the
  antecedent (102) path, until the default is moved.
- **D44** — the assembly with Paper 1's signs, scored as registered on three
  backgrounds. The three frame conditions hold to $3\times10^{-13}$; one
  $C_\ell$ in both frames to $4.2\times10^{-14}$; the odd acoustic series on
  Einstein–de Sitter (165, 495; trough 360) and ΛCDM (150, 450), and one
  maximum on Planck, at $0.71\thinspace\ell_A$.
- **D45** — the slots summed back to the integral they rearrange. Built from
  one set of arrays, the three slots plus the end points against the direct
  quadrature: the difference falls by exactly four when the $\eta$ step
  halves, in every band to $k=1500$ and in both frames, so it is quadrature,
  and it sits in the direct integral; the slots move by at most
  $6\times10^{-5}$ when the step halves. The photon moments stored after last
  scattering move the direct integral by $10^2$ of the transfer and the slots
  by at most $1.3\times10^{-2}$. The slots' cross-spectra put Planck's
  cancellation at $\ell\lesssim30$, between the Sachs–Wolfe and integrated
  slots, and find none across the acoustic band. The one floor the step does
  not move is the visibility against the opacity's derivative, finding
  **T-191**.
- `scripts/figure_f10_formation_surface.py` — **F10**, and it is the release's
  new key figure. The fraction of today's $C_\ell$ already in place at each
  conformal time, six multipoles, three backgrounds, both frames. **Every curve
  is complete at recombination and the late share is 0.0000 everywhere**, where
  $\Lambda$CDM and Planck require $\mathcal O(0.1)$ at $\ell=2$ — the late
  integrated Sachs–Wolfe effect — and Einstein–de Sitter requires exactly zero.
  The EdS null control is what makes it a defect rather than a numerical
  artefact. *That was (102). Drawn with the assembly, the late share is
  restored; see* Changed. Mechanism: **B-17 (i)**, the bulk bracket carried at
  $\mathcal V\mathcal D$ where the by-parts wants $W$. Finding **T-128**.
  **F9 is not deprecated by it** and moves down one section: F9 says *where*
  the power lands in $\ell$, F10 says *when* it was laid down.
- `scripts/diagnostic_d30_formation_surface.py` — **D30**, F10's instrument,
  at twenty-four slices against the figure's sixteen. Two gates: the $\eta_0$
  slice must equal the released quadrature it decomposes (**1.15e-12**), and
  non-monotonicity is reported rather than assumed.
- `captions/F10-formation-surface.md` — F10's caption, which is its
  specification (**V15**), including what the figure does *not* establish.
- `scripts/_fingerprint.py` — one definition of the cached-artefact digest,
  shared by F9 and F10. Finding **T-129**.
- `tests/test_cache_fingerprint_is_path_independent.py` — eight tests holding
  T-129 shut, with the negative control **T-44** requires: the superseded rule
  is reproduced in four lines and shown to be blind to a lazily-imported
  module.
- `functions/spectra/integral_solution.py` gained `eta_slices` and
  `IntegralSolution.partial_bulk` — the bulk accumulated cumulatively in
  $\eta$ **inside the released quadrature**, one pass rather than one spectrum
  per slice, so there is no second definition of the integral to drift.

- `scripts/_versions.py` — the one module that says what version this tree is.
  `CITATION.cff` states the **released** version, `README.md`'s header states
  the **tree** version, and all three supplement filenames derive from them.
  Nine string literals naming the live supplement became zero.
- `scripts/check_release_hygiene.py` — release-blocking gate beside
  portability. Every text file must decode as **UTF-8 with no NUL byte**; the
  supplement's generated artefacts must name **only** the source the build is
  pointed at; and no script but `_versions.py` may spell a supplement filename
  as a string literal. Finding **T-50**.
- `scripts/bump_release.py --open X.Y.Z` — the symmetric half of `--to`. Flips
  the three tree labels and the README's supplement links, opens the changelog
  section, copies the supplement forward with its `\date` and its own `\input`
  repointed, and removes the previous release's build outputs (**S36**).
- `tests/test_release_hygiene.py` — four negative controls that rebuild each
  file that shipped in the v1.2.0 archive and assert the gate refuses it.

- `scripts/diagnostic_d9_acoustic_scale.py` — **D9**, the acoustic scale
  against *Annals II*'s own printed formula ℓ_j = |r_θ/r_s| jπ. Both sides are
  computable in this bundle with no external code, and nothing compared them
  until now. It disagrees by a factor of **2.0–2.8**. Finding **T-51**.
- `tests/test_acoustic_scale.py` — eight tests pinning T-51's measured values,
  **written to fail when the defect is repaired** so the record cannot go out
  of date quietly (**S33** clause (d) applied to a second finding).
- `run_all.py` `DEFERRED` carries T-51's fix targeted at **v1.3.0**, so
  `check_deferrals` refuses a v1.3.0 release that still has it. The T-47
  mechanism used for a *defect* deferral rather than an artefact one.

### Changed

- **F9 and F10 draw the assembly**, with Paper 1's source signs, in place of
  (102). F9's first maxima: Einstein–de Sitter 165.4, ΛCDM 143.8, Planck
  188.5, against CAMB's 206.1 and CLASS's 206.2; the two frames agree to
  $3.5\times10^{-14}$. F10 now shows the late integrated Sachs–Wolfe term
  that (102) could not carry: on Planck it deposits 22–54% of today's
  $C_\ell$ at $\ell=2$–$4$ after the visibility has closed. The even peaks
  are absent on every background, because the oscillator is not yet driven
  by the decaying potentials (A-3, deferred to v1.4.0).
- **The acoustic start is derived per mode from k** — `pipeline.run` takes
  `acoustic_start`, defaulting to `"derived"`: each mode is integrated from the
  η at which k·r_s(η) ≤ 0.1, which is what (180)'s δT(0,k) = −⅔Φ_A(0,k),
  τ₁ = 0 means by *at the big bang*. Peak spacing against *Annals II*'s own
  Δℓ = π r_θ/r_s: **0.995 (EdS), 0.999 (ΛCDM), 0.998 (Planck)**, from 2.95,
  2.85 and 2.11. The C_ℓ spacing for Planck parameters is **284** against
  CAMB's and CLASS's **285.5**, from 589.7. Decision **S40**, finding **T-51**.
  `acoustic_start="z_max"` reproduces the old behaviour exactly and is kept as
  an executable control.
- `potentials` takes `constant_below`, so Φ_A's normalisation comes from one
  reference rather than from the caller's first grid point — grid-independent
  to twelve figures, and the precondition for a per-mode start.
- `acoustic.sound_horizon`'s docstring claimed ∫₀^η and returned ∫_{η₀}^η. It
  now says so, and `sound_horizon_from_zero` is the quantity (180) means.
- New derived quantities: `acoustic_start_eta`, `required_acoustic_points`,
  `matter_domination_eta`. Four new grids registered (41 of 41).

### Found


- **T-51 — the acoustic oscillation starts at z = 3000 and discards half the
  sound horizon.** The PI asked whether the visibility over-damped the acoustic
  peaks; it does not touch them — (177) is a boundary term at η\*, never
  integrated against 𝒱, and k_D carries Silk diffusion alone. The peaks are not
  damped, they are **in the wrong place**: our period is 589.7 in ℓ against
  CAMB's and CLASS's 285.5, and a damping envelope cannot change a period.
  `pipeline.run` hands `solve_acoustic` a grid starting at
  `RecombinationHistory.build`'s `z_max = 3000.0`, which discards 51–64 % of
  r_s(η\*) = ∫₀^η\* c_s dη. Confirmed by construction: starting at z = 2×10⁵
  reproduces CAMB's spacing to 1.6 %. **Q8 is answered** — its ours/CAMB = 0.14
  at ℓ = 720 was our trough compared with CAMB's second peak.
- Criterion 5b could not see it: both its routes take the same
  `solve_acoustic` call on the same truncated grid, and
  `acoustic.sound_horizon` carries the identical truncation independently.
  **S4c vindicated concretely** — the external comparison, demoted from gate to
  context, is the only instrument in the bundle that could detect it.

### Fixed

- **F9's replot did not reproduce F9.** It weighted the $D_\ell$ shape by
  $\ell(\ell+1)$ a second time, which moved the printed first peak from 189 to
  278, and it read a frame gap of $3.5\times10^{-14}$ as zero from a CSV written
  to ten figures. F9 and F10 now draw from the CSV they write, F9's at
  seventeen figures, so the release route's replot is the figure. F9's legend
  sits in the north-east, in one column, above every curve.
- `scripts/bump_release.py` flips the supplement's computational label
  (`computational v1.3.0-dev`), which is where the `\date` line carries it since
  the supplement started numbering its own editions.
- **T-129 — the cached-figure guard digested the code *path*, not the code.**
  `source_fingerprint` hashed every `functions.*` module *present in
  `sys.modules`*, which differs between the compute branch and the `--replot`
  branch: `peebles` is imported lazily, so on the branch that **reads** the
  cache it was not in the digest at all. That is a false-validation hole inside
  T-54's own instrument — a changed recombination history would not have
  invalidated a cached spectrum there. Both callers now digest a declared set
  walked from disk. F9 and F10 are regenerated rather than waived.
- **The README artefact table was not being checked above one digit.**
  `tests/test_readme_artefacts.py`'s row regex read `[FD]\d`, so `**D10**`
  through `**D18**` matched nothing and were silently skipped while
  `test_the_table_is_not_empty`'s `>= 10` floor went on passing on the
  single-digit rows. Fixed to `\d+`, and a second, looser reading of the same
  table is now compared against the strict one — a count threshold cannot
  detect a parser that sees most of a table. That comparison immediately found
  a thirty-ninth row, **D9**, whose evidence cell contains an escaped pipe the
  cell pattern stopped dead at.
- **The README's diagnostic table was twelve diagnostics behind the tree.**
  D19 through D30 — the whole of the current line of investigation — were in
  the repository and not in the public table. Added, and the prose count
  corrected from "nine figures and eighteen diagnostics" to ten and
  twenty-nine.

- Three files entered the v1.2.0 release archive that nothing in the bundle can
  read or rebuild: a **UTF-16LE** `SUPPLEMENTARY-MATERIAL-v1.0.0.tex`, a
  `figures-v1.0.0.tex` byte-identical to its v1.2.0 successor, and a
  `supplement-v1.0.0.pdf` left behind when the build was repointed. All three
  are inert — the harness opens none of them and the archive reproduces — and
  **the v1.2.0 tag is not moved** (**S39**). Removed here. Finding **T-50**.
- `README.md`'s version-suffix paragraph stated one convention where two
  operate, and named v1.1.0 as the current documentation two releases on.
  Figures and tables carry the release they were *introduced* in; the
  supplement carries the release it *belongs to* (**S36**).

### Decisions

- **S36a** — S36 binds from v1.2.0 forward. No v1.0.0 supplement was ever
  frozen, so there is none to restore; the v1.0.0 document of record is the
  release asset at that tag and its archived DOI.
- **S39** — a released tag is never moved, and a patch release is not cut for
  content nothing reproduces against. A release is corrected by a new release,
  never by rewriting an old one.

## [1.2.0] — 2026-10-16

v1.2.0 is **the full linear source and the audit of it** (S26): an extension of
the linear theory in covariant $1+3$, and a check on the antecedent's own
algebra in the sectors its specialisation discards. Criterion **5b** closes
here.

### Added

- `functions/spectra/two_route.py` — the audit made executable. *Annals II*
  writes its integral solution **twice**, as (102) carried with a generic $u^a$
  and as the source assembly (177)–(179) in the Newtonian frame, and recovers
  the second from the first symbolically; nothing evaluates both and compares
  them. This evaluates both from one setup and states, in
  the module, every input they share — because a comparison that holds an input
  fixed cannot check that input (**T-3**).
- `scripts/diagnostic_d8_criterion_5b_gate.py` — **criterion 5b's gate**
  (decision **S4c**), in `run_all.py`. Three backgrounds, nine modes
  $0.3\le k\le600$, $2\le\ell\le600$: worst $9.5\times10^{-6}$, median
  $2.7\times10^{-8}$, gate $10^{-3}$.
- `functions/spectra/two_frame.py` — (102) evaluated in two frames, which is
  what F2, F5 and F7 are drawn from, with the transfer function driving the
  acoustic oscillation per mode (**T-37**).
- `functions/background/flrw.py` — `PLANCK_MODEL`, the stamped Planck 2018 VI
  column with a photon-only radiation era, $\Omega_\gamma h^2$ **derived** from
  $T_{CMB}$ rather than quoted. It reaches $z_{eq}=5756.0$ against CAMB's and
  CLASS's 5756.0 by an independent route.
- `scripts/make_reference_spectra.py` and `reference/` — CAMB 2.0.5 and CLASS
  v3.4.1 stamped, specialised **down** to what this bundle contains:
  $N_{eff}=0$, no reionisation, no lensing, no tensors, helium explicit.
- `scripts/make_release_status.py` — decision **S27**'s maturity ladder,
  generated and **verified**: a rung whose module, object, test or harness entry
  is missing fails the script rather than appearing in the record. It caught
  five of its own claims on its first run.
- Figures **F2**, **F5** and **F7**, each reporting what it measures rather than
  what it was expected to: F7's planned claim was false (**T-31**), and F2's
  caption was rewritten from its measured shape.

### Changed

- **S4c** — criterion 5b's tolerance moves onto this bundle's own pipeline, with
  CAMB and CLASS reported alongside as context. S4b's floor — the two codes'
  mutual difference, 0.370% across the peaks — is superseded as the threshold
  and kept as the scale: a slow-decoupling solution with no polarisation
  hierarchy and no neutrino anisotropic stress cannot meet two full Boltzmann
  codes, and a criterion that can only be failed is not a criterion.
- **S29/S29a** — the project's word for a choice of $u^a$ is **frame**;
  *threading* returns for the velocity field carried through the propagation,
  and *gauge* is not used.
- **S31a** — $16/15$ is *Annals II*'s own corrected coefficient, not a departure
  from it (**T-43**). `F2_DEFAULT` moves to the polarised value and the legacy
  constants are removed.
- **S28** — F5 is drawn in the rank decomposition $C_0,C_1,C_2$, which (89)
  produces and which is defined in every frame, rather than the Newtonian
  three-way split of §7.1.1.
- **S23 is falsified by its own premise** and recorded as such: at linear order
  every $\ell\pm1,\ell\pm2$ coupling is a product of two first-order quantities
  and is dropped, so there is no first-order generic-$u^a$ hierarchy to build.
  The $\ell\pm2$ shear couplings are v1.5.0's subject, where **S2** had them.

### Fixed

- **T-17**, **T-18** — an $\ell$ ceiling of 507 set by a quantity equal to one,
  and the 1.4 GB Bessel table it was hiding.
- **T-32** — every v1.2.0 figure was drawn on a $k$ grid stopping at the peak of
  the shear integrand. Raised to 1900; the lesson is to vary the *limit* and the
  *resolution* separately.
- **T-34** — F7 sized its $\eta$ grid for $k=140$ and integrated to $k=420$.
  `check_k` now refuses.
- **T-37** — the potentials had no $k$ in them, so nothing oscillated.
- **T-41**, **T-42** — the Sachs–Wolfe plateau on the two-frame path, diagnosed
  wrongly twice and settled as approximation **A-2**, a documented property of
  what (102) prints.
- **T-44** — criterion 5b's gate printed PASS on a `nan`, because
  `nan >= gate` is `False`. A gate that cannot fail is not a gate.
- **T-45** — the two-route agreement had been measured on a fixed 4 000-point
  grid and a frozen acoustic tail, on which both routes were un-converged *in
  the same direction*. The grid is derived from $k$ now, as everything else in
  this bundle is.

### Shipped as a stated limit

- **T-46 / Q7 / S33** — the recombination grid sets the primary source at
  $\eta_*$ and nothing derives it: refining it moves that source by **1.2%**,
  four times criterion 5a's measured 0.26%. Both routes share it, so criterion
  5b's gate cannot see it — **T-3** with the subject changed. **Measured,
  declared, and scheduled**: decision **S33** derives the grid immediately after
  the v1.2.0 tag, with five acceptance conditions, so the release closes on the
  numbers it was measured with. Every tolerance v1.2.0 states is wider than the
  bound.

### Raised, not taken
- **T-38 part (1)** — the portable manifest canonicalises by rounding to a
  string, which cannot express a tolerance. Three designs recorded.

## [1.1.0] — 2026-10-12

### Added

- `functions/spectra/peebles.py` — **Peebles recombination**, the effective
  three-level atom, and v1.1.0's named deliverable. Freeze-out comes out at
  $2.15\times10^{-4}$ against the standard $\sim2\times10^{-4}$, and it moves the
  visibility peak from $z\simeq1300$ (Saha) to $z\simeq1107$, against a standard
  1080–1100, while **widening the function by about 40%**. The width is what
  fixes the Silk damping envelope, which is why criterion 5b was blocked on this
  (S18). What is *derived* and what is *imported* is tabulated in the module
  docstring: the ODE structure and $\beta_B$ by detailed balance are derived, and
  $\alpha_B$, the atomic constants and the RECFAST fudge factor are imported with
  their sources. **The fudge is a named parameter, not a buried coefficient**, and
  `tests/` measures what it is worth.
- `functions/spectra/decoupling.py` — a `Recombination` enum. **`SAHA` remains
  the default**: flipping it changes every number in every released figure, which
  is a decision to be taken once with the before-and-after in view, not a side
  effect of adding a module.
- `functions/spectra/frame_transform.py` — the threading change made numerical.
  $\tilde\Phi_A=0$ and the Weyl invariant $\Phi_A-\Phi_H$ both hold to
  $1.1\times10^{-16}$.
- `functions/frames.py` — the curvature half of criterion 2:
  `weyl_invariance_residual` is identically zero, **with a negative control**
  showing it fails for any other potential rule, plus the dipole and
  $\ell\ge2$ statements as callable functions.
- `scripts/make_release_archive.py` — finding **T-13** closed. It found a real
  defect on its first run: `dist/` was not gitignored, so a release archive
  would have entered the fingerprint it was an archive of.

### Fixed

- `functions/spectra/sources.py` — a docstring that asserted a frame invariance
  the equations cannot have. Finding **T-14**.

### Changed

- **S21**: F5 and F7 move from v1.1.0 to v1.5.0, and F2 joins them — all three
  wait on the generic-$u^a$ hierarchy, not on figure work.

## [1.0.0] — 2026-10-05 *(tag date; the GitHub **release** is dated 9 Oct)*

> **The two dates are not in conflict and neither is verified here.** This
> heading was written on 2026-10-20 from the supplement's own front matter,
> *"First public analytical reproducibility release: v1.0.0, 5 October 2026"*.
> The GitHub releases page, read the same day, dates the **release object**
> 9 Oct — and v1.1.0 shows the same pattern, tagged 12 Oct (`dist/`) and
> released 14 Oct. A tag and its release are different events. **Neither date
> has been read off `git log`**, which is the artefact that settles it:
> `git log -1 --format=%ai v1.0.0`. Until it is, this line is the supplement's
> date and says so.

### Added

- `functions/background/flrw.py` — the expansion law **derived** from the $1+3$
  covariant energy constraint, so that (185) and (G.3) are checks on this bundle
  rather than sources for it. `CDM_MODEL` and `LCDM_MODEL` are *models*; the CDM
  *frame* is the total-energy frame and lives elsewhere (decision S8).
- `functions/spectra/sources.py` — the three temperature sources (177)–(179) and
  the integral solution (176), which returns $\alpha_\ell^{-1}\tau_\ell$ and is
  checked against the free-streaming projection of `functions/harmonics/`.
- `functions/spectra/decoupling.py` — optical depth, visibility (101), the
  diffusion scale (168), and **both** weightings of the integrated source.
- `functions/spectra/acoustic.py` — the acoustic pair (152)/(153), with the
  printed oscillator (154) recovered symbolically and the dropped term named.
- `functions/spectra/transfer.py` — (J.1), (J.3) and the transfer function (J.5).
- `functions/spectra/angular.py` — (186), (187) and (188): both routes to
  $C_\ell$, computed rather than asserted to agree.
- `functions/harmonics/external.py` — **Wilson Eq. (8)** as a fourth external
  hierarchy, integrated complex and as printed, in the imaginary convention.
- `provenance/EQUATION-NUMBERS-ANNALS-II-v1.md` — the generated label→number map
  from the accepted manuscript, which caught a tight-coupling mis-citation.
- `provenance/SOURCE-APPROXIMATIONS-v1.md` — **deliberate narrow choices of the
  source**, kept separate from defects (decision S15, approximation A-1).
- `COLD-START.md` — the resume file. **Removed again before release**: it was
  working scaffolding, not a reader's artefact. It carried a session status
  block that went stale within days — at removal it reported the wrong
  acceptance-criteria set, contradicted itself on the findings count in a single
  cell, named one figure where three had been generated, and listed as "next"
  two stages that were done — and it opened by telling a reader to read it
  first. Its durable content was already elsewhere: the run instructions in
  `README.md`, the rules in `provenance/DECISIONS-v1.0.0.md`, the `k_com`/
  `k_phys` discipline in the corrections record. Nothing was lost.

### Changed

- Findings renumbered **G1–G10 → B-1–B-10**: Annals II's own appendix equations
  are (G.1)–(G.3) and the two collided (decision S13).
- `delta_over_pi` → `delta_over_four_pi`. It returned $\Delta_\ell/(4\pi)$ while
  its name said otherwise; the two-route $C_\ell$ comparison caught the resulting
  factor of four before it reached a figure.
- Criterion 1 restated for **four** external hierarchies in two normalisations
  *and* two phase conventions; F1 redrawn with four panels.
- Criterion 5b: compare against CAMB and CLASS with a **measured** tolerance
  (decisions S4a, S4b).
- $\Lambda$CDM corrected from v2.0.0 to **v1.0.0** in the supplement's
  interpretive limits, where stale text had survived the scope decision.

- House layout, root files and licences: MIT for code, CC BY 4.0 for the
  supplement, text, captions, generated figures and generated tables.
- `provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md` — the corrections
  record, with findings B-1 and B-2.
- `provenance/OPEN-QUESTIONS-v1.0.0.md` — specification questions raised before
  code was written rather than resolved in flight.
- `functions/harmonics/weights.py` — PSTF weights as exact rationals, each cited
  to a published equation number.
- `tests/test_appendix_f_chain.py` — the Appendix F acceptance spine as
  arithmetic on the printed equations; no convention imported.
- `scripts/run_all.py`, `scripts/make_manifests.py`, `scripts/sync_conventions.py`.
- *Disclosure of AI assistance* in `README.md`.
- `captions/FIGURE-PLAN-v1.0.0.md` — the agreed specification for the figure set
  F1–F8 and the diagnostics, with colour roles and panel structure.

- `config/implementation-register.toml` and `scripts/make_tables.py` — the audit
  spine: published equation → provenance → `.py` file and object → test, generated
  into `tables/` and included by the supplement.
- `tests/test_register.py` — resolves every reference in the register, so the
  audit tables cannot drift from the code.
- `functions/harmonics/free_streaming.py`, `functions/harmonics/external.py` —
  the recursion in three normalisations, and the external hierarchies as
  printed in their own papers.
- `functions/plotting/style.py` and figure **F1**, the Appendix F match.

### Changed

- Figure set revised with the PI: the released set is now F1–F8, organised around
  the angular autocorrelation, the source decomposition of §7.1.1 drawn in two
  frames, and frame specialisation from a generic $u^a$.
- The $\pm(\ell+2)$ control is **withdrawn from v1.0.0** and replaced by a
  relative-sign control on the free-streaming bracket, in `diagnostics/`. The
  $\pm(\ell+2)$ term is second order and is not in this release's physics.
- v1.5.0 restated as a **recovery and check** of v1.0.0 rather than an extension
  of it, in the version-control policy and the supplement.
- Palette re-validated against the house surfaces rather than inherited.
- Criterion 5's range derived and closed: $2\le\ell\le20$ at 5%, generated by
  `scripts/derive_ell_range.py` rather than asserted.
- Finding **B-3** recorded: Annals II's Bessel identity (199) is correct only at
  even $m$; (204) and (205) inherit a constant error.
- `make_manifests.py` now distinguishes **append** from **rewrite** on the
  corrections record. Hash-freezing it raised a release-blocking alarm every time
  a finding was added — an alarm that fires on success trains people to ignore
  it. The guard now fails only if recorded bytes change.

### Notes

- Equation numbers in this bundle are **published** numbers, resolved from the
  published PDFs. The published and arXiv numberings differ, and not by a
  constant offset.
