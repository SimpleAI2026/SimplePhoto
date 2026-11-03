# 08 — i18n 右上角语言选择器、SimplePhoto 品牌化与 Logo

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **本文件只指导实现；当前阶段仅提交本计划文档，不要生成 logo 图像、不要写 patch、不要改 `thirdparty/photocraft` 工作区并当作真相源。**

**Goal:** 在 v0 之后用 `patches/*.patch` 为扩展内嵌的 PhotoCraft UI 增加右上角语言选择器、将 Help / About / splash / 左上角品牌标改为 SimplePhoto，并在根仓库生成 SimplePhoto logo 供 UI 与 Chrome 扩展图标使用。

**Architecture:** PhotoCraft 已有完整 i18n（`crates/ui-egui/src/i18n.rs` + `i18n/*.tsv`，偏好 `interface.language`，Preferences 内已有 Language 下拉）。本里程碑 **不新建 locale 系统**；只在顶栏右上角（`title_bar.rs` 中 workspace / search / appearance 控件旁）增加选择器，经 `prefs.set` 写 `interface.language`。品牌文案与链接集中改 `links.rs`、`shell_commands.rs`、About / splash / title bar 字符串；左上角标来自 `panels/brand.rs` 的 `include_bytes!(…app-icon…)`。所有对 photocraft 的永久改动只进 `patches/`；扩展侧 16/48/128 图标只改根仓库 `extension/icons/`（及可选 `branding/` 源图），**不**进 submodule。

**Tech Stack:** PhotoCraft `ui-egui` / `photocraft_engine` prefs、现有 `tl!` / TSV、`scripts/apply-patches.sh` + `build-web-assets.sh`、Chrome MV3 `extension/icons/`。

**Pinned PhotoCraft SHA:** `287352bf92d56817db9a510e506551f394a68ea4`

## Global Constraints

- photocraft 改动 **仅** 以 `patches/*.patch` 形式提交；执行时：干净 pin → 编辑 → `git diff` 生成 patch → `reset --hard` pin → `./scripts/apply-patches.sh` 验证；禁止把脏 submodule 当真相源（见 `plan/patches.md`）
- 本步允许为 SimplePhoto 做 branding / i18n chrome 类 patch（已在 `patches.md` 注明），仍须最小 diff、不破坏 wasm
- 不修改已钉死的 submodule gitlink SHA（除非另开升级 pin 任务）
- 本计划文档阶段：**不**生成 logo PNG/SVG 成品、**不**创建 `patches/*.patch`、**不**改 `thirdparty/photocraft` 跟踪内容
- 计划正文简体中文；路径、命令、crate、API、patch 文件名保持英文

## 开放决策（执行前由产品确认；未确认前 patch 用占位 URL / 文案）

| 项 | 默认占位（可改） | 说明 |
|---|---|---|
| SimplePhoto Website URL | `https://github.com/linkxzhou/SimplePhoto`（或用户指定站点） | 替换 `help.website` / splash「PhotoCraft website」 |
| SimplePhoto GitHub URL | 同上仓库根 | 替换 `help.github` |
| Report Issue URL | `…/issues` | 替换 `help.reportIssue` |
| Discord / ArtCraft Website 行 | **建议保留并改指向**，或 **删除行** | 用户截图含 Discord / PhotoCraft Website / ArtCraft Website / GitHub / Report Issue / About；SimplePhoto 是否仍挂 ArtCraft 社区需确认 |
| About 文案 | 「SimplePhoto — PhotoCraft-powered local image editor」+ 上游致谢 | 须保留 PhotoCraft / ArtCraft 许可与 NOTICE 指针 |

---

## 文件与产物地图（执行时）

