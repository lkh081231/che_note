#!/usr/bin/env python3
"""
chemfig2svg.py — compile a practical subset of ChemFig source to inline SVG.

Why this exists: organic-reaction-roadmap.html is a single zero-dependency file, so it
cannot run LaTeX / TikZJax. Structures are authored in ChemFig — the same notation used
throughout this vault and the syllabus — and compiled here to plain SVG, so the ChemFig
source stays the thing we edit and review.

Supported subset:
  \\chemfig{...}           atoms, and - = ~ bonds (single / double / triple)
  <  >  <:  >:            solid and hashed wedge bonds (cram)
  [:angle]                absolute bond angle, degrees CCW from +x
  [:angle,len]            angle plus bond-length multiplier
  [n]  [n,len]            relative angle in 45° increments (n × 45°)
  ( ... )                 branches
  @{name}                 named atom labels / implicit vertices
  ?  /  ?[a]              ring-closure labels
  X^{...}  X_{...}        super / subscripts (with unbraced shortcuts X_2, X^+)
  R'                      prime notation rendered as ′ (U+2032)
  data-atoms / data-bonds output attributes on root <svg> for KO (kitorg.js)

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
    __slots__ = ('label', 'x', 'y', 'idx', 'name', 'implicit')

    def __init__(self, label, x, y, idx, name=None, implicit=False):
        self.label, self.x, self.y, self.idx, self.name = label, x, y, idx, name
        self.implicit = implicit     # a skeletal vertex nobody wrote a letter for: drawn without a label


class Bond:
    __slots__ = ('a', 'b', 'order', 'kind')

    def __init__(self, a, b, order, kind='-'):
        self.a, self.b, self.order, self.kind = a, b, order, kind


TOKEN = re.compile(r"""
    (?P<open>\()
  | (?P<close>\))
  | (?P<name>@\{[^}]*\})
  | (?P<bond><:|>:|[-=~<>])
  | (?P<opt>\[[^\]]*\])
  | (?P<ring>\?(?:\[[^\]]*\])?)
  | (?P<atom>(?:[A-Za-z]|\\[A-Za-z]+)(?:[A-Za-z0-9']|\\'|\\[A-Za-z]+|\^\{[^}]*\}|_\{[^}]*\}|\^[0-9A-Za-z+-]|_[0-9A-Za-z+-]|\{[^}]*\})*|\{[^}]*\})
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
    pending = None      # [order, angle, length-multiplier, kind] for the next bond
    pending_name = None # pending atom name from @{name}
    i = 0

    def place(label, frm, ang, lenmul, name=None, implicit=False):
        lbl = (label or 'C').replace(r"\'", '′').replace("'", '′')
        if lbl.startswith('{') and lbl.endswith('}'):
            lbl = lbl[1:-1]
        if frm is None:
            a = Atom(lbl, 0.0, 0.0, len(atoms), name, implicit)
            atoms.append(a)
            return a.idx
        p = atoms[frm]
        r = math.radians(ang)
        x = p.x + BOND_LEN * lenmul * math.cos(r)
        y = p.y - BOND_LEN * lenmul * math.sin(r)   # SVG y grows downward
        a = Atom(lbl, x, y, len(atoms), name, implicit)
        atoms.append(a)
        return a.idx

    def resolve_pending(implicit_label='C'):
        nonlocal cur, angle, pending, pending_name
        if pending is None:
            if cur is None and pending_name is not None:
                cur = place(implicit_label, None, 0, 1.0, pending_name, True)
                pending_name = None
            return
        order, ang, lm, kind_str = pending
        if ang is None:
            ang = angle
        nxt = place(implicit_label, cur, ang, lm, pending_name, True)
        bonds.append(Bond(cur, nxt, order, kind_str))
        cur, angle, pending, pending_name = nxt, ang, None, None

    while i < len(body):
        mt = TOKEN.match(body, i)
        if not mt:
            i += 1
            continue
        i = mt.end()
        kind, val = mt.lastgroup, mt.group()

        if kind == 'space':
            continue
        if kind == 'name':
            pending_name = val[2:-1].strip()
            continue
        if kind == 'open':
            resolve_pending()
            stack.append((cur, angle))
            continue
        if kind == 'close':
            resolve_pending()
            cur, angle = stack.pop()
            continue
        if kind == 'bond':
            resolve_pending()
            if cur is None:
                cur = place('C', None, 0, 1.0, pending_name, True)
                pending_name = None
            if val == '-':
                order, kind_str = 1, '-'
            elif val == '=':
                order, kind_str = 2, '='
            elif val == '~':
                order, kind_str = 3, '~'
            elif val in ('<', '>'):
                order, kind_str = 'w', val
            elif val in ('<:', '>:'):
                order, kind_str = 'h', val
            else:
                order, kind_str = 1, '-'
            pending = [order, None, 1.0, kind_str]
            continue
        if kind == 'opt':
            inner = val[1:-1].strip()
            if pending is None:
                pending = [1, None, 1.0, '-']
            if inner.startswith(':'):
                parts = inner[1:].split(',')
                pending[1] = float(parts[0])
                if len(parts) > 1 and parts[1].strip():
                    pending[2] = float(parts[1])
            elif inner.startswith(','):
                parts = inner.split(',')
                if len(parts) > 1 and parts[1].strip():
                    pending[2] = float(parts[1])
            else:
                parts = inner.split(',')
                if parts[0].strip():
                    try:
                        pending[1] = float(parts[0].strip()) * 45.0
                    except ValueError:
                        pass
                if len(parts) > 1 and parts[1].strip():
                    try:
                        pending[2] = float(parts[1].strip())
                    except ValueError:
                        pass
            continue
        if kind == 'ring':
            lbl = val[1:] or '?'
            resolve_pending()
            if cur is None:                      # '?' before any atom: it marks an implicit first vertex
                cur = place('C', None, 0, 1.0, pending_name, True)
                pending_name = None
            if lbl in rings:
                bonds.append(Bond(rings[lbl], cur, 1, '-'))
            else:
                rings[lbl] = cur
            continue
        if kind == 'atom':
            label = val
            if pending is None:
                cur = place(label, None, 0, 1.0, pending_name)
                pending_name = None
            else:
                order, ang, lm, kind_str = pending
                if ang is None:
                    ang = angle
                nxt = place(label, cur, ang, lm, pending_name)
                bonds.append(Bond(cur, nxt, order, kind_str))
                cur, angle, pending, pending_name = nxt, ang, None, None
            continue

    resolve_pending()
    return atoms, bonds


