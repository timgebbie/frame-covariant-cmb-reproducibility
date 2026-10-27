#!/usr/bin/env python3
"""C10 -- the oscillator's phase at the boundary, and the criterion that is
blind to it.   P1-T, 2026-10-26.

WHY THIS EXISTS.  The acceptance criterion carried for the acoustic step is
that (delta-T + Phi_A)(eta_*) tracks cos(k r_s) IN EXACT PHASE, and passing it
has been reported as evidence that the acoustic physics is right.  A DRIVEN
oscillator does not track cos(k r_s).  It tracks cos(k r_s + phi), and that
phase is the radiation-era driving.  SO THE CRITERION, AS STATED, PASSES ONLY
WHEN THE DRIVING IS ABSENT and fails any calculation that carries it.  The
step that should have caught approximation A-3 certifies that A-3 is gone.

That is C10d below, and it is the point of the file.  The first-peak budget
puts the driving at d(phi_1) = +0.1124, the same size as the artefact half, so
this is not a small omission.

THE TWO HALVES AGREE TO 2.0 PER CENT ONLY AGAINST THE MEASURED artefact-
suppressed midpoint l = 236.6.  Against the PREDICTED undriven position
0.852 l_A = 231.9 they are +0.1275 and +0.0951 and agree to 29 per cent.  The
equality is a measured coincidence at one midpoint and not a derived result,
and this file asserts neither number -- the budget is cited here only for the
size of what the criterion cannot see.

WHAT IS ASSERTED HERE, AND WHAT IS NOT.

  ANALYSIS.  Eliminating tau-tilde_1 between Annals II (152) and (153) returns
  the oscillator with c_s^2 = 1/(3(1+R)) exactly and the standard baryon-drag
  coefficient R'/(1+R).  Nothing is imported to get it.  That is C10a and it
  needs no measurement.

  DEMONSTRATION.  The oscillator is then integrated on two potentials of this
  file's own construction -- one constant, one decaying -- and the phase of
  (delta-T + Phi) against cos(k c_s eta) is read off at the boundary.  THIS IS
  NOT A MODEL OF THE RADIATION ERA.  The decaying form here falls at
  x = k eta / sqrt(3), so for large k it has decayed before the mode has
  oscillated appreciably and the measured phase falls as 1/k.  In the real
  case the decay is tied to equality rather than to k, and persists through
  several oscillations for modes entering well inside radiation domination.
  WHAT THE DEMONSTRATION ESTABLISHES is the mechanism and its sign -- a
  time-dependent potential puts a phase into the boundary value and a constant
  one does not -- NOT the magnitude of that phase in this bundle.

  NO PROJECT CODE IS IMPORTED.  The potentials, the oscillator and the
  integration are built here, so this file cannot agree with `solve_acoustic`
  by construction.

THE EINSTEIN-DE SITTER NULL.  On K = 0 dust Omega_r = 0 and Phi is constant,
so the driving CANNOT ACT and the phase must be exactly zero.  That is the
control which separates a driving mechanism from a fit: any repair that moves
the peak must leave the Einstein-de Sitter phase at zero.  C10b is that null
evaluated.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = 'The oscillator phase, and the criterion that cannot see it'
AUDIT_PROSE = (
  "Eliminating $\\tilde\\tau_1$ between \\emph{Annals~II} (152) and (153) returns "
  "$\\delta\\tilde T''+\\frac{R'}{1+R}\\delta\\tilde T'+k^2c_s^2\\delta\\tilde T="
  "-\\frac{k^2}{3}\\Phi_A-\\mathcal F$ with $c_s^2=1/[3(1+R)]$ exactly. With "
  "$\\Phi$ constant the boundary value $(\\delta\\tilde T+\\Phi_A)(\\eta_\\ast)$ is a "
  "pure cosine of amplitude $\\Phi/3$ and its phase is zero; with $\\Phi$ "
  "time-dependent the phase is non-zero. The released acceptance criterion "
  "asks that the oscillator track $\\cos(kr_s)$ in exact phase, so it accepts "
  "the undriven solution and rejects the driven one: the step that should "
  "have caught approximation **A-3** certifies its absence. On Einstein--de~Sitter "
  "$\\Omega_r=0$ and the phase must be exactly zero, which is the control that "
  "separates a driving mechanism from a fit."
)

import math
import sympy as sp
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import spherical_jn
from _common import finish, report

# ---------------------------------------------------------------------------
# C10a  ANALYSIS.  (152) and (153) eliminate to the oscillator, c_s^2 exact.
# ---------------------------------------------------------------------------
eta, kk = sp.symbols('eta k', positive=True)
R   = sp.Function('R')(eta)
dT  = sp.Function('deltaT')(eta)
PhA = sp.Function('Phi_A')(eta)
PhH = sp.Function('Phi_H')(eta)
aH  = sp.Function('aH')(eta)

tau1 = sp.simplify(3*(sp.diff(dT, eta) + aH*PhA + sp.diff(PhH, eta))/kk)   # (153)
osc  = sp.expand((kk/3)*(sp.diff(tau1, eta)                                # (152)
                         + sp.diff(R, eta)/(1+R)*tau1
                         + kk/(1+R)*dT + kk*PhA))
c_dT   = sp.simplify(osc.coeff(dT))
c_dTp  = sp.simplify(osc.coeff(sp.diff(dT, eta)))
cs2    = sp.simplify(c_dT/kk**2)
ok_a = report('C10a  (152)+(153) give the oscillator with c_s^2 = 1/(3(1+R))',
              sp.simplify(cs2 - 1/(3*(1+R))) == 0
              and sp.simplify(c_dTp - sp.diff(R, eta)/(1+R)) == 0,
              f'c_s^2 = {cs2}, drag = {c_dTp}')

# ---------------------------------------------------------------------------
# The construction.  R = 0, so c_s^2 = 1/3 exactly and r_s = c_s eta.
# Adiabatic start at rest: delta-T + Phi = Phi/3, which is the Sachs-Wolfe
# value, so the undriven amplitude is an analytic number and C10e can score it.
# ---------------------------------------------------------------------------
CS, ETA_B = 1/math.sqrt(3.0), 1.0
KS = (20., 50., 100., 200., 400., 800.)

def phi_constant(e, k):
    """Einstein-de Sitter: K = 0 dust, Omega_r = 0, Phi constant to 1e-13."""
    return 1.0

def phi_decaying(e, k):
    """A potential that decays inside the sound horizon.  NOT a model of the
    radiation era: see the docstring.  3 j_1(x)/x with x = k eta / sqrt(3)."""
    x = k*e/math.sqrt(3.0)
    return 3.0*spherical_jn(1, x)/x if x > 1e-8 else 1.0

def boundary(k, phi):
    """Phase and amplitude of (delta-T + Phi) against cos(k c_s eta) at eta_B."""
    def rhs(e, y):
        return [y[1], -k*k*CS*CS*y[0] - (k*k/3.0)*phi(e, k)]
    y0 = [-(2.0/3.0)*phi(1e-9, k), 0.0]
    s = solve_ivp(rhs, (1e-9, ETA_B), y0, rtol=1e-12, atol=1e-14, dense_output=True)
    y  = s.sol(ETA_B)[0] + phi(ETA_B, k)
    dy = s.sol(ETA_B)[1] + (phi(ETA_B+1e-6, k) - phi(ETA_B-1e-6, k))/2e-6
    ph = math.atan2(-dy/(k*CS), y) - k*CS*ETA_B
    return (ph + math.pi) % (2*math.pi) - math.pi, math.hypot(y, dy/(k*CS))

print('  %6s %15s %12s %15s %12s %8s'
      % ('k', 'phi/pi undriven', 'amplitude', 'phi/pi driven', 'amplitude', 'boost'))
und, drv = [], []
for k in KS:
    pc, ac = boundary(k, phi_constant)
    pd, ad = boundary(k, phi_decaying)
    und.append((pc, ac)); drv.append((pd, ad))
    print('  %6.0f %15.2e %12.5f %15.5f %12.5f %8.4f'
          % (k, pc/math.pi, ac, pd/math.pi, ad, ad/ac))

worst_und   = max(abs(p) for p, _ in und)
worst_amp   = max(abs(a - 1/3.) for _, a in und)
least_drv   = min(abs(p) for p, _ in drv)
boost       = drv[-1][1]/und[-1][1]

# ---------------------------------------------------------------------------
# C10b  the Einstein-de Sitter null: constant Phi, phase exactly zero.
# C10c  a time-dependent Phi puts a phase in, at every k.
# C10e  the undriven amplitude is the analytic Sachs-Wolfe value Phi/3.
# ---------------------------------------------------------------------------
ok_b = report('C10b  constant Phi: the boundary phase is zero at every k',
              worst_und < 1e-6, f'worst |phi| = {worst_und:.1e} rad')
ok_c = report('C10c  time-dependent Phi: the boundary phase is non-zero at every k',
              least_drv > 1e-3, f'smallest |phi| = {least_drv/math.pi:.4f} pi')
ok_e = report('C10e  control: the undriven amplitude is the analytic Phi/3',
              worst_amp < 1e-9, f'worst deviation {worst_amp:.1e}; '
              f'driven/undriven amplitude -> {boost:.4f}')

# ---------------------------------------------------------------------------
# C10d  THE POINT.  A criterion of the form "tracks cos(k r_s) in exact phase"
# accepts the undriven solution and rejects the driven one.  Scored by applying
# that criterion, at its own stated tolerance, to both.
# ---------------------------------------------------------------------------
TOL = 1e-3                     # "exact phase", read generously
accepts_undriven = all(abs(p) < TOL for p, _ in und)
rejects_driven   = all(abs(p) > TOL for p, _ in drv)
ok_d = report('C10d  a "tracks cos(k r_s) in exact phase" criterion accepts the '
              'UNDRIVEN solution and rejects the DRIVEN one',
              accepts_undriven and rejects_driven,
              f'at tolerance {TOL:g} rad: undriven accepted {accepts_undriven}, '
              f'driven rejected {rejects_driven} -- so the criterion certifies '
              'the absence of driving rather than the presence of the physics')

finish({'c_s_squared': str(cs2),
        'worst_undriven_phase_rad': worst_und,
        'worst_undriven_amplitude_error': worst_amp,
        'smallest_driven_phase_over_pi': least_drv/math.pi,
        'driven_over_undriven_amplitude': boost,
        'criterion_tolerance_rad': TOL,
        'criterion_accepts_undriven': accepts_undriven,
        'criterion_rejects_driven': rejects_driven})
