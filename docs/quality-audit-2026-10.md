# Quality audit and upgrade, October 2026

Scope: Palliative & Benign (all seven readings, 56 cards, 10 cases), the six
Before You Start readings, site-wide references, cross-site consistency for
shared topics, images, and technical checks. Clinical statements were checked
against PubMed abstracts or full text and the named guidelines (October 16-17,
2026). This is not a full clinical validation of the site; see "Still needs
expert review" at the end.

Priority key: **P0** potentially misleading clinical claim, unsafe omission, or
broken core function. **P1** important educational, evidence, visual, or
usability gap. **P2** editorial consistency or polish.

## P0: corrected

| # | File / section | Problem | Fix | Verified by |
|---|---|---|---|---|
| 1 | `tools/palliative_readings.py`, Palliative Radiation (SBRT) | RTOG 0631 described as SBRT "not improving" pain relief. The primary endpoint actually favored 8 Gy in 1 (pain response 61% vs 41%). | Reworded in reading, card pal-21, HY summary; "higher dose is not automatically better pain relief" now taught alongside SC.24. | Ryu et al., JAMA Oncol 2023 (PMID 37079324) |
| 2 | Background & Epidemiology | Universal dose rule ("a few Gy calms inflammation, 8-30 Gy relieves symptoms, 50-80 Gy cures cancer") presented as defining intent. | Removed. New "Name the Intent Before the Dose" table (palliative, prophylactic, emergency, ablative/definitive) and text that dose ranges overlap and cannot define intent. | Internal consistency with Other Sites (24 Gy curative lymphoma, 50-56 Gy desmoid) |
| 3 | Background emergency table | Implied every emergency gets radiation "within hours to a day." | Table now lists what usually comes first (steroids, MRI, surgeon, stent, resuscitation, biopsy). Emergencies reading adds "how fast radiation helps." | NICE NG234; ASTRO 2024 guideline (PMID 38788923) |
| 4 | Benign Disease, heterotopic ossification; case 4; card pal-39 | "Shield uncemented porous components" taught as a universal instruction. | Now described as institution-dependent, with the 2022 series showing unshielded low-dose preoperative RT did not increase loosening. Case step rewritten. | PMID 35133992; Pakos meta-analysis PMID 15465207 |
| 5 | Benign Disease opening | "Doses so low they would never control a cancer." Wrong for desmoid (50-56 Gy) and inconsistent with the site's own content. | Replaced with three dose/goal groups including tumor-level doses for benign tumors. | EORTC 62991 (PMID 23868907) |
| 6 | Functional & Vascular SRS (AVM latency); case 8; cards pal-48; CNS Treatment Paradigms; CNS card cnsx-52 | "Bleeding risk remains until obliteration" implied no protection during latency (and CNS said 2-3 years). | Risk is lower but not gone during latency; best protection after obliteration, usually 1-3 years. Aligned in CNS. | Maruyama et al., NEJM 2005 (PMID 15647577) |
| 7 | Palliative Radiation, Gillespie; case 9; card pal-22; HY summary | Survival benefit stated as a finding without noting it was a secondary, underpowered endpoint; eligibility (more than 5 metastases, ECOG 0-2) and the SRE definition (includes RT for pain) omitted. | All added; framed as promising phase II needing phase III confirmation, not a universal standard. | Gillespie et al., JCO 2024 (PMID 37748124) full text |
| 8 | Case 2 (cord compression) | Intended answer (surgery then RT) was not fully supported by the stem; breast cancer is relatively radiosensitive, so RT alone was also defensible. | Stem now gives mechanical pain, collapse, SINS 12, and prognosis; explanation covers why RT alone would be reasonable if the spine were stable. | Patchell (PMID 16112300); NOMS (PMID 23709750) |
| 9 | Workup & Prognosis, Mirels; builder | Threshold taught only as "9 or more" without noting Mirels' original recommendation (fixation at 8 or more) or poor specificity. | Added in reading, builder text, card pal-14. | Mirels 1989 (PMID 2684463) |

## P1: implemented

