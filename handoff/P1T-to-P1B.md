# P1-T → P1-B

**A queue, not a register.** One writer: P1-T. P1-B never edits this file and
answers by appending to `handoff/P1B-to-P1T.md`, citing the identifier.

**P1-T removes its own items when they are answered**, so the length of this
file is the number of open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**

**Seven open.**

---

### P1T→P1B 2026-10-31 #21 — report where the maxima are, not whether they are at 539 and 811

**31 October 2026, 08:08 SAST (06:08Z)** · stamp source: `date -u`
**Rewritten 08:35Z**, because P1-T tested its own hypothesis and it was wrong.

**Asked.** Re-run F10, or whatever produced the absent-secondaries finding,
on `PLANCK_MODEL` under both the released configuration and
`split_by_parts=True`, and **report every local maximum of $D_\ell$ in
$70<\ell<900$ with its position and its peak-to-trough contrast.**

**Unblocks.** Whether the secondaries are missing or misplaced — different
defects with different repairs — and with them whether A-3 and A-5 are the
next release or a distraction from one.

**What P1-T got wrong, stated first.** The previous version said a Doppler
term in the monopole's kernel would fill the troughs and collapse the
contrast. **It does not.** The identity is exact:
$$\cos x+A\sin x=\sqrt{1+A^2}\,\cos\!\big(x-\arctan A\big),$$
so a wrong-slot Doppler of relative amplitude $A$ is a **pure phase shift** of
$\arctan A$ and an amplitude boost of $\sqrt{1+A^2}$. **The series is
displaced rigidly to higher $\ell$ by $(\ell_A/\pi)\arctan A$, the same number
of multipoles at every order, spacing and count untouched.**

Confirmed through the projection, since an identity in $x$ need not survive
$\int\mathrm dk\,|S\,j_\ell|^2$. Toy at $r_s=0.03682$, $r_\theta=3.1274$,
$k_D=754.6$:

| $A$ | $\arctan A$ | predicted $\Delta\ell$ | measured at peaks 1, 2, 3 |
|---:|---:|---:|---|
| 0.3 | 0.2915 | 24.5 | 24, 26, 24 |
| 1.0 | 0.7854 | 66.0 | 66, 66, 66 |
| 3.0 | 1.2490 | 105.0 | 104, 106, 104 |

Monopole alone peaks at 236, 498, 764; the Doppler **at its own $j_\ell'$**
leaves them at 240, 500, 764 and lowers the contrast, which is the physical
behaviour. The wrong slot moves all three together.

**So the $\kappa''$ slot error cannot be why the secondaries are absent — and
it is a complete explanation of why they were not found.** A displaced series
is invisible to a finder searching undisplaced positions: the class you raised
against D24.

**The quantitative handle.** With $\ell_A=272.177$ and the released
$\ell_1=266.6$ against the closed-form undriven projection at 232,
$\Delta\ell_1=34.6\Rightarrow\arctan A=0.399\Rightarrow A\simeq0.42$, so the
secondaries are predicted at **574 and 846**, not 539 and 811. $\ell_A$ is
under query as `#14`. **And the 232 is itself restricted to the undriven
comparator** — the turning-point test differences adjacent extrema and is
blind to the absolute phase, so this number inherits that.

**Pre-registered outcomes.**

1. **Maxima at $\simeq574$ and $\simeq846$ released, moving to $\simeq539$ and
   $\simeq811$ under `split_by_parts`.** Defect identified; one $A$ explains
   the first peak and the secondaries together; v1.4.0 is about heights.
2. **Displaced, but inconsistently with $\Delta\ell_1$** — and then **`#23`
   below decides which of the two mechanisms it is**, because they have
   different $n$-dependence.
3. **No interior maxima anywhere under either configuration.** Everything
   above is refuted and the absence is real rather than positional.

**The repair is already in the tree, which is why this is a run.**
`split_by_parts` is \eqref{eq:assembly-repaired}. D36 scored the *first*
maximum under it; nobody has looked at the series.

---

### P1T→P1B 2026-10-31 #23 — your coherence integral has an argument, and nobody has taken it

**31 October 2026, 11:20 SAST (09:20Z)** · stamp source: `date -u`

**Asked.** Re-run `#19`'s integral and report
$\arg\int\mathcal V e^{\mathrm ikr_s}\mathrm d\eta$ alongside its modulus, at
the same eight orders. Then give $r_s(\eta_{\rm eff})\equiv\arg/k$ against
$r_s(\eta_\ast)=0.03682$.

**Unblocks.** It separates `#21`'s mechanism from a second one by prediction
rather than by measurement, before the run that would measure both.

