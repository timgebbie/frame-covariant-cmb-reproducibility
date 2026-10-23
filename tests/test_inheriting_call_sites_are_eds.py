r"""The five scripts that inherit $\Gamma$ and $h$ must be the ones entitled to.

**Finding T-118, turned into a guard.** `build_environment` defaults to
``omega_m=1.0`` --- Einstein--de Sitter, which *is* ``CDM_MODEL`` --- and to
``transfer_gamma=ANNALS_II_GAMMA`` (0.48) and ``hubble_h=0.5``, which are
*Annals II* §8.3.2's standard-CDM values. Those three defaults are **mutually
consistent**: a caller that names no background gets EdS, and 0.48/0.5 are the
right constants for EdS. ``two_frame.py``'s own field comment says so --- *"the
model ``CDM_MODEL`` reconstructs"*.

Coordination's hardening item 6 read the module header, saw two inherited
constants, and concluded that `figure_f5_sources.py`, `figure_f7_frames.py`,
`measure_frame_invariance.py`, `figure_f2_truncation.py` and
`diagnostic_d7_frame_identification.py` *"take the dataclass defaults on every
background they sweep"*, so that the frame gap was *"measured in a published
artefact built on a transfer function belonging to standard CDM"*. **Both
halves were wrong.** The five sweep no background at all, and
``FRAME-INVARIANCE-MEASUREMENT-v1.md`` --- named as the artefact --- has no
PLANCK column and no $\Lambda$CDM column: its table is $k\times\ell$ on one
background. Nothing was changed in response.

**But the worry is one step from true**, and that step is cheap to prevent.
The day one of these scripts gains a PLANCK or $\Lambda$CDM sweep without also
naming $\Gamma$ and $h$, Coordination's sentence becomes correct and the
artefact becomes exactly what they described. That is what this file stops.
It is the general lesson of **T-115** written as a test rather than as a
count: inheriting a default is safe only while the default is right for the
background, and the only way to keep that true is to assert it.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

#: The five Coordination named. They are listed by hand because the point is
#: these five artefacts, not a property of the tree --- a generated list would
#: silently drop one if it were renamed, which is the failure this prevents.
INHERITING = [
    "scripts/figure_f2_truncation.py",
    "scripts/figure_f5_sources.py",
    "scripts/figure_f7_frames.py",
    "scripts/measure_frame_invariance.py",
    "scripts/diagnostic_d7_frame_identification.py",
]

#: Naming any of these is naming a background. ``omega_m`` covers the direct
#: form; the model constants cover the `PLANCK_MODEL.omega_m` form.
BACKGROUND_NAMES = frozenset({
    "omega_m", "omega_lambda", "omega_r",
    "PLANCK_MODEL", "LCDM_MODEL", "PLANCK_H", "PLANCK_OMEGA_B_H2",
})
TRANSFER_NAMES = frozenset({"transfer_gamma", "hubble_h"})


def _build_environment_calls(path: Path) -> list[ast.Call]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and getattr(n.func, "id", getattr(n.func, "attr", None))
            == "build_environment"]


@pytest.mark.parametrize("rel", INHERITING)
def test_a_script_that_inherits_gamma_and_h_names_no_background(rel: str) -> None:
    r"""Inheriting $\Gamma=0.48$ and $h=0.5$ is correct **only** on EdS.

    So a call that names neither must also name no background, and a call that
    names a background must name both. Either is fine; the mixture is the
    defect, and the mixture is what Coordination believed it had found.
    """
    path = ROOT / rel
    assert path.exists(), f"{rel} is gone -- update this list, do not delete it"
    for call in _build_environment_calls(path):
        kw = {k.arg for k in call.keywords if k.arg}
        names_transfer = bool(kw & TRANSFER_NAMES)
        names_background = bool(kw & BACKGROUND_NAMES)
        source = ast.unparse(call)[:160]
        if names_background and not names_transfer:
            pytest.fail(
                f"{rel}:{call.lineno} names a background and inherits Gamma "
                f"and h. 0.48/0.5 belong to Einstein-de Sitter; on any other "
                f"background they are the wrong constants and the figure is "
                f"built on a transfer function that does not belong to it. "
                f"Name transfer_gamma and hubble_h here.\n    {source}")


def test_the_inherited_defaults_are_the_eds_ones() -> None:
    """The premise of the test above, asserted rather than assumed.

    If someone changes `build_environment`'s defaults, inheriting them stops
    being safe and the test above stops meaning what it says.
    """
    import inspect

    from functions.spectra.transfer import ANNALS_II_GAMMA
    from functions.spectra.two_frame import build_environment

    sig = inspect.signature(build_environment)
    assert sig.parameters["omega_m"].default == 1.0, (
        "build_environment no longer defaults to Einstein-de Sitter")
    assert sig.parameters["omega_lambda"].default == 0.0
    assert sig.parameters["omega_r"].default == 0.0
    assert sig.parameters["transfer_gamma"].default == ANNALS_II_GAMMA
    assert float(ANNALS_II_GAMMA) == 0.48, "Annals II SS8.3.2's shape parameter"
    assert sig.parameters["hubble_h"].default == 0.5, (
        "Annals II SS8.3.2's standard-CDM h")
