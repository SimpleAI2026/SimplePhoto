#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EDITOR="$ROOT/extension/editor"
# Soft budget: plan/06 originally suggested 28 MiB. Trunk release wasm grew with
# the photocraft pin: ~29 MiB on 287352bf, ~30 MiB on 3d60ad01, ~37.6 MiB on
# e052eabf4 (updated pin). Allow 40 MiB wasm / 40 MiB zip
# (still far below Chrome Web Store package limits).
MAX_WASM=$((40 * 1024 * 1024))
MAX_ZIP=$((40 * 1024 * 1024))

shopt -s nullglob
wasms=("$EDITOR"/*_bg.wasm)
if [ "${#wasms[@]}" -eq 0 ]; then
  echo "error: no *_bg.wasm under $EDITOR" >&2
  exit 1
fi
if [ "${#wasms[@]}" -gt 1 ]; then
  echo "error: multiple *_bg.wasm under $EDITOR: ${wasms[*]}" >&2
  exit 1
fi
wasm="${wasms[0]}"
bytes=$(wc -c <"$wasm" | tr -d ' ')
echo "wasm=$wasm bytes=$bytes"
if [ "$bytes" -gt "$MAX_WASM" ]; then
  echo "error: wasm over soft budget $MAX_WASM" >&2
  exit 1
fi

shopt -s nullglob
zips=("$ROOT"/dist/simplephoto-extension-*.zip)
for art in "${zips[@]}"; do
  zbytes=$(wc -c <"$art" | tr -d ' ')
  echo "zip=$art bytes=$zbytes"
  if [ "$zbytes" -gt "$MAX_ZIP" ]; then
    echo "error: zip over soft budget $MAX_ZIP" >&2
    exit 1
  fi
done
echo OK
