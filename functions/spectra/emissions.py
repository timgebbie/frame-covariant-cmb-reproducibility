"""Quantities emitted for Paper 1's floats, on the solver's own grid.

**Floats are named by content, never by number.** P1-T's specification records
that the printed numbers moved under them --- `fig:efficiency` prints as Fig. 2
where the work order said Fig. 5, and `fig:bulk` likewise --- so a handover keyed
to a number would have gone to the wrong box. These emissions are keyed to
`fig:efficiency` and `fig:bulk` and to the physics, and are unaffected by
renumbering.

**STATUS: active. Convention imported: none — every quantity is taken from the
objects this bundle already integrates.**

P1-T's work order of 2026-10-06 asks for two emissions from v1.0.0, so that the
code hands over what the paper needs instead of computing it and discarding it.
The governing rule is the same in both cases and is the reason this module
exists rather than a note saying "recompute it from the parameters":

> if it is re-derived afterwards the figure compares two different cosmologies
> and the agreement means nothing.

So nothing here recomputes anything. Each function takes the live object --- the
`Background` that was integrated, the `RecombinationHistory` that was built ---
and reads the quantity off it.

**Paper 1, `fig:efficiency`** (needs v1.0.0). The lensing efficiency
$(\\chi_*-\\chi)/\\chi_*$ shown to emerge from the lever arm of the direction
derivative rather than being inserted. Emitted: $\\chi(\\eta)$ on the solver's own
time grid, and $\\chi_*$ at last scattering. `lensing_efficiency` is provided so
the *inserted* kernel is built from the same $\\chi_*$ as the emergent one; using
a separately computed $\\chi_*$ is the failure mode the work order names.

**Paper 1, `fig:bulk`** (its second half needs v1.5.0). The $O(\\ell)$ aberration
operator is large all along the ray yet contributes only at the endpoints.
Emitted from v1.0.0: the line-of-sight field --- the integrand of (176) and its
running integral --- at a stated $\\ell$ and $k$, so that v1.5.0 can evaluate its
$O(\\varepsilon^2\\ell)$ source on that field at each $\\chi$. **The running
integral is the point**: P1-T's acceptance is that it returns to the endpoint
value, and that the residual bulk fraction is stated. This module emits the
curve; it does not judge it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from functions.background.flrw import Background
from functions.spectra.bessel_table import BesselTable
from functions.spectra.decoupling import RecombinationHistory

__all__ = [
    "DistanceEmission",
    "RayEmission",
    "comoving_distance",
    "lensing_efficiency",
    "line_of_sight_field",
]


@dataclass(frozen=True)
class DistanceEmission:
    """chi(eta) on the solver's grid, and chi_* --- Paper 1 `fig:efficiency`."""

    eta: np.ndarray
    chi: np.ndarray
    chi_star: float
    eta_star: float
    model: str

    def to_csv(self, path) -> None:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"# model={self.model} chi_star={self.chi_star:.12e} "
                     f"eta_star={self.eta_star:.12e}\n")
            fh.write("eta,chi\n")
            for e, c in zip(self.eta, self.chi):
                fh.write(f"{e:.12e},{c:.12e}\n")


def comoving_distance(
    background: Background, recombination: RecombinationHistory, eta: np.ndarray | None = None
) -> DistanceEmission:
    """chi(eta) = eta_0 - eta from the background that was integrated.

    `eta` defaults to the recombination history's own grid, which is the
    solver's grid. $\\chi_*$ is taken at the **visibility peak**, not at
    $\\kappa=1$: the peak is where photons actually last scatter and it is what
    (176)'s primary term is evaluated at, so a lensing kernel built on anything
    else is built on a different last-scattering surface from the spectrum.
    """
    grid = recombination.eta if eta is None else np.asarray(eta, dtype=float)
    eta_star = recombination.eta_star
    return DistanceEmission(
        eta=grid,
        chi=background.eta_0 - grid,
        chi_star=float(background.eta_0 - eta_star),
        eta_star=float(eta_star),
        model=f"Om_m={background.omega_m} Om_L={background.omega_lambda} "
              f"Om_r={background.omega_r} h0={background.h0}",
    )


def lensing_efficiency(emission: DistanceEmission) -> np.ndarray:
    """(chi_* - chi)/chi_*, built from the **emitted** chi_*, not a fresh one.

    Returned for $\\chi\\le\\chi_*$ and zero beyond, so that the endpoints are
    exactly 1 at the observer and exactly 0 at last scattering --- P1-T's
    acceptance is that the emergent and inserted kernels coincide *including*
    both endpoints, and an inserted kernel that misses them by rounding would
    make that test meaningless.
    """
    chi = np.asarray(emission.chi, dtype=float)
    out = (emission.chi_star - chi) / emission.chi_star
    return np.where(chi <= emission.chi_star, out, 0.0)


