# -*- coding: utf-8 -*-
"""v3：十二指肠持续梗阻再手术 归因核阅（四分法）。
【v3 变更】病例选取改为「裁定表共识原因 == 十二指肠持续梗阻」(n=19)，
不再用第二台术式关键词初筛(旧口径仅 12 例，且与裁定不一致)。

  A 首台Ladd技术不彻底 —— 需**阳性**证据：残留索带未离断 / 系膜根部未展开(窄) / 复位不到位(肠管位置不正确)
  C 术后致密性十二指肠周围粘连 —— 广泛致密粘连包裹，但肠管位置正确、无残留索带、系膜无明显未展开
  B 内在十二指肠病变 —— 隔膜/蹼/内在狭窄，术中或内镜直接证实
  D 不确定 / 混合
"""
import openpyxl, re
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from collections import defaultdict
from datetime import datetime
from _dataprep import load, approach, reop_set, adjudicated

SRC = r"D:\全部肠旋转不良\全部肠旋转不良数据.xlsx"
OUT = r"D:\全部肠旋转不良\③肠旋转不良术后再手术\十二指肠梗阻再手术_归因核阅v3.xlsx"

REOP_DUO = ["十二指肠空肠", "十二指肠成形", "侧侧吻合", "球囊扩张", "胃空肠", "十二指肠吻合",
            "Roux", "十二指肠膈膜", "十二指肠隔膜切除"]
DUO_KW = ["十二指肠闭锁", "十二指肠狭窄", "十二指肠隔膜", "十二指肠膜", "环状胰腺"]
EXCL = {"3545381", "6109437", "2673171", "90868"}

# 证据抽取
POS_KW  = ["小肠位于", "大肠位于", "结肠位于", "回盲部位于", "空肠位于", "十二指肠位于", "阑尾"]
A_BAND  = ["索带", "Ladd带", "拉德带", "膜样", "膜状", "未离断", "未松解", "残留", "残余"]
A_MESE  = ["系膜根", "系膜宽", "拓宽系膜", "系膜未", "系膜狭", "展开"]
A_POS   = ["复位不", "位置异常", "未复位", "扭转", "再次扭转"]
C_ADH   = ["致密", "广泛", "包裹", "成团", "纠结", "严重粘连", "扭叠", "难以分离", "分离困难", "无法分离"]
C_INFL  = ["脓", "渗液", "水肿", "充血", "感染", "炎"]
B_INTR  = ["隔膜", "膈膜", "蹼", "膜式", "内在", "环状胰腺", "闭锁"]

def sents(t):
    return [s.strip() for s in re.split(r"[。；;\n]", t or "") if s.strip()]

def pick(t, kws, maxn=3):
    out = [s for s in sents(t) if any(k in s for k in kws)]
    return "；".join(out[:maxn])

def flags(t, kws):
    return "、".join(sorted({k for k in kws if k in (t or "")}))

D = load()
malrot, first = D["malrot"], D["first"]
wb0 = openpyxl.load_workbook(SRC, read_only=True, data_only=True)

surg = defaultdict(list)
ws = wb0["住院病历手术记录"]
for r in ws.iter_rows(min_row=2, values_only=True):
    if not r or r[0] is None: continue
    pid, vid, sdate, dx, sname, anes, narr = (list(r) + [None] * 7)[:7]
    d = sdate if isinstance(sdate, datetime) else None
    if d is None and sdate:
        try: d = datetime.strptime(str(sdate)[:10], "%Y-%m-%d")
        except: d = None
    surg[str(pid).strip()].append(dict(vid=str(vid).strip() if vid else "", d=d,
                                       dx=dx or "", sname=sname or "", narr=narr or ""))

