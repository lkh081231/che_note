/* che_note Colab kit — shared interactions, inlined into every html cell by tools/build_colab.py.
   Defines window.K once; each cell then calls K.init(root) on its own .k root. */
(function () {
  if (window.K) return;
  var K = {};
  K.$ = function (root, sel) { return root.querySelector(sel); };
  K.$$ = function (root, sel) { return Array.prototype.slice.call(root.querySelectorAll(sel)); };
  K.el = function (tag, attrs, html) {
    var e = document.createElement(tag);
    for (var a in attrs || {}) e.setAttribute(a, attrs[a]);
    if (html != null) e.innerHTML = html;
    return e;
  };
  K.svg = function (tag, attrs) {
    var e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (var a in attrs || {}) e.setAttribute(a, attrs[a]);
    return e;
  };
  /* superscript / subscript digits for building formula strings in JS */
  var SUP = { '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '+': '⁺', '-': '⁻' };
  K.sup = function (s) { return String(s).split('').map(function (c) { return SUP[c] || c; }).join(''); };
  K.nuc = function (A, Z, sym, q) {
    return '<span class="nuc"><sup>' + A + '</sup><sub>' + Z + '</sub></span>' + sym + (q ? K.sup(q) : '');
  };

  /* ask Colab to grow the output iframe after content changes; silent everywhere else */
  K.fit = function () {
    try {
      var r = document.querySelector('.k');
      var h = r ? Math.ceil(r.getBoundingClientRect().height) + 20 : document.documentElement.scrollHeight;
      if (window.google && google.colab && google.colab.output && google.colab.output.setIframeHeight)
        google.colab.output.setIframeHeight(h, true, { maxHeight: 5000 });
    } catch (e) { /* not in Colab */ }
  };

  /* nice round axis ticks from 0 to ≥ max */
  K.ticks = function (max, n) {
    var raw = max / (n || 4), mag = Math.pow(10, Math.floor(Math.log10(raw))), step = mag;
    [1, 2, 2.5, 5, 10].some(function (m) { step = m * mag; return step >= raw; });
    var out = [];
    for (var v = 0; v <= max + step * 0.999; v += step) out.push(+v.toPrecision(12));
    return out;
  };

  /* place an SVG text label next to (x, y) without touching any line segment in `avoid`
     ([[x1,y1,x2,y2],…]) or any rect already in `placed`; tries the candidate offsets in order.
     Every opaque thing on a chart must be in these lists — a label that hides a line looks like
     a broken line. Returns the text element. */
  function segHitsRect(s, r) {
    function inside(x, y) { return x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h; }
    if (inside(s[0], s[1]) || inside(s[2], s[3])) return true;
    var edges = [[r.x, r.y, r.x + r.w, r.y], [r.x, r.y + r.h, r.x + r.w, r.y + r.h], [r.x, r.y, r.x, r.y + r.h], [r.x + r.w, r.y, r.x + r.w, r.y + r.h]];
    return edges.some(function (e) {
      var d = (s[2] - s[0]) * (e[3] - e[1]) - (s[3] - s[1]) * (e[2] - e[0]);
      if (!d) return false;
      var t = ((e[0] - s[0]) * (e[3] - e[1]) - (e[1] - s[1]) * (e[2] - e[0])) / d;
      var u = ((e[0] - s[0]) * (s[3] - s[1]) - (e[1] - s[1]) * (s[2] - s[0])) / d;
      return t >= 0 && t <= 1 && u >= 0 && u <= 1;
    });
  }
  function rectsHit(a, b) { return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h; }
  K.label = function (svg, x, y, text, o) {
    o = o || {};
    var cands = o.cands || [[10, 22, 'start'], [10, -11, 'start'], [-10, 22, 'end'], [-10, -11, 'end'], [12, 5, 'start'], [-12, 5, 'end'],
                              [0, -14, 'middle'], [0, 26, 'middle'], [16, 34, 'start'], [-16, 34, 'end'], [16, -22, 'start'], [-16, -22, 'end']];
    var t = K.svg('text', { 'class': 'halo ' + (o.cls || '') });
    t.textContent = text; svg.appendChild(t);
    var vb = (svg.getAttribute('viewBox') || '0 0 9999 9999').split(/\s+/).map(Number);
    var best = null, bestBad = 1e9, pad = o.pad == null ? 2 : o.pad;
    for (var i = 0; i < cands.length; i++) {
      t.setAttribute('x', x + cands[i][0]); t.setAttribute('y', y + cands[i][1]); t.setAttribute('text-anchor', cands[i][2]);
      var b = t.getBBox(), r = { x: b.x - pad, y: b.y - pad, w: b.width + 2 * pad, h: b.height + 2 * pad };
      var bad = (o.avoid || []).filter(function (s) { return segHitsRect(s, r); }).length * 2 +
                (o.placed || []).filter(function (q) { return rectsHit(q, r); }).length * 2 +
                (r.x < vb[0] || r.y < vb[1] || r.x + r.w > vb[0] + vb[2] || r.y + r.h > vb[1] + vb[3] ? 1 : 0);
      if (bad < bestBad) { bestBad = bad; best = { c: cands[i], r: r }; }
      if (!bad) break;
    }
    t.setAttribute('x', x + best.c[0]); t.setAttribute('y', y + best.c[1]); t.setAttribute('text-anchor', best.c[2]);
    if (o.placed) o.placed.push(best.r);
    if (bestBad) t.setAttribute('data-clash', bestBad);   /* tests assert there is none */
    return t;
  };
  /* polyline points → segments for K.label's avoid list */
  K.segs = function (pts) {
    var out = [];
    for (var i = 1; i < pts.length; i++) out.push([pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1]]);
    return out;
  };

  K.store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* sandboxed */ } }
  };

  function norm(s) { return String(s).trim().toLowerCase().replace(/\s+/g, ' ').replace(/[−–]/g, '-'); }

  /* bind every widget inside root that is not bound yet; safe to call again after a cell
     rebuilds part of its DOM (e.g. a new quiz question) */
  function fresh(root, sel) {
    return K.$$(root, sel).filter(function (e) { if (e.__kBound) return false; e.__kBound = true; return true; });
  }
  K.init = function (root) {
    if (!root) return;

    /* reveal: <button class="reveal">答案</button><div class="ans">…</div> */
    fresh(root, 'button.reveal').forEach(function (b) {
      var label = b.textContent;
      b.addEventListener('click', function () {
        var a = b.nextElementSibling;
        while (a && !a.classList.contains('ans')) a = a.nextElementSibling;
        if (!a) return;
        var on = a.classList.toggle('show');
        b.textContent = on ? '收起' : label;
        K.fit();
      });
    });

    /* self-check fill-in: <input class="fill" data-ans="12|twelve"> */
    fresh(root, 'input.fill').forEach(function (inp) {
      var answers = inp.getAttribute('data-ans').split('|').map(norm);
      inp.setAttribute('autocomplete', 'off');
      var longest = Math.max.apply(null, answers.map(function (a) { return a.length; }));
      if (longest > 4) inp.style.width = (longest * 0.62 + 1.6) + 'em';
      inp.addEventListener('input', function () {
        var v = norm(inp.value);
        inp.classList.remove('good', 'badv');
        if (!v) return;
        var ok = answers.some(function (a) {
          if (a === v) return true;
          var x = parseFloat(a), y = parseFloat(v);
          return !isNaN(x) && !isNaN(y) && /^[-+]?[\d.]+$/.test(v) && Math.abs(x - y) < 1e-9;
        });
        inp.classList.add(ok ? 'good' : 'badv');
      });
    });

    /* single choice: <div class="mcq" data-ans="b"><button data-v="a">…</button>…<div class="why">…</div></div> */
    fresh(root, '.mcq').forEach(function (box) {
      var ans = box.getAttribute('data-ans');
      K.$$(box, 'button[data-v]').forEach(function (b) {
        b.addEventListener('click', function () {
          K.$$(box, 'button[data-v]').forEach(function (o) { o.classList.remove('good', 'badv'); });
          b.classList.add(b.getAttribute('data-v') === ans ? 'good' : 'badv');
          var why = K.$(box, '.why');
          if (why) why.classList.add('show');
          K.fit();
        });
      });
    });

    /* tabs: <div class="tabbar"><button data-tab="x">…</button></div> … <div data-pane="x"> */
    fresh(root, '.tabbar').forEach(function (bar) {
      var scope = bar.parentNode;
      var btns = K.$$(bar, 'button[data-tab]');
      function show(id) {
        btns.forEach(function (b) { b.classList.toggle('on', b.getAttribute('data-tab') === id); });
        K.$$(scope, ':scope > [data-pane]').forEach(function (p) { p.classList.toggle('show', p.getAttribute('data-pane') === id); });
        scope.dispatchEvent(new CustomEvent('tab', { detail: id }));
        K.fit();
      }
      btns.forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-tab')); }); });
      if (btns.length) show(btns[0].getAttribute('data-tab'));
    });

    /* LO checklist: <div class="lolist" data-key="ch01"> with <label class="chk"><input data-id="1.1.1">… */
    fresh(root, '.lolist').forEach(function (list) {
      var key = 'che9701:' + list.getAttribute('data-key');
      var saved = {};
      try { saved = JSON.parse(K.store.get(key) || '{}'); } catch (e) { saved = {}; }
      var boxes = K.$$(list, 'input[data-id]');
      var bar = K.$(list, '.bar > i'), count = K.$(list, '.count') || K.$(root, '.count');
      function refresh() {
        var n = 0;
        boxes.forEach(function (b) { b.closest('.chk').classList.toggle('done', b.checked); if (b.checked) n++; });
        if (bar) bar.style.width = (100 * n / boxes.length) + '%';
        if (count) count.textContent = n + ' / ' + boxes.length;
      }
      boxes.forEach(function (b) {
        b.checked = !!saved[b.getAttribute('data-id')];
        b.addEventListener('change', function () {
          saved[b.getAttribute('data-id')] = b.checked;
          K.store.set(key, JSON.stringify(saved));
          refresh();
        });
      });
      refresh();
    });

    if (root.__kInit) return;
    root.__kInit = true;

    /* tooltip for anything with data-tip (HTML or SVG) */
    var tip = K.el('div', { 'class': 'tip' });
    root.appendChild(tip);
    root.addEventListener('mousemove', function (ev) {
      var t = ev.target.closest ? ev.target.closest('[data-tip]') : null;
      if (!t || !root.contains(t)) { tip.classList.remove('show'); return; }
      tip.innerHTML = t.getAttribute('data-tip');
      tip.classList.add('show');
      var x = ev.clientX + 14, y = ev.clientY + 12;
      var w = tip.offsetWidth, h = tip.offsetHeight;
      if (x + w > window.innerWidth - 4) x = ev.clientX - w - 10;
      if (y + h > window.innerHeight - 4) y = ev.clientY - h - 10;
      tip.style.left = x + 'px'; tip.style.top = y + 'px';
    });
    root.addEventListener('mouseleave', function () { tip.classList.remove('show'); });

    if (window.ResizeObserver) new ResizeObserver(function () { K.fit(); }).observe(root);
    setTimeout(K.fit, 50);
  };

  /* ---------- chemistry helpers ---------- */
  var SYM = ('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr ' +
    'Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu ' +
    'Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn').split(' ');
  /* Aufbau order up to 4p (the syllabus stops at krypton) */
  var ORDER = [['1s', 2], ['2s', 2], ['2p', 6], ['3s', 2], ['3p', 6], ['4s', 2], ['3d', 10], ['4p', 6]];
  var LORD = { s: 0, p: 1, d: 2 };
  var CORES = [[36, 'Kr'], [18, 'Ar'], [10, 'Ne'], [2, 'He']];
  function writeOrder(a, b) { return a.n - b.n || LORD[a.l] - LORD[b.l]; }

  K.chem = {
    SYM: SYM,
    ORDER: ORDER,
    /* ground-state configuration of element Z with charge q (H–Kr, ≤ 36 electrons).
       Cr and Cu use 3d⁵4s¹ / 3d¹⁰4s¹; cations lose electrons from the highest n first (4s before 3d). */
    config: function (Z, q) {
      q = q || 0;
      var occ = {}, i, left = Z;
      ORDER.forEach(function (o) { occ[o[0]] = 0; });
      for (i = 0; i < ORDER.length && left > 0; i++) {
        var take = Math.min(ORDER[i][1], left); occ[ORDER[i][0]] = take; left -= take;
      }
      if (Z === 24) { occ['3d'] = 5; occ['4s'] = 1; }
      if (Z === 29) { occ['3d'] = 10; occ['4s'] = 1; }
      var subs = ORDER.map(function (o) { return { name: o[0], n: +o[0][0], l: o[0][1], cap: o[1] }; });
      if (q > 0) {
        for (var k = 0; k < q; k++) {
          var cand = subs.filter(function (s) { return occ[s.name] > 0; })
            .sort(function (a, b) { return b.n - a.n || LORD[b.l] - LORD[a.l]; })[0];
          if (!cand) return null;
          occ[cand.name]--;
        }
      } else if (q < 0) {
        for (k = 0; k < -q; k++) {
          var room = subs.filter(function (s) { return occ[s.name] < s.cap; })[0];
          if (!room) return null;
          occ[room.name]++;
        }
      }
      subs.forEach(function (s) { s.e = occ[s.name]; });
      var used = subs.filter(function (s) { return s.e > 0; }).sort(writeOrder);
      var total = used.reduce(function (t, s) { return t + s.e; }, 0);
      function str(list) { return list.map(function (s) { return s.name + K.sup(s.e); }).join(''); }
      var full = str(used), short = full;
      for (i = 0; i < CORES.length; i++) {
        if (CORES[i][0] >= total) continue;
        var core = K.chem.config(CORES[i][0], 0);
        if (core.used.every(function (c) { return occ[c.name] === c.e; })) {
          short = '[' + CORES[i][1] + ']' + str(used.filter(function (s) { return !core.used.some(function (c) { return c.name === s.name; }); }));
          break;
        }
      }
      var unpaired = 0, shells = {};
      subs.forEach(function (s) {
        var orbs = s.cap / 2; unpaired += s.e <= orbs ? s.e : s.cap - s.e;
        if (s.e) shells[s.n] = (shells[s.n] || 0) + s.e;
      });
      return { subs: subs, used: used, occ: occ, total: total, full: full, short: short, unpaired: unpaired, shells: shells };
    },
    /* arrows in each orbital box: Hund's rule, then pair up */
    boxes: function (e, cap) {
      var orbs = cap / 2, out = [], i;
      for (i = 0; i < orbs; i++) out.push(0);
      for (i = 0; i < e; i++) out[i % orbs]++;
      return out;
    },
    /* '1s2 2s2…' / '[Ar]3d6 4s2' / with superscripts → {name: count}, cores expanded; null if unreadable */
    parse: function (txt) {
      var s = String(txt).replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹]/g, function (c) { return '⁰¹²³⁴⁵⁶⁷⁸⁹'.indexOf(c); })
        .replace(/\s+/g, '').toLowerCase();
      var occ = {}, m = s.match(/^\[(he|ne|ar|kr)\]/);
      if (m) {
        var Zc = { he: 2, ne: 10, ar: 18, kr: 36 }[m[1]];
        K.chem.config(Zc, 0).used.forEach(function (u) { occ[u.name] = u.e; });
        s = s.slice(m[0].length);
      }
      /* written without spaces '3d64s2' is ambiguous, so s/p take one digit and d takes '10' or one digit */
      var re = /([1-4])(?:([sp])(\d)|(d)(10|\d))/g, mm, eaten = 0;
      while ((mm = re.exec(s))) {
        var name = mm[1] + (mm[2] || mm[4]);
        occ[name] = (occ[name] || 0) + (+(mm[3] || mm[5])); eaten += mm[0].length;
      }
      if (eaten !== s.length) return null;
      return occ;
    },
    same: function (a, b) {
      if (!a || !b) return false;
      var keys = {}; Object.keys(a).concat(Object.keys(b)).forEach(function (k) { keys[k] = 1; });
      return Object.keys(keys).every(function (k) { return (a[k] || 0) === (b[k] || 0); });
    }
  };

  window.K = K;
})();
