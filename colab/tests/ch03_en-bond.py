"""ch03 en-bond cell test: Pauling electronegativity heatmap, ΔEN calculator & ruler, bond electron-pair schematic.

usage: uv run --with playwright python -I colab/tests/ch03_en-bond.py <preview.html> <shots-dir>
(build the preview first: COLAB_TMP=/mnt/ai-shared/che_tmp/ch03 python3 tools/build_colab.py ch03 --cell en-bond)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []

EXPECTED_PT = [
    (1, 1, 'H', '2.1'),
    (2, 1, 'Li', '1.0'), (2, 2, 'Be', '1.5'), (2, 13, 'B', '2.0'), (2, 14, 'C', '2.5'),
    (2, 15, 'N', '3.0'), (2, 16, 'O', '3.5'), (2, 17, 'F', '4.0'),
    (3, 1, 'Na', '0.9'), (3, 2, 'Mg', '1.2'), (3, 13, 'Al', '1.5'), (3, 14, 'Si', '1.8'),
    (3, 15, 'P', '2.1'), (3, 16, 'S', '2.5'), (3, 17, 'Cl', '3.0'),
    (4, 1, 'K', '0.8'), (4, 2, 'Ca', '1.0'), (4, 13, 'Ga', '1.6'), (4, 14, 'Ge', '1.8'),
    (4, 15, 'As', '2.0'), (4, 16, 'Se', '2.4'), (4, 17, 'Br', '2.8'),
    (5, 17, 'I', '2.5'),
]


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


SMALL_JS = """() => {
  const out = [];
  for (const e of document.querySelectorAll('.k *')) {
    if (e.closest('svg')) continue;
    const st = getComputedStyle(e);
    if (st.display === 'none' || st.visibility === 'hidden' || (!e.offsetParent && e.tagName !== 'DIV')) continue;
    if (e.classList.contains('tip') && !e.classList.contains('show')) continue;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own && parseFloat(st.fontSize) < 12 - 1e-3) {
      out.push(e.tagName + '.' + e.className + ':' + parseFloat(st.fontSize) + 'px:' + e.textContent.trim().slice(0, 20));
    }
  }
  for (const svg of document.querySelectorAll('.k svg')) {
    const vb = (svg.getAttribute('viewBox') || '').trim().split(/\\s+/).map(Number);
    const scale = vb[2] ? svg.getBoundingClientRect().width / vb[2] : 1;
    for (const t of svg.querySelectorAll('text')) {
      if (!t.textContent.trim()) continue;
      const px = parseFloat(getComputedStyle(t).fontSize) * scale;
      if (px < 12 - 1e-3) out.push('SVG:' + t.textContent.trim().slice(0, 20) + ':' + px.toFixed(2) + 'px');
    }
  }
  return out;
}"""

SVG_AUDIT_JS = """(sel) => {
  const svg = document.querySelector(sel);
  const ts = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim());
  const boxes = ts.map(t => ({ txt: t.textContent.trim(), r: t.getBoundingClientRect(), b: t.getBBox(),
    ax: +t.getAttribute('data-ax'), ay: +t.getAttribute('data-ay'), clash: t.getAttribute('data-clash') }));
  const overlaps = [];
  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i].r, b = boxes[j].r;
      if (a.width && b.width && a.x < b.x + b.width - 0.5 && b.x < a.x + a.width - 0.5 &&
          a.y < b.y + b.height - 0.5 && b.y < a.y + b.height - 0.5) {
        overlaps.push(boxes[i].txt + ' <-> ' + boxes[j].txt);
      }
    }
  }
  const jumped = [];
  for (const x of boxes) {
    const dx = Math.max(x.b.x - x.ax, 0, x.ax - (x.b.x + x.b.width));
    const dy = Math.max(x.b.y - x.ay, 0, x.ay - (x.b.y + x.b.height));
    const dist = Math.hypot(dx, dy);
    if (dist > 34) jumped.push(x.txt + ':' + dist.toFixed(1));
  }
  const clashes = boxes.filter(x => x.clash).map(x => x.txt + ':' + x.clash);
  return { overlaps, jumped, clashes };
}"""

CONTRAST_JS = """() => {
  function lum(cs) {
    const is01 = cs.startsWith('color(');
    const m = cs.match(/[\\d.]+/g).map(Number).slice(0, 3).map(v => {
      if (!is01) v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2];
  }
  const bad = [], bgs = {};
  for (const c of document.querySelectorAll('.eb-cell')) {
    const bg = getComputedStyle(c).backgroundColor;
    const fg = getComputedStyle(c.querySelector('.eb-sym')).color;
    bgs[c.dataset.el] = bg;
    const l1 = lum(bg), l2 = lum(fg);
    const cr = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    if (cr < 4.5) bad.push(c.dataset.el + ':' + cr.toFixed(2));
  }
  return { bad, distinct: new Set(Object.values(bgs)).size };
}"""


def audit_svgs(page, tag):
    r1 = page.evaluate(SVG_AUDIT_JS, '.eb-ruler')
    r2 = page.evaluate(SVG_AUDIT_JS, '.eb-bond')
    ok = not (r1['overlaps'] or r1['jumped'] or r1['clashes'] or r2['overlaps'] or r2['jumped'] or r2['clashes'])
    check(f'{tag}: SVG 0 clash / 0 overlap / 0 jumped label', ok, f'ruler={r1} bond={r2}')


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1150}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        sfx = '' if scheme == 'light' else '-dark'

        def shot(name, sel='.k'):
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        cr = page.evaluate(CONTRAST_JS)
        check(f'{scheme}: all 23 heatmap cells contrast >= 4.5 & sequential ramp',
              not cr['bad'] and cr['distinct'] >= 12, str(cr))

        if scheme == 'dark':
            shot('01-default-HCl')
            page.hover('.eb-cell[data-el="F"]'); page.wait_for_timeout(120)
            shot('07-zoom-heatmap-tip', '.eb-ptwrap')
            page.click('.eb-pre[data-preset="Al-Cl"]'); page.wait_for_timeout(80)
            shot('03-preset-AlCl')
            page.click('.eb-pre[data-preset="Na-Cl"]'); page.wait_for_timeout(80)
            shot('04-preset-NaCl')
            page.click('.eb-pre[data-preset="Mg-O"]'); page.wait_for_timeout(80)
            shot('10-zoom-bond-MgO', '.eb-bcard')
            page.set_viewport_size({'width': 720, 'height': 1150}); page.wait_for_timeout(150)
            page.click('.eb-pre[data-preset="H-Cl"]'); page.wait_for_timeout(80)
            shot('06-narrow-720')
            audit_svgs(page, 'dark 720px H-Cl')
            ctx.close(); continue

        print('== Pauling heatmap table & trends')
        cells = page.evaluate("""() => [...document.querySelectorAll('.eb-cell')].map(c => [
          +c.dataset.per, +c.dataset.grp, c.dataset.el, c.dataset.en,
          c.querySelector('.eb-sym').textContent.trim(), c.querySelector('.eb-val').textContent.trim()
        ])""")
        got_tuples = [(r[0], r[1], r[2], r[3]) for r in cells]
        check('exact 23 elements in Pauling table (no Group 18)', got_tuples == EXPECTED_PT, str(got_tuples))
        check('every cell displays symbol + EN value matching dataset',
              all(r[2] == r[4] and r[3] == r[5] for r in cells), str(cells[:5]))
        grps = page.evaluate("[...document.querySelectorAll('.eb-gh')].map(e => +e.textContent.trim())")
        check('Group columns 1, 2, 13, 14, 15, 16, 17 (no 18)', grps == [1, 2, 13, 14, 15, 16, 17], str(grps))
        pt_txt = page.inner_text('.eb-ptwrap')
        check('trend arrows across period & down group',
              'across a period: electronegativity increases' in pt_txt and 'down a' in pt_txt and 'decreases' in pt_txt, pt_txt)
        check('F marked most electronegative',
              'most electronegative' in pt_txt and page.get_attribute('.eb-cell[data-el="F"]', 'data-most') == 'most electronegative')

        # Tooltip check on hover
        for sym in ('F', 'H', 'Na', 'Cl', 'Ga', 'I'):
            page.hover(f'.eb-cell[data-el="{sym}"]'); page.wait_for_timeout(80)
            tip = page.inner_text('.tip')
            ok_tip = sym in tip and 'nuclear charge' in tip and 'atomic radius' in tip and 'shielding' in tip
            if not ok_tip:
                check(f'tooltip {sym} has nuclear charge / atomic radius / shielding', False, tip)
                break
        else:
            check('hover tooltips explain EN via nuclear charge / atomic radius / shielding', True)
        page.hover('.eb-cell[data-el="F"]'); page.wait_for_timeout(100)
        shot('07-zoom-heatmap-tip', '.eb-ptwrap')
        page.mouse.move(5, 5); page.wait_for_timeout(60)

        print('== default H–Cl state')
        check('default preset H–Cl active', 'on' in page.get_attribute('.eb-pre[data-preset="H-Cl"]', 'class'))
        check('default equation ΔEN = 3.0 − 2.1 = 0.9', page.inner_text('.eb-eq') == 'ΔEN = 3.0 − 2.1 = 0.9', page.inner_text('.eb-eq'))
        check('H selected as A, Cl selected as B with distinct border colors',
              page.evaluate("""() => {
                const h = document.querySelector('.eb-cell[data-el="H"]'), cl = document.querySelector('.eb-cell[data-el="Cl"]');
                return h.classList.contains('sel-a') && cl.classList.contains('sel-b') &&
                       getComputedStyle(h).borderColor !== getComputedStyle(cl).borderColor;
              }"""))
        hcl_geo = page.evaluate("""() => {
          const s = document.querySelector('.eb-bond');
          const xl = +s.getAttribute('data-xl'), xr = +s.getAttribute('data-xr'), xp = +s.getAttribute('data-xpair');
          const dneg = s.querySelector('text.eb-dneg'), dpos = s.querySelector('text.eb-dpos');
          return { xl, xr, xp, mid: (xl + xr) / 2, negAtom: dneg && dneg.getAttribute('data-atom'),
                   posAtom: dpos && dpos.getAttribute('data-atom'), negTxt: dneg && dneg.textContent, posTxt: dpos && dpos.textContent };
        }""")
        check('H–Cl electron pair noticeably shifted toward Cl',
              hcl_geo['xp'] > hcl_geo['mid'] + 25 and hcl_geo['xp'] < hcl_geo['xr'], str(hcl_geo))
        check('H–Cl marks Cl δ− and H δ+',
              hcl_geo['negAtom'] == 'Cl' and hcl_geo['negTxt'] == 'δ−' and hcl_geo['posAtom'] == 'H' and hcl_geo['posTxt'] == 'δ+',
              str(hcl_geo))
        audit_svgs(page, 'default H-Cl')
        shot('01-default-HCl')
        shot('09-zoom-bond-HCl', '.eb-bcard')

        print('== all 6 presets')
        PRESET_CASES = [
            ('Cl-Cl', 'ΔEN = 3.0 − 3.0 = 0',   'nonpolar',     'non-polar covalent'),
            ('C-H',   'ΔEN = 2.5 − 2.1 = 0.4', 'polar',        'covalent'),
            ('H-Cl',  'ΔEN = 3.0 − 2.1 = 0.9', 'polar',        'covalent'),
            ('Al-Cl', 'ΔEN = 3.0 − 1.5 = 1.5', 'intermediate', 'intermediate — 不考'),
            ('Na-Cl', 'ΔEN = 3.0 − 0.9 = 2.1', 'ionic',        'ionic'),
            ('Mg-O',  'ΔEN = 3.5 − 1.2 = 2.3', 'ionic',        'ionic'),
        ]
        for key, want_eq, want_z, want_word in PRESET_CASES:
            page.click(f'.eb-pre[data-preset="{key}"]'); page.wait_for_timeout(80)
            eq = page.inner_text('.eb-eq')
            verd = page.inner_text('.eb-verdict')
            z = page.get_attribute('.eb-calc', 'data-zone')
            check(f'preset {key}: {want_eq} → {want_word}', eq == want_eq and z == want_z and want_word in verd, f'{eq} | {z} | {verd}')
            audit_svgs(page, f'preset {key}')

        # Specific visual/structural checks per preset
        page.click('.eb-pre[data-preset="Cl-Cl"]'); page.wait_for_timeout(80)
        cl_geo = page.evaluate("""() => {
          const s = document.querySelector('.eb-bond');
          return { mid: (+s.getAttribute('data-xl') + +s.getAttribute('data-xr')) / 2, xp: +s.getAttribute('data-xpair'),
                   deltas: s.querySelectorAll('text.eb-dneg,text.eb-dpos').length,
                   bothSel: document.querySelector('.eb-cell[data-el="Cl"]').classList.contains('sel-a') &&
                            document.querySelector('.eb-cell[data-el="Cl"]').classList.contains('sel-b') };
        }""")
        check('Cl–Cl: electron pair centered & no δ+/δ− & Cl has dual A·B badge',
              cl_geo['xp'] == cl_geo['mid'] and cl_geo['deltas'] == 0 and cl_geo['bothSel'], str(cl_geo))
        shot('02-preset-ClCl')

        page.click('.eb-pre[data-preset="C-H"]'); page.wait_for_timeout(80)
        ch_geo = page.evaluate("""() => {
          const s = document.querySelector('.eb-bond');
          return { mid: (+s.getAttribute('data-xl') + +s.getAttribute('data-xr')) / 2, xp: +s.getAttribute('data-xpair'),
                   negAtom: s.querySelector('text.eb-dneg').getAttribute('data-atom') };
        }""")
        check('C–H: electron pair shifted left toward C (δ−)', ch_geo['xp'] < ch_geo['mid'] - 15 and ch_geo['negAtom'] == 'C', str(ch_geo))
        # B review: the ruler pointer must not run under the opaque zone label
        for key in ('C-H', 'Al-Cl', 'H-Cl', 'Na-Cl'):
            page.click(f'.eb-pre[data-preset="{key}"]'); page.wait_for_timeout(60)
            hit = page.evaluate("""() => {
              const s = document.querySelector('.eb-ruler');
              const ls = [...s.querySelectorAll('line.eb-stub')].map(l => l.getBoundingClientRect());
              const ts = [...s.querySelectorAll('text')].map(t => [t.textContent, t.getBoundingClientRect()]);
              const out = [];
              for (const l of ls) for (const [txt, r] of ts)
                if (l.right >= r.left && l.left <= r.right && l.bottom >= r.top && l.top <= r.bottom) out.push(txt);
              return { n: ls.length, out };
            }""")
            check(f'{key}: ruler pointer stubs (2) do not touch any ruler text', hit['n'] == 2 and not hit['out'], str(hit))
        page.click('.eb-pre[data-preset="C-H"]'); page.wait_for_timeout(60)
        page.set_viewport_size({'width': 1000, 'height': 1150})
        page.locator('.eb-ruler').first.screenshot(path=str(OUT / f'11-zoom-ruler-CH{sfx}.png'))

        page.click('.eb-pre[data-preset="Al-Cl"]'); page.wait_for_timeout(80)
        al_note = page.inner_text('.eb-alnote')
        verd_al = page.inner_text('.eb-verdict')
        check('Al–Cl side note verbatim & highlighted',
              'metal + non-metal 但不是 ionic → AlCl₃ covalent' in al_note and
              'on' in page.get_attribute('.eb-alnote', 'class'), al_note)
        check('Al–Cl verdict mentions not entirely covalent & out of syllabus',
              'not entirely covalent' in verd_al and 'out of syllabus' in verd_al, verd_al)
        check('Al–Cl draws covalent pair (no ionic brackets)', page.locator('.eb-bond .eb-brk').count() == 0)
        shot('03-preset-AlCl')
        shot('08-zoom-ruler-AlCl', '.eb-rcard')

        page.click('.eb-pre[data-preset="Na-Cl"]'); page.wait_for_timeout(80)
        btxt_na = page.text_content('.eb-bond')
        check('Na–Cl draws 2 bracketed ions [Na]⁺ and [Cl]⁻',
              page.locator('.eb-bond .eb-brk').count() == 4 and '[Na]⁺' in btxt_na and '[Cl]⁻' in btxt_na, btxt_na)
        shot('04-preset-NaCl')

        page.click('.eb-pre[data-preset="Mg-O"]'); page.wait_for_timeout(80)
        btxt_mg = page.text_content('.eb-bond')
        check('Mg–O draws [Mg]²⁺ and [O]²⁻ with Unicode charges',
              page.locator('.eb-bond .eb-brk').count() == 4 and '[Mg]²⁺' in btxt_mg and '[O]²⁻' in btxt_mg, btxt_mg)
        shot('05-preset-MgO')
        shot('10-zoom-bond-MgO', '.eb-bcard')

        print('== interactive table clicking (1st=A, 2nd=B, 3rd=restart, same cell twice → ΔEN 0)')
        page.click('.eb-cell[data-el="K"]'); page.wait_for_timeout(60)
        check('1st click K → phase 1, only K selected as A',
              page.get_attribute('.eb-calc', 'data-phase') == '1' and
              page.locator('.eb-cell.sel-a').count() == 1 and page.locator('.eb-cell.sel-b').count() == 0)
        page.click('.eb-cell[data-el="F"]'); page.wait_for_timeout(80)
        check('2nd click F → ΔEN = 4.0 − 0.8 = 3.2 (ionic [K]⁺ [F]⁻)',
              page.get_attribute('.eb-calc', 'data-phase') == '2' and
              page.inner_text('.eb-eq') == 'ΔEN = 4.0 − 0.8 = 3.2' and
              '[K]⁺' in page.text_content('.eb-bond') and '[F]⁻' in page.text_content('.eb-bond'))
        audit_svgs(page, 'custom K-F (3.2)')

        # 3rd click restarts; clicking same cell twice gives ΔEN = 0
        page.click('.eb-cell[data-el="Br"]'); page.wait_for_timeout(60)
        check('3rd click Br → restarts as A (phase 1)',
              page.get_attribute('.eb-calc', 'data-phase') == '1' and
              'sel-a' in page.get_attribute('.eb-cell[data-el="Br"]', 'class') and
              page.locator('.eb-cell.sel-b').count() == 0)
        page.click('.eb-cell[data-el="Br"]'); page.wait_for_timeout(80)
        check('clicking Br twice → ΔEN = 2.8 − 2.8 = 0 (non-polar covalent)',
              page.inner_text('.eb-eq') == 'ΔEN = 2.8 − 2.8 = 0' and
              page.get_attribute('.eb-calc', 'data-zone') == 'nonpolar')
        audit_svgs(page, 'custom Br-Br (0)')

        # Reverse order ionic click: Cl first (A), Na second (B) → still big minus small, Cl is anion [Cl]⁻, Na is cation [Na]⁺
        page.click('.eb-cell[data-el="Cl"]'); page.click('.eb-cell[data-el="Na"]'); page.wait_for_timeout(80)
        btxt_rev = page.text_content('.eb-bond')
        check('reverse click Cl then Na → ΔEN = 3.0 − 0.9 = 2.1, [Cl]⁻ and [Na]⁺',
              page.inner_text('.eb-eq') == 'ΔEN = 3.0 − 0.9 = 2.1' and '[Cl]⁻' in btxt_rev and '[Na]⁺' in btxt_rev, btxt_rev)
        audit_svgs(page, 'reverse Cl-Na (2.1)')

        # Boundary values 1.0 (O–C) and 2.0 (Ca–Cl) and 1.9 (H–F)
        for e1, e2, z_exp in [('O', 'C', 'intermediate'), ('Ca', 'Cl', 'ionic'), ('H', 'F', 'intermediate')]:
            page.click(f'.eb-cell[data-el="{e1}"]'); page.click(f'.eb-cell[data-el="{e2}"]'); page.wait_for_timeout(60)
            check(f'boundary {e1}–{e2} → {z_exp}', page.get_attribute('.eb-calc', 'data-zone') == z_exp)
            audit_svgs(page, f'boundary {e1}-{e2}')

        check('desktop 1000px: all fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
        check('no [data-clash]', page.locator('[data-clash]').count() == 0)

        print('== narrow viewport (720px)')
        page.set_viewport_size({'width': 720, 'height': 1150}); page.wait_for_timeout(150)
        page.click('.eb-pre[data-preset="H-Cl"]'); page.wait_for_timeout(80)
        ov = page.evaluate("() => { const k = document.querySelector('.k'); return k.scrollWidth - k.clientWidth; }")
        check('narrow 720px: no horizontal overflow', ov <= 1, str(ov))
        sc = page.evaluate("""() => Math.min(...[...document.querySelectorAll('.eb-ruler,.eb-bond')].map(
          s => s.getBoundingClientRect().width / +s.getAttribute('viewBox').split(' ')[2]))""")
        check('narrow 720px: SVGs redrawn 1:1 (scale >= 0.99)', sc >= 0.99, str(sc))
        check('narrow 720px: all HTML & SVG fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
        for key in ('Cl-Cl', 'H-Cl', 'Al-Cl', 'Na-Cl', 'Mg-O'):
            page.click(f'.eb-pre[data-preset="{key}"]'); page.wait_for_timeout(60)
            audit_svgs(page, f'narrow 720px {key}')
        page.click('.eb-pre[data-preset="H-Cl"]'); page.wait_for_timeout(80)
        shot('06-narrow-720')
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for r in results if r[1])
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
