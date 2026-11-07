"""ch13 shapes3d cell test (3D): organic molecule shape, hybridisation (sp³ / sp² / sp),
bond angle (K3.arc + value), sp² planar sheet (ethene all 6 atoms in-plane; propene CH₃ H's
sticking out), σ / π bonds (K3.porb, 2 perpendicular π in ethyne & propanenitrile),
IUPAC carbon selection (canvas raycast + buttons), atom tag occlusion,xrefs, fallback SVG.

usage:
  TMPDIR=/mnt/ai-shared/che_tmp/organic/prof/shapes3d /home/lkh/.local/bin/uv run --with playwright \
    python -I colab/tests/ch13_shapes3d.py /mnt/ai-shared/che_tmp/organic/cells/ch13-shapes3d.html \
    /mnt/ai-shared/che_tmp/organic/shots/shapes3d
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


def shot_clip(page, clip, path):
    c = {
        'x': max(0.0, float(clip['x'])),
        'y': max(0.0, float(clip['y'])),
        'width': max(10.0, float(clip['width'])),
        'height': max(10.0, float(clip['height'])),
    }
    page.screenshot(path=str(path), clip=c, full_page=True)


def ev(page, js, *a):
    return page.evaluate(js, *a)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


# Expected whole-molecule (sigma, pi) and per-carbon (cNum, hyb, shape, ang, deg, c_sig, c_pi)
MOLS = {
    'ethane': {
        'tot': (7, 0),
        'planar': False,
        'carbons': [
            (1, 'sp³', 'tetrahedral', '109.5°', 109.47, 4, 0),
            (2, 'sp³', 'tetrahedral', '109.5°', 109.47, 4, 0),
        ],
    },
    'ethene': {
        'tot': (5, 1),
        'planar': True,
        'carbons': [
            (1, 'sp²', 'trigonal planar', '120°', 120.0, 3, 1),
            (2, 'sp²', 'trigonal planar', '120°', 120.0, 3, 1),
        ],
    },
    'ethyne': {
        'tot': (3, 2),
        'planar': False,
        'carbons': [
            (1, 'sp', 'linear', '180°', 180.0, 2, 2),
            (2, 'sp', 'linear', '180°', 180.0, 2, 2),
        ],
    },
    'propene': {
        'tot': (8, 1),
        'planar': True,
        'carbons': [
            (1, 'sp²', 'trigonal planar', '120°', 120.0, 3, 1),
            (2, 'sp²', 'trigonal planar', '120°', 120.0, 3, 1),
            (3, 'sp³', 'tetrahedral', '109.5°', 109.47, 4, 0),
        ],
    },
    'ethanal': {
        'tot': (6, 1),
        'planar': True,
        'carbons': [
            (1, 'sp²', 'trigonal planar', '120°', 120.0, 3, 1),
            (2, 'sp³', 'tetrahedral', '109.5°', 109.47, 4, 0),
        ],
    },
    'propanenitrile': {
        'tot': (8, 2),
        'planar': False,
        'carbons': [
            (1, 'sp', 'linear', '180°', 180.0, 2, 2),
            (2, 'sp³', 'tetrahedral', '109.5°', 109.47, 4, 0),
            (3, 'sp³', 'tetrahedral', '109.5°', 109.47, 4, 0),
        ],
    },
    'cyclohexane': {
        'tot': (18, 0),
        'planar': False,
        'carbons': [
            (c, 'sp³', 'tetrahedral', '109.5°', 109.47, 4, 0) for c in range(1, 7)
        ],
    },
}

CANVAS_JS = """() => {
  const c = document.querySelector('.stage canvas');
  if (!c) return null;
  const g = document.createElement('canvas');
  g.width = c.width; g.height = c.height;
  const x = g.getContext('2d');
  x.drawImage(c, 0, 0);
  const d = x.getImageData(0, 0, g.width, g.height).data;
  let s = 0, s2 = 0, n = 0;
  for (let i = 0; i < d.length; i += 16) {
    const v = d[i] + d[i + 1] + d[i + 2];
    s += v; s2 += v * v; n++;
  }
  const m = s / n;
  const u = c.toDataURL();
  return { std: Math.sqrt(Math.max(0, s2 / n - m * m)), hash: u.length + ':' + u.slice(-320) };
}"""

LAYOUT_BAD_JS = """() => {
  const L = document.querySelector('.k').__sh.layout();
  if (!L) return ['no layout'];
  const bad = [];
  const rc = (r, c) => {
    const dx = Math.max(r.x - c.x, 0, c.x - (r.x + r.w));
    const dy = Math.max(r.y - c.y, 0, c.y - (r.y + r.h));
    return Math.hypot(dx, dy) < c.r - 1.5;
  };
  const rr = (a, b) => a.x < b.x + b.w - 1 && b.x < a.x + a.w - 1 && a.y < b.y + b.h - 1 && b.y < a.y + a.h - 1;
  L.tags.forEach((t, i) => {
    L.atoms.forEach(a => { if (rc(t, a)) bad.push(t.text + ' overlaps atom ' + a.el); });
    if (t.x < 0 || t.y < L.hud || t.x + t.w > L.W || t.y + t.h > L.H) bad.push(t.text + ' out of stage');
    if (L.tot && rr(t, L.tot)) bad.push(t.text + ' overlaps .sh-tot badge');
    L.tags.forEach((u, j) => {
      if (j > i && rr(t, u)) bad.push(t.text + ' overlaps tag ' + u.text);
      if (j !== i && rc(t, { x: u.ax, y: u.ay, r: 4 })) bad.push(t.text + ' covers anchor of ' + u.text);
    });
    if (L.arcPts.some(p => rc(t, { x: p[0], y: p[1], r: 2 }))) bad.push(t.text + ' sits on K3.arc');
    if (t.h * 0.6875 < 12) bad.push(t.text + ' sprite font < 12px (' + (t.h * 0.6875).toFixed(1) + ')');
  });
  L.elH.forEach((h, i) => {
    if (h * 0.6875 < 12) bad.push('atom tag ' + L.atoms[i].el + ' font < 12px (' + (h * 0.6875).toFixed(1) + ')');
  });
  /* Arc must stay cleanly outside the selection purple ring (no crossing / tangling) */
  if (L.selC && L.arcPts.length >= 15) {
    for (let k = 2; k <= 14; k++) {
      const dRing = Math.hypot(L.arcPts[k][0] - L.selC.x, L.arcPts[k][1] - L.selC.y);
      if (dRing < L.selC.ringR + 1.0) {
        bad.push('K3.arc crosses/tangles with selection ring (d=' + dRing.toFixed(1) + ' <= ringR=' + L.selC.ringR.toFixed(1) + ')');
        break;
      }
    }
  }
  /* Non-arc leader lines must not cross K3.arc or each other */
  const ccw = (x1, y1, x2, y2, x3, y3) => (y3 - y1) * (x2 - x1) > (y2 - y1) * (x3 - x1);
  const segX = (a, b) => ccw(a[0], a[1], b[0], b[1], b[2], b[3]) !== ccw(a[2], a[3], b[0], b[1], b[2], b[3]) &&
                         ccw(a[0], a[1], a[2], a[3], b[0], b[1]) !== ccw(a[0], a[1], a[2], a[3], b[2], b[3]);
  const leads = L.tags.map(t => ({ text: t.text, isArc: t.isArc, s: [t.ax, t.ay, t.x + t.w / 2, t.y + t.h / 2] }));
  for (let i = 0; i < leads.length; i++) {
    for (let j = i + 1; j < leads.length; j++) {
      if (segX(leads[i].s, leads[j].s)) bad.push('leader ' + leads[i].text + ' crosses leader ' + leads[j].text);
    }
    if (!leads[i].isArc && L.arcPts.length > 1) {
      for (let k = 1; k < L.arcPts.length; k++) {
        if (segX(leads[i].s, [L.arcPts[k - 1][0], L.arcPts[k - 1][1], L.arcPts[k][0], L.arcPts[k][1]])) {
          bad.push('leader ' + leads[i].text + ' crosses K3.arc');
          break;
        }
      }
    }
  }
  /* Check atom tag occlusion: no visible rear atom tag may sit inside a nearer atom sphere or overlap a nearer visible atom tag */
  const vis = L.atomTags.filter(a => a.visible);
  if (vis.length === 0) bad.push('all atom tags hidden');
  vis.forEach(a => {
    L.atomTags.forEach(b => {
      if (a.i === b.i) return;
      if (b.depth < a.depth - 0.04) {
        const d = Math.hypot(a.cx - b.cx, a.cy - b.cy);
        if (d < b.rPx + 1) bad.push('occluded atom tag ' + a.text + ' drawn over nearer sphere ' + b.text);
        if (b.visible) {
          const ox = Math.min(a.x + a.w * 0.85, b.x + b.w * 0.85) - Math.max(a.x + a.w * 0.15, b.x + b.w * 0.15);
          const oy = Math.min(a.y + a.h * 0.85, b.y + b.h * 0.85) - Math.max(a.y + a.h * 0.15, b.y + b.h * 0.15);
          if (ox > 1.5 && oy > 1.5) bad.push('atom tag ' + a.text + ' overlaps nearer tag ' + b.text);
        }
      }
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
      if (b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5) {
        out.push(t.textContent);
      }
    }
  }
  return out;
}"""


def zoom_around_arc(page, pad_x=115, pad_y=115):
    L = ev(page, "() => document.querySelector('.k').__sh.layout()")
    sb = page.eval_on_selector(
        '.stage',
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }',
    )
    pts = list(L['arcPts'])
    for t in L['tags']:
        if '平面' not in t['text']:
            pts.extend([[t['x'], t['y']], [t['x'] + t['w'], t['y'] + t['h']], [t['ax'], t['ay']]])
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    max_y = (L['tot']['y'] - 6) if L.get('tot') else sb['height']
    x0 = max(4.0, min(xs) - pad_x)
    y0 = max(float(L['hud']) + 2.0, min(ys) - pad_y * 0.45)
    x1 = min(sb['width'] - 4.0, max(xs) + pad_x)
    y1 = min(float(max_y), max(ys) + pad_y * 0.55)
    return {'x': sb['x'] + x0, 'y': sb['y'] + y0, 'width': max(160.0, x1 - x0), 'height': max(140.0, y1 - y0)}


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=ARGS)

    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1400}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, sc=scheme: errors.append(f'{sc}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, sc=scheme: errors.append(f'{sc}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.k[data-3d=ready]', timeout=30000)
        page.wait_for_timeout(450)
        sfx = '' if scheme == 'light' else '-dark'

        print(f'== {scheme}: startup & xrefs')
        check(f'{scheme}: 3D ready', page.get_attribute('.k', 'data-3d') == 'ready')
        check(f'{scheme}: default molecule is propene C1 (sp²)',
              page.get_attribute('.k', 'data-mol') == 'propene'
              and page.get_attribute('.k', 'data-c') == '1'
              and page.get_attribute('.k', 'data-hyb') == 'sp²')

        if scheme == 'light':
            xrefs = ev(page, "() => [...document.querySelectorAll('.k a.xref')].map(a => ({href: a.href, target: a.target, txt: a.textContent}))")
            check('xrefs: 2 links to ch03#hybrid and ch03#sigma-pi with target=_blank',
                  len(xrefs) == 2
                  and any('scrollTo=ch03-hybrid' in x['href'] and x['target'] == '_blank' for x in xrefs)
                  and any('scrollTo=ch03-sigma-pi' in x['href'] and x['target'] == '_blank' for x in xrefs),
                  str(xrefs))

            # Verify 3D SDF orientation & IUPAC geometry invariants
            geo = ev(page, "() => document.querySelector('.k').__sh.DATA")
            eth_y = [abs(a['p'][1]) for a in geo['ethene']['atoms']]
            check('ethene 3D: all 6 atoms lie on y=0 plane (|y| < 0.002 Å)', max(eth_y) < 0.002, str(eth_y))

            pr_atoms = geo['propene']['atoms']
            pr_cop = geo['propene']['meta']['plane']['coplanar']
            pr_out = geo['propene']['meta']['plane']['outH']
            check('propene 3D: 6 sp²-plane atoms on y=0 and 2 CH₃ H atoms stick out (|y| > 0.8 Å)',
                  len(pr_cop) == 6 and all(abs(pr_atoms[i]['p'][1]) < 0.002 for i in pr_cop)
                  and len(pr_out) == 2 and all(abs(pr_atoms[i]['p'][1]) > 0.80 for i in pr_out),
                  str([round(pr_atoms[i]['p'][1], 3) for i in range(len(pr_atoms))]))

            # Verify IUPAC numbering on propene: C1 (=CH₂) has 2 H + 1 C=C; C3 (–CH₃) has 3 H + 1 C–C
            pr_c1_at = geo['propene']['carbons'][0]['at']
            pr_c3_at = geo['propene']['carbons'][2]['at']
            pr_bonds = geo['propene']['bonds']
            c1_nb = [pr_atoms[bd[1] if bd[0] == pr_c1_at else bd[0]]['el'] for bd in pr_bonds if pr_c1_at in (bd[0], bd[1])]
            c3_nb = [pr_atoms[bd[1] if bd[0] == pr_c3_at else bd[0]]['el'] for bd in pr_bonds if pr_c3_at in (bd[0], bd[1])]
            check('propene IUPAC: C1 is =CH₂ (2 H, 1 C) and C3 is –CH₃ (3 H, 1 C)',
                  sorted(c1_nb) == ['C', 'H', 'H'] and sorted(c3_nb) == ['C', 'H', 'H', 'H'],
                  f'C1:{c1_nb} C3:{c3_nb}')

            # Verify ethyne & propanenitrile perpendicular π axes
            ey_pis = geo['ethyne']['meta']['pis']
            pn_pis = geo['propanenitrile']['meta']['pis']
            check('ethyne & propanenitrile: 2 mutually perpendicular π axes (dot = 0)',
                  len(ey_pis) == 2 and abs(dot(ey_pis[0]['axis'], ey_pis[1]['axis'])) < 1e-6
                  and len(pn_pis) == 2 and abs(dot(pn_pis[0]['axis'], pn_pis[1]['axis'])) < 1e-6)

        # Default screenshots (propene C1)
        shot(page, '.k', OUT / f'01-propene-c1{sfx}.png')
        shot(page, '.stage', OUT / f'z-propene-stage{sfx}.png')
        shot(page, '.sh-info', OUT / f'z-info-propene{sfx}.png')

        # Sweep all 7 molecules
        print(f'== {scheme}: all 7 molecules & C selection')
        mol_hashes = {}
        for mid, spec in MOLS.items():
            page.click(f'[data-mol="{mid}"]')
            page.wait_for_timeout(300)
            c_stat = ev(page, CANVAS_JS)
            mol_hashes[mid] = c_stat['hash']
            tot_s, tot_p = spec['tot']

            check(f'{scheme} {mid}: canvas rendered (std > 8)', c_stat['std'] > 8, f"std={c_stat['std']:.2f}")
            check(f'{scheme} {mid}: corner total {tot_s} σ + {tot_p} π',
                  page.inner_text('.sh-tot-s') == f'{tot_s} σ'
                  and page.inner_text('.sh-tot-p') == f'{tot_p} π'
                  and page.get_attribute('.k', 'data-tot-sigma') == str(tot_s)
                  and page.get_attribute('.k', 'data-tot-pi') == str(tot_p),
                  page.inner_text('.sh-tot'))
            check(f'{scheme} {mid}: 3D π bond & K3.porb count = {tot_p} / {2 * tot_p}',
                  ev(page, "() => document.querySelector('.k').__sh.piCount3D()") == tot_p
                  and ev(page, "() => document.querySelector('.k').__sh.porbCount3D()") == 2 * tot_p)

            # Check layout, non-overlapping spheres & full atom-tag visibility on default C1 view of every molecule
            bad = ev(page, LAYOUT_BAD_JS)
            check(f'{scheme} {mid} C1: labels, arc-ring clearance & occlusion clean', not bad, '; '.join(bad))
            if scheme == 'light':
                sep_info = ev(page, """() => {
                  const L = document.querySelector('.k').__sh.layout();
                  let minRatio = 999;
                  for (let i = 0; i < L.atoms.length; i++) {
                    for (let j = i + 1; j < L.atoms.length; j++) {
                      const d = Math.hypot(L.atoms[i].x - L.atoms[j].x, L.atoms[i].y - L.atoms[j].y);
                      minRatio = Math.min(minRatio, d / (L.atoms[i].r + L.atoms[j].r));
                    }
                  }
                  const hidden = L.atomTags.filter(a => !a.visible).map(a => a.text);
                  return { minRatio, hidden };
                }""")
                check(f'{mid} default view: all atom spheres separated (ratio ≥ 1.15) & 0 hidden atom tags',
                      sep_info['minRatio'] >= 1.15 and len(sep_info['hidden']) == 0,
                      str(sep_info))

            # Check carbons: test all carbons in light mode, first & last in dark mode
            carb_list = spec['carbons'] if scheme == 'light' else [spec['carbons'][0], spec['carbons'][-1]]
            seen_c = set()
            for cnum, hyb, shape, ang_txt, deg_val, csig, cpi in carb_list:
                if cnum in seen_c:
                    continue
                seen_c.add(cnum)
                page.click(f'.sh-cbars button[data-cnum="{cnum}"]')
                page.wait_for_timeout(180)
                exp_sp = f'{csig} σ + {cpi} π' if cpi else f'{csig} σ（0 π）'
                got_hyb = page.inner_text('.sh-hyb').strip()
                got_shape = page.inner_text('.sh-shape').strip()
                got_ang = page.inner_text('.sh-ang').strip()
                got_csp = page.inner_text('.sh-csp').splitlines()[0].strip()
                arc = ev(page, "() => document.querySelector('.k').__sh.arc()")
                check(f'{scheme} {mid} C{cnum}: {hyb} / {shape} / {ang_txt} / {exp_sp} + K3.arc matches',
                      got_hyb == hyb and got_shape == shape and got_ang == ang_txt and got_csp == exp_sp
                      and arc is not None and arc['text'] == ang_txt and abs(arc['deg'] - deg_val) < 4.5,
                      f'got=({got_hyb},{got_shape},{got_ang},{got_csp}) arc={arc}')

                # Angle tag proximity & colour
                L = ev(page, "() => document.querySelector('.k').__sh.layout()")
                at = [x for x in L['tags'] if x['isArc']]
                if at:
                    a0 = at[0]
                    dx = max(a0['x'] - a0['ax'], 0, a0['ax'] - (a0['x'] + a0['w']))
                    dy = max(a0['y'] - a0['ay'], 0, a0['ay'] - (a0['y'] + a0['h']))
                    gap = math.hypot(dx, dy)
                    check(f'{scheme} {mid} C{cnum}: angle label near arc (≤ 52 px) in --s3',
                          gap <= 52 and a0['band'] == 'ang', f'gap={gap:.1f}')

                bad_c = ev(page, LAYOUT_BAD_JS)
                check(f'{scheme} {mid} C{cnum}: layout clean', not bad_c, '; '.join(bad_c))

            # Capture key molecule screenshots
            if mid == 'propene':
                page.click('.sh-cbars button[data-cnum="3"]')
                page.wait_for_timeout(200)
                shot(page, '.k', OUT / f'02-propene-c3{sfx}.png')
                if scheme == 'light':
                    shot_clip(page, zoom_around_arc(page, 110, 95), OUT / 'z-propene-c3-angle.png')
            elif mid == 'ethene':
                page.click('.sh-cbars button[data-cnum="1"]')
                page.wait_for_timeout(200)
                shot(page, '.k', OUT / f'03-ethene-planar{sfx}.png')
            elif mid == 'ethyne':
                page.click('.sh-cbars button[data-cnum="1"]')
                page.wait_for_timeout(200)
                shot(page, '.k', OUT / f'04-ethyne-2pi{sfx}.png')
                shot_clip(page, zoom_around_arc(page, 120, 95), OUT / f'z-ethyne-180-2pi{sfx}.png')
            elif mid == 'ethanal':
                page.click('.sh-cbars button[data-cnum="1"]')
                page.wait_for_timeout(200)
                shot(page, '.k', OUT / f'05-ethanal-c1{sfx}.png')
                if scheme == 'light':
                    shot(page, '.stage', OUT / 'z-ethanal-stage.png')
            elif mid == 'propanenitrile':
                page.click('.sh-cbars button[data-cnum="1"]')
                page.wait_for_timeout(200)
                shot(page, '.k', OUT / f'06-propanenitrile-c1{sfx}.png')
                if scheme == 'light':
                    shot_clip(page, zoom_around_arc(page, 135, 100), OUT / 'z-propanenitrile-cn.png')
            elif mid == 'cyclohexane':
                if scheme == 'light':
                    page.click('.sh-cbars button[data-cnum="4"]')
                    page.wait_for_timeout(200)
                    shot_clip(page, zoom_around_arc(page, 120, 95), OUT / 'z-cyclohexane-c4-rear.png')
                page.click('.sh-cbars button[data-cnum="1"]')
                page.wait_for_timeout(200)
                shot(page, '.k', OUT / f'07-cyclohexane-chair{sfx}.png')
                if scheme == 'light':
                    shot_clip(page, zoom_around_arc(page, 115, 95), OUT / 'z-cyclohexane-c1-angle.png')

        check(f'{scheme}: all 7 molecules produce 7 distinct canvas renders', len(set(mol_hashes.values())) == 7)

        # Ethane with σ sleeves toggled ON (both light and dark)
        page.click('[data-mol="ethane"]')
        page.wait_for_timeout(220)
        h_before_sig = ev(page, CANVAS_JS)['hash']
        page.click('[data-tog="sigma"]')
        page.wait_for_timeout(220)
        h_after_sig = ev(page, CANVAS_JS)['hash']
        check(f'{scheme}: σ toggle changes 3D render', h_after_sig != h_before_sig)
        shot(page, '.k', OUT / f'08-ethane-sigma{sfx}.png')
        page.click('[data-tog="sigma"]')
        page.wait_for_timeout(180)

        check(f'{scheme}: no [data-clash]', page.locator('[data-clash]').count() == 0)
        check(f'{scheme}: HTML font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))

        if scheme == 'light':
            print('== 3D raycast C-atom click, toggles, drag, zoom, spin')
            page.click('[data-mol="propene"]')
            page.wait_for_timeout(250)
            check('raycast start: propene on C1', page.get_attribute('.k', 'data-c') == '1')
            cb = page.locator('.stage canvas').bounding_box()
            c3_scr = ev(page, "() => document.querySelector('.k').__sh.carbonScreen(3)")
            page.mouse.click(cb['x'] + c3_scr['x'], cb['y'] + c3_scr['y'])
            page.wait_for_timeout(250)
            check('3D canvas click on propene C3 selects C3 (sp³ 109.5°)',
                  page.get_attribute('.k', 'data-c') == '3'
                  and page.inner_text('.sh-hyb').strip() == 'sp³'
                  and page.inner_text('.sh-ang').strip() == '109.5°')
            c1_scr = ev(page, "() => document.querySelector('.k').__sh.carbonScreen(1)")
            page.mouse.click(cb['x'] + c1_scr['x'], cb['y'] + c1_scr['y'])
            page.wait_for_timeout(250)
            check('3D canvas click back on propene C1 selects C1 (sp² 120°)',
                  page.get_attribute('.k', 'data-c') == '1'
                  and page.inner_text('.sh-hyb').strip() == 'sp²')

            # Toggle planar & pi on propene
            h0 = ev(page, CANVAS_JS)['hash']
            page.click('[data-tog="planar"]')
            page.wait_for_timeout(220)
            h_no_pl = ev(page, CANVAS_JS)['hash']
            check('planar toggle off changes propene render', h_no_pl != h0)
            page.click('[data-tog="planar"]')
            page.wait_for_timeout(220)

            page.click('[data-tog="pi"]')
            page.wait_for_timeout(220)
            check('π toggle off removes K3.porb meshes and changes render',
                  ev(page, "() => document.querySelector('.k').__sh.porbCount3D()") == 0
                  and ev(page, CANVAS_JS)['hash'] != h0)
            page.click('[data-tog="pi"]')
            page.wait_for_timeout(220)

            # Drag to rotate, check hash changes & labels re-place cleanly, then reset
            c0 = ev(page, CANVAS_JS)
            page.mouse.move(cb['x'] + cb['width'] * 0.35, cb['y'] + cb['height'] * 0.55)
            page.mouse.down()
            page.mouse.move(cb['x'] + cb['width'] * 0.62, cb['y'] + cb['height'] * 0.68, steps=8)
            page.mouse.up()
            page.wait_for_timeout(420)
            c_drag = ev(page, CANVAS_JS)
            check('drag rotates molecule (canvas hash changes)', c_drag['hash'] != c0['hash'])
            bad_drag = ev(page, LAYOUT_BAD_JS)
            check('after drag: labels re-placed cleanly & no occluded atom tag', not bad_drag, '; '.join(bad_drag))
            shot(page, '.k', OUT / '50-propene-dragged.png')

            page.click('[data-3d="reset"]')
            page.wait_for_timeout(400)
            check('复位视角 restores exact view', ev(page, CANVAS_JS)['hash'] == c0['hash'])

            # Wheel zoom keeps sprite pixel height constant
            page.mouse.move(cb['x'] + cb['width'] * 0.5, cb['y'] + cb['height'] * 0.5)
            page.mouse.wheel(0, -320)
            page.wait_for_timeout(400)
            Lz = ev(page, "() => document.querySelector('.k').__sh.layout()")
            check('wheel zoom: floating tags keep target screen px height (26 / 22 px)',
                  all(abs(t['h'] - (22 if '平面' in t['text'] else 26)) < 1.8 for t in Lz['tags']),
                  str([(t['text'], round(t['h'], 1)) for t in Lz['tags']]))
            page.click('[data-3d="reset"]')
            page.wait_for_timeout(300)

            # Auto-spin advances frames & stops cleanly
            page.click('[data-3d="spin"]')
            spin_hashes = []
            for _ in range(6):
                page.wait_for_timeout(240)
                spin_hashes.append(ev(page, CANVAS_JS)['hash'])
            check('自动旋转 advances frames (≥ 3 distinct hashes in 6 samples)', len(set(spin_hashes)) >= 3, str(len(set(spin_hashes))))
            page.click('[data-3d="spin"]')
            page.wait_for_timeout(450)
            h_stop = ev(page, CANVAS_JS)['hash']
            page.wait_for_timeout(350)
            check('spin off stops motion', ev(page, CANVAS_JS)['hash'] == h_stop)
            page.click('[data-3d="reset"]')
            page.wait_for_timeout(300)

            # Narrow 720 px viewport
            print('== narrow (720 px)')
            page.set_viewport_size({'width': 720, 'height': 1600})
            page.wait_for_timeout(650)
            ov = ev(page, "() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('720px: .k has no horizontal overflow', ov[0] <= ov[1] + 1, str(ov))
            check('720px: HTML font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)[:5]))
            bad_narrow = []
            for mid in MOLS:
                page.click(f'[data-mol="{mid}"]')
                page.wait_for_timeout(240)
                lb = ev(page, LAYOUT_BAD_JS)
                if lb:
                    bad_narrow.append(f'{mid}: {lb}')
            check('720px: labels & atom-tag occlusion clean across all 7 molecules', not bad_narrow, '; '.join(bad_narrow))
            page.click('[data-mol="propene"]')
            page.wait_for_timeout(250)
            shot(page, '.k', OUT / '60-narrow-720-propene.png')
            page.click('[data-mol="propanenitrile"]')
            page.wait_for_timeout(250)
            shot(page, '.k', OUT / '61-narrow-720-propanenitrile.png')

        ctx.close()

    print('== fallback (CDN blocked)')
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1400}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('pageerror', lambda e, sc=scheme: errors.append(f'fallback-{sc}: PAGEERROR {e}'))
        page.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
        page.goto(PAGE.as_uri())
        page.wait_for_selector('.fallback.show', timeout=20000)
        page.wait_for_timeout(250)
        sfx = '' if scheme == 'light' else '-dark'

        check(f'{scheme} fallback: .fallback.show & data-3d=fallback', page.get_attribute('.k', 'data-3d') == 'fallback')
        check(f'{scheme} fallback: 3D stage & 3D-only buttons hidden',
              not page.locator('.sh-main .stage').is_visible()
              and not page.locator('[data-3d="reset"]').is_visible())
        fb_txt = ev(page, "() => [...document.querySelectorAll('.sh-fb svg text')].map(t => t.textContent).join(' | ')")
        check(f'{scheme} fallback SVG: shows propene (8 σ + 1 π, 120°, 109.5°) & ethyne (3 σ + 2 π, 180°)',
              all(s in fb_txt for s in ('propene', '8 σ + 1 π', '120°', '109.5°', 'ethyne', '3 σ + 2 π', '180°')),
              fb_txt)
        check(f'{scheme} fallback SVG: no [data-clash]', page.locator('[data-clash]').count() == 0,
              str(ev(page, "() => [...document.querySelectorAll('[data-clash]')].map(e => e.textContent)")))
        check(f'{scheme} fallback SVG: all text inside viewBox', not ev(page, SVG_OUTSIDE_JS), str(ev(page, SVG_OUTSIDE_JS)))
        check(f'{scheme} fallback SVG: font ≥ 12px', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)))

        # Info card still interactive in fallback mode
        page.click('[data-mol="propanenitrile"]')
        page.wait_for_timeout(120)
        check(f'{scheme} fallback: info card switches to propanenitrile C1 sp 180° (8 σ + 2 π)',
              page.inner_text('.sh-hyb').strip() == 'sp'
              and page.inner_text('.sh-ang').strip() == '180°'
              and page.get_attribute('.k', 'data-tot-sigma') == '8'
              and page.get_attribute('.k', 'data-tot-pi') == '2')
        page.click('.sh-cbars button[data-cnum="2"]')
        page.wait_for_timeout(120)
        check(f'{scheme} fallback: C2 button switches info card to sp³ 109.5°',
              page.inner_text('.sh-hyb').strip() == 'sp³' and page.inner_text('.sh-ang').strip() == '109.5°')

        page.click('[data-mol="propene"]')
        page.wait_for_timeout(120)
        shot(page, '.k', OUT / f'70-fallback{sfx}.png')
        shot(page, '.sh-fb', OUT / f'z-fallback-svg{sfx}.png')

        if scheme == 'light':
            page.set_viewport_size({'width': 720, 'height': 1500})
            page.wait_for_timeout(250)
            ov_fb = ev(page, "() => { const k = document.querySelector('.k'); return [k.scrollWidth, k.clientWidth]; }")
            check('fallback 720px: no overflow', ov_fb[0] <= ov_fb[1] + 1, str(ov_fb))
            check('fallback 720px: SVG font ≥ 12px', not ev(page, SVG_SMALL_JS), str(ev(page, SVG_SMALL_JS)))
            check('fallback 720px: HTML font ≥ 12px', not ev(page, SMALL_JS), str(ev(page, SMALL_JS)))
            shot(page, '.k', OUT / '71-fallback-narrow-720.png')

        ctx.close()

    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for _, ok, _ in results if ok)
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
