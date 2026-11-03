# PhotoCraft patch 工作流

> **硬规则：** 永远不要把「脏的 `thirdparty/photocraft` 工作区」当作长期真相源。根仓库只提交 `patches/*.patch` 与钉死的 submodule **gitlink SHA**。需要改 PhotoCraft 时：改 → 生成 patch → reset submodule → 用脚本 apply。

**Pinned baseline SHA:** `287352bf92d56817db9a510e506551f394a68ea4`

对应计划步骤：`01`（钉 SHA）、`05`（何时需要改）、`02`（apply 后重建）。

---

## 目录约定

```text
SimplePhoto/
  patches/
    0001-short-description.patch
    0002-another.patch
  scripts/
    apply-patches.sh
    refresh-patch.sh
  thirdparty/photocraft/       # submodule @ pinned SHA，apply 后可暂时有本地 diff
```

命名：四位序号 + 短英文短横线描述，方便按序 `git apply`。

---

## 何时需要 patch

仅当扩展沙箱 / `chrome.*` 迫使行为变化，且 **扩展侧 JS bridge 不够** 时，例如：

- `apps/photocraft-web/src/web.rs` 的 `download()` 必须调用扩展桥
- Save 对话框需要 File System Access 才能清除 unsaved
- 需要向 `Services` 注入扩展专有 inbox 钩子

**不要**为纯 CSS/欢迎页/manifest 去 patch PhotoCraft。

**SimplePhoto 例外（post-v0 / `08`）：** 允许用 patch 改 photocraft **UI chrome** 以适配扩展产品壳——包括顶栏右上角语言选择器（复用现有 `interface.language` / i18n，不新建 locale 系统）、Help / About / splash 的 SimplePhoto 品牌文案与链接、以及 `panels/brand.rs` 顶栏图标 `include_bytes!`。扩展侧 `extension/icons/` 与根仓库 `branding/` 资产 **不** 进 submodule。仍须最小 diff、可 `git apply`、不把脏 submodule 当真相源。详见 [`08-i18n-branding-logo.md`](08-i18n-branding-logo.md)。

---

## 编写第一个 patch

- [ ] **Step 1: 确认干净基线**

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/bootstrap-submodule.sh
git -C thirdparty/photocraft status -sb
git -C thirdparty/photocraft rev-parse HEAD
# 必须是 287352bf92d56817db9a510e506551f394a68ea4 且干净
```

- [ ] **Step 2: 在 submodule 内做最小改动**

只改必要文件；遵守 PhotoCraft `AGENTS.md`（Never break wasm；无 unwrap 等）。

```bash
cd /Volumes/my/github/SimplePhoto/thirdparty/photocraft
# 编辑… 例如 apps/photocraft-web/src/web.rs
cargo xtask wasm   # 若改了 L0–L6 或 web 依赖路径
```

- [ ] **Step 3: 生成 patch 文件**

```bash
cd /Volumes/my/github/SimplePhoto/thirdparty/photocraft
git diff > ../../patches/0001-extension-download-bridge.patch
wc -l ../../patches/0001-extension-download-bridge.patch
```

Expected: patch 非空；路径相对 submodule 根。

- [ ] **Step 4: 复位 submodule 并验证可应用**

```bash
cd /Volumes/my/github/SimplePhoto
git -C thirdparty/photocraft reset --hard 287352bf92d56817db9a510e506551f394a68ea4
./scripts/apply-patches.sh
git -C thirdparty/photocraft status -sb
```

Expected: apply 成功；status 显示预期改动，无冲突。

- [ ] **Step 5: 根仓库只提交 patch**

```bash
cd /Volumes/my/github/SimplePhoto
git add patches/0001-extension-download-bridge.patch scripts/apply-patches.sh
git commit -m "patch: extension download bridge for photocraft-web"
# 不要把 submodule 工作区内容当普通文件提交；gitlink SHA 保持原 pin
git submodule status
```

---

## 脚本内容（创建后提交）

### `scripts/apply-patches.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PC="$ROOT/thirdparty/photocraft"
PIN="287352bf92d56817db9a510e506551f394a68ea4"
cd "$PC"
HEAD=$(git rev-parse HEAD)
if [[ "$HEAD" != "$PIN" ]]; then
  echo "error: photocraft HEAD=$HEAD, expected $PIN (refuse to apply on wrong base)" >&2
  exit 1
fi
git reset --hard "$PIN"
shopt -s nullglob
patches=("$ROOT"/patches/*.patch)
if (( ${#patches[@]} == 0 )); then
  echo "no patches to apply"
  exit 0
fi
for p in "${patches[@]}"; do
  echo "apply $(basename "$p")"
  git apply --index "$p" || git apply "$p"
done
echo "patches applied on $PIN"
git status -sb
```

### `scripts/refresh-patch.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NUM="${1:?usage: refresh-patch.sh 0001}"
PC="$ROOT/thirdparty/photocraft"
out=$(ls "$ROOT"/patches/${NUM}-*.patch 2>/dev/null | head -1 || true)
if [[ -z "$out" ]]; then
  echo "error: no patches/${NUM}-*.patch" >&2
  exit 1
fi
cd "$PC"
git diff > "$out"
echo "refreshed $out ($(wc -l <"$out") lines)"
```

更稳妥的再生流程：

1. `git reset --hard $PIN`
2. `git apply` 除待刷新外的其它 patch
3. 手工重做或继续编辑
4. `git diff > patches/000N-….patch`
5. 再全量 `apply-patches.sh` 验证

---

## 升级 PhotoCraft pin 时

1. 在干净树上把 submodule checkout 到新 SHA
2. 尝试 `git apply` 旧 patches；冲突则在新树上手工重放并 refresh
3. 更新本文件与 `scripts/*.sh` / `plan/README.md` 中的 PIN 字符串
4. `trunk build` + 扩展回归（`06`）
5. 根仓库提交：**新的 gitlink SHA** + 更新后的 patches

---

## 禁止事项

- 在根仓库 `git add -f` submodule 内部跟踪文件来「固化修改」
- 提交未记录在 `patches/` 的本地 submodule commit（除非另开 fork——本计划不采用）
- 把 `target/`、`dist/web` 放进 patch

## Success criteria

- [ ] `apply-patches.sh` 在干净 pin 上可重复得到一致结果（先 hard reset 再 apply）
- [ ] 协作者只需：`submodule update` + `apply-patches.sh` + `build-web-assets.sh`
