# 投稿准备（一）：定位 + 方法学自查（STROBE）

> 目标期刊：Journal of Pediatric Surgery（Original Article）
> 框架约束（已查证）：结构化摘要 ≤250 词、正文 ≤5000 词、参考文献 ≤50、STROBE、Highlights 3–5 条、末尾标 **Type of Study** 与 **Level of Evidence**。
> 本文档只做投稿前定位与自查，不动手写稿。写稿时对照本表逐条落实。

---

## A. 核心定位（决定全稿主线，先定这个）

### A1. 主线信息（clinical message）——以“描述性”为主，不以“比较”为主

| | 内容 | 为什么放这个位置 |
|---|---|---|
| **主线 A（最强，放标题/Abstract Purpose）** | Ladd 术后早期再手术**高度集中在术后第 2–3 周**（中位 14 天，86% 在 8–21 天），**逾半数（12/22）是持续性十二指肠梗阻**——提示首次 Ladd 对十二指肠梗阻解除不彻底 / 漏诊内在十二指肠病变 | 清晰、可操作的临床信息（术中充分处理十二指肠、术后 2–3 周警惕再梗阻）；**不依赖脆弱的 OR**，站得最稳 |
| **主线 B（次要，须降级）** | 竞争风险校正下腹腔镜完成组 CIF 更高，但两组置信带重叠 | 只能作 hypothesis-generating |

### A2. 标题重构（把脆弱的“与首次术式关联”移出标题）

- 现标题（中）：肠旋转不良首次 Ladd 术后早期梗阻再手术：间隔特征及与首次术式的关联
- 建议英文（主线 A 优先）：
  - **“Early Reoperation for Obstruction After the Primary Ladd Procedure: Timing, Mechanisms, and a Competing-Risk Analysis of 466 Children”**
  - 备选：“Timing and Mechanisms of Early Reoperation After the Ladd Procedure for Intestinal Malrotation: A Single-Center Retrospective Cohort”

### A3. 证据等级 / 研究类型（摘要末尾必填）

- **Type of Study:** Retrospective comparative study（retrospective cohort with competing-risk analysis）
- **Level of Evidence:** **Level III**（回顾性比较；描述性部分 Level IV，取更保守的 III 标注）

---

## B. 三个必须**主动 frame** 的方法学软肋（审稿人一定打，先发制人）

### B1. 对照臂事件仅 2 例 → 比较分析必须降级
- 开腹+中转 208 例里只有 **2 个再手术事件**。所有 OR（8.2 / 11.0 / 14.1）都建立在“2”上，CI 极宽、极不稳。
- **对策**：正文明确写 sparse-event，OR 只作描述；**主分析用竞争风险 CIF**（见 B2），不用 OR 下因果结论。

### B2. 竞争风险 / 幸存者偏倚（本稿最关键，也是最大加分点）
- 方向明确：开腹/中转组**坏死 24.7% / 25.9%、放弃或自动出院 13%、竞争结局合计 16.9%**（腹腔镜仅 1.2%）。重症患者在“能够再手术”之前已死亡/坏死切除/放弃 → **退出可再手术人群**（informative censoring）。腹腔镜组再手术率高，部分只是因为“活下来的轻症”。
- **你们已经做了正确的事**：`CIF_reop.png` 是竞争风险校正的累积发生率，且**校正后两组置信带重叠**——这恰恰证明朴素比较被竞争风险扭曲。
- **对策**：把 **Aalen–Joh@nson / Fine–Gray 竞争风险 CIF 提为 Methods 的主分析**（死亡、坏死性肠切除、放弃/自动出院列为竞争事件），朴素率/OR 降为次要。Discussion 用一段专门讲 competing risk 如何 inflate 朴素组间差异。这一段写好，等于替审稿人把最锋利的刀先接住了。

### B3. 指征偏倚 + 时代 / 学习曲线混杂
- 腹腔镜近年才开展（时代 + 学习曲线），且术者倾向给轻症选腹腔镜（indication bias），与 B2 叠加。
- **对策**：Limitations 明写；标题/结论不出现“腹腔镜导致”字样，一律用 associated with / in the context of competing risks。

---

## C. STROBE 逐条自查（只列**有 gap 或需强化**的条目）

| STROBE | 条目 | 现状 | 投稿前要补 |
|---|---|---|---|
| 4 | 研究设计 | 报告未在开头点明 | Methods 首句：single-center **retrospective cohort** |
| 5 | Setting | **只写“跨度较长”** | ⚠️ **必补具体起止年月**（例：2010-01–2023-12）、中心层级 |
| 6 | Participants | 关键词检索纳入 | 写清检索词、纳排标准；配 **flow diagram**（见 13） |
| 8 | 测量 | 关键词抽取 + 盲法核对 + κ | ✅ 亮点：写明双评者盲法裁定、κ/PABAK（一致性结果直接引用） |
| 9 | 偏倚 | 局限里零散提到 | ⚠️ **单列一段** competing risk / survivor / indication / era（见 B） |
| 12 | 统计方法 | Wilson/Fisher/MH | ⚠️ **加竞争风险 CIF 为主分析**，写明竞争事件定义、软件版本 |
| 12c | 缺失数据 | 报告未提 | ⚠️ **必补**缺失数据数量与处理方式 |
| 13 | 参与者流程 | 无 | ⚠️ **必做 flow diagram**：466 → 三术式分组 → 21 事件（+ 队列外 1 例说明） |
| 14 | 基线描述 | **无两组基线表** | ⚠️ **必加基线特征表**：腹腔镜 vs 开腹相关的年龄/新生儿比例/性别/合并畸形/坏死等（证明/暴露不可比性） |
| 22 | 经费 | 无 | ⚠️ 补 Funding 声明（无经费也要写 “received no specific grant…”） |

> 未列出的条目（结局数据、主要结果、敏感性/分层、讨论主体）报告里已有，扩写即可。

---

## D. 这项研究的加分项（Methods/Results 里要主动亮出来）

1. **双评者盲法裁定 + κ/PABAK** —— 罕见事件用 PABAK 校正（坏死 Po 93.9%/PABAK 0.879；肠切除 Po 95.5%/PABAK 0.909），一致性质控做得比多数回顾性研究规范。
2. **竞争风险 CIF** —— 见 B2，是本稿方法学的骨架。
3. **多重敏感性 / 分层**（限定轻症、MH 校正新生儿、层内）—— 已具备，规范呈现即可。

---

## E. 投稿前硬门槛（并行去落实，不然稿子写好也投不出）

- [ ] **IRB / 伦理批件号** + 回顾性研究**知情同意豁免**声明
- [ ] 研究**具体起止年月**（STROBE item 5，无此无法投）
- [ ] 作者名单 / 单位 / 通讯作者 / CRediT 贡献分工
- [ ] 利益冲突、Funding、Data availability 三项声明

---

## 下一步接口

本页 A 段（主线 + 标题 + 证据等级）一旦你确认，即可进入**第 2 步：扩写英文 IMRaD 全稿**——摘要与引言按主线 A 落笔，方法按 C 表补齐，讨论按 B 段布防。C 表中标 ⚠️ 的 6 项建议在写稿同时逐条清零。
