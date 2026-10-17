r"""Appendix C's scattering-strength expansion, checked three ways.

**The closed form is the claim and the printed appendix is the arbiter.** A
derivation checked only against the recursion it was summed from proves that
the summation is right and nothing else, so every test below that matters
compares against *Annals II*'s own $\tau_{(1)}$ and $\tau_{(2)}$, transcribed
from the page in `scattering_expansion.PRINTED_TAU_1` and `PRINTED_TAU_2`.

This is **S42**'s first deliverable and it carries no numerics at all: the
expansion is an operator identity, so it is checked as one.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.spectra.scattering_expansion import (  # noqa: E402
    DOT,
    GRAD,
    PRINTED_TAU_1,
    PRINTED_TAU_2,
    Term,
    expansion,
    max_rank,
    recursion,
    words,
)


def test_the_closed_form_reproduces_the_recursion():
    """$(1+t_c\\mathcal D)^{-1}$ summed, against the recursion applied $n$ times."""
    for order in range(5):
        assert sorted(expansion(order)) == sorted(recursion(order)), (
            f"the Neumann series and the literal recursion disagree at order "
            f"{order}. One of them is wrong and the recursion is the definition.")


@pytest.mark.parametrize("order,printed", [(1, PRINTED_TAU_1), (2, PRINTED_TAU_2)])
def test_the_closed_form_reproduces_the_printed_appendix(order, printed):
    r"""**The independent check.** Appendix C prints $\tau_{(1)}$ and
    $\tau_{(2)}$; the closed form was derived from the recursion without
    looking at either, and must land on them term for term.

    The fifth term of the $t_c^2$ bracket is compared as
    $e^ce^d\mathrm D_c\dot v_d$, not as the page's
    $e^ce^d\mathrm D_c\dot v_b$, which leaves two indices free in a scalar.
    Finding **B-15**.
    """
    assert sorted(expansion(order)) == sorted(printed), (
        f"the closed form does not reproduce Annals II's printed tau_({order}).\n"
        f"  derived but not printed: {sorted(set(expansion(order)) - set(printed))}\n"
        f"  printed but not derived: {sorted(set(printed) - set(expansion(order)))}")


def test_a_comparison_that_cannot_fail_is_not_a_comparison():
    """The control. Perturb one term and the comparison above must notice."""
    broken = list(PRINTED_TAU_2)
    broken[-1] = Term(2, "V", (GRAD, GRAD), -1)          # sign flipped
    assert sorted(expansion(2)) != sorted(broken), (
        "a sign flip in the highest term went unnoticed, so the term-for-term "
        "comparison is not comparing terms")


@pytest.mark.parametrize("order,bracket,total", [(0, 1, 1), (1, 3, 4), (2, 6, 10),
                                                 (3, 12, 22), (4, 24, 46)])
def test_the_term_count_is_two_to_the_m_plus_two_to_the_m_minus_one(order, bracket, total):
    r"""Each $t_c^m$ **bracket** holds $2^m+2^{m-1}$ terms; $\tau_{(n)}$ holds
    $1+\sum_{m\le n}(2^m+2^{m-1})$ of them, because it carries every order up
    to $n$ and $\mathcal D^m$ is a sum over words.

    **Appendix C prints exactly these brackets** --- three terms multiplying
    $t_c$, six multiplying $t_c^2$ --- and does not say why those are the
    counts. They are not chosen; they are $2+1$ and $4+2$.

    *The first version of this test asserted the bracket counts as the totals
    and failed at every order above zero. The counts here are the arithmetic,
    not the measurement, and getting them wrong is how a test comes to agree
    with whatever the code does.*
    """
    assert len(words(order)) == 2 ** order
    at_order = [t for t in expansion(order) if t.power == order]
    assert len(at_order) == bracket, (
        f"the t_c^{order} bracket should hold 2^{order} + 2^{order - 1} terms")
    assert len(expansion(order)) == total


def test_order_two_already_sources_an_octupole_the_closure_discards():
    r"""**The result S42 is for.** $\tau_{(n)}$ reaches PSTF rank $n+1$.

    Each $e^a\mathrm D_a$ carries a direction vector and $V=v^ae_a$ carries one
    already, so the second-order term $e^ce^ae^b\mathrm D_c\mathrm D_av_b$ has
    three. The near-tight-coupling closure **(L0082)** sets
    $\tau^{A_\ell}\simeq0$ for every $\ell>2$.

    **So Appendix C's printed $\tau_{(2)}$ and (L0082) cannot both hold.** They
    are consistent only at first order, and §5.5.3 licenses $\mathcal O(t_c^3)$
    — rank four — which is further still. That is approximation **A-4** stated
    as a rank rather than as a dropped term, and *Annals II*'s **Appendix E**
    says what sits in the discarded harmonics: if four consecutive ones vanish
    exactly then $\sigma_{ab}=0$ exactly, so the residual is where the shear
    lives.
    """
    assert max_rank(0) == 1
    assert max_rank(1) == 2, "first order reaches the quadrupole, which (L0082) keeps"
    assert max_rank(2) == 3, "second order reaches the octupole"
    assert max_rank(3) == 4

    octupole = [t for t in expansion(2) if t.rank == 3]
    assert len(octupole) == 1 and octupole[0].word == (GRAD, GRAD), (
        "the rank-three term at second order is e^c e^a e^b D_c D_a v_b and "
        "there is exactly one of it")


def test_every_term_is_printable_and_says_what_it_is():
    """A record nobody can read is not a record."""
    rendered = {str(t) for t in expansion(2)}
    assert "+ t_c^0 v_a e^a" in rendered
    assert "- t_c^1 B" in rendered
    assert "+ t_c^2 e^c D_c(e^c D_c(v_a e^a))" in rendered
    assert len(rendered) == len(expansion(2)), "two terms rendered identically"


def test_the_seeds_are_the_two_the_appendix_names():
    r"""$v^ae_a$ and $\mathcal B$, and nothing else enters."""
    assert {t.seed for t in expansion(4)} == {"V", "B"}
    assert all(t.sign == (1 if t.power % 2 == 0 else -1) for t in expansion(4)), (
        "the sign is (-1)^m by the Neumann series; a term disagreeing with "
        "that is a term in the wrong order")
    assert all(t.word == () for t in expansion(3) if t.power == 0)
    # B enters one order later than V: D^(m-1) B against D^m V.
    for m in range(1, 4):
        assert max(len(t.word) for t in expansion(m) if t.seed == "B") == m - 1
        assert max(len(t.word) for t in expansion(m) if t.seed == "V") == m
