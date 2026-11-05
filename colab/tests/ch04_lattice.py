"""ch04 lattice cell test (3D): nine lattices — geometry of K3.lattice, one renderer, hover neighbours,
delocalised-electron animation (pause / off-screen), real-size switch, dark, 720 px, CDN-blocked fallback.

usage: uv run --with playwright python -I colab/tests/ch04_lattice.py $COLAB_TMP/cells/ch04-lattice.html <shots-dir>
(build first: python3 tools/build_colab.py ch04 --cell lattice --3d)
"""
import sys, math, json
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']
KINDS = ['nacl', 'mgo', 'cu', 'diamond', 'graphite', 'sio2', 'i2', 'c60', 'ice']

CANVAS_JS = """() => { const c=document.querySelector('.stage canvas'); if(!c) return null;
  const g=document.createElement('canvas'); g.width=c.width; g.height=c.height; const x=g.getContext('2d'); x.drawImage(c,0,0);
  const d=x.getImageData(0,0,g.width,g.height).data; let s=0,s2=0,n=0;
  for(let i=0;i<d.length;i+=16){const v=d[i]+d[i+1]+d[i+2]; s+=v; s2+=v*v; n++;}
  const m=s/n; const u=c.toDataURL(); return {mean:m, std:Math.sqrt(s2/n-m*m), hash:u.length+':'+u.slice(-300), corner:[d[0],d[1],d[2]]}; }"""


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def shot(page, sel, path):
    """element screenshot via a page clip: Locator.screenshot waits for 'stable' (two rAFs), which
    hangs when several headless Chromes share the machine"""
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def dist(p, q):
    return math.dist(p, q)


def angle(c, p, q):
    u = [p[i] - c[i] for i in range(3)]; v = [q[i] - c[i] for i in range(3)]
    return math.degrees(math.acos(sum(u[i] * v[i] for i in range(3)) / math.hypot(*u) / math.hypot(*v)))


def adjacency(d, kinds):
    adj = [[] for _ in d['atoms']]
    for b in d['bonds']:
        if b['kind'] in kinds:
            adj[b['a']].append(b['b']); adj[b['b']].append(b['a'])
    return adj


def rings(adj, size):
    """number of simple cycles of the given length (each counted once)"""
    n = 0
    for s in range(len(adj)):
        stack = [(s, [s])]
        while stack:
            v, path = stack.pop()
            for w in adj[v]:
                if w == s and len(path) == size:
                    n += 1
                elif w > s and w not in path and len(path) < size:
                    stack.append((w, path + [w]))
    return n // 2


