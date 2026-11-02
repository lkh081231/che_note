# AS chapter 1–22 Colab 可交互笔记（ipynb + %%html）

> 本计划已于 2026-10-30 在 Windows session 里定稿，**在 Linux Mint session 里执行**。
> Mint session 开工先做 Step 0（见「每章流程」末尾），然后从 ch1 开始；每章做完停下等用户确认。
> 另：官方 colab CLI 只支持 Linux / macOS，这也是全程放在 Mint 的原因之一。
> 2026-10-30 已在 Mint 上实测过一遍环境，结论见下节；与 Windows 版计划不同的地方都已改写。

## Mint 环境（2026-10-30 实测）

repo 在 Windows 分区上，两边是**同一份工作区**（同一个 `.git`）：

| | Windows | Mint |
|---|---|---|
| repo 根 | `C:\che_note` | `/media/lkh/OS/che_note`（NTFS，`fuseblk`，权限全是 777，`core.fileMode=false` 已设） |
| `file://` URI | `file:///C:/che_note/...` | `file:///media/lkh/OS/che_note/...` |
| Chrome | `/c/Program Files/Google/Chrome/Application/chrome.exe` | **未安装** → Step 0 装 `chromium`（Mint 源里有 156.x），之后 `CHROME=chromium` |
| scratch | — | `$COLAB_TMP` / `$ROADMAP_TMP` 放 `/tmp/...` 或 session scratchpad，不进 repo |

实测状态：

| 项 | 状态 | 处理 |
|---|---|---|
| python | 3.12.3（系统 python，PEP 668，别 `pip install` 进系统） | 用 `uv run --with pymupdf python ...`；`build_colab.py` / `check_colab.py` **只用标准库**（ipynb 就是 JSON，不依赖 nbformat） |
| PyMuPDF / nbformat | 都没装 | 同上，按需 `uv run --with` |
| uv / uvx / node 22 | ✅ `~/.local/bin` | |
| headless 浏览器 | ✅ `/usr/bin/chromium` 156.0.8078.47（2026-10-30 装）；Firefox 仍是默认浏览器 | `CHROME=chromium`；`probe-roadmap-geometry.py` + `check` 在 Mint 实跑，四项全 0 |
| playwright MCP | ❌ 本 session 连不上（launcher 走 `npx @playwright/mcp@latest`，且本机没有 Chrome） | 装好 chromium 后重连；若仍不行，交互实测退到 `uv run --with playwright` 写脚本跑（`playwright install chromium` 装到 `~/.cache/ms-playwright`） |
| Claude in Chrome | 不可用（Mint 没 Chrome，扩展无处可装） | 不依赖它 |
| screenshot CLI | ✅ `uvx screenshot-feedback-hook-mcp monitors`：`[0]` 拼接 3840×1080、`[1]` `[2]` 各 1920×1080（X11） | 与 CLAUDE.md 一致 |
| colab CLI | ✅ `~/.local/bin/colab`，已授权（余额 223.98 CU，CPU runtime 不耗 CU） | **验收第 5 步用它**：`colab new` CPU → `colab exec -f <nb>.ipynb` 逐 cell 真跑 → `colab log -o` 导出查 error → `colab stop`。它只能开云端 VM，连不了本地 Jupyter |
| Colab 本地运行时 | ✅ `uv tool install --with ipykernel notebook`（Notebook 7.6.3，装在 `~/.local/share/uv/tools/notebook`），根目录 `~/colab-runtime/`（含官方要求的 `content/`） | 启动命令见「Colab 本地运行时」 |
| colab MCP | ❌ 授权有问题（2026-10-30 用户决定不用） | 改用 colab CLI |
| Google Drive connector | ⚠️ `create_file` 能传内容，但 `update_file` **只改 metadata，不能覆盖内容** | Drive 同步改走 rclone，见「入口」 |
| rclone | ✅ 已配 remote `gdrive:`，里面已有 `Colab Notebooks/` | `rclone copyto` 覆盖同名文件，file id 不变 → 链接不变。注意 rclone 共享 client_id 2026 年内会停用，届时要换自建 client_id |
| gh CLI / GitHub 凭据 | ❌ gh 未装；HTTPS 没有 credential、`~/.ssh` 没有 key → **Mint 上 push 不了** | 需要用户配一次（`gh auth login` 或加 SSH key）；之前在 Windows 端 push |
| 磁盘 | OS 分区剩 26 G | 够用 |

