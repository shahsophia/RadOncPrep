# Flashcard review against the readings (October 17, 2026)

A targeted quality pass over every flashcard on the site. The readings were rewritten
(October 8 onward) after the last full flashcard audit, so this pass checked every card
against the reading it now sits under. The aim was to fix real problems, not to restyle
the decks: wording was left alone wherever a card already tested an important concept
clearly and accurately.

## Method

- **Source of truth:** `src/data/decks/*.json` (cards are maintained by hand; no
  generator). `python3 build.py` embeds them as `DECKS`. Card `category` must equal a
  reading section name in `src/data/docs/<site>.json` (or, for the overview deck, a
  `BACKGROUND_FLASHCARD_MAP` entry in `src/app.js`).
- Each reading section was read as plain text next to its cards. For every card:
  what it tests, whether the reading teaches it, whether it is foundational and new to a
  student, whether the answer is accurate and qualified, and whether it duplicates
  another card or can be guessed from the deck's patterns.
- Each deck was then reviewed as a whole for coverage, redundancy, and predictable
  answers (especially staging).
- Edits were applied with a script so untouched cards keep their exact text. Removed
  card IDs are not reused; new concepts get new IDs. Saved progress for a removed ID is
  simply ignored (stats iterate over the deck, not over saved state).

## Results

| | Count |
|---|---|
| Cards reviewed | 394 |
| Kept unchanged | 368 |
| Minor edits | 16 |
| Rewritten (same ID) | 4 |
| Removed | 6 |
| Added | 7 |
| Cards after review | 395 |

| Deck | Before | Kept | Minor | Rewrite | Removed | Added | After |
|---|---|---|---|---|---|---|---|
| Thoracic | 43 | 42 | 1 | 0 | 0 | 1 | 44 |
| Head & Neck | 42 | 40 | 2 | 0 | 0 | 0 | 42 |
| Breast | 38 | 35 | 2 | 0 | 1 | 1 | 38 |
| Prostate | 44 | 40 | 3 | 0 | 1 | 1 | 44 |
| GYN | 39 | 39 | 0 | 0 | 0 | 0 | 39 |
| GI | 40 | 36 | 3 | 0 | 1 | 1 | 40 |
| CNS | 43 | 40 | 1 | 1 | 1 | 0 | 42 |
| Palliative & Benign | 57 | 54 | 2 | 1 | 0 | 0 | 57 |
| Before You Start | 48 | 42 | 2 | 2 | 2 | 3 | 49 |

The decks were already in good shape. Most problems were cards testing something the
rewritten readings no longer teach (mostly in Before You Start), Extras that overstated
a trial, and a few places where staging was tested by one card with one answer.

## Patterns corrected

- **Staging with a single answer.** Thoracic had one N-stage card (station 7, always
  N2). Added thx-67 (a right-sided tumor with a station 5 node is N3), so the two cards
  test the side rule from opposite directions.
- **"Supraclavicular = regional" across decks.** Lung (N3) and breast (cN3c) both teach
  that a supraclavicular node is still curable. Esophagus is the opposite (generally M1),
  and prostate already teaches common iliac = M1a. Added gix-64 so students learn the
  rule per site instead of one reflex.
- **Definitions without application.** Prostate listed the risk-group factors but never
  asked students to count them for a patient; added prx-72. Breast had no stage
  application; added br-59 (a small tumor with a supraclavicular node is still IIIC and
  curable).
- **Epidemiology and generic cards.** Removed prx-2 (a mortality statistic whose
  clinical point is already prx-4), gix-57 (T = depth, N = count, which students know),
  and br-2 (redundant with br-5). Merged cnsx-1 into cnsx-2 so the three "most common
  tumor" answers are tested together, as the reading's pearl intends. Remaining
  percentages sit in Extras, where they are context rather than tested facts.
- **Cards testing content outside the reading.** Before You Start had four: ov-26 (cell
  cycle phases), ov-88 (dose build-up), ov-95 (parotid mean dose), and ov-96 (CTCAE).
  Two were rewritten to the objective the reading teaches; two were replaced with
  objectives the reading teaches but no card tested (ov-107, ov-109). Added ov-108 (the
  one-liner).

