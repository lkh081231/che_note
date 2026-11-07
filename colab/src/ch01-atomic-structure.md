<!-- md -->
# Chapter 1 Atomic structure

Cambridge International AS & A Level Chemistry 9701（2025 / 2026 / 2027）· **Physical chemistry**

- 内容边界与 learning outcome 逐字取自 syllabus；数值取自 data booklet；判分句式取自 2024–2026 Paper 2 的 mark scheme，引用写卷号。
- 🔬 / 🧊 / 📝 开头的 cell 是交互图（已经预先渲染好，打开就能用）。如果显示空白：**Runtime → Run all**（连本地运行时即可，几秒跑完）。
- 🧊 3D 图需要联网加载 three.js；拖动旋转、滚轮缩放。离线时会退回一张静态图。

<!-- md -->
## 1.1 Particles in the atom and atomic radius

### A. Atomic model

atom 大部分是 **empty space**：中间是一个非常小、非常 dense 的 **nucleus**（含 protons 和 neutrons），electrons 在 nucleus 外面的 **shells** 里。下面是 $^{4}_{2}\text{He}$ 的 Bohr model（不画 electron cloud）。

<!-- html: Bohr model of helium-4 -->
<h3>Bohr model of <span class="nuc"><sup>4</sup><sub>2</sub></span>He</h3>
<div class="row"><button data-m="schem" class="on">示意图（不按比例）</button><button data-m="real">按真实比例</button>
<span class="faint">鼠标移到各部分上看说明</span></div>
<svg class="am" viewBox="0 0 760 390" font-family="system-ui, sans-serif">
  <defs><marker id="am-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="am-dark"/></marker></defs>
  <rect x="0" y="0" width="760" height="390" fill="transparent"/>
  <circle cx="230" cy="190" r="150" class="am-shell" data-tip="<b>shell</b>：electrons 所在的 energy level；He 只有 1 个 shell（n = 1）"/>
  <g data-tip="<b>empty space</b>：nucleus 和 electrons 之间几乎什么都没有；atom 的体积绝大部分是 empty space"><rect x="120" y="70" width="60" height="40" fill="transparent"/></g>
  <g class="am-schem">
    <circle cx="230" cy="190" r="36" class="am-ring" data-tip="<b>nucleus</b>：very small, very dense；含 protons + neutrons（合称 nucleons）；几乎全部 mass；带 positive charge"/>
    <circle cx="217" cy="177" r="13" class="am-p" data-tip="<b>proton, p</b> — relative charge +1，relative mass 1"/>
    <circle cx="243" cy="177" r="13" class="am-n" data-tip="<b>neutron, n</b> — relative charge 0，relative mass 1"/>
    <circle cx="217" cy="203" r="13" class="am-n" data-tip="<b>neutron, n</b> — relative charge 0，relative mass 1"/>
    <circle cx="243" cy="203" r="13" class="am-p" data-tip="<b>proton, p</b> — relative charge +1，relative mass 1"/>
    <line x1="400" y1="300" x2="262" y2="214" class="am-lead" marker-end="url(#am-ah)"/>
    <text x="405" y="306" class="am-acc">nucleus</text>
    <text x="405" y="326" class="am-small">very dense — almost all the mass</text>
    <line x1="194" y1="122" x2="194" y2="150" class="am-guide"/><line x1="266" y1="122" x2="266" y2="150" class="am-guide"/>
    <line x1="196" y1="130" x2="264" y2="130" class="am-dim" marker-start="url(#am-ah)" marker-end="url(#am-ah)"/>
    <text x="230" y="118" text-anchor="middle" class="am-small">0.0034 pm</text>
  </g>
  <g class="am-real" style="display:none">
    <circle cx="230" cy="190" r="1.2" class="am-dark" data-tip="nucleus：按比例只有约 0.017 px，这个点已经放大了 70 倍"/>
    <line x1="400" y1="300" x2="234" y2="193" class="am-lead" marker-end="url(#am-ah)"/>
    <text x="405" y="306" class="am-acc">nucleus 在这里</text>
    <text x="405" y="326" class="am-small">（按比例只有约 0.017 px，画不出来）</text>
  </g>
  <circle cx="230" cy="40" r="7" class="am-e" data-tip="<b>electron, e</b> — relative charge −1，relative mass 1/1836"/>
  <circle cx="230" cy="340" r="7" class="am-e" data-tip="<b>electron, e</b> — relative charge −1，relative mass 1/1836"/>
  <line x1="372" y1="58" x2="337" y2="85" class="am-lead" marker-end="url(#am-ah)"/><text x="377" y="56" class="am-mut">shell</text>
  <line x1="92" y1="82" x2="140" y2="112" class="am-lead" marker-end="url(#am-ah)"/>
  <text x="88" y="64" text-anchor="end" class="am-mut">mostly</text><text x="88" y="82" text-anchor="end" class="am-mut">empty space</text>
  <line x1="80" y1="352" x2="80" y2="372" class="am-guide"/><line x1="380" y1="352" x2="380" y2="372" class="am-guide"/>
  <line x1="82" y1="366" x2="378" y2="366" class="am-dim" marker-start="url(#am-ah)" marker-end="url(#am-ah)"/>
  <text x="230" y="386" text-anchor="middle" class="am-small">62 pm（atom diameter）</text>
  <g transform="translate(560,150)">
    <circle cx="0" cy="0" r="10" class="am-p"/><text x="20" y="5">proton, p</text>
    <circle cx="0" cy="34" r="10" class="am-n"/><text x="20" y="39">neutron, n</text>
    <circle cx="0" cy="68" r="6" class="am-e"/><text x="20" y="73">electron, e</text>
    <path d="M110,0 L124,0 L124,34 L110,34 M124,17 L134,17" class="am-lead" fill="none"/>
    <text x="138" y="22" class="am-mut">nucleon</text>
  </g>
</svg>
<p class="faint am-note">示意图把 nucleus 画大了很多倍，才看得见里面的 protons 和 neutrons。</p>
<style>
.k .am-shell{fill:none;stroke:var(--faint);stroke-width:1.5;stroke-dasharray:6 5}
.k .am-ring{fill:var(--acc-soft);stroke:var(--acc);stroke-width:2}
.k .am-p{fill:#d9534f;stroke:#7a2421;stroke-width:1}
.k .am-n{fill:#5b7fd6;stroke:#26408a;stroke-width:1}
.k .am-e{fill:var(--fg)}
.k .am-dark{fill:var(--fg)}
.k .am-lead{stroke:var(--mut);stroke-width:1.2}
.k .am-guide{stroke:var(--faint);stroke-dasharray:2 3}
.k .am-dim{stroke:var(--mut);stroke-width:1.2}
.k svg text.am-acc{fill:var(--acc);font-size:16px}
.k svg text.am-mut{fill:var(--mut);font-size:15px}
.k svg text.am-small{fill:var(--mut);font-size:13px}
.k .am text{font-size:15px}
</style>
<script>
var notes = {
  schem: '示意图把 nucleus 画大了很多倍，才看得见里面的 protons 和 neutrons。',
  real: '按比例：atom 直径约 62 pm，nucleus 只有约 0.0034 pm，相差约 18 000 倍。打个比方：atom 如果有足球场那么大（约 100 m），nucleus 只有约 5.5 mm，像一粒豌豆放在中圈——其余全是 empty space。'
};
$root.querySelectorAll('[data-m]').forEach(function (b) {
  b.addEventListener('click', function () {
    var m = b.getAttribute('data-m');
    $root.querySelectorAll('[data-m]').forEach(function (o) { o.classList.toggle('on', o === b); });
    $root.querySelector('.am-schem').style.display = m === 'schem' ? '' : 'none';
    $root.querySelector('.am-real').style.display = m === 'real' ? '' : 'none';
    $root.querySelector('.am-note').textContent = notes[m];
  });
});
</script>

<!-- md -->
{{lo 1.1.1}}

### B. Relative charge and mass

relative charge 和 relative mass 都是相对值：以 proton 的 charge（+1.60 × 10⁻¹⁹ C）和 mass（1.67 × 10⁻²⁷ kg）为标准，所以**没有单位**。

| particle | symbol | relative charge | relative mass | 位置 |
|---|---|---:|---:|---|
| proton | p | +1 | 1 | nucleus |
| neutron | n | 0 | 1 | nucleus |
| electron | e | −1 | 1/1836 | shells（nucleus 外） |

distribution of mass and charge：

- proton 和 neutron 合称 **nucleons**，relative mass 都是 1；electron 只有 1/1836，可以忽略。所以 **most of the mass is in the nucleus, because protons and neutrons / nucleons are found in the nucleus**（9701/22 Feb/Mar 2025 Q2(c)(i) 的得分句）。
- nucleus 只有 protons（+）和 neutrons（0），所以带 **positive charge**；negative charge 在 nucleus 外的 electrons 上。
- neutral atom 里 number of protons = number of electrons，整体 charge 为 0。

{{lo 1.1.2}}

{{lo 1.1.4}}

### C. Standard representation of an atom

$^{A}_{Z}\text{X}$ —— *A* 写左上，*Z* 写左下，*X* 是元素符号。

- *A* = **mass number / nucleon number** = number of protons + number of neutrons
- *Z* = **atomic number / proton number** = number of protons

| 求 | 算法 |
|---|---|
| number of protons | *Z* |
| number of neutrons | *A* − *Z* |
| number of electrons（neutral atom） | *Z* |
| number of electrons（ion，charge *q*） | *Z* − *q*（cation 少 electrons，anion 多 electrons） |

例：$^{23}_{11}\text{Na}^{+}$ → p = 11，n = 23 − 11 = 12，e = 11 − 1 = 10。

{{lo 1.1.3}}

{{lo 1.1.6}}

<!-- html: p / n / e 计算器 + 自测 -->
<h3>p / n / e 计算器</h3>
<div class="row">element <select class="pz"></select>
  <i>A</i> (nucleon number) <input type="number" class="pa" min="1" max="300" value="23">
  charge <select class="pq"></select></div>
<div class="card pout"></div>
<h4>自测：填出每个 species 的 p / n / e（填对变绿）</h4>
<table class="pquiz"><tr><th>species</th><th>protons</th><th>neutrons</th><th>electrons</th></tr></table>
<style>
.k .pout .big{font-size:28px;margin:2px 0 6px}
.k .pout .err{color:var(--bad)}
.k .pquiz td:first-child{font-size:17px}
</style>
<script>
var S = K.chem.SYM, zs = $root.querySelector('.pz'), as = $root.querySelector('.pa'), qs = $root.querySelector('.pq');
S.forEach(function (s, i) { zs.appendChild(K.el('option', { value: i + 1 }, (i + 1) + '  ' + s)); });
[-3, -2, -1, 0, 1, 2, 3].forEach(function (q) {
  qs.appendChild(K.el('option', { value: q }, q === 0 ? '0（neutral atom）' : (q > 0 ? q + '+' : -q + '−')));
});
zs.value = 11; qs.value = 1;
function qtxt(q) { return q === 0 ? '' : (Math.abs(q) === 1 ? '' : Math.abs(q)) + (q > 0 ? '+' : '-'); }
function show() {
  var Z = +zs.value, A = +as.value, q = +qs.value, sym = S[Z - 1], out = $root.querySelector('.pout');
  var head = '<div class="big">' + K.nuc(A, Z, sym, qtxt(q)) + '</div>';
  if (!(A >= Z)) { out.innerHTML = head + '<p class="err">A 不能小于 Z：nucleon number 至少等于 proton number。</p>'; return; }
  if (Z - q < 0) { out.innerHTML = head + '<p class="err">electrons 不能是负数。</p>'; return; }
  out.innerHTML = head +
    '<p>protons = <i>Z</i> = <b>' + Z + '</b></p>' +
    '<p>neutrons = <i>A</i> − <i>Z</i> = ' + A + ' − ' + Z + ' = <b>' + (A - Z) + '</b></p>' +
    '<p>electrons = <i>Z</i> − <i>q</i> = ' + Z + (q >= 0 ? ' − ' + q : ' − (−' + (-q) + ')') + ' = <b>' + (Z - q) + '</b>' +
    (q > 0 ? '　（cation：失去 ' + q + ' 个 electron）' : q < 0 ? '　（anion：得到 ' + (-q) + ' 个 electron）' : '　（neutral：electrons = protons）') + '</p>';
}
[zs, as, qs].forEach(function (e) { e.addEventListener('input', show); });
show();
var quiz = [['Mg', 24, 2], ['Al', 27, 3], ['Fe', 56, 3], ['Cr', 52, 0], ['Mn', 55, 0], ['Cl', 37, -1], ['O', 16, -2], ['S', 32, -2], ['Ir', 191, 0], ['Rh', 103, 0]];
var tb = $root.querySelector('.pquiz');
quiz.forEach(function (r) {
  var Z = S.indexOf(r[0]) + 1, tr = K.el('tr');
  tr.innerHTML = '<td>' + K.nuc(r[1], Z, r[0], qtxt(r[2])) + '</td>' +
    '<td><input class="fill" data-ans="' + Z + '"></td><td><input class="fill" data-ans="' + (r[1] - Z) + '"></td>' +
    '<td><input class="fill" data-ans="' + (Z - r[2]) + '"></td>';
  tb.appendChild(tr);
});
</script>

<!-- md -->
### D. Behaviour of beams in an electric field

p、n、e 以**相同的 velocity** 射入两块带电 plate 之间的 electric field：

| particle | charge | 偏转方向 | 偏转大小 |
|---|---|---|---|
| proton | +1 | towards the **negative** plate | small |
| neutron | 0 | none — travels straight through | none |
| electron | −1 | towards the **positive** plate | large（electron 的 mass 只有 proton 的 1/1836） |

为什么 electron 偏得多：两者 charge 大小一样，但 electron **lighter / smaller mass**，所以偏转大得多。mark scheme 接受 heavier / higher mass-to-charge ratio / greater momentum / "x are lighter"；只说 "electrons have negligible mass"（没有比较）不给分，说 protons have greater charge density 判错（9701/22 May/June 2026 Q2(a)(ii)）。

画图题（9701/22 Feb/Mar 2025 Q2(c)(iii)）：neutron 画成从同一 source 出发的**直线**；electron 画成往**相反方向**弯、而且**弯得比 proton 多得多**的曲线，并标清楚。

<!-- html: p / n / e beams in an electric field -->
<h3>Beams of p, n, e in an electric field</h3>
<div class="row">
  <label><input type="checkbox" class="bp" checked> proton</label>
  <label><input type="checkbox" class="bn" checked> neutron</label>
  <label><input type="checkbox" class="be" checked> electron</label>
  <span style="margin-left:12px">plate voltage</span> <input type="range" class="bv" min="3" max="10" value="5">
</div>
<div class="row"><button data-b="schem" class="on">示意（不按比例）</button><button data-b="real">按真实比例（1 : 1836）</button></div>
<svg class="bm" viewBox="0 0 760 414" font-family="system-ui, sans-serif">
  <defs>
    <marker id="bm-p" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--pos)"/></marker>
    <marker id="bm-n" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--neu)"/></marker>
    <marker id="bm-e" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--fg)"/></marker>
    <marker id="bm-f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--faint)"/></marker>
  </defs>
  <g class="bm-field"></g>
  <g class="bm-mask"></g>
  <rect x="220" y="40" width="340" height="12" class="bm-plate bm-plate-pos"/>
  <rect x="220" y="348" width="340" height="12" class="bm-plate bm-plate-neg"/>
  <text x="390" y="30" text-anchor="middle" class="bm-pos">+ + + + +　positive plate　+ + + + +</text>
  <text x="390" y="382" text-anchor="middle" class="bm-neg">− − − − −　negative plate　− − − − −</text>
  <rect x="22" y="185" width="40" height="30" rx="4" class="bm-src"/>
  <text x="42" y="235" text-anchor="middle" class="bm-small">source</text>
  <g class="bm-paths"></g>
  <g class="bm-zoom"></g>
  <g class="bm-dots"></g>
  <text x="10" y="408" class="bm-small bm-foot"></text>
