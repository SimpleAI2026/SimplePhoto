# Extension vs static web host

Pinned PhotoCraft: `2239ee9cb6c87583242ccd247f0a621f3d4d90ee`

| 能力 | 静态 https / localhost | Chrome extension page (v0) |
|---|---|---|
| Open | rfd file picker | rfd / same as web (user confirmed splash Open available) |
| Save | `<a download>`，unconfirmed | `<a download>`, unconfirmed (v0 accepted) |
| Prefs | localStorage | 同左（extension page secure context; load verified） |
| Presets | IndexedDB | 同左 |
| WebGPU | secure context | chrome-extension:// 亦是（editor page load verified） |
| Folder pick | 不支持 | 同左 |
| TCP control | 无 | 无 |

## v0 decisions

- **Full-tab only** — editor opens as a Chrome extension page (`chrome-extension://…/editor/…`), not a content-script overlay.
- **No chrome.downloads bridge for v0** — Save/Export keeps PhotoCraft web semantics (`<a download>` + `write_unconfirmed: true`). No `downloads` permission; no photocraft patches.
- **Open** — same as web via `rfd`; splash New/Open UI confirmed working.

## Bundled tutorials

The start-screen **Learn** action opens `../tutorials/index.html?lang={lang}` (resolved from the editor page to `chrome-extension://<id>/tutorials/index.html?lang=…`) in a new tab. `{lang}` is the editor interface language, or `auto`. This is an extension page, so `web_accessible_resources` is not required. Packaged via `scripts/package-extension.sh` (copies all of `extension/`).

Tutorials ship in English, Simplified Chinese, Traditional Chinese, Japanese, Korean, German, and French (`en`, `zh-hans`, `zh-hant`, `ja`, `ko`, `de`, `fr`). The tutorial switcher lists only those seven. Any other editor language falls back to English. The editor's own language selector is unchanged.
