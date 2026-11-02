r"""The one peak finder, and the plateau spike it must not return. **T-184.**

**Why this file exists, and it is an absence rather than a defect.** Until
31 October 2026 this tree carried *three* implementations of "the first
acoustic peak" --- `d24.peak_position`, `d36._peak` and
`compare_criterion_5b.peak_position` --- with three different bands, and a
test-suite scan found **no test covering any of them**. One of the three was
wired to gate G-a, whose number is published in `README.md` as a scored and
failed pre-registered prediction.

That number was an instrument artefact. The finder took a global `argmax`
over $\ell\ge2$, the released spectrum carries a spurious maximum at
$\ell\simeq7$ at $9.6\times$ CAMB's plateau (**T-181b**), and so the gate
reported the plateau under the name of a peak position.

**An untested instrument behind a published number is the failure here**, not
the missing floor. The floor was a one-line fix; nothing in the suite could
have told anyone it was needed.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _peak import PLATEAU_FLOOR, first_acoustic_peak  # noqa: E402


def test_the_plateau_spike_is_not_returned_as_an_acoustic_peak() -> None:
    r"""**The regression that gate G-a needed and did not have.**

    A spectrum shaped like the released one: a tall spurious maximum at
    $\ell=7$, then the Sachs--Wolfe plateau, then a genuine acoustic peak near
    $\ell=265$. The global maximum is the spike. The first ACOUSTIC maximum is
    not, and the two differ by a factor of 30 in $\ell$.
    """
    ell = np.array([2.0, 4, 7, 11, 16, 22, 30, 60, 120, 180, 230, 265, 300, 360])
    d = np.array([0.7, 2.6, 9.6, 5.6, 2.6, 1.5, 1.0, 1.2, 1.9, 2.4, 2.6, 2.7,
                  2.6, 2.1])

    assert int(ell[int(np.argmax(d))]) == 7, (
        "fixture is wrong: the global maximum must be the plateau spike, "
        "otherwise this test cannot fail for the reason it exists")

    pos, _ = first_acoustic_peak(ell, d)
    assert 230.0 < pos < 300.0, (
        f"the finder returned {pos:.2f}. Anything near 7 means the plateau "
        f"spike is being reported as an acoustic peak, which is exactly what "
        f"gate G-a published as 0.0073.")


def test_it_still_fires_when_there_is_no_acoustic_peak() -> None:
    """`nan`, not a number. **A finder that always answers is not a gate.**

    The released Newtonian frame genuinely has no interior maximum above the
    floor under some weightings, and D36 reports that. A finder that returned
    an endpoint instead would turn a real negative result into a false
    positive.
    """
    ell = np.linspace(2.0, 400.0, 40)
    pos, unc = first_acoustic_peak(ell, np.exp(-ell / 50.0))
    assert np.isnan(pos) and np.isnan(unc)


def test_the_floor_is_what_separates_the_two_answers() -> None:
    """The same data, two floors, two answers --- so the floor is doing work.

    **T-44's discipline applied to a parameter**: if moving the floor across
    the spike changed nothing, the floor would not be the thing excluding it
    and this file would be testing a coincidence.
    """
    ell = np.array([2.0, 4, 7, 11, 16, 22, 30, 60, 120, 180, 230, 265, 300, 360])
    d = np.array([0.7, 2.6, 9.6, 5.6, 2.6, 1.5, 1.0, 1.2, 1.9, 2.4, 2.6, 2.7,
                  2.6, 2.1])
    below, _ = first_acoustic_peak(ell, d, floor=2.0)
    above, _ = first_acoustic_peak(ell, d, floor=PLATEAU_FLOOR)
    assert below < 20.0 < above, (
        f"floor=2 gave {below:.2f} and floor={PLATEAU_FLOOR} gave {above:.2f}; "
        f"they must straddle the spike or the floor is not the mechanism")


def test_the_vertex_is_exact_on_an_UNEQUALLY_spaced_grid() -> None:
    r"""A known parabola, sampled at unequal spacing, recovered exactly.

    **This is the property D36's form did not have and D24's did**, which is
    why the shared module took D24's Lagrange vertex. These grids change
    spacing at the join between their sparse and dense halves, so a vertex
    formula that assumes even spacing is wrong precisely where the grids are
    interesting.
    """
    vertex = 137.0
    ell = np.array([30.0, 60.0, 100.0, 125.0, 155.0, 300.0])
    d = -((ell - vertex) ** 2) + 1000.0
    pos, _ = first_acoustic_peak(ell, d)
    assert pos == pytest.approx(vertex, abs=1e-6), (
        f"recovered {pos!r} for a parabola whose vertex is exactly {vertex}")


def test_it_reproduces_D36s_published_number() -> None:
    """60.65 on D41's committed spectra, which is what D36 printed.

    **The golden check that the T-184 merge moved nothing.** Three finders
    became one; D36's published Newtonian maximum must survive that, and if it
    does not then the refactor changed a result and has to say so.
    """
    csv_path = ROOT / "diagnostics" / "d41-newtonian-maximum-fine-grid.csv"
    if not csv_path.exists():
        pytest.skip("D41's artefact is not in this tree")
    rows = [r for r in csv.reader(csv_path.open(encoding="utf-8"))
            if r and not r[0].startswith("#")]
    pairs = [(float(l), float(v)) for f, l, v in rows[1:] if f == "newtonian"]
    ell = np.array([p[0] for p in pairs])
    d = np.array([p[1] for p in pairs])

    d36_grid = np.unique(np.concatenate([
        np.array([2, 3, 5, 7, 10, 15, 20, 25]), np.arange(40, 341, 15)]))
    keep = np.isin(ell, d36_grid)
    pos, _ = first_acoustic_peak(ell[keep], d[keep])
    assert pos == pytest.approx(60.65, abs=0.01)


def test_no_second_copy_of_the_finder_survives_in_scripts() -> None:
    """No `scripts/*.py` may define its own peak finder. **T-184 missed one.**

    The merge on 31 October took three copies on the argument that a rule two
    copies be kept in step is kept only by someone remembering. **There were
    four** --- `d34` had one too, the scan that found the others listed that
    file, and it was read past. An incomplete merge leaves exactly the
    condition the merge was for, so the guard is structural rather than a
    note: anything in `scripts/` that defines a finder rather than importing
    one fails here.
    """
    import ast

    offenders = []
    for path in sorted((ROOT / "scripts").glob("*.py")):
        if path.name == "_peak.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name not in ("_peak", "peak_position"):
                continue
            # **Semantic, not shape.** A first draft asserted the body was
            # exactly one `return first_acoustic_peak(...)` and flagged
            # `compare_criterion_5b`, which delegates and then rounds to the
            # nearest multipole --- a false positive in the guard rather than
            # a copy in the tree. What makes a function a second finder is
            # that it does the SEARCH itself, so that is what is tested: it
            # must call the shared one, and must contain neither an `argmax`
            # nor a loop looking for a maximum.
            # **The docstring is not code, and a first draft forgot that.**
            # Dumping the whole node matched the word `argmax` inside D24's
            # and criterion-5b's docstrings, where both explain what they
            # used to do --- so the guard flagged the two functions whose
            # documentation is clearest about having been repaired. The
            # leading docstring is dropped before anything is inspected.
            body = list(node.body)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(getattr(body[0], "value", None), ast.Constant)
                    and isinstance(body[0].value.value, str)):
                body = body[1:]
            dump = "".join(ast.dump(n) for n in body)
            calls_shared = "first_acoustic_peak" in dump
            searches_itself = (
                "argmax" in dump
                or any(isinstance(n, (ast.For, ast.While))
                       for stmt in body for n in ast.walk(stmt)))
            if not calls_shared or searches_itself:
                offenders.append(
                    f"{path.name}::{node.name} "
                    f"(calls_shared={calls_shared}, "
                    f"searches_itself={searches_itself})")
    assert not offenders, (
        "these define a peak finder instead of importing the one in "
        f"scripts/_peak.py: {offenders}")


def test_the_four_call_sites_now_share_one_definition() -> None:
    """D24, D34, D36 and criterion-5b must not drift apart again.

    **The rule that two copies be kept in step is kept only by someone
    remembering**, and this bundle has lost that bet four times --- the three
    registries in `gen_theory_audit.py`, the tight-coupling continuation
    (T-125), `build_supplement.py`'s staged directory list (T-174), and these
    finders. This asserts the sharing structurally rather than by note.
    """
    import compare_criterion_5b as c5b
    import diagnostic_d24_phi_prime_sweep as d24
    import diagnostic_d34_split_by_parts as d34
    import diagnostic_d36_frame_invariance_by_weighting as d36

    ell = np.array([2.0, 4, 7, 11, 16, 22, 30, 60, 120, 180, 230, 265, 300, 360])
    d = np.array([0.7, 2.6, 9.6, 5.6, 2.6, 1.5, 1.0, 1.2, 1.9, 2.4, 2.6, 2.7,
                  2.6, 2.1])
    shared, _ = first_acoustic_peak(ell, d)

    assert d24.peak_position(ell, d)[0] == pytest.approx(shared)
    assert d34._peak(ell, d) == pytest.approx(shared)
    assert d36._peak(ell, d) == pytest.approx(shared)
    assert c5b.peak_position(ell, d) == int(round(shared))
