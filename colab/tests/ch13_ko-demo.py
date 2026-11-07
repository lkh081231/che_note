"""ch13 ko-demo — test page for colab/kit/kitorg.js (window.KO).

usage: uv run --with playwright python -I colab/tests/ch13_ko-demo.py $COLAB_TMP/cells/ch13-ko-demo.html <shots-dir>
(build first: python3 tools/build_colab.py ch13 --cell ko-demo)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
PLAYERS = {'ea': '.d-ea', 'hbr': '.d-hbr', 'sn2': '.d-sn2', 'na': '.d-na', 'exam': '.d-exam'}

HELP = r'''() => { window.T = {
  sc(svg) { return svg.getBoundingClientRect().width / svg.viewBox.baseVal.width; },
  rd(x, y, r) { const dx = Math.max(r.x - x, 0, x - r.x - r.width), dy = Math.max(r.y - y, 0, y - r.y - r.height); return Math.hypot(dx, dy); },
  rr(a, b) { const dx = Math.max(a.x - b.x - b.width, 0, b.x - a.x - a.width), dy = Math.max(a.y - b.y - b.height, 0, b.y - a.y - a.height); return Math.hypot(dx, dy); },
  svg(sel) { return document.querySelector(sel + ' .ko-stage svg'); },
  arrows(sel) {
    const svg = T.svg(sel), s = T.sc(svg), D = KO.atoms(svg), out = [];
    svg.querySelectorAll('path.ko-arrow:not(.ko-try)').forEach(p => {
      const from = p.dataset.from, to = p.dataset.to, F = KO.pt(svg, from), R = KO.ref(svg, to), Rf = KO.ref(svg, from);
      const sx = +p.dataset.sx, sy = +p.dataset.sy, tx = +p.dataset.tx, ty = +p.dataset.ty;
      let tip = null;
      let tipOther = null;
      if (R.kind === 'atom') {
        tip = T.rd(tx, ty, D.atoms[R.i].el.getBBox()) * s;
        tipOther = Math.min(...D.atoms.filter(a => a.el && a.i !== R.i).map(a => T.rd(tx, ty, a.el.getBBox()) * s));
      }
      const L = p.getTotalLength(), e = p.getPointAtLength(L), e2 = p.getPointAtLength(L - 0.6), ul = Math.hypot(e.x - e2.x, e.y - e2.y) || 1;
      const cons = Math.hypot(e.x + (e.x - e2.x) / ul * 5 - tx, e.y + (e.y - e2.y) / ul * 5 - ty);
      const id = ((p.getAttribute('marker-end') || '').match(/#([^)]+)/) || [])[1];
      const mk = id && svg.querySelector('marker#' + CSS.escape(id)), mp = mk && mk.querySelector('path');
      const mb = mp ? mp.getBBox() : null;
      const units = mk ? mk.getAttribute('markerUnits') : null;
      const skip = new Set([Rf.i, Rf.j, R.i, R.j].filter(v => v != null)), cross = [];
      D.atoms.forEach(a => {
        if (!a.el || skip.has(a.i)) return;
        const b = a.el.getBBox();
        for (let t = 0; t <= L; t += 1) { const q = p.getPointAtLength(t);
          if (q.x > b.x + 1 && q.x < b.x + b.width - 1 && q.y > b.y + 2 && q.y < b.y + b.height - 2) { cross.push(a.l); break; } }
      });
      out.push({ from, to, kind: Rf.kind, tipOther, start: Math.hypot(sx - F.x, sy - F.y) * s, tip, cons, units, len: L * s,
                 msz: mb ? Math.min(mb.width, mb.height) * s : 0, cross, vis: getComputedStyle(p.parentNode).display !== 'none' });
    });
    return out;
  },
  /* δ± / charges / locants: gap to their own atom's text box, and no other atom closer */
  marks(svg) {
    const D = KO.atoms(svg), out = [];
    svg.querySelectorAll('text.ko-d, text.ko-q, text.ko-num').forEach(t => {
      const i = +t.getAttribute('data-atom'), b = t.getBBox();
      const box = a => a.el ? a.el.getBBox() : { x: a.x - 2.5, y: a.y - 2.5, width: 5, height: 5 };
      const own = T.rr(b, box(D.atoms[i]));
      const other = Math.min(...D.atoms.filter(a => a.i !== i).map(a => T.rr(b, box(a))));
      out.push({ txt: t.textContent, atom: D.atoms[i].l, own, other });
    });
    return out;
  },
  lps(svg) {
    const D = KO.atoms(svg);
    return [...svg.querySelectorAll('g.ko-lp')].map(g => { const a = D.atoms[+g.dataset.atom];
      return a.el ? T.rd(+g.dataset.x, +g.dataset.y, a.el.getBBox()) : Math.hypot(+g.dataset.x - a.x, +g.dataset.y - a.y); });
  },
  outside() {
    return [...document.querySelectorAll('.ko-stage svg, .d-num svg')].flatMap(s => { const v = s.viewBox.baseVal;
      return [...s.querySelectorAll('text, circle, path.ko-br')].filter(t => { if (t.closest('defs') || getComputedStyle(t).display === 'none' || (t.closest('g') && getComputedStyle(t.closest('g')).display === 'none')) return false; const b = t.getBBox();
        return b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5; })
        .map(t => t.textContent || t.tagName); });
  },
  client(sel, ref) {   /* screen point of a KO ref in the player's current svg */
    const svg = T.svg(sel), P = KO.pt(svg, ref), m = svg.getScreenCTM();
    return { x: m.a * P.x + m.c * P.y + m.e, y: m.b * P.x + m.d * P.y + m.f };
  }
}; }'''


def shot(page, sel, path):
    """element screenshot via a page clip: Locator.screenshot waits for 'stable' (two rAFs), which
    hangs when several headless Chromes share the machine"""
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def arrows_ok(page, tag, sel, n_expect):
    ar = page.evaluate(f'T.arrows({sel!r})')
    vis = [a for a in ar if a['vis']]
    check(f'{tag}: {n_expect} arrows drawn', len(vis) == n_expect, str(len(vis)))
    for a in vis:
        nm = f"{tag}: {a['from']} → {a['to']}"
        check(f'{nm} starts ≤ 3 px from its {a["kind"]}', a['start'] <= 3, f"{a['start']:.2f}")
        if a['tip'] is not None:
            check(f'{nm} tip 2–8 px from the target label', 2 <= a['tip'] <= 8, f"{a['tip']:.2f}")
            check(f'{nm} tip unambiguous (other labels ≥ 1.8× farther)', a['tipOther'] >= 1.8 * a['tip'], f"{a['tip']:.1f} vs {a['tipOther']:.1f}")
        check(f'{nm} marker userSpaceOnUse, ≥ 6 px', a['units'] == 'userSpaceOnUse' and a['msz'] >= 6, f"{a['units']} {a['msz']:.1f}")
        check(f'{nm} head sits on the path end', a['cons'] < 0.8, f"{a['cons']:.2f}")
        check(f'{nm} has a visible shaft (≥ 14 px)', a['len'] >= 14, f"{a['len']:.1f}")
        check(f'{nm} crosses no other atom label', not a['cross'], str(a['cross']))
    return ar


def decor_ok(page, tag, svg_js):
    ms = page.evaluate(f'T.marks({svg_js})')
    for m in ms:
        check(f"{tag}: {m['txt']} on {m['atom']} hugs its atom (≤ 6, nearest)", m['own'] <= 6 and m['own'] <= m['other'] + 0.01,
              f"own {m['own']:.1f} other {m['other']:.1f}")
    lp = page.evaluate(f'T.lps({svg_js})')
    check(f'{tag}: lone pairs ≤ 5 from their atom', all(d <= 5 for d in lp), str(lp))
    c = page.eval_on_selector_all('[data-clash]', 'ts => ts.map(t => (t.closest("[class^=d-]") || {}).className + ":" + t.textContent + ":" + t.getAttribute("data-clash"))')
    check(f'{tag}: no [data-clash]', not c, str(c))
    o = page.evaluate('T.outside()')
    check(f'{tag}: everything inside the viewBox', not o, str(o))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])  # without it screenshots hang
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        page.evaluate(HELP)

        def step(key, k):
            page.click(f'{PLAYERS[key]} .ko-dots button[data-i="{k}"]'); page.wait_for_timeout(30)

        if scheme == 'dark':
            shot(page, '.k', OUT / 'card-dark.png')
            for key, sel in PLAYERS.items():
                shot(page, f'{sel} .ko-stage', OUT / f'z2-{key}-dark.png')
            step('sn2', 1); shot(page, '.d-sn2 .ko-stage', OUT / 'z2-sn2-ts-dark.png')
            shot(page, '.d-num svg', OUT / 'z2-num-dark.png')
            check('dark: no label clash', page.locator('[data-clash]').count() == 0)
            ctx.close()
            continue

        print('== 1 Br2 + ethene')
        arrows_ok(page, 'ea', '.d-ea', 2)
        decor_ok(page, 'ea', 'T.svg(".d-ea")')
        txt = page.text_content('.d-ea .ko-stage svg')
        check('ea: δ+ and δ− drawn', 'δ+' in txt and 'δ−' in txt, txt)
        check('ea: tags pt2 / pt3', 'pt2' in txt and 'pt3' in txt, txt)
        check('ea: 3 marks listed', page.locator('.d-ea .ko-marks li.cur').count() == 3)
        check('ea: one step → prev and next disabled', page.is_disabled('.d-ea .ko-prev') and page.is_disabled('.d-ea .ko-next'))

        print('== 2 HBr + propene step 2')
        arrows_ok(page, 'hbr', '.d-hbr', 1)
        decor_ok(page, 'hbr', 'T.svg(".d-hbr")')
        check('hbr: two circled charges', page.locator('.d-hbr circle.ko-qc').count() == 2)
        check('hbr: one lone pair (2 dots) on Br', page.locator('.d-hbr g.ko-lp circle').count() == 2)
        sx = page.evaluate('''() => { const s = T.svg(".d-hbr"), D = KO.atoms(s), br = D.atoms[D.byName.br], c = D.atoms[D.byName.c2], l = D.lps[D.byName.br][0];
            return (l.x - br.x) * (c.x - br.x) + (l.y - br.y) * (c.y - br.y) > 0; }''')
        check('hbr: Br⁻ lone pair faces the C⁺', sx)

        print('== 3 SN2')
        arrows_ok(page, 'sn2', '.d-sn2', 2)
        decor_ok(page, 'sn2', 'T.svg(".d-sn2")')
        cap1 = page.text_content('.d-sn2 .ko-cap')
        check('sn2 step 1: marks M1, M2 current', page.locator('.d-sn2 .ko-marks li.cur').count() == 2)
        page.click('.d-sn2 .ko-next'); page.wait_for_timeout(30)
        check('sn2 step 2: no arrows', page.locator('.d-sn2 path.ko-arrow').count() == 0)
        check('sn2 step 2: caption changes', page.text_content('.d-sn2 .ko-cap') != cap1 and 'transition state' in page.text_content('.d-sn2 .ko-cap'))
        check('sn2 step 2: two dashed partial bonds (single lines)', page.locator('.d-sn2 line.ko-partial').count() == 2,
              str(page.locator('.d-sn2 line.ko-partial').count()))
        check('sn2 step 2: [ ] with charge', page.locator('.d-sn2 path.ko-br').count() == 1 and '−' in page.text_content('.d-sn2 text.ko-bq'))
        check('sn2 step 2: earlier marks shown as done', page.locator('.d-sn2 .ko-marks li.done').count() == 2 and page.locator('.d-sn2 .ko-marks li.cur').count() == 0)
        check('sn2 step 2: "no marks" note shown', page.is_visible('.d-sn2 .ko-marks li.none'))
        decor_ok(page, 'sn2-ts', 'T.svg(".d-sn2")')
        shot(page, '.d-sn2 .ko-stage', OUT / 'z2-sn2-ts.png')
        page.click('.d-sn2 .ko-next'); page.wait_for_timeout(30)
        check('sn2 step 3: product caption', 'propanenitrile' in page.text_content('.d-sn2 .ko-cap'))
        check('sn2 step 3: next disabled at the end', page.is_disabled('.d-sn2 .ko-next'))
        decor_ok(page, 'sn2-prod', 'T.svg(".d-sn2")')
        shot(page, '.d-sn2 .ko-stage', OUT / 'z2-sn2-prod.png')
        page.click('.d-sn2 .ko-reset'); page.wait_for_timeout(30)
        check('sn2: 重来 → step 1 with 2 arrows', page.locator('.d-sn2 path.ko-arrow').count() == 2)

        print('== 4 HCN + ethanal')
        arrows_ok(page, 'na', '.d-na', 2)
        decor_ok(page, 'na', 'T.svg(".d-na")')
        page.focus('.d-na .ko-mech'); page.keyboard.press('ArrowRight'); page.wait_for_timeout(30)
        check('na: → key goes to step 2', page.locator('.d-na .ko-dots button.on').text_content() == '2')
        arrows_ok(page, 'na step 2', '.d-na', 1)
        decor_ok(page, 'na-2', 'T.svg(".d-na")')
        check('na step 2: M3 current, M1 M2 done', page.locator('.d-na .ko-marks li.cur').count() == 1 and page.locator('.d-na .ko-marks li.done').count() == 2)
        shot(page, '.d-na .ko-stage', OUT / 'z2-na-2.png')
        page.keyboard.press('ArrowRight'); page.wait_for_timeout(30)
        check('na: → again → step 3, no arrows', page.locator('.d-na .ko-dots button.on').text_content() == '3' and page.locator('.d-na path.ko-arrow').count() == 0)
        shot(page, '.d-na .ko-stage', OUT / 'z2-na-3.png')
        page.keyboard.press('ArrowLeft'); page.keyboard.press('ArrowLeft'); page.wait_for_timeout(30)
        check('na: ← ← back to step 1', page.locator('.d-na .ko-dots button.on').text_content() == '1')
        page.keyboard.press('ArrowLeft')
        check('na: ← at step 1 stays', page.locator('.d-na .ko-dots button.on').text_content() == '1')

        print('== 5 KO.num')
        nums = page.eval_on_selector_all('.d-num text.ko-num', 'ts => ts.map(t => t.textContent)')
        check('num: locants 1–5', nums == ['1', '2', '3', '4', '5'], str(nums))
        decor_ok(page, 'num', 'document.querySelector(".d-num svg")')
        check('num: 5 highlight discs', page.locator('.d-num circle.ko-hl').count() == 5)
        near = page.evaluate('''() => { const s = document.querySelector('.d-num svg'), D = KO.atoms(s);
            return [...s.querySelectorAll('text.ko-num')].map(t => { const b = t.getBBox(), cx = b.x + b.width / 2, cy = b.y + b.height / 2, i = +t.dataset.atom;
              const d = a => Math.hypot(a.x - cx, a.y - cy); return D.atoms.every(a => a.i === i || d(a) > d(D.atoms[i])); }); }''')
        check('num: each locant nearest its own carbon', all(near), str(near))

        print('== 6 exam mode')
        E = '.d-exam'
        check('exam: arrows hidden', page.locator(f'{E} g.ko-ag:not(.ko-hide) path.ko-arrow:not(.ko-try)').count() == 0 and page.locator(f'{E} g.ko-ag').count() == 2)
        check('exam: bond targets shown', page.locator(f'{E} circle.ko-tg').count() > 3)
        shot(page, f'{E} .ko-stage', OUT / 'z2-exam-0.png')

        page.locator(E).scroll_into_view_if_needed()

        def click_ref(ref):
            pt = page.evaluate(f'T.client({E!r}, {ref!r})'); page.mouse.click(pt['x'], pt['y']); page.wait_for_timeout(30)

        def fb():
            return page.text_content(f'{E} .ko-fb'), page.get_attribute(f'{E} .ko-fb', 'class')

        sv = page.evaluate(f'(() => {{ const r = T.svg({E!r}).getBoundingClientRect(); return {{x: r.x, y: r.y}}; }})()')
        page.mouse.click(sv['x'] + 4, sv['y'] + 4); page.wait_for_timeout(30)
        check('exam: click on nothing → 没点中', '没点中' in fb()[0], fb()[0])
        click_ref('lp:cn')
        check('exam: first click selects the lone pair', '起点' in fb()[0] and 'lone pair on C' in fb()[0] and page.locator(f'{E} circle.ko-sel').count() == 1, fb()[0])
        click_ref('c1')
        t, c = fb()
        check('exam: lone pair → C is right', '✓' in t and 'ok' in c, t)
        check('exam: correct arrow revealed', page.locator(f'{E} g.ko-ag:not(.ko-hide) path.ko-arrow:not(.ko-try)').count() == 1)
        check('exam: M1 ticked', page.text_content(f'{E} .ko-marks li[data-m="M1"] .st') == '✓')
        click_ref('c1-o'); click_ref('c1')
        t, c = fb()
        check('exam: C=O → C is wrong, says the start was right', '✗' in t and '起点对' in t and 'bad' in c, t)
        check('exam: wrong try drawn dashed', page.locator(f'{E} path.ko-try').count() == 1)
        check('exam: correct C=O → O arrow shown', page.locator(f'{E} g.ko-ag:not(.ko-hide) path.ko-arrow:not(.ko-try)').count() == 2)
        check('exam: M2 crossed', page.text_content(f'{E} .ko-marks li[data-m="M2"] .st') == '✗')
        check('exam: step score 1 / 2', '1 / 2' in fb()[0], fb()[0])
        shot(page, f'{E} .ko-stage', OUT / 'z2-exam-1.png')
        check('exam: no clash after the try', page.locator('[data-clash]').count() == 0)
        page.click(f'{E} .ko-next'); page.wait_for_timeout(30)
        click_ref('o'); click_ref('h')
        t, c = fb()
        check('exam: O → H⁺ (from the atom) is wrong: must start at the lone pair', '✗' in t and '终点对' in t and 'lone pair' in t, t)
        page.click(f'{E} .ko-reset'); page.wait_for_timeout(30)
        page.click(f'{E} .ko-next'); page.wait_for_timeout(30)
        check('exam: 重来 clears the answers', page.locator(f'{E} g.ko-ag:not(.ko-hide) path.ko-arrow:not(.ko-try)').count() == 0)
        click_ref('lp:o'); click_ref('h')
        check('exam: lone pair on O⁻ → H⁺ right', '✓' in fb()[0] and '1 / 1' in fb()[0], fb()[0])
        page.click(f'{E} .ko-prev'); page.wait_for_timeout(30)
        page.click(f'{E} .ko-show'); page.wait_for_timeout(30)
        check('exam: 显示答案 reveals the rest', page.locator(f'{E} g.ko-ag:not(.ko-hide) path.ko-arrow:not(.ko-try)').count() == 2)
        page.focus(f'{E} .ko-mech'); page.keyboard.press('ArrowRight'); page.wait_for_timeout(30)
        check('exam: keyboard works here too', page.locator(f'{E} .ko-dots button.on').text_content() == '2')
        arrows_ok(page, 'exam step 2', E, 1)

        print('== shots')
        page.click('.d-sn2 .ko-reset'); page.click('.d-na .ko-reset'); page.wait_for_timeout(30)
        shot(page, '.k', OUT / 'card-light.png')
        for key, sel in PLAYERS.items():
            shot(page, f'{sel} .ko-stage', OUT / f'z2-{key}.png')
            shot(page, sel, OUT / f'player-{key}.png')
        shot(page, '.d-num svg', OUT / 'z2-num.png')
        check('no console error so far', not errors, '; '.join(errors))

        print('== narrow (720 px)')
        page.set_viewport_size({'width': 720, 'height': 1200}); page.wait_for_timeout(200)
        ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('no horizontal overflow at 720 px', ov <= 0, str(ov))
        fs = page.evaluate('''() => Math.min(...[...document.querySelectorAll('.ko-stage svg, .d-num svg')].flatMap(s => {
            const k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return [...s.querySelectorAll('text')].filter(t => getComputedStyle(t).display !== 'none' && !(t.closest('g') && getComputedStyle(t.closest('g')).display === 'none'))
              .map(t => parseFloat(getComputedStyle(t).fontSize) * k); }))''')
        check('every label ≥ 12 px at 720 px (CSS px × rendered / viewBox)', fs >= 12, f'{fs:.2f}')
        shot(page, '.k', OUT / 'card-720.png')
        shot(page, '.d-sn2', OUT / 'player-sn2-720.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