ws = wb0["病案首页基本信息"]
hdr = [str(c) for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
i_vid, i_zy = hdr.index("科研就诊编号"), hdr.index("住院号")
vid2zy = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    if r and r[i_vid] is not None and r[i_zy] is not None:
        vid2zy.setdefault(str(r[i_vid]).strip(), str(r[i_zy]).strip())

dx_all = defaultdict(str)
ws = wb0["住院病历出院记录"]
for r in ws.iter_rows(min_row=2, values_only=True):
    if r and r[0] is not None:
        dx_all[str(r[0]).strip()] += " " + " ".join(str(r[i]) for i in (3, 5) if len(r) > i and r[i])
ws = wb0["病案病理诊断"]
for r in ws.iter_rows(min_row=2, values_only=True):
    if r and r[0] is not None and len(r) > 2 and r[2]:
        dx_all[str(r[0]).strip()] += " " + str(r[2])

def has_anom(p):
    return (p not in EXCL) and any(k in dx_all.get(p, "") for k in DUO_KW)


# 主库缺失第二次住院记录、由病案调阅补录的病例（裁定表 B/答案页已注明）
SUPPLEMENT = {
    "4042304": dict(
        zy="1041483",
        sname="腹腔镜十二指肠空肠Roux-Y吻合+胃镜检查+腹腔引流术",
        narr=("3、探查见腹腔肠管广泛粘连，特别是十二指肠降部与大网膜及后腹壁粘连成团，分离极其困难，"
              "十二指肠降部以上肠管扩张明显。4、向头侧牵拉横结肠，用抓钳提起距韧带15-20cm处空肠…"
              "距屈氏韧带15-20cm处横断空肠，封闭远端肠腔。将近端与距远侧封闭25-30cm空肠行端侧吻合。"
              "在结肠中动脉右侧无血管区切开腹膜，形成结肠后隧道。紧靠十二指肠梗阻近端切开十二指肠系膜对侧肠壁，"
              "行十二指肠空肠Roux-Y吻合。5.经口置胃镜检查见胃及十二指肠粘膜未见明显充血、水肿，"
              "十二指肠吻合口处吻合完好，未见狭窄及漏液、漏气。"
              "【来源：病案调阅补录（住院号1041483），第二次住院记录未导入主库】")),
}

ADJ = adjudicated()
DUO_CASES = sorted(p for p in reop_set() if ADJ[p]["cause"] == "十二指肠持续梗阻")
cases = []
for p in DUO_CASES:
    vs = sorted(surg[p], key=lambda x: (x["d"] or datetime(2100, 1, 1)))
    if len(vs) < 2:
        s = SUPPLEMENT.get(p)
        if not s:
            print("!! 缺第二台手术记录且无补录:", p); continue
        cases.append(dict(pid=p, zy=s["zy"],
            grp="腹腔镜" if approach(first[p]) == "腹腔镜完成" else "开腹相关",
            interval=ADJ[p]["gap"], anom="是" if has_anom(p) else "否",
            sname=s["sname"], narr=s["narr"],
            pos=pick(s["narr"], POS_KW, 4),
            a_band=flags(s["narr"], A_BAND), a_mese=pick(s["narr"], A_MESE, 2),
            a_pos=flags(s["narr"], A_POS),
            c_adh=flags(s["narr"], C_ADH), c_infl=flags(s["narr"], C_INFL),
            b_intr=flags(s["sname"] + " " + s["narr"], B_INTR)))
        continue
    # 取与裁定「再手术日期」最接近的那台手术记录
    dr = ADJ[p]["d_reop"]
    op1 = vs[0]
    op2 = min((v for v in vs[1:] if v["d"]), key=lambda v: abs((v["d"] - dr).days)) if dr else vs[1]
    n = op2["narr"]
    cases.append(dict(
        pid=p, zy=vid2zy.get(op2["vid"], "(未查到)"),
        grp="腹腔镜" if approach(first[p]) == "腹腔镜完成" else "开腹相关",
        interval=ADJ[p]["gap"],
        anom="是" if has_anom(p) else "否",
        sname=op2["sname"], narr=n,
        pos=pick(n, POS_KW, 4),
        a_band=flags(n, A_BAND), a_mese=pick(n, A_MESE, 2), a_pos=flags(n, A_POS),
        c_adh=flags(n, C_ADH), c_infl=flags(n, C_INFL),
        b_intr=flags(op2["sname"] + " " + n, B_INTR)))

HFILL = PatternFill("solid", fgColor="1F3864"); HFONT = Font(bold=True, color="FFFFFF", size=11)
F_A = PatternFill("solid", fgColor="FDE9E9"); F_C = PatternFill("solid", fgColor="E8F0FE")
thin = Side(style="thin", color="999999"); BORD = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = openpyxl.Workbook(); ws1 = wb.active; ws1.title = "归因核阅v2"
ws1.cell(1, 1, "十二指肠持续梗阻再手术 归因核阅 v3（四分法，n=%d）" % len(cases)).font = Font(bold=True, size=14)
ws1.cell(2, 1,
    "A 首台Ladd技术不彻底：需阳性证据——残留/未离断索带、系膜根部未展开(窄)、复位不到位(肠管位置不正确)。 | "
    "C 术后致密性十二指肠周围粘连：广泛致密粘连包裹，但肠管位置正确、无残留索带、系膜无明显未展开。 | "
    "B 内在十二指肠病变：隔膜/蹼/内在狭窄，术中或内镜直接证实。 | D 不确定或混合。")
ws1.cell(3, 1, "★关键区分点：『肠管位置』列——若小肠在右、结肠在左、回盲部已移位至左，说明首台复位到位，"
               "则致密粘连更可能是术后愈合反应(C)而非技术不彻底(A)。")
for rr in (1, 2, 3):
    ws1.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=11)
