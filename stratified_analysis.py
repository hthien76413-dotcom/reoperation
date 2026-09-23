# -*- coding: utf-8 -*-
"""按年龄分层的主分析（2026-07-26 大改的计算层）。

改动缘由见 审稿意见_v2_批判性复核.md 第 1、2 条：
  · 「新生儿」原用 Apgar 代理（41 例假阳性），改用真实年龄 <28 天；
  · 年龄同时预测暴露与结局，是让粗 OR 偏大的混杂，方向与全文「严重度混杂相反」
    的论证不同，必须分层而不是仅在讨论里带一句；
  · 14 例十二指肠持续梗阻年龄呈双峰（3–10 天 6 例 / 4.5–13 岁 8 例，中间空白），
    分层后新生儿层 6/142 vs 0/166（p=0.009）、儿童层 7/76 vs 1/18（p=1.00）。

产出（均为可直接贴稿的英文 markdown）：
  Table_baseline_v2.md      Table 1（年龄取值修正 + 新生儿改真实年龄 + 年龄分段行）
  Table_cause_v2.md         Table 2（病因×入路，补精确 95%CI 与 Holm 校正 p）
  Table_stratified.md       新表：十二指肠持续梗阻与总体率，按年龄分层 × 入路
  Table_sensitivity_v2.md   Table 3（Firth 惩罚 LRT 修正 + 年龄校正）
  stratified_out.txt        中文核对底稿
"""
import io, math
import numpy as np
from scipy import stats
from _dataprep import (load, approach, reop_set, adjudicated, has_necrosis,
                       CAUSES6, AGE_BANDS, age_band, all_statuses)

D = load(); A = adjudicated(); R = reop_set()
malrot, first = D["malrot"], D["first"]
# 2026-07-27：资格裁定剔除 16 例后，结局集合必须同步收缩到队列之内，
# 否则被剔除者仍计入分子（曾因此把 36 例写成 39 例，各行百分比分母全错）。
R = {p for p in R if p in set(malrot)}
AGED = D["age_d"]
LAP = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
OPR = [p for p in malrot if approach(first[p]) != "腹腔镜完成"]
nL, nO = len(LAP), len(OPR)

L = []
def log(*a): L.append(" ".join(str(x) for x in a))


# ---------------------------------------------------------------- 统计工具
def fisher_p(a, b, c, d):
    return stats.fisher_exact([[a, b], [c, d]])[1]

def _lc(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

def exact_or_ci(a, b, c, d, alpha=0.05):
    """条件精确（Cornfield）95%CI。"""
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

def orfmt(a, b, c, d):
    """OR 与精确区间的排版。
    · 点估计 ≥10 时只保留 1 位小数——这类区间常跨两个数量级，两位小数是假精确。
    · 含零格时点估计不可估，写 NE 而非 ∞：部分投稿系统会丢 ∞ 字符，
      且『OR=∞』易被误读为一个真实的巨大效应。单侧区间用 ≥/≤ 表示。"""
    lo, hi = exact_or_ci(a, b, c, d)
    if b == 0 or c == 0:
        if a and not c:
            return "NE", "≥%.2f" % lo
        if c and not a:
            return "NE", "≤%.1f" % hi
        return "NE", "—"
    orv = (a * d) / (b * c)
    pt = ("%.1f" if orv >= 10 else "%.2f") % orv
    return pt, "%.2f–%s" % (lo, "NE" if not np.isfinite(hi) else "%.1f" % hi)

def wilson(x, n, z=1.96):
    if n == 0: return 0.0, 0.0
    p = x / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h) * 100, min(1.0, c + h) * 100

