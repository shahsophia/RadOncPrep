#!/usr/bin/env python3
"""Build docs/audit/AUDIT_REPORT.md and docs/audit/high_risk_review_queue.csv
from docs/audit/findings.json and docs/audit/claim_ledger.csv.
Run tools/audit/extract_claims.py first.  Usage: python3 tools/audit/make_report.py"""
import csv, json, os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "docs", "audit")
F = json.load(open(os.path.join(A, "findings.json"), encoding="utf8"))
L = list(csv.DictReader(open(os.path.join(A, "claim_ledger.csv"), encoding="utf8")))
S = json.load(open(os.path.join(A, "ledger_summary.json"), encoding="utf8"))
by_id = {c["claim_id"]: c for c in L}
fclaims = {}
for c in L:
    for fid in filter(None, (c.get("finding_ids") or "").split("; ")):
        fclaims.setdefault(fid, []).append(c)

# ---- prioritized high-risk review queue (claims, not findings)
CAT_PRI = ["emergency", "oar-constraint", "dose-fractionation", "brachytherapy", "reirradiation", "staging",
           "indication", "serious-toxicity"]
STATUS_PRI = {"Revise": 0, "Expert review": 1, "Unable to verify": 2, "Pending": 3, "Verified": 4}
def pri(c):
    cats = c["categories"].split("; ")
    best = min([CAT_PRI.index(x) for x in cats if x in CAT_PRI] or [len(CAT_PRI)])
    kind = 0 if c["unit_kind"] in ("app.js", "app.js-logic", "case-answer", "flashcard", "table-row") else 1
    return (STATUS_PRI.get(c["status"], 3), best, kind, c["site"])
high = sorted([c for c in L if c["risk"] == "HIGH"], key=pri)
with open(os.path.join(A, "high_risk_review_queue.csv"), "w", newline="", encoding="utf8") as fh:
    w = csv.writer(fh)
    w.writerow(["priority", "claim_id", "status", "first_pass", "site", "edit_in", "section", "categories", "statement", "finding_ids"])
    for i, c in enumerate(high, 1):
        w.writerow([i, c["claim_id"], c["status"], c["first_pass"], c["site"], c["edit_in"], c["section"], c["categories"], c["statement"], c.get("finding_ids", "")])

def src_lines(f):
    out = []
    for s in f.get("sources", []):
        bits = [s.get("title", "")]
        if s.get("year"): bits.append(f"({s['year']})")
        if s.get("pmid"): bits.append(f"PMID {s['pmid']}")
        if s.get("doi"): bits.append(f"doi:{s['doi']}")
        line = " ".join(b for b in bits if b)
        if s.get("url"): line = f"[{line}]({s['url']})"
        out.append(line)
    return out

def locs(f):
    cs = fclaims.get(f["finding_id"], [])
    seen, out = set(), []
    for c in cs:
        k = (c["edit_in"], c["section"])
        if k in seen: continue
        seen.add(k)
        out.append(f"`{c['edit_in']}` ({c['section'][:90]}) [{c['claim_id']}]")
    if not out and f.get("retired_file"):
        out.append(f"`{f['retired_file']}`")
    return out

def block(f, with_correction=True, original=False):
    lines = [f"**{f['finding_id']}** ({f['risk']} risk, {f['type']}, status: {f['status']})", "", f["finding"], ""]
    if locs(f): lines += ["Location: " + "; ".join(locs(f)), ""]
    if original and f.get("original_match"):
        lines += ["Original text: " + " / ".join(f'"{m["text"]}"' for m in f["original_match"]), ""]
    if with_correction and f.get("correction"): lines += ["Correction: " + f["correction"], ""]
    if f.get("implemented"): lines += ["Implemented: " + f["implemented"], ""]
    s = src_lines(f)
    if s: lines += ["Sources:"] + [f"- {x}" for x in s] + [""]
    return "\n".join(lines)

