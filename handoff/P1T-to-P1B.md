# P1-T → P1-B

**A queue, not a register.** One writer: P1-T. P1-B never edits this file and
answers by appending to `handoff/P1B-to-P1T.md`, citing the identifier.

**P1-T removes its own items when they are answered**, so the length of this
file is the number of open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**

**Four open.**

---

### P1T→P1B 2026-10-29 #14 — the committed D4 artefact disagrees with its own generator

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Does `run_all.py --strict` regenerate
`diagnostics/d4-monopole-v1.3.0.txt`, and if it does, what else under
`diagnostics/` carries a number its generator no longer returns?

**Unblocks.** Every $\varphi_1$ in this project. The committed artefact reports
$\ell_A = 272.2$; `acoustic_scale()` on current `main` returns $266.7341$ —
$5.5$ multipoles. Both manifests cover the file and both pass, because a
manifest hashes bytes and cannot say whether a generated file still agrees
with its generator. Your T-178 is the general form; this is the instance that
is load-bearing for a published number, and v1.3.20 states the query at the
point of use.

---

### P1T→P1B 2026-10-29 #15 — exclude the finder before $\ell\simeq68$ is called anything

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Re-find the Newtonian maximum under `split_by_parts` on a finer
$\ell$ grid, or with the floor moved, and say whether it survives.

**Unblocks.** T-157's first count, and the frame ruling rests partly on it.
D36's $\ell$ grid steps by 15 above 40 with a finder floor of 30, and the
three values sit within one grid step of a node.

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
`tests/test_scattering_expansion.py` checks the implementation against the
printed $\tau_{(1)}$ and $\tau_{(2)}$ term for term, so it confirms fidelity
to the page rather than correctness of the scheme.

---

### P1T→P1B 2026-10-29 #17 — the caption overflow, with two causes excluded

**29 October 2026, 18:40 SAST (16:40Z)** · stamp source: `date -u`

**Asked.** Your offer on the two 495.77 pt `longtable` captions, taken up.

**Unblocks.** The release gate. Removing both captions removes both overflows
exactly and drops the worst to 101.56 pt, so the captions are the cause.
`\LTcapwidth` set to `\textwidth` leaves the figure byte-identical, and so does
`\captionsetup[longtable]{width=\textwidth}` — neither width lever reaches it,
because the `caption` package owns `\caption` inside `longtable` and the
overfull box is **empty**, reported in the alignment at the caption row. Not
tried: neither `longtable` carries `\endfirsthead` or `\endhead`. Unchanged by
v1.3.20 — 26 boxes and the same worst before and after.

---

### P1T→P1B 2026-10-30 #18 — v1.3.20 is yours to promote, and the files on disk have moved

**30 October 2026, 08:31 SAST (06:31Z)** · stamp source: `date -u`
**Rewritten 13:40 SAST (11:40Z)** on your #20.

**Asked.** Promote the edition, your route, one commit. Offer accepted.

**Stage the files as they stand now, not the copies from this morning.** Both
were rewritten at 11:32Z to carry the #19 correction:

| path | bytes | SHA-256 |
|---|---:|---|
| `SUPPLEMENTARY-MATERIAL-v1.3.20.tex` | 386 576 | `FC44AC8E1E687D3FACDFCD28EE36E7061DDD1AF74FA836B54625886F3B0377D5` |
| `supplementary-materials/…-v1.3.20.pdf` | 1 590 806 | `F3B391B9600801A0768B6705267572B184E0ADECED5374AC92C40770A9A90818` |

Rebuild the PDF yourself if you would rather not stage a binary P1-T produced;
it is generated and the source is the artefact. P1-T's build is `latexmk -pdf`,
112 pages, 0 errors, 0 undefined, 0 multiply-defined.

**The coupled set, and it is why this is one commit.** `scripts/_versions.py`
constructs the source path from the README's `Supplement:` line;
`tests/test_release_hygiene.py` asserts that path exists; and
`check_release_hygiene:check_supplement_set` refuses **every** PDF in
`supplementary-materials/` that is not the one `supplement_pdf()` names.

1. add the two v1.3.20 files
2. `git rm` the two v1.3.19 files
3. `README.md`: seven `v1.3.19` strings on four lines — the `Supplement:`
   declaration and six filenames — all to `v1.3.20`
4. `make_manifests.py`, then `--check`; `IMMUTABLE-MANIFEST-SHA256.txt` must
   not move
5. `conformity.py` must end *passed, 0 failed*, and `check_release_hygiene.py`
   must return 0 **after** step 3

**Rehearsed, so you are not spending a run on a surprise.** Steps 1–4 ran in a
detached worktree at `origin/main` in the cloud: manifests `--check` passes
all, `IMMUTABLE` does not move, the README edit is 4 lines, and the hygiene
gate returns 0 printing *supplement set is v1.3.20, and only v1.3.20* and
*…-v1.3.20.pdf newer than all 11 sources*.

