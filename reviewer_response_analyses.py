# -*- coding: utf-8 -*-
"""回应模拟审稿人 2 的三项必做分析（均用现有数据，不新增采集）：
  R2-M2  限制在 132 例共识裁定子样本内重算（该池 = 全部再手术 + 22% 随机非再手术，
         结构等同病例对照抽样，故 OR 可估、率不可估）
  R2-M3  新生儿层十二指肠梗阻的正式竞争风险分析（Aalen–Johansen CIF + Gray 检验），
         并给出竞争事件的发生时点与"按暴露时间折算的期望漏检数"
  R2-M6  E-value（未测混杂容忍度）
  附带    R2-M4 新生儿层风险差 + Newcombe 区间 + NNH；R1-M4 十二指肠信号的年代分层
输出：reviewer_response_out.txt
"""
import io, sys, math, random
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import openpyxl
import numpy as np
from scipy.stats import fisher_exact, norm
import _dataprep as D

OUT = []
def P(s=""):
    print(s); OUT.append(str(s))

d = D.load()
coh = set(d["malrot"])
first = d["first"]
appr = {p: D.approach(first[p]) for p in coh}
LAPS = "腹腔镜完成"
adj = D.adjudicated()
ad = d["age_d"]
# 2026-07-28：竞争事件改为【电话随访确认的死亡】。旧口径 death|abandon 把随访后
# 证实存活的 4 例、失访 2 例也计为竞争事件，会高估被截断的风险时间。
COMP = d["died"] & coh
neo = {p for p in coh if p in d["neonate"]}

DUO = {p for p, v in adj.items() if p in coh and v["cause"] == "十二指肠持续梗阻"}
REOP = {p for p in adj if p in coh}


# ---------- 通用工具 ----------
def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n; den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den
    h = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return c - h, c + h


def newcombe(k1, n1, k2, n2, z=1.96):
    """两独立比例之差的 Newcombe（method 10）区间。"""
    l1, u1 = wilson(k1, n1, z); l2, u2 = wilson(k2, n2, z)
    p1, p2 = k1/n1, k2/n2
    lo = (p1-p2) - z*math.sqrt(l1*(1-l1)/n1 + u2*(1-u2)/n2)
    hi = (p1-p2) + z*math.sqrt(u1*(1-u1)/n1 + l2*(1-l2)/n2)
    return lo, hi


def orfmt(a, b, c, dd):
    """OR 与条件精确区间（用 fisher_exact 的 OR，区间用 scipy 的精确法）。"""
    from scipy.stats import fisher_exact as fe
    try:
        from scipy.stats.contingency import odds_ratio
        r = odds_ratio([[a, b], [c, dd]], kind="conditional")
        lo, hi = r.confidence_interval(0.95)
        return r.statistic, lo, hi, fe([[a, b], [c, dd]])[1]
    except Exception:
        return fe([[a, b], [c, dd]])[0], float("nan"), float("nan"), fe([[a, b], [c, dd]])[1]


P("=" * 78)
P("R2-M2  限制在 132 例共识裁定子样本内重算")
P("=" * 78)

wb = openpyxl.load_workbook("裁定表.xlsx", data_only=True)
wsB = wb["B_术式与严重度_池"]
hdr = [str(wsB.cell(1, c).value) for c in range(1, wsB.max_column + 1)]
i_pid = hdr.index("患者编号") + 1
i_con = hdr.index("共识_术式") + 1
pool = {}
for r in range(2, wsB.max_row + 1):
    pid = str(wsB.cell(r, i_pid).value).strip()
    con = wsB.cell(r, i_con).value
    if pid and con:
        pool[pid] = str(con).strip()

pool = {p: v for p, v in pool.items() if p in coh}
P(f"  池内可用 {len(pool)} 例（均在 {len(coh)} 例队列内）")
n_case = len({p for p in pool if p in REOP})
P(f"  其中再手术 {n_case} 例、非再手术 {len(pool)-n_case} 例")
P(f"  抽样结构：全部（当时的）再手术 + 非再手术随机抽样 → 等同病例对照，OR 可估、率不可估")

