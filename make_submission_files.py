# -*- coding: utf-8 -*-
"""按 Surgical Endoscopy 的投稿文件构成，把主稿拆成可直接上传的若干文件。

官方 Instructions for Authors（2025-07 版）的相关规定：
  · 上传的 Word 主文件须含「title page, abstract with keywords, main text,
    disclosures section, references and figure legends」——即**不含表格、不含图**
  · 「Each table must be uploaded separately and should not be embedded in the text」
  · 图另以 uncompressed TIFF 等格式单独上传（见 make_submission_figures.py）
  · 正文顺序须为 Introduction / Materials and Methods / Results / Discussion /
    Acknowledgments / Disclosures / References / Figure legends
  · 「the manuscript will be returned to the corresponding author if the disclosure
    statement is not included in the manuscript text」——故 Disclosures 必须留在正文内
  · 扉页须含各作者最高学位与本文的经费信息

本脚本只做重排与拆分，不改动任何数字或论述。
主稿 SurgEndosc_manuscript_v1.md 保持完整（含表格），便于阅读与核对。

产出：
  SurgEndosc_submission_maintext.md/.docx   上传用主文件
  SurgEndosc_Table1..4.md/.docx             每张表一个文件

用法：  python3 make_submission_files.py
"""
import io
import re
import subprocess
import sys

SRC = "SurgEndosc_manuscript_v1.md"
MAIN_OUT = "SurgEndosc_submission_maintext"
TABLE_OUT = "SurgEndosc_Table%d"

# 后置各节的目标顺序（官方：… Discussion / Acknowledgments / Disclosures / References …）
BACK_ORDER = [
    "Acknowledgements",
    "Disclosures",
    "Ethics approval",
    "Funding",
    "Data availability",
    "CRediT authorship contribution statement",
    "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process",
]
# 投稿主文件中要剔除的节（表格与图各自单独上传；补充材料是另一个文件）
DROP = ["Tables", "Figures", "Supplementary material"]


def split_sections(text):
    """按 '## ' 切成 [(标题, 正文), ...]，保留出现顺序。"""
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    lead = parts[0]
    out = []
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip(), parts[i + 1]))
    return lead, out


def build_maintext(text):
    lead, secs = split_sections(text)
    by = dict(secs)
    order = [t for t, _ in secs]

    # 「Declaration of competing interest」改名为官方称谓 Disclosures
    if "Declaration of competing interest" in by:
        by["Disclosures"] = by.pop("Declaration of competing interest")
        order = ["Disclosures" if t == "Declaration of competing interest" else t for t in order]

    front = [t for t in order if t not in BACK_ORDER and t not in DROP
             and t not in ("References", "Figure legends")]
    chunks = [lead]
    for t in front:
        chunks.append("## %s%s" % (t, by[t]))
    for t in BACK_ORDER:
        if t in by:
            chunks.append("## %s%s" % (t, by[t]))
    for t in ("References", "Figure legends"):
        if t in by:
            chunks.append("## %s%s" % (t, by[t]))
    return "".join(chunks)


def extract_tables(text):
    """从 ## Tables 节里按 '**Table N.**' 切出每张表（含其脚注）。"""
    _, secs = split_sections(text)
    body = dict(secs).get("Tables")
    if body is None:
        raise SystemExit("主稿中未找到 ## Tables 节")
    marks = list(re.finditer(r"^\*\*Table (\d+)\.\*\*", body, flags=re.M))
    if not marks:
        raise SystemExit("未能在 Tables 节中定位到任何 '**Table N.**'")
    out = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        chunk = body[m.start():end]
        # 去掉分页标记；每张表单独成文件，不需要
        chunk = chunk.replace("<!--pagebreak-->", "").rstrip() + "\n"
        out[int(m.group(1))] = chunk
    return out


def to_docx(md_path, docx_path):
    r = subprocess.run([sys.executable, "md2docx_v2.py", md_path, docx_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("  !! docx 生成失败:", r.stderr.strip()[:200])
        return False
    print("  ", r.stdout.strip())
    return True


def main():
    text = io.open(SRC, encoding="utf-8").read()

    main_md = build_maintext(text)
    io.open(MAIN_OUT + ".md", "w", encoding="utf-8").write(main_md)
    assert "## Tables" not in main_md, "主文件仍含表格节"
    assert "## Disclosures" in main_md, "主文件缺 Disclosures 节"
    print("主文件：%s.md（已剔除表格与图，Disclosures 已就位）" % MAIN_OUT)
    to_docx(MAIN_OUT + ".md", MAIN_OUT + ".docx")

    tables = extract_tables(text)
    print("\n表格（各自单独上传）：")
    for n in sorted(tables):
        md = TABLE_OUT % n + ".md"
        io.open(md, "w", encoding="utf-8").write(tables[n])
        to_docx(md, TABLE_OUT % n + ".docx")

    print("\n提示：图另需 uncompressed TIFF，见 make_submission_figures.py")


if __name__ == "__main__":
    main()