**换行符坑（必须 Step 0 先处理）**：Windows 端 checkout 出来的工作区是 CRLF，而仓库里存的是 LF。
Mint 上 git 没设 `autocrlf`，于是 `git status` 显示 176 个文件 modified、`git diff` 两万多行全是 `\r`，
实际内容改动只有 `.gitignore`（`git -c core.autocrlf=input status` 验证过）。不处理的话，Mint 上第一次
`git add -A` 就会把整库改成 CRLF 提交上去。处理方式二选一（Step 0 问用户）：

**已处理（2026-10-30）**：加了 `.gitattributes`（`* text=auto`），两边都生效、跟着仓库走；之后 Mint 上
`git status` 只剩真实改动。没用 `git config core.autocrlf input`，因为 `.git/config` 是两边共用的，
会把 Windows 端的设置一起盖掉。新文件在 Mint 上照常写 LF 即可。

## Colab 本地运行时

用户定了：**Colab 的 runtime 一律连本机 Jupyter，不用云端 VM**（不耗 compute unit，也不用 colab CLI）。
做法照官方 local-runtimes 页面的 Jupyter 选项，不用装 `jupyter_http_over_ws`。Notebook 7 已经把
`NotebookApp.*` 改名为 `ServerApp.*`：

```bash
cd ~/colab-runtime && jupyter-notebook --no-browser \
  --ServerApp.allow_origin='https://colab.research.google.com' \
  --port=8888 --ServerApp.port_retries=0 --ServerApp.allow_credentials=True
```

- 启动日志里会打出 `http://127.0.0.1:8888/tree?token=…`，去掉 `tree` 后贴进 Colab：Connect ▾ → *Connect to a local runtime…*。
- 在 Mint 上用 agent 的后台任务起这个服务，拿到 token 后交给用户。服务挂掉不影响阅读，因为 output 是预填的，只有 Run all 那一步需要它。
- 本地内核里**没有 Python 的 `google.colab` 模块**，所以 notebook 里不写任何依赖它的 Python 代码。
  html cell 里的 JS（例如 `google.colab.output` 的 resize）由 Colab 前端注入，跟 runtime 无关，照常用，失败静默。
- 根目录放在 ext4 的 `~/colab-runtime/`，不放 NTFS 上的 repo，免得 Jupyter 的 checkpoint 之类文件弄脏仓库。
- 别人用 GitHub / Drive 链接打开时，默认连的是 hosted runtime。这不影响阅读，因为 output 是预填的。

## Context

vault 里目前只有 `chapter1 atomic structure.md` 一份成品笔记（而且只写到 1.1 / 1.2），其余章节只有
`pdfnote/che/` 里的老师 PDF 讲义。用户要为 **AS 每一章（ch1–ch22）** 做一份能在 **Google Colab**
上打开的可视化、可交互笔记：markdown cell 写正文，`%%html` 前端代码块做图和交互；
风格照 chapter1 md（syllabus 小节分段、A/B/C 子题、中文 prose + 英文 chemistry term、
每段后 learning outcome、末尾 Practice 真题 + 判分、最后 LO 清单）。

已定（用户回答）：
- **入口两者都要**：repo 内 `colab/` 放 ipynb，GitHub 链接 `colab.research.google.com/github/lkh081231/che_note/blob/main/colab/<file>.ipynb`（private repo，首次需在 Colab 授权）；同时同步到 Drive `Colab Notebooks/che_note/`。
  - Drive 同步用 **rclone**：`rclone copyto colab/<file>.ipynb "gdrive:Colab Notebooks/che_note/<file>.ipynb"`，覆盖同一文件、id 不变；
    id 用 `rclone lsjson --stat "gdrive:Colab Notebooks/che_note/<file>.ipynb"` 的 `ID` 字段取，记进 `drive-ids.json`，
    链接 `https://colab.research.google.com/drive/<id>`。
  - Drive connector 只当 fallback：它没法覆盖内容，只能 trash + 重新 `create_file`（`disableConversionToGoogleType: true`），**链接会变**，要同步改 README。
