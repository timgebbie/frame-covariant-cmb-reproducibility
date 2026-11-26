#!/usr/bin/env python3
"""C17 -- the tight-coupling transition (approximation A-5).  Added 2026-11-25.

A-5 carries the photons through the end of tight coupling with Thomson
scattering in the hierarchy, in place of the pair held after 6 eta_*.  This
instrument checks the construction the supplement registers (sec:a5-construction)
before anything is built, from the 1+3 relations and Paper 1's collision term
alone:

    C[tau] ~ sigma_T n_e ( fbar_1 e^a v^B_a + fbar_2 e^a e^b tau_ab - tau ),   Paper 1 (38).

C17a  the collision term on the PSTF basis, CONFIRMATORY of c16.  c16 settles
      fbar_2 = 1/10 in index algebra at every rank (CLAUDE.md 3b); here the
      same weight is read off a test field -- random PSTF tensors of ranks
      0 to 3 on an explicit Cartesian basis, integrated by Gauss-Legendre
      quadrature on the sphere -- which is a representation and so confirms
      rather than settles.  The monopole is returned (S_0 = tau_0), the
      dipole and the octupole are not (S_1 = S_3 = 0), and the quadrupole
      returns one tenth of itself.  So the quadrupole scatters out at
      (1 - fbar_2) kappa' = (9/10) kappa', and Kaiser's f_2 in Annals II
      (169) is 1 - fbar_2.  The polarised value is a
      comparator, not derived here: the E-mode moments of Ma & Bertschinger's
      hierarchy, held at their tight-coupling values, return 1/4 of the
      quadrupole, so 1 - fbar_2 = 3/4.
C17b  the hierarchy with scattering, in both phases.  The rows of (F.1) with
      the collision term and the pair's rows map onto each other by
      sigma_l = (-1)^(l+1) tau_l with the baryon velocity one object in both,
      as the dipole is; (-1)^l fails at the Thomson dipole term as well as at
      the sources (negative control).  The drag conserves momentum with
      R = 3 rho_b / (4 rho_gamma), and at zeroth order the photon and baryon
      rows give the pair (152).
C17c  tight coupling at first order in the scattering time 1/kappa':
          v_b - sigma_1 = R / ((1+R) kappa') (k sigma_0 - H sigma_1),
          sigma_2 = -k sigma_1 / ((1 - fbar_2) kappa'),
      so tau_2 = (10/9)(k/kappa') tau_1 in the phase of (F.1).
C17d  the damping.  The first-order system's acoustic root is
      k c_s - i Gamma with
          Gamma = k^2 / (6 (1+R) kappa') [ R^2/(1+R) + (4/5)/(1 - fbar_2) ],
      which is T-21's envelope with Annals II's 4/5 at fbar_2 = 0, Hu &
      Sugiyama's 8/9 at 1/10 and 16/15 at 1/4.  The full hierarchy, with
      constant coefficients and l_max = 40, has a slow eigenvalue whose real
      part is -Gamma to O(x^2) in x = k/kappa', for all three; and a hand-over
      to it from the pair leaves an amplitude error of O(x^2) at zeroth order
      and O(x^4) at first order.
C17e  the stress constraint before decoupling.  The tight-coupling quadrupole
      enters eq:stress-constraint with the ruled sign,
          k^2 (Phi_A + Phi_H) = (16/9) Hc^2 Omega_g (k/kappa') tau_1,
      the same in either phase when each is paired with its own constraint;
      outside the horizon in the radiation era the ratio is
      -(8/9) Omega_g / (eta kappa'), negative, as after decoupling.
C17f  the line of sight.  The weights come from the matching rows, which are
      index algebra: Paper 1's source carries the selected row at +S_B at
      ranks zero and two (eq:paper1-source), and the rows give C_0 = r_2/3,
      C_2 = r_2/k^2 for a rank-two forcing r_2.  CONFIRMATORY: on a plane wave
      the same source projects with j_l/3 + j_l'' beside the rank-zero j_l,
      read with the Rayleigh convention e^{-i x mu} = sum (2l+1)(-i)^l j_l P_l
      by Gauss-Legendre quadrature, to 1e-13.  The in-scattered
      quadrupole is therefore the slot  V fbar_2 tau_2 (K/3 + K''/k^2), carried
      at V on the undifferentiated tau_2 (W kappa' = V).  CONFIRMATORY, with
      Ma & Bertschinger's Legendre normalisation as the bundle identifies it
      (sigma_2 = (15/2) Theta_2, radiation_era.py and c14): the slot is
      -(1/4) V Theta_2 (j + 3 j''), the standard form at the Sachs-Wolfe
      slot's sign.  GDE99 (37) leaves tau_A_l invariant for l >= 2 at first
      order in v, so the slot and the slip v_b - sigma_1 are frame-invariant;
      CONFIRMATORY, an exact Lorentz transformation of a test brightness moves
      the dipole by the boost and the quadrupole only at second order.

No project code is imported; `_common` checks that before anything runs.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = "The tight-coupling transition (A-5)"
AUDIT_PROSE = ("With Thomson scattering returning $\\bar f_2=\\tfrac1{10}$ of the photon quadrupole, "
               "which c16 settles in index algebra, the quadrupole scatters out at "
               "$\\tfrac9{10}\\kappa'$ and Kaiser's $f_2$ is $1-\\bar f_2$. To first order in $1/\\kappa'$ the baryons slip by "
               "$R(k\\delta T-\\mathcal H\\tau_1)/[(1+R)\\kappa']$ and the quadrupole is "
               "$\\tau_2=\\tfrac{10}9(k/\\kappa')\\tau_1$. The acoustic root then damps at "
               "$\\Gamma=k^2[R^2/(1+R)+\\tfrac45(1-\\bar f_2)^{-1}]/[6(1+R)\\kappa']$, which is "
               "T-21's envelope: $\\tfrac45$, $\\tfrac89$ and $\\tfrac{16}{15}$ at "
               "$\\bar f_2=0$, $\\tfrac1{10}$ and $\\tfrac14$, and the full hierarchy's slow "
               "eigenvalue meets it to $O(x^2)$. The quadrupole enters the stress constraint "
               "with the ruled sign, and the line of sight as a fourth slot, "
               "$\\mathcal V\\bar f_2\\tau_2(K/3+K''/k^2)$, which is frame-invariant.")

import numpy as np
import sympy as sp
from scipy.special import spherical_jn, eval_legendre
from _common import finish, report

metrics = {}
I3 = np.eye(3)

# --------------------------------------------------------------------------
# C17a -- the collision term on the PSTF basis.
mu, wmu = np.polynomial.legendre.leggauss(64)
phi = np.linspace(0.0, 2 * np.pi, 128, endpoint=False)
M, P = np.meshgrid(mu, phi, indexing='ij')
w = (np.outer(wmu, np.full(phi.size, 2 * np.pi / phi.size)) / (4 * np.pi)).reshape(-1)
st = np.sqrt(1 - M**2)
e = np.stack([st * np.cos(P), st * np.sin(P), M]).reshape(3, -1)   # unit directions
rng = np.random.default_rng(20261125)

def pstf2(t):
    t = 0.5 * (t + t.T)
    return t - np.trace(t) / 3 * I3

def pstf3(t):
    perms = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
    s = sum(np.transpose(t, p) for p in perms) / 6
    tr = np.einsum('iij->j', s)
    return s - (np.einsum('ij,k->ijk', I3, tr) + np.einsum('ik,j->ijk', I3, tr)
                + np.einsum('jk,i->ijk', I3, tr)) / 5

t0 = 0.3
t1 = rng.normal(size=3)
t2 = pstf2(rng.normal(size=(3, 3)))
t3 = pstf3(rng.normal(size=(3, 3, 3)))
O2 = np.einsum('an,bn->abn', e, e) - I3[:, :, None] / 3
tau = (t0 + t1 @ e + np.einsum('abn,ab->n', O2, t2)
       + np.einsum('abc,an,bn,cn->n', t3, e, e, e))
phase_fn = 0.75 * (1 + (e.T @ e) ** 2)                       # (3/4)(1 + (e.e')^2)
S = phase_fn @ (w * tau)                                     # int dOmega'/4pi P tau
# PSTF moments, with int O^<A_l> O_<A_l> dOmega/4pi = l!/(2l+1)!!
S0 = float(np.sum(w * S))
S1 = (e * w) @ S * 3.0
S2 = np.einsum('abn,n->ab', O2, w * S) * 7.5
S3 = float(np.einsum('abc,an,bn,cn,n->', t3, e, e, e, w * S))  # overlap with tau's octupole
big = np.abs(t2) > 0.1
f2bar = float(np.mean(S2[big] / t2[big]))
print(f'  C17a  S_0/tau_0 = {S0/t0:.15f}   |S_1| = {np.abs(S1).max():.1e}'
      f'   S_2/tau_2 = {f2bar:.15f}   <tau_3, S_3> = {S3:.1e}')
report('C17a  confirmatory of c16: Thomson scattering returns the monopole and neither the dipole nor the octupole',
       abs(S0 / t0 - 1) < 1e-13 and np.abs(S1).max() < 1e-13 and abs(S3) < 1e-13)
report('C17a  confirmatory of c16: it returns one tenth of the quadrupole, fbar_2 = 1/10',
       np.allclose(S2, t2 / 10, atol=1e-13), f'{f2bar:.15f}')

# The Doppler term, fbar_1 = 1.  In the electrons' rest frame the brightness is
# tau - e.v_B to first order; the rest-frame scattering returns no dipole (above),
# and transforming the scattered brightness back adds + e.v_B.
vB = rng.normal(size=3) * 1e-3
S_rest = phase_fn @ (w * (tau - vB @ e))
S_lab = S_rest + vB @ e
S1_lab = (e * w) @ S_lab * 3.0
report('C17a  in-scattering carries the baryon velocity: fbar_1 = 1',
       np.allclose(S1_lab, vB, atol=1e-13), f'{np.abs(S1_lab - vB).max():.1e}')

# Polarisation, as a comparator (Ma & Bertschinger, their Eq. 64): with
# Pi = F_2 + G_0 + G_2 the E-mode moments are driven by kappa' Pi (1/2, 1/10)
# and the quadrupole receives kappa' Pi/10.  Held at their tight-coupling values:
F2, G0, G2, Pi = sp.symbols('F_2 G_0 G_2 Pi')
tc = sp.solve([sp.Eq(G0, Pi / 2), sp.Eq(G2, Pi / 10), sp.Eq(Pi, F2 + G0 + G2)],
              [G0, G2, Pi], dict=True)[0]
fbar_pol = sp.simplify(tc[Pi] / 10 / F2)
report('C17a  the E-mode moments at tight coupling return 1/4 of the quadrupole: '
       '1 - fbar_2 = 3/4 (comparator)', fbar_pol == sp.Rational(1, 4), f'{fbar_pol}')
metrics.update(fbar_2=f2bar, fbar_2_polarised=float(fbar_pol))

# --------------------------------------------------------------------------
# C17b -- the hierarchy with scattering, in both phases.
k, kp, fb = sp.symbols('k kappa_p fbar_2', positive=True)
dPhiH, PhiA, vb = sp.symbols('dPhiH PhiA v_B')
LMAP = 6
tl = sp.symbols('tl0:%d' % (LMAP + 1))
wl = [sp.Rational((l + 1) ** 2, (2 * l + 3) * (2 * l + 1)) for l in range(LMAP + 1)]

def collision(l, x1, xl):
    """Thomson's term at rank l, for the dipole x1 and the rank-l moment xl."""
    if l == 0:
        return 0
    if l == 1:
        return kp * (vb - x1)
    if l == 2:
        return -(1 - fb) * kp * xl
    return -kp * xl

