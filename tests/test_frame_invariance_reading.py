"""**T-205.** The F5 record's readings are chosen by its table.

`provenance/FRAME-INVARIANCE-MEASUREMENT-v1.md` computed every number it
printed and fixed every claim: with the coefficients as built the median
disagreement is of order one at every `k`, and the record said it fell "roughly
like `1/k`", from 1.00e+00 at `k = 1` to 1.00e+00 at `k = 1`; with no ragged
`k` it printed "At k =  it is not". A reading of a table is chosen by the table.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import measure_frame_invariance as record  # noqa: E402

GRID = (1.0, 5.0, 20.0, 60.0, 140.0, 300.0)


def test_a_median_of_order_one_is_not_read_as_falling():
    per_k = {k: (m, 0.9 * m, 1.1 * m) for k, m in zip(GRID, (1.0, 1.84, 1.15, 1.62, 1.01, 1.03))}
    text = "\n".join(record._reading_in_k(per_k, best=1.0))
    assert "Of order one at every `k`" in text and "closer" not in text, text


def test_a_median_falling_like_one_over_k_is_read_so():
    per_k = {k: (1.0 / k, 0.9 / k, 1.1 / k) for k in GRID}
    text = "\n".join(record._reading_in_k(per_k, best=300.0))
    assert "closer as `k` grows" in text and "roughly like `1/k`" in text, text


def test_an_empty_set_is_not_printed_as_a_sentence():
    for flat, ragged in ((list(GRID), []), ([], list(GRID)), ([1.0, 5.0], [20.0])):
        text = "\n".join(record._reading_in_l(flat, ragged))
        assert "k =  " not in text and "()" not in text, text
    assert "under 1.5 at every `k`" in "\n".join(record._reading_in_l(list(GRID), []))
