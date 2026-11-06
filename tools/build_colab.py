"""Build colab/src/chNN-*.md into colab/chNN-*.ipynb (standard library only).

Source format — a cell starts at a marker line:
  <!-- md -->                markdown cell
  <!-- html: title -->       interactive cell (HTML + <style> + <script>), 2D, zero dependencies
  <!-- html3d: title -->     same, plus colab/kit/kit3d.js (three.js from jsDelivr)
  <!-- practice: title -->   past-paper block in a mini markdown, rendered to an html cell

Directives:
  {{lo 1.1.5}}        learning outcome, verbatim from reference.md (md: blockquote, html: .lo box)
  {{lo-note 1.3}}     the italic scope note that heads a syllabus subsection
  {{lo-checklist}}    (alone in an md slot) interactive checklist of every LO of the chapter
  {{img path [w]}}    image as a data: URI (path relative to the repo root), html/practice only
  {{cell name}}       (alone in an html / html3d slot) the cell body lives in colab/src/chNN/name.html;
                      while that file does not exist yet the notebook gets a "待合并" placeholder card,
                      so the skeleton builds before the cells are written
  {{xref ch15#sn2 text}} / {{xref #sn2 text}}
                      link to the cell anchored #sn2 (in ch15 / in this notebook): a Colab Drive URL
                      with #scrollTo=<cell id>; ids from colab/drive-ids.json
  {{rxn-in X}} / {{rxn-out X}}   (md) table of the reactions that make / use compound class X,
                      from colab/data/organic.json, each with a link to the cell that details it
  {{org-nav}}         (md) ch13–ch21 navigation line + this chapter's neighbours in the registry
  {{chemfig \\chemfig{...}}}  (html / practice) inline SVG via tools/chemfig2svg.py
  {{mol3d name}}      (html3d, inside <script>) colab/data/mol/name.sdf as a K3.molecule spec literal

A marker may end in an anchor, '<!-- md #sn2 -->' or '<!-- html: title #sn2-mech -->': the cell id is
then 'ch15-sn2' instead of the position-based 'ch15-07', so links to it survive inserting cells.
A cell whose body uses KO. gets colab/kit/kitorg.js (organic structures / curly arrows) inlined.

Cells are written, tested and reviewed one at a time, then merged (see colab/PLAN.md 每章流程):
  python tools/build_colab.py ch02 --cell beams      one cell → $COLAB_TMP/cells/ch02-beams.html

Every html cell becomes a Colab form cell: '#@title' + display(HTML(r\"\"\"...\"\"\")) with the
rendered HTML pre-filled as a display_data output, so the notebook shows its figures without
running anything. (%%html cannot be used: a cell magic must be the first line, and '#@title'
must be too.)

usage: python tools/build_colab.py ch01 [ch02 ...]
       python tools/build_colab.py ch02 --cell NAME [--3d]
"""
import base64
import html
import json
import mimetypes
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COLAB = ROOT / 'colab'
KIT = COLAB / 'kit'

MARK = re.compile(r'^<!-- (md|html|html3d|practice)(?::\s*(.*?))?(?:\s+#([a-z][\w-]*))?\s*-->\s*$')
CELL = re.compile(r'^\s*\{\{cell\s+([\w-]+)\}\}\s*$')
PAGE = ('<!DOCTYPE html><html><head><meta charset="utf-8"><title>{t}</title></head>'
        '<body style="margin:12px;background:#eee">\n{b}\n</body></html>\n')


def cell_file(slug, name):
    return COLAB / 'src' / slug[:4] / f'{name}.html'


def cell_body(slug, text, title):
    """html slot text → body; resolves {{cell name}} to colab/src/chNN/name.html or a placeholder"""
    m = CELL.match(text.strip())
    if not m:
        return text
    f = cell_file(slug, m.group(1))
    if f.exists():
        return f.read_text(encoding='utf-8')
    return (f'<h3>{html.escape(title or m.group(1))}</h3><p class="faint">待合并：'
            f'<code>colab/src/{slug[:4]}/{m.group(1)}.html</code> 还没写好</p>')


# ---------------------------------------------------------------- reference.md

