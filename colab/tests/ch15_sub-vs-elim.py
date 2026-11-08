"""ch15 sub-vs-elim — 🔬 substitution 还是 elimination：选 nucleophile 和 solvent.

usage:
  TMPDIR=/mnt/ai-shared/che_tmp/organic/prof/sub-vs-elim uv run --with playwright python -I colab/tests/ch15_sub-vs-elim.py $COLAB_TMP/cells/ch15-sub-vs-elim.html /mnt/ai-shared/che_tmp/organic/shots/sub-vs-elim
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch15 --cell sub-vs-elim)
"""
import re
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
    if page.locator(sel).count() == 0:
        return
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


# =========================================================================
# 1. HTML File Hygiene Checks
# =========================================================================
raw_html = PAGE.read_text(encoding='utf-8')

unexp_cf = re.findall(r'\{\{chemfig\s+[^\}]*\}\}', raw_html)
check('no unexpanded {{chemfig ...}} in built HTML', len(unexp_cf) == 0, f'{len(unexp_cf)} unexpanded')

unexp_xr = re.findall(r'\{\{xref\s+[^\}]*\}\}', raw_html)
check('no unexpanded {{xref ...}} in built HTML', len(unexp_xr) == 0, f'{len(unexp_xr)} unexpanded')

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
        page.wait_for_selector('.sve-wrap')

        # Check initial state
        state = page.evaluate('window.__subVsElim.state()')
        check(f'{scheme}: cell initialised with 2-bromobutane', state['subId'] == '2-bromobutane', state['subId'])
        check(f'{scheme}: cell initialised with naoh-etoh', state['rgId'] == 'naoh-etoh', state['rgId'])

        # Check 2-bromobutane elimination initial output: 3 products
        prod_names = [t.strip() for t in page.eval_on_selector_all('.sve-prod-name', 'els => els.map(e => e.textContent)')]
        check(f'{scheme}: 2-bromobutane elimination gives 3 products', len(prod_names) == 3, f'{prod_names}')
        check(f'{scheme}: but-1-ene in products', 'but-1-ene' in prod_names, f'{prod_names}')
        check(f'{scheme}: cis-but-2-ene in products', 'cis-but-2-ene' in prod_names, f'{prod_names}')
        check(f'{scheme}: trans-but-2-ene in products', 'trans-but-2-ene' in prod_names, f'{prod_names}')

        # Check elimination annotations exist for C1 and C3
        elim_notes = [t.strip() for t in page.eval_on_selector_all('.sve-prod-elim-site', 'els => els.map(e => e.textContent)')]
        check(f'{scheme}: elimination site annotations point to C1 and C3', any('C1' in n for n in elim_notes) and any('C3' in n for n in elim_notes), f'{elim_notes}')

        # =====================================================================
        # Test 5 Substrates × 5 Reagents = 25 Combinations
        # =====================================================================
        sub_keys = ['bromoethane', '1-bromopropane', '2-bromopropane', '2-bromobutane', '2-bromo-2-methylpropane']
        rg_keys = ['naoh-aq', 'naoh-etoh', 'kcn', 'nh3', 'agno3']

        all_combos_valid = True
        combos_tested = 0

        for sId in sub_keys:
            sub_btn = page.locator(f'.sve-sub-btn[data-sub="{sId}"]')
            if sub_btn.count() > 0:
                sub_btn.click()
            else:
                all_combos_valid = False
            for rId in rg_keys:
                rg_btn = page.locator(f'.sve-rg-btn[data-rg="{rId}"]')
                if rg_btn.count() > 0:
                    rg_btn.click()
                else:
                    all_combos_valid = False
                combos_tested += 1

                p_names = [t.strip() for t in page.eval_on_selector_all('.sve-prod-name', 'els => els.map(e => e.textContent)')]
                if not p_names or any(not n for n in p_names):
                    all_combos_valid = False
                    print(f'FAIL combo {sId} + {rId}: p_names={p_names}')

                # Assert ChemFig SVGs rendered
                cf_count = page.locator('.sve-prod-stage svg.cf').count()
                if cf_count != len(p_names):
                    all_combos_valid = False
                    print(f'FAIL SVG count {sId} + {rId}: cf={cf_count} vs {len(p_names)}')

                # Specific chemical assertions (at least 8 key combinations)
                if sId == 'bromoethane' and rId == 'naoh-aq':
                    check(f'{scheme}: bromoethane + NaOH(aq) gives ethanol', 'ethanol' in p_names, f'{p_names}')
                elif sId == 'bromoethane' and rId == 'naoh-etoh':
                    check(f'{scheme}: bromoethane + NaOH/EtOH gives ethene', 'ethene' in p_names, f'{p_names}')
                elif sId == 'bromoethane' and rId == 'kcn':
                    check(f'{scheme}: bromoethane + KCN gives propanenitrile', 'propanenitrile' in p_names, f'{p_names}')
                    cplus_visible = page.locator('.sve-badge-cplus').count() > 0 and page.is_visible('.sve-badge-cplus')
                    check(f'{scheme}: KCN displays C+1 badge', cplus_visible)
                elif sId == 'bromoethane' and rId == 'nh3':
                    check(f'{scheme}: bromoethane + NH3 gives ethylamine', 'ethylamine' in p_names, f'{p_names}')
                elif sId == '1-bromopropane' and rId == 'naoh-etoh':
                    check(f'{scheme}: 1-bromopropane + NaOH/EtOH gives propene', 'propene' in p_names, f'{p_names}')
                elif sId == '2-bromopropane' and rId == 'naoh-aq':
                    check(f'{scheme}: 2-bromopropane + NaOH(aq) gives propan-2-ol', 'propan-2-ol' in p_names, f'{p_names}')
                elif sId == '2-bromo-2-methylpropane' and rId == 'naoh-aq':
                    check(f'{scheme}: 2-bromo-2-methylpropane + NaOH(aq) gives 2-methylpropan-2-ol', '2-methylpropan-2-ol' in p_names, f'{p_names}')
                elif sId == '2-bromo-2-methylpropane' and rId == 'kcn':
                    check(f'{scheme}: 2-bromo-2-methylpropane + KCN gives 2,2-dimethylpropanenitrile', '2,2-dimethylpropanenitrile' in p_names, f'{p_names}')
                elif sId == '2-bromobutane' and rId == 'agno3':
                    obs_loc = page.locator('.sve-obs-box')
                    obs_text = obs_loc.inner_text() if obs_loc.count() > 0 else ''
                    check(f'{scheme}: AgNO3 mentions cream precipitate', 'cream precipitate' in obs_text, obs_text)

        check(f'{scheme}: all 25 combinations have valid product cards & SVGs', all_combos_valid and combos_tested == 25, f'tested {combos_tested}')

        # =====================================================================
        # Test Contrast Mode (aq vs ethanol side-by-side)
        # =====================================================================
        print(f'== Testing contrast mode in {scheme}')
        btn_contrast = page.locator('.sve-btn-contrast')
        if btn_contrast.count() > 0:
            btn_contrast.click()
            page.wait_for_timeout(100)

        check(f'{scheme}: contrast view is visible', page.is_visible('.sve-contrast-view'))
        check(f'{scheme}: single view is hidden in contrast mode', not page.is_visible('.sve-single-view'))

        # Check left column (NaOH aq) and right column (NaOH ethanol)
        sub_title_loc = page.locator('.sve-ccol-sub h4')
        sub_title = sub_title_loc.inner_text() if sub_title_loc.count() > 0 else ''
        elim_title_loc = page.locator('.sve-ccol-elim h4')
        elim_title = elim_title_loc.inner_text() if elim_title_loc.count() > 0 else ''
        check(f'{scheme}: left col title has NaOH(aq)', 'NaOH(aq)' in sub_title, sub_title)
        check(f'{scheme}: right col title has NaOH in ethanol', 'NaOH in ethanol' in elim_title, elim_title)

        # In 2-bromo-2-methylpropane contrast mode
        sub3_btn = page.locator('.sve-sub-btn[data-sub="2-bromo-2-methylpropane"]')
        if sub3_btn.count() > 0:
            sub3_btn.click()
        sub_prod_loc = page.locator('.sve-csub-prod .sve-prod-name')
        sub_prod = sub_prod_loc.inner_text() if sub_prod_loc.count() > 0 else ''
        elim_prod_loc = page.locator('.sve-celim-prods .sve-prod-name')
        elim_prod = elim_prod_loc.inner_text() if elim_prod_loc.count() > 0 else ''
        check(f'{scheme}: contrast left col is 2-methylpropan-2-ol', sub_prod == '2-methylpropan-2-ol', sub_prod)
        check(f'{scheme}: contrast right col is 2-methylpropene', elim_prod == '2-methylpropene', elim_prod)

        # Toggle contrast mode off
        if btn_contrast.count() > 0:
            btn_contrast.click()
            page.wait_for_timeout(100)
        check(f'{scheme}: single view restored after toggling off contrast', page.is_visible('.sve-single-view'))

        # =====================================================================
        # Test Practice Quiz
        # =====================================================================
        print(f'== Testing practice quiz in {scheme}')
        # Q1: 2-bromopropane + NaOH in ethanol -> propene
        q1_inp = page.locator('.sve-q-input[data-qid="q1"]')
        q1_btn = page.locator('.sve-btn-check[data-qid="q1"]')
        if q1_inp.count() > 0 and q1_btn.count() > 0:
            q1_inp.fill('propene')
            q1_btn.click()
        fb_cls1 = page.get_attribute('.sve-q-fb[data-qid="q1"]', 'class') if page.locator('.sve-q-fb[data-qid="q1"]').count() > 0 else ''
        check(f'{scheme}: Q1 propene accepted as ok', 'ok' in (fb_cls1 or ''), fb_cls1)

        # Q1 order check: non-C first
        if q1_inp.count() > 0 and q1_btn.count() > 0:
            q1_inp.fill('H3CCH=CH2')
            q1_btn.click()
        fb_text1 = page.locator('.sve-q-fb[data-qid="q1"]').inner_text() if page.locator('.sve-q-fb[data-qid="q1"]').count() > 0 else ''
        check(f'{scheme}: Q1 wrong element order detected with "顺序"', '顺序' in fb_text1, fb_text1)

        # Q1 reveal answer
        q1_rev = page.locator('.sve-btn-rev[data-qid="q1"]')
        if q1_rev.count() > 0:
            q1_rev.click()
        rev_text1 = page.locator('.sve-q-fb[data-qid="q1"]').inner_text() if page.locator('.sve-q-fb[data-qid="q1"]').count() > 0 else ''
        check(f'{scheme}: Q1 reveal shows reference answer', '参考答案' in rev_text1 and 'propene' in rev_text1, rev_text1)

        # Q2: 2-bromobutane number of alkenes -> 3
        q2_inp = page.locator('.sve-q-input[data-qid="q2"]')
        q2_btn = page.locator('.sve-btn-check[data-qid="q2"]')
        if q2_inp.count() > 0 and q2_btn.count() > 0:
            q2_inp.fill('3')
            q2_btn.click()
        fb_cls2 = page.get_attribute('.sve-q-fb[data-qid="q2"]', 'class') if page.locator('.sve-q-fb[data-qid="q2"]').count() > 0 else ''
        check(f'{scheme}: Q2 "3" accepted as ok', 'ok' in (fb_cls2 or ''), fb_cls2)

        # Q3: bromoethane + KCN -> propanenitrile
        q3_inp = page.locator('.sve-q-input[data-qid="q3"]')
        q3_btn = page.locator('.sve-btn-check[data-qid="q3"]')
        if q3_inp.count() > 0 and q3_btn.count() > 0:
            q3_inp.fill('propanenitrile')
            q3_btn.click()
        fb_cls3 = page.get_attribute('.sve-q-fb[data-qid="q3"]', 'class') if page.locator('.sve-q-fb[data-qid="q3"]').count() > 0 else ''
        check(f'{scheme}: Q3 propanenitrile accepted as ok', 'ok' in (fb_cls3 or ''), fb_cls3)

        # Periodic Table test
        pt_btn = page.locator('.k-ptable .pt-btn')
        pt_btn_present = pt_btn.count() > 0 and pt_btn.is_visible()
        check(f'{scheme}: Periodic Table button present', pt_btn_present)
        if pt_btn_present:
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
        # Set to 2-bromobutane + naoh-etoh (rich elimination state with 3 alkenes)
        sub_btn_2b = page.locator('.sve-sub-btn[data-sub="2-bromobutane"]')
        if sub_btn_2b.count() > 0:
            sub_btn_2b.click()
        rg_btn_el = page.locator('.sve-rg-btn[data-rg="naoh-etoh"]')
        if rg_btn_el.count() > 0:
            rg_btn_el.click()
        page.wait_for_timeout(100)

        if scheme == 'light':
            shot(page, '.sve-wrap', OUT / 'light-2bromobutane-elim.png')
            check('Screenshot: light-2bromobutane-elim.png captured', (OUT / 'light-2bromobutane-elim.png').exists())

            # Detail zoom on first product card
            shot(page, '.sve-prod-card:first-child', OUT / 'zoom-elim-detail.png')
            check('Screenshot: zoom-elim-detail.png captured', (OUT / 'zoom-elim-detail.png').exists())

            # Contrast mode screenshot
            if btn_contrast.count() > 0:
                btn_contrast.click()
                page.wait_for_timeout(100)
                shot(page, '.sve-wrap', OUT / 'light-contrast.png')
                check('Screenshot: light-contrast.png captured', (OUT / 'light-contrast.png').exists())
                btn_contrast.click()  # toggle off
                page.wait_for_timeout(100)
        else:
            shot(page, '.sve-wrap', OUT / 'dark-2bromobutane-elim.png')
            check('Screenshot: dark-2bromobutane-elim.png captured', (OUT / 'dark-2bromobutane-elim.png').exists())

            if btn_contrast.count() > 0:
                btn_contrast.click()
                page.wait_for_timeout(100)
                shot(page, '.sve-wrap', OUT / 'dark-contrast.png')
                check('Screenshot: dark-contrast.png captured', (OUT / 'dark-contrast.png').exists())
                btn_contrast.click()
                page.wait_for_timeout(100)

        # =====================================================================
        # Narrow Viewport Test (720 px)
        # =====================================================================
        print(f'== Testing narrow 720 px in {scheme}')
        page.set_viewport_size({'width': 720, 'height': 1200})
        page.wait_for_timeout(200)

        # Horizontal overflow check
        ov = page.evaluate('() => { const k = document.querySelector(".k"); return k ? (k.scrollWidth - k.clientWidth) : 0; }')
        check(f'{scheme} 720 px: no horizontal overflow on .k', ov <= 1, f'overflow={ov}px')

        # SVG text font size check: computed font size >= 12.0px and scaled >= 12.0px (visible SVGs only)
        min_fs = page.evaluate('''() => {
            const svgs = [...document.querySelectorAll('.sve-prod-stage svg.cf')].filter(s => {
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
            shot(page, '.sve-wrap', OUT / 'narrow-720.png')
            check('Screenshot: narrow-720.png captured', (OUT / 'narrow-720.png').exists())

        ctx.close()

    b.close()

# Console errors assertion
check('no console errors / page errors throughout test', len(errors) == 0, '; '.join(errors))

n = sum(1 for r in results if r[1])
print(f'\n{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
