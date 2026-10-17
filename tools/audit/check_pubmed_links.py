#!/usr/bin/env python3
"""Resolve every PubMed link in src/data against Europe PMC and record the
linked paper's title next to the link text, so mismatches can be reviewed.
Writes docs/audit/pubmed_link_check.csv."""
import csv, json, os, re, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
links = {}
for dp, _, fs in os.walk(os.path.join(ROOT, "src", "data")):
    for f in fs:
        if f.endswith(".json"):
            rel = os.path.relpath(os.path.join(dp, f), ROOT)
            txt = open(os.path.join(dp, f), encoding="utf8").read().replace('\\"', '"')
            for m in re.finditer(r"<a href=['\"]https://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/?['\"][^>]*>(.*?)</a>", txt):
                ctx = re.sub(r"<[^>]+>", "", txt[max(0, m.start() - 200): m.end() + 120])
                links.setdefault(m.group(1), []).append((rel, re.sub(r"<[^>]+>", "", m.group(2)), ctx.replace("\\n", " ")))
rows = []
for pmid, uses in sorted(links.items(), key=lambda x: int(x[0])):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode({"query": f"EXT_ID:{pmid} AND SRC:MED", "resultType": "core", "format": "json"})
    try:
        r = json.load(urllib.request.urlopen(url, timeout=30))["resultList"]["result"]
    except Exception:
        r = []
    a = r[0] if r else {}
    first = (a.get("authorList", {}).get("author") or [{}])[0].get("lastName", "")
    rows.append({"pmid": pmid, "resolves": "yes" if a else "NO", "first_author": first, "year": a.get("pubYear", ""),
                 "journal": a.get("journalInfo", {}).get("journal", {}).get("isoabbreviation", ""), "title": a.get("title", ""),
                 "link_text": " || ".join(sorted({u[1] for u in uses})), "files": "; ".join(sorted({u[0] for u in uses})),
                 "context": uses[0][2][-330:]})
    time.sleep(0.12)
with open(os.path.join(ROOT, "docs", "audit", "pubmed_link_check.csv"), "w", newline="", encoding="utf8") as fh:
    w = csv.DictWriter(fh, fieldnames=["pmid", "resolves", "first_author", "year", "journal", "title", "link_text", "files", "context", "review"]); w.writeheader(); w.writerows(rows)
for r in rows:
    print(f"{r['pmid']:>9} {r['resolves']:3} | {r['link_text'][:40]:40} | {r['first_author'][:12]:12} {r['year']} | {r['title'][:95]}")
