import math
import os, sys
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _dataprep import load, approach, reop_set

D = load()
R = reop_set()
malrot, first = D["malrot"], D["first"]
R = {p for p in R if p in set(malrot)}

LAP = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
OPR = [p for p in malrot if approach(first[p]) != "腹腔镜完成"]

a = sum(1 for p in LAP if p in R)
b = len(LAP) - a
c = sum(1 for p in OPR if p in R)
d = len(OPR) - c

p_fisher = stats.fisher_exact([[a, b], [c, d]])[1]
or_crude = (a * d) / (b * c)


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


ci_lo, ci_hi = exact_or_ci(a, b, c, d)

print("a =", a, " b =", b, " c =", c, " d =", d)
print("OR (crude) = %.4f" % or_crude)
print("95%% CI (exact, Cornfield) = %.4f – %.4f" % (ci_lo, ci_hi))
print("Fisher exact p = %.6f" % p_fisher)

from scipy.stats.contingency import odds_ratio
r = odds_ratio([[a, b], [c, d]], kind="conditional")
lo2, hi2 = r.confidence_interval(0.95)
print()
print("交叉核对 scipy.stats.contingency.odds_ratio (conditional):")
print("OR =", r.statistic, " 95% CI =", lo2, "-", hi2)
