#!/usr/bin/env python3
"""C13 -- the endpoint map, the orientation of the optical depth, and where a
late potential can enter the line of sight.   2026-11-11.

The three synthetic controls of the supplement's section "Line-of-sight
assembly and repository conformity".  Until Supplement v1.4.3 they were cited
to scripts that were never in this tree, so their numbers had no generator a
reader could run.  This file is that generator.  Every history in it is built
here and every reference value is a closed form.

C13a  THE OPACITY LEDGER.  With the Thomson part of a coefficient
      C1T = -kappa' vB and W' = V = kappa' W,

          W C1T = -V vB              an identity,
          V C1T = -W kappa'^2 vB     the rate counted twice.

      Their ratio is kappa'(eta) itself, so on a history whose rate is not
      constant no rescaling maps one onto the other, and their line-of-sight
      integrals against the same kernel differ.  This is the negative control:
      the check fails if the double count could be absorbed into a constant.

C13b  THE ENDPOINT MAP.  u_C = gamma (u_N + beta z) with z orthogonal to u_N,
      one photon p = E_N (u_N + e_N) = E_C (u_C + e_C), mu_N = z.e_N, and
      mu_C = z_C.e_C with z_C = gamma (z + beta u_N), the boost axis in the
      rest space of u_C.  Then

          E_C = gamma E_N (1 - beta mu_N),
          mu_C = (mu_N - beta) / (1 - beta mu_N),
          T_C(mu_C) = D(mu_C) T_N(mu_N),  D = sqrt(1 - beta^2) / (1 + beta mu_C)

      for a directionally Planckian brightness.  The boost and its inverse
      return T_N to round-off.  The untransformed Legendre coefficients do not
      agree, and the generator at beta = 0,

          dT_C/dbeta = (1 - mu^2) dT_N/dmu - mu T_N ,

      predicts by how much.  For T_N = sum_l c_l P_l it carries c_l to
      l - 1 with weight l^2/(2l+1) and to l + 1 with weight -(l+1)^2/(2l+1),
      so with c_0 = 1 and c_1 = 0

          da_1 = beta (-1 + 4 c_2 / 5)        + O(beta^3, beta^2 c),
          da_2 = (2/3) beta^2 + (9/7) beta c_3 + O(beta^2 c),

      the (2/3) beta^2 being the kinematic quadrupole of the monopole.

C13c  THE LATE SUPPORT.  kappa(eta) = int_eta^eta0 q ds is integrated towards
      the observer, so W = e^-kappa has W' = q W = V while the ordinary
      derivative of kappa is -q.  A potential that moves only where q = 0
      reaches int W g in full, 2 dPhi_A with Phi_H = -Phi_A, and int V g not
      at all.  The control moves the same step inside the scattering window,
      where V does see it, so the null is a statement about support and not
      an integrand that cannot respond.

No project code is imported; `_common` checks that before anything runs.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = 'The endpoint map and the late support'
AUDIT_PROSE = ("A boost and its inverse return a directional temperature to round-off, "
               "while the untransformed dipole and quadrupole differ by the amounts the "
               "generator $(1-\\mu^2)\\partial_\\mu T-\\mu T$ predicts, so the raw multipoles "
               "of two frames are not the frame comparison. The optical depth is integrated "
               "towards the observer, so $W'=\\mathcal V$, and a potential that moves where "
               "the scattering rate vanishes reaches $\\int Wg$ in full and "
               "$\\int\\mathcal Vg$ not at all. $\\mathcal VC_1^{\\rm T}$ counts the rate "
               "twice and is not a rescaling of $WC_1^{\\rm T}$.")

import numpy as np
from scipy.integrate import quad
from scipy.special import eval_legendre
from _common import finish, jp, report

# --------------------------------------------------------------------------
# The rate history: compact support on 0.13 < eta < 0.37, closed-form depth.
# q = A (1 - u^2)^3 with u = (eta - C)/H; int (1-u^2)^3 du = F(u) below.
A_Q, C_Q, H_Q, ETA0 = 3.4, 0.25, 0.12, 1.0

def _u(e):
    return (e - C_Q) / H_Q

def q(e):
    u = _u(e)
    return A_Q * (1.0 - u * u) ** 3 if abs(u) < 1.0 else 0.0

def q_prime(e):
    u = _u(e)
    return -6.0 * A_Q * u * (1.0 - u * u) ** 2 / H_Q if abs(u) < 1.0 else 0.0

def _F(u):
    return u - u ** 3 + 0.6 * u ** 5 - u ** 7 / 7.0

def kappa(e):
    """int_e^eta0 q ds, in closed form."""
    u = min(max(_u(e), -1.0), 1.0)
    return A_Q * H_Q * (_F(1.0) - _F(u))

def W(e):
    return np.exp(-kappa(e))

def V(e):
    return q(e) * W(e)

metrics = {}

# --------------------------------------------------------------------------
# C13a -- the opacity ledger, a negative control.
def v_b(e):                                   # a synthetic baryon velocity
    return np.sin(7.0 * e) + 0.3

support = np.linspace(0.14, 0.36, 221)       # strictly inside q > 0
identity = max(abs(W(e) * (-q(e) * v_b(e)) + V(e) * v_b(e)) for e in support)
ratio = np.array([(V(e) * (-q(e) * v_b(e))) / (W(e) * (-q(e) * v_b(e)))
                  for e in support if abs(v_b(e)) > 1e-3])
spread = float(ratio.max() / ratio.min())
ell, k = 10, 80.0
los_once = quad(lambda e: W(e) * (-q(e) * v_b(e)) * jp(ell, k * (ETA0 - e)),
                0.13, 0.37, limit=400)[0]
los_twice = quad(lambda e: V(e) * (-q(e) * v_b(e)) * jp(ell, k * (ETA0 - e)),
                 0.13, 0.37, limit=400)[0]
best_scale = los_twice / los_once
# The best single constant cannot map the twice-counted integrand onto the
# once-counted one: the residual after the best rescaling stays order one.
grid = np.linspace(0.13, 0.37, 2401)
once = np.array([W(e) * (-q(e) * v_b(e)) for e in grid])
twice = np.array([V(e) * (-q(e) * v_b(e)) for e in grid])
c_ls = float(np.dot(once, twice) / np.dot(once, once))
resid = float(np.linalg.norm(twice - c_ls * once) / np.linalg.norm(twice))
print(f'  C13a  W C1T + V vB, max over the support: {identity:.2e}')
print(f'  C13a  (V C1T)/(W C1T) = kappa\' spans a factor {spread:.1f} on the support')
print(f'  C13a  best constant rescaling leaves {resid:.3f} of V C1T unexplained')
report('C13a  W C1T = -V vB is an identity', identity < 1e-13, f'{identity:.1e}')
report('C13a  V C1T is not a rescaling of W C1T (negative control)',
       spread > 2.0 and resid > 0.1, f'ratio spans x{spread:.1f}, residual {resid:.2f}')
metrics.update(ledger_identity=identity, ledger_ratio_span=spread,
               ledger_rescaling_residual=resid,
               ledger_los_once=los_once, ledger_los_twice=los_twice)

# --------------------------------------------------------------------------
# C13b -- the endpoint map.
BETA = 0.002
GAMMA = 1.0 / np.sqrt(1.0 - BETA ** 2)
C2, C3, C4 = 3e-4, 2e-4, 1e-4

def T_N(mu):
    return (1.0 + C2 * eval_legendre(2, mu) + C3 * eval_legendre(3, mu)
            + C4 * eval_legendre(4, mu))

def T_N_prime(mu):
    # d/dmu of P2, P3, P4
    return C2 * 3.0 * mu + C3 * 0.5 * (15.0 * mu ** 2 - 3.0) \
        + C4 * 0.125 * (140.0 * mu ** 3 - 60.0 * mu)

def T_C(mu_c, beta=BETA):
    mu_n = (mu_c + beta) / (1.0 + beta * mu_c)
    return np.sqrt(1.0 - beta ** 2) / (1.0 + beta * mu_c) * T_N(mu_n)

mu = np.linspace(-1.0, 1.0, 20001)
mu_c = (mu - BETA) / (1.0 - BETA * mu)
round_trip = float(np.max(np.abs(T_C(mu_c) / (GAMMA * (1.0 - BETA * mu)) - T_N(mu))))

nodes, weights = np.polynomial.legendre.leggauss(64)   # exact for these degrees
def a_ell(f, l):
    return (2 * l + 1) / 2.0 * float(np.sum(weights * f(nodes) * eval_legendre(l, nodes)))

da1 = a_ell(T_C, 1) - a_ell(T_N, 1)
da2 = a_ell(T_C, 2) - a_ell(T_N, 2)
da1_pred = BETA * (-1.0 + 0.8 * C2)
da2_pred = (2.0 / 3.0) * BETA ** 2 + (9.0 / 7.0) * BETA * C3
h = 1e-4
gen_num = (T_C(mu, h) - T_C(mu, -h)) / (2.0 * h)
gen_err = float(np.max(np.abs(gen_num - ((1.0 - mu ** 2) * T_N_prime(mu) - mu * T_N(mu)))))
print(f'  C13b  boost then inverse boost, max |T - T_N|: {round_trip:.2e}')
print(f'  C13b  untransformed dipole difference      {da1:+.6e}  (predicted {da1_pred:+.6e})')
print(f'  C13b  untransformed quadrupole difference  {da2:+.6e}  (predicted {da2_pred:+.6e})')
print(f'  C13b  generator against a central difference at beta = 1e-4: {gen_err:.1e}')
report('C13b  the boost and its inverse return the sky to round-off',
       round_trip < 1e-14, f'{round_trip:.1e}')
report('C13b  untransformed dipole difference is the predicted one',
       abs(da1 - da1_pred) < 1e-8, f'{da1:+.5e}, off by {abs(da1 - da1_pred):.1e}')
report('C13b  untransformed quadrupole difference is the predicted one',
       abs(da2 - da2_pred) < 1e-8, f'{da2:+.5e}, off by {abs(da2 - da2_pred):.1e}')
report('C13b  dT_C/dbeta = (1-mu^2) dT_N/dmu - mu T_N at beta = 0',
       gen_err < 1e-7, f'{gen_err:.1e}')
metrics.update(beta=BETA, round_trip=round_trip, dipole_difference=da1,
               dipole_predicted=da1_pred, quadrupole_difference=da2,
               quadrupole_predicted=da2_pred, generator_error=gen_err)

# --------------------------------------------------------------------------
# C13c -- the late support.  Phi_A constant to 0.62, then down by 0.006 under
# a quintic smoothstep completed at 0.85; Phi_H = -Phi_A, so g = 2 Phi_A'.
E1, E2, DPHI = 0.62, 0.85, -0.006

def phi_a_prime(e):
    x = (e - E1) / (E2 - E1)
    if x <= 0.0 or x >= 1.0:
        return 0.0
    return DPHI * (30 * x ** 4 - 60 * x ** 3 + 30 * x ** 2) / (E2 - E1)

def g(e):
    return 2.0 * phi_a_prime(e)

cuts = [0.13, 0.25, 0.37, E1, E2]
int_Wg = quad(lambda e: W(e) * g(e), 0.0, ETA0, points=cuts, limit=400, epsabs=1e-15)[0]
int_Vg = quad(lambda e: V(e) * g(e), 0.0, ETA0, points=cuts, limit=400, epsabs=1e-15)[0]
# The control that makes the null a statement about support: the same step
# moved inside the scattering window, 0.15 to 0.35, IS seen by V.
def g_early(e):
    x = (e - 0.15) / 0.20
    if x <= 0.0 or x >= 1.0:
        return 0.0
    return 2.0 * DPHI * (30 * x ** 4 - 60 * x ** 3 + 30 * x ** 2) / 0.20
int_Vg_early = quad(lambda e: V(e) * g_early(e), 0.0, ETA0,
                    points=[0.13, 0.15, 0.25, 0.35, 0.37], limit=400)[0]
# W' = V on the history, by a central difference against the closed form.
probe = np.linspace(0.135, 0.365, 47)
hd = 1e-6
w_err = max(abs((W(e + hd) - W(e - hd)) / (2 * hd) - V(e)) / max(V(e), 1e-300)
            for e in probe)
kappa_err = max(abs((kappa(e + hd) - kappa(e - hd)) / (2 * hd) + q(e)) / q(e)
                for e in probe)
print(f'  C13c  total optical depth {kappa(0.0):.6f}')
print(f'  C13c  int W g = {int_Wg:+.7f}  (2 dPhi_A = {2 * DPHI:+.7f})')
print(f'  C13c  int V g = {int_Vg:+.1e}; with the step inside the window {int_Vg_early:+.4f}')
print(f'  C13c  W\' = V to {w_err:.1e} relative; d kappa/d eta = -q to {kappa_err:.1e}')
report('C13c  W\' = V with the depth integrated towards the observer',
       w_err < 1e-6 and kappa_err < 1e-6, f'{w_err:.1e}, {kappa_err:.1e}')
report('C13c  a late potential reaches int W g in full',
       abs(int_Wg - 2 * DPHI) < 1e-12, f'{int_Wg:+.7f}')
report('C13c  and int V g not at all', abs(int_Vg) < 1e-15, f'{int_Vg:.1e}')
report('C13c  the same step inside the window is seen by V (control)',
       abs(int_Vg_early) > 1e-3, f'{int_Vg_early:+.4f}')
metrics.update(optical_depth=kappa(0.0), int_W_g=int_Wg, int_V_g=int_Vg,
               int_V_g_inside_window=int_Vg_early,
               w_prime_error=w_err, kappa_prime_error=kappa_err)

finish(metrics)