</svg>
<style>
.k .bm-plate{fill:var(--line)}
.k .bm-plate-pos{stroke:var(--pos);stroke-width:2}
.k .bm-plate-neg{stroke:var(--neg);stroke-width:2}
.k .bm-src{fill:var(--acc-soft);stroke:var(--acc)}
.k svg text.bm-pos{fill:var(--pos);font-size:14px;font-weight:600}
.k svg text.bm-neg{fill:var(--neg);font-size:14px;font-weight:600}
.k svg text.bm-small{fill:var(--mut);font-size:13px}
.k .bm-field line{stroke:var(--faint);stroke-width:1.2;stroke-dasharray:4 5;opacity:.7}
.k .bm-paths path{fill:none;stroke-width:3}
.k svg text.bm-lab{font-size:15px;font-weight:600}
.k .bm-mask rect{fill:var(--card)}
.k .bm-dots circle{stroke:var(--card);stroke-width:1.5}
.k svg .bm-dots text{fill:var(--card);font-size:13px;font-weight:700}
.k .bm-zbox{fill:var(--card);stroke:var(--mut);stroke-width:1}
.k .bm-zsrc{fill:none;stroke:var(--mut);stroke-width:1.2}
.k .bm-zlead{stroke:var(--mut);stroke-width:1;stroke-dasharray:3 3}
.k .bm-zoom path{fill:none;stroke-width:3}
</style>
<script>
var g = $root.querySelector('.bm-paths'), dots = $root.querySelector('.bm-dots'), mode = 'schem';
var Y0 = 200, X0 = 62, XA = 220, XB = 560, GAP = 140, fieldBox;
/* field lines run + plate → − plate: the way a positive charge is pushed */
(function () {
  var f = $root.querySelector('.bm-field');
  for (var x = 248; x <= 540; x += 58) f.appendChild(K.svg('line', { x1: x, y1: 58, x2: x, y2: 340, 'marker-end': 'url(#bm-f)' }));
  var t = K.svg('text', { x: 256, y: 78, 'class': 'bm-small halo' }); t.textContent = 'electric field'; f.appendChild(t);
  fieldBox = function () { var b = t.getBBox(); return { x: b.x - 3, y: b.y - 3, w: b.width + 6, h: b.height + 6 }; };
})();
/* inside the field the path is y = Y0 + dir·k·u² (u = x − XA): drawn as the exact quadratic Bézier
   (control point at u/2 on the entry line), so the 1836× electron curls smoothly instead of a
   coarsely sampled polyline with a kink; pts are sampled densely only for label avoidance */
function track(k, dir, xe) {
  var XE = xe || 610, u = XB - XA, hit = false;
  if (k > 0 && k * u * u >= GAP) { u = Math.sqrt(GAP / k); hit = true; }
  var x1 = XA + u, y1 = Y0 + dir * k * u * u, pts = [[X0, Y0], [XA, Y0]];
  for (var i = 1; i <= 40; i++) { var t = u * i / 40; pts.push([XA + t, Y0 + dir * k * t * t]); }
  var f = function (v) { return v.toFixed(2); };
  var d = 'M' + X0 + ',' + Y0 + ' L' + XA + ',' + Y0 + ' Q' + f(XA + u / 2) + ',' + Y0 + ' ' + f(x1) + ',' + f(y1);
  if (!hit) {
    var s = dir * 2 * k * u, xe2 = XE, ye = y1 + s * (XE - x1);
    if (ye < 12) { xe2 = x1 + (12 - y1) / s; ye = 12; }
    if (ye > 388) { xe2 = x1 + (388 - y1) / s; ye = 388; }
    pts.push([xe2, ye]); d += ' L' + f(xe2) + ',' + f(ye);
  }
  return { pts: pts, d: d, end: pts[pts.length - 1], hit: hit };
}
var movers = [];
function draw() {
  var V = +$root.querySelector('.bv').value / 5;
  /* real mode keeps e : p = 1836 : 1; the proton's own bend is kept just large enough (slider ≥ 3)
     that its line clears the neutron's arrowhead by ≥ 8 px (arrowhead half-height ≈ 9 px), otherwise the two beams merge into one */
  var kp = (mode === 'schem' ? 0.0005 : 0.00024) * V, ke = kp * (mode === 'schem' ? 2.2 : 1836);
  var beams = [
    ['bp', 'proton, p', 'var(--pos)', 'bm-p', track(kp, 1), 'towards the negative plate', '+'],
    ['bn', 'neutron, n', 'var(--neu)', 'bm-n', track(0, 0, 586), 'not deflected', '0'],   /* ends earlier so its arrowhead never sits on the proton's */
    ['be', 'electron, e', 'var(--fg)', 'bm-e', track(ke, -1), 'towards the positive plate', '−']
  ];
  var mask = $root.querySelector('.bm-mask');
  g.innerHTML = ''; dots.innerHTML = ''; mask.innerHTML = ''; movers = [];
  var on = beams.filter(function (b) { return $root.querySelector('.' + b[0]).checked; });
  var avoid = [[XA, 40, XB, 40], [XA, 52, XB, 52], [XA, 348, XB, 348], [XA, 360, XB, 360]], placed = [fieldBox()];
  on.forEach(function (b) { avoid = avoid.concat(K.segs(b[4].pts)); });
  /* real mode: at 1836× the electron's parabola has a vertex radius of ~1 px, so it reads as a right
     angle; a ×Z inset of the entry corner (same exact quadratic, clipped to the box) shows it is a curve */
  var zoom = $root.querySelector('.bm-zoom'); zoom.innerHTML = '';
  if (mode === 'real' && $root.querySelector('.be').checked) {
    var Z = 20, BX = 30, BY = 262, BW = 150, BH = 104, L0 = XA - 4, T0 = Y0 - 4.6;   /* region x XA−4…XA+3.5, y Y0−4.6…Y0+0.6 */
    var mx = function (x) { return (BX + (x - L0) * Z).toFixed(1); }, my = function (y) { return (BY + (y - T0) * Z).toFixed(1); };
    var ue = Math.min(Math.sqrt((Y0 - T0) / ke), L0 + BW / Z - XA), ye = Y0 - ke * ue * ue;
    zoom.appendChild(K.svg('rect', { x: L0 - 1.5, y: T0 - 1.5, width: BW / Z + 3, height: BH / Z + 3, 'class': 'bm-zsrc' }));
    zoom.appendChild(K.svg('line', { x1: L0 - 1.5, y1: T0 + BH / Z + 1.5, x2: BX + 70, y2: BY, 'class': 'bm-zlead' }));
    zoom.appendChild(K.svg('rect', { x: BX, y: BY, width: BW, height: BH, rx: 4, 'class': 'bm-zbox' }));
    zoom.appendChild(K.svg('path', { d: 'M' + mx(XA) + ',' + my(Y0) + ' L' + (BX + BW) + ',' + my(Y0), style: 'stroke:var(--neu)' }));
    var ze = K.svg('path', { d: 'M' + BX + ',' + my(Y0) + ' L' + mx(XA) + ',' + my(Y0) + ' Q' + mx(XA + ue / 2) + ',' + my(Y0) + ' ' + mx(XA + ue) + ',' + my(ye), style: 'stroke:var(--fg)' });
    ze.setAttribute('data-tip', '放大 ×' + Z + '：electron 进 field 的地方——也是一条 parabola，只是弯得极急');
    zoom.appendChild(ze);
    var zt = K.svg('text', { x: BX + 7, y: BY + 18, 'class': 'bm-small' }); zt.textContent = '放大 ×' + Z; zoom.appendChild(zt);
    var zc = K.svg('text', { x: BX + 7, y: BY + 36, 'class': 'bm-small' }); zc.textContent = '也是 parabola'; zoom.appendChild(zc);
    placed.push({ x: BX - 2, y: BY - 2, w: BW + 4, h: BH + 4 });
  }
  on.forEach(function (b) {
    var t = b[4];
    var p = K.svg('path', { d: t.d, style: 'stroke:' + b[2], 'marker-end': t.hit ? '' : 'url(#' + b[3] + ')' });
    p.setAttribute('data-tip', '<b>' + b[1] + '</b>：' + b[5] + (t.hit ? '（撞上 plate 了）' : ''));
    g.appendChild(p);
    /* a moving particle that carries its charge sign, so which way it is pushed reads at a glance */
    var d = K.svg('g', {}), c = K.svg('circle', { r: 9, style: 'fill:' + b[2] }), s = K.svg('text', { 'text-anchor': 'middle', y: 4.5 });
    s.textContent = b[6]; d.appendChild(c); d.appendChild(s); dots.appendChild(d);
    /* a beam that hits the plate gets an impact mark instead of an arrowhead */
    if (t.hit) g.appendChild(K.svg('circle', { cx: t.end[0], cy: t.end[1], r: 5, style: 'fill:' + b[2] }));
    /* particles vanish before the arrowhead so they never sit on it: markers scale with
       stroke-width (markerUnits=strokeWidth), so the head is 7 × 3 = 21 px long, plus the 9 px dot */
    movers.push({ path: p, dot: d, len: p.getTotalLength() - (t.hit ? 6 : 32), phase: beams.indexOf(b) / 3 });
  });
  on.forEach(function (b) {
    var t = b[4], up = t.end[1] < Y0;
    var cands = t.hit
      ? [[10, up ? 26 : -14, 'start'], [10, up ? 44 : -32, 'start'], [-10, up ? 26 : -14, 'end']]
      : [[12, 5, 'start'], [12, -10, 'start'], [12, 20, 'start'], [12, -24, 'start'], [12, 34, 'start']];
    var lab = K.label(g, t.end[0], t.end[1], b[1] + (t.hit ? ' — hits the plate' : ''), { cls: 'bm-lab', avoid: avoid, placed: placed, cands: cands, pad: 3 });
    lab.setAttribute('style', 'fill:' + b[2]);
    /* card-coloured patch under the label: hides only the faint field lines (beams are in avoid) */
    var bb = lab.getBBox(); mask.appendChild(K.svg('rect', { x: bb.x - 3, y: bb.y - 1, width: bb.width + 6, height: bb.height + 2 }));
  });
  $root.querySelector('.bm-foot').textContent = mode === 'schem'
    ? '示意：electron 只画成 proton 的约 2 倍弯曲，真实是约 1836 倍'
    : '真实比例：proton 几乎走直线；electron 弯曲约 1836 倍，一进 field 就急转撞上 positive plate（左下是放大图）';
  place(performance.now());
}
var still = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
function place(now) {
  /* same speed, launched a third of a cycle apart: in real mode the p and n paths almost coincide,
     and two particles leaving together would sit on top of each other */
  movers.forEach(function (m) {
    var u = still ? 0.55 - m.phase * 0.25 : (now / 2600 + m.phase) % 1, L0 = 640 * u;
    var q = m.path.getPointAtLength(Math.min(L0, m.len));
    m.dot.setAttribute('transform', 'translate(' + q.x.toFixed(1) + ',' + q.y.toFixed(1) + ')');
    m.dot.style.opacity = L0 > m.len ? 0 : 1;   /* len is already shortened */
  });
}
(function loop(now) {
  if (!still && document.visibilityState !== 'hidden') place(now);
  requestAnimationFrame(loop);
})(performance.now());
$root.querySelectorAll('input').forEach(function (i) { i.addEventListener('input', draw); });
$root.querySelectorAll('[data-b]').forEach(function (b) {
  b.addEventListener('click', function () {
    mode = b.getAttribute('data-b');
    $root.querySelectorAll('[data-b]').forEach(function (o) { o.classList.toggle('on', o === b); });
    draw();
  });
});
draw();
</script>

<!-- md -->
{{lo 1.1.5}}

### E. Atomic radius 与 ionic radius

**atomic radius**：half the distance between the nuclei of two bonded atoms of the same type（两个相邻、同种、成键 atom 的 nucleus 之间距离的一半）。

决定 radius（以及后面 ionisation energy）的两个 factor，方向相反，比较时要说**哪个占上风**（which effect outweighs the other）：

| factor | 变大时 | 对 outer electrons 的 attraction | radius |
|---|---|---|---|
| **nuclear charge**（number of protons） | ↑ | ↑ | ↓ |
| **shielding**（inner shells of electrons repel the outer electrons） | ↑ | ↓ | ↑ |

| | down a group | across a period（left → right） |
|---|---|---|
| atomic radius | increases | decreases |
| number of shells | 每往下一个 period 多一个 shell | same |
| shielding | increases | similar |
| nuclear charge | increases | increases |
| 谁占上风 | extra shell + increased shielding **outweigh** the increased nuclear charge | nuclear charge（shielding 差不多） |
| attraction on outer electrons | weaker | stronger |

mark scheme 标准句式：

- **across a period**：nuclear charge increases **and** (there is) similar shielding；greater / stronger attraction to the nucleus（9701/21 Oct/Nov 2025 Q2(a)(i)）。
- **down a group**：extra shell (of electrons)，so increased shielding；the additional shell outweighs the increase in nuclear charge，so less attraction for the outer electrons（9701/22 Feb/Mar 2025 Q2(b)(i)；9701/22 May/June 2026 Q2(b)(iii)）。