| 路径 | 职责 |
|---|---|
| `patches/0001-top-right-language-selector.patch` | 顶栏右上角语言选择器 → `prefs.set` `interface.language` |
| `patches/0002-simplephoto-help-about-splash-branding.patch` | Help 标签/URL、About、splash、相关 PhotoCraft 字符串 → SimplePhoto |
| `patches/0003-simplephoto-titlebar-icon.patch` | `brand.rs`（及必要资源路径）改用 SimplePhoto 图标字节 |
| `branding/simplephoto-logo.svg`（建议） | 源 logo（执行时生成；本计划步不生成） |
| `branding/simplephoto-logo-1024.png`（建议） | 栅格母版，再导出 UI / 扩展尺寸 |
| `extension/icons/icon{16,48,128}.png` | Chrome `manifest.json` / action 图标（根仓库） |
| photocraft 内供 `include_bytes!` 的 PNG | 由 patch 指向或随 patch 引入的资产路径（见 Task 4；**不要**把 ArtCraft `docs/brand/` 商标当 SimplePhoto logo） |

### 已定位的 photocraft 钩子（pin `287352bf…`）

- **i18n 运行时：** `crates/ui-egui/src/i18n.rs`，目录 `crates/ui-egui/src/i18n/*.tsv`；偏好键 `interface.language`（`auto` 或语言码）；Preferences › Interface 已有 Language 下拉（`prefs/prefs_ui/fields.rs`）
- **顶栏右区控件：** `crates/ui-egui/src/panels/title_bar.rs`（workspace 下拉、search、appearance 循环；语言选择器加在此簇旁）
- **Help 命令表：** `crates/engine/src/shell_commands.rs` 中 `help.discord` / `help.website` / `help.artcraftWebsite` / `help.github` / `help.reportIssue` / `help.about` 等
- **Help URL：** `crates/ui-egui/src/links.rs`（`DISCORD`、`APP_PAGE`、`ARTCRAFT_WEBSITE`、`GITHUB`、`ISSUES`、`COMMANDS`）
- **菜单顺序：** `crates/ui-egui/src/menus/items.rs`（及 `menu_catalog` / `UI_COMMANDS` 相关）
- **About：** `crates/ui-egui/src/dialogs.rs`（及 `dialogs/` 下 About 实现；执行时精确定位 `DialogKind::About`）
- **Splash：** `crates/ui-egui/src/canvas/start_screen.rs`
- **左上角品牌标：** `crates/ui-egui/src/panels/brand.rs` — `include_bytes!("../../../../assets/app-icon/hicolor/128x128/apps/ai.storyteller.photocraft.png")`
- **标题栏其它 PhotoCraft 文案：** `title_bar.rs` / native app 菜单等；执行时 `rg "PhotoCraft"` 扫 UI 字符串，扩展 web 路径优先改用户可见 chrome

若执行时路径漂移：在 submodule 内 `rg`「Help menu / prefs / splash / brand mark」，把本表补全后再写 patch。

---

### Task 1: 调研确认与开放决策落地

**Files:**
- Modify（仅笔记）：本文件底部「执行记录」小节（实现阶段追加）
- 不修改：`thirdparty/photocraft`（只读 `rg` / `sed`）

- [ ] **Step 1: 确认顶栏插入点**

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/bootstrap-submodule.sh
rg -n "workspace|search|appearance|ICON_SLOT" thirdparty/photocraft/crates/ui-egui/src/panels/title_bar.rs
```

Expected: 看清右区控件绘制顺序；语言控件应紧邻 appearance（或 search 与 appearance 之间），RTL 时仍落在「逻辑右上 / 控件簇」一侧。

- [ ] **Step 2: 确认 prefs 写入路径**

```bash
rg -n "interface.language" thirdparty/photocraft/crates/ui-egui/src/menus/invoke.rs \
  thirdparty/photocraft/crates/engine/src/prefs/validate.rs \
  thirdparty/photocraft/crates/ui-egui/src/prefs/prefs_ui/fields.rs
```

Expected: 切换语言应等价于 `prefs.set` + `{"values":{"interface.language":"<code>"}}`（与 native Language 菜单、`invoke.rs` 一致），并触发现有 `i18n::set_current` / 重绘路径。

- [ ] **Step 3: 列出 Help / About / splash 需改字符串与 URL**

```bash
rg -n "help\.(discord|website|artcraftWebsite|github|reportIssue|about)" \
  thirdparty/photocraft/crates/engine/src/shell_commands.rs \
  thirdparty/photocraft/crates/ui-egui/src/links.rs \
  thirdparty/photocraft/crates/ui-egui/src/menus/items.rs
