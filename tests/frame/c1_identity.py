#!/usr/bin/env python3
"""C1 -- the frame identity and the Sachs-Wolfe invariant.   Audit results 4, 5.

Under u~_a = u_a + w_a, with both sources reduced to potentials,
    Delta(deltaT + Phi_A) = (Delta C_2)',   coefficient exactly 1.
The boost-invariant combination is therefore (deltaT + Phi_A) - C_2', and on
the EdS columns it equals +Phi/3 -- the Sachs-Wolfe combination -- in BOTH
threadings, independent of k and eta.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sympy as sp
from _common import finish, report

eta, k, Phi = sp.symbols('eta k Phi', positive=True)
dT_N, PhiA_N, sig_N = -sp.Rational(2,3)*Phi, Phi, sp.Integer(0)
v = -k*Phi*eta/3
dT_C, PhiA_C, sig_C = sp.Integer(0), sp.Integer(0), -k*v      # a.sigma = -kv
C2_N, C2_C = sp.simplify(-sig_N/k**2), sp.simplify(-sig_C/k**2)

w = sp.Symbol('w')
w_sol = sp.simplify(sp.solve(sp.Eq(sig_C - k*w, sig_N), w)[0])   # from the SHEAR alone
pred  = sp.simplify(sp.diff(w_sol, eta)/k)
meas  = sp.simplify((dT_N+PhiA_N) - (dT_C+PhiA_C))
ok1 = sp.simplify(pred - meas) == 0

inv_C = sp.simplify((dT_C+PhiA_C) - sp.diff(C2_C, eta))
inv_N = sp.simplify((dT_N+PhiA_N) - sp.diff(C2_N, eta))
ok2 = sp.simplify(inv_C - inv_N) == 0
ok3 = sp.simplify(inv_C - Phi/3) == 0
ok4 = k not in inv_C.free_symbols and eta not in inv_C.free_symbols

print(f'  boost from the shear alone      w = {w_sol}')
print(f'  predicted D(deltaT+Phi_A)         = {pred}')
print(f'  measured  D(deltaT+Phi_A)         = {meas}')
print(f'  invariant (deltaT+Phi_A) - C2\'    = {inv_C} (CDM)  {inv_N} (Newtonian)')

allok = (report('C1a  frame law predicts the measured bracket shift', ok1)
         & report('C1b  invariant equal in both threadings', ok2)
         & report('C1c  invariant equals the SW amplitude Phi/3', ok3)
         & report('C1d  invariant is k- and eta-independent', ok4))
finish({'invariant': str(inv_C), 'predicted': str(pred), 'measured': str(meas)})
