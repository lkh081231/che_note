"""ch02 ar-spectrum cell test: mass spectrum → A_r.

usage: uv run --with playwright python -I colab/tests/ch02_ar-spectrum.py <preview.html> <shots-dir>
(python tools/build_colab.py ch02 --cell ar-spectrum writes the preview page)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []

PRESETS = {'boron': '10.8', 'neon': '20.2', 'chlorine': '35.5', 'lead': '207.2', 'iridium': '192.35', 'magnesium': '24.3'}


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


GEOM = """(sel) => { const s=document.querySelector(sel); const [x,y,w,h]=s.getAttribute('data-plot').split(',').map(Number);
  const top=+s.getAttribute('data-ytop'); const y0=y+h;
  const bars=[...s.querySelectorAll('rect.ars-bar')].map(r=>({v:+r.dataset.v, m:+r.dataset.m, h:+r.getAttribute('height'),
     cx:+r.getAttribute('x') + +r.getAttribute('width')/2, want:(+r.dataset.v)/top*h}));
  const ln=s.querySelector('line.ars-arl');
  const lo=Math.min(...bars.map(b=>b.m))-1, hi=Math.max(...bars.map(b=>b.m))+1;
  const X=m=>x+(m-lo)/(hi-lo)*w;
  return {bars, ar: ln? +ln.dataset.ar : null, lx: ln? +ln.getAttribute('x1') : null, ax: ln? X(+ln.dataset.ar) : null,
    abLabels:[...s.querySelectorAll('text.ars-ab')].map(t=>t.textContent),
    arText: (s.querySelector('text.ars-ar')||{}).textContent || ''}; }"""


def overlaps(page, sel):
    """pairs of overlapping text boxes inside one svg (screen space) — K.label should never allow it"""
    return page.evaluate("""(sel) => { const ts=[...document.querySelectorAll(sel+' text')].map(t=>t.getBoundingClientRect());
      let n=0; for(let i=0;i<ts.length;i++) for(let j=i+1;j<ts.length;j++){const a=ts[i],b=ts[j];
        if(a.width&&b.width&&a.x<b.x+b.width-0.5&&b.x<a.x+a.width-0.5&&a.y<b.y+b.height-0.5&&b.y<a.y+a.height-0.5) n++;}
      return n; }""", sel)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True)
    ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=1.5)
    page = ctx.new_page()
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
    page.goto(PAGE.as_uri()); page.wait_for_timeout(500)

    def clashes():
        return page.locator('[data-clash]').count()

    def res():
        return page.inner_text('.ars-res')

    def work():
        return page.inner_text('.ars-work')

    print('== default boron')
    check('boron working shows Σ abundance denominator', work() == 'Aᵣ = (10 × 23 + 11 × 100) ÷ (23 + 100)', work())
    check('boron result 10.8', res() == '10.8', res())
    check('boron intermediate 1330 ÷ 123', '1330 ÷ 123' in page.inner_text('.ars-out'), page.inner_text('.ars-out'))
    page.locator('.k').first.screenshot(path=str(OUT / 'card-boron.png'))

    print('== every preset')
    for i, (name, want) in enumerate(PRESETS.items()):
        page.select_option('.ars-pre', str(i)); page.wait_for_timeout(80)
        g = page.evaluate(GEOM, '.ars-svg')
        check(f'{name}: result {want}', res() == want, res())
        check(f'{name}: bar heights match abundances', all(abs(x['h'] - x['want']) < 0.6 for x in g['bars']),
              str([(x['v'], round(x['h'], 1), round(x['want'], 1)) for x in g['bars']]))
        check(f'{name}: A_r line at the right x', g['lx'] is not None and abs(g['lx'] - g['ax']) < 0.5, f"{g['lx']} vs {g['ax']}")
        check(f'{name}: A_r label on chart says {want}', g['arText'] == f'Aᵣ = {want}', g['arText'])
        check(f'{name}: every bar has its abundance label', len(g['abLabels']) == len(g['bars']), str(g['abLabels']))
        check(f'{name}: no data-clash', clashes() == 0, str(clashes()))
        check(f'{name}: no overlapping text', overlaps(page, '.ars-svg') == 0, str(overlaps(page, '.ars-svg')))
        if name in ('neon', 'iridium', 'lead'):
            page.locator('.k').first.screenshot(path=str(OUT / f'card-{name}.png'))

    print('== neon: the 0.3 bar')
    page.select_option('.ars-pre', '1'); page.wait_for_timeout(80)
    lab = page.locator('.ars-svg text.ars-ab[data-i="1"]')
    check('neon 0.3 label exists and is visible', lab.text_content() == '0.3' and lab.is_visible())
    bb = lab.bounding_box()
    check('neon 0.3 label sits just above the axis (near its bar)', bb is not None and bb['height'] > 10, str(bb))
    check('neon working', work() == 'Aᵣ = (20 × 90.9 + 21 × 0.3 + 22 × 8.8) ÷ (90.9 + 0.3 + 8.8)', work())
    svgbox = page.locator('.ars-svg').bounding_box()
    page.screenshot(path=str(OUT / 'zoom-neon.png'), clip={'x': svgbox['x'], 'y': svgbox['y'], 'width': svgbox['width'], 'height': svgbox['height']})

    print('== iridium 2 d.p.')
    page.select_option('.ars-pre', '4'); page.wait_for_timeout(80)
    check('iridium working', work() == 'Aᵣ = (190.96 × 15.18 + 192.96 × 34.82) ÷ (15.18 + 34.82)', work())
    check('iridium 9617.64 ÷ 50.00 (data d.p. kept)', '9617.64 ÷ 50.00 =' in page.inner_text('.ars-out'), page.inner_text('.ars-out'))

    print('== type a new abundance')
    page.select_option('.ars-pre', '0'); page.wait_for_timeout(80)
    before = page.evaluate(GEOM, '.ars-svg')
    page.fill('.ars-ab-in[data-i="1"]', '50'); page.dispatch_event('.ars-ab-in[data-i="1"]', 'input'); page.wait_for_timeout(80)
    after = page.evaluate(GEOM, '.ars-svg')
    check('input → working updates', work() == 'Aᵣ = (10 × 23 + 11 × 50) ÷ (23 + 50)', work())
    check('input → result 10.7', res() == '10.7', res())
    check('input → bar redrawn to 50', abs(after['bars'][1]['v'] - 50) < 1e-9 and abs(after['bars'][1]['h'] - after['bars'][1]['want']) < 0.6)
    check('input → A_r line moves left', after['lx'] < before['lx'] - 5, f"{before['lx']} → {after['lx']}")
    check('input → chart label 10.7', after['arText'] == 'Aᵣ = 10.7', after['arText'])
    page.fill('.ars-ab-in[data-i="1"]', '300'); page.dispatch_event('.ars-ab-in[data-i="1"]', 'input'); page.wait_for_timeout(80)
    g = page.evaluate(GEOM, '.ars-svg')
    check('value above the axis top rescales the axis (bar still fits)', g['bars'][1]['h'] <= page.evaluate(
        "+document.querySelector('.ars-svg').getAttribute('data-plot').split(',')[3]") + 0.1 and abs(g['bars'][1]['h'] - g['bars'][1]['want']) < 0.6)
    check('big value: no clash', clashes() == 0 and overlaps(page, '.ars-svg') == 0)
    page.fill('.ars-ab-in[data-i="0"]', '0'); page.dispatch_event('.ars-ab-in[data-i="0"]', 'input')
    page.fill('.ars-ab-in[data-i="1"]', '0'); page.dispatch_event('.ars-ab-in[data-i="1"]', 'input'); page.wait_for_timeout(80)
    check('all zero → error message, no NaN', 'Σ abundance = 0' in page.inner_text('.ars-out') and 'NaN' not in page.inner_text('.k'))

    print('== drag a bar top')
    page.select_option('.ars-pre', '0'); page.wait_for_timeout(80)
    before = page.evaluate(GEOM, '.ars-svg')
    knob = page.locator('.ars-knob[data-i="0"]').bounding_box()
    cx, cy = knob['x'] + knob['width'] / 2, knob['y'] + knob['height'] / 2
    page.mouse.move(cx, cy); page.mouse.down()
    page.mouse.move(cx, cy - 120, steps=10); page.wait_for_timeout(50)
    page.screenshot(path=str(OUT / 'zoom-dragging.png'), clip={'x': svgbox['x'], 'y': svgbox['y'], 'width': svgbox['width'], 'height': svgbox['height']})
    page.mouse.up(); page.wait_for_timeout(80)
    after = page.evaluate(GEOM, '.ars-svg')
    v = after['bars'][0]['v']
    inp = page.input_value('.ars-ab-in[data-i="0"]')
    check('drag raised ¹⁰B abundance', v > 23 + 20, str(v))
    check('drag: number input follows', inp == str(int(v)), f'{inp} vs {v}')
    check('drag: bar height matches new value', abs(after['bars'][0]['h'] - after['bars'][0]['want']) < 0.6)
    check('drag: working follows', work() == f'Aᵣ = (10 × {int(v)} + 11 × 100) ÷ ({int(v)} + 100)', work())
    want = f'{(10 * v + 1100) / (v + 100):.1f}'
    check('drag: result recomputed', res() == want, f'{res()} vs {want}')
    check('drag: A_r line moved toward ¹⁰B', after['lx'] < before['lx'] - 5, f"{before['lx']} → {after['lx']}")
    check('drag: no clash', clashes() == 0 and overlaps(page, '.ars-svg') == 0)
    # drag far below the axis clamps at 0
    knob = page.locator('.ars-knob[data-i="0"]').bounding_box()
    page.mouse.move(knob['x'] + 7, knob['y'] + 7); page.mouse.down(); page.mouse.move(knob['x'] + 7, knob['y'] + 600, steps=6); page.mouse.up()
    check('drag below axis clamps to 0', page.input_value('.ars-ab-in[data-i="0"]') == '0' and res() == '11.0', f"{page.input_value('.ars-ab-in[data-i=\"0\"]')} {res()}")
    # iridium drags in 0.01 steps
    page.select_option('.ars-pre', '4'); page.wait_for_timeout(80)
    knob = page.locator('.ars-knob[data-i="1"]').bounding_box()
    page.mouse.move(knob['x'] + 7, knob['y'] + 7); page.mouse.down(); page.mouse.move(knob['x'] + 7, knob['y'] + 47, steps=5); page.mouse.up()
    iv = page.input_value('.ars-ab-in[data-i="1"]')
    check('iridium drag keeps 2 d.p. input', len(iv.split('.')[-1]) == 2 and float(iv) < 34.82, iv)

    print('== self-test')
    for k in range(4):
        ans = float(page.get_attribute('.ars-qsvg', 'data-ans'))
        bars = page.evaluate("[...document.querySelectorAll('.ars-qsvg rect.ars-bar')].map(r=>[+r.dataset.m,+r.dataset.v])")
        mine = sum(m * a for m, a in bars) / sum(a for _, a in bars)
        check(f'q{k}: 2–3 peaks, answer matches the drawn spectrum', 2 <= len(bars) <= 3 and abs(mine - ans) < 1e-9, str(bars))
        check(f'q{k}: no clash / overlap', clashes() == 0 and overlaps(page, '.ars-qsvg') == 0)
        gaps = page.evaluate("[...document.querySelectorAll('.ars-qsvg rect.ars-bar')].map((r,i)=>r.getBoundingClientRect().top - document.querySelectorAll('.ars-qsvg text.ars-ab')[i].getBoundingClientRect().bottom)")
        check(f'q{k}: abundance labels sit right on their bar tops', all(-1 <= d <= 8 for d in gaps), str(gaps))
        page.fill('.ars-qin', f'{ans:.1f}'); page.dispatch_event('.ars-qin', 'input')
        check(f'q{k}: right answer (1 d.p.) turns green', 'good' in page.get_attribute('.ars-qin', 'class'), page.input_value('.ars-qin'))
        page.fill('.ars-qin', f'{ans + 0.3:.1f}'); page.dispatch_event('.ars-qin', 'input')
        check(f'q{k}: answer off by 0.3 turns red', 'badv' in page.get_attribute('.ars-qin', 'class'))
        page.fill('.ars-qin', f'{ans + 0.04:.3f}'); page.dispatch_event('.ars-qin', 'input')
        check(f'q{k}: within ±0.05 accepted', 'good' in page.get_attribute('.ars-qin', 'class'))
        if k == 0:
            page.fill('.ars-qin', f'{ans:.1f}'); page.dispatch_event('.ars-qin', 'input')
            page.click('button.reveal'); check('reveal shows working', page.is_visible('.ars-qans') and '÷' in page.inner_text('.ars-qans'))
            qb = page.locator('.ars-qsvg').bounding_box()
            page.screenshot(path=str(OUT / 'zoom-quiz.png'), clip={'x': qb['x'], 'y': qb['y'], 'width': qb['width'], 'height': qb['height'] + 170})
        old = page.get_attribute('.ars-qsvg', 'data-ans')
        page.click('.ars-qnew'); page.wait_for_timeout(50)
        check(f'q{k}: new question resets input and hides answer', page.input_value('.ars-qin') == '' and not page.is_visible('.ars-qans'))
    page.select_option('.ars-pre', '0'); page.wait_for_timeout(80)
    page.locator('.k').first.screenshot(path=str(OUT / 'card-full.png'))

    print('== narrow (700 px) + dark')
    page.set_viewport_size({'width': 720, 'height': 1100}); page.wait_for_timeout(150)
    ov = page.evaluate("(() => { const k=document.querySelector('.k'); return k.scrollWidth - k.clientWidth; })()")
    check('700 px: no horizontal overflow', ov <= 0, str(ov))
    page.locator('.k').first.screenshot(path=str(OUT / 'card-700.png'))
    sc = page.evaluate("Math.min(...[...document.querySelectorAll('.ars-svg,.ars-qsvg')].map(s=>s.getBoundingClientRect().width / +s.getAttribute('viewBox').split(' ')[2]))")
    check('700 px: charts drawn 1:1, so 13 px tick labels stay ≥ 12 px', sc >= 0.99, str(sc))
    check('700 px: no clash after resize', clashes() == 0 and overlaps(page, '.ars-svg') == 0 and overlaps(page, '.ars-qsvg') == 0)
    ctx2 = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=1.5, color_scheme='dark')
    pg2 = ctx2.new_page(); pg2.on('pageerror', lambda e: errors.append(f'dark PAGEERROR {e}'))
    pg2.goto(PAGE.as_uri()); pg2.wait_for_timeout(400); pg2.select_option('.ars-pre', '1'); pg2.wait_for_timeout(80)
    pg2.locator('.k').first.screenshot(path=str(OUT / 'card-dark-neon.png'))
    ctx2.close(); b.close()

check('no console errors', not errors, '; '.join(errors))
bad = [r for r in results if not r[1]]
print(f'== {len(results) - len(bad)}/{len(results)} passed')
sys.exit(1 if bad else 0)
