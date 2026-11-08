"""ch14 alkene-wheel — 🔬 alkene 反应轮：ethene / propene × reagent.

usage:
  TMPDIR=/mnt/ai-shared/che_tmp/organic/prof/alkene-wheel uv run --with playwright python -I colab/tests/ch14_alkene-wheel.py $COLAB_TMP/cells/ch14-alkene-wheel.html /mnt/ai-shared/che_tmp/organic/shots/alkene-wheel
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch14 --cell alkene-wheel)
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
    """Element screenshot via page clip to avoid rAF hanging."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


# =========================================================================
# 1. HTML File Hygiene Checks
# =========================================================================
raw_html = PAGE.read_text(encoding='utf-8')

# Ensure no literal unrendered {{chemfig ...}} remains
import re
unexp_cf = re.findall(r'\{\{chemfig\s+[^\}]*\}\}', raw_html)
check('no unexpanded {{chemfig ...}} in built HTML', len(unexp_cf) == 0, f'{len(unexp_cf)} unexpanded')

# Ensure no unexpanded cross-references
unexp_xr = re.findall(r'\{\{xref\s+[^\}]*\}\}', raw_html)
check('no unexpanded {{xref ...}} in built HTML', len(unexp_xr) == 0, f'{len(unexp_xr)} unexpanded')

# Ensure no missing xref targets
missing_xr = re.findall(r'#xref-missing-[^\s"\'>]+', raw_html)
check('no missing Drive xref targets (#xref-missing-*)', len(missing_xr) == 0, str(missing_xr))


