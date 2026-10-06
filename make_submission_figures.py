# -*- coding: utf-8 -*-
"""按 Pediatric Surgery International 的 Artwork Guidelines 生成投稿用图。

**2026-09-11：按作者要求改为一律输出 PNG。** 原先是 EPS（三张矢量）+ TIFF
（Figure S1），那更贴合官方首选格式；若投稿系统退回 PNG，把 `FIGURES` 里的
格式字段改回 "eps"/"tif" 重跑即可，`do_eps` / `do_tiff` 两个函数都保留着。

官方规定与本脚本的对应处理：

  · 格式：「For vector graphics, the preferred format is EPS; for halftones,
     please use TIFF format.」——PNG 不在这句话里，属于让步选择，故位图的
     分辨率必须足量，不能再靠矢量绕开 dpi 门槛。
  · 分辨率：line art 1200 dpi / halftone 300 dpi / combination art 600 dpi。
     Figure 1 是纯线条图（矩形框+连线+文字，无半色调）→ **1200 dpi**；
     其余三张含色块、曲线与文字，属 combination art → **600 dpi**。
     这些 dpi 由各出图脚本的 savefig 决定，本脚本只校验，不重采样——
     放大低分辨率位图不会增加信息，只会骗过检查。
  · 命名：「Name your figure files with "Fig" and the figure number」
     → 输出统一为 Fig1 / Fig2 / FigS1 / FigS2，与出图脚本的工作文件名解耦。

PNG 一律合成到白底并转 RGB：出图脚本存的是 RGBA，透明通道在部分排版软件里
会被渲染成黑色。

先跑四个出图脚本，再跑本脚本。产物已 gitignore，投稿前跑一次即可。

用法：  python3 make_submission_figures.py
"""
import os
import shutil
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None      # 1200 dpi 的流程图约 1.0 亿像素，超过 PIL 默认上限

# (出图脚本的工作文件名, 投稿文件名, 格式, 该图的 dpi 下限)
FIGURES = [
    ("Figure1_flow_EN",             "Fig1",  "png", 1200),   # line art
    ("Figure2_duodenal_by_age",     "Fig2",  "png",  600),   # combination art
    ("FigureS1_CIF_reoperation_EN", "FigS1", "png",  600),
    ("FigureS2_cause_by_approach",  "FigS2", "png",  600),
]


def _flatten(src):
    """读入 PNG，把透明区合成到白底并转 RGB，返回 (图像, 源 dpi)。"""
    im = Image.open(src)
    dpi = im.info.get("dpi", (None, None))[0]
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    return im, dpi


def _dpi_note(dpi, floor):
    if dpi is None:
        return "  ★ 源图未记录 dpi，请检查出图脚本的 savefig"
    if dpi < floor - 1:                       # 容差：matplotlib 写的是 599.9988
        return "  ★ 仅 %d dpi，低于本图要求的 %d dpi，请改出图脚本的 savefig 后重跑" % (
            round(dpi), floor)
    return ""


def do_png(stem, out_stem, floor):
    src = stem + ".png"
    if not os.path.exists(src):
        return None, "缺 %s（先跑对应出图脚本）" % src
    im, dpi = _flatten(src)
    out = out_stem + ".png"
    im.save(out, format="PNG", dpi=(dpi or floor, dpi or floor), optimize=True)
    return out, "PNG %dx%d，%d dpi，%.1f MB%s" % (
        im.size[0], im.size[1], round(dpi or 0), os.path.getsize(out) / 1e6,
        _dpi_note(dpi, floor))


def do_eps(stem, out_stem, floor=None):
    """保留：EPS 是该刊对矢量图的首选格式，退回 PNG 时改 FIGURES 即可启用。"""
    src = stem + ".eps"
    if not os.path.exists(src):
        return None, "缺 %s（先跑对应出图脚本）" % src
    out = out_stem + ".eps"
    shutil.copyfile(src, out)
    if b"/FontType" not in open(out, "rb").read():
        return out, "★ 未检出字体嵌入，请检查 ps.fonttype 设置"
    return out, "矢量 EPS，字体已嵌入，%.1f KB" % (os.path.getsize(out) / 1024)


def do_tiff(stem, out_stem, floor=600):
    """保留：该刊对半色调图的首选格式。LZW 无损压缩，像素与源 PNG 完全一致。"""
    src = stem + ".png"
    if not os.path.exists(src):
        return None, "缺 %s（先跑对应出图脚本）" % src
    im, dpi = _flatten(src)
    out = out_stem + ".tif"
    im.save(out, format="TIFF", compression="tiff_lzw",
            dpi=(dpi or floor, dpi or floor))
    return out, "位图 TIFF %dx%d，%d dpi，%.1f MB%s" % (
        im.size[0], im.size[1], round(dpi or 0), os.path.getsize(out) / 1e6,
        _dpi_note(dpi, floor))


HANDLER = {"png": do_png, "eps": do_eps, "tif": do_tiff}


def main():
    print("Pediatric Surgery International 投稿图打包（PNG）")
    print("line art 需 1200 dpi，combination art 需 600 dpi；本脚本只校验不重采样\n")
    missing, warned = [], False
    for stem, out_stem, kind, floor in FIGURES:
        out, info = HANDLER[kind](stem, out_stem, floor)
        if out is None:
            missing.append(stem)
        if "★" in info:
            warned = True
        print("  %-9s ← %-30s %s" % (out or "—", stem, info))

    if missing:
        print("\n★ 以下图缺少源文件，请先运行对应出图脚本：")
        for s in missing:
            print("   -", s)
        sys.exit(1)
    if warned:
        print("\n★ 有告警项，请按提示检查后重跑。")
        sys.exit(1)
    print("\n完成。上传时用 Fig1 / Fig2 / FigS1 / FigS2 这四个文件。")
    print("若系统因 PNG 不在首选格式内退回，把 FIGURES 的格式字段改回"
          " eps（Fig1/Fig2/FigS2）与 tif（FigS1）重跑即可。")


if __name__ == "__main__":
    main()
