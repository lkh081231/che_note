"""kit Periodic Table (<div class="k-ptable">) test, on a ch01 practice cell.

usage: uv run --with playwright python -I colab/tests/kit_ptable.py $COLAB_TMP/ch01-atomic-structure <shots-dir>
(build first: python3 tools/build_colab.py ch01 && python3 tools/check_colab.py ch01)
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402  ($CHROME → Windows path → PATH)
from pathlib import Path
from playwright.sync_api import sync_playwright

D = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
results, errors = [], []

# the first practice page (title '📝 9701/…'); build_colab puts the table placeholder at the top of every one
PAGE = next(f for f in sorted(D.glob('cell-*.html')) if '<title>📝' in f.read_text(encoding='utf-8'))
print('page:', PAGE.name)


def shot(page, sel, path):
    bb = page.eval_on_selector(sel, 'e => { const r = e.getBoundingClientRect(); return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }')
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


OVER = '''() => ({ page: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  k: (k => k.scrollWidth - k.clientWidth)(document.querySelector('.k')),
  scroll: (s => s.scrollWidth - s.clientWidth)(document.querySelector('.pt-scroll')) })'''

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome(), headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'PAGEERROR {e}'))
        page.add_init_script('''window.__fits = 0; window.google = { colab: { output: { setIframeHeight: function () { window.__fits++; } } } };''')
        page.goto(PAGE.as_uri()); page.wait_for_timeout(400)
        print(f'== {scheme}')
        btn = page.locator('.k-ptable .pt-btn')
        if scheme == 'light':
            check('one table button, first thing in the practice cell', btn.count() == 1 and
                  page.evaluate('() => document.querySelector(".k").firstElementChild.classList.contains("k-ptable")'))
            check('button reads "Periodic Table"', 'Periodic Table' in btn.inner_text(), btn.inner_text())
            check('collapsed by default (aria-expanded=false, table hidden)',
                  btn.get_attribute('aria-expanded') == 'false' and not page.locator('.pt-grid').is_visible())
            check('it is a real <button type=button> (keyboard reachable)',
                  page.evaluate('() => { const b = document.querySelector(".pt-btn"); return b.tagName === "BUTTON" && b.type === "button"; }'))
            # open with the keyboard: focus + Enter
            btn.focus(); fits0 = page.evaluate('window.__fits'); page.keyboard.press('Enter'); page.wait_for_timeout(150)
        else:
            btn.click(); page.wait_for_timeout(150)
        check(f'{scheme}: opens (aria-expanded=true, grid visible)', btn.get_attribute('aria-expanded') == 'true' and page.locator('.pt-grid').is_visible())
        if scheme == 'light':
            check('opening calls K.fit (setIframeHeight)', page.evaluate('window.__fits') > fits0)
            n_el = page.locator('.pt-el[data-z]').count()
            check('118 element cells', n_el == 118, str(n_el))
            check('2 placeholders 57–71 / 89–103 in period 6 / 7, group 3',
                  page.locator('.pt-el[data-range]').count() == 2 and
                  page.evaluate('''() => [...document.querySelectorAll('.pt-el[data-range]')].map(e => e.style.gridColumnStart + '/' + e.style.gridRowStart + ':' + e.querySelector('.pt-z').textContent).join(' ')''')
                  == '4/7:57–71 4/8:89–103')
            check('15 lanthanoids + 15 actinoids in the f rows', page.locator('.pt-el[data-f]').count() == 30)
            fe = page.evaluate('''() => { const e = document.querySelector('.pt-el[data-sym="Fe"]');
                return [e.querySelector('.pt-z').textContent, e.querySelector('.pt-s').textContent, e.querySelector('.pt-a').textContent, e.dataset.p, e.dataset.g]; }''')
            check('Fe cell: 26 / Fe / 55.8, period 4 group 8', fe == ['26', 'Fe', '55.8', '4', '8'], str(fe))
            rh = page.evaluate('() => { const e = document.querySelector(".pt-el[data-sym=Rh]"); return [e.dataset.z, e.dataset.p, e.dataset.g]; }')
            check('Rh: Z 45, period 5, group 9', rh == ['45', '5', '9'], str(rh))
            # visual position: Rh sits in the 5th period row, directly under Co
            pos = page.evaluate('''() => { const r = s => document.querySelector('.pt-el[data-sym="' + s + '"]').getBoundingClientRect();
                const ph = [...document.querySelectorAll('.pt-ph')].find(e => e.textContent === '5').getBoundingClientRect();
                const rh = r('Rh'), co = r('Co');
                return { row: Math.abs((rh.top + rh.bottom) / 2 - (ph.top + ph.bottom) / 2), col: Math.abs(rh.left - co.left), below: rh.top > co.bottom }; }''')
            check('Rh drawn on the period-5 row, under Co', pos['row'] < 1 and pos['col'] < 1 and pos['below'], str(pos))
            dash = page.evaluate('() => [...document.querySelectorAll(".pt-el[data-z]")].filter(e => e.querySelector(".pt-a").textContent === "–").map(e => e.dataset.sym)')
            check('Aᵣ "–" exactly where the syllabus gives none (Tc, Pm, Po–Ra, Ac, Np–Og)',
                  {'Tc', 'Pm', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Og', 'Np', 'Lr'} <= set(dash) and 'Th' not in dash and len(dash) == 34, f'{len(dash)} {dash}')
            hd = page.evaluate('() => [[...document.querySelectorAll(".pt-gh")].map(e => e.textContent).join(","), [...document.querySelectorAll(".pt-ph")].map(e => e.textContent).join(",")]')
            check('group header 1–18, period labels 1–7', hd == [','.join(map(str, range(1, 19))), ','.join(map(str, range(1, 8)))], str(hd))
            check('element symbols keep their case (no text-transform)',
                  page.evaluate('() => getComputedStyle(document.querySelector(".pt-el[data-sym=Cl] .pt-s")).textTransform') == 'none')
        fs = page.evaluate('''() => Math.min(...[...document.querySelectorAll('.k-ptable *')].filter(e => e.offsetParent && e.childNodes.length &&
            [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())).map(e => parseFloat(getComputedStyle(e).fontSize)))''')
        check(f'{scheme}: smallest text in the table ≥ 12 px', fs >= 12, str(fs))
        clip = page.evaluate('''() => [...document.querySelectorAll('.pt-el, .pt-key, .pt-fl')].filter(e => e.scrollWidth > e.clientWidth + 0.5 || e.scrollHeight > e.clientHeight + 0.5)
            .map(e => e.dataset.sym || e.className)''')
        check(f'{scheme}: no cell text overflows its cell', not clip, str(clip))
        ov = page.evaluate(OVER)
        check(f'{scheme} 1000 px: no horizontal overflow (page, card, table)', ov['page'] <= 0 and ov['k'] <= 0 and ov['scroll'] <= 0, str(ov))
        if scheme == 'light':
            contrast = page.evaluate('''() => { const c = s => getComputedStyle(document.querySelector(s)).color; return [c('.pt-el .pt-z'), c('.pt-el .pt-s')]; }''')
            print('   colors light', contrast)
        shot(page, '.k-ptable', str(OUT / f'table-{scheme}.png'))
        if scheme == 'light':
            # z = 2 detail around Fe (rows 3–5, groups 6–11), with the period labels
            # (z = 2 against the 2× base: a device_scale_factor 4 context, same CSS layout)
            zc = b.new_context(viewport={'width': 1000, 'height': 1100}, device_scale_factor=4, color_scheme='light')
            zp = zc.new_page(); zp.goto(PAGE.as_uri()); zp.wait_for_timeout(300); zp.click('.pt-btn'); zp.wait_for_timeout(150)
            fb2 = zp.evaluate('''() => { const r = s => document.querySelector('.pt-el[data-sym="' + s + '"]').getBoundingClientRect();
                const a = r('Cr'), c = r('Cu'), t = r('Al'), g = r('Ag'), ph = [...document.querySelectorAll('.pt-ph')][2].getBoundingClientRect();
                return {x: ph.left - 4 + scrollX, y: t.top - 4 + scrollY, width: c.right - ph.left + 8, height: g.bottom - t.top + 8}; }''')
            zp.screenshot(path=str(OUT / 'zoom-fe-z2.png'), clip=fb2, full_page=True)
            zc.close()
            # f rows detail
            fr = page.evaluate('''() => { const a = document.querySelector('.pt-fl').getBoundingClientRect(), z = document.querySelector('.pt-el[data-sym="Lr"]').getBoundingClientRect(),
                l = document.querySelector('.pt-el[data-sym="Lu"]').getBoundingClientRect();
                return {x: a.left + scrollX - 4, y: l.top + scrollY - 4, width: z.right - a.left + 8, height: z.bottom - l.top + 8}; }''')
            page.screenshot(path=str(OUT / 'zoom-frows.png'), clip=fr, full_page=True)
            # close again
            btn.click(); page.wait_for_timeout(150)
            check('closes again (aria-expanded=false, grid hidden)', btn.get_attribute('aria-expanded') == 'false' and not page.locator('.pt-grid').is_visible())
            # Enter / arrow-key jumps between answer boxes still work with the button in the cell
            boxes = page.locator('input.fill')
            if boxes.count() >= 2:
                boxes.nth(0).focus(); page.keyboard.press('Enter')
                check('Enter in the first answer box still jumps to the next box',
                      page.evaluate('() => document.activeElement === document.querySelectorAll("input.fill")[1]'))
            print('== narrow (720 px)')
            btn.click(); page.wait_for_timeout(100)
            page.set_viewport_size({'width': 720, 'height': 1100}); page.wait_for_timeout(250)
            ov = page.evaluate(OVER)
            check('720 px: page and card do not overflow; the table scrolls inside .pt-scroll',
                  ov['page'] <= 0 and ov['k'] <= 0 and ov['scroll'] > 0, str(ov))
            check('720 px: .pt-scroll is overflow-x:auto', page.evaluate('() => getComputedStyle(document.querySelector(".pt-scroll")).overflowX') == 'auto')
            shot(page, '.k', str(OUT / 'card-720.png'))
            shot(page, '.k-ptable', str(OUT / 'table-720.png'))
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
