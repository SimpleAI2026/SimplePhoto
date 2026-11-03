# 02 — 构建流水线：从 submodule 产出扩展可消费资源

> **For agentic workers:** 逐步勾选。本任务不改 PhotoCraft 源码，只构建并同步产物。

**Goal:** 在本机从 `thirdparty/photocraft` @ `287352bf92d56817db9a510e506551f394a68ea4` 跑通 `trunk build --release`，把 `dist/web` 同步到 `extension/editor/`，供 MV3 扩展直接加载。

**Architecture notes:** 默认使用 **单文件** `photocraft-web` Trunk 产物（`apps/photocraft-web` → `dist/web`）。不默认运行 `packaging/web/package.sh`（boot+parts 是为 CDN 25 MiB 上限）。扩展包无该上传硬限。

**MV3 CSP 后处理：** Trunk 会在 `index.html` 写入内联 `<script type="module">`（import glue + `init()`）。Chrome MV3 `extension_pages` 的 `script-src` 只有 `'self' 'wasm-unsafe-eval'`，**禁止** `'unsafe-inline'`。因此 `scripts/build-web-assets.sh` 在 `cp dist/web → extension/editor/` 之后，必须把内联 module 抽出为 `trunk-boot.js`（多个则 `trunk-boot-N.js`），并改成 `<script type="module" src="./trunk-boot.js">`；若仍残留内联 `<script` 则脚本失败退出。勿改 `thirdparty/photocraft`。

## Global Constraints

- 工具：Rust stable（PhotoCraft 文档写 1.95+）、`wasm32-unknown-unknown`、`trunk`
- 构建目录：`thirdparty/photocraft`
- 输出同步到：`extension/editor/`（被 gitignore；每次构建刷新）
- `index.html` 中 URL 必须保持相对路径（Trunk.toml 已设 `public_url = "./"`）

---

### Task 1: 安装工具链并验证 wasm 目标

**Files:** 无仓库文件变更（工具装在机器上）

- [ ] **Step 1: 检查 Rust 与 wasm 目标**

```bash
rustc -V
rustup target list --installed | grep wasm32-unknown-unknown || rustup target add wasm32-unknown-unknown
```

Expected: 有稳定 Rust；`wasm32-unknown-unknown` 已安装。

- [ ] **Step 2: 安装 trunk（若缺失）**

```bash
command -v trunk || cargo install trunk --locked
trunk -V
```

Expected: `trunk` 可执行。

