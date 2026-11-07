"""ch13 formula-count — skeletal → molecular / empirical formula cell test.

usage: uv run --with playwright python -I colab/tests/ch13_formula-count.py $COLAB_TMP/cells/ch13-formula-count.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch13 --cell formula-count)
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

# id: (molecular, empirical, gcd, k = rings + π bonds, C count, hidden H on C, written H)
WANT = {
    'butan2ol': ('C₄H₁₀O', 'C₄H₁₀O', 1, 0, 4, 9, 1),
    'but1ene': ('C₄H₈', 'CH₂', 4, 1, 4, 8, 0),
    'ethanoic': ('C₂H₄O₂', 'CH₂O', 2, 1, 2, 3, 1),
    'diol': ('C₂H₆O₂', 'CH₃O', 2, 0, 2, 4, 2),
    'butanal': ('C₄H₈O', 'C₄H₈O', 1, 1, 4, 8, 0),
    'butanone': ('C₄H₈O', 'C₄H₈O', 1, 1, 4, 8, 0),
    'ester': ('C₄H₈O₂', 'C₂H₄O', 2, 1, 4, 8, 0),
    'amine': ('C₃H₉N', 'C₃H₉N', 1, 0, 3, 7, 2),
    'nitrile': ('C₅H₉N', 'C₅H₉N', 1, 2, 5, 9, 0),
    'tbucl': ('C₄H₉Cl', 'C₄H₉Cl', 1, 0, 4, 9, 0),
    'cyhex': ('C₆H₁₂O', 'C₆H₁₂O', 1, 1, 6, 11, 1),
    'E': ('C₆H₇NO₂', 'C₆H₇NO₂', 1, 4, 6, 7, 0),
    'X': ('C₅H₁₂O₄', 'C₅H₁₂O₄', 1, 0, 5, 8, 4),
}
SUBD = '₀₁₂₃₄₅₆₇₈₉'

HELP = r'''() => { window.T = {
  root() { return [...document.querySelectorAll('.k, [id]')].find(e => e.__fc); },
  svg() { return document.querySelector('.fc-stage svg'); },
  targets() {
    return [...document.querySelectorAll('.fc-stage .fc-t')].map(t => {
      const r = t.getBoundingClientRect();
      return { i: +t.getAttribute('data-i'), x: r.x + r.width / 2, y: r.y + r.height / 2 };
    });
  },
  segHit(s, r) {
    const inside = (x, y) => x > r.x && x < r.x + r.w && y > r.y && y < r.y + r.h;
    if (inside(s[0], s[1]) || inside(s[2], s[3])) return true;
    const E = [[r.x, r.y, r.x + r.w, r.y], [r.x, r.y + r.h, r.x + r.w, r.y + r.h], [r.x, r.y, r.x, r.y + r.h], [r.x + r.w, r.y, r.x + r.w, r.y + r.h]];
    return E.some(e => {
      const d = (s[2] - s[0]) * (e[3] - e[1]) - (s[3] - s[1]) * (e[2] - e[0]);
      if (!d) return false;
      const t = ((e[0] - s[0]) * (e[3] - e[1]) - (e[1] - s[1]) * (e[2] - e[0])) / d;
      const u = ((e[0] - s[0]) * (s[3] - s[1]) - (e[1] - s[1]) * (s[2] - s[0])) / d;
      return t >= 0 && t <= 1 && u >= 0 && u <= 1;
    });
  },
  rr(a, b) {   /* gap between two rects (0 if they touch / overlap) */
    const dx = Math.max(a.x - b.x - b.w, 0, b.x - a.x - a.w), dy = Math.max(a.y - b.y - b.h, 0, b.y - a.y - a.h);
    return Math.hypot(dx, dy);
  },
  /* every hidden-H label: its own C, nearest other atom, bond overlap, viewBox */
  hLabels() {
    const s = T.svg(), v = s.viewBox.baseVal, A = T.root().__fc.atoms();
    const segs = [...s.querySelectorAll('.cf-b line')].map(l => ['x1', 'y1', 'x2', 'y2'].map(k => +l.getAttribute(k)));
    const box = a => {
      const t = s.querySelector('text.cf-a[data-i="' + a.i + '"]');
      if (!t) return { x: a.x, y: a.y, w: 0, h: 0 };
      const b = t.getBBox(); return { x: b.x, y: b.y, w: b.width, h: b.height };
    };
    const labs = [...s.querySelectorAll('text.fc-h')];
    const rects = labs.map(t => { const b = t.getBBox(); return { x: b.x, y: b.y, w: b.width, h: b.height }; });
    return labs.map((t, n) => {
      const i = +t.getAttribute('data-atom'), r = rects[n], a = A[i];
      const cx = r.x + r.w / 2, cy = r.y + r.h / 2;
      const others = A.filter(o => o.i !== i);
      return {
        i, txt: t.textContent, h: a.h, carbon: a.carbon, cx, cy,
        gapOwn: T.rr(r, { x: a.x, y: a.y, w: 0, h: 0 }),
        cOwn: Math.hypot(a.x - cx, a.y - cy),
        cOther: Math.min(...others.map(o => Math.hypot(o.x - cx, o.y - cy))),
        gapOther: Math.min(...others.map(o => T.rr(r, box(o)))),
        bonds: segs.filter(sg => T.segHit(sg, r)).length,
        overLab: rects.filter((q, m) => m !== n && T.rr(q, r) === 0).length,
        out: r.x < v.x - 0.5 || r.y < v.y - 0.5 || r.x + r.w > v.x + v.width + 0.5 || r.y + r.h > v.y + v.height + 0.5,
      };
    });
  },
  counts() {
    const o = {};
    document.querySelectorAll('.fc-c').forEach(c => { o[c.getAttribute('data-el')] = c.querySelector('b').textContent; });
    return o;
  },
  clipped() {   /* the structure must not be cut off by the stage (overflow:hidden) */
    const st = document.querySelector('.fc-stage').getBoundingClientRect(), r = T.svg().getBoundingClientRect();
    return Math.max(st.x - r.x, r.right - st.right, st.y - r.y, r.bottom - st.bottom);
  },
  cntFit() {   /* counter labels / numbers stay inside their boxes (X(Cl) is the longest) */
    return [...document.querySelectorAll('.fc-c')].filter(c => {
      const r = c.getBoundingClientRect();
      return [...c.children].some(e => { const q = e.getBoundingClientRect(); return e.scrollWidth > e.clientWidth + 0.5 || q.left < r.left || q.right > r.right; });
    }).map(c => c.getAttribute('data-el') + ':' + c.textContent);
  },
  minFont() {   /* CSS px × rendered width / viewBox width over every text in the structure */
    const s = T.svg(), k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
    return Math.min(...[...s.querySelectorAll('text')].filter(t => getComputedStyle(t).display !== 'none')
      .map(t => parseFloat(getComputedStyle(t).fontSize) * k));
  }
}; }'''


def shot(page, sel, path):
    """element screenshot via a page clip (avoids Locator.screenshot GPU rAF hang)."""
    bb = page.eval_on_selector(
        sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def sub(n):
    return ''.join(SUBD[int(d)] for d in str(n))


def goto_q(page, k):
    page.select_option('.fc-jmp', str(k))
    page.wait_for_timeout(60)


def click_all(page):
    """real mouse clicks on every atom, one at a time; returns (all hit their own atom, steps)"""
    page.eval_on_selector('.fc-stage', 'e => e.scrollIntoView({block: "center"})')
    page.wait_for_timeout(40)
    ok, log = True, []
    for t in page.evaluate('T.targets()'):
        before = page.evaluate('T.root().__fc.done()')
        page.mouse.click(t['x'], t['y'])
        after = page.evaluate('T.root().__fc.done()')
        newly = [j for j, (a, b) in enumerate(zip(before, after)) if b and not a]
        if newly != [t['i']]:
            ok = False
            log.append(f"click atom {t['i']} → counted {newly}")
    return ok, log


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme} PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        page.evaluate(HELP)
        Q = page.evaluate('T.root().__fc.Q.map(q => q.id)')

        if scheme == 'dark':
            for k, qid in enumerate(Q):
                if qid not in ('E', 'X', 'tbucl'):
                    continue
                goto_q(page, k)
                hit, _ = click_all(page)
                page.click('.fc-emp-btn')
                check(f'dark {qid}: clicks counted', hit)
                check(f'dark {qid}: no label clash', page.locator('[data-clash]').count() == 0)
                shot(page, '.k', OUT / f'dark-{qid}.png')
            shot(page, '.fc-stage', OUT / 'dark-zoom-stage-X.png')
            shot(page, '.fc-side', OUT / 'dark-zoom-side-X.png')
            ctx.close()
            continue

        check('13 questions in the bank', Q == list(WANT), str(Q))
        print('== before counting')
        check('molecular formula hidden before counting', page.inner_text('.fc-mol') == '—')
        check('empirical button disabled before counting', page.is_disabled('.fc-emp-btn'))
        check('H check waits', '数完才能比' in page.inner_text('.fc-hbody'))
        check('progress 0 / n', '已数 0 /' in page.inner_text('.fc-prog'), page.inner_text('.fc-prog'))
        shot(page, '.k', OUT / 'card-start.png')

        for k, qid in enumerate(Q):
            mol, emp, g, kk, nC, hid, wr = WANT[qid]
            print(f'== {qid}')
            goto_q(page, k)
            check(f'{qid}: fresh question, nothing counted', not any(page.evaluate('T.root().__fc.done()')))
            hit, log = click_all(page)
            check(f'{qid}: every real click counts exactly its own atom', hit, '; '.join(log))
            n = len(page.evaluate('T.root().__fc.done()'))
            check(f'{qid}: progress n / n', f'已数 {n} / {n}' in page.inner_text('.fc-prog'), page.inner_text('.fc-prog'))
            got = page.inner_text('.fc-mol').split('\n')[0].strip()
            check(f'{qid}: molecular formula {mol}', got == mol, got)
            c = page.evaluate('T.counts()')
            H = hid + wr
            check(f'{qid}: counter C = {nC}, H = {H}', c['C'] == str(nC) and c['H'] == str(H), str(c))
            hs = page.inner_text('.fc-hsplit')
            check(f'{qid}: H split hidden {hid}' + (f' + written {wr}' if wr else ''),
                  f'隐藏的 {hid}' in hs and ((f'写出来的 {wr}' in hs) if wr else '写出来' not in hs), hs)
            page.click('.fc-emp-btn')
            ef = page.inner_text('.fc-emp-f')
            check(f'{qid}: empirical formula {emp}', ef == emp, ef)
            check(f'{qid}: common divisor {g}', page.get_attribute('.fc-emp', 'data-g') == str(g),
                  page.get_attribute('.fc-emp', 'data-g'))
            hb = page.inner_text('.fc-hbody')
            # every "=" in the saturated-H chain must hold: symbolic side (n = C count) = numeric side = result
            sat_txt = page.inner_text('.fc-hbody .fc-sat').replace('\n', ' ')
            sides = [t.strip() for t in sat_txt.split('：', 1)[1].split('=')][1:]
            def ev(t):
                return eval(t.replace('2n', f'2*{nC}').replace('×', '*').replace('−', '-'), {'__builtins__': {}})
            try:
                vals = [ev(t) for t in sides]
            except Exception as e:
                vals = [repr(e)]
            check(f'{qid}: saturated-H chain — every "=" is true', len(vals) == 3 and len(set(vals)) == 1, f'{sat_txt} → {vals}')
            nb = page.evaluate('''() => [...T.root().querySelectorAll('.fc-hbody *')].filter(e => e.tagName !== 'A' && (getComputedStyle(e).borderTopStyle !== 'none' || getComputedStyle(e).borderBottomStyle !== 'none')).length''')
            check(f'{qid}: H check text carries no stray borders (class collision)', nb == 0, str(nb))
            if kk:
                kn = page.get_attribute('.fc-hbody .k-n', 'data-k') if page.locator('.fc-hbody .k-n').count() else None
                check(f'{qid}: H check → {kk} ring / π bond', kn == str(kk) and f'少了 {2 * kk} 个 H' in hb, f'{kn} | {hb}')
            else:
                check(f'{qid}: H check → saturated, no ring / π bond', '没有 ring，也没有 π bond' in hb, hb)
            L = page.evaluate('T.hLabels()')
            A = page.evaluate('T.root().__fc.atoms()')
            needH = sorted(a['i'] for a in A if a['carbon'] and a['h'] > 0)
            check(f'{qid}: one H label per C that has H', sorted(l['i'] for l in L) == needH, f"{[l['i'] for l in L]} vs {needH}")
            bad_txt = [l for l in L if l['txt'] != 'H' + (sub(l['h']) if l['h'] > 1 else '')]
            check(f'{qid}: H label text = H / H₂ / H₃ by the bond count', not bad_txt, str(bad_txt))
            check(f'{qid}: H labels — no K.label clash', page.locator('.fc-stage [data-clash]').count() == 0,
                  str(page.locator('.fc-stage [data-clash]').count()))
            far = [(l['i'], round(l['gapOwn'], 1)) for l in L if l['gapOwn'] > 12]
            check(f'{qid}: each H label hugs its C (box gap ≤ 12 units)', not far, str(far))
            near = [(l['i'], round(l['cOwn'], 1), round(l['cOther'], 1)) for l in L if l['cOwn'] >= l['cOther']]
            check(f'{qid}: each H label centre is nearer its own C than any other atom', not near, str(near))
            touch = [(l['i'], round(l['gapOther'], 1)) for l in L if l['gapOther'] < 2]
            check(f'{qid}: H labels keep off other atoms / letters (≥ 2 units)', not touch, str(touch))
            onb = [l['i'] for l in L if l['bonds']]
            check(f'{qid}: H labels do not sit on a bond', not onb, str(onb))
            ovl = [l['i'] for l in L if l['overLab']]
            check(f'{qid}: H labels do not touch each other', not ovl, str(ovl))
            if qid == 'cyhex':   # ring Hs go outside the ring, not into the hole
                ring = [x for x in A if x['carbon']]
                gx, gy = sum(x['x'] for x in ring) / 6, sum(x['y'] for x in ring) / 6
                rad = sum(((x['x'] - gx) ** 2 + (x['y'] - gy) ** 2) ** 0.5 for x in ring) / 6
                inner = [(l['i'], round(((l['cx'] - gx) ** 2 + (l['cy'] - gy) ** 2) ** 0.5, 1)) for l in L
                         if ((l['cx'] - gx) ** 2 + (l['cy'] - gy) ** 2) ** 0.5 < rad]
                check('cyhex: no H label inside the ring', not inner, f'ring radius {rad:.1f}: {inner}')
            out = [l['i'] for l in L if l['out']]
            check(f'{qid}: H labels inside the viewBox', not out, str(out))
            if kk:
                last = page.eval_on_selector_all('.fc-hbody .fc-nw', 'es => es.length ? es[es.length - 1].innerText : ""')
                check(f'{qid}: H check tick kept with the last item', '✓' in last, last)
            check(f'{qid}: counter labels fit their boxes', not page.evaluate('T.cntFit()'), str(page.evaluate('T.cntFit()')))
            cl = page.evaluate('T.clipped()')
            check(f'{qid}: structure not clipped by the stage', cl <= 0.5, f'{cl:.1f}px')
            if qid in ('butan2ol', 'nitrile', 'tbucl', 'cyhex', 'E', 'X'):
                shot(page, '.k', OUT / f'card-{qid}.png')
            if qid in ('E', 'X'):
                shot(page, '.fc-stage', OUT / f'zoom-stage-{qid}.png')
                shot(page, '.fc-side', OUT / f'zoom-side-{qid}.png')

        print('== one click explains the C')
        goto_q(page, Q.index('butanone'))
        A = page.evaluate('T.root().__fc.atoms()')
        c2 = next(a for a in A if a['carbon'] and a['h'] == 0)   # the C=O carbon
        t = next(t for t in page.evaluate('T.targets()') if t['i'] == c2['i'])
        page.mouse.click(t['x'], t['y'])
        why = page.inner_text('.fc-why')
        check('C=O carbon: double ×1 (算 2) → H = 4 − 4 = 0', 'double ×1（算 2）' in why and '4 − 4 = 0' in why, why)
        check('C=O carbon gets no H label', page.locator('.fc-stage text.fc-h').count() == 0)
        check('counter bumps C', 'bump' in page.get_attribute('.fc-c[data-el="C"]', 'class'))
        check('molecular formula still hidden mid-way', page.inner_text('.fc-mol') == '—')
        o = next(a for a in A if a['l'] == 'O')
        t = next(t for t in page.evaluate('T.targets()') if t['i'] == o['i'])
        page.mouse.click(t['x'], t['y'])
        check('O click: counter O = 1', page.evaluate('T.counts()')['O'] == '1')
        page.click('.fc-reset')
        check('reset clears counts', page.evaluate('T.counts()')['C'] == '0' and not any(page.evaluate('T.root().__fc.done()')))
        page.focus('.fc-stage .fc-t')
        page.keyboard.press('Enter')
        check('keyboard: Enter on a focused atom counts it', sum(page.evaluate('T.root().__fc.done()')) == 1)
        page.click('.fc-all')
        check('全部显示 counts everything', all(page.evaluate('T.root().__fc.done()')) and page.inner_text('.fc-mol').startswith('C₄H₈O'))
        shot(page, '.k', OUT / 'card-butanone-all.png')

        print('== nav')
        goto_q(page, 0)
        check('prev disabled on first', page.is_disabled('.fc-prev'))
        page.click('.fc-next')
        check('next → question 2', page.evaluate('T.root().__fc.cur()') == 1)
        goto_q(page, len(Q) - 1)
        check('next disabled on last', page.is_disabled('.fc-next'))
        check('X source line cites 9701/22 May/June 2026 Q4(b)', '9701/22 May/June 2026 Q4(b)' in page.inner_text('.fc-src'),
              page.inner_text('.fc-src'))
        check('E source in the select', any('9701/22 Feb/Mar 2026 Q4(d)(iii)' in o
                                            for o in page.eval_on_selector_all('.fc-jmp option', 'os => os.map(o => o.textContent)')))

        print('== typed answers')

        def judge(qid, mol, emp):
            goto_q(page, Q.index(qid))
            page.fill('.fc-in-mol', mol); page.fill('.fc-in-emp', emp)
            page.click('.fc-go')
            return (page.inner_text('.fc-fb-mol') if page.locator('.fc-fb-mol').is_visible() else '',
                    page.get_attribute('.fc-fb-mol', 'class'),
                    page.inner_text('.fc-fb-emp') if page.locator('.fc-fb-emp').is_visible() else '',
                    page.get_attribute('.fc-fb-emp', 'class'))

        m, mc, e, ec = judge('ethanoic', 'C2H4O2', 'CH2O')
        check('ethanoic: C2H4O2 / CH2O both right (ASCII digits)', 'ok' in mc and 'ok' in ec and '✓' in m and '✓' in e, f'{m} | {e}')
        check('right answer box turns green', 'good' in page.get_attribute('.fc-in-mol', 'class'))
        m, mc, e, ec = judge('ethanoic', 'C₂H₄O₂', 'CH₂O')
        check('Unicode subscripts accepted', 'ok' in mc and 'ok' in ec, f'{m} | {e}')
        m, mc, e, ec = judge('ethanoic', 'CH2O', 'C2H4O2')
        check('empirical written as molecular → told it is the empirical formula', 'bad' in mc and '约过的 empirical' in m, m)
        check('molecular written as empirical → told it can still be divided by 2', 'bad' in ec and '还能约' in e and '2' in e, e)
        m, mc, e, ec = judge('ethanoic', 'C4H8O4', 'C3H6O3')
        check('multiple of the molecular formula → ratio right, not the actual atoms', 'bad' in mc and '比例对' in m, m)
        check('empirical not in lowest terms → 还没约到最简', 'bad' in ec and '最简' in e, e)
        m, mc, e, ec = judge('butan2ol', 'C4H8O', 'C4H9O')
        check('wrong H → says H count wrong and how to count it', 'bad' in mc and 'H 的数目不对' in m and '4 − 画出的 bond 数' in m, m)
        check('wrong ratio in empirical', 'bad' in ec and '比例不对' in e, e)
        m, mc, e, ec = judge('butan2ol', 'C3H10O', '')
        check('wrong C → C hint', 'bad' in mc and 'C 的数目不对' in m and '折点' in m, m)
        check('empty empirical box → no feedback', e == '' and 'ok' not in ec and 'bad' not in ec, f'{e!r} {ec}')
        m, mc, e, ec = judge('butan2ol', 'c4h10o', 'C4H10O')
        check('lower-case symbols → unreadable', 'bad' in mc and '读不懂' in m, m)
        m, mc, e, ec = judge('butan2ol', 'H10C4O', 'C4OH10')
        check('H first → ✗ 先写 C、再写 H', 'bad' in mc and '✗' in m and '先写 C、再写 H' in m, m)
        check('H not second → ✗ 先写 C、再写 H', 'bad' in ec and '✗' in e and '先写 C、再写 H' in e, e)
        shot(page, '.fc-type', OUT / 'zoom-typed-order.png')
        for qid, bad in (('ethanoic', 'O2H4C2'), ('ethanoic', 'C2O2H4'), ('ethanoic', 'H4C2O2')):
            m, mc, e, ec = judge(qid, bad, '')
            check(f'{qid}: {bad} → ✗ C first, H second', 'bad' in mc and '先写 C、再写 H' in m and 'C₂H₄O₂' in m, m)
        m, mc, e, ec = judge('E', 'C6H7O2N', 'C6H7O2N')
        check('C, H first but rest not alphabetical → ✓ with 习惯写法 note', 'ok' in mc and '习惯写法' in m and 'C₆H₇NO₂' in m
              and 'ok' in ec and '习惯写法' in e, f'{m} | {e}')
        shot(page, '.fc-type', OUT / 'zoom-typed-hill.png')
        m, mc, e, ec = judge('butanal', 'H6C3O', '')
        check('H6C3O (wrong count AND wrong order) → both said', 'bad' in mc and '数目不对' in m and '先写 C、再写 H' in m, m)
        m, mc, e, ec = judge('tbucl', 'C4H9Cl', 'C4H9CL')
        check('tbucl: C4H9Cl right', 'ok' in mc, m)
        check('CL (capital L) → unreadable', 'bad' in ec and '读不懂' in e, e)
        m, mc, e, ec = judge('E', 'C6H7NO2', 'C6H7NO2')
        check('E: C6H7NO2 right for both', 'ok' in mc and 'ok' in ec, f'{m} | {e}')
        m, mc, e, ec = judge('but1ene', 'C4H8', 'C2H4')
        check('but-1-ene: C2H4 → not lowest terms (CH₂)', 'ok' in mc and 'bad' in ec and '最简' in e, f'{m} | {e}')
        shot(page, '.fc-type', OUT / 'zoom-typed.png')
        shot(page, '.k', OUT / 'card-typed.png')
        check('no console error so far', not errors, '; '.join(errors))

        print('== narrow (720 px)')
        page.set_viewport_size({'width': 720, 'height': 1100}); page.wait_for_timeout(200)
        for k, qid in enumerate(Q):
            goto_q(page, k)
            page.click('.fc-all'); page.click('.fc-emp-btn')
            ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
            fs = page.evaluate('T.minFont()')
            cl = page.evaluate('T.clipped()')
            cf = page.evaluate('T.cntFit()')
            ok = ov <= 0 and fs >= 12 and cl <= 0.5 and page.locator('[data-clash]').count() == 0 and not cf
            check(f'720 px {qid}: no overflow, structure text ≥ 12 px, not clipped, no clash, counters fit', ok,
                  f'overflow {ov}, font {fs:.2f}, clipped {cl:.1f}, counters {cf}')
            if qid in ('E', 'X', 'cyhex', 'tbucl'):
                shot(page, '.k', OUT / f'card-720-{qid}.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
