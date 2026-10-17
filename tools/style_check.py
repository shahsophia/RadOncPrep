#!/usr/bin/env python3
"""
Checks user-facing text against docs/style-guide.md: no contractions, no em or
en dashes, and no spaced hyphens used as dashes.

Scans every string value in src/data/**/*.json (except IDs, paths, and URLs),
the string literals in src/app.js, and the text of src/index.template.html.
Python generators are covered through the JSON they write.

Usage:  python3 tools/style_check.py      (exit status 1 if anything is found)
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = "['’]"
CONTRACTION = re.compile(
    r"\b(?:\w+n" + A + r"t|(?:it|that|there|what|who|here|let|where|how|he|she|this)" + A + r"s"
    r"|\w+" + A + r"(?:re|ve|ll|d|m))\b", re.I)
DASH = re.compile("[—–]|&mdash;|&ndash;|&#821[12];")
SPACED_HYPHEN = re.compile(r"[A-Za-z>)\]%,] - [A-Za-z<(]")
SKIP_KEYS = {"id", "image", "src", "href", "url", "pmid", "doi", "pmcid", "module", "plate", "group"}
# Literal text that must stay as published (file titles, quotations).
ALLOW = ["BC - Hirnmetastasen MRT T1KM ax"]


def problems(text):
    for a in ALLOW:
        text = text.replace(a, "")
    text = re.sub(r"data:[\w/+.-]+;base64,[A-Za-z0-9+/=]+", "", text)
    out = [("contraction", m.group()) for m in CONTRACTION.finditer(text)]
    out += [("dash", m.group()) for m in DASH.finditer(text)]
    out += [("spaced hyphen", text[max(0, m.start() - 25):m.end() + 25]) for m in SPACED_HYPHEN.finditer(text)]
    return out


def walk(node, path, hits):
    if isinstance(node, dict):
        for k, v in node.items():
            if k not in SKIP_KEYS:
                walk(v, f"{path}.{k}", hits)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]", hits)
    elif isinstance(node, str):
        for kind, s in problems(node):
            hits.append((path, kind, s))


def js_strings(src):
    src = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group().count("\n"), src, flags=re.S)
    src = re.sub(r"(?m)^\s*//.*$", "", src)
    for m in re.finditer(r'"(?:[^"\\\n]|\\.)*"|`(?:[^`\\]|\\.)*`', src):
        s = m.group()
        s = re.sub(r"\$\{[^}]*\}", "0", s)
        yield src.count("\n", 0, m.start()) + 1, s


def main():
    hits = []
    for f in sorted(glob.glob(os.path.join(ROOT, "src/data/**/*.json"), recursive=True)):
        rel = os.path.relpath(f, ROOT)
        with open(f, encoding="utf8") as fh:
            walk(json.load(fh), rel, hits)
    with open(os.path.join(ROOT, "src/app.js"), encoding="utf8") as fh:
        for line, s in js_strings(fh.read()):
            for kind, x in problems(s):
                hits.append((f"src/app.js:{line}", kind, x))
    with open(os.path.join(ROOT, "src/index.template.html"), encoding="utf8") as fh:
        html = re.sub(r"<(script|style)\b.*?</\1>", "", fh.read(), flags=re.S | re.I)
        html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
        for kind, x in problems(html):
            hits.append(("src/index.template.html", kind, x))
    for path, kind, s in hits:
        print(f"{path}: {kind}: {s!r}")
    print(f"{len(hits)} style problem(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
