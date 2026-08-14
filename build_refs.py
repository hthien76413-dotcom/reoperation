# -*- coding: utf-8 -*-
"""把手稿正文里的 [citekey] 按【首次出现顺序】编号，并生成参考文献表。

为什么用 key 而不是直接写数字：2026-07-26 补充近年文献时新增 11 条，手工重排
1–24 号极易出错（漏改一处就是引用错配）。改成 key 之后，编号完全由本脚本推导，
增删文献只需改 REFS，正文不用动。

Vancouver 式：按正文首次引用顺序编号。
文献元数据全部来自 PubMed 实际检索（`_refs.json`，见 reviewB 补文献那一轮），
未经核实的条目一律不写入。
"""
import io, re

SRC = "JPS_manuscript_draft_v2.md"

REFS = {
 # —— 临床 ——
 "nehra2011": "Nehra D, Goldstein AM. Intestinal malrotation: varied clinical presentation from infancy through adulthood. *Surgery*. 2011;149(3):386-393.",
 "catania2016": "Catania VD, Lauriti G, Pierro A, Zani A. Open versus laparoscopic approach for intestinal malrotation in infants and children: a systematic review and meta-analysis. *Pediatr Surg Int*. 2016;32(12):1157-1164.",
 "arnaud2019": "Arnaud AP, Suply E, Eaton S, Blackburn SC, Giuliani S, Curry JI, et al. Laparoscopic Ladd's procedure for malrotation in infants and children is still a controversial approach. *J Pediatr Surg*. 2019;54(9):1843-1847.",
 "lang2026": "Lang Y, Chen Q, Wu M, Chen G, Liu W, Yuan C. Laparoscopic vs open Ladd's procedure for intestinal malrotation in infants and children: a systematic review and meta-analysis. *Surg Innov*. 2026:15533506261460156.",
 "johnston2024": "Johnston WR, Hwang R, Mattei P. Laparoscopic versus open Ladd procedure for midgut malrotation. *J Pediatr Surg*. 2024;59(12):161673.",
 "zhang2022": "Zhang Z, Chen Y, Yan J. Laparoscopic versus open Ladd's procedure for intestinal malrotation in infants and children: a systematic review and meta-analysis. *J Laparoendosc Adv Surg Tech A*. 2022;32(2):204-212.",
 "xie2022": "Xie W, Li Z, Wang Q, Wang L, Pan Y, Lu C. Laparoscopic vs open Ladd's procedure for malrotation in neonates and infants: a propensity score matching analysis. *BMC Surg*. 2022;22(1):25.",
 "dacosta2021": "da Costa KM, Saxena AK. Laparoscopic Ladd procedure for malrotation in newborns and infants. *Am Surg*. 2021;87(2):253-258.",
 "skertich2021": "Skertich NJ, Ingram MC, Grunvald M, Ritz E, Pillai S, Madonna MB, et al. Outcomes of laparoscopic versus open Ladd procedures and risk factors for conversion. *J Laparoendosc Adv Surg Tech A*. 2021;31(3):336-342.",
 "elgohary2010": "El-Gohary Y, Alagtal M, Gillick J. Long-term complications following operative intervention for intestinal malrotation: a 10-year review. *Pediatr Surg Int*. 2010;26(2):203-206.",
 "karlslatt2024": "Salehi Karlslätt K, Husberg B, Ullberg U, Nordenskjöld A, Wester T. Intestinal malrotation in children: clinical presentation and outcomes. *Eur J Pediatr Surg*. 2024;34(3):228-235.",
 "gomaa2024": "Gomaa IA, Mirande MD, Armenia SJ, Aboelmaaty S, Dozois EJ, Perry WRG. Intestinal malrotation in the adult population: diagnosis, management, and outcomes after laparoscopic Ladd procedure. *J Gastrointest Surg*. 2024;28(8):1339-1343.",
 "duy2025": "Duy HP, Manh HV, Tran NX, Yoshimura S, Okata Y. Risk factors for postoperative volvulus and its laparoscopic management following laparoscopic Ladd's procedure in pediatric patients with intestinal malrotation: a single-center, retrospective cohort study. *J Pediatr Surg*. 2025;60(7):162356.",
 "zeng2025": "Zeng X, Lian N, Wang X, Du D. Abnormal anatomical landmarks: the guide points of laparoscopic Ladd's surgery for neonatal congenital intestinal malrotation. *Surg Endosc*. 2025;39(7):4386-4391.",
 "takamoto2026": "Takamoto N, Aso S, Konishi T, Fujiogi M, Kutsukake M, Yanagida Y, et al. Effect of adhesion barrier use during Ladd procedure for intestinal malrotation on postoperative midgut volvulus and postoperative small-bowel obstruction: a retrospective cohort study using a national inpatient database. *J Am Coll Surg*. 2026;242(5):1279-1288.",
 "eksarko2013": "Eksarko P, Nazir S, Kessler E, LeBlanc P, Zeidman M, Asarian AP, et al. Duodenal web associated with malrotation and review of literature. *J Surg Case Rep*. 2013;2013(12):rjt110.",
 "bass1998": "Bass KD, Rothenberg SS, Chang JH. Laparoscopic Ladd's procedure in infants with malrotation. *J Pediatr Surg*. 1998;33(2):279-281.",
 # —— 方法学 ——
 "strobe2007": "von Elm E, Altman DG, Egger M, Pocock SJ, Gøtzsche PC, Vandenbroucke JP; STROBE Initiative. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *Lancet*. 2007;370(9596):1453-1457.",
 "byrt1993": "Byrt T, Bishop J, Carlin JB. Bias, prevalence and kappa. *J Clin Epidemiol*. 1993;46(5):423-429.",
 "firth1993": "Firth D. Bias reduction of maximum likelihood estimates. *Biometrika*. 1993;80(1):27-38.",
 "holm1979": "Holm S. A simple sequentially rejective multiple test procedure. *Scand J Stat*. 1979;6(2):65-70.",
 "aalen1978": "Aalen OO, Johansen S. An empirical transition matrix for non-homogeneous Markov chains based on censored observations. *Scand J Stat*. 1978;5(3):141-150.",
 "newcombe1998": "Newcombe RG. Interval estimation for the difference between independent proportions: comparison of eleven methods. *Stat Med*. 1998;17(8):873-890.",
 "austin2009": "Austin PC. Balance diagnostics for comparing the distribution of baseline covariates between treatment groups in propensity-score matched samples. *Stat Med*. 2009;28(25):3083-3107.",
}