- [ ] **Step 3:（推荐）确认 submodule SHA**

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/bootstrap-submodule.sh
```

Expected: HEAD=`287352bf92d56817db9a510e506551f394a68ea4`。

---

### Task 2: 构建 photocraft-web 并检查产物

**Files:**
- Generate (gitignored): `thirdparty/photocraft/dist/web/index.html`
- Generate (gitignored): `thirdparty/photocraft/dist/web/photocraft-web-<hash>.js`
- Generate (gitignored): `thirdparty/photocraft/dist/web/photocraft-web-<hash>_bg.wasm`

- [ ] **Step 1: Trunk release 构建**

```bash
cd /Volumes/my/github/SimplePhoto/thirdparty/photocraft/apps/photocraft-web
trunk build --release
```

Expected: 退出码 0；写出 `../../dist/web/`。首次会下载匹配的 wasm-bindgen / wasm-opt，耗时长、占磁盘大（数 GB `target/`），属正常。

- [ ] **Step 2: 验证产物结构与相对 URL**

```bash
APP=/Volumes/my/github/SimplePhoto/thirdparty/photocraft/dist/web
ls -lh "$APP"
test -f "$APP/index.html"
# 恰好一个 _bg.wasm
wasm=$(echo "$APP"/*_bg.wasm)
test -f "$wasm"
# glue js 存在
stem=$(basename "$wasm" _bg.wasm)
test -f "$APP/$stem.js"
# 禁止根绝对路径（与 package.sh 同款检查）
if grep -Eq '(src|href)="/[^/]' "$APP/index.html"; then
  echo "FAIL: absolute URLs in index.html"; exit 1
fi
echo "OK wasm=$(du -h "$wasm" | awk '{print $1}')"
```

Expected: `OK wasm=…`（大约二十多 MiB 量级）；`index.html` 无 `src="/…"` 这类根绝对引用。

- [ ] **Step 3:（可选）本地静态服务器冒烟**

```bash
cd /Volumes/my/github/SimplePhoto/thirdparty/photocraft/dist/web
python3 -m http.server 8765
# 浏览器打开 http://127.0.0.1:8765/ 应出现 Loading 后进入编辑器
```

Expected: 页面最终去掉 `#photocraft_loading`；控制台无 WASM MIME/CSP 致命错误。

---

### Task 3: 同步脚本 `scripts/build-web-assets.sh`

**Files:**
- Create: `scripts/build-web-assets.sh`
- Modify: `extension/editor/`（生成，gitignore）

**Interfaces:**
- Consumes: submodule 源码 + trunk
- Produces: `extension/editor/` 下与 `dist/web` 一致的可加载静态树，外加 `BUILD_INFO.txt`

- [ ] **Step 1: 写入构建同步脚本**

将以下内容写入 `scripts/build-web-assets.sh`：

```bash
#!/usr/bin/env bash
# Build photocraft-web and sync static assets into extension/editor/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PC="$ROOT/thirdparty/photocraft"
APP_SRC="$PC/apps/photocraft-web"
DIST="$PC/dist/web"
DEST="$ROOT/extension/editor"
PIN_EXPECTED="287352bf92d56817db9a510e506551f394a68ea4"

cd "$PC"
HEAD="$(git rev-parse HEAD)"
if [[ "$HEAD" != "$PIN_EXPECTED" ]]; then
  echo "warning: photocraft HEAD=$HEAD (plan pin=$PIN_EXPECTED). Continue only if intentional." >&2
fi

if [[ "${1:-}" != "--skip-build" ]]; then
  command -v trunk >/dev/null || { echo "error: trunk not found" >&2; exit 1; }
  (cd "$APP_SRC" && trunk build --release)
fi

[[ -f "$DIST/index.html" ]] || { echo "error: $DIST/index.html missing" >&2; exit 1; }
if grep -Eq '(src|href)="/[^/]' "$DIST/index.html"; then
  echo "error: absolute URLs in $DIST/index.html" >&2
  exit 1
fi

rm -rf "$DEST"
mkdir -p "$DEST"
# 复制静态站（含 index.html、*.js、*_bg.wasm 及 trunk 其它资源）
cp -R "$DIST"/. "$DEST"/
# 保留目录可被 git 跟踪的占位在清理后消失；构建后不需要 .gitkeep

{
  echo "photocraft_sha=$HEAD"
  echo "built_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "source=apps/photocraft-web trunk build --release"
  ls -lh "$DEST"/*_bg.wasm 2>/dev/null | awk '{print "wasm="$0}'
} | tee "$DEST/BUILD_INFO.txt"

echo "synced -> $DEST"
```

```bash
chmod +x /Volumes/my/github/SimplePhoto/scripts/build-web-assets.sh
```

- [ ] **Step 2: 运行同步**

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/build-web-assets.sh --skip-build   # 若 Task 2 已构建
# 或全量：./scripts/build-web-assets.sh
ls -la extension/editor | head
test -f extension/editor/index.html
test -f extension/editor/BUILD_INFO.txt
```

Expected: `extension/editor/index.html` 存在；`BUILD_INFO.txt` 含 `photocraft_sha=`。

- [ ] **Step 3: 提交脚本（不提交 editor 产物）**

```bash
cd /Volumes/my/github/SimplePhoto
git add scripts/build-web-assets.sh
git status
# 确认 extension/editor 下的 wasm/js 被 ignore
git check-ignore -v extension/editor/index.html || true
git commit -m "chore: add build-web-assets.sh to sync photocraft-web into extension/editor"
```

Expected: 仅脚本进版本库；大 wasm 被 ignore。

## Success criteria（02 完成）

- [ ] `trunk build --release` 在 `apps/photocraft-web` 成功
- [ ] `extension/editor/` 含相对路径 `index.html` + glue JS + `*_bg.wasm`
- [ ] `scripts/build-web-assets.sh` 可重复执行
- [ ] 构建产物未误提交到 git
