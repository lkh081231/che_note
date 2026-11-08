"""ch15 agno3-rate test — 🔬 AgNO₃ test tubes: precipitate colors, rates, bond energies vs polarity, and quiz.

usage:
  uv run --with playwright python -I colab/tests/ch15_agno3-rate.py $COLAB_TMP/cells/ch15-agno3-rate.html <shots-dir>
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


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])

    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s} PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300)

        page.evaluate("window.T = document.querySelector('.k').agno3Hook;")

        # 1. Initial State: 3 tubes, opacities 0 at t=0
        page.evaluate("T.reset();")
        ops0 = page.evaluate("T.getOpacities();")
        check(f'{scheme}: initial opacities are 0 at t=0', ops0['chloro'] == 0 and ops0['bromo'] == 0 and ops0['iodo'] == 0, str(ops0))

        # Check 3 test tubes rendered by default
        tube_count = page.locator('.ag-tube-group').count()
        check(f'{scheme}: 3 test tubes rendered initially', tube_count == 3, f'found {tube_count}')

        # 2. Controls: Play & Pause
        page.evaluate("T.play();")
        check(f'{scheme}: play button starts animation', page.evaluate("T.isPlaying()"), 'running=True')
        page.wait_for_timeout(250)
        t_after_play = page.evaluate("T.getT();")
        check(f'{scheme}: time advances when playing', t_after_play > 0, f't={t_after_play}')

        page.evaluate("T.pause();")
        check(f'{scheme}: pause button stops animation', not page.evaluate("T.isPlaying()"), 'running=False')
        t_paused = page.evaluate("T.getT();")
        page.wait_for_timeout(100)
        t_paused_again = page.evaluate("T.getT();")
        check(f'{scheme}: time remains fixed while paused', abs(t_paused - t_paused_again) < 1e-4, f'{t_paused} vs {t_paused_again}')

        # 3. Monotonicity Across Sampled Timeline (0 .. 60)
        sample_times = [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60]
        ops_samples = []
        for st in sample_times:
            page.evaluate(f"T.setT({st});")
            ops_samples.append(page.evaluate("T.getOpacities();"))

        cl_mono = all(ops_samples[i + 1]['chloro'] >= ops_samples[i]['chloro'] for i in range(len(sample_times) - 1))
        br_mono = all(ops_samples[i + 1]['bromo'] >= ops_samples[i]['bromo'] for i in range(len(sample_times) - 1))
        i_mono = all(ops_samples[i + 1]['iodo'] >= ops_samples[i]['iodo'] for i in range(len(sample_times) - 1))
        check(f'{scheme}: opacity is monotonically non-decreasing for chloro', cl_mono)
        check(f'{scheme}: opacity is monotonically non-decreasing for bromo', br_mono)
        check(f'{scheme}: opacity is monotonically non-decreasing for iodo', i_mono)

        # 4. Threshold Rate Ordering (iodo reaches threshold first, then bromo, then chloro)
        # Threshold: opacity >= 0.25
        t_reach_iodo = next(st for i, st in enumerate(sample_times) if ops_samples[i]['iodo'] >= 0.25)
        t_reach_bromo = next(st for i, st in enumerate(sample_times) if ops_samples[i]['bromo'] >= 0.25)
        t_reach_chloro = next(st for i, st in enumerate(sample_times) if ops_samples[i]['chloro'] >= 0.25)
        order_ok = (t_reach_iodo < t_reach_bromo < t_reach_chloro)
        check(
            f'{scheme}: threshold order iodo ({t_reach_iodo}s) < bromo ({t_reach_bromo}s) < chloro ({t_reach_chloro}s)',
            order_ok,
            f'{t_reach_iodo}, {t_reach_bromo}, {t_reach_chloro}'
        )

        # 5. Precipitate Visual Differentiation in Light and Dark
        # Colors: white, cream, yellow
        colors = page.evaluate("T.getColors();")
        check(f'{scheme}: 3 precipitate colors defined and distinct', len(set(colors.values())) == 3, str(colors))

        # Pass/fail requirement: in dark mode, white precipitate must have a border / outline
        page.evaluate("T.setT(45.0);")
        white_stroke_width = page.eval_on_selector(
            '.ag-precip-white',
            'el => parseFloat(getComputedStyle(el).strokeWidth) || 0'
        )
        check(
            f'{scheme}: white precipitate has outline border (strokeWidth={white_stroke_width}px)',
            white_stroke_width >= 1.0,
            f'width={white_stroke_width}'
        )

        # 6. Bar Heights Ratio & Bond Energies (467, 346, 290, 228)
        bar_heights = page.evaluate("T.getBarHeights();")
        bar_energies = page.evaluate("T.getBarEnergies();")
        h_cf = bar_heights['C–F']
        h_ccl = bar_heights['C–Cl']
        h_cbr = bar_heights['C–Br']
        h_ci = bar_heights['C–I']

        # Check proportion tolerance < 2%
        check(f'{scheme}: C-Cl / C-F height ratio matches 346 / 467', abs((h_ccl / h_cf) - (346.0 / 467.0)) < 0.02)
        check(f'{scheme}: C-Br / C-F height ratio matches 290 / 467', abs((h_cbr / h_cf) - (290.0 / 467.0)) < 0.02)
        check(f'{scheme}: C-I / C-F height ratio matches 228 / 467', abs((h_ci / h_cf) - (228.0 / 467.0)) < 0.02)

        # 7. Check Data Booklet Values and Conclusions
        theory_text = page.locator('.ag-theory-card').inner_text()
        check(f'{scheme}: theory card contains 467, 346, 290, 228', all(str(v) in theory_text for v in (467, 346, 290, 228)))
        check(f'{scheme}: theory card concludes bond strength determines rate', 'bond strength' in theory_text and 'polarity' in theory_text)

        # 8. Bromoethane Toggle: 4 tubes, bromoethane matches 1-bromobutane rate
        page.evaluate("T.toggleBromoethane(true);")
        tube_count_4 = page.locator('.ag-tube-group').count()
        check(f'{scheme}: toggling bromoethane renders 4 test tubes', tube_count_4 == 4, f'count={tube_count_4}')
        ops_be = page.evaluate("T.getOpacities();")
        check(f'{scheme}: bromoethane opacity closely matches 1-bromobutane', abs(ops_be['bromoethane'] - ops_be['bromo']) < 0.1)
        page.evaluate("T.toggleBromoethane(false);")
        check(f'{scheme}: toggling off returns to 3 test tubes', page.locator('.ag-tube-group').count() == 3)

        # 9. Quiz Scoring & Feedback
        page.evaluate("T.resetQuiz();")
        check(f'{scheme}: quiz resets score to 0', page.evaluate("T.getScore();") == 0)

        # Q1 Wrong answer: Cl
        page.evaluate("T.answerQuiz(0, 'Cl');")
        fb1_text = page.locator('.ag-qitem[data-qi="0"] .ag-fb').inner_text()
        check(f'{scheme}: Q1 wrong option gives explanation', '不正确' in fb1_text)
        check(f'{scheme}: score is still 0 after wrong answer', page.evaluate("T.getScore();") == 0)

        # Q1 Correct answer: Br
        page.evaluate("T.answerQuiz(0, 'Br');")
        fb1_correct = page.locator('.ag-qitem[data-qi="0"] .ag-fb').inner_text()
        check(f'{scheme}: Q1 correct answer accepted', '正确' in fb1_correct)
        check(f'{scheme}: score increments to 1', page.evaluate("T.getScore();") == 1)

        # Q2 Correct answer: B (C-X bond gets weaker)
        page.evaluate("T.answerQuiz(1, 'B');")
        check(f'{scheme}: Q2 correct answer accepted, score=2', page.evaluate("T.getScore();") == 2)

        # Q3 Correct answer: B (common solvent)
        page.evaluate("T.answerQuiz(2, 'B');")
        check(f'{scheme}: Q3 correct answer accepted, score=3', page.evaluate("T.getScore();") == 3)

        # Test Show Answers & Reset buttons
        page.evaluate("T.resetQuiz();")
        check(f'{scheme}: resetQuiz clears score', page.evaluate("T.getScore();") == 0)
        page.evaluate("T.showAnswers();")
        check(f'{scheme}: showAnswers sets score to 3', page.evaluate("T.getScore();") == 3)

        # 10. Data Clash: No label collisions
        clashes = page.locator('[data-clash]').count()
        check(f'{scheme}: zero label clashes (data-clash=0)', clashes == 0, f'found {clashes}')

        # 11. Screenshots (taken in state with content at t=45)
        page.evaluate("T.setT(45.0);")
        if scheme == 'light':
            shot(page, '.k', OUT / 'shot-light.png')
            shot(page, '.ag-stage-card', OUT / 'shot-light-tubes.png')
            shot(page, '.ag-theory-card', OUT / 'shot-light-charts.png')
        elif scheme == 'dark':
            shot(page, '.k', OUT / 'shot-dark.png')
            shot(page, '.ag-stage-card', OUT / 'shot-dark-tubes.png')
            shot(page, '.ag-theory-card', OUT / 'shot-dark-charts.png')

        ctx.close()

    # 12. Responsive Viewport: 720px
    ctx720 = b.new_context(viewport={'width': 720, 'height': 1200}, device_scale_factor=2)
    page720 = ctx720.new_page()
    page720.goto(PAGE.as_uri())
    page720.wait_for_timeout(300)
    page720.evaluate("window.T = document.querySelector('.k').agno3Hook;")
    page720.evaluate("T.setT(45.0);")

    # Check horizontal scroll on .k
    overflow = page720.evaluate("() => { const el = document.querySelector('.k'); return Math.max(0, el.scrollWidth - el.clientWidth); }")
    check('720px: .k no horizontal overflow', overflow <= 1, f'overflow={overflow}px')

    # Check SVG font size (minimum >= 12px)
    min_svg_fs = page720.evaluate("T.getMinFontSize();")
    check('720px: SVG text min font size >= 12px', min_svg_fs >= 12.0, f'minFontSize={min_svg_fs:.2f}px')

    # Screenshots at 720px and zoom
    shot(page720, '.k', OUT / 'shot-720px.png')
    shot(page720, '.ag-stage', OUT / 'shot-zoom-tubes.png')
    shot(page720, '.ag-chart-box', OUT / 'shot-zoom-bars.png')

    ctx720.close()
    b.close()

# Summary
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f'\n{passed}/{total} passed')
assert len(errors) == 0, f'Console errors: {errors}'
assert passed == total, f'{total - passed} assertions failed'
