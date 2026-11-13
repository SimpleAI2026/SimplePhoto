#!/usr/bin/env python3
"""Generate tutorials/src/zh-hant from zh-hans with glossary + term map + zhconv."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tutorials" / "src"
GLOSSARY = ROOT / "tutorials" / "i18n" / "menu-glossary.json"

# Longest-first manual terms (Taiwan-leaning Photoshop / UI wording).
# Applied after glossary substitutions and before/with OpenCC-style conversion.
TERMS = [
    ("文档位于扩展内部", "這些頁面位於擴充功能內部"),
    ("不必访问外部教程网站", "不必前往外部教學網站"),
    ("这份教程", "這份教學"),
    ("外部教程网站", "外部教學網站"),
    ("开源项目", "開源專案"),
    ("Chrome 扩展", "Chrome 擴充功能"),
    ("本扩展", "本擴充功能"),
    ("生成式扩展", "生成式擴充"),
    ("扩展并补全", "擴充並補全"),
    ("打开扩展后", "開啟擴充功能後"),
    ("打开扩展", "開啟擴充功能"),
    ("扩展内部", "擴充功能內部"),
    ("作为 Chrome", "作為 Chrome"),

    ("选择与蒙版", "選取並遮住"),
    ("智能对象", "智慧型物件"),
    ("历史记录", "步驟記錄"),
    ("污点修复画笔", "污點修復筆刷"),
    ("修复画笔", "修復筆刷"),
    ("仿制图章", "仿製印章"),
    ("快速选择", "快速選取"),
    ("对象选择", "物件選取"),
    ("自由变换", "任意變形"),
    ("图层蒙版", "圖層遮色片"),
    ("层蒙版", "層遮色片"),
    ("蒙版", "遮色片"),
    ("画笔", "筆刷"),
    ("色阶", "色階"),
    ("图像大小", "影像尺寸"),
    ("画布大小", "畫布大小"),
    ("另存为", "另存新檔"),
    ("导出为", "匯出為"),
    ("快速导出", "快速匯出"),
    ("文件菜单", "檔案選單"),
    ("主页", "首頁"),
    ("窗口", "視窗"),
    ("视图", "檢視"),
    ("帮助", "說明"),
    ("软件", "軟體"),
    ("默认", "預設"),
    ("设置", "設定"),
    ("质量", "品質"),
    ("分辨率", "解析度"),
    ("屏幕", "螢幕"),
    ("视频", "影片"),
    ("信息", "資訊"),
    ("数据", "資料"),
    ("程序", "程式"),
    ("计算机", "電腦"),
    ("快捷键", "快捷鍵"),
    ("右键", "右鍵"),
    ("单击", "點一下"),
    ("点击", "點選"),
    ("粘贴", "貼上"),
    ("选区", "選取範圍"),
    ("魔棒", "魔術棒"),
    ("混合模式", "混合模式"),
    ("不透明度", "不透明度"),
    ("图像", "影像"),
    ("文档", "文件"),
    ("文件夹", "資料夾"),
    ("打开", "開啟"),
    ("保存", "儲存"),
    ("新建", "新增"),
    ("导出", "匯出"),
    ("文件", "檔案"),  # File menu / files on disk; after 文档→文件 and 文件夹
    ("导入", "導入"),
    ("复选", "勾選"),
    ("算法", "演算法"),
    ("内存", "記憶體"),
    ("缓存", "快取"),
    ("图层组", "圖層群組"),
    ("分组", "分組"),
    ("菜单", "選單"),
    ("界面", "介面"),
    ("支持", "支援"),
    ("访问", "前往"),
    ("打印", "列印"),
    ("默认", "預設"),
    ("里", "裡"),

]


def load_zhconv():
    for path in ("/tmp/venv-zh/bin/python", sys.executable):
        pass
    try:
        import zhconv  # type: ignore
        return zhconv
    except ImportError:
        sys.path.insert(0, "/tmp/venv-zh/lib/python3.14/site-packages")
        try:
            import zhconv  # type: ignore
            return zhconv
        except ImportError:
            sys.path[0] = "/tmp/venv-zh/lib/python3.13/site-packages"
            import zhconv  # type: ignore
            return zhconv


def apply_pairs(text: str, pairs: list[tuple[str, str]]) -> str:
    # longest first
    for src, dst in sorted(pairs, key=lambda kv: len(kv[0]), reverse=True):
        if src and dst and src != dst:
            text = text.replace(src, dst)
    return text


def convert(text: str, glossary_pairs: list[tuple[str, str]], zhconv) -> str:
    # Long phrases first, so glossary terms like 打开→開啟 cannot split them.
    text = apply_pairs(text, TERMS)
    text = apply_pairs(text, glossary_pairs)
    text = zhconv.convert(text, "zh-hant")
    text = apply_pairs(text, TERMS)
    text = apply_pairs(text, glossary_pairs)
    text = text.replace("擴展", "擴充功能")
    return text


def main() -> None:
    zhconv = load_zhconv()
    g = json.loads(GLOSSARY.read_text(encoding="utf-8"))
    glossary_pairs = []
    for en_key, hans in g.get("zh-hans", {}).items():
        hant = g.get("zh-hant", {}).get(en_key, "")
        if hans and hant:
            glossary_pairs.append((hans, hant))
    src_dir = SRC / "zh-hans"
    dest_dir = SRC / "zh-hant"
    dest_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for src in sorted(src_dir.glob("*.html")):
        dest = dest_dir / src.name
        dest.write_text(convert(src.read_text(encoding="utf-8"), glossary_pairs, zhconv), encoding="utf-8", newline="\n")
        n += 1
    print(f"wrote {n} zh-hant chapters to {dest_dir}")


if __name__ == "__main__":
    main()
