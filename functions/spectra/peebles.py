r"""Peebles recombination: the effective three-level atom.

**v1.1.0's named deliverable, and the thing equilibrium Saha cannot do.**
`functions.spectra.decoupling.saha_ionisation` places last scattering within a
few percent in redshift, which is all v1.0.0 needed. It cannot give the
*visibility width*, because equilibrium has no freeze-out: Saha drives
$x_e\to0$ while Peebles leaves a residual plateau at $x_e\sim2\times10^{-4}$,
and the width of the visibility is what fixes the Silk damping envelope. That
is why criterion **5b** is blocked on this module and not on the spectrum code
(decision **S18**).

---

## The equation

Peebles (1968); Zel'dovich, Kurt & Sunyaev (1968). In redshift, with
$\mathrm dt=-\mathrm dz/[H(1+z)]$,

$$\frac{\mathrm dx_e}{\mathrm dz}
  = \frac{C_r}{H(z)(1+z)}
    \Bigl[\alpha_B\,x_e^2\,n_H - \beta_B\,(1-x_e)\,e^{-E_{21}/k_BT}\Bigr].$$

The bracket is the net recombination rate, positive while recombination
proceeds, so $x_e$ **increases with $z$** — it is larger in the past, which is
the sign check worth doing before any number comes out.

$C_r$ is Peebles' suppression factor, the fraction of $n=2$ atoms that reach the
ground state before a Lyman-$\alpha$ photon re-excites them:

$$C_r = \frac{1+K\Lambda_{2s1s}n_{1s}}{1+K(\Lambda_{2s1s}+\beta_B)n_{1s}},
\qquad K=\frac{\lambda_\alpha^3}{8\pi H},\qquad n_{1s}=(1-x_e)n_H.$$

Without $C_r$ the universe recombines far too fast: the net rate is throttled by
the fact that direct recombination to the ground state produces a photon that
immediately ionises a neighbour, so recombination proceeds only through the
two-photon $2s\to1s$ decay ($\Lambda_{2s1s}=8.2246\ \mathrm s^{-1}$) and through
the redshifting of Lyman-$\alpha$ out of resonance (the $K$ term).

## What is derived and what is imported, stated plainly

This bundle's rule is *derive, do not transcribe*, and **recombination is the
place that rule stops**. $\alpha_B$ is a fit to an atomic-physics calculation and
cannot be obtained from the $1+3$ formalism or from anything else in this tree.
It is therefore **imported**, with its source, and marked as such — the same
honesty the conventions sheet applies to a sourced row.

| quantity | status | source |
|---|---|---|
| the ODE above, and $C_r$ | **derived** structure, standard | Peebles (1968) |
| $\beta_B$ from $\alpha_B$ | **derived**, by detailed balance | — |
| $\alpha_B(T)$ | **imported fit** | Pequignot, Petitjean & Boisson (1991), in the RECFAST form of Seager, Sasselov & Scott (1999) |
| $\Lambda_{2s1s}$, $\lambda_\alpha$, $E_{21}$ | **imported constants** | atomic physics |
| the fudge factor $F=1.14$ | **imported, and it is a fudge** | Seager, Sasselov & Scott (1999) |

**$F=1.14$ is carried as a named parameter, not hidden in a coefficient.** It
exists because the three-level atom is not the true multi-level atom, and
RECFAST calibrates it against a full level-resolved code. Setting `fudge=1.0`
runs the honest three-level model and recombines measurably later; the
difference is what the fudge is worth, and `tests/` measures it rather than
asserting it.

## Helium is not modelled, and that is a scope statement

$x_e$ here is $n_e/n_H$ from **hydrogen only**. Helium recombines at
$z\sim2000$–$6000$, above the range where the visibility has support, so it does
not move last scattering; what it does do is change $x_e$ at high $z$ (the true
curve starts near $1.16$, not $1$) and contribute to $n_e$ through $Y_p$. The
helium *mass fraction* enters here only through $n_H=(1-Y_p)n_b$, which is a
normalisation, and `y_he=0.0` reproduces the existing Saha convention exactly so
that a Saha/Peebles comparison measures freeze-out and nothing else. **One
change at a time**: turning helium on is v1.2.0's business, with 5b.

## Why `h` appears here when the rest of the bundle runs at $h_0=1$

The background carries `h0=1.0`: that is a **choice of time unit**, not a claim
about the Hubble constant. Every dimensionless combination elsewhere in the
bundle either has no $h$ in it or cancels it — `_thomson_scale` says so
explicitly. Peebles does not cancel: $K\Lambda n_{1s}\propto\Omega_bh^2/(hE)
=\Omega_bh/E$, so the physical $h$ survives and has to be supplied. It is an
explicit parameter with a stated default rather than a number reached into from
somewhere, because a hidden $h$ here would be a silent cosmology.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from functions.background.flrw import Background
from functions.spectra.decoupling import saha_ionisation

__all__ = [
    "PeeblesSolution",
    "peebles_ionisation",
    "case_b_recombination",
    "RECFAST_FUDGE",
]

# ---------------------------------------------------------------------------
# constants: imported, each with its provenance in the module docstring
# ---------------------------------------------------------------------------

_B_HYDROGEN_EV = 13.605693          #: n=1 binding energy
_E_2S_EV = _B_HYDROGEN_EV / 4.0     #: n=2 binding energy, 3.4 eV
_E_21_EV = _B_HYDROGEN_EV - _E_2S_EV  #: Lyman-alpha, 10.204 eV
_T_CMB_K = 2.7255
_K_B_EV_PER_K = 8.617333262e-5
_M_E_EV = 510998.95
_HBAR_C_EV_CM = 1.9733e-5

_LAMBDA_2S1S = 8.2245809            #: two-photon decay rate, s^-1
_LAMBDA_ALPHA_CM = 1.21567e-5       #: Lyman-alpha wavelength, cm
_N_B0_PER_OMEGA_B_H2 = 1.123e-5     #: baryon number density today, cm^-3
_H0_PER_H_INV_S = 3.2408e-18        #: 100 km/s/Mpc in s^-1

#: The RECFAST fudge factor. **Named, not buried.** See the module docstring:
#: it corrects the three-level atom toward a full multi-level calculation, and
#: `fudge=1.0` is the un-fudged three-level model.
RECFAST_FUDGE = 1.14


def case_b_recombination(temperature_k: np.ndarray, *,
                         fudge: float = RECFAST_FUDGE) -> np.ndarray:
    r"""$\alpha_B(T)$ in cm$^3$ s$^{-1}$ — **an imported fit, not a derivation**.

    Pequignot, Petitjean & Boisson (1991), in the form RECFAST uses
    (Seager, Sasselov & Scott 1999):

    $$\alpha_B = F\cdot10^{-13}\,\frac{a\,t^{b}}{1+c\,t^{d}},
      \qquad t=T/10^4\,\mathrm K,$$

    with $a=4.309$, $b=-0.6166$, $c=0.6703$, $d=0.5300$.
    """
    t = np.asarray(temperature_k, dtype=float) / 1.0e4
    t = np.clip(t, 1e-8, None)
    return fudge * 1.0e-13 * 4.309 * t**-0.6166 / (1.0 + 0.6703 * t**0.5300)


def _photoionisation(alpha_b: np.ndarray, temperature_k: np.ndarray) -> np.ndarray:
    r"""$\beta_B$ from $\alpha_B$ by **detailed balance** — derived, not fitted.

    $$\beta_B=\alpha_B\left(\frac{m_ek_BT}{2\pi\hbar^2}\right)^{3/2}
      e^{-E_{2s}/k_BT},$$

    the same thermal factor the Saha routine assembles, with the $n=2$ binding
    energy rather than the $n=1$. Writing it this way rather than fitting it
    separately means the pair cannot drift apart: whatever $\alpha_B$ is, $\beta_B$
    is its equilibrium partner.
    """
    temperature_ev = _K_B_EV_PER_K * np.asarray(temperature_k, dtype=float)
    thermal = (_M_E_EV * temperature_ev / (2.0 * np.pi)) ** 1.5 / _HBAR_C_EV_CM**3
    with np.errstate(over="ignore", under="ignore"):
        return alpha_b * thermal * np.exp(-_E_2S_EV / temperature_ev)


@dataclass(frozen=True)
class PeeblesSolution:
    """x_e(z) from the three-level atom, with what it was computed from."""

    z: np.ndarray
    x_e: np.ndarray
    omega_b_h2: float
    h: float
    y_he: float
    fudge: float

    def at(self, z: np.ndarray) -> np.ndarray:
        """x_e interpolated onto another redshift grid, in log for the tail.

        The freeze-out plateau spans four decades in $x_e$; interpolating it
        linearly would smear the tail that the whole module exists to produce.
        """
        return np.exp(
            np.interp(
                np.asarray(z, dtype=float)[::-1],
                self.z[::-1],
                np.log(np.clip(self.x_e, 1e-30, None))[::-1],
            )[::-1]
        )

    @property
    def freeze_out(self) -> float:
        """The residual ionisation left behind — the number Saha cannot produce."""
        return float(self.x_e[int(np.argmin(self.z))])


def peebles_ionisation(
    background: Background,
    *,
    z_start: float = 1800.0,
    z_end: float = 100.0,
    omega_b_h2: float = 0.0224,
    h: float = 0.674,
    y_he: float = 0.0,
    fudge: float = RECFAST_FUDGE,
    n_points: int = 2000,
) -> PeeblesSolution:
    r"""Integrate the three-level atom from `z_start` down to `z_end`.

    **The initial condition is Saha, and that is not circular.** At
    $z\simeq1800$ the recombination rate still vastly exceeds the expansion
    rate, so equilibrium holds and Saha *is* the solution there; the integration
    then follows the departure from equilibrium, which is the part Saha gets
    wrong. Starting higher costs stiffness for no information. `tests/` starts
    from two different redshifts and requires the freeze-out tail to agree,
    which is the check that the choice is not load-bearing — the same discipline
    as deriving a grid rather than choosing one (finding **T-3**).

    **Integrated with an implicit method.** The equation is stiff near the start,
    where the bracket is a difference of two large and nearly equal terms; an
    explicit stepper either crawls or goes unstable, and a stepper that silently
    takes 10^6 steps is a defect waiting to be blamed on the physics.
    """
    if not (z_end < z_start):
        raise ValueError("z_end must be below z_start: the integration runs forward in time")

    hubble_0 = h * _H0_PER_H_INV_S
    n_h0 = (1.0 - y_he) * _N_B0_PER_OMEGA_B_H2 * omega_b_h2  # cm^-3 today

    def hubble(z: float) -> float:
        """H(z) in s^-1 — the background's shape, in physical units."""
        a = 1.0 / (1.0 + z)
        return hubble_0 * float(background.conformal_hubble(a)) / a

    def rhs(z: float, y: np.ndarray) -> list[float]:
        x_e = float(np.clip(y[0], 0.0, 1.0))
        temperature_k = _T_CMB_K * (1.0 + z)
        temperature_ev = _K_B_EV_PER_K * temperature_k

        n_h = n_h0 * (1.0 + z) ** 3
        alpha_b = float(case_b_recombination(temperature_k, fudge=fudge))
        beta_b = float(_photoionisation(np.array(alpha_b), np.array(temperature_k)))

        hz = hubble(z)
        k_factor = _LAMBDA_ALPHA_CM**3 / (8.0 * np.pi * hz)
        n_1s = (1.0 - x_e) * n_h

        suppression = (1.0 + k_factor * _LAMBDA_2S1S * n_1s) / (
            1.0 + k_factor * (_LAMBDA_2S1S + beta_b) * n_1s
        )

        with np.errstate(over="ignore", under="ignore"):
            excite = beta_b * (1.0 - x_e) * np.exp(-_E_21_EV / temperature_ev)
        net = alpha_b * x_e**2 * n_h - float(excite)

        return [suppression * net / (hz * (1.0 + z))]

    x_start = float(saha_ionisation(np.array([z_start]), omega_b_h2=omega_b_h2)[0])
    z_grid = np.linspace(z_start, z_end, int(n_points))

    solution = solve_ivp(
        rhs, (z_start, z_end), [x_start], t_eval=z_grid,
        method="Radau", rtol=1e-8, atol=1e-14, max_step=20.0,
    )
    if not solution.success:
        raise RuntimeError(f"the three-level atom did not integrate: {solution.message}")

    return PeeblesSolution(
        z=z_grid, x_e=np.clip(solution.y[0], 1e-30, 1.0),
        omega_b_h2=omega_b_h2, h=h, y_he=y_he, fudge=fudge,
    )
