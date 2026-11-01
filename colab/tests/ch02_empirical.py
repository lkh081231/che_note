"""ch02 empirical cell test: empirical → molecular formula, step-by-step table (by mass / by % / molecular formula / hydrated salt).

usage: uv run --with playwright python -I colab/tests/ch02_empirical.py <preview.html> <shots-dir>
(python tools/build_colab.py ch02 --cell empirical writes the preview page)
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
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=["--disable-gpu"])  # GPU process stalls under parallel runs → rAF never fires → clicks hang
    ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2)
    page = ctx.new_page()
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
    page.goto(PAGE.as_uri()); page.wait_for_timeout(500)
    K = page.locator('.k').first

    def pane(m):
        return page.locator(f'[data-pane="{m}"]')

    def shot(name, sel=None):
        (page.locator(sel).first if sel else K).screenshot(path=str(OUT / f'{name}.png'))

    def tab(m):
        page.click(f'button[data-tab="{m}"]'); page.wait_for_timeout(80)

    def preset(m, i):
        pane(m).locator('.em-preset').select_option(str(i))

    def attr(m, a):
        return pane(m).get_attribute(f'data-{a}')

    def txt(m, sel):
        return pane(m).locator(sel).inner_text()

    def visible_rows(m):
        return pane(m).locator('.em-tab tr:not(.hid)').count() - 1   # minus header

    def all_steps(m):
        btn = pane(m).locator('.em-all')
        if not btn.is_disabled(): btn.click()
        assert pane(m).locator('.em-all').is_disabled()

    def fill(m, key, v):
        pane(m).locator(f'input[data-k="{key}"]').fill(v)

    print('== ① by mass')
    tab('mass')
    check('4 tabs', page.locator('.tabbar button').count() == 4)
    check('3 mass presets', pane('mass').locator('.em-preset option').count() == 3)
    preset('mass', 1)
    check('P: starts at step 1, only mass row visible', attr('mass', 'step') == '1' and visible_rows('mass') == 1, f"{attr('mass','step')} {visible_rows('mass')}")
    sub_cell = txt('mass', '.em-tab td.em-sub')
    check('O by subtraction shown explicitly: 3.55 − 1.55 = 2.00', '3.55 − 1.55 =' in sub_cell and '2.00' in sub_cell and '用减法' in sub_cell, sub_cell)
    check('step-1 note says 用减法', '用减法' in txt('mass', '.em-steps li:first-child'))
    check('result hidden before last step', not pane('mass').locator('.em-res').is_visible())
    pane('mass').locator('.em-next').click()
    check('next → ÷ Aᵣ row', visible_rows('mass') == 2 and '1.55 ÷ 31.0' in txt('mass', 'tr.em-r2') and '0.0500' in txt('mass', 'tr.em-r2')
          and '2.00 ÷ 16.0' in txt('mass', 'tr.em-r2') and '0.125' in txt('mass', 'tr.em-r2'), txt('mass', 'tr.em-r2'))
    check('smallest (P) is outlined', pane('mass').locator('td.em-min').count() == 1 and '31.0' in pane('mass').locator('td.em-min').inner_text())
    pane('mass').locator('.em-next').click()
    check('÷ smallest row: 1.00 and 2.50', '1.00' in txt('mass', 'tr.em-r3') and '2.50' in txt('mass', 'tr.em-r3'), txt('mass', 'tr.em-r3'))
    shot('01-p-step3')
    pane('mass').locator('.em-next').click()
    r4 = txt('mass', 'tr.em-r4')
    check('× 2 row: 2.50 × 2 = 5.00 → 5', '× 2' in r4 and '2.50 × 2 = 5.00' in r4 and '→ 5' in r4.replace('\n', ' '), r4)
    n4 = txt('mass', '.em-steps li:nth-child(4)')
    check('note: 2.50 不能四舍五入成 3, × 2', '不能四舍五入成 3' in n4 and '1.00 : 2.50 → 2 : 5' in n4, n4)
    pane('mass').locator('.em-next').click()
    check('P → P₂O₅', attr('mass', 'ef') == 'P₂O₅' and 'P₂O₅' in txt('mass', '.em-res'), attr('mass', 'ef'))
    check('next disabled at the end', pane('mass').locator('.em-next').is_disabled())
    shot('02-p-done'); shot('02z-p-table', '[data-pane="mass"] .em-tab'); shot('02z-p-steps', '[data-pane="mass"] .em-steps')
    pane('mass').locator('.em-reset').click()
    check('从头开始 → step 1', attr('mass', 'step') == '1' and visible_rows('mass') == 1)
    # edit values: 2.48 g P → 4.40 g oxide → O 1.92 g: 0.0800 : 0.120 = 1 : 1.5 → P₂O₃
    fill('mass', 'c0', '2.48'); fill('mass', 'total', '4.40')
    all_steps('mass')
    check('edited 2.48 g P / 4.40 g oxide → P₂O₃ (1.5 ×2)', attr('mass', 'ef') == 'P₂O₃' and '× 2' in txt('mass', 'tr.em-r4'), attr('mass', 'ef'))
    fill('mass', 'total', '2.00')
    check('oxide lighter than P → error, no table', pane('mass').locator('.em-err').is_visible() and pane('mass').locator('.em-tab tr').count() == 0, txt('mass', '.em-err'))
    shot('03-err')
    preset('mass', 0); all_steps('mass')
    check('Mg 0.486 / MgO 0.806 → MgO', attr('mass', 'ef') == 'MgO' and '0.806 − 0.486' in txt('mass', 'td.em-sub') and '0.0200' in txt('mass', 'tr.em-r2'), attr('mass', 'ef'))
    preset('mass', 2)
    check('S/Cl: 6 steps (has Mᵣ)', '/ 6' in txt('mass', '.em-prog'), txt('mass', '.em-prog'))
    all_steps('mass')
    check('S/Cl: Cl = 100.0 − 47.49 = 52.51', '100.0 − 47.49' in txt('mass', 'td.em-sub') and '52.51' in txt('mass', 'td.em-sub'), txt('mass', 'td.em-sub'))
    check('S/Cl → SCl, + Mᵣ 135.2 → S₂Cl₂', attr('mass', 'ef') == 'SCl' and attr('mass', 'mf') == 'S₂Cl₂' and 'S₂Cl₂' in txt('mass', '.em-res'))
    check('S/Cl note: 32.1 + 35.5 = 67.6; 135.2 ÷ 67.6 = 2.00', '32.1 + 35.5 = 67.6' in txt('mass', '.em-steps') and '135.2 ÷ 67.6 = 2.00' in txt('mass', '.em-steps'))
    check('S/Cl note names Cl 35.5 not 71.0 (no stray O)', 'Cl₂ 的 71.0' in txt('mass', '.em-steps') and '32.0' not in txt('mass', '.em-steps'), txt('mass', '.em-steps li:nth-child(2)'))
    shot('04-scl-done')
    fill('mass', 'Mr', '')
    check('Mᵣ cleared → 5 steps, no molecular formula', attr('mass', 'mf') is None and '/ 5' in txt('mass', '.em-prog'))

    print('== ② by %')
    tab('pct')
    all_steps('pct')
    check('85.7% C 14.3% H → CH₂', attr('pct', 'ef') == 'CH₂', attr('pct', 'ef'))
    check('CH: 85.7 ÷ 12.0 = 7.14, 14.3 ÷ 1.0 = 14.3', '85.7 ÷ 12.0' in txt('pct', 'tr.em-r2') and '7.14' in txt('pct', 'tr.em-r2') and '14.3 ÷ 1.0' in txt('pct', 'tr.em-r2'))
    check('CH note names H (1.0, not H₂ 2.0), not O', 'H₂ 的 2.0' in txt('pct', '.em-steps') and '32.0' not in txt('pct', '.em-steps'), txt('pct', '.em-steps li:nth-child(2)'))
    shot('05-ch2-done')
    fill('pct', 'c1', '15.3')
    check('% not summing to 100 → error', '100' in txt('pct', '.em-err') and pane('pct').locator('.em-err').is_visible())
    preset('pct', 1)
    check('preset change resets to step 1', attr('pct', 'step') == '1')
    all_steps('pct')
    sc = txt('pct', 'td.em-sub')
    check('vitamin C: O = 100 − 40.9 − 4.5 = 54.6', '100 − 40.9 − 4.5' in sc and '54.6' in sc, sc)
    check('vitamin C ratio 1.32 → × 3', '1.32' in txt('pct', 'tr.em-r3') and '× 3' in txt('pct', 'tr.em-r4') and '3.96' in txt('pct', 'tr.em-r4'), txt('pct', 'tr.em-r4'))
    check('vitamin C → C₃H₄O₃', attr('pct', 'ef') == 'C₃H₄O₃', attr('pct', 'ef'))
    check('vitamin C + Mᵣ 176 → C₆H₈O₆', attr('pct', 'mf') == 'C₆H₈O₆', attr('pct', 'mf'))
    check('note mentions ⅓ and 不能四舍五入', '⅓' in txt('pct', '.em-steps') and '不能四舍五入' in txt('pct', '.em-steps'))
    shot('10-vitc-done'); shot('10z-vitc-table', '[data-pane="pct"] .em-tab')

    print('== ③ molecular formula')
    tab('mf')
    want = ['C₂H₄Br₂', 'C₆H₁₀', 'C₂Cl₆', 'C₈H₁₆', 'S₂Cl₂']
    check('5 mf presets', pane('mf').locator('.em-preset option').count() == 5)
    for i, w in enumerate(want):
        preset('mf', i)
        check(f'mf preset {i}: result hidden at step 1', not pane('mf').locator('.em-res').is_visible())
        all_steps('mf')
        check(f'mf preset {i} → {w}', attr('mf', 'mf') == w and w in txt('mf', '.em-res'), f"{attr('mf', 'mf')}")
        if i == 0:
            s = txt('mf', '.em-steps')
            check('CH₂Br: 12.0 + 2 × 1.0 + 79.9 = 93.9; 187.8 ÷ 93.9 = 2.00', '12.0 + 2 × 1.0 + 79.9 = 93.9' in s and '187.8 ÷ 93.9 = 2.00' in s, s)
            shot('20-mf-ch2br'); shot('20z-mf-table', '[data-pane="mf"] .em-tab')
    fill('mf', 'ef', 'CH2O'); fill('mf', 'Mr', '180')
    check('typed CH2O + 180 → C₆H₁₂O₆', attr('mf', 'mf') == 'C₆H₁₂O₆', attr('mf', 'mf'))
    fill('mf', 'ef', 'CH₂O')
    check('subscript digits accepted too', attr('mf', 'ef') == 'CH₂O')
    fill('mf', 'Mr', '100')
    check('Mᵣ not a multiple → warning, no mf', attr('mf', 'mf') is None and '不是整数' in txt('mf', '.em-res'))
    fill('mf', 'ef', 'ch2')
    check('lower-case formula → parse error', '看不懂' in txt('mf', '.em-err'))
    fill('mf', 'ef', 'Xy2')
    check('unknown element → error', 'Xy' in txt('mf', '.em-err'))
    shot('21-mf-err')

    print('== ④ hydrated salt')
    tab('hyd')
    all_steps('hyd')
    check('CuSO₄: water = 2.50 − 1.60 = 0.90', '2.50 − 1.60' in txt('hyd', 'td.em-sub') and '0.90' in txt('hyd', 'td.em-sub'), txt('hyd', 'td.em-sub'))
    check('CuSO₄: ÷ Mᵣ 159.6 and 18.0', '÷ 159.6' in txt('hyd', 'tr.em-r2') and '÷ 18.0' in txt('hyd', 'tr.em-r2'))
    check('CuSO₄ Mᵣ working shown 63.5 + 32.1 + 4 × 16.0', '63.5 + 32.1 + 4 × 16.0 = 159.6' in txt('hyd', '.em-steps'))
    check('CuSO₄·5H₂O', attr('hyd', 'x') == '5' and 'CuSO₄·5H₂O' in txt('hyd', '.em-res'), attr('hyd', 'x'))
    shot('30-cuso4-done')
    preset('hyd', 1); all_steps('hyd')
    check('RhCl₃: % RhCl₃ = 100 − 20.5 = 79.5', '100 − 20.5' in txt('hyd', 'td.em-sub') and '79.5' in txt('hyd', 'td.em-sub'), txt('hyd', 'td.em-sub'))
    check('RhCl₃·xH₂O → x = 3', attr('hyd', 'x') == '3' and 'RhCl₃·3H₂O' in txt('hyd', '.em-res'), attr('hyd', 'x'))
    shot('31-rhcl3-done'); shot('31z-rhcl3-table', '[data-pane="hyd"] .em-tab')
    preset('hyd', 2); all_steps('hyd')
    check('CoCl₂·xH₂O → x = 6', attr('hyd', 'x') == '6', attr('hyd', 'x'))

    print('== layout')
    check('no [data-clash]', page.locator('[data-clash]').count() == 0)
    for w in (700, 1000):
        page.set_viewport_size({'width': w, 'height': 1100})
        for m in ('mass', 'pct', 'mf', 'hyd'):
            tab(m); all_steps(m)
            ov = page.evaluate("() => { const k=document.querySelector('.k'); return k.scrollWidth - k.clientWidth; }")
            tw = page.evaluate(f"() => {{ const w=document.querySelector('[data-pane=\"{m}\"] .em-wrap'); return w.scrollWidth - w.clientWidth; }}")
            check(f'width {w}, {m}: no horizontal overflow', ov <= 0 and tw <= 0, f'{ov} {tw}')
            small = page.evaluate("""() => { let m=99; document.querySelectorAll('.k *').forEach(e=>{ if(e.offsetParent && [...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())) m=Math.min(m, parseFloat(getComputedStyle(e).fontSize)); }); return m; }""")
            check(f'width {w}, {m}: smallest visible font >= 12px', small >= 12, str(small))
        if w == 700:
            tab('pct'); shot('40-w700-pct'); tab('mass'); shot('41-w700-mass')
    check('no svg in this cell (no viewBox font scaling)', page.locator('.k svg').count() == 0)

    print('== dark mode')
    ctx3 = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme='dark')
    pg3 = ctx3.new_page(); pg3.on('pageerror', lambda e: errors.append(f'PAGEERROR dark {e}'))
    pg3.on('console', lambda m: errors.append('dark ' + m.text) if m.type == 'error' else None)
    pg3.goto(PAGE.as_uri()); pg3.wait_for_timeout(400)
    pg3.locator('[data-pane="mass"] .em-preset').select_option('1'); pg3.locator('[data-pane="mass"] .em-all').click()
    pg3.locator('.k').first.screenshot(path=str(OUT / '50-dark-p.png'))
    pg3.click('button[data-tab="hyd"]'); pg3.locator('[data-pane="hyd"] .em-preset').select_option('1'); pg3.locator('[data-pane="hyd"] .em-all').click()
    pg3.locator('.k').first.screenshot(path=str(OUT / '51-dark-rhcl3.png'))
    ctx3.close(); b.close()

check('console / page errors = 0', not errors, '; '.join(errors))
n_ok = sum(1 for r in results if r[1])
print(f'{n_ok}/{len(results)} passed')
sys.exit(0 if n_ok == len(results) else 1)
