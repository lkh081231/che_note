/* che_note Colab kit — 3D helpers, inlined only into html3d cells by tools/build_colab.py.
   Loads three.js core (pinned) from jsDelivr with a dynamic import; no import map and no
   examples/jsm addons, so there is no bare 'three' specifier to resolve. Drag-rotate and
   wheel-zoom are implemented here. If the CDN or WebGL is unavailable, the cell's
   .fallback block (a static SVG) is shown instead. */
(function () {
  if (window.K3) return;
  var K3 = {};
  var URL3 = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js';
  var loading = null;
  K3.load = function () {
    if (!loading) loading = import(URL3);
    return loading;
  };
  function webgl() {
    try { var c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); }
    catch (e) { return false; }
  }
  function cssVar(el, name) { return getComputedStyle(el).getPropertyValue(name).trim() || '#ffffff'; }

  /* K3.start(root, build): build(T, api) fills api.group; returns nothing.
     root must contain .stage, and may contain .fallback plus buttons [data-3d=reset|spin]. */
  K3.start = function (root, build) {
    var stage = root.querySelector('.stage');
    var fb = root.querySelector('.fallback');
    function fail(why) {
      if (stage) stage.style.display = 'none';
      if (fb) { fb.classList.add('show'); var w = fb.querySelector('.why'); if (w) w.textContent = why; }
      root.setAttribute('data-3d', 'fallback');
      if (window.K) K.fit();
    }
    if (!webgl()) { fail('WebGL 不可用'); return; }
    K3.load().then(function (T) {
      var W = stage.clientWidth || 600, H = stage.clientHeight || 380;
      var renderer = new T.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setSize(W, H);
      renderer.setClearColor(new T.Color(cssVar(root, '--card')));
      stage.appendChild(renderer.domElement);
      var scene = new T.Scene();
      var camera = new T.PerspectiveCamera(40, W / H, 0.05, 200);
      var DIST = 6;
      camera.position.set(0, 0, DIST);
      scene.add(new T.AmbientLight(0xffffff, 0.55));
      var key = new T.DirectionalLight(0xffffff, 0.9); key.position.set(3, 4, 5); scene.add(key);
      var rim = new T.DirectionalLight(0xffffff, 0.35); rim.position.set(-4, -2, -3); scene.add(rim);
      var group = new T.Group();
      scene.add(group);
      var api = { T: T, scene: scene, group: group, camera: camera, root: root, renderer: renderer,
                  dist: DIST, rx: 0.35, ry: -0.6, spin: false };
      api.color = function (name) { return new T.Color(cssVar(root, name)); };
      api.render = function () { renderer.render(scene, camera); };
      api.view = function () {
        group.rotation.set(api.rx, api.ry, 0);
        camera.position.set(0, 0, api.dist);
        camera.lookAt(0, 0, 0);
        api.render();
      };
      api.reset = function () { api.rx = api.rx0; api.ry = api.ry0; api.dist = api.dist0; api.view(); };
      build(T, api);
      api.rx0 = api.rx; api.ry0 = api.ry; api.dist0 = api.dist;

      /* drag to rotate, wheel / pinch to zoom */
      var c = renderer.domElement, drag = null;
      c.addEventListener('pointerdown', function (e) { drag = { x: e.clientX, y: e.clientY }; c.setPointerCapture(e.pointerId); c.style.cursor = 'grabbing'; });
      c.addEventListener('pointermove', function (e) {
        if (!drag) return;
        api.ry += (e.clientX - drag.x) * 0.01; api.rx += (e.clientY - drag.y) * 0.01;
        var lim = api.limit || 1.55;   /* a flat slice turned edge-on is just a line: cells may cap the tilt */
        api.rx = Math.max(-lim, Math.min(lim, api.rx));
        if (api.limit) api.ry = Math.max(-lim, Math.min(lim, api.ry));
        drag = { x: e.clientX, y: e.clientY }; api.view();
      });
      c.addEventListener('pointerup', function () { drag = null; c.style.cursor = 'grab'; });
      c.addEventListener('wheel', function (e) {
        e.preventDefault();
        api.dist = Math.max(1.2, Math.min(40, api.dist * (e.deltaY > 0 ? 1.1 : 0.9)));
        api.view();
      }, { passive: false });

      root.querySelectorAll('[data-3d=reset]').forEach(function (b) { b.addEventListener('click', api.reset); });
      root.querySelectorAll('[data-3d=spin]').forEach(function (b) {
        b.addEventListener('click', function () { api.spin = !api.spin; b.classList.toggle('on', api.spin); });
      });
      (function loop() {
        if (api.spin && document.visibilityState !== 'hidden') { api.ry += 0.008; api.view(); }
        requestAnimationFrame(loop);
      })();
      if (window.ResizeObserver) new ResizeObserver(function () {
        var w = stage.clientWidth, h = stage.clientHeight;
        if (!w || !h) return;
        renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); api.render();
      }).observe(stage);
      api.view();
      root.setAttribute('data-3d', 'ready');
      root.__k3 = api;
    }).catch(function (e) { fail('three.js 载入失败（' + (e && e.message ? e.message : e) + '）'); });
  };

  /* ---------- builders ---------- */

  /* text label sprite */
  /* text sprite; the canvas is sized to the text so long labels are never cut off.
     size = world height of the text line */
  K3.label = function (T, text, color, size) {
    var cv = document.createElement('canvas'), g = cv.getContext('2d'), font = 'italic 600 40px "Noto Sans","DejaVu Sans",sans-serif';
    g.font = font;
    var w = Math.ceil(g.measureText(text).width) + 16;
    cv.width = w; cv.height = 64;
    g = cv.getContext('2d'); g.font = font; g.fillStyle = color; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(text, w / 2, 34);
    var sp = new T.Sprite(new T.SpriteMaterial({ map: new T.CanvasTexture(cv), depthTest: false, transparent: true }));
    var h = size || 0.3;
    sp.scale.set(h * w / 64, h, 1);
    sp.renderOrder = 10;
    return sp;
  };

  /* x / y / z axes through the nucleus */
  K3.axes = function (T, api, len) {
    var g = new T.Group(), col = api.color('--mut').getStyle();
    var mat = new T.LineBasicMaterial({ color: api.color('--faint') });
    [['x', [1, 0, 0]], ['y', [0, 1, 0]], ['z', [0, 0, 1]]].forEach(function (a) {
      var v = new T.Vector3().fromArray(a[1]).multiplyScalar(len);
      g.add(new T.Line(new T.BufferGeometry().setFromPoints([v.clone().negate(), v]), mat));
      var s = K3.label(T, a[0], col, 0.3); s.position.copy(v.clone().multiplyScalar(1.1)); g.add(s);
    });
    /* nucleus: drawn on top, otherwise the p lobes (which meet at the origin) hide it. It must be
       'transparent' too — three.js draws all opaque objects before transparent ones, so an opaque
       dot would still be painted over by semi-transparent lobes whatever its renderOrder */
    var nuc = new T.Mesh(new T.SphereGeometry(0.06, 16, 12), new T.MeshBasicMaterial({ color: api.color('--fg'), depthTest: false, transparent: true }));
    nuc.renderOrder = 11;
    g.add(nuc);
    return g;
  };

  /* angular part of real hydrogen-like orbitals, as functions of a unit vector */
  var ANG = {
    s: function () { return 1; },
    px: function (x) { return x; }, py: function (x, y) { return y; }, pz: function (x, y, z) { return z; },
    dxy: function (x, y) { return 2 * x * y; }, dxz: function (x, y, z) { return 2 * x * z; }, dyz: function (x, y, z) { return 2 * y * z; },
    dx2y2: function (x, y) { return x * x - y * y; }, dz2: function (x, y, z) { return (3 * z * z - 1) / 2; }
  };
  /* boundary-surface style lobe mesh: radius ∝ angular part squared, two colours for the two phases */
  K3.orbital = function (T, api, type, scale, opacity) {
    var f = ANG[type], geo = new T.SphereGeometry(1, 120, 80), pos = geo.attributes.position;
    var cols = new Float32Array(pos.count * 3), cA = api.color('--s1'), cB = api.color('--s2'), v = new T.Vector3();
    var vals = [], mx = 0;
    for (var i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i).normalize();
      var a = f(v.x, v.y, v.z); vals.push(a); mx = Math.max(mx, Math.abs(a));
    }
    for (i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i).normalize();
      var r = type === 's' ? 1 : Math.pow(Math.abs(vals[i]) / mx, 2);
      pos.setXYZ(i, v.x * r * scale, v.y * r * scale, v.z * r * scale);
      var c = vals[i] >= 0 ? cA : cB; cols[3 * i] = c.r; cols[3 * i + 1] = c.g; cols[3 * i + 2] = c.b;
    }
    geo.setAttribute('color', new T.BufferAttribute(cols, 3));
    geo.computeVertexNormals();
    var mat = new T.MeshPhongMaterial({ vertexColors: true, shininess: 40, transparent: opacity < 1, opacity: opacity || 1,
                                        side: T.DoubleSide, depthWrite: !(opacity < 1) });
    return new T.Mesh(geo, mat);
  };

  /* hydrogen-like ns radial functions (a0 = 1) */
  var RAD = {
    '1s': function (r) { return Math.exp(-r); },
    '2s': function (r) { return (2 - r) * Math.exp(-r / 2) / 5.657; },
    '3s': function (r) { return (27 - 18 * r + 2 * r * r) * Math.exp(-r / 3) / 140.3; }
  };
  /* radius (a0) inside which the electron is found with probability p: integrates r²ψ² */
  K3.rBound = function (kind, p, R) {
    var f = RAD[kind], dr = R / 4000, tot = 0, acc = [], r, i;
    for (i = 0; i < 4000; i++) { r = (i + 0.5) * dr; tot += r * r * f(r) * f(r); acc.push(tot); }
    for (i = 0; i < 4000; i++) if (acc[i] >= p * tot) return (i + 1) * dr;
    return R;
  };
  /* 3D dot-density picture of an ns orbital: n points drawn with probability ∝ psi² per volume
     (r from r²psi², direction uniform), so the dots are the electron density. Colour = sign of psi.
     A dot cloud is a projection, so in a still view the nodes are hidden behind dots; they are
     drawn as translucent grey shells with a leader line to a "radial node" label outside the
     cloud, and seen by rotating / zooming / cutting. (Tried a strong dot layer on a cut face: the
     cloud then looks like it all lies in one plane.) With cut = true the front half (z > 0) is
     left out. userData.mat (caller sets size ∝ camera distance), userData.labels (sprites, size
     set by caller), userData.rMax = outermost dot radius (a0). */
  K3.dots = function (T, api, kind, n, scale, nodes, cut) {
    var f = RAD[kind], Rmax = K3.rBound(kind, 0.995, 80), g = new T.Group();
    var P = function (r) { return r * r * f(r) * f(r); }, mx = 0, i;
    for (i = 1; i <= 2000; i++) mx = Math.max(mx, P(i / 2000 * Rmax));
    var cA = api.color('--s1'), cB = api.color('--s2'), pts = [], cols = [], tries = 0;
    while (pts.length < n * 3 && tries < 5e6) {
      tries++;
      var r = Math.random() * Rmax;
      if (Math.random() * mx * 1.02 > P(r)) continue;
      var z = Math.random() * 2 - 1, ph = Math.random() * 2 * Math.PI, q = Math.sqrt(1 - z * z);
      var x = q * Math.cos(ph), y = q * Math.sin(ph);
      if (cut && z > 0) continue;
      pts.push(x * r * scale, y * r * scale, z * r * scale);
      var c = f(r) >= 0 ? cA : cB; cols.push(c.r, c.g, c.b);
    }
    var geo = new T.BufferGeometry();
    geo.setAttribute('position', new T.Float32BufferAttribute(pts, 3));
    geo.setAttribute('color', new T.Float32BufferAttribute(cols, 3));
    var mat = new T.PointsMaterial({ vertexColors: true, size: 0.02, sizeAttenuation: true, transparent: true, opacity: 0.7, depthWrite: false });
    g.add(new T.Points(geo, mat));
    /* leaders use the text colour: a grey line vanishes over the dense dots at the centre (3s node 1 is only ~7 % of the radius) */
    var grey = api.color('--mut'), ink = api.color('--fg'), labels = [], Rw = Rmax * scale;
    (nodes || []).forEach(function (rn, k) {
      var sh = new T.Mesh(new T.SphereGeometry(rn * scale, 48, 32, cut ? Math.PI : 0, cut ? Math.PI : 2 * Math.PI),
        new T.MeshPhongMaterial({ color: grey, transparent: true, opacity: 0.3, side: T.DoubleSide, depthWrite: false }));
      sh.renderOrder = 3; g.add(sh);
      /* leader from the shell to a label just outside the cloud; one direction per node so labels never stack */
      var a = [0.75, 2.39][k % 2], d = new T.Vector3(Math.cos(a), Math.sin(a), cut ? -0.25 : 0.25).normalize();
      var p0 = d.clone().multiplyScalar(rn * scale), p1 = d.clone().multiplyScalar(Rw * 1.04);
      var ln = new T.Line(new T.BufferGeometry().setFromPoints([p0, p1]), new T.LineBasicMaterial({ color: ink, depthTest: false, transparent: true }));
      ln.renderOrder = 12; g.add(ln);
      var dot = new T.Mesh(new T.SphereGeometry(Rw * 0.018, 10, 8), new T.MeshBasicMaterial({ color: ink, depthTest: false, transparent: true }));
      dot.position.copy(p0); dot.renderOrder = 12; g.add(dot);
      var lb = K3.label(T, nodes.length > 1 ? 'radial node ' + (k + 1) : 'radial node', ink.getStyle(), 0.3);
      lb.position.copy(d.clone().multiplyScalar(Rw * 1.04 + 0.01)); lb.center.set(Math.cos(a) > 0 ? 0 : 1, 0.5);
      lb.renderOrder = 13; g.add(lb); labels.push(lb);
    });
    g.userData = { mat: mat, labels: labels, rBound: K3.rBound(kind, 0.9, 80), rMax: Rmax };
    return g;
  };

  // ---- ch3: molecules (ball-and-stick), VSEPR geometry, lone-pair / hybrid / p lobes, angle arcs, arrows ----
  /* CPK-like colours, softened so every atom reads on both the light and the dark card */
  var CPK = { H: '#e6e9ee', C: '#4b5059', N: '#3d63dd', O: '#e0362c', F: '#86d04a', Cl: '#2fb24a', Br: '#a33a2e', I: '#8a3fb0',
              S: '#e2c11c', P: '#f08c1a', B: '#eba0a0', Be: '#a7d63a', Al: '#b3a7a7', Si: '#d9b58c', Xe: '#3aa6be',
              Na: '#a06ae6', Li: '#c08af2', Mg: '#69c24a', Ca: '#56a356', K: '#9050d6' };
  var ARAD = { H: 0.2, C: 0.3, N: 0.29, O: 0.28, F: 0.27, Cl: 0.36, Br: 0.39, I: 0.44, S: 0.37, P: 0.37, B: 0.29,
               Be: 0.28, Al: 0.4, Si: 0.39, Xe: 0.44 };
  K3.CPK = CPK; K3.ARAD = ARAD;
  K3.v = function (T, a) { return a && a.isVector3 ? a.clone() : new T.Vector3(a[0], a[1], a[2]); };
  function lum(hex) { var c = parseInt(hex.slice(1), 16); return (0.299 * (c >> 16) + 0.587 * (c >> 8 & 255) + 0.114 * (c & 255)) / 255; }

  /* upright (non-italic) text sprite, optionally on a rounded pill so it stays readable over lobes and bonds.
     o: { color, bg (pill colour or null), size (world height), bold } */
  K3.tag = function (T, text, o) {
    o = o || {};
    var cv = document.createElement('canvas'), g = cv.getContext('2d');
    var font = (o.bold === false ? '500' : '650') + ' 44px "Noto Sans","DejaVu Sans","Segoe UI",sans-serif';
    g.font = font;
    var pad = o.bg ? 18 : 8, w = Math.ceil(g.measureText(text).width) + 2 * pad, h = 64;
    cv.width = w; cv.height = h; g = cv.getContext('2d'); g.font = font;
    if (o.bg) {
      g.fillStyle = o.bg; var r = 22;
      g.beginPath(); g.moveTo(r, 2); g.lineTo(w - r, 2); g.quadraticCurveTo(w - 2, 2, w - 2, r); g.lineTo(w - 2, h - r);
      g.quadraticCurveTo(w - 2, h - 2, w - r, h - 2); g.lineTo(r, h - 2); g.quadraticCurveTo(2, h - 2, 2, h - r); g.lineTo(2, r);
      g.quadraticCurveTo(2, 2, r, 2); g.fill();
    }
    g.fillStyle = o.color || '#111'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, w / 2, h / 2 + 2);
    var tex = new T.CanvasTexture(cv); tex.anisotropy = 4;
    var sp = new T.Sprite(new T.SpriteMaterial({ map: tex, depthTest: false, transparent: true }));
    var s = o.size || 0.26; sp.scale.set(s * w / h, s, 1); sp.renderOrder = 20;
    sp.userData.aspect = w / h;
    return sp;
  };
  /* resize a K3.tag sprite to world height s (e.g. to keep labels a constant screen size while zooming) */
  K3.tagSize = function (sp, s) { sp.scale.set(s * sp.userData.aspect, s, 1); };

  /* cylinder from a to b */
  K3.rod = function (T, a, b, r, mat) {
    var A = K3.v(T, a), B = K3.v(T, b), d = B.clone().sub(A), L = d.length();
    var m = new T.Mesh(new T.CylinderGeometry(r, r, L, 20, 1), mat);
    m.position.copy(A).add(B).multiplyScalar(0.5);
    m.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), d.normalize());
    return m;
  };
  /* arrow a → b: shaft + cone head ending exactly at b. o: { r, head, cross } — cross puts the
     "+" bar near the tail, as a dipole arrow is drawn in exams (the head points to δ−) */
  K3.arrow = function (T, a, b, color, o) {
    o = o || {};
    var r = o.r || 0.035, A = K3.v(T, a), B = K3.v(T, b), d = B.clone().sub(A), L = d.length(), u = d.clone().normalize();
    var head = Math.min(o.head || 0.26, L * 0.45), g = new T.Group(), mat = new T.MeshPhongMaterial({ color: color, shininess: 30 });
    g.add(K3.rod(T, A, B.clone().sub(u.clone().multiplyScalar(head * 0.9)), r, mat));
    var cone = new T.Mesh(new T.ConeGeometry(r * 2.9, head, 24), mat);
    cone.position.copy(B).sub(u.clone().multiplyScalar(head / 2));
    cone.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), u); g.add(cone);
    if (o.cross) {
      var side = new T.Vector3(0, 0, 1).cross(u); if (side.lengthSq() < 1e-4) side = new T.Vector3(1, 0, 0).cross(u);
      side.normalize().multiplyScalar(Math.min(0.16, L * 0.12));
      var c = A.clone().add(u.clone().multiplyScalar(Math.min(0.22, L * 0.18)));
      g.add(K3.rod(T, c.clone().sub(side), c.clone().add(side), r * 0.9, mat));
    }
    return g;
  };

  /* teardrop lobe from `origin` along `dir` (length len, max half-width w): a lone pair, or the big
     lobe of a hybrid orbital. Pointed at the nucleus, round at the far end. */
  K3.lobe = function (T, origin, dir, len, w, color, opacity) {
    var pts = [], i, n = 28;
    for (i = 0; i <= n; i++) {
      var t = i / n;
      pts.push(new T.Vector2(w * Math.sin(Math.PI * Math.pow(t, 0.75)) * (0.35 + 0.65 * Math.sqrt(t)) + 1e-4, t * len));
    }
    var op = opacity == null ? 0.55 : opacity;
    var m = new T.Mesh(new T.LatheGeometry(pts, 40), new T.MeshPhongMaterial({ color: color, transparent: op < 1, opacity: op,
      shininess: 50, side: T.DoubleSide, depthWrite: op >= 1 }));
    m.position.copy(K3.v(T, origin));
    m.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), K3.v(T, dir).normalize());
    return m;
  };
  /* hybrid orbital (sp / sp² / sp³ all look alike): big lobe along dir + small back lobe */
  K3.hybrid = function (T, origin, dir, len, color, opacity) {
    var g = new T.Group(), d = K3.v(T, dir).normalize();
    g.add(K3.lobe(T, origin, d, len, len * 0.36, color, opacity));
    g.add(K3.lobe(T, origin, d.clone().negate(), len * 0.3, len * 0.15, color, opacity));
    return g;
  };
  /* unhybridised p orbital: two equal lobes along axis, one per phase colour */
  K3.porb = function (T, origin, axis, len, colorA, colorB, opacity) {
    var g = new T.Group(), d = K3.v(T, axis).normalize();
    g.add(K3.lobe(T, origin, d, len, len * 0.42, colorA, opacity));
    g.add(K3.lobe(T, origin, d.clone().negate(), len, len * 0.42, colorB || colorA, opacity));
    return g;
  };

  /* bond-angle arc between directions a and b (from centre), radius r, as a thin tube.
     Returns { mesh, mid } — mid is where the angle label goes (on the bisector, just outside the arc). */
  K3.arc = function (T, center, a, b, r, color) {
    var C = K3.v(T, center), A = K3.v(T, a).normalize(), B = K3.v(T, b).normalize(), pts = [], i;
    var ang = A.angleTo(B), ax = new T.Vector3().crossVectors(A, B);
    if (ax.lengthSq() < 1e-8) ax = Math.abs(A.y) < 0.9 ? new T.Vector3(0, 1, 0).cross(A) : new T.Vector3(1, 0, 0).cross(A);
    ax.normalize();
    for (i = 0; i <= 32; i++) pts.push(A.clone().applyAxisAngle(ax, ang * i / 32).multiplyScalar(r).add(C));
    var mesh = new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts), 48, 0.014, 6, false), new T.MeshBasicMaterial({ color: color }));
    var mid = A.clone().applyAxisAngle(ax, ang / 2).multiplyScalar(r * 1.35).add(C);
    return { mesh: mesh, mid: mid, deg: ang * 180 / Math.PI };
  };

  /* VSEPR electron-pair directions round a central atom at the origin.
     Returns { bonds: [[x,y,z]…], lps: [[x,y,z]…] } (unit vectors). Lone pairs go where they repel least:
     the top vertex (3, 4 pairs), equatorial (5), trans to each other (6).
     real = true squeezes the bonds of NH₃-like (107°) and H₂O-like (104.5°) molecules to the real angle. */
  K3.vsepr = function (bp, lp, real) {
    var n = bp + lp, s8 = Math.sqrt(8 / 9), c = Math.cos, s = Math.sin, d2r = Math.PI / 180, slots, lpi;
    if (n === 2) { slots = [[1, 0, 0], [-1, 0, 0]]; lpi = []; }
    else if (n === 3) { slots = [[0, 1, 0], [-c(30 * d2r), -0.5, 0], [c(30 * d2r), -0.5, 0]]; lpi = [0]; }
    else if (n === 4 && lp === 2) {
      var hb = (real ? 104.5 : 109.47) / 2 * d2r;
      return { bonds: [[-s(hb), -c(hb), 0], [s(hb), -c(hb), 0]], lps: [[0, 0.5774, 0.8165], [0, 0.5774, -0.8165]] };
    }
    else if (n === 4) {
      var top = [0, 1, 0], rest = [90, 210, 330].map(function (a) { return [s8 * c(a * d2r), -1 / 3, s8 * s(a * d2r)]; });
      if (lp === 1 && real) {
        var phi = Math.asin(Math.sqrt((1 - Math.cos(107 * d2r)) / 1.5));
        rest = [90, 210, 330].map(function (a) { return [s(phi) * c(a * d2r), -c(phi), s(phi) * s(a * d2r)]; });
      }
      if (lp === 3) return { bonds: [[0, -1, 0]], lps: rest.map(function (v) { return [v[0], -v[1], v[2]]; }) };
      slots = [top].concat(rest); lpi = [0];
    }
    else if (n === 5) {
      var eq = [0, 120, 240].map(function (a) { return [c(a * d2r), 0, s(a * d2r)]; });
      slots = eq.concat([[0, 1, 0], [0, -1, 0]]); lpi = [0, 1, 2];
    }
    else if (n === 6) { slots = [[0, 1, 0], [0, -1, 0], [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]]; lpi = [0, 1]; }
    else return null;
    var take = lpi.slice(0, lp), out = { bonds: [], lps: [] };
    slots.forEach(function (v, i) { (take.indexOf(i) >= 0 ? out.lps : out.bonds).push(v); });
    return out;
  };
  /* shape name + bond angle for bp bonding pairs and lp lone pairs (syllabus wording where it has one) */
  K3.SHAPES = {
    '2-0': ['linear', '180°'], '3-0': ['trigonal planar', '120°'], '2-1': ['non-linear (bent)', 'about 118°'],
    '4-0': ['tetrahedral', '109.5°'], '3-1': ['pyramidal', '107°'], '2-2': ['non-linear', '104.5°'],
    '5-0': ['trigonal bipyramidal', '120° and 90°'], '4-1': ['see-saw', 'about 117° and 87°'], '3-2': ['T-shaped', 'about 87°'],
    '2-3': ['linear', '180°'], '6-0': ['octahedral', '90°'], '5-1': ['square pyramidal', 'about 85°'], '4-2': ['square planar', '90°']
  };

  /* ball-and-stick molecule. spec = {
       atoms: [{ el, p:[x,y,z], r (optional radius) }],
       bonds: [[i, j, order (1|2|3), plane-normal (optional, for the offset of double/triple rods)]],
       lps:   [{ at: i, dir:[x,y,z], len (optional) }] }
     o: { labels: true, bondR: 0.07, lpColor, lpOpacity, scale }
     Bonds are two-tone (each half in its atom's colour). Returns a Group; userData = { atoms: [mesh], tags: [sprite], lps: [mesh], pos: [Vector3] } */
  K3.molecule = function (T, api, spec, o) {
    o = o || {};
    var g = new T.Group(), k = o.scale || 1, br = (o.bondR || 0.07) * k, ud = { atoms: [], tags: [], lps: [], pos: [] };
    var mats = {};
    function mat(el) { return mats[el] || (mats[el] = new T.MeshPhongMaterial({ color: CPK[el] || '#999999', shininess: 60 })); }
    spec.atoms.forEach(function (a) { ud.pos.push(K3.v(T, a.p).multiplyScalar(k)); });
    spec.atoms.forEach(function (a, i) {
      var r = (a.r || ARAD[a.el] || 0.36) * k;
      var m = new T.Mesh(new T.SphereGeometry(r, 36, 24), mat(a.el)); m.position.copy(ud.pos[i]); m.userData.el = a.el;
      g.add(m); ud.atoms.push(m);
      if (o.labels !== false) {
        var col = CPK[a.el] || '#999999', t = K3.tag(T, a.el, { color: lum(col) > 0.6 ? '#1b1e24' : '#ffffff', size: Math.max(0.17, r * 0.95) });
        t.position.copy(ud.pos[i]); g.add(t); ud.tags.push(t);
      }
    });
    (spec.bonds || []).forEach(function (b) {
      var A = ud.pos[b[0]], B = ud.pos[b[1]], order = b[2] || 1, d = B.clone().sub(A).normalize();
      var nrm = b[3] ? K3.v(T, b[3]) : new T.Vector3(0, 0, 1);
      var off = nrm.clone().cross(d); if (off.lengthSq() < 1e-6) off = new T.Vector3(0, 1, 0).cross(d);
      off.normalize();
      var shifts = order === 1 ? [0] : order === 2 ? [-1, 1] : [-1.6, 0, 1.6], r = order === 1 ? br : br * 0.62;
      shifts.forEach(function (sh) {
        var v = off.clone().multiplyScalar(sh * br * 1.15), a1 = A.clone().add(v), b1 = B.clone().add(v), mid = a1.clone().add(b1).multiplyScalar(0.5);
        g.add(K3.rod(T, a1, mid, r, mat(spec.atoms[b[0]].el)));
        g.add(K3.rod(T, mid, b1, r, mat(spec.atoms[b[1]].el)));
      });
    });
    var lpc = o.lpColor || (api ? api.color('--s5') : '#8a5cf0');
    (spec.lps || []).forEach(function (l) {
      var m = K3.lobe(T, ud.pos[l.at], l.dir, (l.len || 0.95) * k, 0.3 * k, lpc, o.lpOpacity == null ? 0.42 : o.lpOpacity);
      m.renderOrder = 2; g.add(m); ud.lps.push(m);
    });
    g.userData = ud;
    return g;
  };
  // ---- end ch3 ----

  window.K3 = K3;
})();
