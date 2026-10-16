"""Inline SVG illustrations for the Radiation Modalities reading.

All schematic (not real anatomy or real plans). Colors come from theme tokens
where they need to follow light/dark mode; dose colors are fixed so they read
the same in both themes.
"""
import math

BODY = "color-mix(in srgb, var(--ink-faint) 22%, var(--surface))"
BODY_EDGE = "color-mix(in srgb, var(--ink-faint) 55%, var(--surface))"
MACHINE = "color-mix(in srgb, var(--ink-faint) 40%, var(--surface))"
MACHINE_DARK = "color-mix(in srgb, var(--ink-faint) 70%, var(--surface))"
PANEL = "var(--surface)"
LINE = "var(--line)"
TEXT = "var(--ink-soft)"
TITLE = "var(--ink)"
TUMOR = "#ef4444"
CORD = "#3b82f6"
BEAM = "#f5b942"
DOSE = "#f59e0b"
FONT = "font-family='var(--font-body)'"


def _t(x, y, s, size=12, fill=TEXT, anchor="middle", weight="400"):
    return f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' fill='{fill}' {FONT} text-anchor='{anchor}' font-weight='{weight}'>{s}</text>"


def _figure(svg, caption):
    return f"<figure>\n{svg}\n<figcaption>{caption}</figcaption>\n</figure>"


def _panel(x, y, w, h):
    return f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='14' fill='{PANEL}' stroke='{LINE}'/>"


# ---------------------------------------------------------------------------
def linac_mlc():
    p = ["<svg viewBox='0 0 600 270' xmlns='http://www.w3.org/2000/svg' role='img' aria-labelledby='linactitle'>",
         "<title id='linactitle'>A linear accelerator from the side, and the multileaf collimator seen looking down the beam</title>",
         _panel(4, 4, 286, 262), _panel(310, 4, 286, 262)]
    # Left: the machine from the side
    p += [
        _t(147, 28, "The linac, from the side", 13, TITLE, weight="700"),
        f"<rect x='232' y='52' width='46' height='184' rx='8' fill='{MACHINE}'/>",
        f"<rect x='92' y='52' width='170' height='38' rx='10' fill='{MACHINE}'/>",
        f"<rect x='82' y='78' width='62' height='44' rx='8' fill='{MACHINE_DARK}'/>",
        f"<rect x='90' y='114' width='46' height='7' rx='2' fill='var(--ink-soft)'/>",
        f"<polygon points='98,122 128,122 150,192 76,192' fill='{BEAM}' fill-opacity='0.45'/>",
        f"<rect x='26' y='180' width='170' height='16' rx='8' fill='{BODY_EDGE}'/>",
        f"<circle cx='40' cy='176' r='10' fill='{BODY_EDGE}'/>",
        f"<rect x='18' y='198' width='190' height='8' rx='3' fill='var(--ink-faint)'/>",
        f"<rect x='98' y='206' width='28' height='30' fill='var(--ink-faint)'/>",
        f"<line x1='14' y1='236' x2='282' y2='236' stroke='{LINE}' stroke-width='2'/>",
        f"<path d='M58,70 A70,70 0 0 1 108,44' fill='none' stroke='{TEXT}' stroke-width='1.8'/>",
        f"<polygon points='108,44 99,42 104,51' fill='{TEXT}'/>",
        _t(52, 60, "Gantry", 11.5, anchor="end", weight="700"),
        _t(52, 73, "rotates", 11, anchor="end"),
        _t(162, 112, "Head with", 11, anchor="start"),
        _t(162, 125, "the MLC", 11, anchor="start", weight="700"),
        _t(148, 160, "Beam", 11, anchor="start"),
        _t(155, 222, "Couch", 11, anchor="start"),
    ]
    # Right: beam's-eye view of the MLC
    x0, x1, y0, y1 = 336, 570, 44, 238
    cx, cy, rx, ry = 453, 141, 44, 62
    p += [_t(453, 28, "Looking down the beam", 13, TITLE, weight="700"),
          f"<rect x='{x0}' y='{y0}' width='{x1 - x0}' height='{y1 - y0}' fill='{BEAM}' fill-opacity='0.35'/>"]
    rows = 19
    h = (y1 - y0) / rows
    for i in range(rows):
        yc = y0 + h * (i + 0.5)
        d = (yc - cy) / ry
        half = rx * math.sqrt(1 - d * d) + 6 if abs(d) < 1 else 0
        xl, xr = cx - half, cx + half
        ytop = y0 + h * i + 0.6
        p.append(f"<rect x='{x0}' y='{ytop:.1f}' width='{xl - x0:.1f}' height='{h - 1.2:.1f}' fill='#9aa4b2' stroke='#5b6573' stroke-width='0.6'/>")
        p.append(f"<rect x='{xr:.1f}' y='{ytop:.1f}' width='{x1 - xr:.1f}' height='{h - 1.2:.1f}' fill='#9aa4b2' stroke='#5b6573' stroke-width='0.6'/>")
    p += [f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='{TUMOR}' fill-opacity='0.85'/>",
          _t(cx, cy + 4, "Tumor", 11, "#fff", weight="700"),
          _t(375, 258, "Leaves", 11, weight="700"), _t(531, 258, "Leaves", 11, weight="700"),
          "</svg>"]
    return _figure("\n".join(p),
                   "Schematic, not to scale. Left: the gantry swings around the patient on the couch. Right: the view from the machine's head. "
                   "Dozens of thin metal leaves slide in from each side so the opening matches the shape of the tumor; the leaves block the beam everywhere else.")


