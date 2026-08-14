# Supplementary material — addendum for the *Surgical Endoscopy* submission

> These two items carry the material removed from the main text when it was compressed to the
> 3500-word limit. Nothing here is new: every sentence is taken verbatim, or condensed without
> change of meaning, from `JPS_manuscript_draft_v2.md`. Splice S4 and S5 into
> `Supplementary_Material.md` after Table S3, keeping Figures S1–S2 last.

---

**Supplementary Table S4.** Full four-pass blinded adjudication protocol.

Adjudication was performed in four independent passes designed to keep eligibility, exposure, outcome, and mechanism apart. Agreement for every adjudicated item is given in Supplementary Table S1.

| Pass | What was adjudicated | Masking | Material read | Agreement |
|---|---|---|---|---|
| 1 | Cause of reoperation (six categories) and presence of an associated anomaly | All approach-identifying wording masked; reviewers blinded to whether the index operation had been laparoscopic or open | Reoperation operative narratives | Cause κ=0.90 (95% CI 0.81–0.99; observed agreement 92.3%); associated-anomaly and prior-diagnosis fields κ=1.00 |
| 2 | Index approach and index severity | Reviewers did not know who had been reoperated | Complete index operative notes for a pool of 132 children: the 38 reoperations adjudicated at that time, mixed with 94 non-reoperated children drawn at random (22% of 427) | Index approach κ=0.82; index necrosis observed agreement 93.9% (PABAK 0.88); bowel resection 95.5% (PABAK 0.91) |
| 3 | Mechanism of each persistent duodenal obstruction (technical deficiency / intrinsic lesion / postoperative periduodenal adhesion / indeterminate) | All abdominal-access wording masked; case order randomized; no access to age, study number, or index approach | Reoperation narratives of the 12 duodenal cases | Agreement on all 12 cases (100%; Wilson 95% CI 75.7–100%; κ=1.00) |
| 4 | Whether the index operation was a primary Ladd procedure | Records *after* the index operation withheld, so reoperation status could not influence eligibility | Index operative note (abdominal-access wording masked) plus any preceding operations, for 19 children with a questionable index record | κ=0.844 (95% CI 0.640–1.00; observed agreement 89.5%); the two disagreements resolved by consensus |

*Second pass.* This pass validated the keyword rules of §2.3, which assigned exposure for the remaining children. Disagreements were resolved by consensus. Agreement was quantified with Cohen's κ and, for rare binary outcomes, prevalence-adjusted bias-adjusted κ (PABAK) [15].

*Derivation of the* missed associated anomaly *category.* This category was separated out from *persistent duodenal obstruction* after adjudication. No record was re-read: membership is a deterministic function of two fields each reviewer had already scored independently under blinding (an associated anomaly other than "none", plus that anomaly having been unrecognized at the index operation), and agreement on both was perfect (κ=1.00). Applying that rule to each reviewer's own ratings gives their rating under the final taxonomy; agreement on cause was κ=0.90, unchanged from the scheme used at scoring, and the four disagreements were identical under both.

*Fourth-pass outcome.* Sixteen children were judged not to have had a primary Ladd operation — four because the index record was a diagnostic endoscopy or biopsy, eight because the index operation was a redo Ladd for recurrent malrotation, and four because a previous Ladd had been performed and the index operation was not itself a Ladd — and two further children were excluded by consensus for the same reason. In three children the true primary Ladd was identified on a later date than the earliest record, and the index operation, its approach, and the age at operation were corrected accordingly. Three of the 39 reoperations initially identified were in children excluded by this pass, all aged over one year.

*Record retrieval.* Records for four children were absent from the research extract (three reoperations and one index operation); they were retrieved from the medical-records department and re-entered before analysis. In that one child the missing index note showed conversion to open, which would otherwise have been misclassified.

---

**Supplementary Table S5.** Secondary and sensitivity analyses, taxonomy check, and full limitations.

### S5a. Secondary and sensitivity analyses

All are reported in Table 4 of the main text unless noted.

| Analysis | Purpose | Result |
|---|---|---|
| Mantel–Haenszel pooling across age bands | Stratum-adjusted overall rate | OR 1.54 (0.74–3.24) |
| Intention-to-treat regrouping (conversions with laparoscopic arm) | A surgeon cannot know in advance which child will require conversion [13] | OR 2.45 (0.97–7.4), p=0.060 |
| Consensus-adjudicated subsample (n=124) | Exposure misclassification | OR 2.03 (0.84–5.17) |
| Era comparison within the laparoscopic arm (≤2017 vs. >2017) | Learning curve | 10.0% vs. 8.8%, p=0.832 |
| Firth + index year | Approach was associated with calendar period | OR 1.49 (0.73–3.06) |
| Counting planned staged reoperations as outcomes | Outcome definition | OR 1.48 (0.74–3.1) |
| Reverting the fourth-pass eligibility exclusions (n=468) | Cohort definition | OR 1.47 (0.71–3.2) |
| Gray's test within neonates | Competing risks | χ²=7.01, p=0.008 |
| E-value for the neonatal association | Unmeasured confounding | 2.10 (for the exact lower bound of 1.38) |