**ionic radius**：

- **cation 比原 atom 小**：loss of the outer / valence shell (of electrons)，**or** loss of electrons so increase in attraction from the nucleus（9701/22 May/June 2025 Q2(e)：Fe → Fe³⁺ smaller）。
- **anion 比原 atom 大**：得到 electrons 后 electrons 多于 protons，每个 electron 受到的 nuclear attraction 变弱、electron 之间 repulsion 变大，electron cloud 胀大。
- **isoelectronic species**（same number of electrons）只比 nuclear charge：Na⁺ < Ne < F⁻，因为 the larger species has a smaller nuclear charge / fewer protons，so smaller nuclear attraction（9701/23 May/June 2025 Q1(b)(iii)）。Al³⁺ 比 Mg²⁺ 小：same shielding **and** greater nuclear charge，so greater nuclear attraction for the remaining electrons（9701/22 May/June 2024 Q1(b)）。

<!-- html: atomic & ionic radius（data booklet 数据） -->
<div class="grid2">
  <div>{{img image/atomic radius.jpg 260}}</div>
  <div><h3>atomic radius 怎么量</h3>
  <p>图中每个亮点是一个 atom，红线量的是两个相邻 nuclei 之间的距离，它的<b>一半</b>就是 atomic radius。</p>
  <p class="faint">下面的数据取自 data booklet（单位 nm）。metallic radius 和 single covalent radius 可以一起比较；noble gas 只有 van der Waals radius，不放进趋势线。</p></div>
</div>
<div class="row rbtn"></div>
<svg class="rc" viewBox="0 0 720 360" font-family="system-ui, sans-serif"></svg>
<div class="card rtext"></div>
<style>
.k .rc .ax{stroke:var(--line)}
.k .rc .at{fill:none;stroke:var(--s1);stroke-width:2.2}
.k .rc .io{fill:none;stroke:var(--s2);stroke-width:2.2}
.k .rc .jump{fill:none;stroke:var(--s2);stroke-width:1.6;stroke-dasharray:5 5;opacity:.6}
.k .rc circle.at-pt{fill:var(--s1);stroke:var(--card);stroke-width:2}
.k .rc circle.io-pt{fill:var(--s2);stroke:var(--card);stroke-width:2}
.k .rc text{font-size:13px}
.k .rc text.big{font-size:16px}
.k .rc text.mut{fill:var(--mut)}
.k .rc text.ion{font-size:14px}
</style>
<script>
var SETS = {
  'Period 3': {
    at: [['Na', .186, 'metallic'], ['Mg', .160, 'metallic'], ['Al', .143, 'metallic'], ['Si', .117, 'single covalent'], ['P', .110, 'single covalent'], ['S', .104, 'single covalent'], ['Cl', .099, 'single covalent']],
    io: [['Na⁺', .095], ['Mg²⁺', .065], ['Al³⁺', .050], null, ['P³⁻', .212], ['S²⁻', .184], ['Cl⁻', .181]],
    text: '<p><b>atomic radius</b> 逐渐变小：nuclear charge increases <b>and</b> similar shielding → greater attraction to the nucleus。</p>' +
      '<p><b>cations Na⁺ → Al³⁺</b> 比各自的 atom 小很多：失去了整个 3rd shell；三者 isoelectronic（10 electrons），nuclear charge 越大越小。</p>' +
      '<p><b>Al³⁺ → P³⁻ 大跳</b>：Al loses 3 electrons，P gains 3 electrons；Al³⁺ has one fewer shell than P³⁻（9701/21 Oct/Nov 2025 Q2(a)(ii)）。</p>' +
      '<p><b>anions P³⁻ → Cl⁻</b> 又逐渐变小：isoelectronic（18 electrons），nuclear charge 越大越小。Si 不形成 simple ion，真题图里不画。</p>'
  },
  'Period 2': {
    at: [['Li', .152, 'metallic'], ['Be', .112, 'metallic'], ['B', .080, 'single covalent'], ['C', .077, 'single covalent'], ['N', .074, 'single covalent'], ['O', .073, 'single covalent'], ['F', .072, 'single covalent']],
    io: [['Li⁺', .060], ['Be²⁺', .031], ['B³⁺', .020], null, ['N³⁻', .171], ['O²⁻', .140], ['F⁻', .136]],
    text: '<p>和 Period 3 同一个规律，只是整体少一个 shell：atomic radius 逐渐变小；cations 失去 2nd shell 后只剩 1s²；anions 是 isoelectronic 的 10-electron species（N³⁻ > O²⁻ > F⁻）。</p>' +
      '<p class="faint">C 的 ion（C⁴⁺、C⁴⁻）在 data booklet 里有，但 C 不形成 simple ion，这里不画。</p>'
  },
  'Group 2': {
    at: [['Be', .112, 'metallic'], ['Mg', .160, 'metallic'], ['Ca', .197, 'metallic'], ['Sr', .215, 'metallic'], ['Ba', .217, 'metallic']],
    io: [['Be²⁺', .031], ['Mg²⁺', .065], ['Ca²⁺', .099], ['Sr²⁺', .113], ['Ba²⁺', .135]],
    text: '<p>往下 atomic radius 和 ionic radius 都变大：each element has an <b>extra shell</b> of electrons → increased shielding，outweighs the increased nuclear charge（9701/22 Feb/Mar 2025 Q2(b)(i)：ionic radius increases；extra shell）。</p>'
  },
  'Group 17': {
    at: [['F', .072, 'single covalent'], ['Cl', .099, 'single covalent'], ['Br', .114, 'single covalent'], ['I', .133, 'single covalent']],
    io: [['F⁻', .136], ['Cl⁻', .181], ['Br⁻', .195], ['I⁻', .216]],
    text: '<p>往下同样每个 element 多一个 shell，atomic radius 和 ionic radius 都变大。每个 X⁻ 都比 X atom 大：多了一个 electron，repulsion 增大而 nuclear charge 不变。</p>'
  }
};
var svg = $root.querySelector('.rc'), bar = $root.querySelector('.rbtn');
var L = 70, R = 680, T = 30, B = 300, MAX = 0.25;
function y(v) { return B - v / MAX * (B - T); }
function draw(name) {
  var s = SETS[name], n = s.at.length, step = (R - L) / (n - 1 || 1);
  bar.querySelectorAll('button').forEach(function (b) { b.classList.toggle('on', b.textContent === name); });
  svg.innerHTML = '';
  for (var v = 0; v <= MAX + 1e-9; v += 0.05) {
    svg.appendChild(K.svg('line', { x1: L, x2: R, y1: y(v), y2: y(v), 'class': 'ax' }));
    var t = K.svg('text', { x: L - 8, y: y(v) + 4, 'text-anchor': 'end', 'class': 'mut halo' }); t.textContent = v.toFixed(2); svg.appendChild(t);
  }
  var yl = K.svg('text', { x: 18, y: (T + B) / 2, transform: 'rotate(-90 18 ' + (T + B) / 2 + ')', 'text-anchor': 'middle', 'class': 'mut' });
  yl.textContent = 'radius / nm'; svg.appendChild(yl);
  var X = function (i) { return L + i * step; };
  svg.appendChild(K.svg('polyline', { points: s.at.map(function (a, i) { return X(i) + ',' + y(a[1]); }).join(' '), 'class': 'at' }));
  var runs = [], cur = [];
  s.io.forEach(function (o, i) {
    if (!o) { if (cur.length) runs.push(cur); cur = []; return; }
    if (cur.length && /⁺/.test(s.io[cur[cur.length - 1]][0]) !== /⁺/.test(o[0])) { runs.push(cur); cur = []; }
    cur.push(i);
  });
  if (cur.length) runs.push(cur);
  runs.forEach(function (r, k) {
    svg.appendChild(K.svg('polyline', { points: r.map(function (i) { return X(i) + ',' + y(s.io[i][1]); }).join(' '), 'class': 'io' }));
    if (k > 0) { var a = runs[k - 1][runs[k - 1].length - 1], b = r[0];
      svg.appendChild(K.svg('line', { x1: X(a), y1: y(s.io[a][1]), x2: X(b), y2: y(s.io[b][1]), 'class': 'jump' })); }
  });
  var avoid = K.segs(s.at.map(function (a, i) { return [X(i), y(a[1])]; })), placed = [];
  runs.forEach(function (r, k) {
    avoid = avoid.concat(K.segs(r.map(function (i) { return [X(i), y(s.io[i][1])]; })));
    if (k > 0) { var a = runs[k - 1][runs[k - 1].length - 1], b = r[0]; avoid.push([X(a), y(s.io[a][1]), X(b), y(s.io[b][1])]); }
  });
  s.at.forEach(function (a, i) {   /* every point is an obstacle for every label */
    placed.push({ x: X(i) - 7, y: y(a[1]) - 7, w: 14, h: 14 });
    if (s.io[i]) placed.push({ x: X(i) - 7, y: y(s.io[i][1]) - 7, w: 14, h: 14 });
  });
  s.at.forEach(function (a, i) {
    var lab = K.svg('text', { x: X(i), y: B + 22, 'text-anchor': 'middle', 'class': 'big' }); lab.textContent = a[0]; svg.appendChild(lab);
    var c = K.svg('circle', { cx: X(i), cy: y(a[1]), r: 6, 'class': 'at-pt' });
    c.setAttribute('data-tip', '<b>' + a[0] + '</b> atomic radius ' + a[1].toFixed(3) + ' nm（' + a[2] + '）');
    svg.appendChild(c);
    var o = s.io[i];
    if (o) {
      var ci = K.svg('circle', { cx: X(i), cy: y(o[1]), r: 6, 'class': 'io-pt' });
      ci.setAttribute('data-tip', '<b>' + o[0] + '</b> ionic radius ' + o[1].toFixed(3) + ' nm');
      svg.appendChild(ci);
      K.label(svg, X(i), y(o[1]), o[0], { cls: 'mut ion', avoid: avoid, placed: placed });
    }
  });
  var lg = K.svg('g', { transform: 'translate(' + (R - 230) + ',' + (B + 46) + ')' });
  lg.innerHTML = '<circle cx="0" cy="0" r="6" class="at-pt"/><text x="12" y="5">atomic radius</text><circle cx="120" cy="0" r="6" class="io-pt"/><text x="132" y="5">ionic radius</text>';
  svg.appendChild(lg);
  $root.querySelector('.rtext').innerHTML = s.text;
}
svg.setAttribute('viewBox', '0 0 720 360');
Object.keys(SETS).forEach(function (k) {
  var b = K.el('button', {}, k); b.addEventListener('click', function () { draw(k); }); bar.appendChild(b);
});
draw('Period 3');
</script>

<!-- md -->
{{lo 1.1.7}}

## 1.2 Isotopes

**isotopes**：atoms of the same element with the **same number of protons** but **different numbers of neutrons**（9701/21 May/June 2025 Q2(a)；9701/22 Oct/Nov 2025 Q1(a)(ii)）。

等价说法（补充，别用来代替上面那句）：same proton number / atomic number but different nucleon number / mass number。

{{lo 1.2.1}}

isotope 记法 $^{x}_{y}\text{A}$：*x* = mass / nucleon number，*y* = atomic / proton number。例：$^{35}_{17}\text{Cl}$ 和 $^{37}_{17}\text{Cl}$——都是 17 protons，neutrons 分别是 18 和 20。

{{lo 1.2.2}}

| | chemical properties | physical properties（limited to mass and density） |
|---|---|---|
| isotopes 之间 | **same** | **different** |
| 原因 | same number of electrons → same electronic configuration（chemical reactions 只和 electrons 有关） | different number of neutrons → different mass per atom；atom 大小（volume）几乎一样，所以 density 不同 |

延伸（9701/21 May/June 2025 Q2(e)）：⁵⁴Fe 和 ⁵⁶Fe 的 first ionisation energy **一样**——same electronic configuration / same shielding，same number of protons / same nuclear charge，so same nuclear attraction to the outer electron。

{{lo 1.2.3}}

{{lo 1.2.4}}

<!-- html: isotope 对比 -->
<h3>isotope 对比：哪些一样，哪些不一样</h3>
<div class="row ibtn"></div>
<div class="grid2 icards"></div>
<p class="faint">density 一栏按「同样大小的 atom，mass 越大 density 越大」示意，以最轻的 isotope 为 1。</p>
<style>
.k .icards .card h4{margin:0 0 4px;font-size:20px}
.k .icards .meter{height:9px;background:var(--line);border-radius:5px;overflow:hidden;margin:2px 0 6px}
.k .icards .meter i{display:block;height:100%;background:var(--s4)}
.k .icards .same{color:var(--ok);font-weight:600}
.k .icards .diff{color:var(--s4);font-weight:600}
</style>
<script>
var ISO = { hydrogen: ['H', [1, 2, 3]], carbon: ['C', [12, 13, 14]], magnesium: ['Mg', [24, 25, 26]], chlorine: ['Cl', [35, 37]] };
var bar = $root.querySelector('.ibtn'), box = $root.querySelector('.icards');
function show(name) {
  var sym = ISO[name][0], As = ISO[name][1], Z = K.chem.SYM.indexOf(sym) + 1, cfg = K.chem.config(Z, 0);
  bar.querySelectorAll('button').forEach(function (b) { b.classList.toggle('on', b.textContent === name); });
  box.innerHTML = '';
  As.forEach(function (A) {
    var r = A / As[0], c = K.el('div', { 'class': 'card' });
    c.innerHTML = '<h4>' + K.nuc(A, Z, sym) + '　<span class="faint">' + name + '-' + A + '</span></h4>' +
      '<p>protons <b>' + Z + '</b> · electrons <b>' + Z + '</b> · neutrons <b class="diff">' + (A - Z) + '</b></p>' +
      '<p>electronic configuration <span class="same">' + cfg.full + '</span></p>' +
      '<p>chemical properties：<span class="same">same</span></p>' +
      '<p>mass per atom ≈ <span class="diff">' + A + '</span>（相对）</p><div class="meter"><i style="width:' + (100 * A / As[As.length - 1]) + '%"></i></div>' +
      '<p>density ∝ mass（same volume）≈ <span class="diff">' + r.toFixed(2) + ' ×</span></p><div class="meter"><i style="width:' + (100 * A / As[As.length - 1]) + '%"></i></div>';
    box.appendChild(c);
  });
  K.fit();
}
Object.keys(ISO).forEach(function (k) {
  var b = K.el('button', {}, k); b.addEventListener('click', function () { show(k); }); bar.appendChild(b);
});
show('chlorine');
</script>

