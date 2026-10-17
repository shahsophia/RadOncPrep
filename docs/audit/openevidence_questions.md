# OpenEvidence Questions (prepared, not submitted)

OpenEvidence was **not accessed** during this audit. These questions are prepared for a reviewer to submit. Treat any answer as a lead for source verification, not as proof, and record the returned citations in `docs/audit/findings.json` against the finding ID before changing site content.

For each question, ask OpenEvidence to return: (1) supporting evidence, (2) opposing evidence, (3) the current applicable guideline and its version, (4) relevant trial limitations, and (5) the exact source (title, year, PMID/DOI) for each conclusion.

---

### Q1. Nasopharynx staging edition (F-HN-01)
**Claim on site:** Nasopharyngeal carcinoma is staged with AJCC 8th edition: N1 unilateral cervical (or retropharyngeal) nodes ≤6 cm above the caudal cricoid, N2 bilateral, N3 >6 cm or below the cricoid; stage groups I to IVB; M0 or M1 only.
**Context:** Teaching resource for US medical students; NCCN Head and Neck Cancers guideline is the reference.
**Question:** Does the current NCCN Head and Neck Cancers guideline stage nasopharyngeal carcinoma with the AJCC 8th edition or the AJCC/UICC 9th version (2024)? What exactly changed in version 9 (advanced radiologic ENE, stage regrouping I-III, M1a/M1b), and is the 8th edition still acceptable to teach?

### Q2. Oral cavity T4a by size plus depth of invasion (F-HN-02)
**Claim on site:** Oral cavity tumor >4 cm with DOI >10 mm is T4a.
**Question:** In the AJCC 8th edition as currently printed (with errata) used in the US, is a >4 cm oral cavity tumor with DOI >10 mm classified as T3 or T4a? How does this differ from the UICC 8th edition errata (2018)? Cite the AJCC text.

### Q3. Esophageal cancer supraclavicular nodes (F-GI-03)
**Claim on site:** Supraclavicular nodes are generally considered distant (M1) for esophageal cancer and are included electively for some cervical/upper tumors.
**Question:** Under AJCC 8th edition esophageal staging, are supraclavicular lymph nodes regional (N) or distant (M1)? Does this depend on primary tumor location (cervical vs thoracic)? Cite the AJCC regional node definition.

### Q4. Clinical T stage in prostate cancer: DRE vs MRI (F-PR-02)
**Claim on site:** Clinical T stage is set by DRE; a tumor that can't be felt is cT1c even if MRI shows it. A case assigns cT3b from MRI showing seminal vesicle invasion.
**Question:** For NCCN risk stratification and AJCC 8th edition clinical staging, may MRI findings of extraprostatic extension or seminal vesicle invasion be used to assign cT3a/cT3b? What do the current NCCN Prostate Cancer guidelines say about imaging-based T staging?

### Q5. Prior chest RT and breast conservation (F-BR-05)
**Claim on site:** Pregnancy and prior radiation to the breast/chest make breast RT unsafe; active scleroderma or lupus and Li-Fraumeni are relative contraindications.
**Question:** In the current NCCN Breast Cancer guideline, is prior breast or chest wall radiation an absolute or relative contraindication to breast-conserving therapy requiring RT? List current absolute vs relative contraindications.

### Q6. QUANTEC stomach constraint (F-OV-03; retired file, still worth confirming)
**Claim:** Stomach "Max <45 Gy" for <7% ulceration (QUANTEC).
**Question:** In the QUANTEC summary (Marks 2010, Table 1), is the stomach ulceration constraint expressed as D100 (whole organ) <45 Gy or as a maximum dose?

### Q7. HPV-positive oropharynx de-escalation (current status check)
**Claim on site:** Off a clinical trial, HPV-positive oropharyngeal cancer is treated with the same intensity as HPV-negative disease; cetuximab substitution was worse and dose de-escalation has not yet been shown safe.
**Question:** As of 2026, have NRG-HN005 or other phase III trials established reduced-dose chemoradiation as a standard option for selected HPV-positive oropharyngeal cancer? Has NCCN changed its recommendation?

### Q8. NCCN very-low-risk prostate definition (builder logic)
**Claim in risk builder:** Very low risk = cT1c, Grade Group 1, PSA <10, PSA density <0.15 (core-count criteria not required).
**Question:** In the current NCCN Prostate Cancer guideline, does very-low-risk still require fewer than 3 positive cores and ≤50% cancer in each core, or only cT1c, GG1, PSA <10, and PSA density <0.15?

### Q9. Partial breast irradiation eligibility (F-BR-02, implemented)
**Claim on site (corrected):** PBI candidates are generally 40 or older with small (≤2 cm), N0, ER+, lower-grade tumors and clear margins.
**Question:** Confirm the 2024 ASTRO PBI guideline age threshold and the tumor features for which PBI is recommended vs conditionally recommended.

### Q10. Limited-stage SCLC once-daily dose (F-CX-01)
**Claim on site:** Once-daily thoracic RT for LS-SCLC is quoted as 60-66 Gy in some places and 60-70 Gy in others.
**Question:** What once-daily dose range does the current NCCN Small Cell Lung Cancer guideline list, and what did CONVERT (66 Gy) and CALGB 30610 (70 Gy) show?
