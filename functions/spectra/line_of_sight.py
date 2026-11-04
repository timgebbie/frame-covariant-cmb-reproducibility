r"""The line of sight at one $k$: $\int W\{C_0K+C_1K'+C_2K''\}\,\mathrm d\eta$.

$K=j_\ell(k(\eta_0-\eta))$, with primes on $K$ meaning $\mathrm d/\mathrm d\eta$,
so $K'=-k\,j_\ell'$ and $K''=k^2j_\ell''$. $W=e^{-\kappa}$ and $W'=\mathcal V$.
$C_1=C_1^{\rm grav}+C_1^{\rm scatt}$ with $C_1^{\rm scatt}=-\kappa'\hat v_B$, so
$WC_1^{\rm scatt}=-\mathcal V\hat v_B$ exactly, and **no coefficient holding
$\kappa'$ is differentiated anywhere in this module.**

Three evaluations of the one integral.

**`three_slots`** --- the supplement's eq:assembly-invariant. With
$G\equiv C_1^{\rm grav}-C_2'$,

    W{C_0 K + C_1 K' + C_2 K''} = W (C_0 - G') K - V G K - V (vhat_B + C_2) K'
                                  + d/d(eta) [ W (G K + C_2 K') ] ,

and the total derivative projects onto $\ell\le1$ alone. Each rank-two term
is integrated by parts once, onto the slot its rank-one partner occupies; the
scattering half of $C_1$ never:

| slot | source | weight | kernel |
|---|---|---|---|
| Sachs--Wolfe | $-G$ | $\mathcal V$ | $K$ |
| Doppler | $\hat v_B+C_2$ | $\mathcal V$ | $-K'=k\,j_\ell'$ |
| integrated | $C_0-G'$ | $W$ | $K$ |

A first-order change of frame moves only $\ell\le1$ exactly when
$\Delta C_0=0$, $\Delta C_1^{\rm scatt}=\kappa'\Delta C_2$ and
$\Delta C_1^{\rm grav}=\Delta C_2'$, that is, when $C_0$, $\hat v_B+C_2$ and
$G$ are each invariant; then every slot is invariant **at every** $\eta$,
whatever the width of $\mathcal V$. With the source equation's signs and $C_1^{\rm grav}{}'$ from the
dynamical relation, the integrated slot's source in a shear-free frame is
$-(\Phi_A'-\Phi_H')$: the photon monopole and dipole are read only where
$\mathcal V\neq0$, and only the potentials accumulate along the path.

**`slots`** --- the five-term assembly, rank two integrated by parts once, so
$-\int WC_2'K'$ stands as its own term; and **`direct`**, nothing integrated
by parts. With the same $C_1^{\rm grav}{}'$ the five slots and the three slots
are one identity; `direct` equals them only when $C_1^{\rm grav}{}'$ is the
$\eta$-derivative of the stored $C_1^{\rm grav}$. Where it comes from the
dynamical relation instead, the difference is
$\int W(C_1^{\rm grav}{}'_{\rm rel}-C_1^{\rm grav}{}'_{\rm stored})K$: how far
the stored photon moments depart from their own evolution after last
scattering, along the whole path.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import spherical_jn

__all__ = ["Kernels", "kernel_set", "Sources", "ThreeSlots", "three_slots",
           "Slots", "slots"]


@dataclass(frozen=True)
class Kernels:
    r"""$j_\ell$, $j_\ell'$ and $j_\ell''$ at $x=k(\eta_0-\eta)$, one row per
    multipole. They depend on $k$, $\ell$ and the grid, **not on the frame**,
    so one set serves both frames and every assembly at a mode."""

    ell: np.ndarray
    k_com: float
    eta: np.ndarray
    j: np.ndarray       # (n_ell, n_eta)
    jd: np.ndarray      # j_l'
    jdd: np.ndarray     # j_l''


def kernel_set(ells: np.ndarray, k_com: float, *, eta: np.ndarray,
               eta_0: float, table=None) -> Kernels:
    r"""$j_\ell,j_\ell',j_\ell''$ for each of `ells` on the grid `eta`.

    $j_\ell'$ from the recurrence $[\ell j_{\ell-1}-(\ell+1)j_{\ell+1}]/(2\ell+1)$
    and $j_\ell''$ from Bessel's equation, $j''=-(2/x)j'-(1-\ell(\ell+1)/x^2)j$,
    so no derivative is taken of a table; at $x\to0$, $j_2''(0)=2/15$ and
    $j_\ell''(0)=0$ for $\ell\ge3$. `table`, when given, is a `BesselTable`
    carrying $\ell-1,\ell,\ell+1$; otherwise the functions are evaluated
    directly. The assemblies are exact for $\ell\ge2$, where the end-point terms
    at $\eta_0$ vanish.
    """
    ells = np.asarray(ells, dtype=int)
    if ells.size == 0 or ells.min() < 2:
        raise ValueError("the assemblies are exact for ell >= 2 only: the "
                         "end-point terms at eta_0 carry j_l(0) and j_l'(0)")
    eta = np.asarray(eta, dtype=float)
    k = float(k_com)
    x = np.maximum(k * (float(eta_0) - eta), 0.0)
    j = np.empty((ells.size, x.size))
    jd, jdd = np.empty_like(j), np.empty_like(j)
    small = x < 1e-6
    big = ~small
    for i, ell in enumerate(ells):
        l = int(ell)
        if table is None:
            jl, jm, jp = (spherical_jn(l, x), spherical_jn(l - 1, x),
                          spherical_jn(l + 1, x))
        else:
            jl, jm, jp = table(l, x), table(l - 1, x), table(l + 1, x)
        j[i] = jl
        jd[i] = (l * jm - (l + 1) * jp) / (2 * l + 1)
        jdd[i, big] = (-(2.0 / x[big]) * jd[i, big]
                       - (1.0 - l * (l + 1) / x[big] ** 2) * jl[big])
        jdd[i, small] = 2.0 / 15.0 if l == 2 else 0.0
    return Kernels(ell=ells, k_com=k, eta=eta, j=j, jd=jd, jdd=jdd)


@dataclass(frozen=True)
class Sources:
    r"""One frame's coefficients and weights on the $\eta$ grid.

    `c1_grav_prime` is supplied by the caller: from the dynamical relation for
    the physics (T-23), or as the derivative of the stored `c1_grav` when an
    identity is being checked.
    """

    eta: np.ndarray
    opacity: np.ndarray        # W
    visibility: np.ndarray     # V
    c0: np.ndarray
    c1_grav: np.ndarray
    c1_grav_prime: np.ndarray
    v_hat_b: np.ndarray
    c2: np.ndarray
    c2_prime: np.ndarray
    c2_second: np.ndarray

    def __post_init__(self):
        n = np.shape(self.eta)
        for name in ("opacity", "visibility", "c0", "c1_grav", "c1_grav_prime",
                     "v_hat_b", "c2", "c2_prime", "c2_second"):
            if np.shape(getattr(self, name)) != n:
                raise ValueError(f"{name} must share the eta grid")


@dataclass(frozen=True)
class ThreeSlots:
    r"""`three_slots`, slot by slot, over `ell`. Undamped: `transfer` applies
    the diffusion factor to the two scattering slots, which carry the
    photon--baryon fluid at last scattering, and not to the integrated one."""

    ell: np.ndarray
    k_com: float
    sachs_wolfe: np.ndarray   # - Int V G K
    doppler: np.ndarray       # - Int V (vhat_B + C2) K'
    integrated: np.ndarray    #   Int W (C0 - G') K
    #: `(3, n_ell, n_slices)`: each slot integrated from the start of the grid
    #: up to each requested $\eta$, or `None` when no slices were asked for.
    partial: np.ndarray | None = None

    def transfer(self, damping: float = 1.0) -> np.ndarray:
        return float(damping) * (self.sachs_wolfe + self.doppler) + self.integrated

    def partial_transfer(self, damping: float = 1.0) -> np.ndarray:
        """`transfer` laid down by each slice: `(n_ell, n_slices)`."""
        if self.partial is None:
            raise ValueError("no eta slices were requested")
        sw, dop, isw = self.partial
        return float(damping) * (sw + dop) + isw


def three_slots(kernels: Kernels, s: Sources,
                eta_slices: np.ndarray | None = None) -> ThreeSlots:
    r"""The three slots at the kernels' $k$, with $G=C_1^{\rm grav}-C_2'$.

    `eta_slices` asks also for each slot accumulated up to each slice: the
    same trapezoid, summed cumulatively, so the last slice at $\eta_0$ is the
    full integral and not a second definition of it.
    """
    if s.eta.shape != kernels.eta.shape:
        raise ValueError("sources and kernels must share the eta grid")
    eta, k = kernels.eta, kernels.k_com
    V, W = s.visibility, s.opacity
    g = s.c1_grav - s.c2_prime
    g_prime = s.c1_grav_prime - s.c2_second
    integrands = (-kernels.j * (V * g),
                  k * kernels.jd * (V * (s.v_hat_b + s.c2)),
                  kernels.j * (W * (s.c0 - g_prime)))
    totals = [np.trapezoid(f, eta, axis=1) for f in integrands]
    partial = None
    if eta_slices is not None:
        at = np.asarray(eta_slices, dtype=float)
        partial = np.empty((3, kernels.ell.size, at.size))
        for n, f in enumerate(integrands):
            cum = np.concatenate(
                [np.zeros((f.shape[0], 1)),
                 np.cumsum(0.5 * (f[:, 1:] + f[:, :-1]) * np.diff(eta), axis=1)],
                axis=1)
            for i in range(f.shape[0]):
                partial[n, i] = np.interp(at, eta, cum[i])
    return ThreeSlots(ell=kernels.ell, k_com=k, sachs_wolfe=totals[0],
                      doppler=totals[1], integrated=totals[2], partial=partial)


@dataclass(frozen=True)
class Slots:
    r"""The five-term assembly and `direct`, over `ell`. Undamped."""

    ell: np.ndarray
    k_com: float
    w_c0: np.ndarray             # + Int W C_0 K
    v_c1_grav: np.ndarray        # - Int V C_1^grav K
    w_c1_grav_prime: np.ndarray  # - Int W C_1^grav' K
    v_pair: np.ndarray           # - Int V (vhat_B + C_2) K'
    w_c2_prime: np.ndarray       # - Int W C_2' K'
    direct: np.ndarray           #   Int W {C_0 K + C_1 K' + C_2 K''}

    TERMS = ("w_c0", "v_c1_grav", "w_c1_grav_prime", "v_pair", "w_c2_prime")

    @property
    def total(self) -> np.ndarray:
        return (self.w_c0 + self.v_c1_grav + self.w_c1_grav_prime
                + self.v_pair + self.w_c2_prime)


def slots(kernels: Kernels, s: Sources) -> Slots:
    r"""The five slots and the direct integral at the kernels' $k$."""
    if s.eta.shape != kernels.eta.shape:
        raise ValueError("sources and kernels must share the eta grid")
    eta, k = kernels.eta, kernels.k_com
    W, V = s.opacity, s.visibility
    K, Kp, Kpp = kernels.j, -k * kernels.jd, k * k * kernels.jdd

    def integral(rows: np.ndarray, f: np.ndarray) -> np.ndarray:
        return np.trapezoid(rows * f, eta, axis=1)

    w_c0 = integral(K, W * s.c0)
    return Slots(
        ell=kernels.ell, k_com=k, w_c0=w_c0,
        v_c1_grav=integral(K, -V * s.c1_grav),
        w_c1_grav_prime=integral(K, -W * s.c1_grav_prime),
        v_pair=integral(Kp, -V * (s.v_hat_b + s.c2)),
        w_c2_prime=integral(Kp, -W * s.c2_prime),
        direct=(w_c0 + integral(Kp, W * s.c1_grav - V * s.v_hat_b)
                + integral(Kpp, W * s.c2)))
