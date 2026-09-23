import os, sys
_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(_d, "_dataprep.py")):
    _p = os.path.dirname(_d)
    if _p == _d:
        raise SystemExit("找不到 _dataprep.py，请确认本脚本仍在原仓库目录树下（任意层子文件夹均可）")
    _d = _p
sys.path.insert(0, _d)
from _dataprep import load, approach, reop_set, adjudicated

D = load()
R = reop_set()
A = adjudicated()
malrot, first = D["malrot"], D["first"]
R = {p for p in R if p in set(malrot)}
NEO = D["neonate"]

LAP = {p for p in malrot if approach(first[p]) == "腹腔镜完成"}
OPR = {p for p in malrot if approach(first[p]) != "腹腔镜完成"}

lap_neo = LAP & NEO
opr_neo = OPR & NEO

duo_lap_neo = {p for p in lap_neo if p in R and A[p]["cause"] == "十二指肠持续梗阻"}
duo_opr_neo = {p for p in opr_neo if p in R and A[p]["cause"] == "十二指肠持续梗阻"}

print("新生儿层（年龄 <28 天）")
print("腹腔镜完成 n =", len(lap_neo), " 开腹相关 n =", len(opr_neo))
print()
print("十二指肠持续梗阻:")
print("腹腔镜完成: %d/%d = %.4f" % (len(duo_lap_neo), len(lap_neo), len(duo_lap_neo) / len(lap_neo)))
print("开腹相关:   %d/%d = %.4f" % (len(duo_opr_neo), len(opr_neo), len(duo_opr_neo) / len(opr_neo)))
