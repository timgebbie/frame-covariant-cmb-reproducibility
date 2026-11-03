"""Independent 1+3 covariant audit checks for TG-FrameCovariantCMBR-v1.1.6.
All coefficients are transcribed from the supplied PDF text; original source
and visual-render comparison were unavailable. Python 3 + SymPy.
"""
import json, sys, math, hashlib
from pathlib import Path
from fractions import Fraction as F
import sympy as s

results=[]
def check(name, actual, expected=0, details=""):
    d=s.simplify(s.expand(actual-expected))
    if d != 0:
        raise AssertionError(f"{name}: residual {d}")
    results.append({"check":name,"status":"PASS","details":details})
def record(name,details):
    # AMENDED 2026-10-21 (P1-T): was "PASS".  A recorded STATEMENT is not a
    # verified CHECK, and reporting both as PASS overstates what ran.  The
    # summary now counts them separately.
    results.append({"check":name,"status":"RECORDED","details":details})
def finding(name,details):
    """A discrepancy against the paper.  NOT a pass, and not a mere note."""
    results.append({"check":name,"status":"FINDING","details":details})
def control(name, actual, expected):
    """A deliberately WRONG expectation that MUST fail.

    AMENDED 2026-10-21 (P1-T): the file had 191 records and no control, so
    nothing demonstrated that check() can fail at all.  A suite with no
    failing control cannot distinguish "every identity holds" from "the
    comparison is vacuous".
    """
    try:
        check(name, actual, expected)
    except AssertionError:
        results.append({"check":"CONTROL "+name,"status":"FAILED AS REQUIRED",
                        "details":"a wrong expectation is rejected"})
        return
    results.pop()
    raise AssertionError(f"CONTROL {name} did NOT fail: check() is vacuous here")
