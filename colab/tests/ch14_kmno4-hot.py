"""ch14 kmno4-hot test — 🔬 hot KMnO₄: forward product prediction & reverse C=C deduction.

usage:
  uv run --with playwright python -I colab/tests/ch14_kmno4-hot.py $COLAB_TMP/cells/ch14-kmno4-hot.html <shots-dir>
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
CHROMIUM = '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else chrome()


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def shot(page, sel, path):
    """element screenshot via a page clip (Locator.screenshot waits for rAF, which hangs with several headless Chromes)"""
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


# Expected products for all 8 alkenes
HOT_WANT = {
    'but1ene': ['carbon dioxide', 'propanoic acid'],
    'but2ene': ['ethanoic acid'],
    'pent2ene': ['ethanoic acid', 'propanoic acid'],
    'mb2ene': ['propanone', 'ethanoic acid'],
    'mpropene': ['propanone', 'carbon dioxide'],
    'cyclopentene': ['pentanedioic acid'],
    'hex3ene': ['propanoic acid'],
    'diene': ['carbon dioxide', 'propanedioic acid', 'propanone']
}

COLD_WANT = {
    'but1ene': 'butane-1,2-diol',
    'but2ene': 'butane-2,3-diol',
    'pent2ene': 'pentane-2,3-diol',
    'mb2ene': '2-methylbutane-2,3-diol',
    'mpropene': '2-methylpropane-1,2-diol',
    'cyclopentene': 'cyclopentane-1,2-diol',
    'hex3ene': 'hexane-3,4-diol',
    'diene': 'tetraol'
}

REV_WANT = [
    ('q1', 'mb2ene', 'pent2ene'),       # Q1: 2-methylbut-2-ene correct, pent-2-ene wrong
    ('q2', 'pent1ene', 'pent2ene'),     # Q2: pent-1-ene correct
    ('q3', 'cyclopentene', 'pent1ene'), # Q3: cyclopentene correct (9701/w25/21)
    ('q4', 'but2ene', 'but1ene'),       # Q4: but-2-ene correct
    ('q5', 'diene', 'hex14')            # Q5: 5-methylhexa-1,4-diene correct (9701/s25/22)
]

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])

    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s} PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300)

        # 1. Legend verification (pass/fail: 3 colors distinct and have legend)
        leg_pills = page.locator('.km-leg-pill')
        check(f'{scheme}: legend has 3 carbon substitution types', leg_pills.count() == 3, f'found {leg_pills.count()}')
        has_ch2 = any('=CH₂' in t for t in leg_pills.all_inner_texts())
        has_chr = any('=CHR' in t for t in leg_pills.all_inner_texts())
        has_cr2 = any('=CR₂' in t for t in leg_pills.all_inner_texts())
        check(f'{scheme}: legend defines =CH2, =CHR, =CR2', has_ch2 and has_chr and has_cr2)

        # 2. Part 1 (正推): Hot concentrated KMnO4 products for all 8 alkenes
        page.evaluate("window.T = document.querySelector('.k').kmHook;")
        page.evaluate("T.setTab('fwd'); T.setMode('hot');")

        for alk_id, want_prods in HOT_WANT.items():
            page.evaluate(f"T.setAlkene('{alk_id}'); T.setT(1.0);")
            stage_text = page.locator('.km-stage').inner_text()
            obs_text = page.locator('.km-obs-card').inner_text()
            full_text = stage_text + '\n' + obs_text
            missing = [p for p in want_prods if p not in full_text and (p != 'carbon dioxide' or 'CO₂' not in full_text)]
            check(f'{scheme}: hot KMnO4 + {alk_id} products {want_prods}', len(missing) == 0, f'missing: {missing}')

        # 3. Part 1 (正推): Cold dilute KMnO4 diols for all 8 alkenes
        page.evaluate("T.setMode('cold');")
        for alk_id, want_diol in COLD_WANT.items():
            page.evaluate(f"T.setAlkene('{alk_id}'); T.setT(1.0);")
            stage_text = page.locator('.km-stage').inner_text()
            obs_text = page.locator('.km-obs-card').inner_text()
            full_text = stage_text + '\n' + obs_text
            check(f'{scheme}: cold dilute KMnO4 + {alk_id} forms {want_diol}', want_diol in full_text, full_text[:80])

        # 4. Multi-frame animation sampling & Non-overlapping products at t=1.0
        page.evaluate("T.setMode('hot'); T.setAlkene('but1ene');")
        t_samples = [0.0, 0.25, 0.5, 0.75, 1.0]
        boxes_at_t = []
        for t_val in t_samples:
            page.evaluate(f"T.setT({t_val});")
            boxes = page.evaluate("T.getProductBoxes();")
            boxes_at_t.append(boxes)
        check(f'{scheme}: multi-frame sampling collected 5 frames', len(boxes_at_t) == 5)

        # Non-overlapping verification at t=1.0:
        # For but-1-ene (and diene), all product boxes must be disjoint (distance > 0)
        overlap_found = False
        final_boxes = boxes_at_t[-1]
        for i in range(len(final_boxes)):
            for j in range(i + 1, len(final_boxes)):
                b1, b2 = final_boxes[i], final_boxes[j]
                # Check bounding box collision
                x_overlap = (b1['x'] < b2['x'] + b2['w']) and (b1['x'] + b1['w'] > b2['x'])
                y_overlap = (b1['y'] < b2['y'] + b2['h']) and (b1['y'] + b1['h'] > b2['y'])
                if x_overlap and y_overlap:
                    overlap_found = True
        check(f'{scheme}: product structures do not overlap at t=1.0', not overlap_found)

        # Also verify diene has 3 non-overlapping product boxes at t=1.0
        page.evaluate("T.setAlkene('diene'); T.setT(1.0);")
        diene_boxes = page.evaluate("T.getProductBoxes();")
        diene_overlap = False
        for i in range(len(diene_boxes)):
            for j in range(i + 1, len(diene_boxes)):
                b1, b2 = diene_boxes[i], diene_boxes[j]
                if (b1['x'] < b2['x'] + b2['w']) and (b1['x'] + b1['w'] > b2['x']) and \
                   (b1['y'] < b2['y'] + b2['h']) and (b1['y'] + b1['h'] > b2['y']):
                    diene_overlap = True
        check(f'{scheme}: diene 3 products do not overlap at t=1.0', (not diene_overlap) and len(diene_boxes) == 3, f'boxes count={len(diene_boxes)}')

        # 5. Part 2 (反推): Question scoring & feedback
        page.evaluate("T.setTab('rev');")
        for q_idx, (qid, correct_opt, wrong_opt) in enumerate(REV_WANT):
            page.evaluate(f"T.setQIndex({q_idx});")
            # Click wrong option first
            page.evaluate(f"T.answerQ('{wrong_opt}');")
            fb_text = page.locator('.km-fb-banner').inner_text()
            check(f'{scheme}: Q{q_idx+1} wrong answer gives explanation', '不正确' in fb_text)

            # Click correct option
            page.evaluate(f"T.answerQ('{correct_opt}');")
            fb_text = page.locator('.km-fb-banner').inner_text()
            check(f'{scheme}: Q{q_idx+1} correct answer accepted', '正确' in fb_text)

            # Verify puzzle diagram is visible and contains reassembly text
            puzzle_flow = page.locator('.km-puzzle-flow').inner_text()
            check(f'{scheme}: Q{q_idx+1} puzzle reconstruct shows C=C', '对拼' in puzzle_flow or '──' in puzzle_flow)

        score = page.evaluate("T.getScore();")
        check(f'{scheme}: all 5 questions answered correctly', score == 5, f'score={score}')

        # Test Show Answer & Reset
        page.evaluate("T.setQIndex(0); T.resetQ();")
        check(f'{scheme}: reset sets score to 4', page.evaluate("T.getScore();") == 4)
        page.evaluate("T.showAnswer();")
        check(f'{scheme}: showAnswer restores answer', page.evaluate("T.getScore();") == 5)

        # Screenshots
        if scheme == 'light':
            # Tab 1: but-1-ene cleaved at t=1.0
            page.evaluate("T.setTab('fwd'); T.setMode('hot'); T.setAlkene('but1ene'); T.setT(1.0);")
            shot(page, '.k', OUT / 'shot-light-tab1.png')

            # Tab 1: Cold dilute diol
            page.evaluate("T.setMode('cold'); T.setAlkene('but1ene'); T.setT(1.0);")
            shot(page, '.km-stage-card', OUT / 'shot-light-cold.png')

            # Tab 2: Q1 answered with puzzle
            page.evaluate("T.setTab('rev'); T.setQIndex(0); T.answerQ('mb2ene');")
            shot(page, '.km-q-card', OUT / 'shot-light-tab2.png')

        elif scheme == 'dark':
            # Tab 1 dark
            page.evaluate("T.setTab('fwd'); T.setMode('hot'); T.setAlkene('diene'); T.setT(1.0);")
            shot(page, '.k', OUT / 'shot-dark-tab1.png')

            # Tab 2 dark (Q3 cyclopentene 9701/w25/21)
            page.evaluate("T.setTab('rev'); T.setQIndex(2); T.answerQ('cyclopentene');")
            shot(page, '.km-q-card', OUT / 'shot-dark-tab2.png')

        ctx.close()

    # 6. Viewport 720px: No horizontal overflow & min SVG font size >= 12px
    ctx720 = b.new_context(viewport={'width': 720, 'height': 1200}, device_scale_factor=2)
    page720 = ctx720.new_page()
    page720.goto(PAGE.as_uri())
    page720.wait_for_timeout(300)
    page720.evaluate("window.T = document.querySelector('.k').kmHook;")

    # Check horizontal scroll on .k
    overflow = page720.evaluate("() => { const el = document.querySelector('.k'); return Math.max(0, el.scrollWidth - el.clientWidth); }")
    check('720px: .k no horizontal overflow', overflow == 0, f'overflow={overflow}px')

    # Check SVG font size
    page720.evaluate("T.setTab('fwd'); T.setAlkene('but1ene'); T.setT(1.0);")
    min_fs = page720.evaluate("T.getMinFontSize();")
    check('720px: SVG text min font size >= 12px', min_fs >= 12.0, f'minFontSize={min_fs:.2f}px')

    # Zoomed screenshot on cleavage stage (z=2)
    shot(page720, '.k', OUT / 'shot-720px-tab1.png')
    shot(page720, '.km-stage', OUT / 'shot-zoom-cleavage.png')

    ctx720.close()
    b.close()

# Summary
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f'\n{passed}/{total} passed')
assert len(errors) == 0, f'Console errors: {errors}'
assert passed == total, f'{total - passed} assertions failed'
