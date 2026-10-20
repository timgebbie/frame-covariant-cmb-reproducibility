r"""The slow-decoupling integral solution, carried with a generic $u^a$ --- (102).

    (102)  tau_l(eta_0) beta_l / (2l+1)
             ~= [ C_2'(eta_*) - C_1(eta_*) ] D(eta_0,k) j_l(k dEta_*)
              +  k C_2(eta_*) D(eta_0,k)
                   [ l/(2l+1) j_{l-1}(k dEta_*) - (l+1)/(2l+1) j_{l+1}(k dEta_*) ]
              +  Int_{eta_*}^{eta_0} d(eta) V e^{-(k/k_D)^2}
                   { C_0(eta) - C_1'(eta) + C_2''(eta) } j_l(k dEta)

**This is (102), not (111).** The difference is the whole point of the module.
*Annals II* specialises to the Newtonian frame **before** it writes its
sources --- \S7.1.1, *"We therefore choose the Newtonian frame in which the
shear contribution does not appear"* --- so (110), (111) and hence (176)--(179)
carry $\tilde C_1$ alone. Everything this bundle computed before `coefficients.py`
descends from that. (102) carries all three coefficients and **a frame choice
sets them**, which is what makes the choice cascade rather than be asserted.

**The second line has never existed in this bundle.** $kC_2(\eta_*)$ against the
$j_{\ell\pm1}$ combination is a rank-two boundary term, and $\tilde C_2\equiv0$
in the Newtonian frame, so no released figure has ever evaluated it. It is also
why the Bessel table must now carry $\ell-1$ and $\ell+1$ --- cheap only because
finding **T-18** made that table sparse.

**Two routes for $C_1'$, both computed.** The generic route differentiates $C_1$
on the grid, because the point of carrying $u^a$ generic is not to re-derive
$C_1$'s expansion once per frame. The Newtonian route uses the expansion
*Annals II* performs between (109) and (111), which regroups into (178)'s
Doppler bracket and (179)'s ISW bracket. They must agree, and `tests/` reports
the number rather than asserting agreement.

**The lower limit is $\eta_*$**, as every integral in (98), (102), (110), (111)
and (176) prints it. `functions.spectra.pipeline` has always integrated from the
start of the recombination history instead; `eta_floor` makes that difference
measurable rather than silent.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import CubicSpline

from functions.spectra.bessel_table import BesselTable
from functions.spectra.coefficients import SourceCoefficients

__all__ = ["IntegralSolution", "integral_solution", "required_multipoles"]


def required_multipoles(ells: np.ndarray) -> np.ndarray:
    r"""The multipoles a (102) evaluation needs tabulated: $\ell-1,\ell,\ell+1$.

    The rank-two boundary term couples each $\ell$ to its neighbours, which the
    Newtonian specialisation hides because it multiplies $C_2$. A table built
    for `ells` alone silently lacks them --- and since T-18 the table **raises**
    on a multipole it does not carry rather than returning a different one.
    """
    ells = np.asarray(ells, dtype=int)
    if ells.min() < 0:
        raise ValueError("ells must be non-negative")
    return np.unique(np.concatenate([np.maximum(ells - 1, 0), ells, ells + 1]))


@dataclass(frozen=True)
class IntegralSolution:
    r"""(102)'s three terms, kept apart.

    `total` is what (186) consumes --- $\beta_\ell\tau_\ell/(2\ell+1)$, the
    quantity `functions.spectra.angular` calls the transfer function. The three
    pieces are retained because **$C_\ell$ is quadratic in the source, so they
    do not add**, and a decomposition that only ever shows the sum cannot
    display the cancellation finding T-19 measures.
    """

    ell: np.ndarray
    k_com: float
    boundary_scalar: np.ndarray    # [C_2'(eta_*) - C_1(eta_*)] D j_l
    boundary_shear: np.ndarray     # k C_2(eta_*) D [ ... j_{l-1} ... j_{l+1} ]
    integrated: np.ndarray         # Int V e^{-(k/k_D)^2} {C_0 - C_1' + C_2''} j_l
    total: np.ndarray

    @property
    def shear_boundary_is_empty(self) -> bool:
        """Whether the rank-two boundary term contributed at all.

        True in the Newtonian frame, where it is identically zero, and the
        single statement that distinguishes a specialised run from a generic
        one at the level of the solution rather than of the coefficients.
        """
        return bool(np.all(self.boundary_shear == 0.0))


def integral_solution(
    ells: np.ndarray,
    *,
    coefficients: SourceCoefficients,
    table: BesselTable,
    weight: np.ndarray,
    diffusion: np.ndarray | float,
    damping_total: float,
    eta_star: float,
    eta_0: float,
    c1_prime: np.ndarray,
    c2_second: np.ndarray | None = None,
    c2_prime_star: float = 0.0,
    eta_floor: float | None = None,
    c2_prime: np.ndarray | None = None,
    visibility: np.ndarray | None = None,
    by_parts_weight_terms: bool = False,
    opacity: np.ndarray | None = None,
    c1_thomson: np.ndarray | None = None,
    c1_thomson_prime: np.ndarray | None = None,
    c1_thomson_kappa: np.ndarray | None = None,
    slot_weight_split: bool = False,
    jprime_bulk_slot: bool = False,
    boundary_weight_w: bool = False,
    thomson_carries_shear: bool = False,
    c1_prime_isw: np.ndarray | None = None,
    w_half_is_isw_only: bool = False,
    thomson_boundary_and_vdot: bool = False,
) -> IntegralSolution:
    r"""Evaluate (102) at one $k$ for a set of multipoles.

    `weight` is $\mathcal V$ as (102) prints it, or $e^{-\kappa}$ where a caller
    departs from it --- approximation **A-2**, and finding **T-20**, which
    measures that the two are each right in one regime and neither in both. It
    has no default here for the same reason `Weighting` has none.

    `diffusion` is $e^{-(k/k_D)^2}$ on the integrand and `damping_total` is
    $\mathcal D(\eta_0,k)$ on the two boundary terms, which is how (102)
    distinguishes them.

    `c1_prime`, `c2_second` and `c2_prime_star` are **supplied, not computed
    here** --- finding **T-23**. Each $\mathcal B_A$ needs its own
    mode-expanded derivative relation, because the mode functions carry the
    scale factor; `newtonian_c1_prime` is the one *Annals II* derives at (106),
    and a generic frame owes its own. Differentiating the stored amplitude
    instead is wrong by a median of 100%, measured.

    `eta_floor` overrides (102)'s lower limit of $\eta_*$. Supplied so the
    pipeline's long-standing choice of integrating from the start of the
    recombination history can be **measured** against the printed one rather
    than inherited.
    """
    ells = np.asarray(ells, dtype=int)
    if ells.size == 0:
        raise ValueError("ells is empty")
    if ells.min() < 1:
        raise ValueError("(102)'s rank-two term needs ell >= 1 to carry j_{l-1}")

    eta = coefficients.eta
    k = float(coefficients.k_com)
    weight = np.asarray(weight, dtype=float)
    if weight.shape != eta.shape:
        raise ValueError("weight must share the coefficients' eta grid")

    # --- the derivatives are SUPPLIED, never differentiated here -------------
    # Finding **T-23**. Mode-expanding a derivative is not differentiating a
    # mode amplitude: the mode functions carry the scale factor, so
    # D_<a Bdot_b> expands as -(a/k)(Bdot_1 + 2 H B_1) D_<a D_b> Q -- the
    # footnote to (105) -- and the 2 H B_1 is invisible to a spline through the
    # amplitude. Measured against (106), a plain derivative of the stored
    # a B~_1 is wrong by a median of 100%. This is conventions row C3.1a in the
    # integral solution, and it is why Annals II derives (106) instead of
    # differentiating (105).
    c1_spline = CubicSpline(eta, coefficients.c1)
    c2_spline = CubicSpline(eta, coefficients.c2)
    c1_prime = np.asarray(c1_prime, dtype=float)
    c2_second = (np.zeros_like(eta) if c2_second is None
                 else np.asarray(c2_second, dtype=float))
    if c1_prime.shape != eta.shape or c2_second.shape != eta.shape:
        raise ValueError("the supplied derivatives must share the eta grid")

    # --- the integrand's source bracket, (102) third line --------------------
    bracket = coefficients.c0 - c1_prime + c2_second

    # **Finding T-72 --- the rank-two by-parts slot (102) never carries.**
    #
    # The exact bulk source of $\int W[C_0K+C_1K'+C_2K'']$, by parts, is
    #
    #     W C_0 - (W C_1)' + (W C_2)''
    #       = W(C_0 - C_1' + C_2'')  -  V C_1  +  2 V C_2'  +  Vdot C_2
    #
    # verified by direct quadrature independently by P1-T (1e-11..1e-15).
    # (102) carries **only the first group**. Of the other three:
    #
    #   -V C_1   collapses to the primary under $\int\mathcal V=1$, which is
    #            Annals II's own `visibe` step, and this bundle already carries
    #            it as the boundary term. Nothing to add.
    #   +2V C_2' and Vdot C_2 are **rank two**. They are identically zero in
    #            the Newtonian frame --- which is why Annals II never needed
    #            them, having specialised to that frame at \S7.1.1 *before*
    #            writing its sources --- and in the CDM frame they are, by
    #            T-62 and P1-T \S1.2, **the whole source**: $\delta T_E\equiv0$
    #            there, so rank one vanishes identically and everything the
    #            CDM column has must arrive through $C_2$.
    #
    # Measured: the frame gap is ~1.0--1.9 at **every** multipole and barely
    # moves when $C_0$ is rescaled by 7.5 (P2-T \S4's value). An
    # $\ell$-independent gap of order one is not a projection defect; it is a
    # source that is missing. This is it.
    #
    # The sign is the one `decoupling.py`'s convention forces: $\kappa$ is
    # built as `forward[-1] - forward`, so $d\kappa/d\eta=-\kappa'$ and
    # $W'=+\kappa'e^{-\kappa}=+\mathcal V$, **positive**.
    #
    # `by_parts_weight_terms=False` restores (102) exactly as printed, and is
    # the control. Nothing moves in the Newtonian frame either way.
    if by_parts_weight_terms and visibility is not None:
        vis = np.asarray(visibility, dtype=float)
        if c2_prime is not None:
            bracket = bracket + 2.0 * vis * np.asarray(c2_prime, dtype=float)
        if not np.all(coefficients.c2 == 0.0):
            vis_dot = np.gradient(vis, eta, edge_order=2)
            bracket = bracket + vis_dot * coefficients.c2

    integrand_weight = weight * np.asarray(diffusion, dtype=float)

    # **THE B-SLOT REPAIR --- findings T-85, T-86. Three independent controls,
    # every one of them `False` by default, so nothing released moves unless a
    # caller asks.** They exist to be measured, not to be believed.
    #
    # The identity the bundle is being held to is
    #
    #     Int g M j_l  =  [ W M j_l ]  -  Int W M' j_l  +  k Int W M j_l'
    #
    # and T-86 read what this file has against it: the boundary carries
    # D(eta_0,k) where the identity wants W(eta_*); the bulk carries
    # Int V.D {C_0 - C_1' + C_2''} j_l where the identity wants -Int W M' j_l,
    # so weight AND sign differ; and **the third term has no counterpart at
    # all**, because everything was by-parted onto the coefficients and that
    # decomposition is only legal at W.
    #
    # `slot_weight_split` separates C_1's two contents and gives each the
    # weight its physics calls for: the gravitational half under
    # $W=e^{-\kappa}$, the Thomson half under $g=\mathcal V$. Scattering
    # damping belongs to the scattering source; this is also **C6 / T-81b**,
    # which is why one change is expected to move three symptoms.
    #
    # `jprime_bulk_slot` supplies the missing $+k\int W M j_\ell'$. The
    # recurrence it needs is already in this file, at the rank-two boundary
    # term, which has never been evaluated because $C_2$ vanishes in every
    # Newtonian run.
    #
    # `boundary_weight_w` puts $W(\eta_*)$ on the boundary.
    #
    # **M11a governs how these are read.** T-77 is the instance: two defects
    # that fix it only together score as two failed fixes one at a time. The
    # measuring script walks the full 2^3 lattice for that reason, and no
    # single column licenses a conclusion.
    W_arr = None if opacity is None else np.asarray(opacity, dtype=float)
    if (slot_weight_split or jprime_bulk_slot or boundary_weight_w) and W_arr is None:
        raise ValueError(
            "the B-slot controls need `opacity` (e^-kappa) on the eta grid: "
            "the identity they implement is written at W weight and this "
            "function cannot invent it from `weight`, which A-2 may have set "
            "to V")

    c1_thom = (np.zeros_like(eta) if c1_thomson is None
               else np.asarray(c1_thomson, dtype=float))
    c1_thom_prime = (np.zeros_like(eta) if c1_thomson_prime is None
                     else np.asarray(c1_thomson_prime, dtype=float))
    c1_grav = coefficients.c1 - c1_thom
    c1_grav_prime = c1_prime - c1_thom_prime
    vis_dot_arr = (np.gradient(np.asarray(visibility, dtype=float), eta,
                               edge_order=2) if visibility is not None
                   else np.zeros_like(eta))

    # **`thomson_carries_shear` --- finding T-88, and it is T-82 read
    # forwards.** CAMB carries the rank-1 scattering source as $g(v_b+\sigma)$,
    # **one object**, and T-82 measured that in this bundle's variables the
    # boost-invariant combination is $\hat v_B + C_2$ to $10^{-15}$. The first
    # repair (D14, controls 1-3) split $C_1$ into gravitational and Thomson
    # halves and left $C_2$ in the rank-two sector --- that is, **it separated
    # the one pair T-82 had just shown must stay together**, and the CDM column
    # is where $C_2\ne0$, so that is exactly where it broke.
    #
    # With this on, the $g$-weighted slot carries $-\kappa'(\hat v_B + C_2)$
    # rather than $-\kappa'\hat v_B$. The added piece $-\kappa'C_2$ is a term
    # this bundle has nowhere at present.
    if thomson_carries_shear:
        if c1_thomson_kappa is None:
            raise ValueError(
                "thomson_carries_shear needs `c1_thomson_kappa` --- kappa' on "
                "the eta grid. It is not reconstructed from c1_thomson here: "
                "two routes to one quantity is what S8 forbids")
        kp_arr = np.asarray(c1_thomson_kappa, dtype=float)
        c2_arr = np.asarray(coefficients.c2, dtype=float)
        c2p_arr = (np.zeros_like(eta) if c2_prime is None
                   else np.asarray(c2_prime, dtype=float))
        kpp_arr = np.gradient(kp_arr, eta, edge_order=2)
        c1_thom = c1_thom - kp_arr * c2_arr
        c1_thom_prime = c1_thom_prime - (kpp_arr * c2_arr + kp_arr * c2p_arr)
        c1_grav = coefficients.c1 - c1_thom
        c1_grav_prime = c1_prime - c1_thom_prime

    # **`w_half_is_isw_only` --- finding T-89, and it is the k=300 failure.**
    #
    # T-88 moved the WHOLE gravitational half to $W$. That is wrong, and the
    # standard line-of-sight decomposition says why: the Sachs--Wolfe
    # combination $(\delta T+\Phi_A)$ is evaluated **at last scattering** and
    # belongs under $g$; only the potential derivative accumulated **along the
    # path** belongs under $W$. From (107),
    #
    #     -C_1' = (kappa' vhat_B)' + (a B_1)'/k ,
    #     (a B_1)'/k = (Phi_A' - Phi_H') + (k/3) tau_1
    #                   \_____ISW, -> W___/   \_dT', -> g_/
    #
    # so the gravitational half is itself two things, and only the first is a
    # path integral. Putting $(k/3)\tau_1$ under $W$ is putting a rapidly
    # oscillating source under the wrong weight, which is why T-88 rewrites the
    # Newtonian column by $7\times$ at $k=300$ and does nothing for the gap
    # there: $\tau_1$ oscillates fastest exactly where the repair fails.
    c1_isw = (np.zeros_like(eta) if c1_prime_isw is None
              else np.asarray(c1_prime_isw, dtype=float))
    # **THE BOUNDARY DERIVATION --- finding T-90, and it is what T-89 said was
    # missing.** (102) descends from $\int W[C_0K+C_1K'+C_2K'']$, and the
    # boundary is not an independent object: it is forced by the product rule.
    # For a term carried under $W$,
    #
    #     Int W C K' = [W C K] - Int V C K - Int W C' K ,
    #
    # and $[WCK]$ vanishes at both ends --- $W(\eta_0)=1$ with $j_\ell(0)=0$
    # for $\ell\ge1$ at the top, $W\to0$ at the bottom --- so the whole
    # boundary this bundle draws is the **collapse of $-\int\mathcal VCK$**
    # under $\int\mathcal V=1$, which is Annals II's `visibe` step.
    #
    # For a term carried under $\mathcal V$ instead, the product rule gives a
    # different shape entirely:
    #
    #     Int V C K' = [V C K] - Int Vdot C K - Int V C' K ,   [V C K] = 0
    #
    # because $\mathcal V$ vanishes at both ends. **So a $\mathcal V$-carried
    # term contributes NO primary and DOES contribute a $\dot{\mathcal V}C$
    # bulk term.**
    #
    # T-88 moved the Thomson half to $\mathcal V$ and left the boundary
    # carrying $C_1(\eta_*)$ **in full**. That double-counts the Thomson half
    # at the boundary and omits its $\dot{\mathcal V}$ bulk term. This control
    # supplies both corrections together, because the derivation produces them
    # together and **M11a is the standing reason not to test them apart**.
    if slot_weight_split:
        # the gravitational half moves to W; the Thomson half keeps V
        if w_half_is_isw_only:
            # only the ISW goes to W; the dynamical remainder stays at V with
            # the Thomson half, where (102) already had it
            bracket_w = coefficients.c0 - c1_isw + c2_second
            c1_thom_prime = c1_thom_prime + (c1_grav_prime - c1_isw)
            c1_grav_prime = c1_isw
        else:
            bracket_w = coefficients.c0 - c1_grav_prime + c2_second
        bracket_v = -c1_thom_prime
        weight_w = W_arr * np.asarray(diffusion, dtype=float)
        weight_v = (visibility if visibility is not None else weight) \
            * np.asarray(diffusion, dtype=float)
    else:
        bracket_w, weight_w = bracket, integrand_weight
        bracket_v, weight_v = None, None

    floor = float(eta_star if eta_floor is None else eta_floor)
    inside = eta >= floor
    if inside.sum() < 8:
        raise ValueError("too little of the grid lies above the lower limit")

    # --- the two boundary terms, at eta_* ------------------------------------
    c1_star = float(c1_spline(eta_star))
    # T-90: with the Thomson half carried at V it contributes no primary, so
    # the boundary keeps only the W-carried (gravitational) part of C_1.
    c1_grav_star = float(CubicSpline(eta, c1_grav)(eta_star))
    c2_star = float(c2_spline(eta_star))
    c2_prime_star = float(c2_prime_star)
    x_star = k * (eta_0 - eta_star)
    x = k * (eta_0 - eta)

    scalar = np.empty(ells.size)
    shear = np.empty(ells.size)
    integrated = np.empty(ells.size)
    for i, ell in enumerate(ells):
        l = int(ell)
        j_l_star = float(table(l, np.array([x_star]))[0])
        boundary_weight = damping_total * (
            float(np.interp(eta_star, eta, W_arr)) if boundary_weight_w
            else 1.0)
        c1_at_star = (c1_grav_star if thomson_boundary_and_vdot else c1_star)
        scalar[i] = (c2_prime_star - c1_at_star) * boundary_weight * j_l_star

        # The rank-two boundary term. Zero wherever C_2 is, which is every
        # Newtonian run, and the reason this line has never been evaluated.
        if c2_star == 0.0:
            shear[i] = 0.0
        else:
            j_lm1 = float(table(l - 1, np.array([x_star]))[0])
            j_lp1 = float(table(l + 1, np.array([x_star]))[0])
            combination = (l / (2 * l + 1)) * j_lm1 - ((l + 1) / (2 * l + 1)) * j_lp1
            shear[i] = k * c2_star * damping_total * combination

        j_l = table(l, x)
        total_bulk = (weight_w * bracket_w * j_l)
        if bracket_v is not None:
            total_bulk = total_bulk + weight_v * bracket_v * j_l
        if thomson_boundary_and_vdot:
            # - Int Vdot C_1^thom K : the term a V-carried piece owes and
            #   which (102) has nowhere, because (102) carries nothing at V.
            total_bulk = total_bulk - (vis_dot_arr
                                       * np.asarray(diffusion, dtype=float)
                                       * c1_thom * j_l)
        if jprime_bulk_slot:
            # j_l' = [ l j_{l-1} - (l+1) j_{l+1} ] / (2l+1) -- the SAME
            # recurrence the rank-two boundary uses twenty lines above, and
            # finding T-23's rule: a derivative comes from a published
            # relation, never from differentiating a table.
            j_lm1_grid = table(l - 1, x)
            j_lp1_grid = table(l + 1, x)
            j_l_prime = ((l / (2 * l + 1)) * j_lm1_grid
                         - ((l + 1) / (2 * l + 1)) * j_lp1_grid)
            total_bulk = total_bulk + k * (W_arr * np.asarray(diffusion, dtype=float)
                                           * (-c1_grav) * j_l_prime)
        integrated[i] = float(np.trapezoid(total_bulk[inside], eta[inside]))

    return IntegralSolution(
        ell=ells, k_com=k,
        boundary_scalar=scalar, boundary_shear=shear, integrated=integrated,
        total=scalar + shear + integrated,
    )