def rows_F1(l):
    r = k * ((tl[l - 1] if l else 0) - wl[l] * tl[l + 1])
    r += (dPhiH if l == 0 else 0) - (k * PhiA if l == 1 else 0)
    return r + collision(l, tl[1], tl[l])

def rows_pair(l, sgn):
    sig = lambda j: sgn(j) * tl[j] if j >= 0 else 0
    r = k * (wl[l] * sig(l + 1) - sig(l - 1))
    r -= (dPhiH if l == 0 else 0) + (k * PhiA if l == 1 else 0)
    return r + collision(l, sig(1), sig(l))

maps = lambda sgn: all(sp.expand(rows_pair(l, sgn) - sgn(l) * rows_F1(l)) == 0
                       for l in range(LMAP))
report("C17b  with Thomson's term the pair's multipoles are (-1)^(l+1) times (F.1)'s, "
       "v_B shared as the dipole is", maps(lambda j: (-1) ** (j + 1)))
report("C17b  (-1)^l fails at the Thomson dipole term too (negative control)",
       not maps(lambda j: (-1) ** j))

rho_g, rho_b = sp.symbols('rho_gamma rho_b', positive=True)
s0, s1, Hc, Rb = sp.symbols('sigma_0 sigma_1 Hc R', positive=True)
R_def = 3 * rho_b / (4 * rho_g)
drag = sp.Rational(4, 3) * rho_g * kp * (vb - s1) + rho_b * (kp / R_def) * (s1 - vb)
report('C17b  the drag conserves momentum with R = 3 rho_b/(4 rho_gamma)',
       sp.simplify(drag) == 0)