def mh_or(strata):
    """Mantel–Haenszel OR 与 95%CI（Robins–Breslow–Greenland 方差）。
    只报点估计而不给区间是统计审稿的硬伤——本研究里十二指肠梗阻的 MH 区间恰好跨过 1。"""
    Rr = S = F = G = Hh = 0.0
    for a, b, c, d in strata:
        n = a + b + c + d
        if not n: continue
        Rr += a*d/n; S += b*c/n
        F += (a+d)*a*d/n**2
        G += ((a+d)*b*c + (b+c)*a*d)/n**2
        Hh += (b+c)*b*c/n**2
    # 2026-07-27：资格裁定后开腹相关组各层十二指肠事件数全为 0，S=Σbc/n 归零，
    # MH 比值与其 RBG 方差在数学上均不可估——返回 None 由调用方打印 NE，不可硬算。
    if S == 0 or Rr == 0:
        return None, None, None
    se = math.sqrt(F/(2*Rr**2) + G/(2*Rr*S) + Hh/(2*S**2))
    orv = Rr/S
    return orv, orv*math.exp(-1.96*se), orv*math.exp(1.96*se)

def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out = [0.0] * len(ps); prev = 0.0
    for rank, i in enumerate(order):
        prev = min(1.0, max(prev, (len(ps) - rank) * ps[i])); out[i] = prev
    return out


# ---------------------------------------------------------------- Firth
def firth_fit(X, y, fixed=None, max_iter=500, tol=1e-10):
    """fixed=(索引,值) 时固定该系数；惩罚项始终用完整设计矩阵的信息阵，
    故约束模型与全模型的惩罚似然可比（旧 strengthen.py 用缩小矩阵，错）。"""
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

def firth(y, covs, label):
    X = np.column_stack([np.ones(len(y)), lapv] + covs)
    b = firth_fit(X, y)
    eta = X @ b; pr = 1 / (1 + np.exp(-eta)); W = pr * (1 - pr)
    se = np.sqrt(np.diag(np.linalg.pinv(X.T @ (X * W[:, None]))))
    b0 = firth_fit(X, y, fixed=(1, 0.0))
    p = stats.chi2.sf(max(2 * (firth_pll(X, y, b) - firth_pll(X, y, b0)), 0), 1)
    return (label, math.exp(b[1]), math.exp(b[1] - 1.96 * se[1]),
            math.exp(b[1] + 1.96 * se[1]), p)

lapv = np.array([1.0 if approach(first[p]) == "腹腔镜完成" else 0.0 for p in malrot])
necv = np.array([1.0 if has_necrosis(first[p]) else 0.0 for p in malrot])
aged = np.array([AGED[p] if AGED.get(p) is not None else np.nan for p in malrot])
lagev = np.log(aged + 1); lagev = (lagev - lagev.mean()) / lagev.std()
neov = (aged < 28).astype(float)
b28 = (aged >= 28).astype(float); b365 = (aged >= 365.25).astype(float)
yall = np.array([1.0 if p in R else 0.0 for p in malrot])
yduo = np.array([1.0 if (p in R and A[p]["cause"] == "十二指肠持续梗阻") else 0.0 for p in malrot])


# ================================================================ Table 1
log("=" * 78); log("Table 1（修正版：报标准化差值 SMD，不报基线 p 值）"); log("=" * 78)
def med_iqr_m(ps):
    v = [AGED[p] / 30.44 for p in ps if AGED.get(p) is not None]
    return np.median(v), np.percentile(v, 25), np.percentile(v, 75)

def smd_bin(a, na, c, nc):
    """二分类变量的标准化差值。|SMD|>0.10 通常判为不均衡。"""
    p1, p2 = a / na, c / nc
    den = math.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / 2)
    return (p1 - p2) / den if den > 0 else 0.0

def smd_cont(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    den = math.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2)
    return (x.mean() - y.mean()) / den if den > 0 else 0.0

T1 = []
T1.append("**Table 1.** Baseline characteristics by index surgical approach.")
T1.append("")
T1.append("| Characteristic | Overall (n=%d) | Laparoscopic completion (n=%d) | Open-related (n=%d) | SMD\\* |" % (nL + nO, nL, nO))
T1.append("|---|---|---|---|---|")

def row(label, a, c, smd):
    mark = "**" if abs(smd) >= 0.10 else ""
    T1.append(("| %s | %d (%.1f) | %d (%.1f) | %d (%.1f) | %s%+.2f%s |"
               % (label, a + c, (a + c) / (nL + nO) * 100, a, a / nL * 100, c, c / nO * 100,
                  mark, smd, mark)).replace("-", "−"))   # 真正的减号

