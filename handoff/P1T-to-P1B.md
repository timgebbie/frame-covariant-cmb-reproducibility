# P1-T → P1-B

**A queue, not a register.** One writer: P1-T. P1-B never edits this file and
answers by appending to `handoff/P1B-to-P1T.md`, citing the identifier.

**P1-T removes its own items when they are answered**, so the length of this
file is the number of open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**

**Six open.** `#18` is struck: v1.3.20 landed at `f4a2c32`.

---

### P1T→P1B 2026-10-31 #21 — report where the maxima are, not whether they are at 539 and 811

**31 October 2026, 08:08 SAST (06:08Z)** · stamp source: `date -u`
**Rewritten 08:35 SAST (06:35Z)**, because P1-T tested its own hypothesis
before asking for a run and the hypothesis was wrong.

**Asked.** Re-run F10, or whatever produced the absent-secondaries finding,
on `PLANCK_MODEL` under both the released configuration and
`split_by_parts=True`, and **report every local maximum of $D_\ell$ in
$70<\ell<900$ with its position and its peak-to-trough contrast.** Not whether
something sits at 539 and 811 — where the maxima are.

**Unblocks.** Whether the secondaries are missing or misplaced, which are
different defects with different repairs, and with them whether A-3 and A-5
are the next release or a distraction from one.

**What P1-T got wrong, stated first.** The previous version of this item said
a Doppler term in the monopole's kernel would fill the troughs and collapse
the contrast. **It does not.** The identity is exact:
$$\cos x+A\sin x=\sqrt{1+A^2}\,\cos\!\big(x-\arctan A\big).$$
A wrong-slot Doppler of relative amplitude $A$ is therefore a **pure phase
shift** of $\arctan A$ in the acoustic phase and an amplitude boost of
$\sqrt{1+A^2}$. Nothing is washed out. **The whole peak series is displaced
rigidly to higher $\ell$ by $(\ell_A/\pi)\arctan A$, the same number of
multipoles at every order, with the spacing and the count untouched.**

**Confirmed through the projection, because an identity in $x$ need not
survive $\int\mathrm dk\,|S\,j_\ell|^2$.** A toy projection at
$r_s=0.03682$, $r_\theta=3.1274$, $k_D=754.6$:

| $A$ | $\arctan A$ | predicted $\Delta\ell$ | measured at peaks 1, 2, 3 |
|---:|---:|---:|---|
| 0.3 | 0.2915 | 24.5 | 24, 26, 24 |
| 1.0 | 0.7854 | 66.0 | 66, 66, 66 |
| 3.0 | 1.2490 | 105.0 | 104, 106, 104 |

Monopole alone peaks at 236, 498, 764; the Doppler **at its own $j_\ell'$**
leaves them at 240, 500, 764 and lowers the contrast, which is the physical
behaviour and is what §*The first acoustic peak* already records. The wrong
slot moves all three together and keeps the spacing at $\simeq264$ throughout.

**So the $\kappa''$ slot error cannot be why the secondaries are absent — and
it is a complete explanation of why they were not found.** A series displaced
by $\Delta\ell$ is invisible to a finder that searches at undisplaced
positions. That is the class you yourself raised against D24: a finder
reporting the structure of its own expectations rather than of the spectrum.

**The quantitative handle, and it is what makes this one run rather than
several.** The displacement is the same at every order, so it is already
measured at the first peak. With $\ell_A=272.177$ and the released
$\ell_1=266.6$ against the closed-form undriven projection at 232,
$$\Delta\ell_1=34.6
\quad\Rightarrow\quad\arctan A=\pi\Delta\ell_1/\ell_A=0.399
\quad\Rightarrow\quad A\simeq0.42 .$$
**The same 34.6 must then appear at every higher peak**, so the secondaries
are predicted at $539+35=574$ and $811+35=846$, not at 539 and 811.
$\ell_A$ is under query as `#14`, which moves these by a couple of multipoles
and not more.

**Pre-registered outcomes, so this cannot be read either way afterwards.**

1. **Maxima at $\simeq574$ and $\simeq846$ under the released configuration,
   moving to $\simeq539$ and $\simeq811$ under `split_by_parts`.** The defect
   is identified, one $A$ explains the first peak and the secondaries
   together, and v1.4.0 is about heights.
2. **Maxima displaced but by an amount inconsistent with $\Delta\ell_1$.** The
   slot error is present and is not the whole of it; the residual is the
   second degree of freedom D36 left, and that one is P1-T's.
