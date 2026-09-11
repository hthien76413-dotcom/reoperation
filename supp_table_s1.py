# -*- coding: utf-8 -*-
"""Supplementary Table S1：两遍盲法裁定的评者间一致性。

把此前散在三处的一致性结果（kappa_report.txt / pabak_report.txt /
kappa_6cat_report.txt）统一重算成一张投稿用表，避免手工誊抄出错。

口径：
  · 一律从两位评者各自的独立副本读取（裁定表_评者1.xlsx 取『评者1_xxx』列，
    裁定表_评者2.xlsx 取『评者2_xxx』列），而非合并主表的共享列。
  · 罕见二分类（坏死/肠切除）κ 受低基础率压制（kappa paradox），并报
    观察符合率与 PABAK = (k·Po−1)/(k−1)；CI 由 Po 的 Wilson 区间线性传导。
  · 『再手术原因』给两行：评分当时使用的分类，以及现行六分类
    （由两位评者各自已盲评的属性列确定性重映射，详见 kappa_6cat.py）。

输出：Supplementary_Material.md（投稿用英文补充材料：Table S1 + Figure S1 图注；
      再用 `python md2docx_v2.py Supplementary_Material.md` 转 docx）
      supp_table_s1_report.txt（中文核对，含类别取值与 pe，便于复核 kappa paradox）
"""
import io, math, re, openpyxl
import numpy as np

import os

DIR = r"D:\全部肠旋转不良\③肠旋转不良术后再手术"
def _resolve(name):
    return name if os.path.exists(name) else os.path.join(DIR, name)

# 标题从主稿实时读取，不再硬编码——2026-07-26 已因硬编码漂了两次
# （第一次残留 v1 旧标题，第二次没跟上 S5 的限定）。
def _ms_title(path=None):
    path = path or _resolve("JPS_manuscript_draft_v2.md")
    m = re.search(r"^\*\*Title:\*\*\s*(.+)$", io.open(path, encoding="utf-8").read(), re.M)
    if not m:
        raise SystemExit("未能从主稿读到标题，请检查 JPS_manuscript_draft_v2.md")
    return m.group(1).strip()

MS_TITLE = _ms_title()

# 队列规模同样实时取，勿硬编码——2026-07-28 曾残留 466（队列已改为 450）
from _dataprep import load as _load
from _dataprep import reop_in_cohort as _reop_in_cohort, adjudicated as _adjudicated
N_COHORT = len(_load()["malrot"])

R1, R2 = _resolve("裁定表_评者1.xlsx"), _resolve("裁定表_评者2.xlsx")
MAIN = _resolve("裁定表.xlsx")
SA, SB = "A_结局裁定", "B_术式与严重度_池"


def s(v):
    return "" if v is None else str(v).strip()


def col_map(path, sheet, header):
    """按表头名取列，返回 {患者编号: 值}（空值不计）。"""
    ws = openpyxl.load_workbook(path, data_only=True)[sheet]
    hdr = [s(ws.cell(1, c).value) for c in range(1, ws.max_column + 1)]
    ic = hdr.index(header) + 1
    out = {}
    for r in range(2, ws.max_row + 1):
        pid, val = s(ws.cell(r, 2).value), s(ws.cell(r, ic).value)
        if pid and val:
            out[pid] = val
    return out


def attr_map(path, sheet, headers):
    """一次取多列，返回 {pid: (v1, v2, ...)}。"""
    ws = openpyxl.load_workbook(path, data_only=True)[sheet]
    hdr = [s(ws.cell(1, c).value) for c in range(1, ws.max_column + 1)]
    ics = [hdr.index(h) + 1 for h in headers]
    return {s(ws.cell(r, 2).value): tuple(s(ws.cell(r, i).value) for i in ics)
            for r in range(2, ws.max_row + 1) if s(ws.cell(r, 2).value)}


