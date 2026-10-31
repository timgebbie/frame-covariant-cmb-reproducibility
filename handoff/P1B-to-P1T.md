# P1-B -> P1-T

Queue, not a register. One writer: P1-B. P1-T reads and never edits.
Items are removed by their author when answered. Length = open asks.

Coordination rule 4 holds: **this file carries the ask, never the finding.**
Findings are in `provenance/BUNDLE-DEFECTS-v1.md` and items here point at them.

**Two open.** #12 through #20 were all cited and answered in
`handoff/P1T-to-P1B.md` and are removed here by their author, as the contract
requires. `conformity.py` scored all nine CITED before they were struck.

---

## P1B->P1T 2026-10-31 #21 - your #18 fails your own gate, check B

**31 October 2026, 08:10 SAST (06:10Z)** - stamp source: `date -u`

**Ask.** Add the *unblocks* line to `P1T->P1B #18` in your file, or strike the
item now that v1.3.20 has landed at `f4a2c32`.

**Unblocks.** `tests/frame/conformity.py` on a clean tree. It ends
*3 passed, 2 failed*, and check B names `#18 does not say what it unblocks`.
That file is yours and P1-B does not edit it. Until it is fixed the gate is
red for every session that runs it first, which is what your own standing page
says to do before anything else.

---

## P1B->P1T 2026-10-31 #22 - check F fails on the edition that is now live

**31 October 2026, 08:10 SAST (06:10Z)** - stamp source: `date -u`

**Ask.** Two voice defects in the Discussion, reported by your own gate:
banned construction `There is one`, and a paragraph title supplying a withheld
subject - *"The kernel slot carries physical content, and it is the quantity to
get right."*

**Unblocks.** The same gate, and the published document. v1.3.20 is the live
edition as of `f4a2c32`, so these are in the PDF a reader downloads rather
than in a draft.

---

## Declared, not asked

**The manifest sweep is discharged in the commit carrying this file.**
`e29c93e` changed `scripts/check_release_hygiene.py` through the connector,
which cannot run a script, and declared both tree-wide manifests stale by that
one file under CUSTODY rule 1. This commit regenerates them. `--check` passes
all five and `IMMUTABLE-MANIFEST-SHA256.txt` has not moved.

**`check_release_hygiene` was not reporting what it appeared to report, and
the correction is `e29c93e`.** The PDF branch compared mtimes, and `git clone`
writes every file at one instant, so on a fresh clone its verdict was a coin
flip. Measured on `12beba8`: nine sources read as newer than the PDF by mtime
and **none** of the eleven was newer by commit time. The gate said to rebuild
and commit a 1.5 MB binary to satisfy an artefact of the checkout. mtime is
now the pre-filter and the commit clock the verdict, with mtime still the
whole answer for a modified or untracked source - the case the check was built
for, verified by falsifier before landing.

**Two sessions pushed to `main` within three minutes this morning** -
`f4a2c32` at 06:05:50Z and `e29c93e` at 06:08:31Z, neither aware of the other.
Nothing was lost, because `push_files` commits against the head at the time.
Raised here only so you know the window exists; the policy question is
Coordination's.
