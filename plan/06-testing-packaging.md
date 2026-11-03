# 06 — 测试（Load unpacked）、打包与体积预算

> **For agentic workers:** 先手工验收，再定打包命令与体积闸门。

**Goal:** 固化「如何测」「如何打 zip」「体积红线」；保证 ~24 MiB wasm 不会在不知情下膨胀失控。

**Architecture notes:** v0 交付物是 **Load unpacked 目录** `extension/`。可选打 `simplephoto-extension-<ver>.zip`（商店/分发以后再做）。不默认使用 `photocraft-web-boot` 分片。

Pinned PhotoCraft：`287352bf92d56817db9a510e506551f394a68ea4`

---

### Task 1: Load unpacked 测试剧本

- [ ] **Step 1: 干净加载**

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/bootstrap-submodule.sh
./scripts/build-web-assets.sh
# Chrome → Load unpacked → .../extension
```

Expected: 扩展出现；无 manifest 错误。

- [ ] **Step 2: 功能剧本（全部勾选才算过）**

- [ ] Action 打开编辑器，Loading 结束，UI 可见
- [ ] Open PNG；画布显示图像
- [ ] 简单编辑（如画笔/裁剪任一）后 Export PNG，下载文件可打开
- [ ] 刷新后 preferences 仍在（改一项验证）
- [ ] `editor/index.html?webgl` 可进入
- [ ] Service worker 控制台无未捕获异常（`chrome://extensions` → service worker 链接）
- [ ] 编辑器页 Console 无 CSP / WASM compile 错误

- [ ] **Step 3: 失败注入（可选，验证 stalled UI）**

临时重命名 `extension/editor/*_bg.wasm`，刷新页面，20s 内应出现 Reload 提示；再改回文件名。

Expected: 不无限假死而无文案。

---

### Task 2: 体积预算与检查脚本

官方 web 闸门：`packaging/web/package.sh` 默认 **24 MiB/文件**（CDN）。扩展包更宽松，但仍应监视 wasm。

**建议预算（v0）：**

| 项 | 预算 |
|---|---|
| `*_bg.wasm` | ≤ 28 MiB（软上限；超过需说明原因） |
| `extension/` 打包 zip | ≤ 35 MiB（软上限） |
| JS glue | 通常 ≪ 1 MiB |

**Files:**
- Create: `scripts/check-extension-size.sh`

- [ ] **Step 1: 写入检查脚本**

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EDITOR="$ROOT/extension/editor"
MAX_WASM=$((28 * 1024 * 1024))
MAX_ZIP=$((35 * 1024 * 1024))

wasm=$(echo "$EDITOR"/*_bg.wasm)
test -f "$wasm"
bytes=$(wc -c <"$wasm" | tr -d ' ')
echo "wasm=$wasm bytes=$bytes"
if [ "$bytes" -gt "$MAX_WASM" ]; then
  echo "error: wasm over soft budget $MAX_WASM" >&2
  exit 1
fi

art=$(ls "$ROOT"/dist/simplephoto-extension-*.zip 2>/dev/null | head -1 || true)
if [ -n "${art:-}" ]; then
  zbytes=$(wc -c <"$art" | tr -d ' ')
  echo "zip=$art bytes=$zbytes"
  if [ "$zbytes" -gt "$MAX_ZIP" ]; then
    echo "error: zip over soft budget $MAX_ZIP" >&2
    exit 1
  fi
fi
echo OK
```

```bash
chmod +x /Volumes/my/github/SimplePhoto/scripts/check-extension-size.sh
./scripts/check-extension-size.sh
```

Expected: 打印 `OK`（需先有构建产物）。

---

### Task 3: 打包 zip（非商店签名）

**Files:**
- Create: `scripts/package-extension.sh`
- Generate: `dist/simplephoto-extension-0.1.0.zip`（gitignore）

- [ ] **Step 1: 打包脚本**

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER=$(python3 -c "import json;print(json.load(open('$ROOT/extension/manifest.json'))['version'])")
OUT_DIR="$ROOT/dist"
NAME="simplephoto-extension-$VER"
./scripts/build-web-assets.sh
./scripts/check-extension-size.sh
rm -rf "$OUT_DIR/$NAME" "$OUT_DIR/$NAME.zip"
mkdir -p "$OUT_DIR/$NAME"
rsync -a --exclude '.DS_Store' "$ROOT/extension/" "$OUT_DIR/$NAME/"
cp "$ROOT/thirdparty/photocraft/LICENSE-MIT" "$OUT_DIR/$NAME/LICENSE-PHOTCRAFT-MIT"
cp "$ROOT/thirdparty/photocraft/NOTICE" "$OUT_DIR/$NAME/NOTICE-PHOTCRAFT"
(cd "$OUT_DIR" && zip -qr9 "$NAME.zip" "$NAME")
ls -lh "$OUT_DIR/$NAME.zip"
./scripts/check-extension-size.sh
```

- [ ] **Step 2: 运行并验证可再次 Load**

```bash
cd /Volumes/my/github/SimplePhoto
chmod +x scripts/package-extension.sh
./scripts/package-extension.sh
```

Expected: zip 可解压；Load unpacked 通过 Task 1 核心项。

- [ ] **Step 3: 提交脚本**

```bash
cd /Volumes/my/github/SimplePhoto
git add scripts/check-extension-size.sh scripts/package-extension.sh
grep -q '^dist/$' .gitignore || echo 'dist/' >> .gitignore
git add .gitignore
git commit -m "chore: add extension size gate and zip packaging scripts"
```

## Success criteria（06 完成）

- [ ] Task 1 功能剧本全绿
- [ ] `check-extension-size.sh` 对当前 pin 构建通过
- [ ] zip 可被解压后再次 Load unpacked
