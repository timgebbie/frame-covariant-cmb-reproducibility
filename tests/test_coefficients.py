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


def _energy_frame_fixture():
    """One configuration, shared by the closure tests and the T-24 sign tests."""
    n = 400
    eta = np.linspace(0.1, 3.0, n)
    a = np.linspace(1e-3, 1.0, n)
    cH, rho = np.full(n, 1.3), 3.0 * np.ones(n)
    phi_a = 0.1 / (1.0 + eta**2)
    v = 0.05 * np.exp(-(((eta - 0.5) / 0.4) ** 2))
    return dict(n=n, eta=eta, a=a, cH=cH, rho=rho, phi_a=phi_a, v=v, k=60.0)


def test_the_energy_frame_closes_three_ways():
    r"""**The frame machinery against the field equations.**

    Three relations, and any two give the third:

    1. $\sigma=-k_{\rm phys}v$ --- **(31)**, the *general* transformation
       $\tilde\sigma_{ab}\approx\sigma_{ab}+\mathcal D_{\langle a}v_{b\rangle}$,
       with $\tilde\sigma=0$ in the Newtonian frame and $v=-v^N$. **Not (40)**,
       which contradicts it --- finding **B-13**;
    2. $\dot\sigma=-2H\sigma-E$ --- Appendix G's shear equation with $A_a=0$;
    3. $v'+\mathcal Hv=-k_{\rm com}\Phi_A$ --- the energy-frame Euler equation,
       derived independently in `frames.py` from **(32)**.

    It passes --- and the two tests below say what that is and is not worth.
    """
    from functions.spectra.coefficients import energy_frame_shear

    f = _energy_frame_fixture()
    a, cH, k, v, phi_a = f["a"], f["cH"], f["k"], f["v"], f["phi_a"]

    _, sigma_dot, _ = energy_frame_shear(k, v=v, phi_a=phi_a, scale_factor=a,
                                         conformal_hubble=cH, rho=f["rho"])

    # (3): v' from the Euler equation, not from differentiating v
    v_prime = -cH * v - k * phi_a
    # (1): sigma = -k_phys v, so sigma-dot = -(k/a^2)(v' - script-H v)
    from_frame_transformation = -(k / a**2) * (v_prime - cH * v)

    worst = (np.max(np.abs(from_frame_transformation - sigma_dot))
             / np.max(np.abs(from_frame_transformation)))
    assert worst < 1e-14, f"the energy frame does not close: {worst:.2e}"


def test_T24_the_closure_is_an_identity_in_both_conventions():
    r"""**Finding T-24, resolved.** The closure above is evidence for no convention.

    Write a scalar's gradient as $\mathcal D_aX=\lambda k_{\rm phys}XQ_a$ and
    the raising operator as $\mathcal D_{\langle a}Q_{b\rangle}=rk_{\rm
    phys}Q_{ab}$. With the general rule **(31)**, the three relations close
    **for every $\lambda$ and every $r$** --- as they must, being a statement
    about physical fields and not about a basis.

    The corollary is the whole of T-24: **this closure cannot be cited for
    C3.5**, the claim in `GENERIC-SOURCE-DERIVATIVES-v1.md` that it
    "corroborates the magnitude" is withdrawn, and an identity is why it could
    not catch the sign error that was made inside it.
    """
    f = _energy_frame_fixture()
    a, cH, k, v, phi_a = f["a"], f["cH"], f["k"], f["v"], f["phi_a"]

    for lam in (+1.0, -1.0):
        for r in (-1.0, +1.0):
            v_prime = -lam * k * phi_a - cH * v           # (32) with A_a = 0
            sigma = r * (k / a) * v                       # (31) with sigma~ = 0
            electric = lam * r * (k / a) ** 2 * phi_a     # D_<a D_b> Phi_A
            from_transformation = r * (k / a**2) * (v_prime - cH * v)
            from_appendix_g = -2.0 * (cH / a) * sigma - electric
            worst = (np.max(np.abs(from_transformation - from_appendix_g))
                     / np.max(np.abs(from_transformation)))
            assert worst < 1e-14, (
                f"lambda={lam:+.0f}, r={r:+.0f} does not close: {worst:.2e}")


