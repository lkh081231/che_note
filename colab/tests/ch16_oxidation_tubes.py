"""ch16 oxidation-tubes test — 🔬 K₂Cr₂O₇ test tubes: 1°/2°/3° alcohol oxidation under distillation vs reflux.

usage:
  uv run --with playwright python -I colab/tests/ch16_oxidation_tubes.py $COLAB_TMP/cells/ch16-oxidation-tubes.html <shots-dir>
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
    """Element screenshot via bounding box clip to avoid rAF freeze in headless chromium."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + window.scrollX, y: r.y + window.scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


ALCOHOL_LIST = ['ethanol', 'propan1ol', 'mpropan1ol', 'propan2ol', 'butan2ol', 'tbutanol']
QUIZ_CORRECT = {0: 'B', 1: 'B', 2: 'B', 3: 'A'}

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu', '--no-sandbox'])

    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s} PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300)

        page.evaluate("window.T = document.querySelector('.k').oxTubesHook;")

        # =====================================================================
        # 1. Initial State & DOM Check
        # =====================================================================
        cur_tab = page.evaluate("T.getTab();")
        check(f'{scheme}: initial tab is explorer', cur_tab == 'explorer', str(cur_tab))

        cur_alc = page.evaluate("T.getAlcohol();")
        check(f'{scheme}: default alcohol is ethanol', cur_alc == 'ethanol', str(cur_alc))

        cur_cond = page.evaluate("T.getCondition();")
        check(f'{scheme}: default condition is reflux', cur_cond == 'reflux', str(cur_cond))

        cur_ox = page.evaluate("T.getOxidant();")
        check(f'{scheme}: default oxidant is dichromate', cur_ox == 'dichromate', str(cur_ox))

        # Check SVG rendered in stage
        app_svg_count = page.locator('.ox-app-svg').count()
        check(f'{scheme}: apparatus SVG is present', app_svg_count == 1)

        # =====================================================================
        # 2. 1° Alcohol: Distillation (aldehyde) vs Reflux (carboxylic acid)
        # =====================================================================
        page.evaluate("T.setAlcohol('ethanol'); T.setCondition('distil');")
        page.wait_for_timeout(50)
        prod_name_dist = page.locator('.ox-prod-name').inner_text()
        check(f'{scheme}: ethanol + distillation produces ethanal', 'ethanal' in prod_name_dist.lower(), prod_name_dist)

        page.evaluate("T.setCondition('reflux');")
        page.wait_for_timeout(50)
        prod_name_ref = page.locator('.ox-prod-name').inner_text()
        check(f'{scheme}: ethanol + reflux produces ethanoic acid', 'ethanoic acid' in prod_name_ref.lower(), prod_name_ref)

        # =====================================================================
        # 3. 2° Alcohol: Propan-2-ol produces ketone in both distil and reflux
        # =====================================================================
        page.evaluate("T.setAlcohol('propan2ol'); T.setCondition('distil');")
        page.wait_for_timeout(50)
        prod_2d = page.locator('.ox-prod-name').inner_text()
        check(f'{scheme}: propan-2-ol + distil produces propanone', 'propanone' in prod_2d.lower(), prod_2d)

        page.evaluate("T.setCondition('reflux');")
        page.wait_for_timeout(50)
        prod_2r = page.locator('.ox-prod-name').inner_text()
        check(f'{scheme}: propan-2-ol + reflux produces propanone', 'propanone' in prod_2r.lower(), prod_2r)

        # =====================================================================
        # 4. 3° Alcohol: 2-Methylpropan-2-ol does not react (remains orange)
        # =====================================================================
        page.evaluate("T.setAlcohol('tbutanol');")
        page.wait_for_timeout(50)
        prod_3 = page.locator('.ox-prod-name').inner_text()
        badge_3 = page.locator('.ox-res-badge').inner_text()
        check(f'{scheme}: 2-methylpropan-2-ol product is "No reaction"', 'no reaction' in prod_3.lower(), prod_3)
        check(f'{scheme}: 2-methylpropan-2-ol badge is "remains orange"', 'remains orange' in badge_3.lower(), badge_3)

        # =====================================================================
        # 5. Oxidising Agent Switching & Color Progress
        # =====================================================================
        # Switch back to ethanol + reflux
        page.evaluate("T.setAlcohol('ethanol'); T.setCondition('reflux'); T.setOxidant('dichromate');")
        page.evaluate("T.setProgress(0);")
        c0 = page.evaluate("T.getColor();")
        page.evaluate("T.setProgress(100);")
        c100 = page.evaluate("T.getColor();")
        check(f'{scheme}: K2Cr2O7 color changes with progress', c0 != c100, f'{c0} -> {c100}')

        # Switch to KMnO4 (purple -> colourless)
        page.evaluate("T.setOxidant('manganate'); T.setProgress(0);")
        badge_km = page.locator('.ox-res-badge').inner_text()
        check(f'{scheme}: KMnO4 badge specifies purple to colourless', 'purple' in badge_km and 'colourless' in badge_km, badge_km)

        # =====================================================================
        # 6. Tab 2: 3-Tube Parallel Distinguishing Test
        # =====================================================================
        page.evaluate("T.setTab('parallel');")
        page.wait_for_timeout(150)
        check(f'{scheme}: switched to parallel tab', page.evaluate("T.getTab();") == 'parallel')

        page.evaluate("T.setParallelWarmed(false);")
        check(f'{scheme}: parallel test initially not warmed', not page.evaluate("T.isParallelWarmed();"))

        # Warm tubes
        page.evaluate("T.setParallelWarmed(true);")
        page.wait_for_timeout(100)
        check(f'{scheme}: parallel test warmed', page.evaluate("T.isParallelWarmed();"))

        ptube_cards = page.locator('.ox-ptube-card')
        check(f'{scheme}: 3 parallel tube cards present', ptube_cards.count() == 3)

        # =====================================================================
        # 7. Tab 3: Practice Quiz
        # =====================================================================
        page.evaluate("T.setTab('quiz');")
        page.wait_for_timeout(150)
        check(f'{scheme}: switched to quiz tab', page.evaluate("T.getTab();") == 'quiz')

        page.evaluate("T.resetQuiz();")
        check(f'{scheme}: initial quiz score is 0', page.evaluate("T.getScore();") == 0)

        # Answer all 4 questions correctly
        for qi, want_opt in QUIZ_CORRECT.items():
            page.evaluate(f"T.answerQuiz({qi}, '{want_opt}');")
        check(f'{scheme}: score is 4 after answering all correctly', page.evaluate("T.getScore();") == 4)

        # Check feedback boxes have .ok class
        ok_count = page.locator('.ox-fb.ok').count()
        check(f'{scheme}: all 4 quiz feedbacks display .ok', ok_count == 4, f'found {ok_count}')

        # Reset quiz
        page.evaluate("T.resetQuiz();")
        check(f'{scheme}: resetQuiz resets score to 0', page.evaluate("T.getScore();") == 0)

        # Show answers
        page.evaluate("T.showAnswers();")
        check(f'{scheme}: showAnswers sets score to 4', page.evaluate("T.getScore();") == 4)

        # =====================================================================
        # 8. Capture Screenshots in Meaningful States
        # =====================================================================
        # Tab 1: Ethanol Distillation vs Reflux
        page.evaluate("T.setTab('explorer'); T.setAlcohol('ethanol'); T.setCondition('distil'); T.setOxidant('dichromate'); T.setProgress(60);")
        page.wait_for_timeout(150)
        if scheme == 'light':
            shot(page, '.ox-wrap', OUT / 'light-distillation-ethanol.png')
            check('Screenshot: light-distillation-ethanol.png captured', (OUT / 'light-distillation-ethanol.png').exists())

            # Reflux screenshot
            page.evaluate("T.setCondition('reflux'); T.setProgress(100);")
            page.wait_for_timeout(100)
            shot(page, '.ox-wrap', OUT / 'light-reflux-ethanol.png')
            check('Screenshot: light-reflux-ethanol.png captured', (OUT / 'light-reflux-ethanol.png').exists())

            # Parallel tab screenshot
            page.evaluate("T.setTab('parallel'); T.setParallelWarmed(true);")
            page.wait_for_timeout(100)
            shot(page, '.ox-wrap', OUT / 'light-parallel-tubes.png')
            check('Screenshot: light-parallel-tubes.png captured', (OUT / 'light-parallel-tubes.png').exists())
        else:
            shot(page, '.ox-wrap', OUT / 'dark-distillation-ethanol.png')
            check('Screenshot: dark-distillation-ethanol.png captured', (OUT / 'dark-distillation-ethanol.png').exists())

            page.evaluate("T.setCondition('reflux'); T.setProgress(100);")
            page.wait_for_timeout(100)
            shot(page, '.ox-wrap', OUT / 'dark-reflux-ethanol.png')
            check('Screenshot: dark-reflux-ethanol.png captured', (OUT / 'dark-reflux-ethanol.png').exists())

            page.evaluate("T.setTab('parallel'); T.setParallelWarmed(true);")
            page.wait_for_timeout(100)
            shot(page, '.ox-wrap', OUT / 'dark-parallel-tubes.png')
            check('Screenshot: dark-parallel-tubes.png captured', (OUT / 'dark-parallel-tubes.png').exists())

        # =====================================================================
        # 9. Narrow Viewport Test (720px)
        # =====================================================================
        print(f'== Testing narrow 720 px in {scheme}')
        page.set_viewport_size({'width': 720, 'height': 1200})
        page.wait_for_timeout(200)

        # Horizontal overflow check
        ov = page.evaluate('() => { const k = document.querySelector(".k"); return k ? (k.scrollWidth - k.clientWidth) : 0; }')
        check(f'{scheme} 720 px: no horizontal overflow on .k', ov <= 1, f'overflow={ov}px')

        # SVG text font size check: computed font size >= 12.0px and scaled >= 12.0px (visible SVGs only)
        min_fs = page.evaluate('''() => {
            const svgs = [...document.querySelectorAll('.ox-svg')].filter(s => {
                const r = s.getBoundingClientRect();
                return r.width > 0 && r.height > 0 && !s.closest('[hidden]');
            });
            if (svgs.length === 0) return 0.0;
            let minFs = 999;
            for (const s of svgs) {
                const vbW = s.viewBox.baseVal.width || 1;
                const rW = s.getBoundingClientRect().width;
                const k = rW / vbW;
                const texts = [...s.querySelectorAll('text')];
                for (const t of texts) {
                    const fs = parseFloat(getComputedStyle(t).fontSize) * k;
                    if (fs < minFs) minFs = fs;
                }
            }
            return minFs === 999 ? 0.0 : minFs;
        }''')
        check(f'{scheme} 720 px: SVG text scaled font-size >= 12px', min_fs >= 12.0, f'minFs={min_fs:.2f}px')

        if scheme == 'light':
            shot(page, '.ox-wrap', OUT / 'narrow-720.png')
            check('Screenshot: narrow-720.png captured', (OUT / 'narrow-720.png').exists())

        ctx.close()

    b.close()

# Console errors assertion
check('no console errors / page errors throughout test', len(errors) == 0, '; '.join(errors))

n = sum(1 for r in results if r[1])
print(f'\n{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
