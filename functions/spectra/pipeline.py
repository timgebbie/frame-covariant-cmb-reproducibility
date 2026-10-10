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
from functions.spectra.acoustic import baryon_photon_ratio, solve_acoustic
from functions.spectra.angular import AngularSpectrum, angular_spectrum
from functions.spectra.bessel_table import BesselTable
from functions.spectra.decoupling import RecombinationHistory, Weighting, diffusion_scale
from functions.spectra.potentials import potentials
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
    "SpectrumRun",
    "primordial_power",
    "required_n_eta",
    "run",
]

#: Samples per $j_\ell$ oscillation the line-of-sight $\eta$ grid must carry at
#: the largest $k$ on the grid. Twelve, matching `BesselTable`'s sampling of the
#: same oscillation in $x$: the two grids resolve one function and there is no
#: reason for them to disagree about how finely. Nyquist is 2; the shipped
#: v1.0.0-rc grid sat at 2.3 for ΛCDM, which is how finding T-3 happened.
ETA_POINTS_PER_PERIOD = 12


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
) -> SpectrumRun:
    """Background -> C_l. `weighting` is required; see the module docstring.

    `n_eta=None` derives the grid from `k_com.max()` via `required_n_eta`. An
    explicit value below that requirement raises: see finding T-3, where a
    hand-set 1000 aliased the line-of-sight integrand and moved $D_\\ell$ by up
    to 575%.
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

    eta = np.linspace(recombination.eta[0], background.eta_0, n_eta)
    phi_a, phi_h = potentials(background, eta)
    a = background.a_of_eta(eta)
    aH = background.conformal_hubble(a)
    r = baryon_photon_ratio(a, omega_b_h2=omega_b_h2)

    kappa_prime = np.interp(eta, recombination.eta, recombination.kappa_prime)
    visibility = np.interp(eta, recombination.eta, recombination.visibility)
    opacity = np.interp(eta, recombination.eta, recombination.opacity)
    gravitational_weight = visibility if weighting is Weighting.ANNALS_II else opacity
    k_d = diffusion_scale(recombination, r_of_eta=recombination.kappa_prime * 0.0)
    damping_k = float(k_d(eta_star))

    # one Bessel table serves every (k, eta) pair: j_l depends on k*dEta only
    table = BesselTable.build(
        ell_max=int(ells.max()), x_max=float(k_com.max() * (background.eta_0 - eta[0])) + 20.0
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

    for i, k in enumerate(k_com):
        acoustic = solve_acoustic(
            float(k), eta[inside], background=background,
            phi_a=phi_a[inside], phi_h=phi_h[inside],
            omega_b_h2=omega_b_h2, expansion_coupling=False,
        )
        delta_T, tau_1 = freeze(acoustic.delta_T), freeze(acoustic.tau_1)
        history = PerturbationHistory(
            eta=eta, delta_T=delta_T, phi_a=phi_a, phi_h=phi_h,
            tau_1=tau_1, v_b=tau_1, frame="newtonian",
        )
        scattering = ScatteringHistory(
            eta=eta, kappa_prime=kappa_prime, visibility=visibility, damping_k=damping_k
        )

        damping = scattering.diffusion(float(k))
        primary_at_star = float(
            np.interp(eta_star, eta, source_primary(history, scattering, damping_total=damping))
        )
        integrated = source_doppler(
            history, scattering, float(k), weight=gravitational_weight
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
        damping_at_k_max=float(np.exp(-((k_max / damping_k) ** 2))),
        k_com=k_com, power=power,
    )
