# -*- coding: utf-8 -*-
"""全量数字核对：从原始数据独立复算，与稿件逐项比对。

与 arith_audit.py 的分工：
  arith_audit.py 只查 "a/b (c%)" 形式的百分比、分母合法性、三处风险差。
  本脚本补足其查不到的部分：中位数/IQR/极差、P 值、精确置信区间、
  摘要-正文-表-图的跨文件一致性、以及"不同结局误用同一分母"。

原则：所有复核值一律现算，不从稿件读取；无法从数据复算的项显式标注。
"""
import io, re, sys, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from collections import Counter, defaultdict
from scipy.stats import fisher_exact
from scipy.stats.contingency import odds_ratio
import _dataprep as D

MS   = "JPS_manuscript_draft_v2.md"
SUPP = "Supplementary_Material.md"
ms   = io.open(MS, encoding="utf-8").read()
supp = io.open(SUPP, encoding="utf-8").read()

d    = D.load()
coh  = set(d["malrot"])
first= d["first"]
adj  = D.adjudicated()
ad   = d["age_d"]
L    = "腹腔镜完成"
ap   = {p: D.approach(first[p]) for p in coh}
R    = {p for p in adj if p in coh}
DUO  = {p for p in R if adj[p]["cause"] == "十二指肠持续梗阻"}

lap  = [p for p in coh if ap[p] == L]
opn  = [p for p in coh if ap[p] != L]
conv = [p for p in coh if ap[p] == "中转开腹"]
open_only = [p for p in coh if ap[p] == "开腹"]

def band(p):
    a = ad.get(p)
    return None if a is None else ("neo" if a < 28 else ("inf" if a < 365.25 else "big"))

def med_iqr(xs):
    xs = sorted(xs)
    n = len(xs)
    def q(f):
        # 与 numpy 默认 linear 插值一致
        i = f * (n - 1)
        lo, hi = int(math.floor(i)), int(math.ceil(i))
        return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)
    return q(0.5), q(0.25), q(0.75), xs[0], xs[-1]

def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den
    h = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return (c-h)*100, (c+h)*100

def fisher_or(k1, n1, k2, n2):
    tbl = [[k1, n1-k1], [k2, n2-k2]]
    p = fisher_exact(tbl)[1]
    r = odds_ratio(tbl, kind="conditional")
    lo, hi = r.confidence_interval(0.95)
    return r.statistic, lo, hi, p

ROWS = []
def chk(loc, quoted, recomputed, ok, note="", suggest=""):
    ROWS.append(dict(loc=loc, quoted=quoted, recomputed=recomputed,
                     ok=ok, note=note, suggest=suggest))

def has(pattern, text=None, flags=0):
    return re.search(pattern, text if text is not None else ms, flags) is not None

print("=" * 78)
print("全量数字核对  数据源：全部肠旋转不良数据.xlsx + 裁定表.xlsx")
print("=" * 78)

# ---------------------------------------------------------------- 1 队列与分组
print("\n【1】样本量与分组")
n_coh, n_lap, n_conv, n_open = len(coh), len(lap), len(conv), len(open_only)
n_opn = len(opn)
print(f"  队列 {n_coh}；腹腔镜完成 {n_lap}；中转 {n_conv}；开腹 {n_open}；开腹相关 {n_opn}")
print(f"  分组之和 {n_lap}+{n_conv}+{n_open} = {n_lap+n_conv+n_open}  vs 队列 {n_coh}  "
      f"→ {'一致' if n_lap+n_conv+n_open==n_coh else '★不一致'}")
print(f"  开腹相关 = 中转+开腹 = {n_conv+n_open}  vs {n_opn} → "
      f"{'一致' if n_conv+n_open==n_opn else '★不一致'}")
chk("§3.1/Table 1/Fig 1", f"450 / 255 / 53 / 142",
    f"{n_coh} / {n_lap} / {n_conv} / {n_open}",
    (n_coh, n_lap, n_conv, n_open) == (450, 255, 53, 142))