male = lambda ps: sum(1 for p in ps if str(D["sex"].get(p, "")).startswith("男"))
a, c = male(LAP), male(OPR)
row("Male sex, n (%)", a, c, smd_bin(a, nL, c, nO))

mA, mL, mO = med_iqr_m(malrot), med_iqr_m(LAP), med_iqr_m(OPR)
# 年龄极度右偏（中位 0.2 月、四分位上界 2.7 月），均值/标准差口径的 SMD 会失真，
# 故在 log(天+1) 尺度上计算并注明。
lg = lambda ps: [math.log(AGED[p] + 1) for p in ps if AGED.get(p) is not None]
T1.append("| Age at index operation, months, median (IQR) | %.1f (%.1f–%.1f) | %.1f (%.1f–%.1f) | %.1f (%.1f–%.1f) | **%+.2f**† |"
          % (mA + mL + mO + (smd_cont(lg(LAP), lg(OPR)),)))   # 该行 SMD 为正，无需替换减号
for nm, lo, hi in AGE_BANDS:
    f = lambda ps: sum(1 for p in ps if AGED.get(p) is not None and lo <= AGED[p] < hi)
    a, c = f(LAP), f(OPR)
    row("— %s, n (%%)" % nm, a, c, smd_bin(a, nL, c, nO))
nec = lambda ps: sum(1 for p in ps if has_necrosis(first[p]))
a, c = nec(LAP), nec(OPR)
row("Bowel necrosis at index operation, n (%)", a, c, smd_bin(a, nL, c, nO))
T1.append("")
T1.append("\\* Standardized mean difference (laparoscopic completion minus open-related), with values of "
          "|SMD| ≥ 0.10 shown in bold. We report SMDs rather than p values because the two groups are not "
          "samples from a common population and no null hypothesis of equal baseline distributions is of "
          "interest here; the SMD quantifies the size of the imbalance that the analysis must contend with, "
          "independently of sample size. Age was taken from the earliest admission record for each child. "
          "Necrosis is shown as a marker of index-operation severity, not a baseline demographic.")
T1.append("† Age is strongly right-skewed, so its SMD is computed on the log(days + 1) scale; the "
          "median and IQR are shown untransformed, in months.")
io.open("Table_baseline_v2.md", "w", encoding="utf-8").write("\n".join(T1))
for x in T1: log(x)


# ================================================================ Table 2
log(""); log("=" * 78); log("Table 2（补精确 CI 与 Holm）"); log("=" * 78)
cause_rows, praw = [], []
for zh in CAUSES6:
    a = sum(1 for p in LAP if p in R and A[p]["cause"] == zh)
    c = sum(1 for p in OPR if p in R and A[p]["cause"] == zh)
    pv = fisher_p(a, nL - a, c, nO - c)
    pt, ci = orfmt(a, nL - a, c, nO - c)
    cause_rows.append([zh, a + c, a, c, a / nL * 100, c / nO * 100, pt, ci, pv])
    praw.append(pv)
padj = holm(praw)
EN = {"十二指肠持续梗阻": "1. Persistent duodenal obstruction (no intrinsic lesion)",
      "肠坏死/穿孔/吻合口并发症": "2. Necrosis / perforation / anastomotic complication",
      "粘连性肠梗阻": "3. Adhesive obstruction (non-duodenal)",
      "合并畸形漏诊": "4. Missed associated anomaly†",
      "肠扭转复发": "5. Recurrent volvulus / redo-Ladd",
      "其他": "6. Other‡"}
T3 = ["**Table 2.** Cause of unplanned reoperation, overall and by index approach.", "",
      "| Cause (adjudicated, single choice) | Overall (n=%d) | Lap (n=%d) | Open-related (n=%d) | Rate, lap vs. open-related | OR (exact 95%% CI) | p\\* | Holm-adjusted p |"
      % (len(R), sum(1 for _p in LAP if _p in R), sum(1 for _p in OPR if _p in R)),
      "|---|---|---|---|---|---|---|---|"]
