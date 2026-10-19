"""The v1.0.0 driver: background to $C_\\ell$, assembling the tested parts.

Nothing new is derived here. Every piece has its own module, its own published
equation number and its own tests; this file is the wiring, and it is kept
separate for that reason --- a bug here is a plumbing bug, and a bug in the parts
is a physics bug, and the two should not be able to hide in each other.

The chain, with the equation each step implements:

    background        the 1+3 energy constraint          functions.background
    recombination     visibility (101), damping (168)    functions.spectra.decoupling
    potentials        the growth equation, Phi ~ D/a     functions.spectra.potentials
    acoustic          (152), (153)                       functions.spectra.acoustic
    sources           (177), (178), (179)                functions.spectra.sources
    line of sight     (176)                              functions.spectra.sources
    angular spectrum  (186) and (187)+(188)              functions.spectra.angular

**Primordial power.** (186) integrates $\\int dk\\,k^2\\,\\mathcal P(k)|T_\\ell|^2$,
and a scale-invariant spectrum is $\\mathcal P\\propto k^{n_s-4}$ in that
convention: at $n_s=1$ it gives $\\int dk\\,k^{-1}j_\\ell^2 = 1/[2\\ell(\\ell+1)]$ and
hence a flat $\\ell(\\ell+1)C_\\ell$, which is the definition of scale invariance
and is asserted as a test rather than assumed. Appendix J's $\\mathcal A(k\\eta_0)^{n-1}$
is the same statement after the $k^{-3}$ of the measure is moved across.

**Tight coupling is integrated only while it holds.** (152) and (153) have
equilibrium $\\delta\\tilde T\\to-(1+R)\\Phi_A$, and $R$ reaches $\\sim680$ by
today, so integrating them to $\\eta_0$ returns $|\\delta\\tilde T|\\sim600$ --- the
equations faithfully tracking an equilibrium that ceased to be physical at
decoupling. They are stopped a few multiples of $\\eta_*$ past the visibility
peak and the result frozen, there being no scattering afterwards to drive the
monopole. `tight_coupling_factor` is that multiple, and the spectrum must be
insensitive to it; the test says so.

**The baryon velocity** is $\\tilde v_B=\\tilde\\tau_1$, the leading order of
(L005) in $1/\\dot\\kappa$ --- tight coupling locks the baryons to the radiation
dipole. It is not a free choice and it is not invented here.

**Where the weighting choice enters.** `weighting` selects which of the two
forms of the integrated source is used --- Annals II's visibility, or the
opacity of (98) that a late integrated Sachs--Wolfe term needs. It has **no
default**, by design. See `provenance/SOURCE-APPROXIMATIONS-v1.md`.

**The $\\eta$ grid is derived from $k_{\\max}$, not chosen** --- finding
**T-3**. The line-of-sight integrand carries $j_\\ell(k(\\eta_0-\\eta))$, which
oscillates with period $\\pi/k$ in $\\eta$. A fixed $\\eta$ grid therefore
resolves that oscillation at low $k$ and **aliases** it at high $k$, and the
aliased contribution does not announce itself: it returns a smooth, plausible
spectrum of entirely the wrong shape. This is the same argument the $k$ grid
already carried in `scripts/figure_f3_angular_spectrum.py` --- *a logarithmic
grid aliases the integrand at high k however many points it has* --- which had
never been applied to $\\eta$. At the shipped `n_eta=1000` the grid gave 3.7
points per oscillation at $k_{\\max}$ for CDM and **2.3 for $\\Lambda$CDM**, the
latter below the Nyquist limit of 2 at the band edge; $D_\\ell$ was wrong by up
to 94% and 575% respectively, and the $\\Lambda$CDM peak-to-plateau ratio read
37 where it converges to 7.0.

`n_eta` therefore defaults to `None`, meaning *derive it*, and an explicit value
that under-samples **raises** rather than aliasing quietly.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from functions.background.flrw import Background
from scipy.interpolate import CubicSpline

from functions.spectra.acoustic import (
    acoustic_start_eta,
    baryon_photon_ratio,
    required_acoustic_points,
    solve_acoustic,
    sound_horizon_from_zero,
)
from functions.spectra.angular import AngularSpectrum, angular_spectrum
from functions.spectra.bessel_table import BesselTable
from functions.spectra.coefficients import reduce_dipole
from functions.spectra.decoupling import RecombinationHistory, Weighting, diffusion_scale
from functions.spectra.potentials import matter_domination_eta, potentials
from functions.spectra.sources import (
    PUBLISHED_ISW_SIGN,
    PerturbationHistory,
    ScatteringHistory,
    source_doppler,
    source_integrated,
    source_primary,
)

__all__ = [
    "ETA_POINTS_PER_PERIOD",
    "K_POINTS_PER_PERIOD",
    "N_ETA_FLOOR",
    "SpectrumRun",
    "primordial_power",
    "required_k_points",
    "required_n_eta",
    "run",
]

#: Samples per $j_\ell$ oscillation the line-of-sight $\eta$ grid must carry at
#: the largest $k$ on the grid. Twelve, matching `BesselTable`'s sampling of the
#: same oscillation in $x$: the two grids resolve one function and there is no
#: reason for them to disagree about how finely. Nyquist is 2; the shipped
#: v1.0.0-rc grid sat at 2.3 for ΛCDM, which is how finding T-3 happened.
ETA_POINTS_PER_PERIOD = 12


#: Floor on the $\eta$ grid, under the rate `required_n_eta` derives from $k$.
#:
#: **Finding T-45 put it in `two_route`; finding T-58 moved it here.** The rate
#: is arithmetic from $k$ and the floor is not: it exists because the
#: *recombination* structure, not the $j_\ell$ oscillation, sets the sampling
#: the integrand actually needs near $\eta_*$, and nothing in this bundle yet
#: derives that. T-45 measured the consequence of going without it --- at
#: $k=600$ the two routes differed by $2.2\times10^{-4}$ on 4000 points and
#: $9.6\times10^{-4}$ on 8000, *non-monotone*, which is aliasing rather than
#: convergence.
#:
#: **`two_frame` never had it**, and that is most of what was left of **Q12**
#: once the window and the lower limit were settled: with its grid taken from
#: `k_max` alone it sat at $2.4\times10^{-1}$ against `two_route`'s
#: (177)--(179) column at $k=10$, and at $5.9\times10^{-3}$ once the floor was
#: applied --- a factor of forty from one number neither route was deriving.
#:
#: It is a **stand-in for S33**, which derives the recombination grid and
#: $\eta_*$ from the visibility rather than fixing either, and it should be
#: deleted the day S33 lands. Until then it is one hand-set number in one
#: place, which is the most that can honestly be said for it.
N_ETA_FLOOR = 8000


def required_n_eta(
    k_max: float, eta_span: float, *, points_per_period: int = ETA_POINTS_PER_PERIOD
) -> int:
    """How many $\\eta$ samples the line-of-sight integral needs, from $k_{\\max}$.

    $j_\\ell(k(\\eta_0-\\eta))$ has period $\\pi/k$ in $\\eta$, so resolving it at
    the band edge takes `points_per_period` samples per $\\pi/k_{\\max}$ across
    the whole span. This is arithmetic, not a tuning knob, which is why it is
    computed rather than configured.
    """
    if k_max <= 0.0 or eta_span <= 0.0:
        raise ValueError("k_max and eta_span must be positive")
    return int(np.ceil(points_per_period * k_max * eta_span / np.pi))


#: Samples per $j_\ell^2$ oscillation the **$k$** grid must carry. Three, and
#: **not** the twelve above, because the two grids integrate the same kernel
#: against different companions and the arithmetic says so rather than taste.
#:
#: The $\eta$ grid integrates $j_\ell$ against a source that itself oscillates,
#: so phase error accumulates along the line of sight and T-3 happened at 2.3.
#: The $k$ grid integrates $j_\ell^{\,2}$ --- sign-definite, against a smooth
#: $k^2\mathcal P(k)$ --- so the trapezoid converges far faster. Measured
#: against the closed form in `required_k_points`, on `PLANCK_MODEL`:
#:
#:     samples per period   1.92     3.84     7.67
#:     worst error, l<=400  0.4%     0.4%     0.4%
#:     worst error, l<=200  0.1%     0.1%     0.1%
#:
#: Flat from Nyquist upward: the residual at $\ell\ge600$ is the $k_{\max}$
#: truncation of **T-32**, not $dk$. Three is Nyquist plus half, which buys
#: nothing measurable and costs 50% --- it is there because the margin is what
#: separates a derived grid from a grid that was measured once and got lucky.
K_POINTS_PER_PERIOD = 3


def required_k_points(
    k_max: float, eta_span: float, *, points_per_period: int = K_POINTS_PER_PERIOD
) -> int:
    r"""How many $k$ samples $C_\ell=\int dk\,k^2\mathcal P|T_\ell|^2$ needs.

    **Finding T-56, and it is `required_n_eta` read along the other axis.**
    One kernel, $j_\ell(k\,\Delta\eta)$, is sampled on two grids: at fixed $k$
    across $\eta$, which is the function above, and at fixed $\Delta\eta$
    across $k$, which is this one. In $k$ the period of $j_\ell$ is
    $2\pi/\Delta\eta$ and the spectrum integrates its **square**, so the
    period that must be resolved is $\pi/\Delta\eta$ and

    $$dk\;\le\;\frac{\pi}{\texttt{points\_per\_period}\;\Delta\eta},
      \qquad n_k\;\ge\;\frac{\texttt{points\_per\_period}\,k_{\max}\Delta\eta}
      {\pi},$$

    which is the formula above with $\Delta\eta$ in place of the $\eta$ span.
    **The bundle derived one of the two and set the other by hand.** F9 shipped
    `np.arange(0.05, 1500.0, np.pi/3)` with a comment arguing, correctly, that
    a *logarithmic* grid aliases --- and then chose the linear spacing without
    asking what it had to resolve. On $\Lambda$CDM and `PLANCK_MODEL`, where
    $\Delta\eta\simeq3.13$, that is **0.94--0.96 samples per oscillation**:
    below one. On Einstein--de Sitter, $\Delta\eta\simeq1.94$, it is 1.55 and
    the figure looked plausible, which is why it survived.

    **The acceptance is a closed form, not a convergence study.** For a pure
    Sachs--Wolfe transfer $T_\ell=j_\ell(k\Delta\eta)$ at $n_s=1$, where
    $\mathcal P\propto k^{-3}$,

    $$\int_0^\infty\!dk\;k^2\mathcal P(k)\,j_\ell^2(k\Delta\eta)
      \;=\;\int_0^\infty\!\frac{dk}{k}\,j_\ell^2(k\Delta\eta)
      \;=\;\frac{1}{2\ell(\ell+1)},$$

    independent of $\Delta\eta$. So the quadrature can be checked against an
    exact number at every $\ell$ with no physics in the comparison at all, and
    `tests/test_k_grid.py` does, including on F9's shipped grid, where the
    error reaches **22.5%** at $\ell=2$ and is non-monotonic in $\ell$ --- a
    spurious $\pm5\%$ ripple that moves peaks and moves them differently in
    each route, because each route's $T_\ell(k)$ aliases differently.

    `eta_span` is the **largest** $\Delta\eta=\eta_0-\eta$ the integrand
    reaches, so $\eta_0-\eta_*$ is the floor and $\eta_0-\eta_{\text{start}}$
    is the conservative choice; passing the smaller under-resolves the early
    part of the line-of-sight integral.
    """
    if k_max <= 0.0 or eta_span <= 0.0:
        raise ValueError("k_max and eta_span must be positive")
    return int(np.ceil(points_per_period * k_max * eta_span / np.pi))


def primordial_power(
    k_com: np.ndarray, *, n_s: float = 1.0, amplitude: float = 1.0
) -> np.ndarray:
    """P(k) in the convention (186) integrates against: P ~ k^{n_s - 4}.

    At $n_s=1$ this makes $\\ell(\\ell+1)C_\\ell$ flat for a pure Sachs--Wolfe
    transfer, which is what scale invariance means and what the test asserts.
    """
    return amplitude * np.asarray(k_com, dtype=float) ** (n_s - 4.0)


@dataclass(frozen=True)
class SpectrumRun:
    """A completed run: the spectrum plus everything needed to audit it."""

    spectrum: AngularSpectrum
    recombination: RecombinationHistory
    eta_star: float
    weighting: Weighting
    background: Background
    transfer: np.ndarray  # (n_ell, n_k), what (176) returned
    n_eta: int                     # the grid actually used, derived unless forced
    eta_points_per_period: float   # samples per j_l oscillation at k_max
    damping_at_k_max: float        # exp[-(k_max/k_D)^2]: what the k grid left out
    k_com: np.ndarray              # the grid itself, so convergence is testable
    power: np.ndarray              # P(k) on that grid, for the same reason

    @property
    def reaches_diffusion_scale(self) -> bool:
        r"""Whether the $k$ grid extends past the Silk damping cut-off.

        $\exp[-(k_{\max}/k_D)^2]$ is the weight still sitting on the integrand
        where the grid stops; small means the grid ran past the cut-off.

        **This is a readiness test for v1.2.0, not a convergence test for this
        release — finding T-16.** It used to be called
        `k_truncation_is_negligible` and `figure_f3_angular_spectrum.py` printed
        "TRUNCATED, not converged" whenever it was false, which was *every run*,
        beside the key figure of a released bundle. The statement is true of the
        integrand at the damping scale and false of the spectrum the figure
        draws: $j_\ell(k\Delta\eta)$ contributes around $k\simeq\ell/\Delta\eta$,
        so $\ell\le20$ lives near $k\simeq10$ on a grid that runs to 420. The
        acoustic peaks and Silk damping of v1.2.0 *do* need the cut-off; this
        release does not, and `cl_truncation_sensitivity` is what tests what
        this release claims.

        An alarm that fires on every correct run is worse than no alarm --- the
        lesson of T-4, printed next to the figure a reader looks at first.
        """
        return self.damping_at_k_max < 1e-2

    def cl_truncation_sensitivity(self, *, drop: float = 0.1,
                                  ell_max: int | None = None) -> float:
        r"""**The convergence test that matches what this release claims.**

        Recomputes every $C_\ell$ with the top `drop` fraction of the $k$ grid
        removed and returns the worst relative change. If discarding the last
        10% of the grid does not move the answer, the integral has converged
        over the range being plotted --- which is a direct statement about the
        output, needing no assumption about the integrand's shape.

        Cheap: the transfer function is already computed, so this is a second
        quadrature over an array that exists, not a second pipeline run.
        """
        from functions.spectra.angular import angular_spectrum

        keep = int(round(self.k_com.size * (1.0 - float(drop))))
        if keep < 8:
            raise ValueError("too little of the grid left to compare against")

        reduced = angular_spectrum(
            self.spectrum.ell, self.k_com[:keep],
            self.transfer[:, :keep], self.power[:keep],
        )
        full, cut = self.spectrum.cl_mode, reduced.cl_mode

        # **Measured over the range the release CLAIMS, not every l computed.**
        # The first version of this method took the maximum over all l, and
        # `figure_f3_angular_spectrum.py` computes out to l=400 while claiming
        # only l<=20 and shading the rest. It therefore reported 2.4e-1 and
        # called a converged spectrum unconverged --- the severity came entirely
        # from multipoles the figure tells the reader not to trust. Part of
        # finding T-16.
        if ell_max is not None:
            within = np.asarray(self.spectrum.ell) <= int(ell_max)
            if not within.any():
                raise ValueError(f"no computed l at or below {ell_max}")
            full, cut = full[within], cut[within]

        return float(np.max(np.abs(cut - full) / np.maximum(np.abs(full), 1e-300)))


def run(
    background: Background,
    *,
    ells: np.ndarray,
    k_com: np.ndarray,
    weighting: Weighting,
    n_s: float = 1.0,
    amplitude: float = 1.0,
    omega_b_h2: float = 0.0224,
    isw_sign: float = PUBLISHED_ISW_SIGN,
    n_eta: int | None = None,
    tight_coupling_factor: float = 6.0,
    damping_epoch: str = "star",
    expansion_coupling: bool = False,
    doppler_weighting: Weighting | None = None,
    acoustic_start: str = "derived",
) -> SpectrumRun:
    """Background -> C_l. `weighting` is required; see the module docstring.

    **`doppler_weighting` separates two approximations the code had conflated.**
    `provenance/SOURCE-APPROXIMATIONS-v1.md` records **A-1** (which weight the
    *gravitational* source of (179) carries) and **A-2** (which weight the
    *Doppler* source of (178) carries) as two decisions with two reasons. This
    function passed one `weighting` to both. `None` keeps that --- so no
    released number moves --- and an explicit value sets (178)'s weight
    independently, which is what finding **T-19** needed in order to be
    measured at all.

    `n_eta=None` derives the grid from `k_com.max()` via `required_n_eta`. An
    explicit value below that requirement raises: see finding T-3, where a
    hand-set 1000 aliased the line-of-sight integrand and moved $D_\\ell$ by up
    to 575%.

    **`acoustic_start` is finding T-51, and `"derived"` is the correction.**
    Until 2026-10-16 every mode was integrated from the first point of the
    recombination grid --- `RecombinationHistory.build`'s ``z_max = 3000.0`` ---
    which discards **51% to 64%** of the sound horizon
    $r_s=\\int_0^{\\eta_*}c_s\\,d\\eta$. The accumulated phase $k\\,r_s$ was
    therefore halved and the acoustic peak spacing came out **2.0 to 3.0 times**
    the antecedent's own printed $\\Delta\\ell=\\pi r_\\theta/r_s$. With
    ``"derived"`` each mode starts where $k\\,r_s(\\eta)\\le\\varepsilon$, which
    is what (180)'s $\\delta T(0,k)\\simeq-\\tfrac23\\Phi_A(0,k)$, $\\tau_1=0$
    means by *at the big bang*, and the spacing lands within **0.5%** of the
    formula on all three backgrounds.

    ``"z_max"`` keeps the old behaviour **exactly**, including the potentials'
    old normalisation, so T-51 stays executable rather than only recorded ---
    the same discipline `sachs_wolfe_at_last_scattering_printed` keeps for B-8
    and `expansion_coupling` keeps for (154). It is a control, not an option:
    nothing should ship on it.
    """
    ells = np.asarray(ells, dtype=int)
    k_com = np.asarray(k_com, dtype=float)

    # --- k-independent: recombination, potentials, the background grid -------
    recombination = RecombinationHistory.build(background, omega_b_h2=omega_b_h2)
    eta_star = recombination.eta_star

    # --- T-3: the eta grid is derived from k_max, never assumed --------------
    eta_span = float(background.eta_0 - recombination.eta[0])
    k_max = float(k_com.max())
    needed = required_n_eta(k_max, eta_span)
    if n_eta is None:
        n_eta = needed
    elif n_eta < needed:
        raise ValueError(
            f"n_eta={n_eta} aliases the line-of-sight integrand: j_l(k(eta_0-eta)) "
            f"has period pi/k_max = {np.pi / k_max:.3e} in eta, and this grid gives "
            f"{np.pi / k_max / (eta_span / n_eta):.1f} samples per oscillation where "
            f"{ETA_POINTS_PER_PERIOD} are required (n_eta >= {needed}). "
            "Pass n_eta=None to derive it. See finding T-3."
        )

    if acoustic_start not in ("derived", "z_max"):
        raise ValueError("acoustic_start is 'derived' (the correction, T-51) "
                         "or 'z_max' (the control that reproduces it)")
    derived_start = acoustic_start == "derived"

    # **One reference for Phi_A, shared by every mode** --- see `potentials`.
    # The recombination grid's own first point, for **every** background.
    #
    # **It was matter-radiation equality for a background with radiation, and
    # that was wrong twice over --- finding T-55.** Wrong physically, because
    # `growth_factor` starts from D = a, the matter-domination growing mode,
    # and at equality the universe is half radiation, so the integration opens
    # on a transient. Wrong numerically, because `coefficients.cdm_set` holds
    # Appendix G's sigma-dot against the Euler equation at rtol=1e-9 over every
    # eta including those first points, and the transient sits exactly there:
    # it passed on Linux and **failed on the PI's Windows machine**, from
    # nothing but DOP853 choosing different steps.
    #
    # And unnecessary. `constant_below` exists so that a mode starting at 1e-4
    # and the common grid starting at 0.033 share one Phi_A(0,k); any fixed eta
    # does that, and Phi is held CONSTANT below it either way --- which is the
    # antecedent's own result, Phi_E time-independent for K=0 dust (Appendix G).
    # Taking the grid's first point makes the common-grid potentials
    # bit-identical to the pre-T-51 ones on every background, so **no released
    # number moves for this reason**, only for T-51's.
    #
    # `matter_domination_eta` remains, as the diagnostic that measures A-3's
    # marginality --- rho_M/rho_R = 5.16 at last scattering for Planck
    # parameters --- and is no longer an input to anything computed.
    md_reference = float(recombination.eta[0])

    # r_s from the big bang: what `acoustic_start_eta` reads to place each
    # mode's start, and the quantity the antecedent's own peak-spacing formula
    # is written in. T-51.
    eta_rs, r_s_table = sound_horizon_from_zero(
        background, float(recombination.eta_star), omega_b_h2=omega_b_h2)

    eta = np.linspace(recombination.eta[0], background.eta_0, n_eta)
    phi_a, phi_h = (potentials(background, eta, constant_below=md_reference)
                    if derived_start else potentials(background, eta))
    a = background.a_of_eta(eta)
    aH = background.conformal_hubble(a)
    r = baryon_photon_ratio(a, omega_b_h2=omega_b_h2)

    kappa_prime = np.interp(eta, recombination.eta, recombination.kappa_prime)
    visibility = np.interp(eta, recombination.eta, recombination.visibility)
    opacity = np.interp(eta, recombination.eta, recombination.opacity)
    gravitational_weight = visibility if weighting is Weighting.ANNALS_II else opacity
    # A-1 is the gravitational weight, A-2 the Doppler weight: two approximations,
    # recorded separately, and until now driven by one knob. See T-19.
    doppler_choice = weighting if doppler_weighting is None else doppler_weighting
    doppler_weight = visibility if doppler_choice is Weighting.ANNALS_II else opacity
    k_d = diffusion_scale(recombination, r_of_eta=recombination.kappa_prime * 0.0)
    # **The release stipulates k_D at last scattering; the running k_D(eta) is
    # the fuller statement.** Both are kept and neither is hidden: `"star"` is
    # the default and is what every released figure uses, `"running"` is what
    # F6 ratios it against. An approximation whose cost nobody has measured is
    # a free parameter in disguise.
    damping_k_star = float(k_d(eta_star))
    if damping_epoch not in ("star", "running"):
        raise ValueError("damping_epoch is 'star' (the release) or 'running'")
    # **`k_d(min(eta, eta_*))`, not `k_d(eta)`.** Diffusion damping accumulates
    # only while the photons are still scattering. After last scattering
    # kappa' -> 0, so 1/kappa' in (dif-damp) diverges and k_D(eta) collapses,
    # which would damp every integrated source to nothing --- an artefact of
    # evaluating a plasma formula in a universe that has none. Measured before
    # this clamp was added, the "fuller" variant reported the release's choice
    # as costing a factor of nine at l=2, and the factor was the artefact.
    # Frozen after eta_*, the running k_D is the physical statement and the
    # comparison in F6 is a real one.
    damping_k = (damping_k_star if damping_epoch == "star"
                 else np.asarray(k_d(np.minimum(eta, eta_star)), dtype=float))

    # One Bessel table serves every (k, eta) pair: j_l depends on k*dEta only.
    # **Only the requested multipoles are tabulated** --- finding T-18. `ells`
    # is logarithmic and sparse, so building the contiguous 0..ell_max range
    # spends ~60x the memory and the build time on multipoles nothing asks for,
    # which is unnoticeable at ell_max=400 and is 1.5 GB at ell_max=2000.
    table = BesselTable.build(
        ell_max=int(ells.max()), ells=ells,
        x_max=float(k_com.max() * (background.eta_0 - eta[0])) + 20.0,
    )

    transfer = np.zeros((ells.size, k_com.size))

    # **Tight coupling is integrated only while it holds.** Its equilibrium is
    # dT -> -(1+R)Phi_A, and R reaches ~680 by today, so running (152)/(153) to
    # eta_0 gives |dT| ~ 600 -- the equations tracking an equilibrium that stopped
    # being physical at decoupling. After last scattering there is no scattering
    # to drive the monopole, so dT and tau_1 are **frozen** at their values at
    # the end of the tight-coupling window. The window is carried a few multiples
    # of eta_* past the visibility peak so that nothing is cut while the
    # visibility is still non-negligible.
    eta_couple = min(float(background.eta_0), tight_coupling_factor * eta_star)
    inside = eta <= eta_couple
    if inside.sum() < 50:
        raise ValueError("the tight-coupling window is too short to integrate")

    def freeze(values: np.ndarray) -> np.ndarray:
        out = np.empty_like(eta)
        out[inside] = values
        out[~inside] = values[-1]
        return out

    # **The potentials are splined once, not re-integrated per mode.** Each
    # mode now has its own grid, and `potentials` runs a growth integration on
    # an internal 8192-point grid; doing that 1433 times would spend the whole
    # run on a quantity that does not depend on k at all. The shape is a
    # function of eta alone, so it is built once over the widest span any mode
    # will ask for and evaluated per mode.
    if derived_start:
        earliest = acoustic_start_eta(float(k_com.max()), eta_rs, r_s_table)
        master = np.logspace(np.log10(earliest), np.log10(eta_couple), 16_384)
        master_a, master_h = potentials(
            background, master, constant_below=md_reference)
        phi_a_of, phi_h_of = CubicSpline(master, master_a), CubicSpline(master, master_h)

    for i, k in enumerate(k_com):
        if derived_start:
            # T-51. The start is k's, not z_max's; the grid is k's too.
            start = acoustic_start_eta(float(k), eta_rs, r_s_table)
            mode_eta = np.linspace(
                start, eta_couple, required_acoustic_points(float(k), eta_couple - start))
            acoustic = solve_acoustic(
                float(k), mode_eta, background=background,
                phi_a=phi_a_of(mode_eta), phi_h=phi_h_of(mode_eta),
                omega_b_h2=omega_b_h2, expansion_coupling=expansion_coupling,
            )
            # Onto the common grid. `np.interp` holds the end value beyond
            # `eta_couple`, which **is** the freeze the tight-coupling window
            # calls for --- the same clamp, arrived at by the same reasoning,
            # not a coincidence worth leaving unremarked.
            delta_T = np.interp(eta, mode_eta, acoustic.delta_T)
            tau_1 = np.interp(eta, mode_eta, acoustic.tau_1)
        else:
            acoustic = solve_acoustic(
                float(k), eta[inside], background=background,
                phi_a=phi_a[inside], phi_h=phi_h[inside],
                omega_b_h2=omega_b_h2, expansion_coupling=expansion_coupling,
            )
            delta_T, tau_1 = freeze(acoustic.delta_T), freeze(acoustic.tau_1)
        # **Finding T-66.** `tau_1` stays as `solve_acoustic` returns it --- the
        # **velocity** normalisation, which is what (178)'s $(1/3)k\tilde\tau_1$
        # wants, since that term is $(1/k)(a\mathcal B_1)'$'s dipole piece.
        # `v_b` is the **reduced** $\tilde v_B=v_B/k$, which is what (177)'s
        # $\kappa'v_B$ and (178)'s $(\kappa'\tilde v_B)'$ want, per (109). The
        # two fields are differently normalised **and now they are each the one
        # their consumers assume**; before T-66 both were the oscillator's.
        history = PerturbationHistory(
            eta=eta, delta_T=delta_T, phi_a=phi_a, phi_h=phi_h,
            tau_1=tau_1, v_b=reduce_dipole(tau_1, float(k)), frame="newtonian",
        )
        scattering = ScatteringHistory(
            eta=eta, kappa_prime=kappa_prime, visibility=visibility, damping_k=damping_k
        )

        damping = scattering.diffusion(float(k))
        primary_at_star = float(
            np.interp(eta_star, eta, source_primary(history, scattering, damping_total=damping))
        )
        integrated = source_doppler(
            history, scattering, float(k), weight=doppler_weight
        ) + source_integrated(
            history, scattering, float(k),
            aH=aH, isw_sign=isw_sign, weight=gravitational_weight,
        )

        x = k * (background.eta_0 - eta)
        bessel = np.stack([table(int(l), x) for l in ells])          # (n_ell, n_eta)
        transfer[:, i] = (
            primary_at_star * np.array([float(table(int(l), k * (background.eta_0 - eta_star)))
                                        for l in ells])
            + np.trapezoid(integrated[None, :] * bessel, eta, axis=1)
        )

    power = primordial_power(k_com, n_s=n_s, amplitude=amplitude)
    spectrum = angular_spectrum(ells, k_com, transfer, power)
    return SpectrumRun(
        spectrum=spectrum, recombination=recombination, eta_star=eta_star,
        weighting=weighting, background=background, transfer=transfer,
        n_eta=int(n_eta),
        eta_points_per_period=float(np.pi / k_max / (eta_span / n_eta)),
        damping_at_k_max=float(np.exp(-((k_max / damping_k_star) ** 2))),
        k_com=k_com, power=power,
    )
