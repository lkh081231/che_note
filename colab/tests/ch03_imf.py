"""ch03 imf cell test: boiling point vs intermolecular forces, five tabs —
① hydride b.p. (Groups 14–17, group toggles, trend extrapolation, hover / click info card),
② id-id vs number of electrons, ③ contact points (isomers), ④ pd-pd pairs, ⑤ id-id animation (pause / step).

usage: uv run --with playwright python -I colab/tests/ch03_imf.py <preview.html> <shots-dir>
(build the preview first: COLAB_TMP=/mnt/ai-shared/che_tmp/ch03 python3 tools/build_colab.py ch03 --cell imf)
note: never name a shot con.png — CON is a reserved file name on the NTFS share.
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402
from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []

HYD = {
    14: [('CH₄', -162), ('SiH₄', -112), ('GeH₄', -88), ('SnH₄', -52)],
    15: [('NH₃', -33), ('PH₃', -88), ('AsH₃', -62), ('SbH₃', -17)],
    16: [('H₂O', 100), ('H₂S', -60), ('H₂Se', -41), ('H₂Te', -2)],
    17: [('HF', 20), ('HCl', -85), ('HBr', -67), ('HI', -35)],
}
ELEC = [10, 18, 36, 54]


def lsq(g):  # least-squares line through Periods 3–5, evaluated at Period 2
    y = [r[1] for r in HYD[g][1:]]
    return round(sum(y) / 3 - 2 * (y[2] - y[0]) / 2)


EXP = {g: lsq(g) for g in (15, 16, 17)}
NOBLE = [('He', 2, -269), ('Ne', 10, -246), ('Ar', 18, -186), ('Kr', 36, -153), ('Xe', 54, -108)]
HAL = [('F₂', 18, -188), ('Cl₂', 34, -35), ('Br₂', 70, 59), ('I₂', 106, 184)]
ISO = {'pentane': (36, 5), '2,2-dimethylpropane': (10, 1), 'hexane': (69, 6), '2-methylpentane': (60, 5), '2,3-dimethylbutane': (58, 4)}
PD = [('propanone', 56), ('butane', -1), ('ICl', 97), ('Br₂', 59), ('methanal', -19), ('CO₂', -78)]


def fmt(v):
    return ('−' + str(-v)) if v < 0 else str(v)


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

# rendered boxes: every text vs every other text, and vs every marker (points, bars, atoms) of the visible svg
AUDIT_JS = """(sel) => {
  const svg = document.querySelector(sel);
  const R = e => e.getBoundingClientRect();
  const hit = (a, b) => a.left < b.right - 0.5 && b.left < a.right - 0.5 && a.top < b.bottom - 0.5 && b.top < a.bottom - 0.5;
  const labs = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim());
  const marks = [...svg.querySelectorAll('.imf-pt, .imf-exp, .imf-ept, .imf-pbar, .imf-cbar, .imf-mol circle')];
  const out = [];
  for (let i = 0; i < labs.length; i++) for (let j = i + 1; j < labs.length; j++)
    if (hit(R(labs[i]), R(labs[j]))) out.push(labs[i].textContent + ' <-> ' + labs[j].textContent);
  for (const t of labs) for (const m of marks) if (hit(R(t), R(m))) { out.push('on mark: ' + t.textContent); break; }
  const vb = R(svg);
  for (const t of labs) { const r = R(t); if (r.left < vb.left - 0.5 || r.right > vb.right + 0.5 || r.top < vb.top - 0.5 || r.bottom > vb.bottom + 0.5) out.push('outside svg: ' + t.textContent); }
  return out;
}"""

ANI_JS = "() => { const s = document.querySelector('.imf-asvg'); return [+s.dataset.a, +s.dataset.b, +s.dataset.phase, +s.dataset.dir, +document.querySelector('.imf-attr').getAttribute('opacity')]; }"


def at(page, sel, click=False):
    """move the mouse to the centre of an svg mark (PH₃ / HCl overlap, so page.hover would be intercepted)"""
    box = page.locator(sel).first.bounding_box()
    x, y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    page.mouse.move(x - 30, y); page.mouse.move(x, y)
    if click:
        page.mouse.click(x, y)
    page.wait_for_timeout(40)


def tab(page, t):
    page.click(f'.tabbar button[data-tab="{t}"]'); page.wait_for_timeout(150)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m, s=scheme: errors.append(f'{s}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e, s=scheme: errors.append(f'{s}: PAGEERROR {e}'))
        page.goto(PAGE.as_uri()); page.wait_for_timeout(500)
        sfx = '' if scheme == 'light' else '-dark'
        L = scheme == 'light'

        def shot(name, sel='.k'):
            if sel == '.k' and 'hover' not in name:
                page.mouse.move(2, 2); page.wait_for_timeout(30)
            page.locator(sel).first.screenshot(path=str(OUT / f'{name}{sfx}.png'))

        def clean(sel, what):
            a = page.evaluate(AUDIT_JS, sel); c = page.locator('[data-clash]').count()
            check(f'{scheme} {what}: [data-clash] = 0, no rendered overlaps', c == 0 and not a, f'clash {c}; {a[:4]}')

        # ================= ① hydrides
        print(f'== {scheme}: ① hydrides')
        check('default tab = hydride boiling points', page.get_attribute('.tabbar button[data-tab="hyd"]', 'class').find('on') >= 0)
        pts = page.evaluate("[...document.querySelectorAll('.imf-hsvg .imf-pt')].map(c => [+c.dataset.g, +c.dataset.p, c.dataset.f, +c.dataset.bp, +c.dataset.e, +c.getAttribute('cy')])")
        want = sorted((g, i + 2, f, bp, ELEC[i]) for g, rows in HYD.items() for i, (f, bp) in enumerate(rows))
        check('16 points: formula, b.p., electrons per Period', sorted(tuple(x[:5]) for x in pts) == want, str(pts))
        y0, ky = page.evaluate("[+document.querySelector('.imf-hsvg').dataset.y0, +document.querySelector('.imf-hsvg').dataset.ky]")
        check('points sit at their b.p. on the y axis', all(abs(x[5] - (y0 - x[3] * ky)) < 0.6 for x in pts))
        plabs = page.evaluate("[...document.querySelectorAll('.imf-hsvg text.imf-plab')].map(t => t.dataset.f)")
        check('16 point labels (one per hydride)', sorted(plabs) == sorted(f for rows in HYD.values() for f, _ in rows), str(plabs))
        ends = page.evaluate("[...document.querySelectorAll('.imf-hsvg text.imf-endlab')].map(t => t.textContent)")
        check('line-end labels name the group', sorted(ends) == sorted(f'{HYD[g][3][0]}  Group {g}' for g in HYD), str(ends))
        ticks = page.evaluate("[...document.querySelectorAll('.imf-hsvg text.imf-tick')].map(t => t.textContent)")
        check('y axis −200 … 120, x axis Period 2–5', ticks[:9] == [fmt(v) for v in range(-200, 121, 40)] and ticks[9:] == [f'Period {i}' for i in range(2, 6)], str(ticks))
        check('0 °C reference line', page.locator('.imf-hsvg line.imf-zero').count() == 1)
        check('no extrapolation by default', page.locator('.imf-hsvg .imf-exp, .imf-hsvg .imf-hblab').count() == 0)
        clean('.imf-hsvg', 'hydrides')
        info = page.inner_text('.imf-info')
        check('default info card = H₂O (pinned), hydrogen bonding tag', info.startswith('H₂O：100 °C') and 'hydrogen bonding' in page.inner_text('.imf-info .imf-ii'), info)
        if L:
            shot('hyd-default')

        # hover every point → info card content
        for g, rows in HYD.items():
            for i, (f, bp) in enumerate(rows):
                at(page, f'.imf-hsvg .imf-pt[data-f="{f}"]')
                head = page.inner_text('.imf-info .imf-ih'); e = page.inner_text('.imf-info .imf-ie')
                tags = page.evaluate("[...document.querySelectorAll('.imf-info .imf-tag')].map(t => t.textContent)")
                wt = ['id-id'] + (['pd-pd'] if g != 14 else []) + (['hydrogen bonding'] if g != 14 and i == 0 else [])
                why = page.inner_text('.imf-info .imf-iw')
                ok = head.startswith(f'{f}：{fmt(bp)} °C') and f'Group {g}，Period {i + 2}' in head and e == str(ELEC[i]) and tags == wt and len(why) > 20
                if g != 14 and i == 0:
                    ok = ok and 'hydrogen bonding' in why
                if g == 14:
                    ok = ok and 'non-polar' in why
                check(f'hover {f}: card b.p. {fmt(bp)}, {ELEC[i]} electrons, IMF {wt}', ok, f'{head} | {e} | {tags} | {why}')
        at(page, '.imf-hsvg .imf-pt[data-f="NH₃"]')
        shot('hyd-hover-NH3', '.k')
        shot('zoom-hover-NH3-card', '.imf-info')
        page.mouse.move(2, 2); page.wait_for_timeout(50)
        check('mouse leave → card back to pinned H₂O', page.inner_text('.imf-info .imf-ih').startswith('H₂O'))
        at(page, '.imf-hsvg .imf-pt[data-f="HCl"]', click=True); page.mouse.move(2, 2); page.wait_for_timeout(50)
        check('click HCl pins it (card stays after leave, point marked sel)',
              page.inner_text('.imf-info .imf-ih').startswith('HCl：−85 °C') and page.get_attribute('.imf-hsvg .imf-pt[data-f="HCl"]', 'class').find('sel') >= 0
              and page.locator('.imf-hsvg .imf-pt.sel').count() == 1)
        at(page, '.imf-hsvg .imf-pt[data-f="PH₃"]')
        check('PH₃ (a few px from HCl) picks PH₃', page.inner_text('.imf-info .imf-ih').startswith('PH₃：−88 °C'))

        # extrapolation on
        page.click('.imf-extbox'); page.wait_for_timeout(100)
        exps = page.evaluate("[...document.querySelectorAll('.imf-hsvg .imf-exp')].map(c => [+c.dataset.g, +c.dataset.bp, +c.getAttribute('cy')])")
        check(f'extrapolation: hollow points for Groups 15/16/17 at {EXP}', sorted(x[:2] for x in exps) == sorted([g, v] for g, v in EXP.items()), str(exps))
        check('extrapolated points at their y', all(abs(x[2] - (y0 - x[1] * ky)) < 0.6 for x in exps))
        check('Group 14 not extrapolated', page.locator('.imf-hsvg [data-g="14"].imf-exp, .imf-hsvg [data-g="14"].imf-dash, .imf-hsvg [data-g="14"].imf-arrow, .imf-hsvg [data-g="14"].imf-hblab').count() == 0)
        check('3 dashed trend lines, 3 double arrows', page.locator('.imf-hsvg .imf-dash').count() == 3 and page.locator('.imf-hsvg .imf-arrow').count() == 3)
        hb = page.evaluate("""() => [...document.querySelectorAll('.imf-hsvg text.imf-hblab')].map(t => { const g = t.dataset.g;
            const a = document.querySelector('.imf-hsvg .imf-arrow[data-g="' + g + '"]'), bb = t.getBBox();
            return [+g, t.textContent, bb.y + bb.height / 2, +a.getAttribute('y1'), +a.getAttribute('y2'), bb.x + bb.width, +a.getAttribute('x1')]; })""")
        check('"hydrogen bonding" label beside each arrow, between actual and expected points',
              len(hb) == 3 and all(x[1] == 'hydrogen bonding' and x[3] - 2 < x[2] < x[4] + 2 and x[5] < x[6] for x in hb), str(hb))
        h2o = [x for x in hb if x[0] == 16]
        ya, ye = y0 - 100 * ky, y0 - EXP[16] * ky
        check('H₂O: label between actual (100) and expected point', bool(h2o) and ya < h2o[0][2] < ye, str(h2o))
        exl = page.evaluate("[...document.querySelectorAll('.imf-hsvg text.imf-exlab')].map(t => t.textContent).join(' ')")
        check('"expected without hydrogen bonding" label', exl == 'expected without hydrogen bonding', exl)
        clean('.imf-hsvg', 'hydrides + extrapolation')
        at(page, '.imf-hsvg .imf-exp[data-g="16"]')
        it = page.inner_text('.imf-info')
        check(f'hover expected H₂O: card ≈ {fmt(EXP[16])} °C vs actual 100 °C, hydrogen bonding',
              'expected without hydrogen bonding' in it and f'≈ {fmt(EXP[16])} °C' in it and f'高出约 {100 - EXP[16]} °C' in it, it)
        shot('hyd-ext-hover-H2O-expected', '.k')
        shot('zoom-ext-period2', '.imf-plot')
        page.mouse.move(2, 2)
        page.click('.imf-extbox'); page.wait_for_timeout(80)
        check('extrapolation off again → removed', page.locator('.imf-hsvg .imf-exp, .imf-hsvg .imf-dash, .imf-hsvg .imf-hblab').count() == 0)
        page.click('.imf-extbox'); page.wait_for_timeout(80)
        shot('hyd-ext-on')

        # group toggles
        for g in (16, 14):
            page.click(f'.imf-g[data-g="{g}"]'); page.wait_for_timeout(60)
            check(f'Group {g} off: its points / line / labels gone, button aria-pressed=false',
                  page.locator(f'.imf-hsvg [data-g="{g}"]').count() == 0 and page.get_attribute(f'.imf-g[data-g="{g}"]', 'aria-pressed') == 'false')
        check('Groups 15 + 17 left: 8 points, 2 extrapolations', page.locator('.imf-hsvg .imf-pt').count() == 8 and page.locator('.imf-hsvg .imf-exp').count() == 2)
        clean('.imf-hsvg', 'groups 15+17')
        if L:
            shot('hyd-g15-g17-ext')
        for g in (16, 14):
            page.click(f'.imf-g[data-g="{g}"]'); page.wait_for_timeout(60)
        check('all groups back on: 16 points', page.locator('.imf-hsvg .imf-pt').count() == 16 and page.locator('.imf-hsvg text.imf-plab').count() == 16)
        page.click('.imf-extbox'); page.wait_for_timeout(60)

        # ================= ② electrons
        print(f'== {scheme}: ② id-id vs electrons')
        tab(page, 'ele')
        ep = page.evaluate("[...document.querySelectorAll('.imf-esvg .imf-ept')].map(c => [c.dataset.f, +c.dataset.e, +c.dataset.bp])")
        check('9 points: noble gases + halogens, electrons and b.p.', sorted(map(tuple, ep)) == sorted(NOBLE + HAL), str(ep))
        el = page.evaluate("[...document.querySelectorAll('.imf-esvg text.imf-elab')].map(t => t.textContent)")
        check('point labels "symbol  b.p."', sorted(el) == sorted(f'{f}  {fmt(v)}' for f, _, v in NOBLE + HAL), str(el))
        sl = page.evaluate("[...document.querySelectorAll('.imf-esvg text.imf-slab')].map(t => t.textContent)")
        check('series labels', sl == ['noble gases', 'halogens'], str(sl))
        check('x axis = number of electrons', 'number of electrons' in page.evaluate("[...document.querySelectorAll('.imf-esvg text')].map(t => t.textContent).join('|')"))
        ms = ' '.join(page.inner_text('[data-pane="ele"] .imf-chain').split())
        check('MS chain: electrons ↑ → stronger id-id → more energy → higher b.p.',
              ms == 'number of electrons increases → stronger id-id forces → more energy needed to overcome them → boiling point increases', ms)
        w = page.inner_text('[data-pane="ele"] .imf-warn')
        check('warning: number of protons / size of molecule 不给分', 'number of protons' in w and 'size of molecule' in w and '不给分' in w, w)
        nt = page.inner_text('[data-pane="ele"] .imf-ms')
        check('Group 14 hydrides MS (9701/21 Oct/Nov 2024 Q3(d)(i))', '9701/21 Oct/Nov 2024 Q3(d)(i)' in nt and 'greater number of electrons' in nt and 'stronger id-id forces' in nt, nt)
        page.hover('.imf-esvg .imf-ept[data-f="Kr"]'); page.wait_for_timeout(80)
        tip = page.inner_text('.k .tip.show') if page.locator('.k .tip.show').count() else ''
        check('hover Kr: tooltip 36 electrons, −153 °C, id-id only', 'Kr' in tip and '36 electrons' in tip and '−153 °C' in tip and 'id-id' in tip, tip)
        shot('ele-hover-Kr', '[data-pane="ele"] .imf-plot')
        clean('.imf-esvg', 'electrons')
        shot('ele'); shot('zoom-ele-Ar-F2', '[data-pane="ele"] .imf-plot')

        # ================= ③ contact points
        print(f'== {scheme}: ③ contact points')
        tab(page, 'con')
        for st, names in (('c5', ['pentane', '2,2-dimethylpropane']), ('c6', ['hexane', '2-methylpentane', '2,3-dimethylbutane'])):
            page.click(f'.imf-set[data-set="{st}"]'); page.wait_for_timeout(80)
            check(f'{st}: set button on, svg data-set', page.get_attribute(f'.imf-set[data-set="{st}"]', 'class').find('on') >= 0 and page.get_attribute('.imf-csvg', 'data-set') == st)
            mols = page.evaluate("[...document.querySelectorAll('.imf-csvg .imf-mol')].map(g => [g.dataset.name, g.querySelectorAll('.imf-contact').length])")
            check(f'{st}: molecules {names} with contact points {[ISO[n][1] for n in names]}', mols == [[n, ISO[n][1]] for n in names], str(mols))
            cnt = page.evaluate("[...document.querySelectorAll('.imf-csvg text.imf-cnt')].map(t => t.textContent)")
            check(f'{st}: contact count labels', [c.split('contact points ')[-1] for c in cnt] == [str(ISO[n][1]) for n in names], str(cnt))
            bars = page.evaluate("[...document.querySelectorAll('.imf-csvg .imf-cbar')].map(r => [r.dataset.name, +r.dataset.bp, +r.getAttribute('width')])")
            vals = page.evaluate("[...document.querySelectorAll('.imf-csvg text.imf-bval')].map(t => t.textContent)")
            check(f'{st}: b.p. bars {[ISO[n][0] for n in names]} °C, lengths ordered', [x[:2] for x in bars] == [[n, ISO[n][0]] for n in names]
                  and vals == [f'{ISO[n][0]} °C' for n in names] and all(bars[i][2] > bars[i + 1][2] for i in range(len(bars) - 1)), f'{bars} {vals}')
            clean('.imf-csvg', f'contact {st}')
            shot(f'contact-{st}')
        cm = page.inner_text('.imf-cms')
        check('c6 MS: 9701/22 Oct/Nov 2025 Q3(d)(ii) M1 B < A < hexane, M2 stronger / more IMFs, M3 more energy',
              '9701/22 Oct/Nov 2025 Q3(d)(ii)' in cm and 'B < A < hexane' in cm and 'stronger / more IMFs' in cm and 'most / more energy' in cm, cm)
        shot('zoom-contact-c6-mols', '[data-pane="con"] .imf-plot')
        page.click('.imf-set[data-set="c5"]'); page.wait_for_timeout(60)
        cm = page.inner_text('.imf-cms')
        check('c5 card: pentane 36 °C > 2,2-dimethylpropane 10 °C, contact points', 'pentane（36 °C）> 2,2-dimethylpropane（10 °C）' in cm and 'contact points' in cm, cm)

        # ================= ④ pd-pd
        print(f'== {scheme}: ④ pd-pd')
        tab(page, 'pd')
        bars = page.evaluate("[...document.querySelectorAll('.imf-psvg .imf-pbar')].map(r => [r.dataset.name, +r.dataset.bp])")
        check('6 bars: propanone 56 / butane −1 / ICl 97 / Br₂ 59 / methanal −19 / CO₂ −78', [tuple(x) for x in bars] == PD, str(bars))
        imfs = page.evaluate("[...document.querySelectorAll('.imf-psvg text.imf-pimf')].map(t => t.textContent)")
        check('IMF labels: polar pd-pd + id-id, non-polar id-id only', imfs == ['pd-pd + id-id', 'id-id only'] * 3, str(imfs))
        pv = page.evaluate("[...document.querySelectorAll('.imf-psvg text.imf-pval')].map(t => t.textContent)")
        check('value labels, CO₂ marked sublimes', pv == ['56 °C', '−1 °C', '97 °C', '59 °C', '−19 °C', '−78 °C（sublimes）'], str(pv))
        caps = page.evaluate("[...document.querySelectorAll('.imf-psvg text.imf-pcap')].map(t => t.textContent)")
        check('pair captions: electrons', caps == ['32 vs 34 electrons', '70 vs 70 electrons', '16 vs 22 electrons'], str(caps))
        pc = [page.inner_text(f'.imf-pc[data-pair="{i}"]') for i in range(3)]
        check('pair cards: explanation + MS (9701/21 Oct/Nov 2025 Q1(c)(iv))', 'permanent dipole' in pc[0] and '97 °C > 59 °C' in pc[1]
              and '9701/21 Oct/Nov 2025 Q1(c)(iv)' in pc[2] and 'only id-id' in pc[2] and 'pd-pd' in pc[2] and 'stronger' in pc[2], str(pc))
        page.hover('.imf-psvg .imf-pbar[data-name="ICl"]'); page.wait_for_timeout(80)
        tip = page.inner_text('.k .tip.show') if page.locator('.k .tip.show').count() else ''
        check('hover ICl bar: tooltip 70 electrons, 97 °C, pd-pd', '70 electrons' in tip and '97 °C' in tip and 'pd-pd' in tip, tip)
        shot('pd-hover-ICl', '[data-pane="pd"] .imf-plot')
        page.mouse.move(2, 2)
        clean('.imf-psvg', 'pd-pd')
        shot('pd'); shot('zoom-pd-bars', '[data-pane="pd"] .imf-plot')

        # ================= ⑤ animation
        print(f'== {scheme}: ⑤ id-id animation')
        tab(page, 'ani'); page.wait_for_timeout(300)
        fr = []
        for _ in range(8):
            fr.append(page.evaluate(ANI_JS)); page.wait_for_timeout(110)
        changed = sum(1 for i in range(1, len(fr)) if fr[i][:2] != fr[i - 1][:2] or fr[i][4] != fr[i - 1][4])
        check('playing: cloud offset changes frame to frame (≥ 5 of 7)', changed >= 5, str(fr))
        # run through a whole cycle: all three phases appear
        seen = set()
        for _ in range(30):
            seen.add(page.evaluate(ANI_JS)[2]); page.wait_for_timeout(200)
        check('playing: phases 1, 2, 3 all appear', seen == {1, 2, 3}, str(seen))
        page.click('.imf-play'); page.wait_for_timeout(100)
        check('pause button → ▶ 播放', page.inner_text('.imf-play') == '▶ 播放' and page.get_attribute('.imf-play', 'data-playing') == '0')
        fr = []
        for _ in range(5):
            fr.append(page.evaluate(ANI_JS)); page.wait_for_timeout(120)
        check('paused: nothing changes', all(f == fr[0] for f in fr), str(fr))
        # step to the end of a phase-3 then wrap, so each phase is a fully developed frame
        for _ in range(3):
            if page.evaluate(ANI_JS)[2] == 3:
                break
            page.click('.imf-step'); page.wait_for_timeout(60)
        page.click('.imf-step'); page.wait_for_timeout(80)   # → phase 1 of the next half-cycle
        d0 = page.evaluate(ANI_JS)[3]
        for want_ph in (1, 2, 3):
            a, bb, ph, d, op = page.evaluate(ANI_JS)
            pill = page.inner_text('.imf-st.on'); cap = page.inner_text('.imf-cap')
            deltas = page.evaluate("[...document.querySelectorAll('.imf-asvg text')].filter(t => /δ/.test(t.textContent)).map(t => t.dataset.atom + t.textContent)")
            names = page.evaluate("[...document.querySelectorAll('.imf-asvg text')].map(t => t.textContent)")
            want_pill = {1: '① instantaneous dipole', 2: '② induced dipole', 3: '③ id-id attraction'}[want_ph]
            ok = ph == want_ph and pill == want_pill and want_pill[2:] in cap and d == d0
            if want_ph == 1:
                ok = ok and abs(a) > 0.29 and bb == 0 and op == 0 and sorted(deltas) == ['Aδ+', 'Aδ−'] and 'atom B' in names
            elif want_ph == 2:
                ok = ok and abs(a) > 0.29 and abs(bb) > 0.21 and a * bb > 0 and op == 0 and sorted(deltas) == ['Aδ+', 'Aδ−', 'Bδ+', 'Bδ−'] and 'atom B：induced dipole' in names
            else:
                ok = ok and abs(bb) > 0.21 and op > 0.99 and 'id-id attraction' in names
            check(f'step → phase {want_ph}: pill "{want_pill}", cloud offsets, δ labels, caption', ok, f'{a} {bb} {ph} {d} {op} {pill} {deltas} {cap}')
            # δ− sits on the side the electron cloud moved to
            sides = page.evaluate("""() => { const s = document.querySelector('.imf-asvg'), dir = +s.dataset.dir, out = [];
                for (const at of ['A', 'B']) { const n = s.querySelector('text.imf-dneg[data-atom="' + at + '"]'), q = s.querySelector('text.imf-dpos[data-atom="' + at + '"]');
                  if (n && q) out.push((n.getBBox().x - q.getBBox().x) * dir > 0); } return out; }""")
            check(f'phase {want_ph}: δ− on the side the electrons moved to', all(sides) and len(sides) == min(want_ph, 2), str(sides))
            if want_ph == 3:
                ab = page.evaluate("""() => { const s = document.querySelector('.imf-asvg'), dir = +s.dataset.dir;
                    const an = s.querySelector('text.imf-dneg[data-atom="A"]').getBBox().x, bp = s.querySelector('text.imf-dpos[data-atom="B"]').getBBox().x,
                          ap = s.querySelector('text.imf-dpos[data-atom="A"]').getBBox().x, bn = s.querySelector('text.imf-dneg[data-atom="B"]').getBBox().x;
                    /* facing pair between the atoms: opposite charges */
                    return dir > 0 ? [an < bp, 'A δ− faces B δ+'] : [ap < bn, 'A δ+ faces B δ−']; }""")
                check('phase 3: facing charges of A and B are opposite (attraction)', ab[0], str(ab))
            clean('.imf-asvg', f'animation phase {want_ph}')
            shot(f'ani-phase{want_ph}')
            if want_ph == 3 or L:
                shot(f'zoom-ani-phase{want_ph}', '[data-pane="ani"] .imf-plot')
            fr = [page.evaluate(ANI_JS)]; page.wait_for_timeout(250); fr.append(page.evaluate(ANI_JS))
            check(f'phase {want_ph}: still paused after step', fr[0] == fr[1] and page.inner_text('.imf-play') == '▶ 播放')
            page.click('.imf-step'); page.wait_for_timeout(80)
        a, bb, ph, d, op = page.evaluate(ANI_JS)
        check('step after phase 3 → phase 1 with the dipole reversed', ph == 1 and d == -d0, f'{ph} {d} {d0}')
        page.click('.imf-play'); page.wait_for_timeout(150)
        fr = [page.evaluate(ANI_JS)]; page.wait_for_timeout(1000); fr.append(page.evaluate(ANI_JS))
        check('play again: moving (sampled 1 s apart, past the hold)', fr[0] != fr[1] and page.inner_text('.imf-play') == '⏸ 暂停', str(fr))

        check(f'{scheme} 1000px: fonts >= 12px (all tabs drawn)', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))

        # ================= narrow
        print(f'== {scheme}: narrow 720px')
        page.set_viewport_size({'width': 720, 'height': 1300}); page.wait_for_timeout(300)
        for t, sel in (('hyd', '.imf-hsvg'), ('ele', '.imf-esvg'), ('con', '.imf-csvg'), ('pd', '.imf-psvg'), ('ani', '.imf-asvg')):
            tab(page, t)
            if t == 'hyd':
                page.click('.imf-extbox'); page.wait_for_timeout(80)
            if t == 'con':
                page.click('.imf-set[data-set="c6"]'); page.wait_for_timeout(80)
            if t == 'ani' and page.inner_text('.imf-play') == '⏸ 暂停':
                page.click('.imf-play')
            page.wait_for_timeout(150)
            ov = page.evaluate("() => { const k = document.querySelector('.k'); return k.scrollWidth - k.clientWidth; }")
            check(f'narrow {t}: no horizontal overflow', ov <= 1, str(ov))
            check(f'narrow {t}: fonts >= 12px (HTML + SVG scaled)', not page.evaluate(SMALL_JS), str(page.evaluate(SMALL_JS)[:5]))
            if t == 'hyd':
                check('narrow hyd: still 16 point labels', page.locator('.imf-hsvg text.imf-plab').count() == 16)
            clean(sel, f'narrow {t}')
            shot(f'narrow-720-{t}')
        ctx.close()
    b.close()

check('console / page errors = 0', not errors, '; '.join(errors[:5]))
passed = sum(1 for r in results if r[1])
print(f'{passed}/{len(results)} passed')
sys.exit(0 if passed == len(results) else 1)
