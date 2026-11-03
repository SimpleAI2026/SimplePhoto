# SimplePhoto

Chrome MV3 扩展：把 [PhotoCraft](https://github.com/storytold/photocraft) 的 WASM/web 编辑器嵌进扩展全页，做本地图片编辑（Open / Save·Export 走浏览器下载语义）。

实现计划见 [`plan/`](plan/)（从 [`plan/README.md`](plan/README.md) 开始）。PhotoCraft 以 submodule 钉在 `thirdparty/photocraft`（SHA `287352bf92d56817db9a510e506551f394a68ea4`）。对上游的必要改动只放 `patches/*.patch`，不要长期保留脏 submodule。

## 快速开始（Load unpacked）

```bash
cd /Volumes/my/github/SimplePhoto
./scripts/bootstrap-submodule.sh
./scripts/apply-patches.sh          # 无 patch 时 no-op 成功
./scripts/apply-branding-assets.sh  # 安装 SimplePhoto 顶栏图标（避免二进制 patch）
./scripts/build-web-assets.sh       # 需要 trunk；已有产物可用 --skip-build
./scripts/check-extension-size.sh
```

Chrome → `chrome://extensions` → 开发者模式 → **加载已解压的扩展程序** → 选本仓库的 `extension/` → 点工具栏图标打开编辑器 → Open 图片 → Export/Save 下载。

可选打包（产物在 gitignore 的 `dist/`）：

```bash
./scripts/package-extension.sh --skip-build   # 或省略 --skip-build 做全量重建
```

## 说明

- v0：全页编辑器、web 下载语义；无 downloads 桥、无 PhotoCraft 源码 patch。
- 平台约定：`extension/PLATFORM.md`
- Patch 工作流：`plan/patches.md`
- 下一里程碑（i18n / SimplePhoto 品牌 / logo）：[`plan/08-i18n-branding-logo.md`](plan/08-i18n-branding-logo.md)
