"""ch02 titration cell test.

usage: uv run --with playwright python -I colab/tests/ch02_titration.py $COLAB_TMP/cells/ch02-titration.html <shots-dir>
(build first: python3 tools/build_colab.py ch02 --cell titration)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
VBW = 780


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


# every back-calc arrow must start and stop just outside a mol label; forward arrows just outside a vessel
GEOM = """() => {
  const boxes = [...document.querySelectorAll('.tt-labels text.mol:not(.hid)')].map(t => t.getBBox());
  const d = (q, b) => Math.hypot(Math.max(b.x - q.x, 0, q.x - b.x - b.width), Math.max(b.y - q.y, 0, q.y - b.y - b.height));
  return [...document.querySelectorAll('.tt-wires path.back:not(.hid):not([data-w^=lg])')].map(p => {
    const L = p.getTotalLength(), a = p.getPointAtLength(0), z = p.getPointAtLength(L);
    return { id: p.dataset.w, len: Math.round(L), start: Math.min(...boxes.map(b => d(a, b))), end: Math.min(...boxes.map(b => d(z, b))),
             marker: p.getAttribute('marker-end') };
  });
}"""
FWD = """() => [...document.querySelectorAll('.tt-wires path.fwd:not([data-w^=lg])')].map(p => {
  const L = p.getTotalLength(); return { id: p.dataset.w, len: Math.round(L), marker: p.getAttribute('marker-end') }; })"""


with sync_playwright() as p:
    # without --disable-gpu this chromium (156) never fires rAF headless → every screenshot times out
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1500}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        card = page.locator('.k').first

        def shot(loc, name):
            # locator.screenshot waits for 'stable' via rAF, which stalls in this headless setup; clip instead
            bb = loc.bounding_box(); sx, sy = page.evaluate('() => [scrollX, scrollY]')
            bb = {'x': bb['x'] + sx, 'y': bb['y'] + sy, 'width': bb['width'], 'height': bb['height']}
            page.screenshot(path=str(OUT / name), clip=bb, full_page=True)

        def clashes():
            return page.locator('[data-clash]').count()

        def work():
            return page.inner_text('.tt-work')

        def labels():
            return page.eval_on_selector_all('.tt-labels text', 'ts => ts.map(t => t.textContent)')

        def put(k, v):
            page.fill(f'input.tt-v[data-k="{k}"]', v)

        def preset(i):
            page.click(f'.tt-pre button[data-pre="{i}"]')

        def geom(tag):
            g = page.evaluate(GEOM)
            check(f'{tag}: back arrows start 4–12 px outside a mol label', g and all(4 <= a['start'] <= 12 for a in g), str(g))
            check(f'{tag}: back arrows end 4–12 px outside a mol label', g and all(4 <= a['end'] <= 12 for a in g), str(g))
            check(f'{tag}: back arrows have a visible shaft (≥ 30)', all(a['len'] >= 30 for a in g), str([a['len'] for a in g]))
            check(f'{tag}: every back arrow has its own marker-end', all(a['marker'] == 'url(#tt-a-back)' for a in g))
            f = page.evaluate(FWD)
            check(f'{tag}: forward arrows ≥ 30 long with marker', all(a['len'] >= 30 and a['marker'] == 'url(#tt-a-fwd)' for a in f), str(f))
            check(f'{tag}: no label clash', clashes() == 0, str(clashes()))

        if scheme == 'dark':
            for pid in ('tab', 'mn'):
                preset(pid)
                check(f'dark {pid}: no label clash', clashes() == 0, str(clashes()))
                shot(card, f'card-dark-{pid}.png')
            ctx.close()
            continue

        print('== default: vitamin C tablet (9701/21 s25 Q4)')
        check('default preset is the tablet', 'on' in page.get_attribute('.tt-pre button[data-pre="tab"]', 'class'))
        check('inputs keep written digits', [page.input_value(f'input.tt-v[data-k="{k}"]') for k in ('ct', 'vt', 'v1', 'v2', 'mr')]
              == ['5.00 × 10⁻⁴', '28.40', '200.0', '5.00', '176'])
        w = work()
        check('step 1 n(I2) = 1.42 × 10⁻⁵', '5.00 × 10⁻⁴ × 28.40 ÷ 1000 = 1.42 × 10⁻⁵ mol' in w, w)
        check('dilution factor explicit: 200.0 / 5.00 = 40', 'dilution factor = V₁ / V₂ = 200.0 / 5.00 = 40' in w, w)
        check('n in 200.0 cm³ = 5.68 × 10⁻⁴', '× 200.0/5.00 = 5.68 × 10⁻⁴ mol' in w, w)
        check('mass = 0.099968 → 0.100 g', '5.68 × 10⁻⁴ × 176 = 0.099968 → 0.100 g' in w, w)
        L = labels()
        check('diagram shows burette data as given', 'titre = 28.40 cm³' in L and 'I₂(aq), 5.00 × 10⁻⁴ mol dm⁻³' in L, str(L))
        check('diagram shows × 200.0/5.00 (= 40) on the dilution arrow', '× 200.0/5.00 (= 40)' in L, str(L))
        check('diagram shows × 176 and m = 0.100 g', '× 176' in L and '= 0.100 g' in L, str(L))
        check('mole ratio label × 1/1', '× 1/1' in L)
        geom('tablet')
        check('quantity symbols italic in svg', page.locator('.tt-labels tspan[font-style="italic"]').count() >= 5)
        shot(card, 'card-tablet.png')
        mb = page.locator('.tt-map').bounding_box(); sc = mb['width'] / VBW
        for name, (x, y, w_, h) in {'zoom-bottom-left': (0, 360, 420, 188), 'zoom-bottom-right': (360, 360, 420, 188),
                                    'zoom-burette': (380, 20, 400, 240), 'zoom-vessels': (0, 200, 780, 200)}.items():
            page.screenshot(path=str(OUT / f'{name}.png'), clip={'x': mb['x'] + x * sc, 'y': mb['y'] + y * sc, 'width': w_ * sc, 'height': h * sc})
        shot(page.locator('.tt-work'), 'zoom-work.png')
        shot(page.locator('.tt-form'), 'zoom-form.png')

        print('== ① NaOH vs H2SO4 (no dilution)')
        preset('naoh')
        w = work()
        check('n(H2SO4) = 0.00302', '0.200 × 15.10 ÷ 1000 = 0.00302 mol' in w, w)
        check('× 2/1 → 0.00604', '0.00302 × 2/1 = 0.00604 mol' in w, w)
        check('c = 0.00604 ÷ 0.0250 = 0.2416 → 0.242', '0.00604 ÷ 0.0250 = 0.2416 → 0.242 mol dm⁻³' in w, w)
        check('no dilution step', page.locator('.tt-work .dil').count() == 0)
        check('no volumetric flask drawn, its name dimmed', page.locator('.tt-art g.vf').count() == 0 and page.locator('.tt-labels text.dim').count() == 2)
        check('V1 input disabled', page.is_disabled('input.tt-v[data-k="v1"]'))
        L = labels()
        check('final arrow ÷ 0.0250 dm³', '÷ 0.0250 dm³' in L, str(L))
        geom('naoh')
        shot(card, 'card-naoh.png')
        put('vt', '20.00')
        check('titre 20.00 → 0.320', '→ 0.320 mol dm⁻³' in work() or '= 0.320 mol dm⁻³' in work(), work())
        check('burette label follows edit', 'titre = 20.00 cm³' in labels())
        put('ct', '2.00e-1')
        check('2.00e-1 accepted, echoed as 0.200', '0.200 × 20.00 ÷ 1000' in work(), work())
        put('ct', 'abc')
        check('bad number flagged', 'bad' in page.get_attribute('input.tt-v[data-k="ct"]', 'class') and '看不懂' in work())
        check('no mol labels while input bad', page.locator('.tt-labels text.mol').count() == 0)
        put('ct', '0.200'); put('vt', '15.10')
        page.check('.tt-dil')
        check('dilution on → V0 field shown', page.is_visible('input.tt-v[data-k="v0"]'))
        w = work()
        check('dilution 250.0 / 25.0 = 10 appears', 'dilution factor = V₁ / V₂ = 250.0 / 25.0 = 10' in w, w)
        check('c(original 25.0 cm³) = 2.42', '0.0604 ÷ 0.0250 = 2.416 → 2.42 mol dm⁻³' in w, w)
        page.select_option('.tt-tg', 'mass')
        check('mass target → Mr shown, V0 hidden', page.is_visible('input.tt-v[data-k="mr"]') and not page.is_visible('input.tt-v[data-k="v0"]'))
        check('m = 0.0604 × 40.0 = 2.42 g', '0.0604 × 40.0 = 2.416 → 2.42 g' in work(), work())
        geom('naoh-edited')
        put('v1', '10.0')
        check('V1 < V2 rejected', 'V₁ 要比 V₂ 大' in work(), work())

        print('== ③ lemon (9701/22 s25 Q5)')
        preset('lemon')
        w = work()
        check('n(I2) = 1.83 × 10⁻⁴', '5.00 × 10⁻³ × 36.65 ÷ 1000 = 1.83 × 10⁻⁴ mol' in w, w)
        check('dilution factor 100.0 / 25.0 = 4', 'dilution factor = V₁ / V₂ = 100.0 / 25.0 = 4' in w, w)
        check('m = 0.12901 → 0.129 g', '0.12901 → 0.129 g' in w, w)
        check('% = 0.086005 → 0.0860 %', '÷ 150.0 × 100 = 0.086005 → 0.0860 %' in w, w)
        L = labels()
        check('diagram: 150.0 g lemon, × 100.0/25.0, 0.0860 %', '150.0 g lemon' in L and '× 100.0/25.0 (= 4)' in L and '= 0.0860 % by mass' in L, str(L))
        check('sample-mass field shown', page.is_visible('input.tt-v[data-k="ms"]'))
        geom('lemon')
        shot(card, 'card-lemon.png')

        print('== ④ Mn2+ with NaBiO3 (9701/22 m24 Q1(e))')
        preset('mn')
        w = work()
        check('n(BiO3-) = 0.00215', '0.100 × 21.50 ÷ 1000 = 0.00215 mol' in w, w)
        check('ratio Mn²⁺ : BiO₃⁻ = 2 : 5', 'Mn²⁺ : BiO₃⁻ = 2 : 5' in w and '× 2/5 = 8.60 × 10⁻⁴ mol' in w, w)
        check('dilution 1000 / 25.00 = 40', 'dilution factor = V₁ / V₂ = 1000 / 25.00 = 40' in w, w)
        check('c = 0.0344 ÷ 0.1000 = 0.344', '0.0344 ÷ 0.1000 = 0.344 mol dm⁻³' in w, w)
        L = labels()
        check('diagram: × 2/5, × 1000/25.00, ÷ 0.1000 dm³', all(s in L for s in ('× 2/5', '× 1000/25.00 (= 40)', '÷ 0.1000 dm³')), str(L))
        check('diagram: = 0.344 mol dm⁻³', '= 0.344 mol dm⁻³' in L, str(L))
        geom('mn')
        shot(card, 'card-mn.png')

        print('== step-by-step')
        page.click('.tt-reset')
        check('reset → 0 / 4', '已展开 0 / 4 步' in page.inner_text('.tt-prog'))
        check('reset → no mol label or back arrow visible',
              page.evaluate("() => [...document.querySelectorAll('.tt-labels text.mol, .tt-wires path.back:not([data-w^=lg])')].every(e => getComputedStyle(e).visibility === 'hidden')"))
        check('reset → no working line visible', page.locator('.tt-work li:visible').count() == 0)
        shot(card, 'card-step0.png')
        page.click('.tt-next')
        check('step 1: one line, burette n shown', page.locator('.tt-work li:visible').count() == 1 and
              page.evaluate("() => [...document.querySelectorAll('.tt-labels text.mol')].filter(e => getComputedStyle(e).visibility !== 'hidden').length") == 2)
        page.click('.tt-next'); page.click('.tt-next')
        check('step 3 is the dilution step', page.locator('.tt-work li:visible').last.get_attribute('data-k') == 'nT')
        check('dilution arrow visible at step 3', page.evaluate("() => getComputedStyle(document.querySelector('[data-w=dil]')).visibility") == 'visible')
        check('final arrow still hidden at step 3', page.evaluate("() => getComputedStyle(document.querySelector('[data-w=fin]')).visibility") == 'hidden')
        shot(card, 'card-step3.png')
        page.click('.tt-next')
        check('step 4 → next disabled', page.is_disabled('.tt-next'))
        preset('lemon')
        check('preset change in step mode restarts at 0', '已展开 0 / 5 步' in page.inner_text('.tt-prog'))
        page.click('.tt-all')
        check('全部展开 → 5 lines', page.locator('.tt-work li:visible').count() == 5)

        print('== narrow (720 px)')
        preset('tab')
        page.set_viewport_size({'width': 720, 'height': 1500}); page.wait_for_timeout(250)
        ov = page.evaluate('() => { const k=document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('no horizontal overflow at 720 px', ov <= 0, str(ov))
        px = page.evaluate("""() => { const s = document.querySelector('.tt-map'), k = s.getBoundingClientRect().width / 780;
          return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k)); }""")
        check('smallest diagram text ≥ 12 px on screen at 720', px >= 12, f'{px:.1f}')
        geom('720')
        shot(card, 'card-720.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
