"""Mechanical checks for colab/chNN-*.ipynb, plus preview pages and a headless JS error scan.

usage: python tools/check_colab.py ch01 [--js]
  writes $COLAB_TMP/<slug>/cell-<id>.html (one per html cell) and all.html (every html cell stacked)
  --js  load every preview page in headless Chrome/Chromium and report uncaught errors

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
from build_colab import ROOT, COLAB, load_los  # noqa: E402

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
