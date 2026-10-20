#!/usr/bin/env python3
"""C6 -- the Thomson v_B slot.   P1-T, 2026-10-19.

C-B-coef bundles the Thomson term: -C_1 = (1/k)(a B_1 + kappa' v_B).
Under the boost Dv_B = -v = -k s, so DC_1 = -sdot + kappa' s -- the
gravitational -sdot PLUS a kappa' s.  That extra piece enters the alpha C_1 K'
slot as alpha int V s K', and the K' coefficient becomes 2 alpha V.

  A  kappa' v_B INSIDE C_1 *AND DIFFERENTIATED* -> no (alpha,beta,gamma)
     makes the bulk invariant
  B  carried as its own term, NOT differentiated, reduced vhat_B = v_B/k
     -> invariance needs c = alpha, and the residual goes to machine zero
     unreduced v_B -> needs c = alpha/k, which is not a constant

  CORRECTION 2026-10-20, P1-T, and it matters.  "Carried separately under V"
  in an earlier version of this docstring read as a WEIGHT CHANGE.  It is not
  one.  W*kappa' = V is an identity, so W*C_1^thom = -V*vhat_B already: the
  Thomson term is at visibility weight in (102) as printed, and there was
  never a weight to change.  What is wrong is that (102) DIFFERENTIATES it --
  d/deta of a coefficient still carrying a bare kappa' is what manufactures
  kappa'^2.  The remedy is not to move it; it is not to differentiate it.

  P1-B measured the misreading at 320-682x and withdrew T-88 (T-93); T-94
  measures what the differentiation costs -- the resulting V kappa'' vhat
  term is 93-97% of the Newtonian integrand and 1.8e5 times the physical
  Doppler source g vhat_B.

  The ASSERTIONS BELOW ARE UNCHANGED by that correction.  What c6 establishes
  is the invariance obstruction, and it survives: kappa' v_B inside C_1 AND
  DIFFERENTIATED admits no (alpha,beta,gamma).  Only the remedy was misstated.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sympy as sp
from _common import (finish, ETA_0 as E0, V, W, s, sdot, j, jp, jpp, integrate, GRID,
                     report)

a_, b_, c_, k_, D_, W_, V_ = sp.symbols('alpha beta c k Delta W V')
inside = sp.simplify((a_*V_ + (a_+b_)*2*W_/D_ + a_*V_).subs(b_, -a_))
out_r  = sp.simplify((a_*V_ + (a_+b_)*2*W_/D_ - c_*V_).subs(b_, -a_))
out_u  = sp.simplify((a_*V_ + (a_+b_)*2*W_/D_ - c_*k_*V_).subs(b_, -a_))
print(f"  A  inside C_1, alpha+beta=0 :  K' coeff {inside}  -> zero only if alpha=0")
print(f"  B  outside, reduced         :  K' coeff {out_r}  -> c = alpha")
print(f"  B  outside, un-reduced      :  K' coeff {out_u}  -> c = alpha/k, not constant")
ok_sym = (inside == 2*a_*V_ and sp.solve(out_r, c_) == [a_])

def resid(l, kk, mode, c=1.0):
    X  = lambda e: kk*(E0-e)
    K1 = lambda e: -kk*jp(l, X(e))
    def f(e):
        base = W(e)*(-sdot(e)*K1(e) - s(e)*(kk*kk*jpp(l, X(e))))
        if mode == 'inside':  base += V(e)*s(e)*K1(e)
        if mode == 'outside': base += -c*V(e)*s(e)*K1(e)
        return base
    sc = integrate(lambda e: W(e)*abs(s(e))*abs(j(l, X(e))))*kk*kk
    return abs(integrate(f))/max(sc, 1e-30)

grav = max(resid(l, k, 'none')          for l, k in GRID)
ins  = max(resid(l, k, 'inside')        for l, k in GRID)
out1 = max(resid(l, k, 'outside', 1.0)  for l, k in GRID)
out2 = max(resid(l, k, 'outside', 2.0)  for l, k in GRID)
print(f'  worst residual:  grav only {grav:.2e} | inside C_1 {ins:.2e}'
      f' | outside c=alpha {out1:.2e} | outside c=2alpha {out2:.2e}')
allok = (report('C6a  symbolic: inside C_1 is unsatisfiable; outside needs c=alpha',
                ok_sym)
         & report('C6b  c=alpha drives the residual to machine zero', out1 < 1e-11,
                  f'{out1:.1e}')
         & report('C6c  c=2alpha does not', out2 > 1e-6, f'{out2:.1e}'))
finish({'r_grav': grav, 'r_inside': ins, 'r_c_alpha': out1, 'r_c_2alpha': out2})