ws1.row_dimensions[2].height = 30

cols = ["序号", "住院号(第二次)", "研究编号", "首次术式", "间隔(天)", "有内在畸形诊断",
        "★肠管位置(判A/C关键)", "A线索:索带/残留", "A线索:系膜根部", "C线索:致密粘连/炎症", "B线索:内在病变"]
widths = [6, 13, 12, 10, 8, 12, 46, 16, 34, 24, 18]
HR = 5
for j, (c, w) in enumerate(zip(cols, widths), 1):
    cell = ws1.cell(HR, j, c); cell.fill = HFILL; cell.font = HFONT; cell.border = BORD
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws1.column_dimensions[get_column_letter(j)].width = w
ws1.row_dimensions[HR].height = 34

for i, c in enumerate(cases, HR + 1):
    fill = F_A if (c["a_band"] or c["a_mese"] or c["a_pos"]) else F_C
    vals = [i - HR, c["zy"], c["pid"], c["grp"], c["interval"], c["anom"], c["pos"],
            c["a_band"] or "—", c["a_mese"] or "—",
            (c["c_adh"] + ("｜炎症:" + c["c_infl"] if c["c_infl"] else "")) or "—",
            c["b_intr"] or "—"]
    for j, v in enumerate(vals, 1):
        cell = ws1.cell(i, j, v); cell.border = BORD; cell.fill = fill
        cell.alignment = Alignment(vertical="top", wrap_text=(j >= 7),
                                    horizontal="center" if j <= 6 else "left")
    ws1.row_dimensions[i].height = 62

ws2 = wb.create_sheet("手术经过全文_填归因")
cols2 = ["序号", "住院号", "研究编号", "有内在畸形诊断", "第二台手术名称", "手术经过（原文）",
         "★归因(A/B/C/D)", "依据原文摘句"]
widths2 = [6, 13, 12, 12, 26, 110, 14, 40]
for j, (c, w) in enumerate(zip(cols2, widths2), 1):
    cell = ws2.cell(1, j, c); cell.fill = HFILL; cell.font = HFONT; cell.border = BORD
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws2.column_dimensions[get_column_letter(j)].width = w
ws2.row_dimensions[1].height = 34
for i, c in enumerate(cases, 2):
    vals = [i - 1, c["zy"], c["pid"], c["anom"], c["sname"], c["narr"], "", ""]
    for j, v in enumerate(vals, 1):
        cell = ws2.cell(i, j, v); cell.border = BORD
        cell.alignment = Alignment(vertical="top", wrap_text=(j in (5, 6, 8)))
    ws2.row_dimensions[i].height = 150

ws3 = wb.create_sheet("判读标准")
crit = [
    ["类别", "判定要点（需阳性证据）", "典型措辞"],
    ["A 首台Ladd技术不彻底",
     "再探查时发现本应在首台完成而未完成的步骤", "残留/未离断的Ladd带或索带；系膜根部仍狭窄(如『系膜宽度仅2cm』)；肠管未复位(小肠未在右/结肠未在左)；十二指肠仍未拉直"],
    ["C 术后致密性十二指肠周围粘连",
     "首台步骤已完成，梗阻源于新形成的粘连", "肠管位置正确；十二指肠被致密粘连包裹/成团/扭叠、与后腹膜粘连紧密；常伴渗液、水肿、脓苔等炎症背景；无残留索带、系膜无明显未展开"],
    ["B 内在十二指肠病变", "术中或内镜直接证实的先天性腔内病变", "扪及隔膜并切除；胃镜见膈膜；内在狭窄环"],
    ["D 不确定 / 混合", "证据不足或多种机制并存", "描述含糊；A与C证据并存且无法分主次"],
]
for i, row in enumerate(crit, 1):
    for j, v in enumerate(row, 1):
        cell = ws3.cell(i, j, v); cell.border = BORD
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        if i == 1: cell.fill = HFILL; cell.font = HFONT
for j, w in enumerate([22, 40, 70], 1):
    ws3.column_dimensions[get_column_letter(j)].width = w
for i in range(2, 6): ws3.row_dimensions[i].height = 66

wb.save(OUT)
print("saved", OUT, "| n =", len(cases))
print("自动提示 A线索(索带/系膜/复位):", sum(1 for c in cases if c["a_band"] or c["a_mese"] or c["a_pos"]))
print("自动提示 C线索(致密粘连):", sum(1 for c in cases if c["c_adh"]))