<!-- md -->
## 1.3 Electrons, energy levels and atomic orbitals

{{lo-note 1.3}}

### A. Shells, sub-shells, orbitals

- **shell**（principal quantum shell / energy level）：用 **principal quantum number *n*** 编号，*n* = 1, 2, 3, 4 …；*n* 越大离 nucleus 越远、energy 越高、被 nucleus 抓得越松。
- **sub-shell**：每个 shell 再分成 s、p、d（f）sub-shells；同一个 shell 里 energy 是 s < p < d。
- **orbital**：a region of space where there is a high probability (95% or more) of finding an electron；**每个 orbital 最多 2 个 electrons**（spin 相反）。
- **ground state**：the lowest energy state（9701/22 Oct/Nov 2024 Q1(a)(i)，也接受 electrons are not promoted to a higher energy level / most energetically stable）。

| sub-shell | number of orbitals | max electrons |
|---|---:|---:|
| s | 1 | 2 |
| p | 3 | 6 |
| d | 5 | 10 |

| shell | sub-shells | max electrons |
|---|---|---:|
| *n* = 1 | 1s | 2 |
| *n* = 2 | 2s 2p | 8 |
| *n* = 3 | 3s 3p 3d | 18 |
| *n* = 4 | 4s 4p 4d 4f | 32 |

{{lo 1.3.1}}

{{lo 1.3.2}}

### B. Shapes of s and p orbitals

- **s orbital**：**spherical**（球形，不是圆）；1s、2s、3s 形状一样，*n* 越大越大、离 nucleus 越远。考试「draw the shape」画**一个圆**，题目要求时标上名字（如 1s）——只写 "spherical" 不画、画坐标轴、画 dot-and-cross 都不给分（9701/21 May/June 2026 Q1(b)(i)；9701/21 Oct/Nov 2024 Q1(a)(ii)；9701/22 May/June 2025 Q2(c)；9701/23 May/June 2025 Q1(a)(iii)）。
- **p orbital**：**dumbbell / hourglass**，两个 lobe；三个 p orbital 分别沿 x、y、z 轴，互相垂直，叫 p<sub>x</sub>、p<sub>y</sub>、p<sub>z</sub>。*n* = 1 没有 p orbital。
- **d orbital**：*n* ≥ 3 才有，5 个；syllabus 只要求知道个数，形状不考。

<!-- html3d: s / p / d orbital 3D -->
<h3>atomic orbital 的形状 <span class="faint">拖动旋转 · 滚轮缩放</span></h3>
<div class="row obtn">
  <button data-o="s">s</button><button data-o="px">p<sub>x</sub></button><button data-o="py">p<sub>y</sub></button><button data-o="pz">p<sub>z</sub></button><button data-o="p3">三个 p 叠加</button>
  <span class="faint">｜</span>
  <button data-o="dxy">d<sub>xy</sub></button><button data-o="dxz">d<sub>xz</sub></button><button data-o="dyz">d<sub>yz</sub></button><button data-o="dx2y2">d<sub>x²−y²</sub></button><button data-o="dz2">d<sub>z²</sub></button><button data-o="d5">五个 d 并排</button>
</div>
<div class="row"><button data-3d="reset">复位视角</button><button data-3d="spin">自动旋转</button></div>
<div class="stage"><div class="hud">两种颜色是 wavefunction 的两个 phase（考试不要求）</div></div>
<p class="ocap"></p>
<div class="fallback card"><p><b>3D 没有加载</b>（<span class="why"></span>），下面是静态示意：</p>
<svg viewBox="0 0 520 200" font-family="system-ui, sans-serif">
  <g transform="translate(110,100)"><line x1="-90" y1="0" x2="90" y2="0" stroke="#999"/><line x1="0" y1="-80" x2="0" y2="80" stroke="#999"/>
  <circle r="55" fill="#7aa2ff" fill-opacity=".55" stroke="#2f5fd0"/><text x="0" y="95" text-anchor="middle">s — spherical</text></g>
  <g transform="translate(360,100)"><line x1="-140" y1="0" x2="140" y2="0" stroke="#999"/><line x1="0" y1="-80" x2="0" y2="80" stroke="#999"/>
  <ellipse cx="-55" cy="0" rx="55" ry="30" fill="#ff8b7b" fill-opacity=".6" stroke="#c0392b"/><ellipse cx="55" cy="0" rx="55" ry="30" fill="#7aa2ff" fill-opacity=".6" stroke="#2f5fd0"/>
  <text x="135" y="-6" text-anchor="end">x</text><text x="0" y="95" text-anchor="middle">p<tspan font-size="10" dy="3">x</tspan><tspan dy="-3"> — dumbbell along the x axis</tspan></text></g>
</svg></div>
<style>
.k .obtn button{min-width:2.6em}
</style>
<script>
var CAP = {
  s: '<b>s orbital</b>：spherical。考试画一个圆（sphere 的截面），题目要名字时标上 1s / 2s …。',
  px: '<b>p<sub>x</sub></b>：dumbbell，两个 lobe 沿 x 轴，nucleus 在两 lobe 之间。',
  py: '<b>p<sub>y</sub></b>：形状和 p<sub>x</sub> 一样，只是沿 y 轴。',
  pz: '<b>p<sub>z</sub></b>：形状和 p<sub>x</sub> 一样，只是沿 z 轴。',
  p3: '<b>三个 p orbital</b> 沿 x、y、z 互相垂直（at right angles），合起来是一个 p sub-shell：3 orbitals，最多 6 electrons。',
  d: '<b>d orbital</b>：*n* ≥ 3 才有，一个 d sub-shell 有 5 个 orbital、最多 10 electrons；大多是四瓣（clover），d<sub>z²</sub> 是两瓣加一圈。形状不考。',
  d5: '<b>五个 d orbital</b>：d<sub>xy</sub>、d<sub>xz</sub>、d<sub>yz</sub>、d<sub>x²−y²</sub>、d<sub>z²</sub>。syllabus 只要求知道是 5 个。'
};
K3.start($root, function (T, api) {
  var axes = K3.axes(T, api, 1.9), holder = new T.Group();
  api.group.add(axes); api.group.add(holder);
  function clear() { while (holder.children.length) { var c = holder.children.pop(); c.geometry && c.geometry.dispose(); } }
  function show(o) {
    clear(); axes.visible = o !== 'd5'; api.dist = o === 'd5' ? 13.5 : 7.4;
    if (o === 'd5') { api.rx = 0.1; api.ry = 0; }
    if (o === 'p3') ['px', 'py', 'pz'].forEach(function (t) { holder.add(K3.orbital(T, api, t, 1.6, 0.8)); });
    else if (o === 'd5') ['dxy', 'dxz', 'dyz', 'dx2y2', 'dz2'].forEach(function (t, i) {
      /* turn each one so the plane it lives in faces the viewer, as textbooks draw them:
         xz / z² → rotate z up onto y; yz → rotate z onto x */
      var m = K3.orbital(T, api, t, 1.1, 1); m.position.x = (i - 2) * 2.7;
      if (t === 'dxz' || t === 'dz2') m.rotation.x = -Math.PI / 2;
      if (t === 'dyz') m.rotation.y = Math.PI / 2;
      holder.add(m);
      var lb = K3.label(T, { dxy: 'd xy', dxz: 'd xz', dyz: 'd yz', dx2y2: 'd x²−y²', dz2: 'd z²' }[t], api.color('--fg').getStyle(), 0.62);
      lb.position.set((i - 2) * 2.7, -1.75, 0); holder.add(lb);
    });
    else holder.add(K3.orbital(T, api, o, o === 's' ? 1.1 : 1.6, 1));
    $root.querySelectorAll('[data-o]').forEach(function (b) { b.classList.toggle('on', b.getAttribute('data-o') === o); });
    $root.querySelector('.ocap').innerHTML = (CAP[o] || CAP.d).replace('*n*', '<i>n</i>');
    api.view(); K.fit();
  }
  $root.querySelectorAll('[data-o]').forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-o')); }); });
  show('px');
});
</script>

<!-- html3d: 1s / 2s / 3s：size 与 radial node -->
<h3>1s、2s、3s：越来越大，中间有 node <span class="faint">拖动旋转 · 滚轮缩放</span></h3>
<div class="row"><button data-c="1s">1s</button><button data-c="2s">2s</button><button data-c="3s">3s</button>
<button data-3d="reset">复位视角</button><button data-3d="spin">自动旋转</button><label style="margin-left:8px"><input type="checkbox" class="ccut"> 切掉前半个看里面</label><label style="margin-left:8px"><input type="checkbox" class="csame"> 三个用同一比例</label></div>
<div class="stage"><div class="hud">3D 点图：点的密度 ∝ ψ²（electron density）· 灰色半透明球壳 = radial node（点稀到没有的那层球面；旋转、滚轮放大或切开来看）· 两种颜色 = ψ 的正负 · <b class="csize"></b></div></div>
<p class="ccap"></p>
<div class="fallback card"><p><b>3D 没有加载</b>（<span class="why"></span>），下面是静态示意（同一比例）：</p>
<svg viewBox="0 0 560 220" font-family="system-ui, sans-serif">
  <g transform="translate(70,110)"><circle r="20" fill="#7aa2ff" fill-opacity=".6"/><text y="100" text-anchor="middle">1s</text></g>
  <g transform="translate(210,110)"><circle r="55" fill="#ff8b7b" fill-opacity=".35"/><circle r="11" fill="#fff" stroke="#888" stroke-dasharray="3 3"/><circle r="8" fill="#7aa2ff" fill-opacity=".7"/><text y="100" text-anchor="middle">2s（1 个 node）</text></g>
  <g transform="translate(420,110)"><circle r="95" fill="#7aa2ff" fill-opacity=".2"/><circle r="38" fill="#fff" stroke="#888" stroke-dasharray="3 3"/><circle r="30" fill="#7aa2ff" fill-opacity=".35"/><circle r="10" fill="#fff" stroke="#888" stroke-dasharray="3 3"/><circle r="7" fill="#7aa2ff" fill-opacity=".7"/><text y="112" text-anchor="middle">3s（2 个 node）</text></g>
</svg></div>
<script>
var CC = {
  '1s': '<b>1s</b>：最小、最靠近 nucleus，electron density 在 nucleus 附近最高、向外逐渐变稀。',
  '2s': '<b>2s</b>：形状同样是 spherical，但大得多；里面有一层球壳形的 <b>node</b>（灰色半透明球壳；这一层球面上几乎没有点，electron density 为零，颜色也在这里翻转），外层那一圈才是 2s electron 最常出现的地方——greatest chance of finding the electron is further from the nucleus。',
  '3s': '<b>3s</b>：更大，有 2 个 node。所以 3s、4s … 依次离 nucleus 越来越远，energy 越来越高。'
};
var SCALE = 0.074, NODES = { '1s': [], '2s': [2], '3s': [1.902, 7.098] }, NPTS = { '1s': 9000, '2s': 22000, '3s': 32000 }, cur = '2s';
K3.start($root, function (T, api) {
  var holder = new T.Group(), cache = {}, same = $root.querySelector('.csame'), cut = $root.querySelector('.ccut');
  api.group.add(holder); api.rx = 0.4; api.ry = -0.35;
  var nuc = new T.Mesh(new T.SphereGeometry(0.03, 12, 8), new T.MeshBasicMaterial({ color: api.color('--fg'), depthTest: false, transparent: true }));
  nuc.renderOrder = 11; holder.add(nuc);
  var layer = new T.Group(); holder.add(layer);
  /* camera distance that makes a sphere of world radius R (the outermost dots) fill ~80 % of the
     canvas height (vertical FOV 40°; the HUD covers the top strip) */
  function fit(R) { return R / Math.sin(0.8 * 20 * Math.PI / 180); }
  function show(k) {
    cur = k;
    var key = k + (cut.checked ? '-cut' : '');
    while (layer.children.length) layer.remove(layer.children[0]);
    if (!cache[key]) cache[key] = K3.dots(T, api, k, NPTS[k], SCALE, NODES[k], cut.checked);
    var obj = cache[key]; layer.add(obj);
    var R3 = K3.rBound('3s', 0.995, 80) * SCALE, r = obj.userData.rBound, Rw = obj.userData.rMax * SCALE;
    /* same scale: the camera is set for 3s and the scene is shifted down a little, clear of the HUD */
    api.dist = fit(same.checked ? R3 : Rw); holder.position.y = -0.04 * api.dist;
    api.dist0 = api.dist;
    /* dot and nucleus sizes follow the zoom, so they look the same on screen at any scale */
    nuc.scale.setScalar(api.dist / 6); obj.userData.mat.size = 0.006 * api.dist;
    obj.userData.labels.forEach(function (l) { var h = 0.05 * api.dist; l.scale.set(h * l.scale.x / l.scale.y, h, 1); });
    $root.querySelector('.csize').textContent = k + ' 的 90% 半径 ≈ ' + r.toFixed(1) + ' a₀ ≈ ' + Math.round(r * 52.9) + ' pm' + (same.checked ? '（同一比例）' : '（自动缩放）');
    $root.querySelectorAll('[data-c]').forEach(function (b) { b.classList.toggle('on', b.getAttribute('data-c') === k); });
    $root.querySelector('.ccap').innerHTML = CC[k];
    api.view(); K.fit();
  }
  $root.querySelectorAll('[data-c]').forEach(function (b) { b.addEventListener('click', function () { show(b.getAttribute('data-c')); }); });
  same.addEventListener('change', function () { show(cur); });
  /* looked at face-on a half ball is just a disc: turn it to an oblique view when the cut is switched on */
  cut.addEventListener('change', function () {
    if (cut.checked) { api.rx = 0.45; api.ry = -1.15; } else { api.rx = api.rx0 = 0.4; api.ry = api.ry0 = -0.35; }
    api.rx0 = api.rx; api.ry0 = api.ry; show(cur);
  });
  show('2s');
});
</script>

<!-- md -->
{{lo 1.3.8}}

### C. 填 electron 的顺序：energy 与 inter-electron repulsion

sub-shell 的 energy 由低到高（*n* = 1–3 加上 4s、4p）：

**1s < 2s < 2p < 3s < 3p < 4s < 3d < 4p**

注意 **4s 比 3d 低**，所以 4s 先填；但**写 configuration 时按 *n* 排，3d 写在 4s 前面**（`[Ar]3d⁶4s²`）。

三条规则：

