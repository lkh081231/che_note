"""ch02 combustion cell test.

usage: uv run --with playwright python -I colab/tests/ch02_combustion.py $COLAB_TMP/cells/ch02-combustion.html <shots-dir>
(build first: python3 tools/build_colab.py ch02 --cell combustion)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


# every <text> in the bar chart: no two overlap; outside labels never sit on a bar segment
GEOM = """() => {
  const svg = document.querySelector('.cb-bars');
  const ts = [...svg.querySelectorAll('text')].filter(t => t.textContent);
  const bb = ts.map(t => { const b = t.getBBox(); return {t: t.textContent, x: b.x, y: b.y, w: b.width, h: b.height}; });
  const hit = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
  const over = [];
  for (let i = 0; i < bb.length; i++) for (let j = i + 1; j < bb.length; j++) if (hit(bb[i], bb[j])) over.push(bb[i].t + ' / ' + bb[j].t);
  const segs = [...svg.querySelectorAll('rect.seg')].map(r => ({x: +r.getAttribute('x'), y: +r.getAttribute('y'), w: +r.getAttribute('width'), h: +r.getAttribute('height')}));
  /* a label may lie inside exactly one segment (its own, fully contained) or touch none */
  const bad = [];
  bb.forEach(b => {
    const hs = segs.filter(s => hit(b, s));
    if (!hs.length) return;
    const inside = hs.length === 1 && b.x >= hs[0].x && b.x + b.w <= hs[0].x + hs[0].w && b.y >= hs[0].y && b.y + b.h <= hs[0].y + hs[0].h;
    if (!inside) bad.push(b.t);
  });
  const vb = svg.viewBox.baseVal, out = bb.filter(b => b.x < vb.x || b.y < vb.y || b.x + b.w > vb.x + vb.width || b.y + b.h > vb.y + vb.height).map(b => b.t);
  return {over, bad, out, n: bb.length};
}"""

# each leader line: one end on the bar edge, the other end within 3 px of its label box
LEADS = """() => {
  const svg = document.querySelector('.cb-bars');
  const ts = [...svg.querySelectorAll('text')].map(t => t.getBBox());
  return [...svg.querySelectorAll('line.lead')].map(l => {
    const x = +l.getAttribute('x2'), y = +l.getAttribute('y2');
    return Math.min(...ts.map(b => Math.hypot(Math.max(b.x - x, 0, x - b.x - b.width), Math.max(b.y - y, 0, y - b.y - b.height))));
  });
}"""


def shot(page, loc, path):
    """clip screenshot: element.screenshot() waits on rAF 'stable' checks that hang when the box is busy"""
    bb = loc.bounding_box(); sy = page.evaluate('scrollY'); sx = page.evaluate('scrollX')
    page.screenshot(path=str(path), full_page=True, clip={'x': bb['x'] + sx, 'y': bb['y'] + sy, 'width': bb['width'], 'height': bb['height']})


def geom_ok(page, tag):
    g = page.evaluate(GEOM)
    check(f'{tag}: bar labels do not overlap each other', not g['over'], str(g['over']))
    check(f'{tag}: no label sits across a bar segment', not g['bad'], str(g['bad']))
    check(f'{tag}: labels inside the viewBox', not g['out'], str(g['out']))
    check(f'{tag}: no data-clash', page.locator('[data-clash]').count() == 0, str(page.locator('[data-clash]').count()))
    ld = page.evaluate(LEADS)
    check(f'{tag}: leader lines end ≤ 3 px from a label', all(d <= 3 for d in ld), str(ld))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])  # GPU headless hangs screenshots here
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        card = page.locator('.k').first

        def lab(t):
            return page.locator(f'.cb-bars text[data-lab="{t}"]').count()

        if scheme == 'dark':
            shot(page, card, str(OUT / 'card-dark.png'))
            geom_ok(page, 'dark')
            page.click('button[data-tab="rev"]')
            shot(page, card, str(OUT / 'card-dark-rev.png'))
            ctx.close()
            continue

        print('== default: C3H8 50 cm³, exact O2')
        check('C₃H₈ preset lit', 'on' in (page.get_attribute('.cb-pre button[data-f="C₃H₈"]', 'class') or ''))
        check('O₂ needed 250', page.inner_text('.cb-need') == '250 cm³', page.inner_text('.cb-need'))
        check('CO₂ 150', page.inner_text('.cb-co2') == '150 cm³', page.inner_text('.cb-co2'))
        w = page.inner_text('.cb-work')
        check('working 50 × (3 + 8/4) = 50 × 5', '50 × (3 + 8/4) = 50 × 5 = 250' in w, w)
        check('contraction 300 − 150 = 150', page.inner_text('.cb-con') == '150 cm³', page.inner_text('.cb-con'))
        eq = page.inner_text('.cb-eq')
        check('equation C₃H₈(g) + 5O₂(g) → 3CO₂(g) + 4H₂O(l)', 'C3H8(g) + 5O₂(g) → 3CO₂(g) + 4H₂O(l)' in eq.replace('\n', '') or
              'C₃H₈(g) + 5O₂(g) → 3CO₂(g) + 4H₂O(l)' in eq, eq)
        check('ratio 1 : 5 : 3', page.inner_text('.cb-ratio') == '1 : 5 : 3', page.inner_text('.cb-ratio'))
        check('bar labels present', lab('C₃H₈ 50 cm³') and lab('O₂ 250 cm³') and lab('CO₂ 150 cm³') and lab('contraction 150 cm³') and lab('H2O'))
        # bar lengths proportional: before (300) is full width, after CO₂ = half
        ws = page.evaluate("() => Object.fromEntries([...document.querySelectorAll('.cb-bars rect.seg')].map(r => [r.dataset.seg || 'gone', +r.getAttribute('width')]))")
        check('bar widths: C₃H₈ : O₂ : CO₂ = 50 : 250 : 150', abs(ws['C₃H₈ 50'] * 5 - ws['O₂ 250']) < 0.5 and abs(ws['C₃H₈ 50'] * 3 - ws['CO₂ 150']) < 0.5, str(ws))
        # H₂O tick sits exactly at the end of the CO₂ segment
        h = page.evaluate("""() => { const r=document.querySelector('.cb-bars rect[data-seg^="CO₂"]'), l=document.querySelector('.cb-bars line.h2o');
            return Math.abs(+r.getAttribute('x') + +r.getAttribute('width') - +l.getAttribute('x1')); }""")
        check('H₂O tick at end of CO₂ bar', h < 0.5, str(h))
        geom_ok(page, 'default')
        fs = page.eval_on_selector_all('.cb-bars text', 'ts => Math.min(...ts.map(t => parseFloat(getComputedStyle(t).fontSize) * t.ownerSVGElement.getBoundingClientRect().width / 820))')
        check('bar text ≥ 12 px rendered (1000 px)', fs >= 12, str(fs))
        shot(page, card, str(OUT / 'card-default.png'))
        shot(page, page.locator('.cb-bars'), str(OUT / 'zoom-bars.png'))
        shot(page, page.locator('.cb-eq'), str(OUT / 'zoom-eq.png'))
        shot(page, page.locator('.cb-work'), str(OUT / 'zoom-work.png'))

        print('== excess O2 300')
        page.check('.cb-ex')
        check('O₂ input enabled', page.is_enabled('.cb-o2'))
        page.fill('.cb-o2', '300')
        check('O₂ left 50', page.inner_text('.cb-left') == '50 cm³', page.inner_text('.cb-left'))
        check('after 150 + 50 = 200', page.inner_text('.cb-after') == '200 cm³', page.inner_text('.cb-after'))
        check('contraction still 150', page.inner_text('.cb-con') == '150 cm³', page.inner_text('.cb-con'))
        check('O₂ left segment drawn', lab('O₂ left 50 cm³') == 1)
        geom_ok(page, 'excess')
        shot(page, page.locator('.cb-bars'), str(OUT / 'zoom-bars-excess.png'))
        page.fill('.cb-o2', '200')
        check('too little O₂ → incomplete combustion message', 'incomplete combustion' in page.inner_text('.cb-work'))
        check('no bars when O₂ insufficient', page.locator('.cb-bars rect.seg').count() == 0)
        page.fill('.cb-o2', '1000')
        geom_ok(page, 'big excess (narrow segments)')
        shot(page, page.locator('.cb-bars'), str(OUT / 'zoom-bars-bigexcess.png'))
        page.uncheck('.cb-ex')

        print('== fractional coefficient C2H6, CH4, y options')
        page.click('.cb-pre button[data-f="C₂H₆"]')
        eq = page.inner_text('.cb-eq')
        check('C₂H₆ + 3½O₂', '3½O₂(g)' in eq, eq)
        check('× 2 form 2C₂H₆ + 7O₂ → 4CO₂ + 6H₂O', '7O₂ → 4CO₂ + 6H₂O' in eq, eq)
        check('C₂H₆ 50 → O₂ 175', page.inner_text('.cb-need') == '175 cm³', page.inner_text('.cb-need'))
        geom_ok(page, 'C2H6')
        shot(page, page.locator('.cb-eq'), str(OUT / 'zoom-eq-c2h6.png'))
        page.fill('.cb-x', '1')
        opts = page.eval_on_selector_all('.cb-y option', 'os => os.map(o => o.value)')
        check('x = 1 → y only 4', opts == ['4'], str(opts))
        eqn = page.inner_text('.cb-eq').translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789'))
        check('CH₄ equation', 'CH4(g) + 2O2(g) → CO2(g) + 2H2O(l)' in eqn, eqn)
        geom_ok(page, 'CH4')
        shot(page, page.locator('.cb-bars'), str(OUT / 'zoom-bars-ch4.png'))
        page.fill('.cb-x', '6')
        opts = page.eval_on_selector_all('.cb-y option', 'os => os.map(o => o.value)')
        check('x = 6 → y 6…14 even', opts == ['6', '8', '10', '12', '14'], str(opts))
        check('C₅+ liquid note shown', 'liquid' in page.inner_text('.cb-note'))
        page.fill('.cb-x', '9')
        check('x = 9 rejected', 'bad' in page.get_attribute('.cb-x', 'class'))
        page.fill('.cb-x', '3'); page.select_option('.cb-y', '8')
        page.fill('.cb-v', 'abc')
        check('bad volume flagged', '看不懂' in page.inner_text('.cb-work'))
        page.fill('.cb-v', '50')

        print('== n ↔ V: 0.50 mol C2H4 → 24 dm³ CO2')
        page.click('.cb-pre button[data-f="C₂H₄"]')
        page.fill('.cb-n', '0.50')
        check('V(C₂H₄) = 12 dm³', page.input_value('.cb-vd') == '12', page.input_value('.cb-vd'))
        check('V(CO₂) = 24 dm³', page.inner_text('.cb-vco2') == '24 dm³', page.inner_text('.cb-vco2'))
        check('V(O₂) = 36 dm³', page.inner_text('.cb-vo2') == '36 dm³', page.inner_text('.cb-vo2'))
        check('working n(CO₂) = 2 × 0.50 = 1.0 mol', '2 × 0.50 = 1.0 mol' in page.inner_text('.cb-nv'), page.inner_text('.cb-nv'))
        shot(page, page.locator('.cb-nv'), str(OUT / 'zoom-nv.png'))   # the 0.50 mol C₂H₄ pass-line case
        page.fill('.cb-vd', '6.00')
        check('6.00 dm³ → 0.250 mol', page.input_value('.cb-n') == '0.250', page.input_value('.cb-n'))
        check('pV = nRT hint present', 'pV = nRT' in page.inner_text('[data-pane="fwd"]'))
        shot(page, page.locator('.cb-nv'), str(OUT / 'zoom-nv-6dm3.png'))

        print('== reverse: 50 / 250 / 150 → C3H8')
        page.click('button[data-tab="rev"]')
        check('x = 3', page.inner_text('.cb-rx') == '3', page.inner_text('.cb-rx'))
        check('y = 8', page.inner_text('.cb-ry') == '8', page.inner_text('.cb-ry'))
        check('formula C₃H₈', page.inner_text('.cb-rf').replace('\n', '') in ('C3H8', 'C₃H₈'), page.inner_text('.cb-rf'))
        check('ratio 1 : 5 : 3 in working', '1 : 5 : 3' in page.inner_text('.cb-rwork'))
        page.fill('.cb-rh', '20'); page.fill('.cb-ro', '60'); page.fill('.cb-rc', '40')
        check('20/60/40 → C₂H₄', page.inner_text('.cb-rx') == '2' and page.inner_text('.cb-ry') == '4', page.inner_text('.cb-rwork'))
        page.fill('.cb-rc', '45')
        check('nonsense data flagged', '得不到' in page.inner_text('.cb-rwork'))
        page.fill('.cb-rh', '50'); page.fill('.cb-ro', '250'); page.fill('.cb-rc', '150')
        shot(page, page.locator('.cb-rwork'), str(OUT / 'zoom-rwork.png'))

        print('== practice question')
        seen = set()
        for i in range(8):
            f = page.get_attribute('.cb-q', 'data-f'); seen.add(f)
            ax, ay = page.get_attribute('.cb-fx', 'data-ans'), page.get_attribute('.cb-fy', 'data-ans')
            expect = 'C' + ('' if ax == '1' else ax.translate(str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))) + 'H' + ay.translate(str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉'))
            if f != expect:
                check(f'q{i}: data-ans matches formula', False, f'{f} vs {expect}')
            # the numbers in the question must actually give that answer
            qt = page.inner_text('.cb-q .qt')
            nums = [float(t) for t in __import__('re').findall(r'(\d+(?:\.\d+)?) cm³', qt)]
            if len(nums) == 3:
                V, O, C = nums
            else:
                V, T, P, Lf = nums; C, O = P - Lf, T - Lf
            x, y = C / V, 4 * (O / V - C / V)
            if (round(x), round(y)) != (int(ax), int(ay)):
                check(f'q{i}: numbers give the answer', False, f'{qt} → {x},{y} vs {ax},{ay}')
            if i == 0:
                page.fill('.cb-fx', '9')
                check('wrong x turns red', 'badv' in page.get_attribute('.cb-fx', 'class'))
            page.fill('.cb-fx', ax); page.fill('.cb-fy', ay)
            if 'good' not in page.get_attribute('.cb-fx', 'class') or 'good' not in page.get_attribute('.cb-fy', 'class'):
                check(f'q{i}: correct answers turn green', False)
            if i == 0:
                page.click('.cb-q button.reveal')
                check('solution revealed', page.is_visible('.cb-q .ans'))
                shot(page, page.locator('.cb-q'), str(OUT / 'zoom-practice.png'))
                shot(page, card, str(OUT / 'card-rev.png'))
            page.click('.cb-new')
        check('8 practice questions consistent & green on correct answer', not [r for r in results if r[0].startswith('q') and not r[1]])
        check('questions vary', len(seen) >= 3, str(seen))

        print('== narrow (720 px)')
        page.click('button[data-tab="fwd"]')
        page.click('.cb-pre button[data-f="C₃H₈"]'); page.check('.cb-ex'); page.fill('.cb-o2', '300')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(200)
        ov = page.evaluate('() => { const k=document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('no horizontal overflow at 720 px', ov <= 0, str(ov))
        fs = page.eval_on_selector_all('.cb-bars text', 'ts => Math.min(...ts.map(t => t.getBoundingClientRect().height))')
        fs2 = page.eval_on_selector_all('.cb-bars text', 'ts => Math.min(...ts.map(t => parseFloat(getComputedStyle(t).fontSize) * t.ownerSVGElement.getBoundingClientRect().width / 820))')
        check('bar text ≥ 12 px rendered at 720 px', fs2 >= 12, f'font {fs2:.1f}px, box {fs:.1f}px')
        shot(page, card, str(OUT / 'card-720.png'))
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
