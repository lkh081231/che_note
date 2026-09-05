# 七个阶段的详细机制

参考实现在 `c:\che_note\passyear\`（Chemistry 9701 Paper 2, 2024–2026）。
`tools/` 里的脚本可以复制过去改：`extract.py` `crop.py` `mirror.py` `verify.py`
`audit.py` `heat.py`（`chapters.py` 是数据不是代码，每个科目都要重写）。

`extract.py` 和 `crop.py` 处理的是 **CIE 的 PDF 排版**，不是化学——大部分逻辑对别的科目
同样成立，值得先复制再按侦查结果调参数。`mirror.py` / `verify.py` / `audit.py` / `heat.py`
是纯组织逻辑，跟科目无关，基本可以直接用。

---

## Phase 0 · 侦查

对 2–3 份目标 PDF：

```python
page.get_text()          # 有没有干净文字层？字符数量级？
page.get_images()        # 恒为 0 → 图全是矢量
page.get_drawings()      # 每页几百条 → 同上
```

同时记下：每份满分、大题数、页数、mark scheme 的结构与「正式答案从第几页开始」。

**换 Paper 要重测。** 同一科的 Paper 1（多半是 MCQ）、Paper 2（结构题）、
Paper 4（A Level 结构题）、Paper 5（planning & analysis）产物格式完全不同。
MCQ 卷的「题库」形态应该是「题干 + 四个选项 + 正确答案 + 为什么其它三个错」，
跟结构题不是一回事。

## Phase 1 · 下载与去重

PapaCambridge 直链可以拼，不用爬页面：

```
https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload/<syllabus>_<sess><yy>_<qp|ms>_<variant>.pdf
```

`<sess>`：`m` = Feb/March（India only）· `s` = May/June · `w` = Oct/Nov
`<variant>`：`11`/`12`/`13`（Paper 1）、`21`/`22`/`23`（Paper 2）…… 首位是 Paper 号

**不存在的组合返回 HTTP 200 + 一个固定大小的占位 PDF，不是 404。判空看文件大小。**

### 去重必须自己验，不能照抄别科的结论

做法：全文归一化（剥卷号 / 条形码 / 印刷码 / 空白）后逐 token diff。

化学 P2 2024–2026 的结论是：w 卷 v1 ≡ v3（MS 差 0 token）、s 卷三个 variant 都不同、
m 卷只开 variant 2 → 18 份卷去重后 16 份唯一。**别的科目、别的 Paper、别的年份都可能不同。**

注意：同会期不同 variant **共享命题素材但换物质换数据**，这不算重复，照提。

## Phase 2 · 确定性抽取

**这一步必须由 Python 完成，绝不交给模型猜。**

CIE 的 PDF 文字层会把上下标压平（`SO42-`、`3s2`、`kJ mol–1`），但 span 层完全可复原。
化学卷实测（换年份/换科目要重验，CIE 换排版工具就会变）：

| 类型 | `size` | `flags` | `origin.y` 相对正文 |
|---|---|---|---|
| 正文 | 11.0 | 4 | — |
| 下标 | 8.25 | 4 | +3.9 |
| 上标 | 8.25 | 5（bit0 = superscript） | −3.8 |

验法：拿一页含已知上下标的页面，打印所有 span 的这三个字段，看聚类是否还是三类。

### 要剥掉的噪声（各科通用）

页眉页脚（`<syllabus>/<variant>/<sess>/<yy>`、`© Cambridge …`、`Page n of m`）、
页底站点行（固定几行，在固定 y 带）、`DO NOT WRITE IN THIS MARGIN` 竖排边注、
条形码乱码行（非 ASCII 且不在符号白名单的连续串）。

> 🐛 **注意这个白名单别写太窄。** 化学那版把 `>` `<` `≥` `×` `°` 全滤掉了：
> `104.5()` 实为 `104.5°`、`(28.40 / 1000  0.0005)` 中间掉了 `×`。
> 计算量大的科目（物理、数学、经济）中招会更严重。**建库前先把这几个字符加进白名单。**

### 切题

按行首题号 + `x0` 阈值切大题，按 `(a)` `(i)` 切小问，保留 `[n]` 分值。
MS 侧跳过前几页的通用 marking principles，从表头页开始按栏切。

### 输出 QP vs MS 的分值对账表

每份卷输出一个 `marks_check`。**三类差异含义完全不同**：

| 形态 | 含义 |
|---|---|
| 某题 `ms: 0` | **MS 整段缺失**，真红旗，派活前要警告执行体 |
| 差额 = 某被撤销小问的分值 | 官方撤题，不是缺陷 |
| 零散小差额 | MS 解析漏抓，不影响产物 |

化学那次 `s24_22` Q5 的 `ms: 0` 信号一直躺在 json 里没人看，
结果执行体自己发现后判成「文件损坏」跑去别的站下替代文件。

## Phase 3 · 裁图：caption 锚定带状裁剪

图**恒定位于自己的 `Figure N.N` / `Fig. N.N` caption 正上方**
（CIE 2026 起用 `Figure`，之前用 `Fig.`；别的科目可能是 `Table` / `Source` / `Extract`）。

取「上一条正文基线底部 → caption 顶部」的整栏宽带，左右收进正文栏、下边界卡在页底站点行以上，
`get_pixmap(clip=…, dpi=300)`。这样天然排掉竖排边注、条形码、页底站点行。

**不要走 `get_drawings()` 聚类找 bbox**——实测答题虚线和页面边框会把整页并成一块。

另外提供一个 `render(pdf, pages, dpi=170)` 出整页 PNG，**只给含图/含公式的页用**，
控制 image token。

裁完每张都要看一眼。

## Phase 4 · 分类（必须先于分工）

按 chapter 分工的前提是先知道每道题归哪章。用大题 stem + 抽好的小问文本即可，
**不开 subagent、不读图**——这一步很便宜，别浪费额度。

规矩：只落 chapter 级（不到 subsection）· **一题一个主章** · 跨章的标出来 · **不拆题**。

**按 outcome 原文定章，不按章节标题望文生义**（见 SKILL.md 第 3 条）。

产物是一张 `classification.md`：大题 → chapter 总表 + 各章清单（= 分工单）。

## Phase 5 · 派活

**一个 subagent 独占一个 chapter 文件夹。** prompt 的硬规矩清单见 `pitfalls.md`，
每条背后都有一次实际返工，**照抄不要凭记忆重写**。

只给本章上下文：本章在 `classification.md` 里的行 + 对应卷的抽取中间态片段 +
已裁好的图 + 含图页的 170dpi PNG + 样板 md 路径。
**不塞整份分类全表，不传整卷高 dpi 渲染。**

要求完成报告**只回三行**（做了什么 / 新发现 / 拿不准的）——长报告浪费主 session 的 context。

## Phase 6 · 跨章镜像与小问级标注

实测 77 题里 **43 题跨章**，一道 19 分的题能压到 9 个章。按章刷题的人不希望
「这题主章是 A 所以在 B 文件夹里看不到」。

**小问标签**（只标跨章题的、只标带 `[n]` 分值的小问）：

```markdown
### (b)(iii) [3] · ch9
### (c) [4] · ch16 ch17        ← 真两边都占分才双标
```

格式写死成「空格 + `·` + 空格 + `chN`」，为的是能 grep。

**镜像门槛：≥2 分 且 ≥15% 题分。** 只卡绝对分会爆炸（43 题外推出 108 个镜像）。
够不上门槛但确实考到的，在该章 README 里列一条「零星考点」指路。

**执行顺序不能错**：`mirror.py` → `verify.py` → `audit.py` → `heat.py`。

- ⚠️ **`mirror.py` 会重写正本文件，跑标注 subagent 期间绝对不要执行它**（会和 Edit 撞车）
- `mirror.py --check` 是 dry-run，**删文件前先跑它看清单**
- `audit.py` 专门抓 `mirror.py` 和 `verify.py` 都看不见的问题：
  **主章在自己题里占 0 分**（要么执行体漏标了「能力型」章节，要么当初分类判错了）

## Phase 7 · 验收

全部做成 grep 能跑的机械检查，每批收工必跑：

1. 上下标未还原的特征串零命中
2. `ℓ` / `$$` / 临时目录路径 / HTML 实体零命中
3. 只该出现在特定文件的标注，确实只在那些文件里
4. 不该有的语言混入零命中（如「答案栏出现中文」）
5. 每个图片链接都指向存在文件
6. 每道大题恰好落在一个 chapter 文件夹；**同一卷跨各章的 `[n]` 求和 = 卷面满分**
7. 镜像块不计分（否则总分翻倍）
8. `git status` 里 syllabus 文件恒为 clean

人眼补两条：Markdown preview 里看公式渲染；随机抽 10 个小问对 MS 核数值。
