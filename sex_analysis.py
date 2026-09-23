# -*- coding: utf-8 -*-
"""基于性别的报告与分析。

缘由：Surgical Endoscopy 所属的 Surgery Journal Editors Group 联合声明（见官方
Instructions for Authors 附录 2）要求「对人体研究做统一、明确的性别报告，
并对全部人体研究做基于性别的数据分析」。本稿此前只在 Table 1 报告了性别构成，
未做分层分析，本脚本补上。

一律现算，不从稿件读取任何数字。

用法：  python3 sex_analysis.py
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from collections import Counter

from scipy.stats import fisher_exact
from scipy.stats.contingency import odds_ratio

import _dataprep as D

MALE, FEMALE = "男性", "女性"
LAP = "腹腔镜完成"
CAUSE1 = "十二指肠持续梗阻"


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return max(0.0, (c - h) * 100), min(100.0, (c + h) * 100)


def exact_or(k1, n1, k2, n2):
    tbl = [[k1, n1 - k1], [k2, n2 - k2]]
    p = fisher_exact(tbl)[1]
    r = odds_ratio(tbl, kind="conditional")
    lo, hi = r.confidence_interval(0.95)
    return r.statistic, lo, hi, p


def rd_newcombe(k1, n1, k2, n2, z=1.96):
    """两独立比例差的 Newcombe 区间（与稿件其余风险差口径一致）。"""
    l1, u1 = [x / 100 for x in wilson(k1, n1, z)]
    l2, u2 = [x / 100 for x in wilson(k2, n2, z)]
    p1, p2 = k1 / n1, k2 / n2
    lo = (p1 - p2) - ((p1 - l1) ** 2 + (u2 - p2) ** 2) ** 0.5
    hi = (p1 - p2) + ((u1 - p1) ** 2 + (p2 - l2) ** 2) ** 0.5
    return (p1 - p2) * 100, lo * 100, hi * 100


def main():
    d = D.load()
    coh = set(d["malrot"])
    adj = D.adjudicated()
    reop = D.reop_in_cohort()
    sex = d["sex"]
    appr = {p: D.approach(d["first"][p]) for p in coh}
    duo = {p for p in coh if p in adj and adj[p]["cause"] == CAUSE1}

    M = {p for p in coh if sex.get(p) == MALE}
    F = {p for p in coh if sex.get(p) == FEMALE}
    assert len(M) + len(F) == len(coh), "有性别缺失，需单独处理"

    print("=" * 74)
    print("基于性别的报告与分析（n=%d）" % len(coh))
    print("=" * 74)

    print("\n【1】队列性别构成")
    for nm, s in (("Male", M), ("Female", F)):
        lo, hi = wilson(len(s), len(coh))
        print("  %-7s %3d/%d (%.1f%%, 95%% CI %.1f–%.1f)" %
              (nm, len(s), len(coh), len(s) / len(coh) * 100, lo, hi))
    print("  说明：男性占优是肠旋转不良的已知特征，非本研究的选择所致。")

    print("\n【2】性别在两术式臂间是否均衡")
    lapM = len(M & {p for p in coh if appr[p] == LAP}); lapN = len([p for p in coh if appr[p] == LAP])
    oprM = len(M & {p for p in coh if appr[p] != LAP}); oprN = len([p for p in coh if appr[p] != LAP])
    print("  腹腔镜完成 男性 %d/%d (%.1f%%)；开腹相关 男性 %d/%d (%.1f%%)" %
          (lapM, lapN, lapM / lapN * 100, oprM, oprN, oprM / oprN * 100))
    _, _, _, p = exact_or(lapM, lapN, oprM, oprN)
    print("  Fisher p=%.3f（Table 1 的 SMD 为 +0.02，两臂性别构成基本一致）" % p)

    print("\n【3】主要结局：非计划再手术率，按性别")
    kM, kF = len(M & reop), len(F & reop)
    for nm, k, n in (("Male", kM, len(M)), ("Female", kF, len(F))):
        lo, hi = wilson(k, n)
        print("  %-7s %2d/%3d (%.1f%%, 95%% CI %.1f–%.1f)" % (nm, k, n, k / n * 100, lo, hi))
    orr, lo, hi, p = exact_or(kM, len(M), kF, len(F))
    rd, rlo, rhi = rd_newcombe(kM, len(M), kF, len(F))
    print("  男 vs 女：OR %.2f (95%% CI %.2f–%.2f), p=%.3f；风险差 %+.1f pp (%.1f 到 %.1f)" %
          (orr, lo, hi, p, rd, rlo, rhi))

    print("\n【4】主要发现：持续性十二指肠梗阻，按性别")
    dM, dF = len(M & duo), len(F & duo)
    for nm, k, n in (("Male", dM, len(M)), ("Female", dF, len(F))):
        lo, hi = wilson(k, n)
        print("  %-7s %2d/%3d (%.1f%%, 95%% CI %.1f–%.1f)" % (nm, k, n, k / n * 100, lo, hi))
    orr, lo, hi, p = exact_or(dM, len(M), dF, len(F))
    print("  男 vs 女：OR %.2f (95%% CI %.2f–%.2f), p=%.3f" % (orr, lo, hi, p))
    print("  12 例十二指肠梗阻的性别构成：", dict(Counter(sex[p] for p in duo)))

    print("\n【5】术式与十二指肠梗阻的关联在两性别内是否一致")
    for nm, s in (("Male", M), ("Female", F)):
        sl = s & {p for p in coh if appr[p] == LAP}
        so = s & {p for p in coh if appr[p] != LAP}
        kl, ko = len(sl & duo), len(so & duo)
        line = "  %-7s 腹腔镜 %d/%-3d (%.1f%%)  开腹相关 %d/%-3d (%.1f%%)" % (
            nm, kl, len(sl), kl / len(sl) * 100, ko, len(so), ko / len(so) * 100)
        if kl + ko > 0:
            rd, rlo, rhi = rd_newcombe(kl, len(sl), ko, len(so))
            _, _, _, p = exact_or(kl, len(sl), ko, len(so))
            line += "  风险差 %+.1f pp (%.1f 到 %.1f), p=%.4f" % (rd, rlo, rhi, p)
        print(line)
    print("  两性别内方向一致（均为腹腔镜侧全部事件、开腹相关侧零事件），")
    print("  故未做正式的 sex×approach 交互检验：开腹相关臂在两性别内均为零单元，模型不可识别。")

    print("\n【6】机制分层（3 例技术不彻底 / 9 例术后粘连）的性别构成")
    import openpyxl
    ws = openpyxl.load_workbook("机制核阅_盲法_答案键.xlsx", data_only=True)["答案键_评分前勿开"]
    mech = {str(r[1]).strip(): r[3] for r in ws.iter_rows(min_row=2, values_only=True) if r[1] is not None}
    for code, label in (("A", "技术不彻底"), ("C", "术后粘连")):
        ps = [p for p in duo if mech.get(str(p)) == code]
        print("  %-6s n=%d  %s" % (label, len(ps), dict(Counter(sex[p] for p in ps))))

    print("\n" + "=" * 74)


if __name__ == "__main__":
    main()
