"""ch16 acidity test — 🔬 alcohol vs water: reaction with sodium & acidity comparison.

usage:
  uv run --with playwright python -I colab/tests/ch16_acidity.py $COLAB_TMP/cells/ch16-acidity.html <shots-dir>
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


MOL_ORDER = ['water', 'methanol', 'ethanol', 'propan2ol', 'tbutanol']
QUIZ_CORRECT = {0: 'B', 1: 'C', 2: 'A', 3: 'B'}

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu', '--no-sandbox'])

    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s} PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300)

        page.evaluate("window.T = document.querySelector('.k').acidityHook;")

        # =====================================================================
        # 1. Initial State & DOM Check
        # =====================================================================
        cur_tab = page.evaluate("T.getTab();")
        check(f'{scheme}: initial tab is theory', cur_tab == 'theory', str(cur_tab))

        mol_list = page.evaluate("T.getMoleculesList();")
        check(f'{scheme}: 5 molecules defined in theory tab', len(mol_list) == 5, str(mol_list))

        cur_mol = page.evaluate("T.getMolecule();")
        check(f'{scheme}: default molecule is ethanol', cur_mol == 'ethanol', str(cur_mol))

        # Check SVG rendered in single view
        theory_svg_count = page.locator('.ac-theory-svg').count()
        check(f'{scheme}: theory SVG is present', theory_svg_count == 1)

        # =====================================================================
        # 2. Molecule Selection & Data Updates
        # =====================================================================
        for mol in MOL_ORDER:
            page.evaluate(f"T.setMolecule('{mol}');")
            page.wait_for_timeout(50)
            got_mol = page.evaluate("T.getMolecule();")
            check(f'{scheme}: switched to molecule {mol}', got_mol == mol)

            title_text = page.locator('.ac-mol-title').inner_text()
            check(f'{scheme}: title updated for {mol}', mol in title_text.lower(), title_text)

        # Switch back to ethanol
        page.evaluate("T.setMolecule('ethanol');")

        # =====================================================================
        # 3. Contrast Mode (Water vs Ethanol)
        # =====================================================================
        page.evaluate("T.toggleContrast(true);")
        page.wait_for_timeout(100)
        is_contrast = page.evaluate("T.isContrast();")
        check(f'{scheme}: contrast mode enabled', is_contrast)
        check(f'{scheme}: contrast view visible', page.is_visible('.ac-contrast-view'))
        check(f'{scheme}: single view hidden', not page.is_visible('.ac-single-view'))

        # Switch back to single mode
        page.evaluate("T.toggleContrast(false);")
        page.wait_for_timeout(100)
        check(f'{scheme}: returned to single view', not page.is_visible('.ac-contrast-view') and page.is_visible('.ac-single-view'))

        # =====================================================================
        # 4. Tab 2: Reaction with Sodium Simulation
        # =====================================================================
        page.evaluate("T.setTab('sodium');")
        page.wait_for_timeout(150)
        check(f'{scheme}: switched to sodium tab', page.evaluate("T.getTab();") == 'sodium')

        # Check initial state at t=0
        page.evaluate("T.reset();")
        t0 = page.evaluate("T.getT();")
        check(f'{scheme}: initial sodium reaction time is 0.0s', abs(t0) < 1e-4, f't={t0}')

        # Play / Pause / Time progression
        page.evaluate("T.play();")
        check(f'{scheme}: play starts sodium animation', page.evaluate("T.isPlaying();"))
        page.wait_for_timeout(300)
        t_prog = page.evaluate("T.getT();")
        check(f'{scheme}: time advances when playing sodium reaction', t_prog > 0, f't={t_prog}')

        page.evaluate("T.pause();")
        check(f'{scheme}: pause stops sodium animation', not page.evaluate("T.isPlaying();"))

        t_pause1 = page.evaluate("T.getT();")
        page.wait_for_timeout(100)
        t_pause2 = page.evaluate("T.getT();")
        check(f'{scheme}: time remains fixed while paused', abs(t_pause1 - t_pause2) < 1e-4)

        # Sample timeline across [0, 2, 5, 8, 10]
        for st in [0, 2, 5, 8, 10]:
            page.evaluate(f"T.setT({st});")
            t_curr = page.evaluate("T.getT();")
            check(f'{scheme}: slider sets time {st}s', abs(t_curr - st) < 0.15)

        # Check tubes legend exists and has 3 tubes
        tubes_count = page.locator('.ac-tleg-col').count()
        check(f'{scheme}: 3 test tube explanations present in sodium tab', tubes_count == 3)

        # =====================================================================
        # 5. Tab 3: Practice Quiz
        # =====================================================================
        page.evaluate("T.setTab('quiz');")
        page.wait_for_timeout(150)
        check(f'{scheme}: switched to quiz tab', page.evaluate("T.getTab();") == 'quiz')

        page.evaluate("T.resetQuiz();")
        check(f'{scheme}: initial quiz score is 0', page.evaluate("T.getScore();") == 0)

        # Answer all 4 questions correctly
        for qi, want_opt in QUIZ_CORRECT.items():
            page.evaluate(f"T.answerQuiz({qi}, '{want_opt}');")
        check(f'{scheme}: score is 4 after answering correctly', page.evaluate("T.getScore();") == 4)

        # Check feedback boxes have .ok class
        ok_count = page.locator('.ac-fb.ok').count()
        check(f'{scheme}: all 4 feedback boxes display .ok', ok_count == 4, f'found {ok_count}')

        # Reset quiz
        page.evaluate("T.resetQuiz();")
        check(f'{scheme}: resetQuiz resets score to 0', page.evaluate("T.getScore();") == 0)

        # Show answers
        page.evaluate("T.showAnswers();")
        check(f'{scheme}: showAnswers sets score to 4', page.evaluate("T.getScore();") == 4)

        # =====================================================================
        # 6. Capture Screenshots in Meaningful States
        # =====================================================================
        # Switch back to Tab 1 (Theory) with ethanol
        page.evaluate("T.setTab('theory'); T.setMolecule('ethanol'); T.toggleContrast(false);")
        page.wait_for_timeout(150)
        if scheme == 'light':
            shot(page, '.ac-wrap', OUT / 'light-theory-ethanol.png')
            check('Screenshot: light-theory-ethanol.png captured', (OUT / 'light-theory-ethanol.png').exists())

            # Contrast view screenshot
            page.evaluate("T.toggleContrast(true);")
            page.wait_for_timeout(100)
            shot(page, '.ac-contrast-view', OUT / 'light-contrast.png')
            check('Screenshot: light-contrast.png captured', (OUT / 'light-contrast.png').exists())

            # Sodium tab screenshot at t=2.0s
            page.evaluate("T.setTab('sodium'); T.setT(2.0);")
            page.wait_for_timeout(100)
            shot(page, '.ac-wrap', OUT / 'light-sodium-reaction.png')
            check('Screenshot: light-sodium-reaction.png captured', (OUT / 'light-sodium-reaction.png').exists())
        else:
            shot(page, '.ac-wrap', OUT / 'dark-theory-ethanol.png')
            check('Screenshot: dark-theory-ethanol.png captured', (OUT / 'dark-theory-ethanol.png').exists())

            page.evaluate("T.toggleContrast(true);")
            page.wait_for_timeout(100)
            shot(page, '.ac-contrast-view', OUT / 'dark-contrast.png')
            check('Screenshot: dark-contrast.png captured', (OUT / 'dark-contrast.png').exists())

            page.evaluate("T.setTab('sodium'); T.setT(2.0);")
            page.wait_for_timeout(100)
            shot(page, '.ac-wrap', OUT / 'dark-sodium-reaction.png')
            check('Screenshot: dark-sodium-reaction.png captured', (OUT / 'dark-sodium-reaction.png').exists())

        # =====================================================================
        # 7. Narrow Viewport Test (720px)
        # =====================================================================
        print(f'== Testing narrow 720 px in {scheme}')
        page.set_viewport_size({'width': 720, 'height': 1200})
        page.wait_for_timeout(200)

        # Horizontal overflow check
        ov = page.evaluate('() => { const k = document.querySelector(".k"); return k ? (k.scrollWidth - k.clientWidth) : 0; }')
        check(f'{scheme} 720 px: no horizontal overflow on .k', ov <= 1, f'overflow={ov}px')

        # SVG text font size check: computed font size >= 12.0px and scaled >= 12.0px (visible SVGs only)
        min_fs = page.evaluate('''() => {
            const svgs = [...document.querySelectorAll('.ac-svg')].filter(s => {
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
            shot(page, '.ac-wrap', OUT / 'narrow-720.png')
            check('Screenshot: narrow-720.png captured', (OUT / 'narrow-720.png').exists())

        ctx.close()

    b.close()

# Console errors assertion
check('no console errors / page errors throughout test', len(errors) == 0, '; '.join(errors))

n = sum(1 for r in results if r[1])
print(f'\n{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
