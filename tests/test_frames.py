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


# ---------------------------------------------------------------------------
# The curvature half: what a numerical change of threading additionally needs
# ---------------------------------------------------------------------------
#
# The tests above settle the rank-one bracket. These settle the pieces F5 and
# F7 need, and they are held to the same standard: assert the mechanism, and
# show that the identity *fails* for a wrong rule, so that a passing test is
# evidence rather than a tautology.


def test_the_electric_weyl_tensor_is_invariant_under_the_threading_shift():
    r"""$\tilde E_{ab}=E_{ab}$ identically — the curvature half of criterion 2.

    $E_{ab}=\frac12\D_{\la a}\D_{b\ra}(\Phi_A-\Phi_H)$ (GDE99 Eq. (24)) vanishes
    in the background, so Stewart-Walker makes it first-order frame-invariant.
    The residual is built by shifting both potentials by the amount the
    *acceleration* rule forces and rebuilding $E_{ab}$ from the result.
    """
    from functions.frames import weyl_invariance_residual

    assert weyl_invariance_residual() == 0


def test_the_weyl_invariance_fails_for_any_other_potential_rule():
    r"""The negative control. Without it the test above proves nothing.

    If $\Phi_H$ did not shift, or shifted the other way, the residual is
    proportional to $(v'+\mathcal Hv)$ and non-zero. So "both potentials shift
    by the same amount" is **forced** by the invariance rather than chosen to
    make a residual vanish.
    """
    import sympy as sp

    from functions.frames import (
        EPS,
        harmonic_potential_shift,
        weyl_electric_amplitude,
    )

    k, a, H = sp.symbols("k a mathcalH", positive=True)
    pa, ph = sp.symbols("Phi_A Phi_H", real=True)
    v = EPS * sp.Symbol("v", real=True)
    vp = EPS * sp.Symbol("vprime", real=True)

    shift = harmonic_potential_shift(v, vp, H, k)
    before = weyl_electric_amplitude(pa, ph, k, a)

    frozen = sp.simplify(weyl_electric_amplitude(pa + shift, ph, k, a) - before)
    flipped = sp.simplify(weyl_electric_amplitude(pa + shift, ph - shift, k, a) - before)

    assert frozen != 0, "a rule that leaves Phi_H alone must not pass"
    assert flipped != 0, "a rule that flips the sign must not pass"

    # **And the failure has the shape the derivation predicts**, which is the
    # part that makes this a control rather than a complaint: the residual is
    # proportional to $(v'+\mathcal Hv)$ exactly, so it vanishes on that locus
    # and nowhere else. Substituting the *bare* symbols, because sympy factors
    # EPS out of the product and `vp` as built here is `EPS*vprime`.
    bare_v, bare_vp = sp.Symbol("v", real=True), sp.Symbol("vprime", real=True)
    assert sp.simplify(frozen.subs({bare_vp: -H * bare_v})) == 0
    assert sp.simplify(flipped.subs({bare_vp: -H * bare_v})) == 0


def test_the_energy_frame_condition_is_the_geodesic_euler_equation():
    r"""$\tilde A_a=0 \Rightarrow v'+\mathcal Hv=-k\Phi_A$.

    The energy frame is **not** imposed as an ODE someone wrote down; it falls
    out of setting the boosted acceleration to zero. That the result is the
    Euler equation of a pressureless geodesic fluid is the check: it is what the
    cold dark matter obeys, and decision S8 is the statement that the CDM frame
    and the total-energy frame are the same threading for that reason.
    """
    import sympy as sp

    from functions.frames import (
        energy_frame_velocity_equation,
        harmonic_potential_shift,
    )

    k, H = sp.symbols("k mathcalH", positive=True)
    pa, v, vp = sp.symbols("Phi_A v vprime", real=True)

    # the boosted acceleration potential, set to zero
    boosted = pa + harmonic_potential_shift(v, vp, H, k)
    condition = sp.simplify(sp.expand(boosted * k))

    assert sp.simplify(condition - energy_frame_velocity_equation(pa, v, vp, H, k)) == 0


def test_the_dipole_is_the_only_multipole_the_threading_moves():
    r"""$\tilde\tau_a=\tau_a-v_a$, and $\tilde\tau_{A_\ell}=\tau_{A_\ell}$ for $\ell\ge2$.

    GDE99 Eq. (37) and the list below its Eq. (35), as Paper 1 Sec. VI A records
    them. The $\ell\ge2$ half is the standard the whole frame-covariance section
    has to meet: **any threading dependence surviving at $\ell\ge2$ is an
    artefact of the reduction, not physics.**
    """
    import sympy as sp

    import pytest

    from functions.frames import boosted_dipole, boosted_multipole

    tau, v = sp.symbols("tau v", real=True)

    assert sp.simplify(boosted_dipole(tau, v) - (tau - v)) == 0
    for ell in (2, 3, 7, 20):
        assert boosted_multipole(tau, ell) is tau

    # the monopole and dipole must not be silently passed through the l>=2 rule
    for ell in (0, 1):
        with pytest.raises(ValueError, match="invariant range"):
            boosted_multipole(tau, ell)