rg -n "PhotoCraft|ArtCraft|Discord" \
  thirdparty/photocraft/crates/ui-egui/src/canvas/start_screen.rs \
  thirdparty/photocraft/crates/ui-egui/src/dialogs.rs \
  thirdparty/photocraft/crates/ui-egui/src/panels/brand.rs \
  thirdparty/photocraft/crates/ui-egui/src/panels/title_bar.rs
```

Expected: 得到改动清单；对照上方「开放决策」表填入最终 URL / 是否删除 Discord·ArtCraft 行。

- [ ] **Step 4: 把决策写入执行记录（本文件末尾）**

未确认项保持占位，但 patch 内字符串必须一致（同一 URL 不写两处不同值）。

---

### Task 2: Patch `0001` — 顶栏右上角语言选择器

**Files:**
- Create: `patches/0001-top-right-language-selector.patch`
- Touch in submodule (via patch only): `crates/ui-egui/src/panels/title_bar.rs`（必要时极小改动 `i18n` 列出已注册语言的辅助函数——优先复用已有 `Lang` 枚举 / prefs 下拉数据源，避免复制语言表）

**Interfaces:**
- Consumes: `app.session.prefs().interface.language`；`crate::i18n::Lang` / 已注册语言列表；现有 `prefs.set` 命令
- Produces: 顶栏可见语言控件；变更后 UI 字符串随当前语言更新（与 Preferences › Language 行为一致）

- [ ] **Step 1: 干净基线**

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/bootstrap-submodule.sh
git -C thirdparty/photocraft rev-parse HEAD
# 必须为 287352bf92d56817db9a510e506551f394a68ea4 且 status 干净（或仅有已 apply 的先前 patch）
```

- [ ] **Step 2: 在 `title_bar.rs` 右区加入语言控件（最小 UI）**

实现要点（执行时写成真实代码再 diff）：

1. 在 workspace / search / appearance 同一 `ui.horizontal`（或现有右对齐簇）增加 dropdown / combo，标签可用 `tl!("Language")` 或简短语言码显示。
2. 选项：`auto` + `Lang` 已注册 code（与 Preferences 同源；不要手写残缺列表）。
3. 选中后：`app.run("prefs.set", json!({"values": {"interface.language": code}}))`（或项目内等价封装），不要另造存储。
4. 控件变窄时遵循现有 `ICON_SLOT` / `room` 降级逻辑：空间不足时可只显示图标或收入 overflow，避免挤爆标题。

- [ ] **Step 3: 生成并验证 patch**

```bash
cd /Volumes/my/github/SimplePhoto/thirdparty/photocraft
git diff > ../../patches/0001-top-right-language-selector.patch
cd /Volumes/my/github/SimplePhoto
git -C thirdparty/photocraft reset --hard 287352bf92d56817db9a510e506551f394a68ea4
./scripts/apply-patches.sh
```

Expected: `0001` 干净 apply；`git -C thirdparty/photocraft status -sb` 仅显示预期文件。

- [ ] **Step 4: 重建扩展资源并手工验收语言切换**

```bash
./scripts/build-web-assets.sh
# Chrome Load unpacked → extension/ → 打开编辑器
```

Expected: 右上角可选语言；选 `zh-hans` / `ja` 等后面板与菜单文案切换；刷新后若 prefs 持久化（localStorage）语言仍在；Preferences › Language 与顶栏选择一致。

- [ ] **Step 5: 提交 patch（根仓库）**

```bash
cd /Volumes/my/github/SimplePhoto
git add patches/0001-top-right-language-selector.patch
git commit -m "patch: top-right language selector for photocraft title bar"
```

---

### Task 3: Patch `0002` — Help / About / splash SimplePhoto 品牌化

**Files:**
- Create: `patches/0002-simplephoto-help-about-splash-branding.patch`
- Touch via patch（按 Task 1 清单裁剪）:
  - `crates/ui-egui/src/links.rs`
  - `crates/engine/src/shell_commands.rs`
  - `crates/ui-egui/src/menus/items.rs`（及必要 catalog）
  - About：`crates/ui-egui/src/dialogs.rs` / `dialogs/*`
  - `crates/ui-egui/src/canvas/start_screen.rs`
  - 其它用户可见 `"PhotoCraft"` / `"About PhotoCraft"` 等（**不要**批量改 crate 名、路径、AGENTS 文档）

