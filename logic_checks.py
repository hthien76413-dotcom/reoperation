# -*- coding: utf-8 -*-
"""逻辑审查用的核算：只验证讨论部分那些"结果里没报过"的数字，以及几处强断言能否被数据支持。
不生成新结论，只核实原稿数字。"""
import io, sys, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import _dataprep as D
from scipy.stats import fisher_exact, norm

d = D.load()
coh = set(d["malrot"])
appr = {p: D.approach(d["first"][p]) for p in coh}
lap = {p for p in coh if appr[p] == "腹腔镜完成"}
opr = {p for p in coh if appr[p] != "腹腔镜完成"}
neo = {p for p in coh if p in d["neonate"]}
# 【2026-08-14 修正】原为 (death | abandon)，即把「自动出院」一概当作竞争事件。
# 该口径已被主分析废弃（stratified_analysis.py §竞争风险）：电话随访后，竞争事件
# 仅限【确认死亡】（院内死亡 + 随访确认死亡），自动出院但确认存活者须留在风险集内。
# 且须限于 42 天窗口内，与主结局窗口一致。
H_WIN = 42
def _within_window(p):
    t0 = d["first"][p]["d"]
    dd = (d["last_dis"][p] - t0).days if (t0 and d["last_dis"].get(p)) else None
    return dd is not None and 0 <= dd <= H_WIN
# 已再手术者计为【结局】而非竞争事件（即便其后死亡），与主分析的事件编码一致。
_reop = D.reop_in_cohort()
comp = {p for p in coh if p in d["died"] and p not in _reop and _within_window(p)}
nec = {p for p in coh if D.has_necrosis(d["first"][p])}

print("=== 1. 新生儿层：讨论里的四个数 ===")
for nm, s in (("lap", lap & neo), ("open-related", opr & neo)):
    n = len(s)
    print(f"  {nm:14s} n={n:4d}  坏死 {len(s & nec):3d} ({len(s & nec)/n*100:.1f}%)"
          f"  竞争事件 {len(s & comp):3d} ({len(s & comp)/n*100:.1f}%)")

print("\n=== 2. 粘连机制型十二指肠梗阻的率（§3.7 与讨论）===")
# 【2026-09-11 修正】原先写死 10 例腹腔镜 / 1 例开腹相关，那是第四轮资格裁定
# 【之前】的计数。该轮排除了 2 例机制核阅对象（开腹 1 例、腹腔镜 1 例，均为
# C=粘连），现队列只剩 12 例十二指肠梗阻：A=技术缺陷 3 例、C=粘连 9 例，全为
# 腹腔镜完成。改为直接从机制核阅答案键现算，避免再次与稿件脱节。
import openpyxl as _oxl
_wk = _oxl.load_workbook("机制核阅_盲法_答案键.xlsx", data_only=True)["答案键_评分前勿开"]
_mech = {}
for _r in range(2, _wk.max_row + 1):
    _sid = _wk.cell(_r, 2).value
    if _sid is None:
        continue
    _mech[str(_sid).strip()] = str(_wk.cell(_r, 4).value).strip().upper()
_adh = {p for p, m in _mech.items() if m == "C" and p in coh}
_tec = {p for p, m in _mech.items() if m == "A" and p in coh}
print(f"  粘连型 lap {len(_adh & lap)}/{len(lap)} = {len(_adh & lap)/len(lap)*100:.2f}%"
      f"   open-related {len(_adh & opr)}/{len(opr)} = {len(_adh & opr)/len(opr)*100:.2f}%")
print(f"  技术缺陷型 lap {len(_tec & lap)}   open-related {len(_tec & opr)}"
      f"   （机制核阅共 {len(_mech)} 例，其中 {len(_mech) - len(_adh) - len(_tec)} 例已被第四轮裁定排除出队列）")

# 【2026-08-14 修正】原第 3、5 节用的是第四轮资格裁定【之前】的硬编码数字
# （7/76、1/18、合计 94 例）。该轮裁定排除了 18 例非初次 Ladd，其中 3 例是
# >1 岁的再手术，故 ≥1 岁层现为 71+13=84 例、6 例第 1 类结局。以下改为现算。
big = {p for p in coh if d["age_d"].get(p) is not None and d["age_d"][p] >= 365.25}
adj_all = D.adjudicated()
duo = {p for p in coh if p in adj_all and adj_all[p]["cause"] == "十二指肠持续梗阻"}

print("\n=== 3. ≥1 岁层的效能（按现队列现算）===")
n1, n2 = len(big & lap), len(big & opr)
x1, x2 = len(big & lap & duo), len(big & opr & duo)
p1, p2 = x1 / n1, (x2 / n2 if n2 else 0.0)
pbar = (x1 + x2) / (n1 + n2)
se0 = math.sqrt(pbar*(1-pbar)*(1/n1 + 1/n2))
se1 = math.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
z = norm.ppf(0.975)
if se1 > 0:
    pw = norm.cdf((abs(p1-p2) - z*se0)/se1) + norm.cdf((-abs(p1-p2) - z*se0)/se1)
    pwtxt = f"{pw*100:.1f}%"
else:
    pwtxt = "不可估（观察到的开腹相关组为零事件，正态近似退化）"
print(f"  ≥1 岁：腹腔镜 {x1}/{n1} ({p1*100:.1f}%)  开腹相关 {x2}/{n2} ({p2*100:.1f}%)")
print(f"  正态近似双侧效能 ≈ {pwtxt}")

print("\n=== 4. 竞争风险无法解释 —— 能否量化 ===")
# 最坏情形：把开腹相关新生儿中发生竞争事件者全部当作"本会发生十二指肠梗阻"
k = len(opr & neo & comp)
n_lap, x_lap = len(lap & neo), 6
n_opr = len(opr & neo)
print(f"  开腹相关新生儿竞争事件 {k}/{n_opr}")
for add in (0, 1, 2, 3, k):
    tbl = [[x_lap, n_lap - x_lap], [add, n_opr - add]]
    print(f"   假设其中 {add:2d} 例本会发生 → {x_lap}/{n_lap} vs {add}/{n_opr}, "
          f"Fisher p={fisher_exact(tbl)[1]:.4f}")

print("\n=== 5. ≥1 岁层 8.5% 的构成：是否只含第1类（现算）===")
print(f"  ≥1 岁合计 {len(big)} 例（腹腔镜 {len(big & lap)} / 开腹相关 {len(big & opr)}）")
print(f"  第1类（十二指肠持续梗阻）腹腔镜 {len(big & lap & duo)}/{len(big & lap)}"
      f" = {len(big & lap & duo)/len(big & lap)*100:.2f}%  ← 稿件 Table 4 应为 6/71 (8.5%)")
allreop_big = {p for p in big if p in adj_all}
print(f"  该层全部再手术 {len(allreop_big & lap)}/{len(big & lap)} 腹腔镜、"
      f"{len(allreop_big & opr)}/{len(big & opr)} 开腹相关；"
      f"其中第1类占 {len(big & duo)}/{len(allreop_big)}")
