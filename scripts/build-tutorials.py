#!/usr/bin/env python3
"""Generate per-language SimplePhoto tutorial pages under extension/tutorials/."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "tutorials" / "i18n"
SRC = ROOT / "tutorials" / "src"
OUT = ROOT / "extension" / "tutorials"
BILINGUAL_SRC = SRC  # legacy combined files live here as <slug>.html

CHAPTERS = [
    "index",
    "01-interface",
    "02-open-save",
    "03-crop-resize",
    "04-layers",
    "05-selections",
    "06-brushes",
    "07-adjustments",
    "08-masks",
    "09-text",
    "10-transform",
    "11-retouch",
    "12-filters-blend",
    "13-compositing",
    "14-nondestructive",
    "15-shortcuts",
]

CHAPTER_SECTIONS = {
    "01-interface": "basics",
    "02-open-save": "basics",
    "03-crop-resize": "basics",
    "04-layers": "core",
    "05-selections": "core",
    "06-brushes": "painting",
    "07-adjustments": "adjustments",
    "08-masks": "core",
    "09-text": "type",
    "10-transform": "transform",
    "11-retouch": "retouch",
    "12-filters-blend": "effects",
    "13-compositing": "intermediate",
    "14-nondestructive": "intermediate",
    "15-shortcuts": "reference",
}


def _set_text(tag, text: str) -> None:
    tag.clear()
    tag.append(text)


def localize_body(html: str, *, slug: str, lang: str, titles: dict, chrome: dict, phrases: dict) -> str:
    soup = BeautifulSoup(html, "html.parser")
    headings = phrases["headings"]
    sections = phrases["sections"]
    blurbs = phrases["blurbs"]
    for p in soup.select("p.kicker"):
        if slug == "index":
            _set_text(p, headings["index_kicker"][lang])
        else:
            n = int(slug.split("-", 1)[0])
            chapter = chrome["chapter"].replace("{n}", f"{n:02d}")
            section = sections[CHAPTER_SECTIONS[slug]][lang]
            _set_text(p, f"{chapter} · {section}")
    for h in soup.find_all("h1"):
        _set_text(h, titles[slug][lang])
    if slug == "index":
        for h in soup.select("aside.in-app > h3"):
            _set_text(h, headings["starting_in_simplephoto"][lang])
        for h in soup.select("aside.ps-only > h3"):
            _set_text(h, headings["where_not_photoshop"][lang])
    else:
        for h in soup.select("aside.in-app > h3"):
            _set_text(h, headings["in_simplephoto"][lang])
        for h in soup.select("aside.ps-only > h3"):
            _set_text(h, headings["photoshop_only_notes"][lang])
    for h in soup.select("section.reading > h2"):
        if slug == "index":
            _set_text(h, chrome["further_reading"])
        else:
            _set_text(h, headings["further_reading_short"][lang])
    cards = soup.select_one("div.cards")
    if cards is not None:
        cards.clear()
        for ch in CHAPTERS:
            if ch == "index":
                continue
            n = int(ch.split("-", 1)[0])
            a = soup.new_tag("a", href=f"{ch}.html")
            strong = soup.new_tag("strong")
            num = soup.new_tag("span", attrs={"class": "num"})
            num.string = f"{n:02d}"
            title_span = soup.new_tag("span")
            title_span.string = titles[ch][lang]
            strong.append(num)
            strong.append(" ")
            strong.append(title_span)
            blurb = soup.new_tag("span")
            blurb.string = blurbs[ch][lang]
            a.append(strong)
            a.append(blurb)
            cards.append(a)
    return soup.decode_contents().strip() + "\n"


def load_json(name: str):
    return json.loads((I18N / name).read_text(encoding="utf-8"))


def class_list(tag) -> set[str]:
    raw = tag.get("class") or []
    if isinstance(raw, str):
        return set(raw.split())
    return set(raw)


def split_bilingual(html: str, keep: str) -> str:
    """keep is 'zh' or 'en'. Drop the other language's elements; unwrap kept ones."""
    drop = "en" if keep == "zh" else "zh"
    soup = BeautifulSoup(html, "html.parser")
    # Drop the other language first (deepest first).
    for tag in list(soup.find_all(True)):
        if tag.attrs is None:
            continue
        classes = class_list(tag)
        if drop in classes and keep not in classes:
            tag.decompose()
    for tag in list(soup.find_all(True)):
        if tag.attrs is None:
            continue
        classes = class_list(tag)
        if keep in classes:
            classes.discard(keep)
            if classes:
                tag["class"] = sorted(classes)
            else:
                del tag["class"]
            # If the tag is now a class-less span with a single text child, leave it.
    # Pretty but stable enough
    body = soup.decode_contents().strip()
    return body + "\n"


def lang_switcher(langs: list[dict], current: str, chrome: dict) -> str:
    opts = []
    for meta in langs:
        sel = " selected" if meta["code"] == current else ""
        opts.append(f'<option value="{meta["code"]}"{sel}>{meta["name"]}</option>')
    label = chrome["language"]
    return (
        f'<div class="lang"><label for="lang-select">{label}</label>'
        f'<select id="lang-select" name="lang">\n'
        + "\n".join(opts)
        + "\n</select></div>"
    )


