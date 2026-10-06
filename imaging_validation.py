# -*- coding: utf-8 -*-
"""影像学独立核验：12 例持续性十二指肠梗阻，术后影像能否印证盲法机制学分类。

动机：稿件当前最大的方法学软肋是自己承认的那一句——两位评者读的是**同一份手术记录**，
所以「concordance measures reproducibility rather than accuracy」。本脚本用一个
**独立数据源**（术后影像报告）去检验机制分类，并顺带给出诊断路径的定量描述。

三个问题：
  Q1 首台术后至再手术之间，这些患儿做了什么检查？（诊断路径）
  Q2 上消化道造影能否发现该梗阻？其阴性能否排除？（临床可操作性）
  Q3 影像表现能否区分「技术不彻底(A)」与「术后粘连(C)」？（分类的外部验证）

一律现算，不从稿件读取任何数字。输出为聚合统计，不含患者标识。

用法：  python3 imaging_validation.py
       路径经 _dataprep 解析（环境变量 MALROT_SRC / MALROT_ADJ > 工作目录 > 作者本机）。
"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from collections import defaultdict, Counter
from datetime import datetime

import openpyxl
from scipy.stats import mannwhitneyu, fisher_exact

import _dataprep as D

MECH_KEY = "机制核阅_盲法_答案键.xlsx"
CAUSE1 = "十二指肠持续梗阻"
# 机制编码（见 十二指肠梗阻再手术_归因核阅v3.xlsx / 判读标准）
MECH_LABEL = {"A": "技术不彻底", "B": "内在病变", "C": "术后粘连", "D": "无法判断"}

# 造影报告的判读以【对比剂通过】的明确陈述为准，而不是以形态学词汇的出现为准。
# 这样做的理由：报告里「显示不清」「形态显示不清」讲的是成像质量，不是梗阻；
# 而「扩张」既出现在阳性句，也出现在「未见梗阻及扩张」这种否定句里，单看词无法定性。
DUO = r"十二指肠"
# 通过受阻的明确陈述 —— 判为阳性
POS_TRANSIT = ["通过不畅", "通过显示不畅", "通过欠通畅", "通过显示欠通畅", "通过受阻"]
# 形态学异常 —— 仅作辅助描述，单独出现不足以定为阳性
POS_MORPH = ["变窄", "弹簧征", "螺旋状", "圈变形", "曲变形"]
# 通过正常的明确陈述 —— 判为阴性
NEG_TRANSIT = ["通过顺利", "通过可", "通过尚通畅", "显示通畅",
               "未见梗阻及扩张", "未见明显梗阻及扩张", "未见梗阻征象"]


def load_mechanisms():
    ws = openpyxl.load_workbook(MECH_KEY, data_only=True)["答案键_评分前勿开"]
    out = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[1] is not None:
            out[str(r[1]).strip()] = {"approach": r[2], "mech": r[3]}
    return out


def parse_dt(t):
    if isinstance(t, datetime):
        return t
    if isinstance(t, str):
        for cut, fmt in ((19, "%Y-%m-%d %H:%M:%S"), (10, "%Y-%m-%d")):
            try:
                return datetime.strptime(t[:cut], fmt)
            except Exception:
                pass
    return None


def load_imaging(pids):
    """取三种模态的报告；返回 {pid: [(模态, 名称, 时间, 全文), ...]}，已按内容去重。"""
    spec = {"X线报告":  ("报告名称", "检查时间", "检查所见", "检查结论"),
            "超声报告": ("超声报告名称", "超声检查时间", "超声检查所见", "超声检查结论"),
            "CT报告":   ("报告名称", "检查时间", "检查所见", "检查结论")}
    wb = openpyxl.load_workbook(D.SRC, data_only=True, read_only=True)
    out = defaultdict(list)
    for sheet, (ncol, tcol, fcol, ccol) in spec.items():
        ws, hdr, ix = wb[sheet], None, None
        for row in ws.iter_rows(values_only=True):
            if hdr is None:
                hdr = list(row); ix = {h: i for i, h in enumerate(hdr)}; continue
            pid = str(row[0]).strip() if row[0] is not None else ""
            if pid not in pids:
                continue
            txt = ((row[ix[fcol]] or "") + " || " + (row[ix[ccol]] or ""))
            out[pid].append((sheet, row[ix[ncol]], parse_dt(row[ix[tcol]]), " ".join(str(txt).split())))
    # 同一次检查在库中可能重复导入：按 (名称, 时间, 全文) 去重
    for pid in out:
        seen, uniq = set(), []
        for rec in out[pid]:
            k = (rec[1], rec[2], rec[3])
            if k not in seen:
                seen.add(k); uniq.append(rec)
        out[pid] = uniq
    return out


def is_contrast(name):
    return "造影" in str(name)


def duodenal_verdict(txt):
    """判读一份造影报告在十二指肠水平是否提示梗阻。

    只看「小肠：…」那一段（十二指肠所在处），并以对比剂通过的陈述为准：
      阳性   明确写了通过不畅/欠通畅
      阴性   明确写了通过顺利/未见梗阻
      形态可疑 只有形态学异常而无通过受阻的陈述
    """
    if DUO not in txt:
        return "无十二指肠描述"
    seg = [s for s in re.split(r"[;；。\n]", txt) if DUO in s]
    body = " ".join(seg)
    if any(w in body for w in POS_TRANSIT):
        return "阳性"
    morph = any(w in body for w in POS_MORPH)
    if any(w in body for w in NEG_TRANSIT):
        return "形态可疑但通过正常" if morph else "阴性"
    return "形态可疑" if morph else "未描述异常"


def main():
    adj = D.adjudicated()
    d = D.load()
    coh = set(d["malrot"])
    cases = [p for p, v in adj.items() if p in coh and v.get("cause") == CAUSE1]
    mech = load_mechanisms()
    assert len(cases) == 12, "病因1 例数应为 12，实为 %d" % len(cases)
    assert all(str(p) in mech for p in cases), "有病例缺机制判定"

    grp = {p: mech[str(p)]["mech"] for p in cases}
    img = load_imaging({str(p) for p in cases})

    print("=" * 78)
    print("影像学独立核验：%d 例持续性十二指肠梗阻" % len(cases))
    print("=" * 78)
    print("机制分布：", {MECH_LABEL[k]: v for k, v in Counter(grp.values()).items()})
    print("首台入路：", Counter(mech[str(p)]["approach"] for p in cases))

    # ---- Q0 时距是否区分机制（阴性对照）--------------------------------------
    print("\n【Q0】首台→再手术间隔能否区分机制")
    A = [adj[p]["gap"] for p in cases if grp[p] == "A"]
    C = [adj[p]["gap"] for p in cases if grp[p] == "C"]
    nA = [adj[p]["gap"] for p in cases if grp[p] == "A" and d["age_d"][p] < 28]
    nC = [adj[p]["gap"] for p in cases if grp[p] == "C" and d["age_d"][p] < 28]
    oC = [adj[p]["gap"] for p in cases if grp[p] == "C" and d["age_d"][p] >= 365]
    fmt = lambda v: "n=%d 中位%.1f (%d–%d)" % (len(v), sorted(v)[len(v)//2], min(v), max(v))
    print("   A 技术不彻底  %s" % fmt(A))
    print("   C 术后粘连    %s" % fmt(C))
    print("   —— 限新生儿： A %s ; C %s" % (fmt(nA), fmt(nC)))
    print("   —— C 组 ≥1岁： %s" % fmt(oC))
    print("   A vs C（全部）      p=%.3f  ← 受年龄混杂" % mannwhitneyu(A, C).pvalue)
    print("   A vs C（限新生儿）  p=%.3f  ← 无区分力" % mannwhitneyu(A, nC).pvalue)
    print("   新生儿 vs ≥1岁      p=%.3f  ← 真实信号是年龄，不是机制" % mannwhitneyu(nA + nC, oC).pvalue)

    # ---- Q1 诊断路径 ---------------------------------------------------------
    print("\n【Q1】首台术后至再手术之间的检查")
    win = {}
    for p in cases:
        di, dr = adj[p]["d_index"], adj[p]["d_reop"]
        win[p] = sorted([(( t - di).days, sh, nm, tx) for sh, nm, t, tx in img.get(str(p), [])
                         if t and di <= t <= dr])
    n_img = sum(len(v) for v in win.values())
    print("   %d/%d 例有窗口内影像，共 %d 份（去重后）" % (sum(1 for v in win.values() if v), len(cases), n_img))
    print("   模态：", dict(Counter(sh for v in win.values() for _, sh, _, _ in v)))
    ncon = sum(1 for v in win.values() for _, _, nm, _ in v if is_contrast(nm))
    withcon = [p for p in cases if any(is_contrast(nm) for _, _, nm, _ in win[p])]
    print("   上消化道/全消化道造影 %d 份，覆盖 %d/%d 例" % (ncon, len(withcon), len(cases)))
    for m in ("A", "C"):
        ps = [p for p in cases if grp[p] == m]
        cov = [p for p in ps if p in withcon]
        print("     机制%s(%s)：%d/%d 例做过造影" % (m, MECH_LABEL[m], len(cov), len(ps)))

    # ---- Q2 造影的检出能力 ---------------------------------------------------
    print("\n【Q2】造影对该梗阻的检出能力（每例取窗口内最后一次造影）")
    last, verdict = {}, {}
    for p in cases:
        con = [(pod, nm, tx) for pod, sh, nm, tx in win[p] if is_contrast(nm)]
        if con:
            last[p] = con[-1]
            verdict[p] = duodenal_verdict(con[-1][2])
    print("   %d 例可评：%s" % (len(verdict), dict(Counter(verdict.values()))))
    for m in ("A", "C"):
        ps = [p for p in cases if grp[p] == m and p in verdict]
        print("     机制%s(%s)：%s" % (m, MECH_LABEL[m], dict(Counter(verdict[p] for p in ps))))
    print("   逐例（机制 / 末次造影 POD / 判读 / 该次距再手术天数）：")
    for p in sorted(verdict, key=lambda x: (grp[x], adj[x]["gap"])):
        pod = last[p][0]
        print("     %s  POD%-3d  %-14s  距再手术 %2d 天"
              % (grp[p], pod, verdict[p], adj[p]["gap"] - pod))
    fn = [p for p in verdict if verdict[p] != "阳性"]
    print("   末次造影【未明确提示】十二指肠通过受阻者 %d/%d 例" % (len(fn), len(verdict)))
    print("     其中机制A %d 例、机制C %d 例" % (sum(1 for p in fn if grp[p] == "A"),
                                              sum(1 for p in fn if grp[p] == "C")))
    if fn:
        print("     这些病例末次造影距再手术 %s 天" %
              sorted(adj[p]["gap"] - last[p][0] for p in fn))

    # ---- Q3 影像能否区分机制 -------------------------------------------------
    print("\n【Q3】造影表现能否区分 A 与 C")
    tab = Counter((grp[p], verdict[p] == "阳性") for p in verdict)
    a_pos = tab[("A", True)]; a_neg = tab[("A", False)]
    c_pos = tab[("C", True)]; c_neg = tab[("C", False)]
    print("            造影阳性  造影阴性")
    print("   A 技术      %2d        %2d" % (a_pos, a_neg))
    print("   C 粘连      %2d        %2d" % (c_pos, c_neg))
    if min(a_pos + a_neg, c_pos + c_neg) > 0:
        print("   Fisher p=%.3f" % fisher_exact([[a_pos, a_neg], [c_pos, c_neg]])[1])
    # 形态学征象是否为某一机制所独有
    print("\n   特征性征象在两组中的出现（造影全文）：")
    for w in ("螺旋状", "弹簧征", "变窄", "变形", "扩张"):
        ga = sum(1 for p in cases if grp[p] == "A" and any(w in tx for _, _, nm, tx in win[p] if is_contrast(nm)))
        gc = sum(1 for p in cases if grp[p] == "C" and any(w in tx for _, _, nm, tx in win[p] if is_contrast(nm)))
        print("     %-6s A组 %d/3 例，C组 %d/9 例" % (w, ga, gc))

    print("\n" + "=" * 78)


if __name__ == "__main__":
    main()