def load_los(chapter):
    """{'1.1.1': {'text':…, 'subs':[…], 'extra':[…]}, …} plus {'1.3': note} for chapter N."""
    lines = (ROOT / 'reference.md').read_text(encoding='utf-8').splitlines()
    los, notes, sec, cur, in_fence, in_ch = {}, {}, None, None, False, False
    for ln in lines:
        m = re.match(r'^## (\d+) ', ln)
        if m:
            in_ch = int(m.group(1)) == chapter
            continue
        if not in_ch:
            continue
        m = re.match(r'^### (\d+\.\d+) ', ln)
        if m:
            sec, cur = m.group(1), None
            continue
        if sec is None:
            continue
        if ln.strip().startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r'^> (.*)$', ln)
        if m and cur is None:
            notes[sec] = m.group(1)
            continue
        m = re.match(r'^(\d+)\. (.*)$', ln)
        if m:
            cur = f'{sec}.{m.group(1)}'
            los[cur] = {'text': m.group(2), 'subs': [], 'extra': [], 'parts': []}
            continue
        # 'parts' keeps source order: '(b) …' lines can come before the bullets that belong to them (3.6.1),
        # and '     - ' bullets nest under the previous bullet (3.4.1(a)'s molecule list)
        m = re.match(r'^     - (.*)$', ln)
        if m and cur and los[cur]['parts'] and los[cur]['parts'][-1]['kind'] == 'sub':
            los[cur]['parts'][-1]['kids'].append(m.group(1))
            los[cur]['extra'].append(ln.strip())
            continue
        m = re.match(r'^   - (.*)$', ln)
        if m and cur:
            los[cur]['subs'].append(m.group(1))
            los[cur]['parts'].append({'kind': 'sub', 'text': m.group(1), 'kids': []})
            continue
        if ln.startswith('   ') and ln.strip() and cur:
            los[cur]['extra'].append(ln.strip())
            los[cur]['parts'].append({'kind': 'extra', 'text': ln.strip()})
    return los, notes


# ---------------------------------------------------------------- inline helpers

def data_uri(rel):
    p = (ROOT / rel).resolve()
    mime = mimetypes.guess_type(p.name)[0] or 'image/png'
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()


DRIVE = 'https://colab.research.google.com/drive/'
MISSING = []          # xref targets without a Drive id / anchor (check_colab --xref fails on them)


def drive_ids():
    f = COLAB / 'drive-ids.json'
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}


def nb_name(prefix):
    """'ch15' → 'ch15-halogen-compounds.ipynb' (from colab/src)"""
    src = sorted((COLAB / 'src').glob(f'{prefix}-*.md'))
    return src[0].stem + '.ipynb' if src else None


def xref_url(here, ch, anchor, html_cell=False):
    """here: this notebook's prefix; ch: target prefix or None (= here)"""
    ch = ch or here
    if ch == here and not html_cell:
        return f'#scrollTo={ch}-{anchor}'
    nid = drive_ids().get(nb_name(ch) or '')
    if not nid:
        MISSING.append(f'{ch}#{anchor}')
        return f'#xref-missing-{ch}-{anchor}'
    return f'{DRIVE}{nid}#scrollTo={ch}-{anchor}' if anchor else f'{DRIVE}{nid}'


_ORG = None


def organic():
    global _ORG
    if _ORG is None:
        f = COLAB / 'data' / 'organic.json'
        _ORG = json.loads(f.read_text(encoding='utf-8')) if f.exists() else {'classes': {}, 'reactions': []}
    return _ORG


def split_home(h):
    """'ch16#rx-oxidation' → ('ch16', 'rx-oxidation')"""
    ch, _, a = h.partition('#')
    return ch, a


