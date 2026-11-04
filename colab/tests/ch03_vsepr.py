"""ch03 vsepr cell test (3D): VSEPR shapes — syllabus / analogous / crossed-out presets, bp × lp selector,
lone-pair toggle, CH₄ → NH₃ → H₂O compare mode, angle labels clear of atoms, fallback SVG.

usage: uv run --with playwright python -I colab/tests/ch03_vsepr.py <preview.html> <shots-dir>
(build the preview first: python tools/build_colab.py ch03 --cell vsepr --3d)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1])
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


# id: (bp, lp, shape, angle, arrangement, angle labels drawn in 3D) — 3.5 A / 3.5 B tables of the chapter
SYL = {
    'CO2': (2, 0, 'linear', '180°', 'linear', ['180°']),
    'BF3': (3, 0, 'trigonal planar', '120°', 'trigonal planar', ['120°']),
    'CH4': (4, 0, 'tetrahedral', '109.5°', 'tetrahedral', ['109.5°']),
    'NH3': (3, 1, 'pyramidal', '107°', 'tetrahedral', ['107°']),
    'H2O': (2, 2, 'non-linear', '104.5°', 'tetrahedral', ['104.5°']),
    'PF5': (5, 0, 'trigonal bipyramidal', '120° and 90°', 'trigonal bipyramidal', ['120°', '90°']),
    'SF6': (6, 0, 'octahedral', '90°', 'octahedral', ['90°']),
}
ANA = {
    'SO2': (2, 1, 'non-linear (bent)', 'about 118°', 'trigonal planar', ['≈118°']),
    'H2S': (2, 2, 'non-linear', '92.5°', 'tetrahedral', ['92.5°']),
    'NH4': (4, 0, 'tetrahedral', '109.5°', 'tetrahedral', ['109.5°']),
    'H3O': (3, 1, 'pyramidal', '107°', 'tetrahedral', ['107°']),
    'PCl4': (4, 0, 'tetrahedral', '109.5°', 'tetrahedral', ['109.5°']),
    'PCl6': (6, 0, 'octahedral', '90°', 'octahedral', ['90°']),
    'XeF4': (4, 2, 'square planar', '90°', 'octahedral', ['90°']),
}
CROSSED = {
    'SF4': (4, 1, 'see-saw', 'about 117° and 87°', 'trigonal bipyramidal', ['≈117°', '≈87°']),
    'ClF3': (3, 2, 'T-shaped', 'about 87°', 'trigonal bipyramidal', ['≈87°']),
    'XeF2': (2, 3, 'linear', '180°', 'trigonal bipyramidal', ['180°']),
    'BrF5': (5, 1, 'square pyramidal', 'about 85°', 'octahedral', ['≈85°']),
}
ALL = {**SYL, **ANA, **CROSSED}

CANVAS_JS = """() => { const c=document.querySelector('.stage canvas'); if(!c) return null;
  const g=document.createElement('canvas'); g.width=c.width; g.height=c.height; const x=g.getContext('2d'); x.drawImage(c,0,0);
  const d=x.getImageData(0,0,g.width,g.height).data; let s=0,s2=0,n=0;
  for(let i=0;i<d.length;i+=16){const v=d[i]+d[i+1]+d[i+2]; s+=v; s2+=v*v; n++;}
  const m=s/n; const u=c.toDataURL(); return {std:Math.sqrt(s2/n-m*m), hash:u.length+':'+u.slice(-300)}; }"""

# every angle tag must stay clear of every atom disc (incl. its element letter), of the HUD strip, of the canvas
# edges, of the compare-mode captions, and of the other angle tags
LAYOUT_BAD = """() => { const L = document.querySelector('.k').__vs.layout(), bad = [];
  const rc = (r, c) => { const dx=Math.max(r.x-c.x,0,c.x-(r.x+r.w)), dy=Math.max(r.y-c.y,0,c.y-(r.y+r.h)); return Math.hypot(dx,dy) < c.r - 1; };
  const rr = (a, b) => a.x < b.x + b.w - 1 && b.x < a.x + a.w - 1 && a.y < b.y + b.h - 1 && b.y < a.y + a.h - 1;
  L.tags.forEach((t, i) => {
    L.atoms.forEach(a => { if (rc(t, a)) bad.push(t.text + ' on atom ' + a.el); });
    if (t.x < 0 || t.y < L.hud || t.x + t.w > L.W || t.y + t.h > L.H) bad.push(t.text + ' out of canvas');
    L.tags.forEach((u, j) => { if (j > i && rr(t, u)) bad.push(t.text + ' on ' + u.text); });
    L.caps.forEach(c => { if (rr(t, c)) bad.push(t.text + ' on caption'); });
  });
  return bad; }"""

SMALL_JS = '''() => { const out = [];
  for (const e of document.querySelectorAll('.k *')) {
    if (!e.offsetParent && e.tagName !== 'svg') continue;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own && parseFloat(getComputedStyle(e).fontSize) < 12) out.push(e.tagName + '.' + e.className + ':' + e.textContent.slice(0, 20));
  } return out; }'''


def info(page):
    g = lambda s: page.inner_text(f'.vs-info {s}').strip() if page.locator(f'.vs-info {s}').count() else ''
    return {'shape': g('.vs-sh'), 'ang': g('.vs-ang'), 'bp': g('.vs-nbp'), 'lp': g('.vs-nlp'), 'tot': g('.vs-ntot'), 'arr': g('.vs-arr'),
            'why': g('.vs-why'), 'all': page.inner_text('.vs-info')}


def tags(page):
    return [t['text'] for t in page.evaluate("() => document.querySelector('.k').__vs.layout().tags")]


def angles(page):
    return page.evaluate("() => document.querySelector('.k').__vs.angles()")


def stage_clip(page, frac=0.62):
    """central part of the 3D stage, where the molecule and its angle labels are"""
    b = page.locator('.stage').bounding_box()
    w, h = b['width'] * frac, b['height'] * 0.86
    return {'x': b['x'] + (b['width'] - w) / 2, 'y': b['y'] + b['height'] * 0.1, 'width': w, 'height': h}


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=ARGS)   # own instance (another agent runs a browser too)
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.k[data-3d=ready]', timeout=30000); page.wait_for_timeout(300)
        sfx = '' if scheme == 'light' else '-dark'

        def shot(name, sel='.k'):
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        def zoom(name, frac=0.62):
            page.screenshot(path=str(OUT / f'{name}{sfx}.png'), clip=stage_clip(page, frac))

        print(f'== {scheme}: presets')
        check(f'{scheme}: 3D ready', page.get_attribute('.k', 'data-3d') == 'ready')
        i0 = info(page)
        check(f'{scheme}: default CH₄ tetrahedral 109.5°', i0['shape'] == 'tetrahedral' and i0['ang'] == '109.5°', str(i0))
        n = 1
        for pid, (bp, lp, shape, ang, arr, labs) in ALL.items():
            page.click(f'[data-p="{pid}"]'); page.wait_for_timeout(120)
            i = info(page)
            check(f'{scheme} {pid}: shape "{shape}", angle "{ang}"', i['shape'] == shape and i['ang'] == ang, f"{i['shape']} / {i['ang']}")
            if scheme == 'light':
                check(f'{pid}: bp {bp} / lp {lp} / {bp + lp} pairs / {arr}',
                      i['bp'].split('（')[0] == str(bp) and i['lp'] == str(lp) and i['tot'] == str(bp + lp) and i['arr'] == arr, str(i))
                want = (f'{bp} bonding pairs' + (f' and {lp} lone pair' if lp else ', no lone pairs'))
                check(f'{pid}: MS sentence', want in i['why'] and (('lone pairs repel more than bonding pairs' in i['why']) if lp else
                                                                   ('repel equally' in i['why'] and 'as far apart as possible' in i['why'])), i['why'])
                check(f'{pid}: selector shows bp {bp}, lp {lp}',
                      page.locator('[data-bp].on').get_attribute('data-bp') == str(bp) and page.locator('[data-lp].on').get_attribute('data-lp') == str(lp))
                check(f'{pid}: preset button on', page.locator(f'[data-p="{pid}"].on').count() == 1)
                check(f'{pid}: crossed-out note only for SF₄ / ClF₃ / XeF₂ / BrF₅',
                      (page.locator('.vs-cross').count() == 1) == (pid in CROSSED))
                check(f'{pid}: 3D lone-pair lobes = {lp}', page.evaluate("() => document.querySelector('.k').__vs.layout().nLp") == lp)
            t = tags(page)
            check(f'{scheme} {pid}: angle labels {labs}', sorted(t) == sorted(labs), str(t))
            bad = page.evaluate(LAYOUT_BAD)
            check(f'{scheme} {pid}: angle labels clear of atoms / each other / edges', not bad, str(bad))
            shot(f'{n:02d}-{pid}'); n += 1
            if pid in ('CH4', 'NH3', 'H2O', 'PF5', 'SF4', 'XeF4', 'H2S', 'XeF2'):
                zoom(f'z-{pid}')

        if scheme == 'light':
            print('== bond angles measured in the scene')
            for pid, want, tol in [('CH4', 109.47, 0.5), ('NH3', 107, 0.5), ('H2O', 104.5, 0.5), ('H2S', 92.5, 0.3),
                                   ('H3O', 107, 0.5), ('NH4', 109.47, 0.5), ('SO2', 118, 1.0)]:
                page.click(f'[data-p="{pid}"]'); page.wait_for_timeout(80)
                a = angles(page)[0]['angles']
                check(f'{pid}: every X–A–X angle {want}±{tol}° (measured {[round(x, 2) for x in a]})', a and all(abs(x - want) <= tol for x in a))
            page.click('[data-p="PF5"]'); a = sorted(round(x) for x in angles(page)[0]['angles'])
            check('PF₅: 3 × 120°, 6 × 90°, 1 × 180°', a == [90] * 6 + [120] * 3 + [180], str(a))
            page.click('[data-p="SF6"]'); a = sorted(round(x) for x in angles(page)[0]['angles'])
            check('SF₆: 12 × 90°, 3 × 180°', a == [90] * 12 + [180] * 3, str(a))
            page.click('[data-p="XeF4"]'); a = sorted(round(x) for x in angles(page)[0]['angles'])
            check('XeF₄: 4 × 90°, 2 × 180° (square planar)', a == [90] * 4 + [180] * 2, str(a))
            page.click('[data-p="CO2"]'); a = angles(page)[0]['angles']
            check('CO₂: 180°', abs(a[0] - 180) < 0.1, str(a))
            check('CO₂: double bonds drawn (4 rod halves per C=O)',
                  page.evaluate("() => document.querySelector('.k').__vs.mols()[0].children.filter(c => c.geometry && c.geometry.type === 'CylinderGeometry').length") == 8)

            print('== bp × lp selector')
            check('bp = 1 disabled (no shape with one pair)', page.locator('[data-bp="1"]').is_disabled())
            page.click('[data-bp="6"]')
            check('bp 6 → only lp 0 allowed', [page.locator(f'[data-lp="{k}"]').is_disabled() for k in range(4)] == [False, True, True, True])
            check('bp 6 lp 0 → octahedral, generic XY₆', info(page)['shape'] == 'octahedral' and 'XY₆' in info(page)['all'])
            check('generic mode: no preset on', page.locator('[data-p].on').count() == 0)
            page.click('[data-bp="2"]')
            check('bp 2 → lp 0–3 all allowed', not any(page.locator(f'[data-lp="{k}"]').is_disabled() for k in range(4)))
            page.click('[data-lp="3"]')
            check('bp 2 lp 3 → linear (XeF₂ type)', info(page)['shape'] == 'linear' and info(page)['arr'] == 'trigonal bipyramidal')
            page.click('[data-bp="5"]')
            check('bp 5 with lp 3 → lp drops to 1 (square pyramidal)', info(page)['shape'] == 'square pyramidal' and info(page)['lp'] == '1', str(info(page)))
            check('bp 5 → lp 2 / 3 disabled', page.locator('[data-lp="2"]').is_disabled() and page.locator('[data-lp="3"]').is_disabled())
            page.click('[data-bp="4"]'); page.click('[data-lp="2"]')
            check('bp 4 lp 2 → square planar 90°', info(page)['shape'] == 'square planar' and info(page)['ang'] == '90°')
            check('generic: X central, Y terminal atoms', page.evaluate("() => document.querySelector('.k').__vs.angles()[0].el") == 'Y')
            bad = page.evaluate(LAYOUT_BAD); check('generic XY₄E₂: labels clear', not bad, str(bad))
            shot('20-generic-XY4-2lp')
            page.click('[data-bp="3"]'); page.click('[data-lp="0"]')
            check('bp 3 lp 0 → trigonal planar', info(page)['shape'] == 'trigonal planar')
            combos = page.evaluate("() => { const out = []; for (let b = 1; b <= 6; b++) for (let l = 0; l <= 3; l++) if (K3.SHAPES[b + '-' + l]) out.push([b, l]); return out; }")
            bad = []
            for bp, lp in combos:
                page.click(f'[data-bp="{bp}"]'); page.click(f'[data-lp="{lp}"]'); page.wait_for_timeout(60)
                if page.get_attribute('.k', 'data-vs') != f'{bp}-{lp}': bad.append(f'{bp}-{lp} not selected')
                lb = page.evaluate(LAYOUT_BAD)
                if lb: bad.append(f'{bp}-{lp} {lb}')
            check(f'all {len(combos)} bp/lp combos selectable, labels clear', len(combos) == 13 and not bad, '; '.join(bad))

        print(f'== {scheme}: lone pairs on / off')
        page.click('[data-p="H2O"]'); page.wait_for_timeout(100)
        h1 = page.evaluate(CANVAS_JS)
        page.click('.vs-lpt'); page.wait_for_timeout(100)
        L = page.evaluate("() => document.querySelector('.k').__vs.layout()")
        check(f'{scheme}: hide → no lobe visible', L['lpVisible'] is False and L['nLp'] == 2)
        check(f'{scheme}: hide → canvas changes', page.evaluate(CANVAS_JS)['hash'] != h1['hash'])
        check(f'{scheme}: hide → button says 显示 lone pairs, card says shape only atoms',
              page.inner_text('.vs-lpt') == '显示 lone pairs' and '只看 atoms' in info(page)['all'])
        shot('30-H2O-lp-hidden'); zoom('z-H2O-lp-hidden')
        page.click('[data-p="NH3"]'); page.wait_for_timeout(100)
        check(f'{scheme}: hidden state kept on preset change', page.evaluate("() => document.querySelector('.k').__vs.layout().lpVisible") is False)
        shot('31-NH3-lp-hidden')
        page.click('.vs-lpt'); page.wait_for_timeout(100)
        check(f'{scheme}: show again → lobes visible', page.evaluate("() => document.querySelector('.k').__vs.layout().lpVisible") is True)

        print(f'== {scheme}: compare CH₄ → NH₃ → H₂O')
        page.click('.vs-cmp'); page.wait_for_timeout(150)
        check(f'{scheme}: compare on', page.get_attribute('.k', 'data-vs') == 'compare' and 'on' in page.get_attribute('.vs-cmp', 'class'))
        t = tags(page)
        check(f'{scheme}: compare labels 109.5° / 107° / 104.5°', t == ['109.5°', '107°', '104.5°'], str(t))
        a = angles(page)
        check(f'{scheme}: compare: three molecules, angles 109.5 / 107 / 104.5 ±0.5',
              len(a) == 3 and all(abs(x - w) <= 0.5 for m, w in zip(a, (109.47, 107, 104.5)) for x in m['angles']), str([[round(x, 1) for x in m['angles']] for m in a]))
        ci = info(page)['all']
        check(f'{scheme}: compare card: table + 2.5° rule', all(s in ci for s in ('109.5°', '107°', '104.5°', '减小约 2.5°', 'lone pairs repel more than bonding pairs')), ci)
        bad = page.evaluate(LAYOUT_BAD); check(f'{scheme}: compare: labels clear', not bad, str(bad))
        shot('40-compare'); zoom('z-compare', 0.98)
        page.click('.vs-lpt'); page.wait_for_timeout(100); shot('41-compare-lp-hidden'); page.click('.vs-lpt')
        h1 = page.evaluate(CANVAS_JS)
        box = page.locator('.stage canvas').bounding_box()
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2); page.mouse.down()
        page.mouse.move(box['x'] + box['width'] / 2 + 120, box['y'] + box['height'] / 2 + 30, steps=6); page.mouse.up(); page.wait_for_timeout(80)
        rot = page.evaluate("() => document.querySelector('.k').__vs.mols().map(m => m.parent.rotation.y.toFixed(3))")
        check(f'{scheme}: compare drag turns each molecule about its own centre', len(set(rot)) == 1 and rot[0] != '-0.500', str(rot))
        check(f'{scheme}: compare drag changes canvas', page.evaluate(CANVAS_JS)['hash'] != h1['hash'])
        page.click('.vs-cmp'); page.wait_for_timeout(100)
        check(f'{scheme}: compare off → back to single molecule', len(angles(page)) == 1 and page.get_attribute('.k', 'data-vs') != 'compare')

        if scheme == 'light':
            print('== 3D interaction')
            page.click('[data-p="SF6"]'); page.wait_for_timeout(100)
            c0 = page.evaluate(CANVAS_JS)
            check('canvas is not a flat colour', c0['std'] > 8, str(c0['std']))
            box = page.locator('.stage canvas').bounding_box()
            page.mouse.move(box['x'] + 200, box['y'] + 200); page.mouse.down(); page.mouse.move(box['x'] + 330, box['y'] + 240, steps=8); page.mouse.up()
            page.wait_for_timeout(80)
            c1 = page.evaluate(CANVAS_JS)
            check('drag rotates (canvas hash changes)', c1['hash'] != c0['hash'])
            shot('50-SF6-dragged')
            page.click('[data-3d=reset]'); page.wait_for_timeout(80)
            check('复位视角 restores the preset view', page.evaluate(CANVAS_JS)['hash'] == c0['hash'])
            page.mouse.move(box['x'] + 280, box['y'] + 220); page.mouse.wheel(0, -400); page.wait_for_timeout(120)
            d = page.evaluate("() => document.querySelector('.k').__k3.dist")
            sz = page.evaluate("() => { const t = document.querySelector('.k').__vs.layout().tags[0]; return t.h; }")
            check('wheel zooms in, label keeps its screen size (~27 px)', d < 5.5 and 22 < sz < 33, f'{d} {sz}')
            page.click('[data-3d=reset]')
            page.click('[data-3d=spin]')
            hs = []
            for _ in range(5):
                page.wait_for_timeout(250); hs.append(page.evaluate(CANVAS_JS)['hash'])
            check('自动旋转: 5 frames over ~1.2 s all different', len(set(hs)) == 5, str(len(set(hs))))
            page.click('[data-3d=spin]'); page.wait_for_timeout(100)
            h = page.evaluate(CANVAS_JS)['hash']; page.wait_for_timeout(300)
            check('spin off → still', page.evaluate(CANVAS_JS)['hash'] == h)
            check('no [data-clash]', page.locator('[data-clash]').count() == 0)
            check('font ≥ 12px (wide)', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
            page.click('[data-p="NH3"]')
            page.locator('.vs-info').screenshot(path=str(OUT / 'z-info-NH3.png'))
            page.locator('.vs-presets').screenshot(path=str(OUT / 'z-presets.png'))
            page.locator('.vs-sel').screenshot(path=str(OUT / 'z-selector.png'))

            print('== narrow (720 px)')
            page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(400)
            k = page.evaluate("() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('narrow: card does not overflow', k[0] <= k[1] + 1, str(k))
            check('narrow: font ≥ 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
            bad = []
            for pid in list(SYL) + ['XeF4', 'SF4', 'BrF5']:
                page.click(f'[data-p="{pid}"]'); page.wait_for_timeout(80)
                lb = page.evaluate(LAYOUT_BAD)
                if lb: bad.append(f'{pid} {lb}')
            check('narrow: angle labels clear for every syllabus shape', not bad, '; '.join(bad))
            page.click('[data-p="PF5"]'); shot('60-narrow-PF5')
            page.click('.vs-cmp'); page.wait_for_timeout(100)
            bad = page.evaluate(LAYOUT_BAD); check('narrow: compare labels clear', not bad, str(bad))
            shot('61-narrow-compare')
        ctx.close()

    print('== fallback (CDN blocked)')
    ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2)
    page = ctx.new_page()
    page.on('pageerror', lambda e: errors.append(f'fallback: PAGEERROR {e}'))
    page.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
    page.goto(PAGE.as_uri())
    page.wait_for_selector('.fallback.show', timeout=20000)
    check('fallback shown, data-3d=fallback', page.get_attribute('.k', 'data-3d') == 'fallback')
    check('fallback: 7 syllabus drawings', page.locator('.vs-fbgrid figure').count() == 7)
    rows = page.locator('.vs-fbtab tbody tr').all_inner_texts()
    check('fallback table: 7 rows with shapes + angles',
          len(rows) == 7 and all(SYL[k][2] in r and SYL[k][3] in r for k, r in zip(SYL, rows)), str(rows))
    page.click('[data-p="H2O"]')
    check('fallback: info card still works', info(page)['shape'] == 'non-linear')
    page.locator('.k').screenshot(path=str(OUT / '70-fallback.png'))
    page.locator('.vs-fbgrid').screenshot(path=str(OUT / 'z-fallback-grid.png'))
    ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
