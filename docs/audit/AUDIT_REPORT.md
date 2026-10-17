# Clinical Accuracy Audit: RadOnc Sub-I Companion

Audit dates: 2026-10-16 to 2026-10-17. Reviewer: Claude (AI-assisted). **This audit is not a substitute for review by a radiation oncologist, and the site is not fully verified.** 12 high-risk claims are awaiting expert review, and 3257 high-risk claims were read without a source being attached to each one.

## How to read this

- Every clinical statement in the source files is a row in `claim_ledger.csv` with a stable ID, file, JSON path, section, risk tier, and status.
- Review results live in `findings.json`. Each finding names the claims it covers, the sources checked (with PMID/DOI where one exists), the proposed correction, and whether it was implemented. `tools/audit/extract_claims.py` merges findings into the ledger.
- Statuses: **Verified** = a cited source was retrieved and supports the exact statement; **Revise** = the evidence supports a change; **Expert review** = sources conflict or could not be accessed; **Unable to verify** = no accessible source; **Pending** = not yet checked against a source.
- `first_pass` records whether the claim was read line by line in this audit. "Read, no discrepancy found" is **not** verification: no source was attached to that claim.
- Risk tiers come from keyword rules (`extract_claims.py`). They are a triage tool, so expect some miscategorized rows.
- Regenerate everything: `python3 tools/audit/extract_claims.py && python3 tools/audit/make_report.py`.

## Summary

| | Count |
|---|---|
| Claims inventoried | 11,517 |
| HIGH / MODERATE / LOWER | 3,295 / 2,981 / 5,241 |
| HIGH-risk claims read in this audit | 3,293 of 3,295 |
| All claims read in this audit | 3,379 of 11,517 |
| Findings | 31 |
| Verified errors or misleading statements | 14 |
| Corrections implemented | 17 |
| Items needing a radiation oncologist | 10 |
| Trial citations checked (Europe PMC) | 155 named trials + 27 inline PubMed links + 101 caption PMC IDs |

Claim status after this audit: Pending 11,473, Verified 30, Expert review 14. HIGH-risk: Pending 3,257, Verified 26, Expert review 12.

**Concurrent edits.** Two other Claude sessions edited this folder during the audit (Before You Start revisions, which added `src/data/sources.json` and retired `src/data/docs/overview.json`; and the Palliative & Benign rewrite). The ledger reflects the working tree on 2026-10-17, including their uncommitted work. Palliative claims changed after the first read were read again.

## 1. Claim ledger

`docs/audit/claim_ledger.csv`: 11,517 rows. Columns: claim_id, risk, status, first_pass, site, source_file, edit_in (the file a correction must be made in, e.g. a case generator), json_path, section, unit_kind, statement, categories, disease_context, treatment_context, supporting_source, verification_findings, proposed_correction, implemented, related_claims, finding_ids, date_reviewed, reviewer.

Claims by site: breast 1,169, thoracic 1,524, cns 1,372, gi 1,330, prostate 1,417, gyn 1,392, headneck 1,414, palliative 1,063, overview 836.

## 2. Prioritized high-risk claims requiring review

`docs/audit/high_risk_review_queue.csv` ranks all 3,295 HIGH claims: open findings first, then by category (emergency, organ-at-risk constraint, dose/fractionation, brachytherapy, re-irradiation, staging, indication, serious toxicity), with interactive tools, case answers, flashcards, and tables ahead of prose. Suggested order for a physician reviewer:

1. The open items in section 9 (expert judgment).
2. Organ-at-risk constraint tables (thoracic, CNS, GYN, GI, prostate, Before You Start planning reference).
3. Dose/fractionation tables and case 'Dose' steps for every site.
4. Staging tables and the interactive builders (tests in section 10 cover the builders' logic only, not the prose around them).
5. Emergency pathways (cord compression, SVC, bleeding) in Palliative & Benign and CNS.

## 3. Verified errors and misleading statements

**F-TH-01** (HIGH risk, error, status: Verified)

Lung stage builder grid assigns T3 N2a to IIIB (should be IIIA) and T3-4 N2b to IIIC (should be IIIB). In the AJCC/UICC 9th edition, T3N2a moved to IIIA, T2-T4 N2b are IIIB, and IIIC is T3-4 N3 only. Every quiz patient generated with these combinations is graded with the wrong answer.

Location: `src/app.js` (lungStageGroup) [THO-fd1733d3]

Original text: "N2a: { T1:"IIB"" / "N2b: { T1:"IIIA""

Correction: N2a: { T1:"IIB", T2:"IIIA", T3:"IIIA", T4:"IIIB" }; N2b: { T1:"IIIA", T2:"IIIB", T3:"IIIB", T4:"IIIB" }

Implemented: Yes, 2026-10-17: src/app.js lungStageGroup grid. Claim now matches the cited source.

Sources:
- [IASLC Lung Cancer Staging Project: Proposals for Revision of the TNM Stage Groups in the Forthcoming (Ninth) Edition (2024) PMID 38447919 doi:10.1016/j.jtho.2024.02.011](https://pubmed.ncbi.nlm.nih.gov/38447919/)
- [Radiopaedia: Lung cancer staging (IASLC 9th edition) (2025)](https://radiopaedia.org/articles/lung-cancer-staging-iaslc-9th-edition)

**F-TH-02** (HIGH risk, error, status: Verified)

Thoracic Workup & Staging AJCC stage-group table lists T3 N2a under IIIB and T3-4 N2b under IIIC. Under the 9th edition T3N2a is IIIA, T3-4 N2b is IIIB, and IIIC is T3-4 N3 only. Disagrees with the abstract of the IASLC proposal the page is based on.

Location: `src/data/docs/thoracic.json` (Workup & Staging > Stage groups > AJCC Staging Tables) [THO-d8737d39]

Original text: "IIIA | T4 N0; T3-4 N1; T2 N2a; T1 N2b" / "IIIB | T3-4 N2a; T2 N2b; T1-2 N3" / "IIIC | T3-4 N2b; T3-4 N3"

Correction: IIIA | T4 N0; T3-4 N1; T2-3 N2a; T1 N2b. IIIB | T4 N2a; T2-4 N2b; T1-2 N3. IIIC | T3-4 N3.

Implemented: Yes, 2026-10-17: src/data/docs/thoracic.json AJCC stage-group table. Claim now matches the cited source.

Sources:
- [IASLC proposals for stage groups, ninth edition (2024) PMID 38447919 doi:10.1016/j.jtho.2024.02.011](https://pubmed.ncbi.nlm.nih.gov/38447919/)

**F-TH-03** (HIGH risk, error, status: Verified)

Thoracic Case 3 stages a 5.2 cm tumor with a single subcarinal station as T3 N2a = Stage IIIB. Under the AJCC 9th edition (which the case says it uses) T3 N2a is Stage IIIA. Treatment answer (unresectable -> chemoRT -> durvalumab) is unaffected.

Location: `tools/cases/thoracic_cases.py` (Case 3: Cough and Blood > step 1: Stage) [THO-d428b9f1]

Original text: "T3 N2a M0, Stage IIIB" / "T3 N2a is stage IIIB"

Correction: Answer: T3 N2a M0, Stage IIIA. Explanation: 'T3 N2a is stage IIIA in the 9th edition (it was IIIB in the 8th).'

Implemented: Yes, 2026-10-17: tools/cases/thoracic_cases.py Case 3 (regenerated). Claim now matches the cited source.

Sources:
- [IASLC proposals for stage groups, ninth edition (2024) PMID 38447919 doi:10.1016/j.jtho.2024.02.011](https://pubmed.ncbi.nlm.nih.gov/38447919/)

**F-TH-04** (MODERATE risk, misleading, status: Verified)

Flashcard extra says SWOG 9416 achieved 'complete resection in over 90%'. In the trial, 83 of 110 eligible patients (76%) had complete resection; 83 of 88 who went to thoracotomy (94%). The over-90% figure applies only to patients who reached surgery. 5-year OS was 44% overall.

Location: `src/data/decks/thoracic.json` (Flashcard thx-44 (Treatment Paradigms)) [THO-1f0e18e9]

Original text: "complete resection in over 90%"

Correction: SWOG 9416 / INT 0160: complete resection in 76% of all patients (over 90% of those who reached surgery); 5-year survival 44%.

Implemented: Yes, 2026-10-17: src/data/decks/thoracic.json thx-44 extra. Claim now matches the cited source.

Sources:
- [Rusch VW et al. Induction chemoradiation and surgical resection for superior sulcus NSCLC: long-term results of SWOG 9416 (INT 0160). J Clin Oncol (2007) PMID 17235046 doi:10.1200/jco.2006.08.2826](https://pubmed.ncbi.nlm.nih.gov/17235046/)

**F-TH-06** (LOWER risk, error, status: Verified)

Imaging plate says the upper border of the left brachiocephalic vein is where station 2R ends and 4R begins. The IASLC map uses the caudal (lower) margin of the left brachiocephalic vein where it crosses the trachea.

Location: `src/data/imaging/thoracic.json` (Imaging > Axial: Great Vessels (T2-T3) > Left Brachiocephalic Vein) [THO-a5e116d7]

Original text: "Its upper border is where station 2R ends and 4R begins"

Correction: Its lower edge, where it crosses the trachea, is where station 2R ends and 4R begins.

Implemented: Yes, 2026-10-17: src/data/imaging/thoracic.json left brachiocephalic vein hotspot. Claim now matches the cited source.

Sources:
- [Rusch VW et al. The IASLC lung cancer staging project: a proposal for a new international lymph node map. J Thorac Oncol (2009) PMID 19357537 doi:10.1097/jto.0b013e3181a0d82e](https://pubmed.ncbi.nlm.nih.gov/19357537/)

**F-TH-07** (MODERATE risk, misleading, status: Verified)

Thoracic reading and Case 2 say CALGB 140503 showed segmentectomy was noninferior to lobectomy. The trial randomized lobar vs sublobar resection (wedge or segmentectomy) for peripheral T1a N0 tumors <=2 cm; sublobar resection was noninferior for DFS. JCOG0802 is the trial that compared segmentectomy specifically and showed better OS.

Location: `tools/cases/thoracic_cases.py` (Case 2: The Fit Golfer > step 1: Treatment) [THO-9186ffe6]; `src/data/docs/thoracic.json` (Treatment Paradigms > The Role of Surgery) [THO-9b576c0a]

Original text: "CALGB 140503 showed it was noninferior to lobectomy" / "CALGB 140503 showed it was noninferior to lobectomy"

Correction: CALGB 140503 showed sublobar resection (segmentectomy or wedge) was noninferior to lobectomy, and JCOG0802 showed better overall survival with segmentectomy.

Implemented: Yes, 2026-10-17: docs/thoracic.json + tools/cases/thoracic_cases.py Case 2. Claim now matches the cited source.

Sources:
- [Altorki N et al. Lobar or Sublobar Resection for Peripheral Stage IA Non-Small-Cell Lung Cancer. N Engl J Med (2023) PMID 36780674 doi:10.1056/nejmoa2212083](https://pubmed.ncbi.nlm.nih.gov/36780674/)

**F-BR-03** (MODERATE risk, misleading, status: Verified)

Quiz answer says high-risk screening after childhood mantle RT starts '8 years after radiation or at age 25'. The harmonized guideline starts surveillance at age 25 or 8 years after radiation, whichever comes LAST; 'or' reads as whichever comes first.

Location: `src/app.js` (breast-epi) [BRE-b7db9c38]

Original text: "usually starting 8 years after radiation or at age 25"

Correction: usually starting at age 25 or 8 years after radiation, whichever comes later

Implemented: Yes, 2026-10-17: src/app.js breast-epi quiz. Claim now matches the cited source.

Sources:
- [Mulder RL et al. Recommendations for breast cancer surveillance for female survivors of childhood, adolescent, and young adult cancer given chest radiation (IGHG). Lancet Oncol (2013) PMID 24275135 doi:10.1016/s1470-2045(13)70303-6](https://pubmed.ncbi.nlm.nih.gov/24275135/)

**F-GI-01** (HIGH risk, error, status: Verified)

GI Case 4 stages anal cancer T3 N1a M0 as Stage IIIC. The GI cases and reading state that anal cancer uses the AJCC version 9 system, where T3 N0-1 is Stage IIIA (IIIC is T4 N1). IIIC is the AJCC 8th edition grouping. Contradicts the reading's own stage-group row. Treatment answer is unaffected.

Location: `tools/cases/gi_cases.py` (Case 4: The Groin Node > step 2: Stage) [GI-2570ba06]

Original text: "T3 N1a M0, Stage IIIC"

Correction: Answer: T3 N1a M0, Stage IIIA (AJCC version 9: T3 N0-1 is IIIA; it was IIIC in the 8th edition). Update the distractor list so 'Stage IIIA' is the correct choice.

Implemented: Yes, 2026-10-17: tools/cases/gi_cases.py Case 4 (regenerated). Claim now matches the cited source.

Sources:
- [Janczewski LM et al. Survival outcomes used to generate version 9 AJCC staging system for anal cancer. CA Cancer J Clin (2023) PMID 37114458 doi:10.3322/caac.21780](https://pubmed.ncbi.nlm.nih.gov/37114458/)
- [Data-driven optimization of version 9 AJCC staging system for anal cancer. Cancer (2024) PMID 38140735 doi:10.1002/cncr.35155](https://pubmed.ncbi.nlm.nih.gov/38140735/)

**F-GI-02** (MODERATE risk, misleading, status: Verified)

Case 7, the GI reading, and flashcard gix-51 say RTOG 1112 'improved overall and progression-free survival'. In the published trial (closed early), OS for SBRT + sorafenib vs sorafenib was 15.8 vs 12.3 months, HR 0.77, one-sided P = .06 (did not meet the prespecified threshold); OS was significant only after adjusting for stratification factors (HR 0.72, P = .04). PFS clearly improved (9.2 vs 5.5 months, HR 0.55, P < .001). Sorafenib is also no longer the usual first-line systemic therapy, which limits how directly the result applies today.

Location: `tools/cases/gi_cases.py` (Case 7: The Surveillance Ultrasound > step 4: Trial) [GI-c7405f58]; `src/data/decks/gi.json` (Flashcard gix-51 (Treatment Paradigms)) [GI-b5a6f3ad]; `src/data/docs/gi.json` (Treatment Paradigms > Paradigm 5: Liver (HCC): The Liver Is the OAR) [GI-51ff4c3d]

Original text: "adding SBRT to sorafenib improved overall and progression-free survival" / "RTOG 1112: SBRT + sorafenib improved outcomes" / "Adding SBRT to sorafenib improved outcomes in unresectable HCC"

Correction: Case 7 question: 'Which trial found that adding SBRT to sorafenib improved progression-free survival, with a trend toward better overall survival, in locally advanced HCC?' Explanation: 'OS 15.8 vs 12.3 months (borderline; significant only after adjustment); PFS 9.2 vs 5.5 months.'

Implemented: Yes, 2026-10-17: gi_cases.py Case 7, decks/gi.json gix-51, docs/gi.json. Claim now matches the cited source.

Sources:
- [Dawson LA et al. Stereotactic Body Radiotherapy vs Sorafenib Alone in Hepatocellular Carcinoma: The NRG Oncology/RTOG 1112 Phase 3 Randomized Clinical Trial. JAMA Oncol (2025) PMID 39699905 doi:10.1001/jamaoncol.2024.5403](https://pubmed.ncbi.nlm.nih.gov/39699905/)

**F-PR-01** (HIGH risk, error, status: Verified)

Prostate Case 5 defines NCCN very high risk as '2 or more of: T3-4, Gleason 8-10, PSA 40 or more'. Those are the STAMPEDE criteria for adding abiraterone, not the NCCN very-high-risk definition (T3b-T4, primary Gleason pattern 5, >4 cores with GG4-5, or 2-3 high-risk features: T3a, GG4-5, PSA >20). Contradicts the prostate reading's risk table, flashcard prx-36, and the risk builder. The answer (very high risk) is still correct for this patient.

Location: `tools/cases/prostate_cases.py` (Case 5: A Hard Gland and a Family History > step 3: Risk group) [PRO-2efb9aa9]

Original text: "Very high risk is 2 or more of: T3-4, Gleason 8-10, PSA 40 or more"

Correction: Very high risk means T3b-T4, primary Gleason pattern 5, more than 4 cores with Grade Group 4-5, or 2-3 high-risk features (T3a, GG4-5, PSA over 20). He has T3b and two high-risk features (GG5, PSA 45). He also meets the STAMPEDE criteria for abiraterone (2 or more of T3-4, Gleason 8-10, PSA 40 or more).

Implemented: Yes, 2026-10-17: tools/cases/prostate_cases.py Case 5 (regenerated). Claim now matches the cited source.

Sources:
- [Attard G et al. Abiraterone acetate and prednisolone with or without enzalutamide for high-risk non-metastatic prostate cancer: a meta-analysis of two randomised controlled trials (STAMPEDE). Lancet (eligibility: node-positive or >=2 of T3/4, Gleason 8-10, PSA >=40) (2022) PMID 34953525 doi:10.1016/S0140-6736(21)02437-5](https://pubmed.ncbi.nlm.nih.gov/34953525/)
- [NCCN Clinical Practice Guidelines: Prostate Cancer (risk stratification table; login required, not accessed) (current)](https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1459)

**F-GY-01** (HIGH risk, misleading, status: Verified)

The Sedlis/Peters builder says adjuvant chemoradiation for Peters criteria is '45-50.4 Gy + weekly cisplatin (GOG 109)'. GOG 109/SWOG 8797/RTOG 91-12 gave 49.3 Gy with cisplatin 70 mg/m2 plus 96-hour 5-FU every 3 weeks for 4 cycles (2 concurrent). Weekly cisplatin is common modern practice, extrapolated from the definitive-setting trials, but it is not what GOG 109 tested.

Location: `src/app.js` (POSTOP_TX) [GYN-ba4cbaa4]

Original text: "45-50.4 Gy + weekly cisplatin (GOG 109)"

Correction: Adjuvant pelvic chemoradiation: 45-50.4 Gy with concurrent cisplatin-based chemo (GOG 109 used cisplatin + 5-FU; weekly cisplatin is the common modern choice).

Implemented: Yes, 2026-10-17: src/app.js POSTOP_TX peters. Claim now matches the cited source.

Sources:
- [Peters WA 3rd et al. Concurrent chemotherapy and pelvic radiation therapy compared with pelvic radiation therapy alone as adjuvant therapy after radical surgery in high-risk early-stage cancer of the cervix. J Clin Oncol 2000;18:1606-13 (reprinted J Clin Oncol 2023) (2000) PMID 10764420 doi:10.1200/JCO.2000.18.8.1606](https://pubmed.ncbi.nlm.nih.gov/10764420/)

**F-OV-01** (MODERATE risk, error, status: Revise)

[Retired file, not user-facing] Radiation Physics reading says 'a 9 MeV electron beam has a Dmax of about 4.5 cm and a practical range of about 4.5 cm'. By the page's own rule of thumb (Dmax ~ E/5) Dmax is about 1.8-2 cm; 4.5 cm is the practical range (E/2). As written, Dmax and the practical range coincide, which is physically impossible and contradicts the preceding sentence.

Location: `docs/legacy-overview-docs.json (moved out of src/data by the Before You Start session on 2026-10-16; not rendered in the app)`

Correction: For example, a 9 MeV electron beam has a Dmax of about 2 cm, a 90% isodose depth of about 2.8 cm, and a practical range of about 4.5 cm.

Sources:
- Internal arithmetic: the same paragraph defines Dmax ~ E/5, R90 ~ E/3.2-3.3, Rp ~ E/2 (9/5 = 1.8 cm)

**F-OV-02** (MODERATE risk, error, status: Revise)

[Retired file, not user-facing] QUANTEC table in the Common Dose Constraints reading lists 'Bilateral parotid | Mean < 26 Gy | <25% long-term salivary function'. QUANTEC gives a mean dose of about 25 Gy for both glands (or about 20 Gy for one gland) to avoid severe xerostomia, defined as long-term salivary function below 25% of baseline; the 25% is the definition of the endpoint, not the risk. (The 26 Gy figure is the older Eisbruch threshold quoted correctly in the flashcard.)

Location: `docs/legacy-overview-docs.json (moved out of src/data by the Before You Start session on 2026-10-16; not rendered in the app)`

Correction: Parotids | Mean < 25 Gy (both) or < 20 Gy (one) | <20% risk of severe xerostomia (salivary function <25% of baseline)

Sources:
- [Deasy JO et al. Radiotherapy dose-volume effects on salivary gland function (QUANTEC). Int J Radiat Oncol Biol Phys (2010) PMID 20171519 doi:10.1016/j.ijrobp.2009.06.090](https://pubmed.ncbi.nlm.nih.gov/20171519/)

**F-TH-08** (MODERATE risk, misleading, status: Verified)

Flashcard thx-50 says 'Gomez and SABR-COMET showed better survival', and the reading says the same without qualification. Both were randomized phase II trials. SABR-COMET used a screening design with two-sided alpha 0.20 (OS 41 vs 28 months, HR 0.57, p=0.090), with 3 of 66 SABR-arm treatment-related deaths. Gomez (49 patients, closed early, p<.10 counted as significant) showed OS 41.2 vs 17.0 months, p=.017. The reading's Case 7 already labels Gomez as phase II. Raised by the Before You Start session; confirmed here against the abstracts.

Location: `tools/cases/thoracic_cases.py` (Case 7: Four Months Later > step 6: Trial) [THO-af853347]; `src/data/decks/thoracic.json` (Flashcard thx-50 (Treatment Paradigms)) [THO-f5aad18c]; `src/data/docs/thoracic.json` (Treatment Paradigms > Treat every site) [THO-5f26d715]

Original text: "Gomez and SABR-COMET showed better survival" / "Gomez (phase II) and SABR-COMET showed better survival"

Correction: Two randomized phase II trials (Gomez; SABR-COMET, which used a relaxed p<0.20 threshold) showed longer survival with local therapy to every site; SABR-COMET had about 4.5% treatment-related deaths. Phase III trials are ongoing.

Implemented: Yes, 2026-10-17: decks/thoracic.json thx-50, docs/thoracic.json, thoracic Case 7. Claim now matches the cited source.

Sources:
- [Palma DA et al. SABR-COMET: a randomised, phase 2, open-label trial. Lancet (2019) PMID 30982687 doi:10.1016/s0140-6736(18)32487-5](https://pubmed.ncbi.nlm.nih.gov/30982687/)
- [Gomez DR et al. Local Consolidative Therapy vs Maintenance Therapy or Observation for Oligometastatic NSCLC: Long-Term Results. J Clin Oncol (2019) PMID 31067138 doi:10.1200/jco.19.00201](https://pubmed.ncbi.nlm.nih.gov/31067138/)

## 4. Outdated or weakly supported claims

**F-BR-02** (HIGH risk, outdated, status: Verified)

Breast Case 4 says a 44-year-old is 'too young for partial breast RT'. The 2024 ASTRO PBI guideline lowered the age criterion to 40; her tumor is a poor fit for PBI because it is grade 3 and larger than 2 cm, not because of her age. The reading's description of PBI candidates as 'older' has the same problem.

Location: `tools/cases/breast_cases.py` (Case 4: The Left-Sided Plan > step 3: Fields) [BRE-9ccd3b0e]; `src/data/docs/breast.json` (Treatment Paradigms > Paradigm 1: Invasive Cancer After Lumpectomy) [BRE-99f65663]

Correction: Case 4: 'Her grade 3 tumor over 2 cm makes partial breast RT a poor fit, and she is too young and too high-risk for omission.' Reading: 'low-risk patients (generally 40 or older): small (<=2 cm), N0, ER+, lower grade, clear margins.'

Implemented: Yes, 2026-10-17: tools/cases/breast_cases.py Case 4 + docs/breast.json. Claim now matches the cited source.

Sources:
- [Shaitelman SF et al. Partial Breast Irradiation for Patients With Early-Stage Invasive Breast Cancer or DCIS: An ASTRO Clinical Practice Guideline. Pract Radiat Oncol (2024) PMID 37977261 doi:10.1016/j.prro.2023.11.001](https://pubmed.ncbi.nlm.nih.gov/37977261/)
- [Impact of the ASTRO 2024 Guideline on PBI Eligibility (KROG 24-01): age criterion expanded from 50 to 40. Pract Radiat Oncol (2025) PMID 39667667 doi:10.1016/j.prro.2024.11.007](https://pubmed.ncbi.nlm.nih.gov/39667667/)

**F-HN-01** (HIGH risk, outdated, status: Expert review)

Nasopharynx staging throughout (reading tables, Case 4, flashcard hn-42, quiz 'M-stage is simply M0 or M1') uses AJCC 8th edition. The AJCC/UICC 9th version for NPC (2024) adds advanced radiologic ENE as an N3 criterion, regroups nonmetastatic disease into stages I-III (I = T1-2 N0-1 with IA/IB, II = T3 or N2, III = T4 or N3), and splits M1 into M1a (<=3 lesions, IVA) and M1b (>3, IVB). The content is correct for the 8th edition and labeled as such in Case 4, but readers are not told a newer version exists. Whether to switch editions (and match NCCN's current choice) is an editorial/clinical decision.

Location: `src/app.js` (hn-staging) [HEA-6b1aae88]; `tools/cases/headneck_cases.py` (Case 4: The Ear That Won't Clear > step 3: Stage) [HEA-510c4d2e]; `src/data/decks/headneck.json` (Flashcard hn-42 (Workup & Staging)) [HEA-5b60b6c7]; `src/data/docs/headneck.json` (Workup & Staging > Nasopharynx > N category) [HEA-a8fcb5cd]

Correction: Minimum: add an edition note to the NPC staging table ('AJCC 8th edition shown; the AJCC/UICC 9th version (2024) adds advanced radiologic ENE to N3, regroups stages I-III, and splits M1a/M1b'), and qualify the quiz answer ('M0 or M1 for most H&N sites in the 8th edition; NPC version 9 splits M1'). Full migration to version 9 needs radiation oncologist sign-off and a check of the current NCCN edition.

Sources:
- [Pan JJ et al. Ninth Version of the AJCC and UICC Nasopharyngeal Cancer TNM Staging Classification. JAMA Oncol (2024) PMID 39388190 doi:10.1001/jamaoncol.2024.4354](https://pubmed.ncbi.nlm.nih.gov/39388190/)

**F-OV-05** (MODERATE risk, weak, status: Verified)

Before You Start flashcard ov-95 gives the parotid goal as 'mean dose under about 26 Gy'. 26 Gy is the older Eisbruch threshold; QUANTEC recommends about 25 Gy mean when both glands are spared, or about 20 Gy for one gland. Not wrong, but less precise than the consensus source.

Correction: Back: 'Mean dose under about 25 Gy (both glands) or 20 Gy (at least one gland)'. Extra: add 'Older series used 26 Gy.' (Owned by the Before You Start session; proposed, not edited here.)

Implemented: Yes, 2026-10-17, by the Before You Start session: ov-95 now reads about 25 Gy for both parotids or 20 Gy for one (QUANTEC), with 'many protocols use about 26 Gy' in the extra.

Sources:
- [Deasy JO et al. Radiotherapy dose-volume effects on salivary gland function (QUANTEC). Int J Radiat Oncol Biol Phys (2010) PMID 20171519 doi:10.1016/j.ijrobp.2009.06.090](https://pubmed.ncbi.nlm.nih.gov/20171519/)

## 5. References: missing, broken, or mismatched

- **Trial citations.** At the start, `curriculum.json` named 155 trials with no PMID/DOI. During the audit the Before You Start session added `src/data/sources.json`. `docs/audit/trial_references.csv` gives an independent primary-report lookup for all 155 (Europe PMC: PMID, DOI, year, journal, title).
- **Inline PubMed links.** `docs/audit/pubmed_link_check.csv`: all 27 linked PMIDs resolve, and each title matches its link text.
- **Figure captions.** `docs/audit/caption_reference_check.csv`: all 101 cited PMC IDs exist; attribution issues are listed below.
- **Guideline versions.** NCCN guideline versions quoted in the GYN reading (e.g., v2.2026, v3.2026) could not be checked because NCCN requires a login. Status: Unable to verify.

**F-REF-01** (MODERATE risk, reference, status: Verified)

At the start of the audit, curriculum.json listed 155 trial names with no PMID, DOI, or link. The Before You Start session added src/data/sources.json + tools/sources.py during the audit (uncommitted). All 155 trial PMIDs in it resolve in Europe PMC, and every stored title matches the real paper title (2 differences are HTML markup only). The 4 guideline entries without a pmid field point to correct PubMed/NICE URLs. An independent lookup (docs/audit/trial_references.csv) agrees.

Sources:
- [Europe PMC REST API lookups (docs/audit/trial_references.csv) (2026)](https://www.ebi.ac.uk/europepmc/webservices/rest/)

**F-REF-02** (LOWER risk, reference, status: Revise)

Figure caption attribution: all 101 cited PMC IDs exist. PMC6661304 is credited to 'Hashmi R, Sectional Anatomy Quiz IV' but its first author is Lathif. PMC10847842 (Crosetti) is cited as 2024; the record says 2023. PMC7874055 (Sardaro) is cited as 2021; the record says 2020 (likely epub vs issue year). Ten captions give the journal and year without an author. See docs/audit/caption_reference_check.csv.

Correction: Fix the PMC6661304 author; add first authors to the ten unattributed captions; align years with the PubMed record.

Sources:
- docs/audit/caption_reference_check.csv (Europe PMC lookups) (2026)

**F-REF-03** (MODERATE risk, reference, status: Verified)

src/data/sources.json linked three trials to NEJM correspondence instead of the trial reports (Perry 28564572, RTOG 9802 27518677, MA.20 26535517). Fixed by the owning session. This audit's own trial table had the same MA.20 letter, now corrected to 26200977.

Correction: In tools/sources.py: Perry -> 28296618; RTOG 9802 -> 27050206. Reported to the owning session.

Implemented: Yes, 2026-10-17, by the Before You Start session in tools/sources.py: Perry -> 28296618, RTOG 9802 -> 27050206, plus a third letter it found (MA.20 26535517 -> 26200977). That session's verifier now rejects Letter/Comment publication types.

Sources:
- [Perry JR et al. Short-Course Radiation plus Temozolomide in Elderly Patients with Glioblastoma. N Engl J Med (2017) PMID 28296618 doi:10.1056/nejmoa1611977](https://pubmed.ncbi.nlm.nih.gov/28296618/)
- [Buckner JC et al. Radiation plus Procarbazine, CCNU, and Vincristine in Low-Grade Glioma. N Engl J Med (2016) PMID 27050206 doi:10.1056/nejmoa1500925](https://pubmed.ncbi.nlm.nih.gov/27050206/)

## 6. Contradictions between readings, flashcards, cases, and tools

**F-TH-05** (HIGH risk, contradiction, status: Verified)

Thoracic imaging plate calls SVC compression 'an urgent indication for RT', contradicting thoracic Case 8 and the Palliative & Benign content, which correctly teach that SVC syndrome without airway compromise is not a radiation emergency: tissue diagnosis first, endovascular stent for severe symptoms.

Location: `src/data/imaging/thoracic.json` (Imaging > Axial: Aortic Arch (T4) > Superior Vena Cava (SVC)) [THO-7cc7d994]

Correction: Tumor or bulky 4R nodes can compress it (SVC syndrome). Get tissue first; severe symptoms are relieved fastest with a stent, and RT follows the histology.

Implemented: Yes, 2026-10-17: src/data/imaging/thoracic.json SVC hotspot. Claim now matches the cited source.

Sources:
- [Wilson LD, Detterbeck FC, Yahalom J. Superior vena cava syndrome with malignant causes. N Engl J Med (2007) PMID 17476012 doi:10.1056/nejmcp067190](https://pubmed.ncbi.nlm.nih.gov/17476012/)

**F-BR-01** (HIGH risk, contradiction, status: Verified)

Breast Case 6 explanation says PMRT 'is indicated for T3-T4 tumors', which treats T3N0 as a firm indication. The breast reading's NCCN table and flashcard br-25 say T3N0 is individualized, and the flashcard lists 'T3 with positive nodes' as the clear indication.

Location: `tools/cases/breast_cases.py` (Case 6: After the Mastectomy > step 2: PMRT) [BRE-658b36c6]

Correction: PMRT is indicated for T4 tumors, T3 with positive nodes, 4 or more positive nodes, or a positive margin; it is strongly considered for 1-3 nodes, and T3N0 is individualized.

Implemented: Yes, 2026-10-17: tools/cases/breast_cases.py Case 6 (regenerated). Claim now matches the cited source.

Sources:
- [Recht A et al. Postmastectomy Radiotherapy: An ASCO, ASTRO, and SSO Focused Guideline Update. J Clin Oncol (2016) PMID 27646947 doi:10.1200/JCO.2016.69.1188](https://pubmed.ncbi.nlm.nih.gov/27646947/)

**F-GI-01** (HIGH risk, error, status: Verified)

GI Case 4 stages anal cancer T3 N1a M0 as Stage IIIC. The GI cases and reading state that anal cancer uses the AJCC version 9 system, where T3 N0-1 is Stage IIIA (IIIC is T4 N1). IIIC is the AJCC 8th edition grouping. Contradicts the reading's own stage-group row. Treatment answer is unaffected.

Location: `tools/cases/gi_cases.py` (Case 4: The Groin Node > step 2: Stage) [GI-2570ba06]

Correction: Answer: T3 N1a M0, Stage IIIA (AJCC version 9: T3 N0-1 is IIIA; it was IIIC in the 8th edition). Update the distractor list so 'Stage IIIA' is the correct choice.

Implemented: Yes, 2026-10-17: tools/cases/gi_cases.py Case 4 (regenerated). Claim now matches the cited source.

Sources:
- [Janczewski LM et al. Survival outcomes used to generate version 9 AJCC staging system for anal cancer. CA Cancer J Clin (2023) PMID 37114458 doi:10.3322/caac.21780](https://pubmed.ncbi.nlm.nih.gov/37114458/)
- [Data-driven optimization of version 9 AJCC staging system for anal cancer. Cancer (2024) PMID 38140735 doi:10.1002/cncr.35155](https://pubmed.ncbi.nlm.nih.gov/38140735/)

**F-PR-01** (HIGH risk, error, status: Verified)

Prostate Case 5 defines NCCN very high risk as '2 or more of: T3-4, Gleason 8-10, PSA 40 or more'. Those are the STAMPEDE criteria for adding abiraterone, not the NCCN very-high-risk definition (T3b-T4, primary Gleason pattern 5, >4 cores with GG4-5, or 2-3 high-risk features: T3a, GG4-5, PSA >20). Contradicts the prostate reading's risk table, flashcard prx-36, and the risk builder. The answer (very high risk) is still correct for this patient.

Location: `tools/cases/prostate_cases.py` (Case 5: A Hard Gland and a Family History > step 3: Risk group) [PRO-2efb9aa9]

Correction: Very high risk means T3b-T4, primary Gleason pattern 5, more than 4 cores with Grade Group 4-5, or 2-3 high-risk features (T3a, GG4-5, PSA over 20). He has T3b and two high-risk features (GG5, PSA 45). He also meets the STAMPEDE criteria for abiraterone (2 or more of T3-4, Gleason 8-10, PSA 40 or more).

Implemented: Yes, 2026-10-17: tools/cases/prostate_cases.py Case 5 (regenerated). Claim now matches the cited source.

Sources:
- [Attard G et al. Abiraterone acetate and prednisolone with or without enzalutamide for high-risk non-metastatic prostate cancer: a meta-analysis of two randomised controlled trials (STAMPEDE). Lancet (eligibility: node-positive or >=2 of T3/4, Gleason 8-10, PSA >=40) (2022) PMID 34953525 doi:10.1016/S0140-6736(21)02437-5](https://pubmed.ncbi.nlm.nih.gov/34953525/)
- [NCCN Clinical Practice Guidelines: Prostate Cancer (risk stratification table; login required, not accessed) (current)](https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1459)

**F-PR-02** (HIGH risk, contradiction, status: Expert review)

The prostate reading and flashcard prx-33 teach that clinical T stage is set by DRE ('a big tumor that can't be felt is still T1c, even if the MRI shows it clearly'), but Case 5 assigns cT3b from MRI and PSMA findings. Practice varies: AJCC/NCCN cT is DRE-based, while many clinicians use MRI evidence of EPE/SVI for risk assignment. The case teaches the opposite rule from the reading without saying so.

Location: `src/data/docs/prostate.json` (Workup & Staging > Step 4: Clinical T Stage (by DRE)) [PRO-5233705f]; `tools/cases/prostate_cases.py` (Case 5: A Hard Gland and a Family History > step 2: T stage) [PRO-7d00978c]

Correction: Proposed: keep the case, but have the explanation say 'Formally, clinical T comes from the DRE; MRI evidence of seminal vesicle invasion is commonly used to treat him as T3b (very high risk).' A radiation oncologist should confirm the preferred teaching.

**F-OV-01** (MODERATE risk, error, status: Revise)

[Retired file, not user-facing] Radiation Physics reading says 'a 9 MeV electron beam has a Dmax of about 4.5 cm and a practical range of about 4.5 cm'. By the page's own rule of thumb (Dmax ~ E/5) Dmax is about 1.8-2 cm; 4.5 cm is the practical range (E/2). As written, Dmax and the practical range coincide, which is physically impossible and contradicts the preceding sentence.

Location: `docs/legacy-overview-docs.json (moved out of src/data by the Before You Start session on 2026-10-16; not rendered in the app)`

Correction: For example, a 9 MeV electron beam has a Dmax of about 2 cm, a 90% isodose depth of about 2.8 cm, and a practical range of about 4.5 cm.

Sources:
- Internal arithmetic: the same paragraph defines Dmax ~ E/5, R90 ~ E/3.2-3.3, Rp ~ E/2 (9/5 = 1.8 cm)

**F-CX-01** (LOWER risk, contradiction, status: Expert review)

Limited-stage SCLC once-daily dose is given as '60-66 Gy daily' in the thoracic quiz (app.js) and flashcard thx-52, but as '60-70 Gy daily' in the reading's NCCN table. Both are defensible (CONVERT used 66 Gy; CALGB 30610 tested 70 Gy), but students see two ranges.

Location: `src/app.js` (th-treatment) [THO-71878d94]; `src/data/decks/thoracic.json` (Flashcard thx-52 (Treatment Paradigms)) [THO-ec88ac55]; `src/data/docs/thoracic.json` (Treatment Paradigms > Small Cell > NCCN Treatment by Stage) [THO-e1590c0f]

Correction: Harmonize on one range after checking the current NCCN SCLC guideline (proposed: '60-70 Gy daily, for example 66 Gy in 33 as in CONVERT').

Sources:
- [Faivre-Finn C et al. CONVERT. Lancet Oncol (2017) PMID 28642008 doi:10.1016/s1470-2045(17)30318-2](https://pubmed.ncbi.nlm.nih.gov/28642008/)

## 7. Proposed corrections with exact source locations

| Finding | Status | Edit in | Proposed correction |
|---|---|---|---|

| F-TH-01 | Verified (implemented) | src/app.js | N2a: { T1:"IIB", T2:"IIIA", T3:"IIIA", T4:"IIIB" }; N2b: { T1:"IIIA", T2:"IIIB", T3:"IIIB", T4:"IIIB" } |

| F-TH-02 | Verified (implemented) | src/data/docs/thoracic.json | IIIA / T4 N0; T3-4 N1; T2-3 N2a; T1 N2b. IIIB / T4 N2a; T2-4 N2b; T1-2 N3. IIIC / T3-4 N3. |

| F-TH-03 | Verified (implemented) | tools/cases/thoracic_cases.py | Answer: T3 N2a M0, Stage IIIA. Explanation: 'T3 N2a is stage IIIA in the 9th edition (it was IIIB in the 8th).' |

| F-TH-04 | Verified (implemented) | src/data/decks/thoracic.json | SWOG 9416 / INT 0160: complete resection in 76% of all patients (over 90% of those who reached surgery); 5-year survival 44%. |

| F-TH-05 | Verified (implemented) | src/data/imaging/thoracic.json | Tumor or bulky 4R nodes can compress it (SVC syndrome). Get tissue first; severe symptoms are relieved fastest with a stent, and RT follows the histology. |

| F-TH-06 | Verified (implemented) | src/data/imaging/thoracic.json | Its lower edge, where it crosses the trachea, is where station 2R ends and 4R begins. |

| F-TH-07 | Verified (implemented) | src/data/docs/thoracic.json; tools/cases/thoracic_cases.py | CALGB 140503 showed sublobar resection (segmentectomy or wedge) was noninferior to lobectomy, and JCOG0802 showed better overall survival with segmentectomy. |

| F-BR-01 | Verified (implemented) | tools/cases/breast_cases.py | PMRT is indicated for T4 tumors, T3 with positive nodes, 4 or more positive nodes, or a positive margin; it is strongly considered for 1-3 nodes, and T3N0 is individualized. |

| F-BR-02 | Verified (implemented) | src/data/docs/breast.json; tools/cases/breast_cases.py | Case 4: 'Her grade 3 tumor over 2 cm makes partial breast RT a poor fit, and she is too young and too high-risk for omission.' Reading: 'low-risk patients (generally 40 or older): small (<=2 cm), N0, ER+, lower grade, clear margins.' |

| F-BR-03 | Verified (implemented) | src/app.js | usually starting at age 25 or 8 years after radiation, whichever comes later |

| F-BR-05 | Expert review | src/data/decks/breast.json | Proposed (needs NCCN check): 'Pregnancy is an absolute contraindication; prior breast/chest RT, active scleroderma or lupus, and Li-Fraumeni syndrome are relative contraindications that need individual review.' |

| F-HN-01 | Expert review | src/app.js; src/data/decks/headneck.json; src/data/docs/headneck.json; tools/cases/headneck_cases.py | Minimum: add an edition note to the NPC staging table ('AJCC 8th edition shown; the AJCC/UICC 9th version (2024) adds advanced radiologic ENE to N3, regroups stages I-III, and splits M1a/M1b'), and qualify the quiz answer ('M0 or M1 for most H&N sites in the 8th edition; NPC version 9 splits M1'). Full migration to version 9 needs radiation oncologist sign-off and a check of the current NCCN edition. |

| F-HN-02 | Expert review | src/app.js; src/data/docs/headneck.json | Keep the current table; add a footnote that this subgroup is T4a in the UICC errata and some AJCC printings, and confirm against the AJCC manual edition the site cites. |

| F-GI-01 | Verified (implemented) | tools/cases/gi_cases.py | Answer: T3 N1a M0, Stage IIIA (AJCC version 9: T3 N0-1 is IIIA; it was IIIC in the 8th edition). Update the distractor list so 'Stage IIIA' is the correct choice. |

| F-GI-02 | Verified (implemented) | src/data/decks/gi.json; src/data/docs/gi.json; tools/cases/gi_cases.py | Case 7 question: 'Which trial found that adding SBRT to sorafenib improved progression-free survival, with a trend toward better overall survival, in locally advanced HCC?' Explanation: 'OS 15.8 vs 12.3 months (borderline; significant only after adjustment); PFS 9.2 vs 5.5 months.' |

| F-GI-03 | Expert review | src/data/anatomy/gi.json; src/data/docs/gi.json | Proposed (needs confirmation): 'Lower cervical paratracheal nodes are regional in the AJCC 8th edition; how supraclavicular nodes are classified depends on the primary's location, and they are routinely covered for cervical and upper thoracic tumors.' |

| F-PR-01 | Verified (implemented) | tools/cases/prostate_cases.py | Very high risk means T3b-T4, primary Gleason pattern 5, more than 4 cores with Grade Group 4-5, or 2-3 high-risk features (T3a, GG4-5, PSA over 20). He has T3b and two high-risk features (GG5, PSA 45). He also meets the STAMPEDE criteria for abiraterone (2 or more of T3-4, Gleason 8-10, PSA 40 or more). |

| F-PR-02 | Expert review | src/data/docs/prostate.json; tools/cases/prostate_cases.py | Proposed: keep the case, but have the explanation say 'Formally, clinical T comes from the DRE; MRI evidence of seminal vesicle invasion is commonly used to treat him as T3b (very high risk).' A radiation oncologist should confirm the preferred teaching. |

| F-GY-01 | Verified (implemented) | src/app.js | Adjuvant pelvic chemoradiation: 45-50.4 Gy with concurrent cisplatin-based chemo (GOG 109 used cisplatin + 5-FU; weekly cisplatin is the common modern choice). |

| F-OV-01 | Revise | docs/legacy-overview-docs.json (moved out of src/data by the Before You Start session on 2026-10-16; not rendered in the app) | For example, a 9 MeV electron beam has a Dmax of about 2 cm, a 90% isodose depth of about 2.8 cm, and a practical range of about 4.5 cm. |

| F-OV-02 | Revise | docs/legacy-overview-docs.json (moved out of src/data by the Before You Start session on 2026-10-16; not rendered in the app) | Parotids / Mean < 25 Gy (both) or < 20 Gy (one) / <20% risk of severe xerostomia (salivary function <25% of baseline) |

| F-OV-03 | Expert review | docs/legacy-overview-docs.json (moved out of src/data by the Before You Start session on 2026-10-16; not rendered in the app) | Proposed after checking Table 1: 'Stomach (whole organ) / D100 < 45 Gy / <7% ulceration', and drop stomach from the list of max-dose organs. |

| F-OV-05 | Verified (implemented) | see finding | Back: 'Mean dose under about 25 Gy (both glands) or 20 Gy (at least one gland)'. Extra: add 'Older series used 26 Gy.' (Owned by the Before You Start session; proposed, not edited here.) |

| F-REF-02 | Revise | see finding | Fix the PMC6661304 author; add first authors to the ten unattributed captions; align years with the PubMed record. |

| F-TH-08 | Verified (implemented) | src/data/decks/thoracic.json; src/data/docs/thoracic.json; tools/cases/thoracic_cases.py | Two randomized phase II trials (Gomez; SABR-COMET, which used a relaxed p<0.20 threshold) showed longer survival with local therapy to every site; SABR-COMET had about 4.5% treatment-related deaths. Phase III trials are ongoing. |

| F-CX-01 | Expert review | src/app.js; src/data/decks/thoracic.json; src/data/docs/thoracic.json | Harmonize on one range after checking the current NCCN SCLC guideline (proposed: '60-70 Gy daily, for example 66 Gy in 33 as in CONVERT'). |

| F-REF-03 | Verified (implemented) | see finding | In tools/sources.py: Perry -> 28296618; RTOG 9802 -> 27050206. Reported to the owning session. |


## 8. Corrections implemented

Every change was a targeted string replacement. Case JSON was regenerated from `tools/cases/<site>_cases.py`, and each regenerated diff touched only the intended lines. `dist/index.html` has **not** been rebuilt and nothing has been committed, so as not to collide with the two other sessions.


| Finding | What changed | Where |
|---|---|---|

| F-TH-01 | N2a: { T1:"IIB", T2:"IIIA", T3:"IIIA", T4:"IIIB" }; N2b: { T1:"IIIA", T2:"IIIB", T3:"IIIB", T4:"IIIB" } | src/app.js lungStageGroup grid. Claim now matches the cited source. |

| F-TH-02 | IIIA / T4 N0; T3-4 N1; T2-3 N2a; T1 N2b. IIIB / T4 N2a; T2-4 N2b; T1-2 N3. IIIC / T3-4 N3. | src/data/docs/thoracic.json AJCC stage-group table. Claim now matches the cited source. |

| F-TH-03 | Answer: T3 N2a M0, Stage IIIA. Explanation: 'T3 N2a is stage IIIA in the 9th edition (it was IIIB in the 8th).' | tools/cases/thoracic_cases.py Case 3 (regenerated). Claim now matches the cited source. |

| F-TH-04 | SWOG 9416 / INT 0160: complete resection in 76% of all patients (over 90% of those who reached surgery); 5-year survival 44%. | src/data/decks/thoracic.json thx-44 extra. Claim now matches the cited source. |

| F-TH-05 | Tumor or bulky 4R nodes can compress it (SVC syndrome). Get tissue first; severe symptoms are relieved fastest with a stent, and RT follows the histology. | src/data/imaging/thoracic.json SVC hotspot. Claim now matches the cited source. |

| F-TH-06 | Its lower edge, where it crosses the trachea, is where station 2R ends and 4R begins. | src/data/imaging/thoracic.json left brachiocephalic vein hotspot. Claim now matches the cited source. |

| F-TH-07 | CALGB 140503 showed sublobar resection (segmentectomy or wedge) was noninferior to lobectomy, and JCOG0802 showed better overall survival with segmentectomy. | docs/thoracic.json + tools/cases/thoracic_cases.py Case 2. Claim now matches the cited source. |

| F-BR-01 | PMRT is indicated for T4 tumors, T3 with positive nodes, 4 or more positive nodes, or a positive margin; it is strongly considered for 1-3 nodes, and T3N0 is individualized. | tools/cases/breast_cases.py Case 6 (regenerated). Claim now matches the cited source. |

| F-BR-02 | Case 4: 'Her grade 3 tumor over 2 cm makes partial breast RT a poor fit, and she is too young and too high-risk for omission.' Reading: 'low-risk patients (generally 40 or older): small (<=2 cm), N0, ER+, lower grade, cl | tools/cases/breast_cases.py Case 4 + docs/breast.json. Claim now matches the cited source. |

| F-BR-03 | usually starting at age 25 or 8 years after radiation, whichever comes later | src/app.js breast-epi quiz. Claim now matches the cited source. |

| F-GI-01 | Answer: T3 N1a M0, Stage IIIA (AJCC version 9: T3 N0-1 is IIIA; it was IIIC in the 8th edition). Update the distractor list so 'Stage IIIA' is the correct choice. | tools/cases/gi_cases.py Case 4 (regenerated). Claim now matches the cited source. |

| F-GI-02 | Case 7 question: 'Which trial found that adding SBRT to sorafenib improved progression-free survival, with a trend toward better overall survival, in locally advanced HCC?' Explanation: 'OS 15.8 vs 12.3 months (borderlin | gi_cases.py Case 7, decks/gi.json gix-51, docs/gi.json. Claim now matches the cited source. |

| F-PR-01 | Very high risk means T3b-T4, primary Gleason pattern 5, more than 4 cores with Grade Group 4-5, or 2-3 high-risk features (T3a, GG4-5, PSA over 20). He has T3b and two high-risk features (GG5, PSA 45). He also meets the  | tools/cases/prostate_cases.py Case 5 (regenerated). Claim now matches the cited source. |

| F-GY-01 | Adjuvant pelvic chemoradiation: 45-50.4 Gy with concurrent cisplatin-based chemo (GOG 109 used cisplatin + 5-FU; weekly cisplatin is the common modern choice). | src/app.js POSTOP_TX peters. Claim now matches the cited source. |

| F-OV-05 | Back: 'Mean dose under about 25 Gy (both glands) or 20 Gy (at least one gland)'. Extra: add 'Older series used 26 Gy.' (Owned by the Before You Start session; proposed, not edited here.) | ov-95 now reads about 25 Gy for both parotids or 20 Gy for one (QUANTEC), with 'many protocols use about 26 Gy' in the extra. |

| F-TH-08 | Two randomized phase II trials (Gomez; SABR-COMET, which used a relaxed p<0.20 threshold) showed longer survival with local therapy to every site; SABR-COMET had about 4.5% treatment-related deaths. Phase III trials are  | decks/thoracic.json thx-50, docs/thoracic.json, thoracic Case 7. Claim now matches the cited source. |

| F-REF-03 | In tools/sources.py: Perry -> 28296618; RTOG 9802 -> 27050206. Reported to the owning session. | Perry -> 28296618, RTOG 9802 -> 27050206, plus a third letter it found (MA.20 26535517 -> 26200977). That session's verifier now rejects Letter/Comment publication types. |


## 9. Claims still requiring a radiation oncologist's judgment

**F-BR-05** (HIGH risk, expert, status: Expert review)

Flashcard br-54 lists prior breast/chest radiation alongside pregnancy as a factor that makes breast RT unsafe, and scleroderma/lupus and Li-Fraumeni as relative. Recent NCCN versions are understood to list prior chest RT as a relative contraindication (dose and interval matter). NCCN tables need a login and were not accessed, so the current wording could not be confirmed.

Location: `src/data/decks/breast.json` (Flashcard br-54 (Treatment Paradigms)) [BRE-a5671acd]

Correction: Proposed (needs NCCN check): 'Pregnancy is an absolute contraindication; prior breast/chest RT, active scleroderma or lupus, and Li-Fraumeni syndrome are relative contraindications that need individual review.'

**F-HN-01** (HIGH risk, outdated, status: Expert review)

Nasopharynx staging throughout (reading tables, Case 4, flashcard hn-42, quiz 'M-stage is simply M0 or M1') uses AJCC 8th edition. The AJCC/UICC 9th version for NPC (2024) adds advanced radiologic ENE as an N3 criterion, regroups nonmetastatic disease into stages I-III (I = T1-2 N0-1 with IA/IB, II = T3 or N2, III = T4 or N3), and splits M1 into M1a (<=3 lesions, IVA) and M1b (>3, IVB). The content is correct for the 8th edition and labeled as such in Case 4, but readers are not told a newer version exists. Whether to switch editions (and match NCCN's current choice) is an editorial/clinical decision.

Location: `src/app.js` (hn-staging) [HEA-6b1aae88]; `tools/cases/headneck_cases.py` (Case 4: The Ear That Won't Clear > step 3: Stage) [HEA-510c4d2e]; `src/data/decks/headneck.json` (Flashcard hn-42 (Workup & Staging)) [HEA-5b60b6c7]; `src/data/docs/headneck.json` (Workup & Staging > Nasopharynx > N category) [HEA-a8fcb5cd]

Correction: Minimum: add an edition note to the NPC staging table ('AJCC 8th edition shown; the AJCC/UICC 9th version (2024) adds advanced radiologic ENE to N3, regroups stages I-III, and splits M1a/M1b'), and qualify the quiz answer ('M0 or M1 for most H&N sites in the 8th edition; NPC version 9 splits M1'). Full migration to version 9 needs radiation oncologist sign-off and a check of the current NCCN edition.

Sources:
- [Pan JJ et al. Ninth Version of the AJCC and UICC Nasopharyngeal Cancer TNM Staging Classification. JAMA Oncol (2024) PMID 39388190 doi:10.1001/jamaoncol.2024.4354](https://pubmed.ncbi.nlm.nih.gov/39388190/)

**F-HN-02** (HIGH risk, expert, status: Expert review)

Oral cavity T table assigns tumors >4 cm with DOI >10 mm to T4a. This matches the UICC 8th edition errata (2018) and several AJCC-derived tables, but other AJCC 8th summaries (e.g., Radiopaedia) define T3 as >4 cm or any DOI >10 mm with T4a reserved for invasion of adjacent structures. The two sources conflict for exactly this subgroup. Content is internally consistent across the reading, quiz, and drill.

Location: `src/app.js` (hn-staging) [HEA-46512773]; `src/data/docs/headneck.json` (Workup & Staging > Oral Cavity > T category) [HEA-4f8ea618]

Correction: Keep the current table; add a footnote that this subgroup is T4a in the UICC errata and some AJCC printings, and confirm against the AJCC manual edition the site cites.

Sources:
- [UICC TNM Classification 8th edition errata (25 May 2018) (2018)](https://www.uicc.org/sites/main/files/atoms/files/UICC%208th%20Edition%20Errata_25May2018%20final.pdf)
- [Radiopaedia: Oral cavity carcinoma staging (2025)](https://radiopaedia.org/articles/oral-cavity-carcinoma-staging)

**F-GI-03** (HIGH risk, expert, status: Expert review)

GI reading and anatomy plate say supraclavicular nodes are 'generally considered distant (M1)' for esophageal cancer and are 'included electively for some cervical/upper tumors'. AJCC 8th edition regional nodes for the esophagus include lower cervical paratracheal stations (1R/1L), and treatment of supraclavicular nodes for cervical/upper thoracic primaries is common. Whether 'supraclavicular = M1' is accurate as written could not be confirmed against the AJCC manual text.

Location: `src/data/anatomy/gi.json` (Anatomy > Esophagus & Stomach Nodes > Supraclavicular Nodes (104)) [GI-c1bb9aa0]; `src/data/docs/gi.json` (Workup & Staging > Esophagus) [GI-ab0b5cf9]

Correction: Proposed (needs confirmation): 'Lower cervical paratracheal nodes are regional in the AJCC 8th edition; how supraclavicular nodes are classified depends on the primary's location, and they are routinely covered for cervical and upper thoracic tumors.'

**F-PR-02** (HIGH risk, contradiction, status: Expert review)

The prostate reading and flashcard prx-33 teach that clinical T stage is set by DRE ('a big tumor that can't be felt is still T1c, even if the MRI shows it clearly'), but Case 5 assigns cT3b from MRI and PSMA findings. Practice varies: AJCC/NCCN cT is DRE-based, while many clinicians use MRI evidence of EPE/SVI for risk assignment. The case teaches the opposite rule from the reading without saying so.

Location: `src/data/docs/prostate.json` (Workup & Staging > Step 4: Clinical T Stage (by DRE)) [PRO-5233705f]; `tools/cases/prostate_cases.py` (Case 5: A Hard Gland and a Family History > step 2: T stage) [PRO-7d00978c]

Correction: Proposed: keep the case, but have the explanation say 'Formally, clinical T comes from the DRE; MRI evidence of seminal vesicle invasion is commonly used to treat him as T3b (very high risk).' A radiation oncologist should confirm the preferred teaching.

**F-OV-01** (MODERATE risk, error, status: Revise)

[Retired file, not user-facing] Radiation Physics reading says 'a 9 MeV electron beam has a Dmax of about 4.5 cm and a practical range of about 4.5 cm'. By the page's own rule of thumb (Dmax ~ E/5) Dmax is about 1.8-2 cm; 4.5 cm is the practical range (E/2). As written, Dmax and the practical range coincide, which is physically impossible and contradicts the preceding sentence.

Location: `docs/legacy-overview-docs.json (moved out of src/data by the Before You Start session on 2026-10-16; not rendered in the app)`

Correction: For example, a 9 MeV electron beam has a Dmax of about 2 cm, a 90% isodose depth of about 2.8 cm, and a practical range of about 4.5 cm.

Sources:
- Internal arithmetic: the same paragraph defines Dmax ~ E/5, R90 ~ E/3.2-3.3, Rp ~ E/2 (9/5 = 1.8 cm)

**F-OV-02** (MODERATE risk, error, status: Revise)

[Retired file, not user-facing] QUANTEC table in the Common Dose Constraints reading lists 'Bilateral parotid | Mean < 26 Gy | <25% long-term salivary function'. QUANTEC gives a mean dose of about 25 Gy for both glands (or about 20 Gy for one gland) to avoid severe xerostomia, defined as long-term salivary function below 25% of baseline; the 25% is the definition of the endpoint, not the risk. (The 26 Gy figure is the older Eisbruch threshold quoted correctly in the flashcard.)

Location: `docs/legacy-overview-docs.json (moved out of src/data by the Before You Start session on 2026-10-16; not rendered in the app)`

Correction: Parotids | Mean < 25 Gy (both) or < 20 Gy (one) | <20% risk of severe xerostomia (salivary function <25% of baseline)

Sources:
- [Deasy JO et al. Radiotherapy dose-volume effects on salivary gland function (QUANTEC). Int J Radiat Oncol Biol Phys (2010) PMID 20171519 doi:10.1016/j.ijrobp.2009.06.090](https://pubmed.ncbi.nlm.nih.gov/20171519/)

**F-OV-03** (MODERATE risk, expert, status: Expert review)

[Retired file, not user-facing] The same QUANTEC table lists 'Stomach | Max < 45 Gy | <7% ulceration' and the text then names the stomach as a max-dose (serial) organ. The QUANTEC summary table is recalled to list the whole-stomach D100 < 45 Gy for <7% ulceration, not a maximum dose. The summary table in the free manuscript is an image and could not be read programmatically, and the organ-specific abstract does not state the parameter.

Location: `docs/legacy-overview-docs.json (moved out of src/data by the Before You Start session on 2026-10-16; not rendered in the app)`

Correction: Proposed after checking Table 1: 'Stomach (whole organ) | D100 < 45 Gy | <7% ulceration', and drop stomach from the list of max-dose organs.

Sources:
- [Kavanagh BD et al. Radiation dose-volume effects in the stomach and small bowel (QUANTEC). Int J Radiat Oncol Biol Phys (2010) PMID 20171503 doi:10.1016/j.ijrobp.2009.05.071](https://pubmed.ncbi.nlm.nih.gov/20171503/)
- [Marks LB et al. Use of normal tissue complication probability models in the clinic (QUANTEC summary, Table 1) (2010) PMID 20171502 doi:10.1016/j.ijrobp.2009.07.1754](https://pubmed.ncbi.nlm.nih.gov/20171502/)

**F-REF-02** (LOWER risk, reference, status: Revise)

Figure caption attribution: all 101 cited PMC IDs exist. PMC6661304 is credited to 'Hashmi R, Sectional Anatomy Quiz IV' but its first author is Lathif. PMC10847842 (Crosetti) is cited as 2024; the record says 2023. PMC7874055 (Sardaro) is cited as 2021; the record says 2020 (likely epub vs issue year). Ten captions give the journal and year without an author. See docs/audit/caption_reference_check.csv.

Correction: Fix the PMC6661304 author; add first authors to the ten unattributed captions; align years with the PubMed record.

Sources:
- docs/audit/caption_reference_check.csv (Europe PMC lookups) (2026)

**F-CX-01** (LOWER risk, contradiction, status: Expert review)

Limited-stage SCLC once-daily dose is given as '60-66 Gy daily' in the thoracic quiz (app.js) and flashcard thx-52, but as '60-70 Gy daily' in the reading's NCCN table. Both are defensible (CONVERT used 66 Gy; CALGB 30610 tested 70 Gy), but students see two ranges.

Location: `src/app.js` (th-treatment) [THO-71878d94]; `src/data/decks/thoracic.json` (Flashcard thx-52 (Treatment Paradigms)) [THO-ec88ac55]; `src/data/docs/thoracic.json` (Treatment Paradigms > Small Cell > NCCN Treatment by Stage) [THO-e1590c0f]

Correction: Harmonize on one range after checking the current NCCN SCLC guideline (proposed: '60-70 Gy daily, for example 66 Gy in 33 as in CONVERT').

Sources:
- [Faivre-Finn C et al. CONVERT. Lancet Oncol (2017) PMID 28642008 doi:10.1016/s1470-2045(17)30318-2](https://pubmed.ncbi.nlm.nih.gov/28642008/)

Also for physician review (not separate findings):
- The ~3,300 HIGH claims marked "Read, no discrepancy found" have no source attached per claim. Spot-check them, starting with the constraint and dose tables.
- Prepared OpenEvidence questions for the items above are in `docs/audit/openevidence_questions.md`. **OpenEvidence was not accessed in this audit.**

## 10. Validation report

**Tests run**
- `tools/audit/builder_tests.js`: 249 assertions on the interactive builders, run in a browser against a scratch build that included all changes: lung stage group for every T × N × M combination (AJCC 9th edition, IASLC 2024), station-to-N drill, Gleason to Grade Group, NCCN prostate risk group, AJCC 8 prostate stage, Sedlis/Peters, WHO 2021 glioma. **249/249 pass.** Before the fix, the lung grid returned IIIB for T3 N2a and IIIC for T3-4 N2b.
- Content check in the same build: all 9 corrected strings render (thoracic table and Case 3, GI Case 4, prostate Case 5, breast Case 6, SVC hotspot, SWOG flashcard, survivor-screening quiz, Sedlis text). No console errors.
- The builder logic for SINS, Mirels, and the 2008 GPA was checked by hand against the source scoring tables (Fisher 2010, Mirels 1989, Sperduto 2008); no discrepancy.
- `extract_claims.py` reports 0 finding targets that fail to match a claim.
- Citation checks: 155/155 trial PMIDs resolve (2 in sources.json point to letters, F-REF-03); 27/27 inline links resolve and match; 101/101 caption PMC IDs exist.

**Limitations**
- No NCCN guideline text was accessed (login required). Statements summarizing NCCN were checked against primary trials and consensus papers where possible, otherwise left Pending or Expert review.
- Most verification used abstracts (Europe PMC), not full texts. Claims depending on numbers found only in tables or figures (e.g., the QUANTEC summary table) are marked accordingly.
- MODERATE and LOWER claims were not systematically read (8,136 unread), except Palliative & Benign MODERATE claims and claims surfaced during cross-checks.
- Risk tiering and sentence splitting are automatic. A claim split across two ledger rows, or a 'Try it' question separated from its answer, can lose context (one apparent contradiction in Head & Neck was a splitting artifact and was not recorded).
- Content changed by other sessions after this audit, or after 2026-10-17, is not covered; rerun the extractor and compare claim IDs.
- Reviewer was an AI model. Absence of a finding is not proof of accuracy.


## Files

- `docs/audit/claim_ledger.csv`: full claim inventory

- `docs/audit/findings.json`: all findings with sources and corrections

- `docs/audit/high_risk_review_queue.csv`: HIGH claims in review order

- `docs/audit/trial_references.csv`: primary publication for each named trial

- `docs/audit/pubmed_link_check.csv`: inline PubMed link check

- `docs/audit/caption_reference_check.csv`: figure caption PMC check

- `docs/audit/openevidence_questions.md`: prepared questions (not submitted)

- `docs/audit/first_pass_reviewed_ids.txt`: claim IDs read in this audit

- `docs/audit/ledger_summary.json`: counts


Tools: `tools/audit/extract_claims.py`, `add_findings.py`, `epmc.py` (Europe PMC lookup), `trial_queries.py` + `trial_refs.py`, `check_pubmed_links.py`, `check_pmc_captions.py`, `builder_tests.js`, `make_report.py`.
