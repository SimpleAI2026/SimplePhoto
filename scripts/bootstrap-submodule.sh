#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIN="3d60ad01f941519307c755eed8e0896d6274cde6"
cd "$ROOT"
git submodule update --init --recursive
git -C thirdparty/photocraft fetch origin
git -C thirdparty/photocraft checkout "$PIN"
echo "photocraft HEAD=$(git -C thirdparty/photocraft rev-parse HEAD)"
test "$(git -C thirdparty/photocraft rev-parse HEAD)" = "$PIN"
