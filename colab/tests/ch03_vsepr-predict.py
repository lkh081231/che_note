"""ch03 vsepr-predict cell test: step-by-step VSEPR derivation (3.5 B table), 2D electron-pair schematic,
answer mode with tolerance, mark-scheme sentence card.

usage: uv run --with playwright python -I colab/tests/ch03_vsepr-predict.py <preview.html> <shots-dir>
(build the preview first: COLAB_TMP=/mnt/ai-shared/che_tmp/ch03 python3 tools/build_colab.py ch03 --cell vsepr-predict)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []

# chapter 3.5 B table (verbatim) + 3.5 A table: id, formula, bp, lp, shape shown, angle shown, bond order
B_TABLE = [
    ('NH4', 'NH₄⁺', 4, 0, 'tetrahedral', '109.5°', 1),
    ('H3O', 'H₃O⁺', 3, 1, 'pyramidal', '107°', 1),
    ('NH2', 'NH₂⁻', 2, 2, 'non-linear', '104.5°', 1),
    ('SCl2', 'SCl₂', 2, 2, 'non-linear', '104.5°（MS 接受 103–105°）', 1),
    ('PCl3', 'PCl₃', 3, 1, 'pyramidal', '107°', 1),
    ('SiH4', 'SiH₄', 4, 0, 'tetrahedral', '109.5°', 1),
    ('CCl4', 'CCl₄', 4, 0, 'tetrahedral', '109.5°', 1),
    ('BeCl2', 'BeCl₂', 2, 0, 'linear', '180°', 1),
    ('CS2', 'CS₂', 2, 0, 'linear', '180°', 2),
    ('SO2', 'SO₂', 2, 1, 'non-linear（bent）', '约 118°（略小于 120°）', 2),
    ('PCl4', 'PCl₄⁺', 4, 0, 'tetrahedral', '109.5°', 1),
    ('PCl6', 'PCl₆⁻', 6, 0, 'octahedral', '90°', 1),
    ('XeF4', 'XeF₄', 4, 2, 'square planar', '90°', 1),
]
A_TABLE = [
    ('CO2', 'CO₂', 2, 0, 'linear', '180°', 2),
    ('BF3', 'BF₃', 3, 0, 'trigonal planar', '120°', 1),
    ('CH4', 'CH₄', 4, 0, 'tetrahedral', '109.5°', 1),
    ('NH3', 'NH₃', 3, 1, 'pyramidal', '107°', 1),
    ('H2O', 'H₂O', 2, 2, 'non-linear', '104.5°', 1),
    ('PF5', 'PF₅', 5, 0, 'trigonal bipyramidal', '120° and 90°', 1),
    ('SF6', 'SF₆', 6, 0, 'octahedral', '90°', 1),
]
ANALOG = {'NH4': 'CH₄', 'H3O': 'NH₃', 'NH2': 'H₂O', 'SCl2': 'H₂O', 'PCl3': 'NH₃', 'SiH4': 'CH₄', 'CCl4': 'CH₄',
          'BeCl2': 'CO₂', 'CS2': 'CO₂', 'PCl4': 'CH₄', 'PCl6': 'SF₆'}
# arithmetic that must appear in the steps (step number, substring)
STEP_TXT = {
    'NH4': [(2, '5 − 1 = 4'), (4, 'N：5 − 1 = 4；4 个 N–H 用掉 4 → 剩 0 → 0 lone pairs')],
    'H3O': [(2, '6 − 1 = 5'), (4, '5 − 3 = 2'), (4, '1 lone pair')],
    'NH2': [(2, '5 + 1 = 6'), (4, '6 − 2 = 4'), (4, '2 lone pairs')],
    'SCl2': [(1, 'outer electrons = 6'), (2, 'neutral'), (4, '6 − 2 = 4'), (4, '4 ÷ 2 = 2')],
    'PCl3': [(4, '5 − 3 = 2')],
    'BeCl2': [(1, 'Group 2'), (4, '2 − 2 = 0')],
    'CS2': [(3, 'C=S double bond'), (3, '2 × 2 = 4'), (4, '4 − 4 = 0')],
    'SO2': [(3, 'S=O double bond'), (3, '2 × 2 = 4'), (4, '6 − 4 = 2'), (4, '2 ÷ 2 = 1'), (4, '1 lone pair'),
            (5, '3 个区域'), (5, 'trigonal planar 排布')],
    'PCl4': [(2, '5 − 1 = 4'), (4, '4 − 4 = 0')],
    'PCl6': [(2, '5 + 1 = 6'), (4, '6 − 6 = 0'), (5, '6 个区域'), (5, 'octahedral 排布')],
    'XeF4': [(1, 'Group 18'), (1, 'outer electrons = 8'), (4, '8 − 4 = 4'), (4, '2 lone pairs'), (5, '6 个区域'), (5, 'octahedral 排布')],
    'PF5': [(5, '5 个区域')],
}


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
    if (!svg.getBoundingClientRect().width) continue;
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
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const a = boxes[i].r, b = boxes[j].r;
    if (a.x < b.x + b.width - 0.5 && b.x < a.x + a.width - 0.5 && a.y < b.y + b.height - 0.5 && b.y < a.y + a.height - 0.5)
      overlaps.push(boxes[i].txt + ' <-> ' + boxes[j].txt);
  }
  const jumped = [];
  for (const x of boxes) {
    const dx = Math.max(x.b.x - x.ax, 0, x.ax - (x.b.x + x.b.width));
    const dy = Math.max(x.b.y - x.ay, 0, x.ay - (x.b.y + x.b.height));
    if (Math.hypot(dx, dy) > 30) jumped.push(x.txt + ':' + Math.hypot(dx, dy).toFixed(1));
  }
  // text must stay inside the viewBox
  const vb = svg.getAttribute('viewBox').split(' ').map(Number);
  const outside = boxes.filter(x => x.b.x < vb[0] || x.b.y < vb[1] || x.b.x + x.b.width > vb[0] + vb[2] || x.b.y + x.b.height > vb[1] + vb[3]).map(x => x.txt);
  // labels (not the atom symbols) must not touch any bond line / lobe / arc drawn
  const shapes = [...svg.querySelectorAll('.vp-bond, polyline.vp-arc, g.vp-lp, circle.vp-at')].map(e => e.getBoundingClientRect());
  const cover = [];
  for (const t of ts) {
    const role = t.getAttribute('data-role');
    if (role === 'center' || role === 'outer') continue;
    const r = t.getBoundingClientRect();
    // bbox test is coarse for slanted lines, so only flag when the text box sits on a line's own box AND that box is thin
    for (const s of shapes) {
      const thin = s.width < 4 || s.height < 4;
      if (thin && r.left < s.right && s.left < r.right && r.top < s.bottom && s.top < r.bottom) cover.push(t.textContent);
    }
  }
  const clashes = boxes.filter(x => x.clash).map(x => x.txt + ':' + x.clash);
  return { overlaps, jumped, clashes, outside, cover, n: boxes.length };
}"""

