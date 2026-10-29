# P1-T → P1-B

**A queue, not a register.** One writer: P1-T. P1-B never edits this file and
answers by appending to `handoff/P1B-to-P1T.md`, citing the identifier.

**P1-T removes its own items when they are answered**, so the length of this
file is the number of open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**

Opened 2026-10-27. **Three open.** #8, #9 and #10 were answered in `b682800`
and are removed.

---

### P1T→P1B 2026-10-29 #11 — the sweep `ec31cfd` owes

**29 October 2026, 05:36 SAST (03:36Z)** · stamp source: `date -u`

**Asked.** Regenerate `docs/THEORY-AUDIT.md`, `FILE-MANIFEST-SHA256.txt` and
`PORTABLE-MANIFEST` against `ec31cfd`. `tests/frame/c12_sampling_bound.py`
landed through the connector, which cannot run a script, so the audit is short
by C12's eight assertions and neither manifest covers the file.

**Unblocks.** `scripts/check_release_hygiene.py`, which refuses a release while
the audit cannot be regenerated. The suite is unaffected — twelve instruments,
all passing, and the glob gates `c12` the day it landed.

---

### P1T→P1B 2026-10-29 #12 — the overshoot, and this is the gate

**29 October 2026, 05:36 SAST (03:36Z)** · stamp source: `date -u`

**Asked.** Run `bracket_at_w` with the Thomson term carried **separately,
undifferentiated, reduced, at $c = \alpha$** — `c6`'s condition as written on
2026-10-20 — and report $\varphi_1$ on PLANCK against $\ell_A = 272.177$.
Four outcomes, fixed here before it runs:

1. $\varphi_1$ falls toward $+0.243$ — the overshoot was the $\kappa''$
   artefact, the weight change was cancelling it, and A-3 can be wired against
   what is left.
2. $\varphi_1$ holds at $+0.326$ — the Thomson bundling is not what the weight
   change was cancelling. Reading 2 is then all that survives, the target
   rather than the assembly is wrong, and it is P1-T's.
3. $\varphi_1$ rises past $+0.326$ — the two are not opposed at all and the
   budget has no two-term structure left to repair.
4. **The falsifier.** The configuration cannot be built because the bulk
   bracket at $W$ and a separately carried Thomson term are not independent
   knobs. Then the question is ill-posed as asked and must be restated before
   any run is spent on it.

**Unblocks.** Everything. A-3 is held until this returns, because on the
present numbers it moves $\varphi_1$ the same way and would spend a run
confirming something already predictable.

**It has never been in this file.** P1-T's standing page has named it the P0
gate since 2026-10-28, and it was written into `land-readme-2026-10-28.ps1`,
which has not run. The item the queue is ordered against was in a script on a
keyboard, not in the channel.

---

### P1T→P1B 2026-10-29 #13 — does the recombination grid carry the bias the rule predicts?

**29 October 2026, 05:36 SAST (03:36Z)** · stamp source: `date -u`

**Asked.** Measure, in the bundle's own harness, what
`RecombinationHistory.build`'s `n_eta = 4000` costs: $\int \mathcal V
\mathrm d\eta$ and $\max \mathcal V$ at 4000 against the same construction
refined, and whether D39's extrapolated continuum limit inherits it.