Near-duplicate questions remaining are deliberate contrast pairs (definitive vs
postoperative H&N dose; operable vs inoperable early lung; acute vs late prostate
effects; GBM vs metastasis MRI). A few high-yield emergencies appear in two decks on
purpose because both readings teach them: cord compression first steps (cnsx-60,
pal-27), SINS (cnsx-65, pal-10), SABR-COMET (thx-50, pal-23), AVM radiosurgery
(cnsx-52, pal-46 to pal-48).

## Changes by card

### Thoracic

| Card | Change | Reason |
|---|---|---|
| thx-44 | Minor edit | Trial percentages and the ~45-50 Gy dose were not in the reading; kept the sequence and the trial's take-home. |
| thx-67 | Added | Only one card asked for an N stage (station 7, answer N2); this applies the left-sided station rule from the reading and gives a different answer. |

### Head & Neck

| Card | Change | Reason |
|---|---|---|
| hn-51 | Minor edit | Extra said levels II-IV are covered "usually on both sides", which conflicts with the reading and with hn-53 on ipsilateral treatment. |
| hn-32 | Minor edit | PARSPORT compared IMRT with conventional RT, not 3D; matched the reading. |

### Breast

| Card | Change | Reason |
|---|---|---|
| br-2 | Removed | Redundant with br-5 (the three receptor groups and their systemic backbone already require ER/PR and HER2), and the Extra repeated br-4 and br-58. |
| br-59 | Added | Applies the "N3 is still curable" rule from the reading to a patient. |
| br-35 | Minor edit | Supraclavicular-node content moved to br-59. |
| br-26 | Minor edit | Extra framed Z0011 patients as an "exception" to RNI, which blurred br-57; replaced with the nodal-burden rule the reading teaches. |

### Prostate

| Card | Change | Reason |
|---|---|---|
| prx-2 | Removed | Mostly an epidemiology statistic; its one clinical point (start screening talks earlier for Black men) is already the answer to prx-4. |
| prx-4 | Minor edit | Absorbed the disparity fact from prx-2. |
| prx-72 | Added | The deck listed the risk-group definitions but never asked students to count factors for a patient, which is how the reading teaches it. |
| prx-15 | Minor edit | The ~60 cc cutoff is not in the reading; kept the reading's reason (pubic arch interference). |
| prx-49 | Minor edit | "Routine adjuvant RT added nothing" overstated the trials; matched the reading. |

### GYN

All 39 cards kept. The deck already covers the cervix FIGO ladder with varied answers
(IB1-3, IIB, IIIA, IIIB, IIIC1/2, IVA), the clinical vs surgical staging split, and the
postoperative Sedlis/Peters decision.

### GI

| Card | Change | Reason |
|---|---|---|
| gix-57 | Removed | Generic definition (T = depth, N = node count); the exceptions it mentions each have their own card (gix-27, gix-30, gix-35). |
| gix-64 | Added | No esophageal staging card existed; the reading flags this trap, and it breaks the "supraclavicular = N3" pattern from lung and breast. |
| gix-27 | Minor edit | Added the anal T4 trap from the reading (sphincter or skin alone is not T4). |
| gix-12 | Minor edit | "The strongest predictor of local recurrence" is stronger than the reading's claim. |
| gix-21 | Minor edit | "Better than nodal status" is stronger than the reading's claim. |

### CNS

| Card | Change | Reason |
|---|---|---|
| cnsx-1 | Removed | Merged into cnsx-2. |
| cnsx-2 | Rewrite | Now asks for all three "most common" answers together (metastases, meningioma, glioblastoma), the distinction the reading's pearl emphasizes. |
| cnsx-39 | Minor edit | "Nearly doubled survival" overstated RTOG 9802 (median about 13 vs 8 years). |

### Palliative & Benign

| Card | Change | Reason |
|---|---|---|
| pal-7 | Minor edit | The reading names four inputs (goal, prognosis, urgency, stability); the card said three and left out urgency. |
| pal-17 | Minor edit | "About 20% vs 8%" blended two trials; now uses the RTOG 9714 numbers the reading gives (18% vs 9%). |
| pal-37 | Rewrite | A dose schedule for a low-evidence benign condition is a narrow detail; the card now tests how strong the evidence is and how to describe the benefit. The regimen moved to the Extra. |

### Before You Start

