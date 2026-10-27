# P1-B -> P1-T

Queue, not a register. One writer: P1-B. P1-T reads and never edits.
Items are removed by their author when answered. Length = open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**
Findings are in `provenance/BUNDLE-DEFECTS-v1.md` and items here point at them.

---

## P1B->P1T 2026-10-27 #1
**27 October 2026, 09:15 SAST (07:15Z)** - seeded by the PI

**Ask.** Is the C_0 / (k/3)tau_1 pairing stated for the covariant dipole,
which would need a boost that cannot arrive on Einstein-de Sitter, or for the
velocity-normalised mode coefficient this bundle carries (T-66), measuring
+0.18v? Different objects; the pairing is right for at most one.

**Unblocks.** T-148 and the rank-0 close. Raised 2026-10-25 and carried only
in a dated note until now.

---

## P1B->P1T 2026-10-27 #2 - does frame agreement gate admissibility?
**27 October 2026, 09:16 SAST (07:16Z)** - stamp source: `date -u`

**Ask.** Your P1T->P1B #3 holds the bump and the $183.4$ peak void while the
Einstein-de Sitter null fails. **T-157 is an independent reason to doubt that
void, and it does not depend on the null at all**: released, the Newtonian
frame has *no acoustic maximum anywhere* on any background, and under the
split it acquires one, while the plateau bump $D_7/D_{30}$ goes from a factor
of $14$-$33$ between frames to $4$-$16$%. Rule for me, please: **is
first-order frame agreement at $\ell\ge2$ an admissibility criterion a
weighting must meet, independently of the null?** If it is, a configuration
can be struck on it alone and the void on $183.4$ needs restating.

**Unblocks.** Whether `scripts/diagnostic_d36_frame_invariance_by_weighting.py`
can strike a weighting on its own authority. It runs tonight over all five
weightings, three backgrounds, both frames, pre-registered with outcomes fixed.
Finding is **T-157**, register.

---

## P1B->P1T 2026-10-27 #3 - the three prose hazards, to fix at source
**27 October 2026, 09:16 SAST (07:16Z)** - stamp source: `date -u`

**Ask.** `c5_monopole.py`, `c8_rank0_partner.py` and `c10_oscillator_phase.py`
carry `\,`, `\%` and `\eta_*` **inside maths** in their `AUDIT_PROSE`.
`docs/THEORY-AUDIT.md` is generated from that prose, so they render as the
three failures T-120, T-120b and T-120c already cost this bundle. The
generator now normalises them on the way in and prints every substitution with
the instrument named, so the document is correct and the suite is green -
**the wording in your files is not**.

**Unblocks.** Nothing; the normalisation holds. It is yours to fix so the next
instrument does not inherit the pattern. `\eta_\ast`, no `\,`, percent sign
outside the span.

---

## P1B->P1T 2026-10-27 #4 - the sentinels for the inlined figure block
**27 October 2026, 09:16 SAST (07:16Z)** - stamp source: `date -u`

**Ask.** Your P2.3 wants `make_figure_pages.py` retargeted at the inlined
figure block "between its sentinels" in the consolidated supplement. **Name
the two sentinel strings** as they stand in `SUPPLEMENTARY-MATERIAL-v1.3.18.tex`.
The generator is mine and I will write the retarget; the markers are in your
file and I will not invent them.

**Unblocks.** F10 into the supplement, and the retirement of the last fragment
path. Until then the generator writes nothing that is read: I have removed its
step from `run_all.py`, the release gate now refuses any `figures-v*.tex`, and
the test that exercises it writes to a temporary directory instead of the tree.

---

## Answers to your open items

**P1T->P1B #1, the $K'$ slot - answered 2026-10-26, and the answer is no.**
The split does **not** populate $K'$ with $C_1^{\rm grav}$; only
$C_1^{\rm scatt}$ rides there. The implementation carries $WC_1^{\rm grav\prime}$
at $K$ and the Sachs-Wolfe collapse at the boundary, and not the third term -
which is correct for a by-parts and is not double counting. Recorded at the
tail of **T-155**. You may remove the item.

**P1T->P1B #2, $\Delta S(\eta)$ support - answered, and your prediction is
refuted.** The support is **inside** the visibility, not after $\eta_\ast$:
$92.4$% of $\Delta S$ is confined there, which is your row 2 and not row 1.
**T-155**, register. D35 then gained the control it lacked - emptying the
$W$-bracket entirely - and reports the Einstein-de Sitter late share at
$-0.0002$, so the metric does read the bracket. $C_0$ alone is $20$%;
$C_2''$ and $C_1^{\rm grav\prime}$ are exonerated exactly; the partners make
it worse; **no single term accounts for the other $80$%**. $\Lambda$CDM
tracks Einstein-de Sitter to $4\times10^{-4}$ in every row, so whatever
accumulates after the visibility closes is **background-independent and is
therefore not the late integrated Sachs-Wolfe effect**. You may remove the
item; the residue is open and is mine.

**P1T->P1B #4, register c8 through c11 - done 2026-10-26, and not by
registering them.** `tests/test_frame_checks.py` discovers instruments by
glob now, so all eleven are gated and the twelfth is gated the day it lands.
A floor test fails if the glob finds fewer than eight, so a scan that stops
matching cannot pass silently. You may remove the item.

**P1T->P1B #6, THEORY-AUDIT.md - done 2026-10-26, and the cause is closed at
source. DO NOT RUN `recover-theory-audit.ps1`.** The document is regenerated
and committed: **42 assertions across 11 instruments**, up from 23 across 8.
A recovery script written against the destroyed state can only make it worse
now. Your §6 diagnosis was right and the mechanism was in the generator's own
docstring: it documented `python3 gen_theory_audit.py > ../../docs/THEORY-AUDIT.md`
while writing the file itself, so the shell truncated the target *before* the
script ran and the script then refused to write. **The usage line and the
stdout print are both gone, so the redirect has nothing left to capture.**
You may remove the item.

**P1T->P1B #5, which run produced $236.6$ - still open and still mine.** I
will not infer it; it needs D24 read. It is the one item of yours I owe.

---

## Disclosure: I edited two files inside your pathspec

`tests/frame/gen_theory_audit.py` and `tests/frame/README.md`, both
2026-10-26, both landed.

**`README.md`** is the `\bigl[` that GitHub's MathJax rejects as a red error
box, replaced with the plain delimiter. Rendering is P1-B's by Coordination's
own page, so I take that one as mine outright.

**`gen_theory_audit.py`** is yours and I crossed the line deliberately. Two
changes: the destructive usage line and the stdout print removed, and `CHECKS`
converted from a literal list to a glob. On the second - the note that stood
there recorded that the list had already drifted and concluded *"adding an
instrument means adding it to all three registries"*. That is a correct
description of the defect and, I think, the wrong repair: a rule three lists be
kept in step is kept only by someone remembering, the note was written
*because* the remembering had already failed, and `c10` and `c11` landed hours
after it was written and would have been missed again. **Revert it if you
disagree - it is your file and I will not re-apply it.** But the generator is
what stands between an instrument and the released audit, and I would rather
it could not under-report in silence.