l,n,E,mu=s.symbols("l n E mu", positive=True)
x,y,z=s.symbols("x y z", real=True)
vs=(x,y,z); r2=x*x+y*y+z*z
lap=lambda p:s.expand(sum(s.diff(p,v,2) for v in vs))
def hp(p,m):
    out=p; d=p; a=s.Integer(1)
    for j in range(1,m//2+1):
        d=lap(d)
        a=-a/(2*j*(2*m-2*j+1))
        out+=a*r2**j*d
    return s.expand(out)
def solid(m,u):
    p=s.Poly(s.legendre(m,mu),mu)
    b=s.factorial(m)/s.factorial2(2*m-1)
    return s.expand(b*sum(c*u**j[0]*r2**((m-j[0])//2) for j,c in p.terms()))

# A. General-rank energy integration by parts: total exponent is always 4.
# -int E^(p+3) d(E^q F)/dE = (p+3) int E^3 F, p+q=1.
c2=(l+1)*(l+2)/((2*l+3)*(2*l+5))
ibp=[
 ("A lower",l,1,l+3),
 ("A upper",-l-1,(l+1)/(2*l+3),-(l+1)*(l-2)/(2*l+3)),
 ("shear lower",l-1,1,l+2),
 ("shear upper",-l-2,c2,-(l-1)*c2),
 ("shear same",s.Rational(-1,2),2*l/(2*l+3),5*l/(2*l+3))]
for label,p,c,want in ibp: check("energy IBP "+label,c*(p+3),want)
control("energy IBP total exponent is 4, not 5",
        ibp[0][2]*(ibp[0][1]+3),ibp[0][1]+4)
# Explicit integral arbiter independent of symbolic integration-by-parts rule.
for L in (2,4,9):
    f=E**3*s.exp(-E)
    expr=-E**(L+2)*s.diff(E**(2-L)*f,E)
    check(f"lower shear direct energy integral l={L}",s.integrate(expr,(E,0,s.oo)),
          (L+2)*s.integrate(E**3*f,(E,0,s.oo)))

# B. Table I: exact redshift/aberration sums.
# NOTE 2026-10-21 (P1-T): the coefficients r and t below are TRANSCRIBED from
# the paper, so this section verifies that Table I is internally consistent --
# that its rows sum as the (4 + rank) rule requires.  It does NOT independently
# derive the coefficients.  Section A's energy rule, with its direct integral
# arbiter, is the check that can fail on the physics.
rows=[
 ("A lower",l-1,1,0,l+3),
 ("A upper",l+1,(l+1)/(2*l+3),-(l+1),-(l+1)*(l-2)/(2*l+3)),
 ("shear lower",l-2,1,0,l+2),
 ("shear upper",l+2,c2,-(l+1)*(l+2)/(2*l+3),-(l-1)*c2),
 ("shear same",l,2*l/(2*l+3),-l,5*l/(2*l+3)),
 ("vorticity",l,0,-l,-l)]
for name,rank,r,t,total in rows:
    check("Table I "+name,4*r+rank*r+t,total)

# C. Non-aligned Cartesian PSTF polynomial tests. No spatial harmonics.
A=s.Matrix([2,-1,3])
sigma=s.Matrix([[2,1,-1],[1,-3,2],[-1,2,1]])
w=s.Matrix([1,2,-1]); e=s.Matrix(vs)
Ae=(A.dot(e)); see=(e.dot(sigma*e))
for m in range(1,7):
    H=solid(m,z)+2*solid(m,x)-solid(m,(x+2*y+2*z)/3)
    check(f"PSTF harmonic trace rank {m}",lap(H))
    if m==3:
        control("a non-harmonic polynomial is not traceless",lap(r2*H),0)
    grad=s.Matrix([s.diff(H,v) for v in vs])
    lower=A.dot(grad)/m
    upper=hp(Ae*H,m+1)
    check(f"non-aligned acceleration product Eq27 rank {m}", Ae*H,
          upper+s.Rational(m,2*m+1)*r2*lower)
    check(f"non-aligned acceleration angular generator rank {m}",
          r2*A.dot(grad)-m*Ae*H,
          -m*upper+s.Rational(m*(m+1),2*m+1)*r2*lower)
    same=hp((sigma*e).dot(grad)/m,m)
    down=0 if m<2 else sum(sigma[i,j]*s.diff(H,vs[i],vs[j])
                           for i in range(3) for j in range(3))/(m*(m-1))
    up=hp(see*H,m+2)
    check(f"non-aligned shear transverse Eq29 rank {m}",
          (sigma*e).dot(grad)/m,
          same+s.Rational(m-1,2*m-1)*r2*down)
    check(f"non-aligned shear product Eq28 rank {m}",see*H,
          up+s.Rational(2*m,2*m+3)*r2*same+
          s.Rational(m*(m-1),(2*m+1)*(2*m-1))*r2**2*down)
    check(f"non-aligned shear angular generator rank {m}",
          r2*(sigma*e).dot(grad)-m*see*H,
          -m*up+s.Rational(3*m,2*m+3)*r2*same+
          s.Rational(m*(m-1)*(m+1),(2*m-1)*(2*m+1))*r2**2*down)
    rotation=e.cross(w).dot(grad)
    check(f"vorticity preserves harmonic rank {m}",lap(rotation))

# D. Lambda recursion and aligned generators, independent polynomial route.
def beta(m): return s.factorial(m)/s.factorial2(2*m-1)
def Lam(m): return beta(m)*s.legendre(m,mu)
for m in range(1,15):
    check(f"Lambda recursion rank {m}",mu*Lam(m),
          Lam(m+1)+s.Rational(m*m,4*m*m-1)*Lam(m-1))
    angular=(1-mu**2)*s.diff(Lam(m),mu)
    check(f"aligned acceleration generator rank {m}",angular,
          -m*Lam(m+1)+s.Rational(m*m*(m+1),(2*m-1)*(2*m+1))*Lam(m-1))
    lower2=s.S(0) if m<2 else s.Rational(m*m*(m-1)**2*(m+1),
                        (2*m-3)*(2*m-1)**2*(2*m+1))*Lam(m-2)
    check(f"aligned shear generator rank {m}",mu*angular,
          -m*Lam(m+2)+s.Rational(m*(m+1),(2*m-1)*(2*m+3))*Lam(m)+lower2)
ap=(l+1)*(l+2)/(2*l+3); am=l*(l-1)/(2*l-1)
sp=(l+1)*(l+2)*(l+3)/((2*l+3)*(2*l+5))
sm=l*(l-1)*(l-2)/((2*l-1)*(2*l-3))
s0=l*(l+1)/((2*l-1)*(2*l+3))
check("Eq83 exact acceleration residual",ap-am,2*(2*l*l+2*l-1)/((2*l-1)*(2*l+3)))
check("Eq84 exact shear residual",sp-sm,
      3*(4*l**4+8*l**3-11*l*l-15*l+6)/((2*l-3)*(2*l-1)*(2*l+3)*(2*l+5)))
check("Eq85 rank-preserving coefficient",
      l*(l/(2*l-1)-(l+1)**2/(4*(l+1)**2-1)-l*l/(4*l*l-1)),s0)
check("derivative weight A",s.limit((ap+am)/l,l,s.oo),1)
check("derivative weight shear",s.limit(2*(sp+sm)/l,l,s.oo),1)
check("constant residual A",s.limit(ap-am,l,s.oo),1)
check("constant residual shear total",s.limit(sp-sm+s0,l,s.oo),1)
check("Figure3 signed residual asymptote",s.limit(l*l*(ap-am-sp+sm-s0),l,s.oo),s.Rational(-1,2))
finding("Figure3 signed residual sign",
   "The signed residual (83)-(84)-(85) tends to -1/(2 l^2). If Figure 3 or its "
   "caption prints +1/(2 l^2) as the signed value rather than the magnitude, "
   "that is a discrepancy against the paper and belongs in the corrections "
   "record, not in a note with PASS beside it. Paper 1 Sec. 6.3's text states "
   "O(l^-2) without a sign, so the text is unaffected; the FIGURE has not been "
   "checked here. PROMOTED from a record 2026-10-21 (P1-T).")
# All five angular coefficient identities at 297 ranks in exact Fraction arithmetic.
for L in range(4,301):
    got=[
      F((L+1)*(L+2),2*L+3)*F(L+1,2*L+1),
      F(-(L-1)),
      F((L+3)*(L+1)*(L+2),(2*L+3)*(2*L+5))*F((L+1)*(L+2),(2*L+1)*(2*L+3)),
      F(-(L-2)),
      L*(F(L,2*L-1)-F((L+1)**2,4*(L+1)**2-1)-F(L**2,4*L**2-1))]
    want=[
      F((L+1)**2*(L+2),(2*L+1)*(2*L+3)),F(-(L-1)),
      F((L+1)**2*(L+2)**2*(L+3),(2*L+1)*(2*L+3)**2*(2*L+5)),F(-(L-2)),
      F(L*(L+1),(2*L-1)*(2*L+3))]
    assert got==want
record("1485 exact rational coefficient comparisons","Five identities at each rank l=4,...,300.")

# E. Boost generator from kinematics. J_ij = D_j v_i.
j=s.Matrix(3,3,s.symbols("j0:9")); vdot=s.Matrix(s.symbols("dv0:3")); h=s.symbols("H")
sheart=(j+j.T)/2-s.eye(3)*s.trace(j)/3
rot=(j-j.T)/2
P=s.eye(3)-e*e.T
# Difference is along e; screen kills it on the unit sphere.
deltak=vdot+sheart*e+rot*e
wanted=vdot+j*e
res=P*(deltak-wanted)
for i in range(3):check(f"boost shear/vorticity recombination component {i}",
                       res[i],s.trace(j)*e[i]*(r2-1)/3)
# AMENDED 2026-10-21 (P1-T): the +Hv was RECORDED.  It is the load-bearing
# coefficient of the frame law and it is four lines of index algebra, so it is
# now DERIVED.  Note what section E above actually establishes: it decomposes
# J_ij = D_j v_i, which is the SHEAR boost sigma~ = sigma + D_<a v_b>.  It
# never touches grad_b u_a, which is where the acceleration boost comes from.
Theta=s.symbols("Theta")
# A_a = u^b grad_b u_a ; with u~ = u + v,  A~_a = A_a + vdot_a + v^b grad_b u_a
# and grad_b u_a = -A_a u_b + (1/3) h_ab Theta + eps_abc w^c + sigma_ab  [C2.2].
# Contract with v^b, using v^b u_b = 0 and h_ab v^b = v_a:
vv=s.Matrix(s.symbols("v0:3"))
A_vec=s.Matrix(s.symbols("A0:3"))
sig=s.Matrix(3,3,s.symbols("s0:9")); sig=(sig+sig.T)/2-s.eye(3)*s.trace(sig)/3
om=s.Matrix(s.symbols("w0:3"))
def eps_contract(vv,om):
    return s.Matrix([sum(s.LeviCivita(i,jj,kk)*vv[jj]*om[kk]
                         for jj in range(3) for kk in range(3)) for i in range(3)])
grad_u_dot_v = Theta/3*vv + eps_contract(vv,om) + sig*vv
for i in range(3):
    check(f"acceleration boost: the +Hv term, component {i}",
          grad_u_dot_v[i] - (sig*vv)[i] - eps_contract(vv,om)[i],
          Theta/3*vv[i],
          "Theta/3 = H, so A~ = A + vdot + Hv; the shear and vorticity pieces "
          "are O(eps^2) since sigma, omega and v are each first order.")
record("boost H term, now derived",
       "A~_a = A_a + vdot_a + Hv_a + sigma_ab v^b + eps_abc v^b w^c. The +Hv "
       "is (Theta/3) h_ab v^b from C2.2's expansion term; the last two are "
       "O(eps^2). This is the term that pairs against the -Hv the moving "
       "projector puts into D~_a ln T.")

# F. Conformal spatial geometry and normalization.
g=s.Matrix(s.symbols("g0:3"))
Gamma=lambda i,jj,k: s.KroneckerDelta(i,jj)*g[k]+s.KroneckerDelta(i,k)*g[jj]-s.KroneckerDelta(jj,k)*g[i]
for m in range(1,5):
    H=solid(m,z)+2*solid(m,x)
    grad=s.Matrix([s.diff(H,u) for u in vs])
    # On r^2=1, connection terms sum to g.grad(H).
    # With contravariant multipoles Pi^I=e^(-m Phi) pi^I, differentiating
    # the physical components adds -m(e.g)H, leaving P g.grad(H).
    check(f"conformal normalization cancellation rank {m}",
          g.dot(grad)-m*g.dot(e)*H,
          (g-e*g.dot(e)).dot(grad))
Phi=s.Function("Phi")(*vs)
C=lambda i,jj,k: (s.KroneckerDelta(i,jj)*s.diff(Phi,vs[k])+
 s.KroneckerDelta(i,k)*s.diff(Phi,vs[jj])-s.KroneckerDelta(jj,k)*s.diff(Phi,vs[i]))
for i in range(3):
 for jj in range(3):
    R=sum(s.diff(C(k,i,jj),vs[k])-s.diff(C(k,i,k),vs[jj]) for k in range(3))
    check(f"conformal Ricci {i}{jj}",R,-s.diff(Phi,vs[i],vs[jj])-s.KroneckerDelta(i,jj)*sum(s.diff(Phi,u,2) for u in vs))
# Shear propagation/Gauss cancellation, all symbols denote STF tensors.
sdot,Th,sh,DA,AA,pi,EW,ss=s.symbols("sdot Th sh DA AA pi EW ss")
gauss=-sdot-Th*sh+DA+AA+pi
shear_eq=DA-s.Rational(2,3)*Th*sh+AA-ss-EW+pi/2
check("Gauss Eq65 to Eq66",gauss.subs(sdot,shear_eq),EW+pi/2-Th*sh/3+ss)

# G. Proper/conformal time and the growth factor.
a,q,H0,Om,D,Ddot,delta=s.symbols("a q H0 Om D Ddot delta",nonzero=True)
H=s.symbols("H")
Phi0=3*H0**2*Om*delta/(2*q*q)
ph=Phi0*D/a; phdot=Phi0*(Ddot-H*D)/a
k=q/a; rho=3*H0**2*Om/a**3
check("Eq49 to Eq50 with physical k",2*(-k*k*(phdot+H*ph))/rho,-Ddot*delta)
chi,cs,ct=s.symbols("chi cs ct",positive=True)
own=s.integrate(1-chi/cs,(chi,0,cs)); inserted=s.integrate(1-chi/ct,(chi,0,cs))
check("Figure2 total efficiency ratio",inserted/own,2-cs/ct)
# Exchange of integrations with a generic polynomial force.
force=2+3*chi+chi**2
u=s.symbols("u")
acc=-s.integrate(force.subs(chi,u),(u,0,chi))
check("Eq68-69 distance factor",s.integrate(acc,(chi,0,cs)),
      -s.integrate((cs-chi)*force,(chi,0,cs)))
b,GM=s.symbols("b GM",positive=True)
bend=GM/b*(1+z/s.sqrt(b*b+z*z))
check("point-mass accumulation derivative",s.diff(bend,z),GM*b/(b*b+z*z)**s.Rational(3,2))
check("Figure1 fraction within one impact parameter",
      (bend.subs(z,b)-bend.subs(z,-b))/(2*GM/b),1/s.sqrt(2))

# H. Power: independent Taylor/angular calculation.
# AMENDED 2026-10-21 (P1-T): `mu` below is the FLAT-SKY 2D angle cosine, where
# <mu^2> = 1/2.  Sections C, D and J use the same symbol for the 3D polar
# cosine, where <mu^2> = 1/3.  One symbol, two meanings, in one file -- which
# is the hazard T-33 is about.  The averaging convention is now asserted.
L,ell,C0,C1,C2=s.symbols("L ell C0 C1 C2",positive=True)
kernel=(ell*L*mu-L*L)**2
d=-L*mu+L*L*(1-mu*mu)/(2*ell)
product=s.expand(kernel*(C0+d*C1+L*L*mu*mu*C2/2))
def av(poly):
    p=s.Poly(poly,mu)
    return s.expand(sum(coef*(s.binomial(power[0],power[0]//2)/2**power[0] if power[0]%2==0 else 0)
                        for power,coef in p.terms()))
check("av() is the 2D flat-sky average, not the 3D spherical one",
      av(mu**2),s.Rational(1,2),
      "3D would be 1/3; section H is flat-sky and 1/2 is correct there")
check("av() fourth moment",av(mu**4),s.Rational(3,8))
control("av() is NOT the 3D spherical average",av(mu**2),s.Rational(1,3))
check("quartic residual AppendixC",av(product.coeff(L,4)),
      s.Rational(3,16)*ell*ell*C2+s.Rational(17,16)*ell*C1+C0)
check("leading ell squared cancellation",av(product.coeff(L,2)),ell*ell*C0/2)
nu=s.symbols("nu")
check("power-law residual",s.Rational(3,16)*nu*(nu+1)-s.Rational(17,16)*nu+1,(nu-2)*(3*nu-8)/16)
# WITHDRAWN 2026-10-21 (P1-T).  The original read
#     gain = A*B/2 ;  R = B/2 ;  loss = R*A
# which is A*B/2 == (B/2)*A -- commutativity of multiplication.  It cannot
# fail and it establishes nothing about variance conservation.  Confirmed
# symbolically: gain-loss simplifies to 0 before either integral is done.
record("variance conservation NOT established",
       "The original gain-loss check was A*B/2 == (B/2)*A, a tautology. "
       "Conservation needs the lensed spectrum's full second moment including "
       "the linear-quadratic cross term, which is not computed here. The "
       "external review's point stands: quartic scaling alone proves neither "
       "conservation nor redistribution.")

# I. Counterexamples and limits, not failures of the central covariant result.
# A time integral at fixed x is not a characteristic solution when D_a != 0.
T,qq,zz,muv=s.symbols("T qq zz muv",nonzero=True,real=True)
transport=(s.sin(qq*zz)-s.sin(qq*(zz-muv*T)))/(qq*muv)
check("source with free propagation solves transport",s.diff(transport,T)+muv*s.diff(transport,zz),s.cos(qq*zz))
naive=T*s.cos(qq*zz)
check("plain source integral transport residual",s.diff(naive,T)+muv*s.diff(naive,zz)-s.cos(qq*zz),-T*muv*qq*s.sin(qq*zz))
record("Eq48 interpretation warning","A plain time integral at a fixed spatial-mode label does not include the free propagator; Eq48 is only an illustrative source weight unless propagation is supplied.")
record("radial-gradient counterexample","For a local 1+3 scalar mode with k_parallel=k_perp=ell/chi_s, delta_chi*D_parallel tau is O(epsilon^2 ell), unless nearly transverse source support is assumed.")
record("smooth-sequence qualification","Slow change over four ranks alone does not imply ell*f' is O(f); f(l)=exp(i*l/L0), L0>>4 fixed, retains ell/L0 response.")
record("uniform convergence qualification","An isotropic quadratic potential has zero STF Hessian but nonzero trace Hessian; it carries isotropic focusing even though no shear.")
# J. Normalizations and harmonic phase checks, independent of coefficient sums.
for m in range(1,9):
    H=solid(m,z); poly=s.Poly(H,x,y,z)
    norm=sum(c*c/(s.factorial(m)/s.prod(s.factorial(a) for a in powers))
             for powers,c in poly.terms())
    check(f"PSTF tensor norm beta rank {m}",norm,beta(m))
    check(f"one-index contraction rank {m}",s.diff(H,z)/m,
          s.Rational(m,2*m-1)*solid(m-1,z))
    check(f"angular orthogonality normalization rank {m}",
          2*s.pi*s.integrate(Lam(m)**2,(mu,-1,1)),
          4*s.pi*beta(m)**2/(2*m+1))
    check(f"real harmonic gradient rank {m}",s.diff(s.cos(z-m*s.pi/2),z),
          -s.cos(z-(m+1)*s.pi/2))
    check(f"real harmonic divergence rank {m}",
          s.Rational(m+1,2*m+1)*s.diff(s.cos(z-(m+1)*s.pi/2),z),
          s.Rational(m+1,2*m+1)*s.cos(z-m*s.pi/2))
    check(f"STF projector dimension rank {m}",
          s.binomial(m+2,2)-s.binomial(m,2),2*m+1)
# Gaussianity alone does not license the independent Wick factorization at order four.
c=s.symbols("corr",real=True)
u1,u2=s.symbols("u1 u2")
gp=s.Poly(s.expand(u1**2*(c*u1+s.sqrt(1-c*c)*u2)**2),u1,u2)
def normal_moment(k): return 0 if k%2 else (s.S.One if k==0 else s.factorial2(k-1))
four=sum(coef*normal_moment(power[0])*normal_moment(power[1]) for power,coef in gp.terms())
check("correlated Gaussian fourth moment",four,1+2*c*c)
record("statistical qualification","Joint Gaussianity removes the cubic expectation, but correlated fields have extra fourth-order Wick contractions; it cannot replace independence in Eq90.")
from collections import Counter
tally=Counter(r["status"] for r in results)
out={"sympy_version":s.__version__,"python_version":sys.version.split()[0],
     "total_records":len(results),"by_status":dict(tally),
     "verified_checks":tally.get("PASS",0),
     "recorded_statements":tally.get("RECORDED",0),
     "findings":tally.get("FINDING",0),
     "controls_that_failed_as_required":tally.get("FAILED AS REQUIRED",0),
     "checks":results,
     "scope":"Independent 1+3 covariant algebra; supplied PDF text only; source ZIP and rendered-page verification pending.",
     "amendments":"P1-T 2026-10-21: record() no longer reports PASS; the "
                  "tautological variance gain-loss check is withdrawn; the +Hv "
                  "acceleration boost is derived rather than recorded; the mu "
                  "convention collision between sections C/D/J and H is "
                  "asserted; the Figure 3 sign item is promoted to a FINDING; "
                  "deliberately failing controls added, the file previously "
                  "having none."}
root=Path(__file__).resolve().parent
(root/"independent-results.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
print(json.dumps({"total_records":len(results),"by_status":dict(tally),
                  "sympy":s.__version__,"scope":out["scope"]},indent=2))