# 算法 vs 共识 的错分
mis = [(p, appr[p], pool[p]) for p in pool if appr[p] != pool[p]]
P(f"\n  算法赋值 vs 盲法共识：不一致 {len(mis)}/{len(pool)}（{len(mis)/len(pool)*100:.1f}%）")
from collections import Counter
P("  不一致去向：" + "; ".join(f"算法{a}→共识{c}: {n}" for (a, c), n in Counter((a, c) for _, a, c in mis).items()))

def lap_or(expo, keys, outcome):
    a = sum(1 for p in keys if expo[p] == LAPS and p in outcome)
    b = sum(1 for p in keys if expo[p] == LAPS and p not in outcome)
    c = sum(1 for p in keys if expo[p] != LAPS and p in outcome)
    e = sum(1 for p in keys if expo[p] != LAPS and p not in outcome)
    return a, b, c, e

for label, outcome in (("任何非计划再手术", REOP), ("十二指肠持续梗阻", DUO)):
    P(f"\n  —— {label} ——")
    for tag, expo in (("算法暴露（池内同样 132 例）", appr), ("共识暴露（盲法人工）", pool)):
        a, b, c, e = lap_or(expo, pool.keys(), outcome)
        orv, lo, hi, pv = orfmt(a, b, c, e)
        P(f"    {tag:<26} lap {a}/{a+b}  open-rel {c}/{c+e}   "
          f"OR {orv:.2f} ({lo:.2f}–{hi:.2f})  p={pv:.3f}")
    # 新生儿层
    kn = [p for p in pool if p in neo]
    a, b, c, e = lap_or(pool, kn, outcome)
    orv, lo, hi, pv = orfmt(a, b, c, e)
    P(f"    共识暴露·新生儿层 (n={len(kn)})     lap {a}/{a+b}  open-rel {c}/{c+e}   p={pv:.3f}")

P(f"\n  全队列（算法暴露，{len(coh)} 例）对照值：")
for label, outcome in (("任何非计划再手术", REOP), ("十二指肠持续梗阻", DUO)):
    a, b, c, e = lap_or(appr, coh, outcome)
    orv, lo, hi, pv = orfmt(a, b, c, e)
    P(f"    {label:<10} lap {a}/{a+b}  open-rel {c}/{c+e}   OR {orv:.2f} ({lo:.2f}–{hi:.2f})  p={pv:.4f}")


P("\n" + "=" * 78)
P("R2-M3  新生儿层十二指肠梗阻的正式竞争风险分析")
P("=" * 78)

# 事件时间：再手术间隔（天）；竞争事件时间用末次出院日 − 索引手术日
def reop_gap(p):
    return adj[p]["gap"] if p in adj else None

def comp_time(p):
    dis = d["last_dis"].get(p); idx = first[p]["d"]
    if dis and idx:
        t = (dis - idx).days
        return t if 0 <= t <= 42 else None
    return None

def build(arm_keys):
    """返回 (time, status) ；status 1=十二指肠再手术 2=其他原因再手术 3=死亡/放弃 0=删失"""
    rows = []
    for p in arm_keys:
        t_r = reop_gap(p)
        if t_r is not None and t_r <= 42:
            rows.append((t_r, 1 if p in DUO else 2))
            continue
        if p in COMP:
            tc = comp_time(p)
            rows.append((tc if tc is not None else 42, 3))
            continue
        rows.append((42, 0))
    return rows

nl = [p for p in neo if appr[p] == LAPS]
no_ = [p for p in neo if appr[p] != LAPS]
RL, RO = build(nl), build(no_)

def aj_cif(rows, cause=1, tmax=42):
    """Aalen–Johansen 累积发生率（单臂）。"""
    n = len(rows)
    ts = sorted({t for t, s in rows if s > 0})
    S = 1.0; cif = 0.0; curve = []
    for t in ts:
        at_risk = sum(1 for tt, ss in rows if tt >= t)
        d_c = sum(1 for tt, ss in rows if tt == t and ss == cause)
        d_all = sum(1 for tt, ss in rows if tt == t and ss > 0)
        if at_risk == 0: break
        cif += S * d_c / at_risk
        S *= (1 - d_all / at_risk)
        curve.append((t, cif))
    return cif, curve