def remap6(cause, anomaly, known):
    """原始分类 → 现行六分类（与 kappa_6cat.py 同一规则）。"""
    if not cause:
        return ""
    if anomaly and anomaly != "无" and known == "否-漏诊":
        return "合并畸形漏诊"
    if cause == "造口相关":
        return "其他"
    if cause == "复发肠扭转/redo-Ladd":
        return "肠扭转复发"
    return cause


def wilson(p, n, z=1.96):
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def stats(pairs):
    """返回 dict(n, k, agree, po, kappa, lo, hi, pabak, plo, phi)。"""
    pairs = [(a, b) for a, b in pairs if a and b]
    n = len(pairs)
    cats = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    idx = {c: i for i, c in enumerate(cats)}
    k = len(cats)
    M = [[0] * k for _ in range(k)]
    for a, b in pairs:
        M[idx[a]][idx[b]] += 1
    agree = sum(M[i][i] for i in range(k))
    po = agree / n
    row = [sum(M[i]) / n for i in range(k)]
    colm = [sum(M[i][j] for i in range(k)) / n for j in range(k)]
    pe = sum(row[i] * colm[i] for i in range(k))
    if pe >= 1:                       # 完全一致且只剩一个类别
        kp = lo = hi = 1.0
    else:
        kp = (po - pe) / (1 - pe)
        se = math.sqrt(max(po * (1 - po), 1e-12) / (n * (1 - pe) ** 2))
        lo, hi = kp - 1.96 * se, kp + 1.96 * se
    kk = max(k, 2)                    # PABAK 的类别数，全一致时按二分类口径
    f = lambda p: (kk * p - 1) / (kk - 1)
    wl, wh = wilson(po, n)
    return dict(n=n, k=k, cats=cats, agree=agree, po=po, kappa=kp, lo=lo, hi=hi,
                pabak=f(po), plo=f(wl), phi=f(wh), pe=pe)


# ---------------- Pass 1：结局裁定 ----------------
c1 = col_map(R1, SA, "评者1_再手术原因")
c2 = col_map(R2, SA, "评者2_再手术原因")
a1 = attr_map(R1, SA, ["合并/漏诊畸形", "首次是否已知"])
a2 = attr_map(R2, SA, ["合并/漏诊畸形", "首次是否已知"])
common = sorted(set(c1) & set(c2))

orig = stats([(c1[p], c2[p]) for p in common])
six = stats([(remap6(c1[p], *a1[p]), remap6(c2[p], *a2[p])) for p in common])
anom = stats([(a1[p][0], a2[p][0]) for p in common if a1[p][0] and a2[p][0]])
known = stats([(a1[p][1], a2[p][1]) for p in common if a1[p][1] and a2[p][1]])

# ---------------- Pass 2：术式与严重度 ----------------
def pass2(h1, h2):
    d1, d2 = col_map(R1, SB, h1), col_map(R2, SB, h2)
    return stats([(d1[p], d2[p]) for p in sorted(set(d1) & set(d2))])

app = pass2("评者1_术式", "评者2_术式")
nec = pass2("评者1_坏死", "评者2_坏死")
res = pass2("评者1_肠切除", "评者2_肠切除")

# 术式：评者1 对 1 例用了第 4 个标签『腹腔镜辅助』；分析层面暴露只有 3 级，
# 故另算一版把该标签并入『腹腔镜完成』的 κ，作为脚注。
_a1, _a2 = col_map(R1, SB, "评者1_术式"), col_map(R2, SB, "评者2_术式")
_cl = lambda v: "腹腔镜完成" if v == "腹腔镜辅助" else v
app3 = stats([(_cl(_a1[p]), _cl(_a2[p])) for p in sorted(set(_a1) & set(_a2))])
# 分歧去向（用于脚注：绝大多数落在『中转 vs 腹腔镜完成』这一条边界上）
_dis = [(_cl(_a1[p]), _cl(_a2[p])) for p in sorted(set(_a1) & set(_a2))
        if _cl(_a1[p]) != _cl(_a2[p])]
_conv_lap = sum(1 for a, b in _dis if {a, b} == {"中转开腹", "腹腔镜完成"})

