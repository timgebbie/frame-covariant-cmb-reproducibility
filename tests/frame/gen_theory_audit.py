#!/usr/bin/env python3
"""Generate docs/THEORY-AUDIT.md from the instruments under tests/frame/.

    python3 gen_theory_audit.py

**No redirection, and the usage line said otherwise until 2026-10-26.** This
script writes `docs/THEORY-AUDIT.md` itself (see the end of the file). A shell
redirect on top of that is not merely redundant, it is destructive: the shell
truncates the target *before* the script runs, so a generator that then
refuses to write -- because an instrument failed, or because `sympy` is not
installed for this interpreter -- leaves the audit at **zero bytes**. That is
what happened on the PI's machine on 2026-10-26, and the release gate reported
it as "0 instruments" against the eleven on disk. Nothing is printed to stdout
any more, so the redirect has nothing left to capture.

Every number in the output is read from a check's own machine-readable
record, and **every word of prose is read from the instrument it describes**
-- its AUDIT_TITLE and AUDIT_PROSE. This generator holds no copy of either, so
correcting an instrument corrects the audit by construction and a wording
cannot drift from the test it reports. Exits non-zero if any check fails, so a failing suite
cannot produce a document.
"""
import ast, hashlib, json, pathlib, re, subprocess, sys, datetime

HERE = pathlib.Path(__file__).resolve().parent
#: **Discovered, not listed --- changed by P1-B 2026-10-26.**
#:
#: This was a literal list, and the note that stood here recorded that it had
#: drifted: `c9` landed and was absent, so `docs/THEORY-AUDIT.md` carried no
#: by-parts admissibility result at all. The conclusion drawn was *"three
#: registries run over this one directory, so adding an instrument means
#: adding it to all three"*.
#:
#: **That is a correct description of the defect and the wrong repair.** A
#: rule that three lists be updated together is kept only by somebody
#: remembering, and the note was itself the evidence that nobody does --- it
#: was written *because* the remembering had already failed once.
#: `tests/test_frame_checks.py` became a glob the same morning for the same
#: reason, and `c10` and `c11` landed hours after the note was written.
#:
#: So the registry is the directory. Sorted numerically rather than lexically
#: so that `c10` follows `c9` and the audit reads in the order the instruments
#: were written.
CHECKS = sorted((p.name for p in HERE.glob('c*.py') if p.name[1:2].isdigit()),
                key=lambda n: int(n[1:].split('_', 1)[0]))
if len(CHECKS) < 8:
    sys.exit(f'only {len(CHECKS)} instruments found under {HERE}: the glob is '
             'measuring nothing and this document would under-report in '
             'silence, which is the failure it was converted to prevent')

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
    return (_render_safe(found['AUDIT_TITLE'], check),
            _render_safe(found['AUDIT_PROSE'], check))


#: Every normalisation this run applied, `(instrument, from, to)`, so the
#: report names the file to fix rather than leaving the author to find it.
NORMALISED = []

#: **Three hazards GitHub's renderer has already caught this bundle with, and
#: they arrive here through somebody else's prose --- added by P1-B
#: 2026-10-26.**
#:
#: The audit is *generated from the instruments' own wording*, which is the
#: property that keeps it from drifting. The cost of that property is that an
#: instrument author can break the rendered document without ever opening it,
#: and on 2026-10-26 three of them did: `c9`--`c11` landed carrying `\,`,
#: `\%` and `\eta_*` inside maths, and `docs/THEORY-AUDIT.md` went red on
#: three render tests the moment it was regenerated.
#:
#: Each is **typographic and not semantic**, so this normalises rather than
#: refusing --- a generator that will not run until another stream fixes its
#: spacing blocks the wrong person. What it must not do is normalise in
#: silence, so every substitution is reported at the end of the run.
#:
#:   `_*`   the emphasis parser eats the asterisk (**T-120**, the first of
#:          the three). `\ast` is the house spelling.
#:   `\,`   markdown eats the backslash before ASCII punctuation, leaving a
#:          bare comma inside the maths.
#:   `\%`   same mechanism; the house rule is to put the percent sign outside
#:          the span. Only the trailing case is mechanical, so a `\%` anywhere
#:          else is refused rather than guessed at.
_MATHS = re.compile(r'\$\$.*?\$\$|(?<!\$)\$(?!\s)[^$\n]{1,400}?(?<!\s)\$(?!\$)',
                    re.S)


def _render_safe(text, check):
    def fix(m):
        span = was = m.group(0)
        span = span.replace('_*', r'_\ast')
        span = span.replace(r'\,', '')
        # `$...98.5\%$` -> `$...98.5$%`: close the span before the sign.
        span = re.sub(r'\\%\$$', '$%', span)
        if r'\%' in span:
            print(f'{check}: `\\%` inside maths and not at the end of the '
                  f'span, which cannot be moved out mechanically: {was[:80]}\n'
                  '  Put the percent sign outside the $...$ in the '
                  'instrument itself.', file=sys.stderr)
            sys.exit(2)
        if span != was:
            NORMALISED.append((check, was[:60], span[:60]))
        return span
    return _MATHS.sub(fix, text)



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

text = '\n'.join(o)

# **The generator WRITES the document.  Added 2026-10-21 by P1-B.**
#
# It used to print to stdout only, so `docs/THEORY-AUDIT.md` existed solely by
# a shell redirection somebody had to remember.  They did not: the committed
# file sat five days and one instrument behind its own instruments, publishing
# a refuted conclusion and a withdrawn prohibition as normative record, under
# a header reading "Generated, not transcribed".  And a well-meant
# `>/dev/null` while checking the exit status DISCARDED the document.
#
# An artefact whose generation depends on a human remembering a redirection is
# not generated.  `run_all.py` runs this, and the write is here.
out = HERE.parents[1] / 'docs' / 'THEORY-AUDIT.md'
if allok:
    out.parent.mkdir(exist_ok=True)
    out.write_text(text + '\n', encoding='utf-8', newline='\n')
    print(f'\nwrote {out.relative_to(HERE.parents[1])}', file=sys.stderr)
    if NORMALISED:
        print(f'\n  {len(NORMALISED)} render normalisation(s) applied to '
              'instrument prose on the way in. These are typographic and the\n'
              '  document is correct; FIX THEM AT SOURCE so the next author '
              'does not inherit them:', file=sys.stderr)
        for c, was, now in NORMALISED:
            print(f'    {c}\n      {was}\n   -> {now}', file=sys.stderr)
else:
    print('\nFAILING SUITE -- document NOT written', file=sys.stderr)
sys.exit(0 if allok else 1)
