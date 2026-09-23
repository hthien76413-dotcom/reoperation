# -*- coding: utf-8 -*-
"""在【现行六分类】口径下重算两评者「再手术原因」的 Cohen's κ。

为什么需要单独算：
  两位评者当初是在【原始分类】下独立盲评的（当时第5类为「造口相关」，
  且内在畸形归入「十二指肠持续梗阻」）。现行六分类中的第4类「合并畸形漏诊」
  是其后新增的类别，评者从未直接使用过——因此不能把原始 κ 直接标称为
  「六分类的一致性」。

可以诚实重算的理由：
  第4类是两个【评者各自独立盲评过】的属性列的确定性函数：
      合并/漏诊畸形 ≠ 无  且  首次是否已知 = 否-漏诊  →  合并畸形漏诊
  这两列的评者间一致性均为 κ=1.000。故把同一规则分别施加到每位评者
  「自己的」原因+属性评分上，得到的即是该评者在六分类下的评分，
  据此计算的 κ 是真实的评者间一致性，而非事后拼凑。

输出：kappa_6cat_report.txt
"""
import io, math, os, openpyxl

_WIN_DIR = r"D:\全部肠旋转不良\③肠旋转不良术后再手术"
def _resolve(name):
    return name if os.path.exists(name) else os.path.join(_WIN_DIR, name)
FILES = {"评者1": (_resolve("裁定表_评者1.xlsx"), "评者1_再手术原因"),
         "评者2": (_resolve("裁定表_评者2.xlsx"), "评者2_再手术原因")}

def s(v): return "" if v is None else str(v).strip()

def remap(cause, anomaly, known):
    """把原始分类下的一次评分，按现行六分类规则映射。"""
    if not cause: return ""
    # 第4类：再手术才发现/证实的合并畸形
    if anomaly and anomaly != "无" and known == "否-漏诊":
        return "合并畸形漏诊"
    if cause == "造口相关":            return "其他"
    if cause == "复发肠扭转/redo-Ladd": return "肠扭转复发"
    return cause

def load_ratings(path, cause_col):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["A_结局裁定"]
    hdr = [s(ws.cell(1, c).value) for c in range(1, ws.max_column + 1)]
    ic = hdr.index(cause_col) + 1
    ia = hdr.index("合并/漏诊畸形") + 1
    ik = hdr.index("首次是否已知") + 1
    orig, new = {}, {}
    for r in range(2, ws.max_row + 1):
        pid = s(ws.cell(r, 2).value)
        if not pid: continue
        c = s(ws.cell(r, ic).value)
        if not c: continue
        orig[pid] = c
        new[pid] = remap(c, s(ws.cell(r, ia).value), s(ws.cell(r, ik).value))
    return orig, new

def kappa(pairs):
    pairs = [(a, b) for a, b in pairs if a and b]
    n = len(pairs)
    if n == 0: return None
    cats = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    idx = {c: i for i, c in enumerate(cats)}
    k = len(cats)
    M = [[0]*k for _ in range(k)]
    for a, b in pairs: M[idx[a]][idx[b]] += 1
    po = sum(M[i][i] for i in range(k)) / n
    row = [sum(M[i]) / n for i in range(k)]
    col = [sum(M[i][j] for i in range(k)) / n for j in range(k)]
    pe = sum(row[i]*col[i] for i in range(k))
    if pe >= 1: return 1.0, 1.0, 1.0, n, po, cats, M
    kp = (po - pe) / (1 - pe)
    se = math.sqrt(max(po*(1-po), 1e-12) / (n * (1 - pe) ** 2))
    return kp, kp - 1.96*se, kp + 1.96*se, n, po, cats, M

o1, n1 = load_ratings(*FILES["评者1"])
o2, n2 = load_ratings(*FILES["评者2"])
common = sorted(set(o1) & set(o2))

L = []
def log(*a): L.append(" ".join(str(x) for x in a))

log("再手术原因 —— 评者间一致性（原始分类 vs 现行六分类）")
log("=" * 72)
for tag, d1, d2 in [("原始分类（评分当时使用）", o1, o2),
                    ("现行六分类（按确定性规则重映射）", n1, n2)]:
    res = kappa([(d1[p], d2[p]) for p in common])
    kp, lo, hi, n, po, cats, M = res
    log("")
    log("【%s】" % tag)
    log("  Cohen's κ = %.3f (95%%CI %.3f–%.3f)，观察符合率 %.1f%%，n=%d，类别数=%d"
        % (kp, lo, hi, po*100, n, len(cats)))
    dis = [(p, d1[p], d2[p]) for p in common if d1[p] != d2[p]]
    log("  分歧 %d 例：" % len(dis))
    for p, a, b in dis:
        log("    pid=%-10s 评者1=%-22s 评者2=%s" % (p, a, b))

log("")
log("=" * 72)
log("说明：第4类『合并畸形漏诊』由两个评者各自独立盲评的属性列确定性推导——")
log("      『合并/漏诊畸形≠无』且『首次是否已知=否-漏诊』。该两列评者间 κ 均为 1.000，")
log("      故上述『现行六分类』κ 反映的是真实的评者间一致性，而非事后重编码的产物。")

out = "\n".join(L)
io.open("kappa_6cat_report.txt", "w", encoding="utf-8").write(out)
try: print(out)
except UnicodeEncodeError: print(out.encode("gbk", "replace").decode("gbk"))