# ---------------------------------------------------------------- 2 年龄分层
print("\n【2】年龄分层人数")
tot_band = 0
band_counts = {}
for b, label in (("neo","Neonate <28d"), ("inf","28d–1y"), ("big","≥1y")):
    g  = [p for p in coh if band(p) == b]
    gl = [p for p in g if ap[p] == L]
    go = [p for p in g if ap[p] != L]
    band_counts[b] = (len(g), len(gl), len(go))
    tot_band += len(g)
    print(f"  {label:<14} 合计 {len(g):>3}  腹腔镜 {len(gl):>3}  开腹相关 {len(go):>3}")
print(f"  三层合计 {tot_band} vs 队列 {n_coh} → {'一致' if tot_band==n_coh else '★不一致'}")
chk("Table 1 年龄行", "305 / 61 / 84",
    f"{band_counts['neo'][0]} / {band_counts['inf'][0]} / {band_counts['big'][0]}",
    (band_counts['neo'][0], band_counts['inf'][0], band_counts['big'][0]) == (305, 61, 84))
chk("Table 3 分层分母", "142/163 · 42/19 · 71/13",
    f"{band_counts['neo'][1]}/{band_counts['neo'][2]} · "
    f"{band_counts['inf'][1]}/{band_counts['inf'][2]} · "
    f"{band_counts['big'][1]}/{band_counts['big'][2]}",
    (band_counts['neo'][1], band_counts['neo'][2],
     band_counts['inf'][1], band_counts['inf'][2],
     band_counts['big'][1], band_counts['big'][2]) == (142,163,42,19,71,13))

# ---------------------------------------------------------------- 3 性别
print("\n【3】性别")
male_all = sum(1 for p in coh if str(d["sex"].get(p,"")).startswith("男"))
male_lap = sum(1 for p in lap if str(d["sex"].get(p,"")).startswith("男"))
male_opn = sum(1 for p in opn if str(d["sex"].get(p,"")).startswith("男"))
print(f"  男性 合计 {male_all}/{n_coh} ({male_all/n_coh*100:.1f}%)  "
      f"腹腔镜 {male_lap}/{n_lap} ({male_lap/n_lap*100:.1f}%)  "
      f"开腹相关 {male_opn}/{n_opn} ({male_opn/n_opn*100:.1f}%)")
chk("Table 1 性别行", "344 (76.4) / 196 (76.9) / 148 (75.9)",
    f"{male_all} ({male_all/n_coh*100:.1f}) / {male_lap} ({male_lap/n_lap*100:.1f}) / "
    f"{male_opn} ({male_opn/n_opn*100:.1f})",
    (male_all, male_lap, male_opn) == (344, 196, 148))

# ---------------------------------------------------------------- 4 年龄中位数
print("\n【4】年龄中位数（月）")
def age_months(ps):
    xs = [ad[p]/30.4375 for p in ps if ad.get(p) is not None]
    return med_iqr(xs)
for nm, ps in (("Overall", coh), ("Laparoscopic", lap), ("Open-related", opn)):
    m, q1, q3, lo, hi = age_months(ps)
    print(f"  {nm:<14} median {m:.2f}  IQR {q1:.2f}–{q3:.2f}  range {lo:.2f}–{hi:.2f}")
mo_all = age_months(coh); mo_lap = age_months(lap); mo_opn = age_months(opn)
chk("Table 1 年龄行", "Overall 0.2 (0.1–2.0) · Lap 0.6 (0.2–22.0) · Open 0.1 (0.1–0.5)",
    f"Overall {mo_all[0]:.1f} ({mo_all[1]:.1f}–{mo_all[2]:.1f}) · "
    f"Lap {mo_lap[0]:.1f} ({mo_lap[1]:.1f}–{mo_lap[2]:.1f}) · "
    f"Open {mo_opn[0]:.1f} ({mo_opn[1]:.1f}–{mo_opn[2]:.1f})",
    None, note="需人工看下方复算值与表内是否逐位一致")