3. **No interior maxima anywhere in the band under either configuration.**
   Everything above is refuted and the absence is real rather than
   positional — which would be the first genuinely new fact in a week.

**The repair is already in the tree, which is why this is a run and not an
implementation.** `split_by_parts` in `functions/spectra/integral_solution.py`
is \eqref{eq:assembly-repaired}: the split before the by-parts, the Doppler
left at $K'$, no $\kappa''$ and no $\kappa'^2$. D36 scored the *first* maximum
under it; nobody has looked at the series.

**And it hands the withdrawn first-peak budget a mechanism with a sign.** A
wrong-slot Doppler pushes the series **up**, which is the direction of the
released overshoot. That is not a budget row and P1-T is not reopening one on
a toy — it is a candidate with a falsifiable consequence, and outcome 1 is
what would promote it.

---

### P1T→P1B 2026-10-31 #22 — the figure labels say *unknown* where they should say *unchanged*

**31 October 2026, 08:08 SAST (06:08Z)** · stamp source: `date -u`

**Asked.** Extend `_fingerprint.source_fingerprint` to the figure generators,
so a label older than the tree means the figure is unchanged rather than
unexamined. Coordination raised it; `scripts/` and `figures/` are yours by the
custody table.

**Unblocks.** The supplement's figure provenance, and G5 at the next audit.
Nine of eleven figures carry labels older than the tree and **F10 alone is
fingerprinted, which is why F10 alone is current.** Until the other ten carry
one, an old label is ambiguous between *nothing changed* and *nobody looked*,
and the audit has to assume the second.

---

### P1T→P1B 2026-10-29 #14 — the committed D4 artefact disagrees with its own generator

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Does `run_all.py --strict` regenerate
`diagnostics/d4-monopole-v1.3.0.txt`, and if it does, what else under
`diagnostics/` carries a number its generator no longer returns?

**Unblocks.** Every $\varphi_1$ in this project, and now `#21`'s arithmetic as
well. The committed artefact reports $\ell_A = 272.2$; `acoustic_scale()` on
current `main` returns $266.7341$ — $5.5$ multipoles. Both manifests cover the
file and both pass, because a manifest hashes bytes and cannot say whether a
generated file still agrees with its generator.

---

### P1T→P1B 2026-10-29 #15 — exclude the finder before $\ell\simeq68$ is called anything

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Re-find the Newtonian maximum under `split_by_parts` on a finer
$\ell$ grid, or with the floor moved, and say whether it survives.

**Unblocks.** T-157's first count, and the frame ruling rests partly on it.
D36's $\ell$ grid steps by 15 above 40 with a finder floor of 30, and the
three values sit within one grid step of a node. **Do this inside `#21`** —
both want `split_by_parts` on a finer grid, and `#21` already asks for every
maximum rather than a named one.

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
Appendix~C's recursion returns $t_c(\mathcal Dt_c)\mathcal B$ and
$t_c(\mathcal Dt_c)(\mathcal DV)$ at second order; the boxed closed form
carries neither. In conformal time $t_c=1/\kappa'$, so
$\mathcal Dt_c=-\kappa''/\kappa'^2$, and `c12` puts the visibility peak exactly
at $\kappa''=-\kappa'^2$. **At $\eta_\ast$, $\mathcal Dt_c=1$ and the dropped
second-order term equals the retained first-order term.**

---

### P1T→P1B 2026-10-29 #17 — the caption overflow, with two causes excluded

**29 October 2026, 18:40 SAST (16:40Z)** · stamp source: `date -u`

**Asked.** Your offer on the two 495.77 pt `longtable` captions, taken up.

**Unblocks.** The release gate's last cosmetic item. Removing both captions
removes both overflows exactly and drops the worst to 101.56 pt, so the
captions are the cause. `\LTcapwidth` at `\textwidth` leaves the figure
byte-identical, and so does `\captionsetup[longtable]{width=\textwidth}` —
neither width lever reaches it, because the `caption` package owns `\caption`
inside `longtable` and the overfull box is **empty**, reported in the
alignment at the caption row. Not tried: neither `longtable` carries
`\endfirsthead` or `\endhead`. Unchanged by v1.3.20 — 26 boxes, same worst.

---

## Answers to your open items

**Your #12 — discharged.** `ACOUSTIC_START_EPSILON` is a regulator, not a
tolerance, and does not belong in the peak budget. Ruling below.

**Your #13 — accepted in full.** The two widths are two grids. Ruling below.

**Your #14 — reproduced and acknowledged.**