def sel(pred): return [f for f in F if pred(f)]
errors = sel(lambda f: f["type"] in ("error", "misleading"))
outdated = sel(lambda f: f["type"] in ("outdated", "weak"))
refs = sel(lambda f: f["type"] == "reference")
contra = sel(lambda f: f["type"] == "contradiction" or "contradict" in f["finding"].lower())
proposed = sel(lambda f: f.get("correction"))
implemented = sel(lambda f: f.get("implemented"))
expert = sel(lambda f: f["status"] in ("Expert review", "Unable to verify") or (f["status"] == "Revise" and not f.get("implemented")))
verified_only = sel(lambda f: f["type"] == "verified")

hs = S["high_by_status"]
md = []
md.append("# Clinical Accuracy Audit: RadOnc Sub-I Companion\n")
md.append("Audit dates: 2026-10-16 to 2026-10-17. Reviewer: Claude (AI-assisted). **This audit is not a substitute for review by a radiation oncologist, and the site is not fully verified.** "
          f"{hs.get('Expert review', 0)} high-risk claims are awaiting expert review, and "
          f"{hs.get('Pending', 0)} high-risk claims were read without a source being attached to each one.\n")
md.append("## How to read this\n")
md.append("- Every clinical statement in the source files is a row in `claim_ledger.csv` with a stable ID, file, JSON path, section, risk tier, and status.\n"
          "- Review results live in `findings.json`. Each finding names the claims it covers, the sources checked (with PMID/DOI where one exists), the proposed correction, and whether it was implemented. `tools/audit/extract_claims.py` merges findings into the ledger.\n"
          "- Statuses: **Verified** = a cited source was retrieved and supports the exact statement; **Revise** = the evidence supports a change; **Expert review** = sources conflict or could not be accessed; **Unable to verify** = no accessible source; **Pending** = not yet checked against a source.\n"
          "- `first_pass` records whether the claim was read line by line in this audit. \"Read, no discrepancy found\" is **not** verification: no source was attached to that claim.\n"
          "- Risk tiers come from keyword rules (`extract_claims.py`). They are a triage tool, so expect some miscategorized rows.\n"
          "- Regenerate everything: `python3 tools/audit/extract_claims.py && python3 tools/audit/make_report.py`.\n")

md.append("## Summary\n")
md.append(f"| | Count |\n|---|---|\n| Claims inventoried | {S['total_claims']:,} |\n| HIGH / MODERATE / LOWER | {S['by_risk']['HIGH']:,} / {S['by_risk']['MODERATE']:,} / {S['by_risk']['LOWER']:,} |\n"
          f"| HIGH-risk claims read in this audit | {S['high_first_pass'].get('Read 2026-10-16/17', 0):,} of {S['by_risk']['HIGH']:,} |\n"
          f"| All claims read in this audit | {S['all_first_pass'].get('Read 2026-10-16/17', 0):,} of {S['total_claims']:,} |\n"
          f"| Findings | {len(F)} |\n| Verified errors or misleading statements | {len(errors)} |\n| Corrections implemented | {len(implemented)} |\n"
          f"| Items needing a radiation oncologist | {len(expert)} |\n| Trial citations checked (Europe PMC) | 155 named trials + 27 inline PubMed links + 101 caption PMC IDs |\n")
md.append("Claim status after this audit: " + ", ".join(f"{k} {v:,}" for k, v in S["by_status"].items()) + ". "
          "HIGH-risk: " + ", ".join(f"{k} {v:,}" for k, v in hs.items()) + ".\n")
md.append("**Concurrent edits.** Two other Claude sessions edited this folder during the audit (Before You Start revisions, which added `src/data/sources.json` and retired `src/data/docs/overview.json`; and the Palliative & Benign rewrite). The ledger reflects the working tree on 2026-10-17, including their uncommitted work. Palliative claims changed after the first read were read again.\n")

