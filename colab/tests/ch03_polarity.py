"""ch03 polarity cell test (3D): 12 molecules, bond dipoles (longer for larger ΔEN, head at δ−), δ+ / δ− tags, net dipole =
vector sum of the bond dipoles, guess-then-reveal, show-answer switch, toggles, fallback SVG (CO₂ / H₂O).

usage: uv run --with playwright python -I colab/tests/ch03_polarity.py <preview.html> <shots-dir>
(build the preview first: python tools/build_colab.py ch03 --cell polarity --3d)
"""
import sys
import math
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


EN = {'H': 2.1, 'B': 2.0, 'C': 2.5, 'N': 3.0, 'O': 3.5, 'F': 4.0, 'S': 2.5, 'Cl': 3.0}
# id: (polar, shape, number of bond-dipole arrows, δ tags {element: [signs]}) — chapter 3.6 A
MOL = {
    'H2': (False, 'linear', 0, {}),
    'HCl': (True, 'linear', 1, {'H': '+', 'Cl': '−'}),
    'CO2': (False, 'linear', 2, {'C': '+', 'O': '−'}),
    'BF3': (False, 'trigonal planar', 3, {'B': '+', 'F': '−'}),
    'CH4': (False, 'tetrahedral', 0, {}),
    'CCl4': (False, 'tetrahedral', 4, {'C': '+', 'Cl': '−'}),
    'CH3Cl': (True, 'tetrahedral', 1, {'C': '+', 'Cl': '−'}),
    'CHCl3': (True, 'tetrahedral', 3, {'C': '+', 'Cl': '−'}),
    'H2O': (True, 'non-linear', 2, {'O': '−', 'H': '+'}),
    'NH3': (True, 'pyramidal', 3, {'N': '−', 'H': '+'}),
    'SCl2': (True, 'non-linear', 2, {'S': '+', 'Cl': '−'}),
    'SF6': (False, 'octahedral', 6, {'S': '+', 'F': '−'}),
}
# where δ− lies in the conclusion (chapter table: CHCl₃ "δ− 在 Cl 一侧")
CONCL = {'HCl': 'polar（δ− 在 Cl）', 'CH3Cl': 'polar（δ− 在 Cl）', 'CHCl3': 'polar（δ− 在 Cl 一侧）', 'H2O': 'polar（δ− 在 O）',
         'NH3': 'polar（δ− 在 N）', 'SCl2': 'polar（δ− 在 Cl 一侧）'}

CANVAS_JS = """() => { const c=document.querySelector('.stage canvas'); if(!c) return null;
  const g=document.createElement('canvas'); g.width=c.width; g.height=c.height; const x=g.getContext('2d'); x.drawImage(c,0,0);
  const d=x.getImageData(0,0,g.width,g.height).data; let s=0,s2=0,n=0;
  for(let i=0;i<d.length;i+=16){const v=d[i]+d[i+1]+d[i+2]; s+=v; s2+=v*v; n++;}
  const m=s/n; const u=c.toDataURL(); return {std:Math.sqrt(s2/n-m*m), hash:u.length+':'+u.slice(-300)}; }"""

# every visible δ tag must stay clear of every atom disc, of the other δ tags, of the HUD and of the canvas edges
LAYOUT_BAD = """() => { const L = document.querySelector('.k').__po.layout(), bad = [];
  const rc = (r, c) => { const dx=Math.max(r.x-c.x,0,c.x-(r.x+r.w)), dy=Math.max(r.y-c.y,0,c.y-(r.y+r.h)); return Math.hypot(dx,dy) < c.r - 1; };
  const rr = (a, b) => a.x < b.x + b.w - 1 && b.x < a.x + a.w - 1 && a.y < b.y + b.h - 1 && b.y < a.y + a.h - 1;
  L.dl.forEach((t, i) => {
    L.atoms.forEach(a => { if (rc(t, a)) bad.push(t.text + '@' + t.at + ' on atom ' + a.el + a.i); });
    if (t.x < 0 || t.y < L.hud || t.x + t.w > L.W || t.y + t.h > L.H) bad.push(t.text + '@' + t.at + ' out of canvas');
    L.dl.forEach((u, j) => { if (j > i && rr(t, u)) bad.push(t.text + '@' + t.at + ' on ' + u.text + '@' + u.at); });
    const near = Math.hypot(t.x + t.w / 2 - L.atoms[t.at].x, t.y + t.h / 2 - L.atoms[t.at].y);
    if (near > L.atoms[t.at].r + 75) bad.push(t.text + '@' + t.at + ' far from its atom (' + Math.round(near) + 'px)');
  });
  return bad; }"""

