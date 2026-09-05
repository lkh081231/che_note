# passyear/ — CIE 9701 Paper 2 真题提取工作流

本目录存放 Cambridge International AS & A Level Chemistry **9701 Paper 2**（AS Structured
Questions）的历年真题 PDF，以及从中提取的题目-答案 Markdown。

本文件记录**可复用的提取工作流**：一次摸清，换年份 / 换 Paper 照此执行即可。

上级 `../CLAUDE.md` 的所有记法与语言规则在本目录**全部适用**，本文件只补充增量约定。

---

## 绝对红线：`../reference.md` 只读

`reference.md` / `reference.pdf` 是整个 vault 的 source of truth。**任何自动化流程都不许改它**
——主 session、subagent、codex 一律禁止。

已装 PreToolUse hook 强制执行：

- 脚本 `../.claude/hooks/protect_reference.py`
- 注册于 `../.claude/settings.json` 和 `./.claude/settings.json` 两处（哪个目录开 session 都拦得住）
- 拦 `Edit` / `Write` / `NotebookEdit` / `MultiEdit` 指向这两个文件的写入
- 拦 `Bash` / `PowerShell` 里 `reference.(md|pdf)` 与写操作同现的命令
  （`>` `>>` `tee` `sed -i` `mv` `cp` `rm` `truncate` `Set-Content` `Out-File` `git checkout` `open(...,'w')`）
- **读一律放行**：`cat` / `head` / `sed -n` / `grep` / `Read` 都可以直接用
- subagent 的工具调用走同一条 hook 管线，所以 subagent 一并被拦

需要改 `reference.md` 时**由人手动编辑**，不要绕过 hook。

---

## 目录约定

```
passyear/
├── CLAUDE.md              本文件
├── .claude/settings.json  reference.md 保护 hook
├── originalpdf/           36 份 CIE 原始 PDF（18 QP + 18 MS），只读归档
├── topical-2015-2021/     20 份 PapaCambridge 按章合集，纯扫描件，只存不动
├── tools/                 extract.py / crop.py / mirror.py / verify.py / audit.py / heat.py
├── _json/                 抽取器中间态，喂给 subagent 用
├── classification.md      大题 → chapter 总表 + 章节热度统计
├── BUDGET.md              每批额度用量记录
└── extracted/
    ├── ch03-chemical-bonding/     ← 一个 chapter 一个文件夹
    │   ├── 9701_s26_21.md         ← 该卷属于本章的题
    │   ├── 9701_w25_22.md
    │   └── img/9701_s26_21_fig1-1.png
    ├── ch11-group-17/
    └── …（只建有题的章）
```

`originalpdf/` 和 `topical-2015-2021/` 共 61MB，已 gitignore——PDF 随时可按下面的直链重下。

---

## 数据源与命名

### PapaCambridge 直链

网页 viewer 页里的下载链接指向同一个 upload 目录，**可以直接拼 URL，不用爬页面**：

```
https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload/9701_<sess><yy>_<qp|ms>_<variant>.pdf
```

- `<sess>`：`m` = Feb/March（India only）、`s` = May/June、`w` = Oct/Nov
- `<yy>`：两位年份　`<variant>`：`21` / `22` / `23`（Paper 2 的三个时区卷）
- `qp` = question paper，`ms` = mark scheme

**不存在的组合会返回 HTTP 200 + 一个 270953 字节的占位 PDF**，不是 404。判空看文件大小，
别看状态码。

topical 合集在同一目录，文件名带空格，需 URL 编码：
`Chemistry 9701 Paper 2 - <章节名>.pdf`

### ⚠️ 已知的源站缺陷：`9701_s24_ms_22.pdf` 缺 Q5

这份 MS 只有 13 页、页脚 `Page 13 of 13`、正文止于 4(e)(ii)，**没有 Q5 的 mark scheme**。
从直链重下得到**逐字节相同**的文件 → 不是下载坏了，是源站文件本身就缺。

**不要再去别的站点找替代品**（实测有执行体自行从 pastpapers.co 取了 14 页版，内容虽对但
数据源失控）。口径已定：**归档只放官方那份**，缺失在产物里注明——
见 `extracted/ch22-analytical-techniques/9701_s24_22.md` 的 Q5 题头。

