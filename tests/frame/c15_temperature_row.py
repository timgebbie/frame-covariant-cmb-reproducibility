#!/usr/bin/env python3
"""C15 -- the temperature row of the acoustic pair, from the 1+3 equations.
Added 2026-11-24.

Annals II writes the Newtonian (shear-free) frame's radiation monopole as

  (147)  (D_a ln T)^. + H (D_a ln T + A_a) + (1/3) D_a Theta
                                             = -(1/3) D_a (D_c tau^c),
  (149)  D_<a D_b> (ln T)^. = -D_<a D_b> Phi_H^. - (1/3) D_<a D_b> (D_c tau^c),
  (153)  dT^. = -H Phi_A - Phi_H^. + (k/a) tau_1 / 3,

and reaches the oscillator (154) by "ignoring the expansion coupled term (i.e.
the small scale approximation)", the -H Phi_A of (153).  The bundle's released
pair runs without that term.  This instrument decides whether the term is in
the 1+3 equation at all, from the 1+3 relations alone:

C15a  the harmonics on a plane wave: D_<a Q_b> = -(k/a) Q_ab and
      D^a Q_a = (k/a) Q for Annals I's Q_a = -(a/k) D_a Q, the rules the mode
      algebra below uses (c14 checks the scalar rule
      D_<a D_b> X = -(k/a)^2 X Q_ab);
C15b  (147) is the gradient of the radiation energy equation,
      (ln T)^. = -Theta/3 - (1/3) D_c tau^c, carried through the 1+3
      commutator (D_a f)^. = D_a f^. - (Theta/3) D_a f + f^. A_a: its H A_a
      is that commutator's f^. A_a with f^. = -H, so (147) is right;
C15c  in the shear-free frame the E_ab equation, with Annals II's potentials
      E_ab + pi_ab/2 = -D_<a D_b> Phi_H and pi_ab = -D_<a D_b>(Phi_A + Phi_H),
      gives D_<a D_b>(Phi_H^. - H Phi_A) = (1/2) D_<a q_b>, and the
      (0 alpha) constraint gives (2/3) D_a Theta = q_a, so
      (1/3) D_a Theta = D_a(Phi_H^. - H Phi_A), the lapse term included;
C15d  with C15c, (147) in modes is dT^. = -Phi_H^. + (k/a) tau_1 / 3: the
      H Phi_A cancels.  Negative controls: (149)'s replacement
      (1/3) D_a Theta -> D_a Phi_H^. returns (153) as printed, -H Phi_A and
      all; dropping (147)'s commutator term instead returns +H Phi_A;
C15e  the antecedent's own limit: outside the horizon the adiabatic dT that
      (180) and (181) start from, -(2/3) Phi_A in the matter era, is constant
      under the 1+3 row and drifts as -2 Phi_A ln(eta) under (153) as
      printed (-Phi_i ln(eta) in the radiation era);
C15f  comparator, not derivation: in the perturbed FLRW metric the normal
      observers' expansion has (1/3) delta Theta = -H psi - phi^., and the
      map psi = Phi_A, phi = -Phi_H returns C15c's relation.

The slip is (149)'s: it writes the expansion gradient without its lapse term,
which cancels the H A_a that (147) correctly carries.

No project code is imported; `_common` checks that before anything runs.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
AUDIT_TITLE = "The temperature row of the acoustic pair"
AUDIT_PROSE = ("Annals~II's (153) carries $-H\\Phi_A$, which it drops as the small-scale "
               "approximation. The $1+3$ equations do not carry it: (147)'s $H\\tilde A_a$, the "
               "commutator's, is cancelled by the lapse term of the expansion gradient, "
               "$\\tfrac13\\mathrm D_a\\Theta=\\mathrm D_a(\\dot\\Phi_H-H\\Phi_A)$ from the shear-free "
               "frame's $E_{ab}$ equation and $(0\\alpha)$ constraint, which (149) writes as "
               "$\\mathrm D_a\\dot\\Phi_H$. The row is $\\delta T'=-\\Phi_H'+\\tfrac k3\\tau_1$, and the "
               "antecedent's own super-horizon condition, constant under it, drifts as "
               "$-2\\Phi_A\\ln\\eta$ under the printed row.")

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp
from _common import finish, report

metrics = {}

# --------------------------------------------------------------------------
# C15a -- the harmonics on a plane wave (a = 1 at the instant considered).
X1, X2, X3, k = sp.symbols('x1 x2 x3 k', positive=True)
xs = (X1, X2, X3)
Q = sp.cos(k * X3)
grad = lambda f: [sp.diff(f, v) for v in xs]
lap = lambda f: sum(sp.diff(f, v, 2) for v in xs)
Qa = [-g / k for g in grad(Q)]                                  # (-k)^-1 D_a Q
Qab = [[(sp.diff(Q, xs[i], xs[j]) - sp.KroneckerDelta(i, j) * lap(Q) / 3) / k**2
        for j in range(3)] for i in range(3)]                   # k^-2 D_<a D_b> Q
symgrad = [[(sp.diff(Qa[j], xs[i]) + sp.diff(Qa[i], xs[j])) / 2
            - sp.KroneckerDelta(i, j) * sum(sp.diff(Qa[c], xs[c]) for c in range(3)) / 3
            for j in range(3)] for i in range(3)]               # D_<a Q_b>
vec_rule = all(sp.simplify(symgrad[i][j] + k * Qab[i][j]) == 0
               for i in range(3) for j in range(3))
div_rule = sp.simplify(sum(sp.diff(Qa[c], xs[c]) for c in range(3)) - k * Q) == 0
report('C15a  D_<a Q_b> = -(k/a) Q_ab and D^a Q_a = (k/a) Q on Annals I\'s harmonics',
       vec_rule and div_rule)

# --------------------------------------------------------------------------
# Mode algebra in cosmic time t.  Coefficients: dT (D_a ln T = (k/a) dT Q_a),
# PhiA, PhiH (gradient coefficients, D_a Phi = (k/a) Phi Q_a), tau1
# (tau_a = tau1 Q_a), Thg (D_a Theta = (k/a) Thg Q_a), q (q_a = q Q_a),
# E, pi (E_ab = E Q_ab, pi_ab = pi Q_ab).  Q, Q_a, Q_ab are comoving, so their
# time derivatives along u vanish at background order.
t = sp.symbols('t')
a = sp.Function('a')(t)
H = sp.diff(a, t) / a
dT, PhiA, PhiH, tau1, Thg, q = (sp.Function(n)(t) for n in
                                 ('dT', 'PhiA', 'PhiH', 'tau1', 'Thg', 'q'))
K = k / a

# C15b -- (147) from the energy equation and the commutator.  The radiation
# energy equation (ln T)^. = -Theta/3 - (1/3) D_c tau^c, at first order, has
# gradient coefficient (f^.)_g = -(1/3) Thg - (1/3)(-(k/a) tau1)... in the
# scalar-to-gradient rule a scalar S = S_s Q has S_g = -S_s, and
# D_a(D^c tau_c) = (k/a) tau1 D_a Q = (k/a) * (-(k/a) tau1) Q_a.
fdot_g = -Thg / 3 + K * tau1 / 3                 # gradient coefficient of (ln T)^.
lhs_commutator = sp.diff(K * dT, t)              # (D_a ln T)^. along u, coefficient
rhs_commutator = K * fdot_g - H * K * dT + (-H) * K * PhiA   # D_a f^. - H D_a f + f^. A_a
# (147) as printed, in the same coefficients:
eq147 = sp.diff(K * dT, t) + H * (K * dT + K * PhiA) + K * Thg / 3 - K**2 * tau1 / 3
from_commutator = lhs_commutator - rhs_commutator
report('C15b  (147) is the energy equation carried through the 1+3 commutator; its H A_a is the commutator\'s',
       sp.simplify(eq147 - from_commutator) == 0)

# C15c -- the E_ab equation and the (0 alpha) constraint, shear-free frame.
#   E^._ab = -Theta E_ab - (1/2) pi^._ab - (1/6) Theta pi_ab - (1/2) D_<a q_b>
# with D_<a q_b> = -(k/a) q Q_ab, and the potentials
#   E + pi/2 = (k/a)^2 PhiH,   pi = (k/a)^2 (PhiA + PhiH).
pi_c = K**2 * (PhiA + PhiH)
E_c = K**2 * PhiH - pi_c / 2
edot_residual = sp.expand(sp.diff(E_c, t) + 3 * H * E_c + sp.diff(pi_c, t) / 2
                          + H * pi_c / 2 - K * q / 2)
target = sp.expand(K**2 * (sp.diff(PhiH, t) - H * PhiA) - K * q / 2)
edot_ok = sp.simplify(edot_residual - target) == 0
# (0 alpha): (2/3) D_a Theta = q_a, so (2/3) K Thg = q.  Eliminate q.
q_sol = sp.Rational(2, 3) * K * Thg
theta_third = sp.solve(sp.Eq(target.subs(q, q_sol), 0), Thg)[0] / 3
lapse_ok = sp.simplify(theta_third - (sp.diff(PhiH, t) - H * PhiA)) == 0
report('C15c  E_ab equation and (0 alpha) constraint: (1/3) D_a Theta = D_a(Phi_H^. - H Phi_A)',
       edot_ok and lapse_ok, str(sp.simplify(theta_third)))

# C15d -- the row, and the two controls.
def row(theta_third_expr, drop_commutator=False):
    e = eq147 - (0 if not drop_commutator else H * K * PhiA)
    e = e.subs(Thg, 3 * theta_third_expr)
    return sp.simplify(sp.solve(sp.Eq(e, 0), sp.diff(dT, t))[0])
row_13 = row(sp.diff(PhiH, t) - H * PhiA)
row_149 = row(sp.diff(PhiH, t))
row_nocomm = row(sp.diff(PhiH, t) - H * PhiA, drop_commutator=True)
want_13 = -sp.diff(PhiH, t) + K * tau1 / 3
want_153 = -H * PhiA - sp.diff(PhiH, t) + K * tau1 / 3
report('C15d  the 1+3 row is dT^. = -Phi_H^. + (k/a) tau_1/3: the H Phi_A cancels',
       sp.simplify(row_13 - want_13) == 0, str(row_13))
report('C15d  negative control: (149)\'s D_a Phi_H^. for (1/3) D_a Theta returns (153) as printed',
       sp.simplify(row_149 - want_153) == 0, str(row_149))
report('C15d  negative control: dropping (147)\'s commutator term returns +H Phi_A instead',
       sp.simplify(row_nocomm - (want_13 + H * PhiA)) == 0)
report("C15d  Annals II's (153) as printed carries -H Phi_A, which the 1+3 equations do not",
       sp.simplify(want_153 - want_13) != 0, 'defect in the antecedent', polarity='defect')

# --------------------------------------------------------------------------
# C15e -- the antecedent's own limit, outside the horizon, conformal time eta.
# Matter era: Hc = 2/eta, Phi_A = -Phi_H = 1, tau_1' = -k(dT + Phi_A).
# Radiation era: Hc = 1/eta, Phi_A = -Phi_H = 1 (the primordial value).
def drift(era, printed, k_eta_i=1e-4, span=100.0):
    hc_coef = 2.0 if era == 'matter' else 1.0
    dT0 = -2.0 / 3.0 if era == 'matter' else -0.5
    kk = k_eta_i                                     # eta_i = 1
    def rhs(eta, y):
        d, t1 = y
        dd = (-hc_coef / eta * 1.0 if printed else 0.0) + kk / 3.0 * t1
        return [dd, -kk * (d + 1.0)]
    t1_0 = -(1.0 / 3.0 if era == 'matter' else 0.5) * kk * 1.0
    s = solve_ivp(rhs, (1.0, span), [dT0, t1_0], rtol=1e-11, atol=1e-14)
    return s.y[0, -1] - dT0
m13, mpr = drift('matter', False), drift('matter', True)
r13, rpr = drift('radiation', False), drift('radiation', True)
print(f'  C15e  matter era, 100-fold in eta: 1+3 row {m13:+.3e}, printed {mpr:+.4f} '
      f'(-2 ln 100 = {-2*np.log(100):+.4f})')
print(f'  C15e  radiation era, 100-fold in eta: 1+3 row {r13:+.3e}, printed {rpr:+.4f} '
      f'(-ln 100 = {-np.log(100):+.4f})')
report('C15e  the adiabatic dT outside the horizon, -(2/3) Phi_A as (180)-(181) start from and -Phi_i/2 in the radiation era, is constant under the 1+3 row',
       abs(m13) < 1e-4 and abs(r13) < 1e-4, f'{m13:+.1e}, {r13:+.1e}')
report('C15e  under (153) as printed it drifts as -2 Phi_A ln(eta) (matter), -Phi_i ln(eta) (radiation)',
       abs(mpr + 2 * np.log(100)) < 1e-3 and abs(rpr + np.log(100)) < 1e-3,
       f'{mpr:+.4f}, {rpr:+.4f}')
metrics.update(matter_drift_13=m13, matter_drift_printed=mpr,
               radiation_drift_13=r13, radiation_drift_printed=rpr)

# --------------------------------------------------------------------------
# C15f -- comparator only: the normal observers' expansion in the perturbed
# FLRW metric ds^2 = a^2[-(1+2 psi) d eta^2 + (1-2 phi) dx^2].
eta, eps = sp.symbols('eta epsilon')
A = sp.Function('A')(eta)                         # the scale factor in eta
psi, phi = sp.Function('psi')(eta), sp.Function('phi')(eta)
sqrtg = A**4 * sp.sqrt((1 + 2 * eps * psi) * (1 - 2 * eps * phi)**3)
u0 = 1 / (A * sp.sqrt(1 + 2 * eps * psi))
theta = sp.diff(sqrtg * u0, eta) / sqrtg          # (1/sqrt g) d_mu (sqrt g u^mu), spatially uniform part
dtheta3 = sp.simplify(sp.diff(theta / 3, eps).subs(eps, 0))
Hc = sp.diff(A, eta) / A
comparator = sp.simplify(dtheta3 - (-(Hc / A) * psi - sp.diff(phi, eta) / A))
# psi = Phi_A, phi = -Phi_H, and Phi_H^. = Phi_H'/a: (1/3) delta Theta = Phi_H^. - H Phi_A
report('C15f  comparator: the metric\'s normal observers give (1/3) delta Theta = -H psi - phi^., i.e. C15c under psi = Phi_A, phi = -Phi_H',
       comparator == 0, str(comparator))

finish(metrics)
