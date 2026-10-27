r"""The nine weighting configurations, frozen bit-for-bit against a digest.

**Why a digest and not a tolerance.** Every finding in `provenance/` that names
a weighting --- **T-94**, **T-101**, **T-121**, **T-144**, **T-154**,
**T-155** --- is a number produced by one of these nine configurations. If a
refactor of the control surface moved any of them by so much as an ulp, every
one of those rows would silently become a statement about a configuration that
no longer exists, and nothing in the suite would say so. A tolerance would hide
exactly the size of change a refactor produces.

So the gate is equality of bytes.

**What it is for.** It was written the hour before the four mutually-exclusive
booleans `bracket_all_at_w`, `slot_weight_split`, `isw_only_at_w` and
`split_by_parts` were replaced by a single `weighting=` argument, and the
digests below were taken from the tree as it stood *before* that change. They
therefore prove the refactor was a renaming and not a repair --- which is the
claim being made, and is otherwise unfalsifiable.

**What it is not.** It is not a claim that any of these nine is *right*. Six of
them are controls and at most one is the assembly; the file asserts only that
whatever they were, they still are.

**If one of these digests has to change**, it is because the physics changed,
and that is a finding: record it in `provenance/` with the old and the new
value before touching the literal here. A digest edited to make a suite go
green is the end of this file's usefulness.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from functions.spectra.bessel_table import BesselTable  # noqa: E402
from functions.spectra.decoupling import F2_DEFAULT  # noqa: E402
from functions.spectra import integral_solution as _is  # noqa: E402
from functions.spectra.integral_solution import (  # noqa: E402
    integral_solution, required_multipoles)

#: The single `weighting=` argument that is to replace the four
#: mutually-exclusive booleans. **It does not exist yet, and this file is
#: deliberately written to work both before and after it lands.** The freeze
#: below is the whole point and must be live *now* --- a characterisation test
#: that arrives with the refactor it is meant to characterise proves nothing.
WEIGHTINGS = getattr(_is, "WEIGHTINGS", None)
from functions.spectra.two_frame import (  # noqa: E402
    build_environment, bulk_source_primitives, coefficient_sets)

#: $\Lambda$CDM and not Einstein--de Sitter, for T-146's reason: on EdS
#: $\Phi$ is constant, $(\Phi_A'-\Phi_H')\equiv0$, and three of these nine
#: configurations would be frozen against a number that is zero for a reason
#: having nothing to do with the control.
K = 30.0
ELLS = np.array([2, 10, 50, 200])

#: `weighting=` value, plus the sub-options that are legal only inside it.
#: Keyed by the name the findings in `provenance/` use.
#: Spelled in the booleans the tree carries today. When `weighting=` lands,
#: the right change is to respell these and watch every digest below hold ---
#: which is the one piece of evidence that the refactor was a renaming.
MODES: dict[str, dict] = {
    "released": {},
    "bracket_at_w": dict(bracket_all_at_w=True),
    "bracket_at_w_partners": dict(bracket_all_at_w=True,
                                  by_parts_weight_terms=True),
    "slot_split": dict(slot_weight_split=True),
    "slot_split_isw_half": dict(slot_weight_split=True,
                                w_half_is_isw_only=True),
    "slot_split_thomson_shear": dict(slot_weight_split=True,
                                     thomson_carries_shear=True),
    "isw_at_w": dict(isw_only_at_w=True),
    "split_by_parts": dict(split_by_parts=True),
    "split_by_parts_partners": dict(split_by_parts=True,
                                    by_parts_weight_terms=True),
}

#: Which `weighting=` value each spelling above will become.
INTENDED = {
    "released": "released", "bracket_at_w": "bracket_at_w",
    "bracket_at_w_partners": "bracket_at_w", "slot_split": "slot_split",
    "slot_split_isw_half": "slot_split",
    "slot_split_thomson_shear": "slot_split", "isw_at_w": "isw_at_w",
    "split_by_parts": "split_by_parts",
    "split_by_parts_partners": "split_by_parts",
}

#: Taken 2026-10-26 from the boolean control surface, before `weighting=`
#: existed. The comment is the $\ell=2$ transfer, so that a failure can be read
#: without rerunning anything.
FROZEN: dict[str, str] = {
    "released": "ea34e84c444815f9a9252d1aa53b7fb3",                  # +6.076132e+00
    "bracket_at_w": "e088fad44df65594985717120296c5e7",              # -7.121610e+00
    "bracket_at_w_partners": "4ff5d76c0e6391d3e2070c435b746b5c",     # -7.139914e+00
    "slot_split": "a4ad4ad35f5a50c7b1db27837cf4336b",                # -1.222578e+00
    "slot_split_isw_half": "7263b3781d27c196658efc9ec1a56a69",       # -3.780116e-01
    "slot_split_thomson_shear": "26784469f57ef7e15a2a562affa3a1a0",  # -2.051702e+01
    "isw_at_w": "f14f4e08a776bc1c5bb3b7a00896c88e",                  # +6.058460e+00
    "split_by_parts": "8ff81d5f67bea3e632844ed3d20ab671",            # -7.119302e+00
    "split_by_parts_partners": "392088a2fb3112e92d951a7421e007b5",   # -7.137606e+00
}


@pytest.fixture(scope="module")
def fixture():
    from functions.background.flrw import LCDM_MODEL
    env = build_environment(
        60.0, omega_m=LCDM_MODEL.omega_m, omega_lambda=LCDM_MODEL.omega_lambda,
        omega_r=LCDM_MODEL.omega_r, omega_b_h2=0.0224, transfer_gamma=0.48,
        hubble_h=0.5, f_2=F2_DEFAULT, line_of_sight_weight="printed")
    s = coefficient_sets(K, env)[1]
    needed = required_multipoles(ELLS)
    eta_0 = float(env.background.eta_0)
    table = BesselTable.build(
        ell_max=int(needed.max()), ells=needed,
        x_max=float(K * (eta_0 - env.eta[0])) + 20.0)
    diffusion = float(np.exp(-((K / env.damping_k) ** 2)))
    common = dict(table=table, weight=env.weight, diffusion=diffusion,
                  damping_total=diffusion, eta_star=float(env.eta_star),
                  eta_floor=float(env.eta[0]), visibility=env.visibility,
                  eta_0=eta_0)
    common.update(bulk_source_primitives(K, env, s))
    coeffs = dict(coefficients=s.coefficients, c1_prime=s.c1_prime,
                  c2_second=s.c2_second, c2_prime_star=s.c2_prime_star,
                  c2_prime=s.c2_prime)
    return common, coeffs


def _digest(common, coeffs, **flags) -> tuple[str, np.ndarray]:
    res = integral_solution(ELLS, **coeffs, **common, **flags)
    t = (np.asarray(res.integrated, dtype=float)
         + np.asarray(res.boundary_scalar, dtype=float)
         + np.asarray(res.boundary_shear, dtype=float))
    return hashlib.sha256(t.tobytes()).hexdigest()[:32], t


@pytest.mark.parametrize("name", sorted(MODES))
def test_the_configuration_still_produces_the_number_it_did(name, fixture):
    """**The gate.** Byte equality against the pre-refactor tree."""
    common, coeffs = fixture
    got, t = _digest(common, coeffs, **MODES[name])
    assert got == FROZEN[name], (
        f"`{name}` has moved. ell=2 is now {t[0]:+.6e}; the digest frozen "
        f"before the `weighting=` refactor is {FROZEN[name]} and this tree "
        f"produces {got}. Either the refactor changed the physics -- in which "
        "case it is not a renaming and the finding that cites this "
        "configuration has to be revisited -- or something upstream of the "
        "integral moved. Do not edit the literal to make this pass.")


def test_the_nine_are_nine_and_not_fewer(fixture):
    """**Distinctness, which is the pairwise form of the T-125 gate.**

    Nine named configurations that produce eight distinct answers means two of
    them are the same configuration under two names, and every finding that
    distinguishes them is reporting a difference that is not there.
    """
    common, coeffs = fixture
    seen: dict[str, str] = {}
    for name in sorted(MODES):
        d, _ = _digest(common, coeffs, **MODES[name])
        assert d not in seen, (
            f"`{name}` and `{seen[d]}` return bit-identical transfers. They "
            "are one configuration with two names, and any finding that "
            "compares them measured nothing (T-125).")
        seen[d] = name


@pytest.mark.skipif(WEIGHTINGS is None,
                    reason="`weighting=` has not landed yet; the nine digests "
                           "above are frozen against the boolean surface and "
                           "are what the refactor will be checked against")
def test_every_weighting_value_is_exercised_here():
    """A frozen set that does not cover the modes freezes nothing."""
    assert set(INTENDED.values()) == set(WEIGHTINGS), (
        f"`weighting=` accepts {sorted(WEIGHTINGS)} but this file freezes "
        f"{sorted(set(INTENDED.values()))}. A mode added without a digest is "
        "a mode a refactor can move silently.")
