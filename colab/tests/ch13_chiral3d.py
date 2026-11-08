"""ch13 chiral3d cell test (3D): optical isomerism, enantiomers, chiral centre (*),
butan-2-ol (chiral) vs 2-hydroxypropanoic acid (lactic acid, chiral) vs propan-2-ol (achiral control),
left molecule and right mirror image separated by semi-transparent mirror plane (x=0),
synchronous rotation (both slot hashes change), try to superimpose animation (overlay t=0..1),
chiral molecules cannot superimpose (at most 2 of the 4 groups ever coincide, the other 2 are swapped —
a proper rotation cannot map 3 tetrahedral directions onto their mirror images -> 不能重合 non-superimposable),
propan-2-ol completely superimposes (能完全重合 superimposable), plane-polarised light banner with rotation arrows,
four group colors distinguishable in light & dark, 720px no overflow, fallback when CDN blocked, console 0 errors.

usage:
  TMPDIR=/mnt/ai-shared/che_tmp/organic/prof/chiral3d /home/lkh/.local/bin/uv run --with playwright \
    python -I colab/tests/ch13_chiral3d.py /mnt/ai-shared/che_tmp/organic/cells/ch13-chiral3d.html \
    /mnt/ai-shared/che_tmp/organic/shots/chiral3d
"""
import math
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

CHROMIUM = '/usr/bin/chromium'
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']

