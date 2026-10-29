#!/usr/bin/env python3
"""C12 -- the rate at which a grid must sample the visibility, and the three
scales that are one scale.   P1-T, 2026-10-29.  Answers P1B->P1T #11.

WHAT WAS ASKED.  Is the controlling scale the FWHM of the visibility, the
scale height of the Thomson rate, or the recombination width?  A rule, not a
number, because N_ETA_FLOOR = 8000 is the constant standing in for it and S33
leaves it underived.

THE QUESTION DISSOLVES, AND THAT IS THE ANSWER.  The three are one scale at
the visibility peak, and the definition of the peak is what forces them equal.
With kappa(eta) = int_eta^eta_0 kappa' and V = kappa' e^-kappa,

    V' = (kappa'' + kappa'^2) e^-kappa                        [C12a]

and e^-kappa never vanishes, so eta_ast -- the peak of V -- is the point where

    kappa''(eta_ast) = -kappa'(eta_ast)^2 ,

the logarithmic shut-off rate of the Thomson rate equalling the Thomson rate
itself.  The scale height -kappa'/kappa'' and the optical-depth e-fold
1/kappa' are therefore the SAME NUMBER there, identically, not approximately.
The width follows: with Lambda = kappa'^2 - kappa'''/kappa' at the peak,

    sigma_V^-2 = kappa'(eta_ast)^2 + Lambda ,                  [C12b]

and Lambda vanishes for exponential freeze-out, which is what recombination
is.  The FWHM is then 1/kappa'(eta_ast) times a constant of order 2.4 -- 2.3548
for a Gaussian core, 2.4457 for the exponential -- so the PROFILE sets the
constant and the RATE sets the scale.  Write the rule in kappa'(eta_ast): not
because it is more accurate than the other two, it is the same number, but
because it is the only one of the three defined POINTWISE, and a non-uniform
grid is built from a rate at every eta rather than from one width for the
whole bump.

THE TWO REQUIREMENTS ADD; THEY ARE NOT A MAXIMUM.  Trapezoid error on a
uniform grid is exactly the aliasing of the integrand's transform at the
sampling frequency.  The kernel is exactly band-limited: by the Rayleigh
expansion, in the convention e^{i z mu} with P_l(1) = 1,

    j_l(z) = (1 / 2 i^l) int_{-1}^{1} P_l(mu) e^{i z mu} dmu ,  [C12c]

which exhibits j_l(k(eta_0 - eta)) as a superposition of e^{i omega eta} with
|omega| <= k and nothing outside -- for EVERY l, with no l in the band edge.
A product transforms to a convolution, so a band-limited factor SHIFTS the
frequency at which the source must already be small:

    2 pi / h  >=  k_max  +  nu_V(epsilon) .                     [C12d]

THE BOUND IS NOT ON SAMPLING V; IT IS ON BUILDING KAPPA.  A uniform grid
INTEGRATING a smooth V that decays at both ends errs only by aliasing, which
[C12d] already makes negligible -- so the line-of-sight quadrature has no
visibility rate to meet beyond the band edge.  The second-order error is
elsewhere, and it is in the construction: kappa is accumulated from kappa' by
trapezoid on whatever grid the history is built on, and Euler-Maclaurin on the
PARTIAL sums does not vanish.  With kappa(eta) = F(eta_0) - F(eta),

    d.kappa(eta) = (h^2/12)[kappa''(eta_0) - kappa''(eta)] = -(h^2/12) kappa''(eta)

since kappa'' -> 0 at eta_0, and d.V/V = -d.kappa.  At the peak C12a turns
kappa'' into -kappa'^2, which is the step that makes the rule a RULE:

    d(int V)/int V  =  -(h kappa'(eta_ast))^2 / 12 ,            [C12e]

negative, so a coarse grid LOWERS the visibility.  Hence

    h kappa'(eta_ast) <= sqrt(12 epsilon)
    N >= L kappa'(eta_ast) / sqrt(12 epsilon)    (uniform, span L)

or, in the form checkable against a figure, 2 sqrt(2 ln 2) / sqrt(12 epsilon)
samples across the FWHM: 21.5 at one part in a thousand, 68 at one in ten
thousand.

THE GRADED GRID FOLLOWS, AND THE OPTICAL DEPTH IS ITS OWN COORDINATE.
Imposing [C12d] and [C12e] locally, 1/h(eta) >= 12 k_max / pi + kappa'(eta) /
sqrt(12 epsilon), and integrating across the span,

    N  =  12 k_max L / pi  +  kappa(eta_i) / sqrt(12 epsilon) . [C12f]

A grid uniform in k_max eta + kappa(eta) / sqrt(12 epsilon) -- conformal time
plus a multiple of optical depth -- meets both conditions with one knob, and
the recombination term is independent of k_max AND of L.  That is the
structural point: the two costs ADD, rather than one flooring the other.

WHAT THIS DOES NOT ESTABLISH.  The prefactor is demonstrated on a history
built here, whose kappa is a closed form so that int V d(eta) has an EXACT
reference rather than another quadrature.  The identities and the error law
hold for any kappa' whatever; the constant 1/12 is Euler-Maclaurin's and is
asserted, not fitted.  The constant relating the FWHM to 1/kappa'(eta_ast) is
profile-dependent at the four-per-cent level and is reported, not asserted.

NO PROJECT CODE IS IMPORTED.  The history is built here.

THE CONTROL THIS FILE EXISTS TO CARRY.  The first version of C12, withdrawn
2026-10-28, laid its grid over the window it meant to undersample and so could
never violate its own bound -- an instrument measuring an artefact of its own
construction.  C12g and C12h are the repair: the bound is evaluated at a grid
chosen FROM it to fail and at one chosen to meet it, and the instrument fails
if the bound does not discriminate between them.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
AUDIT_TITLE = 'The sampling rate of the visibility, and the three scales that are one'
AUDIT_PROSE = (
  "The peak of the visibility is the point where $\\kappa''=-\\kappa'^2$, so at "
  "$\\eta_\\ast$ the scale height of the Thomson rate and the optical-depth "
  "e-fold are identically the same number, and the width follows as "
  "$\\sigma_{\\mathcal V}^{-2}=\\kappa'(\\eta_\\ast)^2+\\Lambda$ with $\\Lambda$ "
  "vanishing for exponential freeze-out. The three candidate scales --- the "
  "FWHM of $\\mathcal V$, the Thomson scale height, the recombination width "
  "--- are one scale, and the rule is written in $\\kappa'(\\eta_\\ast)$ because "
  "it is the only one defined pointwise. The kernel is exactly band-limited: "
  "$j_\\ell(z)=(2i^\\ell)^{-1}\\int_{-1}^{1}P_\\ell(\\mu)e^{iz\\mu}\\mathrm d\\mu$ "
  "exhibits $j_\\ell(k(\\eta_0-\\eta))$ as a superposition of $e^{i\\omega\\eta}$ "
  "with $|\\omega|\\le k$ and nothing outside, for every $\\ell$, so the band "
  "edge enters as a shift and the two requirements add rather than one "
  "flooring the other. The binding statement is Euler--Maclaurin on the "
  "partial sums that accumulate $\\kappa$ from $\\kappa'$, "
  "$h\\kappa'(\\eta_\\ast)\\le\\sqrt{12\\epsilon}$ on the grid $\\kappa$ is built "
  "on, which is 21.5 samples across "
  "the FWHM at one part in a thousand. Imposed locally it integrates to "
  "$N=12k_{\\max}L/\\pi+\\kappa(\\eta_i)/\\sqrt{12\\epsilon}$, so a grid uniform "
  "in conformal time plus a multiple of optical depth meets both conditions "
  "with one knob and the recombination cost is independent of $k_{\\max}$."
)

import math
import numpy as np
from scipy.special import spherical_jn, eval_legendre
from scipy.optimize import brentq
from _common import report, finish

# ---------------------------------------------------------------------------
# A history with a CLOSED-FORM optical depth, so the reference for int V d(eta)
# is exact rather than another quadrature.  Exponential freeze-out, which is
# the local form of recombination at the peak:
#
#   kappa'(eta) = beta exp[-beta (eta - eta_ast)]      so kappa'(eta_ast) = beta
#   kappa(eta)  = [kappa'(eta) - kappa'(eta_0)] / beta
#   int V d(eta) = e^-kappa(eta_0) - e^-kappa(eta_i)            EXACTLY
#
# beta and the span are PLANCK's, so the numbers below are the bundle's own:
# kappa'(eta_ast) = 267.77 and kappa(eta_i) = 275.14.
# ---------------------------------------------------------------------------
BETA, ETA_I, ETA_0 = 267.77, 0.0333, 3.1987
ETA_STAR = ETA_I + math.log(275.14)/BETA

def kprime(e):  return BETA*math.exp(-BETA*(e - ETA_STAR))
def kappa(e):   return (kprime(e) - kprime(ETA_0))/BETA
def kpp(e):     return -BETA*kprime(e)
def kppp(e):    return BETA*BETA*kprime(e)
def vis(e):     return kprime(e)*math.exp(-kappa(e))
def kprime_arr(e):  return BETA*np.exp(-BETA*(e - ETA_STAR))

L = ETA_0 - ETA_I
EXACT = math.exp(-kappa(ETA_0)) - math.exp(-kappa(ETA_I))
KAPPA_I = kappa(ETA_I)

# ---------------------------------------------------------------------------
# C12a  the peak of V is where kappa'' = -kappa'^2.
# ---------------------------------------------------------------------------
eta_star = brentq(lambda e: kpp(e) + kprime(e)**2,
                  ETA_STAR - 0.01, ETA_STAR + 0.01, xtol=1e-16)
kp_s, kpp_s = kprime(eta_star), kpp(eta_star)
res_a = abs(kpp_s + kp_s**2)/kp_s**2
ok_a = report('C12a  the visibility peak is the point where kappa\'\' = -kappa\'^2, '
              'so the shut-off rate of the Thomson rate equals the Thomson rate',
              res_a < 1e-10,
              f"eta_ast = {eta_star:.8f}, kappa'(eta_ast) = {kp_s:.4f}, "
              f"residual = {res_a:.1e}")

# ---------------------------------------------------------------------------
# C12b  the three candidate scales are one scale.
# ---------------------------------------------------------------------------
fine = np.linspace(ETA_STAR - 0.06, ETA_STAR + 0.06, 1200001)
Vf = np.array([vis(float(x)) for x in fine])
above = fine[Vf >= Vf.max()/2.0]
fwhm = float(above.max() - above.min())
s_efold, s_height = 1.0/kp_s, -kp_s/kpp_s
Lam = kp_s**2 - kppp(eta_star)/kp_s
pair = abs(s_efold - s_height)/s_efold
const = fwhm*kp_s
ok_b = report('C12b  the optical-depth e-fold and the Thomson scale height are '
              'identically one scale at eta_ast, and the FWHM is that scale to '
              'within the freeze-out profile',
              pair < 1e-12 and abs(Lam)/kp_s**2 < 1e-10 and 2.30 < const < 2.50,
              f"1/kappa' and -kappa'/kappa'' agree to {pair:.1e}; "
              f"Lambda/kappa'^2 = {abs(Lam)/kp_s**2:.1e}; "
              f"FWHM x kappa'(eta_ast) = {const:.4f}, against 2.3548 for a Gaussian "
              f"core and 2.4457 for exponential freeze-out")

# ---------------------------------------------------------------------------
# C12c  the kernel is exactly band-limited at k, for every l.  The Rayleigh
# identity IS the claim: it writes j_l as a superposition of e^{i omega eta}
# with |omega| <= k and nothing outside.  A windowed numerical transform was
# tried and discarded -- it measures the window, not the kernel.
# ---------------------------------------------------------------------------
mu_g, w_g = np.polynomial.legendre.leggauss(600)
worst_id, rows_c = 0.0, 0
for l in (0, 1, 2, 5, 20, 60, 150):
    for z in (3.0, 25.0, 140.0, 400.0):
        lhs = float(spherical_jn(l, z))
        if abs(lhs) < 1e-10:        # below the quadrature's own floor: a
            continue                # relative score there measures nothing
        rhs = float((0.5*np.sum(w_g*eval_legendre(l, mu_g)*np.exp(1j*z*mu_g))
                     / (1j**l)).real)
        worst_id = max(worst_id, abs(lhs - rhs)/abs(lhs)); rows_c += 1
ok_c = report('C12c  j_l(k(eta_0-eta)) is a superposition of e^{i omega eta} with '
              '|omega| <= k and nothing outside, for every l',
              worst_id < 1e-9 and rows_c >= 14,
              f'the Rayleigh identity holds to {worst_id:.1e} over {rows_c} (l, z) '
              f'rows, l = 0 to 150 -- the band edge is k and carries no l')

# ---------------------------------------------------------------------------
# C12d  the shift, as an exact identity: for a band-limited factor cos(K x),
# the transform of the product is [V-hat(nu-K) + V-hat(nu+K)] / 2.
# ---------------------------------------------------------------------------
K_BAND = 900.0
xs = np.linspace(ETA_STAR - 0.08, ETA_STAR + 0.08, 1600001)
Vx = np.array([vis(float(x)) for x in xs])
def Vhat(nu):
    return np.trapezoid(Vx*np.exp(-1j*nu*(xs - ETA_STAR)), xs)
worst_d = 0.0
for nu in (4.0*kp_s, 7.0*kp_s, 11.0*kp_s):
    nu_tot = nu + K_BAND
    lhs = np.trapezoid(Vx*np.cos(K_BAND*(xs - ETA_STAR))
                       * np.exp(-1j*nu_tot*(xs - ETA_STAR)), xs)
    rhs = 0.5*(Vhat(nu_tot - K_BAND) + Vhat(nu_tot + K_BAND))
    worst_d = max(worst_d, abs(lhs - rhs)/abs(rhs))
ratio_d = abs(Vhat(7.0*kp_s))/abs(Vhat(7.0*kp_s + K_BAND))
ok_d = report('C12d  a band-limited factor SHIFTS the frequency at which the '
              'visibility must already be small, so k_max and the rate add',
              worst_d < 1e-8 and ratio_d > 10.0,
              f'the shift identity holds to {worst_d:.1e}; the source at '
              f'7 kappa\' is {ratio_d:.0f}x what it is at 7 kappa\' + k, which is '
              f'the cost of not adding them')

# ---------------------------------------------------------------------------
# C12e  the error law, scored against the CLOSED FORM and not against a finer
# grid of the same quadrature.
# ---------------------------------------------------------------------------
def built_integral(n):
    """int V on an n-point uniform grid, with kappa ACCUMULATED from kappa' by
    trapezoid, which is how a history is built.  Scored against the closed
    form, so the reference is not another quadrature."""
    g = np.linspace(ETA_I, ETA_0, n)
    K = kprime_arr(g)
    fwd = np.concatenate(([0.0], np.cumsum(0.5*(K[1:] + K[:-1])*np.diff(g))))
    return float(np.trapezoid(K*np.exp(-(fwd[-1] - fwd)), g))

rows, orders = [], []
for n in (2000, 4000, 8000, 16000, 32000):
    err = (built_integral(n) - EXACT)/EXACT
    rows.append((n, (L/n)*kp_s, err, -((L/n)*kp_s)**2/12.0))
for i in range(1, len(rows)):
    orders.append(math.log(abs(rows[i-1][2])/abs(rows[i][2]))/math.log(2.0))
worst_law = max(abs(r[2] - r[3])/abs(r[3]) for r in rows)
signs = all(r[2] < 0.0 for r in rows)
ok_e = report('C12e  the second-order error is in BUILDING kappa, not in sampling '
              'V, and C12a turns it into -(h kappa\'(eta_ast))^2 / 12',
              min(orders) > 1.9 and worst_law < 0.02 and signs,
              f'order {min(orders):.3f} to {max(orders):.3f}; the law holds to '
              f'{worst_law*100:.2f} per cent at every grid, and the sign is '
              f'negative throughout -- a coarse grid lowers the visibility')

# ---------------------------------------------------------------------------
# C12f  the bound in points across the FWHM, and the graded grid.
# ---------------------------------------------------------------------------
def n_uniform(eps):      return L*kp_s/math.sqrt(12.0*eps)
def per_fwhm(eps):       return 2.0*math.sqrt(2.0*math.log(2.0))/math.sqrt(12.0*eps)
def n_graded(kmax, eps): return 12.0*kmax*L/math.pi + KAPPA_I/math.sqrt(12.0*eps)
ok_f = report('C12f  the bound in points across the FWHM, and the graded grid that '
              'makes the two costs add',
              0.90*8000 < n_uniform(1e-3) < 1.05*8000,
              f'uniform at eps = 1e-3 needs {n_uniform(1e-3):.0f} points '
              f'({per_fwhm(1e-3):.1f} across the FWHM) -- N_ETA_FLOOR is 8000; '
              f'graded at k_max = 1500 needs {n_graded(1500.0, 1e-3):.0f}, of which '
              f'{KAPPA_I/math.sqrt(12e-3):.0f} are the recombination term and do '
              f'not depend on k_max')

# ---------------------------------------------------------------------------
# C12g / C12h  THE CONTROL.  The bound must FIRE on a grid chosen from it to
# fail and must NOT fire on one chosen to pass.  Without both, the instrument
# is decoration -- which is what the withdrawn first version was.
# ---------------------------------------------------------------------------
EPS = 1.0e-3
n_need = n_uniform(EPS)
n_bad, n_good = int(0.25*n_need), int(4.0*n_need)
def err_at(n):
    return abs(built_integral(n) - EXACT)/EXACT
e_bad, e_good = err_at(n_bad), err_at(n_good)
ok_g = report('C12g  the bound fires: a grid at a quarter of the required rate '
              'misses the tolerance it was sized for',
              e_bad > EPS,
              f'n = {n_bad}, h kappa\' = {(L/n_bad)*kp_s:.3f} against the bound '
              f'{math.sqrt(12*EPS):.3f}, gives {e_bad:.2e} against eps = {EPS:.0e}')
ok_h = report('C12h  and it discriminates: a grid at four times the required rate '
              'meets it, so C12g is not an instrument that always fails',
              e_good < EPS and e_bad/e_good > 50.0,
              f'n = {n_good} gives {e_good:.2e} -- a separation of '
              f'{e_bad/e_good:.0f}x across the bound')

finish({'eta_star': float(eta_star),
        'kappa_prime_at_eta_star': float(kp_s),
        'kappa_at_eta_i': float(KAPPA_I),
        'fwhm': float(fwhm),
        'fwhm_times_kappa_prime': float(const),
        'exact_visibility_integral': float(EXACT),
        'worst_rayleigh_residual': float(worst_id),
        'worst_shift_identity_residual': float(worst_d),
        'measured_order': float(min(orders)),
        'worst_departure_from_one_twelfth': float(worst_law),
        'n_uniform_eps_1e_3': float(n_uniform(1e-3)),
        'points_across_fwhm_eps_1e_3': float(per_fwhm(1e-3)),
        'recombination_term_eps_1e_3': float(KAPPA_I/math.sqrt(12e-3)),
        'control_error_quarter_rate': float(e_bad),
        'control_error_four_times_rate': float(e_good)})
