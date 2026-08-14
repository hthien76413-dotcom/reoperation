# -*- coding: utf-8 -*-
"""核心结论（十二指肠持续梗阻 OR 10.98）对【年龄校正方式】的稳健性。

起因：review_checks.py 第 8 节用 log(年龄+0.1) 校正后 OR 掉到 3.96、p=0.077。
但病案首页“年龄”单位是【年】，中位 0.03 年≈11 天，而 +0.1 的偏移 = 36 天，
比中位数还大——会把新生儿之间的差异压平。必须换多种参数化验证结论是否稳健，
否则不能把“校正后不显著”当成事实报出去。

输出 age_sensitivity_out.txt
"""
import io, math
import numpy as np
from scipy import stats
from _dataprep import load, approach, reop_set, adjudicated, has_necrosis

L = []
def log(*a): L.append(" ".join(str(x) for x in a))

D = load(); A = adjudicated(); R = reop_set()
malrot, first = D["malrot"], D["first"]
age_y = np.array([D["age"].get(p) if D["age"].get(p) is not None else np.nan for p in malrot])
age_d = age_y * 365.25                                   # 换成天
lap = np.array([1.0 if approach(first[p]) == "腹腔镜完成" else 0.0 for p in malrot])
nec = np.array([1.0 if has_necrosis(first[p]) else 0.0 for p in malrot])
neo = np.array([1.0 if p in D["neo"] else 0.0 for p in malrot])
duo = np.array([1.0 if (p in R and A[p]["cause"] == "十二指肠持续梗阻") else 0.0 for p in malrot])
reop = np.array([1.0 if p in R else 0.0 for p in malrot])

log("=" * 78)
log("零、年龄本身与结局的关系（先看清楚要校正的是什么）")
log("=" * 78)
log("  年龄单位=年；全队列中位 %.3f 年 = %.0f 天；四分位 %.0f–%.0f 天"
    % (np.median(age_y), np.median(age_d), np.percentile(age_d, 25), np.percentile(age_d, 75)))
for nm, m in [("腹腔镜完成", lap == 1), ("开腹相关", lap == 0)]:
    log("  %-10s n=%3d 中位年龄 %5.0f 天（IQR %.0f–%.0f）"
        % (nm, m.sum(), np.median(age_d[m]), np.percentile(age_d[m], 25), np.percentile(age_d[m], 75)))
log("")
bands = [("<28 天", age_d < 28), ("28 天–1 岁", (age_d >= 28) & (age_d < 365)), ("≥1 岁", age_d >= 365)]
log("  %-12s %8s %8s %10s | %8s %8s %10s" % ("年龄段", "腹腔镜n", "十二梗阻", "率",
                                              "开腹n", "十二梗阻", "率"))
for nm, m in bands:
    a1 = int(((lap == 1) & m & (duo == 1)).sum()); n1 = int(((lap == 1) & m).sum())
    a0 = int(((lap == 0) & m & (duo == 1)).sum()); n0 = int(((lap == 0) & m).sum())
    log("  %-12s %8d %8d %9.1f%% | %8d %8d %9.1f%%"
        % (nm, n1, a1, a1 / max(n1, 1) * 100, n0, a0, a0 / max(n0, 1) * 100))
log("")
log("  十二指肠梗阻 14 例的年龄（天）：%s"
    % sorted(int(x) for x in age_d[duo == 1]))


# ---------------- Firth ----------------
def firth_fit(X, y, fixed=None, max_iter=500, tol=1e-10):
    n, p = X.shape; beta = np.zeros(p)
    free = [j for j in range(p) if fixed is None or j != fixed[0]]
    if fixed is not None: beta[fixed[0]] = fixed[1]
    for _ in range(max_iter):
        eta = X @ beta; pr = 1 / (1 + np.exp(-eta)); W = pr * (1 - pr)
        XtWX = X.T @ (X * W[:, None]); Ainv = np.linalg.pinv(XtWX)
        h = np.sum((X @ Ainv) * X, axis=1) * W
        U = X.T @ (y - pr + h * (0.5 - pr))
        step = np.linalg.pinv(XtWX[np.ix_(free, free)]) @ U[free]
        beta[free] += step
        if np.max(np.abs(step)) < tol: break
    return beta

def firth_pll(X, y, beta):
    eta = X @ beta; pr = np.clip(1 / (1 + np.exp(-eta)), 1e-12, 1 - 1e-12)
    ll = np.sum(y * np.log(pr) + (1 - y) * np.log(1 - pr))
    W = pr * (1 - pr); _, ld = np.linalg.slogdet(X.T @ (X * W[:, None]))
    return ll + 0.5 * ld