md.append("## 1. Claim ledger\n")
md.append("`docs/audit/claim_ledger.csv`: " + f"{S['total_claims']:,} rows. Columns: claim_id, risk, status, first_pass, site, source_file, edit_in (the file a correction must be made in, e.g. a case generator), json_path, section, unit_kind, statement, categories, disease_context, treatment_context, supporting_source, verification_findings, proposed_correction, implemented, related_claims, finding_ids, date_reviewed, reviewer.\n")
md.append("Claims by site: " + ", ".join(f"{k} {v:,}" for k, v in S["by_site"].items()) + ".\n")

md.append("## 2. Prioritized high-risk claims requiring review\n")
md.append(f"`docs/audit/high_risk_review_queue.csv` ranks all {len(high):,} HIGH claims: open findings first, then by category (emergency, organ-at-risk constraint, dose/fractionation, brachytherapy, re-irradiation, staging, indication, serious toxicity), with interactive tools, case answers, flashcards, and tables ahead of prose. Suggested order for a physician reviewer:\n")
md.append("1. The open items in section 9 (expert judgment).\n2. Organ-at-risk constraint tables (thoracic, CNS, GYN, GI, prostate, Before You Start planning reference).\n3. Dose/fractionation tables and case 'Dose' steps for every site.\n4. Staging tables and the interactive builders (tests in section 10 cover the builders' logic only, not the prose around them).\n5. Emergency pathways (cord compression, SVC, bleeding) in Palliative & Benign and CNS.\n")

md.append("## 3. Verified errors and misleading statements\n")
for f in errors: md.append(block(f, original=True))
md.append("## 4. Outdated or weakly supported claims\n")
for f in outdated: md.append(block(f))
md.append("## 5. References: missing, broken, or mismatched\n")
md.append("- **Trial citations.** At the start, `curriculum.json` named 155 trials with no PMID/DOI. During the audit the Before You Start session added `src/data/sources.json`. `docs/audit/trial_references.csv` gives an independent primary-report lookup for all 155 (Europe PMC: PMID, DOI, year, journal, title).\n"
          "- **Inline PubMed links.** `docs/audit/pubmed_link_check.csv`: all 27 linked PMIDs resolve, and each title matches its link text.\n"
          "- **Figure captions.** `docs/audit/caption_reference_check.csv`: all 101 cited PMC IDs exist; attribution issues are listed below.\n"
          "- **Guideline versions.** NCCN guideline versions quoted in the GYN reading (e.g., v2.2026, v3.2026) could not be checked because NCCN requires a login. Status: Unable to verify.\n")
for f in refs: md.append(block(f))
md.append("## 6. Contradictions between readings, flashcards, cases, and tools\n")
for f in contra: md.append(block(f, with_correction=True))
md.append("## 7. Proposed corrections with exact source locations\n")
md.append("| Finding | Status | Edit in | Proposed correction |\n|---|---|---|---|\n")
for f in proposed:
    where = "; ".join(sorted({c["edit_in"] for c in fclaims.get(f["finding_id"], [])})) or f.get("retired_file", "see finding")
    md.append(f"| {f['finding_id']} | {f['status']}{' (implemented)' if f.get('implemented') else ''} | {where} | {f['correction'].replace('|', '/')} |\n")
md.append("\n## 8. Corrections implemented\n")
md.append("Every change was a targeted string replacement. Case JSON was regenerated from `tools/cases/<site>_cases.py`, and each regenerated diff touched only the intended lines. `dist/index.html` has **not** been rebuilt and nothing has been committed, so as not to collide with the two other sessions.\n\n")
md.append("| Finding | What changed | Where |\n|---|---|---|\n")
for f in implemented:
    md.append(f"| {f['finding_id']} | {f.get('correction','')[:220].replace('|','/')} | {f['implemented'].split(': ',1)[-1].replace('|','/')} |\n")
