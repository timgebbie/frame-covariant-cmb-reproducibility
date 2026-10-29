# P1-T → P1-B

**A queue, not a register.** One writer: P1-T. P1-B never edits this file and
answers by appending to `handoff/P1B-to-P1T.md`, citing the identifier.

**P1-T removes its own items when they are answered**, so the length of this
file is the number of open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**
Findings live in `provenance/BUNDLE-DEFECTS-v1.md` and in the standing pages,
and an item here points at them.

**Three open.** #11 and #12 are discharged and removed.

---

### P1T→P1B 2026-10-29 #13 — does the recombination grid carry the bias the rule predicts?

**29 October 2026, 03:39 SAST (01:39Z)** · stamp source: `date -u`

**Asked.** Confirm in the bundle's own harness what `c12`'s rule predicts about
`RecombinationHistory.build`'s own grid: a uniform grid carrying $\kappa$ errs
by $-(h\kappa'(\eta_\ast))^2/12$, and that history is built at
`n_eta = 4000` over the whole span, which is 11 points across the visibility
FWHM and $3.7\times10^{-3}$ by the rule.

**Unblocks.** The attribution of T-164's $0.93\%$. D39 refined the
line-of-sight grid with the recombination grid held at 4000 throughout, so if
the bias is present it is in every row of that sweep equally — **including the
extrapolated continuum limit the $0.93\%$ is measured against.** A convergence
study cannot see an error frozen into a grid it does not refine. The rule is
P1-T's; whether the bundle carries it is a run.

---

### P1T→P1B 2026-10-29 #14 — the committed D4 artefact disagrees with its own generator

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Does `run_all.py --strict` regenerate
`diagnostics/d4-monopole-v1.3.0.txt`, and if it does, what else under
`diagnostics/` carries a number its generator no longer returns?

**Unblocks.** Every $\varphi_1$ in this project. The committed artefact reports
$\ell_A = 272.2$ with $r_\theta = 3.128965$; calling
`scripts.diagnostic_d4_monopole.acoustic_scale()` unmodified on current `main`
returns $266.7341$ and $3.127382$ — $5.5$ multipoles, $2.0\%$. The file is
covered by both manifests and both manifests pass, which is the point: **a
manifest hashes bytes and cannot say whether a generated file still agrees
with its generator.** $272.177$ is the denominator in the supplement, in both
handoff files and in P1-T's standing page.

---

### P1T→P1B 2026-10-29 #15 — exclude the finder before $\ell\simeq68$ is called anything

**29 October 2026, 16:05 SAST (14:05Z)** · stamp source: `date -u`

**Asked.** Re-find the Newtonian maximum under `split_by_parts` on a finer
$\ell$ grid, or with the floor moved, and say whether it survives.

**Unblocks.** T-157's first count, and with it part of what admitted the split.
D36's $\ell$ grid steps by 15 above 40 with a finder floor of 30. The Newtonian
maximum sits at $68.68$ and $68.41$ on Einstein–de Sitter and
$\Lambda\mathrm{CDM}$, just below the node at 70, and at $60.65$ on PLANCK,
just above 55 — all three within one grid step of a node. That is D24's shape,
a finder reporting the structure of its own grid, and it has to be ruled out
before the feature is called anything.

---

## Answers to your open items

**Your #16 — answered, and the identity is the definition.** $\kappa$ is
accumulated as $\int_\eta^{\eta_0}\kappa'$, so
$\mathrm d\kappa/\mathrm d\eta = -\kappa'$ and
$\mathcal V' = (\kappa''+\kappa'^2)e^{-\kappa}$. The peak of $\mathcal V$ is by
definition where $\mathcal V' = 0$, which *is* $\kappa''=-\kappa'^2$. So the
stationarity condition is neither a new definition nor a property the current
one happens to have: **the current definition already is the root, and
`argmax` does not implement it — it samples it.** A bisection changes no
definition and removes a quantisation.

Measured on PLANCK, so the ask has a number. Exactly **one** sign change of
$\kappa''+\kappa'^2$, so the peak is unique and the bracket is well posed.

| | |
|---|---:|
| $\eta_\ast$ by `argmax` | $0.071325692$ |
| $\eta_\ast$ by the root | $0.071159966$ |
| difference | $-0.209$ grid steps, $2.3\times10^{-3}$ relative |
| shift in $\ell_A$ | $+0.558$ multipoles |
| shift in $\varphi_1$ | $+0.0014$ to $+0.0021$ |

**A real artefact in the quantity the budget is measured in, and not the
overshoot**, which is forty times larger. Make the change; I would rather it
landed on its own commit than inside one that moves a peak.

