r"""The integral solution's source coefficients $C_0,C_1,C_2$ --- Annals II \S4.

    (89)  C_0 d(l,0) + C_1 beta_1^-1 k d(l,1)
            + C_2 k^2 5 beta_2^-1 ( 2/15 d(l,2) + 1/3 d(l,0) )
          = -[ (a B_1 + kappa' v_B) d(l,1) + a B_2 d(l,2) ]
    (90)  -C_0 ~= +5/2 a B_2,  -C_1 ~= (1/k)(a B_1 + kappa' v_B),
          -C_2 ~= (1/k^2) a B_2

**(89) is the definition and (90) is a result, so this module implements (89).**
The coefficients are obtained by solving the rank-by-rank match in exact
rationals and (90) is then a *check* on this bundle rather than a source for it
--- the discipline `functions/background/flrw.py` applies to the expansion law,
applied here. It is not pedantry: solved that way, **(90)'s $C_0$ comes out with
the opposite sign to the printed one**, which is finding **B-11**.

**These are CGI with respect to a generic $u^a$**, in the paper's own words
below (90). That is the whole point of this module. The $\mathcal B_A$ are the
rank-decomposed source,

    B_0 = -(1/3) D^a tau_a,    B_1 = D_a ln T + A_a,    B_2 = sigma_ab,

so a **frame choice sets the coefficients** rather than the equations
presupposing one. Annals II specialises before it writes its sources --- \S7.1.1,
*"We therefore choose the Newtonian frame in which the shear contribution does
not appear"* --- and every equation this bundle implemented before this module
descends from that specialisation. The Newtonian frame is
$\tilde\sigma_{ab}\approx0$, hence $\tilde C_0\approx\tilde C_2\approx0$ and
$\tilde C_1$ alone survives, which is (110). The energy frame is $q_a=0$ and
keeps all three.

**Why the sign of $C_0$ was unreachable until now.** $C_0\propto\mathcal B_2$,
and $\mathcal B_2$ is identically zero in the only frame anyone computed in. A
specialised solution cannot see its own errors in the sector it discards; that
is the argument for carrying $u^a$ generic, stated as a measurement rather than
as a preference.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

import numpy as np

from functions.harmonics.weights import beta

__all__ = [
    "SourceCoefficients",
    "match_coefficients",
    "newtonian_coefficients",
    "c0_printed",
    "c0_from_the_match",
]


@lru_cache(maxsize=1)
def _solved_match() -> tuple[Fraction, Fraction, Fraction]:
    r"""(89) solved rank by rank, in $\mathbb Q$.

    Returns the three rational prefactors $(p_0,p_1,p_2)$ defined by

        C_0 = p_0 (a B_2),   C_1 = p_1 (1/k)(a B_1 + kappa' v_B),
        C_2 = p_2 (1/k^2)(a B_2).

    Exact, never floating point: a sign on a harmonic weight is settled exactly
    or it is not settled.
    """
    b1, b2 = beta(1), beta(2)

    # The free-streaming solution's value and derivatives at zero argument are
    # j_l^(n)(0), and **j_0''(0) = -1/3 is NEGATIVE**: from the ascending series
    # j_0(x) = 1 - x^2/6 + ... Finding **B-11**. (89) prints this entry as
    # +1/3 and with that sign the match contradicts (90)'s C_0 by exactly -1.
    # Flipped, all three of (90)'s relations come out exactly.
    j0_second = Fraction(-1, 3)
    j1_first = Fraction(1, 3)
    j2_second = Fraction(2, 15)

    # ell = 2:  C_2 k^2 * (5/b2) * j_2''(0) = -(a B_2)
    p2 = Fraction(-1) / (Fraction(5) / b2 * j2_second)
    # ell = 1:  C_1 * (1/b1) * k = -(a B_1 + kappa' v_B);  (1/b1) = 3 j_1'(0)
    p1 = Fraction(-1) * b1
    # ell = 0:  C_0 + C_2 k^2 * (5/b2) * j_0''(0) = 0
    p0 = -(Fraction(5) / b2 * j0_second) * p2

    return p0, p1, p2


#: $C_0$ as it follows from (89) **with the sign (89) prints** on its
#: $\delta_{\ell0}$ entry. Kept as a known-wrong alternative that must change
#: the answer (decision **S12**), and the subject of finding **B-11**.
c0_from_printed_89: Fraction = Fraction(5, 2)

#: $C_0$ from the match with $j_0''(0)=-\tfrac13$, which is what (90) prints:
#: $-C_0\simeq+\tfrac52a\mathcal B_2$. The two differ by exactly $-1$.
c0_from_the_match: Fraction = _solved_match()[0]

#: Backwards-compatible alias; `c0_from_printed_89` is the accurate name.
c0_printed: Fraction = c0_from_printed_89


@dataclass(frozen=True)
class SourceCoefficients:
    r"""$C_0,C_1,C_2$ on a conformal-time grid, for one comoving wavenumber.

    `frame` is a label only in the sense that it records which $\mathcal B_2$
    was supplied --- unlike `PerturbationHistory.frame` before this module,
    nothing here reads the string. The frame enters through the numbers.
    """

    eta: np.ndarray
    k_com: float
    c0: np.ndarray
    c1: np.ndarray
    c2: np.ndarray
    frame: str

    @property
    def shear_sector_is_empty(self) -> bool:
        r"""Whether $C_0$ and $C_2$ vanish --- i.e. whether $\mathcal B_2$ did.

        True in the Newtonian frame and false in any other, which is the one
        statement this object exists to make computable.
        """
        return bool(np.all(self.c0 == 0.0) and np.all(self.c2 == 0.0))


def match_coefficients(
    eta: np.ndarray,
    k_com: float,
    *,
    a_b1: np.ndarray,
    a_b2: np.ndarray,
    kappa_prime_v_b: np.ndarray,
    frame: str,
    use_printed_c0: bool = False,
) -> SourceCoefficients:
    r"""Solve (89) for $C_0,C_1,C_2$ at one $k$.

    `a_b1` is $a\mathcal B_1$, `a_b2` is $a\mathcal B_2$ and `kappa_prime_v_b`
    is $\kappa'v_B$ --- all gradient-level mode coefficients, as (89) carries
    them. The $1/k$ that converts $a\mathcal B_1$ to $(\delta\tilde T+\Phi_A)$
    is the same $1/k$ that converts $\kappa'v_B$ to $\kappa'\tilde v_B$, which
    is why both sit inside $C_1$ and neither is applied here twice.

    `use_printed_c0=True` substitutes the $C_0$ that follows from (89)
    **with the sign (89) prints** on its $\delta_{\ell0}$ entry. It must change
    the answer wherever $\mathcal B_2\ne0$ and must change nothing in the
    Newtonian frame; `tests/` asserts both. See **B-11** --- and note that it is
    (89) that is wrong there, not (90).
    """
    p0, p1, p2 = _solved_match()
    k = float(k_com)
    if k <= 0.0:
        raise ValueError("k_com must be positive")

    a_b1 = np.asarray(a_b1, dtype=float)
    a_b2 = np.asarray(a_b2, dtype=float)
    kpvb = np.asarray(kappa_prime_v_b, dtype=float)
    if not (a_b1.shape == a_b2.shape == kpvb.shape == np.shape(eta)):
        raise ValueError("every source array must share the eta grid's shape")

    prefactor = float(p0) if not use_printed_c0 else float(c0_from_printed_89)
    return SourceCoefficients(
        eta=np.asarray(eta, dtype=float),
        k_com=k,
        c0=prefactor * a_b2,
        c1=float(p1) / k * (a_b1 + kpvb),
        c2=float(p2) / k**2 * a_b2,
        frame=frame,
    )


def newtonian_coefficients(
    eta: np.ndarray,
    k_com: float,
    *,
    delta_t: np.ndarray,
    phi_a: np.ndarray,
    kappa_prime: np.ndarray,
    v_b: np.ndarray,
) -> SourceCoefficients:
    r"""The Newtonian specialisation, $\tilde\sigma_{ab}\approx0$.

    $\tilde{\mathcal B}_1=\tilde{\mathcal D}_a\ln T+\tilde A_a$ with
    $\tilde A_a=\mathcal D_a\Phi_A$, so in mode form
    $a\tilde{\mathcal B}_1=k(\delta\tilde T+\Phi_A)$ --- the $k/a$ of a gradient
    against the $a$ of $a\mathcal B_1$. Then

        -C~_1 = (1/k)( k (dT~ + Phi_A) + kappa' v_B ) = (dT~ + Phi_A) + kappa' v~_B

    which is (109) `calc-ng` exactly, and $\tilde v_B=v_B/k$ falls out rather
    than being imposed. $\tilde{\mathcal B}_2=0$ gives
    $\tilde C_0=\tilde C_2=0$, which is (110).

    **This function must reproduce what the bundle computed before it existed.**
    That is the acceptance condition for the covariant form, in the sense of
    decision S2's *restricted case which must recover v1.0.0's numbers*.
    """
    delta_t = np.asarray(delta_t, dtype=float)
    phi_a = np.asarray(phi_a, dtype=float)
    return match_coefficients(
        eta, k_com,
        a_b1=float(k_com) * (delta_t + phi_a),
        a_b2=np.zeros_like(delta_t),
        kappa_prime_v_b=float(k_com) * np.asarray(kappa_prime, dtype=float)
        * np.asarray(v_b, dtype=float),
        frame="newtonian",
    )


def newtonian_c1_prime(
    eta: np.ndarray,
    k_com: float,
    *,
    delta_t: np.ndarray,
    phi_a: np.ndarray,
    phi_a_prime: np.ndarray,
    phi_h_prime: np.ndarray,
    tau_1: np.ndarray,
    conformal_hubble: np.ndarray,
    kappa_prime_v_b_prime: np.ndarray,
) -> np.ndarray:
    r"""$\tilde C_1'$ from (106), **not** from differentiating $\tilde C_1$.

    *Annals II* derives

        (a B~_1)' ~= -a^2 H B~_1 + k(Phi_A' - Phi_H') - 2 H a k Phi_A
                     + (1/3) k^2 tau~_1

    and then $-\tilde C_1'=(\kappa'\tilde v_B)'+\tfrac1k(a\tilde{\mathcal B}_1)'$
    from (107). It derives (106) rather than differentiating (105) for a
    reason, and that reason is finding **T-23**: the footnote to (105) expands

        D_<a Bdot_b> ~= -(a/k)( Bdot_1 + 2 H B_1 ) D_<a D_b> Q

    so **mode-expanding a derivative is not differentiating a mode amplitude**.
    The $2H\mathcal B_1$ comes from the $1/a$ inside the decomposition and is
    invisible to a spline through the stored amplitude. Measured against (106),
    a plain derivative of $a\tilde{\mathcal B}_1$ is wrong by a **median of
    100%**, the difference being 60% of the whole.

    This is conventions row **C3.1a** --- *"a reduction that forgets either side
    puts a spurious $a$-dependence into every rank"* --- met in the integral
    solution rather than in the hierarchy.

    `conformal_hubble` is $a'/a$, so $a^2H$ against the stored
    $a\tilde{\mathcal B}_1=k(\delta\tilde T+\Phi_A)$ is that times it.
    """
    k = float(k_com)
    a_b1 = k * (np.asarray(delta_t, dtype=float) + np.asarray(phi_a, dtype=float))
    aH = np.asarray(conformal_hubble, dtype=float)
    a_b1_prime = (
        -aH * a_b1
        + k * (np.asarray(phi_a_prime, dtype=float)
               - np.asarray(phi_h_prime, dtype=float))
        - 2.0 * aH * k * np.asarray(phi_a, dtype=float)
        + (k**2 / 3.0) * np.asarray(tau_1, dtype=float)
    )
    # (107): -C~_1' = (kappa' v~_B)' + (1/k)(a B~_1)'
    return -(np.asarray(kappa_prime_v_b_prime, dtype=float) + a_b1_prime / k)


__all__.append("newtonian_c1_prime")


# ---------------------------------------------------------------------------
# The generic source derivatives (102) needs. See
# `provenance/GENERIC-SOURCE-DERIVATIVES-v1.md` for the derivation and the two
# controls. **Computed from the published relations, never splined** --- T-23.
# ---------------------------------------------------------------------------


def generic_shear_derivatives(
    *,
    sigma: np.ndarray,
    electric_weyl: np.ndarray,
    conformal_hubble: np.ndarray,
    scale_factor: np.ndarray,
    rho: np.ndarray,
    pressure: np.ndarray | float = 0.0,
    acceleration_pstf: np.ndarray | float = 0.0,
    acceleration_pstf_dot: np.ndarray | float = 0.0,
    anisotropic_stress: np.ndarray | float = 0.0,
    anisotropic_stress_dot: np.ndarray | float = 0.0,
    curl_magnetic_weyl: np.ndarray | float = 0.0,
    flux_pstf: np.ndarray | float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    r"""$\dot\sigma$ and $\ddot\sigma$ for a **generic** $u^a$ --- Appendix G.

    The shear propagation equation, with no frame, matter model or scalar
    restriction:

        sigma-dot<ab> + 2H sigma<ab> - D<a A b> + E<ab> ~= 1/2 pi<ab>

    and its derivative with $\dot E_{ab}$ from Appendix G's Bianchi propagation
    equation substituted and $E_{ab}$ eliminated through the first:

        sigma-ddot = -5H sigma-dot + [1/2(rho+p) - 2 H-dot - 6H^2] sigma
                     + 3H Lambda + Lambda-dot + 2H pi + pi-dot
                     - curl H + 1/2 D<a q b>

    with $\Lambda\equiv\mathcal D_{\langle a}A_{b\rangle}$.

    **The control passes exactly.** Reduced to the paper's scalar
    matter-dominated case --- $A_a\approx0$, $\pi_{ab}=q_a=\mathrm{curl}H=0$,
    $p=0$ --- this reproduces the printed

        (a^2 sigma)^.. + H (a^2 sigma)^. ~= + 1/2 a^2 rho_M sigma

    term for term, with the difference identically zero before the Friedmann
    relation is used. `tests/` asserts it.

    All arguments are **proper-time** quantities on a shared $\eta$ grid;
    `conformal_hubble` is $a'/a$, so $H=a'/a^2$ is formed here rather than
    passed, which keeps one definition of $H$ in the module.
    """
    a = np.asarray(scale_factor, dtype=float)
    H = np.asarray(conformal_hubble, dtype=float) / a
    sig = np.asarray(sigma, dtype=float)
    E = np.asarray(electric_weyl, dtype=float)
    pi_ab = np.asarray(anisotropic_stress, dtype=float) * np.ones_like(sig)
    lam = np.asarray(acceleration_pstf, dtype=float) * np.ones_like(sig)

    sigma_dot = -2.0 * H * sig + lam - E + 0.5 * pi_ab

    # H-dot from the background Friedmann equation, Appendix G:
    #     H-dot = -H^2 - (rho + 3p)/6
    p_ = np.asarray(pressure, dtype=float) * np.ones_like(sig)
    rho_ = np.asarray(rho, dtype=float)
    H_dot = -(H**2) - (rho_ + 3.0 * p_) / 6.0

    sigma_ddot = (
        -5.0 * H * sigma_dot
        + (0.5 * (rho_ + p_) - 2.0 * H_dot - 6.0 * H**2) * sig
        + 3.0 * H * lam
        + np.asarray(acceleration_pstf_dot, dtype=float) * np.ones_like(sig)
        + 2.0 * H * pi_ab
        + np.asarray(anisotropic_stress_dot, dtype=float) * np.ones_like(sig)
        - np.asarray(curl_magnetic_weyl, dtype=float) * np.ones_like(sig)
        + 0.5 * np.asarray(flux_pstf, dtype=float) * np.ones_like(sig)
    )
    return sigma_dot, sigma_ddot


def c2_derivatives(
    k_com: float,
    *,
    sigma: np.ndarray,
    sigma_dot: np.ndarray,
    sigma_ddot: np.ndarray,
    conformal_hubble: np.ndarray,
    scale_factor: np.ndarray,
    rho: np.ndarray,
    pressure: np.ndarray | float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r"""$C_2$, $C_2'$ and $C_2''$ from $\mathcal B_2=\sigma$ --- (90).

    $-C_2\simeq\tfrac1{k^2}a\mathcal B_2$ with $k$ **comoving and constant**, so
    it passes through the conformal derivative untouched and the whole content
    is $(a\sigma)'$ and $(a\sigma)''$. With $\mathcal H\equiv a'/a$ and
    $\sigma'=a\dot\sigma$:

        (a sigma)'  = a^2 (H sigma + sigma-dot)
        (a sigma)'' = a'' sigma + 2 a' sigma' + a sigma''

    The $a$ is the rank's, not a convenience --- the scale-factor rule in
    `provenance/GENERIC-SOURCE-DERIVATIVES-v1.md`.

    **Nothing is splined and nothing is differentiated numerically** (T-23).
    $\dot\sigma$ and $\ddot\sigma$ come from `generic_shear_derivatives`, and
    $a''$ comes from the **same** Friedmann relation that function uses:

        H-dot = -H^2 - (rho + 3p)/6   =>   script-H' = -a^2 (rho + 3p)/6
        a'' = a (script-H' + script-H^2)

    so the background cannot disagree between the two. An earlier draft of this
    function reached for `np.gradient` here and multiplied it by zero --- the
    `kappa_prime * 0.0` idiom of finding **T-21**, written by the same hand that
    recorded T-21, for the third time in one session. It is gone; the exact
    relation is three lines and has no grid dependence at all.
    """
    a = np.asarray(scale_factor, dtype=float)
    cH = np.asarray(conformal_hubble, dtype=float)           # script-H = a'/a
    H = cH / a                                               # proper H
    sig = np.asarray(sigma, dtype=float)
    sd = np.asarray(sigma_dot, dtype=float)
    sdd = np.asarray(sigma_ddot, dtype=float)
    rho_ = np.asarray(rho, dtype=float)
    p_ = np.asarray(pressure, dtype=float) * np.ones_like(a)

    a_prime = cH * a
    cH_prime = -(a**2) * (rho_ + 3.0 * p_) / 6.0             # exact, Appendix G
    a_second = a * (cH_prime + cH**2)

    sigma_prime = a * sd
    sigma_second = a_prime * sd + a**2 * sdd

    a_sigma = a * sig
    a_sigma_prime = a_prime * sig + a * sigma_prime
    a_sigma_second = a_second * sig + 2.0 * a_prime * sigma_prime + a * sigma_second

    pref = -1.0 / float(k_com) ** 2
    return pref * a_sigma, pref * a_sigma_prime, pref * a_sigma_second


__all__ += ["generic_shear_derivatives", "c2_derivatives"]


@dataclass(frozen=True)
class CoefficientSet:
    r"""Everything (102) consumes, assembled for one frame at one $k$.

    The point of the dataclass is that `integral_solution` takes its
    derivatives as **inputs** (finding T-23), and a caller assembling them by
    hand is a caller who can get one wrong silently. This is the assembly, done
    once, from the published relations.
    """

    coefficients: SourceCoefficients
    c1_prime: np.ndarray
    c2_second: np.ndarray
    c2_prime_star: float


def tau_1_prime(
    k_com: float,
    *,
    tau_1: np.ndarray,
    delta_t: np.ndarray,
    phi_a: np.ndarray,
    r_baryon: np.ndarray,
    r_baryon_prime: np.ndarray,
) -> np.ndarray:
    r"""$\tilde\tau_1'$ from **(152)**, not from a spline.

        (152)  tau~_1-dot = -(R-dot/(1+R)) tau~_1 - (1/(1+R))(k/a) dT~ - (k/a) Phi_A

    in conformal time, where every $k/a$ against a proper-time dot becomes a
    bare $k_{\rm com}$ against a conformal prime. The mode dipole's evolution is
    *printed*; differentiating the integrated $\tau_1$ instead would be T-23's
    error in a second place, and here it is avoidable in one line.
    """
    k = float(k_com)
    r = np.asarray(r_baryon, dtype=float)
    return (
        -np.asarray(r_baryon_prime, dtype=float) / (1.0 + r) * np.asarray(tau_1, dtype=float)
        - k / (1.0 + r) * np.asarray(delta_t, dtype=float)
        - k * np.asarray(phi_a, dtype=float)
    )


def newtonian_set(
    eta: np.ndarray,
    k_com: float,
    *,
    delta_t: np.ndarray,
    phi_a: np.ndarray,
    phi_a_prime: np.ndarray,
    phi_h_prime: np.ndarray,
    tau_1: np.ndarray,
    kappa_prime: np.ndarray,
    kappa_double_prime: np.ndarray,
    conformal_hubble: np.ndarray,
    r_baryon: np.ndarray,
    r_baryon_prime: np.ndarray,
) -> CoefficientSet:
    r"""(102)'s full input set in the Newtonian frame, $\tilde\sigma_{ab}=0$.

    $\tilde{\mathcal B}_2=0$ makes $C_0$, $C_2$, $C_2'$ and $C_2''$ **identically
    zero**, so (102) collapses to (110) and the solution must be the one
    `pipeline.run` has always computed. That is the acceptance condition for the
    covariant assembly --- decision **S2**'s *restricted case which must recover
    v1.0.0's numbers*.

    $\tilde v_B=\tilde\tau_1$ by tight coupling (156 at zeroth order in the
    scattering time), so $(\kappa'\tilde v_B)'=\kappa'\tilde\tau_1'
    +\kappa''\tilde\tau_1$ **as (178) prints it**, with $\tilde\tau_1'$ from
    (152) rather than from a spline.
    """
    tau1 = np.asarray(tau_1, dtype=float)
    kp = np.asarray(kappa_prime, dtype=float)
    t1p = tau_1_prime(k_com, tau_1=tau1, delta_t=delta_t, phi_a=phi_a,
                      r_baryon=r_baryon, r_baryon_prime=r_baryon_prime)
    kpvb_prime = kp * t1p + np.asarray(kappa_double_prime, dtype=float) * tau1

    coefficients = newtonian_coefficients(
        eta, k_com, delta_t=delta_t, phi_a=phi_a, kappa_prime=kp, v_b=tau1)
    c1p = newtonian_c1_prime(
        eta, k_com, delta_t=delta_t, phi_a=phi_a, phi_a_prime=phi_a_prime,
        phi_h_prime=phi_h_prime, tau_1=tau1, conformal_hubble=conformal_hubble,
        kappa_prime_v_b_prime=kpvb_prime)
    zero = np.zeros_like(np.asarray(eta, dtype=float))
    return CoefficientSet(coefficients=coefficients, c1_prime=c1p,
                          c2_second=zero, c2_prime_star=0.0)


__all__ += ["CoefficientSet", "tau_1_prime", "newtonian_set"]
