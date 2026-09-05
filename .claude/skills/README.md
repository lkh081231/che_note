# 这里的 skill 是副本，不是正本

这两份 skill 在**两个地方各有一份**：

| 位置 | 作用 |
|---|---|
| `C:\Users\sebas\.claude\skills\` | **正本**。user 级，任何目录开 session 都能用——做物理 / 生物题库时 vault 不是 `che_note`，只有 user 级的才生效 |
| `c:\che_note\.claude\skills\`（这里） | 副本。跟着 vault 进 git，做版本管理与备份用 |

**改动请改正本，然后同步过来**：

```sh
cp -r "$USERPROFILE/.claude/skills/cie-9701-pastpaper-bank" \
      "$USERPROFILE/.claude/skills/cie-pastpaper-bank" c:/che_note/.claude/skills/
```

反向核对（看两边是否已经漂移）：

```sh
diff -r "$USERPROFILE/.claude/skills/cie-9701-pastpaper-bank" c:/che_note/.claude/skills/cie-9701-pastpaper-bank
diff -r "$USERPROFILE/.claude/skills/cie-pastpaper-bank"      c:/che_note/.claude/skills/cie-pastpaper-bank
```

⚠️ 在 `che_note` 目录下开 session 时，**同名 skill 会有两份可见**（user 级一份、项目级一份）。
如果两边内容不一致，谁生效取决于加载顺序——所以别让它们漂移。

## 两份 skill 的分工

- **`cie-9701-pastpaper-bank`** —— 化学 9701 换年份 / 换 Paper。具体到 URL 模式、
  span 规则、`extract.py` 的已知 bug、subagent prompt 模板。
- **`cie-pastpaper-bank`** —— 换科目（9702 物理、9700 生物、9709 数学、9708 经济 …）。
  讲的是哪些能直接搬、哪些必须按科目重做（mark scheme 结构差异最大）。

两者的 description 里互相指向，避免选错。