### 原始文件名就是规范名

CIE 官方命名已经统一（`9701_s26_qp_21.pdf`），**不需要像 SPM 那样重命名**，直接用。
输出 md 沿用同一 key：`9701_<sess><yy>_<variant>.md`，图 `img/<同名前缀>_fig<N-N>.png`。

---

## Variant 去重（实测结论，不要重新验证）

对全文归一化（剥卷号 / 条形码 / 印刷码 / 空白）后逐 token diff 得出：

| 会期 | 结论 |
|---|---|
| **Oct/Nov（w 卷）** | **variant 1 ≡ variant 3，同一份卷**。MS 差 0 token，QP 差 20 token 且全是条形码乱码字形 |
| May/June（s 卷） | 21 / 22 / 23 是三份不同的卷，QP 差 2200+ token，**都要提** |
| Feb/March（m 卷） | 只开 variant 2，v1 / v3 的 URL 返回占位 PDF |

→ **2024–2026 共 18 份卷，去重后 16 份唯一**：

```
m24_22  s24_21  s24_22  s24_23  w24_21(≡23)  w24_22
m25_22  s25_21  s25_22  s25_23  w25_21(≡23)  w25_22
m26_22  s26_21  s26_22  s26_23
```

w 卷只提 `_21`，md 顶部注明 `> 本卷与 9701/23 同卷（逐字一致，仅条形码与印刷码不同）`。

s 卷三变体虽是不同卷，但同会期**共享命题素材**（同一个 outcome 换物质换数据，例如 s26 的
21 用 NaCl / NaBr / NaI + 浓 H₂SO₄、22 只用 NaCl / NaBr）——**这不算重复，照提**。

---

## PDF 技术特征（2024–2026 实测）

- **全部有干净文字层**（QP 18k–31k 字符，MS 10k–35k 字符），**不需要 OCR**。
- **图全是矢量**（`get_images()` 恒为 0，`get_drawings()` 每页数百条）→ 裁 PNG 可任意 dpi 且锐利。
- 每份 60 分、4–6 道大题、12–20 页。
- MS 是 4 栏表 `Question / Answer / Marks / Guidance`，前 5–7 页是通用 marking principles，
  正式答案从表头页开始。

### 上下标还原（本流程最关键的一条）

文字层把上下标**压平**了：`SF6`、`3s2 3p4`、`kJ mol–1` 抽出来都是普通字符。
但 span 层面**完全确定可复原**：

| 类型 | size | flags | origin.y 相对正文 |
|---|---|---|---|
| 正文 | 11.0 | 4 | — |
| 下标 | 8.25 | 4 | **+3.9**（下移） |
| 上标 | 8.25 | **5**（bit0 = superscript） | **−3.8**（上移） |

→ 用 `page.get_text("dict")` 逐 span 判型，把数字与 `+ − ( )` 映射到 Unicode
（`₀-₉ ⁰-⁹ ⁺ ⁻`），直接产出 `SF₆` / `3s² 3p⁴` / `kJ mol⁻¹` / `SO₄²⁻`。

**这一步必须由 Python 确定性完成，绝不交给模型猜。** 机械正确性前置做完，
执行体只干版式和判断——这既是质量保证，也是省额度的关键。

### 需要剥掉的噪声

- 页眉页脚：`9701/21/M/J/26`、`© Cambridge University Press & Assessment 2026`、`Page n of m`
- 页底站点行（固定 7 行，位于 QP 的 y ∈ [818, 842] / MS 的 y ∈ [571, 595]，x ∈ [36, 227]）
- `DO NOT WRITE IN THIS MARGIN` 竖排边注（每页重复多次）
- 条形码乱码行（非 ASCII 且不在化学符号白名单的连续串）

### 裁图：caption 锚定带状裁剪

图**恒定位于自己的 `Figure N.N` / `Fig. N.N` caption 正上方**（2026 年起用 `Figure`，
2024–2025 用 `Fig.`）。所以：

