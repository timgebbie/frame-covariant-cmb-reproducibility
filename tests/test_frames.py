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
# The curvature half: what a numerical change of frame additionally needs
# ---------------------------------------------------------------------------
#
# The tests above settle the rank-one bracket. These settle the pieces F5 and
# F7 need, and they are held to the same standard: assert the mechanism, and
# show that the identity *fails* for a wrong rule, so that a passing test is
# evidence rather than a tautology.


def test_the_electric_weyl_tensor_is_invariant_under_the_frame_shift():
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


def test_the_cdm_frame_condition_is_the_geodesic_euler_equation():
    r"""$\tilde A_a=0 \Rightarrow v'+\mathcal Hv=-k\Phi_A$.

    The CDM frame is **not** imposed as an ODE someone wrote down; it falls
    out of setting the boosted acceleration to zero. That the result is the
    Euler equation of a pressureless geodesic fluid is the check: it is what the
    cold dark matter obeys.

    Decisions **S8a** and **S29**: $A_a=0$ *is* the CDM frame, exactly, because
    pressureless and collisionless means no non-gravitational force and hence
    geodesic --- and it is the energy frame of the CDM **component**,
    $q^C_a=0$, which is **not** the total-energy frame. Finding T-29 is the
    eight days this bundle spent conflating the two.
    """
    import sympy as sp

    from functions.frames import (
        cdm_frame_velocity_equation,
        harmonic_potential_shift,
    )

    k, H = sp.symbols("k mathcalH", positive=True)
    pa, v, vp = sp.symbols("Phi_A v vprime", real=True)

    # the boosted acceleration potential, set to zero
    boosted = pa + harmonic_potential_shift(v, vp, H, k)
    condition = sp.simplify(sp.expand(boosted * k))

    assert sp.simplify(condition - cdm_frame_velocity_equation(pa, v, vp, H, k)) == 0


