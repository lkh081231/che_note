"""ch03 hybrid cell test (3D): sp³ / sp² / sp hybrid orbitals — alone and in CH₄ / C₂H₄ / C₂H₂, mixing strip,
info card (chapter table 3.4 E word for word), hybrid vs unhybridised p colours, angle arcs + labels, quiz
(propene C1 / C2 / C3 with IUPAC numbering, NH₃ N, H₂O O), fallback SVG.

usage: uv run --with playwright python -I colab/tests/ch03_hybrid.py <preview.html> <shots-dir>
(build the preview first: python tools/build_colab.py ch03 --cell hybrid --3d)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1])
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


# chapter 3.4 E table, word for word
TAB = {
    'sp3': dict(name='sp³', mix='1 s + 3 p', hyb='4 个 sp³', ang='109.5°（tetrahedral）', p='0', n=4, np=0, pi=0, deg=109.47, angT='109.5°',
                ex='CH₄、C₂H₆；NH₃、H₂O 的 N / O 也是 sp³（lone pair 占一个 hybrid orbital）', mol='CH₄', chips='2s+2p+2p+2p→4 × sp³'),
    'sp2': dict(name='sp²', mix='1 s + 2 p', hyb='3 个 sp²', ang='120°（同一平面）', p='1 个 p，垂直于平面 → 形成 π', n=3, np=1, pi=1, deg=120, angT='120°',
                ex='C₂H₄（每个 C）、C=O 的 C', mol='C₂H₄', chips='2s+2p+2p→3 × sp²，剩2p'),
    'sp': dict(name='sp', mix='1 s + 1 p', hyb='2 个 sp', ang='180°', p='2 个 p，互相垂直 → 形成 2 个 π', n=2, np=2, pi=2, deg=180, angT='180°',
               ex='C₂H₂、HCN 的 C', mol='C₂H₂', chips='2s+2p→2 × sp，剩2p+2p'),
}
MOL = {'sp3': {'C': 1, 'H': 4}, 'sp2': {'C': 2, 'H': 4}, 'sp': {'C': 2, 'H': 2}}
LABS = {
    ('sp3', 'iso'): ['sp³', '109.5°'], ('sp2', 'iso'): ['sp²', 'p', '120°'], ('sp', 'iso'): ['sp', 'p', 'p', '180°'],
    ('sp3', 'mol'): ['sp³', 's (H)', 'σ (sp³–s)', '109.5°'],
    ('sp2', 'mol'): ['sp²', 'p', 'p', 'π: p ∥ p, sideways overlap', '120°'],
    ('sp', 'mol'): ['sp', 'p', 'p', 'π', 'π', '180°'],
}
QUIZ = {'C1': 'sp2', 'C2': 'sp2', 'C3': 'sp3', 'N': 'sp3', 'O': 'sp3'}

CANVAS_JS = """() => { const c=document.querySelector('.stage canvas'); if(!c) return null;
  const g=document.createElement('canvas'); g.width=c.width; g.height=c.height; const x=g.getContext('2d'); x.drawImage(c,0,0);
  const d=x.getImageData(0,0,g.width,g.height).data; let s=0,s2=0,n=0;
  for(let i=0;i<d.length;i+=16){const v=d[i]+d[i+1]+d[i+2]; s+=v; s2+=v*v; n++;}
  const m=s/n; const u=c.toDataURL(); return {std:Math.sqrt(s2/n-m*m), hash:u.length+':'+u.slice(-300)}; }"""

PIX_JS = """([x, y]) => { const c=document.querySelector('.stage canvas'); const k=c.width/c.clientWidth;
  const g=document.createElement('canvas'); g.width=c.width; g.height=c.height; const t=g.getContext('2d'); t.drawImage(c,0,0);
  const d=t.getImageData(Math.round(x*k),Math.round(y*k),1,1).data; return [d[0],d[1],d[2]]; }"""

# labels clear of atoms, the HUD, canvas edges, each other, other labels' anchors, the angle arcs; ≥ 12 px
LAYOUT_BAD = """() => { const L = document.querySelector('.k').__hy.layout(), bad = [];
  const rc = (r, c) => { const dx=Math.max(r.x-c.x,0,c.x-(r.x+r.w)), dy=Math.max(r.y-c.y,0,c.y-(r.y+r.h)); return Math.hypot(dx,dy) < c.r - 1; };
  const rr = (a, b) => a.x < b.x + b.w - 1 && b.x < a.x + a.w - 1 && a.y < b.y + b.h - 1 && b.y < a.y + a.h - 1;
  L.tags.forEach((t, i) => {
    L.atoms.forEach(a => { if (rc(t, a)) bad.push(t.text + ' on atom ' + a.el); });
    if (t.x < 0 || t.y < L.hud || t.x + t.w > L.W || t.y + t.h > L.H) bad.push(t.text + ' out of canvas');
    L.tags.forEach((u, j) => { if (j > i && rr(t, u)) bad.push(t.text + ' on ' + u.text);
                              if (j !== i && rc(t, {x: u.ax, y: u.ay, r: 4})) bad.push(t.text + ' hides anchor of ' + u.text); });
    L.arcs.forEach(pts => { if (pts.some(p => rc(t, {x: p[0], y: p[1], r: 2}))) bad.push(t.text + ' on an angle arc'); });
    if (t.h * 0.6875 < 12) bad.push(t.text + ' font < 12px (' + t.h.toFixed(1) + ')');
  });
  L.elH.forEach((h, i) => { if (h * 0.6875 < 12) bad.push('element ' + L.atoms[i].el + ' font < 12px'); });
  return bad; }"""

SMALL_JS = '''() => { const out = [];
  for (const e of document.querySelectorAll('.k *')) {
    if (!e.offsetParent && e.tagName !== 'svg') continue;
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


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def deg(a, b):
    import math
    c = dot(a, b) / (dot(a, a) ** 0.5 * dot(b, b) ** 0.5)
    return math.degrees(math.acos(max(-1, min(1, c))))


def hue(c):
    import colorsys
    h, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in c))
    return h * 360, s, v


def stage_clip(page, frac=0.9):
    b = page.locator('.stage').bounding_box()
    w = b['width'] * frac
    return {'x': b['x'] + (b['width'] - w) / 2, 'y': b['y'] + b['height'] * 0.07, 'width': w, 'height': b['height'] * 0.92}


def setmode(page, m, v):
    page.click(f'[data-hy="{m}"]'); page.click(f'[data-view="{v}"]'); page.wait_for_timeout(450)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=ARGS)   # own instance (another agent runs a browser too)
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1500}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.k[data-3d=ready]', timeout=30000); page.wait_for_timeout(500)
        sfx = '' if scheme == 'light' else '-dark'

        def shot(name, sel='.k'):
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        def zoom(name, frac=0.9):
            page.screenshot(path=str(OUT / f'{name}{sfx}.png'), clip=stage_clip(page, frac))

        print(f'== {scheme}: default')
        check(f'{scheme}: 3D ready', page.get_attribute('.k', 'data-3d') == 'ready')
        check(f'{scheme}: default sp³, isolated', page.get_attribute('.k', 'data-hy') == 'sp3' and page.get_attribute('.k', 'data-view') == 'iso')

        n = 1
        for view in ('iso', 'mol'):
            for m, t in TAB.items():
                setmode(page, m, view)
                tag = f'{scheme} {m}/{view}'
                # info card
                info = {k: page.inner_text(f'.hy-{k}') for k in ('tmix', 'thyb', 'tang', 'tp', 'tex', 'nh', 'np', 'npi')}
                check(f'{tag}: table row word for word', info['tmix'] == t['mix'] and info['thyb'] == t['hyb'] and info['tang'] == t['ang']
                      and info['tp'] == t['p'] and info['tex'] == t['ex'], str(info))
                check(f'{tag}: counts {t["n"]} hybrid / {t["np"]} p / {t["pi"]} π', info['nh'] == str(t['n']) and info['np'] == str(t['np']) and info['npi'] == str(t['pi'])
                      and page.get_attribute('.k', 'data-nh') == str(t['n']) and page.get_attribute('.k', 'data-np') == str(t['np']))
                check(f'{tag}: rule sentence', '数 σ bonds + lone pairs：4 → sp³、3 → sp²、2 → sp' in page.inner_text('.hy-rule'))
                chips = page.inner_text('.hy-eq').replace('\n', '').replace(' ', '')
                check(f'{tag}: mixing strip {t["chips"]}', chips == t['chips'].replace(' ', ''), chips)
                check(f'{tag}: orbital boxes: {t["n"]} hybrid + {t["np"]} p, 1 electron each',
                      page.locator('.hy-box i.hy-bh').count() == t['n'] and page.locator('.hy-box i.hy-bp, .hy-box i.hy-bp2').count() == t['np']
                      and all(x == '↑' for x in page.locator('.hy-box i.hy-bh, .hy-box i.hy-bp, .hy-box i.hy-bp2').all_inner_texts()))
                check(f'{tag}: buttons on', page.locator(f'[data-hy="{m}"].on').count() == 1 and page.locator(f'[data-view="{view}"].on').count() == 1)
                # 3D content
                orbs = ev(page, "() => document.querySelector('.k').__hy.orbs()")
                atoms = ev(page, "() => document.querySelector('.k').__hy.atoms()")
                carbons = [i for i, a in enumerate(atoms) if a['el'] == 'C']
                for c in carbons:
                    hy_ = [o for o in orbs if o['at'] == c and o['k'] == 'hyb']
                    pp = [o for o in orbs if o['at'] == c and o['k'] == 'p']
                    check(f'{tag} C#{c}: {t["n"]} hybrids, {t["np"]} unhybridised p', len(hy_) == t['n'] and len(pp) == t['np'], f'{len(hy_)} {len(pp)}')
                    angs = [deg(a['dir'], b_['dir']) for i, a in enumerate(hy_) for b_ in hy_[i + 1:]]
                    check(f'{tag} C#{c}: every hybrid–hybrid angle = {t["deg"]}°', all(abs(a - t['deg']) < 0.1 for a in angs), str([round(a, 2) for a in angs]))
                    check(f'{tag} C#{c}: p ⟂ every hybrid and ⟂ each other',
                          all(abs(dot(q['dir'], h['dir'])) < 1e-9 for q in pp for h in hy_) and all(abs(dot(pp[0]['dir'], q['dir'])) < 1e-9 for q in pp[1:]))
                    check(f'{tag} C#{c}: hybrids one colour, p another', len({o['color'] for o in hy_}) == 1 and all(q['color'] not in {o['color'] for o in hy_} for q in pp))
                if view == 'mol':
                    els = {}
                    for a in atoms: els[a['el']] = els.get(a['el'], 0) + 1
                    check(f'{tag}: molecule {t["mol"]} atoms {MOL[m]}', els == MOL[m], str(els))
                    check(f'{tag}: caption names {t["mol"]}', t['mol'] in page.inner_text('.hy-cap'))
                    if m == 'sp2':
                        pp = [o for o in orbs if o['k'] == 'p']
                        check(f'{tag}: the two C p orbitals are parallel (→ π)', len(pp) == 2 and abs(abs(dot(pp[0]['dir'], pp[1]['dir'])) - 1) < 1e-9)
                        check(f'{tag}: all 6 atoms in the plane ⟂ p', all(abs(dot(a['p'], pp[0]['dir'])) < 1e-9 for a in atoms))
                    if m == 'sp':
                        pp = [o for o in orbs if o['k'] == 'p']
                        pairs = {}
                        for q in pp: pairs.setdefault(q['band'], []).append(q['dir'])
                        check(f'{tag}: two π directions: each p pair parallel, the pairs at right angles',
                              len(pairs) == 2 and all(abs(dot(v[0], v[1]) - 1) < 1e-9 for v in pairs.values())
                              and abs(dot(pairs['p1'][0], pairs['p2'][0])) < 1e-9)
                        check(f'{tag}: H–C≡C–H on a straight line', all(abs(a['p'][1]) < 1e-9 and abs(a['p'][2]) < 1e-9 for a in atoms))
                    if m == 'sp3':
                        c0 = atoms[0]['p']; hs = [a['p'] for a in atoms if a['el'] == 'H']
                        ang = [deg([x - y for x, y in zip(hs[i], c0)], [x - y for x, y in zip(hs[j], c0)]) for i in range(4) for j in range(i + 1, 4)]
                        check(f'{tag}: every H–C–H = 109.47°', all(abs(a - 109.47) < 0.05 for a in ang), str(ang))
                # angle arc ↔ label
                arcs = ev(page, "() => document.querySelector('.k').__hy.arcs()")
                check(f'{tag}: one arc, {t["angT"]}, real arc angle matches', len(arcs) == 1 and arcs[0]['text'] == t['angT'] and abs(arcs[0]['deg'] - t['deg']) < 1.0,
                      str([(a['text'], round(a['deg'], 2)) for a in arcs]))
                L = ev(page, "() => document.querySelector('.k').__hy.layout()")
                texts = sorted(x['text'] for x in L['tags'])
                check(f'{tag}: labels {LABS[(m, view)]}', texts == sorted(LABS[(m, view)]), str(texts))
                at_ = [x for x in L['tags'] if x['arc']]
                if at_:
                    a0 = at_[0]
                    dx = max(a0['x'] - a0['ax'], 0, a0['ax'] - (a0['x'] + a0['w'])); dy = max(a0['y'] - a0['ay'], 0, a0['ay'] - (a0['y'] + a0['h']))
                    check(f'{tag}: angle label sits by its arc (gap ≤ 45 px)', (dx * dx + dy * dy) ** 0.5 <= 45, f'{(dx * dx + dy * dy) ** 0.5:.1f}')
                check(f'{tag}: angle label is in the arc colour (--s3)', all(x['band'] == 'ang' for x in at_) and len(at_) == 1)
                bad = ev(page, LAYOUT_BAD)
                check(f'{tag}: labels clear', not bad, str(bad))
                c = ev(page, CANVAS_JS)
                check(f'{tag}: canvas not flat', c['std'] > 8)
                # on screen: a hybrid lobe is blue, an unhybridised p lobe red / orange
                if t['np']:
                    c0 = carbons[0]
                    hy0 = [o for o in orbs if o['at'] == c0 and o['k'] == 'hyb']
                    pp = [o for o in orbs if o['at'] == c0 and o['k'] == 'p']
                    # sample the point 0.6 along each lobe; skip hybrids hidden behind something
                    hcols = [ev(page, PIX_JS, ev(page, f"() => document.querySelector('.k').__hy.proj({o['centre']})")) for o in hy0]
                    pcols = [ev(page, PIX_JS, ev(page, f"() => document.querySelector('.k').__hy.proj({o['centre']})")) for o in pp]
                    blue = lambda col: 180 <= hue(col)[0] <= 260 and hue(col)[1] > 0.15
                    warm = lambda col: (hue(col)[0] <= 45 or hue(col)[0] >= 330) and hue(col)[1] > 0.15
                    check(f'{tag}: on screen hybrids blue, p red / orange', sum(blue(x) for x in hcols) >= 1 and all(warm(x) for x in pcols),
                          f'h {hcols} p {pcols}')
                shot(f'{n:02d}-{m}-{view}'); zoom(f'z-{m}-{view}')
                # close-up of the angle label + arc
                if at_:
                    a0 = at_[0]; sb = page.locator('.stage').bounding_box()
                    x0 = min(a0['x'], a0['ax']) - 60; y0 = min(a0['y'], a0['ay']) - 50
                    x1 = max(a0['x'] + a0['w'], a0['ax']) + 60; y1 = max(a0['y'] + a0['h'], a0['ay']) + 50
                    x0 = max(0, x0); y0 = max(0, y0); x1 = min(sb['width'], x1); y1 = min(sb['height'], y1)
                    page.screenshot(path=str(OUT / f'z-angle-{m}-{view}{sfx}.png'), clip={'x': sb['x'] + x0, 'y': sb['y'] + y0, 'width': x1 - x0, 'height': y1 - y0})
                n += 1
        page.click('[data-hy="sp2"]'); page.click('[data-view="iso"]'); page.wait_for_timeout(400)
        page.locator('.hy-mix').screenshot(path=str(OUT / f'z-mix-sp2{sfx}.png'))
        page.click('[data-hy="sp"]'); page.wait_for_timeout(400)
        page.locator('.hy-mix').screenshot(path=str(OUT / f'z-mix-sp{sfx}.png'))
        page.locator('.hy-info').screenshot(path=str(OUT / f'z-info-sp{sfx}.png'))
        page.locator('.stage .hud').screenshot(path=str(OUT / f'z-hud-sp{sfx}.png'))

        print(f'== {scheme}: quiz')
        check(f'{scheme}: propene drawn with C1 C2 C3 under H₂C / CH / CH₃',
              ev(page, "() => [...document.querySelectorAll('.hy-prop text')].map(t => t.textContent).join(' ')") == 'H₂C C1 CH C2 CH₃ C3')
        xs = ev(page, "() => { const t=[...document.querySelectorAll('.hy-prop text')]; return t.map(e => { const b=e.getBBox(); return [e.textContent, b.x + b.width/2]; }); }")
        d = dict(xs)
        check(f'{scheme}: IUPAC: C1 under the =CH₂ end, C3 under CH₃', abs(d['C1'] - d['H₂C']) < 2 and abs(d['C3'] - d['CH₃']) < 2 and d['C1'] < d['C2'] < d['C3'])
        for q, a in QUIZ.items():
            wrong = 'sp' if a != 'sp' else 'sp3'
            page.click(f'.hy-q[data-q="{q}"] [data-a="{wrong}"]')
            check(f'{scheme} quiz {q}: {wrong} marked wrong', page.get_attribute(f'.hy-q[data-q="{q}"]', 'data-ok') == '0'
                  and page.locator(f'.hy-q[data-q="{q}"] button.badv').count() == 1 and '✗' in page.inner_text(f'.hy-q[data-q="{q}"] .hy-qf'))
        check(f'{scheme} quiz: score 0 / 5 after all wrong', page.inner_text('.hy-score') == '答对 0 / 5')
        shot('40-quiz-wrong', '.hy-quiz')
        for q, a in QUIZ.items():
            page.click(f'.hy-q[data-q="{q}"] [data-a="{a}"]')
            f = page.inner_text(f'.hy-q[data-q="{q}"] .hy-qf')
            check(f'{scheme} quiz {q}: {a} right, with σ / lone-pair count', page.get_attribute(f'.hy-q[data-q="{q}"]', 'data-ok') == '1'
                  and page.locator(f'.hy-q[data-q="{q}"] button.good').count() == 1 and page.locator(f'.hy-q[data-q="{q}"] button.badv').count() == 0
                  and '✓' in f and 'σ' in f and TAB[a]['name'] in f, f)
        check(f'{scheme} quiz: 5 / 5', page.inner_text('.hy-score') == '答对 5 / 5')
        shot('41-quiz-right', '.hy-quiz')

        if scheme == 'light':
            print('== 3D interaction')
            setmode(page, 'sp2', 'iso')
            c0 = ev(page, CANVAS_JS)
            box = page.locator('.stage canvas').bounding_box()
            page.mouse.move(box['x'] + 200, box['y'] + 250); page.mouse.down(); page.mouse.move(box['x'] + 320, box['y'] + 300, steps=8); page.mouse.up()
            page.wait_for_timeout(450)
            c1 = ev(page, CANVAS_JS)
            check('drag rotates (canvas hash changes)', c1['hash'] != c0['hash'])
            bad = ev(page, LAYOUT_BAD); check('after drag: labels placed again, clear', not bad, str(bad))
            shot('50-sp2-iso-dragged')
            page.click('[data-3d=reset]'); page.wait_for_timeout(450)
            check('复位视角 restores the view', ev(page, CANVAS_JS)['hash'] == c0['hash'])
            page.mouse.move(box['x'] + 280, box['y'] + 220); page.mouse.wheel(0, -300); page.wait_for_timeout(450)
            L = ev(page, "() => document.querySelector('.k').__hy.layout()")
            check('wheel zoom: labels keep their screen size (26 px)', all(abs(t['h'] - 26) < 1.5 for t in L['tags']), str([round(t['h'], 1) for t in L['tags']]))
            page.click('[data-3d=reset]'); page.wait_for_timeout(300)
            page.click('[data-3d=spin]')
            hs = []
            for _ in range(5):
                page.wait_for_timeout(250); hs.append(ev(page, CANVAS_JS)['hash'])
            check('自动旋转: 5 frames over ~1.2 s all different', len(set(hs)) == 5, str(len(set(hs))))
            page.click('[data-3d=spin]'); page.wait_for_timeout(500)
            h = ev(page, CANVAS_JS)['hash']; page.wait_for_timeout(400)
            check('spin off → still', ev(page, CANVAS_JS)['hash'] == h)
            page.click('[data-3d=reset]'); page.wait_for_timeout(300)
            hs = set()
            for m in TAB:
                for v in ('iso', 'mol'):
                    setmode(page, m, v); hs.add(ev(page, CANVAS_JS)['hash'])
            check('six scenes → six different pictures', len(hs) == 6)
            check('no [data-clash]', page.locator('[data-clash]').count() == 0)
            check('font ≥ 12px (wide)', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            check('SVG font ≥ 12px (wide)', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)[:5]))

            print('== narrow (720 px)')
            page.set_viewport_size({'width': 720, 'height': 1700}); page.wait_for_timeout(700)
            k = ev(page, "() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('narrow: card does not overflow', k[0] <= k[1] + 1, str(k))
            check('narrow: font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            check('narrow: SVG font ≥ 12px', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)[:5]))
            bad = []
            for m in TAB:
                for v in ('iso', 'mol'):
                    setmode(page, m, v)
                    lb = ev(page, LAYOUT_BAD)
                    if lb: bad.append(f'{m}/{v} {lb}')
            check('narrow: labels clear in all six scenes', not bad, '; '.join(bad))
            setmode(page, 'sp2', 'mol'); shot('60-narrow-sp2-mol')
            setmode(page, 'sp', 'iso'); shot('61-narrow-sp-iso')
        ctx.close()

    print('== fallback (CDN blocked)')
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1400}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(f'fallback: PAGEERROR {e}'))
        page.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.fallback.show', timeout=20000); page.wait_for_timeout(200)
        sfx = '' if scheme == 'light' else '-dark'
        check(f'{scheme} fallback shown, data-3d=fallback', page.get_attribute('.k', 'data-3d') == 'fallback')
        txt = ev(page, "() => [...document.querySelectorAll('.hy-fb svg text')].map(t => t.textContent).join(' | ')")
        check(f'{scheme} fallback SVG: three panels, angles + names', all(s in txt for s in ('109.5°', '120°', '180°', 'sp³：4 × sp³，剩 0 个 p',
                                                                                           'sp²：3 × sp²，剩 1 个 p', 'sp：2 × sp，剩 2 个 p')), txt)
        check(f'{scheme} fallback: p labels 0 + 1 + 2', txt.split(' | ').count('p') == 3, txt)
        check(f'{scheme} fallback: 3D-only controls hidden', not page.locator('.hy-views').is_visible())
        check(f'{scheme} fallback: 3 angle arcs', page.locator('.hy-fb path').count() == 3)
        check(f'{scheme} fallback: no [data-clash]', page.locator('[data-clash]').count() == 0,
              str(ev(page, "() => [...document.querySelectorAll('[data-clash]')].map(e => e.textContent)")))
        page.click('[data-hy="sp"]')
        check(f'{scheme} fallback: info card still switches', page.inner_text('.hy-nh') == '2' and page.inner_text('.hy-tp') == TAB['sp']['p'])
        page.click('.hy-q[data-q="C1"] [data-a="sp2"]')
        check(f'{scheme} fallback: quiz still works', page.get_attribute('.hy-q[data-q="C1"]', 'data-ok') == '1')
        page.locator('.k').screenshot(path=str(OUT / f'70-fallback{sfx}.png'))
        page.locator('.hy-fb').screenshot(path=str(OUT / f'z-fallback{sfx}.png'))
        if scheme == 'light':
            page.set_viewport_size({'width': 720, 'height': 1500}); page.wait_for_timeout(300)
            check('fallback narrow: SVG text ≥ 12px', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)[:5]))
            check('fallback narrow: font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            page.locator('.hy-fb').screenshot(path=str(OUT / 'z-fallback-narrow.png'))
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