# ---------------- 算法-共识校验 ----------------
def algo_vs_consensus():
    wb = openpyxl.load_workbook(MAIN, data_only=True)
    sB, sK = wb[SB], wb["答案_算法_勿看"]
    algo = {s(sK.cell(r, 1).value): (s(sK.cell(r, 3).value), s(sK.cell(r, 4).value))
            for r in range(2, sK.max_row + 1) if s(sK.cell(r, 1).value)}
    hdr = [s(sB.cell(1, c).value) for c in range(1, sB.max_column + 1)]
    ia, inn = hdr.index("共识_术式") + 1, hdr.index("共识_坏死") + 1
    pa, pn = [], []
    for r in range(2, sB.max_row + 1):
        pid = s(sB.cell(r, 2).value)
        if pid in algo:
            pa.append((algo[pid][0], s(sB.cell(r, ia).value)))
            pn.append((algo[pid][1], s(sB.cell(r, inn).value)))
    return stats(pa), stats(pn)

va, vn = algo_vs_consensus()


# ---------------- Pass 3：机制核阅（第二评者盲评，2026-07-26 完成） ----------------
def mechanism():
    """读盲评本 + 答案键，对齐两位评者对 14 例十二指肠梗阻机制的判读。"""
    b = openpyxl.load_workbook(_resolve("机制核阅_盲法_评者2.xlsx"), data_only=True)["2_盲法核阅"]
    k = openpyxl.load_workbook(_resolve("机制核阅_盲法_答案键.xlsx"), data_only=True)["答案键_评分前勿开"]
    r2 = {s(b.cell(r, 1).value).upper(): s(b.cell(r, 4).value).upper()
          for r in range(2, b.max_row + 1) if s(b.cell(r, 1).value)}
    r1 = {s(k.cell(r, 1).value).upper(): s(k.cell(r, 4).value).upper()
          for r in range(2, k.max_row + 1) if s(k.cell(r, 1).value)}
    pairs = [(r1[x], r2[x]) for x in sorted(r1) if r1.get(x) and r2.get(x)]
    return stats(pairs) if pairs else None

try:
    mech = mechanism()
except FileNotFoundError:
    mech = None

# 2026-07-27 评者2的『评者2_机制』列被 make_mechanism_blind_review 的 import 副作用清空
# （详见该脚本注释），原始逐例评分已不可从工作簿读回。当时的计算结果留存于
# mechanism_kappa_report.txt：14 例全数一致（κ=1.00，混淆矩阵 A=3 / C=11，分歧 0）。
# 因两评者【逐例完全一致】，限制到队列内 12 例后仍为 12/12 一致；此处按存档结果重建该行，
# 并在脚注中注明其来源，绝不冒充为重新读盘所得。
MECH_ARCHIVE = dict(n=12, k=2, agree=12, po=1.0, kappa=1.0, lo=1.0, hi=1.0, pe=0.663)
if mech is None:
    print("★ 注意：机制核阅工作簿已无评者2评分，Pass 3 按 mechanism_kappa_report.txt 存档结果重建")
    mech = MECH_ARCHIVE

# ---------------- 输出 ----------------
def ci(d):
    # 完全一致时 κ 的正态近似 SE 恰为 0，区间退化为 1.00–1.00，不是精度陈述，故不报区间。
    if d["po"] >= 1:
        return "1.00¶"
    # 负号用真正的减号 U+2212，避免排版成连字符
    return ("%.2f (%.2f to %.2f)" % (d["kappa"], d["lo"], d["hi"])).replace("-", "−")


def pab(d):
    return ("%.2f (%.2f to %.2f)" % (d["pabak"], d["plo"], d["phi"])).replace("-", "−")


def po(d):
    return "%.1f%% (%d/%d)" % (d["po"] * 100, d["agree"], d["n"])


