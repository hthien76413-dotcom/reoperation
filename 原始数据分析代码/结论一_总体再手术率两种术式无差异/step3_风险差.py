import math
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _dataprep import load, approach, reop_set

D = load()
R = reop_set()
malrot, first = D["malrot"], D["first"]
R = {p for p in R if p in set(malrot)}

LAP = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
OPR = [p for p in malrot if approach(first[p]) != "腹腔镜完成"]

k1, n1 = sum(1 for p in LAP if p in R), len(LAP)
k2, n2 = sum(1 for p in OPR if p in R), len(OPR)

p1, p2 = k1 / n1, k2 / n2
rd = p1 - p2


def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def newcombe(k1, n1, k2, n2, z=1.96):
    l1, u1 = wilson(k1, n1, z)
    l2, u2 = wilson(k2, n2, z)
    p1, p2 = k1 / n1, k2 / n2
    lo = (p1 - p2) - z * math.sqrt(l1 * (1 - l1) / n1 + u2 * (1 - u2) / n2)
    hi = (p1 - p2) + z * math.sqrt(u1 * (1 - u1) / n1 + l2 * (1 - l2) / n2)
    return lo, hi


lo, hi = newcombe(k1, n1, k2, n2)

print("腹腔镜完成: %d/%d = %.4f" % (k1, n1, p1))
print("开腹相关:   %d/%d = %.4f" % (k2, n2, p2))
print("风险差 (RD) = %.4f (即 %+.2f 个百分点)" % (rd, rd * 100))
print("95%% CI (Newcombe) = %.4f 到 %.4f (即 %+.2f 到 %+.2f 个百分点)"
      % (lo, hi, lo * 100, hi * 100))