- **Palliative visuals (original HTML/CSS):** factor map (goal, prognosis, urgency, stability, preference); palliative consult checklist; pre-consult bone checklist; single vs multiple fraction bar chart drawn to scale from Chow 2012 and RTOG 9714; pain-flare and response timeline; NOMS 2x2 grid with M and S gates; cord compression, SVC, and bleeding/airway decision pathways; benign comparison with plain-language evidence labels; trigeminal neuralgia vs AVM response timeline. All tested in light and dark mode and at 375 px wide.
- **Palliative Radiation reorganized** around the three requested questions, with a definition of "uncomplicated" bone metastasis and new card pal-57.
- **Evidence nuance:** SC.20 (noninferior by intention-to-treat only), SC.23 vs the later Dutch dexamethasone trial, SCORAD III (noninferiority not met at 8 weeks), SABR-COMET (relaxed phase II threshold, 4.5% treatment-related deaths), osteoarthritis (sham trials negative, labeled contested), Dupuytren (NICE IPG573: evidence inadequate), gynecomastia (tamoxifen more effective), trigeminal neuralgia outcomes from an 871-patient series.
- **Scores framed as decision support** (SINS, Bilsky, Mirels, prognostic models), with four kinds of bone pain (biologic, mechanical, neuropathic, neurologic compromise).
- **Site-wide verified sources:** `tools/sources.py` holds PubMed IDs for every trial named in `curriculum.json` (155), each checked against the PubMed record; `--verify` re-checks them. All 83 trial boxes across the eight sites now show a "Source" line, and "Trials cited here" and Sources & References link each trial to PubMed.
- **Treatment Planning figures:** the nested target-volume figure clipped its legend and the isodose figure hard-coded a dark background. Both are now HTML/CSS; the DVH was redrawn with readable axes and a V20 reading in place of a "D_mean" point (mean dose is not read as a point on a cumulative DVH).
- **Curriculum metadata** for Palliative & Benign updated to match (ledes, essentials, objectives, core trials, guideline name).

## P2: implemented

- Removed double numbering in Palliative Radiation headings.
- `src/data/docs/overview.json` was not reachable from any page (the Before You Start readings live in `background.json`) and was embedded in every build. Moved to `docs/legacy-overview-docs.json`.
- External links open in a new tab with `rel="noopener"` and a small arrow marker.

## Reviewed, no change needed

- Radiation Modalities figures (`tools/bys_figures.py`): theme-aware, no text outside the viewBox, render cleanly.
- Other sites' Treatment Paradigms already open with a decision framework, keep visible tables at 9 rows or fewer, and put NCCN detail in tab tables at the end. Restructuring them wholesale would not improve learning, so it was not done.
- Images: 211 unique JPEGs, already deduplicated, none over 1400 px, 45-105 KB each. A lossy WebP re-encode of already recompressed JPEGs was not done, to avoid degrading diagnostic detail (and it would need a package download). The build is about 15.7 MB, under 16 MB, and remains a single offline file.

## Tests run

JSON validation of every data file; duplicate card IDs (394 cards) and case IDs (66 cases): none; no em or en dashes in `src/data`; `app.js` parsed with JavaScriptCore; `python3 build.py`; every reading on every site opened with no console errors; trial box source links (83 of 83) and curriculum trial resolution (all); SINS, Mirels, lung stage builder, anatomy plate explore and quiz mode, contour exercises, fractionation drill, flashcard session, and a palliative case stepped through to the corrected explanation; light, dark, and 375 px layouts for the new figures; homepage markup and computed styles compared with the previous build (identical except the automatic flashcard total, 393 to 394); external resources (only the existing Google Fonts, which fall back offline).

## Still needs expert review

- Representative benign regimens vary by institution (keloid, Dupuytren interval, Graves orbitopathy dose); confirm against local practice.
- NICE NG234 details (dexamethasone 16 mg, MRI within 24 hours) were confirmed through secondary summaries because nice.org.uk blocked automated access; check the guideline page directly.
- Plasmacytoma dose range (35-50 Gy) and thymoma PORT indications are summarized from general knowledge rather than a single cited guideline.
- Other sites' readings were checked for consistency on shared topics only (spine metastases, AVM, trials shared with Palliative & Benign). A line-by-line clinical review of Head & Neck, Breast, Thoracic, Prostate, GYN, CNS, and GI against current NCCN versions was out of scope here.
- Thoracic card thx-50 ("Gomez and SABR-COMET showed better survival") should note both were randomized phase II. Handed to the concurrent clinical-accuracy audit session, which owns `decks/thoracic.json`.
