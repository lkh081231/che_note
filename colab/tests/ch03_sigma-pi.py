"""ch03 sigma-pi cell test (3D): σ / π overlap for H₂, Cl₂, C₂H₆, C₂H₄, HCN, N₂ — overlap slider, σ / π filter,
σ / π counts + orbital table, labels clear of atoms / each other, π above + below the σ axis, two π at right angles,
fallback SVG.

usage: uv run --with playwright python -I colab/tests/ch03_sigma-pi.py <preview.html> <shots-dir>
(build the preview first: python tools/build_colab.py ch03 --cell sigma-pi --3d)
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


# id: (formula, σ, π, table rows [bond, σ, π, orbitals snippet], bond-phase labels) — 3.4 D table of the chapter
SPECIES = {
    'H2': ('H₂', 1, 0, [('H–H', 1, 0, 's–s')], ['σ (s–s)', 'direct (end-on) overlap']),
    'Cl2': ('Cl₂', 1, 0, [('Cl–Cl', 1, 0, 'p–p')], ['σ (p–p)', 'p–p, direct (end-on) overlap']),
    'C2H6': ('C₂H₆', 7, 0, [('C–C', 1, 0, 'sp³–sp³'), ('C–H × 6', 6, 0, 'sp³–s')], ['σ (sp³–sp³)', 'σ (sp³–s)', 'direct (end-on) overlap']),
    'C2H4': ('C₂H₄', 5, 1, [('C=C', 1, 1, 'sp²–sp²'), ('C–H × 4', 4, 0, 'sp²–s')],
             ['σ (sp²–sp²)', 'σ (sp²–s)', 'π (p–p)', 'π', 'sideways overlap of adjacent p orbitals', 'direct (end-on) overlap', 'molecular plane']),
    'HCN': ('HCN', 2, 2, [('H–C', 1, 0, 's–sp'), ('C≡N', 1, 2, 'sp–sp')],
            ['σ (s–sp)', 'σ (sp–sp)', 'π', 'π', 'sideways overlap of adjacent p orbitals', 'direct (end-on) overlap']),
    'N2': ('N₂', 1, 2, [('N≡N', 1, 2, 'sideways overlap of adjacent p orbitals')],
           ['σ', 'π', 'π', 'sideways overlap of adjacent p orbitals', 'direct (end-on) overlap']),
}
SIGMA_LAB = {'direct (end-on) overlap', 'p–p, direct (end-on) overlap'}

CANVAS_JS = """() => { const c=document.querySelector('.stage canvas'); if(!c) return null;
  const g=document.createElement('canvas'); g.width=c.width; g.height=c.height; const x=g.getContext('2d'); x.drawImage(c,0,0);
  const d=x.getImageData(0,0,g.width,g.height).data; let s=0,s2=0,n=0;
  for(let i=0;i<d.length;i+=16){const v=d[i]+d[i+1]+d[i+2]; s+=v; s2+=v*v; n++;}
  const m=s/n; const u=c.toDataURL(); return {std:Math.sqrt(s2/n-m*m), hash:u.length+':'+u.slice(-300)}; }"""

# pixel colour of the canvas at CSS point (x, y)
PIX_JS = """([x, y]) => { const c=document.querySelector('.stage canvas'); const k=c.width/c.clientWidth;
  const g=document.createElement('canvas'); g.width=c.width; g.height=c.height; const t=g.getContext('2d'); t.drawImage(c,0,0);
  const d=t.getImageData(Math.round(x*k),Math.round(y*k),1,1).data; return [d[0],d[1],d[2]]; }"""

# every label must stay clear of atoms, the HUD strip, the canvas edges, the other labels, and not cover what any label points at
LAYOUT_BAD = """() => { const L = document.querySelector('.k').__sp.layout(), bad = [];
  const rc = (r, c) => { const dx=Math.max(r.x-c.x,0,c.x-(r.x+r.w)), dy=Math.max(r.y-c.y,0,c.y-(r.y+r.h)); return Math.hypot(dx,dy) < c.r - 1; };
  const rr = (a, b) => a.x < b.x + b.w - 1 && b.x < a.x + a.w - 1 && a.y < b.y + b.h - 1 && b.y < a.y + a.h - 1;
  L.tags.forEach((t, i) => {
    L.atoms.forEach(a => { if (rc(t, a)) bad.push(t.text + ' on atom ' + a.el); });
    if (t.x < 0 || t.y < L.hud || t.x + t.w > L.W || t.y + t.h > L.H) bad.push(t.text + ' out of canvas');
    L.tags.forEach((u, j) => { if (j > i && rr(t, u)) bad.push(t.text + ' on ' + u.text);
                              if (j !== i && rc(t, {x: u.ax, y: u.ay, r: 4})) bad.push(t.text + ' hides anchor of ' + u.text); });
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

# SVG text: rendered size = font-size × (rendered width / viewBox width)
SVG_SMALL_JS = '''() => { const out = [];
  for (const s of document.querySelectorAll('.k svg')) { const vb = s.viewBox.baseVal; if (!vb || !vb.width) continue;
    const k = s.getBoundingClientRect().width / vb.width;
    for (const t of s.querySelectorAll('text')) { const f = parseFloat(getComputedStyle(t).fontSize) * k; if (f < 12) out.push(t.textContent + ':' + f.toFixed(1)); } }
  return out; }'''


def ev(page, js):
    return page.evaluate(js)


def setT(page, v):
    page.evaluate(f"() => {{ const r = document.querySelector('.sp-t'); r.value = {v}; r.dispatchEvent(new Event('input')); }}")
    page.wait_for_timeout(120)


def tags(page):
    return [t['text'] for t in page.evaluate("() => document.querySelector('.k').__sp.layout().tags")]


def clouds(page):
    return page.evaluate("() => document.querySelector('.k').__sp.clouds()")


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def stage_clip(page, frac=0.8):
    b = page.locator('.stage').bounding_box()
    w = b['width'] * frac
    return {'x': b['x'] + (b['width'] - w) / 2, 'y': b['y'] + b['height'] * 0.12, 'width': w, 'height': b['height'] * 0.84}


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=ARGS)   # own instance (another agent runs a browser too)
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1150}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.k[data-3d=ready]', timeout=30000); page.wait_for_timeout(400)
        sfx = '' if scheme == 'light' else '-dark'

        def shot(name, sel='.k'):
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        def zoom(name, frac=0.8):
            page.screenshot(path=str(OUT / f'{name}{sfx}.png'), clip=stage_clip(page, frac))

        print(f'== {scheme}: default')
        check(f'{scheme}: 3D ready', page.get_attribute('.k', 'data-3d') == 'ready')
        check(f'{scheme}: default C₂H₄, slider 1, show all',
              page.get_attribute('.k', 'data-sp') == 'C2H4' and page.get_attribute('.k', 'data-t') == '1.00' and page.get_attribute('.k', 'data-show') == 'all')
        check(f'{scheme}: HUD rule', '每条 bond 都有 1 个 σ；double = 1σ + 1π；triple = 1σ + 2π' in page.inner_text('.stage .hud'))
        ms = page.inner_text('.sp-ms')
        check(f'{scheme}: MS sentence (π breaks first)', 'electrons in π bond are further away from the nuclei so weaker attraction' in ms, ms)

        n = 1
        for sid, (f, ns, npi, rows, labs) in SPECIES.items():
            page.click(f'[data-sp="{sid}"]'); page.wait_for_timeout(350)
            setT(page, 100); page.wait_for_timeout(300)
            info = page.inner_text('.sp-info')
            check(f'{scheme} {sid}: σ {ns} / π {npi}',
                  page.inner_text('.sp-ns') == str(ns) and page.inner_text('.sp-np') == str(npi) and f in info, info[:80])
            if scheme == 'light':
                trs = page.locator('.sp-info tbody tr').all_inner_texts()
                ok = len(trs) == len(rows) and all(r[0] in t and r[3] in t and t.split('\t')[1:3] == [str(r[1]), str(r[2])] for r, t in zip(rows, trs))
                check(f'{sid}: bond table {rows}', ok, str(trs))
                check(f'{sid}: row σ sum = {ns}, π sum = {npi}', sum(r[1] for r in rows) == ns and sum(r[2] for r in rows) == npi)
                check(f'{sid}: species button on', page.locator(f'[data-sp="{sid}"].on').count() == 1)
                check(f'{sid}: caption names the molecule', f in page.inner_text('.sp-cap'))
            t1 = tags(page)
            check(f'{scheme} {sid}: slider 1 labels {labs}', sorted(t1) == sorted(labs), str(t1))
            bad = ev(page, LAYOUT_BAD)
            check(f'{scheme} {sid} slider 1: labels clear', not bad, str(bad))
            cl = clouds(page)
            check(f'{scheme} {sid}: slider 1 → every bond cloud shown', cl and all(c['visible'] and c['opacity'] > 0.45 for c in cl))
            check(f'{scheme} {sid}: π clouds = {npi}', sum(1 for c in cl if c['k'] == 'pi') == npi)
            h1 = ev(page, CANVAS_JS)
            shot(f'{n:02d}-{sid}-t1'); zoom(f'z-{sid}-t1')
            setT(page, 0); page.wait_for_timeout(300)
            h0 = ev(page, CANVAS_JS)
            check(f'{scheme} {sid}: slider 0 changes canvas', h0['hash'] != h1['hash'])
            check(f'{scheme} {sid}: slider 0 → bond clouds hidden, orbital labels', all(not c['visible'] for c in clouds(page))
                  and not any(t.startswith('σ') or t.startswith('π') for t in tags(page)), str(tags(page)))
            check(f'{scheme} {sid}: slider 0 text', '分开' in page.inner_text('.sp-tv'))
            bad = ev(page, LAYOUT_BAD)
            check(f'{scheme} {sid} slider 0: labels clear', not bad, str(bad))
            shot(f'{n:02d}-{sid}-t0'); zoom(f'z-{sid}-t0')
            if scheme == 'light':
                at0 = page.evaluate("() => document.querySelector('.k').__sp.atoms()")
                setT(page, 50)
                at5 = page.evaluate("() => document.querySelector('.k').__sp.atoms()")
                setT(page, 100)
                at1 = page.evaluate("() => document.querySelector('.k').__sp.atoms()")
                d = lambda A: max(abs(a['p'][0] - b_['p'][0]) for a in A for b_ in A)
                check(f'{sid}: slider pulls atoms together continuously (span 0 > 0.5 > 1)', d(at0) > d(at5) > d(at1), f'{d(at0):.2f} {d(at5):.2f} {d(at1):.2f}')
                check(f'{sid}: half-way text', page.get_attribute('.k', 'data-t') == '1.00' and '成键位置' in page.inner_text('.sp-tv'))
            setT(page, 100)
            n += 1

        print(f'== {scheme}: geometry of the π bonds')
        page.click('[data-sp="C2H4"]'); page.wait_for_timeout(300)
        at = page.evaluate("() => document.querySelector('.k').__sp.atoms()")
        check(f'{scheme}: C₂H₄ all 6 atoms coplanar (y = 0)', len(at) == 6 and all(abs(a['p'][1]) < 1e-6 for a in at))
        pi = [c for c in clouds(page) if c['k'] == 'pi'][0]
        ys = sorted(c[1] for c in pi['centres'])
        check(f'{scheme}: C₂H₄ π = two lobes, above and below the C=C axis (⟂ plane)',
              len(pi['centres']) == 2 and ys[0] < -0.4 and ys[1] > 0.4 and abs(dot(pi['axis'], [0, 1, 0])) > 0.999, str(pi['centres']))
        # pixel check: the two π lobe centres on screen are coloured (π), and the axis midpoint between them is σ, not π
        page.click('[data-show="pi"]'); page.wait_for_timeout(350)
        bg = ev(page, "() => getComputedStyle(document.querySelector('.k')).getPropertyValue('--card')")
        pts = [page.evaluate(f"() => document.querySelector('.k').__sp.proj({c})") for c in pi['centres']]
        mid = page.evaluate(f"() => document.querySelector('.k').__sp.proj({pi['mid']})")
        cols = [ev_ for ev_ in (page.evaluate(PIX_JS, q) for q in pts)]
        cm = page.evaluate(PIX_JS, mid)
        redish = lambda c: c[0] > c[2] + 40 and c[0] > c[1] + 25
        check(f'{scheme}: only-π C₂H₄: both lobes red on screen, gap between them is not', all(redish(c) for c in cols) and not redish(cm), f'{cols} mid {cm}')
        check(f'{scheme}: lobes are far apart on screen (> 60 px)', abs(pts[0][1] - pts[1][1]) > 60, str(pts))
        zoom('z-C2H4-only-pi')
        page.click('[data-show="all"]'); page.wait_for_timeout(200)
        for sid in ('HCN', 'N2'):
            page.click(f'[data-sp="{sid}"]'); page.wait_for_timeout(300)
            pis = [c for c in clouds(page) if c['k'] == 'pi']
            check(f'{scheme} {sid}: two π at right angles to each other and to the axis',
                  len(pis) == 2 and abs(dot(pis[0]['axis'], pis[1]['axis'])) < 1e-6 and all(abs(dot(c['axis'], c['u'])) < 1e-6 for c in pis),
                  str([c['axis'] for c in pis]))
            check(f'{scheme} {sid}: the two π have different colours (--s2 / --s4)', pis[0]['color'] != pis[1]['color'] and {c['band'] for c in pis} == {'p1', 'p2'})
            page.click('[data-show="pi"]'); page.wait_for_timeout(350)
            # on screen: the first π lobes are separated vertically, the second π lobes mostly horizontally
            s1 = [page.evaluate(f"() => document.querySelector('.k').__sp.proj({c})") for c in pis[0]['centres']]
            s2 = [page.evaluate(f"() => document.querySelector('.k').__sp.proj({c})") for c in pis[1]['centres']]
            v1 = (s1[0][0] - s1[1][0], s1[0][1] - s1[1][1]); v2 = (s2[0][0] - s2[1][0], s2[0][1] - s2[1][1])
            cosang = abs(dot(v1, v2)) / ((dot(v1, v1) * dot(v2, v2)) ** 0.5)
            check(f'{scheme} {sid}: on screen the two π directions cross at > 60°', cosang < 0.5 and dot(v1, v1) ** 0.5 > 50 and dot(v2, v2) ** 0.5 > 50, f'{v1} {v2}')
            bad = ev(page, LAYOUT_BAD); check(f'{scheme} {sid} only π: labels clear', not bad, str(bad))
            shot(f'{sid}-only-pi'); zoom(f'z-{sid}-only-pi')
            page.click('[data-show="sigma"]'); page.wait_for_timeout(350)
            shot(f'{sid}-only-sigma')
            page.click('[data-show="all"]'); page.wait_for_timeout(200)

        print(f'== {scheme}: σ / π filter')
        for sid in SPECIES:
            page.click(f'[data-sp="{sid}"]'); page.wait_for_timeout(250)
            for show in ('sigma', 'pi'):
                page.click(f'[data-show="{show}"]'); page.wait_for_timeout(300)
                vis = [c for c in clouds(page) if c['visible']] + [o for o in page.evaluate("() => document.querySelector('.k').__sp.orbs()") if o['visible']]
                want = {'s'} if show == 'sigma' else {'p1', 'p2'}
                check(f'{scheme} {sid} only {show}: only {sorted(want)} visible', all(v['band'] in want for v in vis)
                      and (len(vis) > 0) == (show == 'sigma' or SPECIES[sid][2] > 0), str({v['band'] for v in vis}))
                t = tags(page)
                if show == 'sigma':
                    check(f'{scheme} {sid} only σ: no π labels', not any('π' in x or 'sideways' in x for x in t), str(t))
                else:
                    check(f'{scheme} {sid} only π: no σ labels', not any('σ' in x or x in SIGMA_LAB for x in t), str(t))
                    check(f'{scheme} {sid} only π: "no π bond" note ⇔ π = 0', (page.locator('.sp-nopi').count() == 1) == (SPECIES[sid][2] == 0))
                bad = ev(page, LAYOUT_BAD); check(f'{scheme} {sid} only {show}: labels clear', not bad, str(bad))
                check(f'{scheme} {sid} only {show}: button on', page.locator(f'[data-show="{show}"].on').count() == 1)
                if sid in ('C2H4', 'H2'):
                    shot(f'{sid}-only-{show}')
            page.click('[data-show="all"]'); page.wait_for_timeout(200)
        page.click('[data-sp="C2H4"]'); page.wait_for_timeout(300)
        page.locator('.sp-info').screenshot(path=str(OUT / f'z-info-C2H4{sfx}.png'))
        page.locator('.stage .hud').screenshot(path=str(OUT / f'z-hud{sfx}.png'))
        page.locator('.sp-mols').screenshot(path=str(OUT / f'z-controls{sfx}.png'))
        page.screenshot(path=str(OUT / f'z-caption{sfx}.png'), clip={**page.locator('.sp-cap').bounding_box(),
                        'height': page.locator('.sp-ms').bounding_box()['y'] + page.locator('.sp-ms').bounding_box()['height'] - page.locator('.sp-cap').bounding_box()['y']})

        if scheme == 'light':
            print('== 3D interaction')
            c0 = ev(page, CANVAS_JS)
            check('canvas is not a flat colour', c0['std'] > 8, str(c0['std']))
            box = page.locator('.stage canvas').bounding_box()
            page.mouse.move(box['x'] + 200, box['y'] + 250); page.mouse.down(); page.mouse.move(box['x'] + 330, box['y'] + 290, steps=8); page.mouse.up()
            page.wait_for_timeout(400)
            c1 = ev(page, CANVAS_JS)
            check('drag rotates (canvas hash changes)', c1['hash'] != c0['hash'])
            bad = ev(page, LAYOUT_BAD); check('after drag: labels placed again, clear', not bad, str(bad))
            shot('50-C2H4-dragged')
            page.click('[data-3d=reset]'); page.wait_for_timeout(400)
            check('复位视角 restores the view', ev(page, CANVAS_JS)['hash'] == c0['hash'])
            page.mouse.move(box['x'] + 280, box['y'] + 220); page.mouse.wheel(0, -300); page.wait_for_timeout(400)
            L = page.evaluate("() => document.querySelector('.k').__sp.layout()")
            check('wheel zoom: labels keep their screen size', all(abs(t['h'] - (22 if ' ' in t['text'] and not t['text'].startswith(('σ', 'π')) else 26)) < 2 for t in L['tags']),
                  str([(t['text'], round(t['h'], 1)) for t in L['tags']]))
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
            # slider sweep: every step changes the picture (continuous, not two states)
            hs = []
            for v in (0, 25, 50, 75, 100):
                setT(page, v); page.wait_for_timeout(60); hs.append(ev(page, CANVAS_JS)['hash'])
            check('slider 0 / 25 / 50 / 75 / 100 → 5 different pictures', len(set(hs)) == 5)
            setT(page, 50); shot('51-C2H4-t050'); setT(page, 100)
            check('no [data-clash]', page.locator('[data-clash]').count() == 0)
            check('font ≥ 12px (wide)', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))

            print('== narrow (720 px)')
            page.set_viewport_size({'width': 720, 'height': 1400}); page.wait_for_timeout(600)
            k = page.evaluate("() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('narrow: card does not overflow', k[0] <= k[1] + 1, str(k))
            check('narrow: font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            bad = []
            for sid in SPECIES:
                page.click(f'[data-sp="{sid}"]'); page.wait_for_timeout(300)
                for v in (100, 0):
                    setT(page, v); page.wait_for_timeout(150)
                    lb = ev(page, LAYOUT_BAD)
                    if lb: bad.append(f'{sid}@{v} {lb}')
                setT(page, 100)
            check('narrow: labels clear for every species at slider 0 and 1', not bad, '; '.join(bad))
            page.click('[data-sp="C2H4"]'); page.wait_for_timeout(300); shot('60-narrow-C2H4')
            page.click('[data-sp="HCN"]'); page.wait_for_timeout(300); shot('61-narrow-HCN')
        ctx.close()

    print('== fallback (CDN blocked)')
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(f'fallback: PAGEERROR {e}'))
        page.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.fallback.show', timeout=20000); page.wait_for_timeout(200)
        sfx = '' if scheme == 'light' else '-dark'
        check(f'{scheme} fallback shown, data-3d=fallback', page.get_attribute('.k', 'data-3d') == 'fallback')
        txt = page.evaluate("() => [...document.querySelectorAll('.sp-fb svg text')].map(t => t.textContent).join(' | ')")
        check(f'{scheme} fallback SVG: C₂H₄ σ + π labels', all(s in txt for s in ('σ (sp²–sp²)', 'π', 'sideways overlap of adjacent p orbitals',
                                                                      'direct (end-on) overlap', 'molecular plane')), txt)
        check(f'{scheme} fallback: 3 π/σ ellipses on the axis (π above, σ on, π below)', page.locator('.sp-fb ellipse').count() == 5)
        check(f'{scheme} fallback: no [data-clash]', page.locator('[data-clash]').count() == 0,
              str(page.evaluate("() => [...document.querySelectorAll('[data-clash]')].map(e => e.textContent)")))
        page.click('[data-sp="HCN"]')
        check(f'{scheme} fallback: counts panel still works', page.inner_text('.sp-ns') == '2' and page.inner_text('.sp-np') == '2')
        page.click('[data-sp="C2H4"]')
        page.locator('.k').screenshot(path=str(OUT / f'70-fallback{sfx}.png'))
        page.locator('.sp-fb').screenshot(path=str(OUT / f'z-fallback{sfx}.png'))
        if scheme == 'light':
            page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(300)
            check('fallback narrow: SVG text ≥ 12px', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)[:5]))
            check('fallback narrow: font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
