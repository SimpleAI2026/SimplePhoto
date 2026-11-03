# 05 — 打开 / 保存 / 剪贴板与平台桥接

> **For agentic workers:** 先验证现有 web `Services` 在 extension page 是否足够；只有失败才写 patch 或薄 JS bridge。

**Goal:** 在 Chrome 扩展页上跑通 Open、拖放、Save/Export 下载、基础剪贴板；文档化与静态 https 宿主的差异，以及何时必须改 PhotoCraft。

**Architecture notes:** 真相源是 `apps/photocraft-web/src/web.rs` 的 `services()`：`rfd` 打开、`<a download>` 写出、`write_unconfirmed: true`、localStorage prefs、IndexedDB presets。扩展页同为 secure context，优先复用。

Pinned PhotoCraft：`287352bf92d56817db9a510e506551f394a68ea4`

---

### Task 1: 基线验收（零改 Rust）

**Files:** 无（手工测试清单）

- [ ] **Step 1: File → Open**

1. 打开编辑器
2. File → Open，选一张 PNG/JPEG/PSD
3. 文档应出现在标签/画布

Expected: 与浏览器里 `trunk serve` 行为一致（`rfd::AsyncFileDialog` → `Contents`）。

- [ ] **Step 2: 拖放打开**

把图片拖到 canvas 上。

Expected: 经 `inbox` / `place_inbox` 异步打开或置入（见 `web.rs` `WebShell`）。

- [ ] **Step 3: Save / Export 下载**

编辑后 File → Save As / Export，应触发浏览器下载。

Expected: 下载开始；注意 web 语义：`write_unconfirmed: true`，用户取消下载时文档仍可能标 unsaved（#4962）。这是 **已知 web 行为**，v0 可接受除非产品要求「确认落盘」。

- [ ] **Step 4: 偏好与 presets**

改一个 Preferences 项，刷新页面。

Expected: `localStorage` key `photocraft.preferences` 仍在；预设若有改动走 IndexedDB。

- [ ] **Step 5: 剪贴板**

复制选区 / 粘贴图像（若 UI 暴露）。

Expected: 记录是否需要额外 manifest 权限。若浏览器提示权限或静默失败，进入 Task 2。

把结果记入本文件底部「实测记录」小节（执行时追加）。

---

### Task 2: 仅在需要时加扩展桥（JS 优先，Rust patch 次之）

**决策树：**

1. **`<a download>` 在 extension page 被拦**
   - 方案 A（优先）：`background.js` 暴露消息，调用 `chrome.downloads.download({ url: objectUrl, filename })`；扩展页内一段 **极薄** 的 bridge 脚本。
   - PhotoCraft 页面本身 **无手写 script**（Trunk 注入 loader）。插入 bridge 的合法方式：
     - 在 `scripts/build-web-assets.sh` 对同步后的 `index.html` 追加 `<script type="module" src="../bridges/download.js">`，**不要**改 submodule 的 `apps/photocraft-web/index.html`；或
     - patch `web.rs` 的 `download()` 改为调用 `window.simplePhotoSave(bytes, name)`（需 `patches/`）。
   - manifest 增加 `"permissions": ["downloads"]`。

2. **需要「另存为真实路径 / 清除 unsaved」**
   - 评估 File System Access API（`showSaveFilePicker`）是否在 extension page 可用。
   - 若可用：patch `file_dialog` Save 分支与 `write`，确认写入后走非 `write_unconfirmed` 语义。
   - 变更必须进 `patches/`（见 `patches.md`）。

3. **从扩展图标「打开文件」直接喂给编辑器**
   - 不必改 Rust：用编辑器内 Open；或 background 读字节后 `postMessage` 到 inbox 钩子（钩子若无则需 patch）。

4. **剪贴板图像**
   - 先试不加权限；失败再加 `clipboardRead` / `clipboardWrite`。

**Files（方案 A 示例，仅当 Task 1 Step 3 失败时创建）：**
- Create: `extension/bridges/download.js`
- Modify: `scripts/build-web-assets.sh`（注入 script 标签）
- Modify: `extension/manifest.json`（`downloads` 权限）
- Modify: `extension/background.js`

- [ ] **Step 1: 仅当下载失败时实现 bridge**

`extension/bridges/download.js` 思路：

```js
window.simplePhotoSave = async function simplePhotoSave(bytes, filename) {
  const blob = new Blob([bytes]);
  const url = URL.createObjectURL(blob);
  try {
    const res = await chrome.runtime.sendMessage({
      type: "download-url",
      url,
      filename,
    });
    if (!res?.ok) throw new Error(res?.error || "download failed");
  } finally {
    setTimeout(() => URL.revokeObjectURL(url), 60_000);
  }
};
```

`background.js` 增加：

```js
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "download-url") {
    chrome.downloads.download({ url: msg.url, filename: msg.filename, saveAs: true })
      .then((id) => sendResponse({ ok: true, id }))
      .catch((e) => sendResponse({ ok: false, error: String(e) }));
    return true;
  }
});
```

若 `<a download>` 已够用：**跳过本 Task**，在实测记录写「无需 bridge」。

- [ ] **Step 2: 若必须改 `web.rs`，走 patch 流程**

见 `patches.md`：生成 `patches/0001-extension-download-bridge.patch`，再用 `scripts/apply-patches.sh` 应用。根仓库只提交 patch 文件。

- [ ] **Step 3: 回归 Task 1 清单**

Expected: Open/Save/拖放再次全部通过；新增权限在 `chrome://extensions` 详情页可见。

---

### Task 3: 文档化语义差异

**Files:**
- Create: `extension/PLATFORM.md`

```markdown
# Extension vs static web host

| 能力 | 静态 https / localhost | Chrome extension page (v0) |
|---|---|---|
| Open | rfd file picker | 同左（验证：____） |
| Save | `<a download>`，unconfirmed | 同左 / downloads bridge（选择：____） |
| Prefs | localStorage | 同左 |
| Presets | IndexedDB | 同左 |
| WebGPU | secure context | chrome-extension:// 亦是 |
| Folder pick | 不支持 | 同左 |
| TCP control | 无 | 无 |
```

- [ ] **Step 1: 写完并提交**

```bash
cd /Volumes/my/github/SimplePhoto
git add extension/PLATFORM.md extension/bridges extension/manifest.json extension/background.js scripts/build-web-assets.sh patches 2>/dev/null || true
git status
git commit -m "feat: document and wire extension platform bridges for open/save"
```

## Success criteria（05 完成）

- [ ] Open + 拖放 + Save/Export 在扩展内可用（有证据：截图或操作记录）
- [ ] 任何 PhotoCraft 源码 diff 都以 `patches/*.patch` 形式存在
- [ ] `extension/PLATFORM.md` 写明与静态宿主差异

---

## 实测记录

**日期：** 2026-11-04（Asia/Shanghai）

- Editor loads past the Loading splash after Trunk `trunk-boot.js` inline-script extraction (MV3 CSP).
- Splash UI confirmed 2026-11-04：New / Open visible and usable (user confirmed editor opens).
- **Task 2 skipped** — no `chrome.downloads` bridge; no photocraft patches; no `downloads` permission.
- Save semantics accepted as web download：`<a download>` + `write_unconfirmed`（v0）.
- Open：rfd / same as web；prefs / WebGPU treated as working on extension page for load baseline.
