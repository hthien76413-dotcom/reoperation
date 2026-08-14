# -*- coding: utf-8 -*-
"""为 14 例十二指肠持续梗阻的【机制核阅】制作第二评者盲法评分包。

背景（审稿意见 v2 第 12 条）：机制四分法（A 首台技术不彻底 / C 术后致密性粘连 /
B 内在病变 / D 不确定）此前由单人、非盲完成，却在 Discussion 里承担最重的论证
（"三例技术不彻底全是腹腔镜、全是新生儿"）。审稿人必然要求第二读者与一致性。
14 份记录，复核成本很低。

盲法设计：
  · 遮蔽再手术记录原文中一切可推断【首台入路】的措辞（腹腔镜/腔镜/镜下/Trocar/
    气腹/中转/开腹/剖腹 等），替换为「【入路已遮蔽】」；
  · 打乱顺序，只给盲编号 M01…M14，不给研究编号/住院号/年龄/术式；
  · 判读标准原样附上，评者只依据再手术所见判定机制。
  · 答案键（盲编号 ↔ 研究编号 ↔ 评者1 原判）单独写入另一个文件，评分前请勿打开。

输出：
  机制核阅_盲法_评者2.xlsx      —— 交给第二评者填写
  机制核阅_盲法_答案键.xlsx      —— 请勿在评分完成前打开
"""
import io, re, random, sys, os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from _dataprep import load, approach, reop_set, adjudicated

SRC_V3 = "十二指肠梗阻再手术_归因核阅v3.xlsx"
OUT_BLIND = "机制核阅_盲法_评者2.xlsx"
OUT_KEY = "机制核阅_盲法_答案键.xlsx"
SEED = 20260726                     # 固定种子，便于复现打乱顺序

D = load(); A = adjudicated(); R = reop_set()
first = D["first"]
DUO = {p for p in R if A[p]["cause"] == "十二指肠持续梗阻"}

# ---------------- 读取 v3 原文 ----------------
wb = openpyxl.load_workbook(SRC_V3, data_only=True)
ws = wb["手术经过全文_填归因"]
hdr = [str(ws.cell(1, c).value or "").strip() for c in range(1, ws.max_column + 1)]
i_sid = hdr.index("研究编号") + 1
i_name = [i for i, c in enumerate(hdr) if "第二台手术名称" in c][0] + 1
i_narr = [i for i, c in enumerate(hdr) if "手术经过" in c][0] + 1
i_att = [i for i, c in enumerate(hdr) if "归因" in c][0] + 1
i_quote = [i for i, c in enumerate(hdr) if "摘句" in c][0] + 1

rows = []
for r in range(2, ws.max_row + 1):
    sid = ws.cell(r, i_sid).value
    if sid is None: continue
    sid = str(sid).strip()
    if sid not in DUO: continue          # 只取现行六分类下仍属第 1 类的 14 例
    rows.append(dict(sid=sid,
                     name=str(ws.cell(r, i_name).value or "").strip(),
                     narr=str(ws.cell(r, i_narr).value or "").strip(),
                     r1=str(ws.cell(r, i_att).value or "").strip(),
                     quote=str(ws.cell(r, i_quote).value or "").strip()))
assert len(rows) == len(DUO), "取到 %d 例，应为 %d 例" % (len(rows), len(DUO))

# ---------------- 遮蔽入路措辞 ----------------
# 只遮蔽【腹腔入路】相关措辞。胃镜/结肠镜/内镜等诊断性内镜【不遮蔽】——它们承载
# 关键所见（如 M09 胃镜见水平部受压），且与首台是腹腔镜还是开腹无关。
MASK = ["腹腔镜", "腹腔鏡", "腔镜", "镜下", "目镜", "镜头",
        "Trocar", "trocar", "TROCAR", "Troca", "troca", "套管针", "穿刺套管",
        "气腹", "CO2人工", "CO₂人工", "人工气腹",
        "中转开腹", "中轉開腹", "转开腹", "中转", "开腹", "剖腹",
        "戳卡", "戳孔", "腹腔探查孔", "微创"]
TOKEN = "【入路已遮蔽】"

def mask(t):
    if not t: return ""
    out = t
    for k in sorted(MASK, key=len, reverse=True):
        out = out.replace(k, TOKEN)
    out = re.sub(r"(%s)+" % re.escape(TOKEN), TOKEN, out)   # 合并相邻遮蔽标记
    return out

for d in rows:
    d["name_m"] = mask(d["name"])
    d["narr_m"] = mask(d["narr"])

leak = [(d["sid"], k) for d in rows for k in MASK
        if k in d["narr_m"] or k in d["name_m"]]
assert not leak, "遮蔽不彻底：%s" % leak

random.Random(SEED).shuffle(rows)
for i, d in enumerate(rows, 1):
    d["blind"] = "M%02d" % i

# ---------------- 判读标准 ----------------
CRIT = []
try:
    wc = wb["判读标准"]
    for r in range(1, wc.max_row + 1):
        vals = [str(wc.cell(r, c).value or "").strip() for c in range(1, wc.max_column + 1)]
        if any(vals): CRIT.append(vals)
except KeyError:
    pass

# ---------------- 写盲评本 ----------------
HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="4A4A4A")
YFILL = PatternFill("solid", fgColor="FFF2CC")
WRAP = Alignment(wrap_text=True, vertical="top")

