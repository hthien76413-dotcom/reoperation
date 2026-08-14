# -*- coding: utf-8 -*-
"""把 stratified_analysis.py 生成的 Table 1/2/3/4 替换进主稿的 ## Tables 节。

逐表按 "**Table N.**" 定位，替换该表的表体（markdown 表格行）。
Table 4 下方还有第二张表（"**Adjusted models for persistent duodenal obstruction**"），
以及它自己的脚注段落——2026-07-28 发现这两处从未被本脚本覆盖，导致队列由 466 改为 450 后，
主稿仍留着旧的 Firth OR（7.61/6.54/...）与旧脚注（p 0.03–0.08）。现一并处理。

注意：各表的**主脚注**（Table 1/2/3/4 表体正下方那段）是主稿手工维护的，本脚本不动，
改数后需人工核对——arith_audit.py 只查 a/b (c%) 形式，查不出脚注里的 OR/HR/p。
"""
import io, re

MS = r"D:\全部肠旋转不良\③肠旋转不良术后再手术\JPS_manuscript_draft_v2.md"
SRC = {1: "Table_baseline_v2.md", 2: "Table_cause_v2.md",
       3: "Table_stratified.md", 4: "Table_sensitivity_v2.md"}
ADJ_HDR = "**Adjusted models for persistent duodenal obstruction**"

t = io.open(MS, encoding="utf-8").read()

def grab(path, which=0):
    """取文件里第 which 个 markdown 表格（连续以 | 开头的行）。"""
    lines = io.open(path, encoding="utf-8").read().split("\n")
    blocks, cur = [], []
    for ln in lines:
        if ln.startswith("|"):
            cur.append(ln)
        elif cur:
            blocks.append("\n".join(cur)); cur = []
    if cur: blocks.append("\n".join(cur))
    return blocks[which] if which < len(blocks) else ""

for n, f in SRC.items():
    new = grab(f)
    if not new:
        print("★ %s 未取到表体" % f); continue
    # Table 1 的畸形行来自 anomaly_table.py，不在 stratified_analysis.py 的产物里。
    # 2026-07-27/28 已三次因本脚本整体替换表体而把它们丢掉（脚注却还在讨论这些行），
    # 故在此显式续接，不再依赖事后人工补插。
    if n == 1:
        extra = grab("Table1_anomaly_rows.md")
        if extra:
            new = new + "\n" + "\n".join(extra.split("\n")[2:])   # 去掉它自己的表头与分隔行
            print("  Table 1 已续接畸形行（%d 行）" % (len(extra.split("\n")) - 2))
        else:
            print("★ 未取到 Table1_anomaly_rows.md，Table 1 将缺畸形行")
    m = re.search(r"(\*\*Table %d\.\*\*[^\n]*\n\n)((?:\|[^\n]*\n)+)" % n, t)
    if not m:
        print("★ 主稿未定位 Table %d" % n); continue
    t = t[:m.start(2)] + new + "\n" + t[m.end(2):]
    print("Table %d 已替换（%d 行）" % (n, new.count("\n") + 1))

# ---- Table 4 的第二张表（校正模型）+ 其后的脚注段落 ----
adj_body = grab("Table_sensitivity_v2.md", which=1)
adj_note = io.open("Table_sensitivity_v2.md", encoding="utf-8").read().rsplit("|", 1)[-1].strip()
if adj_body and adj_note:
    m = re.search(re.escape(ADJ_HDR) + r"[^\n]*\n\n((?:\|[^\n]*\n)+)", t)
    if m:
        t = t[:m.start(1)] + adj_body + "\n" + t[m.end(1):]
        print("Table 4 校正模型表已替换（%d 行）" % (adj_body.count("\n") + 1))
        # 紧随其后的第一个非空段落即该表脚注，整段替换
        tail = t[m.start(1) + len(adj_body) + 1:]
        m2 = re.match(r"\n*([^\n]+)\n", tail)
        if m2 and m2.group(1).startswith("Adjustment for age"):
            off = m.start(1) + len(adj_body) + 1
            t = t[:off + m2.start(1)] + adj_note + t[off + m2.end(1):]
            print("Table 4 校正模型脚注已替换")
        else:
            print("★ 未定位校正模型脚注，请人工核对")
    else:
        print("★ 主稿未定位『校正模型』表")

io.open(MS, "w", encoding="utf-8").write(t)
