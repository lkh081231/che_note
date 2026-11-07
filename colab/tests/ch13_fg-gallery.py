"""ch13 fg-gallery cell test.

usage: TMPDIR=/mnt/ai-shared/che_tmp/organic/prof/fg-gallery uv run --with playwright python -I colab/tests/ch13_fg-gallery.py /mnt/ai-shared/che_tmp/organic/cells/ch13-fg-gallery.html /mnt/ai-shared/che_tmp/organic/shots/fg-gallery
(build first: COLAB_TMP=/mnt/ai-shared/che_tmp/organic python3 tools/build_colab.py ch13 --cell fg-gallery)
"""
import math
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from check_colab import chrome  # noqa: E402

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
CHROMIUM = '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else chrome()

results, errors = [], []


def shot(page, sel, path):
    """Element screenshot via page clip so headless Chromium never hangs waiting for rAF stability."""
    bb = page.eval_on_selector(
        sel,
        'e => { const r = e.getBoundingClientRect(); '
        'return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}; }'
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


def shot_pair(page, sel_a, sel_b, path, pad=6):
    """Clip spanning two adjacent cards for z>=2 local inspection."""
    bb = page.evaluate(
        '''([sa, sb, p]) => {
            const a = document.querySelector(sa).getBoundingClientRect();
            const b = document.querySelector(sb).getBoundingClientRect();
            const x0 = Math.max(0, Math.min(a.left, b.left) + scrollX - p);
            const y0 = Math.max(0, Math.min(a.top, b.top) + scrollY - p);
            const x1 = Math.max(a.right, b.right) + scrollX + p;
            const y1 = Math.max(a.bottom, b.bottom) + scrollY + p;
            return {x: x0, y: y0, width: x1 - x0, height: y1 - y0};
        }''',
        [sel_a, sel_b, pad]
    )
    page.screenshot(path=str(path), clip=bb, full_page=True)


def check(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(('  ok   ' if cond else '  FAIL ') + name + (f' — {detail}' if detail and not cond else ''))


EXPECTED = [
    ('alkene',          'alkene',          'C=C bond',  'propene',           'CH₂=CHCH₃',     'ch14-alkenes',         9),
    ('halogenoalkane',  'halogenoalkane',  'halogen',   '1-chloropropane',   'CH₃CH₂CH₂Cl',   'ch15-halogenoalkanes', 10),
    ('alcohol',         'alcohol',         'hydroxyl',  'propan-1-ol',       'CH₃CH₂CH₂OH',   'ch16-alcohols',        11),
    ('aldehyde',        'aldehyde',        'carbonyl',  'propanal',          'CH₃CH₂CHO',     'ch17-carbonyls',       10),
    ('ketone',          'ketone',          'carbonyl',  'propanone',         'CH₃COCH₃',      'ch17-carbonyls',       10),
    ('carboxylic-acid', 'carboxylic acid', 'carboxyl',  'propanoic acid',    'CH₃CH₂COOH',    'ch18-acids',           11),
    ('ester',           'ester',           'ester',     'methyl propanoate', 'CH₃CH₂COOCH₃',  'ch18-esters',          14),
    ('amine',           'amine',           'amine',     'propylamine',       'CH₃CH₂CH₂NH₂',  'ch19-amines',          12),
    ('nitrile',         'nitrile',         'nitrile',   'propanenitrile',    'CH₃CH₂CN',      'ch19-nitriles',        10),
]
MODES = ('general', 'structural', 'displayed', 'skeletal')


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, headless=True, args=['--disable-gpu'])
    for scheme in ('light', 'dark'):
        ctx = b.new_context(viewport={'width': 1000, 'height': 1400}, device_scale_factor=2, color_scheme=scheme)
        page = ctx.new_page()
        page.on('console', lambda m: errors.append(f'{scheme}: {m.text}') if m.type == 'error' else None)
        page.on('pageerror', lambda e: errors.append(f'{scheme} PAGEERROR: {e}'))
        page.goto(PAGE.as_uri())
        page.wait_for_timeout(300)

        def clashes():
            return page.locator('[data-clash]').count()

        def svg_geometry_issues():
            """Check all visible svg.cf: inside card, text inside viewBox, no text-text bbox overlap."""
            return page.evaluate('''() => {
                const bad = [];
                document.querySelectorAll('.fg-card').forEach(card => {
                    const key = card.getAttribute('data-series');
                    const cr = card.getBoundingClientRect();
                    const pane = card.querySelector('.fg-pane.show');
                    if (!pane) { bad.push(key + ': no .show pane'); return; }
                    const svg = pane.querySelector('svg.cf');
                    if (!svg) return;
                    const sr = svg.getBoundingClientRect();
                    if (sr.width < 40 || sr.height < 30) bad.push(key + ': tiny svg ' + sr.width + 'x' + sr.height);
                    if (sr.left < cr.left - 0.5 || sr.right > cr.right + 0.5 ||
                        sr.top < cr.top - 0.5 || sr.bottom > cr.bottom + 0.5) {
                        bad.push(key + ': svg overflows card');
                    }
                    // .fg-stage is overflow:hidden — anything poking out of it is silently clipped
                    const st = card.querySelector('.fg-stage').getBoundingClientRect();
                    pane.querySelectorAll('svg.cf, .fg-cap, .fg-stxt').forEach(el => {
                        const r = el.getBoundingClientRect();
                        if (r.top < st.top - 0.5 || r.bottom > st.bottom + 0.5)
                            bad.push(key + ': clipped by stage: ' + el.tagName + ' ' + el.textContent.slice(0, 20));
                    });
                    const vb = svg.viewBox.baseVal;
                    const boxes = [...svg.querySelectorAll('text')].map(t => ({t: t.textContent, b: t.getBBox()}));
                    boxes.forEach(({t, b}) => {
                        if (b.x < vb.x - 0.5 || b.y < vb.y - 0.5 ||
                            b.x + b.width > vb.x + vb.width + 0.5 || b.y + b.height > vb.y + vb.height + 0.5) {
                            bad.push(key + ': text outside viewBox: ' + t);
                        }
                    });
                    for (let i = 0; i < boxes.length; i++) {
                        for (let j = i + 1; j < boxes.length; j++) {
                            const a = boxes[i].b, c = boxes[j].b;
                            if (a.x + 1 < c.x + c.width && c.x + 1 < a.x + a.width &&
                                a.y + 1 < c.y + c.height && c.y + 1 < a.y + a.height) {
                                bad.push(key + ': text overlap ' + boxes[i].t + '/' + boxes[j].t);
                            }
                        }
                    }
                });
                return bad;
            }''')

        def row_alignment_issues():
            """Cards on the same grid row must align at top and bottom within 1 px."""
            return page.evaluate('''() => {
                const rects = [...document.querySelectorAll('.fg-card')].map(c => c.getBoundingClientRect());
                const rows = [];
                rects.forEach(r => {
                    const row = rows.find(g => Math.abs(g[0].top - r.top) < 8);
                    if (row) row.push(r); else rows.push([r]);
                });
                const bad = [];
                rows.forEach((g, idx) => {
                    const tops = g.map(r => r.top), hs = g.map(r => r.height);
                    if (Math.max(...tops) - Math.min(...tops) > 1) bad.push('row ' + idx + ' top mismatch');
                    if (Math.max(...hs) - Math.min(...hs) > 1) bad.push('row ' + idx + ' height mismatch');
                });
                return {cols: rows[0] ? rows[0].length : 0, bad};
            }''')

        if scheme == 'dark':
            print('== dark theme')
            check('dark: no label clash', clashes() == 0, str(clashes()))
            hl_col = page.evaluate('''() => {
                const k = getComputedStyle(document.querySelector('.k'));
                const acc = k.getPropertyValue('--acc').trim();
                const ln = getComputedStyle(document.querySelector('svg.cf line.fg-b')).stroke;
                const fg = getComputedStyle(document.querySelector('svg.cf .cf-b line:not(.fg-b)')).stroke;
                return {acc, ln, fg, diff: ln !== fg};
            }''')
            check('dark: --acc highlight distinct from --fg bond colour', hl_col['diff'], str(hl_col))
            check('dark: displayed geometry clean', not svg_geometry_issues(), str(svg_geometry_issues()))
            shot(page, '.k', OUT / 'card-displayed-dark.png')
            page.click('.fg-all button[data-all="skeletal"]')
            page.wait_for_timeout(100)
            check('dark: skeletal geometry clean', not svg_geometry_issues(), str(svg_geometry_issues()))
            shot(page, '.k', OUT / 'card-skeletal-dark.png')
            page.click('.fg-all button[data-all="general"]')
            page.wait_for_timeout(80)
            check('dark: general geometry clean', not svg_geometry_issues(), str(svg_geometry_issues()))
            shot(page, '.k', OUT / 'card-general-dark.png')
            page.click('.fg-all button[data-all="structural"]')
            page.wait_for_timeout(80)
            mf_dark = page.evaluate('''() => {
                const el = document.querySelector('.fg-card .fg-pane.show .fg-mf');
                const s = getComputedStyle(el);
                return {fs: parseFloat(s.fontSize), color: s.color};
            }''')
            check('dark: molecular formula text >= 16px', mf_dark['fs'] >= 16.0, str(mf_dark))
            shot(page, '.k', OUT / 'card-structural-dark.png')
            page.click('.fg-all button[data-all="displayed"]')
            page.wait_for_timeout(60)

            # z>=2 close-up in dark mode via 3x DPR context (no CSS zoom clip drift)
            zctx = b.new_context(viewport={'width': 1000, 'height': 1400}, device_scale_factor=3, color_scheme='dark')
            zp = zctx.new_page()
            zp.goto(PAGE.as_uri())
            zp.wait_for_timeout(200)
            zp.click('.fg-card[data-series="nitrile"] button[data-f="skeletal"]')
            zp.click('.fg-card[data-series="amine"] button[data-f="skeletal"]')
            zp.wait_for_timeout(60)
            shot_pair(zp, '.fg-card[data-series="ester"]', '.fg-card[data-series="nitrile"]',
                      OUT / 'zoom-dark-ester-nitrile.png')
            btn_on_dark = page.evaluate('''() => {
                const s = getComputedStyle(document.querySelector('.fg-tabs button.on'));
                return {fg: s.color, bg: s.backgroundColor, ok: s.color !== s.backgroundColor && !s.color.includes('170, 177')};
            }''')
            check('dark: active card tab button text high contrast', btn_on_dark['ok'], str(btn_on_dark))
            zctx.close()
            ctx.close()
            continue

        print('== light: 9 cards metadata & xrefs')
        cards_meta = page.evaluate('''() => [...document.querySelectorAll('.fg-card')].map(c => ({
            key: c.getAttribute('data-series'),
            series: c.querySelector('.fg-s').textContent.trim(),
            fg: c.querySelector('.fg-pill').textContent.trim(),
            ex: c.querySelector('.fg-name').textContent.trim(),
            href: c.querySelector('a.xref') ? c.querySelector('a.xref').getAttribute('href') : '',
            target: c.querySelector('a.xref') ? c.querySelector('a.xref').getAttribute('target') : '',
            ref: c.querySelector('.fg-ref') ? c.querySelector('.fg-ref').textContent.trim() : ''
        }))''')
        check('9 homologous series cards present', len(cards_meta) == 9, str(len(cards_meta)))
        check('all 9 cards have syllabus ref in footer', all(len(c['ref']) >= 4 for c in cards_meta),
              str([c['ref'] for c in cards_meta]))
        check('series order matches syllabus table',
              [c['series'] for c in cards_meta] == [e[1] for e in EXPECTED],
              str([c['series'] for c in cards_meta]))
        check('functional group names match syllabus',
              [c['fg'] for c in cards_meta] == [e[2] for e in EXPECTED],
              str([c['fg'] for c in cards_meta]))
        check('example names match syllabus',
              [c['ex'] for c in cards_meta] == [e[3] for e in EXPECTED],
              str([c['ex'] for c in cards_meta]))
        check('9 xref links with Drive URL + #scrollTo= + target=_blank',
              all(c['href'].startswith('https://colab.research.google.com/drive/')
                  and f'#scrollTo={e[5]}' in c['href']
                  and c['target'] == '_blank'
                  for c, e in zip(cards_meta, EXPECTED)),
              str([c['href'] for c in cards_meta]))

        print('== default displayed mode & --acc highlight')
        check('global displayed button active initially',
              'on' in page.get_attribute('.fg-all button[data-all="displayed"]', 'class'))
        disp_counts = page.evaluate('''() => [...document.querySelectorAll('.fg-card')].map(c => {
            const svg = c.querySelector('.fg-pane[data-pane="displayed"] svg.cf');
            return {
                lines: svg.querySelectorAll('.cf-b line').length,
                fgLines: svg.querySelectorAll('.cf-b line.fg-b').length,
                fgAtoms: svg.querySelectorAll('text.cf-a.fg-a').length
            };
        })''')
        check('displayed: bond line counts match all 9 molecules',
              [d['lines'] for d in disp_counts] == [e[6] for e in EXPECTED],
              str([d['lines'] for d in disp_counts]))
        check('displayed: every card highlights functional group in --acc',
              all(d['fgLines'] >= 1 and d['fgAtoms'] >= 1 for d in disp_counts),
              str(disp_counts))
        hl_light = page.evaluate('''() => {
            const ln = getComputedStyle(document.querySelector('svg.cf line.fg-b')).stroke;
            const fg = getComputedStyle(document.querySelector('svg.cf .cf-b line:not(.fg-b)')).stroke;
            const btn = getComputedStyle(document.querySelector('.fg-tabs button.on'));
            return {ln, fg, diff: ln !== fg, btnColor: btn.color, btnOk: btn.color === 'rgb(255, 255, 255)'};
        }''')
        check('light: --acc highlight stroke differs from --fg', hl_light['diff'], str(hl_light))
        check('light: active card tab button text is white', hl_light['btnOk'], str(hl_light))
        check('displayed: no label clash', clashes() == 0, str(clashes()))
        check('displayed: svg geometry & bounds clean', not svg_geometry_issues(), str(svg_geometry_issues()))
        align_1000 = row_alignment_issues()
        check('1000 px: 3-column grid aligned cleanly', align_1000['cols'] == 3 and not align_1000['bad'], str(align_1000))
        disp_cc_ratio = page.evaluate('''() => {
            const svg = document.querySelector('.fg-card[data-series="alkene"] .fg-pane[data-pane="displayed"] svg.cf');
            const fgLns = [...svg.querySelectorAll('.cf-b line.fg-b')];
            if (fgLns.length < 2) return 0;
            const d0 = Math.hypot(fgLns[0].x2.baseVal.value - fgLns[0].x1.baseVal.value, fgLns[0].y2.baseVal.value - fgLns[0].y1.baseVal.value);
            const d1 = Math.hypot(fgLns[1].x2.baseVal.value - fgLns[1].x1.baseVal.value, fgLns[1].y2.baseVal.value - fgLns[1].y1.baseVal.value);
            const minD = Math.min(d0, d1), maxD = Math.max(d0, d1);
            return maxD > 0 ? (minD / maxD) : 0;
        }''')
        check('displayed: alkene C=C two lines length ratio > 0.8', disp_cc_ratio > 0.8, f'ratio={disp_cc_ratio:.3f}')
        shot(page, '.k', OUT / 'card-displayed-light.png')

        print('== global switching across all 4 modes')
        for mode in MODES:
            page.click(f'.fg-all button[data-all="{mode}"]')
            page.wait_for_timeout(80)
            active_all = page.eval_on_selector_all('.fg-all button.on', 'bs => bs.map(b => b.dataset.all)')
            card_modes = page.eval_on_selector_all('.fg-card', 'cs => cs.map(c => c.dataset.mode)')
            check(f'global -> {mode}: all 9 cards switch', active_all == [mode] and card_modes == [mode] * 9,
                  f'{active_all} / {card_modes}')
            if mode == 'structural':
                stxts = page.eval_on_selector_all('.fg-card .fg-pane.show .fg-stxt', 'es => es.map(e => e.textContent.trim())')
                check('structural: all 9 condensed formulas exact',
                      stxts == [e[4] for e in EXPECTED], str(stxts))
                shot(page, '.k', OUT / 'card-structural-light.png')
            else:
                vis_svgs = page.locator('.fg-card .fg-pane.show svg.cf').count()
                fg_any = page.evaluate('''() => [...document.querySelectorAll('.fg-card .fg-pane.show svg.cf')]
                    .every(s => s.querySelectorAll('.fg-b, .fg-a').length >= 1)''')
                check(f'{mode}: 9 visible SVGs with functional group highlight', vis_svgs == 9 and fg_any, str(vis_svgs))
                check(f'{mode}: svg geometry & bounds clean', not svg_geometry_issues(), str(svg_geometry_issues()))
                check(f'{mode}: no label clash', clashes() == 0, str(clashes()))
                if mode == 'general':
                    gen_lens = page.evaluate('''() => {
                        const out = {};
                        ['halogenoalkane', 'alcohol', 'carboxylic-acid', 'amine'].forEach(k => {
                            const svg = document.querySelector(`.fg-card[data-series="${k}"] .fg-pane[data-pane="general"] svg.cf`);
                            const lns = [...svg.querySelectorAll('.cf-b line')];
                            const last = lns[lns.length - 1];
                            out[k] = Math.hypot(last.x2.baseVal.value - last.x1.baseVal.value,
                                                last.y2.baseVal.value - last.y1.baseVal.value);
                        });
                        return out;
                    }''')
                    check('general: multi-char OH / NH2 covalent bonds full length (>= 14 units)',
                          all(v >= 14.0 for v in gen_lens.values()), str(gen_lens))
                    shot(page, '.k', OUT / 'card-general-light.png')
                elif mode == 'skeletal':
                    # Verify skeletal bond angles: every C vertex has ~120° except sp nitrile C1 which is ~180°
                    ang_issues = page.evaluate('''() => {
                        const bad = [];
                        document.querySelectorAll('.fg-card').forEach(c => {
                            const key = c.dataset.series;
                            const svg = c.querySelector('.fg-pane[data-pane="skeletal"] svg.cf');
                            const atoms = JSON.parse(svg.dataset.atoms);
                            const bonds = JSON.parse(svg.dataset.bonds);
                            const adj = atoms.map(() => []);
                            bonds.forEach(([a, b]) => { adj[a].push(b); adj[b].push(a); });
                            atoms.forEach(a => {
                                if (adj[a.i].length < 2) return;
                                for (let p = 0; p < adj[a.i].length; p++) {
                                    for (let q = p + 1; q < adj[a.i].length; q++) {
                                        const u = atoms[adj[a.i][p]], v = atoms[adj[a.i][q]];
                                        const ax = u.x - a.x, ay = u.y - a.y, bx = v.x - a.x, by = v.y - a.y;
                                        const cos = (ax * bx + ay * by) / (Math.hypot(ax, ay) * Math.hypot(bx, by));
                                        const deg = Math.acos(Math.max(-1, Math.min(1, cos))) * 180 / Math.PI;
                                        const want = (key === 'nitrile' && a.i === 2) ? 180 : 120;
                                        if (Math.abs(deg - want) > 1.5) bad.push(key + ' atom ' + a.i + ': ' + deg.toFixed(1));
                                    }
                                }
                            });
                        });
                        return bad;
                    }''')
                    check('skeletal: all zig-zag / sp2 angles 120° and sp nitrile 180°', not ang_issues, str(ang_issues))
                    join_issues = page.evaluate('''() => {
                        const bad = [];
                        // 1. Skeletal alkene C=C: primary line meets single bond at vertex; secondary line is on inner side and inset
                        const alkSvg = document.querySelector('.fg-card[data-series="alkene"] .fg-pane[data-pane="skeletal"] svg.cf');
                        const alkLns = [...alkSvg.querySelectorAll('.cf-b line')].map(l => ({
                            x1: l.x1.baseVal.value, y1: l.y1.baseVal.value,
                            x2: l.x2.baseVal.value, y2: l.y2.baseVal.value
                        }));
                        const dbMain = alkLns[0], dbSec = alkLns[1], sg = alkLns[2];
                        if (Math.hypot(sg.x1 - dbMain.x2, sg.y1 - dbMain.y2) > 0.25) {
                            bad.push('alkene: double-single vertex gap');
                        }
                        const lMain = Math.hypot(dbMain.x2 - dbMain.x1, dbMain.y2 - dbMain.y1);
                        const lSec = Math.hypot(dbSec.x2 - dbSec.x1, dbSec.y2 - dbSec.y1);
                        if (lSec >= lMain - 2.0) {
                            bad.push('alkene: secondary line not inset');
                        }

                        // 1b. Aldehyde CH=O on a chain-end vertex: offset like the alkene — main line starts exactly at
                        //     the vertex where the single bond ends, second line on the inner side, nothing pokes past the vertex
                        {
                            const svg = document.querySelector('.fg-card[data-series="aldehyde"] .fg-pane[data-pane="skeletal"] svg.cf');
                            const L = l => ({x1: l.x1.baseVal.value, y1: l.y1.baseVal.value, x2: l.x2.baseVal.value, y2: l.y2.baseVal.value});
                            const fg = [...svg.querySelectorAll('.cf-b line.fg-b')].map(L);
                            const sg = [...svg.querySelectorAll('.cf-b line:not(.fg-b)')].map(L);
                            const ends = sg.flatMap(l => [[l.x1, l.y1], [l.x2, l.y2]]);
                            const main = fg.find(l => ends.some(([x, y]) => Math.hypot(l.x1 - x, l.y1 - y) < 0.25));
                            if (fg.length !== 2 || !main) bad.push('aldehyde: =O main line does not start at the vertex');
                            else {
                                const sec = fg.find(l => l !== main);
                                const ux = main.x2 - main.x1, uy = main.y2 - main.y1, d = Math.hypot(ux, uy);
                                const along = ((sec.x1 - main.x1) * ux + (sec.y1 - main.y1) * uy) / d;
                                if (along < 2) bad.push('aldehyde: second line pokes past the vertex (' + along.toFixed(1) + ')');
                                const nb = sg.find(l => Math.hypot(l.x2 - main.x1, l.y2 - main.y1) < 0.25);
                                const side = (p, q) => ((q[0] - main.x1) * -uy + (q[1] - main.y1) * ux);
                                if (nb && side(0, [sec.x1, sec.y1]) * side(0, [nb.x1, nb.y1]) <= 0)
                                    bad.push('aldehyde: second line not on the inner side');
                            }
                        }

                        // 2. Carbonyl =O in ketone / carboxylic-acid / ester (C has two other neighbours): centered symmetric lines (+-2.2, sep ~4.4)
                        ['ketone', 'carboxylic-acid', 'ester'].forEach(k => {
                            const svg = document.querySelector(`.fg-card[data-series="${k}"] .fg-pane[data-pane="skeletal"] svg.cf`);
                            const fgLns = [...svg.querySelectorAll('.cf-b line.fg-b')];
                            const l0 = fgLns[0], l1 = fgLns[1];
                            const d0 = Math.hypot(l0.x2.baseVal.value - l0.x1.baseVal.value, l0.y2.baseVal.value - l0.y1.baseVal.value);
                            const d1 = Math.hypot(l1.x2.baseVal.value - l1.x1.baseVal.value, l1.y2.baseVal.value - l1.y1.baseVal.value);
                            if (Math.abs(d0 - d1) > 0.2) {
                                bad.push(k + ': =O lines length mismatch');
                            }
                            const sep = Math.hypot(l0.x1.baseVal.value - l1.x1.baseVal.value, l0.y1.baseVal.value - l1.y1.baseVal.value);
                            if (Math.abs(sep - 4.4) > 0.3) {
                                bad.push(k + ': =O lines separation not ~4.4: ' + sep.toFixed(2));
                            }
                        });
                        return bad;
                    }''')
                    check('skeletal: crisp double-bond joins at 120° vertices', not join_issues, str(join_issues))
                    shot(page, '.k', OUT / 'card-skeletal-light.png')

        print('== per-card independent tab switching')
        page.click('.fg-all button[data-all="displayed"]')
        page.click('.fg-card[data-series="alkene"] .fg-tabs button[data-f="skeletal"]')
        check('single card switches to skeletal while others stay displayed',
              page.get_attribute('.fg-card[data-series="alkene"]', 'data-mode') == 'skeletal'
              and page.get_attribute('.fg-card[data-series="ester"]', 'data-mode') == 'displayed')
        check('global active button clears when cards are mixed',
              page.locator('.fg-all button.on').count() == 0)
        page.click('.fg-card[data-series="alkene"] .fg-tabs button[data-f="displayed"]')
        check('global active button restores when all 9 match again',
              page.eval_on_selector_all('.fg-all button.on', 'bs => bs.map(b => b.dataset.all)') == ['displayed'])

        print('== z>=2 detail screenshots (light, 3x DPR)')
        zctx = b.new_context(viewport={'width': 1000, 'height': 1400}, device_scale_factor=3, color_scheme='light')
        zp = zctx.new_page()
        zp.goto(PAGE.as_uri())
        zp.wait_for_timeout(200)
        shot_pair(zp, '.fg-card[data-series="alkene"]', '.fg-card[data-series="halogenoalkane"]',
                  OUT / 'zoom-displayed-alkene-halo.png')
        shot_pair(zp, '.fg-card[data-series="carboxylic-acid"]', '.fg-card[data-series="ester"]',
                  OUT / 'zoom-displayed-acid-ester.png')
        zp.click('.fg-all button[data-all="skeletal"]')
        zp.wait_for_timeout(80)
        shot_pair(zp, '.fg-card[data-series="alkene"]', '.fg-card[data-series="alcohol"]',
                  OUT / 'zoom-skeletal-alkene-alcohol.png')
        shot_pair(zp, '.fg-card[data-series="carboxylic-acid"]', '.fg-card[data-series="ester"]',
                  OUT / 'zoom-skeletal-acid-ester.png')
        shot_pair(zp, '.fg-card[data-series="amine"]', '.fg-card[data-series="nitrile"]',
                  OUT / 'zoom-skeletal-amine-nitrile.png')
        zp.click('.fg-all button[data-all="general"]')
        zp.wait_for_timeout(80)
        shot_pair(zp, '.fg-card[data-series="halogenoalkane"]', '.fg-card[data-series="carboxylic-acid"]',
                  OUT / 'zoom-general-alcohol-acid.png')
        zctx.close()

        print('== narrow viewport (720 px)')
        page.set_viewport_size({'width': 720, 'height': 1400})
        page.wait_for_timeout(150)
        align_720 = row_alignment_issues()
        check('720 px: exact 2-column grid aligned cleanly', align_720['cols'] == 2 and not align_720['bad'], str(align_720))
        tab_ov = page.evaluate('''() => Math.max(...[...document.querySelectorAll('.fg-tabs')]
            .map(t => t.scrollWidth - t.clientWidth))''')
        check('720 px: card tab bars do not overflow', tab_ov <= 0, str(tab_ov))
        ft_ov = page.evaluate('''() => Math.max(...[...document.querySelectorAll('.fg-ft')]
            .map(t => t.scrollWidth - t.clientWidth))''')
        check('720 px: card footers do not overflow', ft_ov <= 0, str(ft_ov))

        min_fs_all = 999.0
        for mode in MODES:
            page.click(f'.fg-all button[data-all="{mode}"]')
            page.wait_for_timeout(60)
            ov = page.evaluate('() => { const k = document.querySelector(".k"); return k.scrollWidth - k.clientWidth; }')
            check(f'720 px ({mode}): no horizontal overflow', ov <= 0, str(ov))
            if mode != 'structural':
                check(f'720 px ({mode}): svg stays inside card', not svg_geometry_issues(), str(svg_geometry_issues()))
                fs = page.evaluate('''() => Math.min(...[...document.querySelectorAll('.fg-card .fg-pane.show svg.cf')].map(s => {
                    const k = s.getBoundingClientRect().width / s.viewBox.baseVal.width;
                    const ts = [...s.querySelectorAll('text')];
                    return ts.length ? Math.min(...ts.map(t => parseFloat(getComputedStyle(t).fontSize) * k)) : 13 * k;
                }))''')
                min_fs_all = min(min_fs_all, fs)
        check('720 px: SVG font size (CSS px × rendered / viewBox width) >= 12 across all 27 SVGs',
              min_fs_all >= 12.0, f'{min_fs_all:.2f}')

        page.click('.fg-all button[data-all="displayed"]')
        page.wait_for_timeout(80)
        shot(page, '.k', OUT / 'card-720-displayed.png')
        page.click('.fg-all button[data-all="skeletal"]')
        page.wait_for_timeout(80)
        shot(page, '.k', OUT / 'card-720-skeletal.png')
        ctx.close()
    b.close()

check('no console errors / page errors', not errors, '; '.join(errors))
n = sum(1 for r in results if r[1])
print(f'{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