# ---------------------------------------------------------------------------
def _target_path(cx, cy):
    """A cap-shaped target that wraps over the spinal cord."""
    return (f"M{cx - 45},{cy + 20} C{cx - 50},{cy - 36} {cx + 50},{cy - 36} {cx + 45},{cy + 20} "
            f"C{cx + 30},{cy + 20} {cx + 28},{cy - 4} {cx},{cy - 4} C{cx - 28},{cy - 4} {cx - 30},{cy + 20} {cx - 45},{cy + 20} Z")


def _beam(cx, cy, angle, width, length, modulated):
    if not modulated:
        return f"<rect x='{-width / 2}' y='{-length}' width='{width}' height='{length}' fill='{BEAM}' fill-opacity='0.32' transform='translate({cx} {cy}) rotate({angle})'/>"
    colors = ["#f59e0b", "#ef4444", "#f59e0b", "#fef3c7", "#f59e0b", "#ef4444", "#f59e0b"]
    n = len(colors)
    w = width / n
    strips = "".join(f"<rect x='{-width / 2 + i * w:.1f}' y='{-length}' width='{w + 0.3:.1f}' height='{length}' fill='{c}' fill-opacity='0.26'/>" for i, c in enumerate(colors))
    return f"<g transform='translate({cx} {cy}) rotate({angle})'>{strips}</g>"


