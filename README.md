# SimplePhoto

Chrome MV3 扩展：将 [PhotoCraft](https://github.com/storytold/photocraft) 的 WASM/web 构建嵌入扩展页面，作为本地图片编辑器。

- 实现计划：见 [`plan/`](plan/)（从 [`plan/README.md`](plan/README.md) 开始）
- PhotoCraft 以 git submodule 形式放在 `thirdparty/photocraft`（计划钉住 SHA `287352bf92d56817db9a510e506551f394a68ea4`）
- 对 PhotoCraft 的必要改动一律用 `patches/` 中的 patch 文件维护，不要把脏 submodule 当作长期方案

当前仓库仅有计划文档与已检出的 `thirdparty/photocraft`；扩展实现按 `plan/01-*.md` 起逐步执行。
