#!/usr/bin/env bash
# Copy SimplePhoto branding PNGs into the photocraft tree after patches are applied.
# Avoids shipping a huge binary patch for the title-bar include_bytes! icon.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/branding/simplephoto-app-128.png"
DEST_DIR="$ROOT/thirdparty/photocraft/assets/app-icon/hicolor/128x128/apps"
DEST="$DEST_DIR/ai.storyteller.photocraft.png"

if [[ ! -f "$SRC" ]]; then
  echo "error: missing $SRC" >&2
  exit 1
fi
if [[ ! -d "$DEST_DIR" ]]; then
  echo "error: photocraft assets dir missing at $DEST_DIR — run ./scripts/bootstrap-submodule.sh && ./scripts/apply-patches.sh first" >&2
  exit 1
fi

cp "$SRC" "$DEST"
echo "apply-branding-assets: installed $SRC -> $DEST"
ls -lh "$DEST"
