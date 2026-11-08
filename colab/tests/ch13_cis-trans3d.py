"""ch13 cis-trans3d cell test (3D): butane turns freely about C2–C3 (σ), but-2-ene about C2=C3 breaks the
π overlap (|cos θ|: 0° = 100 %, 90° = 0 %, 180° = trans), the K3.porb p axes really turn, cis vs trans
side by side, but-1-ene / 2-methylpropene counter-examples with the identical groups highlighted, the
end-on SVG (K.label, no clash at any θ), play / pause animation, slot titles + pills never cover an atom
or a lobe, 720 px, fallback with the CDN blocked, light / dark.

usage:
  TMPDIR=/mnt/ai-shared/che_tmp/organic/prof/cis-trans3d /home/lkh/.local/bin/uv run --with playwright \
    python -I colab/tests/ch13_cis-trans3d.py /mnt/ai-shared/che_tmp/organic/cells/ch13-cis-trans3d.html \
    /mnt/ai-shared/che_tmp/organic/shots/cis-trans3d
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
  return { hash: u.length + ':' + u.slice(-400) };
}"""


def chash(page):
    return ev(page, CANVAS_JS)['hash']


def set_slider(page, w, deg):
    ev(page, """([w, d]) => { const r = document.querySelector('input.ct-r[data-w=' + w + ']');
                r.value = d; r.dispatchEvent(new Event('input', {bubbles: true})); }""", [w, deg])
    page.wait_for_timeout(60)


def tab(page, m):
    page.click(f'.ct-modes button[data-tab="{m}"]')
    page.wait_for_timeout(250)