def rxn_table(here, cls, way):
    org = organic()
    C = org['classes']
    if cls not in C:
        raise ValueError(f'rxn-{way}: unknown class {cls}')
    key = 'to' if way == 'in' else 'from'
    rows = [r for r in org['reactions'] if cls in (r[key] if isinstance(r[key], list) else [r[key]])]
    if not rows:
        raise ValueError(f'rxn-{way} {cls}: no reactions in the registry')
    other = 'from' if way == 'in' else 'to'
    head = ('| 起点 | reaction | reagents and conditions | LO | 详见 |' if way == 'in'
            else '| 产物 | reaction | reagents and conditions | LO | 详见 |')
    out = [head, '|---|---|---|---|---|']
    for r in rows:
        ends = r[other] if isinstance(r[other], list) else [r[other]]
        names = ', '.join(C[e]['name'] for e in ends)
        kind = r.get('mech') or r.get('type', '')
        kind = '' if kind == r['name'] else kind
        ch, a = split_home(r['home'])
        label = f'{ch} {r["home_title"]}' if r.get('home_title') else ch
        link = f'[{label} →]({xref_url(here, ch, a)})'
        out.append(f'| {names} | {r["name"]}' + (f'<br>{kind}' if kind else '') +
                   f' | {r["reagents"]} | {" · ".join(r["los"])} | {link} |')
    return '\n'.join(out)


ORG_CH = [(13, 'Intro'), (14, 'Hydrocarbons'), (15, 'Halogen compounds'), (16, 'Hydroxy compounds'),
          (17, 'Carbonyl compounds'), (18, 'Carboxylic acids'), (19, 'Nitrogen compounds'),
          (20, 'Polymerisation'), (21, 'Synthesis')]


def org_nav(here):
    n = int(here[2:])
    items = []
    for c, t in ORG_CH:
        p = f'ch{c}'
        items.append(f'**{c} {t}**' if p == here else f'[{c} {t}]({xref_url(here, p, "")})')
    org = organic()
    C = org['classes']
    mine = {k for k, v in C.items() if v.get('ch') == n}
    def chs(rs, side):
        s = set()
        for r in rs:
            for e in (r[side] if isinstance(r[side], list) else [r[side]]):
                if e in C and C[e].get('ch') not in (None, n):
                    s.add(C[e]['ch'])
        return sorted(s)
    def ends(r, k):
        return set(r[k] if isinstance(r[k], list) else [r[k]])
    came = chs([r for r in org['reactions'] if ends(r, 'to') & mine], 'from')
    goes = chs([r for r in org['reactions'] if ends(r, 'from') & mine], 'to')
    line = '🧭 Organic：' + ' · '.join(items)
    if came or goes:
        def lk(cs):
            return '、'.join(f'[ch{c}]({xref_url(here, f"ch{c}", "")})' for c in cs) or '—'
        line += f'\n\n本章的 compounds 从 {lk(came)} 来，又变成 {lk(goes)} 里的 compounds。'
    return line


def chemfig_spans(text):
    """yield (start, end, chemfig source) for every {{chemfig ...}} (braces nest)"""
    i = 0
    while True:
        i = text.find('{{chemfig ', i)
        if i < 0:
            return
        j, depth = i + 2, 0
        while j < len(text):
            if text[j] == '{':
                depth += 1
            elif text[j] == '}':
                if depth == 0:
                    break
                depth -= 1
            j += 1
        if not text.startswith('}}', j):
            raise ValueError('unclosed {{chemfig')
        yield i, j + 2, text[i + len('{{chemfig '):j].strip()
        i = j + 2


def expand_chemfig(text):
    spans = list(chemfig_spans(text))
    if not spans:
        return text
    sys.path.insert(0, str(ROOT / 'tools'))
    from chemfig2svg import render
    out, last = [], 0
    for n, (a, b, src) in enumerate(spans):
        out.append(text[last:a]); out.append(render(src, f'cf{n}')); last = b
    return ''.join(out) + text[last:]


def sdf_spec(name):
    """V2000 molfile → {atoms:[{el,p}], bonds:[[i,j,order]]} (coordinates in Å, centred)"""
    ls = (COLAB / 'data' / 'mol' / f'{name}.sdf').read_text(encoding='utf-8').splitlines()
    na, nb = int(ls[3][:3]), int(ls[3][3:6])
    atoms = []
    for ln in ls[4:4 + na]:
        x, y, z, el = float(ln[:10]), float(ln[10:20]), float(ln[20:30]), ln[31:34].strip()
        atoms.append([el, x, y, z])
    cx, cy, cz = (sum(a[k] for a in atoms) / na for k in (1, 2, 3))
    bonds = [[int(ln[:3]) - 1, int(ln[3:6]) - 1, int(ln[6:9])] for ln in ls[4 + na:4 + na + nb]]
    return json.dumps({'atoms': [{'el': a[0], 'p': [round(a[1] - cx, 3), round(a[2] - cy, 3), round(a[3] - cz, 3)]}
                                 for a in atoms], 'bonds': bonds}, separators=(',', ':'))