cl, _ = aj_cif(RL); co, _ = aj_cif(RO)
P(f"  腹腔镜新生儿 n={len(nl)}  42 天十二指肠再手术 AJ 累积发生率 = {cl*100:.2f}%")
P(f"  开腹相关新生儿 n={len(no_)}  同上                        = {co*100:.2f}%")
naive_l = sum(1 for p in nl if p in DUO)/len(nl)
P(f"  （朴素比例 {naive_l*100:.2f}% vs 0.00%；AJ 与朴素的差异反映竞争事件移走的风险集）")

# Gray 检验（k=2）：对子分布风险的加权对数秩型统计量
def gray_test(rowsA, rowsB, cause=1):
    allr = [(t, s, 0) for t, s in rowsA] + [(t, s, 1) for t, s in rowsB]
    ts = sorted({t for t, s, g in allr if s == cause})
    # 子分布风险集：已发生竞争事件者仍留在风险集中（权重按删失分布，这里无随机删失，权重=1）
    U = 0.0; V = 0.0
    for t in ts:
        # 子分布风险集 = 未发生任何事件者 + 已发生竞争事件者
        def sub_at_risk(rows):
            return sum(1 for tt, ss in rows if tt >= t or (tt < t and ss not in (0, cause)))
        r1, r0 = sub_at_risk(rowsB), sub_at_risk(rowsA)
        d1 = sum(1 for tt, ss in rowsB if tt == t and ss == cause)
        d0 = sum(1 for tt, ss in rowsA if tt == t and ss == cause)
        r, dd = r0 + r1, d0 + d1
        if r < 2 or dd == 0: continue
        U += d0 - dd * r0 / r
        V += dd * (r0/r) * (1 - r0/r) * (r - dd) / (r - 1) if r > 1 else 0
    if V <= 0: return float("nan"), float("nan")
    z = U / math.sqrt(V)
    return z*z, 2*(1 - norm.cdf(abs(z)))

chi, pg = gray_test(RL, RO)
P(f"  Gray 检验（子分布风险，2 组）：χ²={chi:.3f}, p={pg:.4f}")
a_ = sum(1 for p in nl if p in DUO)
P(f"  对照：Fisher 精确检验 {a_}/{len(nl)} vs 0/{len(no_)}  p="
  f"{fisher_exact([[a_, len(nl)-a_],[0, len(no_)]])[1]:.4f}")

tc = sorted(t for t, s in RO if s == 3)
P("\n  —— %d 例竞争事件的发生时点（开腹相关新生儿）——" % len(tc))
P(f"  n={len(tc)}  中位 {int(np.median(tc))} 天  IQR {int(np.percentile(tc,25))}–{int(np.percentile(tc,75))}  范围 {min(tc)}–{max(tc)}")
bins = [(0,3),(4,7),(8,14),(15,21),(22,42)]
P("  分箱：" + "; ".join(f"{a}-{b}d: {sum(1 for t in tc if a<=t<=b)}" for a,b in bins))

# 按"暴露时间折算"的期望漏检数：以腹腔镜臂十二指肠再手术的日风险为基准
lap_events = [t for t, s in RL if s == 1]
P(f"  腹腔镜臂 {len(lap_events)} 例十二指肠再手术发生于第 {sorted(lap_events)} 天")
# 每例竞争事件个体在其删失前"本应经历"的风险，用腹腔镜臂 AJ 曲线在该时点的值近似
_, curve_l = aj_cif(RL)
def cif_at(t):
    v = 0.0
    for tt, c in curve_l:
        if tt <= t: v = c
    return v
exp_missed = sum(cl - cif_at(t) for t in tc)
P(f"  若这 {len(tc)} 例携带腹腔镜臂的风险，其被竞争事件截断后**未观测到**的期望例数 = {exp_missed:.2f}")
P(f"  （对照：不考虑时点、按整体 4.2% 直接折算 = {len(tc)*naive_l:.2f} 例）")
for add in (0, 1, 2):
    P(f"    若实际漏检 {add} 例 → {a_}/{len(nl)} vs {add}/{len(no_)}, "
      f"Fisher p={fisher_exact([[a_, len(nl)-a_],[add, len(no_)-add]])[1]:.4f}")