LAYOUT_BAD_JS = """() => {
  const L = document.querySelector('.k').__ct.layout();
  if (!L) return ['no layout'];
  const bad = [];
  const rc = (r, c, m) => {
    const dx = Math.max(r.x - c.x, 0, c.x - (r.x + r.w)), dy = Math.max(r.y - c.y, 0, c.y - (r.y + r.h));
    return Math.hypot(dx, dy) < c.r - (m || 0);
  };
  L.slots.forEach((S, k) => {
    S.circles.forEach(c => {
      L.overlays.forEach(o => { if (rc(o, c, 0.5)) bad.push('slot' + k + ' ' + S.id + ' ' + c.kind + (c.el || '') + ' under overlay "' + o.text.slice(0, 18) + '"'); });
      if (rc(L.hud, c, 0.5)) bad.push('slot' + k + ' ' + c.kind + ' under HUD');
      if (c.x - c.r < 0 || c.x + c.r > L.W || c.y - c.r < 0 || c.y + c.r > L.H) bad.push('slot' + k + ' ' + c.kind + ' outside stage');
    });
  });
  /* overlays never overlap each other or the HUD */
  L.overlays.forEach((a, i) => {
    L.overlays.forEach((b, j) => {
      if (j > i && a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) bad.push('overlay "' + a.text.slice(0, 12) + '" overlaps "' + b.text.slice(0, 12) + '"');
    });
    if (a.y < L.hud.y + L.hud.h) bad.push('overlay "' + a.text.slice(0, 12) + '" under HUD');
    if (a.x < 0 || a.x + a.w > L.W + 0.5 || a.y + a.h > L.H + 0.5) bad.push('overlay "' + a.text.slice(0, 12) + '" outside stage');
  });
  /* atom tags: font ≥ 12 px and inside their sphere's neighbourhood */
  L.tags.filter(t => t.visible).forEach(t => {
    if (t.h * 0.6875 < 12) bad.push('C tag font < 12px (' + (t.h * 0.6875).toFixed(1) + ')');
    L.overlays.forEach(o => {
      if (t.x < o.x + o.w && o.x < t.x + t.w && t.y < o.y + o.h && o.y < t.y + t.h) bad.push('C tag under overlay');
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

# end-on SVG: label off every lobe outline and the arc, at all angles (no data-clash), inside the viewBox
EO_SWEEP_JS = """() => {
  const k = document.querySelector('.k'), bad = [];
  for (let d = 0; d < 360; d += 5) {
    k.__ct.setTheta('p', d);
    const svg = k.querySelector('.ct-eosvg'), v = svg.viewBox.baseVal;
    svg.querySelectorAll('[data-clash]').forEach(e => bad.push(d + ': clash ' + e.textContent));
    svg.querySelectorAll('text').forEach(t => {
      const b = t.getBBox();
      if (b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5) bad.push(d + ': outside ' + t.textContent);
    });
    const t = svg.querySelector('text.ct-eot');
    if (!t || !t.textContent.includes(d + '°')) bad.push(d + ': θ label missing');
  }
  k.__ct.setTheta('p', 0);
  return bad;
}"""


def v_sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def v_len(a):
    return math.sqrt(sum(x * x for x in a))


def angle(a, c, b):
    u, w = v_sub(a, c), v_sub(b, c)
    return math.degrees(math.acos(max(-1, min(1, sum(x * y for x, y in zip(u, w)) / (v_len(u) * v_len(w))))))


def geometry_checks(page):
    print('== geometry (idealised, Å)')
    for mid in ('butane', 'cis', 'trans', 'but1', 'mprop'):
        g = ev(page, f"() => document.querySelector('.k').__ct.geom('{mid}')")
        A = g['atoms']
        nb = {i: [] for i in range(len(A))}
        for b in g['bonds']:
            nb[b[0]].append(b[1])
            nb[b[1]].append(b[0])
        bad = []
        for b in g['bonds']:
            d = v_len(v_sub(A[b[0]]['p'], A[b[1]]['p']))
            els = {A[b[0]]['el'], A[b[1]]['el']}
            if 'H' in els and abs(d - 1.09) > 0.01:
                bad.append(f'C–H {d:.2f}')
            if els == {'C'} and b[2] == 2 and abs(d - 1.34) > 0.01:
                bad.append(f'C=C {d:.2f}')
            if els == {'C'} and b[2] == 1 and not (1.49 <= d <= 1.55):
                bad.append(f'C–C {d:.2f}')
        for i, a in enumerate(A):
            if a['el'] != 'C':
                continue
            n = nb[i]
            want = 120.0 if len(n) == 3 else 109.47
            if len(n) not in (3, 4):
                bad.append(f'C{i} has {len(n)} bonds')
            for x in range(len(n)):
                for y in range(x + 1, len(n)):
                    ang = angle(A[n[x]]['p'], a['p'], A[n[y]]['p'])
                    if abs(ang - want) > 0.6:
                        bad.append(f'angle at {i}: {ang:.1f} (want {want})')
            if len(n) == 3:   # sp²: all 3 neighbours + C in one plane (y = 0 for the C=C carbons)
                if any(abs(A[j]['p'][1]) > 1e-6 for j in n + [i]):
                    bad.append(f'sp² C{i} not planar')
        hs = sum(1 for a in A if a['el'] == 'H')
        cs = sum(1 for a in A if a['el'] == 'C')
        want_h = 10 if mid == 'butane' else 8
        check(f'geometry {mid}: C4H{want_h}, ideal bond lengths & 120° / 109.5° angles', cs == 4 and hs == want_h and not bad, '; '.join(bad[:4]) + f' C{cs}H{hs}')
        if mid in ('cis', 'trans'):
            z1, z4 = A[g['me'][0]]['p'][2], A[g['me'][1]]['p'][2]
            same = z1 * z4 > 0
            check(f'geometry {mid}: the two CH₃ are on {"the same side" if mid == "cis" else "opposite sides"} of C=C',
                  same == (mid == 'cis'), f'z = {z1:.2f}, {z4:.2f}')
        if mid in ('but1', 'mprop'):
            ok = True
            det = []
            for s in g['same']:
                g1, g2 = s['g']
                if A[g1]['el'] != A[g2]['el'] or len(nb[g1]) != len(nb[g2]) or s['c'] not in nb[g1] or s['c'] not in nb[g2]:
                    ok = False
                det.append(f"C{s['c']}:{A[g1]['el']}{len(nb[g1])}/{A[g2]['el']}{len(nb[g2])}")
            check(f'geometry {mid}: highlighted pairs are two identical groups on one C=C carbon '
                  f'({"1 pair" if mid == "but1" else "2 pairs"})',
                  ok and len(g['same']) == (1 if mid == 'but1' else 2), ' '.join(det))


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
        check(f'{scheme}: 3D ready, mode = rot', page.get_attribute('.k', 'data-mode3d') == 'rot')
        if scheme == 'light':
            geometry_checks(page)

        print(f'== {scheme}: overlap readout')
        expect = {0: (100, 'cis-but-2-ene'), 45: (71, 'twisted'), 90: (0, 'broken'), 135: (71, 'twisted'),
                  180: (100, 'trans-but-2-ene'), 270: (0, 'broken'), 360: (100, 'cis-but-2-ene')}
        bad = []
        for d, (ov, st) in expect.items():
            set_slider(page, 'p', d)
            got = (int(page.get_attribute('.k', 'data-overlap')), page.get_attribute('.k', 'data-pstate'))
            txt = page.inner_text('.ct-ovp').strip()
            if got != (ov, st) or txt != f'{ov}%':
                bad.append(f'{d}°: {got} {txt}')
        check(f'{scheme}: π overlap = |cos θ| (0°=100%, 90°=0%, 180°=100% trans, 45°=71%)', not bad, '; '.join(bad))
        set_slider(page, 'p', 90)
        pill = page.inner_text('.ct-p.ct-r')
        check(f'{scheme}: 90° pill says π bond 断开', 'π bond 断开' in pill, pill)
        set_slider(page, 'p', 180)
        pill = page.inner_text('.ct-p.ct-r')
        stp = page.inner_text('.ct-stp')
        check(f'{scheme}: 180° → trans-but-2-ene, another compound', 'trans' in pill and '另一个 compound' in stp, pill + ' | ' + stp)

        # the p axes really turn: world-space cos between the two p axes follows θ
        bad = []
        for d in (0, 30, 60, 90, 120, 180, 250):
            set_slider(page, 'p', d)
            L = ev(page, "() => document.querySelector('.k').__ct.layout()")
            c = L['axes']['cos']
            if abs(c - math.cos(math.radians(d))) > 1e-3:
                bad.append(f'{d}: cos {c:.3f}')
            S = L['slots'][1]
            want_br = 0 if abs(math.cos(math.radians(d))) < 0.02 else 2
            if S['bridges'] != want_br:
                bad.append(f'{d}: {S["bridges"]} bridges')
            elif want_br and abs(S['bridgeOpacity'] - 0.55 * abs(math.cos(math.radians(d)))) > 1e-3:
                bad.append(f'{d}: bridge opacity {S["bridgeOpacity"]:.3f}')
        check(f'{scheme}: K3.porb axes turn with θ (cos = cos θ) and the overlap bridge fades as |cos θ|', not bad, '; '.join(bad))

        print(f'== {scheme}: sliders change the picture')
        set_slider(page, 'p', 0)
        set_slider(page, 's', 0)
        page.wait_for_timeout(150)
        h0 = chash(page)
        set_slider(page, 's', 120)
        page.wait_for_timeout(150)
        h1 = chash(page)
        L = ev(page, "() => document.querySelector('.k').__ct.layout()")
        check(f'{scheme}: butane slider turns the rotor and changes the canvas',
              h1 != h0 and abs(L['slots'][0]['rotor'] - math.radians(120)) < 1e-6)
        sts = page.inner_text('.ct-sts')
        check(f'{scheme}: butane at 120° still butane, no bond broken', '没有 bond 断开' in sts and '100%' in page.inner_text('.ct-ovs'), sts)
        set_slider(page, 'p', 90)
        page.wait_for_timeout(150)
        h2 = chash(page)
        check(f'{scheme}: but-2-ene slider changes the canvas', h2 != h1)

        # layout: titles / pills / HUD never cover an atom, a halo or a p lobe — any θ (fit covers the full turn)
        bad = []
        for d in range(0, 360, 30):
            set_slider(page, 's', d)
            set_slider(page, 'p', (d * 7) % 360)
            lb = ev(page, LAYOUT_BAD_JS)
            if lb:
                bad.append(f'{d}: {lb[:3]}')
        check(f'{scheme}: rot mode — overlays / HUD clear of atoms & lobes at every θ, C tags ≥ 12px', not bad, '; '.join(bad[:3]))
        vis = ev(page, "() => document.querySelector('.k').__ct.layout().tags.filter(t => t.visible).length")
        check(f'{scheme}: rot mode — C tags visible (≥ 6 of 8)', vis >= 6, str(vis))

        # default view: both p axes must read clearly as parallel / not parallel on screen (B round 1: the right
        # slot was seen ~18° from the side, so at 90° C3's p stood end-on as a blob), and every C is labelled
        bad = []
        for d in (0, 45, 90, 180):
            set_slider(page, 's', d)
            set_slider(page, 'p', d)
            L = ev(page, "() => document.querySelector('.k').__ct.layout()")
            pa, pb = L['axes']['sa'], L['axes']['sb']   # screen px, as drawn
            la, lb_ = math.hypot(*pa), math.hypot(*pb)
            ang = math.degrees(math.acos(min(1, abs(pa[0] * pb[0] + pa[1] * pb[1]) / (la * lb_ + 1e-9))))
            if la < 20 or lb_ < 0.6 * la:
                bad.append(f'{d}°: projected p axes {la:.2f} / {lb_:.2f}')
            if d in (0, 180) and ang > 6:   # parallel in 3D; perspective alone tilts them ~4°
                bad.append(f'{d}°: p axes should look parallel, {ang:.0f}°')
            if d == 90 and ang < 45:
                bad.append(f'90°: p axes only {ang:.0f}° apart on screen')
            hid = [f"s{t['slot']}#{t['i']}" for t in L['tags'] if not t['visible']]
            if hid:
                bad.append(f'{d}°: hidden C tags {hid}')
        check(f'{scheme}: rot default view — p axes look parallel (≤ 6°) at 0° / 180°, ≥ 45° apart at 90°, all 8 C tags shown', not bad, '; '.join(bad[:4]))

        # end-on SVG sweep
        eo = ev(page, EO_SWEEP_JS)
        check(f'{scheme}: end-on SVG — θ label present, no clash, inside viewBox for θ = 0…355°', not eo, '; '.join(eo[:4]))

        # screenshots of the rotation mode
        set_slider(page, 's', 0)
        set_slider(page, 'p', 0)
        page.wait_for_timeout(200)
        shot(page, '.k', OUT / f'01-rot-0{sfx}.png')
        set_slider(page, 's', 90)
        set_slider(page, 'p', 90)
        page.wait_for_timeout(200)
        shot(page, '.k', OUT / f'02-rot-90{sfx}.png')
        shot_clip(page, '.ct-stage', 0.5, 0, 1, 1, OUT / f'z-rot-90-right{sfx}.png')
        set_slider(page, 'p', 45)
        page.wait_for_timeout(120)
        shot(page, '.ct-cp', OUT / f'z-card-45{sfx}.png')
        set_slider(page, 'p', 180)
        set_slider(page, 's', 180)
        page.wait_for_timeout(200)
        shot(page, '.ct-stage', OUT / f'03-rot-180{sfx}.png')
        # oblique view (as if dragged): C=C plane edge-on-ish, groups either side, p lobes upright
        ev(page, """() => { const a = document.querySelector('.k').__k3; a.rx = 0.62; a.ry = -1.0; a.view(); }""")
        set_slider(page, 'p', 0)
        page.wait_for_timeout(200)
        shot(page, '.ct-stage', OUT / f'04-rot-oblique-0{sfx}.png')
        set_slider(page, 'p', 60)
        page.wait_for_timeout(200)
        shot(page, '.ct-stage', OUT / f'05-rot-oblique-60{sfx}.png')
        shot_clip(page, '.ct-stage', 0.5, 0.05, 1, 0.95, OUT / f'z-rot-oblique-60-right{sfx}.png')
        page.click('[data-3d="reset"]')
        page.wait_for_timeout(200)

        print(f'== {scheme}: play / pause')
        set_slider(page, 'p', 0)
        set_slider(page, 's', 0)
        page.click('.ct-play')
        hs, ths = [], []
        for _ in range(10):
            page.wait_for_timeout(260)
            hs.append(chash(page))
            ths.append(page.get_attribute('.k', 'data-th'))
        distinct = len(set(hs))
        check(f'{scheme}: playing — ≥ 5 of 10 frames over 2.6 s differ, θ keeps increasing',
              distinct >= 5 and len(set(ths)) >= 5 and page.get_attribute('.k', 'data-play') == '1', f'{distinct} {ths}')
        page.click('.ct-play')
        page.wait_for_timeout(150)
        t0 = page.get_attribute('.k', 'data-th')
        hp = chash(page)
        page.wait_for_timeout(500)
        check(f'{scheme}: pause stops θ and the picture', page.get_attribute('.k', 'data-th') == t0 and chash(page) == hp and page.get_attribute('.k', 'data-play') == '0')
        ev(page, "() => { const k = document.querySelector('.k'); k.__ct.setTheta('s', 0); k.__ct.setTheta('p', 0); k.__ct.step(2250); }")
        check(f'{scheme}: step(2250 ms) at 40°/s → θ = 90°, overlap 0', page.get_attribute('.k', 'data-th') == '90,90' and page.get_attribute('.k', 'data-overlap') == '0',
              page.get_attribute('.k', 'data-th'))
        page.click('.ct-zero')
        page.wait_for_timeout(100)
        check(f'{scheme}: θ 归零 resets both sliders', page.get_attribute('.k', 'data-th') == '0,0')

        print(f'== {scheme}: cis vs trans')
        tab(page, 'ct')
        check(f'{scheme}: ct mode built', page.get_attribute('.k', 'data-mode3d') == 'ct')
        L = ev(page, "() => document.querySelector('.k').__ct.layout()")
        check(f'{scheme}: ct — cis left, trans right, CH₃ halos on C1 and C4 of each',
              [s['id'] for s in L['slots']] == ['cis', 'trans'] and all(len(s['halos']) == 2 for s in L['slots']))
        pl = page.inner_text('.ct-p.ct-l') + ' | ' + page.inner_text('.ct-p.ct-r')
        tl = page.inner_text('.ct-t.ct-l') + ' | ' + page.inner_text('.ct-t.ct-r')
        check(f'{scheme}: ct — titles & pills label cis / trans', 'cis' in pl and 'trans' in pl and '同侧' in pl and '两侧' in pl
              and 'cis-but-2-ene' in tl and 'trans-but-2-ene' in tl, pl + ' || ' + tl)
        lb = ev(page, LAYOUT_BAD_JS)
        check(f'{scheme}: ct — cis / trans labels do not cover any atom or halo', not lb, '; '.join(lb[:4]))
        hl = ev(page, "() => ['cis','trans'].map(f => document.querySelectorAll('.ct-f[data-f=' + f + '] .ko-hl').length)")
        nums = ev(page, "() => [...document.querySelectorAll('.ct-f[data-f=cis] text.ko-num')].map(t => t.textContent)")
        check(f'{scheme}: ct — displayed formulae highlight both CH₃ and number C1–C4', hl == [2, 2] and nums == ['C1', 'C2', 'C3', 'C4'], f'{hl} {nums}')
        check(f'{scheme}: ct — no [data-clash]', not ev(page, CLASH_JS), str(ev(page, CLASH_JS)))
        page.wait_for_timeout(150)
        shot(page, '.k', OUT / f'10-ct{sfx}.png')
        shot_clip(page, '.ct-stage', 0, 0, 1, 1, OUT / f'z-ct-stage{sfx}.png')
        shot(page, '[data-pane="ct"] .ct-grid', OUT / f'z-ct-formulae{sfx}.png')

        print(f'== {scheme}: counter-examples')
        tab(page, 'no')
        L = ev(page, "() => document.querySelector('.k').__ct.layout()")
        check(f'{scheme}: no — but-1-ene (2 H halos) and 2-methylpropene (2 H + 2 CH₃ halos)',
              [s['id'] for s in L['slots']] == ['but1', 'mprop'] and [len(s['halos']) for s in L['slots']] == [2, 4],
              str([(s['id'], s['halos']) for s in L['slots']]))
        g1 = ev(page, "() => document.querySelector('.k').__ct.geom('but1')")
        g2 = ev(page, "() => document.querySelector('.k').__ct.geom('mprop')")
        h_ok = (sorted(L['slots'][0]['halos']) == sorted(g1['same'][0]['g'])
                and sorted(L['slots'][1]['halos']) == sorted(g2['same'][0]['g'] + g2['same'][1]['g']))
        check(f'{scheme}: no — halos sit on exactly the identical groups', h_ok)
        lb = ev(page, LAYOUT_BAD_JS)
        check(f'{scheme}: no — labels do not cover any atom or halo', not lb, '; '.join(lb[:4]))
        hl = ev(page, "() => ['but1','mprop'].map(f => document.querySelectorAll('.ct-f[data-f=' + f + '] .ko-hl.ko-bad').length)")
        check(f'{scheme}: no — displayed formulae highlight the identical groups (2, 4)', hl == [2, 4], str(hl))
        nums = ev(page, "() => [...document.querySelectorAll('.ct-f[data-f=but1] text.ko-num')].map(t => t.textContent)")
        check(f'{scheme}: no — but-1-ene formula numbers C1–C4 with CH₂ and CH₃ drawn apart (C3 is the CH₂)', nums == ['C1', 'C2', 'C3', 'C4'], str(nums))
        hid = [f"s{t['slot']}#{t['i']}" for t in L['tags'] if not t['visible']]
        check(f'{scheme}: no — every numbered C tag visible (but-1-ene C1–C4, 2-methylpropene C1–C3)', not hid and len(L['tags']) == 7, f'{hid} {len(L["tags"])}')
        check(f'{scheme}: no — no [data-clash]', not ev(page, CLASH_JS), str(ev(page, CLASH_JS)))
        page.wait_for_timeout(150)
        shot(page, '.k', OUT / f'20-no{sfx}.png')
        shot_clip(page, '.ct-stage', 0, 0, 1, 1, OUT / f'z-no-stage{sfx}.png')
        shot(page, '[data-pane="no"] .ct-grid', OUT / f'z-no-formulae{sfx}.png')

        check(f'{scheme}: SVG text ≥ 12px & inside viewBox (all panes seen)',
              not ev(page, SVG_SMALL_JS) and not ev(page, SVG_OUTSIDE_JS), str(ev(page, SVG_SMALL_JS)) + str(ev(page, SVG_OUTSIDE_JS)))
        check(f'{scheme}: HTML font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))

        if scheme == 'light':
            print('== narrow (720 px)')
            tab(page, 'rot')
            page.set_viewport_size({'width': 720, 'height': 1700})
            page.wait_for_timeout(700)
            ov = ev(page, "() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('720px: .k has no horizontal overflow', ov[0] <= ov[1] + 1, str(ov))
            check('720px: HTML font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            check('720px: SVG font ≥ 12px', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)))
            bad = []
            for d in range(0, 360, 45):
                set_slider(page, 's', d)
                set_slider(page, 'p', d)
                lb = ev(page, LAYOUT_BAD_JS)
                if lb:
                    bad.append(f'{d}: {lb[:2]}')
            check('720px: rot mode overlays clean at every θ', not bad, '; '.join(bad[:3]))
            set_slider(page, 's', 60)
            set_slider(page, 'p', 60)
            page.wait_for_timeout(200)
            shot(page, '.k', OUT / '60-narrow-720-rot.png')
            for m, n in (('ct', '61'), ('no', '62')):
                tab(page, m)
                page.wait_for_timeout(200)
                lb = ev(page, LAYOUT_BAD_JS)
                check(f'720px: {m} mode overlays clean', not lb, '; '.join(lb[:3]))
                shot(page, '.k', OUT / f'{n}-narrow-720-{m}.png')
            tab(page, 'rot')
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
              page.get_attribute('.k', 'data-3d') == 'fallback' and not page.locator('.ct-stage').is_visible()
              and not page.locator('[data-3d="reset"]').is_visible())
        set_slider(page, 'p', 90)
        check(f'{scheme} fallback: slider still drives the overlap readout (90° → 0%) and the end-on view',
              page.inner_text('.ct-ovp').strip() == '0%' and '90°' in (page.text_content('.ct-eosvg') or ''))
        set_slider(page, 'p', 30)
        shot(page, '.k', OUT / f'70-fallback-rot{sfx}.png')
        tab(page, 'no')
        hl = ev(page, "() => document.querySelectorAll('.ct-f[data-f=mprop] .ko-hl.ko-bad').length")
        check(f'{scheme} fallback: counter-example formulae still highlighted', hl == 4, str(hl))
        check(f'{scheme} fallback: no [data-clash]', not ev(page, CLASH_JS), str(ev(page, CLASH_JS)))
        shot(page, '.k', OUT / f'71-fallback-no{sfx}.png')
        ctx.close()

    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for _, ok, _ in results if ok)
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