NUC = re.compile(r'\$\^\{([^}]*)\}_\{([^}]*)\}\\text\{([^}]*)\}\$')


def inline_html(s):
    """markdown-ish inline → HTML for html cells (no KaTeX there)."""
    s = NUC.sub(lambda m: f'<span class="nuc"><sup>{m.group(1)}</sup><sub>{m.group(2)}</sub></span>{m.group(3)}', s)
    s = re.sub(r'\$\^\{([^}]*)\}\$', r'<sup>\1</sup>', s)
    if '$' in s:
        raise ValueError(f'unsupported $…$ in an html cell: {s!r}')
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    # ASCII-only word boundaries: *A*ᵣ (ᵣ is a Unicode letter) and 18*x* (digit before) must still italicise
    s = re.sub(r'(?<![A-Za-z*])\*(?!\s)(.+?)(?<!\s)\*(?![A-Za-z0-9*])', r'<i>\1</i>', s)
    s = re.sub(r'\[\[([^\]]+)\]\]', lambda m: f'<input class="fill" data-ans="{html.escape(m.group(1))}">', s)
    s = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)(?:\{width=(\d+)\})?',
               lambda m: f'<img alt="{html.escape(m.group(1))}" src="{data_uri(m.group(2))}"'
                         + (f' width="{m.group(3)}"' if m.group(3) else '') + '>', s)
    return s


def lo_md(los, key):
    lo = los[key]
    out = [f'> **LO {key}** — {lo["text"]}']
    prev = 'text'
    for p in lo['parts']:
        if p['kind'] == 'sub':
            out.append(('>\n' if prev == 'extra' else '') + f'> - {p["text"]}')
            out += [f'>   - {k}' for k in p['kids']]
        elif not p['text'].startswith('e.g. for Fe:'):
            out.append(f'>\n> {p["text"]}')
        prev = p['kind']
    return '\n'.join(out)


def lo_extra_html(e):
    """an LO continuation line: '(b) …' is a sub-part (normal text); '> …' is a syllabus note (faint italic)"""
    if e.startswith('> '):
        return f'<span class="faint"><i>{inline_html(e[2:])}</i></span>'
    if re.match(r'^\([a-z]\) ', e):
        return inline_html(e)
    return f'<span class="faint">{inline_html(e)}</span>'


def lo_html(los, key):
    lo = los[key]
    return f'<div class="lo"><b>LO {key}</b> — {inline_html(lo["text"])}' + lo_parts_html(lo) + '</div>'


def lo_parts_html(lo):
    """bullets and continuation lines in source order; consecutive bullets share one <ul>"""
    out, ul = [], []

    def close():
        if ul:
            out.append('<ul>' + ''.join(ul) + '</ul>'); ul.clear()
    for p in lo['parts']:
        if p['kind'] == 'sub':
            kids = ''.join(f'<li>{inline_html(k)}</li>' for k in p['kids'])
            ul.append(f'<li>{inline_html(p["text"])}' + (f'<ul>{kids}</ul>' if kids else '') + '</li>')
        elif not p['text'].startswith('e.g. for Fe:'):
            close(); out.append(f'<br>{lo_extra_html(p["text"])}')
    close()
    return ''.join(out)


