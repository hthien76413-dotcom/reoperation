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
- **Surgical Endoscopy 已拒稿（2026-09-03，SEND-D-26-02727）**。主编 Mark Talamini 签发，
  「after an initial evaluation by two members of the editorial board」——**同样没送外审**，
  且模板信里未给任何具体理由。至此连续两刊都止步于送审前，说明问题反复出在
  标题/摘要/cover letter 这一层，不是正文论证。原选刊依据（本稿是 Zeng 2025 的临床续篇）
  只对 Surg Endosc 有效，换刊后失效。

- **当前目标刊：Pediatric Surgery International（Springer，IF 1.8，JCR Q2 外科）**。
  选刊依据：文献 [2] Catania 2016、[8] El-Gohary 2010 两篇同类研究均发在该刊；
  本稿本质是儿外科**结局/病因**研究而非内镜技术创新论文，与该刊定位吻合。
  混合期刊，**选订阅模式则零版面费**（OA 可选，£2890/$4390/€3390）；
  中国大陆作者无强制 OA 政策。录用后系统会让通讯作者二选一，**务必选 subscription**。

### Ped Surg Int 投稿规定（据官方 submission guidelines 检索摘要，link.springer.com 被本环境网络策略屏蔽，**未能逐字打开官方页面，投稿前须自行复核**）

| 项目 | 官方要求 | 本稿现状 |
|---|---|---|
| 摘要 | **≤200 词**，四段 **Purpose / Methods / Results / Conclusion** | 194 词（含小标题 198）✅ 已改 |
| 关键词 | **4–6 个** | 6 个 ✅ |
| 正文格式 | Word，10 号 Times Roman | 待调字号 |
| Declarations | 置于参考文献**之前**，含 Funding / Competing interests / Ethics approval / Consent / Data availability / Authors' contribution | ⚠️ 现为多个独立小节，待重排 |
| 作者贡献 + 利益冲突 | **必须在投稿系统界面填写**，只有系统内填的进最终版 | ⚠️ 投稿时需在网站另填 |
| 图 | 矢量图 EPS / 半色调 TIFF | 已有 TIFF ✅ |
| 文章类型 | 不收 case report | Original Article ✅ |

**仍未查到、须作者自行核实**：正文字数上限、参考文献条数上限、图表数量上限、
表格是否须单独成文件（Surg Endosc 要求单独上传，本刊未知）。
另：官方写「10-point Times Roman」，现有脚本出的是 12 pt 双倍行距（投稿稿通用格式）。
原文用 "e.g." 属建议而非硬性，暂未改；如要改，在 `md2docx_v2.py` 里统一调。

### Ped Surg Int 投稿文件

| 文件 | 说明 |
|---|---|
| `PedSurgInt_manuscript_v1.md` | 正文（由 Surg Endosc 稿派生；该稿已冻结留档）|
| `Cover_letter_PedSurgInt.md` | 推介信，以「病因/机制盲法裁定」与该刊自身文献 [2][8] 的承接关系开篇 |
| `Supplementary_Material_PedSurgInt.md` | 补充材料来源（S1–S5 + 图 S1/S2），除题目外与 Surg Endosc 版逐字一致 |
| `STROBE_checklist.md` | **就地更新，现跟随 Ped Surg Int 稿**（不再对应已冻结的 Surg Endosc 稿）|

**补充材料的打包方式与 Surg Endosc 不同**：Surg Endosc 要求每张表单独上传，
故当时拆成「核心 + S4 + S5」三个文件（`make_submission_supplement.py`）；
Ped Surg Int 无此规定，补充材料按通行惯例**合成单一文件**
（`Supplementary_Material_PedSurgInt.docx`，含全部 S1–S5 与两图）。
若核实后发现该刊也要求拆分，把 `make_submission_supplement.py` 的 `SRC`
与输出前缀指向 PedSurgInt 版即可。

**题目已改**（去掉句首 Versus，把病因与机制提前）：
Cause and Operative Mechanism of Early Unplanned Reoperation After Primary
Ladd Procedure: A Blinded Adjudication Study of 450 Children

### Ped Surg Int 投稿上传清单

| 上传项 | 文件 | 生成方式 |
|---|---|---|
| 正文（**含表含图的单一文件**）| `PedSurgInt_submission.docx` | `make_submission_pedsurgint.py` |
| 补充材料（单一整合文件）| `Supplementary_Material_PedSurgInt.docx` | `md2docx_v2.py` |
| 图（供排版用）| `Fig1.eps` / `Fig2.eps` / `FigS1.tif` / `FigS2.eps` | `make_submission_figures.py`（产物已 gitignore）|
| 推介信 | `Cover_letter_PedSurgInt.docx` | `md2docx_v2.py` |
| STROBE 清单 | `STROBE_checklist.docx` | 已有 |
| ICMJE COI 表 | `ICMJE_<姓名>.docx` ×5 | `make_icmje_forms.py`（产物已 gitignore）⚠️ 仍需各作者自查并签名 |
| 系统内填写用文本 | `Submission_system_statements_PedSurgInt.md/.docx` | 手写，非上传件，供复制粘贴 |

