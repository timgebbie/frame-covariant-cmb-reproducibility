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
$\tilde C_1$ alone survives, which is (110). The CDM frame is $q_a=0$ and
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
    a_b1_prime = newtonian_a_b1_prime(
        k_com, delta_t=delta_t, phi_a=phi_a, phi_a_prime=phi_a_prime,
        phi_h_prime=phi_h_prime, tau_1=tau_1, conformal_hubble=conformal_hubble)
    # (107): -C~_1' = (kappa' v~_B)' + (1/k)(a B~_1)'
    return -(np.asarray(kappa_prime_v_b_prime, dtype=float)
             + a_b1_prime / float(k_com))


def newtonian_a_b1_prime(
    k_com: float,
    *,
    delta_t: np.ndarray,
    phi_a: np.ndarray,
    phi_a_prime: np.ndarray,
    phi_h_prime: np.ndarray,
    tau_1: np.ndarray,
    conformal_hubble: np.ndarray,
) -> np.ndarray:
    r"""$(a\tilde{\mathcal B}_1)'$ --- **(106) itself**, before (107) wraps it.

    Split out of `newtonian_c1_prime` unchanged, because it is the *dynamical*
    input a second frame needs and differencing it out of $\tilde C_1'$ would
    be arithmetic standing in for a derivation. (107) is one line and belongs
    to the Newtonian specialisation; (106) is the evolution equation, and
    `cdm_set` consumes it directly.
    """
    k = float(k_com)
    aH = np.asarray(conformal_hubble, dtype=float)
    a_b1 = k * (np.asarray(delta_t, dtype=float) + np.asarray(phi_a, dtype=float))
    return (
        -aH * a_b1
        + k * (np.asarray(phi_a_prime, dtype=float)
               - np.asarray(phi_h_prime, dtype=float))
        - 2.0 * aH * k * np.asarray(phi_a, dtype=float)
        + (k**2 / 3.0) * np.asarray(tau_1, dtype=float)
    )


__all__ += ["newtonian_c1_prime", "newtonian_a_b1_prime"]


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

    # --- the primitives of (89), kept because (101) is printed in them -------
    # (102) is written in $C_A$; the fuller solution (101) it is approximated
    # from is written in $a\mathcal B_A$ and $v_B$. Reconstructing those from
    # the $C_A$ means re-applying the $1/k$ of (90) and the $k$ of (89)'s
    # $\kappa'v_B$ in the right places --- which is finding **T-25**, made once
    # already. They are carried instead, in the **printed** normalisation:
    # $v_B$, not $\tilde v_B=v_B/k$.
    a_b1: np.ndarray | None = None
    a_b1_prime: np.ndarray | None = None
    a_b2: np.ndarray | None = None
    a_b2_prime: np.ndarray | None = None
    a_b2_second: np.ndarray | None = None
    v_b: np.ndarray | None = None
    v_b_prime: np.ndarray | None = None


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
    k = float(k_com)
    a_b1 = k * (np.asarray(delta_t, dtype=float) + np.asarray(phi_a, dtype=float))
    return CoefficientSet(
        coefficients=coefficients, c1_prime=c1p,
        c2_second=zero, c2_prime_star=0.0,
        a_b1=a_b1,
        a_b1_prime=newtonian_a_b1_prime(
            k, delta_t=delta_t, phi_a=phi_a, phi_a_prime=phi_a_prime,
            phi_h_prime=phi_h_prime, tau_1=tau1, conformal_hubble=conformal_hubble),
        a_b2=zero, a_b2_prime=zero, a_b2_second=zero,
        # (89) prints kappa' v_B; the bundle carries v~_B = tau~_1 = v_B/k.
        v_b=k * tau1, v_b_prime=k * t1p,
    )


__all__ += ["CoefficientSet", "tau_1_prime", "newtonian_set"]


