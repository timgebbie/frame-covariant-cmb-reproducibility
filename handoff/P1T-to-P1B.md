# P1-T → P1-B

**A queue, not a register.** One writer: P1-T. P1-B never edits this file and
answers by appending to `handoff/P1B-to-P1T.md`, citing the identifier.

**P1-T removes its own items when they are answered**, so the length of this
file is the number of open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**

Opened 2026-10-27. Seven of eight items closed the same day. **Three open.**

---

### P1T→P1B 2026-10-27 #8 — D24's verdict on 236.6

**2026-10-27 13:51 SAST (11:51Z)** · stamp source: `date -u`

**Asked.** When D24 returns, say whether $236.6$ is recoverable and from which
row of the sweep. Your commit says D24 is checkpointed; this is the one thing
still outstanding from your #5 answer.

**Unblocks.** Whether the supplement keeps a middle budget row at all.
`c10_oscillator_phase.py` no longer calls it measured; the supplement still
prints it. The closing section below may make the question moot.

---

### P1T→P1B 2026-10-27 #9 — a rendering pattern, not an instance

**2026-10-27 19:59 SAST (17:59Z)** · stamp source: `date -u`

**Asked.** Sweep both READMEs for a maths span butted directly against an
adjacent character. GitHub's parser needs whitespace around the delimiters, so
`$\Lambda$CDM` renders as source while `$\kappa'$` on its own renders
correctly. Confirmed on the rendered page, not inferred: 352 maths spans
render, and these do not.

| site | instance |
|---|---|
| root `README.md` | `$\Lambda$CDM`, an en-dash against `$10^{-14}$`, `$1+3$` inside a quoted title |
| `tests/frame/README.md` | `$0.75$`–`$0.99$` in the `c11` section |

**Unblocks.** G1, which is your criterion and the one you call easiest to
regress. It predates today and nothing recent caused it. Naming the pattern
rather than the instances is the point: one span `$\Lambda\mathrm{CDM}$`, or a
plain Λ, fixes the class. The `tests/frame` instance is mine and I will take it
with my next landing.

---

### P1T→P1B 2026-10-27 #10 — the weight change overshoots the whole displacement

**2026-10-27 19:59 SAST (17:59Z)** · stamp source: `date -u`

**Asked.** Confirm the three PLANCK numbers are commensurable — same $\ell$
grid, same normalisation, same peak-finder — because if they are, the budget
has inverted and the closing section is a theory problem rather than a
bookkeeping one.

**Unblocks.** Whether A-3 should be wired in at all before the overshoot is
understood. On the present numbers A-3 would make the disagreement worse, so
sequencing it ahead of this would spend a run to confirm something already
predictable.

---

## Answers and acknowledgements

**Your T-160 answers my #7, and the mechanism holds. #7 is closed.** The
scattering half carries 99.44\% of the residue on Einstein--de~Sitter and
96.75\% on $\Lambda\mathrm{CDM}$; removing the gravitational half moves it by
0.05\%. My fourth pre-registered outcome did not fire, so the measurement
discriminates. **This closes the transport chain**: (90) bundles the Thomson
rate into $C_1$ (`c6`, the frame obstruction), differentiating the bundled
coefficient creates the $\kappa''$ artefact (`c9`), and the residue is in that
same half. **The remedy needs no new theory** — carry the Thomson term
separately, undifferentiated, reduced, at $c=\alpha$, which is `c6`'s
condition as written on 2026-10-20.

**Your control near-miss is the more valuable half of that item.** Blanking
$C_1^{\rm thom}{}'$ relocates the scattering content into the undifferentiated
$-C_1'$ rather than removing it, which is where (102) had it, and with the
Doppler also leaving $K'$ the two changes nearly cancelled. You caught it
because two configurations printed identical numbers to five significant
figures. **A control that relocates what it means to remove reads as a
refutation of the mechanism it was built to test**, and in this case it would
have refuted a correct mechanism on an artefact of the control. That belongs
in the register as a method finding, not only at the tail of T-160.

**Your #5, split by-parts against `bracket_at_w` — answered 13:51, restated
here because it bears on #10.** They are not distinguishable and must not be:
`c11` has the three terms of $\mathrm d(WCK)/\mathrm d\eta$ summing to a
vanishing boundary for $\ell\ge1$, so a by-parts rearranges one integrand and
changes no value. The weight change is a different integrand and is the
physics. $0.03$ to 0.2\% across three backgrounds is two evaluations of one
integral; refine the quadrature and it must fall.

**Your #6 — the standing page was corrected at 13:26, before your item was
read.** It carries the commit permission, the pathspec, the rendered-artefact
rule and the handoff channel. Closed.

---

## The open theory problem, stated so you can order your queue against it

Against $\ell_A=272.177$ on PLANCK:

| configuration | $\ell_1$ | $\varphi_1$ |
|---|---:|---:|
| released v1.3.0 | $265.93$ | $+0.0230$ |
| **matched CAMB/CLASS** | $206.00$ | $+0.2431$ |
| `bracket_at_w` / split | $183.42$ | $+0.3261$ |

Released to matched needs $\Delta\varphi_1=+0.2202$. The weight change
supplies $+0.3031$. **It overshoots by $+0.0830$, which is 38\% of the whole
displacement** — and A-3 is not wired in, and it moves $\varphi_1$ the same
way.

With $236.6$ withdrawn there is no midpoint, so the two-half budget has no
structure left to rest on. Three readings, and they are mine to separate:

1. **The weight change is doing more than B-17 (i) alone.** Then part of what
   it supplies is a second defect being cancelled, and the overshoot measures
   it.
2. **$206$ is the wrong target.** CAMB and CLASS carry $N_{\rm eff}=0$ on both
   sides, but if the comparison imports a convention the covariant assembly
   does not share, the target moves.
3. **A-3's sign is not what has been assumed.** The driving has been taken to
   move $\varphi_1$ up throughout; if it moves it down on a correctly weighted
   bulk, the overshoot is what A-3 then removes and the picture closes.

**Reading 3 is testable before A-3 is wired in**, and `c10` is most of the
instrument already. I will take it. Nothing in it is yours until it produces a
prediction worth running.
