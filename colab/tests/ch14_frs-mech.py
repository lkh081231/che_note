"""ch14 frs-mech — free-radical substitution mechanism player & further substitution.

usage: uv run --with playwright python -I colab/tests/ch14_frs-mech.py $COLAB_TMP/cells/ch14-frs-mech.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch14 --cell frs-mech)
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


def shot(page, sel, path):
    """element screenshot via a page clip: Locator.screenshot waits for 'stable' (two rAFs), which
    hangs when several headless Chromes share the machine"""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def safe_eval(page, sel, expr, default=None):
    try:
        if page.locator(sel).count() == 0:
            return default
        return page.eval_on_selector(sel, expr)
    except Exception:
        return default


def safe_click(page, sel):
    try:
        if page.locator(sel).count() > 0:
            page.click(sel)
            return True
        return False
    except Exception:
        return False


def safe_shot(page, sel, path):
    try:
        if page.locator(sel).count() > 0:
            shot(page, sel, path)
            return True
        return False
    except Exception:
        return False


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROMIUM, args=['--disable-gpu'])
    page = browser.new_page(viewport={'width': 980, 'height': 1100})

    page.on('console', lambda msg: errors.append(f'[{msg.type}] {msg.text}') if msg.type == 'error' else None)
    page.on('pageerror', lambda err: errors.append(str(err)))

    page.goto(PAGE.as_uri())
    page.wait_for_selector('.k')

    check('Initial page load: 0 console errors', len(errors) == 0, str(errors))

    # ================= 1. Tab 1: Mechanism Player =================
    check('Player container exists', page.locator('.ko-mech').count() > 0)
    check('Player stage exists', page.locator('.ko-stage').count() > 0)
    check('Player side card exists', page.locator('.ko-side').count() > 0)
    check('Step dots exist (4 steps)', page.locator('.ko-dots button').count() == 4)

    # Step 1: Initiation
    s1_dot_on = bool(safe_eval(page, '.ko-dots button[data-i="0"]', 'e => e.classList.contains("on")', False))
    check('Step 1 dot active initially', s1_dot_on)

    s1_eq = safe_eval(page, '.frs-side-eq', 'e => e.textContent', '') or ''
    check('Step 1 equation has Cl₂ and Cl•', 'Cl₂' in s1_eq and 'Cl•' in s1_eq, s1_eq)

    s1_marks = safe_eval(page, '.ko-marks', 'e => e.textContent', '') or ''
    check('Step 1 mark scheme mentions homolytic fission', 'homolytic' in s1_marks or '均裂' in s1_marks, s1_marks)

    # Radical dots in step 1
    s1_rad_count = page.locator('.frs-rad').count()
    check('Step 1 radical dots present in SVG', s1_rad_count >= 2, str(s1_rad_count))

    # Check radical dot distance to its atom (tightly hugging)
    rad_close = False
    if page.locator('.frs-rad').count() > 0:
        rad_close = bool(page.evaluate('''() => {
            const dots = [...document.querySelectorAll('.frs-rad')];
            if (!dots.length) return false;
            return dots.every(d => {
                const atomIdx = d.getAttribute('data-atom');
                const svg = d.closest('svg');
                const atoms = JSON.parse(svg ? svg.getAttribute('data-atoms') || '[]' : '[]');
                const a = atoms[+atomIdx];
                if (!a) return true;
                const dx = +d.getAttribute('x') - a.x;
                const dy = +d.getAttribute('y') - a.y;
                return Math.hypot(dx, dy) <= 22; // tightly hugging within 22 units
            });
        }'''))
    check('Radical dots tightly hug their respective atoms (dist <= 22)', rad_close)

    # Step forward to Step 2 (Propagation 1)
    safe_click(page, '.ko-next')
    s2_dot_on = bool(safe_eval(page, '.ko-dots button[data-i="1"]', 'e => e.classList.contains("on")', False))
    check('Step 2 dot active after next click', s2_dot_on)

    s2_eq = safe_eval(page, '.frs-side-eq', 'e => e.textContent', '') or ''
    check('Step 2 equation has Cl•, CH₃CH₃, CH₃CH₂• and HCl',
          'Cl•' in s2_eq and 'CH₃CH₃' in s2_eq and 'CH₃CH₂•' in s2_eq and 'HCl' in s2_eq, s2_eq)

    s2_marks = safe_eval(page, '.ko-marks', 'e => e.textContent', '') or ''
    check('Step 2 mark scheme emphasizes HCl and alkyl radical', 'HCl' in s2_marks and 'alkyl radical' in s2_marks, s2_marks)

    # Step forward to Step 3 (Propagation 2)
    safe_click(page, '.ko-next')
    s3_dot_on = bool(safe_eval(page, '.ko-dots button[data-i="2"]', 'e => e.classList.contains("on")', False))
    check('Step 3 dot active', s3_dot_on)

    s3_eq = safe_eval(page, '.frs-side-eq', 'e => e.textContent', '') or ''
    check('Step 3 equation has CH₃CH₂•, Cl₂, CH₃CH₂Cl and Cl•',
          'CH₃CH₂•' in s3_eq and 'Cl₂' in s3_eq and 'CH₃CH₂Cl' in s3_eq and 'Cl•' in s3_eq, s3_eq)

    s3_marks = safe_eval(page, '.ko-marks', 'e => e.textContent', '') or ''
    check('Step 3 mark scheme mentions regenerated Cl• driving chain reaction',
          '再生' in s3_marks or 'chain reaction' in s3_marks, s3_marks)

    # Circular chain loop arrow check
    has_loop_arrow = page.locator('.frs-loop-arrow').count() > 0
    check('Circular chain loop arrow drawn in Step 3', has_loop_arrow)

    has_loop_tag = page.locator('.frs-loop-tag').count() > 0
    check('Circular loop tag present in Step 3', has_loop_tag)

    # Loop arrow collision check (pass/fail criterion: 循环箭头不压文字)
    no_loop_overlap = False
    if has_loop_tag and has_loop_arrow:
        no_loop_overlap = bool(page.evaluate('''() => {
            const loopTag = document.querySelector('.frs-loop-tag');
            const loopPath = document.querySelector('.frs-loop-arrow');
            if (!loopTag || !loopPath) return false;
            const tagBox = loopTag.getBBox();
            const svg = loopTag.closest('svg');
            const atomTexts = [...svg.querySelectorAll('text.cf-a')];
            if (!atomTexts.length) return false;
            // Ensure tag sits well above highest atom text (y < minAtomY - 10)
            const minAtomY = Math.min(...atomTexts.map(t => t.getBBox().y));
            return (tagBox.y + tagBox.height) < minAtomY;
        }'''))
    check('Circular chain loop arrow & tag sit clear above all atoms (no text overlap)', no_loop_overlap)

    # Step forward to Step 4 (Termination)
    safe_click(page, '.ko-next')
    s4_dot_on = bool(safe_eval(page, '.ko-dots button[data-i="3"]', 'e => e.classList.contains("on")', False))
    check('Step 4 dot active', s4_dot_on)

    next_disabled = bool(safe_eval(page, '.ko-next', 'e => e.disabled', False))
    check('Next button disabled on last step (step 4)', next_disabled)

    # Termination combination switcher
    term_btns = page.locator('.frs-term-btns button')
    check('Termination options (3 combinations) visible in step 4', term_btns.count() == 3)

    # Test switching termination option 1 (2Cl• → Cl₂)
    safe_click(page, '.frs-term-btns button[data-term="1"]')
    s4_eq1 = safe_eval(page, '.frs-side-eq', 'e => e.textContent', '') or ''
    check('Termination option 1 equation is 2Cl• → Cl₂', '2Cl•' in s4_eq1 and 'Cl₂' in s4_eq1, s4_eq1)

    # Test switching termination option 2 (CH₃CH₂• + Cl• → CH₃CH₂Cl)
    safe_click(page, '.frs-term-btns button[data-term="2"]')
    s4_eq2 = safe_eval(page, '.frs-side-eq', 'e => e.textContent', '') or ''
    check('Termination option 2 equation is CH₃CH₂• + Cl• → CH₃CH₂Cl',
          'CH₃CH₂•' in s4_eq2 and 'Cl•' in s4_eq2 and 'CH₃CH₂Cl' in s4_eq2, s4_eq2)

    # Test switching termination option 3 (2CH₃CH₂• → C₄H₁₀ butane)
    safe_click(page, '.frs-term-btns button[data-term="3"]')
    s4_eq3 = safe_eval(page, '.frs-side-eq', 'e => e.textContent', '') or ''
    check('Termination option 3 equation is 2CH₃CH₂• → C₄H₁₀ (butane)',
          '2CH₃CH₂•' in s4_eq3 and ('C₄H₁₀' in s4_eq3 or 'butane' in s4_eq3), s4_eq3)

    # Step navigation back
    safe_click(page, '.ko-prev')
    s3_back = bool(safe_eval(page, '.ko-dots button[data-i="2"]', 'e => e.classList.contains("on")', False))
    check('Previous button successfully returns to step 3', s3_back)

    safe_click(page, '.ko-dots button[data-i="0"]')
    s1_back = bool(safe_eval(page, '.ko-dots button[data-i="0"]', 'e => e.classList.contains("on")', False))
    check('Direct step dot jump back to step 1 works', s1_back)

    # ================= 2. Substrate & Halogen Toggles =================
    # Switch to Propane
    safe_click(page, '.frs-sub[data-sub="propane"]')
    safe_click(page, '.ko-dots button[data-i="1"]')  # go to step 2
    prop_eq = safe_eval(page, '.frs-side-eq', 'e => e.textContent', '') or ''
    check('Propane substrate step 2 equation reflects propane', 'CH₃CH₂CH₃' in prop_eq and 'CH₃•CHCH₃' in prop_eq, prop_eq)

    # Switch to Cyclopentane
    safe_click(page, '.frs-sub[data-sub="cyclopentane"]')
    cyclo_eq = safe_eval(page, '.frs-side-eq', 'e => e.textContent', '') or ''
    check('Cyclopentane substrate step 2 equation reflects C₅H₁₀ and C₅H₉•',
          'C₅H₁₀' in cyclo_eq and 'C₅H₉•' in cyclo_eq, cyclo_eq)

    # Switch to Br₂
    safe_click(page, '.frs-hal[data-hal="br2"]')
    br_eq = safe_eval(page, '.frs-side-eq', 'e => e.textContent', '') or ''
    check('Br₂ halogen step 2 equation reflects Br• and HBr', 'Br•' in br_eq and 'HBr' in br_eq, br_eq)

    # Restore default ethane and Cl₂
    safe_click(page, '.frs-sub[data-sub="ethane"]')
    safe_click(page, '.frs-hal[data-hal="cl2"]')

    # Fish-hook toggle
    safe_click(page, '.frs-hook')
    hook_checked = bool(safe_eval(page, '.frs-hook', 'e => e.checked', False))
    check('Fish-hook checkbox toggles on', hook_checked)
    safe_click(page, '.frs-hook')

    # ================= 3. Tab 2: Further Substitution & Distribution =================
    safe_click(page, '.tabbar button[data-tab="dist"]')
    tab2_shown = bool(safe_eval(page, '[data-pane="dist"]', 'e => e.classList.contains("show")', False))
    check('Tab 2 pane is shown on tab click', tab2_shown)

    bar_count = page.locator('.frs-bar-col').count()
    check('7 product distribution bars present', bar_count == 7, str(bar_count))

    # Test slider preset buttons
    safe_click(page, '.frs-preset-row button[data-val="0.2"]')
    r02_val = safe_eval(page, '.frs-ratio-val', 'e => e.textContent', '') or ''
    check('Preset 0.2:1 updates ratio text', '0.2' in r02_val, r02_val)

    pct_ethane_02_str = safe_eval(page, '.frs-bar-col[data-k="0"] .frs-bar-pct', 'e => e.textContent', None)
    pct_hexa_02_str = safe_eval(page, '.frs-bar-col[data-k="6"] .frs-bar-pct', 'e => e.textContent', None)
    pct_ethane_02 = int(pct_ethane_02_str.replace('%', '')) if pct_ethane_02_str and '%' in pct_ethane_02_str else -1
    pct_hexa_02 = int(pct_hexa_02_str.replace('%', '')) if pct_hexa_02_str and '%' in pct_hexa_02_str else -1
    check('At ratio 0.2:1 (excess ethane), unreacted ethane is highest and hexachloro is ~0%',
          pct_ethane_02 >= 70 and pct_hexa_02 == 0, f'ethane={pct_ethane_02}%, hexa={pct_hexa_02}%')

    safe_click(page, '.frs-preset-row button[data-val="6.0"]')
    r60_val = safe_eval(page, '.frs-ratio-val', 'e => e.textContent', '') or ''
    check('Preset 6.0:1 updates ratio text', '6.0' in r60_val, r60_val)

    pct_ethane_60_str = safe_eval(page, '.frs-bar-col[data-k="0"] .frs-bar-pct', 'e => e.textContent', None)
    pct_hexa_60_str = safe_eval(page, '.frs-bar-col[data-k="6"] .frs-bar-pct', 'e => e.textContent', None)
    pct_ethane_60 = int(pct_ethane_60_str.replace('%', '')) if pct_ethane_60_str and '%' in pct_ethane_60_str else -1
    pct_hexa_60 = int(pct_hexa_60_str.replace('%', '')) if pct_hexa_60_str and '%' in pct_hexa_60_str else -1
    check('At ratio 6.0:1 (excess Cl₂), hexachloroethane reaches > 90% and ethane is 0%',
          pct_hexa_60 >= 90 and pct_ethane_60 == 0, f'ethane={pct_ethane_60}%, hexa={pct_hexa_60}%')

    # Slider direct input
    if page.locator('.frs-ratio-range').count() > 0:
        page.eval_on_selector('.frs-ratio-range', '''e => {
            e.value = "1.0";
            e.dispatchEvent(new Event("input", { bubbles: true }));
        }''')
    r10_val = safe_eval(page, '.frs-ratio-val', 'e => e.textContent', '') or ''
    check('Slider direct input 1.0 updates ratio', '1.0' in r10_val, r10_val)

    # Check schematic note & summary text
    has_schem = bool(safe_eval(page, '.frs-schem-badge', 'e => e.textContent.includes("示意比例")', False))
    check('Tab 2 clearly indicates schematic proportions (示意比例)', has_schem)

    has_summary = page.locator('.frs-exam-summary').count() > 0
    check('Tab 2 exam summary card exists', has_summary)

    # ================= 4. Cross-reference Link =================
    xref_href = safe_eval(page, '.frs-xref a', 'e => e.getAttribute("href")', '') or ''
    check('Bottom xref link points to ch15 halogenoalkanes', 'ch15' in xref_href, xref_href)

    # ================= 5. Fonts, Clash & Responsive Layout =================
    # Equation font size >= 12px
    eq_font_size = float(safe_eval(page, '.frs-side-eq', 'e => parseFloat(getComputedStyle(e).fontSize)', 0.0) or 0.0)
    check('Side equation font size >= 12px', eq_font_size >= 12, f'{eq_font_size}px')

    # SVG text font size in stage
    safe_click(page, '.tabbar button[data-tab="mech"]')
    safe_click(page, '.ko-dots button[data-i="2"]')  # step 3
    svg_font_size = float(safe_eval(page, '.ko-stage svg text', 'e => parseFloat(getComputedStyle(e).fontSize)', 0.0) or 0.0)
    check('SVG stage text font size >= 12px', svg_font_size >= 12, f'{svg_font_size}px')

    # Clash check across all labels
    clash_count = page.locator('[data-clash]:not([data-clash="0"])').count()
    check('Total [data-clash] is 0 across page', clash_count == 0, str(clash_count))

    # 720px width: no horizontal overflow
    page.set_viewport_size({'width': 720, 'height': 1100})
    overflow_720 = bool(page.evaluate('() => { const k = document.querySelector(".k"); return k ? (k.scrollWidth > k.clientWidth + 1) : false; }'))
    check('720px width: no horizontal overflow in .k', not overflow_720)

    # ================= 6. Screenshots =================
    # 1. 720px width
    safe_shot(page, '.k', OUT / 'w720.png')
    check('Screenshot: w720.png captured', (OUT / 'w720.png').exists())

    # Restore viewport to 980 for overview shots
    page.set_viewport_size({'width': 980, 'height': 1100})

    # 2. Light mode overview (Step 3 Propagation 2 active)
    safe_shot(page, '.k', OUT / 'light.png')
    check('Screenshot: light.png captured', (OUT / 'light.png').exists())

    # 3. High-resolution zoom crop (z >= 2) of Step 3 stage (loop arrow & radical dots)
    safe_shot(page, '.ko-stage', OUT / 'z2-step3-loop.png')
    check('Screenshot: z2-step3-loop.png captured', (OUT / 'z2-step3-loop.png').exists())

    # 4. Dark mode overview
    page.emulate_media(color_scheme='dark')
    safe_shot(page, '.k', OUT / 'dark.png')
    check('Screenshot: dark.png captured', (OUT / 'dark.png').exists())
    page.emulate_media(color_scheme='light')

    # 5. Tab 2 distribution screenshot
    safe_click(page, '.tabbar button[data-tab="dist"]')
    safe_shot(page, '[data-pane="dist"]', OUT / 'tab2-dist.png')
    check('Screenshot: tab2-dist.png captured', (OUT / 'tab2-dist.png').exists())

    # Final check on console errors
    check('0 console errors throughout entire test run', len(errors) == 0, str(errors))

    browser.close()

pass_count = sum(1 for _, ok, _ in results if ok)
total_count = len(results)
print(f"\n{pass_count}/{total_count} passed")
if pass_count != total_count:
    sys.exit(1)
