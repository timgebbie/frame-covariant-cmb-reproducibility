#!/usr/bin/env python3
"""Conformity gate for the supplement's voice and the README's maths spans.
Standard library only.

It gates three things, each of which has already cost this bundle something:

  D  no maths span in the README files is butted against a letter, a digit or
     a dash -- GitHub's renderer reads the pair as one token
  E  the D check's own regex cannot straddle two spans -- the control, which is
     T-44's requirement and the defect that produced a false 91 on 2026-10-28
  F  the supplement's own voice, on the sections listed below

NO PROJECT CODE IS IMPORTED.  Nothing here is a physics claim and this file is
not a frame instrument: `run_all.py` globs `c<digit>*.py` and will not collect
it, which is deliberate -- the instrument count is a count of physics.

    python tests/frame/conformity.py            # gate; exit 1 on any failure
"""
import re
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

README = ROOT / 'README.md'

FAILED = []
PASSED = []


def report(name, ok, detail=''):
    (PASSED if ok else FAILED).append(name)
    print('  %-4s %s' % ('ok' if ok else 'FAIL', name))
    if detail:
        for line in detail.splitlines():
            print('       %s' % line)
    return ok


# ---------------------------------------------------------------------------
# Markdown stripping.  A maths span quoted inside backticks is an EXAMPLE, not
# an instance -- both handoff files quote the bad pattern on purpose -- and a
# fenced block is code.  Checking either would make the gate unusable, which is
# how a gate gets switched off.
# ---------------------------------------------------------------------------
def strip_code(text):
    """Blank fenced blocks and inline code, preserving line structure."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
            out.append('')
            continue
        out.append('' if fenced else re.sub(r'`[^`]*`', lambda m: ' ' * len(m.group(0)), line))
    return '\n'.join(out)


DASHES = '\u2013\u2014'          # en dash, em dash


def blank_display_math(text):
    """Blank ``$$...$$`` blocks.  Display maths is block-level: nothing is
    adjacent to it in the sense the rule is about, and its delimiters would
    otherwise corrupt the open/close alternation for everything after it."""
    return re.sub(r'\$\$.*?\$\$', lambda m: ' ' * len(m.group(0)), text, flags=re.S)


def inline_spans(text):
    """Index pairs of the inline maths spans across the WHOLE document.

    THIS IS THE WHOLE POINT OF THE FILE.  A regex of the form ``\\$[^$]+\\$``
    has no way to know which delimiter opened the span it is looking at, so it
    pairs the CLOSE of one span with the OPEN of the next and matches the
    ordinary prose between them.  That produced 91 false positives on the root
    README on 2026-10-28 and nearly became a reported finding.  Delimiters
    alternate, so the spans are (p0,p1), (p2,p3), ... and nothing else is one.

    Pairing runs over the whole text rather than line by line because a span
    may legitimately wrap a line, and a per-line parse reports every wrapped
    span as unbalanced -- a false alarm that is how a gate gets switched off.
    """
    pos = [m.start() for m in re.finditer(r'(?<!\\)\$', text)]
    return list(zip(pos[0::2], pos[1::2])), len(pos) % 2


def rendering_violations(text):
    """P1-B's narrowed rule, gated at b682800, applied without straddling.

    A letter or digit immediately after the closing delimiter, or an en/em dash
    touching either delimiter.  NOT every adjacency: a hyphen after a span is
    everywhere in this bundle's prose and was never among the evidence.
    """
    clean = blank_display_math(strip_code(text))
    starts = [0] + [m.end() for m in re.finditer(r'\n', clean)]

    def lineno(off):
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= off:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    spans, odd = inline_spans(clean)
    bad = []
    if odd:
        bad.append((lineno(len(clean) - 1),
                    'the document carries an odd number of maths delimiters, so '
                    'at least one span never closes', ''))
    for a, b in spans:
        after = clean[b + 1] if b + 1 < len(clean) else ''
        before = clean[a - 1] if a > 0 else ''
        ctx = clean[max(0, a - 12):b + 14].replace('\n', ' ')
        if after and (after.isalnum() or after in DASHES):
            bad.append((lineno(b), 'closing delimiter butted against %r' % after, ctx))
        elif before and before in DASHES:
            bad.append((lineno(a), 'opening delimiter butted against %r' % before, ctx))
    return bad




# ---------------------------------------------------------------------------
# D  the rendering rule, on the files P1-T writes
# ---------------------------------------------------------------------------
def check_rendering():
    targets = [HERE / 'README.md', README]
    bad = []
    for p in targets:
        if not p.exists():
            continue
        for n, why, ctx in rendering_violations(p.read_text(encoding='utf-8')):
            bad.append('%s:%d  %s  ... %s ...' % (p.relative_to(ROOT), n, why, ctx.strip()))
    return report('D  no maths span butted against a letter, digit or dash',
                  not bad, '\n'.join(bad[:20]) +
                  ('\n... and %d more' % (len(bad) - 20) if len(bad) > 20 else ''))


# ---------------------------------------------------------------------------
# E  THE CONTROL.  Without it this file is decoration: an instrument that
#    cannot fail on a case it should catch has not been tested, and the naive
#    regex is the specific error that produced a false 91 on 2026-10-28.
# ---------------------------------------------------------------------------
NAIVE = re.compile(r'\$[^$\n]+\$[A-Za-z0-9]')
PROBE_STRADDLE = r'The $\ell$ column reproduces the released spectrum to $1$ part.'
PROBE_REAL     = r'A run on $\Lambda$CDM.'
PROBE_HYPHEN   = r'An $\ell$-dependent coefficient.'


def check_control():
    problems = []
    if not NAIVE.search(PROBE_STRADDLE):
        problems.append('the naive regex no longer straddles, so this control '
                        'tests nothing and must be re-pointed')
    if rendering_violations(PROBE_STRADDLE):
        problems.append('the span-paired check reports the straddling probe, '
                        'which is the false positive it exists to avoid')
    if not rendering_violations(PROBE_REAL):
        problems.append('the span-paired check misses a real violation, so it '
                        'would pass a file carrying the class')
    if rendering_violations(PROBE_HYPHEN):
        problems.append('a hyphen after a span is flagged; that is the widening '
                        'P1-B refused on evidence and must stay refused')
    return report('E  control: the naive regex straddles and this one does not',
                  not problems, '\n'.join(problems))


# ---------------------------------------------------------------------------
# F  THE SUPPLEMENT'S VOICE, which is the failure mode that keeps coming back.
#
# `claude/style-supplementary-materials-voice.md` is thorough, has mechanical
# tests, and ends by naming its own cause: "The count that predicts the drift
# is the one nobody was running."  The rule was never missing.  The running
# was.  So the counts run here, and they run on the section being edited.
#
# SCOPE IS THE WHOLE POINT.  Section 5 of that document: "correct mine, not
# his."  The released prose uses some of the same words and is not in scope --
# the RC's own `Current situation` carries 18 bold spans in prose and is
# correct.  Only sections P1-T wrote are gated, and a section nobody has
# classified is reported rather than guessed at.
# ---------------------------------------------------------------------------
SUPPLEMENT = sorted(ROOT.glob('SUPPLEMENTARY-MATERIAL-v*.tex'))

#: Sections P1-T wrote.  Adding a section here is what puts it under the gate.
P1T_SECTIONS = ('Discussion', 'Implications')

BANNED = ('worth naming', 'worth saying', 'worth stating', 'and that is the point',
          'not a hypothetical', 'There is one', 'and it is the one')

#: Titles already landed and not yet repaired.  Each needs a reason, and the
#: list is meant to shrink.  An empty entry is not allowed.
TITLE_DEBT = {
    # empty, and it is meant to stay empty: a title is repaired, not recorded.
}


def title_failures(title):
    """The three patterns of style section 6, and only those.

    Pattern 1 is NOT "opens with an interrogative".  It is "opens with an
    interrogative THAT THE TITLE THEN ANSWERS" -- a label with no assertion in
    it.  A cleft names its subject at once and is correct: the document's own
    exemplar of a GOOD title is "What cancels is the deflection response, and
    variance conservation is not established."  A first reading of the rule
    condemned that sentence, which would have enforced the opposite of the
    rule, so the exemplars below are the control.
    """
    bad = []
    if re.match(r'(What|Why|Where|How)\b', title) and \
       not re.search(r'\b(is|are|was|were)\b', title):
        bad.append('interrogative label with no assertion in it')
    if re.search(r',\s*(which is|and it is)\b', title):
        bad.append('"which is" / "and it is" supplying a withheld subject')
    if re.match(r'(The scope of|The nature of|A note on|The question of|On the)\b', title):
        bad.append('names a category instead of making a claim')
    return bad


#: Every verdict the style document states, as the control for the test above.
TITLE_EXEMPLARS = (
    ('What this establishes, and what it does not.', False),
    ('What cancels is the deflection response, and variance conservation is not established.', True),
    ('The scope of this statement, which is the kernels and not any solver.', False),
    ('This is a statement about the kernels and not about any solver.', True),
    ('Criterion 5b compares against CAMB and CLASS. It does not port them.', True),
    ('A note on the damping coefficient.', False),
    ('Why the peak moves.', False),
)

_TABLE = re.compile(r'\\begin\{(tabularx|longtable|tabular)\}.*?\\end\{\1\}', re.S)
_PARA  = re.compile(r'\\paragraph\{((?:[^{}]|\{[^{}]*\})*)\}')


def _regions(text):
    """Each P1-T section's body, by \\section title."""
    heads = [(m.start(), m.group(1)) for m in re.finditer(r'\\section\{([^}]*)\}', text)]
    out = {}
    for i, (pos, title) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        if title in P1T_SECTIONS:
            out[title] = text[pos:end]
    return out


