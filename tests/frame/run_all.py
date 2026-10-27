#!/usr/bin/env python3
"""Run every frame check.  Exit 0 only if all pass."""
import subprocess, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
#: **The registry is the directory.** Converted from a hand-maintained list
#: 2026-10-27, after P1-B made `gen_theory_audit.py` and
#: `tests/test_frame_checks.py` globs on the 26th and put the argument to
#: P1-T. The argument is accepted and it is the better repair: the note this
#: replaces concluded that adding an instrument means adding it to all three
#: lists, which is a rule kept only by somebody remembering, and that note was
#: itself the evidence that nobody does --- it was written *because* the
#: remembering had already failed, and `c10` and `c11` landed hours later.
#: Leaving one hand-maintained list of the three would have been the same
#: defect with a smaller surface.
#:
#: Sorted numerically rather than lexically so `c10` follows `c9`.
CHECKS = sorted((p.name for p in HERE.glob('c*.py') if p.name[1:2].isdigit()),
                key=lambda n: int(n[1:].split('_', 1)[0]))
if len(CHECKS) < 8:
    sys.exit(f'only {len(CHECKS)} instruments found under {HERE}: the glob is '
             'measuring nothing and an empty suite would report ALL FRAME '
             'CHECKS PASS, which is the failure it was converted to prevent')

NEEDED = ('numpy', 'scipy', 'sympy')
PROBE = 'import ' + ', '.join(NEEDED)


def reachable(flags):
    """Can a CHILD with these flags import the dependencies?

    Asked of the child and not of this process, because this process is
    normally launched without `-I` while the children are launched with it.
    Checking here would find a user site-packages directory the children are
    about to ignore -- which is the exact confusion of 2026-10-27, where
    `pip` reported `Requirement already satisfied` and every child reported
    `ModuleNotFoundError`, both honestly.
    """
    return subprocess.run([sys.executable, *flags, '-c', PROBE],
                          capture_output=True).returncode == 0


#: **How the flags are chosen, and why dropping `-I` is not a concession.**
#:
#: `-I` was the mechanism by which these instruments imported no project code:
#: it implies `-E`, so PYTHONPATH cannot reach the solver. It is a proxy for
#: the property, and a proxy that also implies `-s`, which ignores the
#: per-user site directory where `pip install` lands on a machine whose
#: interpreter is not writable. On such a machine the proxy makes the suite
#: unrunnable.
#:
#: Since 2026-10-27 `_common.py` checks the PROPERTY directly -- no bundle
#: directory reachable on `sys.path`, nothing from the bundle imported -- and
#: exits 2 before any check runs if it does not hold. Every instrument records
#: `independent` and `isolated_interpreter` in its machine-readable result, so
#: a run made without `-I` is marked in the record and in the generated
#: `docs/THEORY-AUDIT.md`.
#:
#: So: prefer `-I`, keep it wherever it works, and fall back only when the
#: isolated interpreter cannot see the dependencies and the ordinary one can.
#: The fallback is announced, never silent. **The guard is what the
#: independence now rests on; the flag is defence in depth.**
if reachable(['-I']):
    FLAGS, NOTE = ['-I'], None
elif reachable([]):
    FLAGS = []
    NOTE = ('running WITHOUT -I: the isolated interpreter cannot see '
            f'{", ".join(NEEDED)}, the ordinary one can.\n'
            '  Independence is enforced by _common.py and recorded per '
            'instrument. See doctor.py.')
else:
    print('FRAME CHECKS NOT RUN -- ' + ', '.join(NEEDED)
          + ' are not importable, with or without -I.')
    print(f'  interpreter  {sys.executable}')
    print(f'  python {HERE/"doctor.py"}   says why, and what to do about it')
    sys.exit(3)

if NOTE:
    print('NOTE  ' + NOTE)

fails = []
for c in CHECKS:
    print(f'\n===== {c} ' + '='*(60-len(c)))
    r = subprocess.run([sys.executable, *FLAGS, str(HERE/c)], cwd=HERE)
    if r.returncode: fails.append(c)
print('\n' + '='*68)
print('FRAME CHECKS FAILED: ' + ', '.join(fails) if fails
      else 'ALL FRAME CHECKS PASS'
           + ('' if FLAGS else '  (without -I; independence checked directly)'))
sys.exit(1 if fails else 0)
