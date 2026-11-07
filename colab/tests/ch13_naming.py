"""ch13 naming — IUPAC 命名练习与四步拆解 cell test.

usage: uv run --with playwright python -I colab/tests/ch13_naming.py $COLAB_TMP/cells/ch13-naming.html <shots-dir>
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch13 --cell naming)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []
CHROMIUM = '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else chrome()

HELP = r'''() => { window.T = {
  rr(a, b) {
    const dx = Math.max(a.x - b.x - b.width, 0, b.x - a.x - a.width);
    const dy = Math.max(a.y - b.y - b.height, 0, b.y - a.y - a.height);
    return Math.hypot(dx, dy);
  },
  visSvgs() {
    return [...document.querySelectorAll('.nm-stage svg, .nm-walk-stage svg, .nm-opt-svg svg')]
      .filter(s => s.getBoundingClientRect().width > 0);
  },
  outside() {
    return T.visSvgs().flatMap(s => {
      const v = s.viewBox.baseVal;
      return [...s.querySelectorAll('text, circle, line')].filter(el => {
        if (el.closest('defs') || getComputedStyle(el).display === 'none') return false;
        const b = el.getBBox();
        return b.x < v.x - 0.8 || b.y < v.y - 0.8 ||
               b.x + b.width > v.x + v.width + 0.8 || b.y + b.height > v.y + v.height + 0.8;
      }).map(el => (el.textContent || el.tagName) + '@' + s.parentElement.className);
    });
  },
  locants(sel) {
    const svg = document.querySelector(sel);
    const D = KO.atoms(svg);
    return [...svg.querySelectorAll('text.ko-num')].map(t => {
      const i = +t.getAttribute('data-atom'), rb = t.getBBox();
      const b = { x: rb.x, y: rb.y, width: rb.width, height: rb.height };
      const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
      const box = a => {
        if (!a.el) return { x: a.x - 2.5, y: a.y - 2.5, width: 5, height: 5 };
        const r = a.el.getBBox();
        return { x: r.x, y: r.y, width: r.width, height: r.height };
      };
      const own = T.rr(b, box(D.atoms[i]));
      const other = Math.min(...D.atoms.filter(a => a.i !== i).map(a => T.rr(b, box(a))));
      const dOwn = Math.hypot(D.atoms[i].x - cx, D.atoms[i].y - cy);
      const dOther = Math.min(...D.atoms.filter(a => a.i !== i).map(a => Math.hypot(a.x - cx, a.y - cy)));
      return { txt: t.textContent, i, x: cx, y: cy, ax: D.atoms[i].x, ay: D.atoms[i].y, own, other, dOwn, dOther };
    });
  },
  minSvgFontPx() {
    const vals = T.visSvgs().flatMap(s => {
      const k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
      return [...s.querySelectorAll('text')]
        .filter(t => getComputedStyle(t).display !== 'none')
        .map(t => ({
          px: parseFloat(getComputedStyle(t).fontSize) * k,
          txt: t.textContent,
          cls: s.parentElement.className
        }));
    });
    if (!vals.length) return { px: 99, txt: '', cls: '' };
    return vals.reduce((a, b) => a.px <= b.px ? a : b);
  }
}; }'''


def shot(page, sel, path):
    """element screenshot via a page clip (avoids Locator.screenshot GPU rAF hang)."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


