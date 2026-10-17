#!/usr/bin/env python3
"""Append or replace findings in docs/audit/findings.json from a JSON list on stdin.
Fills in date and reviewer. Usage: python3 tools/audit/add_findings.py < new.json"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "docs", "audit", "findings.json")
cur = json.load(open(PATH, encoding="utf8")) if os.path.exists(PATH) else []
idx = {f["finding_id"]: i for i, f in enumerate(cur)}
for f in json.load(sys.stdin):
    f.setdefault("date", "2026-10-16")
    f.setdefault("reviewer", "Claude (AI-assisted audit); not a substitute for radiation oncologist review")
    assert f["status"] in ("Pending", "Verified", "Revise", "Expert review", "Unable to verify"), f["finding_id"]
    if f["finding_id"] in idx:
        cur[idx[f["finding_id"]]] = {**cur[idx[f["finding_id"]]], **f}
    else:
        idx[f["finding_id"]] = len(cur)
        cur.append(f)
json.dump(cur, open(PATH, "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(cur), "findings")
