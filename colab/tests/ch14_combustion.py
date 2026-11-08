"""ch14 combustion cell test — combustion balancing & catalytic converter exhaust flow.

usage: uv run --with playwright python -I colab/tests/ch14_combustion.py $COLAB_TMP/cells/ch14-combustion.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch14 --cell combustion)
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


def shot(page, sel, path):
    """element screenshot via a page clip (avoids hanging on waiting for stable rAF)."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


# Check built HTML text hygiene before launching browser
raw = PAGE.read_text(encoding='utf-8')
vis_txt = re.sub(r'<[^>]+>', '', re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', raw, flags=re.S | re.I))
check('built HTML: no leaked literal * / {{ in visible text', '*' not in vis_txt and '{{' not in vis_txt, vis_txt[:100])

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])

    for scheme in ('light', 'dark'):
        print(f'== Scheme: {scheme}')
        ctx = b.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme} PAGEERROR: {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300)

        def tab(name):
            page.click(f'.tabbar button[data-tab="{name}"]')
            page.wait_for_timeout(100)

        def clashes():
            return page.locator('[data-clash]').count()

        # =========================================================
        # TAB 1: COMBUSTION BALANCING & PRACTICE
        # =========================================================
        print('== Tab 1: combustion balancing & conservation')
        tab('bal')

        # 1. Assert all 48 combinations in JS are elemental-balanced
        js_balanced = page.evaluate('() => window.T_root ? window.T_root.__cb.allBalanced : document.querySelector(".k").__cb.allBalanced')
        check('all 8 alkanes x 3 tiers x 2 doubled states strictly atom-balanced in JS', js_balanced is True)

        # 2. Verify 3 sampled alkanes independently in test:
        # Sample A: Methane (n=1)
        page.click('.cb-alk-btn[data-idx="0"]')  # methane
        page.wait_for_timeout(50)
        # Tier 0 (complete)
        page.evaluate('() => document.querySelector(".k").__cb.setTier(0)')
        page.wait_for_timeout(50)
        eq_m0 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('methane complete: CH₄ + 2O₂ → CO₂ + 2H₂O', 'CH₄ + 2O₂ → CO₂ + 2H₂O' in eq_m0, eq_m0)

        # Tier 1 (CO)
        page.evaluate('() => document.querySelector(".k").__cb.setTier(1)')
        page.wait_for_timeout(50)
        eq_m1 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('methane incomplete (CO): CH₄ + 1½O₂ → CO + 2H₂O', 'CH₄ + 1½O₂ → CO + 2H₂O' in eq_m1, eq_m1)

        # Tier 2 (C soot)
        page.evaluate('() => document.querySelector(".k").__cb.setTier(2)')
        page.wait_for_timeout(50)
        eq_m2 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('methane incomplete (C): CH₄ + O₂ → C + 2H₂O', 'CH₄ + O₂ → C + 2H₂O' in eq_m2, eq_m2)

        # Sample B: Hexane (n=6, past paper 9701_w25_22)
        page.click('.cb-alk-btn[data-idx="5"]')  # hexane
        page.wait_for_timeout(50)
        page.evaluate('() => document.querySelector(".k").__cb.setTier(0)')
        page.wait_for_timeout(50)
        eq_h0 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('hexane complete: C₆H₁₄ + 9½O₂ → 6CO₂ + 7H₂O', 'C₆H₁₄ + 9½O₂ → 6CO₂ + 7H₂O' in eq_h0, eq_h0)

        page.evaluate('() => document.querySelector(".k").__cb.setTier(1)')
        page.wait_for_timeout(50)
        eq_h1 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('hexane incomplete (CO): C₆H₁₄ + 6½O₂ → 6CO + 7H₂O', 'C₆H₁₄ + 6½O₂ → 6CO + 7H₂O' in eq_h1, eq_h1)

        page.evaluate('() => document.querySelector(".k").__cb.setTier(2)')
        page.wait_for_timeout(50)
        eq_h2 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('hexane incomplete (C): C₆H₁₄ + 3½O₂ → 6C + 7H₂O', 'C₆H₁₄ + 3½O₂ → 6C + 7H₂O' in eq_h2, eq_h2)

        # Sample C: Octane (n=8, syllabus & ch14 notes)
        page.click('.cb-alk-btn[data-idx="7"]')  # octane
        page.wait_for_timeout(50)
        page.evaluate('() => document.querySelector(".k").__cb.setTier(0)')
        page.wait_for_timeout(50)
        eq_o0 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('octane complete: C₈H₁₈ + 12½O₂ → 8CO₂ + 9H₂O', 'C₈H₁₈ + 12½O₂ → 8CO₂ + 9H₂O' in eq_o0, eq_o0)

        page.evaluate('() => document.querySelector(".k").__cb.setTier(1)')
        page.wait_for_timeout(50)
        eq_o1 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('octane incomplete (CO): C₈H₁₈ + 8½O₂ → 8CO + 9H₂O', 'C₈H₁₈ + 8½O₂ → 8CO + 9H₂O' in eq_o1, eq_o1)

        page.evaluate('() => document.querySelector(".k").__cb.setTier(2)')
        page.wait_for_timeout(50)
        eq_o2 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('octane incomplete (C): C₈H₁₈ + 4½O₂ → 8C + 9H₂O', 'C₈H₁₈ + 4½O₂ → 8C + 9H₂O' in eq_o2, eq_o2)

        # 3. Test "×2 去掉 ½" toggle button
        page.evaluate('() => document.querySelector(".k").__cb.setTier(0)')  # octane complete
        page.wait_for_timeout(50)
        btn_double = page.locator('.cb-btn-double')
        btn_double.click()
        page.wait_for_timeout(50)
        eq_dbl = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('octane doubled: 2C₈H₁₈ + 25O₂ → 16CO₂ + 18H₂O', '2C₈H₁₈ + 25O₂ → 16CO₂ + 18H₂O' in eq_dbl, eq_dbl)
        check('button says ÷2 还原 ½', '÷2' in btn_double.text_content(), btn_double.text_content())

        btn_double.click()
        page.wait_for_timeout(50)
        eq_half = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('octane restored to fractional: C₈H₁₈ + 12½O₂ → 8CO₂ + 9H₂O', '12½O₂' in eq_half, eq_half)

        # 4. Test practice inputs & judging
        print('== Tab 1 practice judging')
        # Fill wrong values
        page.fill('.cb-in-alk', '1')
        page.fill('.cb-in-o2', '10')  # should be 12.5
        page.fill('.cb-in-prod', '8')
        page.fill('.cb-in-h2o', '9')
        page.click('.cb-check-btn')
        page.wait_for_timeout(50)
        fb_bad = page.text_content('.cb-fb')
        check('wrong O2 coefficient flags error', '不守恒' in fb_bad and 'O' in fb_bad, fb_bad)
        check('o2 input has badv class', 'badv' in (page.get_attribute('.cb-in-o2', 'class') or ''))

        # Fill correct fractional values (12.5)
        page.fill('.cb-in-o2', '12.5')
        page.click('.cb-check-btn')
        page.wait_for_timeout(50)
        fb_ok = page.text_content('.cb-fb')
        check('correct fractional values (12.5) pass check', '✓' in fb_ok and '守恒' in fb_ok, fb_ok)
        check('all inputs have good class', all('good' in (page.get_attribute(f'.cb-in-{k}', 'class') or '') for k in ['alk', 'o2', 'prod', 'h2o']))

        # Fill correct 12½ fraction
        page.fill('.cb-in-o2', '12½')
        page.click('.cb-check-btn')
        page.wait_for_timeout(50)
        check('fraction 12½ passes check', '✓' in page.text_content('.cb-fb'))

        # Fill correct doubled values (2, 25, 16, 18)
        page.fill('.cb-in-alk', '2')
        page.fill('.cb-in-o2', '25')
        page.fill('.cb-in-prod', '16')
        page.fill('.cb-in-h2o', '18')
        page.click('.cb-check-btn')
        page.wait_for_timeout(50)
        check('doubled integer coefficients (2, 25, 16, 18) pass check', '✓' in page.text_content('.cb-fb'))

        # Test reset
        page.click('.cb-reset-btn')
        page.wait_for_timeout(50)
        check('reset clears inputs', page.input_value('.cb-in-alk') == '' and page.is_hidden('.cb-fb'))

        # Test show answer
        page.click('.cb-show-btn')
        page.wait_for_timeout(50)
        check('show answer fills correct values', page.input_value('.cb-in-alk') == '1' and '12½' in page.input_value('.cb-in-o2'))

        shot(page, '.cb-wrap', OUT / f'tab-bal-{scheme}.png')

        # severely-limited tier with ½ coefficient (ethane: C₂H₆ + 1½O₂ → 2C + 3H₂O)
        page.click('.cb-alk-btn[data-idx="1"]')
        page.evaluate('() => document.querySelector(".k").__cb.setTier(2)')
        page.wait_for_timeout(50)
        eq_e2 = page.text_content('.cb-eq-text').replace('\xa0', ' ').strip()
        check('ethane incomplete (C): C₂H₆ + 1½O₂ → 2C + 3H₂O', 'C₂H₆ + 1½O₂ → 2C + 3H₂O' in eq_e2, eq_e2)
        page.fill('.cb-in-alk', '2'); page.fill('.cb-in-o2', '3'); page.fill('.cb-in-prod', '4'); page.fill('.cb-in-h2o', '6')
        page.click('.cb-check-btn'); page.wait_for_timeout(50)
        check('ethane soot doubled (2, 3, 4, 6) passes', '✓' in page.text_content('.cb-fb'))
        page.fill('.cb-in-o2', '3.5'); page.click('.cb-check-btn'); page.wait_for_timeout(50)
        check('ethane soot with O₂ = 3.5 is rejected', '✗' in page.text_content('.cb-fb'))
        if scheme == 'light':
            shot(page, '.cb-eq-box', OUT / 'bal-soot-ethane-z2.png')
        # whole-number tier disables the ×2 button (methane complete)
        page.click('.cb-alk-btn[data-idx="0"]')
        page.evaluate('() => document.querySelector(".k").__cb.setTier(0)')
        page.wait_for_timeout(50)
        check('×2 button disabled when coefficients are already whole', page.is_disabled('.cb-btn-double'))
        page.click('.cb-alk-btn[data-idx="7"]')
        page.wait_for_timeout(50)

        # =========================================================
        # TAB 2: EXHAUST FLOW & CATALYTIC CONVERTER
        # =========================================================
        print('== Tab 2: exhaust flow & catalytic converter')
        tab('flow')
        page.wait_for_timeout(100)

        # 1. Structural elements present
        check('SVG flow diagram present', page.locator('.cb-flow-svg').count() == 1)
        check('Engine, exhaust pipe, converter, tailpipe present',
              page.locator('.cb-engine-zone').count() == 1 and
              page.locator('.cb-conv-zone').count() == 1 and
              page.locator('.cb-post-pipe-zone').count() == 1)

        # 2. Animation & multi-frame sampling
        is_playing = page.evaluate('() => document.querySelector(".k").__cb.playing()')
        check('animation initially playing', is_playing is True)

        samples = []
        for _ in range(5):
            page.wait_for_timeout(150)
            p0 = page.evaluate('() => document.querySelector(".k").__cb.particles()[0]')
            samples.append(p0['x'])
        check('≥ 3 distinct x positions sampled while animation is playing', len({round(x, 1) for x in samples}) >= 3, str(samples))

        # Pause test
        page.click('.cb-anim-btn')  # Pause
        page.wait_for_timeout(50)
        paused = page.evaluate('() => document.querySelector(".k").__cb.playing()')
        check('pause button pauses animation', paused is False and '播放' in page.text_content('.cb-anim-btn'))

        freeze_x1 = page.evaluate('() => document.querySelector(".k").__cb.particles()[0]["x"]')
        page.wait_for_timeout(250)
        freeze_x2 = page.evaluate('() => document.querySelector(".k").__cb.particles()[0]["x"]')
        check('particles frozen while paused', freeze_x1 == freeze_x2, f'{freeze_x1} vs {freeze_x2}')

        # Resume test
        page.click('.cb-anim-btn')  # Resume
        page.wait_for_timeout(100)
        check('resume button restarts animation', page.evaluate('() => document.querySelector(".k").__cb.playing()') is True)

        # Advance hook test
        page.evaluate('() => document.querySelector(".k").__cb.advance(1200)')
        adv_p0 = page.evaluate('() => document.querySelector(".k").__cb.particles()[0]["x"]')
        check('advance hook updates particle positions', adv_p0 != freeze_x1)

        # 3. Pollutant detail cards
        print('== Tab 2: pollutant cards')
        # Click CO
        page.click('.cb-pol-btn[data-pol="co"]')
        page.wait_for_timeout(50)
        co_text = page.text_content('.cb-detail-card')
        check('CO card details source & haemoglobin harm', 'incomplete combustion' in co_text and 'haemoglobin' in co_text)
        check('CO card lists 2CO + O2 and 2CO + 2NO equations', '2CO + O₂ → 2CO₂' in co_text and '2CO + 2NO → 2CO₂ + N₂' in co_text)
        check('CO card does not claim haemoglobin binding is irreversible', '不可逆' not in co_text and 'irreversib' not in co_text)
        check('detail equations are not in monospace <code> (O vs 0 ambiguity)',
              page.locator('.cb-detail-card code').count() == 0 and page.locator('.cb-detail-card .cb-eqn').count() >= 1)
        if scheme == 'light':
            shot(page, '.cb-detail-card', OUT / 'card-co-light.png')

        # Click NOx
        page.click('.cb-pol-btn[data-pol="nox"]')
        page.wait_for_timeout(50)
        nox_text = page.text_content('.cb-detail-card')
        check('NOx card details high temp & pressure formation', 'high temperature and pressure' in nox_text and 'N₂ + O₂ → 2NO' in nox_text)
        check('NOx card mentions acid rain & photochemical smog', 'acid rain' in nox_text and 'photochemical smog' in nox_text)
        check('NOx card includes chapter 12 plain text reference', 'chapter 12' in nox_text)
        check('NOx card lists reduction equation 2CO + 2NO → 2CO₂ + N₂', '2CO + 2NO → 2CO₂ + N₂' in nox_text)

        # Click Unburnt HC
        page.click('.cb-pol-btn[data-pol="hc"]')
        page.wait_for_timeout(50)
        hc_text = page.text_content('.cb-detail-card')
        check('Unburnt HC card mentions photochemical smog & carcinogenic', 'photochemical smog' in hc_text and 'carcinogenic' in hc_text)
        check('Unburnt HC card lists oxidation equation', 'CxHy + (x + y/4)O₂ → xCO₂ + (y/2)H₂O' in hc_text, hc_text)
        check('no Greek subscript gamma (ᵧ) used as subscript y anywhere',
              'ᵧ' not in page.text_content('.cb-wrap'))
        if scheme == 'light':
            shot(page, '.cb-detail-card', OUT / 'card-hc-light.png')

        # 4. Greenhouse gas alert check
        ghg_box = page.text_content('.cb-ghg-alert')
        check('greenhouse gas alert explains CO2 cannot be removed', '无法除去 CO₂' in ghg_box and 'greenhouse gas' in ghg_box)
        check('inline <b>CO₂</b> in the alert paragraph stays inline',
              page.evaluate('() => getComputedStyle(document.querySelector(".cb-ghg-alert p b")).display') == 'inline')

        # 4b. SVG static text geometry: inside viewBox, no text/text overlap, no shape edge through text,
        #     greenhouse lines inside their box
        geo = page.evaluate('''() => {
          const s = document.querySelector('.cb-flow-svg'), vb = s.viewBox.baseVal;
          const texts = [...s.querySelectorAll('text')].map(t => { const b = t.getBBox();
            return {s: t.textContent, x: b.x, y: b.y, w: b.width, h: b.height, ax: t.getAttribute('x'), ay: +t.getAttribute('y'),
                    fs: parseFloat(getComputedStyle(t).fontSize)}; });
          // lines of one multi-line label (same anchor x) may share line-box padding, but the baseline pitch must be >= 1.1 em
          const stacked = (a, b) => a.ax === b.ax && Math.abs(a.ay - b.ay) >= 1.1 * Math.max(a.fs, b.fs);
          const segs = [];
          s.querySelectorAll('rect:not(.cb-svg-bg):not(.cb-svg-ghg-box), polygon, line:not(.cb-grid-line)').forEach(e => {
            let p;
            if (e.tagName === 'rect') { const x = +e.getAttribute('x'), y = +e.getAttribute('y'), w = +e.getAttribute('width'), h = +e.getAttribute('height'); p = [[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]]; }
            else if (e.tagName === 'polygon') { p = e.getAttribute('points').trim().split(/\\s+/).map(q => q.split(',').map(Number)); p.push(p[0]); }
            else p = [[+e.getAttribute('x1'), +e.getAttribute('y1')], [+e.getAttribute('x2'), +e.getAttribute('y2')]];
            for (let i = 1; i < p.length; i++) segs.push(p[i-1].concat(p[i]));
          });
          const hitSeg = (r, g) => {  // sample along the segment
            for (let k = 0; k <= 40; k++) { const x = g[0] + (g[2]-g[0])*k/40, y = g[1] + (g[3]-g[1])*k/40;
              if (x > r.x && x < r.x + r.w && y > r.y && y < r.y + r.h) return true; }
            return false; };
          const out = [], over = [], cross = [];
          texts.forEach((a, i) => {
            if (a.x < vb.x || a.y < vb.y || a.x + a.w > vb.x + vb.width || a.y + a.h > vb.y + vb.height) out.push(a.s);
            texts.slice(i+1).forEach(b => { if (!stacked(a, b) && a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) over.push(a.s + ' / ' + b.s); });
            segs.forEach(g => { if (hitSeg(a, g)) cross.push(a.s); });
          });
          const gb = s.querySelector('.cb-svg-ghg-box').getBBox();
          const ghgOut = [...s.querySelectorAll('.cb-txt-ghg')].filter(t => { const b = t.getBBox();
            return b.x < gb.x + 4 || b.y < gb.y + 1 || b.x + b.width > gb.x + gb.width - 4 || b.y + b.height > gb.y + gb.height - 1; }).map(t => t.textContent);
          return {out, over, cross: [...new Set(cross)], ghgOut};
        }''')
        check(f'{scheme}: SVG text inside viewBox', not geo['out'], str(geo['out']))
        check(f'{scheme}: SVG text boxes do not overlap', not geo['over'], str(geo['over']))
        check(f'{scheme}: no box / pipe / arrow edge runs through SVG text', not geo['cross'], str(geo['cross']))
        check(f'{scheme}: greenhouse-gas text fits inside its box with margin', not geo['ghgOut'], str(geo['ghgOut']))

        # 4c. live before / after counts match the particles
        page.click('.cb-anim-btn'); page.wait_for_timeout(50)   # pause so counts are stable
        cnt = page.evaluate('''() => { const cb = document.querySelector(".k").__cb, ps = cb.particles();
          const pre = {co:0, nox:0, hc:0}; let post = 0, postPol = 0;
          ps.forEach(p => { if (p.cx < 375) pre[p.type]++; else if (p.cx >= 500) { post++; if (p.state !== 'clean') postPol++; } });
          const t = k => document.querySelector(`[data-cnt="${k}"]`).textContent;
          return {pre, post, postPol, txt: ['pre-co','pre-nox','pre-hc','post-pol','post-clean'].map(t)}; }''')
        exp = [f"CO × {cnt['pre']['co']}", f"NOₓ × {cnt['pre']['nox']}", f"HC × {cnt['pre']['hc']}",
               'CO / NOₓ / HC × 0', f"CO₂ / N₂ / H₂O × {cnt['post']}"]
        check('before / after pills show the live particle counts', cnt['txt'] == exp and cnt['postPol'] == 0, f"{cnt['txt']} vs {exp}")
        check('every pollutant type is visible before the converter', min(cnt['pre'].values()) >= 2, str(cnt['pre']))
        hits = page.evaluate('''() => { const cb = document.querySelector(".k").__cb, s = document.querySelector('.cb-flow-svg');
          const tb = [...s.querySelectorAll('text')].map(t => [t.textContent, t.getBBox()]); const t0 = cb.t(), out = new Set();
          for (let k = 0; k < 80; k++) { cb.setT(t0 + k * 0.137);
            s.querySelectorAll('.cb-p-dot').forEach(c => { const x = +c.getAttribute('cx'), y = +c.getAttribute('cy'), r = +c.getAttribute('r');
              tb.forEach(([n, b]) => { if (x + r > b.x && x - r < b.x + b.width && y + r > b.y && y - r < b.y + b.height) out.add(n); }); }); }
          cb.setT(t0); return [...out]; }''')
        check('particles never run over any SVG label (80 sampled frames)', not hits, str(hits))
        page.click('.cb-anim-btn'); page.wait_for_timeout(50)

        # 5. Converter contrast check: pre vs post converter particle states
        all_p = page.evaluate('() => document.querySelector(".k").__cb.particles()')
        pre_p = [p for p in all_p if p['cx'] < 375]
        post_p = [p for p in all_p if p['cx'] > 500]
        check('pre-converter contains raw pollutant particles', len(pre_p) > 0 and all(p['state'] == 'raw' for p in pre_p))
        check('post-converter contains only clean converted particles (zero pollutants)', len(post_p) > 0 and all(p['state'] == 'clean' for p in post_p))

        # Check label collisions
        check(f'{scheme}: no data-clash in cell', clashes() == 0, str(clashes()))

        # Take screenshots
        if scheme == 'light':
            shot(page, '.cb-wrap', OUT / 'tab-flow-light.png')
            # z=2 detail of catalytic converter area
            shot(page, '.cb-conv-zone', OUT / 'flow-detail-z2.png')
        else:
            shot(page, '.cb-wrap', OUT / 'tab-flow-dark.png')

        # =========================================================
        # 720 px Viewport Test
        # =========================================================
        print(f'== Narrow (720 px) in {scheme}')
        page.set_viewport_size({'width': 720, 'height': 1200})
        page.wait_for_timeout(200)

        ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('no horizontal overflow at 720 px', ov <= 0, f'overflow = {ov}px')

        fs_min = page.evaluate('''() => {
            const s = document.querySelector('.cb-flow-svg');
            const k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k));
        }''')
        check('SVG font size (CSS px x rendered / viewBox width) >= 12 at 720 px', fs_min >= 12.0, f'{fs_min:.2f}px')

        shot(page, '.cb-wrap', OUT / f'tab-flow-720-{scheme}.png')
        tab('bal')
        page.wait_for_timeout(100)
        ov_b = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('balancer tab: no horizontal overflow at 720 px', ov_b <= 0, f'overflow = {ov_b}px')
        check('switching back to the balancer pauses the animation',
              page.evaluate('() => document.querySelector(".k").__cb.playing()') is False)
        if scheme == 'light':
            shot(page, '.cb-wrap', OUT / 'tab-bal-720.png')

        ctx.close()

    b.close()

check('no console errors / page errors throughout all tests', not errors, '; '.join(errors))

n_pass = sum(1 for r in results if r[1])
print(f'\n{n_pass}/{len(results)} passed')
sys.exit(0 if n_pass == len(results) else 1)
