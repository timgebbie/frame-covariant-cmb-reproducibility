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
    "Recombination",
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


class Recombination(Enum):
    """Which ionisation history to build the optical depth from.

    `SAHA` is equilibrium only. It places last scattering within a few percent
    in redshift, which is all v1.0.0 needed, and it has **no freeze-out**: it
    drives $x_e$ to absurd values (``1e-53`` by $z=200$) where the real universe
    holds a residual plateau.

    `PEEBLES` is the effective three-level atom of
    `functions.spectra.peebles` --- v1.1.0's deliverable, and what criterion
    **5b** is blocked on (decision S18). The difference is not cosmetic:

    Measured through this class at `z_max=2400`, `n_eta=6000`, on a
    $\\Omega_m=0.315$, $\\Omega_\\Lambda=0.685$, $\\Omega_r=9.2\\times10^{-5}$
    background:

    | | $z$ of the visibility peak | FWHM in $z$ |
    |---|---|---|
    | `SAHA` | $\\simeq1300$ | $\\simeq120$ |
    | `PEEBLES` | $\\simeq1107$ | $\\simeq167$ |
    | standard | 1080--1100 | 190--200 |

    Saha puts last scattering roughly 200 in redshift too early and makes the
    visibility **about 40% too narrow**, and the visibility width is precisely
    what fixes the Silk damping envelope.

    **The widths above are grid-dependent and are quoted with their settings
    for that reason.** `tests/test_peebles.py` asserts *bounds* and the
    *relation* between the two rather than these numbers, because a hand-typed
    figure in a docstring is a staleness generator — which is the mistake the
    README's "230 tests pass" made and the reason it is no longer there.

    **`PEEBLES` is the default from v1.1.0** --- decision **S22**, taken by the
    PI on 2026-10-10 with the before-and-after above in view. It was *not* the
    default on the day the module landed: the roadmap requires Peebles to be
    "checkable on its own against the standard ionisation history **before
    anything is built on it**", so it shipped behind this enum, was checked
    standalone in `tests/test_peebles.py`, and was promoted afterwards. Flipping
    a default regenerates every released number, and that is a decision, not a
    side effect of adding a module.

    `SAHA` is kept rather than deleted. It is the v1.0.0 result, so it is what
    makes the change *measurable* instead of merely asserted, and a known-worse
    alternative that must change the answer is evidence of the kind this project
    keeps (decision S12).
    """

    SAHA = "saha"
    PEEBLES = "peebles"


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
        recombination: "Recombination" = None,  # type: ignore[assignment]
        h: float = 0.674,
    ) -> "RecombinationHistory":
        # T-108: under "released" the Peebles ODE runs at h = 0.674 on every
        # background, which is what every shipped number was computed with.
        h_used = _RELEASED_H if RECOMBINATION_H == "released" else float(h)
        eta_min = background.eta_at_redshift(z_max)
        eta = np.linspace(eta_min, background.eta_0, n_eta)
        a = background.a_of_eta(eta)
        z = 1.0 / np.clip(a, 1e-12, None) - 1.0

        if recombination is None:
            recombination = Recombination.PEEBLES

        if recombination is Recombination.SAHA:
            x_e = saha_ionisation(z, omega_b_h2=omega_b_h2)
        else:
            # **Imported here rather than at module scope, deliberately.**
            # `peebles` imports `saha_ionisation` from this module for its own
            # initial condition, so a top-level import would be circular. The
            # dependency is genuinely one-directional in meaning --- Peebles
            # starts from Saha, not the other way round --- and the local import
            # is the honest expression of that rather than a workaround.
            from functions.spectra.peebles import peebles_ionisation

            z_hi = min(float(np.max(z)), 2000.0)
            solution = peebles_ionisation(
                background, z_start=z_hi, z_end=max(float(np.min(z)), 10.0),
                omega_b_h2=omega_b_h2, h=h_used,
            )
            # Above the integration's start the gas is still in equilibrium by
            # construction (see `peebles_ionisation`), so Saha is the solution
            # there and is used rather than extrapolating the ODE backwards.
            x_e = np.where(
                z <= z_hi,
                solution.at(np.clip(z, solution.z.min(), z_hi)),
                saha_ionisation(z, omega_b_h2=omega_b_h2),
            )

        # kappa' = a n_e sigma_T, in units where the normalisation is absorbed
        # into `thomson_scale`: only the shape and the location of the visibility
        # peak matter for the tests, and the scale is fixed by requiring
        # kappa(eta_0) = 0 with kappa increasing backwards in time.
        thomson_scale = _thomson_scale(omega_b_h2, h_used)
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


