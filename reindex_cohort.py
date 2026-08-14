# -*- coding: utf-8 -*-
"""按"索引手术 = 最早的一台【真正的】旋转不良手术"重建队列，替代原来的
"索引手术 = 最早的任意一台手术"。原规则在两个方向上都会出错：

  向内错（误纳入）：首台只是内镜/活检，或诊断栏写明"肠旋转不良术后"（既往已在
                  别处做过 Ladd，属现患而非新发）——共 10 例。
  向外错（误排除）：首台是诊断性活检/结肠镜，故未命中旋转不良关键词而被排除，
                  但其后确有真正的 Ladd 手术——共 2 例。

本脚本只重建纳入与暴露，不触碰任何结局裁定（结局名单仍以裁定表为唯一权威）。
"""
import io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import _dataprep as D

DIAG = ("活检", "活组织检查", "镜检查", "结肠镜", "胃镜")
THERAP = ("松解", "切除", "吻合", "成形", "修补", "造口", "复位", "探查",
          "引流", "还纳", "减压", "切开", "拉德", "Ladd", "ladd", "根治")
POST = ("术后", "手术的随诊", "手术后随诊")

def is_diag_only(o):
    sn = o["sname"] or ""
    return any(k in sn for k in DIAG) and not any(k in sn for k in THERAP)

def is_primary_ladd(o):
    """真正的初次旋转不良手术：命中关键词、不是纯诊断操作、诊断栏未写明'术后'。"""
    if not D.is_malrot(o):        return False
    if is_diag_only(o):           return False
    if any(k in (o["dx"] or "") for k in POST): return False
    return True

d = D.load()
ops, old_coh, old_first = d["ops"], set(d["malrot"]), d["first"]
FAR = datetime.datetime(2100, 1, 1)

new_first = {}
for p, v in ops.items():
    cand = sorted([o for o in v if is_primary_ladd(o)],
                  key=lambda x: x["d"] or FAR)
    if cand:
        new_first[p] = cand[0]
new_coh = set(new_first)

added   = sorted(new_coh - old_coh)
dropped = sorted(old_coh - new_coh)
reidx   = sorted(p for p in (new_coh & old_coh)
                 if new_first[p]["d"] != old_first[p]["d"])

print("原队列 %d → 新队列 %d" % (len(old_coh), len(new_coh)))
print("  新纳入（原被误排除）%d 例：" % len(added))
for p in added:
    print("    %-10s 原首台=%-22s → 索引改为 %s %s"
          % (p, (old_first[p]["sname"] or "")[:22] if p in old_first else "(不在库)",
             new_first[p]["d"].date(), D.approach(new_first[p])))
print("  剔除（首台非初次 Ladd 且全程无真 Ladd）%d 例" % len(dropped))
print("  索引手术改判（原首台被替换）%d 例：" % len(reidx))
for p in reidx:
    print("    %-10s %s %s → %s %s"
          % (p, old_first[p]["d"].date(), D.approach(old_first[p]),
             new_first[p]["d"].date(), D.approach(new_first[p])))

# 暴露分布对比
def dist(keys, f):
    from collections import Counter
    return Counter(D.approach(f[p]) for p in keys)
print("\n暴露分布  原:", dict(dist(old_coh, old_first)))
print("          新:", dict(dist(new_coh, new_first)))

# 结局仍以裁定表为准
adj = D.adjudicated()
R_old = {p for p in adj if p in old_coh}
R_new = {p for p in adj if p in new_coh}
print("\n再手术例数  原 %d  新 %d" % (len(R_old), len(R_new)))
if R_old ^ R_new:
    print("  ★ 差异病例:", sorted(R_old ^ R_new))

io.open("reindex_cohort_out.txt", "w", encoding="utf-8").write(
    "new_cohort=%d\nadded=%s\ndropped=%s\nreindexed=%s\n"
    % (len(new_coh), added, dropped, reidx))