# ---------------------------------------------------------------- 5 结局与时间
print("\n【5】再手术结局与时间分布")
n_reop = len(R)
reop_lap = sum(1 for p in lap if p in R)
reop_conv= sum(1 for p in conv if p in R)
reop_open= sum(1 for p in open_only if p in R)
reop_opn = sum(1 for p in opn if p in R)
print(f"  再手术 {n_reop}/{n_coh} ({n_reop/n_coh*100:.1f}%)  Wilson {wilson(n_reop,n_coh)[0]:.1f}–{wilson(n_reop,n_coh)[1]:.1f}")
print(f"  腹腔镜 {reop_lap}/{n_lap} ({reop_lap/n_lap*100:.1f}%)  Wilson {wilson(reop_lap,n_lap)[0]:.1f}–{wilson(reop_lap,n_lap)[1]:.1f}")
print(f"  中转   {reop_conv}/{n_conv} ({reop_conv/n_conv*100:.1f}%)  Wilson {wilson(reop_conv,n_conv)[0]:.1f}–{wilson(reop_conv,n_conv)[1]:.1f}")
print(f"  开腹   {reop_open}/{n_open} ({reop_open/n_open*100:.1f}%)  Wilson {wilson(reop_open,n_open)[0]:.1f}–{wilson(reop_open,n_open)[1]:.1f}")
print(f"  开腹相关 {reop_opn}/{n_opn} ({reop_opn/n_opn*100:.1f}%)")
print(f"  分支合计 {reop_lap}+{reop_conv}+{reop_open} = {reop_lap+reop_conv+reop_open} vs {n_reop} → "
      f"{'一致' if reop_lap+reop_conv+reop_open==n_reop else '★不一致'}")

gaps = [adj[p]["gap"] for p in R if adj[p]["gap"] is not None]
gaps = [float(g) for g in gaps]
gm, gq1, gq3, glo, ghi = med_iqr(gaps)
in8_21 = sum(1 for g in gaps if 8 <= g <= 21)
bins = [sum(1 for g in gaps if lo <= g <= hi) for lo, hi in
        ((0,7),(8,14),(15,21),(22,30),(31,10**6))]
print(f"  间隔 n={len(gaps)}  median {gm}  IQR {gq1}–{gq3}  range {glo:.0f}–{ghi:.0f}")
print(f"  第 8–21 天 {in8_21}/{len(gaps)} = {in8_21/len(gaps)*100:.0f}%")
print(f"  分箱 0-7/8-14/15-21/22-30/>30 = {'/'.join(map(str,bins))}")
# Q3 精确值 19.25，稿件按四舍五入写 19；比较时对 Q1/Q3 取整后再比，避免假阳性
chk("§3.2 + Supp Table S3", "median 14.5, IQR 10–19, range 2–37, 24 (67%) on days 8–21",
    f"median {gm}, IQR {gq1:.2f}–{gq3:.2f}(→{round(gq1):.0f}–{round(gq3):.0f}), "
    f"range {glo:.0f}–{ghi:.0f}, {in8_21} ({in8_21/len(gaps)*100:.0f}%) on days 8–21",
    (gm, round(gq1), round(gq3), glo, ghi, in8_21) == (14.5, 10, 19, 2, 37, 24))
chk("Supp Table S3 分箱", "5 / 13 / 11 / 5 / 2", "/".join(map(str,bins)),
    bins == [5,13,11,5,2])

