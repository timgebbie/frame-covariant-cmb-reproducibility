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

#: **Discovered from disk, not listed. Finding T-155.**
#:
#: This was a hand-written list holding `c1`–`c7`. P1-T's audit of
#: 2026-10-26 found **three** hand-maintained registries of `tests/frame/`
#: holding **three different suites**: their `run_all.py` had `c1`–`c9`,
#: their `gen_theory_audit.py` had `c1`–`c8` — so `docs/THEORY-AUDIT.md`
#: carried no by-parts admissibility result for five days after `c9` landed —
#: and this one had `c1`–`c7`, so **neither `c8` nor `c9` was gated by the
#: bundle's harness at all**. An instrument that is committed and not
#: registered is a file, not a gate.
#:
#: A list is the wrong shape for this. Globbing means a new instrument is
#: gated **the day it lands**, with nothing to remember — the same reason
#: `tests/test_every_control_moves_something.py` discovers its controls from
#: the signature and `tests/test_readme_renders_on_github.py` discovers its
#: markdown from the tree. **Every registry in this bundle that is a literal
#: list has drifted at least once; none of the discovered ones has.**
#:
#: Sorted numerically rather than lexically, so `c10` follows `c9` and the
#: parametrised test ids read in the order the instruments were written.
CHECKS = sorted(
    (p.name for p in FRAME.glob("c*.py") if p.name[1:2].isdigit()),
    key=lambda n: int(n[1:].split("_", 1)[0]))


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


#: **A missing `sympy` is an absent toolchain, not a failed instrument.**
#:
#: On 2026-10-26 the PI's run reported six of these red on a clean Python
#: 3.13 --- `c1`, `c4`, `c5`, `c6`, `c7` and the Thomson-floor comparison ---
#: every one of them `ModuleNotFoundError: No module named 'sympy'`. Nothing
#: was wrong with the algebra; the interpreter simply could not do any.
#:
#: **Six red on a clean machine is worse than six skips**, because it teaches
#: whoever runs the suite next that red is the normal colour here, and the
#: finding that then goes unread is the real one. The instruments are run
#: under `-I`, so they see the *subprocess* interpreter's packages and not
#: pytest's: the import is probed in that same interpreter rather than here.
#:
#: **The glob floor below stays a hard failure.** An instrument that has gone
#: missing is a defect in the bundle whatever the toolchain can do, and a
#: skip must never be able to hide one.
def _sympy_is_absent() -> bool:
    probe = subprocess.run([sys.executable, "-I", "-c", "import sympy"],
                           capture_output=True, text=True)
    return probe.returncode != 0


_NO_SYMPY = _sympy_is_absent()
_SYMPY_REASON = (
    "sympy cannot be imported by the interpreter these instruments run under, "
    f"which is `{sys.executable} -I`. **`-I` implies `-s`, so a `pip install "
    "--user sympy` is invisible to it** -- on Windows that is pip's default "
    "when the system site-packages is not writable, so `Requirement already "
    "satisfied` and this skip are both true at once. Install into the "
    "interpreter itself (an elevated shell, or a virtualenv), or run "
    "`tests/frame/run_all.py` directly, which does not isolate. This is a "
    "SKIP and not a pass: nothing in tests/frame/ has been verified here, and "
    "scripts/check_release_hygiene.py will still refuse the release because "
    "docs/THEORY-AUDIT.md cannot be regenerated without these.")


def test_the_glob_found_the_instruments():
    """**A glob that matches nothing passes every test below it.**

    The floor is the one thing a discovered registry needs that a literal
    list does not: a list fails loudly when its files vanish, a glob goes
    quiet. Eight is what `tests/frame/` held when discovery replaced the
    list, so a drop below it means instruments left the tree rather than
    that the pattern stopped matching -- and either way it should be said
    out loud.
    """
    assert len(CHECKS) >= 8, (
        f"only {len(CHECKS)} frame instruments discovered in {FRAME}; the "
        "glob is matching less than the tree held when it was written")
    assert CHECKS[0].startswith("c1_"), (
        f"the numeric sort is wrong: first entry is {CHECKS[0]}")


@pytest.mark.skipif(_NO_SYMPY, reason=_SYMPY_REASON)
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


@pytest.mark.skipif(_NO_SYMPY, reason=_SYMPY_REASON)
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