def cdm_frame_shear(
    k_com: float,
    *,
    v: np.ndarray,
    phi_a: np.ndarray,
    phi_h: np.ndarray | None = None,
    scale_factor: np.ndarray,
    conformal_hubble: np.ndarray,
    rho: np.ndarray,
    pressure: np.ndarray | float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r"""$\sigma$, $\dot\sigma$, $\ddot\sigma$ in the CDM frame, $A_a=0$.

    The shear sector is **empty in the Newtonian frame and occupied here**, so
    this is what puts anything into (102)'s rank-two terms for the first time.

    `v` is the frame velocity as `frame_transform.cdm_frame_shift`
    returns it: $v=-v^N$ in *Annals II*'s notation, where $\tilde u^a\approx
    u^a+v^a$ and $n_a=u_a+v^N_a$ with $n^a$ the shear-free (Newtonian)
    frame. That identification is not a choice made here ---
    `FrameShift.temperature_shift` fixes it independently through **(42)**.
    `phi_a`, `phi_h` are the **Newtonian-frame** potentials; $\Phi_A\equiv0$ in
    the CDM frame, which is the frame condition.

    Three relations, and the first is **(31)**, not (40) --- see below:

        (31)  sigma~_ab ~= sigma_ab + D_<a v_b>        =>  sigma = -k_phys v
        (G)   sigma-dot + 2H sigma - D_<a A_b> + E ~= pi/2
        (32)  A~_a ~= A_a + v_a-dot + H v_a            =>  v' + Hv = -k Phi_A

    with $E_{ab}=\mathcal D_{\langle a}\mathcal D_{b\rangle}\Phi_A$, which is
    how *Annals II* **defines** $\Phi_A$ (from (G) with $\tilde\sigma_{ab}=0$).

    **These close identically.** Writing $\mathcal D_aX=\lambda k_{\rm phys}XQ_a$
    for a scalar and $\mathcal D_{\langle a}Q_{b\rangle}=rk_{\rm phys}Q_{ab}$,
    the residual of the three vanishes **for every $\lambda$ and every $r$** ---
    as it must, since it is a statement about physical fields and not about a
    basis. Checked symbolically. The corollary matters: **the closure is
    evidence for neither convention**, so it cannot be cited for C3.5, and that
    is why it did not catch the error recorded as T-24.

    **It is (31) and not (40).** *Annals II* gives the general frame
    transformations at (31)--(37), cited to Maartens, Gebbie & Ellis, and then
    specialises them to the Newtonian frame at (40)--(45). Two of the six
    change sign on the way: (40) prints $0\approx\sigma_{ab}-\mathcal
    D_{\langle a}v^N_{b\rangle}$ against (31)'s plus, and (45) prints $\tilde
    q_a\approx q_a+(\rho+p)v^N_a$ against (34)'s minus. Carried through with
    (40), the CDM frame **fails** to close against the field equations by
    exactly $2E_{ab}$, for every convention. Recorded as **B-13**.

    The signs below therefore come from (31) with **C4.2** ($r=-1$) and from
    **C3.5** ($s_Q=-1$, so $\lambda=+1$); $E$ then agrees with
    `frames.py::weyl_electric_amplitude`, which was written for criterion 2
    before this module existed. The general $\tfrac12(\Phi_A-\Phi_H)$ form is
    used, so no anisotropic stress is assumed even though v1.2.0's `potentials`
    supplies none.
    """
    a = np.asarray(scale_factor, dtype=float)
    k_phys = float(k_com) / a
    phi_a = np.asarray(phi_a, dtype=float)
    phi_h = -phi_a if phi_h is None else np.asarray(phi_h, dtype=float)

    # (31) with sigma~ = 0 and v = -v^N, then C4.2's r = -1.  **Not (40)** --- B-13.
    sigma = -k_phys * np.asarray(v, dtype=float)
    # E = D_<a D_b> Phi_A with C3.5's lambda = +1 and C4.2's r = -1.
    electric = -0.5 * k_phys**2 * (phi_a - phi_h)

    sigma_dot, sigma_ddot = generic_shear_derivatives(
        sigma=sigma, electric_weyl=electric, conformal_hubble=conformal_hubble,
        scale_factor=a, rho=rho, pressure=pressure,
    )
    return sigma, sigma_dot, sigma_ddot


__all__ += ["cdm_frame_shear"]


# ---------------------------------------------------------------------------
# The CDM frame as a *second* frame (102) can be evaluated in. Everything
# below exists so that a frame choice **cascades** --- the sources, their
# derivatives and the rank-two sector all follow from one velocity --- rather
# than being asserted by a label. Decision S8: the CDM frame is the
# CDM frame, which is the energy frame of the CDM component alone.
# ---------------------------------------------------------------------------


def background_fluid(
    scale_factor: np.ndarray,
    *,
    omega_m: float,
    omega_lambda: float = 0.0,
    omega_r: float = 0.0,
    h0: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r"""$(\rho,p,\mathcal H')$ for an FLRW background, from **one** expression.

    Appendix G's propagation equations carry $\rho$, $p$ and (through
    $\dot H=-H^2-(\rho+3p)/6$) the background acceleration. `Background` carries
    $\Omega$'s. Three numbers derived separately from those two descriptions can
    disagree by a sign or a factor and still look plausible, so they are derived
    here together and only once:

        script-H^2 = h0^2 ( Om_r/a^2 + Om_m/a + Om_k + Om_L a^2 )
        script-H'  = h0^2 ( -Om_r/a^2 - Om_m/(2a) + Om_L a^2 )      (exact)
        rho        = 3 script-H^2/a^2 - 3 h0^2 Om_k /a^2            (the fluids alone)
        p          = ( -6 script-H'/a^2 - rho ) / 3                 (Appendix G)

    $\Omega_k$ is subtracted from $\rho$ because curvature is not a fluid; the
    $p$ line then **defines** the pressure by Appendix G's own relation, so
    `c2_derivatives` recomputing $\mathcal H'$ from $(\rho,p)$ returns exactly
    the $\mathcal H'$ this function started from. `tests/` checks that round
    trip and checks $\mathcal H'$ against the `Background`'s own $\mathcal H$.
    """
    a = np.asarray(scale_factor, dtype=float)
    omega_k = 1.0 - omega_m - omega_lambda - omega_r
    cH_sq = h0**2 * (omega_r / a**2 + omega_m / a + omega_k + omega_lambda * a**2)
    cH_prime = h0**2 * (-omega_r / a**2 - omega_m / (2.0 * a) + omega_lambda * a**2)
    rho = 3.0 * cH_sq / a**2 - 3.0 * h0**2 * omega_k / a**2
    pressure = (-6.0 * cH_prime / a**2 - rho) / 3.0
    return rho, pressure, cH_prime


def cdm_set(
    eta: np.ndarray,
    k_com: float,
    *,
    delta_t: np.ndarray,
    phi_a: np.ndarray,
    phi_a_prime: np.ndarray,
    phi_h: np.ndarray,
    phi_h_prime: np.ndarray,
    tau_1: np.ndarray,
    kappa_prime: np.ndarray,
    kappa_double_prime: np.ndarray,
    conformal_hubble: np.ndarray,
    conformal_hubble_prime: np.ndarray,
    scale_factor: np.ndarray,
    rho: np.ndarray,
    pressure: np.ndarray | float,
    r_baryon: np.ndarray,
    r_baryon_prime: np.ndarray,
    v: np.ndarray,
    v_prime: np.ndarray,
    eta_star: float,
) -> CoefficientSet:
    r"""(102)'s full input set in the CDM frame, $A_a=0$, $\sigma_{ab}\ne0$.

    **Every argument is a Newtonian-frame quantity** except `v`, `v_prime`,
    which are the frame shift `frame_transform.cdm_frame_shift` returns
    ($u^a_{\rm E}=u^a_{\rm N}+v^a$, $v'+\mathcal Hv=-k\Phi_A$). The frame change
    is performed here, on the sources **and on their derivatives**, which is the
    part `to_frame` cannot do: `to_frame` moves five amplitudes, and (102) needs
    $C_1'$ and $C_2''$ as well. Transforming an amplitude and then
    differentiating it is finding **T-23** in a third place.

    The assembly is the same in both frames, and that is the point:

        a B_1 = k dT + aA ,     (a B_1)' = k dT' + (aA)'
        -C_1  = (1/k)( a B_1 + kappa' v_B )          (89)
        -C_2  = (1/k^2) a B_2 ,  B_2 = sigma_ab      (90)

    Only the *inputs* to that assembly know which frame they are in:

    | | Newtonian | CDM |
    |---|---|---|
    | $aA$ | $k\Phi_A$ | $0$ --- the frame condition |
    | $\delta T$ | $\delta\tilde T$ | $\delta\tilde T-\mathcal Hv/k$ (n-t3) |
    | $\tau_1$ | $\tilde\tau_1$ | $\tilde\tau_1-v$ (n-t4) |
    | $\mathcal B_2$ | $0$ | $-k_{\rm phys}v$ (n-t1) |

    **The dynamics enter once**, through (106) for $(a\tilde{\mathcal B}_1)'$ and
    (152) for $\tilde\tau_1'$, both in the Newtonian frame where *Annals II*
    derives them; $\delta\tilde T'$ is read off (106) and then shifted
    **exactly**, since $\mathcal H'$ is a background quantity and $v'$ is the
    Euler equation. Nothing here is splined.

    **The generic assembly is not used, and this records why.** The frame-free
    $\dot{\mathcal B}_1$ relation of
    `provenance/GENERIC-SOURCE-DERIVATIVES-v1.md` would give a second,
    independent route to $(a\mathcal B_1^{\rm E})'$ --- and it is still carrying
    the unresolved $(\star)=-H\mathcal D_{\langle a}\mathcal D_{b\rangle}\ln T$
    and needs $\Theta$, which no history in this bundle carries. Until $(\star)$
    is settled under \S2.5's $O(\epsilon\epsilon_H)$ bookkeeping that route
    cannot be a check, so it is named here and not used.
    """
    k = float(k_com)
    eta = np.asarray(eta, dtype=float)
    cH = np.asarray(conformal_hubble, dtype=float)
    cHp = np.asarray(conformal_hubble_prime, dtype=float)
    v = np.asarray(v, dtype=float)
    vp = np.asarray(v_prime, dtype=float)
    phi_a = np.asarray(phi_a, dtype=float)
    phi_a_prime = np.asarray(phi_a_prime, dtype=float)
    tau_1 = np.asarray(tau_1, dtype=float)
    kp = np.asarray(kappa_prime, dtype=float)
    kpp = np.asarray(kappa_double_prime, dtype=float)

    # --- rank one: the Newtonian dynamics, then the exact shift --------------
    a_b1_prime_N = newtonian_a_b1_prime(
        k, delta_t=delta_t, phi_a=phi_a, phi_a_prime=phi_a_prime,
        phi_h_prime=phi_h_prime, tau_1=tau_1, conformal_hubble=cH)
    # a B~_1 = k(dT~ + Phi_A)  =>  dT~' = [ (a B~_1)' - k Phi_A' ] / k
    delta_t_prime_N = a_b1_prime_N / k - phi_a_prime

    # n-t3, differentiated exactly: dT^E = dT~ - script-H v / k
    delta_t_E = np.asarray(delta_t, dtype=float) - cH * v / k
    delta_t_prime_E = delta_t_prime_N - (cHp * v + cH * vp) / k

    # A_a = 0 is the frame condition, so a B_1 is the temperature gradient alone
    a_b1_E = k * delta_t_E
    a_b1_prime_E = k * delta_t_prime_E

    # --- the Thomson term: n-t4, with (152) for the Newtonian dipole ---------
    tau_1_prime_N = tau_1_prime(k, tau_1=tau_1, delta_t=delta_t, phi_a=phi_a,
                                r_baryon=r_baryon, r_baryon_prime=r_baryon_prime)
    # **T-27**: the dipole is carried in the covariant normalisation
    # tau~_1 = v~_B = v_B/k, so (37) tau~_a = tau_a - v_a reads
    # tau~_1 -> tau~_1 - v/k here. The same 1/k the monopole carries in
    # `FrameShift.temperature_shift`, for the same reason.
    tau_1_E = tau_1 - v / k
    tau_1_prime_E = tau_1_prime_N - vp / k
    # **The two are differently normalised and the names do not say so.**
    # `match_coefficients` takes kappa' v_B, which is k times the kappa' v~_B of
    # (109); `newtonian_c1_prime` takes the derivative of the *un*-multiplied
    # one, because (107) reads -C_1' = (kappa' v~_B)' + (a B_1)'/k. Writing the
    # second with the k of the first is a factor of k_com -- 60 at the first k
    # this was run at -- and it is what the first draft of this function did.
    # Recorded as **T-25**; the argument names are now explicit about it.
    kappa_prime_v_b_E = k * kp * tau_1_E                       # for (89)
    kappa_prime_v_b_tilde_prime_E = kpp * tau_1_E + kp * tau_1_prime_E   # for (107)

    # --- rank two: the sector that is empty in the Newtonian frame -----------
    sigma, sigma_dot, sigma_ddot = cdm_frame_shear(
        k, v=v, phi_a=phi_a, phi_h=phi_h, scale_factor=scale_factor,
        conformal_hubble=cH, rho=rho, pressure=pressure)

    # **Evaluated through $v$, checked through Appendix G --- finding T-26.**
    # $a\mathcal B_2=a\sigma=-k_{\rm com}v$ exactly ((31) and C4.2 with
    # $k_{\rm phys}=k/a$), so $-C_2=a\mathcal B_2/k^2$ collapses to $v/k$ and
    # its derivatives are $v'/k$, $v''/k$ --- both closed-form, $v'$ from the
    # Euler equation and $v''$ from differentiating it. `c2_derivatives` reaches
    # the same three numbers through $(a\sigma)''=a''\sigma+2a'\sigma'+a\sigma''$
    # with $\ddot\sigma$ from Appendix G, and **that route is unusable here**:
    # $\ddot\sigma\sim10^{15}$ against a result of order $10^{-3}$, so the exact
    # relation loses about eighteen significant figures to cancellation and
    # returns noise. T-23 said a derivative must come from a published relation
    # rather than a spline; T-26 is the other edge of the same knife --- the
    # published relation must also be *evaluated* in a variable that does not
    # cancel. Appendix G stays, as the check `tests/` runs on $\ddot\sigma$
    # itself, where nothing cancels.
    vpp = -cHp * v - cH * vp - k * phi_a_prime      # d/d(eta) of the Euler equation
    c2, c2_prime, c2_second = v / k, vp / k, vpp / k

    a = np.asarray(scale_factor, dtype=float)
    a_b2 = a * sigma
    coefficients = match_coefficients(
        eta, k, a_b1=a_b1_E, a_b2=a_b2,
        kappa_prime_v_b=kappa_prime_v_b_E, frame="cdm")
    # (90) through `match_coefficients` and the $v$ route must agree.
    if not np.allclose(coefficients.c2, c2, rtol=1e-12, atol=0.0):
        raise ValueError(
            "match_coefficients and the v route disagree on C_2: p_2 from (89) "
            "and the n-t1 reduction have drifted apart")
    # The **first** derivative is well conditioned both ways, so Appendix G is
    # still held to account where it can be: (a sigma)' = a'sigma + a^2 sigma-dot
    # must be -k v'. Only the second derivative cancels (T-26).
    a_sigma_prime = a * cH * sigma + a**2 * sigma_dot
    if not np.allclose(a_sigma_prime, -k * vp, rtol=1e-9, atol=0.0):
        raise ValueError(
            "Appendix G's sigma-dot and the Euler equation disagree on "
            "(a sigma)'; the CDM frame no longer closes")

    # (107), with both halves of the derivative built from published relations
    c1_prime = -(kappa_prime_v_b_tilde_prime_E + a_b1_prime_E / k)

    return CoefficientSet(
        coefficients=coefficients,
        c1_prime=c1_prime,
        c2_second=c2_second,
        c2_prime_star=float(np.interp(float(eta_star), eta, c2_prime)),
        a_b1=a_b1_E, a_b1_prime=a_b1_prime_E,
        a_b2=-(k**2) * c2, a_b2_prime=-(k**2) * c2_prime,
        a_b2_second=-(k**2) * c2_second,
        v_b=k * tau_1_E, v_b_prime=k * tau_1_prime_E,
    )


__all__ += ["background_fluid", "cdm_set"]
