# -*- coding: utf-8 -*-
"""Table 1 基线特征表：腹腔镜完成 vs 开腹相关（呼应竞争风险主分析的暴露分组）。
组间检验手写实现（本机无 scipy）：分类→Fisher 精确；年龄→Mann–Whitney U 正态近似。
输出 Table_baseline.md（可直接贴稿）+ 控制台。"""
import io, math
import numpy as np
from collections import defaultdict
from _dataprep import load, approach, has_necrosis

def fisher_2x2(a, b, c, d):
    """双侧 Fisher 精确检验 p。表 [[a,b],[c,d]]。"""
    from math import comb
    r1, r2, c1, n = a + b, c + d, a + c, a + b + c + d
    def p_tab(x):  # x = a 格
        return comb(c1, x) * comb(n - c1, r1 - x) / comb(n, r1)
    p_obs = p_tab(a)
    lo, hi = max(0, r1 - (n - c1)), min(r1, c1)
    return sum(p_tab(x) for x in range(lo, hi + 1) if p_tab(x) <= p_obs * (1 + 1e-9))

def mannwhitney(x, y):
    """Mann–Whitney U 双侧 p（正态近似 + tie 校正）。"""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n1, n2 = len(x), len(y)
    allv = np.concatenate([x, y])
    order = allv.argsort()
    ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
    # tie 平均秩
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.zeros(len(cnt)); np.add.at(sums, inv, ranks); avg = sums / cnt
    ranks = avg[inv]
    R1 = ranks[:n1].sum()
    U1 = R1 - n1 * (n1 + 1) / 2; U = min(U1, n1 * n2 - U1)
    mu = n1 * n2 / 2
    tie = np.sum(cnt ** 3 - cnt)
    sigma = math.sqrt(n1 * n2 / 12 * ((n1 + n2 + 1) - tie / ((n1 + n2) * (n1 + n2 - 1))))
    if sigma == 0: return 1.0
    z = (abs(U - mu) - 0.5) / sigma
    return 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))

def med_iqr(v):
    v = [x for x in v if x is not None]
    return np.median(v), np.percentile(v, 25), np.percentile(v, 75)

D = load()
malrot, first = D["malrot"], D["first"]
LAP  = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
OPEN = [p for p in malrot if approach(first[p]) != "腹腔镜完成"]  # 中转+开腹=开腹相关
ALL  = malrot

def sex_male(ps): return sum(1 for p in ps if str(D["sex"].get(p, "")).startswith("男"))
def neo_n(ps):    return sum(1 for p in ps if p in D["neo"])
def nec_n(ps):    return sum(1 for p in ps if has_necrosis(first[p]))
def ages(ps):     return [D["age"].get(p) * 12 for p in ps if D["age"].get(p) is not None]  # 换算为月

def pct(x, n): return f"{x} ({x/n*100:.1f}%)"

rows = []
# 男性
a, b = sex_male(LAP), len(LAP) - sex_male(LAP)
c, d = sex_male(OPEN), len(OPEN) - sex_male(OPEN)
rows.append(("Male sex, n (%)", pct(sex_male(ALL), len(ALL)), pct(sex_male(LAP), len(LAP)),
             pct(sex_male(OPEN), len(OPEN)), fisher_2x2(a, b, c, d)))
# 年龄
mA = med_iqr(ages(ALL)); mL = med_iqr(ages(LAP)); mO = med_iqr(ages(OPEN))
rows.append(("Age at index operation, months, median (IQR)",
             f"{mA[0]:.1f} ({mA[1]:.1f}–{mA[2]:.1f})",
             f"{mL[0]:.1f} ({mL[1]:.1f}–{mL[2]:.1f})",
             f"{mO[0]:.1f} ({mO[1]:.1f}–{mO[2]:.1f})",
             mannwhitney(ages(LAP), ages(OPEN))))
# 新生儿
a, b = neo_n(LAP), len(LAP) - neo_n(LAP); c, d = neo_n(OPEN), len(OPEN) - neo_n(OPEN)
rows.append(("Neonate (Apgar-proxied), n (%)", pct(neo_n(ALL), len(ALL)), pct(neo_n(LAP), len(LAP)),
             pct(neo_n(OPEN), len(OPEN)), fisher_2x2(a, b, c, d)))
# 首次坏死（术中严重度代理）
a, b = nec_n(LAP), len(LAP) - nec_n(LAP); c, d = nec_n(OPEN), len(OPEN) - nec_n(OPEN)
rows.append(("Bowel necrosis at index op, n (%)", pct(nec_n(ALL), len(ALL)), pct(nec_n(LAP), len(LAP)),
             pct(nec_n(OPEN), len(OPEN)), fisher_2x2(a, b, c, d)))

def pfmt(p): return "<0.001" if p < 0.001 else f"{p:.3f}"

L = []
L.append("**Table 1.** Baseline characteristics by index surgical approach")
L.append("")
L.append(f"| Characteristic | Overall (n={len(ALL)}) | Laparoscopic completion (n={len(LAP)}) | Open-related (n={len(OPEN)}) | p\\* |")
L.append("|---|---|---|---|---|")
for name, o, l, op, p in rows:
    L.append(f"| {name} | {o} | {l} | {op} | {pfmt(p)} |")
L.append("")
L.append("\\* Laparoscopic completion vs. open-related (open + conversion). "
         "Fisher exact test for categorical variables; Mann–Whitney U test for age. "
         "“Open-related” = open + conversion-to-open. Necrosis shown as a marker of index-operation "
         "severity (a competing-risk driver), not a baseline demographic.")
L.append("")
L.append("> TODO（人工核对后补行）: associated congenital anomalies (cardiac / GI / chromosomal); "
         "birth weight in neonates. 需人工核对诊断文本，暂留空以免关键词过抓。")

txt = "\n".join(L)
io.open("Table_baseline.md", "w", encoding="utf-8").write(txt)
# 控制台安全打印
try: print(txt)
except UnicodeEncodeError: print(txt.encode("gbk", "replace").decode("gbk"))