for r, pa in zip(cause_rows, padj):
    bold = "**" if pa < 0.05 else ""
    T3.append("| %s | %d (%.1f%%) | %d | %d | %s%.1f%% vs. %.1f%%%s | %s%s (%s)%s | %s%.4f%s | %s%.3f%s |"
              % (EN[r[0]], r[1], r[1] / len(R) * 100, r[2], r[3], bold, r[4], r[5], bold,
                 bold, r[6], r[7], bold, bold, r[8], bold, bold, pa, bold))
a = sum(1 for p in LAP if p in R and A[p]["cause"] in {"十二指肠持续梗阻", "粘连性肠梗阻", "肠扭转复发"})
c = sum(1 for p in OPR if p in R and A[p]["cause"] in {"十二指肠持续梗阻", "粘连性肠梗阻", "肠扭转复发"})
T3.append("| **Obstructive causes combined (1+3+5)** | **%d (%.1f%%)** | %d | %d | %.1f%% vs. %.1f%% | — | — | — |"
          % (a + c, (a + c) / len(R) * 100, a, c, a / len(LAP) * 100, c / len(OPR) * 100))
T3.append("")
n_duo = sum(1 for _p in R if A[_p]["cause"] == "十二指肠持续梗阻")
T3.append("\\* Fisher exact test on rates with the full cohort as the denominator (%d laparoscopic, %d open-related); "
          "odds ratios with conditional exact (Cornfield) 95%% confidence intervals. Holm's step-down correction is applied "
          "across the six cause-specific comparisons. No open-related child had a persistent duodenal obstruction, so that "
          "odds ratio is not estimable and only the one-sided lower bound is informative; the comparison rests on %d events. "
          "The cause-specific comparison for persistent duodenal obstruction is confounded by age and is presented "
          "stratified in Table 4." % (len(LAP), len(OPR), n_duo))
T3.append("† Coexisting malformation first identified or confirmed at reoperation: duodenal membrane 3, multiple jejunal atresia 1.")
T3.append("‡ Wound dehiscence 2, stress-ulcer bleeding 2, stoma prolapse 1.")
io.open("Table_cause_v2.md", "w", encoding="utf-8").write("\n".join(T3))
for x in T3: log(x)


# ================================================================ 新 Table 4：分层
log(""); log("=" * 78); log("新 Table 4：按年龄分层"); log("=" * 78)
T4 = ["**Table 4.** Persistent duodenal obstruction and overall unplanned reoperation, "
      "stratified by age at the index operation.", "",
      "| Age stratum | Outcome | Laparoscopic completion | Open-related | OR (exact 95% CI) | p\\* |",
      "|---|---|---|---|---|---|"]
mh_num = mh_den = 0.0
mh_strata = []
p_duo, p_any = [], []          # 供分层比较的多重性校正用
for nm, lo, hi in AGE_BANDS:
    sl = [p for p in LAP if AGED.get(p) is not None and lo <= AGED[p] < hi]
    so = [p for p in OPR if AGED.get(p) is not None and lo <= AGED[p] < hi]
    for tag, sel in [("Persistent duodenal obstruction",
                      lambda p: p in R and A[p]["cause"] == "十二指肠持续梗阻"),
                     ("Any unplanned reoperation", lambda p: p in R)]:
        a = sum(1 for p in sl if sel(p)); c = sum(1 for p in so if sel(p))
        b, d = len(sl) - a, len(so) - c
        pt, ci = orfmt(a, b, c, d)
        pv = fisher_p(a, b, c, d)
        (p_duo if tag.startswith("Persistent") else p_any).append(pv)
        # a=c=0（两臂都零事件）时 Fisher p 恒为 1.000，但这不是一次有信息量的比较——
        # 显示"—"而非表面上的 1.000，否则与脚注"no p value is given"自相矛盾
        # （2026-07-28 发现）。Holm 校正仍按三层计算，不受此处显示方式影响。
        pv_disp = "—" if (a == 0 and c == 0) else "%.3f" % pv
        T4.append("| %s | %s | %d/%d (%.1f%%) | %d/%d (%.1f%%) | %s (%s) | %s |"
                  % (nm if tag.startswith("Persistent") else "", tag,
                     a, len(sl), a / max(len(sl), 1) * 100,
                     c, len(so), c / max(len(so), 1) * 100, pt, ci, pv_disp))
        if tag.startswith("Persistent") and (a + b + c + d):
            n = a + b + c + d
            mh_num += a * d / n; mh_den += b * c / n
            mh_strata.append((a, b, c, d))