def test_B13_the_printed_n_t1_does_not_close_and_the_general_rule_does():
    r"""**Finding B-13**, pinned to a number: (40) contradicts (31), by $2E_{ab}$.

    *Annals II* gives the general frame transformations at (31)--(37), cited to
    Maartens, Gebbie & Ellis, then specialises them to the Newtonian threading
    at (40)--(45). Two of the six change sign on the way:

    | | general | specialised |
    |---|---|---|
    | shear | **(31)** $\tilde\sigma_{ab}\approx\sigma_{ab}+\mathcal D_{\langle a}v_{b\rangle}$ | **(40)** $0\approx\sigma_{ab}-\mathcal D_{\langle a}v^N_{b\rangle}$ |
    | energy flux | **(34)** $\tilde q_a\approx q_a-(\rho+p)v_a$ | **(45)** $\tilde q_a\approx q_a+(\rho+p)v^N_a$ |

    (32), (33) and (37) keep their signs in (41), (42), (44) and (43). The
    sharpest internal contradiction is (33) against (40): $\tilde\Theta\approx
    \Theta+\mathrm{div}\,v$ is the **trace** of the same derivative whose
    trace-free part is $\tilde\sigma_{ab}$, it keeps its plus in both places,
    and (40) does not.

    With (40) the energy frame misses closure by exactly $2E_{ab}$, for every
    convention.
    """
    f = _energy_frame_fixture()
    a, cH, k, v, phi_a = f["a"], f["cH"], f["k"], f["v"], f["phi_a"]
    lam, r = 1.0, -1.0                                    # C3.5 and C4.2

    v_prime = -lam * k * phi_a - cH * v
    electric = lam * r * (k / a) ** 2 * phi_a
    sigma_printed = -r * (k / a) * v                      # (40) as printed
    from_transformation = -r * (k / a**2) * (v_prime - cH * v)
    from_appendix_g = -2.0 * (cH / a) * sigma_printed - electric

    assert np.allclose(from_transformation - from_appendix_g, 2.0 * electric,
                       rtol=1e-12, atol=0.0), (
        "the (40) residual is no longer 2 E_ab --- B-13 has changed shape")


def test_the_two_modules_now_agree_on_E_and_on_sigma():
    r"""The two $E_{ab}$ in this repository, reconciled.

    `frames.py::weyl_electric_amplitude` returns
    $-\tfrac12(k/a)^2(\Phi_A-\Phi_H)$, written for criterion 2 before
    `coefficients.py` existed. `energy_frame_shear` must give the same thing:
    both are $\mathcal D_{\langle a}\mathcal D_{b\rangle}\Phi_A$ under C3.5 and
    C4.2, and for one sitting they disagreed by a sign --- the shape T-24 took
    before (31) settled it.

    $\sigma=-k_{\rm phys}v$ is checked against (31) directly, with no reference
    to the closure, because the closure is an identity and checks nothing.
    """
    from functions.frames import weyl_electric_amplitude
    from functions.spectra.coefficients import energy_frame_shear

    f = _energy_frame_fixture()
    a, cH, k, v, phi_a = f["a"], f["cH"], f["k"], f["v"], f["phi_a"]
    phi_h = -phi_a

    sigma, sigma_dot, _ = energy_frame_shear(
        k, v=v, phi_a=phi_a, phi_h=phi_h, scale_factor=a,
        conformal_hubble=cH, rho=f["rho"])

    assert np.allclose(sigma, -(k / a) * v, rtol=1e-14, atol=0.0)

    electric_used = -2.0 * (cH / a) * sigma - sigma_dot
    # sympy Rational against a numpy array returns an object array
    electric_frames = np.asarray(
        weyl_electric_amplitude(phi_a, phi_h, k, a), dtype=float)
    assert np.allclose(electric_used, electric_frames, rtol=1e-13, atol=0.0)


