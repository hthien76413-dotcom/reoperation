# -*- coding: utf-8 -*-
"""参考文献机械核对：引用位置、编号连续性、首现顺序、引而未列/列而未引、组内升序。
只读，不改稿。"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"D:\全部肠旋转不良\③肠旋转不良术后再手术\JPS_manuscript_draft_v2.md"
txt = io.open(P, encoding="utf-8").read()
# 2026-07-27 起 References 已前置于 Tables，故不能再按"末尾"切；
# 取 ## References 到下一个顶级标题之间作为文献表，其余全部算正文（表注/图注里的引用要计入）。
m = re.search(r"(?ms)^## References\s*\n(.*?)(?=^## |\Z)", txt)
if not m:
    raise SystemExit("未找到 ## References 节")
refs = m.group(1)
body = txt[:m.start()] + txt[m.end():]

# 参考文献表
listed = {}
for m in re.finditer(r"^(\d+)\.\s+(.+)$", refs, re.M):
    listed[int(m.group(1))] = m.group(2).strip()

# 正文引用（含表注、图注）。排除形如 [1.5%] 之类：只认纯数字与逗号
cites = []          # (行号, 节, 原始标记, [编号...])
lines = body.split("\n")
sec = "(前置)"
for i, ln in enumerate(lines, 1):
    ms = re.match(r"^#{1,3}\s+(.+)$", ln)
    if ms: sec = ms.group(1).strip()
    if ln.startswith("- **Figure"): sec = "Figure legends"
    if ln.startswith("**Table"):    sec = ln[:40]
    for m in re.finditer(r"\[(\d+(?:\s*,\s*\d+)*)\]", ln):
        nums = [int(x) for x in m.group(1).replace(" ", "").split(",")]
        cites.append((i, sec, m.group(0), nums))

used = [n for _, _, _, ns in cites for n in ns]
uniq = sorted(set(used))

print("=== 1. 引而未列 / 列而未引 ===")
print("  引用编号 %d 个；文献表 %d 条" % (len(uniq), len(listed)))
print("  引而未列:", sorted(set(uniq) - set(listed)) or "无")
print("  列而未引:", sorted(set(listed) - set(uniq)) or "无")
print("  编号连续性:", "连续 1–%d" % max(listed) if sorted(listed) == list(range(1, max(listed)+1)) else "★跳号")

print("\n=== 2. 首现顺序（应为 1,2,3… 递增）===")
seen, order, bad = set(), [], []
for i, sec, raw, ns in cites:
    for n in ns:
        if n not in seen:
            seen.add(n); order.append((n, i, sec, raw))
exp = 1
for n, i, sec, raw in order:
    flag = "" if n == exp else "  ★首现顺序不符（期望 %d）" % exp
    if flag: bad.append((n, i, sec, raw, exp))
    print("  第%2d 个首现: [%2d]  行%-4d %-28s %s%s" % (exp, n, i, sec[:28], raw, flag))
    exp += 1

print("\n=== 3. 组内是否升序 ===")
for i, sec, raw, ns in cites:
    if ns != sorted(ns):
        print("  ★ 行%d %s  %s 非升序" % (i, sec, raw))
    if len(ns) != len(set(ns)):
        print("  ★ 行%d %s  %s 组内重复" % (i, sec, raw))
print("  （无输出即全部升序且无重复）")

print("\n=== 4. 每条文献的被引位置 ===")
where = {}
for i, sec, raw, ns in cites:
    for n in ns: where.setdefault(n, []).append((i, sec))
for n in sorted(listed):
    locs = where.get(n, [])
    first = listed[n][:70]
    print("  [%2d] %-72s 被引 %d 次: %s" % (n, first, len(locs),
          ", ".join("行%d/%s" % (i, s[:16]) for i, s in locs) or "★未被引"))

print("\n=== 5. 全部引用点清单（供逐条比对论断）===")
for i, sec, raw, ns in cites:
    ctx = lines[i-1]
    # 截取标记前 130 字符作为语境
    pos = ctx.find(raw)
    print("  行%-4d %-26s %-12s …%s" % (i, sec[:26], raw, ctx[max(0, pos-130):pos].strip()[-130:]))
