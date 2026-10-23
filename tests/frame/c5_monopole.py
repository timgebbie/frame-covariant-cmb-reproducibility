#!/usr/bin/env python3
"""C5 -- the monopole row, and the dipole shift.   Audit results 7, 8.

SUPERSEDED IN ITS CONCLUSION BY T-107, 2026-10-21.  Every measurement below
stands.  What was drawn from them does not: gamma pairs Delta C_0 against
k^2 Delta C_2, and the partner of Delta C_0 is in -C_1' instead -- (107)
carries +(k/3) tau_1 = -a.B_0 already.  So the restoration that drives gamma
to zero counts the monopole source twice and criterion 5b doubles.  The l=0
row is correctly EMPTY of B_0: tau_0 = 0 is a CONSTRAINT, since T is defined
as the monopole of T(x,e), and differentiating it puts a zero on the right.
Only the normalisation is wrong -- B-16.  See c8_rank0_partner.py.

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
piece X with Delta X = 0 passes this check for free.  A missing additive term
of O(k) or lower is invisible where the k^2 piece dominates and dominant where
it does not.  This instrument cannot distinguish that case and nothing here
should be read as excluding one.

**CORRECTED 2026-10-22.**  The sentence above read "Since
C_0 = (1/3) k^2 C_2 + (1/3) k tau_1, ..." -- the RESTORED form, written while
T-105 stood.  T-105 has fallen: tau_0 == 0 is a constraint, not initial data,
so (89)'s ell = 0 row carries ZERO on the right and solves to
C_0 = -(1/3) a.B_2 with no a.B_0 in it.  a.B_0 = -(k/3) tau_1 is an identity
and -C_1' carries +(k/3) tau_1 already, so the restoration double-counts; and
criterion 5b doubles to 98.5% under it (T-107).  The caveat itself is
unaffected -- it is about additive boost-invariant pieces and holds under
either form -- so only the parenthetical justification is withdrawn.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = 'The monopole row and the dipole shift'
AUDIT_PROSE = (
  '$a\\,\\Delta\\mathcal{B}_0=\\tfrac13kv=\\tfrac13k^2\\Delta C_2$ exactly, and '
  '$\\gamma$ -- which pairs $\\Delta C_0$ against $k^2\\Delta C_2$ -- vanishes '
  'only with $\\mathcal{B}_0$ restored. **Both measurements stand and the '
  'conclusion drawn from them was wrong.** Finding **T-107**: the partner of '
  '$\\Delta C_0$ is not in $C_2$ but in $-C_1$\u2032, so $\\gamma$ asks the wrong '
  'pairing, and the restoration that makes it vanish counts the monopole '
  'source twice -- criterion 5b doubles at $98.5\\%$. See **C8**, which scores '
  'the whole rank-0 content of the bracket instead of one coefficient against '
  'another. **M15: a gate built from one coefficient cannot see a '
  'cancellation distributed across the bracket.**')
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
# **C5b and C5c are DEFECT-polarity as of 2026-10-21, finding T-107.**
#
# They asserted that the restored a.B_0 row is the right one, because it is
# the only one giving gamma = 0.  **That measurement is correct and its
# conclusion is refuted**: criterion 5b caught the restoration at 98.5% and
# c8_rank0_partner.py shows why -- gamma pairs Delta C_0 against k^2 Delta C_2
# while the partner sits in -C_1'.  **M15: a gate built from one coefficient
# cannot see a cancellation distributed across the bracket.**
#
# The numbers are kept and the polarity is flipped, so the suite now records
# gamma's misleading zero as a KNOWN DEFECT OF THIS GATE rather than asserting
# its conclusion.  If either ever stops holding, something has changed in the
# gamma pairing and DEFECT GONE will say so -- which is what S33(d) is for.
# **c8 is the gate for the ell=0 row; this is the record of why it had to be.**
allok = (report('C5a  a.Delta B_0 cancels (1/3) k^2 Delta C_2 exactly', ok_cancel)
         & report('C5b  gamma reports zero for the row c8 REFUTES (M15)',
                  gammas[2] == 0, 'the pairing is wrong, not the arithmetic',
                  polarity='defect')
         & report('C5c  and gamma scores it >=10x better than the correct row',
                  r[2]*10 < min(r[0], r[1]),
                  f'{r[2]:.1e} vs {min(r[0],r[1]):.1e} -- see c8, T-107',
                  polarity='defect'))
finish({'gamma_printed': str(gammas[0]), 'gamma_no_B0': str(gammas[1]),
        'gamma_restored': str(gammas[2]), 'r_printed': r[0], 'r_no_B0': r[1],
        'r_restored': r[2]})
