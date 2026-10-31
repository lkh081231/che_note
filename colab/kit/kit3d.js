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

  window.K3 = K3;
})();
