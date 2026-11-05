"""ch03 metallic cell test: lattice of positive metal ions + sea of delocalised electrons (rAF animation),
metal picker (across Period 3 / down Group 1), power switch (drift to + terminal), pause.

usage: uv run --with playwright python -I colab/tests/ch03_metallic.py <preview.html> <shots-dir>
(build the preview first: COLAB_TMP=/mnt/ai-shared/che_tmp/ch03 python3 tools/build_colab.py ch03 --cell metallic)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []

METALS = {  # metal: (ion, charge, m.p. / °C)
    'Na': ('Na⁺', 1, 98), 'Mg': ('Mg²⁺', 2, 650), 'Al': ('Al³⁺', 3, 660),
    'Li': ('Li⁺', 1, 181), 'K': ('K⁺', 1, 63),
}
SERIES = {'p3': ['Na', 'Mg', 'Al'], 'g1': ['Li', 'Na', 'K']}


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
    if (own && parseFloat(st.fontSize) < 12 - 1e-3)
      out.push(e.tagName + '.' + e.className + ':' + parseFloat(st.fontSize) + 'px:' + e.textContent.trim().slice(0, 20));
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

# every svg text vs every other text, vs ion circles, vs leader lines / block edges (rendered boxes)
AUDIT_JS = """() => {
  const svg = document.querySelector('.mt-fig');
  const R = e => e.getBoundingClientRect();
  const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
  const labs = [...svg.querySelectorAll('text')].filter(t => !t.classList.contains('mt-chg'));
  const out = [];
  for (let i = 0; i < labs.length; i++) for (let j = i + 1; j < labs.length; j++)
    if (hit(R(labs[i]), R(labs[j]))) out.push(labs[i].textContent + ' <-> ' + labs[j].textContent);
  const block = R(svg.querySelector('.mt-block'));
  for (const t of labs) {
    if (hit(R(t), block)) out.push('inside lattice: ' + t.textContent);
    for (const c of svg.querySelectorAll('.mt-ion-c')) if (hit(R(t), R(c))) out.push('on ion: ' + t.textContent);
  }
  /* charge text sits inside its own circle */
  const chg = [...svg.querySelectorAll('text.mt-chg')], circ = [...svg.querySelectorAll('.mt-ion-c')];
  chg.forEach((t, i) => { const a = R(t), c = R(circ[i]);
    if (a.left < c.left || a.right > c.right || a.top < c.top - 1 || a.bottom > c.bottom + 1) out.push('charge outside circle ' + i + ' ' + t.textContent); });
  return out;
}"""

ELX_JS = """() => [...document.querySelectorAll('.mt-e')].map(g => {
  const m = g.getAttribute('transform').match(/translate\\(([-\\d.]+),([-\\d.]+)\\)/); return [+m[1], +m[2]]; })"""


def frames(page, n=6, gap=120):
    out = []
    for _ in range(n):
        out.append(page.evaluate(ELX_JS)); page.wait_for_timeout(gap)
    return out


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(500)
        sfx = '' if scheme == 'light' else '-dark'
        st = lambda: page.evaluate('() => document.querySelector(".k").__mt.stats()')  # noqa: E731

        def shot(name, sel='.k'):
            page.evaluate('() => document.querySelector(".k").__mt.setPaused(true)'); page.wait_for_timeout(60)
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        def resume():
            page.evaluate('() => document.querySelector(".k").__mt.setPaused(false)')

        def pick(series, metal):
            page.click(f'.mt-ser button[data-series="{series}"][data-metal="{metal}"]'); page.wait_for_timeout(80)

        if scheme == 'light':
            print('== static content')
            d = page.inner_text('.mt-def')
            check('definition verbatim', 'metallic bonding：the electrostatic attraction between positive metal ions and delocalised electrons' in d, d)
            labs = page.evaluate("[...document.querySelectorAll('.mt-fig text.mt-lab')].map(t => t.textContent)")
            check('both MS labels present', labs == ['positive metal ions — regular arrangement', '(sea of) delocalised electrons'], str(labs))
            check('two leader lines', page.locator('.mt-lead').count() == 2)
            lead = page.evaluate("""() => { const s = document.querySelector('.mt-fig'), k = document.querySelector('.k').__mt;
              const l = [...s.querySelectorAll('.mt-lead')].map(e => ['x1','y1','x2','y2'].map(a => +e.getAttribute(a)));
              const c = s.querySelectorAll('.mt-ion-c')[1];
              return { l, cx: +c.getAttribute('cx'), cy: +c.getAttribute('cy'), r: +c.getAttribute('r') }; }""")
            l0 = lead['l'][0]
            check('ion leader starts on an ion edge', abs(l0[0] - lead['cx']) < 0.5 and abs(lead['cy'] - lead['r'] - 1 - l0[1]) < 0.5, str(lead))
            l1 = lead['l'][1]
            check('electron leader starts in a gap (not in an ion)',
                  page.evaluate("""([x, y]) => [...document.querySelectorAll('.mt-ion-c')].every(c =>
                     Math.hypot(x - c.getAttribute('cx'), y - c.getAttribute('cy')) > +c.getAttribute('r') + 8)""", [l1[0], l1[1]]), str(l1))

        print(f'== {scheme}: every metal')
        radii = {}
        for series, metals in SERIES.items():
            mps = []
            for m in metals:
                pick(series, m)
                s = st(); ion, q, mp = METALS[m]
                n_dom = page.locator('.mt-e').count(); n_ion = page.locator('.mt-ion-c').count()
                charges = set(page.evaluate("[...document.querySelectorAll('.mt-ion-c')].map(c => +c.dataset.charge)"))
                chg_txt = set(page.evaluate("[...document.querySelectorAll('.mt-fig text.mt-chg')].map(t => t.textContent)"))
                want_txt = '+' if q == 1 else f'{q}+'
                check(f'{series} {m}: electrons {n_dom} = ions {n_ion} × {q}', n_dom == n_ion * q and n_ion == 15 and charges == {q} and s['n'] == n_dom, f'{n_dom} {n_ion} {charges}')
                check(f'{series} {m}: ion charge text "{want_txt}" in every circle', chg_txt == {want_txt} and page.locator('.mt-fig text.mt-chg').count() == 15, str(chg_txt))
                cnt = page.inner_text('.mt-count')
                check(f'{series} {m}: counter "15 ions × {q} = {15*q}"', f'15 ions × {q} = {15*q} delocalised electrons' in cnt, cnt)
                t_ion, t_ne, t_mp = (page.inner_text(c) for c in ('.mt-t-ion', '.mt-t-ne', '.mt-t-mp'))
                check(f'{series} {m}: card ion {ion}, {q} e⁻/atom, m.p. {mp} °C', (t_ion, t_ne, t_mp) == (ion, str(q), f'{mp} °C'), f'{t_ion} {t_ne} {t_mp}')
                bars = page.evaluate("""() => [...document.querySelectorAll('.mt-brow')].map(r => [r.dataset.metal, +r.dataset.mp,
                    r.querySelector('i').getBoundingClientRect().width, r.classList.contains('sel'), r.querySelector('.mt-bv').textContent])""")
                check(f'{series} {m}: bars = {metals}, selected highlighted, values match',
                      [x[0] for x in bars] == metals and [x[3] for x in bars] == [k == m for k in metals] and
                      all(x[1] == METALS[x[0]][2] and x[4] == f'{METALS[x[0]][2]} °C' for x in bars), str(bars))
                mps.append([x[2] for x in bars])
                why = page.inner_text('.mt-why').replace('\u00a0', ' '); trend = page.inner_text('.mt-trend')
                check(f'{series} {m}: explanation mentions {ion} and {mp} °C', ion in why and f'{mp} °C' in why, why)
                want_tr = 'across Period 3：charge ↑、ion 变小 → 增强' if series == 'p3' else 'down Group 1：ion 变大 → 减弱'
                check(f'{series} {m}: trend line', trend == want_tr, trend)
                on_btn = page.evaluate("[...document.querySelectorAll('.mt-ser button.on')].map(b => b.dataset.series + b.dataset.metal)")
                check(f'{series} {m}: exactly that button on', on_btn == [series + m], str(on_btn))
                check(f'{series} {m}: no electron inside an ion, no overlapping electrons', s['inside'] == 0 and s['overlaps'] == 0, str(s))
                radii[m] = s['r']
                check(f'{series} {m}: [data-clash] = 0 & labels clear', page.locator('[data-clash]').count() == 0 and not page.evaluate(AUDIT_JS),
                      str(page.evaluate(AUDIT_JS)))
                if scheme == 'light' or m in ('Al', 'K'):
                    shot(f'm-{series}-{m}'); resume()
            w = mps[-1]
            if series == 'p3':
                check('p3 strength bars increase Na < Mg < Al', w[0] < w[1] < w[2], str(w))
            else:
                check('g1 strength bars decrease Li > Na > K', w[0] > w[1] > w[2], str(w))
        check('ion radius Li⁺ < Na⁺ < K⁺', radii['Li'] < radii['Na'] < radii['K'], str(radii))
        check('ion radius Al³⁺ < Mg²⁺ < Na⁺', radii['Al'] < radii['Mg'] < radii['Na'], str(radii))

        print(f'== {scheme}: animation, power, pause')
        pick('p3', 'Mg'); resume(); page.wait_for_timeout(200)
        fr = frames(page)
        moved = sum(1 for i in range(1, len(fr)) if fr[i] != fr[i - 1])
        check('animation runs: electrons move between frames', moved == len(fr) - 1, str(moved))
        s0 = st(); page.wait_for_timeout(2000); s1 = st()
        check('power off: no net drift (|Δ mean x| < 20, no wrap)', abs(s1['meanUx'] - s0['meanUx']) < 20 and s1['wraps'] == s0['wraps'],
              f"{s1['meanUx'] - s0['meanUx']:.1f} wraps {s0['wraps']}->{s1['wraps']}")
        check('caption off state', 'off' in page.get_attribute('.mt-circ', 'class') and page.get_attribute('.mt-cap', 'data-on') == '0')
        ions_before = page.evaluate("[...document.querySelectorAll('.mt-ion-c')].map(c => c.getAttribute('cx') + ',' + c.getAttribute('cy'))")

        page.click('.mt-pow'); page.wait_for_timeout(100)
        cap = page.inner_text('.mt-cap')
        check('power on: caption quotes MS wording', 'delocalised electrons move (through the structure)' in cap and '9701/21 May/June 2025 Q1(a)(ii)' in cap, cap)
        check('power on: button pressed, circuit drawn solid', page.get_attribute('.mt-pow', 'aria-pressed') == 'true' and
              'off' not in page.get_attribute('.mt-circ', 'class') and page.inner_text('.mt-pow') == '断开电源')
        s0 = st(); fr = frames(page, 12, 150); s1 = st()
        dmean = s1['meanUx'] - s0['meanUx']
        check('power on: mean x moves toward + terminal (Δ > 40)', dmean > 40, f'{dmean:.1f}')
        check('power on: electrons leave at + end and re-enter at − end (wraps grow, count fixed)',
              s1['wraps'] > s0['wraps'] and s1['n'] == 30 and page.locator('.mt-e').count() == 30, f"{s0['wraps']}->{s1['wraps']}")
        # DOM sampling: per-frame Δx of each electron (wraps excluded) averages positive
        dx = [fr[i][k][0] - fr[i - 1][k][0] for i in range(1, len(fr)) for k in range(len(fr[i])) if abs(fr[i][k][0] - fr[i - 1][k][0]) < 100]
        avg = sum(dx) / len(dx)
        check('power on: DOM frames show average Δx > 0 every sample window', avg > 2, f'{avg:.2f} px / frame')
        pos_frames = sum(1 for i in range(1, len(fr)) if sum(fr[i][k][0] - fr[i - 1][k][0] for k in range(len(fr[i])) if abs(fr[i][k][0] - fr[i - 1][k][0]) < 100) > 0)
        check('power on: ≥ 9 of 11 frame windows drift to +', pos_frames >= 9, str(pos_frames))
        s2 = st()
        check('power on: still no electron inside an ion, ≤ 1 overlapping electron pair', s2['inside'] == 0 and s2['overlaps'] <= 1, str(s2))
        ions_after = page.evaluate("[...document.querySelectorAll('.mt-ion-c')].map(c => c.getAttribute('cx') + ',' + c.getAttribute('cy'))")
        check('ions do not move', ions_before == ions_after)
        check('power on: [data-clash] = 0', page.locator('[data-clash]').count() == 0 and not page.evaluate(AUDIT_JS), str(page.evaluate(AUDIT_JS)))
        shot('power-on-Mg'); shot('zoom-power-fig', '.mt-figcard'); resume()
        for m, ser in (('Al', 'p3'), ('K', 'g1')):
            pick(ser, m)
            check(f'power stays on after switching to {m}; electrons {15 * METALS[m][1]}', st()['on'] and page.locator('.mt-e').count() == 15 * METALS[m][1])
            s0 = st(); page.wait_for_timeout(1500); s1 = st()
            check(f'{m} powered: drift Δ > 30', s1['meanUx'] - s0['meanUx'] > 30, f"{s1['meanUx'] - s0['meanUx']:.1f}")
            if scheme == 'light':
                shot(f'power-on-{m}'); resume()

        page.click('.mt-pow'); page.wait_for_timeout(300)
        s0 = st(); page.wait_for_timeout(2000); s1 = st()
        check('power off again: drift stops (|Δ| < 20, wraps unchanged)', abs(s1['meanUx'] - s0['meanUx']) < 20 and s1['wraps'] == s0['wraps'],
              f"{s1['meanUx'] - s0['meanUx']:.1f}")
        check('power off again: caption back to off', page.get_attribute('.mt-cap', 'data-on') == '0' and page.inner_text('.mt-pow') == '接上电源')

        page.click('.mt-pause'); page.wait_for_timeout(100)
        fr = frames(page, 4, 150)
        check('pause button: electrons frozen', all(f == fr[0] for f in fr) and page.inner_text('.mt-pause') == '▶ 继续动画')
        page.click('.mt-pause'); page.wait_for_timeout(100)
        fr = frames(page, 4, 150)
        check('resume: electrons move again', fr[0] != fr[-1] and page.inner_text('.mt-pause') == '⏸ 暂停动画')
        page.evaluate("""() => { Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'hidden' });
                                 document.dispatchEvent(new Event('visibilitychange')); }""")
        page.wait_for_timeout(100); fr = frames(page, 4, 150)
        check('page hidden: animation paused', all(f == fr[0] for f in fr))
        page.evaluate("() => { delete document.visibilityState; document.dispatchEvent(new Event('visibilitychange')); }")
        page.wait_for_timeout(100); fr = frames(page, 4, 150)
        check('page visible again: animation resumes', fr[0] != fr[-1])
        page.evaluate('window.scrollTo(0, 0)')
        page.set_viewport_size({'width': 1000, 'height': 300}); page.evaluate('() => document.querySelector(".k").style.marginTop = "1200px"')
        page.wait_for_timeout(250); fr = frames(page, 3, 150)
        check('scrolled out of view: animation paused', all(f == fr[0] for f in fr) and not st()['inView'])
        page.evaluate('() => document.querySelector(".k").style.marginTop = ""'); page.set_viewport_size({'width': 1000, 'height': 1100})
        page.wait_for_timeout(250)

        check(f'{scheme} 1000px: fonts >= 12px', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))

        pick('p3', 'Na')
        shot('zoom-lattice-Na', '.mt-fig'); shot('zoom-info-Na', '.mt-info'); resume()
        pick('p3', 'Al'); page.click('.mt-pow'); page.wait_for_timeout(600)
        shot('zoom-lattice-Al-on', '.mt-figcard'); resume()
        page.click('.mt-pow')

        print(f'== {scheme}: narrow 720px')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(200)
        pick('g1', 'K')
        ov = page.evaluate("() => { const k = document.querySelector('.k'); return k.scrollWidth - k.clientWidth; }")
        check('narrow: no horizontal overflow', ov <= 1, str(ov))
        check('narrow: fonts >= 12px (HTML + SVG scaled)', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
        check('narrow: no clash', page.locator('[data-clash]').count() == 0 and not page.evaluate(AUDIT_JS))
        shot('narrow-720-K'); resume()
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for r in results if r[1])
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
