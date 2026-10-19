#!/usr/bin/env python3
"""C5 -- the monopole row, and the dipole shift.   Audit results 7, 8.

The l=0 matching row of Annals II `find_coef`, with the l=0 SOURCE restored
(which `source-calB` carries and `find_coef` drops):

    C_0 + k^2 C_2 h_0''(0) = - a B_0 ,     h_0''(0) = -1/3,  beta_0 = 1

Boost:  DC_2 = v/k;  B_0 = -(1/3) D^a tau_a  and  tau~_a = tau_a - v_a
[GDE99 (37)], so  D B_0 = +(1/3) D^a v_a, and with D carrying k/a
(cbrII.tex line 2563 at K=0),  a.D B_0 = +(1/3) k v  =  (1/3) k^2 DC_2.

They cancel exactly, giving gamma = 0.  Dropping B_0 leaves gamma = +1/3;
the printed row (5/beta_2 * 1/3 = +5/2) leaves gamma = -5/2.

**WHAT THIS CHECK CANNOT SEE** -- P1-T, 2026-10-19, at P1-B's request.
Delta C_0 = 0 constrains how B_0 MOVES, not what it IS.  It fixes the
multiplicative normalisation exactly -- scale a.B_0 by lambda and the
cancellation closes only at lambda = 1 -- but any ADDITIVE boost-invariant
piece X with Delta X = 0 passes this check for free.  Since
C_0 = (1/3) k^2 C_2 + (1/3) k tau_1, a missing additive term of O(k) or lower
is invisible where the k^2 piece dominates and dominant where it does not.
This instrument cannot distinguish that case and nothing here should be read
as excluding one.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sympy as sp
from _common import (finish, ETA_0 as E0, W, s, sdot, j, jp, jpp, integrate, GRID, report)

k, v = sp.symbols('k v', positive=True)
h0, dC2, adB0 = sp.Rational(-1,3), v/k, sp.Rational(1,3)*k*v
rows = [('printed  +5/2, B_0 dropped',  sp.Rational(5,2), 0),
        ("h_0''(0)=-1/3, B_0 dropped",  h0,               0),
        ("h_0''(0)=-1/3, B_0 RESTORED", h0,               1)]
gammas = []
for name, h, src in rows:
    dC0 = sp.simplify(-src*adB0 - k**2*h*dC2)
    g = sp.simplify(dC0/(k**2*(v/k)))
    gammas.append(g)
    print(f'  {name:32s}  Delta C_0 = {str(dC0):>10s}   gamma = {g}')
ok_cancel = sp.simplify(adB0 - sp.Rational(1,3)*k**2*dC2) == 0

def resid(l, kk, ga):
    X = lambda e: kk*(E0-e)
    f = lambda e: W(e)*(ga*kk*kk*s(e)*j(l, X(e)) + sdot(e)*kk*jp(l, X(e))
                        - s(e)*kk*kk*jpp(l, X(e)))
    sc = integrate(lambda e: W(e)*abs(s(e))*abs(j(l, X(e))))*kk*kk
    return abs(integrate(f))/max(sc, 1e-30)
r = [max(resid(l, kk, float(g)) for l, kk in GRID) for g in gammas]
print(f'  worst residual:  gamma=-5/2 {r[0]:.2e} | gamma=+1/3 {r[1]:.2e}'
      f' | gamma=0 {r[2]:.2e}')
print('  NB this check cannot see an ADDITIVE boost-invariant piece in C_0;')
print('     see the docstring.  Delta C_0 = 0 fixes normalisation, not content.')
allok = (report('C5a  a.Delta B_0 cancels (1/3) k^2 Delta C_2 exactly', ok_cancel)
         & report('C5b  only the restored row gives gamma = 0', gammas[2] == 0)
         & report('C5c  and it is >=10x better than either alternative',
                  r[2]*10 < min(r[0], r[1]), f'{r[2]:.1e} vs {min(r[0],r[1]):.1e}'))
finish({'gamma_printed': str(gammas[0]), 'gamma_no_B0': str(gammas[1]),
        'gamma_restored': str(gammas[2]), 'r_printed': r[0], 'r_no_B0': r[1],
        'r_restored': r[2]})
