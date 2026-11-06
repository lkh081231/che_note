"""Mechanical checks for colab/chNN-*.ipynb, plus preview pages and a headless JS error scan.

usage: python tools/check_colab.py ch01 [--js] [--xref]
  writes $COLAB_TMP/<slug>/cell-<id>.html (one per html cell) and all.html (every html cell stacked)
  --js    load every preview page in headless Chrome/Chromium and report uncaught errors
  --xref  links and the reaction registry (on by default for ch13–ch21): every {{xref}} target anchor
          exists and has a Drive id, every registry home anchor of this chapter exists, LO references
          in the registry exist, each "recall the reactions by which … can be produced" LO sits in an
          md cell with a {{rxn-in}} table, and the built notebook has no unresolved link

Chrome is found as in probe-roadmap-geometry.py: $CHROME → Windows install path → PATH.
3D cells need WebGL, so the scan uses SwiftShader (--use-angle=swiftshader), not --disable-gpu.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_colab import ROOT, COLAB, load_los, parse_blocks, drive_ids, nb_name, organic, split_home  # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def chrome():
    c = os.environ.get('CHROME')
    if c:
        return c
    if os.path.isfile('C:/Program Files/Google/Chrome/Application/chrome.exe'):
        return 'C:/Program Files/Google/Chrome/Application/chrome.exe'
    for n in ('google-chrome', 'chromium', 'chromium-browser'):
        if shutil.which(n):
            return shutil.which(n)
    raise SystemExit('No Chrome/Chromium found. Set CHROME=/path/to/chrome.')


XREF = re.compile(r'\{\{xref\s+(ch\d\d)?#([\w-]+)')


def anchors_of(prefix):
    src = sorted((COLAB / 'src').glob(f'{prefix}-*.md'))
    return {a for _, _, a, _ in parse_blocks(src[0])} - {None} if src else set()


def lo_exists(ref):
    """'16.1.2(d)(i)' → LO 16.1.2 exists and (when given) its sub-part (d) is there"""
    m = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:\(([a-z])\))?', ref)
    if not m:
        return False
    los, _ = load_los(int(m.group(1)))
    lo = los.get(f'{m.group(1)}.{m.group(2)}.{m.group(3)}')
    if not lo:
        return False
    if not m.group(4):
        return True
    t = ' '.join([lo['text']] + lo['subs'] + lo['extra'])
    return f'({m.group(4)})' in t


def check_xref(prefix, nb, fail):
    print('== links / registry')
    srcf = sorted((COLAB / 'src').glob(f'{prefix}-*.md'))[0]
    blocks = parse_blocks(srcf)
    texts = [t for _, _, _, t in blocks] + [f.read_text(encoding='utf-8') for f in sorted((COLAB / 'src' / prefix).glob('*.html'))]
    ids, cache, n = drive_ids(), {}, 0
    for t in texts:
        for m in XREF.finditer(t):
            ch, a = m.group(1) or prefix, m.group(2)
            n += 1
            if ch not in cache:
                cache[ch] = anchors_of(ch)
            if a not in cache[ch]:
                fail(f'xref {ch}#{a}: no such anchor')
            if not ids.get(nb_name(ch) or ''):
                fail(f'xref {ch}#{a}: {ch} has no Drive id in drive-ids.json')
    org = organic()
    mine = anchors_of(prefix)
    homes = [r['home'] for r in org['reactions']] + [t['home'] for t in org.get('tests', [])] + \
            [c['home'] for c in org['classes'].values()]
    for h in sorted(set(homes)):
        ch, a = split_home(h)
        if ch == prefix and a not in mine:
            fail(f'registry home {h}: no such anchor in {srcf.name}')
    chap = int(prefix[2:])
    for r in org['reactions'] + org.get('tests', []):
        for ref in r['los']:
            if ref.startswith(f'{chap}.') and not lo_exists(ref):
                fail(f'registry {r["id"]}: LO {ref} not in reference.md')
    los, _ = load_los(chap)
    for k, lo in los.items():
        if lo['text'].startswith('recall the reaction'):
            cell = [t for _, _, _, t in blocks if '{{lo ' + k + '}}' in t]
            if cell and '{{rxn-in' not in cell[0]:
                fail(f'LO {k} (how … is produced) has no {{{{rxn-in}}}} table in its md cell')
    raw = json.dumps(nb, ensure_ascii=False)
    if '#xref-missing-' in raw:
        fail(f'{raw.count("#xref-missing-")} unresolved link(s) in the built notebook')
    print(f'  {n} xrefs, {len(mine)} anchors')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    js = '--js' in sys.argv
    prefix = args[0] if args else 'ch01'
    nbp = sorted(COLAB.glob(f'{prefix}-*.ipynb'))[0]
    slug = nbp.stem
    chapter = int(prefix[2:])
    nb = json.loads(nbp.read_text(encoding='utf-8'))
    fails = []

    def fail(msg):
        fails.append(msg)
        print('  FAIL', msg)

    # 1. structure
    print('== structure')
    if nb.get('nbformat') != 4:
        fail('nbformat is not 4')
    ids = [c.get('id') for c in nb['cells']]
    if len(set(ids)) != len(ids) or None in ids:
        fail('cell ids missing or not unique')
    md_text, html_cells = [], []
    for c in nb['cells']:
        src = ''.join(c['source'])
        if c['cell_type'] == 'markdown':
            md_text.append(src)
            continue
        first = src.split('\n', 1)[0]
        if not first.startswith('# @title '):
            fail(f'{c["id"]}: first line is not a #@title form line')
        if c['metadata'].get('cellView') != 'form':
            fail(f'{c["id"]}: cellView is not form')
        outs = [o for o in c.get('outputs', []) if o.get('output_type') == 'display_data' and 'text/html' in o.get('data', {})]
        if not outs:
            fail(f'{c["id"]}: no pre-filled text/html output')
            continue
        page = ''.join(outs[0]['data']['text/html'])
        m = re.search(r'display\(HTML\(r"""(.*)"""\)\)\s*$', src, re.S)
        if not m or m.group(1) != page:
            fail(f'{c["id"]}: source HTML and pre-filled output differ')
        html_cells.append((c['id'], first[len('# @title '):].split(' {')[0], page))
    print(f'  {len(nb["cells"])} cells: {len(md_text)} markdown, {len(html_cells)} html')

    # 2. every learning outcome verbatim
    print('== learning outcomes')
    los, notes = load_los(chapter)
    unsup = dict(zip('0123456789+−', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻'))
    md_all = re.sub(r'<sup>([0-9+−]+)</sup>', lambda m: ''.join(unsup[c] for c in m.group(1)), '\n'.join(md_text))
    for k, lo in los.items():
        for piece in [lo['text']] + lo['subs']:
            if piece not in md_all:
                fail(f'LO {k} not verbatim in markdown: {piece[:60]}')
    for k, n in notes.items():
        if n not in md_all:
            fail(f'note {k} missing')
    print(f'  {len(los)} LOs, {len(notes)} notes checked')

    # 3. banned patterns
    print('== banned patterns')
    everything = md_all + '\n'.join(p for _, _, p in html_cells)
    for pat, why in [(r'```tikz', 'tikz block'), ('𝑙', 'italic l glyph'),
                     (r'<img[^>]+src="(?!data:|https?:)', 'relative image path'),
                     (r'!\[[^\]]*\]\((?!https?:)', 'markdown image (data: URIs untested in Colab markdown)')]:
        hits = re.findall(pat, everything)
        if hits:
            fail(f'{why}: {len(hits)} hit(s)')
    for i, t in enumerate(md_text):
        for ln in t.splitlines():
            if re.search(r'(?<!\$)\$\$(?!\$)', ln):
                fail(f'md cell {i}: $$')
    print('  done')

    if '--xref' in sys.argv or 13 <= chapter <= 21:
        check_xref(prefix, nb, fail)

    # 4. preview pages
    tmp = Path(os.environ.get('COLAB_TMP', Path(tempfile.gettempdir()) / 'colab')) / slug
    tmp.mkdir(parents=True, exist_ok=True)
    head = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>{t}</title></head><body style="margin:12px;background:#eee">'
    for cid, title, page in html_cells:
        (tmp / f'cell-{cid}.html').write_text(head.format(t=title) + page + '</body></html>', encoding='utf-8')
    (tmp / 'all.html').write_text(head.format(t=slug) + '\n'.join(
        f'<h2 style="font:600 15px system-ui;margin:22px 0 4px">{cid} · {title}</h2>{page}' for cid, title, page in html_cells)
        + '</body></html>', encoding='utf-8')
    print(f'== previews → {tmp}')

    # 5. headless JS error scan
    if js:
        print('== JS errors (headless)')
        exe = chrome()
        for cid, title, _ in html_cells:
            f = tmp / f'cell-{cid}.html'
            r = subprocess.run([exe, '--headless', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--enable-logging=stderr', '--v=0',
                                '--virtual-time-budget=8000', '--dump-dom', f.resolve().as_uri()],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
            errs = [l for l in r.stderr.splitlines() if 'Uncaught' in l or ('CONSOLE' in l and 'rror' in l)]
            state = re.search(r'data-3d="(\w+)"', r.stdout)
            tag = f' [3d: {state.group(1)}]' if state else ''
            if errs:
                fail(f'{cid} {title}: ' + ' | '.join(e.strip()[-200:] for e in errs))
            else:
                print(f'  ok   {cid} {title}{tag}')

    print('== result:', 'PASS' if not fails else f'FAIL ({len(fails)})')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