def crt_vs_imrt():
    p = ["<svg viewBox='0 0 600 290' xmlns='http://www.w3.org/2000/svg' role='img' aria-labelledby='crtimrttitle'>",
         "<title id='crtimrttitle'>3D-CRT compared with IMRT on a schematic cross-section of the body</title>",
         "<defs><clipPath id='cl-crt'><rect x='5' y='42' width='284' height='202' rx='12'/></clipPath>",
         "<clipPath id='cl-imrt'><rect x='311' y='42' width='284' height='202' rx='12'/></clipPath></defs>"]
    for (px, cid, title, sub, modulated) in [(4, "cl-crt", "3D-CRT", "Shape the beams", False),
                                             (310, "cl-imrt", "IMRT", "Vary the intensity within each beam", True)]:
        cx, cy = px + 143, 148
        p.append(_panel(px, 4, 286, 242))
        p.append(_t(cx, 26, title, 14, TITLE, weight="700"))
        p.append(_t(cx, 41, sub, 11.5))
        p.append(f"<g clip-path='url(#{cid})'>")
        p.append(f"<ellipse cx='{cx}' cy='{cy}' rx='108' ry='70' fill='{BODY}' stroke='{BODY_EDGE}' stroke-width='1.5'/>")
        for a in (-55, 55, 125, -125):
            p.append(_beam(cx, cy, a, 104, 170, modulated))
        p.append("</g>")
        target = _target_path(cx, cy)
        if modulated:
            scaled = f"transform='translate({cx} {cy}) scale(1.22) translate({-cx} {-cy})'"
            p.append(f"<path d='{target}' {scaled} fill='{DOSE}' fill-opacity='0.18' stroke='#fff' stroke-width='5' stroke-opacity='0.8'/>")
            p.append(f"<path d='{target}' {scaled} fill='none' stroke='{DOSE}' stroke-width='2.6' stroke-dasharray='5 4'/>")
        else:
            p.append(f"<rect x='{cx - 56}' y='{cy - 34}' width='112' height='68' rx='16' fill='{DOSE}' fill-opacity='0.18' stroke='#fff' stroke-width='5' stroke-opacity='0.8'/>")
            p.append(f"<rect x='{cx - 56}' y='{cy - 34}' width='112' height='68' rx='16' fill='none' stroke='{DOSE}' stroke-width='2.6' stroke-dasharray='5 4'/>")
        p.append(f"<path d='{target}' fill='{TUMOR}' fill-opacity='0.85'/>")
        p.append(f"<circle cx='{cx}' cy='{cy + 15}' r='8' fill='{CORD}'/>")
        p.append(_t(cx, 236, "The cord sits inside the high-dose region" if not modulated else "The high dose bends around the cord", 11.5, weight="700"))
    p += [f"<circle cx='120' cy='272' r='6' fill='{TUMOR}'/>", _t(131, 276, "Tumor (target)", 11.5, anchor="start"),
          f"<circle cx='250' cy='272' r='6' fill='{CORD}'/>", _t(261, 276, "Spinal cord (organ at risk)", 11.5, anchor="start"),
          f"<rect x='428' y='265' width='16' height='13' rx='3' fill='{DOSE}' fill-opacity='0.14' stroke='{DOSE}' stroke-width='2' stroke-dasharray='4 3'/>",
          _t(450, 276, "High-dose region", 11.5, anchor="start"), "</svg>"]
    return _figure("\n".join(p),
                   "Schematic cross-section of the body, not a real plan. Both techniques aim several beams at the tumor. In 3D-CRT each beam is the same strength all the way across, "
                   "so the high-dose region is a simple block. In IMRT each beam is split into many small pieces of different strength (the colored stripes), so the high dose can curve around the spinal cord.")


# ---------------------------------------------------------------------------
def _head_and_beam(cx, cy, angle, r, style):
    rot = angle + 90
    if style == "uniform":
        beam = f"<polygon points='-8,{-r + 9} 8,{-r + 9} 20,0 -20,0' fill='{BEAM}' fill-opacity='0.5'/>"
    else:
        colors = ["#fde68a", "#ef4444", "#f59e0b", "#fef3c7"]
        strips = []
        for i, c in enumerate(colors):
            t0, t1 = -8 + 4 * i, -8 + 4 * (i + 1)
            b0, b1 = -20 + 10 * i, -20 + 10 * (i + 1)
            strips.append(f"<polygon points='{t0},{-r + 9} {t1},{-r + 9} {b1},0 {b0},0' fill='{c}' fill-opacity='0.55'/>")
        beam = "".join(strips)
    head = f"<rect x='-15' y='{-r - 9}' width='30' height='18' rx='4' fill='{MACHINE_DARK}'/>"
    return f"<g transform='translate({cx} {cy}) rotate({rot})'>{beam}{head}</g>"