# zeroth order: v_b = sigma_1, photon row + R * baryon row, R' = Hc R
s1p = sp.Symbol('s1p')
photon = -k * s0 - k * PhiA + kp * (vb - s1)
baryon = -Hc * vb - k * PhiA + (kp / Rb) * (s1 - vb)
pair = sp.solve(sp.Eq(s1p + Rb * s1p, (photon + Rb * baryon).subs(vb, s1)), s1p)[0]
pair_152 = -(Hc * Rb / (1 + Rb)) * s1 - k * s0 / (1 + Rb) - k * PhiA
report('C17b  at zeroth order the photon and baryon rows give the pair (152)',
       sp.simplify(pair - pair_152) == 0)

# --------------------------------------------------------------------------
# C17c -- tight coupling at first order in 1/kappa'.
# The baryon row solved for the slip, with the zeroth-order derivative inside:
slip = sp.simplify(-(Rb / kp) * (pair_152 + Hc * s1 + k * PhiA))
slip_reg = Rb / ((1 + Rb) * kp) * (k * s0 - Hc * s1)
report('C17c  the slip: v_b - sigma_1 = R (k sigma_0 - H sigma_1) / ((1+R) kappa\')',
       sp.simplify(slip - slip_reg) == 0)
# The quadrupole row: sigma_2' and sigma_3 are higher order, so
s2 = sp.Symbol('sigma_2')
quad = sp.solve(sp.Eq(-k * s1 - (1 - fb) * kp * s2, 0), s2)[0]
report('C17c  the quadrupole: sigma_2 = -k sigma_1 / ((1 - fbar_2) kappa\')',
       sp.simplify(quad + k * s1 / ((1 - fb) * kp)) == 0)
