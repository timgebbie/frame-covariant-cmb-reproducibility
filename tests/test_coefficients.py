r"""The covariant source coefficients, and finding **B-11**.

Annals II specialises to the Newtonian frame *before* it writes its sources
(\S7.1.1), so every equation this bundle implemented before `coefficients.py`
descends from $\tilde\sigma_{ab}\approx0$. These tests do two things and the
second is the point of the module:

1. the specialisation **recovers** what the bundle already computed --- decision
   S2's *restricted case which must recover v1.0.0's numbers*, applied to the
   coefficients rather than to a release;
2. the sector the specialisation discards is where (90)'s printed $C_0$ is
   wrong, and nothing in a Newtonian-only treatment can tell.
"""

from __future__ import annotations

from fractions import Fraction

import numpy as np
import pytest

from functions.harmonics.weights import beta
from functions.spectra.coefficients import (
    _solved_match,
    c0_from_printed_89,
    c0_from_the_match,
    match_coefficients,
    newtonian_coefficients,
)

ETA = np.linspace(0.11, 3.3, 11)
K = 60.0
DT = np.linspace(-1.9, 0.4, 11)
PHI = np.linspace(0.21, 0.04, 11)
KP = np.linspace(232.0, 0.0, 11)
VB = np.linspace(-1.9, -0.2, 11)
SIGMA = np.linspace(0.31, 0.02, 11)


def _match(**kw):
    base = dict(a_b1=K * (DT + PHI), a_b2=np.zeros_like(DT),
                kappa_prime_v_b=K * KP * VB, frame="test")
    return match_coefficients(ETA, K, **{**base, **kw})


def test_the_coefficients_are_exact_rationals_not_floats():
    """A sign on a harmonic weight is settled exactly or it is not settled."""
    assert all(isinstance(p, Fraction) for p in _solved_match())


def test_all_three_of_90_are_reproduced_by_the_match():
    r"""**(90) is correct and the match reproduces all three of its relations.**

    That is the content of B-11's resolution: solved with
    $j_0''(0)=-\tfrac13$, the $\ell=0$ row gives $-C_0=+\tfrac52a\mathcal B_2$
    exactly as (90) prints, alongside $C_1$ and $C_2$ which never disagreed.
    Four releases rest on (90), and they rest on it correctly.
    """
    p0, p1, p2 = _solved_match()
    assert -p0 == Fraction(5, 2), "-C_0 = +5/2 a B_2, as (90) prints"
    assert p1 == -1, "-C_1 = +(1/k)(a B_1 + kappa' v_B), as (90) prints"
    assert p2 == -1, "-C_2 = +(1/k^2) a B_2, as (90) prints"
    assert beta(1) == 1 and beta(2) == Fraction(2, 3)


def test_b11_is_a_sign_in_89_not_in_90():
    r"""**The finding, located.** (89) prints its $\delta_{\ell0}$ entry as
    $+\tfrac13$. That entry is $j_0''(0)$, and from the ascending series
    $j_0(x)=1-x^2/6+\dots$ it is $-\tfrac13$. With the printed sign the match
    contradicts (90)'s $C_0$ by exactly $-1$; with the true one it reproduces
    it. **The defect is in the intermediate equation, and (90) is right.**
    """
    assert c0_from_the_match == Fraction(-5, 2), "C_0 = -5/2 a B_2, so -C_0 = +5/2"
    assert c0_from_printed_89 == Fraction(5, 2)
    assert c0_from_printed_89 / c0_from_the_match == -1


def test_the_newtonian_specialisation_is_equation_109():
    r"""$-\tilde C_1=(\delta\tilde T+\Phi_A)+\kappa'\tilde v_B$, which is (109)
    `calc-ng`. Note $\tilde v_B=v_B/k$ **falls out** of the match rather than
    being imposed --- the $1/k$ in $C_1$ is the same one that turns
    $a\mathcal B_1$ into $(\delta\tilde T+\Phi_A)$. That is the reading A-2
    flagged, settled by arithmetic.
    """
    c = newtonian_coefficients(ETA, K, delta_t=DT, phi_a=PHI,
                               kappa_prime=KP, v_b=VB)
    # Relative, not absolute: these values are of order 400, where one ulp is
    # already 6e-14, so an absolute 1e-14 asserts better than double precision.
    assert np.allclose(-c.c1, (DT + PHI) + KP * VB, rtol=1e-14, atol=0.0)


