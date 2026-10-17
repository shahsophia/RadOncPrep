#!/usr/bin/env python3
"""Look up the primary publication for every trial named in curriculum.json
(queries in trial_queries.py) and write docs/audit/trial_references.csv.
A row is marked 'match' only after a human checks the returned title against
the trial; this script just fetches and records."""
import csv, json, os, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trial_queries import Q
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cur = json.load(open(os.path.join(ROOT, "src", "data", "curriculum.json"), encoding="utf8"))["sites"]
named = [(s, t) for s, m in cur.items() for t in m.get("trials", [])]
rows = []
for site, t in named:
    q = Q.get(t)
    if not q:
        rows.append({"site": site, "trial": t, "status": "no query"}); continue
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({"query": q[0], "resultType": "core", "format": "json", "pageSize": 1})
    try:
        res = json.load(urllib.request.urlopen(url, timeout=30))["resultList"]["result"]
    except Exception as e:
        res = []
    if not res:
        rows.append({"site": site, "trial": t, "expected": q[1], "status": "not found"}); continue
    r = res[0]
    first = (r.get("authorList", {}).get("author") or [{}])[0].get("lastName", "")
    rows.append({"site": site, "trial": t, "expected": q[1], "status": "found", "pmid": r.get("pmid", ""), "doi": r.get("doi", ""),
                 "year": r.get("pubYear", ""), "first_author": first,
                 "journal": r.get("journalInfo", {}).get("journal", {}).get("isoabbreviation", ""), "title": r.get("title", "")})
    time.sleep(0.12)
out = os.path.join(ROOT, "docs", "audit", "trial_references.csv")
cols = ["site", "trial", "expected", "status", "first_author", "year", "journal", "pmid", "doi", "title", "check"]
with open(out, "w", newline="", encoding="utf8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
for r in rows:
    print(f"{r['trial'][:28]:28} | {r.get('expected','')[:26]:26} | {r['status']:9} | {r.get('first_author','')[:14]:14} {r.get('year','')} {r.get('pmid','')} | {r.get('title','')[:90]}")
