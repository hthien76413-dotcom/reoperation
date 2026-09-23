# -*- coding: utf-8 -*-
"""把补充材料按 Surg Endosc「each table must be uploaded separately」的要求拆分。

架构与 make_submission_files.py 对主稿的处理完全对应：
  Supplementary_Material_SurgEndosc.md 保持为【含 S1–S5 全部内容的完整来源】，
  改动后仍在这一个文件里改；本脚本只做拆分，不改动任何数字或论述。

产出（均为投稿用，可直接上传）：
  SurgEndosc_submission_supplement.md/.docx   S1 + S2 + S3 + 图注 + 图（不含 S4/S5）
  SurgEndosc_SupplementaryTableS4.md/.docx    仅 Supplementary Table S4
  SurgEndosc_SupplementaryTableS5.md/.docx    仅 Supplementary Table S5（含 S5a–d）

用法：  python3 make_submission_supplement.py
"""
import io
import re
import subprocess
import sys

SRC = "Supplementary_Material_SurgEndosc.md"
CORE_OUT = "SurgEndosc_submission_supplement"
TABLE_OUT = {4: "SurgEndosc_SupplementaryTableS4", 5: "SurgEndosc_SupplementaryTableS5"}
SEP = "\n\n---\n\n"

# 把 S4/S5 从核心文件里摘除后，在原位置留一句指引，避免读者以为内容丢失
POINTER = ("*Supplementary Tables S4 and S5 are provided as separate files "
           "(SurgEndosc_SupplementaryTableS4 / S5) per journal formatting requirements.*")

TITLE_BLOCK = ("# Supplementary material\n\n"
               "**Early Unplanned Reoperation After Laparoscopic Versus Open Ladd Procedure: "
               "Adjudicated Cause and Mechanism in 450 Children**\n\n"
               "Jun Shu, Kai Zheng, Hongqiang Bian, Jun Yang, Xin Wang\n\n---\n\n")


def to_docx(md_path, docx_path):
    r = subprocess.run([sys.executable, "md2docx_v2.py", md_path, docx_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("  !! docx 生成失败:", r.stderr.strip()[:200])
        return False
    print("  ", r.stdout.strip())
    return True


def split_items(text):
    """按 '**Supplementary Table/Figure SN.**' 切分，每项正文两端去除多余的 '---' 与空白。"""
    marks = list(re.finditer(
        r"^\*\*Supplementary (Table|Figure) S(\d+)\.\*\*", text, flags=re.M))
    if not marks:
        raise SystemExit("未能在补充材料中定位到任何 Supplementary Table/Figure 锚点")
    lead = text[:marks[0].start()]
    lead = re.sub(r"(\n+---\s*)+$", "\n", lead)  # 去掉 lead 末尾的分隔线，重新拼接时统一加

    items = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        chunk = text[m.start():end]
        chunk = re.sub(r"(\n+---\s*)+$", "", chunk).strip() + "\n"  # 去掉本项末尾的分隔线
        items.append((m.group(1), int(m.group(2)), chunk))
    return lead, items


def main():
    text = io.open(SRC, encoding="utf-8").read()
    lead, items = split_items(text)

    by_key = {(k, n): c for k, n, c in items}
    s4, s5 = by_key.get(("Table", 4)), by_key.get(("Table", 5))
    if s4 is None or s5 is None:
        raise SystemExit("未找到 Supplementary Table S4 或 S5，检查锚点是否变化")

    # ---- 核心文件：lead + 除 S4/S5 外的全部条目（原顺序），S4/S5 位置换成指引句 ----
    core_chunks, pointer_done = [lead], False
    for kind, num, chunk in items:
        if (kind, num) in (("Table", 4), ("Table", 5)):
            if not pointer_done:
                core_chunks.append(POINTER)
                pointer_done = True
            continue
        core_chunks.append(chunk)
    core_md = SEP.join(c.rstrip("\n") for c in core_chunks) + "\n"
    io.open(CORE_OUT + ".md", "w", encoding="utf-8").write(core_md)
    for check in ("Supplementary Table S1", "Supplementary Table S2",
                  "Supplementary Table S3", "Supplementary Figure S1",
                  "Supplementary Figure S2"):
        assert check in core_md, "核心文件缺少 " + check
    assert "Supplementary Table S4.**" not in core_md
    assert "Supplementary Table S5.**" not in core_md
    print("核心补充材料：%s.md（S1/S2/S3/图注/图，S4/S5 已移出并留指引句）" % CORE_OUT)
    to_docx(CORE_OUT + ".md", CORE_OUT + ".docx")

    # ---- S4、S5 各自单独成文件 ----
    for n, chunk in ((4, s4), (5, s5)):
        stem = TABLE_OUT[n]
        io.open(stem + ".md", "w", encoding="utf-8").write(TITLE_BLOCK + chunk)
        print("Supplementary Table S%d：%s.md" % (n, stem))
        to_docx(stem + ".md", stem + ".docx")

    # ---- 校验：lead + 全部 items 原样拼回，应与原文逐字符一致 ----
    reassembled = lead + SEP + SEP.join(c.rstrip("\n") for k, n, c in items) + "\n"
    def norm(s): return re.sub(r"\s+", " ", s).strip()
    if norm(reassembled) == norm(text):
        print("校验通过：拆分前后内容（去除空白差异后）逐字符一致")
    else:
        print("  !! 警告：拆分前后内容比对不完全一致，请人工核查")


if __name__ == "__main__":
    main()