def test_the_closure_is_not_vacuous():
    r"""**The control.** Without the Euler equation the two routes must *not*
    agree --- they differ by exactly $-(k/a^2)(v'+\mathcal Hv)-E$, which is zero
    only on the energy-frame solution.
    """
    from functions.spectra.coefficients import energy_frame_shear

    f = _energy_frame_fixture()
    eta, a, cH, k, v, phi_a = (f["eta"], f["a"], f["cH"], f["k"], f["v"], f["phi_a"])

    _, sigma_dot, _ = energy_frame_shear(k, v=v, phi_a=phi_a, scale_factor=a,
                                         conformal_hubble=cH, rho=f["rho"])
    v_prime_arbitrary = np.gradient(v, eta, edge_order=2)   # NOT the Euler solution
    from_frame = -(k / a**2) * (v_prime_arbitrary - cH * v)

    gap = np.max(np.abs(from_frame - sigma_dot)) / np.max(np.abs(from_frame))
    assert gap > 1e-3, "the two routes agree for arbitrary v; the closure is vacuous"

    predicted = -(k / a**2) * (v_prime_arbitrary + cH * v) - (k / a) ** 2 * phi_a
    residual = np.max(np.abs((from_frame - sigma_dot) - predicted)) / np.max(np.abs(from_frame))
    assert residual < 1e-14, f"the gap is not the predicted expression: {residual:.2e}"


# ---------------------------------------------------------------------------
# The energy frame as a second frame: T-25, T-26, and the control that caught
# T-25. See `provenance/BUNDLE-DEFECTS-v1.md`.
# ---------------------------------------------------------------------------


def _two_frame_fixture(k=60.0, n=600):
    """A consistent Newtonian history plus a threading shift, built by hand.

    Synthetic, so the test is fast and so that `v` is **not** the quadrature's
    own output --- only `v_prime` is tied to it, through the Euler equation,
    which is the one relation `energy_set` relies on.
    """
    from functions.spectra.coefficients import background_fluid

    eta = np.linspace(0.05, 2.0, n)
    a = (eta / eta[-1]) ** 2                       # Einstein-de Sitter
    cH = 2.0 / eta
    # script-H^2 = h0^2/a for EdS, so 4/eta^2 = h0^2 eta_0^2/eta^2 fixes h0.
    # Derived, not fitted: a rescaling factor here would hide exactly the
    # background inconsistency `energy_set`'s (a sigma)' guard exists to catch.
    rho, pressure, cH_prime = background_fluid(a, omega_m=1.0, h0=2.0 / eta[-1])
    assert np.allclose(rho, 3.0 * (cH / a) ** 2, rtol=1e-12)

    phi_a = 0.1 / (1.0 + 0.3 * eta**2)
    phi_a_prime = -0.1 * 0.6 * eta / (1.0 + 0.3 * eta**2) ** 2
    phi_h, phi_h_prime = -phi_a, -phi_a_prime
    delta_t = 0.2 * np.cos(0.8 * k * eta) * np.exp(-eta)
    tau_1 = 0.1 * np.sin(0.8 * k * eta) * np.exp(-eta)
    kappa_prime = 300.0 * np.exp(-(((eta - 0.35) / 0.08) ** 2))
    kappa_second = np.gradient(kappa_prime, eta, edge_order=2)
    r_baryon = 0.6 * a
    r_baryon_prime = cH * r_baryon                 # R propto a, exactly
    v = 0.4 * eta * np.exp(-0.2 * eta)
    v_prime = -cH * v - k * phi_a                  # the Euler equation
    return dict(eta=eta, k=k, a=a, cH=cH, cH_prime=cH_prime, rho=rho,
                pressure=pressure, phi_a=phi_a, phi_a_prime=phi_a_prime,
                phi_h=phi_h, phi_h_prime=phi_h_prime, delta_t=delta_t,
                tau_1=tau_1, kappa_prime=kappa_prime, kappa_second=kappa_second,
                r_baryon=r_baryon, r_baryon_prime=r_baryon_prime,
                v=v, v_prime=v_prime, eta_star=0.35)


def _build_both(f):
    from functions.spectra.coefficients import energy_set, newtonian_set
    common = dict(
        delta_t=f["delta_t"], phi_a=f["phi_a"], phi_a_prime=f["phi_a_prime"],
        phi_h_prime=f["phi_h_prime"], tau_1=f["tau_1"],
        kappa_prime=f["kappa_prime"], kappa_double_prime=f["kappa_second"],
        conformal_hubble=f["cH"], r_baryon=f["r_baryon"],
        r_baryon_prime=f["r_baryon_prime"])
    n = newtonian_set(f["eta"], f["k"], **common)
    e = energy_set(f["eta"], f["k"], phi_h=f["phi_h"],
                   conformal_hubble_prime=f["cH_prime"], scale_factor=f["a"],
                   rho=f["rho"], pressure=f["pressure"], v=f["v"],
                   v_prime=f["v_prime"], eta_star=f["eta_star"], **common)
    return n, e


