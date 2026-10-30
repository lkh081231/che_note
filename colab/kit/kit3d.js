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
  /* dot-density picture of a thin slice through the nucleus: points inside a disc of radius R,
     |z| < slab, accepted with probability ∝ psi² (true density, so nodes come out as empty rings);
     coloured by the sign of psi so each node is also a colour boundary */
  K3.cloud = function (T, api, kind, n, R, scale) {
    var f = RAD[kind], pts = [], cols = [], slab = R * 0.03, mx = f(0) * f(0), tries = 0;
    var cA = api.color('--s1'), cB = api.color('--s2');
    while (pts.length < n * 3 && tries < 6e6) {
      tries++;
      var x = (Math.random() * 2 - 1) * R, y = (Math.random() * 2 - 1) * R, z = (Math.random() * 2 - 1) * slab;
      var r = Math.sqrt(x * x + y * y + z * z);
      if (r > R) continue;
      var psi = f(r);
      if (Math.random() * mx < psi * psi) {
        pts.push(x * scale, y * scale, z * scale);
        var c = psi >= 0 ? cA : cB; cols.push(c.r, c.g, c.b);
      }
    }
    var geo = new T.BufferGeometry();
    geo.setAttribute('position', new T.Float32BufferAttribute(pts, 3));
    geo.setAttribute('color', new T.Float32BufferAttribute(cols, 3));
    return new T.Points(geo, new T.PointsMaterial({ vertexColors: true, size: 0.022, sizeAttenuation: true }));
  };
  K3.ring = function (T, api, radius, color) {
    var pts = [];
    for (var i = 0; i <= 128; i++) { var a = i / 128 * Math.PI * 2; pts.push(new T.Vector3(Math.cos(a) * radius, Math.sin(a) * radius, 0)); }
    return new T.Line(new T.BufferGeometry().setFromPoints(pts),
      new T.LineDashedMaterial({ color: color, dashSize: 0.06, gapSize: 0.05 })).computeLineDistances();
  };

  window.K3 = K3;
})();
