"""Slow decoupling: optical depth, visibility, and the diffusion scale.

Annals II §5 and §5.2. Published equation numbers, resolved against the accepted
manuscript (`provenance/EQUATION-NUMBERS-ANNALS-II-v1.md`).

    (90)   -C_0 = +5/2 a B_2,  -C_1 = +1/k (a B_1 + kappa' v_B),  -C_2 = +1/k^2 a B_2

    (98)   the slow-decoupling integral solution, **before** the visibility
           approximation. Its weights are explicit and they are NOT the same on
           every term:

             gravitational sources   ... Int d(eta) e^{-kappa}      {...} j_l
             scattering sources      ... Int d(eta) kappa' e^{-kappa} [...] j_l

           and the text immediately after says so: "We see that damping effects
           are controlled by e^{-kappa} **and** kappa' e^{-kappa}."

    (102)  the same solution with both weights replaced by V = kappa' e^{-kappa}

    (visibility, §5.2)   V(k,eta) ~= kappa' e^{-kappa}
    (visibe)             D(eta_0,k) = Int d(eta) V e^{-(k/k_D)^2} ~= e^{-(k/k_D)^2}
    (dif-damp)           gamma ~= k^2 (1/kappa')/6 * [R^2 + 4/5 (1+R)]/(1+R)^2 = k^2/k_D^2

**The visibility on the integrated sources is a choice, not a defect.** The
single-$\\mathcal V$ form of (102), carried into (178)--(179), is applied to the
integrated part **deliberately**: the paper says so, at (102)'s derivation ---
"A similar correction is made using the visibility function in the integrated
part of the solution, in order to best deal with a changing ionization fraction."
Section 5.2 is the slow-decoupling solution, a specialisation built to model a
finite, changing ionisation fraction, and the visibility is the right weight for
that question.

The consequence matters more than the definition, and it is a **limit of range,
not an error**: (179) weighted by $\\mathcal V$ is *not* the standard integrated
Sachs-Wolfe term. The standard ISW carries the opacity $e^{-\\kappa}$ and
accumulates along the whole line of sight; this carries the visibility and
concentrates at last scattering. $\\mathcal V$ is a sharp spike there and is zero
to many decimal places by $z\\lesssim1$, where a late-ISW from $\\Lambda$
accumulates. So Annals II's expression cannot carry a late-ISW --- and in
Annals II it never needs to, because its own section 8.3.2 model is standard CDM
with no $\\Lambda$.

**Both weights are therefore first-class here, and which one is correct depends
on what is being computed.** Reproducing Annals II uses `Weighting.ANNALS_II`:
that is the comparison, and substituting $e^{-\\kappa}$ there would be
reproducing something the paper did not write. Computing the $\\Lambda$CDM
spectrum, which Annals II does not treat and v1.0.0 must deliver, uses
`Weighting.STANDARD_ISW`, the $e^{-\\kappa}$ of (98) --- which is the antecedent's
own weighting one equation earlier, before the slow-decoupling approximation is
made, and is also the Seljak & Zaldarriaga line-of-sight split this bundle
already cites.

(98) prints both weights explicitly and distinguishes them in its own text ---
"We see that damping effects are controlled by $e^{-\\kappa}$ **and**
$\\kappa'e^{-\\kappa}$" --- so neither weighting is imported from outside the
antecedent. Recorded as an approximation of the source in
`provenance/SOURCE-APPROXIMATIONS-v1.md`, **not** as a finding against it.

**If F4 is tested against a standard ISW it will mismatch, and that is not a
defect in this code.** The mismatch is the documented approximation, and the
figure must say which weighting it used.

**Recombination.** `saha_ionisation` is equilibrium Saha only. That is enough to
put last scattering in the right place and to exercise every weight above, and it
is *not* enough for the CAMB and CLASS comparison of criterion 5b: Saha
decouples too sharply and too early, which is why Peebles' effective three-level
atom exists. Stated here rather than discovered later; see the release notes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import CubicSpline

from functions.background.flrw import Background

__all__ = [
    "Weighting",
    "RecombinationHistory",
    "saha_ionisation",
    "diffusion_scale",
]

# Physical constants in the units this bundle uses: H0 = 1, lengths in 1/H0.
# Only ratios enter, so the Saha equation is written in terms of dimensionless
# combinations and the one dimensionful input is the baryon number density.
_B_HYDROGEN_EV = 13.605693
_T_CMB_K = 2.7255
_K_B_EV_PER_K = 8.617333262e-5
_M_E_EV = 510998.95


class Weighting(Enum):
    """Which weight the integrated gravitational source carries.

    `ANNALS_II` is (102)'s single $\\mathcal V=\\kappa'e^{-\\kappa}$, carried into
    (179). It is what Annals II deliberately writes, and it is the right choice
    **for reproducing Annals II**.

    `STANDARD_ISW` is (98)'s $e^{-\\kappa}$ on the gravitational source --- the
    antecedent's own weighting one equation earlier, before the slow-decoupling
    approximation, and the Seljak & Zaldarriaga split. It is the right choice
    **for the $\\Lambda$CDM spectrum**, which Annals II does not treat and which
    needs a late-ISW the visibility weighting cannot carry.

    Neither is a correction of the other, and there is deliberately **no
    default**: the caller states which question it is asking, because getting
    this wrong silently is the failure this enum exists to prevent.
    """

    ANNALS_II = "visibility"
    STANDARD_ISW = "opacity"


def saha_ionisation(z: np.ndarray, *, omega_b_h2: float = 0.0224) -> np.ndarray:
    """Equilibrium ionisation fraction x_e(z), Saha.

    Equilibrium only: no freeze-out, so this overestimates how fast the universe
    recombines. It places last scattering within a few percent in redshift, which
    is what the weights above need, and it is not adequate for criterion 5b.
    """
    z = np.asarray(z, dtype=float)
    temperature_ev = _K_B_EV_PER_K * _T_CMB_K * (1.0 + z)

    # n_b = 1.123e-5 Omega_b h^2 (1+z)^3 cm^-3; the Saha right-hand side is
    # (1/n_b)(m_e T/2pi)^{3/2} e^{-B/T} in natural units, assembled as a pure
    # number so that no unit system has to be carried through the module.
    n_b_cm3 = 1.123e-5 * omega_b_h2 * (1.0 + z) ** 3
    # (m_e T / 2 pi)^{3/2} in cm^-3, with hbar c = 1.9733e-5 eV cm
    hbar_c_ev_cm = 1.9733e-5
    thermal = (_M_E_EV * temperature_ev / (2.0 * np.pi)) ** 1.5 / hbar_c_ev_cm**3

    with np.errstate(over="ignore", under="ignore"):
        rhs = thermal / n_b_cm3 * np.exp(-_B_HYDROGEN_EV / temperature_ev)
    rhs = np.clip(rhs, 0.0, 1e30)

    # x^2/(1-x) = rhs  ->  x = (-rhs + sqrt(rhs^2 + 4 rhs))/2. Written in the
    # rationalised form 2 rhs / (rhs + sqrt(rhs^2 + 4 rhs)): the direct form
    # subtracts two nearly equal large numbers once rhs is big, and loses
    # monotonicity to rounding exactly where x_e should be flat at 1.
    root = np.sqrt(rhs**2 + 4.0 * rhs)
    return np.where(rhs > 0.0, 2.0 * rhs / np.maximum(rhs + root, 1e-300), 0.0)


@dataclass(frozen=True)
class RecombinationHistory:
    """kappa, kappa', the visibility V and the opacity e^{-kappa} on an eta grid.

    Both weights are carried, because (98) uses both and distinguishes them in
    its own text. Which one a caller wants depends on whether it is reproducing
    Annals II or computing $\\Lambda$CDM; see `Weighting`.
    """

    eta: np.ndarray
    x_e: np.ndarray
    kappa: np.ndarray
    kappa_prime: np.ndarray
    visibility: np.ndarray  # V = kappa' e^{-kappa}
    opacity: np.ndarray  # e^{-kappa}
    background: Background

    @classmethod
    def build(
        cls,
        background: Background,
        *,
        omega_b_h2: float = 0.0224,
        n_eta: int = 4000,
        z_max: float = 3000.0,
    ) -> "RecombinationHistory":
        eta_min = background.eta_at_redshift(z_max)
        eta = np.linspace(eta_min, background.eta_0, n_eta)
        a = background.a_of_eta(eta)
        z = 1.0 / np.clip(a, 1e-12, None) - 1.0

        x_e = saha_ionisation(z, omega_b_h2=omega_b_h2)

        # kappa' = a n_e sigma_T, in units where the normalisation is absorbed
        # into `thomson_scale`: only the shape and the location of the visibility
        # peak matter for the tests, and the scale is fixed by requiring
        # kappa(eta_0) = 0 with kappa increasing backwards in time.
        thomson_scale = _thomson_scale(omega_b_h2)
        kappa_prime = thomson_scale * x_e * a ** (-2)

        # kappa(eta) = Int_eta^eta_0 kappa' d(eta'), so kappa(eta_0) = 0
        forward = np.concatenate(([0.0], cumulative_trapezoid(kappa_prime, eta)))
        kappa = forward[-1] - forward

        opacity = np.exp(-kappa)
        return cls(
            eta=eta,
            x_e=x_e,
            kappa=kappa,
            kappa_prime=kappa_prime,
            visibility=kappa_prime * opacity,
            opacity=opacity,
            background=background,
        )

    # ---- derived quantities ------------------------------------------------

    @property
    def eta_star(self) -> float:
        """Last scattering: the peak of the visibility function, not kappa = 1.

        The visibility peak is the physically meaningful definition --- it is
        where photons actually last scatter --- and it is what (176)'s primary
        term is evaluated at.
        """
        return float(self.eta[int(np.argmax(self.visibility))])

    def visibility_norm(self) -> float:
        """Int V d(eta), which must be 1: V is a probability density.

        This is the identity that makes (visibe)'s `~= e^{-(k/k_D)^2}` hold, so
        it is checked rather than assumed.
        """
        return float(np.trapezoid(self.visibility, self.eta))

    def weight(self, which: Weighting) -> np.ndarray:
        """The weight the integrated gravitational source carries.

        See `Weighting`: this is a modelling choice tied to what is being
        computed, not a correction, and the caller must state it.
        """
        return self.visibility if which is Weighting.ANNALS_II else self.opacity


def _thomson_scale(omega_b_h2: float) -> float:
    """sigma_T n_{b,0} c / H0, dimensionless, for a_0 = 1.

    n_{b,0} = 1.123e-5 Omega_b h^2 cm^-3, sigma_T = 6.6525e-25 cm^2, and the
    Hubble length c/H0 = 2997.9/h Mpc = 9.2506e27/h cm. Taking h inside
    Omega_b h^2 leaves one factor of h, which cancels against c/H0 for the
    combination that appears here.
    """
    n_b0 = 1.123e-5 * omega_b_h2
    sigma_t = 6.6525e-25
    hubble_length_cm = 9.2506e27
    return n_b0 * sigma_t * hubble_length_cm


def diffusion_scale(
    history: RecombinationHistory, *, r_of_eta: np.ndarray | None = None
):
    """k_D(eta) from (dif-damp), by the integral it implies.

    (dif-damp) prints the damping *rate*

        gamma ~= k^2 (1/kappa') / 6 * [R^2 + 4/5 (1+R)] / (1+R)^2,

    and identifies it with k^2/k_D^2. The scale itself is the accumulated
    integral of that rate, which is the Hu & Sugiyama form the equation cites:

        k_D^{-2}(eta) = Int d(eta) 1/(6 kappa') [R^2 + 4/5 (1+R)]/(1+R)^2.

    Returned as a callable in eta so that (178) and (179) can evaluate
    exp[-(k/k_D)^2] at the epoch they are being integrated over, rather than at a
    single stipulated value.
    """
    eta = history.eta
    r = np.zeros_like(eta) if r_of_eta is None else np.asarray(r_of_eta, dtype=float)
    integrand = (
        1.0
        / (6.0 * np.clip(history.kappa_prime, 1e-30, None))
        * (r**2 + 0.8 * (1.0 + r))
        / (1.0 + r) ** 2
    )
    accumulated = np.concatenate(([0.0], cumulative_trapezoid(integrand, eta)))

    # Spline the *accumulated* quantity, which is smooth and monotone, and take
    # the reciprocal square root afterwards. Splining k_D directly fails: near
    # the start the accumulation is ~0, k_D diverges, and a cubic through those
    # values oscillates wildly over the whole early range.
    inverse_square = CubicSpline(eta, accumulated)

    def k_d(at: np.ndarray | float) -> np.ndarray:
        value = np.clip(inverse_square(np.asarray(at, dtype=float)), 1e-30, None)
        return 1.0 / np.sqrt(value)

    return k_d
