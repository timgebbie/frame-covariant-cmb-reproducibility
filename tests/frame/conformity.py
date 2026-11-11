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
# was.  So the counts run here.
#
# THE RULE IS THE PI'S OF 4 NOVEMBER, AND IT IS ONE RULE AT EVERY LEVEL.
# With the author's style profile v2.0 the PI decided that headings at every
# level, `\paragraph` included, are short and object-centred, and that a claim
# a heading carried moves into the paragraph's first sentence.  That replaces
# the rule of 26-27 October this check first encoded, under which a
# `\paragraph` title read as a sentence and ended in a full stop, so three of
# the verdicts that rule's exemplars asserted are reversed below and say so.
#
# SCOPE IS EVERY SECTION.  The first version gated only `Discussion` and
# `Implications`, because the voice document said "correct mine, not his".
# The sequential style audit the PI asked for on 4 November and again on
# 10 November ("some of the later sections seem to have reverted") brought
# every section to the profile, v1.3.x Part I first and v1.4.2-v1.4.5 the
# rest, so the gate now covers every section and a section it does not gate
# is named in EXCLUDED_SECTIONS with its reason and printed on every run.
#
# WHAT IT CANNOT SEE.  A heading is judged by its words, not its meaning: a
# claim made without a finite verb from the list passes, and a noun spelt like
# a verb fails.  The exemplars below are the control on both directions, and
# `The hold and the peaks.` is in them because a first version of the list
# condemned it.  A green F is the absence of the named failure modes, not a
# verdict on the voice.
# ---------------------------------------------------------------------------
def _version(path):
    """`SUPPLEMENTARY-MATERIAL-v1.4.10.tex` sorts after `v1.4.9`."""
    m = re.search(r'-v(\d+)\.(\d+)\.(\d+)\.tex$', path.name)
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


SUPPLEMENT = sorted(ROOT.glob('SUPPLEMENTARY-MATERIAL-v*.tex'), key=_version)

#: Sections the gate does not read, each with its reason.  Meant to shrink.
EXCLUDED_SECTIONS = {
    'Evidence': 'the figure captions, generated from captions/*.md; their '
                'voice is repaired in the caption files and the block '
                'regenerated, not in the pasted copy',
}

BANNED = ('worth naming', 'worth saying', 'worth stating', 'worth drawing',
          'and that is the point', 'not a hypothetical', 'There is one',
          'and it is the one', 'closes the loop', 'operationally relevant',
          'natural framework', 'provides a way to', 'deliberately modest',
          'quite specific')

#: Titles already landed and not yet repaired.  Each needs a reason, and the
#: list is meant to shrink.  An empty entry is not allowed.
TITLE_DEBT = {
    # empty, and it is meant to stay empty: a title is repaired, not recorded.
}

#: Finite verbs that turn a heading into a claim: the auxiliaries, copulas and
#: modals, and the third-person forms of the verbs the audit found in failing
#: headings.  Base forms that are also nouns (hold, count, return, fix) are
#: left out on purpose, and so is `bounds`, which a first version condemned in
#: `The almost-EGS bounds`; the exemplars carry the control.
FINITE = frozenset('''is are was were be been has have had does do did can
cannot could must should would will may might shall gives holds fails carries
shows says moves needs makes stands closes sits lands returns reads puts takes
keeps leaves enters differs depends agrees survives requires follows remains
becomes fixes lives supplies decides answers replaces explains counts compares
cancels removes suffices performs freezes'''.split())

#: More words than this and a heading is summarising rather than naming.
TITLE_MAX_WORDS = 8


def _words(text):
    t = re.sub(r'\$[^$]*\$|\\\(.*?\\\)', ' X ', text)
    t = re.sub(r'\\(?:eqref|ref|S|texttt|emph|textit|textbf)\{[^{}]*\}', ' X ', t)
    t = re.sub(r'\\[a-zA-Z]+\*?', ' ', t)
    t = re.sub(r'[{}~]', ' ', t)
    return [w for w in re.split(r'\s+', t.strip()) if w]


def title_failures(title):
    """The 4 November rule, at every heading level: short and object-centred.

    A heading fails if it runs past TITLE_MAX_WORDS, carries a finite verb,
    opens with an interrogative, joins a second clause, or names a category
    in place of its object.  The last three are the patterns of the voice
    document's section 6, which the 4 November rule keeps.
    """
    ws = _words(title)
    bad = []
    if len(ws) > TITLE_MAX_WORDS:
        bad.append('%d words; a heading names its object' % len(ws))
    verbs = sorted({w.strip('.,;:()').lower() for w in ws} & FINITE)
    if verbs:
        bad.append('finite verb (%s): the claim belongs in the first sentence'
                   % ', '.join(verbs))
    if re.match(r'(What|Why|Where|How|Whether|When|Which)\b', title):
        bad.append('opens with an interrogative')
    if re.search(r',\s*(and|which|so|but)\b|;|---', title):
        bad.append('joins a second clause')
    if re.match(r'(The scope of|The nature of|A note on|The question of|On the)\b', title):
        bad.append('names a category instead of its object')
    return bad


