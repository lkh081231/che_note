"""ch03 bond-energy cell test: two tabs —
① bond energy vs bond length scatter (15 bonds from chapter 3.4 F, family buttons + explanation cards,
   F–F anomaly ring, hover / click readout), ② qualitative potential energy curve with a distance slider.

usage: uv run --with playwright python -I colab/tests/ch03_bond-energy.py <preview.html> <shots-dir>
(build the preview first: COLAB_TMP=/mnt/ai-shared/che_tmp/ch03 python3 tools/build_colab.py ch03 --cell bond-energy)
note: never name a shot con.png / aux.png / nul.png — reserved file names on the NTFS share.
"""
import math
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []

# chapter 3.4 F table (bond energy kJ mol⁻¹ data booklet, bond length nm textbook) + F–F from rule 3
BONDS = {
    'C–C': (350, 0.154, 'cc'), 'C=C': (610, 0.134, 'cc'), 'C≡C': (840, 0.120, 'cc'),
    'H–F': (562, 0.092, 'hx'), 'H–Cl': (431, 0.127, 'hx'), 'H–Br': (366, 0.141, 'hx'), 'H–I': (299, 0.161, 'hx'),
    'F–F': (158, 0.142, 'hal'), 'Cl–Cl': (242, 0.199, 'hal'), 'Br–Br': (193, 0.228, 'hal'), 'I–I': (151, 0.267, 'hal'),
    'N≡N': (944, 0.110, 'nn'), 'O=O': (496, 0.121, 'nn'), 'C–H': (410, 0.109, 'none'), 'O–H': (460, 0.096, 'none'),
}
KEYS = {
    'all': ['multiple bond 更短、更强', 'atom 越大，bond 越长、越弱', 'F–F 是例外', '158 < 242'],
    'cc': ['multiple bond 更短、更强', 'C–C 350 kJ mol⁻¹ / 0.154 nm → C=C 610 / 0.134 → C≡C 840 / 0.120',
           'C=C 610 < 2 × 350 = 700', 'π bond 比 σ bond 弱'],
    'hx': ['atom 越大，bond 越长、越弱', 'H–F 562 > H–Cl 431 > H–Br 366 > H–I 299', 'HF > HCl > HBr > HI', 'hot glass rod'],
    'hal': ['Cl–Cl 242 > Br–Br 193 > I–I 151', 'F–F 反常地弱（158 < 242）', 'F–F 太短', '3 对 lone pairs', 'repulsion',
            'H 上没有 lone pair'],
    'nn': ['N≡N 944', 'O=O 496', 'N₂ 很不活泼', 'strong triple (covalent) bond AND non-polar', '9701/23 May/June 2024 Q1(a)(i)'],
}
MA = 2.2


def V(r):
    e = math.exp(-MA * (r - 1))
    return (1 - e) ** 2 - 1


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


SMALL_JS = """() => {
  const out = [];
  for (const e of document.querySelectorAll('.k *')) {
    if (e.closest('svg')) continue;
    const st = getComputedStyle(e);
    if (st.display === 'none' || st.visibility === 'hidden' || (!e.offsetParent && e.tagName !== 'DIV')) continue;
    if (e.classList.contains('tip') && !e.classList.contains('show')) continue;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own && parseFloat(st.fontSize) < 12 - 1e-3)
      out.push(e.tagName + '.' + e.className + ':' + parseFloat(st.fontSize) + 'px:' + e.textContent.trim().slice(0, 20));
  }
  for (const svg of document.querySelectorAll('.k svg')) {
    if (!svg.getBoundingClientRect().width) continue;
    const vb = (svg.getAttribute('viewBox') || '').trim().split(/\\s+/).map(Number);
    const scale = vb[2] ? svg.getBoundingClientRect().width / vb[2] : 1;
    for (const t of svg.querySelectorAll('text')) {
      if (!t.textContent.trim()) continue;
      const px = parseFloat(getComputedStyle(t).fontSize) * scale;
      const h = t.getBoundingClientRect().height;
      if (px < 12 - 1e-3 || h < 12) out.push('SVG:' + t.textContent.trim().slice(0, 20) + ':' + px.toFixed(2) + 'px h' + h.toFixed(1));
    }
  }
  return out;
}"""

