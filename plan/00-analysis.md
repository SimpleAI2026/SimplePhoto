# 00 — PhotoCraft 现状分析（基于本机树）

> 分析对象：`/Volumes/my/github/SimplePhoto/thirdparty/photocraft`  
> 验证 SHA：`287352bf92d56817db9a510e506551f394a68ea4`（`git rev-parse HEAD` 与预期一致）  
> 远程：`git@github.com:storytold/photocraft`  
> 分支状态：`main...origin/main`（分析时工作区干净）

## 1. 产品与技术栈（来自 `AGENTS.md`）

- **纯 Rust** 图像编辑器；**禁止** Tauri / Electron / webview / JS·TS UI 框架。
- 桌面：egui/eframe + wgpu；Web：**同一套 Rust → WebAssembly**（trunk + wasm-bindgen）。
- 分层 `crates/` L0–L6；`cargo xtask layers` 强制依赖方向。
- **Never break wasm**：L0–L6 必须 `cargo check --target wasm32-unknown-unknown`（`cargo xtask wasm`）。文件系统相关代码须 `cfg(not(target_arch = "wasm32"))` 或走 platform services。
- 许可：MIT OR Apache-2.0（`LICENSE-MIT` / `LICENSE-APACHE`）；品牌资源有单独限制（`NOTICE`、`docs/brand/LICENSE-brand.txt`）。扩展分发需保留 NOTICE/ATTRIBUTION 义务。

## 2. Web 应用入口（真实路径）

### `apps/photocraft-web`

| 文件 | 作用 |
|---|---|
| `apps/photocraft-web/Cargo.toml` | crate `photocraft-web`；描述为 eframe web runner，WebGPU + WebGL2 fallback；feature `heif` |
| `apps/photocraft-web/Trunk.toml` | `dist = "../../dist/web"`，`public_url = "./"`，`filehash = true`；serve `127.0.0.1:8765` |
| `apps/photocraft-web/index.html` | canvas `#photocraft_canvas`；Trunk rust link：`data-cargo-profile="wasm-release"`、`data-cargo-features="heif"`、`data-wasm-opt="z"`；**页面自身无 `<script>`**（测试强制） |
| `apps/photocraft-web/src/main.rs` | wasm 调 `web::start()`；差异说明：无 TCP control、异步 file dialog、download 保存、drop → inbox |
| `apps/photocraft-web/src/web.rs` | 组装 `Services`、eframe web runner、拖放、localStorage prefs、IndexedDB presets、`<a download>` |
| `apps/photocraft-web/src/indexed_presets.rs` / `preset_bridge.rs` | 浏览器预设持久化 |

**URL 查询标志**（`main.rs` / `packaging/web/README.md`）：

- `?cpu` → 强制 CPU canvas（等同 `PHOTOCRAFT_CPU_CANVAS=1`）
- `?webgl` → 强制 WebGL2（不用 WebGPU）

### `apps/photocraft-web-boot`

- 小 boot WASM：读取 `./app/parts.txt`，拉取 gzip 分片、拼接/解压，再调用 `./app/photocraft-web.js` 的 default export。
- 目的：绕过 **静态宿主单文件 ~25 MiB 上限**（Cloudflare Pages/Workers；issue #198 / #5302）。
- Trunk 输出：`dist/web-boot`。

### 打包：`packaging/web/`

| 文件 | 作用 |
|---|---|
| `package.sh` | 先 `trunk build --release` web + boot；把 app wasm gzip 后按 `PART_BYTES`（默认 20 MiB）切开；最大文件闸门默认 **24 MiB**（`PHOTOCRAFT_WEB_MAX_FILE_BYTES`） |
| `_headers` / `.htaccess` / `nginx.conf` | MIME（`application/wasm`）、缓存、示例服务器配置 |
| `README.md` | 宿主要求、iframe 嵌入、字体、相对 URL |

**对扩展的含义：** Cloudflare 单文件上限 **不适用于** Chrome 扩展包。Chrome Web Store 扩展上限远大于 ~24 MiB wasm。因此 v0 **优先直接使用 `dist/web`（单文件 wasm）**，不必默认引入 boot/parts 复杂度。

## 3. 构建与体积

- Profile：`[profile.wasm-release]`（根 `Cargo.toml`）：fat LTO、整体偏 size；像素路径部分 crate 保 `opt-level = 3`。
- 文档记载未 gzip 的 app wasm 约 **23.9 MiB**（`packaging/web/README.md` 表）；CI 有 web build + size gate。
- 命令（`docs/development.md` › Web build）：

```bash
rustup target add wasm32-unknown-unknown
# trunk: brew install trunk  或  cargo install trunk --locked
cd apps/photocraft-web
trunk build --release    # → ../../dist/web
trunk serve --release    # http://127.0.0.1:8765
```

- 官方打包：`packaging/web/package.sh`（可选 `PHOTOCRAFT_WEB_FONTS_DIR`）。
- Web **从不嵌入 craft-fonts**（会撑破 24 MiB 闸门）；字体靠站点旁 `fonts/manifest.txt` 按需 fetch。

## 4. Platform services / 文件系统如何适配 wasm

核心抽象：`crates/ui-egui/src/services.rs` 的 `Services`（由 app binary 注入，保持 ui-egui 无直接 I/O 依赖）。

Web 壳（`apps/photocraft-web/src/web.rs` 的 `services()`）已接线：