wbo = openpyxl.Workbook()
s0 = wbo.active; s0.title = "0_说明"
s0.column_dimensions["A"].width = 110
notes = [
    "十二指肠持续梗阻 —— 机制盲法核阅（第二评者）",
    "",
    "【任务】14 份再手术的手术经过原文，请为每一份判定梗阻机制，填在『评者2_机制』列。",
    "",
    "【为什么盲】本表已遮蔽原文中可推断【腹腔入路】的措辞（统一替换为「%s」)，" % TOKEN,
    "并打乱了顺序、隐去研究编号、住院号与年龄。请只依据再手术所见判读。",
    "  · 胃镜/结肠镜等诊断性内镜措辞【未遮蔽】——它们承载关键所见，且与首台入路无关。",
    "  · 切口长度、置管位置等描述可能仍隐约提示【本次再手术】怎么进的腹；那不是首台的入路，",
    "    请勿据此推断，也不要让它影响判断。A 与 C 的区分只看【所见】：肠管位置是否正确、",
    "    该离断的结构是否仍在、系膜根部是否仍窄。",
    "",
    "【类别】",
    "  A 首台 Ladd 技术不彻底：再探查发现本应在首台完成而未完成的步骤（残留/未离断的索带、",
    "     系膜根部仍狭窄、十二指肠仍成角未复位等），需有阳性证据。",
    "  B 内在十二指肠病变：术中或内镜直接证实的先天性腔内病变（隔膜、内在狭窄环）。",
    "  C 术后致密性十二指肠周围粘连：首台步骤已完成（肠管位置正确），梗阻源于新形成的粘连。",
    "  D 不确定：证据不足以区分 A 与 C。",
    "",
    "【关键区分点】看『肠管位置』：若小肠在右、结肠在左、十二指肠已复位，则倾向 C；",
    "  若发现本该离断的结构仍在、系膜根部仍窄，则为 A。",
    "",
    "【填写】在『评者2_机制』填 A/B/C/D，并在『评者2_依据原文摘句』摘录支持该判断的原文片段。",
    "  不要参考任何其他文件；填完后交回，再由第三方揭盲并计算 κ。",
]
for i, t in enumerate(notes, 1):
    c = s0.cell(i, 1, t); c.alignment = Alignment(wrap_text=True)
    if i == 1: c.font = Font(bold=True, size=13)

if CRIT:
    s1 = wbo.create_sheet("1_判读标准")
    for r, vals in enumerate(CRIT, 1):
        for c, v in enumerate(vals, 1):
            cell = s1.cell(r, c, v); cell.alignment = WRAP
            if r == 1: cell.font = HEAD; cell.fill = FILL
    for c, w in enumerate([22, 52, 60], 1):
        s1.column_dimensions[get_column_letter(c)].width = w

s2 = wbo.create_sheet("2_盲法核阅")
cols = ["盲编号", "第二台手术名称（已遮蔽）", "手术经过原文（已遮蔽）", "评者2_机制", "评者2_依据原文摘句"]
for c, v in enumerate(cols, 1):
    cell = s2.cell(1, c, v); cell.font = HEAD; cell.fill = FILL; cell.alignment = WRAP
for r, d in enumerate(rows, 2):
    s2.cell(r, 1, d["blind"]).alignment = WRAP
    s2.cell(r, 2, d["name_m"]).alignment = WRAP
    s2.cell(r, 3, d["narr_m"]).alignment = WRAP
    s2.cell(r, 4, "").fill = YFILL
    s2.cell(r, 5, "").fill = YFILL
    s2.row_dimensions[r].height = 150
for c, w in enumerate([10, 34, 96, 14, 40], 1):
    s2.column_dimensions[get_column_letter(c)].width = w
s2.freeze_panes = "A2"

# ★ 只有直接运行本脚本才写盘（见文件末尾的 __main__ 保护）。
#   2026-07-27 make_index_adjudication.py 为取 mask() 而 import 本模块，触发了这里的 save()，
#   把评者2已填好的『评者2_机制』列整列清空，Pass 3 从 Supplementary Table S1 静默消失。

# ---------------- 写答案键 ----------------
wk = openpyxl.Workbook(); sk = wk.active; sk.title = "答案键_评分前勿开"
for c, v in enumerate(["盲编号", "研究编号", "首台入路", "评者1_机制", "评者1_依据摘句"], 1):
    cell = sk.cell(1, c, v); cell.font = HEAD; cell.fill = FILL
for r, d in enumerate(rows, 2):
    sk.cell(r, 1, d["blind"])
    sk.cell(r, 2, d["sid"])
    sk.cell(r, 3, approach(first[d["sid"]]))
    sk.cell(r, 4, d["r1"])
    sk.cell(r, 5, d["quote"]).alignment = WRAP
for c, w in enumerate([10, 14, 14, 14, 60], 1):
    sk.column_dimensions[get_column_letter(c)].width = w

if __name__ == "__main__":
    # 写盘前先自查：盲评本若已有人填过『评者2_机制』，一律不覆盖，除非显式加 --force
    filled = 0
    if os.path.exists(OUT_BLIND):
        _old = openpyxl.load_workbook(OUT_BLIND, data_only=True)["2_盲法核阅"]
        filled = sum(1 for r in range(2, _old.max_row + 1)
                     if str(_old.cell(r, 4).value or "").strip())
    if filled and "--force" not in sys.argv:
        raise SystemExit("★ %s 中已有 %d 例填了『评者2_机制』，拒绝覆盖。\n"
                         "  确需重新出题请加 --force，并先另存备份。" % (OUT_BLIND, filled))
    wbo.save(OUT_BLIND)
    wk.save(OUT_KEY)
    print("saved %s (%d 例) / %s" % (OUT_BLIND, len(rows), OUT_KEY))
print("评者1 原判分布:", {k: sum(1 for d in rows if d["r1"] == k) for k in sorted({d["r1"] for d in rows})})
print("遮蔽标记出现次数:", sum(d["narr_m"].count(TOKEN) for d in rows))
