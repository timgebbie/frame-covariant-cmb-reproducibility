#!/usr/bin/env python3
"""C9 -- the admissibility of the by-parts, and the cancellation it protects.

WRITTEN 2026-10-26 BY THE PAPER 1 THEORY STREAM, after the first-peak budget
showed that half the peak displacement was an artefact of this one operation.
It is the gate that B-17 (iv), T-94 and T-101 each needed and none had.

THE STATEMENT.  (90) gives

    -C_1 = (a.B_1 + kappa' v_B)/k = (dT + Phi_A) + kappa' vhat_B ,

two objects of different kinds.  Write them as C1g (gravitational, a GRADIENT
in the 1+3 formulation, since a.B_1 = k(dT + Phi_A) and B_a = D_a ln T + A_a)
and C1s (scattering, ALREADY a rate times an amplitude).

    W . C1s  =  V . vhat_B / k                    <-- the Doppler source.
                                                      Bounded.  int V = 1.

SO (90) IS NOT A DEFECT.  The rate is inside the coefficient precisely so that
W.C1 delivers V, and C1 sits at K' = -k j_l', which is the Doppler kernel.
The construction is correct.  WHAT IS WRONG IS ONE OPERATION.

THE CANCELLATION.  The exact rank-1 bulk is -(W C1)' = -(W' C1 + W C1').  On
the scattering half the two terms carry, with r = V/W the scattering rate:

    W' C1s  ~  r^2        (differentiating the WEIGHT)
    W C1s'  ~  r'         (differentiating the COEFFICIENT)

and they are the two halves of d(V.vhat_B)/d-eta, which is bounded and
integrates to a boundary difference.  INDIVIDUALLY THEY ARE ENORMOUS AND THEY
CANCEL.

WHAT (102) DOES.  It carries V(C_0 - C_1' + C_2'') -- the weight OUTSIDE, the
derivative INSIDE -- and drops W'C_1 entirely.  Against the exact form that is
two departures on one slot:

    W C1s'   ->   V C1s'      a factor of EXACTLY r too large
    W' C1s   ->   absent      the partner that would have cancelled it

THE CANCELLATION IS DESTROYED FROM BOTH SIDES IN ONE OPERATION.  One half is
scaled so it can no longer cancel; the other is deleted so it cannot try.

AND THE SAME OPERATION DOES TWO MORE THINGS.  By-parting C1s at all moves the
Doppler term out of the j_l' slot (B-17 (iv) -- not a term missing from (102)
but a term (102) REMOVED) and carries r.vhat_B into the boundary beside the
Sachs-Wolfe combination (T-101, T-121 -- the l~7 plateau bump).

THE ADMISSIBILITY CONDITION, which is what this check asserts:

    A COEFFICIENT MAY BE CARRIED THROUGH AN INTEGRATION BY PARTS ONLY IF IT
    IS FREE OF RATES.

C_1 is not, by (90).  Therefore the by-parts may be applied to C1g and may
not be applied to C1s.  C9d is that condition evaluated: the SPLIT assembly
reproduces the ancestor exactly, and produces no r' term at all.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = 'The admissibility of the by-parts, and the cancellation it protects'
AUDIT_PROSE = (
  "Equation~(90) places the Thomson rate inside $C_1$ so that $WC_1$ is the "
  "bounded Doppler source $\\mathcal{V}\\hat v_B/k$ at the kernel $K'=-kj_\\ell'$; "
  "the construction is correct. The exact rank-one bulk $-(WC_1)'$ splits into "
  "$W'C_1\\sim\\kappa'^2$ and $WC_1'\\sim\\kappa''$, which are the two halves of "
  "$\\mathrm{d}(\\mathcal{V}\\hat v_B)/\\mathrm{d}\\eta$ and cancel. (102) carries "
  "$\\mathcal{V}C_1'$ in place of $WC_1'$ --- larger by exactly $\\kappa'$ --- and "
  "drops $W'C_1$ altogether, destroying the cancellation from both sides in one "
  "operation; the same operation empties the $j_\\ell'$ slot and carries "
  "$\\kappa'\\hat v_B$ into the boundary. The admissibility condition is that a "
  "coefficient may be carried through an integration by parts only if it is free "
  "of rates."
)

import math
from _common import (finish, report, integrate, j, jp, jpp,
                     ETA_STAR as ES, ETA_0 as E0, V, W, Vdot)

# --------------------------------------------------------------------------
# the rate, r = |d kappa / d eta| = V / W, and its derivative
# --------------------------------------------------------------------------
def r(e):    return V(e)/W(e)
def rdot(e): return (Vdot(e)*W(e) - V(e)*V(e))/(W(e)*W(e))

# the two halves of C_1, per (90).  vhat_B is the baryon velocity, smooth.
def vB(e):   return 0.6*math.sin(3.0*e) + 0.25*e
def vBd(e):  return 1.8*math.cos(3.0*e) + 0.25

K_WAVE = 80.0
def C1g(e):  return -(0.7 + 0.3*math.sin(4.0*e))          # -(dT + Phi_A)
def C1gd(e): return -(1.2*math.cos(4.0*e))
def C1s(e):  return -r(e)*vB(e)/K_WAVE                     # -kappa' vhat_B / k
def C1sd(e): return -(rdot(e)*vB(e) + r(e)*vBd(e))/K_WAVE
def C1(e):   return C1g(e) + C1s(e)
def C1d(e):  return C1gd(e) + C1sd(e)

# --------------------------------------------------------------------------
# C9a  the two large pieces are equal and opposite and cancel into a bounded
#      total derivative:  W'C1s + W C1s'  ==  d(W C1s)/d-eta  ==  (V vB)'/k
# --------------------------------------------------------------------------
SAMPLE = [ES + (E0-ES)*t for t in (0.001, 0.005, 0.02, 0.05, 0.12, 0.3, 0.6, 0.9)]

worst_sum, worst_ratio = 0.0, 0.0
_H = ('eta', 'r = |kappa1|', 'W1.C1s', 'W.C1s1', 'sum', 'cancel x')
print('  %7s %13s %13s %13s %13s %10s' % _H)
for e in SAMPLE:
    a = V(e)*C1s(e)                      # W' C1s   -- carries r^2
    b = W(e)*C1sd(e)                     # W  C1s'  -- carries r'
    exact = (Vdot(e)*vB(e) + V(e)*vBd(e))/K_WAVE   # d(V vB)/d-eta / k
    # (W C1s)' = W'C1s + W C1s' ; and W C1s = -V vB / k, so the sum is -exact
    resid = abs(a + b + exact)/max(abs(a), abs(b), 1e-30)
    worst_sum = max(worst_sum, resid)
    cancel = max(abs(a), abs(b))/max(abs(a+b), 1e-300)
    worst_ratio = max(worst_ratio, cancel)
    print(f'  {e:7.4f} {r(e):13.4e} {a:13.4e} {b:13.4e} {a+b:13.4e} {cancel:10.2e}')

ok_a = report('C9a  W\'C1s and W C1s\' are the two halves of d(V.vhat_B)/d-eta '
              'and cancel', worst_sum < 1e-9,
              f'worst residual {worst_sum:.1e}; largest cancellation '
              f'{worst_ratio:.1e}x')

# --------------------------------------------------------------------------
# C9b  (102) carries V C1s' where the exact form carries W C1s'.
#      The ratio is EXACTLY the scattering rate r, pointwise.
# --------------------------------------------------------------------------
worst_rat_err, peak_rate = 0.0, 0.0
for e in SAMPLE:
    exact_piece = W(e)*C1sd(e)
    used_piece  = V(e)*C1sd(e)
    if abs(exact_piece) > 1e-300:
        worst_rat_err = max(worst_rat_err, abs(used_piece/exact_piece - r(e))/max(r(e), 1e-30))
    peak_rate = max(peak_rate, r(e))
ok_b = report('C9b  (102) carries V.C1\' where the exact form carries W.C1\'; '
              'the ratio is exactly the scattering rate',
              worst_rat_err < 1e-12,
              f'worst deviation from r {worst_rat_err:.1e}; peak r {peak_rate:.1f}')

# --------------------------------------------------------------------------
# C9c  the partner W'C1s is what (102) drops, and it is the LARGER half.
#      Measure what the bulk becomes without it, at the released weight.
# --------------------------------------------------------------------------
def X(e):  return K_WAVE*(E0-e)
def Kk(l, e):  return j(l, X(e))
def K1(l, e):  return -K_WAVE*jp(l, X(e))

worst_blow = 0.0
print('\n  %3s %16s %16s %12s' % ('l', 'exact -(W.C1s)1', '(102) V.C1s1', 'ratio'))
for l in (2, 3, 5, 10, 20):
    exact = integrate(lambda e: -(V(e)*C1s(e) + W(e)*C1sd(e))*Kk(l, e))
    used  = integrate(lambda e: V(e)*(-C1sd(e))*Kk(l, e))
    ratio = abs(used)/max(abs(exact), 1e-300)
    worst_blow = max(worst_blow, ratio)
    print(f'  {l:3d} {exact:16.5e} {used:16.5e} {ratio:12.3e}')
ok_c = report('C9c  (102)\'s rank-1 scattering bulk exceeds the exact one by the '
              'scattering rate', worst_blow > 10.0,
              f'worst factor {worst_blow:.1f}x', polarity='defect')

# --------------------------------------------------------------------------
# C9d  THE ADMISSIBILITY CONDITION, EVALUATED.  The split assembly --
#      by-parts C1g, leave C1s at K' -- reproduces the ancestor exactly.
# --------------------------------------------------------------------------
worst_split = 0.0
print('\n  %3s %15s %15s %11s' % ('l', 'ancestor', 'split assembly', 'rel err'))
for l in (2, 3, 5, 10, 20):
    ancestor = integrate(lambda e: W(e)*C1(e)*K1(l, e))
    # by-parts the gravitational half only; leave the scattering half at K'
    bdry  = W(E0)*C1g(E0)*Kk(l, E0) - W(ES)*C1g(ES)*Kk(l, ES)
    bulk  = integrate(lambda e: -(V(e)*C1g(e) + W(e)*C1gd(e))*Kk(l, e))
    dopp  = integrate(lambda e: W(e)*C1s(e)*K1(l, e))
    split = bdry + bulk + dopp
    rel = abs(split-ancestor)/max(abs(ancestor), 1e-30)
    worst_split = max(worst_split, rel)
    print(f'  {l:3d} {ancestor:15.6e} {split:15.6e} {rel:11.2e}')
ok_d = report('C9d  the split by-parts -- gravitational half by-parted, '
              'scattering half left at K\' -- reproduces the ancestor',
              worst_split < 1e-8, f'worst {worst_split:.1e}')

# --------------------------------------------------------------------------
# C9e  and it produces no r' term at all.  Structural: the split assembly's
#      integrand is built from C1g, C1gd and C1s -- never C1sd -- so rdot
#      cannot appear.  Evaluated by perturbing rdot and showing the split
#      assembly does not move while (102)'s form does.
# --------------------------------------------------------------------------
def split_val(l, bump):
    bdry = W(E0)*C1g(E0)*Kk(l, E0) - W(ES)*C1g(ES)*Kk(l, ES)
    bulk = integrate(lambda e: -(V(e)*C1g(e) + W(e)*C1gd(e))*Kk(l, e))
    dopp = integrate(lambda e: W(e)*C1s(e)*K1(l, e))
    return bdry + bulk + dopp          # bump cannot enter: no C1sd anywhere

def printed_val(l, bump):
    return integrate(lambda e: V(e)*(-(C1gd(e)
                     + -(rdot(e)*(1.0+bump)*vB(e) + r(e)*vBd(e))/K_WAVE))*Kk(l, e))

worst_split_move, worst_printed_move = 0.0, 0.0
for l in (2, 5, 20):
    s0, s1 = split_val(l, 0.0), split_val(l, 0.10)
    p0, p1 = printed_val(l, 0.0), printed_val(l, 0.10)
    worst_split_move   = max(worst_split_move,   abs(s1-s0)/max(abs(s0), 1e-30))
    worst_printed_move = max(worst_printed_move, abs(p1-p0)/max(abs(p0), 1e-30))
print('\n  a 10%% perturbation of kappa2:  split moves %.1e,  (102) moves %.1e'
      % (worst_split_move, worst_printed_move))
ok_e = report('C9e  the split assembly contains no kappa\'\' term; (102)\'s does',
              worst_split_move < 1e-14 and worst_printed_move > 1e-3,
              f'split {worst_split_move:.1e} vs printed {worst_printed_move:.1e}')

finish({'worst_cancellation_residual': worst_sum,
        'largest_cancellation_factor': worst_ratio,
        'worst_rate_ratio_deviation': worst_rat_err,
        'peak_scattering_rate': peak_rate,
        'worst_bulk_inflation': worst_blow,
        'worst_split_residual': worst_split,
        'split_sensitivity_to_kappa2': worst_split_move,
        'printed_sensitivity_to_kappa2': worst_printed_move})
