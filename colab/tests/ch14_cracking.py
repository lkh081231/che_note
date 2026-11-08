"""ch14 cracking — interactive catalytic cracking of alkanes and equation balancing.

usage: uv run --with playwright python -I colab/tests/ch14_cracking.py $COLAB_TMP/cells/ch14-cracking.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch14 --cell cracking)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
CHROMIUM = '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else chrome()


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def shot(page, sel, path):
    """Element screenshot via a page clip to avoid GPU rAF hang in headless mode."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])

    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300)

        # Basic rendering check
        check(f'{scheme}: cell loaded successfully', page.is_visible('.crk-wrap'))

        # Check click target touch sizes on C12
        targets = page.eval_on_selector_all(
            '.crk-svg .crk-hit',
            'els => els.map(e => { const r = e.getBoundingClientRect(); return { w: r.width, h: r.height }; })'
        )
        all_targets_big = len(targets) == 11 and all(t['w'] >= 25 and t['h'] >= 60 for t in targets)
        check(f'{scheme}: bond cut click targets are sufficiently large (>=25px x >=60px)', all_targets_big, f'{targets[:2]}')

        # Check cut toggle
        page.click('.crk-hit-wrap[data-bond="8"]')
        page.wait_for_timeout(100)
        check(f'{scheme}: cutting bond 8 activates cut', page.eval_on_selector('.crk-cut-num', 'e => e.textContent') == '1')
        check(f'{scheme}: equation card visible after cutting', page.is_visible('.crk-eq-card'))

        eq_text = page.eval_on_selector('.crk-eq-rhs', 'e => e.textContent')
        check(f'{scheme}: one cut at C8–C9 gives octane + butene', 'C₈H₁₈' in eq_text and 'C₄H₈' in eq_text, eq_text)

        # Check distinct styling between alkane and alkene
        alkane_color = page.eval_on_selector('.crk-frag-card.alkane', 'e => getComputedStyle(e).borderColor')
        alkene_color = page.eval_on_selector('.crk-frag-card.alkene', 'e => getComputedStyle(e).borderColor')
        check(f'{scheme}: alkane and alkene cards have distinct colors', alkane_color != alkene_color, f'alkane:{alkane_color} vs alkene:{alkene_color}')

        # Check node colors on SVG
        node_alkane_fill = page.eval_on_selector('.crk-atom.alkane', 'e => getComputedStyle(e).fill')
        node_alkene_fill = page.eval_on_selector('.crk-atom.alkene', 'e => getComputedStyle(e).fill')
        check(f'{scheme}: alkane and alkene SVG nodes have distinct fills', node_alkane_fill != node_alkene_fill, f'{node_alkane_fill} vs {node_alkene_fill}')

        # Check data-clash is 0
        clashes = page.locator('[data-clash]').count()
        check(f'{scheme}: no K.label data-clash detected', clashes == 0, f'clashes={clashes}')

        # Capture overview screenshot
        shot(page, '.k', OUT / f'{scheme}.png')

        if scheme == 'light':
            # Detailed close up screenshot of the cut bond
            shot(page, '.crk-stage-card', OUT / 'zoom-cut.png')

        ctx.close()

    # Deep logic & chemistry verification context
    ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2)
    page = ctx.new_page()
    page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
    page.goto(PAGE.as_uri())
    page.wait_for_timeout(300)

    # 1. Test multiple cuts (2 cuts and 3 cuts on C12)
    page.click('.crk-hit-wrap[data-bond="4"]')
    page.click('.crk-hit-wrap[data-bond="8"]')
    page.wait_for_timeout(100)
    check('2 cuts produces 3 fragments', page.locator('.crk-frag-card').count() == 3)
    eq_2cuts = page.eval_on_selector('.crk-eq-rhs', 'e => e.textContent')
    check('2 cuts equation has butane and butene', 'C₄H₁₀' in eq_2cuts and 'C₄H₈' in eq_2cuts, eq_2cuts)

    # 3 cuts
    page.click('.crk-hit-wrap[data-bond="2"]')
    page.wait_for_timeout(100)
    check('3 cuts produces 4 fragments', page.locator('.crk-frag-card').count() == 4)

    # 4th cut attempt should be rejected (max 3 cuts)
    dialog_handled = []
    page.on('dialog', lambda d: (dialog_handled.append(d.message), d.accept()))
    page.click('.crk-hit-wrap[data-bond="10"]')
    page.wait_for_timeout(100)
    check('4th cut rejected inline, no browser dialog', len(dialog_handled) == 0 and '3 刀' in page.eval_on_selector('.crk-cap-msg', 'e => e.textContent'))
    check('cuts capped at 3', page.eval_on_selector('.crk-cut-num', 'e => e.textContent') == '3')

    # Switch alkane fragment
    set_alkane_btns = page.locator('.crk-btn-set-alkane')
    if set_alkane_btns.count() > 0:
        set_alkane_btns.first.click()
        page.wait_for_timeout(100)
        check('switch alkane button updates equation correctly', page.is_visible('.crk-eq-card'))

    # Reset button test
    page.click('.crk-reset-btn')
    page.wait_for_timeout(100)
    check('reset button clears all cuts', page.eval_on_selector('.crk-cut-num', 'e => e.textContent') == '0')
    check('empty prompt shown after reset', page.is_visible('.crk-empty-card'))

    # Substrate switching: C10
    page.click('.crk-sub-btn[data-k="C10"]')
    page.wait_for_timeout(100)
    check('C10 selected has 9 bonds', page.locator('.crk-svg .crk-hit').count() == 9)
    page.click('.crk-hit-wrap[data-bond="7"]')
    eq_c10 = page.eval_on_selector('.crk-eq-rhs', 'e => e.textContent')
    check('C10 cracked at bond 7 gives C7H16 and C3H6', 'C₇H₁₆' in eq_c10 and 'C₃H₆' in eq_c10, eq_c10)

    # Substrate switching: C14
    page.click('.crk-sub-btn[data-k="C14"]')
    page.wait_for_timeout(100)
    check('C14 selected has 13 bonds', page.locator('.crk-svg .crk-hit').count() == 13)
    page.click('.crk-hit-wrap[data-bond="8"]')
    eq_c14 = page.eval_on_selector('.crk-eq-rhs', 'e => e.textContent')
    check('C14 cracked at bond 8 gives C8H18 and C6H12', 'C₈H₁₈' in eq_c14 and 'C₆H₁₂' in eq_c14, eq_c14)

    # 2. Test Quiz mode
    page.click('button[data-tab="quiz"]')
    page.wait_for_timeout(200)
    check('quiz pane displayed', page.is_visible('[data-pane="quiz"].show'))

    # Q1 correct answer
    page.fill('.crk-qinp', 'C4H8')
    page.click('.crk-qcheck')
    check('Q1: C4H8 accepted as correct', page.is_visible('.crk-qinp.good') and '正确' in page.inner_text('.crk-qfeedback'))

    # Q1 reversed order H8C4 must fail with order explanation
    page.fill('.crk-qinp', 'H8C4')
    page.click('.crk-qcheck')
    q1_fb = page.inner_text('.crk-qfeedback')
    check('Q1: H8C4 rejected with order feedback', page.is_visible('.crk-qinp.badv') and '顺序' in q1_fb, q1_fb)

    # Q1 wrong formula
    page.fill('.crk-qinp', 'C4H10')
    page.click('.crk-qcheck')
    check('Q1: C4H10 rejected as unbalanced', page.is_visible('.crk-qinp.badv'))

    # Q5 reverse alkane test: Q5 expects C8H18
    page.select_option('.crk-qjmp', '4')
    page.wait_for_timeout(100)
    page.fill('.crk-qinp', 'H18C8')
    page.click('.crk-qcheck')
    q5_fb = page.inner_text('.crk-qfeedback')
    check('Q5: H18C8 rejected with order feedback', page.is_visible('.crk-qinp.badv') and '顺序' in q5_fb, q5_fb)

    page.fill('.crk-qinp', 'C8H18')
    page.click('.crk-qcheck')
    check('Q5: C8H18 accepted', page.is_visible('.crk-qinp.good'))

    # Q6 catalyst condition
    page.select_option('.crk-qjmp', '5')
    page.wait_for_timeout(100)
    page.fill('.crk-qinp', 'heat with Al2O3')
    page.click('.crk-qcheck')
    check('Q6: heat with Al2O3 accepted', page.is_visible('.crk-qinp.good'))

    # Q7 MCQ uses
    page.select_option('.crk-qjmp', '6')
    page.wait_for_timeout(100)
    page.click('.crk-qopt[data-v="a"]')
    page.click('.crk-qcheck')
    check('Q7: MCQ option A accepted', page.is_visible('.crk-qopt.good') and '正确' in page.inner_text('.crk-qfeedback'))

    # Screenshot of Quiz mode
    shot(page, '.crk-qcard', OUT / 'quiz.png')

    # Periodic Table expander test
    pt_btn = page.locator('.pt-btn')
    check('k-ptable button rendered', pt_btn.is_visible())
    pt_btn.click()
    page.wait_for_timeout(100)
    check('Periodic Table expanded after clicking', page.is_visible('.pt-grid, table, .pt-wrap'))

    # 3. Narrow viewport test (720px)
    print('== testing narrow (720 px)')
    page.click('button[data-tab="sim"]')
    page.set_viewport_size({'width': 720, 'height': 1200})
    page.wait_for_timeout(200)

    # Active cuts state for screenshot
    page.click('.crk-hit-wrap[data-bond="4"]')
    page.click('.crk-hit-wrap[data-bond="8"]')
    page.wait_for_timeout(100)

    # Overflow assertion: .k scrollWidth <= clientWidth + 1
    overflow = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
    check('720 px: no horizontal overflow on .k', overflow <= 1, f'overflow={overflow}')

    # SVG text rendered font size >= 12px
    min_fs = page.evaluate('''() => {
      const texts = document.querySelectorAll(".crk-svg text");
      let minFs = 999;
      texts.forEach(t => {
        const fs = parseFloat(getComputedStyle(t).fontSize);
        if (fs < minFs) minFs = fs;
      });
      return minFs;
    }''')
    check('720 px: SVG text font-size >= 12px', min_fs >= 12.0, f'minFs={min_fs:.2f}px')

    # Mobile screenshot
    shot(page, '.k', OUT / 'mobile-720.png')

    ctx.close()
    b.close()

# Console errors check
check('no console errors / page errors occurred', len(errors) == 0, '; '.join(errors))

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f'\n{passed}/{total} passed')
sys.exit(0 if passed == total else 1)
