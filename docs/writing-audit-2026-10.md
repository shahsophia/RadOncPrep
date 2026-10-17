# Writing and Style Audit (October 2026)

This was an editing pass over all user-facing text against the new [style guide](style-guide.md). The visual design, layout, navigation, IDs, schemas, and clinical content did not change.

## What was reviewed

| Content type | Source of truth | How it was checked |
|---|---|---|
| Before You Start readings (6) | `tools/background_readings.py` | Pattern search, targeted edits, regenerated |
| Disease-site readings (7 sites, 38 pages) | `src/data/docs/*.json` | Pattern search, sampled reading, targeted edits |
| Palliative & Benign readings (7) | `tools/palliative_readings.py` | Pattern search, regenerated |
| High-Yield Summary boxes | `tools/hy_summaries.py` | Pattern search, regenerated |
| Flashcards (9 decks) | `src/data/decks/*.json` | Pattern search, random sample read |
| Clinical cases (66) | `tools/cases/*_cases.py` | Pattern search, sample read, regenerated |
| Curriculum metadata (ledes, objectives, attending questions) | `src/data/curriculum.json` | Pattern search, targeted edits |
| Anatomy and imaging plates (blurbs, captions, intros) | `src/data/anatomy/*.json`, `src/data/imaging/*.json` | Full read of Head & Neck, pattern search elsewhere |
| Quick checks, staging builders, interface text, empty states | `src/app.js` | Pattern search, full read of the Head & Neck quick checks |
| Page shell and homepage copy | `src/index.template.html` | Contractions only (the homepage is frozen) |
| Trial citations | `tools/sources.py` → `src/data/sources.json` | Regenerated; no edits (titles are literal) |

All eight generators were rerun after editing, and every regenerated JSON file was byte-identical to the edited data. That confirms the sources and the generated files agree.

## Changes by category

1. **Contractions: 417 removed from user-facing text.** By content type: readings 225, cases 45, flashcards 29, curriculum 15, imaging plates 15, anatomy plates 6, and `app.js` plus the page shell 82. The same expansions were made in the Python generators (about 70 duplicate occurrences) and in a few JS code comments, so a rebuild cannot bring them back.
2. **Questions that the expansion would have garbled: 15 rewritten by hand.** For example, "Why isn't chemotherapy given at the same time as breast radiation?" became "Why is chemotherapy not given at the same time...?", and "Why don't we treat stage III NSCLC to 74 Gy?" became "Why is stage III NSCLC not treated to 74 Gy?"
3. **Em dashes: 0 found in user-facing text.** Earlier rewrites had already removed them. The two remaining literal em and en dashes in the repo are inside the generators' own "refuse to write a dash" checks. Sentence-level en dashes: also 0.
4. **Spaced hyphens used as dashes: 33 replaced** (16 in the Head & Neck quick checks in `app.js`, 10 in Head & Neck anatomy blurbs, and 7 in Head & Neck imaging). Each was replaced with a comma, a colon, or a new sentence, chosen to fit the sentence. Four plate titles changed from "Oral Cavity - MRI" to "Oral Cavity: MRI" to match the other sites.
5. **Filler and AI-sounding phrasing.** Searches for stock phrases ("it is important to note," "plays a key role," "when it comes to," "in the realm of," "delve," "pivotal," "cornerstone," and similar) returned almost nothing. Earlier rewrites had removed most of them. What remained and was fixed:
   - "Actually" and "really" used for emphasis in about two dozen headings, ledes, table headers, and blurbs. For example, "What Are We Actually Treating?" became "What Are We Treating?", and the GI table header "Staging really asks about" became "What staging asks".
   - Generic sentences rewritten to say something concrete. The CNS opener "Radiation plays an important role in many CNS tumors" now says what decides surgery, systemic therapy, observation, or radiation.
   - "Workhorse" (4), "basically geography," "a classic pimp point," and "The key is to..." were rewritten in plain teaching language.
   - Head & Neck quick-check questions were tightened. They were written in a more formal register than the rest of the site ("What is the surrogate IHC marker used clinically to identify...").
