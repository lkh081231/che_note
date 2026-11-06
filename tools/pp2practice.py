"""Past-paper bank → practice blocks for a colab chapter source (standard library only).

Collects every sub-question tagged '· chNN' in passyear/extracted/ch*/9701_*.md (mirrors are
deduplicated by paper + question + part), keeps the stem headings and figures above it so the part
reads on its own, and prints colab practice blocks in exam order (Feb/Mar → May/June → Oct/Nov,
2024 → 2026):

  <!-- practice: 9701/22 May/June 2026 -->
  ### 9701/22 May/June 2026
  #### Q4(a)(i) [1]
  …question…
  ::: answer
  **答案** — …
  **判分** — …
  :::

The output is a starting point: paste it into colab/src/chNN-*.md, then trim stems and add
[[fill-ins]] by hand.

usage: python tools/pp2practice.py ch16 [> scratch.md]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / 'passyear' / 'extracted'
SESS = {'m': (0, 'Feb/Mar'), 's': (1, 'May/June'), 'w': (2, 'Oct/Nov')}
SUB = re.compile(r'^### (\([a-z]\)(?:\([ivx]+\))?(?:\([a-z0-9]+\))?) \[(\d+)\] · (.*)$')
STEM = re.compile(r'^### (\([a-z]\)(?:\([ivx]+\))?) (?!\[)(.*)$')


def latex_plain(s):
    """the bank has a handful of $…$ (html cells have no KaTeX)"""
    def one(m):
        t = m.group(1)
        t = re.sub(r'\\d?frac\{([^{}]*)\}\{([^{}]*)\}', r'(\1)/(\2)', t)
        return t.replace('\\times', '×').replace('\\', '')
    return re.sub(r'\$([^$]+)\$', one, s)


def parts(path, chap):
    """[(qkey, part, marks, [lines])] for parts of this file tagged chap"""
    out, q, stems, cur = [], None, {}, None
    imgdir = path.parent.relative_to(ROOT).as_posix() + '/img/'
    for ln in path.read_text(encoding='utf-8').splitlines():
        ln = ln.replace('](img/', '](' + imgdir)
        m = re.match(r'^## (Q\d+) ', ln)
        if m:
            q, stems, cur = m.group(1), {}, None
            continue
        if q is None or ln.startswith('# ') or ln.strip() == '---':
            continue
        if ln.startswith('> 正本在') or ln.startswith('> 本题正本'):
            continue
        m = SUB.match(ln)
        if m:
            tags = m.group(3).split()
            cur = None
            if chap in tags:
                ctx = [l for k, ls in stems.items() if m.group(1).startswith(k) for l in ls]
                cur = (q, m.group(1), int(m.group(2)), ctx, [])
                out.append(cur)
            continue
        m = STEM.match(ln)
        if m:
            key = m.group(1)
            stems = {k: v for k, v in stems.items() if key.startswith(k) and k != key}
            stems[key] = [m.group(2)]
            cur = ('stem', key)
            continue
        if cur and cur[0] == 'stem':
            stems[cur[1]].append(ln)
        elif cur:
            cur[4].append(ln)
    return out


def paper_key(stem):
    m = re.match(r'9701_([msw])(\d\d)_(\d\d)$', stem)
    return (int(m.group(2)), SESS[m.group(1)][0], m.group(3)), \
        f'9701/{m.group(3)} {SESS[m.group(1)][1]} 20{m.group(2)}'


def block(q, part, marks, ctx, body, shown):
    """shown: stems already printed for this question (a shared stem is printed once)"""
    lines = []
    new = [l for l in ctx if l.strip()]
    if new and (q, tuple(new)) not in shown:
        shown.add((q, tuple(new)))
        lines += new + ['']
    lines.append(f'#### {q}{part} [{marks}]')
    ans, inans = [], False
    for l in body:
        if l.startswith('**答案**') or l.startswith('**判分**'):
            inans = True
        if re.match(r'^\*\*\[Total', l.strip()):
            continue
        (ans if inans else lines).append(l)
    if ans:
        lines += ['::: answer'] + [a for a in ans] + [':::']
    return '\n'.join(latex_plain(x) for x in lines)


def main():
    chap = sys.argv[1] if len(sys.argv) > 1 else 'ch16'
    seen, papers = set(), {}
    for f in sorted(BANK.glob('ch*/9701_*.md')):
        for q, part, marks, ctx, body in parts(f, chap):
            k = (f.stem, q, part)
            if k in seen:
                continue
            seen.add(k)
            papers.setdefault(f.stem, []).append((q, part, marks, ctx, body))
    total = 0
    for stem in sorted(papers, key=lambda s: paper_key(s)[0]):
        title = paper_key(stem)[1]
        print(f'<!-- practice: {title} -->\n### {title}\n')
        shown = set()
        for q, part, marks, ctx, body in sorted(papers[stem], key=lambda t: (int(t[0][1:]), t[1])):
            print(re.sub(r'\n{3,}', '\n\n', block(q, part, marks, ctx, body, shown)) + '\n')
            total += marks
    print(f'<!-- {chap}: {len(seen)} parts, {total} marks, {len(papers)} papers -->', file=sys.stderr)


if __name__ == '__main__':
    main()