def firth(y, covs, names, label):
    X = np.column_stack([np.ones(len(y)), lap] + covs)
    b = firth_fit(X, y)
    eta = X @ b; pr = 1 / (1 + np.exp(-eta)); W = pr * (1 - pr)
    se = np.sqrt(np.diag(np.linalg.pinv(X.T @ (X * W[:, None]))))
    b0 = firth_fit(X, y, fixed=(1, 0.0))
    p = stats.chi2.sf(max(2 * (firth_pll(X, y, b) - firth_pll(X, y, b0)), 0), 1)
    log("  %-38s OR=%6.2f  95%%CI %5.2f–%-7.2f LRT p=%.4f"
        % (label, math.exp(b[1]), math.exp(b[1] - 1.96 * se[1]), math.exp(b[1] + 1.96 * se[1]), p))
    return math.exp(b[1]), p

log("")
log("=" * 78)
log("一、结局 = 十二指肠持续梗阻（核心结论），换多种年龄参数化")
log("=" * 78)
l1 = np.log(age_d + 1); l1 = (l1 - l1.mean()) / l1.std()
l7 = np.log(age_d + 7); l7 = (l7 - l7.mean()) / l7.std()
ly = np.log(age_y + 0.1); ly = (ly - ly.mean()) / ly.std()
gt28 = (age_d >= 28).astype(float)
gt365 = (age_d >= 365).astype(float)
firth(duo, [], [], "① 仅 lap（＝现稿的粗 OR）")
firth(duo, [neo], ["neo"], "② + 新生儿(Apgar 代理)")
firth(duo, [nec], ["nec"], "③ + 首台坏死")
firth(duo, [neo, nec], ["neo", "nec"], "④ + 新生儿 + 坏死（现稿总体模型的协变量）")
firth(duo, [ly, nec], ["log(年+0.1)", "nec"], "⑤ + log(年龄年+0.1) + 坏死〔前次所用〕")
firth(duo, [l1, nec], ["log(天+1)", "nec"], "⑥ + log(年龄天+1) + 坏死")
firth(duo, [l7, nec], ["log(天+7)", "nec"], "⑦ + log(年龄天+7) + 坏死")
firth(duo, [gt28, nec], [">28d", "nec"], "⑧ + 年龄≥28天(二分) + 坏死")
firth(duo, [gt28, gt365, nec], [">28d", ">1y", "nec"], "⑨ + 年龄三分段 + 坏死")

log("")
log("=" * 78)
log("二、同样的年龄参数化用在【总体再手术率】上（现稿的阴性结论）")
log("=" * 78)
firth(reop, [], [], "① 仅 lap")
firth(reop, [neo, nec], ["neo", "nec"], "④ + 新生儿 + 坏死〔现稿 Table 4〕")
firth(reop, [l1, nec], ["log(天+1)", "nec"], "⑥ + log(年龄天+1) + 坏死")
firth(reop, [gt28, gt365, nec], [">28d", ">1y", "nec"], "⑨ + 年龄三分段 + 坏死")

log("")
log("=" * 78)
log("三、按年龄分层的 Mantel–Haenszel（不依赖模型设定）")
log("=" * 78)
num = den = 0.0
for nm, m in bands:
    a1 = int(((lap == 1) & m & (duo == 1)).sum()); b1 = int(((lap == 1) & m).sum()) - a1
    a0 = int(((lap == 0) & m & (duo == 1)).sum()); b0 = int(((lap == 0) & m).sum()) - a0
    n = a1 + b1 + a0 + b0
    if n == 0: continue
    orr = (a1 * b0) / (b1 * a0) if b1 and a0 else float("inf") if a1 else float("nan")
    log("  %-12s 腹腔镜 %d/%d  开腹相关 %d/%d   层内 OR=%s"
        % (nm, a1, a1 + b1, a0, a0 + b0, ("%.2f" % orr) if np.isfinite(orr) else "∞/不可估"))
    num += a1 * b0 / n; den += b1 * a0 / n
log("  Mantel–Haenszel 合并 OR = %.2f" % (num / den) if den else "  MH 不可估")

out = "\n".join(L)
io.open("age_sensitivity_out.txt", "w", encoding="utf-8").write(out)
print("saved age_sensitivity_out.txt")
