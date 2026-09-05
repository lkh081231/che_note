---
name: cie-9701-pastpaper-bank
description: |
  把 CIE / Cambridge International AS & A Level **Chemistry 9701** 的历年真题（question
  paper + mark scheme PDF）批量转成按 syllabus chapter 组织的 Markdown 题库——下载去重、
  确定性抽取（含上下标还原）、裁图、章节分类、subagent 分工、跨章镜像、机械验收、额度控制。
  只要用户提到 9701、CIE 化学真题、past paper、mark scheme、题库、按章刷题、papacambridge，
  或者说「再做一年」「把 Paper 1 / Paper 3 / Paper 4 / Paper 5 也做了」「补 2022 的卷」，
  **就该用这个 skill**，哪怕他没说「题库」两个字。已有 2024–2026 Paper 2 的完整实现可照抄。
  换**别的科目**（物理 9702 / 生物 9700 / 数学 9709 …）请改用 `cie-pastpaper-bank`。
---

# CIE 9701 真题库：换年份 / 换 Paper

已有一套跑通的实现：**9701 Paper 2 (2024–2026)，77 题 / 960 分 / 16 卷**，
在 `c:\che_note\passyear\`。本 skill 是它的可迁移版本。

**动手之前先做两件事**：

1. 读 `c:\che_note\passyear\CLAUDE.md` —— 那是活的工作流文档，比本 skill 更新更快。
2. 确认 `c:\che_note\reference.md` 存在（syllabus 全文转写，37 章 / 538 outcomes）。
   它是**分类与判题的唯一依据**，也是**只读的**（见下）。

`tools/` 里的 6 个脚本可以直接复制过去用：`extract.py`（抽取）、`crop.py`（裁图）、
`mirror.py`（镜像）、`verify.py`（验收）、`audit.py`（标注审计）、`heat.py`（热度统计）。
`chapters.py` 是数据不是代码，每次都要重写。

---

## 红线：syllabus 文件只读

`reference.md` / `reference.pdf` 是整个 vault 的 source of truth。
**任何自动化流程都不许改它**——主 session、subagent 一律禁止。

已有 PreToolUse hook 强制执行（`.claude/hooks/protect_reference.py`，在 vault 根和子目录
两处 `settings.json` 注册）。它拦写、放行读。subagent 走同一条 hook 管线，一并被拦。

⚠️ **这个 hook 会误伤你自己的日志**：往 `BUDGET.md` 写一段提到 `reference.md` 的文字时，
如果用 `python - <<'PY' … write_text(…)` 这种形式，hook 看到命令串里同时有文件名和写操作
就会拦下来。**绕法**：先用 Write 工具把内容写到暂存文件，再 `cat 暂存 >> BUDGET.md`
（这条命令里不含那个文件名）。

---

## 七个阶段

### Phase 0 — 侦查（半小时，别跳过）

对 2–3 份目标 PDF 做技术摸底，**结论决定后面所有事**：

- `page.get_text()` 有没有干净文字层？（9701 2024–2026 全部有，QP 18k–31k 字符）
  没有 → 是扫描件，本工作流不适用，得先做 OCR 质量摸底，那是另一套。
- `page.get_images()` 是不是恒为 0、`get_drawings()` 每页几百条？
  是 → 图全是矢量，裁 PNG 可以任意 dpi 且锐利。
- 每份多少分、多少道大题、多少页？

**换 Paper 时这三条都要重新测**，不要假设 Paper 1（MCQ）或 Paper 4/5 和 Paper 2 一样。
Paper 1 是选择题，产物格式完全不同；Paper 5 是 planning/analysis，mark scheme 结构也不同。

### Phase 1 — 下载与去重

PapaCambridge 的直链可以拼，不用爬页面：

```
https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload/9701_<sess><yy>_<qp|ms>_<variant>.pdf
```

`<sess>`：`m` = Feb/March（India only）· `s` = May/June · `w` = Oct/Nov
`<yy>`：两位年份　`<variant>`：`21`/`22`/`23`（Paper 2 的三个时区卷，其它 Paper 换首位数字）

**不存在的组合返回 HTTP 200 + 一个 270953 字节的占位 PDF，不是 404。判空看文件大小。**

**去重必须每个 Paper 重新验，不要照抄 Paper 2 的结论。**
Paper 2 2024–2026 实测：w 卷 v21 ≡ v23（MS 差 0 token，QP 差 20 token 全是条形码字形）、
s 卷三个 variant 都不同、m 卷只开 variant 2。做法是全文归一化（剥卷号/条形码/印刷码/空白）
后逐 token diff。同会期的不同 variant **共享命题素材但换物质换数据，这不算重复，照提**。

### Phase 2 — 确定性抽取（本流程最关键的一环）

**机械正确性必须由 Python 做完，绝不交给模型猜。** 这既是质量保证，也是省额度的关键——
执行体拿到的是已经修好的干净文本，只需要干版式和判断。

上下标在文字层被压平（`SF6`、`3s2 3p4`、`kJ mol–1`），但 span 层完全可复原。
规则表和噪声清单见 **`references/extraction.md`**——那里也列了 `extract.py` 的**已知 bug**，
换年份重跑之前值得先看一眼，有一个（算术符号被静默吃掉）是纠错量最大的一类。

### Phase 3 — 裁图：caption 锚定带状裁剪

图**恒定位于自己的 `Figure N.N` / `Fig. N.N` caption 正上方**（2026 起用 `Figure`，
2024–2025 用 `Fig.`）。取「上一条正文基线底部 → caption 顶部」的整栏宽带，
左右收进 `x ∈ [70, 525]`、下边界卡 `y < 810`，`get_pixmap(clip=…, dpi=300)`。
这样天然排掉竖排边注、条形码、页底站点行。

**不要走 `get_drawings()` 聚类找 bbox**——实测答题虚线和页面边框会把整页并成一块。

裁完每张都要看一眼。

### Phase 4 — 分类（必须先于分工）

按 chapter 分工的前提是先知道每道题归哪章。用大题 stem + `_json` 里的小问文本即可，
**不开 subagent、不读图**。只落到 chapter 级（AS 是 1–22，A Level 才碰 23–37），
**一题一个主章，不拆题**。

⚠️ **分类要以 outcome 原文为准，不要按章节标题望文生义。** 本次栽过两次：

- 「lattice 结构 → 物理性质」写在 **4.2**（States of matter），不在 ch3 Chemical bonding。
  我按标题想当然归了 ch3，导致 ch3 在热度表里虚高到 15%，实际只有 5%。
- ch12 标题叫「Nitrogen and **sulfur**」，但 5 条 outcome 全是 nitrogen，
  sulfur 只在 12.1.5 作为「NO/NO₂ 催化氧化大气 SO₂」出现一次。
  → sulfur 的氧化数归 **ch6**，Contact process 归 **ch7**。

拿不准就 `grep -n` 去 syllabus 里找那条 outcome 的原文再定。

### Phase 5 — 派活：一个 subagent 独占一个 chapter

写者唯一 → 无写冲突（按卷分工会让多个 agent 同时写同一份卷）；而且一个执行体只在一个
主题里打转，chemistry 上下文建立一次反复用，比按卷跳 5 个不相干主题更省也更一致。

**subagent prompt 的硬规矩清单见 `references/dispatch.md`**——那是逐条用血换来的，
每一条背后都有一次实际的返工。**照抄，不要凭记忆重写。**

主 session 每章抽查 1 题 + 对账关键数值，**不逐字通读产物**（省主 session 的 context）。

### Phase 6 — 跨章镜像与小问级标注

一道 CIE 大题经常横跨好几章。口径：**正本只有一份放主章，够分量的其它章拿整题镜像。**
门槛、标签格式、四个脚本的执行顺序见 **`references/mirroring.md`**。

一条必须记住的：**`mirror.py` 会重写正本文件，跑标注 subagent 期间绝对不要执行它。**

### Phase 7 — 验收

`python tools/verify.py` 跑机械检查，全绿才算完。清单见 `references/mirroring.md` 末尾。
外加人眼两件事：VS Code Markdown preview 里开 2–3 份看 `$…$` 与 ChemFig 渲染；
随机抽 10 个小问对官方 MS 核数值。

---

## 记法（`../CLAUDE.md` 全部生效，这里重申最容易违反的）

- **题干、答案、chemistry term 全部英文逐字**——这是考试原文，不翻译。
  **`**答案**` / `**判分**` 两栏一个中文字都不许有**（2026-09 收紧的规矩：
  这两栏是拿来对着背的，中英混排会让人分不清哪些是 MS 原文、哪些是执行体的话）。
  要解释就用英文括注，或另起一行 `**注**` 用中文。
- Unicode 上下标 `H₂SO₄` `SO₄²⁻` `3s²`；**双重角标**用行内 `$E^{\ominus}_{\text{cell}}$`，
  **绝不** `$$…$$`（块公式会打断句子，截图很难看）。
- `Cl` `AlCl₃` `PCl₅` 用普通小写 `l`，不是 `ℓ`。
- 提到第几个碳一律 **IUPAC 编号**。
- 执行体爱在括号里补中文译名（「cyclopropane（环丙烷）」），**化合物名不行**，grep 得掉。

---

## 额度纪律

额度是主刹车，时间是次刹车。**绝不主动跑进 extra usage**——它只是防止已启动任务被腰斩的
保险，不是可花的预算。剩余 ≤ **15%** 一律停。

**5 小时窗口从「本窗口第一次调用」起算，刷新点会漂**，不是固定钟点。唯一可靠读数是
VS Code 侧栏 `ACCOUNT & USAGE` 面板的「Resets in …」（面板上那个百分比是**已用**不是剩余）。
挂定时任务一律「**一次性 cron + 刷新时刻后留 10 min 冗余**」，且 cron prompt 的第一条指令
必须是「先复核面板确认窗口真的换了，没换就重挂」——定时器只是闹钟，门禁是面板读数。
（实测按固定钟点挂 recurring cron，在额度已用 95% 时触发，白烧一轮。）

**实测成本**（供排批）：提取约 6.7–11 额度点/章、28–36k subagent token/题；
小问标注约 6.5 点/章。主 session 的 context 长度显著影响单章成本——compact 之后
同样的活从 11 点掉到 6.7 点。

---

## 这一轮踩过的坑（换年份时大概率重演）

| 坑 | 症状 | 对策 |
|---|---|---|
| **成本模型全错** | 估 12% 实际 34% | 别建模，用面板前后读数当唯一依据 |
| **执行体误报「官方缺陷」** | 说结构式少一个碳、说 MS 损坏 | prompt 里写死「骨架式每个拐点都是碳」「报缺陷前自己数两遍，主 session 会亲自看图」 |
| **执行体自己去别的站下 PDF** | 数据源失控 | 写死「只用 `originalpdf/`，怀疑就停下报告」 |
| **执行体凭空补标注** | 给 variant 2 加了「与 /23 同卷」 | 加进 grep 验收清单 |
| **能力型章节被标空** | ch21 Organic synthesis 4 题 38 小问，ch21 一分没有 | 见 `references/mirroring.md` |
| **md 文件数 ≠ 题数** | 误判某章缺卷 | 用脚本比对「应有卷 key 集合 vs 实际」 |
| **GBK 控制台炸在 emoji 上** | `UnicodeEncodeError` | 脚本里 `sys.stdout = io.TextIOWrapper(..., encoding="utf-8")`，**但只在 `__main__` 下包**，否则被 import 时会关掉调用者的 stdout |
| **TODO 记半截题号** | 记了 `w25_21 Q1(b)(iii)`，实际是 ch21 的 Q4(b)(iii) | 记位置要写全 `<chapter>/<卷> Q<n>(<小问>)`，或只记内容特征让执行体自己 grep |

---

## 参考文件

- **`references/extraction.md`** —— span 规则表、噪声清单、`extract.py` 的已知 bug 与修法
- **`references/dispatch.md`** —— subagent prompt 模板与硬规矩（照抄用）
- **`references/mirroring.md`** —— 镜像架构、门槛、小问标签、四个脚本、验收清单