#: Every verdict the rule states, as the control for the test above.  The
#: second, fourth and fifth were GOOD under the rule of 26-27 October and are
#: BAD under the PI's of 4 November; the supplement now carries
#: `The deflection response.` and `The kernels, not a solver.` in their place.
TITLE_EXEMPLARS = (
    ('What this establishes, and what it does not.', False),
    ('What cancels is the deflection response, and variance conservation is not established.', False),
    ('The scope of this statement, which is the kernels and not any solver.', False),
    ('This is a statement about the kernels and not about any solver.', False),
    ('Criterion 5b compares against CAMB and CLASS. It does not port them.', False),
    ('A note on the damping coefficient.', False),
    ('Why the peak moves.', False),
    ('What gates this, and what each gate can and cannot see', False),
    ('The kernel is the cascade', False),
    ('The monopole and the dipole carry the dynamics, and the quadrupole is not negligible.', False),
    ('The deflection response.', True),
    ('The kernels, not a solver.', True),
    ('Suppression, not truncation', True),
    ('The hold and the peaks.', True),
    ('The number of terms.', True),
    ('Open questions', True),
    (r"The $\kappa'$ ledger", True),
    ('Asserted, not gated', True),
    ('The almost-EGS bounds', True),
    ('Markovianity and memory', True),
)

#: Bold in prose: a short tag is the convention, a sentence is the failure.
BOLD_MAX_WORDS = 3
BOLD_EXEMPLARS = (
    (r'\textbf{T-57}', True),
    (r'\textbf{S4c}', True),
    (r'\textbf{A-n}', True),
    (r'\textbf{What carries to those sectors is the geometric statement}', False),
    (r'\textbf{Refuted by measurement, 2026-10-25}', False),
)

_TABLE = re.compile(r'\\begin\{(tabularx|longtable|tabular)\}.*?\\end\{\1\}', re.S)
_HEAD = re.compile(r'\\(section|subsection|subsubsection|paragraph)\{'
                   r'((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}')
_BOLD = re.compile(r'\\textbf\{((?:[^{}]|\{[^{}]*\})*)\}')


def bold_sentences(prose):
    return [b for b in _BOLD.findall(prose) if len(_words(b)) > BOLD_MAX_WORDS]


def _regions(text):
    """Every section's body, by \\section title."""
    heads = [(m.start(), m.group(1)) for m in re.finditer(r'\\section\{([^}]*)\}', text)]
    out = {}
    for i, (pos, title) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
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
    stale = [s for s in EXCLUDED_SECTIONS if s not in regions]
    if stale:
        bad.append('excluded section(s) not found in %s, so the exclusion is '
                   'stale: %s' % (tex.name, ', '.join(stale)))
    n_heads = 0
    for name, body in regions.items():
        if name in EXCLUDED_SECTIONS:
            print('       excluded  %s: %s' % (name, EXCLUDED_SECTIONS[name]))
            continue
        prose = _TABLE.sub('', body)
        for b in bold_sentences(prose):
            bad.append('%s: bold sentence in prose -- a short tag is the '
                       'convention, a sentence is the failure\n         %s'
                       % (name, re.sub(r'\s+', ' ', b)[:76]))
        for b in BANNED:
            if b in body:
                bad.append('%s: banned construction %r' % (name, b))
        grammars = {m.group(1) for m in re.finditer(r'\\begin\{(tabularx|longtable)\}', body)}
        if len(grammars) > 1:
            bad.append('%s: %d table grammars in one section (%s); one per section'
                       % (name, len(grammars), ', '.join(sorted(grammars))))
        for m in _HEAD.finditer(body):
            n_heads += 1
            title = re.sub(r'\s+', ' ', m.group(2)).strip()
            why = title_failures(title)
            if not why:
                continue
            if title in TITLE_DEBT:
                print('       debt  %s: %s  [%s]' % (name, title[:56], TITLE_DEBT[title]))
                continue
            bad.append('%s: %s title -- %s\n         %s'
                       % (name, m.group(1), '; '.join(why), title))

    # the controls: the tests must reproduce every verdict stated above
    wrong = [tl for tl, good in TITLE_EXEMPLARS if bool(title_failures(tl)) == good]
    wrong += [b for b, good in BOLD_EXEMPLARS if bool(bold_sentences(b)) == good]
    if wrong:
        bad.append('CONTROL FAILED -- the tests no longer reproduce the stated '
                   'verdicts on %d exemplar(s). They are measuring something '
                   'else and must not be trusted:\n         %s'
                   % (len(wrong), '\n         '.join(t[:76] for t in wrong)))

    detail = '\n'.join(bad) if bad else ('%s: %d sections, %d headings read'
                                         % (tex.name, len(regions) - len(EXCLUDED_SECTIONS),
                                            n_heads))
    return report('F  the supplement keeps its own voice', not bad, detail)


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