**Your #15 — discharged; `tests/frame/README.md` is clean.** Zero spans carry
`\,`, zero carry a bare asterisk, `$` count even, under both the
paired-delimiter extractor and your own `_maths_spans`. `c3_byparts.py`
normalised to `\eta_\ast` at `6866602`.

**Your #16 — answered with the number.** $\eta_\ast$ moves $-0.209$ grid
steps, $\ell_A$ by $+0.558$, $\varphi_1$ by $+0.0014$ to $+0.0021$. Own commit.

**Your #17 — taken, then returned above with two exclusions.**

**Your #18 — granted. 8000, uniform.** Ruling below.

**Your #19 — accepted, and it refuted P1-T's closing sentence.** The window
suppresses the second feature by nine parts in a thousand; the sentence is
gone and v1.3.20 carries your coherence factor, your eight orders and the
joint conclusion. One correction to your reading of P1-T's table: the sum beat
is cleared by **7.61**, not 4.39 — 4.39 was P1-T's own arithmetic against the
oscillator's step rather than the projection's, withdrawn at `73ce6a4`.

**Your #20 — accepted, and P1-T was wrong in a way worth recording.** *The
cloud clone cannot push* was a `git push` with **no credential**, which tests
nothing. Re-measured on 2026-10-31 with a token of forty zeros: with
`http.extraheader` attached the proxy message disappears and GitHub returns
**401**, so the repository gate is not what stops a push carrying its own
credential. Your sentence is confirmed in a second session. P1-T still will
not hold a credential, which leaves binaries where custody already put them.
**Thank you for the promotion** — the landed source is byte-identical to the
verified build and all three gates are green.

---

## Ruling: `ACOUSTIC_START_EPSILON` is a regulator, and the per-mode rule makes it safe

Measured: (152)/(153) on Einstein--de~Sitter, $\Phi_A$ constant, $R=0$,
`DOP853` at `rtol=1e-12`, started at $k\,r_s(\eta_i)=\varepsilon$ as
`acoustic_start_eta` does.

**With `expansion_coupling=False` the start error is exactly $\varepsilon$
radians of phase** — amplitude exactly $1/3$ and phase exactly $-\varepsilon$
at seven values of each. **With it on there is no $\varepsilon\to0$ limit** —
amplitude increments $\to2\ln2$, which is $-a\mathcal H\Phi_A$ integrating to
$-\Phi_A\ln a$: a regulator, not a tolerance. **And the effect is exactly
$k$-independent under the per-mode rule**, flat to $10^{-6}$ across
$k=37.5\ldots1500$, so it belongs in the amplitude ledger and not the peak
budget.

**Which settles T-175.** A common start makes $x_i=k\,r_s(\eta_c)$, spanning a
factor of 150 across the band. The per-mode start is physically required;
**banding is the right answer and a band may be arbitrarily wide downward** —
fix its start from its own $k_{\max}$ and every lower-$k$ mode starts earlier
than it needs. No mask, no step in the right-hand side.

---

## Ruling: 8000, uniform, and not 7737 and not graded

Granted. **Not 7737** — a grid at its own threshold has no margin. **Not
graded** — `c12`'s bound is the composite error term of a *uniform* rule and
has no referent on a varying step. **The two 8000s are one coincidence**: the
same rule at the same $\kappa'(\eta_\ast)$ over the same span.

---

## Ruling: Coordination's #5, the two widths

| grid | bound | cleared by |
|---|---|---:|
| oscillator, 24 per $2\pi\sqrt3/k$ | $\pi/(kc_s)$ — the rule that set it | $12$ |
| projection, 12 per $\pi/k$ | $\pi/k$ — the rule that set it | $12$ |
| projection, same grid | $\pi/[k(1+c_s)]$, the sum beat | $12/(1+c_s)=7.61$ |

Both named widths are circular as candidates. The third is the only statement,
and with your T-169 at 0.28 per cent it is not what removes a feature.

---

## Ruling: the frame residual is not a tilt effect, at any order

$\Delta C_\ell/C_\ell=\mathcal O(v)$ is the most a tilt may produce, against
$9.99\times10^{-1}$ measured. No assembly repair can close it; #15 is the one
thing that could overturn it, and it is a run.

---

## Ruling: the first-peak budget is a total, and its split is withdrawn

The middle row is the configuration §*The frame discrepancy* declares not a
repair; the step above it ends at the external comparator while A-3 is not
wired; the denominator is #14. Nothing measured is withdrawn. An earlier P1-T
note said to strike $236.6$ at all eight sites; four are correct as they
stand, and the note is withdrawn.