# =========================================================================
# 2. Browser Tests
# =========================================================================
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, args=['--disable-gpu'])

    for scheme in ('light', 'dark'):
        print(f'== Testing scheme: {scheme}')
        ctx = b.new_context(color_scheme=scheme, viewport={'width': 1000, 'height': 1200})
        page = ctx.new_page()

        page.on('pageerror', lambda err: errors.append(f'[{scheme} pageerror] {err}'))
        page.on('console', lambda msg: errors.append(f'[{scheme} console.{msg.type}] {msg.text}') if msg.type == 'error' else None)

        page.goto(PAGE.as_uri())
        page.wait_for_selector('.aw-wrap')

        # Check title & initial load
        check(f'{scheme}: cell initialised with propene', page.evaluate('window.__alkeneWheel.state().subId') == 'propene')
        check(f'{scheme}: cell initialised with hx-add (HBr)', page.evaluate('window.__alkeneWheel.state().rgId') == 'hx-add')

        # Assert propene + HBr details
        title = page.inner_text('.aw-rx-title')
        check(f'{scheme}: propene + HBr title correct', 'propene' in title and 'HBr' in title, title)
        maj_prod = page.inner_text('.aw-prod-card.maj .aw-prod-name')
        check(f'{scheme}: propene + HBr major product is 2-bromopropane', maj_prod == '2-bromopropane', maj_prod)
        min_prod = page.inner_text('.aw-prod-card:not(.maj) .aw-prod-name')
        check(f'{scheme}: propene + HBr minor product is 1-bromopropane', min_prod == '1-bromopropane', min_prod)

        # Pre-rendered SVGs exist in major and minor cards
        cf_count = page.locator('.aw-prod-stage svg.cf').count()
        check(f'{scheme}: ChemFig SVGs rendered in product cards', cf_count >= 2, f'count={cf_count}')

        # =====================================================================
        # Test 5 alkenes × 7 reagents = 35 combinations
        # =====================================================================
        sub_keys = ['ethene', 'propene', 'but2ene', 'mb2ene', 'cyclohexene']
        rg_keys = ['hydrogenation', 'steam', 'hx-add', 'x2-add', 'kmno4-cold', 'kmno4-hot', 'polymerisation']

        all_rx_ok = True
        combos_tested = 0

        for s_idx, sId in enumerate(sub_keys):
            page.click(f'.aw-sub-btn[data-sub="{sId}"]')
            for r_idx, rId in enumerate(rg_keys):
                page.click(f'.aw-btn-rg[data-rg="{rId}"]')
                combos_tested += 1

                p_names = [t.strip() for t in page.eval_on_selector_all('.aw-prod-name', 'els => els.map(e => e.textContent)')]
                if not p_names or any(not n for n in p_names):
                    all_rx_ok = False
                    print(f'FAIL combo {sId} + {rId}: p_names={p_names}')

                # Specific chemical assertions
                if sId == 'propene' and rId == 'steam':
                    maj = page.inner_text('.aw-prod-card.maj .aw-prod-name')
                    check('propene + steam major is propan-2-ol', maj == 'propan-2-ol', maj)
                elif sId == 'mb2ene' and rId == 'hx-add':
                    maj = page.inner_text('.aw-prod-card.maj .aw-prod-name')
                    check('2-methylpropene + HBr major is 2-bromo-2-methylpropane', maj == '2-bromo-2-methylpropane', maj)
                elif sId == 'mb2ene' and rId == 'steam':
                    maj = page.inner_text('.aw-prod-card.maj .aw-prod-name')
                    check('2-methylpropene + steam major is 2-methylpropan-2-ol', maj == '2-methylpropan-2-ol', maj)
                elif sId == 'but2ene' and rId == 'hx-add':
                    prod = page.inner_text('.aw-prod-name')
                    check('but-2-ene + HBr gives 2-bromobutane (single)', prod == '2-bromobutane', prod)
                elif sId == 'cyclohexene' and rId == 'kmno4-hot':
                    prod = page.inner_text('.aw-prod-name')
                    check('cyclohexene + hot KMnO4 gives hexanedioic acid', prod == 'hexanedioic acid', prod)
                elif sId == 'ethene' and rId == 'kmno4-cold':
                    prod = page.inner_text('.aw-prod-name')
                    check('ethene + cold KMnO4 gives ethane-1,2-diol', prod == 'ethane-1,2-diol', prod)
                elif sId == 'propene' and rId == 'kmno4-hot':
                    eq = page.inner_text('.aw-eq-text')
                    check('propene + hot KMnO4 equation has ethanoic acid', 'CH₃COOH' in eq and 'CO₂' in eq, eq)
                elif rId == 'x2-add':
                    obs = page.inner_text('.aw-obs-text')
                    check('Br2(aq) observation mentions orange and colourless', 'orange' in obs and 'colourless' in obs, obs)
                elif rId == 'kmno4-cold':
                    obs = page.inner_text('.aw-obs-text')
                    check('cold KMnO4 observation mentions purple and colourless', 'purple' in obs and 'colourless' in obs, obs)

        check(f'{scheme}: all 35 alkene x reagent combinations have valid products', all_rx_ok and combos_tested == 35, f'tested {combos_tested}')

        # =====================================================================
        # Test "对比 alkane" (ethane comparison mode)
        # =====================================================================
        print(f'== Testing alkane mode in {scheme}')
        page.check('.aw-chk-alkane')
        page.wait_for_timeout(100)

        hub_name = page.text_content('.aw-hub-name').strip()
        check(f'{scheme}: alkane toggle sets hub to ethane', hub_name == 'ethane', hub_name)

        # Alkene buttons are disabled
        btns_disabled = page.eval_on_selector_all('.aw-sub-btn', 'els => els.every(e => e.disabled)')
        check(f'{scheme}: alkene substrate buttons disabled in alkane mode', btns_disabled)

        # Polar reagent (HBr) displays "no reaction"
        page.click('.aw-btn-rg[data-rg="hx-add"]')
        p_no_rx = page.inner_text('.aw-prod-name')
        check(f'{scheme}: ethane + HBr displays no reaction', p_no_rx == 'no reaction', p_no_rx)
        notes = page.inner_text('.aw-mech-notes')
        check(f'{scheme}: notes explain lack of pi bond', 'π bond' in notes or 'pi bond' in notes or 'non-polar' in notes, notes[:60])

        # Cl2 / UV button is visible and clickable
        check(f'{scheme}: Cl2 / UV button is visible in alkane mode', page.is_visible('.aw-btn-frs'))
        page.click('.aw-btn-frs')
        frs_prod = page.inner_text('.aw-prod-name')
        check(f'{scheme}: ethane + Cl2/UV gives chloroethane', frs_prod == 'chloroethane', frs_prod)
        frs_tag = page.inner_text('.aw-rx-tag')
        check(f'{scheme}: reaction tag is free-radical substitution', 'free-radical substitution' in frs_tag.lower(), frs_tag)

        # Switch back to alkene mode
        page.uncheck('.aw-chk-alkane')
        page.wait_for_timeout(100)
        reverted_hub = page.text_content('.aw-hub-name').strip()
        check(f'{scheme}: unchecking alkane reverts hub to alkene', reverted_hub in sub_keys, reverted_hub)

        # =====================================================================
        # Test Practice Quiz
        # =====================================================================
        print(f'== Testing practice quiz in {scheme}')
        # Question 1: propene + HBr major product
        # Test correct answer
        page.fill('.aw-prac-input', '2-bromopropane')
        page.click('.aw-prac-btn-check')
        fb_cls = page.get_attribute('.aw-prac-fb', 'class')
        check(f'{scheme}: quiz correct answer returns ok', 'ok' in fb_cls, fb_cls)

        # Test order validation: formula starting with non-C (e.g. BrCH2... or H3C...)
        page.fill('.aw-prac-input', 'BrCH2CH2CH3')
        page.click('.aw-prac-btn-check')
        fb_text = page.inner_text('.aw-prac-fb')
        check(f'{scheme}: quiz detects wrong element order (C first, H second)', '顺序' in fb_text, fb_text)

        # Test reveal answer
        page.click('.aw-prac-btn-rev')
        fb_rev = page.inner_text('.aw-prac-fb')
        check(f'{scheme}: reveal answer shows reference answer', '参考答案' in fb_rev and '2-bromopropane' in fb_rev, fb_rev)

        # Test next question
        page.click('.aw-prac-btn-next')
        q2_text = page.inner_text('.aw-q-text')
        check(f'{scheme}: next question loaded', 'steam' in q2_text, q2_text)

        # =====================================================================
        # Test Periodic Table expander
        # =====================================================================
        pt_btn = page.locator('.k-ptable .pt-btn')
        check(f'{scheme}: Periodic Table button present', pt_btn.is_visible())
        pt_btn.click()
        page.wait_for_timeout(100)
        check(f'{scheme}: Periodic Table expanded on click', page.is_visible('.pt-grid'))

        # =====================================================================
        # Check Clash: [data-clash] must be 0
        # =====================================================================
        clash_count = page.locator('[data-clash]:not([data-clash="0"])').count()
        check(f'{scheme}: Total [data-clash] is 0 across page', clash_count == 0, f'clash={clash_count}')

        # =====================================================================
        # Capture Screenshots in Meaningful State
        # =====================================================================
        # Set to propene + HBr (rich state with major/minor cards)
        page.click('.aw-sub-btn[data-sub="propene"]')
        page.click('.aw-btn-rg[data-rg="hx-add"]')
        page.wait_for_timeout(100)

        if scheme == 'light':
            shot(page, '.aw-wrap', OUT / 'light-propene-hbr.png')
            check('Screenshot: light-propene-hbr.png captured', (OUT / 'light-propene-hbr.png').exists())

            # Detail zoom on product card
            shot(page, '.aw-detail-card', OUT / 'zoom-detail.png')
            check('Screenshot: zoom-detail.png captured', (OUT / 'zoom-detail.png').exists())

            # Alkane mode screenshot
            page.check('.aw-chk-alkane')
            page.click('.aw-btn-frs')
            page.wait_for_timeout(100)
            shot(page, '.aw-wrap', OUT / 'alkane-compare.png')
            check('Screenshot: alkane-compare.png captured', (OUT / 'alkane-compare.png').exists())
            page.uncheck('.aw-chk-alkane')
        else:
            shot(page, '.aw-wrap', OUT / 'dark-propene-hbr.png')
            check('Screenshot: dark-propene-hbr.png captured', (OUT / 'dark-propene-hbr.png').exists())

        # =====================================================================
        # Narrow Viewport Test (720 px)
        # =====================================================================
        print(f'== Testing narrow 720 px in {scheme}')
        page.set_viewport_size({'width': 720, 'height': 1200})
        page.wait_for_timeout(200)

        # Horizontal overflow check
        ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check(f'{scheme} 720 px: no horizontal overflow on .k', ov <= 1, f'overflow={ov}px')

        # SVG text font size check: computed font size >= 12.0px and scaled >= 12.0px
        min_fs = page.evaluate('''() => {
            const s = document.querySelector('.aw-wheel-svg');
            const k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            const texts = [...s.querySelectorAll('text')];
            return Math.min(...texts.map(t => parseFloat(getComputedStyle(t).fontSize) * k));
        }''')
        check(f'{scheme} 720 px: SVG text scaled font-size >= 12px', min_fs >= 12.0, f'minFs={min_fs:.2f}px')

        if scheme == 'light':
            shot(page, '.aw-wrap', OUT / 'narrow-720.png')
            check('Screenshot: narrow-720.png captured', (OUT / 'narrow-720.png').exists())

        ctx.close()

    b.close()

# Console errors assertion
check('no console errors / page errors throughout test', len(errors) == 0, '; '.join(errors))

n = sum(1 for r in results if r[1])
print(f'\n{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
