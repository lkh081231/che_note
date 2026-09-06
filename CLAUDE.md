# CLAUDE.md

Chemistry notes for Cambridge International AS & A Level Chemistry 9701 (2025 / 2026 / 2027).

## Source of truth

`reference.md` is the reference for **all** notes in this vault. Base every
answer, summary, and new note on it.

Fall back to `reference.pdf` only when the `.md` is unclear, looks wrong, or is
missing something — then fix the `.md` so the next lookup does not need the PDF.

The `.md` is a full transcription of the PDF's Subject content (syllabus p.16–55) plus the
Periodic Table (p.91): 37 chapters, 90 subsections, 538 learning outcomes, all verified against
the PDF.

### Deliberate differences from the PDF

Do not "restore" these when editing:

- Page furniture (running headers, footers, page numbers, "Back to contents page") is removed;
  navigation is a Contents list at the top plus `[↑ Contents](#contents)` at each chapter end.
- The `Learning outcomes` heading is collapsed to the italic line `*Candidates should be able to:*`.
- Page cross-references are rewritten as document-relative ones
  ("the table on pages 29 and 30" → "the table above").
- The two functional-group tables are HTML tables; their structural / displayed / skeletal
  formulas are ChemFig drawings in ` ```tikz ` blocks, not the PDF's images.
- The Periodic Table is rebuilt as an 18-column Markdown table with lanthanoids and actinoids
  as separate rows below.

Note the PDF's own text layer is unreliable: its `ffi` ligature extracts as `)`
(`di)culty`, `coe)cient`, `a)nity`), and `l` in `Cl` / `Al` is a separate italic glyph. When
checking against the PDF, read the rendered page, not the extracted text.

## Carbon numbering

**Always use IUPAC numbering when saying which carbon.** Number the parent chain so the
principal characteristic group — or, failing that, the first point of difference — gets the
lowest locant, and say "C3" / "the third carbon" accordingly.

Example: in propene (prop-1-ene) C1 is the terminal `=CH₂`, C2 is the `=CH–`, and C3 is the
`CH₃`. Never number by position in the drawing, in the ChemFig source, or left-to-right on the
page.

## Notation in the notes

- Chemical formulas use Unicode sub/superscripts: `H₂SO₄`, `SO₄²⁻`, `NH₄⁺`, `sp³`, `¹H`.
- Physical quantities with a single letter script use `<sub>`: `*K*<sub>c</sub>`, `*E*<sub>A</sub>`.
  Unicode subscripts are used where the letter exists (`*A*ᵣ`, `*K*ₚ`, `*K*ₐ`, `Δ*H*ₙₑᵤₜ`) —
  Unicode has no subscript `b c d f g q w y z` or capitals.
- Anything carrying **two** scripts at once uses inline LaTeX `$…$`, not HTML:
  `$E^{\ominus}_{\text{cell}}$`, `$\Delta H^{\ominus}_{\text{sol}}$`, `$^{x}_{y}\text{A}$`,
  `$3\text{d}_{z^2}$`. Use `$…$`, never `$$…$$` — block math breaks the sentence and looks
  wrong in screenshots.
- Standard-state symbol is `\ominus` in LaTeX, `⦵` in plain text.
- Write `Cl`, `AlCl₃`, `PCl₅` with a normal `l`.

## Rendering target

The notes are read and screenshotted in the **VS Code Markdown preview**, which renders both
KaTeX (`$…$`) and ` ```tikz ` blocks with ChemFig. Obsidian is not the target — check rendering
in VS Code's preview.

ChemFig blocks must carry their own preamble:

````
```tikz
\usepackage{chemfig}
\begin{document}
\chemfig{...}
\end{document}
```
````

To put a drawing inside an HTML table cell, leave a blank line after `<td>` and before `</td>`
— otherwise the fenced block is not parsed:

```html
<td>

```tikz
...
```

</td>
```

Draw sp² centres with 120° geometry (`[:30]` / `[:-30]` / `[:60]` …) and keep C=C horizontal at
`[:0]`. sp³ carbons are drawn as an upright cross (`[:90]` / `[:180]` / `[:270]`), matching the
syllabus.

### 改完 diagram 一定要截图检查

