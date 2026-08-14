# -*- coding: utf-8 -*-
"""【2026-07-29 状态更新：本脚本的探索性发现已被吸收，勿再据本文件判断"是否已修"】

把【已知且可识别】的两类错误从"只写进局限"改为"在主数据集里改正"，并量化影响
——这是 2026-07-27 当天的探索/诊断脚本，运行本脚本时下述两类错误确实
"均已在稿中承认，但均未修正主数据集"。此后当天即扩展为正式的第四遍盲法
资格裁定（19 例问题索引记录、两名评者独立判读、κ=0.844），结论已固化进
`_dataprep.py` 的 `INDEX_FIX`（对应本文件的"方案 B"：31645511 改判为真 Ladd、
保留在队列、暴露改腹腔镜）与 `NONPRIMARY`（18 例排除，覆盖并扩大了本文件
下面 NON_LADD 列出的 10 例）。现行正稿 §2.2/§2.4 第四遍裁定即为此修复的
披露，Table 4 "Reverting the fourth-pass eligibility exclusions" 一行是其敏感性
分析。本脚本保留仅作为该问题的原始发现记录，不代表当前数据集状态。

两类错误（发现时的原始描述）：
  E1 10 例的首台记录并非初次 Ladd 手术——或仅为内镜/活检，或诊断栏明确写着
     "肠旋转不良术后"（即 Ladd 已在别处/更早完成，属现患而非新发）。
     按本稿自己的纳入标准（primary Ladd operation）本不应入组。
  E2 其中 1 例（31645511）在数据库内存在真正的 Ladd 手术，且为腹腔镜完成，
     却因首台是"开放性大肠活组织检查"而被记为【开腹】——暴露方向性错分。

方案 A：剔除全部 10 例
方案 B：剔除 9 例 + 把 E2 那 1 例的首台改判为真正的 Ladd（保留在队列内，暴露改为腹腔镜完成）
        →【已采纳，即 `_dataprep.py` 现行逻辑】
"""
import io, sys, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from scipy.stats import fisher_exact
from scipy.stats.contingency import odds_ratio
import _dataprep as D

d = D.load()
coh = set(d["malrot"]); first = d["first"]; ops = d["ops"]
adj = D.adjudicated(); ad = d["age_d"]
LAPS = "腹腔镜完成"
REOP = {p for p in adj if p in coh}
DUO = {p for p, v in adj.items() if p in coh and v["cause"] == "十二指肠持续梗阻"}

NON_LADD = ["1325420", "1463669", "17337851", "18598477", "20002991",
            "28934957", "31645511", "4370043", "5400633", "8336031"]
E2 = "31645511"

THERAP = ["松解", "切除", "吻合", "成形", "修补", "造口", "复位", "探查",
          "引流", "还纳", "减压", "切开", "拉德", "Ladd", "根治"]

def is_ladd_op(o):
    """真正的 Ladd 手术：命中旋转不良关键词，且不是"纯诊断性"操作。
    注意：同一台手术可能既做 Ladd 又顺带取活检，故不能只看到"活组织检查"就排除
    ——必须同时确认不含任何治疗性术式（此处曾出错，漏掉了 31645511 的真 Ladd）。"""
    sn = o["sname"] or ""
    diag = any(k in sn for k in ("活检", "活组织检查", "镜检查", "结肠镜", "胃镜"))
    ther = any(k in sn for k in THERAP)
    return D.is_malrot(o) and not (diag and not ther)

# E2 的真 Ladd
cand = sorted([o for o in ops[E2] if o["d"] and is_ladd_op(o)], key=lambda x: x["d"])
print("=== E2 患儿 %s 的手术记录 ===" % E2)
for o in sorted(ops[E2], key=lambda x: (x["d"] or __import__("datetime").datetime(2100,1,1))):
    print("   %s | %s" % (o["d"].date() if o["d"] else "??", (o["sname"] or "")[:52]))
if cand:
    print("   → 真 Ladd: %s，入路 %s" % (cand[0]["d"].date(), D.approach(cand[0])))

def stats(keys, appr):
    out = {}
    for nm, S in (("any", REOP), ("duo", DUO)):
        a = sum(1 for p in keys if appr[p] == LAPS and p in S)
        b = sum(1 for p in keys if appr[p] == LAPS) - a
        c = sum(1 for p in keys if appr[p] != LAPS and p in S)
        e = sum(1 for p in keys if appr[p] != LAPS) - c
        r = odds_ratio([[a, b], [c, e]], kind="conditional")
        lo, hi = r.confidence_interval(0.95)
        out[nm] = (a, a+b, c, c+e, r.statistic, lo, hi,
                   fisher_exact([[a, b], [c, e]])[1])
    neo = [p for p in keys if ad.get(p) is not None and ad[p] < 28]
    a = sum(1 for p in neo if appr[p] == LAPS and p in DUO)
    b = sum(1 for p in neo if appr[p] == LAPS) - a
    c = sum(1 for p in neo if appr[p] != LAPS and p in DUO)
    e = sum(1 for p in neo if appr[p] != LAPS) - c
    out["neo"] = (a, a+b, c, c+e, None, None, None,
                  fisher_exact([[a, b], [c, e]])[1])
    return out

base_appr = {p: D.approach(first[p]) for p in coh}

scen = {}
scen["现稿（466，未修正）"] = (coh, base_appr)
A = coh - set(NON_LADD)
scen["方案 A：剔除全部 10 例"] = (A, base_appr)
B = coh - (set(NON_LADD) - {E2})
apprB = dict(base_appr)
if cand: apprB[E2] = D.approach(cand[0])
scen["方案 B：剔除 9 例 + 改判 1 例"] = (B, apprB)

for nm, (keys, appr) in scen.items():
    s = stats(keys, appr)
    nlap = sum(1 for p in keys if appr[p] == LAPS)
    print("\n=== %s ===  n=%d（腹腔镜 %d / 开腹相关 %d）"
          % (nm, len(keys), nlap, len(keys) - nlap))
    for lab, k in (("任何再手术", "any"), ("十二指肠梗阻", "duo")):
        a, na, c, nc, orv, lo, hi, pv = s[k]
        print("  %-12s 腹腔镜 %2d/%3d (%.1f%%)  开腹相关 %2d/%3d (%.1f%%)  "
              "OR %.2f (%.2f–%.1f)  p=%.4f"
              % (lab, a, na, a/na*100, c, nc, c/nc*100, orv, lo, hi, pv))
    a, na, c, nc, _, _, _, pv = s["neo"]
    print("  %-12s 腹腔镜 %2d/%3d (%.1f%%)  开腹相关 %2d/%3d (%.1f%%)  p=%.4f"
          % ("新生儿·十二指肠", a, na, a/na*100, c, nc, c/nc*100, pv))
