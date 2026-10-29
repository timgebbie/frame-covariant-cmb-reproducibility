#!/usr/bin/env python3
"""C3 -- the exact bulk source, and Annals II's printed form.  Audit results 1, 2.

    W C0 - (W C1)' + (W C2)''  =  W(C0 - C1' + C2'') - V C1 + 2 V C2' + Vdot C2

checked by direct quadrature against the integral it comes from.  Annals II's
`int_soln_damping` is then evaluated AS PRINTED and compared.  Three
discrepancies, in order of size:
  1  visibility-weighted rank-2 slot: correct +2 V C2', printed -2 V C2
  2  sign on V C1: correct -V C1, printed +V C1
  3  a missing lower-limit boundary V(eta*) C2(eta*)
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = 'The bulk source, against the integral it comes from'
AUDIT_PROSE = "The exact bulk source is $W(C_0-C_1'+C_2'')-\\mathcal{V}C_1+2\\mathcal{V}C_2'+\\dot{\\mathcal{V}}C_2$. Annals II's printed `int_soln_damping` does not reproduce its own integral: $+2\\mathcal{V}C_2'$ is printed as $-2\\mathcal{V}C_2$, the sign on $\\mathcal{V}C_1$ is reversed, and a lower-limit boundary $\\mathcal{V}(\\eta_\\ast)C_2(\\eta_\\ast)$ is absent."
import math
from _common import (finish, ETA_STAR as ES, ETA_0 as E0, V, W, Vdot, j, jp, jpp,
                     integrate, report)

C0  = lambda e: 0.7+0.3*math.sin(4*e)
C1  = lambda e: -0.4+0.9*e-0.2*e*e
C1d = lambda e: 0.9-0.4*e
C2  = lambda e: 0.25*math.cos(3*e)+0.5*e
C2d = lambda e: -0.75*math.sin(3*e)+0.5
C2dd= lambda e: -2.25*math.cos(3*e)

def columns(l, k):
    X  = lambda e: k*(E0-e)
    K  = lambda e: j(l, X(e))
    K1 = lambda e: -k*jp(l, X(e))            # d/deta'
    K2 = lambda e: k*k*jpp(l, X(e))
    direct = integrate(lambda e: W(e)*(C0(e)*K(e)+C1(e)*K1(e)+C2(e)*K2(e)))
    Ks, K1s, Ws, Vs = K(ES), K1(ES), W(ES), V(ES)
    bdry = (C2d(ES)-C1(ES))*Ws*Ks - C2(ES)*Ws*K1s
    grp  = integrate(lambda e: W(e)*(C0(e)-C1d(e)+C2dd(e))*K(e))
    vdot = integrate(lambda e: Vdot(e)*C2(e)*K(e))
    printed = bdry + grp + integrate(lambda e: V(e)*(C1(e)-2*C2(e))*K(e)) + vdot
    derived = (bdry + Vs*C2(ES)*Ks + grp
               + integrate(lambda e: V(e)*(-C1(e)+2*C2d(e))*K(e)) + vdot)
    return direct, printed, derived

wd = wp = 0.0
print(f'  {"l":>3s} {"k":>5s} {"direct":>13s} {"derived err":>12s} {"printed err":>12s}')
for l in (2, 3, 5, 10, 20):
    for k in (20., 80., 200.):
        a, p, c = columns(l, k); sc = max(abs(a), 1e-30)
        wd = max(wd, abs(c-a)/sc); wp = max(wp, abs(p-a)/sc)
        if k == 80.:
            print(f'  {l:3d} {k:5.0f} {a:13.5e} {abs(c-a)/sc:12.2e} {abs(p-a)/sc:12.2e}')
print(f'  worst over 15 (l,k):  derived {wd:.2e}   printed {wp:.2e}')
allok = (report('C3a  four-term bulk source reproduces the integral', wd < 1e-8,
                f'worst {wd:.1e}')
         & report('C3b  Annals II printed int_soln_damping does not reproduce '
                  'its own integral', wp > 1e-2, f'worst relative error {wp:.1e}',
                  polarity='defect'))
finish({'worst_derived': wd, 'worst_printed': wp})
