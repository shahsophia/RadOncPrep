#!/usr/bin/env python3
"""Check every 'PMC<id>' cited in a caption against Europe PMC: does the article
exist, and do the first author, journal and year in the caption match?
Writes docs/audit/caption_reference_check.csv."""
import csv, json, os, re, time, urllib.parse, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
hits = {}
for dp, _, fs in os.walk(os.path.join(ROOT, "src", "data")):
    for f in fs:
        if not f.endswith(".json"):
            continue
        rel = os.path.relpath(os.path.join(dp, f), ROOT)
        txt = open(os.path.join(dp, f), encoding="utf8").read()
        for m in re.finditer(r"PMC(\d{5,9})", txt):
            s = txt[max(0, m.start() - 160): m.end() + 5]
            s = re.sub(r"\\n|<[^>]+>", " ", s).split('"')[-1] if '"' in s else s
            hits.setdefault(m.group(1), []).append((rel, s.strip()))
out = []
for pmcid, uses in sorted(hits.items()):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": f"PMCID:PMC{pmcid}", "resultType": "core", "format": "json"})
    try:
        r = json.load(urllib.request.urlopen(url, timeout=30))["resultList"]["result"]
    except Exception as e:
        r = []
    if not r:
        out.append({"pmcid": f"PMC{pmcid}", "found": "NO", "files": "; ".join(sorted({u[0] for u in uses})), "caption_excerpt": uses[0][1][-160:]})
        continue
    a = r[0]
    first = (a.get("authorList", {}).get("author") or [{}])[0]
    last = first.get("lastName", "")
    jour = a.get("journalInfo", {}).get("journal", {}).get("isoabbreviation") or a.get("journalInfo", {}).get("journal", {}).get("title", "")
    year = a.get("pubYear", "")
    cap = " ".join(u[1] for u in uses)
    issues = []
    if last and last.lower() not in cap.lower():
        issues.append(f"first author '{last}' not in caption")
    if year and year not in cap:
        issues.append(f"year {year} not in caption")
    lic = a.get("license", "")
    out.append({"pmcid": f"PMC{pmcid}", "found": "yes", "first_author": last, "journal": jour, "year": year,
                "title": a.get("title", "")[:150], "license": lic, "issues": "; ".join(issues),
                "files": "; ".join(sorted({u[0] for u in uses})), "caption_excerpt": uses[0][1][-160:]})
    time.sleep(0.15)
cols = ["pmcid", "found", "first_author", "journal", "year", "license", "issues", "title", "files", "caption_excerpt"]
with open(os.path.join(ROOT, "docs", "audit", "caption_reference_check.csv"), "w", newline="", encoding="utf8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(out)
print(len(out), "PMC ids;", sum(o["found"] == "NO" for o in out), "not found;", sum(bool(o.get("issues")) for o in out), "with mismatches")
for o in out:
    if o["found"] == "NO" or o.get("issues"):
        print(o["pmcid"], o["found"], o.get("first_author", ""), o.get("year", ""), "|", o.get("issues", ""), "|", o["caption_excerpt"][-120:])