def test_the_frame_shift_of_every_coefficient_is_the_closed_form_one():
    r"""**The control that found T-25.** Five shifts, five closed forms.

    A frame change from the Newtonian threading to the energy one shifts each
    coefficient of (89) by something that can be written down in one line, and
    `energy_set` must reproduce all five **exactly** --- not nearly:

        dC_0  = +5/2 k v            (the shear sector, empty before)
        dC_1  = -( v' - kappa' v )/k
        dC_2  = + v/k
        dC_1' = -( v'' - kappa'' v - kappa' v' )/k
        dC_2''= + v''/k

    with $v''=-\mathcal H'v-\mathcal Hv'-k\Phi_A'$ from the Euler equation.
    The first draft of `energy_set` passed four of these and failed $C_1'$ by a
    factor of $k_{\rm com}$ --- finding **T-25**, the two differently
    normalised $\kappa'v_B$ arguments --- and **that is how it was found**. The
    (102) totals it produced were wrong by sixty-fold and looked like physics.
    """
    f = _two_frame_fixture()
    n, e = _build_both(f)
    k, v, vp = f["k"], f["v"], f["v_prime"]
    cH, cHp, kp, kpp = f["cH"], f["cH_prime"], f["kappa_prime"], f["kappa_second"]
    vpp = -cHp * v - cH * vp - k * f["phi_a_prime"]

    def worst(got, want):
        return np.max(np.abs(got - want)) / np.max(np.abs(want))

    assert worst(e.coefficients.c0 - n.coefficients.c0, 2.5 * k * v) < 1e-13
    assert worst(e.coefficients.c1 - n.coefficients.c1, -(vp - kp * v) / k) < 1e-13
    assert worst(e.coefficients.c2 - n.coefficients.c2, v / k) < 1e-13
    assert worst(e.c1_prime - n.c1_prime, -(vpp - kpp * v - kp * vp) / k) < 1e-13
    assert worst(e.c2_second - n.c2_second, vpp / k) < 1e-13


def test_the_newtonian_set_is_unmoved_by_the_energy_frame_machinery():
    """The Newtonian shear sector stays empty, which is (110)."""
    f = _two_frame_fixture()
    n, e = _build_both(f)
    assert n.coefficients.shear_sector_is_empty
    assert not e.coefficients.shear_sector_is_empty


def test_T26_the_appendix_G_route_to_C2_second_loses_every_significant_figure():
    r"""**Finding T-26, pinned: an exact relation evaluated in the wrong variable.**

    $C_2''$ has two routes. Through $v$ it is $v''/k$ --- three closed-form
    terms. Through Appendix G it is $-(a\sigma)''/k^2$ with $(a\sigma)''=
    a''\sigma+2a'\sigma'+a\sigma''$ and $\ddot\sigma$ from the Bianchi
    propagation equation. **They are the same number and only one of them can
    be computed**: $\ddot\sigma$ runs to $10^{15}$ against a result of order
    $10^{-3}$, so the second route cancels away about eighteen significant
    figures and returns noise.

    T-23 established that a derivative must come from a published relation
    rather than from a spline. T-26 is the other edge: the published relation
    must also be *evaluated* in a variable that does not cancel. The test
    asserts both halves --- the first and second $C_2$ derivatives agree where
    nothing cancels, and disagree completely where everything does --- so that
    the day someone reinstates `c2_derivatives` in `energy_set` it fails.
    """
    from functions.spectra.coefficients import c2_derivatives, energy_frame_shear

    f = _two_frame_fixture()
    k, v, vp, cH, cHp = f["k"], f["v"], f["v_prime"], f["cH"], f["cH_prime"]
    vpp = -cHp * v - cH * vp - k * f["phi_a_prime"]
    sigma, sd, sdd = energy_frame_shear(
        k, v=v, phi_a=f["phi_a"], phi_h=f["phi_h"], scale_factor=f["a"],
        conformal_hubble=cH, rho=f["rho"], pressure=f["pressure"])
    c2, c2p, c2pp = c2_derivatives(
        k, sigma=sigma, sigma_dot=sd, sigma_ddot=sdd, conformal_hubble=cH,
        scale_factor=f["a"], rho=f["rho"], pressure=f["pressure"])

    def worst(got, want):
        return np.max(np.abs(got - want)) / np.max(np.abs(want))

    # where nothing cancels, the two routes are the same number
    assert worst(c2, v / k) < 1e-13, "C_2 itself must agree to machine precision"
    assert worst(c2p, vp / k) < 1e-8, "C_2' is well conditioned both ways"
    # and where everything cancels, the Appendix G route is noise
    assert worst(c2pp, vpp / k) > 1e-2, (
        "the sigma-ddot route to C_2'' no longer loses its digits. If the "
        "grouping has been reformulated so that it is conditioned, this test "
        "is now wrong and T-26 should be closed rather than pinned.")