Cause-specific Cox regression was fitted censoring at the competing event, with the proportional-hazards assumption checked by scaled Schoenfeld residuals (p=0.15). Firth p values are from the penalized likelihood-ratio test, obtained by constraining the coefficient of interest to zero within the full design matrix, keeping the Jeffreys penalty at the same dimension in both models. Cumulative incidence used 1000-resample bootstrap bands with administrative censoring at 42 days, matching the outcome window.

### S5b. Taxonomy check against coded intrinsic duodenal anomalies

As a check on the taxonomy, we asked whether a coded intrinsic duodenal anomaly predicted category-1 obstruction. We could not detect such a relation, but the comparison is uninformative: 1 of 20 such children had a category-1 reoperation (5.0%) versus 11/430 (2.6%) of the rest (OR 2.00, 95% CI 0.04–15.2, p=0.42), a point estimate above unity resting on a single event. It is consistent with the intended separation but does not establish it. Three of the four missed-anomaly reoperations occurred in children with an intrinsic duodenal anomaly somewhere in their record, but anomaly coding draws on text from all admissions including the reoperation, so that association cannot be interpreted.

### S5c. Full limitations

*Ascertainment.* This is a single-center retrospective study spanning 13.5 years; a child reoperated elsewhere, or managed non-operatively for the same problem, would not be captured, so 8.0% is the reoperated fraction rather than the complication rate. Children discharged against medical advice, in whom reoperation elsewhere would be most likely, were traced by telephone; 22 of 24 were accounted for and none had been operated elsewhere. The 2 who could not be contacted were both open-related neonates; counting them as unobserved duodenal reoperations — the most adverse assumption — would move the neonatal comparison to 6/142 versus 2/163 (p=0.15).

*The post hoc stratification.* The age stratification that shapes our conclusions was not prespecified; it was prompted by the bimodal age distribution of the duodenal-obstruction cases. Although the blinded mechanism data corroborate it independently of any subgroup test, it remains a post hoc division requiring confirmation in an independent cohort. The age cut-points were themselves data-driven and are covered by no multiplicity correction. We did not test the approach-by-age interaction formally: with no open-related event in any stratum the model is unidentifiable, so the difference between strata rests on separate tests, and a significant neonatal result alongside a null one beyond infancy is not itself evidence that the effect differs by age.

*Sparse events and separation.* The neonatal comparison rests on six events against a zero cell, so its lower confidence bound (1.38) is informative but its upper bound is not, and it is not robust to a single unobserved competing event: had one of the 16 open-related neonates who died reached a duodenal reoperation, p would move from 0.010 to 0.053. The expected number of such unobserved events is 0.68. The ≥1-year estimate is correspondingly imprecise, and the overall-rate comparison was underpowered (19% power for an odds ratio of 1.5, 51% for 2.0, against the observed open-related rate of 6.2%).

*Measurement.* Cause assignment used a single-choice scheme, and mixed presentations were forced to a dominant category by the prespecified priority rule. The mechanistic re-review was double-read under blinding with complete agreement, but both readers read the same records, so concordance measures reproducibility rather than accuracy: the distinction between a step left undone and adhesion around a correctly performed repair rests on what the surgeon chose to record, and a deficiency already corrected, or not remarked upon, would be missed by both readers. Agreement was also less demanding than it appears, since all three technically deficient cases were documented in unusually explicit terms. Operative narratives may carry inadvertent cues to approach despite masking. For the two rare binary severity items, positive agreement was modest (bowel resection: of seven records called positive by either reviewer, only one by both; Supplementary Table S1), so index necrosis, used as a covariate, carries measurement error that propagates into the adjusted estimates.

*Exposure.* Exposure was assigned by keyword rule and validated against blinded reviewer consensus in a 132-child subsample (κ=0.82); for the remainder it was not independently reviewed, though the rule and the reviewers agreed on 120 of 132 in that subsample and restricting the analysis to it changed nothing. Within the consensus-adjudicated subsample the keyword rule and the reviewer consensus disagreed on 5 of 124 children (4.0%). The intention-to-treat analysis is the one most sensitive to exposure misclassification, since most reviewer disagreements about approach lay on the very boundary it moves.

*Cohort and outcome definitions.* Planned staged reoperations were excluded by design; counting them as outcomes left the comparison null. Eighteen children whose index record proved not to be a primary Ladd procedure were excluded by blinded adjudication rather than as a sensitivity analysis alone; three had been reoperated, which is why the cohort and event count differ from the earliest-operation rule. The 42-day window is arbitrary: adhesive obstruction presenting later was not counted, so 8.5% after laparoscopy beyond one year is a lower bound, and the design cannot address recurrent volvulus, the outcome on which the comparative literature has focused, of which we saw two cases.

*Residual confounding and other.* Indication and urgency were not recorded separately, and index necrosis is only a partial proxy for them, so confounding by severity persists within strata. Associated-anomaly ascertainment was indeterminate for 7/450 (1.6%), and because anomaly coding draws on text from every admission including the reoperation, it records anomalies ever documented rather than anomalies known preoperatively. Reoperations may cluster by operating surgeon; we did not model surgeon-level clustering. Finally, two-thirds of this cohort presented as neonates, so the balance of causes may differ where malrotation more often presents beyond infancy.
