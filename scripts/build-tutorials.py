#!/usr/bin/env python3
"""Generate bilingual SimplePhoto tutorial pages under extension/tutorials/."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tutorials" / "src"
OUT = ROOT / "extension" / "tutorials"

# (slug, zh title, en title)
CHAPTERS: list[tuple[str, str, str]] = [
    ("index", "学习路径", "Learning path"),
    ("01-interface", "界面与画布", "Interface and canvas"),
    ("02-open-save", "打开、保存与导出", "Open, save, and export"),
    ("03-crop-resize", "裁剪、图像大小与画布", "Crop, image size, and canvas"),
    ("04-layers", "图层", "Layers"),
    ("05-selections", "选区工具", "Selection tools"),
    ("06-brushes", "画笔与橡皮擦", "Brushes and eraser"),
    ("07-adjustments", "色调与颜色调整", "Tone and color adjustments"),
    ("08-masks", "图层蒙版", "Layer masks"),
    ("09-text", "文字", "Type and text"),
    ("10-transform", "变换", "Transform"),
    ("11-retouch", "修饰、修复与仿制", "Retouch, heal, and clone"),
    ("12-filters-blend", "滤镜与混合模式", "Filters and blend modes"),
    ("13-compositing", "合成工作流", "Compositing workflow"),
    ("14-nondestructive", "非破坏性编辑", "Non-destructive editing"),
    ("15-shortcuts", "快捷键", "Keyboard shortcuts"),
]


def nav(current: str) -> str:
    items = []
    for i, (slug, zh, en) in enumerate(CHAPTERS):
        href = f"{slug}.html"
        current_attr = ' aria-current="page"' if slug == current else ""
        if slug == "index":
            label = (
                f'<span class="zh">概览</span><span class="en">Overview</span>'
            )
        else:
            label = (
                f'<span class="num">{i:02d}</span>'
                f'<span class="zh">{zh}</span><span class="en">{en}</span>'
            )
        items.append(f'<li><a href="{href}"{current_attr}>{label}</a></li>')
    return "\n".join(items)


def pager(idx: int) -> str:
    parts = ['<nav class="pager">']
    if idx > 0:
        slug, zh, en = CHAPTERS[idx - 1]
        parts.append(
            f'<a href="{slug}.html"><span class="zh">上一章：{zh}</span>'
            f'<span class="en">Previous: {en}</span></a>'
        )
    else:
        parts.append("<span></span>")
    if idx + 1 < len(CHAPTERS):
        slug, zh, en = CHAPTERS[idx + 1]
        parts.append(
            f'<a href="{slug}.html"><span class="zh">下一章：{zh}</span>'
            f'<span class="en">Next: {en}</span></a>'
        )
    parts.append("</nav>")
    return "\n".join(parts)


def page(idx: int, body: str) -> str:
    slug, zh, en = CHAPTERS[idx]
    title_zh = "SimplePhoto 教程" if slug == "index" else f"{zh} · SimplePhoto 教程"
    title_en = "SimplePhoto tutorials" if slug == "index" else f"{en} · SimplePhoto tutorials"
    return f"""<!DOCTYPE html>
<html lang="zh-Hans" data-lang="zh">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title class="page-title">{title_zh}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip" href="#main">跳到正文 / Skip to content</a>
  <header class="top">
    <a class="brand" href="index.html">SimplePhoto</a>
    <span class="tag"><span class="zh">教程</span><span class="en">Tutorials</span></span>
    <div class="lang" role="group" aria-label="Language">
      <button type="button" data-lang="zh" aria-pressed="true">中文</button>
      <button type="button" data-lang="en" aria-pressed="false">EN</button>
    </div>
  </header>
  <div class="layout">
    <nav class="side" aria-label="Curriculum">
      <h2><span class="zh">目录</span><span class="en">Contents</span></h2>
      <ol>
        {nav(slug)}
      </ol>
    </nav>
    <main id="main">
      {body}
      {pager(idx)}
    </main>
  </div>
  <script src="app.js"></script>
</body>
</html>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    missing = []
    for idx, (slug, _, _) in enumerate(CHAPTERS):
        src = SRC / f"{slug}.html"
        if not src.is_file():
            missing.append(str(src))
            continue
        html = page(idx, src.read_text(encoding="utf-8"))
        dest = OUT / f"{slug}.html"
        dest.write_text(html, encoding="utf-8", newline="\n")
        print(f"wrote {dest.relative_to(ROOT)}")
    if missing:
        raise SystemExit("missing sources:\n" + "\n".join(missing))


if __name__ == "__main__":
    main()