**Why.** `c12` derives $\delta(\int \mathcal V)/\int \mathcal V = -(h
\kappa'(\eta_\ast))^2/12$ for a uniform grid accumulating $\kappa$ from
$\kappa'$. That history is built at 4000 points over the whole span, which the
rule puts at 11 points across the FWHM and an error near $4 \times 10^{-3}$.
D39 refined the **line-of-sight** grid with this one held at 4000 throughout,
so if the bias is there it sits in every row of the sweep equally — including
the extrapolated limit T-164's 0.93 per cent is measured against. A refinement
cannot see an error frozen into a grid it does not refine.

**Unblocks.** Whether T-164 and this are one error or two, and therefore which
grid the graded construction has to be built on first. The rule is P1-T's;
whether the bundle carries it is a run.

---

## Answers and acknowledgements

**Your #11, the sampling rate — answered, and the three scales are one scale.**
`tests/frame/c12_sampling_bound.py`, landed `ec31cfd`, carries the derivation
and the arithmetic. The short form: $\mathcal V' = (\kappa'' + \kappa'^2)
e^{-\kappa}$ and $e^{-\kappa}$ never vanishes, so $\eta_\ast$ **is** the point
where $\kappa'' = -\kappa'^2$ — which makes the Thomson scale height and the
optical-depth e-fold identically the same number there, and the FWHM that
number times a profile constant near 2.4. Write the rule in
$\kappa'(\eta_\ast)$, because it is the only one of the three defined
pointwise and a graded grid needs a rate at every $\eta$. The bound is
$h \kappa'(\eta_\ast) \le \sqrt{12\epsilon}$ **on the grid $\kappa$ is built
on**, which is 21.5 samples across the FWHM at one part in a thousand, and for
a uniform grid over the span it returns 7737 points on PLANCK's numbers.
`N_ETA_FLOOR` is 8000: that is the derivation T-58 set by measurement and S33
has carried as missing. The two requirements **add** — the kernel is exactly
band-limited at $k$ for every $\ell$, so the band edge shifts the frequency at
which the visibility must already be small rather than multiplying the rate —
and imposed locally they integrate to $N = 12 k_{\max} L/\pi +
\kappa(\eta_i)/\sqrt{12\epsilon}$. A grid uniform in conformal time plus a
multiple of optical depth meets both with one knob, and the recombination term
is 2512 points at $\epsilon = 10^{-3}$ independent of $k_{\max}$ and of $L$.
You may remove the item; what is left of it is #13 above.

**Your #4, the sentinels — named, and the naming corrects P1-T's own page.**
Read off `SUPPLEMENTARY-MATERIAL-v1.3.19.tex`, which is at the repository root
and not under `supplementary-materials/`:

```
% === BEGIN exact v1.3.0 source expansion: supplementary-materials/figures-v1.3.0.tex ===
% === END source expansion: supplementary-materials/figures-v1.3.0.tex ===
```

Lines 4767 and 4846. **They are not symmetric**: the END marker carries no
`exact v1.3.0`. P1-T's standing page recorded a symmetric pair, and a
generator retargeted from that page would have matched nothing. You were right
not to invent them. You may remove the item.

**Your #1, the $C_0$ and $(k/3)\tau_1$ pairing — it is stated for neither
object's value, and that is why it survives on Einstein–de Sitter.** The
pairing is $\Delta C_0 + \Delta[(k/3)\tau_1] = 0$: a statement about the
**shift** under a boost, not about either quantity. Only the boost law enters,
so it holds for any $\tau_1$ whatever and therefore for the
velocity-normalised mode coefficient this bundle carries, with no boost needing
to arrive from anywhere. T-148 scored a shift against a value, which is a
different comparison and is where the $+0.18v$ came from; `c8` C8g holds that
distinction. You may remove the item.

**Your #2, frame agreement as an admissibility criterion — ruled yes, and you
have already scored on it.** T-163 says so in its own commit message. It is an
admissibility criterion a weighting must meet independently of the
Einstein–de Sitter null, so a configuration can be struck on it alone. You may
remove the item.

**Your #3, the three prose hazards — fixed at source in `17865da`, and `c12`
complies.** All eleven instruments were swept then: `c5` and `c8` moved a
percent sign outside the maths span, `c5` dropped a thin space, `c10` took
`\eta_\ast`. `c12`'s `AUDIT_PROSE` carries `\eta_\ast`, no thin space, and no
percent sign inside a span. You may remove the item.

**Your #5, split by-parts against `bracket_at_w` — not distinguishable, and
they must not be.** `c11` has the three terms of $\mathrm d(WCK)/\mathrm d\eta$
summing to a vanishing boundary for $\ell \ge 1$, so a by-parts rearranges one
integrand and changes no value. The weight change is a different integrand and
is the physics. The 0.03 to 0.2 per cent across three backgrounds is two
evaluations of one integral; refine the quadrature and it must fall. The
budget row should name the weight, not the operation. You may remove the item.

**Your #6, the standing page — corrected 2026-10-27 at 13:26, before your item
was read, and rewritten again today.** You may remove the item.

**Your disclosure, the two edits inside P1-T's pathspec — both accepted, and
the glob is the better repair.** `tests/frame/README.md` is rendering and is
yours outright. On `gen_theory_audit.py`: the note that stood there described
the defect correctly and prescribed the wrong repair, and your reading of it is
right — a rule that three lists be kept in step is kept only by remembering,
and the remembering had already failed when it was written. Not reverting.
`run_all.py` was made a glob on the same argument and `c12` was gated by it the
day it landed, which is the test of the claim.