# 分层比较的多重性：族的定义会改变结论，两种都报，由读者取用
h_duo = holm(p_duo)[0]                 # 族 = 十二指肠梗阻的 3 个年龄层
h_all = holm(p_duo + p_any)[0]         # 族 = 2 结局 × 3 层，共 6 个
T4.append("")
T4.append("\\* Fisher exact test; conditional exact (Cornfield) 95% confidence intervals. "
          "Applying Holm's correction across the three age strata for persistent duodenal obstruction leaves the "
          "neonatal comparison significant (adjusted p=" + ("%.3f" % h_duo) + "); if all six stratum-by-outcome "
          "comparisons in this table are treated as one family, the adjusted p becomes " + ("%.3f" % h_all) +
          " and no longer falls below 0.05. We report both so that either family definition can be applied. "
          "Mantel–Haenszel odds ratio for persistent duodenal obstruction pooled across the three age strata = **"
          + (lambda t: "not estimable (no open-related event in any stratum)"
             if t[0] is None else "%.2f (95%% CI %.2f–%.2f)" % t)(mh_or(mh_strata))
          + "**, showing that part of the crude association is attributable to age: "
          "children aged ≥1 year had both a higher background rate of duodenal-type reoperation and a much higher "
          "probability of being operated laparoscopically.")
io.open("Table_stratified.md", "w", encoding="utf-8").write("\n".join(T4))
for x in T4: log(x)

log("")
log("14 例十二指肠持续梗阻的年龄（天）：%s" % sorted(int(AGED[p]) for p in R
    if A[p]["cause"] == "十二指肠持续梗阻" and AGED.get(p) is not None))


# ================================================================ Table 3
log(""); log("=" * 78); log("Table 3（总体率 + 校正/敏感性，Firth 已修正）"); log("=" * 78)

CONV = [p for p in malrot if approach(first[p]) == "中转开腹"]
OPEN = [p for p in malrot if approach(first[p]) == "开腹"]

# mh_or 已提升为模块级函数（含 RBG 区间），此处原有的单值版本已删除

# 竞争风险：与 cif_english.py 同一构造（H=90 行政删失）
from lifelines import CoxPHFitter
import pandas as pd
H = 42          # 与主结局窗口一致（原为 90，三条时间轴自相矛盾；实测最长间隔 37 天）
recs = []
for p in malrot:
    t0 = first[p]["d"]
    if t0 is None: continue
    ev, t = 0, H
    if p in R:
        dd = A[p]["gap"]
        if dd is None and A[p]["d_reop"] and A[p]["d_index"]:
            dd = (A[p]["d_reop"] - A[p]["d_index"]).days
        if dd is not None and 0 < dd <= H: ev, t = 1, dd
    elif p in D["lost"]:
        # 2026-07-27：随访失访 2 例自末次出院日删失——既非竞争事件也非结局。
        dd = (D["last_dis"][p] - t0).days if D["last_dis"][p] else None
        if dd is not None and 0 <= dd <= H: ev, t = 0, dd
    elif p in D["died"]:
        # 竞争事件仅限【确认死亡】：院内死亡 + 电话随访确认死亡。
        # 自动出院但随访确认存活者不在此列，须留在风险集内（曾误计为竞争事件）。
        # 当日死亡 gap=0 必须计入：他们在第 0 天离开风险集，用 0< 会把 7 例
        # 当日放弃出院并死亡者误作"活满 42 天无事件"。时间由下方 max(t,0.5) 处理。
        dd = (D["last_dis"][p] - t0).days if D["last_dis"][p] else None
        if dd is not None and 0 <= dd <= H: ev, t = 2, dd
    recs.append(dict(t=max(float(t), 0.5), ev=ev,
                     lap=1 if approach(first[p]) == "腹腔镜完成" else 0))
