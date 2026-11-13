#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIN="2239ee9cb6c87583242ccd247f0a621f3d4d90ee"
cd "$ROOT"
git submodule update --init --recursive
git -C thirdparty/photocraft fetch origin
git -C thirdparty/photocraft checkout "$PIN"
echo "photocraft HEAD=$(git -C thirdparty/photocraft rev-parse HEAD)"
test "$(git -C thirdparty/photocraft rev-parse HEAD)" = "$PIN"
