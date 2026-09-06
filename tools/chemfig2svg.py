#!/usr/bin/env python3
"""
chemfig2svg.py — compile a practical subset of ChemFig source to inline SVG.

Why this exists: organic-reaction-roadmap.html is a single zero-dependency file, so it
cannot run LaTeX / TikZJax. Structures are authored in ChemFig — the same notation used
throughout this vault and the syllabus — and compiled here to plain SVG, so the ChemFig
source stays the thing we edit and review.

Supported subset (enough for AS display formulae):
  \\chemfig{...}           atoms, and - = ~ bonds (single / double / triple)
  [:angle]                absolute bond angle, degrees CCW from +x
  [:angle,len]            angle plus bond-length multiplier
  ( ... )                 branches
  ?  /  ?[a]              ring-closure labels
  X^{...}  X_{...}        super / subscripts, rendered as SVG tspan

CLI:
  python tools/chemfig2svg.py --src '\\chemfig{R-[:30]OH}' --id alcohol
  python tools/chemfig2svg.py --json formulae.json
  python tools/chemfig2svg.py --self-test
"""
import re, math, sys, json, argparse, io

BOND_LEN = 34.0          # px per unit bond
FONT     = 13.0
ATOM_PAD = 7.0           # gap between bond end and atom glyph


class Atom:
    __slots__ = ('label', 'x', 'y', 'idx')

    def __init__(self, label, x, y, idx):
        self.label, self.x, self.y, self.idx = label, x, y, idx


class Bond:
    __slots__ = ('a', 'b', 'order')

    def __init__(self, a, b, order):
        self.a, self.b, self.order = a, b, order


TOKEN = re.compile(r"""
    (?P<open>\()
  | (?P<close>\))
  | (?P<bond>[-=~])
  | (?P<opt>\[[^\]]*\])
  | (?P<ring>\?(?:\[[^\]]*\])?)
  | (?P<atom>[A-Za-z][A-Za-z0-9]*(?:\^\{[^}]*\}|_\{[^}]*\})*|\{[^}]*\})
  | (?P<space>\s+)
""", re.X)


def parse(src):
    """ChemFig source -> (atoms, bonds) with absolute coordinates."""
    m = re.search(r'\\chemfig\s*\{(.*)\}\s*$', src.strip(), re.S)
    body = m.group(1) if m else src.strip()

    atoms, bonds, rings = [], [], {}
    stack = []
    cur = None          # index of current atom
    angle = 0.0         # current direction in degrees
    pending = None      # [order, angle, length-multiplier] for the next bond
    i = 0

    def place(label, frm, ang, lenmul):
        if frm is None:
            a = Atom(label, 0.0, 0.0, len(atoms))
            atoms.append(a)
            return a.idx
        p = atoms[frm]
        r = math.radians(ang)
        x = p.x + BOND_LEN * lenmul * math.cos(r)
        y = p.y - BOND_LEN * lenmul * math.sin(r)   # SVG y grows downward
        a = Atom(label, x, y, len(atoms))
        atoms.append(a)
        return a.idx

    while i < len(body):
        mt = TOKEN.match(body, i)
        if not mt:
            i += 1
            continue
        i = mt.end()
        kind, val = mt.lastgroup, mt.group()

        if kind == 'space':
            continue
        if kind == 'open':
            stack.append((cur, angle))
            continue
        if kind == 'close':
            cur, angle = stack.pop()
            continue
        if kind == 'bond':
            pending = [{'-': 1, '=': 2, '~': 3}[val], None, 1.0]
            continue
        if kind == 'opt':
            inner = val[1:-1]
            if pending is None:
                pending = [1, None, 1.0]
            if inner.startswith(':'):
                parts = inner[1:].split(',')
                pending[1] = float(parts[0])
                if len(parts) > 1 and parts[1].strip():
                    pending[2] = float(parts[1])
            elif inner.startswith(','):
                parts = inner.split(',')
                if len(parts) > 1 and parts[1].strip():
                    pending[2] = float(parts[1])
            continue
        if kind == 'ring':
            lbl = val[1:] or '?'
            if lbl in rings:
                bonds.append(Bond(rings[lbl], cur, 1))
            else:
                rings[lbl] = cur
            continue
        if kind == 'atom':
            label = val
            if label.startswith('{') and label.endswith('}'):
                label = label[1:-1]
            if pending is None:
                cur = place(label, None, 0, 1.0)
            else:
                order, ang, lm = pending
                if ang is None:
                    ang = angle
                nxt = place(label, cur, ang, lm)
                bonds.append(Bond(cur, nxt, order))
                cur, angle, pending = nxt, ang, None
            continue

    return atoms, bonds


SUP = re.compile(r'\^\{([^}]*)\}')
SUB = re.compile(r'_\{([^}]*)\}')


LATEX = {r'\prime': '′', r'\alpha': 'α', r'\beta': 'β',
         r'\delta': 'δ', r'\equiv': '≡', r'\cdot': '·'}