- **每章做完都停下等用户确认**，再开下一章。
- **全程在 Linux Mint 做**（Mint 已装 colab MCP + colab CLI，可读写本文件夹）。

## 内容来源（每章都按这个优先级）

1. `reference.md` 该章节 — LO 逐字、内容边界（source of truth；只读，hook 已拦写入）
2. `pdfnote/che/` 对应讲义 — 正文、数据、图（`uv run --with pymupdf` 抽 text layer；要看图就渲染页面 PNG，读图交给 subagent）
3. `passyear/extracted/chNN-*/` — Practice 题目 + mark scheme 标准句式（冲突以最新卷为准），引用写卷号如 `9701/22 May/June 2026 Q2(b)(iii)`
4. `pdfnote/che/164870-2016-specimen-data-booklet.pdf` — IE、radius、IR 吸收等数值

讲义对应：ch1 `Chapter 1 - Atomic structure (notes) (2).pdf`（7.1 MB，2026-05；同目录的 `… (2) 2.pdf` 是另一个版本，
4.5 MB、md5 不同，开工时先比一下两份差在哪，再定以哪份为准）；ch3 是 `Chapter 3- Chemical bonding (notes) 4.pdf`，另加 `VSEPR Theory tutorial .pdf`；ch8 另加 `Structure question exercise Chapter 8`；
ch10/15/16/19/22 用 `SN-Chapter NN`；ch14 与 ch20 共用 `SN-+Chapter+14+%2B+20.pdf`；ch21 只有 exercises，正文靠
reference.md + 复用 `organic-reaction-roadmap.html`。文件名 slug 沿用 `passyear/extracted/` 的
（`ch01-atomic-structure` … `ch22-analytical-techniques`）。

## Repo 结构（新增）

```
colab/
  PLAN.md                          本计划副本（Mint session 从这里读）
  README.md                        索引：每章 GitHub-Colab 链接 / Drive 链接 / 状态
  kit/kit.css  kit/kit.js          共享样式 + 交互件（build 时内联进每个 html cell）
  kit/kit3d.js                     3D 封装（只内联进 3D cell）
  data/mol/*.sdf                   PubChem 3D 坐标（build 时内联）
  src/ch01-atomic-structure.md     章节源文件（人写、人审）
  ch01-atomic-structure.ipynb      build 产物（commit；不在 Colab 里直接改）
  drive-ids.json                   Drive file id 映射，更新时覆盖同一文件、链接不变
tools/build_colab.py               src → ipynb
tools/check_colab.py               机械校验 + 导出 preview 页面
```

### 源文件格式（`colab/src/chNN-*.md`）

用注释分 cell：`<!-- md -->` 后面是 markdown cell；`<!-- html: 标题 -->` 后面是一个交互 cell（HTML + `<style>` + `<script>`）。
build 指令：
- `{{lo 1.1.5}}` → 插入 reference.md 该 LO 原文（保证 verbatim，不靠手抄）
- `{{lo-checklist}}` → 自动生成本章全部 LO 的交互清单（勾选 + 进度条）
- `{{chemfig \chemfig{...}}}` → 调 `tools/chemfig2svg.py` 的 `render()` 编成内联 SVG（有机章结构式；ChemFig 仍是源码，沿用 CLAUDE.md 的 120° / upright cross 约定，必要时扩展该脚本的 subset）
- `{{img path}}` → base64 data URI（chapter1 的 `image/…`、真题 `img/*.png`）

### build 产物约定

- html cell → code cell：`# @title 标题 { display-mode: "form" }` + `display(HTML(r"""…"""))`，内联 kit；**预填 `display_data` text/html outputs**，打开即见图，不必先 Run。
  （试点发现：`%%html` 和 `#@title` 都必须在第一行，没法共存，所以不用 `%%html`。）
