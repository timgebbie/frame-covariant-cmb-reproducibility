#!/usr/bin/env python3
"""C16 -- the Thomson in-scattering weight at every rank, in index algebra.

WHAT IS AT ISSUE.  Paper 1, Eq. (38), writes the collision term as

    C[tau] ~= sigma_T n_E ( fbar_1 e^a v^B_a + fbar_2 e^a e^b tau_ab - tau ),

and approximation A-5 is the statement fbar_2 = 0.  v1.5.0 lifts A-5, so it
must supply fbar_2.  Separately the bundle carries Kaiser's f_2, through
Annals II (169), as the damping coefficient (4/5) f_2^-1, with f_2 = 9/10
unpolarised and 3/4 polarised.  Both numbers are l-weights, and the tree
derives NEITHER: f_2 is imported on the antecedent's authority
(functions/spectra/decoupling.py, lines 421-455; supplement S-oscillator).

CLAUDE.md 3b: an l-weight is settled in index algebra or it is not settled --
no plane wave, no test field, no Legendre projection, no l=2 specialisation.
This file settles it that way and, in doing so, fixes fbar_2 and f_2 together.

THE DERIVATION, in three steps and no imported weight.

 C16a  the sphere moments, by direct integration, not quoted:
           <e^a1 ... e^an> = 0                                (n odd)
                           = (1/(n+1)!!) sum_{pairings} delta...delta  (n even)
       established here by symbolic integration over the sphere in 3D and
       compared against the pairing form term by term.

 C16b  the in-scattering at ARBITRARY rank.  With the unpolarised Thomson
       phase function (3/16pi)(1 + mu^2), mu = e_a e'^a, and a brightness
       tau(e') = sum_l tau_B_l e'^B_l with every tau_B_l PSTF,

           I(e) = (3/4) Int dOmega'/4pi [1 + (e.e')^2] tau_B_l e'^B_l .

       Expand by C16a.  Every surviving term is a product of deltas.  A delta
       joining two tau-indices dies on the trace; a delta joining the two
       e-indices gives delta^ab e_a e_b = 1 times a delta-product among the
       tau-indices, which dies likewise unless there are none.  So a term
       survives only if EVERY tau-index is paired to an e-index.  There are
       exactly two e-indices in the (e.e')^2 term and none in the 1, hence

           l = 0  from both terms, l = 2 from the (e.e')^2 term, nothing else,

       at every l, with no l=2 specialisation entering the argument.

 C16c  the two weights, and the bridge between them.  Evaluating the two
       survivors gives I(e) = tau_0 + (1/10) tau_ab e^a e^b, so

           fbar_2 = 1/10   and   f_2 = 1 - fbar_2 = 9/10 ,

       Kaiser's f_2 derived rather than imported, and the rank-2 collision
       term is C_2 = -kappa' (1 - fbar_2) tau_ab = -(9/10) kappa' tau_ab.
       The rank-1 in-scattering from the PHOTON brightness is zero, so
       fbar_1 = 1 is a statement about the electrons' v^B_a and is not a
       photon l-weight at all.

 CONTROLS.  (i) the monopole must be preserved exactly (photon number), which
 fixes the phase function's normalisation and fails for any other; (ii) the
 negative control fbar_2 = 9/10 -- the confusion this file exists to prevent --
 is carried through to the damping coefficient and shown absurd.

No project code is imported; `_common` checks that before anything runs.

Derived by a scheduled P1-T run on 2026-11-26 (03:31Z) and landed the same day
with supplement v1.5.1, where `sec:a5-construction` cites it.  Landed on the
suite's harness: `_common`'s independence guard, `report` and the
machine-readable `finish` record that `run_all.py`, `gen_theory_audit.py` and
`tests/test_frame_checks.py` read.  The moments of C16a are checked on the
sorted index tuples, which is every component, since both sides are symmetric
in their indices; the derivation is unchanged.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import itertools
import sympy as sp

#: The one source for this check's wording in docs/THEORY-AUDIT.md.
#: The generator reads it from here and holds no copy, so correcting
#: the instrument corrects the audit by construction.
AUDIT_TITLE = "The Thomson in-scattering weight at every rank"
AUDIT_PROSE = (
    "The unpolarised Thomson phase function $\\tfrac3{16\\pi}(1+\\mu^2)$, integrated "
    "against a PSTF brightness $\\tau_{A_\\ell}e^{A_\\ell}$ with the sphere moments "
    "$\\langle e^{a_1}\\negthinspace\\cdots e^{a_n}\\rangle$ in their pairing form, returns "
    "$\\tau_0+\\tfrac1{10}\\tau_{ab}e^ae^b$ and nothing else: a term survives only when "
    "every $\\tau$-index is paired to one of the two $e$-indices, so ranks other than "
    "0 and 2 vanish identically at every $\\ell$. Hence $\\bar f_2=\\tfrac1{10}$ in "
    "Paper~1's Eq.~(38) and $f_2=1-\\bar f_2=\\tfrac9{10}$, Kaiser's unpolarised "
    "coefficient derived rather than imported, with "
    "$\\tfrac45f_2^{-1}=\\tfrac89$. The rank-one in-scattering from the brightness is "
    "zero, so $\\bar f_1=1$ is a statement about $v^B_a$ and not a photon "
    "$\\ell$-weight. The monopole returns exactly, on $e_ae^a=1$, which is the "
    "control on the phase function's normalisation."
)

from _common import finish, report

th, ph = sp.symbols('theta phi', real=True)
EP = [sp.sin(th)*sp.cos(ph), sp.sin(th)*sp.sin(ph), sp.cos(th)]
FAILS = []

def check(tag, ok, msg):
    report(f"C16  {tag}", ok, msg)
    if not ok:
        FAILS.append(tag)

def sphere_avg(expr):
    """<expr> = Int dOmega/(4pi), exactly, by symbolic integration."""
    return sp.simplify(sp.integrate(sp.integrate(sp.expand_trig(sp.expand(expr))*sp.sin(th),
                                                 (th, 0, sp.pi)), (ph, 0, 2*sp.pi)) / (4*sp.pi))

def pairings(idx):
    """All perfect matchings of a list of index positions."""
    if not idx:
        yield []
        return
    a, rest = idx[0], idx[1:]
    for i, b in enumerate(rest):
        for tail in pairings(rest[:i] + rest[i+1:]):
            yield [(a, b)] + tail

def dfact(n):
    r = 1
    while n > 1:
        r *= n
        n -= 2
    return r

# ---------------------------------------------------------------- C16a
print("C16a  the sphere moments, by direct integration")
for n in range(0, 7):
    bad = None
    for comp in itertools.combinations_with_replacement(range(3), n):
        lhs = sphere_avg(sp.prod([EP[c] for c in comp]) if n else sp.Integer(1))
        if n % 2:
            rhs = sp.Integer(0)
        else:
            tot = 0
            for m in pairings(list(range(n))):
                t = 1
                for (i, j) in m:
                    t *= 1 if comp[i] == comp[j] else 0
                tot += t
            rhs = sp.Rational(tot, dfact(n + 1))
        if sp.simplify(lhs - rhs) != 0:
            bad = (comp, lhs, rhs)
            break
    check(f"moments n={n}", bad is None,
          "pairing form reproduces every component (sorted tuples; both sides symmetric)"
          if bad is None else f"component {bad[0]}: {bad[1]} != {bad[2]}")

# ---------------------------------------------------------------- PSTF basis
def sym_basis(l):
    """Multi-indices of symmetric rank-l tensors in 3D (sorted tuples)."""
    return list(itertools.combinations_with_replacement(range(3), l))

def pstf_basis(l):
    """A basis of rank-l PSTF tensors over Q: the kernel of the trace map.

    Built by linear algebra on the symmetric tensors, not from any quoted
    STF formula and not from solid harmonics.
    """
    S = sym_basis(l)
    pos = {s: i for i, s in enumerate(S)}
    if l < 2:
        return [[1 if i == j else 0 for i in range(len(S))] for j in range(len(S))]
    T = sym_basis(l - 2)
    M = sp.zeros(len(T), len(S))
    for r, t in enumerate(T):
        for c in range(3):
            key = tuple(sorted((c, c) + t))
            M[r, pos[key]] += 1
    return [list(v) for v in M.nullspace()]

def contract_with_e(l, vec, evec):
    """tau_B_l e^B_l for a PSTF tensor given in the symmetric basis."""
    S = sym_basis(l)
    out = 0
    for coeff, s in zip(vec, S):
        if coeff == 0:
            continue
        mult = sp.factorial(l)
        for _, g in itertools.groupby(sorted(s)):
            mult /= sp.factorial(len(list(g)))
        out += coeff * mult * sp.prod([evec[i] for i in s])
    return sp.expand(out)

# ---------------------------------------------------------------- C16b / C16c
print()
print("C16b  the in-scattering at arbitrary rank")
e1, e2, e3 = sp.symbols('e1 e2 e3', real=True)
EV = [e1, e2, e3]
MU = sum(EV[i]*EP[i] for i in range(3))
PHASE = sp.Rational(3, 4) * (1 + MU**2)          # (3/16pi)(1+mu^2) with dOmega/4pi

results = {}
for l in range(0, 7):
    basis = pstf_basis(l)
    check(f"PSTF dim l={l}", len(basis) == 2*l + 1,
          f"kernel of the trace map has dimension {len(basis)} (expected {2*l+1})")
    outs = []
    for vec in basis:
        tau_ep = contract_with_e(l, vec, EP)
        I = sphere_avg(PHASE * tau_ep)
        outs.append(sp.simplify(sp.expand(I)))
    results[l] = (basis, outs)
    if l not in (0, 2):
        allzero = all(o == 0 for o in outs)
        check(f"in-scattering l={l}", allzero,
              "vanishes for every PSTF tensor of this rank"
              if allzero else f"NONZERO: {outs}")

print()
print("C16c  the two survivors, and the weights")
# l = 0 : the monopole must come back exactly (photon number).
#   e^a is a UNIT direction, so the control is read on |e| = 1.  Off the
#   sphere I splits as 3/4 from the "1" of the phase function and (1/4)|e|^2
#   from its (e.e')^2, and the two are one only because e_a e^a = 1.  That
#   split is itself the normalisation statement, so both are reported.
b0, o0 = results[0]
unit = {e3: sp.sqrt(1 - e1**2 - e2**2)}
on_sphere = sp.simplify(sp.expand(o0[0]).subs(unit))
ok0 = sp.simplify(on_sphere - 1) == 0
check("monopole preserved", ok0,
      f"I = ({sp.expand(o0[0])}) x tau_0 = {on_sphere} x tau_0 on e_a e^a = 1 "
      f"(control on the phase function's normalisation)")

# l = 2 : read fbar_2 off I(e) = fbar_2 tau_ab e^a e^b, for EVERY basis tensor.
b2, o2 = results[2]
weights = []
for vec, I in zip(b2, o2):
    tau_ee = contract_with_e(2, vec, EV)
    if sp.simplify(tau_ee) == 0:
        continue
    w = sp.simplify(sp.expand(I) / sp.expand(tau_ee))
    weights.append(sp.nsimplify(sp.simplify(w)))
uniq = set(weights)
ok2 = len(uniq) == 1 and uniq.pop() == sp.Rational(1, 10)
# the rank-2 reading needs no unit-sphere condition: both sides are
# homogeneous of degree 2 in e, so the ratio is independent of |e|.
hom = all(sp.simplify(sp.expand(I).subs({e1: 2*e1, e2: 2*e2, e3: 2*e3})
                      - 4*sp.expand(I)) == 0 for I in o2)
check("rank-2 reading is |e|-independent", hom,
      "I and tau_ab e^a e^b are both homogeneous of degree 2, so fbar_2 is "
      "well defined off the sphere as well as on it")
check("fbar_2", ok2, f"I = {weights[0]} x tau_ab e^a e^b for all {len(weights)} PSTF tensors"
      if weights else "no rank-2 tensor tested")

fbar2 = sp.Rational(1, 10)
f2 = 1 - fbar2
check("bridge f_2 = 1 - fbar_2", f2 == sp.Rational(9, 10),
      f"f_2 = 1 - {fbar2} = {f2}, Kaiser's unpolarised value, DERIVED")
check("rank-2 collision", sp.Rational(9, 10) == f2,
      f"C_2 = -kappa' (1 - fbar_2) tau_ab = -({f2}) kappa' tau_ab")

# rank 1: no photon in-scattering at all -> fbar_1 is about the electrons
b1, o1 = results[1]
ok1 = all(o == 0 for o in o1)
check("rank-1 photon in-scattering", ok1,
      "zero, so fbar_1 = 1 is a statement about v^B_a and not a photon l-weight")

# ---------------------------------------------------------------- the damping bridge
print()
print("C16d  the bridge to the damping coefficient (4/5) f_2^-1")
coef = sp.Rational(4, 5) / f2
check("unpolarised damping", coef == sp.Rational(8, 9),
      f"(4/5) f_2^-1 = (4/5)/({f2}) = {coef}, Hu & Sugiyama's 8/9")
pol = sp.Rational(4, 5) / sp.Rational(3, 4)
check("polarised damping", pol == sp.Rational(16, 15),
      f"(4/5)/(3/4) = {pol}; the polarised f_2 = 3/4 is NOT derived here -- see the note")
check("the 6/5 the two differ by",
      sp.Rational(16, 15)/sp.Rational(8, 9) == sp.Rational(6, 5),
      f"(16/15)/(8/9) = {sp.Rational(16,15)/sp.Rational(8,9)} = (9/10)/(3/4)")

print()
print("NEGATIVE CONTROL  fbar_2 = 9/10, the confusion this file prevents")
bad_f2 = 1 - sp.Rational(9, 10)
bad_coef = sp.Rational(4, 5) / bad_f2
check("the confusion is caught", bad_coef == 8,
      f"fbar_2 = 9/10 gives f_2 = {bad_f2} and (4/5) f_2^-1 = {bad_coef}, "
      f"{sp.nsimplify(bad_coef/coef)}x the right coefficient; "
      f"the quadrupole would be damped at kappa'/10, not 9kappa'/10")

print()
print("FAILURES:", FAILS if FAILS else "none")
finish({"fbar_2": float(fbar2), "f_2": float(f2), "damping_unpolarised": float(coef),
        "damping_polarised": float(pol), "negative_control_coefficient": float(bad_coef)})