def check_voice():
    if not SUPPLEMENT:
        return report('F  the supplement keeps its own voice', True,
                      'no SUPPLEMENTARY-MATERIAL-v*.tex in the tree; nothing to gate')
    tex = SUPPLEMENT[-1]
    text = tex.read_text(encoding='utf-8')
    regions = _regions(text)

    bad = []
    missing = [s for s in P1T_SECTIONS if s not in regions]
    if missing:
        bad.append('declared P1-T section(s) not found in %s: %s'
                   % (tex.name, ', '.join(missing)))

    for name, body in sorted(regions.items()):
        prose = _TABLE.sub('', body)
        n_bold = prose.count('\\textbf{')
        if n_bold:
            bad.append('%s: %d bold span(s) in prose, and the baseline is 0 -- '
                       'inline bold as a heading substitute is the named failure mode'
                       % (name, n_bold))
        for b in BANNED:
            if b in body:
                bad.append('%s: banned construction %r' % (name, b))
        grammars = {m.group(1) for m in re.finditer(r'\\begin\{(tabularx|longtable)\}', body)}
        if len(grammars) > 1:
            bad.append('%s: %d table grammars in one section (%s); one per section'
                       % (name, len(grammars), ', '.join(sorted(grammars))))
        for m in _PARA.finditer(body):
            title = re.sub(r'\s+', ' ', m.group(1)).strip()
            why = title_failures(title)
            if not why:
                continue
            if title in TITLE_DEBT:
                print('       debt  %s: %s  [%s]' % (name, title[:56], TITLE_DEBT[title]))
                continue
            bad.append('%s: paragraph title -- %s\n         %s' % (name, '; '.join(why), title))

    # the control: the test must reproduce every verdict the style document states
    wrong = [tl for tl, good in TITLE_EXEMPLARS if bool(title_failures(tl)) == good]
    if wrong:
        bad.append('CONTROL FAILED -- the title test no longer reproduces the style '
                   'document\'s own verdicts on %d exemplar(s). It is measuring '
                   'something else and must not be trusted:\n         %s'
                   % (len(wrong), '\n         '.join(t[:76] for t in wrong)))

    return report('F  the supplement keeps its own voice', not bad, '\n'.join(bad))


def main():
    print('Conformity gate -- %s' % ROOT)
    print()
    check_rendering()
    check_control()
    check_voice()
    print()
    print('  %d passed, %d failed' % (len(PASSED), len(FAILED)))
    return 1 if FAILED else 0


if __name__ == '__main__':
    sys.exit(main())
