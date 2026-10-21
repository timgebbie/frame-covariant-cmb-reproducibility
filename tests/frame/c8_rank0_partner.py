#!/usr/bin/env python3
"""C8 -- the rank-0 partner.  Settles whether a.B_0 belongs in C_0.

WRITTEN AFTER T-107 REFUTED THE RESTORATION.  P1-B measured that putting
a.B_0 into C_0 doubles criterion 5b, because (107) already carries the
monopole source:

    -C_1' = (kappa' vhat_B)' + (a.B_1)'/k ,
    (a.B_1)'/k = (Phi_A' - Phi_H') + (k/3) tau_1        [D11, T-79]

and (k/3) tau_1 = -a.B_0.  So the integrand C_0 - C_1' + C_2'' holds the
monopole source ONCE ALREADY, inside -C_1'.

WHY c5 COULD NOT SEE THIS, AND WHY THIS CHECK CAN.  c5 scores Delta C_0
against k^2 Delta C_2 -- one coefficient against another.  The partner of
Delta C_0 is not in C_2; it is in -C_1'.  A check built from one coefficient
cannot see a cancellation distributed across the bracket.  THIS CHECK SCORES
THE WHOLE RANK-0 CONTENT OF THE INTEGRAND, which is the object the
cancellation lives in.

THE ALGEBRA.  With C_0 = p0.(a.B_2) + q0.(a.B_0), and under a boost
(appendix-frame-division's frame table, with tau_1 UN-REDUCED per T-66):

    Delta(a.B_2) = -k v ,   Delta tau_1 = -v ,   Delta(a.B_0) = +k v / 3

the rank-0 frame shift of C_0 - C_1' is

    -p0 k v  +  q0 k v / 3  -  k v / 3 .

Three rows, and only one of them vanishes.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here; it holds no copy. Correcting
#: the instrument therefore corrects the audit by construction.
AUDIT_TITLE = 'The rank-0 partner, and where the monopole source enters'
AUDIT_PROSE = (
  '(107) already carries the monopole source: $-C_1\'=(\\kappa\'\\hat v_B)\'+'
  '(a\\mathcal{B}_1)\'/k$ and $(a\\mathcal{B}_1)\'/k=(\\Phi_A\'-\\Phi_H\')+'
  '\\tfrac k3\\tau_1$, with $\\tfrac k3\\tau_1=-a\\mathcal{B}_0$. So (89)\'s '
  '$\\delta_{\\ell0}$ row is **correctly empty** of $\\mathcal{B}_0$ and only '
  'its normalisation is wrong. With $\\alpha_0$ in place of $\\alpha_2$, '
  '$C_0=-\\tfrac13a\\mathcal{B}_2$ and its frame shift $+\\tfrac13kv$ is '
  'cancelled **inside the bracket**, by $\\Delta[\\tfrac k3\\tau_1]$ in '
  '$-C_1\'$. Restoring $a\\mathcal{B}_0$ counts the source twice and leaves '
  'the same residual with the opposite sign -- finding T-107, which criterion '
  '5b caught at $98.5\\%$ and no frame instrument could.')

import sympy as sp
from _common import (finish, ETA_0 as E0, W, s, sdot, j, jp, integrate, GRID,
                     report)

k, v = sp.symbols('k v', positive=True)

# the three boosted inputs, from the frame table.  tau_1 is UN-REDUCED (T-66).
dB2   = -k*v                 # Delta(a.B_2)
dtau1 = -v                   # Delta tau_1
dB0   = sp.Rational(1, 3)*k*v   # Delta(a.B_0) = -(k/3) Delta tau_1

# the monopole term (107) already carries inside -C_1'
partner = sp.Rational(1, 3)*k*dtau1          # Delta[ (k/3) tau_1 ]

rows = [
    ('A  printed       alpha_2, no B_0', sp.Rational(-5, 2), 0),
    ('B  T-104         alpha_0, no B_0', sp.Rational(-1, 3), 0),
    ('C  T-105         alpha_0 + B_0  ', sp.Rational(-1, 3), -1),
]

shifts = []
for name, p0, q0 in rows:
    d = sp.simplify(p0*dB2 + q0*dB0 + partner)
    shifts.append(d)
    print(f'  {name}   Delta[C_0 - C_1\']_rank0 = {sp.nsimplify(d/(k*v))} k v')

A, B, C = shifts
print()
print(f'  B cancels exactly                 : {B == 0}')
print(f'  C is the double count, equal and  : C = {sp.nsimplify(C/(k*v))} k v'
      f'   vs  B-without-partner = {sp.nsimplify((B-partner)/(k*v))} k v')
print(f'  A is the appendix\'s "no partner"  : {sp.nsimplify(A/(k*v))} k v'
      f'   = 13/6, not 5/2 -- the partner is there, it is simply outmatched')
print()

# ---- numeric confirmation: the shift under the actual weighted integral ----
def resid(l, kk, d_over_kv):
    """|Delta of the rank-0 integrand| / its own scale, with d = d_over_kv*k*v."""
    X = lambda e: kk*(E0 - e)
    # v is carried by the boost potential s(e); the rank-0 shift rides on it
    f  = lambda e: W(e)*float(d_over_kv)*kk*s(e)*j(l, X(e))
    sc = integrate(lambda e: W(e)*abs(kk*s(e))*abs(j(l, X(e))))
    return abs(integrate(f))/max(sc, 1e-30)

r = [max(resid(l, kk, sp.nsimplify(d/(k*v))) for l, kk in GRID) for d in shifts]
print(f'  worst residual:  A {r[0]:.2e} | B {r[1]:.2e} | C {r[2]:.2e}')

allok = (
  report('C8a  the printed row leaves a rank-0 shift', A != 0)
  & report('C8b  alpha_0 with NO B_0 cancels against (k/3)tau_1 in -C_1\'',
           B == 0)
  & report('C8c  restoring B_0 counts the source twice', C != 0,
           f'residual {sp.nsimplify(C/(k*v))} k v, equal and opposite to B\'s partner')
  & report('C8d  and what it leaves is exactly one more copy of the partner',
           sp.simplify(C - partner) == 0,
           'the restoration adds a source the bracket already held')
  & report('C8e  numerically, only B is at the floor', r[1]*10 < min(r[0], r[2]),
           f'{r[1]:.1e} vs {min(r[0], r[2]):.1e}'))

finish({'shift_printed': str(sp.nsimplify(A/(k*v))),
        'shift_alpha0_no_B0': str(sp.nsimplify(B/(k*v))),
        'shift_alpha0_with_B0': str(sp.nsimplify(C/(k*v))),
        'r_printed': r[0], 'r_alpha0_no_B0': r[1], 'r_alpha0_with_B0': r[2]})
