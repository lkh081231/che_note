"""ch02 balance cell test: balancing equations (+/- coefficients, atom table) and ionic equations.

usage: uv run --with playwright python -I colab/tests/ch02_balance.py $COLAB_TMP/cells/ch02-balance.html <shots-dir>
(run tools/build_colab.py ch02 --cell balance first)
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


EQ_ANS = [  # (button index, answer coefficients, balanced text)
    (0, [1, 3, 2, 3], 'Fe₂O₃ + 3CO → 2Fe + 3CO₂'),
    (1, [2, 1, 3], '2Al(OH)₃ → Al₂O₃ + 3H₂O'),
    (2, [1, 2, 1, 1], 'Fe + 2HCl → FeCl₂ + H₂'),
    (3, [1, 5, 3, 4], 'C₃H₈ + 5O₂ → 3CO₂ + 4H₂O'),
    (4, [2, 3, 1, 3], '2Bi + 3H₂O → Bi₂O₃ + 3H₂'),
    (5, [1, 6, 3, 2], 'Mg₃N₂ + 6H₂O → 3Mg(OH)₂ + 2NH₃'),
]
ION = [  # (button index, spectator chip keys, wrong chip key, final ionic equation, spectator text)
    (0, ['SO4|-2|aq'], 'Cu|2|aq', 'Zn(s) + Cu²⁺(aq) → Zn²⁺(aq) + Cu(s)', 'SO₄²⁻'),
    (1, ['Na|1|aq', 'SO4|-2|aq'], 'H|1|aq', 'H⁺(aq) + OH⁻(aq) → H₂O(l)', 'Na⁺、SO₄²⁻'),
    (2, ['K|1|aq'], 'I|-1|aq', 'Br₂(aq) + 2I⁻(aq) → 2Br⁻(aq) + I₂(aq)', 'K⁺'),
    (3, ['SO4|-2|aq', 'Na|1|aq'], 'OH|-1|aq', 'Cu²⁺(aq) + 2OH⁻(aq) → Cu(OH)₂(s)', 'Na⁺、SO₄²⁻'),
    (4, ['K|1|aq', 'NO3|-1|aq'], 'Pb|2|aq', 'Pb²⁺(aq) + 2I⁻(aq) → PbI₂(s)', 'K⁺、NO₃⁻'),
]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True)
    ctx = b.new_context(viewport={'width': 1000, 'height': 1000}, device_scale_factor=2)
    page = ctx.new_page()
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
    page.goto(PAGE.as_uri()); page.wait_for_timeout(500)
    K = page.locator('.k').first

    def shot(name, sel=None, scale=None):
        (page.locator(sel).first if sel else K).screenshot(path=str(OUT / f'{name}.png'))

    def bal():
        return page.get_attribute('.k', 'data-bal')

    def term(k):
        return page.locator(f'.bl-term[data-i="{k}"]')

    def setco(target):
        """click +/- until every coefficient matches target (really clicking the buttons)"""
        for k, n in enumerate(target):
            for _ in range(20):
                v = int(term(k).locator('.bl-co').inner_text())
                if v == n: break
                term(k).locator('.bl-plus' if v < n else '.bl-minus').click()

    def ion(state):
        return page.get_attribute('.k', 'data-ionic')

    print('== tab 1: balance')
    shot('01-default')
    check('6 equations offered', page.locator('.bl-pick button').count() == 6)
    check('default: unbalanced', bal() == 'no', bal())
    check('formula is not editable (no input inside .bl-f)', page.locator('.bl-term .bl-f input').count() == 0 and page.locator('.bl-eq input').count() == 0)
    check('minus disabled at 1', term(0).locator('.bl-minus').is_disabled())
    term(0).locator('.bl-minus').click(force=True)
    check('coefficient never goes below 1', term(0).locator('.bl-co').inner_text() == '1')
    setco([1, 1, 2, 1])
    o = page.locator('.bl-tab tr[data-el="O"]').get_attribute('class'); fe = page.locator('.bl-tab tr[data-el="Fe"]').get_attribute('class')
    check('2Fe only: Fe row green, O row not', fe == 'eq' and o == 'ne', f'Fe {fe} O {o}')
    check('status names O as unbalanced', 'O' in page.inner_text('.bl-st') and '还没平衡' in page.inner_text('.bl-st'), page.inner_text('.bl-st'))
    setco([1, 3, 2, 3])
    check('Fe₂O₃ + 3CO → 2Fe + 3CO₂: ok', bal() == 'ok', bal())
    check('✓ + balanced equation shown', '✓ Fe₂O₃ + 3CO → 2Fe + 3CO₂' in page.inner_text('.bl-st'), page.inner_text('.bl-st'))
    check('all atom rows green', page.locator('.bl-tab tr.ne').count() == 0 and page.locator('.bl-tab tr.eq').count() == 3)
    o_row = page.inner_text('.bl-tab tr[data-el="O"]')
    check('O row shows working 1×3 + 3×1 = 6 vs 2×... ', '1×3 + 3×1' in o_row and '3×2' in o_row, o_row)
    shot('02-fe2o3-ok'); shot('02z-eq', '.bl-eqcard'); shot('02z-table', '.bl-tab')
    setco([2, 6, 4, 6])
    check('2:6:4:6 → balanced but not lowest terms', bal() == 'reduce' and '÷ 2' in page.inner_text('.bl-st'), page.inner_text('.bl-st'))
    shot('03-reduce')
    page.click('.bl-reset'); check('reset → all 1', [term(k).locator('.bl-co').inner_text() for k in range(4)] == ['1'] * 4)
    for i, ans, txt in EQ_ANS:
        page.click(f'.bl-pick button[data-eq="{i}"]')
        check(f'eq {i}: starts unbalanced', bal() == 'no', bal())
        setco(ans)
        check(f'eq {i}: {txt} ✓', bal() == 'ok' and txt in page.inner_text('.bl-st'), page.inner_text('.bl-st'))
    shot('04-mg3n2-ok')
    page.click('.bl-hint'); check('hint opens', page.is_visible('.bl-hintbox') and '12' in page.inner_text('.bl-hintbox')); shot('05-hint')

    print('== tab 2: ionic equation')
    page.click('button[data-tab="ion"]'); page.wait_for_timeout(100)
    check('5 reactions offered', page.locator('.bl-ipick button').count() == 5)
    page.click('.bl-ipick button[data-r="4"]')
    full = page.inner_text('.bl-full')
    check('full equation with state symbols', 'Pb(NO₃)₂(aq) + 2KI(aq) → PbI₂(s) + 2KNO₃(aq)' in full, full)
    check('② ③ disabled before ①', page.locator('.bl-s2').is_disabled() and page.locator('.bl-s3').is_disabled())
    shot('10-pb-start')
    page.click('.bl-s1')
    w = page.inner_text('.bl-work .bl-line')
    check('split: Pb²⁺ + 2NO₃⁻ + 2K⁺ + 2I⁻ → PbI₂(s) + 2K⁺ + 2NO₃⁻',
          w.replace('\n', ' ').split() == 'Pb²⁺(aq) + 2NO₃⁻(aq) + 2K⁺(aq) + 2I⁻(aq) → PbI₂(s) + 2K⁺(aq) + 2NO₃⁻(aq)'.split(), w)
    check('PbI₂(s) kept whole, explained', '不拆' in page.inner_text('.bl-why') and 'precipitate' in page.inner_text('.bl-why'))
    page.locator('.bl-chip[data-key="K|1|aq"]').first.click()
    check('chips not clickable before ②', page.locator('.bl-chip.gone').count() == 0)
    shot('11-pb-split')
    page.click('.bl-s2')
    page.locator('.bl-chip[data-key="Pb|2|aq"]').click()
    check('striking Pb²⁺ is refused with a warning', ion(0) == 'wrong' and page.locator('.bl-chip.gone').count() == 0 and '不是 spectator' in page.inner_text('.bl-msg'), page.inner_text('.bl-msg'))
    shot('12-pb-wrong'); shot('12z-wrong', '.bl-work')
    page.locator('.bl-chip[data-key="PbI2|0|s"]').click()
    check('striking PbI₂(s) is refused', page.locator('.bl-chip.gone').count() == 0 and '参与了反应' in page.inner_text('.bl-msg'))
    page.locator('.bl-chip[data-key="K|1|aq"]').first.click()
    check('K⁺ struck on both sides', page.locator('.bl-chip.gone[data-key="K|1|aq"]').count() == 2)
    page.click('.bl-s3')
    check('check too early → NO₃⁻ still missing', ion(0) == 'incomplete' and '1 种' in page.inner_text('.bl-msg'), page.inner_text('.bl-msg'))
    page.locator('.bl-chip[data-key="NO3|-1|aq"]').first.click()
    check('NO₃⁻ struck on both sides', page.locator('.bl-chip.gone[data-key="NO3|-1|aq"]').count() == 2)
    shot('13-pb-struck')
    page.click('.bl-s3')
    check('Pb: done', ion(0) == 'done', ion(0))
    check('Pb²⁺(aq) + 2I⁻(aq) → PbI₂(s)', page.inner_text('.bl-ionic') == 'Pb²⁺(aq) + 2I⁻(aq) → PbI₂(s)', page.inner_text('.bl-ionic'))
    check('spectators K⁺、NO₃⁻', page.inner_text('.bl-specs') == 'K⁺、NO₃⁻', page.inner_text('.bl-specs'))
    ch = page.inner_text('.bl-chk tr:last-child')
    check('charge row: +2 + 2×(−1) = 0 vs 0', '(+2) + 2×(−1) = 0' in ch and '✓' in ch, ch)
    shot('14-pb-done'); shot('14z-final', '.bl-final')
    # unstrike works
    for i, specs, wrong, final, spec_txt in ION:
        page.click(f'.bl-ipick button[data-r="{i}"]')
        page.click('.bl-s1'); page.click('.bl-s2')
        page.locator(f'.bl-chip[data-key="{wrong}"]').first.click()
        check(f'ion {i}: wrong pick refused', ion(0) == 'wrong' and page.locator('.bl-chip.gone').count() == 0)
        for k in specs:
            page.locator(f'.bl-chip[data-key="{k}"]').first.click()
        page.click('.bl-s3')
        got = page.inner_text('.bl-ionic') if page.locator('.bl-ionic').count() else page.inner_text('.bl-msg')
        check(f'ion {i}: {final}', ion(0) == 'done' and got == final, got)
        check(f'ion {i}: spectators {spec_txt}', page.inner_text('.bl-specs') == spec_txt, page.inner_text('.bl-specs'))
        check(f'ion {i}: no ✗ in check table', '✗' not in page.inner_text('.bl-final'))
        if i == 1:
            check('H₂SO₄: simplification ÷ 2 explained', '同除以 2' in page.inner_text('.bl-final'))
            check('H₂SO₄ split explained as strong acid', 'strong acid' in page.inner_text('.bl-why'))
            shot('15-h2so4-done')
    page.click('.bl-ire'); check('重来 resets', ion(0) == 'start' and page.locator('.bl-work .bl-chip').count() == 0)

    print('== layout')
    check('no [data-clash]', page.locator('[data-clash]').count() == 0)
    for w in (700, 1000):
        page.set_viewport_size({'width': w, 'height': 1000})
        for tab in ('bal', 'ion'):
            page.click(f'button[data-tab="{tab}"]')
            if tab == 'ion':
                page.click('.bl-ipick button[data-r="1"]'); page.click('.bl-s1'); page.click('.bl-s2')
            ov = page.evaluate("() => { const k=document.querySelector('.k'); return k.scrollWidth - k.clientWidth; }")
            check(f'width {w}, tab {tab}: no horizontal overflow', ov <= 0, str(ov))
            if w == 700: shot(f'20-w700-{tab}')
    small = page.evaluate("""() => { let m=99; document.querySelectorAll('.k *').forEach(e=>{ if(e.offsetParent && e.childNodes.length && [...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())) m=Math.min(m, parseFloat(getComputedStyle(e).fontSize)); }); return m; }""")
    check('smallest visible font >= 12px', small >= 12, str(small))

    print('== dark mode')
    ctx3 = b.new_context(viewport={'width': 1000, 'height': 1000}, device_scale_factor=2, color_scheme='dark')
    pg3 = ctx3.new_page(); pg3.on('pageerror', lambda e: errors.append(f'PAGEERROR dark {e}'))
    pg3.goto(PAGE.as_uri()); pg3.wait_for_timeout(400)
    pg3.click('.bl-pick button[data-eq="5"]')
    for k, n in enumerate([1, 6, 3, 1]):
        for _ in range(n - 1): pg3.locator(f'.bl-term[data-i="{k}"] .bl-plus').click()
    pg3.locator('.k').first.screenshot(path=str(OUT / '30-dark-bal.png'))
    pg3.click('button[data-tab="ion"]'); pg3.click('.bl-ipick button[data-r="3"]'); pg3.click('.bl-s1'); pg3.click('.bl-s2')
    pg3.locator('.bl-chip[data-key="Na|1|aq"]').first.click(); pg3.locator('.bl-chip[data-key="Cu|2|aq"]').first.click()
    pg3.locator('.k').first.screenshot(path=str(OUT / '31-dark-ion.png'))
    ctx3.close(); b.close()

check('console / page errors = 0', not errors, '; '.join(errors))
n_ok = sum(1 for r in results if r[1])
print(f'{n_ok}/{len(results)} passed')
sys.exit(0 if n_ok == len(results) else 1)
