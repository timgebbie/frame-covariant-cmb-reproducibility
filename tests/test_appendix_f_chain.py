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
    """Finding G2: printed (F.4) is not yet in the Ma & Bertschinger form.

    Ma & Bertschinger, Eqs. (49)/(50), carry k/(2l+1) on the right-hand side.
    Appendix F says (F.3) is rewritten "on first multiplying through by
    (2l+1)^{-1}", but the display is the direct substitution, which leaves
    -(2l+1)(alpha_l^{-1} tau_l)' on the left.

    This test pins the factor so that a harness comparing printed (F.4) against
    printed Ma & Bertschinger does not read the resulting (2l+1) as a failure of
    the reconstruction. See
    provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md, finding G2.
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
# These two tests together are finding G1 stated executably, and they are the
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
    """tau_{A_l} = sum_k tau_l Q_{A_l} is unchanged. Finding G1.

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


# --- finding G3: Annals II (199), the Bessel identity of §8.3 ---------------


def test_annals_ii_199_needs_the_square_in_its_denominator():
    """(199) as printed is exact only where Gamma(m/2+1) = 1, i.e. m = 0 and 2.

    Convention imported: none — this is arithmetic on the printed identity
    against the integral it claims to equal. See
    provenance/ANNALS-II-ANTECEDENT-AND-CORRECTIONS-v1.md, finding G3.
    """
    from scipy.integrate import quad
    from scipy.special import gamma, spherical_jn

    def numeric(m: int, ell: int) -> float:
        f = lambda z: spherical_jn(ell, z) ** 2 / z**m  # noqa: E731
        total, a = 0.0, 1e-8
        for b in (1, 10, 50, 200, 1000, 5000, 20000):
            value, _ = quad(f, a, b, limit=400)
            total += value
            a = b
        return total + 1 / (2 * (1 + m) * a ** (1 + m))

    def closed(m, ell, square):
        d = gamma(m / 2 + 1) ** (2 if square else 1)
        return (
            (float(sp.pi) / 2 ** (m + 2))
            * gamma(m + 1)
            * gamma(ell - m / 2 + 0.5)
            / (d * gamma(ell + m / 2 + 1.5))
        )

    for m in (0, 1, 2, 3):
        for ell in (2, 10):
            n = numeric(m, ell)
            assert abs(float(closed(m, ell, square=True)) / n - 1) < 2e-5, (m, ell)
            # the printed form is the corrected one multiplied by Gamma(m/2+1),
            # so it is exact exactly where that gamma is 1 — at m = 0 and m = 2
            printed_ratio = float(closed(m, ell, square=False)) / n
            assert abs(printed_ratio - float(gamma(m / 2 + 1))) < 2e-5, (m, ell)

    # the two cases Annals II actually uses
    assert abs(float(gamma(2)) - 1.0) < 1e-12  # m = 2, used by (201): unaffected
    assert abs(float(gamma(1.5)) - 0.8862269) < 1e-6  # m = 1, used by (204): 11.4% low


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