#: **The $h$ convention in recombination --- `"released"` or `"corrected"`.
#: Finding T-108, raised by the PI 2026-10-21.**
#:
#: `"released"` reproduces the shipped numbers exactly: $h=0.674$ in the
#: Peebles ODE **whatever the background**, and no $1/h$ in the Thomson scale.
#: `"corrected"` uses the caller's $h$ in both places.
#:
#: **The two defects land together because the first needs the second.** The
#: surviving $1/h$ cannot be applied without knowing $h$ per background, and
#: knowing $h$ per background *is* the second defect. M11a is satisfied by the
#: arithmetic rather than by choice.
#:
#: **It defaults to `"released"` and moves nothing.** What it does to $z_*$,
#: $r_s$, $\ell_A$ and the visibility width is measured by **D20** before the
#: default moves --- T-107 is the standing reason.
RECOMBINATION_H: str = "corrected"

#: The $h$ every released run has silently used, on all three backgrounds.
_RELEASED_H: float = 0.674


def _thomson_scale(omega_b_h2: float, h: float | None = None) -> float:
    r"""$\sigma_Tn_{b,0}c/H_0$, dimensionless, for $a_0=1$.

    $n_{b,0}=1.123\times10^{-5}\,\Omega_bh^2$ cm$^{-3}$,
    $\sigma_T=6.6525\times10^{-25}$ cm$^2$, and the Hubble length
    $c/H_0=2997.9/h$ Mpc $=9.2506\times10^{27}/h$ cm.

    **Finding T-108.** This docstring used to end: *"Taking h inside
    Omega_b h^2 leaves one factor of h, **which cancels** against c/H0."* **It
    does not cancel.** $n_{b,0}c/H_0\propto\Omega_bh^2\cdot h^{-1}
    =\Omega_bh$: one power of $h$ **survives**, and the released code dropped
    it by using $c/H_0$ at $h=1$ --- the function did not even take an `h`
    argument, so it could not have applied the factor. The released rate is
    therefore **low by $1/h$**: 1.48 on `PLANCK_MODEL`, 2.00 on
    Einstein--de~Sitter, 1.43 on $\Lambda$CDM at $h=0.7$.

    The statement *"which cancels"* was read as a derivation for four
    releases. It is **T-103's shape in a second file**: a docstring that
    states the rule and then breaks it, with the code implementing the
    docstring rather than the arithmetic.
    """
    n_b0 = 1.123e-5 * omega_b_h2
    sigma_t = 6.6525e-25
    hubble_length_cm = 9.2506e27          # c/H0 at h = 1
    scale = n_b0 * sigma_t * hubble_length_cm
    if RECOMBINATION_H == "corrected":
        if h is None:
            raise ValueError(
                "the corrected Thomson scale needs h: the surviving 1/h in "
                "c/H0 cannot be applied without it, which is why the released "
                "signature taking no h was not merely incomplete but "
                "unable to be right. T-108.")
        scale /= float(h)
    return scale


