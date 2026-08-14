# -*- coding: utf-8 -*-
"""Supplementary Figure S1（英文版）：竞争风险校正下的再手术累积发生率。
（2026-07-26 原为正文 Figure 2；总体率无差异，该图承担的是方法学稳健性而非
  主要论点，故降为补充材料，正文主图让位给病因×入路图。）
Aalen–Johansen CIF 自实现（本机无 lifelines），bootstrap 95% 置信带。
竞争风险记录构造：H=42 天行政删失（与主结局窗口一致）；
事件1=早期梗阻再手术；事件2=死亡/放弃（竞争）；余为删失。"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime
from _dataprep import load, approach, reop_set, adjudicated

# 【2026-07-26】行政删失时限由 90 天改为 42 天，与主结局定义（42 天内的计划外再手术）
# 一致。原先三条时间轴互不相同（结局 42 天 / 竞争事件 42 天 / CIF 90 天），
# 实测最长间隔 37 天故数值不变，但定义上自相矛盾，审稿人会问。
H = 42
D = load()
ops, first, malrot = D["ops"], D["first"], D["malrot"]
# 2026-07-27：竞争事件改为【确认死亡】（院内死亡 + 电话随访确认死亡）；
# 自动出院但随访确认存活者留在风险集，失访 2 例自末次出院日删失。
died, lost, last_dis = D["died"], D["lost"], D["last_dis"]
REOP, ADJ = reop_set(), adjudicated()   # 事件与间隔一律取自盲法裁定表

def group(p):
    return "Laparoscopic" if approach(first[p]) == "腹腔镜完成" else "Open-related"

recs = []
for p in malrot:
    t0 = first[p]["d"]
    if t0 is None: continue
    ev, t = 0, H
    if p in REOP:
        dd = ADJ[p]["gap"]
        if dd is None and ADJ[p]["d_reop"] and ADJ[p]["d_index"]:
            dd = (ADJ[p]["d_reop"] - ADJ[p]["d_index"]).days
        if dd is not None and 0 < dd <= H: ev, t = 1, dd
    elif p in lost:
        dd = (last_dis[p] - t0).days if last_dis[p] else None
        if dd is not None and 0 <= dd <= H: ev, t = 0, dd
    elif p in died:
        # 当日死亡（gap=0）必须计入，否则 7 例被误作活满 42 天无事件
        dd = (last_dis[p] - t0).days if last_dis[p] else None
        if dd is not None and 0 <= dd <= H: ev, t = 2, dd
    recs.append((group(p), max(float(t), 0.5), ev))

rng = np.random.default_rng(7)
G = {g: [] for g in ["Laparoscopic", "Open-related"]}
for g, t, ev in recs:
    G[g].append((t + rng.uniform(-0.05, 0.05), ev))

def aj_cif(data, grid):
    """Aalen–Johansen CIF for event of interest = 1, evaluated on grid.
    data: list of (time, event) with event in {0 censor,1 interest,2 competing}."""
    times = np.array([t for t, _ in data]); evs = np.array([e for _, e in data])
    order = times.argsort(); times, evs = times[order], evs[order]
    uniq = np.unique(times[evs > 0])
    S_prev, cif = 1.0, 0.0
    curve = []  # (t, cif)
    n = len(times)
    for ut in uniq:
        at_risk = np.sum(times >= ut - 1e-9)
        d1 = np.sum((np.abs(times - ut) < 1e-9) & (evs == 1))
        d_all = np.sum((np.abs(times - ut) < 1e-9) & (evs > 0))
        if at_risk > 0:
            cif += S_prev * (d1 / at_risk)
            S_prev *= (1 - d_all / at_risk)
        curve.append((ut, cif))
    # 阶梯投影到 grid
    out = np.zeros_like(grid, dtype=float)
    ct = np.array([c[0] for c in curve]); cv = np.array([c[1] for c in curve])
    for i, g in enumerate(grid):
        out[i] = cv[ct <= g][-1] if np.any(ct <= g) else 0.0
    return out

grid = np.arange(0, H + 1, 1.0)
B = 1000
# 配色与 Figure 2 一致：同一组在全文任何一张图里都是同一个颜色
# （蓝=腹腔镜完成，橙=开腹相关；原先本图是红/蓝，与 Figure 2 冲突）
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
colors = {"Laparoscopic": "#2a78d6", "Open-related": "#eb6834"}
plt.rcParams.update({"font.family": "sans-serif",
                     "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"]})

fig, ax = plt.subplots(figsize=(6.4, 4.2))
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
LABEL = {"Laparoscopic": "Laparoscopic completion", "Open-related": "Open-related"}
top = 0.0                                   # 记录置信带上界，避免自动 ylim 把带截断
for g in ["Laparoscopic", "Open-related"]:
    data = G[g]; n = len(data)
    point = aj_cif(data, grid) * 100        # 全文一律用百分数，与 Table 4 的 42 天 CIF 对齐
    boot = np.zeros((B, len(grid)))
    for b in range(B):
        idx = rng.integers(0, n, n)
        boot[b] = aj_cif([data[i] for i in idx], grid) * 100
    lo, hi = np.percentile(boot, 2.5, axis=0), np.percentile(boot, 97.5, axis=0)
    top = max(top, hi.max())
    ax.step(grid, point, where="post", color=colors[g], lw=2.0, zorder=3,
            label=f"{LABEL[g]} (n={n})")
    ax.fill_between(grid, lo, hi, step="post", color=colors[g], alpha=0.16,
                    linewidth=0, zorder=2)

ax.set_xlim(0, H); ax.set_ylim(0, top * 1.28)   # 上方留白给图例，置信带不被裁
ax.yaxis.set_major_formatter(lambda v, _: f"{v:g}%")
ax.set_xlabel("Days after index operation", fontsize=9.4, color=INK2, labelpad=6)
ax.set_ylabel("Cumulative incidence of unplanned reoperation (%)",
              fontsize=9.4, color=INK2, labelpad=6)
ax.set_title("Competing-risk cumulative incidence of unplanned early reoperation",
             fontsize=11.0, color=INK, fontweight="bold", loc="left", pad=26)
ax.text(0, 1.015, "Confirmed death treated as the competing event; "
                  "shaded areas are 95% bootstrap bands.",
        transform=ax.transAxes, fontsize=8.6, color=MUTED, va="bottom")
ax.legend(frameon=False, loc="upper left", fontsize=9.2, labelcolor=INK)
ax.grid(axis="y", color=GRID, lw=0.8, zorder=0); ax.set_axisbelow(True)
ax.tick_params(colors=MUTED, labelsize=8.8, length=0)
ax.spines[["top", "right"]].set_visible(False)
for sp in ("left", "bottom"):
    ax.spines[sp].set_color(AXIS); ax.spines[sp].set_linewidth(0.9)
fig.tight_layout()
fig.savefig("FigureS1_CIF_reoperation_EN.png", dpi=300, facecolor=SURFACE)
fig.savefig("FigureS1_CIF_reoperation_EN.pdf", facecolor=SURFACE)  # 矢量版备投稿

# 报数：42 天 CIF 点估计
for g in ["Laparoscopic", "Open-related"]:
    v = aj_cif(G[g], grid)[-1] * 100
    print(f"{g}: 42-day reoperation CIF = {v:.1f}%  (n={len(G[g])})")
print("saved FigureS1_CIF_reoperation_EN.png / .pdf")
