"""ch14 br2-pi3d cell test (3D): Br₂ comes down onto the π cloud of ethene and picks up an induced dipole.

Checks: 3D ready (light / dark), far = non-polar (plain "Br" labels, no arrow, symmetric clouds, bonding pair in
the middle), the slider changes d and the canvas, polarisation grows monotonically as d falls, near Br = δ+ and
far Br = δ− (labels sit by the right atoms, clouds shrink / grow, bonding pair shifts to the far Br, dipole arrow
on), readout card text per stage, 靠近极化 animation (frames differ, d falls to 2.2 Å, pause), 复位远离, drag /
复位视角 / 自动旋转, stage labels never cover an atom / cloud / lobe / HUD at any d or rotation, no [data-clash],
fonts ≥ 12 px, 720 px layout, fallback SVG (CDN blocked) follows the slider, console 0 error.

usage (both arguments optional; the preview is rebuilt when they are omitted):
  uv run --with playwright python -I colab/tests/ch14_br2-pi3d.py [preview.html] [shots-dir]
"""
import os
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
TMP = Path(os.environ.get('COLAB_TMP', '/tmp/colab'))
if len(sys.argv) > 1:
    PAGE = Path(sys.argv[1]).resolve()
else:
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_colab.py'), 'ch14', '--cell', 'br2-pi3d', '--3d'],
                   check=True, cwd=ROOT, env={**os.environ, 'COLAB_TMP': str(TMP)}, stdout=subprocess.DEVNULL)
    PAGE = TMP / 'cells' / 'ch14-br2-pi3d.html'
OUT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else TMP / 'shots' / 'br2-pi3d'
OUT.mkdir(parents=True, exist_ok=True)

CHROMIUM = '/usr/bin/chromium'
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']

results, errors = [], []


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def shot(page, sel, path):
    bb = page.eval_on_selector(
        sel, 'e => { const r = e.getBoundingClientRect(); '
             'return {x: Math.max(0, r.x + scrollX), y: Math.max(0, r.y + scrollY), width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def shot_clip(page, sel, fx0, fy0, fx1, fy1, path):
    bb = page.eval_on_selector(
        sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height}; }')
    page.screenshot(path=str(path), full_page=True, clip={
        'x': bb['x'] + bb['w'] * fx0, 'y': bb['y'] + bb['h'] * fy0,
        'width': bb['w'] * (fx1 - fx0), 'height': bb['h'] * (fy1 - fy0)})


def ev(page, js, *a):
    return page.evaluate(js, *a)


def chash(page):
    return ev(page, """() => { const c = document.querySelector('.stage canvas'); if (!c) return null;
                        const u = c.toDataURL(); return u.length + ':' + u.slice(-400); }""")


def set_d(page, d):
    """drive the real slider: value = (8.0 − d) × 10"""
    v = round((8.0 - d) * 10)
    ev(page, """v => { const r = document.querySelector('.bp-r'); r.value = v;
                r.dispatchEvent(new Event('input', {bubbles: true})); }""", v)
    page.wait_for_timeout(60)


def layout(page):
    return ev(page, "() => document.querySelector('.k').__bp.layout()")


def lab(L, q):
    return next(x for x in L['labels'] if x['q'] == q)


LAYOUT_BAD_JS = """() => {
  const L = document.querySelector('.k').__bp.layout(), bad = [];
  const rc = (r, c, m) => {
    const dx = Math.max(r.x - c.x, 0, c.x - (r.x + r.w)), dy = Math.max(r.y - c.y, 0, c.y - (r.y + r.h));
    return Math.hypot(dx, dy) < c.r - m;
  };
  L.labels.forEach(l => {
    L.circles.forEach(c => { if (rc(l, c, 0.5)) bad.push('"' + l.text + '" covers ' + c.kind + (c.el || '')); });
    if (l.y < L.hud.y + L.hud.h) bad.push('"' + l.text + '" under HUD');
    if (l.x < 0 || l.y < 0 || l.x + l.w > L.W + 0.5 || l.y + l.h > L.H + 0.5) bad.push('"' + l.text + '" outside stage');
  });
  L.labels.forEach((a, i) => L.labels.forEach((b, j) => {
    if (j > i && a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) bad.push('"' + a.text + '" overlaps "' + b.text + '"');
  }));
  L.circles.forEach(c => {
    if (c.kind === 'lobe' || c.kind === 'arrow') return;
    if (c.x - c.r < 0 || c.x + c.r > L.W || c.y - c.r < L.hud.y + L.hud.h || c.y + c.r > L.H) bad.push(c.kind + (c.el || '') + ' outside band');
  });
  return bad;
}"""

