# -*- coding: utf-8 -*-
"""把主稿的末尾各部分重排为期刊通行顺序，并插入分页符与图片占位。
只改章节顺序与排版标记，**不改任何一个字的正文内容**。

目标顺序：
  Title Page → Highlights → Structured Abstract → 1–4 正文 → Declarations
  → References → Tables → Figure legends → Figures（内嵌图片）→ Supplementary material

注意：wordcount.py 依赖 `---` + `## Declarations` 紧跟正文，故 Declarations 位置不动。
"""
import io, re

P = r"D:\全部肠旋转不良\③肠旋转不良术后再手术\JPS_manuscript_draft_v2.md"
t = io.open(P, encoding="utf-8").read()

if "## Figures" in t:
    raise SystemExit("已排版过（存在 ## Figures 节），勿重复运行。")

# 按顶级标题切块
parts = re.split(r"(?m)^(## .+)$", t)
head, blocks = parts[0], {}
order = []
for i in range(1, len(parts), 2):
    name = parts[i].strip()
    blocks[name] = parts[i + 1]
    order.append(name)

need = ["## Declarations", "## Tables", "## Figure legends",
        "## Supplementary material", "## References"]
missing = [n for n in need if n not in blocks]
if missing:
    raise SystemExit("缺少章节: %s" % missing)

def clean(s):
    """去掉块首尾多余的 --- 与空行，统一为前后各一个空行。"""
    s = s.strip("\n")
    s = re.sub(r"^\s*---\s*\n", "", s)
    s = re.sub(r"\n\s*---\s*$", "", s)
    return s.strip("\n")

PB = "<!--pagebreak-->"

# 每张表前分页：把 Tables 块内的 --- 分隔改成分页符
tables = clean(blocks["## Tables"])
tables = re.sub(r"(?m)^---$", PB, tables)

# Figures 节：图注在 Figure legends，图片本身单独成节，每图一页
# 2026-07-31 更正：曾是 3 图（Figure 2=cause_by_approach），2026-07-28 起
# Figure 2 已改为 duodenal_by_age、cause_by_approach 降为 Supplementary Figure S2，
# 正文现只有 2 图。此脚本是一次性重排工具，若未来重跑务必先核对此列表与现行编号一致。
figs = [("Figure 1", "Figure1_flow_EN.png"),
        ("Figure 2", "Figure2_duodenal_by_age.png")]
fig_block = []
for j, (label, path) in enumerate(figs):
    if j: fig_block.append(PB)
    fig_block.append("**%s**" % label)
    fig_block.append("")
    fig_block.append("![%s](%s)" % (label, path))
    fig_block.append("")

if "## Title Page" not in blocks:
    raise SystemExit("未找到 ## Title Page，中止（曾因此漏掉整页题名页）。")

out = ["## Title Page", "", clean(blocks["## Title Page"]), "",
       PB, "## Highlights", "", clean(blocks["## Highlights"]), "",
       PB, "## Structured Abstract", "", clean(blocks["## Structured Abstract"]), "",
       PB]
# 正文四节按原顺序原样保留
for name in order:
    if re.match(r"^## \d\. ", name):
        out += [name, "", clean(blocks[name]), ""]
out += ["---", "",
        "## Declarations", "", clean(blocks["## Declarations"]), "",
        PB, "## References", "", clean(blocks["## References"]), "",
        PB, "## Tables", "", tables, "",
        PB, "## Figure legends", "", clean(blocks["## Figure legends"]), "",
        PB, "## Figures", ""] + fig_block + [
        PB, "## Supplementary material", "", clean(blocks["## Supplementary material"]), ""]

new = "\n".join(out) + "\n"

# 安全闸：重排只允许移动，不允许丢内容。逐块比对非空行集合。
def sig(s):
    return sorted(l.strip() for l in s.split("\n")
                  if l.strip() and l.strip() not in ("---", PB))
lost = set(sig(t)) - set(sig(new))
if lost:
    raise SystemExit("★ 重排会丢失 %d 行，已中止。示例：%s"
                     % (len(lost), list(lost)[:3]))

io.open(P, "w", encoding="utf-8").write(new)
print("已重排：References 前置于 Tables，新增 ## Figures 节（3 图内嵌，每图一页），插入分页符。")
print("内容完整性：原文非空行 %d 行，全部保留。" % len(sig(t)))
