# 04 — 将 photocraft-web 集成进扩展 UI shell

> **For agentic workers:** 默认 **零改 PhotoCraft**；只调整扩展侧如何托管静态站。

**Goal:** 确保扩展页完整承载 PhotoCraft UI（全视口 canvas），加载体验与官方 web 一致，并提供 WebGL/CPU 回退入口。

**Architecture notes:** `extension/editor/` **就是** Trunk 的 `dist/web` 镜像。不要用扩展 popup（太小且短命）承载 egui；不要用沙箱 iframe 套一层（会丢 storage/downloads，见 `packaging/web/README.md`）。

Pinned PhotoCraft：`287352bf92d56817db9a510e506551f394a68ea4`

---

### Task 1: 扩展页即编辑器（无额外 HTML 包装，优先）

**Files:**
- Use: `extension/editor/index.html`（来自 Trunk，含 `#photocraft_canvas`）
- Modify (仅当需要): `extension/background.js`
- Optional Create: `extension/welcome.html`

**Interfaces:**
- Consumes: `02` 同步的静态资源
- Produces: 用户可见的全页编辑器

- [ ] **Step 1: 验证相对资源在 chrome-extension 源下可解析**

在已 Load unpacked 后打开：

`chrome-extension://<EXTENSION_ID>/editor/index.html`

DevTools → Network：确认 glue `*.js` 与 `*_bg.wasm` 均为 200。

Expected: 资源全部命中；Document 为 `editor/index.html`。

- [ ] **Step 2: 确认 loading 与 stalled 行为仍在**

- 应短暂看到 “Loading PhotoCraft…”
- 成功后 `#photocraft_loading` 被 Rust 移除
- 若故意让 wasm 404，约 20s 后应出现 Reload 提示（`index.html` CSS 动画；见 `apps/photocraft-web/src/main.rs` 测试）

Expected: 与官方 web 行为一致。

- [ ] **Step 3: 全视口与缩放**

窗口缩放到不同大小；canvas 应 `position:absolute; inset:0` 铺满。Retina 下 UI 可交互。

Expected: 无巨大空白或固定死尺寸。

---

### Task 2: 渲染回退入口与 welcome 页

PhotoCraft 已支持（`apps/photocraft-web/src/main.rs` / `packaging/web/README.md`）：

| URL | 行为 |
|---|---|
| `editor/index.html` | WebGPU，失败则 WebGL2 |
| `editor/index.html?webgl` | 强制 WebGL2 |
| `editor/index.html?cpu` | 强制 CPU canvas |

**Files:**
- Modify: `extension/background.js`
- Create: `extension/welcome.html`

- [ ] **Step 1: background 增加消息接口**

```js
const EDITOR_PATH = "editor/index.html";

async function openEditor(query = "") {
  const url = chrome.runtime.getURL(EDITOR_PATH) + query;
  await chrome.tabs.create({ url });
}

chrome.action.onClicked.addListener(() => {
  openEditor().catch(console.error);
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "open-editor") {
    openEditor(msg.query || "")
      .then(() => sendResponse({ ok: true }))
      .catch((e) => sendResponse({ ok: false, error: String(e) }));
    return true;
  }
});
```

- [ ] **Step 2: 写入 `extension/welcome.html`**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>SimplePhoto</title>
  <style>
    body { font: 14px system-ui, sans-serif; max-width: 40rem; margin: 2rem auto;
           color: #e8e8e8; background: #262626; }
    a { color: #9cf; }
  </style>
</head>
<body>
  <h1>SimplePhoto</h1>
  <p>基于 PhotoCraft WASM 的本地编辑器（Chrome MV3）。</p>
  <ul>
    <li><a href="editor/index.html">打开编辑器（默认 WebGPU）</a></li>
    <li><a href="editor/index.html?webgl">打开编辑器（强制 WebGL2）</a></li>
    <li><a href="editor/index.html?cpu">打开编辑器（CPU canvas）</a></li>
  </ul>
  <p>构建信息见 <code>editor/BUILD_INFO.txt</code>。</p>
</body>
</html>
```

- [ ] **Step 3: 手工验收**

| 检查项 | 通过标准 |
|---|---|
| 默认入口 | 编辑器 UI 出现（菜单/工具栏可辨） |
| `?webgl` | 可正常绘制 |
| 刷新 | localStorage 偏好保留（若改过） |
| 架构 | 无自造 JS UI 框架 / 无 Tauri |

- [ ] **Step 4: 提交**

```bash
cd /Volumes/my/github/SimplePhoto
git add extension/background.js extension/welcome.html
git commit -m "feat: integrate photocraft-web editor page and renderer fallback links"
```

## Success criteria（04 完成）

- [ ] Action / welcome 能打开可用的 PhotoCraft UI
- [ ] 未引入 Tauri/Electron/React 壳
- [ ] 未修改 submodule 源码（若修改，必须已进入 `patches/`）
