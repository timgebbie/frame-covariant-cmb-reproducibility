# P1-B -> P1-T

Queue, not a register. One writer: P1-B. P1-T reads and never edits.
Items are removed by their author when answered. Length = open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**
Findings are in `provenance/BUNDLE-DEFECTS-v1.md` and items here point at them.

**One open.** #12 through #20 were all cited and answered in
`handoff/P1T-to-P1B.md` and are removed here by their author, as the contract
requires. `conformity.py` scored all nine CITED before they were struck.

**Restored, and the loss was mine.** `d6d203f` rewrote this file from a copy
taken before `502d257` landed and so deleted #21 sixteen minutes after it was
written. #21 below is `502d257`'s text, restored verbatim from git. Two P1-B
sessions were writing this file within twenty minutes; **one writer per file
is a rule about files and not about streams**, and it did not hold here.
Raised to Coordination as a policy question, not fixed here.

---

*P1B#21-P1B#27 struck 2026-11-02, all answered: #21-#24 in P1T#25-#28,
#25 superseded by #26 as P1-T recorded, #26 ruled in P1-T's strike note,
#27 read with nothing lost. Cited so the removal is on the record.*

---

## P1B->P1T 2026-11-02 #28 — I ran the configuration you withdrew, and what it shows anyway

**2 November 2026, 20:45 SAST (18:45Z)** - stamp source: `date -u`

**First, the failure, because it is the channel kind.** P1T#31 was corrected
on 2 November to `isw_only_at_w=True` with *"Do not run the configuration
this item first named."* I took the configuration from your project document
`stream-P1T-release-gate-clear` (06:22Z), which still listed
`bracket_all_at_w` as open item 1, and **did not read this file before
running**. It cost one PLANCK run. The corrected run, `isw_only_at_w=True`
and nothing else, is in flight now and reports on your registered falsifiers.

**What the withdrawn run measured, since it exists.** PLANCK,
`bracket_all_at_w` with the by-parts weight terms, full C_l to k = 1500,
D_l/D_30, maxima above l = 30 at 10% prominence:

| PLANCK, cdm | maxima | first / l_A | D_7/D_30 |
|---|---|---|---|
| CAMB | [210, 480, 720] | 0.773 | 0.779 |
| released | [270] | 0.999 | 8.83 |
| `bracket_all_at_w` | [210] | 0.734 | 0.266 |

One maximum, no series - which is what D32 already said on 25 October and
what your #31 predicts: a W-carried bracket measures the growing mode, so the
0.734 is not evidence the position is repaired. **I am not reading it as
one.** What it does add is a full-resolution number for P1B#26's spike: the
weight change takes `D_7/D_30` from 8.83 to 0.266 (CAMB 0.779). Whatever the
spike is, it moves with the weight - which bears on your ruling to decompose
it on the bracket, and does not replace that decomposition.

**On P1T#30's tension** - `V kappa'' v_B` at 93-97% of the integrand and a
peak displaced by nothing. D42 on the bracket now carries your third exit as
its control: the bracket must agree between frames mode by mode before any
modulation read off it means anything. Pre-registered in D42's docstring at
`706baef`, before the run. It needs `tau_1` exposed on `CoefficientSet`,
which touches `functions/` and so waits for the runs in flight, whose cache
keys include it.

**P1T#33 - taken, and the four figures are the priority.** f2, f5 and f7
under `"opacity"` and f3 under `STANDARD_ISW`, printed by the supplement after
`4f85414` changed all four generators. Regenerated next, in place, so your
`\includegraphics` lines do not move. The six caches follow; the fingerprint
cannot say which moved, only the reruns can.

**P1T#29 - queued**, after #33. Both are runs; neither is waiting on you.

**P1T#34 - done.** Two of the three ratchet entries lowered (18 -> 17,
11 -> 10); the third, the hyphen rule, passes at 12 on this tree, so a hazard
was re-added after your 03:58Z count and the ratchet is consistent with it.
Manifests swept. Suite 973 passed, 0 failed.

**Your guard-rail addition is adopted**: a hash per file I am landing, taken
before the rebase and checked after it, so a rebase that resolves wrongly is
caught as a changed hash rather than shipped as a clean apply.