def delivery():
    p = ["<svg viewBox='0 0 600 250' xmlns='http://www.w3.org/2000/svg' role='img' aria-labelledby='delivtitle'>",
         "<title id='delivtitle'>How 3D-CRT, IMRT, and VMAT deliver radiation</title>",
         "<defs><linearGradient id='vmat-arc' x1='0' x2='1' y1='0' y2='0'>"
         "<stop offset='0' stop-color='#3b82f6'/><stop offset='0.35' stop-color='#22c55e'/><stop offset='0.65' stop-color='#f59e0b'/><stop offset='1' stop-color='#ef4444'/>"
         "</linearGradient></defs>"]
    panels = [(100, "3D-CRT", "uniform", ("A few fixed beams,", "each the same strength across")),
              (300, "IMRT", "modulated", ("A few fixed beams,", "strength varies within each")),
              (500, "VMAT", "arc", ("The gantry rotates,", "strength varies as it moves"))]
    for cx, title, style, (l1, l2) in panels:
        cy, r = 140, 82
        p.append(_panel(cx - 96, 4, 192, 242))
        p.append(_t(cx, 28, title, 14, TITLE, weight="700"))
        p.append(f"<rect x='{cx - 66}' y='{cy + 34}' width='132' height='7' rx='3' fill='var(--ink-faint)'/>")
        if style == "arc":
            a0, a1 = math.radians(-168), math.radians(-12)
            sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
            ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
            p.append(f"<path d='M{sx:.1f},{sy:.1f} A{r},{r} 0 0 1 {ex:.1f},{ey:.1f}' fill='none' stroke='url(#vmat-arc)' stroke-width='5' stroke-linecap='round' stroke-opacity='0.8'/>")
            p.append(f"<polygon points='{ex + 2:.1f},{ey + 12:.1f} {ex - 9:.1f},{ey - 3:.1f} {ex + 8:.1f},{ey - 6:.1f}' fill='#ef4444'/>")
        p.append(f"<ellipse cx='{cx}' cy='{cy}' rx='52' ry='32' fill='{BODY}' stroke='{BODY_EDGE}' stroke-width='1.5'/>")
        angles = [-60] if style == "arc" else [-90, -150, -30]
        for a in angles:
            p.append(_head_and_beam(cx, cy, a, r, "uniform" if style == "uniform" else "modulated"))
        p.append(f"<circle cx='{cx}' cy='{cy}' r='9' fill='{TUMOR}' fill-opacity='0.9'/>")
        p.append(_t(cx, 210, l1, 11.5, weight="700"))
        p.append(_t(cx, 226, l2, 11.5))
    p.append("</svg>")
    return _figure("\n".join(p),
                   "Schematic, not to scale. Same goal, different delivery: IMRT and VMAT both vary the strength of the beam to shape the dose, "
                   "but VMAT does it while the gantry is moving, which usually makes each treatment faster.")


# ---------------------------------------------------------------------------
def _converging(tx, ty, angles, length=105, width=7):
    return "".join(f"<rect x='{-width / 2}' y='{-length}' width='{width}' height='{length}' fill='{BEAM}' fill-opacity='0.5' transform='translate({tx} {ty}) rotate({a})'/>" for a in angles)