**Interfaces:**
- Consumes: Task 1 决策表中的最终 URL 与「保留/删除 Discord·ArtCraft」结论
- Produces: Help 菜单与用户截图对应的条目文案（SimplePhoto 品牌）；链接打开 SimplePhoto（或明确保留的上游）URL；About / splash 不再主打 PhotoCraft 产品名（可保留「Powered by PhotoCraft」致谢）

- [ ] **Step 1: 在干净 + 已 apply `0001` 的树上做最小字符串/URL 替换**

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/apply-patches.sh   # 含 0001
# 编辑 links.rs 常量与 shell_commands 标签；同步 menus/items 顺序与可见性
```

建议映射（按决策表改）：

| 原（PhotoCraft） | SimplePhoto 目标 |
|---|---|
| Join the ArtCraft Discord… | 改 URL / 文案，或删除命令 |
| PhotoCraft Website | SimplePhoto Website |
| ArtCraft Website | 保留改链或删除 |
| PhotoCraft on GitHub | SimplePhoto on GitHub |
| Report an Issue… | 指向 SimplePhoto issues |
| About PhotoCraft | About SimplePhoto |

- [ ] **Step 2: About / splash**

About 标题与正文改为 SimplePhoto；保留 MIT/Apache 与 PhotoCraft NOTICE 指针（法律底线，与 `07` Legal 一致）。splash `start_screen.rs` 主标题、副标题、链接行与 `links::link_row` 文案对齐。

- [ ] **Step 3: i18n TSV（仅当英文源字符串变更导致缺译）**

若 `tl!("About PhotoCraft")` 等 key 改成新英文源，按 PhotoCraft 惯例更新 `en` 源并视需要补 `zh-hans.tsv` 等；**不要**为未改 key 的语言做无关重译。可用 `cargo xtask i18n-coverage` 看缺口（在 submodule 内）。

- [ ] **Step 4: 生成 `0002` 并双重 apply 验证**

```bash
cd /Volumes/my/github/SimplePhoto/thirdparty/photocraft
git diff > ../../patches/0002-simplephoto-help-about-splash-branding.patch
cd /Volumes/my/github/SimplePhoto
git -C thirdparty/photocraft reset --hard 287352bf92d56817db9a510e506551f394a68ea4
./scripts/apply-patches.sh
./scripts/build-web-assets.sh
```

Expected: `0001`+`0002` 顺序 apply 成功；Load unpacked 后 Help 条目与 About/splash 为 SimplePhoto 品牌；外链打开决策表 URL。

- [ ] **Step 5: 提交**

```bash
git add patches/0002-simplephoto-help-about-splash-branding.patch
git commit -m "patch: SimplePhoto Help, About, and splash branding"
```

---

### Task 4: Logo 资产 + Patch `0003` 顶栏图标 + 扩展图标

**Files:**
- Create（根仓库，**非** submodule）: `branding/simplephoto-logo.svg`、导出的 PNG 母版与 `extension/icons/icon16.png` / `icon48.png` / `icon128.png`
- Create: `patches/0003-simplephoto-titlebar-icon.patch`
- Touch via patch: `crates/ui-egui/src/panels/brand.rs`（`ICON_PNG` / `include_bytes!` 路径）；若需新 PNG 进入 submodule 树，优先 **由 patch 添加** `assets/…` 下 SimplePhoto 文件，或改为 `include_bytes!` 指向 patch 新增路径——**禁止**未记录在 patch 中的脏文件

**Interfaces:**
- Consumes: Task 3 后的品牌名；设计约束：可辨识、在 16px 仍清晰、避免使用 ArtCraft `docs/brand/` 商标资产
- Produces: 顶栏左上角 SimplePhoto 标；Chrome 工具栏 / 扩展管理页 16/48/128 图标一致

- [ ] **Step 1: 生成 SimplePhoto logo（本计划提交时不做；实现阶段做）**

在根仓库创建 `branding/`：

1. 产出矢量源（建议 SVG）与至少 1024 栅格母版。
2. 导出 `extension/icons/icon16.png`、`icon48.png`、`icon128.png`（与 `extension/manifest.json` 现有字段一致）。
3. 导出供 `brand.rs` `include_bytes!` 使用的 PNG（建议 128×128，与现钩子一致）。

```bash
mkdir -p /Volumes/my/github/SimplePhoto/branding
# 生成工具由执行者选择（设计工具 / GenerateImage 等）；完成后：
ls -la branding/ extension/icons/
file extension/icons/icon16.png extension/icons/icon48.png extension/icons/icon128.png
```

Expected: 三枚扩展图标非占位杂色块；视觉与顶栏标同源。

- [ ] **Step 2: 写 `0003` 让 `brand.rs` 使用 SimplePhoto PNG**

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/apply-patches.sh   # 0001+0002
# 将 PNG 放入 submodule 内 patch 可追踪路径，或调整 include_bytes! 后：
git -C thirdparty/photocraft diff > patches/0003-simplephoto-titlebar-icon.patch
git -C thirdparty/photocraft reset --hard 287352bf92d56817db9a510e506551f394a68ea4
./scripts/apply-patches.sh
```