- 2D html cell **零外部依赖**；只有 3D cell 从 CDN 加载 pinned 版本的 Three.js（见下节）。$^{A}_{Z}X$ 这类双脚标用 kit 的 `.nuc` 堆叠 span 画；markdown cell 里照 CLAUDE.md 用 `$…$`（绝不 `$$`）、Unicode 上下标、`<sub>`。
- 所有颜色走 kit 的 token，有 light/dark 两套，卡片自带背景色（Colab dark theme 下输出区是深色）。
- 记法与语言规则全部沿用 CLAUDE.md（中文 prose、chemistry term 英文、`Cl` 正常 l、IUPAC 碳编号）。chapter1 md 里的 `$$…$$` 和英文语病（outweight、electron deflect more compare…）在 notebook 版里改正，不动原 md。

### kit 提供的交互件

reveal（真题「答案」按钮，代替 `<details>`）、自测填空（填数字即时判对错，如 p/n/e 表）、单选题、
LO checklist（localStorage 持久化，全包 try/catch）、tabs、slider 绑定、SVG tooltip、
iframe 高度自适应（交互展开后调用 `google.colab.output` 的 resize，失败静默）。

## 3D 图

凡是空间结构决定答案的地方都配一个可拖动旋转的 3D cell（`<!-- html3d: 标题 -->`）。

- **引擎**：Three.js `three@0.160.0`，从 jsDelivr 动态 `import()` `build/three.module.min.js`，版本写死。
  不用 import map / `examples/jsm`（OrbitControls 里的 bare `'three'` 要 import map 才解析得了）；拖动旋转、滚轮缩放在 kit3d 里自己实现。
- **`colab/kit/kit3d.js`**（build 时内联进每个 3D cell）封装：
  - `molecule(atoms, bonds)` — ball-and-stick，CPK 配色，lone pair 画成半透明 lobe，可选显示 bond angle 弧和数值；
  - `orbital(type)` — 由 angular part |Y<sub>lm</sub>| 生成 s / p<sub>x,y,z</sub> / 5 个 d 的 lobe 网格，phase 双色；1s/2s/3s 用 point cloud 显示 radial node；
  - `lattice(kind, n)` — 程序生成 NaCl、metallic、diamond、graphite、SiO₂、I₂、ice（含 hydrogen bond 虚线），可调 unit cell 数量；
  - 统一：OrbitControls 拖动旋转 / 滚轮缩放、「复位视角」「自动旋转」按钮、hover 显示原子名、light/dark 背景跟随 kit token。
- **分子坐标**：VSEPR 理想几何在 kit3d 里解析生成；真实有机分子 build 时从 PubChem 取 3D SDF，**存进 `colab/data/mol/*.sdf` 并 commit**，运行时不再联网取数据；`{{mol3d name}}` 指令把坐标内联进 cell。
- **CDN 不可达时**：cell 显示一张同角度的静态 SVG 投影 + 提示文字，不留空白。

各章 3D 清单：

| ch | 3D cell |
|---|---|
| 1 | s / p / d orbital 形状（可切换叠加 3 个 p、5 个 d）；1s vs 2s radial node point cloud |
| 3 | VSEPR 全部形状（linear → octahedral，含 NH₃、H₂O、SF₄、ClF₃、XeF₄ 等 lone pair 情形，显示 bond angle）；σ 与 π overlap；sp / sp² / sp³ hybrid orbital；polar vs non-polar（dipole 箭头） |
| 4 | giant ionic / metallic / giant molecular（diamond、graphite、SiO₂）/ simple molecular（I₂）/ ice 晶格 |
| 11 | halogen 分子大小对比 + instantaneous dipole 示意 |
| 12 | NH₃ / NH₄⁺ 形状对比（lone pair → dative bond） |
| 13 | ethene 平面 + π 电子云；cis/trans 对比；optical isomer（chiral centre 镜像对，可同步旋转对照是否重合）；butane 构象 |
| 14 | Br₂ 接近 C=C π 电子云（electrophilic addition 的空间图） |
| 15 | S<sub>N</sub>2 backside attack 动画（Walden inversion）；S<sub>N</sub>1 平面 carbocation 两面进攻 |
| 17 | trigonal planar C=O 两面受 CN⁻ 进攻 → racemic mixture |
| 20 | poly(ethene) / poly(chloroethene) 链段 |

