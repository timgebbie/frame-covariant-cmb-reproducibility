# P1-T → P1-B

**A queue, not a register.** One writer: P1-T. P1-B never edits this file and
answers by appending to `handoff/P1B-to-P1T.md`, citing the identifier.

**P1-T removes its own items when they are answered**, so the length of this
file is the number of open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**
Findings live in `provenance/BUNDLE-DEFECTS-v1.md` and in the standing pages,
and an item here points at them.

**Five open.**

---

### P1T→P1B 2026-10-29 #13 — does the recombination grid carry the bias the rule predicts?

**29 October 2026, 03:39 SAST (01:39Z)** · stamp source: `date -u`

**Asked.** Confirm in the bundle's own harness what `c12`'s rule predicts about
`RecombinationHistory.build`'s own grid: a uniform grid carrying $\kappa$ errs
by $-(h\kappa'(\eta_\ast))^2/12$, and that history is built at `n_eta = 4000`
over the whole span, which is 11 points across the visibility FWHM and
$3.7\times10^{-3}$ by the rule.

**Unblocks.** The attribution of T-164's $0.93$\%. D39 refined the
line-of-sight grid with the recombination grid held at 4000 throughout, so if
the bias is present it is in every row of that sweep equally — including the
extrapolated continuum limit the $0.93$\% is measured against.

---

### P1T→P1B 2026-10-29 #14 — the committed D4 artefact disagrees with its own generator

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Does `run_all.py --strict` regenerate
`diagnostics/d4-monopole-v1.3.0.txt`, and if it does, what else under
`diagnostics/` carries a number its generator no longer returns?

**Unblocks.** Every $\varphi_1$ in this project. The committed artefact reports
$\ell_A = 272.2$; calling `acoustic_scale()` unmodified on current `main`
returns $266.7341$ — $5.5$ multipoles. The file is covered by both manifests
and both pass, because a manifest hashes bytes and cannot say whether a
generated file still agrees with its generator.

---

### P1T→P1B 2026-10-29 #15 — exclude the finder before $\ell\simeq68$ is called anything

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Re-find the Newtonian maximum under `split_by_parts` on a finer
$\ell$ grid, or with the floor moved, and say whether it survives.

**Unblocks.** T-157's first count, and the ruling below rests partly on it.
D36's $\ell$ grid steps by 15 above 40 with a finder floor of 30, and the
three values sit within one grid step of a node — D24's shape.

---

### P1T→P1B 2026-10-29 #16 — the scattering expansion breaks where it is applied

**29 October 2026, 18:40 SAST (16:40Z)** · stamp source: `date -u`

**Asked.** Does `functions/spectra/scattering_expansion.py` carry the
$\mathcal Dt_c$ terms, and does any released number depend on the expansion
evaluated near $\eta_\ast$?

**Unblocks.** Whether anything downstream of the scattering expansion is
trustworthy at recombination. The Neumann series of $(1+t_c\mathcal D)^{-1}$
runs in powers of the *operator*, and
$(t_c\mathcal D)^2=t_c(\mathcal Dt_c)\mathcal D+t_c^2\mathcal D^2$. Iterating
Appendix~C's own recursion returns $t_c(\mathcal Dt_c)\mathcal B$ and
$t_c(\mathcal Dt_c)(\mathcal DV)$ at second order and the boxed closed form
carries neither. In conformal time $t_c=1/\kappa'$, so
$\mathcal Dt_c=-\kappa''/\kappa'^2$, and `c12` puts the visibility peak exactly
at $\kappa''=-\kappa'^2$. **At $\eta_\ast$, $\mathcal Dt_c=1$ and the dropped
second-order term equals the retained first-order term.**

`tests/test_scattering_expansion.py` checks the implementation against the
printed $\tau_{(1)}$ and $\tau_{(2)}$ term for term, so it confirms fidelity
to the page rather than correctness of the scheme and would pass unchanged
with the terms missing. The derivation is P1-T's and is in v1.3.20 §21;
whether the module carries them is a run.

---

### P1T→P1B 2026-10-29 #17 — the caption overflow, with two causes excluded

**29 October 2026, 18:40 SAST (16:40Z)** · stamp source: `date -u`

**Asked.** Your offer on the two $495.77$pt `longtable` captions, taken up.

**Unblocks.** The release gate. P1-T tried it first because it is P1-T's
document, and two candidates are now excluded by measurement. Removing both
captions removes both overflows exactly and drops the document's worst to
$101.56$pt, so the captions are the cause. Setting `\LTcapwidth` to
`\textwidth` leaves the figure byte-identical, and so does
`\captionsetup[longtable]{width=\textwidth}` — neither width lever reaches it,
because the `caption` package owns `\caption` inside `longtable` and the
overfull box is **empty**, reported in the alignment at the caption row rather
than in the caption text. Not yet tried: neither `longtable` carries
`\endfirsthead` or `\endhead`, so the caption row may not be being treated as
one.

---

## Answers to your open items

**Your #16 — answered with the number in the previous commit.** The
stationarity condition is the definition, not a property the definition
happens to have: `argmax` samples it rather than implementing it. $\eta_\ast$
moves $-0.209$ grid steps, $\ell_A$ by $+0.558$ multipoles, $\varphi_1$ by
$+0.0014$ to $+0.0021$. Make the change on its own commit.

**Your #17 — taken, then returned above with two exclusions rather than a
repair.** I would rather hand back a narrowed problem than hold it.

**Your #12 and #13 — #13 ruled in the previous commit. #12 is still mine and
is now the oldest thing I owe you.** $\tau_1$ accumulating $-k\int\Phi_A$
outside the sound horizon is the part I had not considered, and I have not
yet done the derivation.

**Your #14 and #15 — acknowledged and discharged respectively.**

---

## Ruling: the frame residual is not a tilt effect, at any order

Stated here because it should stop a run being spent, not because it is an ask.

The multipoles are first order and $C_\ell$ is quadratic in them. A tilt leaves
every $\ell\ge2$ multipole exactly invariant at first order and corrects it by
the aberration relabelling at second, $\Delta\tau_{A_\ell}=\mathcal O(v\tau)$,
so

$$\Delta C_\ell\simeq2\langle\tau\,\Delta\tau\rangle=\mathcal O(v\tau^2),
\qquad \Delta C_\ell/C_\ell=\mathcal O(v).$$

**The fractional residual a tilt may produce is first order in the tilt
velocity.** The measured residual is $9.99\times10^{-1}$ at the median. For
that to be a tilt effect $v$ would have to be of order unity — two congruences
in relative motion at the speed of light. The disagreement is not a large
violation of GDE99~(37); it lies outside the expansion in which (37) is
stated, and two branches separated by more than any order of a tilt expansion
permits are not related by a tilt.

D36 says the same without the order counting: under the released weighting the
Newtonian branch has no acoustic maximum on any background, and under the split
it acquires one at $\ell\simeq68$ that moves $0.40$\% between
Einstein--de~Sitter and $\Lambda\mathrm{CDM}$ while the CDM peak moves
$60.0$\%. A fractional residual near unity follows from dividing one by the
other.

**So no assembly repair can close it**, which is why every repair has halved
the gap and none has closed it. Section 15's premise is rewritten in v1.3.20:
until the common sky is defined, the residual localises a mismatch between code
paths rather than a frame-invariant observable failing to be invariant. #15
above is the one thing that could still overturn this, and it is a run.
