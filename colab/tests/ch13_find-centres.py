"""ch13 find-centres — mark the chiral centres and the C=C that show cis/trans, check, count 2ⁿ⁺ᵐ.

usage: uv run --with playwright python -I colab/tests/ch13_find-centres.py $COLAB_TMP/cells/ch13-find-centres.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch13 --cell find-centres)
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

# the answer, worked out by hand (IUPAC locants): chiral centres, C=C with cis/trans, 2^(n+m)
WANT = {
    'butan2ol': (['c2'], [], 2),
    'lactic': (['c2'], [], 2),
    'but2ene': ([], ['c2=c3'], 2),
    'but1ene': ([], [], 1),
    'mb2ene': ([], [], 1),
    'mp2ene': ([], ['c2=c3'], 2),
    'butenedioic': ([], ['c2=c3'], 2),
    'malic': (['c2'], [], 2),
    'mbutanoic': (['c2'], [], 2),
    'pentenol': (['c2'], ['c3=c4'], 4),
    'mecyhexol1': ([], [], 1),
    'mecyhexol2': (['c1', 'c2'], [], 4),
    'V': (['c2', 'c3'], [], 4),
    'X': ([], [], 1),
}
# ink gaps (viewBox units): glyphs to disc edge / band edge / bare vertex
GAP_STAR, GAP_CT, GAP_LOC = 4, 4, 8
GAPS = []
SUPS = str.maketrans('0123456789+', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺')

HELP = r'''() => { window.T = {
  api() { return [...document.querySelectorAll('[id]')].find(e => e.__fcn).__fcn; },
  svg() { return document.querySelector('.fcn-stage svg'); },
  /* screen centre + rendered size of every click target */
  targets() {
    return [...document.querySelectorAll('.fcn-stage .fcn-t')].map(t => {
      const r = t.getBoundingClientRect();
      return { kind: t.dataset.kind, i: t.dataset.i == null ? null : +t.dataset.i, key: t.dataset.key || null,
               x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height };
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
  rr(a, b) { const dx = Math.max(a.x - b.x - b.w, 0, b.x - a.x - a.w), dy = Math.max(a.y - b.y - b.h, 0, b.y - a.y - a.h); return Math.hypot(dx, dy); },
  segDist(sg, r) {          /* distance from a segment to a rect (0 if they touch) */
    if (T.segHit(sg, r)) return 0;
    const pd = (px, py) => { const [x1, y1, x2, y2] = sg, L2 = (x2 - x1) ** 2 + (y2 - y1) ** 2;
      const t = L2 ? Math.max(0, Math.min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / L2)) : 0;
      return Math.hypot(px - x1 - t * (x2 - x1), py - y1 - t * (y2 - y1)); };
    return Math.min(pd(r.x, r.y), pd(r.x + r.w, r.y), pd(r.x, r.y + r.h), pd(r.x + r.w, r.y + r.h),
                    T.rr(r, { x: sg[0], y: sg[1], w: 0, h: 0 }), T.rr(r, { x: sg[2], y: sg[3], w: 0, h: 0 }));
  },
  /* the glyphs' ink box (canvas metrics in the label's own font), not getBBox: getBBox spans the
     font's ascent-descent, which for '*' is ~4x the glyph and would hide a star floating off its C */
  ink(t, halo) {
    const cs = getComputedStyle(t), g = (T.cv || (T.cv = document.createElement('canvas'))).getContext('2d');
    g.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`; g.textAlign = 'center'; g.textBaseline = 'alphabetic';
    const m = g.measureText(t.textContent), x = +t.getAttribute('x'), y = +t.getAttribute('y');
    return { x: x - m.actualBoundingBoxLeft - halo, y: y - m.actualBoundingBoxAscent - halo,
             w: m.actualBoundingBoxLeft + m.actualBoundingBoxRight + 2 * halo, h: m.actualBoundingBoxAscent + m.actualBoundingBoxDescent + 2 * halo };
  },
  /* every * / cis/trans / locant label (ink + 1.5 of its 2-unit halo): bonds, discs, bands, other
     labels / atom letters, its own anchor vs the others, viewBox */
  labels() {
    const s = T.svg(), v = s.viewBox.baseVal, A = T.api().atoms(), B = T.api().bonds();
    const segs = [...s.querySelectorAll('.cf-b line')].map(l => ['x1', 'y1', 'x2', 'y2'].map(k => +l.getAttribute(k)));
    const discs = [...s.querySelectorAll('circle.fcn-disc')].map(c => ({ i: +c.dataset.i, x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r') + 0.7 }));
    const bands = [...s.querySelectorAll('line.fcn-band')].map(l => ['x1', 'y1', 'x2', 'y2'].map(k => +l.getAttribute(k)));
    const box = a => { const t = s.querySelector('text.cf-a[data-i="' + a.i + '"]'); if (!t) return null; const b = t.getBBox(); return { x: b.x + 1, y: b.y + 2.5, w: b.width - 2, h: b.height - 5 }; };
    const labs = [...s.querySelectorAll('text.fcn-star, text.fcn-ct, text.fcn-loc')];
    const rects = labs.map(t => T.ink(t, 1.5)), bare = labs.map(t => T.ink(t, 0));
    return labs.map((t, n) => {
      const r = rects[n], cx = r.x + r.w / 2, cy = r.y + r.h / 2;
      const o = { txt: t.textContent, cls: t.getAttribute('class'),
        bonds: segs.filter(sg => T.segHit(sg, r)).length,
        discs: discs.filter(c => T.rr(r, { x: c.x, y: c.y, w: 0, h: 0 }) < c.r).length,
        band: bands.filter(sg => T.segDist(sg, r) < 7.5).length,
        overLab: rects.filter((q, m) => m !== n && T.rr(q, r) === 0).length,
        overAtom: A.filter(a => box(a) && T.rr(box(a), r) === 0).length,
        out: r.x < v.x - 0.5 || r.y < v.y - 0.5 || r.x + r.w > v.x + v.width + 0.5 || r.y + r.h > v.y + v.height + 0.5 };
      if (t.dataset.atom != null) {
        const a = A[+t.dataset.atom], d = discs.find(c => c.i === a.i);
        const onBand = bands.some(sg => Math.hypot(sg[0] - a.x, sg[1] - a.y) < 0.1 || Math.hypot(sg[2] - a.x, sg[3] - a.y) < 0.1);
        o.own = Math.hypot(a.x - cx, a.y - cy);
        o.other = Math.min(...A.filter(q => q.i !== a.i).map(q => Math.hypot(q.x - cx, q.y - cy)));
        /* air between the glyphs and what is drawn on the C: its disc, the band's round end, or the bare vertex */
        o.gap = T.rr(bare[n], { x: a.x, y: a.y, w: 0, h: 0 }) - Math.max(d ? d.r : 0, onBand ? 7.5 : 0);
      } else {
        const me = B.find(b => b.key === t.dataset.key), p = A[me.a], q = A[me.b];
        o.own = Math.hypot((p.x + q.x) / 2 - cx, (p.y + q.y) / 2 - cy);
        o.other = Math.min(1e9, ...A.map(a => Math.hypot(a.x - cx, a.y - cy) + 10));
        /* air between the glyphs and the edge of the highlight band (stroke 15 -> 7.5 either side) */
        o.gap = T.segDist([p.x, p.y, q.x, q.y], bare[n]) - 7.5;
      }
      return o;
    });
  },
  clipped() {
    const st = document.querySelector('.fcn-stage').getBoundingClientRect(), r = T.svg().getBoundingClientRect();
    return Math.max(st.x - r.x, r.right - st.right, st.y - r.y, r.bottom - st.bottom);
  },
  minFont() {
    const s = T.svg(), k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
    return Math.min(...[...s.querySelectorAll('text')].filter(t => getComputedStyle(t).display !== 'none')
      .map(t => parseFloat(getComputedStyle(t).fontSize) * k));
  },
  lis() { return [...document.querySelectorAll('.fcn-why li')].map(l => ({ s: l.className, t: l.innerText })); }
}; }'''


def shot(page, sel, path):
    """element screenshot via a page clip (Locator.screenshot waits for rAF, which hangs with several headless Chromes)"""
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def goto_q(page, k):
    page.select_option('.fcn-jmp', str(k))
    page.wait_for_timeout(60)


def target_for(page, ref):
    """'c2' → the C2 target; 'c2=c3' → the C2=C3 bond target"""
    A = page.evaluate('T.api().atoms()')
    by = {f"c{a['loc']}": a['i'] for a in A if a['loc'] is not None}
    T = page.evaluate('T.targets()')
    if '=' in ref:
        a, b = (by[x] for x in ref.split('='))
        key = f'{min(a, b)}-{max(a, b)}'
        return next(t for t in T if t['kind'] == 'b' and t['key'] == key)
    return next(t for t in T if t['kind'] == 'c' and t['i'] == by[ref])


def click(page, ref):
    t = target_for(page, ref)
    page.mouse.click(t['x'], t['y'])
    page.wait_for_timeout(20)


def labels_ok(page, tag):
    L = page.evaluate('T.labels()')
    check(f'{tag}: no [data-clash]', page.locator('.fcn-stage [data-clash]').count() == 0, str(page.locator('.fcn-stage [data-clash]').count()))
    bad = [(l['txt'], l['bonds']) for l in L if l['bonds']]
    check(f'{tag}: * / cis/trans / locants do not sit on a bond', not bad, str(bad))
    bad = [l['txt'] for l in L if l['discs'] or l['band']]
    check(f'{tag}: labels clear of every marking disc and C=C highlight band', not bad, str(bad))
    bad = [l['txt'] for l in L if l['overLab'] or l['overAtom']]
    check(f'{tag}: labels touch no other label / atom letters', not bad, str(bad))
    bad = [(l['txt'], round(l['own'], 1), round(l['other'], 1)) for l in L if l['own'] >= l['other']]
    check(f'{tag}: every label nearer its own C / C=C than any other atom', not bad, str(bad))
    lim = {'fcn-star': GAP_STAR, 'fcn-ct': GAP_CT, 'fcn-loc': GAP_LOC}
    bad = [(l['txt'], round(l['gap'], 1)) for l in L if l['gap'] > lim[l['cls'].split()[1]]]
    check(f'{tag}: every label hugs its anchor (ink gap <= {GAP_STAR} for *, {GAP_CT} for cis/trans, {GAP_LOC} for locants)', not bad, str(bad))
    GAPS.extend((l['cls'].split()[1], round(l['gap'], 1)) for l in L)
    bad = [l['txt'] for l in L if l['out']]
    check(f'{tag}: labels inside the viewBox', not bad, str(bad))
    return L


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s} PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        page.evaluate(HELP)
        Q = page.evaluate('T.api().Q.map(q => q.id)')

        if scheme == 'dark':
            for qid in ('pentenol', 'V', 'mecyhexol2'):
                goto_q(page, Q.index(qid))
                ch, ct, mx = WANT[qid]
                for r in ch[:1] + ct:        # one right, the rest missed, plus a wrong one
                    click(page, r)
                A = page.evaluate('T.api().atoms()')
                wrong = next(f"c{a['loc']}" for a in A if a['carbon'] and a['loc'] and f"c{a['loc']}" not in ch)
                click(page, wrong)
                page.click('.fcn-go')
                labels_ok(page, f'dark {qid}')
                shot(page, '.k', OUT / f'dark-{qid}.png')
            shot(page, '.fcn-stage', OUT / 'dark-zoom-stage-mecyhexol2.png')
            shot(page, '.fcn-fb', OUT / 'dark-zoom-fb-mecyhexol2.png')
            ctx.close()
            continue

        check('14 questions in the bank', Q == list(WANT), str(Q))
        shot(page, '.k', OUT / 'card-start.png')
        check('feedback hidden before checking', not page.is_visible('.fcn-fb'))
        T0 = page.evaluate('T.targets()')
        small = [(t['kind'], round(t['w']), round(t['h'])) for t in T0 if min(t['w'], t['h']) < (28 if t['kind'] == 'c' else 22)]
        check('click targets big enough (C ≥ 28 px across, C=C ≥ 22 px)', not small, str(small))

        for k, qid in enumerate(Q):
            ch, ct, mx = WANT[qid]
            print(f'== {qid}')
            goto_q(page, k)
            tr = page.evaluate('T.api().truth()')
            check(f'{qid}: computed answer = {ch} {ct} → {mx}', sorted(tr['chiral']) == ch and sorted(tr['ct']) == ct and tr['max'] == mx, str(tr))
            # every target hits only itself: click on, check the pick, click off
            T = page.evaluate('T.targets()')
            stray = []
            for t in T:
                page.mouse.click(t['x'], t['y'])
                pk = page.evaluate('T.api().picks()')
                want = 'c' + str(t['i']) if t['kind'] == 'c' else 'b' + t['key']
                if pk != [want]:
                    stray.append((want, pk))
                page.mouse.click(t['x'], t['y'])
                if page.evaluate('T.api().picks()'):
                    stray.append((want, 'not toggled off'))
            check(f'{qid}: every C / C=C target toggles exactly itself (real clicks)', not stray, str(stray))
            for r in ch + ct:
                click(page, r)
            page.fill('.fcn-n', str(mx))
            page.click('.fcn-go')
            sm = page.inner_text('.fcn-sum')
            check(f'{qid}: marking the answer → ✓ 全对', sm.startswith('✓ 全对'), sm)
            lis = page.evaluate('T.lis()')
            check(f'{qid}: no ✗ / 漏 lines', not [l for l in lis if l['s'] in ('bad', 'miss')], str(lis))
            check(f'{qid}: one ✓ line per answer item', len([l for l in lis if l['s'] == 'ok']) == len(ch) + len(ct), str(lis))
            check(f'{qid}: stars / cis-trans drawn green', page.locator('.fcn-stage text.fcn-star.ok').count() == len(ch)
                  and page.locator('.fcn-stage text.fcn-ct.ok').count() == len(ct))
            cnt = page.inner_text('.fcn-count')
            sup = '2' + f'{len(ch)}+{len(ct)}'.translate(SUPS)
            check(f'{qid}: count n = {len(ch)}, m = {len(ct)}, {sup} = {mx}',
                  f'n = {len(ch)}' in cnt and f'm = {len(ct)}' in cnt and sup in cnt and page.inner_text('.fcn-max') == str(mx), cnt)
            check(f'{qid}: typed {mx} → green', 'good' in page.get_attribute('.fcn-n', 'class') and '✓' in page.inner_text('.fcn-nfb'))
            labels_ok(page, qid)
            cl = page.evaluate('T.clipped()')
            check(f'{qid}: structure not clipped by the stage', cl <= 0.5, f'{cl:.1f}px')
            if qid in ('pentenol', 'mecyhexol2', 'V', 'butenedioic', 'malic'):
                shot(page, '.k', OUT / f'card-{qid}.png')
            if qid in ('pentenol', 'V'):
                shot(page, '.fcn-stage', OUT / f'zoom-stage-{qid}.png')
        check('score counts every solved question', page.inner_text('.fcn-sc') == str(len(Q)), page.inner_text('.fcn-sc'))
        check('solved questions get ✓ in the select', all(o.startswith('✓') for o in page.eval_on_selector_all('.fcn-jmp option', 'os => os.map(o => o.textContent)')))

        print('== wrong / missed marks and their reasons')

        def run(qid, refs, n=''):
            goto_q(page, Q.index(qid))
            for r in refs:
                click(page, r)
            page.fill('.fcn-n', n)
            page.click('.fcn-go')
            return page.evaluate('T.lis()')

        def line(lis, s, frag):
            return next((l['t'] for l in lis if l['s'] == s and frag in l['t']), None)

        lis = run('butan2ol', ['c3'])
        check('butan-2-ol C3 marked → ✗ 连着 2 个 H', line(lis, 'bad', 'C3：连着 2 个 H') is not None, str(lis))
        check('butan-2-ol C2 left → 漏, lists its 4 groups', line(lis, 'miss', 'C2：连着 4 个不同的 group：–H、–OH、–CH₃、–CH₂CH₃') is not None, str(lis))
        check('summary counts 0 / 1 / 1', page.inner_text('.fcn-sum') == '对 0 个，漏标 1 个，标错 1 个。', page.inner_text('.fcn-sum'))
        check('wrong star red, missed star yellow', page.locator('.fcn-stage text.fcn-star.bad').count() == 1 and page.locator('.fcn-stage text.fcn-star.miss').count() == 1)
        check('disc colours: bad + miss', page.locator('.fcn-stage circle.fcn-disc.bad').count() == 1 and page.locator('.fcn-stage circle.fcn-disc.miss').count() == 1)
        check('locants C2, C3 shown after checking', sorted(page.eval_on_selector_all('.fcn-stage text.fcn-loc', 'ts => ts.map(t => t.textContent)')) == ['C2', 'C3'])
        labels_ok(page, 'butan-2-ol wrong')
        shot(page, '.k', OUT / 'card-wrong-butan2ol.png')
        shot(page, '.fcn-stage', OUT / 'zoom-stage-wrong-butan2ol.png')
        shot(page, '.fcn-fb', OUT / 'zoom-fb-wrong-butan2ol.png')
        check('score unchanged by a wrong answer', page.inner_text('.fcn-sc') == str(len(Q)))

        lis = run('mecyhexol1', ['c1'])
        check('1-methylcyclohexan-1-ol C1 → ✗ ring 两边一样', line(lis, 'bad', '沿 ring 顺时针、逆时针各走一圈，两边完全一样') is not None, str(lis))
        lis = run('mecyhexol1', [])
        check('unmarked decoy C1 still explained (不标)', line(lis, 'none', 'C1：沿 ring') is not None, str(lis))
        check('…and the summary says 全对', page.inner_text('.fcn-sum').startswith('✓ 全对'), page.inner_text('.fcn-sum'))
        lis = run('X', ['c2'])
        check('X C2 → ✗ two identical –CH₂OH', line(lis, 'bad', '有两个相同的 group（–CH₂OH 和 –CH₂OH）') is not None, str(lis))
        lis = run('lactic', ['c1', 'c2'])
        check('C=O carbon → ✗ sp², 3 groups', line(lis, 'bad', 'C1：在 C=O 上（sp²），只连 3 个 group') is not None, str(lis))
        lis = run('mb2ene', ['c2=c3'])
        check('2-methylbut-2-ene C2=C3 → ✗ C2 上两个都是 –CH₃', line(lis, 'bad', 'C2 上两个都是 –CH₃') is not None, str(lis))
        check('wrong cis/trans label red', page.locator('.fcn-stage text.fcn-ct.bad').count() == 1)
        lis = run('but1ene', [])
        check('but-1-ene unmarked C=C explained: C1 上两个都是 –H', line(lis, 'none', 'C1 上两个都是 –H') is not None, str(lis))
        lis = run('mp2ene', [])
        check('3-methylpent-2-ene missed C=C → 漏, both ends compared',
              line(lis, 'miss', 'C2 上 –H 与 –CH₃ 不同，C3 上 –CH₃ 与 –CH₂CH₃ 不同') is not None, str(lis))
        check('missed cis/trans label yellow', page.locator('.fcn-stage text.fcn-ct.miss').count() == 1)
        lis = run('V', ['c3', 'c1'])
        check('V: C2 (no H) missed → its 4 groups', line(lis, 'miss', 'C2：连着 4 个不同的 group：–OH、–CH₃、–CH₂OH、–CH(OH)CH₂OH') is not None, str(lis))
        check('V: C1 → ✗ 2 H', line(lis, 'bad', 'C1：连着 2 个 H') is not None, str(lis))
        check('V note: no H on C2 still chiral', '一个 H 都没有' in page.inner_text('.fcn-note'))
        lis = run('mecyhexol2', ['c1'])
        check('2-methylcyclohexan-1-ol: C2 missed, ring sides named', line(lis, 'miss', 'ring 经 C1 的一边') is not None and line(lis, 'miss', 'ring 经 C3 的一边') is not None, str(lis))
        run('mecyhexol2', [])
        page.click('.fcn-reset')
        A = page.evaluate('T.api().atoms()')
        me = next(a for a in A if a['carbon'] and a['loc'] is None)
        t = next(t for t in page.evaluate('T.targets()') if t['kind'] == 'c' and t['i'] == me['i'])
        page.mouse.click(t['x'], t['y']); page.click('.fcn-go')
        lis = page.evaluate('T.lis()')
        check('branch CH₃ named by its chain carbon: C2 上 –CH₃ 的 C', line(lis, 'bad', 'C2 上 –CH₃ 的 C：连着 3 个 H') is not None, str(lis))

        print('== count box')
        run('pentenol', ['c2', 'c3=c4'], '2')
        check('pentenol: 2 → ✗ and the 2¹⁺¹ = 4 hint', 'badv' in page.get_attribute('.fcn-n', 'class') and '2¹⁺¹ = 4' in page.inner_text('.fcn-nfb'), page.inner_text('.fcn-nfb'))
        run('pentenol', ['c2', 'c3=c4'], 'four')
        check('non-number → ✗ 填一个整数', '整数' in page.inner_text('.fcn-nfb'))
        run('mecyhexol1', [], '1')
        check('1-methylcyclohexan-1-ol: 1 → ✓ (2⁰⁺⁰ = 1)', 'good' in page.get_attribute('.fcn-n', 'class') and '没有 stereoisomerism' in page.inner_text('.fcn-count'))
        goto_q(page, Q.index('malic'))
        click(page, 'c2'); page.fill('.fcn-n', '2'); page.press('.fcn-n', 'Enter')
        check('Enter in the count box checks', page.is_visible('.fcn-fb') and page.inner_text('.fcn-sum').startswith('✓'))
        click(page, 'c3')
        check('a new click after checking clears the result', not page.is_visible('.fcn-fb') and page.locator('.fcn-stage text.fcn-star.sel').count() == 2)

        print('== keyboard, reveal, reset, nav')
        goto_q(page, Q.index('butan2ol'))
        page.focus('.fcn-stage .fcn-t')
        page.keyboard.press('Enter')
        check('Enter on a focused C marks it', len(page.evaluate('T.api().picks()')) == 1)
        page.keyboard.press(' ')
        check('Space toggles it off', not page.evaluate('T.api().picks()'))
        goto_q(page, Q.index('V'))
        page.click('.fcn-show')
        check('显示答案 marks C2 and C3', sorted(page.evaluate('T.api().picks()')) == sorted(['c' + str(a['i']) for a in page.evaluate('T.api().atoms()') if a['loc'] in (2, 3)]))
        check('显示答案 summary', '答案已标在图上' in page.inner_text('.fcn-sum'))
        check('显示答案 lines tagged 答案', len([l for l in page.evaluate('T.lis()') if l['s'] == 'ans']) == 2)
        labels_ok(page, 'V reveal')
        shot(page, '.k', OUT / 'card-reveal-V.png')
        page.click('.fcn-reset')
        check('重来 clears everything', not page.evaluate('T.api().picks()') and not page.is_visible('.fcn-fb') and page.locator('.fcn-stage text').count() == page.locator('.fcn-stage text.cf-a').count())
        goto_q(page, 0)
        check('prev disabled on first', page.is_disabled('.fcn-prev'))
        page.click('.fcn-next')
        check('next → question 2', page.evaluate('T.api().cur()') == 1)
        goto_q(page, len(Q) - 1)
        check('next disabled on last', page.is_disabled('.fcn-next'))
        check('X cites 9701/23 May/June 2026 Q4(c)', '9701/23 May/June 2026 Q4(c)' in page.inner_text('.fcn-src'), page.inner_text('.fcn-src'))
        check('no console error so far', not errors, '; '.join(errors))

        print('== narrow (720 px)')
        page.set_viewport_size({'width': 720, 'height': 1200}); page.wait_for_timeout(200)
        for k, qid in enumerate(Q):
            goto_q(page, k)
            ch, ct, mx = WANT[qid]
            A = page.evaluate('T.api().atoms()')
            wrong = [f"c{a['loc']}" for a in A if a['carbon'] and a['loc'] and f"c{a['loc']}" not in ch][:1]
            for r in ch[1:] + ct + wrong:     # a busy state: one missed (if any), the rest, one wrong
                click(page, r)
            page.click('.fcn-go')
            ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
            fs = page.evaluate('T.minFont()')
            cl = page.evaluate('T.clipped()')
            ok = ov <= 0 and fs >= 12 and cl <= 0.5 and page.locator('[data-clash]').count() == 0
            check(f'720 px {qid}: no overflow, structure text ≥ 12 px, not clipped, no clash', ok,
                  f'overflow {ov}, font {fs:.2f}, clipped {cl:.1f}, clash {page.locator("[data-clash]").count()}')
            if qid in ('V', 'X', 'pentenol', 'mecyhexol2'):
                labels_ok(page, f'720 {qid}')
                shot(page, '.k', OUT / f'card-720-{qid}.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
for c in ('fcn-star', 'fcn-ct', 'fcn-loc'):
    g = sorted(x for k, x in GAPS if k == c)
    if g:
        print(f'gap {c}: min {g[0]} median {g[len(g) // 2]} max {g[-1]}')
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
