"""ch14 cracking — cut a long-chain alkane, balance the cracking equation, fill-in quiz.

usage: uv run --with playwright python -I colab/tests/ch14_cracking.py $COLAB_TMP/cells/ch14-cracking.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch14 --cell cracking)
"""
import itertools
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
CHROMIUM = '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else chrome()
SUBD = '₀₁₂₃₄₅₆₇₈₉'
NC = {'C10': (10, 22), 'C12': (12, 26), 'C14': (14, 30)}


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def shot(page, sel, path):
    """Element screenshot via a page clip to avoid GPU rAF hang in headless mode."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


def ascii_digits(s):
    return ''.join(str(SUBD.index(ch)) if ch in SUBD else ch for ch in s)


def parse_side(s):
    """'C₈H₁₈ + 2C₂H₄' -> list of (coef, c, h)"""
    out = []
    for term in ascii_digits(s).split('+'):
        m = re.fullmatch(r'\s*(\d*)C(\d*)H(\d+)\s*', term)
        if not m:
            return None
        out.append((int(m.group(1) or 1), int(m.group(2) or 1), int(m.group(3))))
    return out


def eq_ok(lhs, rhs, n_frag):
    """balanced, ≥1 alkene, exactly one alkane, every product CnH2n or CnH2n+2, mol total = fragments"""
    L, R = parse_side(lhs), parse_side(rhs)
    if not L or not R:
        return False, f'unparsable {lhs} -> {rhs}'
    c = sum(k * a for k, a, _ in R); h = sum(k * b for k, _, b in R)
    alkene = sum(k for k, a, b in R if b == 2 * a)
    alkane = sum(k for k, a, b in R if b == 2 * a + 2)
    mol = sum(k for k, _, _ in R)
    ok = (c == L[0][1] and h == L[0][2] and alkene >= 1 and alkane == 1
          and alkene + alkane == mol and mol == n_frag)
    return ok, f'{lhs} -> {rhs}'


GEOM_JS = '''() => {
  const svg = document.querySelector('.crk-svg');
  const vb = svg.viewBox.baseVal, r = svg.getBoundingClientRect();
  const atoms = [...svg.querySelectorAll('circle.crk-atom')].map(c => ({i: +c.dataset.atom, x: +c.getAttribute('cx'), y: +c.getAttribute('cy')}));
  const labs = [...svg.querySelectorAll('text.crk-loc')].map(t => { const b = t.getBBox();
    return {t: t.textContent, cx: b.x + b.width / 2, cy: b.y + b.height / 2, x: b.x, y: b.y, w: b.width, h: b.height,
            fs: parseFloat(getComputedStyle(t).fontSize)}; });
  return {scale: r.width / vb.width, vb: [vb.x, vb.y, vb.width, vb.height], atoms, labs,
          clash: document.querySelectorAll('[data-clash]').length};
}'''


def check_geom(page, tag):
    g = page.evaluate(GEOM_JS)
    check(f'{tag}: no K.label data-clash', g['clash'] == 0, f"clash={g['clash']}")
    vx, vy, vw, vh = g['vb']
    inside = all(l['x'] >= vx and l['y'] >= vy and l['x'] + l['w'] <= vx + vw and l['y'] + l['h'] <= vy + vh for l in g['labs'])
    check(f'{tag}: all C labels inside viewBox', inside)
    # each label is nearest to its own atom, and within 30 viewBox units of it
    bad = []
    for l in g['labs']:
        own = int(l['t'][1:])
        d = {a['i']: ((a['x'] - l['cx']) ** 2 + (a['y'] - l['cy']) ** 2) ** .5 for a in g['atoms']}
        if min(d, key=d.get) != own or d[own] > 30:
            bad.append((l['t'], round(d[own], 1)))
    check(f'{tag}: every Cn label sits nearest its own atom (≤30)', not bad, str(bad[:4]))
    return g


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])

    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type in ('error', 'assert') else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.on('dialog', lambda d: (errors.append(f'DIALOG {d.message}'), d.dismiss()))
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300)

        check(f'{scheme}: cell loaded', page.is_visible('.crk-wrap'))
        targets = page.eval_on_selector_all(
            '.crk-svg .crk-hit', 'els => els.map(e => { const r = e.getBoundingClientRect(); return { w: r.width, h: r.height }; })')
        check(f'{scheme}: 11 cut targets, each ≥ 25 × 60 px', len(targets) == 11 and all(t['w'] >= 25 and t['h'] >= 60 for t in targets), str(targets[:2]))
        # cut positions must be visible before hover (the prompt says 点虚线处)
        guide = page.eval_on_selector('.crk-guide', 'e => getComputedStyle(e).stroke')
        check(f'{scheme}: dashed cut guides visible before any hover', guide not in ('transparent', 'rgba(0, 0, 0, 0)', 'none'), guide)
        if scheme == 'light':
            shot(page, '.k', OUT / 'initial.png')
        # hover feedback on a target
        page.hover('.crk-hit-wrap[data-bond="5"]')
        page.wait_for_timeout(250)
        hov = page.eval_on_selector('.crk-hit-wrap[data-bond="5"] .crk-guide', 'e => getComputedStyle(e).stroke')
        check(f'{scheme}: hovered guide changes colour', hov != guide, f'{hov} vs {guide}')
        layer = page.evaluate('''() => { const s = document.querySelector('.crk-svg');
            const lab = [...s.querySelectorAll('text.crk-loc')].find(t => t.textContent === 'C5').getBBox();
            const hit = s.querySelector('.crk-hit-wrap[data-bond="5"]');
            return {first: s.firstElementChild.classList.contains('crk-g-targets'),
                    labAfter: !!(hit.compareDocumentPosition(s.querySelector('text.crk-loc')) & Node.DOCUMENT_POSITION_FOLLOWING)}; }''')
        check(f'{scheme}: hover tint layer painted under labels / bonds', layer['first'] and layer['labAfter'], str(layer))
        shot(page, '.crk-stage-card', OUT / f'{scheme}-hover.png')
        page.mouse.move(5, 5)

        page.click('.crk-hit-wrap[data-bond="8"]')
        page.wait_for_timeout(100)
        check(f'{scheme}: cutting bond 8 → count 1', page.eval_on_selector('.crk-cut-num', 'e => e.textContent') == '1')
        rhs = page.eval_on_selector('.crk-eq-rhs', 'e => e.textContent')
        check(f'{scheme}: one cut at C8–C9 gives C₈H₁₈ + C₄H₈', rhs == 'C₈H₁₈ + C₄H₈', rhs)
        dbs = page.eval_on_selector_all('.crk-db', 'els => els.map(e => +e.dataset.db)')
        check(f'{scheme}: alkene fragment C9–C12 drawn with C=C at C9=C10', dbs == [9], str(dbs))
        names = page.eval_on_selector_all('.crk-frag-name b', 'els => els.map(e => e.textContent)')
        check(f'{scheme}: product names octane / but-1-ene (match drawn C=C)', names == ['octane', 'but-1-ene'], str(names))
        heads = page.eval_on_selector_all('.crk-frag-num', 'els => els.map(e => e.textContent)')
        check(f'{scheme}: fragment heads give IUPAC carbon range', heads == ['碎片 1：C1–C8', '碎片 2：C9–C12'], str(heads))

        ca = page.eval_on_selector('.crk-frag-card.alkane', 'e => getComputedStyle(e).borderColor')
        ce = page.eval_on_selector('.crk-frag-card.alkene', 'e => getComputedStyle(e).borderColor')
        check(f'{scheme}: alkane / alkene cards distinct colours', ca != ce, f'{ca} vs {ce}')
        na = page.eval_on_selector('.crk-atom.alkane', 'e => getComputedStyle(e).fill')
        ne = page.eval_on_selector('.crk-atom.alkene', 'e => getComputedStyle(e).fill')
        check(f'{scheme}: alkane / alkene atoms distinct fills', na != ne, f'{na} vs {ne}')
        dbc = page.eval_on_selector('.crk-db', 'e => getComputedStyle(e).stroke')
        check(f'{scheme}: C=C second line has alkene colour', dbc == ne, f'{dbc} vs {ne}')
        check_geom(page, scheme)
        shot(page, '.k', OUT / f'{scheme}.png')

        # 3-cut state with a middle alkene fragment
        page.click('.crk-hit-wrap[data-bond="3"]')
        page.click('.crk-hit-wrap[data-bond="5"]')
        page.wait_for_timeout(150)
        check_geom(page, f'{scheme} 3 cuts')
        shot(page, '.k', OUT / f'{scheme}-3cuts.png')
        if scheme == 'light':
            # z = 3 detail of the chain
            ctx2 = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=3, color_scheme=scheme)
            pz = ctx2.new_page()
            pz.goto(PAGE.as_uri()); pz.wait_for_timeout(300)
            for k in (3, 5, 8):
                pz.click(f'.crk-hit-wrap[data-bond="{k}"]')
            pz.wait_for_timeout(150)
            shot(pz, '.crk-svg', OUT / 'zoom-chain-z3.png')
            ctx2.close()
        ctx.close()

    # ---------- logic / chemistry ----------
    ctx = b.new_context(viewport={'width': 1000, 'height': 1200}, device_scale_factor=1)
    page = ctx.new_page()
    page.on('console', lambda m: errors.append(f'{m.text}') if m.type in ('error', 'assert') else None)
    page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
    page.on('dialog', lambda d: (errors.append(f'DIALOG {d.message}'), d.dismiss()))
    page.goto(PAGE.as_uri())
    page.wait_for_timeout(300)
    page.evaluate('() => { window.__crkApi = [...document.querySelectorAll("*")].find(e => e.__crk).__crk; }')

    # exhaustive: every 1-, 2- and 3-cut set on every substrate
    STATE_JS = '''() => ({lhs: document.querySelector('.crk-eq-lhs').textContent,
      rhs: document.querySelector('.crk-eq-rhs').textContent,
      eq: !document.querySelector('.crk-eq-card').hidden, warn: !document.querySelector('.crk-warn-card').hidden,
      cards: document.querySelectorAll('.crk-frag-card').length,
      db: document.querySelectorAll('.crk-db').length,
      alkCards: document.querySelectorAll('.crk-frag-card.alkene').length,
      mr: document.querySelector('.crk-mass-row').textContent,
      clash: document.querySelectorAll('[data-clash]').length})'''
    for key, (n, hh) in NC.items():
        page.click(f'.crk-sub-btn[data-k="{key}"]')
        page.wait_for_timeout(50)
        fails, warn_bad, n_sets = [], [], 0
        for r in (1, 2, 3):
            for combo in itertools.combinations(range(1, n), r):
                n_sets += 1
                page.evaluate('(cs) => { const a = window.__crkApi; a.resetCuts(); cs.forEach(c => a.cutBond(c)); }', list(combo))
                st = page.evaluate(STATE_JS)
                frs = [b2 - a2 for a2, b2 in zip((0,) + combo, combo + (n,))]
                ones = sum(1 for f in frs if f == 1)
                if ones >= 2:
                    if not (st['warn'] and not st['eq']):
                        warn_bad.append(combo)
                    continue
                ok, det = eq_ok(st['lhs'], st['rhs'], len(frs))
                expect_db = len(frs) - 1
                if not ok or st['cards'] != len(frs) or st['db'] != expect_db or st['alkCards'] != expect_db or st['clash']:
                    fails.append((combo, det, st['db'], st['clash']))
        check(f'{key}: all {n_sets} cut sets balanced, 1 alkane + ≥1 alkene, one C=C per alkene, clash 0', not fails, str(fails[:3]))
        check(f'{key}: ≥2 single-C fragments → warning, no equation', not warn_bad, str(warn_bad[:3]))
        lhs = page.eval_on_selector('.crk-eq-lhs', 'e => e.textContent')
        check(f'{key}: reactant formula', ascii_digits(lhs) == f'C{n}H{hh}', lhs)

    # Mr row: C12 cut at 4 & 8 → C₄H₁₀ + 2C₄H₈, 58.0 + 2 × 56.0 = 170.0
    page.click('.crk-sub-btn[data-k="C12"]')
    page.evaluate('() => { const a = window.__crkApi; a.resetCuts(); a.cutBond(4); a.cutBond(8); }')
    st = page.evaluate(STATE_JS)
    check('C12 cuts 4,8: equation C₁₂H₂₆ → C₄H₁₀ + 2C₄H₈', st['rhs'] == 'C₄H₁₀ + 2C₄H₈', st['rhs'])
    check('C12 cuts 4,8: Mr row 170.0 = 58.0 + 2 × 56.0 = 170.0',
          'Reactant Mᵣ = 170.0' in st['mr'] and '58.0 + 2 × 56.0 = 170.0' in st['mr'], st['mr'])

    # switching the alkane fragment keeps the equation balanced and moves the C=C
    ALK_JS = '() => [...document.querySelectorAll(".crk-frag-card")].findIndex(e => e.classList.contains("alkane"))'
    before = page.evaluate(ALK_JS)
    page.locator('.crk-btn-set-alkane').first.click()
    page.wait_for_timeout(50)
    st2 = page.evaluate(STATE_JS)
    after = page.evaluate(ALK_JS)
    ok, det = eq_ok(st2['lhs'], st2['rhs'], 3)
    check('set-alkane button: alkane moves to that fragment, still balanced, C=C count unchanged',
          ok and before == 0 and after == 1 and st2['db'] == 2, f'{det} alkane {before}->{after} db={st2["db"]}')
    # a single-C fragment must be methane → no set-alkane buttons offered
    page.evaluate('() => { const a = window.__crkApi; a.resetCuts(); a.cutBond(1); }')
    page.wait_for_timeout(50)
    rhs1 = page.eval_on_selector('.crk-eq-rhs', 'e => e.textContent')
    check('cut C1–C2: CH₄ + C₁₁H₂₂', rhs1 == 'CH₄ + C₁₁H₂₂', rhs1)
    check('cut C1–C2: no (useless) set-alkane button', page.locator('.crk-btn-set-alkane').count() == 0)

    # 4th cut capped inline
    page.evaluate('() => { const a = window.__crkApi; a.resetCuts(); }')
    for k in (2, 5, 8, 10):
        page.click(f'.crk-hit-wrap[data-bond="{k}"]')
    page.wait_for_timeout(100)
    check('4th cut rejected inline (no dialog)', '3 刀' in page.eval_on_selector('.crk-cap-msg', 'e => e.textContent'))
    check('cuts capped at 3', page.eval_on_selector('.crk-cut-num', 'e => e.textContent') == '3')
    page.click('.crk-hit-wrap[data-bond="8"]')  # undo one
    check('clicking a cut bond undoes it', page.eval_on_selector('.crk-cut-num', 'e => e.textContent') == '2')
    page.click('.crk-reset-btn')
    page.wait_for_timeout(50)
    check('reset clears cuts', page.eval_on_selector('.crk-cut-num', 'e => e.textContent') == '0' and page.is_visible('.crk-empty-card'))

    # ---------- quiz ----------
    page.click('button[data-tab="quiz"]')
    page.wait_for_timeout(200)
    check('quiz pane displayed', page.is_visible('[data-pane="quiz"].show'))

    def answer(idx, val):
        page.evaluate(f'() => window.__crkApi.setQuiz({idx})')
        page.fill('.crk-qinp', val)
        page.click('.crk-qcheck')
        good = page.is_visible('.crk-qinp.good')
        return good, page.inner_text('.crk-qfeedback')

    for idx, right in ((0, 'C4H8'), (1, 'C3H6'), (2, 'C2H4'), (3, 'C2H4'), (4, 'C8H18')):
        g, fb = answer(idx, right)
        check(f'Q{idx + 1}: {right} ✓', g and '正确' in fb, fb)
    g, fb = answer(0, 'C₄H₈')
    check('Q1: Unicode C₄H₈ ✓', g)
    g, fb = answer(0, 'H8C4')
    check('Q1: H8C4 ✗ with 顺序', not g and '顺序' in fb, fb)
    g, fb = answer(4, 'H18C8')
    check('Q5: H18C8 ✗ with 顺序', not g and '顺序' in fb, fb)
    g, fb = answer(0, 'c4h8')
    check('Q1: lower-case c4h8 ✗ (大小写)', not g and '大小写' in fb, fb)
    g, fb = answer(0, 'C4H10')
    check('Q1: C4H10 ✗ (C, H 守恒 hint)', not g and 'C、H' in fb, fb)
    g, fb = answer(3, '3C2H4')
    check('Q4: coefficient typed twice (3C2H4) ✗', not g)
    for v in ('Al2O3', 'Al₂O₃', 'aluminium oxide', 'heat with Al2O3'):
        g, fb = answer(5, v)
        check(f'Q6: "{v}" ✓', g, fb)
    g, fb = answer(5, 'al2o3')
    check('Q6: al2o3 ✗ (大小写)', not g and '大小写' in fb, fb)
    g, fb = answer(6, 'cracking')
    check('Q7: cracking ✓', g, fb)
    g, fb = answer(6, 'fractional distillation')
    check('Q7: fractional distillation ✗', not g)
    src = page.eval_on_selector('.crk-qsrc', 'e => e.textContent')
    check('Q7 source is the real paper', src == '9701/22 Oct/Nov 2025 Q3(c)', src)
    page.evaluate('() => window.__crkApi.setQuiz(5)')
    check('Q6 source is the real paper', page.eval_on_selector('.crk-qsrc', 'e => e.textContent') == '9701/23 May/June 2025 Q3(a)(i)')
    page.click('.crk-qshow')
    check('Q6 show answer fills Al2O3', page.input_value('.crk-qinp') == 'Al2O3')
    page.evaluate('() => window.__crkApi.setQuiz(6)')
    page.click('.crk-qshow')
    check('Q7 show answer fills cracking', page.input_value('.crk-qinp') == 'cracking')

    page.evaluate('() => window.__crkApi.setQuiz(7)')
    page.click('.crk-qopt[data-v="b"]'); page.click('.crk-qcheck')
    check('Q8: option B ✗', page.is_visible('.crk-qopt.badv'))
    page.click('.crk-qopt[data-v="a"]'); page.click('.crk-qcheck')
    check('Q8: option A ✓', page.is_visible('.crk-qopt.good') and '正确' in page.inner_text('.crk-qfeedback'))
    sc = page.eval_on_selector('.crk-qscore', 'e => e.textContent')
    check('score counts 8 / 8 after all correct', '8' in sc and '/ 8' in sc, sc)

    page.evaluate('() => window.__crkApi.setQuiz(0)')
    page.fill('.crk-qinp', 'H8C4'); page.click('.crk-qcheck')
    shot(page, '.crk-qcard', OUT / 'quiz-order.png')
    page.evaluate('() => window.__crkApi.setQuiz(5)')
    page.fill('.crk-qinp', 'aluminium oxide'); page.click('.crk-qcheck')
    shot(page, '.crk-qcard', OUT / 'quiz.png')

    pt_btn = page.locator('.pt-btn')
    check('k-ptable button rendered', pt_btn.is_visible())

    # no literal markdown asterisks / untranslated chemistry-term slips
    txt = page.evaluate('() => document.querySelector(".k").innerText')
    check('no literal * in rendered text', '*' not in txt)
    check('no Chinese translation of chemistry terms (烯烃/烷烃/催化裂化/乙醇)',
          not re.search('烯烃|烷烃|催化裂化|乙醇|乙烯|丙烯', txt))
    ctx.close()

    # ---------- 720 px ----------
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 720, 'height': 1200}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type in ('error', 'assert') else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300)
        page.click('.crk-sub-btn[data-k="C14"]')
        for k in (4, 8):
            page.click(f'.crk-hit-wrap[data-bond="{k}"]')
        page.wait_for_timeout(150)
        ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
        check(f'720 {scheme}: no horizontal overflow', ov <= 1, f'overflow={ov}')
        svg_ov = page.evaluate('() => { const w = document.querySelector(".crk-svg-wrap"); return w.scrollWidth - w.clientWidth; }')
        check(f'720 {scheme}: chain svg not scrolled sideways', svg_ov <= 1, f'{svg_ov}')
        g = check_geom(page, f'720 {scheme}')
        eff = min(l['fs'] for l in g['labs']) * g['scale']
        check(f'720 {scheme}: rendered C-label size ≥ 12 px (CSS × width / viewBox)', eff >= 12, f'{eff:.2f}px')
        tgt = page.eval_on_selector_all('.crk-svg .crk-hit', 'els => els.map(e => e.getBoundingClientRect().width)')
        check(f'720 {scheme}: C14 cut targets still ≥ 25 px wide', min(tgt) >= 25, f'{min(tgt):.1f}')
        small = page.evaluate('''() => [...document.querySelectorAll('.crk-wrap *')].filter(e =>
            e.childNodes.length && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) &&
            e.getClientRects().length && !e.closest('svg') && !e.closest('sub') && e.tagName !== 'SUB' &&
            parseFloat(getComputedStyle(e).fontSize) < 12).map(e => e.className + ':' + getComputedStyle(e).fontSize)''')
        check(f'720 {scheme}: no HTML text below 12 px', not small, str(small[:4]))
        shot(page, '.k', OUT / f'mobile-720-{scheme}.png')
        ctx.close()
    b.close()

check('no console errors / asserts / dialogs', len(errors) == 0, '; '.join(errors[:5]))

passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f'\n{passed}/{total} passed')
sys.exit(0 if passed == total else 1)
