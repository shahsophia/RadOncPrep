#!/usr/bin/env python3
"""
Verified sources for every trial named in the curriculum (curriculum.json
"trials") and every trial box in the readings. Writes src/data/sources.json,
which the app uses to link trial boxes, "Trials cited here", and the Sources
& References lists to the original publication on PubMed.

Each entry was checked in October 2026 by looking up the PubMed record and
confirming the title, journal, year, first author, and publication type (not a letter or reply) match the trial named in
the reading (the primary report or the long-term update the reading cites).
To re-check every PMID against PubMed:   python3 tools/sources.py --verify

Usage:  python3 tools/sources.py && python3 build.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# key: (PMID, first author surname, journal, year, title)
TRIALS = {
    "RTOG 91-11": ("23182993", "Forastiere", "J Clin Oncol", "2013", "Long-term results of RTOG 91-11: a comparison of three nonsurgical treatment strategies to preserve the larynx in patients with locally advanced larynx cancer"),
    "VA Larynx": ("2034244", "VA Laryngeal Cancer Study Group", "N Engl J Med", "1991", "Induction chemotherapy plus radiation compared with surgery plus radiation in patients with advanced laryngeal cancer"),
    "RTOG 9501": ("15128893", "Cooper", "N Engl J Med", "2004", "Postoperative concurrent radiotherapy and chemotherapy for high-risk squamous-cell carcinoma of the head and neck"),
    "EORTC 22931": ("15128894", "Bernier", "N Engl J Med", "2004", "Postoperative irradiation with or without concomitant chemotherapy for locally advanced head and neck cancer"),
    "RTOG 1016": ("30449625", "Gillison", "Lancet", "2019", "Radiotherapy plus cetuximab or cisplatin in human papillomavirus-positive oropharyngeal cancer (NRG Oncology RTOG 1016): a randomised, multicentre, non-inferiority trial"),
    "De-ESCALaTE": ("30449623", "Mehanna", "Lancet", "2019", "Radiotherapy plus cisplatin or cetuximab in low-risk human papillomavirus-positive oropharyngeal cancer (De-ESCALaTE HPV): an open-label randomised controlled phase 3 trial"),
    "Tata Memorial": ("26027881", "D'Cruz", "N Engl J Med", "2015", "Elective versus Therapeutic Neck Dissection in Node-Negative Oral Cancer"),
    "PARSPORT": ("21236730", "Nutting", "Lancet Oncol", "2011", "Parotid-sparing intensity modulated versus conventional radiotherapy in head and neck cancer (PARSPORT): a phase 3 multicentre randomised controlled trial"),
    "NSABP B-06": ("12393820", "Fisher", "N Engl J Med", "2002", "Twenty-year follow-up of a randomized trial comparing total mastectomy, lumpectomy, and lumpectomy plus irradiation for the treatment of invasive breast cancer"),
    "Milan": ("12393819", "Veronesi", "N Engl J Med", "2002", "Twenty-year follow-up of a randomized study comparing breast-conserving surgery with radical mastectomy for early breast cancer"),
    "EBCTCG meta-analysis": ("22019144", "EBCTCG", "Lancet", "2011", "Effect of radiotherapy after breast-conserving surgery on 10-year recurrence and 15-year breast cancer death: meta-analysis of individual patient data for 10,801 women in 17 randomised trials"),
    "ACOSOG Z0011": ("28898379", "Giuliano", "JAMA", "2017", "Effect of Axillary Dissection vs No Axillary Dissection on 10-Year Overall Survival Among Women With Invasive Breast Cancer and Sentinel Node Metastasis: The ACOSOG Z0011 (Alliance) Randomized Clinical Trial"),
    "AMAROS": ("25439688", "Donker", "Lancet Oncol", "2014", "Radiotherapy or surgery of the axilla after a positive sentinel node in breast cancer (EORTC 10981-22023 AMAROS): a randomised, multicentre, open-label, phase 3 non-inferiority trial"),
    "NSABP B-17": ("8292119", "Fisher", "N Engl J Med", "1993", "Lumpectomy compared with lumpectomy and radiation therapy for the treatment of intraductal breast cancer"),
    "EORTC 10853": ("24043739", "Donker", "J Clin Oncol", "2013", "Breast-conserving treatment with or without radiotherapy in ductal carcinoma In Situ: 15-year recurrence rates and outcome after a recurrence, from the EORTC 10853 randomized phase III trial"),
    "RTOG 9804": ("25605856", "McCormick", "J Clin Oncol", "2015", "RTOG 9804: a prospective randomized trial for good-risk ductal carcinoma in situ comparing radiotherapy with observation"),
    "START B": ("24055415", "Haviland", "Lancet Oncol", "2013", "The UK Standardisation of Breast Radiotherapy (START) trials of radiotherapy hypofractionation for treatment of early breast cancer: 10-year follow-up results of two randomised controlled trials"),
    "FAST-Forward": ("32580883", "Murray Brunt", "Lancet", "2020", "Hypofractionated breast radiotherapy for 1 week versus 3 weeks (FAST-Forward): 5-year efficacy and late normal tissue effects results from a multicentre, non-inferiority, randomised, phase 3 trial"),
    "EORTC 22881": ("25500422", "Bartelink", "Lancet Oncol", "2015", "Whole-breast irradiation with or without a boost for patients treated with breast-conserving surgery for early breast cancer: 20-year follow-up of a randomised phase 3 trial"),
    "CALGB 9343": ("23690420", "Hughes", "J Clin Oncol", "2013", "Lumpectomy plus tamoxifen with or without irradiation in women age 70 years or older with early breast cancer: long-term follow-up of CALGB 9343"),
    "PRIME II": ("36791159", "Kunkler", "N Engl J Med", "2023", "Breast-Conserving Surgery with or without Irradiation in Early Breast Cancer"),
    "MA.20": ("26200977", "Whelan", "N Engl J Med", "2015", "Regional Nodal Irradiation in Early-Stage Breast Cancer"),
    "EORTC 22922": ("26200978", "Poortmans", "N Engl J Med", "2015", "Internal Mammary and Medial Supraclavicular Irradiation in Breast Cancer"),
    "NSABP B-51": ("40466065", "Mamounas", "N Engl J Med", "2025", "Omitting Regional Nodal Irradiation after Response to Neoadjuvant Chemotherapy"),
    "KEYNOTE-522": ("32101663", "Schmid", "N Engl J Med", "2020", "Pembrolizumab for Early Triple-Negative Breast Cancer"),
    "RTOG 0236": ("20233825", "Timmerman", "JAMA", "2010", "Stereotactic body radiation therapy for inoperable early stage lung cancer"),
    "Indiana phase II (Timmerman)": ("17050868", "Timmerman", "J Clin Oncol", "2006", "Excessive toxicity when treating central tumors in a phase II study of stereotactic body radiation therapy for medically inoperable early-stage lung cancer"),
    "RTOG 0813": ("30943123", "Bezjak", "J Clin Oncol", "2019", "Safety and Efficacy of a Five-Fraction Stereotactic Body Radiotherapy Schedule for Centrally Located Non-Small-Cell Lung Cancer: NRG Oncology/RTOG 0813 Trial"),
    "HILUS": ("33823286", "Lindberg", "J Thorac Oncol", "2021", "The HILUS-Trial-a Prospective Nordic Multicenter Phase 2 Study of Ultracentral Lung Tumors Treated With Stereotactic Body Radiotherapy"),
    "JCOG0802": ("35461558", "Saji", "Lancet", "2022", "Segmentectomy versus lobectomy in small-sized peripheral non-small-cell lung cancer (JCOG0802/WJOG4607L): a multicentre, open-label, phase 3, randomised, controlled, non-inferiority trial"),
    "SWOG 9416 / INT 0160": ("17235046", "Rusch", "J Clin Oncol", "2007", "Induction chemoradiation and surgical resection for superior sulcus non-small-cell lung carcinomas: long-term results of Southwest Oncology Group Trial 9416 (Intergroup Trial 0160)"),
    "RTOG 0617": ("25601342", "Bradley", "Lancet Oncol", "2015", "Standard-dose versus high-dose conformal radiotherapy with concurrent and consolidation carboplatin plus paclitaxel with or without cetuximab for patients with stage IIIA or IIIB non-small-cell lung cancer (RTOG 0617): a randomised, two-by-two factorial phase 3 study"),
    "PACIFIC": ("28885881", "Antonia", "N Engl J Med", "2017", "Durvalumab after Chemoradiotherapy in Stage III Non-Small-Cell Lung Cancer"),
    "LAURA": ("38828946", "Lu", "N Engl J Med", "2024", "Osimertinib after Chemoradiotherapy in Stage III EGFR-Mutated NSCLC"),
    "CheckMate 816": ("35403841", "Forde", "N Engl J Med", "2022", "Neoadjuvant Nivolumab plus Chemotherapy in Resectable Lung Cancer"),
    "KEYNOTE-671": ("37272513", "Wakelee", "N Engl J Med", "2023", "Perioperative Pembrolizumab for Early-Stage Non-Small-Cell Lung Cancer"),
    "LungART": ("34919827", "Le Pechoux", "Lancet Oncol", "2022", "Postoperative radiotherapy versus no postoperative radiotherapy in patients with completely resected non-small-cell lung cancer and proven mediastinal N2 involvement (Lung ART): an open-label, randomised, phase 3 trial"),
    "SABR-COMET": ("30982687", "Palma", "Lancet", "2019", "Stereotactic ablative radiotherapy versus standard of care palliative treatment in patients with oligometastatic cancers (SABR-COMET): a randomised, phase 2, open-label trial"),
    "Turrisi": ("9920950", "Turrisi", "N Engl J Med", "1999", "Twice-daily compared with once-daily thoracic radiotherapy in limited small-cell lung cancer treated concurrently with cisplatin and etoposide"),
    "CONVERT": ("28642008", "Faivre-Finn", "Lancet Oncol", "2017", "Concurrent once-daily versus twice-daily chemoradiotherapy in patients with limited-stage small-cell lung cancer (CONVERT): an open-label, phase 3, randomised, superiority trial"),
    "ADRIATIC": ("39268857", "Cheng", "N Engl J Med", "2024", "Durvalumab after Chemoradiotherapy in Limited-Stage Small-Cell Lung Cancer"),
    "ProtecT": ("36912538", "Hamdy", "N Engl J Med", "2023", "Fifteen-Year Outcomes after Monitoring, Surgery, or Radiotherapy for Prostate Cancer"),
    "RTOG 9408": ("21751904", "Jones", "N Engl J Med", "2011", "Radiotherapy and short-term androgen deprivation for localized prostate cancer"),
    "RTOG 9202": ("18413638", "Horwitz", "J Clin Oncol", "2008", "Ten-year follow-up of radiation therapy oncology group protocol 92-02: a phase III trial of the duration of elective androgen deprivation in locally advanced prostate cancer"),
    "EORTC 22961": ("19516032", "Bolla", "N Engl J Med", "2009", "Duration of androgen suppression in the treatment of prostate cancer"),
    "RTOG 9413": ("12743142", "Roach", "J Clin Oncol", "2003", "Phase III trial comparing whole-pelvic versus prostate-only radiotherapy and neoadjuvant versus adjuvant combined androgen suppression: Radiation Therapy Oncology Group 9413"),
    "RTOG 0415": ("38759121", "Lee", "J Clin Oncol", "2024", "Long-Term Analysis of NRG Oncology RTOG 0415: A Randomized Phase III Noninferiority Study Comparing Two Fractionation Schedules in Patients With Low-Risk Prostate Cancer"),
    "CHHiP": ("27339115", "Dearnaley", "Lancet Oncol", "2016", "Conventional versus hypofractionated high-dose intensity-modulated radiotherapy for prostate cancer: 5-year outcomes of the randomised, non-inferiority, phase 3 CHHiP trial"),
    "PROFIT": ("28296582", "Catton", "J Clin Oncol", "2017", "Randomized Trial of a Hypofractionated Radiation Regimen for the Treatment of Localized Prostate Cancer"),
    "HYPO-RT-PC": ("31227373", "Widmark", "Lancet", "2019", "Ultra-hypofractionated versus conventionally fractionated radiotherapy for prostate cancer: 5-year outcomes of the HYPO-RT-PC randomised, non-inferiority, phase 3 trial"),
    "PACE-B": ("39413377", "van As", "N Engl J Med", "2024", "Phase 3 Trial of Stereotactic Body Radiotherapy in Localized Prostate Cancer"),
    "ASCENDE-RT": ("28262473", "Morris", "Int J Radiat Oncol Biol Phys", "2017", "Androgen Suppression Combined with Elective Nodal and Dose Escalated Radiation Therapy (the ASCENDE-RT Trial): An Analysis of Survival Endpoints for a Randomized Trial Comparing a Low-Dose-Rate Brachytherapy Boost to a Dose-Escalated External Beam Boost for High- and Intermediate-risk Prostate Cancer"),
    "RTOG 0232": ("37315297", "Michalski", "J Clin Oncol", "2023", "Effect of Brachytherapy With External Beam Radiation Therapy Versus Brachytherapy Alone for Intermediate-Risk Prostate Cancer: NRG Oncology RTOG 0232 Randomized Clinical Trial"),
    "FLAME": ("33471548", "Kerkmeijer", "J Clin Oncol", "2021", "Focal Boost to the Intraprostatic Tumor in External Beam Radiotherapy for Patients With Localized Prostate Cancer: Results From the FLAME Randomized Phase III Trial"),
    "POP-RT": ("33497252", "Murthy", "J Clin Oncol", "2021", "Prostate-Only Versus Whole-Pelvic Radiation Therapy in High-Risk and Very High-Risk Prostate Cancer (POP-RT): Outcomes From Phase III Randomized Controlled Trial"),
    "RTOG 9601": ("28146658", "Shipley", "N Engl J Med", "2017", "Radiation with or without Antiandrogen Therapy in Recurrent Prostate Cancer"),
    "SPPORT": ("35569466", "Pollack", "Lancet", "2022", "The addition of androgen deprivation therapy and pelvic lymph node treatment to prostate bed salvage radiotherapy (NRG Oncology/RTOG 0534 SPPORT): an international, multicentre, randomised phase 3 trial"),
    "GETUG-AFU 17": ("33002438", "Sargos", "Lancet Oncol", "2020", "Adjuvant radiotherapy versus early salvage radiotherapy plus short-term androgen deprivation therapy in men with localised prostate cancer after radical prostatectomy (GETUG-AFU 17): a randomised, phase 3 trial"),
    "RADICALS": ("33002429", "Parker", "Lancet", "2020", "Timing of radiotherapy after radical prostatectomy (RADICALS-RT): a randomised, controlled phase 3 trial"),
    "RAVES": ("33002437", "Kneebone", "Lancet Oncol", "2020", "Adjuvant radiotherapy versus early salvage radiotherapy following radical prostatectomy (TROG 08.03/ANZUP RAVES): a randomised, controlled, phase 3, non-inferiority trial"),
    "STAMPEDE": ("30355464", "Parker", "Lancet", "2018", "Radiotherapy to the primary tumour for newly diagnosed, metastatic prostate cancer (STAMPEDE): a randomised controlled phase 3 trial"),
    "GOG 85": ("10334517", "Whitney", "J Clin Oncol", "1999", "Randomized comparison of fluorouracil plus cisplatin versus hydroxyurea as an adjunct to radiation therapy in stage IIB-IVA carcinoma of the cervix with negative para-aortic lymph nodes: a Gynecologic Oncology Group and Southwest Oncology Group study"),
    "GOG 92": ("10329031", "Sedlis", "Gynecol Oncol", "1999", "A randomized trial of pelvic radiation therapy versus no further therapy in selected patients with stage IB carcinoma of the cervix after radical hysterectomy and pelvic lymphadenectomy: A Gynecologic Oncology Group Study"),
    "GOG 109": ("10764420", "Peters", "J Clin Oncol", "2000", "Concurrent chemotherapy and pelvic radiation therapy compared with pelvic radiation therapy alone as adjuvant therapy after radical surgery in high-risk early-stage cancer of the cervix"),
    "RTOG 9001": ("10202164", "Morris", "N Engl J Med", "1999", "Pelvic radiation with concurrent chemotherapy compared with pelvic and para-aortic radiation for high-risk cervical cancer"),
    "GOG 120": ("10202165", "Rose", "N Engl J Med", "1999", "Concurrent cisplatin-based radiotherapy and chemotherapy for locally advanced cervical cancer"),
    "GOG 123": ("10202166", "Keys", "N Engl J Med", "1999", "Cisplatin, radiation, and adjuvant hysterectomy compared with radiation and adjuvant hysterectomy for bulky stage IB cervical carcinoma"),
    "GOG 99": ("14984936", "Keys", "Gynecol Oncol", "2004", "A phase III trial of surgery with or without adjunctive external pelvic radiation therapy in intermediate risk endometrial adenocarcinoma: a Gynecologic Oncology Group study"),
    "PORTEC-1": ("10791524", "Creutzberg", "Lancet", "2000", "Surgery and postoperative radiotherapy versus surgery alone for patients with stage-1 endometrial carcinoma: multicentre randomised trial. PORTEC Study Group. Post Operative Radiation Therapy in Endometrial Carcinoma"),
    "PORTEC-2": ("20206777", "Nout", "Lancet", "2010", "Vaginal brachytherapy versus pelvic external beam radiotherapy for patients with endometrial cancer of high-intermediate risk (PORTEC-2): an open-label, non-inferiority, randomised trial"),
    "PORTEC-3": ("29449189", "de Boer", "Lancet Oncol", "2018", "Adjuvant chemoradiotherapy versus radiotherapy alone for women with high-risk endometrial cancer (PORTEC-3): final results of an international, open-label, multicentre, randomised, phase 3 trial"),
    "GOG 258": ("31189035", "Matei", "N Engl J Med", "2019", "Adjuvant Chemotherapy plus Radiation for Locally Advanced Endometrial Cancer"),
    "RUBY": ("36972026", "Mirza", "N Engl J Med", "2023", "Dostarlimab for Primary Advanced or Recurrent Endometrial Cancer"),
    "NRG-GY018": ("36972022", "Eskander", "N Engl J Med", "2023", "Pembrolizumab plus Chemotherapy in Advanced Endometrial Cancer"),
    "RTOG 1203": ("29989857", "Klopp", "J Clin Oncol", "2018", "Patient-Reported Toxicity During Pelvic Intensity-Modulated Radiation Therapy: NRG Oncology-RTOG 1203"),
    "LACC": ("30380365", "Ramirez", "N Engl J Med", "2018", "Minimally Invasive versus Abdominal Radical Hysterectomy for Cervical Cancer"),
    "SHAPE": ("38416430", "Plante", "N Engl J Med", "2024", "Simple versus Radical Hysterectomy in Women with Low-Risk Cervical Cancer"),
    "EMBRACE": ("33794207", "Pötter", "Lancet Oncol", "2021", "MRI-guided adaptive brachytherapy in locally advanced cervical cancer (EMBRACE-I): a multicentre prospective cohort study"),
    "INTERLACE": ("39419054", "McCormack", "Lancet", "2024", "Induction chemotherapy followed by standard chemoradiotherapy versus standard chemoradiotherapy alone in patients with locally advanced cervical cancer (GCIG INTERLACE): an international, multicentre, randomised phase 3 trial"),
    "KEYNOTE-A18": ("38521086", "Lorusso", "Lancet", "2024", "Pembrolizumab or placebo with chemoradiotherapy followed by pembrolizumab or placebo for newly diagnosed, high-risk, locally advanced cervical cancer (ENGOT-cx11/GOG-3047/KEYNOTE-A18): a randomised, double-blind, phase 3 clinical trial"),
    "KEYNOTE-826": ("34534429", "Colombo", "N Engl J Med", "2021", "Pembrolizumab for Persistent, Recurrent, or Metastatic Cervical Cancer"),
    "GOG 37": ("3785783", "Homesley", "Obstet Gynecol", "1986", "Radiation therapy versus pelvic node resection for carcinoma of the vulva with positive groin nodes"),
    "GOG 205": ("22079361", "Moore", "Gynecol Oncol", "2012", "A phase II trial of radiation therapy and weekly cisplatin chemotherapy for the treatment of locally-advanced squamous cell carcinoma of the vulva: a gynecologic oncology group study"),
    "GROINSS-V": ("18281661", "Van der Zee", "J Clin Oncol", "2008", "Sentinel node dissection is safe in the treatment of early-stage vulvar cancer"),
    "NCCTG N0574": ("27458945", "Brown", "JAMA", "2016", "Effect of Radiosurgery Alone vs Radiosurgery With Whole Brain Radiation Therapy on Cognitive Function in Patients With 1 to 3 Brain Metastases: A Randomized Clinical Trial"),
    "Mahajan": ("28687375", "Mahajan", "Lancet Oncol", "2017", "Post-operative stereotactic radiosurgery versus observation for completely resected brain metastases: a single-centre, randomised, controlled, phase 3 trial"),
    "N107C": ("28687377", "Brown", "Lancet Oncol", "2017", "Postoperative stereotactic radiosurgery compared with whole brain radiotherapy for resected metastatic brain disease (NCCTG N107C/CEC·3): a multicentre, randomised, controlled, phase 3 trial"),
    "NRG CC001": ("32058845", "Brown", "J Clin Oncol", "2020", "Hippocampal Avoidance During Whole-Brain Radiotherapy Plus Memantine for Patients With Brain Metastases: Phase III Trial NRG Oncology CC001"),
    "JLGK0901": ("24621620", "Yamamoto", "Lancet Oncol", "2014", "Stereotactic radiosurgery for patients with multiple brain metastases (JLGK0901): a multi-institutional prospective observational study"),
    "QUARTZ": ("27604504", "Mulvenna", "Lancet", "2016", "Dexamethasone and supportive care with or without whole brain radiotherapy in treating patients with non-small cell lung cancer with brain metastases unsuitable for resection or stereotactic radiotherapy (QUARTZ): results from a phase 3, non-inferiority, randomised trial"),
    "Stupp (EORTC/NCIC)": ("15758009", "Stupp", "N Engl J Med", "2005", "Radiotherapy plus concomitant and adjuvant temozolomide for glioblastoma"),
    "EF-14": ("29260225", "Stupp", "JAMA", "2017", "Effect of Tumor-Treating Fields Plus Maintenance Temozolomide vs Maintenance Temozolomide Alone on Survival in Patients With Glioblastoma: A Randomized Clinical Trial"),
    "Perry": ("28296618", "Perry", "N Engl J Med", "2017", "Short-Course Radiation plus Temozolomide in Elderly Patients with Glioblastoma"),
    "Roa": ("26392096", "Roa", "J Clin Oncol", "2015", "International Atomic Energy Agency Randomized Phase III Study of Radiation Therapy in Elderly and/or Frail Patients With Newly Diagnosed Glioblastoma Multiforme"),
    "RTOG 9802": ("27050206", "Buckner", "N Engl J Med", "2016", "Radiation plus Procarbazine, CCNU, and Vincristine in Low-Grade Glioma"),
    "INDIGO": ("37272516", "Mellinghoff", "N Engl J Med", "2023", "Vorasidenib in IDH1- or IDH2-Mutant Low-Grade Glioma"),
    "RTOG 9402": ("23071247", "Cairncross", "J Clin Oncol", "2013", "Phase III trial of chemoradiotherapy for anaplastic oligodendroglioma: long-term results of RTOG 9402"),
    "EORTC 26951": ("23071237", "van den Bent", "J Clin Oncol", "2013", "Adjuvant procarbazine, lomustine, and vincristine chemotherapy in newly diagnosed anaplastic oligodendroglioma: long-term follow-up of EORTC brain tumor group study 26951"),
    "CATNON": ("28801186", "van den Bent", "Lancet", "2017", "Interim results from the CATNON trial (EORTC study 26053-22054) of treatment with concurrent and adjuvant temozolomide for 1p/19q non-co-deleted anaplastic glioma: a phase 3, randomised, open-label intergroup study"),
    "RTOG 90-05": ("10802351", "Shaw", "Int J Radiat Oncol Biol Phys", "2000", "Single dose radiosurgical treatment of recurrent previously irradiated primary brain tumors and brain metastases: final report of RTOG protocol 90-05"),
    "Nigro": ("4830803", "Nigro", "Dis Colon Rectum", "1974", "Combined therapy for cancer of the anal canal: a preliminary report"),
    "RTOG 9811": ("18430910", "Ajani", "JAMA", "2008", "Fluorouracil, mitomycin, and radiotherapy vs fluorouracil, cisplatin, and radiotherapy for carcinoma of the anal canal: a randomized controlled trial"),
    "ACT II": ("23578724", "James", "Lancet Oncol", "2013", "Mitomycin or cisplatin chemoradiation with or without maintenance chemotherapy for treatment of squamous-cell carcinoma of the anus (ACT II): a randomised, phase 3, open-label, 2 × 2 factorial trial"),
    "RTOG 0529": ("23154075", "Kachnic", "Int J Radiat Oncol Biol Phys", "2013", "RTOG 0529: a phase 2 evaluation of dose-painted intensity modulated radiation therapy in combination with 5-fluorouracil and mitomycin-C for the reduction of acute morbidity in carcinoma of the anal canal"),
    "CAO/ARO/AIO-94": ("15496622", "Sauer", "N Engl J Med", "2004", "Preoperative versus postoperative chemoradiotherapy for rectal cancer"),
    "RAPIDO": ("33301740", "Bahadoer", "Lancet Oncol", "2021", "Short-course radiotherapy followed by chemotherapy before total mesorectal excision (TME) versus preoperative chemoradiotherapy, TME, and optional adjuvant chemotherapy in locally advanced rectal cancer (RAPIDO): a randomised, open-label, phase 3 trial"),
    "PRODIGE 23": ("33862000", "Conroy", "Lancet Oncol", "2021", "Neoadjuvant chemotherapy with FOLFIRINOX and preoperative chemoradiotherapy for patients with locally advanced rectal cancer (UNICANCER-PRODIGE 23): a multicentre, randomised, open-label, phase 3 trial"),
    "OPRA": ("35483010", "Garcia-Aguilar", "J Clin Oncol", "2022", "Organ Preservation in Patients With Rectal Adenocarcinoma Treated With Total Neoadjuvant Therapy"),
    "PROSPECT": ("37272534", "Schrag", "N Engl J Med", "2023", "Preoperative Treatment of Locally Advanced Rectal Cancer"),
    "CROSS": ("22646630", "van Hagen", "N Engl J Med", "2012", "Preoperative chemoradiotherapy for esophageal or junctional cancer"),
    "RTOG 8501": ("1584260", "Herskovic", "N Engl J Med", "1992", "Combined chemotherapy and radiotherapy compared with radiotherapy alone in patients with cancer of the esophagus"),
    "RTOG 9405": ("11870157", "Minsky", "J Clin Oncol", "2002", "INT 0123 (Radiation Therapy Oncology Group 94-05) phase III trial of combined-modality therapy for esophageal cancer: high-dose versus standard-dose radiation therapy"),
    "ESOPEC": ("39842010", "Hoeppner", "N Engl J Med", "2025", "Perioperative Chemotherapy or Preoperative Chemoradiotherapy in Esophageal Cancer"),
    "CheckMate 577": ("33789008", "Kelly", "N Engl J Med", "2021", "Adjuvant Nivolumab in Resected Esophageal or Gastroesophageal Junction Cancer"),
    "PRODIGE 24": ("30575490", "Conroy", "N Engl J Med", "2018", "FOLFIRINOX or Gemcitabine as Adjuvant Therapy for Pancreatic Cancer"),
    "LAP07": ("27139057", "Hammel", "JAMA", "2016", "Effect of Chemoradiotherapy vs Chemotherapy on Survival in Patients With Locally Advanced Pancreatic Cancer Controlled After 4 Months of Gemcitabine With or Without Erlotinib: The LAP07 Randomized Clinical Trial"),
    "PREOPANC": ("32105518", "Versteijne", "J Clin Oncol", "2020", "Preoperative Chemoradiotherapy Versus Immediate Surgery for Resectable and Borderline Resectable Pancreatic Cancer: Results of the Dutch Randomized Phase III PREOPANC Trial"),
    "RTOG 1112": ("39699905", "Dawson", "JAMA Oncol", "2025", "Stereotactic Body Radiotherapy vs Sorafenib Alone in Hepatocellular Carcinoma: The NRG Oncology/RTOG 1112 Phase 3 Randomized Clinical Trial"),
    "INT-0116": ("11547741", "Macdonald", "N Engl J Med", "2001", "Chemoradiotherapy after surgery compared with surgery alone for adenocarcinoma of the stomach or gastroesophageal junction"),
    "CRITICS": ("29650363", "Cats", "Lancet Oncol", "2018", "Chemotherapy versus chemoradiotherapy after surgery and preoperative chemotherapy for resectable gastric cancer (CRITICS): an international, open-label, randomised phase 3 trial"),
    "RTOG 9714": ("15928300", "Hartsell", "J Natl Cancer Inst", "2005", "Randomized trial of short- versus long-course radiotherapy for palliation of painful bone metastases"),
    "Dutch Bone Metastasis Study": ("10577695", "Steenland", "Radiother Oncol", "1999", "The effect of a single fraction compared to multiple fractions on painful bone metastases: a global analysis of the Dutch Bone Metastasis Study"),
    "TROG 96.05": ("15878101", "Roos", "Radiother Oncol", "2005", "Randomized trial of 8 Gy in 1 versus 20 Gy in 5 fractions of radiotherapy for neuropathic pain due to bone metastases (Trans-Tasman Radiation Oncology Group, TROG 96.05)"),
    "NCIC SC.23": ("26489389", "Chow", "Lancet Oncol", "2015", "Dexamethasone in the prophylaxis of radiation-induced pain flare after palliative radiotherapy for bone metastases: a double-blind, randomised placebo-controlled, phase 3 trial"),
    "NCIC SC.20": ("24369114", "Chow", "Lancet Oncol", "2014", "Single versus multiple fractions of repeat radiation for painful bone metastases: a randomised, controlled, non-inferiority trial"),
    "SC.24": ("34126044", "Sahgal", "Lancet Oncol", "2021", "Stereotactic body radiotherapy versus conventional external beam radiotherapy in patients with painful spinal metastases: an open-label, multicentre, randomised, controlled, phase 2/3 trial"),
    "RTOG 0631": ("37079324", "Ryu", "JAMA Oncol", "2023", "Stereotactic Radiosurgery vs Conventional Radiotherapy for Localized Vertebral Metastases of the Spine: Phase 3 Results of NRG Oncology/RTOG 0631 Randomized Clinical Trial"),
    "Gillespie (MSKCC)": ("37748124", "Gillespie", "J Clin Oncol", "2024", "Prophylactic Radiation Therapy Versus Standard of Care for Patients With High-Risk Asymptomatic Bone Metastases: A Multicenter, Randomized Phase II Clinical Trial"),
    "ORIOLE": ("32215577", "Phillips", "JAMA Oncol", "2020", "Outcomes of Observation vs Stereotactic Ablative Radiation for Oligometastatic Prostate Cancer: The ORIOLE Phase 2 Randomized Clinical Trial"),
    "STOMP": ("29240541", "Ost", "J Clin Oncol", "2018", "Surveillance or Metastasis-Directed Therapy for Oligometastatic Prostate Cancer Recurrence: A Prospective, Randomized, Multicenter Phase II Trial"),
    "Gomez": ("31067138", "Gomez", "J Clin Oncol", "2019", "Local Consolidative Therapy Vs. Maintenance Therapy or Observation for Patients With Oligometastatic Non-Small-Cell Lung Cancer: Long-Term Results of a Multi-Institutional, Phase II, Randomized Study"),
    "CURB": ("38104577", "Tsai", "Lancet", "2024", "Standard-of-care systemic therapy with or without stereotactic body radiotherapy in patients with oligoprogressive breast cancer or non-small-cell lung cancer (Consolidative Use of Radiotherapy to Block [CURB] oligoprogression): an open-label, randomised, controlled, phase 2 study"),
    "NRG-BR002": ("42842849", "Chmura", "J Clin Oncol", "2026", "NRG-BR002: A Randomized Phase II/III Trial of Metastasis-Directed Ablation With First-Line Systemic Therapy for Oligometastatic Breast Cancer"),
    "ALSYMPCA": ("23863050", "Parker", "N Engl J Med", "2013", "Alpha emitter radium-223 and survival in metastatic prostate cancer"),
    "VISION": ("34161051", "Sartor", "N Engl J Med", "2021", "Lutetium-177-PSMA-617 for Metastatic Castration-Resistant Prostate Cancer"),
    "NETTER-1": ("28076709", "Strosberg", "N Engl J Med", "2017", "Phase 3 Trial of (177)Lu-Dotatate for Midgut Neuroendocrine Tumors"),
    "Patchell": ("16112300", "Patchell", "Lancet", "2005", "Direct decompressive surgical resection in the treatment of spinal cord compression caused by metastatic cancer: a randomised trial"),
    "SCORAD III": ("31794625", "Hoskin", "JAMA", "2019", "Effect of Single-Fraction vs Multifraction Radiotherapy on Ambulatory Status Among Patients With Spinal Canal Compression From Metastatic Cancer: The SCORAD Randomized Clinical Trial"),
    "ICORG 05-03": ("32157242", "Thirion", "Br J Cancer", "2020", "Non-inferiority randomised phase 3 trial comparing two radiation schedules (single vs. five fractions) in malignant spinal cord compression"),
    "Mahler (osteoarthritis sham trials)": ("30366945", "Mahler", "Ann Rheum Dis", "2019", "Effectiveness of low-dose radiation therapy on symptoms in patients with knee osteoarthritis: a randomised, double-blinded, sham-controlled trial"),
    "Niewald": ("22836057", "Niewald", "Int J Radiat Oncol Biol Phys", "2012", "Randomized, multicenter trial on the effect of radiation therapy on plantar fasciitis (painful heel spur) comparing a standard dose with a very low dose: mature results after 12 months' follow-up"),
    "ARUBA": ("24268105", "Mohr", "Lancet", "2014", "Medical management with or without interventional therapy for unruptured brain arteriovenous malformations (ARUBA): a multicentre, non-blinded, randomised trial"),
    "GHSG HD10": ("20818855", "Engert", "N Engl J Med", "2010", "Reduced treatment intensity in patients with early-stage Hodgkin's lymphoma"),
    "GHSG HD11": ("20713848", "Eich", "J Clin Oncol", "2010", "Intensified chemotherapy and dose-reduced involved-field radiotherapy in patients with early unfavorable Hodgkin's lymphoma: final analysis of the German Hodgkin Study Group HD11 trial"),
    "RAPID": ("25901426", "Radford", "N Engl J Med", "2015", "Results of a trial of PET-directed therapy for early-stage Hodgkin's lymphoma"),
    "H10": ("28291393", "André", "J Clin Oncol", "2017", "Early Positron Emission Tomography Response-Adapted Treatment in Stage I and II Hodgkin Lymphoma: Final Results of the Randomized EORTC/LYSA/FIL H10 Trial"),
    "HD16": ("31498753", "Fuchs", "J Clin Oncol", "2019", "Positron Emission Tomography-Guided Treatment in Early-Stage Favorable Hodgkin Lymphoma: Final Results of the International, Randomized Phase III HD16 Trial by the German Hodgkin Study Group"),
    "FORT": ("24572077", "Hoskin", "Lancet Oncol", "2014", "4 Gy versus 24 Gy radiotherapy for patients with indolent lymphoma (FORT): a randomised phase 3 non-inferiority trial"),
    "NCIC SR2": ("12103287", "O'Sullivan", "Lancet", "2002", "Preoperative versus postoperative radiotherapy in soft-tissue sarcoma of the limbs: a randomised trial"),
    "STRASS": ("32941794", "Bonvalot", "Lancet Oncol", "2020", "Preoperative radiotherapy plus surgery versus surgery alone for patients with primary retroperitoneal sarcoma (EORTC-62092: STRASS): a multicentre, open-label, randomised, phase 3 trial"),
    "BC2001": ("22512481", "James", "N Engl J Med", "2012", "Radiotherapy with or without chemotherapy in muscle-invasive bladder cancer"),
    "COMS": ("17159027", "COMS Group", "Arch Ophthalmol", "2006", "The COMS randomized trial of iodine 125 brachytherapy for choroidal melanoma: V. Twelve-year mortality rates and prognostic factors: COMS report No. 28"),
    "ANZMTG/TROG": ("22575589", "Burmeister", "Lancet Oncol", "2012", "Adjuvant radiotherapy versus observation alone for patients at risk of lymph-node field relapse after therapeutic lymphadenectomy for melanoma: a randomised trial"),
    "MRC TE18": ("15718317", "Jones", "J Clin Oncol", "2005", "Randomized trial of 30 versus 20 Gy in the adjuvant treatment of stage I Testicular Seminoma: a report on Medical Research Council Trial TE18, European Organisation for the Research and Treatment of Cancer Trial 30942 (ISRCTN18525328)"),
    "EORTC 62991": ("23868907", "Keus", "Ann Oncol", "2013", "Results of a phase II pilot study of moderate dose radiotherapy for inoperable desmoid-type fibromatosis--an EORTC STBSG and ROG study (EORTC 62991-22998)"),
}

# Names used in trial boxes or curriculum.json that are not keys above.
# Combined box names ("A / B", "A + B", "A & B") are split automatically.
ALIASES = {
    "Gillespie (MSKCC, 2024)": ["Gillespie (MSKCC)"],
    "Patchell (2005)": ["Patchell"],
    "NCIC SR2 (O'Sullivan)": ["NCIC SR2"],
    "GHSG HD10/HD11": ["GHSG HD10", "GHSG HD11"],
    "EORTC 22881 boost trial": ["EORTC 22881"],
    "Tata Memorial (elective neck)": ["Tata Memorial"],
    "1999 Cisplatin Trials": ["RTOG 9001", "GOG 85", "GOG 109", "GOG 120", "GOG 123"],
    "SWOG 8797": ["GOG 109"],
    "SWOG 9416 / INT 0160": ["SWOG 9416 / INT 0160"],
    "HD11": ["GHSG HD11"],
}

# Guidelines and other non-trial sources linked from the readings.
GUIDELINES = {
    "ASTRO bone metastases guideline (2024)": ("https://pubmed.ncbi.nlm.nih.gov/38788923/", "Alcorn et al., Pract Radiat Oncol 2024"),
    "NICE NG234": ("https://www.nice.org.uk/guidance/ng234", "Spinal metastases and metastatic spinal cord compression, NICE 2023"),
    "NICE IPG573": ("https://www.nice.org.uk/guidance/ipg573", "Radiation therapy for early Dupuytren's disease, NICE 2016"),
    "EUGOGO 2021": ("https://pubmed.ncbi.nlm.nih.gov/34297684/", "Bartalena et al., Eur J Endocrinol 2021"),
}


def build():
    trials = {}
    for k, (pmid, au, j, y, t) in TRIALS.items():
        group = au in ("EBCTCG", "VA Laryngeal Cancer Study Group", "COMS Group")
        trials[k] = {"pmid": pmid, "cite": f"{au}, {j} {y}" if group else f"{au} et al., {j} {y}", "title": t,
                     "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"}
    for a, keys in ALIASES.items():
        for k in keys:
            assert k in trials, (a, k)
    return {"trials": trials, "aliases": ALIASES,
            "guidelines": {k: {"url": u, "cite": c} for k, (u, c) in GUIDELINES.items()}}


def verify():
    import time, urllib.request
    ids = [v[0] for v in TRIALS.values()]
    bad = 0
    for i in range(0, len(ids), 80):
        u = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids[i:i + 80])
        r = json.loads(urllib.request.urlopen(u, timeout=30).read())["result"]
        for k, (pmid, au, j, y, t) in TRIALS.items():
            if pmid not in r:
                continue
            if r[pmid]["title"].rstrip(".") != t:
                bad += 1
                print("MISMATCH", k, pmid, r[pmid]["title"])
            # A matching title is not enough: NEJM letters reuse the trial's title.
            pt = set(r[pmid].get("pubtype", []))
            if pt & {"Letter", "Comment", "Editorial"} or "reply" in r[pmid]["title"].lower():
                bad += 1
                print("NOT A PRIMARY REPORT", k, pmid, sorted(pt))
        time.sleep(0.5)
    print("verified", len(ids), "PMIDs;", bad, "mismatches")


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        p = os.path.join(ROOT, "src", "data", "sources.json")
        with open(p, "w", encoding="utf8") as f:
            json.dump(build(), f, ensure_ascii=False, indent=1)
        print("wrote", os.path.relpath(p, ROOT), len(TRIALS), "trials")