6. **Units and slashes.** Missing spaces between numbers and units were fixed ("1.8cm" to "1.8 cm", "7mm" to "7 mm"; about a dozen values, all in Head & Neck). Some slash pairs in prose were spelled out ("smoker/drinker" became "smoker and drinker").

## Exceptions that remain on purpose

- **`BC - Hirnmetastasen MRT T1KM ax`** (CNS imaging caption). This is the literal Wikimedia Commons file title in an attribution, so it is allowlisted in `tools/style_check.py`.
- **Paper titles in `sources.json`** are reproduced as published. None contained a contraction or dash.
- **Homepage.** Only contractions were expanded (4 on the home view). Its prose and layout were not rewritten because the homepage is frozen.
- **Math in code.** Minus signs in `app.js` and the generators (for example, `(Gleason - 6)` in the Roach formula) are arithmetic, not punctuation.
- **Possessives** ("patient's," "Barrett's," "Broca's") are not contractions and were left alone.

## Needs clinical review

These came up while editing. The wording was kept or only lightly adjusted, and the claims were not changed.

1. **NPC retropharyngeal nodes** (`anatomy/headneck.json`, Level VII blurb in the nasopharynx plate): "Nearly all patients have retropharyngeal nodal involvement at diagnosis." Published series more often report about two-thirds. The claim may be overstated.
2. **PET for perineural recurrence vs radiation neuritis** (`app.js`, `hn-imaging` quick check). The original question described "an FDG-avid area" and then asked how PET tells the two apart, which contradicted itself. The question now says "a possible abnormality." The answer's claim that radiation neuritis is typically not FDG-avid should be confirmed.
3. **Glottic nodal risk.** One blurb gives "~2% for T1" and another gives "~2-5%" for T1-T2. Both are defensible, but a reviewer may want one figure.
4. **"Only two definite indications" for postoperative chemoradiation** in H&N (ENE, positive margin). This is the standard teaching from the pooled EORTC 22931 and RTOG 9501 analysis. It is worth confirming that it matches how the readings phrase it elsewhere.

## Validation

- `python3 build.py`: built `dist/index.html` (15.7 MB, 281 embedded images).
- All 44 JSON files under `src/data/` parse.
- `app.js` parses (JavaScriptCore). All Python sources compile.
- `tools/audit/builder_tests.js` run in the browser: 249 tests, 0 failures (lung, prostate, cervix, and glioma builders).
- No console errors on load.
- `python3 tools/style_check.py`: 0 problems. Run against the pre-edit tree, it reports 417 contractions and 33 spaced-hyphen dashes, so it does catch what it is meant to catch.
- A rendered sweep of all 44 reading pages in the browser found no contractions or dashes except the allowlisted file title.
- The edited Head & Neck pages were spot-checked in the browser.

## Worth a second editing pass

- **Case intros** repeat one template across all eight sites ("Eight cases that get harder as you go... Each starts with a one-liner, then gives you more information step by step: ..."). This is consistent, but formulaic.
- **"Why it matters" table columns** appear in CNS, GI, H&N, palliative, and thoracic readings. The repetition is useful as a pattern, but some pages could use a more specific header.
- **"Classic"** shows up about 60 times ("classic presentation," "classic trap," "classic example"), most heavily in the H&N anatomy plates and the CNS and thoracic decks.
- **Head & Neck anatomy blurbs** still lean on slash shorthand ("oropharynx/tonsil," "IIa/IIb") more than other sites do.
- **Quick checks in `app.js` for sites other than Head & Neck** were checked by pattern search and sampling, not read line by line.
- **"Multidisciplinary"** recurs often in the GI and Palliative readings. It is accurate each time, but dense on a few pages.