md.append("\n## 9. Claims still requiring a radiation oncologist's judgment\n")
for f in expert: md.append(block(f))
md.append("Also for physician review (not separate findings):\n"
          "- The ~3,300 HIGH claims marked \"Read, no discrepancy found\" have no source attached per claim. Spot-check them, starting with the constraint and dose tables.\n"
          "- Prepared OpenEvidence questions for the items above are in `docs/audit/openevidence_questions.md`. **OpenEvidence was not accessed in this audit.**\n")
md.append("## 10. Validation report\n")
md.append("**Tests run**\n"
          "- `tools/audit/builder_tests.js`: 249 assertions on the interactive builders, run in a browser against a scratch build that included all changes: lung stage group for every T × N × M combination (AJCC 9th edition, IASLC 2024), station-to-N drill, Gleason to Grade Group, NCCN prostate risk group, AJCC 8 prostate stage, Sedlis/Peters, WHO 2021 glioma. **249/249 pass.** Before the fix, the lung grid returned IIIB for T3 N2a and IIIC for T3-4 N2b.\n"
          "- Content check in the same build: all 9 corrected strings render (thoracic table and Case 3, GI Case 4, prostate Case 5, breast Case 6, SVC hotspot, SWOG flashcard, survivor-screening quiz, Sedlis text). No console errors.\n"
          "- The builder logic for SINS, Mirels, and the 2008 GPA was checked by hand against the source scoring tables (Fisher 2010, Mirels 1989, Sperduto 2008); no discrepancy.\n"
          "- `extract_claims.py` reports 0 finding targets that fail to match a claim.\n"
          "- Citation checks: 155/155 trial PMIDs resolve (2 in sources.json point to letters, F-REF-03); 27/27 inline links resolve and match; 101/101 caption PMC IDs exist.\n\n"
          "**Limitations**\n"
          "- No NCCN guideline text was accessed (login required). Statements summarizing NCCN were checked against primary trials and consensus papers where possible, otherwise left Pending or Expert review.\n"
          "- Most verification used abstracts (Europe PMC), not full texts. Claims depending on numbers found only in tables or figures (e.g., the QUANTEC summary table) are marked accordingly.\n"
          "- MODERATE and LOWER claims were not systematically read (8,136 unread), except Palliative & Benign MODERATE claims and claims surfaced during cross-checks.\n"
          "- Risk tiering and sentence splitting are automatic. A claim split across two ledger rows, or a 'Try it' question separated from its answer, can lose context (one apparent contradiction in Head & Neck was a splitting artifact and was not recorded).\n"
          "- Content changed by other sessions after this audit, or after 2026-10-17, is not covered; rerun the extractor and compare claim IDs.\n"
          "- Reviewer was an AI model. Absence of a finding is not proof of accuracy.\n")
md.append("\n## Files\n")
for fn, d in [("claim_ledger.csv", "full claim inventory"), ("findings.json", "all findings with sources and corrections"),
              ("high_risk_review_queue.csv", "HIGH claims in review order"), ("trial_references.csv", "primary publication for each named trial"),
              ("pubmed_link_check.csv", "inline PubMed link check"), ("caption_reference_check.csv", "figure caption PMC check"),
              ("openevidence_questions.md", "prepared questions (not submitted)"), ("first_pass_reviewed_ids.txt", "claim IDs read in this audit"),
              ("ledger_summary.json", "counts")]:
    md.append(f"- `docs/audit/{fn}`: {d}\n")
md.append("\nTools: `tools/audit/extract_claims.py`, `add_findings.py`, `epmc.py` (Europe PMC lookup), `trial_queries.py` + `trial_refs.py`, `check_pubmed_links.py`, `check_pmc_captions.py`, `builder_tests.js`, `make_report.py`.\n")

open(os.path.join(A, "AUDIT_REPORT.md"), "w", encoding="utf8").write("\n".join(md))
print("wrote AUDIT_REPORT.md;", len(errors), "errors,", len(implemented), "implemented,", len(expert), "expert-review items,", len(high), "high-risk claims in queue")
