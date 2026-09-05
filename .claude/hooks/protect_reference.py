#!/usr/bin/env python
"""PreToolUse hook: 禁止任何工具修改 vault 的 source of truth。

保护 c:\\che_note\\reference.md 和 reference.pdf —— 主 session 和 subagent
的工具调用都走同一条 hook 管线，所以两边都拦得住。

读操作（cat / head / grep / Read）一律放行，只拦写。
"""
import json
import os
import re
import sys

# 受保护的文件（vault 根目录下）
VAULT = os.path.normcase(os.path.realpath(r"C:\che_note"))
PROTECTED = {"reference.md", "reference.pdf"}

REASON = (
    "reference.md / reference.pdf 是本 vault 的 source of truth，"
    "仓库策略禁止任何自动修改（主 session 与 subagent 同样受限）。"
    "如需改动请由人工手动编辑。"
)

# Bash / PowerShell 里代表「写」的形态
WRITE_PATTERNS = [
    r">>?\s*[^|;&]*reference\.(?:md|pdf)",           # > file / >> file
    r"\btee\b[^|;&]*reference\.(?:md|pdf)",
    r"\bsed\b[^|;&]*-i[^|;&]*reference\.(?:md|pdf)",
    r"\b(?:mv|cp|rsync|install)\b[^|;&]*reference\.(?:md|pdf)",
    r"\b(?:rm|unlink|shred|truncate)\b[^|;&]*reference\.(?:md|pdf)",
    r"\b(?:Set-Content|Add-Content|Out-File|Clear-Content|Remove-Item|Move-Item|Copy-Item)\b"
    r"[^|;&]*reference\.(?:md|pdf)",
    r"reference\.(?:md|pdf)[^|;&]*\|\s*(?:tee|Set-Content|Out-File)",
    r"open\s*\(\s*[^)]*reference\.(?:md|pdf)[^)]*['\"][waxr]?\+?[wax]",  # python open(...,'w')
    r"\bwrite_text\b[^|;&]*reference\.(?:md|pdf)",
    r"\bgit\b[^|;&]*\b(?:checkout|restore|clean)\b[^|;&]*reference\.(?:md|pdf)",
]
WRITE_RE = [re.compile(p, re.IGNORECASE) for p in WRITE_PATTERNS]


def deny(reason):
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def is_protected(path):
    if not path:
        return False
    try:
        real = os.path.realpath(path)
    except OSError:
        real = os.path.abspath(path)
    if os.path.basename(real).lower() not in PROTECTED:
        return False
    return os.path.normcase(os.path.dirname(real)) == VAULT


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # 读不懂就放行，不阻塞正常工作

    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}

    if tool in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
        paths = [ti.get("file_path"), ti.get("notebook_path")]
        for e in ti.get("edits") or []:
            if isinstance(e, dict):
                paths.append(e.get("file_path"))
        for p in paths:
            if is_protected(p):
                deny(f"{REASON}\n（被拦下的写入目标：{p}）")

    elif tool in ("Bash", "PowerShell"):
        cmd = ti.get("command") or ""
        if re.search(r"reference\.(?:md|pdf)", cmd, re.IGNORECASE):
            for rx in WRITE_RE:
                if rx.search(cmd):
                    deny(
                        f"{REASON}\n（被拦下的命令：{cmd[:200]}）\n"
                        "读取是允许的：cat / head / sed -n / grep 都可以直接用。"
                    )

    sys.exit(0)


if __name__ == "__main__":
    main()