def nav_html(titles: dict, current_slug: str, lang: str, chrome: dict) -> str:
    items = []
    for slug in CHAPTERS:
        href = f"{slug}.html"
        current_attr = ' aria-current="page"' if slug == current_slug else ""
        if slug == "index":
            label = chrome["overview"]
        else:
            n = int(slug.split("-", 1)[0])
            label = f'<span class="num">{n:02d}</span>{titles[slug][lang]}'
        items.append(f'<li><a href="{href}"{current_attr}>{label}</a></li>')
    return "\n".join(items)


def pager_html(idx: int, titles: dict, lang: str, chrome: dict) -> str:
    parts = ['<nav class="pager">']
    if idx > 0:
        slug = CHAPTERS[idx - 1]
        label = chrome["previous"].replace("{title}", titles[slug][lang])
        parts.append(f'<a href="{slug}.html">{label}</a>')
    else:
        parts.append("<span></span>")
    if idx + 1 < len(CHAPTERS):
        slug = CHAPTERS[idx + 1]
        label = chrome["next"].replace("{title}", titles[slug][lang])
        parts.append(f'<a href="{slug}.html">{label}</a>')
    parts.append("</nav>")
    return "\n".join(parts)


def page_html(*, lang_meta: dict, chrome: dict, langs: list[dict], titles: dict, slug: str, idx: int, body: str) -> str:
    code = lang_meta["code"]
    title = titles[slug][code]
    if slug == "index":
        head_title = f"{chrome['tutorials']} · SimplePhoto"
    else:
        head_title = f"{title} · {chrome['tutorials']}"
    return f"""<!DOCTYPE html>
<html lang="{lang_meta['html_lang']}" dir="{lang_meta['dir']}" data-lang="{code}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{head_title}</title>
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <a class="skip" href="#main">{chrome['skip']}</a>
  <header class="top">
    <a class="brand" href="index.html">SimplePhoto</a>
    <span class="tag">{chrome['tutorials']}</span>
    {lang_switcher(langs, code, chrome)}
  </header>
  <div class="layout">
    <nav class="side" aria-label="{chrome['contents']}">
      <h2>{chrome['contents']}</h2>
      <ol>
        {nav_html(titles, slug, code, chrome)}
      </ol>
    </nav>
    <main id="main">
      {body}
      {pager_html(idx, titles, lang, chrome) if False else pager_html(idx, titles, code, chrome)}
    </main>
  </div>
  <script src="../app.js"></script>
</body>
</html>
"""


def trampoline_html(chrome_en: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SimplePhoto {chrome_en['tutorials']}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body class="trampoline">
  <p>{chrome_en['redirecting']}</p>
  <script src="app.js"></script>
</body>
</html>
"""


def sync_bilingual_sources() -> None:
    """Split legacy bilingual tutorials/src/<slug>.html into src/en and src/zh-hans."""
    for slug in CHAPTERS:
        combined = BILINGUAL_SRC / f"{slug}.html"
        if not combined.is_file():
            continue
        html = combined.read_text(encoding="utf-8")
        for keep, dest_lang in (("en", "en"), ("zh", "zh-hans")):
            dest = SRC / dest_lang / f"{slug}.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(split_bilingual(html, keep), encoding="utf-8", newline="\n")


def lang_is_complete(code: str) -> bool:
    return all((SRC / code / f"{slug}.html").is_file() for slug in CHAPTERS)


def main() -> None:
    langs = load_json("languages.json")
    chrome_all = load_json("chrome.json")
    titles = load_json("titles.json")
    phrases = load_json("phrases.json")
    # Legacy bilingual files live in tutorials/legacy-bilingual/; split on demand.
    shipped = [meta for meta in langs if lang_is_complete(meta["code"])]
    skipped = [meta["code"] for meta in langs if meta not in shipped]
    if skipped:
        print("skipping incomplete languages:", ", ".join(skipped))
    if not any(meta["code"] == "en" for meta in shipped):
        raise SystemExit("English tutorial sources are required")
    OUT.mkdir(parents=True, exist_ok=True)
    # Drop stale per-language trees and former flat bilingual pages so only shipped langs remain.
    for child in OUT.iterdir():
        if child.is_dir() and child.name not in {meta["code"] for meta in shipped}:
            shutil.rmtree(child)
        elif child.is_file() and child.name.endswith(".html") and child.name != "index.html":
            child.unlink()
    (OUT / "index.html").write_text(trampoline_html(chrome_all["en"]), encoding="utf-8", newline="\n")
    written = 0
    for meta in shipped:
        code = meta["code"]
        ch = chrome_all[code]
        for idx, slug in enumerate(CHAPTERS):
            src = SRC / code / f"{slug}.html"
            body = localize_body(
                src.read_text(encoding="utf-8"),
                slug=slug,
                lang=code,
                titles=titles,
                chrome=ch,
                phrases=phrases,
            )
            html = page_html(
                lang_meta=meta,
                chrome=ch,
                langs=shipped,
                titles=titles,
                slug=slug,
                idx=idx,
                body=body,
            )
            dest = OUT / code / f"{slug}.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(html, encoding="utf-8", newline="\n")
            written += 1
    print(f"wrote trampoline + {written} pages for {', '.join(m['code'] for m in shipped)}")


if __name__ == "__main__":
    main()
