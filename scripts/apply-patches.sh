#!/usr/bin/env bash
# Apply patches/*.patch onto thirdparty/photocraft (submodule).
# No-op success when patches/ has no *.patch files (e.g. only .gitkeep).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PC="$ROOT/thirdparty/photocraft"
PATCH_DIR="$ROOT/patches"

if [ ! -d "$PC/.git" ] && [ ! -f "$PC/.git" ]; then
  echo "error: photocraft submodule missing at $PC — run ./scripts/bootstrap-submodule.sh" >&2
  exit 1
fi

shopt -s nullglob
patches=("$PATCH_DIR"/*.patch)
if [ "${#patches[@]}" -eq 0 ]; then
  echo "apply-patches: no patches/*.patch — nothing to apply (OK)"
  exit 0
fi

cd "$PC"
for p in "${patches[@]}"; do
  echo "applying $(basename "$p")"
  git apply --check "$p"
  git apply "$p"
done
echo "apply-patches: applied ${#patches[@]} patch(es)"
