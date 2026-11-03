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

{
  echo "photocraft_sha=$HEAD"
  echo "built_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "source=apps/photocraft-web trunk build --release"
  ls -lh "$DEST"/*_bg.wasm 2>/dev/null | awk '{print "wasm="$0}'
} | tee "$DEST/BUILD_INFO.txt"

echo "synced -> $DEST"
