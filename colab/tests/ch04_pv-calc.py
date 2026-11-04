"""ch04 pv-calc cell test.

usage: uv run --with playwright python -I colab/tests/ch04_pv-calc.py $COLAB_TMP/cells/ch04-pv-calc.html <shots-dir>
(build first: python3 tools/build_colab.py ch04 --cell pv-calc)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []

# preset → (answer in .pv-res, strings that must appear in the working)
PRESETS = {
    'ex1': ('V = 8.09 × 10⁻³ m³', ['150 kPa = 150 000 Pa', '19 °C = 19 + 273 = 292 K', 'V = 0.500 × 8.31 × 292 / 150 000 = 8.0884 × 10⁻³ m³',
                                   '= 8.09 dm³ = 8090 cm³']),
    'ex2': ('p = 8.31 × 10⁴ Pa', ['n = m / Mᵣ = 4.00 / 32.0 = 0.125 mol', '5.00 dm³ = 5.00 × 10⁻³ m³', '127 + 273 = 400 K',
                                  'p = 0.125 × 8.31 × 400 / (5.00 × 10⁻³) = 8.31 × 10⁴ Pa', '= 83.1 kPa']),
    'ex3': ('30.4', ['1 atm = 101 325 Pa', '1 × 10⁻³ m³', '20 + 273 = 293 K', 'n = 101 325 × 1 × 10⁻³ / (8.31 × 293)', 'Mᵣ = m / n = 1.264 / 0.041615 = 30.374']),
    'pr1': ('32.1', ['200 kPa = 200 000 Pa', '2.00 dm³ = 2.00 × 10⁻³ m³', 'n = 200 000 × 2.00 × 10⁻³ / (8.31 × 293)']),
    'pr2': ('T = 578 K', ['120 kPa = 120 000 Pa', '10 dm³ = 10 × 10⁻³ m³', 'T = 120 000 × 10 × 10⁻³ / (0.25 × 8.31) = 577.62 K', '= 305 °C']),
    'mj23': ('71.0', ['101 kPa = 101 000 Pa', '617.0 cm³ = 617.0 × 10⁻⁶ m³', 'T = 300 K（已是 SI）',
                      'n = 101 000 × 617.0 × 10⁻⁶ / (8.31 × 300) = 0.024997 mol', 'Mᵣ = m / n = 1.775 / 0.024997 = 71.009']),
    'fm22': ('V = 5.99 × 10⁻⁵ m³', ['n(NO) = 0.00393 × 2/3 = 0.00262 mol', '5 °C = 5 + 273 = 278 K', '101 kPa = 101 000 Pa', '= 59.9 cm³']),
    'mj21': ('V = 0.0138 m³', ['n(O₂) = 0.500 ÷ 2 = 0.250 mol', '400 + 273 = 673 K', 'V = 0.250 × 8.31 × 673 / 101 000', '= 13.8 dm³']),
}


def shot(page, sel, path):
    """element screenshot via a page clip: Locator.screenshot waits for 'stable' (two rAFs), which
    hangs when several headless Chromes share the machine"""
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True, timeout=30000)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def nb(s):
    return s.replace('\xa0', ' ')


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2, color_scheme=scheme)
        ctx.set_default_timeout(15000)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri(), timeout=30000); page.wait_for_timeout(400)

        def work():
            return nb(page.inner_text('.pv-work'))

        def res():
            return nb(page.inner_text('.pv-res')) if page.locator('.pv-res').count() else ''

        def forgot():
            return page.get_attribute('.pv-forgot', 'class'), nb(page.inner_text('.pv-forgot'))

        def clashes():
            return page.locator('[data-clash]').count()

        def outside():
            return page.evaluate('''() => { const s = document.querySelector('.pv-fig'), v = s.viewBox.baseVal;
                return [...s.querySelectorAll('text')].filter(t => { const b = t.getBBox();
                  return b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5; })
                  .map(t => t.textContent); }''')

        def pre(i):
            page.click(f'.pv-pre button[data-pre="{i}"]'); page.wait_for_timeout(30)

        if scheme == 'dark':
            pre('ex1')
            shot(page, '.k', OUT / 'card-dark.png')
            shot(page, '.pv-forgot', OUT / 'zoom-forgot-dark.png')
            pre('mj23')
            shot(page, '.k', OUT / 'card-dark-mj23.png')
            red = page.eval_on_selector('.pv-forgot', 'e => getComputedStyle(e).color')
            check('dark: forgot line uses the dark --bad red', red == 'rgb(255, 123, 114)', red)
            check('dark: no label clash', clashes() == 0, str(clashes()))
            ctx.close()
            continue

        print('== 8 presets')
        for pid, (ans, lines) in PRESETS.items():
            pre(pid)
            w = work()
            check(f'{pid}: result {ans}', res().startswith(ans), res())
            for ln in lines:
                check(f'{pid}: working has “{ln}”', ln in w, w)
            check(f'{pid}: source note shown', '出处：' in page.inner_text('.pv-src'))
            check(f'{pid}: no label clash', clashes() == 0, str(clashes()))
            check(f'{pid}: labels inside the figure', not outside(), str(outside()))
        pre('fm22')
        check('fm22: source names the paper', '9701/22 Feb/Mar 2026 Q2(b)' in page.inner_text('.pv-src'))
        shot(page, '.k', OUT / 'card-fm22.png')
        pre('mj23')
        check('mj23: source names the paper', '9701/23 May/June 2026 Q2(c)' in page.inner_text('.pv-src'))
        shot(page, '.k', OUT / 'card-mj23.png')
        check('mj23: ladder highlights cm³ (the unit V was given in)', page.locator('.pv-fig rect.cur[data-u="cm³"]').count() == 1)
        check('mj23: ladder values 6.17 × 10⁻⁴ m³ / 0.617 dm³ / 617 cm³',
              [nb(t) for t in page.eval_on_selector_all('.pv-fig text[data-v]', 'ts => ts.map(t => t.textContent)')] ==
              ['6.17 × 10⁻⁴ m³', '0.617 dm³', '617 cm³'])

        print('== forgot-to-convert line')
        pre('ex1')
        c, t = forgot()
        check('ex1: red forgot line', 'bad' in c, c)
        check('ex1: forgot line uses 19 (°C) and 150 (kPa)', 'V = 0.500 × 8.31 × 19 / 150 = 0.526 m³' in t, t)
        check('ex1: forgot line names both mistakes', 'T 直接用 19 °C' in t and 'p 用 kPa' in t, t)
        check('ex1: forgot line shows the right answer', '正确：8.09 × 10⁻³ m³' in t, t)
        red = page.eval_on_selector('.pv-forgot', 'e => getComputedStyle(e).color')
        check('light: forgot line is --bad red', red == 'rgb(207, 34, 46)', red)
        shot(page, '.k', OUT / 'card-default.png')
        shot(page, '.pv-work', OUT / 'zoom-work-ex1.png')
        shot(page, '.pv-forgot', OUT / 'zoom-forgot-ex1.png')
        shot(page, '.pv-fig', OUT / 'zoom-ladder.png')
        shot(page, '.pv-pre', OUT / 'zoom-presets.png')
        pre('pr2')
        c, t = forgot()
        check('pr2 (kPa with dm³, T in K): consistent note, not red', 'okn' in c and 'bad' not in c, c)
        check('pr2: raw 120 × 10 / (0.25 × 8.31) also gives 578', '= 578' in t, t)
        shot(page, '.pv-forgot', OUT / 'zoom-forgot-consistent.png')
        pre('mj23')
        c, t = forgot()
        check('mj23 (kPa with cm³): red', 'bad' in c, c)
        check('mj23: raw 1.775 × 8.31 × 300 / (101 × 617.0)', 'Mᵣ = 1.775 × 8.31 × 300 / (101 × 617.0) = 0.0710' in t, t)
        pre('ex2')
        c, t = forgot()
        check('ex2 (T 127 °C): red', 'bad' in c and 'T 直接用 127 °C' in t, t)

        print('== changing a unit converts the number, the result stays')
        pre('ex1')
        base = res()
        page.select_option('.pv-f[data-f="p"] select', 'Pa')
        check('150 kPa → 150000 Pa in the box', page.input_value('.pv-f[data-f="p"] input') == '150000', page.input_value('.pv-f[data-f="p"] input'))
        check('result unchanged after kPa → Pa', res() == base, res())
        page.select_option('.pv-f[data-f="p"] select', 'atm')
        check('result unchanged after Pa → atm', res() == base, res())
        page.select_option('.pv-f[data-f="T"] select', 'K')
        check('19 °C → 292 K in the box', page.input_value('.pv-f[data-f="T"] input') == '292', page.input_value('.pv-f[data-f="T"] input'))
        check('result unchanged after °C → K', res() == base, res())
        page.select_option('.pv-f[data-f="p"] select', 'Pa')
        page.fill('.pv-f[data-f="p"] input', '150000')
        c, t = forgot()
        check('all SI → neutral "already SI" note', 'si' in c.split() and '已经全是 SI' in t, c + t)
        pre('mj23')
        base = res()
        for u, v in (('dm³', '0.6170'), ('m³', '0.0006170'), ('cm³', '617.0')):
            page.select_option('.pv-f[data-f="V"] select', u)
            check(f'617.0 cm³ shown as {v} {u}', page.input_value('.pv-f[data-f="V"] input') == v, page.input_value('.pv-f[data-f="V"] input'))
            check(f'Mr unchanged in {u}', res() == base, res())
        page.select_option('.pv-f[data-f="V"] select', 'dm³')
        check('kPa + dm³ now → consistent note', 'okn' in forgot()[0], forgot()[0])
        check('ladder highlight follows the V unit', page.locator('.pv-fig rect.cur[data-u="dm³"]').count() == 1)

        print('== switching what to solve for')
        pre('ex1')
        page.click('.pv-mode button[data-mode="p"]')
        check('solve for p: V field filled with the old answer 8.088 dm³ (4 s.f.)', page.input_value('.pv-f[data-f="V"] input') == '8.088')
        check('solve for p: p row hidden', page.locator('.pv-f[data-f="p"]').is_hidden())
        check('round trip gives p ≈ 150 kPa', res().startswith('p = 1.50 × 10⁵ Pa'), res())
        page.click('.pv-mode button[data-mode="n"]')
        check('solve for n → 0.500 mol', res() == 'n = 0.500 mol', res())
        page.click('.pv-mode button[data-mode="T"]')
        check('solve for T → 292 K', res() == 'T = 292 K', res())
        pre('ex3')
        page.click('.pv-mode button[data-mode="V"]')
        check('density preset → solve V: m = 1.264 g, V row hidden, 1.00 dm³ back',
              page.input_value('.pv-f[data-f="m"] input') == '1.264' and '= 1.00 dm³' in work(), work())
        page.click('.pv-mode button[data-mode="M"]')
        check('back to Mr → 30.4', res().startswith('30.4'), res())

        print('== invalid input')
        pre('ex1')
        page.fill('.pv-f[data-f="n"] input', 'abc')
        check('letters → field flagged red', 'bad' in page.get_attribute('.pv-f[data-f="n"] input', 'class'))
        check('letters → message, no result', '> 0 的数' in work() and res() == '', work())
        page.fill('.pv-f[data-f="n"] input', '-1')
        check('negative n flagged', 'bad' in page.get_attribute('.pv-f[data-f="n"] input', 'class'))
        page.fill('.pv-f[data-f="n"] input', '0.500')
        page.fill('.pv-f[data-f="T"] input', '-300')
        check('T = −300 °C → < 0 K error', '不可能' in work() and '−27 K' in work() and 'bad' in page.get_attribute('.pv-f[data-f="T"] input', 'class'), work())
        shot(page, '.pv-work', OUT / 'zoom-error-T.png')
        page.select_option('.pv-f[data-f="T"] select', 'K')
        page.fill('.pv-f[data-f="T"] input', '-5')
        check('T = −5 K → error', '不可能' in work(), work())
        page.fill('.pv-f[data-f="T"] input', '292')
        check('fixed → result back', res() == 'V = 8.09 × 10⁻³ m³', res())
        check('e-notation accepted', (page.fill('.pv-f[data-f="n"] input', '5.00e-1') or True) and res() == 'V = 8.09 × 10⁻³ m³', res())
        check('no console error so far', not errors, '; '.join(errors))

        print('== narrow (720 px)')
        pre('mj23')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(250)
        ov = page.evaluate('() => { const k=document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('no horizontal overflow at 720 px', ov <= 0, str(ov))
        fs = page.evaluate('''() => { const s = document.querySelector('.pv-fig'), k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k)); }''')
        check('ladder font size (CSS px × rendered / viewBox width) ≥ 12 at 720 px', fs >= 12, f'{fs:.2f}')
        check('no label clash at 720 px', clashes() == 0, str(clashes()))
        shot(page, '.k', OUT / 'card-720.png')
        pre('ex1')
        shot(page, '.k', OUT / 'card-720-ex1.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
