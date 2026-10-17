# Writing Style Guide

This guide covers every piece of text a student sees: readings, flashcards, cases, quick checks, anatomy and imaging blurbs, captions, tables, and interface copy. The reader is a medical student getting ready for a radiation oncology sub-internship. Write the way a resident explains something on rotation: clearly, specifically, and without filler.

Run `python3 tools/style_check.py` before a build. It flags contractions, em and en dashes, and spaced hyphens used as dashes in user-facing text.

## Mechanical rules

- **No contractions.** Write "do not," "cannot," "it is," "you will." Turn inverted questions around so they still read naturally: "Why is SBRT not used for node-positive disease?" and not "Why is not SBRT used...?"
- **No em dashes, and no en dashes or spaced hyphens used as sentence punctuation.** Use a comma, colon, semicolon, parentheses, or a new sentence. Keep a hyphen for compound modifiers ("node-positive," "short-course").
- **Ranges use a plain hyphen with no spaces:** 45-50.4 Gy, 1-3 positive nodes, 2020-2024. Do not write "45 to 50.4 Gy" in one place and "45-50.4 Gy" in the next sentence.
- **Exclamation points:** none.
- **Slashes:** fine in fixed clinical shorthand (ER/PR, PET/CT, T1/T2, IIa/IIb). In prose, write "and" or "or" instead ("smoker and drinker," not "smoker/drinker").
- **Literal text stays literal.** Do not change trial names, paper or file titles, quoted guideline language, URLs, IDs, or code to satisfy these rules.

## Headings and labels

- Reading headings (`h3`, `h4`) and plate titles use title case: "What Gets Treated," "Oral Cavity: MRI."
- Separate a plate title from its modality with a colon, not a hyphen.
- Table headers, card labels, buttons, and summaries use sentence case.
- Do not add "Actually" or "Really" to headings for emphasis.

## Voice

- Lead with the fact or the decision. Cut openers such as "It is important to note that," "When it comes to," and "In clinical practice."
- Prefer the concrete version. "VMAT changes the beam shape and intensity as the gantry turns" is better than "VMAT allows improved treatment delivery."
- Explain why something matters only when the reason is not obvious, and then give the actual reason.
- Do not end every paragraph with a summary sentence, and do not reuse one rhetorical pattern ("The key is...", "Here is the...") across a page.
- Avoid promotional words: groundbreaking, transformative, remarkable, pivotal, cornerstone, seamless, powerful tool. Do not swap in equally inflated synonyms.
- Do not use filler intensifiers ("actually," "really," "truly," "essentially," "basically") unless they carry meaning, as in "where the target really is today" (contrasting the plan with the daily setup).
- Avoid ward slang such as "pimp point." Write "a common question on rounds."
- Keep analogies rare and specific. Never use one just to sound friendly.

## Format

- **Paragraphs** for mechanisms and clinical reasoning.
- **Bullets** for criteria, indications, contraindications, steps, and lists of side effects.
- **Tables** for comparisons across tumors, stages, or regimens.
- Sentence fragments are fine in table cells, flashcard answers, labels, and checklists, and nowhere else.
- Flashcards: the front is one question. The back is the answer, short enough to say out loud. The optional "extra" adds the reason or the trial and does not repeat the back.

## Doses, units, and numbers

- Write doses as "60 Gy in 30 fractions" in prose. "60 Gy/30 fx" is acceptable in tables and plan summaries.
- Leave a space between a number and its unit: 2 cm, 7 mm, 50 Gy. Use symbols such as &le; and &gt; in staging cutoffs, tables, and flashcards.
- Use numerals for doses, sizes, ages, node counts, and fractions.

## Abbreviations

- Spell out an abbreviation the first time it appears in a reading unless it is standard for this audience (CT, MRI, PET, RT, DNA, HPV, PSA).
- Use the same abbreviation for the same idea across modules: RT (radiation therapy), SBRT, SRS, IMRT, VMAT, OAR, GTV/CTV/PTV, ENE, DOI, ADT, PMRT.
- "ChemoRT" and "chemoradiation" are both acceptable. Pick one within a paragraph.

## Trials and citations

- Use the trial's published name or acronym exactly (ACOSOG Z0011, CALGB 9343, RTOG 9802, PACIFIC). Trial citations are generated from `tools/sources.py`. Do not edit links by hand.
- A trial box states the question, the result, and what to remember. Report the effect as the trial reported it.
- Do not add a citation, statistic, or trial result that has not been checked against the source.

## Clinical uncertainty

- Keep the qualifiers: usually versus always, may versus will, selected patients versus all patients.
- Say whose recommendation it is when that matters: "NCCN recommends," "commonly used," "one randomized trial showed."
- Separate association from causation, and a single trial's finding from the standard of care.
- When practice varies, say so plainly ("practice varies; this is a tumor board decision") rather than giving one answer as though it were universal.
- Keep definitive, adjuvant, neoadjuvant, salvage, and palliative distinct. Do not use them interchangeably.

## Where to edit

Several JSON files are generated. Edit the source, then regenerate:

| Content | Source of truth |
|---|---|
| Before You Start readings | `tools/background_readings.py` (figures in `tools/bys_figures.py`) |
| Palliative & Benign readings | `tools/palliative_readings.py`, then `tools/hy_summaries.py` |
| High-Yield Summary boxes | `tools/hy_summaries.py` |
| Clinical cases | `tools/cases/<site>_cases.py` |
| Trial citations | `tools/sources.py` |
| Other readings, decks, curriculum, anatomy, imaging | the JSON file under `src/data/` |
| Quick checks, staging tools, interface text | `src/app.js`, `src/index.template.html` |