SMALL_JS = '''() => { const out = [];
  for (const e of document.querySelectorAll('.k *')) {
    if (!e.offsetParent && e.tagName !== 'svg') continue;
    if (e.closest('svg')) continue;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own && parseFloat(getComputedStyle(e).fontSize) < 12) out.push(e.tagName + '.' + e.className + ':' + e.textContent.slice(0, 20));
  } return out; }'''

SVG_SMALL_JS = '''() => { const out = [];
  for (const s of document.querySelectorAll('.k svg')) { const vb = s.viewBox.baseVal; if (!vb || !vb.width) continue;
    if (!s.getBoundingClientRect().width) continue;
    const k = s.getBoundingClientRect().width / vb.width;
    for (const t of s.querySelectorAll('text')) { const f = parseFloat(getComputedStyle(t).fontSize) * k; if (f < 12) out.push(t.textContent + ':' + f.toFixed(1)); } }
  return out; }'''


def ev(page, js, *a):
    return page.evaluate(js, *a)


def sub(a, b):
    return [x - y for x, y in zip(a, b)]


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def scene(page):
    return ev(page, "() => document.querySelector('.k').__po.scene()")


def geom(page, i):
    return ev(page, "(i) => document.querySelector('.k').__po.geom(i)", i)


def card(page, sel):
    return page.inner_text(f'.po-info {sel}').strip() if page.locator(f'.po-info {sel}').count() else ''


