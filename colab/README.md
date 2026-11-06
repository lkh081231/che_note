# Colab 可交互笔记（AS chapter 1–22）

每章一本 notebook：markdown cell 写正文，🔬 / 🧊 / 📝 开头的 cell 是交互图（预先渲染好，打开即见；
空白时 Runtime → Run all）。计划与约定见 [PLAN.md](PLAN.md)。

| ch | notebook | GitHub → Colab | Drive | 状态 |
|---|---|---|---|---|
| 1 | [ch01-atomic-structure](ch01-atomic-structure.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch01-atomic-structure.ipynb) | [打开](https://colab.research.google.com/drive/1rY1FpH39jXLyIfQYKn3OaheFBJJNszFn) | 试点，待确认 |
| 2 | [ch02-stoichiometry](ch02-stoichiometry.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch02-stoichiometry.ipynb) | [打开](https://colab.research.google.com/drive/1TjG9hzPY8LKOM5lytl7xbiFMuKMBgAWB) | 待确认 |
| 3 | [ch03-chemical-bonding](ch03-chemical-bonding.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch03-chemical-bonding.ipynb) | [打开](https://colab.research.google.com/drive/1IB-5mkQW0RpRMH-iBwZdOALFi5fXuZ4R) | 待确认 |
| 4 | [ch04-states-of-matter](ch04-states-of-matter.ipynb) | [打开](https://colab.research.google.com/github/lkh081231/che_note/blob/main/colab/ch04-states-of-matter.ipynb) | [打开](https://colab.research.google.com/drive/1lVU8VJllwPRYi1usWZMDWe_2PfegcBj9) | 待确认 |

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
