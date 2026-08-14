# -*- coding: utf-8 -*-
"""把出图脚本产出的 PNG 转成投稿用的 uncompressed TIFF。

缘由：Surgical Endoscopy 的 Instructions for Authors（2025-07 版）规定
「Provide each figure as a single image file in either uncompressed TIFF, GIF,
JPEG, or EPS format」——PNG 不在允许之列。本脚本只做格式转换，不改动像素内容。

不选其它格式的理由：
  · JPEG 有损，图中文字与细线会出现压缩伪影
  · EPS 为矢量、体积最小，但本稿 FigureS1 的置信带用了 alpha 透明，
    EPS 不支持透明，会渲染错误；且容器内无 ghostscript
  · 故统一用 uncompressed TIFF（官方列表中的首选，且无损）

产物较大（合计约 50 MB，官方上限 500 MB），且完全可由 PNG 复现，
因此 .tif 已加入 .gitignore，不入库；投稿前跑一次本脚本即可。

用法：  python3 make_submission_figures.py
"""
import os
import sys

from PIL import Image

FIGURES = [
    "Figure1_flow_EN",
    "Figure2_duodenal_by_age",
    "FigureS1_CIF_reoperation_EN",
    "FigureS2_cause_by_approach",
]
DPI = (300, 300)


def to_tiff(stem):
    src = stem + ".png"
    if not os.path.exists(src):
        return None, "源文件缺失"
    im = Image.open(src)
    # PNG 可能带 alpha 通道。投稿 TIFF 一律转 RGB，并把透明区合成到白底上，
    # 否则部分排版软件会把透明区渲染成黑色。
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    out = stem + ".tif"
    im.save(out, format="TIFF", compression="none", dpi=DPI)
    return out, "%dx%d, %.1f MB" % (im.size[0], im.size[1], os.path.getsize(out) / 1e6)


def main():
    total = 0
    missing = []
    for stem in FIGURES:
        out, info = to_tiff(stem)
        if out is None:
            missing.append(stem)
            print("  %-32s %s" % (stem, info))
            continue
        total += os.path.getsize(out)
        print("  %-32s → %-34s %s" % (stem + ".png", out, info))
    print("合计 %.1f MB（Surg Endosc 单次投稿全部文件上限 500 MB）" % (total / 1e6))
    if missing:
        print("以下图未生成，请先运行对应出图脚本：", ", ".join(missing))
        sys.exit(1)


if __name__ == "__main__":
    main()
