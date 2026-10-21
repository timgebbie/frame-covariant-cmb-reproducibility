#!/usr/bin/env python3
"""Generate docs/THEORY-AUDIT.md from the instruments under tests/frame/.

    python3 gen_theory_audit.py > ../../docs/THEORY-AUDIT.md

Every number in the output is read from a check's own machine-readable
record, and **every word of prose is read from the instrument it describes**
-- its AUDIT_TITLE and AUDIT_PROSE. This generator holds no copy of either, so
correcting an instrument corrects the audit by construction and a wording
cannot drift from the test it reports. Exits non-zero if any check fails, so a failing suite
cannot produce a document.
"""
import ast, hashlib, json, pathlib, re, subprocess, sys, datetime

HERE = pathlib.Path(__file__).resolve().parent
CHECKS = ['c1_identity.py', 'c2_weight.py', 'c3_byparts.py',
          'c4_rank_slot.py', 'c5_monopole.py', 'c6_thomson.py',
          'c7_kappa_ledger.py', 'c8_rank0_partner.py']

def audit_prose(check):
    """Read AUDIT_TITLE and AUDIT_PROSE from the instrument's SOURCE TEXT.

    By `ast.parse`, which builds the syntax tree without executing anything --
    the instruments run and `sys.exit`, so importing one would execute it.
    Parsing rather than pattern-matching also takes whatever literal form the
    author used: a single string or a parenthesised concatenation.
    **The generator holds no copy of any wording.**

    A check without both literals fails the run rather than being reported
    with stale or absent prose -- which is the defect that put the
    pre-correction c6 wording into a *generated* file and left it there
    through a regeneration (D6).
    """
    tree = ast.parse((HERE / check).read_text(), filename=check)
    found = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in ('AUDIT_TITLE', 'AUDIT_PROSE'):
                try:
                    found[t.id] = ast.literal_eval(node.value)
                except ValueError:
                    print(f'{check}: {t.id} is not a literal', file=sys.stderr)
                    sys.exit(2)
    for name in ('AUDIT_TITLE', 'AUDIT_PROSE'):
        if name not in found:
            print(f'{check} carries no {name}', file=sys.stderr)
            sys.exit(2)
    return found['AUDIT_TITLE'], found['AUDIT_PROSE']



def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]

def run(c):
    r = subprocess.run([sys.executable, '-I', str(HERE/c)], cwd=HERE,
                       capture_output=True, text=True)
    m = re.search(r'^##RESULT## (.*)$', r.stdout, re.M)
    if not m:
        print(f'no machine-readable record from {c}\n{r.stdout}\n{r.stderr}',
              file=sys.stderr)
        sys.exit(2)
    return json.loads(m.group(1)), r.stdout

def fmt(v):
    if isinstance(v, float):
        return f'{v:.2e}' if (v and (abs(v) < 1e-3 or abs(v) >= 1e4)) else f'{v:g}'
    return str(v)

recs, logs, allok = {}, {}, True
for c in CHECKS:
    recs[c], logs[c] = run(c)
    allok &= recs[c]['ok']

import numpy, scipy, sympy
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

o = []
o.append('# Theory audit — frame covariance of the source assembly\n')
o.append('> **Generated, not transcribed. Do not edit by hand.**\n>\n'
         f'> Produced by `tests/frame/gen_theory_audit.py` at {now}. Every number '
         'below is read from the machine-readable record of the instrument '
         'named beside it. To change this document, change the instrument.\n')
o.append(f'**Status: {"ALL CHECKS PASS" if allok else "FAILING"}** — '
         f'{sum(len(r["checks"]) for r in recs.values())} assertions across '
         f'{len(CHECKS)} instruments.\n')
o.append('## What this document does not establish — read first\n')
o.append('Every assertion below is a condition on the functional or on the '
         'matching, verified in isolation against fixtures the instruments '
         'build themselves. **No project code is imported, so none of these '
         'can agree with the solver by construction — and none of them is a '
         'claim about the spectrum.** Attribution of a measured symptom to any '
         'of these conditions belongs to whoever can run the solver.\n')
o.append('Measurements of the solver are recorded in '
         '`provenance/BUNDLE-DEFECTS-v1.md` and are **not** restated here. '
         'A number copied out of that register into this one is a third copy, '
         'and a third copy is how a fabricated quotation enters a brief.\n')
o.append('**Polarity.** A row marked `DEFECT PRESENT` asserts that a defect in '
         'the antecedent is *still there*; it is not a failure of this suite. '
         'If such a row ever reads `DEFECT GONE` the suite fails deliberately, '
         'because this document would otherwise assert a defect that no longer '
         'exists.\n')
o.append('## Results\n')
for c in CHECKS:
    title, body = audit_prose(c)
    r = recs[c]
    o.append(f'### {title}\n')
    o.append(body + '\n')
    o.append(f'| assertion | verdict |\n|---|---|')
    for ch in r['checks']:
        d = f" — {ch['detail']}" if ch['detail'] else ''
        o.append(f"| {ch['name']} | **{ch.get('verdict','PASS')}**{d} |")
    if r['metrics']:
        o.append('\n| measured | value |\n|---|---|')
        for k_, v_ in r['metrics'].items():
            o.append(f'| `{k_}` | {fmt(v_)} |')
    o.append(f'\n*Instrument: `tests/frame/{c}`, sha256 `{sha(HERE/c)}…`*\n')

o.append('## Provenance\n')
o.append(f'| | |\n|---|---|\n| generated | {now} |\n'
         f'| python | {sys.version.split()[0]} |\n| numpy | {numpy.__version__} |\n'
         f'| scipy | {scipy.__version__} |\n| sympy | {sympy.__version__} |\n'
         f'| generator | `tests/frame/gen_theory_audit.py`, sha256 '
         f'`{sha(pathlib.Path(__file__))}…` |\n')
o.append('Annals II is read from `sources/annals/cbrII.tex` and referred to by '
         'label — `IBE-source`, `modeibe`, `source-calB`, `find_coef`, '
         '`C-B-coef`, `int_soln_damping`, `slowdecoupling`, '
         '`slowdecoupling-ng-0`. Paper 1 is referred to by label (`eq:B`, '
         '`eq:frame-transf`, `eq:raise`), never by printed number: those '
         'differ between the two lines.\n')

print('\n'.join(o))
sys.exit(0 if allok else 1)