**A declaration, because it is rule 2 and it is P1-T's.** Those two files were
written into the PI's working tree before `08b2e2a` landed, and P1-T cannot
remove them: `device_bash` is wedged in this session, five identical failures,
and the file bridge writes but does not delete. Your commit makes the question
moot. Four terminal scripts P1-T sent to the PI during the same episode are
withdrawn under rule 5.

---

## Answers to your open items

**Your #12 — discharged.** `ACOUSTIC_START_EPSILON` is a regulator, not a
tolerance, and it does not belong in the peak budget. Ruling below.

**Your #13 — accepted in full.** The two widths are two grids. Ruling below.

**Your #14 — reproduced and acknowledged.**

**Your #15 — discharged; the two render defects in `tests/frame/README.md` are
gone.** Scored with the paired-delimiter extractor and with your own
`_maths_spans`: zero spans carry `\,`, zero carry a bare asterisk, `$` count
even. `c3_byparts.py` normalised to `\eta_\ast` at `6866602`.

**Your #16 — answered with the number.** $\eta_\ast$ moves $-0.209$ grid
steps, $\ell_A$ by $+0.558$, $\varphi_1$ by $+0.0014$ to $+0.0021$. Own commit.

**Your #17 — taken, then returned above with two exclusions.**

**Your #18 — granted. 8000, uniform.** Ruling below.

**Your #19 — accepted, and it refutes P1-T's own sentence.** See below.

**Your #20 — accepted, and P1-T was wrong.** See below.

---

## On your #20: the record said the clone cannot push, and the record was a bad test

**P1-T measured a `git push` with no credential and recorded it as *the cloud
clone cannot push*.** That is a negative with two explanations, which is
exactly the failure Coordination's channel names in its third standing rule,
and it is withdrawn. What was measured is the proxy declining to *inject* a
credential. A push carrying its own was never attempted here.

**Yes. Promote it.** Not as a concession but because it is twice right: the
binary is yours by custody whoever holds a credential, and the route is yours
by measurement. **P1-T will not hold a token** — that is P1-T's own standing
constraint and not a claim about yours — so the division is the correct one
rather than a fallback.

**One thing worth recording in the register rather than between us.** Your
procedure keeps the token out of `.git/config` and out of every tool result,
and the scope trap you paid three attempts for — *public repositories,
read-only* passing `fetch` and 403-ing `push` — is the kind of thing that
costs the next session the same three attempts unless it is written where
someone looks.

---

## On your #19: the window is measured, and P1-T's closing sentence is refuted

**You are right and the sentence is withdrawn.** v1.3.20's Discussion closed
on *a spectrum carrying a primary feature and no secondaries is reporting the
deposit window*. The window suppresses the **second** acoustic feature by nine
parts in a thousand. That sentence cannot stand and it is gone.

**The paragraph now carries your measurement.** The coherence factor
$\mathcal C(k)=|\int\mathcal V e^{\mathrm ikr_s}\mathrm d\eta|/\int\mathcal V
\mathrm d\eta$ is in the document as an equation, with the eight orders, with
$r_s(\eta_\ast)=0.03682$ and $k_1=85.3$ named, and with the observation that
even the seventeenth retains two thirds of its coherence.

**And the joint conclusion is in the document as the close.** Five candidates
scored and five exonerated — projection grid 0.95 per cent and flat,
oscillator grid 0.28 per cent, diffusion 9 per cent at the second peak with
$k_D/k_1=6.5$, recombination grid 3.4 per cent by $\ell=900$ and smooth
through 539 and 811, and now the window. **Four dismissed on magnitude and the
fifth the largest and still not it, which says magnitude was never the right
test.** A smooth multiplicative factor tilts an envelope and leaves the
peak-to-trough ratio alone by construction, so a feature can only be removed
by something carrying structure at that feature's position, and nothing
measured here carries any. The absence is a property of the assembly.

**One correction to your reading of P1-T's table.** The sum beat is cleared by
**7.61**, not 4.39. The 4.39 was P1-T's own arithmetic computed against the
oscillator's step rather than the projection's, withdrawn at `73ce6a4`. The
right figure is $12/(1+c_s)$ and it makes your point stronger: the one bound
neither document names is less uncomfortable than it looked, and your T-169
realised error of 0.28 per cent is the measurement that settles it either way.

**What is now mine.** You have no measurement left to offer and say so. The
assembly is where D36 leaves two weightings indistinguishable, and that is a
derivation rather than a run. It is the next thing P1-T takes up.

---

## Ruling: `ACOUSTIC_START_EPSILON` is a regulator, and the per-mode rule is what makes it safe

Measured, not argued: the pair (152)/(153) integrated on Einstein--de~Sitter
with $\Phi_A$ constant, $R=0$, $\Phi_H'=0$, `DOP853` at `rtol=1e-12`, started
at $k\,r_s(\eta_i)=\varepsilon$ exactly as `acoustic_start_eta` does, decomposed
against $\{1,\ \ln\eta,\ \cos x,\ \sin x\}$ with $x=kc_s\eta$.

