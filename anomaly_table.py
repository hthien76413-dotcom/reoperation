# -*- coding: utf-8 -*-
"""合并结构性先天畸形（保守定义，排除孤立 PFO/PDA/继发孔 ASD 等生理性表现）。
按术式分组、病人级去重，供 Table 1 追加行。

两处已落实的修正（2026-07-25）：
 1) 内在十二指肠畸形 24 例经人工调阅核实，排除 4 例（关键词命中均出自入院疑诊，
    出院诊断/术中未证实），见《十二指肠畸形核查清单.xlsx》→ 确认 20 例。
 2) 修复子串误计：'十二指肠闭锁' 含子串 '肠闭锁'，曾使 6 例在 gi_other 被重复计数。
    现在检索 gi_other 前先屏蔽十二指肠类词条。
"""
import io, math, os, openpyxl
from collections import defaultdict
from _dataprep import load, approach
from baseline_table import fisher_2x2
import _dataprep

SRC = _dataprep.SRC
D = load()
malrot, first = D["malrot"], D["first"]
LAP = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
OPEN = [p for p in malrot if approach(first[p]) != "腹腔镜完成"]

wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
dx = defaultdict(str)
ws = wb["住院病历出院记录"]
for r in ws.iter_rows(min_row=2, values_only=True):
    if r and r[0] is not None:
        dx[str(r[0]).strip()] += " " + " ".join(str(r[i]) for i in (3, 5) if len(r) > i and r[i])
ws = wb["病案病理诊断"]
for r in ws.iter_rows(min_row=2, values_only=True):
    if r and r[0] is not None and len(r) > 2 and r[2]:
        dx[str(r[0]).strip()] += " " + str(r[2])

CAT = {
    "duodenal": ["十二指肠闭锁", "十二指肠狭窄", "十二指肠隔膜", "十二指肠膜", "环状胰腺"],
    "gi_other": ["空肠闭锁", "回肠闭锁", "肠闭锁", "食管闭锁", "肛门闭锁", "直肠肛管", "无肛",
                 "肛门直肠", "膈疝", "腹裂", "脐膨出", "胆道闭锁", "巨结肠", "梅克尔", "美克尔"],
    "chd": ["先天性心脏病", "先心病", "室间隔缺损", "法洛", "四联症", "大动脉转位",
            "单心室", "肺动脉闭锁", "右室双出口"],  # 排除孤立 ASD/PFO/PDA
    "heterotaxy": ["内脏异位", "内脏转位", "心房异构", "右位心", "无脾", "多脾"],
    "chromo": ["唐氏", "21三体", "18三体", "13三体", "染色体异常", "三体综合征"],
}

# 人工核实排除的 4 例（住院号 1001469 / 846315 / 1150395 / 1217267）
VERIFIED_EXCLUDED_DUODENAL = {"3545381", "6109437", "2673171", "90868"}

def has(p, cat):
    t = dx.get(p, "")
    if cat == "duodenal":
        return (p not in VERIFIED_EXCLUDED_DUODENAL) and any(k in t for k in CAT[cat])
    if cat == "gi_other":
        # 屏蔽十二指肠类词条，避免 '十二指肠闭锁' 的子串 '肠闭锁' 造成重复计数
        for k in CAT["duodenal"]:
            t = t.replace(k, "")
    return any(k in t for k in CAT[cat])

def has_any(p):  return any(has(p, c) for c in CAT)

def smd_bin(p1, p2):
    """二分类变量的标准化差值：(p1−p2)/sqrt((p1(1−p1)+p2(1−p2))/2)。"""
    den = math.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / 2)
    return 0.0 if den == 0 else (p1 - p2) / den

def row(label, fn):
    a = sum(1 for p in LAP if fn(p)); c = sum(1 for p in OPEN if fn(p))
    alln = a + c
    # Table 1 一律报 SMD 不报基线 p——其脚注已写明理由，这里若报 p 会与脚注自相矛盾
    d = smd_bin(a / len(LAP), c / len(OPEN))
    ds = f"{d:+.2f}".replace("-", "−")      # 用真正的减号，与 Table 1 其余行一致
    if abs(d) >= 0.10: ds = f"**{ds}**"
    return (f"| {label} | {alln} ({alln/len(malrot)*100:.1f}) | "
            f"{a} ({a/len(LAP)*100:.1f}) | {c} ({c/len(OPEN)*100:.1f}) | {ds} |")

L = []
L.append(f"| Characteristic | Overall (n={len(malrot)}) | Laparoscopic completion (n={len(LAP)}) | Open-related (n={len(OPEN)}) | SMD\\* |")
L.append("|---|---|---|---|---|")
L.append(row("Any associated structural anomaly, n (%)", has_any))
L.append(row("— Intrinsic duodenal anomaly (atresia/stenosis/annular pancreas)", lambda p: has(p, "duodenal")))
L.append(row("— Other GI / abdominal-wall anomaly", lambda p: has(p, "gi_other")))
L.append(row("— Structural congenital heart disease", lambda p: has(p, "chd")))
L.append(row("— Heterotaxy / situs anomaly", lambda p: has(p, "heterotaxy")))
L.append(row("— Chromosomal / syndromic", lambda p: has(p, "chromo")))
L.append("")
L.append("\\* Isolated patent foramen ovale, patent ductus arteriosus, and secundum atrial "
         "septal defect were treated as physiological in neonates and excluded. Keyword-screened "
         "from discharge and coded diagnoses; all 24 keyword-positive intrinsic duodenal anomalies "
         "underwent manual chart review, of which 4 were excluded (term appeared only as an "
         "unconfirmed admission-time suspicion), leaving 20 verified cases.")
txt = "\n".join(L)
io.open("Table1_anomaly_rows.md", "w", encoding="utf-8").write(txt)
try: print(txt)
except UnicodeEncodeError: print(txt.encode("gbk", "replace").decode("gbk"))
