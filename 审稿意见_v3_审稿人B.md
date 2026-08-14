# 审稿意见（审稿人 B · 独立复核）

对象：`JPS_manuscript_draft_v2.md`（2026-07-26 21:00 版，正文 4203 字）
支撑计算：`reviewB_checks.py` → `reviewB_out.txt`

**总体判断.** 这一稿的方法学自觉程度高于同类回顾性外科研究：报了率差与效能而不把阴性当等效、报了精确区间与 Holm 校正、把年龄混杂摆到台面上、机制核阅做了双人盲读。核心发现（新生儿腹腔镜 Ladd 后十二指肠持续梗阻 6/142 vs 0/166，且三例技术不彻底全在此层）是有分量且可检验的。

但本稿有**一处会被直接质疑的数字对不上**、**一处把分层论证建立在合并层数字上的逻辑漏洞**，以及**若干处在次要结论上重犯了自己在主结论上明确避免的错误**。以下按严重程度排列。

---

## 一、必须修改

### B1. §3.7 末段的「4/20 vs 8/446，OR 13.7」与全文任何口径都对不上 ★

> "Children carrying a coded intrinsic duodenal anomaly were more likely to undergo duodenal-type reoperation than those without (4/20, 20.0% vs. 8/446, 1.8%; OR 13.7, p<0.001)"

事件合计 = 4 + 8 = **12**。但全文的口径只有：第 1 类 14 例、第 4 类 4 例、两者合计 18 例。**12 不等于其中任何一个。** 读者无法复现，审稿人会直接要求解释。

更麻烦的是它的逻辑：第 1 类**按定义排除内在病变**（"with **no** intrinsic duodenal lesion found"）。用一个把内在病变排除在外的结局，去论证"带内在病变者更容易发生该结局"，是自相矛盾的。

**诊断**：这句几乎肯定是分类改版前（第 4 类尚未从第 1 类拆出时）的遗留——那时"duodenal-type reoperation"确是一个包含内在病变的合并类别，12 这个数才讲得通。同一轮改版已经清掉了 Figure 1 里的 v1 残留（"4.5%"、"22 reoperations"），这一句漏网了。

**建议**：删除，或改用现行口径重算并明确定义分子（例如"第 1 类 + 第 4 类合计 18 例"），同时说明它回答的是什么问题。若保留，须避免用第 1 类做分子。

### B2. 新生儿段落用【全队列】数字论证【层内】的严重度梯度 ★

Discussion 第三段专讲新生儿层，却写：

> "neonates chosen for open surgery were the sicker ones, with **ten-fold more bowel necrosis** and a **ten-fold higher hazard** of death or treatment withdrawal … the open-related arm's **competing events (24/208)** are too few to conceal a difference of this size."

这三个数（24.5% vs 2.3%、HR 0.11、24/208）**全部是全队列口径**。全文刚刚用两节篇幅证明年龄是强混杂、合并层会误导，紧接着又把合并层的严重度数字搬进分层论证——审稿人一眼看得出。

层内真实值（`reviewB_out.txt` ①）：

| | 全队列 | **新生儿层** | ≥1 岁层 |
|---|---|---|---|
| 首台坏死 腹腔镜 vs 开腹相关 | 2.3% vs 24.5%（10.5×） | **3.5% vs 23.5%（6.7×）** | 1.3% vs 27.8%（21×） |
| 死亡/放弃 | 1.2% vs 11.5% | **1.4% vs 13.9%（2/142 vs 23/166）** | 0% vs 0% |

**好消息是论证本身站得住**：新生儿层内开腹组坏死仍高 6.7 倍、死亡/放弃仍高约 10 倍，混杂方向确实与观察到的效应相反。只需把数字换成层内值即可——"ten-fold more necrosis"改为"六倍"，"24/208"改为"23/166"。**不改则是一个可被指出的方法学不一致；改了论证反而更硬。**

### B3. ≥1 岁层把"不显著"当成"无差异"——正是本文在总体率处明确避免的错误 ★

Highlights：*"Children over one year had an 8.5% adhesive duodenal reoperation rate **whatever the approach**"*
Discussion：*"the approach **made no difference**"*、*"**without contributing any evidence** about approach"*

该层的实际证据（`reviewB_out.txt` ③）：

- 腹腔镜 7/76 (9.2%) vs 开腹相关 **1/18** (5.6%)，精确 95%CI **0.20–82.2**
- 开腹组仅 18 例，其率的 Wilson 95%CI 为 **1.0%–25.8%**（宽 25 个百分点）
- 以观察值为真，本层检验效能 **5%**

在总体率那里，本文写的是"we did not detect a difference … this is a bounded null rather than a demonstration of equivalence"，并附率差区间与效能——处理得很好。**同一支笔在 ≥1 岁层却写"made no difference""without contributing any evidence"**，标准不一致。18 例的开腹组不足以支持任何等效陈述；正确的说法是"该层未能检出差异，且其效能极低，无法排除临床上重要的差异"。

