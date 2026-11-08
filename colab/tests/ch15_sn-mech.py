"""ch15 sn-mech — S_N1 / S_N2 mechanism player, exam mode & kinetics.

usage: TMPDIR=/mnt/ai-shared/che_tmp/organic/prof/sn-mech uv run --with playwright python -I colab/tests/ch15_sn-mech.py /mnt/ai-shared/che_tmp/organic/cells/ch15-sn-mech.html /mnt/ai-shared/che_tmp/organic/shots/sn-mech
"""
import sys
from pathlib import Path

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
CHROMIUM = '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    status = '  ok   ' if cond else '  FAIL '
    print(status + name + (f' — {detail}' if detail and not cond else ''))


def shot(page, sel, path):
    """Clip element screenshot avoiding rAF hanging in multi-process headless environments."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROMIUM, args=['--disable-gpu'])
    page = browser.new_page(viewport={'width': 960, 'height': 1100})

    page.on('console', lambda msg: errors.append(f'[{msg.type}] {msg.text}') if msg.type == 'error' else None)
    page.on('pageerror', lambda err: errors.append(str(err)))

    page.goto(PAGE.as_uri())
    page.wait_for_selector('.k')

    print('== 1. Basic initialization & DOM check')
    check('Initial page load: 0 console errors', len(errors) == 0, str(errors))
    check('Main container .sn-wrap exists', page.locator('.sn-wrap').count() > 0)
    check('Control card .sn-ctrl-card exists', page.locator('.sn-ctrl-card').count() > 0)
    check('Player host .sn-player-host exists', page.locator('.sn-player-host').count() > 0)
    check('KO.mech player .ko-mech exists', page.locator('.ko-mech').count() > 0)
    check('Player stage .ko-stage exists', page.locator('.ko-stage').count() > 0)
    check('Side card .ko-side exists', page.locator('.ko-side').count() > 0)
    check('Rate card .sn-rate-card exists', page.locator('.sn-rate-card').count() > 0)
    check('Analysis card .sn-analysis-card exists', page.locator('.sn-analysis-card').count() > 0)

    # Chemical atom conservation assertion
    atom_ok = page.evaluate('() => { try { window.__snMech.verifyAtomConservation(); return true; } catch(e) { return false; } }')
    check('Equation atom conservation assertion passes in JS', atom_ok)

    print('== 2. Mechanism auto-determination logic')
    # bromoethane (1°) -> S_N2
    page.evaluate('window.__snMech.setSub("et_br")')
    st = page.evaluate('window.__snMech.getState()')
    badge_text = page.inner_text('#sn-mech-badge')
    sn1_disabled = page.eval_on_selector('.sn-mbtn[data-m="sn1"]', 'e => e.disabled')
    check('bromoethane (1°) selects S_N2', st['mech'] == 'sn2' and 'S_N2' in badge_text, badge_text)
    check('bromoethane (1°) disables S_N1 button', sn1_disabled)

    # 1-bromobutane (1°) -> S_N2
    page.evaluate('window.__snMech.setSub("bu1_br")')
    st = page.evaluate('window.__snMech.getState()')
    badge_text = page.inner_text('#sn-mech-badge')
    check('1-bromobutane (1°) selects S_N2', st['mech'] == 'sn2' and 'S_N2' in badge_text, badge_text)

    # 2-bromo-2-methylpropane (3°) -> S_N1
    page.evaluate('window.__snMech.setSub("tbu_br")')
    st = page.evaluate('window.__snMech.getState()')
    badge_text = page.inner_text('#sn-mech-badge')
    sn2_disabled = page.eval_on_selector('.sn-mbtn[data-m="sn2"]', 'e => e.disabled')
    check('2-bromo-2-methylpropane (3°) selects S_N1', st['mech'] == 'sn1' and 'S_N1' in badge_text, badge_text)
    check('2-bromo-2-methylpropane (3°) disables S_N2 button', sn2_disabled)

    # 2-bromobutane (2°) -> mixture of S_N1 and S_N2
    page.evaluate('window.__snMech.setSub("bu2_br")')
    badge_text = page.inner_text('#sn-mech-badge')
    sn1_disabled = page.eval_on_selector('.sn-mbtn[data-m="sn1"]', 'e => e.disabled')
    sn2_disabled = page.eval_on_selector('.sn-mbtn[data-m="sn2"]', 'e => e.disabled')
    check('2-bromobutane (2°) displays "mixture, depending on structure"', 'mixture, depending on structure' in badge_text, badge_text)
    check('2-bromobutane (2°) enables both S_N2 and S_N1 buttons', not sn1_disabled and not sn2_disabled)

    # Switch 2-bromobutane to S_N1 and back to S_N2
    page.evaluate('window.__snMech.setMech("sn1")')
    check('2-bromobutane toggles to S_N1', page.evaluate('window.__snMech.getState()["mech"]') == 'sn1')
    page.evaluate('window.__snMech.setMech("sn2")')
    check('2-bromobutane toggles back to S_N2', page.evaluate('window.__snMech.getState()["mech"]') == 'sn2')

    print('== 3. 4 Substrates x 3 Nucleophiles combination playback')
    subs = ['et_br', 'bu1_br', 'bu2_br', 'tbu_br']
    nus = ['oh', 'cn', 'nh3']
    all_combos_ok = True

    for s in subs:
        for n in nus:
            page.evaluate(f'window.__snMech.setSub("{s}"); window.__snMech.setNu("{n}");')
            cnt = page.evaluate('window.__snMech.getStepsCount()')
            if cnt < 2:
                all_combos_ok = False
                break
            # Step forward and back
            page.evaluate('window.__snMech.go(1)')
            cur = page.evaluate('window.__snMech.getCurStep()')
            if cur != 1:
                all_combos_ok = False
                break
            svg_ok = page.locator('.ko-stage svg').count() > 0
            if not svg_ok:
                all_combos_ok = False
                break

    check('All 4 substrates x 3 nucleophiles (12 combinations) render and step smoothly', all_combos_ok)

    print('== 4. CN⁻ arrow origin on Carbon lone pair')
    page.evaluate('window.__snMech.setSub("et_br"); window.__snMech.setNu("cn"); window.__snMech.go(0);')
    cn_arrow_from = page.eval_on_selector('.ko-stage [data-n="0"] path', 'e => e.getAttribute("data-from")')
    check('CN⁻ curly arrow starts at lp:cn (C lone pair)', cn_arrow_from == 'lp:cn', str(cn_arrow_from))

    # Inspect data-atoms to ensure 'cn' is indeed C
    atom_cn_label = page.evaluate('''() => {
        const svg = document.querySelector('.ko-stage svg');
        const atoms = JSON.parse(svg.getAttribute('data-atoms') || '[]');
        const cn = atoms.find(a => a.n === 'cn');
        return cn ? cn.l : null;
    }''')
    check('Atom cn is Carbon (l="C")', atom_cn_label == 'C', str(atom_cn_label))

    # Mark scheme item explicitly mentions C of CN⁻
    marks_text = page.inner_text('.ko-marks')
    check('Mark scheme explicitly specifies "lone pair on C of CN⁻"', 'C of CN⁻' in marks_text, marks_text)

    print('== 5. S_N2 Transition state structure & rate equation')
    page.evaluate('window.__snMech.setSub("et_br"); window.__snMech.setNu("oh"); window.__snMech.setTs(true); window.__snMech.go(1);')
    # Step 1 should be Transition state
    ts_partial_count = page.locator('.ko-stage .ko-partial').count()
    check('Transition state has partial bonds (dashed lines)', ts_partial_count >= 2, str(ts_partial_count))
    ts_bracket_count = page.locator('.ko-stage .ko-br').count()
    check('Transition state has [ ... ] brackets', ts_bracket_count > 0, str(ts_bracket_count))
    ts_charge_text = page.locator('.ko-stage .ko-bq').text_content() if page.locator('.ko-stage .ko-bq').count() > 0 else ''
    check('Transition state carries negative charge −', '−' in ts_charge_text or '-' in ts_charge_text, ts_charge_text)

    # S_N2 rate equation
    rate_eq = page.inner_text('#sn-rate-eq')
    check('S_N2 rate equation: rate = k [RX] [Nu⁻]', '[RX]' in rate_eq and '[Nu⁻]' in rate_eq, rate_eq)

    print('== 6. S_N1 Carbocation intermediate, +I inductive effect & rate equation')
    page.evaluate('window.__snMech.setSub("tbu_br"); window.__snMech.setNu("oh"); window.__snMech.go(1);')
    # Step 1 is Planar tertiary carbocation
    cat_charge_text = page.inner_text('.ko-stage')
    check('Carbocation has positive charge +', '+' in cat_charge_text)
    inductive_arrows = page.locator('.ko-stage polygon.sn-inductive-poly').count()
    check('Planar 3° carbocation has 3 inductive effect arrows pointing to C⁺', inductive_arrows == 3, str(inductive_arrows))

    # S_N1 rate equation
    rate_eq_sn1 = page.inner_text('#sn-rate-eq')
    check('S_N1 rate equation: rate = k [RX] (unimolecular)', '[RX]' in rate_eq_sn1 and '[Nu⁻]' not in rate_eq_sn1, rate_eq_sn1)

    print('== 7. S_N1 with NH₃ extra deprotonation step (M3)')
    page.evaluate('window.__snMech.setSub("tbu_br"); window.__snMech.setNu("nh3");')
    nh3_steps = page.evaluate('window.__snMech.getStepsCount()')
    check('S_N1 with NH₃ has 4 steps (including M3 deprotonation)', nh3_steps == 4, str(nh3_steps))
    page.evaluate('window.__snMech.go(2)')  # step 3 (0-indexed 2)
    nh3_marks = page.inner_text('.ko-marks')
    check('Step 3 checklist has M3 N–H bond breaking arrow to lose H⁺', 'M3' in nh3_marks and 'N–H' in nh3_marks, nh3_marks)

    print('== 8. Exam mode feedback (考卷模式)')
    page.evaluate('window.__snMech.setSub("et_br"); window.__snMech.setNu("oh"); window.__snMech.setExam(true); window.__snMech.go(0);')
    hidden_arrows = page.locator('.ko-stage .ko-hide').count()
    check('Exam mode: arrows initially hidden', hidden_arrows >= 2, str(hidden_arrows))

    # Simulate click on lone pair of OH⁻ (target: lp:o), then click C1 (target: c1)
    # Using KO.hit or simulating click via page.mouse
    click_success = page.evaluate('''() => {
        const svg = document.querySelector('.ko-stage svg');
        const ctm = svg.getScreenCTM();
        const D = svg.__ko;
        if (!D || !D.lps || !D.lps[D.byName['o']]) return false;
        const lp = D.lps[D.byName['o']][0];
        const pt = svg.createSVGPoint();
        pt.x = lp.x; pt.y = lp.y;
        const scr = pt.matrixTransform(ctm);
        // trigger click at scr.x, scr.y
        const ev1 = new MouseEvent('click', { clientX: scr.x, clientY: scr.y, bubbles: true });
        svg.dispatchEvent(ev1);

        const c1 = D.atoms[D.byName['c1']];
        pt.x = c1.x; pt.y = c1.y;
        const scr2 = pt.matrixTransform(ctm);
        const ev2 = new MouseEvent('click', { clientX: scr2.x, clientY: scr2.y, bubbles: true });
        svg.dispatchEvent(ev2);

        return true;
    }''')
    check('Exam mode correct click dispatched', click_success)
    fb_text = page.inner_text('.ko-fb')
    check('Exam mode feedback shows success ✓', '✓' in fb_text or '对' in fb_text, fb_text)
    got_count = page.locator('.ko-stage .ko-got').count()
    check('Arrow revealed in got state (.ko-got)', got_count >= 1, str(got_count))

    # Test "显示答案"
    page.click('.ko-show')
    fb_after_show = page.inner_text('.ko-fb')
    check('Clicking "显示答案" reveals all arrows', '已显示本步全部箭头' in fb_after_show, fb_after_show)

    # Test "重来"
    page.click('.ko-reset')
    hidden_arrows_reset = page.locator('.ko-stage .ko-hide').count()
    check('Clicking "重来" resets arrows to hidden state', hidden_arrows_reset >= 2, str(hidden_arrows_reset))

    print('== 9. Data clash & SVG text size check')
    clash_count = page.locator('[data-clash]').count()
    check('0 data-clash attributes on labels', clash_count == 0, str(clash_count))

    min_font_size = page.evaluate('''() => {
        const texts = [...document.querySelectorAll('.ko-stage svg text')];
        let minFs = 999;
        texts.forEach(t => {
            const fs = parseFloat(window.getComputedStyle(t).fontSize);
            if (fs > 0 && fs < minFs) minFs = fs;
        });
        return minFs;
    }''')
    check('SVG text font size >= 12 px', min_font_size >= 12.0, f'min font size: {min_font_size}')

    print('== 10. Screenshots')
    # Normal view (960px)
    page.set_viewport_size({'width': 960, 'height': 1100})
    # Light: S_N2 with TS
    page.evaluate('window.__snMech.setSub("et_br"); window.__snMech.setNu("oh"); window.__snMech.setExam(false); window.__snMech.setTs(true); window.__snMech.go(1);')
    shot(page, '.k', OUT / 'sn2-light.png')

    # Zoomed detail: TS stage
    shot(page, '.ko-stage', OUT / 'ts-detail-z2.png')

    # Dark mode
    page.emulate_media(color_scheme='dark')
    page.wait_for_timeout(100)
    shot(page, '.k', OUT / 'sn2-dark.png')

    # S_N1 in light mode
    page.emulate_media(color_scheme='light')
    page.evaluate('window.__snMech.setSub("tbu_br"); window.__snMech.setNu("oh"); window.__snMech.go(1);')
    shot(page, '.k', OUT / 'sn1-light.png')

    # S_N1 in dark mode
    page.emulate_media(color_scheme='dark')
    page.wait_for_timeout(100)
    shot(page, '.k', OUT / 'sn1-dark.png')

    # Exam mode
    page.emulate_media(color_scheme='light')
    page.evaluate('window.__snMech.setSub("et_br"); window.__snMech.setNu("cn"); window.__snMech.setExam(true); window.__snMech.go(0);')
    shot(page, '.k', OUT / 'exam-mode-light.png')

    print('== 11. Narrow 720 px view')
    page.set_viewport_size({'width': 720, 'height': 1100})
    page.evaluate('window.__snMech.setSub("et_br"); window.__snMech.setNu("oh"); window.__snMech.setExam(false); window.__snMech.go(0);')
    page.wait_for_timeout(150)
    overflow = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
    check('720 px narrow view: no horizontal overflow (scrollWidth <= clientWidth)', overflow <= 0, f'overflow: {overflow}px')
    shot(page, '.k', OUT / 'sn-720px.png')

    browser.close()

print('== Final status')
check('Zero console error or unhandled exceptions across all tests', len(errors) == 0, '; '.join(errors))
passed = sum(1 for r in results if r[1])
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