**Author Contribution 与 Competing Interest 必须在 Editorial Manager 界面里另填，
且只有系统内填的那一版进入最终发表的文章**，故已把两段（连同 Funding / Ethics /
Consent / Data availability / 共同一作说明）整理进
`Submission_system_statements_PedSurgInt.md`，与稿件 Declarations **逐字一致**，
直接整段粘贴、不要改写。为此已把稿件里 Competing interests 的措辞改成 Springer
模板用语「The authors have no relevant financial or non-financial interests to
disclose.」（原句只提 conflicts of interest 与 financial ties，未覆盖非经济利益）。

ICMJE 表用的是通用短表模板 `ICMJE_Disclosure_Form_template.docx`（当初从 Surg
Endosc 系统下载，正文不含刊名，任何期刊通用）。13 项披露一律填 None，签署日期与
稿号写在 `make_icmje_forms.py` 的 `SIGN_DATE` / `MS_NUMBER` 里，改完重跑即可。
**Springer 公开指南只要求正文 Declarations 段，未见明文要求上传 ICMJE 表**，备用而已。
作者签名前最易漏报的是第 10 项（学会/委员会任职，有偿无偿均须申报）与第 2 项
（任何来源的科研经费，含院内课题）；任一作者确有申报事项，须同时改表、改系统
填写文本、改稿件 Declarations 三处。

**与 Surg Endosc 的打包方式正好相反，勿混用脚本**：Surg Endosc 要求表格与图
各自单独上传（`make_submission_files.py`，**已停用**）；Ped Surg Int 要求
「Figures should be submitted within the body of the text」，Tables 一节亦未
要求单独上传，故产出**一个含表含图的完整 docx**，每张表／图插在正文**首次
引用它的那一段之后**（表题在表上方、图注在图下方）。

**改动 `PedSurgInt_manuscript_v1.md` 后须重跑 `make_submission_pedsurgint.py`。**
主稿本身保持「表图集中在文末」的版面不变——全部审计脚本都依赖该版面，
插入只发生在打包这一步。

### 已按该刊 Artwork/Tables 规定做过的合规改动（勿回退）

1. **图内不得有标题或图注**：四个出图脚本的 `set_title` 与底部说明文字已全部
   移除，内容都在稿件图注里。分图标号用**小写** a/b。
2. **图片格式**：Fig 1/2/S2 出**矢量 EPS**（该刊对矢量图的首选，且不受 dpi
   门槛约束）；FigS1 因置信带用 alpha 透明、EPS 不支持，改 **600 dpi TIFF**。
   注意 `ps.fonttype=42` 必须放在 PDF 保存**之后**，否则本机 matplotlib 写 PDF
   会抛 `ValueError: bytes must be in range(0, 256)`。
3. **表格脚注标记**：† ‡ § → **上标小写字母**（`^a^` 语法，md2docx 已支持）；
   星号保留（官方允许用于 significance values 与其它统计量）。
   ⚠️ 批量替换 § 时**务必避开正文小节引用**（§2.5、§4 等），曾经误伤。
4. **图注格式**：粗体 `Fig. N` 开头、编号后无标点、caption 末尾无标点；
   正文内引用亦作 `Fig. N`。补充材料的图注未改（单独文件，不进期刊校对）。
5. **表格编号顺序**：官方要求按连续编号顺序被引用。原 Table 3/4 已**对调编号**
   （现 Table 3 = 总体率与敏感性分析，Table 4 = 年龄分层），且 §2.5 的两处
   前向引用改为小节号。**`stratified_analysis.py` 里写死的表号已同步**，
   重跑不会产出旧编号。

6. **参考文献格式**：已由 Vancouver/AMA 改为 Springer 式——作者后接（年份）、
   刊名不斜体、卷:页去期号、附 DOI 全链接。25 条中 **23 条已附 DOI**，
   均取自本轮检索结果中可见的 URL 或页面文本，**未核实者一律留空**
   （官方原文 "If available, please always include DOIs"，允许缺省）。
   **[3] Lang 2026 *Surg Innov* 已于 2026-09-11 核实存在**（此前多轮检索未果，
   一度列为最大单点风险，现已解除）：PMID 42264504，DOI 10.1177/15533506261460156，
   online first 文章号 15533506261460156。所引数据亦已对上——18 项研究 3479 例
   （腹腔镜 928 / 开腹 2551），腹腔镜粘连性肠梗阻更少（OR 0.44）但术后肠扭转与
   **再手术更多（OR 1.67，P=0.03）**，即正文 §4 所引之值。DOI 已补入文献表。
   无 DOI 的两条及原因：
   - **[18] Holm 1979**、**[19] Aalen–Johansen 1978**：DOI 制度之前的旧文，
     仅有 JSTOR stable URL（如 jstor.org/stable/4615733），确无 DOI。
