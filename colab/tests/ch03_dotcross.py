"""ch03 dotcross cell test: dot-and-cross diagrams (ionic / covalent / coordinate).

usage: uv run --with playwright python -I colab/tests/ch03_dotcross.py <preview.html> <shots-dir>
(build the preview first: COLAB_TMP=… python3 tools/build_colab.py ch03 --cell dotcross)
"""
import math
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1])
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
ER = 3.3


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


GROUP = {'NaCl': 'ion', 'MgO': 'ion', 'CaF2': 'ion', 'Na2O': 'ion', 'MgCl2': 'ion', 'Li2O': 'ion',
         'H2': 'cov', 'Cl2': 'cov', 'HCl': 'cov', 'O2': 'cov', 'N2': 'cov', 'CO2': 'cov', 'NH3': 'cov', 'CH4': 'cov',
         'H2O': 'cov', 'C2H6': 'cov', 'C2H4': 'cov', 'HCN': 'cov', 'BF3': 'cov', 'SO2': 'cov', 'PCl5': 'cov',
         'SF6': 'cov', 'SCl2': 'cov', 'NO': 'cov', 'NH4Cl': 'dat', 'Al2Cl6': 'dat', 'BF3NH3': 'dat'}


def pick(page, sp):
    g = GROUP[sp]
    if 'on' not in (page.get_attribute(f'.dc-groups button[data-g="{g}"]', 'class') or ''):
        page.click(f'.dc-groups button[data-g="{g}"]')
    page.click(f'.dc-chips button[data-sp="{sp}"]')


def setbox(page, sel, on):
    if page.is_checked(sel) != on:
        page.click(sel)


# everything drawn in the dot-and-cross svg, in svg units
GEO_JS = '''() => {
  const svg = document.querySelector('.dc-svg');
  const atoms = [...svg.querySelectorAll('circle.dc-shell')].map(c => ({id: c.dataset.atom, el: c.dataset.el,
      x: +c.getAttribute('cx'), y: +c.getAttribute('cy'), r: +c.getAttribute('r'), empty: c.classList.contains('dc-empty')}));
  const es = [...svg.querySelectorAll('g.dc-e')].map(g => ({atoms: g.dataset.atoms.split(' '), kind: g.dataset.kind, mk: g.dataset.mk,
      x: +g.dataset.x, y: +g.dataset.y, dative: +g.dataset.dative, owner: g.dataset.owner, bond: g.dataset.bond}));
  // glyph box: getBBox is the em box (ascent + descent); element symbols are capitals, so use ±0.4 em round the centre
  const syms = [...svg.querySelectorAll('text.dc-sym')].map(t => { const b = t.getBBox(), fs = parseFloat(getComputedStyle(t).fontSize);
      return {id: t.dataset.atom, x: b.x, y: b.y + b.height / 2 - 0.4 * fs, w: b.width, h: 0.8 * fs}; });
  const labels = [...svg.querySelectorAll('text.halo')].map(t => { const b = t.getBBox(); return {t: t.textContent, x: b.x, y: b.y, w: b.width, h: b.height}; });
  const vb = svg.getAttribute('viewBox').split(' ').map(Number);
  return {atoms, es, syms, labels, vb, clash: document.querySelectorAll('.k [data-clash]').length,
          charges: [...svg.querySelectorAll('[data-charge]')].map(t => t.dataset.charge),
          coefs: [...svg.querySelectorAll('[data-coef]')].map(t => t.dataset.coef),
          arrows: [...document.querySelectorAll('.dc-struct [data-arrow]')].map(t => t.dataset.arrow),
          ann: [...svg.querySelectorAll('[data-ann]')].map(t => t.textContent)};
}'''


def count(geo, el):
    """electron count round every atom of element el, in drawing order"""
    return [sum(1 for e in geo['es'] if a['id'] in e['atoms']) for a in geo['atoms'] if a['el'] == el]