## Colab 渲染假设 — ch1 试点时逐条实测，不成立就换 fallback 并写进 CLAUDE.md

| 假设 | fallback |
|---|---|
| 预存的 HTML output（含 `<script>`）打开即渲染并执行 | notebook 顶部提示：连本地运行时 → Run all（%%html 秒跑） |
| `%%html` + `#@title` + `cellView: form` 能隐藏代码 | 代码可见；或改 Python `display(HTML())` + form |
| 交互后 output iframe 会长高 | kit 主动调 resize API |
| markdown cell 的 `$…$`、GFM table、`<sub>`、data-URI `<img>` 正常 | 图改 cell attachments 或挪进 html cell |
| dark theme 下可读 | 卡片强制浅底 |
| output iframe 里 localStorage 可用 | 不持久化，只当页有效 |
| 连本地运行时后 `%%html` 的 output 与 hosted 一样渲染（iframe、resize、JS） | 记录差异；必要时只靠预填 output |
| Drive 上传的 .ipynb 双击即用 Colab 打开 | 换 mimeType `application/vnd.google.colaboratory` |
| output iframe 里能用 import map 从 jsDelivr 载 ES module，WebGL 可用 | 改 cdnjs 的 UMD 版 three；再不行退到静态 SVG 投影 |
| 一个 notebook 里多个 WebGL cell 不会超出浏览器 context 上限 | 3D cell 离开视口时 `dispose()`，回来再建 |

## 每章流程（一章一轮，做完停下）

（2026-10-31 起：先搭框架，交互 cell 逐个单独写、测、审，再合并回 notebook。）

1. 读 reference.md 该章 + 抽讲义 text 到 scratch digest + 读 `passyear/extracted/chNN-*/`（本章主管 + 跨章镜像里考本章的小问）。
2. **搭框架**（主 agent 自己做）：写 `colab/src/chNN-*.md` 的全部 markdown 正文、practice、`{{lo-checklist}}`；
   每个交互 cell 只占一个槽：`<!-- html: 标题 -->` / `<!-- html3d: 标题 -->` 下一行 `{{cell 名字}}`。
   文件不存在时 build 出「待合并」占位卡，框架就能先 build + 机械校验通过。
   同时给每个 cell 写一份**规格**（scratch，不进 repo）：要讲哪条 LO、画什么、交互什么、数据从哪来、
   pass/fail 线（例如「三条 beam 的弯曲方向一眼可辨」「node 数 2s=1 / 3s=2」）。
3. **逐个 cell 写 → 测 → 审改**，可并行；每个 cell 两个 subagent：**A 写 + 测，B 审图 + 改**。
   A：
   - 写 `colab/src/chNN/名字.html`（HTML + `<style>` + `<script>`，用 kit；规则同 ch1）；
   - `python tools/build_colab.py chNN --cell 名字 [--3d]` → `$COLAB_TMP/cells/chNN-名字.html` 单页预览；
   - 写 `colab/tests/chNN_名字.py`（照 `ch01_interact.py`：点 / 拖 / 填、`[data-clash]` 为 0、console 0 error、
     3D 拖动前后 hash 变、动画类要采样多帧断言），截图到 scratch；
   - 测试全绿后回报：文件路径、测试 N/N、截图路径、踩到的坑。
   B（干净上下文，审美把关）：读截图 + 规格判 PASS/FAIL（规则同 CLAUDE.md「看图这一步交给 subagent」：
     逐字转写 ≥8 条最小字、认不出就 FAIL），**FAIL 由 B 自己改** cell → 重跑 `--cell` 预览和测试 →
     重新截图再审，循环到 PASS；回报：VERDICT 原文、改了什么、测试 N/N、踩到的坑。
     B 改的轮数多了上下文会变长、读图变差——超过 3 轮还没 PASS，交回主 agent，另派一个新的 B。
4. **合并**：主 agent 收齐所有 cell → `build chNN` → 整本校验（见下）→ 修到全绿。
5. commit（中文 message：做了什么 + 踩到的坑；按文件名 add）→ push → Drive 同步（rclone copyto，首次记 id）→ 更新 `colab/README.md`。
6. 汇报两个链接 + 本章交互件清单 + 存疑点，**停下等确认**。