1. 找到 caption 的 bbox；
2. 取「上一条正文基线底部」到「caption 顶部」之间的整栏宽带；
3. 左右收进正文栏 `x ∈ [70, 525]`、下边界卡 `y < 810`
   → 天然排掉竖排边注、条形码、页底站点行；
4. `page.get_pixmap(clip=…, dpi=300)`。

**不要走 `get_drawings()` 聚类找 bbox** —— 实测答题虚线和页面边框会把整页并成一块，没用。

裁完**每张都要看一眼**，确认没截断、没夹带。

---

## 提取产物格式

数据表 → Markdown 表；结构式 / 装置图 / 坐标图 / dot-and-cross → 裁 PNG。
答案抄 Answer + Marks 全文，Guidance 精简（只留 A/R/I、ecf、max 等影响判分的，
删同义词罗列和考官流程话术）。

```markdown
# ch03 Chemical bonding · 9701/21 May/June 2026

> 题卷 `originalpdf/9701_s26_qp_21.pdf` ｜ 答案 `originalpdf/9701_s26_ms_21.pdf`

## Q1 [11]  (兼 ch1 Atomic structure)

### (a)(i) [1]
Complete the dot-and-cross diagram in Figure 1.1 …

![Figure 1.1](img/9701_s26_21_fig1-1.png)

**答案** — shared pair 在 S–F 之间，S 周围 6 对 bonding pairs
**判分** — R 画出 lone pair on S
```

格式硬规矩（`../CLAUDE.md` 的规则在此全部生效，重点重申）：

- **题干、答案要点、chemistry term 全部保留英文逐字**——这是考试原文，不翻译。
- **`**答案**` 与 `**判分**` 两栏一律全英文，不许中英混写。** 这是 2026-09-05 收紧的规矩：
  存量产物里有一批答案混进了中文（"见上表 …"、"两端各留一个悬空键" 之类），**存量不改**，
  但**此后新派的 subagent 一律只写英文**。理由是这两栏是拿来对着背、对着默写的，
  混排会让人分不清哪些字是 MS 原文、哪些是执行体的话。
  需要解释的写成英文的括注（`(i.e. …)`）或另起一行 `**注**` 用中文，不要塞进答案里。
- 只有章节标注、`**注**` 旁注、以及本目录的文档（`classification.md` / `BUDGET.md` /
  `QUESTIONS.md` / README）用中文。
- Unicode 上下标：`H₂SO₄`、`SO₄²⁻`、`3s²`。
- **双重角标**用行内 `$E^{\ominus}_{\text{cell}}$`，**绝不** `$$…$$`。
- `Cl`、`AlCl₃`、`PCl₅` 用普通小写 l。
- 提到第几个碳一律 **IUPAC 编号**。

---

## 章节分类

只落到 **chapter（1–22）**，不到 subsection / outcome。Paper 2 是 AS，**不碰 23–37 章**。

**按大题归属，一题一个主章**，跨章的在题头标 `(兼 chNN)`，**不拆题**。

分类必须**先于**分工完成——按 chapter 派活的前提是先知道每道题归哪章。
分类用大题 stem + `_json` 里的小问文本即可，不开 subagent、不读图。

---

## 分工与额度纪律

### 按 chapter 分工，写者独占

**一个 subagent 独占一个 chapter 文件夹**，只写自己那个目录。这样：

- 写者唯一 → 无写冲突（如果按卷分工，多个 subagent 会同时写同一份卷 md）；
- 一个执行体只在一个主题里打转，chemistry 上下文建立一次反复用，比按卷跳 5 个
  不相干主题更省也更一致。

### 派活规矩

- 每个 subagent **只做 1 个 chapter**，做完即结束——避免长跑失控吃额度。
- 执行体**只拿本章上下文**：本章在 `classification.md` 里的行 + 对应卷的 `_json` 片段 +
  已裁好的图 + 含图页的 170dpi PNG + 样板 md 路径。
  **不塞整份 classification 全表，不传整卷高 dpi 渲染。**
- 先开 **1 个试点**测单章成本，再据此排批。并发起手 2，稳了加到 4。
- 主 session 每章抽查 1 题 + 对账关键数值，**不逐字通读产物**（省主 session 的 context）。

### 额度是主刹车，时间是次刹车

