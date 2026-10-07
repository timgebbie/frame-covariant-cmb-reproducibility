"""The matter power spectrum and transfer function, Annals II Appendix J.

Published equation numbers, resolved against the accepted manuscript.

    (J.1)  P(k) = A (k eta_0)^{n-1}
    (J.3)  P(k) = B k^n T^2(k),  with T(k) ~ +1 on large scales
    (J.5)  T(k) = [1 + (a k + (b k)^{3/2} + (c k)^2)^nu]^{-1/nu}

           a = 6.4/Gamma, b = 3.0/Gamma, c = 1.7/Gamma  (all in h^-1 Mpc),
           nu = 1.13, Gamma ~= Omega_0 h.

**Finding B-10: (J.5) is printed with $+1/\\nu$.** As printed the transfer
function *grows without bound*: at $k=10\\,{\\rm Mpc}^{-1}$ it reaches $6.7\\times
10^3$ instead of $1.5\\times10^{-4}$. That inverts the physics --- a transfer
function suppresses small scales, because modes entering the horizon during
radiation domination stagnate --- and it would make the matter power spectrum
rise without limit at high $k$.

The large-scale limit is the same either way, which is why the text's own
statement that "$T(k)\\sim+1$ on large scales" does not catch it: the bracket
tends to 1 and $1^{\\pm1/\\nu}=1$. Only the small-scale limit distinguishes them,
and only the negative exponent gives the $k^{-2}$ falloff that Bond &
Efstathiou's fit is a fit *to*. Corrected here; the printed form is kept as
`transfer_function_printed` so the difference is demonstrable.

**On the two normalisations.** (J.1) and (J.3) are *different* definitions of
$P(k)$, differing by one power of $k$, which is the fact that settled finding
B-5: (201) descends from (J.1) and carries one factor of the comoving distance,
while (204) descends from (J.3) and is correctly free of it. (J.1) carries
$\\eta_0^{n-1}$, which is unity at $n=1$ and so does not disturb B-5's analysis.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "shape_parameter",
    "transfer_function",
    "transfer_function_printed",
    "power_spectrum_j1",
    "power_spectrum_j3",
    "BOND_EFSTATHIOU",
    "ANNALS_II_GAMMA",
]

#: (a, b, c, nu) of (J.5), with a, b, c in units of 1/Gamma h^-1 Mpc.
BOND_EFSTATHIOU = (6.4, 3.0, 1.7, 1.13)

#: The shape parameter Annals II states for its standard-CDM model.
#:
#: The text says "Gamma ~= Omega_0 h" and then, for h = 0.5 and Omega_B = 0.05,
#: gives **Gamma = 0.48**. Omega_0 h is 0.50 for that model, so the stated value
#: carries an unnamed baryon correction of about 4%. The standard corrections of
#: that era -- Gamma = Omega_0 h exp[-Omega_B(1 + sqrt(2h)/Omega_0)] -- give
#: 0.452, not 0.48. The paper's own number is used, and the discrepancy is
#: recorded in the parameter table rather than reconciled by guessing which
#: correction was meant.
ANNALS_II_GAMMA = 0.48


def shape_parameter(omega_0: float, h: float) -> float:
    """Gamma ~= Omega_0 h, Appendix J. The uncorrected form the text states."""
    return omega_0 * h


def _bracket(k_mpc: np.ndarray, gamma: float, h: float) -> np.ndarray:
    """(a k + (b k)^{3/2} + (c k)^2)^nu, with k in Mpc^-1.

    The fit's a, b, c are in $h^{-1}$ Mpc, so each is divided by `h` to put it in
    Mpc before multiplying a wavenumber in Mpc$^{-1}$. Getting that wrong is a
    silent factor of two at $h=0.5$, so it is done once, here.
    """
    a, b, c, nu = BOND_EFSTATHIOU
    k = np.asarray(k_mpc, dtype=float)
    a_mpc, b_mpc, c_mpc = a / (gamma * h), b / (gamma * h), c / (gamma * h)
    return (a_mpc * k + (b_mpc * k) ** 1.5 + (c_mpc * k) ** 2) ** nu


def transfer_function(
    k_mpc: np.ndarray, *, gamma: float = ANNALS_II_GAMMA, h: float = 0.5
) -> np.ndarray:
    """(J.5), **corrected**: the exponent is $-1/\\nu$. Finding B-10.

    T -> 1 as k -> 0 and T ~ k^-2 as k -> infinity, which is the CDM behaviour
    the Bond & Efstathiou form is fitted to.
    """
    nu = BOND_EFSTATHIOU[3]
    return (1.0 + _bracket(k_mpc, gamma, h)) ** (-1.0 / nu)


def transfer_function_printed(
    k_mpc: np.ndarray, *, gamma: float = ANNALS_II_GAMMA, h: float = 0.5
) -> np.ndarray:
    """(J.5) exactly as printed, with $+1/\\nu$. Kept so B-10 is demonstrable."""
    nu = BOND_EFSTATHIOU[3]
    return (1.0 + _bracket(k_mpc, gamma, h)) ** (1.0 / nu)


def power_spectrum_j1(
    k: np.ndarray, *, amplitude: float = 1.0, n: float = 1.0, eta_0: float = 2.0
) -> np.ndarray:
    """(J.1): P(k) = A (k eta_0)^{n-1}. No transfer function.

    This is the definition (201) descends from, and the one finding B-5 is about.
    At n = 1 it is the constant A, and eta_0 drops out.
    """
    return amplitude * (np.asarray(k, dtype=float) * eta_0) ** (n - 1.0)


def power_spectrum_j3(
    k: np.ndarray,
    *,
    amplitude: float = 1.0,
    n: float = 1.0,
    transfer: np.ndarray | None = None,
) -> np.ndarray:
    """(J.3): P(k) = B k^n T^2(k). One power of k more than (J.1).

    `transfer` defaults to unity, which is the §8.3.2 large-scale case (204)
    uses; supply `transfer_function(k)` for the full matter spectrum.
    """
    k = np.asarray(k, dtype=float)
    t = 1.0 if transfer is None else np.asarray(transfer, dtype=float)
    return amplitude * k**n * t**2