cr = pd.DataFrame(recs)
rng = np.random.default_rng(7)
cr["t"] = (cr["t"] + rng.uniform(-0.05, 0.05, len(cr))).clip(lower=0.1)
def cox(evcode):
    """任一臂该类事件为 0 时完全分离，Cox 不可估——返回 None 由调用方改写措辞，
    不可让 exp(coef) 溢出。2026-07-27 竞争事件改为【确认死亡】后腹腔镜臂为 0。"""
    _x = cr.copy(); _x["e"] = (_x.ev == evcode).astype(int)
    if _x[_x.lap == 1]["e"].sum() == 0 or _x[_x.lap == 0]["e"].sum() == 0:
        return None
    x = cr.copy(); x["e"] = (x.ev == evcode).astype(int)
    m = CoxPHFitter().fit(x[["t", "e", "lap"]], duration_col="t", event_col="e")
    ci = m.confidence_intervals_.loc["lap"]
    return math.exp(m.params_["lap"]), math.exp(ci.iloc[0]), math.exp(ci.iloc[1]), m.summary.loc["lap", "p"]
hr1 = cox(1); hr2 = cox(2)

T5 = ["**Table 3.** Overall unplanned reoperation rate by index approach, with adjusted and sensitivity analyses.", "",
      "| Analysis | Estimate | 95% CI | p |", "|---|---|---|---|"]
for nm, ps in [("Laparoscopic completion", LAP), ("Conversion to open", CONV), ("Open", OPEN), ("**All children**", malrot)]:
    x = sum(1 for p in ps if p in R); lo, hi = wilson(x, len(ps))
    T5.append("| %s | %d/%d (%.1f%%) | %.1f–%.1f | — |" % (nm, x, len(ps), x / len(ps) * 100, lo, hi))
a = sum(1 for p in LAP if p in R); c = sum(1 for p in OPR if p in R)
pt, ci = orfmt(a, nL - a, c, nO - c)
T5.append("| Crude, laparoscopic vs. open-related | OR %s | %s (exact) | %.3f |"
          % (pt, ci, fisher_p(a, nL - a, c, nO - c)))
# 对照组内部是否同质——主比较把中转与纯开腹合并，必须让读者看到这一步的代价
_ac = sum(1 for p_ in CONV if p_ in R); _ao = sum(1 for p_ in OPEN if p_ in R)
T5.append("| *Heterogeneity within the comparator:* conversion vs. open | %.1f%% vs. %.1f%% | %s (exact) | %.3f |"
          % (_ac / len(CONV) * 100, _ao / len(OPEN) * 100,
             orfmt(_ac, len(CONV) - _ac, _ao, len(OPEN) - _ao)[1],
             fisher_p(_ac, len(CONV) - _ac, _ao, len(OPEN) - _ao)))
T5.append("| Competing-risk cumulative incidence at 42 days | %.1f%% vs. %.1f%% | — | — |"
          % (sum(1 for _p in LAP if _p in R)/len(LAP)*100, sum(1 for _p in OPR if _p in R)/len(OPR)*100))
T5.append("| Cause-specific Cox (competing event censored) | HR %.2f | %.2f–%.2f | %.3f |" % hr1)

for covs, lab in [([], "Firth, unadjusted"),
                  ([neov, necv], "Firth + neonate (<28 days) + index necrosis"),
                  ([b28, b365, necv], "Firth + age band + index necrosis")]:
    lab_, orv, lo, hi, p = firth(yall, covs, lab)
    T5.append("| %s | OR %.2f | %.2f–%.2f | %.3f |" % (lab_, orv, lo, hi, p))
strata = []
for nm, lo_, hi_ in AGE_BANDS:
    sl = [p for p in LAP if AGED.get(p) is not None and lo_ <= AGED[p] < hi_]
    so = [p for p in OPR if AGED.get(p) is not None and lo_ <= AGED[p] < hi_]
    aa = sum(1 for p in sl if p in R); cc = sum(1 for p in so if p in R)
    strata.append((aa, len(sl) - aa, cc, len(so) - cc))