1. **Aufbau principle**：electrons enter the lowest available energy level first —— 先填 energy 最低的 orbital。
2. **Pauli exclusion principle**：一个 orbital 最多 2 个 electrons，而且 **spin 相反**（↑↓），以减小 repulsion。
3. **Hund's rule**：同一 sub-shell 里 energy 相同的 orbitals，electrons **先各占一个、spin 平行**，全部单占之后才配对——因为同一 orbital 里的两个 electrons 之间有 **spin-pair repulsion**，分开放 repulsion 更小、更 stable。

一句话（对应 LO 1.3.5）：electrons go into the **lowest energy** orbitals available，and occupy **separate orbitals** of the same energy before pairing，**to minimise inter-electron (spin-pair) repulsion**。

{{lo 1.3.3}}

{{lo 1.3.5}}

### D. Electronic configuration 与 electrons in boxes

- **full**：`1s²2s²2p⁶3s²3p⁶3d⁶4s²`　**shorthand**：`[Ar]3d⁶4s²`（[Ar] = `1s²2s²2p⁶3s²3p⁶`，9701/21 Oct/Nov 2024 Q1(a)(i)）。
- **两个例外要背**：Cr = `[Ar]3d⁵4s¹`（不是 3d⁴4s²），Cu = `[Ar]3d¹⁰4s¹`（不是 3d⁹4s²）。
- **positive ions**：先失去 *n* 最大的 electrons —— d-block 的 **4s electrons are lost first**，再失 3d：Fe²⁺ = `[Ar]3d⁶`，Fe³⁺ = `[Ar]3d⁵`，Cu⁺ = `[Ar]3d¹⁰`。
- **negative ions**：按 Aufbau 继续加：S²⁻ = `1s²2s²2p⁶3s²3p⁶`。
- **electrons in boxes**：每个方框是一个 orbital，箭头是 electron（方向 = spin）。d / p sub-shell 里的单个 electron 可以画在任意一个框里（9701/22 Oct/Nov 2024 Q1(a)(ii) 判分：the 3 d electrons may go in any of the d orbitals）。

常考的「数一数」：

| 问法 | 例 | 答案 |
|---|---|---|
| number of unpaired electrons | Co `[Ar]3d⁷4s²` | 3（9701/21 Oct/Nov 2024 Q1(a)(iii)） |
| | Cr `[Ar]3d⁵4s¹` | 6（9701/21 Oct/Nov 2025 Q1(b)(ii)） |
| | Mn `[Ar]3d⁵4s²` | 5（9701/22 Oct/Nov 2025 Q1(b)(ii)） |
| pairs of electrons in a shell / sub-shell | O，*n* = 2：2s² 2p⁴ | 2 pairs（9701/23 May/June 2025 Q1(a)(ii)） |
| | Fe，*n* = 3：3s² 3p⁶ 3d⁶ | 5 pairs（9701/21 May/June 2025 Q2(c)） |
| | Fe²⁺ 的 3d：3d⁶ | 1 pair（9701/22 May/June 2025 Q2(b)） |
| electrons in p sub-shells | V `1s²2s²2p⁶3s²3p⁶3d³4s²` | 12（9701/22 Oct/Nov 2024 Q1(a)(iii)） |

{{lo 1.3.4}}

{{lo 1.3.6}}

{{lo 1.3.7}}

<!-- html: electronic configuration 填充器（H–Kr，含 ion） -->
<h3>electronic configuration 填充器</h3>
<div class="row">element <select class="fz"></select> charge <select class="fq"></select>
<button class="fstep">逐个填入 ▶</button><button class="fall">直接填满</button></div>
<div class="grid2">
  <svg class="fl" viewBox="0 0 560 390" font-family="system-ui, sans-serif"></svg>
  <div class="card fout"></div>
</div>
<h4>自测：写出 electronic configuration（full 或 shorthand 都行，空格随意，写 1s2 或 1s² 都可以）</h4>
<div class="k-ptable"></div>
<table class="fquiz"><tr><th>species</th><th>你的答案</th><th>判定</th></tr></table>
<style>
.k .fl rect.box{fill:var(--card);stroke:var(--mut);stroke-width:1.3}
.k .fl rect.box.last{stroke:var(--acc);stroke-width:2.6}
.k .fl text.lab{font-size:15px;font-weight:600}
.k .fl text.arr{font-size:19px;font-weight:700}
.k .fl text.gone{fill:var(--bad);opacity:.45}
.k .fl text.mut{fill:var(--mut);font-size:13px}
.k .fl line.ax{stroke:var(--mut);stroke-width:1.5}
.k .fout .cfg{font-size:19px;font-family:"Cascadia Mono","DejaVu Sans Mono","Noto Sans Mono","SF Mono",Consolas,ui-monospace,monospace;word-break:break-all}
.k .fout .note{border-left:3px solid var(--s4);padding:2px 8px;margin:6px 0;color:var(--mut);font-size:14px}
.k .fquiz input{width:20em}
.k .fquiz .res{font-weight:700}
</style>
<script>
var C = K.chem, S = C.SYM, zs = $root.querySelector('.fz'), qs = $root.querySelector('.fq'), svg = $root.querySelector('.fl');
for (var i = 1; i <= 36; i++) zs.appendChild(K.el('option', { value: i }, i + '  ' + S[i - 1]));
[-3, -2, -1, 0, 1, 2, 3].forEach(function (q) { qs.appendChild(K.el('option', { value: q }, q === 0 ? '0' : (q > 0 ? q + '+' : -q + '−'))); });
zs.value = 26; qs.value = 0;
var POS = { '1s': [70, 350], '2s': [70, 290], '2p': [190, 262], '3s': [70, 205], '3p': [190, 178], '4s': [70, 128], '3d': [330, 104], '4p': [190, 62] };
var W = 32, H = 28, shown = null;
function chg(q) { return q === 0 ? '' : K.sup((Math.abs(q) === 1 ? '' : Math.abs(q)) + (q > 0 ? '+' : '-')); }
function partial(Z, n) {  /* Aufbau order, first n electrons, no exceptions */
  var occ = {}, left = n;
  C.ORDER.forEach(function (o) { var t = Math.min(o[1], left); occ[o[0]] = t; left -= t; });
  return occ;
}
function draw() {
  var Z = +zs.value, q = +qs.value, cfg = C.config(Z, q), out = $root.querySelector('.fout');
  if (!cfg || Z - q > 36 || Z - q < 0) {
    svg.innerHTML = ''; out.innerHTML = '<p>这个 species 超出了 H–Kr 的范围（electrons 必须在 0–36 之间）。</p>'; return;
  }
  var atom = C.config(Z, 0), occ = cfg.occ, last = null, stepping = shown !== null && q === 0;
  if (stepping) { occ = shown >= Z ? atom.occ : partial(Z, shown); }
  if (stepping && shown > 0 && shown < Z) {
    var acc = 0; C.ORDER.some(function (o) { acc += o[1]; if (acc >= shown) { last = o[0]; return true; } });
  }
  svg.innerHTML = '';
  svg.appendChild(K.svg('line', { x1: 22, y1: 380, x2: 22, y2: 24, 'class': 'ax', 'marker-end': '' }));
  svg.appendChild(K.svg('path', { d: 'M16,32 L22,18 L28,32 z', style: 'fill:var(--mut)' }));
  var et = K.svg('text', { x: 14, y: 210, transform: 'rotate(-90 14 210)', 'text-anchor': 'middle', 'class': 'mut' }); et.textContent = 'energy'; svg.appendChild(et);
  C.ORDER.forEach(function (o) {
    var name = o[0], cap = o[1], p = POS[name], orbs = cap / 2;
    var arrows = C.boxes(occ[name] || 0, cap), gone = C.boxes(atom.occ[name] || 0, cap);
    var lab = K.svg('text', { x: p[0] - 8, y: p[1] + 19, 'text-anchor': 'end', 'class': 'lab' }); lab.textContent = name; svg.appendChild(lab);
    for (var j = 0; j < orbs; j++) {
      var x = p[0] + j * W;
      var r = K.svg('rect', { x: x, y: p[1], width: W, height: H, 'class': 'box' + (name === last ? ' last' : '') });
      r.setAttribute('data-tip', name + ' orbital ' + (j + 1) + ' / ' + orbs);
      svg.appendChild(r);
      var have = arrows[j], had = stepping ? have : Math.max(have, q > 0 ? gone[j] : have);
      for (var a = 0; a < had; a++) {
        var t = K.svg('text', { x: x + (had === 1 ? W / 2 : a === 0 ? W / 2 - 6 : W / 2 + 6), y: p[1] + 21, 'text-anchor': 'middle', 'class': 'arr' + (a >= have ? ' gone' : '') });
        t.textContent = a === 0 ? '↑' : '↓';
        svg.appendChild(t);
      }
    }
  });
  if (q > 0 && !stepping) {
    var gt = K.svg('text', { x: 300, y: 380, 'class': 'mut' }); gt.textContent = '淡红色箭头 = 形成 ion 时失去的 electrons'; svg.appendChild(gt);
  }
  var cur = stepping && shown < Z ? null : cfg;
  var name = S[Z - 1] + chg(q), shells = cur ? Object.keys(cur.shells).map(function (n) { return 'n=' + n + ': ' + cur.shells[n]; }).join(' · ') : '';
  var html = '<p><b style="font-size:20px">' + name + '</b>　Z = ' + Z + '，electrons = ' + (Z - q) + '</p>';
  if (stepping && shown < Z) {
    html += '<p>已填 <b>' + shown + '</b> / ' + Z + ' 个 electron' + (last ? '，刚填进 <b>' + last + '</b>' : '') + '</p>' +
      '<p class="faint">顺序：1s → 2s → 2p → 3s → 3p → 4s → 3d → 4p；同一 sub-shell 先单占（Hund），再配对（Pauli）。</p>';
  } else if (cur.total === 0) {
    html += '<p>没有 electron 了（只剩 nucleus）。</p>';
  } else {
    html += '<p class="faint">full</p><div class="cfg">' + cur.full + '</div><p class="faint">shorthand</p><div class="cfg">' + cur.short + '</div>' +
      '<p>electrons per shell：' + shells + '</p><p>unpaired electrons：<b>' + cur.unpaired + '</b></p>';
    if (Z === 24 || Z === 29) html += '<div class="note">' + S[Z - 1] + ' 是例外：' + (Z === 24 ? '[Ar]3d⁵4s¹，不是 3d⁴4s²' : '[Ar]3d¹⁰4s¹，不是 3d⁹4s²') + '。要背。</div>';
    if (q > 0 && Z >= 21 && Z <= 30) html += '<div class="note">d-block 形成 positive ion 时 <b>4s electrons are lost first</b>，然后才失 3d。</div>';
    if (q > 0 && !(Z >= 21 && Z <= 30)) html += '<div class="note">positive ion：从最外层（<i>n</i> 最大）的 sub-shell 拿走 electrons。</div>';
    if (q < 0) html += '<div class="note">negative ion：得到的 electrons 按 Aufbau 顺序继续填。</div>';
    if (Z >= 19 && cur.occ['3d'] > 0 && cur.occ['4s'] > 0) html += '<div class="note">写的时候 3d 写在 4s 前面（按 <i>n</i> 排），虽然 4s 先填。</div>';
    if (cur.unpaired > 0 && q === 0 && Z === 17) html += '<div class="note">一个单独的 Cl atom 有 1 个 unpaired electron，所以是 <b>free radical</b>，写作 Cl•。</div>';
  }
  out.innerHTML = html;
  K.fit();
}
zs.addEventListener('input', function () { shown = null; draw(); });
qs.addEventListener('input', function () { shown = null; draw(); });
$root.querySelector('.fstep').addEventListener('click', function () {
  qs.value = 0;
  var Z = +zs.value;
  shown = shown === null || shown >= Z ? 1 : shown + 1;
  draw();
});
$root.querySelector('.fall').addEventListener('click', function () { shown = null; draw(); });
draw();
var QZ = [['Fe', 0], ['Fe', 3], ['Cl', 0], ['Al', 3], ['Cu', 1], ['O', -2], ['Cr', 0], ['Ca', 0], ['V', 0], ['S', -2]];
var tb = $root.querySelector('.fquiz');
QZ.forEach(function (r) {
  var Z = S.indexOf(r[0]) + 1, want = C.config(Z, r[1]), tr = K.el('tr');
  tr.innerHTML = '<td>' + r[0] + chg(r[1]) + (r[0] === 'Cl' && r[1] === 0 ? '•（free radical）' : '') + '</td><td><input type="text" spellcheck="false"></td><td class="res"></td>';
  var inp = tr.querySelector('input'), res = tr.querySelector('.res');
  inp.addEventListener('input', function () {
    var got = C.parse(inp.value);
    if (!inp.value.trim()) { res.textContent = ''; return; }
    if (!got) { res.textContent = '看不懂'; res.style.color = 'var(--faint)'; return; }
    var right = C.same(got, want.occ), ok = right && C.ordered(got);
    res.textContent = ok ? '✓' : right ? '✗ 顺序' : '✗'; res.style.color = ok ? 'var(--ok)' : 'var(--bad)';
    res.setAttribute('data-tip', ok ? want.full : right
      ? 'electrons 对了，顺序不对：按 n 写，3d 写在 4s 前面（syllabus：' + want.short + '）'
      : '再想想：electrons = ' + want.total);
  });
  tb.appendChild(tr);
});
</script>

<!-- md -->
### E. Free radicals

**free radical**：a species with one or more **unpaired electrons**。unpaired electron 用一个点表示：

- 单独的 Cl atom：`1s²2s²2p⁶3s²3p⁵`，3p 里有一个 unpaired electron → Cl•
- methyl radical CH₃•：carbon 上有一个 unpaired electron

（free radical 在 ch14 的 free-radical substitution 里会再用到。）

{{lo 1.3.9}}

<!-- md -->
## 1.4 Ionisation energy

{{lo-note 1.4}}

### A. 定义与方程式

**first ionisation energy**（*IE*₁）：the energy needed to remove **one mole of electrons** from **one mole of gaseous atoms** to form **one mole of gaseous 1+ ions**。

- 方程式**必须写 (g)**，每一步只拿走 **一个** electron：
  - first：Ca(g) → Ca⁺(g) + e⁻　*IE*₁ = 590 kJ mol⁻¹
  - second：Ca⁺(g) → Ca²⁺(g) + e⁻　*IE*₂ = 1150 kJ mol⁻¹
  - third：Ca²⁺(g) → Ca³⁺(g) + e⁻　*IE*₃ = 4940 kJ mol⁻¹
