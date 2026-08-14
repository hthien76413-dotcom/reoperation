# -*- coding: utf-8 -*-
"""主库缺失手术记录的补录模块。

背景：部分患儿的某次住院记录未导入主库《全部肠旋转不良数据.xlsx》，
导致 (a) 再手术记录缺失，或 (b) **首台记录缺失**（更严重：会使 first[] 取到再手术，
从而错判暴露变量『首台入路』与『首台坏死』）。

来源：《17例丢失的再次手术病例原始临床资料.xlsx》——病案室调阅补录，按患儿分 sheet 存放原始文本。
本模块按【住院号 + 手术日期】定位记录并解析，避免硬编码行号。
"""
import re, openpyxl
from datetime import datetime

LOST17 = r"D:\全部肠旋转不良\③肠旋转不良术后再手术\17例丢失的再次手术病例原始临床资料.xlsx"

# pid -> (sheet名, 住院号, 手术日期, 该记录是首台还是再手术)
SUPP_SPEC = {
    "4042304": ("12胡瑞凯",     "1041483", datetime(2017, 4, 22), "reop"),
    "5148381": ("14庞玉霞之子", "948599",  datetime(2016, 1, 25),  "reop"),
    "3545381": ("11柯思杰",     "979358",  datetime(2016, 11, 11), "reop"),
    # ↓ 首台缺失：主库仅有再手术记录，若不补则 first[] 会误取再手术（入路/坏死判定全错）
    "2080111": ("9邱心宇",      "1099401", datetime(2018, 2, 1),   "index"),
}

_CACHE = None

def _field(txt, key, maxlen=4000):
    """从『k:v,k:v』式文本里取字段值（值可能含中文逗号，故按下一个已知键截断）。"""
    m = re.search(re.escape(key) + r"[:：]", txt)
    if not m: return ""
    rest = txt[m.end():]
    nxt = re.search(r",[^,:：]{2,12}[:：]", rest)
    return (rest[:nxt.start()] if nxt else rest)[:maxlen].strip()

def _op_names(txt):
    # 需前接行首或逗号，避免误匹配『复制手术名称1:复制』『主手术备注…』等派生字段
    names = re.findall(r"(?:^|,)手术名称\d*[:：]([^,，]{1,100})", txt)
    out, seen = [], set()
    for n in names:
        n = n.strip()
        if n and n != "复制" and n not in seen:
            seen.add(n); out.append(n)
    return "+".join(out)

def load_supplements(path=LOST17):
    """返回 {pid: dict(kind, d, sname, dx, anes, narr, source)}。文件不存在时返回空。"""
    global _CACHE
    if _CACHE is not None: return _CACHE
    out = {}
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as e:
        print("[_supplements] 无法打开补录文件:", e)
        _CACHE = {}; return _CACHE
    for pid, (sheet, zyh, dtarget, kind) in SUPP_SPEC.items():
        if sheet not in wb.sheetnames:
            print("[_supplements] sheet 缺失:", sheet); continue
        ws = wb[sheet]
        want = "%d年%d月%d日" % (dtarget.year, dtarget.month, dtarget.day)
        found = None
        for r in range(1, ws.max_row + 1):
            v = ws.cell(r, 1).value
            if v is None: continue
            t = str(v)
            if "手术开始时间" not in t: continue
            if want not in t: continue
            if zyh and zyh not in t: continue
            found = t; break
        if not found:
            print("[_supplements] 未定位到记录: pid=%s %s %s" % (pid, sheet, want)); continue
        out[pid] = dict(
            kind=kind, d=dtarget, zyh=zyh,
            sname=_op_names(found) or _field(found, "手术名称1", 200),
            dx=_field(found, "术中诊断", 300),
            anes=_field(found, "麻醉方式", 40) or _field(found, "麻醉方法", 40),
            narr=_field(found, "手术经过"),
            source="17例丢失的再次手术病例原始临床资料.xlsx / sheet[%s] / 住院号%s（该次住院记录未导入主库）" % (sheet, zyh),
        )
    _CACHE = out
    return out

if __name__ == "__main__":
    for pid, s in load_supplements().items():
        print("pid=%s [%s] %s 住院号%s" % (pid, s["kind"], s["d"].date(), s["zyh"]))
        print("   术式:", s["sname"][:80])
        print("   诊断:", s["dx"][:60])
        print("   经过长度:", len(s["narr"]))
