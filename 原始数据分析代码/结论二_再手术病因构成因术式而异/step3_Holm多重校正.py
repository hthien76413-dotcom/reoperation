import os, sys
from scipy import stats
_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(_d, "_dataprep.py")):
    _p = os.path.dirname(_d)
    if _p == _d:
        raise SystemExit("找不到 _dataprep.py，请确认本脚本仍在原仓库目录树下（任意层子文件夹均可）")
    _d = _p
sys.path.insert(0, _d)
from _dataprep import load, approach, reop_set, adjudicated, CAUSES6

D = load()
R = reop_set()
A = adjudicated()
malrot, first = D["malrot"], D["first"]
R = {p for p in R if p in set(malrot)}

LAP = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
OPR = [p for p in malrot if approach(first[p]) != "腹腔镜完成"]
nL, nO = len(LAP), len(OPR)

EN = {"十二指肠持续梗阻": "1. Persistent duodenal obstruction",
      "肠坏死/穿孔/吻合口并发症": "2. Necrosis / perforation / anastomotic complication",
      "粘连性肠梗阻": "3. Adhesive obstruction (non-duodenal)",
      "合并畸形漏诊": "4. Missed associated anomaly",
      "肠扭转复发": "5. Recurrent volvulus / redo-Ladd",
      "其他": "6. Other"}


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out = [0.0] * len(ps); prev = 0.0
    for rank, i in enumerate(order):
        prev = min(1.0, max(prev, (len(ps) - rank) * ps[i])); out[i] = prev
    return out


praw = []
labels = []
for zh in CAUSES6:
    a = sum(1 for p in LAP if p in R and A[p]["cause"] == zh)
    c = sum(1 for p in OPR if p in R and A[p]["cause"] == zh)
    pv = stats.fisher_exact([[a, nL - a], [c, nO - c]])[1]
    praw.append(pv)
    labels.append(EN[zh])

padj = holm(praw)

print("Holm 逐步法，六个病因的族内校正：")
for lab, p, pa in zip(labels, praw, padj):
    sig = "  *** p<0.05 ***" if pa < 0.05 else ""
    print("%-45s raw p = %.6f   Holm-adjusted p = %.6f%s" % (lab, p, pa, sig))
