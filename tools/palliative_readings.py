#!/usr/bin/env python3
"""
Source of truth for the Palliative & Benign readings (src/data/docs/palliative.json).
This site has no anatomy, lymph node, or staging reading: its "staging" is
prognosis, goals, and stability, so Workup & Prognosis takes that slot.

Usage:  python3 tools/palliative_readings.py
        python3 tools/hy_summaries.py   (fills each High-Yield Summary)
        python3 build.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Replaced by tools/hy_summaries.py (HY["palliative"]).
HY = "<div class='pearl hy-summary'>\n<strong>High-Yield Summary</strong>\n<ul style='margin-bottom:0;'>\n<li>See tools/hy_summaries.py</li>\n</ul>\n</div>"


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


def framework(title, sub, steps):
    out = [f"<div class='tx-framework'>\n<div class='txf-title'>{title}</div>\n<p class='txf-sub'>{sub}</p>"]
    for i, (iff, trig, then) in enumerate(steps, 1):
        out.append(f"<div class='tx-step'><div class='txs-num'>{i}</div><div>\n<div class='txs-if'>{iff}</div>\n<span class='txs-trigger'>{trig}</span>\n<div class='txs-then'>{then}</div>\n</div></div>")
    return "\n".join(out) + "\n</div>"


def big(t):
    return f"<div class='big-idea'>{t}</div>"


def pearl(t):
    return f"<div class='pearl'><strong>Clinical Pearl</strong><p>{t}</p></div>"


# ---------------------------------------------------------------------------
BACKGROUND = "\n".join([
"<p>Not every patient on a radiation service has a cancer you are trying to cure. A large share of the day is <strong>palliative</strong> work (pain, bleeding, obstruction, a spine that is about to fail), <strong>emergencies</strong> paged in overnight, and a smaller group of <strong>benign conditions</strong> where low doses of radiation calm inflammation or stop tissue from overgrowing. This module is the catch-all for that work, plus a short tour of the sites the other modules don't cover.</p>",
"<p>There is no anatomy, nodal, or staging reading here. The question that replaces staging is: <strong>what is the goal, how long is this patient likely to live, and what is the least burdensome treatment that reaches that goal?</strong></p>",
flow("Who is this patient? (this reading)", "Goals, prognosis, stability", "Palliative RT", "Emergencies", "Benign disease", "Functional and vascular SRS", "Other sites"),
"",
"<h3>Four Kinds of Patients</h3>",
table(["Patient", "Typical example", "What radiation is for", "Typical dose range"], [
 ["<strong>Palliative</strong>", "Painful bone metastasis, bleeding bladder tumor, obstructing lung mass", "Relieve a symptom or prevent one, with as few visits as possible", "8 Gy in 1 to 30 Gy in 10"],
 ["<strong>Emergency</strong>", "Cord compression, SVC obstruction, life-threatening bleeding", "Protect function (walking, breathing) or stop the event, fast", "8 Gy in 1 to 30 Gy in 10, started within hours to a day"],
 ["<strong>Benign</strong>", "Knee osteoarthritis, Dupuytren nodules, keloid, before a hip replacement", "Calm inflammation or stop overgrowth when other treatment has failed", "A few Gy (inflammation) to about 30 Gy (overgrowth)"],
 ["<strong>Functional or vascular SRS</strong>", "Trigeminal neuralgia, arteriovenous malformation", "A precise single high dose to a tiny target", "About 16-25 Gy to an AVM margin; 70-90 Gy maximum to the trigeminal nerve"],
]),
big("The dose depends on the goal: a few Gy calms inflammation, 8-30 Gy relieves symptoms, 50-80 Gy cures cancer, and a single very high dose to a tiny target destroys it."),
"",
"<h3>Palliative Radiation: Who and Why</h3>",
"<p>Palliative radiation is one of the most common things a radiation oncologist does; a large share of all radiation courses are given with palliative intent. The most common reason by far is a <strong>painful bone metastasis</strong>.</p>",
cards(
 ("Pain", "Bone metastases, nerve or plexus invasion, liver capsule stretch, pelvic masses. Pain relief usually starts within <strong>1-2 weeks</strong> and peaks at about <strong>4-6 weeks</strong>."),
 ("Bleeding", "Hemoptysis, hematuria, vaginal or rectal bleeding, fungating skin or breast tumors. <strong>Hemostatic RT</strong> often slows bleeding within days."),
 ("Obstruction", "Airway, esophagus, SVC, ureter, or bowel. Stents act faster; radiation can be more durable."),
 ("Neurologic function", "Cord compression and brain metastases. The goal is to keep the patient walking, thinking, and continent."),
),
"<h4>Which Cancers Go to Bone?</h4>",
"<p>Five primaries account for most bone metastases: <strong>prostate, breast, lung, kidney, and thyroid</strong>, plus <strong>multiple myeloma</strong>, which lives in the marrow. The axial skeleton (spine, pelvis, ribs) and the proximal femur and humerus are the usual sites, because that is where red marrow is.</p>",
table(["Lesion type", "Typical cancers", "Why it matters"], [
 ["<strong>Blastic</strong> (bone-forming, bright on CT)", "Prostate, some breast", "Shows up well on bone scan; less likely to fracture"],
 ["<strong>Lytic</strong> (bone-destroying, dark on CT)", "Kidney, thyroid, myeloma, lung, many breast", "Higher fracture risk; myeloma can be <strong>invisible on bone scan</strong>"],
 ["<strong>Mixed</strong>", "Breast, lung", "Judge by the lytic component"],
]),
pearl("Most patients with bone metastases have them in more than one place. Treat the lesion that is causing the symptom, not every spot on the scan, unless there is a specific reason (see prophylactic radiation in Palliative Radiation)."),
"",
"<h3>Benign Disease: Who and Why</h3>",
"<p>Radiation for benign conditions is common in Germany and other parts of Europe and much less common in the United States, but you will still see it, and it shows up on exams. It works through two mechanisms:</p>",
compare(
 ("A few Gy", "Anti-inflammatory", "Very low doses (often 0.5-1 Gy per fraction) change how macrophages, white cells, and blood vessel walls behave in inflamed tissue. Used for painful <strong>osteoarthritis</strong>, <strong>plantar fasciitis</strong>, and other degenerative joint and tendon problems."),
 ("Roughly 7-30 Gy", "Anti-proliferative", "Moderate doses stop fibroblasts or bone-forming precursor cells from multiplying. Used for <strong>Dupuytren</strong> and <strong>Ledderhose</strong> disease, <strong>keloids</strong>, <strong>heterotopic ossification</strong>, and <strong>gynecomastia</strong> prevention."),
),
"<p>Functional and vascular radiosurgery (trigeminal neuralgia, AVMs) is a third group: the target is tiny and the single dose is very high. It gets its own reading.</p>",
"<h4>The Rule for Benign Radiation</h4>",
cards(
 ("Other options first", "Radiation is usually offered after conservative treatment (drugs, injections, physical therapy) fails or isn't tolerated."),
 ("Lowest effective dose", "Benign doses are a small fraction of cancer doses, to the smallest volume that works."),
 ("Respect the cancer risk", "Any radiation carries a small lifetime risk of a second cancer. Be cautious in <strong>young patients</strong> and near the <strong>thyroid, breast, and gonads</strong>, and say so during consent."),
),
"",
"<h3>The Rest of the Service</h3>",
"<p>Lymphoma, skin cancer, sarcoma, plasmacytoma and myeloma, pediatric tumors, total body irradiation, and a few smaller sites (bladder, seminoma, thymoma, eye) don't have their own module. The last reading covers each in a few lines: what it is, where radiation fits, and the trial or rule you're most likely to be asked about.</p>",
"",
HY,
])

# ---------------------------------------------------------------------------
WORKUP = "\n".join([
"<p>In a curative site, stage tells you the plan. On the palliative service, five questions do that job. Answer them in order on every consult:</p>",
cards(
 ("What is the symptom, and is it from this lesion?", "A painful spot on the bone scan may not be the cause of the pain. Match the exam to the imaging."),
 ("What is the goal?", "Relieve pain, stop bleeding, keep walking, prevent a fracture, or durable control of limited disease."),
 ("How long is the patient likely to live?", "Prognosis picks the fractionation: weeks, months, or years."),
 ("Is the bone or spine stable, and is the cord safe?", "Instability and cord compression may need a surgeon before (or instead of) radiation."),
 ("What has already been treated?", "Prior radiation to the same area limits what you can safely give now."),
),
big("Stage tells you the plan in curative disease. In palliative disease, the goal, the prognosis, and stability tell you the plan."),
"",
"<h3>Goals and Prognosis</h3>",
"<p>Start with what matters to the patient and what they understand about their illness. Then estimate prognosis honestly. Clinicians tend to <strong>overestimate</strong> how long patients will live, which leads to courses that are longer than the patient's remaining time.</p>",
table(["Expected survival", "What it means for radiation"], [
 ["<strong>Weeks</strong>", "Single fraction (8 Gy in 1) or no radiation; focus on hospice and comfort. Pain relief takes 1-2 weeks to start, so very short survival may not leave time to benefit."],
 ["<strong>Months</strong>", "Short courses (8 Gy in 1 or 20 Gy in 5). Accept a higher chance of needing retreatment for fewer visits."],
 ["<strong>Years</strong> (or limited disease)", "Longer courses (30 Gy in 10) or <strong>SBRT</strong> for durable local control and less retreatment."],
]),
"<h4>What Predicts Survival</h4>",
"<ul>",
"<li><strong>Performance status</strong> (KPS or ECOG) is the single most useful predictor. A patient in bed most of the day (KPS 40 or less, ECOG 3-4) usually has weeks to a few months.</li>",
"<li><strong>Primary cancer</strong>: breast and prostate cancer with bone-only disease can live for years; lung cancer with visceral metastases usually much less.</li>",
"<li><strong>Where the metastases are</strong>: bone only is better than liver or brain.</li>",
"<li><strong>Systemic options left</strong>: a patient starting effective targeted therapy has a different outlook from one who has exhausted treatment.</li>",
"</ul>",
reveal("Reference: prognostic scores you might hear named",
 "<ul><li><strong>Chow three-item score</strong>: non-breast primary, metastases beyond bone, and KPS 60 or less. Median survival falls from more than a year with 0-1 factors to about 2 months with all 3.</li>"
 "<li><strong>TEACHH</strong>: tumor type, ECOG, age, prior palliative chemo, hospitalizations in the last 3 months, and liver metastases.</li>"
 "<li><strong>Rades score</strong> (cord compression) and the <strong>GPA</strong> (brain metastases, see CNS).</li>"
 "<li>The <strong>surprise question</strong> (\"Would I be surprised if this patient died in the next year?\") is a quick bedside screen for a goals-of-care talk.</li></ul>"),
"",
"<h3>Imaging: Which Test Answers Which Question</h3>",
table(["Question", "Best test", "Why"], [
 ["Where are the bone metastases?", "<strong>Bone scan</strong> or <strong>PET/CT</strong> (FDG; PSMA for prostate)", "Bone scan sees bone-forming activity, so it can <strong>miss purely lytic lesions such as myeloma</strong> (use a skeletal survey, low-dose CT, or MRI)"],
 ["Will this long bone break?", "<strong>Plain X-rays</strong> of the whole bone, then CT", "X-rays show cortical destruction; a lytic lesion is visible only after a large share of the bone is gone"],
 ["Is the cord compressed?", "<strong>MRI of the whole spine</strong>", "Many patients have disease at more than one level; CT myelogram if MRI is impossible"],
 ["Is the spine stable?", "<strong>CT</strong> plus MRI", "Bony collapse, alignment, and which parts of the vertebra are involved feed the SINS score"],
 ["Planning", "<strong>CT simulation</strong>", "Old plans and diagnostic imaging are fused to see prior dose and the target"],
]),
"<p><strong>Do you need a biopsy?</strong> Yes if there is no known cancer, if this would be the first metastasis, if the lesion is solitary after a long disease-free interval, or if a second cancer, lymphoma, myeloma, or infection is possible. A diagnosis of lymphoma or myeloma changes the plan, because both are very radiosensitive and often treated with drugs first.</p>",
"",
"<h3>Is the Spine Stable? SINS</h3>",
"<p>The <strong>Spinal Instability Neoplastic Score (SINS)</strong> adds six features into a 0-18 score. You don't need to memorize the points; you need to know what pushes a spine toward instability and that <strong>a score of 7 or higher means a spine surgeon should see the patient</strong>.</p>",
"<div class='sins-builder'></div>",
"<ul>",
"<li><strong>0-6: stable.</strong> Radiation alone is reasonable from a stability standpoint.</li>",
"<li><strong>7-12: potentially unstable.</strong> Surgical consultation.</li>",
"<li><strong>13-18: unstable.</strong> Stabilization is usually needed; radiation does not fix a broken spine.</li>",
"</ul>",
pearl("<strong>Mechanical pain</strong> (pain with movement, sitting up, or bearing weight that is relieved by lying still) suggests instability. <strong>Biologic pain</strong> (worse at night, steady, relieved by steroids) comes from the tumor itself and responds to radiation."),
"",
"<h3>Is the Cord Compressed? Bilsky Grade</h3>",
"<p>The <strong>Bilsky epidural spinal cord compression (ESCC) grade</strong> describes on axial T2 MRI how far tumor has pushed into the canal.</p>",
table(["Grade", "What MRI shows", "What it means"], [
 ["<strong>0</strong>", "Tumor in bone only", "Low grade"],
 ["<strong>1a-1c</strong>", "Epidural tumor that touches or indents the thecal sac but does not deform the cord", "Low grade: usually radiation (conventional or SBRT)"],
 ["<strong>2</strong>", "Cord compressed, but CSF still visible around it", "High grade"],
 ["<strong>3</strong>", "Cord compressed with no CSF visible", "High grade: surgical decompression if the tumor is radioresistant and the patient can tolerate it"],
]),
"<h4>Putting It Together: NOMS</h4>",
"<p>Spine teams combine these into the <strong>NOMS</strong> framework, four questions that decide surgery, conventional RT, or SBRT:</p>",
table(["Letter", "Question"], [
 ["<strong>N</strong>eurologic", "How high is the Bilsky grade, and is there myelopathy or radiculopathy?"],
 ["<strong>O</strong>ncologic", "Is the tumor <strong>radiosensitive</strong> (lymphoma, myeloma, seminoma, breast, prostate, small cell) or <strong>radioresistant</strong> to conventional doses (kidney, thyroid, melanoma, sarcoma, colon, liver, many NSCLC)?"],
 ["<strong>M</strong>echanical", "Is the spine unstable (SINS)?"],
 ["<strong>S</strong>ystemic", "Can the patient tolerate surgery, and what is the prognosis?"],
]),
big("Radiosensitive tumors usually get conventional RT even with high-grade compression. Radioresistant tumors with low-grade compression can get SBRT; with high-grade compression they often need surgery first."),
"",
"<h3>Will This Long Bone Break? Mirels Score</h3>",
"<p>For a lesion in the femur, humerus, or another long bone, <strong>Mirels' score</strong> adds four features (site, pain, lesion type, and how much of the bone's width is involved), each scored 1-3, for a total of 4-12.</p>",
"<div class='mirels-builder'></div>",
"<ul>",
"<li><strong>9 or more</strong>: high fracture risk. Orthopedics for <strong>prophylactic fixation</strong>, then postoperative radiation.</li>",
"<li><strong>8</strong>: borderline; use judgment.</li>",
"<li><strong>7 or less</strong>: radiation alone is reasonable.</li>",
"</ul>",
pearl("<strong>Pain with weight bearing</strong> (functional pain) in a lytic femur lesion is a warning sign of impending fracture. Ask about it on every bone metastasis consult and keep the patient off the leg until orthopedics weighs in."),
"",
"<h3>Prior Radiation</h3>",
"<p>Always ask whether the patient has had radiation before. Get the old plan, find the previous dose to the spinal cord or other limiting organs, and add it to what you plan now. Re-irradiation is often possible, especially with conventional palliative doses or SBRT, but it is planned around the <strong>cumulative</strong> dose.</p>",
quiz("Read the Consult", [
 ("A man with prostate cancer has a painful L3 metastasis. Pain is worst at night, steady, and better on dexamethasone. MRI shows bone disease without epidural extension. Biologic or mechanical pain?", "<strong>Biologic.</strong> Night pain that steroids relieve comes from the tumor and usually responds well to radiation."),
 ("A woman with renal cell carcinoma has back pain only when she sits up or stands. CT shows a lytic T12 lesion with 60% collapse. What score do you calculate and who do you call?", "<strong>SINS</strong>, which will be in at least the indeterminate range (junctional level, mechanical pain, lytic lesion, collapse over 50%). Call <strong>spine surgery</strong>: mechanical pain suggests instability, which radiation can't fix."),
 ("A lytic lesion in the mid femoral shaft takes up most of the bone's width and hurts with walking. Mirels score?", "Lower limb 2 + functional pain 3 + lytic 3 + more than 2/3 of the width 3 = <strong>11</strong>. High fracture risk: orthopedics for <strong>prophylactic fixation</strong>, then postoperative RT."),
 ("A patient with myeloma has new rib pain but a negative bone scan. What do you do?", "Bone scan can <strong>miss purely lytic myeloma lesions</strong>. Get CT or MRI (or a skeletal survey). Myeloma is very radiosensitive, so even low palliative doses work well."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
PALLIATIVE = "\n".join([
"<p>Palliative radiation answers one question: <strong>what is the shortest, simplest course that achieves this patient's goal?</strong> For most bone metastases the answer is shorter than students expect.</p>",
cards(
 ("What is the goal?", "Pain relief, local control, prevention of a fracture or cord compression, or durable control of limited metastases."),
 ("How long will they live?", "Short survival favors a single fraction; long survival favors a longer course or SBRT."),
 ("Is it complicated?", "Cord compression, a fracture or recent fixation, a soft tissue mass, or nerve pain change the plan."),
),
"",
"<h3>The Fractionation Menu</h3>",
"<p>For an <strong>uncomplicated, painful bone metastasis</strong>, these regimens give <strong>the same pain relief</strong>. About 60% of patients get meaningful relief and about a quarter become pain free. What differs is how many visits it takes and how often the pain comes back.</p>",
table(["Regimen", "Visits", "Best for", "Trade-off"], [
 ["<strong>8 Gy in 1</strong>", "1", "Most uncomplicated bone metastases; poor performance status or short survival; patients who travel far", "About <strong>twice as likely to need retreatment</strong> (about 20% vs about 8%)"],
 ["<strong>20 Gy in 5</strong>", "5", "A middle ground; often used for neuropathic pain and cord compression", "Slightly more acute side effects"],
 ["<strong>30 Gy in 10</strong>", "10", "Longer expected survival, after surgical fixation, cord compression, or a large soft tissue mass", "Most visits; no better pain relief for uncomplicated lesions"],
 ["<strong>SBRT</strong> (for example 24 Gy in 2, 27 Gy in 3, 30-35 Gy in 5, or 16-24 Gy in 1)", "1-5", "Good prognosis, radioresistant tumors, oligometastases, some re-irradiation", "Needs immobilization, MRI fusion, and image guidance; risk of vertebral fracture after spine SBRT"],
]),
big("For an uncomplicated painful bone metastasis, 8 Gy in 1, 20 Gy in 5, and 30 Gy in 10 relieve pain equally well. The single fraction trades fewer visits for more retreatment."),
"<div class='choice-drill' data-drill-set='pal-fx'></div>",
studies(
 ("RTOG 9714", "In breast and prostate cancer bone metastases, 8 Gy in 1 relieved pain as well as 30 Gy in 10, with less acute toxicity and more retreatment."),
 ("Dutch Bone Metastasis Study", "In more than 1,100 patients, 8 Gy in 1 matched 24 Gy in 6 for pain relief; retreatment was more common after the single fraction."),
),
reveal("Reference: other bone metastasis trials",
 "<ul><li><strong>Chow meta-analyses</strong>: across randomized trials, single and multiple fractions give equal overall and complete pain response; retreatment is higher after a single fraction.</li>"
 "<li><strong>TROG 96.05</strong> (neuropathic bone pain): 8 Gy in 1 could not be proven as good as 20 Gy in 5, so many clinicians use 20 Gy in 5 when the pain follows a nerve root.</li>"
 "<li><strong>ASTRO bone metastases guideline</strong> and <strong>Choosing Wisely</strong>: offer single fraction; avoid routine courses longer than 10 fractions for uncomplicated bone metastases.</li></ul>"),
"",
"<h3>What to Tell the Patient</h3>",
"<ul>",
"<li><strong>Timing</strong>: pain usually starts improving in 1-2 weeks and is best at about 4-6 weeks. Keep taking pain medication until it does.</li>",
"<li><strong>Pain flare</strong>: a temporary increase in pain within the first few days, in roughly a third to 40% of patients. <strong>Dexamethasone</strong> given around the treatment lowers the risk.</li>",
"<li><strong>Side effects depend on the site</strong>: nausea when the field includes the stomach or upper abdomen, diarrhea for the pelvis, sore throat or swallowing pain for the cervical or upper thoracic spine, fatigue for most.</li>",
"<li><strong>Retreatment</strong> is possible if pain returns.</li>",
"</ul>",
studies(
 ("NCIC SC.23", "Dexamethasone 8 mg before and for several days after palliative bone RT reduced pain flare compared with placebo."),
 ("NCIC SC.20", "For painful bone metastases needing re-irradiation, 8 Gy in 1 was noninferior to 20 Gy in 5 or 8 in the main analysis, with fewer side effects."),
),
"",
"<h3 class='paradigm-h'>SBRT for Spine and Bone</h3>",
"<p>SBRT gives a much higher dose in 1-5 treatments with tight margins. It is not needed for most palliative patients, but it helps when you need <strong>durable control</strong>: a good prognosis, a <strong>radioresistant</strong> tumor (kidney, melanoma, sarcoma), oligometastatic disease, or re-irradiation where the cord has already had its share.</p>",
studies(
 ("SC.24", "For painful spine metastases, SBRT 24 Gy in 2 gave more complete pain responses than conventional 20 Gy in 5."),
 ("RTOG 0631", "Single-fraction spine SBRT (16-18 Gy) did not improve pain relief at 3 months over 8 Gy in 1, so SBRT is not automatically better for pain."),
),
"<p>The main risks of spine SBRT are <strong>vertebral compression fracture</strong> (higher with lytic lesions, existing collapse, and very high single doses), pain flare, and rarely radiation myelopathy. SBRT needs MRI fusion, strict cord limits, and daily image guidance.</p>",
"",
"<h3 class='paradigm-h'>Prophylactic Radiation for High-Risk Bone Metastases</h3>",
"<p>Most asymptomatic bone metastases are watched. But some are likely to cause a fracture, cord compression, or severe pain soon, and treating them early can prevent a hospitalization.</p>",
studies(
 ("Gillespie (MSKCC, 2024)", "In a randomized phase II trial, radiating <strong>asymptomatic, high-risk</strong> bone metastases (bulky lesions of 2 cm or more, hip, shoulder, or sacroiliac joint, junctional spine, or posterior vertebral involvement) caused far fewer skeletal-related events and hospitalizations, and patients lived longer, than standard care."),
),
"<p>This is a phase II trial, so it is changing practice at many centers but is not a universal standard. The take-home: <strong>a bulky asymptomatic lesion in a weight-bearing or junctional site deserves a conversation</strong>, not just observation.</p>",
reveal("Reference: Gillespie trial details",
 "<p>Patients had widespread metastatic solid tumors with at least one high-risk asymptomatic or minimally symptomatic bone lesion. Skeletal-related events (pathologic fracture, cord compression, surgery, or radiation for pain) fell from about 29% to about 2%, hospitalizations for those events also fell, and overall survival at one year was better in the radiation arm. Larger confirmatory trials are under way.</p>"),
"",
"<h3 class='paradigm-h'>Oligometastases: When Palliation Becomes Ablation</h3>",
"<p>Some patients have only a few metastases. Treating each one with SBRT (with systemic therapy) may give <strong>durable control and, in selected patients, longer survival</strong>. This is a different goal from symptom relief, and it needs a different patient: good performance status, a controlled primary, and limited disease on modern imaging.</p>",
table(["Term", "Meaning"], [
 ["<strong>Oligometastatic</strong>", "Limited metastatic disease, usually up to 3-5 lesions"],
 ["<strong>Oligorecurrent</strong>", "A few new metastases after the primary was treated"],
 ["<strong>Oligoprogressive</strong>", "Most disease is controlled on systemic therapy, but a few sites are growing; treat those and stay on the drug"],
]),
studies(
 ("SABR-COMET", "In patients with a controlled primary and up to 5 metastases, adding SABR to standard care improved overall survival in a randomized phase II trial, with a small risk of treatment-related death."),
 ("ORIOLE", "In oligorecurrent prostate cancer, SBRT delayed progression compared with observation; PSMA PET helped find all the disease."),
 ("NRG-BR002", "In oligometastatic breast cancer, adding local ablative therapy to systemic therapy did not improve survival, a reminder that benefit is not universal."),
),
reveal("Reference: other oligometastasis trials",
 "<ul><li><strong>Gomez</strong>: in NSCLC with up to 3 metastases after first-line systemic therapy, consolidative local therapy improved progression-free and overall survival.</li>"
 "<li><strong>STOMP</strong>: metastasis-directed therapy delayed the need for ADT in oligorecurrent prostate cancer.</li>"
 "<li><strong>CURB</strong>: SBRT for oligoprogressive disease improved progression-free survival in NSCLC but not in breast cancer.</li>"
 "<li>Larger phase III trials (SABR-COMET-3 and -10 and others) are testing these results.</li></ul>"),
"",
"<h3 class='paradigm-h'>Other Palliative Targets</h3>",
table(["Problem", "How radiation helps", "Representative regimens"], [
 ["<strong>Bleeding</strong> (bladder, cervix, rectum, lung, skin, stomach)", "Hemostatic RT often slows bleeding within a few days", "8 Gy in 1 (sometimes repeated), 20 Gy in 5, 30 Gy in 10"],
 ["<strong>Airway obstruction or hemoptysis</strong>", "Shrinks the tumor; a stent or bronchoscopic debulking is faster if the airway is critical", "17 Gy in 2 (a week apart), 20 Gy in 5, 30 Gy in 10; 10 Gy in 1 for poor performance status"],
 ["<strong>Dysphagia</strong> (esophagus)", "Stent relieves faster; RT or brachytherapy is more durable", "20 Gy in 5, 30 Gy in 10"],
 ["<strong>Head and neck</strong> mass", "Pain, bleeding, airway, and fungating tumor", "<strong>Quad shot</strong>: 14.8 Gy in 4 fractions over 2 days (twice daily), repeated every 4 weeks up to 3 times"],
 ["<strong>Liver capsule pain</strong>", "Low-dose whole-liver RT", "For example 8 Gy in 1"],
 ["<strong>Brain metastases</strong>", "SRS, whole-brain RT, or supportive care", "See the CNS module"],
]),
"",
"<h3 class='paradigm-h'>Radiopharmaceuticals</h3>",
"<p>When pain is everywhere, a drug that carries radiation to every bone metastasis can do what external beam can't.</p>",
table(["Agent", "Use", "Know"], [
 ["<strong>Radium-223</strong> (alpha emitter, behaves like calcium)", "Castration-resistant prostate cancer with symptomatic bone metastases and <strong>no visceral metastases</strong>", "<strong>ALSYMPCA</strong>: improved overall survival, not just pain"],
 ["<strong>Lutetium-177 PSMA-617</strong>", "PSMA-positive metastatic castration-resistant prostate cancer after hormonal therapy and chemotherapy", "<strong>VISION</strong>: improved overall survival"],
 ["<strong>Lutetium-177 dotatate</strong>", "Somatostatin receptor-positive neuroendocrine tumors", "<strong>NETTER-1</strong>: improved progression-free survival"],
 ["<strong>Strontium-89, samarium-153</strong> (beta emitters)", "Diffuse bone pain", "Pain relief only; cause low blood counts"],
]),
"",
"<h3>End of Life</h3>",
"<ul>",
"<li>Starting radiation in the last weeks of life is common and often more burden than benefit. If expected survival is short, give <strong>one fraction or none</strong>, and involve palliative care and hospice.</li>",
"<li>A short course should not delay hospice enrollment; many hospices can coordinate a single palliative fraction.</li>",
"<li>The most useful question in the room is often <strong>\"What are you hoping this treatment will do for you?\"</strong></li>",
"</ul>",
quiz("Choose the Course", [
 ("An 84-year-old with metastatic lung cancer, ECOG 3, lives 2 hours away and has a painful rib metastasis. Regimen?", "<strong>8 Gy in 1.</strong> Same pain relief as longer courses, one trip. Retreatment is possible if needed."),
 ("A 52-year-old with ER-positive breast cancer and bone-only disease had a femur rod placed yesterday for an impending fracture. Regimen?", "<strong>A multifraction course</strong> (for example 20 Gy in 5 or 30 Gy in 10) to the <strong>whole length of the hardware</strong> once the wound allows. Her prognosis may be years, and postoperative RT lowers the chance the rod fails."),
 ("A 60-year-old with renal cell carcinoma, a controlled primary, and a single painful T9 metastasis without cord compression, KPS 90. What do you consider?", "<strong>Spine SBRT.</strong> Renal cell is radioresistant to conventional doses, and his prognosis justifies durable local control."),
 ("Three months after 8 Gy in 1 to a painful hip metastasis, the pain is back. Can you retreat?", "<strong>Yes.</strong> Re-irradiation is common after a single fraction; 8 Gy in 1 again is reasonable (SC.20)."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
EMERGENCIES = "\n".join([
"<p>True radiation oncology emergencies are few, but you will be paged about them. For each one, ask: <strong>is this actually a radiation emergency, or does something else (steroids, surgery, a stent, a biopsy) have to happen first?</strong></p>",
table(["Emergency", "Do first", "Where radiation fits"], [
 ["<strong>Metastatic spinal cord compression</strong>", "<strong>Dexamethasone</strong> and <strong>MRI of the whole spine</strong>", "Urgent RT, or surgery then RT"],
 ["<strong>Superior vena cava syndrome</strong>", "Secure the airway if needed, then <strong>get tissue</strong>; stent for severe symptoms", "After the diagnosis, for radiosensitive or chemoresistant tumors"],
 ["<strong>Life-threatening bleeding</strong>", "Resuscitate; endoscopy or interventional radiology", "Hemostatic RT when those fail or aren't possible"],
 ["<strong>Airway obstruction</strong>", "Bronchoscopy (debulking or stent) if critical", "RT or brachytherapy for durable relief"],
 ["<strong>Impending pathologic fracture</strong>", "Protect weight bearing; orthopedics", "Postoperative RT after fixation"],
 ["<strong>Symptomatic brain metastases</strong>", "Steroids; neurosurgery for mass effect", "SRS or whole-brain RT (see CNS)"],
]),
big("Before you radiate an emergency, ask what has to happen first: steroids, a scan, a surgeon, a stent, or a biopsy."),
"",
"<h3 class='paradigm-h'>Metastatic Spinal Cord Compression</h3>",
"<p>Up to about 5% of patients with cancer develop cord compression, most often from <strong>lung, breast, or prostate cancer</strong>, then myeloma, lymphoma, and kidney cancer. Most cases are in the <strong>thoracic spine</strong>.</p>",
"<h4>Recognize It</h4>",
"<ul>",
"<li><strong>Back pain</strong> is the first symptom in almost everyone, often for weeks before weakness. New back pain in a patient with cancer is cord compression until proven otherwise.</li>",
"<li>Then <strong>weakness</strong>, a <strong>sensory level</strong>, and finally <strong>bladder or bowel dysfunction</strong> (a late sign).</li>",
"<li><strong>Ambulatory status before treatment is the strongest predictor of walking afterward.</strong> Patients who walk in usually walk out; patients paralyzed for more than a day or two rarely recover.</li>",
"</ul>",
framework("Cancer + back pain + a neurologic finding", "Move fast: hours matter.", [
 ("First,", "Give steroids", "<b>Dexamethasone</b>, commonly a 10 mg IV load then 16 mg a day in divided doses. Very high doses add side effects without clear benefit."),
 ("Then,", "Image", "<b>MRI of the whole spine</b> (many patients have more than one level). CT myelogram if MRI isn't possible."),
 ("Ask,", "Is there tissue?", "If this could be the first sign of cancer, a biopsy may be needed, but don't let it delay decompression."),
 ("Ask,", "Is the patient a surgical candidate?", "A single area of compression, a tumor that is not very radiosensitive, reasonable prognosis, and not paralyzed for long: <b>surgical decompression and stabilization, then RT</b>."),
 ("Otherwise,", "Radiate", "<b>Urgent RT</b> with steroids, started the same day if possible."),
 ("Consider,", "SBRT", "For radioresistant tumors with low-grade compression or a good prognosis, at experienced centers."),
]),
studies(
 ("Patchell (2005)", "In selected patients with cord compression from a single area of a non-radiosensitive tumor, direct decompressive surgery followed by RT kept more patients walking, and for longer, than RT alone."),
 ("SCORAD III", "For cord compression in patients with a limited prognosis, 8 Gy in 1 gave ambulatory results close to 20 Gy in 5; it did not formally meet its noninferiority margin, but supports a single fraction for many patients."),
),
reveal("Reference: more on cord compression",
 "<ul><li><strong>Patchell</strong> excluded radiosensitive tumors (lymphoma, myeloma, leukemia, germ cell tumors) and patients paraplegic for more than 48 hours. In the trial, 84% kept walking with surgery plus RT versus 57% with RT alone.</li>"
 "<li><strong>ICORG 05-03</strong>: 10 Gy in 1 was noninferior to 20 Gy in 5 for ambulatory status.</li>"
 "<li>Retrospective series (Rades) suggest longer courses (30 Gy in 10) give better <strong>local control</strong>, which matters for patients expected to live longer.</li>"
 "<li><strong>Fields</strong>: conventional RT usually covers the involved vertebrae plus about one vertebral body above and below, and any paraspinal mass. After surgery, the field covers the operated levels and the hardware.</li></ul>"),
"",
"<h3 class='paradigm-h'>Superior Vena Cava Syndrome</h3>",
"<p>Tumor (or a clot) blocks blood returning from the head and arms. Most cases are from <strong>lung cancer</strong> (especially small cell) and <strong>lymphoma</strong>; a growing share are from <strong>catheter-related thrombosis</strong>.</p>",
"<ul>",
"<li><strong>Symptoms</strong>: swelling of the face, neck, and arms, distended chest wall veins, shortness of breath, cough, and headache, all worse when lying flat or bending over.</li>",
"<li><strong>Most patients are not in immediate danger</strong>, because collateral veins develop. The true emergencies are <strong>stridor or laryngeal edema</strong> and <strong>confusion from cerebral edema</strong>.</li>",
"</ul>",
compare(
 ("Severe symptoms", "Stent first", "An endovascular <strong>stent</strong> relieves symptoms within hours to a day or two. Radiation takes 1-2 weeks or more."),
 ("Stable patient", "Diagnosis first", "Get <strong>tissue</strong> before treatment. Small cell lung cancer, lymphoma, and germ cell tumors are treated with <strong>chemotherapy</strong>, and radiating before a biopsy can make the pathology unreadable."),
),
pearl("SVC syndrome used to be treated as an automatic emergency for radiation. Now the priorities are: protect the airway, stent if the patient is severely symptomatic, and <strong>get a diagnosis before you radiate</strong>."),
"",
"<h3 class='paradigm-h'>Bleeding, Airway, and Fracture</h3>",
cards(
 ("Bleeding", "Hemostatic RT (for example 8 Gy in 1, or 20 Gy in 5) works for many tumors, often within 24-72 hours. It complements, not replaces, transfusion, endoscopy, or embolization."),
 ("Airway", "A tumor that is closing the airway needs a bronchoscopist first (debulking or stent). Radiation then keeps it open."),
 ("Fracture", "A completed or impending fracture needs <strong>orthopedic fixation</strong>. Postoperative RT to the full length of the hardware improves function and reduces the need for repeat surgery."),
),
quiz("Triage the Page", [
 ("A woman with breast cancer has had back pain for 3 weeks and now trips on stairs. Exam shows mild leg weakness and brisk reflexes. First two orders?", "<strong>Dexamethasone</strong> and <strong>MRI of the whole spine</strong>, now."),
 ("A man with lung cancer has face and arm swelling for 2 weeks. He is breathing comfortably and is alert. CT shows a mediastinal mass. No biopsy yet. Radiate tonight?", "<strong>No.</strong> He is stable, so get <strong>tissue first</strong>. If it is small cell or lymphoma, chemotherapy is the main treatment. A stent is the fast fix if he worsens."),
 ("A 55-year-old with renal cell carcinoma has a single-level T7 compression (Bilsky 3), has been weak for 12 hours, and can still walk with help. Best approach?", "<strong>Surgical decompression and stabilization, then RT</strong> (Patchell). Renal cell is radioresistant and he is a good candidate."),
 ("A patient with myeloma has cord compression at T10 and can walk. Surgery or radiation?", "Usually <strong>radiation</strong>. Myeloma is highly radiosensitive, so surgery is reserved for instability or bone fragments in the canal."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
BENIGN = "\n".join([
"<p>Benign disease radiation uses doses so low they would never control a cancer. The skill is knowing <strong>which condition, at what stage, after which other treatments</strong>, and how to talk honestly about a small but real lifetime cancer risk.</p>",
table(["Condition", "Goal of radiation", "When it helps most", "Representative regimen"], [
 ["<strong>Osteoarthritis</strong> (knee, hand, shoulder, hip)", "Pain relief", "Painful joints that failed medicines, injections, and physical therapy, in older adults", "0.5-1 Gy per fraction, 3-6 Gy total"],
 ["<strong>Plantar fasciitis / heel spur</strong>", "Pain relief", "Chronic heel pain after conservative care fails", "0.5-1 Gy per fraction, 3-6 Gy total"],
 ["<strong>Dupuytren disease</strong> (palm) and <strong>Ledderhose</strong> (sole)", "Stop progression", "<strong>Early</strong>: nodules or cords with little or no contracture", "About 30 Gy in two courses of 5 x 3 Gy, 6-12 weeks apart (or 21 Gy in 7)"],
 ["<strong>Heterotopic ossification</strong>", "Prevent bone forming in soft tissue", "High-risk patients around a hip replacement or acetabular fracture surgery", "7-8 Gy in 1, within 24 hours before or 72 hours after surgery"],
 ["<strong>Keloid</strong>", "Prevent regrowth after excision", "Recurrent keloids, started right after surgery", "For example 12-16 Gy in 3-4 fractions, within about 24-48 hours of excision"],
 ["<strong>Gynecomastia</strong>", "Prevent breast growth on antiandrogens", "Men starting antiandrogen monotherapy (bicalutamide), <strong>before</strong> breast growth", "A single low dose (for example 10-12 Gy) with electrons"],
 ["<strong>Graves orbitopathy</strong>", "Reduce orbital inflammation", "Active, moderate disease, often with steroids", "About 20 Gy in 10 (low-dose schedules also used)"],
]),
big("Inflammatory conditions get a few Gy for pain. Overgrowth conditions get more, and must be treated early, before the scar, contracture, or bone has formed."),
"",
"<h3>Safety First</h3>",
cards(
 ("Age", "The lifetime risk of a radiation-induced cancer falls with age. Benign radiation is usually reserved for older adults; be very cautious under about 40."),
 ("Location", "Keep the thyroid, breast, eyes, and gonads out of the field whenever possible. Hands and feet are relatively safe sites."),
 ("Consent", "Explain the expected benefit, the alternatives, and the small cancer risk. Document it."),
),
"",
"<h3 class='paradigm-h'>Osteoarthritis and Plantar Fasciitis</h3>",
"<ul>",
"<li><strong>Who</strong>: older adults with chronic joint or heel pain that has not responded to NSAIDs, injections, physical therapy, orthotics, or weight loss, or who are poor surgical candidates.</li>",
"<li><strong>How</strong>: very low doses, often 0.5-1 Gy two to three times a week, 3-6 Gy total, with a second course after about 6-12 weeks if the response is incomplete.</li>",
"<li><strong>Side effects</strong>: essentially none acutely at these doses. Pain sometimes flares briefly before improving.</li>",
"</ul>",
studies(
 ("Dutch sham-controlled trials (Mahler, 2019)", "In knee and hand osteoarthritis, low-dose RT (6 x 1 Gy) did not relieve pain better than sham radiation, a reminder that the placebo effect in joint pain is large."),
 ("Niewald (plantar fasciitis)", "6 Gy (6 x 1 Gy) relieved heel pain better than a very low 0.6 Gy control dose, supporting a real effect in calcaneal pain."),
),
"<p>The evidence is mixed: German series and some newer randomized trials report benefit, while sham-controlled trials have not always shown it. If asked, say that low-dose RT is <strong>an option after conservative care fails, with evidence that is still debated</strong>.</p>",
"",
"<h3 class='paradigm-h'>Dupuytren and Ledderhose Disease</h3>",
"<p>Dupuytren disease is a fibroproliferative disorder of the palmar fascia: first <strong>nodules</strong>, then <strong>cords</strong>, then <strong>flexion contracture</strong> of the fingers (ring and little fingers most often). Ledderhose disease is the same process in the sole of the foot.</p>",
compare(
 ("Early: nodules and cords, little or no contracture", "Radiation", "RT slows or stops progression in most patients by suppressing the proliferating fibroblasts."),
 ("Late: established contracture", "Procedures", "Needle aponeurotomy, collagenase injection, or surgery straighten the finger. RT can't reverse a contracture once the cord has matured."),
),
"<ul>",
"<li><strong>Technique</strong>: low-energy X-rays (orthovoltage) or electrons to the nodules and cords with a margin of about 1-2 cm, with the rest of the hand shielded.</li>",
"<li><strong>Regimen</strong>: about 30 Gy in two courses of 5 x 3 Gy separated by 6-12 weeks, or 21 Gy in 7 fractions.</li>",
"<li><strong>Side effects</strong>: dry skin and mild redness acutely; late skin dryness, thinning, or reduced sweating in a few patients.</li>",
"</ul>",
pearl("The key word for Dupuytren is <strong>early</strong>. A patient who can still lay the hand flat on a table (a negative tabletop test) is the patient who benefits."),
"",
"<h3 class='paradigm-h'>Heterotopic Ossification</h3>",
"<p>Heterotopic ossification (HO) is <strong>bone that forms in soft tissue</strong>, most often around the hip after arthroplasty or acetabular fracture surgery, and around the elbow. It can cause pain and stiffness and sometimes needs another operation.</p>",
"<ul>",
"<li><strong>Highest risk</strong>: <strong>prior HO</strong> (the strongest predictor), ankylosing spondylitis, diffuse idiopathic skeletal hyperostosis (DISH), hypertrophic osteoarthritis, and male sex.</li>",
"<li><strong>Why timing is everything</strong>: radiation kills the precursor cells before they turn into bone-forming cells, which happens in the first few days after surgery. Once bone has formed, radiation can't remove it.</li>",
"<li><strong>Regimen</strong>: a single <strong>7-8 Gy</strong> given within about <strong>24 hours before</strong> or <strong>72 hours after</strong> surgery; both work about equally well.</li>",
"<li><strong>Shield</strong> uncemented (porous) prosthesis components so bone can still grow into them.</li>",
"<li><strong>Alternative</strong>: NSAIDs such as indomethacin, which carry GI and kidney side effects.</li>",
"</ul>",
"",
"<h3 class='paradigm-h'>Keloids</h3>",
"<ul>",
"<li>Keloids are scars that grow beyond the original wound. Excision alone often fails, frequently with a larger keloid.</li>",
"<li><strong>Postoperative RT</strong>, started within about 24-48 hours of excision, lowers recurrence substantially.</li>",
"<li>Electrons or superficial X-rays (or brachytherapy) to the scar with a small margin; for example 12-16 Gy in 3-4 fractions.</li>",
"<li>Recurrence is higher on the chest, shoulder, and upper back (high-tension skin) than on the earlobe. Avoid in children when possible.</li>",
"</ul>",
"",
"<h3 class='paradigm-h'>Gynecomastia Prevention</h3>",
"<p>Men with prostate cancer who take an <strong>antiandrogen alone</strong> (for example bicalutamide) often develop painful breast enlargement. A single low dose to each breast bud <strong>before</strong> starting the drug prevents much of it. <strong>Tamoxifen</strong> prevents it even more effectively, and treatment after the breast has grown works poorly, because the tissue has become fibrotic.</p>",
"",
"<h3>Other Benign Conditions You May Hear About</h3>",
table(["Condition", "Where radiation fits"], [
 ["<strong>Graves orbitopathy</strong>", "Orbital RT for active, moderate disease, often with steroids; avoid in diabetic retinopathy; newer drugs (teprotumumab) have reduced its use"],
 ["<strong>Pterygium</strong>", "Beta radiation (strontium-90 applicator) right after excision lowers regrowth"],
 ["<strong>Desmoid tumor</strong>", "Observation or systemic therapy first; RT (about 50-56 Gy) for progressive or symptomatic disease when surgery would be morbid"],
 ["<strong>Epicondylitis, shoulder syndromes</strong>", "Low-dose anti-inflammatory RT, similar to osteoarthritis"],
 ["<strong>Benign tumors</strong> (meningioma, vestibular schwannoma, pituitary adenoma, paraganglioma)", "Fractionated RT or SRS; see the CNS module"],
]),
quiz("Benign or Not Now?", [
 ("A 70-year-old has painful nodules in both palms and can still lay her hands flat. Radiation?", "<strong>Yes, she's a good candidate.</strong> Early Dupuytren disease: about 30 Gy in two split courses to slow progression."),
 ("A 64-year-old has a ring finger fixed at 60 degrees of flexion from a thick cord. Radiation?", "<strong>No.</strong> RT can't reverse an established contracture. Refer for needle aponeurotomy, collagenase, or surgery."),
 ("A man with HO after his left hip replacement is scheduled for a right hip replacement next week. What do you offer, and when?", "<strong>A single 7-8 Gy</strong> within about 24 hours before or 72 hours after surgery. Prior HO is the strongest risk factor."),
 ("A 25-year-old asks for radiation for knee osteoarthritis. What do you weigh?", "<strong>Her age.</strong> The lifetime cancer risk is highest in young patients, and the evidence for OA pain is mixed. Other treatment is preferred."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
SRS = "\n".join([
"<p>Radiosurgery isn't only for tumors. Two benign brain conditions come up again and again on the service and on exams: <strong>trigeminal neuralgia</strong> and <strong>arteriovenous malformations (AVMs)</strong>. Both use a single, very precise, very high dose, and in both the benefit is <strong>delayed</strong>.</p>",
compare(
 ("Trigeminal neuralgia", "Target: a nerve", "A tiny spot on the trigeminal nerve root gets 70-90 Gy maximum dose. Pain relief takes weeks to months."),
 ("AVM", "Target: a tangle of vessels", "The whole nidus gets about 16-25 Gy at its edge. The vessels close over 1-3 years, and the bleeding risk lasts until they do."),
),
big("In functional and vascular radiosurgery, the effect is delayed. Pain relief takes weeks, and AVM closure takes years."),
"",
"<h3 class='paradigm-h'>Trigeminal Neuralgia</h3>",
"<h4>Recognize It</h4>",
"<ul>",
"<li><strong>Brief, electric shock-like, one-sided facial pain</strong> lasting seconds, usually in the <strong>V2 or V3</strong> distribution (cheek, jaw).</li>",
"<li>Triggered by <strong>light touch, chewing, talking, brushing teeth, or wind</strong>. Between attacks the patient is usually pain free and the neurologic exam is normal.</li>",
"<li>Most patients are over 50 and more are women. In a <strong>young patient or with bilateral symptoms, think of multiple sclerosis</strong>.</li>",
"<li>The usual cause is <strong>a blood vessel</strong> (most often the superior cerebellar artery) pressing on the nerve where it enters the pons, wearing away its myelin.</li>",
"</ul>",
"<h4>Workup and First-Line Treatment</h4>",
"<ul>",
"<li><strong>MRI</strong> with thin-slice sequences to exclude a tumor or MS and to look for a compressing vessel.</li>",
"<li><strong>Carbamazepine</strong> (or oxcarbazepine) is first-line and works for most patients at first. Procedures are for pain that drugs no longer control or side effects the patient can't tolerate.</li>",
"</ul>",
table(["Procedure", "Best for", "Trade-off"], [
 ["<strong>Microvascular decompression</strong>", "Younger, healthy patients with a compressing vessel", "Most durable relief, but a craniotomy"],
 ["<strong>Percutaneous rhizotomy</strong> (glycerol, balloon, radiofrequency)", "Older patients who want immediate relief", "Quick, but more numbness and recurrence"],
 ["<strong>Stereotactic radiosurgery</strong>", "Older or medically frail patients, those on anticoagulants, or after other procedures fail", "Noninvasive, but relief is delayed and recurrence is common over years"],
]),
"<h4>Radiosurgery Details</h4>",
"<ul>",
"<li><strong>Target</strong>: the trigeminal nerve root in the cistern, a few millimeters in front of where it enters the pons, with a single small (4 mm) shot.</li>",
"<li><strong>Dose</strong>: a <strong>maximum dose of 70-90 Gy</strong> (often about 80 Gy) in one session. Because the target is a nerve, the dose is prescribed to the center, not the edge.</li>",
"<li><strong>Response</strong>: most patients get meaningful relief, usually starting within about 1-3 months. About half are still pain free several years later; repeat SRS is possible.</li>",
"<li><strong>Main side effect</strong>: <strong>facial numbness</strong> or tingling in a minority, more often with higher doses and retreatment. Severe painful numbness (anesthesia dolorosa) is rare.</li>",
"</ul>",
reveal("Reference: Barrow Neurological Institute (BNI) pain score",
 "<p>Outcomes are reported on the BNI scale: <strong>I</strong> no pain, no medication; <strong>II</strong> occasional pain, no medication; <strong>IIIa</strong> no pain on medication; <strong>IIIb</strong> some pain, adequately controlled on medication; <strong>IV</strong> some pain, not adequately controlled; <strong>V</strong> severe pain, no relief. \"Success\" is usually BNI I-IIIb.</p>"),
"",
"<h3 class='paradigm-h'>Arteriovenous Malformations</h3>",
"<p>An AVM is a tangle of abnormal vessels (the <strong>nidus</strong>) where arteries connect directly to veins without capillaries in between. The high-pressure flow can rupture.</p>",
"<h4>Recognize It</h4>",
"<ul>",
"<li><strong>Hemorrhage</strong> is the most common presentation, usually in a young adult; then <strong>seizures</strong>, headache, or a focal deficit. Many are found by chance on MRI.</li>",
"<li>The risk of bleeding is roughly <strong>2-4% per year</strong>, higher after a prior bleed and with deep location, deep venous drainage, or an associated aneurysm.</li>",
"<li><strong>Catheter angiography</strong> is the gold standard to map the feeding arteries, nidus, and draining veins.</li>",
"</ul>",
"<h4>Spetzler-Martin Grade</h4>",
table(["Feature", "Points"], [
 ["<strong>Size</strong>: under 3 cm / 3-6 cm / over 6 cm", "1 / 2 / 3"],
 ["<strong>Eloquent brain</strong> nearby (motor, sensory, language, visual cortex, thalamus, brainstem): no / yes", "0 / 1"],
 ["<strong>Venous drainage</strong>: superficial only / any deep", "0 / 1"],
]),
"<p>Grades run I-V. <strong>Low grades (I-II)</strong> are usually best treated with <strong>surgery</strong>, which cures immediately. <strong>Small AVMs in deep or eloquent locations</strong>, where surgery is risky, are the classic <strong>radiosurgery</strong> patients. High grades (IV-V) are often observed.</p>",
"<h4>Radiosurgery Details</h4>",
"<ul>",
"<li><strong>Who</strong>: small AVMs (usually under about 3 cm, or about 10 cc) in deep or eloquent brain.</li>",
"<li><strong>Dose</strong>: about <strong>16-25 Gy</strong> to the edge of the nidus in one session, often around 18-22 Gy. Higher doses close more AVMs but cause more brain injury.</li>",
"<li><strong>How it works</strong>: radiation injures the vessel lining, which slowly thickens until the vessels close. <strong>Complete obliteration takes 1-3 years</strong> and occurs in roughly 70-80% of small AVMs.</li>",
"<li><strong>The latency period</strong>: until the AVM is fully obliterated, <strong>the bleeding risk remains</strong>. Patients need to understand this.</li>",
"<li><strong>Follow-up</strong>: MRI every 6-12 months, then <strong>angiography</strong> to confirm obliteration, usually around 3 years.</li>",
"<li><strong>Side effects</strong>: imaging changes around the treated area are common; symptomatic swelling, seizures, or late cysts occur in a minority.</li>",
"</ul>",
studies(
 ("ARUBA", "In <strong>unruptured</strong> brain AVMs, medical management alone led to fewer strokes and deaths over the short follow-up than medical management plus intervention (surgery, embolization, or SRS). The trial is widely debated, but it made observation a real option for unruptured AVMs."),
),
pearl("Ruptured AVMs are usually treated, because the risk of bleeding again is highest in the first year. For unruptured AVMs, the decision weighs a lifetime of small annual risk (higher in young patients) against the immediate risk of treatment."),
"",
"<h3>Other Functional Radiosurgery</h3>",
"<ul>",
"<li><strong>Essential tremor</strong> and tremor-dominant Parkinson disease: Gamma Knife <strong>thalamotomy</strong> (a very high single dose to the ventral intermediate nucleus) for patients who can't have deep brain stimulation or focused ultrasound. Effect is delayed by months.</li>",
"<li><strong>Cardiac radioablation</strong> for refractory ventricular tachycardia (a single 25 Gy to the arrhythmia scar) is an emerging, investigational use.</li>",
"</ul>",
quiz("Radiosurgery Check", [
 ("A 72-year-old on warfarin has electric shock-like right jaw pain when she chews. Carbamazepine now makes her too drowsy. MRI shows no tumor. Which procedure fits her best?", "<strong>Stereotactic radiosurgery.</strong> It is noninvasive, needs no stopping of anticoagulation, and suits an older patient; relief takes weeks."),
 ("What is the main side effect to counsel her about?", "<strong>Facial numbness or tingling</strong> in the treated distribution, in a minority of patients."),
 ("A 28-year-old has a 2.2 cm AVM in the left thalamus with deep venous drainage that bled 2 months ago. Spetzler-Martin grade, and best option?", "Size 1 + eloquent 1 + deep drainage 1 = <strong>grade III</strong>. Deep and eloquent location makes surgery risky, so <strong>SRS</strong> is a good option."),
 ("Six months after SRS, the AVM above is smaller but still fills on MRA. Is he protected from bleeding?", "<strong>No.</strong> The bleeding risk persists until the AVM is completely obliterated, which usually takes 1-3 years."),
]),
"",
HY,
])

# ---------------------------------------------------------------------------
OTHER = "\n".join([
"<p>These sites don't have their own module, but they appear on the schedule and on exams. For each one: <strong>where does radiation fit, and what is the one rule or trial to know?</strong></p>",
"",
"<h3 class='paradigm-h'>Lymphoma</h3>",
"<p>Lymphomas are <strong>very radiosensitive</strong>, so doses are low (often 20-36 Gy) and radiation is usually given <strong>after chemotherapy</strong> as consolidation. Fields have shrunk from large extended fields to <strong>involved-site RT (ISRT)</strong>, which treats only the originally involved nodes, to cut late effects.</p>",
table(["Disease", "Where radiation fits", "Know"], [
 ["<strong>Early Hodgkin lymphoma</strong>", "Short chemotherapy (ABVD) then ISRT: 20 Gy for favorable disease, 30 Gy for unfavorable", "<strong>GHSG HD10/HD11</strong> set those doses. PET-adapted trials (<strong>RAPID, H10, HD16</strong>): omitting RT after a negative interim PET slightly increases relapse but not death, so the decision is individualized."],
 ["<strong>Diffuse large B-cell lymphoma</strong>", "R-CHOP, then RT to bulky disease or a PET-positive residual mass (often 30-36 Gy)", "Early, low-risk disease can be treated with chemotherapy alone"],
 ["<strong>Follicular lymphoma</strong>, early stage", "ISRT <strong>24 Gy</strong> alone can be curative", "<strong>FORT</strong>: 24 Gy controlled disease better than 4 Gy"],
 ["<strong>Indolent lymphoma</strong>, palliative", "<strong>4 Gy in 2</strong> (\"boom-boom\") relieves symptoms", "Very low dose, high response"],
 ["<strong>Gastric MALT lymphoma</strong>", "<strong>H. pylori eradication first</strong>; RT (about 24-30 Gy) if it persists or is H. pylori negative", "Highly curable with RT"],
 ["<strong>Mycosis fungoides</strong>", "Local RT for plaques; <strong>total skin electron beam</strong> for widespread skin disease", "Even single low doses work for individual lesions"],
]),
pearl("Why fields shrank: survivors of Hodgkin lymphoma treated with large mantle fields as young women had high rates of <strong>breast cancer</strong>, <strong>heart disease</strong>, and <strong>hypothyroidism</strong> decades later."),
"",
"<h3 class='paradigm-h'>Skin Cancer</h3>",
"<ul>",
"<li><strong>Basal and squamous cell carcinoma</strong>: surgery (often <strong>Mohs</strong>) is standard. <strong>Definitive RT</strong> is an excellent alternative for older patients and for the <strong>nose, eyelid, lip, and ear</strong>, where surgery would cost function or cosmesis.</li>",
"<li><strong>Adjuvant RT</strong> after surgery for squamous cell carcinoma with <strong>perineural invasion</strong> of a named nerve, positive margins that can't be re-excised, or nodal disease.</li>",
"<li><strong>Be cautious</strong> in young patients (late cosmetic changes), on the <strong>lower leg</strong> (poor healing), in genetic syndromes that sensitize to radiation (Gorlin, xeroderma pigmentosum), and in connective tissue diseases such as scleroderma.</li>",
"<li><strong>Merkel cell carcinoma</strong>: aggressive and very radiosensitive; wide excision with sentinel node biopsy, then RT to the tumor bed (and often the nodes).</li>",
"<li><strong>Melanoma</strong>: adjuvant nodal RT lowers regional recurrence without improving survival (ANZMTG/TROG); used less in the immunotherapy era. RT is common for melanoma brain metastases (see CNS).</li>",
"</ul>",
"<p>Regimens range from about <strong>50-60 Gy in 20-30 fractions</strong> to shorter courses (for example <strong>35 Gy in 5</strong> or 40 Gy in 10) for frail patients.</p>",
"",
"<h3 class='paradigm-h'>Soft Tissue Sarcoma</h3>",
"<p>For extremity sarcoma, <strong>limb-sparing surgery plus radiation</strong> replaced amputation with the same survival. The question is whether to give radiation before or after surgery.</p>",
compare(
 ("Preoperative", "About 50 Gy in 25", "Smaller field, lower dose, less permanent <strong>fibrosis, edema, and joint stiffness</strong>, but more <strong>wound complications</strong>. Now commonly preferred."),
 ("Postoperative", "About 60-66 Gy", "Fewer wound problems, but a larger, higher-dose field and more permanent late effects."),
),
studies(
 ("NCIC SR2 (O'Sullivan)", "Preoperative and postoperative RT gave the same local control in extremity sarcoma; preoperative RT had about twice the wound complications, and postoperative RT more late fibrosis."),
 ("STRASS", "In retroperitoneal sarcoma, preoperative RT did not improve abdominal recurrence-free survival overall."),
),
"",
"<h3 class='paradigm-h'>Plasmacytoma and Myeloma</h3>",
"<ul>",
"<li><strong>Solitary plasmacytoma</strong> (one lesion, no myeloma): <strong>definitive RT, about 40-50 Gy</strong>, controls the lesion in most patients, though many solitary bone plasmacytomas later progress to myeloma.</li>",
"<li><strong>Multiple myeloma</strong>: radiation is palliative and <strong>very low doses work</strong> (for example 8 Gy in 1 or 20 Gy in 5). Keep fields small to protect marrow for future therapy and stem cell collection.</li>",
"</ul>",
"",
"<h3 class='paradigm-h'>Pediatrics</h3>",
"<p>Children are the most sensitive patients to late effects: <strong>growth</strong>, <strong>cognition</strong>, <strong>hormones</strong>, <strong>fertility</strong>, and <strong>second cancers</strong>. That is why pediatric plans use the lowest effective dose, often use <strong>protons</strong>, and young children often need <strong>daily anesthesia</strong> to lie still.</p>",
table(["Tumor", "Where radiation fits"], [
 ["<strong>Medulloblastoma</strong>", "Craniospinal RT plus a posterior fossa boost after surgery (see CNS)"],
 ["<strong>Wilms tumor</strong>", "Low-dose flank RT for higher-stage disease; whole-lung RT for lung metastases that don't resolve with chemo"],
 ["<strong>Rhabdomyosarcoma</strong>", "RT for most patients except completely resected, favorable tumors"],
 ["<strong>Ewing sarcoma</strong>", "Radiosensitive; RT when surgery would be too morbid or margins are positive"],
 ["<strong>Hodgkin lymphoma</strong>", "Response-adapted: RT omitted for many children who respond well to chemotherapy"],
]),
"",
"<h3 class='paradigm-h'>Total Body Irradiation</h3>",
"<p><strong>TBI</strong> is part of the conditioning regimen before some <strong>allogeneic stem cell transplants</strong> (most often for leukemia): it kills leukemia cells, including those in sanctuary sites, and suppresses the immune system so the donor graft can take. Myeloablative regimens give about <strong>12-13.2 Gy in 6-8 twice-daily fractions</strong>; non-myeloablative regimens give as little as 2 Gy. The <strong>lungs</strong> are the main dose-limiting organ (pneumonitis), so they are often partly shielded.</p>",
"",
"<h3>Also on the Schedule</h3>",
table(["Site", "Where radiation fits", "Know"], [
 ["<strong>Bladder</strong>", "<strong>Trimodality therapy</strong> (maximal TURBT, then chemoRT) as a bladder-sparing alternative to cystectomy", "<strong>BC2001</strong>: adding chemo to RT improved local control"],
 ["<strong>Testicular seminoma</strong>, stage I", "Surveillance is preferred; para-aortic RT (20 Gy) or single-dose carboplatin are alternatives", "Very radiosensitive; low doses cure"],
 ["<strong>Thymoma</strong>", "Postoperative RT for invasive or incompletely resected tumors", "Myasthenia gravis is a common association"],
 ["<strong>Uveal melanoma</strong>", "<strong>Plaque brachytherapy</strong> for medium tumors preserves the eye", "<strong>COMS</strong>: same survival as enucleation"],
 ["<strong>Renal cell carcinoma</strong>", "SBRT for primary tumors in patients who can't have surgery, and for metastases", "Radioresistant to conventional doses, but responds to ablative doses"],
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
    assert "\u2014" not in v and "\u2013" not in v and "&mdash;" not in v and "&ndash;" not in v, k

out = {k: {"title": k, "html": v} for k, v in DOCS.items()}
p = os.path.join(ROOT, "src", "data", "docs", "palliative.json")
with open(p, "w", encoding="utf8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("wrote", os.path.relpath(p, ROOT), len(out), "readings")
