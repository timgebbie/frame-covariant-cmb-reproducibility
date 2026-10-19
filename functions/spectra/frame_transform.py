r"""Changing the frame, numerically — the frame specialisation made real.

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

The last two are the standard Paper 1 Sec. VI A sets: *any frame dependence
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

which is **exactly** `cdm_frame_velocity_equation`. The photon dipole in the
heavily-loaded limit obeys the geodesic Euler equation, as it must when the
baryons dominate the inertia and the pair falls freely. So `tau_1` and $v_B$
carry the same normalisation as $v$, and both shift by $-v$. `tests/` asserts
the limit rather than leaving it as a remark.

---

**The CDM frame needs no numerical derivative, and that is the point of
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

__all__ = ["FrameShift", "cdm_frame_shift", "to_frame"]


@dataclass(frozen=True)
class FrameShift:
    r"""A first-order change of frame $u^a\to u^a+v^a$ at one wavenumber.

    `v` and `v_prime` are the scalar mode amplitudes of $v_a$ and $v_a'$ on the
    conformal-time grid. Both are carried explicitly: `v_prime` is **not**
    recovered by differentiating `v`, because for the CDM frame it is known
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

    def dipole_shift(self) -> np.ndarray:
        r"""$-v/k$ — what $\tilde\tau_1$ and $\tilde v_B$ shift by. **Finding T-27.**

        *Annals II* **(43)** (**n-t4**, cited in this bundle as GDE99 Eq. (37)) is
        $\tilde\tau_a=\tau_a-v^N_a$, and this bundle wrote that as `tau_1 - v`. It is wrong by $k_{\rm com}$, because `v` is a
        **velocity** amplitude --- it is the $v$ of $v'+\mathcal Hv=-k\Phi_A$
        and of $\sigma=-k_{\rm phys}v$ --- while $\tilde\tau_1$ is the dipole in
        the *covariant normalisation*, $\tilde\tau_1=\tilde v_B=v_B/k$, which is
        the normalisation (109) needs to read $-\tilde C_1=(\delta\tilde
        T+\Phi_A)+\kappa'\tilde v_B$.

        **`temperature_shift` had it right and that is how this was found.** The
        monopole carries exactly the same $1/k$, for exactly the same reason: a
        scalar amplitude is $1/k_{\rm phys}$ times its gradient's, so
        $\mathcal D_a\ln T\to\mathcal D_a\ln T-Hv_a$ becomes $\delta T\to\delta
        T-\mathcal Hv/k$. Two rank-one objects in one dataclass, one divided by
        $k$ and one not.

        The symptom was visible without any of that reasoning: at $k=300$ the
        old rule shifted a dipole of $1.1$ by $200$ --- a *first-order* frame
        change 186 times the quantity it corrects. Divided by $k$ it is $0.6$,
        and $|v/k|/|\tilde\tau_1|$ stays between $0.2$ and $1.1$ across the
        whole $k$ range instead of growing like $k$.

        **This is why T-14 must be re-measured**, not merely re-run: T-14
        concluded the transfer function is not frame-invariant under
        (177)--(179), and it concluded that from a frame change that was too
        large by $k_{\rm com}$ --- a factor of 300 at the top of the grid.
        """
        return -np.asarray(self.v, dtype=float) / self.k_com

    def velocity_shift(self) -> np.ndarray:
        r"""$-v$ --- what an **un-reduced** dipole shifts by. **Finding T-66.**

        `dipole_shift` above is right, and so is the reasoning for it: a
        *reduced* dipole $\tilde v_B=v_B/k$ shifts by $-v/k$. What was missing
        is that `solve_acoustic` does not return a reduced dipole. It
        integrates (152)/(153) with $k$ on both source terms, so its $\tau_1$
        is a **velocity** amplitude --- and the heavily-loaded limit
        $\tau_1'+\mathcal H\tau_1=-k\Phi_A$ is *identical* to
        `cdm_frame_velocity_equation` for $v$, which is the argument this
        module's own header makes and then does not act on.

        So (37) applied to that object is $-v$, and the reduction to
        $\tilde v_B$ comes afterwards. **Both readings in the record are right
        about different objects**: P1-T \S3.2's *"the boost is $-v$"* (of
        $\tau_1$) and the external review's *"$-v/k$ is the correct boost for
        the reduced dipole"* (of $\tilde v_B$). The released code applied the
        **reduced** boost to the **un-reduced** quantity, which is one power of
        $k_{\rm com}$ --- 300 at the top of the grid.
        """
        return -np.asarray(self.v, dtype=float)


def cdm_frame_shift(
    eta: np.ndarray,
    phi_a: np.ndarray,
    k_com: float,
    *,
    background: Background,
) -> FrameShift:
    r"""The shift from the Newtonian frame to the CDM frame.

    Solves $v'+\mathcal Hv=-k\Phi_A$ — decision **S8a**'s CDM frame,
    which for pressureless geodesic cold dark matter is the frame in which
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

    return FrameShift(
        eta=eta, v=v, v_prime=v_prime, k_com=float(k_com),
        conformal_H=aH, target="cdm",
    )


def to_frame(
    history: PerturbationHistory,
    shift: FrameShift,
) -> PerturbationHistory:
    r"""Apply a frame shift to a history, returning the history in the new frame.

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
        # **T-66**: `tau_1` is velocity-normalised and takes `-v`; `v_b` is the
        # reduced $\tilde v_B$ and takes `-v/k`. Two rank-one objects in one
        # dataclass, differently normalised -- which is what
        # `dipole_shift`'s own docstring says of `temperature_shift`, one
        # field too early.
        tau_1=np.asarray(history.tau_1, dtype=float) + shift.velocity_shift(),
        v_b=np.asarray(history.v_b, dtype=float) + shift.dipole_shift(),
        frame=shift.target,
    )