SMALL_JS = """() => {
  const out = [];
  for (const e of document.querySelectorAll('.k *')) {
    const st = getComputedStyle(e);
    if (st.display === 'none' || st.visibility === 'hidden' || !e.getClientRects().length || e.closest('svg')) continue;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own && parseFloat(st.fontSize) < 12) out.push(e.tagName + '.' + e.className + ':' + e.textContent.trim().slice(0, 24) + ' ' + st.fontSize);
  }
  return out;
}"""

SVG_JS = """() => {
  const out = [];
  for (const s of document.querySelectorAll('.k svg')) {
    const v = s.viewBox.baseVal, w = s.getBoundingClientRect().width;
    if (!v || !v.width || !w) continue;
    for (const t of s.querySelectorAll('text')) {
      const f = parseFloat(getComputedStyle(t).fontSize) * w / v.width, b = t.getBBox();
      if (f < 12) out.push('small ' + t.textContent + ':' + f.toFixed(1));
      if (b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5) out.push('outside ' + t.textContent);
    }
  }
  return out;
}"""

CLASH_JS = "() => [...document.querySelectorAll('.k [data-clash]')].map(e => e.textContent)"


def sweep_layout(page, ds, tag):
    bad = []
    for d in ds:
        set_d(page, d)
        lb = ev(page, LAYOUT_BAD_JS) + [f'clash {c}' for c in ev(page, CLASH_JS)]
        if lb:
            bad.append(f'{tag} d={d}: {lb[:3]}')
    return bad


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=ARGS)

    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1400}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, sc=scheme: errors.append(f'{sc}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, sc=scheme: errors.append(f'{sc}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.k[data-3d=ready]', timeout=40000)
        page.wait_for_timeout(500)
        sfx = '' if scheme == 'light' else '-dark'
        print(f'== {scheme}: start (far)')
        L = layout(page)
        st = page.inner_text('.bp-st')
        check(f'{scheme}: starts at d = 7.5 Å, non-polar: plain "Br" labels, no dipole arrow, equal clouds, pair centred',
              page.get_attribute('.k', 'data-d') == '7.5' and page.get_attribute('.k', 'data-pol') == 'none'
              and lab(L, 'p')['text'] == 'Br' and lab(L, 'n')['text'] == 'Br' and not L['arrow']
              and abs(L['clouds'][0] - L['clouds'][1]) < 0.02 and abs(L['pairY'] - 1.14) < 0.02 and 'non-polar' in st,
              f"{L['clouds']} {L['pairY']} {st}")
        shot(page, '.k', OUT / f'01-far{sfx}.png')

        if scheme == 'light':
            print('== polarisation model')
            ps = ev(page, "() => [8.0,7.5,6,5,4,3,2.5,2.2].map(d => document.querySelector('.k').__bp.pol(d))")
            check('δ grows monotonically as d falls: 0 at 8.0 Å → 1 at 2.2 Å',
                  all(ps[i] < ps[i + 1] for i in range(len(ps) - 1)) and ps[0] == 0 and abs(ps[-1] - 1) < 1e-9, str(ps))

        print(f'== {scheme}: slider → close')
        h0 = chash(page)
        set_d(page, 2.5)
        page.wait_for_timeout(150)
        h1 = chash(page)
        L = layout(page)
        qp, qn = lab(L, 'p'), lab(L, 'n')
        check(f'{scheme}: slider to 2.5 Å changes the canvas and d readout', h1 != h0 and page.get_attribute('.k', 'data-d') == '2.5'
              and page.inner_text('.bp-d') == '2.5' and 'd = 2.5 Å' in page.inner_text('.bp-dv'))
        check(f'{scheme}: close → labels Brδ+ / Brδ− visible (opacity ≥ 0.9), coloured, dipole arrow on',
              qp['text'] == 'Brδ+' and qn['text'] == 'Brδ−' and qp['op'] >= 0.9 and qn['op'] >= 0.9
              and 'bp-pos' in qp['cls'] and 'bp-neg' in qn['cls'] and L['arrow'], f'{qp} {qn}')
        near = next(c for c in L['circles'] if c['kind'] == 'atom' and c.get('near'))
        far = next(c for c in L['circles'] if c['kind'] == 'atom' and c['el'] == 'Br' and not c.get('near'))
        cc = [c for c in L['circles'] if c['kind'] == 'atom' and c['el'] == 'C']
        mid_y = sum(c['y'] for c in cc) / 2

        def dist(l, c):
            return ((l['x'] + l['w'] / 2 - c['x']) ** 2 + (l['y'] + l['h'] / 2 - c['y']) ** 2) ** 0.5
        check(f'{scheme}: δ+ is on the Br nearer the C=C, δ− on the far Br (labels beside the right atoms)',
              abs(near['y'] - mid_y) < abs(far['y'] - mid_y) and dist(qp, near) < dist(qp, far) and dist(qn, far) < dist(qn, near)
              and dist(qp, near) < 90 and dist(qn, far) < 90, f'{dist(qp, near):.0f} {dist(qn, far):.0f}')
        check(f'{scheme}: near cloud shrinks, far cloud grows, bonding pair pushed to the far Br',
              L['clouds'][0] < 0.65 and L['clouds'][1] > 0.9 and L['pairY'] > 1.6, f"{L['clouds']} {L['pairY']}")
        st = page.inner_text('.bp-st')
        check(f'{scheme}: card at 2.5 Å: strong, electrophile / electrophilic addition, key sentence present',
              page.get_attribute('.k', 'data-pol') == 'strong' and 'electrophile' in st and 'electrophilic addition' in st
              and 'repels the bonding electrons in Br–Br, inducing a dipole' in page.inner_text('.bp-key'), st)
        shot(page, '.k', OUT / f'02-close{sfx}.png')
        shot(page, '.bp-stage', OUT / f'z-stage-close{sfx}.png')
        shot_clip(page, '.bp-stage', 0.2, 0.25, 0.8, 0.85, OUT / f'z-zoom-close{sfx}.png')

        levels = {}
        for d in (7.0, 5.0, 3.2, 2.2):
            set_d(page, d)
            levels[d] = page.get_attribute('.k', 'data-pol')
        check(f'{scheme}: stages along the way: 7.0 none · 5.0 weak · 3.2 mid · 2.2 strong',
              levels == {7.0: 'none', 5.0: 'weak', 3.2: 'mid', 2.2: 'strong'}, str(levels))
        set_d(page, 3.2)
        page.wait_for_timeout(120)
        shot(page, '.bp-stage', OUT / f'03-mid{sfx}.png')

        print(f'== {scheme}: labels / layout')
        bad = sweep_layout(page, [8.0, 7.5, 6.5, 5.5, 4.5, 3.8, 3.2, 2.8, 2.5, 2.2], 'default view')
        for rx, ry in ((0.6, -1.2), (-0.2, 0.7), (0.9, 2.4)):
            ev(page, "([x, y]) => { const a = document.querySelector('.k').__k3; a.rx = x; a.ry = y; a.view(); }", [rx, ry])
            bad += sweep_layout(page, [7.5, 4.5, 2.2], f'rx={rx} ry={ry}')
        page.click('[data-3d="reset"]')
        page.wait_for_timeout(100)
        check(f'{scheme}: stage labels clear of atoms / clouds / lobes / arrow / HUD / each other, no [data-clash], molecule inside band (all d, 4 views)',
              not bad, '; '.join(bad[:3]))

        print(f'== {scheme}: buttons')
        page.click('.bp-far')
        page.wait_for_timeout(80)
        page.click('.bp-go')
        hs, ds = [], []
        for _ in range(8):
            page.wait_for_timeout(220)
            hs.append(chash(page))
            ds.append(float(page.get_attribute('.k', 'data-d')))
        check(f'{scheme}: 靠近极化 animates: ≥ 5 of 8 frames differ, d keeps falling',
              len(set(hs)) >= 5 and all(ds[i] >= ds[i + 1] for i in range(len(ds) - 1)) and ds[-1] < ds[0] - 1
              and page.get_attribute('.k', 'data-anim') == '1', f'{len(set(hs))} {ds}')
        page.click('.bp-go')
        page.wait_for_timeout(120)
        d0, hp = page.get_attribute('.k', 'data-d'), chash(page)
        page.wait_for_timeout(400)
        check(f'{scheme}: second click pauses (d and picture still)', page.get_attribute('.k', 'data-d') == d0 and chash(page) == hp
              and page.get_attribute('.k', 'data-anim') == '0')
        page.click('.bp-go')
        page.wait_for_function("() => document.querySelector('.k').getAttribute('data-anim') === '0'", timeout=8000)
        check(f'{scheme}: animation ends at 2.2 Å with Brδ+ / Brδ−', page.get_attribute('.k', 'data-d') == '2.2'
              and lab(layout(page), 'p')['text'] == 'Brδ+')
        page.click('.bp-far')
        page.wait_for_timeout(100)
        check(f'{scheme}: 复位远离 → 7.5 Å, labels plain "Br" again', page.get_attribute('.k', 'data-d') == '7.5'
              and lab(layout(page), 'p')['text'] == 'Br' and page.input_value('.bp-r') == '5')

        hb = chash(page)
        box = page.eval_on_selector('.bp-stage canvas', 'e => { const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }')
        cx, cy = box[0] + box[2] / 2, box[1] + box[3] / 2
        page.mouse.move(cx, cy)
        page.mouse.down()
        page.mouse.move(cx + 120, cy + 30, steps=6)
        page.mouse.up()
        page.wait_for_timeout(150)
        L1 = layout(page)
        moved = chash(page) != hb and abs(L1['ry'] - (-0.55)) > 0.5
        page.click('[data-3d="reset"]')
        page.wait_for_timeout(150)
        L2 = layout(page)
        check(f'{scheme}: drag rotates (canvas changes), 复位视角 restores the view', moved and abs(L2['rx'] - 0.3) < 1e-6
              and abs(L2['ry'] + 0.55) < 1e-6 and chash(page) == hb, f"{L1['ry']} {L2['rx']} {L2['ry']}")
        page.click('[data-3d="spin"]')
        sh = []
        for _ in range(4):
            page.wait_for_timeout(250)
            sh.append(chash(page))
        page.click('[data-3d="spin"]')
        lb = ev(page, LAYOUT_BAD_JS)
        check(f'{scheme}: 自动旋转 turns the view (4 frames all differ), labels still clean', len(set(sh)) == 4 and not lb, str(lb[:2]))
        page.click('[data-3d="reset"]')

        check(f'{scheme}: HTML font ≥ 12 px, SVG text ≥ 12 px', not ev(page, SMALL_JS) and not ev(page, SVG_JS),
              str(ev(page, SMALL_JS)[:4]) + str(ev(page, SVG_JS)[:4]))

        if scheme == 'light':
            print('== narrow (720 px)')
            page.set_viewport_size({'width': 720, 'height': 1600})
            page.wait_for_timeout(700)
            ov = ev(page, "() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('720px: no horizontal overflow, fonts ≥ 12 px', ov[0] <= ov[1] + 1 and not ev(page, SMALL_JS), f'{ov} {ev(page, SMALL_JS)[:3]}')
            bad = sweep_layout(page, [7.5, 5.0, 3.5, 2.6, 2.2], '720')
            check('720px: stage labels clean at every d', not bad, '; '.join(bad[:3]))
            set_d(page, 2.6)
            page.wait_for_timeout(150)
            shot(page, '.k', OUT / '60-narrow-720.png')
        ctx.close()

    print('== fallback (CDN blocked)')
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1400}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('pageerror', lambda e, sc=scheme: errors.append(f'fallback-{sc}: PAGEERROR {e}'))
        page.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.fallback.show', timeout=20000)
        page.wait_for_timeout(300)
        sfx = '' if scheme == 'light' else '-dark'
        txt = page.text_content('.bp-fb') or ''
        check(f'{scheme} fallback: stage & 3D buttons hidden, SVG drawn (ethene + π cloud + Br₂, non-polar at 7.5 Å)',
              page.get_attribute('.k', 'data-3d') == 'fallback' and not page.locator('.bp-stage').is_visible()
              and not page.locator('[data-3d="reset"]').is_visible() and 'π 电子云' in txt and 'non-polar' in txt
              and txt.count('Br') == 2 and txt.count('H') == 4, txt)
        shot(page, '.k', OUT / f'70-fallback-far{sfx}.png')
        set_d(page, 3.0)
        page.wait_for_timeout(100)
        txt = page.text_content('.bp-fb') or ''
        check(f'{scheme} fallback: slider redraws SVG with δ+ / δ− and d = 3.0 Å, card follows',
              'δ+' in txt and 'δ−' in txt and 'd = 3.0 Å' in txt and page.inner_text('.bp-d') == '3.0', txt)
        bad = []
        for d in (8.0, 7.5, 6.0, 5.0, 4.0, 3.0, 2.6, 2.2):
            set_d(page, d)
            bad += [f'{d}: clash {c}' for c in ev(page, CLASH_JS)] + [f'{d}: {s}' for s in ev(page, SVG_JS)]
        check(f'{scheme} fallback: no [data-clash], SVG text ≥ 12 px & inside the viewBox at every d', not bad, '; '.join(bad[:4]))
        set_d(page, 3.0)
        page.wait_for_timeout(80)
        shot(page, '.k', OUT / f'71-fallback-close{sfx}.png')
        shot(page, '.bp-fb', OUT / f'z-fallback-svg{sfx}.png')
        page.click('.bp-go')
        page.wait_for_function("() => document.querySelector('.k').getAttribute('data-anim') === '0'", timeout=8000)
        check(f'{scheme} fallback: 靠近极化 still animates to 2.2 Å', page.get_attribute('.k', 'data-d') == '2.2')
        ctx.close()

    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for _, ok, _ in results if ok)
print(f'{passed}/{len(results)} passed')
print(f'shots: {OUT}')
sys.exit(0 if passed == len(results) else 1)
