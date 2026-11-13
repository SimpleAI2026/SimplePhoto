# SimplePhoto tutorials

Bundled, original documentation that teaches Photoshop-style image editing from a blank canvas through compositing, with steps checked against SimplePhoto (PhotoCraft) menus and tools.

## Shipped languages

Tutorials ship in seven languages: English (`en`), Simplified Chinese (`zh-hans`), Traditional Chinese (`zh-hant`), Japanese (`ja`), Korean (`ko`), German (`de`), and French (`fr`). The in-page switcher lists only these. The editor can still use its own language list; if Learn opens with `?lang=` set to a locale that has no tutorial, the pages fall back to English.

## Layout

| Path | Role |
|---|---|
| `tutorials/src/<lang>/<slug>.html` | Chapter bodies per shipped language. Edit these. |
| `tutorials/i18n/` | Language metadata, chrome strings, titles, glossary. |
| `tutorials/legacy-bilingual/` | Original combined Chinese+English sources (not packaged). |
| `scripts/build-tutorials.py` | Wraps bodies with shared chrome (nav, language switcher, pager). Incomplete languages in `languages.json` are skipped instead of failing the build. |
| `scripts/convert-zh-hant.py` | Generates `zh-hant` sources from `zh-hans` (Taiwan Photoshop terms). |
| `extension/tutorials/index.html` | Trampoline that resolves `?lang=`, saved preference, editor prefs, or the browser language, then redirects to `<lang>/index.html`. |
| `extension/tutorials/<lang>/` | Generated chapter pages for each shipped language. |
| `extension/tutorials/styles.css`, `app.js` | Shared styles and language resolution. |

Regenerate after editing a source chapter:

```bash
./scripts/build-tutorials.py
```

`scripts/package-extension.sh` copies all of `extension/`, so these pages are included automatically.

## How “Learn” opens this

The start-screen **Learn** / **学习** control calls `crate::links::tutorials_url(app)`, which is `../tutorials/index.html?lang={lang}` (or `?lang=auto`). From `chrome-extension://<id>/editor/index.html` the browser opens a new tab at `chrome-extension://<id>/tutorials/index.html?lang=…`. No extra extension permission and no `web_accessible_resources` entry are required (these are extension pages).

## Sources and copyright

The wording here is original. Official Adobe pages are linked as further reading only and are not quoted. SimplePhoto is not affiliated with Adobe; Photoshop is a trademark of Adobe.

Suggested official starting points:

- https://helpx.adobe.com/photoshop/tutorials.html
- https://www.adobe.com/learn/photoshop/paths/photo-editing
- https://helpx.adobe.com/photoshop/desktop.html