tau2_coeff = sp.simplify(-quad / s1 * kp / k).subs(fb, sp.Rational(1, 10))
report('C17c  in the phase of (F.1), tau_2 = (10/9)(k/kappa\') tau_1 on the released path',
       tau2_coeff == sp.Rational(10, 9), f'{tau2_coeff}')

# --------------------------------------------------------------------------
# C17d -- the damping.  Constant R and kappa', no expansion and no gravity:
# the system (sigma_0, sigma_1, sigma_2, v_b) with sigma_3 = 0, eps = 1/kappa'.
eps, lam, l0, l1 = sp.symbols('epsilon lambda l0 l1')
g = 1 - fb
A = sp.Matrix([[0, k / 3, 0, 0],
               [-k, -1 / eps, sp.Rational(4, 15) * k, 1 / eps],
               [0, -k, -g / eps, 0],
               [0, 1 / (eps * Rb), 0, -1 / (eps * Rb)]])
charp = sp.expand(sp.simplify((A - lam * sp.eye(4)).det() * eps**2 * Rb))
Pser = sp.expand(charp.subs(lam, l0 + eps * l1))
order0 = sp.factor(Pser.subs(eps, 0))
lam0 = sp.I * k / sp.sqrt(3 * (1 + Rb))
slow0 = sp.simplify(order0.subs(l0, lam0)) == 0
lam1 = sp.solve(sp.Eq(sp.diff(Pser, eps).subs(eps, 0).subs(l0, lam0), 0), l1)[0]
Gamma = k**2 / (6 * (1 + Rb)) * (Rb**2 / (1 + Rb) + sp.Rational(4, 5) / g)
report('C17d  the acoustic root at zeroth order is i k c_s, c_s^2 = 1/(3(1+R))', slow0)
report('C17d  at first order it damps at Gamma = k^2 [R^2/(1+R) + (4/5)/(1-fbar_2)] '
       '/ (6 (1+R) kappa\'), with no shift of frequency',
       sp.simplify(lam1 + Gamma) == 0)
