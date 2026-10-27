"""Shared fixtures for the frame checks.  No project code is imported: every
check is self-contained so it can be run against a fresh checkout.

THE INDEPENDENCE IS NOW CHECKED RATHER THAN ASSERTED.  Added 2026-10-27.

Until today the claim rested on the `-I` flag in `run_all.py` and in
`tests/test_frame_checks.py`.  `-I` implies `-E`, so PYTHONPATH is ignored,
and implies `-P`, which is why every instrument carries its own
`sys.path.insert` for this module.  BUT A PROPERTY THAT HOLDS BECAUSE OF AN
INVOCATION FLAG HOLDS ONLY WHILE SOMEBODY REMEMBERS THE FLAG, and the first
time the suite is run without it -- to reach an interpreter where the
dependencies happen to be installed, say -- the independence goes silently and
every check still prints PASS.  That is the project's oldest failure mode: a
green check looking at the wrong object.

So the guard below asserts the PROPERTY and not the MECHANISM.  No directory
of the bundle outside `tests/frame/` may be reachable on `sys.path`, and
nothing from the bundle outside `tests/frame/` may have been imported.  It
exits 2 before any check runs, because a suite that cannot show its
independence must not produce a result that implies it.  `CLAUDE.md` 3c,
applied to the instrument's own warrant.

THE PRACTICAL CONSEQUENCE, which is why this is not merely tidy: running the
suite WITHOUT `-I` is now safe, and it is the way out when the dependencies
sit in a user site-packages directory that `-I` is designed to ignore.  The
flag stays, because defence in depth costs nothing; the guard is what the
claim now rests on.
"""
import os
import sys
import pathlib

_HERE = pathlib.Path(__file__).resolve().parent          # tests/frame
_ROOT = _HERE.parents[1]                                 # the bundle root


def _independence_violations():
    """Bundle directories on sys.path, and bundle modules already imported.

    Named by PATH rather than by module name, so a module renamed or added in
    the solver cannot slip past a hard-coded list.  `tests/frame` itself is
    exempt: that is this file.
    """
    bad_path, bad_mod = [], []
    for entry in sys.path:
        if not entry:
            continue
        try:
            p = pathlib.Path(entry).resolve()
        except (OSError, ValueError):
            continue
        if p == _HERE or not p.is_dir():
            continue
        if p == _ROOT or _ROOT in p.parents:
            bad_path.append(str(p))
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, '__file__', None)
        if not f:
            continue
        try:
            p = pathlib.Path(f).resolve()
        except (OSError, ValueError):
            continue
        if _HERE in p.parents or p.parent == _HERE:
            continue
        if _ROOT in p.parents:
            bad_mod.append(f'{name} ({p})')
    return bad_path, bad_mod


_BAD_PATH, _BAD_MOD = _independence_violations()
INDEPENDENT = not (_BAD_PATH or _BAD_MOD)

if not INDEPENDENT and not os.environ.get('FRAME_ALLOW_PROJECT_IMPORTS'):
    print('INDEPENDENCE VIOLATED -- no check has run.', file=sys.stderr)
    for e in _BAD_PATH:
        print(f'  bundle directory on sys.path: {e}', file=sys.stderr)
    for e in _BAD_MOD:
        print(f'  bundle module imported:        {e}', file=sys.stderr)
    print('These instruments establish that the frame conditions hold in a '
          'construction\nthey build themselves. Reachable project code makes '
          'a PASS unfalsifiable,\nso the suite refuses to report one.',
          file=sys.stderr)
    sys.exit(2)

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
    """Emit a machine-readable record and exit non-zero on any FAIL.

    The record carries the independence status, so a run made with the
    override open is marked in the record and therefore in the generated
    `docs/THEORY-AUDIT.md`.  An escape hatch is allowed; a silent one is not.
    """
    import json, sys
    rec = {'checks': RESULTS, 'metrics': metrics or {},
           'independent': INDEPENDENT,
           'isolated_interpreter': bool(sys.flags.isolated),
           'ok': all(r['ok'] for r in RESULTS) and INDEPENDENT}
    if not INDEPENDENT:
        rec['independence_violations'] = {'sys_path': _BAD_PATH,
                                          'imported': _BAD_MOD}
    print('##RESULT## ' + json.dumps(rec))
    sys.exit(0 if rec['ok'] else 1)
