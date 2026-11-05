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
        /* tags draw on top of everything (depthTest off), so the symbol of an atom hidden behind a
           nearer atom would print onto it (CH₄'s back H read as "HC"): fade it out at render time
           when its view ray passes through a nearer atom's sphere */
        (function (idx, tag) {
          var pa = new T.Vector3(), pb = new T.Vector3(), cp = new T.Vector3();
          tag.onBeforeRender = function (rd, sc, cam) {
            cp.setFromMatrixPosition(cam.matrixWorld);
            ud.atoms[idx].getWorldPosition(pa); var da = pa.sub(cp), la = da.length(); da.divideScalar(la);
            var hide = ud.atoms.some(function (m, j) {
              if (j === idx || !m.visible) return false;
              m.getWorldPosition(pb); var db = pb.sub(cp), lb = db.length();
              if (lb >= la - 1e-6) return false;
              var rw = m.geometry.parameters.radius * m.getWorldScale(cp.clone()).x;
              return Math.acos(Math.min(1, da.dot(db.divideScalar(lb)))) < 0.8 * Math.asin(Math.min(1, rw / lb));
            });
            tag.material.opacity = hide ? 0 : 1;
          };
        })(i, t);
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

  // ---- ch4: lattice ----
  /* Crystal lattices (ch4, LO 4.2.1). K3.lattice(kind, n) is pure geometry in nm, no three.js:
       { atoms: [{ el, name, p:[x,y,z], r (drawing radius), rr (real ionic / metallic radius, optional), mol, layer }],
         bonds: [{ a, b, kind }]   kind = cov | hb | ionic | vdw,
         cell:  [[p1, p2], …]      unit-cell edges,
         info:  { nb: nearest neighbours of every atom (what hover highlights), … numbers for tests } }
     kind ∈ nacl mgo cu diamond graphite sio2 i2 c60 ice; n = 1–3 (unit cells along each edge; graphite: 2n layers;
     ice: (n + 1)³ hexagonal cells; c60: 1 molecule / 1 fcc cell / 2 × 2 × 2 fcc cells).
     K3.latticeMesh(T, api, data, o) draws it: InstancedMesh spheres, two-tone cylinder bonds, dashed hb / vdw
     (rows of short cylinders: a 1 px LineDashedMaterial line all but vanishes at a zoomed-out scale), thin
     unit-cell lines, optional delocalised-electron dots. */
  var LCOL = { Na: '#a06ae6', Cl: '#2fb24a', Mg: '#69c24a', O: '#e0362c', Cu: '#de7c3c', C: '#3f4652',
               Si: '#d9a66a', I: '#8a3fb0', H: '#b4c3d6' };
  K3.LCOL = LCOL;
  /* colour of an element on this card: C is lifted on a dark card, otherwise a dark-grey ball vanishes into it */
  K3.lcol = function (el, dark) { return dark && el === 'C' ? '#9aa4b2' : dark && el === 'H' ? '#dde6f2' : LCOL[el] || '#999999'; };
  K3.rng = function (seed) {   /* mulberry32: fixed-seed random numbers, so every run draws the same thing */
    return function () {
      seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  };
  function ldist(p, q) { return Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]); }
  function lbox(a, b, c, o) {   /* 12 edges of the parallelepiped at o spanned by a, b, c */
    o = o || [0, 0, 0];
    function P(i, j, k) { return [0, 1, 2].map(function (t) { return o[t] + i * a[t] + j * b[t] + k * c[t]; }); }
    var E = [], i, j;
    for (i = 0; i < 2; i++) for (j = 0; j < 2; j++) {
      E.push([P(0, i, j), P(1, i, j)]); E.push([P(i, 0, j), P(i, 1, j)]); E.push([P(i, j, 0), P(i, j, 1)]);
    }
    return E;
  }
  /* every pair of atoms d·(1 ± tol) apart (spatial hash); filter(a, b) may veto a pair */
  function llink(atoms, d, kind, tol, filter) {
    tol = tol || 0.03;
    var cs = d * (1 + tol), H = {}, out = [];
    function cell(p) { return [Math.floor(p[0] / cs), Math.floor(p[1] / cs), Math.floor(p[2] / cs)]; }
    atoms.forEach(function (a, i) { var c = cell(a.p).join(); (H[c] = H[c] || []).push(i); });
    atoms.forEach(function (a, i) {
      var c = cell(a.p), dx, dy, dz;
      for (dx = -1; dx <= 1; dx++) for (dy = -1; dy <= 1; dy++) for (dz = -1; dz <= 1; dz++) {
        (H[[c[0] + dx, c[1] + dy, c[2] + dz].join()] || []).forEach(function (j) {
          if (j <= i) return;
          var dd = ldist(a.p, atoms[j].p);
          if (Math.abs(dd - d) <= d * tol && (!filter || filter(a, atoms[j]))) out.push({ a: i, b: j, kind: kind });
        });
      }
    });
    return out;
  }
  function lnb(N, bonds, kinds) {
    var nb = [], i;
    for (i = 0; i < N; i++) nb.push([]);
    bonds.forEach(function (b) { if (kinds.indexOf(b.kind) >= 0) { nb[b.a].push(b.b); nb[b.b].push(b.a); } });
    return nb;
  }
  /* drop atoms with fewer than min bonds (repeat until none left) and renumber */
  function lprune(atoms, linkFn, min) {
    for (;;) {
      var bonds = linkFn(atoms), deg = atoms.map(function () { return 0; });
      bonds.forEach(function (b) { deg[b.a]++; deg[b.b]++; });
      var keep = atoms.filter(function (a, i) { return deg[i] >= min; });
      if (keep.length === atoms.length) return { atoms: atoms, bonds: bonds };
      atoms = keep;
    }
  }

  /* rock-salt: 6 : 6, anions on an fcc lattice, cations in every octahedral hole */
  function rocksalt(n, a, C, A) {
    var atoms = [], i, j, k;
    for (i = 0; i <= 2 * n; i++) for (j = 0; j <= 2 * n; j++) for (k = 0; k <= 2 * n; k++) {
      var s = (i + j + k) % 2 === 0 ? A : C;
      atoms.push({ el: s.el, name: s.name, ion: s.ion, p: [i * a / 2, j * a / 2, k * a / 2], rr: s.r, r: s.r * 0.55 });
    }
    var bonds = llink(atoms, a / 2, 'ionic');
    return { atoms: atoms, bonds: bonds, cell: [],
             info: { a: a, d: a / 2, nb: lnb(atoms.length, bonds, ['ionic']) } };
  }
  /* diamond sites in quarter-cell units 0..4n: fcc points (all even) + the fcc shifted by (¼, ¼, ¼) */
  function tetraSites(n, a) {
    var pts = [], i, j, k, q = a / 4;
    for (i = 0; i <= 4 * n; i++) for (j = 0; j <= 4 * n; j++) for (k = 0; k <= 4 * n; k++) {
      var e = i % 2 === 0 && j % 2 === 0 && k % 2 === 0, o = i % 2 === 1 && j % 2 === 1 && k % 2 === 1;
      if (e && (i + j + k) / 2 % 2 === 0) pts.push([i * q, j * q, k * q]);
      else if (o && (i + j + k - 3) / 2 % 2 === 0) pts.push([i * q, j * q, k * q]);
    }
    return pts;
  }
  var GEN = {
    nacl: function (n) {
      return rocksalt(n, 0.564, { el: 'Na', name: 'Na⁺ ion', ion: 1, r: 0.095 }, { el: 'Cl', name: 'Cl⁻ ion', ion: -1, r: 0.181 });
    },
    mgo: function (n) {
      return rocksalt(n, 0.421, { el: 'Mg', name: 'Mg²⁺ ion', ion: 2, r: 0.065 }, { el: 'O', name: 'O²⁻ ion', ion: -2, r: 0.140 });
    },
    cu: function (n) {
      var a = 0.361, atoms = [], i, j, k;
      for (i = 0; i <= 2 * n; i++) for (j = 0; j <= 2 * n; j++) for (k = 0; k <= 2 * n; k++)
        if ((i + j + k) % 2 === 0) atoms.push({ el: 'Cu', name: 'positive copper ion', p: [i * a / 2, j * a / 2, k * a / 2], rr: 0.128, r: 0.128 * 0.55 });
      var near = llink(atoms, a / Math.SQRT2, 'nb');
      return { atoms: atoms, bonds: [], cell: lbox([a, 0, 0], [0, a, 0], [0, 0, a]),
               info: { a: a, d: a / Math.SQRT2, nb: lnb(atoms.length, near, ['nb']), electrons: true } };
    },
    diamond: function (n) {
      /* corner atoms with no bond inside the box would float: drop them */
      var a = 0.357, pr = lprune(tetraSites(n, a).map(function (p) { return { el: 'C', name: 'C atom', p: p, r: 0.042 }; }),
                                 function (at) { return llink(at, a * Math.sqrt(3) / 4, 'cov'); }, 1);
      var atoms = pr.atoms, bonds = pr.bonds;
      return { atoms: atoms, bonds: bonds, cell: lbox([a, 0, 0], [0, a, 0], [0, 0, a]),
               info: { a: a, d: a * Math.sqrt(3) / 4, nb: lnb(atoms.length, bonds, ['cov']) } };
    },
    sio2: function (n) {
      /* ideal β-cristobalite: Si on diamond sites, an O half-way along every Si–Si line (Si–O 0.161 nm) */
      var dSiO = 0.161, a = 2 * dSiO * 4 / Math.sqrt(3);
      var pr = lprune(tetraSites(n, a).map(function (p) { return { el: 'Si', name: 'Si atom', p: p, r: 0.052 }; }),
                      function (at) { return llink(at, a * Math.sqrt(3) / 4, 'ss'); }, 1);
      var si = pr.atoms, ss = pr.bonds, atoms = si.slice(), bonds = [];
      ss.forEach(function (b) {
        var P = si[b.a].p, Q = si[b.b].p, o = atoms.length;
        atoms.push({ el: 'O', name: 'O atom', p: [(P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2, (P[2] + Q[2]) / 2], r: 0.04 });
        bonds.push({ a: b.a, b: o, kind: 'cov' }, { a: o, b: b.b, kind: 'cov' });
      });
      return { atoms: atoms, bonds: bonds, cell: lbox([a, 0, 0], [0, a, 0], [0, 0, a]),
               info: { a: a, d: dSiO, nb: lnb(atoms.length, bonds, ['cov']) } };
    },
    graphite: function (n) {
      /* hexagonal layers in the x–z plane, stacked along y, ABAB: layer B is layer A moved one bond length,
         so half its atoms sit right over atoms of A and half over hexagon centres */
      var A = 0.246, d = 0.142, gap = 0.335, W = 0.26 + 0.14 * n, raw = [], L, i, j, s;
      for (L = 0; L < 2 * n; L++) for (i = -14; i <= 14; i++) for (j = -14; j <= 14; j++) for (s = 0; s < 2; s++) {
        var x = i * A + j * A / 2, z = j * A * Math.sqrt(3) / 2 + s * d + (L % 2 ? d : 0);
        if (Math.abs(x) <= W && Math.abs(z) <= W) raw.push({ el: 'C', name: 'C atom', layer: L, p: [x, L * gap, z], r: 0.036 });
      }
      var same = function (p, q) { return p.layer === q.layer; };
      var pr = lprune(raw, function (at) { return llink(at, d, 'cov', 0.03, same); }, 2), atoms = pr.atoms;
      var vdw = llink(atoms, gap, 'vdw', 0.01, function (p, q) { return Math.abs(p.layer - q.layer) === 1; });
      var bonds = pr.bonds.concat(vdw);
      return { atoms: atoms, bonds: bonds, cell: [],
               info: { a: A, d: d, gap: gap, layers: 2 * n, nb: lnb(atoms.length, bonds, ['cov']) } };
    },
    i2: function (n) {
      /* orthorhombic (Cmca) iodine: x = c (wide), y = b (up), z = a (depth). Molecules lie in the c–b (x–y) plane,
         at the corners and face centres, two orientations (herringbone). I–I set to the bond length 0.267 nm. */
      var a = 0.7136, b = 0.4686, c = 0.9784, h = [0.1174 * c, 0.1543 * b, 0], s = 0.1335 / Math.hypot(h[0], h[1]);
      var h1 = [h[0] * s, h[1] * s, 0], h2 = [h1[0], -h1[1], 0];
      var types = [[[0, 0, 0], h1], [[0.5, 0.5, 0], h2], [[0, 0.5, 0.5], h1], [[0.5, 0, 0.5], h2]];   /* (c, b, a) fractions */
      var atoms = [], bonds = [], i, j, k, m = 0;
      for (i = 0; i <= n; i++) for (j = 0; j <= n; j++) for (k = 0; k <= n; k++) types.forEach(function (t) {
        var f = [t[0][0] + i, t[0][1] + j, t[0][2] + k];
        if (f[0] > n + 1e-9 || f[1] > n + 1e-9 || f[2] > n + 1e-9) return;
        var C = [f[0] * c, f[1] * b, f[2] * a], o = atoms.length;
        atoms.push({ el: 'I', name: 'I atom', mol: m, p: [C[0] + t[1][0], C[1] + t[1][1], C[2] + t[1][2]], r: 0.064 });
        atoms.push({ el: 'I', name: 'I atom', mol: m, p: [C[0] - t[1][0], C[1] - t[1][1], C[2] - t[1][2]], r: 0.064 });
        bonds.push({ a: o, b: o + 1, kind: 'cov' }); m++;
      });
      var vdw = llink(atoms, 0.350, 'vdw', 0.02, function (p, q) { return p.mol !== q.mol; });
      var dInter = Math.min.apply(null, vdw.map(function (v) { return ldist(atoms[v.a].p, atoms[v.b].p); }));
      return { atoms: atoms, bonds: bonds.concat(vdw), cell: lbox([c, 0, 0], [0, b, 0], [0, 0, a]),
               info: { dIntra: 0.267, dInter: dInter, molecules: m, nb: lnb(atoms.length, bonds, ['cov']) } };
    },
    c60: function (n) {
      /* truncated icosahedron: cyclic permutations of (0, ±1, ±3φ), (±1, ±(2+φ), ±2φ), (±φ, ±2, ±(2φ+1)), edge 2 → 0.144 nm */
      var ph = (1 + Math.sqrt(5)) / 2, base = [[0, 1, 3 * ph], [1, 2 + ph, 2 * ph], [ph, 2, 2 * ph + 1]], V = [], seen = {};
      var sc = n === 1 ? 0.072 : n === 2 ? 0.043 : 0.032, ar = n === 1 ? 0.032 : n === 2 ? 0.019 : 0.014;
      base.forEach(function (v) {
        [1, -1].forEach(function (sx) { [1, -1].forEach(function (sy) { [1, -1].forEach(function (sz) {
          var w = [sx * v[0], sy * v[1], sz * v[2]];
          [[w[0], w[1], w[2]], [w[1], w[2], w[0]], [w[2], w[0], w[1]]].forEach(function (u) {
            var key = u.map(function (x) { return x.toFixed(4); }).join();
            if (!seen[key]) { seen[key] = 1; V.push([u[0] * sc, u[1] * sc, u[2] * sc]); }
          });
        }); }); });
      });
      var tmpl = llink(V.map(function (p) { return { p: p }; }), 2 * sc, 'cov');
      var A = 1.417, cen = [], i, j, k, m = n === 1 ? 0 : n - 1;
      if (n === 1) cen.push([0, 0, 0]);
      else for (i = 0; i <= 2 * m; i++) for (j = 0; j <= 2 * m; j++) for (k = 0; k <= 2 * m; k++)
        if ((i + j + k) % 2 === 0) cen.push([i * A / 2, j * A / 2, k * A / 2]);
      var atoms = [], bonds = [];
      cen.forEach(function (C, mi) {
        var o = atoms.length;
        V.forEach(function (p) { atoms.push({ el: 'C', name: 'C atom', mol: mi, p: [C[0] + p[0], C[1] + p[1], C[2] + p[2]], r: ar }); });
        tmpl.forEach(function (b) { bonds.push({ a: o + b.a, b: o + b.b, kind: 'cov' }); });
      });
      return { atoms: atoms, bonds: bonds, cell: n === 1 ? [] : lbox([A, 0, 0], [0, A, 0], [0, 0, A]),
               info: { a: A, d: 2 * sc, molecules: cen.length, nb: lnb(atoms.length, bonds, ['cov']) } };
    },
    ice: function (n) {
      /* ice Ih: O on the hexagonal-diamond sites (O···O 0.276 nm, c up = y). One H on every O···O line, 0.10 nm
         from one O (covalent) and 0.176 nm from the other (hydrogen bond). Which O gets it: orient the O···O
         graph along an Euler circuit (odd-degree O joined to one extra vertex first), so every O has as many
         lines leaving as arriving → each inner O has exactly 2 covalent H + 2 hydrogen bonds. An O on the edge
         that ends up with fewer than 2 H gets one along an empty tetrahedral direction (still an H₂O molecule). */
      var d = 0.276, c = 8 * d / 3, a = d * Math.sqrt(8 / 3), m = n + 1;   /* m cells along every edge */
      var a1 = [a, 0, 0], a2 = [-a / 2, 0, a * Math.sqrt(3) / 2], cz = [0, c, 0];
      var basis = [[1 / 3, 2 / 3, 0], [2 / 3, 1 / 3, 0.5], [1 / 3, 2 / 3, 3 / 8], [2 / 3, 1 / 3, 7 / 8]], pad = [], i, j, k;
      for (i = -1; i <= m; i++) for (j = -1; j <= m; j++) for (k = -1; k <= m; k++) basis.forEach(function (f) {
        var u = i + f[0], v = j + f[1], w = k + f[2];
        pad.push({ p: [0, 1, 2].map(function (t) { return u * a1[t] + v * a2[t] + w * cz[t]; }),
                   inside: u >= 0 && u < m && v >= 0 && v < m && w >= 0 && w < m });
      });
      var pb = llink(pad, d, 'oo'), adj = pad.map(function () { return []; });
      pb.forEach(function (b) { adj[b.a].push(b.b); adj[b.b].push(b.a); });
      /* keep the inside O, then drop any left with < 2 O neighbours */
      var keep = pad.map(function (q) { return q.inside; }), changed = true;
      while (changed) {
        changed = false;
        pad.forEach(function (q, x) {
          if (keep[x] && adj[x].filter(function (y) { return keep[y]; }).length < 2) { keep[x] = false; changed = true; }
        });
      }
      var idx = {}, O = [];
      pad.forEach(function (q, x) { if (keep[x]) { idx[x] = O.length; O.push(x); } });
      var E = [];
      pb.forEach(function (b) { if (keep[b.a] && keep[b.b]) E.push([idx[b.a], idx[b.b]]); });
      var N = O.length, deg = O.map(function () { return 0; });
      E.forEach(function (e) { deg[e[0]]++; deg[e[1]]++; });
      var real = E.length;
      deg.forEach(function (g, x) { if (g % 2) E.push([x, N]); });
      var inc = []; for (i = 0; i <= N; i++) inc.push([]);
      E.forEach(function (e, x) { inc[e[0]].push(x); inc[e[1]].push(x); });
      var used = E.map(function () { return false; }), dir = E.map(function () { return null; }), ptr = inc.map(function () { return 0; });
      for (var s0 = 0; s0 <= N; s0++) {   /* Hierholzer: every closed walk leaves and enters each vertex equally often */
        var st = [s0];
        while (st.length) {
          var v = st[st.length - 1];
          while (ptr[v] < inc[v].length && used[inc[v][ptr[v]]]) ptr[v]++;
          if (ptr[v] === inc[v].length) { st.pop(); continue; }
          var e = inc[v][ptr[v]], w = E[e][0] === v ? E[e][1] : E[e][0];
          used[e] = true; dir[e] = [v, w]; st.push(w);
        }
      }
      var atoms = O.map(function (x) { return { el: 'O', name: 'O atom', mol: idx[x], p: pad[x].p, r: 0.048 }; });
      var bonds = [], nH = O.map(function () { return 0; });
      function addH(o, toward, len) {
        var P = atoms[o].p, u = [0, 1, 2].map(function (t) { return (toward[t] - P[t]) / len; }), h = atoms.length;
        atoms.push({ el: 'H', name: 'H atom', mol: o, p: [0, 1, 2].map(function (t) { return P[t] + 0.1 * u[t]; }), r: 0.028 });
        bonds.push({ a: o, b: h, kind: 'cov' }); nH[o]++;
        return h;
      }
      for (i = 0; i < real; i++) {
        var t0 = dir[i][0], t1 = dir[i][1], hh = addH(t0, atoms[t1].p, d);
        bonds.push({ a: hh, b: t1, kind: 'hb' });
      }
      O.forEach(function (x, o) {   /* edge O short of H: point one along a tetrahedral direction with no O */
        adj[x].filter(function (y) { return !keep[y]; }).forEach(function (y) {
          if (nH[o] < 2) addH(o, pad[y].p, d);
        });
      });
      var nb0 = lnb(atoms.length, bonds, ['cov', 'hb']), nb = nb0.map(function (list, x) {
        if (atoms[x].el !== 'O') return list;
        var ext = list.slice();
        list.forEach(function (h) { nb0[h].forEach(function (o2) { if (o2 !== x && ext.indexOf(o2) < 0) ext.push(o2); }); });
        return ext;
      });
      return { atoms: atoms, bonds: bonds, cell: [],
               info: { dOO: d, dOH: 0.1, dHB: d - 0.1, O: N, degO: deg, nb: nb } };
    }
  };
  K3.lattice = function (kind, n) {
    var g = GEN[kind];
    if (!g) return null;
    var out = g(Math.max(1, Math.min(3, n || 1)));
    out.kind = kind; out.n = n;
    return out;
  };

  /* bounding centre + radius (nm) of a lattice, counting the larger of the two radii so the real-size
     switch does not change the zoom */
  K3.latticeBounds = function (data) {
    var lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9];
    data.atoms.forEach(function (a) { for (var t = 0; t < 3; t++) { lo[t] = Math.min(lo[t], a.p[t]); hi[t] = Math.max(hi[t], a.p[t]); } });
    var c = [0, 1, 2].map(function (t) { return (lo[t] + hi[t]) / 2; }), R = 0;
    data.atoms.forEach(function (a) { R = Math.max(R, ldist(a.p, c) + Math.max(a.r, a.rr || 0)); });
    return { c: c, R: R };
  };

  /* o: { S (world units per nm), centre [nm], real (draw rr where an atom has one), seed }
     userData: { meshes, pick(raycaster) → atom index | -1, highlight(set | null), elec (or null), dispose() } */
  K3.latticeMesh = function (T, api, data, o) {
    o = o || {};
    var S = o.S || 1, c0 = o.centre || [0, 0, 0], g = new T.Group(), N = data.atoms.length, ud = { meshes: [] };
    var card = api.color('--card'), dark = card.r * 0.3 + card.g * 0.59 + card.b * 0.11 < 0.4;
    function W(p) { return new T.Vector3((p[0] - c0[0]) * S, (p[1] - c0[1]) * S, (p[2] - c0[2]) * S); }
    var pos = data.atoms.map(function (a) { return W(a.p); });
    var rad = data.atoms.map(function (a) { return (o.real && a.rr ? a.rr : a.r) * S; });
    var M = new T.Matrix4(), Q = new T.Quaternion(), V = new T.Vector3(), Y = new T.Vector3(0, 1, 0), I = new T.Quaternion();
    var seg = N > 1500 ? [14, 10] : N > 400 ? [20, 14] : [28, 18];
    var sph = new T.SphereGeometry(1, seg[0], seg[1]), cyl = new T.CylinderGeometry(1, 1, 1, 10, 1, true);
    var base = {}, dimc = {};
    function colOf(el) {
      if (!base[el]) { base[el] = new T.Color(K3.lcol(el, dark)); dimc[el] = base[el].clone().lerp(card, 0.86); }
      return base[el];
    }
    var byEl = {};
    data.atoms.forEach(function (a, i) { (byEl[a.el] = byEl[a.el] || []).push(i); });
    var where = [];   /* atom → [mesh, instance] */
    Object.keys(byEl).forEach(function (el) {
      var list = byEl[el], m = new T.InstancedMesh(sph, new T.MeshPhongMaterial({ color: 0xffffff, shininess: 55 }), list.length);
      list.forEach(function (ai, k) {
        M.compose(pos[ai], I, V.set(rad[ai], rad[ai], rad[ai])); m.setMatrixAt(k, M); m.setColorAt(k, colOf(el));
        where[ai] = [m, k];
      });
      m.userData = { idx: list, el: el }; m.computeBoundingSphere(); g.add(m); ud.meshes.push(m);
    });
    /* solid bonds: covalent = neutral grey rod matching the legend; ionic = thinner, lighter reference line */
    var solid = data.bonds.filter(function (b) { return b.kind === 'cov' || b.kind === 'ionic'; });
    var covCol = new T.Color(dark ? '#687280' : '#8b939e'), ionCol = new T.Color(dark ? '#4d5562' : '#b2b9c2');
    var halves = solid.map(function (b) {
      var isIon = b.kind === 'ionic';
      return { from: pos[b.a], to: pos[b.b], pair: b, r: (isIon ? 0.0046 : (o.bondR || 0.013)) * S, col: isIon ? ionCol : covCol };
    });
    function rodMatrix(A, B, r) {
      var d = B.clone().sub(A), L = d.length();
      Q.setFromUnitVectors(Y, d.normalize());
      return M.compose(A.clone().add(B).multiplyScalar(0.5), Q, V.set(r, L, r));
    }
    var rods = null;
    if (halves.length) {
      rods = new T.InstancedMesh(cyl, new T.MeshPhongMaterial({ color: 0xffffff, shininess: 30 }), halves.length);
      halves.forEach(function (h, k) {
        rods.setMatrixAt(k, rodMatrix(h.from, h.to, h.r));
        h.base = h.col; h.dim = h.base.clone().lerp(card, 0.86);
        rods.setColorAt(k, h.base);
      });
      g.add(rods);
    }
    /* dashed: hydrogen bonds (--s4) and id-id forces (--mut), from sphere surface to sphere surface */
    var dashes = [];
    data.bonds.forEach(function (b) {
      if (b.kind !== 'hb' && b.kind !== 'vdw') return;
      var A = pos[b.a], B = pos[b.b], u = B.clone().sub(A), L = u.length(); u.normalize();
      var s = A.clone().add(u.clone().multiplyScalar(rad[b.a] * 1.15)), e = B.clone().sub(u.clone().multiplyScalar(rad[b.b] * 1.15));
      var len = s.distanceTo(e), unit = 0.034 * S, k = Math.max(2, Math.round((len + unit * 0.45) / unit)), dl = len / (k - 0.45);
      for (var q = 0; q < k; q++) {
        var p0 = s.clone().add(u.clone().multiplyScalar(q * dl)), p1 = p0.clone().add(u.clone().multiplyScalar(dl * 0.55));
        dashes.push({ from: p0, to: p1, pair: b, kind: b.kind, r: (b.kind === 'hb' ? 0.0075 : 0.0052) * S });
      }
    });
    var dmesh = null;
    if (dashes.length) {
      var hbC = api.color('--s4'), vdC = api.color('--mut');
      dmesh = new T.InstancedMesh(cyl, new T.MeshBasicMaterial({ color: 0xffffff }), dashes.length);
      dashes.forEach(function (h, k) {
        dmesh.setMatrixAt(k, rodMatrix(h.from, h.to, h.r));
        h.base = h.kind === 'hb' ? hbC : vdC; h.dim = h.base.clone().lerp(card, 0.86); dmesh.setColorAt(k, h.base);
      });
      g.add(dmesh);
    }
    /* unit cell: thin lines */
    if (data.cell && data.cell.length) {
      var pts = [];
      data.cell.forEach(function (e) { pts.push(W(e[0]), W(e[1])); });
      g.add(new T.LineSegments(new T.BufferGeometry().setFromPoints(pts),
        new T.LineBasicMaterial({ color: api.color('--acc'), transparent: true, opacity: 0.78 })));
    }
    /* delocalised electrons: small dots doing a random walk inside the lattice (fixed seed, stratified start) */
    ud.elec = null;
    if (data.info.electrons) {
      var rnd = K3.rng(o.seed || 7), lo = new T.Vector3(1e9, 1e9, 1e9), hi = new T.Vector3(-1e9, -1e9, -1e9);
      pos.forEach(function (p) { lo.min(p); hi.max(p); });
      var ne = Math.max(42, Math.round(N * 2.8)), ep = [], ev = [], er = 0.0145 * S, step = 0.012 * S;
      var em = new T.InstancedMesh(new T.SphereGeometry(1, 10, 8), new T.MeshBasicMaterial({ color: api.color('--s1') }), ne);
      for (var x = 0; x < ne; x++) {
        var ox = x % 2, oy = (x >> 1) % 2, oz = (x >> 2) % 2;
        ep.push(new T.Vector3(
          lo.x + (ox * 0.47 + 0.03 + rnd() * 0.47) * (hi.x - lo.x),
          lo.y + (oy * 0.47 + 0.03 + rnd() * 0.47) * (hi.y - lo.y),
          lo.z + (oz * 0.47 + 0.03 + rnd() * 0.47) * (hi.z - lo.z)
        ));
        ev.push(new T.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).multiplyScalar(step));
      }
      var put = function () {
        ep.forEach(function (p, x) { M.compose(p, I, V.set(er, er, er)); em.setMatrixAt(x, M); });
        em.instanceMatrix.needsUpdate = true;
      };
      put(); g.add(em);
      ud.elec = {
        mesh: em, pos: ep,
        step: function (k) {
          for (var t = 0; t < (k || 1); t++) ep.forEach(function (p, x) {
            var v = ev[x];
            v.x += (rnd() - 0.5) * step * 0.6; v.y += (rnd() - 0.5) * step * 0.6; v.z += (rnd() - 0.5) * step * 0.6;
            if (v.length() > step) v.setLength(step);
            p.add(v);
            ['x', 'y', 'z'].forEach(function (ax) {
              if (p[ax] < lo[ax]) { p[ax] = lo[ax]; v[ax] = Math.abs(v[ax]); }
              if (p[ax] > hi[ax]) { p[ax] = hi[ax]; v[ax] = -Math.abs(v[ax]); }
            });
          });
          put();
        }
      };
    }
    ud.pos = pos;
    ud.pick = function (ray) {
      var hit = ray.intersectObjects(ud.meshes, false)[0];
      return hit && hit.instanceId != null ? hit.object.userData.idx[hit.instanceId] : -1;
    };
    /* set = { atom index: true } to keep bright (everything else shrinks + fades toward card); null = all bright */
    ud.highlight = function (set, focus) {
      Object.keys(byEl).forEach(function (el) {
        byEl[el].forEach(function (ai) {
          var w = where[ai], onA = !set || set[ai], scA = !set ? 1 : ai === focus ? 1.12 : onA ? 1 : 0.72, rA = rad[ai] * scA;
          M.compose(pos[ai], I, V.set(rA, rA, rA)); w[0].setMatrixAt(w[1], M);
          w[0].setColorAt(w[1], onA ? base[el] : dimc[el]);
        });
      });
      ud.meshes.forEach(function (m) { m.instanceColor.needsUpdate = true; m.instanceMatrix.needsUpdate = true; m.computeBoundingSphere(); });
      function on(b) { return !set || (set[b.a] && set[b.b]); }
      if (rods) {
        halves.forEach(function (h, k) {
          var ok = on(h.pair);
          rods.setMatrixAt(k, rodMatrix(h.from, h.to, h.r * (ok ? 1 : 0.6)));
          rods.setColorAt(k, ok ? h.base : h.dim);
        });
        rods.instanceColor.needsUpdate = true; rods.instanceMatrix.needsUpdate = true;
      }
      if (dmesh) {
        dashes.forEach(function (h, k) {
          var ok = on(h.pair);
          dmesh.setMatrixAt(k, rodMatrix(h.from, h.to, h.r * (ok ? 1 : 0.6)));
          dmesh.setColorAt(k, ok ? h.base : h.dim);
        });
        dmesh.instanceColor.needsUpdate = true; dmesh.instanceMatrix.needsUpdate = true;
      }
    };
    ud.dispose = function () {
      g.traverse(function (ob) {
        if (ob.geometry) ob.geometry.dispose();
        if (ob.material) ob.material.dispose();
        if (ob.isInstancedMesh && ob.dispose) ob.dispose();
      });
    };
    g.userData = ud;
    return g;
  };
  // ---- end ch4: lattice ----

  window.K3 = K3;
})();