- mark scheme 也接受 S(g) − e⁻ → S⁺(g) 的写法（9701/23 May/June 2025 Q1(b)(i)）；写成 Cl(g) + e⁻ → Cl⁺(g) + 2e⁻ 不给分（9701/21 May/June 2026 Q1(b)(ii)）。
- **successive ionisation energies**：一个接一个地拿走 electrons，每一步的 energy。

{{lo 1.4.1}}

{{lo 1.4.2}}

### B. 影响 ionisation energy 的 factors

ionisation energy 的本质是 **the attraction between the nucleus and the outer electron**：attraction 越强，IE 越大。

| factor | 怎么影响 |
|---|---|
| **nuclear charge** | protons 越多 → attraction 越强 → IE ↑ |
| **atomic / ionic radius**（distance of outer electron） | outer electron 离 nucleus 越远 → attraction 越弱 → IE ↓ |
| **shielding** by inner shells and sub-shells | inner electrons 越多 → 挡掉的 attraction 越多 → IE ↓ |
| **spin-pair repulsion** | 要拿走的 electron 在已经有 2 个 electrons 的 orbital 里 → 被另一个 electron 排斥 → 更容易拿走 → IE ↓ |

{{lo 1.4.5}}

{{lo 1.4.6}}

### C. Trends in first ionisation energy

下图把 H–Kr 的 *IE*₁ 画出来；点上面的按钮看每一个 trend 的解释。

<!-- html: first ionisation energy H–Kr -->
<h3>first ionisation energy，H → Kr</h3>
<div class="row ibtn"></div>
<svg class="ie" viewBox="0 0 760 390" font-family="system-ui, sans-serif"></svg>
<div class="card itext"></div>
<p class="faint">数据：data booklet；Ge、As、Se、Kr 不在 data booklet 里，取自 NIST（图上空心点）。鼠标移到点上看数值和 configuration。</p>
<style>
.k .ie .ax{stroke:var(--line)}
.k .ie .band{fill:var(--acc-soft);opacity:.55}
.k .ie polyline{fill:none;stroke:var(--faint);stroke-width:1.6}
.k .ie circle{fill:var(--s1);stroke:var(--card);stroke-width:1.5}
.k .ie circle.ext{fill:var(--card);stroke:var(--s1);stroke-width:1.8}
.k .ie circle.hl{fill:var(--s2);r:7}
.k .ie circle.dim{opacity:.35}
.k .ie text{font-size:12px}
.k .ie text.mut{fill:var(--mut)}
.k .ie text.sym{font-size:11px;fill:var(--mut)}
.k .ie text.hl{fill:var(--s2);font-weight:700;font-size:13px}
.k .ie line.arrow{stroke:var(--s2);stroke-width:2}
</style>
<script>
var IE1 = [1310, 2370, 519, 900, 799, 1090, 1400, 1310, 1680, 2080, 494, 736, 577, 786, 1060, 1000, 1260, 1520,
           418, 590, 632, 661, 648, 653, 716, 762, 757, 736, 745, 908, 577, 762, 947, 941, 1140, 1350];
var EXT = { 32: 1, 33: 1, 34: 1, 36: 1 };
var STORIES = [
  ['across a period', [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], [],
   '<p><b>整体上升</b>：nuclear charge increases；electrons 从同一个 shell 拿走，distance 差不多；shielding by inner shells 差不多 → attraction 变强 → IE increases。</p>' +
   '<p>mark scheme（9701/21 May/June 2026 Q1(b)(iii)，S → Cl）两条路线任选：①（small）increase in shielding is outweighed by increased nuclear charge，Cl has greater nuclear attraction；② similar shielding，Cl has greater nuclear charge，Cl has greater nuclear attraction。<b>至少点名 chlorine 一次</b>才给满分。</p>'],
  ['Be → B，Mg → Al', [4, 5, 12, 13], [[4, 5], [12, 13]],
   '<p><b>小幅下降</b>：B / Al 要拿走的 electron 在 <b>2p / 3p</b>，2p 比 2s energy 高、离 nucleus 稍远，而且多了 2s / 3s electrons 的 shielding → 这两点 outweigh 增加的 nuclear charge → attraction 变弱 → IE 下降。</p><p class="faint">Be 1s²2s² → B 1s²2s²2p¹；Mg [Ne]3s² → Al [Ne]3s²3p¹</p>'],
  ['N → O，P → S', [7, 8, 15, 16], [[7, 8], [15, 16]],
   '<p><b>小幅下降</b>：O / S 要拿走的 electron 所在的 2p / 3p orbital 里已经有另一个 electron（paired）→ <b>spin-pair repulsion</b> → 更容易拿走。</p>' +
   '<p>得分句（9701/23 May/June 2025 Q1(b)(ii)，S < P）：M1 pair of electrons in a 3p orbital (in S) repel each other；M2 outweighs the effect of increase in nuclear charge。</p><p class="faint">N 2p: ↑ ↑ ↑ → O 2p: ↑↓ ↑ ↑</p>'],
  ['noble gas → Group 1', [2, 3, 10, 11, 18, 19], [[2, 3], [10, 11], [18, 19]],
   '<p><b>大幅下降</b>：Group 1 的 outer electron 进入了<b>新的 shell</b> → distance 变大、shielding by inner shells 增加 → outweigh 增加的 nuclear charge → attraction 弱很多。</p>'],
  ['down a group', [2, 10, 18, 36, 3, 11, 19], [[3, 11], [11, 19], [2, 10], [10, 18], [18, 36]],
   '<p><b>往下降低</b>：more shells / larger atomic radius；increased shielding；less attraction for the outer electron / lower energy required（9701/22 Feb/Mar 2026 Q1(a)(ii)，Mg → Ba 的 IE₁ + IE₂）。</p>'],
  ['Sc → Cu 几乎不变', [21, 22, 23, 24, 25, 26, 27, 28, 29], [],
   '<p>d-block：拿走的 electron 一直来自 4s；每多一个 proton 同时也多一个 3d electron（inner sub-shell，shielding 增加），两者大致抵消，所以 IE₁ 变化很小。<span class="faint">（讲义内容，syllabus 只要求 H–Kr 的一般 trend。）</span></p>']
];
var svg = $root.querySelector('.ie'), L = 60, R = 740, T = 34, B = 330, MAX = 2500;
function X(z) { return L + (z - 1) * (R - L) / 35; }
function Y(v) { return B - v / MAX * (B - T); }
function draw(si) {
  var st = STORIES[si];
  $root.querySelectorAll('.ibtn button').forEach(function (b, k) { b.classList.toggle('on', k === si); });
  svg.innerHTML = '';
  [[1, 2], [3, 10], [11, 18], [19, 36]].forEach(function (p, k) {
    if (k % 2) svg.appendChild(K.svg('rect', { x: X(p[0]) - 9, y: T, width: X(p[1]) - X(p[0]) + 18, height: B - T, 'class': 'band' }));
    var t = K.svg('text', { x: (X(p[0]) + X(p[1])) / 2, y: T - 10, 'text-anchor': 'middle', 'class': 'mut' }); t.textContent = 'Period ' + (k + 1); svg.appendChild(t);
  });
  for (var v = 0; v <= MAX; v += 500) {
    svg.appendChild(K.svg('line', { x1: L, x2: R, y1: Y(v), y2: Y(v), 'class': 'ax' }));
    var t = K.svg('text', { x: L - 6, y: Y(v) + 4, 'text-anchor': 'end', 'class': 'mut halo' }); t.textContent = v; svg.appendChild(t);
  }
  var yl = K.svg('text', { x: 14, y: 175, transform: 'rotate(-90 14 175)', 'text-anchor': 'middle', 'class': 'mut' });
  yl.textContent = 'first ionisation energy / kJ mol⁻¹'; svg.appendChild(yl);
  svg.appendChild(K.svg('polyline', { points: IE1.map(function (v, i) { return X(i + 1) + ',' + Y(v); }).join(' ') }));
  st[2].forEach(function (pr) {
    svg.appendChild(K.svg('line', { x1: X(pr[0]), y1: Y(IE1[pr[0] - 1]), x2: X(pr[1]), y2: Y(IE1[pr[1] - 1]), 'class': 'arrow' }));
  });
  IE1.forEach(function (v, i) {
    var z = i + 1, on = st[1].indexOf(z) >= 0, cfg = K.chem.config(z, 0);
    var c = K.svg('circle', { cx: X(z), cy: Y(v), r: 5, 'class': (EXT[z] ? 'ext ' : '') + (on ? 'hl' : 'dim') });
    c.setAttribute('data-tip', '<b>' + K.chem.SYM[i] + '</b>（Z = ' + z + '）　IE₁ = ' + v + ' kJ mol⁻¹' + (EXT[z] ? '（NIST）' : '') + '<br>' + cfg.short);
    svg.appendChild(c);
    var s = K.svg('text', { x: X(z), y: B + 16 + (i % 2) * 12, 'text-anchor': 'middle', 'class': on ? 'hl' : 'sym' }); s.textContent = K.chem.SYM[i]; svg.appendChild(s);
  });
  var xl = K.svg('text', { x: (L + R) / 2, y: 384, 'text-anchor': 'middle', 'class': 'mut' }); xl.textContent = 'proton number'; svg.appendChild(xl);
  $root.querySelector('.itext').innerHTML = st[3];
  K.fit();
}
var bar = $root.querySelector('.ibtn');
STORIES.forEach(function (s, k) { var b = K.el('button', {}, s[0]); b.addEventListener('click', function () { draw(k); }); bar.appendChild(b); });
draw(0);
</script>

<!-- md -->
{{lo 1.4.3}}

### D. Successive ionisation energies

- **总趋势：一个比一个大**。每拿走一个 electron，剩下的 ion 带的 positive charge 更多：less shielding / successive ionic radii are smaller / greater attraction (of the electron) to the nucleus（9701/22 Feb/Mar 2025 Q2(b)(ii)）。
- **大跳跃**：下一个 electron 来自 **an inner shell / lower energy level**——离 nucleus 更近、shielding 少得多（9701/22 Feb/Mar 2025 Q2(b)(ii)；9701/22 Feb/Mar 2026 Q1(a)(iv)：Mg 的 *IE*₃ 远大于 *IE*₁ + *IE*₂，因为 electron removed from a closer / inner (2p) shell，much less shielding / greater nuclear attraction）。
- **用法**：第一次大跳跃前面有几个 electrons，就是 outer shell 有几个 electrons → 推出 **group**；数一数有几次大跳跃（几个 shell），推出 **period** 和 electronic configuration。

<!-- html: successive ionisation energies -->
<h3>successive ionisation energies</h3>
<div class="card"><b>方程式生成器</b>　element <select class="sz"></select>　第 <select class="sn"></select> ionisation energy
<div class="seq" style="font-size:19px;margin-top:6px"></div></div>
<div class="tabbar" style="margin-top:10px"><button data-tab="na">Na：全部 11 个</button><button data-tab="si">Si：全部 14 个</button><button data-tab="quiz">从 IE₁–IE₄ 推 group</button></div>
<div data-pane="na"><div class="row"><label><input type="checkbox" class="lg" checked> log scale</label></div><svg class="sv-na" viewBox="0 0 720 340" font-family="system-ui, sans-serif"></svg>
<p>Na：1 个 electron 在 <i>n</i> = 3 → 大跳 → 8 个在 <i>n</i> = 2 → 大跳 → 2 个在 <i>n</i> = 1，所以是 2,8,1 → <b>Group 1，Period 3</b>，[Ne]3s¹。</p></div>
<div data-pane="si"><div class="row"><label><input type="checkbox" class="lg" checked> log scale</label></div><svg class="sv-si" viewBox="0 0 720 340" font-family="system-ui, sans-serif"></svg>
<p>Si：4 个在 <i>n</i> = 3 → 大跳（IE₄ → IE₅）→ 8 个在 <i>n</i> = 2 → 大跳 → 2 个在 <i>n</i> = 1 → <b>Group 14</b>，[Ne]3s²3p²。9701/21 Oct/Nov 2024 Q3(c)(i) 就是让你补画 IE₃–IE₆：IE₃、IE₄ 和 IE₁、IE₂ 同一低水平略升，IE₅ 起大跳。</p></div>
<div data-pane="quiz"><p>数据取自 data booklet（只有前 4 个 IE）。看最大的那一次跳跃在哪里。</p>
<svg class="sv-q" viewBox="0 0 720 260" font-family="system-ui, sans-serif"></svg>
<div class="mcqbox"></div><button class="qnext">下一题 ▶</button></div>
<p class="faint">Na、Si 的全部 IE 不在 data booklet 里，取自 NIST；IE₁–IE₄ 与 data booklet 一致（个位数有舍入差）。</p>
<style>
.k .sv-na rect,.k .sv-si rect,.k .sv-q rect{stroke:var(--card);stroke-width:1}
.k .s3{fill:var(--s1)} .k .s2{fill:var(--s3)} .k .s1{fill:var(--s4)}
.k svg text.mut{fill:var(--mut);font-size:12px}
.k svg text.v{font-size:11px;fill:var(--mut)}
.k svg text.j{fill:var(--s2);font-size:13px;font-weight:700}
.k .ax2{stroke:var(--line)}
</style>
<script>
var DB = { H: [1310], He: [2370, 5250], Li: [519, 7300, 11800], Be: [900, 1760, 14800, 21000], B: [799, 2420, 3660, 25000], C: [1090, 2350, 4610, 6220],
  N: [1400, 2860, 4590, 7480], O: [1310, 3390, 5320, 7450], F: [1680, 3370, 6040, 8410], Ne: [2080, 3950, 6150, 9290], Na: [494, 4560, 6940, 9540],
  Mg: [736, 1450, 7740, 10500], Al: [577, 1820, 2740, 11600], Si: [786, 1580, 3230, 4360], P: [1060, 1900, 2920, 4960], S: [1000, 2260, 3390, 4540],
  Cl: [1260, 2300, 3850, 5150], Ar: [1520, 2660, 3950, 5770], K: [418, 3070, 4600, 5860], Ca: [590, 1150, 4940, 6480], Sc: [632, 1240, 2390, 7110],
  Ti: [661, 1310, 2720, 4170], V: [648, 1370, 2870, 4600], Cr: [653, 1590, 2990, 4770], Mn: [716, 1510, 3250, 5190], Fe: [762, 1560, 2960, 5400],
  Co: [757, 1640, 3230, 5100], Ni: [736, 1750, 3390, 5400], Cu: [745, 1960, 3350, 5690], Zn: [908, 1730, 3828, 5980], Ga: [577, 1980, 2960, 6190],
  Br: [1140, 2080, 3460, 4850], Sr: [548, 1060, 4120, 5440], Ba: [502, 966, 3390] };
