r"""Changing the threading, numerically — the frame specialisation made real.

Until v1.1.0 `PerturbationHistory.frame` was a **label**: the string
``"newtonian"`` sat on the dataclass and nothing in the bundle read it. This
module is what reads it. It turns the choice of $u^a$ from an annotation into a
calculation, which is what decision **S20** deferred to this release and what
F5 and F7 both need.

---

**The rules are not invented here.** Every one of them is derived in
`functions.frames`, symbolically and with its order in $\varepsilon$ tracked,
and each carries a source:

| object | under $\tilde u_a = u_a + v_a$ | from |
|---|---|---|
| $\mathrm D_a\ln T$ | $-Hv_a$ | moving projector, `boosted_temperature_gradient` |
| $A_a$ | $+\dot v_a + Hv_a$ | `boosted_acceleration` |
| $\sigma_{ab}$ | $+\mathrm D_{\langle a}v_{b\rangle}$ | `boosted_shear` |
| $\Phi_A,\ \Phi_H$ | both $+(v'+\mathcal Hv)/k$ | `harmonic_potential_shift` |
| $\Phi_A-\Phi_H$ | **invariant** | GDE99 Eq. (24) + Stewart–Walker |
| $\tau_a$ | $-v_a$ | GDE99 Eq. (37) |
| $\tau_{A_\ell},\ \ell\ge2$ | **invariant** | GDE99, below Eq. (35) |

The last two are the standard Paper 1 Sec. VI A sets: *any threading dependence
surviving at $\ell\ge2$ is an artefact of the reduction and not physics.*

---

**Why the dipole shifts with coefficient exactly one, checked rather than
assumed.** GDE99 Eq. (37) is $\tilde\tau_a=\tau_a-v_a$ for the covariant
dipole, and this bundle's `tau_1` is a *mode* coefficient — so the coefficient
only survives the conversion if `tau_1` is normalised like a velocity. It is,
and (152) says so: in the baryon-dominated limit $R\to\infty$, where
$R'/(1+R)\to\mathcal H$ because $R\propto a$,

$$\tau_1' = -\frac{R'}{1+R}\tau_1 - \frac{k}{1+R}\delta T - k\Phi_A
\;\longrightarrow\;
\tau_1' + \mathcal H\tau_1 = -k\Phi_A ,$$

which is **exactly** `energy_frame_velocity_equation`. The photon dipole in the
heavily-loaded limit obeys the geodesic Euler equation, as it must when the
baryons dominate the inertia and the pair falls freely. So `tau_1` and $v_B$
carry the same normalisation as $v$, and both shift by $-v$. `tests/` asserts
the limit rather than leaving it as a remark.

---

**The energy frame needs no numerical derivative, and that is the point of
defining it by $\tilde A_a=0$ rather than by a velocity someone supplies.**
Imposing it gives $v'+\mathcal Hv=-k\Phi_A$, so the quantity the potentials
shift by, $(v'+\mathcal Hv)/k$, is $-\Phi_A$ **exactly** — algebraically, with
no spline of $v$ anywhere. Hence $\tilde\Phi_A=0$ by construction and
$\tilde\Phi_H=\Phi_H-\Phi_A$, and the invariant $\Phi_A-\Phi_H$ is manifestly
preserved. A numerically differentiated $v$ would have put a discretisation
error into a quantity the formalism says is exact, and F5's residual would then
have measured the spline rather than the physics — which is finding **T-3**'s
lesson in a new place.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from functions.background.flrw import Background
from functions.spectra.sources import Frame, PerturbationHistory

__all__ = ["ThreadingShift", "energy_frame_shift", "to_frame"]


@dataclass(frozen=True)
class ThreadingShift:
    r"""A first-order change of threading $u^a\to u^a+v^a$ at one wavenumber.

    `v` and `v_prime` are the scalar mode amplitudes of $v_a$ and $v_a'$ on the
    conformal-time grid. Both are carried explicitly: `v_prime` is **not**
    recovered by differentiating `v`, because for the energy frame it is known
    in closed form from the defining condition, and a spline there would be a
    discretisation error inside an exact statement.
    """

    eta: np.ndarray
    v: np.ndarray
    v_prime: np.ndarray
    k_com: float
    conformal_H: np.ndarray
    target: Frame

    def potential_shift(self) -> np.ndarray:
        r"""$(v'+\mathcal Hv)/k$ — what **both** potentials shift by."""
        return (np.asarray(self.v_prime, dtype=float)
                + np.asarray(self.conformal_H, dtype=float)
                * np.asarray(self.v, dtype=float)) / self.k_com

    def temperature_shift(self) -> np.ndarray:
        r"""$-(\mathcal H/k)\,v$ — the moving projector acting on $\ln T$."""
        return -(np.asarray(self.conformal_H, dtype=float)
                 * np.asarray(self.v, dtype=float)) / self.k_com


def energy_frame_shift(
    eta: np.ndarray,
    phi_a: np.ndarray,
    k_com: float,
    *,
    background: Background,
) -> ThreadingShift:
    r"""The shift from the Newtonian threading to the energy ($q_a=0$) frame.

    Solves $v'+\mathcal Hv=-k\Phi_A$ — decision **S8**'s total-energy frame,
    which for pressureless geodesic cold dark matter is the threading in which
    the CDM is at rest, and Paper 1 Sec. VI C's $\tilde A_a=0$.

    **By quadrature, not by an ODE solver.** The integrating factor is $a$
    itself, since $(av)'=a(v'+\mathcal Hv)$, so

    $$a(\eta)\,v(\eta) = a(\eta_1)v(\eta_1) - k\int_{\eta_1}^{\eta} a\,\Phi_A\,
      \mathrm d\eta' ,$$

    one cumulative trapezoid rather than a stepper with its own error control.

    **The initial condition is the matter-domination attractor and is not
    load-bearing.** With $\mathcal H=2/\eta$ and $\Phi_A$ constant, $v=C\eta$
    gives $C+2C=-k\Phi_A$, so $v=-k\Phi_A\eta/3$. The homogeneous solution is
    $v\propto1/a$, which *decays*, so a wrong start is forgotten rather than
    propagated — `tests/` starts from zero instead and shows the two converge.
    """
    eta = np.asarray(eta, dtype=float)
    phi_a = np.asarray(phi_a, dtype=float)
    a = np.asarray(background.a_of_eta(eta), dtype=float)
    aH = np.asarray(background.aH_of_eta(eta), dtype=float)

    # the growing-mode attractor deep in matter domination
    v0 = -k_com * float(phi_a[0]) * float(eta[0]) / 3.0

    integrand = a * phi_a
    cumulative = np.concatenate(
        ([0.0], np.cumsum(0.5 * (integrand[1:] + integrand[:-1]) * np.diff(eta)))
    )
    v = (a[0] * v0 - k_com * cumulative) / a

    # **Exact, from the defining condition** --- never from a spline of v.
    v_prime = -aH * v - k_com * phi_a

    return ThreadingShift(
        eta=eta, v=v, v_prime=v_prime, k_com=float(k_com),
        conformal_H=aH, target="energy",
    )


def to_frame(
    history: PerturbationHistory,
    shift: ThreadingShift,
) -> PerturbationHistory:
    r"""Apply a threading shift to a history, returning the history in the new frame.

    Every field moves by the rule `functions.frames` derives for it, and the
    frame label moves with them — so a history can no longer *claim* a frame it
    was not transformed into, which is what the label used to do.

    The monopole is not touched. $\delta T$ moves because the **gradient** of
    $\ln T$ does, through the projector, which is a different statement from
    the monopole being frame-dependent; the mode amplitude carries that shift.
    """
    if history.frame == shift.target:
        raise ValueError(
            f"history is already in the {shift.target!r} frame; applying the "
            "shift again would double-count it"
        )
    if np.asarray(history.eta).shape != np.asarray(shift.eta).shape:
        raise ValueError("the shift and the history are on different grids")

    potential = shift.potential_shift()

    return replace(
        history,
        delta_T=np.asarray(history.delta_T, dtype=float) + shift.temperature_shift(),
        phi_a=np.asarray(history.phi_a, dtype=float) + potential,
        phi_h=np.asarray(history.phi_h, dtype=float) + potential,
        tau_1=np.asarray(history.tau_1, dtype=float) - np.asarray(shift.v, dtype=float),
        v_b=np.asarray(history.v_b, dtype=float) - np.asarray(shift.v, dtype=float),
        frame=shift.target,
    )