def central(d, pred=lambda a: True):
    """index of the atom nearest the middle of the lattice (an inner atom: full set of neighbours)"""
    ps = [a['p'] for a in d['atoms']]
    c = [sum(p[i] for p in ps) / len(ps) for i in range(3)]
    cand = [i for i, a in enumerate(d['atoms']) if pred(a)]
    return min(cand, key=lambda i: dist(ps[i], c))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=ARGS)
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1100, 'height': 1250}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.k[data-3d]', timeout=60000); page.wait_for_timeout(500)
        check(f'{scheme}: 3D ready', page.get_attribute('.k', 'data-3d') == 'ready', page.get_attribute('.k', 'data-3d'))

        def data():
            return page.evaluate('() => document.querySelector(".k").__lat.data()')

        def pick(k, n=None):
            page.click(f'[data-k="{k}"]')
            if n:
                page.click(f'[data-n="{n}"]')
            page.wait_for_timeout(250)

        if scheme == 'dark':
            for k in ['nacl', 'graphite', 'diamond', 'ice', 'c60']:
                pick(k, 1)
                st = page.evaluate(CANVAS_JS)
                check(f'dark {k}: canvas background is dark', sum(st['corner']) < 200, str(st['corner']))
                check(f'dark {k}: canvas not blank', st['std'] > 8, f"{st['std']:.1f}")
                shot(page, '.k', OUT / f'dark-{k}.png')
            pick('cu', 1); shot(page, '.k', OUT / 'dark-cu.png')
            ctx.close()
            continue

        s1 = page.evaluate(CANVAS_JS)
        check('canvas not blank', s1 and s1['std'] > 8, json.dumps(s1 and {k: s1[k] for k in ('mean', 'std')}))
        box = page.locator('.stage canvas').bounding_box()
        page.mouse.move(box['x'] + 120, box['y'] + 120); page.mouse.down()
        page.mouse.move(box['x'] + 300, box['y'] + 180, steps=8); page.mouse.up(); page.wait_for_timeout(150)
        check('drag changes the view', page.evaluate(CANVAS_JS)['hash'] != s1['hash'])
        page.click('[data-3d=reset]'); page.wait_for_timeout(100)
        check('reset returns to the start view', page.evaluate(CANVAS_JS)['hash'] == s1['hash'])

        print('== geometry of every lattice (n = 1 and 2)')
        # NaCl / MgO: every inner ion has 6 neighbours of the other charge at a/2
        for k, a in (('nacl', 0.564), ('mgo', 0.421)):
            pick(k, 2); d = data()
            i = central(d); nb = d['info']['nb'][i]; ion = d['atoms'][i]['ion']
            check(f'{k}: inner ion has 6 nearest neighbours', len(nb) == 6, str(len(nb)))
            check(f'{k}: all 6 of opposite charge', all(d['atoms'][j]['ion'] * ion < 0 for j in nb))
            check(f'{k}: at a/2 = {a / 2:.3f} nm', all(abs(dist(d['atoms'][j]['p'], d['atoms'][i]['p']) - a / 2) < 1e-6 for j in nb))
            inner = [x for x, a_ in enumerate(d['atoms']) if len(d['info']['nb'][x]) == 6]
            check(f'{k}: every 6-coordinate ion has only opposite neighbours',
                  all(all(d['atoms'][j]['ion'] * d['atoms'][x]['ion'] < 0 for j in d['info']['nb'][x]) for x in inner), str(len(inner)))
        pick('nacl', 1); d = data()
        rr = {a['el']: a['rr'] for a in d['atoms']}
        check('NaCl radii Na⁺ 0.095, Cl⁻ 0.181', rr == {'Na': 0.095, 'Cl': 0.181}, str(rr))
        check('NaCl drawn at 0.55 × real size', all(abs(a['r'] / a['rr'] - 0.55) < 1e-9 for a in d['atoms']))
        pick('mgo', 1); d = data()
        rr = {a['el']: a['rr'] for a in d['atoms']}
        check('MgO radii Mg²⁺ 0.065, O²⁻ 0.140', rr == {'Mg': 0.065, 'O': 0.14}, str(rr))
        # copper: 12 nearest neighbours
        pick('cu', 2); d = data()
        i = central(d); nb = d['info']['nb'][i]
        check('Cu: inner ion has 12 nearest neighbours', len(nb) == 12, str(len(nb)))
        check('Cu: no bonds drawn (metallic bonding is not pairwise)', len(d['bonds']) == 0)
        # diamond: 4 bonds, 109.5°
        pick('diamond', 2); d = data()
        adj = adjacency(d, ['cov']); i = central(d, lambda a: True)
        i = min((x for x in range(len(adj)) if len(adj[x]) == 4), key=lambda x: dist(d['atoms'][x]['p'], d['atoms'][i]['p']))
        angs = [angle(d['atoms'][i]['p'], d['atoms'][u]['p'], d['atoms'][v]['p']) for x, u in enumerate(adj[i]) for v in adj[i][x + 1:]]
        check('diamond: inner C has 4 covalent bonds', len(adj[i]) == 4)
        check('diamond: all 6 bond angles 109.5°', len(angs) == 6 and all(abs(t - 109.47) < 0.05 for t in angs), str([round(t, 2) for t in angs]))
        check('diamond: C–C 0.154 nm', all(abs(dist(d['atoms'][i]['p'], d['atoms'][j]['p']) - 0.1546) < 0.001 for j in adj[i]))
        check('diamond: no C has more than 4 bonds, none floats', max(map(len, adj)) == 4 and min(map(len, adj)) >= 1)
        # graphite: 3 in-layer bonds, gap / bond ≈ 2.36, vdw only between neighbouring layers
        pick('graphite', 2); d = data()
        adj = adjacency(d, ['cov'])
        check('graphite: every covalent bond inside one layer', all(d['atoms'][b_['a']]['layer'] == d['atoms'][b_['b']]['layer'] for b_ in d['bonds'] if b_['kind'] == 'cov'))
        i = min((x for x in range(len(adj)) if len(adj[x]) == 3), key=lambda x: dist(d['atoms'][x]['p'], d['atoms'][central(d)]['p']))
        angs = [angle(d['atoms'][i]['p'], d['atoms'][u]['p'], d['atoms'][v]['p']) for x, u in enumerate(adj[i]) for v in adj[i][x + 1:]]
        check('graphite: inner C has 3 bonds at 120°', len(adj[i]) == 3 and all(abs(t - 120) < 0.05 for t in angs), str(angs))
        check('graphite: max 3 bonds', max(map(len, adj)) == 3)
        bl = dist(d['atoms'][i]['p'], d['atoms'][adj[i][0]]['p'])
        vd = [b_ for b_ in d['bonds'] if b_['kind'] == 'vdw']
        gaps = {round(dist(d['atoms'][b_['a']]['p'], d['atoms'][b_['b']]['p']), 4) for b_ in vd}
        check('graphite: layer gap 0.335, C–C 0.142, ratio ≈ 2.36', gaps == {0.335} and abs(bl - 0.142) < 1e-4 and abs(0.335 / bl - 2.36) < 0.01, f'{gaps} {bl}')
        check('graphite: id-id lines only between neighbouring layers', vd and all(abs(d['atoms'][b_['a']]['layer'] - d['atoms'][b_['b']]['layer']) == 1 for b_ in vd))
        check('graphite: n = 2 → 4 layers', len({a['layer'] for a in d['atoms']}) == 4)
        # ABAB: half the atoms of layer 1 sit over layer-0 atoms
        L0 = [a['p'] for a in d['atoms'] if a['layer'] == 0]; L1 = [a['p'] for a in d['atoms'] if a['layer'] == 1]
        over = sum(1 for q in L1 if any(abs(q[0] - r[0]) < 1e-6 and abs(q[2] - r[2]) < 1e-6 for r in L0))
        check('graphite: ABAB — about half of layer B is over layer-A atoms', 0.35 < over / len(L1) < 0.65, f'{over}/{len(L1)}')
        L2 = [a['p'] for a in d['atoms'] if a['layer'] == 2]
        check('graphite: layer 3 repeats layer 1 (A)', all(any(abs(q[0] - r[0]) < 1e-6 and abs(q[2] - r[2]) < 1e-6 for r in L0) for q in L2[:20]))
        # SiO2
        pick('sio2', 2); d = data()
        adj = adjacency(d, ['cov']); at = d['atoms']
        si4 = [x for x, a in enumerate(at) if a['el'] == 'Si' and len(adj[x]) == 4]
        check('SiO₂: inner Si has 4 O', si4 and all(all(at[j]['el'] == 'O' for j in adj[x]) for x in si4), str(len(si4)))
        check('SiO₂: every O bonded to exactly 2 Si', all(len(adj[x]) == 2 and all(at[j]['el'] == 'Si' for j in adj[x]) for x, a in enumerate(at) if a['el'] == 'O'))
        x = si4[0]
        angs = [angle(at[x]['p'], at[u]['p'], at[v]['p']) for q, u in enumerate(adj[x]) for v in adj[x][q + 1:]]
        check('SiO₂: SiO₄ tetrahedral (109.5°), Si–O 0.161', all(abs(t - 109.47) < 0.05 for t in angs) and all(abs(dist(at[x]['p'], at[j]['p']) - 0.161) < 1e-6 for j in adj[x]))
        # I2
        for n in (1, 2):
            pick('i2', n); d = data(); at = d['atoms']
            cov = [dist(at[b_['a']]['p'], at[b_['b']]['p']) for b_ in d['bonds'] if b_['kind'] == 'cov']
            inter = min(dist(at[u]['p'], at[v]['p']) for u in range(len(at)) for v in range(u + 1, len(at)) if at[u]['mol'] != at[v]['mol'])
            check(f'I₂ n={n}: I–I 0.267 nm in every molecule', all(abs(c - 0.267) < 1e-6 for c in cov) and len(cov) * 2 == len(at))
            check(f'I₂ n={n}: inside molecule (0.267) < between molecules (≈ 0.35)', 0.267 < inter and abs(inter - 0.35) < 0.01, f'{inter:.3f}')
            vd = [dist(at[b_['a']]['p'], at[b_['b']]['p']) for b_ in d['bonds'] if b_['kind'] == 'vdw']
            check(f'I₂ n={n}: id-id lines join different molecules, 0.35–0.40 nm', vd and all(0.349 < v < 0.401 for v in vd)
                  and all(at[b_['a']]['mol'] != at[b_['b']]['mol'] for b_ in d['bonds'] if b_['kind'] == 'vdw'))
        # C60
        pick('c60', 1); d = data(); adj = adjacency(d, ['cov'])
        check('C₆₀: 60 atoms, 90 bonds', len(d['atoms']) == 60 and len(d['bonds']) == 90, f"{len(d['atoms'])} / {len(d['bonds'])}")
        check('C₆₀: every C bonded to 3', all(len(x) == 3 for x in adj))
        check('C₆₀: 12 five-membered rings', rings(adj, 5) == 12, str(rings(adj, 5)))
        check('C₆₀: 20 six-membered rings', rings(adj, 6) == 20, str(rings(adj, 6)))
        pick('c60', 2); d = data()
        check('C₆₀ n=2: 14 molecules on a face-centred cubic cell', d['info']['molecules'] == 14 and len(d['atoms']) == 840)
        # ice
        for n in (1, 2):
            pick('ice', n); d = data(); at = d['atoms']
            cov = {}; hb = {}
            for b_ in d['bonds']:
                if b_['kind'] == 'cov':
                    o = b_['a'] if at[b_['a']]['el'] == 'O' else b_['b']; cov[o] = cov.get(o, 0) + 1
                    check_len = dist(at[b_['a']]['p'], at[b_['b']]['p'])
                    if abs(check_len - 0.10) > 1e-6:
                        cov['bad'] = check_len
                if b_['kind'] == 'hb':
                    hb[b_['b']] = hb.get(b_['b'], 0) + 1
                    if abs(dist(at[b_['a']]['p'], at[b_['b']]['p']) - 0.176) > 1e-6:
                        hb['bad'] = 1
            Os = [x for x, a in enumerate(at) if a['el'] == 'O']
            deg = d['info']['degO']
            check(f'ice n={n}: every O has 2 covalent H (H₂O)', all(cov.get(x) == 2 for x in Os) and 'bad' not in cov, str({x: cov.get(x) for x in Os[:6]}))
            inner = [x for x in Os if deg[x] == 4]
            check(f'ice n={n}: every inner O: 2 covalent + 2 hydrogen bonds', inner and all(hb.get(x) == 2 for x in inner) and 'bad' not in hb, f'{len(inner)} inner')
            check(f'ice n={n}: H count = 2 × O count', sum(1 for a in at if a['el'] == 'H') == 2 * len(Os))
            check(f'ice n={n}: every H has one covalent O and at most one hydrogen bond',
                  all(sum(1 for b_ in d['bonds'] if b_['kind'] == 'cov' and x in (b_['a'], b_['b'])) == 1 and
                      sum(1 for b_ in d['bonds'] if b_['kind'] == 'hb' and b_['a'] == x) <= 1 for x, a in enumerate(at) if a['el'] == 'H'))
            oo = {round(dist(at[u]['p'], at[v]['p']), 3) for u in Os for v in Os if u < v and dist(at[u]['p'], at[v]['p']) < 0.3}
            check(f'ice n={n}: O···O 0.276 nm', oo == {0.276}, str(oo))

        print('== n = 1 → 3 grows every lattice')
        counts = {}
        for k in KINDS:
            c = []
            for n in (1, 2, 3):
                pick(k, n); c.append(len(data()['atoms']))
            counts[k] = c
            check(f'{k}: atoms grow with n', c[0] < c[1] < c[2], str(c))
        print(json.dumps(counts))

        print('== one renderer, switching disposes')
        check('one canvas in the stage', page.locator('.stage canvas').count() == 1)
        for k in KINDS:
            pick(k, 2)
        m1 = page.evaluate('() => document.querySelector(".k").__lat.mem()')
        for k in KINDS:
            pick(k, 2)
        m2 = page.evaluate('() => document.querySelector(".k").__lat.mem()')
        check('GPU geometries do not pile up over switches', m2['geo'] <= m1['geo'], f'{m1} → {m2}')
        check('still one canvas after 18 switches', page.locator('.stage canvas').count() == 1)

        print('== screenshots: every lattice at n = 1, and NaCl / diamond / ice at n = 2')
        for k in KINDS:
            pick(k, 1)
            st = page.evaluate(CANVAS_JS)
            check(f'{k}: canvas not blank', st['std'] > 8, f"{st['std']:.1f}")
            check(f'{k}: info card + legend + hud filled', len(page.inner_text('.lt-info')) > 60 and page.locator('.lt-legend span').count() >= 2 and len(page.inner_text('.hud')) > 10)
            shot(page, '.k', OUT / f'{k}-1.png')
        for k in ('nacl', 'diamond', 'ice', 'graphite', 'c60', 'sio2'):
            pick(k, 2); shot(page, '.lt-main', OUT / f'{k}-2.png')
        pick('c60', 3); shot(page, '.lt-main', OUT / 'c60-3.png')
        pick('nacl', 3); shot(page, '.lt-main', OUT / 'nacl-3.png')

        print('== info texts')
        pick('graphite', 1)
        check('graphite info: weak id-id forces between layers', 'weak id-id forces' in page.inner_text('.lt-info') and 'between layers' in page.inner_text('.hud'))
        pick('sio2', 1)
        check('SiO₂ caption: quartz differs, 4 O per Si / 2 Si per O', 'quartz' in page.inner_text('.lt-info') and '每个 Si 4 个 O、每个 O 2 个 Si' in page.inner_text('.lt-info'))
        pick('i2', 1)
        check('I₂ info: 0.27 nm < 0.35 nm', '0.27 nm' in page.inner_text('.lt-info') and '0.35 nm' in page.inner_text('.lt-info'))
        pick('c60', 1)
        check('C₆₀ info: 12 pentagons + 20 hexagons', '12 pentagons + 20 hexagons' in page.inner_text('.lt-info'))
        check('buttons: 4 groups, 9 structures', page.locator('.lt-grp').count() == 4 and page.locator('[data-k]').count() == 9)
        check('real-size / pause buttons only where they apply',
              not page.is_visible('.lt-real') and not page.is_visible('.lt-pause'))

        print('== hover (Raycaster) highlights neighbours')
        for k, n, want in (('nacl', 1, '6 个最近的 Cl⁻ ion'), ('cu', 2, '12 个最近的 ions'), ('diamond', 2, '4 个 covalent bond'),
                           ('ice', 2, '2 个 covalent O–H + 2 个 hydrogen bond')):
            pick(k, n); d = data()
            if k == 'nacl':
                i = central(d)
            elif k == 'ice':
                i = central(d, lambda a: a['el'] == 'O')
                i = min((x for x, a in enumerate(d['atoms']) if a['el'] == 'O' and d['info']['degO'][x] == 4), key=lambda x: dist(d['atoms'][x]['p'], d['atoms'][i]['p']))
            else:
                i = central(d)
                i = min((x for x in range(len(d['atoms'])) if len(d['info']['nb'][x]) == (12 if k == 'cu' else 4)), key=lambda x: dist(d['atoms'][x]['p'], d['atoms'][i]['p']))
            # turn the view until the atom is the front-most thing under its own screen position
            sp = None
            for rx, ry in ((None, None), (0.2, 0.3), (-0.4, 0.9), (0.9, -1.3), (0.1, 2.2), (-1.0, -0.2), (0.6, 1.6)):
                if rx is not None:
                    page.evaluate(f'() => {{ const a = document.querySelector(".k").__lat.api; a.rx = {rx}; a.ry = {ry}; a.view(); }}')
                sp = page.evaluate(f'() => document.querySelector(".k").__lat.screen({i})')
                if sp['hit'] == i:
                    break
            check(f'{k}: atom {i} reachable by the pointer', sp['hit'] == i, str(sp))
            before = page.evaluate(CANVAS_JS)['hash']
            page.mouse.move(box['x'] + sp['x'] - 30, box['y'] + sp['y'] - 30)
            page.mouse.move(box['x'] + sp['x'], box['y'] + sp['y'], steps=3); page.wait_for_timeout(120)
            hv = page.evaluate('() => document.querySelector(".k").__lat.hovered()')
            tip = page.evaluate('() => document.querySelector(".k").__lat.tip()')
            check(f'{k}: hover picks the atom', hv == i, f'{hv} vs {i}')
            check(f'{k}: tooltip names it and its neighbours', want in tip, tip)
            check(f'{k}: highlight changes the picture', page.evaluate(CANVAS_JS)['hash'] != before)
            shot(page, '.stage', OUT / f'hover-{k}.png')
            tb = page.eval_on_selector('.lt-tip', 'e => { const r = e.getBoundingClientRect(), s = e.parentNode.getBoundingClientRect(); return [r.left - s.left, r.top - s.top, s.right - r.right, s.bottom - r.bottom]; }')
            check(f'{k}: tooltip inside the stage', min(tb) >= 0, str(tb))
            page.mouse.move(box['x'] + 5, box['y'] + box['height'] - 5); page.wait_for_timeout(80)
            check(f'{k}: moving off the atoms clears the tooltip', page.evaluate('() => document.querySelector(".k").__lat.tip()') == '')
            page.click('[data-3d=reset]')

        print('== copper: delocalised electrons move; pause; off-screen')
        pick('cu', 1)
        check('pause button shown for copper', page.is_visible('.lt-pause'))
        e0 = page.evaluate('() => document.querySelector(".k").__lat.elec()')
        check('electrons drawn (more than ions)', e0 and len(e0) > len(data()['atoms']), str(len(e0 or [])))
        page.evaluate('() => document.querySelector(".k").__lat.tick(30)')
        e1 = page.evaluate('() => document.querySelector(".k").__lat.elec()')
        moved = sum(1 for a, c in zip(e0, e1) if dist(a, c) > 1e-4)
        check('tick(30): every electron moved', moved == len(e0), f'{moved}/{len(e0)}')
        samples = []
        for _ in range(6):   # swiftshader on a busy machine sometimes skips a frame: ask for 4 distinct of 6
            samples.append(page.evaluate('() => document.querySelector(".k").__lat.elec()')[0]); page.wait_for_timeout(250)
        check('rAF animation runs on its own (≥ 4 of 6 sampled frames differ)', len({tuple(round(v, 6) for v in s) for s in samples}) >= 4, str(samples))
        lo = [min(p[i] for p in e1) for i in range(3)]
        hi = [max(p[i] for p in e1) for i in range(3)]
        R = page.evaluate('() => { const a = document.querySelector(".k").__lat; return a.api.dist; }')
        check('electrons stay inside the lattice box', max(map(abs, lo + hi)) < 2.0, f'{lo} {hi}')
        page.click('.lt-pause'); page.wait_for_timeout(100)
        a = page.evaluate('() => document.querySelector(".k").__lat.elec()'); page.wait_for_timeout(400)
        c = page.evaluate('() => document.querySelector(".k").__lat.elec()')
        check('paused: electrons stand still', a == c)
        check('pause button relabelled', '继续' in page.inner_text('.lt-pause'))
        page.click('.lt-pause'); page.wait_for_timeout(300)
        check('resumed: electrons move again', page.evaluate('() => document.querySelector(".k").__lat.elec()') != c)
        page.evaluate('() => { const s = document.createElement("div"); s.style.height = "3000px"; s.id = "spacer"; document.body.appendChild(s); window.scrollTo(0, 2600); }')
        page.wait_for_timeout(400)
        a = page.evaluate('() => document.querySelector(".k").__lat.elec()'); page.wait_for_timeout(400)
        c = page.evaluate('() => document.querySelector(".k").__lat.elec()')
        check('off-screen (IntersectionObserver): electrons stop', a == c)
        page.evaluate('() => { window.scrollTo(0, 0); document.getElementById("spacer").remove(); }'); page.wait_for_timeout(400)
        a = page.evaluate('() => document.querySelector(".k").__lat.elec()'); page.wait_for_timeout(300)
        check('back on screen: electrons move', page.evaluate('() => document.querySelector(".k").__lat.elec()') != a)
        page.click('.lt-pause'); page.wait_for_timeout(100)   # freeze for stable screenshots
        shot(page, '.lt-main', OUT / 'cu-electrons.png')
        page.click('.lt-pause')

        print('== real size switch')
        for k in ('nacl', 'cu'):
            pick(k, 1)
            if k == 'cu':
                page.click('.lt-pause'); page.wait_for_timeout(100)   # moving electrons would change every frame
            h0 = page.evaluate(CANVAS_JS)['hash']
            page.click('.lt-real'); page.wait_for_timeout(200)
            check(f'{k}: real-size button on, picture changes', 'on' in page.get_attribute('.lt-real', 'class') and page.evaluate(CANVAS_JS)['hash'] != h0)
            shot(page, '.lt-main', OUT / f'{k}-real.png')
            page.click('.lt-real'); page.wait_for_timeout(200)
            if k == 'cu':   # the rebuild re-seeds the electrons, so compare the button state only
                check('cu: real-size button off again', 'on' not in (page.get_attribute('.lt-real', 'class') or ''))
                page.click('.lt-pause')
            else:
                check(f'{k}: switching back restores the picture', page.evaluate(CANVAS_JS)['hash'] == h0)

        print('== zoomed details (z ≥ 2)')
        def zoom_shot(name, fx, fy, fw, fh):
            sb = page.eval_on_selector('.stage', 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height}; }')
            page.screenshot(path=str(OUT / f'{name}.png'), full_page=True,
                            clip={'x': sb['x'] + sb['w'] * fx, 'y': sb['y'] + sb['h'] * fy, 'width': sb['w'] * fw, 'height': sb['h'] * fh})
        for k in ('graphite', 'ice', 'i2', 'sio2'):
            pick(k, 1)
            page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
            for _ in range(5):
                page.mouse.wheel(0, -200); page.wait_for_timeout(60)
            page.mouse.move(box['x'] + 3, box['y'] + box['height'] - 3); page.wait_for_timeout(150)
            zoom_shot(f'zoom-{k}', 0.2, 0.08, 0.6, 0.88)
            page.click('[data-3d=reset]')
        shot(page, '.lt-legend', OUT / 'zoom-legend.png')
        shot(page, '.hud', OUT / 'zoom-hud.png')
        shot(page, '.lt-info', OUT / 'zoom-info.png')
        shot(page, '.lt-pick', OUT / 'zoom-buttons.png')

        print('== auto-rotate')
        h = page.evaluate(CANVAS_JS)['hash']; page.click('[data-3d=spin]'); page.wait_for_timeout(400)
        check('auto-rotate turns the view', page.evaluate(CANVAS_JS)['hash'] != h)
        page.click('[data-3d=spin]')

        print('== narrow (720 px)')
        page.set_viewport_size({'width': 720, 'height': 1600}); page.wait_for_timeout(400)
        pick('graphite', 1)
        ov = page.evaluate('() => { const k=document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check('no horizontal overflow at 720 px', ov <= 0, str(ov))
        fs = page.evaluate('''() => Math.min(...[...document.querySelectorAll('.k .lt-legend span, .k .hud, .k .lt-info li, .k .lt-note, .k .lt-gl, .k .lt-nt, .k .lt-tip, .k h3 .faint')]
            .map(e => parseFloat(getComputedStyle(e).fontSize)))''')
        check('smallest text ≥ 12 px', fs >= 12, str(fs))
        st = page.evaluate(CANVAS_JS)
        check('720 px: canvas not blank', st['std'] > 8)
        check('canvas follows the stage width', abs(page.eval_on_selector('.stage canvas', 'c => c.clientWidth') - page.eval_on_selector('.stage', 's => s.clientWidth')) <= 2)
        shot(page, '.k', OUT / 'card-720.png')
        check('no K.label clash', page.locator('[data-clash]').count() == 0)
        ctx.close()

    print('== fallback (CDN blocked)')
    ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2)
    ctx.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
    page = ctx.new_page()
    page.on('pageerror', lambda e: errors.append(f'fallback: PAGEERROR {e}'))
    page.goto(PAGE.as_uri())
    page.wait_for_selector('.fallback.show', timeout=30000)
    check('fallback shown, data-3d=fallback', page.get_attribute('.k', 'data-3d') == 'fallback')
    check('fallback: table of 9 structures', page.locator('.lt-fbtab tbody tr').count() == 9)
    check('fallback: NaCl and graphite drawings', page.locator('.lt-fb-nacl circle').count() == 25 and page.locator('.lt-fb-gr circle').count() > 20)
    check('fallback: stage, buttons and info card hidden', not page.is_visible('.stage') and not page.is_visible('.lt-pick') and not page.is_visible('.lt-tools') and not page.is_visible('.lt-info'))
    shot(page, '.k', OUT / 'fallback.png')
    ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
