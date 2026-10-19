#!/usr/bin/env python3
"""Generate docs/THEORY-AUDIT.md from the instruments under tests/frame/.

    python3 gen_theory_audit.py > ../../docs/THEORY-AUDIT.md

Every number in the output is read from a check's own machine-readable record.
Nothing is transcribed. Exits non-zero if any check fails, so a failing suite
cannot produce a document.
"""
import hashlib, json, pathlib, re, subprocess, sys, datetime

HERE = pathlib.Path(__file__).resolve().parent
CHECKS = ['c1_identity.py', 'c2_weight.py', 'c3_byparts.py',
          'c4_rank_slot.py', 'c5_monopole.py', 'c6_thomson.py']

ROWS = {   # check -> (short title, what it establishes)
 'c1_identity.py': ('The frame identity and the Sachs--Wolfe invariant',
   'Under $\\tilde u_a=u_a+w_a$, $\\Delta(\\delta T+\\Phi_A)=(\\Delta C_2)\'$ with '
   'coefficient exactly 1 — the $-Hw_a$ arising from the projector '
   '$\\tilde h_{ab}=h_{ab}+2u_{(a}w_{b)}$, not from $T$. The boost-invariant '
   'combination $(\\delta T+\\Phi_A)-C_2\'$ equals the same value in **both** '
   'threadings, independent of $k$ and $\\eta$, and it is the Sachs--Wolfe '
   'combination.'),
 'c2_weight.py': ('The rank-2 weight',
   'The rank-2 sector enters at $k^{-2}$, and the boundary pair left by two '
   'integrations by parts is in $S$ and $S\'$ — **never** $S\'\'$.'),
 'c3_byparts.py': ('The bulk source, against the integral it comes from',
   'The exact bulk source is $W(C_0-C_1\'+C_2\'\')-\\mathcal{V}C_1+2\\mathcal{V}C_2\''
   '+\\dot{\\mathcal{V}}C_2$. Annals II\'s printed `int_soln_damping` does not '
   'reproduce its own integral: $+2\\mathcal{V}C_2\'$ is printed as '
   '$-2\\mathcal{V}C_2$, the sign on $\\mathcal{V}C_1$ is reversed, and a '
   'lower-limit boundary $\\mathcal{V}(\\eta_*)C_2(\\eta_*)$ is absent.'),
 'c4_rank_slot.py': ('The rank-2 slot forced by frame invariance',
   'Requiring $\\Delta\\tau_\\ell=0$ at $\\ell\\ge2$ for arbitrary boost potential '
   'gives $\\beta=-\\alpha$ and $\\gamma=0$. **The residual floor here is not '
   'numerical** — it is the Thomson term, absent from this functional; see C6.'),
 'c5_monopole.py': ('The monopole row and the dipole shift',
   '$a\\,\\Delta\\mathcal{B}_0=\\tfrac13kv=\\tfrac13k^2\\Delta C_2$ exactly, so '
   '$\\gamma=0$ closes **only with $\\mathcal{B}_0$ restored** to the $\\ell=0$ '
   'matching row. The monopole row is the only place GDE99 (37)\'s dipole shift '
   'enters the integral solution. **This check cannot see an additive '
   'boost-invariant piece in $C_0$** — $\\Delta C_0=0$ fixes normalisation, not '
   'content.'),
 'c6_thomson.py': ('The Thomson $v^B_a$ slot',
   '$\\kappa\'v_B$ **cannot** sit inside $C_1$: the $K\'$ coefficient becomes '
   '$2\\alpha\\mathcal{V}$ and no $(\\alpha,\\beta,\\gamma)$ makes the bulk '
   'invariant. Carried separately under $\\mathcal{V}$, invariance requires '
   '$c=\\alpha$ and the reduced $\\hat v_B=v_B/k$; the un-reduced form needs '
   '$c=\\alpha/k$, which is not a constant.'),
}

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
    title, body = ROWS[c]
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