results, errors = [], []


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def shot(page, sel, path):
    """Clip-based element screenshot (avoids Locator.screenshot rAF stability hang)."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); '
        'return {x: Math.max(0, r.x + scrollX), y: Math.max(0, r.y + scrollY), width: r.width, height: r.height}; }',
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


def shot_clip(page, sel, fx0, fy0, fx1, fy1, path):
    """screenshot of the fraction [fx0, fx1] × [fy0, fy1] of an element"""
    bb = page.eval_on_selector(
        sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height}; }')
    clip = {'x': bb['x'] + bb['w'] * fx0, 'y': bb['y'] + bb['h'] * fy0,
            'width': bb['w'] * (fx1 - fx0), 'height': bb['h'] * (fy1 - fy0)}
    page.screenshot(path=str(path), clip=clip, full_page=True)


def ev(page, js, *a):
    return page.evaluate(js, *a)


CANVAS_JS = """() => {
  const c = document.querySelector('.stage canvas');
  if (!c) return null;
  const u = c.toDataURL();
  return { hash: u.length + ':' + u.slice(-300) };
}"""


def chash(page):
    return ev(page, CANVAS_JS)['hash']


def slot_hash(page, k):
    return ev(page, f"() => document.querySelector('.k').__ch.slotHash({k})")


def tab(page, m):
    sel = f'.ch-modes button[data-tab="{m}"]'
    if page.locator(sel).count():
        page.click(sel)
        page.wait_for_timeout(250)


def set_overlay(page, t):
    ev(page, f"() => document.querySelector('.k').__ch.setOverlay({t})")
    page.wait_for_timeout(100)


LAYOUT_BAD_JS = """() => {
  const L = document.querySelector('.k').__ch.layout();
  if (!L) return ['no layout'];
  const bad = [];
  const rc = (r, c, m) => {
    const dx = Math.max(r.x - c.x, 0, c.x - (r.x + r.w)), dy = Math.max(r.y - c.y, 0, c.y - (r.y + r.h));
    return Math.hypot(dx, dy) < c.r - (m || 0);
  };
  L.slots.forEach((S, k) => {
    S.circles.forEach(c => {
      L.overlays.forEach(o => {
        if (rc(o, c, 0.5)) bad.push('slot' + k + ' ' + S.id + ' ' + c.kind + (c.el || '') + ' under overlay "' + o.text.slice(0, 18) + '"');
      });
      if (L.hud && rc(L.hud, c, 0.5)) bad.push('slot' + k + ' ' + c.kind + ' under HUD');
      if (c.x - c.r < 0 || c.x + c.r > L.W || c.y - c.r < 0 || c.y + c.r > L.H) bad.push('slot' + k + ' ' + c.kind + ' outside stage');
    });
  });
  /* overlays never overlap each other or the HUD */
  L.overlays.forEach((a, i) => {
    L.overlays.forEach((b, j) => {
      if (j > i && a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) {
        bad.push('overlay "' + a.text.slice(0, 12) + '" overlaps "' + b.text.slice(0, 12) + '"');
      }
    });
    if (L.hud && a.y < L.hud.y + L.hud.h) bad.push('overlay "' + a.text.slice(0, 12) + '" under HUD');
    if (a.x < 0 || a.x + a.w > L.W + 0.5 || a.y + a.h > L.H + 0.5) bad.push('overlay "' + a.text.slice(0, 12) + '" outside stage');
  });
  /* visible tags never overlap each other (they are drawn on top of everything) */
  const vt = L.tags.filter(t => t.visible);
  vt.forEach((a, i) => vt.forEach((b, j) => {
    if (j > i && a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h)
      bad.push('tag overlaps tag (slot' + a.slot + (a.pair ? ' pair' : '') + ' / slot' + b.slot + (b.pair ? ' pair' : '') + ')');
  }));
  /* atom tags: font ≥ 12 px and inside stage */
  L.tags.filter(t => t.visible).forEach(t => {
    if (t.x < 0 || t.y < 0 || t.x + t.w > L.W || t.y + t.h > L.H) bad.push('tag outside stage');
    if (t.h * 0.6875 < 12) bad.push('tag font < 12px (' + (t.h * 0.6875).toFixed(1) + ')');
    L.overlays.forEach(o => {
      if (t.x < o.x + o.w && o.x < t.x + t.w && t.y < o.y + o.h && o.y < t.y + t.h) bad.push('tag under overlay');
    });
  });
  return bad;
}"""

SMALL_JS = """() => {
  const out = [];
  for (const e of document.querySelectorAll('.k *')) {
    const st = getComputedStyle(e);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    if (!e.getClientRects().length) continue;
    if (e.closest('svg')) continue;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own && parseFloat(st.fontSize) < 12) out.push(e.tagName + '.' + e.className + ':' + e.textContent.trim().slice(0, 24));
  }
  return out;
}"""

SVG_SMALL_JS = """() => {
  const out = [];
  for (const s of document.querySelectorAll('.k svg')) {
    const vb = s.viewBox.baseVal;
    if (!vb || !vb.width) continue;
    const w = s.getBoundingClientRect().width;
    if (!w) continue;
    const k = w / vb.width;
    for (const t of s.querySelectorAll('text')) {
      if (!t.getClientRects().length) continue;
      const f = parseFloat(getComputedStyle(t).fontSize) * k;
      if (f < 12) out.push(t.textContent + ':' + f.toFixed(1));
    }
  }
  return out;
}"""

SVG_OUTSIDE_JS = """() => {
  const out = [];
  for (const s of document.querySelectorAll('.k svg')) {
    const v = s.viewBox.baseVal;
    if (!v || !v.width || !s.getBoundingClientRect().width) continue;
    for (const t of s.querySelectorAll('text')) {
      const b = t.getBBox();
      if (!b.width) continue;
      if (b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5) out.push(t.textContent);
    }
  }
  return out;
}"""

CLASH_JS = "() => [...document.querySelectorAll('.k [data-clash]')].map(e => e.textContent)"


def v_sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def v_len(a):
    return math.sqrt(sum(x * x for x in a))


def angle(a, c, b):
    u, w = v_sub(a, c), v_sub(b, c)
    return math.degrees(math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(u, w)) / (v_len(u) * v_len(w))))))


def mirror_err(page):
    """max distance between each right atom and the reflection of its left partner through the drawn mirror"""
    w = ev(page, "() => document.querySelector('.k').__ch.world()")
    P, N = w['mirror']['p'], w['mirror']['n']
    worst = 0.0
    for a, b in zip(w['slots'][0], w['slots'][1]):
        d = sum((a[i] - P[i]) * N[i] for i in range(3))
        r = [a[i] - 2 * d * N[i] for i in range(3)]
        worst = max(worst, v_len(v_sub(r, b)))
    return worst


def screen_pos(page, k):
    L = ev(page, "() => document.querySelector('.k').__ch.layout()")
    return [(c['x'], c['y']) for c in L['slots'][k]['circles']]


def moved(a, b):
    return max(math.hypot(p[0] - q[0], p[1] - q[1]) for p, q in zip(a, b))


def mapping(page):
    return ev(page, "() => document.querySelector('.k').__ch.mapping()")


def geometry_checks(page):
    print('== geometry checks (idealised, Å)')
    for mid in ('butan2ol', 'lactic', 'propan2ol'):
        g = ev(page, f"() => document.querySelector('.k').__ch.geom('{mid}')")
        A = g['atoms']
        nb = {i: [] for i in range(len(A))}
        for b in g['bonds']:
            nb[b[0]].append(b[1])
            nb[b[1]].append(b[0])

        bad = []
        for b in g['bonds']:
            d = v_len(v_sub(A[b[0]]['p'], A[b[1]]['p']))
            els = {A[b[0]]['el'], A[b[1]]['el']}
            if els == {'C', 'H'} and abs(d - 1.09) > 0.02:
                bad.append(f'C–H {d:.2f}')
            if els == {'O', 'H'} and abs(d - 0.96) > 0.02:
                bad.append(f'O–H {d:.2f}')
            if els == {'C', 'O'} and b[2] == 1 and not (1.33 <= d <= 1.45):
                bad.append(f'C–O {d:.2f}')
            if els == {'C', 'O'} and b[2] == 2 and abs(d - 1.22) > 0.02:
                bad.append(f'C=O {d:.2f}')
            if els == {'C'} and b[2] == 1 and not (1.49 <= d <= 1.55):
                bad.append(f'C–C {d:.2f}')

        # Central carbon C2 must have 4 single bonds with 109.47° angles
        c2 = g['cL']
        c2_nb = nb[c2]
        if len(c2_nb) != 4:
            bad.append(f'C2 coordination {len(c2_nb)} != 4')
        for x in range(len(c2_nb)):
            for y in range(x + 1, len(c2_nb)):
                ang = angle(A[c2_nb[x]]['p'], A[c2]['p'], A[c2_nb[y]]['p'])
                if abs(ang - 109.47) > 0.6:
                    bad.append(f'angle at C2: {ang:.1f} (want 109.5)')

        c_cnt = sum(1 for a in A if a['el'] == 'C')
        h_cnt = sum(1 for a in A if a['el'] == 'H')
        o_cnt = sum(1 for a in A if a['el'] == 'O')
        want_f = {'butan2ol': (4, 10, 1), 'lactic': (3, 6, 3), 'propan2ol': (3, 8, 1)}[mid]
        check(f'geometry {mid}: C{want_f[0]}H{want_f[1]}O{want_f[2]}, tetrahedral angles around C2',
              (c_cnt, h_cnt, o_cnt) == want_f and not bad,
              '; '.join(bad[:4]) + f' (C{c_cnt}H{h_cnt}O{o_cnt})')

        # Check chirality assignment
        if mid in ('butan2ol', 'lactic'):
            check(f'{mid} has chiral centre C2 (4 different groups attached)',
                  g['isChiral'] is True and len(g['groups']) == 4)
        else:
            check(f'{mid} is achiral control (two identical –CH₃ groups)',
                  g['isChiral'] is False and g['groups']['g3']['name'] == g['groups']['g4']['name'])


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=ARGS)

    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1500}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, sc=scheme: errors.append(f'{sc}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, sc=scheme: errors.append(f'{sc}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.k[data-3d=ready]', timeout=40000)
        page.wait_for_timeout(500)
        sfx = '' if scheme == 'light' else '-dark'

        print(f'== {scheme}: startup')
        check(f'{scheme}: 3D ready, mode = butan2ol', page.get_attribute('.k', 'data-mode3d') == 'butan2ol')
        if scheme == 'light':
            geometry_checks(page)

        print(f'== {scheme}: mirror symmetry')
        # Check that right slot atoms are exact x-reflection of left slot atoms
        L = ev(page, "() => document.querySelector('.k').__ch.layout()")
        s0, s1 = L['slots'][0], L['slots'][1]
        mir_bad = []
        for i in range(len(s0['atoms'])):
            a0, a1 = s0['atoms'][i], s1['atoms'][i]
            if a0['el'] != a1['el']:
                mir_bad.append(f'atom {i} element {a0["el"]} != {a1["el"]}')
            if abs(a1['p'][0] - (-a0['p'][0])) > 1e-4 or abs(a1['p'][1] - a0['p'][1]) > 1e-4 or abs(a1['p'][2] - a0['p'][2]) > 1e-4:
                mir_bad.append(f'atom {i} pos [{a1["p"][0]:.2f},{a1["p"][1]:.2f}] != [-({a0["p"][0]:.2f}),{a0["p"][1]:.2f}]')
        check(f'{scheme}: right slot is exact enantiomer mirror image (x_R = -x_L)', not mir_bad, '; '.join(mir_bad[:3]))
        check(f'{scheme}: mirror plane is present and transparent (depthWrite=false)', L['mirror']['visible'] is True and 0.05 < L['mirror']['opacity'] < 0.3)

        print(f'== {scheme}: sync rotation')
        me0 = mirror_err(page)
        check(f'{scheme}: default view — right molecule is the reflection of the left one through the drawn mirror',
              me0 < 1e-3, f'{me0:.4f} Å')
        # With sync rotation ON, changing view rotation moves BOTH molecules and they stay mirror images
        p0_l, p0_r = screen_pos(page, 0), screen_pos(page, 1)
        h0_l = slot_hash(page, 0)
        h0_r = slot_hash(page, 1)
        ev(page, "() => { const a = document.querySelector('.k').__k3; a.rx += 0.25; a.ry += 0.35; a.view(); }")
        page.wait_for_timeout(150)
        p1_l, p1_r = screen_pos(page, 0), screen_pos(page, 1)
        h1_l = slot_hash(page, 0)
        h1_r = slot_hash(page, 1)
        check(f'{scheme}: sync rotation ON — rotating view moves both molecules on screen and changes both halves',
              moved(p0_l, p1_l) > 5 and moved(p0_r, p1_r) > 5 and h1_l != h0_l and h1_r != h0_r,
              f'L {moved(p0_l, p1_l):.1f}px R {moved(p0_r, p1_r):.1f}px hashes {h0_l != h1_l} {h0_r != h1_r}')
        me1 = mirror_err(page)
        check(f'{scheme}: after rotating the view they are still exact mirror images through the (rotated) mirror',
              me1 < 1e-3, f'{me1:.4f} Å')

        # Reset view
        if page.locator('[data-3d="reset"]').count():
            page.click('[data-3d="reset"]')
            page.wait_for_timeout(150)

        # With sync rotation OFF, a drag on the right half turns only the right molecule
        # (judged on the projected atom positions: a pixel hash of the screen half is not a valid
        #  test, the right molecule's halo / perspective can reach across the centre line)
        ev(page, "() => document.querySelector('.k').__ch.setSync(false)")
        p2_l, p2_r = screen_pos(page, 0), screen_pos(page, 1)
        cb = page.eval_on_selector('.ch-stage canvas', 'e => { const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }')
        page.mouse.move(cb[0] + cb[2] * 0.75, cb[1] + cb[3] * 0.5)
        page.mouse.down()
        page.mouse.move(cb[0] + cb[2] * 0.75 + 60, cb[1] + cb[3] * 0.5, steps=6)
        page.mouse.up()
        page.wait_for_timeout(150)
        p3_l, p3_r = screen_pos(page, 0), screen_pos(page, 1)
        check(f'{scheme}: sync rotation OFF — dragging the right half turns only the right molecule',
              moved(p2_r, p3_r) > 5 and moved(p2_l, p3_l) < 0.01,
              f'R moved {moved(p2_r, p3_r):.2f}px, L moved {moved(p2_l, p3_l):.3f}px')
        ev(page, "() => document.querySelector('.k').__ch.setSync(true)")
        page.wait_for_timeout(100)
        me2 = mirror_err(page)
        check(f'{scheme}: sync back ON — mirror relation restored', me2 < 1e-3, f'{me2:.4f} Å')
        ev(page, "() => { const k = document.querySelector('.k'); k.__ch.state.rotR = 0; k.__ch.setSync(true); k.__k3.view(); }")
        page.wait_for_timeout(100)

        print(f'== {scheme}: overlay test — butan-2-ol (chiral)')
        tab(page, 'butan2ol')
        set_overlay(page, 0)
        page.wait_for_timeout(150)
        check(f'{scheme}: separated state (overlay=0) -> data-super=separate',
              page.get_attribute('.k', 'data-super') == 'separate')
        if scheme == 'light':
            shot(page, '.k', OUT / '01-butan2ol-separated.png')

        # Translate overlay to 1.0 (superimposed)
        set_overlay(page, 1.0)
        page.wait_for_timeout(200)
        super_res = page.get_attribute('.k', 'data-super')
        res_txt = page.inner_text('.ch-res') if page.locator('.ch-res').count() else ''
        check(f'{scheme}: butan-2-ol overlay -> cannot superimpose (data-super=no, 不能重合)',
              super_res == 'no' and '不能重合' in res_txt and 'non-superimposable' in res_txt,
              f'{super_res} | {res_txt}')
        lb_ov = ev(page, LAYOUT_BAD_JS)
        check(f'{scheme}: butan-2-ol overlay — tags / overlays clean', not lb_ov, '; '.join(lb_ov[:3]))
        want = {0: ({'–OH', '–H'}, {'–CH₃', '–C₂H₅'}), 1: ({'–OH', '–C₂H₅'}, {'–CH₃', '–H'}),
                2: ({'–OH', '–CH₃'}, {'–H', '–C₂H₅'})}
        if scheme == 'light':
            shot(page, '.k', OUT / '02-butan2ol-overlay.png')
        else:
            shot(page, '.k', OUT / '12-butan2ol-overlay-dark.png')

        # translation, then turn the mirror image 120° / 240° about C–OH: always exactly 2 groups coincide
        for n in range(3):
            if n:
                page.click('.ch-align-btn')
                page.wait_for_timeout(150)
            m = mapping(page)
            same = {x['l'] for x in m if x['same']}
            swap = {x['l'] for x in m if not x['same']}
            exact = all(x['d'] < 0.02 for x in m if x['same'])
            rt = page.inner_text('.ch-res')
            names_ok = all(nm in rt for nm in want[n][1]) and '最多只能同时对齐 2 个基团' in rt and '不能重合' in rt
            check(f'{scheme}: butan-2-ol turned {120 * n}° — aligned {sorted(want[n][0])}, swapped {sorted(want[n][1])}, verdict text names them',
                  (same, swap) == want[n] and exact and names_ok and page.get_attribute('.k', 'data-super') == 'no',
                  f'same={same} swap={swap} exact={exact} | {rt}')
            lb_a = ev(page, LAYOUT_BAD_JS)
            check(f'{scheme}: butan-2-ol turned {120 * n}° — tags clean', not lb_a, '; '.join(lb_a[:3]))
            if scheme == 'light' and n:
                shot(page, '.k', OUT / f'03-butan2ol-turn{120 * n}.png')

        # Reset overlay
        if page.locator('.ch-reset-trans').count():
            page.click('.ch-reset-trans')
            page.wait_for_timeout(150)

        print(f'== {scheme}: overlay test — lactic acid (chiral)')
        tab(page, 'lactic')
        set_overlay(page, 0)
        page.wait_for_timeout(150)
        if scheme == 'light':
            shot(page, '.k', OUT / '04-lactic-separated.png')
        set_overlay(page, 1.0)
        page.wait_for_timeout(200)
        super_lactic = page.get_attribute('.k', 'data-super')
        res_lactic = page.inner_text('.ch-res') if page.locator('.ch-res').count() else ''
        m = mapping(page)
        check(f'{scheme}: lactic acid overlay -> cannot superimpose (data-super=no, 不能重合), –CH₃ / –COOH swapped',
              super_lactic == 'no' and '不能重合' in res_lactic
              and {x['l'] for x in m if not x['same']} == {'–CH₃', '–COOH'}, f'{super_lactic} | {res_lactic}')
        lb_l = ev(page, LAYOUT_BAD_JS)
        check(f'{scheme}: lactic overlay — tags clean', not lb_l, '; '.join(lb_l[:3]))
        if scheme == 'light':
            shot(page, '.k', OUT / '05-lactic-overlay.png')
        set_overlay(page, 0)

        print(f'== {scheme}: overlay test — propan-2-ol (achiral control)')
        tab(page, 'propan2ol')
        set_overlay(page, 0)
        page.wait_for_timeout(150)
        if scheme == 'light':
            shot(page, '.k', OUT / '06-propan2ol-separated.png')
        else:
            shot(page, '.k', OUT / '15-propan2ol-dark.png')
        set_overlay(page, 1.0)
        page.wait_for_timeout(200)
        super_prop = page.get_attribute('.k', 'data-super')
        res_prop = page.inner_text('.ch-res') if page.locator('.ch-res').count() else ''
        m = mapping(page)
        check(f'{scheme}: propan-2-ol overlay -> completely superimposable (data-super=yes, 能完全重合), all 4 coincide',
              super_prop == 'yes' and '能完全重合' in res_prop and all(x['same'] and x['d'] < 0.02 for x in m),
              f'{super_prop} | {res_prop}')
        lb_p = ev(page, LAYOUT_BAD_JS)
        check(f'{scheme}: propan-2-ol overlay — tags clean', not lb_p, '; '.join(lb_p[:3]))
        if scheme == 'light':
            shot(page, '.k', OUT / '07-propan2ol-overlay.png')
        else:
            shot(page, '.k', OUT / '16-propan2ol-overlay-dark.png')
        set_overlay(page, 0)

        print(f'== {scheme}: optical activity text and icons')
        opt_txt = page.inner_text('.ch-opt-card') if page.locator('.ch-opt-card').count() else ''
        check(f'{scheme}: optical activity banner — plane-polarised light, 角度相等、方向相反, 顺时针 & 逆时针 (ch13 13.4)',
              'plane-polarised light' in opt_txt and '角度相等' in opt_txt and '方向相反' in opt_txt
              and '顺时针' in opt_txt and '逆时针' in opt_txt, opt_txt)
        alltxt = page.inner_text('.k')
        bad_terms = [w for w in ('乳酸', '旋光', '对映', '手性', '羟基', '甲基', '乙基') if w in alltxt]
        check(f'{scheme}: chemistry terms stay English (no Chinese translations)', not bad_terms, str(bad_terms))
        check(f'{scheme}: no claim that 3 groups can be aligned', '3 个基团' not in alltxt and '第 4 个' not in alltxt)
        rot_icons = page.locator('svg.ch-rotsvg').count()
        check(f'{scheme}: two rotating arrow icons present', rot_icons == 2, str(rot_icons))

        print(f'== {scheme}: layout & collision checks')
        tab(page, 'butan2ol')
        set_overlay(page, 0)
        page.wait_for_timeout(150)
        lb = ev(page, LAYOUT_BAD_JS)
        check(f'{scheme}: layout clean — overlays & HUD never cover atoms or halos', not lb, '; '.join(lb[:3]))
        check(f'{scheme}: no [data-clash]', not ev(page, CLASH_JS), str(ev(page, CLASH_JS)))
        check(f'{scheme}: SVG text ≥ 12px & inside viewBox',
              not ev(page, SVG_SMALL_JS) and not ev(page, SVG_OUTSIDE_JS),
              str(ev(page, SVG_SMALL_JS)) + str(ev(page, SVG_OUTSIDE_JS)))
        check(f'{scheme}: HTML font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))

        # Central C* tag and group tags check
        L = ev(page, "() => document.querySelector('.k').__ch.layout()")
        c_star_tags = [t for t in L['tags'] if t['isCenter']]
        check(f'{scheme}: C* tag on central carbon visible on both slots',
              len(c_star_tags) == 2 and all(t['visible'] for t in c_star_tags))

        # Oblique view and detail screenshots
        # Oblique view showing tetrahedral arrangement in 3D
        ev(page, """() => { const a = document.querySelector('.k').__k3; a.rx = 0.58; a.ry = -0.72; a.view(); }""")
        page.wait_for_timeout(200)
        if scheme == 'light':
            shot(page, '.ch-stage', OUT / '08-oblique-tetrahedral.png')
            shot_clip(page, '.ch-stage', 0.15, 0.15, 0.85, 0.85, OUT / 'z-stage-z2.png')
            shot_clip(page, '.ch-stage', 0.40, 0.20, 0.60, 0.80, OUT / 'z-mirror-detail.png')
            shot_clip(page, '.ch-stage', 0.05, 0.25, 0.45, 0.75, OUT / 'z-tags-detail.png')
        else:
            shot(page, '.k', OUT / '11-butan2ol-dark.png')
            shot_clip(page, '.ch-stage', 0.15, 0.15, 0.85, 0.85, OUT / 'z-stage-z2-dark.png')

        if page.locator('[data-3d="reset"]').count():
            page.click('[data-3d="reset"]')
            page.wait_for_timeout(150)

        if scheme == 'light':
            print('== narrow (720 px)')
            page.set_viewport_size({'width': 720, 'height': 1600})
            page.wait_for_timeout(600)
            ov = ev(page, "() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('720px: .k has no horizontal overflow', ov[0] <= ov[1] + 1, str(ov))
            check('720px: HTML font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            check('720px: SVG font ≥ 12px', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)))
            lb_720 = ev(page, LAYOUT_BAD_JS)
            check('720px: overlays clean', not lb_720, '; '.join(lb_720[:2]))
            shot(page, '.k', OUT / '60-narrow-720-butan2ol.png')

            set_overlay(page, 1.0)
            page.wait_for_timeout(200)
            shot(page, '.k', OUT / '61-narrow-720-overlay.png')
            set_overlay(page, 0)

            tab(page, 'propan2ol')
            page.wait_for_timeout(200)
            shot(page, '.k', OUT / '62-narrow-720-propan2ol.png')
            tab(page, 'butan2ol')

        ctx.close()

    print('== fallback (CDN blocked)')
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1500}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('pageerror', lambda e, sc=scheme: errors.append(f'fallback-{sc}: PAGEERROR {e}'))
        page.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.fallback.show', timeout=20000)
        page.wait_for_timeout(250)
        sfx = '' if scheme == 'light' else '-dark'
        check(f'{scheme} fallback: .fallback.show, stage & 3D buttons hidden',
              page.get_attribute('.k', 'data-3d') == 'fallback'
              and not page.locator('.ch-stage').is_visible()
              and not page.locator('[data-3d="reset"]').is_visible())
        cf_cnt = page.locator('svg.cf').count()
        check(f'{scheme} fallback: 2D stereochemical formulae still visible (count={cf_cnt})', cf_cnt >= 2)
        opt_vis = page.locator('.ch-opt-card').is_visible()
        check(f'{scheme} fallback: optical activity banner visible', opt_vis)
        check(f'{scheme} fallback: no [data-clash]', not ev(page, CLASH_JS), str(ev(page, CLASH_JS)))
        shot(page, '.k', OUT / f'70-fallback-{scheme}.png')
        ctx.close()

    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for _, ok, _ in results if ok)
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
