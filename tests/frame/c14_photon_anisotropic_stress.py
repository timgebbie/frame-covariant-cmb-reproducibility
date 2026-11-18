#!/usr/bin/env python3
"""C14 -- the photons' anisotropic stress, and how far Phi_H = -Phi_A holds.
Added 2026-11-11.

The constraint the radiation-era construction closes Phi_A with, derived from
the 1+3 relations alone and checked here term by term:

  (i)   the potentials, as Annals II defines them and Paper 1 tabulates (C2.5),
            E_ab - pi_ab/2 = D_<a D_b> Phi_A,  E_ab + pi_ab/2 = -D_<a D_b> Phi_H,
        so pi_ab = -D_<a D_b>(Phi_A + Phi_H), with 8 pi G = 1;
  (ii)  the photons' stress from their brightness (MGE99 Eqs. 49 and 80, as
        Paper 1 restates them): pi_ab = (8 pi/15) Pi_ab and, linearised,
        tau_A = (pi/rho) Pi_A, so pi_ab = (8/15) rho_gamma tau_ab;
  (iii) Paper 1's mode rule, D_a X = +k X Q_a, writes a scalar by the
        coefficient of its gradient; with Annals I's Q_A_l = (-k)^-l D_<A_l> Q
        that coefficient is minus the scalar's own, hence
        D_<a D_b> X = -k^2 X Q_ab, with tau_ab = tau_2 Q_ab.

Together, with rho_gamma = 3 H^2 Omega_gamma (8 pi G = 1) and k comoving,

        k^2 (Phi_A + Phi_H) = (8/5) Hc^2 Omega_gamma(a) tau_2 .      [C14]

C14a  the moment coefficient 8 pi/15 and the linearised 8/15, by quadrature
      on the sphere of a brightness carrying a quadrupole;
C14b  the mode rule and the phase of the hierarchy, symbolically on a plane
      wave: D_<a D_b> X = -k^2 X Q_ab for X's gradient coefficient; the
      free-streaming rows tau_0' = -(k/3) tau_1 and tau_2' = k tau_1 of (F.1)
      in this phase; and the monopole of (F.1) is minus the gradient variable
      dT that the acoustic pair carries.  Annals II's dust case,
      E_ab = k^2 Phi_H Q_ab with Phi_A = -Phi_H, is the rule applied;
C14c  the size after decoupling.  Outside the horizon the free-streaming
      quadrupole grows from the dipole and [C14] gives (Phi_A+Phi_H)/Phi_A.
      Its matter-era closed form, -(16/15) Omega_g(eta_*) (eta_*/eta)^2
      (1 - (eta_*/eta)^2), peaks at -(4/15) Omega_g(eta_*) at sqrt(2) eta_*;
      the control recovers it with last scattering deep in matter
      domination, and the PLANCK_MODEL value (a_*/a_eq = 5.33) is reported
      and asserted.  The sign is the covariant one, independent of the
      phase: a hierarchy in the opposite phase paired with [C14] gives the
      opposite sign, and that pairing is the negative control.

No project code is imported; `_common` checks that before anything runs.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = "The photons' anisotropic stress"
AUDIT_PROSE = ("With the potentials defined by $E_{ab}\\mp\\tfrac12\\pi_{ab}$ and the photons' "
               "stress $\\pi_{ab}=\\tfrac8{15}\\rho_\\gamma\\tau_{ab}$ from their brightness, "
               "$k^2(\\Phi_A+\\Phi_H)=\\tfrac85\\mathcal H^2\\Omega_\\gamma\\tau_2$ in the phase of (F.1), "
               "whose monopole is $-\\delta T$. Outside the horizon after decoupling the "
               "free-streaming quadrupole makes $(\\Phi_A+\\Phi_H)/\\Phi_A$ negative, peaking at "
               "$-\\tfrac4{15}\\Omega_\\gamma(\\eta_\\ast)$ at $\\sqrt2\\eta_\\ast$ in a matter era "
               "and at $-0.042$ near $1.6\\eta_\\ast$ on the Planck background.")

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp
from _common import finish, report

metrics = {}

# --------------------------------------------------------------------------
# C14a -- the moment coefficient and the linearised 8/15.
mu, wmu = np.polynomial.legendre.leggauss(96)
phi = np.linspace(0.0, 2 * np.pi, 192, endpoint=False)
M, P = np.meshgrid(mu, phi, indexing='ij')
W = np.outer(wmu, np.full(phi.size, 2 * np.pi / phi.size))     # dOmega weights
st = np.sqrt(1 - M**2)
e = np.stack([st * np.cos(P), st * np.sin(P), M])               # unit directions
I3 = np.eye(3)
def stf2(e):                                                    # e_<a e_b>
    return np.einsum('a...,b...->ab...', e, e) - I3[:, :, None, None] / 3.0
O2 = stf2(e)
# Delta_2 from full contraction: int O_ab O^ab dOmega = 5 Delta_2
delta2 = float(np.sum(W * np.einsum('ab...,ab...->...', O2, O2))) / 5.0
# a brightness with a small quadrupole, Pi(e) = Pi0 [1 + x eps_ab e^a e^b]
eps = np.array([[0.7, 0.2, -0.1], [0.2, -0.3, 0.4], [-0.1, 0.4, -0.4]])
eps = 0.5 * (eps + eps.T); eps -= np.trace(eps) / 3 * I3        # PSTF
Pi0, x = 1.0, 1e-6
Pi_e = Pi0 * (1 + x * np.einsum('ab,ab...->...', eps, O2))
rho = float(np.sum(W * Pi_e))                                   # rho = int Pi dOmega
Pi_ab = np.einsum('abij,ij->ab', O2, W * Pi_e) / delta2       # PSTF moment
pi_ab = delta2 * Pi_ab                                          # pi = int Pi O_ab
T_rel = (Pi_e / Pi0) ** 0.25 - 1.0                              # tau(e), exactly
tau_ab = np.einsum('abij,ij->ab', O2, W * T_rel) / delta2
ratio = float(np.sum(pi_ab * tau_ab) / (rho * np.sum(tau_ab * tau_ab)))
print(f'  C14a  Delta_2 = {delta2:.15f}   8 pi/15 = {8*np.pi/15:.15f}')
print(f'  C14a  pi_ab / (rho_gamma tau_ab) = {ratio:.9f}   8/15 = {8/15:.9f}')
report('C14a  pi_ab = (8 pi/15) Pi_ab on the PSTF basis',
       abs(delta2 - 8 * np.pi / 15) < 1e-12, f'{delta2 - 8*np.pi/15:+.1e}')
report('C14a  pi_ab = (8/15) rho_gamma tau_ab to first order in the anisotropy',
       abs(ratio - 8 / 15) < 1e-5, f'{ratio:.7f}')
metrics.update(delta_2=delta2, stress_ratio=ratio)

# --------------------------------------------------------------------------
# C14b -- the mode rule and the phase, symbolically on a plane wave.
X1, X2, X3, k = sp.symbols('x1 x2 x3 k', positive=True)
xs = (X1, X2, X3)
Q = sp.cos(k * X3)                                              # real harmonic
grad = lambda f: [sp.diff(f, v) for v in xs]
lap = lambda f: sum(sp.diff(f, v, 2) for v in xs)
Qa = [-g / k for g in grad(Q)]                                  # (-k)^-1 D_a Q
Qab = [[(sp.diff(Q, xs[i], xs[j]) - sp.KroneckerDelta(i, j) * lap(Q) / 3) / k**2
        for j in range(3)] for i in range(3)]                   # k^-2 D_<a D_b> Q
Xs = sp.Symbol('Xs')                                            # scalar coefficient
X = Xs * Q
# gradient coefficient X_g by D_a X = k X_g Q_a, read off the z-component
X_g = sp.simplify(grad(X)[2] / (k * Qa[2]))
hess = [[sp.diff(X, xs[i], xs[j]) - sp.KroneckerDelta(i, j) * lap(X) / 3
         for j in range(3)] for i in range(3)]
rule = all(sp.simplify(hess[i][j] + k**2 * X_g * Qab[i][j]) == 0
           for i in range(3) for j in range(3))
# Annals II's dust case: E_ab = -D_<a D_b> Phi_H (Phi_A = -Phi_H) = k^2 Phi_H Q_ab
dust = all(sp.simplify(-hess[i][j] - k**2 * X_g * Qab[i][j]) == 0
           for i in range(3) for j in range(3))
# the free-streaming rows in this phase: tau_ab' = -D_<a tau_b>, tau' = -(1/3) D^a tau_a
t1 = sp.Symbol('t1')
taub = [t1 * q for q in Qa]
row2 = [[-(sp.diff(taub[j], xs[i]) + sp.diff(taub[i], xs[j])) / 2
         + sp.KroneckerDelta(i, j) * sum(sp.diff(taub[c], xs[c]) for c in range(3)) / 3
         for j in range(3)] for i in range(3)]
row2_ok = all(sp.simplify(row2[i][j] - k * t1 * Qab[i][j]) == 0
              for i in range(3) for j in range(3))
row0 = -sum(sp.diff(taub[c], xs[c]) for c in range(3)) / 3
row0_ok = sp.simplify(row0 - (-(k / 3) * t1 * Q)) == 0
# the monopole: tau_0 is the scalar coefficient; dT is the gradient coefficient
monopole_sign = sp.simplify(X_g / Xs)
print(f'  C14b  gradient coefficient / scalar coefficient = {monopole_sign}')
report('C14b  D_<a D_b> X = -k^2 X Q_ab for the gradient coefficient', rule)
report("C14b  Annals II's dust case E_ab = k^2 Phi_H Q_ab is the rule applied", dust)
report('C14b  free streaming in this phase: tau_2\' = k tau_1, tau_0\' = -(k/3) tau_1',
       row2_ok and row0_ok)
report('C14b  the monopole of (F.1) is minus the gradient variable dT',
       monopole_sign == -1, f'{monopole_sign}')

# --------------------------------------------------------------------------
# C14c -- outside the horizon after decoupling.  Scaled conformal time x with
# y = a/a_eq = x^2 + 2x (matter and radiation, photons the only radiation);
# tau_1 = k t1, tau_2 = k^2 t2, Phi_A from Kodama & Sasaki, Phi_i = 1.
def y_of(x): return x * x + 2 * x
def hc(x): return (2 * x + 2) / (x * x + 2 * x)
def phi_ks(y):
    y = np.atleast_1d(np.asarray(y, dtype=float))
    out = np.empty_like(y)
    s = y < 1e-3
    yy = y[~s]
    out[~s] = (16 * np.sqrt(1 + yy) + 9 * yy**3 + 2 * yy**2 - 8 * yy - 16) / (10 * yy**3)
    out[s] = 1 - y[s] / 16
    return out

def extremum(y_star, phase=+1):
    """phase=+1: (F.1)'s phase, tau_2' = +k tau_1, paired with [C14].
       phase=-1: the opposite phase paired with the same [C14] -- the control."""
    x_star = -1 + np.sqrt(1 + y_star)
    x0 = 1e-5
    # before decoupling the photons share the adiabatic velocity: v' = -Hc v - k Phi_A
    tc = solve_ivp(lambda x, s: [-hc(x) * s[0] - phi_ks(y_of(x))[0]],
                   (x0, x_star), [-x0 / 2], rtol=1e-11, atol=1e-14)
    t1_star = tc.y[0, -1]
    def fs(x, s):                       # free streaming; dT = Phi_A - (3/2) Phi_i
        t1, t2 = s
        pa = phi_ks(y_of(x))[0]
        return [-((pa - 1.5) + pa), phase * t1]
    grid = np.geomspace(x_star, 60 * x_star, 6000)
    sol = solve_ivp(fs, (x_star, grid[-1]), [t1_star, 0.0], t_eval=grid,
                    rtol=1e-11, atol=1e-14)
    y = y_of(grid)
    r = (8 / 5) * hc(grid)**2 / (1 + y) * sol.y[1] / phi_ks(y)
    i = int(np.argmax(np.abs(r)))
    return r[i], grid[i] / x_star, float(np.interp(10 * x_star, grid, r)), 1 / (1 + y_star)

r_ctl, at_ctl, _, om_ctl = extremum(1.0e4)
r_pl, at_pl, r10_pl, om_pl = extremum(5.33)
r_neg, _, _, _ = extremum(5.33, phase=-1)
pred = -(4 / 15) * om_ctl
print(f'  C14c  matter-era control: extremum {r_ctl:+.4e} at {at_ctl:.3f} eta_*;'
      f'  closed form {pred:+.4e} at {np.sqrt(2):.3f}')
print(f'  C14c  PLANCK_MODEL (a_*/a_eq = 5.33, Omega_g = {om_pl:.4f}): extremum {r_pl:+.4f}'
      f' at {at_pl:.3f} eta_*; {r10_pl:+.5f} at 10 eta_*')
print(f'  C14c  opposite phase with the same constraint: {r_neg:+.4f}')
report('C14c  matter-era control recovers -(4/15) Omega_g(eta_*) at sqrt(2) eta_*',
       abs(r_ctl / pred - 1) < 1e-2 and abs(at_ctl / np.sqrt(2) - 1) < 2e-2,
       f'{r_ctl/pred:.4f}, {at_ctl:.3f}')
report('C14c  PLANCK_MODEL extremum -0.042 near 1.6 eta_*, negative as the covariant sign requires',
       r_pl < 0 and abs(r_pl + 0.0423) < 5e-4 and abs(at_pl - 1.645) < 0.05,
       f'{r_pl:+.4f} at {at_pl:.2f}')
report('C14c  the opposite phase paired with [C14] reverses the sign (negative control)',
       r_neg > 0 and abs(r_neg + r_pl) < 1e-12, f'{r_neg:+.4f}')
metrics.update(matter_era_extremum=r_ctl, matter_era_at=at_ctl,
               planck_extremum=r_pl, planck_at=at_pl, planck_at_10=r10_pl,
               opposite_phase=r_neg)

finish(metrics)