# ---------------------------------------------------------------- 6 病因分布
print("\n【6】病因分布（Table 2）")
cc = Counter(adj[p]["cause"] for p in R)
cc_lap = Counter(adj[p]["cause"] for p in R if ap[p] == L)
cc_opn = Counter(adj[p]["cause"] for p in R if ap[p] != L)
tot_cause = 0
for c in D.CAUSES6:
    n, nl, no = cc.get(c,0), cc_lap.get(c,0), cc_opn.get(c,0)
    tot_cause += n
    rl, ro = nl/n_lap*100, no/n_opn*100
    orv, lo, hi, p = fisher_or(nl, n_lap, no, n_opn)
    orstr = "NE" if (nl==0 or no==0) else f"{orv:.2f} ({lo:.2f}–{hi:.1f})"
    print(f"  {c:<18} {n:>2} ({n/n_reop*100:>4.1f}%)  lap {nl:>2} ({rl:.1f}%)  "
          f"open {no:>2} ({ro:.1f}%)  OR {orstr:<22} p={p:.4f}")
    print(f"      合计校验 {nl}+{no}={nl+no} vs {n} → {'ok' if nl+no==n else '★不一致'}")
print(f"  六类合计 {tot_cause} vs 再手术 {n_reop} → {'一致' if tot_cause==n_reop else '★不一致'}")

obstr = sum(cc.get(c,0) for c in ("十二指肠持续梗阻","粘连性肠梗阻","肠扭转复发"))
obstr_l = sum(cc_lap.get(c,0) for c in ("十二指肠持续梗阻","粘连性肠梗阻","肠扭转复发"))
obstr_o = sum(cc_opn.get(c,0) for c in ("十二指肠持续梗阻","粘连性肠梗阻","肠扭转复发"))
print(f"  梗阻类合计(1+3+5) {obstr} ({obstr/n_reop*100:.1f}%)  lap {obstr_l} ({obstr_l/n_lap*100:.1f}%)  "
      f"open {obstr_o} ({obstr_o/n_opn*100:.1f}%)")
chk("Table 2 梗阻类合计行", "19 (52.8%) · 7.1% vs 0.5%",
    f"{obstr} ({obstr/n_reop*100:.1f}%) · {obstr_l/n_lap*100:.1f}% vs {obstr_o/n_opn*100:.1f}%",
    obstr == 19)

# Holm 校正
print("\n  Holm 校正（六个病因别比较）")
raw = []
for c in D.CAUSES6:
    nl, no = cc_lap.get(c,0), cc_opn.get(c,0)
    raw.append((c, fisher_or(nl,n_lap,no,n_opn)[3]))
order = sorted(range(6), key=lambda i: raw[i][1])
holm = [0]*6
prev = 0
for rank, i in enumerate(order):
    v = min(1.0, max(prev, (6-rank) * raw[i][1]))
    holm[i] = v; prev = v
for (c, p), h in zip(raw, holm):
    print(f"    {c:<18} p={p:.4f}  Holm={h:.4f}")

# ---------------------------------------------------------------- 7 总体率比较
print("\n【7】总体再手术率比较（Table 4）")
orv, lo, hi, p = fisher_or(reop_lap, n_lap, reop_opn, n_opn)
print(f"  Crude lap vs open-related  OR {orv:.2f} ({lo:.2f}–{hi:.2f})  p={p:.4f}")
chk("§3.4 + Table 4", "OR 1.58, exact 95% CI 0.74–3.6, p=0.22 / 0.224",
    f"OR {orv:.2f} ({lo:.2f}–{hi:.2f}) p={p:.4f}",
    abs(orv-1.58)<0.01 and abs(p-0.224)<0.001)
orc, loc_, hic, pc = fisher_or(reop_conv, n_conv, reop_open, n_open)
print(f"  中转 vs 纯开腹             OR {orc:.2f} ({loc_:.2f}–{hic:.2f})  p={pc:.4f}")
chk("Table 4 异质性行", "11.3% vs 4.2%, 0.73–11.3, p=0.091",
    f"{reop_conv/n_conv*100:.1f}% vs {reop_open/n_open*100:.1f}%, "
    f"{loc_:.2f}–{hic:.1f}, p={pc:.4f}",
    abs(pc-0.091)<0.002)
