# -*- coding: utf-8 -*-
"""核心结论三（差异集中新生儿层，且与严重度混杂方向相反）三线表 -> docx。

数字均取自 原始数据分析代码/结论三_差异集中新生儿层且与严重度混杂方向相反/step1-4
的实测输出，与稿件 Table 4 及 Discussion 一致，未手写。
"""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROWS = [
    ("十二指肠持续梗阻", "6/142（4.2%）", "0/163（0.0%）",
     "RD +4.2 个百分点（1.0–8.9）；NNH = 24", "0.0096"),
    ("首次手术肠坏死", "5/142（3.5%）", "38/163（23.3%）",
     "开腹相关约为腹腔镜完成的 6.6 倍", "<0.001"),
    ("窗口内确诊死亡", "0/142（0.0%）", "16/163（9.8%）",
     "全部 16 例死亡均发生于开腹相关组", "<0.001"),
    ("敏感性：假设 1 例死亡本应是十二指肠梗阻再手术",
     "6/142（4.2%）", "1/163（0.6%）", "—", "0.0528"),
]
HEADER = ["指标", "腹腔镜完成 n/N(%)", "开腹相关 n/N(%)", "效应量 / 说明", "P 值"]
TITLE = "表 3　新生儿层的十二指肠梗阻信号与病情严重度对比（核心结论三）"
NOTE = ("注：新生儿定义为年龄 <28 天（腹腔镜完成 142 例、开腹相关 163 例）。"
        "十二指肠持续梗阻的风险差为 Newcombe 95% 置信区间；对照组零事件，OR 不可估。"
        "首次手术肠坏死与窗口内确诊死亡两项显示，开腹相关组的病情严重度明显更高——"
        "若严重度混杂驱动了该差异，理应使并发症更多出现在开腹相关组，而观察方向相反，"
        "故不支持严重度混杂是该发现的解释。末行为稳健性检验：开腹相关组 16 例窗口内"
        "死亡使这些新生儿提前离开风险集，若其中恰有 1 例本应发生十二指肠梗阻再手术而"
        "未被观测到，Fisher 精确检验 p 值将从 0.0096 升至 0.0528，说明该阳性结果对单个"
        "未观测竞争事件并不稳健，此为本研究已披露的主要局限之一。数据来源：本院肠旋转"
        "不良患儿数据库 450 例。")


def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = tcPr.find(qn("w:tcBorders"))
    if tcBorders is None:
        tcBorders = OxmlElement("w:tcBorders")
        tcPr.append(tcBorders)
    for edge, spec in kwargs.items():
        tag = "w:%s" % edge
        el = tcBorders.find(qn(tag))
        if el is None:
            el = OxmlElement(tag)
            tcBorders.append(el)
        el.set(qn("w:sz"), str(spec.get("sz", 4)))
        el.set(qn("w:val"), spec.get("val", "single"))
        el.set(qn("w:color"), spec.get("color", "000000"))


def no_border(cell):
    set_cell_border(cell, top={"sz": 0, "val": "nil"}, bottom={"sz": 0, "val": "nil"},
                     left={"sz": 0, "val": "nil"}, right={"sz": 0, "val": "nil"})


doc = Document()
for st in doc.styles:
    if st.name == "Normal":
        st.font.name = "Times New Roman"
        st.font.size = Pt(10.5)
        rPr = st.element.get_or_add_rPr()
        ea = rPr.find(qn("w:rFonts"))
        if ea is None:
            ea = OxmlElement("w:rFonts")
            rPr.append(ea)
        ea.set(qn("w:eastAsia"), "宋体")

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(TITLE)
r.bold = True
r.font.size = Pt(11)
r.font.name = "Times New Roman"
rPr = r._element.get_or_add_rPr()
ea = OxmlElement("w:rFonts"); ea.set(qn("w:eastAsia"), "黑体"); rPr.append(ea)

ncols = len(HEADER)
table = doc.add_table(rows=1 + len(ROWS), cols=ncols)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.autofit = True

widths = [Cm(5.6), Cm(3.0), Cm(3.0), Cm(4.6), Cm(1.8)]
for i, w in enumerate(widths):
    for cell in table.columns[i].cells:
        cell.width = w

for j, text in enumerate(HEADER):
    cell = table.cell(0, j)
    cell.text = ""
    para = cell.paragraphs[0]
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    run.bold = True
    run.font.size = Pt(10.5)
    run.font.name = "Times New Roman"
    rPr = run._element.get_or_add_rPr()
    ea = OxmlElement("w:rFonts"); ea.set(qn("w:eastAsia"), "黑体"); rPr.append(ea)
    no_border(cell)

for i, row in enumerate(ROWS, start=1):
    for j, text in enumerate(row):
        cell = table.cell(i, j)
        cell.text = ""
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(text)
        run.font.size = Pt(10.5)
        run.font.name = "Times New Roman"
        rPr = run._element.get_or_add_rPr()
        ea = OxmlElement("w:rFonts"); ea.set(qn("w:eastAsia"), "宋体"); rPr.append(ea)
        no_border(cell)

# 三线表边框：表格顶线、表头下线、表格底线，其余一律无线
for j in range(ncols):
    set_cell_border(table.cell(0, j), top={"sz": 12, "val": "single"})
    set_cell_border(table.cell(0, j), bottom={"sz": 8, "val": "single"})
    set_cell_border(table.cell(len(ROWS), j), bottom={"sz": 12, "val": "single"})

note_p = doc.add_paragraph()
note_run = note_p.add_run(NOTE)
note_run.font.size = Pt(9)
note_run.italic = True
note_run.font.name = "Times New Roman"
rPr = note_run._element.get_or_add_rPr()
ea = OxmlElement("w:rFonts"); ea.set(qn("w:eastAsia"), "宋体"); rPr.append(ea)

doc.save("核心结论三_三线表.docx")
print("saved 核心结论三_三线表.docx")