t = io.open(SRC, encoding="utf-8").read()
body, _, _ = t.partition("## References")

# 本脚本【只能对 key 版正文运行一次】。跑完之后正文里的引用已变成数字，
# 再跑一次就只剩零星 key 能被匹配，文献表会被截断——2026-07-26 就这么翻过一次车。
# 故先检查：正文若已含数字引用，直接拒绝运行。
if re.search(r"\[[0-9]+(?:,[0-9]+)*\]", body):
    raise SystemExit("正文已是数字引用（本脚本已运行过）。若要重建，请先把数字还原为 key。")

PAT = re.compile(r"\[((?:[a-z]+[0-9]{4})(?:\s*,\s*[a-z]+[0-9]{4})*)\]")
order, seen = [], set()
for m in PAT.finditer(body):
    for k in [x.strip() for x in m.group(1).split(",")]:
        if k not in REFS:
            raise SystemExit("未知引用键：%s" % k)
        if k not in seen:
            seen.add(k); order.append(k)
num = {k: i + 1 for i, k in enumerate(order)}

unused = [k for k in REFS if k not in seen]
if unused:
    print("[警告] 列而未引，已从文献表剔除：", unused)

out = PAT.sub(lambda m: "[" + ",".join(str(num[x.strip()]) for x in m.group(1).split(",")) + "]", body)
lines = ["%d. %s" % (num[k], REFS[k]) for k in order]
io.open(SRC, "w", encoding="utf-8").write(out + "## References\n\n" + "\n".join(lines) + "\n")

print("参考文献 %d 条，按正文首次引用顺序编号。" % len(order))
yrs = sorted(int(re.search(r"\b(19|20)\d{2}\b", REFS[k]).group(0)) for k in order)
print("年份分布：最早 %d，最新 %d；2020 年及以后 %d 条（共 %d）"
      % (yrs[0], yrs[-1], sum(1 for y in yrs if y >= 2020), len(yrs)))
