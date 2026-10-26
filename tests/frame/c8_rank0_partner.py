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

ADDENDUM 2026-10-26, AND IT IS A CONTROL AGAINST A CONFUSION THAT HAS NOW
HAPPENED.  Finding T-148 scored "C_0 and its putative partner (k/3) tau_1" and
reported that they have the SAME SIGN on every background at every k, sum
1.09-1.23 x C_0 rather than zero.  Both halves of that measurement are right
and the pairing it tests is not the pairing this check asserts.

  what C8 asserts :  Delta C_0  +  Delta[(k/3) tau_1]  =  0     -- two SHIFTS
  what T-148 scored:  Delta C_0  vs       (k/3) tau_1           -- a SHIFT
                                                                   against a
                                                                   VALUE

The first is exact and needs ONLY the boost law Delta tau_1 = -v: it holds for
any tau_1 whatever, because tau_1's own value never enters.  The second is a
statement about the SOLUTION -- whether the dipole satisfies tau_1 = -v -- and
nothing in the frame law requires that.  T-148 measures tau_1 -> +0.18 v at
superhorizon scales, which is a fact about the dipole and not a failure of this
cancellation.

C_0 AND (k/3) tau_1 ARE NOT TWO SOURCES TO BE SUMMED.  C_0 = -(1/3) a.B_2 is
the ell=0 PROJECTION OF THE RANK-2 SOURCE, through j_0''(0) = -1/3 -- the
quadrupole leaking into the monopole slot.  (k/3) tau_1 = -a.B_0 is the
physical rank-0 SOURCE, and it is already inside the bracket, in -C_1'.  A
leakage term and a source term have no reason to cancel in value.  Their frame
SHIFTS do, and that is what makes the bracket frame-consistent at rank zero.

C8f below is the negative control: it shows the shift cancellation survives
arbitrary values of a.B_2 and tau_1, and that the value sum does not vanish and
is not required to.
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
  '5b caught at $98.5\\%$ and no frame instrument could. '
  '**Addendum 2026-10-26.** Finding T-148 scored $C_0$ against $\\tfrac k3\\tau_1$ '
  'and found they do not cancel; both halves of that measurement are right and '
  'the pairing is not this one. What cancels is $\\Delta C_0+\\Delta[\\tfrac k3\\tau_1]$, '
  'two **shifts**, exactly and for any $\\tau_1$ whatever, because only the boost '
  'law $\\Delta\\tau_1=-v$ enters. $C_0$ is the rank-2 source leaking into $\\ell=0$ '
  'through $j_0\'\'(0)=-\\tfrac13$; $\\tfrac k3\\tau_1$ is the rank-0 source itself. '
  'A leakage term and a source term have no reason to cancel in value, and '
  '$\\tau_1\\to+0.18v$ at superhorizon scales is a fact about the dipole, not a '
  'failure of this cancellation.')

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

# ---- C8f: the SHIFT pairing is independent of the VALUES; the value pairing
# ---- does not vanish and is not required to.  Control against T-148's class.
B2v, T1v = sp.symbols('aB2_value tau1_value')      # arbitrary values
shift_sum_free = sp.simplify(sp.Rational(-1,3)*dB2 + partner)   # uses only the boost law
value_sum_free = sp.simplify(sp.Rational(-1,3)*B2v + sp.Rational(1,3)*k*T1v)
print()
print(f'  SHIFT pairing, for ARBITRARY a.B_2 and tau_1 values : {shift_sum_free}')
print(f'  VALUE pairing, same symbols                         : {value_sum_free}')
# T-148's own EdS numbers at k = 10, read back
dC0_measured, src_measured = -21.61, -3.805
print(f'  T-148 at EdS k=10:  Delta C_0 = {dC0_measured}  (a shift),'
      f'  (k/3)tau_1 = {src_measured}  (a value)')
print(f'                      implied v = {3*dC0_measured/10:.4f},'
      f'  tau_1 = {3*src_measured/10:.4f},  tau_1/v = {src_measured/dC0_measured:.4f}')
allok = (allok
  & report('C8f  the shift cancellation is independent of the values',
           shift_sum_free == 0,
           'holds for any a.B_2 and any tau_1: only the boost law enters')
  & report('C8g  the VALUE pairing does not vanish, and is not required to',
           sp.simplify(value_sum_free) != 0,
           'C_0 is the rank-2 leakage at ell=0, (k/3)tau_1 is the rank-0 source; '
           'T-148 scored a shift against a value'))

finish({'shift_printed': str(sp.nsimplify(A/(k*v))),
        'shift_alpha0_no_B0': str(sp.nsimplify(B/(k*v))),
        'shift_alpha0_with_B0': str(sp.nsimplify(C/(k*v))),
        'r_printed': r[0], 'r_alpha0_no_B0': r[1], 'r_alpha0_with_B0': r[2],
        'shift_pairing_free_of_values': str(shift_sum_free),
        'value_pairing': str(value_sum_free),
        't148_tau1_over_v': src_measured/dC0_measured})
