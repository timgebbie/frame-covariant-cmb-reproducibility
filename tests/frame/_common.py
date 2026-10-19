"""Shared fixtures for the frame checks.  No project code is imported: every
check is self-contained so it can be run against a fresh checkout."""
import math
from scipy.special import spherical_jn
from scipy.integrate import quad

ETA_STAR, ETA_0 = 0.02, 1.0
SIG, MU = 0.012, 0.035            # a visibility of realistic narrowness

def V(e):                          # visibility, V = kappa' e^-kappa
    return math.exp(-0.5*((e-MU)/SIG)**2)/(SIG*math.sqrt(2*math.pi))
def W(e):                          # W = e^-kappa, Wdot = V, W(eta0)=1, W(0)=0
    return 0.5*(1+math.erf((e-MU)/(SIG*math.sqrt(2))))
def Vdot(e):
    return -(e-MU)/SIG**2 * V(e)

def s(e):                          # boost potential, vanishing at both ends
    return (e-ETA_STAR)**2*(ETA_0-e)**2*(1+0.7*math.sin(5*e))
def sdot(e):
    return ((2*(e-ETA_STAR)*(ETA_0-e)**2 - 2*(e-ETA_STAR)**2*(ETA_0-e))
            *(1+0.7*math.sin(5*e))
            + (e-ETA_STAR)**2*(ETA_0-e)**2*3.5*math.cos(5*e))

def _dfact(n):
    r = 1.0
    while n > 1:
        r *= n; n -= 2
    return r

def j(l, x):  return spherical_jn(l, x)
def jp(l, x): return spherical_jn(l, x, derivative=True)
def jpp(l, x):
    """j_l'' from the spherical Bessel ODE, with the small-x series."""
    if x < 1e-5:
        return l*(l-1)*x**(l-2)/_dfact(2*l+1) if l >= 2 else 0.0
    return (l*(l+1)/x**2 - 1.0)*j(l, x) - 2.0*jp(l, x)/x

def integrate(f, a=ETA_STAR, b=ETA_0, limit=800):
    return quad(f, a, b, limit=limit)[0]

GRID = [(l, k) for l in (2, 3, 5, 10, 20) for k in (20., 80., 200.)]

RESULTS = []

def report(name, holds, detail='', polarity='assert'):
    """polarity='assert'  -- the named statement SHOULD hold; PASS / FAIL.
       polarity='defect'  -- the named statement is a DEFECT that is expected to
                            be present; DEFECT PRESENT / DEFECT GONE.  A defect
                            that has gone fails the suite, because the generated
                            document would otherwise assert a defect that no
                            longer exists and must be regenerated."""
    holds = bool(holds)
    verdict = {'assert': ('PASS', 'FAIL'),
               'defect': ('DEFECT PRESENT', 'DEFECT GONE')}[polarity][not holds]
    print(f'{verdict:<14s}  {name}' + (f'   {detail}' if detail else ''))
    RESULTS.append({'name': name, 'ok': holds, 'verdict': verdict,
                    'polarity': polarity, 'detail': detail})
    return holds

def finish(metrics=None):
    """Emit a machine-readable record and exit non-zero on any FAIL."""
    import json, sys
    rec = {'checks': RESULTS, 'metrics': metrics or {},
           'ok': all(r['ok'] for r in RESULTS)}
    print('##RESULT## ' + json.dumps(rec))
    sys.exit(0 if rec['ok'] else 1)