coeffs = {str(f): sp.Rational(4, 5) / (1 - f)
          for f in (0, sp.Rational(1, 10), sp.Rational(1, 4))}
report("C17d  4/5, 8/9 and 16/15 at fbar_2 = 0, 1/10 and 1/4: Annals II's (168) and (169)",
       [coeffs['0'], coeffs['1/10'], coeffs['1/4']]
       == [sp.Rational(4, 5), sp.Rational(8, 9), sp.Rational(16, 15)],
       ', '.join(f'{v}' for v in coeffs.values()))
# T-21's integrand, as decoupling.diffusion_scale writes it, with f_2 = 1 - fbar_2
t21 = (Rb**2 + sp.Rational(4, 5) / g * (1 + Rb)) / (6 * kp * (1 + Rb) ** 2)
report('C17d  Gamma/k^2 is T-21\'s integrand [R^2 + (4/5) f_2^-1 (1+R)] / (6 kappa\' (1+R)^2)',
       sp.simplify(Gamma / k**2 / kp - t21) == 0)

def hierarchy(fbar, x, R=0.6, L=40):
    """The full hierarchy with scattering, constant coefficients, k = 1."""
    kap = 1.0 / x
    n = L + 2
    Am = np.zeros((n, n))
    for l in range(L + 1):
        if l < L:
            Am[l, l + 1] += (l + 1) ** 2 / ((2 * l + 3) * (2 * l + 1))
        if l > 0:
            Am[l, l - 1] -= 1.0
    Am[1, 1] -= kap; Am[1, n - 1] += kap
    Am[2, 2] -= (1.0 - fbar) * kap
    for l in range(3, L + 1):
        Am[l, l] -= kap
    Am[n - 1, 1] += kap / R; Am[n - 1, n - 1] -= kap / R
    return Am

R0 = 0.6
cs = 1.0 / np.sqrt(3 * (1 + R0))
eig_err, hand0, hand1 = {}, {}, {}
for fbar in (0.0, 0.1, 0.25):
    for x in (0.02, 0.01, 0.005):
        Am = hierarchy(fbar, x)
        lams, vecs = np.linalg.eig(Am)
        i_up = int(np.argmin(np.abs(lams - 1j * cs)))
        i_dn = int(np.argmin(np.abs(lams + 1j * cs)))
        gam = x / (6 * (1 + R0)) * (R0**2 / (1 + R0) + 0.8 / (1 - fbar))
        eig_err[(fbar, x)] = -lams[i_up].real / gam - 1
        # a state on the slow manifold, then its fast part rebuilt by the hand-over
        ref = np.real(vecs[:, i_up] / vecs[0, i_up])
        def handed(order):
            y = np.zeros_like(ref); y[0], y[1] = ref[0], ref[1]
            y[-1] = ref[1] + (R0 / ((1 + R0)) * x * ref[0] if order else 0.0)
            if order:
                y[2] = -x * ref[1] / (1 - fbar)
            return y
        amp = lambda y: (lambda c: abs(c[i_up]) + abs(c[i_dn]))(
            np.linalg.solve(vecs, y.astype(complex)))
        hand0[(fbar, x)] = amp(handed(0)) / amp(ref) - 1
        hand1[(fbar, x)] = amp(handed(1)) / amp(ref) - 1
for fbar in (0.0, 0.1, 0.25):
    print(f'  C17d  fbar_2 = {fbar:<4}: -Re(lambda)/Gamma - 1 = '
          + ', '.join(f'{eig_err[(fbar, x)]:+.2e}' for x in (0.02, 0.01, 0.005))
          + '  at x = 0.02, 0.01, 0.005')
    print(f'        hand-over: zeroth order '
          + ', '.join(f'{hand0[(fbar, x)]:+.1e}' for x in (0.02, 0.01, 0.005))
          + ';  first order '
          + ', '.join(f'{hand1[(fbar, x)]:+.1e}' for x in (0.02, 0.01, 0.005)))
quad_conv = all(abs(eig_err[(f, 0.02)] / eig_err[(f, 0.01)] - 4) < 0.1
                and abs(eig_err[(f, 0.01)]) < 1e-4 for f in (0.0, 0.1, 0.25))
report('C17d  the full hierarchy\'s slow eigenvalue damps at Gamma, to O(x^2), for all three',
       quad_conv, f'{max(abs(v) for v in eig_err.values()):.1e} worst, x <= 0.02')