itt_l = reop_lap + reop_conv; itt_nl = n_lap + n_conv
oi, loi, hii, pi = fisher_or(itt_l, itt_nl, reop_open, n_open)
print(f"  ITT（中转并入腹腔镜）      OR {oi:.2f} ({loi:.2f}–{hii:.2f})  p={pi:.4f}")
chk("Table 4 ITT 行", "OR 2.45, 0.97–7.4, p=0.060",
    f"OR {oi:.2f} ({loi:.2f}–{hii:.1f}) p={pi:.4f}",
    abs(oi-2.45)<0.01 and abs(pi-0.060)<0.002)

# ---------------------------------------------------------------- 8 十二指肠梗阻
print("\n【8】十二指肠持续梗阻")
duo_l = sum(1 for p in lap if p in DUO); duo_o = sum(1 for p in opn if p in DUO)
orv, lo, hi, p = fisher_or(duo_l, n_lap, duo_o, n_opn)
print(f"  全队列 {duo_l}/{n_lap} ({duo_l/n_lap*100:.1f}%) vs {duo_o}/{n_opn} ({duo_o/n_opn*100:.1f}%)  "
      f"p={p:.4f}  单侧下界 {lo:.2f}")
chk("Table 2 第1类 + §3.5", "12/255 4.7% vs 0/195 0%, NE (≥2.19), p=0.0016, Holm 0.010",
    f"{duo_l}/{n_lap} {duo_l/n_lap*100:.1f}% vs {duo_o}/{n_opn} {duo_o/n_opn*100:.1f}%, "
    f"lower {lo:.2f}, p={p:.4f}, Holm {holm[0]:.4f}",
    duo_l==12 and duo_o==0 and abs(p-0.0016)<0.0002)

print("\n  按年龄分层")
for b, label in (("neo","Neonate"), ("inf","28d–1y"), ("big","≥1y")):
    gl = [p for p in lap if band(p)==b]; go = [p for p in opn if band(p)==b]
    kl = sum(1 for p in gl if p in DUO); ko = sum(1 for p in go if p in DUO)
    if len(gl)==0 or len(go)==0: continue
    orv, lo, hi, pv = fisher_or(kl, len(gl), ko, len(go))
    lostr = f"{lo:.2f}" if kl>0 or ko>0 else "—"
    print(f"    {label:<10} {kl}/{len(gl)} ({kl/len(gl)*100:.1f}%) vs {ko}/{len(go)} "
          f"({ko/len(go)*100:.1f}%)  p={pv:.4f}  下界 {lostr}")
    # 任何再手术
    rl_ = sum(1 for p in gl if p in R); ro_ = sum(1 for p in go if p in R)
    o2, l2, h2, p2 = fisher_or(rl_, len(gl), ro_, len(go))
    o2s = "NE" if (rl_==0 or ro_==0) else f"{o2:.2f} ({l2:.2f}–{h2:.1f})"
    print(f"    {'':<10} any-reop {rl_}/{len(gl)} vs {ro_}/{len(go)}  OR {o2s}  p={p2:.4f}")

# 新生儿层 Holm（三层）
# 族大小必须是 3（稿件把不可估的 28d–1y 层也计入，较保守）。
# 曾误写成 ×2 而得 0.0192，据此错判稿件的 0.029 为不符——族大小要跟稿件口径一致。
neo_gl = [p for p in lap if band(p)=="neo"]; neo_go = [p for p in opn if band(p)=="neo"]
strata_p = []
for b in ("neo", "inf", "big"):
    gl = [p for p in lap if band(p)==b]; go = [p for p in opn if band(p)==b]
    strata_p.append(fisher_or(sum(1 for p in gl if p in DUO), len(gl),
                              sum(1 for p in go if p in DUO), len(go))[3])
order3 = sorted(range(3), key=lambda i: strata_p[i])
holm3 = [0]*3; prev = 0
for rank, i in enumerate(order3):
    v = min(1.0, max(prev, (3-rank) * strata_p[i])); holm3[i] = v; prev = v
print(f"\n  Holm across 3 strata（十二指肠）: neonate raw {strata_p[0]:.4f} → adj {holm3[0]:.4f}")
chk("Table 3 脚注", "neonatal Holm adjusted p=0.029",
    f"{holm3[0]:.4f}", abs(holm3[0]-0.029)<0.002)

