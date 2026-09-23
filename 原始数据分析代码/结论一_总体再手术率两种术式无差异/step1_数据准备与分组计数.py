import os, sys
_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(_d, "_dataprep.py")):
    _p = os.path.dirname(_d)
    if _p == _d:
        raise SystemExit("找不到 _dataprep.py，请确认本脚本仍在原仓库目录树下（任意层子文件夹均可）")
    _d = _p
sys.path.insert(0, _d)
from _dataprep import load, approach, reop_set

D = load()
R = reop_set()
malrot, first = D["malrot"], D["first"]
R = {p for p in R if p in set(malrot)}

LAP = [p for p in malrot if approach(first[p]) == "腹腔镜完成"]
CONV = [p for p in malrot if approach(first[p]) == "中转开腹"]
OPEN = [p for p in malrot if approach(first[p]) == "开腹"]
OPR = CONV + OPEN

n_all, n_lap, n_conv, n_open, n_opr = len(malrot), len(LAP), len(CONV), len(OPEN), len(OPR)
e_all = sum(1 for p in malrot if p in R)
e_lap = sum(1 for p in LAP if p in R)
e_conv = sum(1 for p in CONV if p in R)
e_open = sum(1 for p in OPEN if p in R)
e_opr = sum(1 for p in OPR if p in R)

print("队列总数 n =", n_all)
print("腹腔镜完成 n =", n_lap, " 再手术 =", e_lap, " 率 = %.4f" % (e_lap / n_lap))
print("中转开腹  n =", n_conv, " 再手术 =", e_conv, " 率 = %.4f" % (e_conv / n_conv))
print("开腹      n =", n_open, " 再手术 =", e_open, " 率 = %.4f" % (e_open / n_open))
print("开腹相关(中转+开腹) n =", n_opr, " 再手术 =", e_opr, " 率 = %.4f" % (e_opr / n_opr))
print("全队列 n =", n_all, " 再手术 =", e_all, " 率 = %.4f" % (e_all / n_all))
print()
print("2x2 表（腹腔镜完成 vs 开腹相关）")
print("a =", e_lap, " b =", n_lap - e_lap, " c =", e_opr, " d =", n_opr - e_opr)