_mh = mh_or(strata)
T5.append("| Mantel–Haenszel, stratified by age band | %s | %s | — |"
          % (("not estimable", "—") if _mh[0] is None
             else ("OR %.2f" % _mh[0], "%.2f–%.2f" % (_mh[1], _mh[2]))))
x1 = sum(1 for p in LAP + CONV if p in R); n1 = len(LAP) + len(CONV)
x0 = sum(1 for p in OPEN if p in R); n0 = len(OPEN)
T5.append("| Intention-to-treat (conversions grouped with laparoscopic) | OR %.2f | %s (exact) | %.3f |"
          % ((x1 * (n0 - x0)) / ((n1 - x1) * x0), orfmt(x1, n1 - x1, x0, n0 - x0)[1],
             fisher_p(x1, n1 - x1, x0, n0 - x0)))
yrs = {p: first[p]["d"].year for p in LAP if first[p]["d"]}
med = int(np.median(list(yrs.values())))
ea = [p for p in LAP if yrs.get(p) and yrs[p] <= med]; la = [p for p in LAP if yrs.get(p) and yrs[p] > med]
xe = sum(1 for p in ea if p in R); xl = sum(1 for p in la if p in R)
T5.append("| Era effect within laparoscopic group (≤%d vs. >%d) | %.1f%% vs. %.1f%% | — | %.3f |"
          % (med, med, xe / len(ea) * 100, xl / len(la) * 100,
             fisher_p(xe, len(ea) - xe, xl, len(la) - xl)))

# 三行补算：Results/Methods 里点名的敏感性分析，此前只有文字声称、Table 3 无对应数值
# （2026-07-28 审稿意见指出）。三者都用本文件已有的口径（Fisher 精确/条件精确 CI/Firth）。
STAT = all_statuses()
_planned = {p for p, s in STAT.items() if s == "排除-计划性" and p in set(malrot)}
R_plan = R | _planned
pa = sum(1 for p in LAP if p in R_plan); pc = sum(1 for p in OPR if p in R_plan)
_pt, _pci = orfmt(pa, nL - pa, pc, nO - pc)
T5.append("| Counting planned staged reoperations as outcomes | OR %s (%d/%d vs. %d/%d) | %s (exact) | %.3f |"
          % (_pt, pa, nL, pc, nO, _pci, fisher_p(pa, nL - pa, pc, nO - pc)))

NONPRIMARY = D["nonprimary"]
alt_cohort = set(malrot) | NONPRIMARY
alt_lap = [p for p in alt_cohort if approach(first[p]) == "腹腔镜完成"]
alt_opr = [p for p in alt_cohort if approach(first[p]) != "腹腔镜完成"]
alt_R = R | (NONPRIMARY & set(A))     # 放回队列的 18 例里，本就在裁定表有记录的 3 例保留其结局
ra = sum(1 for p in alt_lap if p in alt_R); rc = sum(1 for p in alt_opr if p in alt_R)
_rt, _rci = orfmt(ra, len(alt_lap) - ra, rc, len(alt_opr) - rc)
T5.append("| Reverting the fourth-pass eligibility exclusions (n=%d) | OR %s (%d/%d vs. %d/%d) | %s (exact) | %.3f |"
          % (len(alt_cohort), _rt, ra, len(alt_lap), rc, len(alt_opr), _rci,
             fisher_p(ra, len(alt_lap) - ra, rc, len(alt_opr) - rc)))
_rda = sum(1 for p in alt_lap if p in alt_R and A.get(p, {}).get("cause") == "十二指肠持续梗阻")
_rdc = sum(1 for p in alt_opr if p in alt_R and A.get(p, {}).get("cause") == "十二指肠持续梗阻")
log("[还原资格裁定·十二指肠持续梗阻] lap %d/%d (%.1f%%) vs open-rel %d/%d (%.1f%%)  Fisher p=%.4f"
    % (_rda, len(alt_lap), _rda / len(alt_lap) * 100, _rdc, len(alt_opr), _rdc / len(alt_opr) * 100,
       fisher_p(_rda, len(alt_lap) - _rda, _rdc, len(alt_opr) - _rdc)))

