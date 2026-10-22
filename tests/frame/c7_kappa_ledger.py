#!/usr/bin/env python3
"""C7 -- the kappa' ledger.   P1-T, 2026-10-20.

Multiplying the transport equation by the integrating factor W = e^-kappa:

    tau_l' + (streaming) + kappa' tau_l  =  a B_l + kappa' S_l
    d/deta[W tau_l] + W(streaming)       =  W a B_l + (W kappa') S_l
                                                      ~~~~~~~~~~~
                                                         = V

The gravitational source arrives under W.  The in-scattered Thomson source
arrives under V, its kappa' already consumed by the integrating factor.

    >>> THE RULE <<<   kappa' may live in W, in V, or in a derivative of
    either.  It may NEVER live in a coefficient.  A coefficient carrying a
    bare kappa' manufactures kappa'^2 the moment it is differentiated.

This distinguishes the legitimate kappa'^2 -- inside Vdot = (kappa''+kappa'^2)W,
which comes from differentiating the WEIGHT -- from the illegitimate one, which
comes from differentiating a COEFFICIENT.  Both look like kappa'^2 in the
output; only one is allowed.

Checked against three assemblies: the W-form, Annals II (102) as printed, and
T-88's withdrawn slot_weight_split.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = "The $\\kappa'$ ledger"
AUDIT_PROSE = "Multiplying the transport equation by $W=e^{-\\kappa}$ sends the gravitational source to $W$ and the in-scattered Thomson source to $\\mathcal V=W\\kappa'$, its $\\kappa'$ consumed by the integrating factor. **This is a REVIEW FLAG, not a prohibition --- revised 2026-10-21, finding T-113 and decision S48.** It read *``$\\kappa'$ may live in $W$, in $\\mathcal V$, or in a derivative of either --- never in a coefficient''* and was taken as normative. **It is not a theorem**: $W(\\kappa'S)=\\mathcal VS$ is exact, so a coefficient may hold $\\kappa'$. The defect in (102) is wrong weights, signs, boundaries or missing partners --- which **C3b** measures at $2.6$ --- not the presence of $\\kappa'$. The flag is kept because it is cheap and every assembly that failed this month trips it; what it may no longer do is settle a question on its own. Note also that $\\kappa''=-\\kappa'^2$ holds **at the visibility maximum**, where $\\dot{\\mathcal V}=0$, so *``three powers of $\\kappa'$''* is a local statement and not a general one."
import sympy as sp
from _common import report, finish

eta = sp.Symbol('eta')
kp  = sp.Function('kprime')(eta)              # kappa'
W   = sp.Function('W')(eta)                   # e^-kappa
V   = kp*W                                    # visibility, = W'
B1  = sp.Function('B1')(eta)                  # gravitational rank-1, kappa'-free
S1  = sp.Function('vhatB')(eta)               # Thomson rank-1, kappa'-free
tau0= sp.Function('tau0')(eta)

def coeff_carries_kappa(expr):
    """True if the COEFFICIENT (weight stripped) contains kappa'."""
    return kp in expr.atoms(sp.Function)

def kappa_power(expr):
    e = sp.expand(sp.simplify(expr))
    sub = {sp.Derivative(kp, eta): sp.Symbol('kpp'), W: sp.Symbol('W0'),
           B1: sp.Symbol('b1'), S1: sp.Symbol('s1'), tau0: sp.Symbol('t0'),
           sp.Derivative(B1, eta): sp.Symbol('b1p'),
           sp.Derivative(S1, eta): sp.Symbol('s1p'),
           sp.Derivative(W, eta): sp.Symbol('W0')*sp.Symbol('kp')}
    e = e.subs(sub).subs(kp, sp.Symbol('kp'))
    try:
        return sp.Poly(e, sp.Symbol('kp')).degree()
    except sp.PolynomialError:
        return -1

# ---- the three assemblies, as (name, weight, coefficient, slot) -----------
ASSEMBLIES = {
 'W-form (P1-T, 2026-10-20)': [
    ('grav rank-1',    W,  B1,            "K'"),
    ('Thomson rank-1', V,  S1,            "K'"),
    ('Thomson rank-0', V,  tau0,          'K'),
 ],
 'Annals II (102) as printed': [
    ('bracket -C1\'',  V,  -sp.diff(-kp*S1 + B1, eta), 'K'),
 ],
 'T-88 slot_weight_split (withdrawn)': [
    ('Thomson, V-wt',  V,  -kp*S1,        "K'"),
 ],
}

print("  rule: kappa-prime may live in W, V or a derivative of either --")
print("        NEVER in a coefficient.\n")
hdr = ('assembly'.ljust(36), 'term'.ljust(16), 'coeff has kp'.rjust(13),
       'kp power'.rjust(9))
print('  ' + ' '.join(hdr))
verdicts = {}
for name, terms in ASSEMBLIES.items():
    clean = True
    for tname, wt, co, slot in terms:
        bad = coeff_carries_kappa(co)
        pw  = kappa_power(wt*co)
        clean &= not bad
        print(f'  {name:36s} {tname:16s} {"YES" if bad else "no":>13s} {pw:>9d}')
    verdicts[name] = clean

allok = (report('C7a  the W-form keeps every kappa-prime in the weight',
                verdicts['W-form (P1-T, 2026-10-20)'])
       & report('C7b  (102) as printed carries kappa-prime in a coefficient',
                not verdicts['Annals II (102) as printed'],
                'differentiating it gives kappa-prime squared', polarity='defect')
       & report('C7c  T-88 carries kappa-prime in a coefficient',
                not verdicts['T-88 slot_weight_split (withdrawn)'],
                'measured 320-682x by P1-B', polarity='defect'))

print()
print('  legitimate vs illegitimate kappa-prime squared:')
print('    Vdot = d/deta[V]                 -> power '
      + str(kappa_power(sp.diff(V, eta))) + '   (from the WEIGHT -- allowed)')
print('    V * d/deta[-kappa-prime vhatB]   -> power '
      + str(kappa_power(-V*sp.diff(-kp*S1, eta))) + '   (from a COEFFICIENT -- not)')
finish({'w_form_clean': verdicts['W-form (P1-T, 2026-10-20)'],
        'printed_102_clean': verdicts['Annals II (102) as printed'],
        't88_clean': verdicts['T-88 slot_weight_split (withdrawn)']})