order2 = all(abs(hand0[(f, 0.01)] / hand0[(f, 0.005)] - 4) < 0.2 for f in (0.0, 0.1, 0.25))
order4 = all(abs(hand1[(f, 0.01)] / hand1[(f, 0.005)] - 16) < 2.0 for f in (0.0, 0.1, 0.25))
report('C17d  the hand-over errs by O(x^2) at zeroth order and O(x^4) at first order',
       order2 and order4,
       f'{abs(hand0[(0.1, 0.01)]):.1e} and {abs(hand1[(0.1, 0.01)]):.1e} at x = 0.01')
metrics.update(eigen_rel_err_x01=eig_err[(0.1, 0.01)],
               handover_zeroth_x01=hand0[(0.1, 0.01)],
               handover_first_x01=hand1[(0.1, 0.01)])

# --------------------------------------------------------------------------
# C17e -- the stress constraint before decoupling.
Om, t1s, eta = sp.symbols('Omega_gamma tau_1 eta', positive=True)
tau2_tc = (k / ((1 - fb) * kp)) * t1s                       # (F.1)'s phase
sig2_tc = -(k / ((1 - fb) * kp)) * t1s                      # the pair's, sigma_1 = tau_1
F1_side = sp.Rational(8, 5) * Hc**2 * Om * tau2_tc          # +8/5 on tau_2
pair_side = -sp.Rational(8, 5) * Hc**2 * Om * sig2_tc       # -8/5 on sigma_2
released = sp.simplify(F1_side.subs(fb, sp.Rational(1, 10)))
report('C17e  k^2 (Phi_A + Phi_H) = (16/9) Hc^2 Omega_g (k/kappa\') tau_1, the same in either phase',
       sp.simplify(F1_side - pair_side) == 0
       and sp.simplify(released - sp.Rational(16, 9) * Hc**2 * Om * k / kp * t1s) == 0)
mixed = -sp.Rational(8, 5) * Hc**2 * Om * tau2_tc           # (F.1)'s tau_2 in the pair's constraint
report('C17e  a quadrupole in one phase with the other phase\'s constraint reverses the sign '
       '(negative control)', sp.simplify(mixed + F1_side) == 0)
# outside the horizon in the radiation era: tau_1 = -(1/2) k eta Phi_A, Hc = 1/eta
ratio = sp.simplify((released / k**2).subs({t1s: -k * eta * PhiA / 2, Hc: 1 / eta}) / PhiA)
report('C17e  outside the horizon in the radiation era (Phi_A + Phi_H)/Phi_A '
       '= -(8/9) Omega_g / (eta kappa\'), negative',
       sp.simplify(ratio + sp.Rational(8, 9) * Om / (eta * kp)) == 0, f'{ratio}')

# --------------------------------------------------------------------------
# C17f -- the line of sight.
mu2, w2 = np.polynomial.legendre.leggauss(400)
worst = 0.0
for ell in (2, 3, 10, 40, 200):
    for xx in (5.0, 37.0, 120.0, 400.0):
        base = 0.5 * np.sum(w2 * eval_legendre(ell, mu2) * np.exp(-1j * xx * mu2))
        rank2 = 0.5 * np.sum(w2 * eval_legendre(ell, mu2) * (mu2**2 - 1 / 3)
                             * np.exp(-1j * xx * mu2))
        j0 = spherical_jn(ell, xx)
        jd = spherical_jn(ell, xx, derivative=True)
        jdd = (ell * (ell + 1) / xx**2 - 1) * j0 - 2 * jd / xx
        ph = (-1j) ** ell
        worst = max(worst, abs(base - ph * j0), abs(rank2 + ph * (jdd + j0 / 3)))
report('C17f  confirmatory (Rayleigh convention): a rank-two source projects with -(j\'\' + j/3) beside the rank-zero j',
       worst < 1e-12, f'{worst:.1e}')
# Q_ab = k^-2 D_<a D_b> Q on Q = e^{i k.x} is -(khat khat - 1/3) Q, so the
# in-scattered quadrupole's kernel is +(j/3 + j''): the matching's rows.
C0, C1, C2, r0, r2 = sp.symbols('C_0 C_1 C_2 r_0 r_2')
rows = sp.Matrix([[1, 0, -k**2 / 3], [0, k, 0], [0, 0, k**2]])
sol = rows.LUsolve(sp.Matrix([0, 0, r2]))
jl, jll = sp.symbols('j jpp')
kern = sp.simplify(sol[0] * jl + sol[2] * k**2 * jll)       # C_0 K + C_2 K''
report('C17f  the matching rows give C_0 = r_2/3 and C_2 = r_2/k^2: the kernel K/3 + K\'\'/k^2',
       sp.simplify(kern - r2 * (jl / 3 + jll)) == 0)
