"""ch03 hbond cell test: three tabs —
① drawing a hydrogen bond mark by mark (9701/22 Feb/Mar 2026 Q4(b)): five pairs (H₂O···H₂O, NH₃···H₂O, ethanol···water,
   CH₂(CN)COOH···H₂O, counterexample CH₄···H₂O), M1–M3 switches, 全部显示 / 全部隐藏, swap direction, four common mistakes;
② hydrogen bonds per molecule (H₂O 2, NH₃ 1) with a central molecule and its hydrogen-bonded neighbours;
③ the three anomalous properties of water + an ice vs liquid 2D toggle.

usage: uv run --with playwright python -I colab/tests/ch03_hbond.py <preview.html> <shots-dir>
(build the preview first: COLAB_TMP=/mnt/ai-shared/che_tmp/ch03 python3 tools/build_colab.py ch03 --cell hbond)
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

# pair → (default type, swapped type or None, lone pairs drawn in both molecules, C–H mistake available)
PAIRS = {
    'ww': ('O–H···O', None, 4, False),
    'nw': ('N–H···O', 'O–H···N', 3, False),
    'ew': ('O–H···O', 'O–H···O', 4, True),
    'aw': ('O–H···O', 'O–H···O', 7, True),
    'mw': (None, None, 2, False),
}
NAMES = {'ww': ('H₂O', 'H₂O'), 'nw': ('NH₃', 'H₂O'), 'ew': ('ethanol', 'H₂O'), 'aw': ('CH₂(CN)COOH', 'H₂O'), 'mw': ('CH₄', 'H₂O')}
SWNAMES = {'nw': ('H₂O', 'NH₃'), 'ew': ('H₂O', 'ethanol'), 'aw': ('H₂O', 'CH₂(CN)COOH')}
# common mistake → (marks M1..M3 awarded, red note)
ERRS = {'ch': ([1, 0, 0], '✗ H 连在 C 上'), 'dl': ([1, 1, 0], '✗ 缺 δ−'), 'lp': ([1, 0, 1], '✗ 没有 lone pair'), 'lab': ([0, 1, 1], '✗ 没有标注')}


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

# every label vs every other text (atoms included), every lone-pair dot, every drawn line / wedge edge, and the svg border.
# Lines are tested against label boxes (atom symbols sit where their own bonds end, so they are not tested against lines).
AUDIT_JS = """(sel) => {
  const svg = document.querySelector(sel);
  if (!svg) return ['no svg ' + sel];
  /* atom symbols: ink box (glyph width × cap height); the em box above / below the letter is empty */
  const BB = e => { const b = e.getBBox(); return e.classList.contains('hb-at') ? { x: b.x, y: +e.getAttribute('y') - 9, w: b.width, h: 18 } : { x: b.x, y: b.y, w: b.width, h: b.height }; };
  const hit = (a, b) => a.x < b.x + b.w - 0.5 && b.x < a.x + a.w - 0.5 && a.y < b.y + b.h - 0.5 && b.y < a.y + a.h - 0.5;
  const segHit = (s, r) => {
    const inside = (x, y) => x > r.x + 0.5 && x < r.x + r.w - 0.5 && y > r.y + 0.5 && y < r.y + r.h - 0.5;
    if (inside(s[0], s[1]) || inside(s[2], s[3])) return true;
    const E = [[r.x, r.y, r.x + r.w, r.y], [r.x, r.y + r.h, r.x + r.w, r.y + r.h], [r.x, r.y, r.x, r.y + r.h], [r.x + r.w, r.y, r.x + r.w, r.y + r.h]];
    return E.some(e => { const d = (s[2] - s[0]) * (e[3] - e[1]) - (s[3] - s[1]) * (e[2] - e[0]); if (!d) return false;
      const t = ((e[0] - s[0]) * (e[3] - e[1]) - (e[1] - s[1]) * (e[2] - e[0])) / d, u = ((e[0] - s[0]) * (s[3] - s[1]) - (e[1] - s[1]) * (s[2] - s[0])) / d;
      return t > 0.001 && t < 0.999 && u > 0.001 && u < 0.999; });
  };
  const texts = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim());
  const labs = texts.filter(t => !t.classList.contains('hb-at'));
  const out = [];
  for (let i = 0; i < texts.length; i++) for (let j = i + 1; j < texts.length; j++) {
    if (texts[i].classList.contains('hb-at') && texts[j].classList.contains('hb-at')) continue;
    if (hit(BB(texts[i]), BB(texts[j]))) out.push(texts[i].textContent + ' <-> ' + texts[j].textContent);
  }
  const dots = [...svg.querySelectorAll('.hb-lp circle, .hb-imol circle')].map(c => { const r = +c.getAttribute('r'); return { x: +c.getAttribute('cx') - r, y: +c.getAttribute('cy') - r, w: 2 * r, h: 2 * r }; });
  const segs = [];
  for (const l of svg.querySelectorAll('line')) segs.push([+l.getAttribute('x1'), +l.getAttribute('y1'), +l.getAttribute('x2'), +l.getAttribute('y2'), l.getAttribute('class')]);
  for (const pg of svg.querySelectorAll('polygon')) { const p = pg.getAttribute('points').split(' ').map(q => q.split(',').map(Number));
    for (let i = 0; i < p.length; i++) { const q = p[(i + 1) % p.length]; segs.push([p[i][0], p[i][1], q[0], q[1], 'wedge']); } }
  for (const rc of svg.querySelectorAll('rect')) { const x = +rc.getAttribute('x'), y = +rc.getAttribute('y'), w = +rc.getAttribute('width'), h = +rc.getAttribute('height');
    [[x, y, x + w, y], [x + w, y, x + w, y + h], [x, y + h, x + w, y + h], [x, y, x, y + h]].forEach(s => segs.push(s.concat(['box']))); }
  for (const c of svg.querySelectorAll('circle.hb-ring')) { const cx = +c.getAttribute('cx'), cy = +c.getAttribute('cy'), r = +c.getAttribute('r');
    for (let a = 0; a < 360; a += 30) { const b = a + 30; segs.push([cx + r * Math.cos(a * Math.PI / 180), cy + r * Math.sin(a * Math.PI / 180), cx + r * Math.cos(b * Math.PI / 180), cy + r * Math.sin(b * Math.PI / 180), 'ring']); } }
  for (const t of labs) {
    const r = BB(t);
    for (const d of dots) if (hit(r, d)) { out.push('on dot: ' + t.textContent); break; }
    for (const s of segs) if (segHit(s, r)) { out.push('line under label: ' + t.textContent + ' / ' + s[4]); break; }
  }
  const vb = svg.viewBox.baseVal;
  for (const t of texts) { const r = BB(t); if (r.x < vb.x - 0.5 || r.y < vb.y - 0.5 || r.x + r.w > vb.x + vb.width + 0.5 || r.y + r.h > vb.y + vb.height + 0.5) out.push('outside svg: ' + t.textContent); }
  return out;
}"""

# label ownership: distance (viewBox px) from each atom label to its own atom vs to the nearest other atom
NEAR_JS = """(sel) => {
  const svg = document.querySelector(sel);
  const atoms = [...svg.querySelectorAll('text.hb-at')].map(t => [t.dataset.mol + t.dataset.id, +t.dataset.x, +t.dataset.y]);
  const out = [];
  for (const t of svg.querySelectorAll('text[data-for]')) {
    const f = t.dataset.for, own = atoms.find(a => a[0] === f);
    if (!own) continue;
    const b = t.getBBox(), gap = p => Math.hypot(Math.max(b.x - p[1], 0, p[1] - b.x - b.width), Math.max(b.y - p[2], 0, p[2] - b.y - b.height));
    const cx = b.x + b.width / 2, cy = b.y + b.height / 2, cd = p => Math.hypot(cx - p[1], cy - p[2]);
    if (t.classList.contains('hb-dl')) {
      /* δ: short label — its centre must be clearly nearest its own atom */
      if (cd(own) > 34) out.push(t.textContent + ' far from ' + f + ' (' + cd(own).toFixed(1) + ')');
      for (const a of atoms) if (a[0] !== f && cd(a) < cd(own) * 1.25) out.push(t.textContent + '@' + f + ' centre near ' + a[0] + ' (' + cd(own).toFixed(1) + ' vs ' + cd(a).toFixed(1) + ')');
    } else if (t.classList.contains('hb-err')) {
      /* red note: the faulty atom is ringed; the note just has to sit beside the ring */
      if (gap(own) > 30) out.push(t.textContent + ' far from ' + f + ' (' + gap(own).toFixed(1) + ')');
    } else {
      if (gap(own) > 26) out.push(t.textContent + ' far from ' + f + ' (' + gap(own).toFixed(1) + ')');
      for (const a of atoms) if (a[0] !== f && gap(a) < gap(own) + 6) out.push(t.textContent + '@' + f + ' near ' + a[0] + ' (' + gap(own).toFixed(1) + ' vs ' + gap(a).toFixed(1) + ')');
    }
  }
  return out;
}"""

STATE_JS = """() => {
  const s = document.querySelector('.hb-dsvg');
  const g = s.dataset.geo.split(',').map(Number);
  const T = sel => [...s.querySelectorAll(sel)];
  const ln = s.querySelector('.hb-hb');
  const at = id => { const t = s.querySelector('text.hb-at[data-mol="' + id[0] + '"][data-id="' + id.slice(1) + '"]'); return t ? t.dataset.el : null; };
  return {
    pair: s.dataset.pair, err: s.dataset.err, swap: s.dataset.swap, X: s.dataset.x, A: s.dataset.a, geo: g,
    hb: ln ? { x1: +ln.getAttribute('x1'), y1: +ln.getAttribute('y1'), x2: +ln.getAttribute('x2'), y2: +ln.getAttribute('y2'), to: ln.dataset.to, bad: ln.classList.contains('hb-bad') } : null,
    gap: T('.hb-gap').length,
    hblab: T('text.hb-hblab').map(t => t.textContent), lplab: T('text.hb-lplab').map(t => t.textContent),
    lead: T('.hb-lead').map(l => [+l.getAttribute('x1'), +l.getAttribute('y1'), +l.getAttribute('x2'), +l.getAttribute('y2')]),
    deltas: T('text.hb-dl').map(t => [t.textContent, t.dataset.for, at(t.dataset.for)]),
    errlab: T('text.hb-err').map(t => t.textContent), no: T('text.hb-no').map(t => t.textContent),
    names: T('text.hb-name').map(t => [t.dataset.for, t.textContent]),
    lps: T('.hb-lp').map(l => ({ mol: l.dataset.mol, at: l.dataset.atom, key: l.classList.contains('hb-lpk'), cx: +l.dataset.cx, cy: +l.dataset.cy, n: l.querySelectorAll('circle').length })),
    rings: T('.hb-ring').length,
    type: document.querySelector('.hb-type').textContent,
    rows: [...document.querySelectorAll('.hb-ms .hb-m')].map(r => [r.dataset.state, r.querySelector('input').checked, r.querySelector('input').disabled, r.querySelector('.hb-mtx').textContent, r.querySelector('.hb-mres').textContent]),
    v: document.querySelector('.hb-verdict').dataset.v, vt: document.querySelector('.hb-verdict').textContent,
    swapVis: getComputedStyle(document.querySelector('.hb-swap')).visibility,
    errBtn: [...document.querySelectorAll('.hb-errs .hb-err')].map(b => [b.dataset.err, b.disabled, b.classList.contains('on')]),
    allDis: document.querySelector('.hb-all').disabled,
    bonded: (() => { const H = g.slice(2, 4); let best = null;
      for (const l of s.querySelectorAll('.hb-bonds[data-mol="d"] [data-bond]')) { const id = l.dataset.bond; if (id === 'wedge' || id === 'hash') continue;
        const [a, b] = id.split('-'); if (s.querySelector('text.hb-at[data-mol="d"][data-id="' + b + '"]').dataset.el === 'H') {
          const th = s.querySelector('text.hb-at[data-mol="d"][data-id="' + b + '"]'); if (Math.hypot(+th.dataset.x - H[0], +th.dataset.y - H[1]) < 0.5)
            best = s.querySelector('text.hb-at[data-mol="d"][data-id="' + a + '"]').dataset.el; } }
      return best; })(),
  };
}"""


def angle(X, H, A):
    v1 = (X[0] - H[0], X[1] - H[1]); v2 = (A[0] - H[0], A[1] - H[1])
    c = (v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))
    return math.degrees(math.acos(max(-1, min(1, c))))


def perp(P, A, B):
    """distance of point P from the line A–B"""
    return abs((B[0] - A[0]) * (A[1] - P[1]) - (A[0] - P[0]) * (B[1] - A[1])) / math.hypot(B[0] - A[0], B[1] - A[1])


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
        W = [1000]

        def shot(name, sel='.k'):
            page.mouse.move(2, 2); page.wait_for_timeout(30)
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        def clean(sel, what, near=True):
            a = page.evaluate(AUDIT_JS, sel); c = page.locator('.k [data-clash]').count()
            check(f'{scheme} {W[0]}px {what}: [data-clash] = 0, no rendered overlaps / lines under labels', c == 0 and not a,
                  f'clash {c} {page.evaluate("[...document.querySelectorAll(`.k [data-clash]`)].map(t => t.textContent)")}; {a[:4]}')
            if near:
                n = page.evaluate(NEAR_JS, sel)
                check(f'{scheme} {W[0]}px {what}: every atom label next to its own atom (>= 6 px nearer than any other atom)', not n, str(n[:4]))
            sm = page.evaluate(SMALL_JS)
            check(f'{scheme} {W[0]}px {what}: fonts >= 12px', not sm, str(sm[:4]))

        def tab(t):
            page.click(f'.tabbar button[data-tab="{t}"]'); page.wait_for_timeout(150)

        def pick(pr):
            page.click(f'.hb-pairs .hb-pair[data-pair="{pr}"]'); page.wait_for_timeout(100)

        def setm(vals):
            page.click('.hb-none'); page.wait_for_timeout(40)
            for i, v in enumerate(vals):
                if v:
                    page.click(f'.hb-ms .hb-m[data-mk="{i + 1}"] input'); page.wait_for_timeout(40)
            page.wait_for_timeout(60)

        def geo_ok(s, what):
            X, H, A, LP = s['geo'][0:2], s['geo'][2:4], s['geo'][4:6], s['geo'][6:8]
            ang = angle(X, H, A)
            check(f'{scheme} {what}: X–H···A collinear (180 ± 2°)', abs(ang - 180) <= 2, f'{ang:.2f}°')
            check(f'{scheme} {what}: acceptor lone pair on the X–H···A line', perp(LP, H, A) < 0.5 and min(H[0], A[0]) < LP[0] < max(H[0], A[0]), f'{perp(LP, H, A):.2f}')
            return X, H, A, LP

        # ================= ①
        print(f'== {scheme}: ① drawing')
        check('default tab = drawing, default pair = H₂O···H₂O', 'on' in page.get_attribute('.tabbar button[data-tab="draw"]', 'class') and
              'on' in page.get_attribute('.hb-pair[data-pair="ww"]', 'class'))
        s = page.evaluate(STATE_JS)
        check('default: M1–M3 all off, nothing drawn but the two molecules', s['hb'] is None and not s['lps'] and not s['deltas'] and not s['hblab'] and not s['lplab']
              and [r[0] for r in s['rows']] == ['off'] * 3 and s['v'] == 'partial' and '已画出 0 / 3' in s['vt'], str(s['rows']) + s['vt'])
        check('default: molecule names under each molecule', s['names'] == [['name-d', 'H₂O'], ['name-a', 'H₂O']], str(s['names']))
        clean('.hb-dsvg', 'default (all off)')
        shot('draw-default')
        for pr, (typ, swtyp, nlp, has_ch) in PAIRS.items():
            pick(pr)
            if pr == 'mw':
                s = page.evaluate(STATE_JS)
                check('CH₄: no hydrogen bond line, no «hydrogen bond» label, no δ', s['hb'] is None and not s['hblab'] and not s['deltas'], str(s))
                check('CH₄: red «✗ no hydrogen bond» across a dotted gap', s['no'] == ['✗ no hydrogen bond'] and s['gap'] == 1, str(s['no']))
                check('CH₄: M switches, 全部显示 and every common-mistake button disabled', all(r[2] for r in s['rows']) and s['allDis'] and
                      all(e[1] for e in s['errBtn']) and s['swapVis'] == 'hidden', str(s['rows']) + str(s['errBtn']))
                need = ['C–H 不够 polar', 'ΔEN = 2.5 − 2.1 = 0.4', '直接连在 N / O / F 上', 'C 上也没有 lone pair', '只有 id-id']
                check('CH₄: explanation (C–H not polar enough, no lone pair on C, only id-id)', s['v'] == 'none' and all(n in s['vt'] for n in need),
                      str([n for n in need if n not in s['vt']]))
                check('CH₄: type line says C–H cannot form a hydrogen bond', 'CH₄ 的 C–H 不能形成 hydrogen bond' in s['type'], s['type'])
                check('CH₄: water lone pairs still drawn (2 dots each), C–H points straight at one', len(s['lps']) == 2 and all(l['n'] == 2 for l in s['lps']), str(s['lps']))
                geo_ok(s, 'CH₄ C–H···O')
                check('CH₄: names CH₄ / H₂O', [n[1] for n in s['names']] == list(NAMES['mw']), str(s['names']))
                clean('.hb-dsvg', 'CH₄ counterexample')
                shot('draw-ch4')
                if L:
                    shot('zoom-ch4', '.hb-dsvg')
                continue
            # one switch at a time
            setm([0, 0, 0])
            s = page.evaluate(STATE_JS)
            check(f'{pr} off: nothing extra drawn', s['hb'] is None and not s['lps'] and not s['deltas'], str(s['deltas']))
            setm([1, 0, 0])
            s = page.evaluate(STATE_JS)
            X, H, A, LP = geo_ok(s, f'{pr} M1 only')
            check(f'{pr} M1 only: dashed line from the H to the acceptor atom + «hydrogen bond» label, no lone pairs / δ',
                  s['hb'] and s['hb']['to'] == 'atom' and abs(s['hb']['x1'] - H[0] - 11) < 0.6 and abs(s['hb']['x2'] - (A[0] - 15)) < 0.6 and
                  s['hblab'] == ['hydrogen bond'] and not s['lps'] and not s['deltas'], str(s['hb']))
            check(f'{pr} M1 only: only row M1 green', [r[0] for r in s['rows']] == ['on', 'off', 'off'] and '已画出 1 / 3' in s['vt'], str(s['rows']))
            clean('.hb-dsvg', f'{pr} M1 only')
            setm([0, 1, 0])
            s = page.evaluate(STATE_JS)
            key = [l for l in s['lps'] if l['key']]
            check(f'{pr} M2 only: every lone pair on N / O drawn as two dots ({nlp}), the acceptor one highlighted + «lone pair»',
                  len(s['lps']) == nlp and all(l['n'] == 2 for l in s['lps']) and len(key) == 1 and key[0]['mol'] == 'a' and
                  abs(key[0]['cx'] - LP[0]) < 0.6 and s['lplab'] == ['lone pair'] and s['hb'] is None and not s['deltas'], str(s['lps']))
            lb = page.evaluate("(() => { const b = document.querySelector('.hb-dsvg text.hb-lplab').getBBox(); return [b.x, b.y, b.width, b.height]; })()")
            ld = s['lead'][0] if s['lead'] else None
            check(f'{pr} M2 only: leader joins the highlighted lone pair to its label',
                  ld and abs(ld[0] - LP[0]) < 0.6 and abs(ld[1] - LP[1]) < 8 and lb[0] <= ld[2] <= lb[0] + lb[2] and abs(ld[3] - lb[1]) < 3, f'{ld} {lb}')
            check(f'{pr} M2 only: row M2 green', [r[0] for r in s['rows']] == ['off', 'on', 'off'])
            clean('.hb-dsvg', f'{pr} M2 only')
            setm([0, 0, 1])
            s = page.evaluate(STATE_JS)
            check(f'{pr} M3 only: three δ — δ− on X, δ+ on its H, δ− on the acceptor atom',
                  [(d[0], d[2], d[1][0]) for d in s['deltas']] == [('δ−', s['X'], 'd'), ('δ+', 'H', 'd'), ('δ−', s['A'], 'a')] and s['hb'] is None, str(s['deltas']))
            check(f'{pr} M3 only: row M3 green, M3 text is the δ sequence', [r[0] for r in s['rows']] == ['off', 'off', 'on'] and
                  f"δ− {s['X']}–H δ+ ···· δ− {s['A']}" in s['rows'][2][3], s['rows'][2][3])
            clean('.hb-dsvg', f'{pr} M3 only')
            for sw in ([False, True] if swtyp else [False]):
                if sw:
                    page.click('.hb-swap'); page.wait_for_timeout(100)
                page.click('.hb-all'); page.wait_for_timeout(100)
                s = page.evaluate(STATE_JS)
                tag = f'{pr}{" swapped" if sw else ""} all on'
                want = swtyp if sw else typ
                check(f'{tag}: type {want}', s['type'].startswith(want) and s['X'] + '–H···' + s['A'] == want and s['swap'] == ('1' if sw else '0'), s['type'])
                check(f'{tag}: donor H is bonded to {s["X"]} (N or O), acceptor atom N or O', s['bonded'] == s['X'] and s['X'] in 'NO' and s['A'] in 'NO', str(s['bonded']))
                X, H, A, LP = geo_ok(s, tag)
                hb = s['hb']
                check(f'{tag}: M1 dashed «hydrogen bond» line, M2 it starts at the acceptor lone pair and ends at the H',
                      hb and hb['to'] == 'lp' and abs(hb['x1'] - H[0] - 11) < 0.6 and abs(hb['x2'] - (LP[0] - 6)) < 0.6 and
                      perp((hb['x1'], hb['y1']), H, A) < 0.5 and perp((hb['x2'], hb['y2']), H, A) < 0.5 and s['hblab'] == ['hydrogen bond'], str(hb))
                key = [l for l in s['lps'] if l['key']]
                check(f'{tag}: M2 lone pairs drawn (two dots), «lone pair» label on the acceptor one', len(s['lps']) == nlp and len(key) == 1 and key[0]['mol'] == 'a'
                      and key[0]['n'] == 2 and s['lplab'] == ['lone pair'], str(len(s['lps'])))
                check(f'{tag}: M3 δ− {s["X"]} / δ+ H / δ− {s["A"]}', [(d[0], d[2], d[1][0]) for d in s['deltas']] == [('δ−', s['X'], 'd'), ('δ+', 'H', 'd'), ('δ−', s['A'], 'a')], str(s['deltas']))
                check(f'{tag}: all three rows green, verdict 3 / 3', [r[0] for r in s['rows']] == ['on'] * 3 and all(r[1] for r in s['rows']) and s['v'] == 'full'
                      and '3 / 3' in s['vt'] and '180°' in s['vt'], s['vt'])
                nm = SWNAMES[pr] if sw else NAMES[pr]
                check(f'{tag}: names {nm}', [n[1] for n in s['names']] == list(nm), str(s['names']))
                check(f'{tag}: type line names donor and acceptor', f'{nm[0]} 提供连在 {s["X"]} 上的 H（donor），{nm[1]} 的 {s["A"]} 提供 lone pair' in s['type'], s['type'])
                clean('.hb-dsvg', tag)
                shot(f'draw-{pr}{"-swap" if sw else ""}-all')
                shot(f'zoom-{pr}{"-swap" if sw else ""}-all', '.hb-dsvg')
            if swtyp:
                page.click('.hb-swap'); page.wait_for_timeout(100)
                check(f'{pr}: swap back → default direction', page.evaluate(STATE_JS)['swap'] == '0')
            # common mistakes
            for e, (marks, note) in ERRS.items():
                btn = page.locator(f'.hb-errs .hb-err[data-err="{e}"]')
                if e == 'ch' and not has_ch:
                    check(f'{pr}: «虚线连到 C 上的 H» disabled (no C–H here)', btn.is_disabled())
                    continue
                btn.click(); page.wait_for_timeout(100)
                s = page.evaluate(STATE_JS)
                tag = f'{pr} mistake {e}'
                check(f'{tag}: drawing + checklist M1–M3 = {marks}', s['err'] == e and [r[0] for r in s['rows']] == [('ok' if m else 'bad') for m in marks] and
                      [r[4] for r in s['rows']] == [('✓' if m else '✗') for m in marks], str(s['rows']))
                check(f'{tag}: verdict {sum(marks)} / 3 with a reason per mark', s['v'] == f'err-{e}' and f'{sum(marks)} / 3' in s['vt'] and
                      all(f'M{i + 1} {"✓" if m else "✗"}' in s['vt'] for i, m in enumerate(marks)), s['vt'])
                check(f'{tag}: red note «{note}»', s['errlab'] == [note], str(s['errlab']))
                geo_ok(s, tag)
                if e == 'ch':
                    check(f'{tag}: the dashed line goes to an H bonded to C (red)', s['bonded'] == 'C' and s['X'] == 'C' and s['hb'] and s['hb']['bad'], str(s['bonded']))
                    check(f'{tag}: verdict says it is not a hydrogen bond, only the O–H H can', '这根本不是 hydrogen bond' in s['vt'] and '连在 O 上的那个 H' in s['vt'], s['vt'])
                    check(f'{tag}: swap hidden', s['swapVis'] == 'hidden')
                if e == 'dl':
                    check(f'{tag}: only δ+ (H) and δ− (acceptor) — the donor δ− is missing', [(d[0], d[1][0]) for d in s['deltas']] == [('δ+', 'd'), ('δ−', 'a')], str(s['deltas']))
                if e == 'lp':
                    check(f'{tag}: no lone pairs anywhere, the line starts at the atom', not s['lps'] and s['hb']['to'] == 'atom' and not s['lplab'], str(s['hb']))
                if e == 'lab':
                    check(f'{tag}: dashed line + lone pair + δ, but no «hydrogen bond» label', s['hb'] and s['hb']['to'] == 'lp' and not s['hblab'] and len(s['deltas']) == 3, str(s['hblab']))
                if e != 'lab':
                    check(f'{tag}: red ring around the faulty atom', s['rings'] == 1)
                clean('.hb-dsvg', tag)
                if pr == 'aw' or (pr == 'ew' and e == 'ch') or (pr == 'ww' and L):
                    shot(f'draw-{pr}-err-{e}')
                    shot(f'zoom-{pr}-err-{e}', '.hb-dsvg')
                btn.click(); page.wait_for_timeout(80)
                check(f'{tag}: click again → back to the switches', page.evaluate(STATE_JS)['err'] == '')
            # leaving mistake mode by a switch
            page.click('.hb-errs .hb-err[data-err="dl"]'); page.wait_for_timeout(80)
            page.click('.hb-ms .hb-m[data-mk="1"] input'); page.wait_for_timeout(80)
            s = page.evaluate(STATE_JS)
            check(f'{pr}: an M switch leaves mistake mode (only M1 on)', s['err'] == '' and [r[0] for r in s['rows']] == ['on', 'off', 'off'], str(s['rows']))
        pick('ww')
        page.click('.hb-all'); page.wait_for_timeout(80)

        # ================= ②
        print(f'== {scheme}: ② counting')
        tab('count')
        for cm, (nh, nlp, n, nhb, spare) in {'w': (2, 2, 2, 4, 0), 'n': (3, 1, 1, 2, 2)}.items():
            page.click(f'.hb-cmols .hb-cmol[data-cm="{cm}"]'); page.wait_for_timeout(120)
            c = page.evaluate("""() => { const k = document.querySelector('.hb-count'), s = document.querySelector('.hb-csvg');
                return { nh: +k.dataset.nh, nlp: +k.dataset.nlp, n: +k.dataset.n, cnh: k.querySelector('.hb-nh').textContent, cnlp: k.querySelector('.hb-nlp').textContent,
                  cn: k.querySelector('.hb-n').textContent, text: k.textContent, mol: s.dataset.mol,
                  hbs: [...s.querySelectorAll('.hb-hb')].map(l => ({ role: l.dataset.role, g: l.dataset.geo.split(';').map(q => q.split(',').map(Number)),
                     x1: +l.getAttribute('x1'), y1: +l.getAttribute('y1'), x2: +l.getAttribute('x2'), y2: +l.getAttribute('y2') })),
                  mols: new Set([...s.querySelectorAll('text.hb-at')].map(t => t.dataset.mol)).size,
                  spare: [...s.querySelectorAll('text.hb-spare')].map(t => [t.textContent, t.dataset.for]),
                  lps: [...s.querySelectorAll('.hb-lp')].map(l => l.querySelectorAll('circle').length) }; }""")
            name = 'H₂O' if cm == 'w' else 'NH₃'
            check(f'{scheme} ② {name}: {nh} H, {nlp} lone pair(s) → {n} hydrogen bond(s) per molecule', (c['nh'], c['nlp'], c['n']) == (nh, nlp, n) and
                  (c['cnh'], c['cnlp'], c['cn']) == (str(nh), str(nlp), str(n)) and f'平均 {n} 个 hydrogen bond' in c['text'], str(c))
            check(f'{scheme} ② {name}: centre + {nhb} hydrogen-bonded neighbours, {nhb} dashed lines', c['mols'] == nhb + 1 and len(c['hbs']) == nhb, f"{c['mols']} {len(c['hbs'])}")
            bad = []
            for h in c['hbs']:
                X, H, A, LP = h['g']
                a = angle(X, H, A)
                if abs(a - 180) > 2 or perp(LP, H, A) > 0.5 or perp((h['x1'], h['y1']), H, A) > 0.5 or perp((h['x2'], h['y2']), H, A) > 0.5 or \
                        math.hypot(h['x1'] - H[0], h['y1'] - H[1]) > 12 or math.hypot(h['x2'] - LP[0], h['y2'] - LP[1]) > 7:
                    bad.append((h['role'], round(a, 2)))
            check(f'{scheme} ② {name}: every X–H···lone pair–A collinear (180 ± 2°), line from the H to the lone pair', not bad, str(bad))
            check(f'{scheme} ② {name}: lone pairs two dots each', all(x == 2 for x in c['lps']) and c['lps'], str(c['lps']))
            if cm == 'w':
                check(f'{scheme} ② H₂O: 2 neighbours accept (centre H → their lone pair), 2 donate (their H → centre lone pair)',
                      sorted(h['role'] for h in c['hbs']) == ['acc', 'acc', 'don', 'don'])
                check(f'{scheme} ② H₂O: text — 4 neighbours, 4 ÷ 2 = 2', '被 4 个邻居包围' in c['text'] and '4 ÷ 2 = 2' in c['text'] and 'extensively hydrogen bonded' in c['text'])
            else:
                check(f'{scheme} ② NH₃: one in, one out; the other two H labelled «多余的 H»', sorted(h['role'] for h in c['hbs']) == ['acc', 'don'] and
                      c['spare'] == [['多余的 H', 'cH2'], ['多余的 H', 'cH3']], str(c['spare']))
                check(f'{scheme} ② NH₃: text — 2 ÷ 2 = 1, boiling point −33 °C vs 100 °C', '2 ÷ 2 = 1' in c['text'] and '−33 °C' in c['text'] and '100 °C' in c['text'])
            clean('.hb-csvg', f'② {name}')
            shot(f'count-{cm}')
            shot(f'zoom-count-{cm}', '.hb-csvg')

        # ================= ③
        print(f'== {scheme}: ③ water')
        tab('water')
        props = page.evaluate("[...document.querySelectorAll('.hb-prop')].map(c => [c.dataset.prop, c.querySelector('.hb-ph').textContent, c.textContent])")
        want = {'bp': ('relatively high melting and boiling points', ['H₂O 100 °C', 'H₂S −60 °C', 'H₂Se −41 °C', 'H₂Te −2 °C', '约 −90 °C', '只有 id-id + pd-pd', 'extensive hydrogen bonding', '多得多的 energy']),
                'st': ('relatively high surface tension', ['水面像一层膜', 'surface tension 大', '被下面的 molecules 用 hydrogen bonds 往里拉']),
                'ice': ('density of ice < liquid water', ['ice 浮在水上', '4 个 H 以 tetrahedral 方式包围', 'open lattice', 'hydrogen bonds 比 covalent bonds 长', '熔化时 lattice 部分塌缩'])}
        check(f'{scheme} ③ three anomalous-property cards in order', [x[0] for x in props] == ['bp', 'st', 'ice'] and all(x[1] == want[x[0]][0] for x in props), str([x[1] for x in props]))
        for k, h, t in props:
            miss = [w for w in want[k][1] if w not in t]
            check(f'{scheme} ③ card «{h}»: 现象 + 原因 from the chapter table', not miss and '现象' in t and '原因' in t, str(miss))
        ICE_JS = """() => { const s = document.querySelector('.hb-isvg'), g = s.querySelector('.hb-net').getBBox();
            return { st: s.querySelector('.hb-net').dataset.state, n: +s.dataset.n, aI: +s.dataset.areaIce, aL: +s.dataset.areaLiq, box: g.width * g.height,
              O: s.querySelectorAll('.hb-iO').length, H: s.querySelectorAll('circle.hb-iH:not(.hb-iz)').length, zOwn: s.querySelectorAll('.hb-iz[data-z="own"]').length,
              zNb: s.querySelectorAll('.hb-iz[data-z="nb"]').length, hb: s.querySelectorAll('.hb-id').length, cov: s.querySelectorAll('.hb-ic').length,
              lab: s.querySelector('text.hb-boxlab').textContent, pct: +document.querySelector('.hb-area').dataset.pct, note: document.querySelector('.hb-icenote').textContent,
              pressed: [...document.querySelectorAll('.hb-states .hb-state')].filter(b => b.classList.contains('on')).map(b => b.dataset.st) }; }"""
        ice = page.evaluate(ICE_JS)
        N = ice['n']
        check(f'{scheme} ③ ice default: {N} molecules, 2 H each (in the page or out of it), every O has a 4th H marked out of the page',
              ice['st'] == 'ice' and N >= 30 and ice['O'] == N and ice['H'] + ice['zOwn'] == 2 * N and ice['zOwn'] + ice['zNb'] == N and ice['cov'] == ice['H'], str(ice))
        check(f'{scheme} ③ ice: hexagonal network with hydrogen bonds (dashed) between neighbours', ice['hb'] >= N, str(ice['hb']))
        check(f'{scheme} ③ ice: box label «ice：{N} 个 H₂O», note says open lattice + density 更小',
              ice['lab'] == f'ice：{N} 个 H₂O' and 'open lattice' in ice['note'] and 'density 更小' in ice['note'] and '4 个 H' in ice['note'] and ice['pressed'] == ['ice'], ice['note'])
        clean('.hb-isvg', '③ ice', near=False)
        shot('water-ice')
        shot('zoom-water-ice', '.hb-icecard')
        page.click('.hb-states .hb-state[data-st="liq"]'); page.wait_for_timeout(150)
        liq = page.evaluate(ICE_JS)
        check(f'{scheme} ③ liquid: same number of molecules ({N}), 2 H each, no out-of-page markers',
              liq['st'] == 'liq' and liq['n'] == N and liq['O'] == N and liq['H'] == 2 * N and liq['zOwn'] + liq['zNb'] == 0, str(liq))
        check(f'{scheme} ③ ice takes more area than liquid (data + rendered bbox), bar < 100 %',
              ice['aI'] > liq['aL'] and ice['box'] > liq['box'] * 1.1 and 50 < liq['pct'] < 100, f"{ice['aI']} {liq['aL']} {ice['box']:.0f} {liq['box']:.0f} {liq['pct']}")
        check(f'{scheme} ③ liquid: box label, note (lattice collapses, molecules closer) + same-number sentence',
              liq['lab'] == f'liquid：{N} 个 H₂O' and '部分塌缩' in liq['note'] and '靠得更近' in liq['note'] and f'同样 {N} 个 molecules' in liq['note'] and
              'ice 占的面积更大' in liq['note'] and liq['pressed'] == ['liq'], liq['note'])
        dmin = page.evaluate("""() => { const o = [...document.querySelectorAll('.hb-isvg .hb-iO')].map(c => [+c.getAttribute('cx'), +c.getAttribute('cy')]); let m = 1e9;
            for (let i = 0; i < o.length; i++) for (let j = i + 1; j < o.length; j++) m = Math.min(m, Math.hypot(o[i][0] - o[j][0], o[i][1] - o[j][1])); return m; }""")
        check(f'{scheme} ③ liquid: molecules do not overlap (O–O >= 30)', dmin >= 30, str(dmin))
        clean('.hb-isvg', '③ liquid', near=False)
        shot('water-liquid')
        shot('zoom-water-liquid', '.hb-icecard')
        page.click('.hb-states .hb-state[data-st="ice"]'); page.wait_for_timeout(100)

        # ================= narrow
        print(f'== {scheme}: narrow 720px')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(300)
        W[0] = 720
        tab('draw')

        def ov(what):
            o = page.evaluate("() => { const k = document.querySelector('.k'); return k.scrollWidth - k.clientWidth; }")
            check(f'narrow {what}: no horizontal overflow', o <= 1, str(o))
        ov('drawing')
        for pr in PAIRS:
            pick(pr)
            if pr == 'mw':
                clean('.hb-dsvg', 'narrow CH₄')
                shot('narrow-720-ch4')
                continue
            for vals in ([1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]):
                setm(vals)
                clean('.hb-dsvg', f'narrow {pr} M={vals}')
            geo_ok(page.evaluate(STATE_JS), f'narrow {pr}')
            if pr in ('ww', 'aw'):
                shot(f'narrow-720-{pr}-all')
            if PAIRS[pr][1]:
                page.click('.hb-swap'); page.wait_for_timeout(100)
                clean('.hb-dsvg', f'narrow {pr} swapped')
                page.click('.hb-swap'); page.wait_for_timeout(100)
            for e in ERRS:
                if e == 'ch' and not PAIRS[pr][3]:
                    continue
                page.click(f'.hb-errs .hb-err[data-err="{e}"]'); page.wait_for_timeout(100)
                clean('.hb-dsvg', f'narrow {pr} mistake {e}')
                if pr == 'aw' and e in ('ch', 'dl') and L:
                    shot(f'narrow-720-aw-err-{e}')
                page.click(f'.hb-errs .hb-err[data-err="{e}"]'); page.wait_for_timeout(80)
        tab('count')
        ov('counting')
        for cm in ('w', 'n'):
            page.click(f'.hb-cmols .hb-cmol[data-cm="{cm}"]'); page.wait_for_timeout(120)
            clean('.hb-csvg', f'narrow ② {cm}')
            shot(f'narrow-720-count-{cm}')
        tab('water')
        ov('water')
        for st in ('ice', 'liq'):
            page.click(f'.hb-states .hb-state[data-st="{st}"]'); page.wait_for_timeout(120)
            clean('.hb-isvg', f'narrow ③ {st}', near=False)
            shot(f'narrow-720-water-{st}')
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for r in results if r[1])
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