@dataclass(frozen=True)
class RayEmission:
    """The line-of-sight field along one ray --- Paper 1 `fig:bulk`."""

    ell: int
    k_com: float
    eta: np.ndarray
    chi: np.ndarray
    integrand: np.ndarray       # S(eta) j_l(k chi), the local contribution
    running: np.ndarray         # its integral from eta_* outward
    endpoint: float

    @property
    def bulk_fraction(self) -> float:
        """How much of the running integral lives away from the endpoints.

        P1-T's acceptance for `fig:bulk` is that the local operator does not fall off
        through the bulk while the running integral still returns to the endpoint
        value. This is the number that statement is made with. It is **reported,
        not asserted**: if the bulk does not cancel that is a finding, and this
        module must not hide it behind a tolerance.
        """
        if self.endpoint == 0.0:
            return float("nan")
        interior = slice(len(self.running) // 10, -len(self.running) // 10)
        return float(np.max(np.abs(self.running[interior] - self.endpoint)) / abs(self.endpoint))

    @property
    def tau_mode(self) -> np.ndarray:
        """$\\tau_\\ell(\\chi)$ — the **mode** coefficient, accumulated along the ray.

        (176) returns $\\alpha_\\ell^{-1}\\tau_\\ell$, which is what `running`
        holds, so the mode coefficient is $\\alpha_\\ell$ times it.
        """
        from functions.harmonics.weights import alpha

        return float(alpha(self.ell)) * self.running

    @property
    def tau_multipole(self) -> np.ndarray:
        """$\\tau_{A_\\ell}(\\chi)$ — the **multipole** coefficient's magnitude.

        $\\beta_\\ell=O^{A_\\ell}O_{A_\\ell}$ is the contraction of the PSTF basis
        with itself, Gebbie & Ellis (2000) Eq. (24), so (187)'s
        $\\langle\\tau_{A_\\ell}\\tau^{A_\\ell}\\rangle=\\beta_\\ell\\langle\\tau_\\ell^2\\rangle$
        gives $|\\tau_{A_\\ell}|=\\sqrt{\\beta_\\ell}\\,\\tau_\\ell$ along one ray.

        **Both are emitted and neither is called "tau".** *Annals II* p. 366
        keeps mode and multipole apart because they are not interchangeable —
        the multipole mean square holds for general geometries where the mode
        one holds only for almost-Robertson--Walker — and silently handing over
        one labelled as the other is how a factor leaks into a paper.
        """
        from functions.harmonics.weights import beta

        return float(beta(self.ell)) ** 0.5 * self.tau_mode

    def to_csv(self, path) -> None:
        """Written multipole-first, because that is what Paper 1 asked for.

        The mode column and the raw integrand stay beside it so the conversion
        is auditable rather than trusted, and the header states the relation.
        """
        from functions.harmonics.weights import alpha, beta

        a, b = float(alpha(self.ell)), float(beta(self.ell))
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(f"# ell={self.ell} k_com={self.k_com:.12e} "
                     f"endpoint={self.endpoint:.12e} bulk_fraction={self.bulk_fraction:.6e}\n")
            fh.write(f"# alpha_l={a:.12e}  beta_l={b:.12e}\n")
            fh.write("# running = the integral of (176) accumulated from eta_* outward,\n")
            fh.write("#           which is alpha_l^-1 tau_l, the normalisation (176) returns\n")
            fh.write("# tau_l    = alpha_l * running            [MODE coefficient]\n")
            fh.write("# tau_Al   = sqrt(beta_l) * tau_l         [MULTIPOLE coefficient, (187)]\n")
            fh.write("# The two are NOT interchangeable; see Annals II p. 366.\n")
            fh.write("chi,tau_Al,tau_l,integrand,running,eta\n")
            for c, tA, tl, i, r, e in zip(self.chi, self.tau_multipole, self.tau_mode,
                                          self.integrand, self.running, self.eta):
                fh.write(f"{c:.12e},{tA:.12e},{tl:.12e},{i:.12e},{r:.12e},{e:.12e}\n")


def line_of_sight_field(
    ell: int,
    k_com: float,
    *,
    eta: np.ndarray,
    source: np.ndarray,
    eta_0: float,
    table: BesselTable | None = None,
) -> RayEmission:
    """The integrand of (176) and its running integral, along one ray.

    This is what (176) computes and then throws away, keeping only the endpoint.
    v1.5.0 needs the field itself, to evaluate its $O(\\varepsilon^2\\ell)$ source
    on it at each $\\chi$ --- hence emitting it now rather than rebuilding the
    integration later from a different grid.
    """
    from scipy.integrate import cumulative_trapezoid
    from scipy.special import spherical_jn

    eta = np.asarray(eta, dtype=float)
    chi = eta_0 - eta
    x = k_com * chi
    j = table(ell, x) if table is not None else spherical_jn(int(ell), x)
    integrand = np.asarray(source, dtype=float) * j
    running = np.concatenate(([0.0], cumulative_trapezoid(integrand, eta)))
    return RayEmission(
        ell=int(ell), k_com=float(k_com), eta=eta, chi=chi,
        integrand=integrand, running=running, endpoint=float(running[-1]),
    )