Conclusion 的 *"In children over a year, duodenal reoperation was commoner still (8.5%) but uniformly adhesive and unrelated to approach"* 同理，且 8.5% 是**两组合并**率，却与新生儿层的**腹腔镜专属**率 4.2% 并列比较，口径不一。

---

## 二、应当修改

### B4. 腹腔镜"粘连更少"的通行认识与本文发现正面冲突，却未被直面

Introduction 写：*"laparoscopy carries a higher risk of recurrent volvulus and **a lower risk of adhesive obstruction**"*。而本文 11 例粘连机制中 **10 例是腹腔镜**——按率算 10/258 (3.9%) vs 1/208 (0.5%)，方向与通行认识相反。

Discussion 只轻描淡写地把粘连归因于"the healing response to a wide retroperitoneal dissection performed through small ports"，没有点明这与自己 Introduction 引用的文献相矛盾。这恰恰是本文最有意思的地方之一：**腹腔镜整体粘连少，但腹腔镜 Ladd 的十二指肠周围粘连并不少**——因为 Ladd 手术需要的正是一次广泛的腹膜后剥离。值得单独用两三句讲清楚，而不是绕过去。

### B5. 意向治疗分析是唯一阳性的总体结果，却从未进入 Discussion

Table 5：ITT（中转归入腹腔镜）OR 2.38，精确 95%CI 1.00–6.5，**p=0.049**。Results 用一个从句带过（"with an interval whose lower bound touches unity"），Discussion **完全没提**。

对术式比较而言 ITT 往往是更合理的主分析——术前无法预知谁会中转，"接受腹腔镜完成"是治疗后才知道的状态。把唯一阳性的总体结果放在表里却在讨论中回避，审稿人会认为是选择性呈现。**建议**：要么在 Discussion 用一段正面处理（承认 ITT 的合理性，同时指出区间下界贴到 1.00、且与其他所有口径不一致），要么在 Methods 说明为何以 as-treated 为主分析。

### B6. 中转开腹组再手术率最高（12.7%），全文未讨论

三组分别为 9.7% / **12.7%** / 4.6%。中转组是率最高的一组，n=55，临床上也最值得说（中转本身标志术中遇到困难）。全文只在 Table 5 与流程图出现，无任何解读。至少应有一句。

### B7. 新颖性断言缺乏检索依据

> "An 8.5% early adhesive-reoperation rate in older children undergoing a Ladd procedure **appears not to have been reported before**"

这是全文第二个主要卖点，建立在 **8 例事件**上，且没有描述任何文献检索。JPS 审稿人通常会要求：检索了哪些库、什么词、什么时间范围。**建议**补一句检索说明，或把措辞降到"we are not aware of a previous report of…"并明确这是 8 例的观察。

### B8. 参考文献仅 9 条，且方法学引用不成体系

引了 Firth、PABAK、STROBE，却未引 **Aalen–Johansen**、**Newcombe** 区间、**Holm** 校正、**标准化差值(SMD)** —— 而这些都是本稿明确使用并在脚注中命名的方法。方法学引用一半有一半没有，显得随意。临床文献侧也偏薄：无 Ladd 原始描述，无腹腔镜与开腹术后粘连形成的对照文献（B4 需要它）。

---

## 三、次要

- **B9. §3.2 的"53 例候选"与 466 队列不同源**：Figure 1 已注明 11 例计划性中有 4 例不在队列内，但 §3.2 正文与 Table 2 脚注仍只写"53 candidate reoperations"，读者会误以为 53 例都是队列内患儿。加半句即可。
- **B10. CRediT 未覆盖机制双人盲读**：现写"Jun Shu and Kai Zheng independently performed the blinded adjudication"，但机制核阅是第三遍、另一套盲法流程，应在贡献声明中体现。
- **B11. "whose patients … were by every severity measure doing better overall"** 措辞诱导因果误读——腹腔镜组是被**选**得更轻，而非因腹腔镜而"doing better"。建议改为 "were a systematically less severe group"。
- **B12. 28 天–1 岁层出现名义显著且方向相反的结果**（0/40 vs 3/24，p=0.049，偏向腹腔镜），仅以括号带过。处理本身诚实（注明了 3 events），但与 B5 合看，本文对"支持自己"与"不支持自己"的阳性结果处理力度不同，建议统一。
- **B13. 效能陈述未给基线风险**："21% power to detect an odds ratio of 1.5" 应注明假定的对照组事件率。

---

## 四、优先级

1. **B1** 删或重算那句 12 例的比较——这是唯一一处读者能当场发现对不上的数字。
2. **B2** 把新生儿段的三个数换成层内值（6.7×、23/166）——改动小，且改完论证更强。
3. **B3** 把 ≥1 岁层的"no difference"改成"未能检出差异 + 效能 5% + 开腹组仅 18 例"。
4. **B4/B5** 各补一段（粘连悖论、ITT）。
5. B6–B13 属清理。

改完 B1–B3 之后，本稿的内部一致性就与它的方法学自觉相称了。