var FULL = { na: [496, 4562, 6910, 9543, 13354, 16613, 20117, 25496, 28932, 141362, 159076],
             si: [786, 1577, 3232, 4356, 16091, 19805, 23780, 29287, 33878, 38726, 45962, 50502, 235196, 257923] };
var S = K.chem.SYM, zs = $root.querySelector('.sz'), ns = $root.querySelector('.sn');
for (var i = 1; i <= 36; i++) zs.appendChild(K.el('option', { value: i }, i + '  ' + S[i - 1]));
zs.value = 20;
function ion(sym, c) { return sym + (c === 0 ? '' : K.sup((c === 1 ? '' : c) + '+')); }
function ord(n) { return n + (n === 1 ? 'st' : n === 2 ? 'nd' : n === 3 ? 'rd' : 'th'); }
function eq() {
  var Z = +zs.value, sym = S[Z - 1], keep = +ns.value || 1;
  ns.innerHTML = '';
  for (var n = 1; n <= Math.min(Z, 4); n++) ns.appendChild(K.el('option', { value: n }, ord(n)));
  ns.value = Math.min(keep, Math.min(Z, 4));
  var n = +ns.value, val = DB[sym] && DB[sym][n - 1];
  $root.querySelector('.seq').innerHTML = ion(sym, n - 1) + '(g) → ' + ion(sym, n) + '(g) + e⁻' +
    (val ? '　<span class="faint">' + ord(n) + ' IE = ' + val + ' kJ mol⁻¹</span>' : '　<span class="faint">（data booklet 没有这个值）</span>');
}
zs.addEventListener('input', eq); ns.addEventListener('input', eq); eq();

function shellsRemoved(Z) {  /* shell number of each electron in removal order: outermost first */
  var c = K.chem.config(Z, 0), list = [];
  c.used.slice().sort(function (a, b) { return b.n - a.n || 'spd'.indexOf(b.l) - 'spd'.indexOf(a.l); })
    .forEach(function (s) { for (var k = 0; k < s.e; k++) list.push(s.n); });
  return list;
}
function bars(svg, vals, shells, log, opts) {
  opts = opts || {};
  var W = 720, H = +svg.getAttribute('viewBox').split(' ')[3], L = 66, R = W - 12, T = 16, B = H - 40;
  var tk = K.ticks(Math.max.apply(null, vals) * 1.05, 4);
  var lo = log ? 2 : 0, hi = log ? 6 : tk[tk.length - 1];
  function Y(v) { return B - ((log ? Math.log10(v) : v) - lo) / (hi - lo) * (B - T); }
  svg.innerHTML = '';
  var ticks = log ? [100, 1000, 10000, 100000, 1000000] : tk;
  ticks.forEach(function (t) {
    svg.appendChild(K.svg('line', { x1: L, x2: R, y1: Y(Math.max(t, log ? 100 : 0)), y2: Y(Math.max(t, log ? 100 : 0)), 'class': 'ax2' }));
    var tx = K.svg('text', { x: L - 6, y: Y(Math.max(t, log ? 100 : 0)) + 4, 'text-anchor': 'end', 'class': 'mut' }); tx.textContent = t.toLocaleString('en'); svg.appendChild(tx);
  });
  var yl = K.svg('text', { x: 12, y: (T + B) / 2, transform: 'rotate(-90 12 ' + (T + B) / 2 + ')', 'text-anchor': 'middle', 'class': 'mut' });
  yl.textContent = (log ? 'log scale · ' : '') + 'IE / kJ mol⁻¹'; svg.appendChild(yl);
  var bw = (R - L) / vals.length;
  vals.forEach(function (v, k) {
    var x = L + k * bw + bw * 0.15, y = Y(v);
    var r = K.svg('rect', { x: x, y: y, width: bw * 0.7, height: B - y, 'class': shells ? 's' + shells[k] : 's3' });
    r.setAttribute('data-tip', ord(k + 1) + ' IE = ' + v.toLocaleString('en') + ' kJ mol⁻¹' + (shells ? '<br>electron from n = ' + shells[k] : ''));
    svg.appendChild(r);
    var tx = K.svg('text', { x: x + bw * 0.35, y: B + 16, 'text-anchor': 'middle', 'class': 'mut' }); tx.textContent = k + 1; svg.appendChild(tx);
    if (opts.values) { var vt = K.svg('text', { x: x + bw * 0.35, y: y - 4, 'text-anchor': 'middle', 'class': 'v' }); vt.textContent = v; svg.appendChild(vt); }
    if (k > 0 && v / vals[k - 1] >= 3 && !opts.noJump) {
      var jt = K.svg('text', { x: x - bw * 0.15, y: y - (opts.values ? 18 : 6), 'text-anchor': 'middle', 'class': 'j' }); jt.textContent = '× ' + (v / vals[k - 1]).toFixed(1); svg.appendChild(jt);
    }
  });
  var xl = K.svg('text', { x: (L + R) / 2, y: H - 6, 'text-anchor': 'middle', 'class': 'mut' }); xl.textContent = 'number of electrons removed'; svg.appendChild(xl);
  if (shells) {
    var lg = K.svg('g', { transform: 'translate(' + (L + 10) + ',' + (T + 6) + ')' });
    lg.innerHTML = '<rect width="12" height="12" class="s3"/><text x="16" y="11" class="mut">n = 3</text><rect x="70" width="12" height="12" class="s2"/><text x="86" y="11" class="mut">n = 2</text><rect x="140" width="12" height="12" class="s1"/><text x="156" y="11" class="mut">n = 1</text>';
    svg.appendChild(lg);
  }
  K.fit();
}
function drawFull() {
  bars($root.querySelector('.sv-na'), FULL.na, shellsRemoved(11), $root.querySelector('[data-pane=na] .lg').checked);
  bars($root.querySelector('.sv-si'), FULL.si, shellsRemoved(14), $root.querySelector('[data-pane=si] .lg').checked);
}
$root.querySelectorAll('.lg').forEach(function (c) { c.addEventListener('input', drawFull); });
drawFull();

var POOL = ['Na', 'K', 'Be', 'Mg', 'Ca', 'Sr', 'B', 'Al', 'C', 'Si', 'N'], qi = -1;   /* only elements with all four IEs in the data booklet */
function groupOf(v) {
  var best = 0, at = -1;
  for (var k = 1; k < v.length; k++) if (v[k] / v[k - 1] > best) { best = v[k] / v[k - 1]; at = k; }
  return best >= 3 ? ({ 1: '1', 2: '2', 3: '13' })[at] : '14+';
}
function quiz() {
  qi = (qi + 1 + Math.floor(Math.random() * (POOL.length - 1))) % POOL.length;
  var sym = POOL[qi], v = DB[sym], g = groupOf(v);
  bars($root.querySelector('.sv-q'), v, null, false, { values: true, noJump: true });
  var box = $root.querySelector('.mcqbox');
  box.innerHTML = '<div class="mcq" data-ans="' + g + '"><p>element <b>X</b> 的 IE₁–IE₄ 如上。X 在哪个 group？</p>' +
    '<button data-v="1">Group 1</button> <button data-v="2">Group 2</button> <button data-v="13">Group 13</button> <button data-v="14+">Group 14 或以后（前 4 个里没有大跳）</button>' +
    '<div class="ans why"></div></div>';
  var why = box.querySelector('.why'), n = { '1': 1, '2': 2, '13': 3 }[g], SUB = '₀₁₂₃₄₅';
  why.textContent = g === '14+'
    ? '相邻两个 IE 的比值都小于 3：前 4 个 electrons 都来自同一个 outer shell，outer shell 至少有 4 个 electrons → Group 14 或以后。（X = ' + sym + '）'
    : '最大的跳跃在 IE' + SUB[n] + ' → IE' + SUB[n + 1] + '（× ' + (v[n] / v[n - 1]).toFixed(1) + '）：前 ' + n + ' 个 electrons 在 outer shell，下一个来自 inner shell → Group ' + g + '。（X = ' + sym + '）';
  K.init($root);
  K.fit();
}
$root.querySelector('.qnext').addEventListener('click', quiz);
quiz();
</script>

<!-- md -->
{{lo 1.4.4}}

{{lo 1.4.7}}

{{lo 1.4.8}}

<!-- md -->
## Practice

2024–2026 Paper 2 里所有考 chapter 1 的小问，按考试时间排列。考 *A*ᵣ / relative isotopic mass 的小问属于 chapter 2 / 22，不放在这里。表格里的空格可以直接填（填对变绿），再展开 **答案** 对照 mark scheme。

<!-- practice: 9701/22 May/June 2024 -->
### 9701/22 May/June 2024

#### Q1(a) [2]
Complete Table 1.1 using relevant information from the Periodic Table.

| | nucleon number | proton number | number of electrons |
|---|---|---|---|
| Mg²⁺ | 24 | [[12]] | [[10]] |
| Al³⁺ | 27 | [[13]] | [[10]] |

::: answer
Mg²⁺：12 protons，10 electrons；Al³⁺：13 protons，10 electrons。

判分：4 个空全对 2 分；对 2 或 3 个 1 分；对 0 或 1 个 0 分。
:::

#### Q1(b) [3]
State and explain the difference in the ionic radius of Al³⁺ compared to Mg²⁺.

::: answer
- M1 it / Al³⁺ is smaller (compared to Mg²⁺)
- M2 greater nuclear attraction for remaining electrons
- M3 same shielding effect **AND** greater nuclear charge
:::

<!-- practice: 9701/21 Oct/Nov 2024 -->
### 9701/21 Oct/Nov 2024

Cobalt, rhodium and iridium are metals in the same group of the Periodic Table. The shorthand electronic configuration of cobalt is [Ar]3d⁷4s².

#### Q1(a)(i) [1]
Identify what is meant by [Ar] by giving its full electronic configuration.

::: answer
1s² 2s² 2p⁶ 3s² 3p⁶
:::

#### Q1(a)(ii) [1]
The lowest-energy electrons in cobalt are in the 1s orbital. Draw the shape of a 1s orbital.

::: answer
画一个圆（spherical 1s orbital）。
:::

#### Q1(a)(iii) [1]
Deduce the number of unpaired electrons in a cobalt atom.

::: answer
3（3d⁷：5 个 3d orbital 里 2 对 + 3 个单的）
:::

#### Q1(b) [3]
Table 1.1 gives some details of the stable naturally occurring isotopes of rhodium and iridium. Complete Table 1.1.

| isotope | number of protons | number of neutrons | total number of electron shells |
|---|---|---|---|
| $^{103}_{45}\text{Rh}$ | [[45]] | 58 | [[5]] |
| $^{191}_{77}\text{Ir}$ | [[77]] | [[114]] | 6 |
| $^{193}_{77}\text{Ir}$ | [[77]] | [[116]] | 6 |

::: answer
Rh：45 protons，5 shells；Ir-191：77 protons，114 neutrons；Ir-193：77 protons，116 neutrons。
:::

#### Q3(c)(i) [2]
Figure 3.1 shows a sketch of some of the ionisation energies of silicon, Si. Complete the graph in Figure 3.1 to show the third to sixth ionisation energies of Si.

{{img passyear/extracted/ch01-atomic-structure/img/9701_w24_21_fig3-1.png 460}}

::: answer
Si = [Ne]3s²3p²：IE₁–IE₄ 拿走的是 outer shell 的 4 个 electrons，所以 IE₃、IE₄ 和 IE₁、IE₂ 在同一个低水平、略微上升；IE₅ 开始拿 *n* = 2 的 electrons，**大跳**到接近已画出的 IE₇ 的水平，与 IE₇–IE₁₄ 连成递增的曲线。

- M1 general increase
- M2 the jump from IE₄ to IE₅ is clearly the largest jump between consecutive plotted IEs
:::

#### Q3(c)(ii) [1]
Construct an equation to represent the second ionisation energy of Si.

::: answer
Si⁺(g) → Si²⁺(g) + e⁻
:::

<!-- practice: 9701/22 Oct/Nov 2024 -->
### 9701/22 Oct/Nov 2024

Vanadium, niobium and tantalum are metals in the same group of the Periodic Table. The shorthand electronic configuration of vanadium in the ground state is [Ar]3d³4s².

#### Q1(a)(i) [1]
State what is meant by the term ground state.

::: answer
lowest energy state（owtte：with lowest energy / with no external (added) energy / electrons are not promoted to a higher energy level / most energetically stable）
:::

#### Q1(a)(ii) [1]
Show the electronic configuration of vanadium using electrons in boxes notation.

::: answer
[Ar] 后面 6 个方框：3d 的 5 个框里 3 个各一个 ↑（另外 2 个空），4s 的框里一对 ↑↓。

判分：the 3 d electrons may go in any of the d orbitals。可以在上面的「electronic configuration 填充器」里选 V 对照。
:::

#### Q1(a)(iii) [1]
Deduce the total number of electrons in the p sub-shells of a vanadium atom.

::: answer
12（2p⁶ + 3p⁶）
:::

#### Q1(b)(i) [2]
Only one naturally occurring isotope exists for each of Nb and Ta. Complete Table 1.1.

| isotope | relative isotopic mass | number of protons | number of neutrons |
|---|---|---|---|
| $^{93}_{41}\text{Nb}$ | 92.91 | [[41]] | [[52]] |
| $^{181}_{73}\text{Ta}$ | 180.95 | [[73]] | [[108]] |

::: answer
Nb-93：41 protons，52 neutrons；Ta-181：73 protons，108 neutrons。
:::

<!-- practice: 9701/22 Feb/Mar 2025 -->
### 9701/22 Feb/Mar 2025

#### Q2(b)(i) [2]
The Group 2 elements form stable 2+ cations. State and explain the variation in ionic radius of the Group 2 elements down the group.

::: answer
ionic radius increases / ions larger (down the group)；extra shell (of electrons)
:::

#### Q2(b)(ii) [2]
Table 2.1 shows successive ionisation energy values for beryllium, Be.

| | 1st | 2nd | 3rd | 4th |
|---|---|---|---|---|
| ionisation energy / kJ mol⁻¹ | 900 | 1760 | 14 800 | 21 000 |

Use Table 2.1 to state and explain the general trend in these values, and the significance of the large difference between the 2nd and 3rd ionisation energies.

