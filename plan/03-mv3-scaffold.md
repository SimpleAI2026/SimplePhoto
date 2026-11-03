# 03 — Chrome MV3 脚手架（manifest / CSP / 权限 / 入口）

> **For agentic workers:** 本任务只建扩展壳；编辑器静态资源来自 `02` 的 `extension/editor/`。

**Goal:** 产出可被 Chrome `Load unpacked` 识别的 Manifest V3 扩展骨架，CSP 允许 WASM（`'wasm-unsafe-eval'`），点击 action 打开编辑器扩展页。

**Architecture notes:** Service worker **不** 运行 PhotoCraft；它只负责打开 `editor/index.html`。WASM 只在 extension page 中加载。

---

### Task 1: 编写 `manifest.json` 与图标占位

**Files:**
- Create: `extension/manifest.json`
- Create: `extension/background.js`
- Create: `extension/icons/icon16.png`, `icon48.png`, `icon128.png`（占位即可）

**Interfaces:**
- Consumes: `extension/editor/index.html`（由 `02` 生成）
- Produces: MV3 可加载包根目录 = `extension/`

- [ ] **Step 1: 写入 manifest（MV3）**

写入 `extension/manifest.json`：

```json
{
  "manifest_version": 3,
  "name": "SimplePhoto",
  "version": "0.1.0",
  "description": "PhotoCraft-powered local image editor (WASM) as a Chrome extension page.",
  "action": {
    "default_title": "Open SimplePhoto",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },
  "content_security_policy": {
    "extension_pages": "script-src 'self' 'wasm-unsafe-eval'; object-src 'self'; worker-src 'self'"
  },
  "permissions": []
}
```

说明：

- **`wasm-unsafe-eval`**：MV3 实例化 WebAssembly 所必需；不等于 `'unsafe-eval'`。
- **`permissions: []`**：v0 先空；`05` 若启用 `chrome.downloads` 再加 `"downloads"`；剪贴板权限按实测追加。
- **不** 声明宽泛 host_permissions（禁止远程拉业务代码）。

- [ ] **Step 2: 写入 background service worker**

写入 `extension/background.js`：

```js
// Open the PhotoCraft editor as an extension page (full tab).
const EDITOR_PATH = "editor/index.html";

async function openEditor(query = "") {
  const url = chrome.runtime.getURL(EDITOR_PATH) + query;
  await chrome.tabs.create({ url });
}

chrome.action.onClicked.addListener(() => {
  openEditor().catch((err) => console.error("openEditor failed", err));
});

chrome.runtime.onInstalled.addListener(() => {
  console.info("SimplePhoto installed; click the action icon to open the editor.");
});
```

- [ ] **Step 3: 生成占位图标**

用任意图像工具在 `extension/icons/` 生成 16/48/128 PNG。无设计稿时可用纯色方块（ImageMagick `convert` 或任意绘图脚本均可）。

```bash
cd /Volumes/my/github/SimplePhoto
mkdir -p extension/icons
ls -la extension/icons/icon16.png extension/icons/icon48.png extension/icons/icon128.png
```

Expected: 三个 `icon*.png` 存在。

- [ ] **Step 4: 确认 editor 资源已就位**

```bash
test -f /Volumes/my/github/SimplePhoto/extension/editor/index.html || /Volumes/my/github/SimplePhoto/scripts/build-web-assets.sh
```

Expected: `extension/editor/index.html` 可读。

- [ ] **Step 5: Load unpacked 冒烟**

1. Chrome → `chrome://extensions` → Developer mode
2. **Load unpacked** → 选择 `/Volumes/my/github/SimplePhoto/extension`
3. 点击扩展 action

Expected: 新标签打开 `chrome-extension://<id>/editor/index.html`。若 WASM/CSP 正确，进入 Loading→编辑器。失败时用 DevTools Console 记录原文（常见：CSP 缺 `wasm-unsafe-eval`、404、wasm 编译失败）。

- [ ] **Step 6: 提交脚手架**

```bash
cd /Volumes/my/github/SimplePhoto
git add extension/manifest.json extension/background.js extension/icons
git commit -m "feat: add Chrome MV3 shell with wasm-unsafe-eval CSP"
```

## Success criteria（03 完成）

- [ ] `Load unpacked` 成功，无 manifest 错误
- [ ] CSP 含 `'wasm-unsafe-eval'`
- [ ] Action 打开 `editor/index.html`
- [ ] 控制台无因 CSP 拒绝 WebAssembly 实例化