# ---------------------------------------------------------------- 9 严重度/竞争事件
print("\n【9】新生儿层严重度与竞争事件（§3.6）")
nec_l = sum(1 for p in neo_gl if D.has_necrosis(first[p]))
nec_o = sum(1 for p in neo_go if D.has_necrosis(first[p]))
print(f"  索引坏死 lap {nec_l}/{len(neo_gl)} ({nec_l/len(neo_gl)*100:.1f}%)  "
      f"open {nec_o}/{len(neo_go)} ({nec_o/len(neo_go)*100:.1f}%)")
# 2026-07-29 订正：稿件原写 39/163 (23.9%)，分子 39 是 466 队列时代（39/166）的残留。
# 该错误能骗过 arith_audit.py，因为分子/分母/百分比三者自洽（39/163 恰为 23.9%），
# 只有回到原始数据重数才发现。现稿件与复算同为 38。
chk("§3.6 坏死", "38/163 (23.3%) vs 5/142 (3.5%)",
    f"{nec_o}/{len(neo_go)} ({nec_o/len(neo_go)*100:.1f}%) vs "
    f"{nec_l}/{len(neo_gl)} ({nec_l/len(neo_gl)*100:.1f}%)",
    (nec_o, nec_l) == (38, 5))

died = d["died"]
death_neo_o = sum(1 for p in neo_go if p in died and p not in R)
death_neo_l = sum(1 for p in neo_gl if p in died and p not in R)
print(f"  窗口内死亡且未再手术 open {death_neo_o}/{len(neo_go)} "
      f"({death_neo_o/len(neo_go)*100:.1f}%)  lap {death_neo_l}/{len(neo_gl)}")
chk("§3.6 死亡", "16/163 (9.8%) versus none of 142",
    f"{death_neo_o}/{len(neo_go)} ({death_neo_o/len(neo_go)*100:.1f}%) vs {death_neo_l}/{len(neo_gl)}",
    death_neo_o == 16 and death_neo_l == 0)

death_all_o = sum(1 for p in opn if p in died and p not in R)
death_all_l = sum(1 for p in lap if p in died and p not in R)
print(f"  全队列窗口内死亡 open {death_all_o}  lap {death_all_l}")
chk("§3.5 + Table 4 脚注", "16 deaths versus none after laparoscopic completion",
    f"open {death_all_o} vs lap {death_all_l}",
    death_all_o == 16 and death_all_l == 0)

# ---------------------------------------------------------------- 10 机制
print("\n【10】机制（§3.7 / Table 2 附注）")
print(f"  十二指肠梗阻 n={len(DUO)}（应为 12）→ {'ok' if len(DUO)==12 else '★'}")
duo_neo = [p for p in DUO if band(p)=="neo"]
duo_big = [p for p in DUO if band(p)=="big"]
print(f"  新生儿 {len(duo_neo)}  ≥1岁 {len(duo_big)}  合计 {len(duo_neo)+len(duo_big)}")
ages_duo = sorted(ad[p] for p in DUO)
print(f"  12 例年龄（天）: {[round(a,1) for a in ages_duo]}")
print(f"  新生儿段 {min(a for a in ages_duo if a<28):.0f}–{max(a for a in ages_duo if a<28):.0f} 天；"
      f"≥1岁段 {min(a for a in ages_duo if a>=365)/365.25:.1f}–{max(ages_duo)/365.25:.1f} 岁")
