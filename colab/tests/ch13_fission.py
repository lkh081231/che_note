"""ch13 fission — homolytic / heterolytic fission 动画、reagent 分类、reaction type 配对 cell test.

usage: uv run --with playwright python -I colab/tests/ch13_fission.py $COLAB_TMP/cells/ch13-fission.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch13 --cell fission)
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
CHROMIUM = '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else chrome()
EXS = {'cl2': ('a', 'b', True), 'ch3cl': ('c', 'x', False), 'tbu': ('c', 'x', False)}
REDOX = [False] * 6   # 13.2 (g): [O] added / H taken by an oxidising agent; ethane + Cl₂ is substitution, not redox (same as ethene + Br₂)

HELP = r'''() => { window.T = {
  root() { let e = document.querySelector('.fi-wrap'); while (e && !e.fiHook) e = e.parentElement; return e; },
  H() { return T.root().fiHook; },
  svg() { return document.querySelector('.fi-stage svg'); },
  sc(svg) { return svg.getBoundingClientRect().width / svg.viewBox.baseVal.width; },
  rd(x, y, r) { const dx = Math.max(r.x - x, 0, x - r.x - r.width), dy = Math.max(r.y - y, 0, y - r.y - r.height); return Math.hypot(dx, dy); },
  rr(a, b) { const dx = Math.max(a.x - b.x - b.width, 0, b.x - a.x - a.width), dy = Math.max(a.y - b.y - b.height, 0, b.y - a.y - a.height); return Math.hypot(dx, dy); },
  vis(e) { for (let n = e; n && n.tagName && n.tagName.toLowerCase() !== 'svg'; n = n.parentNode) if (getComputedStyle(n).display === 'none') return false; return true; },
  /* the two electron dots: position (viewBox) + px distance to each atom's text box and to the bond midpoint */
  es(la, ra) {
    const svg = T.svg(), s = T.sc(svg), D = KO.atoms(svg), A = D.atoms[D.byName[la]], B = D.atoms[D.byName[ra]];
    const mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2, out = {};
    svg.querySelectorAll('circle.fi-e').forEach(c => { const x = +c.getAttribute('cx'), y = +c.getAttribute('cy');
      /* dA / dB in viewBox units (like KO's lone-pair check), dM in px */
      out[c.dataset.e] = { x, y, dA: T.rd(x, y, A.el.getBBox()), dB: T.rd(x, y, B.el.getBBox()), dM: Math.hypot(x - mx, y - my) * s,
                           r: +c.getAttribute('r') * s }; });
    out.n = svg.querySelectorAll('circle.fi-e').length;
    return out;
  },
  arrows() {
    const svg = T.svg(), s = T.sc(svg), D = KO.atoms(svg), out = [];
    svg.querySelectorAll('path.ko-arrow').forEach(p => {
      const from = p.dataset.from, to = p.dataset.to, F = KO.pt(svg, from), R = KO.ref(svg, to), Rf = KO.ref(svg, from);
      const sx = +p.dataset.sx, sy = +p.dataset.sy, tx = +p.dataset.tx, ty = +p.dataset.ty;
      let tip = null, tipOther = null;
      if (R.kind === 'atom') {
        tip = T.rd(tx, ty, D.atoms[R.i].el.getBBox()) * s;
        tipOther = Math.min(...D.atoms.filter(a => a.el && a.i !== R.i).map(a => T.rd(tx, ty, a.el.getBBox()) * s));
      }
      const L = p.getTotalLength(), e = p.getPointAtLength(L), e2 = p.getPointAtLength(L - 0.6), ul = Math.hypot(e.x - e2.x, e.y - e2.y) || 1;
      const cons = Math.hypot(e.x + (e.x - e2.x) / ul * 5 - tx, e.y + (e.y - e2.y) / ul * 5 - ty);
      const id = ((p.getAttribute('marker-end') || '').match(/#([^)]+)/) || [])[1];
      const mk = id && svg.querySelector('marker#' + CSS.escape(id)), mp = mk && mk.querySelector('path');
      const mb = mp ? mp.getBBox() : null;
      const skip = new Set([Rf.i, Rf.j, R.i, R.j].filter(v => v != null)), cross = [];
      D.atoms.forEach(a => {
        if (!a.el || skip.has(a.i)) return;
        const b = a.el.getBBox();
        for (let t = 0; t <= L; t += 1) { const q = p.getPointAtLength(t);
          if (q.x > b.x + 1 && q.x < b.x + b.width - 1 && q.y > b.y + 2 && q.y < b.y + b.height - 2) { cross.push(a.l); break; } }
      });
      /* how close the shaft comes to the far electron dots / other text (in px) */
      out.push({ from, to, kind: Rf.kind, half: p.classList.contains('ko-half'), tip, tipOther,
                 start: Math.hypot(sx - F.x, sy - F.y) * s, cons, len: L * s, units: mk ? mk.getAttribute('markerUnits') : null,
                 msz: mb ? Math.min(mb.width, mb.height) * s : 0, cross, stroke: getComputedStyle(p).stroke, vis: T.vis(p) });
    });
    return out;
  },
  marks() {
    const svg = T.svg(), D = KO.atoms(svg);
    return [...svg.querySelectorAll('text.ko-d, text.ko-q')].map(t => {
      const i = +t.getAttribute('data-atom'), b = t.getBBox();
      const box = a => a.el ? a.el.getBBox() : { x: a.x - 2.5, y: a.y - 2.5, width: 5, height: 5 };
      return { txt: t.textContent.trim(), atom: D.atoms[i].l, own: T.rr(b, box(D.atoms[i])),
               other: Math.min(...D.atoms.filter(a => a.i !== i).map(a => T.rr(b, box(a)))) };
    });
  },
  names() {
    const svg = T.svg(), D = KO.atoms(svg);
    return [...svg.querySelectorAll('text.fi-nm')].map(t => { const b = t.getBBox(), cx = b.x + b.width / 2, cy = b.y + b.height / 2;
      const d = D.atoms.filter(a => a.el).map(a => ({ l: a.l, n: a.n, d: Math.hypot(a.x - cx, a.y - cy) })).sort((p, q) => p.d - q.d);
      return { txt: t.textContent, side: t.dataset.nm, nearest: d[0].n, cx, cy }; });
  },
  outside() {
    const s = T.svg(), v = s.viewBox.baseVal;
    return [...s.querySelectorAll('text, circle, path, line')].filter(t => { if (t.closest('defs') || !T.vis(t)) return false; const b = t.getBBox();
      return b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5; })
      .map(t => t.textContent || t.tagName);
  },
  /* electron dots must not sit on top of letters (other than the lone pair hugging its own atom) */
  dotOverText() {
    const svg = T.svg(), D = KO.atoms(svg), out = [];
    svg.querySelectorAll('circle.fi-e').forEach(c => { const x = +c.getAttribute('cx'), y = +c.getAttribute('cy'), r = +c.getAttribute('r');
      D.atoms.forEach(a => { if (!a.el) return; const b = a.el.getBBox();
        if (x + r > b.x + 1 && x - r < b.x + b.width - 1 && y + r > b.y + 3 && y - r < b.y + b.height - 3) out.push(c.dataset.e + '@' + a.l); }); });
    svg.querySelectorAll('text.ko-d, text.ko-q, text.fi-nm').forEach(t => { const b = t.getBBox();
      svg.querySelectorAll('circle.fi-e').forEach(c => { const x = +c.getAttribute('cx'), y = +c.getAttribute('cy');
        if (T.rd(x, y, b) < 1) out.push(c.dataset.e + '@' + t.textContent); }); });
    return out;
  },
  minSvgFont() {
    const s = T.svg(), k = T.sc(s);
    return Math.min(...[...s.querySelectorAll('text')].filter(t => T.vis(t)).map(t => parseFloat(getComputedStyle(t).fontSize) * k));
  },
  /* smallest computed font of any visible HTML text in the card (sub / sup excluded) */
  minHtmlFont() {
    const out = [];
    document.querySelectorAll('.k *').forEach(e => {
      if (e.closest('svg') || /^(SUB|SUP|SCRIPT|STYLE|SMALL)$/.test(e.tagName)) return;
      if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) return;
      const r = e.getBoundingClientRect(); if (!r.width || !r.height) return;
      out.push([parseFloat(getComputedStyle(e).fontSize), e.className + ':' + e.textContent.trim().slice(0, 20)]);
    });
    return out.sort((a, b) => a[0] - b[0])[0];
  }
}; }'''


def shot(page, sel, path):
    """element screenshot via a page clip (Locator.screenshot waits for rAF stability and can hang)"""
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def frame_ok(page, tag):
    c = page.eval_on_selector_all('[data-clash]', 'ts => ts.map(t => t.textContent + ":" + t.getAttribute("data-clash"))')
    check(f'{tag}: no [data-clash]', not c, str(c))
    o = page.evaluate('T.outside()')
    check(f'{tag}: everything inside the viewBox', not o, str(o))
    d = page.evaluate('T.dotOverText()')
    check(f'{tag}: electron dots clear of every letter / label', not d, str(d))
    for m in page.evaluate('T.marks()'):
        check(f"{tag}: {m['txt']} on {m['atom']} hugs its atom (≤ 6, nearest)", m['own'] <= 6 and m['own'] <= m['other'] + 0.01,
              f"own {m['own']:.1f} other {m['other']:.1f}")


def arrow_ok(a, tag):
    nm = f"{tag}: {a['from']} → {a['to']}{' (fish-hook)' if a['half'] else ''}"
    check(f'{nm} tail ≤ 3 px from the bond midpoint', a['kind'] in ('bond', 'mid') and a['start'] <= 3, f"{a['kind']} {a['start']:.2f}")
    check(f'{nm} tip 2–8 px from the target label', a['tip'] is not None and 2 <= a['tip'] <= 8, str(a['tip']))
    check(f'{nm} tip unambiguous (other labels ≥ 1.8× farther)', a['tipOther'] >= 1.8 * a['tip'], f"{a['tip']:.1f} vs {a['tipOther']:.1f}")
    check(f'{nm} marker userSpaceOnUse, ≥ 6 px', a['units'] == 'userSpaceOnUse' and a['msz'] >= 6, f"{a['units']} {a['msz']:.1f}")
    check(f'{nm} head sits on the path end', a['cons'] < 0.8, f"{a['cons']:.2f}")
    check(f'{nm} visible shaft ≥ 14 px', a['len'] >= 14, f"{a['len']:.1f}")
    check(f'{nm} crosses no other atom label', not a['cross'], str(a['cross']))


raw = PAGE.read_text(encoding='utf-8')
vis_txt = re.sub(r'<[^>]+>', '', re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', raw, flags=re.S | re.I))
check('built HTML: no leaked literal * / {{ in visible text', '*' not in vis_txt and '{{' not in vis_txt, vis_txt[:80])
check('cell never uses oxidation number as the redox test', 'oxidation number' not in Path(__file__).resolve().parents[1].joinpath('src/ch13/fission.html').read_text(encoding='utf-8'))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme} PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        page.evaluate(HELP)

        def ex(k):
            page.click(f'.fi-ex button[data-ex="{k}"]'); page.wait_for_timeout(30)

        def st(k):
            page.click(f'.fi-steps button[data-st="{k}"]'); page.wait_for_timeout(30)

        def tab(k):
            page.click(f'.tabbar button[data-tab="{k}"]'); page.wait_for_timeout(40)

        if scheme == 'dark':
            print('== dark')
            shot(page, '.k', OUT / 'card-fis-dark.png')
            for k in EXS:
                ex(k)
                if k == 'cl2':
                    page.check('.fi-hook')
                for s in (0, 1, 2):
                    st(s); frame_ok(page, f'dark {k} phase {s}')
                    shot(page, '.fi-card', OUT / f'z2-{k}-{s}-dark.png')
            tab('cls')
            page.click('.fi-card2[data-id="nh3"]'); page.click('.fi-bin[data-cat="el"]'); page.wait_for_timeout(30)
            page.click('.fi-card2[data-id="oh"]'); page.click('.fi-bin[data-cat="nu"]'); page.wait_for_timeout(30)
            shot(page, '.k', OUT / 'card-cls-dark.png')
            tab('rx')
            page.click('.fi-rx[data-i="0"] [data-g="t"] button[data-v="substitution"]')
            page.click('.fi-rx[data-i="0"] [data-g="t"] button[data-v="addition"]')
            page.click('.fi-rx[data-i="0"] [data-g="r"] button[data-v="n"]'); page.wait_for_timeout(30)
            shot(page, '.k', OUT / 'card-rx-dark.png')
            ctx.close()
            continue

        print('== 1 load')
        check('tab 1 shown first, Cl–Cl selected, phase 0', page.is_visible('.fi-stage svg') and page.get_attribute('.fi-ex button.on', 'data-ex') == 'cl2'
              and page.get_attribute('.fi-stage', 'data-phase') == '0')
        check('hook exposed', page.evaluate('typeof T.H().set === "function"'))
        check('fish-hooks off by default → no arrows', page.locator('.fi-stage path.ko-arrow').count() == 0)

        print('== 2 electrons for each example')
        for k, (la, ra, homo) in EXS.items():
            ex(k)
            check(f'{k}: kind label', page.text_content('.fi-kind') == ('homolytic fission' if homo else 'heterolytic fission'), page.text_content('.fi-kind'))
            check(f'{k}: fish-hook checkbox {"enabled" if homo else "disabled"}', page.is_disabled('.fi-hook') != homo)
            check(f'{k}: xref to {"ch14#rx-frs" if homo else "ch15#rx-nucsub"} shown',
                  page.is_visible(f'.fi-x span[data-x="{"homo" if homo else "hetero"}"] a.xref') and
                  not page.is_visible(f'.fi-x span[data-x="{"hetero" if homo else "homo"}"] a.xref'))
            caps, pos = [], []
            for s in (0, 1, 2):
                st(s)
                check(f'{k} ③{s}: data-phase = {s}', page.get_attribute('.fi-stage', 'data-phase') == str(s))
                caps.append(page.text_content('.fi-cap'))
                e = page.evaluate(f'T.es({la!r}, {ra!r})')
                pos.append(e)
                check(f'{k} phase {s}: two electron dots, radius ≥ 3.5 px', e['n'] == 2 and min(e['a']['r'], e['b']['r']) >= 3.5, str(e))
                frame_ok(page, f'{k} phase {s}')
                shot(page, '.fi-card', OUT / f'z2-{k}-{s}.png')
                if s == 0:
                    check(f'{k} phase 0: both electrons on the bond (≤ 10 px from its midpoint)', e['a']['dM'] <= 10 and e['b']['dM'] <= 10,
                          f"{e['a']['dM']:.1f} {e['b']['dM']:.1f}")
                    check(f'{k} phase 0: the bond line is drawn', page.locator('.fi-stage .fi-bond line:not(.fi-brk)').count() == 1)
                    ar = page.evaluate('T.arrows()')
                    if homo:
                        check(f'{k} phase 0: no arrow until fish-hooks are switched on', not ar)
                    else:
                        check(f'{k} phase 0: exactly one full curly arrow, bond → X', len(ar) == 1 and not ar[0]['half'] and ar[0]['to'] == ra, str(ar))
                        for a in ar:
                            arrow_ok(a, k)
                        txt = page.text_content('.fi-stage svg')
                        check(f'{k} phase 0: δ+ and δ− drawn', 'δ+' in txt and 'δ−' in txt, txt)
                if s == 1:
                    check(f'{k} phase 1: bond drawn dashed / fading', page.locator('.fi-stage line.fi-brk').count() == 1)
                    check(f'{k} phase 1: no arrows, no δ', not page.evaluate('T.arrows()') and page.locator('.fi-stage text.ko-d').count() == 0)
                if s == 2:
                    check(f'{k} phase 2: no bond line left', page.locator('.fi-stage .fi-bond').count() == 0)
                    nm = page.evaluate('T.names()')
                    check(f'{k} phase 2: two product names, each nearest its own fragment',
                          len(nm) == 2 and {n['side']: n['nearest'] for n in nm}.get('l') in (la, None) and {n['side']: n['nearest'] for n in nm}.get('r') == ra,
                          str(nm))
                    if homo:
                        check(f'{k} ③: one electron ≤ 5 (viewBox units) from each Cl (left dot → left Cl)', e['a']['dA'] <= 5 and e['b']['dB'] <= 5 and e['a']['dB'] > 20 and e['b']['dA'] > 20,
                              f"a→A {e['a']['dA']:.1f} b→B {e['b']['dB']:.1f}")
                        check(f'{k} ③: no charges on radicals', page.locator('.fi-stage text.ko-q').count() == 0)
                        check(f'{k} ③: names say free radical', all(n['txt'] == 'free radical' for n in nm), str(nm))
                    else:
                        check(f'{k} ③: both electrons ≤ 5 (viewBox units) from X (a lone pair on X⁻)', e['a']['dB'] <= 5 and e['b']['dB'] <= 5, f"{e['a']['dB']:.1f} {e['b']['dB']:.1f}")
                        check(f'{k} ③: the lone pair faces the C⁺ (left of X)', e['a']['x'] < page.evaluate(f'KO.atoms(T.svg()).atoms[KO.atoms(T.svg()).byName[{ra!r}]].x'))
                        check(f'{k} ③: electrons far from C (≥ 20)', e['a']['dA'] >= 20 and e['b']['dA'] >= 20)
                        q = page.eval_on_selector_all('.fi-stage text.ko-q', 'ts => ts.map(t => t.textContent.trim())')
                        check(f'{k} ③: circled + on C and − on X', sorted(q) == ['+', '−'] and page.locator('.fi-stage circle.ko-qc').count() == 2, str(q))
            check(f'{k}: electron dots move between ①②③', all(abs(pos[i]['a']['x'] - pos[i + 1]['a']['x']) + abs(pos[i]['b']['x'] - pos[i + 1]['b']['x']) +
                                                            abs(pos[i]['a']['y'] - pos[i + 1]['a']['y']) > 2 for i in (0, 1)))
            check(f'{k}: caption differs per phase', len(set(caps)) == 3, str(caps))
            vbs = []
            for t in (0, 0.1, 0.3, 0.5, 0.7, 0.9, 1):
                page.evaluate(f'T.H().set({t})'); vbs.append(page.evaluate('T.svg().getAttribute("viewBox")'))
                c = page.locator('[data-clash]').count(); o = page.evaluate('T.outside()')
                if c or o:
                    check(f'{k} t={t}: no clash / outside', False, f'{c} {o}')
            check(f'{k}: one viewBox for the whole animation', len(set(vbs)) == 1, str(set(vbs)))

        print('== 3 fish-hooks')
        ex('cl2'); st(0)
        page.check('.fi-hook'); page.wait_for_timeout(30)
        ar = page.evaluate('T.arrows()')
        check('cl2 + fish-hook: 2 half arrows, one to each Cl', len(ar) == 2 and all(a['half'] for a in ar) and sorted(a['to'] for a in ar) == ['a', 'b'], str(ar))
        for a in ar:
            arrow_ok(a, 'cl2 fish-hook')
        check('fish-hooks coloured like their electron (two different colours)', len({a['stroke'] for a in ar}) == 2, str([a['stroke'] for a in ar]))
        check('caption mentions fish-hook', 'fish-hook' in page.text_content('.fi-cap'))
        frame_ok(page, 'cl2 + fish-hook')
        shot(page, '.fi-card', OUT / 'z2-cl2-0-hooks.png')
        st(1)
        check('fish-hooks only in phase ①', page.locator('.fi-stage path.ko-arrow').count() == 0)
        st(0); page.uncheck('.fi-hook'); page.wait_for_timeout(30)
        check('fish-hook off → 0 half arrows', page.locator('.fi-stage path.ko-half').count() == 0)

        print('== 4 controls: slider, play / pause, advance')
        page.evaluate('''() => { const s = document.querySelector('.fi-t'); s.value = 40; s.dispatchEvent(new Event('input', {bubbles: true})); }''')
        check('slider 40 → t = 0.40', abs(page.evaluate('T.H().t()') - 0.40) < 1e-9)
        st(0)
        page.click('.fi-play'); page.wait_for_timeout(60)
        check('play → playing, button says 暂停', page.evaluate('T.H().playing()') and '暂停' in page.text_content('.fi-play'))
        samples = []
        for _ in range(6):   # 350 ms apart: the first ~0.27 of t is the step-① hold, so 120 ms steps never leave it
            page.wait_for_timeout(350)
            samples.append((page.evaluate('T.H().t()'), page.evaluate("T.es('a', 'b')")['a']['x']))
        ts = [s[0] for s in samples]
        check('t increases frame by frame while playing', all(ts[i + 1] > ts[i] for i in range(len(ts) - 1)), str(ts))
        check('≥ 3 different electron positions sampled while playing', len({round(s[1], 2) for s in samples}) >= 3, str(samples))
        page.click('.fi-play'); page.wait_for_timeout(30)
        t1 = page.evaluate('T.H().t()'); page.wait_for_timeout(300); t2 = page.evaluate('T.H().t()')
        check('pause → t stays put', not page.evaluate('T.H().playing()') and t1 == t2 and '播放' in page.text_content('.fi-play'), f'{t1} {t2}')
        page.evaluate('T.H().set(0)'); page.evaluate('T.H().advance(1600)')
        check('advance(1600 ms) → t = 0.5', abs(page.evaluate('T.H().t()') - 0.5) < 1e-9)
        check('slider follows t', page.input_value('.fi-t') == '50')
        page.evaluate('T.H().set(0.97)'); page.click('.fi-play'); page.wait_for_timeout(500)
        check('playing to the end stops at t = 1, phase ③', page.evaluate('T.H().t()') == 1 and not page.evaluate('T.H().playing()')
              and page.get_attribute('.fi-stage', 'data-phase') == '2')
        page.click('.fi-play'); page.wait_for_timeout(60)
        check('play at the end restarts from 0', page.evaluate('T.H().t()') < 0.3 and page.evaluate('T.H().playing()'))
        tab('cls')
        check('switching tab pauses', not page.evaluate('T.H().playing()'))
        tab('fis')
        page.click('.fi-play'); page.wait_for_timeout(60); ex('tbu')
        check('picking another example pauses and resets to ①', not page.evaluate('T.H().playing()') and page.evaluate('T.H().t()') == 0)
        st(0); shot(page, '.k', OUT / 'card-fis-light.png')

        print('== 5 reagent classification')
        tab('cls')
        check('11 cards, 3 bins', page.locator('.fi-pool .fi-card2').count() == 11 and page.locator('.fi-bin').count() == 3)
        check('score starts at 0 / 11', '0 / 11' in page.text_content('.fi-score'))
        page.click('.fi-card2[data-id="nh3"]')
        check('selecting a card highlights the bins', page.locator('.fi-bin.hot').count() == 3 and page.locator('.fi-card2.sel').count() == 1)
        page.click('.fi-bin[data-cat="el"]'); page.wait_for_timeout(20)
        fb = page.text_content('.fi-fb')
        check('NH₃ → electrophile is wrong: card back with .badv, reason shown', page.locator('.fi-pool .fi-card2.badv[data-id="nh3"]').count() == 1
              and '✗' in fb and 'lone pair' in fb and '不带电不等于 electrophile' in fb and 'bad' in page.get_attribute('.fi-fb', 'class'), fb)
        check('wrong count 1', '放错 1 次' in page.text_content('.fi-score'), page.text_content('.fi-score'))
        page.click('.fi-card2[data-id="cl"]'); page.click('.fi-bin[data-cat="nu"]'); page.wait_for_timeout(20)
        check('Cl• → nucleophile: says • is an unpaired electron', 'unpaired electron' in page.text_content('.fi-fb'))
        page.click('.fi-card2[data-id="nh3"]'); page.click('.fi-bin[data-cat="nu"]'); page.wait_for_timeout(20)
        check('NH₃ → nucleophile right: chip in that bin, ✓ + reason', page.locator('.fi-bin[data-cat="nu"] .fi-chip[data-id="nh3"]').count() == 1
              and '✓' in page.text_content('.fi-fb') and page.locator('.fi-pool [data-id="nh3"]').count() == 0)
        page.drag_and_drop('.fi-card2[data-id="h"]', '.fi-bin[data-cat="el"]'); page.wait_for_timeout(30)
        check('drag H⁺ onto electrophile works', page.locator('.fi-bin[data-cat="el"] .fi-chip[data-id="h"]').count() == 1)
        cat = {'oh': 'nu', 'cl': 'fr', 'cat': 'el', 'cn': 'nu', 'br2': 'el', 'ch3': 'fr', 'h2o': 'nu', 'no2': 'el', 'br': 'nu'}
        for cid, c in cat.items():
            page.click(f'.fi-card2[data-id="{cid}"]'); page.click(f'.fi-bin[data-cat="{c}"]')
        page.wait_for_timeout(30)
        check('all placed: pool empty, 11 chips', page.locator('.fi-pool .fi-card2').count() == 0 and page.locator('.fi-chip').count() == 11)
        check('summary with mistakes (not 全对)', '全部放好了' in page.text_content('.fi-fb') and '放错 2 次' in page.text_content('.fi-fb'), page.text_content('.fi-fb'))
        check('chips carry their reason as a tooltip', all(page.eval_on_selector_all('.fi-chip', 'cs => cs.map(c => !!c.dataset.tip)')))
        check('bins: nucleophile 5 · electrophile 4 · free radical 2', [page.locator(f'.fi-bin[data-cat="{c}"] .fi-chip').count() for c in ('nu', 'el', 'fr')] == [5, 4, 2])
        check('every bin has its xref', all(page.locator(f'.fi-bin[data-cat="{c}"] a.xref[target="_blank"]').count() >= 1 for c in ('nu', 'el', 'fr')))
        page.mouse.move(2, 2); page.wait_for_timeout(250)   # let the tooltip fade out (.1 s transition)
        shot(page, '.k', OUT / 'card-cls-light.png')
        shot(page, '.fi-bins', OUT / 'z2-cls-bins.png')
        page.click('.fi-creset'); page.wait_for_timeout(20)
        check('重来: 11 cards back, no chips', page.locator('.fi-pool .fi-card2').count() == 11 and page.locator('.fi-chip').count() == 0 and '0 / 11' in page.text_content('.fi-score'))
        full = dict(cat, nh3='nu', h='el')
        for cid, c in full.items():
            page.click(f'.fi-card2[data-id="{cid}"]'); page.click(f'.fi-bin[data-cat="{c}"]')
        page.wait_for_timeout(20)
        check('all right first time → 全对', '全对' in page.text_content('.fi-fb') and 'ok' in page.get_attribute('.fi-fb', 'class'), page.text_content('.fi-fb'))
        page.click('.fi-creset'); page.click('.fi-card2[data-id="oh"]'); page.click('.fi-bin[data-cat="nu"]'); page.click('.fi-cshow'); page.wait_for_timeout(20)
        check('显示答案: the other 10 shown dashed (.rev)', page.locator('.fi-chip.rev').count() == 10 and page.locator('.fi-chip:not(.rev)').count() == 1)
        shot(page, '.fi-bins', OUT / 'z2-cls-reveal.png')
        page.click('.fi-creset')
        page.click('.fi-card2[data-id="nh3"]'); page.click('.fi-bin[data-cat="el"]'); page.wait_for_timeout(20)
        shot(page, '.k', OUT / 'card-cls-wrong.png')
        page.click('.fi-creset')

        print('== 6 reaction type')
        tab('rx')
        check('6 equations', page.locator('.fi-rx').count() == 6)
        rg = page.eval_on_selector_all('.fi-rg', 'es => es.map(e => e.textContent.replace("reagents and conditions：", "").trim())')
        check('every equation shows registry reagents', len(rg) == 6 and all(rg), str(rg))
        check('every equation links to its chapter (target _blank)', page.locator('.fi-rxl a.xref[target="_blank"]').count() == 6)
        R = '.fi-rx[data-i="{}"] [data-g="{}"] button[data-v="{}"]'
        page.click(R.format(0, 't', 'addition')); page.click(R.format(0, 'r', 'n')); page.wait_for_timeout(20)
        check('ethene + Br₂: addition ✓, redox 否 ✓ (13.2 (g): no O added, no H removed)',
              page.locator(R.format(0, 't', 'addition') + '.good').count() == 1 and page.locator(R.format(0, 'r', 'n') + '.good').count() == 1)
        fb0 = page.text_content('.fi-rx[data-i="0"] .fi-rfb')
        check('ethene feedback uses only the 13.2 (g) wording (no oxidation number)', '13.2 (g)' in fb0 and 'oxidation number' not in fb0, fb0)
        check('score 1 / 6 and 1 / 6', 'reaction type 一次答对 1 / 6' in page.text_content('.fi-rscore') and 'redox 一次答对 1 / 6' in page.text_content('.fi-rscore'))
        page.click(R.format(1, 't', 'addition')); page.wait_for_timeout(20)
        check('ethane + Cl₂ addition ✗: badv + says substitution', page.locator(R.format(1, 't', 'addition') + '.badv').count() == 1
              and '✗' in page.text_content('.fi-rx[data-i="1"] .fi-rfb') and 'substitution' in page.text_content('.fi-rx[data-i="1"] .fi-rfb'))
        page.click(R.format(1, 't', 'substitution')); page.click(R.format(1, 'r', 'y')); page.wait_for_timeout(20)
        fb1 = page.text_content('.fi-rx[data-i="1"] .fi-rfb')
        check('ethane + Cl₂: substitution later ✓; redox 是 ✗ (Cl₂ is not an oxidising agent giving [O])', page.locator(R.format(1, 't', 'substitution') + '.good').count() == 1
              and page.locator(R.format(1, 'r', 'y') + '.badv').count() == 1 and 'Cl₂ 不是提供 [O] 的 oxidising agent' in fb1 and '被 oxidising agent 拿走的 H' in fb1, fb1)
        check('feedback: one ✓ line + one ✗ line → block red, each line marked', 'bad' in page.get_attribute('.fi-rx[data-i="1"] .fi-rfb', 'class')
              and page.locator('.fi-rx[data-i="1"] .fi-rfb .ln.ok[data-g="t"]').count() == 1 and page.locator('.fi-rx[data-i="1"] .fi-rfb .ln.bad[data-g="r"]').count() == 1)
        shot(page, '.fi-rx[data-i="1"]', OUT / 'z2-rx-1-mixed.png')
        check('score unchanged by late answers (1 / 6)', 'reaction type 一次答对 1 / 6' in page.text_content('.fi-rscore'))
        page.click(R.format(1, 'r', 'n')); page.wait_for_timeout(20)
        check('both lines ✓ → block green', 'ok' in page.get_attribute('.fi-rx[data-i="1"] .fi-rfb', 'class').split()
              and page.locator('.fi-rx[data-i="1"] .fi-rfb .ln.bad').count() == 0)
        page.click(R.format(1, 'r', 'y')); page.wait_for_timeout(20)
        check('answered-right rows lock (a later wrong click is ignored)', page.locator(R.format(1, 'r', 'n') + '.good').count() == 1
              and page.locator('.fi-rx[data-i="1"] .fi-rfb .ln.bad').count() == 0)
        page.click(R.format(3, 't', 'addition')); page.click(R.format(3, 'r', 'n')); page.wait_for_timeout(20)
        check('type ✗ then redox ✓ → block stays red (not just the last answer)', 'bad' in page.get_attribute('.fi-rx[data-i="3"] .fi-rfb', 'class'))
        page.click(R.format(2, 't', 'hydrolysis')); page.wait_for_timeout(20)
        check('bromoethane + OH⁻ accepts hydrolysis', page.locator(R.format(2, 't', 'hydrolysis') + '.good').count() == 1)
        for i, rd in enumerate(REDOX):
            if i < 2:
                continue
            page.click(R.format(i, 'r', 'y' if rd else 'n'))
        page.wait_for_timeout(20)
        check('redox answers: none of the 6 is redox', all(page.locator(R.format(i, 'r', 'y' if rd else 'n') + '.good').count() == 1 for i, rd in enumerate(REDOX)))
        types = ['addition', 'substitution', 'hydrolysis', 'elimination', 'hydrolysis', 'condensation']
        for i in (3, 4, 5):
            page.click(R.format(i, 't', types[i]))
        page.wait_for_timeout(20)
        check('all 6 done → score says so', '6 条都做完了' in page.text_content('.fi-rscore'), page.text_content('.fi-rscore'))
        allfb = ' '.join(page.eval_on_selector_all('.fi-rfb', 'es => es.map(e => e.textContent)'))
        check('no feedback mentions oxidation number', 'oxidation number' not in allfb)
        shot(page, '.k', OUT / 'card-rx-light.png')
        shot(page, '.fi-rx[data-i="1"]', OUT / 'z2-rx-1.png')
        page.click('.fi-rreset'); page.wait_for_timeout(20)
        check('重来 clears every answer', page.locator('.fi-rrow button.good, .fi-rrow button.badv').count() == 0 and '0 / 6' in page.text_content('.fi-rscore'))
        page.click(R.format(0, 't', 'elimination')); page.click('.fi-rshow'); page.wait_for_timeout(20)
        check('显示答案 marks the right button in all 12 rows', page.locator('.fi-rrow button.good').count() == 12)
        check('显示答案 does not count as 一次答对', 'reaction type 一次答对 0 / 6' in page.text_content('.fi-rscore'))
        shot(page, '.fi-rx[data-i="0"]', OUT / 'z2-rx-0-reveal.png')
        page.click('.fi-rreset')

        check('no console error so far', not errors, '; '.join(errors))

        print('== 7 narrow (720 px)')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(200)
        tab('fis')
        worst = 99
        for k in EXS:
            ex(k)
            if k == 'cl2' and not page.is_checked('.fi-hook'):
                page.check('.fi-hook')
            for s in (0, 1, 2):
                st(s)
                worst = min(worst, page.evaluate('T.minSvgFont()'))
                fit = page.evaluate('(() => { const s = T.svg(), st = document.querySelector(".fi-stage"); return st.clientWidth - s.getBoundingClientRect().width; })()')
                if fit < 0:
                    check(f'720 {k} {s}: svg fits the stage', False, str(fit))
        check('every SVG label ≥ 12 px at 720 px (CSS px × rendered / viewBox)', worst >= 12, f'{worst:.2f}')
        ex('tbu'); st(0)
        for t in ('fis', 'cls', 'rx'):
            tab(t)
            ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
            check(f'720 {t}: no horizontal overflow', ov <= 0, str(ov))
            mf = page.evaluate('T.minHtmlFont()')
            check(f'720 {t}: HTML text ≥ 12 px', mf[0] >= 12, str(mf))
            shot(page, '.k', OUT / f'card-{t}-720.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