| Card | Change | Reason |
|---|---|---|
| ov-26 | Rewrite | Cell-cycle phase sensitivity (M vs late S) is not taught in How Radiation Works; the card now tests redistribution, which the reading does teach. The phases stay in the Extra. |
| ov-31 | Minor edit | Matched the reading's framing (fraction-size sensitivity) and named prostate cancer in the answer; the ~10 and ~3 values moved to the Extra. |
| ov-54 | Minor edit | Added the consequence the reading stresses: tumors shrink over weeks to months, so an end-of-treatment scan underestimates response. |
| ov-88 | Removed | Tested the dose build-up region (Dmax), which Radiation Modalities does not teach. |
| ov-107 | Added | Why SRS/SBRT can safely use 1-5 large fractions (the reading's exception to fractionation). |
| ov-96 | Rewrite | CTCAE is not in How to Give a Presentation; the card now tests the reading's weekly-visit principle (side effects build and peak at the end), with CTCAE kept as context. |
| ov-108 | Added | The four parts of a one-liner, the first skill the presentation reading builds. |
| ov-95 | Removed | Tested a parotid mean-dose number that neither Treatment Planning nor the H&N reading teaches; parotid sparing is covered by hn-32 and ov-33. |
| ov-109 | Added | When a target touches the cord, the plan gives up a little edge coverage to respect the cord limit, a decision the reading spells out. |

## Gaps that need a content decision

These are places where a card and a reading disagree about what students should know.
Each needs a decision about the reading, not just the card.

1. **Parotid dose goal.** The H&N reading names the parotids as the main gland to spare
   but gives no number. If the reading adds the common mean-dose goal, a card can return
   in the H&N deck.
2. **Dose build-up and skin sparing.** Radiation Modalities no longer explains why
   megavoltage photons spare the skin or why bolus is used, although the breast reading
   relies on bolus for PMRT.
3. **Normal-tissue limits in Before You Start.** ov-34 (cord about 50 Gy) and ov-35
   (brainstem and optic structures about 54 Gy) appear at the end of Treatment Planning,
   which lists these organs but gives no numbers. The numbers are taught in the thoracic
   and CNS readings. Consider one line in Treatment Planning, or accept that these cards
   preview later readings.
4. **Simultaneous integrated boost (ov-12)** and **concurrent chemo as a
   radiosensitizer (ov-80)** are tested in Before You Start but explained only in passing
   in the site readings.
5. **Hypopharynx** has a short paragraph in the H&N reading and no card. This is
   proportionate; listed only for completeness.

## Clinical accuracy items for review

No card now conflicts with its reading. These are smaller details in answers or Extras
that the reading does not state and that this pass did not check against a source:

- gix-64: supraclavicular nodes as M1 for esophageal cancer follows the reading
  ("generally considered distant"). Worth a quick expert check for cervical and upper
  thoracic primaries, where supraclavicular nodes are often in the field.
- thx-39 Extra: RTOG 0236 local control "around 90-95%" vs the reading's "nearly all
  patients at 3 years" (primary tumor control vs primary plus lobe). Both are defensible;
  consider using one.
- thx-64: PCI dose 25 Gy in 10 is not in the thoracic reading.
- hn-10 Extra: early glottic nodal risk "about 2-5%" is not in the reading.
- cnsx-62: the "over ~3-4 cm" surgery threshold is not in the reading (the reading says
  large, mass effect, hydrocephalus, or tissue needed).
- pal-47: "often 18-22 Gy" for AVM SRS is not in the reading (which gives 16-25 Gy).
- gynx-46: names carboplatin/paclitaxel; the reading says systemic therapy.

The open items in docs/audit/AUDIT_REPORT.md (expert-review queue) are unchanged by
this pass.

## Validation

- `python3 tools/style_check.py`: 0 problems.
- `python3 build.py`: built dist/index.html (15,708 KB, under the 16 MB limit).
- All deck files parse; 395 unique IDs; every card has id, category, front, back, and
  extra; every category matches a reading section.
- Preview check: the built page loads with no console errors; `DECKS` holds 395 cards;
  the thoracic Anatomy & Lymphatics session shows 5 cards including thx-67, and reveal
  and grading work.
- `tools/audit/builder_tests.js` was not run (Node is not installed); it tests the staging
  builders in app.js, which this pass did not touch.
