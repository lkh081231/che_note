"""ch02 ion-formula cell test: ionic formula builder, charge prediction from the Periodic Table, 9-ion quiz.

usage: uv run --with playwright python -I colab/tests/ch02_ion-formula.py <preview.html> <shots-dir>
(build the preview first: python tools/build_colab.py ch02 --cell ion-formula)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1])
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def build(page, c, a):
    page.click(f'.if-cats button[data-ion="{c}"]'); page.click(f'.if-ans button[data-ion="{a}"]')
    return (page.inner_text('.if-out .if-f') if page.locator('.if-out .if-f').count() else '',
            page.inner_text('.if-out .if-name') if page.locator('.if-out .if-name').count() else '')


def squares(page):
    return page.locator('.if-top .if-sq').count(), page.locator('.if-bot .if-sq').count()


# labels of neighbouring ion groups must not touch; no box may stick out of the card
OVERLAP_JS = '''() => {
  const bad = [];
  for (const row of document.querySelectorAll('.if-row')) {
    const ls = [...row.querySelectorAll('.if-lab')].map(e => e.getBoundingClientRect());
    for (let i = 1; i < ls.length; i++) if (ls[i].left < ls[i-1].right + 2) bad.push('label ' + i);
  }
  const st = document.querySelector('.if-stage');
  if (st.scrollWidth > st.clientWidth + 1) bad.push('stage scrolls ' + st.scrollWidth + '>' + st.clientWidth);
  const k = document.querySelector('.k');
  if (k.scrollWidth > k.clientWidth + 1) bad.push('card overflows');
  return bad; }'''

SMALL_JS = '''() => { const out = [];
  for (const e of document.querySelectorAll('.k *')) {
    if (!e.offsetParent && e.tagName !== 'svg') continue;
    const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (own && parseFloat(getComputedStyle(e).fontSize) < 12) out.push(e.tagName + '.' + e.className + ':' + e.textContent.slice(0, 20));
  } return out; }'''

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])  # GPU process can stall → rAF never fires → screenshot hangs on 'element stable'
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1000}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(500)
        sfx = '' if scheme == 'light' else '-dark'

        def shot(name, sel='.k'):
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        if scheme == 'dark':
            shot('01-build-AlSO4'); page.click('[data-tab=pt]'); shot('05-pt-Mg'); page.click('[data-tab=quiz]'); shot('07-quiz')
            ctx.close(); continue

        print('== tab 1: build')
        f, n = page.inner_text('.if-out .if-f'), page.inner_text('.if-out .if-name')
        check('default Al³⁺ + SO₄²⁻ → Al₂(SO₄)₃', f == 'Al₂(SO₄)₃', f)
        check('default name aluminium sulfate', n == 'aluminium sulfate', n)
        check('Al₂(SO₄)₃: 6 + squares = 6 − squares', squares(page) == (6, 6), str(squares(page)))
        check('tally says total charge 0', 'total charge 0' in page.inner_text('.if-tally'))
        out = page.inner_text('.if-out')
        check('working shows lcm 6, 2 Al³⁺, 3 SO₄²⁻', 'lowest common multiple of 3 和 2 = 6' in out and '6 ÷ 3 = 2' in out and '6 ÷ 2 = 3' in out, out)
        check('Group 13 → no Roman numeral note', '不是 aluminium(III)' in out, out)
        shot('01-build-AlSO4')
        page.locator('.if-stage').screenshot(path=str(OUT / '02-zoom-blocks-AlSO4.png'))

        for c, a, ef, en, sq in [('NH4', 'PO4', '(NH₄)₃PO₄', 'ammonium phosphate', (3, 3)),
                                 ('Fe3', 'OH', 'Fe(OH)₃', 'iron(III) hydroxide', (3, 3)),
                                 ('Fe2', 'SO4', 'FeSO₄', 'iron(II) sulfate', (2, 2)),
                                 ('Mg', 'O', 'MgO', 'magnesium oxide', (2, 2)),
                                 ('Ca', 'NO3', 'Ca(NO₃)₂', 'calcium nitrate', (2, 2)),
                                 ('Mg', 'N', 'Mg₃N₂', 'magnesium nitride', (6, 6)),
                                 ('Zn', 'NO3', 'Zn(NO₃)₂', 'zinc nitrate', (2, 2)),
                                 ('NH4', 'SO4', '(NH₄)₂SO₄', 'ammonium sulfate', (2, 2)),
                                 ('Ca', 'PO4', 'Ca₃(PO₄)₂', 'calcium phosphate', (6, 6)),
                                 ('Cu2', 'Cl', 'CuCl₂', 'copper(II) chloride', (2, 2)),
                                 ('Ag', 'NO3', 'AgNO₃', 'silver nitrate', (1, 1))]:
            f, n = build(page, c, a)
            check(f'{c} + {a} → {ef}, {en}', (f, n) == (ef, en), f'{f} / {n}')
            check(f'{c} + {a}: blocks {sq}', squares(page) == sq, str(squares(page)))
        build(page, 'NH4', 'PO4'); shot('03-build-NH4PO4')
        build(page, 'Fe3', 'OH')
        out = page.inner_text('.if-out')
        check('Fe(OH)₃: brackets step + Roman numeral reason', '(OH)₃' in out and 'Roman numeral' in out and 'Fe²⁺ / Fe³⁺' in out, out)
        page.locator('.if-out').screenshot(path=str(OUT / '04-zoom-out-FeOH3.png'))

        # every pairing: blocks balance, labels never collide, nothing overflows
        combos = page.evaluate('() => { const f = document.querySelector(".k").__ionf; return f.CAT.flatMap(c => f.AN.map(a => [c.key, a.key])); }')
        bad = []
        for c, a in combos:
            build(page, c, a)
            pos, neg = squares(page)
            if pos != neg or page.get_attribute('.if-out', 'data-state') != 'ok':
                bad.append(f'{c}+{a} {pos}/{neg}')
            ov = page.evaluate(OVERLAP_JS)
            if ov:
                bad.append(f'{c}+{a} {ov}')
        check(f'all {len(combos)} pairings balance with no label overlap / overflow', not bad, '; '.join(bad[:6]))

        # steppers
        build(page, 'Al', 'SO4'); page.click('.if-one')
        check('1 : 1 → unbalanced state', page.get_attribute('.if-out', 'data-state') == 'unbalanced')
        check('1 : 1 → 1 hatched (unmatched) square', page.locator('.if-sq.if-un').count() == 1, str(page.locator('.if-sq.if-un').count()))
        check('tally shows +1 left over', 'total charge +1' in page.inner_text('.if-tally'), page.inner_text('.if-tally'))
        shot('06-build-unbalanced')
        page.click('.if-cp'); page.click('.if-ap'); page.click('.if-ap')
        check('stepped to 2 : 3 → balanced ok', page.get_attribute('.if-out', 'data-state') == 'ok' and page.inner_text('.if-f') == 'Al₂(SO₄)₃')
        build(page, 'Mg', 'O'); page.click('.if-cp'); page.click('.if-ap')
        check('MgO at 2 : 2 → reducible note', page.get_attribute('.if-out', 'data-state') == 'reducible' and '最简整数比' in page.inner_text('.if-out'))
        for _ in range(5): page.click('.if-cp', force=True)
        check('cation count capped at 4', page.inner_text('.if-nc') == '4')
        check('max 4 cations: no overflow', not page.evaluate(OVERLAP_JS), str(page.evaluate(OVERLAP_JS)))
        page.click('.if-auto'); check('自动配平 → back to 1 : 1 MgO', page.inner_text('.if-f') == 'MgO')
        check('tab 1: font ≥ 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))

        print('== tab 2: Periodic Table')
        page.click('[data-tab=pt]')
        check('default Mg → Mg²⁺', page.inner_text('.if-ptout .if-f') == 'Mg²⁺')
        shot('05-pt-Mg')
        for el, ion, word in [('Na', 'Na⁺', 'sodium'), ('Al', 'Al³⁺', 'aluminium'), ('O', 'O²⁻', 'oxide'), ('N', 'N³⁻', 'nitride'),
                              ('S', 'S²⁻', 'sulfide'), ('Cl', 'Cl⁻', 'chloride'), ('Br', 'Br⁻', 'bromide'), ('K', 'K⁺', 'potassium'),
                              ('P', 'P³⁻', 'phosphide'), ('Ca', 'Ca²⁺', 'calcium')]:
            page.click(f'.if-pt button[data-el="{el}"]')
            t = page.inner_text('.if-ptout')
            check(f'{el} → {ion} ({word})', page.inner_text('.if-ptout .if-f') == ion and word in t, t[:80])
        page.click('.if-pt button[data-el="N"]'); t = page.inner_text('.if-ptout')
        check('N³⁻ config same as Ne, example Mg₃N₂', '和 Ne 一样' in t and 'Mg₃N₂ magnesium nitride' in t, t)
        page.locator('.if-ptout').screenshot(path=str(OUT / '08-zoom-pt-N.png'))
        page.click('.if-pt button[data-el="Si"]'); check('Si → covalent, no simple ion', '不形成简单 ion' in page.inner_text('.if-ptout'))
        page.click('.if-pt button[data-el="Ar"]'); check('Ar → noble gas, no ion', '不形成 ion' in page.inner_text('.if-ptout'))
        page.click('.if-pt button[data-el="B"]'); check('B → no B³⁺', '不形成 B³⁺' in page.inner_text('.if-ptout'))
        page.click('.if-pt button[data-el="Ga"]'); check('Ga³⁺ 3d¹⁰ note', 'Ga³⁺' in page.inner_text('.if-ptout') and '3d¹⁰' in page.inner_text('.if-ptout'))
        page.click('.if-pt button[data-el="O"]')
        page.locator('.if-pt').screenshot(path=str(OUT / '09-zoom-pt-grid.png'))
        check('tab 2: font ≥ 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))

        print('== tab 3: quiz')
        page.click('[data-tab=quiz]')
        seen, ok_dirs = set(), set()
        for i in range(9):
            ans = page.get_attribute('.if-quiz', 'data-ans'); seen.add(page.get_attribute('.if-quiz', 'data-ion'))
            ok_dirs.add(page.get_attribute('.if-quiz', 'data-dir'))
            opts = page.locator('.if-opts button')
            vals = [opts.nth(k).get_attribute('data-v') for k in range(opts.count())]
            if i == 0:
                check('4 distinct options incl. the answer', len(set(vals)) == 4 and ans in vals, str(vals))
            if i == 1:   # answer wrong on purpose
                wrong = next(v for v in vals if v != ans)
                page.click(f'.if-opts button[data-v="{wrong}"]')
                check('wrong pick → badv + right one shown good', page.locator('.if-opts button.badv').count() == 1 and
                      page.get_attribute(f'.if-opts button[data-v="{ans}"]', 'class') == 'good')
                check('wrong → ✗ feedback', '✗' in page.inner_text('.if-why'))
                check('options locked after answering', page.locator('.if-opts button:disabled').count() == 4)
                shot('07-quiz-wrong')
            else:
                page.click(f'.if-opts button[data-v="{ans}"]')
                if i == 0:
                    check('right pick → good + ✓', 'good' in page.get_attribute(f'.if-opts button[data-v="{ans}"]', 'class') and '✓' in page.inner_text('.if-why'))
                    check('score 1 / 1', '1 / 1' in page.inner_text('.if-score'), page.inner_text('.if-score'))
            page.click('.if-next')
        check('score 8 / 9 after one round', '8 / 9' in page.inner_text('.if-score'), page.inner_text('.if-score'))
        check('one round covers all 9 ions', len(seen) == 9, str(seen))
        # directions are random; over 9 questions both should almost always appear, so retry a little
        for _ in range(20):
            if len(ok_dirs) == 2: break
            ok_dirs.add(page.get_attribute('.if-quiz', 'data-dir')); page.click('.if-next')
        check('both quiz directions occur', ok_dirs == {'f', 'n'}, str(ok_dirs))
        shot('07-quiz')
        check('tab 3: font ≥ 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
        check('no [data-clash]', page.locator('[data-clash]').count() == 0)

        print('== narrow (700 px)')
        page.set_viewport_size({'width': 720, 'height': 1000}); page.click('[data-tab=build]')
        bad = []
        for c, a in [('Al', 'SO4'), ('Ca', 'PO4'), ('Al', 'HCO3'), ('NH4', 'PO4'), ('Cr3', 'NO3')]:
            build(page, c, a); ov = page.evaluate(OVERLAP_JS)
            if ov: bad.append(f'{c}+{a} {ov}')
        build(page, 'Al', 'Cl'); page.click('.if-one'); [page.click('.if-cp') for _ in range(3)]; [page.click('.if-ap') for _ in range(3)]
        ov = page.evaluate(OVERLAP_JS)
        if ov: bad.append(f'4 Al + 4 Cl {ov}')
        check('narrow: no overlap / overflow (incl. 4 Al³⁺ = 12 squares)', not bad, '; '.join(bad))
        check('4 : 4 with anions maxed → hint says 减 cation', '减 cation' in page.inner_text('.if-out'), page.inner_text('.if-out'))
        shot('10-narrow-max')
        page.click('[data-tab=pt]'); check('narrow: PT fits', page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth <= k.clientWidth + 1; }'))
        shot('11-narrow-pt')
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
