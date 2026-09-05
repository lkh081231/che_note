#!/usr/bin/env python
"""CIE 9701 Paper 2 —— 确定性文本抽取器。

把 PDF 的 span 层还原成上下标正确的干净文本，并切出题号结构。
机械正确性在这里全部做完，下游（模型）只负责版式和判断。

用法：
    python tools/extract.py 9701_s26_21          # 抽一份卷（qp + ms）
    python tools/extract.py --all                # 抽全部 16 份
    python tools/extract.py --selftest           # 上下标还原自检
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDFDIR = os.path.join(ROOT, "originalpdf")
OUTDIR = os.path.join(ROOT, "_json")

# 16 份唯一卷（w24_23 / w25_23 与 _21 逐字相同，不提）
PAPERS = [
    "9701_m24_22",
    "9701_s24_21", "9701_s24_22", "9701_s24_23",
    "9701_w24_21", "9701_w24_22",
    "9701_m25_22",
    "9701_s25_21", "9701_s25_22", "9701_s25_23",
    "9701_w25_21", "9701_w25_22",
    "9701_m26_22",
    "9701_s26_21", "9701_s26_22", "9701_s26_23",
]

DUP_OF_V3 = {"9701_w24_21", "9701_w25_21"}

SESSION_NAME = {"m": "Feb/March", "s": "May/June", "w": "Oct/Nov"}

# ---------------------------------------------------------------- 上下标映射

SUB_MAP = str.maketrans({
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "+": "₊", "-": "₋", "–": "₋", "−": "₋", "=": "₌", "(": "₍", ")": "₎",
    "a": "ₐ", "e": "ₑ", "o": "ₒ", "x": "ₓ", "h": "ₕ", "k": "ₖ",
    "l": "ₗ", "m": "ₘ", "n": "ₙ", "p": "ₚ", "s": "ₛ", "t": "ₜ",
    "r": "ᵣ", "i": "ᵢ", "j": "ⱼ", "u": "ᵤ", "v": "ᵥ",
})

SUP_MAP = str.maketrans({
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "+": "⁺", "-": "⁻", "–": "⁻", "−": "⁻", "=": "⁼", "(": "⁽", ")": "⁾",
    "n": "ⁿ", "i": "ⁱ", "x": "ˣ", "o": "ᵒ",
})


def _map_script(text: str, table, allowed: str) -> str | None:
    """全部字符都能映射才返回映射结果，否则返回 None（保留原样）。"""
    core = text.strip()
    if not core:
        return None
    if any(c not in allowed for c in core):
        return None
    return text.translate(table)


SUB_OK = set("0123456789+-–−=()aeoxhklmnpstrijuv ")
SUP_OK = set("0123456789+-–−=()nixo ")

# ---------------------------------------------------------------- 噪声过滤

NOISE_RE = [
    re.compile(r"^\s*9701/\d\d(/[A-Z]/[A-Z]/\d\d)?\s*$"),
    re.compile(r"©\s*(UCLES|Cambridge University Press)"),
    re.compile(r"^\s*Page\s+\d+\s+of\s+\d+\s*$"),
    re.compile(r"^\s*PUBLISHED\s*$"),
    re.compile(r"^\s*Cambridge International AS & A Level\b"),
    re.compile(r"DO NOT WRITE IN THIS MARGIN"),
    re.compile(r"papacambridge", re.I),
    re.compile(r"^\s*Trace ID:", re.I),
    re.compile(r"Downloaded from|Licensed for hosting|Re-uploading, mirroring", re.I),
    re.compile(r"^\s*Mark Scheme\s*$"),
    re.compile(r"^\s*(BLANK PAGE|\[Turn over)\b"),
    re.compile(r"^\s*\*[\s\d]{8,}\*\s*$"),          # 条形码数字串（含空格形态）
    re.compile(r"^\s*DC\s*\([A-Z/]+\)\s*[\d/]+\s*$"),
    re.compile(r"^\s*DFD\s*$"),                      # 印刷定位标记
    re.compile(r"^\s*This document has \d+ pages"),
    re.compile(r"^\s*(May/June|October/November|February/March)\s+\d{4}\s*$"),
]

# 条形码乱码：非 ASCII 且不是我们要的化学/排版字符
CHEM_OK = set("°⦵→⇌⁻⁺₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹–—’‘“”·×÷≈≤≥±ΔΩαβγπθλμ½¼¾ⁿˣᵒₐₑₒₓₕₖₗₘₙₚₛₜᵣᵢⱼᵤᵥ…′″")


def is_garbage(text: str) -> bool:
    core = text.strip()
    if not core:
        return True
    weird = sum(
        1 for c in core
        if (ord(c) < 32 and c != "\t") or (ord(c) > 127 and c not in CHEM_OK)
    )
    return weird >= max(3, len(core) * 0.4)


# `Cl` / `Al` 里的 l 在 PDF 中是独立斜体字形，抽出来会在角标前多一个空格
_SCRIPT_CHARS = "₀₁₂₃₄₅₆₇₈₉⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"
_TIGHTEN = re.compile(rf"(?<=[A-Za-z\)\]])\s+(?=[{_SCRIPT_CHARS}])")


def is_noise(text: str) -> bool:
    if not text.strip():
        return True
    for rx in NOISE_RE:
        if rx.search(text):
            return True
    return is_garbage(text)


# ---------------------------------------------------------------- 核心：span → 文本


def line_text(line: dict) -> str:
    """把一行的 spans 拼成上下标正确的文本。"""
    spans = [s for s in line["spans"] if s["text"]]
    if not spans:
        return ""

    sizes = [round(s["size"], 2) for s in spans]
    base_size = max(sizes)
    # 正文 span 的基线（取最大字号那些 span 的中位 y）
    base_ys = sorted(s["origin"][1] for s in spans if round(s["size"], 2) >= base_size - 0.01)
    base_y = base_ys[len(base_ys) // 2]

    out = []
    for i, s in enumerate(sorted(spans, key=lambda s: s["origin"][0])):
        txt = s["text"]
        small = round(s["size"], 2) < base_size * 0.92
        if not small:
            out.append(txt)
            continue

        dy = s["origin"][1] - base_y
        flat = abs(dy) <= 1.0
        sup = dy < -1.0 or (flat and bool(s["flags"] & 1))
        # question paper 靠基线偏移；mark scheme 同基线、只缩字号
        # （CO₂ 抽出来是 size 7.2 + origin.y 与正文完全相同）
        sub = (not sup) and (dy > 1.0 or (flat and i > 0 and len(txt.strip()) <= 4))

        if sup:
            m = _map_script(txt, SUP_MAP, SUP_OK)
        elif sub:
            m = _map_script(txt, SUB_MAP, SUB_OK)
        else:
            m = None
        out.append(m if m is not None else txt)

    return _TIGHTEN.sub("", "".join(out))


# 部分年份的 mark scheme 整页旋转 90°（s24 全系列），阅读方向随之改变
_READ_DIR = {0: (1.0, 0.0), 90: (0.0, -1.0), 180: (-1.0, 0.0), 270: (0.0, 1.0)}


def _q(v: float) -> float:
    """行序量化到 2pt —— 同一行的基线会差零点几个点（61.4 vs 61.5），
    不量化的话题号会排到题干后面。"""
    return round(v / 2.0) * 2.0


def _sort_key(bbox, rot: int, uw: float, uh: float):
    """→ (行序, 栏坐标)。栏坐标归一到「距版心左边的点数」，
    这样旋转页和未旋转页可以用同一套阈值。uw/uh 是**未旋转**的页宽/页高。"""
    x0, y0, x1, y1 = bbox
    if rot == 0:
        return (_q(y0), round(x0, 1))
    if rot == 90:
        return (_q(x0), round(uh - y1, 1))
    if rot == 180:
        return (_q(uh - y1), round(uw - x1, 1))
    return (_q(uw - x1), round(y0, 1))


def page_rows(page: fitz.Page, pageno: int = 0, drop_bottom: float = 26.0):
    """一页的正文行，返回 (行序, 栏坐标, 文本)，已按阅读顺序排好。

    行序 = 沿页面向下的位置；栏坐标 = 沿行方向的位置（用来分 MS 的四栏）。
    """
    h = page.rect.height
    rot = page.rotation % 360
    R = page.rect
    uw, uh = (R.height, R.width) if rot in (90, 270) else (R.width, R.height)
    rdx, rdy = _READ_DIR.get(rot, (1.0, 0.0))
    rows = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for ln in b["lines"]:
            # 与阅读方向垂直的（竖排边注）直接丢
            dx, dy = ln["dir"]
            if dx * rdx + dy * rdy < 0.9:
                continue
            y0 = ln["bbox"][1]
            # 页底站点行：只有未旋转时能按几何位置切，旋转页交给正则兜住
            if rot == 0 and y0 > h - drop_bottom:
                continue
            t = line_text(ln)
            if is_noise(t):
                continue
            # 页眉/页脚处孤零零的页码，会和题号撞车
            if t.strip() == str(pageno) and rot == 0 and (y0 < 60 or y0 > h - 60):
                continue
            rows.append(_sort_key(ln["bbox"], rot, uw, uh) + (t,))
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows


def page_lines(page: fitz.Page, pageno: int = 0, drop_bottom: float = 26.0) -> list[str]:
    return [r[2] for r in page_rows(page, pageno, drop_bottom)]


# ---------------------------------------------------------------- 结构切分

# 题号或者单独成行（`1 `），或者和题干同行（`1 Bismuth is …`）
Q_RE = re.compile(r"^\s*(\d{1,2})\s*$|^\s*(\d{1,2})\s+(?=[A-Z(])")
PART_RE = re.compile(r"^\s*(\((?:[a-z]|[ivx]{1,4})\)\s*)+")
MARKS_RE = re.compile(r"\[(\d{1,2})\]")
FIG_RE = re.compile(r"\b(?:Fig(?:ure)?\.?)\s*(\d+\.\d+)")
TAB_RE = re.compile(r"\bTable\s*(\d+\.\d+)")


def extract_qp(path: str) -> dict:
    doc = fitz.open(path)
    pages, figures, flat = [], [], []
    for i, page in enumerate(doc):
        rows = page_rows(page, pageno=i + 1)
        lines = [r[2] for r in rows]
        flat += [(i + 1, r[1], r[2]) for r in rows]      # (页, 左边距 x, 文本)
        pages.append({"page": i + 1, "lines": lines})
        for ln in lines:
            for m in FIG_RE.finditer(ln):
                figures.append({"label": f"Figure {m.group(1)}", "page": i + 1})
            for m in TAB_RE.finditer(ln):
                figures.append({"label": f"Table {m.group(1)}", "page": i + 1})

    # 切大题：题号递增 1、必须顶左边距、光秃秃的数字后面得跟真题干
    # （否则坐标轴刻度 "5" 会被当成第 5 题 —— m26_22 / s24_22 上踩过）
    questions, cur, expect = [], None, 1
    for idx, (pg, x0, ln) in enumerate(flat):
        m = Q_RE.match(ln)
        num = int(m.group(1) or m.group(2)) if m else None
        rest = ln[m.end():].strip() if m else ""
        ok = num == expect and x0 < 95
        if ok and not rest:                       # 题号单独成行
            nxts = [flat[j][2].strip() for j in range(idx + 1, min(idx + 3, len(flat)))]
            ok = any(len(n) > 15 and (n[0] == "(" or n[0].isupper()) for n in nxts)
        if ok:
            if cur:
                questions.append(cur)
            cur = {"n": expect, "page": pg, "lines": [rest] if rest else []}
            expect += 1
        elif cur:
            cur["lines"].append(ln)
    if cur:
        questions.append(cur)

    for q in questions:
        body = "\n".join(q["lines"])
        q["marks"] = sum(int(x) for x in MARKS_RE.findall(body))
        q["figures"] = sorted(set(
            [f"Figure {x}" for x in FIG_RE.findall(body)]
            + [f"Table {x}" for x in TAB_RE.findall(body)]
        ))
        q["stem"] = " ".join(q["lines"][:2])[:180]

    # 去重后的图表清单
    seen, figs = set(), []
    for f in figures:
        if f["label"] in seen:
            continue
        seen.add(f["label"])
        figs.append(f)

    return {"pages": pages, "questions": questions, "figures": figs,
            "total_marks": sum(q["marks"] for q in questions)}


MS_HEAD_RE = re.compile(r"^\s*Question\s*$|^\s*Answer\s*$")
QREF_RE = re.compile(r"^\s*(\d{1,2})(\([a-z]\))?(\((?:[ivx]{1,4})\))?\s*$")


MS_COLS = ("Question", "Answer", "Marks", "Guidance")
INT_RE = re.compile(r"^\s*(\d{1,2})\s*$")
QCOL_MAX = 120.0          # qref 在 74–82，answer 从 127 起，120 是干净的分界


def _ms_table_rules(doc: fitz.Document, start: int):
    """表格画出来的整列分隔线（2026 卷才画全 4 栏）。"""
    best, seen = None, Counter()
    for i in range(start, len(doc)):
        p = doc[i]
        rot, R = p.rotation % 360, p.rect
        uh = R.width if rot in (90, 270) else R.height
        out = []
        for d in p.get_drawings():
            r = d["rect"]
            if rot in (90, 270):
                if r.width > R.width * 0.25 and r.height < 3:
                    out.append(round(uh - r.y1))
            elif r.height > R.height * 0.25 and r.width < 3:
                out.append(round(r.x0))
        out = tuple(sorted(set(out)))
        if len(out) >= 5:
            seen[out] += 1
    if seen:
        best = list(seen.most_common(1)[0][0])
    return best


def _ms_marks_col(doc: fitz.Document, start: int) -> float | None:
    """Marks 栏：整份卷里孤立小整数的众数列坐标。"""
    c = Counter()
    for i in range(start, len(doc)):
        for _, col, t in page_rows(doc[i], pageno=i + 1):
            if INT_RE.match(t) and col > QCOL_MAX + 150:
                c[round(col / 5) * 5] += 1
    return float(c.most_common(1)[0][0]) if c else None


def extract_ms(path: str) -> dict:
    """MS：找到 Question/Answer/Marks/Guidance 表头后，按 qref 分行、按栏坐标分列。"""
    doc = fitz.open(path)
    start = 0
    for i, page in enumerate(doc):
        t = page.get_text()
        # 正式答案表的表头；有的年份 Guidance 栏在首页是空的
        if "Question" in t and "Answer" in t and "Marks" in t:
            start = i
            break

    rules = _ms_table_rules(doc, start)
    mcol = _ms_marks_col(doc, start)
    if rules and len(rules) >= 5:            # 2026：Q | Answer | Marks | Guidance
        m_lo, m_hi = rules[2], rules[3]
    elif mcol is not None:                   # 2024/2025：Q | Answer | Marks
        m_lo, m_hi = mcol - 30, mcol + 60
    else:
        m_lo = m_hi = float("inf")
    ncols = 4 if (rules and len(rules) >= 5) else 3

    def classify(col: float) -> str:
        if col < QCOL_MAX:
            return "Question"
        if m_lo <= col <= m_hi:
            return "Marks"
        if col > m_hi:
            return "Guidance"
        return "Answer"

    rows, cur = [], None
    for i in range(start, len(doc)):
        for _, col, ln in page_rows(doc[i], pageno=i + 1):
            s = ln.strip()
            if s in MS_COLS:
                continue
            name = classify(col)
            if name == "Question":
                if QREF_RE.match(s):
                    if cur:
                        rows.append(cur)
                    cur = {"qref": s, "page": i + 1,
                           "answer": [], "marks": [], "guidance": []}
                    continue
                name = "Answer"          # 顶左但不是题号 → 别丢，算答案
            if cur is None:
                continue
            if name == "Marks":
                # 2026 常把 marks 数字和 guidance 首行黏成一行
                m = re.match(r"^(\d{1,2})\s+(.*)$", s)
                if m:
                    cur["marks"].append(m.group(1))
                    cur["guidance"].append(m.group(2))
                else:
                    cur["marks"].append(s)
            else:
                cur[name.lower()].append(s)
    if cur:
        rows.append(cur)

    for r in rows:
        digits = [x for x in r["marks"] if x.isdigit()]
        r["marks"] = int(digits[0]) if digits else None
    return {"start_page": start + 1, "n_columns": ncols, "rows": rows}


# ---------------------------------------------------------------- 驱动


def run(key: str) -> dict:
    sess, var = key.split("_")[1], key.split("_")[2]
    qp = os.path.join(PDFDIR, f"9701_{sess}_qp_{var}.pdf")
    ms = os.path.join(PDFDIR, f"9701_{sess}_ms_{var}.pdf")
    data = {
        "paper": key,
        "code": f"9701/{var}",
        "session": f"{SESSION_NAME[sess[0]]} 20{sess[1:]}",
        "same_as_v3": key in DUP_OF_V3,
        "qp_pdf": os.path.relpath(qp, ROOT).replace("\\", "/"),
        "ms_pdf": os.path.relpath(ms, ROOT).replace("\\", "/"),
    }
    data.update(extract_qp(qp))
    data["ms"] = extract_ms(ms)

    # 分值对账：QP 的 [n] 是权威（16/16 卷都恰好 60 分）；
    # MS 栏的数字只作交叉校验，跨页/合并单元格时会少算。
    ms_by_q = {}
    for r in data["ms"]["rows"]:
        m = re.match(r"(\d+)", r["qref"])
        if m and r["marks"]:
            ms_by_q[int(m.group(1))] = ms_by_q.get(int(m.group(1)), 0) + r["marks"]
    data["marks_check"] = {
        "authoritative": "qp",
        "qp_total": data["total_marks"],
        "ms_total": sum(ms_by_q.values()),
        "per_question": {str(q["n"]): {"qp": q["marks"], "ms": ms_by_q.get(q["n"], 0)}
                         for q in data["questions"]},
        "agree": all(q["marks"] == ms_by_q.get(q["n"], 0) for q in data["questions"]),
    }
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, key + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return data


def selftest():
    """上下标还原自检：这些压平形态在产物里必须一个都不剩。"""
    doc = fitz.open(os.path.join(PDFDIR, "9701_s26_qp_21.pdf"))
    txt = "\n".join(page_lines(doc[1]))
    want = ["SF₆", "3s² 3p⁴", "3s² 3p⁵", "kJ mol⁻¹"]
    bad = ["SF6", "3s2", "3p4", "mol–1", "mol-1"]
    ok = True
    for w in want:
        hit = w in txt
        ok &= hit
        print(f"  {'ok  ' if hit else 'FAIL'} 应出现  {w}")
    for b in bad:
        hit = b in txt
        ok &= not hit
        print(f"  {'ok  ' if not hit else 'FAIL'} 不应出现 {b}")
    return ok


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--selftest":
        sys.exit(0 if selftest() else 1)
    keys = PAPERS if args[0] == "--all" else args
    for k in keys:
        d = run(k)
        print(f"{k}: {len(d['questions'])} 大题, {d['total_marks']} 分, "
              f"{len(d['figures'])} 图表, MS {len(d['ms']['rows'])} 行")
