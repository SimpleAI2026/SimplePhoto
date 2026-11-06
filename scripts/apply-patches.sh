#!/usr/bin/env bash
# Apply patches/*.patch onto thirdparty/photocraft (submodule) from the pinned baseline.
# No-op success when patches/ has no *.patch files (e.g. only .gitkeep).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PC="$ROOT/thirdparty/photocraft"
PATCH_DIR="$ROOT/patches"
PIN="3d60ad01f941519307c755eed8e0896d6274cde6"

if [ ! -d "$PC/.git" ] && [ ! -f "$PC/.git" ]; then
  echo "error: photocraft submodule missing at $PC — run ./scripts/bootstrap-submodule.sh" >&2
  exit 1
fi

cd "$PC"
HEAD=$(git rev-parse HEAD)
if [[ "$HEAD" != "$PIN" ]]; then
  echo "error: photocraft HEAD=$HEAD, expected $PIN (refuse to apply on wrong base)" >&2
  exit 1
fi
git reset --hard "$PIN"

shopt -s nullglob
patches=("$PATCH_DIR"/*.patch)
if [ "${#patches[@]}" -eq 0 ]; then
  echo "apply-patches: no patches/*.patch — nothing to apply (OK)"
  exit 0
fi

for p in "${patches[@]}"; do
  echo "applying $(basename "$p")"
  git apply --check "$p"
  git apply "$p"
done
echo "apply-patches: applied ${#patches[@]} patch(es) on $PIN"
git status -sb
echo "note: run ./scripts/apply-branding-assets.sh after patches to install SimplePhoto app icon"