def esc(t):
    for k, v in LATEX.items():
        t = t.replace(k, v)
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def label_svg(lbl, x, y):
    """Atom label as an SVG <text>, honouring ^{} and _{} scripts."""
    body = esc(lbl)
    body = SUP.sub(lambda m: '<tspan baseline-shift="super" font-size="9">%s</tspan>' % m.group(1), body)
    body = SUB.sub(lambda m: '<tspan baseline-shift="sub" font-size="9">%s</tspan>' % m.group(1), body)
    return ('<text x="%.1f" y="%.1f" text-anchor="middle" dominant-baseline="central" '
            'class="cf-a">%s</text>' % (x, y, body))


def visible(lbl):
    """Plain carbon vertices are drawn implicitly, like ChemFig's skeleton mode."""
    return lbl not in ('', 'C')


def glyph_w(lbl):
    plain = re.sub(r'[_^]\{[^}]*\}', '', lbl)
    scripts = len(re.findall(r'[_^]\{[^}]*\}', lbl))
    return (len(plain) * 0.42 + scripts * 0.22) * FONT + ATOM_PAD


def render(src, sid='x', pad=14):
    atoms, bonds = parse(src)
    if not atoms:
        return ''

    def trim(a, b):
        """Shorten a bond so it stops clear of any drawn atom label."""
        dx, dy = b.x - a.x, b.y - a.y
        d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d
        wa = glyph_w(a.label) if visible(a.label) else 0
        wb = glyph_w(b.label) if visible(b.label) else 0
        # never trim away more than 55% of the bond, so short bonds stay visible
        room = d * 0.55
        if wa + wb > room:
            k = room / (wa + wb)
            wa, wb = wa * k, wb * k
        return a.x + ux * wa, a.y + uy * wa, b.x - ux * wb, b.y - uy * wb

    seg = []
    for bd in bonds:
        a, b = atoms[bd.a], atoms[bd.b]
        x1, y1, x2, y2 = trim(a, b)
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        offsets = {1: (0,), 2: (2.2, -2.2), 3: (3.2, 0, -3.2)}[bd.order]
        for s in offsets:
            seg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
                       % (x1 + nx * s, y1 + ny * s, x2 + nx * s, y2 + ny * s))

    txt = [label_svg(a.label, a.x, a.y) for a in atoms if visible(a.label)]

    xs = [a.x for a in atoms]
    ys = [a.y for a in atoms]
    extra = 18
    vx = min(xs) - pad - extra
    vy = min(ys) - pad - extra
    vw = (max(xs) - min(xs)) + 2 * (pad + extra)
    vh = (max(ys) - min(ys)) + 2 * (pad + extra)

    return ('<svg class="cf" viewBox="%.1f %.1f %.1f %.1f" width="%.0f" height="%.0f" '
            'role="img" data-cf="%s"><g class="cf-b">%s</g>%s</svg>'
            % (vx, vy, vw, vh, vw, vh, sid, ''.join(seg), ''.join(txt)))


def self_test():
    cases = {
        'alcohol':  r'\chemfig{R-[:30]OH}',
        'aldehyde': r'\chemfig{R-[:30]C(=[:90]O)-[:-30]H}',
        'ketone':   r'\chemfig{R-[:30]C(=[:90]O)-[:-30]R^{\prime}}',
        'acid':     r'\chemfig{R-[:30]C(=[:90]O)-[:-30]OH}',
        'nitrile':  r'\chemfig{R-[:30]C~[:-30]N}',
    }
    ok = True
    for k, v in cases.items():
        a, b = parse(v)
        svg = render(v, k)
        good = len(a) >= 2 and len(b) >= 1 and svg.startswith('<svg')
        print('  %-9s atoms=%2d bonds=%2d %s' % (k, len(a), len(b), 'OK' if good else 'FAIL'))
        ok = ok and good

    # geometry sanity: a [:30] bond must go right and UP (negative SVG y)
    a, _ = parse(r'\chemfig{R-[:30]OH}')
    dx, dy = a[1].x - a[0].x, a[1].y - a[0].y
    geo = dx > 0 and dy < 0
    print('  angle     dx=%+.1f dy=%+.1f %s' % (dx, dy, 'OK' if geo else 'FAIL'))

    # a double bond must emit two parallel lines
    two = render(r'\chemfig{C(=[:90]O)}').count('<line')
    print('  C=O lines=%d %s' % (two, 'OK' if two == 2 else 'FAIL'))
    return 0 if (ok and geo and two == 2) else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--src')
    ap.add_argument('--id', default='x')
    ap.add_argument('--self-test', action='store_true')
    ap.add_argument('--json', help='JSON map {id: chemfig} -> prints {id: svg}')
    g = ap.parse_args()

    if g.self_test:
        sys.exit(self_test())
    if g.json:
        m = json.loads(io.open(g.json, encoding='utf-8').read())
        print(json.dumps({k: render(v, k) for k, v in m.items()}, ensure_ascii=False))
    elif g.src:
        print(render(g.src, g.id))
