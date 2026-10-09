r"""Acceptance criterion 2: the frame round trip returns $\mathcal B_1+\dot v_a$.

Decision S14 states the target and the reason it is a *check* rather than a
rederivation: $\mathcal B_1$ does not change form off the Newtonian frame, so
the generic-$u^a$ construction must return
$\tilde{\mathcal B}_1=\mathcal B_1+\dot v_a$ — **no shear, no $Hv$** — and any
other result is a bug in this bundle.

**Asserting only that the residual vanishes would be the weak test.** A
cancellation can vanish because both halves are zero, because a term was
dropped by hand, or because the right answer was written down. So these tests
assert the *mechanism*: each half carries its $Hv$ with opposite sign before the
sum loses it, the shear and vorticity contractions are present in the
unexpanded acceleration and removed by order rather than by assumption, and the
final residual is **identically** zero in sympy rather than small in floating
point.
"""

from __future__ import annotations

import sympy as sp

from functions.frames import (
    EPS,
    FrameChange,
    boosted_acceleration,
    boosted_temperature_gradient,
    bracket_rank1,
    roundtrip_residual,
)


def _vec(name: str) -> sp.Matrix:
    return sp.Matrix(3, 1, lambda i, _j: EPS * sp.Symbol(f"{name}_{i+1}", real=True))


# ---------------------------------------------------------------------------
# the target
# ---------------------------------------------------------------------------


def test_the_residual_is_identically_zero_not_merely_small():
    """S14's target, as an identity.

    `== 0` in sympy, not `approx(0)`. The claim is exact and stating it to a
    tolerance would be a weaker statement about a stronger fact.
    """
    residual = roundtrip_residual()
    assert list(residual) == [0, 0, 0], residual


def test_the_two_halves_carry_equal_and_opposite_Hv():
    """The cancellation is exhibited, not asserted.

    It is the **same** $H$ twice: $-H$ from $v_a\\dot{\\overline{\\ln T}}$ in the
    gradient, $+H$ from $\\tfrac13\\Theta$ in $v^b\\nabla_bu_a$. If a future
    change makes one of them vanish the sum is still zero and the physics is
    wrong, so both are asserted separately.
    """
    fc = FrameChange.generic()
    grad, accel = _vec("DlnT"), _vec("A")

    from_gradient = sp.expand(boosted_temperature_gradient(grad, fc)[0] - grad[0])
    from_accel = sp.expand(
        boosted_acceleration(accel, fc)[0] - accel[0] - fc.v_dot[0]
    )

    a = from_gradient.coeff(fc.H)
    b = from_accel.coeff(fc.H)
    assert a != 0, "the gradient half has lost its Hv term"
    assert b != 0, "the acceleration half has lost its Hv term"
    assert sp.simplify(a + b) == 0, (a, b)


def test_shear_and_vorticity_are_removed_by_order_not_by_hand():
    """They must be *written* into the acceleration and then expanded away.

    `boosted_acceleration` carries $\\sigma_{ab}v^b$ and
    $\\epsilon_{abc}v^b\\omega^c$ in full before truncating. Both are
    $O(\\varepsilon^2)$ and vanish at first order — which is *why* no shear
    appears in a rank-one bracket, and is a statement about order rather than
    about rank.
    """
    fc = FrameChange.generic()
    result = boosted_acceleration(_vec("A"), fc)
    leftover = {str(s) for s in result.free_symbols}
    assert not any(s.startswith("sigma") for s in leftover), leftover
    assert not any(s.startswith("omega") for s in leftover), leftover


def test_the_shear_terms_really_were_there_before_truncation():
    """Guards the test above against passing because nothing was ever added.

    If `boosted_acceleration` were rewritten to omit the shear contraction, the
    previous test would still pass and the derivation would have become an
    assertion. This fails in that case.
    """
    import inspect

    from functions import frames

    src = inspect.getsource(frames.boosted_acceleration)
    assert "fc.sigma * fc.v" in src, "the shear contraction is no longer formed"
    assert "omega" in src, "the vorticity contraction is no longer formed"


def test_a_boost_with_no_velocity_changes_nothing():
    """The degenerate case, which must be exactly trivial."""
    fc = FrameChange.generic()
    zero = sp.zeros(3, 1)
    still = FrameChange(v=zero, v_dot=zero, H=fc.H, sigma=fc.sigma, omega=fc.omega)
    grad, accel = _vec("DlnT"), _vec("A")
    before = bracket_rank1(grad, accel)
    after = bracket_rank1(
        boosted_temperature_gradient(grad, still),
        boosted_acceleration(accel, still),
    )
    assert list(sp.expand(after - before)) == [0, 0, 0]


def test_a_numerical_evaluation_agrees_with_the_identity():
    """The re-runnable version, for a reader who does not trust the algebra.

    Substituting arbitrary values into an identity must give zero in floating
    point too. This is the weaker statement and is kept because it is the one
    someone can check in ten seconds.
    """
    import random

    residual = roundtrip_residual()
    subs = {s: random.uniform(-1.0, 1.0) for s in residual.free_symbols}
    values = [float(sp.N(c.subs(subs))) for c in residual]
    assert all(abs(x) < 1e-15 for x in values), values