# ---------------------------------------------------------------------------
# The rank decomposition F5 is drawn in. See `functions/spectra/two_frame.py`.
# ---------------------------------------------------------------------------


def test_the_ranks_add_to_the_total_in_the_transfer_but_not_in_cl():
    r"""**The two halves of F5's bottom panel, as one test.**

    (102) is **linear** in $C_0,C_1,C_2$, so the three rank contributions to the
    transfer function sum to it exactly. $C_\ell$ is **quadratic** in the
    source, so the three contributions to $C_\ell$ do *not*: the difference is
    twice the three cross-spectra, and the test asserts both --- that the
    reconstruction with the cross terms is exact and that without them it is
    not. A figure whose parts do not sum to the whole drawn beside them is a
    figure that needs this test to exist.
    """
    from functions.spectra.angular import cl_covariant_route
    from functions.spectra.bessel_table import BesselTable
    from functions.spectra.integral_solution import required_multipoles
    from functions.spectra.two_frame import (
        build_environment,
        cl_cross,
        coefficient_sets,
        transfer_by_rank,
    )

    ells = np.array([2, 10, 60], dtype=int)
    k_com = np.array([5.0, 40.0, 120.0])
    env = build_environment(float(k_com.max()))
    needed = required_multipoles(ells)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(k_com.max() * (env.background.eta_0 - env.eta[0])) + 20.0)

    transfer = {r: np.zeros((ells.size, k_com.size)) for r in (-1, 0, 1, 2)}
    newtonian_rank = {r: np.zeros((ells.size, k_com.size)) for r in (-1, 0, 1, 2)}
    for j, k in enumerate(k_com):
        newtonian, energy = coefficient_sets(float(k), env)
        for r, values in transfer_by_rank(ells, float(k), energy, env, table).items():
            transfer[r][:, j] = values
        for r, values in transfer_by_rank(ells, float(k), newtonian, env, table).items():
            newtonian_rank[r][:, j] = values

    # linear in the C_A: the ranks add
    summed = sum(transfer[r] for r in (0, 1, 2))
    assert np.allclose(summed, transfer[-1], rtol=1e-12, atol=0.0)

    # and the Newtonian frame puts everything in rank one --- that is (110)
    assert np.all(newtonian_rank[0] == 0.0)
    assert np.all(newtonian_rank[2] == 0.0)
    assert np.allclose(newtonian_rank[1], newtonian_rank[-1], rtol=1e-12, atol=0.0)

    # quadratic in the source: the ranks do NOT add in C_l
    power = np.ones_like(k_com)
    cl = {r: np.array([cl_covariant_route(int(l), k_com, transfer[r][i], power)
                       for i, l in enumerate(ells)]) for r in (-1, 0, 1, 2)}
    cross = [np.array([cl_cross(int(l), k_com, transfer[a][i], transfer[b][i], power)
                       for i, l in enumerate(ells)])
             for a, b in ((0, 1), (0, 2), (1, 2))]
    autos = sum(cl[r] for r in (0, 1, 2))

    assert np.allclose(autos + 2.0 * sum(cross), cl[-1], rtol=1e-10, atol=0.0)
    gap = np.max(np.abs(autos - cl[-1]) / np.abs(cl[-1]))
    assert gap > 1e-3, (
        "the auto-spectra alone reproduce C_l, so the cross terms are "
        "negligible and F5's bottom panel is drawing nothing")
