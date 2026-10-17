"""Source of truth for the six "Before You Start" readings.

Writes src/data/background.json (id, num, title, question, objectives, html).
Rerun after editing:  python3 tools/background_readings.py && python3 build.py

The six readings tell one story, written for a first-year medical student:
what radiation is -> how it works -> the tools -> presenting a patient ->
deciding whether radiation helps -> designing the treatment.
Style: plain sentences, no contractions, no em or en dashes (checked in main()).
"""
import json
import os
import re

from bys_figures import crt_vs_imrt, delivery, igrt, linac_mlc, stereotactic

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "data", "background.json")


def vflow(phases):
    """Vertical numbered workflow. phases = [(phase label or None, [(title, text), ...]), ...]"""
    out, n = ["<div class='v-flow'>"], 0
    for label, steps in phases:
        if label:
            out.append(f"<div class='vf-phase'>{label}</div>")
        for title, text in steps:
            n += 1
            out.append(f"<div class='vf-step'><span class='vf-num'>{n}</span><div class='vf-body'><strong>{title}</strong><p>{text}</p></div></div>")
    out.append("</div>")
    return "\n".join(out)


def cards(items, numbered=True):
    out = ["<div class='card-grid'>"]
    for i, (title, body) in enumerate(items, 1):
        num = f"<div class='card-num'>{i}</div>" if numbered else ""
        out.append(f"<div class='card'>{num}<div class='card-title'>{title}</div><p>{body}</p></div>")
    out.append("</div>")
    return "\n".join(out)


def summary(items):
    lis = "".join(f"<li>{t}</li>" for t in items)
    return f"<div class='pearl'>\n<strong>High-Yield Summary</strong>\n<ul style='margin-bottom:0;'>{lis}</ul>\n</div>"


