"""ch04 deduce cell test.

usage: uv run --with playwright python -I colab/tests/ch04_deduce.py $COLAB_TMP/cells/ch04-deduce.html <shots-dir>
(build first: python3 tools/build_colab.py ch04 --cell deduce)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []

# id → (structure, bonding, terminal node) — the answer key, independent of the cell's own data
KEY = {'bi2o3': ('gi', 'ion', 'ti'), 'w': ('sm', 'cov', 'ts'), 'na': ('gm', 'met', 'tm'), 'na2o': ('gi', 'ion', 'ti'),
       'sn': ('gm', 'met', 'tm'), 'sio2': ('gc', 'cov', 'tc'), 'sicl4': ('sm', 'cov', 'ts'), 'bn': ('gc', 'cov', 'tc'),
       'mgo': ('gi', 'ion', 'ti'), 'so2': ('sm', 'cov', 'ts'), 'gr': ('gc', 'cov', 'tg'), 'i2': ('sm', 'cov', 'ts')}
SNAME = {'gi': 'giant ionic', 'gm': 'giant metallic', 'gc': 'giant molecular', 'sm': 'simple molecular'}


def shot(page, sel, path):
    """element screenshot via a page clip: Locator.screenshot waits for 'stable' (two rAFs), which
    hangs when several headless Chromes share the machine"""
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def run():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
        for scheme in ('light', 'dark'):
            ctx = b.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2, color_scheme=scheme)
            ctx.set_default_timeout(15000)
            page = ctx.new_page()
            page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
            page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
            page.goto(PAGE.as_uri(), timeout=20000); page.wait_for_timeout(400)

            def clashes():
                return page.locator('[data-clash]').count()

            def outside():
                return page.evaluate('''() => { const s = document.querySelector('.dd-fig'), v = s.viewBox.baseVal;
                    return [...s.querySelectorAll('text')].filter(t => { const b = t.getBBox();
                      return b.x < v.x - 0.5 || b.y < v.y - 0.5 || b.x + b.width > v.x + v.width + 0.5 || b.y + b.height > v.y + v.height + 0.5; })
                      .map(t => t.textContent); }''')

            def text_out_of_box():
                """node text spilling out of its own box"""
                return page.evaluate('''() => [...document.querySelectorAll('.dd-fig [data-node]')].filter(g => {
                    const r = g.querySelector('rect').getBBox();
                    return [...g.querySelectorAll('text')].some(t => { const b = t.getBBox();
                      return b.x < r.x + 3 || b.x + b.width > r.x + r.width - 3 || b.y < r.y + 1 || b.y + b.height > r.y + r.height - 1; });
                  }).map(g => g.getAttribute('data-node'))''')

            def boxes_overlap():
                return page.evaluate('''() => { const r = [...document.querySelectorAll('.dd-fig [data-node] rect')].map(e => e.getBBox()), o = [];
                    for (let i = 0; i < r.length; i++) for (let j = i + 1; j < r.length; j++) {
                      const a = r[i], b = r[j];
                      if (a.x < b.x + b.width + 4 && b.x < a.x + a.width + 4 && a.y < b.y + b.height + 4 && b.y < a.y + a.height + 4) o.push([i, j]); }
                    return o; }''')

            def card_id():
                return page.evaluate('() => document.querySelector(".k").__dd.CARDS[document.querySelector(".k").__dd.cur()].id')

            def pick(s, bnd):
                page.click(f'.dd-opts[data-k="s"] button[data-v="{s}"]')
                page.click(f'.dd-opts[data-k="b"] button[data-v="{bnd}"]')
                page.click('.dd-go')

            def lit():
                return page.evaluate('''() => ({
                    on: [...document.querySelectorAll('.dd-fig g.on')].map(g => g.getAttribute('data-node') || g.getAttribute('data-edge')),
                    end: [...document.querySelectorAll('.dd-fig g.end')].map(g => g.getAttribute('data-node')),
                    dim: document.querySelectorAll('.dd-fig g.dim').length,
                    pick: [...document.querySelectorAll('.dd-fig g.pick')].map(g => g.getAttribute('data-node')),
                    lit: document.querySelector('.dd-fig').classList.contains('lit'),
                    onMarkers: [...document.querySelectorAll('.dd-fig g.edge.on line')].every(l => l.getAttribute('marker-end').includes('dd-aron')) })''')

            def score():
                return page.inner_text('.dd-x') + '/' + page.inner_text('.dd-n')

            def verdict():
                v = page.locator('.dd-res [data-verdict]')
                return v.get_attribute('data-verdict') if v.count() else None

            check(f'{scheme}: no label clash at load', clashes() == 0, str(clashes()))
            check(f'{scheme}: flowchart labels inside viewBox', not outside(), str(outside()))
            check(f'{scheme}: node text stays inside its box', not text_out_of_box(), str(text_out_of_box()))
            check(f'{scheme}: node boxes do not overlap', not boxes_overlap(), str(boxes_overlap()))

            if scheme == 'dark':
                shot(page, '.k', OUT / 'card-dark-fresh.png')
                pick('gc', 'met')   # Bi2O3, wrong both
                shot(page, '.k', OUT / 'card-dark-wrong.png')
                page.click('.dd-next'); pick('sm', 'cov')   # W, right
                shot(page, '.k', OUT / 'card-dark-right.png')
                shot(page, '.dd-fig', OUT / 'fig-dark-right.png')
                check('dark: lit path drawn', lit()['end'] == ['ts'], str(lit()))
                check('dark: no label clash after submit', clashes() == 0, str(clashes()))
                # contrast: highlighted edge stroke differs from dimmed / default stroke
                cols = page.evaluate('''() => { const on = document.querySelector('.dd-fig g.edge.on line'), off = document.querySelector('.dd-fig g.edge.dim line');
                    return [getComputedStyle(on).stroke, getComputedStyle(off).stroke, getComputedStyle(off.parentNode).opacity]; }''')
                check('dark: lit edge colour differs from dim edge, dim faded', cols[0] != cols[1] and float(cols[2]) < 0.5, str(cols))
                ctx.close()
                continue

            print('== fresh card')
            check('starts on card 1 / 12 (Bi2O3)', page.inner_text('.dd-pos') == 'card 1 / 12' and card_id() == 'bi2o3', page.inner_text('.dd-pos'))
            check('source line shown', '9701/22 Feb/Mar 2024 Q1(b)(ii)' in page.inner_text('.dd-src'))
            check('Bi2O3 data verbatim', 'melts at 1090 K' in page.inner_text('.dd-data') and 'molten compound conducts electricity' in page.inner_text('.dd-data'))
            check('no result before submit, figure not lit', not page.is_visible('.dd-res') and not lit()['lit'])
            check('score starts 0 / 0', score() == '0/0', score())
            shot(page, '.k', OUT / 'card-fresh.png')

            page.click('.dd-go')
            check('submit with nothing chosen → hint, no grading', '两项都要选' in page.inner_text('.dd-hint') and score() == '0/0')
            page.click('.dd-opts[data-k="s"] button[data-v="gi"]')
            check('choice marked on', 'on' in page.get_attribute('.dd-opts[data-k="s"] button[data-v="gi"]', 'class'))
            page.click('.dd-go')
            check('only structure chosen → still not graded', score() == '0/0' and not page.is_visible('.dd-res'))

            print('== every card answered correctly')
            page.click('.dd-opts[data-k="b"] button[data-v="ion"]'); page.click('.dd-go')
            seen = []
            for i in range(12):
                cid = card_id(); seen.append(cid)
                s, bnd, term = KEY[cid]
                if i:
                    pick(s, bnd)
                L = lit()
                check(f'{cid}: judged right', verdict() == 'right', str(verdict()))
                check(f'{cid}: path ends at {term}', L['end'] == [term] and term in L['on'], str(L))
                check(f'{cid}: end box structure = {SNAME[s]}',
                      page.get_attribute(f'.dd-fig [data-node="{term}"]', 'data-st') == s)
                n_edges = sum(1 for x in L['on'] if '>' in x)
                check(f'{cid}: path is connected, starts at q1, others dimmed',
                      L['on'][0:1] and 'q1' in L['on'] and n_edges == len([x for x in L['on'] if '>' not in x]) - 1 and L['dim'] > 0 and L['onMarkers'], str(L))
                check(f'{cid}: M1 / M2 and 易错点 shown',
                      'M1' in page.inner_text('.dd-res') and 'M2' in page.inner_text('.dd-res') and '易错点' in page.inner_text('.dd-res'))
                check(f'{cid}: no clash', clashes() == 0, str(clashes()))
                if cid == 'bi2o3':
                    t = page.inner_text('.dd-res')
                    check('Bi2O3 M1 / M2 = mark scheme wording',
                          'giant AND has a high melting point' in t and 'ionic AND conducts electricity (only) when molten' in t, t)
                    shot(page, '.k', OUT / 'card-bi2o3-right.png')
                    fb = page.eval_on_selector('.dd-fig', 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width}; }')
                    sc = fb['width'] / 800
                    for name, (x, y, w_, h) in {'zoom-fig-left': (0, 0, 400, 400), 'zoom-fig-right': (400, 0, 400, 400)}.items():
                        page.screenshot(path=str(OUT / f'{name}.png'), clip={'x': fb['x'] + x * sc, 'y': fb['y'] + y * sc, 'width': w_ * sc, 'height': h * sc}, full_page=True)
                    shot(page, '.dd-res', OUT / 'zoom-res-bi2o3.png')
                if cid == 'gr':
                    shot(page, '.k', OUT / 'card-graphite-right.png')
                    check('graphite: 易错点 says not metallic', '不是' in page.inner_text('.dd-res .trap') and 'metallic' in page.inner_text('.dd-res .trap'))
                if cid == 'sicl4':
                    check('SiCl4: 易错点 Si–Cl not broken', 'Si–Cl' in page.inner_text('.dd-res .trap'))
                if cid == 'na2o':
                    check('Na2O: 易错点 ions move', 'ions' in page.inner_text('.dd-res .trap'))
                check(f'score after {i + 1} correct', score() == f'{i + 1}/{i + 1}', score())
                page.click('.dd-next')
            check('next × 12 visits all 12 cards', sorted(seen) == sorted(KEY), str(seen))
            check('next wraps 12 → 1', card_id() == 'bi2o3' and page.inner_text('.dd-pos') == 'card 1 / 12')
            page.click('.dd-prev')
            check('prev wraps 1 → 12', page.inner_text('.dd-pos') == 'card 12 / 12' and card_id() == 'i2')
            check('revisited card keeps its submitted state', verdict() == 'right' and lit()['lit'])

            print('== wrong answers')
            page.click('.dd-redo')
            check('redo clears the card, figure unlit', verdict() is None and not lit()['lit'] and not page.is_disabled('.dd-opts button'))
            pick('gi', 'ion')   # iodine as giant ionic
            check('iodine wrong → judged wrong', verdict() == 'wrong')
            check('re-submission does not change the score', score() == '12/12', score())
            t = page.inner_text('.dd-res')
            check('wrong → correct answer + explanation shown', 'simple molecular' in page.inner_text('.dd-ans') and '你选的是 giant ionic' in t and 'M1' in t, t)
            check('wrong choice red, right choice green',
                  'badv' in page.get_attribute('.dd-opts[data-k="s"] button[data-v="gi"]', 'class') and
                  'good' in page.get_attribute('.dd-opts[data-k="s"] button[data-v="sm"]', 'class'))
            L = lit()
            check('wrong → path still ends at the correct box; chosen box marked', L['end'] == ['ts'] and L['pick'] == ['ti'], str(L))
            check('choices locked after submit', page.is_disabled('.dd-opts[data-k="s"] button[data-v="gc"]'))

            # graphite as metallic: the classic trap, fresh state via reload
            page.reload(); page.wait_for_timeout(300)
            page.evaluate('() => document.querySelector(".k").__dd.show(10)')
            check('show(10) → graphite', card_id() == 'gr')
            pick('gm', 'met')
            check('graphite as giant metallic → wrong, score 0 / 1', verdict() == 'wrong' and score() == '0/1', score())
            L = lit()
            check('graphite path q1 → q2 → tg; tm marked as your pick', L['end'] == ['tg'] and 'q2>tg' in L['on'] and L['pick'] == ['tm'], str(L))
            check('partly right: structure ✗ bonding ✗ text', 'structure ✗' in page.inner_text('.dd-res') and 'bonding ✗' in page.inner_text('.dd-res'))
            shot(page, '.k', OUT / 'card-graphite-wrong.png')
            page.click('.dd-next')
            pick('gc', 'cov')   # iodine as giant molecular covalent: bonding right, structure wrong
            check('half right → wrong verdict, bonding ✓', verdict() == 'wrong' and 'bonding ✓' in page.inner_text('.dd-res') and score() == '0/2', score())
            check('giant molecular pick marks both giant molecular boxes', sorted(lit()['pick']) == ['tc', 'tg'], str(lit()))
            check('no clash (wrong states)', clashes() == 0, str(clashes()))

            print('== random')
            page.reload(); page.wait_for_timeout(300)
            seq = []
            for _ in range(8):
                page.click('.dd-rand'); seq.append(card_id())
            check('random never repeats the current card', all(a != b_ for a, b_ in zip(seq, seq[1:])), str(seq))
            page.reload(); page.wait_for_timeout(300)
            seq2 = []
            for _ in range(8):
                page.click('.dd-rand'); seq2.append(card_id())
            check('random is seeded (same sequence after reload)', seq == seq2, f'{seq} vs {seq2}')
            check('no console error so far', not errors, '; '.join(errors))

            print('== narrow (720 px)')
            page.evaluate('() => document.querySelector(".k").__dd.show(3)')
            pick('gi', 'ion')
            page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(250)
            ov = page.evaluate('() => { const k=document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
            check('no horizontal overflow at 720 px', ov <= 0, str(ov))
            fs = page.evaluate('''() => { const s = document.querySelector('.dd-fig'), k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
                return Math.min(...[...s.querySelectorAll('text')].map(t => parseFloat(getComputedStyle(t).fontSize) * k)); }''')
            check('figure font size (CSS px × rendered / viewBox width) ≥ 12 at 720 px', fs >= 12, f'{fs:.2f}')
            check('no clash at 720 px', clashes() == 0, str(clashes()))
            shot(page, '.k', OUT / 'card-720.png')
            ctx.close()
        b.close()


run()
check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