P("\n" + "=" * 78)
P("R2-M4  新生儿层风险差、Newcombe 区间与 NNH")
P("=" * 78)
k1, n1, k2, n2 = a_, len(nl), 0, len(no_)
rd = k1/n1 - k2/n2
lo, hi = newcombe(k1, n1, k2, n2)
P(f"  风险差 = {rd*100:.2f} 个百分点（Newcombe 95% CI {lo*100:+.2f} 到 {hi*100:+.2f}）")
P(f"  NNH = 1/RD = {1/rd:.1f}（区间上下界对应 {1/hi:.0f} 到 {'∞' if lo<=0 else '%.0f'%(1/lo)}）")
P(f"  Wilson 95% CI(腹腔镜率) = {wilson(k1,n1)[0]*100:.2f}–{wilson(k1,n1)[1]*100:.2f}%")


P("\n" + "=" * 78)
P("R2-M6  E-value（未测混杂容忍度）")
P("=" * 78)
def evalue(rr):
    return rr + math.sqrt(rr * (rr - 1)) if rr >= 1 else (1/rr) + math.sqrt((1/rr)*((1/rr)-1))

# 下界一律就地算，勿写死：2026-07-28 曾写死 1.41（实为 1.38），E-value 因此偏大 0.07
from scipy.stats.contingency import odds_ratio as _or
_neo_lo = _or([[a_, len(nl) - a_], [0, len(no_)]], kind="conditional").confidence_interval(0.95)[0]
P("  新生儿层：点估计 OR 不可估（零格），故点估计的 E-value 无定义。")
P(f"  对精确区间下界 {_neo_lo:.2f}（罕见结局下 OR≈RR）：E-value = {evalue(_neo_lo):.2f}")
P(f"    → 未测混杂需与暴露、结局各自的 RR ≥ {evalue(_neo_lo):.2f} 才能把下界推回 1")
_duo_lo = _or([[len(DUO & set(p for p in coh if appr[p] == LAPS)),
                sum(1 for p in coh if appr[p] == LAPS) - len(DUO & set(p for p in coh if appr[p] == LAPS))],
               [0, sum(1 for p in coh if appr[p] != LAPS)]],
              kind="conditional").confidence_interval(0.95)[0]
P(f"  全队列十二指肠：开腹相关零事件 → 点估计与 MH 均不可估，E-value 对点估计无定义；")
P(f"    对精确区间下界 {_duo_lo:.2f}：E-value = {evalue(_duo_lo):.2f}")


P("\n" + "=" * 78)
P("R1-M4  十二指肠信号的年代分层（学习曲线替代解释）")
P("=" * 78)
yr = {p: first[p]["d"].year for p in coh if first[p]["d"]}
med = int(np.median([yr[p] for p in coh if p in yr]))
P(f"  队列索引手术年份中位数 = {med}")
for band, keys in (("全队列", coh), ("新生儿", neo)):
    for era, sel in (("早期(≤中位)", lambda p: yr.get(p, 9999) <= med),
                     ("晚期(>中位)", lambda p: yr.get(p, 0) > med)):
        ks = [p for p in keys if sel(p) and appr[p] == LAPS]
        if not ks: continue
        k = sum(1 for p in ks if p in DUO)
        P(f"  {band:<6} 腹腔镜 {era:<11} {k}/{len(ks)} = {k/len(ks)*100:.2f}%  "
          f"(Wilson {wilson(k,len(ks))[0]*100:.1f}–{wilson(k,len(ks))[1]*100:.1f}%)")
# 3 例技术缺陷的年份需从机制核阅取，这里只报 6 例新生儿十二指肠梗阻的年份
P(f"  6 例新生儿十二指肠梗阻的索引手术年份：{sorted(yr[p] for p in DUO if p in neo)}")
P(f"  ≥1 岁十二指肠梗阻的索引手术年份：{sorted(yr[p] for p in DUO if p not in neo)}")

io.open("reviewer_response_out.txt", "w", encoding="utf-8").write("\n".join(OUT))
P("\n[已写出 reviewer_response_out.txt]")
