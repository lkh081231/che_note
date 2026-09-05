# -*- coding: utf-8 -*-
"""按**小问标签**重算分值分布，喂给 classification.md 的热度表。

口径两条（2026-09-05 用户拍板）：

1. **不按 chapter 统计，按大类统计。** CIE 的章节切得很碎（ch10 Group 2 只有几条 outcome，
   ch20 Polymerisation 更少），单章分值上下浮动大、当复习优先级看没意义。
   分组按 syllabus 自己的编排走：物理化学逐章列，无机 9–12 / 有机 13–21 / 分析 22 各并成一块。
2. 打过标签的题按小问标签分配，没打标签的题（= 单章题）整题归主章。

一个小问同时压两章时：**同一大类内只记一次**（`ch16 ch17` 都是有机，不重复计），
**跨大类才各记一次**（`ch15 ch22` = 有机 + 分析，两边都得会做这一空）。
"""
import sys, io
if __name__ == "__main__":      # 被 import 时不要动 stdout，否则会把调用者的 stdout 关掉
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, "tools")
import mirror
from chapters import CHAPTERS

GROUPS = [
    ((1, 2),               "1–2 Atomic structure & stoichiometry"),
    ((3,),                 "3 Chemical bonding"),
    ((4,),                 "4 States of matter"),
    ((5,),                 "5 Chemical energetics"),
    ((6,),                 "6 Electrochemistry"),
    ((7,),                 "7 Equilibria"),
    ((8,),                 "8 Reaction kinetics"),
    (tuple(range(9, 13)),  "9–12 Inorganic chemistry"),
    (tuple(range(13, 22)), "13–21 Organic chemistry"),
    ((22,),                "22 Analysis"),
]
GROUP_OF = {ch: name for chs, name in GROUPS for ch in chs}
NAMES = [name for _, name in GROUPS]


def collect():
    """→ (每大类分值, 每大类涉及题数, 每章分值)"""
    owner, also, canon, session = mirror.load_state()
    gm = {n: 0 for n in NAMES}
    gq = {n: 0 for n in NAMES}
    cm = {}

    for (key, qn), blk in canon.items():
        tags = mirror.subq_tags(blk)
        if tags:
            groups_here = set()
            for _, marks, chs in tags:
                for c in chs:
                    cm[c] = cm.get(c, 0) + marks
                for g in {GROUP_OF[c] for c in chs}:      # 同大类内只记一次
                    gm[g] += marks
                    groups_here.add(g)
        else:
            c = owner[(key, qn)]
            total = mirror.marks_of(key, qn)
            cm[c] = cm.get(c, 0) + total
            gm[GROUP_OF[c]] += total
            groups_here = {GROUP_OF[c]}
        for g in groups_here:
            gq[g] += 1

    return gm, gq, cm, owner, canon


if __name__ == "__main__":
    gm, gq, cm, owner, canon = collect()
    print("| 部分 | 涉及题数 | 分值 | 占 960 |")
    print("|---|---:|---:|---:|")
    for n in sorted(NAMES, key=lambda n: -gm[n]):
        print(f"| **{n}** | {gq[n]} | {gm[n]} | {gm[n] / 960 * 100:.1f}% |")
    print(f"\n合计 {sum(gm.values())}（>960 是因为跨大类的小问在两边各记一次）")
    print("\n各章明细（只作参考，不当复习优先级用）：")
    for c in sorted(cm):
        print(f"  ch{c:<2} {CHAPTERS.get(c, ('?', []))[0]:<45} {cm[c]:>3}")
