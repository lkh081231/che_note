"""ch01 interaction test: python playwright driving the system chromium over the preview pages.

usage: uv run --with playwright python -I colab/tests/ch01_interact.py $COLAB_TMP/ch01-atomic-structure <shots-dir>
(run tools/check_colab.py ch01 first to write the preview pages)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright

D = Path(sys.argv[1])            # preview dir
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


def canvas_stats(page):
    return page.evaluate("""() => { const c=document.querySelector('.stage canvas'); if(!c) return null;
      const g=document.createElement('canvas'); g.width=c.width; g.height=c.height; const x=g.getContext('2d'); x.drawImage(c,0,0);
      const d=x.getImageData(0,0,g.width,g.height).data; let s=0,s2=0,n=0;
      for(let i=0;i<d.length;i+=16){const v=d[i]+d[i+1]+d[i+2]; s+=v; s2+=v*v; n++;}
      const m=s/n; return {mean:m, std:Math.sqrt(s2/n-m*m), url:c.toDataURL().length, hash:c.toDataURL().slice(-200)}; }""")


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True,
                          args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    ctx = b.new_context(viewport={'width': 1000, 'height': 900}, device_scale_factor=1.5)
    page = ctx.new_page()
    page.on('console', lambda m: errors.append(f'{page.url[-40:]}: {m.text}') if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append(f'{page.url[-40:]}: PAGEERROR {e}'))

    def go(cid):
        page.goto((D / f'cell-{cid}.html').as_uri()); page.wait_for_timeout(600)

    def shot(name):
        page.locator('.k').first.screenshot(path=str(OUT / f'{name}.png'))

    def clashes():
        return page.locator('[data-clash]').count()

    print('== 03 atom model'); go('ch01-03'); shot('03-schem')
    page.click('text=按真实比例'); check('real mode shows .am-real', page.is_visible('.am-real'))
    check('note changes', '18 000' in page.inner_text('.am-note')); shot('03-real')

    print('== 05 p/n/e'); go('ch01-05')
    page.select_option('.pz', '26'); page.fill('.pa', '56'); page.dispatch_event('.pa', 'input'); page.select_option('.pq', '3')
    t = page.inner_text('.pout'); check('Fe-56 3+ → n 30, e 23', '= 30' in t and '= 23' in t, t)
    fills = page.locator('.pquiz input.fill')
    check('quiz has 30 inputs', fills.count() == 30, str(fills.count()))
    fills.nth(0).fill('12'); fills.nth(0).dispatch_event('input')
    fills.nth(1).fill('13'); fills.nth(1).dispatch_event('input')
    check('right answer turns good', 'good' in fills.nth(0).get_attribute('class'))
    check('wrong answer turns badv', 'badv' in fills.nth(1).get_attribute('class'))
    page.fill('.pa', '20'); page.dispatch_event('.pa', 'input')
    check('A < Z shows error', 'A 不能小于 Z' in page.inner_text('.pout')); page.fill('.pa', '56'); page.dispatch_event('.pa', 'input'); shot('05')

    print('== 07 beams'); go('ch01-07'); shot('07-schem')
    check('3 beams', page.locator('.bm-paths path').count() == 3)
    page.uncheck('.be'); check('2 beams after unticking electron', page.locator('.bm-paths path').count() == 2); page.check('.be')
    check('beams: no label clash (schematic)', clashes() == 0, str(clashes()))
    page.click('text=按真实比例'); check('electron hits plate in real mode', 'hits the plate' in page.text_content('.bm-paths')); shot('07-real')
    check('beams: no label clash (real)', clashes() == 0, str(clashes()))
    page.fill('.bv', '3'); page.dispatch_event('.bv', 'input'); shot('07-real-v3')
    gap = page.evaluate('''() => { const ps=[...document.querySelectorAll('.bm-paths path')]; const n=ps.find(p=>p.getAttribute('marker-end')==='url(#bm-n)'), pr=ps.find(p=>p.getAttribute('marker-end')==='url(#bm-p)');
      const L=n.getTotalLength(), tip=n.getPointAtLength(L); let best=1e9; const M=pr.getTotalLength();
      for(let s=0;s<=M;s+=1){const q=pr.getPointAtLength(s); if(Math.abs(q.x-tip.x)<1) best=Math.min(best,Math.abs(q.y-tip.y));} return best; }''')
    # gap is measured from the arrow TIP line; the arrowhead reaches ~9 px below it, so 17 px = 8 px of real clearance
    check('real, min voltage: proton line clears neutron arrowhead (tip gap > 17 px)', gap > 17, str(gap))
    # moving particles: sample ~3 s of animation; visible dots must never sit on each other
    near = 1e9
    for _ in range(15):
        d = page.evaluate('''() => { const ds=[...document.querySelectorAll('.bm-dots g')].filter(g=>g.style.opacity!=='0').map(g=>{const b=g.getBoundingClientRect(); return [b.x+b.width/2,b.y+b.height/2];});
          let m=1e9; for(let i=0;i<ds.length;i++) for(let j=i+1;j<ds.length;j++) m=Math.min(m,Math.hypot(ds[i][0]-ds[j][0],ds[i][1]-ds[j][1])); return m; }''')
        near = min(near, d); page.wait_for_timeout(200)
    check('real, min voltage: moving particles never overlap (> 18 px apart)', near > 18, str(near))
    page.fill('.bv', '10'); page.dispatch_event('.bv', 'input'); check('beams: no clash at max voltage', clashes() == 0, str(clashes()))
    page.click('text=示意（不按比例）'); check('beams: no clash schematic max voltage', clashes() == 0, str(clashes())); shot('07-schem-v10')

    print('== 09 radius'); go('ch01-09'); shot('09-p3')
    for tab in ['Period 2', 'Group 2', 'Group 17']:
        page.click(f'.rbtn button:text-is("{tab}")'); page.wait_for_timeout(150)
        check(f'{tab} draws points', page.locator('.rc circle').count() >= 8)
    page.click('.rbtn button:text-is("Group 2")'); shot('09-g2')
    for tab in ['Period 3', 'Period 2', 'Group 2', 'Group 17']:
        page.click(f'.rbtn button:text-is("{tab}")'); page.wait_for_timeout(100)
        check(f'radius {tab}: no label clash', clashes() == 0, str(clashes()))
    page.click('.rbtn button:text-is("Period 3")'); shot('09-p3')
    page.hover('.rc circle.io-pt >> nth=2'); page.wait_for_timeout(150)
    check('tooltip on hover', 'Al³⁺' in page.inner_text('.tip'), page.inner_text('.tip'))

    print('== 11 isotopes'); go('ch01-11')
    page.click('.ibtn button:text-is("hydrogen")'); check('hydrogen → 3 cards', page.locator('.icards .card').count() == 3); shot('11')

    for cid, name in [('ch01-13', 'orbitals'), ('ch01-14', 'cloud')]:
        print(f'== {cid} 3D {name}'); go(cid)
        page.wait_for_selector('.k[data-3d]', timeout=20000); page.wait_for_timeout(800)
        check(f'{name}: 3D ready', page.get_attribute('.k', 'data-3d') == 'ready', page.get_attribute('.k', 'data-3d'))
        s1 = canvas_stats(page)
        check(f'{name}: canvas not blank', s1 and s1['std'] > 8, json.dumps(s1 and {k: s1[k] for k in ('mean', 'std')}))
        shot(f'{cid[-2:]}-{name}-a')
        box = page.locator('.stage canvas').bounding_box()
        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2); page.mouse.down()
        page.mouse.move(box['x'] + box['width'] / 2 + 160, box['y'] + box['height'] / 2 + 60, steps=8); page.mouse.up()
        page.wait_for_timeout(200)
        s2 = canvas_stats(page)
        check(f'{name}: drag changes the view', s2['hash'] != s1['hash'])
        shot(f'{cid[-2:]}-{name}-b')
    go('ch01-13'); page.wait_for_selector('.k[data-3d=ready]', timeout=20000)
    for o, nm in [('p3', 'p3'), ('d5', 'd5'), ('s', 's')]:
        page.click(f'[data-o={o}]'); page.wait_for_timeout(300); shot(f'13-orb-{nm}')
    check('caption updates', 'spherical' in page.inner_text('.ocap'))
    go('ch01-14'); page.wait_for_selector('.k[data-3d=ready]', timeout=20000)
    page.click('[data-c="3s"]'); page.wait_for_timeout(500); shot('14-cloud-3s')
    check('3s caption', '2 个 node' in page.inner_text('.ccap'))
    page.click('[data-c="1s"]'); page.wait_for_timeout(400); shot('14-cloud-1s')
    check('size readout follows the orbital', '1s' in page.inner_text('.csize') and '自动缩放' in page.inner_text('.csize'), page.inner_text('.csize'))
    page.check('.csame'); page.wait_for_timeout(400); shot('14-cloud-1s-same')
    check('same-scale toggle', '同一比例' in page.inner_text('.csize'))
    page.click('[data-c="3s"]'); page.wait_for_timeout(400); shot('14-cloud-3s-same'); page.uncheck('.csame')
    page.uncheck('.ccut'); page.wait_for_timeout(400); shot('14-cloud-3s-whole'); page.check('.ccut')

    print('== 16 config filler'); go('ch01-16'); shot('16-fe')
    page.select_option('.fz', '24'); t = page.inner_text('.fout'); check('Cr → [Ar]3d⁵4s¹ + exception note', '[Ar]3d⁵4s¹' in t and '例外' in t, t)
    page.select_option('.fz', '26'); page.select_option('.fq', '3'); t = page.inner_text('.fout')
    check('Fe³⁺ → [Ar]3d⁵, 4s lost first note', '[Ar]3d⁵' in t and '4s electrons are lost first' in t, t); shot('16-fe3')
    check('faded arrows for lost electrons', page.locator('.fl text.gone').count() == 3, str(page.locator('.fl text.gone').count()))
    page.select_option('.fz', '8'); page.select_option('.fq', '0')
    for _ in range(6): page.click('.fstep')
    t = page.inner_text('.fout'); check('stepping: 6 of 8, just filled 2p', '已填 6' in t and '2p' in t, t); shot('16-step')
    inp = page.locator('.fquiz input')
    inp.nth(0).fill('[Ar]3d6 4s2'); inp.nth(0).dispatch_event('input')
    inp.nth(1).fill('1s2 2s2 2p6 3s2 3p6 3d6'); inp.nth(1).dispatch_event('input')
    inp.nth(4).fill('[Ar]3d10'); inp.nth(4).dispatch_event('input')
    res = page.locator('.fquiz .res')
    check('Fe right ✓', res.nth(0).inner_text() == '✓'); check('Fe³⁺ wrong ✗', res.nth(1).inner_text() == '✗'); check('Cu⁺ right ✓', res.nth(4).inner_text() == '✓')

    print('== 19 IE1'); go('ch01-19'); shot('19-across')
    btns = page.locator('.ibtn button')
    for k in range(btns.count()):
        btns.nth(k).click(); page.wait_for_timeout(100)
        check(f'story {k} highlights points', page.locator('.ie circle.hl').count() >= 4)
    btns.nth(2).click(); shot('19-NO'); check('N→O text mentions spin-pair', 'spin-pair' in page.inner_text('.itext'))

    print('== 21 successive IE'); go('ch01-21'); shot('21-na')
    page.select_option('.sz', '20'); page.select_option('.sn', '3')
    check('Ca 3rd IE equation', 'Ca²⁺(g) → Ca³⁺(g) + e⁻' in page.inner_text('.seq'), page.inner_text('.seq'))
    page.click('button[data-tab=si]'); page.wait_for_timeout(150); check('Si pane shows 14 bars', page.locator('.sv-si rect.s3, .sv-si rect.s2, .sv-si rect.s1').count() >= 14); shot('21-si')
    page.click('button[data-tab=quiz]'); page.wait_for_timeout(150)
    ans = page.get_attribute('.mcq', 'data-ans'); page.click(f'.mcq button[data-v="{ans}"]')
    check('quiz: right answer marked good', 'good' in page.get_attribute(f'.mcq button[data-v="{ans}"]', 'class'))
    check('quiz: explanation shown', page.is_visible('.mcq .why')); shot('21-quiz')
    page.click('.qnext'); page.wait_for_timeout(100)
    ans2 = page.get_attribute('.mcq', 'data-ans'); wrong = [v for v in ['1', '2', '13', '14+'] if v != ans2][0]
    page.click(f'.mcq button[data-v="{wrong}"]'); check('quiz: wrong answer marked badv', 'badv' in page.get_attribute(f'.mcq button[data-v="{wrong}"]', 'class'))
    page.click('button[data-tab=na]'); page.uncheck('[data-pane=na] .lg'); page.wait_for_timeout(100); shot('21-na-linear')

    print('== practice cells')
    for n in range(24, 36):
        cid = f'ch01-{n}'; go(cid)
        rv = page.locator('button.reveal')
        for k in range(rv.count()): rv.nth(k).click()
        check(f'{cid}: all answers open', page.locator('.ans.show').count() == rv.count(), f'{page.locator(".ans.show").count()}/{rv.count()}')
        fl = page.locator('input.fill')
        for k in range(fl.count()):
            a = fl.nth(k).get_attribute('data-ans').split('|')[0]; fl.nth(k).fill(a); fl.nth(k).dispatch_event('input')
        if fl.count():
            check(f'{cid}: {fl.count()} fills accept their answers', page.locator('input.fill.good').count() == fl.count())
        shot(f'{n}-practice')

    print('== 36 checklist'); go('ch01-36')
    boxes = page.locator('.lolist input[data-id]'); check('28 LOs', boxes.count() == 28, str(boxes.count()))
    for k in range(3): boxes.nth(k).check()
    check('count 3 / 28', '3 / 28' in page.inner_text('.count'))
    page.reload(); page.wait_for_timeout(400)
    check('ticks persist after reload (localStorage)', '3 / 28' in page.inner_text('.count'), page.inner_text('.count')); shot('36-checklist')
    for k in range(3): boxes.nth(k).uncheck()

    print('== offline 3D fallback')
    ctx2 = b.new_context(viewport={'width': 1000, 'height': 900}, device_scale_factor=1.5)
    ctx2.route('**/cdn.jsdelivr.net/**', lambda r: r.abort())
    pg2 = ctx2.new_page(); pg2.goto((D / 'cell-ch01-13.html').as_uri()); pg2.wait_for_timeout(2500)
    check('CDN blocked → fallback shown', pg2.get_attribute('.k', 'data-3d') == 'fallback' and pg2.is_visible('.fallback'))
    pg2.locator('.k').first.screenshot(path=str(OUT / '13-offline.png')); ctx2.close()

    print('== dark mode')
    ctx3 = b.new_context(viewport={'width': 1000, 'height': 900}, device_scale_factor=1.5, color_scheme='dark')
    pg3 = ctx3.new_page()
    for cid in ['ch01-07', 'ch01-16', 'ch01-19', 'ch01-13']:
        pg3.goto((D / f'cell-{cid}.html').as_uri()); pg3.wait_for_timeout(2500 if cid == 'ch01-13' else 600)
        pg3.locator('.k').first.screenshot(path=str(OUT / f'dark-{cid[-2:]}.png'))
    ctx3.close(); b.close()

print('== console errors:', len(errors))
for e in errors: print('  ', e)
bad = [r for r in results if not r[1]]
print(f'== {len(results) - len(bad)}/{len(results)} checks passed')
