# -*- coding: utf-8 -*-
"""汇总索引手术资格裁定：一致性(κ/PABAK)、分歧清单、共识后的队列构成与主要结果。
只读裁定表与原始数据，不改稿。"""
import io, sys, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import openpyxl
from collections import Counter
import _dataprep as D

wb = openpyxl.load_workbook("pending_index_adjudication.xlsx", data_only=True)
key = {}
k = wb["答案键_评分前勿开"]
for r in range(2, k.max_row + 1):
    key[str(k.cell(r, 1).value).strip()] = (str(k.cell(r, 2).value).strip(),
                                            k.cell(r, 3).value)

def read(sheet):
    ws = wb[sheet]; out = {}
    for r in range(2, ws.max_row + 1):
        code = str(ws.cell(r, 1).value).strip()
        v = ws.cell(r, 7).value
        note = ws.cell(r, 8).value
        if v: out[code] = (str(v).strip().upper()[:1], (note or "").strip())
    return out

r1, r2 = read("评者1_裁定"), read("评者2_裁定")
codes = sorted(set(r1) & set(r2))
print("=== 1. 一致性 ===")
print("  完成 %d 例" % len(codes))
agree = sum(1 for c in codes if r1[c][0] == r2[c][0])
po = agree / len(codes)
cats = sorted({r1[c][0] for c in codes} | {r2[c][0] for c in codes})
n = len(codes)
pe = sum((sum(1 for c in codes if r1[c][0] == g) / n) *
         (sum(1 for c in codes if r2[c][0] == g) / n) for g in cats)
kappa = (po - pe) / (1 - pe) if pe < 1 else float("nan")
pabak = 2 * po - 1
se = math.sqrt(po * (1 - po) / n) / (1 - pe) if pe < 1 else float("nan")
print("  观察一致率 %.1f%% (%d/%d)" % (po * 100, agree, n))
print("  Cohen's κ = %.3f (95%% CI %.3f–%.3f)；PABAK = %.3f"
      % (kappa, kappa - 1.96 * se, kappa + 1.96 * se, pabak))
print("  评者1 判定分布:", dict(Counter(v[0] for v in r1.values())))
print("  评者2 判定分布:", dict(Counter(v[0] for v in r2.values())))

print("\n=== 2. 分歧清单（需协商定稿）===")
dis = [c for c in codes if r1[c][0] != r2[c][0]]
if not dis:
    print("  无分歧")
for c in dis:
    pid, cat = key[c]
    print("  %s (%s) 算法初判=%s | 评者1=%s | 评者2=%s"
          % (c, pid, cat, r1[c][0], r2[c][0]))
    if r1[c][1]: print("      评者1备注: %s" % r1[c][1][:70])
    if r2[c][1]: print("      评者2备注: %s" % r2[c][1][:70])

print("\n=== 3. 逐例结果（A=纳入；B/C/D=排除；E=待定）===")
verdict = {}
for c in codes:
    pid, cat = key[c]
    v = r1[c][0] if r1[c][0] == r2[c][0] else "?"
    verdict[pid] = v
    print("  %s %-10s %-22s 评者1=%s 评者2=%s  →%s"
          % (c, pid, cat, r1[c][0], r2[c][0], v))

io.open("index_verdict.txt", "w", encoding="utf-8").write(
    "\n".join("%s\t%s" % (p, v) for p, v in sorted(verdict.items())))
print("\n[已写出 index_verdict.txt]")