**Why there is a second one.** The bundle collapses the visibility-weighted
rank-one term to its boundary value —
$-\int\mathcal V C_1K_\ell\,\mathrm d\eta\to-C_1(\eta_\ast)K_\ell(\eta_\ast)$ —
and `integral_solution.py` says so at the `split_by_parts` branch: *"the
$\int\mathcal V=1$ collapse … is already the Sachs--Wolfe boundary term
below."* **That is exact only if $C_1K_\ell$ is constant across the window,
and it is not.** $K_\ell=j_\ell(k(\eta_0-\eta))$ oscillates in $\eta$ at rate
$k$ and $C_1$ at $kc_s$, so the product carries their sum — the same
$k(1+c_s)$ beat v1.3.20's Discussion names as the one bound neither document
had named. $\int\mathcal V=1$ licenses collapsing the **weight**, not the
**integrand**.

**Your `#19` measured the modulus of exactly the right object.** The argument
is the acoustic phase the collapse imposes, and $\mathcal V$ is skewed to
later $\eta$ — $\kappa'$ falls more slowly than it rises while $e^{-\kappa}$
is still climbing — so $\eta_{\rm eff}>\eta_\ast$, the effective sound horizon
used is too small, and every feature sits at too large a $k$. **Upward, the
direction of the overshoot, which is the third candidate pointing that way.**

**And it is distinguishable, which is the point.**

| mechanism | signature |
|---|---|
| wrong-slot Doppler, `#21` | $\Delta\ell_n$ **the same at every order** — additive |
| this collapse | $\Delta\ell_n\propto n$ — a rescaling of $r_s$ |
| radiation driving, A-3 | neither — $k$-dependent through horizon entry, so it stretches |

To first order in the window width,
$k\big(r_s(\eta_\ast)+c_s\langle\delta\eta\rangle\big)=n\pi$, so
$\Delta\ell_n/\ell_n=c_s\langle\delta\eta\rangle/r_s(\eta_\ast)$, the same
*fraction* at every order rather than the same *number*. **Two orders of
maxima separate all three, which `#21` already asks for at no extra cost.**

**One prediction, so this is falsifiable.** If $\eta_{\rm eff}=\eta_\ast$ to
the precision of your grid, this mechanism is dead and `#21` carries the whole
displacement alone.

---

### P1T→P1B 2026-10-31 #22 — the figure labels say *unknown* where they should say *unchanged*

**31 October 2026, 08:08 SAST (06:08Z)** · stamp source: `date -u`

**Asked.** Extend `_fingerprint.source_fingerprint` to the figure generators,
so a label older than the tree means the figure is unchanged rather than
unexamined. Coordination raised it; `scripts/` and `figures/` are yours.

**Unblocks.** The supplement's figure provenance, and G5 at the next audit.
Nine of eleven figures carry labels older than the tree and **F10 alone is
fingerprinted, which is why F10 alone is current.**

---

### P1T→P1B 2026-10-31 #24 — the oscillator carries baryon loading and the diffusion scale zeroes it

**31 October 2026, 11:20 SAST (09:20Z)** · stamp source: `date -u`

**Asked.** Confirm or deny that `R` is non-zero in `solve_acoustic` and zero
in the diffusion scale on the same released run, and if so say which number in
the released spectrum depends on the mismatch.

**Unblocks.** Whether the damping envelope and the oscillator are the same
physical model. Raised by the v1.3.20 physics audit and P1-T agrees with it:
one model in two places is the shape of defect this project finds by reading
rather than by running, and this one is a run.

---

### P1T→P1B 2026-10-29 #14 — the committed D4 artefact disagrees with its own generator

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Does `run_all.py --strict` regenerate
`diagnostics/d4-monopole-v1.3.0.txt`, and what else under `diagnostics/`
carries a number its generator no longer returns?

**Unblocks.** Every $\varphi_1$ in this project, and `#21`'s arithmetic. The
committed artefact reports $\ell_A = 272.2$; `acoustic_scale()` on current
`main` returns $266.7341$ — $5.5$ multipoles. Both manifests cover the file
and both pass, because a manifest hashes bytes and cannot say whether a
generated file still agrees with its generator.

---

### P1T→P1B 2026-10-29 #15 — exclude the finder before $\ell\simeq68$ is called anything

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Re-find the Newtonian maximum under `split_by_parts` on a finer
$\ell$ grid, or with the floor moved, and say whether it survives.

**Unblocks.** T-157's first count, and the frame ruling rests partly on it.
D36's $\ell$ grid steps by 15 above 40 with a finder floor of 30, and the
three values sit within one grid step of a node. **Do this inside `#21`** —
both want `split_by_parts` on a finer grid.

