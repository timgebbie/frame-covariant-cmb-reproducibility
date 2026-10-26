"""P1-T's frame instruments, run under the bundle's own harness.

**Landed 2026-10-19.** `tests/frame/` is six self-contained instruments behind
the frame-covariance conditions, supplied by P1-T, plus the generator that
turns them into `docs/THEORY-AUDIT.md`. **No project code is imported by any
of them** --- each builds its own visibility, kernel and boost potential, so
the suite cannot agree with the solver by construction. That independence is
the point and this shim must not compromise it: it runs each instrument as a
**subprocess with `-I`**, exactly as `run_all.py` does, rather than importing
it into this process.

**Marked `verification`.** Every assertion is a condition on the functional or
on the matching. None is a claim about the spectrum --- that boundary is the
first section of the instruments' own README and of the generated document,
and it is the boundary that failed repeatedly this week in both directions.

**On the `defect` polarity**, which `tests/frame/_common.py` implements and
which C3b uses: an instrument may assert that a defect in the *antecedent* is
still present. It prints `DEFECT PRESENT` and passes; it prints `DEFECT GONE`
and **fails deliberately**, because a generated document asserting a defect
that has since been fixed is worse than no document. The bundle already has
this pattern --- `test_T14_the_transfer_function_is_NOT_frame_invariant...`
and `c0_from_printed_89` both pin known defects --- so the convention is not
new here, only its naming.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

FRAME = Path(__file__).resolve().parent / "frame"
CHECKS = [
    "c1_identity.py",
    "c2_weight.py",
    "c3_byparts.py",
    "c4_rank_slot.py",
    "c5_monopole.py",
    "c6_thomson.py",
    "c7_kappa_ledger.py",
]


#: **Each instrument is run ONCE per session and its record cached here.**
#:
#: **Streamlined 2026-10-25, and it is a cost finding rather than a
#: correctness one.** This file was 58 s of a 105 s suite because the
#: Thomson-floor test re-ran `c4`, `c5` and `c6` as fresh subprocesses that
#: `test_frame_instrument` had already run — the same three instruments,
#: twice, 27 s of pure duplication.
#:
#: **Nothing about the independence changes.** Each instrument is still a
#: subprocess under `-I`, still with `cwd=FRAME`, still importing no project
#: code — which is the whole argument of this file and must not be traded for
#: speed. What is removed is the second invocation of an identical command,
#: not the isolation of the first.
_RUNS: dict[str, subprocess.CompletedProcess] = {}


def _run(check: str) -> subprocess.CompletedProcess:
    """The instrument's completed run, computed once and reused."""
    if check not in _RUNS:
        _RUNS[check] = subprocess.run(
            [sys.executable, "-I", str(FRAME / check)],
            cwd=FRAME, capture_output=True, text=True)
    return _RUNS[check]


@pytest.mark.verification
@pytest.mark.parametrize("check", CHECKS)
def test_frame_instrument(check):
    """Each instrument exits 0 only if every assertion in it holds."""
    run = _run(check)
    assert run.returncode == 0, (
        f"{check} failed.\n"
        f"--- stdout ---\n{run.stdout}\n--- stderr ---\n{run.stderr}"
    )
    assert "##RESULT##" in run.stdout, (
        f"{check} produced no machine-readable record; "
        f"`gen_theory_audit.py` reads that line and cannot generate without it."
    )


@pytest.mark.verification
def test_the_thomson_floor_is_the_same_number_in_three_instruments():
    r"""**M11a, as a worked instance rather than a maxim.**

    (`M` is the method-failure series, renamed from `V` at T-79 so the letter
    is free for `provenance/DECISIONS-v1.0.0.md`'s released visual grammar.
    Numbers are unchanged: `V11a` is `M11a`.)

    C4's residual floor at $\beta=-\alpha,\gamma=0$, C5's at $\gamma=0$ and
    C6's gravitational-only column are **the same number** --- it is the
    Thomson term, which none of those three functionals carries. Only C6's
    $c=\alpha$ removes it, dropping the residual by ten orders.

    So three of the four conditions together leave $\sim9\times10^{-3}$ and
    all four give $\sim3\times10^{-13}$: **no proper subset works**, and a
    one-at-a-time ablation would have scored each of the four as a failed fix.
    That is exactly the method failure T-77 recorded from the other side, and
    asserting it here keeps the instance from being lost to prose.
    """
    import json
    import re

    def metrics(check):
        # `_run` is the cache: these three have already been run by
        # `test_frame_instrument` in any full-suite pass, and are run on
        # demand when this test is selected alone.
        rec = re.search(r"^##RESULT## (.*)$", _run(check).stdout, re.M)
        assert rec, f"{check} produced no record"
        return json.loads(rec.group(1))["metrics"]

    c4 = metrics("c4_rank_slot.py")["r_beta_minus"]
    c5 = metrics("c5_monopole.py")["r_restored"]
    c6 = metrics("c6_thomson.py")
    assert c4 == pytest.approx(c5, rel=1e-9), (
        "C4's and C5's floors should be one number -- the Thomson term -- and "
        f"are {c4:.6e} and {c5:.6e}")
    assert c4 == pytest.approx(c6["r_grav"], rel=1e-9), (
        f"C6's gravitational-only column should be that same floor; "
        f"{c4:.6e} against {c6['r_grav']:.6e}")
    assert c6["r_c_alpha"] * 1e8 < c4, (
        "c = alpha should remove the floor by many orders, not merely improve "
        f"it: {c6['r_c_alpha']:.2e} against a floor of {c4:.2e}")