#: **(dif-damp) and (dif-damp-correct), in *Annals II*'s own parameter.**
#:
#: The paper prints the tight-coupling damping rate at **(dif-damp)**,
#:
#: $$\gamma \approx k^2\Big(\tfrac{\kappa'^{-1}}{6}\Big)
#:   \Big[\tfrac{R^2+\frac45(1+R)}{(1+R)^2}\Big],$$
#:
#: and then says it *"can be easily corrected to include the effect of
#: anisotropic scattering (which breaks the tight-coupling approximation) and
#: polarization... We follow the approach of Kaiser"*, giving
#: **(dif-damp-correct)**
#:
#: $$\gamma^* \approx k^2\Big(\tfrac{\kappa'^{-1}}{6}\Big)
#:   \Big[\tfrac{R^2+\frac45 f_2^{-1}(1+R)}{(1+R)^2}\Big],$$
#:
#: *"where, first, for the anisotropic effect, $f_2=\frac{9}{10}$, and second,
#: to compensate for the polarization, $f_2=\frac34$."*
#:
#: **So the coefficient is $\frac45 f_2^{-1}$ and the paper supplies the
#: values.** $f_2=1$ is (dif-damp) itself; $f_2=9/10$ gives $8/9$, Hu \&
#: Sugiyama's unpolarised coefficient; $f_2=3/4$ gives **16/15**, the polarised
#: one. All three are *Annals II*'s --- finding **T-43**, which corrects S31's
#: belief that 16/15 was a departure from the paper.
F2_TIGHT_COUPLING = 1.0
F2_ANISOTROPIC = 9.0 / 10.0
F2_POLARISED = 3.0 / 4.0

#: Which $f_2$ the bundle uses by default. **(dif-damp-correct) is the form the
#: paper itself carries downstream**: \S*The Visibility Function* defines
#: $\mathcal D(\eta_0,k)$ with *"diffusion damping, which will be derived from
#: the coupled baryon-photon equations in (\ref{dif-damp-correct})"* --- the
#: corrected equation, not the tight-coupling one. Changing this default is a
#: decision, so it is named here rather than written into a call site.
#: **The bundle's $f_2$, and it is the corrected one.** *The PI, 2026-10-15:
#: "f_2 the default should move to the corrected form."*
#:
#: (dif-damp-correct) is the form **the paper itself carries downstream**:
#: \S*The Visibility Function* defines the damping envelope with *"diffusion
#: damping, which will be derived from the coupled baryon-photon equations in
#: (\ref{dif-damp-correct})"* --- the corrected equation, cited by label.
#:
#: **The two $f_2$ are alternatives, not a composition**, which the printed
#: sentence alone does not settle but the numbers do: $\frac45(9/10)^{-1}=8/9$
#: is the standard unpolarised quadrupole coefficient and
#: $\frac45(3/4)^{-1}=16/15$ the standard polarised one, both measured from the
#: same baseline by Kaiser and by Hu \& Sugiyama. Composing them would give
#: $\frac45(27/40)^{-1}=32/27$, which is not a value anyone reports. So
#: $f_2=3/4$ is the fully corrected figure and carries both effects.
#: Finding **T-43**, decision **S31a**.
F2_DEFAULT = F2_POLARISED


def quadrupole_from_f2(f_2: float) -> float:
    r"""$\frac45 f_2^{-1}$, the coefficient (dif-damp-correct) prints."""
    if f_2 <= 0.0:
        raise ValueError(f"f_2 must be positive; got {f_2!r}")
    return 0.8 / float(f_2)


def diffusion_scale(
    history: RecombinationHistory,
    *,
    r_of_eta: np.ndarray | None = None,
    f_2: float = F2_DEFAULT,
):
    """k_D(eta) from (dif-damp), by the integral it implies.

    `f_2` is (dif-damp-correct)'s correction factor; the coefficient is
    $\\frac45 f_2^{-1}$. It defaults to `F2_POLARISED`, the fully corrected
    value the paper carries downstream. `F2_TIGHT_COUPLING` reproduces the
    uncorrected (dif-damp).

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
        * (r**2 + quadrupole_from_f2(f_2) * (1.0 + r))
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
