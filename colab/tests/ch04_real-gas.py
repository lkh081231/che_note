"""ch04 real-gas cell test.

usage: uv run --with playwright python -I colab/tests/ch04_real-gas.py $COLAB_TMP/cells/ch04-real-gas.html <shots-dir>
(build first: python3 tools/build_colab.py ch04 --cell real-gas)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []


def shot(page, sel, path):
    """element screenshot via a page clip: Locator.screenshot waits for 'stable' (two rAFs), which
    hangs when several headless Chromes share the machine"""
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True, timeout=30000)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2, color_scheme=scheme)
        ctx.set_default_timeout(15000)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri(), timeout=30000); page.wait_for_timeout(400)

        def clashes(svg_sel):
            return page.locator(f'{svg_sel} [data-clash]').count()

        def outside(svg_sel):
            return page.evaluate(f'''() => {{
                const s = document.querySelector('{svg_sel}'), v = s.viewBox.baseVal;
                return [...s.querySelectorAll('text')].filter(t => {{
                    const b = t.getBBox();
                    return b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5;
                }}).map(t => t.textContent);
            }}''')

        def max_anchor_dist(svg_sel):
            return page.evaluate(f'''() => {{
                const s = document.querySelector('{svg_sel}');
                return Math.max(0, ...[...s.querySelectorAll('text[data-ax]:not([data-leader])')].map(t => {{
                    const b = t.getBBox(), ax = +t.getAttribute('data-ax'), ay = +t.getAttribute('data-ay');
                    const dx = ax < b.x ? b.x - ax : ax > b.x + b.width ? ax - (b.x + b.width) : 0;
                    const dy = ay < b.y ? b.y - ay : ay > b.y + b.height ? ay - (b.y + b.height) : 0;
                    return Math.hypot(dx, dy);
                }}));
            }}''')

        def leader_ok(svg_sel):
            """labels pushed away from their dot must have a leader line and stay within 130 px"""
            return page.evaluate(f'''() => {{
                const s = document.querySelector('{svg_sel}');
                return [...s.querySelectorAll('text[data-leader]')].filter(t => {{
                    const b = t.getBBox(), ax = +t.getAttribute('data-ax'), ay = +t.getAttribute('data-ay');
                    const far = Math.hypot(Math.max(b.x - ax, 0, ax - b.x - b.width), Math.max(b.y - ay, 0, ay - b.y - b.height)) > 130;
                    return far || !s.querySelector('line[data-leader="' + t.getAttribute('data-gas') + '"]');
                }}).map(t => t.textContent);
            }}''')

        def clip(path, sel, x, y, w, h):
            """z = 2 local shot: (x, y, w, h) in the svg's viewBox units"""
            fb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, k: r.width / e.viewBox.baseVal.width}; }')
            k = fb['k']
            page.screenshot(path=str(path), clip={'x': fb['x'] + x * k, 'y': fb['y'] + y * k, 'width': w * k, 'height': h * k},
                            full_page=True, timeout=30000)

        if scheme == 'dark':
            print('== dark mode')
            shot(page, '.k', OUT / 'card-tab1-dark.png')
            shot(page, '.rg-zsvg', OUT / 'zoom-zp-dark.png')
            vwd = page.evaluate('() => document.querySelector(".rg-zsvg").viewBox.baseVal.width')
            clip(OUT / 'zoom-legend-dark.png', '.rg-zsvg', 0, 0, vwd / 2, 40)
            clip(OUT / 'zoom-liquefies-dark.png', '.rg-zsvg', 40, 250, 300, 210)
            ideal_col = page.eval_on_selector('.rg-zsvg line.rg-ideal', 'e => getComputedStyle(e).stroke')
            c1_col = page.eval_on_selector('.rg-zsvg polyline.rg-curve[data-gas="N₂"]', 'e => getComputedStyle(e).stroke')
            check('dark: ideal line colour differs from N₂ curve', ideal_col != c1_col, f'{ideal_col} vs {c1_col}')
            check('dark: tab 1 no label clash', clashes('.rg-zsvg') == 0, str(clashes('.rg-zsvg')))
            check('dark: tab 1 labels inside viewBox', not outside('.rg-zsvg'), str(outside('.rg-zsvg')))
            page.click('.tabbar button[data-tab="vm"]'); page.wait_for_timeout(100)
            shot(page, '.k', OUT / 'card-tab2-dark.png')
            v2d = page.evaluate('() => document.querySelector(".rg-vsvg").viewBox.baseVal.width')
            clip(OUT / 'zoom-vm-imf-dark.png', '.rg-vsvg', v2d * 0.35, 50, v2d * 0.65, 280)
            check('dark: tab 2 no label clash', clashes('.rg-vsvg') == 0, str(clashes('.rg-vsvg')))
            check('dark: tab 2 labels inside viewBox', not outside('.rg-vsvg'), str(outside('.rg-vsvg')))
            ctx.close()
            continue

        print('== tab 1: vdW numerical checks at 300 K & 400 K')
        z_n2_300_100 = page.evaluate('() => document.querySelector(".k").__rg.zAt("N₂", 300, 100).Z')
        check('N₂ 300 K 100 atm: Z in [0.95, 1.05]', 0.95 <= z_n2_300_100 <= 1.05, f'{z_n2_300_100:.4f}')

        z_n2_300_800 = page.evaluate('() => document.querySelector(".k").__rg.zAt("N₂", 300, 800).Z')
        check('N₂ 300 K 800 atm: Z > 1.3', z_n2_300_800 > 1.3, f'{z_n2_300_800:.4f}')

        co2_300 = page.evaluate('() => document.querySelector(".k").__rg.zAt("CO₂", 300, 200)')
        check('CO₂ 300 K: T < Tc so curve truncates before 800 atm',
              co2_300['truncated'] and 50 < co2_300['pCut'] < 80, str(co2_300))
        check('CO₂ 300 K: polyline marked data-truncated="1"',
              page.get_attribute('.rg-zsvg .rg-curve[data-gas="CO₂"]', 'data-truncated') == '1')
        check('CO₂ 300 K: endpoint dot and "CO₂ liquefies" label drawn',
              page.locator('.rg-zsvg .rg-liq-pt[data-gas="CO₂"]').count() == 1 and
              'liquefies' in page.text_content('.rg-zsvg .rg-liq-lab[data-gas="CO₂"]'))

        he_min_z = page.evaluate('''() => {
            const rg = document.querySelector(".k").__rg;
            let mn = 99;
            for (let p = 0; p <= 800; p += 10) mn = Math.min(mn, rg.zAt("He", 300, p).Z);
            return mn;
        }''')
        check('He 300 K: Z >= 1 across 0–800 atm', he_min_z >= 1.0 - 1e-9, f'min Z = {he_min_z:.5f}')

        check('tab 1: 6 gas curves drawn at 300 K', page.locator('.rg-zsvg .rg-curve').count() == 6)
        check('tab 1: ideal gas dashed line + label present',
              page.locator('.rg-zsvg line.rg-ideal').count() >= 2 and
              page.locator('.rg-zsvg [data-role="ideal-line-label"]').text_content() == 'ideal gas')
        check('tab 1: legend uses K.label for ideal + 6 gases',
              page.locator('.rg-zsvg .rg-leg-lab').count() == 7)
        check('tab 1: both Z > 1 and Z < 1 region labels present',
              'molecular volume 占主导' in page.text_content('.rg-zsvg .rg-reg-gt') and
              'intermolecular attraction 占主导' in page.text_content('.rg-zsvg .rg-reg-lt'))
        check('tab 1: vdW disclaimer note present',
              'van der Waals 模型，示意；考试不要求' in page.inner_text('.rg-note'))
        check('tab 1 (300 K): no label clash', clashes('.rg-zsvg') == 0, str(clashes('.rg-zsvg')))
        check('tab 1 (300 K): all labels inside viewBox', not outside('.rg-zsvg'), str(outside('.rg-zsvg')))
        check('tab 1 (300 K): labels close to anchors (<= 36 px)', max_anchor_dist('.rg-zsvg') <= 36, f'{max_anchor_dist(".rg-zsvg"):.1f}')

        shot(page, '.k', OUT / 'card-tab1-300K.png')
        shot(page, '.rg-zsvg', OUT / 'zoom-zp-300K.png')
        vw = page.evaluate('() => document.querySelector(".rg-zsvg").viewBox.baseVal.width')
        clip(OUT / 'zoom-liquefies-300K.png', '.rg-zsvg', 40, 250, 300, 210)
        clip(OUT / 'zoom-legend-300K.png', '.rg-zsvg', 0, 0, vw / 2, 40)
        clip(OUT / 'zoom-legend-300K-right.png', '.rg-zsvg', vw / 2, 0, vw / 2, 40)
        clip(OUT / 'zoom-axes-x-300K.png', '.rg-zsvg', 0, 430, vw, 70)
        clip(OUT / 'zoom-axes-y-300K.png', '.rg-zsvg', 0, 36, 340, 420)
        clip(OUT / 'zoom-ideal-label-300K.png', '.rg-zsvg', vw - 330, 250, 330, 120)
        clip(OUT / 'zoom-regions-300K.png', '.rg-zsvg', vw - 520, 380, 520, 75)

        print('== tab 1: T slider & presets (200 K, 400 K, 600 K, 1000 K)')
        cap_300 = page.inner_text('.rg-cap')
        page.click('.rg-tpre button[data-t="400"]'); page.wait_for_timeout(60)
        z_co2_400_100 = page.evaluate('() => document.querySelector(".k").__rg.zAt("CO₂", 400, 100).Z')
        check('CO₂ 400 K 100 atm: Z < 0.85', z_co2_400_100 < 0.85, f'{z_co2_400_100:.4f}')
        check('CO₂ 400 K: no longer truncated (T = 400 K > Tc = 304 K)',
              page.get_attribute('.rg-zsvg .rg-curve[data-gas="CO₂"]', 'data-truncated') == '0')
        check('NH₃ 400 K: still truncated (T = 400 K < Tc = 406 K)',
              page.get_attribute('.rg-zsvg .rg-curve[data-gas="NH₃"]', 'data-truncated') == '1')
        cap_400 = page.inner_text('.rg-cap')
        check('caption updates when T changes 300 K → 400 K', cap_400 != cap_300 and '400 K' in cap_400, cap_400)
        shot(page, '.k', OUT / 'card-tab1-400K.png')

        for t_test in (200, 250, 300, 350, 400, 600, 1000):
            page.evaluate(f'() => document.querySelector(".k").__rg.setT({t_test})')
            page.wait_for_timeout(30)
            check(f'T = {t_test} K: 0 label clashes', clashes('.rg-zsvg') == 0, str(clashes('.rg-zsvg')))
            check(f'T = {t_test} K: labels inside viewBox', not outside('.rg-zsvg'), str(outside('.rg-zsvg')))
            check(f'T = {t_test} K: labels close to anchors', max_anchor_dist('.rg-zsvg') <= 36, f'{max_anchor_dist(".rg-zsvg"):.1f}')
            check(f'T = {t_test} K: displaced liquefies labels have leader lines', not leader_ok('.rg-zsvg'), str(leader_ok('.rg-zsvg')))
            cross = page.evaluate('''() => {
                const s = document.querySelector('.rg-zsvg'), bad = [];
                const o = (p, q, r) => (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0]);
                const X = (a, b) => o(a.slice(0,2), a.slice(2), b.slice(0,2)) * o(a.slice(0,2), a.slice(2), b.slice(2)) < 0 &&
                                    o(b.slice(0,2), b.slice(2), a.slice(0,2)) * o(b.slice(0,2), b.slice(2), a.slice(2)) < 0;
                s.querySelectorAll('line[data-leader]').forEach(l => {
                    const a = ['x1','y1','x2','y2'].map(k => +l.getAttribute(k)), me = l.getAttribute('data-leader');
                    const mine = (l.getAttribute('data-also') || me).split(' ');
                    s.querySelectorAll('polyline.rg-curve').forEach(pl => {
                        if (mine.includes(pl.getAttribute('data-gas'))) return;
                        const pts = pl.getAttribute('points').trim().split(/\\s+/).map(q => q.split(',').map(Number));
                        for (let i = 1; i < pts.length; i++) if (X(a, [...pts[i-1], ...pts[i]])) { bad.push(me + '×' + pl.getAttribute('data-gas')); return; }
                    });
                });
                return bad;
            }''')
            check(f'T = {t_test} K: liquefies leaders cross no other gas curve', not cross, str(cross))
            if t_test == 200:
                liq_txt = ' | '.join(page.locator('.rg-zsvg .rg-liq-lab').all_text_contents())
                check('T = 200 K: CO₂ and NH₃ both named in liquefies label(s)', 'CO₂' in liq_txt and 'NH₃' in liq_txt and 'liquef' in liq_txt, liq_txt)
                clip(OUT / 'zoom-liquefies-200K.png', '.rg-zsvg', 40, 250, 280, 210)

        page.evaluate('() => { const s = document.querySelector(".rg-t"); s.value = 520; s.dispatchEvent(new Event("input", {bubbles: true})); }')
        page.wait_for_timeout(40)
        check('T slider input redraws chart (data-t = 520) and readout shows 520 K',
              page.get_attribute('.rg-zsvg', 'data-t') == '520' and '520 K' in page.inner_text('.rg-tval') and '247 °C' in page.inner_text('.rg-tval'),
              page.inner_text('.rg-tval'))
        check('T slider: caption follows slider', '520 K' in page.inner_text('.rg-cap'))
        page.click('.rg-tpre button[data-t="200"]'); page.wait_for_timeout(50)
        check('200 K preset: button highlighted, CO₂ + NH₃ truncated',
              page.locator('.rg-tpre button.on').inner_text() == '200 K' and page.locator('.rg-zsvg .rg-liq-pt').count() == 2)
        shot(page, '.k', OUT / 'card-tab1-200K.png')
        page.click('.rg-tpre button[data-t="1000"]'); page.wait_for_timeout(50)
        check('1000 K: no gas liquefies', page.locator('.rg-zsvg .rg-liq-pt').count() == 0)
        shot(page, '.k', OUT / 'card-tab1-1000K.png')
        page.click('.rg-tpre button[data-t="300"]'); page.wait_for_timeout(50)

        print('== tab 1: gas multi-select & hover')
        sw = page.eval_on_selector_all('.rg-gas .rg-sw line', 'ls => ls.map(l => getComputedStyle(l).stroke)')
        check('gas toggles: every swatch has a coloured stroke', len(sw) == 6 and all(c not in ('none', '') for c in sw), str(sw))
        page.click('.rg-gas[data-gas="He"]'); page.wait_for_timeout(40)
        check('unchecking He leaves 5 curves', page.locator('.rg-zsvg .rg-curve').count() == 5)
        check('unchecking He dims its legend entry and its toggle',
              page.get_attribute('.rg-zsvg [data-leg="He"]', 'opacity') == '0.4' and
              'on' not in (page.get_attribute('.rg-gas[data-gas="He"]', 'class') or '').split())
        page.click('.rg-gas[data-gas="CO₂"]'); page.wait_for_timeout(40)
        check('unchecking CO₂ leaves 4 curves and only NH₃ liquefies dot',
              page.locator('.rg-zsvg .rg-curve').count() == 4 and page.locator('.rg-zsvg .rg-liq-pt').count() == 1)
        page.click('.rg-all'); page.wait_for_timeout(40)
        check('全选 restores all 6 curves', page.locator('.rg-zsvg .rg-curve').count() == 6)

        # Hover over CH4 at ~100 atm (Z < 1) and N2 at ~700 atm (Z > 1)
        sbox = page.locator('.rg-zsvg').bounding_box()
        page.mouse.move(sbox['x'] + sbox['width'] * 0.18, sbox['y'] + sbox['height'] * 0.68)
        page.wait_for_timeout(40)
        htxt_low = page.inner_text('.rg-hover')
        check('hover at low-moderate p (Z < 1) shows attraction dominant',
              'attraction 占主导 → Z < 1' in htxt_low, htxt_low)
        hg, hp, hz = (page.get_attribute('.rg-hover', a) for a in ('data-gas', 'data-p', 'data-z'))
        check('hover readout names gas, p and Z', hg in htxt_low and f'p = {hp} atm' in htxt_low and f'Z = {float(hz):.3f}' in htxt_low,
              f'{hg} {hp} {hz} | {htxt_low}')
        check('hover draws crosshair + probe dots', page.locator('.rg-zsvg .rg-xhair').count() == 1 and
              page.locator('.rg-zsvg circle[fill^="var(--s"]').count() >= 4)
        shot(page, '.rg-hover', OUT / 'zoom-hover-zlt1.png')
        shot(page, '.k', OUT / 'card-tab1-hover-zlt1.png')

        page.mouse.move(sbox['x'] + sbox['width'] * 0.78, sbox['y'] + sbox['height'] * 0.30)
        page.wait_for_timeout(40)
        htxt_high = page.inner_text('.rg-hover')
        check('hover at high p (Z > 1) shows molecular volume dominant',
              'molecular volume 占主导 → Z > 1' in htxt_high, htxt_high)
        shot(page, '.rg-hover', OUT / 'zoom-hover-zgt1.png')
        shot(page, '.rg-plot', OUT / 'plot-hover-zgt1.png')
        page.mouse.move(sbox['x'] + sbox['width'] * 0.115, sbox['y'] + sbox['height'] * 0.76)
        page.wait_for_timeout(40)
        htxt_liq = page.inner_text('.rg-hover')
        check('hover past a liquefies endpoint says liquefy', '已 liquefy' in htxt_liq or 'liquefies' in htxt_liq, htxt_liq)
        page.mouse.move(sbox['x'] + sbox['width'] * 0.18, sbox['y'] + sbox['height'] * 0.68)

        print('== tab 2: molar volume at s.t.p. (8 bars)')
        page.click('.tabbar button[data-tab="vm"]'); page.wait_for_timeout(120)
        bars = page.eval_on_selector_all(
            '.rg-vsvg .rg-bar',
            'bs => bs.map(b => [b.getAttribute("data-gas"), +b.getAttribute("data-vm"), +b.getAttribute("width"), b.getAttribute("data-imf")])',
        )
        expected_bars = [
            ('He', 22.4), ('N₂', 22.4), ('O₂', 22.4), ('CH₄', 22.3),
            ('CO₂', 22.3), ('C₂H₄', 22.2), ('NH₃', 22.1), ('SO₂', 21.9),
        ]
        check('tab 2: 8 horizontal bars with lecture-note s.t.p. values',
              [(b[0], b[1]) for b in bars] == expected_bars, str([(b[0], b[1]) for b in bars]))
        check('tab 2: bar widths strictly follow molar volume (He > CH₄ > C₂H₄ > NH₃ > SO₂)',
              bars[0][2] > bars[3][2] > bars[5][2] > bars[6][2] > bars[7][2], str([round(b[2], 1) for b in bars]))
        check('tab 2: every bar has an IMF label placed via K.label',
              page.locator('.rg-vsvg .rg-bar-imf').count() == 8)
        check('tab 2: 22.4 reference line and label present',
              '22.4 dm³ mol⁻¹' in page.text_content('.rg-vsvg [data-role="ref-224-label"]'))
        check('tab 2: truncated axis from 21.5 noted explicitly',
              '21.5' in page.text_content('.rg-vsvg [data-role="trunc-note"]') and '截断轴' in page.text_content('.rg-vsvg [data-role="trunc-note"]'))
        q2b_txt = page.inner_text('.rg-q2b')
        check('tab 2: cites 9701/23 May/June 2026 Q2(b) with Ne, smallest volume, weakest id-id, and comparative note',
              '9701/23 May/June 2026 Q2(b)' in q2b_txt and 'neon' in q2b_txt and
              'smallest' in q2b_txt and 'weakest' in q2b_txt and '比较级' in q2b_txt, q2b_txt)
        imfs = page.eval_on_selector_all('.rg-vsvg .rg-bar-imf', 'ts => ts.map(t => t.textContent)')
        check('tab 2: each IMF label names its force (id-id / hydrogen bonding / pd-pd) and its volume',
              len(imfs) == 8 and all(('id-id' in t or 'hydrogen' in t) and t.startswith(v) for t, (_, v) in zip(imfs, [(g, f'{v:.1f}') for g, v in expected_bars])), str(imfs))
        ticks = page.eval_on_selector_all('.rg-vsvg text.rg-tick', 'ts => ts.map(t => t.textContent)')
        check('tab 2: axis ticks start at 21.5 and include 22.4', ticks[:1] == ['21.5'] and '22.4' in ticks, str(ticks))
        check('tab 2: 22.4 reference line drawn dashed', page.locator('.rg-vsvg line.rg-ideal').count() == 1)
        check('tab 2: axis-break mark at the 21.5 end', page.locator('.rg-vsvg path[data-role="axis-break"]').count() == 1)
        check('tab 2: no label clash', clashes('.rg-vsvg') == 0, str(clashes('.rg-vsvg')))
        check('tab 2: all labels inside viewBox', not outside('.rg-vsvg'), str(outside('.rg-vsvg')))
        shot(page, '.k', OUT / 'card-tab2.png')
        shot(page, '.rg-vsvg', OUT / 'zoom-vm-bars.png')
        shot(page, '.rg-q2b', OUT / 'zoom-q2b.png')
        v2 = page.evaluate('() => document.querySelector(".rg-vsvg").viewBox.baseVal.width')
        clip(OUT / 'zoom-vm-trunc-note.png', '.rg-vsvg', 0, 0, v2 * 0.75, 60)
        clip(OUT / 'zoom-vm-axis.png', '.rg-vsvg', 0, 300, v2, 135)
        clip(OUT / 'zoom-vm-imf-top.png', '.rg-vsvg', v2 * 0.35, 50, v2 * 0.65, 160)
        clip(OUT / 'zoom-vm-imf-bottom.png', '.rg-vsvg', v2 * 0.35, 200, v2 * 0.65, 130)

        print('== narrow (720 px) on both tabs')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(200)
        ov2 = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        fs2 = page.evaluate('''() => {
            const s = document.querySelector('.rg-vsvg'), k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k));
        }''')
        check('tab 2 at 720 px: no horizontal overflow', ov2 <= 0, str(ov2))
        check('tab 2 at 720 px: font size >= 12 px', fs2 >= 12, f'{fs2:.2f}')
        check('tab 2 at 720 px: no label clash', clashes('.rg-vsvg') == 0, str(clashes('.rg-vsvg')))
        check('tab 2 at 720 px: labels inside viewBox', not outside('.rg-vsvg'), str(outside('.rg-vsvg')))
        shot(page, '.k', OUT / 'card-tab2-720.png')

        page.click('.tabbar button[data-tab="zp"]'); page.wait_for_timeout(200)
        ov1 = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        fs1 = page.evaluate('''() => {
            const s = document.querySelector('.rg-zsvg'), k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k));
        }''')
        check('tab 1 at 720 px: no horizontal overflow', ov1 <= 0, str(ov1))
        check('tab 1 at 720 px: font size >= 12 px', fs1 >= 12, f'{fs1:.2f}')
        check('tab 1 at 720 px: no label clash', clashes('.rg-zsvg') == 0, str(clashes('.rg-zsvg')))
        check('tab 1 at 720 px: labels inside viewBox', not outside('.rg-zsvg'), str(outside('.rg-zsvg')))
        shot(page, '.k', OUT / 'card-tab1-720.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
