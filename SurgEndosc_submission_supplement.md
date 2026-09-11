# Supplementary material

**Early Unplanned Reoperation After Laparoscopic Versus Open Ladd Procedure: Adjudicated Cause and Mechanism in 450 Children**

Jun Shu, Kai Zheng, Hongqiang Bian, Jun Yang, Xin Wang

---

**Supplementary Table S1.** Inter-rater agreement for the four-pass blinded adjudication.

| Adjudication pass | Item scored | n | Categories | Observed agreement | Cohen's κ (95% CI) | PABAK (95% CI) |
|---|---|---|---|---|---|---|
| **Pass 1** — outcome adjudication (masked operative narratives; reviewers blinded to index approach) | Cause of reoperation, scheme applied at the time of scoring | 52 | 6 | 92.3% (48/52) | 0.90 (0.80 to 0.99) | — |
| | Cause of reoperation, final six-category scheme† | 52 | 6 | 92.3% (48/52) | 0.90 (0.81 to 0.99) | — |
| | Associated anomaly identified at reoperation | 52 | 5 | 100.0% (52/52) | 1.00¶ | — |
| | Anomaly recognized before the index operation | 52 | 3 | 100.0% (52/52) | 1.00¶ | — |
| **Pass 2** — exposure and severity adjudication (complete index operative notes; reoperated children mixed with a random sample of non-reoperated children) | Index surgical approach§ | 132 | 4 | 90.2% (119/132) | 0.82 (0.73 to 0.91) | — |
| | Bowel necrosis at the index operation (yes/no)‡ | 132 | 2 | 93.9% (124/132) | 0.57 (0.29 to 0.86) | 0.88 (0.77 to 0.94) |
| | Bowel resection at the index operation (yes/no)‡ | 132 | 2 | 95.5% (126/132) | 0.23 (−0.38 to 0.83) | 0.91 (0.81 to 0.96) |
| **Pass 3** — mechanism of persistent duodenal obstruction (reoperation narratives with abdominal-access wording masked, case order randomized)‖ | Mechanism: technical deficiency / intrinsic lesion / postoperative adhesion / indeterminate | 12 | 2 | 100% (12/12) | 1.00¶ | — |
| **Pass 4** — eligibility adjudication (index operative note with abdominal-access wording masked, plus any preceding operations; all records after the index operation withheld) | Index operation was a primary Ladd procedure | 19 | 4 | 89.5% (17/19) | 0.84 (0.64 to 1.00) | — |
| **Validation** — automated text classifier vs. reviewer consensus | Index surgical approach | 132 | 4 | 90.9% (120/132) | 0.83 (0.74 to 0.92) | — |
| | Bowel necrosis at the index operation | 132 | 2 | 93.9% (124/132) | 0.57 (0.29 to 0.86) | 0.88 (0.77 to 0.94) |

Agreement was computed from each reviewer's own independent copy of the adjudication workbook, not from the merged consensus file. Pass 1 covers 52 of the 53 candidate reoperations submitted for adjudication; the remaining child, in whom neither reviewer assigned a cause, was later excluded as a late reoperation outside the 42-day window. Of the 52 scored records, 36 were ultimately included as unplanned reoperations (11 excluded as planned staged procedures, 1 more beyond the time window, 1 for unavailable records, and 3 in children whose index operation was judged in Pass 4 not to be a primary Ladd procedure); adding the unscored child gives the 2 beyond-window exclusions reported in Supplementary Table S3. Pass 2 covers a pool of 132 index operations; Pass 3 covers the 12 cohort children reoperated for persistent duodenal obstruction; Pass 4 covers the 19 children whose index record was questionable. Disagreements were resolved by consensus before analysis.

‖ In Pass 3 the reader also had no access to age, study number, or index approach. Diagnostic endoscopy wording was deliberately left unmasked, since it carries the operative findings and does not indicate whether the index operation was laparoscopic or open. Both readers read the same records, so concordance measures reproducibility rather than accuracy.

† The category *missed associated anomaly* was created after scoring. Membership is a deterministic function of two fields each reviewer had already scored independently under blinding (an associated anomaly other than “none”, together with that anomaly being unrecognized at the index operation), and agreement on both fields was perfect (κ=1.00). Applying that rule to each reviewer's own ratings therefore yields that reviewer's rating under the final taxonomy; no record was re-read. The 4 disagreements were identical under both schemes and all lay between adhesive obstruction and either persistent duodenal obstruction or necrosis/perforation.

‡ For these two rare binary items, κ is deflated by the low base rate (the kappa paradox): expected agreement was 0.858 for necrosis and 0.941 for resection, so κ is small despite observed agreement above 93%. The prevalence-adjusted bias-adjusted κ (PABAK = (k·Pₒ − 1)/(k − 1)) is reported alongside; its confidence interval is propagated from the Wilson interval for the observed agreement. Necrosis was scored positive by one reviewer only in 8/132 records and by both in 6/132; bowel resection was scored positive by either reviewer in 7/132 records but by both in only 1, which is why its κ is lower still.

§ Approach was recorded with the labels *laparoscopic completion*, *conversion to open*, and *open*; one reviewer additionally used *laparoscopically assisted* for a single record, resolved to laparoscopic completion by consensus. Collapsing that label gives κ=0.83 (0.74 to 0.92). Of the 12 disagreements, 9 lay on the single boundary between conversion and laparoscopic completion, the same boundary examined in the intention-to-treat sensitivity analysis (Table 4); the remaining 3 involved open versus laparoscopic completion. The automated classifier used to assign approach in the full cohort was validated against the reviewer consensus in this pool (final rows).