Expected: 顶栏左上角为新标；`brand::mark_rect` 仍有绘制（可参考既有 titlebar 测试思路做手工对比）。

- [ ] **Step 3: 扩展图标只提交根仓库文件**

```bash
cd /Volumes/my/github/SimplePhoto
# manifest 已指向 icons/icon{16,48,128}.png — 通常无需改 JSON
git add branding/ extension/icons/icon16.png extension/icons/icon48.png extension/icons/icon128.png \
  patches/0003-simplephoto-titlebar-icon.patch
git commit -m "feat: SimplePhoto logo for title bar and extension icons"
```

- [ ] **Step 4: 全量同步与体积门**

```bash
./scripts/build-web-assets.sh
./scripts/check-extension-size.sh
```

Expected: 构建成功；图标替换不显著抬高 wasm 体积（`include_bytes!` 仅换小 PNG）。

---

### Task 5: Load unpacked 总验收

- [ ] **Step 1: 干净复现路径**

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/bootstrap-submodule.sh
./scripts/apply-patches.sh
./scripts/build-web-assets.sh
./scripts/check-extension-size.sh
```

Expected: 三个 patch 按序成功；`thirdparty/photocraft` 无未进 patch 的额外脏文件；子模块 HEAD 仍为 pin。

- [ ] **Step 2: Chrome 剧本**

1. Load unpacked → `extension/`
2. 工具栏图标为新 SimplePhoto 128/动作图标
3. 编辑器左上角品牌标为 SimplePhoto
4. 右上角切换语言，UI 跟换；与 Preferences › Language 一致
5. Help：条目文案/链接符合决策表；About SimplePhoto 可打开
6. 无文档时 splash 为 SimplePhoto 品牌
7. Console 无 CSP / WASM 错误；Open PNG → Export 仍可用（回归 v0）

- [ ] **Step 3: 更新文档勾选**

实现完成后：勾选本文件各 Step；在 `plan/07-v0-milestone.md` 下一里程碑处可标注 08 已开始/完成；根 `README` 如需可补「post-v0：见 plan/08」。

---

## Success criteria（08 计划文档本身）

- [x] 本文件存在且含三目标、钩子、三枚 patch 命名、logo/扩展图标路径、build/Load unpacked 步骤
- [x] `plan/README.md` 索引含 step 08
- [x] `plan/07-v0-milestone.md`「下一里程碑」指向 08
- [x] `plan/patches.md` 允许 branding/i18n chrome patch
- [ ] （实现阶段）三枚 patch 可重复 `apply-patches.sh`；验收剧本通过

## 非目标（08 不做）

- Chrome Web Store 上架材料
- 新建第二套 i18n / 替换 TSV 引擎
- 把 PhotoCraft 上游默认品牌改回提交到 storytold/photocraft（只活在 SimplePhoto `patches/`）
- 在本「计划提交」中生成 logo 或修改 `thirdparty/photocraft`

---

## 执行记录（实现阶段填写）

- 开放决策确认日期：
- Website / GitHub / Issues URL：
- Discord / ArtCraft 行：保留并改链 / 删除：
- About 最终文案：
- Patch SHA / 提交：