# 2026-07-29 订正：稿件原写 "3–11 days"，下界把 3.6525 截断成 3、上界把 10.9575 四舍五入
# 成 11，同一区间两端用了两套取整规则。现统一为四舍五入 → 4–11 days（正文、Figure 2
# 图注、Cover letter 三处）。注意年龄源自「年龄(岁)」两位小数，粒度 0.01 岁 = 3.65 天。
chk("§3.6 + Fig 2A", "six at 4–11 days and six at 6.6–13.1 years",
    f"{len(duo_neo)} at {round(min(a for a in ages_duo if a<28))}–"
    f"{round(max(a for a in ages_duo if a<28))} d, {len(duo_big)} at "
    f"{min(a for a in ages_duo if a>=365)/365.25:.1f}–{max(ages_duo)/365.25:.1f} y",
    len(duo_neo)==6 and len(duo_big)==6
    and round(min(a for a in ages_duo if a<28))==4
    and round(max(a for a in ages_duo if a<28))==11)

# ---------------------------------------------------------------- 11 摘要 vs 正文
print("\n【11】摘要 / 正文 / 表 / 图 一致性（文本比对）")
def find_all(pat, text=ms):
    return re.findall(pat, text)

pairs = [
    ("队列 450",           r"450 children",       ms),
    ("再手术 36/450 8.0%", r"36/450 \(8\.0%",     ms),
    ("十二指肠 12/36",      r"12/36",              ms),
    ("12/255 4.7%",        r"12/255 \(4\.7%",     ms),
    ("6/142 4.2%",         r"6/142",              ms),
    ("0/163",              r"0/163",              ms),
    ("RD 4.2 CI 1.0–8.9",  r"1\.0[–-]8\.9|1\.0 to 8\.9", ms),
    ("RD 4.7 CI 1.9–8.0",  r"1\.9 to 8\.0",       ms),
    ("RD 3.3 CI −2.0–8.2", r"−2\.0 to \+8\.2",    ms),
]
for nm, pat, txt in pairs:
    print(f"  {nm:<22} 出现 {len(find_all(pat, txt))} 次")

# 摘要段内数字
abs_txt = ms[ms.find("## Structured Abstract"): ms.find("## 1. Introduction")]
print("\n  摘要内关键数字：")
for pat in [r"450 children", r"36/450 \(8\.0%\)", r"12/36", r"9\.4% vs\. 6\.2%",
            r"12/255 \(4\.7%\)", r"6/142 vs\. 0/163", r"4\.2% \(95% CI 1\.0[–-]8\.9",
            r"\+3\.3%", r"−2\.0 to \+8\.2", r"Holm p=0\.010", r"8\.5%",
            r"median 14\.5, IQR 10[–-]19", r"67%"]:
    print(f"    {pat:<40} {'✓' if re.search(pat, abs_txt) else '—'}")

# ---------------------------------------------------------------- 12 分母误用
print("\n【12】分母误用检查")
den_used = Counter(int(m.group(2)) for m in
                   re.finditer(r"(\d+)\s*/\s*(\d+)", ms))
legit_den = {n_coh, n_lap, n_opn, n_open, n_conv, n_reop,
             band_counts['neo'][0], band_counts['neo'][1], band_counts['neo'][2],
             band_counts['inf'][0], band_counts['inf'][1], band_counts['inf'][2],
             band_counts['big'][0], band_counts['big'][1], band_counts['big'][2],
             132, 124, 52, 53, 19, 12, 20, 430, 468, 260, 208, 499, 226, 161}
odd = {k: v for k, v in den_used.items() if k not in legit_den}
print(f"  正文出现的分母共 {len(den_used)} 种；不在已知合法集合的：")
for k, v in sorted(odd.items()):
    print(f"    分母 {k}（{v} 次）— 需人工判断")

# ---------------------------------------------------------------- 汇总
print("\n" + "=" * 78)
print("自动判定汇总")
print("=" * 78)
for r in ROWS:
    mark = "ok  " if r["ok"] is True else ("★FAIL" if r["ok"] is False else "note")
    print(f"[{mark}] {r['loc']}")
    print(f"        稿件: {r['quoted']}")
    print(f"        复算: {r['recomputed']}")
    if r["note"]: print(f"        备注: {r['note']}")
fails = [r for r in ROWS if r["ok"] is False]
print(f"\n自动判定 {len(ROWS)} 项，其中不一致 {len(fails)} 项")