### subagent 选型

| 活 | 用谁 |
|---|---|
| 写 cell / 测试脚本 / 跑测试 | Agent 工具（Claude），或 `agy`（Antigravity CLI）|
| **涉及前端审美的**：设计交互件、审图 + 改（B） | **只用 Opus 5.5 或 Gemini 4 Argon**：Agent 工具 `model: opus`，或 `agy --model gemini-4-argon-high` / `claude-opus-5-5-high` |
| 纯机械的（跑 build / check、数据抽取） | 随意 |

`agy` 用法（非交互，读图可用；`agy models` 列模型）：

```bash
# A：写 + 测
agy -p "<cell 的完整规格>" --model claude-opus-5-5-high --mode auto --add-dir /media/lkh/OS/che_note
# B：审图 + 改（截图绝对路径 + 图里画了什么 + 规格 + pass/fail 线 + 逐字转写 ≥8 条最小字 + VERDICT 行）
agy -p "<审改 prompt>" --model gemini-4-argon-high --mode auto --add-dir /media/lkh/OS/che_note
```

**必须 `--mode auto`**：`--mode accept-edits` 在 headless 下会自动拒绝所有 shell 命令
（`a tool required the "command" permission that headless mode cannot prompt for`），A/B 没法 build / 跑测试，一启动就退出（2026-11-02 ch4 踩过）。

审图和修改是同一个 subagent（B），但 B 不是写 cell 的那个（A）：B 第一次读图时必须是干净上下文，
先只看截图 + 规格下结论，再去看源码改。

ch1 额外：先做 Step 0（环境已于 2026-10-30 摸过，`colab/PLAN.md` 已就位，剩下的是动手项）——
① ~~处理 CRLF~~（已加 `.gitattributes`）；② ~~装 chromium~~（已装，探针已验证），重连 playwright MCP；
③ `rclone lsd gdrive:` 确认 token 还有效，建 `Colab Notebooks/che_note/`；④ 起本地 Jupyter，`colab-mcp` 连一次，确认能打开 Colab 并接上本地运行时；
⑤ 讲义 ch1 两个版本比对；ch1 的 1.1/1.2 从 chapter1 md 移植（tikz atom model、beam、radius 图改成 SVG/交互），1.3/1.4 从讲义新写；试点结论写进 CLAUDE.md（+ AGENTS.md 同步）的新小节「Colab notebook」。

## 各章交互件草案（实际以讲义内容为准，做每章时再细化）

