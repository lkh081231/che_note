"""ch04 gas-box cell test.

usage: uv run --with playwright python -I colab/tests/ch04_gas-box.py $COLAB_TMP/cells/ch04-gas-box.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/ch04 python3 tools/build_colab.py ch04 --cell gas-box)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []


def shot(page, sel, path):
    """element screenshot via a page clip (avoids Locator.screenshot stability hang)"""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); '
        'return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.set_default_timeout(15000)
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri(), timeout=15000)
        page.wait_for_timeout(350)

        def clashes():
            return page.locator('[data-clash]').count()

        def outside():
            return page.evaluate('''() => {
                const s = document.querySelector('.gb-fig'), v = s.viewBox.baseVal;
                return [...s.querySelectorAll('text')].filter(t => {
                    const b = t.getBBox();
                    return b.x < v.x - 0.5 || b.y < v.y - 0.5 ||
                           b.x + b.width > v.x + v.width + 0.5 ||
                           b.y + b.height > v.y + v.height + 0.5;
                }).map(t => t.textContent);
            }''')

        def sim_step(sec):
            return page.evaluate(f'() => document.querySelector(".k").__sim.step({sec})')

        def sim_stats():
            return page.evaluate('() => document.querySelector(".k").__sim.stats()')

        def visible_dots():
            return page.evaluate('''() => [...document.querySelectorAll('.gb-fig .gb-mol')]
                .filter(c => c.style.display !== 'none')
                .map(c => [+c.getAttribute('cx'), +c.getAttribute('cy')])''')

        def flashes_on_walls():
            return page.evaluate('''() => {
                const ch = document.querySelector('.gb-fig .gb-chamber');
                const x0 = +ch.getAttribute('x'), y0 = +ch.getAttribute('y');
                const w = +ch.getAttribute('width'), h = +ch.getAttribute('height');
                const x1 = x0 + w, y1 = y0 + h;
                const dots = [...document.querySelectorAll('.gb-fig .gb-flash-dot')];
                const bad = [];
                for (const d of dots) {
                    const cx = +d.getAttribute('cx'), cy = +d.getAttribute('cy');
                    const wl = d.getAttribute('data-wall');
                    const onLeft = wl === 'left' && Math.abs(cx - x0) <= 0.6 && cy >= y0 - 0.6 && cy <= y1 + 0.6;
                    const onRight = wl === 'right' && Math.abs(cx - x1) <= 0.6 && cy >= y0 - 0.6 && cy <= y1 + 0.6;
                    const onTop = wl === 'top' && Math.abs(cy - y0) <= 0.6 && cx >= x0 - 0.6 && cx <= x1 + 0.6;
                    const onBot = wl === 'bottom' && Math.abs(cy - y1) <= 0.6 && cx >= x0 - 0.6 && cx <= x1 + 0.6;
                    if (!(onLeft || onRight || onTop || onBot)) bad.push({wl, cx, cy, x0, x1, y0, y1});
                }
                const bars = [...document.querySelectorAll('.gb-fig .gb-flash-bar')];
                for (const ln of bars) {
                    const lx1 = +ln.getAttribute('x1'), ly1 = +ln.getAttribute('y1');
                    const lx2 = +ln.getAttribute('x2'), ly2 = +ln.getAttribute('y2');
                    if (lx1 < x0 - 0.6 || lx2 > x1 + 0.6 || ly1 < y0 - 0.6 || ly2 > y1 + 0.6) {
                        bad.push({bar: true, lx1, ly1, lx2, ly2, x0, x1, y0, y1});
                    }
                }
                return {count: dots.length, bad};
            }''')

        def dots_in_bounds():
            return page.evaluate('''() => {
                const ch = document.querySelector('.gb-fig .gb-chamber');
                const x0 = +ch.getAttribute('x'), y0 = +ch.getAttribute('y');
                const w = +ch.getAttribute('width'), h = +ch.getAttribute('height');
                const x1 = x0 + w, y1 = y0 + h;
                const bad = [];
                for (const c of document.querySelectorAll('.gb-fig .gb-mol')) {
                    if (c.style.display === 'none') continue;
                    const cx = +c.getAttribute('cx'), cy = +c.getAttribute('cy'), r = +c.getAttribute('r');
                    if (cx - r < x0 - 0.3 || cx + r > x1 + 0.3 || cy - r < y0 - 0.3 || cy + r > y1 + 0.3) {
                        bad.push({cx, cy, r, x0, x1, y0, y1});
                    }
                }
                for (const ln of document.querySelectorAll('.gb-fig .gb-tail')) {
                    if (ln.style.display === 'none') continue;
                    for (const [px, py] of [[+ln.getAttribute('x1'), +ln.getAttribute('y1')],
                                            [+ln.getAttribute('x2'), +ln.getAttribute('y2')]]) {
                        if (px < x0 - 0.3 || px > x1 + 0.3 || py < y0 - 0.3 || py > y1 + 0.3) {
                            bad.push({tail: true, px, py, x0, x1, y0, y1});
                        }
                    }
                }
                const st = document.querySelector('.k').__sim.stats();
                const ps = document.querySelector('.k').__sim.particles();
                for (const q of ps) {
                    if (q.x < -1e-9 || q.x > st.W + 1e-9 || q.y < -1e-9 || q.y > st.H + 1e-9) {
                        bad.push({phys: true, q, W: st.W, H: st.H});
                    }
                }
                return bad;
            }''')

        def set_slider(sel, val):
            page.eval_on_selector(sel, f'(el) => {{ el.value = "{val}"; el.dispatchEvent(new Event("input", {{bubbles: true}})); }}')

        def ui_pmeas():
            return float(page.inner_text('.gb-stat[data-stat="pmeas"] .gb-st-v'))

        if scheme == 'dark':
            print('== dark theme')
            check('dark: no label clash', clashes() == 0, str(clashes()))
            check('dark: labels inside viewBox', not outside(), str(outside()))
            fw = flashes_on_walls()
            check('dark: flashes visible and strictly on walls', fw['count'] >= 3 and not fw['bad'], str(fw))
            shot(page, '.k', OUT / 'card-dark.png')
            fb = page.eval_on_selector('.gb-fig', 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
            page.screenshot(path=str(OUT / 'zoom-dark-chamber.png'),
                            clip={'x': fb['x'], 'y': fb['y'], 'width': fb['width'] * 0.72, 'height': fb['height']},
                            full_page=True)
            ctx.close()
            continue

        print('== default state & multi-frame animation')
        raw_txt = page.inner_text('.k')
        check('no leaked markdown asterisk in text', '*' not in raw_txt, raw_txt)
        d0 = visible_dots()
        check('default 40 visible molecules', len(d0) == 40, str(len(d0)))
        page.wait_for_timeout(140)
        d1 = visible_dots()
        page.wait_for_timeout(140)
        d2 = visible_dots()
        moved01 = sum(1 for a, c in zip(d0, d1) if abs(a[0] - c[0]) + abs(a[1] - c[1]) > 0.3)
        moved12 = sum(1 for a, c in zip(d1, d2) if abs(a[0] - c[0]) + abs(a[1] - c[1]) > 0.3)
        check('molecules moving across consecutive rAF frames', moved01 >= 35 and moved12 >= 35, f'{moved01}, {moved12}')
        check('all molecules & tails inside chamber bounds (default)', not dots_in_bounds(), str(dots_in_bounds()[:2]))
        fw = flashes_on_walls()
        check('wall flashes present and strictly on walls (default)', fw['count'] >= 3 and not fw['bad'], str(fw))
        check('no label clash (default V=100%)', clashes() == 0, str(clashes()))
        check('labels inside viewBox (default V=100%)', not outside(), str(outside()))

        # Pause right after reset so default screenshots are crisp & deterministic
        page.click('.gb-reset')
        shot(page, '.k', OUT / 'card-default.png')

        # z >= 2 detail zoom crops (device_scale_factor=2 on zoomed sub-regions)
        fb = page.eval_on_selector('.gb-fig', 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width}; }')
        sc = fb['width'] / 740
        for zname, (zx, zy, zw, zh) in {
            'zoom-flashes-left': (0, 0, 360, 296),
            'zoom-piston-right': (370, 0, 370, 296),
        }.items():
            page.screenshot(
                path=str(OUT / f'{zname}.png'),
                clip={'x': fb['x'] + zx * sc, 'y': fb['y'] + zy * sc, 'width': zw * sc, 'height': zh * sc},
                full_page=True
            )
        shot(page, '.gb-stats', OUT / 'zoom-stats.png')
        shot(page, '.gb-cap', OUT / 'zoom-caption.png')

        print('== pause & resume')
        page.click('.gb-pause')
        check('pause button gets .on class and says 继续',
              'on' in (page.get_attribute('.gb-pause', 'class') or '') and '继续' in page.inner_text('.gb-pause'))
        page.wait_for_timeout(60)
        dp0 = visible_dots()
        page.wait_for_timeout(240)
        dp1 = visible_dots()
        max_drift = max(abs(a[0] - c[0]) + abs(a[1] - c[1]) for a, c in zip(dp0, dp1))
        check('paused: zero particle movement over 240 ms', max_drift == 0, str(max_drift))
        page.click('.gb-pause')
        page.wait_for_timeout(160)
        dp2 = visible_dots()
        moved_resume = sum(1 for a, c in zip(dp1, dp2) if abs(a[0] - c[0]) + abs(a[1] - c[1]) > 0.3)
        check('resumed: particles move again', moved_resume >= 35, str(moved_resume))

        print('== quantitative gas laws (via slider UI + fast-forward __sim.step)')
        page.click('.gb-reset')
        page.click('.gb-pause')  # freeze rAF so fast-forward steps are 100% deterministic
        st0 = sim_step(2.5)
        p0, hits0, imp0, pv0 = st0['pMeasured'], st0['hitsPerSec'], st0['avgImpulse'], st0['pV']
        check('baseline measured p near theoretical 100 (88..112)', 88 <= p0 <= 112 and abs(ui_pmeas() - p0) < 0.2, f'p0={p0:.2f}, ui={ui_pmeas()}')
        page.click('.gb-snap')
        check('snapshot banner appears', page.is_visible('.gb-snap-banner'))

        # 1. Boyle's law: V 100% -> 50%
        set_slider('.gb-v', 50)
        check('V readout says 50%', page.inner_text('.gb-v-val') == '50%')
        st_v50 = sim_step(2.5)
        ratio_v = st_v50['pMeasured'] / p0
        check('V halved (100% → 50%): measured p ×1.7–2.3', 1.7 <= ratio_v <= 2.3, f'{ratio_v:.3f} ({p0:.1f} -> {st_v50["pMeasured"]:.1f})')
        check('V halved: UI readout matches & snapshot badge shows ~×2',
              abs(ui_pmeas() - st_v50['pMeasured']) < 0.2 and '×' in page.inner_text('.gb-stat[data-stat="pmeas"] .gb-st-cmp')
              and '单位壁长 ×' in page.inner_text('.gb-stat[data-stat="hits"] .gb-st-cmp'))
        check('V halved: pV stays roughly constant (0.85..1.15 × baseline)',
              0.85 <= st_v50['pV'] / pv0 <= 1.15, f'{pv0:.1f} -> {st_v50["pV"]:.1f}')
        check('V halved: average impulse unchanged (0.88..1.12 × baseline)',
              0.88 <= st_v50['avgImpulse'] / imp0 <= 1.12, f'{imp0:.2f} -> {st_v50["avgImpulse"]:.2f}')
        fw50 = flashes_on_walls()
        check('V=50%: flashes strictly on walls', fw50['count'] >= 3 and not fw50['bad'], str(fw50))
        check('V=50%: no label clash & labels inside viewBox', clashes() == 0 and not outside(), f'{clashes()}, {outside()}')
        shot(page, '.k', OUT / 'card-boyle-v50.png')

        # 2. Temperature: T 300 K -> 600 K
        page.click('.gb-reset')
        page.click('.gb-pause')
        st0 = sim_step(2.5)
        p0, hits0, imp0 = st0['pMeasured'], st0['hitsPerSec'], st0['avgImpulse']
        page.click('.gb-snap')
        set_slider('.gb-t', 600)
        check('T readout says 600 K', page.inner_text('.gb-t-val') == '600 K')
        st_t600 = sim_step(2.5)
        ratio_t = st_t600['pMeasured'] / p0
        check('T 300 → 600 K: measured p ×1.7–2.3', 1.7 <= ratio_t <= 2.3, f'{ratio_t:.3f} ({p0:.1f} -> {st_t600["pMeasured"]:.1f})')
        check('T 300 → 600 K: hits/s increases (~×√2)', 1.22 <= st_t600['hitsPerSec'] / hits0 <= 1.62,
              f'{hits0:.1f} -> {st_t600["hitsPerSec"]:.1f}')
        check('T 300 → 600 K: avg impulse increases (~×√2)', 1.22 <= st_t600['avgImpulse'] / imp0 <= 1.62,
              f'{imp0:.2f} -> {st_t600["avgImpulse"]:.2f}')
        shot(page, '.k', OUT / 'card-temp-t600.png')

        # 3. Amount: N 40 -> 80
        page.click('.gb-reset')
        page.click('.gb-pause')
        st0 = sim_step(2.5)
        p0, hits0, imp0 = st0['pMeasured'], st0['hitsPerSec'], st0['avgImpulse']
        set_slider('.gb-n', 80)
        check('N=80: 80 visible molecules', len(visible_dots()) == 80)
        st_n80 = sim_step(2.5)
        ratio_n = st_n80['pMeasured'] / p0
        check('N doubled (40 → 80): measured p ×≈2 (1.75–2.25)', 1.75 <= ratio_n <= 2.25,
              f'{ratio_n:.3f} ({p0:.1f} -> {st_n80["pMeasured"]:.1f})')
        check('N doubled: hits/s ×≈2 while avg impulse ~unchanged',
              1.75 <= st_n80['hitsPerSec'] / hits0 <= 2.25 and 0.90 <= st_n80['avgImpulse'] / imp0 <= 1.10)

        print('== piston sweep, pointer drag & bounds safety')
        set_slider('.gb-n', 20)
        for v_test in (85, 60, 40):
            set_slider('.gb-v', v_test)
            sim_step(0.15)
            check(f'V={v_test}%: zero particles out of bounds, 0 clashes, inside viewBox',
                  not dots_in_bounds() and clashes() == 0 and not outside(),
                  f'oob={dots_in_bounds()[:1]}, clash={clashes()}, out={outside()}')
        # Now expand N from 20 -> 80 while piston is at minimum V=40%
        set_slider('.gb-n', 80)
        check('N increased 20 → 80 at V=40%: all 80 particles inside compressed chamber',
              len(visible_dots()) == 80 and not dots_in_bounds(), str(dots_in_bounds()[:2]))
        fw40 = flashes_on_walls()
        check('V=40%: flashes strictly on walls', not fw40['bad'], str(fw40))

        # Test direct SVG piston pointer drag from 40% toward ~80%
        pis_box = page.locator('.gb-piston-g').bounding_box()
        svg_box = page.locator('.gb-fig').bounding_box()
        start_x = pis_box['x'] + 12
        start_y = pis_box['y'] + pis_box['height'] / 2
        page.mouse.move(start_x, start_y)
        page.mouse.down()
        page.mouse.move(svg_box['x'] + svg_box['width'] * 0.72, start_y, steps=10)
        page.mouse.up()
        v_after_drag = sim_stats()['V']
        check('dragging SVG piston updates V (> 65%) and keeps particles in bounds',
              v_after_drag > 65 and not dots_in_bounds(), f'V={v_after_drag}')

        # Grab by the handle (grip at xR+70..82) and off the thin rod (above/below it): V follows without a jump
        scale = svg_box['width'] / 740
        for what in ('grip', 'above rod'):
            if what == 'grip':
                bb = page.locator('.gb-pis-grip').bounding_box()
                gx, gy = bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2
            else:
                bb = page.locator('.gb-pis-rod').bounding_box()
                gx, gy = bb['x'] + bb['width'] / 2, bb['y'] - 30 * scale
            v0 = sim_stats()['V']
            hit_cls = page.evaluate('([x, y]) => document.elementFromPoint(x, y).getAttribute("class")', [gx, gy])
            page.mouse.move(gx, gy)
            page.mouse.down()
            page.mouse.move(gx + 2, gy, steps=2)
            v_jump = sim_stats()['V']
            page.mouse.move(gx - 112 * scale, gy, steps=8)
            page.mouse.up()
            v1 = sim_stats()['V']
            check(f'piston hit area covers {what} (class={hit_cls}); grab does not jump, drag −20% follows',
                  hit_cls == 'gb-pis-hit' and abs(v_jump - v0) <= 2 and 16 <= v0 - v1 <= 24,
                  f'V {v0} -> {v_jump} -> {v1}')

        print('== wall-bars checkbox toggle')
        check('per-wall 1 s bars visible by default', page.is_visible('.gb-wallbars'))
        page.uncheck('.gb-tog-bars')
        check('unticking hides per-wall bars', not page.is_visible('.gb-wallbars'))
        page.check('.gb-tog-bars')
        check('ticking restores per-wall bars', page.is_visible('.gb-wallbars'))

        print('== narrow viewport (720 px)')
        page.click('.gb-reset')
        page.click('.gb-pause')
        page.set_viewport_size({'width': 720, 'height': 1300})
        page.wait_for_timeout(200)
        ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('no horizontal overflow at 720 px', ov <= 0, str(ov))
        fs = page.evaluate('''() => {
            const s = document.querySelector('.gb-fig');
            const k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
            return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k));
        }''')
        check('SVG font size (CSS px × rendered / viewBox width) ≥ 12 at 720 px', fs >= 12, f'{fs:.2f}')
        check('no label clash at 720 px', clashes() == 0, str(clashes()))
        shot(page, '.k', OUT / 'card-720.png')
        shot(page, '.gb-wallbars', OUT / 'crop720-wallbars.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
