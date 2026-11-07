/* che_note Colab kit — organic structures (window.KO). Inlined by tools/build_colab.py after kit.js
   whenever a cell's script mentions KO.

   Works on the <svg class="cf" data-atoms='[…]' data-bonds='[…]'> that {{chemfig}} compiles to
   (tools/chemfig2svg.py): atom refs, curly arrows, lone pairs, δ+/δ−, circled charges, transition-state
   (dashed) bonds, highlight discs, IUPAC locants, [ ]⁻ brackets, several structures composed into one
   SVG, and a step-by-step mechanism player with an exam mode (click start, then end of each arrow).

   Atom refs: name from @{name} ('c1'), index (3), bond midpoint ('c1-c2'), lone pair ('lp:o1',
   'lp:o1:2' = its 2nd one), or a raw point [x, y]. Everything is in viewBox units. */
(function () {
  if (window.KO) return;
  var KO = {}, uid = 0;
  var GAP = 4;        /* arrow tip ↔ target atom's text bbox */
  var BACK = 5;       /* the path stops this far before the tip; the marker covers the rest */
  var PI = Math.PI;

  var CSS = [
    '.k svg .ko-arrow{fill:none;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}',
    '.k svg .ko-try{stroke-dasharray:4 3}',
    '.k svg .ko-hide{display:none}',
    '.k svg .ko-lp circle{fill:var(--fg)}',
    '.k svg text.ko-d{font-size:12px;fill:var(--fg)}',
    '.k svg text.ko-q{font-size:12px;fill:var(--fg);dominant-baseline:central}',
    '.k svg circle.ko-qc{fill:var(--card);stroke:var(--fg);stroke-width:1}',
    '.k svg text.ko-num{font-size:12px;fill:var(--acc);font-weight:650}',
    '.k svg text.ko-tag{font-size:12px;fill:var(--acc);font-weight:600}',
    '.k svg text.ko-bq{font-size:15px;fill:var(--fg)}',
    '.k svg text.ko-plus{font-size:16px;fill:var(--fg)}',
    '.k svg .ko-br{fill:none;stroke:var(--fg);stroke-width:1.3}',
    '.k svg.cf .cf-b line.ko-partial{stroke-dasharray:3.2 2.8;stroke-linecap:butt}',
    '.k svg .ko-hl{fill:var(--hl)} .k svg .ko-hl.ko-acc{fill:var(--acc-soft)} .k svg .ko-hl.ko-ok{fill:var(--ok-soft)} .k svg .ko-hl.ko-bad{fill:var(--bad-soft)}',
    '.k svg .ko-tg{fill:var(--acc);fill-opacity:.16;stroke:none}',
    '.k svg .ko-sel{fill:none;stroke:var(--acc);stroke-width:1.6}',
    '.k .ko-mech{outline:none;margin:6px 0}',
    '.k .ko-mech:focus-visible{outline:2px solid var(--acc);outline-offset:3px;border-radius:8px}',
    '.k .ko-bar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:6px}',
    '.k .ko-bar button{font-size:14px}',
    '.k .ko-bar button:disabled{opacity:.45;cursor:default}',
    '.k .ko-dots{display:inline-flex;gap:4px}',
    '.k .ko-dots button{min-width:2.1em;padding:3px 0;text-align:center}',
    '.k .ko-body{display:grid;grid-template-columns:minmax(0,1fr) minmax(190px,250px);gap:10px;align-items:start}',
    '@media (max-width:600px){.k .ko-body{grid-template-columns:minmax(0,1fr)}}',
    '.k .ko-stage{background:var(--card);border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;justify-content:center;padding:4px;overflow:hidden}',
    '.k .ko-stage svg.cf{display:block}',
    '.k .ko-exam .ko-stage svg{cursor:crosshair}',
    '.k .ko-side{font-size:13.5px;line-height:1.45}',
    '.k .ko-side h4{margin:0 0 4px;font-size:13.5px}',
    '.k .ko-marks{list-style:none;padding:0;margin:0}',
    '.k .ko-marks li{display:flex;gap:6px;padding:3px 0;color:var(--fg)}',
    '.k .ko-marks li .st{flex:none;width:1.1em;text-align:center;font-weight:700;color:var(--acc)}',
    '.k .ko-marks li.done{color:var(--mut)} .k .ko-marks li.done .st{color:var(--mut)}',
    '.k .ko-marks li.later{display:none}',
    '.k .ko-marks li.got .st{color:var(--ok)} .k .ko-marks li.miss .st{color:var(--bad)}',
    '.k .ko-marks .none{color:var(--faint);font-size:13px}',
    '.k .ko-cap{margin:6px 0 0}',
    '.k .ko-fb{min-height:1.5em;margin-top:4px;font-size:14px;color:var(--mut)}',
    '.k .ko-fb.ok{color:var(--ok)} .k .ko-fb.bad{color:var(--bad)}'
  ].join('\n');
  function css() {
    if (document.getElementById('ko-css')) return;
    var s = document.createElement('style'); s.id = 'ko-css'; s.textContent = CSS;
    (document.head || document.documentElement).appendChild(s);
  }

  /* ---------- atoms / bonds ---------- */
  function J(svg, attr) { try { return JSON.parse(svg.getAttribute(attr) || '[]'); } catch (e) { return []; } }
  function data(svg) {
    if (svg.__ko) return svg.__ko;
    var atoms = J(svg, 'data-atoms').map(function (a, k) {
      return { i: a.i == null ? k : a.i, l: a.l || '', x: +a.x, y: +a.y, n: a.n || null, el: null };
    });
    var bonds = J(svg, 'data-bonds').map(function (b) { return { a: b[0], b: b[1], o: b[2] }; });
    /* the label <text> sits exactly on its atom (text-anchor middle, dominant-baseline central) */
    var texts = svg.querySelectorAll('text.cf-a');
    for (var t = 0; t < texts.length; t++) {
      var tx = +texts[t].getAttribute('x'), ty = +texts[t].getAttribute('y');
      for (var k = 0; k < atoms.length; k++) {
        var a = atoms[k];
        if (a.l && !a.el && Math.abs(a.x - tx) < 0.6 && Math.abs(a.y - ty) < 0.6) { a.el = texts[t]; break; }
      }
    }
    var byName = {}, nb = atoms.map(function () { return []; });
    atoms.forEach(function (a) { if (a.n) byName[a.n] = a.i; });
    bonds.forEach(function (b) { nb[b.a].push(b.b); nb[b.b].push(b.a); });
    svg.__ko = { atoms: atoms, bonds: bonds, byName: byName, nb: nb, lps: {}, deltas: {}, charges: {},
                 placed: null, avoid: [], arrows: [], mk: {} };
    return svg.__ko;
  }
  KO.atoms = function (svg) { return data(svg); };

  function idx(svg, s) {
    var D = data(svg);
    if (typeof s === 'number') { if (D.atoms[s]) return s; }
    else if (Object.prototype.hasOwnProperty.call(D.byName, s)) return D.byName[s];
    else if (/^\d+$/.test(s) && D.atoms[+s]) return +s;
    throw new Error('KO: no atom "' + s + '"');
  }
  function bondOf(D, i, j) {
    for (var k = 0; k < D.bonds.length; k++) {
      var b = D.bonds[k];
      if ((b.a === i && b.b === j) || (b.a === j && b.b === i)) return b;
    }
    return null;
  }
  function plain(l) {   /* 'CH_{3}' → 'CH₃', '^{+}' → '⁺' */
    var SUB = '₀₁₂₃₄₅₆₇₈₉';
    return String(l).replace(/_\{([^}]*)\}|_(\w)/g, function (m, a, b) {
      return (a || b).replace(/\d/g, function (d) { return SUB[d]; });
    }).replace(/\^\{([^}]*)\}/g, function (m, a) { return K.sup(a.replace('\\delta', 'δ')); });
  }

  /* text bbox of an atom label (viewBox units); implicit (unlabelled) vertices get a 5×5 box */
  function rect(svg, i) {
    var a = data(svg).atoms[i];
    if (a.el) {
      var b = null;
      try { b = a.el.getBBox(); } catch (e) { b = null; }
      if (b && b.width) return { x: b.x, y: b.y, w: b.width, h: b.height };
      var w = plain(a.l).length * 8 + 2;           /* not rendered yet (hidden tab): estimate */
      return { x: a.x - w / 2, y: a.y - 9, w: w, h: 18 };
    }
    return { x: a.x - 2.5, y: a.y - 2.5, w: 5, h: 5, imp: true };
  }
  /* the glyph box: getBBox of a text spans the font's whole ascent–descent, ~3 px of air above and below
     capital letters; lone pairs / δ / charges hug the letters, so they use this tighter box */
  function tight(svg, i) {
    var r = rect(svg, i);
    if (r.imp) return r;
    var a = data(svg).atoms[i], fs = 13;
    try { fs = parseFloat(getComputedStyle(a.el).fontSize) || 13; } catch (e) { /* default */ }
    var top = a.y - 0.40 * fs, bot = Math.min(r.y + r.h, a.y + 0.40 * fs);
    if (/_/.test(a.l)) bot = Math.min(r.y + r.h, a.y + 0.55 * fs);  /* subscripts hang lower */
    return { x: r.x + 0.5, y: Math.max(r.y, top), w: r.w - 1, h: bot - Math.max(r.y, top) };
  }
  function infl(r, dx, dy) { if (dy == null) dy = dx; return { x: r.x - dx, y: r.y - dy, w: r.w + 2 * dx, h: r.h + 2 * dy }; }
  /* distance along unit (ux, uy) from (px, py) — inside r — to r's edge */
  function exitRect(px, py, ux, uy, r) {
    var t = 1e9;
    if (ux > 1e-9) t = Math.min(t, (r.x + r.w - px) / ux);
    if (ux < -1e-9) t = Math.min(t, (r.x - px) / ux);
    if (uy > 1e-9) t = Math.min(t, (r.y + r.h - py) / uy);
    if (uy < -1e-9) t = Math.min(t, (r.y - py) / uy);
    return Math.max(t, 0);
  }
  function inRect(x, y, r) { return x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h; }
  function rdist(x, y, r) {
    var dx = Math.max(r.x - x, 0, x - r.x - r.w), dy = Math.max(r.y - y, 0, y - r.y - r.h);
    return Math.sqrt(dx * dx + dy * dy);
  }
  function adist(a, b) { var d = Math.abs(a - b) % (2 * PI); return d > PI ? 2 * PI - d : d; }

  /* every drawn bond line as a segment (K.label's avoid list) */
  function bondSegs(svg) {
    return Array.prototype.map.call(svg.querySelectorAll('.cf-b line'), function (l) {
      return [+l.getAttribute('x1'), +l.getAttribute('y1'), +l.getAttribute('x2'), +l.getAttribute('y2')];
    });
  }
  function placed(svg) {
    var D = data(svg);
    if (!D.placed) D.placed = D.atoms.filter(function (a) { return a.el; }).map(function (a) { return rect(svg, a.i); });
    return D.placed;
  }
  function avoid(svg) { return bondSegs(svg).concat(data(svg).avoid); }

  /* directions (screen radians, y down) already taken around atom i: bonds, lone pairs, nearby arrow samples */
  function occupied(svg, i) {
    var D = data(svg), a = D.atoms[i], out = [];
    D.nb[i].forEach(function (j) { out.push(Math.atan2(D.atoms[j].y - a.y, D.atoms[j].x - a.x)); });
    (D.lps[i] || []).forEach(function (l) { out.push(l.ang); });
    D.arrows.forEach(function (ar) {
      ar.pts.forEach(function (p) {
        var d = Math.sqrt((p[0] - a.x) * (p[0] - a.x) + (p[1] - a.y) * (p[1] - a.y));
        if (d > 1 && d < 24) out.push(Math.atan2(p[1] - a.y, p[0] - a.x));
      });
    });
    return out;
  }
  /* away from the bonds: opposite the sum of the bond unit vectors; a free atom prefers upper right */
  function prefAng(svg, i) {
    var D = data(svg), a = D.atoms[i], sx = 0, sy = 0;
    D.nb[i].forEach(function (j) {
      var dx = D.atoms[j].x - a.x, dy = D.atoms[j].y - a.y, d = Math.sqrt(dx * dx + dy * dy) || 1;
      sx += dx / d; sy += dy / d;
    });
    return Math.sqrt(sx * sx + sy * sy) > 0.3 ? Math.atan2(-sy, -sx) : -PI / 4;
  }
  /* 24 candidate directions: free ones first (≥ cap from anything taken), then closest to pref */
  function angles(svg, i, o) {
    o = o || {};
    var occ = occupied(svg, i), pref = o.pref != null ? o.pref : prefAng(svg, i), cap = (o.cap || 60) * PI / 180, c = [];
    for (var k = 0; k < 24; k++) {
      var t = -PI + k * PI / 12, m = PI;
      occ.forEach(function (x) { m = Math.min(m, adist(x, t)); });
      c.push({ t: t, s: Math.min(m, cap), p: adist(t, pref) });
    }
    c.sort(function (A, B) { return (B.s - A.s) || (A.p - B.p); });
    return c.map(function (x) { return x.t; });
  }

  /* lone-pair centre on atom i along direction ang */
  function lpAt(svg, i, ang) {
    var D = data(svg), a = D.atoms[i], ux = Math.cos(ang), uy = Math.sin(ang), r = tight(svg, i);
    var d = r.imp ? 7 : exitRect(a.x, a.y, ux, uy, infl(r, 2.8)) + 1.7;
    return { x: a.x + ux * d, y: a.y + uy * d, ux: ux, uy: uy, ang: ang, i: i };
  }
  function lpDir(svg, i, o) {
    o = o || {};
    if (o.ang != null) return -o.ang * PI / 180;          /* o.ang: degrees CCW, like ChemFig */
    var pref = null;
    if (o.toward != null) {
      var a = data(svg).atoms[i], T = KO.pt(svg, o.toward);
      pref = Math.atan2(T.y - a.y, T.x - a.x);
    }
    return angles(svg, i, { pref: pref, cap: o.toward != null ? 45 : 60 })[0];
  }

  /* ---------- refs ---------- */
  KO.ref = function (svg, ref) {
    var D = data(svg), m;
    if (ref && typeof ref === 'object') {
      var x = ref.length ? ref[0] : ref.x, y = ref.length ? ref[1] : ref.y;
      return { kind: 'pt', x: x, y: y, key: 'p:' + Math.round(x) + ',' + Math.round(y) };
    }
    if (typeof ref === 'string' && (m = ref.match(/^lp:(.+?)(?::(\d+))?$/))) {
      var i = idx(svg, m[1]);
      return { kind: 'lp', i: i, k: m[2] ? +m[2] - 1 : 0, key: 'lp:' + i };
    }
    if (typeof ref === 'string' && !Object.prototype.hasOwnProperty.call(D.byName, ref) && ref.indexOf('-') > 0) {
      var p = ref.split('-'), a = idx(svg, p[0]), b = idx(svg, p[1]), lo = Math.min(a, b), hi = Math.max(a, b);
      var bd = bondOf(D, a, b);
      return { kind: bd ? 'bond' : 'mid', i: a, j: b, o: bd ? bd.o : 0, key: (bd ? 'b:' : 'm:') + lo + '-' + hi };
    }
    var n = idx(svg, ref);
    return { kind: 'atom', i: n, key: 'a:' + n };
  };
  /* ref → point {x, y, kind, …}; a lone pair that is not drawn yet is where KO.lp would put it */
  KO.pt = function (svg, ref) {
    var R = KO.ref(svg, ref), D = data(svg), A = D.atoms;
    if (R.kind === 'pt') return R;
    if (R.kind === 'atom') { R.x = A[R.i].x; R.y = A[R.i].y; return R; }
    if (R.kind === 'lp') {
      var l = (D.lps[R.i] || [])[R.k] || lpAt(svg, R.i, lpDir(svg, R.i));
      R.x = l.x; R.y = l.y; R.ux = l.ux; R.uy = l.uy; return R;
    }
    R.x = (A[R.i].x + A[R.j].x) / 2; R.y = (A[R.i].y + A[R.j].y) / 2;
    return R;
  };
  function lab(svg, i) {
    var D = data(svg), a = D.atoms[i], s = a.l ? plain(a.l) : 'C';
    if (D.charges[i]) s += D.charges[i] === '+' ? '⁺' : '⁻';
    else if (D.deltas[i]) s += 'δ' + D.deltas[i];
    return s;
  }
  KO.desc = function (svg, ref) {
    var R = KO.ref(svg, ref), D = data(svg);
    if (R.kind === 'lp') return 'lone pair on ' + lab(svg, R.i);
    if (R.kind === 'bond') {
      var b = D.atoms, s = function (k) { return b[k].l ? plain(b[k].l).replace(/[⁺⁻]/g, '') : 'C'; };
      return s(R.i) + ({ 1: '–', 2: '=', 3: '≡' }[R.o] || '–') + s(R.j) + ' bond';
    }
    if (R.kind === 'mid') return lab(svg, R.i) + ' 与 ' + lab(svg, R.j) + ' 之间';
    if (R.kind === 'atom') return lab(svg, R.i);
    return '(' + Math.round(R.x) + ', ' + Math.round(R.y) + ')';
  };

  /* ---------- curly arrows ---------- */
  function marker(svg, col, kind) {
    var D = data(svg), key = col + kind;
    if (D.mk[key]) return D.mk[key];
    var defs = svg.querySelector('defs.ko-defs');
    if (!defs) { defs = K.svg('defs', { 'class': 'ko-defs' }); svg.insertBefore(defs, svg.firstChild); }
    var id = 'ko-m' + (++uid) + '-' + key;
    /* userSpaceOnUse: the default markerUnits=strokeWidth would scale the head with the line width */
    var m = K.svg('marker', { id: id, markerUnits: 'userSpaceOnUse', viewBox: '0 0 10 8', markerWidth: 10, markerHeight: 8,
                              refX: 5, refY: 4, orient: 'auto', overflow: 'visible' });
    var d = kind === 'f' ? 'M0,0 L10,4 L0,8 L2.6,4 Z' : kind === 'l' ? 'M0.5,0 L10,4 L2.6,4 Z' : 'M0.5,8 L10,4 L2.6,4 Z';
    m.appendChild(K.svg('path', { d: d, 'class': 'ko-head', style: 'fill:var(--' + col + ');stroke:none' }));
    defs.appendChild(m);
    D.mk[key] = id;
    return id;
  }
  function bez(P, t) {
    var u = 1 - t;
    if (P.length === 3) return [u * u * P[0][0] + 2 * u * t * P[1][0] + t * t * P[2][0], u * u * P[0][1] + 2 * u * t * P[1][1] + t * t * P[2][1]];
    return [u * u * u * P[0][0] + 3 * u * u * t * P[1][0] + 3 * u * t * t * P[2][0] + t * t * t * P[3][0],
            u * u * u * P[0][1] + 3 * u * u * t * P[1][1] + 3 * u * t * t * P[2][1] + t * t * t * P[3][1]];
  }
  /* from: bond midpoint / lone pair (or atom); to: atom (tip stops GAP short of its text) / bond / point.
     o.bend: bulge as a fraction of the start–end distance, + = left of the direction of travel;
     o.bend2 (or o.c1 + o.c2, absolute points) → cubic; o.cls: colour token (acc, s2, pos, …);
     o.half: fish-hook (one electron); o.tag: small label beside the arrow ('M1'). */
  KO.arrow = function (svg, from, to, o) {
    o = o || {}; css();
    var D = data(svg), F = KO.pt(svg, from), T = KO.pt(svg, to);
    var col = o.cls || 'acc', b = o.bend == null ? 0.35 : o.bend;
    var S = [F.x, F.y], dx = T.x - S[0], dy = T.y - S[1], L = Math.sqrt(dx * dx + dy * dy) || 1;
    var nx = dy / L, ny = -dx / L, P;
    if (o.c1 && o.c2) P = [S, o.c1, o.c2];
    else if (o.c1) P = [S, o.c1];
    else if (o.bend2 != null) P = [S, [S[0] + dx / 3 + nx * b * L, S[1] + dy / 3 + ny * b * L], [S[0] + 2 * dx / 3 + nx * o.bend2 * L, S[1] + 2 * dy / 3 + ny * o.bend2 * L]];
    else P = [S, [(S[0] + T.x) / 2 + nx * b * L, (S[1] + T.y) / 2 + ny * b * L]];
    var C1 = P[1], CL = P[P.length - 1];
    /* tail: on the π line nearest the bulge for a multiple bond; just outside the dots of a lone pair */
    if (F.kind === 'bond' && F.o > 1) {
      var A = D.atoms[F.i], B = D.atoms[F.j], bx = B.x - A.x, by = B.y - A.y, bl = Math.sqrt(bx * bx + by * by) || 1;
      var mx = -by / bl, my = bx / bl, side = (C1[0] - S[0]) * mx + (C1[1] - S[1]) * my > 0 ? 1 : -1, off = F.o === 2 ? 1.2 : 1.8;
      S = [S[0] + mx * side * off, S[1] + my * side * off];
    } else if (F.kind === 'lp') {
      S = [F.x + F.ux * 1.8, F.y + F.uy * 1.8];
    } else if (F.kind === 'atom') {
      var ra = rect(svg, F.i), ex = C1[0] - F.x, ey = C1[1] - F.y, el = Math.sqrt(ex * ex + ey * ey) || 1;
      var ta = exitRect(F.x, F.y, ex / el, ey / el, infl(ra, 3));
      S = [F.x + ex / el * ta, F.y + ey / el * ta];
    }
    P[0] = S;
    /* tip: where the line from the atom towards the last control point leaves the inflated text box,
       so the head points straight at the atom and stops clear of the letters */
    var E = [T.x, T.y];
    if (T.kind === 'atom') {
      var r0 = rect(svg, T.i), gp = r0.imp ? 3.5 : GAP, rt = infl(r0, gp);
      /* first point along the ray that is gp from the text box (rounded corners: a square corner
         would leave the tip gp·√2 away on diagonals) */
      var tipT = function (vx, vy) {
        var lo = 0, hi = exitRect(T.x, T.y, vx, vy, rt);
        for (var it = 0; it < 24; it++) { var md = (lo + hi) / 2; if (rdist(T.x + vx * md, T.y + vy * md, r0) < gp) lo = md; else hi = md; }
        return hi;
      };
      var ux = CL[0] - T.x, uy = CL[1] - T.y;
      if (inRect(CL[0], CL[1], rt)) { ux = S[0] - T.x; uy = S[1] - T.y; }
      var ul = Math.sqrt(ux * ux + uy * uy) || 1;
      ux /= ul; uy /= ul;
      var te = tipT(ux, uy), cd = Math.sqrt((CL[0] - T.x) * (CL[0] - T.x) + (CL[1] - T.y) * (CL[1] - T.y));
      if (!o.c1 && cd < te + BACK + 7 && L >= 30) {
        /* long arrow, control point just too near the tip: push it out along the same line */
        CL = [T.x + ux * (te + BACK + 7), T.y + uy * (te + BACK + 7)]; P[P.length - 1] = CL;
      } else if (!o.c1 && L < 30) {
        /* short hop (< 30, e.g. a bond to one of its own atoms): a quadratic hooks back on itself. Cubic loop
           instead — out of the bond on the bulge side, back in to the atom from that side, slightly
           leaning back towards the bond, so the arc stays compact and the head points at the letters */
        var sg = b < 0 ? -1 : 1, ox = nx * sg, oy = ny * sg, sx0 = S[0] - T.x, sy0 = S[1] - T.y, sl = Math.sqrt(sx0 * sx0 + sy0 * sy0) || 1;
        ux = ox + 0.25 * sx0 / sl; uy = oy + 0.25 * sy0 / sl; ul = Math.sqrt(ux * ux + uy * uy) || 1; ux /= ul; uy /= ul;
        te = tipT(ux, uy);
        var kk = Math.max(Math.abs(b), 0.8) * L * 0.75;
        CL = [T.x + ux * (te + BACK + 0.55 * L + 4), T.y + uy * (te + BACK + 0.55 * L + 4)];
        P = [S, [S[0] + ox * kk + (T.x - S[0]) * 0.2, S[1] + oy * kk + (T.y - S[1]) * 0.2], CL];
      }
      E = [T.x + ux * te, T.y + uy * te];
    }
    var tx = E[0] - CL[0], ty = E[1] - CL[1], tl = Math.sqrt(tx * tx + ty * ty) || 1;
    var Pend = [E[0] - tx / tl * BACK, E[1] - ty / tl * BACK];
    P.push(Pend);
    var f = function (p) { return p[0].toFixed(2) + ',' + p[1].toFixed(2); };
    var d = 'M' + f(P[0]) + (P.length === 3 ? ' Q' + f(P[1]) + ' ' + f(P[2]) : ' C' + f(P[1]) + ' ' + f(P[2]) + ' ' + f(P[3]));
    var kind = o.half ? (b >= 0 ? 'l' : 'r') : 'f';
    var g = K.svg('g', { 'class': 'ko-ag' });
    var path = K.svg('path', {
      d: d, 'class': 'ko-arrow' + (o.half ? ' ko-half' : '') + (o.try ? ' ko-try' : ''), style: 'stroke:var(--' + col + ')',
      'marker-end': 'url(#' + marker(svg, col, kind) + ')',
      'data-from': String(from), 'data-to': String(to),
      'data-sx': S[0].toFixed(2), 'data-sy': S[1].toFixed(2), 'data-tx': E[0].toFixed(2), 'data-ty': E[1].toFixed(2)
    });
    g.appendChild(path);
    svg.appendChild(g);
    var pts = [], k;
    for (k = 0; k <= 20; k++) pts.push(bez(P, k / 20));
    pts.push(E);
    D.arrows.push({ pts: pts, el: g });
    D.avoid = D.avoid.concat(K.segs(pts));
    if (o.tag) {
      var mid = bez(P, 0.5), sgn = b >= 0 ? 1 : -1;
      var t = around(svg, mid[0], mid[1], { x: mid[0] - 2, y: mid[1] - 2, w: 4, h: 4 }, o.tag, 'ko-tag',
                     angleList(Math.atan2(ny * sgn, nx * sgn)), [3, 9, 16, 24]);
      g.appendChild(t);
    }
    path.__ko = { P: P, E: E, S: S };
    return path;
  };
  function angleList(first) {
    var out = [];
    for (var k = 0; k < 12; k++) {
      var s = (k % 2 ? 1 : -1) * Math.ceil(k / 2);
      out.push(first + s * PI / 6);
    }
    return out;
  }

  /* ---------- labels hugging an atom (δ±, charges, locants, tags) ---------- */
  function measure(svg, text, cls) {
    var t = K.svg('text', { 'class': 'halo ' + cls, x: 0, y: 0, 'text-anchor': 'middle' });
    t.textContent = text; svg.appendChild(t);
    var b = null;
    try { b = t.getBBox(); } catch (e) { b = null; }
    svg.removeChild(t);
    if (!b || !b.width) b = { x: -text.length * 3.6, y: -11, width: text.length * 7.2, height: 14 };
    return b;
  }
  /* K.label at the first of `angs` (× each gap in g, nearest ring first) where the label box sits g outside box r without touching anything */
  function around(svg, ax, ay, r, text, cls, angs, g, pad) {
    var m = measure(svg, text, cls), hw = m.width / 2, hh = m.height / 2, cxo = m.x + hw, cyo = m.y + hh;
    var cands = [];
    [].concat(g).forEach(function (gg) {
      var outer = infl(r, hw + gg, hh + gg);
      angs.forEach(function (t) {
        var ux = Math.cos(t), uy = Math.sin(t), d = exitRect(ax, ay, ux, uy, outer);
        cands.push([ax + ux * d - cxo - ax, ay + uy * d - cyo - ay, 'middle']);
      });
    });
    return K.label(svg, ax, ay, text, { cls: cls, cands: cands, avoid: avoid(svg), placed: placed(svg), pad: pad == null ? 1.5 : pad });
  }
  /* label beside atom i, the way a textbook writes δ+ or a charge: first try the slots that hug the
     letters (raised right = superscript position, raised left, above, right, left, below, lowered right /
     left), then the diagonal corners, then a looser ring. Free directions first (nothing taken within
     o.cap degrees), then closest to o.pref / away from the bonds. */
  function besideAtom(svg, i, text, cls, g, pad, o) {
    o = o || {};
    var a = data(svg).atoms[i], tb = tight(svg, i), m = measure(svg, text, cls);
    var hw = m.width / 2, hh = m.height / 2, cxo = m.x + hw, cyo = m.y + hh, up = tb.imp ? 0 : o.up != null ? o.up : 1.5;
    var R = tb.x + tb.w + g + hw, L = tb.x - g - hw, U = tb.y - g - hh, Dn = tb.y + tb.h + g + hh;
    var pts = [[R, tb.y + up], [L, tb.y + up], [a.x, U], [R, a.y], [L, a.y], [a.x, Dn], [R, tb.y + tb.h - up], [L, tb.y + tb.h - up]];
    [g, g + 6].forEach(function (gg, ring) {
      var outer = infl(tb, hw + gg, hh + gg);
      for (var k = 0; k < 8; k++) {
        if (!ring && k % 2 === 0) continue;               /* first ring: the four diagonals only */
        var t = -PI + k * PI / 4, ux = Math.cos(t), uy = Math.sin(t), d = exitRect(a.x, a.y, ux, uy, outer);
        pts.push([a.x + ux * d, a.y + uy * d, ring]);
      }
    });
    var occ = occupied(svg, i), pref = o.pref != null ? o.pref : prefAng(svg, i), cap = (o.cap || 50) * PI / 180;
    var c = pts.map(function (q, n) {
      var t = Math.atan2(q[1] - a.y, q[0] - a.x), mo = PI;
      occ.forEach(function (x) { mo = Math.min(mo, adist(x, t)); });
      return { q: q, s: Math.min(mo, cap), grp: q.length > 2 ? 1 + q[2] : 0, p: adist(t, pref) + n * 1e-3 };
    });
    c.sort(function (A, B) { return (B.s - A.s) || (A.grp - B.grp) || (A.p - B.p); });
    var cands = c.map(function (x) { return [x.q[0] - cxo - a.x, x.q[1] - cyo - a.y, 'middle']; });
    var lt = K.label(svg, a.x, a.y, text, { cls: cls, cands: cands, avoid: avoid(svg), placed: placed(svg), pad: pad == null ? 1.5 : pad });
    lt.setAttribute('data-atom', i);
    return lt;
  }
  KO.delta = function (svg, atom, sign, o) {
    css();
    var i = idx(svg, atom), s = sign === '+' ? '+' : '−';
    data(svg).deltas[i] = s;
    return besideAtom(svg, i, 'δ' + s, 'ko-d', 2.5, 1.5, o);
  };
  KO.charge = function (svg, atom, sign, o) {
    css();
    var i = idx(svg, atom), s = sign === '+' ? '+' : '−';
    data(svg).charges[i] = s;
    /* no-break spaces pad the box to the circle's width (K.label's pad is the same on all sides) */
    var t = besideAtom(svg, i, '\u00a0' + s + '\u00a0', 'ko-q', 2.5, 0.8, { up: -2, pref: (o || {}).pref, cap: (o || {}).cap });
    var b = t.getBBox(), c = K.svg('circle', { 'class': 'ko-qc', cx: +t.getAttribute('x'), cy: (b.y + b.height / 2), r: 6.2 });
    svg.insertBefore(c, t);
    return t;
  };
  /* IUPAC locants: atoms[k] gets k + 1 (o.start to begin elsewhere, o.prefix e.g. 'C') */
  KO.num = function (svg, atoms, o) {
    o = o || {}; css();
    return atoms.map(function (ref, k) {
      return besideAtom(svg, idx(svg, ref), (o.prefix || '') + ((o.start || 1) + k), 'ko-num', 2.5, 1.5, o);
    });
  };
  KO.lp = function (svg, atom, n, o) {
    o = o || {}; css();
    var D = data(svg), i = idx(svg, atom), out = [];
    for (var k = 0; k < (n || 1); k++) {
      var l = lpAt(svg, i, k === 0 ? lpDir(svg, i, o) : lpDir(svg, i, {}));
      var px = -l.uy * 2.7, py = l.ux * 2.7, g = K.svg('g', { 'class': 'ko-lp', 'data-atom': i });
      g.appendChild(K.svg('circle', { cx: (l.x + px).toFixed(2), cy: (l.y + py).toFixed(2), r: 1.7 }));
      g.appendChild(K.svg('circle', { cx: (l.x - px).toFixed(2), cy: (l.y - py).toFixed(2), r: 1.7 }));
      g.setAttribute('data-x', l.x.toFixed(2)); g.setAttribute('data-y', l.y.toFixed(2));
      svg.appendChild(g);
      (D.lps[i] = D.lps[i] || []).push(l);
      placed(svg).push({ x: l.x - 4.6, y: l.y - 4.6, w: 9.2, h: 9.2 });
      out.push(g);
    }
    return out;
  };
  /* bond i–j drawn dashed (partial bond in a transition state) */
  KO.partial = function (svg, a, b) {
    css();
    var D = data(svg), A = D.atoms[idx(svg, a)], B = D.atoms[idx(svg, b)], bx = B.x - A.x, by = B.y - A.y, bl2 = bx * bx + by * by;
    return Array.prototype.filter.call(svg.querySelectorAll('.cf-b line'), function (l) {
      var x1 = +l.getAttribute('x1'), y1 = +l.getAttribute('y1'), x2 = +l.getAttribute('x2'), y2 = +l.getAttribute('y2');
      var mx = (x1 + x2) / 2 - A.x, my = (y1 + y2) / 2 - A.y, t = (mx * bx + my * by) / bl2;
      var perp = Math.abs(mx * by - my * bx) / Math.sqrt(bl2), lx = x2 - x1, ly = y2 - y1;
      var par = Math.abs(lx * by - ly * bx) / (Math.sqrt(lx * lx + ly * ly) * Math.sqrt(bl2) || 1);
      var hit = t > 0.05 && t < 0.95 && perp < 4.5 && par < 0.1;
      if (hit) l.classList.add('ko-partial');
      return hit;
    });
  };
  /* soft disc behind atoms; cls: '' (yellow), 'acc', 'ok', 'bad' */
  KO.hl = function (svg, atoms, cls) {
    css();
    var after = svg.querySelector('defs.ko-defs');
    return (atoms.length != null && typeof atoms !== 'string' ? atoms : [atoms]).map(function (ref) {
      var i = idx(svg, ref), r = rect(svg, i), a = data(svg).atoms[i];
      var c = K.svg('circle', { 'class': 'ko-hl' + (cls ? ' ko-' + cls : ''), cx: r.imp ? a.x : r.x + r.w / 2, cy: r.imp ? a.y : a.y,
                                r: r.imp ? 8 : Math.max(r.w, r.h * 0.8) / 2 + 3, 'data-atom': i });
      svg.insertBefore(c, after ? after.nextSibling : svg.firstChild);
      return c;
    });
  };
  /* [ … ] around the given atoms (all by default), o.charge ('−', '+') at the top right */
  KO.bracket = function (svg, o) {
    o = o || {}; css();
    var D = data(svg), list = (o.atoms || D.atoms.map(function (a) { return a.i; })).map(function (r) { return idx(svg, r); });
    var x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    list.forEach(function (i) {
      var r = rect(svg, i);
      x0 = Math.min(x0, r.x); y0 = Math.min(y0, r.y); x1 = Math.max(x1, r.x + r.w); y1 = Math.max(y1, r.y + r.h);
    });
    var p = o.pad == null ? 6 : o.pad, arm = 5;
    x0 -= p; y0 -= p; x1 += p; y1 += p;
    var g = K.svg('g', { 'class': 'ko-bk' });
    g.appendChild(K.svg('path', { 'class': 'ko-br', d: 'M' + (x0 + arm) + ',' + y0 + ' H' + x0 + ' V' + y1 + ' H' + (x0 + arm) +
                                  ' M' + (x1 - arm) + ',' + y0 + ' H' + x1 + ' V' + y1 + ' H' + (x1 - arm) }));
    svg.appendChild(g);
    D.avoid = D.avoid.concat([[x0, y0, x0, y1], [x1, y0, x1, y1], [x0, y0, x0 + arm, y0], [x0, y1, x0 + arm, y1], [x1 - arm, y0, x1, y0], [x1 - arm, y1, x1, y1]]);
    if (o.charge) {
      var t = K.label(svg, x1, y0, o.charge === '+' ? '+' : '−', { cls: 'ko-bq', cands: [[3, 6, 'start'], [3, 10, 'start']], avoid: avoid(svg), placed: placed(svg), pad: 1 });
      g.appendChild(t);
    }
    return g;
  };

  /* ---------- several structures in one SVG ---------- */
  function toSvg(x) {
    if (typeof x === 'string') { var d = document.createElement('div'); d.innerHTML = x.trim(); return d.querySelector('svg'); }
    return x && x.tagName && x.tagName.toLowerCase() === 'svg' ? x : x.querySelector('svg');
  }
  function shift(el, dx, dy) {
    var tag = el.tagName.toLowerCase();
    function add(a, d) { if (el.hasAttribute(a)) el.setAttribute(a, (+el.getAttribute(a) + d).toFixed(1)); }
    if (tag === 'g') { Array.prototype.forEach.call(el.children, function (c) { shift(c, dx, dy); }); return; }
    if (tag === 'line') { add('x1', dx); add('x2', dx); add('y1', dy); add('y2', dy); return; }
    if (tag === 'text' || tag === 'rect' || tag === 'use' || tag === 'image') { add('x', dx); add('y', dy); return; }
    if (tag === 'circle' || tag === 'ellipse') { add('cx', dx); add('cy', dy); return; }
    if ((tag === 'polygon' || tag === 'polyline') && el.hasAttribute('points')) {
      var n = el.getAttribute('points').trim().split(/[\s,]+/).map(Number), out = [];
      for (var k = 0; k + 1 < n.length; k += 2) out.push((n[k] + dx).toFixed(1) + ',' + (n[k + 1] + dy).toFixed(1));
      el.setAttribute('points', out.join(' ')); return;
    }
    el.setAttribute('transform', 'translate(' + dx + ' ' + dy + ') ' + (el.getAttribute('transform') || ''));
  }
  /* parts: [{svg: <svg class="cf"> | its markup | an element holding it, at: atom (default the first),
               x, y: where that atom goes, pre: name prefix}, {text: '+', x, y}]; o.scale, o.vb [x y w h] */
  KO.compose = function (parts, o) {
    o = o || {}; css();
    var out = K.svg('svg', { 'class': 'cf ko-c', role: 'img' }), atoms = [], bonds = [], vb = null;
    function grow(v) {
      if (!vb) { vb = v.slice(); return; }
      var x1 = Math.max(vb[0] + vb[2], v[0] + v[2]), y1 = Math.max(vb[1] + vb[3], v[1] + v[3]);
      vb[0] = Math.min(vb[0], v[0]); vb[1] = Math.min(vb[1], v[1]); vb[2] = x1 - vb[0]; vb[3] = y1 - vb[1];
    }
    parts.forEach(function (p) {
      if (p.text != null) {
        var t = K.svg('text', { x: p.x, y: p.y, 'text-anchor': 'middle', 'dominant-baseline': 'central', 'class': 'ko-plus ' + (p.cls || '') });
        t.textContent = p.text; out.appendChild(t); grow([p.x - 12, p.y - 12, 24, 24]);
        return;
      }
      var src = toSvg(p.svg), A = J(src, 'data-atoms'), B = J(src, 'data-bonds'), off = atoms.length;
      var anc = p.at == null ? A[0] : A.filter(function (a) { return a.n === p.at || a.i === p.at; })[0];
      if (!anc) throw new Error('KO.compose: no atom "' + p.at + '"');
      var dx = (p.x || 0) - anc.x, dy = (p.y || 0) - anc.y;
      Array.prototype.forEach.call(src.children, function (c) { var cc = c.cloneNode(true); shift(cc, dx, dy); out.appendChild(cc); });
      A.forEach(function (a) {
        var q = { i: off + a.i, l: a.l, x: +(a.x + dx).toFixed(1), y: +(a.y + dy).toFixed(1) };
        if (a.n) q.n = (p.pre || '') + a.n;
        atoms.push(q);
      });
      B.forEach(function (b) { bonds.push([b[0] + off, b[1] + off, b[2]]); });
      var v = src.getAttribute('viewBox').trim().split(/[\s,]+/).map(Number);
      grow([v[0] + dx, v[1] + dy, v[2], v[3]]);
    });
    if (o.vb) vb = o.vb;
    out.setAttribute('viewBox', vb.map(function (v) { return +v.toFixed(1); }).join(' '));
    out.setAttribute('data-atoms', JSON.stringify(atoms));
    out.setAttribute('data-bonds', JSON.stringify(bonds));
    KO.scale(out, o.scale || 1);
    return out;
  };
  KO.scale = function (svg, s) {
    var v = svg.getAttribute('viewBox').trim().split(/[\s,]+/).map(Number);
    svg.setAttribute('width', Math.round(v[2] * s)); svg.setAttribute('height', Math.round(v[3] * s));
    return svg;
  };

  /* nearest click target to (x, y) within tol: a drawn lone pair, a bond midpoint or an atom → its ref */
  KO.hit = function (svg, x, y, tol) {
    var D = data(svg), best = null, bd = tol;
    function take(d, ref) { if (d <= bd) { bd = d; best = ref; } }
    Object.keys(D.lps).forEach(function (i) {
      D.lps[i].forEach(function (l, k) { take(Math.sqrt((l.x - x) * (l.x - x) + (l.y - y) * (l.y - y)) - 0.5, 'lp:' + i + (k ? ':' + (k + 1) : '')); });
    });
    D.bonds.forEach(function (b) {
      var A = D.atoms[b.a], B = D.atoms[b.b], mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2;
      take(Math.sqrt((mx - x) * (mx - x) + (my - y) * (my - y)), b.a + '-' + b.b);
    });
    D.atoms.forEach(function (a) { take(a.el ? rdist(x, y, rect(svg, a.i)) : Math.sqrt((a.x - x) * (a.x - x) + (a.y - y) * (a.y - y)) - 2, a.i); });
    return best == null ? null : KO.ref(svg, best) && { ref: best, key: KO.ref(svg, best).key };
  };

  /* ---------- mechanism player ----------
     steps: [{svg, arrows: [[from, to, {bend, tag, m: 'M1', …}]], marks: ['M1 …'], caption, lps: [[atom, n, o]],
              deltas: [[atom, '+']], charges: [[atom, '−']], partials: [[a, b]], hl: [[atoms, cls]],
              bracket: {charge: '−'}, nums: [atoms], draw: function (svg, KO) {}}]
     o.exam: arrows hidden, click start then end; o.scale (1.5); o.title. Returns a small API. */
  KO.mech = function (root, steps, o) {
    o = o || {}; css();
    var exam = !!o.exam, sc = o.scale || 1.5;
    var base = steps.map(function (st) { return KO.scale(toSvg(st.svg).cloneNode(true), sc); });
    var box = K.el('div', { 'class': 'ko-mech' + (exam ? ' ko-exam' : ''), tabindex: '0' });
    var bar = K.el('div', { 'class': 'ko-bar' });
    var prev = K.el('button', { 'class': 'ko-prev', title: '上一步（←）' }, '← 上一步');
    var dots = K.el('span', { 'class': 'ko-dots' });
    var next = K.el('button', { 'class': 'ko-next', title: '下一步（→）' }, '下一步 →');
    var reset = K.el('button', { 'class': 'ko-reset' }, '重来');
    bar.appendChild(prev); bar.appendChild(dots); bar.appendChild(next); bar.appendChild(reset);
    var show = null;
    if (exam) { show = K.el('button', { 'class': 'ko-show' }, '显示答案'); bar.appendChild(show); }
    var body = K.el('div', { 'class': 'ko-body' }), stage = K.el('div', { 'class': 'ko-stage' });
    var side = K.el('div', { 'class': 'ko-side card' }, '<h4>Mark scheme 得分点</h4>'), ol = K.el('ol', { 'class': 'ko-marks' });
    side.appendChild(ol); body.appendChild(stage); body.appendChild(side);
    var cap = K.el('p', { 'class': 'ko-cap mut' }), fb = K.el('div', { 'class': 'ko-fb' });
    box.appendChild(bar); box.appendChild(body); box.appendChild(cap);
    if (exam) box.appendChild(fb);
    root.appendChild(box);

    var hmax = Math.max.apply(null, base.map(function (s) { return +s.getAttribute('height'); }));
    stage.style.minHeight = (hmax + 10) + 'px';
    steps.forEach(function (st, k) {
      var b = K.el('button', { 'data-i': k, title: '第 ' + (k + 1) + ' 步' }, String(k + 1));
      b.addEventListener('click', function () { go(k); });
      dots.appendChild(b);
      (st.marks || []).forEach(function (m) {
        var li = K.el('li', { 'data-step': k, 'data-m': m.split(' ')[0] }, '<span class="st"></span><span>' + m + '</span>');
        ol.appendChild(li);
      });
    });
    var none = K.el('li', { 'class': 'none' }, '本步没有单独的得分点');
    ol.appendChild(none);

    var cur = 0, svg = null, ags = [], keys = [], sel = null, selEl = null;
    var state = steps.map(function () { return {}; });   /* exam: arrow n → 'got' | 'miss' */

    function marksUpdate() {
      var any = false;
      K.$$(ol, 'li[data-step]').forEach(function (li) {
        var k = +li.getAttribute('data-step'), m = li.getAttribute('data-m'), st = li.querySelector('.st');
        li.className = k < cur ? 'done' : k === cur ? 'cur' : 'later';
        if (k === cur) any = true;
        var mine = (steps[k].arrows || []).map(function (a, n) { return (a[2] || {}).m === m ? n : -1; }).filter(function (n) { return n >= 0; });
        var s = k < cur ? '✓' : '•';
        if (exam && mine.length) {
          var S = state[k], got = mine.every(function (n) { return S[n] === 'got'; }), miss = mine.some(function (n) { return S[n] === 'miss'; });
          s = got ? '✓' : miss ? '✗' : '○';
          if (got) li.classList.add('got'); else if (miss) li.classList.add('miss');
        }
        st.textContent = s;
      });
      none.style.display = any ? 'none' : '';
    }
    function say(t, cls) { fb.className = 'ko-fb' + (cls ? ' ' + cls : ''); fb.textContent = t; }
    function render() {
      stage.innerHTML = '';
      svg = base[cur].cloneNode(true);
      stage.appendChild(svg);
      var st = steps[cur];
      (st.hl || []).forEach(function (h) { KO.hl(svg, h[0], h[1]); });
      (st.partials || []).forEach(function (p) { KO.partial(svg, p[0], p[1]); });
      (st.lps || []).forEach(function (l) { if (typeof l === 'string') KO.lp(svg, l, 1); else KO.lp(svg, l[0], l[1], l[2]); });
      ags = (st.arrows || []).map(function (a, n) {
        var g = KO.arrow(svg, a[0], a[1], a[2]).parentNode;
        g.setAttribute('data-n', n);
        if (exam && !state[cur][n]) g.classList.add('ko-hide');
        return g;
      });
      keys = (st.arrows || []).map(function (a) { return [KO.ref(svg, a[0]).key, KO.ref(svg, a[1]).key, a[0], a[1]]; });
      (st.deltas || []).forEach(function (d) { KO.delta(svg, d[0], d[1], d[2]); });
      (st.charges || []).forEach(function (c) { KO.charge(svg, c[0], c[1], c[2]); });
      if (st.bracket) KO.bracket(svg, st.bracket);
      if (st.nums) KO.num(svg, st.nums);
      if (st.draw) st.draw(svg, KO);
      if (exam) {
        var D = data(svg);
        D.bonds.forEach(function (b) {
          var A = D.atoms[b.a], B = D.atoms[b.b];
          /* filled disc behind the bond: a ring crossed by the bond line would read as a ⊖ charge */
          svg.insertBefore(K.svg('circle', { 'class': 'ko-tg', cx: (A.x + B.x) / 2, cy: (A.y + B.y) / 2, r: 4.5 }), svg.firstChild);
        });
        svg.addEventListener('click', click);
        sel = null; selEl = null;
        var left = (st.arrows || []).length - Object.keys(state[cur]).length;
        say(left ? '依次点 curly arrow 的起点（bond 中间 / lone pair），再点终点。本步还有 ' + left + ' 支箭头。' : (st.arrows || []).length ? '本步已完成。' : '本步没有 curly arrow，点「下一步」。');
      }
      cap.innerHTML = st.caption || '';
      K.$$(dots, 'button').forEach(function (b, k) { b.classList.toggle('on', k === cur); });
      prev.disabled = cur === 0; next.disabled = cur === steps.length - 1;
      marksUpdate();
      K.fit();
    }
    function go(k) { cur = Math.max(0, Math.min(steps.length - 1, k)); render(); }
    function reveal(n, how) { state[cur][n] = how; ags[n].classList.remove('ko-hide'); ags[n].classList.add('ko-' + how); }
    function click(ev) {
      var ctm = svg.getScreenCTM(); if (!ctm) return;
      var p = svg.createSVGPoint(); p.x = ev.clientX; p.y = ev.clientY;
      var q = p.matrixTransform(ctm.inverse()), h = KO.hit(svg, q.x, q.y, 10 / ctm.a);
      var S = state[cur], rem = keys.map(function (k, n) { return n; }).filter(function (n) { return !S[n]; });
      if (!rem.length) return;
      K.$$(svg, '.ko-try').forEach(function (e) { e.parentNode.parentNode.removeChild(e.parentNode); });
      if (!h) { say('没点中：点 bond 的中间、lone pair 的两个点，或 atom。', 'bad'); return; }
      if (!sel) {
        sel = h;
        var P = KO.pt(svg, h.ref);
        selEl = K.svg('circle', { 'class': 'ko-sel', cx: P.x, cy: P.y, r: 7 }); svg.appendChild(selEl);
        say('起点：' + KO.desc(svg, h.ref) + '。再点终点。');
        return;
      }
      var s = sel; sel = null; if (selEl) { selEl.parentNode.removeChild(selEl); selEl = null; }
      if (s.key === h.key) { say('已取消起点。'); return; }
      var ok = rem.filter(function (n) { return keys[n][0] === s.key && keys[n][1] === h.key; })[0];
      if (ok != null) {
        reveal(ok, 'got');
        say('✓ 对：' + KO.desc(svg, s.ref) + ' → ' + KO.desc(svg, h.ref) + '。', 'ok');
      } else {
        KO.arrow(svg, s.ref, h.ref, { cls: 'bad', bend: 0.35, 'try': true });
        var sf = rem.filter(function (n) { return keys[n][0] === s.key; })[0], st2 = rem.filter(function (n) { return keys[n][1] === h.key; })[0];
        var m = sf != null ? sf : st2 != null ? st2 : rem[0], want = keys[m];
        var why = sf != null ? '起点对，终点不对：应指向 ' + KO.desc(svg, want[3])
          : st2 != null ? '终点对，但应从 ' + KO.desc(svg, want[2]) + ' 出发'
          : '这支箭头不在 mark scheme 里。正确的是 ' + KO.desc(svg, want[2]) + ' → ' + KO.desc(svg, want[3]);
        reveal(m, 'miss');
        say('✗ ' + why + '（已显示正确箭头）。', 'bad');
      }
      marksUpdate();
      var left = keys.length - Object.keys(S).length;
      if (!left) {
        var got = Object.keys(S).filter(function (n) { return S[n] === 'got'; }).length;
        fb.textContent += ' 本步完成：' + got + ' / ' + keys.length + ' 支一次答对。';
      }
    }
    prev.addEventListener('click', function () { go(cur - 1); });
    next.addEventListener('click', function () { go(cur + 1); });
    reset.addEventListener('click', function () { state = steps.map(function () { return {}; }); go(0); });
    if (show) show.addEventListener('click', function () {
      keys.forEach(function (k, n) { if (!state[cur][n]) reveal(n, 'miss'); });
      marksUpdate(); say('已显示本步全部箭头。');
    });
    box.addEventListener('keydown', function (ev) {
      if (ev.key === 'ArrowRight') { go(cur + 1); ev.preventDefault(); }
      else if (ev.key === 'ArrowLeft') { go(cur - 1); ev.preventDefault(); }
    });
    go(0);
    return { el: box, go: go, next: function () { go(cur + 1); }, prev: function () { go(cur - 1); },
             step: function () { return cur; }, svg: function () { return svg; } };
  };

  window.KO = KO;
})();