::: answer
- ionisation energies increase，because less shielding / successive ionic radii are smaller / greater attraction (of electron) to nucleus
- large difference between 2nd and 3rd IE：the 3rd electron comes from an inner shell / lower energy level
:::

#### Q2(c)(i) [2]
Beryllium exists as the single isotope $^{9}_{4}\text{Be}$. Describe the distribution of mass within an atom of $^{9}_{4}\text{Be}$.

::: answer
most of the mass is in the nucleus；because protons and neutrons / nucleons are found in the nucleus
:::

#### Q2(c)(ii) [2]
Complete Table 2.2 to show the numbers of protons and neutrons in the isotopes of magnesium.

| isotope | number of protons | number of neutrons |
|---|---|---|
| magnesium-24 | [[12]] | [[12]] |
| magnesium-25 | [[12]] | [[13]] |
| magnesium-26 | [[12]] | [[14]] |

::: answer
都是 12 protons；neutrons 12、13、14。
:::

#### Q2(c)(iii) [3]
Fig. 2.1 shows the behaviour of a beam of protons in an electric field. Complete Fig. 2.1 to show the behaviour of separate beams of neutrons and electrons in the same electric field. Label your diagram clearly. Assume that the beams of each particle are moving at the same velocity.

{{img passyear/extracted/ch01-atomic-structure/img/9701_m25_22_fig2-1.png 460}}

::: answer
- neutron beam：从同一个 source 出发的水平**直线**
- electron beam：从同一个 source 出发、往与 proton **相反**的方向弯，而且**弯得比 proton 大得多**
- 两条都要标清楚（可以用上面的「beams」交互图对照）
:::

<!-- practice: 9701/21 May/June 2025 -->
### 9701/21 May/June 2025

A sample of iron is analysed using a mass spectrometer. The mass spectrum shows three isotopes of iron are present in the sample.

#### Q2(a) [1]
Define isotopes.

::: answer
atoms (of an element) with same number of protons and different number of neutrons
:::

#### Q2(b)(ii) [2]
Complete Table 2.1 to show the number of protons and nucleons in one atom of ⁵⁶Fe.

| particle | number of particles in one atom of ⁵⁶Fe |
|---|---|
| protons | [[26]] |
| nucleons | [[56]] |

::: answer
protons = 26；nucleons = 56
:::

#### Q2(c) [1]
Deduce the number of pairs of electrons in the shell with principal quantum number *n* = 3 in an Fe atom.

::: answer
5（3s² 是 1 对、3p⁶ 是 3 对、3d⁶ 里有 1 对）
:::

#### Q2(d) [1]
Write an equation to represent the first ionisation energy of iron.

::: answer
Fe(g) → Fe⁺(g) + e⁻
:::

#### Q2(e) [4]
Suggest how the value for the first ionisation energy of ⁵⁴Fe compares to the first ionisation energy of ⁵⁶Fe. Explain your answer in terms of the factors that affect ionisation energy.

::: answer
- M1 same electronic configuration **OR** same shielding
- M2 same number of protons **OR** same nuclear charge
- M3 so same nuclear attraction to outer shell electron
- M4 no change / will not be affected
:::

<!-- practice: 9701/22 May/June 2025 -->
### 9701/22 May/June 2025

A sample of iron contains three different isotopes.

#### Q2(b) [1]
Deduce the number of pairs of electrons in the 3d sub-shell in an iron(II) ion.

::: answer
1 (pair)（Fe²⁺ = [Ar]3d⁶：先失 4s²）
:::

#### Q2(c) [1]
Sketch the shape of the lowest energy orbital in the shell with principal quantum number *n* = 2.

::: answer
画一个圆（2s orbital，spherical，与 1s 同形状）
:::

#### Q2(d) [2]
Complete Table 2.2 to show information about particles in one ion of ⁵⁶Fe³⁺.

| particle | number of particles present in one ion of ⁵⁶Fe³⁺ |
|---|---|
| electrons | [[23]] |
| [[neutrons\|neutron]] | 30 |

::: answer
electrons = 23；30 那一行的粒子是 **neutrons**。
:::

#### Q2(e) [2]
The atomic radius of iron is 1.26 × 10⁻¹⁰ m. Suggest the change to the radius, if any, after an iron atom reacts to produce an Fe³⁺ ion. Explain your answer.

::: answer
- M1 smaller / decreases
- M2 loss of outer / valence shell (of electrons) **OR** loss of electrons so increase in (force of) attraction from nucleus **OR** loss of electrons so increase nuclear attraction
:::

<!-- practice: 9701/23 May/June 2025 -->
### 9701/23 May/June 2025

The chemical properties of an element are related to the electronic configuration of its atoms.

#### Q1(a)(i) [1]
Give the full electronic configuration of a fluorine atom.

::: answer
1s² 2s² 2p⁵
:::

#### Q1(a)(ii) [1]
Deduce the number of pairs of electrons in the second energy shell, *n* = 2, of an oxygen atom.

::: answer
2 (pairs)（2s² 一对；2p⁴ = ↑↓ ↑ ↑ 一对）
:::

#### Q1(a)(iii) [1]
Draw the shape of the highest energy orbital that contains electrons in an atom of calcium.

::: answer
画一个圆（Ca = [Ar]4s²，4s orbital 是 spherical）
:::

#### Q1(b)(i) [1]
Write an equation to represent the first ionisation energy of sulfur.

::: answer
S(g) → S⁺(g) + e⁻ **OR** S(g) − e⁻ → S⁺(g)
:::

#### Q1(b)(ii) [2]
Explain why the first ionisation energy of sulfur is less than the first ionisation energy of phosphorus.

::: answer
- M1 pair of electrons in a 3p orbital (in S) repel each other
- M2 outweighs the effect of increase in nuclear charge
:::

#### Q1(b)(iii) [4]
Arrange the three species F⁻, Ne and Na⁺ in order of increasing radius. Explain your answer.

::: answer
- M1 Na⁺ < Ne < F⁻
- M2 (all have) same number of electrons / isoelectronic
- M3 larger species has smaller nuclear charge / fewer protons
- M4 (so) smaller nuclear attraction (to outer electrons)
:::

<!-- practice: 9701/21 Oct/Nov 2025 -->
### 9701/21 Oct/Nov 2025

Chromium, Cr, and its compounds are widely used in many chemical reactions. Cr exists as four stable isotopes.

#### Q1(a)(i) [1]
The most common isotope of Cr is chromium-52. Determine the number of protons, neutrons and electrons in an atom of chromium-52.

protons [[24]]　neutrons [[28]]　electrons [[24]]

::: answer
protons = 24；neutrons = 28；electrons = 24
:::

#### Q1(a)(ii) [1]
Describe how an atom of chromium-54 differs from an atom of chromium-52. Refer to numbers of particles in your answer.

::: answer
(⁵⁴Cr has two) more neutrons (than ⁵²Cr)
:::

#### Q1(b)(i) [1]
The shorthand electronic configuration of chromium is [Ar] 3d⁵4s¹. Complete the full electronic configuration of chromium.

::: answer
1s² 2s² 2p⁶ 3s² 3p⁶ (3d⁵ 4s¹)
:::

#### Q1(b)(ii) [1]
Deduce the total number of unpaired electrons in an atom of chromium.

::: answer
6（3d⁵ 五个单的 + 4s¹ 一个）
:::

#### Q2(a)(i) [2]
Fig. 2.1 shows the variation in atomic and ionic radii of the Period 3 elements Na to Cl. The ionic radius of Si is not shown. Explain the trend shown in the atomic radii of the Period 3 elements Na to Cl.

{{img passyear/extracted/ch09-periodicity/img/9701_w25_21_fig2-1.png 460}}

::: answer
- M1 nuclear charge increases (across the period) **AND** (there is) similar shielding
- M2 greater / stronger attraction to (the) nucleus
:::

#### Q2(a)(ii) [2]
Explain why there is a large difference in the ionic radii of Al and P.

::: answer
- M1 Al loses (3) electrons / Al is 3+，and P gains (3) electrons / P is 3−
- M2 Al³⁺ has (one) fewer shell (than P³⁻)
:::

<!-- practice: 9701/22 Oct/Nov 2025 -->
### 9701/22 Oct/Nov 2025

Manganese, Mn, and its compounds are widely used in many chemical reactions. Mn is usually found as a single isotope, manganese-55.

#### Q1(a)(i) [1]
Determine the number of protons, neutrons and electrons in an atom of manganese-55.

protons [[25]]　neutrons [[30]]　electrons [[25]]

::: answer
protons = 25；neutrons = 30；electrons = 25
:::

#### Q1(a)(ii) [1]
Define isotopes.

::: answer
(atoms of an element) with the same number of protons and different number of neutrons
:::

#### Q1(b)(i) [1]
The shorthand electronic configuration of manganese is [Ar] 3d⁵ 4s². Complete the full electronic configuration of manganese.

::: answer
1s² 2s² 2p⁶ 3s² 3p⁶ (3d⁵ 4s²)
:::

#### Q1(b)(ii) [1]
Deduce the total number of unpaired electrons in an atom of manganese.

::: answer
5
:::

<!-- practice: 9701/22 Feb/Mar 2026 -->
### 9701/22 Feb/Mar 2026

Table 1.1 shows some information about the elements Mg to Ba.

| element | proton number | shorthand electronic configuration | sum of first and second ionisation energies / kJ mol⁻¹ | third ionisation energy / kJ mol⁻¹ |
|---|---|---|---|---|
| Mg | 12 | [Ne] 3s² | 2186 | 7740 |
| Ca | 20 | [Ar] 4s² | 1740 | 4940 |
| Sr | 38 | [Kr] 5s² | 1608 | 4120 |
| Ba | 56 | [Xe] 6s² | 1468 | 3390 |

#### Q1(a)(i) [1]
Give the full electronic configuration of a calcium atom.

::: answer
1s² 2s² 2p⁶ 3s² 3p⁶ 4s²
:::

#### Q1(a)(ii) [2]
Explain the trend shown in the sum of the first and second ionisation energies, as proton number increases.

::: answer
(ionisation energy decreases because of) more shells / larger (atomic / ionic) radius；increased shielding；less attraction (for the nucleus / protons) / lower energy required (to remove electrons)
:::

#### Q1(a)(iii) [1]
Write an equation to represent the third ionisation energy of barium.

::: answer
Ba²⁺(g) → Ba³⁺(g) + e⁻
:::

#### Q1(a)(iv) [2]
Explain why the third ionisation energy of magnesium is much greater than the sum of its first and second ionisation energies.

::: answer
- M1 electron removed from closer / inner / lower-energy (p sub)shell / orbital
- M2 (much) less shielding **OR** greater nuclear attraction
:::

<!-- practice: 9701/21 May/June 2026 -->
### 9701/21 May/June 2026

Table 1.1 shows information about sulfur and chlorine.

| element | electronic configuration | first ionisation energy / kJ mol⁻¹ |
|---|---|---|
| sulfur | [Ne] 3s² 3p⁴ | 1000 |
| chlorine | [Ne] 3s² 3p⁵ | 1260 |

#### Q1(b)(i) [1]
Name the orbital that contains the lowest energy electron in an atom of sulfur. Draw the shape of this orbital.

::: answer
画一个圆 **AND** 标 **1s**。

判分：只写 "spherical" 而不画、画坐标轴、只写 1sⁿ 的 n、画 dot-and-cross 都不给分。
:::

#### Q1(b)(ii) [1]
Construct an equation to represent the first ionisation energy of chlorine.

::: answer
Cl(g) → Cl⁺(g) + e⁻

判分：A Cl(g) − e⁻ → Cl⁺(g)；I Cl(g) + e⁻ → Cl⁺(g) + 2e⁻
:::

#### Q1(b)(iii) [3]
Explain the difference in the values of first ionisation energy of sulfur and chlorine in Table 1.1.

::: answer
两条路线任选其一：

- M1 (small) increase in shielding in Cl is outweighed by；M2 increased nuclear charge in Cl；M3 Cl has greater nuclear attraction (ora)
- M1 similar shielding；M2 Cl has greater nuclear charge；M3 Cl has greater nuclear attraction (ora)

判分：三分全给的前提是 **chlorine 在答案里至少点名一次**；M2 接受 number of protons / greater atomic number；"effective" nuclear charge 里的 effective 忽略；若 M2、M3 都没拿到但把 greater nuclear attraction 和 greater nuclear charge 联系起来了，给 max 1。
:::

<!-- practice: 9701/22 May/June 2026 -->
### 9701/22 May/June 2026

#### Q2(a)(i) [1]
Protons, neutrons and electrons are released with the same velocity from a source. Figure 2.1 shows the movement of two of these types of particle when they travel between oppositely charged plates. Name each type of particle that produces the deflection shown by curves x and y.

{{img passyear/extracted/ch01-atomic-structure/img/9701_s26_22_fig2-1.png 420}}

::: answer
curve x = electron **AND** curve y = proton
:::

#### Q2(a)(ii) [1]
Suggest why the particles producing curve y are deflected less than the particles producing curve x.

::: answer
particles in y are deflected less because they have larger mass。

判分：A heavier / higher mass-to-charge ratio / greater momentum / (particles in) x are lighter；I "electrons have negligible mass"（没有比较）、lower charge density、kinetic energy；R protons have greater charge density。
:::

A student considers the information in Table 2.1 and proposes hypothesis 1: *'Atoms with a higher nuclear charge are always larger.'*

| atom | atomic number | mass number | atomic radius / nm |
|---|---|---|---|
| A | 6 | 12 | 0.077 |
| B | 17 | 37 | 0.099 |
| C | 14 | 28 | 0.117 |

#### Q2(b)(i) [1]
Identify a pair of atoms from Table 2.1 that supports hypothesis 1.

::: answer
(atom) A and (atom) B **OR** (atom) A and (atom) C
:::

#### Q2(b)(ii) [1]
Identify a pair of atoms from Table 2.1 that shows hypothesis 1 is false.

::: answer
(atom) B and (atom) C
:::

#### Q2(b)(iii) [2]
Explain why atom A is smaller than atom C.

::: answer
- M1 atom A has (one) fewer (electron) shell(s)（so decreased shielding effect）
- M2 (so) more attraction of nucleus for outer / valence electrons **OR** in atom C the effect of more protons / increased nuclear charge is less significant than / outweighed by the (increased shielding) effect of the additional shell

判分：以 C 为主语反过来论述也接受；提 subshells / orbitals 忽略；若写出具体 shell 数，必须正确（A = 2、C = 3）。
:::

<!-- md -->
{{lo-checklist}}