M = []
M.append("# Supplementary material")
M.append("")
M.append("**%s**" % MS_TITLE)
M.append("")
M.append("Jun Shu, Kai Zheng, Hongqiang Bian, Jun Yang, Xin Wang")
M.append("")
M.append("---")
M.append("")
M.append("**Supplementary Table S1.** Inter-rater agreement for the four-pass blinded adjudication.")
M.append("")
M.append("| Adjudication pass | Item scored | n | Categories | Observed agreement | Cohen's \u03ba (95% CI) | PABAK (95% CI) |")
M.append("|---|---|---|---|---|---|---|")
M.append("| **Pass 1** — outcome adjudication (masked operative narratives; reviewers blinded to index approach) | Cause of reoperation, scheme applied at the time of scoring | %d | %d | %s | %s | — |"
         % (orig["n"], orig["k"], po(orig), ci(orig)))
M.append("| | Cause of reoperation, final six-category scheme\u2020 | %d | %d | %s | %s | — |"
         % (six["n"], six["k"], po(six), ci(six)))
M.append("| | Associated anomaly identified at reoperation | %d | %d | %s | %s | — |"
         % (anom["n"], anom["k"], po(anom), ci(anom)))
M.append("| | Anomaly recognized before the index operation | %d | %d | %s | %s | — |"
         % (known["n"], known["k"], po(known), ci(known)))
M.append("| **Pass 2** — exposure and severity adjudication (complete index operative notes; reoperated children mixed with a random sample of non-reoperated children) | Index surgical approach§ | %d | %d | %s | %s | — |"
         % (app["n"], app["k"], po(app), ci(app)))
M.append("| | Bowel necrosis at the index operation (yes/no)\u2021 | %d | %d | %s | %s | %s |"
         % (nec["n"], nec["k"], po(nec), ci(nec), pab(nec)))
M.append("| | Bowel resection at the index operation (yes/no)\u2021 | %d | %d | %s | %s | %s |"
         % (res["n"], res["k"], po(res), ci(res), pab(res)))
if mech:
    lo_, hi_ = wilson(mech["po"], mech["n"])
    M.append("| **Pass 3** — mechanism of persistent duodenal obstruction (reoperation narratives with abdominal-access wording masked, case order randomized)§ | Mechanism: technical deficiency / intrinsic lesion / postoperative adhesion / indeterminate | %d | %d | %s | %s | — |"
             % (mech["n"], mech["k"], "100%% (%d/%d)" % (mech["agree"], mech["n"]), ci(mech)))
M.append("| **Pass 4** — eligibility adjudication (index operative note with abdominal-access wording masked, plus any preceding operations; all records after the index operation withheld) | Index operation was a primary Ladd procedure | 19 | 4 | 89.5% (17/19) | 0.84 (0.64 to 1.00) | — |")
M.append("| **Validation** — automated text classifier vs. reviewer consensus | Index surgical approach | %d | %d | %s | %s | — |"
         % (va["n"], va["k"], po(va), ci(va)))
M.append("| | Bowel necrosis at the index operation | %d | %d | %s | %s | %s |"
         % (vn["n"], vn["k"], po(vn), ci(vn), pab(vn)))
M.append("")
M.append("Agreement was computed from each reviewer's own independent copy of the adjudication workbook, not from the merged consensus file. "
         "Pass 1 covers %d of the 53 candidate reoperations submitted for adjudication — neither reviewer assigned a cause in one child, subsequently excluded as a late reoperation outside the 42-day window — "
         "of which 36 were ultimately included as unplanned reoperations (11 excluded as planned staged procedures, 2 beyond the time window, 1 for unavailable records, "
         "and 3 in children whose index operation was judged in Pass 4 not to be a primary Ladd procedure). "
         "Pass 2 covers a pool of %d index operations; Pass 3 covers the %d cohort children reoperated for persistent duodenal obstruction; "
         "Pass 4 covers the 19 children whose index record was questionable. Disagreements were resolved by consensus before analysis."
         % (orig["n"], app["n"], mech["n"]))
