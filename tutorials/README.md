# SimplePhoto tutorials

Bundled, original documentation that teaches Photoshop-style image editing from a blank canvas through compositing, with steps checked against SimplePhoto (PhotoCraft) menus and tools.

## Layout

| Path | Role |
|---|---|
| `tutorials/src/*.html` | Chapter bodies (Chinese + English markup). Edit these. |
| `scripts/build-tutorials.py` | Wraps bodies with shared chrome (nav, language toggle, pager). |
| `extension/tutorials/` | What the Chrome extension ships: `index.html`, chapter pages, `styles.css`, `app.js`. |

Regenerate after editing a source chapter:

```bash
./scripts/build-tutorials.py
```

`scripts/package-extension.sh` copies all of `extension/`, so these pages are included automatically.

## How “Learn” opens this

The start-screen **Learn** / **学习** control calls `crate::links::TUTORIALS`, which is `../tutorials/index.html`. From `chrome-extension://<id>/editor/index.html` the browser opens a new tab at `chrome-extension://<id>/tutorials/index.html`. No extra extension permission and no `web_accessible_resources` entry are required (these are extension pages).

## Sources and copyright

The wording here is original. Official Adobe pages are linked as further reading only and are not quoted. SimplePhoto is not affiliated with Adobe; Photoshop is a trademark of Adobe.

Suggested official starting points:

- https://helpx.adobe.com/photoshop/tutorials.html
- https://www.adobe.com/learn/photoshop/paths/photo-editing
- https://helpx.adobe.com/photoshop/desktop.html
