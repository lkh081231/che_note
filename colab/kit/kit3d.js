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
  /* cut-away ns sphere: three-quarters of the boundary sphere (90 % surface), the two cut faces
     shaded by psi² normalised within each layer between nodes (with one global scale the outer
     layers of 2s / 3s are ~0.4 % of the central peak and read as a flat wash); alpha → 0 at every
     node, so nodes are clear rings and the colour flips with the sign of psi. Each radial node is
     also drawn as a grey inner shell.
     The missing quarter is centred on +z, i.e. it faces the camera at ry = 0. */
  K3.sball = function (T, api, kind, scale, nodes) {
    var f = RAD[kind], g = new T.Group(), Rb = K3.rBound(kind, 0.9, 60), Rw = Rb * scale;
    var P0 = 3 * Math.PI / 4, PL = 3 * Math.PI / 2;
    var cA = api.color('--s1'), cB = api.color('--s2');
    /* face texture: u = distance from the y axis (0..Rb), v = y (−Rb..Rb) */
    var N = 384, cv = document.createElement('canvas'); cv.width = N / 2; cv.height = N;
    var cx = cv.getContext('2d'), img = cx.createImageData(N / 2, N);
    var edges = [0].concat(nodes || [], [Rb]), peak = edges.slice(1).map(function () { return 0; });
    function layer(r) { for (var q = 1; q < edges.length; q++) if (r <= edges[q]) return q - 1; return edges.length - 2; }
    for (var q = 0; q < 2000; q++) { var rr = q / 2000 * Rb, L = layer(rr); peak[L] = Math.max(peak[L], f(rr) * f(rr)); }
    for (var j = 0; j < N; j++) for (var i = 0; i < N / 2; i++) {
      var u = (i + 0.5) / (N / 2) * Rb, v = (0.5 - (j + 0.5) / N) * 2 * Rb, r = Math.sqrt(u * u + v * v), o = 4 * (j * N / 2 + i);
      if (r > Rb) { img.data[o + 3] = 0; continue; }
      var psi = f(r), c = psi >= 0 ? cA : cB;
      img.data[o] = c.r * 255; img.data[o + 1] = c.g * 255; img.data[o + 2] = c.b * 255;
      img.data[o + 3] = 255 * 0.92 * Math.pow(psi * psi / peak[layer(r)], 0.5);
    }
    cx.putImageData(img, 0, 0);
    var tex = new T.CanvasTexture(cv);
    function dir(phi) { return [-Math.cos(phi), Math.sin(phi)]; }   /* SphereGeometry's own phi convention */
    [P0, P0 + PL].forEach(function (phi) {
      var d = dir(phi), geo = new T.BufferGeometry();
      geo.setAttribute('position', new T.Float32BufferAttribute([0, -Rw, 0, Rw * d[0], -Rw, Rw * d[1], Rw * d[0], Rw, Rw * d[1], 0, Rw, 0], 3));
      geo.setAttribute('uv', new T.Float32BufferAttribute([0, 0, 1, 0, 1, 1, 0, 1], 2));
      geo.setIndex([0, 1, 2, 0, 2, 3]);
      g.add(new T.Mesh(geo, new T.MeshBasicMaterial({ map: tex, transparent: true, side: T.DoubleSide, depthWrite: false })));
    });
    function shell(rad, color, op) {
      var m = new T.Mesh(new T.SphereGeometry(rad, 64, 40, P0, PL),
        new T.MeshPhongMaterial({ color: color, transparent: true, opacity: op, side: T.DoubleSide, depthWrite: false, shininess: 30 }));
      g.add(m);
    }
    shell(Rw, f(Rb) >= 0 ? cA : cB, 0.22);
    (nodes || []).forEach(function (rn) { shell(rn * scale, api.color('--mut'), 0.18); });
    g.userData.rBound = Rb;
    return g;
  };

  window.K3 = K3;
})();
