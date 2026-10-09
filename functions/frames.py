r"""Frame change at first order, derived rather than transcribed.

**Acceptance criterion 2, and decision S14.** *Annals II*'s source decomposes by
rank --- $\mathcal B_0=-\tfrac13\mathrm D^a\tau_a$,
$\mathcal B_1=\mathrm D_a\ln T+A_a$, $\mathcal B_2=\sigma_{ab}$ --- and the
question the criterion asks is what happens to each under a change of the
threading $u^a\to\tilde u^a=u^a+v^a$.

The target S14 supplies is $\tilde{\mathcal B}_1=\mathcal B_1+\dot v_a$: **no
shear, and no $Hv$.** Any other result from the generic-$u^a$ construction is a
bug in this bundle. This module is where that is settled, and it settles it by
**deriving both halves** rather than quoting them, because the content of the
claim is a cancellation and a cancellation quoted is a cancellation assumed.

**The order bookkeeping is explicit and machine-checked.** Every perturbation
carries the symbol $\varepsilon$, and so does $v^a$; terms like
$\sigma_{ab}v^b$ then carry $\varepsilon^2$ and are removed by series expansion
rather than by an author deciding they are small. That is why this module is
symbolic: the claim is an exact identity in $\varepsilon$, not an agreement to
some tolerance.

---

**The temperature gradient.** $\mathrm D_a$ is $h_a{}^b\nabla_b$, and the
projector itself moves: $\tilde h_{ab}=h_{ab}+2u_{(a}v_{b)}+O(v^2)$. For a
scalar $f$,

$$\tilde{\mathrm D}_a f = \tilde h_a{}^b\nabla_b f
  = \mathrm D_a f + v_a\,\dot f + O(\varepsilon^2),$$

so with $f=\ln T$ and $(\ln T)^{\textstyle\cdot}=-H$ in the background,

$$\tilde{\mathrm D}_a\ln T = \mathrm D_a\ln T - H v_a .$$

**The acceleration.** $A_a=\dot u_a=u^b\nabla_b u_a$, so

$$\tilde A_a = (u^b+v^b)\nabla_b(u_a+v_a)
  = A_a + \dot v_a + v^b\nabla_b u_a + O(\varepsilon^2),$$

and $\nabla_b u_a = -A_au_b+\tfrac13h_{ab}\Theta+\sigma_{ab}+\epsilon_{abc}\omega^c$
gives $v^b\nabla_b u_a = Hv_a + \sigma_{ab}v^b + \epsilon_{abc}v^b\omega^c$.
**The shear and vorticity terms are $O(\varepsilon^2)$** --- that is *why* no
shear appears in $\tilde{\mathcal B}_1$, and it is a statement about order, not
about rank. S14 reaches the same place by observing that $\sigma_{ab}$ is rank
two and $\mathcal B_1$ is rank one; both are true and the order argument is the
one this module can check.

**So the $Hv$ cancels structurally.** It enters $\tilde{\mathrm D}_a\ln T$ with a
minus sign, from $v_a\dot f$ with $\dot{\overline{\ln T}}=-H$, and
$\tilde A_a$ with a plus sign, from $\tfrac13\Theta=H$ in $v^b\nabla_bu_a$. It
is the **same** $H$ twice. The cancellation is therefore not a coincidence of
two independently derived coefficients, and the test asserts that each half
carries its $Hv$ before asserting that the sum does not.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

__all__ = [
    "EPS",
    "FrameChange",
    "bracket_rank0",
    "bracket_rank1",
    "bracket_rank2",
    "boosted_acceleration",
    "boosted_shear",
    "boosted_temperature_gradient",
    "roundtrip_residual",
]

#: The smallness parameter every perturbation carries. Orders are tracked with
#: it rather than argued about, so "second order" is a fact sympy checks.
EPS = sp.Symbol("varepsilon", positive=True)


def _vec(name: str) -> sp.Matrix:
    """A spatial 3-vector of first-order quantities, carrying one power of EPS."""
    return sp.Matrix(3, 1, lambda i, _j: EPS * sp.Symbol(f"{name}_{i+1}", real=True))


def _sym_traceless(name: str) -> sp.Matrix:
    """A symmetric trace-free 3x3 of first-order quantities, one power of EPS."""
    a, b, c, d, e = (sp.Symbol(f"{name}_{s}", real=True) for s in ("11", "12", "13", "22", "23"))
    return EPS * sp.Matrix([[a, b, c], [b, d, e], [c, e, -a - d]])


@dataclass(frozen=True)
class FrameChange:
    r"""A first-order change of threading $u^a\to u^a+v^a$.

    Everything here is symbolic and carries its order in `EPS`. `H` is the
    background expansion rate $\tfrac13\Theta$ and is **zeroth order** --- it
    multiplies $v_a$ to make a first-order term, which is the whole subject of
    the cancellation.
    """

    v: sp.Matrix
    v_dot: sp.Matrix
    H: sp.Symbol
    sigma: sp.Matrix
    omega: sp.Matrix

    @classmethod
    def generic(cls) -> "FrameChange":
        """A boost with nothing special about it: no frame chosen, no term dropped."""
        return cls(
            v=_vec("v"), v_dot=_vec("vdot"), H=sp.Symbol("H", real=True),
            sigma=_sym_traceless("sigma"), omega=_vec("omega"),
        )


def _first_order(expr):
    """Drop everything beyond O(EPS). The only place an order argument is made."""
    return sp.expand(sp.Matrix(expr).applyfunc(
        lambda e: sp.series(sp.expand(e), EPS, 0, 2).removeO()
    ))


def boosted_temperature_gradient(grad_ln_T: sp.Matrix, fc: FrameChange) -> sp.Matrix:
    r"""$\tilde{\mathrm D}_a\ln T = \mathrm D_a\ln T + v_a\,\dot{\overline{\ln T}}$.

    The projector moves with the frame, which is the entire origin of the extra
    term; $\dot{\overline{\ln T}} = -H$ in the background supplies its sign.
    """
    return _first_order(grad_ln_T + fc.v * (-fc.H))


def boosted_acceleration(accel: sp.Matrix, fc: FrameChange) -> sp.Matrix:
    r"""$\tilde A_a = A_a + \dot v_a + v^b\nabla_b u_a$, expanded and truncated.

    $v^b\nabla_bu_a$ is written **in full** --- $Hv_a$ together with the shear
    and vorticity contractions --- and the truncation then removes the latter
    two because they are $O(\varepsilon^2)$. Writing only the $Hv_a$ term would
    assume the result this module exists to establish.
    """
    shear_term = fc.sigma * fc.v
    vort_term = sp.Matrix([
        fc.v[1] * fc.omega[2] - fc.v[2] * fc.omega[1],
        fc.v[2] * fc.omega[0] - fc.v[0] * fc.omega[2],
        fc.v[0] * fc.omega[1] - fc.v[1] * fc.omega[0],
    ])
    return _first_order(accel + fc.v_dot + fc.H * fc.v + shear_term + vort_term)


def boosted_shear(shear: sp.Matrix, fc: FrameChange) -> sp.Matrix:
    r"""$\tilde\sigma_{ab} = \sigma_{ab} + \mathrm D_{\langle a}v_{b\rangle}$.

    Rank two, and it is the one bracket a boost genuinely changes in form.
    Carried symbolically as an opaque first-order addition, because its detailed
    index structure is not what criterion 2 turns on.
    """
    d_v = _sym_traceless("Dv")
    return _first_order(shear + d_v)


# ---------------------------------------------------------------------------
# the rank decomposition, as Annals II writes it
# ---------------------------------------------------------------------------


def bracket_rank0(div_tau: sp.Expr) -> sp.Expr:
    r"""$\mathcal B_0 = -\tfrac13\mathrm D^a\tau_a$."""
    return -sp.Rational(1, 3) * div_tau


def bracket_rank1(grad_ln_T: sp.Matrix, accel: sp.Matrix) -> sp.Matrix:
    r"""$\mathcal B_1 = \mathrm D_a\ln T + A_a$. Rank one, and the subject of S14."""
    return sp.Matrix(grad_ln_T) + sp.Matrix(accel)


def bracket_rank2(shear: sp.Matrix) -> sp.Matrix:
    r"""$\mathcal B_2 = \sigma_{ab}$. Rank two."""
    return sp.Matrix(shear)


# ---------------------------------------------------------------------------
# criterion 2
# ---------------------------------------------------------------------------


def roundtrip_residual() -> sp.Matrix:
    r"""$\tilde{\mathcal B}_1 - (\mathcal B_1 + \dot v_a)$, which must be zero.

    The covariant construction is carried with a **generic** $u^a$, boosted to
    $\tilde u^a=u^a+v^a$, and the rank-one bracket rebuilt from the boosted
    pieces. S14's target is that the result is $\mathcal B_1+\dot v_a$ exactly:
    no shear, no $Hv$.

    Returned as a symbolic residual rather than a float. A round trip whose
    answer is an identity should be shown to *be* an identity --- "zero to
    $10^{-16}$" would be a weaker statement about a stronger fact.
    """
    fc = FrameChange.generic()
    grad_ln_T, accel = _vec("DlnT"), _vec("A")

    before = bracket_rank1(grad_ln_T, accel)
    after = bracket_rank1(
        boosted_temperature_gradient(grad_ln_T, fc),
        boosted_acceleration(accel, fc),
    )
    return sp.simplify(sp.expand(after - (before + fc.v_dot)))