- **5 小时窗口从「本窗口第一次调用」起算，刷新点会漂**——不是固定的 01:10 / 06:10 / 11:10 / 16:10。
  实测按固定点挂过 recurring cron，结果在额度已用 95% 时触发，白烧一轮。
  唯一可靠的读数是侧栏 `ACCOUNT & USAGE` 面板的「Resets in …」（`sh tools/usage.sh` 截图看）。
- **挂定时任务一律「一次性 cron + 刷新时刻后留 10 min 冗余」**：
  1. 收工时跑 `sh tools/usage.sh`，读出「Resets in …」，算出绝对刷新时刻；
  2. 按「刷新时刻 + 10 min」挂**一次性** cron（`CronCreate`，不要 recurring）——
     冗余是给窗口结算延迟留的，掐着点挂会落在旧窗口里；
  3. cron prompt 的**第一条指令必须是**「先跑 `sh tools/usage.sh` 复核额度已刷新，
     若已用 > 20% 说明窗口还没换，按面板重新挂一次性 cron，不要派活」——
     定时器只是闹钟，真正的门禁是面板读数。
  4. 一次性 cron 是 session-only：compact 扛得住，Claude 退出就没了，重开 session 要 `CronList` 复查。
- 派活前先看剩余额度：低于「实测单章成本 × 并发数 × 1.5」就**不派，等下一个刷新点**。
- 剩余 ≤ **15%** 一律停，不管窗口还剩多久。
- **绝不主动跑进 extra usage**——它只是防止已启动任务被腰斩的保险，不是可花的预算。
  一旦 extra usage 非零，说明估算偏了 → 停下重算单章成本。
- 时间上另外在窗口结束前 20 分钟收手。
- 批前批后各记一次用量到 `BUDGET.md`。

### subagent prompt 顶部必须写死的硬规矩

- **凡带化学式、方程、结构式的小问，文本裁题后必须对渲染页视觉核对一遍。**
  `extract.py` 已消掉上下标风险，但版式和符号仍要复核。
- 关键数字（浓度、质量、Aᵣ、ΔH、pH、分值）必须和官方 MS 对账。
- 异常（找不到题 / 页错位 / 题答对不上 / 图裁坏 / 该题实际不属于本章）**停下来报**，
  不许自圆其说、不许硬凑。
- **骨架式（skeletal formula）的每个拐点就是一个碳。** 数碳数前先把拐点数进去——
  实测有执行体把左支链折点漏掉，据此误判「官方 QP 少印一个 CH₂」，主 session 核图后推翻。
- **报「官方 MS / QP 有缺陷」之前先自己数两遍，并知道主 session 会亲自看图复核。**
  真缺陷是有的（空白格、题号印错、小问被官方撤销），但「结构式少一个碳」这类几乎都是数错。
- **只用 `originalpdf/` 里的 PDF。** 若怀疑归档文件有问题（缺页、缺题），**停下来报告**，不要自己去别的站点下载替代品——数据源由主 session 统一把关（实测有执行体自行去 pastpapers.co 取了文件，结果虽对但流程不可控）。
- **`**答案**` / `**判分**` 只写英文**，一个中文字都不要有（详见「提取产物格式」一节）。
- **只写自己那个 chapter 文件夹**，不碰别的章、不改已有文件。
- **绝不碰 `../reference.md`**（hook 也会拦）。

---

## 跨章改造：镜像 + 小问级标注

一道 CIE 大题经常横跨好几章。口径是：**正本只有一份，放主章；够分量的其它章拿整题镜像。**

### 小问标签

正本里给**带 `[n]` 分值的**小问标上它实际考的章：

```markdown
### (b)(iii) [3] · ch9
### (c) [4] · ch16 ch17        ← 真两边都占分才双标
### (a) The chlorides of Period 3 …   ← 没有 [n] 的铺垫行不标
```

格式写死成「一个空格 + `·` + 一个空格 + `chN`」，为的是能 grep。
**只标跨章的题**（单章题无歧义，标了浪费额度）。

### 四个脚本，跑的顺序不能错

