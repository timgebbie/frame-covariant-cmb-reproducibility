#!/usr/bin/env python3
"""Why the frame suite will or will not run here.  Standard library only.

    python tests/frame/doctor.py          # the environment you would get
    python -I tests/frame/doctor.py       # the environment run_all.py uses

WHY THIS EXISTS, 2026-10-27.  `_common.py` imports scipy at module level, so
running it to find out whether scipy is importable dies before it can tell
you.  `run_all.py` ran eleven subprocesses that each failed the same way and
printed eleven tracebacks for one cause.  AND THE GENERATOR THEN REFUSED TO
WRITE `docs/THEORY-AUDIT.md` AND LEFT THE FILE AT ZERO BYTES, which read as a
second failure and was the first one again.

The specific case this was written for: `pip install sympy` puts the package
in the per-user site directory, and `python -I` implies `-s`, which ignores
exactly that directory.  `Requirement already satisfied` and
`ModuleNotFoundError` are then both true at once, which is confusing enough to
cost an afternoon.  This file says so in one line.

It imports nothing outside the standard library, so it runs wherever python
runs.
"""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent          # tests/frame
ROOT = HERE.parents[1]                                  # the bundle root
NEEDED = ('numpy', 'scipy', 'sympy')

print('interpreter   ', sys.executable)
print('version       ', sys.version.split()[0])
print('isolated (-I) ', bool(sys.flags.isolated),
      ' | user site ignored (-s):', bool(sys.flags.no_user_site),
      ' | safe path (-P):', bool(getattr(sys.flags, 'safe_path', False)))
print()

missing = []
for name in NEEDED:
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        spec = None
    where = (spec.origin or '(namespace)') if spec else None
    print('  %-8s %s' % (name, where if where else 'NOT IMPORTABLE HERE'))
    if not spec:
        missing.append(name)
print()

# ---------------------------------------------------------------------------
# The independence condition `_common.py` enforces, reported rather than acted
# on, so this file is readable in an environment that one would refuse.
# ---------------------------------------------------------------------------
bad = []
for entry in sys.path:
    if not entry:
        continue
    try:
        p = pathlib.Path(entry).resolve()
    except (OSError, ValueError):
        continue
    if p == HERE or not p.is_dir():
        continue
    if p == ROOT or ROOT in p.parents:
        bad.append(str(p))

print('independence  ', 'OK -- no bundle directory on sys.path' if not bad
      else 'VIOLATED')
for e in bad:
    print('                 bundle directory on sys.path:', e)
print()

# ---------------------------------------------------------------------------
if not missing and not bad:
    print('VERDICT  the suite will run here.  python tests/frame/run_all.py')
    sys.exit(0)

if bad:
    print('VERDICT  the suite will REFUSE to report a result here, because a')
    print('         reachable bundle directory makes a PASS unfalsifiable.')
    print('         Remove that entry from PYTHONPATH and run again.')
    sys.exit(2)

print('VERDICT  missing here:', ', '.join(missing))
if sys.flags.no_user_site:
    print()
    print('         This interpreter is ignoring the per-user site directory,')
    print('         which is where "pip install --user" puts things and where')
    print('         a plain "pip install" puts things on Windows when python')
    print('         is not writable.  So "Requirement already satisfied" and')
    print('         this message can both be true.  Re-run WITHOUT -I to see')
    print('         what a normal invocation finds.')
print()
print('         Two ways out, and the first is preferred:')
print('           1. a virtual environment, which also pins the versions')
print('                python -m venv .venv')
print('                .venv/Scripts/python -m pip install -r requirements.txt')
print('                .venv/Scripts/python tests/frame/run_all.py')
print('           2. install into the interpreter itself, from an elevated')
print('              shell, so that the isolated path finds it.')
print()
print('         Running the suite without -I is ALSO safe as of 2026-10-27:')
print('         _common.py now checks the independence property directly')
print('         rather than relying on the flag, and records it in each')
print('         instrument\'s machine-readable result.')
sys.exit(1)