FIG_JS = """(sel) => {
  const s = document.querySelector(sel);
  const role = r => [...s.querySelectorAll('text[data-role="' + r + '"]')].map(t => t.textContent);
  return { outer: s.querySelectorAll('circle.vp-at:not(.vp-ctr)').length, bonds: s.querySelectorAll('.vp-bond').length, wedge: s.querySelectorAll('[data-bond=wedge]').length, hash: s.querySelectorAll('[data-bond=hash]').length, lback: s.querySelectorAll('g.vp-lp-back').length,
           lobes: s.querySelectorAll('g.vp-lp').length, arcs: s.querySelectorAll('polyline.vp-arc').length,
           brk: s.querySelectorAll('polyline.vp-brk').length, center: role('center'), outerSym: role('outer'),
           angle: role('angle'), charge: role('charge'), electrons: role('electrons') };
}"""


def audit(page, sel, tag):
    r = page.evaluate(SVG_AUDIT_JS, sel)
    ok = not (r['overlaps'] or r['jumped'] or r['clashes'] or r['outside'] or r['cover'])
    check(f'{tag}: SVG labels 0 clash / overlap / jumped / outside / on-line', ok, str(r))


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        sfx = '' if scheme == 'light' else '-dark'

        def shot(name, sel='.k'):
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        def sp(i):
            page.click(f'.vp-sp[data-sp="{i}"]'); page.wait_for_timeout(40)

        def expand(i):
            sp(i); page.click('.vp-all'); page.wait_for_timeout(60)

        if scheme == 'dark':
            shot('01-default-NH4-step1')
            expand('SO2'); shot('03-SO2-expanded'); shot('10-zoom-fig-SO2', '.vp-dwork .vp-fig'); shot('12-zoom-ms-SO2', '.vp-dwork .vp-ms')
            expand('XeF4'); shot('05-XeF4-expanded'); shot('10-zoom-fig-XeF4', '.vp-dwork .vp-fig')
            expand('PCl6'); shot('10-zoom-fig-PCl6', '.vp-dwork .vp-fig'); shot('11-zoom-steps-PCl6', '.vp-dwork .vp-steps')
            page.click('button[data-tab="quiz"]'); page.wait_for_timeout(60)
            page.evaluate("document.querySelector('.k').__vpAsk('SCl2')")
            page.click('.vp-qbp button[data-v="2"]'); page.click('.vp-qlp button[data-v="2"]')
            page.select_option('.vp-qshape', 'non-linear'); page.fill('.vp-qang', '104'); page.click('.vp-check'); page.wait_for_timeout(80)
            check('dark: quiz SCl₂ right', page.get_attribute('.vp-fb', 'data-result') == 'right')
            shot('20-quiz-right-SCl2'); shot('22-zoom-quiz-fb-right', '.vp-q')
            page.evaluate("document.querySelector('.k').__vpAsk('NH3')")
            page.click('.vp-qbp button[data-v="3"]'); page.click('.vp-qlp button[data-v="0"]')
            page.select_option('.vp-qshape', 'tetrahedral'); page.fill('.vp-qang', '109.5'); page.click('.vp-check'); page.wait_for_timeout(80)
            shot('21-quiz-wrong-NH3'); shot('23-zoom-quiz-fb-wrong', '.vp-q')
            check('dark: [data-clash] = 0', page.locator('[data-clash]').count() == 0)
            check('dark: all fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
            page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(150)
            page.click('button[data-tab="derive"]'); expand('NH4')
            shot('30-narrow-720-NH4')
            ctx.close(); continue

        print('== species buttons')
        rowB = page.evaluate("[...document.querySelectorAll('.vp-rowB .vp-sp')].map(b => b.textContent)")
        rowA = page.evaluate("[...document.querySelectorAll('.vp-rowA .vp-sp')].map(b => b.textContent)")
        check('3.5 B row: 13 species in table order', rowB == [r[1] for r in B_TABLE], str(rowB))
        check('3.5 A row: 7 syllabus species', rowA == [r[1] for r in A_TABLE], str(rowA))

        print('== default NH₄⁺ step 1')
        check('default NH₄⁺, step 1 / 6', page.get_attribute('.vp-dwork', 'data-sp') == 'NH4' and
              page.inner_text('.vp-count') == '步骤 1 / 6' and 'on' in page.get_attribute('.vp-sp[data-sp="NH4"]', 'class'))
        f = page.evaluate(FIG_JS, '.vp-dwork .vp-svg')
        check('step 1: only the central atom N + "5 outer electrons", no bonds / lobes / brackets',
              f['center'] == ['N'] and f['outer'] == 0 and f['bonds'] == 0 and f['lobes'] == 0 and f['brk'] == 0 and
              f['electrons'] == ['5 outer electrons'], str(f))
        check('step 1: 1 step written, 5 still to do',
              page.locator('.vp-dwork .vp-eq').count() == 1 and page.locator('.vp-dwork li.vp-todo').count() == 5)
        shot('01-default-NH4-step1')

        print('== stepping NH₄⁺')
        page.click('.vp-next'); page.wait_for_timeout(40)
        f = page.evaluate(FIG_JS, '.vp-dwork .vp-svg')
        check('step 2: brackets + "+" charge, "ion：4 electrons"',
              f['brk'] == 2 and f['charge'] == ['+'] and f['electrons'] == ['ion：4 electrons'] and f['bonds'] == 0, str(f))
        page.click('.vp-next'); page.wait_for_timeout(40)
        f = page.evaluate(FIG_JS, '.vp-dwork .vp-svg')
        check('step 3: 4 N–H bonds to 4 H, no lobes / arc yet',
              f['outer'] == 4 and f['bonds'] == 4 and f['outerSym'] == ['H'] * 4 and f['lobes'] == 0 and f['arcs'] == 0, str(f))
        shot('02-NH4-step3')
        page.click('.vp-next'); page.click('.vp-next'); page.wait_for_timeout(40)
        f = page.evaluate(FIG_JS, '.vp-dwork .vp-svg')
        check('step 5: arc "109.5°" appears, no MS card yet', f['arcs'] == 1 and f['angle'] == ['109.5°'] and
              page.locator('.vp-dwork .vp-ms').count() == 0, str(f))
        page.click('.vp-next'); page.wait_for_timeout(40)
        check('step 6: next disabled, MS card shown', page.is_disabled('.vp-next') and page.locator('.vp-dwork .vp-ms').count() == 1)
        page.click('.vp-reset'); page.wait_for_timeout(40)
        check('从头再来 → step 1', page.get_attribute('.vp-dwork', 'data-step') == '1' and not page.is_disabled('.vp-next'))
        page.click('.vp-all'); page.wait_for_timeout(40)
        sp('SCl2')
        check('switching species resets to step 1', page.get_attribute('.vp-dwork', 'data-step') == '1')

        print('== all 20 species fully expanded')
        for (i, form, bp, lp, shape, ang, order) in B_TABLE + A_TABLE:
            expand(i)
            res = page.evaluate("""() => { const t = document.querySelector('.vp-dwork .vp-res');
              return t && { bp: t.dataset.bp, lp: t.dataset.lp, cells: [...t.querySelectorAll('td')].map(td => td.textContent) }; }""")
            want = [str(bp), str(lp), shape, ang]
            check(f'{form}: bp {bp} · lp {lp} · {shape} · {ang}',
                  res and res['bp'] == str(bp) and res['lp'] == str(lp) and res['cells'] == want, str(res))
            f = page.evaluate(FIG_JS, '.vp-dwork .vp-svg')
            charged = form[-1] in '⁺⁻'
            check(f'{form}: schematic {bp} atoms, {bp * order} bond lines, {lp} lone-pair lobes, brackets={charged}',
                  f['outer'] == bp and f['bonds'] == bp * order and f['lobes'] == lp and (f['brk'] == 2) == charged and
                  f['arcs'] >= 1 and f['angle'], str(f))
            steps = page.evaluate("[...document.querySelectorAll('.vp-dwork .vp-steps li')].map(l => l.innerText)")
            okst = len(steps) == 6 and all(page.locator('.vp-dwork li.vp-todo').count() == 0 for _ in [0])
            for n, sub in STEP_TXT.get(i, []):
                if sub not in steps[n - 1]:
                    okst = False; print('     missing in step', n, repr(sub), '|', steps[n - 1])
            if i in ANALOG:
                okst = okst and ('类比 ' + ANALOG[i]) in steps[5]
            elif i in ('SO2', 'XeF4'):
                okst = okst and 'syllabus 没有点名' in steps[5]
            else:
                okst = okst and 'syllabus 点名的 7 个之一' in steps[5]
            check(f'{form}: 6 steps, arithmetic + analogue correct', okst, ' || '.join(steps))
            ms = page.inner_text('.vp-dwork .vp-ms')
            m2 = f"{bp} bonding pair{'s' if bp != 1 else ''} and {lp} lone pair{'s' if lp != 1 else ''} (of electrons)"
            m3 = 'lone pairs repel more than bonding pairs' if lp else 'bonding pairs repel equally'
            bname = form[0:2 if form[1].islower() else 1]
            check(f'{form}: MS card M1/M2/M3 + "bonds" warning', ang in ms and m2 in ms and m3 in ms and
                  ' bonds」代替 bonding pairs → 不给 M2' in ms and (('lone pairs repel more' in ms) == bool(lp)), ms)
            audit(page, '.vp-dwork .vp-svg', form)
        expand('SCl2')
        ms = page.inner_text('.vp-dwork .vp-ms')
        check('SCl₂ MS card: 104.5° (103–105°), 「2 S–Cl bonds」 warning, 107–109° 最多 1 分',
              '104.5°（MS 接受 103–105°）' in ms and '「2 S–Cl bonds」' in ms and '最多 1 分' in ms, ms)
        expand('PF5')
        f = page.evaluate(FIG_JS, '.vp-dwork .vp-svg')
        check('PF₅ schematic labels both 120° and 90°', sorted(f['angle']) == ['120°', '90°'], str(f))

        for i in ('NH4', 'H3O', 'SCl2', 'SO2', 'PCl6', 'XeF4', 'PF5', 'CS2', 'BeCl2'):
            expand(i)
            shot(f'03-{i}-expanded' if i == 'SO2' else f'04-{i}-expanded')
        for i in ('NH4', 'H3O', 'NH2', 'SO2', 'XeF4', 'PCl6', 'PF5', 'CS2', 'BF3'):
            expand(i); shot(f'10-zoom-fig-{i}', '.vp-dwork .vp-fig')
        expand('PCl6'); shot('11-zoom-steps-PCl6', '.vp-dwork .vp-steps')
        expand('SO2'); shot('11-zoom-steps-SO2', '.vp-dwork .vp-steps'); shot('12-zoom-ms-SO2', '.vp-dwork .vp-ms')
        expand('SCl2'); shot('12-zoom-ms-SCl2', '.vp-dwork .vp-ms')
        expand('CH4'); shot('12-zoom-ms-CH4', '.vp-dwork .vp-ms')

        check('desktop 1000px: all fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))

        print('== answer mode')
        page.click('button[data-tab="quiz"]'); page.wait_for_timeout(60)
        q0 = page.get_attribute('.vp-q', 'data-sp')
        check('quiz starts with a random species from the 20', q0 in [r[0] for r in B_TABLE + A_TABLE], str(q0))
        seen = set()
        for _ in range(25):
            prev = page.get_attribute('.vp-q', 'data-sp')
            page.click('.vp-new')
            now = page.get_attribute('.vp-q', 'data-sp')
            seen.add(now)
            if now == prev:
                check('换一题 never repeats the same species', False, now); break
        check('换一题 draws several different species', len(seen) >= 8, str(seen))

        def answer(i, bp, lp, shape, ang):
            page.evaluate(f"document.querySelector('.k').__vpAsk('{i}')")
            if bp is not None: page.click(f'.vp-qbp button[data-v="{bp}"]')
            if lp is not None: page.click(f'.vp-qlp button[data-v="{lp}"]')
            if shape: page.select_option('.vp-qshape', shape)
            page.fill('.vp-qang', ang)
            page.click('.vp-check'); page.wait_for_timeout(60)
            return page.get_attribute('.vp-fb', 'data-result')

        r = answer('SCl2', 2, 2, 'non-linear', '104')
        fb = page.inner_text('.vp-fb')
        check('SCl₂ 2 / 2 / non-linear / 104 → 全对 4 / 4', r == 'right' and '全对 4 / 4' in fb, fb)
        check('right answer: derivation + MS card shown below', page.get_attribute('.vp-qwork', 'data-step') == '6' and
              page.locator('.vp-qwork .vp-ms').count() == 1 and page.locator('.vp-qwork .vp-steps li').count() == 6)
        audit(page, '.vp-qwork .vp-svg', 'quiz SCl₂')
        shot('20-quiz-right-SCl2'); shot('22-zoom-quiz-fb-right', '.vp-q')
        check('score 1 / 1', page.inner_text('.vp-score') == '本轮 1 / 1 题全对', page.inner_text('.vp-score'))

        r = answer('NH3', 3, 0, 'tetrahedral', '109.5')
        fb = page.inner_text('.vp-fb')
        parts = page.evaluate("[...document.querySelectorAll('.vp-fb li')].map(l => [l.dataset.part, l.dataset.ok])")
        check('NH₃ 3 / 0 / tetrahedral / 109.5 → wrong, only bonding pairs right',
              r == 'wrong' and page.get_attribute('.vp-fb', 'data-nok') == '1' and
              parts == [['bonding pairs', '1'], ['lone pairs', '0'], ['shape', '0'], ['bond angle', '0']], str(parts))
        check('wrong answer shows the right values', '正确是 1' in fb and '正确是 pyramidal' in fb and '正确是 107°' in fb, fb)
        check('score 1 / 2', page.inner_text('.vp-score') == '本轮 1 / 2 题全对', page.inner_text('.vp-score'))
        shot('21-quiz-wrong-NH3'); shot('23-zoom-quiz-fb-wrong', '.vp-q')
        page.click('.vp-check'); page.wait_for_timeout(40)
        check('judging the same question twice does not count twice', page.inner_text('.vp-score') == '本轮 1 / 2 题全对')

        print('== angle tolerance')
        TOL = [('H2O', 2, 2, 'non-linear', '103', 'right'), ('H2O', 2, 2, 'non-linear', '105°', 'right'),
               ('H2O', 2, 2, 'non-linear', '102.5', 'wrong'), ('NH2', 2, 2, 'non-linear', '105.5', 'wrong'),
               ('NH3', 3, 1, 'pyramidal', '106', 'right'), ('PCl3', 3, 1, 'pyramidal', '108', 'right'),
               ('H3O', 3, 1, 'pyramidal', '108.5', 'wrong'), ('CH4', 4, 0, 'tetrahedral', '109.5', 'right'),
               ('CH4', 4, 0, 'tetrahedral', '109', 'right'), ('CH4', 4, 0, 'tetrahedral', '108', 'wrong'), ('SO2', 2, 1, 'non-linear', '117', 'right'), ('SO2', 2, 1, 'non-linear', '116', 'wrong'), ('PF5', 5, 0, 'trigonal bipyramidal', '120 and 90', 'right'),
               ('PF5', 5, 0, 'trigonal bipyramidal', '90°, 120°', 'right'), ('PF5', 5, 0, 'trigonal bipyramidal', '120', 'wrong'),
               ('SO2', 2, 1, 'non-linear', '118', 'right'), ('SO2', 2, 1, 'non-linear', '120', 'wrong'),
               ('XeF4', 4, 2, 'square planar', '90', 'right'), ('XeF4', 4, 2, 'octahedral', '90', 'wrong'),
               ('BeCl2', 2, 0, 'linear', '180', 'right'), ('PCl6', 6, 0, 'octahedral', '90', 'right'),
               ('BF3', 3, 0, 'trigonal planar', '120', 'right'), ('SF6', 6, 0, 'octahedral', '90', 'right')]
        bad = []
        for i, bp, lp, shape, ang, want in TOL:
            got = answer(i, bp, lp, shape, ang)
            if got != want: bad.append(f'{i} {ang}: {got} (want {want})')
        check(f'{len(TOL)} tolerance / shape cases judged correctly', not bad, '; '.join(bad))
        page.evaluate("document.querySelector('.k').__vpAsk('CO2')")
        page.click('.vp-qbp button[data-v="2"]'); page.click('.vp-check'); page.wait_for_timeout(40)
        check('incomplete answer → asks to fill all 4, nothing scored',
              page.get_attribute('.vp-fb', 'data-result') == 'incomplete' and page.locator('.vp-qwork *').count() == 0)
        check('quiz: all fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
        answer('SCl2', 2, 2, 'non-linear', '104')

        check('no [data-clash] anywhere', page.locator('[data-clash]').count() == 0)

        print('== narrow viewport (720px)')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(150)
        ov = page.evaluate("() => { const k = document.querySelector('.k'); return k.scrollWidth - k.clientWidth; }")
        check('narrow 720px quiz: no horizontal overflow', ov <= 1, str(ov))
        check('narrow 720px quiz: fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
        page.click('button[data-tab="derive"]'); page.wait_for_timeout(60)
        for i in ('NH4', 'SO2', 'PCl6', 'XeF4', 'PF5'):
            expand(i)
            ov = page.evaluate("() => { const k = document.querySelector('.k'); return k.scrollWidth - k.clientWidth; }")
            sc = page.evaluate("() => { const s = document.querySelector('.vp-dwork .vp-svg'); return s.getBoundingClientRect().width / 330; }")
            check(f'narrow 720px {i}: no overflow, SVG scale >= 0.86 (13px labels stay >= 12px)', ov <= 1 and sc >= 0.86, f'{ov} {sc}')
        check('narrow 720px derive: fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
        expand('NH4'); shot('30-narrow-720-NH4')
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for r in results if r[1])
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
