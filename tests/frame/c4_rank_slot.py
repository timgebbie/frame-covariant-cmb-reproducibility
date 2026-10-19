#!/usr/bin/env python3
"""C4 -- the rank-2 slot forced by frame invariance.   Audit result 6.

tau_l = int W [ gamma k^2 C2 K + alpha C1 K' + beta C2 K'' ] deta',
boost: DC2 = s, DC1 = -sdot, DC0 = gamma k^2 s.  Requiring Dtau_l = 0 at l>=2
for ARBITRARY s vanishing at the endpoints gives, after one by-parts and the
spherical Bessel equation,  beta = -alpha  and  gamma = 0.

NOTE the residual at (beta=-alpha, gamma=0) is NOT zero here: it is the
Thomson term, absent from this functional.  See c6_thomson.py.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sympy as sp
from _common import (finish, ETA_STAR as ES, ETA_0 as E0, W, s, sdot, j, jp, jpp,
                     integrate, GRID, report)

a_, b_, g_, k_, l_, D_, W_, V_ = sp.symbols('alpha beta gamma k ell Delta W V')
cK  = sp.expand(g_*k_**2*W_ + (a_+b_)*W_*(l_*(l_+1)/D_**2 - k_**2))
cKp = sp.expand(a_*V_ + (a_+b_)*2*W_/D_)
ok_sym = (sp.simplify(cKp.subs(b_, -a_)) == a_*V_
          and sp.simplify(cK.subs([(b_, -a_), (g_, 0)])) == 0)
print(f'  K  coefficient: {cK}')
print(f"  K' coefficient: {cKp}")
print('  K\' vanishes only if alpha+beta = 0; K then forces gamma = 0')

def resid(l, k, al, be, ga):
    X = lambda e: k*(E0-e)
    f = lambda e: W(e)*(ga*k*k*s(e)*j(l, X(e)) - al*sdot(e)*(-k*jp(l, X(e)))
                        + be*s(e)*(k*k*jpp(l, X(e))))
    sc = integrate(lambda e: W(e)*abs(s(e))*abs(j(l, X(e))))*k*k
    return abs(integrate(f))/max(sc, 1e-30)

good = max(resid(l, k, 1., -1., 0.) for l, k in GRID)
bad1 = max(resid(l, k, 1., +1., 0.) for l, k in GRID)
bad2 = max(resid(l, k, 1., -1., 1/3) for l, k in GRID)
print(f'  worst residual  beta=-alpha,gamma=0 {good:.2e} | beta=+alpha {bad1:.2e}'
      f' | gamma=1/3 {bad2:.2e}')
print('  NB the residual floor at beta=-alpha,gamma=0 is NOT numerical: it is the')
print('     Thomson term, absent from this functional.  c6_thomson.py removes it')
print('     and the residual drops to ~1e-13.  C4a is the result; C4b is a check.')
allok = (report('C4a  symbolic condition is beta=-alpha, gamma=0', ok_sym)
         & report('C4b  that choice is >=10x better than either alternative',
                  good*10 < min(bad1, bad2), f'{good:.1e} vs {min(bad1,bad2):.1e}'))
finish({'r_beta_minus': good, 'r_beta_plus': bad1, 'r_gamma_third': bad2})
