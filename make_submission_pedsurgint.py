# -*- coding: utf-8 -*-
"""按 Pediatric Surgery International 的要求，把主稿打包成【单一完整 docx】。

与上一目标刊（Surgical Endoscopy）的关键差别——两者要求正好相反，勿混用脚本：

  · Surg Endosc：「Each table must be uploaded separately and should not be
    embedded in the text」，图亦单独上传 → 见 make_submission_files.py（已停用）
  · Ped Surg Int：「Figures should be submitted **within the body of the text**.
    Only if the file size of the manuscript causes problems in uploading it,
    the large figures should be submitted separately from the text.」
    Tables 一节亦未要求单独上传 → 本脚本产出一个含表含图的完整 docx

摆放位置：每张表／图插在正文**首次引用它的那一段之后**，便于审稿人就地对照，
也满足「Tables/Figures should always be cited in text in consecutive numerical
order」（表与图的首次引用顺序已在稿件中校正为 1→2→3→4 与 1→2）。

版式约定：
  · 表题在表**上方**（稿件原样：**Table N.** 标题 + 表体 + 脚注）
  · 图注在图**下方**（Springer 惯例），格式为粗体 "Fig. N" 开头、编号后无标点
  · 表格与图之间不插分页符——正文连续排版，交由期刊排版处理

本脚本只做重排，不改动任何数字或论述。主稿保持「表图集中在文末」的版面，
所有审计脚本（full_number_audit / arith_audit / ref_audit）都依赖该版面。

产出：
  PedSurgInt_submission.md / .docx    上传用的唯一正文文件（含表含图）

用法：  python3 make_submission_pedsurgint.py
"""
import io
import os
import re
import subprocess
import sys

SRC = "PedSurgInt_manuscript_v1.md"
OUT = "PedSurgInt_submission"

# 正文之后的节，按 Ped Surg Int 要求：… Discussion / Acknowledgements /
# Declarations（置于参考文献之前）/ References
BACK_ORDER = ["Acknowledgements", "Declarations", "References"]
# 打包时要拆掉、把内容分散插入正文的节；补充材料是另一个上传文件
DROP = ["Tables", "Figure legends", "Figures", "Supplementary material"]


def split_sections(text):
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    return parts[0], [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def extract_tables(by):
    """从 ## Tables 节切出 {编号: 表块}，表块含标题、表体与脚注。"""
    body = by.get("Tables")
    if body is None:
        raise SystemExit("主稿中未找到 ## Tables 节")
    marks = list(re.finditer(r"^\*\*Table (\d+)\.\*\*", body, flags=re.M))
    out = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        chunk = body[m.start():end].replace("<!--pagebreak-->", "").strip() + "\n"
        out[int(m.group(1))] = chunk
    if not out:
        raise SystemExit("未能在 Tables 节中定位到任何 '**Table N.**'")
    return out


def extract_figures(by):
    """把 ## Figures 里的图片行与 ## Figure legends 里的图注配对成 {编号: 图块}。

    图注在图下方（Springer 惯例）。图注本身已是 "**Fig. N** …" 的规定格式。
    """
    legends, images = by.get("Figure legends", ""), by.get("Figures", "")
    caps = {int(m.group(1)): m.group(0).strip()
            for m in re.finditer(r"^\*\*Fig\. (\d)\*\* .+$", legends, flags=re.M)}
    # alt 文字里含括号（如「(255 laparoscopic, …)」），故路径只取行尾那一对括号，
    # 且必须沿用此处捕获的 path，不能事后再从整行重新搜第一个括号。
    imgs = {}
    for m in re.finditer(r"^!\[[^\]]*\]\(([^()]+)\)\s*$", images, flags=re.M):
        path = m.group(1)
        n = re.search(r"Figure(\d)", path)
        if n:
            imgs[int(n.group(1))] = (m.group(0).strip(), path)
    out = {}
    for n in sorted(set(caps) | set(imgs)):
        if n not in caps or n not in imgs:
            raise SystemExit("Figure %d 的图或图注缺失（图注 %s / 图 %s）"
                             % (n, n in caps, n in imgs))
        line, path = imgs[n]
        if not os.path.exists(path):
            raise SystemExit("Figure %d 的图片文件 %s 不存在，请先跑出图脚本" % (n, path))
        out[n] = line + "\n\n" + caps[n] + "\n"
    return out


def place_inline(body, items):
    """把 items = [(引用正则, 内容块, 名称)] 插到各自首次引用所在段之后。

    先在**未改动的**文本上算出全部插入点，再由后往前插，避免偏移串位。
    """
    plans = []
    for pat, chunk, name in items:
        m = re.search(pat, body)
        if not m:
            raise SystemExit("正文中找不到 %s 的引用" % name)
        para_end = body.find("\n\n", m.end())
        if para_end == -1:
            para_end = len(body)
        plans.append((para_end, chunk, name))
    for pos, chunk, name in sorted(plans, key=lambda x: -x[0]):
        body = body[:pos] + "\n\n" + chunk.rstrip() + "\n" + body[pos:]
    return body, [(n, p) for p, _, n in sorted(plans)]


def to_docx(md_path, docx_path):
    r = subprocess.run([sys.executable, "md2docx_v2.py", md_path, docx_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("  !! docx 生成失败:", r.stderr.strip()[:300])
        return False
    print("  ", r.stdout.strip())
    return True


def main():
    text = io.open(SRC, encoding="utf-8").read()
    lead, secs = split_sections(text)
    by, order = dict(secs), [t for t, _ in secs]

    tables, figures = extract_tables(by), extract_figures(by)

    # 正文各节（扉页→讨论），按原顺序拼接
    front = [t for t in order if t not in DROP and t not in BACK_ORDER]
    body = lead + "".join("## %s%s" % (t, by[t]) for t in front)

    items = ([(r"\bTable %d\b" % n, tables[n], "Table %d" % n) for n in sorted(tables)]
             + [(r"\bFig\. %d[ab]?\b" % n, figures[n], "Fig. %d" % n) for n in sorted(figures)])
    body, placed = place_inline(body, items)

    doc = body + "".join("## %s%s" % (t, by[t]) for t in BACK_ORDER if t in by)
    io.open(OUT + ".md", "w", encoding="utf-8").write(doc)

    # ---- 校验 ----
    for n in tables:
        assert doc.count("**Table %d.**" % n) == 1, "Table %d 未唯一出现" % n
    for n in figures:
        # 正文内引用写作 "Fig. N"（不加粗），故加粗形式只应出现在图注这一处
        assert doc.count("**Fig. %d**" % n) == 1, "Fig. %d 的图注未唯一出现" % n
    for s in DROP:
        assert ("## %s" % s) not in doc, "打包件仍含 ## %s 节" % s
    assert "## Declarations" in doc and "## References" in doc

    print("单一投稿文件：%s.md（含全部表与图，插在各自首次引用之后）" % OUT)
    print("  插入位置（按正文先后）：")
    for name, _ in placed:
        print("     %s" % name)
    to_docx(OUT + ".md", OUT + ".docx")
    print("\n补充材料另见 Supplementary_Material_PedSurgInt.docx；"
          "图另有 Fig1/Fig2/FigS1/FigS2 供期刊排版用（make_submission_figures.py）。")


if __name__ == "__main__":
    main()
