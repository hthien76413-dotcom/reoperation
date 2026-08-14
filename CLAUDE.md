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

- **JPS 已拒稿，且是编辑部直接拒（desk reject，未送外审）**。
  这意味着问题出在标题、摘要与 cover letter，正文论证未被读到。
  原 cover letter 以「预设比较阴性 / 分层是事后 / 结果对单个事件不稳健」三条开篇，
  对审稿人是诚实，对分诊编辑等于代写拒稿理由。
- **当前目标刊：Surgical Endoscopy**。选刊依据是文献 [23]（现 [14]）
  Zeng 2025 发在该刊，同病同术式同年龄段；本稿是「未按标志确认会怎样」的临床续篇。
### Surg Endosc 官方投稿规定（已据官方 PDF「Instructions for Authors」2025-07 版核实）

**此前一度采用的「摘要 250 / 正文 3500 / 图表 6 / 文献 35」是错的**——那组数字来自
检索引擎串台（实为 *J Pediatr Endosc Surg* 与 Thieme 的 *Endoscopy* 的规定）。实际规定：

| 项目 | 官方规定 | 本稿现状 |
|---|---|---|
| 摘要 | **≤300 词**，Background/Methods/Results/Conclusions | 250 词 ✅ |
| 正文字数 | **无上限** | 3852 词 ✅ |
| 图表数量 | **无上限**（只要求必要，同一结果不得图表并列）| 4 表 2 图 ✅ |
| 参考文献 | **无上限**，须按引用顺序编号 | 25 条 ✅ |
| 关键词 | ≤6 个 | 6 个 ✅ |
| 短标题 | **≤40 字符** | 38 字符 ✅ |
| 图片格式 | **uncompressed TIFF / GIF / JPEG / EPS**（PNG 不可）| 见 `make_submission_figures.py` |
| 作者署名 | 须含各作者**最高学位**（MD/PhD 等）| ⚠️ **待补，作者需自行提供** |
| 表格 | 每张单独上传，**不得嵌在正文里** | ⚠️ 投稿时需从 docx 拆出 |
| 时间事件数据 | 官方要求用 Kaplan-Meier 曲线 | 本稿用 Aalen-Johansen CIF，
  已在 §2.5 写明理由（存在死亡这一竞争事件，朴素 KM 会高估）|

其它要点：正文顺序须为 Introduction / Materials and Methods / Results / Discussion /
Acknowledgments / Disclosures / References / Figure legends；Disclosures 段**必须**写在
正文内且与 ICMJE COI 表一致，否则退稿；投稿走 Editorial Manager
(editorialmanager.com/send)；LLM 使用须在 Methods 声明（本稿已声明）。
官方明确「鼓励同时给出绝对效应差及其置信区间」——正是本稿以风险差为主、OR 降级的写法。

### Surg Endosc 投稿文件

| 文件 | 说明 |
|---|---|
| `SurgEndosc_manuscript_v1.md` | 正文（JPS 原稿保留不动）|
| `Cover_letter_SurgEndosc.md` | 推介信，以新颖性与 Zeng 2025 的续篇关系开篇 |
| `Supplementary_Material_SurgEndosc.md` | 已并入 S4/S5 的完整补充材料 |
| `Supplementary_addendum_S4_S5.md` | S4/S5 源文件（改动后需重新并入）|

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

- 数据准备：`_dataprep.py`（所有分析的公共入口）、`_supplements.py`（补录 4 例缺失记录）
- 数字核对：`full_number_audit.py`、`arith_audit.py`、`logic_checks.py`、`ref_audit.py`、`wordcount.py`
- 主要分析：`stratified_analysis.py`、`planned_sensitivity.py`、`age_bimodal.py`、`age_sensitivity.py`
- 影像核验：`imaging_validation.py`（见下）
- 参考文献：`renumber_refs.py`（按首现顺序重编，`--check` 预览 / `--apply` 落盘）
- 一致性：`kappa_6cat.py`、`mechanism_kappa.py`
- 出图：`flow_figure.py`、`figure_duodenal_by_age.py`、`cif_english.py`、`figure_cause_by_approach.py`
- 排版：`md2docx_v2.py`、`layout_manuscript.py`、`splice_tables.py`

**改动正文数字后，务必重跑 `full_number_audit.py` 与 `wordcount.py`；
改动引用后重跑 `ref_audit.py`，首现顺序若报 ★ 用 `renumber_refs.py` 修。**

### 影像学核验的结论（`imaging_validation.py`）

用术后影像这一独立数据源检验盲法机制学分类，**两条验证路径均为阴性**：

- 造影表现区分不了「技术不彻底」与「术后粘连」（Fisher p=1.00），
  螺旋状、弹簧征、圈变形等征象两组都出现
- 首台→再手术时距也区分不了（限新生儿层 18 天 vs 19 天，p=1.00）；
  全体 p=0.095 系年龄混杂所致，真实信号是年龄（≥1 岁 14 天 vs 新生儿 18.5 天，p=0.005）

故机制分类仍只依赖手术记录文本这一单一来源，该软肋未能补上。

**但有一个计划外的临床发现**：3 例技术不彻底中有 2 例，术后造影报十二指肠通过正常，
其中一例造影阴性后仅 3 天再手术即发现膜状索带。即术后造影阴性不能排除首台 Ladd 不彻底——
这反过来支持术中确认解剖标志。样本极小（可评造影 8 例），
稿件中必须表述为病例系列观察，**不可写成敏感度或假阴性率**。

## 注意事项

- 原始数据为患儿临床资料（`*.xlsx`），含敏感信息，**不得外传、不得贴入任何外部服务**。
- 脚本路径解析顺序已统一为：**环境变量 > 当前工作目录 > 作者本机 Windows 原路径**
  （`MALROT_SRC` / `MALROT_ADJ` / `MALROT_LOST17`），故在仓库根目录可直接运行，
  也不影响作者本机既有用法。`full_number_audit.py`、`arith_audit.py`、`ref_audit.py`
  另支持把稿件路径作为命令行第一个参数传入。
- 依赖：`openpyxl scipy pandas numpy lifelines`（竞争风险 CIF，`stratified_analysis.py` 与
  `cif_english.py` 需要）。`lifelines` 的间接依赖 `autograd-gamma` 用旧式 `setup.py`，在新版
  setuptools 下会报 `AttributeError: install_layout`（纯打包元数据问题，非缺编译器）；
  用 `SETUPTOOLS_USE_DISTUTILS=stdlib pip install lifelines` 即可装上。
  会连带把 `pandas` 降到 2.3.x（`lifelines` 要求 `<3.0`），与稿件 Methods 所记版本一致。
  `cif_english.py` 的 `savefig` 已加 `bbox_inches="tight"`（2026-08-14）：matplotlib 升到
  3.11 后左对齐加粗标题的度量变化会把标题右侧裁掉，此参数只外扩画布、不改曲线或数据。
- **`logic_checks.py` 曾内含第四轮资格裁定之前的硬编码旧数字**（7/76、8/94），
  且把「自动出院」误计为竞争事件；两处已于 2026-08-14 改为现算。
  若再见到与稿件不符的数，先确认脚本口径是否过时。
