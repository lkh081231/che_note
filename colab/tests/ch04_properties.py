"""ch04 properties cell test (2D animated: malleable vs brittle + electrical conductivity).

usage: uv run --with playwright python -I colab/tests/ch04_properties.py $COLAB_TMP/cells/ch04-properties.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/ch04 python3 tools/build_colab.py ch04 --cell properties)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []


def shot(page, sel, path):
    """Element screenshot via page clip (avoids Locator.screenshot stability hang under --disable-gpu)."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); '
        'return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


def shot_svg_box(page, svg_sel, vx, vy, vw, vh, path):
    """High-res (device_scale_factor=2 => z>=2) clip of a sub-region in SVG viewBox coordinates."""
    info = page.eval_on_selector(
        svg_sel,
        's => { const r = s.getBoundingClientRect(), v = s.viewBox.baseVal; '
        'return {x: r.x + scrollX, y: r.y + scrollY, kx: r.width / v.width, ky: r.height / v.height}; }'
    )
    clip = {
        'x': info['x'] + vx * info['kx'],
        'y': info['y'] + vy * info['ky'],
        'width': vw * info['kx'],
        'height': vh * info['ky'],
    }
    page.screenshot(path=str(path), clip=clip, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])

    for scheme in ('light', 'dark'):
        ctx = b.new_context(
            viewport={'width': 1000, 'height': 920},
            device_scale_factor=2,
            color_scheme=scheme,
        )
        page = ctx.new_page()
        page.set_default_timeout(15000)
        page.on('console', lambda m: errors.append(f'[{scheme}] {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'[{scheme}] PAGEERROR {e}'))
        page.goto(PAGE.as_uri(), timeout=15000)
        page.wait_for_timeout(250)

        def clashes():
            return page.locator('[data-clash]').count()

        def outside(svg_sel):
            return page.evaluate(f'''() => {{
                const s = document.querySelector({svg_sel!r}), v = s.viewBox.baseVal;
                return [...s.querySelectorAll('text')].filter(t => {{
                    const b = t.getBBox();
                    return b.x < v.x - 0.5 || b.y < v.y - 0.5 ||
                           b.x + b.width > v.x + v.width + 0.5 ||
                           b.y + b.height > v.y + v.height + 0.5;
                }}).map(t => t.textContent);
            }}''')

        def set_disp(val):
            page.evaluate(f'() => document.querySelector(".k").__sim.setDisp({val})')

        def set_alloy(on):
            page.evaluate(f'() => document.querySelector(".k").__sim.setAlloy({str(bool(on)).lower()})')

        def sim_step(dt):
            return page.evaluate(f'() => document.querySelector(".k").__sim.step({dt})')

        def sim_reset(t=0):
            return page.evaluate(f'() => document.querySelector(".k").__sim.resetTime({t})')

        def sim_pause(paused):
            page.evaluate(f'() => document.querySelector(".k").__sim.setPaused({str(bool(paused)).lower()})')

        if scheme == 'dark':
            print('== dark mode checks & screenshots')
            sim_pause(True)
            set_disp(0.5)
            check('dark tab1 (s=0.5): no label clash', clashes() == 0, str(clashes()))
            check('dark tab1 (s=0.5): labels inside viewBox', not outside('.pr-svg1'), str(outside('.pr-svg1')))
            shot(page, '.k', OUT / 'tab1-s05-dark.png')

            set_disp(1.0)
            check('dark tab1 (s=1.0): no label clash', clashes() == 0, str(clashes()))
            shot(page, '.k', OUT / 'tab1-s10-dark.png')

            page.click('.tabbar button[data-tab="cond"]')
            page.click('.pr-picks button[data-sample="nacl-l"]')
            sim_reset(0.08)
            check('dark tab2 (nacl-l): no label clash', clashes() == 0, str(clashes()))
            check('dark tab2 (nacl-l): labels inside viewBox', not outside('.pr-svg2'), str(outside('.pr-svg2')))
            shot(page, '.k', OUT / 'tab2-nacl-l-dark.png')

            page.click('.pr-picks button[data-sample="iodine"]')
            sim_reset(0.08)
            check('dark tab2 (iodine): no label clash', clashes() == 0, str(clashes()))
            shot(page, '.k', OUT / 'tab2-iodine-dark.png')
            ctx.close()
            continue

        print('== Tab 1: malleable vs brittle (light)')
        check('tab 1 active by default', 'on' in page.get_attribute('.tabbar button[data-tab="force"]', 'class'))

        # 1. Live rAF electron motion check + pause button check
        e_pos_0 = page.eval_on_selector_all('.pr-svg1 [data-role="metal-e"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])')
        page.wait_for_timeout(160)
        e_pos_1 = page.eval_on_selector_all('.pr-svg1 [data-role="metal-e"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])')
        moved_live = sum(1 for a, c in zip(e_pos_0, e_pos_1) if abs(a[0] - c[0]) + abs(a[1] - c[1]) > 0.05)
        check('tab1: metal delocalised electrons animate in live rAF', moved_live >= 12, f'moved={moved_live}/{len(e_pos_0)}')

        # Pause button stops animation; clicking again resumes
        page.click('.pr-pause')
        check('pause button sets paused state', page.evaluate('() => document.querySelector(".k").__sim.isPaused()'))
        t_p0 = page.evaluate('() => document.querySelector(".k").__sim.time()')
        page.wait_for_timeout(150)
        t_p1 = page.evaluate('() => document.querySelector(".k").__sim.time()')
        check('paused animation does not advance time', abs(t_p1 - t_p0) < 1e-6, f'{t_p0} -> {t_p1}')

        # Multi-frame deterministic sampling via __sim.step()
        frames = []
        for _ in range(4):
            sim_step(0.14)
            frames.append(page.eval_on_selector_all('.pr-svg1 [data-role="metal-e"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])'))
        all_e_moved = all(
            max(abs(frames[f][i][0] - frames[0][i][0]) + abs(frames[f][i][1] - frames[0][i][1]) for f in range(1, 4)) > 0.6
            for i in range(len(frames[0]))
        )
        check('tab1: every delocalised electron moves across sampled frames', all_e_moved)
        check('tab1: delocalised electrons do not overlap metal ions',
              page.evaluate('''() => {
                  const ions = [...document.querySelectorAll('.pr-svg1 [data-role="metal-ion"]')].map(c => ({
                      x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r')
                  }));
                  const es = [...document.querySelectorAll('.pr-svg1 [data-role="metal-e"]')].map(c => ({
                      x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r')
                  }));
                  return es.every(e => ions.every(ion => Math.hypot(e.x - ion.x, e.y - ion.y) > ion.r + e.r + 1.0));
              }'''))

        # 2. Slider = 0
        set_disp(0)
        sim_reset(0.1)
        cap_m0 = page.inner_text('.pr-cap-metal')
        cap_i0 = page.inner_text('.pr-cap-ionic')
        check('s=0: no repulsion arrows', page.locator('.pr-svg1 [data-role="repulsion-arrow"]').count() == 0)
        check('s=0: no cleavage crack', page.locator('.pr-svg1 [data-role="cleavage-crack"]').count() == 0)
        check('s=0: metal caption states malleable / ductile & bonds re-form',
              'layers slide' in cap_m0 and 'metallic bonds 在新位置立即重新形成' in cap_m0 and 'malleable / ductile' in cap_m0, cap_m0)
        check('s=0: Na+ smaller than Cl- in ionic lattice',
              page.evaluate('''() => {
                  const posR = +document.querySelector('.pr-svg1 [data-role="ionic-ion"][data-charge="pos"]').getAttribute('r');
                  const negR = +document.querySelector('.pr-svg1 [data-role="ionic-ion"][data-charge="neg"]').getAttribute('r');
                  return posR < negR * 0.8;
              }'''))
        check('s=0: no label clash', clashes() == 0, str(clashes()))
        check('s=0: labels inside viewBox', not outside('.pr-svg1'), str(outside('.pr-svg1')))
        shot(page, '.k', OUT / 'tab1-s0-light.png')

        base_metal_upper_x = page.eval_on_selector('.pr-svg1 [data-role="metal-ion"][data-layer="upper"]', 'e => +e.getAttribute("cx")')

        # 3. Threshold s = 0.35 vs s = 0.40 vs s = 0.50
        set_disp(0.35)
        check('s=0.35 (< 0.4): no repulsion arrows yet', page.locator('.pr-svg1 [data-role="repulsion-arrow"]').count() == 0)
        set_disp(0.40)
        check('s=0.40 (>= 0.4): repulsion arrows appear', page.locator('.pr-svg1 [data-role="repulsion-arrow"]').count() == 3)

        set_disp(0.50)
        sim_reset(0.2)
        cap_m05 = page.inner_text('.pr-cap-metal')
        cap_i05 = page.inner_text('.pr-cap-ionic')
        check('s=0.50: 3 red repulsion double-arrows visible', page.locator('.pr-svg1 [data-role="repulsion-arrow"]').count() == 3)
        check('s=0.50: like charges vertically aligned across slip plane',
              page.evaluate('''() => {
                  const up = [...document.querySelectorAll('.pr-svg1 [data-role="ionic-ion"][data-layer="upper"]')].slice(4, 7);
                  const lo = [...document.querySelectorAll('.pr-svg1 [data-role="ionic-ion"][data-layer="lower"]')].slice(1, 4);
                  return up.every((u, i) => u.getAttribute('data-charge') === lo[i].getAttribute('data-charge') &&
                                            Math.abs(+u.getAttribute('cx') - +lo[i].getAttribute('cx')) < 1.0);
              }'''))
        check('s=0.50: ionic caption mentions like charges repel', 'like charges repel' in cap_i05, cap_i05)
        check('s=0.50: metal remains malleable', 'malleable / ductile' in cap_m05, cap_m05)
        check('s=0.50: no label clash', clashes() == 0, str(clashes()))
        check('s=0.50: labels inside viewBox', not outside('.pr-svg1'), str(outside('.pr-svg1')))
        shot(page, '.k', OUT / 'tab1-s05-repel-light.png')
        shot_svg_box(page, '.pr-svg1', 392, 8, 384, 372, OUT / 'zoom-ionic-repel.png')

        # 4. Slider = 1.0 (pure metal vs shattered ionic)
        set_disp(1.0)
        sim_reset(0.3)
        cap_m1 = page.inner_text('.pr-cap-metal')
        cap_i1 = page.inner_text('.pr-cap-ionic')
        pure_shift = page.eval_on_selector('.pr-svg1 [data-role="metal-ion"][data-layer="upper"]', 'e => +e.getAttribute("cx")') - base_metal_upper_x
        check('s=1.0: cleavage crack visible (brittle)', page.locator('.pr-svg1 [data-role="cleavage-crack"]').count() == 1)
        check('s=1.0: repulsion arrows still shown across fracture', page.locator('.pr-svg1 [data-role="repulsion-arrow"]').count() == 3)
        check('s=1.0: ionic caption has full brittle causal chain',
              'like charges repel' in cap_i1 and 'lattice shatters' in cap_i1 and 'brittle' in cap_i1, cap_i1)
        check('s=1.0: metal constantly malleable & slid full spacing (~54 px)',
              'malleable / ductile' in cap_m1 and abs(pure_shift - 54.0) < 1.0, f'shift={pure_shift}')
        check('s=1.0: no label clash', clashes() == 0, str(clashes()))
        check('s=1.0: labels inside viewBox', not outside('.pr-svg1'), str(outside('.pr-svg1')))
        shot(page, '.k', OUT / 'tab1-s10-brittle-light.png')
        shot_svg_box(page, '.pr-svg1', 392, 8, 384, 372, OUT / 'zoom-ionic-shatter.png')

        # 5. Alloy (brass: larger Zn atoms)
        set_disp(0)
        set_alloy(True)
        alloy_base_x = page.eval_on_selector('.pr-svg1 [data-role="metal-ion"][data-layer="upper"]', 'e => +e.getAttribute("cx")')
        set_disp(1.0)
        sim_reset(0.25)
        alloy_shift = page.eval_on_selector('.pr-svg1 [data-role="metal-ion"][data-layer="upper"]', 'e => +e.getAttribute("cx")') - alloy_base_x
        cap_al = page.inner_text('.pr-cap-metal')
        check('alloy: larger Zn atoms drawn (r_Zn > r_Cu)',
              page.evaluate('''() => {
                  const zn = +document.querySelector('.pr-svg1 [data-kind="zn"]').getAttribute('r');
                  const cu = +document.querySelector('.pr-svg1 [data-kind="cu"]').getAttribute('r');
                  return zn > cu * 1.25;
              }'''))
        check('alloy: maximum upper-layer displacement is much smaller than pure metal',
              0 < alloy_shift < pure_shift * 0.4, f'alloy_shift={alloy_shift:.1f} vs pure_shift={pure_shift:.1f}')
        check('alloy: caption explains larger Zn disrupts regular layers -> harder / stronger',
              'Zn atoms 比 Cu 大' in cap_al and '打乱 layers 的规则排列' in cap_al and 'layers 不容易 slide' in cap_al and 'hard / strong' in cap_al,
              cap_al)
        check('alloy: no label clash', clashes() == 0, str(clashes()))
        check('alloy: labels inside viewBox', not outside('.pr-svg1'), str(outside('.pr-svg1')))
        check('alloy: delocalised electrons do not overlap Cu or larger Zn ions',
              page.evaluate('''() => {
                  const ions = [...document.querySelectorAll('.pr-svg1 [data-role="metal-ion"]')].map(c => ({
                      x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r')
                  }));
                  const es = [...document.querySelectorAll('.pr-svg1 [data-role="metal-e"]')].map(c => ({
                      x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r')
                  }));
                  return es.every(e => ions.every(ion => Math.hypot(e.x - ion.x, e.y - ion.y) > ion.r + e.r + 1.0));
              }'''))
        shot(page, '.k', OUT / 'tab1-alloy-light.png')
        shot_svg_box(page, '.pr-svg1', 8, 8, 382, 372, OUT / 'zoom-metal-alloy.png')
        set_alloy(False)
        set_disp(0.5)

        print('== Tab 2: electrical conductivity across 7 samples (light)')
        page.click('.tabbar button[data-tab="cond"]')
        check('tab 2 becomes active', 'on' in page.get_attribute('.tabbar button[data-tab="cond"]', 'class'))

        anode_x = page.eval_on_selector('.pr-svg2 [data-electrode="anode"]', 'e => +e.getAttribute("x") + +e.getAttribute("width")/2')
        cathode_x = page.eval_on_selector('.pr-svg2 [data-electrode="cathode"]', 'e => +e.getAttribute("x") + +e.getAttribute("width")/2')
        check('anode (+) on left, cathode (-) on right', anode_x < cathode_x, f'{anode_x} vs {cathode_x}')
        svg2_txt = page.text_content('.pr-svg2')
        check('circuit labels anode (+) and cathode (-)', 'anode (+)' in svg2_txt and 'cathode (−)' in svg2_txt, svg2_txt)

        expected_samples = [
            ('cu', True, ['delocalised electrons move (through the structure)'], 'e-left'),
            ('nacl-s', False, ['ions', 'vibrate'], 'vibrate-ions'),
            ('nacl-l', True, ['ions move (through the liquid)', 'electrons move', '9701/21 May/June 2025 Q1(a)(iii)'], 'ions-split'),
            ('nacl-aq', True, ['ions move', 'cathode', 'anode'], 'ions-split'),
            ('graphite', True, ['delocalised electrons move through / between the layers'], 'e-left'),
            ('diamond', False, ['no delocalised electrons', 'all (4) outer electrons are used in bonding'], 'static-cov'),
            ('iodine', False, ['no mobile charged particles', 'molecules are neutral'], 'vibrate-i2'),
        ]

        for sid, lamp_on, phrases, mode in expected_samples:
            page.click(f'.pr-picks button[data-sample="{sid}"]')
            sim_reset(0.05)
            bulb_attr = page.get_attribute('.pr-svg2 .pr-bulb', 'data-on')
            rays_n = page.locator('.pr-svg2 [data-role="lamp-rays"] line').count()
            svg_t = page.text_content('.pr-svg2')
            cap_t = page.inner_text('.pr-cap-cond')

            check(f'{sid}: lamp state is {"ON" if lamp_on else "OFF"}',
                  bulb_attr == ('true' if lamp_on else 'false') and
                  (rays_n >= 4 if lamp_on else rays_n == 0) and
                  (('lamp: ON' in svg_t) if lamp_on else ('lamp: OFF' in svg_t)),
                  f'attr={bulb_attr}, rays={rays_n}')

            for ph in phrases:
                check(f'{sid}: caption includes {ph!r}', ph in cap_t, cap_t)

            # Sample carrier positions at t=0.05 vs t=0.25 (0.20s step, zero wrap-around)
            if mode == 'e-left':
                x0 = page.eval_on_selector_all('.pr-svg2 [data-carrier="e"]', 'es => es.map(e => +e.getAttribute("cx"))')
                fixed_role = 'cu-ion' if sid == 'cu' else 'c-atom'
                f0 = page.eval_on_selector_all(f'.pr-svg2 [data-role="{fixed_role}"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])')
                sim_step(0.20)
                x1 = page.eval_on_selector_all('.pr-svg2 [data-carrier="e"]', 'es => es.map(e => +e.getAttribute("cx"))')
                f1 = page.eval_on_selector_all(f'.pr-svg2 [data-role="{fixed_role}"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])')
                check(f'{sid}: electrons drift towards anode (+, left)',
                      len(x0) >= 8 and all(b < a - 4.0 for a, b in zip(x0, x1)), f'{x0[:3]} -> {x1[:3]}')
                check(f'{sid}: lattice {fixed_role}s remain stationary', f0 == f1)
            elif mode == 'ions-split':
                cat0 = page.eval_on_selector_all('.pr-svg2 [data-carrier="cation"]', 'es => es.map(e => +e.getAttribute("cx"))')
                ani0 = page.eval_on_selector_all('.pr-svg2 [data-carrier="anion"]', 'es => es.map(e => +e.getAttribute("cx"))')
                sim_step(0.20)
                cat1 = page.eval_on_selector_all('.pr-svg2 [data-carrier="cation"]', 'es => es.map(e => +e.getAttribute("cx"))')
                ani1 = page.eval_on_selector_all('.pr-svg2 [data-carrier="anion"]', 'es => es.map(e => +e.getAttribute("cx"))')
                check(f'{sid}: Na+ cations move towards cathode (-, right)',
                      len(cat0) >= 6 and all(b > a + 4.0 for a, b in zip(cat0, cat1)), f'{cat0[:3]} -> {cat1[:3]}')
                check(f'{sid}: Cl- anions move towards anode (+, left)',
                      len(ani0) >= 6 and all(b < a - 4.0 for a, b in zip(ani0, ani1)), f'{ani0[:3]} -> {ani1[:3]}')
            elif mode == 'vibrate-ions':
                p0 = page.eval_on_selector_all('.pr-svg2 [data-mode="vibrate"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])')
                sim_step(0.09)
                p1 = page.eval_on_selector_all('.pr-svg2 [data-mode="vibrate"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])')
                sim_step(0.50)
                p2 = page.eval_on_selector_all('.pr-svg2 [data-mode="vibrate"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])')
                d01 = [abs(a[0] - c[0]) + abs(a[1] - c[1]) for a, c in zip(p0, p1)]
                d02 = [abs(a[0] - c[0]) + abs(a[1] - c[1]) for a, c in zip(p0, p2)]
                check('nacl-s: ions vibrate locally without drifting out of lattice sites',
                      max(d01) > 0.3 and max(d01) < 9.0 and max(d02) < 9.0, f'max_d={max(d01):.2f}, {max(d02):.2f}')
            elif mode == 'static-cov':
                check('diamond: 0 mobile charge carriers', page.locator('.pr-svg2 [data-carrier]').count() == 0)
                check('diamond: British spelling localised in SVG summary', 'localised' in svg_t and 'localized' not in svg_t, svg_t)
            elif mode == 'vibrate-i2':
                check('iodine: 0 mobile charged carriers', page.locator('.pr-svg2 [data-carrier]').count() == 0)
                i0 = page.eval_on_selector_all('.pr-svg2 [data-role="i2-atom"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])')
                sim_step(0.11)
                i1 = page.eval_on_selector_all('.pr-svg2 [data-role="i2-atom"]', 'es => es.map(e => [+e.getAttribute("cx"), +e.getAttribute("cy")])')
                di = [abs(a[0] - c[0]) + abs(a[1] - c[1]) for a, c in zip(i0, i1)]
                check('iodine: neutral I2 molecules vibrate locally only', max(di) > 0.2 and max(di) < 8.0)

            check(f'{sid}: no label clash', clashes() == 0, str(clashes()))
            check(f'{sid}: labels inside viewBox', not outside('.pr-svg2'), str(outside('.pr-svg2')))
            shot(page, '.k', OUT / f'tab2-{sid}-light.png')

            if sid == 'nacl-l':
                shot_svg_box(page, '.pr-svg2', 235, 6, 420, 100, OUT / 'zoom-circuit-bulb-on.png')
                shot_svg_box(page, '.pr-svg2', 64, 110, 652, 238, OUT / 'zoom-electrodes-molten.png')

        print('== Narrow viewport (720 px) on both tabs')
        page.set_viewport_size({'width': 720, 'height': 1100})
        page.wait_for_timeout(150)

        page.click('.pr-picks button[data-sample="nacl-l"]')
        sim_reset(0.12)
        ov2 = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        fs2 = page.evaluate('''() => {
            const s = document.querySelector('.pr-svg2'), k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k));
        }''')
        check('720 px tab2: no horizontal overflow', ov2 <= 0, str(ov2))
        check('720 px tab2: SVG text >= 12 px on screen', fs2 >= 12.0, f'{fs2:.2f}')
        shot(page, '.k', OUT / 'tab2-720.png')

        page.click('.tabbar button[data-tab="force"]')
        set_disp(0.5)
        sim_reset(0.15)
        ov1 = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        fs1 = page.evaluate('''() => {
            const s = document.querySelector('.pr-svg1'), k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k));
        }''')
        check('720 px tab1: no horizontal overflow', ov1 <= 0, str(ov1))
        check('720 px tab1: SVG text >= 12 px on screen', fs1 >= 12.0, f'{fs1:.2f}')
        shot(page, '.k', OUT / 'tab1-720.png')

        print('== IntersectionObserver off-screen pause & resume')
        page.set_viewport_size({'width': 1000, 'height': 800})
        sim_pause(False)  # resume live rAF
        page.wait_for_timeout(150)
        check('IO: running when visible in viewport',
              page.evaluate('() => document.querySelector(".k").__sim.isVisible() && document.querySelector(".k").__sim.isRunning()'))

        # Push .k completely below the 800 px viewport and scroll to top
        page.evaluate('''() => {
            const sp = document.createElement('div');
            sp.id = 'io-spacer';
            sp.style.height = '3200px';
            document.body.insertBefore(sp, document.body.firstChild);
            window.scrollTo(0, 0);
        }''')
        page.wait_for_timeout(180)
        io_vis_off = page.evaluate('() => document.querySelector(".k").__sim.isVisible()')
        t_off_0 = page.evaluate('() => document.querySelector(".k").__sim.time()')
        page.wait_for_timeout(200)
        t_off_1 = page.evaluate('() => document.querySelector(".k").__sim.time()')
        check('IO: pauses rAF when scrolled out of viewport',
              (not io_vis_off) and abs(t_off_1 - t_off_0) < 1e-6, f'vis={io_vis_off}, {t_off_0}->{t_off_1}')

        # Remove spacer -> .k returns into viewport -> automatically resumes
        page.evaluate('() => { document.getElementById("io-spacer").remove(); window.scrollTo(0, 0); }')
        page.wait_for_timeout(220)
        io_vis_on = page.evaluate('() => document.querySelector(".k").__sim.isVisible()')
        t_on = page.evaluate('() => document.querySelector(".k").__sim.time()')
        check('IO: resumes rAF when scrolled back into viewport',
              io_vis_on and t_on > t_off_1 + 0.04, f'vis={io_vis_on}, {t_off_1}->{t_on}')

        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
