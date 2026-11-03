#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIN="287352bf92d56817db9a510e506551f394a68ea4"
cd "$ROOT"
git submodule update --init --recursive
git -C thirdparty/photocraft fetch origin
git -C thirdparty/photocraft checkout "$PIN"
echo "photocraft HEAD=$(git -C thirdparty/photocraft rev-parse HEAD)"
test "$(git -C thirdparty/photocraft rev-parse HEAD)" = "$PIN"
