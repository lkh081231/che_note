#!/usr/bin/env python
"""跨章大题镜像器 —— 一道题同时出现在它涉及的每一个 chapter 文件夹里。

CIE 的大题经常横跨好几章（77 题里有 43 题是跨章的）。按主章归档的话，
复习 ch9 时就看不到那道「主章 ch3、兼 ch9」的题。所以：

    **主章持有正本，其余相关章各放一份镜像。**

- 正本（canonical）：`chapters.py` 里该题的主章那一份，**唯一可手改的地方**。
- 镜像（mirror）：脚本生成，标题行带 `⟨镜像⟩` 标记，正文与正本逐字一致。

本脚本是**幂等**的：每次运行都先把所有带 `⟨镜像⟩` 标记的块丢掉，
再从正本重新拼装，所以反复跑不会重复堆叠。

⚠️ **正在跑标注 subagent 时不要执行本脚本** —— 它会重写正本文件，
   和执行体的 Edit 撞车。等所有 agent 报完工再跑一次。

用法：
    python tools/mirror.py            # 重建全部镜像
    python tools/mirror.py --check    # 只检查是否与正本同步，不写文件（退出码 1 = 不同步）
"""
from __future__ import annotations

import io
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chapters import CHAPTERS, SLUG          # noqa: E402
from extract import ROOT                     # noqa: E402

EXTRACTED = os.path.join(ROOT, "extracted")

MIRROR_MARK = "⟨镜像"
Q_HEAD = re.compile(r"^## Q(\d+) ", re.M)
IMG_RE = re.compile(r"!\[[^\]]*\]\((img/[^)]+)\)")
TITLE_RE = re.compile(r"^# ch\d+ .*? · 9701/\d\d (.+)$", re.M)


def chapter_name(ch: int) -> str:
    return CHAPTERS[ch][0]


def split_blocks(text: str):
    """(header, [(qn, block_text), …])　block_text 含它自己的 `## Q…` 标题行。"""
    hits = list(Q_HEAD.finditer(text))
    if not hits:
        return text, []
    header = text[: hits[0].start()]
    blocks = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        blocks.append((int(m.group(1)), text[m.start():end]))
    return header, blocks


def load_state():
    """扫描 extracted/，取回每道题的正本块，以及每份卷的会期名。"""
    owner, also = {}, {}
    for ch, (_, items) in CHAPTERS.items():
        for key, qn, marks, topic, extra in items:
            owner[(key, qn)] = ch
            also[(key, qn)] = list(extra)

    canon, session = {}, {}
    for ch, (_, _) in CHAPTERS.items():
        d = os.path.join(EXTRACTED, SLUG[ch])
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md") or fn == "README.md":
                continue
            key = fn[:-3]
            text = io.open(os.path.join(d, fn), encoding="utf-8").read()
            m = TITLE_RE.search(text)
            if m:
                session.setdefault(key, m.group(1).strip())
            header, blocks = split_blocks(text)
            for qn, blk in blocks:
                if MIRROR_MARK in blk.split("\n", 1)[0]:
                    continue                       # 旧镜像，丢掉
                if owner.get((key, qn)) != ch:
                    print(f"  ! {SLUG[ch]}/{fn} 的 Q{qn} 不归本章（chapters.py 说是 "
                          f"ch{owner.get((key, qn))}），跳过")
                    continue
                canon[(key, qn)] = blk.rstrip() + "\n"
    return owner, also, canon, session


# 小问标签：`### (b)(iii) [3] · ch9 ch11`
SUBQ = re.compile(r"^### (.*?)\[(\d+)\]\s*·\s*((?:ch\d+\s*)+)$", re.M)

# 一道题要在某章放整题镜像，该章得在这道题里占够分量：
#   既要 ≥2 分（1 分的顺带考点不算），也要 ≥15% 的题分。
# 只卡绝对分会出事：实测 m25_22 Q1 [17] 散进 8 个章、每章才 1–2 分，
# 整题镜像进去全是噪音；而 s26_23 Q1 [12] 有 8 分是 ch11，那是真·双章题。
# 够不上门槛但确实考到的，不做镜像，改成在该章 README 里列一条「零星考点」指路。
MIRROR_MIN_MARKS = 2
MIRROR_MIN_SHARE = 0.15


def subq_tags(blk: str):
    """[(小问标签, 分值, [章号…]), …]，未打标签的题返回空表。"""
    out = []
    for label, marks, chs in SUBQ.findall(blk):
        out.append((label.strip(), int(marks),
                    [int(c) for c in re.findall(r"ch(\d+)", chs)]))
    return out


def weights(blk: str) -> dict[int, int]:
    """各章在这道题里占的分。"""
    w: dict[int, int] = {}
    for _, marks, chs in subq_tags(blk):
        for c in chs:
            w[c] = w.get(c, 0) + marks
    return w


