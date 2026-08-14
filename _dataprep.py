# -*- coding: utf-8 -*-
"""共享数据加载：从原始数据库重建 466 例队列、术式分组、结局与竞争事件。
逻辑复刻自 strengthen.py，仅将路径改到 D 盘、并补充性别/年龄/肠切除字段供基线表使用。
被 baseline_table.py / cif_english.py / flow_figure.py 复用。"""
import openpyxl
from collections import defaultdict
from datetime import datetime

SRC = r"D:\全部肠旋转不良\全部肠旋转不良数据.xlsx"
ADJ = r"D:\全部肠旋转不良\③肠旋转不良术后再手术\裁定表.xlsx"

# ---------------------------------------------------------------------------
# 再手术病例名单：一律来自双评者盲法裁定表 Sheet A（是否纳入=='纳入'）。
# 【勿再硬编码】2026-07-15 曾用算法初筛的 22 例名单(ADH22)，裁定完成后已作废：
# 裁定纳入 39 例，其中 19 例是初筛漏判、2 例初筛误纳（1 例计划性、1 例队列外）。
# 结局定义 = 所有【计划外】再手术（含梗阻、坏死/穿孔/吻合口并发症、其他并发症等），
# 计划性二次手术（11 例）已在裁定时排除。
# 【2026-07-26 最终六分类】共识_原因 = 1十二指肠持续梗阻(不含内在畸形) / 2肠坏死·穿孔·吻合口并发症 /
# 3粘连性肠梗阻 / 4合并畸形漏诊(再手术才证实的合并消化道畸形) / 5肠扭转复发 / 6其他。
# 沿革：原「造口相关」并入「其他」；原归1的3例十二指肠膜与原归「其他」的1例空肠闭锁改入「4合并畸形漏诊」。
# ---------------------------------------------------------------------------
_REOP_CACHE = None

def adjudicated(path=ADJ):
    """读取裁定表 Sheet A，返回 {pid: dict(zyh, d_index, d_reop, gap, cause)}（仅纳入者）。"""
    global _REOP_CACHE
    if _REOP_CACHE is not None: return _REOP_CACHE
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["A_结局裁定"]
    out = {}
    for r in range(2, ws.max_row + 1):
        pid = ws.cell(r, 2).value
        if pid is None: continue
        if str(ws.cell(r, 12).value or "").strip() != "纳入": continue
        out[str(pid).strip()] = dict(
            zyh=ws.cell(r, 3).value,
            d_index=parse_d(ws.cell(r, 4).value),
            d_reop=parse_d(ws.cell(r, 5).value),
            gap=ws.cell(r, 6).value,
            cause=str(ws.cell(r, 9).value or "").strip())
    _REOP_CACHE = out
    return out

def all_statuses(path=ADJ):
    """读取裁定表 Sheet A 全部候选（不限于"纳入"），返回 {pid: status}。
    供敏感性分析（如"把计划性再手术计入结局"）取用，避免各脚本各自重复读表。"""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["A_结局裁定"]
    out = {}
    for r in range(2, ws.max_row + 1):
        pid = ws.cell(r, 2).value
        if pid is None: continue
        out[str(pid).strip()] = str(ws.cell(r, 12).value or "").strip()
    return out

def reop_set(path=ADJ):
    """裁定表中判为"纳入"的再手术编号集合（**未按队列收缩**，当前 n=39）。

    注意：其中 3 例在 2026-07-27 的资格裁定中被判为非首台 Ladd（见 NONPRIMARY），
    已不属于 450 例队列，因而不能作为队列结局。凡是要算"发生率/构成比/逐例作图"的
    地方，一律用 reop_in_cohort()；本函数只应在描述裁定过程本身（如流程图的候选计数）
    时使用。曾因直接迭代本集合，使 Figure 3 画出 14 例（含 1 例已排除的开腹病例）。
    """
    return set(adjudicated(path))

def reop_in_cohort(path=ADJ):
    """队列内的再手术结局集合（当前 n=36）——分析与作图一律用这个。"""
    return set(adjudicated(path)) & set(load()["malrot"])

# 年龄分层（2026-07-26 起为主分析的预先分层变量）。
# 依据：12 例十二指肠持续梗阻的年龄呈双峰——3.7~11 天 6 例、6.6~13.1 岁 6 例，中间空白；
# 且年龄同时预测结局(≥1岁 8.5% vs <28天 2.0%)与暴露(≥1岁 85% 走腹腔镜 vs <28天 47%)，
# 是让粗关联偏大的混杂，方向与"严重度混杂相反"的论证【不同】，必须分层。
AGE_BANDS = [("Neonate (<28 days)", 0, 28),
             ("28 days – 1 year", 28, 365.25),
             ("≥1 year", 365.25, float("inf"))]