def table(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<div class='table-wrap'><table>\n<thead><tr>{th}</tr></thead>\n<tbody>{trs}</tbody>\n</table></div>"


def compare(*cols):
    out = ["<div class='compare-grid'>"]
    for label, head, body in cols:
        out.append(f"<div class='compare-col'>\n<span class='compare-label'>{label}</span>\n<h5>{head}</h5>\n{body}\n</div>")
    out.append("</div>")
    return "\n".join(out)


def script(label, text):
    return f"<div class='script-box'>\n<span class='script-label'>{label}</span>\n{text}\n</div>"


# ---------------------------------------------------------------------------
# 01  RADIATION 101
# ---------------------------------------------------------------------------
RAD101 = f"""
<p>Imagine a woman who has just learned she has breast cancer. Over the next few months she will meet three kinds of cancer doctors. A <strong>surgeon</strong> will remove the tumor. A <strong>medical oncologist</strong> may give her medicines, such as chemotherapy or hormone therapy, that travel through her whole body. And a <strong>radiation oncologist</strong> will aim carefully planned beams of radiation at her breast to destroy any cancer cells the surgeon could not see.</p>
<p>This guide is about that third doctor. This first reading follows a patient from her first radiation visit to her last, and teaches the few words about dose that everyone in a radiation department uses.</p>

<h3 id='fits'>Three Ways to Treat Cancer</h3>
<p>Cancer treatment comes in two broad kinds. A <strong>local</strong> treatment works on one part of the body. A <strong>systemic</strong> treatment reaches cancer cells wherever they are.</p>
{cards([
    ("Surgery", "Cuts the tumor out, often with nearby lymph nodes. A <strong>local</strong> treatment."),
    ("Medical oncology", "Chemotherapy, immunotherapy, targeted drugs, and hormone therapy. A <strong>systemic</strong> treatment that reaches the whole body."),
    ("Radiation oncology", "Treats a chosen region with radiation instead of a scalpel. A <strong>local</strong> treatment that can reach places that are hard or risky to operate on."),
])}
<p>Most patients receive more than one of these. The doctors often meet as a group, called a <strong>tumor board</strong>, to plan the order. Radiation can be the main treatment, it can come before or after surgery, it can be given at the same time as chemotherapy, or it can be given only to relieve a symptom such as pain. The job radiation is doing for a patient is called the <strong>treatment intent</strong>, and you will learn to name it in <em>The Rad Onc Consult</em>.</p>

<h3 id='workflow'>A Patient's Journey Through Radiation</h3>
<p>Every patient who receives radiation goes through the same steps, in the same order. If you ever feel lost in clinic, ask yourself which step the patient is on.</p>
{vflow([
    ("Before treatment", [
        ("Consult", "The first visit. The radiation oncologist learns the patient's story, examines them, and decides whether radiation will help and what the goal is."),
        ("Simulation", "The patient lies in the exact position they will be treated in, often with a custom mask or cushion, and has a CT scan. <strong>Nothing is treated at simulation.</strong> The scan is used to build the plan."),
        ("Contouring", "On that CT scan, the doctor outlines the tumor, the nearby areas where cancer cells may be hiding, and the healthy organs that need protecting."),
        ("Planning", "A dosimetrist and a physicist design the beams so the tumor gets a high dose and the healthy organs get as little as possible."),
        ("Quality assurance", "The doctor approves the plan, and the physics team checks that the machine will deliver it exactly as designed."),
    ]),
    ("During treatment", [
        ("Treatment", "The patient comes in for each treatment session. Before each one, a quick scan on the machine confirms they are lined up correctly."),
        ("Weekly visits", "About once a week, the doctor checks on side effects, weight, and how the patient is coping. These are called on-treatment visits."),
    ]),
    ("After treatment", [
        ("Follow-up", "Visits over months and years to see how the cancer responded and to manage any long-term side effects."),
    ]),
])}
<p>For a typical cure-focused course, the steps from simulation to the first treatment take about one to two weeks. When a patient needs help urgently, for example because a tumor is pressing on the spinal cord, all of these steps can happen in a single day.</p>
<div class='big-idea'>Consult, simulation, contouring, planning, quality assurance, treatment, weekly visits, follow-up. Knowing this sequence matters more than knowing how the machine works.</div>

<h3 id='dose'>Measuring Radiation: Gray, Fractions, and Courses</h3>
<p>A medicine is measured in milligrams. Radiation is measured in <strong>gray (Gy)</strong>. One gray means one joule of energy absorbed by each kilogram of tissue. You will never need that definition at the bedside, but you will hear "Gy" all day long.</p>
<p>Radiation is almost never given all at once. It is split into smaller daily treatments, and a few words describe how:</p>
<dl class='spec-list'>
<div class='spec-row'><dt>Total dose</dt><dd>All the radiation for the whole course, in Gy.</dd></div>
<div class='spec-row'><dt>Fraction</dt><dd>One treatment session. Most patients receive one fraction each weekday.</dd></div>
<div class='spec-row'><dt>Dose per fraction</dt><dd>The total dose divided by the number of fractions.</dd></div>
<div class='spec-row'><dt>Treatment course</dt><dd>All the fractions together, which can last from a single day to about eight weeks.</dd></div>
</dl>
{script("Read it like this", "&ldquo;60 Gy in 30 fractions&rdquo; means 2 Gy each day, Monday through Friday, for about six weeks.")}
<p>You will hear four common patterns:</p>
{cards([
    ("Conventional", "About 1.8-2 Gy per fraction, usually over five to eight weeks."),
    ("Hypofractionated", "Fewer, larger fractions. For example, 40 Gy in 15 fractions for breast cancer."),
    ("Stereotactic (SRS or SBRT)", "One to five very large, very precise fractions aimed at a small target."),
    ("Single fraction", "Just one treatment. For example, 8 Gy once for a painful bone metastasis."),
], numbered=False)}
<details class='reveal quiz'>
<summary>Try it: read three prescriptions<span class='chev'>&#9662;</span></summary>
<div class='reveal-body'>
<p>Work out the dose per fraction before you look.</p>
<ul>
<li><strong>50.4 Gy in 28 fractions</strong> = 1.8 Gy per fraction (conventional).</li>
<li><strong>40 Gy in 15 fractions</strong> = about 2.67 Gy per fraction (hypofractionated).</li>
<li><strong>54 Gy in 3 fractions</strong> = 18 Gy per fraction (stereotactic).</li>
</ul>
<p>Two courses with the same total dose are <em>not</em> the same if the fraction size is different. The next reading explains why.</p>
</div>
</details>

<h3 id='why-fractions'>Why Split the Dose?</h3>
<p>Picture the dose needed to destroy a tumor delivered in one single blast. The tumor would be gone, but the healthy tissue around it would be badly damaged too. Splitting the dose into small daily pieces changes the picture. Healthy cells are good at repairing themselves overnight, while cancer cells are worse at it. Each day the healthy tissue recovers a little more than the tumor does, and after weeks of treatment the tumor has fallen far behind.</p>
<div class='big-idea'>Fractions give healthy tissue time to repair between treatments while the damage to the tumor adds up.</div>
<p>This is why a cure-focused course often lasts weeks, and why missed treatments matter. Stereotactic treatment is the exception. When the target is small and the beams can hit it very precisely, very little healthy tissue sits in the high-dose area, so a few large fractions become safe.</p>

<h3 id='path'>Where the Next Five Readings Go</h3>
<p>These six readings tell one story. Each disease-site module later applies the same story to one kind of cancer.</p>
{table(["Reading", "The question it answers"], [
    ["01 Radiation 101", "What happens when a patient receives radiation?"],
    ["02 How Radiation Works", "Why does radiation kill cancer cells, and why are healthy tissues hurt too?"],
    ["03 Radiation Modalities", "What machines and techniques does a radiation oncologist use?"],
    ["04 How to Give a Presentation", "How do I tell the team about a patient?"],
    ["05 The Rad Onc Consult", "How do we decide whether, and how, to use radiation?"],
    ["06 Treatment Planning", "How does that decision become a safe radiation plan?"],
    ["Disease sites", "The same steps, applied to each cancer."],
])}

{summary([
    "Radiation oncology is a local treatment that works alongside surgery and systemic therapy, and the plan is often made together at a tumor board.",
    "Every patient follows the same path: consult, simulation, contouring, planning, quality assurance, treatment, weekly visits, and follow-up.",
    "Simulation is a planning CT scan in the treatment position, not the first treatment.",
    "Dose is measured in gray, and a prescription gives the total dose and the number of fractions, so 60 Gy in 30 fractions is 2 Gy per fraction.",
    "Splitting the dose into fractions lets healthy tissue repair between treatments while the damage to the tumor adds up.",
])}
"""

# ---------------------------------------------------------------------------
# 02  HOW RADIATION WORKS
# ---------------------------------------------------------------------------
HOWRT = f"""
<p>When a beam of radiation passes through the body, it does not burn or cut anything. It leaves behind tiny packets of energy inside the cells it crosses. That energy breaks DNA. This reading follows what happens next, and explains two things every student should understand: why radiation kills cancer cells, and why healthy tissue gets hurt along the way.</p>

<h3 id='sequence'>From a Beam to a Shrinking Tumor</h3>
<div class='flow-diagram'>
<div class='flow-step'><div class='flow-num'>1</div><div class='flow-label'>Radiation leaves energy in the cell</div></div>
<div class='flow-arrow'>&rarr;</div>
<div class='flow-step'><div class='flow-num'>2</div><div class='flow-label'>DNA is damaged</div></div>
<div class='flow-arrow'>&rarr;</div>
<div class='flow-step'><div class='flow-num'>3</div><div class='flow-label'>The cell can no longer divide</div></div>
<div class='flow-arrow'>&rarr;</div>
<div class='flow-step'><div class='flow-num'>4</div><div class='flow-label'>The tumor shrinks</div></div>
</div>
<p>Most cells hit by radiation do not die right away. They keep working until they try to divide. Then the broken DNA stops them, and they die. Because of this delay, tumors usually shrink over <strong>weeks to months</strong>, and a scan taken the day treatment ends can make the treatment look less effective than it really was.</p>

<h3 id='dna'>How Radiation Breaks DNA</h3>
<p>Radiation can damage DNA in two ways.</p>
{compare(
    ("Direct", "The radiation hits the DNA itself", "<p>The energy lands right on the DNA molecule and breaks it.</p>"),
    ("Indirect", "The radiation hits water first", "<p>Cells are mostly water. Radiation splits water molecules into <strong>free radicals</strong>, which are very reactive and break the DNA nearby. With the X-rays used for most treatments, this is how most of the damage happens.</p>"),
)}
<p>The most dangerous injury is a <strong>double-strand break</strong>, where both sides of the DNA ladder are cut at the same spot. Cells have a hard time fixing these breaks correctly, and an unfixed break is what finally kills the cell when it tries to divide.</p>
<p>Oxygen makes this damage stick. When oxygen is present, the broken DNA is harder to repair. This is why tumors with poor blood supply, which are low in oxygen, are harder to control with radiation.</p>

<h3 id='normal-tissue'>Why Healthy Tissue Gets Hurt</h3>
<p>Radiation cannot tell a cancer cell from a healthy one. Every cell in the beam's path takes some damage. This is why side effects happen <strong>only where the radiation goes</strong>: a patient treated to the pelvis may get diarrhea, but not mouth sores. Tiredness is the one side effect that can appear no matter which part of the body is treated.</p>
<p>Side effects come in two kinds, and they appear at different times:</p>
{compare(
    ("During treatment and a few weeks after", "Acute side effects", "<p>These appear in tissues whose cells divide quickly, such as skin, the lining of the mouth and gut, and bone marrow. Examples are skin redness, mouth sores, and diarrhea. They usually heal once treatment ends.</p>"),
    ("Months to years later", "Late side effects", "<p>These appear in tissues that renew slowly, and in small blood vessels. Examples are scarring (fibrosis), narrowing of a tube such as the esophagus, dry mouth, and nerve damage. They are often permanent.</p>"),
)}
<div class='pearl'>
<strong>Clinical Pearl</strong>
<p>Acute side effects are what you will ask about at weekly visits. Late side effects are the reason doctors set strict dose limits for healthy organs, because those are the effects patients live with for the rest of their lives.</p>
</div>

<h3 id='four-rs'>The 4 R's: Why Splitting the Dose Works</h3>
<p>The first reading said that fractions give healthy tissue time to recover. Radiation biologists describe what happens between fractions with four words that all start with R.</p>
<div class='card-grid'>
<div class='card'><div class='card-num'>1</div><div class='card-title'>Repair</div><p>Healthy cells fix much of their damage in the hours between fractions.</p><p class='card-use'><em>In the clinic:</em> this is the main reason we split the dose, and why two treatments on the same day are spaced at least about six hours apart.</p></div>
<div class='card'><div class='card-num'>2</div><div class='card-title'>Repopulation</div><p>Cells, including tumor cells, keep dividing and replacing themselves during the course.</p><p class='card-use'><em>In the clinic:</em> breaks in treatment give the tumor time to grow back, so missed days matter, especially for fast-growing cancers such as head and neck and cervix.</p></div>
<div class='card'><div class='card-num'>3</div><div class='card-title'>Redistribution</div><p>Cells are more sensitive to radiation at some points in their growth cycle than others.</p><p class='card-use'><em>In the clinic:</em> cells that survive one fraction may be caught at a more sensitive point by the next one.</p></div>
<div class='card'><div class='card-num'>4</div><div class='card-title'>Reoxygenation</div><p>Low-oxygen tumor cells resist radiation. As the tumor shrinks, oxygen reaches more of them.</p><p class='card-use'><em>In the clinic:</em> this is one reason large tumors are harder to control, and one reason doctors encourage patients to stop smoking.</p></div>
</div>
<div class='big-idea'>Splitting the dose works because tumors and healthy tissues recover differently between fractions.</div>

<h3 id='alpha-beta'>Why the Size of Each Fraction Matters</h3>
<p>Some tissues care a great deal about how big each fraction is. Others care much less. Radiation oncologists describe this with a number called the <strong>&alpha;/&beta; ratio</strong> (said "alpha-beta"). You will not need to calculate it, but the idea is worth knowing.</p>
{compare(
    ("High &alpha;/&beta;", "Less sensitive to fraction size", "<p>Most tumors, and tissues that divide quickly.</p>"),
    ("Low &alpha;/&beta;", "More sensitive to fraction size", "<p>Healthy tissues that show late side effects, and a few tumors, most famously <strong>prostate cancer</strong>.</p>"),
)}
<p>Two things follow. First, large fractions raise the risk of late side effects in healthy tissue that sits in the high-dose area, so big fractions demand very precise aim. Second, a tumor with a low &alpha;/&beta;, such as prostate cancer, is hit especially hard by large fractions. This helps explain why prostate cancer (and breast cancer) can often be treated with fewer, larger fractions.</p>

<details class='reveal'>
<summary>Deeper dive (optional): oxygen, LET, RBE, BED<span class='chev'>&#9662;</span></summary>
<div class='reveal-body'>
<ul>
<li><strong>Oxygen effect:</strong> cells with no oxygen need about two to three times the X-ray dose to be killed (the oxygen enhancement ratio).</li>
<li><strong>LET (linear energy transfer):</strong> how densely a particle leaves energy along its path. X-rays and electrons are low LET; heavy ions such as carbon are high LET and depend less on oxygen.</li>
<li><strong>RBE (relative biological effectiveness):</strong> how much more damaging one kind of radiation is than X-rays. Protons are usually counted as 1.1 times as effective.</li>
<li><strong>BED and EQD2:</strong> formulas that let doctors compare schedules with different fraction sizes on one scale. Recognize the names; you will not be asked to calculate them early on.</li>
<li><strong>A fifth R:</strong> some tumors, such as lymphoma and seminoma, are simply much more sensitive to radiation than others.</li>
</ul>
</div>
</details>

{summary([
    "Radiation leaves energy in cells, which breaks DNA, so the cells die when they try to divide and the tumor shrinks over weeks to months.",
    "With X-rays, most DNA damage is indirect, through free radicals made from water, and double-strand breaks are the hardest for cells to repair.",
    "Healthy tissue in the beam is damaged the same way, causing acute side effects in fast-dividing tissue and late side effects that are often permanent.",
    "The four R's (repair, repopulation, redistribution, reoxygenation) explain why splitting the dose helps healthy tissue more than the tumor.",
    "Tissues with a low &alpha;/&beta; ratio, such as prostate cancer, are more sensitive to fraction size, which is why they can be treated with fewer, larger fractions.",
])}
"""

# ---------------------------------------------------------------------------
# 03  RADIATION MODALITIES
# ---------------------------------------------------------------------------
DEPTH_DOSE_SVG = """<figure>
<svg viewBox='0 0 600 260' xmlns='http://www.w3.org/2000/svg' role='img' aria-labelledby='depthdosetitle'>
<title id='depthdosetitle'>Schematic relative dose versus tissue depth for photons, electrons, and protons</title>
<line x1='50' y1='20' x2='50' y2='210' stroke='var(--ink-faint)' stroke-width='1.5'/>
<line x1='50' y1='210' x2='580' y2='210' stroke='var(--ink-faint)' stroke-width='1.5'/>
<text x='16' y='24' font-size='11' fill='var(--ink-faint)' font-family='var(--font-mono)'>Dose</text>
<text x='500' y='232' font-size='11' fill='var(--ink-faint)' font-family='var(--font-mono)'>Depth &rarr;</text>
<path d='M50,120 C90,45 130,55 190,72 C300,100 420,140 580,168' fill='none' stroke='var(--accent)' stroke-width='3' stroke-linecap='round'/>
<path d='M50,200 C70,60 100,50 130,90 C150,120 165,160 180,205' fill='none' stroke='var(--accent-2)' stroke-width='3' stroke-linecap='round'/>
<path d='M50,195 C160,190 300,190 360,185 C385,178 400,30 420,25 C438,70 445,205 460,208 C500,209 540,209 580,209' fill='none' stroke='color-mix(in srgb, var(--accent) 45%, var(--accent-2))' stroke-width='3' stroke-linecap='round'/>
</svg>
<figcaption>
Schematic dose-versus-depth curves (not to scale). <span style='color:var(--accent);font-weight:700;'>&#9679; Photons</span> travel deep and keep going past the target. <span style='color:var(--accent-2);font-weight:700;'>&#9679; Electrons</span> stay near the surface, then stop. <span style='color:color-mix(in srgb, var(--accent) 45%, var(--accent-2));font-weight:700;'>&#9679; Protons</span> leave little dose on the way in, most at the Bragg peak, then stop.
</figcaption>
</figure>"""

MODALITIES = f"""
<p>A radiation oncologist has a small set of tools. Each one is an answer to a simple question, and the questions come in a natural order. Where is the radiation coming from? What machine makes it? How do we shape it to fit the tumor? How do we deliver it? How do we make sure we hit the target every day? This reading walks through those questions one at a time.</p>

<h3 id='big-split'>Where Does the Radiation Come From?</h3>
<p>The first question is where the source of radiation sits. There are only two answers.</p>
{compare(
    ("Source outside the body", "External beam radiation therapy (EBRT)", "<p>A large machine outside the body aims beams of radiation at the tumor. The patient lies on a couch, the machine does the work, and nothing touches the patient. This is most of what you will see, and most of this reading.</p>"),
    ("Source inside or next to the tumor", "Brachytherapy", "<p>A small radioactive source is placed inside the body, right in or next to the tumor. Because the dose drops off quickly with distance, the tumor gets a very high dose while tissue a short distance away is spared. It is covered at the end of this reading.</p>"),
)}
<div class='big-idea'>External beam brings the radiation to the patient from outside. Brachytherapy puts the source right next to the tumor.</div>

<h3 id='linac'>The Machine: the Linac and the MLC</h3>
<p>Almost all external beam treatment is given by a machine called a <strong>linear accelerator</strong>, or <strong>linac</strong> (said "LIN-ack"). It speeds up electrons and uses them to make high-energy X-rays, which doctors call <strong>photons</strong>. It can also send the electrons out directly for treating tumors near the skin.</p>
<p>Two parts of the linac matter most:</p>
<ul>
<li>The <strong>gantry</strong> is the large arm that holds the head of the machine. It rotates in a full circle around the patient, so the beam can come from any direction.</li>
<li>The <strong>multileaf collimator (MLC)</strong> sits in the head of the machine. It is made of dozens of thin metal leaves that slide in and out, controlled by a computer. Together they form an opening in the shape of the tumor. Radiation passes through the opening, and the leaves block it everywhere else.</li>
</ul>
{linac_mlc()}
<p>Keep the MLC in mind. The techniques in the next two sections are different ways of moving these leaves and this gantry.</p>

<h3 id='shape'>How Do We Shape the Dose?</h3>
<p>Once we know we are using a linac, the next question is how closely the dose needs to fit the tumor. A tumor sitting in open space is easy to treat. A tumor curled around the spinal cord is much harder, because the cord can only tolerate a limited dose. There are two main ways to shape the dose.</p>
<p><strong>3D-CRT</strong> (three-dimensional conformal radiation therapy) is the simpler one. A few beams come from different directions, and the MLC shapes each beam to the outline of the tumor. Each beam is the same strength all the way across. Where the beams overlap, the dose adds up, and the tumor gets a high dose. This works well for simple shapes and for many palliative treatments, where the goal is quick relief of a symptom.</p>
<p><strong>IMRT</strong> (intensity-modulated radiation therapy) adds one important idea: the strength of each beam can <strong>vary across the beam</strong>. The MLC leaves move during the treatment, so some parts of the beam deliver more dose and other parts deliver less. A computer works out the pattern. The result is a high-dose region that can bend around a healthy organ, wrapping the tumor while carving away from the spinal cord, the salivary glands, or the rectum.</p>
{crt_vs_imrt()}
{compare(
    ("Simpler targets and palliation", "3D-CRT", "<ul><li>A few fixed beams</li><li>Each beam the same strength across</li><li>Quick to plan and deliver</li></ul>"),
    ("Complex targets next to organs at risk", "IMRT", "<ul><li>Strength varies within each beam</li><li>Dose curves around healthy organs</li><li>Common for head and neck, prostate, and many others</li></ul>"),
)}

<h3 id='deliver'>How Do We Deliver It?</h3>
<p>The last question about the beams is how the machine actually gives them. With 3D-CRT and classic IMRT, the gantry stops at a few fixed angles, and a beam is given from each one.</p>
<p><strong>VMAT</strong> (volumetric modulated arc therapy) is a kind of IMRT. Instead of stopping at fixed angles, the gantry <strong>sweeps around the patient in an arc while the beam stays on</strong>. As it moves, the MLC leaves keep reshaping the beam and the strength keeps changing. VMAT reaches the same goal as IMRT, a dose that hugs the tumor, and it usually does so faster. Today it is one of the most common ways radiation is given.</p>
{delivery()}
<div class='big-idea'>3D-CRT shapes the beams. IMRT also varies their strength. VMAT does what IMRT does while the gantry rotates.</div>

<h3 id='igrt'>How Do We Hit the Same Spot Every Day?</h3>
<p>A beautiful plan is useless if the patient is lying a centimeter to the left. People breathe, organs shift, and no one lies in exactly the same position twice. So before each treatment, the team takes a quick scan on the machine, usually a <strong>cone-beam CT</strong>, and compares it with the planning scan. If the target is a few millimeters off, the couch moves the patient to line it up. This is called <strong>image-guided radiation therapy (IGRT)</strong>. For prostate cancer, small metal markers called <strong>fiducials</strong> are sometimes placed in the prostate so it is easy to see on these daily scans.</p>
{igrt()}
<div class='big-idea'>Image guidance answers one question before every treatment: is the target where the plan expects it to be today?</div>

<h3 id='stereotactic'>Stereotactic Treatment: SRS and SBRT</h3>
<p>Everything so far describes treatments given in many daily fractions. Stereotactic treatment is a different idea. It gives a <strong>very high dose in just one to five treatments</strong> to a <strong>small, well-defined target</strong>. Many beams or arcs come from different directions and all cross at the target. Each beam on its own is weak, but where they all meet the dose is very high, and it falls off steeply just outside the target.</p>
{stereotactic()}
{compare(
    ("Brain", "SRS: stereotactic radiosurgery", "<p>Despite the name, there is no surgery and no incision. Common uses:</p><ul><li>Brain metastases</li><li>Vestibular schwannoma (a benign tumor of the hearing nerve)</li><li>Arteriovenous malformations (AVMs)</li></ul>"),
    ("Body", "SBRT: stereotactic body radiation therapy", "<p>The same idea used outside the brain (also called SABR). Common uses:</p><ul><li>Early-stage lung cancer</li><li>A small number of metastases (oligometastases)</li><li>Spine metastases</li></ul>"),
)}
<p>Because the margins are so small and the dose is so high, a miss of even a few millimeters could underdose the tumor or overdose a nearby organ. That is why stereotactic patients get extra-careful immobilization, attention to breathing motion, and image guidance before every treatment. You may hear the names of specific machines, such as Gamma Knife or CyberKnife. They are all ways of giving stereotactic radiation.</p>

<h3 id='particles'>Photons, Electrons, and Protons</h3>
<p>So far we have talked about how the beams are shaped and aimed. A separate question is what the beam is made of. Each kind of particle leaves its dose at a different depth in the body.</p>
{cards([
    ("Photons", "High-energy X-rays from the linac, used for most treatments. They travel deep and keep going out the other side of the patient, which is called the <strong>exit dose</strong>. That is why deep tumors are treated with several beams that overlap at the target."),
    ("Electrons", "Also made by the linac. They give their dose near the surface and then stop within a few centimeters. Used for skin cancers, scars, and other shallow targets."),
    ("Protons", "Made by a different, much larger machine. They leave little dose on the way in, deposit most of their energy at a set depth called the <strong>Bragg peak</strong>, and then stop. There is no exit dose."),
])}
{DEPTH_DOSE_SVG}

<h3 id='protons'>Protons: Useful, but Not Automatically Better</h3>
<p>Because protons stop at the Bragg peak, they can spare the tissue behind the tumor. That matters most for <strong>children</strong>, whose growing tissues are especially sensitive to late effects, for <strong>treatment of the whole brain and spine</strong>, and for some tumors pressed against critical structures at the base of the skull. Protons also have drawbacks: small errors in where they stop, sensitivity to changes in the patient's body during treatment, and high cost with limited access. For many adult cancers, it is not yet clear that protons lead to better results than a modern photon plan.</p>
<div class='pearl'>
<strong>Clinical Pearl</strong>
<p>When someone says protons are better, ask: better than which photon plan, for which organ, and does that difference change something the patient will actually feel?</p>
</div>

<h3 id='brachytherapy'>Brachytherapy: Putting the Source Next to the Tumor</h3>
<p>Now back to the other branch from the very first question. In brachytherapy (from the Greek word for "short," as in short distance), the radiation source goes inside the body. It is a <strong>procedure</strong>: an applicator, thin tubes, or tiny seeds are placed, often under anesthesia, and then the dose is planned around them. Two questions describe any implant.</p>
{compare(
    ("How is it placed?", "Intracavitary or interstitial", "<p><strong>Intracavitary:</strong> an applicator sits inside a body cavity, such as the uterus and vagina for cervical cancer.</p><p><strong>Interstitial:</strong> needles, tubes, or seeds go directly into the tissue, as in the prostate.</p>"),
    ("How fast is the dose given?", "LDR or HDR", "<p><strong>Low dose rate (LDR):</strong> a weak source gives its dose slowly. The classic example is permanent seeds left in the prostate.</p><p><strong>High dose rate (HDR):</strong> a strong source travels into the applicator for a few minutes and is then <strong>removed</strong>. Common for cervical and uterine cancer.</p>"),
)}
<div class='pearl'>
<strong>Pearl: Cervical Cancer</strong>
<p>When cervical cancer is treated with radiation instead of surgery, brachytherapy is <strong>essential</strong>. Simply giving more external beam cannot replace it, because nothing else puts such a high dose on the cervix while sparing the bladder and rectum right next to it.</p>
</div>

<h3 id='when'>Putting It Together</h3>
{table(["Tool", "Think of it when", "Classic examples"], [
    ["<strong>3D-CRT</strong>", "The shape is simple or the goal is quick symptom relief", "A painful bone metastasis, the whole brain"],
    ["<strong>IMRT / VMAT</strong>", "The target is complex and close to healthy organs", "Head and neck, prostate, anal cancer"],
    ["<strong>SRS</strong>", "A small target in the brain", "Brain metastases, vestibular schwannoma"],
    ["<strong>SBRT</strong>", "A small target in the body", "Early lung cancer, a few metastases, spine metastases"],
    ["<strong>Electrons</strong>", "A target near the surface", "Skin cancer, a surgical scar"],
    ["<strong>Protons</strong>", "Sparing tissue behind the target may really matter", "Children's tumors, the whole brain and spine, skull base"],
    ["<strong>Brachytherapy</strong>", "The source can be placed in or next to the tumor", "Cervix, prostate, the top of the vagina after hysterectomy"],
])}
<p>These are tendencies, not rules. The same cancer can be treated with different tools depending on the patient's anatomy, the goal, and what the hospital has.</p>

<div class='quiz-carousel' data-quiz-set='modalities-pick'></div>

{summary([
    "Every tool starts with one split: external beam aims radiation from a machine outside the body, and brachytherapy places the source inside or next to the tumor.",
    "The linac makes the beam, the gantry rotates it around the patient, and the multileaf collimator shapes it to the tumor.",
    "3D-CRT shapes the beams, IMRT also varies their strength so the dose can curve around healthy organs, and VMAT does the same while the gantry rotates.",
    "Image guidance before each treatment checks that the target is where the plan expects it, and SRS (brain) and SBRT (body) give very high doses in a few treatments to small targets.",
    "Photons travel deep and exit the body, electrons stay shallow, and protons stop at the Bragg peak, which helps in selected cases but is not automatically better.",
])}
"""

# ---------------------------------------------------------------------------
# 04  HOW TO GIVE A PRESENTATION
# ---------------------------------------------------------------------------
PRESENTATION = f"""
<p>In the hospital, doctors share information about patients in a short, organized speech called a <strong>presentation</strong>. A student sees a new patient, gathers the story, and then tells it to the attending physician in a minute or two. Done well, the attending can picture the patient and the plan without opening the chart.</p>
<p>A radiation oncology presentation has a special shape. It is short, it says the cancer's stage out loud, and it ends with a recommendation about radiation. This reading builds one presentation, piece by piece, for one patient. The next reading, <em>The Rad Onc Consult</em>, is about the thinking behind it.</p>

<h3 id='one-rule'>The One Rule: Think Before You Speak</h3>
<p>It is easy to read the referring doctor's note out loud, including their conclusions, without doing any thinking of your own. Try not to. Look at the scans yourself, work out the stage, and come up with your own idea of the plan before you present. You will sometimes be wrong, and that is completely expected. The point is to show how you reasoned.</p>
{script("Sounds like", "&ldquo;I would stage him as cT3bN1M0. My thought was chemoradiation before surgery, although I was not sure whether a shorter course of radiation would also be reasonable.&rdquo;")}

<h3 id='template'>The Presentation Template</h3>
<p>The same eight parts work for every new patient, no matter the cancer:</p>
<div class='flow-diagram'>
<div class='flow-step'><div class='flow-num'>1</div><div class='flow-label'>One-liner</div></div>
<div class='flow-arrow'>&rarr;</div>
<div class='flow-step'><div class='flow-num'>2</div><div class='flow-label'>Story so far</div></div>
<div class='flow-arrow'>&rarr;</div>
<div class='flow-step'><div class='flow-num'>3</div><div class='flow-label'>Pathology</div></div>
<div class='flow-arrow'>&rarr;</div>
<div class='flow-step'><div class='flow-num'>4</div><div class='flow-label'>Imaging</div></div>
</div>
<div class='flow-connector'>&darr;</div>
<div class='flow-diagram'>
<div class='flow-step'><div class='flow-num'>5</div><div class='flow-label'>Stage</div></div>
<div class='flow-arrow'>&rarr;</div>
<div class='flow-step'><div class='flow-num'>6</div><div class='flow-label'>Treatment so far</div></div>
<div class='flow-arrow'>&rarr;</div>
<div class='flow-step'><div class='flow-num'>7</div><div class='flow-label'>Assessment</div></div>
<div class='flow-arrow'>&rarr;</div>
<div class='flow-step'><div class='flow-num'>8</div><div class='flow-label'>Radiation recommendation</div></div>
</div>
<p>Let us build it for one patient: <strong>Mr. K, a 64-year-old man with newly diagnosed rectal cancer.</strong> (He is a made-up patient, used only for teaching.)</p>

<h4>1. One-liner</h4>
<p>One sentence that tells the room <strong>who the patient is, what cancer they have, how far it has spread, and why they are here</strong>.</p>
{script("Sounds like", "&ldquo;Mr. K is a 64-year-old man with newly diagnosed cT3bN1M0 low rectal adenocarcinoma, referred to us to consider radiation before surgery.&rdquo;")}
<p>After one sentence, the attending already knows the disease, the stage, and the question.</p>

<h4>2. The story so far</h4>
<p>Doctors call this the <strong>history of present illness</strong>, or HPI. It tells how the cancer was found and what has happened since. Keep only the facts that change the <strong>diagnosis</strong>, the <strong>stage</strong>, the <strong>treatment</strong>, or the <strong>safety of radiation</strong>.</p>
<div class='big-idea'>Before each detail, ask: would this fact change what we do? If not, it can probably be left out.</div>
{compare(
    ("Keep", "Changes the plan", "<ul><li>How the cancer showed up, and symptoms that make it urgent (bleeding, blockage, pain)</li><li>How active and independent the patient is</li><li><strong>Any radiation in the past</strong>: where, how much, and when</li><li>Things that make radiation riskier, such as certain autoimmune diseases, inflammatory bowel disease before pelvic radiation, a pacemaker, pregnancy, or being unable to lie flat</li><li>What the patient hopes for, such as keeping an organ</li></ul>"),
    ("Cut", "Does not change the plan", "<ul><li>Every chemotherapy date and dose change</li><li>The full medication list</li><li>Unrelated hospital stays</li><li>The radiology report, read word for word</li></ul>"),
)}
<p>The most common mistake is a very long chemotherapy history. Sum it up in one sentence and spend your time on what the radiation team needs to know.</p>

<h4>3. Pathology</h4>
<p>What the biopsy showed: the type of cancer, how abnormal the cells look (the grade), and any special markers <strong>that change treatment</strong>. Not the whole report.</p>
{script("Sounds like", "&ldquo;Biopsy showed moderately differentiated adenocarcinoma, mismatch-repair proficient.&rdquo;")}
<p>Why mention mismatch repair? Because a rectal cancer that is <strong>mismatch-repair deficient</strong> often responds to immunotherapy, which can change the whole plan.</p>

<h4>4. Imaging</h4>
<p>Use one pattern for every scan: <strong>the date, the type of scan, the key finding, and what it means for treatment.</strong></p>
{script("Sounds like", "&ldquo;An MRI of the pelvis on 9/12 showed a low rectal tumor growing through the bowel wall, 2 mm from the edge of the surgical plane, with tumor in a nearby vein, which puts him at high risk of the cancer coming back.&rdquo;")}
<p>That is far more useful than just "MRI showed a tumor." Look at the images yourself so you can point to what you are describing.</p>

<h4>5. Stage</h4>
<p>The <strong>stage</strong> describes how far the cancer has spread, usually with the TNM system: <strong>T</strong> for the size and depth of the tumor, <strong>N</strong> for lymph nodes, and <strong>M</strong> for spread to distant organs (metastasis). A small letter in front tells where the stage came from: c for clinical (exams and scans), p for pathologic (after surgery), and yp for after treatment that came before surgery. Say the stage out loud.</p>
{script("Sounds like", "&ldquo;I would stage him as cT3bN1M0, stage IIIB.&rdquo;")}

<h4>6. Treatment so far</h4>
<p>Any surgery, chemotherapy, or radiation the patient has already had, and how the cancer responded. For Mr. K: no treatment yet. He has already met medical oncology and the colorectal surgeons.</p>

<h4>7. Assessment</h4>
<p>This is the most important part. Pull the story together in a sentence or two and say <em>why</em> it matters.</p>
{script("Sounds like", "&ldquo;Overall, this is a high-risk, locally advanced rectal cancer. The tumor is low, close to the surgical plane, and has spread to nearby nodes, so surgery alone would carry a high chance of leaving cancer behind.&rdquo;")}

<h4>8. Radiation recommendation</h4>
<p>End by answering four questions:</p>
{cards([
    ("What?", "The radiation you recommend, and its goal."),
    ("Why?", "The problem it solves for this patient."),
    ("How?", "What you would treat, and what you would protect."),
    ("What are the risks?", "The main short-term and long-term side effects."),
])}
{script("Sounds like", "&ldquo;I would recommend chemoradiation to the pelvis before surgery because the tumor is low and close to the surgical plane. I would treat the tumor and the nearby lymph nodes while protecting the small bowel, the bladder, and the hip bones. The main risks are diarrhea, bladder irritation, skin soreness, and tiredness, along with possible long-term bowel and sexual side effects.&rdquo;")}
<p>Finish with anything still undecided. For Mr. K, that might be whether he could avoid surgery altogether if the tumor disappears completely.</p>

<div class='worked-example'>
<span class='worked-example-label'>Worked Example: The Whole Presentation (about 90 seconds, made-up patient)</span>
<p>&ldquo;Mr. K is a 64-year-old man with newly diagnosed cT3bN1M0 low rectal adenocarcinoma, referred to us to consider radiation before surgery.</p>
<p>He came in with three months of rectal bleeding and a change in his bowel habits. Colonoscopy found a mass 5 cm from the anal opening. He is fully active, has never had pelvic radiation, does not have inflammatory bowel disease, and has no hip replacements.</p>
<p>Biopsy showed moderately differentiated adenocarcinoma, mismatch-repair proficient.</p>
<p>An MRI of the pelvis on 9/12 showed a low rectal tumor through the bowel wall, 2 mm from the surgical plane, with tumor in a nearby vein and two suspicious lymph nodes. CT of the chest, abdomen, and pelvis showed no spread to distant organs. I looked at the MRI myself and agree with the report.</p>
<p>I would stage him as cT3bN1M0, stage IIIB. He has not started treatment yet.</p>
<p>Overall, this is a high-risk, locally advanced rectal cancer because the tumor is low and close to the surgical plane.</p>
<p>I would recommend chemoradiation to the pelvis before surgery, treating the tumor and nearby nodes while protecting the small bowel, bladder, and hip bones. The main risks are diarrhea, bladder irritation, skin soreness, and tiredness, with possible long-term bowel and sexual effects. The open question is whether he could avoid surgery if the tumor disappears completely.&rdquo;</p>
</div>

<details class='reveal quiz'>
<summary>Try it yourself: build a one-liner<span class='chev'>&#9662;</span></summary>
<div class='reveal-body'>
<p><strong>Case (made-up):</strong> A 58-year-old woman had a lumpectomy and a lymph node biopsy for a 1.7 cm invasive ductal carcinoma of the left breast. The cancer has estrogen and progesterone receptors and no HER2, and 0 of 2 lymph nodes had cancer. She is referred for radiation. Write your one-liner before reading on.</p>
<p><strong>A strong answer:</strong> &ldquo;Ms. R is a 58-year-old woman with pT1c pN0 hormone receptor-positive, HER2-negative invasive ductal carcinoma of the left breast, after lumpectomy, referred to consider radiation after surgery.&rdquo;</p>
<p>Who, what, how far, and why we are here, all in one sentence.</p>
</div>
</details>

<h3 id='follow-up-otv'>Shorter Visits: Follow-Ups and Weekly Treatment Visits</h3>
<p>Not every visit is a new patient. These two kinds of visits are shorter, but the same rule applies: say only what changes what we do.</p>
{compare(
    ("Follow-up", "What has changed since we last saw them?", "<ol><li>One-liner with a time marker (&ldquo;4 months after breast radiation&rdquo;)</li><li>Any treatment since the last visit</li><li>How the cancer is doing: symptoms, exam, new scans</li><li>Side effects, and whether they are better or worse</li><li>Next step: keep watching, more tests, or a change in plan</li></ol>"),
    ("On-treatment visit", "How is treatment going right now?", "<ol><li>Where, what dose, and which fraction (&ldquo;fraction 12 of 15&rdquo;)</li><li>Symptoms and side effects, and whether they are getting worse</li><li>A focused exam, especially the skin in the treated area</li><li>Weight, blood tests if needed, and any missed treatments</li><li>Plan: continue, add supportive care, or change course</li></ol>"),
)}
<div class='worked-example'>
<span class='worked-example-label'>Worked Example: On-Treatment Visit (made-up patient)</span>
<p>&ldquo;Ms. R is on fraction 12 of 15 of radiation to the left breast and has not missed any treatments. She is a little tired and has mild pinkness of the skin, with no peeling or open areas, slowly increasing as expected. The plan is to continue treatment with gentle skin care, and to let her know the skin may look its worst a week or two after treatment ends before it heals.&rdquo;</p>
</div>
<div class='pearl'>
<strong>Useful Principle</strong>
<p>Side effects from radiation build up over time. A patient who feels fine at fraction 5 may feel much worse by fraction 20, and many side effects peak at the end of treatment or just after. At a weekly visit, your job is to look ahead to what is coming, not only to write down how the patient feels today.</p>
</div>

{summary([
    "Do your own thinking before you present: look at the scans, work out the stage, and form your own recommendation.",
    "Use one template for every new patient: one-liner, story so far, pathology, imaging, stage, treatment so far, assessment, and radiation recommendation.",
    "Before each detail, ask whether it would change what we do, and always mention any past radiation and anything that makes radiation riskier.",
    "Present each scan as the date, the type of scan, the key finding, and what it means for treatment, and say the stage out loud.",
    "End with a recommendation that answers what, why, how, and what the risks are, and keep follow-up and weekly visits focused on what has changed.",
])}
"""

# ---------------------------------------------------------------------------
# 05  THE RAD ONC CONSULT
# ---------------------------------------------------------------------------
CONSULT = f"""
<p>The presentation is how you <strong>tell</strong> the team about a patient. The consult is how you <strong>think</strong> about the patient. A <strong>consult</strong> is the first visit with the radiation oncologist, when the team decides whether radiation will help at all.</p>
<p>Almost any part of the body can be treated with radiation, so the question is never "can we radiate this?" The real question is: <strong>what problem would radiation solve for this patient, and is it the best way to solve it?</strong></p>

<h3 id='nine-questions'>Nine Questions for Every Consult</h3>
<p>Radiation oncologists work through the same questions for every new patient, whatever the cancer. They fall into three groups: understand the disease, make a decision, and check that the plan is safe.</p>
{vflow([
    ("Understand the disease", [
        ("Why was the patient sent to us?", "Read the referral question carefully. Is the hope for cure, or for relief of a symptom?"),
        ("What is the diagnosis?", "The type of cancer, how aggressive it looks, and any markers that matter."),
        ("Where is it?", "Which organ it started in, and what sits right next to it."),
        ("How far has it spread?", "The stage: only where it started, to nearby lymph nodes, or to distant organs."),
        ("What has already happened?", "Surgery, chemotherapy, and especially any <strong>radiation in the past</strong>, and how the cancer responded to each."),
    ]),
    ("Make a decision", [
        ("What is the goal of treatment?", "Cure, or relief of symptoms. This is the single most important word in the chart (see below)."),
        ("What are the other options?", "Surgery, medicines, watching closely, or a different kind of radiation."),
        ("What would radiation add?", "The specific problem radiation would solve for this patient."),
    ]),
    ("Check that it is safe", [
        ("What limits treatment?", "Healthy organs nearby, past radiation, and the patient's own health. <strong>Can we safely give the dose this problem needs?</strong>"),
    ]),
])}

<h3 id='intent'>The Goal of Treatment (Intent)</h3>
<p>Doctors call the goal of treatment its <strong>intent</strong>. It has two layers. The first is the big goal: <strong>cure</strong>, or <strong>relief of symptoms</strong> (palliation). The second is the specific role radiation plays in reaching that goal.</p>
{table(["Intent", "What it means", "Example"], [
    ["<strong>Curative</strong>", "Get rid of the cancer for good. The next three roles usually serve this goal.", "Any of the next three examples"],
    ["<strong>Definitive</strong>", "Radiation, often with chemotherapy, is the main treatment and replaces surgery.", "Chemoradiation for anal or cervical cancer"],
    ["<strong>Neoadjuvant</strong>", "Radiation <em>before</em> surgery, to shrink the tumor or make surgery more successful.", "Rectal cancer before surgery"],
    ["<strong>Adjuvant</strong>", "Radiation <em>after</em> surgery, to destroy cancer cells left behind.", "Breast radiation after a lumpectomy"],
    ["<strong>Consolidative</strong>", "Radiation after another treatment, usually chemotherapy, to control what is left.", "Radiation to a lymphoma mass still present after chemotherapy"],
    ["<strong>Oligometastatic</strong>", "Treating a few spots of spread, in selected patients, for long-term control.", "Stereotactic radiation to a few metastases alongside medicines"],
    ["<strong>Palliative</strong>", "Relieve symptoms or prevent problems, without aiming for cure.", "One treatment for a painful bone metastasis"],
])}
<div class='big-idea'>Name the goal before you name a dose. The goal decides how many side effects are acceptable, how long the course should be, and how aggressive the plan is.</div>
<div class='quiz-carousel' data-quiz-set='rad101-intents'></div>

<h3 id='alternatives'>Radiation Is Not Always the Answer</h3>
<p>A good consult compares radiation honestly with the other choices:</p>
{table(["The decision", "Example"], [
    ["Surgery or radiation as the main treatment", "Early prostate cancer; early cancer of the vocal cord; early lung cancer in someone too frail for surgery"],
    ["Radiation after surgery, or watching closely", "An older woman with a small, slow-growing breast cancer who is taking hormone therapy"],
    ["Radiation or medicines", "Cancer that has spread widely, where medicines treat everywhere and radiation treats only one spot"],
    ["Radiation now or later", "Radiation right after prostate surgery, or only if the cancer comes back"],
])}
<p>Then ask the key question:</p>
<div class='big-idea'>What problem is radiation solving?</div>
{cards([
    ("Destroy hidden cancer cells", "After surgery, in the area around the tumor or nearby lymph nodes."),
    ("Destroy a visible tumor", "Radiation as the main treatment."),
    ("Keep the cancer from coming back", "Lower the chance of it returning where it started."),
    ("Save an organ", "The voice box, anus, bladder, breast, and sometimes the rectum."),
    ("Stop bleeding", "From tumors of the bladder, rectum, lung, or cervix."),
    ("Relieve pain", "Most often from cancer that has spread to bone."),
    ("Protect the spinal cord", "When a tumor is pressing on it."),
    ("Treat a few spots of spread", "In carefully selected patients."),
], numbered=False)}

<h3 id='limits'>What Limits Treatment?</h3>
<p>Even when radiation would help, something may limit how much can be given:</p>
<ul>
<li><strong>Healthy organs nearby</strong>, such as the spinal cord, bowel, or optic nerves. Doctors call these <strong>organs at risk</strong>.</li>
<li><strong>Past radiation</strong> to the same area, because healthy tissue remembers the dose it has already had.</li>
<li><strong>The patient</strong>: how strong they are, whether they can lie still or hold their breath, certain autoimmune diseases, and their own wishes and practical needs.</li>
</ul>
<div class='big-idea'>Can we safely give the dose this problem needs? That question leads straight into Treatment Planning.</div>

<h3 id='worked'>Putting It Together: One Consult, Nine Answers</h3>
<div class='worked-example'>
<span class='worked-example-label'>Worked Example (made-up patient)</span>
<p>A 78-year-old man with severe emphysema has a 2 cm lung cancer in the outer part of his right upper lobe. A PET/CT scan shows no spread to lymph nodes or other organs. The lung surgeon feels his breathing is too poor for him to survive an operation.</p>
{table(["Question", "Answer"], [
    ["Why was he sent to us?", "To treat an early lung cancer with the goal of cure"],
    ["Diagnosis?", "Adenocarcinoma, confirmed by biopsy"],
    ["Where?", "The outer right upper lobe, away from the main airways"],
    ["How far has it spread?", "Not at all: cT1bN0M0 on PET/CT"],
    ["What has happened?", "Nothing yet, and no past chest radiation"],
    ["Goal?", "Cure"],
    ["Other options?", "Surgery (he is too frail), stereotactic radiation, or watching closely"],
    ["What would radiation add?", "It can destroy the tumor, with high rates of control"],
    ["What limits it?", "His weak lungs, the nearby chest wall, and breathing motion, which is handled with a special breathing CT scan"],
])}
<p><strong>Recommendation:</strong> stereotactic body radiation therapy (SBRT).</p>
</div>

<h3 id='in-the-room'>In the Room</h3>
<p>By the time you walk into the exam room, you should already know most of the story from the chart. Your job in the room is to <strong>check the story, fill in the gaps, and understand the person</strong>.</p>
<ul>
<li><strong>Check the history:</strong> how the cancer was found, what treatment happened and in what order, and especially any <strong>past radiation</strong>. Patients often correct the chart.</li>
<li><strong>Ask about symptoms now:</strong> pain, bleeding, trouble swallowing, weight loss, or new weakness. These may become targets for treatment or make it more urgent.</li>
<li><strong>Learn what matters to the patient:</strong> what they have been told and what they care about. Two people with the same cancer can reasonably make different choices.</li>
<li><strong>Know your role:</strong> ask your attending beforehand whether they want you to take only the history or also to try the assessment and plan.</li>
</ul>
<h4>Explaining radiation in plain words</h4>
<p>Most radiation oncologists have a short, plain-language explanation they give every new patient. Writing your own is one of the most useful things you can practice.</p>
{script("Sample script", "&ldquo;We are the doctors who treat cancer with radiation. It is a kind of X-ray, like the ones used for a CT scan, but stronger and aimed from different directions so the dose is concentrated where the cancer is.<br><br>First you will come in for a simulation, which is a CT scan in the exact position you will be treated in. Nothing is treated that day. Over the next week or two, our team builds and checks your plan.<br><br>Then you will come in [Monday through Friday] for about [X] weeks. Plan on about an hour each visit, although the radiation itself takes only a few minutes. Most of the time is spent lining you up carefully.<br><br>Most people feel fine at first. Side effects build slowly, so the later weeks are usually harder than the first ones.&rdquo;")}
<p>Then add the side effects for the part of the body being treated: mouth sores and trouble swallowing for the head and neck, skin changes for the breast, and bowel and bladder changes for the pelvis.</p>
<div class='quiz-carousel' data-quiz-set='consult-spiel'></div>

{summary([
    "The consult is how you think through a patient: what problem would radiation solve, and is it the best way to solve it?",
    "Work through nine questions: why the patient was sent, the diagnosis, the location, the stage, past treatment, the goal, the other options, what radiation adds, and what limits treatment.",
    "The goal of treatment is the most important word in the chart, so name it (cure or relief, and radiation's role) before naming a dose.",
    "Radiation is not always the answer, so compare it honestly with surgery, medicines, and watching closely.",
    "In the room, check the history (especially past radiation), learn what matters to the patient, and explain simulation, planning, treatment, and side effects in plain words.",
])}
"""

# ---------------------------------------------------------------------------
# 06  TREATMENT PLANNING
# ---------------------------------------------------------------------------
# Treatment Planning figures. The target-volume and dose-distribution figures
# are plain HTML/CSS (styles: "PLANNING FIGURES" in styles.css) so labels never
# clip and they follow light and dark mode. The DVH stays a small SVG chart.
NESTED_FIG = """<figure class='edu-fig' role='group' aria-label='Nested target volumes for a lung tumor'>
<div class='tv-fig'>
<div class='tv-stage' aria-hidden='true'>
<div class='tv-body'><div class='tv-ring tv-ptv'><div class='tv-ring tv-itv'><div class='tv-ring tv-ctv'><div class='tv-ring tv-gtv'></div></div></div></div></div>
</div>
<ul class='tv-legend'>
<li><span class='tv-sw tv-sw-gtv'></span><span><strong>GTV</strong> the tumor you can see</span></li>
<li><span class='tv-sw tv-sw-ctv'></span><span><strong>CTV</strong> adds tissue where cancer cells may be hiding</span></li>
<li><span class='tv-sw tv-sw-itv'></span><span><strong>ITV</strong> adds room for movement, such as breathing</span></li>
<li><span class='tv-sw tv-sw-ptv'></span><span><strong>PTV</strong> adds a small margin for day-to-day setup differences</span></li>
</ul>
</div>
<figcaption>Schematic, not a real scan and not to scale. Each layer adds a margin for one kind of uncertainty. Real margins depend on the tumor, the technique, and the imaging used.</figcaption>
</figure>"""

DVH_SVG = """<figure class='edu-fig' role='group' aria-label='Sample dose-volume histogram'>
<svg viewBox='0 0 560 320' xmlns='http://www.w3.org/2000/svg' role='img' aria-labelledby='dvhtitle dvhdesc' style='max-width:640px;margin:0 auto'>
<title id='dvhtitle'>Sample dose-volume histogram with a target curve and an organ-at-risk curve</title>
<desc id='dvhdesc'>The target curve stays near 100 percent of its volume until the prescribed dose and then drops steeply. The organ-at-risk curve falls early. A dashed line at 20 Gy shows how to read V20, the percent of the organ receiving at least 20 Gy.</desc>
<line x1='70' y1='30' x2='70' y2='260' stroke='var(--ink-faint)' stroke-width='1.5'/>
<line x1='70' y1='260' x2='530' y2='260' stroke='var(--ink-faint)' stroke-width='1.5'/>
<text x='62' y='34' font-size='12' fill='var(--ink-faint)' text-anchor='end' font-family='var(--font-body)'>100%</text>
<text x='62' y='149' font-size='12' fill='var(--ink-faint)' text-anchor='end' font-family='var(--font-body)'>50%</text>
<text x='62' y='264' font-size='12' fill='var(--ink-faint)' text-anchor='end' font-family='var(--font-body)'>0%</text>
<text x='18' y='150' font-size='12.5' fill='var(--ink-soft)' text-anchor='middle' font-family='var(--font-body)' transform='rotate(-90 18 150)'>Percent of the structure</text>
<text x='300' y='296' font-size='12.5' fill='var(--ink-soft)' text-anchor='middle' font-family='var(--font-body)'>Dose (Gy), increasing to the right</text>
<line x1='360' y1='30' x2='360' y2='260' stroke='var(--ink-faint)' stroke-width='1' stroke-dasharray='4 5'/>
<text x='360' y='22' font-size='12' fill='var(--ink-soft)' text-anchor='middle' font-family='var(--font-body)'>Prescribed dose</text>
<path d='M70,32 L320,32 C340,32 350,50 355,80 C358,110 359,180 360,260' fill='none' stroke='var(--accent)' stroke-width='3' stroke-linecap='round'/>
<path d='M70,32 C120,62 160,98 200,132 C250,174 300,206 350,224 C390,236 440,246 490,252' fill='none' stroke='var(--svc-headneck)' stroke-width='3' stroke-linecap='round'/>
<line x1='150' y1='260' x2='150' y2='86' stroke='var(--svc-headneck)' stroke-width='1.2' stroke-dasharray='3 4'/>
<line x1='70' y1='86' x2='150' y2='86' stroke='var(--svc-headneck)' stroke-width='1.2' stroke-dasharray='3 4'/>
<circle cx='150' cy='86' r='4.5' fill='var(--svc-headneck)'/>
<text x='158' y='80' font-size='12' fill='var(--ink-soft)' font-family='var(--font-body)'>V20: read up from 20 Gy</text>
<text x='150' y='276' font-size='11.5' fill='var(--ink-faint)' text-anchor='middle' font-family='var(--font-body)'>20 Gy</text>
<text x='250' y='50' font-size='12.5' fill='var(--accent)' font-weight='700' font-family='var(--font-body)'>Target</text>
<text x='410' y='232' font-size='12.5' fill='var(--svc-headneck)' font-weight='700' font-family='var(--font-body)'>Organ at risk</text>
</svg>
<figcaption>Sample DVH (not real patient data). The target curve stays near 100% until the prescribed dose and then drops steeply, which means good coverage. The organ-at-risk curve falls early, which means most of the organ gets little dose. Reading up from 20 Gy to the organ curve and across gives V20, the percent of the organ that receives 20 Gy or more.</figcaption>
</figure>"""

ISODOSE_FIG = """<figure class='edu-fig' role='group' aria-label='Schematic dose distribution'>
<div class='iso-fig' aria-hidden='true'>
<div class='iso-body'></div>
<div class='iso-line iso-low'></div>
<div class='iso-line iso-rx'></div>
<div class='iso-ptv'></div>
<div class='iso-hot'></div>
<div class='iso-oar'>OAR</div>
</div>
<ul class='iso-legend'>
<li><span class='iso-sw iso-sw-ptv'></span>Target (PTV), dashed outline</li>
<li><span class='iso-sw iso-sw-rx'></span>Prescription dose line, hugging the target</li>
<li><span class='iso-sw iso-sw-low'></span>A lower dose line, as the dose falls off</li>
<li><span class='iso-sw iso-sw-hot'></span>Hot spot, a small area above the planned dose</li>
<li><span class='iso-sw iso-sw-oar'></span>Organ at risk, outside the high-dose lines</li>
</ul>
<figcaption>Schematic cross-section, not a real plan. Isodose lines are like contour lines on a map: each one joins points that receive the same dose. Good coverage means the prescription line wraps the whole target; good conformity means it does not spill far beyond it.</figcaption>
</figure>"""

PLANNING = f"""
<p>The consult decided <em>whether</em> to use radiation and <em>why</em>. This last reading follows what happens next: how the team turns that decision into an actual plan, and why we cannot simply give more radiation to be safe.</p>

<h3 id='problem'>Three Things to Balance</h3>
<p>Every radiation plan is a balance between three things:</p>
{cards([
    ("Target", "What are we trying to destroy?"),
    ("Organs at risk", "What healthy tissue are we trying to protect?"),
    ("Dose", "How much radiation does the target need?"),
])}
<div class='big-idea'>That is the whole planning problem. Everything else in this reading is a word for one of those three things.</div>

<h3 id='volumes'>Drawing the Target: GTV, CTV, ITV, PTV</h3>
<p>On the planning CT scan, the doctor draws the target as a set of layers, like the rings of an onion. Each layer adds a margin for one kind of uncertainty.</p>
<dl class='spec-list'>
<div class='spec-row'><dt>GTV</dt><dd><strong>Gross tumor volume:</strong> the tumor you can actually see on a scan or feel on exam.</dd></div>
<div class='spec-row'><dt>CTV</dt><dd><strong>Clinical target volume:</strong> the GTV plus the nearby tissue where cancer cells may be hiding but are too small to see.</dd></div>
<div class='spec-row'><dt>ITV</dt><dd><strong>Internal target volume:</strong> extra room for movement inside the body, such as a lung tumor moving as the patient breathes.</dd></div>
<div class='spec-row'><dt>PTV</dt><dd><strong>Planning target volume:</strong> a final small margin for the tiny differences in how the patient lies from day to day.</dd></div>
</dl>
{NESTED_FIG}
<p>Knowing how the layers are used matters more than memorizing the definitions. Three examples:</p>
{cards([
    ("Lung SBRT", "The tumor is drawn on a breathing CT scan, the ITV covers everywhere it moves, and a small PTV goes around that. There is often no separate CTV."),
    ("Breast after lumpectomy", "The tumor has already been removed, so there is no GTV. The surgical area and the rest of the breast form the CTV, with a PTV around it."),
    ("Glioblastoma", "The surgical cavity and any leftover tumor form the GTV, the CTV adds a margin for cancer cells spreading into the brain, and the PTV goes around that."),
], numbered=False)}
<h4>When a layer is skipped</h4>
<ul>
<li><strong>A brain metastasis</strong> has a sharp edge and does not spread into the tissue around it, so there is <strong>no CTV</strong>. The GTV goes straight to the PTV.</li>
<li><strong>Prostate cancer</strong> is often hard to see and may be in several spots, so there is <strong>no separate GTV</strong>. The whole prostate becomes the CTV.</li>
</ul>
<div class='contour-exercise' id='exercise-gtv-brainmet'></div>

<h3 id='oars'>Organs at Risk</h3>
<p>Healthy organs near the target are drawn too, because an organ that is not drawn cannot be protected. Which ones matter depends on where the tumor is. A helpful first idea is to sort organs by how they handle radiation:</p>
{compare(
    ("Serial organs", "Watch the highest dose", "<p>These organs work like a chain: if one link breaks, the whole chain fails. A small spot of too much dose can matter. Examples are the spinal cord, the brainstem, and the nerves to the eyes.</p>"),
    ("Parallel organs", "Watch the average dose or the amount treated", "<p>These organs are made of many units working side by side. They can handle a small high-dose area as long as enough of the organ is spared. Examples are the lungs, liver, kidneys, and salivary glands.</p>"),
)}
<p>This is a way of thinking, not a strict rule. Many organs behave partly both ways, and the exact limits depend on the part of the body, the number of fractions, and the hospital's protocols.</p>
<div class='contour-exercise' id='exercise-oar-rectum'></div>

<h3 id='sequence'>The Planning Steps</h3>
{vflow([
    (None, [
        ("Simulation", "The patient is positioned, held still with masks or cushions, and scanned with a planning CT. A breathing CT or a breath-hold scan is used when motion matters."),
        ("Image fusion", "An MRI or PET scan is lined up with the planning CT when it helps. MRI shows soft tissue clearly, while the CT gives the information the computer needs to calculate dose."),
        ("Contouring", "The doctor draws the targets and organs at risk, one slice at a time."),
        ("Prescription", "The doctor sets the total dose and the number of fractions for each target."),
        ("Planning", "The planning team chooses the technique and the beams or arcs."),
        ("Optimization", "The planning computer and the dosimetrist push the target dose up and the organ doses down, trading one against the other."),
        ("Review", "The doctor checks the plan, both as a graph (the DVH) and slice by slice on the scan."),
        ("Quality assurance", "The physics team confirms the machine can deliver the plan, often by measuring it before the first treatment."),
        ("Image guidance", "Before every treatment, a quick scan confirms the patient and target are in the right place."),
    ]),
])}

<h3 id='dvh'>Reading a Dose-Volume Histogram</h3>
<p>A <strong>dose-volume histogram (DVH)</strong> is a graph that shows how much of each structure receives each level of dose. There is one curve for each structure:</p>
{compare(
    ("Target", "High dose to almost all of it", "<p>The curve stays flat near 100% until it reaches the prescribed dose, then drops sharply.</p>"),
    ("Organ at risk", "As little dose as possible", "<p>The curve should drop early, meaning most of the organ gets only a small dose.</p>"),
)}
{DVH_SVG}
<p>Dose limits are written in this graph's language. A limit such as &ldquo;lung V20 under 30%&rdquo; means less than 30% of the lungs should receive 20 Gy or more. You do not need to read complicated DVHs yet. Just know what the curves are trying to show.</p>
<div class='pearl'>
<strong>Clinical Pearl</strong>
<p>A DVH shows <em>how much</em> dose an organ gets, but not <em>where</em>. A plan can look fine on the graph and still put a hot spot somewhere it should not be, so doctors always scroll through the scan slice by slice as well.</p>
</div>

<h3 id='coverage-toxicity'>Covering the Target Without Hurting the Patient</h3>
<div class='big-idea'>The best plan is not the one with the lowest dose to healthy organs. It is the one that fully treats the target while keeping side effects acceptable.</div>
<ul>
<li><strong>Coverage:</strong> does the whole target, including its edges, get the prescribed dose?</li>
<li><strong>Conformity:</strong> how tightly does the high dose hug the target?</li>
<li><strong>Hot spots:</strong> small areas that get more than the planned dose. Usually acceptable inside the tumor, but not inside a healthy organ.</li>
</ul>
{ISODOSE_FIG}
<p>When these goals conflict, the doctor decides. If the target touches the spinal cord, for example, the plan usually accepts a slightly lower dose to that edge of the target to protect the cord.</p>
<details class='reveal'>
<summary>Following along at a plan review: CB-CHOP<span class='chev'>&#9662;</span></summary>
<div class='reveal-body'>
<p>Many residents check a plan in this order, and you can follow along with it:</p>
{table(["Letter", "Question"], [
    ["<strong>C</strong>ontours", "Is everything we are treating and protecting drawn correctly?"],
    ["<strong>B</strong>eams", "Does the arrangement of beams or arcs make sense?"],
    ["<strong>C</strong>overage", "Is the target getting its full dose?"],
    ["<strong>H</strong>ot spots", "Is anywhere getting more than intended, especially a healthy organ?"],
    ["<strong>O</strong>rgans at risk", "Are healthy organs within their limits?"],
    ["<strong>P</strong>rescription", "Does the plan match the dose, fractions, and target that were ordered?"],
])}
</div>
</details>

<h3 id='technique'>Choosing a Technique</h3>
<p>The technique follows the shape of the problem (see <em>Radiation Modalities</em>):</p>
<ul>
<li><strong>3D-CRT</strong> when the shape is fairly simple.</li>
<li><strong>IMRT or VMAT</strong> when the target and healthy organs are tangled together.</li>
<li><strong>SRS or SBRT</strong> when a small target can be hit precisely with a very high dose.</li>
<li><strong>Protons</strong> when stopping the beam behind the target may really matter.</li>
<li><strong>Brachytherapy</strong> when putting the source next to the target gives a better dose.</li>
</ul>

<h3 id='why-not-more'>Why Not Just Give More Radiation?</h3>
<div class='big-idea'>Because healthy tissues have limits.</div>
<p>Every target sits next to something that must not be badly injured. These are the organs at risk you will hear about most:</p>
{table(["Organ at risk", "What we are trying to prevent"], [
    ["Spinal cord", "Paralysis"],
    ["Brainstem", "Serious brain injury"],
    ["Optic nerves", "Loss of vision"],
    ["Bowel", "Blockage, narrowing, or a hole in the bowel"],
    ["Rectum", "Inflammation and bleeding"],
    ["Bladder", "Inflammation and bleeding"],
    ["Lungs", "Inflammation and scarring"],
    ["Heart", "Heart problems years later"],
    ["Liver", "Liver failure from radiation"],
    ["Kidneys", "Loss of kidney function"],
])}
<p>The exact limits come from research protocols and from each hospital, and they depend on the number of fractions. Each disease-site module teaches the organs that matter most for that cancer.</p>

<h3 id='apply'>Now Apply It</h3>
<p>You now have the whole story. Understand what radiation is, how it works, and which tools deliver it. Present the patient clearly. Decide whether radiation will help. Then design a treatment that hits the target and protects everything else. Every disease-site module asks the same questions about one cancer: what is it, where is it, how far has it spread, what is radiation's job, and what limits the plan?</p>

{summary([
    "Every plan balances three things: the target, the healthy organs at risk, and the dose the target needs.",
    "Targets are drawn in layers, from the visible tumor (GTV) to hidden spread (CTV), internal motion (ITV), and daily setup differences (PTV), and not every case uses every layer.",
    "Planning moves from simulation and image fusion to contouring, prescription, planning, optimization, review, quality assurance, and daily image guidance.",
    "A DVH shows how much of each structure gets each dose: the target should get a high dose almost everywhere, and healthy organs as little as possible.",
    "A good plan fully treats the target while keeping side effects acceptable, and the limits of healthy tissue are why we cannot simply give more radiation.",
])}
"""

SECTIONS = [
    {
        "id": "rad-onc-101", "num": 1, "title": "Radiation 101",
        "question": "What happens when a patient receives radiation?",
        "objectives": [
            "Describe the steps a patient goes through, from consult to follow-up.",
            "Define dose, fraction, and treatment course.",
            "Explain why radiation is split into fractions.",
        ],
        "html": RAD101,
    },
    {
        "id": "how-rt-works", "num": 2, "title": "How Radiation Works",
        "question": "Why does radiation kill cancer cells, and why are healthy tissues hurt too?",
        "objectives": [
            "Explain how radiation damages DNA, directly and indirectly.",
            "Explain why tumors shrink over weeks to months.",
            "Contrast acute and late side effects.",
            "Explain the 4 R's and why splitting the dose works.",
        ],
        "html": HOWRT,
    },
    {
        "id": "machines-modalities", "num": 3, "title": "Radiation Modalities",
        "question": "What machines and techniques does a radiation oncologist use?",
        "objectives": [
            "Distinguish external beam radiation from brachytherapy.",
            "Describe the linac, the gantry, and the multileaf collimator.",
            "Explain how 3D-CRT, IMRT, and VMAT shape and deliver the dose.",
            "Explain image guidance and when SRS and SBRT are used.",
            "Compare photons, electrons, and protons.",
        ],
        "html": MODALITIES,
    },
    {
        "id": "presenting-patients", "num": 4, "title": "How to Give a Presentation",
        "question": "How do I tell the team about a patient?",
        "objectives": [
            "Give a clear one-sentence summary of a patient.",
            "Present pathology, imaging, and stage efficiently.",
            "End with a clear assessment and radiation recommendation.",
        ],
        "html": PRESENTATION,
    },
    {
        "id": "the-consult", "num": 5, "title": "The Rad Onc Consult",
        "question": "How do we decide whether, and how, to use radiation?",
        "objectives": [
            "Name the goal (intent) of treatment.",
            "Decide what problem radiation would solve.",
            "Compare radiation with surgery, medicines, and watching closely.",
            "Identify what limits treatment.",
        ],
        "html": CONSULT,
    },
    {
        "id": "treatment-planning", "num": 6, "title": "Treatment Planning",
        "question": "How does that decision become a safe radiation plan?",
        "objectives": [
            "Define GTV, CTV, ITV, and PTV.",
            "Explain why organs at risk are drawn and protected.",
            "Describe the steps from simulation to treatment.",
            "Explain what a DVH shows.",
            "Explain how a plan balances the target against healthy tissue.",
        ],
        "html": PLANNING,
    },
]

# Contractions this guide avoids (possessives like "patient's" are fine).
CONTRACTION = re.compile(
    r"\b\w+(?:'|&rsquo;|’)(?:t|re|ve|ll|m|d)\b"
    r"|\b(?:it|that|there|here|what|let|who|he|she|where|how)(?:'|&rsquo;|’)s\b", re.I)


def check_style(text, where):
    for bad in ("—", "–", "&mda" + "sh;", "&nda" + "sh;"):
        assert bad not in text, f"dash {bad!r} in {where}"
    found = CONTRACTION.findall(text)
    assert not found, f"contractions in {where}: {found[:8]}"


def main():
    for s in SECTIONS:
        s["html"] = s["html"].strip() + "\n"
        for field in ("title", "question", "html"):
            check_style(s[field], f"{s['id']}.{field}")
        for o in s["objectives"]:
            check_style(o, s["id"])
    with open(OUT, "w") as f:
        json.dump(SECTIONS, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {OUT} ({len(SECTIONS)} readings)")


if __name__ == "__main__":
    main()