每次调整完 ```tikz 图，都用 screenshot-feedback-hook-mcp 的 **CLI** 截 VS Code preview 看一眼
（不要装它的 MCP server，仓库 https://github.com/lkh081231/screenshot-feedback-hook-mcp）：

```bash
uvx screenshot-feedback-hook-mcp monitors                       # 列出显示器
uvx screenshot-feedback-hook-mcp capture --monitor 0 --out shot.jpg
```

`--monitor 0` 是所有屏拼接，单屏用 1..N（preview 通常在第 2 屏，`--monitor 2` 看得清）；
还有 `--delay`（等渲染）、`--max-edge`、`--target-kb`。截完用 Read 读图，确认 label 不重叠、
引线指对位置、公式没乱码。

已知渲染坑（tikz 块是 TikZJax，不是完整 LaTeX）：

- 数学符号 `\approx`、`\times` 和上标里的负号会渲染成乱码（¼ £ i）。tikz 里只用字母、数字和
  text mode；数值直接写十进制，例如 `0.0000034 nm`，别写 `3.4 \times 10^{-6}`。
  （正文的 `$…$` 走 KaTeX，不受此限。）
- node 选项里裸写颜色（`blue!70`）等于 `color=`，会连 `fill=white` 一起盖成实心色块；
  只想改文字颜色必须写 `text=blue!70`。


## HTML 交付物（organic-reaction-roadmap.html）

`organic-reaction-roadmap.html` 是**单文件零依赖**的有机反应路线图，同时发布为 Claude
Artifact（同一 file path 重新发布即原地更新，链接不变）。内容口径：reagent / condition 逐字取自
syllabus 章 13–21，判分口径与机理得分点取自 `passyear/extracted/` 的 2024–2026 Paper 2
mark scheme，**冲突时以最新卷 `9701_s26_22` 为准**。

### 改完必须两级截图，不能只跑脚本

无头 Chrome 截图（stderr 的 `fallback_task_provider` 是已知噪声，以 `N bytes written` 为准）：

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless --disable-gpu --hide-scrollbars   --screenshot=out.png --window-size=1900,1200   "file:///C:/che_note/organic-reaction-roadmap.html"
```

- **布局级**（整页）：看重叠、错位、结构
- **细节级**（`z>=1.5` 拍局部）：看箭头、虚线、δ± 角标、曲箭头起止点、字号

**两级缺一不可。** 实测教训：5.5px 的箭头在 Fit 缩放（~0.65）下只剩 3px，
整页截图里「有箭头」和「没箭头」根本分辨不出——曾因此让 35 条线全部没有箭头的
bug 通过了一整轮几何校验和视觉检查。

**交互态用 playwright MCP 实拍**，并且**一定要看 console**：
筛选/缩放失效两次都是 JS 抛错导致整个 script 中断，无头截图完全看不出来
（`file:` 协议被 playwright 拦，先 `python -m http.server` 起个本地服务）。

### 已知渲染坑

- `svg.wires path{fill:none}` 会把 `<marker>` 里的箭头三角形一起填透明。
  必须写成 `svg.wires > g path{...}`，并补 `svg.wires marker path{stroke:none;}`
- **`marker-end` 必须写在每条 `<path>` 上**，写在 `<g>` 上不会被子元素继承
- 箭头端点要比方框边缘**提前 ~9px** 收尾，否则会被 `z-index` 更高的方框盖住
- 不透明标签会盖住从它底下穿过的连线，看起来像断线 —— 校验脚本要同时查
  「线穿 node 框」和「线穿 label 框」，只查 node 会漏掉一大批
- `<script>` 必须放在弹窗 / `<template>` 等 DOM 之后，否则 `getElementById` 拿到 null

## Commit 节奏

**完成一个阶段就 commit**，不要攒着一次性提交。commit message 用中文，
说清这一阶段做了什么、以及踩到的坑（后者对下次最有用）。

## Language

In notes, prose may be 中文, but **every chemistry term stays in English**. Do not translate:

- element, compound and reagent names — sodium hydroxide, potassium manganate(VII), phenol
- functional groups and homologous series — carbonyl, hydroxyl, halogenoalkane, ester
- reaction and mechanism names — nucleophilic substitution, electrophilic addition,
  free-radical substitution, disproportionation, S<sub>N</sub>1 / S<sub>N</sub>2
- physical-chemistry quantities and concepts — lattice energy, enthalpy change of hydration,
  activation energy, Boltzmann distribution, dynamic equilibrium, standard electrode potential
- technique and apparatus names — thin-layer chromatography, mass spectrometry, reflux, titration
- wording quoted from a learning outcome — quote it verbatim in English

So: 「propan-1-ol 在 acidified K₂Cr₂O₇ under reflux 会被 oxidise 成 propanoic acid」, not
「丙-1-醇在酸化重铬酸钾下回流会被氧化成丙酸」.

Formulas, `$…$` notation and ChemFig source are unaffected — they are always as specified above.

`reference.md` itself is the exception: it is a verbatim transcription of an
English PDF and stays 100% English, with no Chinese at all.

Chat replies stay in 中文.
