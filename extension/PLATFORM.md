# Extension vs static web host

Pinned PhotoCraft: `287352bf92d56817db9a510e506551f394a68ea4`

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
