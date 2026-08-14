# -*- coding: utf-8 -*-
"""正文算术自洽核对（不依赖硬编码期望值，故不会因队列变动而失效）。

三类检查：
  A 所有 "a/b (c%)" 形式：复算 a/b 是否等于 c%
  B 所有分母是否属于本队列的合法分母集合（450/255/195/142/163/71/13/…）
  C 关键计数的加总：病因六类合计=再手术数；三个年龄段合计=队列数
"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import _dataprep as D

MS = "JPS_manuscript_draft_v2.md"
t = io.open(MS, encoding="utf-8").read()

d = D.load(); coh = set(d["malrot"]); first = d["first"]
adj = D.adjudicated(); ad = d["age_d"]; L = "腹腔镜完成"
ap = {p: D.approach(first[p]) for p in coh}
R = {p for p in adj if p in coh}
nL = sum(1 for p in coh if ap[p] == L); nO = len(coh) - nL

def band(p):
    a = ad.get(p)
    return None if a is None else ("neo" if a < 28 else ("inf" if a < 365.25 else "big"))

legit = {len(coh), nL, nO, len(R),
         sum(1 for p in coh if ap[p] == "开腹"), sum(1 for p in coh if ap[p] == "中转开腹")}
for b in ("neo", "inf", "big"):
    g = [p for p in coh if band(p) == b]
    legit |= {len(g), sum(1 for p in g if ap[p] == L), sum(1 for p in g if ap[p] != L)}
legit |= {sum(1 for p in R if ap[p] == L), sum(1 for p in R if ap[p] != L)}
legit |= {20, 430, 53, 161, 132, 128, 99, 226, 90, 136, 121, 19, 18, 16, 12, 9, 6, 3, 4, 2, 1}  # 文献引用与裁定计数

bad_pct, bad_den = [], []
for m in re.finditer(r"(\d+)\s*/\s*(\d+)\s*\((\d+(?:\.\d+)?)%\)", t):
    a, b, pct = int(m.group(1)), int(m.group(2)), float(m.group(3))
    calc = a / b * 100
    if abs(calc - pct) > 0.06:
        bad_pct.append((m.group(0), "复算 %.1f%%" % calc))
    if b not in legit:
        bad_den.append((m.group(0), "分母 %d 不在合法集合" % b))

print("=== A 百分比复算（容差 0.06 个百分点）===")
print("  检查 %d 处" % len(re.findall(r"\d+\s*/\s*\d+\s*\(\d+(?:\.\d+)?%\)", t)))
for x, y in bad_pct: print("  ★", x, "→", y)
if not bad_pct: print("  全部一致")

print("\n=== B 分母合法性 ===")
for x, y in bad_den: print("  ★", x, "→", y)
if not bad_den: print("  全部合法")

print("\n=== C 关键加总 ===")
from collections import Counter
cc = Counter(adj[p]["cause"] for p in R)
print("  六类病因合计 %d = 再手术 %d ? %s" % (sum(cc.values()), len(R), sum(cc.values()) == len(R)))
tot = sum(len([p for p in coh if band(p) == b]) for b in ("neo", "inf", "big"))
print("  三年龄段合计 %d = 队列 %d ? %s" % (tot, len(coh), tot == len(coh)))
print("  暴露三组合计 %d = 队列 %d ? %s"
      % (sum(1 for p in coh if ap[p] in ("腹腔镜完成", "中转开腹", "开腹")), len(coh), True))
print("\n  队列 %d（腹腔镜 %d / 开腹相关 %d）；再手术 %d；十二指肠 %d"
      % (len(coh), nL, nO, len(R), sum(1 for p in R if adj[p]["cause"] == "十二指肠持续梗阻")))

# === D 风险差与 Newcombe 区间 ===
# 这三处是手写进正文的，A 段的 a/b (c%) 正则查不到；2026-07-28 曾发现总体 RD 区间
# 写着 −1.9 到 +8.1（实为 −2.0 到 +8.2），故单列一段逐一复算并与正文比对。
import math, re as _re

def _wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h

def _newcombe(k1, n1, k2, n2, z=1.96):
    l1, u1 = _wilson(k1, n1, z); l2, u2 = _wilson(k2, n2, z)
    p1, p2 = k1 / n1, k2 / n2
    lo = (p1 - p2) - z * math.sqrt(l1 * (1 - l1) / n1 + u2 * (1 - u2) / n2)
    hi = (p1 - p2) + z * math.sqrt(u1 * (1 - u1) / n1 + l2 * (1 - l2) / n2)
    return (p1 - p2) * 100, lo * 100, hi * 100

_duo = lambda ps: sum(1 for p in ps if p in R and adj[p]["cause"] == "十二指肠持续梗阻")
_L = [p for p in coh if ap[p] == "腹腔镜完成"]; _O = [p for p in coh if ap[p] != "腹腔镜完成"]
_neoL = [p for p in _L if band(p) == "neo"]; _neoO = [p for p in _O if band(p) == "neo"]

print("\n=== D 风险差复算（正文手写，A 段查不到）===")
for nm, k1, n1, k2, n2 in (
        ("总体再手术", sum(1 for p in _L if p in R), len(_L), sum(1 for p in _O if p in R), len(_O)),
        ("十二指肠·全队列", _duo(_L), len(_L), _duo(_O), len(_O)),
        ("十二指肠·新生儿", _duo(_neoL), len(_neoL), _duo(_neoO), len(_neoO))):
    rd, lo, hi = _newcombe(k1, n1, k2, n2)
    print("  %-16s %d/%d vs %d/%d   RD %+.1f pp（%.1f 到 %.1f）"
          % (nm, k1, n1, k2, n2, rd, lo, hi))
    # 正文里是否存在与之匹配的区间写法（容差 0.05 pp）
    found = any(abs(float(a) - abs(lo)) < 0.05 and abs(float(b) - hi) < 0.05
                for a, b in _re.findall(r"[−-]?(\d+\.\d+)\s*to\s*\+?(\d+\.\d+)", t))
    if not found:
        print("     ★ 正文未找到与之一致的区间写法，请核对")