def geometry_bad(geo):
    """shared pairs inside both circles, nothing else inside a foreign circle, no electron overlaps,
    nothing on an element symbol, unbonded circles apart"""
    bad = []
    A = {a['id']: a for a in geo['atoms']}
    for e in geo['es']:
        for a in geo['atoms']:
            d = math.hypot(e['x'] - a['x'], e['y'] - a['y'])
            if a['id'] in e['atoms']:
                if e['kind'] == 'bond' and d > a['r'] - ER + 0.3:
                    bad.append(f"bond e not inside {a['id']} ({d:.1f}>{a['r'] - ER:.1f})")
                if e['kind'] in ('lp', 'one', 'shell', 'gain') and d > a['r'] + 0.5:
                    bad.append(f"{e['kind']} e off {a['id']}")
            elif d < a['r'] + ER - 0.3:
                bad.append(f"{e['kind']} e of {e['atoms']} inside foreign circle {a['id']} ({d:.1f})")
        if e['kind'] == 'bond' and len(e['atoms']) != 2:
            bad.append('bond e without two atoms')
    es = geo['es']
    for i in range(len(es)):
        for j in range(i + 1, len(es)):
            d = math.hypot(es[i]['x'] - es[j]['x'], es[i]['y'] - es[j]['y'])
            if d < 2 * ER + 1.6:
                bad.append(f'electrons overlap {d:.1f} at ({es[i]["x"]:.0f},{es[i]["y"]:.0f})')
    for s in geo['syms']:
        for e in es:
            # distance from the electron centre to the glyph box must exceed the mark radius + a hair
            dx = max(s['x'] - e['x'], 0, e['x'] - s['x'] - s['w']); dy = max(s['y'] - e['y'], 0, e['y'] - s['y'] - s['h'])
            if math.hypot(dx, dy) < ER + 0.9:
                bad.append(f"electron on symbol {s['id']}")
    bonded = {tuple(sorted(e['atoms'])) for e in es if e['kind'] == 'bond'}
    ats = geo['atoms']
    for i in range(len(ats)):
        for j in range(i + 1, len(ats)):
            a, b = ats[i], ats[j]
            d = math.hypot(a['x'] - b['x'], a['y'] - b['y'])
            key = tuple(sorted((a['id'], b['id'])))
            if key in bonded and d >= a['r'] + b['r']:
                bad.append(f'bonded circles {key} do not intersect')
            if key not in bonded and d < a['r'] + b['r'] + 0.5:
                bad.append(f'unbonded circles {key} touch ({d:.1f} < {a["r"] + b["r"]})')
    # labels must not sit on electrons or symbols
    for l in geo['labels']:
        for e in es:
            if e['x'] + 4 > l['x'] and e['x'] - 4 < l['x'] + l['w'] and e['y'] + 4 > l['y'] and e['y'] - 4 < l['y'] + l['h']:
                bad.append(f"label '{l['t']}' on an electron")
    return bad


