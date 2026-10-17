#!/usr/bin/env python3
"""Look up citations in Europe PMC so every source in findings.json has a real
PMID/DOI. Usage: python3 tools/audit/epmc.py "query" [n] [--abstract]"""
import json, sys, urllib.parse, urllib.request

def search(q, n=3):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": q, "resultType": "core", "format": "json", "pageSize": n})
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)["resultList"]["result"]

if __name__ == "__main__":
    q = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 3
    for r in search(q, n):
        print(f"PMID {r.get('pmid')} | doi {r.get('doi')} | {r.get('pubYear')} | {r.get('journalInfo',{}).get('journal',{}).get('isoabbreviation')} | {r.get('title')}")
        if "--abstract" in sys.argv:
            print("   ", (r.get("abstractText") or "")[:2500].replace("\n", " "))