| 脚本 | 干什么 |
|---|---|
| `mirror.py` | 按标签算镜像目标，重写正本 + 生成镜像 + 22 份 README；顺手删过期镜像与孤儿图 |
| `verify.py` | 机械验收：正本题数 / 分值、每卷 60、上下标、图链接、镜像块不计分 |
| `audit.py` | 挑出**主章被标空 / 主章不是最大块 / 有小问漏标**的题 |
| `heat.py` | 按标签重算各章真实分值，喂 `classification.md` 的热度表 |

**`mirror.py` 会重写正本文件 —— 跑标注 subagent 期间绝对不要执行它**，会和执行体的 Edit 撞车。
必须等所有 agent 都报完工。（实测撞过一次：脚本按新门槛正确删掉了一个镜像块，
执行体误以为「文件被截断」，又手工重建了一遍。）

`mirror.py --check` 是 dry-run，只报要改什么、不落盘。**删文件前先跑它看清单。**

### 门槛：≥2 分 **且** ≥15% 题分

只卡绝对分会让镜像爆炸——实测有道 17 分的题散进 8 个章、每章才 1–2 分，
整题镜像进去全是噪音。够不上门槛但确实考到的，写进该章 README 的「零星考点」指路。

### 两条踩过的坑

- **`audit.py` 存在的理由**：`mirror.py` 只认 `chapters.py` 的主章、不会自己改，
  所以「主章在自己题里占 0 分」这种事它发现不了。实测 ch21 Organic synthesis 第一遍
  被整章标空（4 题 38 小问，ch21 一分没有），因为执行体漏了 **21.1.3 analyse a given
  synthetic route**——这类「分析路线某一步」的能力章，很容易被逐个小问拆进官能团章。
  **凡是「能力型」的章（ch21 合成路线、ch13 术语与异构、ch22 谱图），派活时要在 prompt 里
  点名它自己的 outcome**，否则会被拆空。
- **分类要以 outcome 为准，不要按标题望文生义**。实测两处：
  「lattice 结构 → 物理性质」在 **4.2**（States of matter）不在 ch3；
  ch12 标题叫「Nitrogen and sulfur」但 5 条 outcome 全是 nitrogen，sulfur 只在 12.1.5
  作为「NO/NO₂ 催化氧化大气 SO₂」出现一次 → sulfur 的氧化数归 ch6，Contact process 归 ch7。

---

## 验收清单

逐条都是 grep 能跑的机械检查，每批收工必跑一遍。

1. `grep -rE 'SF6|3s2|mol–1|H2SO4|SO42' extracted/` **零命中**（命中即上下标未还原）。
2. `grep -rn 'ℓ|\$\$|(_img/|&lt;' extracted/*/*.md` **零命中**
   —— 分别是 script ℓ、块公式、误引临时渲染目录、HTML 实体未转义。
3. `grep -rln '本卷与 9701/23 同卷' extracted/*/*.md` **只能命中 `9701_w24_21.md` 与
   `9701_w25_21.md`**。variant 2 在任何会期都是独立卷，标上去就是错的
   （实测有执行体凭空补过这条标注）。
4. **中文化学名零命中**：`grep -rnoE '环[丙丁戊己庚辛]烷|[一-龥]{2,}酸[一-龥]?[乙甲]酯' extracted/*/*.md`
   —— 执行体爱在括号里补个中文译名（「cyclopropane（环丙烷）」「diethyl propanedioate（丙二酸二乙酯）」），
   违反「chemistry term 一律英文」。解释性旁注可以中文，**化合物名不行**。
5. 每个 `![…](img/…)` 都指向存在文件，图无截断、无夹带竖排边注。
6. 按 `chapters.py` 核对：每道大题恰好落在一个 chapter 文件夹，无遗漏无重复；
   **同一卷跨各章的 `[n]` 分值求和 = 60**（脚本见 `BUDGET.md`）。
7. 随机抽 10 个小问，答案数值逐个对官方 MS。
8. VS Code Markdown preview 打开 2–3 份，`$…$` 与 Unicode 上下标显示正常。
9. `git status` 里 `../reference.md` 恒为 clean。
10. `BUDGET.md` 每批有开工 / 收工两条记录，extra usage 全程为 $0。