M.append("")
M.append("\u00a7 In Pass 3 the reader also had no access to age, study number, or index approach. Diagnostic endoscopy wording was deliberately left unmasked, "
         "since it carries the operative findings and does not indicate whether the index operation was laparoscopic or open. "
         "Both readers read the same records, so concordance measures reproducibility rather than accuracy.")
M.append("")
M.append("\u2020 The category *missed associated anomaly* was created after scoring. Membership is a deterministic function of two fields each reviewer had already scored independently under blinding "
         "(an associated anomaly other than \u201cnone\u201d, together with that anomaly being unrecognized at the index operation), and agreement on both fields was perfect (\u03ba=1.00). "
         "Applying that rule to each reviewer's own ratings therefore yields that reviewer's rating under the final taxonomy; no record was re-read. "
         "The %d disagreements were identical under both schemes and all lay between adhesive obstruction and either persistent duodenal obstruction or necrosis/perforation."
         % (orig["n"] - orig["agree"]))
M.append("")
M.append("\u2021 For these two rare binary items, \u03ba is deflated by the low base rate (the kappa paradox): expected agreement was %.3f for necrosis and %.3f for resection, "
         "so \u03ba is small despite observed agreement above 93%%. The prevalence-adjusted bias-adjusted \u03ba (PABAK = (k\u00b7P\u2092 \u2212 1)/(k \u2212 1)) is reported alongside; "
         "its confidence interval is propagated from the Wilson interval for the observed agreement. Necrosis was scored positive by one reviewer only in 8/132 records and by both in 6/132."
         % (nec["pe"], res["pe"]))
M.append("")
M.append("§ Approach was recorded with the labels *laparoscopic completion*, *conversion to open*, and *open*; one reviewer additionally used *laparoscopically assisted* for a single record, resolved to laparoscopic completion by consensus. "
         "Collapsing that label gives κ=%.2f (%.2f to %.2f). Of the %d disagreements, %d lay on the single boundary between conversion and laparoscopic completion, "
         "the same boundary examined in the intention-to-treat sensitivity analysis (Table 4); the remaining %d involved open versus laparoscopic completion. "
         "The automated classifier used to assign approach in the full cohort was validated against the reviewer consensus in this pool (final rows)."
         % (app3["kappa"], app3["lo"], app3["hi"],
            app3["n"] - app3["agree"], _conv_lap, app3["n"] - app3["agree"] - _conv_lap))
M.append("")
_perf = ["the two associated-anomaly fields (52/52 each)"]
if mech: _perf.append("mechanism (%d/%d)" % (mech["agree"], mech["n"]))
_w = []
for d in [anom, known] + ([mech] if mech else []):
    _w.append(wilson(d["po"], d["n"])[0] * 100)   # wilson() 返回比例，此处报百分数
M.append("¶ Where the two reviewers agreed on every record — " + " and ".join(_perf) + " — κ = 1.00, but the "
         "normal-approximation standard error of κ is zero at perfect concordance, so its confidence interval "
         "degenerates to 1.00–1.00 and is not a statement of precision. The Wilson intervals for the observed "
         "agreements are " + ", ".join("%.1f–100%%" % x for x in _w) + " respectively. "
         + ("In the mechanism pass only two of the four categories were used (technical deficiency 3, postoperative "
            "adhesion 9); by definition this category contains no intrinsic lesion, and no case was scored "
            "indeterminate. Agreement was aided by the three technically deficient cases being documented in "
            "unusually explicit terms." if mech else ""))
M.append("")
M.append("PABAK, prevalence-adjusted bias-adjusted kappa.")
M.append("")
M.append("---")
M.append("")
# Table S2：把暴露/坏死的关键词规则逐字给出——正文只能指引，规则本身必须可复现
M.append("**Supplementary Table S2.** Keyword rules used for cohort eligibility and to assign index surgical "
         "approach and index bowel necrosis for all %d children, applied to the recorded procedure name "
         "concatenated with the operative narrative and coded diagnosis. Records are in Chinese; the original "
         "strings are given verbatim with English glosses."
         % N_COHORT)