# rendered boxes: every text vs every other text, vs every mark (points, ring, dot, atoms), and inside the svg
AUDIT_JS = """(sel) => {
  const svg = document.querySelector(sel);
  const R = e => e.getBoundingClientRect();
  const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
  const labs = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim());
  const marks = [...svg.querySelectorAll('.be-pt, .be-ring, .be-dot, .be-atom, .be-nuc')];
  const out = [];
  for (let i = 0; i < labs.length; i++) for (let j = i + 1; j < labs.length; j++)
    if (hit(R(labs[i]), R(labs[j]))) out.push(labs[i].textContent + ' <-> ' + labs[j].textContent);
  for (const t of labs) for (const m of marks) if (hit(R(t), R(m))) { out.push('on mark: ' + t.textContent + ' / ' + (m.dataset.b || m.getAttribute('class'))); break; }
  const vb = R(svg);
  for (const t of labs) { const r = R(t); if (r.left < vb.left - 0.5 || r.right > vb.right + 0.5 || r.top < vb.top - 0.5 || r.bottom > vb.bottom + 0.5) out.push('outside svg: ' + t.textContent); }
  return out;
}"""

# label ambiguity: distance from label box to its own point vs to the nearest other point (viewBox px)
NEAR_JS = """() => { const pts = [...document.querySelectorAll('.be-ssvg .be-pt')].map(c => [c.dataset.b, +c.getAttribute('cx'), +c.getAttribute('cy')]);
  const out = [];
  for (const t of document.querySelectorAll('.be-ssvg text.be-plab')) {
    const b = t.getBBox(), d = p => Math.hypot(Math.max(b.x - p[1], 0, p[1] - b.x - b.width), Math.max(b.y - p[2], 0, p[2] - b.y - b.height));
    const own = d(pts.find(p => p[0] === t.dataset.b));
    for (const p of pts) if (p[0] !== t.dataset.b && d(p) < own + 6) out.push(t.dataset.b + ' near ' + p[0] + ' (' + own.toFixed(1) + ' vs ' + d(p).toFixed(1) + ')');
  }
  return out; }"""
PTS_JS = """() => [...document.querySelectorAll('.be-ssvg .be-pt')].map(c => ({b: c.dataset.b, e: +c.dataset.e, l: +c.dataset.l,
  f: c.dataset.fam, x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), dim: c.classList.contains('be-dim'), sel: c.classList.contains('sel')}))"""
PE_JS = """() => { const s = document.querySelector('.be-psvg'), d = s.querySelector('.be-dot'), at = [...s.querySelectorAll('.be-atom')];
  return { r: +s.dataset.r, force: s.dataset.force, geo: s.dataset.geo.split(',').map(Number), dx: +d.getAttribute('cx'), dy: +d.getAttribute('cy'),
    sep: +at[1].getAttribute('cx') - +at[0].getAttribute('cx'), state: document.querySelector('.be-state').dataset.state,
    head: document.querySelector('.be-state .be-sh').textContent, body: document.querySelector('.be-state').textContent,
    rv: document.querySelector('.be-rv').textContent, arrows: s.querySelectorAll('.be-farrow').length,
    flab: (s.querySelector('.be-flab') || {}).textContent,
    ax: [...s.querySelectorAll('.be-farrow')].map(l => [+l.getAttribute('x1'), +l.getAttribute('x2')]),
    acx: at.map(a => +a.getAttribute('cx')) }; }"""


def hover(page, b, click=False):
    box = page.locator(f'.be-ssvg .be-pt[data-b="{b}"]').bounding_box()
    x, y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    page.mouse.move(x - 25, y + 25); page.mouse.move(x, y)
    if click:
        page.mouse.click(x, y)
    page.wait_for_timeout(40)


def set_r(page, v):
    page.evaluate("(v) => { const s = document.querySelector('.be-r'); s.value = v; s.dispatchEvent(new Event('input', {bubbles: true})); }", str(v))
    page.wait_for_timeout(60)