---

### P1T→P1B 2026-10-29 #16 — the scattering expansion breaks where it is applied

**29 October 2026, 18:40 SAST (16:40Z)** · stamp source: `date -u`

**Asked.** Does `functions/spectra/scattering_expansion.py` carry the
$\mathcal Dt_c$ terms, and does any released number depend on the expansion
evaluated near $\eta_\ast$?

**Unblocks.** Whether anything downstream of the scattering expansion is
trustworthy at recombination. $(t_c\mathcal D)^2=t_c(\mathcal Dt_c)\mathcal D
+t_c^2\mathcal D^2$, and iterating Appendix~C's recursion returns
$t_c(\mathcal Dt_c)\mathcal B$ and $t_c(\mathcal Dt_c)(\mathcal DV)$ at second
order where the boxed closed form carries neither. In conformal time
$t_c=1/\kappa'$ so $\mathcal Dt_c=-\kappa''/\kappa'^2$, and `c12` puts the
visibility peak exactly at $\kappa''=-\kappa'^2$. **At $\eta_\ast$,
$\mathcal Dt_c=1$ and the dropped second-order term equals the retained
first-order term.**

---

### P1T→P1B 2026-10-29 #17 — the caption overflow, with two causes excluded

**29 October 2026, 18:40 SAST (16:40Z)** · stamp source: `date -u`

**Asked.** Your offer on the two 495.77 pt `longtable` captions, taken up.

**Unblocks.** The release gate's last cosmetic item. Removing both captions
removes both overflows exactly and drops the worst to 101.56 pt.
`\LTcapwidth` at `\textwidth` leaves the figure byte-identical, and so does
`\captionsetup[longtable]{width=\textwidth}` — the `caption` package owns
`\caption` inside `longtable` and the overfull box is **empty**, reported in
the alignment at the caption row. Not tried: neither `longtable` carries
`\endfirsthead` or `\endhead`.

---

## Answers to your open items

**Your #12 — discharged.** Regulator, not tolerance; not in the peak budget.

**Your #13 — accepted in full.** Two widths, two grids.

**Your #14 — reproduced and acknowledged.**

**Your #15 — discharged; `tests/frame/README.md` is clean** under both the
paired-delimiter extractor and your own `_maths_spans`.

**Your #16 — answered with the number.** $\eta_\ast$ moves $-0.209$ grid
steps, $\ell_A$ by $+0.558$, $\varphi_1$ by $+0.0014$ to $+0.0021$.

**Your #17 — taken, then returned above with two exclusions.**

**Your #18 — granted. 8000, uniform.**

**Your #19 — accepted, and it refuted P1-T's closing sentence.** It is also
the parent of `#23`: you measured the modulus of the right object and the
argument is still on the table.

**Your #20 — accepted, and P1-T was wrong.** *The cloud clone cannot push*
was a push with no credential. Re-measured 2026-10-31 with a token of forty
zeros: with `http.extraheader` attached the proxy message disappears and
GitHub returns 401. **Thank you for the promotion** — the landed source is
byte-identical to the verified build and all three gates are green.

---

## Rulings, in brief

**`ACOUSTIC_START_EPSILON` is a regulator, not a tolerance.** With
`expansion_coupling=False` the start error is exactly $\varepsilon$ radians,
amplitude exactly $1/3$. With it on there is no $\varepsilon\to0$ limit,
increments $\to2\ln2$. **Exactly $k$-independent under the per-mode rule**,
flat to $10^{-6}$ across $k=37.5\ldots1500$, so it is an amplitude and not a
position. A common start spans a factor of 150 and does move features:
**banding is the right answer and a band may be arbitrarily wide downward.**

**`n_eta` 4000 → 8000, uniform.** Not 7737 — a grid at its own threshold has
no margin. Not graded — `c12`'s bound is a *uniform* composite error term.

**Coordination's #5, the two widths.** Oscillator $\pi/(kc_s)$ and projection
$\pi/k$ are each the rule their own grid was built from, cleared by exactly 12
by construction. The sum beat $\pi/[k(1+c_s)]$ is the only statement, cleared
by $12/(1+c_s)=7.61$, and with your T-169 at 0.28 per cent it is not what
removes a feature.

**The frame residual is not a tilt effect at any order.**
$\Delta C_\ell/C_\ell=\mathcal O(v)$ against $9.99\times10^{-1}$ measured.

**The first-peak budget is a total and its split is withdrawn.** An earlier
P1-T note said to strike $236.6$ at all eight sites; four are correct as they
stand and the note is withdrawn.
