"""ch02 limiting cell test.

usage: uv run --with playwright python -I colab/tests/ch02_limiting.py $COLAB_TMP/cells/ch02-limiting.html <shots-dir>
(build first: python3 tools/build_colab.py ch02 --cell limiting)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []


def shot(page, sel, path):
    """element screenshot via a page clip: Locator.screenshot waits for 'stable' (two rAFs), which
    hangs when several headless Chromes share the machine"""
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])  # without it screenshots hang (GPU compositor never delivers a frame)
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        card = page.locator('.k').first

        def clashes():
            return page.locator('[data-clash]').count()

        def outside():
            """figure labels sticking out of the viewBox (K.label only knows the viewBox of the element it is given)"""
            return page.evaluate('''() => { const s = document.querySelector('.lr-fig'), v = s.viewBox.baseVal;
                return [...s.querySelectorAll('text')].filter(t => { const b = t.getBBox();
                  return b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5; })
                  .map(t => t.textContent); }''')

        def work():
            return page.inner_text('.lr-work')

        def lim():
            """which reactant row the figure marks as limiting: 0, 1, 'tie' or None"""
            if page.locator('.lr-fig [data-role="lim-0"]').count():
                return 0
            if page.locator('.lr-fig [data-role="lim-1"]').count():
                return 1
            return 'tie' if '恰好按 mole ratio' in work() else None

        def width(sel):
            return page.eval_on_selector(sel, 'e => +e.getAttribute("width")')

        def pct():
            return page.inner_text('.lr-pct') if page.locator('.lr-pct').count() else ''

        if scheme == 'dark':
            shot(page, '.k', str(OUT / 'card-dark.png'))
            check('dark: no label clash', clashes() == 0, str(clashes()))
            ctx.close()
            continue

        print('== default: 79.8 g Fe2O3 + 9.36 g C')
        w = work()
        check('preset Fe2O3 on', 'on' in page.get_attribute('.lr-pick button[data-pre="fe"]', 'class'))
        check('n(Fe2O3) = 79.8 ÷ 159.6 = 0.500', '79.8 ÷ 159.6 = 0.500 mol' in w, w)
        check('n(C) = 9.36 ÷ 12.0 = 0.780', '9.36 ÷ 12.0 = 0.780 mol' in w, w)
        check('needs 0.500 × 3/2 = 0.750 mol C', '0.500 × 3/2 = 0.750 mol C' in w, w)
        check('Fe2O3 is the limiting reagent', 'Fe₂O₃ is the limiting reagent' in w and 'C in excess' in w, w)
        check('excess C 0.030 mol', '0.780 − 0.750 = 0.030 mol' in w, w)
        check('excess C 0.36 g', '0.030 × 12.0 = 0.36 g' in w, w)
        check('CO2 = 0.750 × 44.0 = 33.0 g', '0.750 × 44.0 = 33.0 g' in w, w)
        check('Fe = 1.00 mol → 55.8 g', '0.500 × 4/2 = 1.00 mol' in w and '1.00 × 55.8 = 55.8 g' in w, w)
        check('Mr working Fe2O3 in header', '2 × 55.8 + 3 × 16.0 = 159.6' in page.inner_text('.lr-mr'))
        check('figure: Fe2O3 marked limiting', lim() == 0, str(lim()))
        check('figure: excess label on C row says 0.030 mol', '0.030 mol' in page.text_content('.lr-fig [data-role="exc-1"]'))
        check('figure: C has a leftover segment, Fe2O3 none',
              page.locator('[data-bar="left-1"]').count() == 1 and page.locator('[data-bar="left-0"]').count() == 0)
        uw = [width(f'[data-bar="{k}"]') for k in ('used-0', 'used-1', 'prod-0', 'prod-1')]
        check('used segments and product bars all end at the same cut', max(uw) - min(uw) < 0.01, str(uw))
        check('C bar (n ÷ 3 = 0.260) longer than Fe2O3 bar (0.250)',
              abs((width('[data-bar="used-1"]') + width('[data-bar="left-1"]')) / width('[data-bar="used-0"]') - 0.26 / 0.25) < 0.01)
        check('CO2 bar label 33.0 g', '33.0 g' in page.text_content('.lr-fig [data-role="prod-1"]'))
        check('no label clash (default)', clashes() == 0, str(clashes()))
        check('labels inside the figure (default)', not outside(), str(outside()))
        lab_px = page.eval_on_selector_all('.lr-fig text', 'ts => Math.min(...ts.map(t => t.getBoundingClientRect().height))')
        check('figure labels ≥ 12 px tall on screen', lab_px >= 12, str(lab_px))
        check('default yield CO2 30.0 / 33.0 = 90.9%', pct() == '90.9%', pct())
        shot(page, '.k', str(OUT / 'card-default.png'))
        fb = page.eval_on_selector('.lr-fig', 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width}; }')
        sc = fb['width'] / 860
        for name, (x, y, w_, h) in {'zoom-reactants': (0, 0, 520, 210), 'zoom-cut': (300, 0, 560, 210),
                                    'zoom-products': (0, 190, 600, 140)}.items():
            page.screenshot(path=str(OUT / f'{name}.png'), clip={'x': fb['x'] + x * sc, 'y': fb['y'] + y * sc, 'width': w_ * sc, 'height': h * sc}, full_page=True)
        shot(page, '.lr-work', str(OUT / 'zoom-work.png'))
        shot(page, '.lr-yield', str(OUT / 'zoom-yield.png'))
        shot(page, '.lr-eqcard', str(OUT / 'zoom-eq.png'))

        print('== keyboard on the C slider across the stoichiometric point (9.00 g)')
        sl = page.locator('.lr-c input[type=range][data-r="1"]')
        sl.focus()
        seen = []
        for _ in range(40):
            page.keyboard.press('ArrowLeft')
            v = page.input_value('.lr-c input[type=text][data-r="1"]')
            seen.append((v, lim()))
        st = dict(seen)
        check('slider moves the text box in 0.01 steps', '9.00' in st and '8.99' in st, str(seen[:3]))
        check('9.01 g C → Fe2O3 still limiting', st.get('9.01') == 0, str(st.get('9.01')))
        check('9.00 g C → exactly stoichiometric', st.get('9.00') == 'tie', str(st.get('9.00')))
        check('8.99 g C → C becomes limiting', st.get('8.99') == 1, str(st.get('8.99')))
        flips = sum(1 for a, c in zip(seen, seen[1:]) if a[1] != c[1])
        check('limiting label switches only at the stoichiometric point', flips == 2, str(seen))
        w = work()
        check('C limiting → Fe2O3 in excess in working', 'C is the limiting reagent' in w and 'Fe₂O₃ in excess' in w, w)
        check('C limiting → excess shown on Fe2O3 row', page.locator('[data-role="exc-0"]').count() == 1)
        page.fill('.lr-c input[type=text][data-r="1"]', '9.00')
        page.wait_for_timeout(50)
        check('tie: no leftover segment on either bar', page.locator('[data-bar^="left-"]').count() == 0)
        check('no label clash (tie)', clashes() == 0, str(clashes()))
        check('labels inside the figure (tie)', not outside(), str(outside()))
        shot(page, '.lr-fig', str(OUT / 'fig-tie.png'))

        print('== mouse drag')
        bb = sl.bounding_box()
        page.mouse.move(bb['x'] + bb['width'] * 0.36, bb['y'] + bb['height'] / 2)
        page.mouse.down()
        page.mouse.move(bb['x'] + bb['width'] * 0.15, bb['y'] + bb['height'] / 2, steps=8)
        page.mouse.up()
        v = float(page.input_value('.lr-c input[type=text][data-r="1"]'))
        check('drag C to the left → small mass (0 < m < 6)', 0 < v < 6, str(v))
        check('drag left → C limiting', lim() == 1, str(lim()))
        page.mouse.move(bb['x'] + bb['width'] * 0.15, bb['y'] + bb['height'] / 2)
        page.mouse.down()
        page.mouse.move(bb['x'] + bb['width'] - 4, bb['y'] + bb['height'] / 2, steps=8)
        page.mouse.up()
        v = float(page.input_value('.lr-c input[type=text][data-r="1"]'))
        check('drag C to the right end → ~25 g', v > 24, str(v))
        check('drag right → Fe2O3 limiting again', lim() == 0, str(lim()))
        check('no label clash (C 25 g)', clashes() == 0, str(clashes()))
        check('labels inside the figure (C 25 g)', not outside(), str(outside()))
        shot(page, '.lr-fig', str(OUT / 'fig-c-excess-big.png'))
        page.fill('.lr-c input[type=text][data-r="0"]', '200')
        check('200 g Fe2O3 + 25 g C → Fe2O3 still limiting (0.627 < 0.694)', lim() == 0, str(lim()))
        page.fill('.lr-c input[type=text][data-r="1"]', '5.00')
        check('200 g Fe2O3 + 5.00 g C → C limiting', lim() == 1, str(lim()))
        check('no label clash (Fe2O3 200 g)', clashes() == 0, str(clashes()))
        check('labels inside the figure (Fe2O3 200 g)', not outside(), str(outside()))
        shot(page, '.lr-fig', str(OUT / 'fig-fe-excess.png'))

        print('== AlCl3 preset')
        page.click('.lr-pick button[data-pre="al"]')
        w = work()
        check('18 ÷ 27.0 = 0.667 mol Al', '18 ÷ 27.0 = 0.667 mol' in w, w)
        check('Al limiting (excess Cl2)', 'Al is the limiting reagent' in w and lim() == 0, w)
        check('AlCl3 theoretical 89.0 g', '0.667 × 133.5 = 89.0 g' in w, w)
        check('AlCl3 Mr working 27.0 + 3 × 35.5 = 133.5', '27.0 + 3 × 35.5 = 133.5' in page.inner_text('.lr-mr'))
        check('actual 71.0 → 79.8%', pct() == '79.8%', pct())
        check('yield working written out', '71.0 ÷ 89.0 × 100% = 79.8%' in page.inner_text('.lr-yield'), page.inner_text('.lr-yield'))
        page.fill('.lr-act', '95')
        check('actual > theoretical → warning', pct() == '107%' and '超过 100%' in page.inner_text('.lr-yield'), page.inner_text('.lr-yield'))
        page.fill('.lr-act', 'abc')
        check('bad actual yield flagged', 'bad' in page.get_attribute('.lr-act', 'class') and '≥ 0' in page.inner_text('.lr-yield'))
        page.fill('.lr-act', '71.0')
        check('no label clash (Al)', clashes() == 0, str(clashes()))
        check('labels inside the figure (Al)', not outside(), str(outside()))
        shot(page, '.k', str(OUT / 'card-al.png'))

        print('== SrO preset')
        page.click('.lr-pick button[data-pre="sr"]')
        w = work()
        check('SrO limiting', 'SrO is the limiting reagent' in w and lim() == 0, w)
        check('Sr = 42.3 g', '× 87.6 = 42.3 g' in w, w)
        check('n(Sr) = 0.965 × 3/6', '0.965 × 3/6 = 0.483 mol' in w, w)
        check('two products drawn', page.locator('[data-bar^="prod-"]').count() == 2)
        check('yield select lists Sr and Sr3Al2O6', page.eval_on_selector_all('.lr-yp option', 'os => os.map(o => o.textContent)') == ['Sr', 'Sr₃Al₂O₆'])
        page.select_option('.lr-yp', '1')
        check('switching yield product updates theoretical', 'Sr₃Al₂O₆' in page.inner_text('.lr-yield'))
        check('no label clash (Sr)', clashes() == 0, str(clashes()))
        check('labels inside the figure (Sr)', not outside(), str(outside()))
        shot(page, '.lr-fig', str(OUT / 'fig-sr.png'))

        print('== Mg preset')
        page.click('.lr-pick button[data-pre="mg"]')
        w = work()
        check('Mg 0.100 mol needs 0.100 × 1/2 = 0.0500 O2', '0.100 × 1/2 = 0.0500 mol O₂' in w, w)
        check('Mg limiting, MgO 4.03 g', 'Mg is the limiting reagent' in w and '4.03 g' in w, w)
        page.fill('.lr-c input[type=text][data-r="1"]', '1.60')
        check('1.60 g O2 → exactly stoichiometric', lim() == 'tie', str(lim()))
        check('slider follows the text box', abs(float(page.input_value('.lr-c input[type=range][data-r="1"]')) - 1.6) < 1e-9)
        page.fill('.lr-c input[type=text][data-r="1"]', '0')
        check('0 g O2 → no reaction', '不发生' in work(), work())
        page.fill('.lr-c input[type=text][data-r="1"]', '-2')
        check('negative mass flagged', 'bad' in page.get_attribute('.lr-c input[type=text][data-r="1"]', 'class') and '≥ 0' in work())
        page.fill('.lr-c input[type=text][data-r="1"]', '2.00')
        check('no label clash (Mg)', clashes() == 0, str(clashes()))
        check('labels inside the figure (Mg)', not outside(), str(outside()))
        check('no console error so far', not errors, '; '.join(errors))

        print('== narrow (720 px)')
        page.click('.lr-pick button[data-pre="fe"]')
        page.set_viewport_size({'width': 720, 'height': 1200}); page.wait_for_timeout(200)
        ov = page.evaluate('() => { const k=document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('no horizontal overflow at 720 px', ov <= 0, str(ov))
        fs = page.evaluate('''() => { const s = document.querySelector('.lr-fig'), k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k)); }''')
        check('figure font size (CSS px × rendered / viewBox width) ≥ 12 at 720 px', fs >= 12, f'{fs:.2f}')
        shot(page, '.k', str(OUT / 'card-720.png'))
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
