import os, sys
from scipy import stats
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
lap_neo, opr_neo = LAP & NEO, OPR & NEO
n1, n2 = len(lap_neo), len(opr_neo)

x_lap = sum(1 for p in lap_neo if p in R and A[p]["cause"] == "十二指肠持续梗阻")

H_WIN = 42
def _within_window(p):
    t0 = first[p]["d"]
    dd = (D["last_dis"][p] - t0).days if (t0 and D["last_dis"].get(p)) else None
    return dd is not None and 0 <= dd <= H_WIN

comp = {p for p in malrot if p in D["died"] and p not in R and _within_window(p)}
k = len(opr_neo & comp)

print("开腹相关新生儿窗口内竞争事件（确诊死亡）%d/%d 例" % (k, n2))
print("敏感性分析：假设其中若干例本应发生十二指肠梗阻再手术而未被观测到")
print()
for add in (0, 1, 2, 3, k):
    tbl = [[x_lap, n1 - x_lap], [add, n2 - add]]
    pv = stats.fisher_exact(tbl)[1]
    print("  假设其中 %2d 例本会发生 -> %d/%d vs %d/%d, Fisher p = %.4f"
          % (add, x_lap, n1, add, n2, pv))
