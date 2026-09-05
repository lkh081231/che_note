#!/usr/bin/env python
"""全库验收 —— 每批收工必跑。镜像块不计分，只认正本。"""
from __future__ import annotations
import io, os, re, sys, collections, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from chapters import CHAPTERS, SLUG
from extract import ROOT
from mirror import MIRROR_MARK, split_blocks

EXTRACTED = os.path.join(ROOT, "extracted")
BAD_FLAT = re.compile(r"SF6|3s2|mol–1|H2SO4|SO42")
BAD_CHAR = re.compile(r"ℓ|\$\$|\(_img/|&lt;|&gt;")
BAD_CN   = re.compile(r"环[丙丁戊己庚辛]烷|[\u4e00-\u9fa5]{2,}酸[\u4e00-\u9fa5]?[乙甲]酯")
IMG_RE   = re.compile(r"!\[[^\]]*\]\((img/[^)]+)\)")
SAME_V3  = "本卷与 9701/23 同卷"

def main() -> int:
    fails = []
    per_paper = collections.Counter()
    canon_q = canon_m = mirror_blocks = 0

    for ch in sorted(SLUG):
        d = os.path.join(EXTRACTED, SLUG[ch])
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md") or fn == "README.md":
                continue
            p, rel = os.path.join(d, fn), f"{SLUG[ch]}/{fn}"
            t = io.open(p, encoding="utf-8").read()
            for name, rx in (("压平上下标", BAD_FLAT), ("ℓ/$$/_img/实体", BAD_CHAR),
                             ("中文化学名", BAD_CN)):
                m = rx.search(t)
                if m:
                    fails.append(f"[{name}] {rel}: {m.group(0)!r}")
            if SAME_V3 in t and fn[:-3] not in ("9701_w24_21", "9701_w25_21"):
                fails.append(f"[同卷错标] {rel}")
            for r in IMG_RE.findall(t):
                if not os.path.exists(os.path.join(d, r)):
                    fails.append(f"[图缺失] {rel} -> {r}")
            _, blocks = split_blocks(t)
            for qn, blk in blocks:
                if MIRROR_MARK in blk.split("\n", 1)[0]:
                    mirror_blocks += 1
                    continue
                marks = next((mk for c, v in CHAPTERS.items() for kk, q, mk, *_ in v[1]
                              if kk == fn[:-3] and q == qn and c == ch), None)
                if marks is None:
                    fails.append(f"[归属错] {rel} Q{qn} 不该由 ch{ch} 主管")
                    continue
                per_paper[fn[:-3]] += marks
                canon_q += 1; canon_m += marks

    bad60 = {k: v for k, v in per_paper.items() if v != 60}
    print(f"正本 {canon_q}/77 题，{canon_m}/960 分；镜像块 {mirror_blocks} 个")
    print(f"卷数 {len(per_paper)}/16　" +
          ("✅ 每卷分值均为 60" if not bad60 else f"❌ 分值≠60: {bad60}"))
    if bad60:
        fails.append(f"[逐卷分值] {bad60}")

    r = subprocess.run(["git", "status", "--porcelain", "../reference.md", "../reference.pdf"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.stdout.strip():
        fails.append("[reference.md 被改动] " + r.stdout.strip())

    if fails:
        print(f"\n❌ {len(fails)} 项不通过：")
        for f in fails[:20]:
            print("  ", f)
        return 1
    print("✅ 全部检查通过")
    return 0

if __name__ == "__main__":
    sys.exit(main())