def directives(text, los, notes, kind, here=None):
    if here:
        text = re.sub(r'\{\{xref\s+(ch\d\d)?#([\w-]+)(?:\s+([^}]*?))?\s*\}\}',
                      lambda m: (f'[{m.group(3) or m.group(1) or "→"}]({xref_url(here, m.group(1), m.group(2))})'
                                 if kind == 'md' else
                                 f'<a class="xref" href="{xref_url(here, m.group(1), m.group(2), True)}" target="_blank" '
                                 f'rel="noopener">{inline_html(m.group(3) or m.group(1) or "→")}</a>'), text)
        if kind == 'md':
            text = re.sub(r'\{\{rxn-(in|out)\s+([\w-]+)\}\}', lambda m: rxn_table(here, m.group(2), m.group(1)), text)
            text = text.replace('{{org-nav}}', org_nav(here)) if '{{org-nav}}' in text else text
        elif re.search(r'\{\{(rxn-|org-nav)', text):
            raise ValueError('{{rxn-…}} / {{org-nav}} are for md cells only')
        text = re.sub(r'\{\{mol3d\s+([\w-]+)\}\}', lambda m: sdf_spec(m.group(1)), text)
    if '{{chemfig ' in text:
        if kind == 'md':
            raise ValueError('{{chemfig}} is for html cells only (inline SVG in Colab markdown is untested)')
        text = expand_chemfig(text)

    def rep(m):
        name, arg = m.group(1), (m.group(2) or '').strip()
        if name == 'lo':
            return lo_md(los, arg) if kind == 'md' else lo_html(los, arg)
        if name == 'lo-note':
            return f'> *{notes[arg]}*' if kind == 'md' else f'<p class="faint"><i>{inline_html(notes[arg])}</i></p>'
        if name == 'img':
            if kind == 'md':
                raise ValueError('{{img}} is for html cells only (markdown data: URIs are not trusted in Colab)')
            m2 = re.match(r'(.+?)(?:\s+(\d+))?$', arg)   # path may contain spaces; optional width last
            w = f' width="{m2.group(2)}"' if m2.group(2) else ''
            return f'<img src="{data_uri(m2.group(1))}"{w} alt="">'
        raise ValueError(f'unknown directive {name}')
    return re.sub(r'\{\{(lo-note|lo|img)\s+([^}]*)\}\}', rep, text)


# ---------------------------------------------------------------- practice mini-markdown

def split_row(row):
    """split a table row on '|', except '\\|' and the '|' between alternative answers inside [[a|b]]"""
    cells, cur, depth, i = [], '', 0, 0
    while i < len(row):
        if row.startswith('[[', i):
            depth += 1; cur += '[['; i += 2; continue
        if row.startswith(']]', i) and depth:
            depth -= 1; cur += ']]'; i += 2; continue
        if row.startswith('\\|', i):
            cur += '\\|'; i += 2; continue
        if row[i] == '|' and not depth:
            cells.append(cur); cur = ''; i += 1; continue
        cur += row[i]; i += 1
    cells.append(cur)
    return cells


def practice_html(text):
    out, para, i = [], [], 0
    lines = text.strip('\n').splitlines()
    open_q = False

    def flush():
        if para:
            out.append('<p>' + inline_html(' '.join(para)) + '</p>')
            para.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush(); i += 1; continue
        m = re.match(r'^(#{3,4}) (.*?)(?: (\[\d+\]))?$', s)
        if m:
            flush()
            if m.group(1) == '###':
                if open_q:
                    out.append('</div>'); open_q = False
                out.append(f'<h3>{inline_html(m.group(2))}</h3>')
            else:
                if open_q:
                    out.append('</div>')
                mark = f' <span class="mark">{m.group(3)}</span>' if m.group(3) else ''
                out.append(f'<div class="q"><h4>{inline_html(m.group(2))}{mark}</h4>')
                open_q = True
            i += 1; continue
        if s.startswith('::: answer'):
            flush()
            label = s[len('::: answer'):].strip() or '答案'
            out.append(f'<button class="reveal">{html.escape(label)}</button><div class="ans">')
            i += 1; continue
        if s == ':::':
            flush(); out.append('</div>'); i += 1; continue
        if s.startswith('|'):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = split_row(lines[i].strip().strip('|'))
                rows.append([c.strip().replace('\\|', '|') for c in cells]); i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r':?-+:?', c) for c in r)]
            t = '<table><tr>' + ''.join(f'<th>{inline_html(c)}</th>' for c in head) + '</tr>'
            t += ''.join('<tr>' + ''.join(f'<td>{inline_html(c)}</td>' for c in r) + '</tr>' for r in body)
            out.append(t + '</table>'); continue
        if re.match(r'^[-*] ', s):
            flush()
            items = []
            while i < len(lines) and re.match(r'^\s*[-*] ', lines[i]):
                items.append(re.sub(r'^\s*[-*] ', '', lines[i]))
                i += 1
                while i < len(lines) and lines[i].startswith('  ') and lines[i].strip() and not re.match(r'^\s*[-*] ', lines[i]):
                    items[-1] += ' ' + lines[i].strip(); i += 1
            out.append('<ul>' + ''.join(f'<li>{inline_html(x)}</li>' for x in items) + '</ul>'); continue
        if s.startswith('<'):
            flush(); out.append(s); i += 1; continue
        para.append(s); i += 1
    flush()
    if open_q:
        out.append('</div>')
    return '\n'.join(out)


