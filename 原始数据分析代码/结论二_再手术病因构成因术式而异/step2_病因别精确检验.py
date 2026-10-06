import math
import os, sys
import numpy as np
from scipy import stats
_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(_d, "_dataprep.py")):
    _p = os.path.dirname(_d)
    if _p == _d:
        raise SystemExit("找不到 _dataprep.py，请确认本脚本仍在原仓库目录树下（任意层子文件夹均可）")
    _d = _p
sys.path.insert(0, _d)
from _dataprep import load, approach, reop_set, adjudicated, CAUSES6

D = load()
R = reop_set()
A = adjudicated()
malrot, first = D["malrot"], D["first"]
R = {p for p in R if p in set(malrot)}

LAP = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
OPR = [p for p in malrot if approach(first[p]) != "腹腔镜完成"]
nL, nO = len(LAP), len(OPR)

EN = {"十二指肠持续梗阻": "1. Persistent duodenal obstruction",
      "肠坏死/穿孔/吻合口并发症": "2. Necrosis / perforation / anastomotic complication",
      "粘连性肠梗阻": "3. Adhesive obstruction (non-duodenal)",
      "合并畸形漏诊": "4. Missed associated anomaly",
      "肠扭转复发": "5. Recurrent volvulus / redo-Ladd",
      "其他": "6. Other"}


def _lc(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def exact_or_ci(a, b, c, d, alpha=0.05):
    n1, n2, m1 = a + b, c + d, a + c
    def tail(psi, upper):
        lo, hi = max(0, m1 - n2), min(n1, m1)
        ks = np.arange(lo, hi + 1)
        lw = np.array([_lc(n1, k) + _lc(n2, m1 - k) for k in ks]) + ks * math.log(psi)
        w = np.exp(lw - lw.max()); w /= w.sum()
        return w[ks >= a].sum() if upper else w[ks <= a].sum()
    def solve(t, upper):
        if upper and a == max(0, m1 - n2): return 0.0
        if (not upper) and a == min(n1, m1): return float("inf")
        f = lambda lp: tail(math.exp(lp), upper) - t
        loP, hiP = -30.0, 30.0
        for _ in range(300):
            mid = (loP + hiP) / 2
            if (f(mid) > 0) == (f(loP) > 0): loP = mid
            else: hiP = mid
        return math.exp((loP + hiP) / 2)
    return solve(alpha / 2, True), solve(alpha / 2, False)


results = []
for zh in CAUSES6:
    a = sum(1 for p in LAP if p in R and A[p]["cause"] == zh)
    c = sum(1 for p in OPR if p in R and A[p]["cause"] == zh)
    b, d = nL - a, nO - c
    pv = stats.fisher_exact([[a, b], [c, d]])[1]
    lo, hi = exact_or_ci(a, b, c, d)
    if b == 0 or c == 0:
        if a and not c:
            orv_str = "NE (>=%.2f)" % lo
        elif c and not a:
            orv_str = "NE (<=%.2f)" % hi
        else:
            orv_str = "NE"
    else:
        orv = (a * d) / (b * c)
        orv_str = "%.4f (%.4f-%.4f)" % (orv, lo, hi)
    results.append((zh, a, c, pv))
    print("%-45s a=%2d c=%2d  OR = %-22s Fisher p = %.6f" % (EN[zh], a, c, orv_str, pv))

print()
print("六个病因的原始 p 值（未校正）:")
for zh, a, c, pv in results:
    print("  %-45s p = %.6f" % (EN[zh], pv))
