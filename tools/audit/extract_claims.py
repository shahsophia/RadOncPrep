#!/usr/bin/env python3
"""
Clinical claim inventory for the clinical accuracy audit.

Walks every source-of-truth file (reading docs, Before You Start readings,
flashcards, cases, curriculum metadata, anatomy and imaging plates, and the
quiz/drill/builder content inside src/app.js), splits the text into
statement-level claims, tags each with a category and a risk tier, and writes
docs/audit/claim_ledger.csv.

Review results live in docs/audit/findings.json. Each finding names the claims
it covers (by claim ID, or by file plus a text fragment that must appear in the
claim), and the script merges them into the ledger. Every claim without a
finding stays "Pending". Nothing is marked Verified by this script on its own.

Usage:  python3 tools/audit/extract_claims.py
"""
import csv, hashlib, html, json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "src", "data")
OUT_DIR = os.path.join(ROOT, "docs", "audit")
SITES = ["breast", "thoracic", "cns", "gi", "prostate", "gyn", "headneck", "palliative", "overview"]

# Which file a correction has to be made in, when the JSON is generated.
def generator_for(rel, path):
    if rel == "src/data/background.json":
        return "tools/background_readings.py"
    m = re.match(r"src/data/cases/(\w+)\.json", rel)
    if m:
        return f"tools/cases/{m.group(1)}_cases.py"
    if rel.startswith("src/data/docs/") and "High-Yield Summary" in path:
        return "tools/hy_summaries.py"
    if rel == "src/data/docs/palliative.json":
        return "tools/palliative_readings.py"
    return rel


# ---------------------------------------------------------------- HTML -> units
BLOCK = {"p", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "figcaption", "summary", "dt", "dd", "caption", "blockquote"}
HEAD = {"h3", "h4", "h5", "summary"}