# ---------------------------------------------------------------- html cell assembly

SCRIPT = re.compile(r'<script>(.*?)</script>', re.S)


def assemble(body, cid, three):
    kit_css = (KIT / 'kit.css').read_text(encoding='utf-8')
    kit_js = (KIT / 'kit.js').read_text(encoding='utf-8')
    scripts = SCRIPT.findall(body)
    body = SCRIPT.sub('', body).strip()
    parts = [f'<style>{kit_css}</style>', f'<div class="k" id="{cid}">\n{body}\n</div>', f'<script>{kit_js}</script>']
    if three:
        parts.append(f'<script>{(KIT / "kit3d.js").read_text(encoding="utf-8")}</script>')
    if re.search(r'\bKO\.', '\n'.join(scripts)) and (KIT / 'kitorg.js').exists():
        parts.append(f'<script>{(KIT / "kitorg.js").read_text(encoding="utf-8")}</script>')
    js = '\n'.join(scripts)
    parts.append(f'<script>(function($root){{\n{js}\nK.init($root);\n}})(document.getElementById("{cid}"));</script>')
    return '\n'.join(parts)


def checklist_body(los, key):
    secs = {}
    for k in los:
        secs.setdefault(k.rsplit('.', 1)[0], []).append(k)
    rows = []
    for sec, keys in secs.items():
        rows.append(f'<h4>{sec}</h4>')
        for k in keys:
            lo = los[k]
            rows.append(f'<label class="chk"><input type="checkbox" data-id="{k}"><span><b>{k}</b> '
                        f'{inline_html(lo["text"])}' + lo_parts_html(lo) + '</span></label>')
    return (f'<h3>Learning outcomes 自查 <span class="faint count"></span></h3>'
            f'<p class="faint">勾选会存在这个浏览器里（localStorage）；Colab 不允许时只在当前页面有效。</p>'
            f'<div class="lolist" data-key="{key}"><div class="bar"><i></i></div>' + '\n'.join(rows) + '</div>')


# ---------------------------------------------------------------- notebook

def lines_of(s):
    ls = s.split('\n')
    return [l + '\n' for l in ls[:-1]] + [ls[-1]]


SUP_MAP = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻', '0123456789+−'))
SUP_RUN = re.compile('[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+')


def md_sup(s):
    """Colab's markdown font (Google Sans) has only ¹²³ (Latin-1); ⁰ ⁴–⁹ fall back to another font, so
    10⁻²⁷ shows ² and ⁷ at different sizes. Every superscript run becomes <sup> (all from one font),
    except inside `code` spans, where <sup> would show literally (the mono font has all the glyphs)."""
    parts = re.split(r'(`[^`\n]*`)', s)
    return ''.join(p if p.startswith('`') else
                   SUP_RUN.sub(lambda m: '<sup>' + ''.join(SUP_MAP[c] for c in m.group(0)) + '</sup>', p)
                   for p in parts)


def md_cell(src, cid):
    return {'cell_type': 'markdown', 'id': cid, 'metadata': {'id': cid}, 'source': lines_of(md_sup(src.strip('\n')))}


def code_cell(title, page, cid):
    if '"""' in page or page.endswith('\\'):
        raise ValueError(f'cell {cid}: HTML cannot be embedded in a raw triple-quoted string')
    src = (f'# @title {title} {{ display-mode: "form" }}\n'
           'from IPython.display import HTML, display\n'
           f'display(HTML(r"""{page}"""))')
    return {'cell_type': 'code', 'execution_count': None, 'id': cid,
            'metadata': {'cellView': 'form', 'id': cid},
            'source': lines_of(src),
            'outputs': [{'output_type': 'display_data', 'metadata': {},
                         'data': {'text/html': lines_of(page), 'text/plain': ['<IPython.core.display.HTML object>']}}]}