def stereotactic():
    p = ["<svg viewBox='0 0 600 250' xmlns='http://www.w3.org/2000/svg' role='img' aria-labelledby='sterotitle'>",
         "<title id='sterotitle'>Stereotactic radiosurgery to a small brain target and stereotactic body radiation to a small lung target</title>",
         "<defs><clipPath id='cl-srs'><rect x='5' y='42' width='284' height='172'/></clipPath>",
         "<clipPath id='cl-sbrt'><rect x='311' y='42' width='284' height='172'/></clipPath></defs>",
         _panel(4, 4, 286, 242), _panel(310, 4, 286, 242),
         _t(147, 28, "SRS: the brain", 14, TITLE, weight="700"),
         _t(453, 28, "SBRT: the body", 14, TITLE, weight="700")]
    # Brain
    p += [f"<ellipse cx='147' cy='132' rx='92' ry='78' fill='#f9a8b8' fill-opacity='0.35' stroke='#e27d93' stroke-width='2'/>",
          "<path d='M147,56 L147,208' stroke='#e27d93' stroke-width='1.5' fill='none'/>",
          "<path d='M90,90 q15,-12 28,0 q12,12 26,0 M88,130 q14,-12 28,0 q12,12 24,0 M96,170 q14,-10 26,0' stroke='#e27d93' stroke-width='1.4' fill='none'/>",
          "<path d='M160,82 q14,-12 28,0 q12,12 26,0 M162,124 q14,-12 26,0 M160,168 q14,-10 26,0 q12,10 22,0' stroke='#e27d93' stroke-width='1.4' fill='none'/>",
          f"<g clip-path='url(#cl-srs)'>{_converging(186, 110, [-80, -40, 0, 40, 80, 120, 160, 200, 240])}</g>",
          f"<circle cx='186' cy='110' r='9' fill='{TUMOR}'/>",
          _t(147, 232, "A small brain metastasis", 11.5, weight="700")]
    # Lungs
    p += ["<path d='M440,60 C400,60 372,110 372,160 C372,196 392,214 420,212 C438,210 444,196 444,180 L444,72 C444,64 443,60 440,60 Z' fill='#f9a8b8' fill-opacity='0.35' stroke='#e27d93' stroke-width='2'/>",
          "<path d='M466,60 C506,60 534,110 534,160 C534,196 514,214 486,212 C468,210 462,196 462,180 L462,72 C462,64 463,60 466,60 Z' fill='#f9a8b8' fill-opacity='0.35' stroke='#e27d93' stroke-width='2'/>",
          f"<g clip-path='url(#cl-sbrt)'>{_converging(500, 118, [-70, -30, 10, 50, 90, 130, 170, 210])}</g>",
          f"<circle cx='500' cy='118' r='9' fill='{TUMOR}'/>",
          _t(453, 232, "A small lung cancer", 11.5, weight="700"),
          "</svg>"]
    return _figure("\n".join(p),
                   "Schematic, not to scale. Many beams (or arcs) cross at one small target. Each beam alone is weak, but where they all meet the dose is very high, "
                   "and it drops off quickly just outside the target.")


# ---------------------------------------------------------------------------
def igrt():
    p = ["<svg viewBox='0 0 600 220' xmlns='http://www.w3.org/2000/svg' role='img' aria-labelledby='igrttitle'>",
         "<title id='igrttitle'>Image guidance: the target is found on the daily scan and the couch is shifted to line it up</title>"]
    panels = [(100, "The plan", "Crosshairs on the target", (0, 0)),
              (300, "Today's scan", "The target is 6 mm off", (24, -15)),
              (500, "After the shift", "Lined up, ready to treat", (0, 0))]
    for cx, title, sub, (dx, dy) in panels:
        cy = 112
        p.append(_panel(cx - 96, 4, 192, 212))
        p.append(_t(cx, 28, title, 14, TITLE, weight="700"))
        p.append(f"<ellipse cx='{cx}' cy='{cy}' rx='70' ry='46' fill='{BODY}' stroke='{BODY_EDGE}' stroke-width='1.5'/>")
        p.append(f"<circle cx='{cx + dx}' cy='{cy + dy}' r='12' fill='{TUMOR}' fill-opacity='0.85'/>")
        p.append(f"<line x1='{cx - 80}' y1='{cy}' x2='{cx + 80}' y2='{cy}' stroke='#22c55e' stroke-width='1.6' stroke-dasharray='5 4'/>")
        p.append(f"<line x1='{cx}' y1='{cy - 58}' x2='{cx}' y2='{cy + 58}' stroke='#22c55e' stroke-width='1.6' stroke-dasharray='5 4'/>")
        if dx:
            p.append(f"<circle cx='{cx}' cy='{cy}' r='12' fill='none' stroke='{TUMOR}' stroke-width='1.6' stroke-dasharray='3 3'/>")
            p.append(f"<line x1='{cx + dx - 10}' y1='{cy + dy + 8}' x2='{cx + 9}' y2='{cy - 6}' stroke='var(--ink)' stroke-width='2'/>")
            p.append(f"<polygon points='{cx + 5},{cy - 2} {cx + 14},{cy - 4} {cx + 9},{cy - 12}' fill='var(--ink)'/>")
        p.append(_t(cx, 196, sub, 11.5, weight="700"))
    p.append("</svg>")
    return _figure("\n".join(p),
                   "Schematic. The green crosshairs mark where the plan expects the target to be. Before each treatment a quick scan on the machine shows where the target really is today, "
                   "and the couch moves the patient a few millimeters so the two match.")