SUP = re.compile(r'\^\{([^}]*)\}')
SUB = re.compile(r'_\{([^}]*)\}')


LATEX = {r'\prime': '′', r'\alpha': 'α', r'\beta': 'β',
         r'\delta': 'δ', r'\equiv': '≡', r'\cdot': '·'}


def esc(t):
    t = t.replace(r"\'", "′").replace("'", "′")
    for k, v in LATEX.items():
        t = t.replace(k, v)
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def normalize_scripts(t):
    t = re.sub(r'_([0-9A-Za-z])', r'_{\1}', t)
    t = re.sub(r'\^([0-9A-Za-z+-])', r'^{\1}', t)
    return t


def label_svg(lbl, x, y):
    """Atom label as an SVG <text>, honouring ^{} and _{} scripts."""
    body = esc(normalize_scripts(lbl))
    body = SUP.sub(lambda m: '<tspan baseline-shift="super" font-size="9">%s</tspan>' % m.group(1), body)
    body = SUB.sub(lambda m: '<tspan baseline-shift="sub" font-size="9">%s</tspan>' % m.group(1), body)
    return ('<text x="%.1f" y="%.1f" text-anchor="middle" dominant-baseline="central" '
            'class="cf-a">%s</text>' % (x, y, body))


def visible(atom):
    """Skeletal vertices (no letter written in the source) are drawn without a label; a C written
    out in a displayed formula is shown."""
    return not atom.implicit and atom.label != ''


