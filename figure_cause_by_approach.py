# -*- coding: utf-8 -*-
"""Supplementary Figure S2：再手术病因 × 首台入路（Table 3 的图形化）。
（2026-07-26 由 Figure 3 升为 Figure 2；2026-07-28 因 JPS 图表数上限（表+图≤6）
  且本图内容与 Table 3 重复，降为 Supplementary Figure S2，正文改保留 Table 3。
  文件名不再带编号，避免今后重编号时又要改脚本。）

设计要点：
  · 形式=横向分组条形图。病因构成对比的关键是"逐类比长短"，分组条共用基线，
    优于堆叠条（堆叠段不共基线，难以跨组比较单一段落）。
  · 颜色=入路（2 类），而非病因（6 类）。全图只有一套颜色语义，避免歧义；
    也把"6 类颜色"降为"2 类颜色"，远低于分类色上限。
  · 蓝 #2a78d6 / 橙 #eb6834 = 参考调色板 slot 1/2，已过验证器全部六项检查
    （worst adjacent CVD ΔE 24.7，normal-vision 33.6，对比度均 ≥3:1）。
  · 误差线=Wilson 95%CI；显著者直接标注 OR 与 p，其余不标（避免"每点一个数"）。
  · 顶部标注总体率无差异，与图内"病因构成截然不同"形成对照——即本文核心论点。
输出 300dpi PNG + 矢量 PDF。
"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.stats import fisher_exact
from _dataprep import load, approach, reop_in_cohort, adjudicated

# ---------- 数据 ----------
D = load(); ADJ = adjudicated(); R = reop_in_cohort(); first = D["first"]; malrot = D["malrot"]
LAP = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
OPR = [p for p in malrot if approach(first[p]) != "腹腔镜完成"]
N_LAP, N_OPR = len(LAP), len(OPR)

CAUSES = [
    ("十二指肠持续梗阻",        "Persistent duodenal obstruction"),
    ("肠坏死/穿孔/吻合口并发症", "Necrosis / perforation /\nanastomotic complication"),
    ("粘连性肠梗阻",            "Adhesive obstruction\n(non-duodenal)"),
    ("合并畸形漏诊",            "Missed associated anomaly"),
    ("肠扭转复发",              "Recurrent volvulus / redo-Ladd"),
    ("其他",                    "Other"),
]
# 仅标注 Holm 校正后仍显著者；标注内容与 p 值一律【就地计算】，不写死。
# 2026-07-28：原写死 "OR 10.98, Holm p=0.027" 系 466 例旧队列的值，且现在开腹侧
# 零事件、OR 已不可估，只能报风险差——故改为算 RD 而非 OR。
def wilson(x, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = x / n; den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den
    h = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return max(0.0, c-h)*100, min(1.0, c+h)*100

rows = []
for zh, en in CAUSES:
    a = sum(1 for p in LAP if p in R and ADJ[p]["cause"] == zh)
    b = sum(1 for p in OPR if p in R and ADJ[p]["cause"] == zh)
    rows.append(dict(en=en, zh=zh, a=a, b=b,
                     ra=a/N_LAP*100, rb=b/N_OPR*100,
                     ca=wilson(a, N_LAP), cb=wilson(b, N_OPR)))
rows.sort(key=lambda r: r["ra"], reverse=True)          # 按腹腔镜率降序

tot_a = sum(r["a"] for r in rows); tot_b = sum(r["b"] for r in rows)

# ---------- 就地重算标注（与 Table 2 / Table 4 同口径） ----------
# 六个病因的 Fisher 精确 p，按 Holm 逐步降序校正（与 Table 2 一致）
praw = {r["zh"]: fisher_exact([[r["a"], N_LAP - r["a"]],
                               [r["b"], N_OPR - r["b"]]])[1] for r in rows}
order = sorted(praw, key=praw.get)
HOLM, run = {}, 0.0
for i, zh in enumerate(order):
    run = max(run, (len(order) - i) * praw[zh])
    HOLM[zh] = min(1.0, run)

def newcombe_rd(a, na, b, nb, z=1.96):
    """风险差的 Newcombe 混合 Wilson 区间（零事件时仍有定义，OR 则不可估）。"""
    l1, u1 = [v / 100 for v in wilson(a, na, z)]
    l2, u2 = [v / 100 for v in wilson(b, nb, z)]
    d = a / na - b / nb
    lo = d - math.sqrt((a / na - l1) ** 2 + (u2 - b / nb) ** 2)
    hi = d + math.sqrt((u1 - a / na) ** 2 + (b / nb - l2) ** 2)
    return d * 100, lo * 100, hi * 100

ANNOT = {}
for r in rows:
    if HOLM[r["zh"]] < 0.05:
        d, lo, hi = newcombe_rd(r["a"], N_LAP, r["b"], N_OPR)
        ANNOT[r["zh"]] = "risk difference +%.1f pp, Holm p=%.3f" % (d, HOLM[r["zh"]])

# 总体率比较的精确 p（Figure 副标题用；对应 Table 4 的 crude 行）
P_OVERALL = fisher_exact([[tot_a, N_LAP - tot_a], [tot_b, N_OPR - tot_b]])[1]

# ---------- 样式 ----------
SURFACE = "#fcfcfb"; INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#898781"
GRID = "#e1e0d9"; AXIS = "#c3c2b7"
C_LAP, C_OPR = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"]})

fig, ax = plt.subplots(figsize=(9.0, 5.2))
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)

y = range(len(rows))
H = 0.30                       # 细条
OFF = 0.17                     # 组内偏移，留出条间空隙
for i, r in enumerate(rows):
    # 蓝(腹腔镜)在上，与图例顺序一致
    ax.barh(i - OFF, r["ra"], height=H, color=C_LAP, zorder=3)
    ax.barh(i + OFF, r["rb"], height=H, color=C_OPR, zorder=3)
    ax.text(r["ra"] + 0.14, i - OFF, f'{r["a"]}', va="center", ha="left",
            fontsize=8.6, color=INK2, zorder=6)
    ax.text(r["rb"] + 0.14, i + OFF, f'{r["b"]}', va="center", ha="left",
            fontsize=8.6, color=INK2, zorder=6)
    if r["zh"] in ANNOT:
        ax.text(r["ra"] + 0.75, i - OFF, ANNOT[r["zh"]], va="center", ha="left",
                fontsize=8.8, color=INK, fontweight="bold", zorder=6)

ax.set_yticks(list(y)); ax.set_yticklabels([r["en"] for r in rows], fontsize=9.4, color=INK)
ax.invert_yaxis()
ax.set_ylim(len(rows) - 0.45, -0.75)
ax.set_xlabel("Reoperations per 100 children undergoing that approach",
              fontsize=9.4, color=INK2, labelpad=8)
ax.set_xlim(0, 11.0)          # 留出右侧空间给风险差标注（比原 OR 标注长）
ax.xaxis.set_major_formatter(lambda v, _: f"{v:g}")
ax.tick_params(axis="x", colors=MUTED, labelsize=8.8, length=0)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
ax.spines["left"].set_color(AXIS); ax.spines["left"].set_linewidth(0.9)

# 标题与副标题（分行，避免溢出）
ax.set_title("Cause of unplanned early reoperation, by index surgical approach",
             fontsize=12.0, color=INK, fontweight="bold", loc="left", pad=62)
ax.text(0, 1.155, f"No difference detected in the overall rate — laparoscopic {tot_a}/{N_LAP} ({tot_a/N_LAP*100:.1f}%) "
                  f"vs. open-related {tot_b}/{N_OPR} ({tot_b/N_OPR*100:.1f}%), p={P_OVERALL:.2f}.",
        transform=ax.transAxes, fontsize=9.4, color=INK2, va="bottom")
ax.text(0, 1.095, "The composition differed: duodenal obstruction after laparoscopy, "
                  "necrosis and perforation after open surgery.",
        transform=ax.transAxes, fontsize=9.4, color=INK, va="bottom", fontweight="bold")

# 图例置于数据区外（右下空白），横排
# 图例移到绘图区之上、副标题之下，横排，完全脱离数据区
ax.legend(handles=[Patch(facecolor=C_LAP, label=f"Laparoscopic completion (n={N_LAP})"),
                   Patch(facecolor=C_OPR, label=f"Open-related (n={N_OPR})")],
          loc="lower left", bbox_to_anchor=(0.0, 1.005), ncol=2, frameon=False,
          fontsize=9.2, labelcolor=INK, handlelength=1.4, handleheight=0.95,
          columnspacing=2.4, borderpad=0.0, handletextpad=0.6)
fig.text(0.012, 0.052,
         "Bars are cause-specific rates with the full approach group as the denominator; numerals are event counts. 95% CIs in Table 2.",
         fontsize=8.0, color=MUTED)
fig.text(0.012, 0.014,
         "The duodenal-obstruction comparison is confounded by age and is shown stratified in Figure 2.",
         fontsize=8.0, color=MUTED)

fig.tight_layout(rect=[0, 0.082, 1, 0.99])
fig.savefig("FigureS2_cause_by_approach.png", dpi=300, facecolor=SURFACE)
fig.savefig("FigureS2_cause_by_approach.pdf", facecolor=SURFACE)
print("saved FigureS2_cause_by_approach.png / .pdf")
for r in rows:
    print(f'  {r["en"][:38]:<40} lap {r["a"]:>2}/{N_LAP} = {r["ra"]:.1f}%   opr {r["b"]:>2}/{N_OPR} = {r["rb"]:.1f}%')