| ch | 交互件 |
|---|---|
| 1 | $^{A}_{Z}X^{q}$ → p/n/e 计算器；electric field 里 p/n/e beam 偏转（可开关粒子）；Period 3 atomic/ionic radius hover 图；H–Kr electronic configuration + orbital box 填充器（含 Cr/Cu、ion 先失 4s）；s/p/d orbital 形状；first IE 跨 period / successive IE 图，点 dip 看解释 |
| 2 | isotope abundance → *A*ᵣ（mass spectrum 柱）；mole 换算图（mass / particles / gas volume / concentration）；empirical → molecular formula 分步解；titration 计算分步 |
| 3 | ΔEN → bond type 滑杆；VSEPR shape explorer（bp/lp → shape + bond angle）；dot-and-cross 示例切换；hydride boiling point 图（H-bond 异常）；σ/π overlap |
| 4 | *pV* = *nRT* 单位换算计算器；ideal vs real gas；giant / simple lattice 结构切换 |
| 5 | energy profile（exo/endo、*E*<sub>A</sub>）；*q* = *mc*Δ*T* 计算器；Hess cycle 交互；bond energy 计算 |
| 6 | oxidation number 计算 / 测验；half-equation 配平分步 |
| 7 | Le Chatelier 模拟（浓度/T/p 改变 → 移动方向，*K*<sub>c</sub> 变不变）；ICE table → *K*<sub>c</sub>/*K*ₚ；Haber / Contact 条件折中；titration curve + indicator 选择 |
| 8 | Boltzmann distribution（T 滑杆、*E*<sub>A</sub> 线、阴影面积、catalyst） |
| 9 | Period 3 性质图；oxide / chloride 与水反应表（筛选 + 溶液 pH） |
| 10 | Group 2 趋势图；thermal decomposition / solubility 趋势 |
| 11 | halogen 颜色（gas / aq / organic solvent）；displacement 网格；halide + AgNO₃ / NH₃ 测试模拟；Cl₂ + NaOH cold/hot 氧化数追踪 |
| 12 | NH₄⁺ 测试、Haber、NOₓ / SO₂ 与 acid rain、catalytic converter 流程 |
| 13 | functional group 图鉴（chemfig SVG，structural / displayed / skeletal 切换）；IUPAC 命名测验；isomer explorer；sp/sp²/sp³ 与 σ/π |
| 14 | free-radical substitution 分步；electrophilic addition 曲箭头分步；Markovnikov 预测；cracking |
| 15 | S<sub>N</sub>1 / S<sub>N</sub>2 分步；C–X bond energy 与 AgNO₃ 水解速率 |
| 16 | 1°/2°/3° alcohol + acidified K₂Cr₂O₇ 颜色变化；tri-iodomethane test |
| 17 | HCN nucleophilic addition 分步；2,4-DNPH / Tollens' / Fehling's 测试模拟 |
| 18 | carboxylic acid 反应；esterification / ester hydrolysis |
| 19 | amine、nitrile、hydroxynitrile 反应 |
| 20 | monomer ↔ repeat unit 互转；polymer disposal |
| 21 | 合成路线谜题；嵌入 / 复用 `organic-reaction-roadmap.html` |
| 22 | IR spectrum 浏览（峰 ↔ bond，取 data booklet）；mass spectrum M / M+1 / M+2（Cl、Br）与碳数计算 |

## Verification（每章都跑，缺一不可）

1. **机械校验** `python tools/check_colab.py chNN --js`：ipynb 结构合法；每个 code cell 首行 `#@title`、cellView form、有预填 output 且与源码一致；本章 reference.md **每条 LO 逐字出现**；无 ```` ```tikz ````、无 `$$`、无相对路径图片、无 `𝑙` 字形；导出每个 html cell 为独立 preview 页 + 一个总页到 `$COLAB_TMP`（scratch，不进 repo）。
2. **JS 报错**：headless `chromium --headless --enable-logging=stderr` 跑 preview（URI 用 `Path(...).resolve().as_uri()` 生成，别手拼 `file:///C:/`），`Uncaught` 为 0（3D cell 要加 `--use-gl=angle --use-angle=swiftshader`，不能用 `--disable-gpu`，否则 WebGL 起不来会误报）。
3. **交互实测**：照 `colab/tests/ch01_interact.py` 写本章的脚本（python playwright 驱动 `$CHROME`，`uv run --with playwright`），逐个点 / 拖 / 填每个交互件，console 0 error；图上的标签一律用 `K.label` 放，脚本断言没有 `[data-clash]`；3D cell 额外：拖动前后各截一张确认视角真变了、canvas 不是全黑 / 全白，断网（拦截 jsDelivr）时 fallback SVG 出现。
4. **两级截图 + subagent 读图**（照 CLAUDE.md）：整页 + 每个交互件 z≥1.5 局部；派 subagent 给绝对路径、图里画了什么、明确 pass/fail 线、逐字转写 ≥8 条最小字号文字，`VERDICT: PASS/FAIL` 收尾。
5. **Colab 真跑**：
   - 内核侧：`colab new -s che-chNN` → `colab exec -s che-chNN -f colab/<slug>.ipynb --timeout 180` → `colab log -o` 导出，确认每个 code cell 都有输出、0 个 error → `colab stop`。
   - 前端侧（预填 output 是否渲染、表单是否藏代码、iframe 高度、dark theme）：用户在自己的浏览器打开 Drive 链接（可连本地运行时），screenshot-feedback-hook CLI 截 light + dark 各一张交 subagent 读。
6. **内容核对**：每个数值、定义、判分句式回查 reference.md / 讲义 / mark scheme，汇报里列出存疑点。
