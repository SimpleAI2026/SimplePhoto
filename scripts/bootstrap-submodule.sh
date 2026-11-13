#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIN="e052eabf4be74612725400955d184f85d208c0f0"
cd "$ROOT"
git submodule update --init --recursive
git -C thirdparty/photocraft fetch origin
git -C thirdparty/photocraft checkout "$PIN"
echo "photocraft HEAD=$(git -C thirdparty/photocraft rev-parse HEAD)"
test "$(git -C thirdparty/photocraft rev-parse HEAD)" = "$PIN"
