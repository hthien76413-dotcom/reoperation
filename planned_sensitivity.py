# -*- coding: utf-8 -*-
"""排除的 11 例『计划性再手术』：构成核查 + 敏感性分析。

起因（审稿意见 v2 第 6 条）：计划性再手术被排除，但在两组间高度不均衡
（开腹相关 9 vs 腹腔镜 2，p=0.014），等于把开腹组的返台事件系统性摘掉。
本脚本先看这 11 例到底是什么，再做把它们计入结局的敏感性分析。

核查过程中发现的更根本的问题：队列纳入用的是
    is_malrot(first[p]) —— 检查【首台手术名 + 首台诊断】是否含旋转不良关键词
诊断栏命中即可入组，于是若一名患儿首台是【直肠活检】而诊断栏写了『肠旋转不良』，
他就以『活检的入路』被记为暴露，真正的 Ladd 手术却发生在其后。本脚本量化全队列
里有多少这样的病例。

输出 planned_sensitivity_out.txt
"""
import io, math
import numpy as np
import openpyxl
from scipy import stats
from _dataprep import load, approach, reop_set, adjudicated, ADJ as ADJ_PATH, AGE_BANDS

L = []
def log(*a): L.append(" ".join(str(x) for x in a))

D = load(); A = adjudicated(); R = reop_set()
malrot, first, ops, AGED = D["malrot"], D["first"], D["ops"], D["age_d"]
LAP = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
OPR = [p for p in malrot if approach(first[p]) != "腹腔镜完成"]
nL, nO = len(LAP), len(OPR)

def fisher_p(a, b, c, d): return stats.fisher_exact([[a, b], [c, d]])[1]
def _lc(n, k): return math.lgamma(n+1) - math.lgamma(k+1) - math.lgamma(n-k+1)
def exact_or_ci(a, b, c, d, alpha=0.05):
    n1, n2, m1 = a+b, c+d, a+c
    def tail(psi, up):
        lo, hi = max(0, m1-n2), min(n1, m1)
        ks = np.arange(lo, hi+1)
        lw = np.array([_lc(n1, k) + _lc(n2, m1-k) for k in ks]) + ks*math.log(psi)
        w = np.exp(lw - lw.max()); w /= w.sum()
        return w[ks >= a].sum() if up else w[ks <= a].sum()
    def solve(t, up):
        if up and a == max(0, m1-n2): return 0.0
        if (not up) and a == min(n1, m1): return float("inf")
        f = lambda lp: tail(math.exp(lp), up) - t
        loP, hiP = -30.0, 30.0
        for _ in range(300):
            mid = (loP+hiP)/2
            if (f(mid) > 0) == (f(loP) > 0): loP = mid
            else: hiP = mid
        return math.exp((loP+hiP)/2)
    return solve(alpha/2, True), solve(alpha/2, False)
def orline(a, b, c, d):
    pt = "%.2f" % ((a*d)/(b*c)) if b and c else ("∞" if a else "0")
    lo, hi = exact_or_ci(a, b, c, d)
    return "%s (%.2f–%s)" % (pt, lo, "∞" if not np.isfinite(hi) else "%.1f" % hi)

# ---------------------------------------------------------------- 1 构成
LADD_KW = ["拉德", "ladd", "Ladd", "LADD", "扭转复位"]
def is_ladd_operation(op):
    """只看【手术名称】是否为 Ladd 类术式，不看诊断栏。"""
    return any(k in (op["sname"] or "") for k in LADD_KW)

ws = openpyxl.load_workbook(ADJ_PATH, data_only=True)["A_结局裁定"]
planned = []
for r in range(2, ws.max_row + 1):
    pid = ws.cell(r, 2).value
    if pid is None: continue
    pid = str(pid).strip()
    if str(ws.cell(r, 12).value or "").strip() != "排除-计划性": continue
    planned.append((pid, ws.cell(r, 6).value, str(ws.cell(r, 13).value or "")))

log("=" * 78)
log("1  11 例『排除-计划性』的实际构成")
log("=" * 78)
log("  %-10s %-6s %-5s %-9s %s" % ("编号", "在队列", "间隔", "首台入路", "首台手术名称（是否 Ladd 类术式）"))
n_in = 0
for pid, gap, note in planned:
    inc = pid in set(malrot)
    n_in += inc
    f = first.get(pid)
    sn = (f["sname"] or "").replace("\n", " ")[:46] if f else "?"
    log("  %-10s %-6s %-5s %-9s %s %s" % (
        pid, "是" if inc else "否", gap, approach(f) if f else "?",
        "[Ladd]" if f and is_ladd_operation(f) else "[非Ladd]", sn))
log("")
log("  在 466 队列内的有 %d/11 例。" % n_in)

# ---------------------------------------------------------------- 2 队列纳入问题
log("")
log("=" * 78)
log("2  队列纯度：首台其实不是【初次 Ladd 手术】的病例")
log("=" * 78)
notladd = [p for p in malrot if not is_ladd_operation(first[p])]
log("  466 例中首台术名不含『拉德/Ladd/扭转复位』者 %d 例。逐例判读后可分两类：" % len(notladd))

DIAG_ONLY = ["活检", "活组织检查", "镜检查", "结肠镜", "胃镜"]
THERAP = ["松解", "切除", "吻合", "成形", "修补", "造口", "复位", "探查", "引流", "还纳", "减压", "切开"]
POST = ["术后", "手术的随诊", "手术后随诊"]

def is_diag_only(op):
    """纯诊断性操作（内镜/活检），且不含任何治疗性术式。"""
    sn = op["sname"] or ""
    return any(k in sn for k in DIAG_ONLY) and not any(k in sn for k in THERAP)