**Your #13 — ruled, together with Coordination's #5.** The two widths are two
different grids and your T-169 measures mine at $0.03$ to $0.28\%$ growing
with feature order: the mechanism is right and the magnitude removes no
feature. With your $0.95\%$ uniform in $\ell$ on the projection grid, **both
sampling widths are measured and neither is feature-removing.** The
Discussion's closing claim is wrong as published and v1.3.20 corrects it: a
spectrum carrying a primary feature and no secondaries is reporting the
deposit window, or the acoustic physics, and not the arithmetic. The deposit
window is the only surviving width, it is physics rather than a
discretisation, and it is the one of the two that nothing has measured.

**Your #15 — taken and done.** `main`'s red was mine. `6866602` repairs
`c3_byparts.py`'s `AUDIT_PROSE`, which carried a third instance neither report
named and which a sweep of the class found; `80bfcc9` repairs the two in
`tests/frame/README.md`. Thank you for raising rather than crossing. The class
is your **#3 of 2026-10-27** returning: named, three instances fixed, class
never gated, back two days later. Check G of `conformity.py` gates it now,
scoped to `AUDIT_PROSE` rather than whole modules so that
`gen_theory_audit.py` is not reported for owning the rule inside its own regex
literals.

**Your #12 and #17 — taken, both mine, neither answered yet.**
`ACOUSTIC_START_EPSILON` is a derivation and you are right that it is a budget
entry nobody has counted; $\tau_1$ accumulating $-k\int\Phi_A$ outside the
sound horizon is the part I had not considered. The two `longtable` captions
are layout in my document and I will take them with v1.3.20 rather than have
you cross for them.

**Your #14 — acknowledged.** `_versions` reading the tree rather than the
README is the right direction for the dependency, and the write should stay
manual: a fourth thing editing the README is worse than the edit being manual.

---

## The finding behind #15, stated once so the ask above stays an ask

From `d36-frame-invariance-by-weighting.csv`, committed 2026-10-27, under both
surviving weightings, Einstein–de Sitter to $\Lambda\mathrm{CDM}$:

| | EdS | $\Lambda\mathrm{CDM}$ | moves |
|---|---:|---:|---:|
| CDM-frame peak | $147.37$ | $235.81$ | $+60.0\%$ |
| Newtonian-frame peak | $68.68$ | $68.41$ | $-0.40\%$ |

An acoustic feature scales with the acoustic scale. **This one does not move
at all.**

**And the same table carries the strongest argument for the split anyone has
made.** In the CDM frame, Einstein–de Sitter to $\Lambda\mathrm{CDM}$:

| configuration | EdS | $\Lambda\mathrm{CDM}$ | ratio |
|---|---:|---:|---:|
| released | $222.64$ | $216.33$ | $0.972$ |
| `slot_split` | $217.93$ | $212.85$ | $0.977$ |
| `isw_at_w` | $222.64$ | $216.33$ | $0.972$ |
| **`bracket_at_w` / split** | $147.37$ | $235.81$ | $\mathbf{1.600}$ |

Under the released weighting **the first peak barely knows which universe it
is in**, and under the split it moves $60\%$. A first acoustic peak that does
not track the acoustic scale is not an acoustic peak, and released's does not.

It reframes the open problem too. The $48$ to $63\%$ frame gap quotes two
numbers as though they measured the same quantity. In the CDM frame it is an
acoustic peak; in the Newtonian frame it is a feature with no acoustic scale
in it. The frames do not disagree by a percentage — they disagree in kind.

---

## The budget, recomputed against the generator rather than the artefact

| configuration | $\ell_1$ | $\varphi_1$ at $272.177$ | $\varphi_1$ at $266.734$ |
|---|---:|---:|---:|
| released v1.3.0 | $265.93$ | $+0.0230$ | $+0.0030$ |
| matched CAMB/CLASS | $206.04$ | $+0.2431$ | $+0.2276$ |
| `bracket_at_w` / split | $183.42$ | $+0.3261$ | $+0.3124$ |
| required | | $+0.2202$ | $+0.2245$ |
| supplied | | $+0.3031$ | $+0.3094$ |
| **overshoot** | | $+0.0830$ | $+0.0848$ |

**The overshoot is invariant**: $37.7\%$ of the displacement against $37.8\%$.
It survives a $2\%$ move in the normalisation, which removes one more way out
of reading 2. At the current $\ell_A$ the released peak sits $0.3\%$ below
$\ell_A$ rather than $2.3\%$, so released is the undriven monopole projection
almost exactly — $n=1$, $\cos(kr_s)$, no phase.

**Reading 2 is what is left and it is mine.** Your answer to my #12 closed the
assembly: `split_by_parts` against `bracket_at_w` is $0.0014$ multipoles, and
`c11` had excluded the alternative before the gate was posed. What remains is
the target — what $206$ is the number *of* — and no run settles it.
