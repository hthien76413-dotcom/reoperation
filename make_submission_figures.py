# -*- coding: utf-8 -*-
"""按 Pediatric Surgery International 的 Artwork Guidelines 生成投稿用图。

官方规定（Artwork and Illustrations Guidelines）与本稿的对应处理：

  · 「For vector graphics, the preferred format is EPS; for halftones, please
     use TIFF format.」→ 四张图里三张是纯矢量、无透明度，直接出 EPS；
     Figure S1 的置信带用 alpha 透明（EPS 不支持透明，改实色会让两条带
     互相遮挡、丢失信息），故只有它走位图 TIFF。
  · 「Combination artwork should have a minimum resolution of 600 dpi.」
     → Figure S1 按 600 dpi 出图后转 TIFF。EPS 为矢量，不受 dpi 门槛约束，
     这也是 Figure 1（流程图，line art 位图需 1200 dpi）走 EPS 的原因——
     1200 dpi 的无压缩 TIFF 约 300 MB，投稿系统无法接受。
  · 「Name your figure files with "Fig" and the figure number, e.g., Fig1.eps」
     → 输出统一命名 Fig1 / Fig2 / FigS1 / FigS2，与出图脚本的工作文件名解耦。
  · 「Vector graphics containing fonts must have the fonts embedded」
     → 出图脚本在保存 EPS 前设 ps.fonttype=42（TrueType 嵌入），本脚本校验。

先跑四个出图脚本，再跑本脚本。产物已 gitignore，投稿前跑一次即可。

用法：  python3 make_submission_figures.py
"""
import os
import shutil
import sys

from PIL import Image

# (出图脚本的工作文件名, 投稿文件名, 格式)
FIGURES = [
    ("Figure1_flow_EN",             "Fig1",  "eps"),
    ("Figure2_duodenal_by_age",     "Fig2",  "eps"),
    ("FigureS1_CIF_reoperation_EN", "FigS1", "tif"),   # 有 alpha，只能位图
    ("FigureS2_cause_by_approach",  "FigS2", "eps"),
]
TIFF_DPI = 600          # combination art 官方下限


def do_eps(stem, out_stem):
    src = stem + ".eps"
    if not os.path.exists(src):
        return None, "缺 %s（先跑对应出图脚本）" % src
    out = out_stem + ".eps"
    shutil.copyfile(src, out)
    blob = open(out, "rb").read()
    if b"/FontType" not in blob:
        return out, "★ 未检出字体嵌入，请检查 ps.fonttype 设置"
    return out, "矢量 EPS，字体已嵌入，%.1f KB" % (os.path.getsize(out) / 1024)


def do_tiff(stem, out_stem):
    src = stem + ".png"
    if not os.path.exists(src):
        return None, "缺 %s（先跑对应出图脚本）" % src
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
    out = out_stem + ".tif"
    # LZW 无损压缩：官方未要求 uncompressed（那是 Surg Endosc 的规定），
    # 600 dpi 无压缩约 90 MB，压缩后可控且像素完全一致。
    im.save(out, format="TIFF", compression="tiff_lzw", dpi=(TIFF_DPI, TIFF_DPI))
    dpi = im.info.get("dpi", ("?", "?"))
    note = ""
    if isinstance(dpi[0], (int, float)) and dpi[0] < TIFF_DPI:
        note = "  ★ 源 PNG 分辨率不足，请确认出图脚本已按 %d dpi 保存" % TIFF_DPI
    return out, "位图 TIFF %dx%d，%.1f MB%s" % (
        im.size[0], im.size[1], os.path.getsize(out) / 1e6, note)


def main():
    print("Pediatric Surgery International 投稿图打包")
    print("（EPS 为矢量首选；仅含透明度的 Figure S1 走 600 dpi TIFF）\n")
    missing, warned = [], False
    for stem, out_stem, kind in FIGURES:
        out, info = (do_eps if kind == "eps" else do_tiff)(stem, out_stem)
        if out is None:
            missing.append(stem)
        if "★" in info:
            warned = True
        print("  %-8s ← %-30s %s" % (out or "—", stem, info))

    if missing:
        print("\n★ 以下图缺少源文件，请先运行对应出图脚本：")
        for s in missing:
            print("   -", s)
        sys.exit(1)
    if warned:
        print("\n★ 有告警项，请按提示检查后重跑。")
        sys.exit(1)
    print("\n完成。上传时用 Fig1 / Fig2 / FigS1 / FigS2 这四个文件。")


if __name__ == "__main__":
    main()
