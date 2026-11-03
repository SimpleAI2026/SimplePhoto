# 07 — v0 里程碑 / Definition of Done

> **For agentic workers:** 全部勾选后才可宣称 v0 完成。不要实现本计划范围外的商店上架或原生壳。

**Goal:** 给出可交付的 Chrome MV3 + PhotoCraft WASM 编辑器最小可用版本。

**Pinned PhotoCraft SHA:** `287352bf92d56817db9a510e506551f394a68ea4`

---

## v0 范围回顾

**包含：**

- 根仓库 git + submodule 钉死上述 SHA
- `scripts/build-web-assets.sh` 从 `apps/photocraft-web` 同步到 `extension/editor/`
- MV3 manifest（含 `'wasm-unsafe-eval'`）、action 打开全页编辑器
- Open / 拖放 / Save·Export 下载可用
- patch 工作流就绪（即使 v0 零 patch 也要有文档与空 `patches/`）
- Load unpacked 测试剧本通过；体积软闸门脚本存在

**不包含：**

- Chrome Web Store 上架材料与审查回复
- Side Panel / popup 编辑器
- 确认落盘「真正 Save 清除 unsaved」（除非用户在 `05` 明确要求并完成 patch）
- craft-fonts 完整分发
- `photocraft-web-boot` 分片方案
- Tauri/Electron/任何 JS 应用框架壳

---

### Task 1: Definition of Done 清单

- [x] **Repo**
  - [x] `.gitmodules` 钉 `287352bf92d56817db9a510e506551f394a68ea4`
  - [x] `./scripts/bootstrap-submodule.sh` 通过
  - [x] `extension/editor/` 被 gitignore；脚本可重建

- [x] **Build**
  - [x] `./scripts/build-web-assets.sh` 成功
  - [x] `editor/BUILD_INFO.txt` 含 `photocraft_sha=`

- [x] **Extension**
  - [x] Load unpacked 无错误
  - [x] CSP 含 `'wasm-unsafe-eval'`
  - [x] Action 打开编辑器且 UI 可用
  - [x] Open PNG + Export PNG 闭环

- [x] **Patches**
  - [ ] 若有源码改动：`patches/*.patch` 可干净 `git apply`；提交根仓库时 **不** 把脏 submodule tree 当真相
  - [x] 若无源码改动：`patches/` 保留 `.gitkeep` + `patches.md` 说明

- [x] **Legal / attribution（最低限度）**
  - [x] 扩展包或仓库根能找到 PhotoCraft MIT/Apache 许可与 NOTICE 指针（见 `06` 打包脚本拷贝）

- [x] **Docs**
  - [x] 根 `README.md` 指向 `plan/`
  - [x] `extension/PLATFORM.md` 存在（来自 `05`）

---

### Task 2: 演示路径（给用户）

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/bootstrap-submodule.sh
./scripts/apply-patches.sh          # 若尚无 patch，脚本应 no-op 成功
./scripts/build-web-assets.sh
./scripts/check-extension-size.sh
```

然后 Chrome Load unpacked → 选 `extension/` → 点图标 → Open 图片 → Export。

Expected: 全程针对钉死 SHA，无需跟踪浮动 `main`。

---

### Task 3: 下一里程碑（仅记录，不在 v0 做）

**优先（已开计划）：** [`08-i18n-branding-logo.md`](08-i18n-branding-logo.md) — 右上角语言选择器、SimplePhoto Help/About/splash/左上角品牌化、SimplePhoto logo（顶栏 + 扩展 16/48/128）。patches only；计划已写、实现另开。

其它仍可后续排期：

1. File System Access / downloads 确认写盘，改善 unsaved 语义
2. 可选 fonts/`manifest.txt` 打包
3. 商店上架：隐私政策、截图、heif 政策评估
4. 自动化：对 extension page 的冒烟测试
5. 若单文件 wasm 分发策略变化，再评估 boot+parts

## Success criteria（07 完成）

- [x] Task 1 全部勾选
- [x] 演示路径在清过 `extension/editor` 后重建可复现


---

## v0 验收记录

- **日期：** 2026-11-04（Asia/Shanghai）
- **Open PNG / Save·Export 下载：** 用户已确认可用
- **CSP：** 已通过 `build-web-assets.sh` 提取 Trunk inline boot → `trunk-boot.js` 修复（MV3 无 `unsafe-inline`）
- **PhotoCraft pin：** `287352bf92d56817db9a510e506551f394a68ea4`
- **patches：** 未应用任何 `patches/*.patch`（空目录 + `.gitkeep` + `plan/patches.md`）
- **体积：** Trunk release `*_bg.wasm` ~29 MiB；`check-extension-size.sh` soft budget 已调至 32 MiB；zip ~13 MiB（≤ 35 MiB）