def age_band(days):
    if days is None: return None
    for nm, lo, hi in AGE_BANDS:
        if lo <= days < hi: return nm
    return None

# 梗阻类原因（用于亚组描述，非主结局筛选）
OBSTRUCTIVE = {"十二指肠持续梗阻", "粘连性肠梗阻", "肠扭转复发"}
CAUSES6 = ["十二指肠持续梗阻", "肠坏死/穿孔/吻合口并发症", "粘连性肠梗阻",
           "合并畸形漏诊", "肠扭转复发", "其他"]

def parse_d(x):
    if isinstance(x, datetime): return x
    if x:
        try: return datetime.strptime(str(x)[:10], "%Y-%m-%d")
        except: return None
    return None

def approach(op):
    txt = op["sname"] + " || " + op["narr"]
    if "中转" in txt: return "中转开腹"
    if any(s in txt for s in ["腹腔镜","腔镜","镜下","Trocar","trocar","气腹"]): return "腹腔镜完成"
    return "开腹"

def is_malrot(op):
    key = op["sname"] + " " + op["dx"]
    return any(k in key for k in ["拉德","ladd","Ladd","扭转复位","肠旋转","中肠","旋转不良"])

def _kw(op, kw, negs):
    t = op["narr"] + op["sname"] + op["dx"]
    if kw not in t: return False
    for neg in negs: t = t.replace(neg, "")
    return kw in t

def has_necrosis(op):
    return _kw(op, "坏死", ["未见坏死","无坏死","未见明显坏死","未坏死","无明显坏死"])

def has_resection(op):
    # 肠切除：手术文本含“肠切除/切除肠管/小肠切除/部分肠切除”，排除“未行肠切除”类否定
    t = op["narr"] + op["sname"] + op["dx"]
    negs = ["未行肠切除","未予肠切除","无需肠切除","未切除","无肠切除"]
    for neg in negs: t = t.replace(neg, "")
    return any(k in t for k in ["肠切除","切除肠管","小肠切除","肠管切除"])