def tab(page, t):
    page.click(f'.tabbar button[data-tab="{t}"]'); page.wait_for_timeout(150)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(500)
        sfx = '' if scheme == 'light' else '-dark'
        L = scheme == 'light'

        def shot(name, sel='.k'):
            if sel == '.k' and 'hover' not in name:
                page.mouse.move(2, 2); page.wait_for_timeout(30)
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        def clip(name, sel, x0, y0, x1, y1):
            """close-up of a region of an svg, given in viewBox units"""
            box = page.locator(sel).bounding_box()
            vbw = page.evaluate(f"document.querySelector('{sel}').viewBox.baseVal.width")
            k = box['width'] / vbw
            page.mouse.move(2, 2); page.wait_for_timeout(30)
            page.screenshot(path=str(OUT / f'{name}{sfx}.png'),
                            clip={'x': box['x'] + x0 * k, 'y': box['y'] + y0 * k, 'width': (x1 - x0) * k, 'height': (y1 - y0) * k})

        def clean(sel, what):
            if sel == '.be-ssvg':
                amb = page.evaluate(NEAR_JS)
                check(f'{scheme} {what}: every bond label clearly nearer its own point than any other point (>= 6 px margin)', not amb, str(amb[:4]))
            a = page.evaluate(AUDIT_JS, sel); c = page.locator('[data-clash]').count()
            check(f'{scheme} {what}: [data-clash] = 0, no rendered overlaps', c == 0 and not a,
                  f'clash {c} {page.evaluate("[...document.querySelectorAll(`[data-clash]`)].map(t => t.textContent)")}; {a[:4]}')

        # ================= ① scatter
        print(f'== {scheme}: ① bond energy vs bond length')
        check('default tab = scatter', 'on' in page.get_attribute('.tabbar button[data-tab="plot"]', 'class'))
        check('default family = 全部', 'on' in page.get_attribute('.be-fam[data-fam="all"]', 'class'))
        pts = page.evaluate(PTS_JS)
        got = {q['b']: (q['e'], q['l'], q['f']) for q in pts}
        check('15 points: bond energy / bond length / family match the chapter table', len(pts) == 15 and got == BONDS,
              str({k: v for k, v in got.items() if BONDS.get(k) != v}))
        Lx, Rx, Ty, By = page.evaluate("document.querySelector('.be-ssvg').dataset.geo.split(',').map(Number)")
        pos_ok = all(abs(q['x'] - (Lx + (q['l'] - 0.08) / 0.2 * (Rx - Lx))) < 0.6 and abs(q['y'] - (By - q['e'] / 1000 * (By - Ty))) < 0.6 for q in pts)
        check('points sit at (bond length, bond energy) on the axes', pos_ok)
        ticks = page.evaluate("[...document.querySelectorAll('.be-ssvg text.be-tick')].map(t => t.textContent)")
        check('axes: y 0 … 1000 step 200, x 0.08 … 0.28 nm step 0.02',
              ticks == [str(v) for v in range(0, 1001, 200)] + [f'{0.08 + i * 0.02:.2f}' for i in range(11)], str(ticks))
        axt = page.evaluate("[...document.querySelectorAll('.be-ssvg text.be-axt')].map(t => t.textContent)")
        check('axis titles with units', axt == ['bond energy / kJ mol⁻¹', 'bond length / nm'], str(axt))
        plabs = page.evaluate("[...document.querySelectorAll('.be-ssvg text.be-plab')].map(t => [t.dataset.b, t.textContent])")
        check('15 point labels, each = its bond name', sorted(plabs) == sorted([k, k] for k in BONDS), str(plabs))
        lines = page.evaluate("[...document.querySelectorAll('.be-ssvg .be-line')].map(l => [l.dataset.fam, l.getAttribute('points').split(' ').length])")
        check('one connecting line per family (cc 3, hx 4, hal 4, nn 2 points)', sorted(lines) == sorted([['cc', 3], ['hx', 4], ['hal', 4], ['nn', 2]]), str(lines))
        cols = page.evaluate("""() => { const o = {}; for (const c of document.querySelectorAll('.be-ssvg .be-pt')) { (o[c.dataset.fam] = o[c.dataset.fam] || new Set()).add(getComputedStyle(c).fill); }
            return Object.fromEntries(Object.entries(o).map(([k, v]) => [k, [...v]])); }""")
        check('one colour per family, families differ', all(len(v) == 1 for v in cols.values()) and len({v[0] for v in cols.values()}) == 5, str(cols))
        # F–F anomaly
        ring = page.evaluate("""() => { const r = document.querySelector('.be-ssvg .be-ring'); if (!r) return null; const st = getComputedStyle(r);
            const p = document.querySelector('.be-ssvg .be-pt[data-b="F–F"]');
            const bad = getComputedStyle(document.querySelector('.k')).getPropertyValue('--bad').trim();
            const tmp = document.createElement('i'); tmp.style.color = bad; document.body.appendChild(tmp); const badRgb = getComputedStyle(tmp).color; tmp.remove();
            return [+r.getAttribute('cx') - +p.getAttribute('cx'), +r.getAttribute('cy') - +p.getAttribute('cy'), st.fill, st.stroke, badRgb, +r.getAttribute('r')]; }""")
        check('F–F anomaly: hollow red ring centred on F–F', ring and ring[0] == 0 and ring[1] == 0 and ring[2] == 'none' and ring[3] == ring[4] and ring[5] > 5.5, str(ring))
        an = page.evaluate("[...document.querySelectorAll('.be-ssvg text.be-anom')].map(t => [t.textContent, t.dataset.b])")
        check('F–F anomaly: label «anomaly»', an == [['anomaly', 'F–F']], str(an))
        d_an = page.evaluate("""() => { const t = document.querySelector('.be-ssvg text.be-anom').getBBox(), p = document.querySelector('.be-ssvg .be-pt[data-b="F–F"]');
            const cx = +p.getAttribute('cx'), cy = +p.getAttribute('cy');
            const dx = Math.max(t.x - cx, 0, cx - t.x - t.width), dy = Math.max(t.y - cy, 0, cy - t.y - t.height); return Math.hypot(dx, dy); }""")
        check('«anomaly» label sits next to the F–F point (< 30 viewBox px)', d_an < 30, str(d_an))
        dl = page.evaluate("""() => [...document.querySelectorAll('.be-ssvg text.be-plab')].map(t => { const b = t.getBBox(), p = document.querySelector('.be-ssvg .be-pt[data-b="' + t.dataset.b + '"]');
            const cx = +p.getAttribute('cx'), cy = +p.getAttribute('cy'); return [t.dataset.b, Math.hypot(Math.max(b.x - cx, 0, cx - b.x - b.width), Math.max(b.y - cy, 0, cy - b.y - b.height))]; })""")
        far = [x for x in dl if x[1] > 30]
        check('every bond label within 30 viewBox px of its point', not far, str(far))
        check('foot note: bond energy data booklet, bond length textbook', page.inner_text('.be-foot').strip() == 'bond energy：data booklet；bond length：教科书值')
        exp = page.inner_text('.be-exp')
        miss = [k for k in KEYS['all'] if k not in exp]
        check('全部: overview card has the three rules', not miss and page.get_attribute('.be-exp', 'data-fam') == 'all', str(miss))
        check('全部: nothing dimmed', not any(q['dim'] for q in pts))
        check('readout hint before any hover', '悬停 / 点一个点' in page.inner_text('.be-read'))
        clean('.be-ssvg', 'scatter 全部')
        shot('plot-all')
        if L:
            clip('zoom-plot-shortbonds', '.be-ssvg', 40, 40, 440, 300)
            clip('zoom-plot-ff', '.be-ssvg', 40, 300, 560, 540)
        else:
            clip('zoom-plot-shortbonds', '.be-ssvg', 40, 40, 440, 300)

        # hover every point → readout values
        bad = []
        for name, (e, l, f) in BONDS.items():
            hover(page, name)
            r = page.evaluate("[document.querySelector('.be-read').dataset.b, (document.querySelector('.be-rE') || {}).textContent, (document.querySelector('.be-rl') || {}).textContent, document.querySelector('.be-read').textContent]")
            if r[0] != name or r[1] != str(e) or r[2] != f'{l:.3f}':
                bad.append((name, r))
        check('hover each of 15 points: readout shows its bond energy and bond length', not bad, str(bad[:3]))
        hover(page, 'C=C')
        if L:
            shot('hover-CC-double')
        hover(page, 'F–F', click=True)
        page.mouse.move(2, 2); page.wait_for_timeout(50)
        sel = [q['b'] for q in page.evaluate(PTS_JS) if q['sel']]
        rd = page.inner_text('.be-read')
        check('click F–F: pinned (selected ring) and readout stays after mouse leaves', sel == ['F–F'] and '158' in rd and '0.142' in rd and 'halogens' in rd, f'{sel} {rd}')
        hover(page, 'O–H')
        check('O–H readout says it is in no family', '不属于上面的 family' in page.inner_text('.be-read'))
        page.mouse.move(2, 2); page.wait_for_timeout(40)

        # families
        for f in ('cc', 'hx', 'hal', 'nn', 'all'):
            page.click(f'.be-fam[data-fam="{f}"]'); page.wait_for_timeout(120)
            pts = page.evaluate(PTS_JS)
            on = [q['b'] for q in pts if not q['dim']]
            want = [k for k, v in BONDS.items() if f == 'all' or v[2] == f]
            check(f'{f}: only its bonds highlighted, the rest dimmed', sorted(on) == sorted(want), str(on))
            pressed = page.evaluate("[...document.querySelectorAll('.be-fam')].filter(b => b.classList.contains('on')).map(b => [b.dataset.fam, b.getAttribute('aria-pressed')])")
            check(f'{f}: button pressed', pressed == [[f, 'true']], str(pressed))
            dimlab = page.evaluate("[...document.querySelectorAll('.be-ssvg text.be-plab')].filter(t => !t.classList.contains('be-dim')).map(t => t.dataset.b)")
            check(f'{f}: labels dimmed with their points', sorted(dimlab) == sorted(want), str(dimlab))
            exp = page.inner_text('.be-exp')
            miss = [k for k in KEYS[f] if k not in exp]
            check(f'{f}: explanation card key sentences', not miss and page.get_attribute('.be-exp', 'data-fam') == f, str(miss))
            nref = page.locator('.be-ssvg .be-ref').count()
            if f == 'cc':
                y700 = page.evaluate("+document.querySelector('.be-ssvg .be-ref').getAttribute('y1')")
                check('cc: dashed 2 × C–C = 700 reference line at 700 kJ mol⁻¹', nref == 1 and abs(y700 - (By - 0.7 * (By - Ty))) < 0.6 and
                      page.text_content('.be-ssvg .be-reflab') == '2 × C–C = 700')
                c2 = [q for q in pts if q['b'] == 'C=C'][0]
                check('cc: C=C point lies below the 700 line', c2['y'] > y700)
            else:
                check(f'{f}: no 700 reference line', nref == 0 and page.locator('.be-ssvg .be-reflab').count() == 0)
            ring_n = page.locator('.be-ssvg .be-ring').count()
            check(f'{f}: F–F anomaly ring shown only for 全部 / halogens', ring_n == (1 if f in ('all', 'hal') else 0), str(ring_n))
            clean('.be-ssvg', f'scatter {f}')
            if f != 'all':
                shot(f'plot-{f}')
            if f == 'hal':
                clip('zoom-plot-hal-ff', '.be-ssvg', 40, 300, 560, 540)
            if f == 'cc' and L:
                clip('zoom-plot-cc', '.be-ssvg', 40, 40, 500, 400)
        check(f'{scheme} 1000px scatter: fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))

        # ================= ② potential energy curve
        print(f'== {scheme}: ② potential energy curve')
        tab(page, 'pe')
        s = page.evaluate(PE_JS)
        Lp, Rp, Tp, Bp, X1, Ymin, Y0 = s['geo']
        check('slider default = 1.00 × bond length', s['r'] == 1 and s['rv'] == '= 1.00 × bond length', str(s['r']) + s['rv'])
        check('r = 1: state «最低点 = bond length», forces balanced', s['state'] == 'bond-length' and s['head'] == '最低点 = bond length' and
              s['force'] == 'balanced' and s['arrows'] == 0 and s['flab'] == 'attraction = repulsion', str(s))
        check('r = 1: card names bond length and bond energy (well depth)', 'bond length' in s['body'] and '阱深就是 bond energy' in s['body'], s['body'])
        check('r = 1: dot at the minimum of the curve', abs(s['dx'] - X1) < 0.6 and abs(s['dy'] - Ymin) < 0.6, f"{s['dx']},{s['dy']} vs {X1},{Ymin}")
        # the minimum really is at r = 1: sample the polyline
        mn = page.evaluate("() => { const p = document.querySelector('.be-psvg .be-curve').getAttribute('points').split(' ').map(q => q.split(',').map(Number)); let b = p[0]; for (const q of p) if (q[1] > b[1]) b = q; return b; }")
        check('curve minimum is at the bond-length mark', abs(mn[0] - X1) < 3 and abs(mn[1] - Ymin) < 1, f'{mn} vs {X1},{Ymin}')
        bl = page.evaluate("() => { const l = document.querySelector('.be-psvg .be-blen'), t = document.querySelector('.be-psvg .be-blab'); return [+l.getAttribute('x1'), t.textContent, +t.getAttribute('x')]; }")
        check('«bond length» marked under the minimum', abs(bl[0] - X1) < 0.6 and bl[1] == 'bond length' and abs(bl[2] - X1) < 0.6, str(bl))
        dep = page.evaluate("() => { const l = document.querySelector('.be-psvg .be-depth'); return [+l.getAttribute('y1'), +l.getAttribute('y2'), document.querySelector('.be-psvg .be-elab').textContent]; }")
        check('«bond energy» = double arrow from the minimum up to 0', abs(dep[0] - 8 - Y0) < 0.6 and abs(dep[1] + 8 - Ymin) < 0.6 and dep[2] == 'bond energy', str(dep))
        zl = page.evaluate("[...document.querySelectorAll('.be-psvg text')].map(t => t.textContent)")
        need = ['potential energy', 'internuclear distance', 'bond length', 'bond energy', 'strong repulsion', 'weak attraction', '0 = atoms far apart', 'atom A', 'atom B']
        check('curve labels present', all(n in zl for n in need), str(zl))
        check('r = 1: atoms 72 px apart (1 bond length)', abs(s['sep'] - 72) < 0.6, str(s['sep']))
        clean('.be-psvg', 'curve r=1.00')
        shot('pe-r100')
        if L:
            clip('zoom-pe-well', '.be-psvg', 0, 150, 560, 470)
        clip('zoom-pe-atoms-r100', '.be-psvg', 200, 0, 800, 160)

        # a real drag of the slider thumb to the left end
        sb = page.locator('.be-r').bounding_box()
        page.mouse.move(sb['x'] + sb['width'] * (0.4 / 2.6), sb['y'] + sb['height'] / 2)
        page.mouse.down(); page.mouse.move(sb['x'] - 40, sb['y'] + sb['height'] / 2, steps=6); page.mouse.up()
        page.wait_for_timeout(80)
        s = page.evaluate(PE_JS)
        check('drag slider to the left end → r = 0.60', s['r'] == 0.6 and s['rv'] == '= 0.60 × bond length', str(s['r']))
        check('r = 0.60: state repulsion («太近：repulsion 急升»)', s['state'] == 'repulsion' and s['head'] == '太近：repulsion 急升' and
              'repulsion 急剧增大' in s['body'], s['head'])
        check('r = 0.60: net repulsion, arrows point outwards', s['force'] == 'repulsion' and s['arrows'] == 2 and s['flab'] == 'net repulsion' and
              s['ax'][0][1] < s['ax'][0][0] and s['ax'][1][1] > s['ax'][1][0], str(s['ax']))
        check('r = 0.60: dot above the 0 line (energy rose steeply)', s['dy'] < Y0 - 40, f"{s['dy']} vs {Y0}")
        check('r = 0.60: atoms overlap heavily (43 px apart)', abs(s['sep'] - 43.2) < 0.6, str(s['sep']))
        kY = (Bp - Tp) / 2.75
        check('r = 0.60: dot on the curve', abs(s['dy'] - (Y0 - V(0.6) * kY)) < 0.8, f"{s['dy']}")
        clean('.be-psvg', 'curve r=0.60')
        shot('pe-r060')
        clip('zoom-pe-atoms-r060', '.be-psvg', 200, 0, 800, 160)
        if L:
            clip('zoom-pe-rep', '.be-psvg', 0, 150, 560, 470)

        set_r(page, 1.5)
        s = page.evaluate(PE_JS)
        check('r = 1.50: state attraction, arrows point inwards', s['state'] == 'attraction' and s['force'] == 'attraction' and s['flab'] == 'net attraction' and
              s['ax'][0][1] > s['ax'][0][0] and s['ax'][1][1] < s['ax'][1][0], str(s))
        clean('.be-psvg', 'curve r=1.50')
        if L:
            shot('pe-r150')

        page.focus('.be-r'); page.keyboard.press('End'); page.wait_for_timeout(80)
        s = page.evaluate(PE_JS)
        check('End key → r = 3.20', s['r'] == 3.2 and s['rv'] == '= 3.20 × bond length', str(s['r']))
        check('r = 3.20: state weak attraction («太远：attraction 很弱»)', s['state'] == 'weak' and s['head'] == '太远：attraction 很弱' and
              'potential energy 接近 0' in s['body'], s['head'])
        check('r = 3.20: dot just below the 0 line', 0 < s['dy'] - Y0 < 6, f"{s['dy']} vs {Y0}")
        check('r = 3.20: atoms well apart', s['sep'] > 2 * 40 + 100, str(s['sep']))
        check('r = 3.20: short inward arrows, «net attraction（very weak）»', s['force'] == 'attraction' and s['arrows'] == 2 and
              s['flab'] == 'net attraction（very weak）' and s['ax'][0][1] > s['ax'][0][0], str(s))
        page.evaluate("document.activeElement.blur()")
        clean('.be-psvg', 'curve r=3.20')
        shot('pe-r320')
        clip('zoom-pe-atoms-r320', '.be-psvg', 200, 0, 800, 160)
        if L:
            clip('zoom-pe-tail', '.be-psvg', 400, 150, 1000, 470)
        # sweep: no clash anywhere along the slider
        sweep = []
        for i in range(0, 27):
            v = round(0.6 + i * 0.1, 2)
            set_r(page, v)
            st = page.evaluate(PE_JS)['state']
            a = page.evaluate(AUDIT_JS, '.be-psvg'); c = page.locator('[data-clash]').count()
            if a or c:
                sweep.append((v, c, a[:2]))
            want = 'repulsion' if v < 0.95 else 'bond-length' if v <= 1.05 else 'attraction' if v <= 2 else 'weak'
            f = page.evaluate(PE_JS)['force']
            if st != want or (f == 'balanced') != (want == 'bond-length'):
                sweep.append((v, 'state', st, f))
        check(f'{scheme} sweep r = 0.6 … 3.2: no clash / overlap, states in order', not sweep, str(sweep[:4]))
        set_r(page, 1)
        check(f'{scheme} 1000px curve: fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))

        # ================= narrow
        print(f'== {scheme}: narrow 720px')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(300)
        for t, sel in (('plot', '.be-ssvg'), ('pe', '.be-psvg')):
            tab(page, t)
            if t == 'plot':
                page.click('.be-fam[data-fam="hal"]'); page.wait_for_timeout(100)
            page.wait_for_timeout(150)
            ov = page.evaluate("() => { const k = document.querySelector('.k'); return k.scrollWidth - k.clientWidth; }")
            check(f'narrow {t}: no horizontal overflow', ov <= 1, str(ov))
            check(f'narrow {t}: fonts >= 12px (HTML + SVG scaled)', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
            if t == 'plot':
                check('narrow plot: still 15 labels + anomaly', page.locator('.be-ssvg text.be-plab').count() == 15 and page.locator('.be-ssvg text.be-anom').count() == 1)
                clean(sel, 'narrow plot hal')
                shot('narrow-720-plot-hal')
                page.click('.be-fam[data-fam="all"]'); page.wait_for_timeout(100)
                clean(sel, 'narrow plot all')
                shot('narrow-720-plot-all')
                if L:
                    clip('zoom-narrow-shortbonds', '.be-ssvg', 30, 40, 330, 300)
            else:
                for v in (0.6, 1, 3.2):
                    set_r(page, v)
                    clean(sel, f'narrow curve r={v}')
                set_r(page, 1)
                shot('narrow-720-pe')
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for r in results if r[1])
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
