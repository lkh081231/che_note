# Colab 可交互笔记（AS chapter 1–22）

每章一本 notebook：markdown cell 写正文，🔬 / 🧊 / 📝 开头的 cell 是交互图（预先渲染好，打开即见；
空白时 Runtime → Run all）。计划与约定见 [PLAN.md](PLAN.md)。

| ch | notebook | GitHub → Colab | Drive | 状态 |
|---|---|---|---|---|
| 1 | [ch01-atomic-structure](ch01-atomic-structure.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch01-atomic-structure.ipynb) | [打开](https://colab.research.google.com/drive/1rY1FpH39jXLyIfQYKn3OaheFBJJNszFn) | 试点，待确认 |
| 2 | [ch02-stoichiometry](ch02-stoichiometry.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch02-stoichiometry.ipynb) | [打开](https://colab.research.google.com/drive/1TjG9hzPY8LKOM5lytl7xbiFMuKMBgAWB) | 待确认 |
| 3 | [ch03-chemical-bonding](ch03-chemical-bonding.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch03-chemical-bonding.ipynb) | [打开](https://colab.research.google.com/drive/1IB-5mkQW0RpRMH-iBwZdOALFi5fXuZ4R) | 待确认 |
| 4 | [ch04-states-of-matter](ch04-states-of-matter.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch04-states-of-matter.ipynb) | [打开](https://colab.research.google.com/drive/1lVU8VJllwPRYi1usWZMDWe_2PfegcBj9) | 待确认 |
| 13 | [ch13-organic-intro](ch13-organic-intro.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch13-organic-intro.ipynb) | [打开](https://colab.research.google.com/drive/1_JofApUgXxwid6EAt2ecO9_nFcqUflZe) | 交互 cell 9/9 已合并（chiral3d 第 2 轮审图未做） |
| 14 | [ch14-hydrocarbons](ch14-hydrocarbons.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch14-hydrocarbons.ipynb) | [打开](https://colab.research.google.com/drive/10uq0QFZnHK9NPDSSsCmw7w3-66mo9ltw) | 交互 cell 7/7 已合并（combustion、cracking 审过；frs-mech、alkene-wheel、kmno4-hot、ea-mech、br2-pi3d 未审） |
| 15 | [ch15-halogen-compounds](ch15-halogen-compounds.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch15-halogen-compounds.ipynb) | [打开](https://colab.research.google.com/drive/16jDQ0vRcndaJ9WwShvAMR9thtMUQgZjW) | 交互 cell 3/4 已合并（agno3-rate、sn-mech、sub-vs-elim 未审；sn2-3d 未写） |
| 16 | [ch16-hydroxy-compounds](ch16-hydroxy-compounds.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch16-hydroxy-compounds.ipynb) | [打开](https://colab.research.google.com/drive/1BbydntDQs6k-6_7fH6qmErxAyDS8GeDh) | 交互 cell 2/4 已合并（acidity、oxidation-tubes 已合并；alcohol-hub、iodoform 待做） |
| 17 | [ch17-carbonyl-compounds](ch17-carbonyl-compounds.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch17-carbonyl-compounds.ipynb) | [打开](https://colab.research.google.com/drive/10P0lQfoNh6lRy7HRbjJZxH7AnzI4V3vL) | 框架（交互 cell 待做） |
| 18 | [ch18-carboxylic-acids](ch18-carboxylic-acids.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch18-carboxylic-acids.ipynb) | [打开](https://colab.research.google.com/drive/1gxHJxFjn1RQSXR5y5n5CSeW5q82c6-6E) | 框架（交互 cell 待做） |
| 19 | [ch19-nitrogen-compounds](ch19-nitrogen-compounds.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch19-nitrogen-compounds.ipynb) | [打开](https://colab.research.google.com/drive/1jADi344pS-tjQUWCfK0JOYxOhl7KLkVk) | 框架（交互 cell 待做） |
| 20 | [ch20-polymerisation](ch20-polymerisation.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch20-polymerisation.ipynb) | [打开](https://colab.research.google.com/drive/1CjNVd9s3Kk67lxilUXDF5TvIdrg-h8PG) | 框架（交互 cell 待做） |
| 21 | [ch21-organic-synthesis](ch21-organic-synthesis.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch21-organic-synthesis.ipynb) | [打开](https://colab.research.google.com/drive/1N3vXBeuMBo9YySp5orLiJjgbQP7NgI5W) | 框架（交互 cell 待做） |

organic（ch13–21）的 9 本互相链接：跨章引用写成 `{{xref chNN#锚点 文字}}`，build 成带 `#scrollTo=` 的 Drive 链接；
reaction 的 reagent / condition 统一取自 [`data/organic.json`](data/organic.json)（`{{rxn-in X}}` / `{{rxn-out X}}` 生成表格，同一个 reaction 只在 home 章详写）。
改了 registry 要重 build 全部 9 本。

## 改一章的流程

```bash
python tools/build_colab.py ch01                 # colab/src/ch01-*.md → colab/ch01-*.ipynb
export COLAB_TMP=/tmp/colab                       # 预览页放这里，不进 repo
python tools/check_colab.py ch01 --js             # 结构 / LO 逐字 / 禁用写法 / 无头 JS 报错
rclone copyto colab/ch01-atomic-structure.ipynb "gdrive:Colab Notebooks/che_note/ch01-atomic-structure.ipynb"   # 手动同步（push 后 Action 会自动做）
```

push 到 `main` 后，GitHub Action [`sync-drive.yml`](../.github/workflows/sync-drive.yml) 会把改过的 `colab/chNN-*.ipynb` 推到 Drive，
**原地替换**同名文件（file ID 不变，上表链接一直有效），再按 `drive-ids.json` 核对 ID：对不上就失败，新章会在 summary 里给出 ID。
Actions 页的 *Run workflow* 可以手动推全部。需要 repo secret `RCLONE_CONF`，内容是 `rclone config show gdrive` 的完整输出。

不要在 Colab 里直接改 notebook——改 `colab/src/` 再 build。

## 本地运行时（连本机 Jupyter）

交互 cell 的 output 是预填的，**只阅读不需要任何 runtime**；只有要 Run all（或重跑某个 cell）时才需要连。
约定一律连本机 Jupyter，不用云端 VM（不耗 compute unit）。做法照 Colab 官方 local-runtimes 页面的 Jupyter 选项，
**不用**装 `jupyter_http_over_ws`。

一次性安装（Notebook 7，装在 `~/.local/share/uv/tools/notebook`）：

```bash
uv tool install --with ipykernel notebook
mkdir -p ~/colab-runtime/content          # 根目录放 ext4，content/ 是官方要求的
```

每次启动（Notebook 7 已把 `NotebookApp.*` 改名为 `ServerApp.*`）：

```bash
cd ~/colab-runtime && jupyter-notebook --no-browser \
  --ServerApp.allow_origin='https://colab.research.google.com' \
  --port=8888 --ServerApp.port_retries=0 --ServerApp.allow_credentials=True
```

连接：

1. 启动日志里找 `http://127.0.0.1:8888/tree?token=…`，**去掉 `tree`**，得到 `http://127.0.0.1:8888/?token=…`。
2. 用上表的 **Drive 链接**打开 notebook（repo 是 private，GitHub → Colab 链接会 404）。
3. Connect ▾ → *Connect to a local runtime…* → 贴入上一步的 URL → Connect。

注意：

- 根目录放在 `~/colab-runtime/`（ext4），不要放在 repo 里，免得 `.ipynb_checkpoints` 之类弄脏仓库。
- 本地内核**没有 Python 的 `google.colab` 模块**，notebook 里不写依赖它的 Python 代码；
  html cell 里的 `google.colab.output`（iframe resize）是 Colab 前端注入的 JS，跟 runtime 无关，照常可用。
- `--ServerApp.port_retries=0`：8888 被占时直接报错，而不是悄悄换端口导致 Colab 连不上。
- 服务挂掉不影响阅读；别人用 Drive 链接打开时默认连 hosted runtime，同样能看。

背景与取舍见 [PLAN.md「Colab 本地运行时」](PLAN.md#colab-本地运行时)。