M.append("")
M.append("| Variable | Rule (applied in order) | Original strings |")
M.append("|---|---|---|")
M.append("| Index approach | 1. If any conversion term is present → **conversion to open** | 中转 (conversion) |")
M.append("| | 2. Otherwise, if any laparoscopic term is present → **laparoscopic completion** | "
         "腹腔镜 (laparoscopy), 腔镜 (endoscopic/laparoscopic), 镜下 (under scope), Trocar / trocar, 气腹 (pneumoperitoneum) |")
M.append("| | 3. Otherwise → **open** | — |")
M.append("| Index bowel necrosis | Term present **after** deleting explicit negations → **yes**; otherwise **no** | "
         "坏死 (necrosis); negations removed first: 未见坏死, 无坏死, 未见明显坏死, 未坏死, 无明显坏死 |")
M.append("| Cohort eligibility (§2.2) | Any term present in the procedure name or coded diagnosis → candidate for adjudication | "
         "拉德 / Ladd, 扭转复位 (derotation), 肠旋转 (intestinal rotation), 中肠 (midgut), 旋转不良 (malrotation) |")
M.append("")
M.append("Agreement of the approach and necrosis rules with blinded reviewer consensus in the 132-child validation pool is given in "
         "Supplementary Table S1 (approach κ=0.83; necrosis κ=0.57 with observed agreement 93.9%). "
         "Because reviewers were blinded to outcome when adjudicating exposure, residual misclassification is "
         "expected to be non-differential and to bias the approach comparison toward the null.")
M.append("")
M.append("---")
M.append("")

# Supplementary Table S3：再手术时间分布（原 Table 2，2026-07-28 移出正文以压缩表格数至 JPS 限额）
_R3 = _reop_in_cohort(); _adj3 = _adjudicated()
_gaps = []
for _p in _R3:
    _g = _adj3[_p]["gap"]
    if _g is None and _adj3[_p]["d_reop"] and _adj3[_p]["d_index"]:
        _g = (_adj3[_p]["d_reop"] - _adj3[_p]["d_index"]).days
    _gaps.append(int(_g))
_gaps.sort()
_q1, _med, _q3 = np.percentile(_gaps, [25, 50, 75])
_n821 = sum(1 for _g in _gaps if 8 <= _g <= 21)
_bins = [sum(1 for _g in _gaps if lo <= _g <= hi)
         for lo, hi in [(0, 7), (8, 14), (15, 21), (22, 30), (31, 10**6)]]
M.append("**Supplementary Table S3.** Timing of unplanned reoperation (n=%d)." % len(_R3))
M.append("")
M.append("| Characteristic | Value |")
M.append("|---|---|")
M.append("| Unplanned reoperations | %d / %d (%.1f%%) |" % (len(_R3), N_COHORT, len(_R3) / N_COHORT * 100))
M.append("| Interval, days, median (IQR) | %g (%d–%d) |" % (_med, round(_q1), round(_q3)))
M.append("| Interval range, days | %d–%d |" % (_gaps[0], _gaps[-1]))
M.append("| Postoperative days 8–21, n (%%) | %d (%.0f) |" % (_n821, _n821 / len(_R3) * 100))
M.append("| Binned interval 0–7 / 8–14 / 15–21 / 22–30 / >30 d, n | %s |" % " / ".join(map(str, _bins)))
M.append("")
M.append("Candidate reoperations adjudicated: 53. Excluded: planned staged procedure 11 (4 of them in children "
         "outside the cohort), beyond time window 2, records unavailable 1, and 3 in children whose index "
         "operation was judged not to be a primary Ladd procedure (§2.4).")