def effective_also(canon, owner, also):
    """镜像目标章 + 零星考点。打过标签的题以标签为准，没打过的沿用 chapters.py。"""
    eff, minor, from_tags = {}, {}, 0
    for (key, qn), blk in canon.items():
        w = weights(blk)
        if not w:
            eff[(key, qn)] = list(also[(key, qn)])
            minor[(key, qn)] = {}
            continue
        from_tags += 1
        total = marks_of(key, qn) or sum(w.values())
        big, small = [], {}
        for c, m in sorted(w.items()):
            if c == owner[(key, qn)]:
                continue
            if m >= MIRROR_MIN_MARKS and m >= MIRROR_MIN_SHARE * total:
                big.append(c)
            else:
                small[c] = m
        eff[(key, qn)] = big
        minor[(key, qn)] = small
    return eff, minor, from_tags


def marks_of(key: str, qn: int) -> int:
    for _, items in CHAPTERS.values():
        for k, q, m, *_ in items:
            if k == key and q == qn:
                return m
    return 0



def write_readmes(owner, also, canon, minor=None):
    """每章一份 README：本章主管的题 + 从别章镜像进来的题。"""
    TOTAL = 960
    rank = {ch: i + 1 for i, ch in enumerate(
        sorted((c for c in CHAPTERS if CHAPTERS[c][1]),
               key=lambda c: -sum(i[2] for i in CHAPTERS[c][1])))}
    topic = {(k, q): (t, tuple(a)) for _, items in CHAPTERS.values()
             for k, q, m, t, a in items}
    own_rows, mir_rows = {}, {}
    for (key, qn), ch in owner.items():
        if (key, qn) not in canon:
            continue
        own_rows.setdefault(ch, []).append((key, qn))
        for c in also[(key, qn)]:
            mir_rows.setdefault(c, []).append((key, qn))

    n = 0
    for ch in sorted(SLUG):
        d = os.path.join(EXTRACTED, SLUG[ch])
        if not os.path.isdir(d):
            continue
        own = sorted(own_rows.get(ch, []))
        mir = sorted(mir_rows.get(ch, []))
        marks = sum(marks_of(k, q) for k, q in own)
        out = [f"# ch{ch:02d} {chapter_name(ch)}", ""]
        if own:
            out.append(f"CIE 9701 Paper 2 · 2024–2026 · 本章主管 **{len(own)} 题 / {marks} 分**，"
                       f"占 Paper 2 总分 **{marks/TOTAL*100:.1f}%**，热度第 **{rank[ch]}** / {len(rank)}。")
        else:
            out.append("CIE 9701 Paper 2 · 2024–2026 · 本章 **没有单独成题**，"
                       "下面全是从别章镜像过来的跨章题。")
        out.append("")
        if own:
            out += ["## 本章主管", "", "| 卷 | 题 | 分 | 主题 |", "|---|---|---:|---|"]
            for k, q in own:
                t, a = topic[(k, q)]
                tag = ("　(兼 " + ", ".join(f"ch{c}" for c in a) + ")") if a else ""
                out.append(f"| [{k.split('_')[1]}/{k.split('_')[2]}]({k}.md) | Q{q} | "
                           f"{marks_of(k,q)} | {t}{tag} |")
            out.append("")
        if mir:
            out += ["## 跨章镜像（正本在别章，这里同样能看全题）", "",
                    "| 卷 | 题 | 分 | 正本章 | 主题 |", "|---|---|---:|---|---|"]
            for k, q in mir:
                t, _ = topic[(k, q)]
                src = owner[(k, q)]
                out.append(f"| [{k.split('_')[1]}/{k.split('_')[2]}]({k}.md) | Q{q} | "
                           f"{marks_of(k,q)} | [ch{src}](../{SLUG[src]}/{k}.md) | {t} |")
            out.append("")
        out.append("总表见 [`../../classification.md`](../../classification.md)。")
        io.open(os.path.join(d, "README.md"), "w",
                encoding="utf-8").write("\n".join(out) + "\n")
        n += 1
    return n


