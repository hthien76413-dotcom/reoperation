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
comp = (d["death"] | d["abandon"]) & coh
nec = {p for p in coh if D.has_necrosis(d["first"][p])}

print("=== 1. 新生儿层：讨论里的四个数 ===")
for nm, s in (("lap", lap & neo), ("open-related", opr & neo)):
    n = len(s)
    print(f"  {nm:14s} n={n:4d}  坏死 {len(s & nec):3d} ({len(s & nec)/n*100:.1f}%)"
          f"  竞争事件 {len(s & comp):3d} ({len(s & comp)/n*100:.1f}%)")

print("\n=== 2. 粘连机制型十二指肠梗阻的率（讨论 3.9% vs 0.5%）===")
# 机制来自裁定，直接用已核定的计数：粘连 11 例中 10 例腹腔镜、1 例开腹相关
print(f"  lap 10/{len(lap)} = {10/len(lap)*100:.2f}%   open-related 1/{len(opr)} = {1/len(opr)*100:.2f}%")

print("\n=== 3. ≥1 岁层的效能（讨论 about 5% power）===")
# 双侧 Fisher 不易解析求解，用正态近似的两比例检验效能，p1=0.092 p2=0.056, n1=76 n2=18
p1, p2, n1, n2 = 7/76, 1/18, 76, 18
pbar = (7 + 1) / (n1 + n2)
se0 = math.sqrt(pbar*(1-pbar)*(1/n1 + 1/n2))
se1 = math.sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
z = norm.ppf(0.975)
pw = norm.cdf((abs(p1-p2) - z*se0)/se1) + norm.cdf((-abs(p1-p2) - z*se0)/se1)
print(f"  正态近似双侧效能 ≈ {pw*100:.1f}%（检出 9.2% vs 5.6% 之差）")

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

print("\n=== 5. ≥1 岁层 8.5% 的构成：是否只含第1类 ===")
print("  （第1类：≥1岁 7/76 + 1/18 = 8/94 =", f"{8/94*100:.2f}%）")
