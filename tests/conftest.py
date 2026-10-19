"""Test markers: **transcription** against **verification**.

**Coordination's item of 2026-10-18, landed with finding T-66 rather than before
it**, because T-66 moves `test_coefficients.py`, `test_sources.py`,
`test_integral_solution.py` and `test_two_route.py` as well as the
(177)--(179) transcription assertions, and a split drawn against the
pre-T-66 tree would have had to be redrawn immediately.

The distinction is what the assertion is *for*:

``transcription``
    The assertion pins **what Annals II prints**. It passes because the bundle
    reproduces the antecedent, including the antecedent's own approximations
    --- `visibe`'s collapse of the visibility width, (102)'s printed weight,
    (106)'s expansion terms. **These are expected to go red when a source
    defect is corrected**, and a red here is a statement about the
    antecedent, not about the bundle.

``verification``
    The assertion pins a **derived or measured** result: an identity, a limit
    with a known answer, a gate between two independent routes, a control that
    must fail. **A red here is a defect.**

Unmarked tests are treated as ``verification``: the stricter reading, so that
forgetting a marker cannot downgrade a failure.

Run one kind alone with ``-m transcription`` or ``-m "not transcription"``.
"""

from __future__ import annotations


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "transcription: pins what Annals II prints, including its own "
        "approximations; a red here is a statement about the antecedent and "
        "is expected when a source defect is corrected.",
    )
    config.addinivalue_line(
        "markers",
        "verification: pins a derived or measured result -- an identity, a "
        "known-answer limit, a route gate or a control that must fail. A red "
        "here is a defect. This is the default reading for unmarked tests.",
    )
