# Editorial Manager 界面填写用（Pediatric Surgery International）

投稿系统里另填的 Author Contribution 与 Competing Interest，**只有系统内填的那一版进入最终发表的文章**，
故下面各段与 `PedSurgInt_manuscript_v1.md` 的 Declarations 段逐字一致，直接整段复制粘贴即可，不要改写。

---

## 1. Author Contribution（必填）

**首选版本**（与稿件 Declarations 逐字一致；系统的富文本框支持粗体时用这版）：

> **Jun Shu:** Conceptualization, Methodology, Software, Formal analysis, Data curation, Validation, Visualization, Writing – original draft. **Kai Zheng:** Conceptualization, Investigation, Data curation, Validation, Writing – original draft. **Hongqiang Bian:** Investigation, Resources, Writing – review & editing. **Jun Yang:** Investigation, Resources, Writing – review & editing. **Xin Wang:** Conceptualization, Supervision, Project administration, Writing – review & editing. Jun Shu and Kai Zheng independently performed the blinded outcome and exposure adjudication and, in a separate blinded pass, the mechanism re-review of the persistent duodenal obstructions. All authors read and approved the final manuscript.

**纯文本版本**（若输入框只收纯文本，粘贴这版；内容完全相同，只是去掉粗体）：

> Jun Shu: Conceptualization, Methodology, Software, Formal analysis, Data curation, Validation, Visualization, Writing – original draft. Kai Zheng: Conceptualization, Investigation, Data curation, Validation, Writing – original draft. Hongqiang Bian: Investigation, Resources, Writing – review & editing. Jun Yang: Investigation, Resources, Writing – review & editing. Xin Wang: Conceptualization, Supervision, Project administration, Writing – review & editing. Jun Shu and Kai Zheng independently performed the blinded outcome and exposure adjudication and, in a separate blinded pass, the mechanism re-review of the persistent duodenal obstructions. All authors read and approved the final manuscript.

**若系统改用 Springer 的叙述式模板**（有些界面给的是填空句式，而非 CRediT 列表）：

> All authors contributed to the study conception and design. Data collection was performed by Jun Shu, Kai Zheng, Hongqiang Bian and Jun Yang. The blinded adjudication of eligibility, index approach, cause and mechanism was performed independently by Jun Shu and Kai Zheng. Statistical analysis was performed by Jun Shu. The first draft of the manuscript was written by Jun Shu and Kai Zheng, and all authors commented on previous versions of the manuscript. Xin Wang supervised the study. All authors read and approved the final manuscript.

---

## 2. Competing Interest（必填）

> The authors have no relevant financial or non-financial interests to disclose.

系统若是逐位作者勾选「是否有利益冲突」的形式：五位作者**全部选「No」**，
再把上面这句填进汇总说明框。

---

## 3. Funding（通常同页一并填）

> The authors declare that no funds, grants, or other support were received during the preparation of this manuscript.

稿件正文用的是等义的另一句（"This research did not receive any specific grant from funding
agencies in the public, commercial, or not-for-profit sectors."），两者都符合该刊模板；
若系统要求与正文一致，用正文那句。

---

## 4. Ethics approval（如有该栏）

> This study was approved by the Ethics Committee of Wuhan Children's Hospital (Wuhan Maternal and Child Healthcare Hospital), Tongji Medical College, Huazhong University of Science & Technology (approval no. 2026R018-E01), and was performed in accordance with the ethical standards of the institutional research committee and with the 1964 Declaration of Helsinki and its later amendments.

## 5. Consent to participate（如有该栏）

> Informed consent was waived by the institutional ethics committee owing to the retrospective design and the use of de-identified records.

## 6. Consent to publish（如有该栏）

> Not applicable; no individually identifiable data are reported.

## 7. Data availability（如有该栏）

> The data that support the findings of this study are not publicly available because they contain information that could compromise the privacy of the children studied. De-identified aggregate data are available from the corresponding author on reasonable request, subject to institutional approval.

---

## 8. 共同第一作者（投稿信息页）

Jun Shu 与 Kai Zheng 为共同第一作者。系统多半没有专门的勾选项，
需在「Comments to the Editor」或作者信息的备注里写明：

> Jun Shu and Kai Zheng contributed equally to this work and should be considered co-first authors.

稿件扉页第 13 行已有同一句，cover letter 末段亦已写明。

---

## 9. ICMJE 利益冲突表

`make_icmje_forms.py` 已按上面同一口径生成五份：
`ICMJE_Jun_Shu.docx` / `ICMJE_Kai_Zheng.docx` / `ICMJE_Hongqiang_Bian.docx` /
`ICMJE_Jun_Yang.docx` / `ICMJE_Xin_Wang.docx`。

- 13 项披露一律填 **None**，与本文件第 2 节的声明一致
- 日期填 2026-09-11；若投稿日不同，改 `make_icmje_forms.py` 里的 `SIGN_DATE` 重跑
- Manuscript Number 留空（尚未获得）；系统给号后填进 `MS_NUMBER` 重跑即可
- **每位作者须自行核对后签名**。最常被漏报的是第 10 项（学会、专业委员会、
  编委等任职，**有偿无偿都要报**）与第 2 项（任何来源的科研经费，含院内课题）。
  任何一位作者若确有需申报的事项，须同时改这份表、本文件第 2 节、
  以及稿件 Declarations 里的 Competing interests 三处。

Springer 的公开投稿指南只硬性要求正文 Declarations 段写明 Funding 与 Competing
interests，**未见明文要求上传 ICMJE 表**；备好是防系统临时索要，不一定用得上。