# Static HTML sanity check: no literal '*' leaked into markup outside <script>/<style>
raw_html = PAGE.read_text(encoding='utf-8')
import re
stripped = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', raw_html, flags=re.S | re.I)
stripped = re.sub(r'<[^>]+>', '', stripped)
check('built HTML has no leaked literal * in visible text', '*' not in stripped, stripped[:120])

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1300}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(350)
        page.evaluate(HELP)

        def go_qi(qi):
            page.evaluate(f'document.querySelector(".k").__naming.goQi({qi})')
            page.wait_for_timeout(20)

        def q_idx(name):
            return page.evaluate(f'document.querySelector(".k").__naming.Q.findIndex(q => q.name === {name!r})')

        if scheme == 'dark':
            print('== dark theme')
            i_br = q_idx('3-ethyl-2-methylpentane')
            go_qi(i_br)
            page.fill('.nm-in', '2-methyl-3-ethylpentane')
            page.click('.nm-go'); page.wait_for_timeout(30)
            page.evaluate('document.querySelector(".k").__naming.setStep(4)'); page.wait_for_timeout(30)
            check('dark: no [data-clash] in Mode 1 Step 4', page.locator('[data-clash]').count() == 0)
            check('dark: everything inside viewBox', not page.evaluate('T.outside()'))
            shot(page, '.k', OUT / 'card-write-dark.png')

            i_halo = q_idx('2-bromo-3,3-dichlorohexane')
            go_qi(i_halo)
            page.evaluate('document.querySelector(".k").__naming.setStep(4)'); page.wait_for_timeout(30)
            shot(page, '.nm-stage-card', OUT / 'z2-step4-halo-dark.png')

            page.click('.nm-modes button[data-mode="pick"]'); page.wait_for_timeout(30)
            go_qi(q_idx('butanenitrile'))
            page.click('.nm-opt[data-ok="0"]'); page.wait_for_timeout(30)
            check('dark: no [data-clash] in Mode 2', page.locator('[data-clash]').count() == 0)
            shot(page, '.k', OUT / 'card-pick-dark.png')
            ctx.close()
            continue

        print('== 1 dataset & initial render')
        meta = page.evaluate('''() => {
            const Q = document.querySelector('.k').__naming.Q;
            return {
              n: Q.length,
              cats: [...new Set(Q.map(q => q.cat))].sort(),
              chains: [...new Set(Q.map(q => q.chain))].sort()
            };
        }''')
        check('dataset has 34 items (≥ 30)', meta['n'] == 34, str(meta['n']))
        check('covers straight / branched / cyclic', meta['chains'] == ['branched', 'cyclic', 'straight'], str(meta['chains']))
        check('covers all 11 homologous series + cyclic', len(meta['cats']) == 12, str(meta['cats']))
        check('Mode 1 active initially', 'on' in page.get_attribute('.nm-modes button[data-mode="write"]', 'class'))

        print('== 2 Mode 1:看结构写名字 — tolerance, accept[], and step-specific diagnostics')
        # Empty input check
        page.fill('.nm-in', '   '); page.click('.nm-go'); page.wait_for_timeout(20)
        check('empty input prompts without scoring', '请先输入' in page.text_content('.nm-fb') and page.text_content('.nm-sc-n') == '0')

        # Wrong answer on #0 (2-methylpentane) + LO 13.3.1 quick self-check pills
        page.fill('.nm-in', '4-methylpentane'); page.keyboard.press('Enter'); page.wait_for_timeout(25)
        fb = page.text_content('.nm-fb')
        check('4-methylpentane rejected with Step ③ & right name',
              'bad' in page.get_attribute('.nm-fb', 'class') and '步骤 ③' in fb and '2-methylpentane' in fb, fb)
        check('score 0 / 1 after wrong attempt', page.text_content('.nm-sc-ok') == '0' and page.text_content('.nm-sc-n') == '1')
        page.click('.nm-cchips button[data-ch="straight"]'); page.wait_for_timeout(20)
        check('self-check wrong pill flags branched', '应为 branched' in page.text_content('.nm-cfb'))
        page.click('.nm-cchips button[data-ch="branched"]'); page.wait_for_timeout(20)
        check('self-check right pill confirms ✓ branched', '✓ branched' in page.text_content('.nm-cfb'))

        # Spec explicit requirement: reject 2-butene on but-2-ene with "IUPAC 写法是 but-2-ene"
        go_qi(q_idx('but-2-ene'))
        page.fill('.nm-in', '2-butene'); page.click('.nm-go'); page.wait_for_timeout(25)
        fb = page.text_content('.nm-fb')
        check('rejects 2-butene with "IUPAC 写法是 but-2-ene" & 步骤 ③',
              'bad' in page.get_attribute('.nm-fb', 'class') and 'IUPAC 写法是 but-2-ene' in fb and '步骤 ③' in fb, fb)

        # Case / whitespace / unicode en-dash tolerance on pent-1-ene
        go_qi(q_idx('pent-1-ene'))
        page.fill('.nm-in', '  PENT – 1 – ENE  '); page.click('.nm-go'); page.wait_for_timeout(25)
        fb = page.text_content('.nm-fb')
        check('accepts "  PENT – 1 – ENE  " with tolerance',
              'ok' in page.get_attribute('.nm-fb', 'class') and '✓ 正确' in fb, fb)
        check('score incremented to 1 / 3', page.text_content('.nm-sc-ok') == '1' and page.text_content('.nm-sc-n') == '3')

        # accept[] variants: butan-2-one, butan-1-amine, 2-methylprop-1-ene
        for qname, alt in [('butanone', 'butan-2-one'), ('butylamine', 'butan-1-amine'), ('2-methylpropene', '2-methylprop-1-ene')]:
            go_qi(q_idx(qname))
            page.fill('.nm-in', alt); page.click('.nm-go'); page.wait_for_timeout(20)
            check(f'accept[] variant {alt!r} accepted on {qname}', 'ok' in page.get_attribute('.nm-fb', 'class'), page.text_content('.nm-fb'))

        # Step ①, ②, ④ specific error diagnostics
        go_qi(q_idx('butanal'))
        page.fill('.nm-in', 'butanone'); page.click('.nm-go'); page.wait_for_timeout(20)
        check('wrong FG on butanal cites 步骤 ①', '步骤 ①' in page.text_content('.nm-fb'), page.text_content('.nm-fb'))

        go_qi(q_idx('butanenitrile'))
        page.fill('.nm-in', 'propanenitrile'); page.click('.nm-go'); page.wait_for_timeout(20)
        fb = page.text_content('.nm-fb')
        check('forgetting nitrile C cites 步骤 ② & –C≡N', '步骤 ②' in fb and '–C≡N' in fb, fb)

        go_qi(q_idx('2-bromo-3,3-dichlorohexane'))
        page.fill('.nm-in', '3,3-dichloro-2-bromohexane'); page.click('.nm-go'); page.wait_for_timeout(20)
        fb = page.text_content('.nm-fb')
        check('wrong alphabetical order cites 步骤 ④', '步骤 ④' in fb and '2-bromo-3,3-dichlorohexane' in fb, fb)

        # Open Step 4 walkthrough here and capture layout shot 1
        page.click('.nm-walk-toggle'); page.wait_for_timeout(25)
        check('walkthrough opens at Step 1 & built banner hidden',
              page.locator('.nm-steps li.cur').get_attribute('data-st') == '1' and not page.is_visible('.nm-built'))
        check('Step 1 highlights 3 halogen FG atoms', page.locator('.nm-stage circle.ko-hl').count() == 3)
        page.click('.nm-stepbtns button[data-st="2"]'); page.wait_for_timeout(25)
        check('Step 2 bolds 5 C–C bonds of hexane chain', page.locator('.nm-stage line.nm-chb').count() == 5)
        page.click('.nm-stnext'); page.wait_for_timeout(25)
        nums = page.eval_on_selector_all('.nm-stage text.ko-num', 'ts => ts.map(t => t.textContent)')
        check('Step 3 via 下一步 draws locants 1..6', nums == ['1', '2', '3', '4', '5', '6'], str(nums))
        page.click('.nm-steps li[data-st="4"]'); page.wait_for_timeout(25)
        check('Step 4 via list click reveals built name & disables 下一步',
              page.is_visible('.nm-built') and page.is_disabled('.nm-stnext') and '2-bromo-3,3-dichlorohexane' in page.text_content('.nm-built'))
        shot(page, '.k', OUT / 'card-write-light.png')

        # Ester right answer + Step 4 walkthrough shot + z2 close-up
        go_qi(q_idx('ethyl butanoate'))
        page.fill('.nm-in', 'ethyl butanoate'); page.click('.nm-go'); page.wait_for_timeout(25)
        check('ethyl butanoate exact match accepted', 'ok' in page.get_attribute('.nm-fb', 'class'))
        page.evaluate('document.querySelector(".k").__naming.setStep(4)'); page.wait_for_timeout(30)
        enums = page.eval_on_selector_all('.nm-stage text.ko-num', 'ts => ts.map(t => t.textContent)')
        check('ester Step 3/4 numbers acyl 1..4 + alkyl 1′..2′', enums == ['1', '2', '3', '4', '1′', '2′'], str(enums))
        shot(page, '.k', OUT / 'card-write-ok-light.png')
        shot(page, '.nm-stage-card', OUT / 'z2-step4-ester.png')

        print('== 3 LO 13.3.1 cyclic items (cyclohexane & methylcyclopentane)')
        go_qi(q_idx('cyclohexane'))
        qtag_before = page.text_content('.nm-qtag')
        check('cyclohexane hides name textbox & shows cyclic box',
              not page.is_visible('.nm-inwrap') and page.is_visible('.nm-cybox'))
        check('cyclohexane unanswered header does not spoil cyclic',
              'cyclic' not in qtag_before and 'cycloalkane' not in qtag_before, qtag_before)
        page.click('.nm-cybtns button[data-cy="cyclic"]'); page.wait_for_timeout(25)
        check('cyclohexane cyclic button accepted', 'ok' in page.get_attribute('.nm-fb', 'class'))
        check('cyclohexane header never duplicates cyclic · cyclic',
              'cyclic · cyclic' not in page.text_content('.nm-qtag'), page.text_content('.nm-qtag'))

        go_qi(q_idx('methylcyclopentane'))
        check('methylcyclopentane hides name textbox & shows cyclic box',
              not page.is_visible('.nm-inwrap') and page.is_visible('.nm-cybox'))
        page.click('.nm-cybtns button[data-cy="branched"]'); page.wait_for_timeout(25)
        fb = page.text_content('.nm-fb')
        check('methylcyclopentane clicking branched explains ring → cyclic',
              'bad' in page.get_attribute('.nm-fb', 'class') and 'cyclic' in fb and 'ring' in fb, fb)
        page.evaluate('document.querySelector(".k").__naming.setStep(4)'); page.wait_for_timeout(30)
        check('methylcyclopentane header never duplicates cyclic · cyclic',
              'cyclic · cyclic' not in page.text_content('.nm-qtag'), page.text_content('.nm-qtag'))
        shot(page, '.k', OUT / 'card-cyclic-light.png')

        print('== 4 IUPAC right-to-left C1 direction & z=2 stage close-ups')
        # Step 1 close-up on butanoic acid + verify C1 is at right-hand -COOH
        go_qi(q_idx('butanoic acid'))
        page.evaluate('document.querySelector(".k").__naming.setStep(1)'); page.wait_for_timeout(25)
        shot(page, '.nm-stage-card', OUT / 'z2-step1-fg.png')
        page.evaluate('document.querySelector(".k").__naming.setStep(3)'); page.wait_for_timeout(25)
        locs = page.evaluate('T.locants(".nm-stage svg")')
        check('butanoic acid C1 is at right-hand –COOH carbon (x1 > x4)', locs[0]['ax'] > locs[3]['ax'], str(locs))

        # Step 2 close-up on 3-ethyl-2-methylpentane
        go_qi(q_idx('3-ethyl-2-methylpentane'))
        page.evaluate('document.querySelector(".k").__naming.setStep(2)'); page.wait_for_timeout(25)
        shot(page, '.nm-stage-card', OUT / 'z2-step2-chain.png')

        # Step 3 close-up on dense branched 2,2,3-trimethylpentane
        go_qi(q_idx('2,2,3-trimethylpentane'))
        page.evaluate('document.querySelector(".k").__naming.setStep(3)'); page.wait_for_timeout(25)
        shot(page, '.nm-stage-card', OUT / 'z2-step3-branched.png')

        # Step 3 close-up on butanenitrile: C1 must be nitrile C at right end
        go_qi(q_idx('butanenitrile'))
        page.evaluate('document.querySelector(".k").__naming.setStep(3)'); page.wait_for_timeout(25)
        locs_cn = page.evaluate('T.locants(".nm-stage svg")')
        check('butanenitrile C1 is nitrile C (4 locants, x1 > x4)',
              len(locs_cn) == 4 and locs_cn[0]['ax'] > locs_cn[3]['ax'], str(locs_cn))
        shot(page, '.nm-stage-card', OUT / 'z2-step3-nitrile.png')

        # Also check butanal C1 is right-hand -CHO carbon
        go_qi(q_idx('butanal'))
        page.evaluate('document.querySelector(".k").__naming.setStep(3)'); page.wait_for_timeout(20)
        locs_al = page.evaluate('T.locants(".nm-stage svg")')
        check('butanal C1 is right-hand –CHO carbon (x1 > x4)', locs_al[0]['ax'] > locs_al[3]['ax'], str(locs_al))

        print('== 5 Sweep ALL 34 items at Step 4: zero [data-clash], inside viewBox, locant hugging')
        clash_items, out_items, loose_items, wrong_near = [], [], [], []
        for qi in range(34):
            go_qi(qi)
            page.evaluate('document.querySelector(".k").__naming.setStep(4)')
            c = page.eval_on_selector_all('[data-clash]', 'ts => ts.map(t => t.textContent + ":" + t.getAttribute("data-clash"))')
            if c:
                clash_items.append((qi, c))
            o = page.evaluate('T.outside()')
            if o:
                out_items.append((qi, o))
            ls = page.evaluate('T.locants(".nm-stage svg")')
            for m in ls:
                if m['own'] > 9.0:
                    loose_items.append((qi, m['txt'], round(m['own'], 2)))
                if m['dOwn'] >= m['dOther']:
                    wrong_near.append((qi, m['txt'], round(m['dOwn'], 2), round(m['dOther'], 2)))
        check('all 34 items Step 4: zero [data-clash]', not clash_items, str(clash_items))
        check('all 34 items Step 4: everything inside viewBox', not out_items, str(out_items))
        check('all 34 items Step 4: every C locant hugs its atom (≤ 9 units)', not loose_items, str(loose_items))
        check('all 34 items Step 4: every C locant nearest its own carbon', not wrong_near, str(wrong_near))

        print('== 6 Mode 2: 看名字选结构 + navigation controls')
        page.click('.nm-modes button[data-mode="pick"]'); page.wait_for_timeout(30)
        check('Mode 2 active & hides Mode 1 box',
              'on' in page.get_attribute('.nm-modes button[data-mode="pick"]', 'class') and page.is_visible('.nm-pbox') and not page.is_visible('.nm-wbox'))

        go_qi(q_idx('methyl propanoate'))
        check('Mode 2 renders 4 skeletal options with 1 right',
              page.locator('.nm-opt').count() == 4 and page.locator('.nm-opt[data-ok="1"]').count() == 1)
        page.locator('.nm-opt[data-ok="0"]').first.click(); page.wait_for_timeout(30)
        fb2 = page.text_content('.nm-fb')
        check('Mode 2 wrong choice marks .badv + .good & explains step',
              page.locator('.nm-opt.badv').count() == 1 and page.locator('.nm-opt.good').count() == 1 and '错在步骤' in fb2, fb2)
        shot(page, '.nm-opts', OUT / 'z2-opts-pick.png')
        page.click('.nm-walk-toggle3'); page.wait_for_timeout(30)
        page.click('.nm-stepbtns button[data-st="3"]'); page.wait_for_timeout(30)
        mp_nums = page.eval_on_selector_all('.nm-walk-stage text.ko-num', 'ts => ts.map(t => t.textContent)')
        check('Mode 2 walkthrough opens .nm-walk-fig with 0 clash',
              page.is_visible('.nm-walk-fig') and page.locator('[data-clash]').count() == 0)
        check('methyl propanoate Step 3 labels acyl 1..3 AND methyl 1′',
              mp_nums == ['1', '2', '3', '1′'], str(mp_nums))
        shot(page, '.k', OUT / 'card-pick-light.png')

        # Navigation: next, prev, category filter, jumper, random + right choice in Mode 2
        cur0 = page.evaluate('document.querySelector(".k").__naming.curQi()')
        page.click('.nm-next'); page.wait_for_timeout(20)
        cur1 = page.evaluate('document.querySelector(".k").__naming.curQi()')
        check('下一题 advances question', cur1 != cur0, f'{cur0} -> {cur1}')
        page.locator('.nm-opt[data-ok="1"]').click(); page.wait_for_timeout(25)
        check('Mode 2 right choice gives ✓ 正确 feedback', 'ok' in page.get_attribute('.nm-fb', 'class'))

        page.click('.nm-prev'); page.wait_for_timeout(20)
        check('上一题 returns to previous question', page.evaluate('document.querySelector(".k").__naming.curQi()') == cur0)

        page.select_option('.nm-cat', 'acid_ester'); page.wait_for_timeout(25)
        check('category filter acid_ester gives 7 items in jumper', page.locator('.nm-jmp option').count() == 7)
        page.select_option('.nm-jmp', '6'); page.wait_for_timeout(25)
        check('jumper selects 7th acid/ester item (hexyl hexanoate)', 'hexyl hexanoate' in page.text_content('.nm-pq'))
        before_rand = page.evaluate('document.querySelector(".k").__naming.curQi()')
        page.click('.nm-rand'); page.wait_for_timeout(25)
        check('随机 button switches to a different item', page.evaluate('document.querySelector(".k").__naming.curQi()') != before_rand)
        page.select_option('.nm-cat', 'all'); page.wait_for_timeout(25)

        # Sweep all 34 items in Mode 2 for viewBox bounds
        out_m2 = []
        for qi in range(34):
            go_qi(qi)
            o = page.evaluate('T.outside()')
            if o:
                out_m2.append((qi, o))
        check('all 34 items Mode 2 options: everything inside viewBox', not out_m2, str(out_m2))

        print('== 7 Narrow viewport (720 px)')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(200)

        # Check Mode 1 across all 34 items at Step 3 (with C1..Cn locants!) at 720 px
        page.click('.nm-modes button[data-mode="write"]'); page.wait_for_timeout(30)
        min_m1 = (999.0, -1, '')
        max_ov1 = 0
        for qi in range(34):
            go_qi(qi)
            page.evaluate('document.querySelector(".k").__naming.setStep(4)')
            ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
            max_ov1 = max(max_ov1, ov)
            mf = page.evaluate('T.minSvgFontPx()')
            if mf['px'] < min_m1[0]:
                min_m1 = (mf['px'], qi, mf['txt'])
        check('720 px Mode 1 (all 34 items Step 4): no horizontal overflow', max_ov1 <= 0, str(max_ov1))
        check('720 px Mode 1 (all 34 items Step 4): every SVG text ≥ 12 px', min_m1[0] >= 12.0, f'{min_m1[0]:.2f} px on q#{min_m1[1]} ({min_m1[2]})')

        go_qi(q_idx('hexyl hexanoate'))
        check('unanswered Mode 1 header hides skeleton & series',
              'ester' not in page.text_content('.nm-qtag') and 'straight-chained' not in page.text_content('.nm-qtag'),
              page.text_content('.nm-qtag'))
        page.evaluate('document.querySelector(".k").__naming.setStep(4)'); page.wait_for_timeout(30)
        check('unanswered Mode 1 with walkthrough still hides LO 13.3.1 skeleton answer',
              'straight-chained' not in page.text_content('.nm-qtag'), page.text_content('.nm-qtag'))
        check('jumper select has no narrow pixel max-width clipping',
              page.eval_on_selector('.nm-jmp', 'e => getComputedStyle(e).maxWidth') == '100%')
        shot(page, '.k', OUT / 'card-720-write.png')

        # Check Mode 2 across all 34 items at 720 px
        page.click('.nm-modes button[data-mode="pick"]'); page.wait_for_timeout(30)
        min_m2 = (999.0, -1, '')
        max_ov2 = 0
        for qi in range(34):
            go_qi(qi)
            ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
            max_ov2 = max(max_ov2, ov)
            mf = page.evaluate('T.minSvgFontPx()')
            if mf['px'] < min_m2[0]:
                min_m2 = (mf['px'], qi, mf['txt'])
        check('720 px Mode 2 (all 34 items): no horizontal overflow', max_ov2 <= 0, str(max_ov2))
        check('720 px Mode 2 (all 34 items): every SVG text ≥ 12 px', min_m2[0] >= 12.0, f'{min_m2[0]:.2f} px on q#{min_m2[1]} ({min_m2[2]})')

        go_qi(q_idx('but-2-ene'))
        alk_joined = page.evaluate('''() => {
            const svgs = [...document.querySelectorAll('.nm-opt-svg svg')];
            let seamless = 0;
            for (const s of svgs) {
              const atoms = JSON.parse(s.getAttribute('data-atoms'));
              const bonds = JSON.parse(s.getAttribute('data-bonds'));
              const lines = [...s.querySelectorAll('.cf-b line')];
              for (const [ia, ib, ord] of bonds) {
                if (ord !== 2) continue;
                const A = atoms[ia], B = atoms[ib];
                const hit = lines.some(l =>
                  Math.hypot(+l.getAttribute('x1') - A.x, +l.getAttribute('y1') - A.y) < 0.3 &&
                  Math.hypot(+l.getAttribute('x2') - B.x, +l.getAttribute('y2') - B.y) < 0.3
                );
                if (hit) seamless++;
              }
            }
            return seamless;
        }''')
        check('skeletal alkene C=C options align primary line seamlessly on C vertices', alk_joined >= 3, str(alk_joined))
        shot(page, '.k', OUT / 'card-720-pick.png')
        shot(page, '.nm-opts', OUT / 'z2-opts-alkene.png')
        go_qi(q_idx('hexyl hexanoate'))
        shot(page, '.k', OUT / 'card-720-pick-wide.png')

        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