def test_the_newtonian_frame_empties_the_shear_sector():
    r"""$\tilde{\mathcal B}_2=0\Rightarrow\tilde C_0=\tilde C_2=0$, which is
    (110). Identically zero, not small."""
    c = newtonian_coefficients(ETA, K, delta_t=DT, phi_a=PHI,
                               kappa_prime=KP, v_b=VB)
    assert c.shear_sector_is_empty
    assert np.all(c.c0 == 0.0) and np.all(c.c2 == 0.0)


def test_b11_is_invisible_in_the_newtonian_frame():
    r"""**Why four releases did not meet it.** $C_0\propto\mathcal B_2$, and
    $\mathcal B_2$ is identically zero in the only frame anyone computed in.
    This test is the statement that no released number can move under B-11.
    """
    matched = _match()
    printed = _match(use_printed_c0=True)
    assert np.array_equal(matched.c0, printed.c0)
    assert np.array_equal(matched.c1, printed.c1)
    assert np.array_equal(matched.c2, printed.c2)


def test_b11_bites_the_moment_the_shear_sector_is_occupied():
    """**The negative control.** Without this, the test above is
    indistinguishable from the finding being vacuous."""
    matched = _match(a_b2=SIGMA, frame="energy")
    printed = _match(a_b2=SIGMA, frame="energy", use_printed_c0=True)
    assert not matched.shear_sector_is_empty
    assert not np.allclose(matched.c0, printed.c0)
    nonzero = matched.c0 != 0.0
    assert np.allclose(printed.c0[nonzero] / matched.c0[nonzero], -1.0)
    # C_1 and C_2 are untouched by the C_0 question
    assert np.array_equal(matched.c1, printed.c1)
    assert np.array_equal(matched.c2, printed.c2)


def test_j0_second_derivative_at_zero_is_negative():
    r"""The one number B-11 turns on, asserted where a reader can see it.

    $j_0(x)=\sin x/x=1-x^2/6+x^4/120-\dots$, so $j_0''(0)=-\tfrac13$. Checked
    against the series and against `scipy`, because an assertion about a
    special function that only consults itself is not a check.
    """
    import sympy as sp
    from scipy.special import spherical_jn

    x = sp.symbols("x")
    series = sp.series(sp.sin(x) / x, x, 0, 6).removeO()
    assert sp.diff(series, x, 2).subs(x, 0) == Fraction(-1, 3)
    h = 1e-3
    numeric = (spherical_jn(0, h) - 2 * spherical_jn(0, 0.0) + spherical_jn(0, h)) / h**2
    assert numeric == pytest.approx(-1 / 3, rel=1e-5)


def test_c0_and_c2_are_the_same_source_at_two_ranks():
    r"""Both carry $\mathcal B_2$, which is why the paper says $C_0$ *"also
    contributes to the shear"*. Their ratio is a pure number times $k^2$ and
    carries no history."""
    c = _match(a_b2=SIGMA, frame="energy")
    ratio = c.c0 / c.c2
    assert np.allclose(ratio, ratio[0]), "the ratio must not depend on eta"
    assert np.isclose(ratio[0], 2.5 * K**2)


def test_a_mis_shaped_source_is_refused():
    with pytest.raises(ValueError):
        _match(a_b2=np.zeros(3))


def test_a_non_positive_wavenumber_is_refused():
    with pytest.raises(ValueError):
        match_coefficients(ETA, 0.0, a_b1=DT, a_b2=DT,
                           kappa_prime_v_b=DT, frame="test")


# --------------------------------------------------------------------------
# The generic source derivatives (102) needs, and their two controls.
# --------------------------------------------------------------------------


