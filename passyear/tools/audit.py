# -*- coding: utf-8 -*-
"""按小问标签统计每道题的「章 → 分值」分布，挑出主章被标空 / 标少的题。

背景：主章由 chapters.py 定死，mirror.py 不会改它。标注 pass 有可能把主章标空
——实测 ch21 Organic synthesis 的 4 道题第一遍全被拆进 ch13/14/15/16/18/19/22，
ch21 自己一分没有，原因是 agent 漏了 21.1.3「analyse a given synthetic route」。
这类题不自动改，列出来人工拍板。

注意 mirror.weights()：小问标 `· ch14 ch15` 时**两章各记满分**，所以 weights 之和
可以大于题目总分。查覆盖率要按「每个小问只数一次」，见 covered()。
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, "tools")
import mirror, chapters

def covered(blk):
    """打过标签的小问分值合计（多章标签只数一次）。"""
    return sum(marks for _, marks, _ in mirror.subq_tags(blk))

owner, also, canon, session = mirror.load_state()

rows = []
for (key, qn), blk in sorted(canon.items()):
    w = mirror.weights(blk)
    if not w:
        continue
    own = owner[(key, qn)]
    total = mirror.marks_of(key, qn) or covered(blk)
    rows.append((key, qn, total, own, w, covered(blk)))

print(f"已标注 {len(rows)} 题 / 共 {len(canon)} 题\n")

print("=== 🔴 主章被标空的题（0 分，肯定是漏标）===")
n = 0
for key, qn, total, own, w, cov in rows:
    if w.get(own, 0) == 0:
        n += 1
        dist = " ".join(f"ch{c}:{m}" for c, m in sorted(w.items(), key=lambda kv: -kv[1]))
        print(f"  {key} Q{qn} [{total}]  主章 ch{own} 占 0 分 → {dist}")
print("  无" if not n else "")

print("=== 🟡 主章不是最大块的题（需人工拍板换主章）===")
n = 0
for key, qn, total, own, w, cov in rows:
    ownm = w.get(own, 0)
    top = max(w.items(), key=lambda kv: kv[1])
    if 0 < ownm < top[1]:
        n += 1
        dist = " ".join(f"ch{c}:{m}" for c, m in sorted(w.items(), key=lambda kv: -kv[1]))
        print(f"  {key} Q{qn} [{total}]  主章 ch{own} 占 {ownm}，最大块 ch{top[0]}:{top[1]}")
        print(f"      {dist}")
print("  无" if not n else "")

print("=== 🟡 有小问没打标签的题（覆盖率不足）===")
n = 0
for key, qn, total, own, w, cov in rows:
    if cov != total:
        n += 1
        print(f"  {key} Q{qn}：已标 {cov} 分 / 题目 [{total}]  差 {total - cov} 分")
print("  无" if not n else "")

print("=== 完全没标注的题 ===")
un = [(k, q) for (k, q), b in sorted(canon.items()) if not mirror.weights(b)]
print(("  %d 题：" % len(un)) + ", ".join(f"{k} Q{q}" for k, q in un) if un else "  无")

print("\n=== 各章按标签得到的总分（含非主章，多章小问重复计入）===")
agg = {}
for key, qn, total, own, w, cov in rows:
    for c, m in w.items():
        agg[c] = agg.get(c, 0) + m
for c in sorted(agg):
    name = chapters.CHAPTERS.get(c, ("?", []))[0]
    print(f"  ch{c:<2} {name:<45} {agg[c]:>3} 分")