### Surg Endosc 官方投稿规定（已据官方 PDF「Instructions for Authors」2025-07 版核实）

**此前一度采用的「摘要 250 / 正文 3500 / 图表 6 / 文献 35」是错的**——那组数字来自
检索引擎串台（实为 *J Pediatr Endosc Surg* 与 Thieme 的 *Endoscopy* 的规定）。实际规定：

| 项目 | 官方规定 | 本稿现状 |
|---|---|---|
| 摘要 | **≤300 词**，Background/Methods/Results/Conclusions | 250 词 ✅ |
| 正文字数 | **无上限** | 4031 词 ✅ |
| 图表数量 | **无上限**（只要求必要，同一结果不得图表并列）| 4 表 2 图 ✅ |
| 参考文献 | **无上限**，须按引用顺序编号 | 25 条 ✅ |
| 关键词 | ≤6 个 | 6 个 ✅ |
| 短标题 | **≤40 字符** | 38 字符 ✅ |
| 图片格式 | **uncompressed TIFF / GIF / JPEG / EPS**（PNG 不可）| 见 `make_submission_figures.py` |
| 作者署名 | 须含各作者**最高学位** | 全部作者均为 MD ✅ |
| 表格 | 每张单独上传，**不得嵌在正文里** | 由 `make_submission_files.py` 拆出 ✅ |
| 时间事件数据 | 官方要求用 Kaplan-Meier 曲线 | 本稿用 Aalen-Johansen CIF，
  已在 §2.5 写明理由（存在死亡这一竞争事件，朴素 KM 会高估）|

其它要点：正文顺序须为 Introduction / Materials and Methods / Results / Discussion /
Acknowledgments / Disclosures / References / Figure legends；Disclosures 段**必须**写在
正文内且与 ICMJE COI 表一致，否则退稿；投稿走 Editorial Manager
(editorialmanager.com/send)；LLM 使用须在 Methods 声明（本稿已声明）。
官方明确「鼓励同时给出绝对效应差及其置信区间」——正是本稿以风险差为主、OR 降级的写法。

### 投稿上传清单（均由脚本生成，勿手工改 docx）

| 上传项 | 文件 | 生成方式 |
|---|---|---|
| 主文件 | `SurgEndosc_submission_maintext.docx` | `make_submission_files.py` |
| 正文表格 ×4 | `SurgEndosc_Table1..4.docx` | 同上 |
| 图 ×4 | `*.tif`（uncompressed TIFF）| `make_submission_figures.py`（.tif 已 gitignore）|
| 补充材料核心 | `SurgEndosc_submission_supplement.docx`（S1/S2/S3/图注/图，不含 S4/S5）| `make_submission_supplement.py` |
| 补充表格 S4 | `SurgEndosc_SupplementaryTableS4.docx` | 同上 |
| 补充表格 S5 | `SurgEndosc_SupplementaryTableS5.docx`（含 S5a–d）| 同上 |
| 推介信 | `Cover_letter_SurgEndosc.docx` | `md2docx_v2.py` |
| STROBE 清单 | `STROBE_checklist.docx` | 已有 |
| ICMJE COI 表 | 每位作者一份 | ⚠️ 需作者自行下载填写 |

**改动 `SurgEndosc_manuscript_v1.md` 后，务必重跑 `make_submission_files.py`；
改动 `Supplementary_Material_SurgEndosc.md` 后，务必重跑 `make_submission_supplement.py`——
否则拆分出的投稿文件会与来源脱节。** 两个来源文件（正文/补充材料）都保持【含全部
表格/S4/S5 的完整版】，方便阅读与核对；拆分只在生成投稿文件这一步发生，不产生
第二份需要手动同步的源文件。

### Surg Endosc 投稿文件

| 文件 | 说明 |
|---|---|
| `SurgEndosc_manuscript_v1.md` | 正文（JPS 原稿保留不动）|
| `Cover_letter_SurgEndosc.md` | 推介信，以新颖性与 Zeng 2025 的续篇关系开篇 |
| `Supplementary_Material_SurgEndosc.md` | 补充材料完整来源（含 S1–S5 全部，改动只在这里改）|
| `Supplementary_addendum_S4_S5.md` | S4/S5 历史来源文件，已被上面的完整来源取代，保留供追溯 |

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
