# -*- coding: utf-8 -*-
"""统计投稿字数：摘要（Background→Conclusions）与正文（1 Introduction → 4 Discussion 末）。

口径按期刊惯例：不计标题页、Highlights、关键词、表格、图注、声明、参考文献；
正文计入小标题文字；剔除 markdown 标记与引用编号 [1,2] 后按空白切词。
"""
import io, re, sys

import os
_WIN_DEFAULT = r"D:\全部肠旋转不良\③肠旋转不良术后再手术\SurgEndosc_manuscript_v1.md"
if len(sys.argv) > 1:
    PATH = sys.argv[1]
elif os.path.exists("SurgEndosc_manuscript_v1.md"):
    PATH = "SurgEndosc_manuscript_v1.md"
else:
    PATH = _WIN_DEFAULT
txt = io.open(PATH, encoding="utf-8").read()


def slice_between(start_pat, end_pat):
    a = re.search(start_pat, txt, re.M)
    b = re.search(end_pat, txt[a.end():], re.M)
    return txt[a.end(): a.end() + b.start()]


def count(t):
    t = re.sub(r"\[[\d,\s–-]+\]", " ", t)          # 参考文献角标
    t = re.sub(r"[*_#>`]|^\s*-\s", " ", t, flags=re.M)
    t = re.sub(r"§\d(\.\d)?", " ", t)
    return len([w for w in t.split() if re.search(r"[A-Za-z0-9]", w)])


abstract = slice_between(r"## Structured Abstract", r"\*\*Keywords:\*\*")
body = slice_between(r"## 1\. Introduction",
                     r"^---\s*$\n+## (?:Ethics approval|Acknowledgements|Declarations)")

print("Abstract   %4d words" % count(abstract))
print("Main text  %4d words" % count(body))