def load():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    def find_sheet(pred):
        for ws in wb.worksheets:
            hdr = [str(c) for c in next(ws.iter_rows(min_row=1,max_row=1,values_only=True)) if c is not None]
            if pred(hdr): return ws
    ws_surg = find_sheet(lambda h: any("手术名称" in c for c in h))
    ws_neo  = find_sheet(lambda h: any("Apgar" in c for c in h))
    ws_dis  = wb["住院病历出院记录"]
    ws_head = wb["病案首页基本信息"]

    # 手术
    ops = defaultdict(list)
    for r in ws_surg.iter_rows(min_row=2, values_only=True):
        if r is None: continue
        pid,vid,sdate,dx,sname,anes,narr = (list(r)+[None]*7)[:7]
        if pid is None and sname is None: continue
        ops[str(pid).strip()].append(dict(d=parse_d(sdate), dx=dx or "", sname=sname or "", narr=narr or ""))
    # 合入补录：主库未导入的住院记录（含 1 例【首台】缺失，不补则 first[] 会误取再手术）
    try:
        from _supplements import load_supplements
        for pid, sp in load_supplements().items():
            if pid not in ops: continue
            if any(o["d"] == sp["d"] for o in ops[pid]): continue   # 已有则不重复加
            ops[pid].append(dict(d=sp["d"], dx=sp["dx"], sname=sp["sname"],
                                 narr=sp["narr"], _supp=sp["source"]))
    except Exception as e:
        print("[_dataprep] 补录合入失败（按主库原样继续）:", e)

    first = {pid: sorted(v, key=lambda x:(x["d"] or datetime(2100,1,1)))[0] for pid,v in ops.items()}

    # 【2026-07-27 索引手术更正】"索引手术=最早一台手术"这条规则在这 3 例上取错了台次：
    # 最早的记录只是诊断性内镜/活检，真正的初次 Ladd 在其后数日。三例均已逐份核对手术
    # 记录，更正无需临床判断（真 Ladd 术名内含拉德/Ladd，诊断栏为先天性肠旋转不良）。
    # 更正前：31645511 暴露被记为【开腹】（错），1921641 与 3558176 被整例排除在队列外。
    # 其余存疑病例（首台为复发/再次 Ladd、或既往已行 Ladd）不在此处硬编码，
    # 需盲法逐例裁定，见 pending_index_adjudication.xlsx。
    INDEX_FIX = {
        "31645511": "2024-05-27",   # 首台=开放性大肠活检；真 Ladd 同期为腹腔镜完成
        "1921641":  "2015-11-17",   # 首台=直肠活检(疑巨结肠)；真 Ladd=腹腔镜Ladd's
        "3558176":  "2016-11-14",   # 首台=结肠镜活检；真 Ladd 含 ladds 术（dx"术后"指回肠造瘘）
    }
    index_fixed = {}
    for pid, day in INDEX_FIX.items():
        cand = [o for o in ops.get(pid, []) if o["d"] and str(o["d"].date()) == day]
        if not cand:
            print("[_dataprep] ★索引更正未命中，请检查:", pid, day); continue
        index_fixed[pid] = (first[pid]["d"], cand[0]["d"])
        first[pid] = cand[0]

    # 【2026-07-27 索引手术资格裁定】两位评者对 19 例存疑索引台次独立盲法判定
    # （pending_index_adjudication.xlsx；κ=0.844，观察一致率 89.5%）。
    # 一致判为"非初次 Ladd"的 16 例在此排除；其中 3 例属于结局病例，均为 ≥1 岁的
    # 复发/再次 Ladd（13992913 粘连性梗阻、17654124 与 36146398 十二指肠梗阻）。
    # 按裁定理由分组（B/C/D 三类见手稿 §2.4 第四遍），供 flow_figure.py 等直接取用，
    # 不必再在别处重复硬编码这三个数——2026-07-28 发现 Figure 1 曾各写各的、互相矛盾。
    NONPRIMARY_REASON = {
        "B_诊断性内镜或活检": {"18598477", "1325420", "1463669", "28934957"},
        "C_复发或再次Ladd":   {"5400633", "4370043", "36146398", "17654124",
                              "3558176", "13992913", "14770822", "36345365",
                              "1426267", "18815691"},   # 末两例=协商一致定为C
        "D_既往已行Ladd":     {"5001066", "17337851", "8336031", "20002991"},
    }
    NONPRIMARY = set().union(*NONPRIMARY_REASON.values())
    # 分歧已于 2026-07-27 协商定稿，二者均判为 C；此集合保留仅为记录，不再影响纳入。
    DISPUTED = {"1426267", "18815691"}

    malrot = [p for p,o in first.items()
              if is_malrot(o) and p not in NONPRIMARY]

    # 新生儿（Apgar 代理）
    neo = set()
    for r in ws_neo.iter_rows(min_row=2, values_only=True):
        if r and r[0] is not None: neo.add(str(r[0]).strip())

    # 死亡 / 放弃
    death, abandon = set(), set()
    for r in ws_dis.iter_rows(min_row=2, values_only=True):
        if not r or not r[0]: continue
        pid = str(r[0]).strip(); blob = " ".join(str(x) for x in r if x)
        cond = str(r[6]) if len(r) > 6 and r[6] else ""
        if "死亡" in cond or ("死亡" in blob and "无死亡" not in blob): death.add(pid)
        if any(k in blob for k in ["放弃治疗","自动出院","自行出院"]): abandon.add(pid)

    # 性别 / 年龄（病案首页）
    # 【2026-07-26 修正】原先取"表中出现的第一行"，而首页是住院级、一人可有多条，
    # 行序不保证按时间排列——466 例中有 8 例因此取到了【后续住院】的年龄（最大偏差 1.6 岁）。
    # 改为按【入院日期最早】的那条记录取性别与年龄。
    hdr = [str(c) for c in next(ws_head.iter_rows(min_row=1,max_row=1,values_only=True))]
    i_pid = hdr.index("科研患者编号"); i_sex = hdr.index("性别")
    i_age = [i for i,c in enumerate(hdr) if "年龄" in c][0]     # 列名『年龄（岁）』，两位小数
    i_out = [i for i,c in enumerate(hdr) if "出院日期" in c][0]
    i_in  = [i for i,c in enumerate(hdr) if "入院日期" in c][0]
    head_rows = defaultdict(list)
    last_dis = defaultdict(lambda: None)   # 每人最晚出院日=末次在院日
    for r in ws_head.iter_rows(min_row=2, values_only=True):
        if not r or r[i_pid] is None: continue
        p = str(r[i_pid]).strip()
        d = parse_d(r[i_out]) if len(r) > i_out else None
        if d and (last_dis[p] is None or d > last_dis[p]): last_dis[p] = d
        head_rows[p].append((parse_d(r[i_in]) if len(r) > i_in else None,
                             r[i_sex], r[i_age]))
    sex, age, adm0 = {}, {}, {}
    for p, rows in head_rows.items():
        dated = [x for x in rows if x[0]]
        r0 = sorted(dated, key=lambda x: x[0])[0] if dated else rows[0]
        adm0[p] = r0[0]
        sex[p] = str(r0[1]).strip() if r0[1] is not None else ""
        try: age[p] = float(r0[2]) if r0[2] is not None else None
        except (TypeError, ValueError): age[p] = None

    # 【2026-07-27 自动出院患儿电话随访】42 天窗口内"放弃治疗/自动出院/自行出院"共 24 例，
    # 由舒俊于 2026-07 逐例电话随访（源表：自动出院随访工作表（已随访）.xlsx）。
    # 结果并非全部死亡：确认死亡 18、存活 4、失访 2。故：
    #   · 竞争事件 = 院内死亡 ∪ 随访确认死亡（存活者不是竞争事件，须留在风险集内）
    #   · 失访 2 例自末次出院日起删失（用户 2026-07-27 决定采用删失口径）
    # 6369231 的"离院后他院手术"一格经用户确认应为"否"（原表误填"是"，其备注描述的是
    # 术中家长拒绝继续手术、要求放弃治疗，9 天后死亡，无他院手术）。
    FU_DEAD = {"1187715","1514720","1862817","1978690","2711129","2878364","3286288",
               "3298398","3333843","3372104","3429325","347541","4144264","4538893",
               "4967841","576039","5971697","6369231"}
    FU_ALIVE = {"2385429","35883147","36212182","4364572"}
    FU_LOST  = {"125440","1632364"}
    died = death | FU_DEAD          # 竞争事件的唯一构成
    lost = FU_LOST                  # 删失，不计为竞争事件也不计为结局

    # 年龄（天）与真实新生儿集合。
    # 【勿再用 neo(Apgar 代理) 做分析】该代理有 41 例假阳性（实际年龄中位 47 天、最大 110 天），
    # 与真实年龄<28天 的一致率仅 90.6%；精确年龄本就可得，代理无法向审稿人交代。
    age_d = {p: (a * 365.25 if a is not None else None) for p, a in age.items()}

    # 首页年龄是【最早一次住院】时的年龄，对 463/466 例而言与索引手术同一次住院，可直接用。
    # 但上面被更正索引台次的 3 例，真 Ladd 落在其后另一次住院，代理即失效——
    # 按 Table 1 的口径（age at index operation）补上日差。31645511 因此由 27.9 天
    # 变为 37.9 天，跨过 28 天界线，不再计入新生儿层（2026-07-29 复核更正此注：
    # 旧注写的 21.9→31.9 是 2026-07-26"改按入院日期最早取值"那次修正之前的口径，
    # 结论方向不变，仅注释数字滞后，运行时 age_d 一直是对的）。
    for pid, (_old_d, new_d) in index_fixed.items():
        if age_d.get(pid) is None or adm0.get(pid) is None: continue
        age_d[pid] = age_d[pid] + (new_d - adm0[pid]).days

    neonate = {p for p, a in age_d.items() if a is not None and a < 28}

    return dict(ops=ops, first=first, malrot=malrot, neo=neo, neonate=neonate,
                death=death, abandon=abandon, sex=sex, age=age, age_d=age_d,
                last_dis=last_dis, nonprimary=NONPRIMARY, nonprimary_reason=NONPRIMARY_REASON,
                disputed=DISPUTED, index_fixed=index_fixed,
                died=died, lost=lost, fu_alive=FU_ALIVE, fu_dead=FU_DEAD)

if __name__ == "__main__":
    D = load()
    R = reop_set()
    malrot, first = D["malrot"], D["first"]
    grp = defaultdict(list)
    for p in malrot: grp[approach(first[p])].append(p)
    print("malrot 队列 n =", len(malrot), "(目标 466)")
    for g in ["腹腔镜完成","中转开腹","开腹"]:
        ps = grp[g]; reop = sum(1 for p in ps if p in R)
        nec = sum(1 for p in ps if has_necrosis(first[p]))
        res = sum(1 for p in ps if has_resection(first[p]))
        print(f"  {g:<6} n={len(ps):<4} 再手术={reop:<3} 坏死={nec}({nec/len(ps)*100:.1f}%) 肠切除={res}({res/len(ps)*100:.1f}%)")
    print("裁定纳入再手术 ∩ 队列 =", len(R & set(malrot)), "(目标 39)")
    print("死亡 n=", len(D["death"]&set(malrot)), " 放弃 n=", len(D["abandon"]&set(malrot)))
    print("性别缺失 n=", sum(1 for p in malrot if not D["sex"].get(p)))
    print("年龄缺失 n=", sum(1 for p in malrot if D["age"].get(p) is None))
