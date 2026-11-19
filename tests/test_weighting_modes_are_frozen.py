r"""The nine weighting configurations, frozen against their values.

**Why a freeze.** Every finding in `provenance/` that names a weighting ---
**T-94**, **T-101**, **T-121**, **T-144**, **T-154**, **T-155** --- is a
number produced by one of these nine configurations. If a refactor of the
control surface moved any of them, every one of those rows would silently
become a statement about a configuration that no longer exists, and nothing in
the suite would say so.

**Why values at a stated tolerance, and not bytes (T-198).** Until 19 November
the gate was equality of bytes, digested. Bytes are a fact about the platform
as well as the physics: the transfer passes through Radau (rtol $10^{-8}$) and
DOP853 (rtol $10^{-10}$), whose step control turns a last-bit difference in a
platform's mathematics library into a difference at the integrator's
tolerance. On Windows all nine digests failed while $\ell=2$ agreed with the
seven digits printed beside each. So the gate is the four values per
configuration, relative to the largest of them, at `RTOL` $=10^{-7}$: ten times
the loosest integrator tolerance in the chain, and 44 times below the smallest
move a change of physics has made here ($4.4\times10^{-6}$, T-180). A refactor
that is a renaming moves nothing at that level; a change of physics moves more.

**What it is for.** It was written the hour before the four mutually-exclusive
booleans `bracket_all_at_w`, `slot_weight_split`, `isw_only_at_w` and
`split_by_parts` were replaced by a single `weighting=` argument, and the
digests below were taken from the tree as it stood *before* that change. They
therefore prove the refactor was a renaming and not a repair --- which is the
claim being made, and is otherwise unfalsifiable.

**What it is not.** It is not a claim that any of these nine is *right*. Six of
them are controls and at most one is the assembly; the file asserts only that
whatever they were, they still are.

**If one of these values has to change**, it is because the physics changed,
and that is a finding: record it in `provenance/` with the old and the new
value before touching the literal here. A value edited to make a suite go
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

#: **The transfer at `ELLS`, to 17 digits** (T-198), taken on Linux at
#: `3bb4490`, where all nine T-180 digests still held. $\ell=200$ is
#: $10^{-43}$, far below $j_\ell$'s turn-on at this $k$, which is why the
#: comparison is relative to each configuration's largest value.
RTOL = 1e-7
FROZEN: dict[str, tuple[float, float, float, float]] = {
    "released": (6.0818393806066879e+00, 5.0118307169475651e+00, 2.9666064952878979e+00, -4.8951906225847324e-43),
    "bracket_at_w": (-7.1217279562188978e+00, -3.4788472296617408e+00, -1.0346847052274033e+00, -1.8179520471898235e-45),
    "bracket_at_w_partners": (-7.1401362284356304e+00, -3.4972587597214728e+00, -1.0488419756390914e+00, -9.9417497627425927e-46),
    "slot_split": (-1.2173229460314272e+00, 1.3785550909151059e+00, 1.8313577558321525e+00, -4.7819262137616551e-43),
    "slot_split_isw_half": (-3.7096294577557415e-01, 1.8250576292581335e+00, 2.0474902748434984e+00, -4.8276522806494253e-43),
    "slot_split_thomson_shear": (-2.0527664484815205e+01, -1.4479843752350556e+01, -7.4992197519120865e+00, 1.0875743644503329e-42),
    "isw_at_w": (6.0658221124482958e+00, 5.0065055578188558e+00, 2.9664784528490413e+00, -4.8951906223554387e-43),
    "split_by_parts": (-7.1193332644146663e+00, -3.4762439535225127e+00, -1.0325644306986768e+00, -1.7870335963940883e-45),
    "split_by_parts_partners": (-7.1377415366313972e+00, -3.4946554835822439e+00, -1.0467217011103651e+00, -9.6325652547852379e-46),
}

#: **The digests this file froze until T-198**, kept as the record they are:
#: taken 2026-10-26 from the boolean control surface, before `weighting=`
#: existed, and re-frozen at T-180. The comment is the $\ell=2$ transfer.
#: Nothing reads them; `FROZEN` above reproduces every one on Linux.
DIGESTS_T180: dict[str, str] = {
    # **RE-FROZEN 2026-10-30, T-180.** The nine digests below replace the nine
    # taken before the `weighting=` refactor. The reason is authorised and
    # measured rather than convenient: `RecombinationHistory.build`'s `n_eta`
    # went 4000 -> 8000 under P1-T's ruling on `P1B->P1T #18`, because `c12`'s
    # bound wants 21.5 samples across the visibility FWHM and 4000 gave 10.0.
    # Every number in the bundle moves with it, which is what this file exists
    # to notice, and it noticed.
    #
    # The pre-change digest and the pre-change $\ell=2$ value are kept on each
    # row. A re-freeze that discards what it replaced is indistinguishable
    # from editing a literal to make a test pass, which the message below
    # forbids -- and the forbidding is right. What makes this legitimate is
    # that the move was predicted, granted, and is recorded with its size.
    #
    # **And the sizes say something the ruling did not.** The two weightings
    # T-163 left standing move by 4.4e-06 and 1.7e-05; the three it struck
    # move by 9.4e-04 to 1.4e-02 -- two to three orders more. The survivors
    # are the configurations least sensitive to the recombination grid, which
    # is an independent corroboration of T-163 from a direction that run did
    # not test.
    "released": "587fc42d8a94d0837456784f17da9df6",                  # +6.081839e+00  was ea34e84c444815f9a9252d1aa53b7fb3 / +6.076132e+00  (9.4e-04)
    "bracket_at_w": "7540b291403bd4bdbe27df560446b803",              # -7.121728e+00  was e088fad44df65594985717120296c5e7 / -7.121610e+00  (1.7e-05)
    "bracket_at_w_partners": "04590723d293bbcf1c5f6ca58e9ecc5f",     # -7.140136e+00  was 4ff5d76c0e6391d3e2070c435b746b5c / -7.139914e+00  (3.1e-05)
    "slot_split": "f387f1e5416c12d17790a558ae17e089",                # -1.217323e+00  was a4ad4ad35f5a50c7b1db27837cf4336b / -1.222578e+00  (4.3e-03)
    # T-190: these two read `c1_prime_isw`, which now carries T(k).
    "slot_split_isw_half": "df82ed11e9f095c7ded44eeb0f03050a",       # -3.709629e-01  was f56a722003f23572021698860a222725 / -3.726177e-01  (4.4e-03, T-190)
    "slot_split_thomson_shear": "b934cfee2f39018f0cafbf14cbd3dba1",  # -2.052766e+01  was 26784469f57ef7e15a2a562affa3a1a0 / -2.051702e+01  (5.2e-04)
    "isw_at_w": "198887fc0cdff87f45e96b9c8d995be2",                  # +6.065822e+00  was 399820fed5b2f70700495ffb024399ba / +6.064167e+00  (2.7e-04, T-190)
    "split_by_parts": "2823c1a62cd334048c7de6e8cdec9cf3",            # -7.119333e+00  was 8ff81d5f67bea3e632844ed3d20ab671 / -7.119302e+00  (4.4e-06)
    "split_by_parts_partners": "71cfc34cdf4b7ec34d239deb50d04ba6",   # -7.137742e+00  was 392088a2fb3112e92d951a7421e007b5 / -7.137606e+00  (1.9e-05)
}


@pytest.fixture(scope="module")
def fixture():
    from functions.background.flrw import LCDM_MODEL
    env = build_environment(
        60.0, omega_m=LCDM_MODEL.omega_m, omega_lambda=LCDM_MODEL.omega_lambda,
        omega_r=LCDM_MODEL.omega_r, omega_b_h2=0.0224, transfer_gamma=0.48,
        hubble_h=0.5, f_2=F2_DEFAULT, line_of_sight_weight="printed")
    s = coefficient_sets(K, env, source="as built")[1]
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
    """**The gate.** The four values, relative to the largest, within `RTOL`."""
    common, coeffs = fixture
    _, t = _digest(common, coeffs, **MODES[name])
    frozen = np.asarray(FROZEN[name])
    moved = float(np.max(np.abs(t - frozen)) / np.max(np.abs(frozen)))
    assert moved < RTOL, (
        f"`{name}` has moved by {moved:.1e} of its largest value, against "
        f"{RTOL:.0e}. ell=2 is now {t[0]:+.10e} and was frozen at "
        f"{frozen[0]:+.10e}. Either the refactor changed the physics -- in "
        "which case it is not a renaming and the finding that cites this "
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