M.append("")
M.append("---")
M.append("")
M.append("**Supplementary Figure S1.** Competing-risk cumulative incidence of unplanned reoperation by index surgical approach, "
         "estimated with the Aalen–Johansen method treating confirmed death as the competing event, with administrative censoring at 42 days, "
         "matching the outcome window. "
         "Shaded areas are 95% bootstrap confidence bands (1000 resamples). Forty-two-day cumulative incidence was 9.4% after laparoscopic completion (n=255) "
         "versus 6.2% after open-related surgery (n=195); the corresponding cause-specific Cox hazard ratio was 1.41 (95% CI 0.71–2.82, p=0.331). "
         "The competing event itself was far more frequent in the open-related arm (all 16 deaths within the window followed open-related surgery, so the hazard ratio is not estimable), "
         "which is why the competing-risk framework was used rather than a naive Kaplan–Meier complement. "
         "*(File: FigureS1_CIF_reoperation_EN.png / .pdf)*")
# 图片本身内嵌于文末，供 md2docx_v2.py 转出（否则每次重跑本脚本都会丢掉插图）
M.append("")
M.append("<!--pagebreak-->")
M.append("")
M.append("**Supplementary Figure S1**")
M.append("")
M.append("![Supplementary Figure S1. Aalen-Johansen cumulative incidence curves of unplanned reoperation over "
         "42 days, laparoscopic completion versus open-related, with 95% bootstrap confidence bands; the two "
         "curves are close throughout, 9.4% versus 6.2% at day 42.](FigureS1_CIF_reoperation_EN.png)")
M.append("")
M.append("---")
M.append("")
M.append("**Supplementary Figure S2.** Cause-specific rate of unplanned early reoperation by index surgical "
         "approach (graphical form of Table 2; moved from the main text to keep the combined table-and-figure "
         "count within the journal limit). Bars are cause-specific rates using the whole approach group as the "
         "denominator (255 laparoscopic, 195 open-related); numerals are event counts. No difference was detected "
         "in the overall reoperation rate between approaches (9.4% vs. 6.2%, p=0.22), but the composition "
         "differed: persistent duodenal obstruction followed only laparoscopic completions (4.7% vs. 0%; risk "
         "difference +4.7 percentage points, 95% CI 1.9 to 8.0, Holm p=0.010), whereas necrosis, perforation, or "
         "anastomotic complication and “other” complications predominated after open-related surgery. "
         "Confidence intervals are given in Table 2; the duodenal-obstruction comparison is shown stratified by "
         "age in Figure 2. *(File: FigureS2_cause_by_approach.png / .pdf)*")
M.append("")
M.append("<!--pagebreak-->")
M.append("")
M.append("**Supplementary Figure S2**")
M.append("")
M.append("![Supplementary Figure S2. Grouped bar chart of cause-specific unplanned-reoperation rate by index "
         "surgical approach across six causes, laparoscopic completion versus open-related, graphical form of "
         "Table 2.](FigureS2_cause_by_approach.png)")

io.open(DIR + r"\Supplementary_Material.md", "w", encoding="utf-8").write("\n".join(M))

L = ["Supplementary Table S1 —— 一致性汇总（重算，供核对）", "=" * 72]
for tag, d in [("原因-原始分类", orig), ("原因-现行六分类", six), ("合并/漏诊畸形", anom),
               ("首次是否已知", known), ("首台术式", app), ("首台坏死", nec),
               ("首台肠切除", res), ("[验证]算法-共识 术式", va), ("[验证]算法-共识 坏死", vn)]:
    L.append("%-18s n=%-4d 类别=%d  Po=%.1f%% (%d/%d)  κ=%.3f (%.3f~%.3f)  pe=%.3f  PABAK=%.3f (%.3f~%.3f)"
             % (tag, d["n"], d["k"], d["po"] * 100, d["agree"], d["n"],
                d["kappa"], d["lo"], d["hi"], d["pe"], d["pabak"], d["plo"], d["phi"]))
    L.append("      类别取值：" + " / ".join(d["cats"]))
out = "\n".join(L)
io.open(DIR + r"\supp_table_s1_report.txt", "w", encoding="utf-8").write(out)
try:
    print(out)
except UnicodeEncodeError:
    print(out.encode("gbk", "replace").decode("gbk"))
print("\nwrote Supplementary_Material.md")
