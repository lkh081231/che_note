/* Periodic Table data in colab/kit/kit.js vs reference.md (syllabus p.91), cell by cell.

   usage: node colab/tests/kit_ptable_data.js
   Checks: 118 elements, Z / symbol / Aᵣ identical to the reference.md table ('–' = none), and that
   each element sits in the reference's period / group column (57–71 and 89–103 in the f rows). */
const fs = require('fs'), path = require('path'), vm = require('vm');
const root = path.resolve(__dirname, '..', '..');
const win = {};
vm.runInNewContext(fs.readFileSync(path.join(root, 'colab/kit/kit.js'), 'utf8'), { window: win, document: {} });
const PT = win.K.chem.PT;

const ref = fs.readFileSync(path.join(root, 'reference.md'), 'utf8').split('## The Periodic Table of Elements')[1];
const want = {};
/* main table: | **p** | cell | cell | … — cell index = group */
ref.split(/\r?\n/).forEach(ln => {
  const m = ln.match(/^\| \*\*(\d)\*\* \|(.*)\|$/);
  if (m) m[2].split('|').forEach((c, i) => {
    const e = c.trim().match(/^([A-Z][a-z]?)<br>(\d+)<br>([\d.]+|–)$/);
    if (e) want[+e[2]] = { sym: e[1], ar: e[3] === '–' ? null : e[3], p: +m[1], g: i + 1 };
  });
});
/* lanthanoid / actinoid rows */
[['Lanthanoids', 6], ['Actinoids', 7]].forEach(([name, p]) => {
  const blk = ref.split(`**${name}`)[1].split(/\r?\n/).find(l => l.startsWith('| '));
  blk.slice(1, -1).split('|').forEach((c, i) => {
    const e = c.trim().match(/^([A-Z][a-z]?)<br>(\d+)<br>([\d.]+|–)$/);
    if (e) want[+e[2]] = { sym: e[1], ar: e[3] === '–' ? null : e[3], p, f: i };
  });
});

let bad = 0;
const fail = s => { bad++; console.log('  FAIL ' + s); };
if (Object.keys(want).length !== 118) fail(`reference.md parsed ${Object.keys(want).length} elements, not 118`);
if (PT.length !== 118) fail(`kit.js has ${PT.length} elements, not 118`);
PT.forEach(e => {
  const w = want[e.z];
  if (!w) return fail(`Z ${e.z} not in reference.md`);
  if (w.sym !== e.sym) fail(`Z ${e.z}: symbol ${e.sym} ≠ ${w.sym}`);
  if (w.ar !== e.ar) fail(`Z ${e.z} ${e.sym}: Ar ${e.ar} ≠ ${w.ar}`);
  if (w.p !== e.p) fail(`Z ${e.z} ${e.sym}: period ${e.p} ≠ ${w.p}`);
  if (w.f != null ? e.f !== w.f : (e.f != null || e.g !== w.g)) fail(`Z ${e.z} ${e.sym}: position g${e.g}/f${e.f} ≠ g${w.g}/f${w.f}`);
});
const n = PT.filter(e => want[e.z] && want[e.z].sym === e.sym && want[e.z].ar === e.ar).length;
console.log(`${n}/118 elements match reference.md (Z / symbol / Ar)` + (bad ? `, ${bad} problem(s)` : ', positions match too'));
process.exit(bad ? 1 : 0);
