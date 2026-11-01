"""ch02 mole-map cell test.

usage: uv run --with playwright python -I colab/tests/ch02_mole-map.py $COLAB_TMP/cells/ch02-mole-map.html <shots-dir>
(build first: python3 tools/build_colab.py ch02 --cell mole-map)
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


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])  # GPU process can stall → rAF never fires → screenshots hang
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        card = page.locator('.k').first

        def val(k):
            return page.input_value(f'input.mm-v[data-k="{k}"]')

        def put(k, v):
            page.fill(f'input.mm-v[data-k="{k}"]', v)

        def on_arrows():
            return sorted(page.eval_on_selector_all('.mm-arrows path.on', 'ps => ps.map(p => p.dataset.arrow)'))

        def clashes():
            return page.locator('[data-clash]').count()

        if scheme == 'dark':
            card.screenshot(path=str(OUT / 'card-dark.png'))
            check('dark: no label clash', clashes() == 0, str(clashes()))
            ctx.close()
            continue

        print('== default: 0.18 g HO2CCO2H')
        mr = page.inner_text('.mm-mr')
        check('Mr(HO2CCO2H) working = 90.0', '2 × 1.0 + 4 × 16.0 + 2 × 12.0 = 90.0' in mr, mr)
        check('n = 0.0020 mol', val('n') == '0.0020', val('n'))
        check('default particle = atoms of C', page.input_value('.mm-kind') == 'el:C')
        check('C atoms = 2.4 × 10²¹', val('part') == '2.4 × 10²¹', val('part'))
        w = page.inner_text('.mm-work')
        check('working shows m ÷ M', '0.18 ÷ 90.0 = 0.0020 mol' in w, w)
        check('working shows × 2 for C atoms', '2 × 0.0020 = 0.0040 mol' in w, w)
        check('arrows: mass-in + 4 outs lit', on_arrows() == sorted(['mass-in', 'gas-out', 'part-out', 'sol-out']), str(on_arrows()))
        check('8 arrow labels', page.locator('.mm-labels text').count() == 8)
        check('every arrow path has its own marker-end',
              page.eval_on_selector_all('.mm-arrows path', 'ps => ps.every(p => /url\\(#mm-a-/.test(p.getAttribute("marker-end")))'))
        # arrows must start/stop just outside the drawn circle (catches a circle moved without its arrows)
        gaps = page.evaluate("""() => { const c=document.querySelector('.mm-core'), X=+c.getAttribute('cx'), Y=+c.getAttribute('cy'), R=+c.getAttribute('r');
          return [...document.querySelectorAll('.mm-arrows path')].map(p => { const L=p.getTotalLength(), a=p.getPointAtLength(0), b=p.getPointAtLength(L);
            return Math.min(Math.hypot(a.x-X,a.y-Y), Math.hypot(b.x-X,b.y-Y)) - R; }); }""")
        check('arrow ends sit 2–12 px outside the n circle', all(2 <= g <= 12 for g in gaps), str([round(g, 1) for g in gaps]))
        boxgap = page.evaluate("""() => { const fo=[...document.querySelectorAll('.mm-map foreignObject')].slice(1).map(f=>({x:+f.getAttribute('x'),y:+f.getAttribute('y'),w:+f.getAttribute('width'),h:+f.getAttribute('height')}));
          return [...document.querySelectorAll('.mm-arrows path')].map(p => { const L=p.getTotalLength(); return [p.getPointAtLength(0), p.getPointAtLength(L)].map(q =>
            Math.min(...fo.map(r => Math.hypot(Math.max(r.x-q.x,0,q.x-r.x-r.w), Math.max(r.y-q.y,0,q.y-r.y-r.h))))); }).map(v => Math.min(...v)); }""")
        check('arrow ends sit 2–12 px outside their box', all(2 <= g <= 12 for g in boxgap), str(boxgap))
        check('part label shows × 2 × L', page.text_content('.mm-labels [data-for="part-out"]') == '× 2 × L')
        check('no label clash (default)', clashes() == 0, str(clashes()))
        lab_px = page.eval_on_selector_all('.mm-labels text', 'ts => Math.min(...ts.map(t => t.getBoundingClientRect().height))')
        check('arrow labels ≥ 12 px tall on screen', lab_px >= 12, str(lab_px))
        card.screenshot(path=str(OUT / 'card-default.png'))
        print('== molecules of HO2CCO2H')
        page.select_option('.mm-kind', 'mol')
        check('molecules = 1.2 × 10²¹', val('part') == '1.2 × 10²¹', val('part'))
        check('part label back to × L', page.text_content('.mm-labels [data-for="part-out"]') == '× L')

        print('== formula parser')
        page.fill('.mm-f', 'CuSO4.5H2O')
        mr = page.inner_text('.mm-mr')
        check('CuSO4.5H2O Mr working', '63.5 + 32.1 + 4 × 16.0 + 5 × 18.0 = 249.6' in mr, mr)
        check('pretty formula CuSO₄·5H₂O', 'CuSO₄·5H₂O' in mr, mr)
        check('mass source kept → n = 0.18 / 249.6 = 7.2 × 10⁻⁴', val('n') == '7.2 × 10⁻⁴', val('n'))
        page.fill('.mm-f', 'CuSO4·5H2O')
        check('· accepted as hydrate dot', '= 249.6' in page.inner_text('.mm-mr'))
        page.click('.mm-pre button[data-f="Mg(OH)2"]')
        mr = page.inner_text('.mm-mr')
        check('Mg(OH)2 → 24.3 + 2 × 16.0 + 2 × 1.0 = 58.3', '24.3 + 2 × 16.0 + 2 × 1.0 = 58.3' in mr, mr)
        check('preset button turns on', 'on' in page.get_attribute('.mm-pre button[data-f="Mg(OH)2"]', 'class'))
        page.fill('.mm-f', 'Ca3(PO4)2')
        check('Ca3(PO4)2 = 310.3', '= 310.3' in page.inner_text('.mm-mr'), page.inner_text('.mm-mr'))
        page.fill('.mm-f', 'Xy2O')
        mr = page.inner_text('.mm-mr')
        check('unknown symbol Xy reported', '不认识' in mr and 'Xy' in mr, mr)
        check('mass source + bad formula → n blank', val('n') == '', val('n'))
        page.fill('.mm-f', 'cuso4')
        check('lowercase start reported', '不认识' in page.inner_text('.mm-mr'))
        page.fill('.mm-f', 'Mg(OH2')
        check('unbalanced bracket reported', '括号' in page.inner_text('.mm-mr'), page.inner_text('.mm-mr'))
        page.fill('.mm-f', 'Tc2O7')
        check('Tc has no Ar', '没有给' in page.inner_text('.mm-mr'), page.inner_text('.mm-mr'))
        check('no console error so far', not errors, '; '.join(errors))

        print('== gas volume 9.6 dm³ ↔ 0.40 mol')
        page.fill('.mm-f', 'CO2')
        put('gas', '9.6')
        check('9.6 dm³ → n = 0.40', val('n') == '0.40', val('n'))
        check('mass CO2 = 0.40 × 44.0 = 18 g', val('mass') == '18', val('mass'))
        check('arrows: gas-in lit, mass-in not', 'gas-in' in on_arrows() and 'mass-in' not in on_arrows() and 'gas-out' not in on_arrows(), str(on_arrows()))
        check('gas box marked as source', 'src' in page.get_attribute('[data-box="gas"]', 'class'))
        check('working 9.6 ÷ 24.0', '9.6 ÷ 24.0 = 0.40 mol' in page.inner_text('.mm-work'))
        check('no label clash (gas source)', clashes() == 0, str(clashes()))
        put('n', '0.40')
        check('0.40 mol → 9.6 dm³', val('gas') == '9.6', val('gas'))
        check('n source: all 4 out arrows, no in', on_arrows() == sorted(['mass-out', 'gas-out', 'part-out', 'sol-out']), str(on_arrows()))

        print('== particles → n')
        page.select_option('.mm-kind', 'mol')
        put('part', '6.02 x 10^23')
        check('6.02 x 10^23 molecules → 1.00 mol', val('n') == '1.00', val('n'))
        put('part', '1.204e24')
        check('1.204e24 → 2.000 mol', val('n') == '2.000', val('n'))
        put('part', '3.01 × 10²³')
        check('superscript input → 0.500 mol', val('n') == '0.500', val('n'))
        page.select_option('.mm-kind', 'el:O')
        check('3.01 × 10²³ O atoms → 0.250 mol CO2', val('n') == '0.250', val('n'))
        check('part-in label ÷ (2 × L)', page.text_content('.mm-labels [data-for="part-in"]') == '÷ (2 × L)')
        put('part', 'abc')
        check('bad number flagged', 'bad' in page.get_attribute('input.mm-v[data-k="part"]', 'class') and '看不懂' in page.inner_text('.mm-work'))

        print('== solution')
        page.fill('.mm-f', 'NaCl')
        put('c', '0.100'); put('vol', '25.0')
        check('0.100 × 25.0 / 1000 = 0.00250 mol', val('n') == '0.00250', val('n'))
        check('NaCl mass 0.146 g', val('mass') == '0.146', val('mass'))
        check('sol-in lit', 'sol-in' in on_arrows(), str(on_arrows()))
        put('mass', '5.85')
        check('5.85 g NaCl in 25.0 cm³ → 4.00 mol dm⁻³', val('c') == '4.00', val('c'))
        put('vol', '250')
        check('changing V keeps mass as source → c = 0.400', val('c') == '0.400' and val('mass') == '5.85', val('c'))
        check('no label clash (end)', clashes() == 0, str(clashes()))

        print('== back to the textbook example, close-ups')
        page.fill('.mm-f', 'HO2CCO2H'); put('mass', '0.18'); page.select_option('.mm-kind', 'el:C')
        check('example again: C atoms 2.4 × 10²¹', val('part') == '2.4 × 10²¹', val('part'))
        mb = page.locator('.mm-map').bounding_box()
        sc = mb['width'] / 808
        for name, (x, y, w_, h) in {'zoom-left': (0, 170, 420, 170), 'zoom-right': (360, 170, 448, 170),
                                    'zoom-top': (204, 0, 400, 200), 'zoom-bottom': (204, 300, 400, 200)}.items():
            page.screenshot(path=str(OUT / f'{name}.png'), clip={'x': mb['x'] + x * sc, 'y': mb['y'] + y * sc, 'width': w_ * sc, 'height': h * sc})
        page.locator('.mm-mr').screenshot(path=str(OUT / 'zoom-mr.png'))
        page.locator('.mm-work').screenshot(path=str(OUT / 'zoom-work.png'))

        print('== narrow (700 px)')
        page.set_viewport_size({'width': 720, 'height': 1100}); page.wait_for_timeout(200)
        ov = page.evaluate('() => { const k=document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('no horizontal overflow at 720 px', ov <= 0, str(ov))
        fo = page.evaluate('''() => [...document.querySelectorAll('.mm-map foreignObject > div')].map(d => d.scrollHeight - d.clientHeight + d.scrollWidth - d.clientWidth)''')
        check('box contents fit their boxes', max(fo) <= 0, str(fo))
        card.screenshot(path=str(OUT / 'card-720.png'))
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