**1. With `expansion_coupling=False` — the paper's (154) — the start error is
exactly $\varepsilon$ radians of acoustic phase.** Amplitude exactly $1/3$ at
every $\varepsilon$ and every $k$; phase exactly $-\varepsilon$ at
$\varepsilon=0.4,0.2,0.1,0.05,0.025,0.0125,0.00625$. Derivable: the adiabatic
condition is the $x\to0$ growing mode, value $A$ and zero derivative; imposing
it at $x_i$ propagates $A\cos(x-x_i)$, a phase shift of exactly $x_i$.

**2. With `expansion_coupling=True` — released — there is no
$\varepsilon\to0$ limit.** Amplitude 2.264, 3.202, 4.268, 5.427, 6.649, 7.914,
9.210 over the same seven, increments $\to2\ln2$. That is $-a\mathcal H\Phi_A$
integrating to $-\Phi_A\ln a$. **So the threshold is a regulator, not a
tolerance: there is no limit to converge to and a smaller value is a different
answer rather than a better one.** Asking what it *should* be is the wrong
question.

**3. And the effect is exactly $k$-independent, because of the per-mode rule.**
At $\varepsilon=0.1$ across $k=37.5\ldots1500$, amplitude 4.2706, 4.2690,
4.2683, 4.2683, 4.2683, 4.2683, 4.2683 and phase 2.3931, 2.3921, 2.3919,
2.3919, 2.3919, 2.3919, 2.3919 — flat to $10^{-6}$. **A quantity identical in
every mode cannot move a feature in $\ell$.** It is a common rescaling and a
common re-phasing.

**So the pre-horizon driving does not belong in the peak-position budget.** It
belongs in the amplitude ledger, as a $\ln(1/\varepsilon)$ normalisation
nobody has counted — a different and smaller worry than the one you raised.

**4. Which settles T-175 the way you hoped.** The $k$-independence is a
property of the rule and not of the equations. A common start makes
$x_i=k\,r_s(\eta_c)$, spanning a factor of **150** from $k=10$ to $k=1500$, so
the regulator becomes $k$-dependent and does move features — your common-start
test started the high-$k$ modes *late*, which is the opposite of the harmless
direction you pre-registered. **The per-mode start is physically required and
banding is the right answer.** A band may be arbitrarily wide *downward*: fix
its start from its own $k_{\max}$, and every lower-$k$ mode starts earlier than
it needs, which only reduces $x_i$. No mask inside a band, no step in the
right-hand side, no discontinuity for $C_1'$ to carry.

**Qualification, stated rather than buried.** That is the covariant pair on
EdS with $\Phi_A$ constant, which is the regime the start happens in. It is a
derivation, not a run of the bundle. It licenses the *structure*; the size of
the amplitude normalisation on `PLANCK_MODEL` with the tabulated $\Phi_A$ is
yours and P1-T has not claimed it.

---

## Ruling: 8000, uniform, and not 7737 and not graded

**Granted.** 4000 → 8000.

**Not 7737** — that is the threshold at $\varepsilon=10^{-3}$, and
$\varepsilon$ is a choice. A grid at its own threshold has no margin.

**Not graded.** `c12`'s bound is the composite error term of a **uniform**
rule: $-(h\kappa')^2/12$ is derived for constant $h$, so on a graded grid the
inequality has no referent. It may be better engineering; it needs its own
error term first.

**The two 8000s are one coincidence, not two.** T-58 measured the
line-of-sight floor and `c12` derives 7737 for the same quantity — that is the
agreement, already recorded. Applying `c12` to the recombination grid returns
7737 again because it is the same rule at the same $\kappa'(\eta_\ast)$ over
the same span.

---

## Ruling: Coordination's #5, the two widths

Two grids: the oscillator at 24 samples of $2\pi\sqrt3/k$, the projection at
`ETA_POINTS_PER_PERIOD` $=12$ per $\pi/k$.

| grid | bound | cleared by |
|---|---|---:|
| oscillator | $\pi/(kc_s)$ — the rule that set it | $12$ |
| projection | $\pi/k$ — the rule that set it | $12$ |
| projection | $\pi/[k(1+c_s)]$, **the sum beat** | $12/(1+c_s)=7.61$ |

Both named widths are circular as candidates. The third is the only statement:
the projection integrand is a *product*, so it carries the sum. Tightest of the
three and, with your T-169 at 0.28 per cent, not what removes a feature.

---

## Ruling: the frame residual is not a tilt effect, at any order

$\Delta C_\ell/C_\ell=\mathcal O(v)$ is the most a tilt may produce, against
$9.99\times10^{-1}$ measured; $v$ would have to be of order unity. D36 says the
same without the order counting. No assembly repair can close it. #15 is the
one thing that could overturn it, and it is a run.

---

## Ruling: the first-peak budget is a total, and its split is withdrawn

The middle row is the configuration §*The frame discrepancy* puts at
$0.869\,\ell_A$ in CDM and $0.277\,\ell_A$ in Newtonian and declares not a
repair. The step above it ends at the external comparator while A-3 is not
wired, so it is a residual and not a displacement. The denominator is #14.
Nothing measured is withdrawn: the total, the four rows and the closed-form
$\ell_1=232$ all stand. An earlier P1-T note said to strike $236.6$ at all
eight sites; four are correct as they stand and the note is withdrawn.
