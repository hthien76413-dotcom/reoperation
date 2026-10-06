# -*- coding: utf-8 -*-
"""Figure 2（原 Figure 3，2026-07-28 因旧 Figure 2 移出正文而顺移编号）：
十二指肠持续梗阻的年龄双峰与分层比较。

为什么需要这张图：
  粗比较把两个互不相干的人群混在一起。12 例的年龄是 3.7–11 天(6例) 与
  6.6–13.1 岁(6例)，中间【一例都没有】；分层后信号只存在于新生儿层
  (6/142 vs 0/163)，大龄层没有 (6/71 vs 0/13)。
  表格给不出"中间是空的"这个事实，点图能。

设计：
  · 左panel = 12 例逐例点图，x=年龄(对数天)。一眼看见双峰与空白区。
  · 右panel = 分层率(分母=该层该术式全部患儿)，与左panel共用颜色语义。
  · 颜色=入路，与 Figure 2 完全一致（蓝 #2a78d6 腹腔镜完成 / 橙 #eb6834 开腹相关）。
  · 分层背景带用极浅灰，不引入第三种颜色语义。
  · 例数、年龄区间、分层 p 值一律【就地计算】，不写死——2026-07-28 曾因写死
    n=14 / p=0.009 而与正文脱节，且当时误用未按队列收缩的 reop_set()。
输出 300dpi PNG + 矢量 PDF。
"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.stats import fisher_exact
from _dataprep import load, approach, reop_in_cohort, adjudicated, AGE_BANDS

D = load(); A = adjudicated(); R = reop_in_cohort()   # 必须是队列内结局（n=36），不是裁定表的 39
malrot, first, AGED = D["malrot"], D["first"], D["age_d"]
is_lap = lambda p: approach(first[p]) == "腹腔镜完成"

cases = sorted([(AGED[p], is_lap(p)) for p in R
                if A[p]["cause"] == "十二指肠持续梗阻" and AGED.get(p) is not None])
NEO = [a for a, _ in cases if a < 28]
OLD = [a for a, _ in cases if a >= 365.25]

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, BAND = "#e1e0d9", "#c3c2b7", "#f2f1ec"
C_LAP, C_OPR = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"]})

fig, (axA, axB) = plt.subplots(1, 2, figsize=(10.0, 4.6),
                               gridspec_kw=dict(width_ratios=[1.30, 1.0], wspace=0.28))
fig.patch.set_facecolor(SURFACE)
for ax in (axA, axB):
    ax.set_facecolor(SURFACE)
    ax.set_axisbelow(True)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(AXIS); ax.spines[sp].set_linewidth(0.9)
    ax.tick_params(colors=MUTED, labelsize=8.6, length=0)

# ---------------- Panel A：逐例年龄点图 ----------------
XMIN, XMAX = 1.5, 9000
axA.axvspan(XMIN, 28, color=BAND, zorder=0)
axA.axvspan(365.25, XMAX, color=BAND, zorder=0)
# 同龄者上下对称错开，避免重叠；y 无实义，故不画轴
seen = {}
for x, lap in cases:
    k = round(math.log10(x), 2)
    n = seen.get(k, 0); seen[k] = n + 1
    y = (0 if n == 0 else (0.15 if n % 2 else -0.15) * ((n + 1) // 2))
    axA.scatter(x, y, s=70, color=C_LAP if lap else C_OPR, zorder=4,
                edgecolor=SURFACE, linewidth=1.5)
axA.set_xscale("log")
axA.set_xlim(XMIN, XMAX)
axA.set_ylim(-0.62, 0.62)
axA.set_yticks([])
axA.spines["left"].set_visible(False)
axA.set_xticks([3, 7, 28, 90, 365, 1825, 4380])
axA.set_xticklabels(["3 d", "1 wk", "28 d", "3 mo", "1 y", "5 y", "12 y"])
axA.grid(axis="x", color=GRID, lw=0.8, zorder=1)
axA.set_xlabel("Age at index operation (log scale)", fontsize=9.2, color=INK2, labelpad=7)
# 空白区的两端取【实际观测到的】最大新生儿日龄与最小大龄日龄，不用分层边界写死
GAP_LO, GAP_HI = max(NEO), min(OLD)
axA.annotate("", xy=(GAP_LO, 0.40), xytext=(GAP_HI, 0.40),
             arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.0))
axA.text(math.sqrt(GAP_LO * GAP_HI), 0.45, "no case in this range",
         ha="center", va="bottom", fontsize=8.6, color=MUTED, style="italic")
axA.text(7.5, -0.52, "%d neonates" % len(NEO), ha="center",
         fontsize=9.0, color=INK, fontweight="bold")
axA.text(2700, -0.52, "%d children aged %.1f–%.1f y"
         % (len(OLD), GAP_HI / 365.25, max(OLD) / 365.25),
         ha="center", fontsize=9.0, color=INK, fontweight="bold")
# Ped Surg Int：图内不得含标题/图注（Artwork Guidelines），分图仅以小写字母标识。
# 原标题文字「Every case of persistent duodenal obstruction (n=12)」已在正文图注中。
axA.set_title("a", fontsize=11.0, color=INK, fontweight="bold", loc="left", pad=10)

# ---------------- Panel B：分层率 ----------------
LABEL = ["Neonate\n(<28 days)", "28 days –\n1 year", "≥1 year"]
H, OFF = 0.30, 0.17
rows = []
for (nm, lo, hi) in AGE_BANDS:
    sl = [p for p in malrot if is_lap(p) and AGED.get(p) is not None and lo <= AGED[p] < hi]
    so = [p for p in malrot if not is_lap(p) and AGED.get(p) is not None and lo <= AGED[p] < hi]
    f = lambda ps: sum(1 for p in ps if p in R and A[p]["cause"] == "十二指肠持续梗阻")
    rows.append((f(sl), len(sl), f(so), len(so)))
for i, (a, na, c, nc) in enumerate(rows):
    ra, rc = a / na * 100, c / nc * 100
    axB.barh(i - OFF, ra, height=H, color=C_LAP, zorder=3)
    axB.barh(i + OFF, rc, height=H, color=C_OPR, zorder=3)
    axB.text(ra + 0.18, i - OFF, "%d/%d" % (a, na), va="center", fontsize=8.4, color=INK2, zorder=5)
    axB.text(rc + 0.18, i + OFF, "%d/%d" % (c, nc), va="center", fontsize=8.4, color=INK2, zorder=5)
    # 分层 Fisher 精确 p 就地算，与 Table 4 同一口径；标在该层较长的条之后。
    # 两臂都零事件时 Fisher p 恒为 1.000 但并非有信息量的比较，标"—"而非表面上的
    # 1.000，否则与 Table 4 脚注"no p value is given"矛盾（2026-07-28 发现）。
    if a == 0 and c == 0:
        axB.text(max(ra, rc) + 1.7, i, "—", va="center", fontsize=9.0, color=MUTED, zorder=5)
    else:
        p = fisher_exact([[a, na - a], [c, nc - c]])[1]
        sig = p < 0.05
        axB.text(max(ra, rc) + 1.7, i, "p=%.3f" % p, va="center", fontsize=9.0,
                 color=INK if sig else MUTED, fontweight="bold" if sig else "normal", zorder=5)
axB.set_yticks(range(3)); axB.set_yticklabels(LABEL, fontsize=9.0, color=INK)
axB.invert_yaxis(); axB.set_ylim(2.55, -0.55)
axB.set_xlim(0, 14.5)
axB.xaxis.set_major_formatter(lambda v, _: f"{v:g}%")
axB.grid(axis="x", color=GRID, lw=0.8, zorder=0)
axB.set_xlabel("Reoperation for persistent duodenal obstruction,\nper 100 children in that age stratum",
               fontsize=9.2, color=INK2, labelpad=7)
axB.set_title("b", fontsize=11.0, color=INK, fontweight="bold", loc="left", pad=10)

fig.legend(handles=[Patch(facecolor=C_LAP, label="Laparoscopic completion"),
                    Patch(facecolor=C_OPR, label="Open-related")],
           loc="upper right", bbox_to_anchor=(0.988, 0.995), ncol=2, frameon=False,
           fontsize=9.2, labelcolor=INK, handlelength=1.4, handleheight=0.95,
           columnspacing=2.0, handletextpad=0.6)
# ≥1 岁层的腹腔镜占比也就地算（脚注要用）
_o_lo = AGE_BANDS[2][1]
_o_all = [p for p in malrot if AGED.get(p) is not None and AGED[p] >= _o_lo]
PCT_LAP_OLD = sum(1 for p in _o_all if is_lap(p)) / len(_o_all) * 100

# Ped Surg Int：图内不得含图注。原底部两行说明（阳性结果限于新生儿层、
# 无开腹相关病例故 OR 不可估、≥1 岁层 85% 走腹腔镜故信息量有限）的内容
# 均已见于正文 Figure 2 图注与 §3.1／Table 3 脚注，故删除不丢信息；
# 下方留白相应收窄（原 bottom=0.255 是为这两行预留的）。

fig.subplots_adjust(left=0.055, right=0.985, top=0.845, bottom=0.165)
fig.savefig("Figure2_duodenal_by_age.png", dpi=600, facecolor=SURFACE)
fig.savefig("Figure2_duodenal_by_age.pdf", facecolor=SURFACE)
# ps.fonttype=42 让 TrueType 字体嵌入 EPS，满足官方「Vector graphics containing
# fonts must have the fonts embedded」。必须放在 PDF 保存【之后】：本机 matplotlib
# 在该参数生效时写 PDF 会抛 ValueError: bytes must be in range(0, 256)
# （字体子集化的共用代码路径所致），只影响 PDF，不影响 EPS 本身。
matplotlib.rcParams["ps.fonttype"] = 42
fig.savefig("Figure2_duodenal_by_age.eps", facecolor=SURFACE)   # 矢量投稿版
print("saved Figure2_duodenal_by_age.png / .pdf")
for (nm, _, _), (a, na, c, nc) in zip(AGE_BANDS, rows):
    print("  %-20s lap %d/%-4d = %4.1f%%   open-related %d/%-4d = %4.1f%%"
          % (nm, a, na, a / na * 100, c, nc, c / nc * 100))