¶ Where the two reviewers agreed on every record — the two associated-anomaly fields (52/52 each) and mechanism (12/12) — κ = 1.00, but the normal-approximation standard error of κ is zero at perfect concordance, so its confidence interval degenerates to 1.00–1.00 and is not a statement of precision. The Wilson intervals for the observed agreements are 93.1–100%, 93.1–100%, 75.7–100% respectively. In the mechanism pass only two of the four categories were used (technical deficiency 3, postoperative adhesion 9); by definition this category contains no intrinsic lesion, and no case was scored indeterminate. Agreement was aided by the three technically deficient cases being documented in unusually explicit terms.

PABAK, prevalence-adjusted bias-adjusted kappa.

---

**Supplementary Table S2.** Keyword rules used for cohort eligibility and to assign index surgical approach and index bowel necrosis for all 450 children, applied to the recorded procedure name concatenated with the operative narrative and coded diagnosis. Records are in Chinese; the original strings are given verbatim with English glosses.

| Variable | Rule (applied in order) | Original strings |
|---|---|---|
| Index approach | 1. If any conversion term is present → **conversion to open** | 中转 (conversion) |
| | 2. Otherwise, if any laparoscopic term is present → **laparoscopic completion** | 腹腔镜 (laparoscopy), 腔镜 (endoscopic/laparoscopic), 镜下 (under scope), Trocar / trocar, 气腹 (pneumoperitoneum) |
| | 3. Otherwise → **open** | — |
| Index bowel necrosis | Term present **after** deleting explicit negations → **yes**; otherwise **no** | 坏死 (necrosis); negations removed first: 未见坏死, 无坏死, 未见明显坏死, 未坏死, 无明显坏死 |
| Cohort eligibility (§2.2) | Any term present in the procedure name or coded diagnosis → candidate for adjudication | 拉德 / Ladd, 扭转复位 (derotation), 肠旋转 (intestinal rotation), 中肠 (midgut), 旋转不良 (malrotation) |

Agreement of the approach and necrosis rules with blinded reviewer consensus in the 132-child validation pool is given in Supplementary Table S1 (approach κ=0.83; necrosis κ=0.57 with observed agreement 93.9%). Because reviewers were blinded to outcome when adjudicating exposure, residual misclassification is expected to be non-differential and to bias the approach comparison toward the null.

---

**Supplementary Table S3.** Timing of unplanned reoperation (n=36).

| Characteristic | Value |
|---|---|
| Unplanned reoperations | 36 / 450 (8.0%) |
| Interval, days, median (IQR) | 14.5 (10–19) |
| Interval range, days | 2–37 |
| Postoperative days 8–21, n (%) | 24 (67) |
| Binned interval 0–7 / 8–14 / 15–21 / 22–30 / >30 d, n | 5 / 13 / 11 / 5 / 2 |

Candidate reoperations adjudicated: 53. Excluded: planned staged procedure 11 (4 of them in children outside the cohort), beyond time window 2, records unavailable 1, and 3 in children whose index operation was judged not to be a primary Ladd procedure (§2.4).

*Follow-up completeness for the 42-day window (n=450).* 396 children (88.0%) completed the window without either the outcome or the competing event; 36 (8.0%) had the primary outcome (Table 2); 16 (3.6%) had the competing event (confirmed death) within the window, at a median of 1 day (Table 3 footnote); 2 children (0.4%) discharged against medical advice could not be traced by telephone and were censored at their last recorded discharge, 5 and 18 days after the index operation (§2.3).

---

*Supplementary Tables S4 and S5 are provided as separate files (SurgEndosc_SupplementaryTableS4 / S5) per journal formatting requirements.*

---

**Supplementary Figure S1.** Competing-risk cumulative incidence of unplanned reoperation by index surgical approach, estimated with the Aalen–Johansen method treating confirmed death as the competing event, with administrative censoring at 42 days, matching the outcome window. Shaded areas are 95% bootstrap confidence bands (1000 resamples). Forty-two-day cumulative incidence was 9.4% after laparoscopic completion (n=255) versus 6.2% after open-related surgery (n=195); the corresponding cause-specific Cox hazard ratio was 1.41 (95% CI 0.71–2.82, p=0.331). The competing event itself was far more frequent in the open-related arm (all 16 deaths within the window followed open-related surgery, so the hazard ratio is not estimable), which is why the competing-risk framework was used rather than a naive Kaplan–Meier complement. *(File: FigureS1_CIF_reoperation_EN.png / .pdf)*

<!--pagebreak-->

**Supplementary Figure S1**

![Supplementary Figure S1. Aalen-Johansen cumulative incidence curves of unplanned reoperation over 42 days, laparoscopic completion versus open-related, with 95% bootstrap confidence bands; the two curves are close throughout, 9.4% versus 6.2% at day 42.](FigureS1_CIF_reoperation_EN.png)

---

**Supplementary Figure S2.** Cause-specific rate of unplanned early reoperation by index surgical approach. Bars are cause-specific rates using the whole approach group as the denominator (255 laparoscopic, 195 open-related); numerals are event counts. No difference was detected in the overall reoperation rate between approaches (9.4% vs. 6.2%, p=0.22), but the composition differed: persistent duodenal obstruction followed only laparoscopic completions (4.7% vs. 0%; risk difference +4.7 percentage points, 95% CI 1.9 to 8.0, Holm p=0.010), whereas necrosis, perforation, or anastomotic complication and “other” complications predominated after open-related surgery. Confidence intervals are given in Table 2; the duodenal-obstruction comparison is shown stratified by age in Figure 2.

<!--pagebreak-->

**Supplementary Figure S2**

![Supplementary Figure S2. Grouped bar chart of cause-specific unplanned-reoperation rate by index surgical approach across six causes, laparoscopic completion versus open-related, graphical form of Table 2.](FigureS2_cause_by_approach.png)
