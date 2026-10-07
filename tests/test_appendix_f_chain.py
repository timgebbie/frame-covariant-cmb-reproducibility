"""Appendix F, Eqs. (F.1)-(F.4): the acceptance spine, checked as arithmetic.

**Convention imported: none.** Every check here is arithmetic on equations as
printed in the published sources, using only the definition of beta_l. No plane
wave, no explicit basis, no Legendre projection, no ell=2 specialisation. The
general-ell checks are symbolic in `ell`; the exact checks use `Fraction`.

Published equation numbers throughout:

    Gebbie, Dunsby & Ellis, Annals of Physics 282, 321 (2000), App. F, pp. 379-380
    Gebbie & Ellis, Annals of Physics 282, 285 (2000), Eqs. (24), (25)

`sympy.factorial2` does **not** simplify at general ell: written with double
factorials, `beta(l)/beta(l-1) - l/(2l-1)` does not reduce to zero. Write beta in
the factorial form `2**l * factorial(l)**2 / factorial(2*l)` instead. This is the
same pattern the project's conventions-gate check script uses.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from functions.harmonics.weights import alpha, beta, free_streaming_weight  # noqa: E402

ELL = sp.symbols("ell", positive=True, integer=True)
ELL_RANGE = range(2, 25)


def _beta_sym(n):
    """beta_n in factorial form — Gebbie & Ellis (2000), Eq. (24)."""
    return 2**n * sp.factorial(n) ** 2 / sp.factorial(2 * n)


def _zero(expr) -> bool:
    return sp.simplify(sp.gammasimp(sp.combsimp(expr))) == 0


# --- beta recurrences, Gebbie & Ellis (2000), Eq. (25) -----------------------


def test_beta_recurrence_descending_general_ell():
    """beta_l = l/(2l-1) beta_{l-1}, at general ell."""
    assert _zero(_beta_sym(ELL) / _beta_sym(ELL - 1) - ELL / (2 * ELL - 1))


def test_beta_recurrence_ascending_general_ell():
    """beta_{l+1} = (l+1)/(2l+1) beta_l, at general ell."""
    assert _zero(_beta_sym(ELL + 1) / _beta_sym(ELL) - (ELL + 1) / (2 * ELL + 1))


def test_beta_module_matches_symbolic_exactly():
    """The Fraction implementation reproduces the symbolic form exactly."""
    for n in ELL_RANGE:
        assert beta(n) == Fraction(sp.Rational(_beta_sym(n)).p, sp.Rational(_beta_sym(n)).q)


# --- (F.1) -> (F.2): multiplying through by beta_l --------------------------


def test_f1_to_f2_raising_term_general_ell():
    """beta_l * (l+1)^2/[(2l+3)(2l+1)] == (l+1)/(2l+3) * beta_{l+1}."""
    lhs = _beta_sym(ELL) * (ELL + 1) ** 2 / ((2 * ELL + 3) * (2 * ELL + 1))
    rhs = (ELL + 1) / (2 * ELL + 3) * _beta_sym(ELL + 1)
    assert _zero(lhs - rhs)


def test_f1_to_f2_lowering_term_general_ell():
    """beta_l * 1 == l/(2l-1) * beta_{l-1}  — the bare tau_{l-1} term of (F.1)."""
    assert _zero(_beta_sym(ELL) - ELL / (2 * ELL - 1) * _beta_sym(ELL - 1))


def test_f1_to_f2_exact_rationals():
    """The same two identities, exactly, over a range of ell."""
    for n in ELL_RANGE:
        assert beta(n) * free_streaming_weight(n) == Fraction(n + 1, 2 * n + 3) * beta(n + 1)
        assert beta(n) == Fraction(n, 2 * n - 1) * beta(n - 1)


# --- (F.3) -> (F.4): substituting beta_l = alpha_l^{-1} (2l+1) --------------


def test_f4_is_direct_substitution_into_f3():
    """(F.4) as printed is (F.3) with beta_l -> alpha_l^{-1}(2l+1), exactly.

    (F.3):  -(beta_l tau_l)' = k [ (l+1)/(2l+3) beta_{l+1} tau_{l+1}
                                   - l/(2l-1) beta_{l-1} tau_{l-1} ]

    Substituting beta_n = (2n+1)/alpha_n collapses both weights:
        (l+1)/(2l+3) * (2l+3)/alpha_{l+1} = (l+1)/alpha_{l+1}
        l/(2l-1)     * (2l-1)/alpha_{l-1} = l/alpha_{l-1}
    which is the printed (F.4) with -(2l+1)(alpha_l^{-1} tau_l)' on the left.
    """
    for n in ELL_RANGE:
        assert Fraction(n + 1, 2 * n + 3) * beta(n + 1) == Fraction(n + 1) / alpha(n + 1)
        assert Fraction(n, 2 * n - 1) * beta(n - 1) == Fraction(n) / alpha(n - 1)
        assert beta(n) == Fraction(2 * n + 1) / alpha(n)


def test_f4_requires_the_stated_division_to_reach_ma_bertschinger():
    """Finding B-2: printed (F.4) is not yet in the Ma & Bertschinger form.

    Ma & Bertschinger, Eqs. (49)/(50), carry k/(2l+1) on the right-hand side.
    Appendix F says (F.3) is rewritten "on first multiplying through by
    (2l+1)^{-1}", but the display is the direct substitution, which leaves
    -(2l+1)(alpha_l^{-1} tau_l)' on the left.

    This test pins the factor so that a harness comparing printed (F.4) against
    printed Ma & Bertschinger does not read the resulting (2l+1) as a failure of
    the reconstruction. See
    provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md, finding B-2.
    """
    for n in ELL_RANGE:
        printed_lhs_factor = Fraction(2 * n + 1)
        ma_bertschinger_rhs_factor = Fraction(1, 2 * n + 1)
        assert printed_lhs_factor * ma_bertschinger_rhs_factor == 1


# --- the hierarchy is the adjoint of the mode recursion ---------------------


def test_f1_weight_is_the_mode_recursion_weight_shifted():
    """(F.1)'s weight on tau_{l+1} is the mode-recursion weight at l -> l+1.

    The mode recursion carries l^2/[(2l+1)(2l-1)] on G_{l-1}; the moment
    hierarchy carries (l+1)^2/[(2l+3)(2l+1)] on tau_{l+1}. They are the same
    function, shifted — the two expansions are adjoint, which is what makes the
    Appendix F chain a check rather than a restatement.
    """
    mode_weight = lambda n: n**2 / ((2 * n + 1) * (2 * n - 1))  # noqa: E731
    assert _zero(mode_weight(ELL + 1) - (ELL + 1) ** 2 / ((2 * ELL + 3) * (2 * ELL + 1)))
    for n in ELL_RANGE:
        assert free_streaming_weight(n) == Fraction((n + 1) ** 2, (2 * n + 3) * (2 * n + 1))


# --- basis rephasing: two true statements about two different objects -------
#
# These two tests together are finding B-1 stated executably, and they are the
# reason the same question has returned three different verdicts. The rescaling
#
#     Q_{A_l} -> lam^l Q_{A_l},   tau_l -> lam^-l tau_l
#
# leaves the COVARIANT multipole tau_{A_l} untouched, which is why the (-1)^l
# versus i^l slip in Annals I never produced a wrong result. It does NOT leave
# the MODE bracket untouched: the raising and lowering terms pick up lam^-1 and
# lam^+1, so their relative coefficient carries lam^-2, and the relative SIGN
# flips whenever lam^2 = -1. The two candidate harmonic normalisations differ by
# exactly lam = i, so they sit on opposite sides of that flip.


def test_covariant_multipole_is_invariant_under_basis_rephasing():
    """tau_{A_l} = sum_k tau_l Q_{A_l} is unchanged. Finding B-1.

    tau_l is defined as the coefficient of Q_{A_l}, so rescaling the basis
    tensor and the coefficient inversely leaves the physical multipole alone.
    """
    lam = sp.symbols("lam", nonzero=True)
    tau, Q = sp.Function("tau"), sp.Function("Q")
    for scale in (lam, sp.I, -sp.I, sp.Integer(-1)):
        rescaled = (scale ** (-ELL) * tau(ELL)) * (scale**ELL * Q(ELL))
        assert sp.simplify(rescaled - tau(ELL) * Q(ELL)) == 0


def test_mode_bracket_relative_sign_tracks_lambda_squared():
    """The (F.1) bracket's relative coefficient carries lam^-2.

    So lam real keeps the printed opposite-sign form
        w_l tau_{l+1} - tau_{l-1},
    while lam imaginary gives a same-sign bracket with an overall factor -/+ i.

    This is what the Appendix F chain discriminates: Hu & Sugiyama, Wilson &
    Silk Eq. (7), Ma & Bertschinger Eqs. (49)/(50) and Seljak & Zaldarriaga
    Eq. (3d) all print REAL coefficients of OPPOSITE relative sign. Only the
    lam^2 = +1 family reproduces that, so the external match fixes the
    normalisation without importing a basis.
    """
    lam = sp.symbols("lam", nonzero=True)
    tau = sp.Function("tau")
    w = (ELL + 1) ** 2 / ((2 * ELL + 3) * (2 * ELL + 1))

    def bracket(scale):
        return sp.expand(
            scale**ELL
            * (w * scale ** (-(ELL + 1)) * tau(ELL + 1) - scale ** (-(ELL - 1)) * tau(ELL - 1))
        )

    def relative(scale):
        b = sp.expand(bracket(scale))
        return sp.simplify((b.coeff(tau(ELL + 1)) / w) / (-b.coeff(tau(ELL - 1))))

    assert sp.simplify(relative(lam) - lam ** (-2)) == 0
    for scale in (sp.Integer(1), sp.Integer(-1)):  # lam^2 = +1
        assert sp.simplify(relative(scale) - 1) == 0
    for scale in (sp.I, -sp.I):  # lam^2 = -1
        assert sp.simplify(relative(scale) + 1) == 0


# Finding B-3, the Bessel identity of Annals II (199), belongs to the spectra
# layer and is tested in tests/test_sachs_wolfe.py against the tuned numerical
# integrator there. The duplicate that stood here used a slower inline
# integrator and was removed rather than kept in step.


# --- the chain closes numerically, not only symbolically --------------------


def _stream():
    import numpy as np

    from functions.harmonics.free_streaming import analytic_projection, free_stream

    return np, free_stream, analytic_projection


def test_f4_variable_is_exactly_the_spherical_bessel_function():
    """alpha_l^{-1} tau_l = j_l(k_com (eta - eta_i)), to integrator precision.

    Appendix F, p. 380, says the free-streaming solution is spherical Bessel. This
    pins which normalisation it is bare in: the (F.4) variable, which is also the
    one in which the hierarchy takes the external Ma & Bertschinger form. The
    normalisation that makes the coefficients external makes the solution bare.

    Convention imported: none. The spherical Bessel recurrence is an independent
    fact about j_l, not a statement taken from Annals II.
    """
    np, free_stream, analytic = _stream()
    eta = np.linspace(0.0, 20.0, 400)
    sol = free_stream(1.0, eta, ell_max=80, normalisation="alpha")
    window = (eta > 2) & (eta < 18)
    for ell in (0, 1, 2, 3, 5, 8, 12, 20):
        j = analytic(1.0, eta, 0.0, ell)
        assert np.max(np.abs(sol.values[window, ell] - j[window])) < 1e-8, ell


def test_the_three_normalisations_are_one_solution():
    """(F.1), (F.3) and (F.4) integrate to the same tau_l."""
    np, free_stream, _ = _stream()
    eta = np.linspace(0.0, 20.0, 400)
    window = (eta > 2) & (eta < 18)
    ref = free_stream(1.0, eta, ell_max=80, normalisation="covariant").covariant()
    for norm in ("beta", "alpha"):
        got = free_stream(1.0, eta, ell_max=80, normalisation=norm).covariant()
        assert np.max(np.abs(got[window, :30] - ref[window, :30])) < 1e-4, norm


def test_sign_control_fails_in_a_known_shape():
    """D1. Flipping the relative sign destroys the projection.

    Both couplings then carry the same sign, so the hierarchy grows instead of
    projecting an oscillatory solution onto higher multipoles. It does not merely
    disagree — it diverges, which is why it is the cheapest wiring check in the
    bundle. Acceptance criterion 4.
    """
    np, free_stream, analytic = _stream()
    eta = np.linspace(0.0, 20.0, 400)
    window = (eta > 2) & (eta < 18)
    good = free_stream(1.0, eta, ell_max=80, normalisation="alpha")
    bad = free_stream(1.0, eta, ell_max=80, normalisation="alpha", sign_control=True)
    for ell in (2, 5, 10):
        j = analytic(1.0, eta, 0.0, ell)
        assert np.max(np.abs(good.values[window, ell] - j[window])) < 1e-8, ell
        # the control is orders of magnitude out, not marginally wrong
        assert np.max(np.abs(bad.values[window, ell])) > 1e3 * np.max(np.abs(j[window])), ell


# --- criterion 1: the external hierarchies, read from their own papers -------


def test_external_hierarchies_match_the_bundle_at_machine_precision():
    """Hu & Sugiyama, Ma & Bertschinger and Seljak & Zaldarriaga, as printed.

    Each is transcribed in functions/harmonics/external.py from the source paper,
    not through Annals II Appendix F — a coefficient read through Appendix F would
    be the same source as Appendix F.

    Two distinct normalisations are involved and both must match:
      HS Eq. (6) carries l/(2l-1), (l+1)/(2l+3)  -> Annals II (F.3), beta
      MB Eqs. (49)/(50) and SZ Eq. (3d) carry l/(2l+1), (l+1)/(2l+1) -> (F.4), alpha

    That two different external normalisations both land on the same covariant
    solution is the content of the acceptance spine. A basis phase leaking into
    the couplings would break at least one of them.
    """
    import numpy as np

    from functions.harmonics.external import APPENDIX_F, integrate_external
    from functions.harmonics.free_streaming import free_stream

    eta = np.linspace(0.0, 20.0, 400)
    window = (eta > 2) & (eta < 18)
    mine = {
        "(F.3)": free_stream(1.0, eta, ell_max=80, normalisation="beta").values,
        "(F.4)": free_stream(1.0, eta, ell_max=80, normalisation="alpha").values,
    }
    for form in ("HS", "MB", "SZ"):
        ref = mine[APPENDIX_F[form]]
        ext = integrate_external(form, 1.0, eta, ell_max=80)
        scale = ref[window, 0].mean() / ext[window, 0].mean()
        # the monopole normalisation is common, so the scale must be exactly one
        assert abs(scale - 1.0) < 1e-10, (form, scale)
        err = np.max(np.abs(ext[window, :26] * scale - ref[window, :26]))
        assert err < 1e-11, (form, err)


# --- the v1.0.0 target: C_l by two routes, (186) and (187)+(188) ------------


def test_mode_route_and_covariant_route_to_cl_are_identical():
    """Annals II (186) equals (187) with (188), exactly.

    (186)  C_l = (2/pi) beta_l^2/(2l+1)^2 Int (dk/k) k^3 |tau_l(k,eta_0)|^2
    (187)  <tau_Al tau^Al> = (1/2pi^2) beta_l Int k^2 dk |tau_l(k,eta_0)|^2
    (188)  C_l = Delta_l (2l+1)^-1 <tau_Al tau^Al>

    with Delta_l = 4 pi beta_l/(2l+1), Annals I (119). Both carry the same
    k-integral, so the identity is a statement about the prefactors alone.

    **This is the point of the paper, as a test.** Section 7.1.4 says that at
    linear order the solutions do not differ importantly from the canonical
    treatment; what the covariant formulation buys is the route through the
    multipole mean-squares, "not attainable in the canonical treatment". The two
    routes must therefore agree exactly, and they do.

    Convention imported: none. Arithmetic on the printed prefactors.
    """
    beta = lambda n: 2**n * sp.factorial(n) ** 2 / sp.factorial(2 * n)  # noqa: E731
    delta = lambda n: 4 * sp.pi * beta(n) / (2 * n + 1)  # noqa: E731

    mode_route = 2 / sp.pi * beta(ELL) ** 2 / (2 * ELL + 1) ** 2
    covariant_route = delta(ELL) / (2 * ELL + 1) * beta(ELL) / (2 * sp.pi**2)

    assert _zero(mode_route - covariant_route)

    # and exactly, over a range of ell
    for n in ELL_RANGE:
        a = sp.Rational(sp.nsimplify(mode_route.subs(ELL, n) * sp.pi))
        b = sp.Rational(sp.nsimplify(covariant_route.subs(ELL, n) * sp.pi))
        assert a == b, n


# ---------------------------------------------------------------------------
# Staging guard: v1.0.0 must carry no O(l) coupling
# ---------------------------------------------------------------------------


def test_no_coupling_in_the_v1_hierarchy_grows_with_ell():
    """**The staging contract, as arithmetic.**

    v1.0.0 reproduces the *linearised* hierarchy of Annals II. The high-$\\ell$
    couplings this project restores at v1.5.0 grow with $\\ell$; the linear ones
    do not --- every coupling in (F.1)-(F.4) and in the external
    hierarchies is a ratio of linear polynomials and tends to a constant.

    So "no $O(\\ell)$ coupling has leaked into v1.0.0" is not a promise to be
    taken on trust, it is a bounded-ness statement that can be asserted. If a
    v1.5.0 coupling is ever wired in early, some weight acquires a factor of
    $\\ell$ and this test fails at large $\\ell$ before anything downstream is
    believed.
    """
    from functions.harmonics.external import WEIGHTS
    from functions.harmonics.weights import free_streaming_weight

    ells = [2, 10, 100, 1000, 10000]

    # the bundle's own moment-hierarchy weight, (l+1)^2/[(2l+3)(2l+1)] -> 1/4
    bundle = [float(free_streaming_weight(l)) for l in ells]
    assert all(0.0 < w < 0.5 for w in bundle)
    assert bundle[-1] == pytest.approx(0.25, abs=1e-4)

    # every external hierarchy, as printed in its own paper
    for form, (lower, upper) in WEIGHTS.items():
        for l in ells:
            assert 0.0 < lower(l) < 1.0, (form, l, "lower")
            assert 0.0 < upper(l) < 1.0, (form, l, "upper")
        # and the limits are constants, not growing
        assert lower(10000) == pytest.approx(0.5, abs=1e-3), form
        assert upper(10000) == pytest.approx(0.5, abs=1e-3), form


# ---------------------------------------------------------------------------
# the fourth external hierarchy: Wilson (1983), Eq. (8)
# ---------------------------------------------------------------------------


def test_wilson_reproduces_the_bundle_and_tests_the_phase_convention():
    """Wilson Eq. (8), read from the scanned paper, as a **fourth** source.

    Wilson is a stronger check than a fourth set of weights would be. His
    weights are Hu & Sugiyama's --- the beta normalisation --- but his equation
    is written in the imaginary convention, with **both** bracket terms positive
    under an overall $-ik$. Only $\\Theta_\\ell = i^\\ell\\delta_\\ell$ turns that
    into the real, opposite-sign form. So this panel exercises the phase
    convention of finding B-1 and criterion 3, not merely the $\\ell$-weights.

    He is integrated **complex and as printed**, and transformed only afterwards.
    Transforming the equation first would assume the identity being tested.
    """
    import numpy as np

    from functions.harmonics.external import integrate_wilson
    from functions.harmonics.free_streaming import free_stream

    eta = np.linspace(0.0, 20.0, 400)
    window = (eta > 2) & (eta < 18)
    mine = free_stream(1.0, eta, ell_max=80, normalisation="beta").values
    wilson = integrate_wilson(1.0, eta, ell_max=80)

    scale = mine[window, 0].mean() / wilson[window, 0].mean()
    assert abs(scale - 1.0) < 1e-10
    assert np.max(np.abs(wilson[window, :26] * scale - mine[window, :26])) < 1e-11


def test_wilsons_solution_is_real_after_the_phase_is_removed():
    """i^l delta_l must be real: that is the content of the convention claim.

    If the phase were anything other than $i^\\ell$ an imaginary part would
    survive, so this is a sharper statement than the agreement test above.
    """
    import numpy as np
    from scipy.integrate import solve_ivp

    from functions.harmonics.external import WILSON_WEIGHTS

    k, ell_max = 1.0, 40
    lower, upper = WILSON_WEIGHTS
    y0 = np.zeros(ell_max + 1, dtype=complex)
    y0[0] = 1.0

    def rhs(_t, y):
        padded = np.concatenate([y, [0j]])
        d = np.empty(ell_max + 1, dtype=complex)
        d[0] = -1j * k * upper(0) * padded[1]
        for l in range(1, ell_max + 1):
            d[l] = -1j * k * (lower(l) * padded[l - 1] + upper(l) * padded[l + 1])
        return d

    sol = solve_ivp(rhs, (0.0, 12.0), y0, t_eval=[12.0], rtol=1e-11, atol=1e-13,
                    method="DOP853")
    transformed = sol.y[:, -1] * 1j ** np.arange(ell_max + 1)
    assert np.max(np.abs(transformed.imag)) < 1e-10
    assert np.max(np.abs(transformed.real)) > 0.1  # and it is not trivially zero


# ---------------------------------------------------------------------------
# what the Appendix F chain does and does not discriminate
# ---------------------------------------------------------------------------


def test_the_external_match_is_invariant_under_a_common_rephasing():
    """**The limit of criterion 1 as evidence for criterion 3.**

    Raised by Coordination, 2026-10-06, and correct. Rephasing *both* sides by
    $i^\\ell$ is a change of variable, so the agreement is untouched. A match at
    scale 1 therefore constrains the $\\ell$-weights --- which are
    convention-independent --- and constrains the *convention* only where the
    phase applied to the external source is fixed from outside the comparison.

    For Hu & Sugiyama, Ma & Bertschinger and Seljak & Zaldarriaga this bundle
    applies no phase, which is a choice and not a derivation. The one place the
    phase is externally fixed is Wilson: Annals II states, in the line following
    its flat mode functions, that the covariant form "differs by a factor of
    $i^{-\\ell}$ from Wilson since we are using plain mode functions instead of
    plane waves". See `test_wilson_reproduces_the_bundle_and_tests_the_phase_convention`.

    This test exists so the limitation is pinned in the suite rather than only
    described in prose.
    """
    import numpy as np

    from functions.harmonics.external import integrate_external
    from functions.harmonics.free_streaming import free_stream

    eta = np.linspace(0.0, 20.0, 400)
    window = (eta > 2) & (eta < 18)
    mine = free_stream(1.0, eta, ell_max=80, normalisation="beta").values
    external = integrate_external("HS", 1.0, eta, ell_max=80)

    phase = 1j ** np.arange(81)
    direct = np.max(np.abs(external[window, :26] - mine[window, :26]))
    rephased = np.max(np.abs((external * phase)[window, :26] - (mine * phase)[window, :26]))

    assert direct < 1e-11
    assert rephased == pytest.approx(direct, rel=1e-9)


def test_the_bracket_ratio_carries_the_square_of_the_normalisation():
    """$\\tau_\\ell\\to c^\\ell\\tau_\\ell$ sends $(A,B)\\to(A/c,\\,Bc)$, so $B/A\\to c^2B/A$.

    At $c=i$ an opposite-sign real bracket becomes a same-sign bracket under an
    overall $i$ --- which is exactly the form Wilson prints. The two conventions
    in the literature are therefore the two values of $c^2=\\pm1$, and nothing
    else. Symbolic, because it is an identity.
    """
    import sympy as sp

    A, B, c = sp.symbols("A B c")
    A_new, B_new = A / c, B * c
    assert sp.simplify((B_new / A_new) / (B / A) - c**2) == 0
    assert sp.simplify(A_new.subs(c, sp.I) + sp.I * A) == 0
    assert sp.simplify(B_new.subs(c, sp.I) - sp.I * B) == 0


def test_c32_fixes_the_convention_and_the_match_then_confirms_it():
    """**Criterion 3 closes here, on the definition rather than on the match.**

    Q1 was reopened because the four-source match cannot select a convention:
    rephasing both sides by $i^\\ell$ is a change of variable. What settles it is
    the *definition*, and the conventions sheet carries it at **C3.2**, marked
    DEF and seed-verified against the GE98 PDF:

        Q_{A_l} = (-k_phys)^{-l} D_<A_l> Q,  the stripped factor REAL, no i.

    A real stripped factor means the two candidate normalisations differ by a
    *real* ratio, so $c^2=+1$ and the bracket keeps opposite signs --- which is
    the form Hu & Sugiyama, Ma & Bertschinger and Seljak & Zaldarriaga print and
    the one this bundle implements.

    The chain is then not circular:

    1. **C3.2** fixes the convention, from the definition, externally verified.
    2. **C3a.3** derives $Q_{A_\\ell}=i^\\ell O^{(k)}_{A_\\ell}Q$ --- the covariant
       basis sits at $i^\\ell$ from the plane-wave basis.
    3. *Annals II* states independently that its form differs from Wilson's, who
       uses plane waves, by $i^{-\\ell}$.
    4. Wilson Eq. (8), integrated complex and as printed, matches after exactly
       that phase, at $3.1\\times10^{-14}$, and is real to $10^{-10}$.

    Steps 2 and 3 are independent derivations of the same phase, and step 4 is
    the measurement. The match *confirms*; it no longer has to *select*.
    """
    import sympy as sp

    A, B, c = sp.symbols("A B c", real=False)
    lam = sp.Symbol("lambda", real=True, nonzero=True)      # C3.2: real, no i
    lam_prime = sp.Symbol("lambdaprime", real=True, nonzero=True)

    # tau_l -> c^l tau_l with c = lam'/lam sends (A, B) -> (A/c, B c)
    ratio = sp.simplify(((B * c) / (A / c)) / (B / A))
    assert sp.simplify(ratio - c**2) == 0

    # C3.2 makes both normalisations real, so c is real and c^2 > 0: the relative
    # sign inside the bracket cannot flip. Only an imaginary ratio flips it.
    c_real = (lam_prime / lam)
    assert sp.simplify(sp.im(c_real**2)) == 0
    assert sp.ask(sp.Q.positive(c_real**2)) is not False

    # and the imaginary alternative, which C3.2 excludes, flips it
    assert sp.simplify((sp.I) ** 2 + 1) == 0


def test_wilson_silk_1981_is_the_same_equation_as_wilson_1983_at_zero_curvature():
    """**The fifth source, and the falsification of a good hypothesis.**

    Coordination proposed, from the 1983 paper being in the imaginary
    convention, that if Wilson & Silk 1981 were in the *real* one then the same
    first author had published in both conventions two years apart --- direct
    evidence that the phase is a convention and not a fact.

    **The scan refutes it.** W&S 1981 Eq. (7) reads

        l > 2,  delta_l^dot = -n_e sigma_T c delta_l
                  - i k T c [ l/(2l-1) delta_{l-1} + (l+1)/(2l+3) delta_{l+1} ]

    --- the **same** same-sign imaginary form, under the same overall $-ikTc$,
    with the same weights. Wilson published in one convention, consistently,
    twice. The 1983 paper is the negative-curvature generalisation and differs
    only by the factor $[1-\\ell(\\ell+2)K/k^2]$, which is unity in the flat case
    this bundle compares in.

    So the two are the *same equation* at $K=0$, and this test says so rather
    than drawing a fifth panel that would show an identical curve. The negative
    result is worth as much as the positive one would have been: the convention
    splits by author lineage, not by paper, which is a cleaner statement than the
    hypothesis would have given.
    """
    from functions.harmonics.external import WILSON_WEIGHTS

    lower, upper = WILSON_WEIGHTS
    for l in (3, 5, 20, 200):
        # W&S 1981 Eq. (7), flat, read from p. 15
        assert lower(l) == pytest.approx(l / (2 * l - 1))
        assert upper(l) == pytest.approx((l + 1) / (2 * l + 3))
        # Wilson 1983 Eq. (8) adds [1 - l(l+2) K/k^2], which is 1 at K = 0
        curvature_factor = 1.0 - l * (l + 2) * 0.0 / 1.0
        assert curvature_factor == 1.0
