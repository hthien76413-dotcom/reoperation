import os, sys
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

print("腹腔镜完成 n =", nL, " 开腹相关 n =", nO)
print()
for zh in CAUSES6:
    a = sum(1 for p in LAP if p in R and A[p]["cause"] == zh)
    c = sum(1 for p in OPR if p in R and A[p]["cause"] == zh)
    print("%-45s lap = %2d/%d (%.4f)   opr = %2d/%d (%.4f)"
          % (EN[zh], a, nL, a / nL, c, nO, c / nO))
