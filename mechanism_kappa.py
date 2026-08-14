# -*- coding: utf-8 -*-
"""揭盲并计算机制核阅（A/B/C/D）的评者间一致性。

用法：待第二评者把《机制核阅_盲法_评者2.xlsx》的『评者2_机制』列填完后运行本脚本。
它会读入盲评本 + 答案键，按盲编号对齐两位评者的判读，输出 κ、观察符合率、
PABAK 与逐例分歧清单，并给出可直接写进 Methods 2.4 的一句话。

输出：mechanism_kappa_report.txt
"""
import io, math, sys
import openpyxl

BLIND = "机制核阅_盲法_评者2.xlsx"
KEY = "机制核阅_盲法_答案键.xlsx"
OUT = "mechanism_kappa_report.txt"

def s(v): return "" if v is None else str(v).strip().upper()

ws = openpyxl.load_workbook(BLIND, data_only=True)["2_盲法核阅"]
r2 = {}
for r in range(2, ws.max_row + 1):
    b = s(ws.cell(r, 1).value)
    if b: r2[b] = s(ws.cell(r, 4).value)

wk = openpyxl.load_workbook(KEY, data_only=True)["答案键_评分前勿开"]
key = {}
for r in range(2, wk.max_row + 1):
    b = s(wk.cell(r, 1).value)
    if b: key[b] = dict(sid=str(wk.cell(r, 2).value).strip(),
                        app=str(wk.cell(r, 3).value).strip(),
                        r1=s(wk.cell(r, 4).value))

blanks = [b for b in sorted(key) if not r2.get(b)]
if blanks:
    print("第二评者尚有 %d 例未填：%s" % (len(blanks), blanks))
    print("请填完《%s》的『评者2_机制』列后再运行。" % BLIND)
    sys.exit(0)

pairs = [(key[b]["r1"], r2[b]) for b in sorted(key)]
n = len(pairs)
cats = sorted({a for a, _ in pairs} | {b for _, b in pairs})
idx = {c: i for i, c in enumerate(cats)}
M = [[0] * len(cats) for _ in cats]
for a, b in pairs: M[idx[a]][idx[b]] += 1
agree = sum(M[i][i] for i in range(len(cats)))
po = agree / n
row = [sum(M[i]) / n for i in range(len(cats))]
col = [sum(M[i][j] for i in range(len(cats))) / n for j in range(len(cats))]
pe = sum(row[i] * col[i] for i in range(len(cats)))
if pe >= 1:
    kp = lo = hi = 1.0
else:
    kp = (po - pe) / (1 - pe)
    se = math.sqrt(max(po * (1 - po), 1e-12) / (n * (1 - pe) ** 2))
    lo, hi = kp - 1.96 * se, kp + 1.96 * se
k = max(len(cats), 2)
pabak = (k * po - 1) / (k - 1)

# 完全一致时 κ 的正态近似 SE 恰为 0，"95%CI 1.00–1.00" 是算法产物而非事实。
# 对 n=14 的完全一致，诚实的做法是给【观察符合率】的 Wilson 区间。
z = 1.96
den = 1 + z * z / n
ctr = (po + z * z / (2 * n)) / den
hlf = z * math.sqrt(po * (1 - po) / n + z * z / (4 * n * n)) / den
w_lo, w_hi = max(0.0, ctr - hlf), min(1.0, ctr + hlf)

L = ["十二指肠持续梗阻 机制核阅（A/B/C/D）—— 评者间一致性", "=" * 66,
     "n=%d，类别=%s" % (n, cats),
     "观察符合率 Po = %.1f%% (%d/%d)，Wilson 95%%CI %.1f%%–%.1f%%"
     % (po * 100, agree, n, w_lo * 100, w_hi * 100),
     "Cohen's κ = %.3f，pe=%.3f" % (kp, pe),
     ("  ⚠ 完全一致时 κ 的正态近似 SE=0，区间退化为 1.00–1.00，不可作为精度陈述；"
      "报观察符合率的 Wilson 区间。" if po >= 1 else
      "  95%%CI %.3f–%.3f" % (lo, hi)),
     "PABAK = %.3f  （类别数按 %d 计）" % (pabak, k), "",
     "混淆矩阵（行=评者1，列=评者2），顺序 %s：" % cats]
for i, c in enumerate(cats):
    L.append("  %s: %s" % (c, "  ".join("%s=%d" % (cats[j], M[i][j]) for j in range(len(cats)))))
dis = [(b, key[b]["sid"], key[b]["app"], key[b]["r1"], r2[b])
       for b in sorted(key) if key[b]["r1"] != r2[b]]
L += ["", "分歧 %d 例：" % len(dis)]
for b, sid, app, a1, a2 in dis:
    L.append("  %s  研究编号=%-10s 首台=%-9s 评者1=%s  评者2=%s" % (b, sid, app, a1, a2))

# 共识后的机制分布（分歧例暂标 ?，需两人讨论）
L += ["", "两人一致的机制分布：",
      "  " + str({c: sum(1 for a, b in pairs if a == b == c) for c in cats})]
ci_txt = ("the two readers agreed on all %d (100%%; Wilson 95%% CI %.1f–100%%), κ=1.00"
          % (n, w_lo * 100)) if po >= 1 else \
         ("agreement was κ=%.2f (95%% CI %.2f–%.2f; observed agreement %.1f%%, n=%d)"
          % (kp, lo, hi, po * 100, n))
L += ["", "可写进 Methods 2.4 的表述：",
      "  Mechanism was assigned independently by a second reviewer, blinded to index approach,",
      "  from operative narratives with all abdominal-access wording masked and case order",
      "  randomised; " + ci_txt + "."]

out = "\n".join(L)
io.open(OUT, "w", encoding="utf-8").write(out)
try: print(out)
except UnicodeEncodeError: print(out.encode("gbk", "replace").decode("gbk"))