def parse_blocks(src):
    """[(kind, title, anchor, text)] of a colab/src/chNN-*.md file"""
    blocks, kind, title, anchor, buf = [], None, None, None, []
    for ln in Path(src).read_text(encoding='utf-8').splitlines():
        m = MARK.match(ln)
        if m:
            if kind:
                blocks.append((kind, title, anchor, '\n'.join(buf)))
            kind, title, anchor, buf = m.group(1), m.group(2), m.group(3), []
        elif kind:
            buf.append(ln)
    if kind:
        blocks.append((kind, title, anchor, '\n'.join(buf)))
    return blocks


def build(slug_prefix):
    src = sorted((COLAB / 'src').glob(f'{slug_prefix}-*.md'))
    if not src:
        raise SystemExit(f'no colab/src/{slug_prefix}-*.md')
    src = src[0]
    slug = src.stem
    chapter = int(re.match(r'ch(\d+)', slug).group(1))
    los, notes = load_los(chapter)

    blocks = parse_blocks(src)
    here = slug[:4]
    seen = set()
    cells = []
    for n, (kind, title, anchor, text) in enumerate(blocks, 1):
        cid = f'{here}-{anchor}' if anchor else f'{here}-{n:02d}'
        if cid in seen:
            raise SystemExit(f'duplicate cell id {cid}')
        seen.add(cid)
        if kind == 'md' and text.strip() == '{{lo-checklist}}':
            page = assemble(checklist_body(los, slug[:4]), 'k-' + cid, False)
            cells.append(code_cell('✅ Learning outcomes 自查清单', page, cid))
        elif kind == 'md':
            cells.append(md_cell(directives(text, los, notes, 'md', here), cid))
        elif kind == 'practice':
            body = practice_html(directives(text, los, notes, 'html', here))
            cells.append(code_cell('📝 ' + title, assemble(body, 'k-' + cid, False), cid))
        else:
            body = directives(cell_body(slug, text, title), los, notes, 'html', here)
            cells.append(code_cell(('🧊 ' if kind == 'html3d' else '🔬 ') + title,
                                   assemble(body, 'k-' + cid, kind == 'html3d'), cid))

    nb = {'nbformat': 4, 'nbformat_minor': 5,
          'metadata': {'colab': {'provenance': [], 'toc_visible': True, 'name': slug + '.ipynb'},
                       'kernelspec': {'name': 'python3', 'display_name': 'Python 3'},
                       'language_info': {'name': 'python'}},
          'cells': cells}
    out = COLAB / f'{slug}.ipynb'
    out.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(f'{out.relative_to(ROOT)}: {len(cells)} cells, {out.stat().st_size // 1024} KB'
          + (f'  ({len(MISSING)} xref without Drive id: {", ".join(sorted(set(MISSING))[:6])}…)' if MISSING else ''))
    MISSING.clear()


def build_cell(slug_prefix, name, three):
    """one cell as a standalone preview page, for writing / testing / review before it is merged"""
    src = sorted((COLAB / 'src').glob(f'{slug_prefix}-*.md'))
    slug = src[0].stem if src else slug_prefix
    f = cell_file(slug, name)
    if not f.exists():
        raise SystemExit(f'no {f.relative_to(ROOT)}')
    los, notes = load_los(int(re.match(r'ch(\d+)', slug).group(1)))
    body = directives(f.read_text(encoding='utf-8'), los, notes, 'html', slug[:4])
    out = Path(os.environ.get('COLAB_TMP', '/tmp/colab')) / 'cells' / f'{slug[:4]}-{name}.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(PAGE.format(t=name, b=assemble(body, f'k-{slug[:4]}-{name}', three)), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    args = sys.argv[1:] or ['ch01']
    if '--cell' in args:
        i = args.index('--cell')
        build_cell(args[0], args[i + 1], '--3d' in args)
    else:
        for arg in args:
            build(arg)
