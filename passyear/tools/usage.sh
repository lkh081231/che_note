#!/bin/sh
# 截 VS Code 左栏 ACCOUNT & USAGE 面板，裁成一小块 PNG —— 每次核额度只花 ~200 image token。
# 用法：sh tools/usage.sh [输出路径]   默认 $TEMP/cc_usage.png
OUT="${1:-$TEMP/cc_usage.png}"
FULL="$TEMP/cc_usage_full.jpg"
uvx screenshot-feedback-hook-mcp capture --monitor 1 --out "$FULL" >/dev/null 2>&1 || exit 1
C:/Python314/python.exe - "$FULL" "$OUT" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1]); w, _ = im.size
# 面板固定在左栏；按宽度比例定位，换分辨率也不用改
im.crop((int(w*.040), int(w*.147), int(w*.275), int(w*.240))).save(sys.argv[2])
PY
echo "$OUT"
