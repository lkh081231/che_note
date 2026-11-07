"""ch13 isomer-explorer — every isomer of 8 molecular formulae, guess first, stereo split.

usage: uv run --with playwright python -I colab/tests/ch13_isomer-explorer.py $COLAB_TMP/cells/ch13-isomer-explorer.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch13 --cell isomer-explorer)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
CHROMIUM = '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else chrome()

# formula: structural [(name, relation to previous, in syllabus table)], stereo-split list, groups (structural)
P, CH, FG, CT, EN = 'pos', 'chain', 'fg', 'ct', 'en'
WANT = {
    'C4H10': ([('butane', '', 1), ('2-methylpropane', CH, 1)], None, [('alkane', 2)]),
    'C5H12': ([('pentane', '', 1), ('2-methylbutane', CH, 1), ('2,2-dimethylpropane', CH, 1)], None, [('alkane', 3)]),
    'C4H8': ([('but-1-ene', '', 1), ('but-2-ene', P, 1), ('2-methylpropene', CH, 1), ('cyclobutane', FG, 1), ('methylcyclopropane', CH, 1)],
             [('but-1-ene', '', 1), ('cis-but-2-ene', P, 1), ('trans-but-2-ene', CT, 1), ('2-methylpropene', CH, 1),
              ('cyclobutane', FG, 1), ('methylcyclopropane', CH, 1)],
             [('alkene', 3), ('cycloalkane', 2)]),
    'C3H6O': ([('propanal', '', 1), ('propanone', FG, 1), ('prop-2-en-1-ol', FG, 1), ('methoxyethene', FG, 0),
               ('cyclopropanol', FG, 0), ('oxetane', FG, 0), ('methyloxirane', CH, 0)],
              'en:methyloxirane',
              [('aldehyde', 1), ('ketone', 1), ('alkene + alcohol', 1), ('ether', 1), ('cyclic alcohol', 1), ('cyclic ether', 2)]),
    'C3H6O2': ([('propanoic acid', '', 1), ('methyl ethanoate', FG, 1), ('ethyl methanoate', P, 1)], None,
               [('carboxylic acid', 1), ('ester', 2)]),
    'C4H9Br': ([('1-bromobutane', '', 1), ('2-bromobutane', P, 1), ('1-bromo-2-methylpropane', CH, 1), ('2-bromo-2-methylpropane', P, 1)],
               'en:2-bromobutane', [('halogenoalkane', 4)]),
    'C4H10O': ([('butan-1-ol', '', 1), ('butan-2-ol', P, 1), ('2-methylpropan-1-ol', CH, 1), ('2-methylpropan-2-ol', P, 1),
                ('ethoxyethane', FG, 0), ('1-methoxypropane', P, 0), ('2-methoxypropane', CH, 0)],
               'en:butan-2-ol', [('alcohol', 4), ('ether', 3)]),
    'C3H7Cl': ([('1-chloropropane', '', 1), ('2-chloropropane', P, 1)], None, [('halogenoalkane', 2)]),
}
COUNTS = {'C4H10': (2, 2), 'C5H12': (3, 3), 'C4H8': (5, 6), 'C3H6O': (7, 8), 'C3H6O2': (3, 3),
          'C4H9Br': (4, 5), 'C4H10O': (7, 8), 'C3H7Cl': (2, 2)}
CHIRAL = {'C3H6O': 'methyloxirane', 'C4H9Br': '2-bromobutane', 'C4H10O': 'butan-2-ol'}


def stereo_list(f):
    s, st, _ = WANT[f]
    if st is None:
        return s
    if isinstance(st, list):
        return st
    name = st.split(':', 1)[1]
    out = []
    for n, r, y in s:
        out.append((n, r, y))
        if n == name:
            out.append((n, EN, y))
    return out


HELP = r'''() => { window.T = {
  ie() { return document.querySelector('.k').__ie; },
  cards() {
    return [...document.querySelectorAll('.ie-groups .ie-card')].map(c => ({
      name: c.getAttribute('data-name'), rel: c.getAttribute('data-rel'), syl: +c.getAttribute('data-syl'),
      off: !!c.querySelector('.ie-off'), pill: (c.querySelector('.ie-rel') || {}).textContent || '',
      stars: c.querySelectorAll('text.ie-star').length }));
  },
  groups() {
    return [...document.querySelectorAll('.ie-grp')].map(g => [g.querySelector('.ie-gh b').textContent, g.querySelectorAll('.ie-card').length,
      !!g.querySelector('.ie-gh .ie-off')]);
  },
  /* the '*' label: nearer its own chiral C than any other atom, and close to it */
  stars() {
    return [...document.querySelectorAll('text.ie-star')].map(t => {
      const s = t.ownerSVGElement, A = JSON.parse(s.getAttribute('data-atoms')), i = +t.getAttribute('data-atom');
      const b = t.getBBox(), cx = b.x + b.width / 2, cy = b.y + b.height / 2;
      const d = a => Math.hypot(a.x - cx, a.y - cy);
      const v = s.viewBox.baseVal;
      return { name: s.getAttribute('aria-label'), own: d(A[i]), other: Math.min(...A.filter(a => a.i !== i).map(d)),
               named: A[i].n === 's', out: b.x < v.x || b.y < v.y || b.x + b.width > v.x + v.width || b.y + b.height > v.y + v.height };
    });
  },
  /* per card: relation pill above the structure, everything inside the card, svg not clipped */
  layout() {
    const bad = [];
    document.querySelectorAll('.ie-groups .ie-card').forEach(c => {
      const cr = c.getBoundingClientRect(), n = c.getAttribute('data-name');
      const st = c.querySelector('.ie-stage').getBoundingClientRect(), sv = c.querySelector('svg').getBoundingClientRect();
      const pill = c.querySelector('.ie-rel').getBoundingClientRect();
      if (pill.bottom > sv.top - 0.5) bad.push(n + ': pill overlaps structure');
      if (sv.left < st.left - 0.5 || sv.right > st.right + 0.5 || sv.top < st.top - 0.5 || sv.bottom > st.bottom + 0.5) bad.push(n + ': svg clipped by stage');
      c.querySelectorAll('.ie-hd > *, .ie-name, .ie-why, .ie-st, .ie-tagl, .ie-off').forEach(e => {
        const r = e.getBoundingClientRect();
        if (r.left < cr.left + 1 || r.right > cr.right - 1 || e.scrollWidth > e.clientWidth + 1) bad.push(n + ': ' + e.className + ' overflows card');
      });
    });
    return bad;
  },
  /* cards on one line (across groups too) share top, height and stage top; group headers stay on one line */
  rows() {
    const bad = [];
    document.querySelectorAll('.ie-gh').forEach(h => { if (h.scrollWidth > h.clientWidth + 1 || h.getBoundingClientRect().height > 30) bad.push('header ' + h.textContent); });
    [document].forEach(g => {
      const rows = {};
      g.querySelectorAll('.ie-groups .ie-card').forEach(c => {
        const r = c.getBoundingClientRect(), k = Math.round(r.top);
        (rows[k] = rows[k] || []).push({ h: r.height, s: c.querySelector('.ie-stage').getBoundingClientRect().top, n: c.getAttribute('data-name') });
      });
      Object.values(rows).forEach(L => {
        if (L.some(x => Math.abs(x.h - L[0].h) > 0.5 || Math.abs(x.s - L[0].s) > 0.5)) bad.push(L.map(x => x.n).join(' / '));
      });
    });
    return bad;
  },
  minFont() {   /* SVG: CSS px × rendered width / viewBox width; HTML card texts: computed px */
    let m = 99;
    document.querySelectorAll('.ie-groups svg.cf').forEach(s => {
      const k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
      s.querySelectorAll('text').forEach(t => { m = Math.min(m, parseFloat(getComputedStyle(t).fontSize) * k); });
    });
    document.querySelectorAll('.ie-groups .ie-card *, .ie-leg *, .ie-gh *').forEach(e => {
      if (e.closest('svg') || !e.textContent.trim()) return;
      m = Math.min(m, parseFloat(getComputedStyle(e).fontSize));
    });
    return m;
  },
  nameFont() { return Math.min(...[...document.querySelectorAll('.ie-name')].map(e => parseFloat(getComputedStyle(e).fontSize))); },
  overflow() { const k = document.querySelector('.k'); return k.scrollWidth - k.clientWidth; },
  scale() {   /* every structure drawn at the same bond length (px per viewBox unit) */
    return [...document.querySelectorAll('.ie-groups svg.cf')].map(s => s.getBoundingClientRect().width / s.viewBox.baseVal.width);
  }
}; }'''


def shot(page, sel, path):
    """element screenshot via a page clip (Locator.screenshot waits for rAF, hangs with parallel Chromes)"""
    bb = page.eval_on_selector(
        sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def pick(page, f):
    page.click(f'.ie-fs button[data-f="{f}"]')
    page.wait_for_timeout(40)


def stereo(page, on):
    if page.is_checked('.ie-stereo') != on:
        page.click('.ie-stereo')
        page.wait_for_timeout(40)


def hide_again(page):
    if page.locator('.ie-again').is_visible():
        page.click('.ie-again')


def guess(page, v, enter=False):
    page.fill('.ie-in', str(v))
    if enter:
        page.press('.ie-in', 'Enter')
    else:
        page.click('.ie-go')
    page.wait_for_timeout(40)
    return page.inner_text('.ie-fb'), page.get_attribute('.ie-fb', 'class')


def reveal(page, f):
    """fresh guess round for f and a right guess, so the cards are shown"""
    pick(page, f)
    hide_again(page)
    n = COUNTS[f][1 if page.is_checked('.ie-stereo') else 0]
    return guess(page, n)


def verify_cards(page, f, on, tag):
    want = stereo_list(f) if on else WANT[f][0]
    got = page.evaluate('T.cards()')
    check(f'{tag} {f}: {len(want)} cards', len(got) == len(want) == COUNTS[f][1 if on else 0], f'{len(got)} vs {len(want)}')
    check(f'{tag} {f}: names in order', [c['name'] for c in got] == [w[0] for w in want], str([c['name'] for c in got]))
    check(f'{tag} {f}: relation to the previous card', [c['rel'] for c in got] == [w[1] for w in want], str([c['rel'] for c in got]))
    full = {'chain': 'chain isomer', 'pos': 'positional isomer', 'fg': 'functional group isomer', 'ct': 'cis / trans isomer', 'en': 'enantiomer'}
    check(f'{tag} {f}: pill text matches relation (first card = 起点)',
          all(c['pill'] == (full[c['rel']] if c['rel'] else '起点') for c in got), str([c['pill'] for c in got]))
    check(f'{tag} {f}: 不在 syllabus 表里 badge exactly on the off-table cards',
          [c['off'] for c in got] == [not w[2] for w in want] and [c['syl'] for c in got] == [w[2] for w in want],
          str([(c['name'], c['off']) for c in got]))
    nchir = sum(1 for c in got if c['name'] == CHIRAL.get(f))
    check(f'{tag} {f}: one * per chiral card ({nchir})', sum(c['stars'] for c in got) == nchir and
          all(c['stars'] == (1 if c['name'] == CHIRAL.get(f) else 0) for c in got), str([(c['name'], c['stars']) for c in got]))
    st = page.evaluate('T.stars()')
    check(f'{tag} {f}: * sits on the chiral C (@{{s}}), nearest to it, within 24 units, inside the viewBox',
          all(s['named'] and s['own'] < s['other'] and s['own'] <= 24 and not s['out'] for s in st), str(st))
    check(f'{tag} {f}: no label clash', page.locator('[data-clash]').count() == 0, str(page.locator('[data-clash]').count()))
    leg = page.evaluate('''() => ({ rel: [...document.querySelectorAll('.ie-leg .ie-rel[data-k]')].filter(e => e.offsetParent).map(e => e.getAttribute('data-k')),
                                    star: !!document.querySelector('.ie-leg .ie-key').offsetParent })''')
    used = [k for k in ('chain', 'pos', 'fg', 'ct', 'en') if any(c['rel'] == k for c in got)]
    check(f'{tag} {f}: legend lists exactly the relations on the cards, * only with a chiral centre',
          leg['rel'] == used and leg['star'] == (f in CHIRAL), f'{leg} vs {used}')
    sm = page.inner_text('.ie-sum')
    kinds = {'C4H8': ('cis / trans', 'enantiomers'), 'C4H9Br': ('enantiomers', 'cis / trans'),
             'C4H10O': ('enantiomers', 'cis / trans'), 'C3H6O': ('enantiomers', 'cis / trans')}
    if f in kinds:
        check(f'{tag} {f}: summary names only the stereoisomer kind it has', kinds[f][0] in sm and kinds[f][1] not in sm, sm)
    lay = page.evaluate('T.layout()')
    check(f'{tag} {f}: pill above structure, nothing overflows the card, svg not clipped', not lay, '; '.join(lay))
    rows = page.evaluate('T.rows()')
    check(f'{tag} {f}: grid rows aligned (same card top / height / stage top)', not rows, str(rows))
    sc = page.evaluate('T.scale()')
    check(f'{tag} {f}: all structures at one scale', max(sc) - min(sc) < 0.01, str(sc))
    return got


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme} PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        page.evaluate(HELP)

        if scheme == 'dark':
            for f, on in (('C4H8', True), ('C4H10O', True), ('C3H6O', True), ('C3H6O2', False)):
                stereo(page, on)
                reveal(page, f)
                verify_cards(page, f, on, 'dark')
                shot(page, '.k', OUT / f'dark-{f}{"-stereo" if on else ""}.png')
            stereo(page, True)
            reveal(page, 'C4H10O')
            shot(page, '.ie-grp[data-g="alcohol"]', OUT / 'dark-zoom-alcohol.png')
            pick(page, 'C4H9Br'); hide_again(page)
            guess(page, 4)
            shot(page, '.ie-guess', OUT / 'dark-zoom-guess-wrong.png')
            ctx.close()
            continue

        print('== start')
        check('8 formulae in the stated order', page.evaluate('T.ie().ORDER') == list(WANT), str(page.evaluate('T.ie().ORDER')))
        check('guess mode on by default', page.is_checked('.ie-gmode'))
        check('stereo off by default', not page.is_checked('.ie-stereo'))
        check('cards hidden before the guess', not page.is_visible('.ie-res') and page.locator('.ie-card').count() == 0)
        check('prompt asks for structural isomers of C₄H₁₀', 'C₄H₁₀' in page.inner_text('.ie-q') and 'structural isomer' in page.inner_text('.ie-q'))
        shot(page, '.k', OUT / 'card-start.png')

        for f in WANT:
            print(f'== {f}')
            stereo(page, False)
            pick(page, f)
            hide_again(page)
            check(f'{f}: hidden until guessed', not page.is_visible('.ie-res') and page.is_visible('.ie-wait'))
            fb, cls = guess(page, COUNTS[f][0])
            check(f'{f}: right guess {COUNTS[f][0]} → ✓', '✓' in fb and 'ok' in cls, fb)
            check(f'{f}: input turns green', 'good' in page.get_attribute('.ie-in', 'class'))
            check(f'{f}: summary states both counts', page.inner_text('.ie-sum .ie-ns') == str(COUNTS[f][0]) and
                  (page.locator('.ie-sum .ie-nt').count() == 0 if COUNTS[f][0] == COUNTS[f][1] else page.inner_text('.ie-sum .ie-nt') == str(COUNTS[f][1])),
                  page.inner_text('.ie-sum'))
            verify_cards(page, f, False, 'structural')
            g = page.evaluate('T.groups()')
            check(f'{f}: grouped by functional group', [(x[0].split('（')[0], x[1]) for x in g] == WANT[f][2], str(g))
            if f == 'C3H6O':
                w = page.inner_text('.ie-card[data-name="cyclopropanol"] .ie-why')
                check('C3H6O: cyclopropanol 的「为什么」对比的是上一张 methoxyethene（ether），不是 prop-2-en-1-ol', 'C–O–C' in w and 'ether' in w, w)
            if CHIRAL.get(f):
                txt = page.inner_text(f'.ie-card[data-name="{CHIRAL[f]}"] .ie-st')
                check(f'{f}: chiral card says C2 is a chiral centre', 'chiral centre' in txt and 'C2' in txt, txt)
            stereo(page, True)
            check(f'{f}: stereo on keeps cards shown', page.is_visible('.ie-res'))
            q = page.inner_text('.ie-q')
            check(f'{f}: prompt still shows the question that was answered (structural)', 'structural isomer' in q and '分开算' not in q, q)
            verify_cards(page, f, True, 'stereo')
            if f in ('C4H8', 'C4H10O', 'C3H6O', 'C4H9Br', 'C3H6O2'):
                shot(page, '.k', OUT / f'card-{f}-stereo.png')
            if f in ('C3H6O', 'C4H8'):
                stereo(page, False)
                shot(page, '.k', OUT / f'card-{f}.png')

        print('== stereo pair drawings')
        stereo(page, True)
        reveal(page, 'C4H8')
        sids = page.eval_on_selector_all('.ie-card', 'cs => cs.map(c => c.getAttribute("data-sid"))')
        check('C4H8 stereo: cis and trans drawn from different ChemFig', 'cis2ene' in sids and 'trans2ene' in sids, str(sids))
        # cis: both CH3 ends on the same side of the horizontal C=C; trans: opposite
        geo = page.evaluate('''() => ['cis2ene', 'trans2ene'].map(id => {
            const s = document.querySelector('.ie-card[data-sid="' + id + '"] svg'), A = JSON.parse(s.getAttribute('data-atoms'));
            return [A[1].y - A[2].y, Math.sign(A[0].y - A[1].y), Math.sign(A[3].y - A[2].y)]; })''')
        check('cis-but-2-ene: C=C horizontal, CH₃ both up', abs(geo[0][0]) < 0.1 and geo[0][1] == geo[0][2], str(geo))
        check('trans-but-2-ene: C=C horizontal, CH₃ on opposite sides', abs(geo[1][0]) < 0.1 and geo[1][1] == -geo[1][2], str(geo))
        reveal(page, 'C4H10O')
        mir = page.evaluate('''() => ['ol2a', 'ol2b'].map(id => {
            const s = document.querySelector('.ie-card[data-sid="' + id + '"] svg'), A = JSON.parse(s.getAttribute('data-atoms'));
            const B = JSON.parse(s.getAttribute('data-bonds'));
            return { xs: A.map(a => +(a.x - A[1].x).toFixed(1)), ys: A.map(a => +(a.y - A[1].y).toFixed(1)), w: B.filter(x => x[2] === 'w').length }; })''')
        check('butan-2-ol enantiomers: mirror images (x → −x, same y), one wedge each',
              mir[0]['xs'] == [-x if x else 0.0 for x in mir[1]['xs']] and mir[0]['ys'] == mir[1]['ys'] and mir[0]['w'] == mir[1]['w'] == 1, str(mir))
        tl = page.eval_on_selector_all('.ie-card[data-name="butan-2-ol"] .ie-tagl', 'es => es.map(e => e.textContent)')
        check('enantiomer cards tagged ① / ②', len(tl) == 2 and '①' in tl[0] and '②' in tl[1], str(tl))
        shot(page, '.ie-grp[data-g="alcohol"]', OUT / 'zoom-alcohol-enantiomers.png')
        reveal(page, 'C3H6O')
        shot(page, '.ie-grp[data-g="cyclic ether"]', OUT / 'zoom-cyclic-ether.png')
        reveal(page, 'C4H8')
        shot(page, '.ie-grp[data-g="alkene"]', OUT / 'zoom-alkene-cis-trans.png')

        print('== guess feedback')
        stereo(page, False)
        pick(page, 'C4H8'); hide_again(page)
        check('stereo off prompt: structural isomer', 'structural isomer' in page.inner_text('.ie-q'))
        fb, cls = guess(page, 6)
        check('C4H8 stereo off, guess 6 → ✗ + "6 counts cis / trans too"', '✗' in fb and 'bad' in cls and 'cis / trans' in fb and '实际 5' in fb, fb)
        check('cards revealed after a wrong guess too', page.is_visible('.ie-res') and page.locator('.ie-card').count() == 5)
        check('wrong guess turns the box red', 'badv' in page.get_attribute('.ie-in', 'class'))
        check('input locked after reveal; 藏起来重猜 shown', page.is_disabled('.ie-in') and page.is_visible('.ie-again') and not page.is_visible('.ie-go'))
        shot(page, '.ie-guess', OUT / 'zoom-guess-wrong.png')
        hide_again(page)
        check('藏起来重猜 hides the cards and clears the box', not page.is_visible('.ie-res') and page.input_value('.ie-in') == '' and
              page.inner_text('.ie-fb') == '')
        stereo(page, True)
        check('stereo on prompt mentions cis / trans', 'cis / trans' in page.inner_text('.ie-q') and 'C₄H₈' in page.inner_text('.ie-q'))
        fb, cls = guess(page, 5)
        check('C4H8 stereo on, guess 5 → ✗ + "5 is the structural count"', '✗' in fb and 'structural isomer 的数目' in fb and '实际 6' in fb, fb)
        hide_again(page)
        fb, cls = guess(page, 6, enter=True)
        check('Enter submits; C4H8 stereo on, 6 → ✓', '✓' in fb and 'ok' in cls and page.is_visible('.ie-res'), fb)
        stereo(page, False)
        pick(page, 'C4H10O'); hide_again(page)
        fb, cls = guess(page, 4)
        check('C4H10O guess 4 → ✗ 少了 3 个, hints ether', '✗' in fb and '少了 3 个' in fb and 'ether' in fb, fb)
        pick(page, 'C5H12'); hide_again(page)
        fb, cls = guess(page, 5)
        check('C5H12 guess 5 → ✗ 多了 2 个, same structure drawn twice', '✗' in fb and '多了 2 个' in fb and '同一个' in fb, fb)
        pick(page, 'C3H7Cl'); hide_again(page)
        fb, cls = guess(page, 'abc')
        check('non-integer → asks for an integer, cards stay hidden', '整数' in fb and not page.is_visible('.ie-res'), fb)
        page.fill('.ie-in', '2')
        check('typing again clears the complaint', page.inner_text('.ie-fb') == '')
        fb, cls = guess(page, '2 个')
        check('"2 个" accepted → ✓', '✓' in fb, fb)
        pick(page, 'C4H10O')
        check('state kept per formula (C4H10O still revealed with its ✗)', page.is_visible('.ie-res') and '✗' in page.inner_text('.ie-fb'))
        pick(page, 'C3H6O2'); hide_again(page)
        check('C3H6O2 prompt states the scope (acid / ester only)', 'carboxylic acid 与 ester' in page.inner_text('.ie-q'))
        page.click('.ie-skip')
        check('不猜，直接看 reveals without feedback', page.is_visible('.ie-res') and page.inner_text('.ie-fb') == '')
        check('C3H6O2 scope line under the summary', page.is_visible('.ie-scope') and '只列' in page.inner_text('.ie-scope'))
        pick(page, 'C4H9Br'); hide_again(page)
        page.click('.ie-gmode')
        check('guess mode off → guess box gone, cards shown at once', not page.is_visible('.ie-guess') and page.is_visible('.ie-res') and
              page.locator('.ie-card').count() == 4)
        page.click('.ie-gmode')
        check('guess mode back on → C4H9Br hidden again (not guessed yet)', page.is_visible('.ie-guess') and not page.is_visible('.ie-res'))
        check('xref links open in a new tab', page.eval_on_selector_all('.ie-more a.xref', 'as => as.length === 2 && as.every(a => a.target === "_blank")'))
        check('no console error so far', not errors, '; '.join(errors))

        print('== narrow (720 px)')
        page.set_viewport_size({'width': 720, 'height': 1100}); page.wait_for_timeout(200)
        for f in WANT:
            for on in (False, True):
                stereo(page, on)
                reveal(page, f)
                ov, fs, nf = page.evaluate('T.overflow()'), page.evaluate('T.minFont()'), page.evaluate('T.nameFont()')
                lay, rows = page.evaluate('T.layout()'), page.evaluate('T.rows()')
                clash = page.locator('[data-clash]').count()
                check(f'720 px {f}{" stereo" if on else ""}: no overflow, text ≥ 12 px, names ≥ 12 px, no clash, layout ok',
                      ov <= 0 and fs >= 12 and nf >= 12 and clash == 0 and not lay and not rows,
                      f'overflow {ov}, font {fs:.2f}, name {nf}, clash {clash}, {lay} {rows}')
                if on and f in ('C4H10O', 'C3H6O', 'C4H8'):
                    shot(page, '.k', OUT / f'card-720-{f}-stereo.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