def build(check_only: bool = False) -> int:
    owner, also, canon, session = load_state()
    also, minor, tagged = effective_also(canon, owner, also)

    # (chapter, key) → [(qn, is_mirror)]
    plan: dict[tuple[int, str], list[tuple[int, bool]]] = {}
    for (key, qn), ch in owner.items():
        if (key, qn) not in canon:
            continue
        plan.setdefault((ch, key), []).append((qn, False))
        for c in also[(key, qn)]:
            plan.setdefault((c, key), []).append((qn, True))

    stale, written, mirrors = [], 0, 0
    for (ch, key), qns in sorted(plan.items()):
        qns.sort()
        slug = SLUG[ch]
        d = os.path.join(EXTRACTED, slug)
        os.makedirs(os.path.join(d, "img"), exist_ok=True)
        sess, var = key.split("_")[1], key.split("_")[2]

        own = [q for q, mir in qns if not mir]
        mir = [q for q, mir in qns if mir]
        total = sum(marks_of(key, q) for q, _ in qns)
        bits = []
        if own:
            bits.append("本章主管 " + "、".join(f"Q{q} [{marks_of(key,q)}]" for q in own))
        if mir:
            bits.append("镜像 " + "、".join(
                f"Q{q} [{marks_of(key,q)}]（主章 ch{owner[(key,q)]}）" for q in mir))

        out = [f"# ch{ch:02d} {chapter_name(ch)} · 9701/{var} {session.get(key,'')}".rstrip(),
               "",
               f"> 题卷 `originalpdf/9701_{sess}_qp_{var}.pdf` ｜ "
               f"答案 `originalpdf/9701_{sess}_ms_{var}.pdf`",
               f"> 本卷本章共 {len(qns)} 题 / {total} 分：" + "；".join(bits)]
        if key in ("9701_w24_21", "9701_w25_21"):
            out.append("> 本卷与 9701/23 同卷（逐字一致，仅条形码与印刷码不同）")
        out += ["", "---", ""]

        for qn, is_mirror in qns:
            blk = canon[(key, qn)]
            if is_mirror:
                src = owner[(key, qn)]
                head, rest = blk.split("\n", 1)
                m = re.match(r"^(## Q\d+ \[\d+\])", head)
                head = (f"{m.group(1)}　{MIRROR_MARK} · 主章 ch{src} {chapter_name(src)}⟩"
                        if m else head)
                note = (f"> 本题正本在 "
                        f"[`{SLUG[src]}/{key}.md`](../{SLUG[src]}/{key}.md)，此处为镜像。"
                        f"**不要在本文件里改它** —— 改正本，再跑 `python tools/mirror.py`。")
                blk = f"{head}\n\n{note}\n{rest}"
                mirrors += 1
                for rel in IMG_RE.findall(blk):          # 图跟着镜像走
                    s = os.path.join(EXTRACTED, SLUG[src], rel)
                    t = os.path.join(d, rel)
                    if os.path.exists(s) and not os.path.exists(t):
                        if not check_only:
                            shutil.copy2(s, t)
            out.append(blk.rstrip())
            out.append("")

        text = "\n".join(out).rstrip() + "\n"
        path = os.path.join(d, key + ".md")
        old = io.open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old == text:
            continue
        stale.append(os.path.relpath(path, ROOT))
        if not check_only:
            io.open(path, "w", encoding="utf-8").write(text)
            written += 1

    # 清掉不再入 plan 的 md —— 门槛或标签变了以后遗留的旧镜像文件。
    # 正本文件一定在 plan 里（plan 就是按 owner 建的），所以这里删掉的只可能是过期镜像。
    removed = []
    for ch in CHAPTERS:
        d = os.path.join(EXTRACTED, SLUG[ch])
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md") or fn == "README.md":
                continue
            if (ch, fn[:-3]) in plan:
                continue
            removed.append(os.path.relpath(os.path.join(d, fn), ROOT))
            if not check_only:
                os.remove(os.path.join(d, fn))

    # 再清掉没有任何 md 引用的图（只可能是跟着上面那些镜像复制进来的）。
    orphan = []
    for ch in CHAPTERS:
        d = os.path.join(EXTRACTED, SLUG[ch])
        imgd = os.path.join(d, "img")
        if not os.path.isdir(imgd):
            continue
        used = set()
        for fn in os.listdir(d):
            if fn.endswith(".md"):
                used |= set(IMG_RE.findall(io.open(os.path.join(d, fn), encoding="utf-8").read()))
        for fn in sorted(os.listdir(imgd)):
            if "img/" + fn in used:
                continue
            orphan.append(os.path.relpath(os.path.join(imgd, fn), ROOT))
            if not check_only:
                os.remove(os.path.join(imgd, fn))

    if check_only:
        if stale or removed or orphan:
            print(f"不同步：{len(stale)} 个文件需要重建，"
                  f"{len(removed)} 个过期镜像 + {len(orphan)} 张孤儿图待删")
            for p in stale[:10]:
                print("   ", p)
            return 1
        print("全部镜像与正本同步")
        return 0

    r = write_readmes(owner, also, canon, minor)
    print(f"写了 {written} 个 md（镜像块 {mirrors} 个，覆盖 {len(plan)} 个「章×卷」组合），{r} 份 README")
    if removed or orphan:
        print(f"删了 {len(removed)} 个过期镜像 md、{len(orphan)} 张孤儿图")
        for p in removed:
            print(f"  - {p}")
    print(f"其中 {tagged}/{len(canon)} 道题的镜像目标由小问标签推导（门槛 ≥{MIRROR_MIN_MARKS} 分），其余沿用 chapters.py")
    return 0


if __name__ == "__main__":
    sys.exit(build(check_only="--check" in sys.argv))