def glyph_w(lbl):
    t = esc(normalize_scripts(lbl))
    plain = re.sub(r'[_^]\{[^}]*\}', '', t)
    scripts = len(re.findall(r'[_^]\{[^}]*\}', t))
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
        wa = glyph_w(a.label) if visible(a) else 0
        wb = glyph_w(b.label) if visible(b) else 0
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
        if bd.kind in ('-', '=', '~'):
            offsets = {1: (0,), 2: (2.2, -2.2), 3: (3.2, 0, -3.2)}[bd.order]
            for s in offsets:
                seg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
                           % (x1 + nx * s, y1 + ny * s, x2 + nx * s, y2 + ny * s))
        elif bd.kind in ('<', '>'):
            max_hw = 2.8
            if bd.kind == '<':
                p1x, p1y = x1, y1
                p2x, p2y = x2 + nx * max_hw, y2 + ny * max_hw
                p3x, p3y = x2 - nx * max_hw, y2 - ny * max_hw
            else:
                p1x, p1y = x2, y2
                p2x, p2y = x1 + nx * max_hw, y1 + ny * max_hw
                p3x, p3y = x1 - nx * max_hw, y1 - ny * max_hw
            seg.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="currentColor"/>'
                       % (p1x, p1y, p2x, p2y, p3x, p3y))
        elif bd.kind in ('<:', '>:'):
            max_hw = 2.8
            n_bars = 6
            for k in range(n_bars):
                t = (k + 1.0) / (n_bars + 1.0)
                cx = x1 + (x2 - x1) * t
                cy = y1 + (y2 - y1) * t
                hw = t * max_hw if bd.kind == '<:' else (1.0 - t) * max_hw
                seg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
                           % (cx + nx * hw, cy + ny * hw, cx - nx * hw, cy - ny * hw))

    txt = [label_svg(a.label, a.x, a.y) for a in atoms if visible(a)]

    xs = [a.x for a in atoms]
    ys = [a.y for a in atoms]
    extra = 18
    vx = min(xs) - pad - extra
    vy = min(ys) - pad - extra
    vw = (max(xs) - min(xs)) + 2 * (pad + extra)
    vh = (max(ys) - min(ys)) + 2 * (pad + extra)

    atoms_data = []
    for a in atoms:
        d = {
            "i": a.idx,
            "l": (a.label if a.label else "C").replace("'", "′").replace(r'\prime', "′"),
            "x": round(a.x, 1) if round(a.x, 1) != 0 else 0.0,
            "y": round(a.y, 1) if round(a.y, 1) != 0 else 0.0,
        }
        if a.name:
            d["n"] = a.name
        atoms_data.append(d)

    bonds_data = [[bd.a, bd.b, bd.order] for bd in bonds]

    atoms_attr = json.dumps(atoms_data, ensure_ascii=False, separators=(',', ':'))
    bonds_attr = json.dumps(bonds_data, ensure_ascii=False, separators=(',', ':'))

    return ('<svg class="cf" viewBox="%.1f %.1f %.1f %.1f" width="%.0f" height="%.0f" '
            'role="img" data-cf="%s" data-atoms=\'%s\' data-bonds=\'%s\'>'
            '<g class="cf-b">%s</g>%s</svg>'
            % (vx, vy, vw, vh, vw, vh, sid, atoms_attr, bonds_attr, ''.join(seg), ''.join(txt)))


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
    ok = ok and geo

    # a double bond must emit two parallel lines
    two = render(r'\chemfig{C(=[:90]O)}').count('<line')
    good_two = (two == 2)
    print('  C=O lines=%d %s' % (two, 'OK' if good_two else 'FAIL'))
    ok = ok and good_two

    # 1. relative angles [n] (n * 45 deg)
    a, _ = parse(r'\chemfig{C(-[2]H)(-[6]H)}')
    up_ok = abs(a[1].x - a[0].x) < 1e-4 and (a[1].y - a[0].y) < -30
    dn_ok = abs(a[2].x - a[0].x) < 1e-4 and (a[2].y - a[0].y) > 30
    rel_ok = up_ok and dn_ok and len(a) == 3
    print('  rel_ang   [2]=up [6]=dn %s' % ('OK' if rel_ok else 'FAIL'))
    ok = ok and rel_ok

    # 2. relative angles with len multiplier [n,len]
    a, _ = parse(r'\chemfig{C-[2,0.5]O}')
    len_ok = abs((a[1].y - a[0].y) - (-0.5 * BOND_LEN)) < 1e-4
    print('  rel_len   [2,0.5] len=%.1f %s' % (abs(a[1].y - a[0].y), 'OK' if len_ok else 'FAIL'))
    ok = ok and len_ok

    # 3. atom label with prime ' -> U+2032 and unbraced subscript _2
    svg_prime = render(r'''\chemfig{R-C(=[2]O)-R'}''', 'prime')
    prime_ok = 'R′' in svg_prime and "data-atoms='[{\"i\":0,\"l\":\"R\"" in svg_prime and "{\"i\":3,\"l\":\"R′\"" in svg_prime
    # Verify JSON attribute inside single quotes does not contain unescaped single quotes
    atoms_str = re.search(r"data-atoms='([^']*)'", svg_prime)
    no_sq = atoms_str is not None and "'" not in atoms_str.group(1)
    print('  prime     R\' -> R′ no-sq=%s %s' % (no_sq, 'OK' if prime_ok and no_sq else 'FAIL'))
    ok = ok and prime_ok and no_sq

    # 4. unbraced subscripts _2 in labels (e.g. NH_2, H_2N)
    svg_nh2 = render(r'\chemfig{R-NH_2}', 'nh2')
    sub_ok = '<tspan baseline-shift="sub" font-size="9">2</tspan>' in svg_nh2
    svg_h2n = render(r'\chemfig{H_2N-[:30]-[:-30]-[:30]}', 'h2n')
    sub_ok = sub_ok and '<tspan baseline-shift="sub" font-size="9">2</tspan>' in svg_h2n
    print('  sub_2     NH_2 / H_2N %s' % ('OK' if sub_ok else 'FAIL'))
    ok = ok and sub_ok

    # 5. named atoms @{name} and empty atoms @{name} for implicit C
    a, _ = parse(r'\chemfig{@{c1}C(-[2]H)=[:0]@{c2}C}')
    svg_named = render(r'\chemfig{@{c1}C(-[2]H)=[:0]@{c2}C}', 'named')
    name_ok = a[0].name == 'c1' and a[2].name == 'c2' and '"n":"c1"' in svg_named and '"n":"c2"' in svg_named
    a_empty, _ = parse(r'\chemfig{@{c1}-[:30]@{c2}}')
    empty_ok = len(a_empty) == 2 and a_empty[0].name == 'c1' and a_empty[1].name == 'c2' and a_empty[0].label == 'C'
    named_all = name_ok and empty_ok
    print('  named     @{c1}C @{c1} %s' % ('OK' if named_all else 'FAIL'))
    ok = ok and named_all

    # 6. wedge bonds < and >
    svg_w1 = render(r'\chemfig{C<[:30]OH}', 'w1')
    svg_w2 = render(r'\chemfig{C>[:30]OH}', 'w2')
    wedge_ok = '<polygon points=' in svg_w1 and '<polygon points=' in svg_w2
    wedge_ok = wedge_ok and '"w"' in svg_w1 and '"w"' in svg_w2
    print('  wedge     < and > solid %s' % ('OK' if wedge_ok else 'FAIL'))
    ok = ok and wedge_ok

    # 7. hashed wedge bonds <: and >:
    svg_h1 = render(r'\chemfig{C<:[:30]OH}', 'h1')
    svg_h2 = render(r'\chemfig{C>:[:30]OH}', 'h2')
    hashed_ok = svg_h1.count('<line') >= 6 and svg_h2.count('<line') >= 6
    hashed_ok = hashed_ok and '"h"' in svg_h1 and '"h"' in svg_h2
    print('  hashed    <: and >: %s' % ('OK' if hashed_ok else 'FAIL'))
    ok = ok and hashed_ok

    # 8. charges: ^{\delta+}, ^{+}, ^{-}
    svg_chg = render(r'\chemfig{C^{\delta+}-[:30]C^{-}}', 'chg')
    chg_ok = 'δ+' in svg_chg and '<tspan baseline-shift="super" font-size="9">δ+</tspan>' in svg_chg
    print('  charge    ^{\\delta+} delta=%s %s' % ('δ+' in svg_chg, 'OK' if chg_ok else 'FAIL'))
    ok = ok and chg_ok

    # ring closure starting with '?' (cyclohexane skeletal): 6 vertices, 6 bonds
    ra, rb = parse(r'\chemfig{?-[:30]-[:-30]-[:-90]-[:-150]-[:150]?}')
    ring_ok = len(ra) == 6 and len(rb) == 6
    print('  ring      ?…? atoms=%d bonds=%d %s' % (len(ra), len(rb), 'OK' if ring_ok else 'FAIL'))
    ok = ok and ring_ok

    # 9. skeletal formula implicit carbons
    a_skel, b_skel = parse(r'\chemfig{=[:30]-[:-30]}')
    skel_ok = len(a_skel) == 3 and len(b_skel) == 2
    svg_skel = render(r'\chemfig{=[:30]-[:-30]}', 'skel')
    skel_ok = skel_ok and svg_skel.startswith('<svg') and 'data-atoms=' in svg_skel
    print('  skeletal  =[:30]-[:-30] atoms=3 bonds=2 %s' % ('OK' if skel_ok else 'FAIL'))
    ok = ok and skel_ok

    # 10. data-atoms / data-bonds JSON validity
    m_atoms = re.search(r"data-atoms='([^']*)'", svg_skel)
    m_bonds = re.search(r"data-bonds='([^']*)'", svg_skel)
    json_ok = False
    if m_atoms and m_bonds:
        parsed_atoms = json.loads(m_atoms.group(1))
        parsed_bonds = json.loads(m_bonds.group(1))
        json_ok = len(parsed_atoms) == 3 and len(parsed_bonds) == 2 and parsed_atoms[0]['l'] == 'C'
    print('  json_io   data-atoms / data-bonds %s' % ('OK' if json_ok else 'FAIL'))
    ok = ok and json_ok

    return 0 if ok else 1


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
