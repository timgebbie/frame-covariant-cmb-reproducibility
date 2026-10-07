"""PSTF harmonic weights, as exact rationals.

Every weight here is a **definition** taken from the published sources, or exact
arithmetic on one. Nothing in this module asserts a sign or an ell-weight of the
hierarchy; those belong to the recursion module and carry their convention with
them.

Sources, cited by **published** equation number:

    beta_l = O^{A_l} O_{A_l} = (l!)^2 2^l / (2l)! = l! / (2l-1)!!
        Gebbie & Ellis, Annals of Physics 282, 285 (2000), Eq. (24).

    Delta_l = 4 pi 2^l (l!)^2 / (2l+1)! = 4 pi beta_l / (2l+1)
        Gebbie & Ellis (2000), Eq. (119).

    beta_l = alpha_l^{-1} (2l+1)
        Gebbie, Dunsby & Ellis, Annals of Physics 282, 321 (2000),
        Appendix F, p. 380, in the step from (F.3) to (F.4).

Exact rationals, never floats. A weight that is compared or asserted anywhere in
this bundle is compared as a `Fraction`, because the whole point of the project
is that a sign or an ell-weight is settled exactly or it is not settled.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import factorial

__all__ = ["beta", "alpha", "delta_over_four_pi", "free_streaming_weight"]


def _check_ell(ell: int, minimum: int = 0) -> int:
    if not isinstance(ell, int) or isinstance(ell, bool):
        raise TypeError(f"ell must be an int, got {type(ell).__name__}")
    if ell < minimum:
        raise ValueError(f"ell must be >= {minimum}, got {ell}")
    return ell


@lru_cache(maxsize=None)
def beta(ell: int) -> Fraction:
    """beta_l = (l!)^2 2^l / (2l)!  —  Gebbie & Ellis (2000), Eq. (24).

    Equivalently l!/(2l-1)!!. Returned exactly.

    >>> beta(0), beta(1), beta(2)
    (Fraction(1, 1), Fraction(1, 1), Fraction(2, 3))
    """
    _check_ell(ell)
    return Fraction(2**ell * factorial(ell) ** 2, factorial(2 * ell))


@lru_cache(maxsize=None)
def alpha(ell: int) -> Fraction:
    """alpha_l, defined by beta_l = alpha_l^{-1} (2l+1).

    Gebbie, Dunsby & Ellis (2000), Appendix F, p. 380. So alpha_l = (2l+1)/beta_l.
    This is the normalisation in which (F.4) takes the Ma & Bertschinger form.
    """
    _check_ell(ell)
    return Fraction(2 * ell + 1) / beta(ell)


@lru_cache(maxsize=None)
def delta_over_four_pi(ell: int) -> Fraction:
    """Delta_l / (4 pi) = beta_l / (2l+1)  —  Gebbie & Ellis (2000), Eq. (119).

    The factor 4 pi is kept out so the result stays an exact rational. Multiply
    by `4 * math.pi` at the point of numerical use, never before a comparison.
    """
    _check_ell(ell)
    return beta(ell) / Fraction(2 * ell + 1)


@lru_cache(maxsize=None)
def free_streaming_weight(ell: int) -> Fraction:
    """The coefficient of tau_{l+1} in the mode-coefficient recursion (F.1).

    Gebbie, Dunsby & Ellis (2000), Appendix F, p. 379, Eq. (F.1), l >= 2:

        -tau_l^dot  ~=  (k_com/a) [ w_l tau_{l+1} - tau_{l-1} ],
        w_l = (l+1)^2 / [(2l+3)(2l+1)].

    Note that `k` in (F.1) is the **comoving** wavenumber: the equation carries an
    explicit 1/a against a proper-time derivative. See
    `provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md`, *Symbols that collide
    across the sources*.
    """
    _check_ell(ell, minimum=2)
    return Fraction((ell + 1) ** 2, (2 * ell + 3) * (2 * ell + 1))
