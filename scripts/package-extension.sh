#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER=$(python3 -c "import json;print(json.load(open('$ROOT/extension/manifest.json'))['version'])")
OUT_DIR="$ROOT/dist"
NAME="simplephoto-extension-$VER"

SKIP_BUILD=0
for arg in "$@"; do
  case "$arg" in
    --skip-build) SKIP_BUILD=1 ;;
    -h|--help)
      echo "Usage: $0 [--skip-build]"
      echo "  --skip-build  sync existing photocraft dist into extension/editor (no trunk rebuild)"
      exit 0
      ;;
    *)
      echo "error: unknown arg: $arg" >&2
      exit 1
      ;;
  esac
done

if [ "$SKIP_BUILD" -eq 1 ]; then
  ./scripts/build-web-assets.sh --skip-build
else
  ./scripts/build-web-assets.sh
fi

./scripts/check-extension-size.sh
rm -rf "$OUT_DIR/$NAME" "$OUT_DIR/$NAME.zip"
mkdir -p "$OUT_DIR/$NAME"
rsync -a --exclude '.DS_Store' "$ROOT/extension/" "$OUT_DIR/$NAME/"
# Destination name is LICENSE-PHOTCRAFT-MIT (plan typo: not LICENSE-PHOTCRAFT-MIT path source)
cp "$ROOT/thirdparty/photocraft/LICENSE-MIT" "$OUT_DIR/$NAME/LICENSE-PHOTCRAFT-MIT"
cp "$ROOT/thirdparty/photocraft/NOTICE" "$OUT_DIR/$NAME/NOTICE-PHOTCRAFT"
(cd "$OUT_DIR" && zip -qr9 "$NAME.zip" "$NAME")
ls -lh "$OUT_DIR/$NAME.zip"
./scripts/check-extension-size.sh
