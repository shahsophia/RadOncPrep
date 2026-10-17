#!/usr/bin/env python3
"""
Source of truth for the Palliative & Benign readings (src/data/docs/palliative.json).
This site has no anatomy, lymph node, or staging reading: its "staging" is
goals, prognosis, urgency, and stability, so Workup & Prognosis takes that slot.

Every number and trial statement here was checked against the cited source
(PubMed abstract or full text, or the guideline itself) in October 2026.
Source links use PubMed IDs; see tools/sources.py for the trial-box citations.

Usage:  python3 tools/palliative_readings.py
        python3 tools/hy_summaries.py   (fills each High-Yield Summary)
        python3 build.py
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Replaced by tools/hy_summaries.py (HY["palliative"]).
HY = "<div class='pearl hy-summary'>\n<strong>High-Yield Summary</strong>\n<ul style='margin-bottom:0;'>\n<li>See tools/hy_summaries.py</li>\n</ul>\n</div>"


# --------------------------------------------------------------------------- helpers
def pm(pmid, text):
    """Inline link to a PubMed record."""
    return f"<a href='https://pubmed.ncbi.nlm.nih.gov/{pmid}/' target='_blank' rel='noopener'>{text}</a>"


def ext(url, text):
    return f"<a href='{url}' target='_blank' rel='noopener'>{text}</a>"


ASTRO_BONE = pm(38788923, "ASTRO bone metastases guideline (2024)")
NICE_MSCC = ext("https://www.nice.org.uk/guidance/ng234", "NICE guideline NG234 (2023)")
NICE_DUP = ext("https://www.nice.org.uk/guidance/ipg573", "NICE IPG573 (2016)")
EUGOGO = pm(34297684, "EUGOGO guideline (2021)")


def reveal(summary, body):
    return f"<details class='reveal'>\n<summary>{summary}<span class='chev'>&#9662;</span></summary>\n<div class='reveal-body'>{body}</div>\n</details>"


def flow(*labels):
    parts = []
    for i, label in enumerate(labels, 1):
        if i > 1:
            parts.append("<div class='flow-arrow'>&rarr;</div>")
        parts.append(f"<div class='flow-step'><div class='flow-num'>{i}</div><div class='flow-label'>{label}</div></div>")
    return "<div class='flow-diagram'>\n" + "\n".join(parts) + "\n</div>"


def cards(*items):
    out = []
    for i, (title, body) in enumerate(items, 1):
        out.append(f"<div class='card'><div class='card-num'>{i}</div><div class='card-title'>{title}</div><p>{body}</p></div>")
    return "<div class='card-grid'>\n" + "\n".join(out) + "\n</div>"


def table(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<div class='table-wrap'><table>\n<thead><tr>{th}</tr></thead>\n<tbody>\n{body}\n</tbody></table></div>"


def studies(*items):
    return "<div class='study-grid'>\n" + "\n".join(
        f"<div class='study'><div class='st-name'>{n}</div><p>{p}</p></div>" for n, p in items) + "\n</div>"


def quiz(title, items):
    qs = "\n".join(f"<div class='qc-item'><div class='qc-q'><p>{q}</p></div><div class='qc-a'><p>{a}</p></div></div>" for q, a in items)
    return f"<div class='quiz-carousel' data-inline-quiz='{title}'>\n{qs}\n</div>"


def compare(*cols):
    return "<div class='compare-grid'>\n" + "\n".join(
        f"<div class='compare-col'><span class='compare-label'>{lab}</span><h5>{h}</h5><p>{p}</p></div>" for lab, h, p in cols) + "\n</div>"


def big(t):
    return f"<div class='big-idea'>{t}</div>"


def pearl(t, label="Clinical Pearl"):
    return f"<div class='pearl'><strong>{label}</strong><p>{t}</p></div>"


def figure(inner, caption, label):
    """An original HTML/CSS teaching figure. Captions say what the figure is
    (a schematic, not patient data) and where any numbers come from."""
    return (f"<figure class='edu-fig' role='group' aria-label='{label}'>\n{inner}\n"
            f"<figcaption>{caption}</figcaption>\n</figure>")


def factor_map(title, items, result):
    """Several inputs that all feed one decision."""
    cells = "\n".join(
        f"<div class='fm-item'><span class='fm-k'>{k}</span><p class='fm-q'>{q}</p><p class='fm-then'>{t}</p></div>"
        for k, q, t in items)
    return (f"<div class='factor-map'>\n<div class='fm-title'>{title}</div>\n<div class='fm-grid'>\n{cells}\n</div>\n"
            f"<div class='fm-arrow' aria-hidden='true'>&darr;</div>\n<div class='fm-result'>{result}</div>\n</div>")


def dpath(title, nodes):
    """A decision pathway: each node is a question with labeled branches.
    kind: 'go' (continue down the path), 'stop' (act now), 'alt' (another route)."""
    out = [f"<div class='dpath'>\n<div class='dp-title'>{title}</div>\n<ol class='dp-list'>"]
    for q, branches in nodes:
        bs = "".join(f"<li class='dp-b dp-{kind}'><span class='dp-lab'>{lab}</span><span class='dp-txt'>{txt}</span></li>"
                     for lab, txt, kind in branches)
        out.append(f"<li class='dp-node'><div class='dp-q'>{q}</div><ul class='dp-branches'>{bs}</ul></li>")
    out.append("</ol>\n</div>")
    return "\n".join(out)


def checklist(title, items):
    lis = "".join(f"<li><span class='ck-box' aria-hidden='true'></span><span><strong>{k}</strong> {v}</span></li>" for k, v in items)
    return f"<div class='checklist'>\n<div class='ck-title'>{title}</div>\n<ul>{lis}</ul>\n</div>"


# Time axis for timelines: log scale from 3 days to about 7 years.
_T0, _T1 = math.log(3), math.log(2500)


def tpos(days):
    return round(100 * (math.log(max(days, 3)) - _T0) / (_T1 - _T0), 1)


def timeline(title, rows, ticks, note=""):
    """rows: (label, [(start_days, end_days, text, kind)], [(day, text)]).
    Bars and numbered markers sit on a shared time axis; their text goes in a
    legend under each row so nothing overlaps on a phone."""
    tick_html = "".join(f"<span class='tl-tick' style='left:{tpos(d)}%'>{t}</span>" for d, t in ticks)
    rows_html = []
    for label, segs, marks in rows:
        seg_html = "".join(
            f"<span class='tl-seg tl-{kind}' style='left:{tpos(a)}%;width:{max(tpos(b) - tpos(a), 2)}%'></span>"
            for a, b, txt, kind in segs)
        mark_html = "".join(f"<span class='tl-mark' style='left:{tpos(d)}%'>{i}</span>" for i, (d, t) in enumerate(marks, 1))
        legend = "".join(f"<li><span class='tl-sw tl-{kind}' aria-hidden='true'></span>{txt}</li>" for a, b, txt, kind in segs)
        legend += "".join(f"<li><span class='tl-num' aria-hidden='true'>{i}</span>{t}</li>" for i, (d, t) in enumerate(marks, 1))
        rows_html.append(f"<div class='tl-row'><div class='tl-label'>{label}</div><div class='tl-track' aria-hidden='true'>{seg_html}{mark_html}</div>"
                         f"<ul class='tl-legend'>{legend}</ul></div>")
    return (f"<div class='timeline'>\n<div class='tl-title'>{title}</div>\n" + "\n".join(rows_html) +
            f"\n<div class='tl-row tl-axis' aria-hidden='true'><div class='tl-label'></div><div class='tl-track'>{tick_html}</div></div>\n"
            + (f"<p class='tl-note'>{note}</p>\n" if note else "") + "</div>")


def bars(title, groups, note):
    """Horizontal bars. groups: (heading, [(label, pct, text, kind)])."""
    out = [f"<div class='hbars'>\n<div class='hb-title'>{title}</div>"]
    for heading, rows in groups:
        out.append(f"<div class='hb-group'><div class='hb-head'>{heading}</div>")
        for label, pct, text, kind in rows:
            out.append(f"<div class='hb-row'><span class='hb-label'>{label}</span><span class='hb-track'>"
                       f"<span class='hb-bar hb-{kind}' style='width:{pct}%'></span></span><span class='hb-val'>{text}</span></div>")
        out.append("</div>")
    out.append(f"<p class='hb-note'>{note}</p>\n</div>")
    return "\n".join(out)


def ev(kind, text):
    return f"<span class='ev ev-{kind}'>{text}</span>"


# ---------------------------------------------------------------------------
BACKGROUND = "\n".join([
"<p>Not every patient on a radiation service has a cancer you are trying to cure. Much of the day is <strong>palliative</strong> work (pain, bleeding, obstruction, a spine at risk), <strong>emergencies</strong> paged in overnight, a smaller group of <strong>benign conditions</strong>, and <strong>radiosurgery</strong> for a few non-cancer brain problems. This module is the catch-all for that work, plus a short tour of the sites the other modules do not cover.</p>",
"<p>There is no anatomy, nodal, or staging reading here. The question that replaces staging is: <strong>what is the goal, how long is this patient likely to live, how urgent is it, and what is the least burdensome treatment that reaches that goal?</strong></p>",
flow("Who is this patient? (this reading)", "Goals, prognosis, stability", "Palliative RT", "Emergencies", "Benign disease", "Functional and vascular SRS", "Other sites"),
"",
"<h3>Four Kinds of Patients</h3>",
table(["Patient", "Typical example", "What radiation is for", "What usually comes first"], [
 ["<strong>Palliative</strong>", "Painful bone metastasis, bleeding bladder tumor, obstructing lung mass", "Relieve a symptom, or prevent one, with as few visits as the goal allows", "Goals, prognosis, and checking for instability or cord compression"],
 ["<strong>Emergency</strong>", "Cord compression, SVC obstruction, life-threatening bleeding", "Protect function (walking, breathing) or help stop the event", "Often something else: steroids, MRI, a surgeon, a stent, resuscitation, or a biopsy"],
 ["<strong>Benign</strong>", "Dupuytren nodules, keloid, heterotopic ossification prevention, painful osteoarthritis", "Slow overgrowth, prevent recurrence, or relieve pain when other treatment has not worked", "Conservative care, the stage of the disease, and a consent talk about long-term risk"],
 ["<strong>Functional or vascular SRS</strong>", "Trigeminal neuralgia, arteriovenous malformation (AVM)", "A precise single high dose to a tiny target, with a delayed effect", "Medication (trigeminal neuralgia) or a multidisciplinary AVM review"],
]),
"",
"<h3>Name the Intent Before the Dose</h3>",
"<p>The same machine and sometimes the same dose serve very different goals. Say which one you mean:</p>",
table(["Intent", "Goal", "Example"], [
 ["<strong>Palliative</strong>", "Relieve a symptom the patient has now", "8 Gy in 1 for a painful rib metastasis"],
 ["<strong>Prophylactic</strong>", "Prevent a problem that has not happened yet", "Radiation to a high-risk asymptomatic bone metastasis; a single fraction before hip surgery to prevent heterotopic ossification"],
 ["<strong>Emergency</strong>", "Protect function during an acute threat, alongside other urgent care", "Radiation for cord compression after steroids and surgical review"],
 ["<strong>Ablative or definitive</strong>", "Durable control of disease, sometimes cure", "SBRT for a few metastases; 40-50 Gy for a solitary plasmacytoma"],
]),
"<p>Dose does <strong>not</strong> define intent. Ranges overlap across these groups: a benign desmoid tumor may get 50-56 Gy, a cured follicular lymphoma 24 Gy, and a palliative bone metastasis 30 Gy. The right dose depends on the <strong>indication, the disease, the goal, the technique, and the normal tissue nearby</strong>.</p>",
big("Dose follows the goal and the disease, not the other way around. A low dose can cure a radiosensitive lymphoma, and a high dose can be purely palliative."),
"",
"<h3>What Shapes a Palliative Plan</h3>",
figure(factor_map("Five inputs, one plan", [
  ("Goal", "What does the patient want this treatment to do?", "Pain relief, function, prevention, or durable control"),
  ("Prognosis", "Weeks, months, or years?", "Shorter survival favors fewer visits"),
  ("Urgency", "Is function at risk in hours or days?", "Neurologic deficit or airway threat changes the order of steps"),
  ("Stability", "Is the spine or long bone mechanically sound?", "Instability or fracture risk needs a surgeon's view"),
  ("Preference", "Travel, time, side effects, other treatment", "Shared decision on the number of visits"),
 ], "<strong>Plan:</strong> the least burdensome treatment that reaches the goal, in the right order with surgery, systemic therapy, and supportive care."),
 "Schematic summary of the factors this module uses; not a validated scoring tool.",
 "Five factors that shape a palliative radiation plan"),
"",
"<h3>Palliative Radiation: Who and Why</h3>",
"<p>Palliative radiation is one of the most common things a radiation oncologist does, and the most common reason is a <strong>painful bone metastasis</strong>.</p>",
cards(
 ("Pain", "Bone metastases, nerve or plexus invasion, liver capsule stretch, pelvic masses. Relief often begins within 1-2 weeks; most responses are seen by about 4-8 weeks."),
 ("Bleeding", "Hemoptysis, hematuria, vaginal or rectal bleeding, fungating skin or breast tumors. Hemostatic RT often slows bleeding over days, alongside other measures."),
 ("Obstruction", "Airway, esophagus, SVC, ureter, or bowel. Stents and procedures act faster; radiation can add durability."),
 ("Neurologic function", "Cord compression and brain metastases. The goal is to keep the patient walking, thinking, and continent."),
),
"<h4>Which Cancers Go to Bone?</h4>",
"<p>Most bone metastases come from <strong>prostate, breast, lung, kidney, and thyroid</strong> cancer, and <strong>multiple myeloma</strong> lives in the marrow. The spine, pelvis, ribs, and proximal femur and humerus are the usual sites, because that is where red marrow is.</p>",
table(["Lesion type", "Typical cancers", "Why it matters"], [
 ["<strong>Blastic</strong> (bone-forming, bright on CT)", "Prostate, some breast", "Shows up well on bone scan"],
 ["<strong>Lytic</strong> (bone-destroying, dark on CT)", "Kidney, thyroid, myeloma, lung, many breast", "Higher fracture risk; myeloma can be <strong>invisible on bone scan</strong>"],
 ["<strong>Mixed</strong>", "Breast, lung", "Judge fracture risk by the lytic component"],
]),
pearl("Most patients with bone metastases have them in more than one place. Treat the lesion causing the symptom, and the occasional high-risk lesion likely to cause trouble soon (see Palliative Radiation), not every spot on the scan."),
"",
"<h3>Benign Disease: Who and Why</h3>",
"<p>Radiation for benign conditions is common in Germany and parts of Europe and much less common in the United States. The evidence differs a lot from one condition to the next, so each indication needs its own justification. Broadly, radiation is used to:</p>",
compare(
 ("Usually below 1 Gy per fraction", "Reduce inflammation and pain", "Very low doses change how inflammatory cells and vessel walls behave. Used for painful <strong>osteoarthritis</strong> and <strong>plantar fasciitis</strong>, where the evidence is debated."),
 ("Moderate doses", "Stop overgrowth or prevent recurrence", "Doses that stop fibroblasts or bone precursor cells from multiplying: early <strong>Dupuytren</strong> disease, <strong>keloids</strong> after excision, <strong>heterotopic ossification</strong> prevention, <strong>gynecomastia</strong> prevention."),
 ("Tumor-level doses", "Control a benign tumor", "Benign tumors such as <strong>desmoid tumors</strong>, meningiomas, and vestibular schwannomas get doses similar to cancer treatment."),
),
"<p>Functional and vascular radiosurgery (trigeminal neuralgia, AVMs) is a separate group: a tiny target and a very high single dose. It has its own reading.</p>",
"<h4>The Rule for Benign Radiation</h4>",
cards(
 ("Alternatives first", "Radiation is usually offered after, or instead of, other treatments the patient cannot have, and only when the expected benefit justifies it."),
 ("Smallest effective dose and volume", "Use the lowest dose and the smallest field that achieves the goal."),
 ("Long-term risk is part of consent", "Any radiation carries a small lifetime risk of a second cancer, highest in <strong>younger patients</strong> and near the <strong>thyroid, breast, eyes, and gonads</strong>. Explain the benefit, the alternatives, the uncertainty, and that risk, and document it."),
),
"",
"<h3>The Rest of the Service</h3>",
"<p>Lymphoma, skin cancer, sarcoma, plasmacytoma and myeloma, pediatric tumors, total body irradiation, and a few smaller sites (bladder, seminoma, thymoma, eye) do not have their own module. The last reading covers each in a few lines: what it is, where radiation fits, and the trial or rule you are most likely to be asked about.</p>",
"",
HY,
])

# ---------------------------------------------------------------------------
WORKUP = "\n".join([
"<p>In a curative site, stage tells you the plan. On the palliative service, five questions do that job. Treat them as the checklist you run before presenting a palliative consult:</p>",
checklist("Palliative consult checklist", [
 ("1. What is the symptom, and is it from this lesion?", "Match the history and exam to the imaging. A hot spot on the scan may not be the cause of the pain."),
 ("2. What is the goal?", "Relieve pain, stop bleeding, keep walking, prevent a fracture, or durable control of limited disease. Ask the patient."),
 ("3. How long is the patient likely to live?", "Performance status, primary cancer, sites of disease, and remaining systemic options."),
 ("4. Is the bone or spine stable, and is the cord safe?", "Mechanical pain, collapse, a lytic long-bone lesion, or any neurologic change needs a surgical opinion and urgent imaging."),
 ("5. What has already been treated?", "Prior radiation to the same area, and when; get the old plan."),
]),
big("Stage tells you the plan in curative disease. In palliative disease, the goal, the prognosis, the urgency, and stability tell you the plan."),
"",
"<h3>Goals and Prognosis</h3>",
"<p>Start with what matters to the patient and what they understand about their illness. Then estimate prognosis honestly. Clinicians tend to <strong>overestimate</strong> survival, which can lead to courses longer than the patient's remaining time.</p>",
table(["Expected survival", "What it often means for radiation"], [
 ["<strong>Weeks</strong>", "A single fraction or no radiation; focus on comfort and hospice. Pain relief takes 1-2 weeks or more to start, so very short survival may not leave time to benefit."],
 ["<strong>Months</strong>", "Short courses (8 Gy in 1, 20 Gy in 5). A single fraction trades fewer visits for a higher chance of retreatment."],
 ["<strong>Years</strong> (or limited disease)", "A longer course (for example 30 Gy in 10) or <strong>SBRT</strong> in selected patients, for durable local control."],
]),
"<p>These are tendencies, not rules. The " + ASTRO_BONE + " lists 8 Gy in 1, 20 Gy in 5, 24 Gy in 6, and 30 Gy in 10 as appropriate options for painful bone metastases and recommends <strong>shared decision-making</strong> that weighs prognosis, prior radiation, normal-tissue risk, quality of life, cost, and the patient's goals.</p>",
"<h4>What Predicts Survival</h4>",
"<ul>",
"<li><strong>Performance status</strong> (KPS or ECOG) is the most useful single predictor. A patient in bed most of the day (KPS 40 or less, ECOG 3-4) usually has weeks to a few months.</li>",
"<li><strong>Primary cancer</strong>: breast and prostate cancer with bone-only disease can live for years; lung cancer with visceral metastases usually much less.</li>",
"<li><strong>Where the metastases are</strong>: bone only is better than liver or brain.</li>",
"<li><strong>Systemic options left</strong>: a patient starting effective targeted therapy has a different outlook from one who has exhausted treatment.</li>",
"</ul>",
reveal("Reference: prognostic scores you might hear named",
 "<ul><li><strong>Chow three-item model</strong> (" + pm(12128132, "Chow 2002") + ", " + pm(18676092, "validated 2009") + "): non-breast primary, metastases beyond bone, and KPS 60 or less. More risk factors mean shorter median survival, from over a year with 0-1 factors to about 2 months with all 3.</li>"
 "<li><strong>TEACHH</strong> (" + pm(24122413, "Krishnan 2014") + "): tumor type, ECOG, age, prior palliative chemotherapy, hospitalizations in the last 3 months, and liver metastases.</li>"
 "<li><strong>Rades score</strong> (" + pm(17948910, "cord compression") + ") and the <strong>GPA</strong> (brain metastases, see CNS).</li>"
 "<li>The <strong>surprise question</strong> (\"Would I be surprised if this patient died in the next year?\") is a quick bedside prompt for a goals-of-care conversation.</li>"
 "<li>All of these help frame a discussion. None predicts an individual patient's survival precisely.</li></ul>"),
"",
"<h3>Four Kinds of Bone Pain</h3>",
"<p>The kind of pain points to the next step. Radiation treats tumor; it does not rebuild bone or decompress a cord by itself in the moment.</p>",
table(["Type", "What it feels like", "What it suggests", "Usual next step"], [
 ["<strong>Biologic</strong>", "Steady, often worse at night, better with steroids", "Inflammation from the tumor itself", "Radiation (and analgesics) usually help"],
 ["<strong>Mechanical</strong>", "Pain with movement, sitting up, or bearing weight; better lying still", "The bone or spine may be <strong>unstable</strong>", "Imaging and a <strong>surgical opinion</strong>; RT may follow"],
 ["<strong>Neuropathic (radicular)</strong>", "Shooting pain along a nerve root or band around the chest", "Nerve root compression or invasion", "Check for epidural disease; RT often given in more than 1 fraction"],
 ["<strong>Neurologic compromise</strong>", "Weakness, numbness below a level, bladder or bowel change", "<strong>Cord or cauda equina compression</strong>", "Emergency pathway: steroids, whole-spine MRI, spine surgery review"],
]),
"",
"<h3>Imaging: Which Test Answers Which Question</h3>",
table(["Question", "Usual test", "Why"], [
 ["Where are the bone metastases?", "<strong>Bone scan</strong> or <strong>PET/CT</strong> (FDG; PSMA for prostate)", "Bone scan detects bone-forming activity, so it can <strong>miss purely lytic lesions such as myeloma</strong> (use low-dose whole-body CT, MRI, or PET)"],
 ["Will this long bone break?", "<strong>Plain X-rays</strong> of the whole bone, then CT", "Shows cortical destruction and how much of the bone's width is involved"],
 ["Is the cord compressed?", "<strong>MRI of the whole spine</strong>", "Many patients have disease at more than one level; CT myelogram if MRI is impossible"],
 ["Is the spine stable?", "<strong>CT</strong> plus MRI", "Collapse, alignment, and which parts of the vertebra are involved feed the SINS score"],
 ["Planning", "<strong>CT simulation</strong>", "Old plans and diagnostic imaging are fused to see prior dose and the target"],
]),
"<p><strong>Do you need a biopsy?</strong> Often yes if there is no known cancer, if this would be the first metastasis, if the lesion is solitary after a long disease-free interval, or if a second cancer, lymphoma, myeloma, or infection is possible. Lymphoma and myeloma change the plan, because both are very radiosensitive and often treated with drugs first.</p>",
"",
"<h3>Scores Are Decision Support, Not Decisions</h3>",
"<p>The three scores below organize what you see so you can communicate it. Each was built to prompt the right conversation (usually with a surgeon), and each has limits. None replaces the history, the exam, the images, and a multidisciplinary discussion.</p>",
"",
"<h3>Is the Spine Stable? SINS</h3>",
"<p>The <strong>Spinal Instability Neoplastic Score</strong> (" + pm(20562730, "Fisher 2010") + ") adds six features into a 0-18 score. You do not need to memorize the points; know what pushes a spine toward instability and that <strong>a score of 7 or higher should prompt a spine surgery consultation</strong>.</p>",
"<div class='sins-builder'></div>",
"<ul>",
"<li><strong>0-6: stable.</strong> Stability does not, by itself, call for surgery.</li>",
"<li><strong>7-12: indeterminate (potentially unstable).</strong> Surgical consultation; some patients still go on to radiation alone.</li>",
"<li><strong>13-18: unstable.</strong> Stabilization or cement augmentation is usually considered. <strong>Radiation does not restore mechanical stability.</strong></li>",
"</ul>",
"",
"<h3>Is the Cord Compressed? Bilsky Grade</h3>",
"<p>The <strong>epidural spinal cord compression (ESCC) scale</strong> (" + pm(20809724, "Bilsky 2010") + ") grades on axial T2 MRI how far tumor has pushed into the canal.</p>",
table(["Grade", "What axial T2 MRI shows", "Group"], [
 ["<strong>0</strong>", "Tumor confined to bone", "Low grade"],
 ["<strong>1a</strong>", "Epidural tumor without deforming the thecal sac", "Low grade"],
 ["<strong>1b</strong>", "Thecal sac deformed, cord not touched", "Low grade"],
 ["<strong>1c</strong>", "Thecal sac deformed and tumor abuts the cord, without compressing it", "Low grade (closest to the cord)"],
 ["<strong>2</strong>", "Cord compressed, CSF still visible around it", "High grade"],
 ["<strong>3</strong>", "Cord compressed, no CSF visible", "High grade"],
]),
"<p>The grade describes the images. Whether the patient has <strong>symptoms</strong> (myelopathy, radiculopathy) is a separate and equally important question.</p>",
"<h4>Putting It Together: NOMS</h4>",
"<p>Spine teams combine these into the <strong>NOMS</strong> framework (" + pm(23709750, "Laufer 2013") + "): Neurologic, Oncologic, Mechanical, and Systemic.</p>",
figure("\n".join([
 "<div class='noms'>",
 "<div class='noms-grid' role='table' aria-label='Neurologic and oncologic assessment'>",
 "<div class='ng-corner' role='columnheader'>Tumor type, by response to conventional radiation</div>",
 "<div class='ng-col' role='columnheader'>Low-grade compression<br><span>Bilsky 0-1</span></div>",
 "<div class='ng-col' role='columnheader'>High-grade compression<br><span>Bilsky 2-3</span></div>",
 "<div class='ng-row' role='rowheader'>Radiosensitive<br><span>lymphoma, myeloma, seminoma; breast, prostate, ovarian, neuroendocrine</span></div>",
 "<div class='ng-cell ng-rt' role='cell'><strong>Conventional RT</strong></div>",
 "<div class='ng-cell ng-rt' role='cell'><strong>Conventional RT</strong>, usually without surgery</div>",
 "<div class='ng-row' role='rowheader'>Radioresistant<br><span>kidney, thyroid, liver, colon, many NSCLC, sarcoma, melanoma</span></div>",
 "<div class='ng-cell ng-sbrt' role='cell'><strong>SBRT</strong> (spine radiosurgery)</div>",
 "<div class='ng-cell ng-surg' role='cell'><strong>Surgical decompression</strong> (\"separation surgery\"), then SBRT</div>",
 "</div>",
 "<div class='noms-gates'>",
 "<div class='ngate'><span class='ngate-k'>M</span><p><strong>Mechanical instability</strong> is its own indication for stabilization or cement augmentation, whatever the grade or tumor type.</p></div>",
 "<div class='ngate'><span class='ngate-k'>S</span><p><strong>Systemic</strong> disease and fitness decide whether surgery is reasonable at all. A patient who cannot tolerate surgery is treated with radiation and supportive care.</p></div>",
 "</div>",
 "</div>",
]), "Simplified from the NOMS framework (Laufer et al., <em>Oncologist</em> 2013). Real decisions also weigh symptoms, the speed of neurologic change, prior radiation, and patient goals. Schematic, not a protocol.",
 "NOMS spine metastasis decision framework"),
"",
"<h3>Will This Long Bone Break? Mirels Score</h3>",
"<p>For a lesion in the femur, humerus, or another long bone, <strong>Mirels' score</strong> (" + pm(2684463, "Mirels 1989") + ") adds four features (site, pain, lesion type, and how much of the bone's width is involved), each scored 1-3, for a total of 4-12.</p>",
"<div class='mirels-builder'></div>",
"<ul>",
"<li><strong>9 or more</strong>: high fracture risk. Orthopedics for <strong>prophylactic fixation</strong>, then postoperative radiation.</li>",
"<li><strong>8</strong>: borderline. Mirels' original paper suggested fixation at 8 or more; many teams treat 8 as a judgment call.</li>",
"<li><strong>7 or less</strong>: lower risk; radiation alone is usually reasonable.</li>",
"</ul>",
"<p>Mirels is sensitive but not very specific: it flags many lesions that would not have broken. Pain with weight bearing, lesion size, and the patient's activity and prognosis all go into the orthopedic decision.</p>",
pearl("<strong>Pain with weight bearing</strong> (functional pain) in a lytic femur lesion is a warning sign of impending fracture. Ask about it on every bone metastasis consult and protect weight bearing until orthopedics weighs in."),
"",
"<h3>Prior Radiation</h3>",
"<p>Always ask whether the patient has had radiation before. Get the old plan, find the previous dose to the spinal cord and other limiting organs, and plan around the <strong>cumulative</strong> dose and the time since the first course. Re-irradiation is often possible, especially with conventional palliative doses or SBRT, and the ASTRO guideline lists 8 Gy in 1, 20 Gy in 5, 24 Gy in 6, and (for spine) 20 Gy in 8 as options.</p>",
quiz("Read the Consult", [
 ("A man with prostate cancer has a painful L3 metastasis. Pain is worst at night, steady, and better on dexamethasone. MRI shows bone disease without epidural extension. Biologic or mechanical pain?", "<strong>Biologic.</strong> Night pain that steroids relieve comes from the tumor and usually responds well to radiation."),
 ("A woman with renal cell carcinoma has back pain only when she sits up or stands. CT shows a lytic T12 lesion with 60% collapse. What score do you calculate and who do you call?", "<strong>SINS</strong>: junctional level 3 + mechanical pain 3 + lytic 2 + collapse over 50% 3 = at least 11, before alignment and posterior elements. Call <strong>spine surgery</strong>: mechanical pain suggests instability, which radiation cannot fix."),
 ("A lytic lesion in the mid femoral shaft takes up most of the bone's width and hurts with walking. Mirels score?", "Lower limb 2 + functional pain 3 + lytic 3 + more than 2/3 of the width 3 = <strong>11</strong>. High fracture risk: orthopedics for <strong>prophylactic fixation</strong>, then postoperative RT."),
 ("A patient with myeloma has new rib pain but a negative bone scan. What do you do?", "Bone scan can <strong>miss purely lytic myeloma lesions</strong>. Get CT, MRI, or PET. Myeloma is very radiosensitive, so low palliative doses usually work well."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
PALLIATIVE = "\n".join([
"<p>Palliative radiation answers one question: <strong>what is the shortest, simplest course that achieves this patient's goal?</strong> Work through three questions in order.</p>",
cards(
 ("Is this uncomplicated painful bone disease?", "If yes, the fractionation choice is mostly about visits, retreatment, and preference."),
 ("Is the goal something more?", "Durable local control, preventing a complication, or treating limited (oligometastatic) disease changes the dose and technique."),
 ("Is a systemic or radiopharmaceutical option relevant?", "Widespread painful bone disease, or a cancer with an effective targeted radiopharmaceutical, may be better treated systemically."),
),
"",
"<h3>Before You Discuss a Bone Lesion With the Team</h3>",
checklist("Pre-consult checklist for a painful bone lesion", [
 ("Primary cancer and histology", "(radiosensitive or not; is a biopsy needed?)"),
 ("Pain", "location, type (biologic, mechanical, neuropathic), severity, analgesics, and whether it matches the imaging."),
 ("Neurologic exam", "strength, sensation, reflexes, bladder and bowel function."),
 ("Imaging", "plain films for long bones; CT and MRI for the spine; is there epidural disease or a soft tissue mass?"),
 ("Stability", "SINS for the spine, Mirels for long bones, and any fracture or recent fixation."),
 ("Prognosis", "performance status, sites of disease, and systemic options left."),
 ("Prior radiation", "site, dose, and date; get the old plan."),
 ("Goals and logistics", "what the patient hopes for, travel distance, and hospice involvement."),
]),
"",
"<h3>Uncomplicated Painful Bone Metastases</h3>",
"<p><strong>Uncomplicated</strong> means a painful bone metastasis without impending or completed pathologic fracture, without cord or cauda equina compression, and without prior surgery or radiation to that site. Lesions with any of those features need the workup in the previous reading first.</p>",
"<p>For uncomplicated lesions, single and multiple fractions relieve pain about equally well. What differs is the number of visits, how often retreatment is needed, and short-term side effects.</p>",
figure(bars("Single vs multiple fractions for uncomplicated bone pain", [
  ("Any pain response (pooled randomized trials)", [
   ("8 Gy in 1", 60, "about 60%", "a"),
   ("Multiple fractions", 61, "about 61%", "b")]),
  ("Complete pain relief (pooled randomized trials)", [
   ("8 Gy in 1", 23, "about 23%", "a"),
   ("Multiple fractions", 24, "about 24%", "b")]),
  ("Retreatment to the same site (RTOG 9714)", [
   ("8 Gy in 1", 18, "18%", "a"),
   ("30 Gy in 10", 9, "9%", "b")]),
 ], "Response figures: " + pm(22130630, "Chow et al. 2012") + ", a systematic review of 25 randomized trials (intention-to-treat). Retreatment: " + pm(15928300, "Hartsell et al. 2005") + " (RTOG 9714), which also found less acute toxicity with 8 Gy in 1 (10% vs 17% grade 2-4)."),
 "Bars are drawn to scale from the cited trial data. Retreatment is also more likely after a single fraction partly because clinicians are more willing to retreat after one fraction.",
 "Bar chart comparing single and multiple fraction palliative radiation"),
table(["Regimen", "Visits", "Often chosen when", "Trade-off"], [
 ["<strong>8 Gy in 1</strong>", "1", "Most uncomplicated lesions; poor performance status, short survival, or long travel", "About twice the retreatment rate"],
 ["<strong>20 Gy in 5</strong>", "5", "A middle ground; neuropathic pain; many spine lesions", "More visits, slightly more acute effects"],
 ["<strong>30 Gy in 10</strong>", "10", "Longer expected survival, after surgical fixation, a large soft tissue mass", "Most visits; not better pain relief for uncomplicated lesions"],
]),
big("For an uncomplicated painful bone metastasis, 8 Gy in 1, 20 Gy in 5, and 30 Gy in 10 relieve pain about equally. The single fraction trades fewer visits for more retreatment."),
"<div class='choice-drill' data-drill-set='pal-fx'></div>",
studies(
 ("RTOG 9714", "Breast and prostate cancer bone metastases: 8 Gy in 1 matched 30 Gy in 10 for pain and narcotic relief at 3 months, with less acute toxicity and more retreatment (18% vs 9%)."),
 ("Dutch Bone Metastasis Study", "1,171 patients: 8 Gy in 1 matched 24 Gy in 6 for pain relief; 25% vs 7% were retreated, partly because doctors were more willing to retreat after one fraction."),
),
reveal("Reference: neuropathic pain, retreatment, and the guideline",
 "<ul><li><strong>TROG 96.05</strong> (neuropathic bone pain): 8 Gy in 1 could not be shown to be as good as 20 Gy in 5 (response 53% vs 61%), so many clinicians use 20 Gy in 5 when pain follows a nerve root. A single fraction remains reasonable for short survival (" + pm(26541402, "Roos review") + ").</li>"
 "<li><strong>NCIC SC.20</strong> (re-irradiation): 8 Gy in 1 was noninferior to 20 Gy in 5 or 8 in the intention-to-treat analysis (28% vs 32% response), but not in the per-protocol analysis (45% vs 51%), with less appetite loss and diarrhea.</li>"
 "<li>The " + ASTRO_BONE + " recommends conventional regimens of 8 Gy in 1, 20 Gy in 5, 24 Gy in 6, or 30 Gy in 10, and shared decision-making about which.</li></ul>"),
"",
"<h3>What to Tell the Patient</h3>",
figure(timeline("After palliative bone radiation", [
  ("Pain flare", [(3, 8, "first days", "warn")], []),
  ("Pain relief", [(9, 60, "often starts at 1-2 weeks; most responses by 4-8 weeks", "good")], []),
  ("Retreatment", [(30, 2000, "possible if pain returns, usually after at least 4 weeks", "info")], []),
 ], [(7, "1 wk"), (30, "1 mo"), (90, "3 mo"), (365, "1 yr")],
 "Approximate timing. Pain flare happened in about 35% of patients on placebo in NCIC SC.23."),
 "Schematic timeline on a stretched (logarithmic) time scale; individual patients vary.",
 "Timeline of pain flare, pain relief, and retreatment after palliative bone radiation"),
"<ul>",
"<li><strong>Timing</strong>: keep taking pain medication until relief arrives. A treatment that has not worked at 1 week may still work by 4-8 weeks.</li>",
"<li><strong>Pain flare</strong>: a temporary increase in pain in the first days. In <strong>NCIC SC.23</strong>, dexamethasone 8 mg on the day of radiation and for 4 days after lowered flare from 35% to 26%; a later " + pm(32446951, "Dutch trial") + " found it delayed flare and lowered early pain but did not significantly reduce how often it happened. Many teams offer it, weighing glucose and other steroid effects.</li>",
"<li><strong>Side effects depend on the site</strong>: nausea when the field includes the stomach, diarrhea for the pelvis, painful swallowing for the cervical or upper thoracic spine, and fatigue for most.</li>",
"<li><strong>Retreatment</strong> is possible if pain returns.</li>",
"</ul>",
studies(
 ("NCIC SC.23", "Dexamethasone 8 mg before and for 4 days after palliative bone RT lowered pain flare from 35% to 26% (randomized, placebo-controlled)."),
 ("NCIC SC.20", "Re-irradiation of painful bone metastases: 8 Gy in 1 was noninferior to 20 Gy in 5 or 8 in the intention-to-treat analysis, with fewer side effects; the per-protocol analysis did not confirm noninferiority."),
),
"",
"<h3>When the Goal Is More Than Pain Relief</h3>",
"<h4 class='paradigm-h'>SBRT for Spine and Bone</h4>",
"<p>SBRT gives a much higher dose in 1-5 treatments with tight margins, MRI fusion, immobilization, and daily image guidance. Its main purpose is <strong>durable local control</strong>: a good prognosis, a <strong>radioresistant</strong> tumor (kidney, melanoma, sarcoma), oligometastatic disease, or re-irradiation where the cord has already had its share. The ASTRO guideline conditionally recommends SBRT over conventional RT for symptomatic bone metastases in <strong>selected</strong> patients with good performance status and no need for surgery or neurologic symptoms.</p>",
"<p><strong>Higher dose does not automatically mean better pain relief.</strong> The two big randomized trials point in different directions, and both matter:</p>",
studies(
 ("SC.24", "Painful spine metastases in selected patients: SBRT 24 Gy in 2 gave more complete pain responses at 3 months than 20 Gy in 5 (35% vs 14%)."),
 ("RTOG 0631", "Single-fraction spine SBRT (16-18 Gy) did <strong>not</strong> beat 8 Gy in 1 for pain at 3 months; pain response was actually higher with 8 Gy (61% vs 41%). Fracture and cord toxicity were similar."),
),
"<p>The main risks of spine SBRT are <strong>vertebral compression fracture</strong> (higher with lytic lesions, existing collapse, and very high single doses), pain flare, and rarely radiation myelopathy.</p>",
"",
"<h4 class='paradigm-h'>Prophylactic Radiation for High-Risk Bone Metastases</h4>",
"<p>Most asymptomatic bone metastases are watched. Some, though, are likely to fracture, compress the cord, or become painful soon, and treating them early may prevent a hospitalization.</p>",
studies(
 ("Gillespie (MSKCC, 2024)", "Randomized phase II, 78 patients with <strong>more than 5 metastases</strong> and ECOG 0-2: radiating asymptomatic <strong>high-risk</strong> lesions lowered skeletal-related events at 1 year (1.6% vs 29% of lesions) and hospitalizations for them (0 vs 4 patients). Overall survival was longer, but it was a secondary endpoint the trial was not powered for."),
),
"<p>\"High risk\" in the trial meant bulky lesions (2 cm or more); hip, shoulder, or sacroiliac joint involvement; long-bone lesions involving a third to two-thirds of the cortex; junctional spine (C7-T1, T12-L1, L5-S1); or posterior vertebral element involvement. The trial is promising but small, mostly from one center, unblinded, and limited to polymetastatic disease, and its definition of a skeletal-related event included radiation for pain. A phase III trial is needed before this is a universal standard. The take-home: <strong>a bulky asymptomatic lesion in a weight-bearing or junctional site deserves a conversation</strong>, not automatic observation and not automatic treatment.</p>",
"",
"<h4 class='paradigm-h'>Oligometastases: When Palliation Becomes Ablation</h4>",
"<p>Some patients have only a few metastases. Treating each one with SBRT (usually alongside systemic therapy) may give <strong>durable control and, in selected patients, longer survival</strong>. This is a different goal from symptom relief, and it needs a different patient: good performance status, a controlled primary, and limited disease on modern imaging. The evidence is still mostly phase II, and the benefit depends on the cancer.</p>",
table(["Term", "Meaning"], [
 ["<strong>Oligometastatic</strong>", "Limited metastatic disease, usually up to 3-5 lesions"],
 ["<strong>Oligorecurrent</strong>", "A few new metastases after the primary was treated"],
 ["<strong>Oligoprogressive</strong>", "Most disease is controlled on systemic therapy, but a few sites are growing; treat those and stay on the drug"],
]),
studies(
 ("SABR-COMET", "Controlled primary and up to 5 metastases: adding SABR improved median overall survival (41 vs 28 months) in a randomized phase II trial designed with a relaxed significance threshold; 3 of 66 patients (4.5%) had a treatment-related death."),
 ("ORIOLE", "Oligorecurrent prostate cancer (up to 3 lesions): SBRT lowered progression at 6 months compared with observation (19% vs 61%); treating all PSMA PET-avid disease lowered the risk of new lesions."),
 ("NRG-BR002", "Oligometastatic breast cancer: adding ablation (mostly SBRT) to first-line systemic therapy did not improve progression-free or overall survival, a reminder that the benefit is not universal."),
),
reveal("Reference: other oligometastasis trials",
 "<ul><li><strong>Gomez</strong>: NSCLC with up to 3 metastases that did not progress on first-line systemic therapy; local consolidative therapy improved progression-free and overall survival (randomized phase II, stopped early).</li>"
 "<li><strong>STOMP</strong>: metastasis-directed therapy for oligorecurrent prostate cancer lengthened androgen deprivation-free survival (21 vs 13 months; randomized phase II).</li>"
 "<li><strong>CURB</strong>: SBRT for oligoprogressive disease improved progression-free survival in NSCLC but not in breast cancer.</li>"
 "<li>Larger phase III trials (SABR-COMET-3 and -10 and others) are testing these results.</li></ul>"),
"",
"<h4 class='paradigm-h'>Other Palliative Targets</h4>",
table(["Problem", "How radiation helps", "Representative regimens"], [
 ["<strong>Bleeding</strong> (bladder, cervix, rectum, lung, skin, stomach)", "Hemostatic RT often slows bleeding over days, alongside transfusion, endoscopy, or embolization", "8 Gy in 1 (sometimes repeated), 20 Gy in 5, 30 Gy in 10"],
 ["<strong>Airway obstruction or hemoptysis</strong>", "Shrinks the tumor; bronchoscopic debulking or a stent is faster if the airway is critical", "17 Gy in 2 (a week apart), 20 Gy in 5, 30 Gy in 10; 10 Gy in 1 for poor performance status"],
 ["<strong>Dysphagia</strong> (esophagus)", "A stent relieves faster; radiation or brachytherapy can be more durable", "20 Gy in 5, 30 Gy in 10"],
 ["<strong>Head and neck</strong> mass", "Pain, bleeding, airway, and fungating tumor", "<strong>Quad shot</strong>: 14.8 Gy in 4 fractions over 2 days (twice daily), repeated about every 4 weeks up to 3 times"],
 ["<strong>Liver capsule pain</strong>", "Low-dose whole-liver RT", "For example 8 Gy in 1"],
 ["<strong>Brain metastases</strong>", "SRS, whole-brain RT, or supportive care", "See the CNS module"],
]),
"",
"<h3>Systemic and Radiopharmaceutical Options</h3>",
"<p>When pain is everywhere, or a cancer has a targeted radiopharmaceutical, a drug that carries radiation to every lesion can do what external beam cannot. These are usually decided with medical oncology and nuclear medicine.</p>",
table(["Agent", "Use", "Know"], [
 ["<strong>Radium-223</strong> (alpha emitter, behaves like calcium)", "Castration-resistant prostate cancer with symptomatic bone metastases and <strong>no visceral metastases</strong>", "<strong>ALSYMPCA</strong>: improved overall survival (median 14.9 vs 11.3 months), not just pain"],
 ["<strong>Lutetium-177 PSMA-617</strong>", "PSMA-positive metastatic castration-resistant prostate cancer after androgen receptor pathway therapy and taxane chemotherapy", "<strong>VISION</strong>: improved overall survival"],
 ["<strong>Lutetium-177 dotatate</strong>", "Somatostatin receptor-positive midgut neuroendocrine tumors", "<strong>NETTER-1</strong>: improved progression-free survival"],
 ["<strong>Strontium-89, samarium-153</strong> (beta emitters)", "Diffuse bone pain", "Pain relief only; lower blood counts"],
]),
"",
"<h3>End of Life</h3>",
"<ul>",
"<li>Starting radiation in the last weeks of life is common and often more burden than benefit. If expected survival is short, consider <strong>one fraction or none</strong>, and involve palliative care and hospice.</li>",
"<li>A short course should not delay hospice enrollment; many hospices can coordinate a single palliative fraction.</li>",
"<li>The most useful question in the room is often <strong>\"What are you hoping this treatment will do for you?\"</strong></li>",
"</ul>",
quiz("Choose the Course", [
 ("An 84-year-old with metastatic lung cancer, ECOG 3, lives 2 hours away and has a painful rib metastasis. Regimen?", "<strong>8 Gy in 1.</strong> Same pain relief as longer courses, one trip. Retreatment is possible if needed."),
 ("A 52-year-old with ER-positive breast cancer and bone-only disease had a femur rod placed yesterday for an impending fracture. Regimen?", "<strong>A multifraction course</strong> (for example 20 Gy in 5 or 30 Gy in 10) covering the <strong>hardware</strong> once the wound allows. Her prognosis may be years, and postoperative RT is recommended after surgery for non-spine bone metastases (ASTRO)."),
 ("A 60-year-old with renal cell carcinoma, a controlled primary, and a single painful T9 metastasis without epidural compression, KPS 90. What do you consider?", "<strong>Spine SBRT.</strong> Renal cell is radioresistant to conventional doses, and his prognosis justifies durable local control. SINS and the Bilsky grade still need to be checked."),
 ("Three months after 8 Gy in 1 to a painful hip metastasis, the pain is back. Can you retreat?", "<strong>Yes.</strong> Re-irradiation is common after a single fraction; 8 Gy in 1 again is one option (SC.20). First make sure the pain is not from a new fracture."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
EMERGENCIES = "\n".join([
"<p>True radiation oncology emergencies are few, but you will be paged about them. For each one, ask: <strong>what has to happen first, who else needs to be involved, and where does radiation fit?</strong> Radiation is rarely the first step, and its benefit takes time.</p>",
table(["Situation", "Do first", "Where radiation fits", "How fast radiation helps"], [
 ["<strong>Metastatic spinal cord compression</strong>", "Dexamethasone, whole-spine MRI, spine surgery review", "Definitive treatment for many; after surgery for others", "Starts within days; aims to preserve function more than restore it"],
 ["<strong>Superior vena cava syndrome</strong>", "Airway, then a <strong>tissue diagnosis</strong>; stent if severe", "After diagnosis, for selected tumors", "Usually 1-2 weeks or more; a stent is faster"],
 ["<strong>Life-threatening bleeding</strong>", "Resuscitation; endoscopy, embolization, or packing", "When those fail, are not possible, or alongside them", "Often days"],
 ["<strong>Airway obstruction</strong>", "Bronchoscopy (debulking or stent) if critical", "For durable relief after or instead of a procedure", "Days to weeks"],
 ["<strong>Impending pathologic fracture</strong>", "Protect weight bearing; orthopedics", "Postoperative RT after fixation, or RT alone if surgery is not appropriate", "Not an immediate fix"],
 ["<strong>Symptomatic brain metastases</strong>", "Steroids; neurosurgery for mass effect", "SRS or whole-brain RT (see CNS)", "Days to weeks"],
]),
big("Before you radiate an emergency, ask what has to happen first: steroids, a scan, a surgeon, a stent, resuscitation, or a biopsy."),
"",
"<h3 class='paradigm-h'>Metastatic Spinal Cord Compression</h3>",
"<p>Cord compression affects a few percent of patients with cancer, most often from <strong>lung, breast, or prostate cancer</strong>, then myeloma, lymphoma, and kidney cancer. Most cases are in the <strong>thoracic spine</strong>.</p>",
"<h4>Recognize It</h4>",
"<ul>",
"<li><strong>Back pain</strong> is the first symptom in almost everyone, often for weeks before weakness. New or worsening back pain in a patient with cancer deserves a careful neurologic exam and a low threshold for MRI.</li>",
"<li>Then <strong>weakness</strong>, a <strong>sensory level</strong>, and finally <strong>bladder or bowel dysfunction</strong> (a late sign).</li>",
"<li><strong>Ambulatory status before treatment is the strongest predictor of walking afterward.</strong> Patients who walk in usually walk out; patients paralyzed for more than a day or two rarely recover.</li>",
"</ul>",
figure(dpath("Suspected cord compression: what happens first", [
  ("Cancer (known or possible) plus back pain and a neurologic symptom or sign", [
   ("Now", "<strong>Dexamethasone</strong> (commonly 16 mg a day, often after a 10 mg IV load) and an urgent spine team or MSCC coordinator call. If lymphoma is possible and the patient is neurologically stable, discuss steroids with the team, because they can make a biopsy nondiagnostic.", "stop"),
   ("Then", "<strong>MRI of the whole spine</strong> as soon as possible (NICE: within 24 hours). CT myelogram if MRI is impossible.", "go")]),
  ("Is there a tissue diagnosis?", [
   ("Yes", "Continue down the pathway.", "go"),
   ("No", "A biopsy may be needed, often of the most accessible lesion. It should not delay decompression in a patient who is getting worse.", "alt")]),
  ("Could surgery help, and could the patient tolerate it?", [
   ("Often yes", "Single area of compression, high-grade (Bilsky 2-3) disease from a tumor that is not highly radiosensitive, mechanical instability, reasonable prognosis, and not paraplegic for long: <strong>decompression and stabilization, then RT</strong>.", "go"),
   ("Often no", "Radiosensitive tumor, many levels, short prognosis, poor fitness, or prolonged paraplegia: <strong>urgent radiation</strong> with steroids.", "alt")]),
  ("Which radiation?", [
   ("Short prognosis", "8 Gy in 1 or 20 Gy in 5 (SCORAD III, ICORG 05-03).", "go"),
   ("Longer prognosis", "Multifraction courses (for example 30 Gy in 10), or SBRT at experienced centers for selected radioresistant tumors after decompression or with low-grade compression.", "go")]),
 ]),
 "Simplified teaching pathway based on " + NICE_MSCC + ", the " + ASTRO_BONE + ", and the trials below. Local MSCC pathways differ; follow the spine team and your institution.",
 "Decision pathway for suspected metastatic spinal cord compression"),
studies(
 ("Patchell (2005)", "Selected patients with compression from one area of a non-radiosensitive tumor: direct decompressive surgery then RT kept more patients walking (84% vs 57%) and for longer (median 122 vs 13 days) than RT alone."),
 ("SCORAD III", "Patients with a limited prognosis: at 8 weeks, 69% walked after 8 Gy in 1 vs 73% after 20 Gy in 5. Noninferiority was not formally met at 8 weeks, but was at 1, 4, and 12 weeks."),
 ("ICORG 05-03", "Patients not having surgery: a single 10 Gy fraction was noninferior to 20 Gy in 5 for preserving mobility."),
),
reveal("Reference: more on cord compression",
 "<ul><li><strong>Patchell</strong> excluded radiosensitive tumors (lymphoma, leukemia, myeloma, germ cell tumors) and patients paraplegic for more than 48 hours, and was stopped early for benefit.</li>"
 "<li>The " + ASTRO_BONE + " conditionally recommends surgery plus postoperative RT over RT alone for cord or cauda equina compression, recommends dexamethasone, and lists 8 Gy in 1, 16 Gy in 2, 20 Gy in 5, or 30 Gy in 10 for patients who are not having surgery.</li>"
 "<li>Retrospective series (Rades) suggest longer courses give better <strong>local control</strong>, which matters for patients expected to live longer.</li>"
 "<li><strong>Fields</strong>: conventional RT usually covers the involved vertebrae plus about one vertebral body above and below, and any paraspinal mass. After surgery, the field covers the operated levels and the hardware.</li></ul>"),
"",
"<h3 class='paradigm-h'>Superior Vena Cava Syndrome</h3>",
"<p>Tumor (or a clot) blocks blood returning from the head and arms. Most malignant cases are from <strong>lung cancer</strong> (especially small cell) and <strong>lymphoma</strong>; a growing share of all cases are from <strong>catheter- or device-related thrombosis</strong>.</p>",
"<ul>",
"<li><strong>Symptoms</strong>: swelling of the face, neck, and arms, distended chest wall veins, shortness of breath, cough, and headache, all worse when lying flat or bending over.</li>",
"<li><strong>Most patients are not in immediate danger</strong>, because collateral veins develop over weeks. The true emergencies are <strong>stridor or laryngeal edema</strong> and <strong>confusion or reduced consciousness from cerebral edema</strong>.</li>",
"</ul>",
figure(dpath("SVC syndrome: the order of steps", [
  ("Stridor, airway compromise, or confusion?", [
   ("Yes", "Secure the airway; urgent <strong>endovascular stenting</strong>, which relieves symptoms within hours to a couple of days.", "stop"),
   ("No", "There is usually time to make a diagnosis.", "go")]),
  ("Is there a tissue diagnosis?", [
   ("No", "<strong>Biopsy first.</strong> Radiating before a biopsy can make the pathology unreadable.", "stop"),
   ("Yes", "Treat the cancer.", "go")]),
  ("What is the cancer?", [
   ("Chemosensitive", "Small cell lung cancer, lymphoma, germ cell tumor: <strong>systemic therapy</strong> first, with radiation as part of the plan where indicated.", "alt"),
   ("Other", "Non-small cell lung cancer and others: <strong>radiation</strong> (often with systemic therapy), or a stent if symptoms are severe or recur.", "go")]),
 ]),
 "Simplified teaching pathway. Anticoagulation for thrombus, the patient's prognosis, and goals of care also shape the plan.",
 "Decision pathway for superior vena cava syndrome"),
"",
"<h3 class='paradigm-h'>Bleeding, Airway, and Fracture</h3>",
figure(dpath("Bleeding or airway: radiation fits alongside other care", [
  ("Is the patient unstable (hemorrhage, hypoxia, critical airway)?", [
   ("Yes", "<strong>Resuscitate</strong>: transfusion, reversal of anticoagulation, and the fastest procedure available (endoscopy, embolization, bronchoscopy, packing, stent).", "stop"),
   ("No", "Plan radiation with the procedural team; it may come first, after, or instead.", "go")]),
  ("What does radiation add?", [
   ("Durability", "Hemostatic RT (for example 8 Gy in 1 or 20 Gy in 5) often slows bleeding over days and lowers recurrence after a procedure.", "go"),
   ("Time to effect", "Radiation is rarely the fastest fix. Benefit can take days (bleeding) to weeks (airway or obstruction).", "alt")]),
 ]),
 "Simplified teaching pathway; the sequence depends on the site, the severity, and local expertise.",
 "Decision pathway for bleeding and airway obstruction"),
cards(
 ("Fracture", "A completed or impending long-bone fracture needs <strong>orthopedic fixation</strong> when the patient can tolerate it. Postoperative RT is recommended after surgery for non-spine bone metastases (ASTRO) and usually covers the hardware."),
 ("Radiation alone", "When surgery is not appropriate, radiation can still relieve pain, but it does not stabilize a broken bone."),
),
quiz("Triage the Page", [
 ("A woman with breast cancer has had back pain for 3 weeks and now trips on stairs. Exam shows mild leg weakness and brisk reflexes. First two orders?", "<strong>Dexamethasone</strong> and <strong>MRI of the whole spine</strong>, now, plus a call to the spine team."),
 ("A man with lung cancer has face and arm swelling for 2 weeks. He is breathing comfortably and is alert. CT shows a mediastinal mass. No biopsy yet. Radiate tonight?", "<strong>No.</strong> He is stable, so get <strong>tissue first</strong>. If it is small cell or lymphoma, systemic therapy is the main treatment. A stent is the fast fix if he worsens."),
 ("A 55-year-old with renal cell carcinoma has single-level T7 compression (Bilsky 3), has been weak for 12 hours, and can still walk with help. Best approach?", "<strong>Surgical decompression and stabilization, then RT</strong> (Patchell, NOMS). Renal cell is radioresistant, and he is a reasonable candidate."),
 ("A patient with myeloma has cord compression at T10 and can walk. Surgery or radiation?", "Usually <strong>radiation</strong>. Myeloma is highly radiosensitive, so surgery is reserved for instability or bone fragments in the canal."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
BENIGN = "\n".join([
"<p>Benign disease radiation covers a wide range of doses and a wide range of evidence. Some indications are supported by randomized trials; others rest on long experience and observational series; a few are genuinely contested. The skill is knowing <strong>which condition, at what stage, after which other treatments</strong>, and how to talk honestly about the evidence and the small lifetime cancer risk.</p>",
figure(table(["Condition", "Goal", "Representative regimen", "Evidence in brief", "Main alternatives"], [
 ["<strong>Heterotopic ossification</strong> (high-risk hip surgery)", "Prevent bone forming in soft tissue", "7-8 Gy in 1, within about 24 hours before or 72 hours after surgery", ev("strong", "Randomized trials and meta-analysis"), "NSAIDs (indomethacin)"],
 ["<strong>Keloid</strong> (after excision)", "Prevent regrowth", "Regimens vary, for example 12-16 Gy in 3-4 fractions, starting within about 1-2 days", ev("mod", "Large observational series and meta-analysis"), "Steroid injection, pressure, silicone"],
 ["<strong>Gynecomastia</strong> (prevention on bicalutamide alone)", "Prevent painful breast growth", "A single 10-12 Gy with electrons, before the drug starts", ev("mod", "Randomized trials; tamoxifen worked better"), "Tamoxifen"],
 ["<strong>Dupuytren / Ledderhose</strong> (early, no contracture)", "Slow progression", "About 30 Gy as 2 courses of 5 x 3 Gy, 6-12 weeks apart, or 21 Gy in 7", ev("lim", "Limited: no untreated control group"), "Observation; procedures once contracture develops"],
 ["<strong>Plantar fasciitis</strong>", "Pain relief", "0.5-1 Gy per fraction, 3-6 Gy total", ev("lim", "Dose-comparison trials, no sham control"), "Stretching, orthotics, injections"],
 ["<strong>Osteoarthritis</strong> (knee, hand)", "Pain relief", "0.5-1 Gy per fraction, 3-6 Gy total", ev("con", "Contested: sham-controlled trials negative"), "Exercise, weight loss, analgesics, injections, joint replacement"],
 ["<strong>Graves orbitopathy</strong> (active, moderate-to-severe)", "Reduce orbital inflammation", "About 20 Gy in 10, or lower-dose schedules", ev("mod", "Mixed trials; second-line with steroids"), "IV steroids with mycophenolate, teprotumumab, others"],
 ["<strong>Pterygium</strong> (after excision)", "Prevent regrowth", "Single beta-ray dose (for example 10 Gy) after surgery", ev("mod", "Randomized trial support"), "Conjunctival autograft, mitomycin C"],
 ["<strong>Desmoid tumor</strong> (progressive, unresectable)", "Control a locally aggressive tumor", "About 50-56 Gy in 25-28 fractions", ev("mod", "Phase II and retrospective data"), "Active surveillance, systemic therapy, surgery"],
]), "Evidence labels are a plain-language summary of the studies cited in this reading, not a formal grading. Representative regimens vary by institution.",
 "Benign radiation indications compared by goal, regimen, evidence, and alternatives"),
big("Benign radiation is not one thing. Each indication has its own goal, its own dose, and its own quality of evidence, and every consent talk covers the long-term risk."),
"",
"<h3>Long-Term Risk and Consent</h3>",
cards(
 ("Age", "The lifetime risk of a radiation-induced cancer falls with age, so inflammatory and cosmetic indications are usually reserved for older adults. Be especially cautious in children and younger adults."),
 ("Location", "Keep the thyroid, breast, eyes, and gonads out of the field whenever possible. Hands and feet carry little marrow or organ dose."),
 ("Alternatives and uncertainty", "Explain what else could be done, how strong the evidence is for this condition, and what happens without treatment. Document the conversation."),
),
"",
"<h3 class='paradigm-h'>Heterotopic Ossification</h3>",
"<p>Heterotopic ossification (HO) is <strong>bone that forms in soft tissue</strong>, most often around the hip after arthroplasty or acetabular fracture surgery, and around the elbow. It can cause pain and stiffness and sometimes needs another operation.</p>",
"<ul>",
"<li><strong>Highest risk</strong>: <strong>prior HO</strong> (the strongest predictor), ankylosing spondylitis, diffuse idiopathic skeletal hyperostosis (DISH), hypertrophic osteoarthritis, and male sex.</li>",
"<li><strong>Why timing is everything</strong>: radiation acts on precursor cells before they become bone-forming cells, early around the time of surgery. Once bone has formed, radiation cannot remove it.</li>",
"<li><strong>Regimen</strong>: a single <strong>7-8 Gy</strong> within about <strong>24 hours before</strong> or <strong>72 hours after</strong> surgery. In a " + pm(15465207, "meta-analysis of randomized trials") + ", radiation was modestly more effective than NSAIDs at preventing severe (Brooker 3-4) HO, the absolute difference was small, and postoperative doses below about 7 Gy worked no better than NSAIDs.</li>",
"<li><strong>Shielding porous implants</strong>: some centers block uncemented, porous-coated components from the field to protect bone ingrowth; others do not. A " + pm(35133992, "2022 series") + " found unshielded low-dose preoperative RT did not increase loosening of porous implants. Follow the institutional approach with the orthopedic surgeon.</li>",
"<li><strong>Alternative</strong>: NSAIDs such as indomethacin, which carry GI bleeding and kidney risks and need several days to weeks of dosing.</li>",
"</ul>",
"",
"<h3 class='paradigm-h'>Keloids</h3>",
"<ul>",
"<li>Keloids are scars that grow beyond the original wound. Excision alone often fails, sometimes with a larger keloid.</li>",
"<li><strong>Postoperative RT</strong>, usually started within about a day or two of excision, lowers recurrence. In a " + pm(28177974, "meta-analysis of 72 studies") + ", recurrence averaged about 22% with surgery plus RT, versus 37% with RT alone; chest keloids recurred most.</li>",
"<li>Electrons, superficial X-rays, or brachytherapy to the scar with a small margin. Regimens vary widely (for example 12-16 Gy in 3-4 fractions), with higher doses sometimes used at high-tension sites such as the chest and shoulder.</li>",
"<li>Side effects are mostly pigment changes. Avoid in children when possible, and discuss the small long-term cancer risk, especially near the breast or thyroid.</li>",
"</ul>",
"",
"<h3 class='paradigm-h'>Gynecomastia Prevention</h3>",
"<p>Men with prostate cancer who take an <strong>antiandrogen alone</strong> (for example high-dose bicalutamide, now uncommon) often develop painful breast enlargement. A single low dose to each breast bud <strong>before</strong> starting the drug reduces it: in a " + pm(15380582, "sham-controlled trial") + ", 10 Gy cut gynecomastia from 85% to 52%. In a " + pm(15863377, "head-to-head trial") + ", <strong>tamoxifen</strong> prevented it more effectively than 12 Gy of radiation (8% vs 34%, compared with 69% with no prevention), so radiation is mainly for men who cannot take tamoxifen. Treatment after the breast has grown works poorly.</p>",
"",
"<h3 class='paradigm-h'>Dupuytren and Ledderhose Disease</h3>",
"<p>Dupuytren disease is a fibroproliferative disorder of the palmar fascia: first <strong>nodules</strong>, then <strong>cords</strong>, then <strong>flexion contracture</strong> of the fingers (ring and little fingers most often). Ledderhose disease is the same process in the sole of the foot.</p>",
compare(
 ("Early: nodules and cords, little or no contracture", "Radiation may slow progression", "Radiation targets proliferating fibroblasts. In a " + pm(11172962, "randomized comparison of two schedules") + ", about 90% of treated hands were stable or improved at 1 year, but there was no untreated control group."),
 ("Late: established contracture", "Procedures", "Needle aponeurotomy, collagenase (where available), or surgery straighten the finger. Radiation cannot reverse a mature contracture."),
),
"<ul>",
"<li><strong>How good is the evidence?</strong> Modest. " + NICE_DUP + " judged the efficacy evidence inadequate, partly because early Dupuytren disease does not always progress on its own, and recommends radiation only with special arrangements for consent and audit.</li>",
"<li><strong>Technique</strong>: low-energy X-rays (orthovoltage) or electrons to the nodules and cords with a margin of about 1-2 cm, the rest of the hand shielded.</li>",
"<li><strong>Regimen</strong>: about 30 Gy in two courses of 5 x 3 Gy separated by 6-12 weeks, or 21 Gy in 7 fractions.</li>",
"<li><strong>Side effects</strong>: dry skin and mild redness acutely; late dryness, thinning, or altered sensation in a small minority.</li>",
"</ul>",
pearl("The key word for Dupuytren radiation is <strong>early</strong>: a patient who can still lay the hand flat on a table (a negative tabletop test). Even then, describe the benefit as possible slowing of progression, not a guarantee."),
"",
"<h3 class='paradigm-h'>Osteoarthritis and Plantar Fasciitis</h3>",
"<ul>",
"<li><strong>Who</strong>: older adults with chronic joint or heel pain that has not responded to exercise, analgesics, injections, physical therapy, orthotics, or weight loss, or who are poor surgical candidates.</li>",
"<li><strong>How</strong>: very low doses, often 0.5-1 Gy two to three times a week, 3-6 Gy total, sometimes repeated after 6-12 weeks.</li>",
"<li><strong>Side effects</strong>: essentially none acutely at these doses.</li>",
"</ul>",
studies(
 ("Mahler (osteoarthritis sham trials)", "Two Dutch randomized trials, knee and hand osteoarthritis: 6 x 1 Gy was no better than sham radiation for pain or function, at 3 months or at 12 months. The placebo effect in joint pain is large."),
 ("Niewald", "Plantar fasciitis: 6 x 1 Gy relieved heel pain better than a very low 6 x 0.1 Gy control. There was no sham arm, and a later trial found 0.5 Gy and 1 Gy per fraction equivalent."),
),
"<p>If asked, say that low-dose RT for osteoarthritis is <strong>contested</strong>: German and other European centers use it widely, but the only sham-controlled trials were negative, and they were small. For plantar fasciitis the randomized data compare doses rather than radiation with no radiation. Either way, it is an option only after conservative care fails, with an honest discussion of uncertain benefit and small long-term risk.</p>",
"",
"<h3>Other Benign Conditions You May Hear About</h3>",
table(["Condition", "Where radiation fits"], [
 ["<strong>Graves orbitopathy</strong>", "The " + EUGOGO + " lists orbital RT, combined with steroids, as a <strong>second-line</strong> option for active moderate-to-severe disease. Avoid in diabetic retinopathy and be cautious in younger patients; newer drugs such as teprotumumab have changed practice."],
 ["<strong>Pterygium</strong>", "A single beta-ray dose after excision lowered recurrence in a " + pm(22284040, "randomized trial") + ". Higher doses can thin the sclera; many surgeons use autografts or mitomycin C instead."],
 ["<strong>Desmoid tumor</strong>", "Active surveillance or systemic therapy first; RT (about 50-56 Gy) for progressive or symptomatic disease when surgery would be morbid. Response is slow, sometimes over years (" + pm(23868907, "EORTC 62991") + ")."],
 ["<strong>Epicondylitis, shoulder syndromes</strong>", "Low-dose anti-inflammatory RT, similar to osteoarthritis, with similar uncertainty"],
 ["<strong>Benign tumors</strong> (meningioma, vestibular schwannoma, pituitary adenoma, paraganglioma)", "Fractionated RT or SRS at tumor-control doses; see the CNS module"],
]),
quiz("Benign or Not Now?", [
 ("A 70-year-old has painful nodules in both palms and can still lay her hands flat. Radiation?", "<strong>It is an option.</strong> Early Dupuytren disease: about 30 Gy in two split courses may slow progression. Explain that the evidence is limited and early disease does not always progress."),
 ("A 64-year-old has a ring finger fixed at 60 degrees of flexion from a thick cord. Radiation?", "<strong>No.</strong> RT cannot reverse an established contracture. Refer for needle aponeurotomy, collagenase, or surgery."),
 ("A man who developed HO after his left hip replacement is scheduled for a right hip replacement next week. What do you offer, and when?", "<strong>A single 7-8 Gy</strong> within about 24 hours before or 72 hours after surgery, or NSAID prophylaxis. Prior HO is the strongest risk factor."),
 ("A 35-year-old asks for radiation for knee osteoarthritis. What do you weigh?", "<strong>Her age and the evidence.</strong> The lifetime cancer risk is higher in younger patients, and sham-controlled trials were negative. Other treatment is preferred."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
SRS = "\n".join([
"<p>Radiosurgery is not only for tumors. Two non-cancer brain conditions come up again and again: <strong>trigeminal neuralgia</strong> and <strong>arteriovenous malformations (AVMs)</strong>. Both use a single, very precise, very high dose, and in both the benefit is <strong>delayed</strong>, on very different time scales.</p>",
compare(
 ("Trigeminal neuralgia", "Target: a nerve", "A tiny spot on the trigeminal nerve root gets about 70-90 Gy maximum dose. Pain relief usually takes weeks."),
 ("AVM", "Target: a tangle of vessels", "The whole nidus gets about 16-25 Gy at its edge. The vessels close over 1-3 years or more."),
),
figure(timeline("When does radiosurgery work?", [
  ("Trigeminal neuralgia", [(7, 120, "pain relief, median about 1 month", "good")],
   [(240, "numbness, median about 8 months"), (1330, "about 4 in 10 have pain return, median about 3.5 years")]),
  ("AVM bleeding risk", [(3, 1095, "latency: risk lower than before treatment but not gone", "warn")], []),
  ("AVM closure", [(365, 1460, "complete obliteration usually at 1-3 years", "good")],
   [(1095, "angiogram to confirm, around 3 years")]),
 ], [(7, "1 wk"), (30, "1 mo"), (90, "3 mo"), (365, "1 yr"), (1095, "3 yr"), (1825, "5 yr")],
 "Trigeminal neuralgia figures from an " + pm(38364220, "871-patient multicenter Gamma Knife series (2024)") + "; AVM latency risk from " + pm(15647577, "Maruyama et al. 2005") + "."),
 "Schematic timeline on a stretched (logarithmic) time scale. Individual patients vary widely.",
 "Timeline comparing trigeminal neuralgia and AVM response to radiosurgery"),
big("In functional and vascular radiosurgery, the effect is delayed. Pain relief takes weeks; AVM closure takes years, and the patient is not fully protected until it happens."),
"",
"<h3 class='paradigm-h'>Trigeminal Neuralgia</h3>",
"<h4>Recognize It</h4>",
"<ul>",
"<li><strong>Brief, electric shock-like, one-sided facial pain</strong> lasting seconds, usually in the <strong>V2 or V3</strong> distribution (cheek, jaw).</li>",
"<li>Triggered by <strong>light touch, chewing, talking, brushing teeth, or wind</strong>. Between attacks the patient is usually pain free and the neurologic exam is normal.</li>",
"<li>Most patients are over 50 and more are women. In a <strong>young patient, with bilateral symptoms, or with sensory loss, think of a secondary cause such as multiple sclerosis or a tumor</strong>.</li>",
"<li>The usual cause is <strong>a blood vessel</strong> (most often the superior cerebellar artery) pressing on the nerve near where it enters the pons.</li>",
"</ul>",
"<h4>Workup and First-Line Treatment</h4>",
"<ul>",
"<li><strong>MRI</strong> with thin-slice sequences to exclude a tumor or MS and to look for a compressing vessel.</li>",
"<li><strong>Carbamazepine</strong> (or oxcarbazepine) is first-line and works for most patients at first. Procedures are for pain that drugs no longer control or side effects the patient cannot tolerate.</li>",
"</ul>",
table(["Procedure", "Often best for", "Trade-off"], [
 ["<strong>Microvascular decompression</strong>", "Healthier patients with a compressing vessel", "Most durable relief, but a craniotomy"],
 ["<strong>Percutaneous rhizotomy</strong> (glycerol, balloon, radiofrequency)", "Patients who need immediate relief", "Quick, but numbness and recurrence are common"],
 ["<strong>Stereotactic radiosurgery</strong>", "Older or medically frail patients, those on anticoagulants, or after other procedures fail", "Noninvasive, but relief is delayed and recurrence is common over years"],
]),
"<h4>Radiosurgery Details</h4>",
"<ul>",
"<li><strong>Target</strong>: the trigeminal nerve root in the cistern with a single small (4 mm) shot. Centers differ on how close to the pons they aim; a target farther from the brainstem tends to give more relief and more numbness.</li>",
"<li><strong>Dose</strong>: a <strong>maximum dose of about 70-90 Gy</strong> (median 80 Gy in a large series) in one session, prescribed to the center of the tiny target, not to an edge.</li>",
"<li><strong>Response</strong>: in the large multicenter series, about 80% had initial relief at a median of about a month; about 4 in 10 of them later had pain return (median about 3.5 years). Repeat SRS is possible.</li>",
"<li><strong>Main side effect</strong>: new <strong>facial numbness</strong> in roughly a quarter of patients, appearing months later. Severe painful numbness (anesthesia dolorosa) is rare.</li>",
"</ul>",
reveal("Reference: Barrow Neurological Institute (BNI) pain score",
 "<p>Outcomes are reported on the BNI scale: <strong>I</strong> no pain, no medication; <strong>II</strong> occasional pain, no medication; <strong>IIIa</strong> no pain on medication; <strong>IIIb</strong> some pain, adequately controlled on medication; <strong>IV</strong> some pain, not adequately controlled; <strong>V</strong> severe pain, no relief. \"Success\" is usually BNI I-IIIa or I-IIIb, depending on the study.</p>"),
"",
"<h3 class='paradigm-h'>Arteriovenous Malformations</h3>",
"<p>An AVM is a tangle of abnormal vessels (the <strong>nidus</strong>) where arteries connect directly to veins without capillaries in between. The high-pressure flow can rupture.</p>",
"<h4>Recognize It</h4>",
"<ul>",
"<li><strong>Hemorrhage</strong> is the most common presentation, usually in a young adult; then <strong>seizures</strong>, headache, or a focal deficit. Many are found by chance on MRI.</li>",
"<li>The risk of bleeding is roughly <strong>2-4% per year</strong> on average, higher after a prior bleed and with deep location, deep venous drainage, or an associated aneurysm.</li>",
"<li><strong>Catheter angiography</strong> is the gold standard to map the feeding arteries, nidus, and draining veins.</li>",
"</ul>",
"<h4>Spetzler-Martin Grade</h4>",
table(["Feature", "Points"], [
 ["<strong>Size</strong>: under 3 cm / 3-6 cm / over 6 cm", "1 / 2 / 3"],
 ["<strong>Eloquent brain</strong> nearby (motor, sensory, language, visual cortex, thalamus, hypothalamus, brainstem): no / yes", "0 / 1"],
 ["<strong>Venous drainage</strong>: superficial only / any deep", "0 / 1"],
]),
"<p>The " + pm(3760956, "Spetzler-Martin grade") + " (I-V) estimates <strong>surgical</strong> risk. In general, low grades (I-II) often go to <strong>surgery</strong>, which closes the AVM immediately; <strong>small AVMs in deep or eloquent locations</strong> are the classic <strong>radiosurgery</strong> patients; grade III needs individual judgment; and high grades (IV-V) are often observed. The grade is a starting point, not a decision: <strong>rupture history, age, anatomy (aneurysms, venous drainage), and the risk of each option</strong> are weighed by a multidisciplinary team of neurosurgery, neurointerventional radiology, and radiation oncology.</p>",
"<h4>Radiosurgery Details</h4>",
"<ul>",
"<li><strong>Who</strong>: usually small AVMs (often under about 3 cm, or about 10 cc) in deep or eloquent brain.</li>",
"<li><strong>Dose</strong>: about <strong>16-25 Gy</strong> to the edge of the nidus in one session. Higher doses close more AVMs but cause more injury to the surrounding brain.</li>",
"<li><strong>How it works</strong>: radiation injures the vessel lining, which slowly thickens until the vessels close. <strong>Complete obliteration usually takes 1-3 years</strong> and occurs in roughly 70-80% of small AVMs.</li>",
"<li><strong>The latency period</strong>: in a " + pm(15647577, "large series") + ", bleeding risk fell by about half after radiosurgery even before obliteration, and fell much further after obliteration, but was not zero in either period. Patients need to understand this.</li>",
"<li><strong>Follow-up</strong>: MRI every 6-12 months, then <strong>angiography</strong> to confirm obliteration, usually around 3 years.</li>",
"<li><strong>Side effects</strong>: imaging changes around the treated area are common; symptomatic swelling, seizures, or late cysts occur in a minority.</li>",
"</ul>",
studies(
 ("ARUBA", "<strong>Unruptured</strong> brain AVMs: the trial was stopped early when medical management alone had fewer deaths or strokes than medical management plus intervention (10% vs 31%, mean follow-up about 33 months)."),
),
"<p>ARUBA is widely debated: follow-up was short compared with a young patient's lifetime risk, interventions were mixed (embolization, surgery, radiosurgery), relatively few patients had surgery, and selection may not reflect experienced centers. It made <strong>observation a real option</strong> for unruptured AVMs; it did not settle the question for every patient.</p>",
pearl("Ruptured AVMs are usually treated, because the risk of bleeding again is highest early. For unruptured AVMs, the decision weighs a long lifetime of small annual risk (higher in young patients) against the immediate risk of treatment."),
"",
"<h3>Other Functional Radiosurgery</h3>",
"<ul>",
"<li><strong>Essential tremor</strong> and tremor-dominant Parkinson disease: Gamma Knife <strong>thalamotomy</strong> (a very high single dose to the ventral intermediate nucleus) for patients who cannot have deep brain stimulation or focused ultrasound. The effect is delayed by months.</li>",
"<li><strong>Cardiac radioablation</strong> for refractory ventricular tachycardia (a single 25 Gy to the arrhythmia substrate) is an emerging, investigational use.</li>",
"</ul>",
quiz("Radiosurgery Check", [
 ("A 72-year-old on warfarin has electric shock-like right jaw pain when she chews. Carbamazepine now makes her too drowsy. MRI shows no tumor. Which procedure fits her best?", "<strong>Stereotactic radiosurgery</strong> is a good fit: noninvasive, no need to stop anticoagulation, and suited to an older patient. Relief takes weeks."),
 ("What is the main side effect to counsel her about?", "<strong>New facial numbness</strong>, in roughly a quarter of patients, often months later."),
 ("A 28-year-old has a 2.2 cm AVM in the left thalamus with deep venous drainage that bled 2 months ago. Spetzler-Martin grade, and a reasonable option?", "Size 1 + eloquent 1 + deep drainage 1 = <strong>grade III</strong>. Deep, eloquent location makes surgery risky, so <strong>SRS</strong> is a reasonable option after multidisciplinary review."),
 ("Six months after SRS, the AVM above is smaller but still fills on MRA. Is he protected from bleeding?", "<strong>Not fully.</strong> Risk is lower during the latency period but not gone, and it falls further only after complete obliteration, which usually takes 1-3 years."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
OTHER = "\n".join([
"<p>These sites do not have their own module, but they appear on the schedule and on exams. For each one: <strong>where does radiation fit, and what is the one rule or trial to know?</strong> Treat these as orientation. Stage, patient selection, institutional practice, and new evidence change the details, and each site has its own guideline.</p>",
"",
"<h3 class='paradigm-h'>Lymphoma</h3>",
"<p>Lymphomas are <strong>very radiosensitive</strong>, so doses are low (often 20-36 Gy) and radiation is usually given <strong>after chemotherapy</strong> as consolidation, or alone for some early indolent lymphomas. Fields have shrunk from large extended fields to <strong>involved-site RT (ISRT)</strong>, which treats only the originally involved sites, to cut late effects.</p>",
table(["Disease", "Where radiation fits", "Know"], [
 ["<strong>Early Hodgkin lymphoma</strong>", "Short chemotherapy (ABVD) then ISRT: 20 Gy for favorable disease, 30 Gy for unfavorable", "<strong>GHSG HD10/HD11</strong> set those doses. PET-adapted trials (<strong>RAPID, H10, HD16</strong>): omitting RT after a negative interim PET slightly increased relapse without a clear survival difference, so the decision is individualized."],
 ["<strong>Diffuse large B-cell lymphoma</strong>", "R-CHOP, then RT to bulky disease or residual PET-positive disease in many patients (often 30-36 Gy)", "Younger patients with early, non-bulky, low-risk disease can often be treated with chemotherapy alone (FLYER)"],
 ["<strong>Follicular lymphoma</strong>, early stage", "ISRT <strong>24 Gy</strong> alone can give long-term control", "<strong>FORT</strong>: 24 Gy controlled disease better than 4 Gy"],
 ["<strong>Indolent lymphoma</strong>, palliative", "<strong>4 Gy in 2</strong> (\"boom-boom\") relieves symptoms", "Very low dose, high response"],
 ["<strong>Gastric MALT lymphoma</strong>", "<strong>H. pylori eradication first</strong>; RT (about 24-30 Gy) if lymphoma persists or is H. pylori negative", "Highly curable with RT"],
 ["<strong>Mycosis fungoides</strong>", "Local RT for plaques; <strong>total skin electron beam</strong> for widespread skin disease", "Even single low doses work for individual lesions"],
]),
pearl("Why fields shrank: survivors of Hodgkin lymphoma treated with large mantle fields as young women had high rates of <strong>breast cancer</strong>, <strong>heart disease</strong>, and <strong>hypothyroidism</strong> decades later."),
"",
"<h3 class='paradigm-h'>Skin Cancer</h3>",
"<ul>",
"<li><strong>Basal and squamous cell carcinoma</strong>: surgery (often <strong>Mohs</strong>) is standard. <strong>Definitive RT</strong> is an alternative, especially for older patients and for the <strong>nose, eyelid, lip, and ear</strong>, where surgery would cost function or cosmesis.</li>",
"<li><strong>Adjuvant RT</strong> after surgery for squamous cell carcinoma is considered for <strong>perineural invasion</strong> of a named or large nerve, positive margins that cannot be re-excised, or nodal disease.</li>",
"<li><strong>Be cautious</strong> in young patients (late cosmetic changes), on the <strong>lower leg</strong> (poor healing), in genetic syndromes that sensitize to radiation (Gorlin, xeroderma pigmentosum), and in some connective tissue diseases.</li>",
"<li><strong>Merkel cell carcinoma</strong>: aggressive and very radiosensitive; excision with sentinel node biopsy, then RT to the tumor bed (and often the nodes) for many patients.</li>",
"<li><strong>Melanoma</strong>: adjuvant nodal RT lowered lymph-node field relapse without improving survival (" + pm(22575589, "ANZMTG/TROG") + "); it is used much less in the immunotherapy era. RT is common for melanoma brain metastases (see CNS).</li>",
"</ul>",
"<p>Regimens range from about <strong>50-66 Gy in 20-33 fractions</strong> to shorter courses (for example 35 Gy in 5 or 40 Gy in 10) for frail patients.</p>",
"",
"<h3 class='paradigm-h'>Soft Tissue Sarcoma</h3>",
"<p>For extremity sarcoma, <strong>limb-sparing surgery plus radiation</strong> replaced amputation in most patients. The question is whether to give radiation before or after surgery.</p>",
compare(
 ("Preoperative", "About 50 Gy in 25", "Smaller field and lower dose, so less permanent <strong>fibrosis, edema, and joint stiffness</strong>, but more <strong>wound complications</strong>. Now commonly preferred."),
 ("Postoperative", "About 60-66 Gy", "Fewer wound problems, but a larger, higher-dose field and more permanent late effects."),
),
studies(
 ("NCIC SR2 (O'Sullivan)", "Extremity sarcoma: preoperative and postoperative RT gave similar local control; preoperative RT had about twice the major wound complications (35% vs 17%), and postoperative RT more late fibrosis."),
 ("STRASS", "Retroperitoneal sarcoma: preoperative RT did not improve abdominal recurrence-free survival overall."),
),
"",
"<h3 class='paradigm-h'>Plasmacytoma and Myeloma</h3>",
"<ul>",
"<li><strong>Solitary plasmacytoma</strong> (one lesion, no myeloma): <strong>definitive RT, about 35-50 Gy depending on site and size</strong>, controls the lesion in most patients, though many solitary bone plasmacytomas later progress to myeloma.</li>",
"<li><strong>Multiple myeloma</strong>: radiation is palliative and <strong>low doses work</strong> (for example 8 Gy in 1 or 20 Gy in 5). Keep fields small to protect marrow for future therapy and stem cell collection.</li>",
"</ul>",
"",
"<h3 class='paradigm-h'>Pediatrics</h3>",
"<p>Children are the most sensitive patients to late effects: <strong>growth</strong>, <strong>cognition</strong>, <strong>hormones</strong>, <strong>fertility</strong>, and <strong>second cancers</strong>. That is why pediatric plans use the lowest effective dose, often use <strong>protons</strong>, and young children often need <strong>daily anesthesia</strong> to lie still. Treatment follows cooperative-group protocols.</p>",
table(["Tumor", "Where radiation fits"], [
 ["<strong>Medulloblastoma</strong>", "Craniospinal RT plus a posterior fossa or tumor-bed boost after surgery (see CNS)"],
 ["<strong>Wilms tumor</strong>", "Low-dose flank RT for higher-stage disease; whole-lung RT for lung metastases that do not fully respond to chemotherapy"],
 ["<strong>Rhabdomyosarcoma</strong>", "RT for most patients except those with completely resected, favorable tumors"],
 ["<strong>Ewing sarcoma</strong>", "Radiosensitive; RT when surgery would be too morbid or margins are positive"],
 ["<strong>Hodgkin lymphoma</strong>", "Response-adapted: RT omitted for many children who respond well to chemotherapy"],
]),
"",
"<h3 class='paradigm-h'>Total Body Irradiation</h3>",
"<p><strong>TBI</strong> is part of the conditioning regimen before some <strong>allogeneic stem cell transplants</strong> (most often for leukemia): it kills leukemia cells, including those in sanctuary sites, and suppresses the immune system so the donor graft can take. Myeloablative regimens commonly give about <strong>12-13.2 Gy in 6-8 twice-daily fractions</strong>; non-myeloablative regimens give as little as 2 Gy. The <strong>lungs</strong> are the main dose-limiting organ (pneumonitis), so they are often partly shielded.</p>",
"",
"<h3>Also on the Schedule</h3>",
table(["Site", "Where radiation fits", "Know"], [
 ["<strong>Bladder</strong>", "<strong>Trimodality therapy</strong> (maximal TURBT, then chemoradiation) as a bladder-sparing alternative to cystectomy in selected patients", "<strong>BC2001</strong>: adding chemotherapy to RT improved locoregional control"],
 ["<strong>Testicular seminoma</strong>, stage I", "Surveillance is preferred for most; para-aortic RT (20 Gy) or single-dose carboplatin are alternatives", "Very radiosensitive; " + pm(15718317, "MRC TE18") + " showed 20 Gy matched 30 Gy"],
 ["<strong>Thymoma</strong>", "Postoperative RT considered for incompletely resected or more invasive tumors; its role in completely resected early tumors is debated", "Myasthenia gravis is a common association"],
 ["<strong>Uveal melanoma</strong>", "<strong>Plaque brachytherapy</strong> for medium tumors preserves the eye", "<strong>COMS</strong>: similar survival to enucleation"],
 ["<strong>Renal cell carcinoma</strong>", "SBRT for primary tumors in selected patients who cannot have surgery (mostly phase II data), and for metastases", "Radioresistant to conventional doses, but responds to ablative doses"],
]),
"",
HY,
])

DOCS = {
    "Background & Epidemiology": BACKGROUND,
    "Workup & Prognosis": WORKUP,
    "Palliative Radiation": PALLIATIVE,
    "Oncologic Emergencies": EMERGENCIES,
    "Benign Disease": BENIGN,
    "Functional & Vascular Radiosurgery": SRS,
    "Other Sites in Brief": OTHER,
}

for k, v in DOCS.items():
    assert "—" not in v and "–" not in v and "&mdash;" not in v and "&ndash;" not in v, k

if __name__ == "__main__":
    out = {k: {"title": k, "html": v} for k, v in DOCS.items()}
    p = os.path.join(ROOT, "src", "data", "docs", "palliative.json")
    with open(p, "w", encoding="utf8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("wrote", os.path.relpath(p, ROOT), len(out), "readings")