| 能力 | Web 行为 |
|---|---|
| `import` / `export` | 调 `photocraft_io` |
| `file_dialog` Open | `rfd::AsyncFileDialog` → `Contents` / `ContentsMany`（字节，非路径） |
| `file_dialog` Folder | 直接 `None`（浏览器目录句柄无法当路径给引擎） |
| `file_dialog` Save | 无系统另存对话框；立刻 `SaveTo(suggested 文件名)` |
| `write` | 构造 Blob + `<a download>`；`write_unconfirmed: true`（下载可取消，文档仍算未保存，#4962） |
| prefs | `localStorage` key `photocraft.preferences` |
| presets | IndexedDB（`indexed_presets`） |
| drop | 异步读入 `inbox` / `place_inbox` |
| `screen_pick` | EyeDropper API（有则用） |
| 桌面专有 | `save_file` 路径回写、`file_stamp`、`automation_*`、TCP control 等均为 `None`/不适用 |

`crates/ui-egui/src/file_dialog.rs`：异步 Open/Save 状态机；web 的 Save 答案是「下载名」，没有可记住的目录。

**扩展含义：** 在 extension page 中，上述 web 路径大概率可直接工作。需要 patch 的典型场景：

1. 想用 `chrome.downloads` 或 File System Access API 做「确认落盘 / 回写原文件」以清除 unsaved 状态  
2. 想暴露 `chrome.storage` 替代或补充 localStorage  
3. CSP / 扩展 API 导致 `rfd` 或 blob download 异常  
4. 需要从扩展 action / 右键菜单把本地文件字节注入 `inbox`（可通过 content-free 的 background → editor `postMessage`，不一定改 Rust）

## 5. 浏览器托管文档要点

摘自 `packaging/web/README.md` / `docs/development.md`：

- 所有资源相对 URL（`public_url = "./"`）→ 可放在扩展子路径 `editor/`
- `.wasm` 必须 `application/wasm`（扩展本地加载由 Chrome 按扩展资源处理，一般可行；若异常需在计划测试步验证）
- HTTPS 或 localhost 才是 secure context；**`chrome-extension://` 也是 secure context** → WebGPU/clipboard 预期可用
- 不需要 COOP/COEP（无 SharedArrayBuffer 硬需求）
- iframe 嵌入需要 `allow-downloads` 等；**本方案避免用沙箱 iframe 嵌编辑器**，直接用 extension page

## 6. Chrome MV3 约束（推断并在实现中验证）

| 约束 | 对 SimplePhoto 的影响 |
|---|---|
| MV3 `extension_pages` CSP 默认无 eval | 必须显式加 `'wasm-unsafe-eval'` 才能实例化 WASM |
| 不能 `'unsafe-eval'` | 与 PhotoCraft「无自有 JS、仅 wasm-bindgen glue」兼容 |
| 大资源进 CRX | ~24 MiB wasm 可接受；应用 `web_accessible_resources` 仅当 content script 要读（v0 不需要） |
| Service worker 无 DOM / 无持久 WASM 重型 UI | 编辑器必须在 **扩展页面/标签页**，不是在 SW 里跑 egui |
| 权限最小化 | v0：可无 host 权限；若用 `chrome.downloads` 再加 `downloads`；剪贴板图像可能需 `clipboardRead`/`clipboardWrite`（先测 eframe 内置 clipboard） |
| 远程代码禁止 | 所有 wasm/js 必须打进包内，禁止运行时拉远程业务代码 |

## 7. 风险与未知项

| ID | 风险 | 缓解 |
|---|---|---|
| R1 | 扩展 CSP 漏配导致 WASM 无法编译 | `03` 写死 CSP；控制台看具体报错 |
| R2 | `<a download>` 在 extension page 行为与普通 https 页不同 | `05`/`06` 实测；必要时改 `write` 走 `chrome.downloads.download({ url: blobUrl })`（可能需薄 JS bridge + 可选 Rust patch） |
| R3 | WebGPU 在部分 GPU/驱动上的扩展进程不稳定 | 提供 `editor/index.html?webgl` 入口或 UI 切换 |
| R4 | 首次加载 ~24 MiB 卡住「Loading…」 | 保留原生 stalled CSS 提示；可选后续再引入 boot 分片 |
| R5 | submodule 构建需 Rust + trunk + 较长时间/磁盘 | `02` 文档化工具链；CI 可缓存 `target` |
| R6 | HEIF feature / 编解码体积与专利顾虑 | 官方 web 默认带 `heif`；扩展可先保持一致，商店政策再评估 |
| R7 | 许可与 ATTRIBUTION 必须随扩展分发 | `01`/`07` 拷贝 NOTICE、LICENSE、ATTRIBUTION 片段 |
| R8 | 脏 submodule 被误提交 | `patches.md` + gitignore 纪律；`01` 不在计划阶段 init 之外的提交策略 |

### 需要用户拍板的未知项（非阻塞写计划，阻塞 v0 部分验收）

1. **扩展 UI 形态：** 仅新标签页全屏编辑器（推荐 v0），还是 Side Panel / 独立 popup（popup 对 ~24 MiB + egui 不合适）？  
2. **是否在 v0 追求「Save 回写原文件」**（需 File System Access 或 downloads + 用户手势），还是接受现有「每次 Export/Save 都是下载、文档仍可能标 unsaved」的 web 语义？  
3. **商店上架是否在 scope：** 影响是否保留 heif、隐私政策、体积与审查材料。

## 8. 架构建议（核实后维持）

**维持用户给定方向并细化：**

> 把现有 `photocraft-web` 静态构建打进 Chrome MV3 **extension page**，外层只做薄 shell；仅在扩展沙箱或 `chrome.*` 迫使平台服务变更时，用 `patches/` 修改 PhotoCraft。

不建议：把编辑器放进沙箱 iframe、在 service worker 跑 WASM、或把 PhotoCraft 改成 JS 壳。