def stage_clip(page, frac=0.7):
    b = page.locator('.stage').bounding_box()
    w, h = b['width'] * frac, b['height'] * 0.84
    return {'x': b['x'] + (b['width'] - w) / 2, 'y': b['y'] + b['height'] * 0.14, 'width': w, 'height': h}


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=ARGS)   # own instance (another agent runs a browser too)
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1150}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.k[data-3d=ready]', timeout=30000); page.wait_for_timeout(300)
        sfx = '' if scheme == 'light' else '-dark'

        def shot(name, sel='.k'):
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        def zoom(name, frac=0.7):
            page.screenshot(path=str(OUT / f'{name}{sfx}.png'), clip=stage_clip(page, frac))

        print(f'== {scheme}: default = CHCl₃, ask first')
        check(f'{scheme}: 3D ready', page.get_attribute('.k', 'data-3d') == 'ready')
        check(f'{scheme}: default CHCl₃ in ask mode', page.get_attribute('.k', 'data-po') == 'CHCl3:ask')
        sc = scene(page)
        check(f'{scheme}: ask mode: net dipole not drawn yet', sc['net'] and sc['net']['visible'] is False)
        check(f'{scheme}: ask mode: bond dipoles + δ tags already shown (the clues)', len(sc['bd']) == 3 and all(x['visible'] for x in sc['bd'])
              and sum(1 for x in sc['dl'] if x['visible']) >= 3)
        check(f'{scheme}: ask mode: no conclusion row, net toggle disabled', card(page, '.po-cl') == '' and page.locator('.po-tn').is_disabled())
        check(f'{scheme}: ask mode: HUD asks to guess first', '先在右边猜' in page.inner_text('.po-res'))
        check(f'{scheme}: ask mode: card shows polar bonds + shape', '3 × C–Cl' in card(page, '.po-pb') and card(page, '.po-sh') == 'tetrahedral')
        shot('00-CHCl3-ask'); zoom('z-00-CHCl3-ask')
        h0 = ev(page, CANVAS_JS)['hash']
        page.click('.po-info [data-g="non-polar"]'); page.wait_for_timeout(150)
        v = card(page, '.po-verdict')
        check(f'{scheme}: wrong guess (non-polar) → ✗ verdict', v.startswith('✗ 不对') and 'CHCl₃ 是 polar' in v and
              'po-no' in page.get_attribute('.po-verdict', 'class'), v)
        check(f'{scheme}: wrong guess: picked button red, true answer green',
              'badv' in page.get_attribute('.po-info [data-g="non-polar"]', 'class') and 'good' in page.get_attribute('.po-info [data-g="polar"]', 'class'))
        check(f'{scheme}: after guess: net dipole drawn, canvas changes', scene(page)['net']['visible'] is True and ev(page, CANVAS_JS)['hash'] != h0)
        check(f'{scheme}: after guess: conclusion + cancel rows', card(page, '.po-cl') == CONCL['CHCl3'] and '没被 C–H 抵消' in card(page, '.po-cc'))
        check(f'{scheme}: molecule button marked ✗', page.inner_text('.po-mols [data-m="CHCl3"] i') == '✗')
        shot('01-CHCl3-guess-wrong'); zoom('z-01-CHCl3-guess-wrong')
        page.click('[data-m="H2O"]'); page.wait_for_timeout(120)
        page.click('.po-info [data-g="polar"]'); page.wait_for_timeout(120)
        v = card(page, '.po-verdict')
        check(f'{scheme}: right guess (H₂O polar) → ✓ verdict', v.startswith('✓ 对') and 'po-ok' in page.get_attribute('.po-verdict', 'class'), v)
        check(f'{scheme}: score line 2 guessed, 1 right', '已猜 2 / 12，对 1 个' in card(page, '.po-score'), card(page, '.po-score'))
        shot('02-H2O-guess-right'); zoom('z-02-H2O-guess-right')
        page.click('[data-m="CO2"]'); page.wait_for_timeout(120)
        page.click('.po-info [data-g="non-polar"]'); page.wait_for_timeout(120)
        check(f'{scheme}: right guess (CO₂ non-polar) → ✓, HUD "net dipole = 0 — dipoles cancel"',
              card(page, '.po-verdict').startswith('✓') and 'net dipole = 0 — dipoles cancel' in page.inner_text('.po-res'))
        shot('03-CO2-guess-right')

        print(f'== {scheme}: 直接显示答案, all 12 molecules')
        page.click('.po-ta'); page.wait_for_timeout(120)
        check(f'{scheme}: show-answer on', 'on' in page.get_attribute('.po-ta', 'class'))
        n = 10
        for mid, (polar, shape, nbd, dl) in MOL.items():
            page.click(f'[data-m="{mid}"]'); page.wait_for_timeout(150)
            g = geom(page, mid); sc = scene(page); res = page.inner_text('.po-res')
            check(f'{scheme} {mid}: shown, shape "{shape}"', page.get_attribute('.k', 'data-po') == f'{mid}:shown' and card(page, '.po-sh') == shape, card(page, '.po-sh'))
            if polar:
                check(f'{scheme} {mid}: |net| = {g["netLen"]:.3f} > 0.1, conclusion "{CONCL[mid]}"', g['netLen'] > 0.1 and card(page, '.po-cl') == CONCL[mid], card(page, '.po-cl'))
                check(f'{scheme} {mid}: net arrow drawn, HUD says polar', sc['net'] and sc['net']['visible'] and '不为 0' in res and 'polar molecule' in res, res)
            else:
                check(f'{scheme} {mid}: |net| < 1e-6, conclusion non-polar', g['netLen'] < 1e-6 and card(page, '.po-cl') == 'non-polar', f"{g['netLen']} {card(page, '.po-cl')}")
                want = 'net dipole = 0 — no polar bonds' if nbd == 0 else 'net dipole = 0 — dipoles cancel'
                check(f'{scheme} {mid}: no net arrow, HUD "{want}"', sc['net'] is None and want in res, res)
            if scheme == 'light':
                check(f'{mid}: {nbd} bond-dipole arrows', len(sc['bd']) == nbd, str(len(sc['bd'])))
                atoms = sc['atoms']
                okdir = []
                for a in sc['bd']:
                    f, t = atoms[a['from']], atoms[a['to']]
                    # head (cone + end point) nearer the more electronegative atom; arrow parallel to from → to
                    okdir.append(EN[t['el']] > EN[f['el']] and dist(a['cone'], t['p']) < dist(a['cone'], f['p']) and
                                 dist(a['e'], t['p']) < dist(a['s'], t['p']) and dot(sub(a['e'], a['s']), sub(t['p'], f['p'])) > 0.99 * dist(a['e'], a['s']) * dist(t['p'], f['p']))
                check(f'{mid}: every arrow points to the more electronegative atom (δ−)', all(okdir), str(okdir))
                dens = sorted(round(d['den'], 2) for d in g['dip'])
                lens = sorted(round(dist(a['s'], a['e']) / d, 3) for a, d in zip(sc['bd'], [x['den'] for x in g['dip']])) if sc['bd'] else []
                check(f'{mid}: equal ΔEN → equal arrow length {dens}', len(set(lens)) <= 1, str(lens))
                if nbd:
                    # on screen at the default view: no stub / head-on blob (C–Cl 0.5 drew as a 25 px "key" before)
                    L = ev(page, "() => document.querySelector('.k').__po.layout()")
                    px = [math.hypot(a[2] - a[0], a[3] - a[1]) for a in L['arrows'][:nbd]]
                    check(f'{mid}: every bond-dipole arrow ≥ 30 px on screen and ≥ 0.45 × the longest', min(px) >= 30 and min(px) >= 0.45 * max(px),
                          str([round(x) for x in px]))
                tags = {}
                for x in sc['dl']:
                    tags.setdefault(atoms[x['at']]['el'], set()).add(x['text'])
                want = {k: {'δ' + v} for k, v in dl.items()}
                if mid in ('CH3Cl', 'CHCl3'):
                    want.pop('H', None)
                check(f'{mid}: δ tags {dl}', tags == want, str(tags))
                cnt = {}
                for x in sc['dl']:
                    cnt[atoms[x['at']]['el']] = cnt.get(atoms[x['at']]['el'], 0) + 1
                nterm = sum(1 for a in atoms if a['el'] in want) if want else 0
                check(f'{mid}: one δ tag per charged atom', len(sc['dl']) == nterm, f'{cnt} vs {nterm}')
                if polar:
                    P = [a['p'] for a, x in zip(atoms, g['q']) if x > 1e-9]; N = [a['p'] for a, x in zip(atoms, g['q']) if x < -1e-9]
                    cp = [sum(c) / len(P) for c in zip(*P)]; cn = [sum(c) / len(N) for c in zip(*N)]
                    ne = sc['net']
                    check(f'{mid}: net arrow along the vector sum, head towards the δ− side',
                          dot(sub(ne['e'], ne['s']), g['net']) > 0.999 * dist(ne['e'], ne['s']) * g['netLen'] and dot(g['net'], sub(cn, cp)) > 0 and
                          dist(ne['cone'], ne['e']) < dist(ne['cone'], ne['s']))
            bad = ev(page, LAYOUT_BAD)
            check(f'{scheme} {mid}: δ tags clear of atoms / each other / edges', not bad, str(bad))
            shot(f'{n:02d}-{mid}'); n += 1
            if mid in ('HCl', 'CO2', 'BF3', 'CHCl3', 'H2O', 'NH3', 'SCl2', 'SF6'):
                zoom(f'z-{mid}')

        if scheme == 'light':
            print('== chemistry checks')
            gs = {m: geom(page, m) for m in MOL}
            check('pure data: non-polar |net| < 1e-6', all(gs[m]['netLen'] < 1e-6 for m, v in MOL.items() if not v[0]), str({m: gs[m]['netLen'] for m in MOL}))
            check('pure data: polar |net| > 0.1', all(gs[m]['netLen'] > 0.1 for m, v in MOL.items() if v[0]))
            check('H₂O net dipole > SCl₂ net dipole (ΔEN 1.4 vs 0.5)', gs['H2O']['netLen'] > gs['SCl2']['netLen'] and
                  {round(d['den'], 2) for d in gs['H2O']['dip']} == {1.4} and {round(d['den'], 2) for d in gs['SCl2']['dip']} == {0.5})
            check('C–H counted as virtually non-polar (CH₄: 4, CHCl₃: 1)', gs['CH4']['np'] == 4 and gs['CHCl3']['np'] == 1 and gs['CH3Cl']['np'] == 3)
            page.click('[data-m="SCl2"]'); page.wait_for_timeout(100)
            ms = page.inner_text('.po-info')
            check('SCl₂ card: S δ+ AND both Cl δ− mark-scheme note', 'S 写 δ+ AND 两个 Cl 都写 δ−' in ms and '只写 δ 不写正负号 → 拒绝' in ms, ms)
            check('SCl₂ card: "electronegativity difference … greater" note', 'electronegativity difference (between H and O) is greater (than S and Cl)' in ms)
            page.locator('.po-info').screenshot(path=str(OUT / 'z-info-SCl2.png'))
            page.click('[data-m="H2O"]'); page.wait_for_timeout(100)
            check('H₂O card: ΔEN comparison note', 'O–H 1.4 vs S–Cl 0.5' in page.inner_text('.po-info'))
            page.click('[data-m="CO2"]'); page.wait_for_timeout(100)
            check('CO₂ card: "not all molecules with polar bonds are polar molecules"', 'not all molecules with polar bonds are polar molecules' in page.inner_text('.po-info'))
            check('CO₂: double bonds drawn', ev(page, "() => { let n = 0; document.querySelector('.k').__k3.group.traverse(c => { if (c.geometry && c.geometry.type === 'CylinderGeometry' && c.parent && c.parent.userData && c.parent.userData.atoms) n++; }); return n; }") == 8)
            page.click('[data-m="CHCl3"]'); page.wait_for_timeout(100)
            check('CHCl₃ HUD: C–H virtually non-polar note', 'C–H（2.5 − 2.1 = 0.4）virtually non-polar' in page.inner_text('.po-res'))

        print(f'== {scheme}: toggles')
        page.click('[data-m="H2O"]'); page.wait_for_timeout(120)
        h1 = ev(page, CANVAS_JS)['hash']
        page.click('.po-tb'); page.wait_for_timeout(120)
        sc = scene(page)
        check(f'{scheme}: bond dipoles off → arrows hidden, canvas changes', not any(x['visible'] for x in sc['bd']) and ev(page, CANVAS_JS)['hash'] != h1)
        shot('30-H2O-no-bond-dipoles'); page.click('.po-tb'); page.wait_for_timeout(80)
        page.click('.po-td'); page.wait_for_timeout(120)
        check(f'{scheme}: δ± off → no δ tag visible', not any(x['visible'] for x in scene(page)['dl']) and not ev(page, "() => document.querySelector('.k').__po.layout().dl").__len__())
        shot('31-H2O-no-delta'); page.click('.po-td'); page.wait_for_timeout(80)
        page.click('.po-tn'); page.wait_for_timeout(120)
        check(f'{scheme}: net dipole off → net hidden, HUD says hidden', scene(page)['net']['visible'] is False and '已隐藏' in page.inner_text('.po-res'))
        shot('32-H2O-no-net'); page.click('.po-tn'); page.wait_for_timeout(80)
        check(f'{scheme}: all back on', scene(page)['net']['visible'] and all(x['visible'] for x in scene(page)['bd']) and
              all('on' in page.get_attribute(s, 'class') for s in ('.po-tb', '.po-td', '.po-tn')))
        page.click('.po-ta'); page.wait_for_timeout(100)
        page.click('[data-m="NH3"]'); page.wait_for_timeout(100)
        check(f'{scheme}: show-answer off → unguessed NH₃ back to ask mode, net hidden',
              page.get_attribute('.k', 'data-po') == 'NH3:ask' and scene(page)['net']['visible'] is False)
        page.click('[data-m="CHCl3"]'); page.wait_for_timeout(100)
        check(f'{scheme}: guessed CHCl₃ stays revealed', page.get_attribute('.k', 'data-po') == 'CHCl3:shown')

        if scheme == 'light':
            print('== guess every molecule')
            ctx2 = b.new_context(viewport={'width': 1000, 'height': 1150}, color_scheme='light')
            p2 = ctx2.new_page(); p2.on('pageerror', lambda e: errors.append(f'guess: PAGEERROR {e}'))
            p2.goto(PAGE.as_uri()); p2.wait_for_selector('.k[data-3d=ready]', timeout=30000)
            wrong = {'BF3', 'NH3', 'H2'}   # deliberately wrong for these three
            okv = []
            for mid, (polar, *_r) in MOL.items():
                p2.click(f'[data-m="{mid}"]')
                ans = polar != (mid in wrong)
                p2.click('.po-info [data-g="' + ('polar' if ans else 'non-polar') + '"]')
                v = p2.inner_text('.po-verdict')
                okv.append(v.startswith('✓') == (mid not in wrong) and p2.inner_text(f'.po-mols [data-m="{mid}"] i') == ('✗' if mid in wrong else '✓'))
            check('all 12 guesses judged right / wrong correctly', all(okv), str(okv))
            check('score 12 / 12 guessed, 9 right', '已猜 12 / 12，对 9 个' in p2.inner_text('.po-score'), p2.inner_text('.po-score'))
            p2.locator('.po-mols').screenshot(path=str(OUT / 'z-mol-buttons-marked.png'))
            ctx2.close()

            print('== 3D interaction')
            page.click('.po-ta'); page.click('[data-m="SF6"]'); page.wait_for_timeout(120)
            c0 = ev(page, CANVAS_JS)
            check('canvas is not a flat colour', c0['std'] > 8, str(c0['std']))
            box = page.locator('.stage canvas').bounding_box()
            page.mouse.move(box['x'] + 200, box['y'] + 220); page.mouse.down(); page.mouse.move(box['x'] + 330, box['y'] + 260, steps=8); page.mouse.up()
            page.wait_for_timeout(100)
            check('drag rotates (canvas hash changes)', ev(page, CANVAS_JS)['hash'] != c0['hash'])
            bad = ev(page, LAYOUT_BAD); check('after drag: δ tags still clear', not bad, str(bad))
            shot('50-SF6-dragged')
            page.click('[data-3d=reset]'); page.wait_for_timeout(100)
            check('复位视角 restores the view', ev(page, CANVAS_JS)['hash'] == c0['hash'])
            page.mouse.move(box['x'] + 280, box['y'] + 240); page.mouse.wheel(0, -400); page.wait_for_timeout(150)
            L = ev(page, "() => document.querySelector('.k').__po.layout()")
            hs = [t['h'] for t in L['dl']]
            check('wheel zooms in, δ tags keep their screen size (~23 px)', hs and all(19 < h < 28 for h in hs), str(hs))
            page.click('[data-3d=reset]'); page.wait_for_timeout(80)
            page.click('[data-m="H2O"]'); page.wait_for_timeout(100)
            page.click('[data-3d=spin]')
            hs = []
            for _ in range(5):
                page.wait_for_timeout(250); hs.append(ev(page, CANVAS_JS)['hash'])
            check('自动旋转: 5 frames all different', len(set(hs)) == 5, str(len(set(hs))))
            bad = ev(page, LAYOUT_BAD); check('while spinning: δ tags clear', not bad, str(bad))
            page.click('[data-3d=spin]'); page.wait_for_timeout(120)
            h = ev(page, CANVAS_JS)['hash']; page.wait_for_timeout(300)
            check('spin off → still', ev(page, CANVAS_JS)['hash'] == h)
            page.click('[data-3d=reset]'); page.wait_for_timeout(80)
            check('no [data-clash]', page.locator('[data-clash]').count() == 0)
            check('font ≥ 12px (wide)', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            page.locator('.po-info').screenshot(path=str(OUT / 'z-info-H2O.png'))
            page.locator('.stage .hud').screenshot(path=str(OUT / 'z-hud-H2O.png'))

            print('== narrow (720 px)')
            page.set_viewport_size({'width': 720, 'height': 1500}); page.wait_for_timeout(500)
            k = ev(page, "() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('narrow: card does not overflow', k[0] <= k[1] + 1, str(k))
            check('narrow: font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            bad = []
            for mid in MOL:
                page.click(f'[data-m="{mid}"]'); page.wait_for_timeout(100)
                lb = ev(page, LAYOUT_BAD)
                if lb: bad.append(f'{mid} {lb}')
            check('narrow: δ tags clear for all 12 molecules', not bad, '; '.join(bad))
            page.click('[data-m="SCl2"]'); page.wait_for_timeout(100); shot('60-narrow-SCl2')
            page.click('[data-m="CHCl3"]'); page.wait_for_timeout(100); shot('61-narrow-CHCl3')
        ctx.close()

    print('== fallback (CDN blocked)')
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1150}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(f'fallback: PAGEERROR {e}'))
        page.on('console', lambda m: errors.append(f'fallback: {m.text}') if m.type == 'error' and 'jsdelivr' not in m.text and 'ERR_FAILED' not in m.text else None)
        page.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.fallback.show', timeout=20000); page.wait_for_timeout(200)
        sfx = '' if scheme == 'light' else '-dark'
        check(f'{scheme} fallback shown, data-3d=fallback', page.get_attribute('.k', 'data-3d') == 'fallback')
        txt = ev(page, "() => [...document.querySelectorAll('.po-fb svg text')].map(t => t.textContent)")
        check(f'{scheme} fallback SVG: CO₂ cancels, H₂O net towards O', all(s in txt for s in ('CO₂：linear', 'H₂O：non-linear', 'net dipole = 0 — dipoles cancel',
                                                                                              'net dipole 不为 0，指向 O 一侧 → polar', 'net dipole')), str(txt))
        check(f'{scheme} fallback: δ− × 3 (2 O + 1 O), δ+ × 3 (C + 2 H)', txt.count('δ−') == 3 and txt.count('δ+') == 3, str(txt))
        check(f'{scheme} fallback: 5 arrowheads (4 bond dipoles + 1 net)', page.locator('.po-fb polygon').count() == 5)
        check(f'{scheme} fallback: no [data-clash]', page.locator('[data-clash]').count() == 0,
              str(ev(page, "() => [...document.querySelectorAll('[data-clash]')].map(e => e.textContent)")))
        check(f'{scheme} fallback: 3D-only controls hidden', not page.locator('.po-tools').is_visible())
        page.click('[data-m="SCl2"]'); page.click('.po-info [data-g="polar"]')
        check(f'{scheme} fallback: guess still works', card(page, '.po-verdict').startswith('✓') and card(page, '.po-cl') == CONCL['SCl2'])
        page.locator('.k').screenshot(path=str(OUT / f'70-fallback{sfx}.png'))
        page.locator('.po-fb').screenshot(path=str(OUT / f'z-fallback{sfx}.png'))
        if scheme == 'light':
            check('fallback: SVG text ≥ 12px (wide)', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)[:5]))
            page.set_viewport_size({'width': 720, 'height': 1500}); page.wait_for_timeout(300)
            check('fallback narrow: SVG text ≥ 12px', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)[:5]))
            check('fallback narrow: font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            k = ev(page, "() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('fallback narrow: no overflow', k[0] <= k[1] + 1, str(k))
            page.locator('.po-fb').screenshot(path=str(OUT / 'z-fallback-narrow.png'))
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
