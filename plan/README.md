# SimplePhoto Chrome 扩展实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `/Volumes/my/github/SimplePhoto` 交付一个可 `Load unpacked` 的 Chrome Manifest V3 扩展，内嵌 PhotoCraft `photocraft-web` 的 WASM 静态构建，支持打开/编辑/导出图片。

**Architecture:** 将现有 `apps/photocraft-web` 的 Trunk 静态产物（`index.html` + wasm-bindgen glue + `*_bg.wasm`）原样装入扩展的 extension page（`chrome-extension://…/editor/`），外层只做极薄的 MV3 shell（`manifest.json`、action 打开编辑器标签页、CSP、可选 background bridge）。PhotoCraft 通过 git submodule 钉在 `287352bf92d56817db9a510e506551f394a68ea4`；若扩展沙箱或 `chrome.*` API 迫使平台服务改动，用 `patches/` 中的 patch 文件改 submodule，再 `git apply`，永不把脏 submodule 当作真相源。

**Tech Stack:** Chrome MV3、PhotoCraft Rust/`wasm32-unknown-unknown`、Trunk、wasm-bindgen、eframe/wgpu（WebGPU→WebGL2）、可选 `chrome.downloads` / File System Access。

**Pinned PhotoCraft SHA:** `287352bf92d56817db9a510e506551f394a68ea4`（已在本机 `thirdparty/photocraft` 验证）

## Global Constraints

- 计划与实现文档路径固定在 `SimplePhoto/plan/`（覆盖任何 docs/superpowers 默认位置）
- PhotoCraft：`thirdparty/photocraft`，远程 `git@github.com:storytold/photocraft`，钉住 `287352bf92d56817db9a510e506551f394a68ea4`
- 遵守 PhotoCraft `AGENTS.md`：Never break wasm；禁止引入 Tauri/Electron/webview；L0–L6 保持 `cargo xtask wasm` 可过
- 对 submodule 的永久改动只以 `patches/*.patch` 形式存在；工作区脏改仅用于生成/刷新 patch
- 计划正文用简体中文；命令、路径、crate 名、API 名保持英文
- 本计划阶段只写文档；不在本步实现扩展、不 `git init`、不 `git submodule add`（这些是执行 `01` 时由用户/执行者完成）

## 目标 / 非目标

### 目标（v0）

- 用户可在 Chrome 中 Load unpacked，点击扩展图标打开全页编辑器
- 编辑器实际跑的是 PhotoCraft `photocraft-web`（同一套 `PhotocraftApp`）
- File → Open（`<input type=file>` / rfd）、拖放打开、Save/Export 触发浏览器下载均可工作
- 构建脚本可从 submodule 产出扩展可消费的静态资源并拷入 `extension/editor/`
- patch 工作流文档化且可复现

### 非目标（v0 不做）

- Chrome Web Store 上架、签名发布流水线（可在后续里程碑）
- 改写 PhotoCraft 为「原生扩展专用」UI 框架或引入 JS/TS 应用壳
- 桌面原生 photocraft / Tauri / Electron
- TCP control server / MCP（浏览器不能 listen；web 构建本就没有）
- 完整 craft-fonts 分发（可选后续；web 本就不嵌入 craft-fonts）
- 用 `photocraft-web-boot` 分片方案作为扩展默认路径（那是为 CDN 单文件 25 MiB 上限；扩展包无此硬限，优先单文件 Trunk 产物）

## 下一里程碑（post-v0）

v0 已完成后的三项计划见 [`08-i18n-branding-logo.md`](08-i18n-branding-logo.md)：（1）patches：顶栏右上角语言选择器（复用现有 `interface.language` i18n）；（2）patches：Help / About / splash / 左上角标改为 SimplePhoto 品牌；（3）生成 SimplePhoto logo，用于顶栏图标与 `extension/icons` 16/48/128。尚未实现——只更新计划文档。

## 架构决策（摘要）

1. **Extension page 直接托管静态站，而不是跨域 iframe 嵌远程站。** `chrome-extension://` 是 secure context，WebGPU/剪贴板与现有 web shell 假设一致；也避免第三方存储分区问题（见 `packaging/web/README.md` iframe 说明）。
2. **默认消费 `trunk build --release`（`dist/web`），不默认走 `packaging/web/package.sh` 的 boot+parts。** 扩展无 Cloudflare 25 MiB 单文件上传限制；单 `.wasm` 更简单，路径与 MIME 更直观。若将来 CRX/商店策略需要拆分，再评估 boot 方案。
3. **薄壳 + 现有 `Services` web 实现优先。** `apps/photocraft-web/src/web.rs` 已提供 rfd 打开、`<a download>` 写出、localStorage 偏好、IndexedDB presets；v0 先验证这些在 extension page 是否足够。只有确认不够（例如需要「另存为真实路径」或 `chrome.downloads` 确认写盘）时才写 patch。
4. **改 PhotoCraft → patch 文件。** 见 `patches.md`。

## 推荐仓库布局（执行后）

```text
SimplePhoto/
  README.md
  .gitignore
  .gitmodules
  plan/                          # 本计划（已存在）
  patches/                       # 对 photocraft 的 patch（按需）
  scripts/
    build-web-assets.sh          # 从 submodule 构建并同步到 extension/editor
    apply-patches.sh
    refresh-patch.sh
  extension/
    manifest.json
    background.js                # 可选：打开编辑器、downloads bridge
    icons/
    editor/                      # 构建产物：index.html + *.js + *_bg.wasm（gitignore 大文件或整目录）
  thirdparty/
    photocraft/                  # submodule @ 287352bf92d56817db9a510e506551f394a68ea4
```

## 如何阅读步骤

按编号顺序执行。每个 `0N-*.md` 含 Goal、涉及文件、带复选框的命令级步骤与成功标准。

| 文件 | 内容 |
|---|---|
| [`00-analysis.md`](00-analysis.md) | 对真实树的调研结论、约束与风险 |
| [`01-repo-bootstrap.md`](01-repo-bootstrap.md) | 根仓库 git、submodule 钉 SHA、布局、gitignore |
| [`02-build-pipeline.md`](02-build-pipeline.md) | 从 submodule 产出扩展可消费的 wasm/web 资源 |
| [`03-mv3-scaffold.md`](03-mv3-scaffold.md) | Manifest V3、CSP（`wasm-unsafe-eval`）、权限、入口 |
| [`04-integrate-ui.md`](04-integrate-ui.md) | 把 photocraft-web 装进扩展 UI shell |
| [`05-platform-bridges.md`](05-platform-bridges.md) | 打开/保存/剪贴板与扩展 vs 静态宿主差异 |
| [`06-testing-packaging.md`](06-testing-packaging.md) | Load unpacked、打包、体积预算 |
| [`07-v0-milestone.md`](07-v0-milestone.md) | v0 完成定义与验收清单 |
| [`08-i18n-branding-logo.md`](08-i18n-branding-logo.md) | 下一里程碑：右上角语言选择器、SimplePhoto Help/About/splash 品牌化、logo（UI + 扩展 16/48/128）；patches only |
| [`patches.md`](patches.md) | patch 的编写、存放、应用、再生 |

## 执行方式

计划写完后，实现阶段可选：

1. **Subagent-Driven（推荐）** — 每任务新 subagent，任务间审查  
2. **Inline Execution** — 本会话用 executing-plans 批量执行并设检查点  

先完成 `01` 再碰构建与 manifest。
