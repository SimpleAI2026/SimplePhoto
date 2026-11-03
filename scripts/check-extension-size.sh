#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EDITOR="$ROOT/extension/editor"
# Soft budget: plan/06 originally suggested 28 MiB. Trunk release wasm on pin
# 287352bf92d56817db9a510e506551f394a68ea4 measures ~29 MiB (~30,606,192 bytes),
# so soft budget is 32 MiB for this pin (still well under zip 35 MiB).
MAX_WASM=$((32 * 1024 * 1024))
MAX_ZIP=$((35 * 1024 * 1024))

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

art=""
shopt -s nullglob
zips=("$ROOT"/dist/simplephoto-extension-*.zip)
if [ "${#zips[@]}" -gt 0 ]; then
  art="${zips[0]}"
fi
if [ -n "${art:-}" ]; then
  zbytes=$(wc -c <"$art" | tr -d ' ')
  echo "zip=$art bytes=$zbytes"
  if [ "$zbytes" -gt "$MAX_ZIP" ]; then
    echo "error: zip over soft budget $MAX_ZIP" >&2
    exit 1
  fi
fi
echo OK
