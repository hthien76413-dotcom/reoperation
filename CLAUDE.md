# 项目记忆

## 交流约定

- **一律用中文与用户交流**（正文、解释、提问、提交说明均用中文）。
- 稿件本身是英文投稿稿，manuscript 内容保持英文；讨论、审阅意见、分析报告用中文。

## 项目概况

肠旋转不良（intestinal malrotation）首次 Ladd 术后**早期非计划再手术**的单中心回顾性队列研究，
拟投英文期刊。武汉儿童医院，2012-12 至 2026-06，450 例。

### 核心结果

- 42 天内非计划再手术 36/450（8.0%），67% 发生在术后第 8–21 天（中位 14.5 天）
- 病因构成：持续性十二指肠梗阻居首 12/36（33.3%）
- **总体再手术率两种术式无差异**（9.4% vs 6.2%，RD +3.3%，95% CI −2.0 至 +8.2）
- 持续性十二指肠梗阻：腹腔镜完成 12/255（4.7%）vs 开腹相关 0 例（RD +4.7%，95% CI 1.9–8.0，Holm p=0.010）；**OR 不可估（零单元）**
- 年龄呈双峰，11 天至 6.6 岁之间无病例（**事后分层，非预设**）
- 新生儿层 RD 4.2%（95% CI 1.0–8.9；6/142 vs 0/163），3 例技术缺陷首台手术全为新生儿腹腔镜
- ≥1 岁层全为粘连性，但开腹仅 13 例，无法比较

### 方法学亮点（转投时的主要资产）

- **四轮独立盲法裁定**（入组、术式、病因、机制），κ 0.82–1.00
- 竞争风险 CIF（Aalen-Johansen）、Firth 校正、精确置信区间、Holm 多重校正、E-value
- 局限性披露极为详尽（自我批判力度罕见）

### 已知软肋（审稿人必打）

1. 单中心、回顾性、13.5 年跨度
2. 对照臂事件稀疏 + 零单元 → OR 不可估，p 值来自分离而非效应量
3. 年龄分层为事后（HARKing 嫌疑），且切点亦为数据驱动、未做多重校正
4. **核心阳性结果对单个未观测竞争事件不稳健**（6/142 vs 1/163 时 p=0.0514）
5. 未做正式的 approach×age 交互检验（模型不可识别）

## 投稿状态

- **JPS（Journal of Pediatric Surgery）已拒稿**
- 稿件规格：摘要 244 词、正文 4990 词、4 表 2 图、25 条文献、补充 3 表 2 图

## 关键文件

| 文件 | 用途 |
|---|---|
| `JPS_manuscript_draft_v2.md` / `.docx` | 正文主稿（md 为源，docx 由 `md2docx_v2.py` 生成）|
| `Cover_letter.md`、`Highlights.md`、`Declaration_of_Interest.md` | 投稿附件 |
| `STROBE_checklist.md`、`Supplementary_Material.md` | 报告规范与补充材料 |
| `Figure1_flow_EN`、`Figure2_duodenal_by_age`、`FigureS1_CIF`、`FigureS2_cause_by_approach` | 图（各有 .pdf/.png）|
| `审稿意见_v2~v5*.md`、`模拟审稿_三审意见.md` | 历次内部批判性复核（v5 为逻辑链审查，已实施）|
| `投稿准备①_定位与STROBE自查.md` | 定位与自查，含主线 A/B 的取舍论证 |

## 核算与出图脚本

- 数据准备：`_dataprep.py`（所有分析的公共入口）
- 数字核对：`full_number_audit.py`、`arith_audit.py`、`logic_checks.py`、`ref_audit.py`、`wordcount.py`
- 主要分析：`stratified_analysis.py`、`planned_sensitivity.py`、`age_bimodal.py`、`age_sensitivity.py`
- 一致性：`kappa_6cat.py`、`mechanism_kappa.py`
- 出图：`flow_figure.py`、`figure_duodenal_by_age.py`、`cif_english.py`、`figure_cause_by_approach.py`
- 排版：`md2docx_v2.py`、`layout_manuscript.py`、`splice_tables.py`

**改动正文数字后，务必重跑 `full_number_audit.py` 与 `wordcount.py`。**

## 注意事项

- 原始数据为患儿临床资料（`*.xlsx`），含敏感信息，**不得外传、不得贴入任何外部服务**。
- 脚本里的 `PATH` 默认值多为作者本机 Windows 路径（`D:\全部肠旋转不良\...`），在本仓库运行时需用命令行参数传入实际文件名。
