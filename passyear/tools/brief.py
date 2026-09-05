#!/usr/bin/env python
"""给一个 chapter 生成自足的施工简报，供单个 subagent 独占使用。

产出：
  _brief/<slug>.md              施工简报（题干 + MS 答案 + 判分要点 + 图清单）
  extracted/<slug>/img/*.png    该章用到的题图（已去水印）
  _img/<卷>_msp<NN>.png         答案本身是图的那些 MS 页（170dpi）

执行体只读简报 + 这些 PNG，不用碰 _json，也不该拿到别章的上下文。

用法：
    python tools/brief.py 8          # 生成 ch8 的简报
    python tools/brief.py --all
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chapters import CHAPTERS, SLUG          # noqa: E402
from crop import IMGDIR, render              # noqa: E402
from extract import ROOT                     # noqa: E402

BRIEFDIR = os.path.join(ROOT, "_brief")
JSONDIR = os.path.join(ROOT, "_json")
EXTRACTED = os.path.join(ROOT, "extracted")

DOTS = re.compile(r"\s*\.{6,}\s*")


def clean(line: str) -> str:
    return DOTS.sub(" ", line).rstrip()


def build(ch: int) -> str:
    name, items = CHAPTERS[ch]
    slug = SLUG[ch]
    outdir = os.path.join(EXTRACTED, slug)
    os.makedirs(os.path.join(outdir, "img"), exist_ok=True)
    os.makedirs(BRIEFDIR, exist_ok=True)

    out = [f"# 施工简报 · ch{ch} {name}",
           "",
           f"本章 {len(items)} 题 / {sum(i[2] for i in items)} 分。",
           f"产物目录：`extracted/{slug}/`，**只写这个目录**。",
           "每份卷一个 md，文件名 = 卷 key，例如 `9701_s25_21.md`。",
           ""]

    for key, qn, marks, topic, also in items:
        d = json.load(open(os.path.join(JSONDIR, key + ".json"), encoding="utf-8"))
        q = next(x for x in d["questions"] if x["n"] == qn)
        sess, var = key.split("_")[1], key.split("_")[2]

        out += ["---", "",
                f"## {key} · Q{qn} [{marks}]",
                "",
                f"- 会期：{d['session']}　卷号：9701/{var}　题在第 {q['page']} 页起",
                f"- 主题：{topic}" + (f"　(兼 {', '.join('ch'+str(c) for c in also)})" if also else ""),
                f"- 输出文件：`extracted/{slug}/{key}.md`",
                f"- 题卷 PDF：`originalpdf/9701_{sess}_qp_{var}.pdf`"
                f"　答案 PDF：`originalpdf/9701_{sess}_ms_{var}.pdf`"]
        if d.get("same_as_v3"):
            out.append("- **本卷与 9701/23 同卷**（逐字一致，仅条形码与印刷码不同）——"
                       "md 顶部要写这一行")
        out.append("")

        # 该题用到的图
        figs = []
        for lab in q.get("figures", []):
            m = re.match(r"Figure (\d+)\.(\d+)", lab)
            if not m or int(m.group(1)) != qn:
                continue
            fn = f"{key}_fig{m.group(1)}-{m.group(2)}.png"
            src = os.path.join(IMGDIR, fn)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(outdir, "img", fn))
                figs.append((lab, fn))
        if figs:
            out += ["### 已裁好的图（直接引用，不要自己截）", ""]
            out += [f"- {lab} → `img/{fn}`" for lab, fn in figs]
            out.append("")
        tabs = [t for t in q.get("figures", [])
                if t.startswith("Table") and t.split()[1].startswith(f"{qn}.")]
        if tabs:
            out += [f"### 表格（转成 Markdown 表，**不要截图**）：{', '.join(tabs)}", ""]

        out += ["### 题干原文（已还原上下标、已剥页眉页脚边注）", "", "```"]
        out += [clean(l) for l in q["lines"] if clean(l).strip()]
        out += ["```", ""]

        rows = [r for r in d["ms"]["rows"]
                if re.match(rf"^{qn}(\D|$)", r["qref"])]
        ms_pages = sorted({r["page"] for r in rows})
        out += ["### 官方 mark scheme", "",
                f"（MS 第 {', '.join(map(str, ms_pages))} 页；"
                f"答案栏为空的小问说明**答案本身是一张图**，必须看 MS 页渲染图才能写对）", ""]
        for r in rows:
            out.append(f"**{r['qref']}**　marks = {r['marks']}")
            if r["answer"]:
                out += ["", "- Answer:"] + [f"  - {l}" for l in r["answer"]]
            else:
                out += ["", "- Answer: *（空 —— 答案是图，去看 MS 渲染页）*"]
            if r["guidance"]:
                out += ["- Guidance:"] + [f"  - {l}" for l in r["guidance"]]
            out.append("")

        # 答案是图的小问 → 渲染对应 MS 页
        need = sorted({r["page"] for r in rows if not r["answer"]})
        if need:
            made = render(key, need, kind="ms")
            out += [f"### 必看的 MS 渲染页（答案是图）", ""]
            out += [f"- `_img/{f}`" for f in made]
            out.append("")

    path = os.path.join(BRIEFDIR, slug + ".md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return path


if __name__ == "__main__":
    a = sys.argv[1:]
    chs = sorted(CHAPTERS) if (not a or a[0] == "--all") else [int(x) for x in a]
    for c in chs:
        p = build(c)
        print(f"ch{c}: {os.path.relpath(p, ROOT)}  ({os.path.getsize(p)/1024:.1f} KB)")
