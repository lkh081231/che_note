"""ch14 ea-mech — electrophilic addition mechanism player (Br2/ethene & HBr/propene, 2-methylpropene, Cl2).

usage: uv run --with playwright python -I colab/tests/ch14_ea-mech.py $COLAB_TMP/cells/ch14-ea-mech.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch14 --cell ea-mech)
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
CHROMIUM = os.environ.get('CHROME') or ('/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else chrome())

HELP = r'''() => { window.T = {
  sc(svg) {
    if (!svg || !svg.viewBox || !svg.viewBox.baseVal || !svg.viewBox.baseVal.width) return 1;
    return svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
  },
  rd(x, y, r) { const dx = Math.max(r.x - x, 0, x - r.x - r.width), dy = Math.max(r.y - y, 0, y - r.y - r.height); return Math.hypot(dx, dy); },
  rr(a, b) { const dx = Math.max(a.x - b.x - b.width, 0, b.x - a.x - a.width), dy = Math.max(a.y - b.y - b.height, 0, b.y - a.y - a.height); return Math.hypot(dx, dy); },
  svg(sel) { return document.querySelector(sel + ' .ko-stage svg'); },
  arrows(sel) {
    const svg = T.svg(sel);
    if (!svg) return [];
    const s = T.sc(svg), D = KO.atoms(svg), out = [];
    svg.querySelectorAll('path.ko-arrow:not(.ko-try)').forEach(p => {
      const from = p.dataset.from, to = p.dataset.to, F = KO.pt(svg, from), R = KO.ref(svg, to), Rf = KO.ref(svg, from);
      const sx = +p.dataset.sx, sy = +p.dataset.sy, tx = +p.dataset.tx, ty = +p.dataset.ty;
      let tip = null, tipOther = null;
      if (R && R.kind === 'atom' && D.atoms[R.i] && D.atoms[R.i].el) {
        tip = T.rd(tx, ty, D.atoms[R.i].el.getBBox()) * s;
        tipOther = Math.min(...D.atoms.filter(a => a.el && a.i !== R.i).map(a => T.rd(tx, ty, a.el.getBBox()) * s));
      }
      const L = p.getTotalLength(), e = p.getPointAtLength(L), e2 = p.getPointAtLength(L - 0.6), ul = Math.hypot(e.x - e2.x, e.y - e2.y) || 1;
      const cons = Math.hypot(e.x + (e.x - e2.x) / ul * 5 - tx, e.y + (e.y - e2.y) / ul * 5 - ty);
      const id = ((p.getAttribute('marker-end') || '').match(/#([^)]+)/) || [])[1];
      const mk = id && svg.querySelector('marker#' + CSS.escape(id)), mp = mk && mk.querySelector('path');
      const mb = mp ? mp.getBBox() : null;
      const units = mk ? mk.getAttribute('markerUnits') : null;
      const skip = new Set([Rf && Rf.i, Rf && Rf.j, R && R.i, R && R.j].filter(v => v != null)), cross = [];
      D.atoms.forEach(a => {
        if (!a.el || skip.has(a.i)) return;
        const b = a.el.getBBox();
        for (let t = 0; t <= L; t += 1) {
          const q = p.getPointAtLength(t);
          if (q.x > b.x + 1 && q.x < b.x + b.width - 1 && q.y > b.y + 2 && q.y < b.y + b.height - 2) {
            cross.push(a.l); break;
          }
        }
      });
      out.push({
        from, to, kind: Rf ? Rf.kind : 'unknown', tipOther, start: F ? Math.hypot(sx - F.x, sy - F.y) * s : 0,
        tip, cons, units, len: L * s,
        msz: mb ? Math.min(mb.width, mb.height) * s : 0, cross,
        vis: getComputedStyle(p.parentNode).display !== 'none'
      });
    });
    return out;
  },
  marks(svg) {
    if (!svg) return [];
    const D = KO.atoms(svg), out = [];
    svg.querySelectorAll('text.ko-d, text.ko-q, text.ko-num').forEach(t => {
      const i = +t.getAttribute('data-atom'), b = t.getBBox();
      const box = a => a && a.el ? a.el.getBBox() : { x: (a ? a.x : 0) - 2.5, y: (a ? a.y : 0) - 2.5, width: 5, height: 5 };
      const targetAtom = D.atoms[i];
      const own = targetAtom ? T.rr(b, box(targetAtom)) : 999;
      const other = Math.min(...D.atoms.filter(a => a.i !== i).map(a => T.rr(b, box(a))));
      out.push({ txt: t.textContent, atom: targetAtom ? targetAtom.l : '', own, other });
    });
    return out;
  },
  outside() {
    return [...document.querySelectorAll('.ko-stage svg')].flatMap(s => {
      if (!s.viewBox || !s.viewBox.baseVal) return [];
      const v = s.viewBox.baseVal;
      return [...s.querySelectorAll('text, circle, path.ko-br')].filter(t => {
        if (t.closest('defs') || getComputedStyle(t).display === 'none' || (t.closest('g') && getComputedStyle(t.closest('g')).display === 'none')) return false;
        const b = t.getBBox();
        return b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5;
      }).map(t => t.textContent || t.tagName);
    });
  },
  client(sel, ref) {
    const svg = T.svg(sel);
    if (!svg) return { x: 0, y: 0 };
    const P = KO.pt(svg, ref);
    if (!P) return { x: 0, y: 0 };
    const m = svg.getScreenCTM();
    if (!m) return { x: 0, y: 0 };
    return { x: m.a * P.x + m.c * P.y + m.e, y: m.b * P.x + m.d * P.y + m.f };
  }
}; }'''


def shot(page, sel, path):
    """element screenshot via a page clip: Locator.screenshot waits for 'stable' (two rAFs), which
    hangs when several headless Chromes share the machine"""
    if page.locator(sel).count() == 0:
        print(f'  WARN shot: selector {sel} not found, skip {path.name}')
        return
    try:
        bb = page.eval_on_selector(
            sel,
            'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
        )
        page.screenshot(path=str(path), clip=bb, full_page=True)
    except Exception as e:
        print(f'  WARN shot: failed to capture {path.name}: {e}')


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def text_of(page, sel):
    loc = page.locator(sel)
    if loc.count() == 0:
        return ''
    return loc.first.text_content() or ''


def click_of(page, sel):
    loc = page.locator(sel)
    if loc.count() == 0:
        return False
    loc.first.click()
    return True


def is_disabled(page, sel):
    loc = page.locator(sel)
    if loc.count() == 0:
        return False
    return loc.first.is_disabled()


def is_visible(page, sel):
    loc = page.locator(sel)
    if loc.count() == 0:
        return False
    return loc.first.is_visible()


def arrows_ok(page, tag, sel, n_expect):
    if page.locator(f'{sel} .ko-stage svg').count() == 0:
        check(f'{tag}: {n_expect} arrows drawn', False, f'{sel} .ko-stage svg not found')
        return []
    try:
        ar = page.evaluate(f'T.arrows({sel!r})')
    except Exception as e:
        check(f'{tag}: {n_expect} arrows drawn', False, f'evaluate failed: {e}')
        return []
    vis = [a for a in ar if a['vis']]
    check(f'{tag}: {n_expect} arrows drawn', len(vis) == n_expect, str(len(vis)))
    for a in vis:
        nm = f"{tag}: {a['from']} → {a['to']}"
        check(f'{nm} starts ≤ 3 px from its {a["kind"]}', a['start'] <= 3.5, f"{a['start']:.2f}")
        if a['tip'] is not None:
            check(f'{nm} tip 2–8 px from the target label', 2 <= a['tip'] <= 8.5, f"{a['tip']:.2f}")
            check(f'{nm} tip unambiguous (other labels ≥ 1.5× farther)', a['tipOther'] >= 1.5 * a['tip'], f"{a['tip']:.1f} vs {a['tipOther']:.1f}")
        check(f'{nm} marker userSpaceOnUse, ≥ 6 px', a['units'] == 'userSpaceOnUse' and a['msz'] >= 6, f"{a['units']} {a['msz']:.1f}")
        check(f'{nm} head sits on the path end', a['cons'] < 0.8, f"{a['cons']:.2f}")
        check(f'{nm} has a visible shaft (≥ 14 px)', a['len'] >= 14, f"{a['len']:.1f}")
        check(f'{nm} crosses no other atom label', not a['cross'], str(a['cross']))
    return ar


def decor_ok(page, tag, svg_js):
    try:
        ms = page.evaluate(f'T.marks({svg_js})')
    except Exception as e:
        check(f'{tag}: marks check', False, f'evaluate failed: {e}')
        ms = []
    for m in ms:
        check(f"{tag}: {m['txt']} on {m['atom']} hugs its atom (≤ 6.5)", m['own'] <= 6.5, f"own {m['own']:.1f} other {m['other']:.1f}")
    c = page.eval_on_selector_all('[data-clash]', 'ts => ts.map(t => t.textContent + ":" + t.getAttribute("data-clash"))')
    check(f'{tag}: no [data-clash]', len(c) == 0, str(c))
    o = page.evaluate('T.outside()')
    check(f'{tag}: everything inside the viewBox', len(o) == 0, str(o))


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])

    for scheme in ('light', 'dark'):
        ctx = browser.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.k')
        page.evaluate(HELP)

        P_HAL = '.ea-player-halogen'
        P_HX = '.ea-player-hx'

        if scheme == 'dark':
            shot(page, '.k', OUT / 'card-dark.png')
            shot(page, f'{P_HAL} .ko-stage', OUT / 'z2-dark-halogen.png')
            click_of(page, '.tabbar button[data-tab="hx"]')
            page.wait_for_timeout(100)
            shot(page, f'{P_HX} .ko-stage', OUT / 'z2-dark-hx.png')
            check('dark: no [data-clash]', page.locator('[data-clash]').count() == 0)
            ctx.close()
            continue

        # ================= Section 1: Halogen Addition (Br2 + ethene) =================
        print('== 1 Halogen Addition (Br2 + ethene)')
        check('Initial load: 0 console errors', len(errors) == 0, str(errors))
        check('Player container exists', page.locator(f'{P_HAL} .ko-mech').count() == 1)
        check('Halogen step 1: 3 dots', page.locator(f'{P_HAL} .ko-dots button').count() == 3)

        # Step 1: Reactants + induced dipole
        arrows_ok(page, 'hal-s1', P_HAL, 2)
        decor_ok(page, 'hal-s1', f'T.svg({P_HAL!r})')
        txt1 = text_of(page, f'{P_HAL} .ko-stage svg')
        check('hal-s1: δ+ and δ− drawn', 'δ+' in txt1 and 'δ−' in txt1, txt1)
        check('hal-s1: tags pt2 and pt3', 'pt2' in txt1 and 'pt3' in txt1, txt1)
        check('hal-s1: 3 marks listed as current', page.locator(f'{P_HAL} .ko-marks li.cur').count() == 3)
        check('hal-s1: prev disabled at start', is_disabled(page, f'{P_HAL} .ko-prev'))
        shot(page, f'{P_HAL} .ko-stage', OUT / 'z2-ea-step1.png')

        # Step 2: Intermediate carbocation + Br-
        click_of(page, f'{P_HAL} .ko-next')
        page.wait_for_timeout(50)
        check('hal-s2: step 2 dot active', text_of(page, f'{P_HAL} .ko-dots button.on') == '2')
        arrows_ok(page, 'hal-s2', P_HAL, 1)
        decor_ok(page, 'hal-s2', f'T.svg({P_HAL!r})')
        txt2 = text_of(page, f'{P_HAL} .ko-stage svg')
        check('hal-s2: tag pt5', 'pt5' in txt2, txt2)
        check('hal-s2: carbocation has + charge and Br- has - charge', page.locator(f'{P_HAL} circle.ko-qc').count() == 2)
        check('hal-s2: lone pair on Br- present', page.locator(f'{P_HAL} g.ko-lp circle').count() == 2)
        check('hal-s2: marks pt4 and pt5 current', page.locator(f'{P_HAL} .ko-marks li.cur').count() == 2)
        check('hal-s2: marks pt1-pt3 done', page.locator(f'{P_HAL} .ko-marks li.done').count() == 3)
        shot(page, f'{P_HAL} .ko-stage', OUT / 'z2-ea-step2.png')

        # Step 3: Product
        click_of(page, f'{P_HAL} .ko-next')
        page.wait_for_timeout(50)
        check('hal-s3: step 3 dot active', text_of(page, f'{P_HAL} .ko-dots button.on') == '3')
        check('hal-s3: 0 arrows on product step', page.locator(f'{P_HAL} path.ko-arrow').count() == 0)
        cap3 = text_of(page, f'{P_HAL} .ko-cap')
        check('hal-s3: caption contains 1,2-dibromoethane', '1,2-dibromoethane' in cap3, cap3)
        check('hal-s3: next disabled at end', is_disabled(page, f'{P_HAL} .ko-next'))
        shot(page, f'{P_HAL} .ko-stage', OUT / 'z2-ea-prod.png')

        # Reset and keyboard navigation
        click_of(page, f'{P_HAL} .ko-reset')
        page.wait_for_timeout(50)
        check('hal: reset returns to step 1', text_of(page, f'{P_HAL} .ko-dots button.on') == '1')
        if page.locator(f'{P_HAL} .ko-mech').count() > 0:
            page.focus(f'{P_HAL} .ko-mech')
            page.keyboard.press('ArrowRight')
            page.wait_for_timeout(50)
            check('hal: ArrowRight moves to step 2', text_of(page, f'{P_HAL} .ko-dots button.on') == '2')
            page.keyboard.press('ArrowLeft')
            page.wait_for_timeout(50)
            check('hal: ArrowLeft moves back to step 1', text_of(page, f'{P_HAL} .ko-dots button.on') == '1')

        # ================= Section 2: Switch to Cl2 + ethene =================
        print('== 2 Switch Halogen: Cl2 + ethene')
        click_of(page, 'button[data-hal="cl2"]')
        page.wait_for_timeout(50)
        arrows_ok(page, 'cl2-s1', P_HAL, 2)
        txt_cl1 = text_of(page, f'{P_HAL} .ko-stage svg')
        check('cl2-s1: Cl2 induced dipole drawn', 'Cl' in txt_cl1 and 'δ+' in txt_cl1, txt_cl1)
        shot(page, f'{P_HAL} .ko-stage', OUT / 'z2-cl2-step1.png')

        # Step forward to product of Cl2
        click_of(page, f'{P_HAL} .ko-next')
        page.wait_for_timeout(50)
        click_of(page, f'{P_HAL} .ko-next')
        page.wait_for_timeout(50)
        cap_cl = text_of(page, f'{P_HAL} .ko-cap')
        check('cl2-s3: product contains 1,2-dichloroethane', '1,2-dichloroethane' in cap_cl, cap_cl)

        # Switch back to Br2
        click_of(page, 'button[data-hal="br2"]')
        page.wait_for_timeout(50)

        # ================= Section 3: Exam Mode (Halogen) =================
        print('== 3 Exam Mode: Halogen')
        click_of(page, '.ea-exam-chk1')
        page.wait_for_timeout(50)
        check('exam-hal: arrows hidden initially', page.locator(f'{P_HAL} g.ko-ag:not(.ko-hide) path.ko-arrow:not(.ko-try)').count() == 0)
        check('exam-hal: target dots on bonds shown', page.locator(f'{P_HAL} circle.ko-tg').count() >= 2)
        shot(page, f'{P_HAL} .ko-stage', OUT / 'z2-exam-halogen.png')

        # Click outside on nothing
        stage_rect = page.evaluate(f'(() => {{ const s = T.svg({P_HAL!r}); return s ? s.getBoundingClientRect() : null; }})()')
        if stage_rect:
            page.mouse.click(stage_rect['x'] + 4, stage_rect['y'] + 4)
            page.wait_for_timeout(30)
            fb_text = text_of(page, f'{P_HAL} .ko-fb')
            check('exam-hal: click nothing gives 没点中 feedback', '没点中' in fb_text, fb_text)
        else:
            check('exam-hal: click nothing gives 没点中 feedback', False, 'svg missing')

        # Correct click: c1-c2 bond -> b2 (Brδ+)
        pt_bond = page.evaluate(f'T.client({P_HAL!r}, "c1-c2")')
        if pt_bond and (pt_bond.get('x') or pt_bond.get('y')):
            page.mouse.click(pt_bond['x'], pt_bond['y'])
            page.wait_for_timeout(30)
            fb_s = text_of(page, f'{P_HAL} .ko-fb')
            check('exam-hal: first click selects C=C bond', '起点' in fb_s and 'bond' in fb_s, fb_s)
        else:
            check('exam-hal: first click selects C=C bond', False, 'pt_bond missing')

        pt_b2 = page.evaluate(f'T.client({P_HAL!r}, "b2")')
        if pt_b2 and (pt_b2.get('x') or pt_b2.get('y')):
            page.mouse.click(pt_b2['x'], pt_b2['y'])
            page.wait_for_timeout(30)
            fb_ok = text_of(page, f'{P_HAL} .ko-fb')
            check('exam-hal: bond -> Brδ+ is correct', '✓' in fb_ok, fb_ok)
            check('exam-hal: pt2 marked with tick', text_of(page, f'{P_HAL} .ko-marks li[data-m="pt2"] .st') == '✓')
        else:
            check('exam-hal: bond -> Brδ+ is correct', False, 'pt_b2 missing')

        # Wrong click: b1-b2 bond -> c1
        pt_b1b2 = page.evaluate(f'T.client({P_HAL!r}, "b1-b2")')
        pt_c1 = page.evaluate(f'T.client({P_HAL!r}, "c1")')
        if pt_b1b2 and pt_c1 and (pt_b1b2.get('x') or pt_b1b2.get('y')):
            page.mouse.click(pt_b1b2['x'], pt_b1b2['y'])
            page.wait_for_timeout(30)
            page.mouse.click(pt_c1['x'], pt_c1['y'])
            page.wait_for_timeout(30)
            fb_bad = text_of(page, f'{P_HAL} .ko-fb')
            check('exam-hal: wrong target reports error', '✗' in fb_bad and '起点对' in fb_bad, fb_bad)
            check('exam-hal: wrong try drawn dashed', page.locator(f'{P_HAL} path.ko-try').count() == 1)
            check('exam-hal: pt3 marked with cross', text_of(page, f'{P_HAL} .ko-marks li[data-m="pt3"] .st') == '✗')
        else:
            check('exam-hal: wrong target reports error', False, 'click targets missing')

        # Turn off exam mode
        click_of(page, '.ea-exam-chk1')
        page.wait_for_timeout(50)

        # ================= Section 4: Pane 2 (HBr + propene) =================
        print('== 4 Pane 2: Hydrogen Halide (HBr + propene)')
        click_of(page, '.tabbar button[data-tab="hx"]')
        page.wait_for_timeout(100)
        check('hx: pane 2 visible', is_visible(page, '[data-pane="hx"]'))
        check('hx: player exists', page.locator(f'{P_HX} .ko-mech').count() == 1)

        # Step 1: propene + HBr
        arrows_ok(page, 'hx-s1', P_HX, 2)
        decor_ok(page, 'hx-s1', f'T.svg({P_HX!r})')
        txt_hx1 = text_of(page, f'{P_HX} .ko-stage svg')
        check('hx-s1: tags M1 and M2', 'M1' in txt_hx1 and 'M2' in txt_hx1, txt_hx1)
        check('hx-s1: dipoles Hδ+ and Brδ−', 'δ+' in txt_hx1 and 'δ−' in txt_hx1, txt_hx1)
        shot(page, f'{P_HX} .ko-stage', OUT / 'z2-hx-step1.png')

        # Step 2: Side-by-side major (secondary) vs minor (primary)
        click_of(page, f'{P_HX} .ko-next')
        page.wait_for_timeout(50)
        check('hx-s2: step 2 dot active', text_of(page, f'{P_HX} .ko-dots button.on') == '2')
        arrows_ok(page, 'hx-s2', P_HX, 2)  # major (M4) + minor (mut)
        decor_ok(page, 'hx-s2', f'T.svg({P_HX!r})')

        txt_hx2 = text_of(page, f'{P_HX} .ko-stage svg')
        check('hx-s2: major secondary carbocation label present', 'major' in txt_hx2 and '2° carbocation' in txt_hx2, txt_hx2)
        check('hx-s2: minor primary carbocation label present', 'minor' in txt_hx2 and '1° carbocation' in txt_hx2, txt_hx2)

        # Inductive effect arrows
        ind_count = page.locator(f'{P_HX} polygon.ko-ind-arr').count()
        check('hx-s2: 3 inductive effect arrows (2 on secondary, 1 on primary)', ind_count == 3, str(ind_count))

        # Check minor pathway has muted style
        faint_count = page.locator(f'{P_HX} .ea-faint').count()
        check('hx-s2: minor pathway elements styled with .ea-faint', faint_count > 0, str(faint_count))
        shot(page, f'{P_HX} .ko-stage', OUT / 'z2-hx-step2.png')

        # Step 3: Products comparison (2-bromopropane vs 1-bromopropane)
        click_of(page, f'{P_HX} .ko-next')
        page.wait_for_timeout(50)
        check('hx-s3: step 3 dot active', text_of(page, f'{P_HX} .ko-dots button.on') == '3')
        txt_hx3 = text_of(page, f'{P_HX} .ko-stage svg')
        check('hx-s3: major product 2-bromopropane', '2-bromopropane' in txt_hx3, txt_hx3)
        check('hx-s3: minor product 1-bromopropane', '1-bromopropane' in txt_hx3, txt_hx3)
        shot(page, f'{P_HX} .ko-stage', OUT / 'z2-hx-step3.png')

        # ================= Section 5: Switch to 2-methylpropene + HBr =================
        print('== 5 Switch Alkene: 2-methylpropene + HBr')
        click_of(page, 'button[data-alk="tbene"]')
        page.wait_for_timeout(50)
        check('tbene-s1: 2-methylpropene step 1 has 2 arrows', page.locator(f'{P_HX} path.ko-arrow').count() == 2)

        # Step 2: tertiary carbocation
        click_of(page, f'{P_HX} .ko-next')
        page.wait_for_timeout(50)
        txt_tb2 = text_of(page, f'{P_HX} .ko-stage svg')
        check('tbene-s2: major tertiary carbocation label', '3° carbocation' in txt_tb2, txt_tb2)
        ind_tb = page.locator(f'{P_HX} polygon.ko-ind-arr').count()
        check('tbene-s2: 4 inductive arrows (3 on tertiary, 1 on primary)', ind_tb == 4, str(ind_tb))
        decor_ok(page, 'tbene-s2', f'T.svg({P_HX!r})')
        shot(page, f'{P_HX} .ko-stage', OUT / 'z2-tbene-step2.png')

        # Step 3: product 2-bromo-2-methylpropane
        click_of(page, f'{P_HX} .ko-next')
        page.wait_for_timeout(50)
        txt_tb3 = text_of(page, f'{P_HX} .ko-stage svg')
        check('tbene-s3: product contains 2-bromo-2-methylpropane', '2-bromo-2-methylpropane' in txt_tb3, txt_tb3)
        shot(page, f'{P_HX} .ko-stage', OUT / 'z2-tbene-step3.png')

        # Switch back to propene
        click_of(page, 'button[data-alk="propene"]')
        page.wait_for_timeout(50)

        # ================= Section 6: Exam Mode (HX) =================
        print('== 6 Exam Mode: HX')
        click_of(page, '.ea-exam-chk2')
        page.wait_for_timeout(50)
        click_of(page, f'{P_HX} .ko-dots button[data-i="1"]')
        page.wait_for_timeout(50)
        check('exam-hx: major arrow hidden', page.locator(f'{P_HX} g.ko-ag:not(.ko-hide) path.ko-arrow:not(.ko-try)').count() == 0)
        shot(page, f'{P_HX} .ko-stage', OUT / 'z2-exam-hx.png')

        # Wrong click on step 2: click lone pair on Br-, then click primary carbocation p_c1
        pt_lp = page.evaluate(f'T.client({P_HX!r}, "lp:s_br")')
        pt_pc1 = page.evaluate(f'T.client({P_HX!r}, "p_c1")')
        if pt_lp and pt_pc1 and (pt_lp.get('x') or pt_lp.get('y')):
            page.mouse.click(pt_lp['x'], pt_lp['y'])
            page.wait_for_timeout(30)
            page.mouse.click(pt_pc1['x'], pt_pc1['y'])
            page.wait_for_timeout(30)
            fb_hx_bad = text_of(page, f'{P_HX} .ko-fb')
            check('exam-hx: attacking primary carbocation is rejected with explanation',
                  '✗' in fb_hx_bad and '起点对' in fb_hx_bad, fb_hx_bad)
        else:
            check('exam-hx: attacking primary carbocation is rejected with explanation', False, 'click targets missing')

        # Reset step 2, click correctly: lp:s_br -> s_c2
        click_of(page, f'{P_HX} .ko-reset')
        page.wait_for_timeout(50)
        click_of(page, f'{P_HX} .ko-dots button[data-i="1"]')
        page.wait_for_timeout(50)
        pt_lp2 = page.evaluate(f'T.client({P_HX!r}, "lp:s_br")')
        pt_sc2 = page.evaluate(f'T.client({P_HX!r}, "s_c2")')
        if pt_lp2 and pt_sc2 and (pt_lp2.get('x') or pt_lp2.get('y')):
            page.mouse.click(pt_lp2['x'], pt_lp2['y'])
            page.wait_for_timeout(30)
            page.mouse.click(pt_sc2['x'], pt_sc2['y'])
            page.wait_for_timeout(30)
            fb_hx_ok = text_of(page, f'{P_HX} .ko-fb')
            check('exam-hx: lone pair -> secondary C+ is correct', '✓' in fb_hx_ok, fb_hx_ok)
            check('exam-hx: M4 marked with tick', text_of(page, f'{P_HX} .ko-marks li[data-m="M4"] .st') == '✓')
        else:
            check('exam-hx: lone pair -> secondary C+ is correct', False, 'click targets missing')

        # Turn off exam mode
        click_of(page, '.ea-exam-chk2')
        page.wait_for_timeout(50)

        # ================= Section 7: Overall Screenshots & 720 px =================
        print('== 7 Responsive 720 px Viewport')
        shot(page, '.k', OUT / 'card-light.png')

        page.set_viewport_size({'width': 720, 'height': 1200})
        page.wait_for_timeout(200)

        ov = page.evaluate('() => { const k = document.querySelector(".k"); return k ? (k.scrollWidth - k.clientWidth) : 0; }')
        check('no horizontal overflow at 720 px', ov <= 0, str(ov))

        fs = page.evaluate('''() => {
            const svgs = [...document.querySelectorAll('.ko-stage svg')];
            if (!svgs.length) return 0;
            const sizes = svgs.flatMap(s => {
                const vb = s.viewBox && s.viewBox.baseVal && s.viewBox.baseVal.width ? s.viewBox.baseVal.width : 1;
                const k = (s.getBoundingClientRect().width / vb) || 1;
                return [...s.querySelectorAll('text')].filter(t => getComputedStyle(t).display !== 'none' && !(t.closest('g') && getComputedStyle(t.closest('g')).display === 'none'))
                  .map(t => parseFloat(getComputedStyle(t).fontSize) * k);
            }).filter(n => !isNaN(n));
            return sizes.length ? Math.min(...sizes) : 12;
        }''')
        check('every SVG label ≥ 12 px at 720 px', fs >= 12, f'{fs:.2f}')
        shot(page, '.k', OUT / 'card-720.png')

        ctx.close()

    browser.close()

check('no console errors or page errors', len(errors) == 0, '; '.join(errors))
n_passed = sum(1 for r in results if r[1])
total = len(results)
print(f'{n_passed}/{total} passed')
sys.exit(0 if n_passed == total else 1)