class Units(HTMLParser):
    """Collect text units (paragraphs, list items, table rows, captions), each
    with the nearest heading above it as its section."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.units, self.buf, self.section, self.cell = [], [], "", []
        self.stack, self.row = [], None
        self.tab = ""

    def flush(self, kind):
        txt = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if txt:
            self.units.append((self.section_label(), kind, txt))

    def section_label(self):
        return " > ".join(x for x in [self.tab, self.section] if x)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and a.get("data-title"):
            self.tab = a["data-title"]
        if tag in ("div",) and "plate-group-inline" in (a.get("class") or ""):
            self.units.append((self.section_label(), "widget", f"[embedded plate group {a.get('data-plate-group')}]"))
        if tag == "div":
            cls = a.get("class") or ""
            for w in ("quiz-carousel", "stage-builder", "nstage-drill", "choice-drill", "gleason-builder", "risk-builder",
                      "sedlis-builder", "glioma-builder", "gpa-builder", "rectal-builder", "pancreas-builder", "sins-builder", "mirels-builder"):
                if w in cls.split():
                    key = a.get("data-quiz-set") or a.get("data-drill-set") or ""
                    self.units.append((self.section_label(), "widget", f"[embedded widget {w} {key}]".strip()))
                    break
        if tag == "tr":
            self.flush("text")
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
            self.buf_before_cell = self.buf
            self.buf = []
        elif tag in BLOCK:
            self.flush("text")
        if tag == "br":
            self.buf.append(" ")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.buf)).strip())
            self.buf = []
        elif tag == "tr" and self.row is not None:
            cells = [c for c in self.row if c]
            if cells:
                self.units.append((self.section_label(), "table-row", " | ".join(cells)))
            self.row = None
        elif tag in HEAD:
            txt = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            self.buf = []
            if txt:
                if tag == "summary":
                    self.units.append((self.section_label(), "heading", txt))
                else:
                    self.section = txt
        elif tag in BLOCK:
            self.flush("text")
        elif tag == "div":
            self.flush("text")
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, data):
        self.buf.append(data)

    def close(self):
        super().close()
        self.flush("text")


def html_units(s):
    p = Units()
    p.feed(s)
    p.close()
    return p.units


ABBREV = r"(?:e\.g|i\.e|vs|approx|Dr|St|Fig|al|No|cf|ca|mo|yr|min|max|Ph|U\.S)"


def sentences(txt):
    """Split a paragraph into sentences without breaking on '2.5 cm', 'e.g.' or 'vs.'."""
    if len(txt) < 160:
        return [txt]
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9<(\[])", txt)
    out, cur = [], ""
    for part in parts:
        cur = f"{cur} {part}".strip() if cur else part
        if re.search(rf"\b{ABBREV}\.$", cur):
            continue
        out.append(cur)
        cur = ""
    if cur:
        out.append(cur)
    return out


def plain(s):
    if "<" in s and ">" in s:
        return None
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


# ---------------------------------------------------------------- classifiers
P = lambda pat: re.compile(pat, re.I)
CATS = [
    ("emergency", P(r"cord compression|\bMSCC\b|\bSVC\b|superior vena cava|emergen|airway obstruct|hemoptysis|hemorrhag|bleeding|stridor|dexamethasone|cauda equina|raised intracranial|herniat")),
    ("reirradiation", P(r"re-?irradiat|retreat|prior (?:radiation|RT)|previously irradiated|second course|cumulative dose")),
    ("brachytherapy", P(r"brachy|\bHDR\b|\bLDR\b|tandem|ovoid|cylinder|\bseeds?\b|implant|\bpoint A\b|HR-CTV|\bD90\b|\bD2cc\b|I-125|Ir-192|Pd-103|Cs-131")),
    ("oar-constraint", P(r"\bV\d{1,3}\b|\bD\s?max\b|\bDmean\b|mean (?:lung |heart |parotid |liver )?dose|constraint|toleran|\bQUANTEC\b|\bD0\.0?3\s?cc|\bD\d+cc\b|\bmax(?:imum)? (?:point )?dose")),
    ("dose-fractionation", P(r"\b\d+(?:\.\d+)?\s?(?:-\s?\d+(?:\.\d+)?\s?)?Gy\b|\bfractions?\b|\bfx\b|hypofraction|\bBED\b|\bEQD2\b|\bSBRT\b|\bSRS\b|\bSABR\b|\bcGy\b|twice daily|\bBID\b")),
    ("staging", P(r"\b[cpy]?[Tt](?:is|[0-4][a-d]?|mi)\b|\b[cpy]?N[0-3][a-c]?\b|\bM[01][a-c]?\d?\b|\bstage\s+(?:0|I{1,3}V?|IV)[A-C]?\d?\b|\bAJCC\b|\bFIGO\b|\bGleason\b|grade group|\brisk group\b|\bWHO grade\b|\bstation\s?\d|\bBilsky\b|limited[- ]stage|extensive[- ]stage")),
    ("indication", P(r"\bindicat|contraindicat|\brecommend|\bstandard\b|candidate|\bomit|\bomission|\bshould\b|\bneeds?\b|\brequires?\b|\bpreferred\b|\badjuvant\b|\bneoadjuvant\b|\bdefinitive\b|\bPMRT\b|\bconcurrent\b|\bTNT\b|\bavoid\b|\breserved for\b|\bfirst-line\b|\bwatch(?:-| and )wait|\bactive surveillance\b|\bobservation\b")),
    ("serious-toxicity", P(r"necrosis|myelopathy|fistula|perforat|stricture|plexopathy|blindness|optic neuropathy|second(?:ary)? (?:cancer|malignanc)|fatal|death|grade [45]|cardiac (?:event|death)|osteoradionecrosis|pneumonitis|fibrosis|infertil|hypopituitar|cognitive decline|leukoencephalopathy|carotid blowout|radiation[- ]induced")),
    ("trial", P(r"\b(?:RTOG|NRG|NSABP|EORTC|CALGB|ACOSOG|GOG|JCOG|SWOG|ECOG|NCIC|CCTG|TROG|ANZ|START|FAST|PRIME|PACIFIC|CROSS|RAPIDO|PROSPECT|OPRA|STAMPEDE|PORTEC|LACC|OUTBACK|INTERLACE|EMBRACE|SABR-COMET|CONVERT|ADRIATIC|LAURA|ADAURA|KEYNOTE|CheckMate|CATNON|INDIGO|QUARTZ|SC\.\d+|Z00\d+|Z1071|AMAROS|MA\.\d+|IMPORT|HYPRO|CHHiP|PROFIT|PACE|HYPO-RT|ProtecT|RADICALS|RAVES|GETUG|SPPORT|CORE|SINDAS|ESTRO|Stupp|Turrisi|LungART|HILUS|PRODIGE|LAP07|Dutch|Swedish|German|Nordic|ARCON|De-ESCALaTE|NRG-HN|HN\d|IMRT trial|trial|randomi[sz]ed|phase (?:I{1,3}|[123])|meta-analys)\w*")),
    ("prognosis", P(r"survival|prognos|\bcure rate|\b\d{1,3}% (?:at|5-year|10-year)|\b(?:5|10)-year\b|local control|recurrence rate|response rate|median")),
    ("follow-up", P(r"follow-?up|surveillance|\bevery \d+ (?:months|weeks)|after treatment.*(?:scan|PET|MRI)|post-?treatment (?:PET|MRI|CT)")),
    ("workup-imaging", P(r"\bMRI\b|\bPET\b|\bCT\b|biopsy|workup|work-up|\bEBUS\b|mammogra|ultrasound|endoscop|laryngoscop|colonoscop|cystoscop|\bEUS\b|\bPSA\b|\bCEA\b|marker|\bIHC\b|\bp16\b|PD-L1|EGFR|ALK|MGMT|IDH|HPV|EBV")),
    ("technique", P(r"\bIMRT\b|\bVMAT\b|\b3D-?CRT\b|proton|\bIGRT\b|\bCBCT\b|\bITV\b|\bPTV\b|\bCTV\b|\bGTV\b|4D-?CT|breath hold|\bDIBH\b|gating|simulation|immobili|mask|bolus|electron|tangent|field|contour|margin|isocenter|boost|SIB")),
    ("toxicity", P(r"toxicit|side effect|mucositis|dermatitis|xerostomia|dysphagia|esophagitis|diarrhea|proctitis|cystitis|fatigue|nausea|erythema|desquamation|alopecia|lymphedema|edema|dysgeusia|trismus|hearing|cataract|hypothyroid|erectile|incontinen")),
    ("epidemiology", P(r"incidence|most common|risk factor|prevalen|\bage\b|smok|alcohol|\bBRCA|Lynch|Li-Fraumeni|carcinogen|exposure|ancestry|\bper year\b|deaths?\b")),
    ("anatomy", P(r"artery|vein|nerve|lobe|level [IV]+[ab]?|lymph|drain|fascia|muscle|vertebra|\bspace\b|ligament|sulcus|foramen|gland|duct|bronch|trachea|carina|mediastin")),
    ("history", P(r"\bhistor|\bin (?:18|19|20)\d\d\b|discover|first used|Roentgen|Curie|\bera\b")),
]
SERIOUS_TOX_WITH_DOSE = P(r"\bGy\b|\bdose\b|\bconstraint|\bV\d|\bD\s?max")

HIGH = {"emergency", "dose-fractionation", "indication", "oar-constraint", "reirradiation", "brachytherapy", "serious-toxicity"}
MODERATE = {"trial", "prognosis", "follow-up", "workup-imaging", "technique", "toxicity"}
# staging is HIGH only when it changes treatment: stage groups, T/N/M definitions,
# risk groups and builders. Bare mentions of "stage" in framing prose are MODERATE.
STAGING_HIGH = P(r"\b[cpy]?T(?:is|[0-4][a-d]?)\b.*(?:=|is|means|count|upstag|=)|\bN[0-3][a-c]?\b|\bM1[a-c]?\b|\bstage (?:I{1,3}V?|IV)[A-C]?\b|\bgrade group|\brisk group|\bFIGO (?:stage )?I|Sedlis|Peters|Gleason \d|station \d|Bilsky|SINS|Mirels|GPA")


def classify(text):
    cats = [name for name, rx in CATS if rx.search(text)]
    if not cats:
        cats = ["framing"]
    high = [c for c in cats if c in HIGH]
    if "staging" in cats and STAGING_HIGH.search(text):
        high.append("staging")
    if high:
        risk = "HIGH"
    elif any(c in MODERATE or c == "staging" for c in cats):
        risk = "MODERATE"
    else:
        risk = "LOWER"
    return cats, risk


DISEASE_HINTS = [
    ("DCIS", P(r"\bDCIS\b")), ("breast", P(r"breast|mastectomy|lumpectomy|axill|PMRT")),
    ("NSCLC", P(r"NSCLC|non-small|adenocarcinoma of the lung|lung adeno")), ("SCLC", P(r"small cell|SCLC|\bLS-SCLC|\bES-SCLC")),
    ("lung", P(r"\blung\b|thorac|pulmonary")), ("mesothelioma", P(r"mesotheli")), ("thymoma", P(r"thym")),
    ("esophagus", P(r"esophag")), ("gastric", P(r"gastric|stomach")), ("pancreas", P(r"pancrea")),
    ("rectum", P(r"rect(?:um|al)")), ("anus", P(r"\banal\b|\banus\b")), ("liver/HCC", P(r"\bHCC\b|hepatocell|\bliver\b")),
    ("cholangio/biliary", P(r"cholangio|biliary|gallbladder")),
    ("prostate", P(r"prostat|\bPSA\b|Gleason")), ("bladder", P(r"bladder")), ("testis/seminoma", P(r"seminoma|testic")),
    ("cervix", P(r"cervi")), ("endometrium", P(r"endometri|uterine")), ("vulva", P(r"vulv")), ("vagina", P(r"vagin")),
    ("oropharynx", P(r"oropharyn|tonsil|base of tongue|HPV")), ("oral cavity", P(r"oral cavity|oral tongue|floor of mouth")),
    ("larynx", P(r"laryn|glott")), ("nasopharynx", P(r"nasopharyn|\bNPC\b")), ("salivary", P(r"parotid gland tumou?r|salivary")),
    ("glioma/GBM", P(r"gliom|glioblastoma|\bGBM\b|oligodendro|astrocytom")), ("brain mets", P(r"brain met|\bWBRT\b|\bSRS\b")),
    ("meningioma", P(r"meningioma")), ("spine mets/MSCC", P(r"cord compression|spinal|vertebra|\bMSCC\b")),
    ("bone mets", P(r"bone met|osseous|fracture")), ("lymphoma", P(r"lymphoma|Hodgkin")), ("myeloma", P(r"myeloma|plasmacytoma")),
    ("benign", P(r"keloid|heterotopic|Graves|trigeminal|AVM|arteriovenous|desmoid|plantar|Dupuytren|osteoarthritis|pterygium|gynecomastia")),
]
TX_HINTS = [
    ("SBRT/SRS", P(r"SBRT|SABR|\bSRS\b|stereotactic")), ("brachytherapy", P(r"brachy|\bHDR\b|\bLDR\b|tandem|cylinder|seed")),
    ("chemoradiation", P(r"chemorad|chemoRT|concurrent")), ("surgery", P(r"resect|ectomy|surgery|surgical|dissection|excision")),
    ("systemic therapy", P(r"chemo|immunotherap|durvalumab|osimertinib|pembrolizumab|nivolumab|trastuzumab|ADT|androgen|temozolomide|cisplatin|endocrine")),
    ("EBRT", P(r"\bIMRT\b|\bVMAT\b|3D-?CRT|external beam|\bEBRT\b|whole[- ]breast|\bWBRT\b|\bPMRT\b|proton")),
]


def context_of(site, text):
    dis = [n for n, rx in DISEASE_HINTS if rx.search(text)]
    tx = [n for n, rx in TX_HINTS if rx.search(text)]
    return "; ".join(dis[:3]) or site, "; ".join(tx[:3])


# ---------------------------------------------------------------- walkers
claims = []
SKIP_KEYS = {"id", "image", "icon", "color", "x", "y", "rx", "ry", "cx", "cy", "kind", "style", "correctIndex", "level", "num", "module", "category", "reviewed", "_note", "tag", "w", "h", "src", "license", "credit", "url", "href"}
CAPTION_KEYS = {"caption", "credit", "source"}


def add(site, rel, path, section, kind, text):
    text = text.strip()
    if len(text) < 12 or not re.search(r"[A-Za-z]{3}", text):
        return
    base = f"{rel}|{path}|{text}"
    cid = f"{site[:3].upper()}-{hashlib.sha1(base.encode()).hexdigest()[:8]}"
    cats, risk = classify(text)
    if kind == "caption" and risk == "LOWER":
        cats = cats + ["figure-caption"]
    disease, tx = context_of(site, text)
    claims.append({
        "claim_id": cid, "site": site, "source_file": rel, "edit_in": generator_for(rel, path),
        "json_path": path, "section": section, "unit_kind": kind, "statement": text,
        "categories": "; ".join(cats), "risk": risk, "disease_context": disease, "treatment_context": tx,
    })


def walk(site, rel, node, path="", section=""):
    if isinstance(node, dict):
        sec = section
        for k in ("title", "label", "name"):
            if isinstance(node.get(k), str) and not sec.endswith(node[k]):
                sec = f"{section} > {node[k]}" if section else node[k]
                break
        for k, v in node.items():
            if k in SKIP_KEYS:
                continue
            walk(site, rel, v, f"{path}.{k}" if path else k, sec)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(site, rel, v, f"{path}[{i}]", section)
    elif isinstance(node, str):
        key = path.rsplit(".", 1)[-1].split("[")[0]
        txt = plain(node)
        if txt is None:
            for sec, kind, unit in html_units(node):
                full_sec = f"{section} > {sec}" if sec else section
                if kind in ("widget", "heading", "table-row"):
                    add(site, rel, path, full_sec, kind, unit)
                else:
                    for s in sentences(unit):
                        add(site, rel, path, full_sec, "caption" if key in CAPTION_KEYS else "text", s)
        else:
            for s in sentences(txt):
                add(site, rel, path, section, "caption" if key in CAPTION_KEYS else ("field:" + key), s)


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf8") as f:
        return json.load(f)


def walk_docs():
    for site in SITES:
        rel = f"src/data/docs/{site}.json"
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        for cat, doc in load(rel).items():
            # tag the High-Yield Summary block so corrections point at hy_summaries.py
            h = doc.get("html", "")
            hy_at = h.rfind("<div class='pearl'>")
            body, hy = (h[:hy_at], h[hy_at:]) if hy_at >= 0 and "High-Yield" in h[hy_at:hy_at + 200] else (h, "")
            for sec, kind, unit in html_units(body):
                if kind in ("widget", "heading", "table-row"):
                    add(site, rel, f"{cat}.html", f"{cat} > {sec}" if sec else cat, kind, unit)
                else:
                    for s in sentences(unit):
                        add(site, rel, f"{cat}.html", f"{cat} > {sec}" if sec else cat, "text", s)
            for sec, kind, unit in html_units(hy):
                for s in sentences(unit):
                    add(site, rel, f"{cat}.High-Yield Summary", f"{cat} > High-Yield Summary", "summary", s)


def walk_decks():
    for site in SITES:
        rel = f"src/data/decks/{site}.json"
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        for card in load(rel):
            sec = f"Flashcard {card['id']} ({card.get('category', '')})"
            # front+back is one claim (the answer only means something with its question)
            qa = f"Q: {plain(card['front']) or card['front']} A: {plain(card['back']) or card['back']}"
            add(site, rel, f"{card['id']}.front+back", sec, "flashcard", qa)
            if card.get("extra"):
                for s in sentences(plain(card["extra"]) or re.sub("<[^>]+>", "", card["extra"])):
                    add(site, rel, f"{card['id']}.extra", sec, "flashcard-extra", s)


def walk_cases():
    for site in SITES:
        rel = f"src/data/cases/{site}.json"
        if not os.path.exists(os.path.join(ROOT, rel)):
            continue
        d = load(rel)
        walk(site, rel, d.get("intro", ""), "intro", "Case-Based Practice intro")
        for case in d["cases"]:
            sec = case.get("title", case["id"])
            add(site, rel, f"{case['id']}.oneLiner", sec, "case-vignette", case.get("oneLiner", ""))
            for i, st in enumerate(case.get("steps", [])):
                ssec = f"{sec} > step {i + 1}: {st.get('label', '')}"
                base = f"{case['id']}.steps[{i}]"
                if st.get("context"):
                    walk(site, rel, st["context"], base + ".context", ssec)
                if st.get("caption"):
                    add(site, rel, base + ".caption", ssec, "caption", st["caption"])
                if "choices" in st and "correctIndex" in st:
                    ans = st["choices"][st["correctIndex"]]
                    add(site, rel, base + ".answer", ssec, "case-answer",
                        f"Q: {re.sub('<[^>]+>', '', st['prompt'])} A: {re.sub('<[^>]+>', '', ans)}")
                elif "answer" in st:
                    add(site, rel, base + ".answer", ssec, "case-answer",
                        f"Q: {re.sub('<[^>]+>', '', st['prompt'])} A: {re.sub('<[^>]+>', '', str(st['answer']))}")
                if st.get("explanation"):
                    walk(site, rel, st["explanation"], base + ".explanation", ssec)
                for k in ("table", "rows", "points", "details"):
                    if k in st:
                        walk(site, rel, st[k], f"{base}.{k}", ssec)


def walk_misc():
    walk("overview", "src/data/background.json", load("src/data/background.json"), "", "Before You Start")
    cur = load("src/data/curriculum.json")["sites"]
    for site, meta in cur.items():
        walk(site, "src/data/curriculum.json", meta, f"sites.{site}", f"Curriculum > {site}")
    for folder in ("anatomy", "imaging"):
        for site in SITES:
            rel = f"src/data/{folder}/{site}.json"
            if os.path.exists(os.path.join(ROOT, rel)):
                walk(site, rel, load(rel), "", folder.title())
    walk("overview", "src/data/services.json", load("src/data/services.json"), "", "Home tiles")


APP_SITE = [("rad101|modalities|consult", "overview"), ("breast", "breast"), ("hn-", "headneck"), ("th-|lung|LUNG|NODAL|nstage", "thoracic"),
            ("pr-|gleason|GLEASON|prostate|RISK", "prostate"), ("gyn|cervix|POSTOP|sedlis", "gyn"), ("cns|glioma|Glioma|gpa|Gpa", "cns"),
            ("gi-|rectal|pancrea|Rectal|Pancrea", "gi"), ("pal-|sins|Sins|mirels|Mirels", "palliative")]


def walk_appjs():
    """Clinical strings inside the widget section of app.js (quiz sets, drills, builders)."""
    rel = "src/app.js"
    lines = open(os.path.join(ROOT, rel), encoding="utf8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("const QUIZ_SETS"))
    end = next(i for i, l in enumerate(lines) if "function renderRiskBuilder" in l) + 120
    block, site = "", "overview"
    str_rx = re.compile(r'"((?:[^"\\]|\\.){25,})"|`((?:[^`\\]|\\.){25,})`')
    for i in range(start, min(end, len(lines))):
        line = lines[i]
        m = re.match(r'\s*"([\w-]+)":\s*[\[{]', line) or re.match(r"^(?:const|function)\s+(\w+)", line)
        if m:
            block = m.group(1)
            for pat, s in APP_SITE:
                if re.search(pat, block):
                    site = s
                    break
        for sm in str_rx.finditer(line):
            s = sm.group(1) or sm.group(2)
            if "${" in s and not re.search(r"[A-Za-z]{4,}\s+[A-Za-z]{3,}\s+[A-Za-z]{3,}", re.sub(r"\$\{[^}]*\}", "", s)):
                continue
            if re.search(r"class=\"|querySelector|addEventListener|container\.", s):
                continue
            txt = re.sub(r"<[^>]+>", "", html.unescape(s))
            txt = re.sub(r"\s+", " ", txt).strip()
            add(site, rel, f"line {i + 1}", block, "app.js", txt)
        # builder lookup rows that hold short clinical facts (e.g. N2a: { T1:"IIB" ...})
        if re.match(r"\s*N[0-3][ab]?:\s*\{\s*T1:", line) or re.search(r"return \{ T1mi:", line):
            add(site, rel, f"line {i + 1}", block, "app.js-logic", re.sub(r"\s+", " ", line.strip()))


def main():
    walk_docs()
    walk_decks()
    walk_cases()
    walk_misc()
    walk_appjs()

    # dedupe exact repeats within the same location
    seen, uniq = set(), []
    for c in claims:
        if c["claim_id"] in seen:
            continue
        seen.add(c["claim_id"])
        uniq.append(c)

    findings_path = os.path.join(OUT_DIR, "findings.json")
    findings = json.load(open(findings_path, encoding="utf8")) if os.path.exists(findings_path) else []
    by_id = {c["claim_id"]: c for c in uniq}
    unmatched = []
    for f in findings:
        hits = []
        for cid in f.get("claim_ids", []):
            if cid in by_id:
                hits.append(by_id[cid])
        for m in f.get("match", []):
            got = [c for c in uniq if (not m.get("file") or c["source_file"] == m["file"]) and m["text"] in c["statement"]]
            hits.extend(got)
            if not got:
                unmatched.append((f["finding_id"], m))
        f["_claims"] = sorted({c["claim_id"] for c in hits})
        for c in hits:
            prev = c.get("finding_ids", "")
            c["finding_ids"] = f"{prev}; {f['finding_id']}" if prev else f["finding_id"]
            # strongest status wins: Revise > Expert review > Unable to verify > Verified
            order = ["Revise", "Expert review", "Unable to verify", "Verified"]
            cur = c.get("status")
            if cur is None or order.index(f["status"]) < order.index(cur):
                c["status"] = f["status"]
            c["verification_findings"] = (c.get("verification_findings", "") + " | " if c.get("verification_findings") else "") + f["finding"]
            c["supporting_source"] = (c.get("supporting_source", "") + " | " if c.get("supporting_source") else "") + "; ".join(
                f"{s['title']} ({s.get('year', '')}){' PMID ' + s['pmid'] if s.get('pmid') else ''}{' doi:' + s['doi'] if s.get('doi') else ''} {s.get('url', '')}".strip()
                for s in f.get("sources", []))
            if f.get("correction"):
                c["proposed_correction"] = f["correction"]
            if f.get("implemented"):
                c["implemented"] = f["implemented"]
            c["date_reviewed"] = f.get("date", "")
            c["reviewer"] = f.get("reviewer", "")
    # cross-references: claims touched by the same finding in other files
    for f in findings:
        files = {by_id[i]["source_file"] for i in f["_claims"] if i in by_id}
        for cid in f["_claims"]:
            others = [o for o in f["_claims"] if o != cid and by_id[o]["source_file"] != by_id[cid]["source_file"]]
            if others:
                by_id[cid]["related_claims"] = "; ".join(sorted(set((by_id[cid].get("related_claims", "") + ";" if by_id[cid].get("related_claims") else "").split(";") + others) - {""}))[:400]

    # Claims read line by line in the first-pass review (IDs captured from the
    # review dumps). A claim whose text changed after that read gets a new ID
    # and so is not credited. "Read" is not "Verified": no source is attached.
    fp_path = os.path.join(OUT_DIR, "first_pass_reviewed_ids.txt")
    reviewed = set(open(fp_path).read().split()) if os.path.exists(fp_path) else set()
    for c in uniq:
        h = c["claim_id"].split("-", 1)[1]
        if h in reviewed or h[1:] in reviewed:
            c["first_pass"] = ("Read 2026-10-16/17; see finding" if c.get("finding_ids")
                               else "Read 2026-10-16/17; no discrepancy found against reviewer knowledge; no source attached")
        else:
            c["first_pass"] = "Not individually read"

    cols = ["claim_id", "risk", "status", "first_pass", "site", "source_file", "edit_in", "json_path", "section", "unit_kind", "statement",
            "categories", "disease_context", "treatment_context", "supporting_source", "verification_findings",
            "proposed_correction", "implemented", "related_claims", "finding_ids", "date_reviewed", "reviewer"]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "claim_ledger.csv"), "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        risk_order = {"HIGH": 0, "MODERATE": 1, "LOWER": 2}
        for c in sorted(uniq, key=lambda c: (risk_order[c["risk"]], c["site"], c["source_file"], c["json_path"])):
            c.setdefault("status", "Pending")
            w.writerow(c)

    # summary for the report
    from collections import Counter
    summ = {
        "total_claims": len(uniq),
        "by_risk": Counter(c["risk"] for c in uniq),
        "by_status": Counter(c["status"] for c in uniq),
        "high_by_status": Counter(c["status"] for c in uniq if c["risk"] == "HIGH"),
        "high_first_pass": Counter(c["first_pass"].split(";")[0] for c in uniq if c["risk"] == "HIGH"),
        "all_first_pass": Counter(c["first_pass"].split(";")[0] for c in uniq),
        "by_site": Counter(c["site"] for c in uniq),
        "high_by_site": Counter(c["site"] for c in uniq if c["risk"] == "HIGH"),
        "by_category": Counter(cat for c in uniq for cat in c["categories"].split("; ")),
        "findings": len(findings),
        "unmatched_finding_targets": unmatched,
    }
    with open(os.path.join(OUT_DIR, "ledger_summary.json"), "w", encoding="utf8") as fh:
        json.dump(summ, fh, indent=1, default=dict)
    print(json.dumps({k: v for k, v in summ.items() if k != "by_category"}, indent=1, default=dict))
    if unmatched:
        print("WARNING: finding targets that matched no claim:", file=sys.stderr)
        for u in unmatched:
            print("  ", u, file=sys.stderr)


if __name__ == "__main__":
    main()