yrs_all = np.array([first[p]["d"].year for p in malrot], dtype=float)
yrv = (yrs_all - yrs_all.mean()) / yrs_all.std()
lab_, orv, lo, hi, pv = firth(yall, [yrv], "Firth + index year")
T5.append("| %s | OR %.2f | %.2f–%.2f | %.3f |" % (lab_, orv, lo, hi, pv))
T5.append("")
T5.append("Wilson 95% confidence intervals for proportions; conditional exact (Cornfield) intervals for odds ratios. "
          "Firth penalized-likelihood logistic regression with p values from the penalized likelihood-ratio test, "
          "obtained by constraining the coefficient of interest to zero within the full design matrix; its 95% "
          "confidence intervals are Wald-type, from the penalized-likelihood standard error, and under "
          "(quasi-)complete separation need not agree with the likelihood-ratio p-value (see the adjusted models below). "
          + (("The competing event occurred only after open-related surgery (%d deaths versus none after "
              "laparoscopic completion), so its cause-specific hazard ratio is not estimable; this is why a "
              "competing-risk framework was used." % int((cr.ev == 2).sum())) if hr2 is None else
             ("The competing event was far commoner after open-related surgery (cause-specific Cox HR for death "
              "%.2f, 95%% CI %.2f–%.2f, p=%.3f), which is why a competing-risk framework was used." % hr2))
          + " The comparator is not internally homogeneous: children converted to open had a higher reoperation "
            "rate than those operated open from the outset, and the intention-to-treat row moves exactly this "
            "subgroup. Every analysis of the **overall** rate is null; the cause-specific and age-stratified "
            "findings are in Tables 3 and 4. Adjusted models for persistent duodenal obstruction are given below.")
T5.append("")
T5.append("**Adjusted models for persistent duodenal obstruction** (Firth penalized likelihood, laparoscopic vs. open-related):")
T5.append("")
T5.append("| Model | OR | 95% CI | p |")
T5.append("|---|---|---|---|")
_fit = []
for covs, lab in [([], "Unadjusted"),
                  ([neov], "+ neonate (<28 days)"),
                  ([neov, necv], "+ neonate + index necrosis"),
                  ([lagev, necv], "+ log(age in days) + index necrosis"),
                  ([b28, b365, necv], "+ age band + index necrosis")]:
    lab_, orv, lo, hi, p = firth(yduo, covs, lab)
    _fit.append((orv, lo, hi, p))
    T5.append("| %s | %.2f | %.2f–%.2f | %.3f |" % (lab_, orv, lo, hi, p))
T5.append("")
# 脚注里的数值全部就地取自上表，避免写死后与数据脱节（曾写死 "p 0.03–0.08"）
_or0 = _fit[0][0]; _adj = [f[0] for f in _fit[1:]]
_nunit = sum(1 for f in _fit if f[1] <= 1.0 <= f[2])      # CI 跨 1 的模型数

def _unity_clause(k):
    if not k: return ""
    return (", and %s despite a penalized likelihood-ratio p below 0.05—expected here because the "
            "table's confidence intervals are Wald-type from the penalized-likelihood standard error rather than "
            "profile-likelihood intervals matched to that same test, and the two need not agree under separation"
            % ("one of them includes unity" if k == 1 else "%d of them include unity" % k))
T5.append("Adjustment for age attenuates the estimate (from OR %.1f unadjusted to %.1f–%.1f adjusted), because age "
          "predicts both the outcome and the choice of approach. These are penalized estimates under complete "
          "separation—no open-related child had this outcome—so they should be read as evidence of direction, not "
          "as effect sizes: the confidence intervals span more than two orders of magnitude%s. "
          "The age-stratified analysis in Table 4 shows where the association actually lies."
          % (_or0, min(_adj), max(_adj), _unity_clause(_nunit)))
io.open("Table_sensitivity_v2.md", "w", encoding="utf-8").write("\n".join(T5))
for x in T5: log(x)

io.open("stratified_out.txt", "w", encoding="utf-8").write("\n".join(L))
print("saved Table_baseline_v2.md / Table_cause_v2.md / Table_stratified.md / Table_sensitivity_v2.md")