def test_the_rank_two_control_passes_symbolically():
    r"""**The control this derivation previously claimed did not exist.**

    *Annals II* prints the scalar matter-dominated second derivative,
    $(a^2\sigma)^{\ddot{}}+H(a^2\sigma)^{\dot{}}\approx\tfrac12a^2\rho_M\sigma$.
    The generic $\ddot\sigma$ assembled from Appendix G's shear and $\dot E$
    equations must reduce to it exactly when $A_a=\pi_{ab}=q_a=\mathrm{curl}H=0$
    and $p=0$. Asserted symbolically, because "identically zero" is the claim
    and a numerical tolerance would not be it.
    """
    import sympy as sp

    t = sp.symbols("t")
    a = sp.Function("a")(t)
    H = sp.diff(a, t) / a
    sig, E = sp.Function("sigma")(t), sp.Function("E")(t)
    rho = sp.symbols("rho")

    sigma_dot = -2 * H * sig - E
    E_dot = -3 * H * E - sp.Rational(1, 2) * rho * sig
    sigma_ddot = sp.diff(sigma_dot, t).subs(sp.Derivative(E, t), E_dot)
    sigma_ddot = sigma_ddot.subs(E, sp.solve(sp.Eq(sp.Symbol("sd"), sigma_dot), E)[0]
                                 .subs(sp.Symbol("sd"), sp.Derivative(sig, t)))

    printed = sp.Eq(sp.diff(a**2 * sig, t, 2) + H * sp.diff(a**2 * sig, t),
                    sp.Rational(1, 2) * a**2 * rho * sig)
    from_printed = sp.solve(printed, sp.Derivative(sig, t, 2))[0]

    assert sp.simplify(sp.expand(sigma_ddot - from_printed)) == 0


def test_the_shear_sector_derivatives_vanish_identically_in_the_newtonian_frame():
    r"""$\tilde\sigma_{ab}=0$ must give $C_2=C_2'=C_2''=0$ **identically**, not
    small. That is what makes the covariant form a strict generalisation: the
    Newtonian recovery cannot acquire a contribution from the sector it
    discards."""
    from functions.spectra.coefficients import c2_derivatives, generic_shear_derivatives

    n = 64
    a = np.linspace(1e-3, 1.0, n)
    cH, rho, zero = np.full(n, 1.3), 3.0 * np.ones(n), np.zeros(n)
    sd, sdd = generic_shear_derivatives(sigma=zero, electric_weyl=zero,
                                        conformal_hubble=cH, scale_factor=a, rho=rho)
    c2, c2p, c2pp = c2_derivatives(60.0, sigma=zero, sigma_dot=sd, sigma_ddot=sdd,
                                   conformal_hubble=cH, scale_factor=a, rho=rho)
    assert np.all(c2 == 0.0) and np.all(c2p == 0.0) and np.all(c2pp == 0.0)


def test_the_shear_sector_switches_on_when_the_shear_does():
    """The negative control for the test above."""
    from functions.spectra.coefficients import c2_derivatives, generic_shear_derivatives

    n = 64
    a = np.linspace(1e-3, 1.0, n)
    cH, rho = np.full(n, 1.3), 3.0 * np.ones(n)
    sigma = 0.02 * np.exp(-(((a - 0.3) / 0.2) ** 2))
    sd, sdd = generic_shear_derivatives(sigma=sigma, electric_weyl=-0.5 * sigma,
                                        conformal_hubble=cH, scale_factor=a, rho=rho)
    c2, c2p, c2pp = c2_derivatives(60.0, sigma=sigma, sigma_dot=sd, sigma_ddot=sdd,
                                   conformal_hubble=cH, scale_factor=a, rho=rho)
    assert np.any(c2 != 0.0) and np.any(c2p != 0.0) and np.any(c2pp != 0.0)


def test_no_numerical_derivative_survives_in_the_c2_chain():
    r"""**Finding T-23, enforced.** The $C_2$ chain must take no numerical
    derivative of a perturbation: $\dot\sigma$ and $\ddot\sigma$ come from the
    published relations and $a''$ from Friedmann. A spline or `np.gradient` here
    would reintroduce exactly the error T-23 records, and silently.
    """
    import ast
    import inspect

    from functions.spectra.coefficients import c2_derivatives

    tree = ast.parse(inspect.getsource(c2_derivatives))
    fn = tree.body[0]
    if isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant):
        fn.body = fn.body[1:]            # the docstring names them; the body must not
    body = ast.unparse(fn)
    for forbidden in ("np.gradient", "CubicSpline", "np.diff", "* 0.0"):
        assert forbidden not in body, f"{forbidden} reappeared in the C_2 chain"
