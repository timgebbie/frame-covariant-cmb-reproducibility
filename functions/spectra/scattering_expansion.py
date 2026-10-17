r"""Appendix C's scattering-strength expansion, re-derived and carried to any order.

*Annals II* Appendix C writes the almost-Friedmann--Lema\^itre integrated
Boltzmann equation for Thomson scattering as

    B + tau-dot + e^a D_a tau  ~=  t_c^-1 [ v^a e_a - tau ],

inverts it,

    tau  =  v^a e_a - t_c [ B + tau-dot + e^a D_a tau ],                 (C.2)

and approximates it *"systematically ... in terms of the smallness parameter
$t_c$"* by the recursion

    tau_(n)  ~=  v^a e_a - t_c [ B + tau-dot_(n-1) + e^a D_a tau_(n-1) ],

printing $\tau_{(0)}$, $\tau_{(1)}$ and $\tau_{(2)}$. **§5.5.3** *Expansion in
Thompson Scattering Time* states the scheme carries *"terms up to $\mathcal
O(t_c^3)$"*, so the ceiling is the antecedent's and the printed orders stop one
short of it.

**The recursion is geometric, and that is the whole derivation.** Writing
$\mathcal D=\partial_t+e^a\mathrm D_a$ for the derivative along the photon path
--- which is exactly the pair of terms the recursion applies to
$\tau_{(n-1)}$ --- (C.2) reads $\tau=V-t_c(B+\mathcal D\tau)$ with
$V\equiv v^ae_a$, hence

    (1 + t_c D) tau  =  V - t_c B,        tau  =  (1 + t_c D)^-1 (V - t_c B),

and expanding the inverse as a Neumann series in $(-t_c\mathcal D)$ gives a
**closed form at every order**:

    tau_(n)  =  V  +  sum_{m=1..n} (-1)^m t_c^m [ D^m V  +  D^(m-1) B ].

This module is that statement, executable. `expansion(n)` returns the terms;
`PRINTED_TAU_2` is Appendix C's own $\tau_{(2)}$ transcribed from the page; and
`tests/test_scattering_expansion.py` asserts they agree term for term. Nothing
here is fitted to the printed form --- the closed form is derived from the
recursion and *then* compared, which is the only order in which the comparison
means anything.

**Two consequences the closed form makes immediate, and neither is in the
printed text.**

1. **The term count is exact**: order $m$ contributes $2^m$ terms seeded by $V$
   and $2^{m-1}$ seeded by $B$, because $\mathcal D^m$ is a sum over words in
   $\{\partial_t,\,e^a\mathrm D_a\}$. Appendix C's $\tau_{(2)}$ prints
   $2+1$ then $4+2$ --- three and six --- and does.
2. **Order $m$ sources multipoles up to $\ell=m+1$.** Each $e^a\mathrm D_a$
   carries one direction vector and $V=v^ae_a$ carries one already, so a word
   with $g$ gradients seeded by $V$ has $g+1$ factors of $e^a$ and, reduced by
   Appendix C's own solid-angle identities, a PSTF part of rank $g+1$. At
   $m=2$ that reaches **rank three** --- the term
   $e^ce^ae^b\mathrm D_c\mathrm D_av_b$.

   **This is a constraint on extending the expansion, not a defect in the
   paper.** §7.1 introduces its near-tight-coupling set *"rewritten to first
   order"*, and (L0082)'s $\tau^{A_\ell}\simeq0$ for $\ell>2$ is consistent
   with first order, where `max_rank` is 2. The two are used in different
   places and *Annals II* does not combine them. What follows is that
   **carrying the expansion past first order --- which §5.5.3 licenses and
   Appendix C prints --- requires carrying $\ell=3$**, and the closure that
   comes with (152)/(153) does not. See `max_rank`, approximation **A-4** and
   decision **S42**.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

__all__ = [
    "DOT",
    "GRAD",
    "PRINTED_TAU_1",
    "PRINTED_TAU_2",
    "Term",
    "expansion",
    "max_rank",
    "recursion",
    "words",
]

#: The two halves of $\mathcal D=\partial_t+e^a\mathrm D_a$. A *word* is the
#: sequence in which they are applied, **innermost first**, so `("dot", "grad")`
#: means $e^c\mathrm D_c\big(\partial_t\,\cdot\big)$.
DOT = "dot"
GRAD = "grad"


@dataclass(frozen=True, order=True)
class Term:
    r"""One term of the expansion: $\pm t_c^{p}\,\mathcal W[\text{seed}]$.

    `seed` is `"V"` for $v^ae_a$ or `"B"` for $\mathcal B$. `word` is the
    operator sequence applied to it, innermost first. `sign` is $(-1)^p$ and is
    carried explicitly rather than recomputed, so a term printed from this
    dataclass is complete on its own.
    """

    power: int
    seed: str
    word: tuple[str, ...]
    sign: int

    @property
    def rank(self) -> int:
        r"""Factors of $e^a$, hence the PSTF rank this term can source.

        One per $e^a\mathrm D_a$, plus one for $V=v^ae_a$ itself. Appendix C's
        own reductions --- $e^ae^b\mathrm D_av_b=O^{ab}\mathrm D_av_b+\tfrac13
        \mathrm D_av^a$ and its two siblings --- are what turn these products
        into PSTF parts, and they lower the rank by two at a time, so this is
        the **highest** multipole the term reaches, not the only one.
        """
        return self.word.count(GRAD) + (1 if self.seed == "V" else 0)

    def __str__(self) -> str:
        body = "v_a e^a" if self.seed == "V" else "B"
        for operator in self.word:
            body = f"({body})." if operator == DOT else f"e^c D_c({body})"
        return f"{'+' if self.sign > 0 else '-'} t_c^{self.power} {body}"


def words(length: int) -> list[tuple[str, ...]]:
    r"""Every word of `length` over $\{\partial_t,\,e^a\mathrm D_a\}$.

    $\mathcal D^m$ expands to exactly these $2^m$ words, which is why the term
    count at order $m$ is $2^m+2^{m-1}$ and not something that has to be
    counted off the page.
    """
    if length < 0:
        raise ValueError("length must be non-negative")
    return [tuple(w) for w in product((DOT, GRAD), repeat=length)]


def expansion(order: int) -> list[Term]:
    r"""$\tau_{(n)}$ by the closed form, as an unordered set of terms.

    $$\tau_{(n)}=V+\sum_{m=1}^{n}(-1)^m t_c^m\big[\mathcal D^mV
      +\mathcal D^{m-1}\mathcal B\big].$$

    Derived from the recursion by summing the Neumann series, **not** read off
    Appendix C. `recursion(order)` builds the same object the long way and the
    tests require the two to agree, which is what makes the closed form a
    result rather than a restatement.
    """
    if order < 0:
        raise ValueError("order must be non-negative")
    terms = [Term(power=0, seed="V", word=(), sign=+1)]
    for m in range(1, order + 1):
        sign = -1 if m % 2 else +1
        terms += [Term(m, "V", w, sign) for w in words(m)]
        terms += [Term(m, "B", w, sign) for w in words(m - 1)]
    return terms


def recursion(order: int) -> list[Term]:
    r"""$\tau_{(n)}$ by applying Appendix C's recursion literally, $n$ times.

    Kept beside `expansion` on purpose. The closed form is the claim; this is
    the definition. **A derivation checked only against the thing it was
    derived from proves nothing**, so the tests check this against the printed
    $\tau_{(1)}$ and $\tau_{(2)}$ as well, which is the independent half.
    """
    if order < 0:
        raise ValueError("order must be non-negative")
    terms = [Term(power=0, seed="V", word=(), sign=+1)]
    for _ in range(order):
        # tau <- V - t_c [ B + D tau ]
        carried: list[Term] = [Term(0, "V", (), +1), Term(1, "B", (), -1)]
        for term in terms:
            for operator in (DOT, GRAD):
                carried.append(Term(term.power + 1, term.seed,
                                    term.word + (operator,), -term.sign))
        terms = [t for t in carried if t.power <= order]
    return terms


def max_rank(order: int) -> int:
    r"""The highest PSTF rank $\tau_{(n)}$ can source: $n+1$.

    **This is the number that collides with (L0082).** The near-tight-coupling
    closure sets $\tau^{A_\ell}\simeq0$ for every $\ell>2$, which is consistent
    with the expansion only while `max_rank(order) <= 2`, that is only at
    `order <= 1`. Appendix C prints $\tau_{(2)}$; §5.5.3 licenses
    $\mathcal O(t_c^3)$ and so rank four. Carrying either without carrying the
    multipoles they generate is approximation **A-4**, and *Annals II*'s own
    **Appendix E** says what the discarded harmonics hold: if four consecutive
    ones vanish exactly then $\sigma_{ab}=0$ exactly, so the residual in them
    is where the shear lives.
    """
    return max(term.rank for term in expansion(order))


#: Appendix C's $\tau_{(1)}$, transcribed from the page:
#: $v^ae_a-t_c[\mathcal B+e^a\dot v_a+e^ae^b\mathrm D_av_b]$.
PRINTED_TAU_1: tuple[Term, ...] = (
    Term(0, "V", (), +1),
    Term(1, "B", (), -1),
    Term(1, "V", (DOT,), -1),
    Term(1, "V", (GRAD,), -1),
)

#: Appendix C's $\tau_{(2)}$, transcribed from the page. The $t_c^2$ bracket is
#: $\dot{\mathcal B}+e^a\ddot v_a+e^ae^b(\mathrm D_av_b)^{\textstyle\cdot}
#: +e^c\mathrm D_c\mathcal B+e^ce^d\mathrm D_c\dot v_b+e^ce^ae^b\mathrm D_c
#: \mathrm D_av_b$ --- six terms, matching $2^2+2^1$.
#:
#: **The fifth is printed with a dangling index.** $e^ce^d\mathrm D_c\dot v_b$
#: leaves both $d$ and $b$ free in a scalar; it is
#: $e^ce^d\mathrm D_c\dot v_d$, the word `(DOT, GRAD)` --- the time derivative
#: taken first and the gradient outside. Recorded as **B-15**; it changes
#: nothing, and a reader re-deriving the appendix stops on it.
PRINTED_TAU_2: tuple[Term, ...] = PRINTED_TAU_1 + (
    Term(2, "B", (DOT,), +1),
    Term(2, "B", (GRAD,), +1),
    Term(2, "V", (DOT, DOT), +1),
    Term(2, "V", (DOT, GRAD), +1),
    Term(2, "V", (GRAD, DOT), +1),
    Term(2, "V", (GRAD, GRAD), +1),
)
