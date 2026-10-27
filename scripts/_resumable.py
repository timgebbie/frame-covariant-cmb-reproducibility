"""Row-at-a-time checkpointing for diagnostics that outlive their container.

**Finding T-127, and it is a reliability defect rather than a physics one.**
Four long runs were lost part-way to container restarts — D24 twice, D29
twice — each about forty minutes, each relaunched from zero into an ephemeral
scratch file. The results that *did* land were read out of partial logs.

That is a defect in the thing P1-B owns. **A diagnostic whose result exists
only while its process does is not reproducible**, and the bundle's whole
claim is reproducibility. The repair is not a better log location; it is that
a completed row is written down the moment it completes, and a rerun does not
recompute it.

Deliberately a CSV and not a pickle: a reader can open it, a diff shows what
moved, and `make_manifests` can hash it. Deliberately keyed on the
configuration rather than on a row index, so inserting a configuration does
not silently reuse another one's answer — which is the failure mode a cache
invites and the reason most caches should not exist.

Usage, and it is three lines in the caller::

    rows = Checkpoint(ROOT / "diagnostics" / "d29-the-identity.csv",
                      ("configuration", "frame", "l_peak", "ratio"))
    for label, cfg in CONFIGS:
        if rows.has(label):           # already computed, in a previous life
            continue
        ...
        rows.add(label, frame=f, l_peak=pos, ratio=pos / ELL_A)

`rows.all()` returns everything, this run's and the previous ones', so the
final table is complete whichever process computed which part of it.
"""
from __future__ import annotations

import csv
import datetime
import os
import pathlib
import sys


class Checkpoint:
    """A CSV that a diagnostic appends to as each configuration completes."""

    def __init__(self, path: pathlib.Path, fields: tuple[str, ...]) -> None:
        self.path = pathlib.Path(path)
        self.fields = ("configuration",) + tuple(
            f for f in fields if f != "configuration") + ("utc",)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._rows: list[dict[str, str]] = []
        if self.path.exists():
            with self.path.open(newline="", encoding="utf-8") as fh:
                self._rows = list(csv.DictReader(fh))
            done = len({r["configuration"] for r in self._rows})
            print(f"  [resume] {self.path.name}: {len(self._rows)} row(s) "
                  f"from {done} configuration(s) already computed; "
                  f"those are skipped", file=sys.stderr, flush=True)
        else:
            with self.path.open("w", newline="", encoding="utf-8") as fh:
                csv.DictWriter(fh, self.fields).writeheader()

    def has(self, configuration: str, *, expect: int | None = None) -> bool:
        """True when this configuration completed in this or a previous run.

        **`expect` exists because `any()` is not completion --- 2026-10-27.**
        A caller writes one row per metric, so a run killed between the first
        row and the last leaves a *partial* configuration on disk. `any()`
        then reports it done, the resume skips it, and the gap is permanent:
        the instrument will never recompute it because it believes it already
        has.

        That is not hypothetical. D36 died on an `fsync` partway through
        `bracket_at_w || PLANCK`, leaving three of its six metrics; the
        resumed run skipped it and the summary table carried `nan` in the one
        cell on the background that matters most. It was noticed only by
        reading the table, which is the weakest check there is.

        Callers that write a known number of rows pass it, and a short
        configuration is then recomputed rather than trusted. Callers that do
        not pass it keep the old behaviour, so this cannot break an instrument
        that has not been taught the count.
        """
        n = sum(1 for r in self._rows if r["configuration"] == configuration)
        if n == 0:
            return False
        if expect is not None and n < expect:
            print(f"  [partial] {configuration}: {n} of {expect} rows on disk "
                  "— recomputing rather than resuming an incomplete row",
                  flush=True)
            return False
        return True

    def add(self, configuration: str, **values) -> None:
        """Append one completed row and **flush it to disk immediately**.

        The flush and the `fsync` are the point of the class. A buffered write
        is exactly as lost as no write when the container goes.
        """
        row = {"configuration": configuration,
               "utc": datetime.datetime.now(datetime.timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ")}
        row.update({k: str(v) for k, v in values.items()})
        self._rows.append(row)
        with self.path.open("a", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, self.fields).writerow(
                {k: row.get(k, "") for k in self.fields})
            fh.flush()
            # **Best-effort, and it must be --- 2026-10-26.** `os.fsync` raised
            # `OSError: [Errno 9] Bad file descriptor` partway through D36 on
            # the PI's Windows machine and **took the run down with it**, five
            # configurations into fifteen. The flush above is what makes the
            # row survive a crash of this process; the fsync only adds survival
            # of a power cut, and **a durability guarantee that can abort a
            # four-hour run costs more than it buys.** The checkpoint's whole
            # purpose is that no run is lost, so the line that enforces
            # durability must not be the line that loses one.
            try:
                os.fsync(fh.fileno())
            except OSError:
                pass

    def all(self) -> list[dict[str, str]]:
        """Every row, this run's and every earlier one's, in order written."""
        return list(self._rows)

    def table(self, *columns: str) -> str:
        """The accumulated rows as a plain text table, for the final report."""
        cols = columns or tuple(c for c in self.fields if c != "utc")
        width = {c: max(len(c), *(len(r.get(c, "")) for r in self._rows))
                 if self._rows else len(c) for c in cols}
        out = ["  " + "  ".join(c.ljust(width[c]) for c in cols),
               "  " + "  ".join("-" * width[c] for c in cols)]
        for r in self._rows:
            out.append("  " + "  ".join(
                r.get(c, "").ljust(width[c]) for c in cols))
        return "\n".join(out)