def pairs_in_bond(geo, a_el, b_el):
    """electrons shared by the first a_el atom and the first b_el atom it is bonded to"""
    out = {}
    for e in geo['es']:
        if e['kind'] == 'bond':
            k = tuple(sorted(e['atoms']))
            out[k] = out.get(k, 0) + 1
    A = {a['id']: a['el'] for a in geo['atoms']}
    return sorted(v // 2 for k, v in out.items() if sorted((A[k[0]], A[k[1]])) == sorted((a_el, b_el)))


SMALL_JS = '''() => { const out = [];
  for (const e of document.querySelectorAll('.k *')) {
    if (e.closest('svg')) continue;
    if (!e.offsetParent) continue;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own && parseFloat(getComputedStyle(e).fontSize) < 12) out.push(e.tagName + '.' + e.className + ':' + e.textContent.slice(0, 20));
  }
  for (const svg of document.querySelectorAll('.k svg.dc-svg, .k svg.dc-struct')) {
    const r = svg.getBoundingClientRect(); if (!r.width) continue;
    const vb = svg.getAttribute('viewBox').split(' ').map(Number), k = r.width / vb[2];
    for (const t of svg.querySelectorAll('text')) {
      const fs = parseFloat(getComputedStyle(t).fontSize) * k;
      if (fs < 12) out.push('svg text ' + t.textContent + ' ' + fs.toFixed(1) + 'px');
    }
    // electron marks: a mark must stay ≥ 7px across to be told apart
    if (svg.classList.contains('dc-svg') && 2 * 3.3 * k < 7) out.push('electron mark ' + (6.6 * k).toFixed(1) + 'px');
  }
  return out; }'''

OVER_JS = '''() => { const k = document.querySelector('.k'); const bad = [];
  if (k.scrollWidth > k.clientWidth + 1) bad.push('card ' + k.scrollWidth + '>' + k.clientWidth);
  for (const s of document.querySelectorAll('.dc-svg, .dc-struct')) {
    const r = s.getBoundingClientRect(), p = s.parentElement.getBoundingClientRect();
    if (r.width && r.right > p.right + 1) bad.push(s.className.baseVal + ' sticks out');
  }
  return bad; }'''

# expected electron counts round each atom of the element (drawing order)
EXPECT = {
    'H2': {'H': [2, 2]}, 'Cl2': {'Cl': [8, 8]}, 'HCl': {'H': [2], 'Cl': [8]}, 'O2': {'O': [8, 8]}, 'N2': {'N': [8, 8]},
    'CO2': {'C': [8], 'O': [8, 8]}, 'NH3': {'N': [8], 'H': [2, 2, 2]}, 'CH4': {'C': [8], 'H': [2] * 4},
    'H2O': {'O': [8], 'H': [2, 2]}, 'C2H6': {'C': [8, 8], 'H': [2] * 6}, 'C2H4': {'C': [8, 8], 'H': [2] * 4},
    'HCN': {'H': [2], 'C': [8], 'N': [8]}, 'BF3': {'B': [6], 'F': [8] * 3}, 'SO2': {'S': [10], 'O': [8, 8]},
    'PCl5': {'P': [10], 'Cl': [8] * 5}, 'SF6': {'S': [12], 'F': [8] * 6}, 'SCl2': {'S': [8], 'Cl': [8, 8]},
    'NO': {'N': [7], 'O': [8]}, 'Al2Cl6': {'Al': [8, 8], 'Cl': [8] * 6}, 'BF3NH3': {'B': [8], 'N': [8], 'F': [8] * 3, 'H': [2] * 3},
    'NaCl': {'Na': [0], 'Cl': [8]}, 'MgO': {'Mg': [0], 'O': [8]}, 'CaF2': {'Ca': [0], 'F': [8, 8]},
    'Na2O': {'Na': [0, 0], 'O': [8]}, 'MgCl2': {'Mg': [0], 'Cl': [8, 8]}, 'Li2O': {'Li': [0, 0], 'O': [8]},
}
# central atom: outer electrons, bonding pairs, lone pairs, total outer electrons drawn, tag
CARD = {'H2': (2, 1, 0, 2, 'duplet'), 'Cl2': (8, 1, 3, 14, 'octet'), 'HCl': (8, 1, 3, 8, 'octet'), 'O2': (8, 2, 2, 12, 'octet'),
        'N2': (8, 3, 1, 10, 'octet'), 'CO2': (8, 4, 0, 16, 'octet'), 'NH3': (8, 3, 1, 8, 'octet'), 'CH4': (8, 4, 0, 8, 'octet'),
        'H2O': (8, 2, 2, 8, 'octet'), 'C2H6': (8, 4, 0, 14, 'octet'), 'C2H4': (8, 4, 0, 12, 'octet'), 'HCN': (8, 4, 0, 10, 'octet'),
        'BF3': (6, 3, 0, 24, 'electron deficient'), 'SO2': (10, 4, 1, 18, 'expanded octet'), 'PCl5': (10, 5, 0, 40, 'expanded octet'),
        'SF6': (12, 6, 0, 48, 'expanded octet'), 'SCl2': (8, 2, 2, 20, 'octet'), 'NO': (7, 2, 1, 11, 'radical'),
        'Al2Cl6': (8, 4, 0, 48, 'octet'), 'BF3NH3': (8, 4, 0, 32, 'octet')}
MARKS = {'SCl2': {'S': {'dot'}, 'Cl': {'cross'}}}

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        sfx = '' if scheme == 'light' else '-dark'

        def shot(name, sel='.k'):
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        if scheme == 'dark':
            pick(page, 'NaCl'); shot('01-ionic-NaCl')
            pick(page, 'SCl2'); shot('10-cov-SCl2')
            pick(page, 'Al2Cl6'); shot('20-dat-Al2Cl6')
            for i, sp in enumerate(GROUP):
                pick(page, sp)
                if sp == 'NH4Cl':
                    page.click('.dc-steps button[data-step="2"]')
                shot(f'z{i:02d}-{sp}', '.dc-fig')
            pick(page, 'Li2O'); setbox(page, '.dc-all', True); shot('z-Li2O-all', '.dc-fig'); setbox(page, '.dc-all', False)
            pick(page, 'NH4Cl'); shot('z-NH4Cl-step1', '.dc-fig')
            setbox(page, '.dc-exam', True); pick(page, 'SO2'); page.click('.dc-next'); shot('z-exam-SO2-stage1', '.dc-fig')
            setbox(page, '.dc-exam', False)
            check('dark: no [data-clash]', page.locator('[data-clash]').count() == 0)
            ctx.close(); continue

        print('== every species: counts, geometry, card')
        for sp in GROUP:
            pick(page, sp)
            if sp == 'NH4Cl':
                continue
            geo = page.evaluate(GEO_JS)
            exp = EXPECT[sp]
            got = {el: count(geo, el) for el in exp}
            check(f'{sp}: electrons per atom {exp}', got == exp, str(got))
            bad = geometry_bad(geo)
            check(f'{sp}: geometry (pairs in lens, no overlaps, symbols clear)', not bad, '; '.join(bad[:4]))
            check(f'{sp}: no [data-clash]', geo['clash'] == 0, str(geo['clash']))
            if sp in CARD:
                ce, bp, lp, tot, tag = CARD[sp]
                card = page.locator('.dc-count')
                vals = (int(card.get_attribute('data-ce')), float(card.get_attribute('data-bp')), float(card.get_attribute('data-lp')), int(card.get_attribute('data-tot')))
                check(f'{sp}: card central {ce} e, {bp} bp, {lp} lp, total {tot}', vals == (ce, bp, lp, tot), str(vals))
                check(f'{sp}: card tag "{tag}"', tag in page.inner_text('.dc-count'), page.inner_text('.dc-count')[:120])
            if sp in MARKS:
                for el, mks in MARKS[sp].items():
                    ids = {a['id'] for a in geo['atoms'] if a['el'] == el}
                    own = {e['mk'] for e in geo['es'] if e['kind'] == 'lp' and e['owner'] in ids}
                    check(f'{sp}: non-bonding electrons of {el} only {mks}', own == mks, str(own))

        print('== specific bonds')
        pick(page, 'O2'); check('O₂: 2 shared pairs', pairs_in_bond(page.evaluate(GEO_JS), 'O', 'O') == [2])
        pick(page, 'N2'); check('N₂: 3 shared pairs', pairs_in_bond(page.evaluate(GEO_JS), 'N', 'N') == [3])
        pick(page, 'C2H4'); check('C₂H₄: C=C 2 shared pairs', pairs_in_bond(page.evaluate(GEO_JS), 'C', 'C') == [2])
        pick(page, 'CO2'); check('CO₂: two C=O of 2 pairs', pairs_in_bond(page.evaluate(GEO_JS), 'C', 'O') == [2, 2])
        pick(page, 'HCN'); g = page.evaluate(GEO_JS)
        check('HCN: C≡N 3 pairs, H–C 1 pair', pairs_in_bond(g, 'C', 'N') == [3] and pairs_in_bond(g, 'C', 'H') == [1])
        check('HCN: N 1 lone pair', sum(1 for e in g['es'] if e['kind'] == 'lp' and e['owner'] == 'n') == 2)
        check('HCN: three different marks', len({e['mk'] for e in g['es']}) == 3)
        pick(page, 'SCl2'); g = page.evaluate(GEO_JS)
        mixed = all({x['mk'] for x in g['es'] if x['kind'] == 'bond' and x['bond'] == bi} == {'dot', 'cross'} for bi in ('0', '1'))
        check('SCl₂ M1: each S–Cl pair is one • and one ×', mixed)
        check('SCl₂: S has 2 lone pairs', sum(1 for e in g['es'] if e['kind'] == 'lp' and e['owner'] == 's') == 4)
        check('SCl₂: mark scheme M1 / M2 shown', 'M1' in page.inner_text('.dc-note') and 'M2' in page.inner_text('.dc-note') and '9701/21 May/June 2024 Q2(b)(i)' in page.inner_text('.dc-note'))
        pick(page, 'SF6'); check('SF₆: mark scheme 9701/21 May/June 2026 Q1(a)(i)', '9701/21 May/June 2026 Q1(a)(i)' in page.inner_text('.dc-note'))
        g = page.evaluate(GEO_JS)
        check('SF₆: S has no lone pair', not [e for e in g['es'] if e['kind'] == 'lp' and e['owner'] == 's'])
        pick(page, 'NO'); g = page.evaluate(GEO_JS)
        ones = [e for e in g['es'] if e['kind'] == 'one']
        check('NO: exactly 1 unpaired electron, on N', len(ones) == 1 and ones[0]['owner'] == 'n', str(ones))
        check('NO: total outer electrons 11', len(g['es']) == 11)
        check('NO: N has 1 lone pair, O has 2', sum(1 for e in g['es'] if e['kind'] == 'lp' and e['owner'] == 'n') == 2 and
              sum(1 for e in g['es'] if e['kind'] == 'lp' and e['owner'] == 'o') == 4)
        check('NO: N=O double bond', pairs_in_bond(g, 'N', 'O') == [2])
        check('NO: "unpaired electron → (free) radical" label', g['ann'] == ['unpaired electron → (free) radical'], str(g['ann']))
        check('NO: unpaired ring drawn', page.locator('.dc-svg .dc-ring').count() == 1)
        check('NO: radical tag on the card', 'radical' in page.inner_text('.dc-count'))
        shot('11-cov-NO')
        pick(page, 'BF3'); check('BF₃: "electron deficient" on the card', 'electron deficient' in page.inner_text('.dc-count'))

        print('== ionic options')
        pick(page, 'NaCl'); g = page.evaluate(GEO_JS)
        check('NaCl: charges + and −', g['charges'] == ['+', '−'], str(g['charges']))
        check('NaCl: Na⁺ shell drawn dashed (empty)', [a['empty'] for a in g['atoms']] == [True, False])
        cl = [e for e in g['es'] if e['atoms'] == ['Cl1']]
        check('NaCl: Cl⁻ = 7 • + 1 × (transferred)', sorted(e['mk'] for e in cl) == ['cross'] + ['dot'] * 7)
        # charge label at the top-right of the bracket
        lab = [l for l in g['labels'] if l['t'] == '−'][0]; clc = [a for a in g['atoms'] if a['id'] == 'Cl1'][0]
        check('NaCl: Cl⁻ charge at top-right', lab['x'] > clc['x'] + clc['r'] and lab['y'] + lab['h'] < clc['y'] - clc['r'] + 6, str(lab))
        check('NaCl: card says Na⁺ 0 / Cl⁻ 8, = Ne / = Ar', page.inner_text('.dc-count tr[data-ion="Na"] [data-k=drawn]') == '0' and
              page.inner_text('.dc-count tr[data-ion="Cl"] [data-k=drawn]') == '8' and '（= Ne）' in page.inner_text('.dc-count') and '（= Ar）' in page.inner_text('.dc-count'))
        shot('01-ionic-NaCl')
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-NaCl.png'))
        setbox(page, '.dc-new', True); g = page.evaluate(GEO_JS)
        check('show new outer shell: Na⁺ 8 (own ×)', count(g, 'Na') == [8] and {e['mk'] for e in g['es'] if e['atoms'] == ['Na1']} == {'cross'})
        check('show new outer shell: geometry ok', not geometry_bad(g), str(geometry_bad(g)[:3]))
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-NaCl-newshell.png'))
        pick(page, 'Li2O'); g = page.evaluate(GEO_JS)
        check('Li₂O new outer shell: each Li⁺ 2 (1s²)', count(g, 'Li') == [2, 2], str(count(g, 'Li')))
        setbox(page, '.dc-new', False)
        pick(page, 'CaF2'); g = page.evaluate(GEO_JS)
        check('CaF₂: drawn twice by default (2 F⁻ brackets, no coefficient)', count(g, 'F') == [8, 8] and g['coefs'] == [] and g['charges'] == ['2+', '−', '−'])
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-CaF2.png'))
        setbox(page, '.dc-coef', True); g = page.evaluate(GEO_JS)
        check('CaF₂ coefficient: one F⁻ with "2" before the bracket', count(g, 'F') == [8] and g['coefs'] == ['2'], f"{count(g, 'F')} {g['coefs']}")
        check('CaF₂ coefficient: 2 sits left of the F⁻ bracket', (lambda l, f: l['x'] + l['w'] < f['x'] - f['r'])(
            [l for l in g['labels'] if l['t'] == '2'][0], [a for a in g['atoms'] if a['el'] == 'F'][0]))
        check('CaF₂ coefficient: no clash', g['clash'] == 0 and not geometry_bad(g))
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-CaF2-coef.png'))
        pick(page, 'Li2O'); g = page.evaluate(GEO_JS)
        check('Li₂O coefficient: 2[Li]⁺ [O]²⁻', g['coefs'] == ['2'] and g['charges'] == ['+', '2−'], f"{g['coefs']} {g['charges']}")
        setbox(page, '.dc-all', True); g = page.evaluate(GEO_JS)
        check('Li₂O all electrons (coef): Li⁺ 2, O²⁻ 10', count(g, 'Li') == [2] and count(g, 'O') == [10], f"{count(g, 'Li')} {count(g, 'O')}")
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-Li2O-all-coef.png'))
        setbox(page, '.dc-coef', False); g = page.evaluate(GEO_JS)
        check('Li₂O all electrons: Li⁺ 2 ×2, O²⁻ 10', count(g, 'Li') == [2, 2] and count(g, 'O') == [10], f"{count(g, 'Li')} {count(g, 'O')}")
        o = [e for e in g['es'] if e['atoms'] == ['O1']]
        check('Li₂O all electrons: O²⁻ has 2 × (from Li) in the outer shell', sorted(e['mk'] for e in o) == ['cross'] * 2 + ['dot'] * 8)
        check('Li₂O all electrons: inner shell circles drawn', page.locator('.dc-svg .dc-inner').count() == 1)
        check('Li₂O all electrons: geometry ok', not geometry_bad(g), str(geometry_bad(g)[:3]))
        check('Li₂O: mark scheme M1 / M2', 'M1' in page.inner_text('.dc-note') and '9701/22 May/June 2026 Q1(b)' in page.inner_text('.dc-note'))
        check('Li₂O all electrons: card 1s² → 2 (= He), O²⁻ 2,8', '2（= He）' in page.inner_text('.dc-count') and '2,8（= Ne）' in page.inner_text('.dc-count'))
        check('all electrons disables "new outer shell"', page.is_disabled('.dc-new'))
        shot('02-ionic-Li2O-all')
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-Li2O-all.png'))
        bad = []
        for sp in ('NaCl', 'MgO', 'CaF2', 'Na2O', 'MgCl2'):
            pick(page, sp); g = page.evaluate(GEO_JS)
            gb = geometry_bad(g)
            if gb or g['clash']:
                bad.append(f'{sp}: {gb[:2]} clash {g["clash"]}')
        check('all electrons: every ionic species geometry ok', not bad, '; '.join(bad))
        pick(page, 'MgCl2'); g = page.evaluate(GEO_JS)
        check('MgCl₂ all electrons: Mg²⁺ 10, Cl⁻ 18 each', count(g, 'Mg') == [10] and count(g, 'Cl') == [18, 18], f"{count(g, 'Mg')} {count(g, 'Cl')}")
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-MgCl2-all.png'))
        setbox(page, '.dc-all', False)
        pick(page, 'NaCl'); check('coefficient option disabled for NaCl', page.is_disabled('.dc-coef'))
        pick(page, 'H2O'); check('ionic options hidden for covalent', not page.is_visible('.dc-all'))

        print('== coordinate bonds')
        pick(page, 'NH4Cl'); g = page.evaluate(GEO_JS)
        check('NH₄Cl step ①: NH₃ N 8 with 1 lone pair, H⁺ empty', count(g, 'N') == [8] and count(g, 'H') == [2, 2, 2, 0] and
              sum(1 for e in g['es'] if e['kind'] == 'lp') == 2, f"{count(g, 'N')} {count(g, 'H')}")
        check('NH₄Cl step ①: charges + and −', g['charges'] == ['+', '−'], str(g['charges']))
        check('NH₄Cl step ①: arrow labels', set(l['t'] for l in g['labels']) >= {'N 的 lone pair 给 H⁺', 'H⁺ 来自 HCl'}, str([l['t'] for l in g['labels']]))
        check('NH₄Cl step ①: geometry ok, no clash', not geometry_bad(g) and g['clash'] == 0, str(geometry_bad(g)[:3]))
        shot('20-dat-NH4Cl-step1')
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-NH4Cl-step1.png'))
        page.click('.dc-steps button[data-step="2"]'); g = page.evaluate(GEO_JS)
        check('NH₄Cl step ②: N 8, every H 2, Cl⁻ 8', count(g, 'N') == [8] and count(g, 'H') == [2] * 4 and count(g, 'Cl') == [8], f"{count(g, 'N')} {count(g, 'H')} {count(g, 'Cl')}")
        dat = [e for e in g['es'] if e['dative']]
        check('NH₄Cl step ②: one coordinate pair, both electrons N\'s •', len(dat) == 2 and {e['mk'] for e in dat} == {'dot'} and {e['owner'] for e in dat} == {'n'})
        check('NH₄Cl step ②: other N–H pairs are • + ×', all({e['mk'] for e in g['es'] if e['kind'] == 'bond' and e['bond'] == bi} == {'dot', 'cross'} for bi in ('0', '1', '2')))
        check('NH₄Cl step ②: [NH₄]⁺ and [Cl]⁻ brackets', g['charges'] == ['+', '−'])
        check('NH₄Cl step ②: Cl⁻ has 7 ○ + 1 ×', sorted(e['mk'] for e in g['es'] if e['atoms'] == ['cl']) == ['circ'] * 7 + ['cross'])
        check('NH₄Cl step ②: displayed formula arrow N→H', g['arrows'] == ['N→H'], str(g['arrows']))
        check('NH₄Cl step ②: geometry ok, no clash', not geometry_bad(g) and g['clash'] == 0, str(geometry_bad(g)[:3]))
        check('NH₄Cl: mark scheme M1 / M2', 'M1' in page.inner_text('.dc-note') and 'M2' in page.inner_text('.dc-note') and '9701/23 May/June 2024 Q4(a)' in page.inner_text('.dc-note'))
        check('NH₄Cl: card 1 coordinate bond', page.inner_text('.dc-count tr[data-k=dat] .dc-v') == '1')
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-NH4Cl-step2.png'))
        pick(page, 'Al2Cl6'); g = page.evaluate(GEO_JS)
        dat = [e for e in g['es'] if e['dative']]
        check('Al₂Cl₆: two coordinate pairs, both × from Cl', len(dat) == 4 and {e['mk'] for e in dat} == {'cross'})
        check('Al₂Cl₆: displayed formula has two Cl→Al', g['arrows'] == ['Cl→Al', 'Cl→Al'], str(g['arrows']))
        check('Al₂Cl₆: highlight per coordinate pair', page.locator('.dc-svg .dc-dat').count() == 2)
        shot('20-dat-Al2Cl6')
        pick(page, 'BF3NH3'); g = page.evaluate(GEO_JS)
        dat = [e for e in g['es'] if e['dative']]
        check('F₃B←NH₃: coordinate pair from N (○ ○)', len(dat) == 2 and {e['mk'] for e in dat} == {'circ'})
        check('F₃B←NH₃: arrow N→B', g['arrows'] == ['N→B'], str(g['arrows']))
        check('F₃B←NH₃: four marks in the legend', page.locator('.dc-legend [data-mk]').count() == 4)

        print('== exam mode')
        pick(page, 'SO2'); setbox(page, '.dc-exam', True)
        vis = lambda: page.evaluate('''() => [...document.querySelectorAll('.dc-svg g.dc-e')].filter(g => getComputedStyle(g).visibility !== 'hidden').map(g => g.dataset.kind)''')
        check('exam stage 0: no electrons visible', vis() == [], str(vis()))
        check('exam stage 0: card hides numbers', '?' in page.inner_text('.dc-count') and '10' not in page.inner_text('.dc-count'))
        check('exam stage 0: displayed formula hidden', not page.is_visible('.dc-struct'))
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-exam-SO2-stage0.png'))
        page.click('.dc-next'); v = vis()
        check('exam stage 1: only the 8 shared-pair electrons', v == ['bond'] * 8, str(v))
        check('exam stage 1: button now says lone pairs', 'lone pairs' in page.inner_text('.dc-next'))
        page.locator('.dc-fig').screenshot(path=str(OUT / 'z-exam-SO2-stage1.png'))
        page.click('.dc-next'); v = vis()
        check('exam stage 2: all 18 electrons', len(v) == 18 and 'lp' in v)
        check('exam stage 2: card shows 10', page.locator('.dc-count').get_attribute('data-ce') == '10' and '?' not in page.inner_text('.dc-count'))
        pick(page, 'NO'); check('exam: new species starts hidden again', vis() == [])
        check('exam: NO radical label hidden at stage 0', page.evaluate("() => getComputedStyle(document.querySelector('[data-ann]')).visibility") == 'hidden')
        pick(page, 'MgO'); page.click('.dc-next'); v = vis()
        check('exam ionic stage 1: only the 2 transferred electrons', v == ['gain', 'gain'], str(v))
        check('exam ionic: button text', '其余' in page.inner_text('.dc-next'))
        shot('30-exam-MgO-stage1')
        setbox(page, '.dc-exam', False)
        pick(page, 'SO2'); check('exam off: everything visible', len(vis()) == 18)

        print('== fonts / overflow')
        bad = []
        for sp in GROUP:
            pick(page, sp)
            sm = page.evaluate(SMALL_JS)
            if sm: bad.append(f'{sp}: {sm[:3]}')
            if sp == 'NH4Cl':
                page.click('.dc-steps button[data-step="2"]')
                sm = page.evaluate(SMALL_JS)
                if sm: bad.append(f'{sp} step 2: {sm[:3]}')
        check('font ≥ 12px everywhere (1000 px)', not bad, '; '.join(bad[:4]))
        shot('12-cov-SF6-full')
        pick(page, 'SCl2'); shot('10-cov-SCl2')

        print('== narrow (720 px)')
        page.set_viewport_size({'width': 720, 'height': 1100})
        bad = []
        for sp in GROUP:
            pick(page, sp)
            ov = page.evaluate(OVER_JS) + page.evaluate(SMALL_JS)
            if ov: bad.append(f'{sp}: {ov[:3]}')
            if sp == 'NH4Cl':   # step ① is the default; step ② checked too
                page.click('.dc-steps button[data-step="2"]')
                ov = page.evaluate(OVER_JS) + page.evaluate(SMALL_JS)
                if ov: bad.append(f'{sp} step 2: {ov[:3]}')
        pick(page, 'CaF2'); setbox(page, '.dc-all', True)
        ov = page.evaluate(OVER_JS) + page.evaluate(SMALL_JS)
        if ov: bad.append(f'CaF2 all: {ov[:3]}')
        check('narrow: no overflow, font ≥ 12px, every species', not bad, '; '.join(bad[:4]))
        shot('40-narrow-CaF2-all')
        setbox(page, '.dc-all', False)
        pick(page, 'Al2Cl6'); shot('41-narrow-Al2Cl6')
        check('no [data-clash] anywhere', page.locator('[data-clash]').count() == 0)

        # per-species detail shots (light)
        page.set_viewport_size({'width': 1000, 'height': 1100})
        for i, sp in enumerate(GROUP):
            pick(page, sp)
            if sp == 'NH4Cl':
                page.click('.dc-steps button[data-step="2"]')
            shot(f'z{i:02d}-{sp}', '.dc-fig')
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