def test_the_dipole_is_the_only_multipole_the_frame_moves():
    r"""$\tilde\tau_a=\tau_a-v_a$, and $\tilde\tau_{A_\ell}=\tau_{A_\ell}$ for $\ell\ge2$.

    GDE99 Eq. (37) and the list below its Eq. (35), as Paper 1 Sec. VI A records
    them. The $\ell\ge2$ half is the standard the whole frame-covariance section
    has to meet: **any frame dependence surviving at $\ell\ge2$ is an
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


# --------------------------------------------------------------------------
# The two-frame environment: what the grid it was built for guarantees, and
# what each frame leaves in the rank-zero and rank-two sectors. These stand
# behind figures F2 and F7, which are the pictures of them.
# --------------------------------------------------------------------------


def test_an_environment_refuses_a_k_its_eta_grid_cannot_resolve():
    r"""Finding **T-34**, and **T-3** before it.

    `build_environment` sizes the $\eta$ grid from the $k$ it is given, six
    samples per $j_\ell$ oscillation at that $k$ and no more. `figure_f7_frames`
    built one for the probe modes, $k=140$, and then integrated to $k=420$:
    **two samples per oscillation**, below Nyquist, and the aliased integrand
    returns a smooth, plausible spectrum of the wrong shape rather than an
    error. `pipeline.run` has raised on this since T-3; this is the same guard
    on the second entry point to the same physics.
    """
    import pytest

    from functions.spectra.two_frame import build_environment, coefficient_sets

    env = build_environment(140.0)
    assert env.k_max == 140.0
    coefficient_sets(140.0, env)                      # at the edge, allowed

    with pytest.raises(ValueError) as excinfo:
        coefficient_sets(420.0, env)
    message = str(excinfo.value)
    # The message has to carry the number, because "too coarse" is not
    # actionable and "2.0 samples per oscillation" is.
    assert "2.0 samples" in message
    assert "T-34" in message


def test_the_newtonian_frame_leaves_the_shear_sectors_empty_and_the_cdm_frame_does_not():
    r"""(110), and the claim footnote 29 on p. 365 makes about truncation.

    The Newtonian frame is $\tilde\sigma_{ab}=0$, so ranks zero and two of (89)
    have nothing in them: $C_0\equiv C_2\equiv0$. That is why a truncation which
    kills the shear exactly --- Appendix E --- **costs nothing there**, and the
    footnote is right to say the frame removes the problem. It removes it by
    having no shear to lose, which is the content of figure F2's lower panel and
    the reason the panel is drawn in two frames rather than one.

    Asserting only the Newtonian half would be the weak test: zero is what a
    sector that was never filled also returns. So the CDM frame is asserted
    **non**-zero in the same breath.
    """
    import numpy as np

    from functions.spectra.bessel_table import BesselTable
    from functions.spectra.integral_solution import required_multipoles
    from functions.spectra.two_frame import (
        build_environment,
        coefficient_sets,
        transfer_by_rank,
    )

    ells = np.array([2, 20, 120])
    env = build_environment(140.0)
    needed = required_multipoles(ells)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(140.0 * (env.background.eta_0 - env.eta[0])) + 20.0)

    for k in (20.0, 60.0, 140.0):
        newtonian, cdm = coefficient_sets(float(k), env)
        flat = transfer_by_rank(ells, float(k), newtonian, env, table)
        tilted = transfer_by_rank(ells, float(k), cdm, env, table)

        assert np.allclose(flat[0], 0.0, atol=0.0), f"(110) at k={k}: rank 0"
        assert np.allclose(flat[2], 0.0, atol=0.0), f"(110) at k={k}: rank 2"
        # and rank 1 therefore carries the whole of it
        assert np.allclose(flat[1], flat[-1], rtol=1e-12)

        # The CDM frame has the shear, so it has something to lose.
        assert np.any(np.abs(tilted[0]) > 0.0)
        assert np.any(np.abs(tilted[2]) > 0.0)
        assert not np.allclose(tilted[1], tilted[-1], rtol=1e-6)


def test_102_cannot_make_its_frame_response_depend_on_the_multipole():
    r"""Finding **T-31**, which is what figure F7 reports instead of its plan.

    (37) moves the dipole and leaves $\tau_{A_\ell}$ alone for $\ell\ge2$, so the
    plan asked F7 to show the dipole standing an order of magnitude apart. It
    does not, and the reason is structural: **(102) builds every multipole from
    the same three $\ell$-independent coefficients $C_0,C_1,C_2$**, projected
    with $j_\ell$. A change of frame moves the $C_A$ and nothing else, so the
    frame response it can produce is $\ell$-independent up to the differing
    $j_\ell$ weights of three lines.

    The test is the consequence: the dipole's frame response sits within a small
    factor of the median over $\ell\ge2$, not orders of magnitude above it. It
    is written as a ceiling rather than an equality because the three $j_\ell$
    weights genuinely do differ.
    """
    import numpy as np

    from functions.spectra.bessel_table import BesselTable
    from functions.spectra.integral_solution import (
        integral_solution,
        required_multipoles,
    )
    from functions.spectra.two_frame import build_environment, coefficient_sets

    ells = np.array([1, 2, 5, 20, 80, 200])
    env = build_environment(140.0)
    needed = required_multipoles(ells)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(140.0 * (env.background.eta_0 - env.eta[0])) + 20.0)

    for k in (20.0, 60.0):
        diffusion = float(np.exp(-((k / env.damping_k) ** 2)))
        totals = [
            integral_solution(
                ells, coefficients=cs.coefficients, c1_prime=cs.c1_prime,
                c2_second=cs.c2_second, c2_prime_star=cs.c2_prime_star,
                table=table, weight=env.weight, diffusion=diffusion,
                damping_total=diffusion, eta_star=env.eta_star,
                eta_0=float(env.background.eta_0)).total
            for cs in coefficient_sets(float(k), env)
        ]
        scale = np.maximum(np.abs(totals[0]), np.abs(totals[1]))
        response = np.abs(totals[1] - totals[0]) / scale

        ratio = response[0] / np.median(response[1:])
        assert 0.1 < ratio < 3.0, (
            f"k={k}: the dipole's frame response is {ratio:.2f}x the median "
            f"over l>=2. The plan expected an order of magnitude; T-31 is the "
            f"finding that (102) cannot produce one.")


def test_the_environment_applies_the_transfer_function_per_mode():
    r"""Finding **T-37**, and a guard for the thing that had no guard.

    Before this, `potentials()` handed $\Phi = D/a$ to **every** mode: there was
    no $k$ in the driving at all, so the acoustic peak heights carried no
    radiation-era suppression. `functions/spectra/transfer.py` had held the
    corrected (J.5) since v1.0.0 and nothing called it.

    **The wiring changed $\Phi$ by a factor of twenty-two at the top of the $k$
    grid and 386 tests passed unchanged**, which is the reason this test exists:
    a quantity nothing asserts is a quantity that can be switched off by
    accident as easily as it was switched on.

    What is asserted is the shape, the limits and the unit conversion --- the
    last being where a factor would actually hide, since the bundle works in
    $c/H_0$ and (J.5)'s fit is in Mpc$^{-1}$.
    """
    import numpy as np

    from functions.spectra.two_frame import HUBBLE_RADIUS_MPC, build_environment

    env = build_environment(1900.0)

    # T -> 1 on large scales, which is (J.3)'s stated normalisation.
    assert env.transfer_at(1.0) == pytest_approx(1.0, 3e-3)

    # The conversion: k_com = 1900 at h = 0.5 is 0.317 / Mpc, where T = 0.0455.
    k_mpc = 1900.0 * env.hubble_h / HUBBLE_RADIUS_MPC
    assert abs(k_mpc - 0.3169) < 1e-3
    assert abs(env.transfer_at(1900.0) - 0.0455) < 1e-3

    # Monotone decreasing, and the CDM k^-2 asymptote rather than the printed
    # +1/nu form, which grows without bound -- finding B-10.
    probes = np.array([1.0, 20.0, 140.0, 420.0, 1900.0])
    values = np.array([env.transfer_at(float(k)) for k in probes])
    assert np.all(np.diff(values) < 0.0)
    assert values[-1] < 0.1 * values[0]

    # The flag restores the pre-T-37 behaviour exactly, so the change is a
    # measurement rather than a claim.
    off = build_environment(1900.0, apply_transfer=False)
    assert all(off.transfer_at(float(k)) == 1.0 for k in probes)


def pytest_approx(value: float, rel: float):
    import pytest

    return pytest.approx(value, rel=rel)


# --------------------------------------------------------------------------
# C3.5: the rank-dependent rescaling, and what physics can and cannot fix.
# --------------------------------------------------------------------------


def test_c35_gravity_does_positive_work_on_the_cdm_which_fixes_lambda():
    r"""**The PI's route, finally written into the tree. Finding T-40.**

    `provenance/conventions.md` row **C3.5** was stipulated, and F2, F5 and F7
    all sat at R above it while `RELEASE-STATUS-v1.md` declared that nothing
    may. The route that settles it needs no harmonic convention at all:
    **cold dark matter falls into a potential well.**

    The CDM frame solves the geodesic Euler equation

    $$v' + \mathcal H v = -k\,\Phi_A ,$$

    and the physically unambiguous consequence is that **gravity does positive
    work on the matter in the growing mode**: the driving term and the velocity
    it produces point the same way, so $v\cdot(-k\Phi_A) > 0$ at every epoch.
    Flip it and the CDM climbs out of the well while the well deepens, which no
    cosmology does.

    **Why this fixes $\lambda$ and not $s_Q$, which is the distinction C3.5's
    own renaming note is about.** $\lambda$ is the *rank-dependent* rescaling
    $Q_{A_\ell}\to\lambda^\ell Q_{A_\ell}$. It therefore does **not** cancel
    between a rank-0 object and a rank-1 one --- and $\Phi_A$ is rank 0 while
    $v$ is rank 1. Their relative sign is physical, this test is that sign, and
    so $\lambda$ is fixed by it. $s_Q$ is a different animal and is handled in
    the test below.
    """
    import numpy as np

    from functions.background.flrw import CDM_MODEL
    from functions.spectra.frame_transform import cdm_frame_shift

    eta = np.linspace(0.05, 1.5, 3000)
    for k in (10.0, 60.0, 300.0):
        for amplitude in (+1.0, -1.0):      # the answer cannot depend on this
            phi_a = amplitude * np.ones_like(eta)
            shift = cdm_frame_shift(eta, phi_a, k, background=CDM_MODEL)
            work = shift.v * (-k * phi_a)
            assert np.all(work > 0.0), (
                f"k={k}, Phi={amplitude:+.0f}: gravity does negative work on the "
                f"CDM, i.e. it is climbing out of the well. Worst {work.min():.3e}")


def test_c35_the_control_climbs_out_of_the_well():
    r"""The half that matters. **S27's C rung requires a check that can fail**,
    and **T-24** is the finding that exists because a closure which could not
    fail was cited as though it could.

    The control is the same quadrature with the Euler equation's relative sign
    reversed --- $v'+\mathcal Hv=+k\Phi_A$ --- which is the opposite choice of
    $\lambda$. If that *also* gave positive work, the test above would be
    measuring the integrator rather than the physics.
    """
    import numpy as np

    from functions.background.flrw import CDM_MODEL

    eta = np.linspace(0.05, 1.5, 3000)
    k, phi_a = 60.0, np.ones_like(eta)
    a = np.asarray(CDM_MODEL.a_of_eta(eta), dtype=float)

    # +k Phi_A instead of -k Phi_A, by the same integrating factor.
    v0 = +k * float(phi_a[0]) * float(eta[0]) / 3.0
    integrand = a * phi_a
    cumulative = np.concatenate(
        ([0.0], np.cumsum(0.5 * (integrand[1:] + integrand[:-1]) * np.diff(eta))))
    v_wrong = (a[0] * v0 + k * cumulative) / a

    work = v_wrong * (-k * phi_a)
    assert np.all(work < 0.0), (
        "the control did not fail: the reversed Euler sign still gives positive "
        "work, so the test above is not measuring what it claims")


def test_c35_s_q_cancels_from_every_ratio_and_so_no_physics_can_fix_it():
    r"""**$s_Q$ is stipulated because it is unfixable, and that is a result, not
    a gap.**

    C3.5's renaming note separates two things that had been one. $s_Q$ is the
    sign of a scalar's own mode coefficient, $X = s_Q\sum_k X^{(k)}Q$, and the
    conventions sheet records its consequences under C3.2:

    $$\mathrm D_aX = -s_Q\,k\,X^{(k)}Q_a, \qquad
      \mathrm D_{\langle a}\mathrm D_{b\rangle}X = +s_Q\,k^2X^{(k)}Q_{ab}.$$

    **Every one of those carries exactly one factor of $s_Q$** --- the scalar,
    its gradient and its second gradient alike --- so $s_Q$ cancels from every
    ratio of them. No physical statement can depend on it, and therefore no
    physical argument can fix it. Stipulating it is the correct treatment and
    the sheet's own wording, *"not fixed by any source"*, is right.

    This test is that cancellation, asserted rather than asserted *about*. It is
    the reason C3.5 can be closed as a gate without a measurement: the half that
    physics can fix is $\lambda$, which the two tests above fix, and the half it
    cannot is immaterial to every number this bundle reports.
    """
    import sympy as sp

    s_q, k, x = sp.symbols("s_q k x", nonzero=True)

    scalar = s_q * x
    gradient = -s_q * k * x
    second = +s_q * k**2 * x

    # Each is linear in s_q, so every ratio is free of it.
    for a, b in ((gradient, scalar), (second, scalar), (second, gradient)):
        ratio = sp.simplify(a / b)
        assert s_q not in ratio.free_symbols, f"s_q survives in {ratio}"

    # And the statement that makes it a *choice*: both signs are admissible,
    # because the two differ by an overall factor that cancels throughout.
    for value in (+1, -1):
        assert sp.simplify((gradient / scalar).subs(s_q, value) + k) == 0


def test_102_must_carry_the_visibility_and_substituting_the_opacity_wrecks_it():
    r"""**(102) is the form in which the $\mathcal V$ substitution has already
    been made. Finding T-42.**

    `provenance/SOURCE-APPROXIMATIONS-v1.md`'s approximation **A-2** is about
    the pipeline's sources (178) and (179), where the weight is a free choice
    and $e^{-\kappa}$ --- (98)'s form --- is the one this bundle takes. The
    same record says where that stops being true: *"the visibility substitution
    enters at (102), described as a slow-decoupling correction."*

    **So (102) carries $\mathcal V$ intrinsically**, and substituting
    $e^{-\kappa}$ into its bracket is not a weighting choice --- it is using the
    wrong equation. This stream made that substitution on 2026-10-14, reasoning
    from A-2's heading without following its last paragraph, and it inverted the
    physics: the rank-0/2 sectors went from 0.5% of $C_\ell$ to **99.5%**, which
    is to say the rank-1 sector --- the one (110) says carries *everything* in
    the Newtonian frame --- carried nothing.

    This test is that signature, so the substitution cannot be made again
    quietly. The control is the half that matters.
    """
    import numpy as np

    from functions.spectra.angular import cl_covariant_route
    from functions.spectra.bessel_table import BesselTable
    from functions.spectra.integral_solution import required_multipoles
    from functions.spectra.pipeline import primordial_power
    from functions.spectra.two_frame import (
        build_environment,
        coefficient_sets,
        transfer_by_rank,
    )

    ells = np.array([2, 5, 10, 20])
    k_com = np.arange(0.05, 60.0, np.pi / 4.0)

    def rank_share(weight_name: str) -> np.ndarray:
        env = build_environment(float(k_com.max()), apply_transfer=False,
                                line_of_sight_weight=weight_name)
        needed = required_multipoles(ells)
        table = BesselTable.build(
            ell_max=int(needed.max()), ells=needed,
            x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)
        total = np.zeros((ells.size, k_com.size))
        rank1 = np.zeros_like(total)
        for j, k in enumerate(k_com):
            _, cdm = coefficient_sets(float(k), env)
            parts = transfer_by_rank(ells, float(k), cdm, env, table)
            total[:, j], rank1[:, j] = parts[-1], parts[1]
        power = primordial_power(k_com, n_s=1.0, amplitude=1.0)
        whole = np.array([cl_covariant_route(int(l), k_com, total[i], power)
                          for i, l in enumerate(ells)])
        one = np.array([cl_covariant_route(int(l), k_com, rank1[i], power)
                        for i, l in enumerate(ells)])
        return np.abs(whole - one) / np.abs(whole)

    # The default. Measured 2026-10-14: 0.47% to 0.62% over 2 <= l <= 20, which
    # is F2's published 0.54% at the quadrupole.
    #
    # **Re-measured 2026-10-18, after finding T-66: 0.22%, 0.11%, 0.71%, 5.19%
    # over l = 2, 5, 10, 20.** This is a **transcription** assertion --- it
    # pins (102)'s printed weight against the rank split that weight produces
    # --- and T-66 moved the rank-1 sector it is measured against, by reducing
    # the Thomson dipole by k_com. The rank-0/2 share therefore *rises*, which
    # is the expected direction: rank 1 got smaller, nothing else changed.
    # The threshold moves with the measurement and the old number is kept
    # above it, rather than the threshold being quietly raised. **The control
    # below is untouched and still inverts**, so the test still exercises the
    # thing it was written for.
    assert rank_share("printed").max() < 0.07, (
        "the rank-0/2 sectors have taken over the spectrum: (102)'s weight has "
        "been changed away from the visibility it is derived with. See T-42.")

    # The control: substituting e^{-kappa} inverts it. 99.3% to 99.7% measured.
    assert rank_share("opacity").min() > 0.9, (
        "the control did not fail, so this test is not exercising (102)'s "
        "weight at all")


def test_phi_is_exactly_one_in_einstein_de_sitter_whatever_the_reference():
    r"""**Finding T-52.** $D=a$ exactly in Einstein--de Sitter, so $\Phi\propto
    D/a$ is **1.0 everywhere** --- an identity, not a tolerance.

    `potentials`' `constant_below` sets where `growth_factor` starts, and
    `growth_factor` integrates an explicit ODE whose friction is $aH=2/\eta$
    and whose source is $\propto1/a$. Started at $\eta=10^{-9}$ those are
    $2\times10^9$ and $10^{18}$, and it returns $1.58\times10^{-6}$ for a
    quantity that is identically one.

    **Every Einstein--de Sitter amplitude in the bundle would have been
    rescaled by six orders of magnitude**, silently, when the acoustic start
    was derived per mode (**S40**). Nothing in the physics tests would have
    seen it: they compare shapes, ratios and two routes that would both have
    carried the same factor. What caught it was the *control* half of T-42's
    test --- the assertion whose job is to fail --- which stopped firing.

    This pins the identity directly, so the next reference that is too early
    fails here rather than four tests away.
    """
    import numpy as np

    from functions.background.flrw import CDM_MODEL
    from functions.spectra.decoupling import RecombinationHistory
    from functions.spectra.potentials import potentials

    recombination = RecombinationHistory.build(CDM_MODEL, n_eta=4000)
    eta = np.linspace(float(recombination.eta[0]), float(CDM_MODEL.eta_0), 2000)

    for reference in (None, float(recombination.eta[0]), 2.0 * float(recombination.eta[0])):
        phi_a, phi_h = potentials(CDM_MODEL, eta, constant_below=reference)
        assert np.allclose(phi_a, 1.0, rtol=0.0, atol=1e-10), (
            f"Phi_A is not identically 1 in Einstein-de Sitter with "
            f"constant_below={reference!r}: it ranges "
            f"{phi_a.min():.6g} to {phi_a.max():.6g}. D = a there, so this is "
            "an identity. See finding T-52 --- a reference early enough to "
            "break the growth integration returns a smooth, plausible, wrong "
            "answer.")
        assert np.allclose(phi_h, -phi_a), "Phi_H = -Phi_A at this order"