def is_post_previous(op):
    """诊断栏把本次住院描述为【既往旋转不良手术之后】——则本台并非初次 Ladd。"""
    dx = op["dx"] or ""
    return any(k in dx for k in POST)

# 只要首台术名里出现 Ladd 类术式，就是初次 Ladd，不论是否同台还做了胃镜等。
nonprimary = sorted({p for p in notladd if is_diag_only(first[p]) or is_post_previous(first[p])})
log("")
log("  (a) 首台仅为内镜/活检，或诊断栏明确为『旋转不良术后』的随诊/再入院 —— 非初次 Ladd：%d 例"
    % len(nonprimary))
for p in nonprimary:
    log("      %-10s %-9s %-42s | dx: %s" % (
        p, approach(first[p]), (first[p]["sname"] or "").replace("\n", " ")[:42],
        (first[p]["dx"] or "").replace("\n", " ")[:46]))
rest = [p for p in notladd if p not in set(nonprimary)]
log("")
log("  (b) 其余 %d 例是急诊剖腹探查/合并畸形手术等【确为初次旋转不良手术】，只是术名未写 Ladd：" % len(rest))
for p in sorted(rest)[:8]:
    log("      %-10s %-9s %s" % (p, approach(first[p]), (first[p]["sname"] or "").replace("\n", " ")[:56]))
log("      …（共 %d 例，保留在队列内）" % len(rest))

later_ladd = [p for p in notladd
              if any(is_ladd_operation(o) for o in ops[p] if o["d"] and first[p]["d"] and o["d"] > first[p]["d"])]
log("")
log("  其中【真正的 Ladd 手术发生在首台之后】者 %d 例：%s" % (len(later_ladd), sorted(later_ladd)))
for p in sorted(later_ladd):
    for o in sorted([x for x in ops[p] if x["d"]], key=lambda x: x["d"])[1:3]:
        if is_ladd_operation(o):
            log("      %-10s 首台记为 %-9s，真 Ladd 在 %s 且为 %s → 暴露错分"
                % (p, approach(first[p]), o["d"].date(), approach(o)))
a = sum(1 for p in nonprimary if approach(first[p]) == "腹腔镜完成")
log("")
log("  非初次 Ladd 的 %d 例：首台记为腹腔镜 %d、开腹相关 %d；其中再手术 %d 例。"
    % (len(nonprimary), a, len(nonprimary)-a, sum(1 for p in nonprimary if p in R)))
log("  → 对内镜/活检这类『手术』判定入路本身没有意义，且它们几乎全被默认归入开腹相关，")
log("    会稀释开腹组的事件率。下节以剔除它们作敏感性分析。")
notladd = nonprimary          # 敏感性分析用『非初次 Ladd』这一集合，而非全部 29 例

# ---------------------------------------------------------------- 3 敏感性分析
log("")
log("=" * 78)
log("3  敏感性分析：把计划性再手术计入结局 / 剔除非 Ladd 首台")
log("=" * 78)

def report(tag, cohort, event):
    lap = [p for p in cohort if approach(first[p]) == "腹腔镜完成"]
    opr = [p for p in cohort if approach(first[p]) != "腹腔镜完成"]
    a = sum(1 for p in lap if p in event); c = sum(1 for p in opr if p in event)
    b, d = len(lap)-a, len(opr)-c
    log("  %-42s 腹腔镜 %2d/%-3d (%4.1f%%)  开腹相关 %2d/%-3d (%4.1f%%)  OR %s  p=%.3f"
        % (tag, a, len(lap), a/len(lap)*100, c, len(opr), c/len(opr)*100,
           orline(a, b, c, d), fisher_p(a, b, c, d)))

COH = set(malrot)
PLAN = {p for p, _, _ in planned} & COH
a = sum(1 for p in PLAN if approach(first[p]) == "腹腔镜完成")
c = len(PLAN) - a
log("  计划性再手术在队列内共 %d 例（另 4 例不属于 466 队列）：腹腔镜 %d/%d (%.1f%%)、"
    "开腹相关 %d/%d (%.1f%%)，Fisher p=%.3f"
    % (len(PLAN), a, nL, a/nL*100, c, nO, c/nO*100, fisher_p(a, nL-a, c, nO-c)))
log("  【订正】审稿意见 v2 曾记为『开腹 9 vs 腹腔镜 2，p=0.014』——那是把 11 例全部对上队列分母，")
log("          其中 4 例并不在 466 队列内。订正后不均衡程度小得多，见上行。")
log("")
log("  — 结局＝任何计划外再手术 —")
report("① 主分析（现稿）", COH, R)
report("② 把计划性再手术也计入结局", COH, R | PLAN)
report("③ 剔除非初次 Ladd 者", COH - set(notladd), R)
report("④ ②＋③ 同时", COH - set(notladd), (R | PLAN) - set(notladd))
log("")
log("  — 结局＝十二指肠持续梗阻（核心结论） —")
DUO = {p for p in R if A[p]["cause"] == "十二指肠持续梗阻"}
report("① 主分析（现稿）", COH, DUO)
report("③ 剔除非初次 Ladd 者", COH - set(notladd), DUO)
log("")
log("  — 新生儿层（核心结论所在层），结局＝十二指肠持续梗阻 —")
NEO = {p for p in malrot if AGED.get(p) is not None and AGED[p] < 28}
report("① 主分析（现稿）", COH & NEO, DUO)
report("③ 剔除非初次 Ladd 者", (COH & NEO) - set(notladd), DUO)

out = "\n".join(L)
io.open("planned_sensitivity_out.txt", "w", encoding="utf-8").write(out)
print("saved planned_sensitivity_out.txt")
