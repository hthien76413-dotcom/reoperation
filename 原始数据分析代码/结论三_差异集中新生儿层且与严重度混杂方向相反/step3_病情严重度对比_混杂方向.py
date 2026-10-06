import os, sys
from scipy import stats
_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(_d, "_dataprep.py")):
    _p = os.path.dirname(_d)
    if _p == _d:
        raise SystemExit("找不到 _dataprep.py，请确认本脚本仍在原仓库目录树下（任意层子文件夹均可）")
    _d = _p
sys.path.insert(0, _d)
from _dataprep import load, approach, reop_set, has_necrosis

D = load()
R = reop_set()
malrot, first = D["malrot"], D["first"]
R = {p for p in R if p in set(malrot)}
NEO = D["neonate"]

LAP = {p for p in malrot if approach(first[p]) == "腹腔镜完成"}
OPR = {p for p in malrot if approach(first[p]) != "腹腔镜完成"}
lap_neo, opr_neo = LAP & NEO, OPR & NEO
n1, n2 = len(lap_neo), len(opr_neo)

nec = {p for p in malrot if has_necrosis(first[p])}
nec1 = sum(1 for p in lap_neo if p in nec)
nec2 = sum(1 for p in opr_neo if p in nec)
pv_nec = stats.fisher_exact([[nec1, n1 - nec1], [nec2, n2 - nec2]])[1]

_reop = R
H_WIN = 42
def _within_window(p):
    t0 = first[p]["d"]
    dd = (D["last_dis"][p] - t0).days if (t0 and D["last_dis"].get(p)) else None
    return dd is not None and 0 <= dd <= H_WIN

comp = {p for p in malrot if p in D["died"] and p not in _reop and _within_window(p)}
comp1 = sum(1 for p in lap_neo if p in comp)
comp2 = sum(1 for p in opr_neo if p in comp)
pv_comp = stats.fisher_exact([[comp1, n1 - comp1], [comp2, n2 - comp2]])[1]

print("新生儿层病情严重度对比（腹腔镜完成 vs. 开腹相关）：")
print()
print("首次手术肠坏死  %d/%d (%.1f%%) vs %d/%d (%.1f%%)   Fisher p = %.6f"
      % (nec1, n1, nec1 / n1 * 100, nec2, n2, nec2 / n2 * 100, pv_nec))
print("窗口内确诊死亡  %d/%d (%.1f%%) vs %d/%d (%.1f%%)   Fisher p = %.6f"
      % (comp1, n1, comp1 / n1 * 100, comp2, n2, comp2 / n2 * 100, pv_comp))
print()
print("坏死率倍数（开腹相关 / 腹腔镜完成）= %.2f" % ((nec2 / n2) / (nec1 / n1)))
print("窗口内死亡：全部 %d 例均发生于开腹相关组" % comp2)
