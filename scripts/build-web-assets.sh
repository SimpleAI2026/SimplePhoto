#!/usr/bin/env bash
# Build photocraft-web and sync static assets into extension/editor/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PC="$ROOT/thirdparty/photocraft"
APP_SRC="$PC/apps/photocraft-web"
DIST="$PC/dist/web"
DEST="$ROOT/extension/editor"
PIN_EXPECTED="287352bf92d56817db9a510e506551f394a68ea4"

cd "$PC"
HEAD="$(git rev-parse HEAD)"
if [[ "$HEAD" != "$PIN_EXPECTED" ]]; then
  echo "warning: photocraft HEAD=$HEAD (plan pin=$PIN_EXPECTED). Continue only if intentional." >&2
fi

if [[ "${1:-}" != "--skip-build" ]]; then
  command -v trunk >/dev/null || { echo "error: trunk not found" >&2; exit 1; }
  (cd "$APP_SRC" && trunk build --release)
fi

[[ -f "$DIST/index.html" ]] || { echo "error: $DIST/index.html missing" >&2; exit 1; }
if grep -Eq '(src|href)="/[^/]' "$DIST/index.html"; then
  echo "error: absolute URLs in $DIST/index.html" >&2
  exit 1
fi

rm -rf "$DEST"
mkdir -p "$DEST"
# 复制静态站（含 index.html、*.js、*_bg.wasm 及 trunk 其它资源）
cp -R "$DIST"/. "$DEST"/
# 保留目录可被 git 跟踪的占位在清理后消失；构建后不需要 .gitkeep

# MV3 extension_pages CSP allows script-src 'self' 'wasm-unsafe-eval' — not 'unsafe-inline'.
# Trunk emits an inline <script type="module"> boot; extract it to external file(s).
python3 - "$DEST/index.html" <<'PY'
import re
import sys
from pathlib import Path

index_path = Path(sys.argv[1])
html = index_path.read_text(encoding="utf-8")
pattern = re.compile(
    r"<script\s+type=[\"']module[\"']\s*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
matches = list(pattern.finditer(html))
if not matches:
    # Already external-only is fine; still fail if any other inline <script> remains later.
    print("note: no inline <script type=\"module\"> found in index.html", file=sys.stderr)
else:
    out = []
    last = 0
    for i, m in enumerate(matches):
        body = m.group(1)
        # Preserve contents exactly (including surrounding newlines from Trunk).
        name = "trunk-boot.js" if len(matches) == 1 else f"trunk-boot-{i}.js"
        (index_path.parent / name).write_text(body, encoding="utf-8", newline="\n")
        replacement = f'<script type="module" src="./{name}"></script>'
        out.append(html[last:m.start()])
        out.append(replacement)
        last = m.end()
        print(f"extracted inline module -> {name} ({len(body)} bytes)")
    out.append(html[last:])
    html = "".join(out)
    index_path.write_text(html, encoding="utf-8", newline="\n")

# Fail if any inline <script ...>body</script> remains (src= external scripts are OK).
inline_left = re.findall(
    r"<script(?![^>]*\bsrc=)[^>]*>\s*\S",
    html,
    flags=re.IGNORECASE,
)
if inline_left:
    print(
        "error: inline <script> still present in index.html after rewrite "
        f"(count={len(inline_left)})",
        file=sys.stderr,
    )
    sys.exit(1)
print("index.html: no inline scripts remain")
PY

{
  echo "photocraft_sha=$HEAD"
  echo "built_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "source=apps/photocraft-web trunk build --release"
  ls -lh "$DEST"/*_bg.wasm 2>/dev/null | awk '{print "wasm="$0}'
} | tee "$DEST/BUILD_INFO.txt"

echo "synced -> $DEST"
