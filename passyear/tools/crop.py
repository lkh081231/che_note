#!/usr/bin/env python
"""CIE 9701 Paper 2 —— 图表裁剪 / 整页渲染。

裁图走 **caption 锚定带状裁剪**：图恒定位于自己的 `Figure N.N` / `Fig. N.N`
caption 正上方，取「上一条正文基线底部」到「caption 顶部」之间的整栏宽带。

不走 get_drawings() 聚类找 bbox —— 实测答题虚线和页面边框会把整页并成一块。

用法：
    python tools/crop.py 9701_s26_21            # 裁一份卷的全部图
    python tools/crop.py --all
    python tools/crop.py --pages 9701_s26_21 2 3 4    # 渲染指定页（视觉核对用）
"""
from __future__ import annotations

import os
import re
import sys

import fitz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract import PAPERS, PDFDIR, ROOT, is_noise, line_text   # noqa: E402

IMGDIR = os.path.join(ROOT, "_img")

CAPTION_RE = re.compile(r"^\s*(?:(Fig(?:ure)?)\.?|(Table))\s*(\d+\.\d+)\s*$")

# 正文栏范围：左右收进来，天然排掉竖排边注、条形码、页底站点行
COL_X0, COL_X1 = 48.0, 549.0
MAX_Y = 812.0
MIN_H = 26.0            # 太薄的多半不是图
MAX_BAND = 430.0        # 一张图最多占这么高，防止裁飞
DEFAULT_DPI = 300


def _is_prose(t: str) -> bool:
    """成句的正文行 —— 用来当图的上/下边界。

    图内部的标注（坐标轴刻度 `10 15 20`、原子字母 `F`、结构式片段）都很短，
    答题虚线 `......` 也不算；只有真正的句子才配当边界。
    """
    t = t.strip()
    if is_noise(t) or len(t) < 25:
        return False
    if set(t) <= set(". "):                 # 答题虚线
        return False
    return t.count(" ") >= 3


WM_RE = re.compile(r"papacambridge|Trace ID|Downloaded from|Licensed for hosting"
                   r"|Re-uploading, mirroring", re.I)


def strip_watermark(doc: fitz.Document) -> tuple[int, int]:
    """去掉 PapaCambridge 的两处水印。

    1. **斜压在题目上的那条**：不是文字对象，而是每页一个叫 `FormXob.pcm`
       的 Form XObject，里面是轮廓化的矢量路径 —— 所以 get_text 看不见它，
       redaction 也删不掉。直接把流清空。
    2. **页底那条站点行**：是真文字，用 redaction 删；只删文字不动 line art。
    """
    killed = set()
    for page in doc:
        for xref, name, *_ in page.get_xobjects():
            if "pcm" in name.lower() and xref not in killed:
                doc.update_stream(xref, b" ")
                killed.add(xref)

    n = 0
    for page in doc:
        hits = []
        for b in page.get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for ln in b["lines"]:
                t = "".join(s["text"] for s in ln["spans"])
                if WM_RE.search(t):
                    hits.append(fitz.Rect(ln["bbox"]))
        for r in hits:
            page.add_redact_annot(r)
        if hits:
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                                  graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                                  text=fitz.PDF_REDACT_TEXT_REMOVE)
            n += len(hits)
    return len(killed), n


def _text_lines(page: fitz.Page):
    """(y0, y1, x0, text)，只保留横排正文。"""
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for ln in b["lines"]:
            if abs(ln["dir"][0]) < 0.9:
                continue
            t = line_text(ln)
            if not t.strip():
                continue
            x0, y0, x1, y1 = ln["bbox"]
            out.append((y0, y1, x0, t))
    out.sort()
    return out


def crop_paper(key: str, dpi: int = DEFAULT_DPI) -> list[dict]:
    sess, var = key.split("_")[1], key.split("_")[2]
    doc = fitz.open(os.path.join(PDFDIR, f"9701_{sess}_qp_{var}.pdf"))
    strip_watermark(doc)
    os.makedirs(IMGDIR, exist_ok=True)
    made = []

    for pno, page in enumerate(doc):
        lines = _text_lines(page)
        for i, (y0, y1, x0, t) in enumerate(lines):
            m = CAPTION_RE.match(t)
            if not m or not m.group(1):
                continue        # 只裁 Figure；Table 一律转 Markdown 表，不截图
            label = f"Figure {m.group(3)}"

            # CIE 的 figure caption 在图**下方** → 取 caption 之前那一段。
            # 边界只认「成句的正文行」：图里的坐标轴刻度、原子字母、结构式标注
            # 都是短碎片，拿它们当上界会把图裁没（实测覆盖率从 57% 掉下来）。
            top = 55.0
            for j in range(i - 1, -1, -1):
                py0, py1, px0, pt = lines[j]
                if py1 >= y0 - 1:            # 和 caption 同一行带，跳过
                    continue
                if not _is_prose(pt):
                    continue
                top = py1 + 3
                break
            bottom = min(y0 - 2, MAX_Y)

            # 少数图 caption 在上方 → 上面那条带太薄时改取下方那条带
            if bottom - top < MIN_H:
                top = y1 + 3
                bottom = MAX_Y
                for j in range(i + 1, len(lines)):
                    ny0, ny1, nx0, nt = lines[j]
                    if ny0 <= y1 + 1 or not _is_prose(nt):
                        continue
                    bottom = min(ny0 - 3, MAX_Y)
                    break
            top = max(top, bottom - MAX_BAND)
            if bottom - top < MIN_H:
                continue

            clip = fitz.Rect(COL_X0, top, COL_X1, bottom)
            name = f"{key}_fig{m.group(3).replace('.', '-')}.png"
            page.get_pixmap(clip=clip, dpi=dpi).save(os.path.join(IMGDIR, name))
            made.append({"label": label, "page": pno + 1, "file": name,
                         "h": round(bottom - top)})
    return made


def render(key: str, pages: list[int], dpi: int = 170, kind: str = "qp") -> list[str]:
    """整页 PNG，只给需要视觉核对的页用（控 image token）。

    kind="ms" 渲染 mark scheme —— 有些答案本身就是图（dot-and-cross、orbital
    形状、机理箭头），文字层里只剩只言片语，必须看图才能写对。
    """
    sess, var = key.split("_")[1], key.split("_")[2]
    doc = fitz.open(os.path.join(PDFDIR, f"9701_{sess}_{kind}_{var}.pdf"))
    strip_watermark(doc)
    os.makedirs(IMGDIR, exist_ok=True)
    out = []
    for p in pages:
        name = f"{key}_{kind}p{p:02d}.png"
        doc[p - 1].get_pixmap(dpi=dpi).save(os.path.join(IMGDIR, name))
        out.append(name)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] in ("--pages", "--ms-pages"):
        kind = "ms" if a[0] == "--ms-pages" else "qp"
        print(render(a[1], [int(x) for x in a[2:]], kind=kind))
    else:
        keys = PAPERS if (not a or a[0] == "--all") else a
        for k in keys:
            made = crop_paper(k)
            print(f"{k}: 裁出 {len(made)} 张  "
                  + ", ".join(f"{m['label']}(p{m['page']},h{m['h']})" for m in made[:5])
                  + (" …" if len(made) > 5 else ""))