Th2, Vv = sp.symbols('Theta_2 V')
slot = -Vv * sp.Rational(1, 10) * (sp.Rational(15, 2) * Th2) * (jl / 3 + jll)
report('C17f  confirmatory (Ma & Bertschinger, sigma_2 = (15/2) Theta_2): the slot is -(1/4) V Theta_2 (j + 3 j\'\'), '
       'the standard form at the Sachs-Wolfe slot\'s sign',
       sp.simplify(slot + Vv * Th2 * (jl + 3 * jll) / 4) == 0)

# Frame invariance at first order: the exact Lorentz transformation of a
# brightness temperature T(n) = T0 exp(tau(n)) to an observer moving at beta.
def boosted_moments(beta_vec, amp):
    tau_dir = lambda n: amp * (t0 + t1 @ n + np.einsum('abn,ab->n',
                               np.einsum('an,bn->abn', n, n) - I3[:, :, None] / 3, t2))
    b = np.linalg.norm(beta_vec)
    bh = beta_vec / b
    gam = 1 / np.sqrt(1 - b**2)
    npr = e                                             # observed directions
    nb = bh @ npr
    n_src = (npr + (gam * b + (gam - 1) * nb) * bh[:, None]) / (gam * (1 + b * nb))
    T_obs = np.exp(tau_dir(n_src)) * gam * (1 + b * nb)   # D = gamma (1 + beta.n')
    lt = np.log(T_obs)
    m1 = (e * w) @ lt * 3.0
    m2 = np.einsum('abn,n->ab', O2, w * lt) * 7.5
    return m1, m2

def shift(beta_vec, amp):
    """The dipole's and the quadrupole's change under the boost."""
    m1, m2 = boosted_moments(beta_vec, amp)
    n1, n2 = boosted_moments(1e-12 * beta_vec, amp)
    return m1 - n1, m2 - n2

beta = np.array([0.3, -0.2, 0.5]) * 1e-4
d1, _ = shift(beta, 1e-5)
lin_dipole = np.allclose(d1, beta, rtol=1e-3)
# The quadrupole's change splits into the kinematic beta^2 of the isotropic
# part and a piece bilinear in beta and the anisotropy; nothing is linear in
# beta alone, so tau_ab is invariant at first order.
q_iso = np.abs(shift(beta, 0.0)[1]).max()
q_iso_half = np.abs(shift(beta / 2, 0.0)[1]).max()
q_bil = np.abs(shift(beta, 1e-5)[1] - shift(beta, 0.0)[1]).max()
q_bil_amp = np.abs(shift(beta, 2e-5)[1] - shift(beta, 0.0)[1]).max()
q_bil_beta = np.abs(shift(beta / 2, 1e-5)[1] - shift(beta / 2, 0.0)[1]).max()
kinematic = abs(q_iso / q_iso_half - 4) < 0.05
bilinear = abs(q_bil_amp / q_bil - 2) < 0.05 and abs(q_bil / q_bil_beta - 2) < 0.05
print(f'  C17f  boost |beta| = {np.linalg.norm(beta):.1e}: the dipole moves by beta '
      f'(to {np.abs(d1 - beta).max():.1e}); the quadrupole by {q_iso:.1e} from the '
      f'isotropic part (x{q_iso / q_iso_half:.3f} per doubled beta) and {q_bil:.1e} '
      f'bilinear (x{q_bil_amp / q_bil:.3f} per doubled anisotropy, '
      f'x{q_bil / q_bil_beta:.3f} per doubled beta)')
report('C17f  confirmatory of GDE99 (37): a boost moves the dipole by beta and the quadrupole only at second order '
       '(beta^2, beta x anisotropy): the slot and the slip are frame-invariant',
       lin_dipole and kinematic and bilinear)
metrics.update(boost_quadrupole_kinematic=q_iso, boost_quadrupole_bilinear=q_bil)

finish(metrics)
